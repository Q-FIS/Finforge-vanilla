# [GEN-07] generate_answer(): ask, read the answer, retry once
labels: team:gen, size:S
**Owner:** G3 · **Size:** S (1 day) · **Due:** day 9 · **Needs:** GEN-03, GEN-06 (GEN-01 and GEN-05 only for real runs)

## What is this, in plain words?
This puts the generation steps together: build the prompt, ask the model, read
its reply. If the reply is broken, ask **once** more, telling the model what
was wrong. If it's still broken, record an error instead of guessing. We never
silently lose an answer.

## Step by step
In `generate_answer` in `src/rag/gen/generate.py`:
1. Pick the template: if `context.passages` is empty, use `"closed_book_v1"`; otherwise `cfg.template`. Build the messages with `render_messages(...)` (GEN-03).
2. `reply, usage = llm.complete(messages)`, then `answer, error = parse_answer(reply)` (GEN-06).
3. **If it failed,** retry once with the conversation so far plus the fix-up request:
   ```python
   messages += [
       {"role": "assistant", "content": reply},
       {"role": "user", "content": f"Your reply was not valid: {error}. Reply again with JSON only."},
   ]
   ```
   Then call and parse again.
4. **If it failed twice,** return `Answer(status="error", text="", citations=[], raw=reply, usage=usage, error=error)`.
5. Set `usage.prompt_version` to the template name used. If there were two calls, add their tokens together.

## How to test it
`tests/gen/test_generate.py`, using `FakeLLM(replies=[...])`, which returns its replies in order:
- a valid reply → status "answered";
- `["not json", <valid>]` → answered after one retry, and the fake was called twice;
- `["not json", "still not json"]` → status "error", with `raw` and `error` filled;
- an empty context → the closed-book template is used.

## Done when
- [ ] The tests pass, and the smoke run passes
- [ ] The `STUB(GEN-06)` line is gone
