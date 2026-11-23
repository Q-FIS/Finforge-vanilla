# [RET-16] Experiment E6: do the filters help?
labels: team:ret, size:M
**Owner:** T3 · **Size:** M (2-3 days) · **Due:** day 15 · **Needs:** EVAL-05, RET-07

## What is this, in plain words?
We built filters to stop wrong-year and wrong-statement passages from winning.
Do they? And which way is better, filtering before the search (pre) or after
(post)? You also run with **"oracle" filters** (the true company and year,
taken from the question file): the best any filter could ever do. It's an
upper limit for comparison, never a real result.

## Step by step
1. Five runs, changing only `retrieve.filter` and `retrieve.filter_source`:
   - `none`
   - `pre` + `extracted`, and `post` + `extracted`
   - `pre` + `oracle`, and `post` + `oracle`
2. Compare recall@5 for the `period_entity_trap` and `statement_basis` categories, and overall.
3. Count how often post-filtering returned fewer than k hits (search the run's log for the RET-07 warning, or count `retrieved` lengths in `results.jsonl`).
4. Write `eval/reports/E6_filters.md`: the table, which mode we choose, and a sentence on how close our extracted filters get to the oracle.

## Done when
- [ ] The run folders and the report are committed
