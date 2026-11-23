# [EVAL-04] Collect about 80 checked questions, and lock the test set
labels: team:eval, size:M
**Owner:** E1 · **Size:** M (runs from day 6 to day 12) · **Due:** day 12 · **Needs:** EVAL-02, EVAL-03

## In one sentence
Organise everyone writing 4 questions each, get every one checked, and set aside 20 as the locked test set.

## What to do
1. Day 6: give each of the 25 people 4 question slots, spread across the categories (a shared sheet works).
2. People add questions to `eval/questions.jsonl` through PRs. `check_questions.py` runs on every PR.
3. A fresher who didn't write the question checks it against the PDF and puts their name in `checked_by`.
4. You decide whenever the writer and the checker disagree.
5. Day 12: mark 20 questions `"split": "test"` (spread across categories), and the rest `"dev"`. Write the sha256 of the test questions in `eval/TEST_SET_LOCK.txt`. From now on, only runs with `--final` may use them.

## Done when
- [ ] About 80 questions, every one with `checked_by` filled in
- [ ] `eval/TEST_SET_LOCK.txt` committed on day 12
