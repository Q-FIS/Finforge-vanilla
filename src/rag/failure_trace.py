"""For a wrong answer, find the FIRST step of the pipeline that went wrong.

Owner: E3        Issue: EVAL-08 (issues/EVAL-08.md)

Labels, checked in this order:
  PARSE          the evidence text is missing after parsing
  CHUNK          the evidence was split badly between chunks
  NOT_RETRIEVED  no relevant chunk in the top 20
  RANKED_LOW     a relevant chunk is in the top 20 but not in the top k
  DROPPED        retrieved, but left out of the prompt (token budget)
  WRONG_STATUS   answered when it should have refused, or the opposite
  GENERATE       everything else: the model had the evidence and got it wrong

(Called `failure_trace` and not `trace`, because `trace` is a built-in Python
module. See DECISIONS.md D1.)

STUB: every wrong answer is labelled GENERATE.
"""

from __future__ import annotations

from rag.schema import Chunk, Document, Question, Result


def trace(question: Question, result: Result, docs: list[Document], chunks: list[Chunk]) -> str:
    """Return "" for a correct answer, otherwise one of the labels above."""
    if result.correct or (result.correct is None and result.status_correct):
        return ""
    return "GENERATE"  # STUB(EVAL-08)
