# [REP-07] Find the headings
labels: team:rep, size:S
**Owner:** R3 · **Size:** S (1 day) · **Due:** day 5 · **Needs:** nothing (use the fixture, with the stub parser or raw PyMuPDF until REP-01 lands)

## What is this, in plain words?
Headings tell us where we are in the report: "Consolidated Statement of Profit
and Loss" means every number after it is a *consolidated* figure, until the
next such heading. Two later steps need headings: the section chunker (REP-08)
starts a new chunk at each one, and the metadata step (REP-10) uses them to
decide standalone vs consolidated.

A PDF doesn't say "this is a heading", so we guess from the look: headings use
**bigger** or **bold** text.

## Where it fits
parse_pdf() → **find_headings() (you)** → section chunker (REP-08), metadata (REP-10)

## Step by step
1. Create `src/rag/rep/headings.py` with `find_headings(doc: Document) -> Document`. It changes `block.block_type` to `"heading"` for heading blocks, and returns the document.
2. **The normal ("body") font size:** count, for each font size, how many characters are written in it across the whole document. The size with the most characters is the body size. (On the fixture it's 10.5.)
3. **A block is a heading if** either:
   - its `font_size >= 1.15 * body_size`, or
   - it is `bold`, its `font_size >= body_size`, it has fewer than 12 words, and it doesn't end with `"."`.
4. Ask R1 to call `find_headings(doc)` at the end of `parse_pdf`, or call it yourself in your PR once REP-01 is merged.

## Watch out for
- In the fixture, the table's first row ("Particulars", "FY2025", "FY2024") is bold but **smaller** than body text (9.5). The `font_size >= body_size` condition in the bold rule is what keeps those from counting as headings.

## How to test it
`tests/rep/test_headings.py`: parse the fixture, run `find_headings`, and check that the texts of the heading blocks (normalised with `rag.match.normalize`) are exactly the `headings` list in `tests/fixtures/acme_ar_fy2025.expected.json`:
`Directors' Report`, `Management Discussion and Analysis`, the two P&L statement titles, `Notes to the Standalone Financial Statements`, `Note 32: Exceptional items`.

## Done when
- [ ] The fixture test passes
- [ ] `uv run pytest` passes

## Learn first
- Open a real annual report and look at 5 headings. What makes them look like headings? Would our rule catch them?
