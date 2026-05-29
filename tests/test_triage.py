from app.models import Ticket, summarize
from app.qwen import parse_triage
from app.store import make_ticket_id


def test_parse_clean_json():
    r = parse_triage('{"category":"billing","priority":"high","sentiment":"negative","summary":"charged twice","draft_reply":"sorry"}')
    assert r.category == "billing"
    assert r.priority == "high"
    assert r.sentiment == "negative"
    assert r.summary == "charged twice"
    assert r.draft_reply == "sorry"


def test_parse_fenced_json():
    text = "Here you go:\n```json\n{\"category\":\"technical\",\"priority\":\"urgent\"}\n```"
    r = parse_triage(text)
    assert r.category == "technical"
    assert r.priority == "urgent"
    # missing fields fall back to defaults
    assert r.sentiment == "neutral"


def test_parse_invalid_enum_falls_back():
    r = parse_triage('{"category":"spaceship","priority":"meh","sentiment":"angry"}')
    assert r.category == "other"
    assert r.priority == "medium"
    assert r.sentiment == "neutral"


def test_parse_garbage_never_raises():
    r = parse_triage("not json at all, just words")
    assert r.category == "other"
    assert r.summary  # falls back to the raw text snippet


def test_parse_empty():
    r = parse_triage("")
    assert r.category == "other"
    assert r.summary == ""


def test_parse_json_with_surrounding_prose():
    r = parse_triage('Sure! {"category":"account","priority":"low"} hope that helps')
    assert r.category == "account"
    assert r.priority == "low"


def test_ticket_id_orders_newest_first():
    older = make_ticket_id(1_000, "aaa")
    newer = make_ticket_id(2_000, "aaa")
    # newer timestamp -> smaller inverse id -> sorts first ascending
    assert newer < older


def _ticket(priority: str, sentiment: str) -> Ticket:
    return Ticket(id="x", message="m", created_at="2026-05-29T00:00:00Z",
                  priority=priority, sentiment=sentiment)


def test_summarize_counts():
    s = summarize([
        _ticket("urgent", "negative"),
        _ticket("high", "neutral"),
        _ticket("low", "positive"),
        _ticket("urgent", "negative"),
    ])
    assert s == {"total": 4, "urgent": 2, "high": 1, "negative": 2}


def test_summarize_empty():
    assert summarize([]) == {"total": 0, "urgent": 0, "high": 0, "negative": 0}
