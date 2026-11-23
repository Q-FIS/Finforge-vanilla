# [RET-01] TF-IDF tokenizer that keeps financial words whole
labels: team:ret, size:S
**Owner:** T1 · **Size:** S (1 day) · **Due:** day 4 · **Needs:** nothing, start now

## In one sentence
Split text into lowercase words, but keep things like `FY2025`, `₹` and `1,45,000` as single tokens.

## What to do
1. In `src/rag/ret/tfidf.py`, write `tokenize(text) -> list[str]` using a regular expression.
2. Words become lowercase. These must stay as one token each: `fy2025`, `₹`, numbers with commas or decimals (`1,45,000`, `12.5`), `crore`, `lakh`.
3. Brackets around a number are dropped: `(1,234)` becomes `1,234`.
4. Optional stop words ("the", "of", "and") removed, switched by a parameter.

## Done when
- [ ] At least 20 tests in `tests/ret/test_tfidf_tokenize.py`, including `"₹1,45,000 crore"` -> `["₹", "1,45,000", "crore"]` and `"FY 2024-25"`
- [ ] `uv run pytest` passes
