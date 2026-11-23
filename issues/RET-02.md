# [RET-02] TF-IDF search, written by hand
labels: team:ret, size:M
**Owner:** T1 · **Size:** M (2-3 days) · **Due:** day 7 · **Needs:** RET-01

## What is this, in plain words?
TF-IDF is the classic keyword search, from long before neural networks. Each
chunk gets a score for each word:
- **TF** (term frequency): how many times the word appears in the chunk;
- **IDF** (inverse document frequency): how *rare* the word is across all chunks. "the" is in every chunk, so it's worth almost nothing; "debenture" is in 3, so it's worth a lot.

A chunk's vector = TF × IDF for each of its words. A question becomes a vector
the same way, and the best chunks are the ones whose vectors point the most in
the same direction (cosine similarity). It's our **baseline**: the embedding
search must beat it to be worth using, and for some questions (exact figures,
names) it often wins.

## Where it fits
chunks → **TfidfIndex.build() (you)** → index; question → **index.search() (you)** → `list[Hit]`
Used when `retrieve.method: tfidf` (see RET-07, and experiment E4 in RET-14).

## The maths, with N = number of chunks
```
df(word)      = number of chunks containing the word
idf(word)     = log((N + 1) / (df(word) + 1)) + 1          (scikit-learn's formula)
weight(w, c)  = count of w in chunk c  ×  idf(w)
then divide each chunk's weights by the vector's length:  sqrt(sum of weight²)
score(question, chunk) = sum over shared words of  q_weight × c_weight
```

## Step by step
In `TfidfIndex` in `src/rag/ret/tfidf.py`:
1. **`build(chunks)`:**
   - tokenize every chunk's text with your `tokenize` (RET-01);
   - count `df` for every word: use a `collections.Counter` and add `set(tokens)` for each chunk;
   - compute `idf` for every word;
   - build each chunk's vector as a dict `{word: weight}`, then normalise it to length 1;
   - store `self.idf` and `self.vectors` (one dict per chunk, in the same order as `self.chunks`).
2. **`search(query, k, allowed=None)`:**
   - tokenize the query, build its vector the same way, using the **stored** idf (ignore words the index has never seen), and normalise;
   - score each chunk by the sum over shared words of `q[w] * chunk[w]`;
   - skip chunks where `allowed` is given and `allowed[i]` is False;
   - sort by score, highest first, and return the top `k` as `Hit(chunk, score, rank, "tfidf")`, with rank 1 = best.
3. **Make it fast (second step):** build an **inverted index**, `{word: [chunk numbers that contain it]}`. At search time, only score chunks that share at least one word with the query. With 15,000 chunks this is the difference between slow and instant.

## How to test it
`tests/ret/test_tfidf.py`:
- a tiny hand-made example (3 chunks, a few words) where you compute the scores **on paper** first, and check the code matches;
- a word in every chunk has the lowest idf;
- `allowed` hides the chunks marked False;
- on the fixture (one chunk per page with the stub chunker), write 3 questions where you can predict the best chunk, e.g. "standalone profit for the year" → page 4, "exports Europe Red Sea" → page 2, and check they come first.

## Done when
- [ ] The tests pass
- [ ] One search over all real chunks takes under 1 second
- [ ] `uv run pytest` and the smoke run (with `retrieve: {method: tfidf}`) pass

## Learn first
- Compute the idf of "the" and of "debenture" by hand, for 100 chunks where "the" is in all 100 and "debenture" is in 2.
- Introduction to Information Retrieval, chapter 6 (free online).
