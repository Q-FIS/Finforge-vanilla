# [RET-15] Experiment E5: how many passages (k)?
labels: team:ret, size:S
**Owner:** T4 · **Size:** S (1 day) · **Due:** day 15 · **Needs:** EVAL-05

## What to do
1. Using one run's `results.jsonl`, compute recall@k for k = 1, 3, 5, 10 and 20. (You don't need 5 runs: we always fetch 20.)
2. Draw recall against k, and find where it stops improving much.
3. Write `eval/reports/E5_choosing_k.md`: the chart, the k we choose, and why.

## Done when
- [ ] The report is committed
