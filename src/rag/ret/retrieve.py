"""RET: dense index and the retrieve() entry point. Owner T2.

STUB(RET-04): DenseIndex.search returns the first k chunks with score 0.
STUB(RET-07): retrieve() does not filter yet.
"""

from __future__ import annotations

import time

import numpy as np

from rag.config import RetrieveConfig
from rag.rep.embed import Embedder
from rag.ret.filters import dedupe
from rag.ret.tfidf import TfidfIndex
from rag.schema import Chunk, Filters, Hit, RegistryEntry, Retrieval


class DenseIndex:
    def __init__(self, chunks: list[Chunk], vectors: np.ndarray, model_name: str) -> None:
        self.chunks = chunks
        self.vectors = vectors
        self.model_name = model_name

    @classmethod
    def build(cls, chunks: list[Chunk], vectors: np.ndarray, model_name: str) -> DenseIndex:
        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
        return cls(chunks, vectors, model_name)

    def search(self, qvec: np.ndarray, k: int, allowed: np.ndarray | None = None) -> list[Hit]:
        """Exact top-k by dot product (= cosine, since rows are unit vectors)."""
        pool = [c for i, c in enumerate(self.chunks) if allowed is None or allowed[i]]
        return [Hit(c, 0.0, r + 1, "dense") for r, c in enumerate(pool[:k])]  # STUB(RET-04)


def retrieve(
    question: str,
    *,
    dense: DenseIndex,
    tfidf: TfidfIndex,
    embedder: Embedder,
    registry: dict[str, RegistryEntry],
    cfg: RetrieveConfig,
    oracle_filters: Filters | None = None,
) -> Retrieval:
    """Fetch `cfg.depth` hits for one question with cfg.method "dense" or
    "tfidf". ("oracle" and "none" are built by run.py, not here.)"""
    start = time.perf_counter()
    filters = Filters()  # STUB(RET-07): extract or take oracle_filters; pre/post filter
    if cfg.method == "dense":
        qvec = embedder.embed([question], "query")[0]
        hits = dense.search(qvec, cfg.depth)
    elif cfg.method == "tfidf":
        hits = tfidf.search(question, cfg.depth)
    else:
        raise ValueError(f"retrieve() handles 'dense' and 'tfidf', not {cfg.method!r}")
    if cfg.dedupe:
        hits = dedupe(hits)
    top = hits[0].score if hits else 0.0
    gap = top - hits[1].score if len(hits) > 1 else 0.0
    return Retrieval(
        question=question,
        hits=hits,
        filters=filters,
        filter_mode=cfg.filter,
        top_score=top,
        gap=gap,
        latency_ms=(time.perf_counter() - start) * 1000,
    )
