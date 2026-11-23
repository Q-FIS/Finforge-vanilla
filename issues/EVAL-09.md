# [EVAL-09] "Oracle" mode: hand the model the true evidence
labels: team:eval, size:S
**Owner:** E2 · **Size:** S (1 day) · **Due:** day 10 · **Needs:** RET-11

## In one sentence
With `retrieve.method: oracle`, skip search and give the model the chunks that really contain the evidence: the best retrieval could ever do.

## What to do
In `run_pipeline()` in `src/rag/run.py` (the `NotImplementedError("... EVAL-09")` line):
1. For the question, find every chunk where `rag.match.is_relevant(evidence.quote, chunk.text)` for one of its evidence items (same document, page within 1).
2. Turn them into `Hit`s with `method="oracle"`, `score=1.0`, and ranks 1, 2, 3...
3. Wrap them in a `Retrieval`, like the "none" mode above it does.

## Done when
- [ ] A test over the fixture questions: in oracle mode, every answerable question's context contains its evidence
- [ ] GEN-11 (experiment E7) can use it
