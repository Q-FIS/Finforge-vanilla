# [RET-14] Experiment E4: keyword search (TF-IDF) vs embeddings
labels: team:ret, size:S
**Owner:** T1 · **Size:** S (1 day) · **Due:** day 15 · **Needs:** EVAL-05, RET-02

## What is this, in plain words?
Is the embedding search actually better than old-fashioned keyword search?
And for which kinds of questions? Embeddings understand meaning, but they're
bad at exact numbers and names, which is exactly where keyword search shines.

## Step by step
1. Two runs, identical except `retrieve.method`: `tfidf` and `dense`. Name them `e4_tfidf` and `e4_dense`.
2. From each `metrics.json`, take hit@5 and recall@5 for each category (`by_category`).
3. Pick 3 questions where TF-IDF wins and 3 where dense wins. Open their `results.jsonl` lines and look at what each method retrieved.
4. Write `eval/reports/E4_tfidf_vs_dense.md`: the table per category, the 6 examples, and your explanation of the pattern.

## Done when
- [ ] The two run folders and the report are committed
