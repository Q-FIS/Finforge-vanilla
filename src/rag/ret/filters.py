"""Read company / year / basis from a question, and use them to filter chunks.

Owner: T3        Issues: RET-08, RET-09, RET-10

Example: "What was Infosys' revenue in FY 2024-25?" -> Filters(company="infosys",
fy="FY2025"). Then only chunks with those labels are searched.

STUB: nothing is extracted, nothing is filtered, nothing is removed.
"""

from __future__ import annotations

import numpy as np

from rag.schema import Chunk, Filters, Hit, RegistryEntry


def extract_filters(question: str, registry: dict[str, RegistryEntry]) -> Filters:
    """Find the company, financial year and basis the question asks about.
    Leave a field as None when the question does not say, or is ambiguous."""
    return Filters(source="extracted")  # STUB(RET-08): finds nothing yet


def allowed_mask(chunks: list[Chunk], filters: Filters) -> np.ndarray:
    """One True/False per chunk: True if the chunk matches every filter."""
    return np.ones(len(chunks), dtype=bool)  # STUB(RET-09): everything allowed


def dedupe(hits: list[Hit]) -> list[Hit]:
    """Remove hits that mostly repeat a better hit (overlapping chunks)."""
    return hits  # STUB(RET-10): nothing removed
