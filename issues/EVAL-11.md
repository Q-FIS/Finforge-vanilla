# [EVAL-11] Failure reports for the weekly meeting
labels: team:eval, size:S
**Owner:** E3 · **Size:** S (1 day each time) · **Due:** day 12 and day 17 · **Needs:** EVAL-08

## What is this, in plain words?
A one-page summary of what went wrong in the latest run, sorted by which team
can fix it. It turns "the scores are bad" into "Team 2: 9 questions lost to
wrong-year passages; here are 2 examples".

## Step by step
1. Take the latest dev run. Count the failure labels in its `metrics.json`, grouped by team:
   PARSE + CHUNK = Team 1 · NOT_RETRIEVED + RANKED_LOW = Team 2 · DROPPED + WRONG_STATUS + GENERATE = Team 3.
2. Pick 5 wrong answers, covering different labels. For each, follow it step by step using its line in `results.jsonl`: what was retrieved (`retrieved`), what went into the prompt (`context_ids`), what the model said (`answer.raw`), and the correct answer.
3. Write `eval/reports/failures_day12.md` (and later `failures_day17.md`): the counts, the 5 examples, and one line per team: "fix this next".
4. Present it in the weekly call, in 10 minutes.

## Done when
- [ ] Both reports are committed
