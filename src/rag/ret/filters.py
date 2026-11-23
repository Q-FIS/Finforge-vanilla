"""RET: metadata filters and de-duplication. Owner T3.

STUB(RET-08, RET-09, RET-10). Today nothing is filtered or removed.
"""

from __future__ import annotations

import numpy as np

from rag.schema import Chunk, Filters, Hit, RegistryEntry


def extract_filters(question: str, registry: dict[str, RegistryEntry]) -> Filters:
    """Company (via registry aliases), FY ("FY 2024-25" -> "FY2025") and basis
    from the question's words. Ambiguous (two companies/years) -> None."""
    return Filters(source="extracted")  # STUB(RET-08)


def allowed_mask(chunks: list[Chunk], filters: Filters) -> np.ndarray:
    """Boolean mask: True where a chunk matches every non-None filter."""
    return np.ones(len(chunks), dtype=bool)  # STUB(RET-09)


def dedupe(hits: list[Hit]) -> list[Hit]:
    """Drop hits that mostly repeat a better-ranked hit (overlapping chunks),
    then renumber ranks from 1."""
    return hits  # STUB(RET-10)
