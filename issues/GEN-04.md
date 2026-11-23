# [GEN-04] Count the tokens of a prompt
labels: team:gen, size:S
**Owner:** G2 · **Size:** S (1 day) · **Due:** day 5 · **Needs:** the API key

## In one sentence
A function that says how many tokens a prompt uses in **our LLM** (not the embedding model: they count differently).

## What to do
1. Create `src/rag/gen/tokens.py` with `count_llm_tokens(messages, cfg) -> int`.
2. Anthropic has a token-counting API (`client.messages.count_tokens`). Use it, and cache the results like GEN-01 does, so tests don't call it repeatedly.
3. Also write `estimate_llm_tokens(text) -> int`, a fast offline estimate (for example, characters / 4). Measure how wrong it is on 10 real prompts, and write that in the docstring.

## Done when
- [ ] On 10 prompts, `count_llm_tokens` equals the `tokens_in` reported by the real call (paste the numbers in your PR)
- [ ] The estimate's typical error is written in the docstring
