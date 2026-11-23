# [REP-03] Parsing quality report on the real annual reports
labels: team:rep, size:S
**Owner:** R1 · **Size:** S (1 day) · **Due:** day 8 · **Needs:** REP-02, EVAL-01 (the PDFs downloaded)

## What is this, in plain words?
Our fake report is tidy; real reports are not. Before anyone builds on the
real ones, we need to know how well parsing went: did any pages come out empty?
Are there garbled characters? This script answers that with numbers, so we
find problems now and not on day 14.

## What you must produce
A script, `scripts/quality.py`, that writes `eval/reports/parsing_quality.md`, like this:

| doc_id | pages | ok | empty | no_text_layer | failed | median chars/page | min chars/page | blocks | odd chars | seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| infosys_ar_fy2025 | 312 | 309 | 2 | 1 | 0 | 2,840 | 0 | 6,120 | 0 | 4.1 |

## Step by step
1. Load the registry: `load_registry("data/registry.csv")`. For each entry, `parse_pdf(pdf_path(entry, "data/pdfs"), ...)`, then `clean_document(...)`.
2. For each document, count the pages of each status, the characters per page (median and minimum), the total blocks, and the "odd characters": `�` (the replacement character, a sign of broken text), and any leftover ligatures like "ﬁ" and "ﬂ".
3. Write the table above as markdown.
4. Below it, list every page that is not `ok`: document, page number, status, reason.
5. Open 3 of those pages in a PDF viewer, and write one line each on what's actually there (for example, "a full-page photo of the board").

## Done when
- [ ] `uv run python scripts/quality.py` writes the report for all 6 reports
- [ ] The report is committed, with your 3 notes
- [ ] E1 has read it, and agrees the corpus is usable (or swaps a report)
