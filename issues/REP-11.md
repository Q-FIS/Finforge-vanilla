# [REP-11] The real embedding model
labels: team:rep, size:M
**Owner:** R4 · **Size:** M (2-3 days) · **Due:** day 7 · **Needs:** nothing, start now

## What is this, in plain words?
To search by **meaning** rather than by exact words, we turn every chunk (and
later every question) into a **vector**: a list of 384 numbers produced by a
small neural network, the "embedding model". Texts with similar meanings get
similar vectors, so "How much did Acme earn?" can find a chunk that says
"Profit for the year".

Right now `get_embedder()` only offers `FakeEmbedder` (used in tests). You add
the real one, using the `sentence-transformers` library and our default model
`BAAI/bge-small-en-v1.5`.

## Where it fits
chunks → **embedder.embed(texts, "passage") (you)** → vectors → DenseIndex (RET-04)
question → **embedder.embed([question], "query") (you)** → one vector → search

## What you must give back
```python
embedder = get_embedder(EmbedConfig())        # real model when fake is False
vectors = embedder.embed(["Profit for the year 16,900", "Exports fell 4%"], "passage")
vectors.shape   # (2, 384)
vectors.dtype   # float32
# every row has length 1:  np.linalg.norm(vectors, axis=1) -> [1.0, 1.0]
```

## Step by step
In `src/rag/rep/embed.py`:
1. Make a class `SentenceTransformerEmbedder(Embedder)`. In `__init__(self, cfg)`: load `SentenceTransformer(cfg.model)` once, and set `self.model_name = cfg.model` and `self.dim = model.get_sentence_embedding_dimension()`.
2. In `embed(self, texts, kind)`:
   - choose the prefix: `cfg.query_prefix` if `kind == "query"`, else `cfg.passage_prefix`, and put it in front of each text;
   - call `self.model.encode(prefixed_texts, batch_size=cfg.batch_size, normalize_embeddings=True)`;
   - return it as `np.float32`.
3. **Cache, so we never embed the same text twice:** before encoding, compute for each text `key = sha1((prefix + text).encode()).hexdigest()` and look for `data/cache/emb/<model name with "/" replaced by "_">/<key>.npy`. Only encode the texts that are missing, save each new vector with `np.save`, then return all of them in the original order.
4. **Warn about text that's too long:** if `count_tokens(prefix + text, cfg.model)` is more than `chunk_limit(cfg.model)`, call `logging.warning(...)` with the first 60 characters. The model will silently cut it, so we must at least say so.
5. In `get_embedder(cfg)`: `return SentenceTransformerEmbedder(cfg)` when `cfg.fake` is False.

## Watch out for
- **E5 models need prefixes.** `intfloat/e5-small-v2` expects `"query: "` before questions and `"passage: "` before chunks. Without them, it gives **worse results with no error**. That's experiment E3 (REP-16).
- The first run downloads the model (about 130 MB). Tests that use it are slow, so keep them few.
- `data/cache/` is ignored by git. Never commit it.

## How to test it
`tests/rep/test_embed.py`:
- shape is `(n, 384)`, dtype float32, every row has length 1 (within 1e-5);
- embedding the same texts twice: the second time, nothing is encoded (count the calls with a small wrapper, or check the cache files exist first);
- a very long text logs a warning (use pytest's `caplog` fixture);
- `"revenue grew"` is closer to `"revenue increased"` than to `"monsoon outlook"` (dot products).

## Done when
- [ ] The tests pass
- [ ] `uv run python -m rag.run --config config.yaml` with `embed.fake: false` gets past the embedding step on the fixture
- [ ] The `STUB(REP-11)` line is gone

## Learn first
- What does "normalised" mean for a vector, and why does it make cosine similarity the same as a dot product?
- Why might "FY2024 revenue" and "FY2025 revenue" get almost the same vector? (This is why we need metadata filters.)
