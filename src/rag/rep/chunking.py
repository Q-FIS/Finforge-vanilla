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

from bisect import bisect_right

from rag.config import ChunkConfig, EmbedConfig
from rag.rep.tokens import chunk_limit, count_tokens, token_offsets
from rag.schema import Chunk, Document


def _page_at(char_pos: int, start_positions: list[int], page_numbers: list[int]) -> int:
    """Return the original page number for a character position in full_text."""
    idx = bisect_right(start_positions, char_pos) - 1
    return page_numbers[idx]


def chunk_document(doc: Document, cfg: ChunkConfig, embed: EmbedConfig) -> list[Chunk]:
    """Run the chunker named in cfg.strategy."""
    if cfg.strategy == "fixed":
        return chunk_fixed(doc, cfg, embed)
    if cfg.strategy == "sentence":
        return chunk_sentences(doc, cfg, embed)
    if cfg.strategy == "section":
        return chunk_sections(doc, cfg, embed)
    raise ValueError(f"unknown chunk strategy: {cfg.strategy!r}")


def chunk_fixed(doc: Document, cfg: ChunkConfig, embed: EmbedConfig) -> list[Chunk]:
    """Windows of cfg.max_tokens tokens, overlapping by cfg.overlap_tokens."""
    parts: list[str] = []
    start_positions: list[int] = []
    page_numbers: list[int] = []
    current_length = 0

    for page in doc.pages:
        if page.status != "ok":
            continue
        page_text = page.text
        if not page_text:
            continue

        if parts:
            parts.append("\n\n")
            current_length += 2

        start_positions.append(current_length)
        page_numbers.append(page.page)
        parts.append(page_text)
        current_length += len(page_text)

    if not parts:
        return []

    full_text = "".join(parts)
    offsets = token_offsets(full_text, embed.model)
    if not offsets:
        return []

    limit = min(cfg.max_tokens, chunk_limit(embed.model, embed.passage_prefix))
    if limit <= 0:
        raise ValueError(f"effective chunk limit must be positive, got {limit}")
    if cfg.overlap_tokens < 0:
        raise ValueError(f"chunk.overlap_tokens must be non-negative, got {cfg.overlap_tokens}")
    step = limit - cfg.overlap_tokens
    if step <= 0:
        raise ValueError(
            f"chunk step must be positive (limit={limit}, overlap_tokens={cfg.overlap_tokens})"
        )

    chunks: list[Chunk] = []
    n_offsets = len(offsets)

    for first in range(0, n_offsets, step):
        last = min(first + limit, n_offsets) - 1
        start_char = offsets[first][0]
        end_char = offsets[last][1]
        chunk_text = full_text[start_char:end_char]

        page_start = _page_at(start_char, start_positions, page_numbers)
        page_end = _page_at(max(start_char, end_char - 1), start_positions, page_numbers)

        chunk = Chunk(
            chunk_id=f"{doc.doc_id}:p{page_start}:c{len(chunks):04d}",
            doc_id=doc.doc_id,
            text=chunk_text,
            page_start=page_start,
            page_end=page_end,
            n_tokens=last - first + 1,
            chunker="fixed",
        )
        chunks.append(chunk)

        if last == n_offsets - 1:
            break

    return chunks


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
