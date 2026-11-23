# [EVAL-03] A script that checks every question
labels: team:eval, size:S
**Owner:** E1 · **Size:** S (1 day) · **Due:** day 6 · **Needs:** nothing (it can use raw PyMuPDF text until REP-01 is merged)

## In one sentence
`uv run python scripts/check_questions.py eval/questions.jsonl` finds mistakes in questions before they cause wrong scores.

## What to do
Create `scripts/check_questions.py`. For the given file:
1. Load it with `load_jsonl(path, Question)`. That already catches bad JSON, typos in field names and wrong values.
2. Check that ids are unique, and that `category` is in `rag.schema.CATEGORIES`.
3. For every evidence item, open that page of the PDF and check `rag.match.on_page(quote, page_text)`. If it fails, search the other pages and print where the quote really is ("Q017: quote not on page 212; found on page 214").
4. Unanswerable questions must have no evidence; other questions must have at least one.
5. At the end, print how many questions there are per category, compared with the guide's targets.
6. Exit with code 1 if anything failed, so CI can run it.

## Done when
- [ ] It passes on `tests/fixtures/questions.jsonl`
- [ ] A test shows it catches a wrong page number and a mistyped figure
- [ ] It runs in CI on `eval/questions.jsonl` (add a step to `.github/workflows/ci.yml`)
