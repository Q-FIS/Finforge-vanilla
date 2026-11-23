# [RET-11] Retrieval scores, written by hand
labels: team:ret, size:M
**Owner:** T4 · **Size:** M (2-3 days) · **Due:** day 7 · **Needs:** nothing (`rag.match` is ready)

## What is this, in plain words?
How do we know if retrieval is good? For each question we know where the
answer is in the report (the "evidence": a quote and a page). After a search,
we check whether the chunks found contain that evidence, and how high they
were ranked. Several standard scores summarise this; you write them by hand.
Every experiment in the project is judged with them, so they must be exactly
right.

## Where it fits
`run.py` calls these after every search, and saves the averages in `metrics.json`.

## The scores, in plain words
Say the search returned 5 chunks, and we marked each relevant (1) or not (0): `[0, 1, 0, 1, 0]`.
- **hit@k:** did *any* of the first k contain the evidence? Here hit@5 = 1.0.
- **recall@k:** what share of the question's *evidence items* were found in the first k? (A question can have 2 evidence items, for example the figure in the highlights and in the statements.)
- **full_support@k:** 1.0 only if *all* evidence items were found in the first k.
- **MRR** (mean reciprocal rank): 1 ÷ (the rank of the first relevant chunk). Here the first relevant is at rank 2, so 0.5.
- **nDCG@k:** rewards relevant chunks near the top more than ones near the bottom:
  `DCG = sum of rel_i / log2(i + 1)` for i = 1..k, divided by the best possible DCG (all relevant ones at the top).
  Here: DCG = 1/log2(3) + 1/log2(5) = 0.631 + 0.431 = 1.062; best = 1/log2(2) + 1/log2(3) = 1.631; nDCG = 0.651.

## Step by step
In `src/rag/ret/metrics.py`:
1. **`relevance(hits, question)`**: for each hit, 1 if for **some** evidence item:
   - `evidence.doc_id == hit.chunk.doc_id`, and
   - `hit.chunk.page_start - 1 <= evidence.page <= hit.chunk.page_end + 1`, and
   - `rag.match.is_relevant(evidence.quote, hit.chunk.text)` is True.
   Otherwise 0.
2. **`evidence_ranks(hits, question)`**: for each evidence item, the rank of the first hit that contains it (same 3 checks), or `None`.
3. **`hit_at_k(rels, k)`**: `1.0 if any(rels[:k]) else 0.0`.
4. **`recall_at_k(ranks, k)`**: the share of `ranks` that are not None and `<= k`. If there are no evidence items, return 0.0.
5. **`full_support_at_k(ranks, k)`**: 1.0 if there is evidence and every rank is not None and `<= k`.
6. **`mrr(rels)`**: `1 / (position of the first 1, counting from 1)`, or 0.0.
7. **`ndcg_at_k(rels, k)`**: as above. If there are no relevant chunks at all, return 0.0. Use `math.log2`.

## Watch out for
- **Use `rag.match.is_relevant`; don't write your own matching.** It also checks that the evidence's figures are in the chunk. Without that, the consolidated "Profit for the year 18,200" row would count as evidence for the standalone "Profit for the year 16,900" row, since they share most of their words.
- **Why recall counts evidence items, not chunks:** the number of relevant chunks changes with the chunker (one quote can be split over two chunks). Counting evidence keeps the chunking experiment fair.
- Questions with no evidence (unanswerable ones) score 0.0 everywhere. That's fine; they're judged on whether the model refuses.

## How to test it
`tests/ret/test_metrics.py`:
- the `[0, 1, 0, 1, 0]` example above, with every score (use `pytest.approx` for nDCG);
- no hits; a question with no evidence; k bigger than the number of hits;
- the fixture: for question FX02 (standalone profit, evidence on page 4), a chunk with the page-3 consolidated text is **not** relevant, and a chunk with the page-4 text **is**.

## Done when
- [ ] The tests pass
- [ ] The `STUB(RET-11)` lines are gone, and the smoke run's `metrics.json` shows non-zero scores

## Learn first
- Introduction to Information Retrieval, chapter 8 (free online): precision, recall and ranked evaluation.
- Work out the example above on paper before you write any code.
