Being completely new to the health domain, I would first try to investigate potential data sources.

A quick search (e.g., with LLM-based web search) found me The European Association for Cancer Research (EACR): https://2026.eacr.org/

I would validate this with domain-experts before proceeding, but for the sake of the task, let's pick this one.

Before building anything I ask myself the question "How could I validate my solution? What could give me quickly some confidance that I am going into a good direction for a good PoC?". The best way is to create a small dataset that I could also verify by hand or with help of a humamn expert before I proceed to a full fledged evaluation.

By looking at the programme of EACR (https://dashboard.eacr.org/eacr26/program/08-jun?_gl=1*rpnxl0*_gcl_au*NDg0NzM0ODQxLjE3OTIzNjc1Nzg.) I see that I could extract first the names of published research papers as well as authors.
Here I will randomly pick 3 papers and try to use Google Scholar to find the pdf files of those papers.

Picks:
- Stromal β3-integrin signature predicting recurrence in Oncotype DX low-risk breast cancer. 
    - ID: EACR26-1448
    - Author: Alex Jordan 
    - Affiliation: Barts Cancer Institute United Kingdom
    - PDF URL: https://www.biorxiv.org/content/biorxiv/early/2026/09/16/2026.09.10.750700.full.pdf
- Stromal β3-integrin signature predicting recurrence in Oncotype DX low-risk breast cancer. 
    - Author: Alex Jordan 
    - Affiliation: Barts Cancer Institute
    - Country: United Kingdom
    - Abstract URL: https://storage.unitedwebnetwork.com/files/991/abstract/2026/EACR26-1448.htm
    - Extra URL: https://www.biorxiv.org/content/biorxiv/early/2026/09/16/2026.09.10.750700.full.pdf
- Intestinal zonation constrains driver mutation selection and shapes tumour evolution in colorectal cancer 
    - ID: EACR26-0547
    - Author: Raheleh Amirkhah
    - Affiliation: Queen's University Belfast
    - Country: United Kingdom
    - Abstract URL: https://storage.unitedwebnetwork.com/files/991/abstract/2026/EACR26-0547.htm
    - Extra URL: Not found
- Plasma Proteomics and AI: Redefining Precision Oncology
    - ID: Not found
    - Author: Yehonatan Elon
    - Affiliation: OncoHost,
    - Country: Israel
    - Abstract URL: Not found
    - Extra URL: https://emea.illumina.com/events/conferences/2026/EACR2026.html


For the first paper I found a pdf using Google Scholar. For the scond I found the abstract but did not find the paper or something else. For the third I found the a link to a video stream but no abstract or pdf.

These three example could serve as an inital data scraping check. I should end up with one csv file containing the initial conference sources. This would be my staring point.

Based on that csv file I would build a script that scrapes the content of the web page and extracts for a start the above data in a JSONL format:
- Paper name
- paper id (if available)
- author
- affiliation
- country
- abstract url
- extra url

For an initial PoC version, lets use our favourite harness and create such a python script to extract the relevant work. I would instruct the harness to create an initial folder for the PoC called step1/ then in the folder use uv and define all required packages in pyproject.toml. 

At this point (to be quickler) we do not need any tests and should keep the documentation (initial README.md file) as concise, short and concrete as possible with only most important information how to run the script and what data is depending on and what will be produced. 

In addition to step1/ folder (next to it), there should be a data/ folder which we will use accross different steps. There should be an initial csv file for conference URLs as source.csv file (at beggining only have the one coference above in it). 

The python script should go over the conference sources, find the appropriate page with the research papers and extract the neccesery information. For the initial phase, we could use Crawl4AI (e.g., from crawl4ai import AsyncWebCrawler) and qwen3.5:4b-mlx (assume you have Ollama with that model running in the background) to extract the research papers and store in a jsonl format (e.g., use pydanticAI for this). Store the jsonl file in data/output/ folder under a <conference-short-name>.jsonl file.

