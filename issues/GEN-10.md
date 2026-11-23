# [GEN-10] Does the model say "I don't know" when it should?
labels: team:gen, size:S
**Owner:** G3 · **Size:** S (1 day) · **Due:** day 11 · **Needs:** GEN-07, GEN-01

## What is this, in plain words?
A good system admits when the documents don't contain the answer, instead of
guessing. You test that with the real model: give it questions it **can't**
answer from the passages provided, and count how often it correctly replies
`insufficient_evidence`.

## Step by step
1. Write 10 questions whose answer is **not** in the passages you'll give, but where the passages look related. Examples: ask for FY2026 figures with FY2025 passages; ask for a subsidiary's figure with only the parent's passages; ask about something the report never mentions (R&D spend).
2. For each, pick 3 to 5 related chunks, and run `build_context` + `generate_answer` with the real model.
3. Count the correct refusals.
4. If fewer than 8 out of 10 are refused, improve the prompt in a **new** file, `prompts/grounded_v2.txt` (keep v1 unchanged so results stay comparable), and run again.
5. Write `eval/reports/abstention.md`: the 10 questions, what the model said before and after, and the prompt change you made.

## Done when
- [ ] The report is committed (and `grounded_v2.txt`, if you made one)
