"""REP: Document -> cleaned Document. Owner R1.

STUB(REP-02). Today the document passes through unchanged.
"""

from __future__ import annotations

from rag.config import CleanConfig
from rag.schema import Document


def clean_document(doc: Document, cfg: CleanConfig) -> Document:
    """NFKC, whitespace, line-break hyphens, headers/footers, page labels.

    Contract: never changes the number of pages; keeps "₹", "crore",
    "1,45,000", "(1,234)" and "—" exactly as they are.
    """
    return doc  # STUB(REP-02)
