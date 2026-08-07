#!/usr/bin/env python3
"""grep -F every current_text against the LIVE file. The categorical audit emitted nine verbatim edits
and all nine failed to apply because the documents moved underneath them; this is the check that prevents
a repeat. Verifies against BOTH origin/main and the working tree, because another agent is editing the map
in this tree right now.

⚠ TAKES A PATH (added 2026-08-07). It always accepted one in the instructions sessions are given —
`verify_map_edit_anchors.py <yourfile.json>` — and never in the code, which hardcoded the three-row
audit's file and ignored argv. So a second map-edits file could be written, "verified", and reported
green while the checker had read a different document entirely: the worst possible failure for a tool
whose entire job is proving a proposal still matches reality. The default is unchanged, so every
existing invocation behaves exactly as before.

Usage:
    python3 research/manuscripts/verify_map_edit_anchors.py [map-edits.json]
"""
import json
import os
import subprocess
import sys

DEFAULT = "research/manuscripts/three-row-audit-map-edits.json"
path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
if not os.path.exists(path):
    sys.exit(f"no such map-edits file: {path}")
print(f"verifying {path}\n")
d = json.load(open(path))
bad = 0
for e in d["map_edits_required"]:
    for ref in ("origin/main", "WORKTREE"):
        if ref == "WORKTREE":
            body = open(e["file"], encoding="utf-8").read()
        else:
            body = subprocess.run(["git", "show", f"{ref}:{e['file']}"],
                                  capture_output=True, text=True).stdout
        n_anchor = body.count(e["anchor"])
        n_cur = body.count(e["current_text"])
        ok = (n_anchor == 1 and n_cur == 1)
        if not ok:
            bad += 1
        print(f"{'OK ' if ok else 'FAIL'} {e['id']:>3} {ref:<11} anchor×{n_anchor} current_text×{n_cur} "
              f"{e['file'].split('/')[-1]}")
print()
print(f"{len(d['map_edits_required'])} edits × 2 refs — {bad} failure(s)")
sys.exit(1 if bad else 0)
