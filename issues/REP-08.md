# [REP-08] Section chunker: split at headings, never split a table
labels: team:rep, size:M
**Owner:** R3 · **Size:** M (2-3 days) · **Due:** day 9 · **Needs:** REP-04, REP-07

## What is this, in plain words?
This is the "smart" chunker and probably our default. Instead of cutting every
N tokens, it follows the report's structure: **a new chunk starts at every
heading**, and each chunk remembers which headings it sits under (its
"section path"). A table is kept in one piece, because a table cut in half
separates figures from their row labels and years.

## Where it fits
`Document` (with headings marked by REP-07) → **chunk_sections() (you)** → `list[Chunk]`

## What you must give back
```python
Chunk(chunk_id="acme_ar_fy2025:p3:c0004", doc_id="acme_ar_fy2025",
      text="Consolidated Statement of Profit and Loss for the year ended March 31, 2025\n\n(₹ in crore)\n\nParticulars ...",
      page_start=3, page_end=3, n_tokens=96, chunker="section",
      section_path=["Consolidated Statement of Profit and Loss for the year ended March 31, 2025"])
```

## Step by step
In `src/rag/rep/chunking.py`, replace the body of `chunk_sections`:
1. Go through every block of every `ok` page, in order.
2. Keep a **heading path**, a list of the headings above you. When you meet a heading, it replaces any heading of the same or smaller font size in the list. (For a first version, simply replace the whole list with `[heading]`.)
3. **A heading closes the current chunk** and starts a new one. The heading's own text is the first line of the new chunk.
4. Add the blocks that follow, joined with `"\n\n"`, while the token count stays within the limit (`chunk_limit(embed.model, embed.passage_prefix)` and `cfg.max_tokens`). If the next block won't fit, close the chunk and start another with the same section path.
5. **Tables:** a block with `block_type == "table"` (created by REP-14, if it's done) is never split. If one table alone is over the limit, split it **between rows** (lines), and repeat the table's first line (its header row) at the top of each part.
6. **Exact text:** the chunk text must be an exact piece of the page text. Build it from the page text the same way `Page.text` does (blocks joined with `"\n\n"`), so `chunk.text in page.text` stays true for chunks within one page.
7. Fill `section_path`, `page_start`, `page_end`, the id (like REP-05) and `chunker="section"`.

## Watch out for
- Without REP-14, table cells are separate small blocks. That's fine: they're consecutive, so they still end up in the same chunk.
- A chunk that spans two pages can't be an exact piece of a single page's text. Prefer closing the chunk at a page break unless the section continues.

## How to test it
`tests/rep/test_chunking_section.py`:
- On the fixture: the page-3 chunk contains all of "Revenue from operations", "1,45,000", "Profit for the year" and "18,200", and its `section_path` names the consolidated statement.
- No chunk is over the limit.
- With a tiny limit and a made-up "table" block, the table splits between rows and each part starts with the header row.

## Done when
- [ ] The tests pass
- [ ] On one real report, at least 90% of chunks have a non-empty `section_path`
- [ ] `uv run pytest` and the smoke run pass
