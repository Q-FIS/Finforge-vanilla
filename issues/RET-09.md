# [RET-09] Filter mask: which chunks match the filters?
labels: team:ret, size:S
**Owner:** T3 · **Size:** S (1 day) · **Due:** day 8 · **Needs:** RET-08

## In one sentence
Make `allowed_mask(chunks, filters)` return True for chunks that match every filter that is set.

## What to do
1. In `src/rag/ret/filters.py`: a chunk matches if, for each filter that is not None, the chunk's field is equal (`chunk.company == filters.company`, and the same for `fy` and `basis`).
2. Return a numpy array of True/False, one per chunk.

## Done when
- [ ] Tests: no filters gives all True; each single filter; all three together; a filter that matches nothing
- [ ] A test shows post-filtering can return fewer than k results (that's expected, and it's why RET-07 warns)
