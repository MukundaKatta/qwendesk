from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["billing", "technical", "account", "feedback", "other"]
Priority = Literal["low", "medium", "high", "urgent"]
Sentiment = Literal["positive", "neutral", "negative"]

CATEGORIES = ("billing", "technical", "account", "feedback", "other")
PRIORITIES = ("low", "medium", "high", "urgent")
SENTIMENTS = ("positive", "neutral", "negative")


class TriageResult(BaseModel):
    category: Category = "other"
    priority: Priority = "medium"
    sentiment: Sentiment = "neutral"
    summary: str = ""
    draft_reply: str = ""


class Ticket(TriageResult):
    id: str
    message: str
    created_at: str
    model: str = ""


class TriageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
