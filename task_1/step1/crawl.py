import logging

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

log = logging.getLogger(__name__)


async def crawl(url: str) -> str:
    # The dashboard is a JS app: wait for network idle so the programme is rendered
    config = CrawlerRunConfig(wait_until="networkidle", delay_before_return_html=3.0)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
    if not result.success:
        raise RuntimeError(f"Crawl failed for {url}: {result.error_message}")
    markdown = str(result.markdown or "").strip()
    if not markdown:
        raise RuntimeError(f"Crawl returned empty content for {url}")
    log.info(
        "Crawled %s: %d chars, %d lines", url, len(markdown), markdown.count("\n") + 1
    )
    return markdown
