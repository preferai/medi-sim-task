Stakeholders who decide on the budget rarely care about F1 scores, so I would turn the Step 2 metrics into questions they already ask:
- Precision: "Of what we publish, how much is real?" In the EACR PoC it was 34 of 38 (0.895).
- Recall: "How much did we miss?" Also 0.895, which means four talks.
- Hallucination: "Does it make things up?" Zero fabricated talks would lead to trust as the main reason for building the system.

For the trade-offs, we do not need at this point choose between accuracy, cost and speed. A small local model is cheap but less accurate. A bigger model or an ensemble is better but costs more per record, and a human reviewer is the most accurate and the slowest. We could introduce a confidence score that can route each extracted record: high is published, medium goes to a reviewer, low is held back. The review threshold is something that can be tuned together with the business stakeholders.

For this PoC, I did not measure the cost or turnaround numbers yet. I would start by loging tokens and time per record. LiteLLM [4] is a popular tool to use also as it measures input/output tokens and the estimated cost across providers (can also be done on a user or service level). Codeburn [5] is also another popular tool to use for your harness to track usage and spending.

In any case, for the begining I would favor larger and more accurate models until a stable folksonomy is built. This could be tracked by the frequency of new topics being found from crawling new sources of information (i.e., we introduce a metric to measure velocity of novel topics).

Once this stabilizes, to reduce cost, we could think about training smaller and less compute-heavy models that are trained to classify content based on the learned topics. E.g., XGBoost is never a bad starting point, but also testing new models like JEV [6] may also result in a cost-effective and accurate solution.

We could also approach the business perspective by trying to construct a knowledge graph based on countries or affiliations that dominate a topic or a talk category. Dominance (the share of talks coming from one country or affiliation) is a popularity signal that could be beneficial when it comes to recommending content. In our PoC example, the UK has 8 of 38 talks (21%) which could be further explored if it holds for other conferences and may result into either boosting or reducing content from UK (depending if a user-engagement analysis finds any correlation here).

[4] https://github.com/BerriAI/litellm

[5] https://github.com/getagentseal/codeburn

[6] https://typesafe.ai/blog/introducing-system-one-models-and-jev