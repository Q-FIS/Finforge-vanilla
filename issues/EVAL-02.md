# [EVAL-02] The guide for writing questions
labels: team:eval, size:S
**Owner:** E1 · **Size:** S (1 day) · **Due:** day 4 · **Needs:** EVAL-01

## In one sentence
A one-page guide, so 25 people write questions the same way.

## What to do
Write `eval/QUESTION_GUIDE.md`. It must cover:
1. Write questions **from the PDF**, never from the system's answers.
2. The quote: copy the exact words from the PDF, 1-3 sentences or one table row with its label and figures.
3. The page: the number your PDF viewer shows (page 1 = the first page), **not** the number printed on the page.
4. List **every** place the answer appears (reports repeat key figures in the highlights, the directors' report and the statements).
5. Fill in `company`, `fy` and `basis` (standalone / consolidated / none).
6. `answer_value`: money in plain rupees (₹1,45,000 crore = 1450000000000). Percent as written (12.5). Counts as written.
7. Categories and how many of each: single_fact_table 25%, single_fact_text 20%, multi_year 15%, statement_basis 10%, period_entity_trap 10%, calculation 5%, unanswerable 15%.
8. One line of JSON per question; show the format (copy one from `tests/fixtures/questions.jsonl`).
9. Add 10 complete example questions about our real reports.

## Done when
- [ ] Two freshers each write one question using only the guide, and both pass `scripts/check_questions.py` (EVAL-03)
