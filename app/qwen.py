"""Qwen triage via Alibaba Cloud Model Studio (DashScope).

This file is the code-level proof of Qwen usage required by the hackathon:
`triage()` calls the DashScope Generation API with a Qwen model.
"""
from __future__ import annotations

import json
import os
import re
from typing import Optional

from .models import CATEGORIES, PRIORITIES, SENTIMENTS, TriageResult

SYSTEM_PROMPT = (
    "You are a customer-support triage assistant. Read the user's message and "
    "respond with ONLY a JSON object (no prose, no code fences) with keys: "
    "category (one of billing, technical, account, feedback, other), "
    "priority (one of low, medium, high, urgent), "
    "sentiment (one of positive, neutral, negative), "
    "summary (one short sentence), and draft_reply (a short, polite reply)."
)


def build_messages(message: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message.strip()},
    ]


def _extract_json(text: str) -> Optional[str]:
    """Pull the first JSON object out of a model response (fenced or bare)."""
    if not text:
        return None
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _one_of(value: object, allowed: tuple[str, ...], default: str) -> str:
    if isinstance(value, str) and value.strip().lower() in allowed:
        return value.strip().lower()
    return default


def parse_triage(text: str) -> TriageResult:
    """Pure: turn raw model text into a validated TriageResult, never raising."""
    raw = _extract_json(text or "")
    data: dict = {}
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                data = parsed
        except json.JSONDecodeError:
            data = {}
    summary = str(data.get("summary") or "").strip()[:500]
    if not summary:
        summary = (text or "").strip()[:200]
    return TriageResult(
        category=_one_of(data.get("category"), CATEGORIES, "other"),
        priority=_one_of(data.get("priority"), PRIORITIES, "medium"),
        sentiment=_one_of(data.get("sentiment"), SENTIMENTS, "neutral"),
        summary=summary,
        draft_reply=str(data.get("draft_reply") or "").strip()[:2000],
    )


def triage(message: str) -> tuple[TriageResult, str]:
    """Call Qwen on DashScope and parse the result. Raises RuntimeError if unconfigured."""
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("DASHSCOPE_API_KEY is not set")
    model = os.environ.get("QWEN_MODEL", "qwen-plus")

    from dashscope import Generation  # lazy: keeps imports/tests SDK-free

    resp = Generation.call(
        api_key=api_key,
        model=model,
        messages=build_messages(message),
        result_format="message",
    )
    status = getattr(resp, "status_code", 200)
    if status != 200:
        raise RuntimeError(f"DashScope error {status}: {getattr(resp, 'message', '')}")

    content = resp.output.choices[0].message.content
    if isinstance(content, list):  # some Qwen models return content parts
        content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
    return parse_triage(content), model
