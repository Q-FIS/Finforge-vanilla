"""Was the answer right?

Owner: G1        Issue: EVAL-06 (issues/EVAL-06.md)

Returns two things:
  status_correct  did the model answer when it should, and refuse when it should?
  correct         is the answer itself right? None means "a person must check it".

STUB: only the status is checked.
"""

from __future__ import annotations

from rag.schema import Answer, CitationReport, Question


def score(question: Question, answer: Answer, report: CitationReport) -> tuple[bool, bool | None]:
    status_correct = answer.status == question.expected_status
    if question.expected_status != "answered":
        # For "insufficient_evidence" questions, the status IS the answer.
        return status_correct, status_correct
    return status_correct, None  # STUB(EVAL-06): compare the amounts
