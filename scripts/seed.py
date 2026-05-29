"""Seed a few canned tickets (no Qwen calls) so the dashboard has data."""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import store  # noqa: E402
from app.models import Ticket, TriageResult  # noqa: E402

SAMPLES: list[tuple[str, TriageResult]] = [
    (
        "I was charged twice for my subscription this month and I'm furious.",
        TriageResult(category="billing", priority="high", sentiment="negative",
                     summary="Double-charged for subscription.",
                     draft_reply="Sorry about the double charge. I've flagged it for a refund within 3-5 business days."),
    ),
    (
        "Love the new dashboard, just wanted to say thanks!",
        TriageResult(category="feedback", priority="low", sentiment="positive",
                     summary="Positive feedback on the new dashboard.",
                     draft_reply="Thank you so much, we're thrilled you like it!"),
    ),
    (
        "The export button throws a 500 error every time I click it.",
        TriageResult(category="technical", priority="urgent", sentiment="negative",
                     summary="Export button returns a 500 error.",
                     draft_reply="Thanks for the report. We're investigating the export 500 now and will update you shortly."),
    ),
]


def main() -> None:
    if not store.enabled():
        print("WARN: Tablestore not configured — writing to a non-persistent in-memory store.")
    for message, r in SAMPLES:
        t = Ticket(
            id=store.new_ticket_id(),
            message=message,
            created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            model="seed",
            **r.model_dump(),
        )
        store.put_ticket(t)
        print(f"  seeded [{r.category}/{r.priority}] {message[:48]}")
    print("done")


if __name__ == "__main__":
    main()
