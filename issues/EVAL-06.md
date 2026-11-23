# [EVAL-06] Score the answers automatically
labels: team:eval, size:M
**Owner:** G1 · **Size:** M (2-3 days) · **Due:** day 10 · **Needs:** GEN-08

## What is this, in plain words?
After the model answers, we must decide: **was it right?** For number answers
("₹16,900 crore") a program can decide, by comparing the amount with the
correct one in the question file, using GEN-08's `same_amount`, so "₹1.69
lakh crore" also counts. For text answers ("Who is the CEO?") a person
decides. You write the automatic part, plus a small tool that sends the rest to
a person and reads their marks back.

## What it must do
```python
score(question, answer, report)  ->  (status_correct, correct)
# FX02 (standalone profit, answer_value 169000000000.0, unit "INR"):
#   answer "₹16,900 crore [C1]", status "answered"   -> (True, True)
#   answer "₹18,200 crore [C1]", status "answered"   -> (True, False)   # the consolidated figure
#   status "insufficient_evidence"                   -> (False, False)
# a question with unit "" (text answer)              -> (status_correct, None)   # a person decides
```

## Step by step
In `score()` in `src/rag/score.py`:
1. `status_correct` is already done: `answer.status == question.expected_status`.
2. If the question expects `insufficient_evidence`, it's already done too: correct = status_correct.
3. **Number answers** (`question.unit` is `"INR"`, `"%"` or `"count"`):
   - if `answer.status != "answered"` → `correct = False`;
   - otherwise `correct` = True if **any** amount in `extract_amounts(answer.text)` is `same_amount` as `Amount(question.answer_value, question.unit, question.answer_text)`.
4. **Text answers** (unit `""`) → `correct = None` (a person decides).
5. **Grading tool:** `scripts/grading.py` with two commands:
   - `export <run folder>`: writes `grading.csv` with question id, question, correct answer, model answer, and an empty `correct` column, for every result where `correct` is None;
   - `merge <run folder>`: reads the filled-in `correct` column (yes/no) back into `results.jsonl`, then re-computes `metrics.json` (call `save_run`'s scoring part from `run.py`).

## How to test it
`tests/test_score.py`, with the three FX02 cases above, plus: "₹1.69 lakh crore" counts as correct; the right number with the wrong unit ("16,900%") is wrong; a refusal on an unanswerable question is correct; a text question gives None. And one test for export → fill in → merge.

## Done when
- [ ] The tests pass, and the `STUB(EVAL-06)` line is gone
