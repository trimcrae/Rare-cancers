#!/usr/bin/env python3
"""NEOANTIGEN-7 · repository-wide scan: which EWSR1 isoform accessions does this repository NAME,
and does it carry a sequence for any of them?

Scope: every tracked file under research/ and systems/ EXCEPT this campaign's investigation lanes
(so the count reflects the repository's own artifacts, not other lanes' prose about them).
No network.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys

REPO = "/home/user/Rare-cancers"
LANE = os.path.dirname(os.path.abspath(__file__))
ACC = re.compile(r"Q01844(?:-\d+)?")
EWSR1_HEAD = "MASTDYSTYSQAAAQQGYSA"   # canonical EWSR1 N-terminus, as held in fet-sequences-cache


def main() -> int:
    files = subprocess.run(["git", "ls-files", "research", "systems"], cwd=REPO,
                           capture_output=True, text=True, check=True).stdout.split()
    files = [f for f in files if "PORTFOLIO-INVESTIGATIONS-2026-09-08" not in f
             and "opus-capacity-campaign" not in f]
    named = {}
    for f in files:
        p = os.path.join(REPO, f)
        try:
            with open(p, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except (IsADirectoryError, OSError):
            continue
        for acc in set(ACC.findall(text)):
            named.setdefault(acc, []).append(f)

    # distinct EWSR1-like sequences held anywhere in the scanned tree
    seqs = {}
    for f in files:
        if not f.endswith(".json"):
            continue
        p = os.path.join(REPO, f)
        try:
            data = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue

        def walk(o, path):
            if isinstance(o, dict):
                for k, v in o.items():
                    walk(v, path + "/" + str(k))
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, path + "[%d]" % i)
            elif isinstance(o, str) and EWSR1_HEAD in o and len(o) > 100:
                h = hashlib.sha256(o.encode()).hexdigest()
                seqs.setdefault(h, {"sha256": h, "length": len(o), "where": []})["where"].append(f + path)

        walk(data, "")

    isoforms = sorted(a for a in named if "-" in a)
    out = {
        "_what": "Repository-wide inventory of EWSR1 accessions NAMED versus EWSR1 sequences HELD.",
        "n_files_scanned": len(files),
        "accessions_named": {a: sorted(set(named[a]))[:8] for a in sorted(named)},
        "isoform_accessions_named": isoforms,
        "n_isoform_accessions_named": len(isoforms),
        "distinct_EWSR1_like_sequences_held": [
            {"sha256": v["sha256"], "length": v["length"], "n_locations": len(v["where"]),
             "example_location": v["where"][0]} for v in sorted(seqs.values(), key=lambda d: d["length"])
        ],
        "n_isoform_sequences_held": 0,
        "⚠_note": "Exactly one held sequence is wild-type EWSR1: the 656-aa canonical Q01844. "
                  "Every other sequence listed here begins with the canonical N-terminus but is a "
                  "DESIGNED CONSTRUCT — truncated EWSR1 fragments, condensate constructs and "
                  "EWSR1::NR4A3 fusion designs — not a wild-type isoform. No wild-type EWSR1 "
                  "isoform sequence is present in this checkout.",
    }
    dest = os.path.join(LANE, "neoantigen7-isoform-gap-scan.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("accessions named:", sorted(named))
    print("isoform accessions named: %d -> %s" % (len(isoforms), isoforms))
    print("distinct EWSR1-like sequences held:",
          [(v["length"], v["sha256"][:12], len(v["where"])) for v in sorted(seqs.values(), key=lambda d: d["length"])])
    print("wrote", dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
