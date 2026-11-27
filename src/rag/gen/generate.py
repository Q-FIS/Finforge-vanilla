"""Step 8: ask the model the question, with the passages, and read its answer.

Owner: G3        Issues: GEN-06 (parse the answer), GEN-07 (this function)
Prompt text: G1, issue GEN-03

The model must reply with JSON like:
    {"status": "answered", "answer": "₹1,45,000 crore [C1]",
     "citations": [{"tag": "C1", "quote": "Revenue from operations 1,45,000"}]}

STUB: a placeholder prompt, and if the reply is not valid JSON we give up
straight away (the real version retries once).
"""

from __future__ import annotations

import json

from rag.config import PromptConfig
from rag.gen.llm import LLM
from rag.schema import Answer, Citation, Context


def generate_answer(question: str, context: Context, llm: LLM, cfg: PromptConfig) -> Answer:
    """Build the prompt, call the model, and turn its reply into an Answer."""
    messages = [  # STUB(GEN-03): the real prompt will live in gen/prompts/
        {"role": "system", "content": "Answer only from the passages. Reply in JSON."},
        {"role": "user", "content": f"{context.text}\n\nQuestion: {question}"},
    ]
    reply, usage = llm.complete(messages)
    usage.prompt_version = cfg.template

    try:  # STUB(GEN-06): no checking of the JSON, no retry
        data = json.loads(reply)
        citations = [Citation(tag=c["tag"], quote=c.get("quote", "")) for c in data["citations"]]
        return Answer(
            status=data["status"],
            text=data.get("answer", ""),
            citations=citations,
            raw=reply,
            usage=usage,
        )
    except (ValueError, KeyError, TypeError) as error:
        return Answer(
            status="error", text="", citations=[], raw=reply, usage=usage, error=str(error)
        )
