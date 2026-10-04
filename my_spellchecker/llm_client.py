import json
import os
from openai import OpenAI
from .state import PipelineState


def _client_and_model():
    provider = os.getenv("LLM_PROVIDER", "ollama")
    if provider == "ollama":
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        return OpenAI(base_url="http://localhost:11434/v1", api_key="ollama"), model
    return (
        OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("Groq_TOKEN")),
        os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    )


def chat_json(system_prompt: str, user_prompt: str, state: PipelineState) -> dict:
    client, model = _client_and_model()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    state.api_calls += 1
    state.total_tokens += resp.usage.total_tokens
    return json.loads(resp.choices[0].message.content)