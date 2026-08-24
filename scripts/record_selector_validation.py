#!/usr/bin/env python3
"""Record the selector/preflight content that a full run has just validated.

Run this ONLY after `PREFLIGHT_FULL=1 ./scripts/preflight.sh` has exited 0, and commit the result in
the same commit as the change it validates. `affected_tests.py` refuses to scope while the recorded
hashes disagree with the files on disk, so a stale record costs a full run and never a missed one.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "scripts", "selector-validation.json")
FILES = ("scripts/affected_tests.py", "scripts/preflight.sh")


def main():
    rec = json.load(open(REC, encoding="utf-8"))
    rec["validated"] = {
        f: hashlib.sha256(open(os.path.join(ROOT, f), "rb").read()).hexdigest() for f in FILES}
    with open(REC, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    for f, h in rec["validated"].items():
        print(f"  {f}: {h[:16]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
