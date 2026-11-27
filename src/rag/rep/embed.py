"""Step 5: turn texts into vectors (lists of numbers) with an embedding model.

Owner: R4        Issue: REP-11 (issues/REP-11.md)

Every embedder returns one row per text, and every row has length 1
("normalised"), so comparing two vectors is just a dot product.

FakeEmbedder is finished and stays forever: tests use it so they never
download a model. STUB: the real embedder (sentence-transformers).
"""

from __future__ import annotations

import hashlib

import numpy as np

from rag.config import EmbedConfig


class Embedder:
    """What every embedder has: a model name, a vector size, and embed()."""

    model_name: str = ""
    dim: int = 0

    def embed(self, texts: list[str], kind: str) -> np.ndarray:
        """Return an array of shape (len(texts), dim).

        kind is "query" for questions and "passage" for chunks. Some models
        need a different prefix for each, e.g. "query: " and "passage: ".
        """
        raise NotImplementedError


class FakeEmbedder(Embedder):
    """A pretend model: each word adds 1 to one position of the vector,
    chosen by the word's hash. Texts that share words get similar vectors.
    Instant, needs no download, and gives the same result every time."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim
        self.model_name = f"fake-{dim}"

    def embed(self, texts: list[str], kind: str) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            for word in text.lower().split():
                position = int(hashlib.md5(word.encode()).hexdigest(), 16) % self.dim
                vectors[row, position] += 1.0
            length = np.linalg.norm(vectors[row])
            if length == 0:  # empty text: use any fixed vector of length 1
                vectors[row, 0] = 1.0
            else:
                vectors[row] /= length
        return vectors


def get_embedder(cfg: EmbedConfig) -> Embedder:
    """The embedder the config asks for."""
    if cfg.fake:
        return FakeEmbedder()
    # STUB(REP-11): return the real sentence-transformers embedder here.
    raise NotImplementedError("The real embedder is issue REP-11. Use embed.fake: true for now.")
