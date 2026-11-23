# [RET-03] Check our TF-IDF against scikit-learn
labels: team:ret, size:S
**Owner:** T1 · **Size:** S (1 day) · **Due:** day 8 · **Needs:** RET-02

## In one sentence
Prove our hand-written TF-IDF gives the same numbers as scikit-learn's.

## What to do
1. Use `TfidfVectorizer(tokenizer=tokenize, lowercase=False, token_pattern=None, smooth_idf=True, norm="l2")` with **our** tokenizer, on the same chunks.
2. Compare every chunk's weights with ours.
3. Compare the top 10 results for 20 questions.

## Done when
- [ ] All weights match within 0.000001, and the top 10s are identical (in `tests/ret/test_tfidf_sklearn.py`)
