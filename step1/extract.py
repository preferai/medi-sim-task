import logging
import re

from pydantic_ai import Agent, NativeOutput
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.settings import ModelSettings
from tqdm import tqdm

from config import CHUNK_CHARS, DEFAULT_MODEL, OLLAMA_URL
from schema import Paper, normalize

log = logging.getLogger(__name__)

# Abstract pages follow this pattern on EACR; the programme page itself has no abstract links
ABSTRACT_URL_TEMPLATE = (
    "https://storage.unitedwebnetwork.com/files/991/abstract/2026/{paper_id}.htm"
)
INTERNAL_LINK = "/event/session/"
NON_TALK_TITLE = re.compile(r"^(introduction( by .*)?|q\s*&\s*a\b.*)$", re.IGNORECASE)

SYSTEM_PROMPT = """\
You extract research papers and talks from a conference programme page (markdown).
Return one record per individual presentation that has a title and a presenter. \
Skip sessions, breaks, chairs and moderators without a talk title.
Rules:
- Use null for any field that is not present in the text. Never invent values.
- title: the talk title only, without prefixes like "Proffered Paper 6:".
- paper_id: an ID such as EACR26-1448 if it appears next to the talk, else null.
- author: the presenter's full name, with a space between first and last name \
(names may be glued together, e.g. "AlexJordan" -> "Alex Jordan"). \
Copy names and affiliations exactly as written; never correct spelling.
- affiliation and country: split the text after the role, \
e.g. "Barts Cancer InstituteUnited Kingdom" -> "Barts Cancer Institute", "United Kingdom".
- category: classify by the presenter's role label and title prefix:
  research_paper = "Proffered Paper" or "Oral Presenter";
  keynote = "Keynote Speaker";
  invited_talk = "Speaker" at a symposium or session;
  industry_talk = "Industry Speaker";
  other = anything else with a title and presenter (e.g. "Award Lecture", "Expert").
- abstract_url, extra_url: copy URLs verbatim from the text; use null if the text has none. \
Do not use session or person page links. Always null for non-research_paper categories.
"""


def chunk_lines(text: str, max_chars: int = CHUNK_CHARS) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    size = 0
    for line in text.splitlines():
        if current and size + len(line) > max_chars:
            chunks.append("\n".join(current))
            current, size = [], 0
        current.append(line)
        size += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks


def merge_duplicates(papers: list[Paper]) -> list[Paper]:
    merged: list[Paper] = []
    for paper in papers:
        title = normalize(paper.title)
        known = next(
            (
                m
                for m in merged
                if normalize(m.title) == title
                and (
                    m.author is None or paper.author is None or m.author == paper.author
                )
            ),
            None,
        )
        if known is None:
            merged.append(paper)
            continue
        for field, value in paper:
            if value is not None and getattr(known, field) is None:
                setattr(known, field, value)
    return merged


def clean(paper: Paper) -> Paper:
    for field in ("abstract_url", "extra_url"):
        url = getattr(paper, field)
        if url and INTERNAL_LINK in url:
            setattr(paper, field, None)
    return paper


def fill_abstract_url(paper: Paper) -> Paper:
    if paper.abstract_url is None and paper.paper_id:
        paper.abstract_url = ABSTRACT_URL_TEMPLATE.format(paper_id=paper.paper_id)
    return paper


def make_agent(model_name: str) -> Agent[None, list[Paper]]:
    model = OpenAIChatModel(model_name, provider=OllamaProvider(base_url=OLLAMA_URL))
    # Schema-constrained output: the model otherwise wraps JSON in ```json fences
    output = NativeOutput(list[Paper])
    # Ollama's OpenAI endpoint ignores `think: false`; reasoning_effort "none" disables thinking
    settings = ModelSettings(extra_body={"reasoning_effort": "none"})
    return Agent(
        model, output_type=output, system_prompt=SYSTEM_PROMPT, model_settings=settings
    )


async def extract_papers(
    content: str, model_name: str = DEFAULT_MODEL, label: str = "extract"
) -> list[Paper]:
    agent = make_agent(model_name)
    chunks = chunk_lines(content)
    log.info(
        "Extracting with %s at %s: %d chars -> %d chunks (max %d chars, sizes %s)",
        model_name,
        OLLAMA_URL,
        len(content),
        len(chunks),
        CHUNK_CHARS,
        [len(c) for c in chunks],
    )
    papers: list[Paper] = []
    failed = 0
    for i, chunk in enumerate(tqdm(chunks, desc=label, unit="chunk"), 1):
        try:
            result = await agent.run(chunk)
        except UnexpectedModelBehavior:
            log.exception("Output validation failed for chunk %d", i)
            failed += 1
            continue
        papers.extend(result.output)
    talks = [clean(p) for p in papers if not NON_TALK_TITLE.match(p.title.strip())]
    merged = merge_duplicates(talks)
    log.info(
        "Extracted %d raw records, %d after dropping non-talks, %d after merging "
        "duplicates; %d/%d chunks failed",
        len(papers),
        len(talks),
        len(merged),
        failed,
        len(chunks),
    )
    return [fill_abstract_url(p) for p in merged]
