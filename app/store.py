"""Ticket storage on Alibaba Cloud Tablestore.

This file is the code-level proof of the Alibaba Cloud backend required by the
hackathon: `put_ticket` / `list_tickets` use the Tablestore (OTS) SDK.

Single composite primary key: pk = "TICKET" (partition), id = inverse-timestamp
(so ascending key order is newest-first). Without Tablestore env vars the app
falls back to a non-persistent in-memory list, so local dev needs only a Qwen key.
"""
from __future__ import annotations

import os
import secrets
import time

from .models import CATEGORIES, PRIORITIES, SENTIMENTS, Ticket

TABLE_DEFAULT = "qwendesk_tickets"
PARTITION = "TICKET"

_memory: list[Ticket] = []
_client = None


def table_name() -> str:
    return os.environ.get("OTS_TABLE", TABLE_DEFAULT)


def _conf() -> tuple:
    return (
        os.environ.get("OTS_ENDPOINT"),
        os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID"),
        os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET"),
        os.environ.get("OTS_INSTANCE"),
    )


def enabled() -> bool:
    """True when Tablestore is fully configured (otherwise: in-memory fallback)."""
    return all(_conf())


def make_ticket_id(ts_ms: int, suffix: str) -> str:
    """Inverse-timestamp id: ascending key order == newest first."""
    inv = 9_999_999_999_999 - int(ts_ms)
    return f"{inv:013d}-{suffix}"


def new_ticket_id() -> str:
    return make_ticket_id(int(time.time() * 1000), secrets.token_hex(3))


def _clamp(value: object, allowed: tuple[str, ...], default: str) -> str:
    s = str(value).strip().lower() if value is not None else ""
    return s if s in allowed else default


def _get_client():
    global _client
    if _client is not None:
        return _client
    from tablestore import OTSClient  # lazy import

    endpoint, akid, aksecret, instance = _conf()
    _client = OTSClient(endpoint, akid, aksecret, instance)
    return _client


def put_ticket(t: Ticket) -> None:
    if not enabled():
        _memory.insert(0, t)
        del _memory[200:]
        return

    from tablestore import Condition, Row, RowExistenceExpectation

    primary_key = [("pk", PARTITION), ("id", t.id)]
    attribute_columns = [
        ("message", t.message),
        ("category", t.category),
        ("priority", t.priority),
        ("sentiment", t.sentiment),
        ("summary", t.summary),
        ("draft_reply", t.draft_reply),
        ("model", t.model),
        ("created_at", t.created_at),
    ]
    row = Row(primary_key, attribute_columns)
    _get_client().put_row(table_name(), row, Condition(RowExistenceExpectation.IGNORE))


def list_tickets(limit: int = 50) -> list[Ticket]:
    if not enabled():
        return _memory[:limit]

    from tablestore import INF_MAX, INF_MIN, Direction

    start = [("pk", PARTITION), ("id", INF_MIN)]
    end = [("pk", PARTITION), ("id", INF_MAX)]
    _, _, rows, _ = _get_client().get_range(table_name(), Direction.FORWARD, start, end, [], limit)

    out: list[Ticket] = []
    for row in rows or []:
        attrs = {k: v for (k, v, *_rest) in row.attribute_columns}
        pk = dict(row.primary_key)
        out.append(
            Ticket(
                id=str(pk.get("id", "")),
                message=str(attrs.get("message", "")),
                category=_clamp(attrs.get("category"), CATEGORIES, "other"),
                priority=_clamp(attrs.get("priority"), PRIORITIES, "medium"),
                sentiment=_clamp(attrs.get("sentiment"), SENTIMENTS, "neutral"),
                summary=str(attrs.get("summary", "")),
                draft_reply=str(attrs.get("draft_reply", "")),
                model=str(attrs.get("model", "")),
                created_at=str(attrs.get("created_at", "")),
            )
        )
    return out
