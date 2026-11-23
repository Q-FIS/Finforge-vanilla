# [RET-08] Read the company, year and basis from a question
labels: team:ret, size:M
**Owner:** T3 · **Size:** M (2-3 days) · **Due:** day 6 · **Needs:** nothing (use `tests/fixtures/registry.csv`)

## What is this, in plain words?
Embeddings are bad at telling "FY2024 revenue" from "FY2025 revenue", or Infosys
from another company: the sentences mean almost the same thing. But the
**question usually says** which company and year it wants. You read those out
of the question with rules and regular expressions, so retrieval can filter
on them (RET-07).

## What it must do
```python
extract_filters("What was Infosys' consolidated revenue in FY 2024-25?", registry)
# -> Filters(company="infosys", fy="FY2025", basis="consolidated", source="extracted")

extract_filters("Compare Acme's revenue in FY2024 and FY2025", registry)
# -> Filters(company="acme", fy=None, basis=None, source="extracted")    # two years: don't filter on year

extract_filters("What was revenue?", registry)
# -> Filters(company=None, fy=None, basis=None, source="extracted")
```

## Step by step
In `extract_filters` in `src/rag/ret/filters.py`:
1. **Company:** for every registry entry, look for each of its `aliases` in the question: ignore capitals, and match whole words only, with `re.search(r"\b" + re.escape(alias) + r"\b", question, re.IGNORECASE)`. Also accept the alias followed by `'s` or `'`.
   - If several aliases match, the **longest** wins ("Acme Chemicals" beats "Acme").
   - If two **different companies** match, set `company=None`.
2. **Year:** find every year mentioned and turn each one into the form `"FY2025"`:
   - `FY2025`, `FY 2025`, `FY25` → FY2025
   - `FY 2024-25`, `2024-25`, `2024–25` (with an en dash), `financial year 2024-25` → FY2025 (the **second** year counts)
   - `year ended March 31, 2025` and `31st March 2025` → FY2025
   - If you find exactly one distinct year, use it; if you find two or more, set `fy=None`.
3. **Basis:** "standalone" → `"standalone"`, "consolidated" → `"consolidated"`, both or neither → `None`.
4. Return `Filters(company=..., fy=..., basis=..., source="extracted")`.

## Watch out for
- `FY25` means 2025, but `FY2024-25` contains both "2024" and "25". Handle the range patterns **first**, then the single years, so you don't count it twice.
- Questions comparing two companies or two years must **not** be filtered, or the filter would hide half the answer.

## How to test it
`tests/ret/test_filters.py`, with at least 30 questions written the way real people ask: every year format above, possessives ("Acme's"), two companies, two years, no company, capital letters, extra spaces.

## Done when
- [ ] At least 30 tests pass
- [ ] The `STUB(RET-08)` line is gone
