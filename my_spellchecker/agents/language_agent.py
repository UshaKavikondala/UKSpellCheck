from collections import Counter

from lingua import Language, LanguageDetectorBuilder

from ..config import EXPECTED_LANGUAGES
from ..state import Issue, PipelineState
from .base_agent import BaseAgent

MIN_CHARS = 30   # below this, detection is unreliable, so the block follows the page language

_detector = LanguageDetectorBuilder.from_languages(
    *[getattr(Language, name.upper()) for name in EXPECTED_LANGUAGES]
).build()


def detect(text: str, min_chars: int = MIN_CHARS) -> str | None:
    """Return the language name (e.g. 'Dutch') or None if the text is too short/unclear."""
    if len(text.strip()) < min_chars:
        return None
    lang = _detector.detect_language_of(text)
    return lang.name.title() if lang else None


class LanguageAgent(BaseAgent):
    name = "language"

    def execute(self, state: PipelineState) -> None:
        blocks = state.blocks or [state.input_text]
        if not any(b.strip() for b in blocks):
            raise ValueError("no text to detect language from")

        detected = [detect(b) for b in blocks]

        if not state.page_language:                        # --lang was not given
            weight = Counter()
            for b, lang in zip(blocks, detected):
                if lang:
                    weight[lang] += len(b)                 # longer blocks count more
            state.page_language = (
                weight.most_common(1)[0][0]
                if weight
                else detect(" ".join(blocks), min_chars=0) or "English"
            )

        state.block_langs = [lang or state.page_language for lang in detected]

        for b, lang in zip(blocks, state.block_langs):
            if lang != state.page_language:
                state.language_issues.append(
                    Issue(b[:60], "language", lang,
                          f"text is {lang}, but this page is {state.page_language}")
                )
