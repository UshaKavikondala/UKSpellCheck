import requests
from ..state import PipelineState
from .base_agent import BaseAgent

HEADERS = {"User-Agent": "my-spellchecker/0.1 (learning project)"}


class FetcherAgent(BaseAgent):
    name = "fetcher"

    def execute(self, state: PipelineState) -> None:
        if not state.url:
            raise ValueError("url is empty")

        resp = requests.get(state.url, headers=HEADERS, timeout=15)
        state.http_status = resp.status_code
        resp.raise_for_status()                      # 404/500 -> exception -> status "failed"

        if "text/html" not in resp.headers.get("Content-Type", ""):
            raise ValueError(f"not an HTML page: {resp.headers.get('Content-Type')}")

        state.raw_html = resp.text