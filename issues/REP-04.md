# [REP-04] Token helpers: count tokens like the embedding model does
labels: team:rep, size:S
**Owner:** R2 · **Size:** S (1 day) · **Due:** day 3 · **Needs:** nothing, start now

## In one sentence
Replace the word-counting stubs in `src/rag/rep/tokens.py` with the embedding model's real tokenizer.

## Why it matters
Embedding models cut off text after a fixed number of tokens (512 for our models) **without any warning**. Chunkers use these functions to make sure every chunk fits.

## What to do
1. Load the tokenizer with `transformers.AutoTokenizer.from_pretrained(model)`. Load it once per model and keep it (a dict, or `functools.lru_cache`).
2. `count_tokens(text, model)`: the number of tokens **without** special tokens (`add_special_tokens=False`).
3. `token_offsets(text, model)`: call the tokenizer with `return_offsets_mapping=True, add_special_tokens=False`. It gives the (start, end) character positions of each token.
4. `chunk_limit(model, prefix)`: `tokenizer.model_max_length`, minus 2 (the special tokens `[CLS]` and `[SEP]`), minus `count_tokens(prefix, model)`.

## Done when
- [ ] For a few texts, `text[start:end]` for every offset gives exactly the token's piece of text
- [ ] `chunk_limit("intfloat/e5-small-v2", "passage: ")` is smaller than `chunk_limit("intfloat/e5-small-v2", "")`
- [ ] Tests in `tests/rep/test_tokens.py` (they may download the tokenizer once, which is small)
- [ ] `uv run pytest` and the smoke run pass

## Learn first
- Tokenize "₹1,45,000 crore" and "consolidated" and look at the pieces. Why are numbers split up so much?
