# [GEN-07] generate_answer(): ask, read the answer, retry once
labels: team:gen, size:S
**Owner:** G3 · **Size:** S (1 day) · **Due:** day 9 · **Needs:** GEN-03, GEN-06 (GEN-01 and GEN-05 only for real runs)

## In one sentence
Finish `generate_answer()`: real prompt, call the model, parse the answer, and retry once if the reply is broken.

## What to do
In `src/rag/gen/generate.py`:
1. Build the messages with `render_messages` (GEN-03). Use the closed-book template when the context has no passages.
2. Call `llm.complete(messages)` and `parse_answer(reply)` (GEN-06).
3. If parsing fails: call the model **once more**, adding the bad reply and a message like "Your reply was not valid: <error>. Reply with JSON only."
4. If it fails again: return `Answer(status="error", raw=<the reply>, error=<message>)`. **Never** drop an answer silently.
5. Set `usage.prompt_version` to the template name.

## Done when
- [ ] Tests with `FakeLLM(replies=[...])`: valid at once; broken then valid; broken twice (in `tests/gen/test_generate.py`)
- [ ] `uv run pytest` and the smoke run pass
