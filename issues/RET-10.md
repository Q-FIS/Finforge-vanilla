# [RET-10] Remove repeated hits from overlapping chunks
labels: team:ret, size:S
**Owner:** T3 · **Size:** S (1 day) · **Due:** day 10 · **Needs:** nothing

## What is this, in plain words?
With overlapping chunks (REP-05), two neighbouring chunks share text, so a
search can return both: the same passage twice, wasting two of our 5 slots in
the prompt. You remove a hit when it mostly repeats a better one.

## Step by step
In `dedupe(hits)` in `src/rag/ret/filters.py`:
1. Go through the hits from best to worst, and keep a list `kept`.
2. For each hit, compare it with every hit already in `kept` **from the same document**. If `rag.match.coverage(hit.chunk.text, kept_hit.chunk.text) > 0.5` (more than half of this hit's text is in the better hit), drop it.
3. Otherwise add it to `kept`.
4. Renumber the ranks of `kept`: 1, 2, 3, ...
5. `logging.info` the ids of dropped chunks.

## How to test it
`tests/ret/test_dedupe.py`: two hits whose texts overlap by 80% → only the better one stays; two different texts → both stay; same text in two **different** documents → both stay; ranks start at 1 with no gaps.

## Done when
- [ ] The tests pass, and the `STUB(RET-10)` line is gone
