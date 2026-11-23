"""REP: texts -> unit vectors. Owner R4.

`FakeEmbedder` is real and permanent: CI and the walking skeleton use it so
they need no model download. STUB(REP-11): the sentence-transformers
embedder behind `get_embedder` when `embed.fake` is false.
"""

from __future__ import annotations

import hashlib
import re
from typing import Literal, Protocol

import numpy as np

from rag.config import EmbedConfig

Kind = Literal["query", "passage"]


class Embedder(Protocol):
    model_name: str
    dim: int

    def embed(self, texts: list[str], kind: Kind) -> np.ndarray:
        """float32 array of shape (len(texts), dim); every row has length 1."""
        ...


class FakeEmbedder:
    """Bag-of-words "hashing trick": each word adds 1 to a dimension chosen by
    its hash. Deterministic, instant, and texts that share words get similar
    vectors, so retrieval on it is crude but not random."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim
        self.model_name = f"fake-hashing-{dim}"

    def embed(self, texts: list[str], kind: Kind) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for word in re.findall(r"\w+", text.lower()):
                digest = hashlib.sha1(word.encode("utf-8")).digest()
                out[i, int.from_bytes(digest[:4], "little") % self.dim] += 1.0
            norm = np.linalg.norm(out[i])
            if norm == 0:  # no words at all: any fixed unit vector will do
                out[i, 0], norm = 1.0, 1.0
            out[i] /= norm
        return out


def get_embedder(cfg: EmbedConfig) -> Embedder:
    if cfg.fake:
        return FakeEmbedder()
    raise NotImplementedError(
        f"Real embeddings ({cfg.model}) are issue REP-11. Set embed.fake: true until then."
    )
