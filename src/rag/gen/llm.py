"""Talk to the language model (the LLM).

Owner: G1        Issue: GEN-01 (issues/GEN-01.md)

complete(messages) sends a conversation to the model and returns two
things: the model's reply text, and a Usage record (tokens, time, cost).

FakeLLM is finished and stays forever: tests use it so they never need an
API key. STUB: the real client (Anthropic, model claude-haiku-5-5).
"""

from __future__ import annotations

import json
import time

from rag.config import LLMConfig
from rag.schema import Usage

# A message looks like {"role": "user", "content": "What was revenue?"}.
# role is "system", "user" or "assistant".
Message = dict[str, str]


class LLM:
    """What every LLM client has: a complete() method."""

    def complete(self, messages: list[Message]) -> tuple[str, Usage]:
        raise NotImplementedError


class FakeLLM(LLM):
    """A pretend model that needs no API key.

    By default: if the prompt contains a passage tagged [C1], it "answers"
    and cites [C1]; otherwise it says there is not enough evidence.

    For tests you can give it exact replies to return, one per call:
        FakeLLM(replies=["not json", '{"status": "answered", ...}'])
    """

    def __init__(self, replies: list[str] | None = None) -> None:
        self.replies = replies or []
        self.calls = 0

    def complete(self, messages: list[Message]) -> tuple[str, Usage]:
        start = time.perf_counter()
        prompt = "\n".join(message["content"] for message in messages)

        if self.replies:
            reply = self.replies[self.calls % len(self.replies)]
        elif "[C1]" in prompt:
            reply = json.dumps(
                {
                    "status": "answered",
                    "answer": "Fake answer [C1]",
                    "citations": [{"tag": "C1", "quote": ""}],
                }
            )
        else:
            reply = json.dumps({"status": "insufficient_evidence", "answer": "", "citations": []})
        self.calls += 1

        usage = Usage(
            model="fake-llm",
            prompt_version="",  # generate_answer() fills this in
            tokens_in=len(prompt.split()),
            tokens_out=len(reply.split()),
            latency_ms=(time.perf_counter() - start) * 1000,
            cached=False,
        )
        return reply, usage


def get_llm(cfg: LLMConfig) -> LLM:
    """The LLM client the config asks for."""
    if cfg.fake:
        return FakeLLM()
    # STUB(GEN-01): return the real Anthropic client here.
    raise NotImplementedError("The real LLM client is issue GEN-01. Use llm.fake: true for now.")
