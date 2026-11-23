"""REP: PDF -> Document. Owner R1.

STUB(REP-01). Replace the body of `parse_pdf` with the real PyMuPDF parser.
The fixture tests/fixtures/acme_ar_fy2025.pdf and its .expected.json say
what the real parser must produce.
"""

from __future__ import annotations

from pathlib import Path

from rag.config import ParseConfig
from rag.schema import Block, Document, Page


def parse_pdf(path: str | Path, doc_id: str, cfg: ParseConfig) -> Document:
    """Parse one PDF into a Document with one Page per PDF page.

    Contract: len(doc.pages) == the PDF's page count. A page that has no
    text or fails gets a status and a reason; it is never dropped.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found (expected <pdf_dir>/<doc_id>.pdf)")
    # STUB(REP-01): one fake page with one fake block.
    block = Block("STUB page text from parse_pdf", "paragraph", (0.0, 0.0, 0.0, 0.0), 10.0)
    return Document(doc_id=doc_id, source_path=str(path), pages=[Page(1, "ok", [block])])
