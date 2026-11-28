"""REP-07: find_headings marks exactly the fixture's headings.

The parser (REP-01) is still a stub, so `fixture_doc` reads the fixture with
raw PyMuPDF, using REP-01's rules for font_size (largest span) and bold (more
than half the characters bold). Once REP-01 is merged, it can be replaced by
parse_pdf().
"""

import json
from pathlib import Path

import pymupdf
import pytest

from rag.match import normalize
from rag.rep.headings import body_font_size, find_headings
from rag.schema import Block, Document, Page

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PDF = FIXTURES / "acme_ar_fy2025.pdf"
EXPECTED = json.loads((FIXTURES / "acme_ar_fy2025.expected.json").read_text(encoding="utf-8"))


def raw_block(b: dict) -> Block:
    """One PyMuPDF text block as a Block, the way REP-01 describes."""
    spans = [span for line in b["lines"] for span in line["spans"]]
    text = "\n".join("".join(s["text"] for s in line["spans"]) for line in b["lines"]).strip()
    bold_chars = sum(len(s["text"]) for s in spans if s["flags"] & 16 or "Bold" in s["font"])
    return Block(
        text=text,
        block_type="paragraph",
        bbox=tuple(b["bbox"]),
        font_size=max(s["size"] for s in spans),
        bold=bold_chars > sum(len(s["text"]) for s in spans) / 2,
    )


@pytest.fixture
def fixture_doc() -> Document:
    pages = []
    with pymupdf.open(PDF) as pdf:
        for number, pdf_page in enumerate(pdf, start=1):
            blocks = [raw_block(b) for b in pdf_page.get_text("dict")["blocks"] if b["type"] == 0]
            blocks = [b for b in blocks if b.text]
            blocks.sort(key=lambda b: (b.bbox[1], b.bbox[0]))  # top to bottom
            pages.append(Page(page=number, status="ok", blocks=blocks))
    return Document(doc_id="acme_ar_fy2025", source_path=str(PDF), pages=pages)


def heading_texts(doc: Document) -> list[str]:
    return [
        normalize(block.text)
        for page in doc.pages
        for block in page.blocks
        if block.block_type == "heading"
    ]


def test_fixture_headings_are_exactly_the_expected_ones(fixture_doc):
    find_headings(fixture_doc)
    assert heading_texts(fixture_doc) == [normalize(h) for h in EXPECTED["headings"]]


def test_body_size_of_fixture_is_10_5(fixture_doc):
    assert body_font_size(fixture_doc) == 10.5


def test_bold_table_header_row_is_not_a_heading(fixture_doc):
    find_headings(fixture_doc)
    header_rows = [
        block
        for page in fixture_doc.pages
        for block in page.blocks
        if block.text.startswith("Particulars")
    ]
    assert len(header_rows) == 3  # pages 3, 4 and 5
    for block in header_rows:
        assert block.bold and block.font_size == 9.5
        assert block.block_type == "paragraph"


def test_document_without_text_does_not_crash():
    empty = Document(doc_id="x", source_path="x.pdf", pages=[])
    assert find_headings(empty) is empty
    no_text = Document(
        doc_id="x", source_path="x.pdf", pages=[Page(page=1, status="no_text_layer")]
    )
    assert find_headings(no_text).pages[0].blocks == []


def block(text: str, size: float, bold: bool = False, block_type: str = "paragraph") -> Block:
    return Block(text=text, block_type=block_type, bbox=(0, 0, 0, 0), font_size=size, bold=bold)


def one_page(*blocks: Block) -> Document:
    return Document(doc_id="x", source_path="x.pdf", pages=[Page(1, "ok", list(blocks))])


BODY = "Body text written at the normal size, long enough to win the character count."


def test_float_noise_in_font_size_is_ignored():
    doc = one_page(
        block(BODY, 10.5), block(BODY, 10.49999), block("Short bold title", 10.4999, True)
    )
    assert body_font_size(doc) == 10.5
    find_headings(doc)
    assert doc.pages[0].blocks[2].block_type == "heading"


def test_bold_sentence_ending_with_full_stop_is_not_a_heading():
    doc = one_page(block(BODY, 10.5), block("Figures are in crore.  \n", 10.5, bold=True))
    find_headings(doc)
    assert doc.pages[0].blocks[1].block_type == "paragraph"


def test_table_block_never_becomes_a_heading():
    doc = one_page(block(BODY, 10.5), block("| Particulars | FY2025 |", 20, True, "table"))
    find_headings(doc)
    assert doc.pages[0].blocks[1].block_type == "table"
