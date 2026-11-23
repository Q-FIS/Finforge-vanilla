# [REP-09] Tests every chunker must pass
labels: team:rep, size:S
**Owner:** R3 · **Size:** S (1 day) · **Due:** day 9 · **Needs:** REP-05

## In one sentence
One set of tests that runs against all three chunkers, plus 10 small "financial" cases.

## What to do
1. In `tests/rep/test_chunk_rules.py`, use `@pytest.mark.parametrize("strategy", ["fixed", "sentence", "section"])` and check, for every chunk:
   ids are unique · same ids on a second run · `n_tokens` within the limit · no empty chunk · `chunk.text` is found in the page text · `page_start <= page_end`
2. Write 10 small texts where a bad split would separate a figure from its year or its explanation. Example:
   "Revenue from operations: FY2024 ₹1,20,000 crore; FY2025 ₹1,45,000 crore. The increase was due to higher domestic sales."
   Check that the figure and its year end up in the same chunk.
3. If a chunker is *expected* to fail a case (the fixed chunker will), mark that test `@pytest.mark.xfail(reason="...")` and explain why.

## Done when
- [ ] The tests run in CI for all three chunkers
- [ ] Every `xfail` has a reason that explains it
