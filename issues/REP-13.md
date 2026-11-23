# [REP-13] Compare our chunkers with LangChain's splitter
labels: team:rep, size:S
**Owner:** R1 · **Size:** S (1 day) · **Due:** day 11 · **Needs:** REP-05, REP-08

## In one sentence
Run LangChain's popular `RecursiveCharacterTextSplitter` on one report and compare it with our chunkers.

## What to do
1. Install it just for this: `uv run --with langchain-text-splitters python ...`. Don't add it to `pyproject.toml`.
2. Pick a size close to our 512 tokens (it counts characters: about 2,000).
3. For it and for each of our chunkers, count: number of chunks · sentences cut in half · tables split · chunks over the token limit.
4. Write `eval/reports/langchain_comparison.md` with the table and 3-5 sentences explaining the differences.

## Done when
- [ ] The report is committed
