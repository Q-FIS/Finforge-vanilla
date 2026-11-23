# [REP-02] Cleaner: tidy the text without changing any number
labels: team:rep, size:M
**Owner:** R1 · **Size:** M (2-3 days) · **Due:** day 7 · **Needs:** REP-01 (until it's merged, build a small `Document` by hand in your tests)

## What is this, in plain words?
Text straight out of a PDF is messy. The same header is repeated on every page,
the page number is in the middle of the text, words are broken across lines
("opera-" / "tions"), and some characters are odd look-alikes (the "ﬁ"
ligature instead of "f" + "i"). If we leave this in, the header gets mixed into
every chunk, and searches match junk.

You clean all of that up, but **never change a figure**. "₹1,45,000 crore",
"(1,234)" and "—" must come out exactly as they went in, because the
answers and the evaluation depend on them.

## Where it fits
parse_pdf() (REP-01) → `Document` → **clean_document() (you)** → `Document` → chunkers

## What you get, and what you must give back
You get a `Document` and `cfg` (a `CleanConfig`: `remove_headers_footers`, `header_footer_min_share` = 0.4). You return a `Document` with the **same number of pages**, where:
- every block's text is cleaned (steps 1-3);
- header and footer blocks are removed (step 4);
- `page.label` is set to the printed page number, if one was found (step 5).

Example, fixture page 1. **Before:** blocks
`"Acme Industries Limited | Annual Report 2024-25"`, `"210"`, `"Directors' Report"`, ...
**After:** blocks `"Directors' Report"`, ..., and `page.label == "210"`.

## Step by step
Write each step as its own small function, so each one can be tested on its own.
1. **Unicode:** `unicodedata.normalize("NFKC", text)`. This turns "ﬁ" into "fi", full-width digits into normal ones, and so on.
2. **Spaces:** replace runs of spaces and tabs with one space (`re.sub(r"[ \t]+", " ", text)`), and strip each line. Keep the line breaks.
3. **Words broken across lines:** `"opera-\ntions"` → `"operations"`. Only join when there's a **letter** before the hyphen and a **letter** after the line break. `"2024-\n25"` must stay as it is. Hint: `re.sub(r"(?<=[a-zA-Z])-\n(?=[a-z])", "", text)`.
4. **Headers and footers** (only if `cfg.remove_headers_footers`):
   - A block is a *candidate* if it sits in the top 8% of its page (`bbox[3] < 0.08 * page.height`) or the bottom 8% (`bbox[1] > 0.92 * page.height`).
   - Make a "signature" for each candidate: its text with every digit replaced by `#` (so "Page 12" and "Page 13" both become "Page ##").
   - Count, for each signature, on how many pages it appears. If that's at least `cfg.header_footer_min_share` × (number of pages), it's a header or footer: remove those blocks from every page.
5. **Page labels:** if a block you removed is only a number (like "210"), save it as `page.label` before removing it.

## Watch out for
- **These must never change.** Write a test for each: `₹`, `crore`, `lakh`, `1,45,000`, `(1,234)`, `—`, `12.5%`, `FY2024-25`, `2024-25`.
- Don't delete a block just because it contains a number. Only repeated, top-or-bottom blocks are headers and footers.
- Never remove a page. If a page ends up with no blocks, keep it and log a warning.
- `page.height` is filled by REP-01. In a hand-made test `Document`, set it yourself (842 for A4).

## How to test it
Create `tests/rep/test_clean.py`:
- small tests for each step, e.g. `assert fix_hyphens("opera-\ntions") == "operations"` and `assert fix_hyphens("2024-\n25") == "2024-\n25"`;
- the fixture: parse it, clean it, and check that the header "Acme Industries Limited | Annual Report 2024-25" is gone from pages 1-5, that `page.label` equals the `label` in `acme_ar_fy2025.expected.json`, and that every `in_order` string is still there.

## Done when
- [ ] At least 15 tests, including the "must never change" list
- [ ] On the fixture, the header is gone and `page.label` is "210" to "214" on pages 1-5
- [ ] All the `in_order` strings are still there after cleaning
- [ ] The number of pages never changes
- [ ] `uv run pytest` and the smoke run pass

## Learn first
- Try `unicodedata.normalize("NFKC", "ﬁnance ①")` in Python. What changed, and why does it matter for searching?
- Why don't we simply delete every line that contains a number?
