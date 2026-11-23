# [EVAL-08] For each wrong answer, find which step failed
labels: team:eval, size:M
**Owner:** E3 · **Size:** M (2-3 days) · **Due:** day 11 · **Needs:** RET-11, GEN-05

## What is this, in plain words?
"The answer was wrong" doesn't tell anyone what to fix. This function follows a
wrong answer back through the pipeline, and names the **first** step where the
evidence got lost. Then each team gets a clear list of its own failures, and
nobody blames another team without data.

## The labels, checked in this order (stop at the first that's true)
| Label | It means | Whose |
| --- | --- | --- |
| PARSE | the evidence text isn't in the parsed page | Team 1 |
| CHUNK | the evidence was parsed, but no chunk holds enough of it | Team 1 |
| NOT_RETRIEVED | no relevant chunk in the top 20 | Team 2 |
| RANKED_LOW | a relevant chunk is in the top 20, but below k | Team 2 |
| DROPPED | it was retrieved, but cut by the token budget | Team 3 |
| WRONG_STATUS | answered when it should have refused, or the opposite | Team 3 |
| GENERATE | the model had the evidence and still got it wrong | Team 3 |

`BAD_QUESTION` is never set by code: a person sets it when the question itself turns out to be wrong.

## Step by step
In `trace()` in `src/rag/failure_trace.py` (it gets the question, its result, all documents and all chunks):
1. If the answer is correct, return `""` (already done).
2. **PARSE:** for each evidence item, find its document in `docs` (by `doc_id`) and the page (`doc.pages[evidence.page - 1]`). If `rag.match.on_page(evidence.quote, page.text)` is False for **every** evidence item → `"PARSE"`.
3. **CHUNK:** if no chunk of that document passes `rag.match.is_relevant(evidence.quote, chunk.text)` for any evidence item → `"CHUNK"`.
4. **NOT_RETRIEVED:** `result.relevant_ranks` is empty → `"NOT_RETRIEVED"`.
5. **RANKED_LOW:** every rank in `result.relevant_ranks` is bigger than k → `"RANKED_LOW"`. The function needs k: add a `k: int` parameter and pass `cfg.retrieve.k` from `run.py`.
6. **DROPPED:** a relevant chunk's id is in `result.dropped_ids` and none is in `result.context_ids` → `"DROPPED"`.
7. **WRONG_STATUS:** `result.status_correct` is False → `"WRONG_STATUS"`.
8. Otherwise → `"GENERATE"`.
9. Unanswerable questions have no evidence: skip steps 2-6 for them.

## How to test it
`tests/test_failure_trace.py`: build one small situation per label by hand (a tiny `Document`, a few `Chunk`s, a `Result`), and check that exactly that label comes out. The `Result` fields you need are in `src/rag/schema.py`.

## Done when
- [ ] One test per label passes, and the `STUB(EVAL-08)` line is gone
- [ ] The smoke run's `metrics.json` shows the label counts (`run.py` already counts them)
