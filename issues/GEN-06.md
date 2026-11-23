# [GEN-06] Read the model's JSON reply safely
labels: team:gen, size:M
**Owner:** G3 · **Size:** M (2-3 days) · **Due:** day 7 · **Needs:** nothing

## What is this, in plain words?
We ask the model to reply in JSON, but models don't always obey. They add
"Here is the answer:" in front, wrap it in ```` ```json ```` fences, use the
wrong field names, or stop halfway. You write the function that turns the reply
into an `Answer`, or explains **exactly** what's wrong, so GEN-07 can ask the
model to fix it.

## What it must do
```python
parse_answer('{"status": "answered", "answer": "₹16,900 crore [C1]", "citations": [{"tag": "C1", "quote": "Profit for the year 16,900"}]}')
# -> (Answer(status="answered", text="₹16,900 crore [C1]", citations=[Citation("C1", "Profit for the year 16,900")], raw=...), "")

parse_answer('Sure! ```json\n{"status": "answered", ...}\n```')
# -> works too: the fences and the extra text are removed

parse_answer('{"status": "maybe", "answer": "", "citations": []}')
# -> (None, "status must be 'answered' or 'insufficient_evidence', got 'maybe'")
```

## Step by step
In `src/rag/gen/generate.py`, write `parse_answer(reply: str) -> tuple[Answer | None, str]`:
1. If the reply is empty, return `(None, "the reply was empty")`.
2. Remove code fences: drop lines that start with ```` ``` ````.
3. Find the JSON: from the first `{` to the last `}`. If there's none, return an error.
4. `json.loads` it. On failure, return the error message (`str(e)`).
5. Check each field, returning a clear message for the first problem:
   - `status` is `"answered"` or `"insufficient_evidence"`;
   - `answer` is a string (it may be empty when refusing);
   - `citations` is a list, and each item has a `tag` like `"C1"` (check with `re.fullmatch(r"C\d+", tag)`) and a `quote` string.
6. Return `(Answer(status, text=answer, citations=[...], raw=reply), "")`.

## How to test it
`tests/gen/test_parse_answer.py`, with at least 15 replies: a perfect reply; extra text before and after; code fences; single quotes instead of double (should fail clearly); a missing field; an unknown status; citations that aren't a list; a tag like "1" instead of "C1"; a reply cut off halfway; an empty string. You can produce replies with `FakeLLM(replies=[...])`, or just test `parse_answer` directly.

## Done when
- [ ] At least 15 tests pass
- [ ] Every error message says exactly what's wrong (the model will read it in GEN-07)
