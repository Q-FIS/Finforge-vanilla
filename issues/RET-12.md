# [RET-12] Check our scores against the ranx library
labels: team:ret, size:S
**Owner:** T4 · **Size:** S (1 day) · **Due:** day 9 · **Needs:** RET-11

## What is this, in plain words?
Like RET-03 for TF-IDF: we wrote the scores by hand, so we prove they're
correct by comparing them with `ranx`, a well-known evaluation library.

## Step by step
1. In `tests/ret/test_metrics_ranx.py`, take one run's results (or make a small fake one: 5 questions, 10 hits each).
2. Build ranx's two inputs:
   - `Qrels`: for each question, which chunk ids are relevant: `{"FX01": {"acme_ar_fy2025:p3:c0004": 1}, ...}`
   - `Run`: for each question, the retrieved chunk ids with their scores.
3. `ranx.evaluate(qrels, run, ["hit_rate@5", "mrr", "ndcg@5"])`, and compare with the averages of our functions.
4. Our recall counts *evidence items* and ranx's counts *chunks*, so they differ. Write one sentence in the test explaining that, instead of comparing them.

## Done when
- [ ] hit@5, MRR and nDCG@5 match ranx to 9 decimal places
