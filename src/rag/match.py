"""Is this quote in this text? One shared answer for the whole project.

Metrics (is a chunk relevant?), the failure trace (did the evidence survive
parsing? chunking?), the citation validator (is the quote really in the
passage?) and the question checker (is the quote on the page the writer
said?) all ask the same question. If each team wrote its own matcher, their
numbers would quietly disagree, so they all use this module:

    normalize(text)               canonical form for comparing text
    coverage(quote, text)         0.0 .. 1.0: how much of the quote is in the text
    figures(text)                 the significant numbers in a text
    is_relevant(quote, chunk)     the project's "relevant chunk" rule
    fully_contains(quote, chunk)  the whole quote is in the chunk
    on_page(quote, page_text)     the question checker's rule

Why figures matter: in a financial table the row label is most of the text.
"Profit for the year 16,900 14,300" (standalone) and "Profit for the year
18,200 15,400" (consolidated, the next page) share 60% of their characters,
so coverage alone would call the wrong statement relevant. The rules below
also require the quote's figures to be there.

Performance: these compare one quote with one text. Callers must first
narrow the candidates (same doc_id, page within +-1 of the evidence page),
so they run on a handful of chunks, not on all 15,000.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

# Thresholds, defined once for the whole project.
RELEVANT = 0.5  # a chunk holding at least half the quote (e.g. split in two)
ON_PAGE = 0.9  # a hand-copied quote, allowing small copy differences

# Curly quotes, primes and the many Unicode dashes all become plain ASCII.
# Only for matching: the stored text itself is never changed.
_SINGLE = "\u2018\u2019\u201a\u201b\u2032"  # curly single quotes, prime
_DOUBLE = "\u201c\u201d\u201e\u201f\u2033"  # curly double quotes, double prime
_DASH = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"  # hyphens, en/em dash, minus
_TRANSLATE = str.maketrans(
    {**dict.fromkeys(_SINGLE, "'"), **dict.fromkeys(_DOUBLE, '"'), **dict.fromkeys(_DASH, "-")}
)
_SOFT_HYPHEN = "\u00ad"  # invisible hyphenation hint some PDFs contain
# A word broken across a line: "opera-\ntions" or "opera- tions" -> "operations".
# Letters on both sides only, so "2024-25" and "(1,234)" are untouched.
_LINE_HYPHEN = re.compile(r"(?<=[^\W\d_])-\s+(?=[^\W\d_])")
_SPACES = re.compile(r"\s+")
# A number as printed: digits with optional grouping commas and decimals.
_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def normalize(text: str) -> str:
    """Text in a canonical form for comparison.

    Does: NFKC (ligatures such as "ﬁ" become "fi"), plain quotes and
    dashes, rejoins words hyphenated across lines, collapses all whitespace
    to single spaces, casefolds.

    Does NOT touch digits, commas, brackets, "₹" or "%": "1,45,000" and
    "(1,234)" stay exactly as written, because figures must match exactly.
    """
    text = unicodedata.normalize("NFKC", text).replace(_SOFT_HYPHEN, "")
    text = text.translate(_TRANSLATE)
    text = _LINE_HYPHEN.sub("", text)
    text = _SPACES.sub(" ", text).strip()
    return text.casefold()


def coverage(quote: str, text: str) -> float:
    """The share of `quote` found in `text` as one unbroken stretch.

    1.0 means the whole quote appears in the text (after `normalize`).
    0.5 means the longest stretch of the quote found in the text is half
    its length, e.g. the quote was split across two chunks.
    An empty quote or text returns 0.0.

    This measures text only. Use `is_relevant` / `on_page` for decisions:
    they also check the figures.
    """
    q, t = normalize(quote), normalize(text)
    if not q or not t:
        return 0.0
    if q in t:
        return 1.0
    # autojunk=False: otherwise difflib ignores very common characters (like
    # spaces) in long texts, and the longest match comes out too short.
    m = SequenceMatcher(None, q, t, autojunk=False).find_longest_match(0, len(q), 0, len(t))
    return m.size / len(q)


def figures(text: str) -> set[str]:
    """The significant numbers in `text`, as printed: those with 3 or more
    digits ("16,900", "2025", "12.50"). Small numbers such as "31" or "4"
    appear everywhere and identify nothing, so they are left out."""
    found = _NUMBER.findall(normalize(text))
    return {n.rstrip(",") for n in found if sum(ch.isdigit() for ch in n) >= 3}


def is_relevant(quote: str, chunk_text: str) -> bool:
    """A chunk is relevant to an evidence quote when it holds at least half of
    the quote AND, if the quote has figures, at least one of them."""
    if coverage(quote, chunk_text) < RELEVANT:
        return False
    wanted = figures(quote)
    return not wanted or bool(wanted & figures(chunk_text))


def fully_contains(quote: str, chunk_text: str) -> bool:
    """The whole quote is in the chunk (the "containment" in experiment E1)."""
    return coverage(quote, chunk_text) == 1.0


def on_page(quote: str, page_text: str) -> bool:
    """A question writer's quote is on the page they named: nearly all of its
    text is there, and every one of its figures is."""
    return coverage(quote, page_text) >= ON_PAGE and figures(quote) <= figures(page_text)
