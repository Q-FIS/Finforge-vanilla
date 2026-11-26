"""Step 7: put the retrieved chunks into the prompt, as tagged passages.

Owner: G2        Issue: GEN-05 (issues/GEN-05.md)

Each chunk becomes a passage tagged [C1], [C2], ... so the model can cite
it. The passages must fit in a token budget (cfg.max_tokens); a passage that
does not fit is left out and recorded in Context.dropped, never cut silently.

STUB: every hit goes in, there is no budget, and tokens are counted as words.
"""

from __future__ import annotations

from rag.config import ContextConfig
from rag.schema import Context, Hit, Passage


def build_context(hits: list[Hit], cfg: ContextConfig) -> Context:
    """Turn hits (best first) into the <context> ... </context> text."""
    passages = []
    parts = []
    for number, hit in enumerate(hits, start=1):  # STUB(GEN-05): no budget yet
        tag = f"C{number}"
        safe_text = hit.chunk.text.replace("</context>", "&lt;/context&gt;")
        passages.append(Passage(tag=tag, chunk=hit.chunk, n_tokens=len(hit.chunk.text.split())))
        parts.append(f"[{tag}]\n{safe_text}")

    text = "<context>\n" + "\n\n".join(parts) + "\n</context>"
    return Context(passages=passages, text=text, n_tokens=len(text.split()))
