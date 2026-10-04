import re
from ..config import MAX_CHUNK_CHARS, MAX_CHUNKS
from ..state import PipelineState
from .base_agent import BaseAgent


def split_long(text: str, limit: int) -> list[str]:
    """Split one oversized block on sentence ends, packing sentences up to limit."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    parts, current = [], ""
    for s in sentences:
        if current and len(current) + 1 + len(s) > limit:
            parts.append(current)
            current = s
        else:
            current = f"{current} {s}".strip()
    if current:
        parts.append(current)
    return parts


class ChunkerAgent(BaseAgent):
    name = "chunker"

    def execute(self, state: PipelineState) -> None:
        blocks = state.blocks or [state.input_text]   # --text input has no blocks
        if not any(b.strip() for b in blocks):
            raise ValueError("nothing to chunk")

        # keep only blocks written in the page language; the others are already in language_issues
        langs = state.block_langs or [state.page_language] * len(blocks)
        blocks = [b for b, lang in zip(blocks, langs) if lang == state.page_language]
        if not blocks:
            raise ValueError("no blocks in the page language")

        pieces: list[str] = []
        for b in blocks:
            pieces.extend(split_long(b, MAX_CHUNK_CHARS) if len(b) > MAX_CHUNK_CHARS else [b])

        chunks, current = [], ""
        for piece in pieces:
            if current and len(current) + 1 + len(piece) > MAX_CHUNK_CHARS:
                chunks.append(current)
                current = piece
            else:
                current = f"{current}\n{piece}" if current else piece
        if current:
            chunks.append(current)

        state.chunks = chunks[:MAX_CHUNKS] if MAX_CHUNKS else chunks