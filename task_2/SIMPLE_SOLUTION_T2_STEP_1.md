For the second task, I think it makes sense to continue leveraging Elasticsearch capabilities and and build on top of it. 

Aslo, for this task I focuseed on the recently held ACM International Conference on Recommender Systems 2026 (especially the industry papers about feeds, music, video, e-commerce, ads). 

As in Task 1, the first question is how I would know that a change helps. Before touching ranking I would build two things.

The first (if already doesn't exist) could be an offline judge set as described in [1]. Here would real queries be graded with relevance labels from an LLM judge and then checked by humans on a sample. QuintoAndar Group has shown that their judge (i.e., to say which ordering better satisfies the user intent) agreed with humans 94%/96%. 

Here we can follow these three rules:
- Hide algorithm names from the judge. Telling it which list "optimises diversity" shifted scores by up to +0.89 on identical lists [2].
- Keep the prompt fixed. Tone shifted severity and calibration more than ranking (max ΔNDCG@10 0.011) [3].
- Keep humans in the loop, as the authors of a music judge study conclude [4].

The second is click and impression logging: every query, every result shown, its position, and what the user clicked or saved. We could for instance train a re-ranking model on this, and position bias can only be corrected if positions are logged.

With both in place I would record baseline metrics for the current Elasticsearch setup: NDCG@10 on the judge set, plus no-result rate and click-through online. We can go easily further we metrics like Serendipity, Catalog Coverage, Diversity, Demographic Parity but let's start with these first.

[1] LLM-Based Re-Ranking for Real Estate Search — https://doi.org/10.1145/3773078.3831907

[2] Intent-Description Anchoring Bias in LLM-as-a-Judge Evaluation of Recommendation Systems — https://doi.org/10.1145/3773078.3841257

[3] Should I Be Polite to My LLM Relevance Judge? Tone as a Severity Operating-Point Shift — https://doi.org/10.1145/3773078.3841249

[4] LLM-as-a-Judge for Evaluating System Responses in Conversational Music Recommendation — https://doi.org/10.1145/3773078.3831800
