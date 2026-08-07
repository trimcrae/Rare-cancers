#!/usr/bin/env python3
"""grep -F every current_text against the LIVE file. The categorical audit emitted nine verbatim edits
and all nine failed to apply because the documents moved underneath them; this is the check that prevents
a repeat. Verifies against BOTH origin/main and the working tree, because another agent is editing the map
in this tree right now.

⭑ TAKES AN OPTIONAL PATH (2026-08-07). It was hard-wired to one edit set, so every later pass either could
not use it or had to copy it — and a verifier nobody can point at a new file is a verifier that stops
being run. The default is unchanged, so existing invocations behave identically."""
import json
import subprocess
import sys

DEFAULT = "research/manuscripts/three-row-audit-map-edits.json"
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else DEFAULT))
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
