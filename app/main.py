from __future__ import annotations

import datetime as dt
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from . import store
from .models import Ticket, TriageRequest
from .qwen import triage

app = FastAPI(title="qwendesk", version="0.1.0")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    backend = "Alibaba Cloud Tablestore" if store.enabled() else "in-memory (set Tablestore env to persist)"
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "tickets": store.list_tickets(50), "backend": backend},
    )


@app.get("/api/health")
def health():
    return {"ok": True, "tablestore": store.enabled()}


@app.get("/api/tickets")
def api_tickets():
    return {"tickets": [t.model_dump() for t in store.list_tickets(50)]}


@app.post("/api/triage")
def api_triage(req: TriageRequest):
    try:
        result, model = triage(req.message)
    except RuntimeError as e:
        return JSONResponse({"error": "qwen_unavailable", "message": str(e)}, status_code=503)

    ticket = Ticket(
        id=store.new_ticket_id(),
        message=req.message,
        created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        model=model,
        **result.model_dump(),
    )
    store.put_ticket(ticket)
    return {"ok": True, "ticket": ticket.model_dump()}
