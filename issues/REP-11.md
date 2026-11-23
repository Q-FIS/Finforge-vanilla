# [REP-11] The real embedding model
labels: team:rep, size:M
**Owner:** R4 · **Size:** M (2-3 days) · **Due:** day 7 · **Needs:** nothing, start now

## In one sentence
Add a real embedder using `sentence-transformers`, with the right prefixes, normalised vectors and a disk cache.

## What to do
In `src/rag/rep/embed.py`:
1. Make a class `SentenceTransformerEmbedder(Embedder)`. Load `SentenceTransformer(cfg.model)` once, and set `model_name` and `dim`.
2. `embed(texts, kind)`: put `cfg.query_prefix` (when kind is "query") or `cfg.passage_prefix` (when kind is "passage") in front of each text. Then call `model.encode(texts, batch_size=cfg.batch_size, normalize_embeddings=True)`. Return float32.
3. **Cache:** before encoding, look for `data/cache/emb/<model name>/<sha1 of prefix+text>.npy`, and only encode texts that are missing. Save new vectors there.
4. **Warn** (with `logging.warning`) when a text is longer than the model's limit (use `count_tokens` from `rep/tokens.py`).
5. In `get_embedder`, return your class when `cfg.fake` is false.

## Done when
- [ ] Every vector has length 1 (within 0.00001)
- [ ] Embedding the same texts a second time loads them all from the cache
- [ ] A text over the limit logs a warning
- [ ] Tests in `tests/rep/test_embed.py` (it's fine for them to download the small model)

## Learn first
- What "normalised" means, and why it makes cosine similarity the same as a dot product.
- Why E5 models need "query: " and "passage: ", and what happens if you forget (no error, just worse results).
