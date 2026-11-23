# [RET-09] Filter mask: which chunks match the filters?
labels: team:ret, size:S
**Owner:** T3 · **Size:** S (1 day) · **Due:** day 8 · **Needs:** RET-08

## What is this, in plain words?
Given the filters from a question (RET-08) and all chunks, make a list of
True/False, one per chunk: True if the chunk may be returned. The search
functions use this list to hide the other chunks.

## What it must do
```python
allowed_mask(chunks, Filters(company="acme", basis="standalone"))
# -> array([False, False, False, True, True, False])   # e.g. only the page-4 and page-5 chunks
```

## Step by step
In `allowed_mask` in `src/rag/ret/filters.py`:
1. Start with all True: `mask = np.ones(len(chunks), dtype=bool)`.
2. For each filter that is **not None** (`company`, `fy`, `basis`), set mask[i] to False when chunk i's field differs, e.g. `chunk.company != filters.company`.
3. Return the mask.

## How to test it
`tests/ret/test_filter_mask.py`: no filters gives all True; each single filter; all three together; a filter that matches nothing gives all False; an empty chunk list gives an empty array.
Also add one test for post-filtering, showing it can return fewer than k hits. That's expected, and it's why RET-07 logs a warning.

## Done when
- [ ] The tests pass, and the `STUB(RET-09)` line is gone
