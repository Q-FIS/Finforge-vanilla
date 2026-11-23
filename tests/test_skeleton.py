"""F-07: the walking skeleton runs end to end on the fixture with fake models.

As owners replace stubs with real code, this test keeps passing: it checks
the run folder's shape, not the quality of the answers.
"""

from pathlib import Path

import pytest
import yaml

from rag.run import main
from rag.schema import Result, load_jsonl

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def ci_config(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO)  # config paths are relative to the repo root
    cfg = yaml.safe_load((REPO / "tests" / "ci.yaml").read_text(encoding="utf-8"))
    cfg["eval"]["runs_dir"] = str(tmp_path / "runs")
    path = tmp_path / "ci.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return path, tmp_path / "runs" / "smoke"


def test_run_writes_a_complete_folder(ci_config):
    config, run_dir = ci_config
    assert main(["--config", str(config)]) == 0
    for name in ("config.yaml", "commit.txt", "results.jsonl", "metrics.json"):
        assert (run_dir / name).exists(), name
    results = load_jsonl(run_dir / "results.jsonl", Result)
    assert [r.question_id for r in results] == ["FX01", "FX02", "FX03", "FX04"]  # dev only


def test_existing_run_is_not_overwritten_by_accident(ci_config):
    config, _ = ci_config
    assert main(["--config", str(config)]) == 0
    assert main(["--config", str(config)]) == 2
    assert main(["--config", str(config), "--overwrite"]) == 0


def test_test_split_needs_final(ci_config, tmp_path):
    config, _ = ci_config
    cfg = yaml.safe_load(config.read_text(encoding="utf-8"))
    cfg["eval"]["split"] = "test"
    config.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    assert main(["--config", str(config)]) == 2
    assert main(["--config", str(config), "--final"]) == 0


def test_closed_book_mode(ci_config):
    config, run_dir = ci_config
    cfg = yaml.safe_load(config.read_text(encoding="utf-8"))
    cfg["retrieve"] = {"method": "none"}
    config.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    assert main(["--config", str(config)]) == 0
    results = load_jsonl(run_dir / "results.jsonl", Result)
    assert all(r.context_ids == [] for r in results)
    assert all(r.answer.status == "insufficient_evidence" for r in results)
