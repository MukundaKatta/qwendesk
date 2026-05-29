import app.main as main
from app import store
from app.models import TriageResult
from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_triage_without_key_returns_503(monkeypatch):
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    r = client.post("/api/triage", json={"message": "hello"})
    assert r.status_code == 503
    assert r.json()["error"] == "qwen_unavailable"


def test_triage_flow_stores_and_lists(monkeypatch):
    store._memory.clear()
    # Tablestore disabled in tests -> in-memory fallback
    monkeypatch.setattr(store, "enabled", lambda: False)
    monkeypatch.setattr(
        main,
        "triage",
        lambda message: (
            TriageResult(category="billing", priority="high", sentiment="negative",
                         summary="charged twice", draft_reply="sorry about that"),
            "qwen-plus",
        ),
    )

    r = client.post("/api/triage", json={"message": "I was charged twice"})
    assert r.status_code == 200
    ticket = r.json()["ticket"]
    assert ticket["category"] == "billing"
    assert ticket["model"] == "qwen-plus"

    listed = client.get("/api/tickets").json()["tickets"]
    assert any(t["summary"] == "charged twice" for t in listed)


def test_triage_validation_rejects_empty():
    r = client.post("/api/triage", json={"message": ""})
    assert r.status_code == 422
