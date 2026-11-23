"""EVAL: one command runs the whole pipeline and writes one run folder. Owner E2.

    python -m rag.run --config config.yaml
    python -m rag.run --config config.yaml --name e1_fixed_256 --overwrite

Writes <eval.runs_dir>/<run_name>/:

    config.yaml     the resolved config (every default filled in)
    commit.txt      the git commit, and whether there were uncommitted changes
    results.jsonl   one rag.schema.Result per question
    metrics.json    the averages, overall and per category, plus trace labels

This is the walking skeleton (F-07): every stage is called through its
public function, so when an owner replaces a stub, the run uses the real
code with no change here. STUB(EVAL-05): stage caching under data/cache/.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from rag.config import Config, ConfigError, load_config, save_config
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
from rag.ret import metrics as m
from rag.ret.retrieve import DenseIndex, retrieve
from rag.ret.tfidf import TfidfIndex
from rag.schema import Chunk, Document, Filters, Question, Result, Retrieval, load_jsonl, save_jsonl
from rag.score import score


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m rag.run")
    parser.add_argument("--config", required=True, help="path to a config YAML file")
    parser.add_argument("--name", help="run name (overrides run_name in the config)")
    parser.add_argument("--final", action="store_true", help="allow the locked test split")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing run")
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config)
    except ConfigError as e:
        print(f"config error: {e}", file=sys.stderr)
        return 2
    if args.name:
        cfg.run_name = args.name
    if cfg.eval.split == "test" and not args.final:
        print("the test split is locked: pass --final (milestones only)", file=sys.stderr)
        return 2
    run_dir = Path(cfg.eval.runs_dir) / cfg.run_name
    if (run_dir / "results.jsonl").exists() and not args.overwrite:
        print(f"{run_dir} already exists: pick another --name or pass --overwrite", file=sys.stderr)
        return 2

    results = run(cfg)
    write_run_folder(run_dir, cfg, results)
    print(f"run '{cfg.run_name}': {len(results)} questions -> {run_dir}")
    return 0


def run(cfg: Config) -> list[Result]:
    """Index the corpus, then answer every question in the configured split."""
    registry = load_registry(cfg.corpus.registry)

    # 1-4. parse, clean, chunk, metadata (per document)
    docs: list[Document] = []
    chunks: list[Chunk] = []
    for entry in registry.values():
        doc = parse_pdf(pdf_path(entry, cfg.corpus.pdf_dir), entry.doc_id, cfg.parse)
        doc = clean_document(doc, cfg.clean)
        doc_chunks = chunk_document(doc, cfg.chunk, cfg.embed.model)
        chunks.extend(add_metadata(doc_chunks, doc, registry))
        docs.append(doc)

    # 5-6. embed and index
    embedder = get_embedder(cfg.embed)
    vectors = embedder.embed([embedding_text(c, cfg.chunk) for c in chunks], "passage")
    dense = DenseIndex.build(chunks, vectors, embedder.model_name)
    tfidf = TfidfIndex.build(chunks)
    llm = get_llm(cfg.llm)

    questions = [q for q in load_jsonl(cfg.eval.questions, Question) if q.split == cfg.eval.split]
    results = []
    for q in questions:
        # 7. retrieve
        if cfg.retrieve.method in ("dense", "tfidf"):
            oracle = Filters(q.company or None, q.fy or None, None, "oracle")
            retrieval = retrieve(
                q.question,
                dense=dense,
                tfidf=tfidf,
                embedder=embedder,
                registry=registry,
                cfg=cfg.retrieve,
                oracle_filters=oracle if cfg.retrieve.filter_source == "oracle" else None,
            )
        elif cfg.retrieve.method == "none":  # closed-book: no passages at all
            retrieval = Retrieval(q.question, [], Filters(), "none", 0.0, 0.0, 0.0)
        else:
            raise NotImplementedError("retrieve.method 'oracle' is issue EVAL-09")

        # 8-9. context and answer
        context = build_context(retrieval.hits[: cfg.retrieve.k], cfg.context)
        answer = generate_answer(q.question, context, llm, cfg.prompt)

        # 10. check and score
        report = validate_citations(answer, context)
        status_correct, correct = score(q, answer, report)
        rels = m.relevance(retrieval.hits, q)
        result = Result(
            question_id=q.id,
            retrieved=[(h.chunk.chunk_id, h.score) for h in retrieval.hits],
            relevant_ranks=[h.rank for h, r in zip(retrieval.hits, rels, strict=True) if r],
            evidence_found_at=m.evidence_ranks(retrieval.hits, q),
            context_ids=[p.chunk.chunk_id for p in context.passages],
            dropped_ids=[chunk_id for chunk_id, _ in context.dropped],
            answer=answer,
            status_correct=status_correct,
            correct=correct,
            citations=report,
        )
        result.trace_label = trace(q, result, docs, chunks)
        results.append(result)
    return results


def summarize(results: list[Result], questions: dict[str, Question], k: int) -> dict:
    """Averages overall and per category, and trace-label counts."""

    def block(rs: list[Result]) -> dict:
        n = len(rs)
        graded = [r for r in rs if r.correct is not None]
        rels = {
            r.question_id: [int(i + 1 in r.relevant_ranks) for i in range(len(r.retrieved))]
            for r in rs
        }
        return {
            "n": n,
            "status_accuracy": sum(r.status_correct for r in rs) / n if n else 0.0,
            "answer_accuracy": (
                sum(bool(r.correct) for r in graded) / len(graded) if graded else None
            ),
            "ungraded": n - len(graded),
            f"hit@{k}": _mean([m.hit_at_k(rels[r.question_id], k) for r in rs]),
            f"recall@{k}": _mean([m.recall_at_k(r.evidence_found_at, k) for r in rs]),
            "mrr": _mean([m.mrr(rels[r.question_id]) for r in rs]),
            f"ndcg@{k}": _mean([m.ndcg_at_k(rels[r.question_id], k) for r in rs]),
            "citations_ok": _mean([float(r.citations.ok) for r in rs]),
        }

    by_cat: dict[str, list[Result]] = defaultdict(list)
    for r in results:
        by_cat[questions[r.question_id].category].append(r)
    return {
        "overall": block(results),
        "by_category": {cat: block(rs) for cat, rs in sorted(by_cat.items())},
        "trace_labels": dict(Counter(r.trace_label or "correct" for r in results)),
    }


def write_run_folder(run_dir: Path, cfg: Config, results: list[Result]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    save_config(cfg, run_dir / "config.yaml")
    (run_dir / "commit.txt").write_text(_git_state() + "\n", encoding="utf-8")
    save_jsonl(run_dir / "results.jsonl", results)
    questions = {q.id: q for q in load_jsonl(cfg.eval.questions, Question)}
    metrics = summarize(results, questions, cfg.retrieve.k)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _git_state() -> str:
    """'<commit>' or '<commit> (dirty)'; a dirty run cannot be reproduced exactly."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown (not a git checkout, or no commits yet)"
    return f"{commit} (dirty: uncommitted changes)" if dirty else commit


if __name__ == "__main__":
    raise SystemExit(main())
