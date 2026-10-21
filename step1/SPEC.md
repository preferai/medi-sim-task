# Project Plan

## Overview
Step 1 of Engineering Case Challenge 1: a PoC script that reads conference programme URLs from `data/source.csv`, crawls each programme page with Crawl4AI, extracts research papers (title, paper ID, author, affiliation, country, abstract URL, extra URL) with PydanticAI and a local Ollama model (`gemma4b:12b-mlx`), and writes `data/output/<short-name>.jsonl`. Output is checked against a hand-verified ground truth of 3 EACR 2026 papers. Only the programme page is scraped; abstract pages and PDFs are out of scope.

**Reference:** `PRD.md` (inputs: `TASK_ECC_1.md`, `SIMPLE_SOLUTION_STEP_1.md`)

---

## Task List

```json
[
  {
    "category": "setup",
    "id": "US-1",
    "title": "Create `step1/` skeleton and `data/source.csv`",
    "description": "As a developer, I want the folder layout and the conference source file in place so that the scraper and later steps have a stable location for inputs and outputs.",
    "steps": [
      "Create `step1/` with `pyproject.toml` managed by `uv`; `uv sync` succeeds from `step1/`",
      "Declare dependencies `crawl4ai`, `pydantic-ai` (with Ollama/OpenAI-compatible support), `pydantic`; declare dev tools `ruff` and `ty`",
      "Create `data/source.csv` next to `step1/` with header `short_name,url`",
      "Ensure `short_name` values are lowercase, use dashes, and contain no whitespace (regex `^[a-z0-9]+(-[a-z0-9]+)*$`)",
      "Add exactly one data row: `eacr-2026,https://dashboard.eacr.org/eacr26/program/08-jun` (tracking query parameters such as `_gl=` removed)",
      "Create `data/output/` directory (a `.gitkeep` or runtime creation is acceptable)",
      "`ruff format --check` and `ruff check` pass",
      "Typecheck passes (`ty check`)"
    ],
    "passes": false
  },
  {
    "category": "setup",
    "id": "US-2",
    "title": "Define the paper record schema and JSONL output",
    "description": "As a developer, I want one Pydantic model describing a paper so that extraction output and verification use the same typed structure.",
    "steps": [
      "Create `Paper` Pydantic model with fields in this order: `title: str`, `paper_id: str | None`, `author: str | None`, `affiliation: str | None`, `country: str | None`, `abstract_url: str | None`, `extra_url: str | None`",
      "Implement a function that writes a list of `Paper` objects to a path as JSONL (one JSON object per line, UTF-8, `null` for missing values, key order as above)",
      "Create the parent directory if it is missing",
      "Overwrite the file on re-run (no duplicate appends)",
      "Add type hints on all public functions",
      "Verify by running the writer twice on a sample list and confirming the file has one line per paper",
      "`ruff format --check` and `ruff check` pass",
      "Typecheck passes (`ty check`)"
    ],
    "passes": false
  },
  {
    "category": "feature",
    "id": "US-3",
    "title": "Fetch programme page content with Crawl4AI",
    "description": "As a developer, I want a function that takes a programme URL and returns the page content as text/markdown so that the LLM can extract papers from it.",
    "steps": [
      "Implement an async crawl function using `AsyncWebCrawler` from `crawl4ai`",
      "Return the rendered page content (markdown) as a string for the EACR 2026 URL",
      "Wait for JavaScript-rendered content (the dashboard is a JS app); add a short comment only if a wait condition or selector is needed",
      "Raise a clear error if the crawl fails or returns empty content",
      "Preserve abstract URLs and other links in the returned content (not stripped)",
      "Verify by crawling the EACR 2026 URL and confirming the returned markdown contains the title `Intestinal zonation constrains driver mutation selection`",
      "`ruff format --check` and `ruff check` pass",
      "Typecheck passes (`ty check`)"
    ],
    "passes": false
  },
  {
    "category": "feature",
    "id": "US-4",
    "title": "Extract papers from page content with PydanticAI and Ollama",
    "description": "As a developer, I want a function that turns page content into a list of `Paper` objects using the local Ollama model so that we get structured data without hand-written parsers.",
    "steps": [
      "Create a PydanticAI `Agent` with `output_type=list[Paper]` against the local Ollama server (default `http://localhost:11434/v1`)",
      "Default the model name to `gemma4b:12b-mlx` and make it overridable (CLI flag or env var)",
      "Write a system prompt that instructs: extract only research papers; use `null` for any field not present in the text; never invent values; copy URLs verbatim",
      "Handle page content larger than the model context by chunking and concatenating results; if not implemented, document the limit in the README",
      "Validate output against `Paper` and log validation failures (do not swallow them silently)",
      "Merge duplicate papers (same normalized title and author) into one record, keeping non-null values",
      "Verify by running extraction on the crawled EACR content and confirming a non-empty list of `Paper` objects",
      "`ruff format --check` and `ruff check` pass",
      "Typecheck passes (`ty check`)"
    ],
    "passes": false
  },
  {
    "category": "feature",
    "id": "US-5",
    "title": "Wire crawl, extract and write for every source row",
    "description": "As a researcher, I want to run one command that processes all conferences in `source.csv` so that I get one JSONL file per conference.",
    "steps": [
      "Create entry point `step1/scrape.py`, runnable as `uv run python scrape.py` from `step1/`",
      "Read `data/source.csv` with paths resolved relative to the repo root, not the current working directory",
      "For each row, run crawl, extract and write to `data/output/<short_name>.jsonl`",
      "Log and isolate a failure on one conference so the others still run; exit non-zero if any conference failed",
      "Log per conference: URL, number of papers extracted, output path",
      "Verify that running it for the EACR row produces a non-empty `data/output/eacr-2026.jsonl`",
      "`ruff format --check` and `ruff check` pass",
      "Typecheck passes (`ty check`)"
    ],
    "passes": false
  },
  {
    "category": "testing",
    "id": "US-6",
    "title": "Hand-verified ground truth and comparison script",
    "description": "As a researcher, I want to compare scraper output to hand-verified records so that I can judge quickly whether the approach is working before scaling.",
    "steps": [
      "Create `data/ground_truth/eacr-2026.jsonl` with the 3 reference papers in the `Paper` schema, using the values from PRD Section 8 (paper 1 ID `EACR26-1448`, paper 2 ID `EACR26-0547`, paper 3 ID `null`)",
      "Create entry point `step1/verify.py` taking a conference short name, runnable as `uv run python verify.py eacr-2026` from `step1/`",
      "Compare `data/output/<short-name>.jsonl` with `data/ground_truth/<short-name>.jsonl`",
      "Match papers by normalized title (lowercased, whitespace and punctuation collapsed)",
      "Report per ground-truth paper: found / not found",
      "Report per field: match / mismatch / expected-null-got-value (hallucination)",
      "Compare `extra_url` and report it, but exclude it from pass/fail",
      "Print a summary line: papers found out of 3, fields matched out of total compared",
      "Exit non-zero if any ground-truth paper is not found",
      "`ruff format --check` and `ruff check` pass",
      "Typecheck passes (`ty check`)"
    ],
    "passes": false
  },
  {
    "category": "docs",
    "id": "US-7",
    "title": "Write a concise `step1/README.md`",
    "description": "As a collaborator, I want a short README so that I can run the script and know what it needs and produces.",
    "steps": [
      "Keep the README to roughly one screen",
      "State prerequisites: `uv`, Ollama running locally with `gemma4b:12b-mlx` available, Crawl4AI browser setup (e.g. `crawl4ai-setup`) if required",
      "State the run commands for scraping and for verification",
      "State inputs (`data/source.csv`) and outputs (`data/output/<short-name>.jsonl`, `data/ground_truth/`)",
      "List the JSONL fields",
      "Execute every command in the README once and confirm it works",
      "Typecheck passes (`ty check`)"
    ],
    "passes": false
  }
]
```

---

## Notes

All commands run from `step1/`. No `pytest` suite (explicit non-goal); `verify.py` is a data check against ground truth, not a test suite.

**Linting:**
```bash
uv run ruff format --check . && uv run ruff check .
```

**Type checking:**
```bash
uv run ty check
```

**Tests:**
```bash
# None in step 1. Data check against ground truth:
uv run python verify.py eacr-2026
```

**Run:**
```bash
# Prerequisites: Ollama running with gemma4b:12b-mlx; `uv run crawl4ai-setup` once
uv run python scrape.py
```

**Constraints:**
- Python with `uv` only; format with `ruff`, type-check with `ty`.
- Follow DRY, no dead code, no overengineering, short comments only.
- Do not fetch abstract pages or PDFs; do not add classification, DB, UI, or multi-page crawling.
- If the Crawl4AI result is incomplete because of the JS app, stop and raise it with the user before changing approach (PRD risk R-1).
