# Step 2: LLM-as-a-judge evaluation

Scores the step 1 extractor output (`data/output/<short-name>.jsonl`) against the live programme page and plots the metrics.

## Files

- `prompt.txt`: judge prompt template. Placeholders: `<<CONFERENCE>>`, `<<CONFERENCE_URL>>`, `<<EVALUATED_FILE>>`, `<<SOURCE_PAGE>>`, `<<EXTRACTED_RECORDS>>`.
- `eval.jsonl`: judge result for `eacr-2026`, one JSON object per line. Created by filling `prompt.txt` with the programme page and `data/output/eacr-2026.jsonl` and letting Claude answer it.
- `eval.ipynb`: reads `eval.jsonl` and plots the metrics. It does not call any model.
- `llm-eval-without-prompt.md`: notes from an earlier, separate judging run done without `prompt.txt`. Its numbers differ from `eval.jsonl`.

## Create `eval.jsonl`

1. Fill the placeholders in `prompt.txt`, e.g. for EACR 2026:
   - `CONFERENCE=eacr-2026`
   - `CONFERENCE_URL=https://dashboard.eacr.org/eacr26/program/08-jun`
   - `EVALUATED_FILE=data/output/eacr-2026.jsonl`
   - `SOURCE_PAGE`: the programme page text
   - `EXTRACTED_RECORDS`: the contents of `EVALUATED_FILE`
2. Run the filled prompt with the judge model. It returns a single JSON object.
3. Save that object as one line in `step2/eval.jsonl`.

## Run the notebook

From the repo root `ecc1/` (shared uv environment, see the root `pyproject.toml`):

```bash
uv sync
uv run jupyter lab step2/eval.ipynb
```

Run all cells. In VS Code, select the `ecc1/.venv` kernel instead.

Plots are shown inline and saved to `data/plots/step2/`:

| File | Content |
|---|---|
| `01_talk_level.png` | talk precision, recall, F1 and record counts |
| `02_field_f1.png` | F1 per field with the macro F1 |
| `03_precision_recall.png` | precision and recall per field |
| `04_verdicts.png` | verdict counts per field (correct, correct_null, incorrect, hallucinated, missing) |

## Metrics

Talk level: precision, recall and F1 over matched records. Field level: computed over matched records only, and a field with no scorable values has `null` metrics (shown as n/a) and is left out of the macro F1. Definitions are in `prompt.txt`.

## Caveats

- `eval.jsonl` is a single judge pass, not human-verified. Re-running the judge can give different counts.
- The current `eval.jsonl` was judged against the programme page as rendered in a browser, not the crawl4ai markdown the extractor saw, so category verdicts may differ from a strict run.
