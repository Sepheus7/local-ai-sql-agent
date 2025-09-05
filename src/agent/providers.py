from __future__ import annotations

import os
from typing import Any, Dict, List

import requests

from .bedrock_client import BedrockToolUseClient
from .sql_guardrails import extract_first_select


class LLMProvider:
    OPENAI = "openai"
    BEDROCK = "bedrock"


def get_provider() -> str:
    return os.getenv("LLM_PROVIDER", LLMProvider.OPENAI).lower()


def generate_sql_openai(prompt: str, api_key: str, model: str = "gpt-4o-mini") -> str:
    url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1/chat/completions")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert SQL generator. Return only a single SQL SELECT statement, end with a semicolon."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return extract_first_select(content)


def generate_sql_bedrock(prompt: str) -> str:
    client = BedrockToolUseClient()
    messages = [{"role": "user", "content": prompt}]
    body = client.invoke_text(system="You return only SQL.", messages=messages)
    # Adapter: extract text depending on provider format
    text = body.get("output", {}).get("text", "") or body.get("content", "")
    return extract_first_select(text)


