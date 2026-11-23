# [RET-15] Experiment E5: how many passages (k) should go in the prompt?
labels: team:ret, size:S
**Owner:** T4 · **Size:** S (1 day) · **Due:** day 15 · **Needs:** EVAL-05

## What is this, in plain words?
More passages in the prompt means a better chance the answer is in there, but
also more cost, and more distraction for the model. You measure how recall
grows with k, to find where adding more stops helping.

## Step by step
1. You don't need 5 runs: we always fetch 20 hits and save them. Take the baseline run's `results.jsonl`; each line has `evidence_found_at`, the rank of each evidence item.
2. For k = 1, 3, 5, 10 and 20, compute the average `recall_at_k(evidence_found_at, k)` over the answerable questions.
3. Draw recall against k (matplotlib, in `notebooks/ret/choosing_k.ipynb`), and save the picture.
4. Write `eval/reports/E5_choosing_k.md`: the chart, the numbers, the k we choose, and why.

## Done when
- [ ] The notebook and the report are committed. If the chosen k differs from 5, change `config.yaml` in the same PR.
