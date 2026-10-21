import argparse
import asyncio
import csv
import json
import logging
import os
from pathlib import Path

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.settings import ModelSettings
from tqdm import tqdm

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/v1")
DEFAULT_MODEL = os.environ.get("TOPICS_MODEL", "qwen3.5:4b-mlx")
MAX_CONTENT_CHARS = int(os.environ.get("MAX_CONTENT_CHARS", "6000"))

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
URL_FIELDS = ("abstract_url", "extra_url")

SYSTEM_PROMPT = """\
You derive topics from a scientific conference talk or paper.
You get the title and text crawled from the pages linked to it (abstract, paper).
Return 3 to 8 topics that describe what the work is about.
Rules:
- Each topic is a short lowercase noun phrase (1-4 words), e.g. "breast cancer", \
"tumour microenvironment", "recurrence prediction".
- Cover the disease or cancer type, biological mechanism, method or technology, \
and drug or therapy if present.
- Use only what the text supports. Never invent topics.
- No duplicates, no generic topics like "research" or "cancer treatment study".
"""

log = logging.getLogger(__name__)


class Topics(BaseModel):
    topics: list[str] = Field(min_length=1)


def make_agent(model_name: str) -> Agent[None, Topics]:
    model = OpenAIChatModel(model_name, provider=OllamaProvider(base_url=OLLAMA_URL))
    # Ollama's OpenAI endpoint ignores `think: false`; reasoning_effort "none" disables thinking
    settings = ModelSettings(extra_body={"reasoning_effort": "none"})
    return Agent(
        model,
        output_type=NativeOutput(Topics),
        system_prompt=SYSTEM_PROMPT,
        model_settings=settings,
    )


async def crawl(url: str) -> str | None:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=CrawlerRunConfig())
    markdown = str(result.markdown or "").strip() if result.success else ""
    if not markdown:
        log.warning("No content from %s: %s", url, result.error_message)
        return None
    return markdown


async def build_content(record: dict) -> str | None:
    pages = [
        page
        for field in URL_FIELDS
        if record.get(field) and (page := await crawl(record[field])) is not None
    ]
    if not pages:
        return None
    text = "\n\n".join(pages)[:MAX_CONTENT_CHARS]
    return f"Title: {record['title']}\n\nContent:\n{text}"


async def add_topics(records: list[dict], model_name: str, label: str) -> list[dict]:
    agent = make_agent(model_name)
    for record in tqdm(records, desc=label, unit="record"):
        record["topics"] = None
        content = await build_content(record)
        if content is None:
            continue
        try:
            result = await agent.run(content)
        except UnexpectedModelBehavior:
            log.exception("Topic extraction failed for %r", record["title"])
            continue
        record["topics"] = result.output.topics
    return records


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def source_names() -> list[str]:
    with (DATA_DIR / "source.csv").open(encoding="utf-8") as f:
        return [row["short_name"] for row in csv.DictReader(f)]


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "names", nargs="*", help="conference short names (default: all)"
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    for name in args.names or source_names():
        records = read_jsonl(DATA_DIR / "output" / f"{name}.jsonl")
        records = await add_topics(records, args.model, name)
        out = DATA_DIR / "topics" / f"{name}.jsonl"
        write_jsonl(records, out)
        done = sum(r["topics"] is not None for r in records)
        log.info("%s: topics for %d/%d records -> %s", name, done, len(records), out)


if __name__ == "__main__":
    asyncio.run(main())
