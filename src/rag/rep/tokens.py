"""Count tokens the way the EMBEDDING model counts them.

Owner: R2        Issue: REP-04 (issues/REP-04.md)

Embedding models read "tokens" (pieces of words), not words, and they have a
maximum number of tokens they can read. Chunks must fit inside that limit,
so the chunkers use these three functions to measure text.

STUB: right now a "token" is just a word separated by spaces.
"""

from __future__ import annotations

import re


def count_tokens(text: str, model: str) -> int:
    """How many tokens `text` is for `model`."""
    return len(text.split())  # STUB(REP-04): counts words, not real tokens


def token_offsets(text: str, model: str) -> list[tuple[int, int]]:
    """Where each token starts and ends in `text`, as (start, end) positions.

    Chunkers use these to cut the ORIGINAL text, e.g. text[start:end].
    """
    # STUB(REP-04): positions of words, not real tokens
    return [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]


def chunk_limit(model: str, prefix: str = "") -> int:
    """The most tokens one chunk may have for `model`.

    That is the model's maximum, minus its special tokens, minus the tokens
    of the prefix some models need (e.g. "passage: ").
    """
    return 510 - count_tokens(prefix, model)  # STUB(REP-04): 510 is a guess
