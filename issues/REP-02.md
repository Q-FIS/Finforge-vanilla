# [REP-02] Cleaner: fix the text without breaking any numbers
labels: team:rep, size:M
**Owner:** R1 · **Size:** M (2-3 days) · **Due:** day 7 · **Needs:** REP-01 (until then, build a `Document` by hand in your tests)

## In one sentence
Clean each page's blocks (odd characters, broken words, repeated headers and footers) without changing a single figure.

## What to do
In `src/rag/rep/clean.py`, inside `clean_document(doc, cfg)`:
1. **Unicode:** `unicodedata.normalize("NFKC", text)` turns odd characters like the "ﬁ" ligature into normal ones.
2. **Spaces:** turn runs of spaces and tabs into one space.
3. **Broken words:** "opera-\ntions" becomes "operations", but only when there is a letter on both sides. "2024-25" must stay.
4. **Headers and footers:** a block near the top or bottom of the page (top or bottom 8%) whose text repeats on at least `cfg.header_footer_min_share` of pages (40%) is a header or footer. Remove it. Tip: replace digits with `#` before comparing, so "Page 12" and "Page 13" count as the same text.
5. **Page numbers:** if a removed footer is just a number (like "212"), store it in `page.label`.
6. Only do step 4 if `cfg.remove_headers_footers` is true.

## Must never change
`₹`, `crore`, `lakh`, `1,45,000`, `(1,234)`, `—`, `12.5%`. Write a test for each.

## Done when
- [ ] On the fixture, the header "Acme Industries Limited | Annual Report 2024-25" is gone from pages 1-5
- [ ] `page.label` is "210" to "214" on pages 1-5 (the expected file lists them)
- [ ] All `in_order` strings are still there
- [ ] At least 15 tests in `tests/rep/test_clean.py`, including the "must never change" list
- [ ] The number of pages never changes
- [ ] `uv run pytest` and the smoke run pass

## Learn first
- What NFKC normalisation does (try it on "ﬁ" and "①").
- Why we don't just delete every line that contains a number.
