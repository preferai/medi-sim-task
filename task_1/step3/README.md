# Step 3: Topic extraction (PoC)

Reads the step 1 output, crawls `abstract_url` / `extra_url` of each record with Crawl4AI, and derives a list of topics with PydanticAI and a local Ollama model (thinking off). Writes the records with an added `topics` attribute.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/)
- Ollama running locally with `qwen3.5:4b-mlx` pulled
- Step 1 output in `data/output/<short-name>.jsonl`
- One-time browser setup: `uv run crawl4ai-setup`

## Run

From `step3/`:

```bash
uv sync
uv run python topics.py                  # all rows in data/source.csv
uv run python topics.py eacr-2026        # one conference
uv run python topics.py --model gemma4:12b-mlx eacr-2026
```

Settings (shell environment or `step3/.env`): `TOPICS_MODEL` (default `qwen3.5:4b-mlx`), `OLLAMA_URL` (default `http://localhost:11434/v1`), `MAX_CONTENT_CHARS` (default `6000`, crawled text sent to the model). The `--model` flag overrides `TOPICS_MODEL`.

## Data

- Input: `data/output/<short-name>.jsonl` (from step 1)
- Output: `data/topics/<short-name>.jsonl`, overwritten on each run

Output has all step 1 fields plus `topics`: a list of short lowercase topic phrases, or `null` when the record has no URL, the crawl returned nothing, or the model output failed validation.
