# [RET-05] Check our search against FAISS
labels: team:ret, size:S
**Owner:** T2 · **Size:** S (1 day) · **Due:** day 9 · **Needs:** RET-04, REP-11 (real vectors)

## What is this, in plain words?
FAISS is Facebook's library for fast vector search, used in many RAG systems.
Its simplest index, `IndexFlatIP`, does exactly what our numpy search does:
compare with every vector using the dot product ("IP" = inner product). You
prove ours gives the same results.

## Step by step
1. In `tests/ret/test_faiss_parity.py`: `index = faiss.IndexFlatIP(dim)`, then `index.add(vectors)` (float32).
2. `scores, rows = index.search(query_vectors, k)`. FAISS returns **row numbers**; row i is `chunks[i]`.
3. For every dev question (or 50 random query vectors if questions aren't ready), compare FAISS's chunk ids and scores with `DenseIndex.search`.

## Done when
- [ ] Same top-k chunk ids, and scores within 0.00001, for every query
