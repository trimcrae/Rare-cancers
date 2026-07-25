import json
import sys

try:
    d = json.load(sys.stdin)
except Exception:
    print("poll-error")
    raise SystemExit
parts = []
for s in d.get("steps", []):
    c = s.get("conclusion")
    parts.append(f"{s['number']}:{s['status'][:4]}" + (f"/{c}" if c else ""))
print(d.get("status"), d.get("conclusion"), "|", " ".join(parts))
