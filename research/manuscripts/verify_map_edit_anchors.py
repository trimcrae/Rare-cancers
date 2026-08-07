#!/usr/bin/env python3
"""grep -F every current_text against the LIVE file. The categorical audit emitted nine verbatim edits
and all nine failed to apply because the documents moved underneath them; this is the check that prevents
a repeat. Verifies against BOTH origin/main and the working tree, because another agent is editing the map
in this tree right now.

Usage:  verify_map_edit_anchors.py [<map-edits.json>]

⛔ THE PATH ARGUMENT WAS DOCUMENTED AND IGNORED (fixed 2026-08-07). Every session that has been told to
"verify your map-edits JSON with `verify_map_edit_anchors.py <yourfile.json>`" was in fact verifying
`three-row-audit-map-edits.json` — a DIFFERENT file — and reading its green output as a check of their own.
A checker that silently checks something else is worse than no checker: it produces a pass that a reader
cannot distinguish from a real one. The default is kept so existing callers are unaffected."""
import json
import os
import subprocess
import sys

DEFAULT = "research/manuscripts/three-row-audit-map-edits.json"
path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
if not os.path.exists(path):
    print(f"no such map-edits file: {path}", file=sys.stderr)
    sys.exit(2)
print(f"verifying {path}")
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
