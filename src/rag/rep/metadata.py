"""REP: fill chunk metadata; build the text that gets embedded. Owner R4.

company and fy are real (they only copy from the registry).
STUB(REP-10): basis, and the E2 header in `embedding_text`.
"""

from __future__ import annotations

from rag.config import ChunkConfig
from rag.schema import Chunk, Document, RegistryEntry


def add_metadata(
    chunks: list[Chunk], doc: Document, registry: dict[str, RegistryEntry]
) -> list[Chunk]:
    """company and fy come from the registry, never from the text. basis
    comes from the nearest "Standalone"/"Consolidated" heading."""
    entry = registry[doc.doc_id]
    for c in chunks:
        c.company = entry.company
        c.fy = entry.fy
        # STUB(REP-10): c.basis stays "none"
    return chunks


def embedding_text(chunk: Chunk, cfg: ChunkConfig) -> str:
    """The text sent to the embedder. With cfg.prepend_header it starts with
    "Company · FY · Basis · Section". chunk.text itself is never changed."""
    return chunk.text  # STUB(REP-10)
