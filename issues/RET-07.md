# [RET-07] retrieve(): add the metadata filters
labels: team:ret, size:S
**Owner:** T2 · **Size:** S (1 day) · **Due:** day 9 · **Needs:** RET-04, RET-09

## What is this, in plain words?
`retrieve()` is the one function the pipeline calls for search. It already
embeds the question and calls the index. You add **filters**: if the question
asks about "Infosys in FY2025", only search chunks labelled infosys and FY2025.
There are two ways to do it, and experiment E6 (RET-16) compares them:
- **pre-filtering:** remove non-matching chunks *before* searching;
- **post-filtering:** search everything, then throw away non-matching hits. This can leave fewer than k results.

## Step by step
In `retrieve()` in `src/rag/ret/retrieve.py`:
1. **Which filters:** if `cfg.filter == "none"`, use `Filters()` (no filtering). Otherwise use `oracle_filters` if it was given (the true labels, for experiments), else `extract_filters(question, registry)` (RET-08).
2. **Pre** (`cfg.filter == "pre"`): `mask = allowed_mask(dense.chunks, filters)`, and pass `allowed=mask` to `dense.search` or `tfidf.search`.
3. **Post** (`cfg.filter == "post"`): search for `cfg.depth * 3` hits without a mask, keep only the hits whose chunk matches the filters (use `allowed_mask` on the hit chunks), take the first `cfg.depth`, and renumber ranks from 1.
4. If fewer than `cfg.k` hits are left, `logging.warning(...)` with the question and the filters.
5. Put the filters used into the returned `Retrieval`.

## How to test it
`tests/ret/test_retrieve.py`, with the fixture chunks and `FakeEmbedder`:
- `filter: none` returns hits from every page;
- with `Filters(basis="standalone")` and pre-filtering, every hit is standalone;
- post-filtering with a filter that matches only 1 chunk returns 1 hit and logs a warning.

## Done when
- [ ] The tests pass, and the smoke run passes
- [ ] The `STUB(RET-07)` line is gone
