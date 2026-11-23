"""F-05: the shared quote matcher."""

import pytest

from rag.match import coverage, figures, fully_contains, is_relevant, normalize, on_page


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Revenue  from\noperations", "revenue from operations"),
        ("\u201cProfit\u201d \u2014 FY2025", '"profit" - fy2025'),
        ("opera-\ntions and opera- tions", "operations and operations"),
        ("pro\ufb01t", "profit"),  # ligature
        ("pro\u00adfit", "profit"),  # soft hyphen
        ("₹1,45,000 crore (1,234) 12.5%", "₹1,45,000 crore (1,234) 12.5%"),  # figures untouched
        ("FY 2024-25", "fy 2024-25"),  # a digit hyphen is not a line break
    ],
)
def test_normalize(raw, expected):
    assert normalize(raw) == expected


def test_exact_and_reformatted_quotes_fully_covered():
    text = "The Company had 23,450 employees\nas on March 31, 2025."
    assert coverage("The Company had 23,450 employees as on March 31, 2025.", text) == 1.0
    assert coverage("THE COMPANY HAD 23,450", text) == 1.0


def test_half_a_quote():
    quote = "Revenue from operations grew 20.8% to ₹1,45,000 crore in FY2025"
    first_half = quote[: len(quote) // 2]
    assert coverage(quote, f"Some other words. {first_half}") == pytest.approx(0.5, abs=0.05)


def test_coverage_alone_is_fooled_by_table_labels():
    # Why is_relevant exists: same row label, different statement and figures.
    standalone = "Profit for the year 16,900 14,300"
    consolidated = "Profit for the year 18,200 15,400"
    assert coverage(standalone, consolidated) >= 0.5  # text alone says "relevant"...
    assert not is_relevant(standalone, consolidated)  # ...the figures say no


def test_is_relevant():
    row = "Revenue from operations 1,45,000 1,20,000"
    assert is_relevant(
        row, "Particulars FY2025 FY2024\nRevenue from operations\n1,45,000\n1,20,000"
    )
    # half of a figure-free quote is enough (a quote split across two chunks)
    sentence = "The increase was primarily attributable to higher domestic sales and exports"
    assert is_relevant(sentence, "...sales. The increase was primarily attributable to higher")
    assert not is_relevant(sentence, "Exports fell because of weaker demand")


def test_figures():
    assert figures("Revenue of \u20b91,45,000 crore on March 31, 2025, up 4.5%") == {
        "1,45,000",
        "2025",
    }
    assert figures("(1,234) and 16,900, then 850") == {"1,234", "16,900", "850"}


def test_fully_contains_and_on_page():
    page = "Net exceptional items\n(384)\n\u2014\nFigures in brackets denote negative amounts."
    assert fully_contains("Net exceptional items (384)", page)
    assert on_page("Net exceptional items (384)", page)
    assert not on_page("Net exceptional items (385)", page)  # one digit wrong: not on page


def test_empty_inputs():
    assert coverage("", "anything") == 0.0
    assert coverage("anything", "") == 0.0
