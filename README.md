# qwendesk

**Qwen-powered support triage on Alibaba Cloud.** Paste a customer message → **Qwen** (via Model Studio / DashScope) classifies it (category, priority, sentiment), writes a draft reply, and the ticket is stored in **Alibaba Cloud Tablestore**. A FastAPI dashboard lists the queue.

> Built for the **Global AI Hackathon Series with Qwen Cloud**. Both mandatory dependencies are exercised in code: **Qwen models** (`app/qwen.py`) and an **Alibaba Cloud backend** (`app/store.py`, Tablestore).

---

## Why this shape

Support triage is the canonical "LLM + a datastore" task: classify an inbound message and keep an auditable queue. Qwen does the reasoning; Tablestore (Alibaba Cloud's serverless wide-column store) holds the tickets with a single composite key that returns newest-first with no secondary index. See [`docs/architecture.md`](docs/architecture.md).

```
browser / agents ──POST /api/triage──▶ FastAPI ──Generation.call──▶ Qwen (DashScope)
                                            └─────put_row / get_range──▶ Alibaba Cloud Tablestore
```

---

## Quickstart (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # set DASHSCOPE_API_KEY (Tablestore optional locally)
uvicorn app.main:app --reload   # http://localhost:8000
```

With only a Qwen key, tickets persist to a non-persistent **in-memory** store so you can demo immediately. Set the Tablestore env vars to persist to Alibaba Cloud.

---

## Alibaba Cloud setup

1. **Qwen key** — create a DashScope / Model Studio API key at the Alibaba Cloud console; set `DASHSCOPE_API_KEY` (and optionally `QWEN_MODEL`, default `qwen-plus`).
2. **Tablestore instance** — create a Tablestore instance, note its endpoint + instance name.
3. **RAM credentials** — a RAM user with Tablestore read/write; set `ALIBABA_CLOUD_ACCESS_KEY_ID` / `..._SECRET`, `OTS_ENDPOINT`, `OTS_INSTANCE`, `OTS_TABLE`.
4. **Create the table** — `python scripts/create_table.py` (composite key `pk`+`id`). Optional demo data: `python scripts/seed.py`.

---

## Deploy the backend on Alibaba Cloud

Target **Function Compute** (FC) so the backend genuinely runs on Alibaba Cloud:

- Runtime: Python; entry exposes the ASGI app `app.main:app` (run under `uvicorn`/`fc-http`).
- Set the same env vars (Qwen + Tablestore) in the FC function config.
- FC gives you the public HTTP URL to submit as the live demo.

(ECS or Serverless App Engine work too; FC is the lowest-ops option.)

---

## API

```bash
curl -X POST http://localhost:8000/api/triage \
  -H "content-type: application/json" \
  -d '{"message":"I was charged twice this month and I am frustrated."}'
```

`GET /api/tickets` lists recent tickets; `GET /api/health` reports whether Tablestore is wired.

---

## Qwen Cloud submission checklist

| Requirement | Where it's covered |
|---|---|
| **Built with Qwen models** | `app/qwen.py` → `Generation.call(model=qwen-plus, …)` via DashScope |
| **Backend on Alibaba Cloud (code proof)** | `app/store.py` → Tablestore `put_row` / `get_range`; deploy on Function Compute |
| **Public repo + open-source license** | this repo + [`LICENSE`](LICENSE) (MIT) |
| **Live URL** | your Function Compute / FC HTTP endpoint |
| **Architecture diagram** | [`docs/architecture.md`](docs/architecture.md) |
| **Demo video (< 3 min)** | script below |
| **"Newly created / significantly updated in window"** | first commit is dated inside the submission window (May 26+); honest |

### 90-second video script
1. "qwendesk — Qwen-powered support triage on Alibaba Cloud."
2. Paste a frustrated billing message → hit **Triage** → row appears with category/priority/sentiment + a Qwen-drafted reply.
3. Show `app/qwen.py` (the DashScope/Qwen call) and `app/store.py` (the Tablestore write).
4. Open the **Tablestore console** → `qwendesk_tickets` → show the row that just landed (the "Alibaba Cloud backend in use" proof).
5. One line on the architecture diagram: agents → FastAPI on Function Compute → Qwen + Tablestore.

---

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

Covers the pure triage parser (clean/fenced/invalid/garbage JSON), the newest-first id ordering, and the API routes (health, 503-without-key, full triage→store→list flow via a mocked Qwen call). No Alibaba credentials needed — the SDKs are lazy-imported.

## Layout

```
app/qwen.py     Qwen (DashScope) call + pure JSON parser
app/store.py    Alibaba Cloud Tablestore CRUD (+ in-memory fallback)
app/main.py     FastAPI routes + dashboard
app/templates/  index.html
scripts/        create_table.py · seed.py
tests/          test_triage.py · test_api.py
docs/           architecture.md
```

MIT.
