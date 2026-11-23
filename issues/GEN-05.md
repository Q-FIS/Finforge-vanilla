# [GEN-05] Context builder: fit the best passages into a token budget
labels: team:gen, size:M
**Owner:** G2 · **Size:** M (2-3 days) · **Due:** day 8 · **Needs:** GEN-04 (until it's merged, use `estimate_llm_tokens` or count words)

## What is this, in plain words?
Retrieval gives us the 5 best chunks. You turn them into the `<context>` part
of the prompt: each passage gets a **tag** ([C1], [C2]...) so the model can
cite it, and a **source line** (company, year, statement, page), so the model
knows exactly what the numbers belong to. And it must fit a **token budget**:
if a passage doesn't fit, it's left out **and recorded**. It's never silently
cut in half, because half a table is worse than no table.

## Where it fits
retrieve() → best hits → **build_context() (you)** → `Context` → generate_answer() (GEN-07)

## What you must give back
```python
context = build_context(hits[:5], ContextConfig(max_tokens=3000))
print(context.text)
```
```
<context>
[C1] Acme Industries Limited · FY2025 · standalone · Standalone Statement of Profit and Loss · p. 4
Standalone Statement of Profit and Loss for the year ended March 31, 2025
(₹ in crore)
Particulars FY2025 FY2024 ...

[C2] Acme Industries Limited · FY2025 · consolidated · Consolidated Statement of Profit and Loss · p. 3
...
</context>
```
`context.passages` holds one `Passage(tag, chunk, n_tokens)` per passage included; `context.dropped` lists `(chunk_id, "budget")` for each passage left out.

## Step by step
In `build_context` in `src/rag/gen/context.py`:
1. Go through the hits in order (best first). For each, format the passage: the tag line `[C<n>] <company name> · <fy> · <basis> · <last heading in section_path> · p. <page_start>`, a newline, then `chunk.text`.
   - Tags are numbered by position in the prompt, C1, C2, C3, with no gaps, even if some hits were dropped.
   - Skip any part of the source line that's empty (e.g. no section path).
2. Count each passage's tokens. If adding it would go over `cfg.max_tokens`, **don't add it**: append `(hit.chunk.chunk_id, "budget")` to `dropped`, and try the next hit (a smaller one may still fit).
3. **The only exception:** if the very first passage alone is over the budget, shorten it to fit and set `truncated=True` on its `Passage`, so the model gets at least something.
4. Join the passages with blank lines and wrap them in `<context>\n ... \n</context>`.
5. `cfg.order`: for `"rank"`, keep the order. `"gold_at:<n>"` is for experiment E8 (GEN-12); leave it until then.

## Watch out for
- The company's full name isn't on the chunk, only `chunk.company` ("acme"). Coordinate with R4 (REP-10), who needs the same thing; until then, use `chunk.company`.
- Counting tokens of a whole prompt with the API on every passage is slow. Count each passage once.

## How to test it
`tests/gen/test_context.py`, with hand-made `Hit`s and a word-counting token function:
- the total never goes over the budget;
- a passage that doesn't fit is in `dropped`, and a smaller later one still gets in;
- tags are C1, C2, C3 with no gaps;
- the source line has company, fy, basis, section and page;
- a single huge first passage is truncated and marked.

## Done when
- [ ] The tests pass, and the smoke run passes
- [ ] The `STUB(GEN-05)` line is gone

## Learn first
- "Lost in the Middle" (Liu et al., 2024): models use the start and end of a long prompt better than the middle. Why does that make passage order matter? (We test it in E8.)
