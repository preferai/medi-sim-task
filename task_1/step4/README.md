# Step 4: Topic extraction analysis

`topics.ipynb` analyses the `title` and `topics` attributes of the step 3 output (`data/topics/<short-name>.jsonl`). It does no crawling and no topic extraction.

Sections:

1. Topic words shared by 2+ records (topics normalized: lowercase, tumour → tumor, stopwords dropped)
2. Word co-occurrence
3. Record similarity (TF-IDF over topic words)
4. Clusters of titles, all records
5. Clusters of title + topics, records with topics only
6. Topics for manual review

## Prerequisites

- Ollama running locally with the embedding model pulled: `ollama pull hf.co/dontia/embeddinggemma-300m-medical-Q8_0-GGUF:Q8_0`

## Run

From the repo root (`ecc1/`):

```bash
uv run jupyter lab step4/topics.ipynb
```

Set `NAME` in the first code cell to analyse another conference. Settings (shell environment or `.env`): `OLLAMA_URL` (default `http://localhost:11434/v1`), `EMBED_MODEL` (default `hf.co/dontia/embeddinggemma-300m-medical-Q8_0-GGUF:Q8_0`), `EMBED_PREFIX` (task prefix prepended to each text, default `task: clustering | query: `; use `clustering: ` for `nomic-embed-text`). Empty values fall back to the defaults.

## Data

- Input: `data/topics/<short-name>.jsonl` (from step 3)
- Output: plots in `data/plots/step4/`
