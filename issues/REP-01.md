# [REP-01] Parser: read a PDF into pages and blocks
labels: team:rep, size:M
**Owner:** R1 · **Size:** M (2-3 days) · **Due:** day 5 · **Needs:** nothing, start now

## In one sentence
Turn a PDF file into a `Document`: one `Page` per PDF page, each with its text `Block`s in reading order.

## Why it matters
This is step 1. If a figure is lost or scrambled here, nothing later can find it.

## What to do
1. Open `src/rag/rep/parse.py`. Run `grep -rn "STUB(REP-01)" src/` to see the part to replace.
2. Open the PDF with PyMuPDF: `pymupdf.open(path)`. Loop over its pages.
3. For each page, call `page.get_text("dict")`. It returns "blocks"; each block has "lines", and each line has "spans" (pieces of text with a font and size).
4. For each text block, make a `Block`: join its spans' text, take its `bbox`, its largest font `size`, and `bold=True` if most of its characters are bold.
5. **Reading order:** sort the blocks top to bottom. If the page has two columns (blocks on both sides of the page's middle), read the whole left column first, then the right.
6. Give each page a `status`:
   - `"ok"`: normal page
   - `"empty"`: no text at all
   - `"no_text_layer"`: fewer than `cfg.min_chars_text_layer` characters (probably a scanned image)
   - `"failed"`: an error happened. Catch it, and put the error message in `reason`. **Never drop a page.**
7. Page numbers start at 1 (`page=1` is the first page).

## Test it with
`tests/fixtures/acme_ar_fy2025.pdf`, a fake 6-page annual report. `tests/fixtures/acme_ar_fy2025.expected.json` lists, for each page, the strings that must appear and in what order. Write your tests in `tests/rep/test_parse.py`.

## Done when
- [ ] Every page of the fixture gives the right `status` (page 6 is `no_text_layer`)
- [ ] For each page, the `in_order` strings from the expected file appear in that order in `page.text` (compare with `rag.match.normalize`, because line breaks differ)
- [ ] Page 2 (two columns) reads left column, then right column
- [ ] `len(doc.pages)` equals the PDF's page count
- [ ] `uv run pytest` and `uv run python -m rag.run --config tests/ci.yaml --name smoke --overwrite` pass

## Learn first
- A PDF stores *drawing instructions* (put this glyph at x, y), not paragraphs. That's why reading order is a problem.
- Look at the raw output: `uv run python -c "import pymupdf; print(pymupdf.open('tests/fixtures/acme_ar_fy2025.pdf')[0].get_text('dict'))"`. Notice the page number "210" comes out before the heading.
