"""F-03: config loading, validation and stage hashes."""

from pathlib import Path

import pytest

from rag.config import (
    Config,
    ConfigError,
    config_from_dict,
    load_config,
    save_config,
    stage_hash,
)

REPO = Path(__file__).resolve().parents[1]


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "cfg.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_repo_configs_load():
    cfg = load_config(REPO / "config.yaml")
    assert cfg.chunk.strategy == "section"
    assert cfg.llm.effort == "low"
    ci = load_config(REPO / "tests" / "ci.yaml")
    assert ci.embed.fake and ci.llm.fake


def test_missing_keys_take_defaults():
    assert config_from_dict({}) == Config()


def test_unknown_key_raises_and_suggests(tmp_path):
    path = write(tmp_path, "chunk:\n  max_tokenz: 256\n")
    with pytest.raises(ConfigError) as err:
        load_config(path)
    message = str(err.value)
    assert "chunk.max_tokenz" in message
    assert "Did you mean 'chunk.max_tokens'" in message


def test_unknown_section_raises():
    with pytest.raises(ConfigError, match="unknown key 'chunking'"):
        config_from_dict({"chunking": {}})


@pytest.mark.parametrize(
    ("data", "fragment"),
    [
        ({"chunk": {"strategy": "semantic"}}, "chunk.strategy"),
        ({"chunk": {"max_tokens": "512"}}, "chunk.max_tokens"),
        ({"embed": {"fake": "yes"}}, "embed.fake"),
        ({"retrieve": {"filter": False}}, "retrieve.filter"),  # YAML `off` -> False
        ({"chunk": "big"}, "must contain keys"),
    ],
)
def test_bad_values_raise(data, fragment):
    with pytest.raises(ConfigError, match=fragment):
        config_from_dict(data)


@pytest.mark.parametrize(
    ("data", "fragment"),
    [
        ({"chunk": {"max_tokens": 256, "overlap_tokens": 256}}, "overlap_tokens"),
        ({"retrieve": {"k": 10, "depth": 5}}, "depth"),
        ({"context": {"order": "middle"}}, "gold_at"),
        ({"run_name": "my run"}, "run_name"),
        ({"llm": {"max_tokens": 0}}, "llm.max_tokens"),
    ],
)
def test_contradictions_raise(data, fragment):
    with pytest.raises(ConfigError, match=fragment):
        config_from_dict(data)


def test_int_is_widened_to_float():
    cfg = config_from_dict({"llm": {"timeout_s": 30}})
    assert cfg.llm.timeout_s == 30.0 and isinstance(cfg.llm.timeout_s, float)


def test_empty_section_is_allowed(tmp_path):
    assert load_config(write(tmp_path, "parse:\n")) == Config()


def test_invalid_yaml_names_the_file(tmp_path):
    with pytest.raises(ConfigError, match="cfg.yaml"):
        load_config(write(tmp_path, "chunk: [unclosed\n"))


def test_save_then_load_is_identical(tmp_path):
    cfg = config_from_dict({"run_name": "e1_fixed_256", "chunk": {"strategy": "fixed"}})
    save_config(cfg, tmp_path / "out.yaml")
    assert load_config(tmp_path / "out.yaml") == cfg


# --- stage_hash ------------------------------------------------------------


def test_stage_hash_is_short_and_stable():
    h = stage_hash(Config(), "parse", "clean")
    assert len(h) == 12
    assert h == stage_hash(Config(), "parse", "clean")
    assert h == stage_hash(Config(), "clean", "parse")  # order does not matter


def test_stage_hash_only_sees_its_sections():
    base = Config()
    changed = config_from_dict({"chunk": {"max_tokens": 256}})
    # The parse cache must survive a chunking change...
    assert stage_hash(base, "parse", "clean") == stage_hash(changed, "parse", "clean")
    # ...but the chunk cache must not.
    assert stage_hash(base, "parse", "clean", "chunk") != stage_hash(
        changed, "parse", "clean", "chunk"
    )


def test_stage_hash_dotted_setting():
    a = config_from_dict({"embed": {"batch_size": 8}})
    b = config_from_dict({"embed": {"model": "intfloat/e5-small-v2"}})
    # batch size does not change chunks; the model (its tokenizer) does
    assert stage_hash(a, "chunk", "embed.model") == stage_hash(Config(), "chunk", "embed.model")
    assert stage_hash(b, "chunk", "embed.model") != stage_hash(Config(), "chunk", "embed.model")


def test_stage_hash_separates_identical_sections():
    # Different keys with equal contents must not collide.
    assert stage_hash(Config(), "prompt") != stage_hash(Config(), "parse")


def test_stage_hash_rejects_unknown_names():
    with pytest.raises(ConfigError, match="chunks"):
        stage_hash(Config(), "chunks")
    with pytest.raises(ValueError):
        stage_hash(Config())
