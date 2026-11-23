# [GEN-12] Experiment E8: does a passage's position in the prompt matter?
labels: team:gen, size:M
**Owner:** G2 · **Size:** M (2-3 days) · **Due:** day 15 · **Needs:** GEN-05, EVAL-09

## What to do
1. Finish `order: gold_at:<n>` in `build_context`: put the true-evidence passage at position n among 9 other (wrong) passages.
2. For 30 questions, run with the evidence first (position 1), in the middle (5) and last (10).
3. Write `eval/reports/E8_position.md`: accuracy by position, compared with the noise floor.

## Done when
- [ ] The run folders and the report are committed
