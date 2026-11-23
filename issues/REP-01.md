# [REP-01] Parser: read a PDF into pages and text blocks
labels: team:rep, size:M
**Owner:** R1 · **Size:** M (2-3 days) · **Due:** day 5 · **Needs:** nothing, start now

## What is this, in plain words?
Everything starts here. You take a PDF file and turn it into Python objects
the rest of the pipeline can use: a `Document` that has one `Page` per PDF
page, and each page has a list of `Block`s (pieces of text, with where they sit
on the page and how big their font is).

If a figure goes missing here, or comes out in the wrong order, no later step
can fix it. That's why this is the first issue on the critical path.

## Where it fits
`PDF file` → **parse_pdf() (you)** → `Document` → clean_document() (REP-02) → chunkers (REP-05/06/08)

## What you get, and what you must give back
- **You get:** a path like `tests/fixtures/acme_ar_fy2025.pdf`, a `doc_id` like `"acme_ar_fy2025"`, and `cfg` (settings; you need `cfg.min_chars_text_layer`, which is 50).
- **You give back:** a `Document` (see `src/rag/schema.py`):

```python
Document(
    doc_id="acme_ar_fy2025",
    source_path="tests/fixtures/acme_ar_fy2025.pdf",
    parse_seconds=0.12,
    pages=[
        Page(page=1, status="ok", width=595.0, height=842.0, blocks=[
            Block(text="Acme Industries Limited | Annual Report 2024-25", block_type="paragraph",
                  bbox=(56.0, 24.0, 290.0, 36.0), font_size=8.0, bold=False, order=0),
            Block(text="Directors' Report", block_type="paragraph",
                  bbox=(56.0, 70.0, 210.0, 92.0), font_size=16.0, bold=True, order=1),
            ...
        ]),
        ...
        Page(page=6, status="no_text_layer", width=595.0, height=842.0, blocks=[],
             reason="0 characters, page has an image (probably scanned)"),
    ],
)
```
(The numbers are illustrative. Leave every `block_type` as "paragraph"; REP-07 marks the headings.)

## Step by step
1. **Look at the raw data first.** Run this and read the output carefully:
   ```bash
   uv run python -c "import pymupdf, pprint; pprint.pprint(pymupdf.open('tests/fixtures/acme_ar_fy2025.pdf')[0].get_text('dict'))" | head -80
   ```
   You'll see a dict with `"blocks"`. Each text block (`"type": 0`) has `"bbox"` and `"lines"`; each line has `"spans"`; each span has `"text"`, `"size"` (font size), `"font"` and `"flags"`.
2. **Open the PDF** with `pymupdf.open(path)` and loop over its pages. Start a timer (`time.perf_counter()`) for `parse_seconds`.
3. **For each page**, wrap everything in `try/except Exception as e`, so one broken page can't crash the whole report. If an error happens, record the page with `status="failed"` and `reason=str(e)`.
4. **Make the blocks.** For each block with `"type": 0`:
   - text: join the spans of a line with `""`, and join the lines with `"\n"`. Use `.strip()`, and skip blocks that end up empty.
   - `bbox`: the block's `"bbox"` as a tuple of 4 floats.
   - `font_size`: the biggest `span["size"]` in the block.
   - `bold`: True if more than half of the block's characters are in spans where `span["flags"] & 16` is non-zero (that's PyMuPDF's "bold" bit), or where `"Bold"` appears in `span["font"]`.
5. **Put the blocks in reading order** (this is the hard part):
   - Find the middle of the page: `mid = page.rect.width / 2`.
   - A block is in the **left column** if it ends before the middle (`x1 < mid`), in the **right column** if it starts after the middle (`x0 > mid`), and **full width** otherwise.
   - If the page has blocks in both columns, it's a two-column page: take the full-width blocks above the columns first (top to bottom), then the whole left column (top to bottom), then the whole right column, then any full-width blocks below.
   - Otherwise just sort all blocks top to bottom (`bbox[1]`, then `bbox[0]`).
   - Set `block.order` to 0, 1, 2, ... in that final order.
6. **Give the page a status:**
   - count the characters in all its blocks;
   - 0 characters and no images → `"empty"`;
   - fewer than `cfg.min_chars_text_layer` characters **and** the page has images (`page.get_images()` is not empty) → `"no_text_layer"` (probably a scanned page). Write a `reason`, e.g. `"12 characters, page has an image"`;
   - otherwise `"ok"`.
7. Fill `width` and `height` from `page.rect`. Pages are numbered **from 1**: `page=index + 1`.

## Watch out for
- **Never drop a page.** `len(doc.pages)` must equal the PDF's page count, even for empty or broken pages. Later steps and the question checker count on it.
- PyMuPDF gives blocks in the order they were *drawn*, not the order you'd read them. On the fixture, the page number "210" comes out **before** the heading. Step 5 fixes this.
- Don't remove headers, footers or page numbers here. That's REP-02's job.

## How to test it
Create `tests/rep/test_parse.py`. The file `tests/fixtures/acme_ar_fy2025.expected.json` was written by the script that made the fake PDF, so it is the correct answer. For each page it lists `status` and `in_order`: strings that must appear in the page text, **in that order**.

```python
import json
from pathlib import Path
from rag.config import ParseConfig
from rag.match import normalize
from rag.rep.parse import parse_pdf

FIX = Path("tests/fixtures")
EXPECTED = json.loads((FIX / "acme_ar_fy2025.expected.json").read_text())

def test_statuses_and_order():
    doc = parse_pdf(FIX / "acme_ar_fy2025.pdf", "acme_ar_fy2025", ParseConfig())
    assert len(doc.pages) == EXPECTED["page_count"]
    for page, exp in zip(doc.pages, EXPECTED["pages"]):
        assert page.status == exp["status"], page.page
        text = normalize(page.text)
        position = 0
        for s in exp["in_order"]:
            found = text.find(normalize(s), position)
            assert found >= 0, f"page {page.page}: {s!r} missing or out of order"
            position = found
```
Also test: a path that doesn't exist raises `FileNotFoundError`; `width` and `height` are filled; `order` goes 0, 1, 2, ...

## Done when
- [ ] The test above passes on all 6 fixture pages (page 2 reads left column, then right; page 6 is `no_text_layer`)
- [ ] It runs on all 6 real reports without crashing (once EVAL-01 has downloaded them), and prints the seconds per report
- [ ] `uv run pytest` and the smoke run both pass

## Learn first
- A PDF stores **drawing instructions** ("put this letter at x=56, y=70"), not paragraphs. Why does that make reading order hard? Why do two-column pages come out scrambled in many tools?
- How can you tell a scanned page from a normal one? (A scanned page is just a picture: no text to extract.)
- Read `Block`, `Page` and `Document` in `src/rag/schema.py`.
