"""RET: retrieval metrics, written by hand. Owner T4.

STUB(RET-11). Every function returns zeros today.

Relevance (RET-11): a chunk is relevant to a question if, for some evidence
item from the same document whose page is within the chunk's pages +-1,
rag.match.is_relevant(quote, chunk.text) is True. That rule needs half the
quote's text AND one of its figures, so a consolidated row never counts as
evidence for the standalone row with the same label. Recall is counted over
evidence items, not chunks (see the backlog doc, decision 7).
"""

from __future__ import annotations

from rag.schema import Hit, Question


def relevance(hits: list[Hit], question: Question) -> list[int]:
    """1/0 per hit, in rank order."""
    return [0] * len(hits)  # STUB(RET-11)


def evidence_ranks(hits: list[Hit], question: Question) -> list[int | None]:
    """Per evidence item: the best (smallest) rank of a hit containing it, or None."""
    return [None] * len(question.evidence)  # STUB(RET-11)


def hit_at_k(rels: list[int], k: int) -> float:
    return 0.0  # STUB(RET-11)


def recall_at_k(ev_ranks: list[int | None], k: int) -> float:
    return 0.0  # STUB(RET-11)


def full_support_at_k(ev_ranks: list[int | None], k: int) -> float:
    return 0.0  # STUB(RET-11)


def mrr(rels: list[int]) -> float:
    return 0.0  # STUB(RET-11)


def ndcg_at_k(rels: list[int], k: int) -> float:
    return 0.0  # STUB(RET-11)
