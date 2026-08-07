#!/usr/bin/env python3
"""grep -F every current_text against the LIVE file. The categorical audit emitted nine verbatim edits
and all nine failed to apply because the documents moved underneath them; this is the check that prevents
a repeat. Verifies against BOTH origin/main and the working tree, because another agent is editing the map
in this tree right now.

⚠ IT TAKES THE ARTIFACT AS AN ARGUMENT, AND IT DID NOT UNTIL 2026-08-07. The path to
`three-row-audit-map-edits.json` was hardcoded, so a session told to *"verify anchors with
verify_map_edit_anchors.py"* — which is what CLAUDE.md's routing pattern asks for — silently verified a
DIFFERENT artifact's anchors and got a green result about work it had not done. A checker that reports OK
on the wrong input is worse than no checker: it manufactures the confidence it was supposed to earn.
That artifact is still the default, so every existing caller is unaffected.

⭑ AN ALREADY-APPLIED EDIT IS `OK`, NOT `FAIL`. `route_map_edits.py` is idempotent and reports
`already_applied` by probing the part of `proposed_text` that is not in `current_text`; this must agree
with it, or re-verifying after a successful routing turns a correct state red and invites someone to
"fix" it by re-applying.

Usage:  python3 research/manuscripts/verify_map_edit_anchors.py [artifact.json ...]
"""
import json
import subprocess
import sys

DEFAULT = "research/manuscripts/three-row-audit-map-edits.json"


def edits_of(doc):
    """Both emitted shapes: a top-level list, and a list nested under `map_edits_required`."""
    if isinstance(doc, list):
        return [e for e in doc if isinstance(e, dict) and "current_text" in e]
    blk = doc.get("map_edits_required", doc)
    if isinstance(blk, list):
        return [e for e in blk if isinstance(e, dict) and "current_text" in e]
    if isinstance(blk, dict):
        for v in blk.values():
            if isinstance(v, list) and any(isinstance(e, dict) and "current_text" in e for e in v):
                return [e for e in v if isinstance(e, dict) and "current_text" in e]
    return []


def verify(path: str) -> int:
    edits = edits_of(json.load(open(path)))
    if not edits:
        print(f"::error::{path} carries no applicable edits")
        return 1
    bad = 0
    for e in edits:
        for ref in ("origin/main", "WORKTREE"):
            if ref == "WORKTREE":
                body = open(e["file"], encoding="utf-8").read()
            else:
                body = subprocess.run(["git", "show", f"{ref}:{e['file']}"],
                                      capture_output=True, text=True).stdout
            n_anchor = body.count(e["anchor"])
            n_cur = body.count(e["current_text"])
            n_new = body.count(e.get("proposed_text") or "\0")
            ok = (n_anchor == 1 and n_cur == 1)
            note = ""
            if not ok and n_new == 1:
                ok, note = True, "  (already applied)"
            if not ok:
                bad += 1
            print(f"{'OK ' if ok else 'FAIL'} {str(e.get('id')):>6} {ref:<11} "
                  f"anchor×{n_anchor} current_text×{n_cur} {e['file'].split('/')[-1]}{note}")
    print()
    print(f"{path}: {len(edits)} edits × 2 refs — {bad} failure(s)")
    return 1 if bad else 0


def main(argv):
    rc = 0
    for path in (argv[1:] or [DEFAULT]):
        rc |= verify(path)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
