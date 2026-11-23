# [REP-03] Parsing quality report for the real annual reports
labels: team:rep, size:S
**Owner:** R1 · **Size:** S (1 day) · **Due:** day 8 · **Needs:** REP-02, EVAL-01 (the PDFs downloaded)

## In one sentence
A script that parses all 6 real reports and writes a table showing how well parsing went.

## What to do
1. Create `scripts/quality.py`. For each row in `data/registry.csv`, parse and clean the PDF.
2. Write `eval/reports/parsing_quality.md` with one row per document:
   pages · how many pages of each status · median and lowest characters per page · number of blocks · odd characters left (`�`, `ﬁ`, `ﬂ`) · seconds taken
3. Below the table, list every page that is not `ok`, by number.
4. Open 3 of those pages in a PDF viewer and write one line each on what went wrong.

## Done when
- [ ] The report exists for all 6 reports and is committed
- [ ] E1 has read it and agrees the corpus is usable (or swaps a report)
