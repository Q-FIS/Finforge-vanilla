# [GEN-09] Check the model's citations with plain code
labels: team:gen, size:M
**Owner:** G4 · **Size:** M (2-3 days) · **Due:** day 10 · **Needs:** GEN-08

## What is this, in plain words?
Models sometimes cite passages that don't exist, "quote" words that aren't
there, or state a number no passage contains. That's **hallucination**, and in
finance it's the worst failure. You catch it with plain code, no AI: every
check is a simple, exact comparison.

## What it must give back
A `CitationReport` (see `src/rag/schema.py`). Empty lists mean everything passed:
```python
CitationReport(unknown_tags=["C7"],                       # cited, but there's no [C7]
               failed_quotes=[Citation("C1", "Profit 16,000")],   # not really in passage C1
               unsupported_numbers=["₹18,200 crore"],    # in the answer, but in no cited passage
               uncited_sentences=["Revenue rose 21%."])   # has a figure, but no [C..] tag
```

## Step by step
In `validate_citations` in `src/rag/gen/citations.py`:
1. Build a dict `{passage.tag: passage.chunk.text}` from `context.passages`.
2. **Unknown tags:** every `citation.tag` not in the dict, plus every `[C<n>]` written in `answer.text` that isn't in the dict.
3. **Failed quotes:** for each citation with a known tag, `rag.match.fully_contains(citation.quote, passage_text)` must be True. Empty quotes fail too.
4. **Unsupported numbers:** for each amount in `answer.text` (`extract_amounts`, GEN-08), there must be a matching amount (`same_amount`) in at least one **cited** passage. Add its `raw` text to the list if not.
5. **Uncited sentences:** split `answer.text` into sentences. Any sentence with an amount in it but no `[C<n>]` tag goes in the list.
6. An answer with status `"insufficient_evidence"` and no figures passes.

## How to test it
`tests/gen/test_citations.py`, with 12 hand-made answers and a small context:
- a correct answer;
- a tag that doesn't exist;
- a quote not in its passage;
- a number in no passage (the classic hallucination);
- a correct number with no citation;
- the right number cited to the wrong passage;
- a correct refusal;
- and a few more.

## Done when
- [ ] The tests pass, and the `STUB(GEN-09)` line is gone
- [ ] The smoke run's `metrics.json` still shows `citations_ok`
