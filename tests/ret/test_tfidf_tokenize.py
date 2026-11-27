from rag.ret.tfidf import tokenize


def test_financial_amount():
    assert tokenize("Revenue of ₹1,45,000 crore in FY2025") == [
        "revenue",
        "of",
        "₹",
        "1,45,000",
        "crore",
        "in",
        "fy2025",
    ]


def test_parentheses():
    assert tokenize("Impairment (1,234) — see Note 32") == [
        "impairment",
        "1,234",
        "see",
        "note",
        "32",
    ]


def test_financial_year_range():
    assert tokenize("FY 2024-25 growth was 12.5%") == [
        "fy",
        "2024-25",
        "growth",
        "was",
        "12.5",
        "%",
    ]


def test_rs_lakh():
    assert tokenize("Rs. 3.2 lakh") == ["rs", "3.2", "lakh"]


def test_fy25():
    assert tokenize("FY25") == ["fy25"]


def test_march_31_2025():
    assert tokenize("March 31, 2025") == ["march", "31", "2025"]


def test_empty_string():
    assert tokenize("") == []


def test_only_stopwords():
    assert tokenize("the of and a an") == ["the", "of", "and", "a", "an"]


def test_long_indian_number():
    assert tokenize("12,34,56,789") == ["12,34,56,789"]


def test_lowercase():
    assert tokenize("REVENUE FY2025") == ["revenue", "fy2025"]


def test_decimal():
    assert tokenize("12.75") == ["12.75"]


def test_percentage():
    assert tokenize("12.5%") == ["12.5", "%"]


def test_rupee_symbol():
    assert tokenize("₹500") == ["₹", "500"]


def test_year_range_stays_one_token():
    assert tokenize("2023-24 and 2024-25") == ["2023-24", "and", "2024-25"]


def test_alphanumeric_financial_term():
    assert tokenize("FY2025 Q3") == ["fy2025", "q3"]


def test_trailing_comma():
    assert tokenize("1,234,") == ["1,234"]


def test_trailing_comma_after_sentence():
    assert tokenize("Revenue was 1,45,000,") == ["revenue", "was", "1,45,000"]


def test_stopword_removal():
    assert tokenize("Revenue of the company in FY2025", remove_stopwords=True) == [
        "revenue",
        "company",
        "fy2025",
    ]


def test_stopword_removal_disabled():
    assert tokenize("Revenue of the company", remove_stopwords=False) == [
        "revenue",
        "of",
        "the",
        "company",
    ]


def test_stopword_removal_preserves_financial_tokens():
    assert tokenize("₹1,45,000 in FY2025 was 12.5%", remove_stopwords=True) == [
        "₹",
        "1,45,000",
        "fy2025",
        "12.5",
        "%",
    ]


def test_symbols_and_words():
    assert tokenize("profit ₹ crore % growth") == ["profit", "₹", "crore", "%", "growth"]


def test_punctuation_is_not_tokenized():
    assert tokenize("Revenue: (₹1,234.50)!") == ["revenue", "₹", "1,234.50"]


def test_stopwords_are_exact_list():
    assert (
        tokenize("the of and a an in to for was is on by with as at", remove_stopwords=True) == []
    )


def test_unknown_punctuation():
    assert tokenize("profit---growth!!!") == ["profit", "growth"]
