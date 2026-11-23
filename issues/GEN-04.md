# [GEN-04] Count the tokens in a prompt
labels: team:gen, size:S
**Owner:** G2 · **Size:** S (1 day) · **Due:** day 5 · **Needs:** the API key

## What is this, in plain words?
The context builder (GEN-05) has a budget: at most 3,000 tokens of passages.
To keep to it, it must count tokens **the way our LLM counts them**. That's
different from the embedding model's count (REP-04), because every model has
its own tokenizer. Anthropic offers a free API call that counts tokens exactly.

## Step by step
1. Create `src/rag/gen/tokens.py`.
2. `count_llm_tokens(messages: list[dict], cfg: LLMConfig) -> int`:
   - split off the system message like GEN-01 does;
   - `client.messages.count_tokens(model=cfg.model, system=system_text, messages=other_messages).input_tokens`;
   - cache the result on disk like GEN-01 (key = sha256 of model + messages), so repeated runs and tests don't call the API again.
3. `estimate_llm_tokens(text: str) -> int`: a fast offline guess, e.g. `len(text) // 4`. GEN-05 uses it in tests and with the fake LLM.
4. Measure how wrong the estimate is on 10 real prompts (real count vs estimate), and write the typical error in its docstring, e.g. "usually within 15%".

## How to test it
`tests/gen/test_llm_tokens.py` with a fake client (like GEN-01's): the cache prevents a second call; the estimate is in a sensible range for a known text. Never call the real API in tests.

## Done when
- [ ] The tests pass
- [ ] Your PR shows, for 10 real prompts: `count_llm_tokens` vs the `tokens_in` reported by a real call (they should be equal or very close) vs the estimate
