# PRD: Step 1 – Conference Programme Scraper (PoC)

## 1. Introduction/Overview

Engineering Case Challenge 1 (see `TASK_ECC_1.md`) asks for an automated content classification pipeline for conference, institution and KOL content. Metadata such as title, affiliation and country is inconsistent and currently collected manually.

Step 1 builds the first, smallest piece: a script that reads a list of conference programme pages and extracts research papers into structured JSONL. Only the programme page is scraped. Abstract pages and PDFs are not fetched.

Before scaling, the output is checked against a small hand-verified ground-truth set of 3 papers from the EACR 2026 programme (`SIMPLE_SOLUTION_STEP_1.md`). This gives early confidence that the approach works. It also covers three different data-availability cases: PDF found, abstract only, and neither.

Stack: Python with `uv`, Crawl4AI (`AsyncWebCrawler`) for crawling, PydanticAI for structured extraction, and a local Ollama model (`gemma4b:12b-mlx`, already running and downloaded) for the LLM.

## 2. Goals

- G-1: Provide `data/source.csv` listing conference sources, seeded with the EACR 2026 programme page.
- G-2: Provide a script in `step1/` that, for every row in `source.csv`, crawls the programme page and writes `data/output/<short-name>.jsonl` with one JSON object per paper.
- G-3: Each record has exactly these fields: paper title, paper ID, author, affiliation, country, abstract URL, extra URL. Fields not present on the page are `null`.
- G-4: Provide a hand-verified ground-truth file and a verification script that reports, per field, whether the extracted output matches it for the 3 reference papers.
- G-5: Keep the setup minimal. The `step1/` folder is self-contained (`uv`, `pyproject.toml`, short `README.md`), and `data/` is shared across future steps.

## 3. Research Questions / Hypotheses

- **H-1:** A small local LLM (`gemma4b:12b-mlx`) with schema-constrained output can extract title, author, affiliation and abstract URL from the EACR programme page well enough to find all 3 reference papers.
- **H-2:** Fields that are not on the programme page (e.g. country, ID, extra URL) are returned as `null` and not hallucinated.

## 4. User Stories

### US-1: Repository layout and source file
- **Title:** Create `step1/` skeleton and `data/source.csv`
- **Priority:** P0 (Critical)
- **Description:** "As a developer, I want the folder layout and the conference source file in place so that the scraper and later steps have a stable location for inputs and outputs."
- **Acceptance Criteria:**
    - [ ] `step1/` exists with `pyproject.toml` managed by `uv` (`uv sync` succeeds from `step1/`)
    - [ ] Dependencies declared: `crawl4ai`, `pydantic-ai` (with Ollama/OpenAI-compatible support), `pydantic`; dev tools `ruff`, `ty`
    - [ ] `data/source.csv` exists next to `step1/` with header `short_name,url`
    - [ ] `short_name` values are lowercase, use dashes, contain no whitespace
    - [ ] File contains exactly one data row: `eacr-2026,https://dashboard.eacr.org/eacr26/program/08-jun` (tracking query parameters such as `_gl=` removed)
    - [ ] `data/output/` directory exists (can be created at runtime)
    - [ ] Code follows project style/linting rules (`ruff format`, `ruff check`, `ty check` pass)

### US-2: Paper schema and JSONL writer
- **Title:** Define the paper record schema and JSONL output
- **Priority:** P0 (Critical)
- **Description:** "As a developer, I want one Pydantic model describing a paper so that extraction output and verification use the same typed structure."
- **Acceptance Criteria:**
    - [ ] A `Paper` Pydantic model with fields: `title: str`, `paper_id: str | None`, `author: str | None`, `affiliation: str | None`, `country: str | None`, `abstract_url: str | None`, `extra_url: str | None`
    - [ ] A function writes a list of `Paper` objects to a path as JSONL (one JSON object per line, UTF-8, `null` for missing values, key order as above)
    - [ ] Parent directory is created if missing
    - [ ] Re-running overwrites the file (no duplicate appends)
    - [ ] Type hints on all public functions; `ruff` and `ty` pass

### US-3: Crawl a programme page
- **Title:** Fetch programme page content with Crawl4AI
- **Priority:** P0 (Critical)
- **Description:** "As a developer, I want a function that takes a programme URL and returns the page content as text/markdown so that the LLM can extract papers from it."
- **Acceptance Criteria:**
    - [ ] Uses `AsyncWebCrawler` from `crawl4ai`
    - [ ] Returns the rendered page content (markdown) as a string for the EACR 2026 URL
    - [ ] Waits for JavaScript-rendered content (the dashboard is a JS app); behavior documented in a short comment if a wait/selector is needed
    - [ ] Raises a clear error if the crawl fails or returns empty content
    - [ ] Abstract URLs and other links on the page are preserved in the returned content (not stripped), so the LLM can copy them
    - [ ] `ruff` and `ty` pass

### US-4: LLM extraction of papers
- **Title:** Extract papers from page content with PydanticAI and Ollama
- **Priority:** P0 (Critical)
- **Description:** "As a developer, I want a function that turns page content into a list of `Paper` objects using the local Ollama model so that we get structured data without hand-written parsers."
- **Acceptance Criteria:**
    - [ ] Uses a PydanticAI `Agent` with `output_type=list[Paper]` against the local Ollama server (default `http://localhost:11434/v1`)
    - [ ] Model name defaults to `gemma4b:12b-mlx` and is overridable (CLI flag or env var)
    - [ ] System prompt instructs: extract only research papers; use `null` for any field not present in the text; never invent values; copy URLs verbatim
    - [ ] Page content larger than the model context is handled (chunked, with results concatenated), or the limit is documented in the README
    - [ ] Output is validated against `Paper`; validation failures are logged (not silently swallowed)
    - [ ] Duplicate papers (same normalized title and author) are merged into one record
    - [ ] `ruff` and `ty` pass

### US-5: End-to-end script
- **Title:** Wire crawl → extract → write for every source row
- **Priority:** P0 (Critical)
- **Description:** "As a researcher, I want to run one command that processes all conferences in `source.csv` so that I get one JSONL file per conference."
- **Acceptance Criteria:**
    - [ ] Runnable as `uv run python -m step1...` or `uv run step1/<script>.py` (exact command documented in README)
    - [ ] Reads `data/source.csv`, resolves paths relative to the repo root, not the current working directory
    - [ ] For each row, writes `data/output/<short_name>.jsonl`
    - [ ] A failure on one conference is logged and does not stop the others; the process exits non-zero if any conference failed
    - [ ] Logs per conference: URL, number of papers extracted, output path
    - [ ] Running it for the EACR row produces a non-empty `data/output/eacr-2026.jsonl`
    - [ ] `ruff` and `ty` pass

### US-6: Ground truth and verification
- **Title:** Hand-verified ground truth and comparison script
- **Priority:** P1 (High)
- **Description:** "As a researcher, I want to compare scraper output to hand-verified records so that I can judge quickly whether the approach is working before scaling."
- **Acceptance Criteria:**
    - [ ] `data/ground_truth/eacr-2026.jsonl` contains the 3 reference papers using the `Paper` schema, with values taken from `SIMPLE_SOLUTION_STEP_1.md` (see Section 8 for the records)
    - [ ] A verification script takes a conference short name and compares `data/output/<short-name>.jsonl` with `data/ground_truth/<short-name>.jsonl`
    - [ ] Papers are matched by normalized title (lowercased, whitespace and punctuation collapsed)
    - [ ] Output reports, per ground-truth paper: found / not found, and per field: match / mismatch / expected-null-got-value (hallucination)
    - [ ] Summary line: papers found out of 3, fields matched out of total compared
    - [ ] Exit code is non-zero if any ground-truth paper is not found
    - [ ] `ruff` and `ty` pass

### US-7: README
- **Title:** Write a concise `step1/README.md`
- **Priority:** P2 (Medium)
- **Description:** "As a collaborator, I want a short README so that I can run the script and know what it needs and produces."
- **Acceptance Criteria:**
    - [ ] Fits on roughly one screen
    - [ ] States prerequisites: `uv`, Ollama running locally with `gemma4b:12b-mlx` available, Crawl4AI browser setup step (e.g. `crawl4ai-setup`) if required
    - [ ] States the run command for scraping and for verification
    - [ ] States inputs (`data/source.csv`) and outputs (`data/output/<short-name>.jsonl`, `data/ground_truth/`)
    - [ ] Lists the JSONL fields
    - [ ] Commands in the README have been executed once and work

## 5. Functional Requirements

- FR-1: `data/source.csv` has columns `short_name,url`; `short_name` matches `^[a-z0-9]+(-[a-z0-9]+)*$`.
- FR-2: The script processes every row of `source.csv` independently.
- FR-3: The page is crawled with Crawl4AI `AsyncWebCrawler`.
- FR-4: Extraction uses PydanticAI against a local Ollama model; default model `gemma4b:12b-mlx`, overridable.
- FR-5: Output record fields: `title`, `paper_id`, `author`, `affiliation`, `country`, `abstract_url`, `extra_url`. Missing values are `null`.
- FR-6: Output is written to `data/output/<short_name>.jsonl`, one object per line, overwritten on each run.
- FR-7: The LLM must not fabricate field values; absent information is `null`.
- FR-8: Duplicate papers within one conference are merged.
- FR-9: Errors per conference are logged and isolated; the exit code reflects any failure.
- FR-10: Ground truth lives in `data/ground_truth/<short_name>.jsonl` and uses the same schema.
- FR-11: The verification script reports found/not-found per paper and match/mismatch per field.
- FR-12: All Python code passes `ruff format`, `ruff check` and `ty check`, and is managed with `uv`.

## 6. Non-Goals (Out of Scope)

- No fetching of abstract pages or PDFs (a later step).
- No `pytest` suite. The verification script is a data check, not a unit-test suite.
- No metadata classification (specialty, sub-specialty, drug mentions, KOL linking).
- No multi-day or multi-page crawling beyond the single URL in `source.csv`.
- No model comparison, prompt tuning, or accuracy targets beyond the 3-paper check.
- No human-in-the-loop UI, database, scheduling, deployment or monitoring.
- No automatic discovery of conferences.
- No authentication handling for gated pages.

## 7. Dependencies & Risks

**Dependencies:**
- Python and `uv`
- `crawl4ai` (needs Playwright browsers installed via its setup command)
- `pydantic-ai`, `pydantic`
- Ollama running locally with `gemma4b:12b-mlx` available
- Network access to `dashboard.eacr.org`
- `ruff`, `ty`

**Risks & Mitigations:**
- **R-1:** The programme page is a JS app, so Crawl4AI may return incomplete content. *Mitigation:* configure a wait condition or selector. If it still fails, inspect network calls for a JSON endpoint (to be raised with the user before changing approach).
- **R-2:** The page is larger than the model context. *Mitigation:* chunk the content and merge results (US-4), or document the limit.
- **R-3:** A small model may miss papers or hallucinate fields. *Mitigation:* the strict "null if absent" prompt, plus the verification script flags hallucinations explicitly (H-2).
- **R-4:** The programme page may not contain authors, affiliations or countries. *Mitigation:* the ground truth and verification treat unavailable fields as an expected `null`, not a failure (see Open Questions 2 and 3).
- **R-5:** The ground truth was gathered by hand and may contain errors or ambiguities (see Open Question 1). *Mitigation:* review it once against the live page before relying on results.
- **R-6:** The model tag `gemma4b:12b-mlx` is non-standard. *Mitigation:* the model name is a configuration value, and the user confirmed it is available locally.

## 8. Technical Considerations

- **Folder layout:**
  ```
  data/
    source.csv
    ground_truth/eacr-2026.jsonl
    output/eacr-2026.jsonl        (generated)
  step1/
    pyproject.toml
    README.md
    <scraper and verification modules>
  ```
- Ollama exposes an OpenAI-compatible API at `http://localhost:11434/v1`; PydanticAI connects through its Ollama/OpenAI provider.
- Keep the code simple: schema, crawl, extract, write and verify functions with no abstractions beyond that (DRY, no dead code).
- **Ground-truth records** (from `SIMPLE_SOLUTION_STEP_1.md`):

  | Field | Paper 1 | Paper 2 | Paper 3 |
  |---|---|---|---|
  | title | Stromal β3-integrin signature predicting recurrence in Oncotype DX low-risk breast cancer | Intestinal zonation constrains driver mutation selection and shapes tumour evolution in colorectal cancer | Plasma Proteomics and AI: Redefining Precision Oncology |
  | paper_id | `EACR26-1448` (taken from the abstract URL; blank in source) | `EACR26-0547` | `null` |
  | author | Alex Jordan | Raheleh Amirkhah | Yehonatan Elon |
  | affiliation | Barts Cancer Institute | Queen's University Belfast | OncoHost |
  | country | United Kingdom | United Kingdom | Israel |
  | abstract_url | `https://storage.unitedwebnetwork.com/files/991/abstract/2026/EACR26-1448.htm` | `https://storage.unitedwebnetwork.com/files/991/abstract/2026/EACR26-0547.htm` | `null` |
  | extra_url | `https://www.biorxiv.org/content/biorxiv/early/2026/09/16/2026.09.10.750700.full.pdf` | `null` | `https://emea.illumina.com/events/conferences/2026/EACR2026.html` |

## 9. Success Metrics

- `uv run` of the script completes for the EACR row and produces a non-empty `data/output/eacr-2026.jsonl`.
- Verification finds 3 of 3 reference papers by title.
- For the fields available on the programme page, match rate is reported. The PoC needs no fixed threshold, but any hallucinated value for an expected-null field is listed.
- `ruff format --check`, `ruff check` and `ty check` report no errors.
- A new reader can run the PoC from `step1/README.md` alone.

## 10. Open Questions

Defaults used while writing this PRD are marked **(default)**. Please confirm or correct them.

1. **(default)** Paper 1 appears twice in `SIMPLE_SOLUTION_STEP_1.md`; I treated it as one paper and merged both entries.
2. **(default)** Verification compares `title`, `paper_id`, `author`, `affiliation`, `country` and `abstract_url`. `extra_url` is compared and reported but doesn't affect pass/fail, because it was found by hand (Google Scholar, Illumina page) and may not be on the programme page. Is that right?
3. Which ground-truth fields does the programme page actually contain? This is unknown until the first crawl. Fields it lacks (e.g. country) may need to be marked "not expected from programme page" in the ground truth. Should the PRD update then?
4. **(default)** Missing fields become `null` and the record is still written. Records are never skipped for missing abstract URLs, and there is no LLM retry loop.
5. **(default)** Only the single URL in `source.csv` is crawled (`/program/08-jun`). Other conference days are not discovered. Is one day enough for the PoC?
6. **(default)** Short name for the first conference is `eacr-2026`.
7. **(default)** No tests; `ruff` and `ty` apply per project rules.
