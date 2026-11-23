# [REP-07] Find the headings
labels: team:rep, size:S
**Owner:** R3 · **Size:** S (1 day) · **Due:** day 5 · **Needs:** nothing (use the fixture)

## In one sentence
Mark which blocks are headings, using font size and boldness, so the section chunker and the metadata know where sections start.

## What to do
1. Write `find_headings(doc)` in a new file, `src/rag/rep/headings.py`. It sets `block.block_type = "heading"` on heading blocks.
2. The "body" font size is the most common size in the document (count characters, not blocks).
3. A block is a heading if its font size is at least 1.15 times the body size, **or** it is bold, shorter than 12 words, and doesn't end with a full stop.
4. Call it from `parse_pdf` once REP-01 is merged, or ask R1 to.

## Done when
- [ ] On the fixture, the blocks marked as headings are exactly the `headings` list in `acme_ar_fy2025.expected.json`
- [ ] Tests in `tests/rep/test_headings.py`; `uv run pytest` passes
