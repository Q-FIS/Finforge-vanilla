"""Check the model's citations with plain code (no LLM).

Owner: G4        Issue: GEN-09 (issues/GEN-09.md)

Catches: tags that were not in the prompt, quotes that are not really in
their passage, and numbers in the answer that no cited passage contains.

STUB: every answer passes.
"""

from __future__ import annotations

from rag.schema import Answer, CitationReport, Context


def validate_citations(answer: Answer, context: Context) -> CitationReport:
    """Return a CitationReport. Empty lists mean "no problems found"."""
    return CitationReport()  # STUB(GEN-09): no checks yet
