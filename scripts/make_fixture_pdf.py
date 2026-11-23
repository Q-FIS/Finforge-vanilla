"""Generate tests/fixtures/acme_ar_fy2025.pdf and its expected-output file.

A 6-page synthetic annual report for a fictional company, built to contain
every situation the parser and cleaner must handle:

    page 1  plain text: heading, paragraphs, ₹ figures, a subsidiary
    page 2  two columns: reading order must be left column, then right
    page 3  consolidated P&L table (ruled lines, brackets, Indian grouping)
    page 4  standalone P&L table (same rows, different figures)
    page 5  notes: "(1,234)" negatives and "—" nil
    page 6  an image only, no text layer (as a scanned page would be)

Pages 1-5 carry a running header and a printed page number (210-214) that
differs from the physical page number (1-5), like a real annual report.

Because this script writes the PDF, it also knows the right answer, and
saves it to acme_ar_fy2025.expected.json. Run from the repo root:

    uv run python scripts/make_fixture_pdf.py

The PDF is committed, so this only needs re-running if the content changes.
All figures are invented.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pymupdf

OUT_DIR = Path("tests/fixtures")
DOC_ID = "acme_ar_fy2025"
HEADER = "Acme Industries Limited | Annual Report 2024-25"
FIRST_PRINTED_PAGE = 210

# Noto Sans has the ₹ glyph; the PDF base fonts (Helvetica etc.) do not.
FONT_DIRS = [Path("/usr/share/fonts/noto"), Path("/usr/share/fonts/truetype/noto")]


def find_font(name: str) -> str:
    for d in FONT_DIRS:
        if (d / name).exists():
            return str(d / name)
    raise SystemExit(f"Font {name} not found in {FONT_DIRS}; install Noto Sans.")


REGULAR = find_font("NotoSans-Regular.ttf")
BOLD = find_font("NotoSans-Bold.ttf")
W, H = pymupdf.paper_size("a4")  # 595 x 842 points
MARGIN = 56


def text(page, rect, s, size=10.0, bold=False, align=0):
    font = ("notob", BOLD) if bold else ("noto", REGULAR)
    left = page.insert_textbox(
        pymupdf.Rect(*rect), s, fontsize=size, fontname=font[0], fontfile=font[1], align=align
    )
    assert left >= 0, f"text did not fit in its box: {s[:40]!r}"


def header_footer(page, printed: int):
    text(page, (MARGIN, 24, W - MARGIN, 40), HEADER, size=8)
    text(page, (MARGIN, H - 36, W - MARGIN, H - 20), str(printed), size=8, align=1)


def table(page, top, rows, col_x=(MARGIN, 360, 460), row_h=22):
    """Ruled table: a line above every row and one below the last."""
    right = W - MARGIN
    for i, row in enumerate(rows):
        y = top + i * row_h
        page.draw_line((MARGIN, y), (right, y), width=0.6)
        for j, cell in enumerate(row):
            x0 = col_x[j]
            x1 = col_x[j + 1] if j + 1 < len(col_x) else right
            text(
                page,
                (x0 + 4, y + 5, x1 - 4, y + row_h),
                cell,
                size=9.5,
                bold=(i == 0),
                align=0 if j == 0 else 2,
            )
    page.draw_line((MARGIN, top + len(rows) * row_h), (right, top + len(rows) * row_h), width=0.6)


# --- page content (single source of truth for the PDF and the expectations) ---

P1 = [
    "Directors' Report",
    "Your Directors present the 40th Annual Report of Acme Industries Limited for the "
    "financial year ended March 31, 2025. Revenue from operations grew 20.8% to "
    "₹1,45,000 crore, compared with ₹1,20,000 crore in the previous year.",
    "The increase was primarily attributable to higher domestic sales. Acme Chemicals "
    "Private Limited, a wholly owned subsidiary, contributed ₹12,500 crore to "
    "consolidated revenue.",
    "The Company had 23,450 employees as on March 31, 2025.",
]
P2_HEADING = "Management Discussion and Analysis"
P2_LEFT = [
    "Domestic demand stayed strong through the year, led by public infrastructure "
    "spending and steady housing construction.",
    "Input costs eased in the second half of the year, which helped operating margins "
    "recover to their earlier levels.",
]
P2_RIGHT = [
    "Exports fell 4% because of weaker demand in Europe and longer shipping times "
    "through the Red Sea.",
    "The outlook for FY2026 remains positive, subject to normal monsoon conditions "
    "and stable commodity prices.",
]
P3_HEADING = "Consolidated Statement of Profit and Loss for the year ended March 31, 2025"
P3_ROWS = [
    ("Particulars", "FY2025", "FY2024"),
    ("Revenue from operations", "1,45,000", "1,20,000"),
    ("Other income", "2,300", "1,950"),
    ("Total income", "1,47,300", "1,21,950"),
    ("Profit for the year", "18,200", "15,400"),
]
P4_HEADING = "Standalone Statement of Profit and Loss for the year ended March 31, 2025"
P4_ROWS = [
    ("Particulars", "FY2025", "FY2024"),
    ("Revenue from operations", "1,32,500", "1,10,000"),
    ("Other income", "2,100", "1,800"),
    ("Total income", "1,34,600", "1,11,800"),
    ("Profit for the year", "16,900", "14,300"),
]
UNIT_LINE = "(₹ in crore)"
P5_HEADING = "Notes to the Standalone Financial Statements"
P5_SUB = "Note 32: Exceptional items"
P5_ROWS = [
    ("Particulars", "FY2025", "FY2024"),
    ("Impairment of investment in subsidiary", "(1,234)", "—"),
    ("Gain on sale of land", "850", "—"),
    ("Net exceptional items", "(384)", "—"),
]
P5_NOTE = "Figures in brackets denote negative amounts. '—' denotes nil."


def build() -> pymupdf.Document:
    doc = pymupdf.open()

    # Page 1: plain text
    page = doc.new_page(width=W, height=H)
    header_footer(page, FIRST_PRINTED_PAGE)
    text(page, (MARGIN, 70, W - MARGIN, 100), P1[0], size=16, bold=True)
    y = 110
    for para in P1[1:]:
        text(page, (MARGIN, y, W - MARGIN, y + 70), para, size=10.5)
        y += 80

    # Page 2: two columns
    page = doc.new_page(width=W, height=H)
    header_footer(page, FIRST_PRINTED_PAGE + 1)
    text(page, (MARGIN, 70, W - MARGIN, 100), P2_HEADING, size=16, bold=True)
    col_w = (W - 2 * MARGIN - 24) / 2
    for col, paras in enumerate((P2_LEFT, P2_RIGHT)):
        x0 = MARGIN + col * (col_w + 24)
        y = 115
        for para in paras:
            text(page, (x0, y, x0 + col_w, y + 90), para, size=10.5)
            y += 100

    # Pages 3 and 4: financial statements
    for i, (heading, rows) in enumerate(((P3_HEADING, P3_ROWS), (P4_HEADING, P4_ROWS))):
        page = doc.new_page(width=W, height=H)
        header_footer(page, FIRST_PRINTED_PAGE + 2 + i)
        text(page, (MARGIN, 70, W - MARGIN, 110), heading, size=13, bold=True)
        text(page, (MARGIN, 112, W - MARGIN, 128), UNIT_LINE, size=9, align=2)
        table(page, 132, rows)

    # Page 5: notes with brackets and dashes
    page = doc.new_page(width=W, height=H)
    header_footer(page, FIRST_PRINTED_PAGE + 4)
    text(page, (MARGIN, 70, W - MARGIN, 100), P5_HEADING, size=13, bold=True)
    text(page, (MARGIN, 102, W - MARGIN, 130), P5_SUB, size=11, bold=True)
    text(page, (MARGIN, 132, W - MARGIN, 150), UNIT_LINE, size=9, align=2)
    table(page, 154, P5_ROWS)
    text(page, (MARGIN, 260, W - MARGIN, 284), P5_NOTE, size=9)

    # Page 6: image only, like a scanned page
    page = doc.new_page(width=W, height=H)
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 200, 280), False)
    pix.set_rect(pix.irect, (225, 225, 225))
    pix.set_rect(pymupdf.IRect(20, 30, 180, 40), (120, 120, 120))  # fake lines of "text"
    pix.set_rect(pymupdf.IRect(20, 50, 160, 60), (120, 120, 120))
    page.insert_image(pymupdf.Rect(MARGIN, 60, W - MARGIN, H - 60), pixmap=pix)

    doc.set_metadata({"title": "Acme Industries Limited Annual Report 2024-25 (synthetic)"})
    return doc


def row_text(row) -> list[str]:
    return list(row)


def expectations() -> dict:
    """What a correct parse + clean must produce, page by page.

    `in_order`: strings that must appear in the page text in this order
    (compare after rag.match.normalize, since line wrapping adds newlines).
    `header_footer`: text the cleaner must remove. `label`: the printed number.
    """

    def table_strings(rows):
        return [cell for row in rows for cell in row]

    pages = [
        {"page": 1, "status": "ok", "in_order": P1},
        {"page": 2, "status": "ok", "in_order": [P2_HEADING, *P2_LEFT, *P2_RIGHT]},
        {"page": 3, "status": "ok", "in_order": [P3_HEADING, UNIT_LINE, *table_strings(P3_ROWS)]},
        {"page": 4, "status": "ok", "in_order": [P4_HEADING, UNIT_LINE, *table_strings(P4_ROWS)]},
        {
            "page": 5,
            "status": "ok",
            "in_order": [P5_HEADING, P5_SUB, UNIT_LINE, *table_strings(P5_ROWS), P5_NOTE],
        },
        {"page": 6, "status": "no_text_layer", "in_order": []},
    ]
    for p in pages[:5]:
        p["header_footer"] = [HEADER, str(FIRST_PRINTED_PAGE + p["page"] - 1)]
        p["label"] = str(FIRST_PRINTED_PAGE + p["page"] - 1)
    pages[5]["header_footer"] = []
    pages[5]["label"] = ""
    return {
        "doc_id": DOC_ID,
        "page_count": 6,
        "headings": [P1[0], P2_HEADING, P3_HEADING, P4_HEADING, P5_HEADING, P5_SUB],
        "pages": pages,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = OUT_DIR / f"{DOC_ID}.pdf"
    doc = build()
    doc.subset_fonts()  # embed only the glyphs used: ~700 KB -> a few KB
    # deterministic output: no timestamps/ids that change on every run
    doc.save(pdf_path, garbage=4, deflate=True, no_new_id=True)
    exp_path = OUT_DIR / f"{DOC_ID}.expected.json"
    exp_path.write_text(
        json.dumps(expectations(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    sha = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    print(f"wrote {pdf_path} ({pdf_path.stat().st_size} bytes, sha256 {sha})")
    print(f"wrote {exp_path}")


if __name__ == "__main__":
    main()
