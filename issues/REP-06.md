# [REP-06] Sentence chunker: never cut a sentence in half
labels: team:rep, size:M
**Owner:** R2 · **Size:** M (2-3 days) · **Due:** day 8 · **Needs:** REP-04

## What is this, in plain words?
The fixed chunker (REP-05) can cut in the middle of a sentence, for example
between "Revenue grew 20.8% to" and "₹1,45,000 crore". This chunker is
smarter: it first splits the text into sentences, then fills each chunk with
**whole** sentences until the next one wouldn't fit.

The tricky part is finding where sentences end. A full stop doesn't always
end a sentence: "Rs. 3.2 lakh", "Acme Pvt. Ltd.", "No. 5", "12.5%".

## Where it fits
Same as REP-05: `Document` → **chunk_sentences() (you)** → `list[Chunk]`

## Step by step
In `src/rag/rep/chunking.py`:
1. **Write `split_sentences(text) -> list[tuple[int, int]]`**, returning the `(start, end)` character position of each sentence (positions, not copies, so you can slice the original text later).
   - A sentence ends at `.`, `?` or `!` followed by a space or newline and then a capital letter, a digit or `₹`.
   - Except after these: `Rs.`, `Ltd.`, `Pvt.`, `No.`, `Co.`, `Inc.`, `Mr.`, `Ms.`, `Dr.`, `viz.`, `i.e.`, `e.g.`, a single capital letter (initials like "N. R."), and between digits (`12.5`).
   - A blank line (`"\n\n"`) always ends a sentence, since headings and table rows don't have full stops.
2. **Build one long text and `page_starts`**, exactly as in REP-05 (reuse that code).
3. **Pack the sentences:** go through them, adding each to the current chunk while the chunk's token count stays within the limit. When the next sentence won't fit, close the chunk and start a new one.
4. **Overlap:** a new chunk starts with the last `cfg.overlap_sentences` sentences of the previous chunk.
5. **A sentence longer than the limit on its own:** cut it into fixed windows (like REP-05), and log a warning with its first 50 characters.
6. Chunk text = `full_text[start of first sentence : end of last sentence]`. Fill pages and ids like REP-05, with `chunker="sentence"`.

## How to test it
Create `tests/rep/test_chunking_sentence.py`:
- at least 20 tests for `split_sentences`, for example:
  - `"Revenue rose. Profit fell."` → 2 sentences
  - `"Paid Rs. 3.2 lakh to Acme Pvt. Ltd. in FY2025."` → 1 sentence
  - `"Growth was 12.5%. Margins held."` → 2 sentences
  - `"Directors' Report\n\nYour Directors present..."` → 2 sentences
- no chunk is over the limit; every chunk starts and ends on a sentence boundary (except the warned ones); overlap is the right number of sentences.

## Done when
- [ ] The tests pass
- [ ] `uv run pytest` and the smoke run (with `chunk: {strategy: sentence}`) pass
