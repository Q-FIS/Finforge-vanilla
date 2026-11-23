# [REP-14] (should) Read tables properly with pdfplumber
labels: team:rep, size:M, should
**Owner:** R3 · **Size:** M (2-3 days) · **Due:** day 12 · **Needs:** REP-01
**This is a "should":** only start it when all your "must" issues are done.

## In one sentence
On pages with ruled tables, read each table as rows and columns and store it as one `table` block in markdown.

## What to do
1. With `pdfplumber`, find tables on each page (`page.find_tables()`). They work best with ruled lines, like the fixture's pages 3-5.
2. Turn each table into a markdown table (`| a | b |` rows).
3. Remove the normal text blocks that sit inside the table's bbox, and add one `Block(block_type="table", ...)` instead.

## Done when
- [ ] Pages 3, 4 and 5 of the fixture each produce one table block with the right rows
- [ ] All parser tests still pass
