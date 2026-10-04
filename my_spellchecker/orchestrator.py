from .agents.fetcher_agent import FetcherAgent
from .agents.extractor_agent import ExtractorAgent
from .agents.language_agent import LanguageAgent
from .agents.chunker_agent import ChunkerAgent
from .agents.spellcheck_agent import SpellcheckAgent
from .agents.grammer_agent import GrammerAgent
from .agents.aggregator_agent import AggregatorAgent
from .state import PipelineState


class Orchestrator:
    def __init__(self):
        self.fetch_steps = [FetcherAgent(), ExtractorAgent()]
        self.chunk_steps = [LanguageAgent(), ChunkerAgent()]
        self.check_steps = [SpellcheckAgent(), GrammerAgent()]
        self.aggregator = AggregatorAgent()

    def run(self, state: PipelineState) -> PipelineState:
        steps = (self.fetch_steps if state.url else []) + self.chunk_steps + self.check_steps
        for agent in steps:
            agent.run(state)
            if state.statuses[agent.name] == "failed":
                break                  # later agents depend on earlier output, so stop
        self.aggregator.run(state)     # always runs, so partial results are still reported
        return state