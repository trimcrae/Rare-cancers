#!/usr/bin/env python3
"""VERIFY EVERY ROUTED MAP EDIT STILL APPLIES — the last step before an artifact is handed over.

WHY THIS EXISTS, MEASURED
-------------------------
The categorical audit emitted NINE verbatim roadmap edits and ALL NINE failed to apply: they were
written against the pre-merge documents while the map was restructured underneath them. The findings
were valid; the anchors were dead. An edit whose anchor no longer exists is not a small defect --
it is a finding that silently does not land, which is the same failure the roadmap's own
"a caveat with nowhere to go is how work gets silently dropped" names.

So any module that emits a `map_edits_required` block runs this against the LIVE map as its final
act, and reports the result beside the block. The check is exact-substring (`grep -F` semantics),
never a regex and never a fuzzy match: a fuzzy match that "nearly" applies is how a stale anchor
survives review.

CONTRACT for one entry in `map_edits_required`:
    section        where it goes, in the map's own numbering
    anchor         a currently-present, unique substring of the map -- or null
    current_text   verbatim text to be replaced, or null when `anchor` is null
    proposed_text  verbatim replacement, ready to apply
    why            one line
    artifact       file:field that OWNS the number, so the map links rather than restates (rule 1)

    `anchor: null` means the edit needs a section that does not exist; `where` must then describe
    where it goes. Such an entry is reported as NEEDS_NEW_SECTION, which is a valid state and not a
    failure.

USAGE
    python3 verify_map_edits.py <artifact.json> [<artifact.json> ...]
    python3 verify_map_edits.py --map <path> --write <report.json> <artifact.json>

Exit code is 1 if any edit is DEAD (an anchor or current_text that is not present verbatim, or a
non-unique anchor), so CI fails on a stale anchor rather than shipping one.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAP = os.path.normpath(os.path.join(HERE, "..", "manuscripts", "nr4a3-program-map.md"))

REQUIRED_FIELDS = ("section", "anchor", "current_text", "proposed_text", "why", "artifact")


def check_edit(edit, map_text):
    """One edit -> a verdict row. Pure."""
    row = {"section": edit.get("section"), "why": edit.get("why"),
           "artifact": edit.get("artifact")}
    missing = [f for f in REQUIRED_FIELDS if f not in edit]
    if missing:
        row["status"] = "MALFORMED"
        row["detail"] = "missing required field(s): %s" % ", ".join(missing)
        return row

    anchor = edit.get("anchor")
    if anchor is None:
        row["status"] = "NEEDS_NEW_SECTION"
        row["detail"] = edit.get("where") or ("anchor is null and no `where` was given -- the map's "
                                              "owner cannot place this edit")
        row["ok"] = bool(edit.get("where"))
        return row

    n_anchor = map_text.count(anchor)
    if n_anchor == 0:
        row["status"] = "DEAD_ANCHOR"
        row["detail"] = "anchor not present in the live map: %r" % anchor[:120]
        return row
    if n_anchor > 1:
        row["status"] = "AMBIGUOUS_ANCHOR"
        row["detail"] = ("anchor occurs %d times; an edit that could land in more than one place is "
                         "not applicable as written: %r" % (n_anchor, anchor[:120]))
        return row

    cur = edit.get("current_text")
    if cur:
        n_cur = map_text.count(cur)
        if n_cur == 0:
            row["status"] = "DEAD_CURRENT_TEXT"
            row["detail"] = ("the anchor is present but `current_text` is not verbatim in the live "
                             "map, so the replacement cannot be applied mechanically. First 160 "
                             "chars: %r" % cur[:160])
            return row
        if n_cur > 1:
            row["status"] = "AMBIGUOUS_CURRENT_TEXT"
            row["detail"] = "`current_text` occurs %d times" % n_cur
            return row

    row["status"] = "APPLIES"
    row["ok"] = True
    row["detail"] = "anchor and current_text are both present exactly once in the live map"
    return row


def verify(artifact_paths, map_path=DEFAULT_MAP):
    with open(map_path, encoding="utf-8") as fh:
        map_text = fh.read()
    report = {"_what": ("verbatim verification that every routed roadmap edit still applies to the "
                        "map AS IT STANDS RIGHT NOW. Exact substring matching only."),
              "map": os.path.relpath(map_path, os.path.join(HERE, "..", "..")),
              "map_bytes": len(map_text), "artifacts": []}
    dead = 0
    for path in artifact_paths:
        entry = {"artifact": os.path.basename(path), "edits": []}
        try:
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, ValueError) as e:
            entry["error"] = "%s: %s" % (type(e).__name__, e)
            dead += 1
            report["artifacts"].append(entry)
            continue
        for edit in doc.get("map_edits_required") or []:
            row = check_edit(edit, map_text)
            entry["edits"].append(row)
            if not row.get("ok"):
                dead += 1
        entry["n_edits"] = len(entry["edits"])
        entry["n_applies"] = sum(1 for r in entry["edits"] if r["status"] == "APPLIES")
        entry["n_needs_new_section"] = sum(1 for r in entry["edits"]
                                           if r["status"] == "NEEDS_NEW_SECTION")
        report["artifacts"].append(entry)
    report["n_not_applicable"] = dead
    report["verdict"] = ("ALL EDITS APPLY" if dead == 0 else
                         "%d edit(s) do NOT apply to the live map and must be rewritten before "
                         "hand-off" % dead)
    return report, dead


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Verify routed roadmap edits against the live map.")
    ap.add_argument("artifacts", nargs="+")
    ap.add_argument("--map", default=DEFAULT_MAP)
    ap.add_argument("--write")
    args = ap.parse_args(argv)
    report, dead = verify(args.artifacts, args.map)
    text = json.dumps(report, indent=1)
    print(text)
    if args.write:
        with open(args.write, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    print("\n%s" % report["verdict"], file=sys.stderr)
    return 1 if dead else 0


if __name__ == "__main__":
    raise SystemExit(main())
