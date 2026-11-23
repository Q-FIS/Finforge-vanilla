"""Step 3: split a cleaned Document into Chunks.

Owners: R2 ("fixed" and "sentence")    Issues: REP-05, REP-06
        R3 ("section")                  Issue:  REP-08

The config's chunk.strategy picks which chunker runs. Each one is a separate
function below, so R2 and R3 can work on the same file without clashing.

Rules every chunker must follow:
- chunk.text is cut out of the cleaned text exactly (never rewritten);
- no chunk has more tokens than chunk_limit(model, passage_prefix);
- the same input always gives the same chunk ids.

STUB: right now every chunker makes one chunk per page.
"""

from __future__ import annotations

from rag.config import ChunkConfig, EmbedConfig
from rag.rep.tokens import count_tokens
from rag.schema import Chunk, Document


def chunk_document(doc: Document, cfg: ChunkConfig, embed: EmbedConfig) -> list[Chunk]:
    """Run the chunker named in cfg.strategy."""
    if cfg.strategy == "fixed":
        return chunk_fixed(doc, cfg, embed)
    if cfg.strategy == "sentence":
        return chunk_sentences(doc, cfg, embed)
    return chunk_sections(doc, cfg, embed)


def chunk_fixed(doc: Document, cfg: ChunkConfig, embed: EmbedConfig) -> list[Chunk]:
    """Windows of cfg.max_tokens tokens, overlapping by cfg.overlap_tokens."""
    return one_chunk_per_page(doc, "fixed", embed)  # STUB(REP-05)


def chunk_sentences(doc: Document, cfg: ChunkConfig, embed: EmbedConfig) -> list[Chunk]:
    """Whole sentences packed up to the limit, never cutting a sentence."""
    return one_chunk_per_page(doc, "sentence", embed)  # STUB(REP-06)


def chunk_sections(doc: Document, cfg: ChunkConfig, embed: EmbedConfig) -> list[Chunk]:
    """A new chunk at every heading; tables are never split."""
    return one_chunk_per_page(doc, "section", embed)  # STUB(REP-08)


def one_chunk_per_page(doc: Document, chunker: str, embed: EmbedConfig) -> list[Chunk]:
    """Placeholder used by the stubs above. Delete it when all three are real."""
    chunks = []
    for page in doc.pages:
        if page.status != "ok" or page.text == "":
            continue
        chunk = Chunk(
            chunk_id=f"{doc.doc_id}:p{page.page}:c{len(chunks):04d}",
            doc_id=doc.doc_id,
            text=page.text,
            page_start=page.page,
            page_end=page.page,
            n_tokens=count_tokens(page.text, embed.model),
            chunker=chunker,
        )
        chunks.append(chunk)
    return chunks
