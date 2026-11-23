# [REP-10] Metadata: standalone or consolidated, and the header line
labels: team:rep, size:S
**Owner:** R4 · **Size:** S (1 day) · **Due:** day 7 · **Needs:** REP-07 (headings)

## In one sentence
Label each chunk "standalone", "consolidated" or "none", and build the optional header line that goes in front of the text we embed.

## What to do
In `src/rag/rep/metadata.py` (company and fy are already done):
1. In `add_metadata`, walk the document's headings in order. When a heading contains "standalone" or "consolidated" (any capitals), that becomes the basis for every following chunk, until another such heading appears. Before any such heading, the basis is "none".
2. In `embedding_text(chunk, cfg)`: if `cfg.prepend_header` is true, return
   `"<company name> · <fy> · <Basis> · <last heading in section_path>\n" + chunk.text`.
   Otherwise return `chunk.text`.
3. **Never change `chunk.text` itself.** The header only goes to the embedder.

## Done when
- [ ] On the fixture, chunks from page 3 are "consolidated" and from pages 4-5 are "standalone"
- [ ] A test shows `chunk.text` is the same with the header on or off
- [ ] Tests in `tests/rep/test_metadata.py`; `uv run pytest` passes
