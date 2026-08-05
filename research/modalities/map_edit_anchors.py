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

#: ⛔ THE PLAN LEFT THE ROADMAP, AND AN ANCHOR RESOLVER THAT KNOWS ONLY THE ROADMAP THEN REPORTS LIVE
#: EDITS AS DEAD. On 2026-08-05 THE ORDERED PLAN, the spend ladder and the dependency spine were lifted
#: out of `nr4a3-program-map.md` into the generated `systems/views/plan.md`. Several modules route edits
#: at plan rows — `fusion_object_inventory` and `antitarget_selfcontrol` both anchor on
#: "THE ORDERED PLAN → RUNG S" — and every one of them started resolving to NOT_FOUND.
#:
#: ⚠ THAT FAILURE IS THE DANGEROUS DIRECTION. `verify()`'s whole job is to distinguish "this edit
#: applies to real text" from "this anchor is dead and the edit reads as done". Reporting a live anchor
#: as dead invites someone to relocate an edit that never moved.
#:
#: So the map is now the PAIR of files that between them hold the roadmap's content. It is a search
#: order, not a fallback: a hit in either is a resolved anchor, and `verify()` records WHICH file
#: matched so a reader can tell a roadmap edit from a plan edit.
#: ⚠ An edit anchored in the plan view must be applied in `systems/graph/plan.json`, never in the view —
#: the view is generated and a hand-edit fails its drift check.
COMPANION_MAPS = [os.path.join(HERE, "..", "..", "systems", "views", "plan.md")]


def _map_sources(map_path=None):
    """Every file that jointly holds the roadmap's content, in search order, that exists on this ref.

    ⛔ COMPANIONS ARE ADDED ONLY WHEN THE CALLER IS ASKING FOR *THE LIVE MAP* — either by passing
    nothing, or by naming the roadmap itself. An arbitrary path means exactly that path.

    ⚠ THE FIRST VERSION WIDENED UNCONDITIONALLY AND IT WAS CAUGHT BY THIS MODULE'S OWN TESTS, IN THE
    WORST DIRECTION. A test writes a temp file holding the PRE-edit text and asserts the status is `OK`
    (not yet applied). With the companion always appended, the probe was found in the real
    `systems/views/plan.md` — which legitimately contains the POST-edit text — and the status came back
    `APPLIED`. A false `APPLIED` tells a router an edit has landed when it has not, which is the exact
    failure this module's `build_probe` docstring spends thirty lines guarding against.
    """
    primary = os.path.abspath(map_path or DEFAULT_MAP)
    out = [primary]
    if primary != os.path.abspath(DEFAULT_MAP):
        return out
    for p in COMPANION_MAPS:
        p = os.path.abspath(p)
        if p not in out and os.path.exists(p):
            out.append(p)
    return out

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
    # ⚠ THE LOOP MUST MEASURE WHAT IT WILL ACTUALLY USE, i.e. the STRIPPED window (measured 2026-08-03,
    # caught by routing the C24 edits twice). Widening on the raw slice length and stripping afterwards
    # let a 25-character window become a 23-character probe — one below the floor — so `discriminating`
    # came back False and an edit that HAD landed was reported as a DEAD ANCHOR. Milder than a false
    # APPLIED, and still wrong: it turns a correctly-applied edit into a red guard.
    while len(proposed[start:end].strip()) < min_chars and (start > 0 or end < len(proposed)):
        if start > 0:
            start -= 1
        if end < len(proposed):
            end += 1
    probe = proposed[start:end].strip()[:max_chars]
    return probe, bool(probe) and len(probe) >= min_chars and probe not in current


#: How far past an edit's anchor to look for a restyled landing. Wide enough for a long table cell,
#: narrow enough that a generic block cannot match somewhere unrelated.
ANCHOR_WINDOW_CHARS = 6000


def _locator(anchor, current, text):
    """Where in `text` to look for a restyled landing, and how far in it starts. Returns -1 if unknown.

    ⚠ THE `anchor` FIELD IS NOT ALWAYS SEARCHABLE TEXT. Several emitters write it as a human location
    description — "row 25's state cell", "the '3 rows wait on a decision' bullet" — which no `find` will
    ever match. For those the region is located by the longest surviving PREFIX of `current_text`, which
    is the right fallback because a partially-edited line is exactly the case being diagnosed: the
    roadmap that says "(7, 8, 28)" still shares every character before the number with an edit written
    against "(7, 8, 25)".
    """
    if anchor:
        i = text.find(anchor)
        if i >= 0:
            return i
    for n in range(len(current), MIN_PROBE_CHARS - 1, -1):
        i = text.find(current[:n])
        if i >= 0:
            return i
    return -1


def _longest_shared_block(probe, anchor, texts, current):
    """The longest contiguous run of `probe` that appears in the region the edit targets. PURE.

    Returns "" unless the block is at least MIN_PROBE_CHARS and is ABSENT from `current` — an
    already-present block would match the document BEFORE the edit landed, which is the false APPLIED
    this whole module is built to prevent. Uniqueness is checked by the caller against all sources.
    """
    import difflib
    best = ""
    for _p, t in texts:
        start = _locator(anchor, current, t)
        if start < 0:
            continue
        region = t[start:start + ANCHOR_WINDOW_CHARS]
        m = difflib.SequenceMatcher(None, probe, region, autojunk=False).find_longest_match(
            0, len(probe), 0, len(region))
        cand = probe[m.a:m.a + m.size].strip()
        if len(cand) >= MIN_PROBE_CHARS and cand not in current and len(cand) > len(best):
            best = cand
    return best


def verify(edits, map_path=None):
    """Annotate each routed edit with its anchor status against the live map. Returns (edits, summary)."""
    # ⚠ THE PRIMARY MAP MUST STILL BE READABLE. If it is not, this is UNREAD — the companion existing is
    # not a substitute, because "absent reading, absent verdict" applies per source, not per set.
    sources = _map_sources(map_path)
    path = sources[0]
    try:
        text = open(path, encoding="utf-8").read()
        read_ok, why = True, None
    except OSError as e:
        text, read_ok, why = "", False, "%s: %s" % (type(e).__name__, e)
    #: {absolute path -> its text} for every source that read, primary first.
    texts = [(path, text)] if read_ok else []
    for p in sources[1:]:
        try:
            texts.append((p, open(p, encoding="utf-8").read()))
        except OSError:
            pass  # a companion that is absent on this ref is not an error; the primary decides UNREAD

    def _count(needle):
        """Occurrences across all readable sources, plus the first source that matched."""
        total, where = 0, None
        for p, t in texts:
            n = t.count(needle)
            if n and where is None:
                where = os.path.relpath(p, os.path.join(HERE, "..", ".."))
            total += n
        return total, where

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
        # ⛔ `current_text: null` IS A CONTRACT, NOT A BUG — `route_map_edits.py`'s own docstring says so
        # (a DERIVED count must be regenerated, never typed, so the edit is deliberately unanchored). But
        # `text.count(None)` raises TypeError, and `verify()` runs over EVERY edit before the router's own
        # `cur is None` branch is reached — so one deferred edit took the whole routing pass down with a
        # traceback, and every other edit in that artifact went unapplied. Measured 2026-08-03 on a live
        # block. An unanchored edit is now reported as UNANCHORED and skipped, which is what the contract
        # already said it was.
        anchor_s, current_s = e.get("anchor"), e.get("current_text")
        if not isinstance(current_s, str) or not isinstance(anchor_s, str):
            e["anchor_status"] = "UNANCHORED"
            e["anchor_occurrences"] = None
            e["current_text_occurrences"] = None
            e["anchor_why"] = ("this edit carries no anchor and/or no current_text — deferred by design "
                               "(a derived count is regenerated, never typed), so there is nothing to "
                               "locate and nothing to apply")
            out.append(e)
            continue
        n_anchor, anchor_in = _count(anchor_s)
        n_current, current_in = _count(current_s)
        # Which file the anchor resolved in — a roadmap edit and a plan-view edit have DIFFERENT
        # application routes (the view is generated; its edits belong in systems/graph/plan.json), so
        # a reader must not have to guess which one they are holding.
        e["anchor_found_in"] = anchor_in or current_in
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
        n_proposed = _count(probe)[0] if discriminating else 0
        # ⛔ A LANDED EDIT THAT WAS LATER RESTYLED STILL LANDED — and without this it reads as DEAD.
        # `build_probe` widens around the difference to reach MIN_PROBE_CHARS, but it takes the WHOLE
        # widened window as the probe. When the routed text lands and the roadmap is then edited FURTHER
        # inside that window — a clause appended, a figure inserted, the whole thing wrapped in a
        # "⚠ Superseded, retained:" marker — the exact match fails and the status flips to NOT_FOUND.
        # Measured 2026-08-05 on `main`: two of the three edits that were keeping CI red were of exactly
        # this shape, their first 30 and 50 characters sitting in the roadmap untouched.
        #
        # ⚠ SHORTENING GLOBALLY WOULD BE THE WRONG FIX — a short probe risks the false APPLIED this whole
        # module is built to prevent. So the retry is narrow and every condition is required:
        #   · only after the FULL probe has already missed (never as the first answer);
        #   · never below MIN_PROBE_CHARS;
        #   · still absent from `current_text`, so it cannot match the pre-edit document; and
        #   · UNIQUE in the sources, so a short prefix cannot match coincidentally.
        # The shortened length is recorded, so an APPLIED reached this way is never indistinguishable
        # from one matched whole.
        if discriminating and not n_proposed:
            for n in range(len(probe) - 1, MIN_PROBE_CHARS - 1, -1):
                short = probe[:n].rstrip()
                if len(short) < MIN_PROBE_CHARS or short in current_s:
                    continue
                if _count(short)[0] == 1:
                    n_proposed = 1
                    e["_probe_shortened_to"] = len(short)
                    e["_probe_shortened_why"] = (
                        "the full probe missed but this unique prefix is present and is still absent "
                        "from current_text — the edit landed and the text was edited further afterwards")
                    break
        # ⛔ AND THE DIVERGENCE IS NOT ALWAYS AT THE END. The prefix retry above catches an edit that
        # landed and was then EXTENDED. It cannot catch one whose FIRST characters differ — and that is
        # the commoner case here, because several emitters open their proposal with a timestamp.
        # Measured 2026-08-05: `nr4a3_5bt_gate.map_edits` stamps `_et_now()` at EDIT-GENERATION time, so
        # its proposal opens "✅ **RAN 2026-08-03 9:19 AM ET" while the roadmap records 8:29 AM ET.
        # Every character after that clause is identical.
        # ⚠ SUPERSEDED READING, RETAINED: this comment said the roadmap "correctly" recorded 8:29 and the
        # 9:19 was an artefact of when map_edits() ran. Re-measured 2026-08-05 from the producing branch:
        # the committed gate is byte-identical to the 9:19 commit (c682873ca) and NOT to the 8:29 one
        # (615f12f73), which differs materially — NR4A1 arm 15 vs 16 models, p_focus_at_least 0.10506 vs
        # 0.59819. 9:19 is this artifact's real provenance; 8:29 names a superseded run. Verdict `NO-GO`
        # in both, so nothing scientific reversed. The anchor lesson is unchanged either way.
        # A prefix probe diverges at character ten and reports a fully-applied edit as dead.
        #
        # So the last resort is the LONGEST CONTIGUOUS BLOCK the proposal and the document share,
        # searched only in the window that follows the edit's own anchor. The guards are unchanged and
        # all of them are required: the block must reach MIN_PROBE_CHARS, must be ABSENT from
        # `current_text` (so it cannot match the pre-edit document), and must be UNIQUE in the sources.
        # Bounding by the anchor is what keeps this cheap and what stops a long generic block matching
        # somewhere unrelated.
        if discriminating and not n_proposed:
            block = _longest_shared_block(probe, anchor_s, texts, current_s)
            if block and _count(block)[0] == 1:
                n_proposed = 1
                e["_probe_matched_block"] = len(block)
                e["_probe_matched_block_why"] = (
                    "neither the full probe nor any prefix of it matched, but this contiguous block of "
                    "the proposal is present, unique, and absent from current_text — the edit landed in "
                    "a restyled form whose difference is not at the end (a re-stamped time, a reworded "
                    "opening). Reporting it NOT_FOUND would call a landed edit dead")
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
