# [RET-04] Vector search with numpy
labels: team:ret, size:M
**Owner:** T2 · **Size:** M (2-3 days) · **Due:** day 6 · **Needs:** nothing (use `FakeEmbedder` vectors)

## In one sentence
Make `DenseIndex.search` find the k chunks whose vectors are closest to the question's vector.

## What to do
In `DenseIndex` in `src/rag/ret/retrieve.py`:
1. Scores: `self.vectors @ query_vector` gives one score per chunk (the vectors have length 1, so this is cosine similarity).
2. Set the score of chunks where `allowed` is False to `-inf`.
3. Find the top k with `np.argpartition` (faster than sorting everything), then sort just those k. If two scores are equal, the lower chunk number comes first.
4. Return `Hit`s: rank 1 = best, `method="dense"`.
5. Guards: an empty index returns `[]`. If `query_vector` has a different length than the chunk vectors, raise `ValueError` with a clear message.
6. `save(folder)` and `load(folder)`: `vectors.npy`, `chunks.jsonl` (use `save_jsonl`), and `meta.json` with the model name.

## Done when
- [ ] Tests for: an empty index, k bigger than the number of chunks, equal scores, wrong vector length, and save then load, in `tests/ret/test_dense.py`
- [ ] `uv run pytest` and the smoke run pass

## Learn first
- Why searching every vector ("brute force") always gives the exact answer, and what it costs per question (N x d multiplications).
