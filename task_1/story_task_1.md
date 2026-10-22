# Story: Task 1 presentation

Working title: **Three papers before a pipeline**

The red line: take the task, then walk through the solution step by step (Step 1 to Step 6), the way it was built. Each step answers a question that the previous step raised.

Audience: mixed (technical and business). One message per slide. Numbers come from `step2/eval.jsonl`, `step2/llm-eval-without-prompt.md`, `step1/IMPLEMENTATION_NOTES.md`, `data/topics/eacr-2026.jsonl` and the plots in `data/plots/`. The conference name appears only where the source is introduced (Step 1), not as a deck-wide label.

---

## 01. The task

**Title:** Classify a large volume of new medical content automatically.

**Message:** Content from conferences, institutions and KOLs keeps growing. Title, specialty, sub-specialty, drug mentions and KOL affiliation are inconsistent and fixed by hand, which hurts search, recommendations and user trust. The ask: build a classification pipeline with Generative AI and explain three things:
- Technical architecture: ingestion, preprocessing, AI inference, human-in-the-loop validation, metadata storage.
- Evaluation and monitoring: precision/recall, taxonomy coverage, hallucination rate, performance over time.
- Business communication: accuracy, cost and turnaround trade-offs, and the value for non-technical stakeholders.

**Visual:** Problem statement as a quote, the five metadata fields as tags, three cards for the three discussion points. A small footer line maps them to the steps: architecture (Steps 1, 3, 6), evaluation (Steps 2, 4), business (Step 5).

## 02. Step 1: Find a source and a way to check it

**Title:** Before any code: how will I know it works?

**Message:** New to the health domain, I searched for sources and picked the European Association for Cancer Research conference programme (to be confirmed with domain experts). Before building anything, I picked three random talks and looked them up by hand. They already show how uneven sources are:

| Talk | What I found |
|---|---|
| Stromal β3-integrin signature (EACR26-1448) | Abstract and a bioRxiv PDF |
| Intestinal zonation in colorectal cancer (EACR26-0547) | Abstract only |
| Plasma proteomics and AI (industry talk) | A video stream, no abstract |

This small hand-checked set is the first ground truth.

**Visual:** Three cards, one per talk, with found / missing chips per field.

## 03. Step 1: The first extraction script

**Title:** One CSV in, one JSONL out.

**Message:** `data/source.csv` lists the conference URLs. A script in `step1/` crawls the programme with Crawl4AI and a small local model (qwen3.5 4B via Ollama) fills a fixed schema with PydanticAI: title, paper ID, author, affiliation, country, abstract URL, extra URL. The result lands in `data/output/<conference>.jsonl`. The script was built with Spec-Driven Prompting: a PRD and a spec first (`step1/PRD.md`, `step1/SPEC.md`), then the code generated from them. No tests yet, a short README, everything runs on a laptop.

Model choice: gemma4 12B was tested first, qwen3.5 4B was kept because it is faster. Turnaround note from the build: switching the model's thinking off cut one chunk from about 62 s to 1.7 s. Whether quality holds in that mode is unchecked.

**Visual:** Left-to-right flow: source.csv, Crawl4AI, local LLM + schema, JSONL. One example record as a code card.

## 04. Step 2: A bigger model as judge

**Title:** 38 talks extracted, none invented.

**Message:** A bigger model compares the output with the source page and scores it. This is the loop for iterating on Step 1 (models, prompts).
- Talk precision: 34 of 38 extracted talks are real (0.895). The other 4 are session headers and similar non-talks. 0 fabricated.
- Talk recall: 34 of 38 expected talks found (0.895), 4 missed.
- Macro F1 over fields: 0.867. Paper ID and abstract URL are perfect, author (0.71) and affiliation (0.78) are weakest.

**Visual:** Three stat numbers on the left, field F1 plot (`data/plots/step2/02_field_f1.png`) on the right.

## 05. Step 2: What the errors look like

**Title:** The errors are wrong values, not invented ones.

**Message:** Across the 34 matched talks no field has a hallucinated value. Errors are incorrect or missing values, mostly in author (10) and affiliation (5 wrong, 4 missing). Real examples:
- Glued names: `KamilLisek`, `CarolineDive`.
- Altered letters: `Sfllomos` for Sflomos, `HUGS` for HUG, and in one run `λ3-integrin` for β3-integrin.
- Category guessed from how the title sounds instead of the printed role label.

These are mechanical and fixable with code (name splitting, "value must appear in the source" check) before reaching for a bigger model.

The judge needs checking too: a second run of the same judge built a different reference list (41 talks instead of 38, precision 0.974). Next iteration: an ensemble of smaller judges with majority or average voting (JudgeBlender, Rahmani et al. 2025) and a human spot check.

**Visual:** Verdicts plot (`data/plots/step2/04_verdicts.png`) on top, evidence chips and a small two-run comparison below.

## 06. Step 3: Topics from the abstracts

**Title:** Topics need text to read.

**Message:** A script in `step3/` follows the extracted URLs, crawls the abstracts and asks the same small model (thinking off) for a `topics` list. A bigger model would do better; the small one saves tokens. Only 7 of 38 talks link to an abstract, so 31 have no topics, and no talk has an extra URL. Where text exists, the model gets close but bends terms:
- `oncodetype dx low-risk` (Oncotype DX)
- `transform growth beta signaling pathway` (transforming growth factor beta)
- `unfolding protein response` (unfolded protein response)

**Visual:** Coverage plot (`data/plots/step5/03_coverage.png`) on the left, topic chips with the bent terms highlighted on the right.

## 07. Step 4: Explore before you trust

**Title:** Clusters find talk formats before subjects.

**Message:** A notebook in `step4/` embeds titles and topics with EmbeddingGemma-300M-medical (fine-tuned on 100k medical question–passage pairs) and clusters them.
- Titles split into three groups, and one is "conclusions, award, address": closing remarks and award lectures. Silhouette stays around 0.06, so the structure is weak.
- Topic words barely overlap: "cancer" is shared by 5 of 7 records, most other words by 2 or 3.

With 38 talks and 7 topic lists this is expected. The next step is human: medical experts judge which topics and groups make sense and fix the vocabulary. Their decisions become the ground truth.

**Visual:** Title cluster plot (`data/plots/step4/04_clusters_titles.png`) as the main image, co-occurrence heatmap (`data/plots/step4/02_cooccurrence.png`) as a smaller side image.

## 08. Step 5: Metrics as business questions

**Title:** Three questions instead of F1.

**Message:** Budget owners ask:
- "Of what we publish, how much is real?" 34 of 38 (89.5%).
- "How much did we miss?" 4 talks.
- "Does it make things up?" 0 fabricated talks. This is the trust argument for the system.

There is no need to pick one of accuracy, cost and speed. A confidence score per record routes it: high is published, medium goes to a reviewer, low is held back. Where the thresholds sit is tuned with the business.

**Visual:** Headline plot (`data/plots/step5/01_headline.png`) on top, a horizontal confidence bar with the three zones below.

## 09. Step 5: Cost now, cheaper later

**Title:** Pay for accuracy until the vocabulary settles.

**Message:**
- Cost and turnaround were not measured in the PoC. First step: log tokens and time per record (LiteLLM, Codeburn).
- Use larger, accurate models until the folksonomy is stable, tracked by the velocity of novel topics. Today every topic string is unique (44 of 44), so it is far from stable.
- Then train cheap classifiers on the learned topics: XGBoost as a baseline, JEV worth testing.
- Dominance as a recommendation signal: the UK has 8 of 38 talks (21%). If that holds across conferences and correlates with engagement, it can boost or damp content.

**Visual:** Dominance plot (`data/plots/step5/04_dominance.png`) on the right, the four points as short cards on the left.

## 10. Step 6: From PoC to production

**Title:** Same steps, now as a pipeline.

**Message:** Steps 1 to 4 stay, each reading from and writing to a shared store, so each can scale or re-run on its own (e.g. Kubernetes pods).
- Source registry in Postgres (replaces `source.csv`): conferences, institutions, KOLs with URL, type and crawl schedule.
- FastAPI for manual triggers, Celery for scheduling, one job per due URL on a queue.
- Crawler workers with retries and per-domain rate limits. URLs that keep failing go to a person via a Slackbot.
- Elasticsearch stores content and catches duplicates with (approximate) kNN, e.g. the same paper in several talks.
- Inference workers for extraction (Step 1) and topics (Step 3), now also filling specialty, sub-specialty, drug mentions and KOL affiliation.
- Pipeline config in Postgres: a row update instead of a redeploy.

**Visual:** Left-to-right architecture diagram built in HTML.

## 11. Step 6: From folksonomy to taxonomy

**Title:** New content gets tags from similar old content.

**Message:** Extracted topics are checked against a fixed taxonomy. Two ways to assign tags at scale:
- XGBoost classifier once the folksonomy is stable (Step 5).
- kNN tag recommendation in Elasticsearch: find similar, already reviewed content and reuse its topics. To test: bag of words, dense or sparse embeddings.

The human loop stays: low-confidence records, failing URLs and new topics go to experts, and their decisions feed the ground truth from Steps 1 and 4.

**Visual:** Two cards for the two tagging options, a small loop diagram for the human feedback.

## 12. Back to the task

**Title:** Small, checked, then scaled.

**Message:** One line per task question:
- Architecture: Steps 1, 3 and 6, from one script to a queue of workers over a shared store.
- Evaluation: Step 2 judge metrics plus Step 4 expert review, monitored over time on a sampled audit set (precision, recall, hallucination rate, taxonomy coverage, novel-topic velocity).
- Business: Step 5 questions, one confidence dial, and a plan to cut cost once the vocabulary settles.

Formulas for the planned metrics:
- Taxonomy coverage: C = N_labelled / N. No taxonomy yet; topics on 7 of 38.
- Novel-topic velocity: v_t = |T_t \ T_<t| / |T_t| (new topics in batch t over all topics in batch t). Today 44 / 44 = 1.0. Settled when v_t < θ for k batches.
- Cost per record: c = Σ_i tokens_i · price / N, latency as p50 and p95. Not measured yet.

Every rate gets a 95% Wilson interval: talk precision 34 of 38 = 0.895, CI [0.759, 0.958]. An alert fires when a rate falls below the lower bound of its baseline interval.

**Visual:** Three cards mirroring slide 1, five monitoring items with formulas under the last three, a closing line on the Wilson interval.
