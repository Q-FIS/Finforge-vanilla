# [EVAL-11] Failure reports for the weekly meeting
labels: team:eval, size:S
**Owner:** E3 · **Size:** S (1 day each time) · **Due:** day 12 and day 17 · **Needs:** EVAL-08

## In one sentence
A one-page summary of what went wrong in the latest run, and which team it belongs to.

## What to do
1. Take the latest dev run. Count the failure labels, grouped by team: PARSE and CHUNK = Team 1; NOT_RETRIEVED and RANKED_LOW = Team 2; DROPPED, WRONG_STATUS and GENERATE = Team 3.
2. Pick 5 wrong answers and follow each through every step: what was retrieved, what went into the prompt, what the model said.
3. Write `eval/reports/failures_day12.md` (and `failures_day17.md`), and present it in the weekly call. End with one line per team: "fix this next".

## Done when
- [ ] Both reports are committed
