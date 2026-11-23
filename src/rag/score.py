"""EVAL: is an answer right? Owner G1 (EVAL-06).

STUB(EVAL-06). Today only the status is checked.
"""

from __future__ import annotations

from rag.schema import Answer, CitationReport, Question


def score(question: Question, answer: Answer, report: CitationReport) -> tuple[bool, bool | None]:
    """(status_correct, correct). correct is None when a person must grade it
    (text answers). A numeric answer is correct when the status is
    "answered" and some amount in it equals question.answer_value."""
    status_correct = answer.status == question.expected_status
    if question.expected_status != "answered":
        return status_correct, status_correct
    return status_correct, None  # STUB(EVAL-06): numeric checking via rag.amounts
