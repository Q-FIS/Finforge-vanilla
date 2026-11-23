# [RET-12] Check our scores against the ranx library
labels: team:ret, size:S
**Owner:** T4 · **Size:** S (1 day) · **Due:** day 9 · **Needs:** RET-11

## In one sentence
Prove our hit@k, MRR and nDCG@k give the same numbers as `ranx`.

## What to do
1. Turn one run into ranx's format: `Qrels` (which chunk ids are relevant to each question) and `Run` (each question's retrieved chunk ids with scores).
2. Compare `hit_rate@5`, `mrr` and `ndcg@5` with ours.
3. Our recall counts evidence items, so it won't match ranx's recall. Write one sentence in the test explaining why.

## Done when
- [ ] hit, MRR and nDCG match to 9 decimal places on a dev run (in `tests/ret/test_metrics_ranx.py`)
