"""Which LLM provider do we talk to, and how?

WHY THIS FILE EXISTS
--------------------
Ollama (running on your laptop) and Groq (a cloud service) BOTH understand the
"OpenAI protocol". That means the same Python code can talk to either one - you
only change three things:

    base_url  : the address of the server
    api_key   : your password (Ollama ignores it, Groq checks it)
    model     : which AI model to use

GitHub Models (the thing you used before it was retired) was ALSO just an
OpenAI-compatible endpoint. So migrating away from it is this small: point
base_url + api_key + model somewhere else. Nothing else in the project changes.

Set LLM_PROVIDER=ollama (default) or LLM_PROVIDER=groq in your .env file.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class LLMConfig:
    provider: str
    base_url: str
    api_key: str
    model: str


def get_llm_config() -> LLMConfig:
    """Build the LLM settings from environment variables.

    Reads from the nearest .env (loaded in main.py). Defaults to Ollama so the
    project runs offline and free out of the box.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    if provider == "ollama":
        # Ollama exposes an OpenAI-compatible server at /v1 on port 11434.
        # The api_key is required by the client library but Ollama ignores it,
        # so we pass a harmless placeholder.
        return LLMConfig(
            provider="ollama",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key="ollama",  # placeholder - not validated by Ollama
            model=os.getenv("OLLAMA_MODEL", "llama3.1"),
        )

    if provider == "groq":
        # Your .env stores the Groq key as `Groq_TOKEN`; we also accept the
        # more conventional `GROQ_API_KEY` as a fallback.
        api_key = os.getenv("Groq_TOKEN") or os.getenv("GROQ_API_KEY") or ""
        if not api_key:
            raise RuntimeError(
                "LLM_PROVIDER=groq but no Groq key found. "
                "Set Groq_TOKEN (or GROQ_API_KEY) in your .env file."
            )
        return LLMConfig(
            provider="groq",
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
            # A current, widely-available Groq model. Override with GROQ_MODEL.
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        )

    raise RuntimeError(
        f"Unknown LLM_PROVIDER='{provider}'. Use 'ollama' or 'groq'."
    )
