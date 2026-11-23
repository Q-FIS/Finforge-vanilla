# [EVAL-10] Experiment E0: how much do results change by chance?
labels: team:eval, size:S
**Owner:** E3 · **Size:** S (1 day) · **Due:** day 12 · **Needs:** EVAL-05

## In one sentence
Run the exact same setup 3 times and measure how much the scores move. Any smaller difference in other experiments means nothing.

## What to do
1. Run the baseline 3 times with `llm.cache: false` (otherwise the cache returns identical answers and the noise looks like zero).
2. For each score, write the biggest difference between the 3 runs to `eval/noise.json`, e.g. `{"answer_accuracy": 0.03, "recall@5": 0.0}`.
3. Write two sentences in `eval/reports/E0_noise.md` on what varied and why (retrieval should not vary at all; the model can).

## Done when
- [ ] `eval/noise.json` and the report are committed
