"""DeepSeek client (flash only): JSON mode, pydantic validation, retries and a per-run call budget."""
from __future__ import annotations

import json
import os
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from .config import config, max_calls, model

T = TypeVar("T", bound=BaseModel)


class BudgetExceeded(RuntimeError):
    pass


class LLMError(RuntimeError):
    pass


class LLM:
    def __init__(self, client=None, budget: int | None = None):
        self.budget = budget if budget is not None else max_calls()
        self.calls = 0
        self.usage = {"prompt_tokens": 0, "completion_tokens": 0}
        self._client = client

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI

            key = os.environ.get("DEEPSEEK_API_KEY")
            if not key:
                raise LLMError("DEEPSEEK_API_KEY is not set")
            cfg = config()["llm"]
            self._client = OpenAI(api_key=key, base_url=cfg["base_url"], timeout=cfg["timeout_seconds"])
        return self._client

    def json_call(self, system: str, user: str, schema: type[T], max_tokens: int = 3000) -> T:
        cfg = config()["llm"]
        last: Exception | None = None
        for _ in range(cfg["max_retries"] + 1):
            if self.calls >= self.budget:
                raise BudgetExceeded(f"LLM call budget of {self.budget} reached")
            self.calls += 1
            resp = self.client.chat.completions.create(
                model=model(),
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                response_format={"type": "json_object"},
                temperature=cfg["temperature"],
                max_tokens=max_tokens + cfg["reasoning_headroom"],
            )
            if resp.usage:
                self.usage["prompt_tokens"] += resp.usage.prompt_tokens
                self.usage["completion_tokens"] += resp.usage.completion_tokens
            try:
                return schema.model_validate(json.loads(resp.choices[0].message.content or ""))
            except (json.JSONDecodeError, ValidationError) as exc:
                last = exc
        raise LLMError(f"invalid model output after retries: {last}")
