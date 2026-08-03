"""EMIT ROADMAP EDITS THAT CANNOT GO STALE — anchors resolved against the LIVE map at generation time.

WHY THIS EXISTS, MEASURED. The categorical-axis audit emitted NINE verbatim `nr4a3-program-map.md` edits and
**all nine failed to apply**: they were written against the pre-merge documents while the map was restructured
underneath them, so the findings were valid and the anchors were dead, and three had to be relocated by hand.

The fix is structural, not diligence. An edit's `current_text` is never TYPED here — it is READ out of the map
as it stands when the artifact is generated, by locating a short `anchor` substring. Three consequences:

  1. A `current_text` in the output is, by construction, a byte-exact substring of the map at generation time.
  2. An anchor that is missing or ambiguous produces an entry with `status: ANCHOR_NOT_FOUND` /
     `ANCHOR_NOT_UNIQUE` and NO `proposed_text` — a visible refusal, never a silently mis-targeted edit.
     ⚠ An edit that cannot be located is not an edit that does not matter: its `why` and `artifact` are still
     emitted so the finding survives its anchor.
  3. The consumer can verify every applicable entry with a single `grep -F` of `current_text`.

Nothing here EDITS the map. It only describes edits, and the descriptions are checkable.
"""
from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
MAP = os.path.join(REPO, "research", "manuscripts", "nr4a3-program-map.md")


def load_map(path=MAP):
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return fh.read()


def locate(text, anchor):
    """(status, current_text). `current_text` is the FULL LINE containing `anchor` — a table row, a heading or
    a bullet — which is the unit an editor actually replaces. PURE."""
    if text is None:
        return "MAP_NOT_READABLE", None
    n = text.count(anchor)
    if n == 0:
        return "ANCHOR_NOT_FOUND", None
    if n > 1:
        return "ANCHOR_NOT_UNIQUE", None
    i = text.index(anchor)
    start = text.rfind("\n", 0, i) + 1
    end = text.find("\n", i)
    return "OK", text[start:(end if end >= 0 else len(text))]


def edit(text, section, anchor, why, artifact, transform, kind="amend"):
    """Build ONE edit entry. `transform(current_text) -> proposed_text` is applied only when the anchor
    resolves, so a proposed_text can never be built against a line that is not there. PURE."""
    status, current = locate(text, anchor)
    e = {"section": section, "anchor": anchor, "kind": kind, "status": status,
         "why": why, "artifact": artifact}
    if status != "OK":
        e["⚠"] = ("This edit could not be targeted against the map as it stands. The FINDING is unaffected — "
                  "apply it by hand at the named section, and see `why` and `artifact`.")
        return e
    proposed = transform(current)
    e["current_text"] = current
    e["proposed_text"] = proposed
    if proposed == current:
        # ⛔ An edit whose proposed_text equals its current_text is not an edit. Emitting it as one wastes a
        # reviewer's attention and, worse, reads as "this section was updated" when nothing was. Fail it
        # loudly here rather than shipping a silent no-op.
        e["status"] = "NO_OP_TRANSFORM_PRODUCED_NO_CHANGE"
        e["⚠"] = ("The transform returned the line unchanged — the target substring was probably not "
                  "present inside the located line. The FINDING stands; the edit needs re-targeting.")
    return e


def verify(entries, text):
    """Re-check every entry's `current_text` against `text` — the `grep -F` the consumer would run. PURE.
    Returns a summary; an entry that no longer matches is reported, never silently dropped."""
    ok, stale, unlocatable = [], [], []
    for e in entries:
        if e.get("status") != "OK":
            unlocatable.append(e["anchor"])
        elif text is not None and e.get("current_text") and text.count(e["current_text"]) == 1:
            ok.append(e["anchor"])
        else:
            stale.append(e["anchor"])
    return {"n_entries": len(entries), "n_applicable": len(ok), "n_unlocatable": len(unlocatable),
            "n_stale": len(stale), "unlocatable_anchors": unlocatable, "stale_anchors": stale,
            "verified_against": os.path.relpath(MAP, REPO),
            "_method": "each entry's current_text re-counted in the live map; exactly one occurrence = "
                       "applicable. This is the `grep -F` check, run at generation time.",
            "status": ("ALL APPLICABLE" if not stale and not unlocatable else
                       "SOME ENTRIES COULD NOT BE TARGETED — see unlocatable_anchors / stale_anchors")}


def append_to_line(suffix):
    """transform: append `suffix` to the located line. The common case for a table cell or a bullet."""
    return lambda cur: cur + suffix


def append_after_line(block):
    """transform: keep the line and add `block` beneath it (a new row under a heading, a new bullet)."""
    return lambda cur: cur + "\n" + block


def replace_in_line(old, new):
    """transform: a targeted substring replacement inside the located line."""
    return lambda cur: cur.replace(old, new)
