# [EVAL-08] For each wrong answer, find which step failed
labels: team:eval, size:M
**Owner:** E3 · **Size:** M (2-3 days) · **Due:** day 11 · **Needs:** RET-11, GEN-05

## In one sentence
Label every wrong answer with the **first** step that lost the evidence, so each team knows which failures are theirs.

## What to do
In `trace()` in `src/rag/failure_trace.py`, for a wrong answer, check in this order and return the first label that applies:
1. **PARSE:** for some evidence item, `rag.match.on_page(quote, parsed page text)` is False. Look the page up in `docs`.
2. **CHUNK:** no chunk of that document passes `rag.match.is_relevant(quote, chunk.text)`.
3. **NOT_RETRIEVED:** `result.relevant_ranks` is empty (nothing relevant in the top 20).
4. **RANKED_LOW:** relevant chunks exist, but all are ranked below k.
5. **DROPPED:** a relevant chunk is in `result.dropped_ids` (cut by the token budget).
6. **WRONG_STATUS:** `result.status_correct` is False.
7. **GENERATE:** anything else: the model had the evidence and still got it wrong.

`BAD_QUESTION` is never set by code: a person sets it when the question itself is wrong.

## Done when
- [ ] One test per label, each building a situation where that label must come out (in `tests/test_failure_trace.py`)
- [ ] `metrics.json` shows how many of each label a run has (`run.py` already counts them)
