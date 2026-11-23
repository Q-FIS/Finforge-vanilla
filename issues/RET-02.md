# [RET-02] TF-IDF search, written by hand
labels: team:ret, size:M
**Owner:** T1 · **Size:** M (2-3 days) · **Due:** day 7 · **Needs:** RET-01

## In one sentence
Build a TF-IDF index over all chunks and return the chunks most similar to a question.

## What to do
In `TfidfIndex` in `src/rag/ret/tfidf.py`:
1. `build(chunks)`: tokenize every chunk. Count, for each word, in how many chunks it appears (document frequency, `df`).
2. IDF for each word: `log((N + 1) / (df + 1)) + 1`, where N is the number of chunks. (This is scikit-learn's formula, so RET-03 can compare.)
3. Each chunk's vector: for each word, (count in chunk) x IDF. Then divide by the vector's length, so it has length 1. Store it as a dict `{word: weight}`.
4. `search(query, k, allowed)`: make the query's vector the same way, score each chunk by the dot product, skip chunks where `allowed` is False, and return the best k as `Hit`s (rank 1 = best, `method="tfidf"`).
5. Speed-up (do this second): an "inverted index", `{word: [chunks that contain it]}`, so you only score chunks that share a word with the query.

## Done when
- [ ] On the fixture, the question "consolidated revenue from operations" ranks a page-3 chunk first
- [ ] A search over all real chunks takes under 1 second
- [ ] Tests in `tests/ret/test_tfidf.py`; `uv run pytest` and the smoke run pass

## Learn first
- Why a word that appears in every chunk ("the", "company") gets a low IDF. Work out one IDF by hand.
