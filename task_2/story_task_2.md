# Story: Search first, answer from it

The red line: measure the current search, make medical metadata searchable, retrieve candidates with lexical and semantic methods, then rank and personalize them. Add an assistant only after that path works. It should answer from the same retrieved candidates and show its sources. Ship each change behind a local evaluation and A/B gate while the current index stays available.

Audience: RecSys and ML practitioners. The proposal draws on selected industry papers from ACM RecSys 2026, mainly in music, video, ads, e-commerce, and recommendation. Their results suggest methods to test; they are not forecasts for medical-content search.

---

## 01. The task

**Title:** Improve site search and add direct answers.

**Problem statement:**

> We currently use Elasticsearch to power site search. While functional, search relevance and ranking need improvement to help users quickly find the most valuable content. Additionally, we want to integrate the AI Assistant so that users can see both search results and direct answers to their queries in one unified experience.

The brief asks for better relevance across specialty, drug, KOL, conference, and recency; optional personalization; AI responses with citations and deep links; and an implementation path that minimizes downtime and balances effort with business value.

**Message:** The assistant responds after retrieval and ranking. It cannot compensate for a poor result set.

## 02. Measure before tuning

**Title:** Set the relevance baseline before changing the ranker.

Build a fixed query set with relevance labels. An LLM judge can help grade order, but check a sample with people. Hide the method names from the judge: one study found that naming the optimization changed scores by up to +0.89 on identical lists. Keep the prompt fixed; tone changed judge severity more than ranking, with a maximum ΔNDCG@10 of 0.011. A real-estate study reported 94%/96% agreement with human judgments. These results support a controlled judging process, not an unreviewed LLM judge [1–4].

Record each query, the results shown, their positions, clicks, and saves. The first baseline is offline NDCG@10 on the judged set, plus online no-result rate and click-through rate. Position logs matter: a click may reflect rank exposure rather than relevance.

Serendipity, catalog coverage, diversity, and demographic parity can follow once the basic relevance and logging loop is stable. They are additional measures, not substitutes for the baseline.

**Visual:** Show the blinded judge protocol, human sample check, and a separate row for offline versus online measures.

## 03. Index the medical fields

**Title:** Match specialty, drug, KOL, conference, and date as fields.

Add specialty, sub-specialty, drug, key opinion leader, conference, and date to the searchable document schema. First inspect the Task 1 extraction output; extend its Pydantic schema, route uncertain values for review, and backfill only where fields are missing. This is a prerequisite for ranking on those attributes, not a result reported by the RecSys papers.

For `pembrolizumab ASCO 2026`, parse the query into drug, conference, and year signals. Search those fields alongside the text with BM25. The annotation model could suggest query expansions, but compare expansions with the original query on the judged set before putting them in the request path [Step 2].

**Visual:** Map each query term to its indexed field, then show schema review and backfill before ranking uses the fields.

## 04. Retrieve candidates, then test sparse representations

**Title:** Keep exact matches and add semantic candidates.

Use BM25 for names, drug strings, trial IDs, dosages, and other exact or rare terms. Add dense retrieval for cases where query wording differs from the content. The Step 4 note names a Two-Tower model; treat it as a candidate-retrieval option, not another name for the later LambdaMART reranker. The notes provide no Two-Tower result, so compare it with the simpler dense path rather than assuming a gain.

Union and deduplicate the lexical and semantic candidates, then cap the semantic branch. Apple's Music search paper leaves its ranker in place: an ELISE encoder retrieves ANN candidates while a token index keeps the lexical path; the hybrid score is mapped back to the text-score distribution before ranking. Its capped semantic variant reported +2.28% conversion, 86.0% fewer no-result queries, and +7.93% on tail queries. Those are music-search results, not medical-search estimates [5].

Other papers support keeping a strong lexical path. Snap's rule-built BM25 queries reached 56.0% recall versus 42.5% for LLM-generated queries. Tubi's offline BM25 test beat a fine-tuned sentence transformer. In Meta ad ranking, lexical tokens helped preserve brands, numbers, and tail terms. Drug names, trial IDs, and dosages are a plausible analogue, but that mapping is our hypothesis [6–8]. Mercari's hybrid retriever raised purchases from its component by 20.4% in a two-week A/B test; that result also comes from another domain [9].

Sparse embeddings deserve a measured experiment, not a production claim. A top-k sparse model kept 32 of 1,024 dimensions and beat dense vectors by 16.6%–75.5% on cold-item NDCG@20 at comparable storage. For 63,001 items, its sparse CSR table used 12.4 MB versus 16.1 MB for 64-dimensional dense float32 vectors. Training cost rose about 15%–20%; the study reported no latency. A sparse autoencoder trained without labels on frozen BGE, Qwen3-Embedding-0.6B, and MiniLM embeddings beat dense alternatives in 70 of 78 settings across 13 datasets, but that result is from a preliminary three-page abstract [10, 11].

Neither sparse paper tests SPLADE/ELSER-style text search or medical/scientific text. Test two local uses against the hybrid baseline: sparse-field retrieval and SAE codes as reranker features. Compare judged tail-query relevance, index size, and p95 latency. Drop the path if it does not beat the dense baseline at an acceptable cost.

**Visuals:** The ELISE diagram shows ANN and token-index paths joining before ranking. The sparse recall plots compare methods at different storage budgets; they do not show medical search. Link each figure to its paper and keep that caveat next to it.

## 05. Rank the candidates with task features

**Title:** A retriever finds candidates; a reranker orders them.

Use a gradient-boosted learning-to-rank model such as LambdaMART on the union. Features can include specialty, drug, KOL, upcoming-versus-past conference, recency, BM25 score, and dense score. This is a different role from Two-Tower candidate retrieval.

Mercari's reranker added another 12.7% purchases beyond its hybrid retriever. Removing structured metadata reduced offline AUROC from 0.656 to 0.638, while its text embedding added little. That supports testing the task's structured medical fields as ranking features; it does not predict a local lift [9].

Do not assume a fixed recency boost helps. YouTube Music measured −0.74% on new-release engagement for a fixed boost, not statistically significant; an uncertainty-based boost reported +7.75%. Treat recency as a feature to learn and test. Upcoming-versus-past conference status is a task-specific assumption, so validate it locally [13].

Clicks and watch time are imperfect relevance labels. Position exposure affects clicks. Video duration affects completion and watch time. FLVM estimates a latent value from consumption, engagement, and valence signals while accounting for duration, session context, and user propensity. Its YouTube Shorts test raised the main viewer-enjoyment metric by 2.67%, while overall completion PR-AUC fell from 0.6898 to 0.6722. The paper's lesson is to validate the feedback target; a completion proxy can improve for long videos and worsen for short ones. Start with a duration-conditioned baseline before a full latent model [15, 16].

**Visual:** Show retrieval feeding LambdaMART. Place the FLVM figure beside the duration-bias point, clearly labeled as a video engagement model rather than a search ranker.

## 06. Put a grounded answer beside results

**Title:** Show results first; answer only when the evidence supports it.

Navigational queries such as `ASCO 2026 programme` stay on the result path. For question-like queries, show results from the common candidate set and stream an assistant response afterward. The assistant can interpret the question and summarize retrieved passages, but it does not create or reorder the result list [23–25].

The chat example uses supplied RecSys evidence rather than inventing a medical claim: one top-k sparse method reported 16.6%–75.5% higher cold-item NDCG@20 than dense vectors at comparable storage. The study did not test medical text search. In production, link each answer claim to the relevant indexed medical source and passage. If retrieved content does not support a reply, keep the results and show no answer.

Space is limited. Keep the on-results-page answer short, put source titles beside the claims they support, and let users open the source for detail. Evaluate correctness with human review, citation coverage, abstention, and latency. One agent system reported a 15.9-second P50 retry cost; a real-estate LLM reranker added 4.2 seconds. Render results immediately and stream the answer later [1, 24].

**Visual:** Put a clearly labeled chat example beside results from the same candidate set. Use distinct user and assistant bubbles, and link the paper titles inside the response. The short answer and clickable sources make the space-versus-explanation trade-off visible without a separate citation-verification panel.

## 07. Add personalization as an optional feature

**Title:** Personalize the shared ranker, with a clear fallback.

Start with a user vector built from clicked or saved items as features in the shared ranker. Apple TV used the mean of watched-item embeddings as two similarity features. It reported +8.63% NDCG@10 for 1–3-character prefixes and +2.13% to +4.37% across history lengths. Users without history or who opted out received a missing value [20]. These are video-search results.

UITP models a lifetime watch sequence as interest tokens, encodes them with a two-layer Transformer, and sends the output into a multi-task ranker. Its online study reported +2.43% exploratory views, +4.74% inter-category diversity, and +1.07% satisfied views. It is a more elaborate option than a mean user vector and should be tested only if the simpler feature helps [21].

Keep the non-personalized ranking for people with no history or who opt out. A declared-specialty fallback for new users is a product assumption; confirm consent, retention, and deletion rules before using it. Measure relevance by history length and track diversity. Do not equate video completion with medical-content relevance.

**Visual:** The UITP figure shows watch history becoming interest tokens, passing through a two-layer Transformer, then feeding multi-task heads. Label its video domain.

## 08. Gate and constrain the assistant path

**Title:** Keep retrieval structured; send only selected queries to the LLM.

Snap's ad-search system used a quality gate to route about 10% of users to an LLM path. It reported 56.6% recall at 0.1× the cost of always-on, which reported 54.5%. This is an ad-system result, not a traffic target for this product [6]. Use a cheap query gate: navigational queries get results only; question-like queries can get a grounded answer.

Melo uses a fixed understand–plan–execute–reflect–synthesize graph over existing tools. Its paper reports a 15.9-second P50 retry cost. A separate design-space study found that removing structured, inspectable retrieval access reduced success by about a third; that is a single-setting thesis abstract and weak evidence [24, 25]. These papers support keeping retrieval tools explicit and the assistant workflow bounded, not giving a free-form agent control of search.

The live-catalogue conversational system in the Infobip paper combines a refreshing product feed with retrieval, reranking, and diversity. It is a useful architecture comparison for content freshness, but it does not specify how to validate citations [23].

**Visuals:** Show SMART's quality gate as an ad-domain analogy, Melo's fixed workflow, and the self-refreshing retrieval pipeline. Caption each figure with its paper title and what it contributes; do not present any as proof of citation correctness.

## 09. Evaluate each release and keep the current index live

**Title:** Measure relevance first; add watch signals where they fit.

Keep offline NDCG@10, online no-result rate, and position-aware CTR as the search gates. Log the query, results and positions shown, clicks, and saves. For video content, also log foreground dwell/watch time relative to video length, plus the sequence of videos watched within each session. Dwell is an implicit-interest proxy, not a relevance label. Count of videos watched in sequence is a rough session-length proxy; record elapsed session time separately and do not optimize either measure alone.

Track catalog coverage and author coverage@K: the share of eligible authors with at least one item represented in the top K over a fixed window. Break it down by specialty and content format. These measures show which creators and parts of the catalog users see; they do not replace relevance or user feedback.

Roll out in order: judged query set and logging; metadata and backfill; hybrid retrieval; learning to rank; optional personalization; then the gated assistant. Run each step behind an A/B test while the current path remains available.

Build new indices in parallel and switch through an alias. Capture updates during each build and replay them before cutover. Keep the old index current through the A/B gate so rollback does not serve stale content. Update catch-up and rollback freshness are implementation details here, not a reported RecSys finding. Apple Music's rebuilds every few hours with change detection are a freshness example, not a cadence to copy [5].

The notes give no local effort estimates, cost model, business thresholds, or answer-quality result. Set those with product and engineering owners against the baseline. The decision path remains: improve retrieval, rank and personalize candidates, then answer from those candidates with linked sources.

**Visual:** Put search quality, video behavior, and author/catalog coverage in separate metric groups. Add the six rollout gates below them and keep the old-index A/B safeguard visible.

---

## Sources

[1] [LLM-Based Re-Ranking for Real Estate Search](https://doi.org/10.1145/3773078.3831907)  
[2] [Intent-Description Anchoring Bias in LLM-as-a-Judge Evaluation of Recommendation Systems](https://doi.org/10.1145/3773078.3841257)  
[3] [Should I Be Polite to My LLM Relevance Judge? Tone as a Severity Operating-Point Shift](https://doi.org/10.1145/3773078.3841249)  
[4] [LLM-as-a-Judge for Evaluating System Responses in Conversational Music Recommendation](https://doi.org/10.1145/3773078.3831800)  
[5] [Multilingual Semantic Retrieval for Apple Music Search](https://doi.org/10.1145/3773078.3831917)  
[6] [SMART: LLM-Augmented Hybrid Retrieval for Dynamic Product Ads](https://doi.org/10.1145/3773078.3831922)  
[7] [TubiFM: Unified Item, Carousel, and Search Ranking for Streaming Discovery](https://doi.org/10.1145/3773078.3831899)  
[8] [The Text on the Creative: An Under-Exploited Ranking Modality for Short-Form Video Ads](https://doi.org/10.1145/3773078.3831887)  
[9] [Hybrid Retrieval and Multimodal Reranking for Item-to-Item Recommendation in a C2C Marketplace](https://doi.org/10.1145/3773078.3831894)  
[10] [Learning Sparse Representations of Multimodal Content for Enhanced Cold Item Recommendation](https://doi.org/10.1145/3773078.3831760)  
[11] [Sparse Autoencoders as Semantic Domain Adapters for Recommender Systems](https://doi.org/10.1145/3773078.3841253)  
[13] [Breaking the Loop: An Empirical Comparison of Strategies for Novelty and Freshness in YouTube Music](https://doi.org/10.1145/3773078.3831876)  
[15] [A Control Function Framework for Mitigating Position Bias in Learning to Rank Systems](https://doi.org/10.1145/3773078.3831824)  
[16] [Mend the Measurement Gap: Latent User Preference Modeling for Short-Form Video Recommendation](https://doi.org/10.1145/3773078.3831923)  
[20] [Personalizing Incremental Video Search with Hybrid Text and ID Embeddings](https://doi.org/10.1145/3773078.3831896)  
[21] [Interest Sequence for User Modeling in Industrial Short-Form Video Recommendation](https://doi.org/10.1145/3773078.3831901)  
[23] [Conversational Recommendation over Live E-Commerce Catalogues with Self-Refreshing Retrieval](https://doi.org/10.1145/3773078.3841297)  
[24] [Melo: A Production LLM-Powered Music Recommendation Agent](https://doi.org/10.1145/3773078.3831935)  
[25] [A Design-Space Approach to Robust Agentic Conversational Recommendation](https://doi.org/10.1145/3773078.3831946)
