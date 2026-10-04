"""Minimal multi-agent spell + grammar checker (learning project).

Read the files in this order to understand the flow:
  1. state.py            - the shared "clipboard" every agent reads/writes
  2. config.py           - which LLM provider (ollama / groq) to use
  3. llm_client.py       - the ONE place we talk to the AI model
  4. agents/base_agent.py- the contract every agent follows
  5. agents/*.py         - each small, single-job worker
  6. orchestrator.py     - wires the agents together in order
  7. main.py             - the entry point you run
"""
