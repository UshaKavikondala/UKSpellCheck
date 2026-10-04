# Minimal Multi-Agent Spell + Grammar Checker (Learning Project)

A tiny, heavily-commented project that teaches **multi-agent orchestration** by
building the smallest version that is still "real". Once you understand this,
larger multi-agent projects will make sense, because they
use these exact same ideas - just more of them.

---

## 1. The big picture (read this first)

A "multi-agent" system is just **several small workers (agents) that share one
object and run in order**. Nothing more mystical than that.

```
            ┌─────────────── PipelineState (the shared clipboard) ───────────────┐
            │  input_text / input_url, text_to_check, spelling_issues,           │
            │  grammar_issues, token usage, agent_statuses, errors, report_path  │
            └────────────────────────────────────────────────────────────────────┘
                 ▲            ▲             ▲             ▲
                 │ reads/     │ reads/      │ reads/      │ reads/
                 │ writes     │ writes      │ writes      │ writes
            ┌────┴────┐  ┌────┴─────┐  ┌────┴────┐  ┌─────┴─────┐
   URL  ──▶ │ Fetcher │─▶│Spellcheck│─▶│ Grammar │─▶│ Reporter  │──▶  report.json
            └─────────┘  └──────────┘  └─────────┘  └───────────┘
             (no AI)       (AI)          (AI)         (no AI)

                         ▲ The Orchestrator runs these four in order,
                           passing the same state object down the line.
```

Key ideas, in plain words:

| Concept            | What it means here                                              |
|--------------------|----------------------------------------------------------------|
| **Agent**          | A class with one `run(state)` method that does ONE job.        |
| **Shared state**   | One `PipelineState` object every agent reads from / writes to. |
| **Orchestrator**   | Decides the order and passes the state along. Just a loop.     |
| **LLM client**     | The single function that talks to the AI model.               |
| **Telemetry**      | Counting tokens/API calls so you can see the cost.            |

---

## 2. Which files to read, in order

1. [state.py](state.py) - the shared clipboard. Start here.
2. [config.py](config.py) - picks Ollama or Groq.
3. [llm_client.py](llm_client.py) - the one place we call the AI.
4. [agents/base_agent.py](agents/base_agent.py) - the contract every agent follows.
5. [agents/fetcher_agent.py](agents/fetcher_agent.py) - get the text (no AI).
6. [agents/spellcheck_agent.py](agents/spellcheck_agent.py) - first AI agent.
7. [agents/grammar_agent.py](agents/grammar_agent.py) - second AI agent (same pattern).
8. [agents/reporter_agent.py](agents/reporter_agent.py) - save results (no AI).
9. [orchestrator.py](orchestrator.py) - wire them together.
10. [main.py](main.py) - run it.

---

## 3. Why we are NOT using CrewAI / LangChain / AutoGen (yet)

Those are great frameworks, but they **hide the flow** behind abstractions. As a
beginner, you learn far more by writing the ~150 lines of orchestration yourself
first. Many real projects do exactly this - it is hand-written, not a
framework. Once this pattern is second nature, adopting a framework is easy and
you will understand what it is doing for you.

For talking to models, you do **not** need a special library. Both **Ollama**
and **Groq** speak the **OpenAI protocol**, so the plain `openai` Python package
works for both. You only change `base_url`, `api_key`, and `model`
(see [config.py](config.py)). That is also why your retired **GitHub Models**
key was so easy to use and so easy to replace - it was the same protocol.

---

## 4. Setup

```powershell
cd c:\WorkSpace\PracticeSpace\UKAIPractice
pip install -r minimal_spellchecker\requirements.txt
```

### Choose a provider in your `.env` (in the UKAIPractice folder)

**Ollama (local, free):** make sure Ollama is running and you have a model:
```powershell
ollama pull llama3.1
```
Then in `.env`:
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
```

**Groq (cloud):** your `.env` already has `Groq_TOKEN`. Just set:
```
LLM_PROVIDER=groq
GROQ_MODEL=openai/gpt-oss-120b
```

---

## 5. Run it

```powershell
# Built-in sample sentence (easiest first run)
python -m minimal_spellchecker.main

# Your own text
python -m minimal_spellchecker.main --text "I has a speling mistke here."

# A web page
python -m minimal_spellchecker.main --url https://example.com
```

You will see the found issues, a **token-usage telemetry block**, and the path
to a saved JSON report in `reports/`.

---

## 6. Exercises to grow it yourself (your path to the full framework)

Do these in order. Each one teaches one new orchestration concept:

1. **Add a 5th agent.** Write `tone_agent.py` that flags overly-negative
   sentences. Add it to the list in [orchestrator.py](orchestrator.py). Notice
   you changed nothing else - that is the power of the shared contract.
2. **Add conditional routing.** In the orchestrator, skip the GrammarAgent if
   the text is shorter than 5 words. This is your first taste of real
   *orchestration logic* (branching), like real pipelines that pick a route per input.
3. **Add retries.** In `base_agent.py`, wrap `execute()` in a retry loop (try 3
   times before failing).
4. **Chunk long text.** Split big pages into pieces and check each piece, then
   merge results. This introduces parallelism and token budgeting.
5. **Add an AI validator.** Add an agent that double-checks the spellchecker's
   findings to remove false positives - the common "validator" pattern.

When these feel natural, continue with [`my_spellchecker`](../my_spellchecker),
which applies the same ideas to real web pages.
```
