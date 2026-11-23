# [REP-16] Experiments E2 and E3: header line, model, and the prefix trap
labels: team:rep, size:M
**Owner:** R4 · **Size:** M (2-3 days) · **Due:** day 15 · **Needs:** EVAL-05, RET-11

## What is this, in plain words?
Three questions, answered with numbers:
- **E2:** does putting "Company · FY · basis · section" in front of each chunk before embedding help retrieval find the right year and statement?
- **E3:** which of our two embedding models is better on *our* questions?
- **E3:** what happens if you forget E5's `"query: "` / `"passage: "` prefixes? (There's no error; we expect worse results.)

## Step by step
1. **E2:** two runs of the baseline: `chunk.prepend_header: false` and `true`.
2. **E3:** three runs: `embed.model: BAAI/bge-small-en-v1.5`; `intfloat/e5-small-v2` with `query_prefix: "query: "` and `passage_prefix: "passage: "`; and e5 again with both prefixes `""`.
3. Compare recall@5 and hit@5, overall and for the `period_entity_trap` and `statement_basis` categories (they're in `metrics.json` under `by_category`).
4. Write `eval/reports/E2_E3_embeddings.md`: the tables, what we choose, and why.

## Done when
- [ ] The run folders and the report are committed
- [ ] The report says clearly what forgetting the prefix did
