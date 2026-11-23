"""The permanent fakes that let CI and the skeleton run without models."""

import json

import numpy as np

from rag.gen.llm import FakeLLM
from rag.rep.embed import FakeEmbedder


def test_fake_embedder_unit_rows_and_deterministic():
    emb = FakeEmbedder()
    v = emb.embed(["Revenue from operations", "", "Revenue from operations"], "passage")
    assert v.shape == (3, emb.dim) and v.dtype == np.float32
    assert np.allclose(np.linalg.norm(v, axis=1), 1.0)
    assert np.array_equal(v[0], v[2])


def test_fake_embedder_shared_words_are_closer():
    emb = FakeEmbedder()
    q, near, far = emb.embed(["consolidated revenue", "revenue grew", "monsoon outlook"], "query")
    assert q @ near > q @ far


def test_fake_llm_cites_when_there_is_context():
    text, usage = FakeLLM().complete([{"role": "user", "content": "[C1]\nsome passage"}])
    assert json.loads(text)["status"] == "answered" and usage.model == "fake-llm"
    text, _ = FakeLLM().complete([{"role": "user", "content": "no passages"}])
    assert json.loads(text)["status"] == "insufficient_evidence"


def test_fake_llm_scripted_responses_cycle():
    llm = FakeLLM(responses=["not json", '{"status": "error"}'])
    msgs = [{"role": "user", "content": "x"}]
    assert [llm.complete(msgs)[0] for _ in range(3)] == [
        "not json",
        '{"status": "error"}',
        "not json",
    ]
