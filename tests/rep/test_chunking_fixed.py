"""Tests for REP-05: fixed-size document chunking."""

from __future__ import annotations

import pytest

from rag.config import ChunkConfig, EmbedConfig
from rag.rep.chunking import chunk_fixed
from rag.rep.tokens import chunk_limit, token_offsets
from rag.schema import Block, Document, Page, PageStatus


def _make_page(page_num: int, text: str, status: PageStatus = "ok") -> Page:
    blocks = (
        [Block(text=text, block_type="paragraph", bbox=(0.0, 0.0, 100.0, 100.0), font_size=10.0)]
        if text
        else []
    )
    return Page(page=page_num, status=status, blocks=blocks)


def _make_doc(pages: list[Page], doc_id: str = "acme_ar_fy2025") -> Document:
    return Document(doc_id=doc_id, source_path=f"{doc_id}.pdf", pages=pages)


def _words(count: int, prefix: str = "w") -> str:
    return " ".join(f"{prefix}{i}" for i in range(count))


@pytest.mark.parametrize("max_tokens", [32, 64, 512])
def test_max_token_count(max_tokens: int) -> None:
    doc = _make_doc([_make_page(1, _words(600))])
    cfg = ChunkConfig(strategy="fixed", max_tokens=max_tokens, overlap_tokens=8)
    embed = EmbedConfig(fake=True)
    limit = min(cfg.max_tokens, chunk_limit(embed.model, embed.passage_prefix))

    chunks = chunk_fixed(doc, cfg, embed)

    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk.n_tokens <= limit
        assert chunk.chunker == "fixed"


def test_exact_overlap() -> None:
    doc = _make_doc([_make_page(1, _words(50))])
    cfg = ChunkConfig(strategy="fixed", max_tokens=20, overlap_tokens=5)
    embed = EmbedConfig(fake=True)

    chunks = chunk_fixed(doc, cfg, embed)

    assert len(chunks) >= 2
    for prev, curr in zip(chunks, chunks[1:], strict=False):
        prev_tokens = [prev.text[s:e] for s, e in token_offsets(prev.text, embed.model)]
        curr_tokens = [curr.text[s:e] for s, e in token_offsets(curr.text, embed.model)]
        assert prev_tokens[-cfg.overlap_tokens :] == curr_tokens[: cfg.overlap_tokens]


def test_exact_source_substring() -> None:
    p1 = "Directors' Report\n\nRevenue grew   12.5% to ₹1,200 crore."
    p2 = "Notes to Accounts — Consolidated   Statement."
    doc = _make_doc([_make_page(1, p1), _make_page(2, p2)])
    full_text = f"{p1}\n\n{p2}"
    cfg = ChunkConfig(strategy="fixed", max_tokens=6, overlap_tokens=2)
    embed = EmbedConfig(fake=True)

    chunks = chunk_fixed(doc, cfg, embed)

    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk.text in full_text


def test_cross_page_chunk() -> None:
    doc = _make_doc(
        [
            _make_page(1, _words(6, prefix="p1_")),
            _make_page(2, _words(8, prefix="p2_")),
        ]
    )
    cfg = ChunkConfig(strategy="fixed", max_tokens=10, overlap_tokens=2)
    embed = EmbedConfig(fake=True)

    chunks = chunk_fixed(doc, cfg, embed)

    assert any(c.page_start == 1 and c.page_end == 2 for c in chunks)


def test_skipped_pages_preserve_original_numbers() -> None:
    doc = _make_doc(
        [
            _make_page(1, _words(6, prefix="p1_")),
            _make_page(2, "ignored failed page", status="failed"),
            _make_page(3, _words(8, prefix="p3_")),
        ]
    )
    cfg = ChunkConfig(strategy="fixed", max_tokens=10, overlap_tokens=2)
    embed = EmbedConfig(fake=True)

    chunks = chunk_fixed(doc, cfg, embed)

    assert any(c.page_start == 1 and c.page_end == 3 for c in chunks)


def test_deterministic_ids() -> None:
    doc = _make_doc([_make_page(1, _words(30)), _make_page(2, _words(30))])
    cfg = ChunkConfig(strategy="fixed", max_tokens=15, overlap_tokens=3)
    embed = EmbedConfig(fake=True)

    first = chunk_fixed(doc, cfg, embed)
    second = chunk_fixed(doc, cfg, embed)

    assert [c.chunk_id for c in first] == [c.chunk_id for c in second]
    assert [c.text for c in first] == [c.text for c in second]


def test_empty_input() -> None:
    cfg = ChunkConfig(strategy="fixed", max_tokens=32, overlap_tokens=4)
    embed = EmbedConfig(fake=True)

    assert chunk_fixed(_make_doc([]), cfg, embed) == []
    assert (
        chunk_fixed(
            _make_doc(
                [
                    _make_page(1, "", status="empty"),
                    _make_page(2, "no text", status="no_text_layer"),
                    _make_page(3, "failed", status="failed"),
                ]
            ),
            cfg,
            embed,
        )
        == []
    )
    assert chunk_fixed(_make_doc([_make_page(1, "   \n  ")]), cfg, embed) == []


def test_single_window_document() -> None:
    text = "Short annual report summary."
    doc = _make_doc([_make_page(1, text)])
    cfg = ChunkConfig(strategy="fixed", max_tokens=32, overlap_tokens=4)
    embed = EmbedConfig(fake=True)

    chunks = chunk_fixed(doc, cfg, embed)

    assert len(chunks) == 1
    assert chunks[0].text == text
    assert chunks[0].page_start == 1
    assert chunks[0].page_end == 1
    assert chunks[0].chunk_id == "acme_ar_fy2025:p1:c0000"


def test_non_positive_step_raises() -> None:
    doc = _make_doc([_make_page(1, _words(20))])
    cfg = ChunkConfig(strategy="fixed", max_tokens=10, overlap_tokens=10)
    embed = EmbedConfig(fake=True)

    with pytest.raises(ValueError):
        chunk_fixed(doc, cfg, embed)


def test_passage_prefix_reduces_effective_limit() -> None:
    doc = _make_doc([_make_page(1, _words(20))])
    cfg = ChunkConfig(strategy="fixed", max_tokens=100, overlap_tokens=1)
    # chunk_limit stub is 510 - count_tokens(prefix); 505-word prefix -> limit = 5
    embed = EmbedConfig(fake=True, passage_prefix=_words(505))

    chunks = chunk_fixed(doc, cfg, embed)

    assert len(chunks) > 1
    assert all(c.n_tokens <= 5 for c in chunks)


def test_zero_overlap() -> None:
    doc = _make_doc([_make_page(1, _words(10))])
    cfg = ChunkConfig(strategy="fixed", max_tokens=4, overlap_tokens=0)
    embed = EmbedConfig(fake=True)

    chunks = chunk_fixed(doc, cfg, embed)

    assert [c.n_tokens for c in chunks] == [4, 4, 2]
