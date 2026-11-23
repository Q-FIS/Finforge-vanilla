"""F-06: the synthetic fixture report is what its expectations file says.

These tests read the PDF with raw PyMuPDF, not with our parser, so they check
the fixture itself. REP-01/REP-02 will test the real parser against the same
expectations file.
"""

import json
from pathlib import Path

import pymupdf
import pytest

from rag.match import normalize, on_page
from rag.schema import Question, load_jsonl

FIXTURES = Path(__file__).parent / "fixtures"
PDF = FIXTURES / "acme_ar_fy2025.pdf"
EXPECTED = json.loads((FIXTURES / "acme_ar_fy2025.expected.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def page_texts() -> list[str]:
    with pymupdf.open(PDF) as doc:
        return [page.get_text() for page in doc]


def test_page_count(page_texts):
    assert len(page_texts) == EXPECTED["page_count"] == 6


@pytest.mark.parametrize("page", EXPECTED["pages"], ids=lambda p: f"page{p['page']}")
def test_expected_strings_appear_in_order(page_texts, page):
    text = normalize(page_texts[page["page"] - 1])
    pos = 0
    for s in page["in_order"]:
        found = text.find(normalize(s), pos)
        assert found >= 0, f"page {page['page']}: {s!r} missing or out of order"
        pos = found + 1


def test_image_page_has_no_text(page_texts):
    assert page_texts[5].strip() == ""


def test_every_fixture_question_quote_is_on_its_page(page_texts):
    # The same check EVAL-03's question checker will run on real questions.
    for q in load_jsonl(FIXTURES / "questions.jsonl", Question):
        for ev in q.evidence:
            assert on_page(ev.quote, page_texts[ev.page - 1]), (q.id, ev.quote)
