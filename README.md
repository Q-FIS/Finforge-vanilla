# Vanilla RAG from scratch

A question-answering system over Indian companies' annual reports (a "RAG":
retrieval-augmented generation), built by hand by the club in 18 days. Every
step is written by hand first, then checked against a library, so everyone
understands how it really works.

    PDF -> parse -> clean -> chunk -> metadata -> embed -> index
        -> retrieve -> build context -> generate -> check citations -> score

## Setup (once)

```bash
# 1. Install uv: https://docs.astral.sh/uv/getting-started/installation/
git clone <repo-url> && cd rag
uv sync                          # installs Python 3.12 and every dependency
uv run pre-commit install        # formats and lints on every commit
uv run pytest                    # should be all green
uv run python -m rag.run --config tests/ci.yaml --name smoke --overwrite
```

The last command runs the whole pipeline on a small synthetic report with fake
models, and writes `.cache/runs/smoke/`. Open its `results.jsonl` and
`metrics.json`: that's what every real run produces.

## How you work

1. **Read your issue** in `issues/` (or on GitHub). It says what to build,
   which file, and how you know you're done. One issue in progress at a time.
2. **Branch:** `git switch -c rep/REP-01-parser` (team / issue ID / short name).
3. **Find your stub:** `grep -rn "STUB(REP-01)" src/` shows exactly what to replace.
   Don't change a public function's name or arguments: other teams call it.
4. **Test** against the fixtures in `tests/fixtures/`, not against other teams'
   unfinished code. Put your tests in `tests/<your team>/`.
5. **Run** `uv run pytest` and the smoke run. Both must pass.
6. **Open a PR** with `Closes #<issue>` and answer the 5 review questions in
   the template. It merges with green CI + one teammate approval + one fresher
   sign-off.

## Where things are

| Path | What | Owner |
| --- | --- | --- |
| `src/rag/schema.py` | Shared data types (`Document`, `Chunk`, `Hit`, `Answer`, ...) | lead |
| `src/rag/config.py` | Loads `config.yaml`; rejects typos | lead |
| `src/rag/match.py` | "Is this quote in this text?", shared by everyone | lead |
| `src/rag/amounts.py` | "Is this the same number?", shared by everyone | G4 |
| `src/rag/registry.py` | Loads `data/registry.csv` | E1 |
| `src/rag/rep/` | parse, clean, tokens, chunking, metadata, embed | Team 1 (R1-R4) |
| `src/rag/ret/` | tfidf, retrieve, filters, metrics | Team 2 (T1-T4) |
| `src/rag/gen/` | llm, context, generate, citations | Team 3 (G1-G4) |
| `src/rag/run.py`, `score.py`, `failure_trace.py`, `compare.py` | Runs and evaluation | Team 4 (E1-E3), G1 (`score.py`) |
| `config.yaml` | Every setting. Experiments copy it and change one value | |
| `data/registry.csv` | The 6 annual reports (PDFs go in `data/pdfs/`, never in git) | E1 |
| `eval/questions.jsonl` | The evaluation questions | everyone writes, E1 checks |
| `tests/fixtures/` | Synthetic report, its expected output, sample questions | |
| `issues/` | Every task, written out step by step | lead |
| `DECISIONS.md` | Why things are the way they are | lead |

## Rules

- **Settings go in `config.yaml`, not in code.** An unknown key is an error.
- **Contracts** (`schema.py`, `config.py`, `match.py`, `amounts.py`,
  `registry.py`) change only with the lead's review: add fields with defaults,
  never rename or remove.
- **If you can't explain a line, it doesn't merge.** Use AI to explain, review
  and debug your code, not to write code you don't understand.
- **No PDFs, API keys or caches in git.** The pre-commit hook blocks big files;
  keys go in environment variables.
