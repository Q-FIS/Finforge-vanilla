"""DEMO-01: count_words."""

from rag.demo.word_count import count_words


def test_simple_sentence():
    assert count_words("Revenue grew 12%.") == 3


def test_empty_text_has_no_words():
    assert count_words("") == 0


def test_extra_spaces_and_newlines_are_ignored():
    assert count_words("  two\n words ") == 2
