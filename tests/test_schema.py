"""F-02: every type that is saved to disk survives a save -> load round trip."""

import json

import pytest

from rag.schema import (
    Answer,
    Block,
    Chunk,
    Citation,
    CitationReport,
    Document,
    Evidence,
    Page,
    Question,
    Result,
    Usage,
    load_jsonl,
    save_jsonl,
)


def make_document() -> Document:
    return Document(
        doc_id="acme_ar_fy2025",
        source_path="data/pdfs/acme_ar_fy2025.pdf",
        pages=[
            Page(
                page=1,
                status="ok",
                blocks=[
                    Block(
                        "Consolidated Statement of Profit and Loss",
                        "heading",
                        (50, 40, 500, 60),
                        14.0,
                        True,
                        0,
                    ),
                    Block(
                        "Revenue from operations ₹1,45,000 crore (1,234) —",
                        "paragraph",
                        (50, 80, 500, 120),
                        9.5,
                    ),
                ],
                label="212",
            ),
            Page(page=2, status="no_text_layer", reason="12 characters"),
        ],
        parse_seconds=1.5,
    )


def make_chunk() -> Chunk:
    return Chunk(
        chunk_id="acme_ar_fy2025:p1:c0000",
        doc_id="acme_ar_fy2025",
        text="Revenue from operations ₹1,45,000 crore",
        page_start=1,
        page_end=1,
        n_tokens=12,
        chunker="section",
        section_path=["Financial Statements", "Consolidated Statement of Profit and Loss"],
        company="acme",
        fy="FY2025",
        basis="consolidated",
    )


def make_question() -> Question:
    return Question(
        id="Q001",
        question="What was Acme's consolidated revenue from operations in FY2025?",
        category="single_fact_table",
        expected_status="answered",
        evidence=[Evidence("acme_ar_fy2025", 1, "Revenue from operations ₹1,45,000 crore")],
        answer_text="₹1,45,000 crore",
        answer_value=1.45e12,
        unit="INR",
        company="acme",
        fy="FY2025",
        basis="consolidated",
    )


def make_result() -> Result:
    return Result(
        question_id="Q001",
        retrieved=[("acme_ar_fy2025:p1:c0000", 0.83), ("acme_ar_fy2025:p2:c0001", 0.61)],
        relevant_ranks=[1],
        evidence_found_at=[1, None],
        context_ids=["acme_ar_fy2025:p1:c0000"],
        dropped_ids=[],
        answer=Answer(
            status="answered",
            text="₹1,45,000 crore [C1]",
            citations=[Citation("C1", "Revenue from operations ₹1,45,000 crore")],
            raw='{"status": "answered"}',
            usage=Usage("fake-llm", "grounded_v1", 900, 40, 12.5, False),
        ),
        status_correct=True,
        correct=True,
        citations=CitationReport(),
    )


@pytest.mark.parametrize(
    ("make", "cls"),
    [
        (make_document, Document),
        (make_chunk, Chunk),
        (make_question, Question),
        (make_result, Result),
    ],
)
def test_round_trip(tmp_path, make, cls):
    original = [make(), make()]
    path = tmp_path / "items.jsonl"
    assert save_jsonl(path, original) == 2
    assert load_jsonl(path, cls) == original


def test_tuples_come_back_as_tuples(tmp_path):
    # JSON has no tuples; without dacite's cast they would come back as lists
    # and Block equality / hashing would quietly change.
    save_jsonl(tmp_path / "d.jsonl", [make_document()])
    doc = load_jsonl(tmp_path / "d.jsonl", Document)[0]
    assert isinstance(doc.pages[0].blocks[0].bbox, tuple)


def test_rupee_sign_is_stored_readably(tmp_path):
    save_jsonl(tmp_path / "c.jsonl", [make_chunk()])
    raw = (tmp_path / "c.jsonl").read_text(encoding="utf-8")
    assert "₹1,45,000" in raw and "\\u20b9" not in raw


def test_value_outside_literal_is_rejected(tmp_path):
    record = json.loads(json.dumps({**make_question().__dict__, "evidence": []}))
    record["expected_status"] = "maybe"
    (tmp_path / "q.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"q\.jsonl:1"):
        load_jsonl(tmp_path / "q.jsonl", Question)


def test_unknown_key_is_rejected(tmp_path):
    record = json.loads(json.dumps({**make_question().__dict__, "evidence": []}))
    record["catgory"] = "typo"
    (tmp_path / "q.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="catgory"):
        load_jsonl(tmp_path / "q.jsonl", Question)


def test_blank_lines_are_skipped(tmp_path):
    path = tmp_path / "c.jsonl"
    save_jsonl(path, [make_chunk()])
    path.write_text(path.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")
    assert len(load_jsonl(path, Chunk)) == 1


def test_page_text_joins_blocks_in_order():
    page = make_document().pages[0]
    assert page.text.startswith("Consolidated Statement")
    assert "\n\nRevenue from operations" in page.text


def test_citation_report_ok():
    assert CitationReport().ok
    assert not CitationReport(unknown_tags=["C9"]).ok
