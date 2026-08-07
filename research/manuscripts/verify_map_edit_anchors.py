#!/usr/bin/env python3
"""grep -F every current_text against the LIVE file. The categorical audit emitted nine verbatim edits
and all nine failed to apply because the documents moved underneath them; this is the check that prevents
a repeat. Verifies against BOTH origin/main and the working tree, because another agent is editing the map
in this tree right now.

⛔ THE FILE TO CHECK IS AN ARGUMENT (added 2026-08-07), because it was hard-coded to
`three-row-audit-map-edits.json` while three other routed map-edits files existed and the project
instructions told every session to run `verify_map_edit_anchors.py <yourfile.json>`. An instruction
whose tool ignores its argument is a dead pointer of the kind CLAUDE.md §6 names — the checker
reported OK on a file the caller had not asked about. The old path remains the default so every
existing caller is unchanged.

⚠ AND "THE FILE DOES NOT EXIST ON THIS REF" IS REPORTED AS ITS OWN STATE, not as a failed anchor.
A map-edits file may legitimately target a document that lives only on a feature branch; conflating
that with "the anchor moved" sends the reader to fix the wrong thing.
"""
import json
import os
import subprocess
import sys

DEFAULT = "research/manuscripts/three-row-audit-map-edits.json"
path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
d = json.load(open(path))
bad = 0
absent = 0
for e in d["map_edits_required"]:
    for ref in ("origin/main", "WORKTREE"):
        if ref == "WORKTREE":
            if not os.path.exists(e["file"]):
                absent += 1
                print(f"--  {e['id']:>3} {ref:<11} FILE ABSENT ON THIS REF  {e['file']}")
                continue
            body = open(e["file"], encoding="utf-8").read()
        else:
            r = subprocess.run(["git", "show", f"{ref}:{e['file']}"],
                               capture_output=True, text=True)
            if r.returncode != 0:
                absent += 1
                print(f"--  {e['id']:>3} {ref:<11} FILE ABSENT ON THIS REF  {e['file']}")
                continue
            body = r.stdout
        n_anchor = body.count(e["anchor"])
        n_cur = body.count(e["current_text"])
        ok = (n_anchor == 1 and n_cur == 1)
        if not ok:
            bad += 1
        print(f"{'OK ' if ok else 'FAIL'} {e['id']:>3} {ref:<11} anchor×{n_anchor} current_text×{n_cur} "
              f"{e['file'].split('/')[-1]}")
print()
print(f"{path}: {len(d['map_edits_required'])} edits × 2 refs — {bad} failure(s), "
      f"{absent} (file, ref) pair(s) where the file does not exist on that ref")
sys.exit(1 if bad else 0)
