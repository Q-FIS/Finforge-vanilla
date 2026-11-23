"""REP: Document -> list[Chunk]. Owners R2 (fixed, sentence), R3 (section).

STUB(REP-05, REP-06, REP-08). Today every page becomes one chunk.
"""

from __future__ import annotations

from rag.config import ChunkConfig
from rag.rep.tokens import count_tokens
from rag.schema import Chunk, Document


def chunk_document(doc: Document, cfg: ChunkConfig, embed_model: str) -> list[Chunk]:
    """Split a cleaned document with the strategy in `cfg.strategy`.

    Contract: chunk.text is an exact substring of the cleaned text;
    n_tokens <= chunk_limit(embed_model, prefix); ids are deterministic.
    """
    chunks = []
    for page in doc.pages:  # STUB: one chunk per page, whatever the strategy
        if page.status != "ok" or not page.text:
            continue
        chunks.append(
            Chunk(
                chunk_id=f"{doc.doc_id}:p{page.page}:c{len(chunks):04d}",
                doc_id=doc.doc_id,
                text=page.text,
                page_start=page.page,
                page_end=page.page,
                n_tokens=count_tokens(page.text, embed_model),
                chunker=cfg.strategy,
            )
        )
    return chunks
