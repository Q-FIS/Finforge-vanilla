# [EVAL-06] Score the answers automatically
labels: team:eval, size:M
**Owner:** G1 · **Size:** M (2-3 days) · **Due:** day 10 · **Needs:** GEN-08

## In one sentence
Decide automatically whether an answer's figure is right, and send the text answers to a person.

## What to do
In `score()` in `src/rag/score.py`:
1. `status_correct` already works: the status must equal the expected status.
2. For questions whose `unit` is "INR", "%" or "count": the answer is correct if its status is "answered" **and** one of `extract_amounts(answer.text)` is `same_amount` as the question's `answer_value` (with the same unit).
3. For other questions: `correct = None` (a person checks it).
4. Write `scripts/grading.py` with two commands: `export` writes the `correct = None` answers of a run to `grading.csv` with an empty "correct" column; `merge` reads the filled-in file back into `results.jsonl`.

## Done when
- [ ] Tests: right number and unit = correct; right number with "insufficient_evidence" = wrong; "₹1.45 lakh crore" equals "₹1,45,000 crore"; the wrong year's figure = wrong (in `tests/test_score.py`)
