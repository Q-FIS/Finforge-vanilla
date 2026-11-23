# [GEN-05] Context builder with a real token budget
labels: team:gen, size:M
**Owner:** G2 · **Size:** M (2-3 days) · **Due:** day 8 · **Needs:** GEN-04 (use `estimate_llm_tokens` until then)

## In one sentence
Put the best passages into the prompt, tagged [C1], [C2], ..., until the token budget is full, and record the ones left out.

## What to do
In `build_context(hits, cfg)` in `src/rag/gen/context.py`:
1. Format each passage as:
   `[C1] Acme Industries Limited · FY2025 · consolidated · Consolidated Statement of Profit and Loss · p. 3`
   then the chunk text on the next lines.
2. Add passages best first. Before adding one, count its tokens. If it would go over `cfg.max_tokens`, **don't add it**: put `(chunk_id, "budget")` in `dropped` and try the next one.
3. Only the very first passage may be shortened, and only if it alone is over the budget. Then set `truncated=True`.
4. Tags are numbered by position in the prompt: C1, C2, C3, with no gaps.
5. `cfg.order`: "rank" keeps the order. "gold_at:<n>" is used by experiment E8 to move a passage to position n (you can leave this until GEN-12).

## Done when
- [ ] Tests: the budget is never exceeded; dropped passages are recorded; tags have no gaps; the source line shows company, year, basis, section and page (in `tests/gen/test_context.py`)
- [ ] `uv run pytest` and the smoke run pass

## Learn first
- "Lost in the Middle" (Liu et al., 2024): models use the start and end of a long prompt better than the middle.
