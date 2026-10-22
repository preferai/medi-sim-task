After running we did everything defined in SIMPLE_SOLUTION_STEP_1.md we end up with a <conference-short-name>.jsonl file in the data/output/ we can use a bigger model for a LLM-as-a-Judge case and iterate over Step-1 (e.g., changing LLMs or prompts) until we converge to the best results.

Within the instructions to the LLM-as-a-judge fro start we could measure:
- Talk precision
    -   How many of the extracted talks are real and correctly matched to the source record on conference page? (This may also account for assessing hallucinations)
- Talk recall
    -   How many of the expected talks were captured?
- Macro F1:
    -   F1 for each field content extraction (e.g., title, author, country, url) and then divide by number of fields


Instead of a bigger model, we could also use an ensamble of smaller-sized LLMs in a blending technique like JudgeBlender from [1] with majority voting or average voting.

[1] Rahmani, H. A., Yilmaz, E., Craswell, N., & Mitra, B. (2025, May). JudgeBlender: ensembling automatic relevance judgments. In Companion Proceedings of the ACM on Web Conference 2025 (pp. 1268-1272).
https://dl.acm.org/doi/pdf/10.1145/3701716.3715536

