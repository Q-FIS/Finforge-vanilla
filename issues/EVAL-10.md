# [EVAL-10] Experiment E0: how much do results change by chance?
labels: team:eval, size:S
**Owner:** E3 · **Size:** S (1 day) · **Due:** day 12 · **Needs:** EVAL-05

## What is this, in plain words?
If you run exactly the same thing twice, do you get exactly the same scores?
Not quite: the model can phrase answers differently each time. So when an
experiment shows "+2%", is that real, or chance? You measure the chance part
(the **noise floor**) first. Every experiment is then compared against it.

## Step by step
1. Run the baseline config **3 times** with `llm.cache: false` (with the cache on, the answers would just be copied, and the noise would look like zero): `--name e0_run1`, `e0_run2`, `e0_run3`.
2. For each overall score in `metrics.json`, compute the spread: the biggest value minus the smallest.
3. Save `eval/noise.json`, e.g. `{"answer_accuracy": 0.03, "status_accuracy": 0.02, "recall@5": 0.0, ...}`.
4. Write `eval/reports/E0_noise.md`: the table, and two or three sentences on what varied and why. Retrieval scores should not vary at all: if they do, something is random that shouldn't be. Tell the lead.

## Done when
- [ ] `eval/noise.json` and the report are committed
