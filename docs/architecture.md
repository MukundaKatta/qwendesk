# Architecture

```mermaid
flowchart LR
  U[Browser] --> APP
  A[Other agents] -- "POST /api/triage" --> APP

  subgraph AC["Alibaba Cloud"]
    subgraph FC["Function Compute"]
      APP[FastAPI app · qwendesk]
    end
    Q[(Model Studio / DashScope<br/>Qwen models)]
    T[(Tablestore<br/>qwendesk_tickets)]
  end

  APP -- "Generation.call (Qwen)" --> Q
  APP -- "put_row / get_range" --> T

  classDef ali fill:#1c1730,stroke:#7c5cff,color:#e7ecf3;
  class Q,T ali;
```

## Flow
1. A message arrives (browser form or `POST /api/triage`).
2. `app/qwen.py` calls **Qwen** via DashScope (`Generation.call`) and parses the JSON triage.
3. `app/store.py` writes the ticket to **Alibaba Cloud Tablestore** (`put_row`) and lists recent ones (`get_range`).
4. The dashboard renders the recent tickets.

## Data model (Tablestore `qwendesk_tickets`)
Composite primary key: `pk` = `"TICKET"` (partition) + `id` = inverse-timestamp string, so a forward range scan returns newest-first. Attribute columns: `message, category, priority, sentiment, summary, draft_reply, model, created_at`.

Both mandatory hackathon dependencies are exercised in code: **Qwen models** (`app/qwen.py`) and an **Alibaba Cloud backend** (`app/store.py`).
