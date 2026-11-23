# [EVAL-09] "Oracle" mode: give the model the true evidence
labels: team:eval, size:S
**Owner:** E2 · **Size:** S (1 day) · **Due:** day 10 · **Needs:** RET-11

## What is this, in plain words?
To know how much accuracy retrieval costs us (experiment E7), we need a run
where retrieval is **perfect**: skip the search, and hand the model the chunks
that really contain the evidence. That's "oracle" mode
(`retrieve.method: oracle`). It's a measuring tool, never a real result.

## Step by step
In `run_pipeline()` in `src/rag/run.py`, where it says `raise NotImplementedError("... EVAL-09")`:
1. For the question, collect every chunk that is relevant to one of its evidence items: same `doc_id`, page within 1 (`chunk.page_start - 1 <= evidence.page <= chunk.page_end + 1`), and `rag.match.is_relevant(evidence.quote, chunk.text)`. It's the same rule as in `metrics.relevance` (RET-11); reuse that code if you can.
2. Turn them into `Hit(chunk=..., score=1.0, rank=1, 2, 3..., method="oracle")`.
3. Wrap them in a `Retrieval`, the same way the `"none"` mode just above it does: `Retrieval(question.question, hits, Filters(), "none", 1.0, 0.0, 0.0)`.
4. Unanswerable questions get no hits (just like closed-book).

## How to test it
`tests/test_oracle.py` with `tests/ci.yaml` and `retrieve: {method: oracle}`: for every answerable fixture question, its `context_ids` contain a chunk that holds the evidence.

## Done when
- [ ] The test passes, and experiment E7 (GEN-11) can use `retrieve.method: oracle`
