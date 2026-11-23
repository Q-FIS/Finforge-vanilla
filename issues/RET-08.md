# [RET-08] Read the company, year and basis from a question
labels: team:ret, size:M
**Owner:** T3 · **Size:** M (2-3 days) · **Due:** day 6 · **Needs:** nothing (use `tests/fixtures/registry.csv`)

## In one sentence
From "What was Infosys' consolidated revenue in FY 2024-25?", get `company="infosys", fy="FY2025", basis="consolidated"`.

## What to do
In `extract_filters(question, registry)` in `src/rag/ret/filters.py`:
1. **Company:** look for each registry entry's `aliases` in the question (ignore capitals, match whole words). If several aliases match, the longest wins.
2. **Year:** all of these mean `"FY2025"`: "FY2025", "FY25", "FY 2024-25", "2024-25", "2024–25", "financial year 2024-25", "year ended March 31, 2025".
3. **Basis:** "standalone" or "consolidated" in the question.
4. If the question names **two** companies or **two** years, leave that field as `None`: questions comparing two things must not be filtered.
5. Return `Filters(company=..., fy=..., basis=..., source="extracted")`.

## Done when
- [ ] At least 30 tests in `tests/ret/test_filters.py`, written like real questions
- [ ] `uv run pytest` passes
