# [EVAL-03] A script that checks every question
labels: team:eval, size:S
**Owner:** E1 · **Size:** S (1 day) · **Due:** day 6 · **Needs:** nothing (use raw PyMuPDF text until REP-01 is merged)

## What is this, in plain words?
People will make mistakes writing questions: a wrong page number, a typo in a
figure, a missing field. One wrong question means one wrong score, and someone
wastes a day chasing a "bug" that's really a bad question. This script catches
those mistakes the moment a question is added.

## What it must do
```
$ uv run python scripts/check_questions.py eval/questions.jsonl
Q017: evidence quote not found on page 212 of infosys_ar_fy2025 (found on page 214)
Q031: category 'single_fact' is not valid
Q044: answerable question has no evidence
82 questions, 3 problems.
Per category: single_fact_table 21 (target 25%) ...
```
It exits with code 1 if there are problems, so CI can block bad questions.

## Step by step
Create `scripts/check_questions.py`:
1. **Load** with `load_jsonl(path, Question)` (from `rag.schema`). That already catches broken JSON, misspelled field names and invalid statuses. Catch the `ValueError` and print it.
2. **Check:**
   - ids are unique;
   - `category` is in `rag.schema.CATEGORIES`;
   - unanswerable questions (`expected_status == "insufficient_evidence"`) have no evidence; other questions have at least one;
   - every evidence `doc_id` is in the registry.
3. **Check every quote is on its page:** open the PDF (`pymupdf.open(pdf_path(entry, "data/pdfs"))`), take the page's text (`doc[page - 1].get_text()`), and check `rag.match.on_page(quote, page_text)`. If it fails, search all the other pages, and say where the quote really is.
4. **Count** questions per category, and print them next to the guide's targets.
5. `sys.exit(1)` if anything failed.
6. **Add it to CI:** in `.github/workflows/ci.yml`, add a step that runs it on `tests/fixtures/questions.jsonl` (CI doesn't have the real PDFs). Give the script `--registry` and `--pdf-dir` arguments, so CI can point them at `tests/fixtures/registry.csv` and `tests/fixtures`.

## How to test it
`tests/test_check_questions.py`: it passes on `tests/fixtures/questions.jsonl`; a copy with a wrong page number fails and names the right page; a copy with "16,900" changed to "16,800" fails (because `on_page` checks the figures).

## Done when
- [ ] The tests pass, and it runs in CI
