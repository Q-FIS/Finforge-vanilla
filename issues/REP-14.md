# [REP-14] (should) Read tables properly with pdfplumber
labels: team:rep, size:M, should
**Owner:** R3 · **Size:** M (2-3 days) · **Due:** day 12 · **Needs:** REP-01
**This is a "should": only start it when all your other issues are done.**

## What is this, in plain words?
PyMuPDF gives us a table as many small separate blocks, one per cell. We lose
which number belongs to which row and column. `pdfplumber` can find tables
drawn with lines and give them back as rows and columns. You turn each table
into **one** block, written as a markdown table, so the chunker keeps it whole
and the LLM can read it.

## Step by step
1. In a new function (in `src/rag/rep/parse.py` or a new `tables.py`), open the PDF with `pdfplumber.open(path)`. Add it with `uv add pdfplumber`; the lead reviews dependency changes.
2. For each page, `page.find_tables()`. For each table, `table.extract()` gives a list of rows (lists of cell strings).
3. Turn the rows into markdown: `| Particulars | FY2025 | FY2024 |`, then a `| --- | --- | --- |` line, then one line per row.
4. In our `Page`: remove the blocks whose bbox is inside the table's bbox (`table.bbox`), and add one `Block(text=markdown, block_type="table", bbox=table.bbox, ...)` in their place, keeping the reading order.

## Done when
- [ ] Fixture pages 3, 4 and 5 each produce one `table` block with the right rows
- [ ] All the parser tests still pass
