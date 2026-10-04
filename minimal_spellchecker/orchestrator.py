"""The Orchestrator - the conductor of the whole pipeline.

WHAT ORCHESTRATION ACTUALLY IS
------------------------------
An orchestrator does two simple things:
  1. Decides the ORDER agents run in.
  2. Passes the shared `state` from one agent to the next.

That's it. In this minimal version the order is a fixed, straight line:

    Fetcher -> Spellcheck -> Grammar -> Reporter

Because every agent shares the same `run(state)` shape, the orchestrator is just
a `for` loop over a list. Later, "orchestration" gets more interesting when the
order becomes CONDITIONAL (e.g. "if the language is Chinese, skip the package
checker and use a different agent"). That branching logic is exactly what the
that branching logic is what larger orchestrators do - but it starts from this same loop.
"""
from __future__ import annotations

import logging

from .agents.base_agent import BaseAgent
from .agents.fetcher_agent import FetcherAgent
from .agents.grammar_agent import GrammarAgent
from .agents.reporter_agent import ReporterAgent
from .agents.spellcheck_agent import SpellcheckAgent
from .state import PipelineState

log = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self) -> None:
        # The pipeline is just an ordered list of agents. Want to add a step?
        # Write a new agent and drop it into this list - nothing else changes.
        self.pipeline: list[BaseAgent] = [
            FetcherAgent(),
            SpellcheckAgent(),
            GrammarAgent(),
            ReporterAgent(),
        ]

    def run(self, state: PipelineState) -> PipelineState:
        for agent in self.pipeline:
            log.info("Running agent: %s", agent.name)
            state = agent.run(state)

            # If a critical early agent failed, there is no point continuing.
            # (A real system might retry or take an alternate path here.)
            if state.agent_statuses.get(agent.name) == "failed":
                log.error("Agent %s failed: stopping pipeline.", agent.name)
                break

        return state
