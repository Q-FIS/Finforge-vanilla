"""DEMO-01: count the words in a piece of text.

A practice task: it shows the workflow, it is not part of the pipeline.
"""


def count_words(text: str) -> int:
    """How many words are in `text`. Words are separated by any whitespace.

    count_words("Revenue grew 12%.")   # -> 3
    count_words("")                    # -> 0
    """
    # str.split() with no argument splits on any run of spaces, tabs or
    # newlines, and ignores whitespace at the start and end.
    return len(text.split())
