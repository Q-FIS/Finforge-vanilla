# [GEN-11] Experiment E7: where do we lose accuracy?
labels: team:gen, size:M
**Owner:** G3 · **Size:** M (2-3 days) · **Due:** day 15 · **Needs:** EVAL-05, EVAL-09

## What is this, in plain words?
When an answer is wrong, is it because retrieval didn't find the right passage,
or because the model misread a passage it had? Three runs tell them apart:

| Run | What the model gets | What it tells us |
| --- | --- | --- |
| closed-book (`retrieve.method: none`) | no passages | what the model "knows" alone |
| our system (`dense`) | our retrieved passages | our real result |
| oracle (`oracle`) | the true evidence passages | the best possible result with perfect retrieval |

**Oracle minus our system** = how much accuracy retrieval costs us.
**100% minus oracle** = how much the model loses even with perfect evidence.

## Step by step
1. Three runs, identical except `retrieve.method`: `e7_closed_book`, `e7_dense`, `e7_oracle`.
2. From each `metrics.json`: `answer_accuracy` and `status_accuracy`, overall and per category.
3. Write `eval/reports/E7_where_we_lose.md`: the table, the two differences above, and which categories lose most at each stage. A difference smaller than the noise floor (`eval/noise.json`) is "no real difference".

## Done when
- [ ] The three run folders and the report are committed
