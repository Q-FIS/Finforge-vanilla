# [EVAL-07] Compare runs side by side
labels: team:eval, size:S
**Owner:** E2 · **Size:** S (1 day) · **Due:** day 12 · **Needs:** EVAL-05, EVAL-10

## What is this, in plain words?
Every experiment ends with "is run B better than run A?". This command prints
the answer as a table, and marks differences too small to mean anything.

## What it must do
```
$ uv run python -m rag.compare eval/runs/baseline eval/runs/e1_fixed_256_0

| score            | baseline | e1_fixed_256_0 | change |
| ---              | ---      | ---            | ---    |
| recall@5         | 0.71     | 0.64           | -0.07  |
| answer_accuracy  | 0.58     | 0.57           | -0.01 (no real change) |
...
```

## Step by step
In `main()` in `src/rag/compare.py`:
1. Read each run folder's `metrics.json` (the folders are given on the command line; use `argparse`).
2. Print a markdown table: one row per score in `overall`, one column per run, plus a "change" column (each run minus the first).
3. Then the same table for each category in `by_category`.
4. Read `eval/noise.json` (EVAL-10). If a change is smaller than that score's noise, write "(no real change)" after it. If the file doesn't exist yet, skip this.
5. Return 0.

## Done when
- [ ] It works on two smoke runs (make two with different `--name`s), and the output pastes cleanly into a report
- [ ] A small test in `tests/test_compare.py`
