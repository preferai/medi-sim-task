import logging
import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

log = logging.getLogger(__name__)

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
DEFAULTS = {
    "OLLAMA_URL": "http://localhost:11434/v1",
    "SCRAPE_MODEL": "gemma4:12b-mlx",
    "CHUNK_CHARS": "3000",
}

in_shell = {key for key in DEFAULTS if key in os.environ}
in_file = {k for k, v in dotenv_values(ENV_FILE).items() if v is not None}
load_dotenv(ENV_FILE)  # does not override variables already set in the shell

OLLAMA_URL = os.environ.get("OLLAMA_URL", DEFAULTS["OLLAMA_URL"])
DEFAULT_MODEL = os.environ.get("SCRAPE_MODEL", DEFAULTS["SCRAPE_MODEL"])
CHUNK_CHARS = int(os.environ.get("CHUNK_CHARS", DEFAULTS["CHUNK_CHARS"]))


def source(key: str) -> str:
    if key in in_shell:
        return "shell environment"
    return "env file" if key in in_file else "default"


def log_config(cli_model: str | None = None) -> None:
    state = "found" if ENV_FILE.exists() else "not found"
    log.info("Env file %s: %s, keys loaded: %s", ENV_FILE, state, sorted(in_file))
    log.info("Using OLLAMA_URL=%s (from %s)", OLLAMA_URL, source("OLLAMA_URL"))
    if cli_model:
        log.info("Using model=%s (from --model flag)", cli_model)
    else:
        log.info("Using model=%s (from %s)", DEFAULT_MODEL, source("SCRAPE_MODEL"))
    log.info("Using CHUNK_CHARS=%d (from %s)", CHUNK_CHARS, source("CHUNK_CHARS"))
