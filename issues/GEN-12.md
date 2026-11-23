# [GEN-12] Experiment E8: does a passage's position in the prompt matter?
labels: team:gen, size:M
**Owner:** G2 · **Size:** M (2-3 days) · **Due:** day 15 · **Needs:** GEN-05, EVAL-09

## What is this, in plain words?
Research ("Lost in the Middle") found that models pay more attention to the
start and end of a long prompt than to the middle. Does that happen with our
model and our documents? You put the right passage first, in the middle, or
last among 9 wrong ones, and measure accuracy for each position.

## Step by step
1. Finish `order: "gold_at:<n>"` in `build_context` (GEN-05): take the true-evidence passage (from oracle mode, EVAL-09) and 9 other retrieved passages, and place the true one at position n.
2. For 30 answerable dev questions, run with `gold_at:1`, `gold_at:5` and `gold_at:10`.
3. Write `eval/reports/E8_position.md`: accuracy by position, compared with the noise floor, and 2 examples where position changed the answer.

## Done when
- [ ] The run folders and the report are committed
