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
    APPLIED     `current_text` is gone AND `proposed_text` is present — the edit SUCCEEDED
    NOT_FOUND   neither is present — the anchor was reworded or deleted; the edit is DEAD and says so
    AMBIGUOUS   more than one `current_text` — a mechanical apply would hit the wrong one
    UNREAD      the map could not be read at all

⚠ AMBIGUOUS IS NOT A WARNING, IT IS A DEFECT IN THE EDIT. An anchor like a bare filename matches wherever
that file is mentioned; the fix is a longer, unique `current_text`, never "apply the first one".

⚠⚠ AND `APPLIED` IS WHY THIS CANNOT BE A ONE-LINE `text.count(anchor) == 0` CHECK (measured 2026-08-03).
`tests/test_linker_library_canonical.py` implemented exactly that check and was RED on `main` with FIFTEEN
"dead" anchors — and every one of the fifteen was dead **because the edit had been applied**: the
`current_text` was gone precisely because the `proposed_text` had replaced it. A guard shaped that way goes
red at the moment routing SUCCEEDS, so its only stable green state is "nobody applied anything", and the
pressure it creates is to stop routing edits. The discriminator costs one extra substring search:
    current_text absent + proposed_text PRESENT  => APPLIED  (nothing to do, and not an error)
    current_text absent + proposed_text ABSENT   => NOT_FOUND (the document really did move)

This module reads. It never writes the roadmap, and it is deliberately incapable of doing so.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAP = os.path.join(HERE, "..", "manuscripts", "nr4a3-program-map.md")

REQUIRED_FIELDS = ("section", "anchor", "current_text", "proposed_text", "why", "artifact")

#: How much of `proposed_text` to search for when deciding whether an edit already LANDED. Long enough to
#: be unique in a 5,000-line document, short enough to survive a tail reword as the edit was applied.
PROPOSED_PROBE_CHARS = 120
#: Below this a probe is too generic to mean anything, so absence of evidence is reported as NOT_FOUND
#: rather than manufactured into an APPLIED.
MIN_PROBE_CHARS = 24


def _introduced_span(proposed, current):
    """(start, end) of the text an edit INTRODUCES — `proposed` minus its common prefix and common suffix
    with `current`. PURE. Correct for all three edit shapes rather than two:

        append   proposed = current + TAIL            -> TAIL
        prepend  proposed = HEAD + current            -> HEAD
        replace  proposed = A + NEW + B (cur A+OLD+B) -> NEW   <- the shape that used to fall through
    """
    n = min(len(proposed), len(current))
    i = 0
    while i < n and proposed[i] == current[i]:
        i += 1
    j = 0
    # the suffix scan must not run back past the prefix it already consumed, or a proposal that merely
    # reorders text could report an empty difference and be called APPLIED on no evidence.
    while j < n - i and proposed[len(proposed) - 1 - j] == current[len(current) - 1 - j]:
        j += 1
    return i, len(proposed) - j


def build_probe(proposed, current, min_chars=None, max_chars=None):
    """The probe every status decision rests on: text that is ABSENT before the edit lands and PRESENT
    after. Returns (probe, discriminating). PURE.

    ⚠ THE DIFFERENCE ALONE IS NOT ALWAYS USABLE, and assuming it is broke a live check (measured
    2026-08-03). `5b-T` flips an ORDERED-PLAN checkbox `[ ]` -> `[x]`: the introduced text is the single
    character `x`, far too short to mean anything in a 6,000-line document, so a bare difference-probe
    reports the applied edit as a DEAD ANCHOR. So the window is WIDENED around the difference until it is
    long enough to be meaningful — the widened probe still straddles the change, so it is still absent
    before and present after.

    ⛔ AND WIDENING IS ONLY SAFE IF IT STAYS DISCRIMINATING. Widening a short APPEND backwards would
    otherwise swallow enough of `current_text` to match the document before the edit — the exact false
    APPLIED this function exists to prevent. So the result is checked against `current_text` and reported
    NOT discriminating rather than guessed at; a caller that gets `discriminating=False` must fall back to
    `current_text` counting instead of manufacturing an APPLIED.
    """
    min_chars = MIN_PROBE_CHARS if min_chars is None else min_chars
    max_chars = PROPOSED_PROBE_CHARS if max_chars is None else max_chars
    if not current:
        # nothing to diff against: the whole proposal is the probe, which is the right answer here
        probe = proposed.strip()[:max_chars]
        return probe, len(probe) >= min_chars
    start, end = _introduced_span(proposed, current)
    if end <= start:
        return "", False                      # a pure deletion introduces nothing probeable
    while (end - start) < min_chars and (start > 0 or end < len(proposed)):
        if start > 0:
            start -= 1
        if end < len(proposed):
            end += 1
    probe = proposed[start:end].strip()[:max_chars]
    return probe, bool(probe) and len(probe) >= min_chars and probe not in current


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
        # ⚠ THE PROBE IS THE PART OF `proposed_text` THAT IS NOT ALREADY IN `current_text`, AND THAT
        # DISTINCTION IS LOAD-BEARING (2026-08-03, caught on live data before it did damage).
        # Many edits APPEND rather than replace — `proposed_text == current_text + " ✅ new clause"`.
        # For those, `current_text` is STILL in the document after the edit lands, so a status decided by
        # `current_text` alone reports OK forever and a second routing pass appends the clause AGAIN.
        # Probing a PREFIX would be just as wrong in the other direction: for an append edit the first
        # 120 characters of `proposed_text` are `current_text`, which is present BEFORE the edit lands,
        # so every append edit would report APPLIED before it had been.
        # Probing the DIFFERENCE is correct in both shapes: absent before, present after.
        # A truncated probe rather than the whole string, because a proposed replacement is routinely
        # restyled as it lands (a link rewritten, a date localised) and an exact full match would report
        # a landed edit as dead.
        # ⛔ THE THIRD SHAPE, AND IT WAS SILENTLY BROKEN (measured 2026-08-03, on live C24 edits before
        # they were routed). The two branches this used to have — `proposed` starts with `current`
        # (append) or ends with it (prepend) — do not cover a MID-LINE REPLACEMENT, which is what
        # `map_edits.replace_in_line` produces and what most instrument-table and coverage-matrix edits
        # are. For those, `proposed` neither starts nor ends with `current`, so the old code fell through
        # to `probe_src = prop` and probed the FIRST 120 CHARACTERS OF THE WHOLE LINE. On a long table row
        # the replacement sits far past character 120, so those 120 characters are byte-identical to the
        # line already in the document — the probe matched, the status came back APPLIED, and the edit was
        # SKIPPED WITHOUT EVER BEING APPLIED while the router printed a clean run. Two of the C24 edits
        # (the `V17` and `R8` rows, the two places the map says no percentile may be quoted for C397) hit
        # exactly this and would have been dropped.
        # The fix generalises the same idea instead of adding a third special case: strip the common
        # PREFIX and the common SUFFIX, and probe what is left — the text the edit actually introduces.
        # It reduces to the old behaviour for append and prepend, and is correct for replacement.
        prop = (e.get("proposed_text") or "")
        cur = (e.get("current_text") or "")
        probe, discriminating = build_probe(prop, cur)
        n_proposed = text.count(probe) if discriminating else 0
        e["_probe_is_the_difference"] = bool(cur)
        e["_probe_is_discriminating"] = discriminating
        if not discriminating:
            # ⚠ An unusable probe is NOT evidence the edit has not landed. Say so, so a reader can tell
            # "we looked and it was absent" from "we could not look".
            e["_probe_why_not"] = ("no probe of this edit could be both long enough to be meaningful and "
                                   "absent from its own current_text, so APPLIED could not be tested and "
                                   "the status below rests on current_text alone")
        e["anchor_occurrences"] = n_anchor
        e["current_text_occurrences"] = n_current
        e["proposed_text_occurrences"] = n_proposed
        e["_proposed_probe_chars"] = len(probe)
        # The apply target is `current_text`; `anchor` is the human locator. Both are reported, and the
        # STATUS is decided by `current_text`, because that is what a mechanical apply would search for.
        # ⛔ `APPLIED` IS TESTED FIRST, AND THAT ORDER IS THE POINT. The question "has this edit's effect
        # already landed" outranks "can this edit still be applied", because for an append-style edit
        # BOTH are true at once and acting on the second one applies it twice.
        if n_proposed >= 1:
            e["anchor_status"] = "APPLIED"
        elif n_current == 1:
            e["anchor_status"] = "OK"
        elif n_current > 1:
            e["anchor_status"] = "AMBIGUOUS"
        else:
            e["anchor_status"] = "NOT_FOUND"
        out.append(e)

    unresolved = [e for e in out if e.get("anchor_status") in ("NOT_FOUND", "AMBIGUOUS", "UNREAD")]
    summary = {
        "map": os.path.relpath(path, HERE),
        "map_read": read_ok,
        "map_read_why": why,
        "n_edits": len(out),
        "n_ok": sum(1 for e in out if e.get("anchor_status") == "OK"),
        "n_applied": sum(1 for e in out if e.get("anchor_status") == "APPLIED"),
        "not_found": [e.get("section") for e in out if e.get("anchor_status") == "NOT_FOUND"],
        "ambiguous": [e.get("section") for e in out if e.get("anchor_status") == "AMBIGUOUS"],
        "unread": [e.get("section") for e in out if e.get("anchor_status") == "UNREAD"],
        "all_applicable": bool(out) and all(e.get("anchor_status") == "OK" for e in out),
        # ★ THE FIELD CALLERS SHOULD GATE ON. `all_applicable` answers "can every edit still be applied",
        # which goes FALSE the moment one lands — correct for a pre-apply check, wrong as a health signal.
        # `all_accounted` answers "is every edit either applicable or already applied", which is the
        # question a build should be red about.
        "all_accounted": bool(out) and not unresolved,
        "_rule": "a routed edit whose current_text is not present EXACTLY ONCE cannot be applied "
                 "mechanically and must be rewritten, not applied by judgement — UNLESS its proposed_text "
                 "is present, which means it already landed and there is nothing to do",
    }
    return out, summary


def check():
    LANDED = "this edit has already landed in the document verbatim, all of it"
    doc = ("# T\n\nalpha unique line\n\nrepeated token\n\nrepeated token\n\n%s\n" % LANDED)
    edits = [
        {"section": "a", "anchor": "alpha", "current_text": "alpha unique line",
         "proposed_text": "beta replacement text that is long enough to probe", "why": "w",
         "artifact": "x.json"},
        {"section": "b", "anchor": "repeated token", "current_text": "repeated token",
         "proposed_text": "beta replacement text that is long enough to probe", "why": "w",
         "artifact": "x.json"},
        {"section": "c", "anchor": "gone", "current_text": "nowhere in the file",
         "proposed_text": "also nowhere in the file, not one character of it", "why": "w",
         "artifact": "x.json"},
        {"section": "d", "anchor": "alpha", "current_text": "alpha unique line"},
        {"section": "e", "anchor": "landed", "current_text": "the text this replaced, now gone",
         "proposed_text": LANDED, "why": "w", "artifact": "x.json"},
    ]
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(doc)
        p = fh.name
    got, summary = verify(edits, p)
    assert [e["anchor_status"] for e in got] == ["OK", "AMBIGUOUS", "NOT_FOUND", "OK", "APPLIED"], \
        [e["anchor_status"] for e in got]
    assert summary["all_applicable"] is False
    assert summary["all_accounted"] is False, "b and c are unresolved"
    assert summary["ambiguous"] == ["b"] and summary["not_found"] == ["c"]
    assert summary["n_applied"] == 1
    assert got[3]["_schema_complete"] is False and "why" in got[3]["_schema_missing"]

    # ★ THE REGRESSION THIS STATE EXISTS FOR: a set in which EVERY edit has landed must be ACCOUNTED FOR
    # (green), not fifteen dead anchors. That was `main`'s state on 2026-08-03.
    got, summary = verify([edits[4]], p)
    assert summary["all_accounted"] is True and summary["all_applicable"] is False
    assert summary["n_applied"] == 1 and not summary["not_found"]

    # ...and a too-short proposed_text may never manufacture an APPLIED out of a common word.
    got, _ = verify([{"section": "f", "anchor": "x", "current_text": "not here at all",
                      "proposed_text": "alpha", "why": "w", "artifact": "x.json"}], p)
    assert got[0]["anchor_status"] == "NOT_FOUND", "a 5-character probe is not evidence of anything"

    # ★ THE APPEND-EDIT ROUND TRIP. `proposed = current + tail`: OK before, APPLIED after, and never
    # OK after — because OK after would apply the tail a second time.
    append = {"section": "g", "anchor": "alpha", "current_text": "alpha unique line",
              "proposed_text": "alpha unique line  ADDENDUM: a clause long enough to probe against",
              "why": "w", "artifact": "x.json"}
    got, _ = verify([append], p)
    assert got[0]["anchor_status"] == "OK", "before it lands, the appended clause is absent"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(doc.replace(append["current_text"], append["proposed_text"], 1))
        p2 = fh.name
    got, summary = verify([append], p2)
    assert got[0]["anchor_status"] == "APPLIED", \
        "after it lands, current_text is STILL present — deciding on it alone appends twice"
    assert summary["all_accounted"] is True
    os.unlink(p2)

    os.unlink(p)
    got, summary = verify(edits, p + ".missing")
    assert all(e["anchor_status"] == "UNREAD" for e in got)
    assert summary["all_applicable"] is False, "an unread map can never report every edit applicable"
    assert summary["all_accounted"] is False, "nor accounted for"
    assert verify([], DEFAULT_MAP)[1]["all_applicable"] is False, "no edits is not 'all applicable'"
    assert verify([], DEFAULT_MAP)[1]["all_accounted"] is False
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
    # Gate on `all_accounted`, not `all_applicable`: an edit that has LANDED is a success, and exiting
    # non-zero on it would make applying a routed edit the thing that breaks the build.
    sys.exit(0 if summary["all_accounted"] else 1)
