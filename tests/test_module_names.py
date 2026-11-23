"""No file or folder in src/rag may share its name with a built-in Python module.

Why: if someone runs a file directly (`python src/rag/rep/some_file.py`),
Python puts that file's folder first on its import path. A local file called
`types.py`, `numbers.py`, `chunk.py` or `trace.py` would then replace the
built-in module of the same name for *every* library that imports it, and
the crash appears somewhere unrelated. Those four names were in the first
plan; this test keeps them (and any new clash) out.
"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "rag"


def test_no_module_shadows_the_standard_library():
    names = {p.stem for p in SRC.rglob("*.py") if p.stem != "__init__"}
    names |= {p.name for p in SRC.rglob("*") if p.is_dir() and p.name != "__pycache__"}
    clashes = sorted(names & set(sys.stdlib_module_names))
    assert not clashes, f"rename these, they hide built-in Python modules: {clashes}"
