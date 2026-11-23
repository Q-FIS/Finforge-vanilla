# The issues: every task, written out

Each file in this folder is one task (one GitHub issue). Find your role
(R1-R4, T1-T4, G1-G4, E1-E3) below and read your files in order of due day.

## How to read an issue

- **Owner · Size · Due · Needs.** Size S = up to 1 day, M = 2-3 days.
  "Due" is the last day it can be merged without slowing anyone down.
  "Needs" lists the issues you must wait for; usually you can start earlier
  using the test files in `tests/fixtures/`.
- **What to do.** The steps, in order, with the exact file and function.
  Run `grep -rn "STUB(<issue id>)" src/` to see exactly which code to replace.
- **Done when.** The checklist your PR must meet. Reviewers check this list.
- **Learn first.** What to understand before you write code. Your reviewer
  will ask you about it.
- **"should"** issues are extras: only start one when your other issues are done.

Every PR needs: green CI + one teammate's approval + one fresher's sign-off.
If you can't explain a line of your code, it doesn't merge.

## All issues, by person

| Role | Issues (due day) |
| --- | --- |
| R1 | REP-01 (5), REP-02 (7), REP-03 (8), REP-13 (11) |
| R2 | REP-04 (3), REP-05 (6), REP-06 (8), REP-15 (15) |
| R3 | REP-07 (5), REP-08 (9), REP-09 (9), REP-14 should (12) |
| R4 | REP-10 (7), REP-11 (7), REP-12 (10), REP-16 (15) |
| T1 | RET-01 (4), RET-02 (7), RET-03 (8), RET-14 (15) |
| T2 | RET-04 (6), RET-05 (9), RET-07 (9), RET-06 (11) |
| T3 | RET-08 (6), RET-09 (8), RET-10 (10), RET-16 (15) |
| T4 | RET-11 (7), RET-12 (9), RET-13 (11), RET-15 (15) |
| G1 | GEN-02 (4), GEN-01 (5), GEN-03 (6), EVAL-06 (10) |
| G2 | GEN-04 (5), GEN-05 (8), GEN-12 (15) |
| G3 | GEN-06 (7), GEN-07 (9), GEN-10 (11), GEN-11 (15) |
| G4 | GEN-08 (6), GEN-09 (10), GEN-13 should (14) |
| E1 | EVAL-01 (3), EVAL-02 (4), EVAL-03 (6), EVAL-04 (6-12) |
| E2 | EVAL-05 (10), EVAL-09 (10), EVAL-07 (12) |
| E3 | EVAL-08 (11), EVAL-10 (12), EVAL-11 (12 and 17) |

Everyone also writes 4 evaluation questions from day 6 (organised by E1 in EVAL-04).

## The most important path

These issues decide when the first real run can happen (day 10). If one is
late, tell the lead the same day; T1, T2 and E2 are the backups:

REP-01 parse -> REP-02 clean -> REP-04 tokens -> REP-05 / REP-08 chunk ->
REP-11 embed -> RET-04 search -> GEN-01 model -> GEN-05 context ->
GEN-07 answer -> EVAL-05 first run (day 10)

## Creating them on GitHub

`scripts/create_issues.sh` creates one GitHub issue per file here (title,
labels and body). Run `scripts/setup_github.sh` first so the labels exist.
