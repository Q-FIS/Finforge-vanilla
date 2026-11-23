# [RET-05] Check our search against FAISS
labels: team:ret, size:S
**Owner:** T2 · **Size:** S (1 day) · **Due:** day 9 · **Needs:** RET-04, REP-11 (real vectors)

## In one sentence
Prove `DenseIndex.search` returns exactly what FAISS's exact index returns.

## What to do
1. Build `faiss.IndexFlatIP(dim)`, add the same vectors, and search with the same query vectors.
2. FAISS returns row numbers. Map them back to chunks (row i = `chunks[i]`).
3. Compare with our results for every dev question.

## Done when
- [ ] Same top-k chunks, with scores within 0.00001, for every dev question (in `tests/ret/test_faiss_parity.py`)
