# [EVAL-07] Compare runs side by side
labels: team:eval, size:S
**Owner:** E2 · **Size:** S (1 day) · **Due:** day 12 · **Needs:** EVAL-05, EVAL-10

## In one sentence
`uv run python -m rag.compare eval/runs/baseline eval/runs/fixed_256` prints a table comparing their scores.

## What to do
In `src/rag/compare.py`:
1. Read `metrics.json` from each run folder given.
2. Print a markdown table: one row per score (overall, then per category), one column per run, plus the difference from the first run.
3. If a difference is smaller than the noise floor in `eval/noise.json` (EVAL-10), write "(no real change)" next to it.

## Done when
- [ ] It works on two smoke runs, and the output pastes cleanly into a report
