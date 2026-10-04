"""The contract that EVERY agent follows.

THE MOST IMPORTANT CONCEPT IN THIS PROJECT
------------------------------------------
An "agent" here is simply: a class with a single `run(state)` method that takes
the shared PipelineState, does one job, writes its result back into the state,
and returns the state.

Because every agent has the same shape, the orchestrator can treat them all
identically - it just loops over a list of agents and calls `.run(state)` on
each. That uniformity is the whole trick behind orchestration.

We use the "Template Method" pattern:
  * `run()`     lives here in the base class. It handles the BORING bits that
                are identical for every agent: marking status, catching errors.
  * `execute()` is left ABSTRACT. Each real agent fills in only its unique work.

So when you write a new agent, you only implement `execute()`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..state import PipelineState


class BaseAgent(ABC):
    # Every agent gives itself a short name, used for status + logging.
    name: str = "base"

    def run(self, state: PipelineState) -> PipelineState:
        """Run this agent's work with shared bookkeeping around it.

        This method is the SAME for every agent. Notice it:
          1. marks the agent as "running"
          2. calls execute() - the part each agent customizes
          3. marks "done", or records the error and marks "failed"
        """
        state.agent_statuses[self.name] = "running"
        try:
            self.execute(state)
            state.agent_statuses[self.name] = "done"
        except Exception as exc:  # noqa: BLE001 - we want to catch everything here
            state.agent_statuses[self.name] = "failed"
            state.errors.append(f"{self.name}: {exc}")
        return state

    @abstractmethod
    def execute(self, state: PipelineState) -> None:
        """Do this agent's unique work by mutating `state` in place.

        Subclasses MUST implement this. They read what they need from `state`
        and write their output back into `state`. They return nothing - the
        state IS the return value.
        """
        raise NotImplementedError
