# Step 2: LLM-as-a-judge evaluation of `data/output/eacr-2026.jsonl`

Judge: Claude (acting as the "bigger model" from SIMPLE_SOLUTION_STEP_2.md).
Reference: the live programme page https://dashboard.eacr.org/eacr26/program/08-jun (fetched 2026-10-21), plus the 7 abstract pages and the session sub-page it links to.

## Method

1. I read the full page text and wrote a reference list of 41 talks (title, author, affiliation, country, paper_id, category).
2. I matched each of the 38 output records to the reference (title match after normalisation, ignoring `Proffered Paper N:` prefixes and markdown brackets).
3. I scored each field per record. A value counts as a true positive if it matches the reference, a false positive if it is non-null and wrong, and a false negative if the reference has a value and the output doesn't. Both-null counts as a true negative and is ignored.
4. I scored twice. Strict compares values after lowercasing and stripping punctuation. Lenient also accepts word-order swaps in names and substring matches for affiliations, so it forgives e.g. `Karolinska Institutet` vs `Karolinska Institutet and SciLifeLab`.
5. I checked the 7 `abstract_url`s with HTTP requests. All return 200 and contain the matching paper ID. 6 of 7 also contain the programme-page title. EACR26-1448 does not: the abstract page is titled "Mural β3-Integrin Signposts a Stromal Gene Signature That Identifies Increased Recurrence in Oncotype DX Low-Risk Breast Cancer", while the programme page says "Stromal β3-integrin signature predicting recurrence ...". The ID and author match, so the link is right and the title was changed by the authors. Matching on titles alone would be unreliable here.

Scorer: `/tmp/ecc_eval/scripts/score.py` (scratch, not part of the repo).

## Caveats on the reference

- It is one pass by me, not human-verified. The category column is partly subjective.
- I excluded entries the prompt skips on purpose: bare `Introduction` / `Q&A` rows, and chairs/moderators without a talk title. If you want these counted, recall drops.
- The programme page contains its own typos (`Joachim Scmid`, `Nadia` and `Sedlyarova` in swapped order). The prompt says "copy exactly", so I scored against the page as written.
- `abstract_url` does not appear on the programme page. `extract.py` fills it from a URL template using `paper_id`. Its score is therefore the same as `paper_id`, not an independent test of extraction.

## Results

### Talk-level

| Metric | Value |
|---|---|
| Reference talks | 41 |
| Extracted records | 38 |
| True positives | 37 |
| **Talk precision** | **0.974** (37/38) |
| **Talk recall** | **0.902** (37/41) |
| Talk F1 | 0.937 |

False positive (1): `[Illumina/SomaLogic Mega Symposium ... (part 2)](https://dashboard.eacr.org/event/session/view/43226...)` is a session title with a markdown link, attached to Tala Khosroheidari's "Introduction". It is not a talk, and it breaks the "no session links" rule.

Missed (4):
- Beata Biri-Kovacs, Ágnes Czikora and Henriett Butz, three consecutive speakers in the HuCaReS symposium.
- Domenico Mavilio, the QIAGEN symposium talk.

All four sit in sessions where neighbouring talks were extracted. This looks like chunk-boundary or small-model dropout, not a page-structure problem.

### Field-level F1

| Field | Strict P | Strict R | Strict F1 | Lenient F1 |
|---|---|---|---|---|
| title | 0.947 | 0.878 | 0.911 | 0.911 |
| author | 0.684 | 0.634 | **0.658** | 0.684 |
| affiliation | 0.794 | 0.659 | 0.720 | 0.880 |
| country | 0.939 | 0.795 | 0.861 | 0.861 |
| paper_id | 1.000 | 1.000 | 1.000 | 1.000 |
| abstract_url | 1.000 | 1.000 | 1.000 | 1.000 |
| extra_url | n/a | n/a | n/a | n/a |
| category (extra) | 0.763 | 0.707 | 0.734 | 0.734 |

**Macro F1** over the fields named in the step-2 spec (title, author, country, url):

| | Strict | Lenient |
|---|---|---|
| title, author, country, abstract_url | **0.858** | **0.864** |
| all six content fields (adds affiliation, paper_id) | 0.858 | 0.889 |

`extra_url` is undefined. It is null in every output record, and no extra URLs appear on the programme page. Against your manual `data/ground_truth/eacr-2026.jsonl`, it misses 2 of 2 (Alex Jordan's bioRxiv PDF, Elon's Illumina link). The programme page can't supply these, so that is a design limit of Step 1, not an extraction failure.

## Where it goes wrong

### 1. Names are the weakest field (F1 0.66)

- **Glued names (7):** `KamilLisek`, `HadrienDe Blander`, `LuciaSimon-Carrasco`, `YardenaSamuels`, `CarolineDive`, `EnzoGalligioni`, `Marisol S.Soengas`. The prompt even gives an example of this, and the 4B model still doesn't handle it consistently. A deterministic post-processing split on lowercase→uppercase boundaries would fix it.
- **Word order swapped (1):** `Jones Gareth`. The page lists surname first.
- **Hallucinated or altered characters (4):**

| Output | Page |
|---|---|
| `Georgios Sfllomos` | `Sflomos` |
| `Nadja Sedlyarova` | `Nadia` |
| `Bodour Sahlia` | `Salhia` |
| `Joachim Schmid` | `Scmid` (silent correction of a page typo, against the "never correct" rule) |

### 2. Unsupported values (hallucination)

| Record | Value | Problem |
|---|---|---|
| Georgios Sflomos | affiliation `HUGS` | page says `HUG` |
| Gareth Jones | country `United Kingdom` | the page gives no country, so this is inferred |

Counting the author errors in section 1 (excluding the silent Schmid correction), that is 5 values in the file not supported by the page. Counting Schmid, it is 6. A "is this string in the source text" guard catches the misspelled names (`Sfllomos`, `Nadja`, `Sahlia`, and `Schmid` if you want to flag it). It misses the other two. `HUGS` appears as a substring once the lines are concatenated (`HUG` + `Switzerland`). `United Kingdom` for Gareth Jones appears elsewhere on the page. Catching those needs the check scoped to the record's own lines, with whole-line matching.

### 3. Missing affiliation or country despite being on the page

- Kamil Lisek: `MDC - BIMSB`, `Germany` both null.
- Joachim Scmid: `Illumina`, `United States` both null.
- Becky Bish and Daniel Kirschenbaum: `""` instead of values. This is also a null-vs-empty-string inconsistency in the schema.

### 4. Truncated or merged affiliations

- `Karolinska Institutet` (page: `... and SciLifeLab`)
- `KU Leuven` (page: `KU Leuven- VIB`)
- `Bruker Cellular Analysis` (page: `Bruker Cellular Analysis/ Bruker Spatial Biology`)
- `Francis Crick Institute` (page: `The Francis Crick Institute`; minor)
- `Dept of Cancer Biology Keck School of Medicine of USC` (the page value is `Inaugural (Interim) Chair & Associate Professor, Dept of Cancer Biology ...`, so the model arguably cleaned it up sensibly)

### 5. Titles

- Two titles have markup leakage: `[Proffered Paper 8: ...]` (brackets and prefix, against the prompt) and the Illumina session link above.
- Daniel Kirschenbaum's title keeps the prefix `2026 EACR - Mark Foundation - Pezcoller Foundation Rising Star Award Lecture:`. This is defensible, since the prefix is part of the page title, but it is inconsistent with how other prefixes are stripped.

### 6. Category (not in the spec metrics, but it drives downstream use)

8 of 37 matched records have the wrong category against the prompt's own role rules (accuracy 78%):

| Author | Output | Role on page | Expected |
|---|---|---|---|
| Georgios Sflomos | research_paper | Speaker | invited_talk |
| Yardena Samuels (Dark Proteome) | research_paper | Speaker | invited_talk |
| Janne Lehtiö | research_paper | Speaker | invited_talk |
| John R. Prensner | research_paper | Speaker | invited_talk |
| Bodour Salhia | other | Industry Speaker | industry_talk |
| Joseph Beechem | other | Industry Speaker | industry_talk |
| Gareth Jones | industry_talk | Industry Moderator/Chair | other |
| Yardena Samuels (Opening Address) | keynote | Chair | other |

The pattern is that the model judges by title content ("sounds like research") instead of the role label, which breaks the prompt's `research_paper = "Proffered Paper" or "Oral Presenter"` rule. Category is deterministic given the role label, so it could be derived in code. Note that Yardena Samuels appears three times on the page in different roles, and the output has two of them (Opening Address, Dark Proteome).

### 7. Not captured by the schema

Co-presenters are dropped: Thomas Campbell, co-presenting with Joseph Beechem on the same talk.

## What worked

- **Proffered-paper IDs:** all 7 IDs on the page were captured correctly, and all 7 abstract URLs resolve.
- **Country:** F1 0.86, and the errors are mostly omissions rather than wrong values.
- **No duplicate records:** 38 unique titles.
- **All three manual ground-truth papers** are present with correct title, author, affiliation, country and ID. The only differences are the unreachable `extra_url`s.

## Verdict

As a PoC extractor it is usable. Titles, IDs, countries and URLs are good (F1 ≥ 0.86). Author names and affiliations need work (0.66 and 0.72 strict). Almost every failure is mechanical, so the next iteration should fix them in code rather than by switching to a bigger model.

Suggested changes before Step 3 (ordered by expected gain):

1. Post-process names: split glued names and strip markdown/prefix artifacts from titles.
2. Add a grounding check: every non-null `author`, `affiliation` and `country` must be a substring of the source chunk after whitespace normalisation, otherwise null it or flag it for review. This addresses hallucinations (section 2).
3. Derive `category` from the role label with a regex, not the LLM.
4. Fix the recall gaps, e.g. smaller chunks or overlap, or a second pass on chunks where the count of role labels (`Speaker`, `Industry Speaker`, ...) exceeds the number of records.
5. Normalise `""` to `null` in the schema.
6. For a stronger judge, run this same comparison with an ensemble (JudgeBlender-style) and check agreement with this single-judge result. Add a human spot check of the reference first, since all numbers above depend on it.
