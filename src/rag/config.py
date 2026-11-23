"""Load config.yaml into Python objects, and stop typos early.

Every setting of a run lives in config.yaml. This file:

1. describes every setting, with its default (the dataclasses below);
2. loads the YAML file into those dataclasses (`load_config`);
3. refuses mistakes: an unknown key (a typo such as `max_tokenz`), a value
   of the wrong type, or settings that contradict each other;
4. makes a short fingerprint of some settings (`stage_hash`), used as the
   name of a cache folder.

Usage:

    cfg = load_config("config.yaml")
    cfg.chunk.max_tokens        # -> 512
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import Literal

import dacite
import yaml


class ConfigError(ValueError):
    """Something is wrong in the config file. The message says what."""


# ---------------------------------------------------------------------------
# The settings. One dataclass per section of config.yaml.
# The field names here ARE the keys in the YAML file.
# ---------------------------------------------------------------------------


@dataclass
class CorpusConfig:
    registry: str = "data/registry.csv"
    pdf_dir: str = "data/pdfs"


@dataclass
class ParseConfig:
    min_chars_text_layer: int = 50  # a page with fewer characters: "no_text_layer"


@dataclass
class CleanConfig:
    remove_headers_footers: bool = True
    header_footer_min_share: float = 0.4  # text repeated on >= 40% of pages


@dataclass
class ChunkConfig:
    strategy: Literal["fixed", "sentence", "section"] = "section"
    max_tokens: int = 512
    overlap_tokens: int = 50  # used by "fixed" only
    overlap_sentences: int = 1  # used by "sentence" only
    prepend_header: bool = False  # experiment E2


@dataclass
class EmbedConfig:
    model: str = "BAAI/bge-small-en-v1.5"
    query_prefix: str = ""  # e5 models need "query: "
    passage_prefix: str = ""  # e5 models need "passage: "
    batch_size: int = 64
    fake: bool = False  # True = FakeEmbedder (no download). Used in tests.


@dataclass
class RetrieveConfig:
    method: Literal["dense", "tfidf", "oracle", "none"] = "dense"  # none = no retrieval
    k: int = 5  # how many passages go into the prompt
    depth: int = 20  # how many hits we fetch (more than k, for the failure trace)
    filter: Literal["none", "pre", "post"] = "none"
    filter_source: Literal["extracted", "oracle"] = "extracted"
    dedupe: bool = True


@dataclass
class ContextConfig:
    max_tokens: int = 3000
    order: str = "rank"  # "rank", or "gold_at:<position>" for experiment E8


@dataclass
class LLMConfig:
    provider: str = "anthropic"
    model: str = "claude-haiku-5-5"
    # Haiku 5.5 does not accept a temperature setting (the API returns an
    # error), so we control it with "effort" instead: how much the model
    # thinks before answering. "low" is cheapest and fast.
    effort: Literal["low", "medium", "high"] = "low"
    max_tokens: int = 4000  # includes the model's thinking, so not too small
    timeout_s: float = 60.0
    cache: bool = True  # False for experiment E0
    fake: bool = False  # True = FakeLLM (no API key). Used in tests.


@dataclass
class PromptConfig:
    template: str = "grounded_v1"


@dataclass
class EvalConfig:
    questions: str = "eval/questions.jsonl"
    split: Literal["dev", "test"] = "dev"
    runs_dir: str = "eval/runs"  # each run is saved in <runs_dir>/<run_name>/


@dataclass
class Config:
    run_name: str = "unnamed"
    corpus: CorpusConfig = field(default_factory=CorpusConfig)
    parse: ParseConfig = field(default_factory=ParseConfig)
    clean: CleanConfig = field(default_factory=CleanConfig)
    chunk: ChunkConfig = field(default_factory=ChunkConfig)
    embed: EmbedConfig = field(default_factory=EmbedConfig)
    retrieve: RetrieveConfig = field(default_factory=RetrieveConfig)
    context: ContextConfig = field(default_factory=ContextConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    prompt: PromptConfig = field(default_factory=PromptConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_config(path: str | Path) -> Config:
    """Read a YAML file and return a checked Config."""
    path = Path(path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ConfigError(f"{path}: this is not valid YAML: {e}") from e
    try:
        return config_from_dict(data or {})
    except ConfigError as e:
        raise ConfigError(f"{path}: {e}") from None


def config_from_dict(data: dict) -> Config:
    """Turn the parsed YAML (a dict) into a checked Config."""
    # A section written with nothing under it ("parse:") comes back as None.
    data = {key: ({} if value is None else value) for key, value in data.items()}

    # Step 1: unknown keys. Our message says where the typo is and
    # suggests the right name.
    check_keys(data, Config, prefix="")

    # Step 2: types. dacite builds the dataclasses and checks that every
    # value has the right type (and that a Literal gets one of its allowed
    # words). cast=[float] lets you write `timeout_s: 60` instead of 60.0.
    try:
        cfg = dacite.from_dict(Config, data, config=dacite.Config(cast=[float], strict=True))
    except (dacite.DaciteError, ValueError) as e:
        raise ConfigError(str(e)) from None

    # Step 3: values that must make sense together.
    check_values(cfg)
    return cfg


def check_keys(data: object, cls: type, prefix: str) -> None:
    """Raise ConfigError for any key that is not a field of `cls`."""
    if not isinstance(data, dict):
        raise ConfigError(f"'{prefix.rstrip('.')}' must contain keys, not {data!r}")
    sections = {f.name: f for f in fields(cls)}
    for key, value in data.items():
        if key not in sections:
            close = get_close_matches(str(key), list(sections), n=1)
            hint = f" Did you mean '{prefix}{close[0]}'?" if close else ""
            raise ConfigError(f"unknown key '{prefix}{key}'.{hint}")
        # If this key is a whole section (chunk:, embed:, ...), check inside it too.
        section_class = sections[key].default_factory
        if is_dataclass(section_class):
            check_keys(value, section_class, prefix=f"{prefix}{key}.")


def check_values(cfg: Config) -> None:
    """Checks that need more than a type, e.g. "overlap smaller than size"."""
    problems = []
    if not cfg.run_name.replace("_", "").replace("-", "").replace(".", "").isalnum():
        problems.append("run_name is a folder name: use only letters, digits, '_', '-', '.'")
    if cfg.chunk.max_tokens <= 0:
        problems.append("chunk.max_tokens must be more than 0")
    if not 0 <= cfg.chunk.overlap_tokens < cfg.chunk.max_tokens:
        problems.append("chunk.overlap_tokens must be at least 0 and less than chunk.max_tokens")
    if cfg.retrieve.k < 1:
        problems.append("retrieve.k must be at least 1")
    if cfg.retrieve.depth < cfg.retrieve.k:
        problems.append("retrieve.depth must be at least retrieve.k")
    if cfg.context.order != "rank" and not cfg.context.order.startswith("gold_at:"):
        problems.append("context.order must be 'rank' or 'gold_at:<position>'")
    if cfg.llm.max_tokens <= 0:
        problems.append("llm.max_tokens must be more than 0")
    if not 0 < cfg.clean.header_footer_min_share <= 1:
        problems.append("clean.header_footer_min_share must be between 0 and 1")
    if problems:
        raise ConfigError("; ".join(problems))


# ---------------------------------------------------------------------------
# Saving, and fingerprints for caches
# ---------------------------------------------------------------------------


def save_config(cfg: Config, path: str | Path) -> None:
    """Write the full config (every default filled in) as YAML.
    Each run folder gets one, so you can always see exactly what ran."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(asdict(cfg), sort_keys=False, allow_unicode=True)
    path.write_text(text, encoding="utf-8")


def stage_hash(cfg: Config, *names: str) -> str:
    """A 12-character fingerprint of only the settings you name.

    Names are sections ("parse") or single settings ("embed.model"):

        stage_hash(cfg, "parse", "clean")   # the cache key for parsed documents

    If any named setting changes, the fingerprint changes, so the old cache
    is not reused. Settings you did not name do not matter.
    """
    if not names:
        raise ValueError("stage_hash needs at least one name")
    chosen = {}
    for name in sorted(set(names)):
        value = cfg
        for part in name.split("."):  # "embed.model" -> cfg.embed.model
            if not hasattr(value, part):
                raise ConfigError(f"stage_hash: there is no setting called '{name}'")
            value = getattr(value, part)
        chosen[name] = asdict(value) if is_dataclass(value) else value
    text = json.dumps(chosen, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
