# [GEN-01] The real LLM client, with a cache
labels: team:gen, size:M
**Owner:** G1 · **Size:** M (2-3 days) · **Due:** day 5 · **Needs:** the club API key (ask the lead; never post it in chat or code)

## What is this, in plain words?
This is the code that talks to the language model, Anthropic's
`claude-haiku-5-5`, over the internet. You send it a list of messages; it
sends back text. Every call costs a little money and takes about a second.
We'll run the same questions many times while we experiment, so you also add
a **cache**: the first time we ask something, we save the answer to disk;
asking the exact same thing again returns the saved answer, free and instant.

Right now `get_llm()` only offers `FakeLLM` (used in tests). You add the real one.

## Where it fits
generate_answer() (GEN-07) → **llm.complete(messages) (you)** → `(reply text, Usage)`

## What you must give back
```python
llm = get_llm(LLMConfig())          # real client when fake is False
reply, usage = llm.complete([
    {"role": "system", "content": "Answer in one word."},
    {"role": "user", "content": "What is the capital of France?"},
])
reply    # "Paris"
usage    # Usage(model="claude-haiku-5-5", prompt_version="", tokens_in=21, tokens_out=4,
         #       latency_ms=812.3, cached=False)
```

## Step by step
1. **Install the SDK:** `uv add anthropic` (this changes `pyproject.toml` and `uv.lock`; the lead reviews it).
2. In `src/rag/gen/llm.py`, make `class AnthropicLLM(LLM)`. In `__init__(self, cfg, client=None)`:
   - `self.client = client or anthropic.Anthropic(timeout=cfg.timeout_s, max_retries=1)`
   - The SDK reads the key from the `ANTHROPIC_API_KEY` environment variable by itself. **Never** put the key in code, config or logs.
   - `max_retries=1` makes the SDK retry once by itself on timeouts, rate limits (429) and server errors (5xx). You don't write retry code.
   - The `client=` parameter lets tests pass in a fake client (see "How to test it").
3. In `complete(self, messages)`:
   - The API wants the system message **separately**: take the content of messages with role `"system"` as `system`, and pass the rest as `messages`.
   - Call:
     ```python
     response = self.client.messages.create(
         model=self.cfg.model,
         max_tokens=self.cfg.max_tokens,
         system=system_text,
         messages=other_messages,
         output_config={"effort": self.cfg.effort},
     )
     ```
   - **Do not send `temperature`.** This model returns an error if you do. (That's why the config has `effort` instead.)
   - The model "thinks" before answering, and `response.content` can contain thinking blocks as well as text. Keep only the text: `"".join(b.text for b in response.content if b.type == "text")`.
   - If `response.stop_reason == "max_tokens"`, the answer was cut off: `logging.warning(...)`.
   - Make the `Usage`: `tokens_in=response.usage.input_tokens`, `tokens_out=response.usage.output_tokens`, `latency_ms` measured with `time.perf_counter()`, `cached=False`.
4. **The cache:**
   - key = `hashlib.sha256(json.dumps({"model": ..., "effort": ..., "max_tokens": ..., "messages": messages}, sort_keys=True).encode()).hexdigest()`
   - Before calling the API, if `data/cache/llm/<key>.json` exists, load the reply and usage from it and return them with `cached=True`.
   - After a real call, save `{"reply": ..., "usage": {...}}` to that file.
   - If `self.cfg.cache` is False, skip the cache completely (experiment E0 needs this).
5. **Errors:** let `anthropic.APIStatusError` and `anthropic.APIConnectionError` reach the caller after the SDK's retry. Don't hide them.
6. In `get_llm(cfg)`: `return AnthropicLLM(cfg)` when `cfg.fake` is False.

## Watch out for
- **The cache key must include everything that changes the answer** (model, effort, max_tokens, every word of every message). Otherwise you get stale answers after changing the prompt.
- Tests must **never** call the real API: it costs money, and CI has no key.
- `data/cache/` is ignored by git. Never commit it.

## How to test it
`tests/gen/test_llm.py`. Make a tiny fake client that records calls and returns an object shaped like the SDK's response:
```python
from types import SimpleNamespace as NS

class FakeClient:
    def __init__(self):
        self.calls = 0
        self.messages = self            # so self.client.messages.create(...) works
    def create(self, **kwargs):
        self.calls += 1
        return NS(content=[NS(type="text", text="Paris")], stop_reason="end_turn",
                  usage=NS(input_tokens=21, output_tokens=4))
```
Test: the reply and usage come back right; calling twice with the same messages → `FakeClient.calls == 1` and the second has `cached=True`; with `cache=False` → 2 calls; the system message goes into `system=`, not `messages=`; `temperature` is **not** among the arguments passed to `create`. Use pytest's `tmp_path` and `monkeypatch.chdir(tmp_path)` so the cache doesn't touch the real `data/cache/`.

## Done when
- [ ] The tests pass, with no real API calls
- [ ] One real call made by hand (`uv run python -c "..."`) is pasted into your PR: the prompt, the reply and the usage
- [ ] `grep -rn "sk-ant" .` finds nothing
- [ ] The `STUB(GEN-01)` line is gone

## Learn first
- Input tokens vs output tokens: which costs more, and why does our prompt's size matter?
- Why is a cache safe here? When would a cached answer be wrong?
