"""EVAL: label the first stage where a wrong answer lost its evidence. Owner E3.

Named `failure_trace`, not `trace`: `trace` is a built-in Python module.

STUB(EVAL-08). Today every wrong answer is labelled GENERATE.
"""

from __future__ import annotations

from rag.schema import Chunk, Document, Question, Result, TraceLabel


def trace(
    question: Question, result: Result, docs: list[Document], chunks: list[Chunk]
) -> TraceLabel:
    """PARSE, CHUNK, NOT_RETRIEVED, RANKED_LOW, DROPPED, WRONG_STATUS or
    GENERATE, checked in that order; "" when the answer is correct."""
    if result.correct or (result.correct is None and result.status_correct):
        return ""
    return "GENERATE"  # STUB(EVAL-08)
