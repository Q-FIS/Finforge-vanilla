"""Keyword search with TF-IDF, written by hand.

Owner: T1        Issues: RET-01, RET-02 (issues/RET-01.md, issues/RET-02.md)

TF-IDF scores a chunk higher when it contains the question's words,
especially rare words. It is our baseline next to the embedding search.

STUB: search() returns the first k chunks with score 0.
"""

from __future__ import annotations

import numpy as np

from rag.schema import Chunk, Hit


class TfidfIndex:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        # RET-02: also store the vocabulary, document frequencies, IDF
        # values and one vector per chunk here.

    @classmethod
    def build(cls, chunks: list[Chunk]) -> TfidfIndex:
        """Build the index from all chunks."""
        return cls(chunks)  # STUB(RET-02): nothing is computed yet

    def search(self, query: str, k: int, allowed: np.ndarray | None = None) -> list[Hit]:
        """The k chunks most similar to `query`, best first.

        `allowed` is an optional list of True/False, one per chunk. When it
        is given, only chunks marked True may be returned (filtering).
        """
        hits = []
        for i, chunk in enumerate(self.chunks):  # STUB(RET-02): no scoring yet
            if allowed is not None and not allowed[i]:
                continue
            hits.append(Hit(chunk=chunk, score=0.0, rank=len(hits) + 1, method="tfidf"))
            if len(hits) == k:
                break
        return hits
