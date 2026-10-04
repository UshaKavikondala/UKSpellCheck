"""The agents package.

Each agent is a small worker that does exactly ONE job. They all follow the
same contract defined in base_agent.py, which is what makes them composable
(the orchestrator can run them in any order without special-casing each one).
"""
