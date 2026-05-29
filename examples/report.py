"""Send a message to qwendesk from any client.

    Usage:
    QWENDESK_URL=https://your-app python examples/report.py "I was charged twice"
"""
import os
import sys

import requests

BASE = os.environ.get("QWENDESK_URL", "http://localhost:8000")
message = " ".join(sys.argv[1:]) or "The export button throws a 500 error every time."

resp = requests.post(f"{BASE}/api/triage", json={"message": message}, timeout=30)
print(resp.status_code)
print(resp.json())
