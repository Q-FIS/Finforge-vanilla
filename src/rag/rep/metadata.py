"""Step 4: label each chunk with company, financial year and statement basis.

Owner: R4        Issue: REP-10 (issues/REP-10.md)

company and fy are already done: they are copied from the registry
(data/registry.csv), never guessed from the text.

STUB: basis is always "none", and embedding_text() returns the plain text.
"""

from __future__ import annotations

from rag.config import ChunkConfig
from rag.schema import Chunk, Document, RegistryEntry


def add_metadata(
    chunks: list[Chunk], doc: Document, registry: dict[str, RegistryEntry]
) -> list[Chunk]:
    """Fill chunk.company, chunk.fy and chunk.basis for every chunk."""
    entry = registry[doc.doc_id]
    for chunk in chunks:
        chunk.company = entry.company
        chunk.fy = entry.fy
        # STUB(REP-10): set chunk.basis from the nearest "Standalone" /
        # "Consolidated" heading. It stays "none" for now.
    return chunks


def embedding_text(chunk: Chunk, cfg: ChunkConfig) -> str:
    """The text we give to the embedding model for this chunk.

    When cfg.prepend_header is on, it starts with a line like
    "Infosys · FY2025 · Consolidated · Statement of Profit and Loss".
    chunk.text itself is never changed.
    """
    return chunk.text  # STUB(REP-10): no header yet
