# [RET-13] Write 20 tricky questions
labels: team:ret, size:M
**Owner:** T4 · **Size:** M (2-3 days) · **Due:** day 11 · **Needs:** EVAL-02 (the question guide)

## What is this, in plain words?
Easy questions make every system look good. You write 20 questions **designed
to fool retrieval**, where a wrong passage looks almost exactly right. These
tell us whether our filters and metadata actually work.

## The kinds of traps (write at least 3 of each)
- **Wrong year:** the FY2025 report also prints last year's figure ("FY2024: ₹1,20,000 crore"). Ask for FY2024 and see if it picks the right column, or the FY2024 report.
- **Restated figures:** the FY2024 number printed in the FY2025 report sometimes differs from the FY2024 report's own number. Note this in `notes`.
- **Subsidiary vs parent:** a subsidiary's revenue vs the group's.
- **Standalone vs consolidated:** the same line item, two statements.
- **Similar words:** "revenue from operations" vs "total income" vs "other income".

## Step by step
1. Read E1's guide (`eval/QUESTION_GUIDE.md`) first. Your questions follow the same rules.
2. For each question, write the exact quote(s) and page(s) from the PDF, the correct `answer_value`, and `company`, `fy` and `basis`.
3. Category: `period_entity_trap` (wrong year, wrong company) or `statement_basis` (standalone vs consolidated).
4. Run `uv run python scripts/check_questions.py eval/questions.jsonl` (EVAL-03) until it passes.
5. A fresher checks each one in the PDF.

## Done when
- [ ] 20 questions in `eval/questions.jsonl`, each with `checked_by` filled in
