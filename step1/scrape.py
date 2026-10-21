import argparse
import asyncio
import csv
import logging
import sys

from config import DEFAULT_MODEL, log_config
from crawl import crawl
from extract import extract_papers
from schema import DATA_DIR, write_jsonl

log = logging.getLogger("scrape")


async def scrape_source(short_name: str, url: str, model: str) -> None:
    content = await crawl(url)
    papers = await extract_papers(content, model, label=short_name)
    path = DATA_DIR / "output" / f"{short_name}.jsonl"
    write_jsonl(papers, path)
    log.info("%s: %s -> %d papers -> %s", short_name, url, len(papers), path)


async def main(model: str) -> int:
    with (DATA_DIR / "source.csv").open(encoding="utf-8", newline="") as f:
        sources = list(csv.DictReader(f))
    failed = 0
    for row in sources:
        try:
            await scrape_source(row["short_name"], row["url"], model)
        except Exception:
            log.exception("%s: failed (%s)", row["short_name"], row["url"])
            failed += 1
    return failed


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="Ollama model name (overrides SCRAPE_MODEL)")
    args = parser.parse_args()
    log_config(args.model)
    sys.exit(1 if asyncio.run(main(args.model or DEFAULT_MODEL)) else 0)
