# [EVAL-04] Collect about 80 checked questions, and lock the test set
labels: team:eval, size:M
**Owner:** E1 · **Size:** M (runs from day 6 to day 12) · **Due:** day 12 · **Needs:** EVAL-02, EVAL-03

## What is this, in plain words?
You organise the question-writing: 25 people × 4 questions each, every one
checked by a second person. Then you set 20 aside as the **test set**: we
don't look at those until the very end. That's how we make sure we didn't
tune the system to the exact questions we measure it on.

## Step by step
1. **Day 6: hand out the slots.** Make a shared sheet with 25 names × 4 slots, and spread the categories using the guide's shares, so we don't get 80 "revenue" questions. Each of the 3 companies gets about a third.
2. **Writing:** people add their questions to `eval/questions.jsonl` through PRs. `check_questions.py` must pass.
3. **Checking:** a fresher who didn't write the question opens the PDF, checks the answer and the quote, and puts their name in `checked_by`.
4. **Disagreements:** you decide. If the question itself is unclear, fix it or drop it.
5. **Day 12: lock the test set.**
   - Choose 20 questions, spread across categories and companies, and set `"split": "test"`. All the others are `"dev"`.
   - Write the sha256 of the test questions (their JSON lines, sorted by id) into `eval/TEST_SET_LOCK.txt`, with the date.
   - From now on, runs on the test questions need `--final` (already built into `run.py`), and only at the final milestone.

## Done when
- [ ] About 80 questions, every one with `checked_by` filled in, and `check_questions.py` passing
- [ ] `eval/TEST_SET_LOCK.txt` committed on day 12
