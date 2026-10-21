import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


def normalize(text: str | None) -> str:
    return re.sub(r"\W+", " ", (text or "").lower()).strip()


Category = Literal[
    "research_paper", "keynote", "invited_talk", "industry_talk", "other"
]


class Paper(BaseModel):
    title: str
    paper_id: str | None = None
    author: str | None = None
    affiliation: str | None = None
    country: str | None = None
    abstract_url: str | None = None
    extra_url: str | None = None
    category: Category


def write_jsonl(papers: list[Paper], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for paper in papers:
            f.write(paper.model_dump_json() + "\n")


def read_jsonl(path: Path) -> list[Paper]:
    with path.open(encoding="utf-8") as f:
        return [Paper.model_validate(json.loads(line)) for line in f if line.strip()]
