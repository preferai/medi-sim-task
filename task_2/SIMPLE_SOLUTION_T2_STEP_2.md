With a baseline in place, the cheapest improvement is to make the additional metadata from Task 1 searchable.

Specialty, drug, KOL, conference and date become explicit fields in the index, filled by the LLM extraction pipeline from Task 1 (Pydantic schema, confidence routing). For a given user query, the underlying annotation model could for instance be used for query expansion which in turn can help with accuracy. For example, the query "pembrolizumab ASCO 2026" becomes a drug, a conference and a year when used for searching. This could help BM25 right away, before any new model ships. 
