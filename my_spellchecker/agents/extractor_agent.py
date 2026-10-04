import re
from bs4 import BeautifulSoup
from ..state import PipelineState
from .base_agent import BaseAgent

NOISE_TAGS = ["script", "style", "noscript", "nav", "footer", "header", "aside", "form"]
TEXT_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]
MIN_WORDS = 3


class ExtractorAgent(BaseAgent):
    name = "extractor"

    def execute(self, state: PipelineState) -> None:
        if not state.raw_html:
            raise ValueError("raw_html is empty")

        soup = BeautifulSoup(state.raw_html, "html.parser")
        for tag in soup(NOISE_TAGS):
            tag.decompose()                          # remove menus, scripts, footers entirely

        seen = set()
        for el in soup.find_all(TEXT_TAGS):
            if el.find_parent(TEXT_TAGS):            # skip text already inside another text tag
                continue
            text = el.get_text(" ", strip=True)
            text = re.sub(r"\s+([,.;:!?%)])", r"\1", text)   # undo spaces get_text added before punctuation
            text = re.sub(r"([(])\s+", r"\1", text)
            if len(text.split()) < MIN_WORDS or text in seen:
                continue
            seen.add(text)
            state.blocks.append(text)

        if not state.blocks:
            raise ValueError("no readable text found")

        state.input_text = "\n\n".join(state.blocks)