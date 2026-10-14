from __future__ import annotations

import os
from functools import cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PROMPTS = ROOT / "prompts"


@cache
def config() -> dict:
    return yaml.safe_load((ROOT / "config.yaml").read_text())


def load(name: str):
    return yaml.safe_load((DATA / f"{name}.yaml").read_text())


def model() -> str:
    return os.environ.get("DEEPSEEK_MODEL") or config()["llm"]["model"]


def max_calls() -> int:
    return int(os.environ.get("MAX_LLM_CALLS_PER_RUN") or config()["llm"]["max_calls_per_run"])
