# [GEN-11] Experiment E7: where do we lose accuracy?
labels: team:gen, size:M
**Owner:** G3 · **Size:** M (2-3 days) · **Due:** day 15 · **Needs:** EVAL-05, EVAL-09

## In one sentence
Compare three runs (no documents, our retrieval, perfect retrieval) to see how much accuracy retrieval costs us.

## What to do
1. Run with `retrieve.method: none` (closed-book), `dense` (our system) and `oracle` (the true evidence handed to the model).
2. Compare answer accuracy and status accuracy, overall and per category.
3. What it tells you: oracle minus dense = what our retrieval loses. Oracle alone = how good the model is with perfect evidence. Closed-book = what the model already "knew".
4. Write `eval/reports/E7_where_we_lose.md`. Differences smaller than the noise floor (E0) count as "no real difference".

## Done when
- [ ] The run folders and the report are committed
