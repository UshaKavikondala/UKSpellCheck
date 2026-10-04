from dataclasses import dataclass, field


@dataclass
class Issue:
    text: str          # the wrong word or phrase
    kind: str          # "spelling", "foreign_word", "grammar", "punctuation" or "language"
    suggestion: str
    reason: str
    chunk_index: int = -1     # which chunk the issue was found in
    count: int = 1            # how many times the aggregator merged the same issue


@dataclass
class PipelineState:
    input_text: str = ""
    spelling_issues: list[Issue] = field(default_factory=list)
    grammar_issues: list[Issue] = field(default_factory=list)
    total_tokens: int = 0
    api_calls: int = 0
    statuses: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    url: str = ""
    raw_html: str = ""
    http_status: int | None = None
    blocks: list[str] = field(default_factory=list)
    chunks: list[str] = field(default_factory=list)
    page_language: str = ""                                         # e.g. "Dutch"; set by --lang or LanguageAgent
    block_langs: list[str] = field(default_factory=list)            # detected language per block
    language_issues: list[Issue] = field(default_factory=list)      # blocks not in the page language
    final_issues: list[Issue] = field(default_factory=list)         # merged, de-duplicated list for reporting
    elapsed_seconds: float = 0.0