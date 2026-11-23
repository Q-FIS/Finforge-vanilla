# [RET-16] Experiment E6: do filters help?
labels: team:ret, size:M
**Owner:** T3 · **Size:** M (2-3 days) · **Due:** day 15 · **Needs:** EVAL-05, RET-07

## What to do
1. Run 5 configs: no filter · extracted + pre · extracted + post · oracle + pre · oracle + post. ("Oracle" means the true company and year from the question file: the best a filter could ever do.)
2. Compare recall@5 for the "period_entity_trap" and "statement_basis" categories, and count how often fewer than k results came back.
3. Write `eval/reports/E6_filters.md`. Explain why the oracle number is only an upper limit, never our real result.

## Done when
- [ ] The run folders and the report are committed
