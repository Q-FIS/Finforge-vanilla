# [GEN-08] Find and compare amounts of money in text
labels: team:gen, size:M
**Owner:** G4 · **Size:** M (2-3 days) · **Due:** day 6 · **Needs:** nothing
**Shared file:** the citation checker and answer scoring both use it, so the lead reviews it too.

## In one sentence
`extract_amounts("Revenue was ₹1,45,000 crore")` returns `[Amount(value=1450000000000.0, unit="INR", raw="₹1,45,000 crore")]`.

## What to do
In `src/rag/amounts.py`:
1. Find numbers written in Indian style (`1,45,000`), international style (`145,000`), with decimals (`12.5`), and in brackets (`(1,234)` means **negative**: -1234).
2. Find the unit after the number: crore (x 10,000,000), lakh (x 100,000), million, billion. Money (₹, Rs., INR, or a crore/lakh unit) gets `unit="INR"` and its value in plain rupees.
3. `12.5%` gets `unit="%"` and value 12.5. A number with no unit gets `unit="count"`.
4. `—` means nil: it is **not** an amount.
5. `same_amount(a, b)`: same unit, and the values match after rounding to the precision written (for example, "₹1.45 lakh crore" should equal "₹1,45,000 crore").

## Done when
- [ ] At least 30 tests in `tests/test_amounts.py`, including `"₹1,45,000 crore"`, `"(1,234.5)"`, `"12.5%"`, `"Rs. 3.2 lakh"` and `"—"`
