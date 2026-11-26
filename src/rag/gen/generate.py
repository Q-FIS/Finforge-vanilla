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
        if not isinstance(data, dict):
            raise ValueError("LLM reply JSON must be an object")
        status = data["status"]
        if status not in ("answered", "insufficient_evidence", "error"):
            raise ValueError(f"invalid status: {status!r}")
        answer_text = data.get("answer", "")
        if not isinstance(answer_text, str):
            raise ValueError("answer must be a string")
        raw_citations = data["citations"]
        if not isinstance(raw_citations, list):
            raise ValueError("citations must be a list")
        citations = []
        for c in raw_citations:
            if not isinstance(c, dict) or not isinstance(c.get("tag"), str):
                raise ValueError("each citation must be an object with a string 'tag'")
            quote = c.get("quote", "")
            if not isinstance(quote, str):
                raise ValueError("citation 'quote' must be a string")
            citations.append(Citation(tag=c["tag"], quote=quote))
        return Answer(
            status=status,
            text=answer_text,
            citations=citations,
            raw=reply,
            usage=usage,
        )
    except (ValueError, KeyError, TypeError) as error:
        return Answer(
            status="error", text="", citations=[], raw=reply, usage=usage, error=str(error)
        )
