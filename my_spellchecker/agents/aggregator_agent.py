from ..state import Issue, PipelineState
from .base_agent import BaseAgent

# When two agents report the same word, the kind that comes first wins.
KIND_PRIORITY = ["spelling", "foreign_word", "grammar", "punctuation", "language"]


class AggregatorAgent(BaseAgent):
    name = "aggregator"

    def execute(self, state: PipelineState) -> None:
        merged: dict[tuple[str, str], Issue] = {}

        for issue in state.spelling_issues + state.grammar_issues + state.language_issues:
            key = (issue.text.lower(), issue.suggestion.lower())
            if key not in merged:
                merged[key] = Issue(issue.text, issue.kind, issue.suggestion,
                                    issue.reason, issue.chunk_index, count=1)
                continue

            kept = merged[key]
            kept.count += 1                                   # same finding seen again
            if KIND_PRIORITY.index(issue.kind) < KIND_PRIORITY.index(kept.kind):
                kept.kind, kept.reason = issue.kind, issue.reason

        state.final_issues = sorted(
            merged.values(),
            key=lambda i: (KIND_PRIORITY.index(i.kind), i.chunk_index),
        )
