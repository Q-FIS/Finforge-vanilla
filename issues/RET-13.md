# [RET-13] Write 20 tricky questions
labels: team:ret, size:M
**Owner:** T4 · **Size:** M (2-3 days) · **Due:** day 11 · **Needs:** EVAL-02 (the question guideline)

## In one sentence
Write 20 questions that are easy to get wrong, to test retrieval properly.

## What to do
Follow E1's guideline (`eval/QUESTION_GUIDE.md`). Write questions where the wrong passage looks almost right:
- the right figure in the wrong year (FY2024 vs FY2025, or last year's number printed in this year's report)
- a subsidiary vs the parent company
- standalone vs consolidated
- similar words: "revenue from operations" vs "total income"

Use category `period_entity_trap` or `statement_basis`. Every question needs exact quotes and page numbers, and must pass `scripts/check_questions.py`.

## Done when
- [ ] 20 questions in `eval/questions.jsonl`, each checked by a fresher
