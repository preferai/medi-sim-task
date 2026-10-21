# Implementation notes

Changes made after the first version (built from `PRD.md` and `SPEC.md`) was run and checked.

## 1. Progress bar
- Added `tqdm` as a dependency of `step1`.
- `extract_papers` shows one progress bar per conference, labelled with the short name and advancing once per chunk.
- `scrape.py` passes the short name as the label.
- Removed the "Extracting chunk i/N" log line, which the bar replaces.

## 2. Chunk validation failure
- Symptom: chunk 1 failed with `Exceeded maximum output retries (1)`, so its papers were lost.
- Cause: the model wrapped its JSON in a ```` ```json ```` fence, and pydantic-ai's default output mode rejected it as `Invalid JSON`. The content itself was correct.
- Fix: the agent now uses `NativeOutput(list[Paper])`, which sends the JSON schema as a constrained response format.
- Retested chunk 1 alone: 9 valid records.

## 3. `category` field
- Added a required `category` field to `Paper`: `research_paper`, `keynote`, `invited_talk`, `industry_talk` or `other`.
- Non-paper talks (keynotes, invited and industry talks) now go in the same JSONL file with `abstract_url` and `extra_url` as `null`.
- The system prompt classifies by the role label on the page (Oral Presenter, Keynote Speaker, Speaker, Industry Speaker).
- Ground truth: added `category` to all three records. The Plasma Proteomics talk is `industry_talk`.
- `verify.py` scores `category`.
- README documents the new field.

## 4. Fixes after the first checked run
Run result: 23 records, 2 of 3 reference papers found, 9 of 14 scored fields matched. Problems found:
- Intestinal zonation paper missing from the output.
- Stromal and Spatial trajectories papers extracted twice. One copy had a null author and a dashboard session link as `abstract_url`.
- Names altered by the model (Szöőr, Mavilio, Scmid).
- "Introduction" and "Q&A" rows extracted as talks.
- Unreliable categories: award lectures and experts landed in `other`, and the keynote speaker was missing.

Fixes in `extract.py`:
- Chunk size reduced from 6000 to 3000 characters, so each call handles fewer talks and drops fewer.
- Duplicate merge now matches on normalized title, and on author only when both are set. This collapses the null-author copies.
- URLs containing `/event/session/` are set to `null` in code instead of relying on the prompt.
- Records titled "Introduction", "Introduction by ...", or "Q&A ..." are dropped.
- Prompt: copy names and affiliations exactly as written, and name "Award Lecture" and "Expert" as `other`.

## 5. Run with fix 4
- Result: 27 records, 10 chunks, 0 failed chunks, but it took 54 minutes (about 323s per chunk, against about 70s earlier). The cause is not investigated.
- `verify.py` found 1 of 3 reference papers (7/7 scored fields matched for that one).
- The model changed "β3-integrin" to "λ3-integrin" in the Stromal title, so the title match failed.
- Intestinal zonation is still missing from the output.
- LLM calls: one per chunk, sequential, no overlap between chunks. Chunks split on line boundaries, so a session can be cut across two chunks.

## 6. Logging
- `crawl.py` logs the URL, characters and lines of the crawled markdown.
- `extract.py` logs, before extraction: model, Ollama URL, total characters, chunk count, `CHUNK_CHARS` and the list of chunk sizes.
- `extract.py` logs, after extraction: raw record count, count after dropping non-talks, count after merging duplicates, and failed chunks out of total.
- These lines appear before the tqdm bar starts. Not yet run.

## 7. Config from `.env`
- Added `python-dotenv` and a new `config.py` that loads `step1/.env` and defines `OLLAMA_URL` and `SCRAPE_MODEL` (with the previous defaults as fallbacks).
- Precedence: `--model` flag, then shell environment, then `.env`, then the code default. `.env` does not override variables already set in the shell.
- `extract.py` no longer reads `os.environ` itself; it imports from `config.py`.
- `scrape.py` logs at startup: env file path and whether it was found, keys loaded from it, and the value used for `OLLAMA_URL` and the model, each with its source (`--model` flag, shell environment, env file or default).
- `--model` no longer has a default value in argparse, so the log can tell a flag from a default.
- The first request was `.env.backup`; the file that exists is `.env`, so the code loads `.env`. Writing `.env.backup` is blocked by a permission rule in the settings.
- Tested the logging three ways (default, `--model`, shell variable) and with the real `.env`. Not run end to end.

## 8. Configurable chunk size
- `CHUNK_CHARS` (default 3000) moved from `extract.py` to `config.py` and can be set in `.env` or the shell. There is no CLI flag for it.
- It is read once at import, parsed as an integer, and logged at startup with its source.
- Tested the shell override only (1500 gave a different chunk count); not run end to end.

## 9. Thinking disabled
- Observed time per chunk grows with chunk size for `qwen3.5:4b-mlx`: 62s at 1000 characters, 157s at 3000. Thinking was on by default for both `gemma4:12b-mlx` and `qwen3.5:4b-mlx`.
- Tested against Ollama's OpenAI endpoint: `think: false` is ignored (reasoning still returned); `reasoning_effort: "none"` disables thinking on both models.
- `make_agent` now passes `ModelSettings(extra_body={"reasoning_effort": "none"})`.
- Tested one 1000-character chunk with `qwen3.5:4b-mlx`: 1.7s, no thinking parts, 2 records (was about 62s).
- Quality of the fast output is unchecked. The test chunk returned a changed name ("Birá-Kovács") and a second record with an empty title. No full scrape or `verify.py` run yet.

## Open
- Thinking is now off for all runs, so earlier results (27 records, 1 of 3 papers found) are not comparable with new ones.
- `.env` sets `SCRAPE_MODEL=qwen3.5:4b-mlx`, which is now installed in Ollama. It has not been run with this pipeline, and `NativeOutput` may behave differently from `gemma4:12b-mlx`.
- The Intestinal zonation paper is missing and the Stromal title is altered, so `verify.py` still fails on 2 of 3 papers.
- A keynote on the page (Arkaitz Carracedo Perez) was missing in the earlier run, and smaller chunks did not clearly fix it.
- A 12B model can still drop talks or alter names, and the outcome may vary between runs.
- The slowdown to about 323s per chunk is unexplained.
- Considered but not done: a deterministic parser for the regular page lines with the LLM as fallback. It would be more reliable but departs from the PRD's LLM-extraction design.
