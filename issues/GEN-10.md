# [GEN-10] Does the model refuse when it should?
labels: team:gen, size:S
**Owner:** G3 · **Size:** S (1 day) · **Due:** day 11 · **Needs:** GEN-07, GEN-01

## In one sentence
Give the real model 10 questions it **can't** answer from the passages, and check it says "insufficient_evidence".

## What to do
1. Write 10 questions whose answer isn't in the passages you give, but the passages look related (for example, ask about FY2026 with FY2025 passages).
2. Run them with the real model and count how many are refused correctly.
3. If too few, improve the prompt in a **new** file, `grounded_v2.txt` (keep v1), and run again.
4. Write `eval/reports/abstention.md` with the before and after numbers.

## Done when
- [ ] The report is committed
