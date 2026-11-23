# [RET-10] Remove repeated hits from overlapping chunks
labels: team:ret, size:S
**Owner:** T3 · **Size:** S (1 day) · **Due:** day 10 · **Needs:** nothing

## In one sentence
When two hits are mostly the same text (because chunks overlap), keep only the better one.

## What to do
In `dedupe(hits)` in `src/rag/ret/filters.py`:
1. Go through hits best first. Drop a hit if it comes from the same document as a hit you already kept, and `rag.match.coverage(hit.chunk.text, kept.chunk.text) > 0.5`.
2. Renumber the ranks of the remaining hits: 1, 2, 3, ...
3. Log which chunk ids were dropped.

## Done when
- [ ] A test with two overlapping chunks keeps only the better one, and ranks start at 1 with no gaps
