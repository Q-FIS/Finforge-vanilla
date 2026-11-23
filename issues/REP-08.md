# [REP-08] Section chunker: split at headings, never split a table
labels: team:rep, size:M
**Owner:** R3 · **Size:** M (2-3 days) · **Due:** day 9 · **Needs:** REP-04, REP-07

## In one sentence
Start a new chunk at every heading, keep the list of headings above each chunk, and keep tables whole.

## What to do
In `src/rag/rep/chunking.py`, replace the body of `chunk_sections(doc, cfg, embed)`:
1. Walk through the blocks in order. A heading starts a new chunk.
2. Keep a "heading path": the headings above the current text, e.g. `["Financial Statements", "Consolidated Statement of Profit and Loss"]`. Save it in `chunk.section_path`.
3. Add paragraphs to the current chunk until the token limit; if needed, start another chunk with the same heading path.
4. A `table` block is never split. If a table alone is over the limit, split it **between rows**, and repeat the header row at the top of each part.
5. Same rules as REP-05: cut from the original text, fill the pages, stable ids.

## Done when
- [ ] On the fixture, each table's rows stay together in one chunk
- [ ] At least 90% of chunks of one real report have a non-empty `section_path`
- [ ] Tests in `tests/rep/test_chunking_section.py`; `uv run pytest` and the smoke run pass
