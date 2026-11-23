# [GEN-01] The real LLM client, with a cache
labels: team:gen, size:M
**Owner:** G1 · **Size:** M (2-3 days) · **Due:** day 5 · **Needs:** the club API key (from the lead)

## In one sentence
Make `get_llm()` return a real client for Anthropic's `claude-haiku-5-5`, which saves every answer so the same call never costs twice.

## What to do
In `src/rag/gen/llm.py`:
1. Make a class `AnthropicLLM(LLM)` using the `anthropic` Python package (add it with `uv add anthropic`). Read the key from the `ANTHROPIC_API_KEY` environment variable. **Never** put the key in code, config or logs.
2. `complete(messages)`: the first message with role "system" goes into the API's `system` field; the rest are the messages. Use `cfg.model`, `cfg.temperature`, `cfg.max_tokens` and `cfg.timeout_s`.
3. Return the reply text and a `Usage` (model, tokens in, tokens out, time in ms, cached).
4. **Retry once** if the call times out or the server returns a 5xx error. Don't retry other errors.
5. **Cache:** the cache key is a sha256 hash of model + temperature + max_tokens + messages. Before calling, look for `data/cache/llm/<key>.json`; if it's there, return it with `cached=True`. After calling, save it. If `cfg.cache` is false, skip the cache completely.
6. In `get_llm`, return your class when `cfg.fake` is false.

## Done when
- [ ] Calling twice with the same messages: the second call returns `cached=True` and doesn't call the API (test with a fake client object, so tests never use the real API)
- [ ] `cache: false` always calls the API
- [ ] The timeout and retry paths are tested with the fake client
- [ ] One real call, done by hand, is pasted into your PR (prompt, answer, usage)
- [ ] `grep -rn "sk-ant" .` finds nothing

## Learn first
- Input tokens vs output tokens, and what each costs.
- Why the cache key must include everything that changes the answer (the model, settings and every word of the prompt).
