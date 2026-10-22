Finally, lets assess now how we could migrate our PoC to a large volume of new content.

I would keep the same steps (1 to 4) and turn them into a pipeline where every step reads from and writes to a shared store. Then each one can be scaled or re-run on its own (e.g., as Kubernetes pods).

For ingestion, the information from source.csv could be transfered into a Postgres databse in order to become a source registry for conferences, institutions and KOLs, each with a URL, a type and a crawl schedule. We coould build a separate python service (FastAPI to trigger manual crawling and e.g., Celery [5] for scheduling) that puts one job per due URL on a queue. Crawler workers take the jobs, with retries and a rate limit per domain. URLs that keep failing are sent to a human expert (e.g., a Slackbot notification) to check.

To store the content we could use Elasticsearch as this allows as to do a quick kNN or aproximate-kNN search to find duplicates and handle them (e.g., the same paper could be presented in multiple talks).

Inference splits into separate workers on the queue: extraction (Step 1) and topics (Step 3), which now also fill specialty, sub-specialty, drug mentions and KOL affiliation. 

The output of the individual steps where we extract topics would be checked against a fixed taxonomy. Besides using the previously mentioned approach with training a XGBoost classifier after the folksonomy stabilizes, we could also leverage Elasticsearch and create a kNN-based hybrid approach which finds similar (previously analaysed) content and uses their derived topics to assign to new documents (i.e., a popular tag-recommendation approach). Here we would need to test how to do the similarity search, i.e., with bag of words, dense embeddings or sparse embeddings which are gaining popularity recently.

We could also use Postgres for any kind of configuration for our pipeline as it may be more convenient to do a record update in a database table then to redeploy a service.

[7] https://github.com/celery/celery