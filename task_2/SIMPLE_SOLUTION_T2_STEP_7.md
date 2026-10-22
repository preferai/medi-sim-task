# Step 7: Roll out without downtime and ship in order of value

The previous points can also be a separate rollout which can be done in order. Each step runs behind an A/B test while the old path stays live.

| Step | Change | Why this order |
|---|---|---|
| 1 | Judge set, baseline metrics, click and impression logging | Baseline |
| 2 | Metadata fields and query tagger | Cheapest; also helps BM25 |
| 3 | Dense field in a new index, hybrid with capped semantic results | Biggest tail-query gain in [5] |
| 4 | LTR with metadata and recency features | Needs Step 1 labels |
| 5 | Personalization features | Gains depend on history length [20] |
| 6 | Answer card behind the query gate | Highest effort and risk, so last |

To keep downtime minimal:
- Build each new index in parallel and switch with an alias. Rollback means switching the alias back (a standard Elasticsearch practice)
- Keep the index fresh similar as Apple Music rebuilds its index every few hours with change detection [5].
- If the query encoder changes later, a query-side adapter can map new queries into the old index space and rerank in source space, which avoids a reindex [27].

The assistant is the most visible feature and the most expensive one as it possibly introduces additional problem statements comming from the UX side (e.g., restrictions to what to display as recommendation due to space or need for further explainability).


[5] Multilingual Semantic Retrieval for Apple Music Search — https://doi.org/10.1145/3773078.3831917

[20] Personalizing Incremental Video Search with Hybrid Text and ID Embeddings — https://doi.org/10.1145/3773078.3831896

[23] Conversational Recommendation over Live E-Commerce Catalogues with Self-Refreshing Retrieval — https://doi.org/10.1145/3773078.3841297

[27] On Reranking Space for Multi-Tenant Retrieval with Adapted Queries — https://doi.org/10.1145/3773078.3831781
