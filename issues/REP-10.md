# [REP-10] Metadata: standalone or consolidated, and the header line
labels: team:rep, size:S
**Owner:** R4 · **Size:** S (1 day) · **Due:** day 7 · **Needs:** REP-07 (headings)

## What is this, in plain words?
Each chunk carries labels: which company, which year, and whether its figures
are **standalone** (the parent company alone) or **consolidated** (the parent
plus its subsidiaries). The question "What was the standalone profit?" must
find the standalone table, not the consolidated one on the next page, and
these labels are how filters (RET-08/09) tell them apart.

`company` and `fy` are already done: they're copied from `data/registry.csv`.
You add `basis`, and an optional "header line" for experiment E2.

## Where it fits
chunkers → `list[Chunk]` → **add_metadata() (you)** → embedding (REP-11)

## What you must give back
The same chunks, with `basis` filled:
```python
chunk.company == "acme"; chunk.fy == "FY2025"; chunk.basis == "consolidated"   # a page-3 chunk
```
And `embedding_text(chunk, cfg)`:
```python
# cfg.prepend_header == False:
"Revenue from operations 1,45,000 ..."
# cfg.prepend_header == True:
"Acme Industries Limited · FY2025 · consolidated · Consolidated Statement of Profit and Loss ...\nRevenue from operations 1,45,000 ..."
```

## Step by step
In `src/rag/rep/metadata.py`:
1. **Collect the "basis headings":** go through the document's blocks in order (page by page). Whenever a block with `block_type == "heading"` contains "standalone" or "consolidated" (ignore capitals), record `(page number, order, "standalone" or "consolidated")`.
2. **For each chunk,** find the last basis heading that comes **at or before** the chunk's start (same page and earlier order, or an earlier page). Its basis is the chunk's basis. If there is none, the basis stays `"none"`.
   - Simpler first version: use the last basis heading on any page `<= chunk.page_start`. Write in a comment that a heading in the middle of a page can then be off by a few blocks.
   - If the chunk's `section_path` contains a basis word, prefer that (it's exact).
3. **`embedding_text(chunk, cfg)`:** if `cfg.prepend_header` is False, return `chunk.text`. Otherwise return a first line made of the company's full name, the fy, the basis and the last entry of `section_path`, joined with " · ", followed by a newline and `chunk.text`.
   - You need the company's full name. `embedding_text` only gets the chunk, so either store it on the chunk in `add_metadata` (ask the lead before adding a field to `schema.py`), or look it up from a small dict you fill in `add_metadata`.

## Watch out for
- **Never change `chunk.text`.** The header only goes to the embedder. Evidence quotes are matched against `chunk.text`, so changing it would break the evaluation.
- "Notes to the **Standalone** Financial Statements" is also a basis heading: notes belong to a statement.

## How to test it
`tests/rep/test_metadata.py` with the fixture: chunks from page 3 are "consolidated", chunks from pages 4 and 5 are "standalone", chunks from pages 1 and 2 are "none". And a test that `chunk.text` is identical with the header on or off.

## Done when
- [ ] The tests pass, and the smoke run passes
- [ ] The `STUB(REP-10)` lines are gone
