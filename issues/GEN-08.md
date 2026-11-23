# [GEN-08] Find and compare amounts of money in text
labels: team:gen, size:M
**Owner:** G4 · **Size:** M (2-3 days) · **Due:** day 6 · **Needs:** nothing
**This file is shared:** the citation checker (GEN-09) and answer scoring (EVAL-06) both depend on it, so the lead reviews it too.

## What is this, in plain words?
To check that an answer's figure is right (EVAL-06), or that the model didn't
invent it (GEN-09), we need to read amounts out of text and compare them. That's
harder than it looks:
- "₹1,45,000 crore", "Rs. 1.45 lakh crore" and "₹1450 billion" are all the **same** amount;
- "(1,234)" is **minus** 1,234;
- "—" means nil, not a number;
- "12.5%" is a percentage, not money.

## What it must do
```python
extract_amounts("Revenue rose to ₹1,45,000 crore, up 20.8%.")
# -> [Amount(value=1450000000000.0, unit="INR", raw="₹1,45,000 crore"),
#     Amount(value=20.8, unit="%", raw="20.8%")]

extract_amounts("Impairment (1,234) — see note")
# -> [Amount(value=-1234.0, unit="count", raw="(1,234)")]      # the "—" is skipped
```

## Step by step
In `src/rag/amounts.py`:
1. **Find numbers** with a regular expression: optional `(`, optional `₹`/`Rs.`/`INR`, digits with commas and maybe a decimal part, optional `)`, then an optional unit word (crore, lakh, million, billion, cr) or `%`.
2. **Value:** remove the commas (Indian `1,45,000` and international `145,000` both become 145000). Brackets → negative.
3. **Units:**
   - crore → × 10,000,000 · lakh → × 100,000 · million → × 1,000,000 · billion → × 1,000,000,000
   - "lakh crore" → × 1,000,000,000,000 (it happens in big reports)
   - money (a ₹/Rs./INR sign, or a crore/lakh/million/billion unit) → `unit="INR"`, value in plain rupees
   - followed by `%` → `unit="%"`, value as written
   - otherwise → `unit="count"`, value as written
4. **Skip** "—", "-" on its own, and years like "2025" or "FY2025" that sit next to "FY" or "March".
5. **`same_amount(a, b)`:** same unit, and the values match **to the precision written**. "₹1.45 lakh crore" is written to 3 significant figures, so it should equal 1,45,000 crore; "₹1.5 lakh crore" should not. A simple way: round both to the number of significant digits in the less precise `raw`, then compare.

## How to test it
`tests/test_amounts.py`, at least 30 cases: `"₹1,45,000 crore"`, `"Rs. 3.2 lakh"`, `"INR 450 million"`, `"(1,234.5)"`, `"12.5%"`, `"—"`, `"FY2025"` (not an amount), `"1,45,000"` (count), and `same_amount` pairs that should and shouldn't match.

## Done when
- [ ] At least 30 tests pass
- [ ] Two people review the PR, including the lead
- [ ] The `STUB(GEN-08)` lines are gone
