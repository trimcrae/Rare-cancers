#!/usr/bin/env python3
"""Verify a routed `map_edits_required` block's anchors against the LIVE roadmap. ($0, pure stdlib)

⛔ WHY THIS IS CODE AND NOT A CHECKLIST ITEM (2026-08-03). The roadmap is edited concurrently by several
lanes, and a routed edit is only applicable if its `current_text` still exists in the file **verbatim and
exactly once**. On 2026-08-03 nine verbatim edits died that way in a single day: each was correct when it
was written, each named a `current_text` that had since been reworded, and every one of them failed
silently — a routed edit that cannot be located does not raise, it simply never gets applied, and the
lane that produced it reports success.

So every module that ROUTES roadmap edits calls `verify()` before it writes its artifact, and the result
travels WITH the edit. Three states, and the two failures are opposite problems:

    OK          exactly one verbatim occurrence — the edit can be applied mechanically
    NOT_FOUND   zero occurrences — the anchor was reworded or deleted; the edit is DEAD and says so
    AMBIGUOUS   more than one — a mechanical apply would hit the wrong one, so it must be narrowed

⚠ AMBIGUOUS IS NOT A WARNING, IT IS A DEFECT IN THE EDIT. An anchor like a bare filename matches wherever
that file is mentioned; the fix is a longer, unique `current_text`, never "apply the first one".

This module reads. It never writes the roadmap, and it is deliberately incapable of doing so.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAP = os.path.join(HERE, "..", "manuscripts", "nr4a3-program-map.md")

REQUIRED_FIELDS = ("section", "anchor", "current_text", "proposed_text", "why", "artifact")


def verify(edits, map_path=None):
    """Annotate each routed edit with its anchor status against the live map. Returns (edits, summary)."""
    path = os.path.abspath(map_path or DEFAULT_MAP)
    try:
        text = open(path, encoding="utf-8").read()
        read_ok, why = True, None
    except OSError as e:
        text, read_ok, why = "", False, "%s: %s" % (type(e).__name__, e)

    out = []
    for e in edits or []:
        e = dict(e)
        missing = [f for f in REQUIRED_FIELDS if f not in e]
        e["_schema_complete"] = not missing
        if missing:
            e["_schema_missing"] = missing
        if not read_ok:
            # ⚠ AN UNREADABLE MAP IS NOT A VERIFIED ANCHOR. Absent reading, absent verdict — never a pass.
            e["anchor_status"] = "UNREAD"
            e["anchor_occurrences"] = None
            e["anchor_why"] = why
            out.append(e)
            continue
        n_anchor = text.count(e.get("anchor", "\0"))
        n_current = text.count(e.get("current_text", "\0"))
        e["anchor_occurrences"] = n_anchor
        e["current_text_occurrences"] = n_current
        # The apply target is `current_text`; `anchor` is the human locator. Both are reported, and the
        # STATUS is decided by `current_text`, because that is what a mechanical apply would search for.
        e["anchor_status"] = ("OK" if n_current == 1 else
                              "NOT_FOUND" if n_current == 0 else "AMBIGUOUS")
        out.append(e)

    summary = {
        "map": os.path.relpath(path, HERE),
        "map_read": read_ok,
        "map_read_why": why,
        "n_edits": len(out),
        "n_ok": sum(1 for e in out if e.get("anchor_status") == "OK"),
        "not_found": [e.get("section") for e in out if e.get("anchor_status") == "NOT_FOUND"],
        "ambiguous": [e.get("section") for e in out if e.get("anchor_status") == "AMBIGUOUS"],
        "all_applicable": bool(out) and all(e.get("anchor_status") == "OK" for e in out),
        "_rule": "a routed edit whose current_text is not present EXACTLY ONCE cannot be applied "
                 "mechanically and must be rewritten, not applied by judgement",
    }
    return out, summary


def check():
    doc = "# T\n\nalpha unique line\n\nrepeated token\n\nrepeated token\n"
    edits = [
        {"section": "a", "anchor": "alpha", "current_text": "alpha unique line",
         "proposed_text": "beta", "why": "w", "artifact": "x.json"},
        {"section": "b", "anchor": "repeated token", "current_text": "repeated token",
         "proposed_text": "beta", "why": "w", "artifact": "x.json"},
        {"section": "c", "anchor": "gone", "current_text": "nowhere in the file",
         "proposed_text": "beta", "why": "w", "artifact": "x.json"},
        {"section": "d", "anchor": "alpha", "current_text": "alpha unique line"},
    ]
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(doc)
        p = fh.name
    got, summary = verify(edits, p)
    assert [e["anchor_status"] for e in got] == ["OK", "AMBIGUOUS", "NOT_FOUND", "OK"]
    assert summary["all_applicable"] is False
    assert summary["ambiguous"] == ["b"] and summary["not_found"] == ["c"]
    assert got[3]["_schema_complete"] is False and "why" in got[3]["_schema_missing"]
    os.unlink(p)
    got, summary = verify(edits, p + ".missing")
    assert all(e["anchor_status"] == "UNREAD" for e in got)
    assert summary["all_applicable"] is False, "an unread map can never report every edit applicable"
    assert verify([], DEFAULT_MAP)[1]["all_applicable"] is False, "no edits is not 'all applicable'"
    print("map_edit_anchors --check: OK")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if not src:
        sys.exit("usage: map_edit_anchors.py <artifact.json> [map.md]")
    d = json.load(open(src))
    edits, summary = verify(d.get("map_edits_required") or [],
                            sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps({"summary": summary, "edits": edits}, indent=2, ensure_ascii=False))
    sys.exit(0 if summary["all_applicable"] else 1)
