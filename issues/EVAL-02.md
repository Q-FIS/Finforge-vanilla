# [EVAL-02] The guide for writing evaluation questions
labels: team:eval, size:S
**Owner:** E1 · **Size:** S (1 day) · **Due:** day 4 · **Needs:** EVAL-01

## What is this, in plain words?
We judge the system with about 80 questions that we write ourselves, with the
correct answers and exactly where they are in the reports. 25 people will write
them, so they must all follow the same rules, or the scores mean nothing. You
write a one-page guide that anyone can follow without asking you.

## What the guide must say (write it in `eval/QUESTION_GUIDE.md`)
1. **Write questions from the PDF**, never from what our system answers.
2. **The quote:** copy the exact words from the PDF that answer the question: 1 to 3 sentences, or one table row with its label and figures (e.g. "Revenue from operations 1,45,000 1,20,000").
3. **The page:** the number your PDF viewer shows (page 1 = the very first page of the file), **not** the number printed at the bottom of the page. They're usually different.
4. **List every place the answer appears.** Annual reports repeat key figures in the highlights, the directors' report and the financial statements. Add each one as an evidence item.
5. **Labels:** fill in `company` (as in the registry), `fy` (e.g. FY2025) and `basis` (`standalone`, `consolidated` or `none`).
6. **The answer value:** money in plain rupees (₹1,45,000 crore → `1450000000000`), with `"unit": "INR"`; percentages as written (12.5, `"unit": "%"`); counts as written (`"unit": "count"`).
7. **Categories, and roughly how many of each:**

   | category | example | share |
   | --- | --- | --- |
   | single_fact_table | Consolidated revenue from operations, FY2025 | 25% |
   | single_fact_text | Number of employees at year end | 20% |
   | multi_year | Revenue in FY2024 vs FY2025 | 15% |
   | statement_basis | Standalone net profit, FY2025 | 10% |
   | period_entity_trap | A subsidiary's figure; last year's figure in this year's report | 10% |
   | calculation | Year-on-year revenue growth | 5% |
   | unanswerable | Something the reports don't contain (status `insufficient_evidence`, no evidence) | 15% |

8. **The format:** one line of JSON per question. Show a complete example (copy one from `tests/fixtures/questions.jsonl` and explain each field).
9. **10 complete example questions** about our real reports, one or two per category.

## Done when
- [ ] The guide is committed
- [ ] Two freshers each wrote one question using **only** the guide, and both passed `scripts/check_questions.py` (EVAL-03)
