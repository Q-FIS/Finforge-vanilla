"""EVAL: compare run folders side by side. Owner E2.

    python -m rag.compare eval/runs/baseline eval/runs/e1_fixed_256

STUB(EVAL-07).
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    print("rag.compare is not built yet: issue EVAL-07", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
