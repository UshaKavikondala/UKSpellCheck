"""The ONE place in the whole project where we talk to the AI model.

WHY CENTRALIZE THIS?
--------------------
Every agent that needs the AI calls `chat_json(...)` here. Because there is only
one function that touches the model, you have exactly one place to:
  - switch providers (handled by config.py)
  - count tokens (telemetry)
  - handle errors / retries later
  - log the prompts you send

This is a key architecture habit: isolate the "outside world" (network, model)
behind a single, small, well-understood function.
"""
from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from .config import get_llm_config
from .state import PipelineState


def _get_client() -> tuple[OpenAI, str]:
    """Create an OpenAI-protocol client pointed at our chosen provider.

    The `OpenAI` class is NOT tied to openai.com - it is just an HTTP client
    that speaks the OpenAI protocol. Point its base_url at Ollama or Groq and
    it talks to them instead.
    """
    cfg = get_llm_config()
    client = OpenAI(base_url=cfg.base_url, api_key=cfg.api_key)
    return client, cfg.model


def chat_json(
    system_prompt: str,
    user_prompt: str,
    state: PipelineState,
) -> dict[str, Any]:
    """Send a prompt to the model and get a JSON object back.

    Parameters
    ----------
    system_prompt : the model's "job description" (who it is, rules to follow)
    user_prompt   : the actual request + data for this specific call
    state         : passed in ONLY so we can record token usage (telemetry)

    Returns a Python dict parsed from the model's JSON reply.

    Teaching notes:
      * temperature=0 -> make the model as deterministic as possible. For
        checking/validation tasks you want consistency, not creativity.
      * response_format={"type": "json_object"} -> ask the model to reply with
        valid JSON so we can parse it reliably instead of scraping free text.
    """
    client, model = _get_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    # --- Telemetry: record how many tokens this call cost ---
    usage = response.usage
    if usage is not None:
        state.tokens.add(
            prompt=usage.prompt_tokens or 0,
            completion=usage.completion_tokens or 0,
        )

    # The model's reply text lives at choices[0].message.content
    content = response.choices[0].message.content or "{}"
    return json.loads(content)
