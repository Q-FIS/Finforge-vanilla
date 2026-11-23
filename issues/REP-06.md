# [REP-06] Sentence chunker: never cut a sentence in half
labels: team:rep, size:M
**Owner:** R2 · **Size:** M (2-3 days) · **Due:** day 8 · **Needs:** REP-04

## In one sentence
Split the text into sentences, then pack whole sentences into chunks up to the token limit.

## What to do
In `src/rag/rep/chunking.py`, replace the body of `chunk_sentences(doc, cfg, embed)`:
1. Write a sentence splitter (a regular expression is fine). It must **not** split after "Rs.", "Ltd.", "No.", "Co.", "Pvt.", decimals like "12.5", or initials like "N. R."
2. Add sentences to the current chunk until the next one would go over the limit, then start a new chunk.
3. Overlap: start each new chunk with the last `cfg.overlap_sentences` sentences of the previous one.
4. One sentence longer than the limit on its own: cut it like the fixed chunker, and log a warning.
5. Same rules as REP-05: cut from the original text, fill the pages, stable ids.

## Done when
- [ ] At least 20 tests for the sentence splitter, in `tests/rep/test_chunking_sentence.py`
- [ ] No sentence is cut, except the too-long ones you warned about
- [ ] `uv run pytest` and the smoke run pass
