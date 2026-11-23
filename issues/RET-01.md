# [RET-01] TF-IDF tokenizer that keeps financial words whole
labels: team:ret, size:S
**Owner:** T1 · **Size:** S (1 day) · **Due:** day 4 · **Needs:** nothing, start now

## What is this, in plain words?
TF-IDF (RET-02) is keyword search: it scores chunks by the words they share
with the question. First you need to split text into words ("tokens"). A
normal word splitter would break `₹1,45,000` into `1`, `45`, `000`, and
`FY2025` might become `fy` and `2025`. Then a search for "FY2025 revenue
1,45,000" matches every chunk with a "2025" or a "000" in it. Your tokenizer
keeps financial terms whole.

## What it must do
```python
tokenize("Revenue of ₹1,45,000 crore in FY2025")
# -> ["revenue", "of", "₹", "1,45,000", "crore", "in", "fy2025"]
tokenize("Impairment (1,234) — see Note 32")
# -> ["impairment", "1,234", "see", "note", "32"]
tokenize("FY 2024-25 growth was 12.5%")
# -> ["fy", "2024-25", "growth", "was", "12.5", "%"]
```

## Step by step
1. In `src/rag/ret/tfidf.py`, write `tokenize(text: str, remove_stopwords: bool = False) -> list[str]`.
2. Lowercase the text first.
3. Use **one** regular expression with `re.findall` that matches, in this order (the order matters: earlier alternatives win):
   - year ranges like `2024-25`: `\d{4}-\d{2}`
   - numbers with commas or decimals: `\d[\d,]*(?:\.\d+)?`
   - words, including words with digits like `fy2025`: `[a-z][a-z0-9]*`
   - the symbols `₹` and `%`
4. Strip a trailing comma from numbers ("1,45,000," → "1,45,000"). Brackets are simply not matched, so `(1,234)` becomes `1,234`.
5. Stop words: a small list (the, of, and, a, an, in, to, for, was, is, on, by, with, as, at). Remove them only when `remove_stopwords` is True.

## How to test it
`tests/ret/test_tfidf_tokenize.py`, with at least 20 cases: the three examples above, `"Rs. 3.2 lakh"`, `"FY25"`, `"March 31, 2025"`, an empty string, a sentence with only stop words, a long number like `"12,34,56,789"`.

## Done when
- [ ] At least 20 tests pass
- [ ] `uv run pytest` passes

## Learn first
- Why do rare words matter more than common ones for search? Think about "the" vs "debenture".
