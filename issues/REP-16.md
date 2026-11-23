# [REP-16] Experiments E2 and E3: header line, model, prefix
labels: team:rep, size:M
**Owner:** R4 · **Size:** M (2-3 days) · **Due:** day 15 · **Needs:** EVAL-05, RET-11

## In one sentence
Measure whether the header line helps, which embedding model is better, and what forgetting the E5 prefix costs.

## What to do
1. **E2:** run the baseline with `chunk.prepend_header` false and true.
2. **E3:** run with `embed.model: BAAI/bge-small-en-v1.5`, then `intfloat/e5-small-v2` with the prefixes `"query: "` and `"passage: "`, then e5 again **without** the prefixes.
3. Compare recall@5 overall, and for the "period_entity_trap" and "statement_basis" question categories.
4. Write `eval/reports/E2_E3_embeddings.md`: the tables, what we choose, and why.

## Done when
- [ ] The run folders and the report are committed
- [ ] The report says clearly what forgetting the prefix did, since nothing gives an error
