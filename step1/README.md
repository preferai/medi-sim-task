# Step 1: Conference programme scraper (PoC)

Crawls each programme page in `data/source.csv` with Crawl4AI, extracts papers with PydanticAI and a local Ollama model, and writes `data/output/<short-name>.jsonl`.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/)
- Ollama running locally with `gemma4:12b-mlx` pulled
- One-time browser setup: `uv run crawl4ai-setup`

The project environment (`pyproject.toml`, `uv.lock`, `.venv`, `.env`) lives in the repo root `ecc1/` and is shared by all steps.

## Run

From the repo root `ecc1/`:

```bash
uv sync
uv run python step1/scrape.py                  # all rows in data/source.csv
uv run python step1/verify.py eacr-2026        # compare output with ground truth
```

Settings come from `ecc1/.env` (`SCRAPE_MODEL`, default `gemma4:12b-mlx`; `OLLAMA_URL`, default `http://localhost:11434/v1`; `CHUNK_CHARS`, default `3000`). Precedence: `--model` flag, shell environment, `.env`, default. The startup log shows what was loaded and used.

## Data

- Input: `data/source.csv` (`short_name,url`)
- Output: `data/output/<short-name>.jsonl`, overwritten on each run
- Ground truth: `data/ground_truth/<short-name>.jsonl`

JSONL fields: `title`, `paper_id`, `author`, `affiliation`, `country`, `abstract_url`, `extra_url` (`null` when missing), `category` (`research_paper`, `keynote`, `invited_talk`, `industry_talk`, `other`).

Non-paper talks (keynotes, invited and industry talks) go in the same file; they have no abstract or PDF, so their URL fields are `null`.

## Notes

- The programme page has no abstract links, so `abstract_url` is derived from `paper_id` (EACR URL pattern, see `extract.py`); talks without a `paper_id` keep `null`. `extra_url` is not on the page and stays `null`.
- Page content is split into ~6000-character chunks and results are merged; duplicates (same title and author) are collapsed.
- Only the programme page is fetched, not abstract pages or PDFs.
