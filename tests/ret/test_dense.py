"""Small, exact examples for dense retrieval."""

import numpy as np
import pytest

from rag.ret.retrieve import DenseIndex
from rag.schema import Chunk


def chunk(number: int) -> Chunk:
    return Chunk(
        chunk_id=f"report:p{number}:c0001",
        doc_id="report",
        text=f"page {number}",
        page_start=number,
        page_end=number,
        n_tokens=2,
        chunker="fixed",
    )


def index() -> DenseIndex:
    chunks = [chunk(1), chunk(2), chunk(3)]
    vectors = np.array([[0.6, 0.8], [1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    return DenseIndex.build(chunks, vectors, "test-model")


def test_search_returns_best_scores_and_ranks():
    hits = index().search(np.array([1.0, 0.0], dtype=np.float32), k=2)
    assert [hit.chunk.chunk_id for hit in hits] == [chunk(2).chunk_id, chunk(1).chunk_id]
    assert [hit.score for hit in hits] == pytest.approx([1.0, 0.6])
    assert [hit.rank for hit in hits] == [1, 2]
    assert [hit.method for hit in hits] == ["dense", "dense"]


def test_empty_index_and_large_or_nonpositive_k():
    empty = DenseIndex.build([], np.empty((0, 2), dtype=np.float32), "test-model")
    query = np.array([1.0, 0.0], dtype=np.float32)
    assert empty.search(query, k=3) == []
    assert len(index().search(query, k=10)) == 3
    assert index().search(query, k=0) == []


def test_ties_use_smaller_chunk_index_even_at_cutoff():
    chunks = [chunk(i) for i in range(1, 5)]
    vectors = np.array([[1, 0], [0, 1], [1, 0], [1, 0]], dtype=np.float32)
    dense = DenseIndex.build(chunks, vectors, "test-model")
    hits = dense.search(np.array([1, 0], dtype=np.float32), k=2)
    assert [hit.chunk.chunk_id for hit in hits] == [chunks[0].chunk_id, chunks[2].chunk_id]


def test_allowed_hides_chunks_before_top_k():
    hits = index().search(
        np.array([1.0, 0.0], dtype=np.float32),
        k=3,
        allowed=np.array([True, False, False]),
    )
    assert [hit.chunk.chunk_id for hit in hits] == [chunk(1).chunk_id]
    assert [hit.rank for hit in hits] == [1]


def test_wrong_query_length_and_vector_count():
    with pytest.raises(ValueError, match="query has 256 numbers, index has 2"):
        index().search(np.zeros(256, dtype=np.float32), k=1)
    with pytest.raises(ValueError, match="3 chunks but 2 vectors"):
        DenseIndex.build([chunk(1), chunk(2), chunk(3)], np.zeros((2, 2)), "test-model")


def test_save_load_keeps_chunks_vectors_and_model(tmp_path):
    original = index()
    original.save(tmp_path / "index")
    loaded = DenseIndex.load(tmp_path / "index")
    assert loaded.model_name == "test-model"
    assert loaded.chunks == original.chunks
    np.testing.assert_array_equal(loaded.vectors, original.vectors)
    query = np.array([1.0, 0.0], dtype=np.float32)
    assert loaded.search(query, k=3) == original.search(query, k=3)
