"""RET: TF-IDF index, written by hand. Owner T1.

STUB(RET-01, RET-02). Today `search` returns the first k chunks, score 0.
"""

from __future__ import annotations

import numpy as np

from rag.schema import Chunk, Hit


class TfidfIndex:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks

    @classmethod
    def build(cls, chunks: list[Chunk]) -> TfidfIndex:
        """Vocabulary, document frequencies, smoothed IDF, L2-normalised vectors."""
        return cls(chunks)  # STUB(RET-02)

    def search(self, query: str, k: int, allowed: np.ndarray | None = None) -> list[Hit]:
        """Top-k chunks by cosine similarity. `allowed` is a boolean mask over
        self.chunks (pre-filtering); None means every chunk is allowed."""
        pool = [c for i, c in enumerate(self.chunks) if allowed is None or allowed[i]]
        return [Hit(c, 0.0, r + 1, "tfidf") for r, c in enumerate(pool[:k])]  # STUB
