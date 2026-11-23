# [REP-15] Experiment E1: which chunker and chunk size?
labels: team:rep, size:M
**Owner:** R2 (with R3) · **Size:** M (2-3 days) · **Due:** day 15 · **Needs:** EVAL-05 (runs work), RET-11 (metrics)

## In one sentence
Run the pipeline with 5 chunking settings and decide which one we keep, based on numbers.

## What to do
1. Make 5 config files in `eval/configs/` (copy `config.yaml`, change only the chunk settings):
   fixed 256 tokens no overlap · fixed 256 overlap 50 · fixed 512 overlap 50 · sentence 512 · section 512
2. Run each: `uv run python -m rag.run --config eval/configs/<file> --name e1_<name>`.
3. For each run, record: number of chunks · average and largest tokens · % of chunks over the limit · % of evidence fully inside one chunk (`rag.match.fully_contains`) · recall@5.
4. Write `eval/reports/E1_chunking.md`: the table, the setting we choose, and why. A difference smaller than the noise floor (E0) counts as "no real difference".

## Done when
- [ ] The 5 run folders and the report are committed
