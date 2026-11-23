# [RET-04] Vector search with numpy
labels: team:ret, size:M
**Owner:** T2 · **Size:** M (2-3 days) · **Due:** day 6 · **Needs:** nothing (use `FakeEmbedder` vectors in your tests)

## What is this, in plain words?
This is the heart of retrieval. Every chunk has a vector (from REP-11). To
answer a question, we turn it into a vector too, then find the chunks whose
vectors are **closest** to it. With vectors of length 1, "closest" means the
biggest **dot product**. And with numpy, the dot products with all chunks at
once is one line: `scores = vectors @ query_vector`.

This is called **brute-force** (or "exact") search: we compare with every
chunk. For our ~15,000 chunks it takes milliseconds, so we don't need a vector
database.

## Where it fits
chunk vectors → **DenseIndex.build() (you)**; question vector → **DenseIndex.search() (you)** → `list[Hit]` → retrieve() (RET-07)

## What you must give back
```python
index = DenseIndex.build(chunks, vectors, "BAAI/bge-small-en-v1.5")
hits = index.search(query_vector, k=3)
# [Hit(chunk=<page-4 chunk>, score=0.82, rank=1, method="dense"),
#  Hit(chunk=<page-3 chunk>, score=0.79, rank=2, method="dense"),
#  Hit(chunk=<page-1 chunk>, score=0.41, rank=3, method="dense")]
```

## Step by step
In `DenseIndex` in `src/rag/ret/retrieve.py`:
1. **Scores:** `scores = self.vectors @ query_vector`, one number per chunk.
2. **Filtering:** if `allowed` is given, `scores = np.where(allowed, scores, -np.inf)`, so filtered-out chunks can never win.
3. **Top k without sorting everything:** `top = np.argpartition(-scores, k - 1)[:k]` finds the k best in any order (fast), then sort just those k: `top = top[np.argsort(-scores[top], kind="stable")]`.
4. **Ties:** if two chunks have the same score, the one with the smaller index comes first. A stable sort does this; write a test for it.
5. **Skip** anything with score `-inf` (filtered out), and return `Hit(chunk, float(score), rank, "dense")` with rank 1 = best.
6. **Guards:**
   - an empty index returns `[]`;
   - `k` bigger than the number of chunks just returns all of them (use `k = min(k, len(scores))`);
   - a query vector of the wrong length raises `ValueError("query has 256 numbers, index has 384")`.
7. **Save and load:** `save(folder)` writes `vectors.npy` (`np.save`), `chunks.jsonl` (`save_jsonl`) and `meta.json` (`{"model_name": ...}`); `DenseIndex.load(folder)` reads them back.

## How to test it
`tests/ret/test_dense.py`, with small hand-made vectors (3 chunks, 2 dimensions) so you know the answer:
- the best match comes first, with the right score;
- an empty index, k larger than the number of chunks, a tie, the wrong vector length;
- `allowed` hides chunks;
- save, then load, then search gives the same hits.

## Done when
- [ ] The tests pass
- [ ] `uv run pytest` and the smoke run pass
- [ ] The `STUB(RET-04)` line is gone

## Learn first
- Why is brute-force search always exactly right? What does one search cost? (Number of chunks × 384 multiplications.)
- Why do we use `argpartition` instead of sorting all the scores?
