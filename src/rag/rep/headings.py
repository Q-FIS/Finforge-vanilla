"""Mark which blocks of a Document are headings.

Owner: R3        Issue: REP-07 (issues/REP-07.md)

A PDF does not say "this is a heading", so we guess from how the text looks:
headings are written bigger than the body text, or in bold. The section
chunker (REP-08) starts a new chunk at each heading, and the metadata step
(REP-10) reads "Standalone" / "Consolidated" from them.

The two numbers below are fixed by the issue, not settings in config.yaml.
"""

from __future__ import annotations

from collections import Counter

from rag.schema import Block, Document

BIG = 1.15  # a heading's font is at least 15% bigger than the body font
MAX_BOLD_WORDS = 12  # a bold heading has fewer words than this


def size_key(block: Block) -> float:
    """The block's font size rounded to 0.1 pt, so 10.4999 and 10.5 count as one size."""
    return round(block.font_size, 1)


def body_font_size(doc: Document) -> float | None:
    """The font size that most characters are written in. None if there is no text."""
    chars: Counter[float] = Counter()
    for page in doc.pages:
        for block in page.blocks:
            if block.text.strip():
                chars[size_key(block)] += len(block.text)
    if not chars:
        return None
    return chars.most_common(1)[0][0]


def is_heading(block: Block, body_size: float) -> bool:
    """True if the block looks like a heading next to body text of `body_size`."""
    text = block.text.strip()
    if block.block_type == "table" or not text:
        return False
    size = size_key(block)
    if size >= BIG * body_size:
        return True
    return (
        block.bold
        and size >= body_size
        and len(text.split()) < MAX_BOLD_WORDS
        and not text.endswith(".")
    )


def find_headings(doc: Document) -> Document:
    """Set block_type to "heading" on every heading block, and return the document."""
    body_size = body_font_size(doc)
    if body_size is None:  # no text at all: nothing to compare with
        return doc
    for page in doc.pages:
        for block in page.blocks:
            if is_heading(block, body_size):
                block.block_type = "heading"
    return doc
