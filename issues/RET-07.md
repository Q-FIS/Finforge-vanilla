# [RET-07] retrieve(): add the metadata filters
labels: team:ret, size:S
**Owner:** T2 · **Size:** S (1 day) · **Due:** day 9 · **Needs:** RET-04, RET-09

## In one sentence
Make `retrieve()` use filters (company, year, basis) in "pre" or "post" mode.

## What to do
In `retrieve()` in `src/rag/ret/retrieve.py`:
1. Filters: if `cfg.filter` is "none", use none. Otherwise use `oracle_filters` when given, else `extract_filters(question, registry)`.
2. **Pre-filtering** (`cfg.filter == "pre"`): make `allowed_mask(chunks, filters)` and pass it to `search`.
3. **Post-filtering** (`cfg.filter == "post"`): search for `cfg.depth * 3` hits with no mask, then keep only hits that match the filters, up to `cfg.depth`.
4. If fewer than `cfg.k` hits come back, log a warning.
5. Put the filters used in the returned `Retrieval`.

## Done when
- [ ] Tests for each mode on the fixture, in `tests/ret/test_retrieve.py`
- [ ] `uv run pytest` and the smoke run pass
