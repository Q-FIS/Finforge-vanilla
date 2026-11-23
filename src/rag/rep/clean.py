"""Step 2: clean the text of a parsed Document.

Owner: R1        Issue: REP-02 (issues/REP-02.md)

Cleaning fixes things like broken hyphenation and repeated headers, but
must never change figures: "₹", "crore", "1,45,000", "(1,234)" and "—"
stay exactly as they are.

STUB: right now the document is returned unchanged.
"""

from __future__ import annotations

from rag.config import CleanConfig
from rag.schema import Document


def clean_document(doc: Document, cfg: CleanConfig) -> Document:
    """Return the cleaned Document. It must have the same number of pages."""
    return doc  # STUB(REP-02): nothing is cleaned yet
