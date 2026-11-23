"""Load config.yaml into typed, nested dataclasses.

Every setting of a run lives in one YAML file. This module turns that file
into a `Config` object and refuses anything suspicious:

* an unknown key (a typo such as `max_tokenz`) raises, with a suggestion;
* a value of the wrong type or outside its allowed set raises;
* settings that contradict each other (overlap >= chunk size) raise.

A key that is left out takes the default below. `save_config` writes the
*resolved* config (defaults filled in) into each run folder, so a run never
depends on a hidden default.

`stage_hash(cfg, "parse", "clean")` gives a short fingerprint of only the
settings a stage depends on. Caches use it as their key: change the chunk
size and the chunk cache misses, but the parse cache still hits.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import Any, Literal, get_args, get_origin, get_type_hints

import yaml


class ConfigError(ValueError):
    """The config file is wrong. The message names the key and the fix."""


# ---------------------------------------------------------------------------
# One dataclass per section of config.yaml. Field names ARE the YAML keys.
# ---------------------------------------------------------------------------


@dataclass
class CorpusConfig:
    registry: str = "data/registry.csv"
    pdf_dir: str = "data/pdfs"


@dataclass
class ParseConfig:
    min_chars_text_layer: int = 50  # fewer characters than this: no_text_layer


@dataclass
class CleanConfig:
    remove_headers_footers: bool = True
    header_footer_min_share: float = 0.4  # repeats on >= 40% of pages: header/footer


@dataclass
class ChunkConfig:
    strategy: Literal["fixed", "sentence", "section"] = "section"
    max_tokens: int = 512  # capped later by the model's limit minus the prefix
    overlap_tokens: int = 50  # used by "fixed" only
    overlap_sentences: int = 1  # used by "sentence" only
    prepend_header: bool = False  # E2: header goes into the embedded text only


@dataclass
class EmbedConfig:
    model: str = "BAAI/bge-small-en-v1.5"
    query_prefix: str = ""  # e5 models: "query: "
    passage_prefix: str = ""  # e5 models: "passage: "
    batch_size: int = 64
    fake: bool = False  # True in CI: hash-based vectors, no download


@dataclass
class RetrieveConfig:
    method: Literal["dense", "tfidf", "oracle", "none"] = "dense"  # none = closed-book
    k: int = 5  # passages handed to the context builder
    depth: int = 20  # always fetched, so the trace can see ranks k+1..depth
    filter: Literal["none", "pre", "post"] = "none"
    filter_source: Literal["extracted", "oracle"] = "extracted"
    dedupe: bool = True


@dataclass
class ContextConfig:
    max_tokens: int = 3000
    order: str = "rank"  # "rank", or "gold_at:<i>" for experiment E8


@dataclass
class LLMConfig:
    provider: str = "anthropic"  # see DECISIONS.md, D3
    model: str = "claude-haiku-5-5"
    temperature: float = 0.0
    max_tokens: int = 512
    timeout_s: float = 60.0
    cache: bool = True  # False for E0, or the noise floor would be zero
    fake: bool = False  # True in CI: canned JSON answers, no API key


@dataclass
class PromptConfig:
    template: str = "grounded_v1"


@dataclass
class EvalConfig:
    questions: str = "eval/questions.jsonl"
    split: Literal["dev", "test"] = "dev"
    runs_dir: str = "eval/runs"  # each run writes <runs_dir>/<run_name>/


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
    """Read a YAML file into a validated Config. Raises ConfigError."""
    path = Path(path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ConfigError(f"{path}: not valid YAML: {e}") from e
    try:
        return config_from_dict(data or {})
    except ConfigError as e:
        raise ConfigError(f"{path}: {e}") from None


def config_from_dict(data: dict[str, Any]) -> Config:
    """Build and validate a Config from already-parsed YAML."""
    cfg = _build(Config, data, prefix="")
    _validate(cfg)
    return cfg


def _build(cls: type, data: Any, prefix: str) -> Any:
    """Turn a dict into dataclass `cls`, checking every key and value."""
    where = prefix.rstrip(".") or "the config"
    if data is None:  # an empty section such as "parse:" with nothing under it
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(f"'{where}' must be a mapping of keys, got {data!r}")

    known = [f.name for f in fields(cls)]
    for key in data:
        if key not in known:
            hint = get_close_matches(str(key), known, n=1)
            suggestion = f" Did you mean '{prefix}{hint[0]}'?" if hint else ""
            raise ConfigError(
                f"unknown key '{prefix}{key}'.{suggestion} Allowed here: {', '.join(known)}"
            )

    hints = get_type_hints(cls)
    values = {
        name: _convert(hints[name], data[name], f"{prefix}{name}") for name in known if name in data
    }
    return cls(**values)


def _convert(tp: Any, value: Any, key: str) -> Any:
    """Check one value against its declared type. bool is never accepted as a
    number (in Python, True == 1), and an int is widened to float."""
    if is_dataclass(tp):
        return _build(tp, value, prefix=f"{key}.")
    if get_origin(tp) is Literal:
        allowed = get_args(tp)
        if value not in allowed:
            raise ConfigError(f"'{key}' must be one of {list(allowed)}, got {value!r}")
        return value
    if tp is bool:
        if not isinstance(value, bool):
            raise ConfigError(f"'{key}' must be true or false, got {value!r}")
        return value
    if tp is int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ConfigError(f"'{key}' must be a whole number, got {value!r}")
        return value
    if tp is float:
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ConfigError(f"'{key}' must be a number, got {value!r}")
        return float(value)
    if tp is str:
        if not isinstance(value, str):
            raise ConfigError(f"'{key}' must be text, got {value!r} (put it in quotes)")
        return value
    raise TypeError(f"config.py cannot handle the type of '{key}': {tp!r}")


def _validate(cfg: Config) -> None:
    """Checks that involve more than one value, or a range."""
    problems: list[str] = []

    def need(ok: bool, message: str) -> None:
        if not ok:
            problems.append(message)

    need(
        re.fullmatch(r"[A-Za-z0-9._-]+", cfg.run_name) is not None,
        "'run_name' becomes a folder name: use only letters, digits, '.', '_' and '-'",
    )
    need(cfg.parse.min_chars_text_layer >= 0, "'parse.min_chars_text_layer' must be >= 0")
    need(
        0 < cfg.clean.header_footer_min_share <= 1,
        "'clean.header_footer_min_share' must be between 0 and 1",
    )
    need(cfg.chunk.max_tokens > 0, "'chunk.max_tokens' must be > 0")
    need(
        0 <= cfg.chunk.overlap_tokens < cfg.chunk.max_tokens,
        "'chunk.overlap_tokens' must be >= 0 and smaller than 'chunk.max_tokens'",
    )
    need(cfg.chunk.overlap_sentences >= 0, "'chunk.overlap_sentences' must be >= 0")
    need(cfg.embed.batch_size > 0, "'embed.batch_size' must be > 0")
    need(cfg.retrieve.k >= 1, "'retrieve.k' must be >= 1")
    need(
        cfg.retrieve.depth >= cfg.retrieve.k,
        "'retrieve.depth' must be >= 'retrieve.k' (the trace needs ranks beyond k)",
    )
    need(cfg.context.max_tokens > 0, "'context.max_tokens' must be > 0")
    need(
        re.fullmatch(r"rank|gold_at:\d+", cfg.context.order) is not None,
        "'context.order' must be 'rank' or 'gold_at:<position>', e.g. 'gold_at:5'",
    )
    need(cfg.llm.temperature >= 0, "'llm.temperature' must be >= 0")
    need(cfg.llm.max_tokens > 0, "'llm.max_tokens' must be > 0")
    need(cfg.llm.timeout_s > 0, "'llm.timeout_s' must be > 0")

    if problems:
        raise ConfigError("; ".join(problems))


# ---------------------------------------------------------------------------
# Saving and fingerprinting
# ---------------------------------------------------------------------------


def config_to_dict(cfg: Config) -> dict[str, Any]:
    return asdict(cfg)


def save_config(cfg: Config, path: str | Path) -> None:
    """Write the resolved config (every default filled in) as YAML."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(config_to_dict(cfg), sort_keys=False, allow_unicode=True)
    path.write_text(text, encoding="utf-8")


def stage_hash(cfg: Config, *keys: str) -> str:
    """A 12-character fingerprint of only the named settings.

    Keys are section names ("parse") or single settings ("embed.model"):

        stage_hash(cfg, "parse", "clean")                    # parsed documents
        stage_hash(cfg, "parse", "clean", "chunk", "embed.model")  # chunks

    The chunk key includes "embed.model" because chunk sizes are counted with
    that model's tokenizer. The order of `keys` does not matter.
    """
    if not keys:
        raise ValueError("stage_hash needs at least one section or setting name")
    payload = {key: _lookup(cfg, key) for key in sorted(set(keys))}
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def _lookup(cfg: Config, dotted: str) -> Any:
    node: Any = cfg
    for part in dotted.split("."):
        if not is_dataclass(node) or part not in {f.name for f in fields(node)}:
            raise ConfigError(f"stage_hash: no config setting called '{dotted}'")
        node = getattr(node, part)
    return asdict(node) if is_dataclass(node) else node
