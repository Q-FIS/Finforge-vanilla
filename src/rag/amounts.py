"""Find amounts of money in text, and compare them. Shared by everyone.

Owner: G4        Issue: GEN-08 (issues/GEN-08.md)
Used by: the citation checker (GEN-09) and answer scoring (EVAL-06).

    extract_amounts("Revenue was ₹1,45,000 crore")
    -> [Amount(value=1450000000000.0, unit="INR", raw="₹1,45,000 crore")]

(Called `amounts` and not `numbers`, because `numbers` is a built-in Python
module. See DECISIONS.md D1.)

STUB: no amounts are found.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Amount:
    value: float  # money in plain rupees: ₹1 crore = 10,000,000. Percent and counts as written.
    unit: str  # "INR", "%" or "count"
    raw: str  # the text it came from, e.g. "₹1,45,000 crore"


def extract_amounts(text: str) -> list[Amount]:
    """Every amount in `text`. "(1,234)" is negative; "—" means nil and is
    not an amount."""
    return []  # STUB(GEN-08)


def same_amount(a: Amount, b: Amount) -> bool:
    """True if a and b are the same amount, allowing for rounding."""
    return a.unit == b.unit and a.value == b.value  # STUB(GEN-08): no rounding allowed yet
