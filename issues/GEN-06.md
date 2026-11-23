# [GEN-06] Read the model's JSON reply safely
labels: team:gen, size:M
**Owner:** G3 · **Size:** M (2-3 days) · **Due:** day 7 · **Needs:** nothing

## In one sentence
Turn the model's reply into an `Answer`, and give a clear error when the reply isn't the JSON we asked for.

## What to do
1. In `src/rag/gen/generate.py`, write `parse_answer(reply) -> tuple[Answer | None, str]`. It returns the `Answer`, or None and an error message.
2. Models often add extra text, so: remove ```` ```json ```` fences, and find the first `{ ... }` in the reply.
3. Check: `status` is one of "answered", "insufficient_evidence"; `answer` is text; `citations` is a list of `{"tag": "C<number>", "quote": text}`.
4. When something is wrong, return a short error saying exactly what. It gets sent back to the model in GEN-07.

## Done when
- [ ] At least 15 tests with broken replies, in `tests/gen/test_parse_answer.py`: extra text before or after, code fences, single quotes, a missing field, an unknown status, an empty reply, citations that aren't a list...
- [ ] Use `FakeLLM(replies=[...])` to produce replies in tests
