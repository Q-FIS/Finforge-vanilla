"""Compare two or more runs side by side.

Owner: E2        Issue: EVAL-07 (issues/EVAL-07.md)

    python -m rag.compare eval/runs/baseline eval/runs/fixed_256

STUB: not built yet.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    print("rag.compare is not built yet: issue EVAL-07", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
