# [REP-05] Fixed-size chunker with overlap
labels: team:rep, size:M
**Owner:** R2 · **Size:** M (2-3 days) · **Due:** day 6 · **Needs:** REP-04 (you can start on the stub: the functions keep the same names)

## In one sentence
Cut a document into chunks of `max_tokens` tokens each, where neighbouring chunks share `overlap_tokens` tokens.

## What to do
In `src/rag/rep/chunking.py`, replace the body of `chunk_fixed(doc, cfg, embed)`:
1. Join the cleaned text of all `ok` pages into one long string. **Remember where each page starts** (a list of character positions), so you can work out which page a chunk came from.
2. Get the token positions with `token_offsets(full_text, embed.model)`.
3. The limit is `min(cfg.max_tokens, chunk_limit(embed.model, embed.passage_prefix))`.
4. Take tokens 0 to limit, then step forward by `limit - cfg.overlap_tokens`, and repeat until the end.
5. Each chunk's text is `full_text[start_of_first_token : end_of_last_token]`. **Never use `tokenizer.decode()`**: it changes spaces and characters, so evidence quotes would no longer match.
6. Fill `page_start` and `page_end` from the chunk's character positions, and `chunk_id = f"{doc_id}:p{page_start}:c{index:04d}"`.

## Done when
- [ ] No chunk has more tokens than the limit (test sizes 32, 64 and 512)
- [ ] Neighbouring chunks overlap by exactly `overlap_tokens` tokens
- [ ] `chunk.text in full_text` is true for every chunk
- [ ] A chunk that crosses from page 1 to page 2 has `page_start=1, page_end=2`
- [ ] Running twice gives the same chunk ids
- [ ] Tests in `tests/rep/test_chunking_fixed.py`; `uv run pytest` and the smoke run pass

## Learn first
- What overlap fixes (a fact cut in half at a boundary) and what it costs (repeated text, more chunks).
