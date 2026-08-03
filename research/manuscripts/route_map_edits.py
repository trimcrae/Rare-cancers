#!/usr/bin/env python3
"""Route `map_edits_required` blocks from any artifact into the roadmap — verified, never blind.

★★ WHY THIS EXISTS (trimcrae, 2026-08-03: *"Be sure you weave these into our documentation as you get
results"*, after *"make sure these are all appropriately documented in the map as they land"*).

Agents that must not edit `nr4a3-program-map.md` concurrently emit their edits as a machine-readable
`map_edits_required` block instead. Routing those blocks was being done BY HAND, which made the map's
correctness depend on one agent remembering — the exact failure the map exists to prevent.

⛔ THE THREE FAILURES THIS AUTOMATES AWAY, ALL MEASURED ON 2026-08-02/03:

1. **DEAD ANCHORS.** `categorical-axis-audit.json` emitted **nine** verbatim edits and **all nine failed to
   apply**: it wrote them against the pre-merge documents while the roadmap merge restructured both
   underneath it (map 1,436 → 4,740 lines, STRATEGY.md 3,317 → 139). Findings valid, anchors dead, three
   relocated by hand. So this refuses to apply anything it cannot locate EXACTLY ONCE, and says which.

2. **TWO INCOMPATIBLE BLOCK SHAPES.** `three-row-audit-map-edits.json` is a top-level list;
   `nr4a3-linker-library-canonical.json` nests the list under `map_edits_required.edits` beside scalar
   metadata. A router that assumed either shape crashed on the other — both crashed here first.

3. **`proposed_text: null` IS A CONTRACT, NOT A BUG.** E13 of the three-row audit carried
   `flag: "DERIVED COUNT — do not hand-edit … regenerate"`. Applying it textually would have typed a total,
   which rule 1 forbids. Null is DEFERRED and reported, never treated as empty.

⚠ Ambiguity is refused, not guessed: an anchor matching 0 times is stale, and matching >1 time is unsafe to
apply blind. Both are reported for a human or a follow-up pass. This tool never *relocates* an edit — a
relocated edit is a judgement call and belongs to whoever understands the finding.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_TARGET = REPO / "research" / "manuscripts" / "nr4a3-program-map.md"


def extract_edits(obj) -> list[dict]:
    """Pull the edit list out of whichever shape the artifact used.

    Both shapes below occurred on the same day; neither is wrong, so both are read.
    """
    if isinstance(obj, list):
        return [e for e in obj if isinstance(e, dict) and "current_text" in e]
    if not isinstance(obj, dict):
        return []
    blk = obj.get("map_edits_required", obj)
    if isinstance(blk, list):
        return [e for e in blk if isinstance(e, dict) and "current_text" in e]
    if isinstance(blk, dict):
        for value in blk.values():                      # the nested-list shape
            if isinstance(value, list) and any(isinstance(e, dict) and "current_text" in e for e in value):
                return [e for e in value if isinstance(e, dict) and "current_text" in e]
        direct = [v for v in blk.values() if isinstance(v, dict) and "current_text" in v]
        if direct:
            return direct
    return []


def route(artifact: pathlib.Path, target: pathlib.Path, apply: bool) -> dict:
    """⚠ IDEMPOTENT SINCE 2026-08-03, AND IT WAS NOT BEFORE.

    The loop below decided everything from `text.count(current_text)`, which is correct for a REPLACE
    edit and silently wrong for an APPEND edit — `proposed_text == current_text + " ✅ new clause"`.
    After such an edit lands, `current_text` is STILL in the document (it is a prefix of what replaced
    it), so a second routing pass sees exactly one match and appends the clause AGAIN. Nothing would
    have reported that: the run prints `APPLIED`, the anchor really was there, and the duplicate lives
    in the middle of a 5,000-line document.

    `map_edit_anchors.verify` decides the status instead. It probes the part of `proposed_text` that is
    NOT in `current_text` — absent before the edit lands, present after — so an already-applied edit is
    reported `already_applied` and skipped rather than re-applied.
    """
    artifact = artifact.resolve()
    edits = extract_edits(json.loads(artifact.read_text()))
    text = target.read_text()
    applied, deferred, dead, ambiguous, already = [], [], [], [], []

    sys.path.insert(0, str(REPO / "research" / "modalities"))
    import map_edit_anchors as mea                                    # noqa: E402

    checked, _summary = mea.verify(edits, str(target))
    for edit, chk in zip(edits, checked):
        eid = edit.get("id") or edit.get("section") or "?"
        cur, new = edit.get("current_text"), edit.get("proposed_text")

        # `proposed_text: null` is the derived-count contract — regenerate it, never type it.
        if new is None or cur is None or not edit.get("anchor"):
            deferred.append({"id": eid, "why": edit.get("why") or edit.get("where_it_goes") or "unanchored by design"})
            continue

        status = chk.get("anchor_status")
        if status == "APPLIED":
            already.append({"id": eid, "section": edit.get("section")})
        elif status == "OK":
            text = text.replace(cur, new, 1)
            applied.append(eid)
        elif status == "NOT_FOUND":
            dead.append({"id": eid, "section": edit.get("section")})
        else:
            ambiguous.append({"id": eid, "occurrences": chk.get("current_text_occurrences")})

    if apply and applied:
        target.write_text(text)

    return {
        "artifact": str(artifact.relative_to(REPO)) if artifact.is_relative_to(REPO) else str(artifact),
        "target": str(target.relative_to(REPO)) if target.is_relative_to(REPO) else str(target),
        "n_edits": len(edits),
        "applied": applied,
        "already_applied": already,
        "deferred_by_design": deferred,
        "dead_anchors": dead,
        "ambiguous_anchors": ambiguous,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("artifacts", nargs="+", help="JSON files carrying a map_edits_required block")
    ap.add_argument("--target", default=str(DEFAULT_TARGET))
    ap.add_argument("--apply", action="store_true", help="write the file; omit for a dry run")
    args = ap.parse_args()

    target = pathlib.Path(args.target).resolve()
    rc = 0
    for name in args.artifacts:
        path = pathlib.Path(name).resolve()
        if not path.exists():
            print(f"::error::{name} does not exist")
            rc = 1
            continue
        r = route(path, target, args.apply)
        verb = "APPLIED" if args.apply else "WOULD APPLY"
        print(f"\n{r['artifact']} → {r['target']}  ({r['n_edits']} edits)")
        print(f"  {verb} {len(r['applied'])}: {', '.join(r['applied']) or '—'}")
        for d in r["already_applied"]:
            print(f"  = already    {d['id']} ({d['section']}) — its proposed text is already in the file; not re-applied")
        for d in r["deferred_by_design"]:
            print(f"  · deferred  {d['id']} — {str(d['why'])[:110]}")
        for d in r["dead_anchors"]:
            print(f"  ✗ DEAD      {d['id']} ({d['section']}) — anchor not found; the map moved under it")
            rc = 1
        for d in r["ambiguous_anchors"]:
            print(f"  ✗ AMBIGUOUS {d['id']} — {d['occurrences']} matches; refusing to guess")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
