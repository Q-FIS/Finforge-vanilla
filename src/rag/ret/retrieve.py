"""Step 6: find the chunks most similar to a question.

Owner: T2        Issues: RET-04 (DenseIndex), RET-07 (retrieve)

DenseIndex holds one vector per chunk. To search, we embed the question and
compare it with every chunk vector (a dot product), then keep the best k.

retrieve() does not use filters yet (RET-07).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from rag.config import RetrieveConfig
from rag.rep.embed import Embedder
from rag.ret.filters import dedupe
from rag.ret.tfidf import TfidfIndex
from rag.schema import Chunk, Filters, Hit, RegistryEntry, Retrieval, load_jsonl, save_jsonl


class DenseIndex:
    def __init__(self, chunks: list[Chunk], vectors: np.ndarray, model_name: str) -> None:
        self.chunks = chunks  # chunk i belongs to row i of vectors
        self.vectors = vectors  # shape (number of chunks, vector size)
        self.model_name = model_name  # which embedding model made the vectors

    @classmethod
    def build(cls, chunks: list[Chunk], vectors: np.ndarray, model_name: str) -> DenseIndex:
        if vectors.ndim != 2:
            raise ValueError("vectors must have one row per chunk")
        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
        return cls(chunks, vectors, model_name)

    def search(
        self, query_vector: np.ndarray, k: int, allowed: np.ndarray | None = None
    ) -> list[Hit]:
        """The k chunks whose vectors have the highest dot product with
        query_vector, best first. `allowed` works as in TfidfIndex.search."""
        if query_vector.ndim != 1 or query_vector.shape[0] != self.vectors.shape[1]:
            raise ValueError(
                f"query has {query_vector.size} numbers, index has {self.vectors.shape[1]}"
            )
        if allowed is not None and (allowed.ndim != 1 or len(allowed) != len(self.chunks)):
            raise ValueError(f"allowed has {allowed.size} entries, index has {len(self.chunks)}")
        if k <= 0 or not self.chunks:
            return []

        scores = self.vectors @ query_vector
        if allowed is not None:
            scores = np.where(allowed, scores, -np.inf)
        k = min(k, len(scores))
        partition = np.argpartition(-scores, k - 1)[:k]
        cutoff = scores[partition].min()

        # argpartition does not promise which rows win a tie at the cutoff.
        # Keep all higher scores, then fill the remaining places in row order.
        higher = np.flatnonzero(scores > cutoff)
        tied = np.flatnonzero(scores == cutoff)[: k - len(higher)]
        top = np.sort(np.concatenate((higher, tied)))
        top = top[np.argsort(-scores[top], kind="stable")]
        return [
            Hit(chunk=self.chunks[i], score=float(scores[i]), rank=rank, method="dense")
            for rank, i in enumerate(top, start=1)
            if scores[i] != -np.inf
        ]

    def save(self, folder: str | Path) -> None:
        """Save the vectors, their matching chunks, and the embedding model name."""
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        np.save(folder / "vectors.npy", self.vectors)
        save_jsonl(folder / "chunks.jsonl", self.chunks)
        (folder / "meta.json").write_text(
            json.dumps({"model_name": self.model_name}) + "\n", encoding="utf-8"
        )

    @classmethod
    def load(cls, folder: str | Path) -> DenseIndex:
        """Load an index saved with `save`."""
        folder = Path(folder)
        vectors = np.load(folder / "vectors.npy", allow_pickle=False)
        chunks = load_jsonl(folder / "chunks.jsonl", Chunk)
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        return cls.build(chunks, vectors, meta["model_name"])


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
