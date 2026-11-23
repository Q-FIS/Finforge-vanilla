# [GEN-09] Check the citations with code
labels: team:gen, size:M
**Owner:** G4 · **Size:** M (2-3 days) · **Due:** day 10 · **Needs:** GEN-08

## In one sentence
Catch made-up citations and made-up numbers, using plain code (no LLM).

## What to do
In `validate_citations(answer, context)` in `src/rag/gen/citations.py`, fill a `CitationReport`:
1. `unknown_tags`: tags the answer cites that aren't in `context.passages`.
2. `failed_quotes`: citations whose quote is not really in their passage (`rag.match.fully_contains(quote, passage text)` is False).
3. `unsupported_numbers`: amounts in the answer (`extract_amounts`) that don't appear in any **cited** passage (`same_amount`).
4. `uncited_sentences`: sentences in the answer that contain a number but no [C..] tag.

## Done when
- [ ] Tests with 12 made-up answers covering: correct · cites a tag that doesn't exist · quote not in the passage · number not in any passage · number with no citation · a correct refusal (in `tests/gen/test_citations.py`)
