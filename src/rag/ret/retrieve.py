"""Step 6: find the chunks most similar to a question.

Owner: T2        Issues: RET-04 (DenseIndex), RET-07 (retrieve)

DenseIndex holds one vector per chunk. To search, we embed the question and
compare it with every chunk vector (a dot product), then keep the best k.

STUB: DenseIndex.search() returns the first k chunks with score 0, and
retrieve() does not use filters yet.
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
        self.chunks = chunks  # chunk i belongs to row i of vectors
        self.vectors = vectors  # shape (number of chunks, vector size)
        self.model_name = model_name  # which embedding model made the vectors

    @classmethod
    def build(cls, chunks: list[Chunk], vectors: np.ndarray, model_name: str) -> DenseIndex:
        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
        return cls(chunks, vectors, model_name)

    def search(
        self, query_vector: np.ndarray, k: int, allowed: np.ndarray | None = None
    ) -> list[Hit]:
        """The k chunks whose vectors have the highest dot product with
        query_vector, best first. `allowed` works as in TfidfIndex.search."""
        hits = []
        for i, chunk in enumerate(self.chunks):  # STUB(RET-04): no scoring yet
            if allowed is not None and not allowed[i]:
                continue
            hits.append(Hit(chunk=chunk, score=0.0, rank=len(hits) + 1, method="dense"))
            if len(hits) == k:
                break
        return hits


def retrieve(
    question: str,
    dense: DenseIndex,
    tfidf: TfidfIndex,
    embedder: Embedder,
    registry: dict[str, RegistryEntry],
    cfg: RetrieveConfig,
    oracle_filters: Filters | None = None,
) -> Retrieval:
    """Search for one question and return a Retrieval (the hits + details).

    Always fetches cfg.depth hits (20), even though only cfg.k go into the
    prompt: the failure trace needs to see ranks k+1 to 20.
    """
    start = time.perf_counter()
    filters = Filters()  # STUB(RET-07): use extract_filters() or oracle_filters

    if cfg.method == "dense":
        query_vector = embedder.embed([question], "query")[0]
        hits = dense.search(query_vector, cfg.depth)
    elif cfg.method == "tfidf":
        hits = tfidf.search(question, cfg.depth)
    else:
        raise ValueError(f"retrieve() handles 'dense' and 'tfidf', not {cfg.method!r}")

    if cfg.dedupe:
        hits = dedupe(hits)

    top_score = hits[0].score if hits else 0.0
    second_score = hits[1].score if len(hits) > 1 else top_score
    return Retrieval(
        question=question,
        hits=hits,
        filters=filters,
        filter_mode=cfg.filter,
        top_score=top_score,
        gap=top_score - second_score,
        latency_ms=(time.perf_counter() - start) * 1000,
    )
