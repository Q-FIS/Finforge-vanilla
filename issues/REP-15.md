# [REP-15] Experiment E1: which chunker and which size?
labels: team:rep, size:M
**Owner:** R2 (with R3) · **Size:** M (2-3 days) · **Due:** day 15 · **Needs:** EVAL-05 (real runs work), RET-11 (scores)

## What is this, in plain words?
We have three chunkers and many possible sizes. Instead of guessing, you run
the whole system with 5 different settings on our dev questions, and pick the
winner **based on numbers**.

## Step by step
1. Make 5 config files in `eval/configs/`. Copy `config.yaml` and change only the `chunk:` section:
   - `e1_fixed_256_0.yaml`: strategy fixed, max_tokens 256, overlap_tokens 0
   - `e1_fixed_256_50.yaml`: fixed, 256, 50
   - `e1_fixed_512_50.yaml`: fixed, 512, 50
   - `e1_sentence_512.yaml`: sentence, 512, overlap_sentences 1
   - `e1_section_512.yaml`: section, 512
2. Run each: `uv run python -m rag.run --config eval/configs/e1_fixed_256_0.yaml --name e1_fixed_256_0`.
3. For each run, record:
   - number of chunks, average and largest `n_tokens`, % of chunks over the model's limit
   - **containment:** % of evidence quotes that sit **entirely inside one chunk** (`rag.match.fully_contains`)
   - recall@5 (from `metrics.json`)
4. Write `eval/reports/E1_chunking.md`: the table, the setting you choose, and why. A difference smaller than the noise floor (`eval/noise.json`, from EVAL-10) counts as "no real difference".

## Done when
- [ ] The 5 run folders and the report are committed
- [ ] If you choose a new default, change `config.yaml` in the same PR
