"""GEN: the language-model client. Owner G1.

`FakeLLM` is real and permanent: CI, the skeleton and GEN-06's tests use it.
STUB(GEN-01): the real client (DECISIONS.md D3: Anthropic, claude-haiku-5-5,
key in the ANTHROPIC_API_KEY environment variable), with cache and call log.
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from itertools import cycle
from typing import Protocol

from rag.config import LLMConfig
from rag.schema import Usage

Message = dict[str, str]  # {"role": "system" | "user" | "assistant", "content": "..."}


class LLM(Protocol):
    def complete(self, messages: list[Message]) -> tuple[str, Usage]:
        """Return the model's raw text and what the call cost.
        Usage.prompt_version is left "" for the caller to fill in."""
        ...


class FakeLLM:
    """Answers without a model. By default it cites [C1] if the prompt has a
    [C1] passage and abstains otherwise. Pass `responses` to script exact
    outputs (e.g. broken JSON for parser tests); they are returned in turn."""

    model_name = "fake-llm"

    def __init__(self, responses: list[str] | None = None) -> None:
        self._scripted: Iterator[str] | None = cycle(responses) if responses else None

    def complete(self, messages: list[Message]) -> tuple[str, Usage]:
        start = time.perf_counter()
        prompt = "\n".join(m["content"] for m in messages)
        if self._scripted is not None:
            text = next(self._scripted)
        elif "[C1]" in prompt:
            text = json.dumps(
                {
                    "status": "answered",
                    "answer": "Fake answer [C1]",
                    "citations": [{"tag": "C1", "quote": ""}],
                }
            )
        else:
            text = json.dumps({"status": "insufficient_evidence", "answer": "", "citations": []})
        usage = Usage(
            model=self.model_name,
            prompt_version="",
            tokens_in=len(prompt.split()),
            tokens_out=len(text.split()),
            latency_ms=(time.perf_counter() - start) * 1000,
            cached=False,
        )
        return text, usage


def get_llm(cfg: LLMConfig) -> LLM:
    if cfg.fake:
        return FakeLLM()
    raise NotImplementedError(
        f"The real client ({cfg.provider}/{cfg.model}) is issue GEN-01. "
        "Set llm.fake: true until then."
    )
