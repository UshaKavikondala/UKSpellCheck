"""Entry point - run the whole pipeline from the command line.

Try it:
    # Check a built-in sample sentence (good first run):
    python -m minimal_spellchecker.main

    # Check your own text:
    python -m minimal_spellchecker.main --text "I has a speling mistke here."

    # Check a web page:
    python -m minimal_spellchecker.main --url https://example.com
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from dotenv import load_dotenv

from .orchestrator import Orchestrator
from .state import PipelineState

# A sentence with deliberate spelling + grammar mistakes, so your first run
# produces visible results even without arguments.
SAMPLE_TEXT = "She go to the libary yesterday and borow three book about histroy."


def main() -> None:
    # Load environment variables. We look for a .env in the UKAIPractice folder
    # (one level up from this package) so your existing keys are picked up.
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    parser = argparse.ArgumentParser(description="Minimal multi-agent spell + grammar checker")
    parser.add_argument("--url", default="", help="Web page URL to check")
    parser.add_argument("--text", default="", help="Raw text to check")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")

    # Build the starting state. If the user gave neither url nor text, use the
    # built-in sample so there is always something to check.
    state = PipelineState(
        input_url=args.url,
        input_text=args.text or ("" if args.url else SAMPLE_TEXT),
    )

    # Hand the state to the orchestrator - this runs every agent in order.
    orchestrator = Orchestrator()
    state = orchestrator.run(state)

    # --- Print a human-friendly summary of what happened ---
    print("\n==================== RESULT ====================")
    print(f"Spelling issues: {len(state.spelling_issues)}")
    for issue in state.spelling_issues:
        print(f"  - '{issue.word_or_phrase}' -> '{issue.suggestion}' ({issue.reason})")

    print(f"Grammar issues: {len(state.grammar_issues)}")
    for issue in state.grammar_issues:
        print(f"  - '{issue.word_or_phrase}' -> '{issue.suggestion}' ({issue.reason})")

    print("\n--- Telemetry (token usage) ---")
    print(f"  API calls        : {state.tokens.api_calls}")
    print(f"  Prompt tokens    : {state.tokens.prompt_tokens}")
    print(f"  Completion tokens: {state.tokens.completion_tokens}")
    print(f"  Total tokens     : {state.tokens.total_tokens}")

    if state.errors:
        print("\n--- Errors ---")
        for err in state.errors:
            print(f"  ! {err}")

    print(f"\nFull report saved to: {state.report_path}")
    print("================================================\n")


if __name__ == "__main__":
    main()
