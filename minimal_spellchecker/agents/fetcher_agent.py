"""Agent 1: Fetcher - get the text we want to check.

JOB: Put clean text into `state.text_to_check`.

Two input modes:
  * If state.input_text is set -> just use it directly (great for testing).
  * Else if state.input_url is set -> download the page and strip the HTML.

This agent does NOT use the AI. Not every agent needs the model! A big part of
good AI architecture is doing cheap, deterministic work (like downloading and
cleaning text) WITHOUT the model, and saving the expensive model calls for the
parts that actually need intelligence.
"""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from ..state import PipelineState
from .base_agent import BaseAgent


class FetcherAgent(BaseAgent):
    name = "fetcher"

    def execute(self, state: PipelineState) -> None:
        # Mode 1: caller gave us raw text - nothing to download.
        if state.input_text.strip():
            state.text_to_check = state.input_text.strip()
            return

        # Mode 2: caller gave us a URL - download and extract visible text.
        if not state.input_url.strip():
            raise ValueError("No input_text and no input_url provided.")

        response = requests.get(state.input_url, timeout=20)
        response.raise_for_status()  # turn HTTP errors (404, 500...) into exceptions

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove tags whose text we never want to spellcheck (code, scripts...).
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # get_text() flattens the page to plain text; we collapse whitespace.
        text = soup.get_text(separator=" ", strip=True)
        if not text:
            raise ValueError("Fetched the page but found no visible text.")

        state.text_to_check = text
