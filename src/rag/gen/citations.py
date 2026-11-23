"""GEN: structural citation checks, no LLM. Owner G4.

STUB(GEN-09). Today every answer passes.
"""

from __future__ import annotations

from rag.schema import Answer, CitationReport, Context


def validate_citations(answer: Answer, context: Context) -> CitationReport:
    """Tags exist in the context; quotes appear word for word in their passage
    (rag.match.coverage == 1.0); every amount in the answer appears in a cited
    passage (rag.amounts); every sentence with a figure has a tag."""
    return CitationReport()  # STUB(GEN-09)
