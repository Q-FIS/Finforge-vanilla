# [REP-04] Token helpers: count text the way the embedding model does
labels: team:rep, size:S
**Owner:** R2 · **Size:** S (1 day) · **Due:** day 3 · **Needs:** nothing, start now

## What is this, in plain words?
Embedding models don't read words, they read **tokens** (pieces of words), and
they can only read so many: 512 for our models. Anything longer is **silently
cut off**. No error, the end of the text just disappears. So every chunk must
fit, and to check that, the chunkers need to count tokens **exactly the way the
model does**. Counting words or characters is not good enough.

You replace three placeholder functions in `src/rag/rep/tokens.py` with the
real tokenizer.

## Where it fits
Used by the chunkers (REP-05, REP-06, REP-08) and the embedder (REP-11).

## What the three functions must do
```python
count_tokens("Revenue from operations", "BAAI/bge-small-en-v1.5")    # -> 3 (or so)
token_offsets("Revenue grew", "BAAI/bge-small-en-v1.5")              # -> [(0, 7), (8, 12)]
chunk_limit("intfloat/e5-small-v2", "passage: ")                     # -> 512 - 2 - 3 = 507 (or so)
```
`token_offsets` gives the start and end **character positions** of each token in the original text, so `text[0:7] == "Revenue"`.

## Step by step
1. Load the tokenizer: `from transformers import AutoTokenizer`, then `AutoTokenizer.from_pretrained(model)`. Loading is slow, so do it **once per model** and keep it, e.g. with `@functools.lru_cache` on a small `get_tokenizer(model)` function.
2. `count_tokens(text, model)`: `len(tok(text, add_special_tokens=False)["input_ids"])`.
3. `token_offsets(text, model)`: `tok(text, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"]`, turned into a list of tuples.
4. `chunk_limit(model, prefix)`: the model's maximum length, minus 2 (the special tokens the model adds itself, `[CLS]` and `[SEP]`), minus `count_tokens(prefix, model)`.

## Watch out for
- Some tokenizers report a huge `model_max_length` (like 1000000000000000019884624838656) when it isn't set. Use `min(tok.model_max_length, 512)`.
- The first call downloads the tokenizer (a few MB). That's fine; later calls use the downloaded copy.

## How to test it
Create `tests/rep/test_tokens.py`:
- for a few texts (include `"₹1,45,000 crore"` and `"FY 2024-25"`), check that `text[start:end]` for every offset gives back non-empty pieces of the text, in order;
- `count_tokens(text, m) == len(token_offsets(text, m))`;
- `chunk_limit("intfloat/e5-small-v2", "passage: ") < chunk_limit("intfloat/e5-small-v2", "")`.

## Done when
- [ ] The tests pass, and the smoke run still passes
- [ ] The three `STUB(REP-04)` lines are gone

## Learn first
- Run `tok.tokenize("₹1,45,000 crore consolidated")` and look at the pieces. Why are numbers broken into so many tokens? (This is also why embeddings are bad at telling numbers apart, which matters later.)
