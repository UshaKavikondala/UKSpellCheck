"""Agent 4: Reporter - collect everything into a final JSON report file.

JOB: Read the issues + telemetry from `state`, write a nice report to disk,
and record where it saved it in `state.report_path`.

Like the Fetcher, this agent uses NO AI. It is pure "gather and format" work.
The reporter is always the LAST agent, because it depends on the output of all
the agents before it.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from ..state import PipelineState
from .base_agent import BaseAgent


class ReporterAgent(BaseAgent):
    name = "reporter"

    def execute(self, state: PipelineState) -> None:
        # Build a plain dictionary (easy to serialize to JSON).
        report = {
            "source": state.input_url or "(raw text input)",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "spelling_issues": [asdict(i) for i in state.spelling_issues],
            "grammar_issues": [asdict(i) for i in state.grammar_issues],
            "summary": {
                "spelling_count": len(state.spelling_issues),
                "grammar_count": len(state.grammar_issues),
            },
            # Telemetry: this is where you SEE token usage per run.
            "token_usage": asdict(state.tokens),
            "agent_statuses": state.agent_statuses,
            "errors": state.errors,
        }

        # Save next to this package in a reports/ folder with a timestamped name.
        reports_dir = Path(__file__).resolve().parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_path = reports_dir / f"report_{stamp}.json"

        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        state.report_path = str(out_path)
