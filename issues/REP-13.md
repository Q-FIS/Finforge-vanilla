# [REP-13] Compare our chunkers with LangChain's splitter
labels: team:rep, size:S
**Owner:** R1 · **Size:** S (1 day) · **Due:** day 11 · **Needs:** REP-05, REP-08

## What is this, in plain words?
Most RAG tutorials use one line of LangChain to split text:
`RecursiveCharacterTextSplitter`. Now that we've built our own chunkers, you
compare: what does the one-liner get wrong on a real annual report, and what
does ours do differently?

## Step by step
1. Run it without adding it to our project:
   `uv run --with langchain-text-splitters python your_script.py`
2. It counts **characters**, not tokens. Use `chunk_size=2000, chunk_overlap=200` (roughly 512 and 50 tokens).
3. Run it, and each of our three chunkers, on the same cleaned real report.
4. For each, count: number of chunks · chunks over 512 tokens (use our `count_tokens`) · sentences cut in half (a chunk that ends without `.`, `?` or `!`) · table rows split from their label.
5. Write `eval/reports/langchain_comparison.md`: the table, plus 3 to 5 sentences explaining the biggest differences, with one real example.

## Done when
- [ ] The report is committed
