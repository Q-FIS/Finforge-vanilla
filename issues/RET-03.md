# [RET-03] Check our TF-IDF against scikit-learn
labels: team:ret, size:S
**Owner:** T1 · **Size:** S (1 day) · **Due:** day 8 · **Needs:** RET-02

## What is this, in plain words?
We wrote TF-IDF by hand to understand it. Now we prove it's **correct** by
checking it gives exactly the same numbers as scikit-learn, a library millions
of people use.

## Step by step
1. In `tests/ret/test_tfidf_sklearn.py`, create
   `TfidfVectorizer(tokenizer=tokenize, lowercase=False, token_pattern=None, smooth_idf=True, norm="l2")`.
   Using **our** tokenizer means both sides see the same words.
2. `matrix = vectorizer.fit_transform([c.text for c in chunks])`.
3. For each chunk and each word, compare our weight with `matrix[chunk_number, vectorizer.vocabulary_[word]]`.
4. For 20 questions, compare our top 10 with scikit-learn's top 10 (`vectorizer.transform([question])`, then multiply by the matrix).

## Watch out for
- If they don't match, the usual cause is the idf formula (the `+ 1`s) or normalising at the wrong moment. Print one word's numbers from both sides and compare.

## Done when
- [ ] All weights match to within 0.000001, and the top 10s are identical
