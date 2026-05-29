# qwendesk — Devpost submission copy

Paste-ready. Written for the Global AI Hackathon Series with Qwen Cloud.

## Tagline
Qwen reads a support message, sorts it, and drafts the reply. Stored on Alibaba Cloud.

## Inspiration
Every support inbox has the same problem. Messages pile up and someone has to read each one, decide how urgent it is, and write a first reply. It is slow and repetitive. I wanted a small tool that does the boring first pass so a person can just check it and send.

## What it does
You paste a customer message. Qwen classifies it by category, priority, and sentiment, writes a one-line summary, and drafts a polite reply. The ticket is saved to Alibaba Cloud Tablestore and shows up in a live queue with a summary bar that counts how many are urgent, high, and negative. Sample messages run the whole flow in one click, so a demo takes seconds.

## How I built it
FastAPI for the web app and the JSON API. Qwen runs through the DashScope (Model Studio) API for the classification and the draft reply. Tickets persist in Alibaba Cloud Tablestore with a single composite key, so recent tickets come back newest-first without a second index. The app deploys on Alibaba Cloud Function Compute. The Qwen call lives in app/qwen.py and the Tablestore code lives in app/store.py, so the two Alibaba pieces are easy to point at.

## Challenges I ran into
Getting clean structured output from a model is never guaranteed. The parser pulls the first JSON object out of the reply, handles code fences and extra prose, and falls back to safe defaults when the model returns junk, so the app never breaks on a bad response. I also kept both SDKs lazy-loaded, so the app and the 14 tests run with no keys at all. That kept local work and CI fast.

## What's next
Auto-route tickets to the right queue, learn from edited replies, and add a thumbs up/down on each draft.

## Built with
python, fastapi, qwen, dashscope, alibaba-cloud, tablestore, function-compute, pydantic

## Try it out
- Code: https://github.com/MukundaKatta/qwendesk
- Live: [paste your Function Compute URL here]

## Demo video script (about 75 seconds)
1. "This is qwendesk. Qwen triages support messages on Alibaba Cloud." Show the page.
2. Click the "charged twice" sample. A row appears: billing, high, negative, with a drafted reply.
3. Click one more sample. The summary bar ticks up.
4. Open app/qwen.py: "here is the Qwen call through DashScope." Open app/store.py: "here is the Tablestore write."
5. Switch to the Alibaba Cloud Tablestore console. Show the qwendesk_tickets rows that just landed.
6. "FastAPI on Function Compute, Qwen for the reasoning, Tablestore for storage." Done.

## Steps left before you can submit (need your Alibaba account)
1. Create a DashScope API key and a Tablestore instance. Set the env vars from .env.example, then run `python scripts/create_table.py`.
2. Deploy `app.main:app` to Function Compute and copy the public URL.
3. Record the video above and upload it to YouTube.
4. Submit on the Qwen Cloud Devpost with the repo link, the live URL, and the diagram in docs/architecture.md.
