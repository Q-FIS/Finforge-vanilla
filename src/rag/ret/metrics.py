"""Measure retrieval: did we find the evidence, and how high was it ranked?

Owner: T4        Issue: RET-11 (issues/RET-11.md)

Two helper functions turn a question's evidence into numbers, and five
metric functions turn those numbers into scores between 0 and 1.

STUB: every function returns zeros.
"""

from __future__ import annotations

from rag.schema import Hit, Question


def relevance(hits: list[Hit], question: Question) -> list[int]:
    """One number per hit, in rank order: 1 if the hit is relevant, else 0.

    A hit is relevant if, for some evidence item of the question from the
    same document and a nearby page (+-1), rag.match.is_relevant(quote,
    hit.chunk.text) is True.
    """
    return [0 for _ in hits]  # STUB(RET-11)


def evidence_ranks(hits: list[Hit], question: Question) -> list[int | None]:
    """One entry per evidence item: the best rank of a hit that contains
    it, or None if no hit does."""
    return [None for _ in question.evidence]  # STUB(RET-11)


def hit_at_k(rels: list[int], k: int) -> float:
    """1.0 if any of the first k hits is relevant, else 0.0."""
    return 0.0  # STUB(RET-11)


def recall_at_k(ranks: list[int | None], k: int) -> float:
    """The share of evidence items found within the first k hits."""
    return 0.0  # STUB(RET-11)


def full_support_at_k(ranks: list[int | None], k: int) -> float:
    """1.0 only if EVERY evidence item was found within the first k hits."""
    return 0.0  # STUB(RET-11)


def mrr(rels: list[int]) -> float:
    """1 / (rank of the first relevant hit), or 0.0 if there is none."""
    return 0.0  # STUB(RET-11)


def ndcg_at_k(rels: list[int], k: int) -> float:
    """How good the ranking of the first k hits is, from 0.0 to 1.0."""
    return 0.0  # STUB(RET-11)
