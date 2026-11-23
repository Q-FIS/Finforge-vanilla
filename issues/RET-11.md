# [RET-11] Retrieval scores, written by hand
labels: team:ret, size:M
**Owner:** T4 · **Size:** M (2-3 days) · **Due:** day 7 · **Needs:** nothing (`rag.match` is ready)

## In one sentence
Write the functions that measure whether retrieval found the evidence: hit@k, recall@k, MRR, nDCG@k.

## What to do
In `src/rag/ret/metrics.py`:
1. `relevance(hits, question)`: for each hit, 1 if it is relevant, else 0. A hit is relevant when some evidence item has the same `doc_id`, its page is between `chunk.page_start - 1` and `chunk.page_end + 1`, and `rag.match.is_relevant(evidence.quote, chunk.text)` is True. **Use `is_relevant`, not your own matching**: it also checks the figures, so the consolidated "Profit for the year" row doesn't count as evidence for the standalone one.
2. `evidence_ranks(hits, question)`: for each evidence item, the rank of the first hit that contains it, or None.
3. `hit_at_k`: 1.0 if any of the first k is relevant.
4. `recall_at_k`: the share of evidence items whose rank is at most k. (We count *evidence items*, not chunks, because the number of chunks depends on the chunker.)
5. `full_support_at_k`: 1.0 only if *every* evidence item is within k.
6. `mrr`: 1 / (rank of the first relevant hit), or 0.0.
7. `ndcg_at_k`: DCG = sum of rel_i / log2(i + 1) for i = 1..k; divide by the best possible DCG.
8. Questions with no evidence (unanswerable ones): every function returns 0.0.

## Example (make it a test)
Relevance `[0, 1, 0, 1, 0]`, k = 5: hit@5 = 1.0 · MRR = 0.5 · nDCG@5 = (1/log2(3) + 1/log2(5)) / (1 + 1/log2(3)) ≈ 0.651. Work it out on paper first.

## Done when
- [ ] The example above is a test
- [ ] A test with the fixture: for question FX02 (standalone profit), a page-3 (consolidated) chunk is **not** relevant
- [ ] Tests for no hits, no evidence, and k bigger than the number of hits, in `tests/ret/test_metrics.py`

## Learn first
- Introduction to Information Retrieval, chapter 8 (free online).
