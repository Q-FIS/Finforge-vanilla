# [REP-12] Notebook: build an embedding by hand
labels: team:rep, size:S
**Owner:** R4 · **Size:** S (1 day) · **Due:** day 10 · **Needs:** REP-11

## In one sentence
In a notebook, make a sentence embedding step by step and show it matches what sentence-transformers gives.

## What to do
Create `notebooks/rep/pooling.ipynb`:
1. Tokenize one sentence with `AutoTokenizer`, run it through `AutoModel`, and look at the output shape (one vector per token).
2. **Mean pooling:** average the token vectors, ignoring padding (use the attention mask). Then normalise to length 1.
3. Compare with `SentenceTransformer(model).encode(sentence, normalize_embeddings=True)`. The biggest difference should be under 0.00001.
4. Also try **CLS pooling** (just the first token's vector) and show how different it is.
5. Take two unit vectors and show that cosine similarity equals the dot product.

## Done when
- [ ] The notebook runs top to bottom without errors, and the comparison passes
