"""The shared state object.

CORE IDEA OF MULTI-AGENT ORCHESTRATION
--------------------------------------
Agents do NOT call each other directly. Instead, they all read from and write
to ONE shared object that is passed along a pipeline. Think of it as a clipboard
that moves from desk to desk: each worker (agent) picks it up, does one small
job, writes the result back on the clipboard, and passes it on.

This single object is the `PipelineState`. Keeping all data in one place makes
the system easy to reason about and easy to debug: at any moment you can print
the state and see exactly what has happened so far.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Issue:
    """One spelling or grammar problem the AI found."""
    word_or_phrase: str          # the text that is wrong
    issue_type: str              # "spelling" or "grammar"
    suggestion: str              # the AI's proposed fix
    reason: str                  # short human-readable explanation


@dataclass
class TokenUsage:
    """Telemetry: how many tokens we spent talking to the model.

    Every LLM call returns a `usage` block. We add it up here so you can SEE
    the cost of your pipeline. Understanding token usage is the first step
    toward architecting efficient AI systems.
    """
    prompt_tokens: int = 0       # tokens we SENT (our text + instructions)
    completion_tokens: int = 0   # tokens the model GENERATED back
    total_tokens: int = 0        # prompt + completion
    api_calls: int = 0           # how many times we hit the model

    def add(self, prompt: int, completion: int) -> None:
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens += prompt + completion
        self.api_calls += 1


@dataclass
class PipelineState:
    """The clipboard passed between every agent.

    Fields start empty and get filled in as agents run. The ORDER of fields
    below roughly matches the order they get populated by the pipeline.
    """
    # --- input (set before the pipeline starts) ---
    input_url: str = ""          # a web page to check (optional)
    input_text: str = ""         # OR raw text to check directly

    # --- filled by the FetcherAgent ---
    text_to_check: str = ""      # the clean text we will spell/grammar check

    # --- filled by the SpellcheckAgent and GrammarAgent ---
    spelling_issues: list[Issue] = field(default_factory=list)
    grammar_issues: list[Issue] = field(default_factory=list)

    # --- filled by the ReporterAgent ---
    report_path: str = ""        # where we saved the final JSON report

    # --- bookkeeping (updated throughout) ---
    tokens: TokenUsage = field(default_factory=TokenUsage)
    agent_statuses: dict[str, str] = field(default_factory=dict)  # name -> status
    errors: list[str] = field(default_factory=list)
