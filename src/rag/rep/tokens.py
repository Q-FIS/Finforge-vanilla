"""REP: token counting with the EMBEDDING model's tokenizer. Owner R2.

STUB(REP-04). Today a "token" is a whitespace-separated word. The real
version uses the model's Hugging Face fast tokenizer.
"""

from __future__ import annotations

import re

_WORD = re.compile(r"\S+")


def count_tokens(text: str, model: str) -> int:
    """Number of tokens `text` takes in `model`, without special tokens."""
    return len(_WORD.findall(text))  # STUB(REP-04)


def token_offsets(text: str, model: str) -> list[tuple[int, int]]:
    """(start, end) character offsets of each token, so chunkers can slice
    the original text instead of decoding token ids."""
    return [(m.start(), m.end()) for m in _WORD.finditer(text)]  # STUB(REP-04)


def chunk_limit(model: str, prefix: str = "") -> int:
    """The most tokens a chunk may have: the model's maximum, minus special
    tokens, minus the tokens of the passage prefix (e.g. "passage: ")."""
    return 510 - count_tokens(prefix, model)  # STUB(REP-04)
