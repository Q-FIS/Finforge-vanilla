# [REP-12] Notebook: build an embedding by hand
labels: team:rep, size:S
**Owner:** R4 · **Size:** S (1 day) · **Due:** day 10 · **Needs:** REP-11

## What is this, in plain words?
`sentence-transformers` turns a sentence into a vector in one line. In this
notebook you open the box and do it step by step, to show exactly what happens
inside, and then prove your result matches the library's.

## Step by step
Create `notebooks/rep/pooling.ipynb`, with a short explanation in a markdown cell before each step:
1. **Tokenize** one sentence (`AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")`) and print the tokens and their ids.
2. **Run the model** (`AutoModel.from_pretrained(...)`) and print the shape of `last_hidden_state`: one 384-number vector **per token**.
3. **Mean pooling:** average the token vectors into one vector. Use the attention mask so padding tokens are ignored:
   `(hidden * mask).sum(1) / mask.sum(1)`
4. **Normalise** it to length 1.
5. **Compare** with `SentenceTransformer("BAAI/bge-small-en-v1.5").encode(sentence, normalize_embeddings=True)` and print the largest difference.
   Note: BGE models are trained with **CLS pooling** (just the first token's vector), so check which one matches. That's the point of the exercise.
6. **CLS vs mean:** compute both and print how different they are.
7. **Cosine equals dot product for unit vectors:** take two normalised vectors and show `cosine(a, b) == a @ b`.

## Done when
- [ ] The notebook runs top to bottom with no errors
- [ ] Your hand-made vector matches sentence-transformers' to within 1e-5, and a markdown cell explains which pooling the model uses and how you found out
