import argparse
import time
from pathlib import Path

import truststore
from dotenv import load_dotenv

from .orchestrator import Orchestrator
from .reporter import default_report_path, write_excel
from .state import PipelineState

truststore.inject_into_ssl()      # use the Windows certificate store (fixes SSL errors behind a corporate proxy)


def load_urls(urls: list[str], urls_file: str) -> list[str]:
    """Combine --url values and --urls-file lines; skip blanks and # comments; drop duplicates."""
    found = list(urls)
    if urls_file:
        for line in Path(urls_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                found.append(line)
    return list(dict.fromkeys(found))


def print_state(state: PipelineState) -> None:
    if state.url:
        print(f"URL: {state.url} | HTTP: {state.http_status} | "
              f"blocks: {len(state.blocks)} | chars: {len(state.input_text)}")
    print(f"language: {state.page_language} | other-language blocks: {len(state.language_issues)}")
    for i in state.final_issues:
        times = f" x{i.count}" if i.count > 1 else ""
        print(f"[{i.kind}] {i.text} -> {i.suggestion} ({i.reason}){times}")
    print(f"API calls: {state.api_calls} | tokens: {state.total_tokens} | "
          f"seconds: {state.elapsed_seconds:.1f}")
    print("Statuses:", state.statuses, "| Errors:", state.errors)


def main():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    p = argparse.ArgumentParser()
    p.add_argument("--text", default="")
    p.add_argument("--url", action="append", default=[], help="repeat for several URLs")
    p.add_argument("--urls-file", default="", help="text file with one URL per line")
    p.add_argument("--lang", default="", help="force the page language for all URLs, e.g. Dutch")
    p.add_argument("--out", default="", help="Excel report path (default: reports/ folder for URL runs)")
    args = p.parse_args()

    urls = load_urls(args.url, args.urls_file)
    if not urls and not args.text:
        args.text = "She go to the libary and borow three book."

    orchestrator = Orchestrator()
    states: list[PipelineState] = []
    jobs = [PipelineState(url=u, page_language=args.lang.title()) for u in urls]
    if args.text:
        jobs.append(PipelineState(input_text=args.text, page_language=args.lang.title()))

    for n, job in enumerate(jobs, start=1):
        print(f"\n=== {n}/{len(jobs)} {job.url or '(text input)'} ===")
        started = time.perf_counter()
        state = orchestrator.run(job)            # one fresh state per URL, so results never mix
        state.elapsed_seconds = time.perf_counter() - started
        print_state(state)
        states.append(state)

    if urls or args.out:
        path = write_excel(states, Path(args.out) if args.out else default_report_path())
        print(f"\nExcel report: {path}")


if __name__ == "__main__":
    main()