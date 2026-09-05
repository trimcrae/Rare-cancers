#!/usr/bin/env python3
"""Replay review selection on committed evidence; no reviews or notifications are launched."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research/autonomy"))
import bounded_review as BR
import publish_bar as PB


def measure():
    start = time.perf_counter()
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    raw, actual = {}, {}
    for path in PB.SEATS_DIR.glob("PUB-ASO-*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        seen = record.get("reviewed_commit")
        if record.get("blind") is True and isinstance(seen, str) and seen:
            raw[seen] = raw.get(seen, 0) + 1
    actual = PB._look_history("PUB-ASO")
    inflated = [{"revision": s, "previous_record_count": n,
                 "independent_reviewers": actual[s]} for s, n in raw.items() if actual[s] < n]
    ledger = json.loads((ROOT / "research/autonomy/research-ledger.json").read_text(encoding="utf-8"))
    candidates = [e for e in ledger["entries"] if not e.get("owner")
                  and str(e.get("state") or "queued") in {"queued", "blocked"}
                  and int(e.get("retry_budget") or 0) > 0 and e.get("score") is not None
                  and not e.get("requires_trimcrae")]
    withheld = []
    for entry in candidates:
        decision = BR.task_review_decision(entry, sha, repo=ROOT)
        if not decision["allowed"]:
            withheld.append({"id": entry["id"], **decision})
    return {
        "schema": "emc-bounded-review-replay/1", "revision": sha,
        "elapsed_seconds": round(time.perf_counter() - start, 3),
        "historical_seat_count": {"paper": "PUB-ASO", "rounds": len(raw),
                                  "inflated_rounds": inflated},
        "dispatch_replay": {"legacy_candidates": len(candidates), "withheld": withheld,
                            "reasons": dict(Counter(d["action"] for d in withheld))},
        "limitations": ["Read-only replay, not observed model runs or measured subscription savings.",
                        "Withheld work includes underspecified or already-reviewed work; it is not a claim that every row is unnecessary.",
                        "No publication clause, historical review, manuscript or queue record was changed by this measurement."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = measure()
    body = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8", newline="\n")
    print(body)
