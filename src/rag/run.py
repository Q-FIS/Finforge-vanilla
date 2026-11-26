"""Run the whole pipeline on the evaluation questions, and save the results.

Owner: E2        Issue: EVAL-05 (issues/EVAL-05.md)

    uv run python -m rag.run --config config.yaml
    uv run python -m rag.run --config config.yaml --name fixed_256 --overwrite

Every run is saved in its own folder, <eval.runs_dir>/<run_name>/:

    config.yaml     every setting this run used
    commit.txt      which version of the code ran
    results.jsonl   what happened to each question (one rag.schema.Result per line)
    metrics.json    the scores, overall and per question category

This file only CALLS the other steps. When someone replaces a stub with
real code, this file does not change.

STUB(EVAL-05): nothing is cached yet, so every run starts from the PDFs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from rag.config import Config, ConfigError, check_values, load_config, save_config
from rag.failure_trace import trace
from rag.gen.citations import validate_citations
from rag.gen.context import build_context
from rag.gen.generate import generate_answer
from rag.gen.llm import get_llm
from rag.registry import load_registry, pdf_path
from rag.rep.chunking import chunk_document
from rag.rep.clean import clean_document
from rag.rep.embed import get_embedder
from rag.rep.metadata import add_metadata, embedding_text
from rag.rep.parse import parse_pdf
from rag.ret import metrics
from rag.ret.retrieve import DenseIndex, retrieve
from rag.ret.tfidf import TfidfIndex
from rag.schema import Filters, Question, Result, Retrieval, load_jsonl, save_jsonl
from rag.score import score


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m rag.run")
    parser.add_argument("--config", required=True, help="the config YAML file")
    parser.add_argument("--name", help="run name (replaces run_name from the config)")
    parser.add_argument("--final", action="store_true", help="allow the locked test questions")
    parser.add_argument("--overwrite", action="store_true", help="replace a run with this name")
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config)
    except ConfigError as error:
        print(f"config error: {error}", file=sys.stderr)
        return 2
    if args.name:
        cfg.run_name = args.name
        try:
            check_values(cfg)
        except ConfigError as error:
            print(f"config error: {error}", file=sys.stderr)
            return 2

    # Safety checks before doing any work.
    if cfg.eval.split == "test" and not args.final:
        print("The test questions are locked. Use --final (milestones only).", file=sys.stderr)
        return 2
    runs_root = Path(cfg.eval.runs_dir).resolve()
    run_dir = (runs_root / cfg.run_name).resolve()
    if not run_dir.is_relative_to(runs_root):
        print("config error: run_name escapes eval.runs_dir", file=sys.stderr)
        return 2
    if (run_dir / "results.jsonl").exists() and not args.overwrite:
        print(f"{run_dir} already exists. Use another --name, or --overwrite.", file=sys.stderr)
        return 2

    all_questions = load_jsonl(cfg.eval.questions, Question)
    questions_by_id = {q.id: q for q in all_questions}
    results = run_pipeline(cfg, all_questions)
    save_run(run_dir, cfg, results, questions_by_id)
    print(f"Run '{cfg.run_name}': {len(results)} questions. Saved in {run_dir}")
    return 0


def _verify_pdf_sha256(path: Path, expected_sha256: str) -> None:
    """Verify PDF checksum when the registry provides one."""
    if not expected_sha256:
        return
    with path.open("rb") as f:
        actual = hashlib.file_digest(f, "sha256").hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"{path}: sha256 mismatch (expected {expected_sha256}, got {actual})")


def run_pipeline(cfg: Config, all_questions: list[Question] | None = None) -> list[Result]:
    """Steps 1-5 once for all documents, then steps 6-10 for each question."""
    registry = load_registry(cfg.corpus.registry)

    # Steps 1-4: parse, clean, chunk and label every document.
    docs = []
    chunks = []
    for entry in registry.values():
        path = pdf_path(entry, cfg.corpus.pdf_dir)
        _verify_pdf_sha256(path, entry.sha256)
        doc = parse_pdf(path, entry.doc_id, cfg.parse)
        doc = clean_document(doc, cfg.clean)
        doc_chunks = chunk_document(doc, cfg.chunk, cfg.embed)
        doc_chunks = add_metadata(doc_chunks, doc, registry)
        docs.append(doc)
        chunks.extend(doc_chunks)

    # Step 5: embed every chunk and build the two search indexes.
    embedder = get_embedder(cfg.embed)
    vectors = embedder.embed([embedding_text(c, cfg.chunk) for c in chunks], "passage")
    dense = DenseIndex.build(chunks, vectors, embedder.model_name)
    tfidf = TfidfIndex.build(chunks)
    llm = get_llm(cfg.llm)

    # Steps 6-10 for every question in the chosen split (dev or test).
    if all_questions is None:
        all_questions = load_jsonl(cfg.eval.questions, Question)
    questions = [q for q in all_questions if q.split == cfg.eval.split]
    results = []
    for question in questions:
        # Step 6: retrieve.
        if cfg.retrieve.method == "none":  # "closed-book": no passages at all
            retrieval = Retrieval(question.question, [], Filters(), "none", 0.0, 0.0, 0.0)
        elif cfg.retrieve.method == "oracle":
            raise NotImplementedError("retrieve.method 'oracle' is issue EVAL-09")
        else:
            oracle_filters = None
            if cfg.retrieve.filter_source == "oracle":
                oracle_filters = Filters(company=question.company or None, fy=question.fy or None)
            retrieval = retrieve(
                question.question, dense, tfidf, embedder, registry, cfg.retrieve, oracle_filters
            )

        # Steps 7-8: build the prompt's passages, and ask the model.
        context = build_context(retrieval.hits[: cfg.retrieve.k], cfg.context)
        answer = generate_answer(question.question, context, llm, cfg.prompt)

        # Steps 9-10: check citations, score, and record everything.
        report = validate_citations(answer, context)
        status_correct, correct = score(question, answer, report)
        relevant = metrics.relevance(retrieval.hits, question)
        result = Result(
            question_id=question.id,
            retrieved=[(hit.chunk.chunk_id, hit.score) for hit in retrieval.hits],
            relevant_ranks=[i + 1 for i, rel in enumerate(relevant) if rel == 1],
            evidence_found_at=metrics.evidence_ranks(retrieval.hits, question),
            context_ids=[p.chunk.chunk_id for p in context.passages],
            dropped_ids=[chunk_id for chunk_id, _reason in context.dropped],
            answer=answer,
            status_correct=status_correct,
            correct=correct,
            citations=report,
        )
        result.trace_label = trace(question, result, docs, chunks)
        results.append(result)
    return results


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------


def save_run(
    run_dir: Path,
    cfg: Config,
    results: list[Result],
    questions_by_id: dict[str, Question] | None = None,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    save_config(cfg, run_dir / "config.yaml")
    (run_dir / "commit.txt").write_text(git_commit() + "\n", encoding="utf-8")
    save_jsonl(run_dir / "results.jsonl", results)

    # Scores overall, and separately for each question category.
    questions = (
        questions_by_id
        if questions_by_id is not None
        else {q.id: q for q in load_jsonl(cfg.eval.questions, Question)}
    )
    by_category: dict[str, list[Result]] = {}
    for result in results:
        category = questions[result.question_id].category
        by_category.setdefault(category, []).append(result)

    labels: dict[str, int] = {}
    for result in results:
        label = result.trace_label or "correct"
        labels[label] = labels.get(label, 0) + 1

    report = {
        "overall": average_scores(results, cfg.retrieve.k),
        "by_category": {cat: average_scores(rs, cfg.retrieve.k) for cat, rs in by_category.items()},
        "trace_labels": labels,
    }
    (run_dir / "metrics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def average_scores(results: list[Result], k: int) -> dict:
    """The average of each score over `results`."""
    if not results:
        return {"n": 0}
    graded = [r for r in results if r.correct is not None]
    rows = []
    for r in results:
        # 1/0 per retrieved hit: was that rank one of the relevant ones?
        rels = [1 if rank in r.relevant_ranks else 0 for rank in range(1, len(r.retrieved) + 1)]
        rows.append(
            {
                f"hit@{k}": metrics.hit_at_k(rels, k),
                f"recall@{k}": metrics.recall_at_k(r.evidence_found_at, k),
                "mrr": metrics.mrr(rels),
                f"ndcg@{k}": metrics.ndcg_at_k(rels, k),
            }
        )
    scores = {name: sum(row[name] for row in rows) / len(rows) for name in rows[0]}
    return {
        "n": len(results),
        "status_accuracy": sum(r.status_correct for r in results) / len(results),
        "answer_accuracy": sum(bool(r.correct) for r in graded) / len(graded) if graded else None,
        "needs_human_grading": len(results) - len(graded),
        "citations_ok": sum(r.citations.ok for r in results) / len(results),
        **scores,
    }


def git_commit() -> str:
    """The current git commit, plus a warning if there were unsaved changes
    (then the run cannot be repeated exactly)."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        changes = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown (not a git folder)"
    if changes:
        return f"{commit} (with uncommitted changes)"
    return commit


if __name__ == "__main__":
    raise SystemExit(main())
