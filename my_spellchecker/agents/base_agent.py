from abc import ABC, abstractmethod
from ..state import PipelineState


class BaseAgent(ABC):
    name = "base"

    def run(self, state: PipelineState) -> PipelineState:
        state.statuses[self.name] = "running"
        try:
            self.execute(state)
            state.statuses[self.name] = "done"
        except Exception as exc:
            state.statuses[self.name] = "failed"
            state.errors.append(f"{self.name}: {' '.join(str(exc).split())[:300]}")   # one short line, never a whole HTML page
        return state

    @abstractmethod
    def execute(self, state: PipelineState) -> None:
        ...