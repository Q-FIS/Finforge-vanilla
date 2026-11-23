# [EVAL-05] Make runs fast with caching, then do the first real run
labels: team:eval, size:M
**Owner:** E2 · **Size:** M (2-3 days) · **Due:** day 10 · **Needs:** nothing to start; the real stages for the first real run

## In one sentence
Save the slow steps (parsing, chunking, embedding) to disk, so a second run with the same settings skips them.

## What to do
In `src/rag/run.py` (the `STUB(EVAL-05)` note at the top):
1. After parsing and cleaning, save the documents to `data/cache/docs/<key>.jsonl`, where `key = stage_hash(cfg, "corpus", "parse", "clean")`. Next time, if that file exists, load it instead of parsing.
2. Do the same for chunks: `data/cache/chunks/<key>.jsonl` with `stage_hash(cfg, "corpus", "parse", "clean", "chunk", "embed.model")`.
3. Embeddings are already cached by REP-11.
4. Print which steps came from the cache, so people can see it working.
5. When the real stages are merged (aim for day 10), run the **first real baseline** on the dev questions: `uv run python -m rag.run --config config.yaml --name baseline`.

## Done when
- [ ] Running the same config twice: the second run uses the cache and gives exactly the same `metrics.json`
- [ ] Changing only `chunk.max_tokens` re-chunks but does **not** re-parse
- [ ] The first baseline run folder is committed

## Learn first
- Read `stage_hash` in `src/rag/config.py`: why does the chunk key include `embed.model`?
