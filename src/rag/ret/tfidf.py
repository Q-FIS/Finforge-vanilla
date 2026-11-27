"""Keyword search with TF-IDF, written by hand.

Owner: T1        Issues: RET-01, RET-02 (issues/RET-01.md, issues/RET-02.md)

TF-IDF scores a chunk higher when it contains the question's words,
especially rare words. It is our baseline next to the embedding search.

STUB: search() returns the first k chunks with score 0.
"""

from __future__ import annotations

import re

import numpy as np

from rag.schema import Chunk, Hit

_STOPWORDS = {
    "the",
    "of",
    "and",
    "a",
    "an",
    "in",
    "to",
    "for",
    "was",
    "is",
    "on",
    "by",
    "with",
    "as",
    "at",
}

_TOKEN_PATTERN = (
    r"\d{4}-\d{2}"
    r"|\d[\d,]*(?:\.\d+)?"
    r"|[a-z][a-z0-9]*"
    r"|₹|%"
)


def tokenize(text: str, remove_stopwords: bool = False) -> list[str]:
    """Tokenize text while preserving financial terms and numbers."""
    text = text.lower()
    tokens = re.findall(_TOKEN_PATTERN, text)

    tokens = [token.rstrip(",") for token in tokens]

    if remove_stopwords:
        tokens = [token for token in tokens if token not in _STOPWORDS]

    return tokens


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
