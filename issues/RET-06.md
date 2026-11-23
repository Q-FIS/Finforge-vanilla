# [RET-06] How fast is our search, and how much memory does it use?
labels: team:ret, size:S
**Owner:** T2 · **Size:** S (1 day) · **Due:** day 11 · **Needs:** RET-05

## What is this, in plain words?
People reach for "vector databases" very early. You measure when that's
actually needed: how slow does brute-force search get as the number of chunks
grows from a thousand to a million?

## Step by step
1. Write `scripts/search_speed.py`. For N = 1,000, 10,000, 100,000 and 1,000,000, make random vectors of size 384 and normalise them to length 1.
2. For both our `DenseIndex` and FAISS `IndexFlatIP`, measure: time to build; memory (N × 384 × 4 bytes, since a float32 is 4 bytes); and the time of 100 searches with k=20 (median and 95th percentile, using `time.perf_counter()`).
3. Write `eval/reports/search_speed.md`: the table, our real corpus's size marked on it, and one sentence on how big N can get before brute force becomes too slow (say, over 100 ms per search).

## Done when
- [ ] The script and report are committed
