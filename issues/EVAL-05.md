# [EVAL-05] Make runs fast with caching, then do the first real run
labels: team:eval, size:M
**Owner:** E2 · **Size:** M (2-3 days) · **Due:** day 10 · **Needs:** nothing to start; the real pipeline steps for the first real run

## What is this, in plain words?
`run.py` already runs the whole pipeline. But parsing 6 big PDFs, chunking
them and embedding 15,000 chunks takes minutes, and we'll do dozens of runs,
most of them changing only one later setting (say, the number of passages).
You make `run.py` **save** the slow results and **reuse** them when the
settings they depend on haven't changed.

Then, when the real pieces are merged (aim for day 10), you do the **first real
run** of the whole system. That's the project's biggest milestone.

## How the cache knows what changed
`stage_hash(cfg, ...)` in `src/rag/config.py` makes a short code from only the settings you name. Same settings → same code → reuse the saved file.
```python
stage_hash(cfg, "corpus", "parse", "clean")                       # e.g. "a91c03f2b7d1"
stage_hash(cfg, "corpus", "parse", "clean", "chunk", "embed.model")
```
If you change `chunk.max_tokens`, the second code changes but the first doesn't: chunking runs again, parsing doesn't.

## Step by step
In `run_pipeline()` in `src/rag/run.py`:
1. **Documents:** `docs_key = stage_hash(cfg, "corpus", "parse", "clean")`. If `data/cache/docs/<docs_key>.jsonl` exists, load it (`load_jsonl(path, Document)`); otherwise parse and clean, then save it (`save_jsonl`).
2. **Chunks:** `chunks_key = stage_hash(cfg, "corpus", "parse", "clean", "chunk", "embed.model")`. Same idea, with `data/cache/chunks/<chunks_key>.jsonl` and `Chunk`. (Metadata is part of chunking here, so include it before saving.)
3. **Embeddings** are already cached text by text (REP-11). Nothing to do.
4. **Print** what was reused, e.g. `docs: from cache (a91c03f2b7d1)`, so people can see it working.
5. Delete the `STUB(EVAL-05)` note in the file's docstring.
6. **The first real run:** once REP-01/02, a chunker, REP-11, RET-04 and GEN-01/05/07 are merged and the questions exist:
   `uv run python -m rag.run --config config.yaml --name baseline`
   Commit the run folder, and post the overall scores in the team channel.

## Watch out for
- The registry is part of "corpus" only by its path. If someone adds a PDF but the path is the same, the cache won't notice. Add the registry file's sha256 to the key (hash it yourself and combine the two).

## How to test it
`tests/test_run_cache.py` with `tests/ci.yaml` (in a `tmp_path`, as `tests/test_skeleton.py` does):
- run twice: the second run reuses both caches (check the files' modification times, or count calls to `parse_pdf` with `monkeypatch`), and `metrics.json` is identical;
- change only `chunk.max_tokens`: chunks are rebuilt, documents are not.

## Done when
- [ ] The tests pass
- [ ] `eval/runs/baseline/` is committed, by day 10 if the pieces are ready
