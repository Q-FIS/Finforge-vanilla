"""GEN: hits -> the <context> block of the prompt. Owner G2.

STUB(GEN-05). Today every hit goes in, tokens are counted as words, and
there is no budget.
"""

from __future__ import annotations

from rag.config import ContextConfig
from rag.schema import Context, Hit, Passage


def build_context(hits: list[Hit], cfg: ContextConfig) -> Context:
    """Tag passages [C1], [C2]... in rank order until cfg.max_tokens (LLM
    tokens) is used. A passage that does not fit is dropped and recorded in
    Context.dropped as (chunk_id, "budget"); none is cut silently."""
    passages, blocks = [], []
    for i, hit in enumerate(hits, start=1):  # STUB(GEN-05): no budget, no source line
        tag = f"C{i}"
        passages.append(Passage(tag, hit.chunk, len(hit.chunk.text.split())))
        blocks.append(f"[{tag}]\n{hit.chunk.text}")
    text = "<context>\n" + "\n\n".join(blocks) + "\n</context>"
    return Context(passages=passages, text=text, n_tokens=len(text.split()))
