# [REP-05] Fixed-size chunker, with overlap
labels: team:rep, size:M
**Owner:** R2 · **Size:** M (2-3 days) · **Due:** day 6 · **Needs:** REP-04 (start now on the placeholder; the function names won't change)

## What is this, in plain words?
We can't search a 300-page report as one piece. We cut it into **chunks**:
pieces small enough for the embedding model (at most 512 tokens), and small
enough that a search hit points to a specific place.

This is the simplest way: cut every N tokens, like slicing bread. To avoid
cutting a fact in half at a boundary, neighbouring slices **overlap**: the last
50 tokens of one chunk are also the first 50 tokens of the next.

## Where it fits
clean_document() (REP-02) → `Document` → **chunk_fixed() (you)** → `list[Chunk]` → metadata (REP-10) → embedding (REP-11)

## What you get, and what you must give back
- **You get:** a cleaned `Document`, `cfg` (a `ChunkConfig`: `max_tokens` = 512, `overlap_tokens` = 50) and `embed` (an `EmbedConfig`: you need `embed.model` and `embed.passage_prefix`).
- **You give back:** a list of `Chunk`s, e.g.:
```python
Chunk(chunk_id="acme_ar_fy2025:p1:c0000", doc_id="acme_ar_fy2025",
      text="Directors' Report\n\nYour Directors present the 40th Annual Report ...",
      page_start=1, page_end=1, n_tokens=118, chunker="fixed")
```

## Step by step
In `src/rag/rep/chunking.py`, replace the body of `chunk_fixed`:
1. **Build one long text.** Join the `page.text` of every page whose status is `"ok"` with `"\n\n"` in between. While doing it, record where each page starts: a list `page_starts` of `(character position, page number)`.
2. **Get the token positions:** `offsets = token_offsets(full_text, embed.model)`. Each item is `(start, end)` in `full_text`.
3. **The limit:** `limit = min(cfg.max_tokens, chunk_limit(embed.model, embed.passage_prefix))`. The step between chunks is `limit - cfg.overlap_tokens`.
4. **Make the windows:** for `first = 0, step, 2*step, ...`: the chunk covers tokens `first` to `last = min(first + limit, len(offsets)) - 1`. Stop after the window that reaches the last token.
5. **Cut the text from the original string:** `text = full_text[offsets[first][0] : offsets[last][1]]`. **Never** rebuild the text with `tokenizer.decode()`.
6. **Pages:** the page of a character position is the last entry in `page_starts` that starts at or before it (`bisect` helps). `page_start` = page of the chunk's first character, `page_end` = page of its last.
7. **Fill the chunk:** `chunk_id=f"{doc.doc_id}:p{page_start}:c{index:04d}"` (index = 0, 1, 2... over the whole document), `n_tokens = last - first + 1`, `chunker="fixed"`.
8. When it works, delete the `one_chunk_per_page` call from `chunk_fixed`.

## Watch out for
- **Why never decode?** `decode()` changes spaces and some characters, so the chunk would no longer be an exact piece of the report, and evidence quotes would stop matching it. Slicing the original string keeps it exact.
- The last window is usually shorter than `limit`. That's fine.
- Empty document (no ok pages) → return `[]`.

## How to test it
Create `tests/rep/test_chunking_fixed.py`. Build a `Document` by hand (or parse and clean the fixture once REP-01 and REP-02 are merged), then check:
- every chunk has `n_tokens <= limit`, for `max_tokens` 32, 64 and 512;
- neighbouring chunks share exactly `overlap_tokens` tokens: the last `overlap_tokens` token texts of chunk i equal the first ones of chunk i+1;
- `chunk.text in full_text` for every chunk;
- with a tiny `max_tokens`, some chunk crosses from page 1 to page 2 and has `page_start=1, page_end=2`;
- running twice gives identical chunk ids.

## Done when
- [ ] All the tests above pass
- [ ] `uv run pytest` and the smoke run pass (try the smoke run with `chunk: {strategy: fixed}` in a copy of `tests/ci.yaml`)

## Learn first
- What does overlap fix (a fact cut in half at a boundary), and what does it cost (repeated text, more chunks, the same passage showing up twice in search results)?
