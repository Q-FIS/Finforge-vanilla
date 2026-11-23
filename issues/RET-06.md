# [RET-06] How fast is our search, and how much memory does it use?
labels: team:ret, size:S
**Owner:** T2 · **Size:** S (1 day) · **Due:** day 11 · **Needs:** RET-05

## In one sentence
Measure search time and memory for 1 thousand up to 1 million chunks, numpy vs FAISS.

## What to do
1. Make random unit vectors of size 384 for N = 1,000, 10,000, 100,000 and 1,000,000.
2. For each N, for numpy and FAISS: time to build, memory (N x 384 x 4 bytes), and the time of 100 searches (median and 95th percentile).
3. Write `eval/reports/search_speed.md` with the table, and one sentence on how big N can get before brute-force search becomes too slow.

## Done when
- [ ] The report is committed
