"""Is this the same number? One shared answer for the whole project. Owner G4.

Used by the citation validator (GEN-09) and answer scoring (EVAL-06).
Named `amounts`, not `numbers`: `numbers` is a built-in Python module.

STUB(GEN-08). Today no amounts are found.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Amount:
    value: float  # absolute rupees for money ("₹1,45,000 crore" -> 1.45e12), else as written
    unit: str  # "INR" | "%" | "count"
    raw: str  # the text it was read from


def extract_amounts(text: str) -> list[Amount]:
    """Every amount in `text`: Indian and international grouping, decimals,
    "(1,234)" as negative, ₹ / Rs. / INR, crore / lakh / million / billion, %.
    "—" means nil and is not an amount."""
    return []  # STUB(GEN-08)


def same_amount(a: Amount, b: Amount) -> bool:
    """Equal after unit conversion, allowing for rounding to the precision shown."""
    return a.unit == b.unit and a.value == b.value  # STUB(GEN-08): no rounding tolerance
