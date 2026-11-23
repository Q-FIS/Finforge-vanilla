"""Shared data shapes for the whole pipeline.

Owned by the project lead (see .github/CODEOWNERS). Every team codes
against these classes, so the rules for changing them are strict:

* Add a field only with a default value, so old saved files still load.
* Never rename or remove a field.
* Any change needs the project lead's approval, and a heads-up to every
  team that uses the type.

The pipeline, and the type each stage hands to the next:

    PDF --parse--> Document --clean--> Document --chunk--> list[Chunk]
        --retrieve--> Retrieval (list[Hit]) --build_context--> Context
        --generate--> Answer --score/trace--> Result

Fields marked "filled by <stage>" are left at their default until that
stage runs.

(This file was first called types.py. It was renamed because `types` is
also a built-in Python module; tests/test_module_names.py now stops any
module in this repo from reusing a built-in module's name.)
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal, TypeVar

import dacite

# ---------------------------------------------------------------------------
# Closed sets of values. `Literal` documents them, and `load_jsonl` rejects
# anything outside the set when reading files back in.
# ---------------------------------------------------------------------------

BlockType = Literal["heading", "paragraph", "table", "other"]
PageStatus = Literal["ok", "empty", "no_text_layer", "failed"]
Basis = Literal["standalone", "consolidated", "none"]
Status = Literal["answered", "insufficient_evidence", "error"]
Method = Literal["dense", "tfidf", "oracle"]
ChunkerName = Literal["fixed", "sentence", "section"]
FilterMode = Literal["none", "pre", "post"]
FilterSource = Literal["none", "extracted", "oracle"]
Split = Literal["dev", "test"]
TraceLabel = Literal[
    "",  # the answer was correct
    "PARSE",
    "CHUNK",
    "NOT_RETRIEVED",
    "RANKED_LOW",
    "DROPPED",
    "WRONG_STATUS",
    "GENERATE",
    "BAD_QUESTION",
]

# Question categories (plan doc, Team 4 section). The question checker uses this.
CATEGORIES: tuple[str, ...] = (
    "single_fact_table",
    "single_fact_text",
    "multi_year",
    "statement_basis",
    "period_entity_trap",
    "calculation",
    "unanswerable",
)


# ---------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------


@dataclass
class RegistryEntry:
    """One row of data/registry.csv: one annual report."""

    doc_id: str  # "infosys_ar_fy2025"
    company: str  # company id, lowercase: "infosys"
    company_name: str  # "Infosys Limited"
    aliases: list[str]  # ["Infosys", "Infosys Ltd", "INFY"]
    fy: str  # "FY2025" = April 2024 to March 2025
    url: str
    pages: int
    sha256: str


# ---------------------------------------------------------------------------
# Representation (Team 1)
# ---------------------------------------------------------------------------


@dataclass
class Block:
    """A run of text that PyMuPDF reports as one block on a page."""

    text: str
    block_type: BlockType
    bbox: tuple[float, float, float, float]  # x0, y0, x1, y1 in PDF points
    font_size: float  # largest span size in the block
    bold: bool = False
    order: int = 0  # reading-order position on its page


@dataclass
class Page:
    """One PDF page. Every page of the PDF gets a Page, even a failed one."""

    page: int  # 1-based: the number a PDF viewer shows, NOT the printed number
    status: PageStatus
    blocks: list[Block] = field(default_factory=list)
    reason: str = ""  # why the status is not "ok"
    label: str = ""  # printed page number, if the cleaner found one

    @property
    def text(self) -> str:
        """The page's text, blocks in reading order, separated by blank lines."""
        return "\n\n".join(b.text for b in self.blocks)


@dataclass
class Document:
    """One parsed (and later cleaned) annual report."""

    doc_id: str
    source_path: str
    pages: list[Page]  # len(pages) == the PDF's page count, always
    parse_seconds: float = 0.0


@dataclass
class Chunk:
    """A unit of retrieval. `text` is an exact slice of the cleaned page text:
    it is never rewritten, so evidence quotes can be matched against it."""

    chunk_id: str  # f"{doc_id}:p{page_start}:c{index:04d}"
    doc_id: str
    text: str
    page_start: int
    page_end: int
    n_tokens: int  # counted with the EMBEDDING model's tokenizer, prefix included
    chunker: ChunkerName
    section_path: list[str] = field(default_factory=list)  # heading stack
    is_table: bool = False
    company: str = ""  # filled by add_metadata (from the registry)
    fy: str = ""  # filled by add_metadata (from the registry)
    basis: Basis = "none"  # filled by add_metadata (from the nearest heading)


# ---------------------------------------------------------------------------
# Retrieval (Team 2)
# ---------------------------------------------------------------------------


@dataclass
class Filters:
    """Metadata constraints for one question. None means "don't filter on this"."""

    company: str | None = None
    fy: str | None = None
    basis: Basis | None = None
    source: FilterSource = "none"  # where these values came from


@dataclass
class Hit:
    chunk: Chunk
    score: float
    rank: int  # 1-based
    method: Method


@dataclass
class Retrieval:
    """Everything retrieval did for one question, so the trace can explain it."""

    question: str
    hits: list[Hit]  # `retrieve.depth` long (20) when the index allows
    filters: Filters
    filter_mode: FilterMode
    top_score: float  # 0.0 when there are no hits
    gap: float  # top_score minus the second score; 0.0 with fewer than 2 hits
    latency_ms: float


# ---------------------------------------------------------------------------
# Generation (Team 3)
# ---------------------------------------------------------------------------


@dataclass
class Passage:
    """One retrieved chunk as it appears in the prompt, tagged [C1], [C2], ..."""

    tag: str
    chunk: Chunk
    n_tokens: int  # counted with the LLM's tokenizer (not the embedding one)
    truncated: bool = False


@dataclass
class Context:
    passages: list[Passage]
    text: str  # the rendered <context> ... </context> block
    n_tokens: int
    dropped: list[tuple[str, str]] = field(default_factory=list)  # (chunk_id, reason)


@dataclass
class Citation:
    tag: str  # "C3"
    quote: str  # exact words from that passage


@dataclass
class Usage:
    """What one model call cost. Logged for every answer."""

    model: str
    prompt_version: str  # "grounded_v1"
    tokens_in: int
    tokens_out: int
    latency_ms: float
    cached: bool


@dataclass
class Answer:
    status: Status
    text: str
    citations: list[Citation]
    raw: str  # exactly what the model returned, kept for debugging
    usage: Usage | None = None
    error: str = ""


@dataclass
class CitationReport:
    """Structural citation checks (no LLM). Empty lists mean the check passed."""

    unknown_tags: list[str] = field(default_factory=list)
    failed_quotes: list[Citation] = field(default_factory=list)
    unsupported_numbers: list[str] = field(default_factory=list)
    uncited_sentences: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (
            self.unknown_tags
            or self.failed_quotes
            or self.unsupported_numbers
            or self.uncited_sentences
        )


# ---------------------------------------------------------------------------
# Evaluation (Team 4)
# ---------------------------------------------------------------------------


@dataclass
class Evidence:
    doc_id: str
    page: int  # 1-based viewer number, same convention as Page.page
    quote: str  # copied exactly from the PDF


@dataclass
class Question:
    """One line of eval/questions.jsonl."""

    id: str
    question: str
    category: str  # one of CATEGORIES
    expected_status: Status
    evidence: list[Evidence]  # every place the answer appears in the corpus
    answer_text: str = ""
    answer_value: float | None = None  # absolute rupees, or the % / count
    unit: str = ""  # "INR" | "%" | "count" | ""
    company: str = ""  # gold labels: used by the oracle filter and the trace
    fy: str = ""
    basis: Basis = "none"
    needs_all_evidence: bool = False
    split: Split = "dev"
    author: str = ""
    checked_by: str = ""
    notes: str = ""


@dataclass
class Result:
    """One question in one run: one line of eval/runs/<name>/results.jsonl."""

    question_id: str
    retrieved: list[tuple[str, float]]  # (chunk_id, score), top `depth`
    relevant_ranks: list[int]  # 1-based ranks of relevant chunks
    evidence_found_at: list[int | None]  # per evidence item: best rank, or None
    context_ids: list[str]
    dropped_ids: list[str]
    answer: Answer
    status_correct: bool
    correct: bool | None  # None = waiting for human grading
    citations: CitationReport
    trace_label: TraceLabel = ""


# ---------------------------------------------------------------------------
# Reading and writing JSON Lines (one object per line)
# ---------------------------------------------------------------------------

T = TypeVar("T")

# JSON has no tuples, so tuples come back as lists. `cast=[tuple]` turns them
# back into tuples; `strict=True` rejects keys the class does not have, so a
# typo in a hand-written file fails loudly instead of being ignored.
_DACITE = dacite.Config(cast=[tuple], strict=True)


def to_dict(obj: object) -> dict:
    """A dataclass (with nested dataclasses) as plain dicts and lists."""
    return asdict(obj)  # type: ignore[call-overload]


def from_dict(cls: type[T], data: dict) -> T:
    """Rebuild a dataclass from a dict. Raises on wrong types, unknown keys,
    missing required fields and values outside a Literal set."""
    return dacite.from_dict(data_class=cls, data=data, config=_DACITE)


def save_jsonl(path: str | Path, items: Iterable[object]) -> int:
    """Write dataclasses to `path`, one JSON object per line. Returns the count.

    `ensure_ascii=False` keeps "₹" and "—" readable in the file instead of
    turning them into \\u20b9 escapes.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(to_dict(item), ensure_ascii=False) + "\n")
            n += 1
    return n


def load_jsonl(path: str | Path, cls: type[T]) -> list[T]:
    """Read a .jsonl file back into a list of `cls`. Blank lines are skipped.
    A bad line raises ValueError naming the file and line number."""
    out: list[T] = []
    with Path(path).open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                out.append(from_dict(cls, json.loads(line)))
            except (json.JSONDecodeError, dacite.DaciteError) as e:
                raise ValueError(f"{path}:{lineno}: cannot load {cls.__name__}: {e}") from e
    return out
