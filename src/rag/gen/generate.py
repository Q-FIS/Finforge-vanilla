"""GEN: question + context -> Answer. Owner G3.

STUB(GEN-03, GEN-06, GEN-07). Today: a placeholder prompt, a single
json.loads, no retry.
"""

from __future__ import annotations

import json
from dataclasses import replace

from rag.config import PromptConfig
from rag.gen.llm import LLM
from rag.schema import Answer, Citation, Context


def generate_answer(question: str, context: Context, llm: LLM, cfg: PromptConfig) -> Answer:
    """Render the prompt, call the model, parse its JSON into an Answer.
    Invalid JSON is retried once; a second failure gives status "error"."""
    messages = [  # STUB(GEN-03): the real template lives in gen/prompts/
        {"role": "system", "content": "Answer only from the passages. Return JSON."},
        {"role": "user", "content": f"{context.text}\n\nQuestion: {question}"},
    ]
    raw, usage = llm.complete(messages)
    usage = replace(usage, prompt_version=cfg.template)
    try:  # STUB(GEN-06): no validation, no retry
        data = json.loads(raw)
        return Answer(
            status=data["status"],
            text=data.get("answer", ""),
            citations=[Citation(c["tag"], c.get("quote", "")) for c in data.get("citations", [])],
            raw=raw,
            usage=usage,
        )
    except (ValueError, KeyError, TypeError) as e:
        return Answer(status="error", text="", citations=[], raw=raw, usage=usage, error=str(e))
