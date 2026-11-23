# [REP-09] Tests every chunker must pass, plus 10 financial cases
labels: team:rep, size:S
**Owner:** R3 · **Size:** S (1 day) · **Due:** day 9 · **Needs:** REP-05

## What is this, in plain words?
We have three chunkers written by two people. Instead of each person writing
their own checks, you write **one set of rules** and run it against all three
automatically. Then you add 10 small, realistic cases where a bad split would
separate a figure from its year or its explanation, the exact failure that
makes RAG systems give wrong financial answers.

## Step by step
1. Create `tests/rep/test_chunk_rules.py`.
2. Use pytest's parametrize to run every test once per chunker:
   ```python
   @pytest.mark.parametrize("strategy", ["fixed", "sentence", "section"])
   def test_ids_are_unique(strategy):
       chunks = chunk_document(doc, ChunkConfig(strategy=strategy), EmbedConfig())
       ids = [c.chunk_id for c in chunks]
       assert len(ids) == len(set(ids))
   ```
3. Rules to test for every chunker: ids are unique; ids are the same on a second run; `n_tokens` is within the limit; no chunk is empty; `chunk.text` is found in the document text; `page_start <= page_end`.
4. Write **10 financial cases**: small texts where a figure, its year and its explanation must stay together. For example:
   ```
   Revenue from operations: FY2024 ₹1,20,000 crore; FY2025 ₹1,45,000 crore.
   The increase was primarily attributable to higher domestic sales.
   ```
   With a 512-token limit, check that "FY2025" and "₹1,45,000 crore" end up in the same chunk. Make up the figures; don't copy real company data.
5. If a chunker is **expected** to fail a case (the fixed chunker might, at small sizes), don't hide it: mark the test `@pytest.mark.xfail(reason="fixed chunker can cut between a year and its figure")`.

## Done when
- [ ] The rules run for all three chunkers in CI
- [ ] 10 financial cases, and every `xfail` has a reason that explains it
