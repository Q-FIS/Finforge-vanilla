"""Step 1 of the pipeline: read a PDF and return a Document.

Owner: R1        Issue: REP-01 (issues/REP-01.md)

A Document has one Page per PDF page, and each Page has a list of Blocks
(pieces of text with a position on the page). See rag/schema.py.

STUB: right now this returns one fake page with one fake block, so the rest
of the pipeline can run. Replace the body of parse_pdf() with real code.
"""

from __future__ import annotations

from pathlib import Path

from rag.config import ParseConfig
from rag.schema import Block, Document, Page


def parse_pdf(path: str | Path, doc_id: str, cfg: ParseConfig) -> Document:
    """Read the PDF at `path` and return a Document.

    Rules the real version must follow:
    - one Page for every page of the PDF, even empty or broken ones;
    - a page with fewer than cfg.min_chars_text_layer characters gets
      status "no_text_layer"; a page that crashes gets status "failed";
    - page numbers start at 1.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found (PDFs are named <doc_id>.pdf)")

    # STUB(REP-01): fake output. Replace everything below.
    fake_block = Block(
        text="STUB page text from parse_pdf",
        block_type="paragraph",
        bbox=(0.0, 0.0, 0.0, 0.0),
        font_size=10.0,
    )
    fake_page = Page(page=1, status="ok", blocks=[fake_block])
    return Document(doc_id=doc_id, source_path=str(path), pages=[fake_page])
