#!/usr/bin/env python3
"""Verify a routed map-edits file's edits against the LIVE documents. ($0, pure stdlib)

The categorical audit emitted nine verbatim edits and all nine failed to apply because the documents moved
underneath them; this is the check that prevents a repeat. It verifies against BOTH `origin/main` and the
working tree, because several lanes edit these documents concurrently and an edit that is applicable in one
tree and dead in the other is a fact a router needs before it writes.

⛔ THE PREDICATE WAS THE RETIRED ONE, AND THAT IS WHY THIS SCRIPT WAS RED FOR DAYS (corrected 2026-08-07).
It asserted `count(anchor) == 1 and count(current_text) == 1` and reported FAIL on all 13 edits × 2 refs.
Twelve of the thirteen had **landed** -- their `current_text` was absent precisely because their
`proposed_text` had replaced it -- so the script went red at the exact moment routing SUCCEEDED, and its
only stable green state was "nobody applied anything". That is the identical defect the roadmap records
being fixed in `tests/test_linker_library_canonical.py` and again in `test_nr4a3_5bt` on 2026-08-03; this
was the **third** instance, and it survived because **no test and no workflow ever ran this file**, so
nothing could report that it had rotted. It is now exercised by
`research/manuscripts/tests/test_verify_map_edit_anchors.py`.

⚠ NOTHING IS LOOSENED BY THE CORRECTION. `AMBIGUOUS` is still a failure, a genuinely relocated anchor is
still `NOT_FOUND` and still a failure, and an edit with no probeable `proposed_text` still cannot reach
`APPLIED`. The one home of the discriminator is `research/modalities/map_edit_anchors.verify()` -- this
script does not reimplement it, which is the point.

⚠ AND IT VERIFIES EACH EDIT AGAINST ITS OWN `file`. Three of the thirteen edits target
`map-merge-inventory.md` and `nr4a3-degrader-paper.md`, not the roadmap; resolving every edit against the
roadmap reports all three as dead anchors when all three have landed.

⭑ TAKES AN OPTIONAL PATH (2026-08-07). It was hard-wired to one edit set, so every later pass either could
not use it or had to copy it -- and a verifier nobody can point at a new file is a verifier that stops
being run. The default is unchanged, so existing invocations behave identically.

⚠ THREE CORRECTIONS TO THIS FILE WERE MADE INDEPENDENTLY AND IN PARALLEL, AND ALL THREE CONFLICTED IN GIT.
Keeping any one alone would have been a real loss: the retired predicate makes every verdict wrong, the
hard-wired path is why nobody ran it to notice, and the single-shape reader silently returns "no edits" on
half the artifacts this repo emits. They are merged deliberately rather than reconciled by picking a
winner -- the failure mode this whole file exists to catch is an edit silently dropped because two people
touched the same lines, and it very nearly happened to the checker itself.

⚠ A FOURTH PARALLEL FIX ARRIVED AFTER THE THREE ABOVE and is partly folded in: it added an existence
check and an echo of the resolved path, both kept. Its predicate half is NOT kept — it restored
`count(anchor) == 1 and count(current_text) == 1`, the retired rule that goes red exactly when routing
succeeds. Four agents fixed this one file independently in a day, three of them correctly and one
regressively; that is worth recording, because the reason is that no test and no workflow ran it.

⭑ AN ALREADY-APPLIED EDIT IS `OK`, NOT `FAIL`. `route_map_edits.py` is idempotent and reports
`already_applied`; this must agree with it, or re-verifying after a successful routing turns a correct
state red and invites someone to "fix" it by re-applying. `map_edit_anchors.verify()` is the one home of
that discriminator and is why this script does not reimplement it.

Usage:  python3 research/manuscripts/verify_map_edit_anchors.py [artifact.json ...]
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "research", "modalities"))

import map_edit_anchors as mea  # noqa: E402

DEFAULT_ARTIFACT = os.path.join(HERE, "degrader", "three-row-audit-map-edits.json")

#: `NOT_FOUND`/`AMBIGUOUS`/`UNREAD` are the unresolved states -- see `map_edit_anchors.verify()`. `OK`
#: (applicable), `APPLIED` (landed) and `UNANCHORED` (deferred by contract) are all accounted for.
UNRESOLVED = ("NOT_FOUND", "AMBIGUOUS", "UNREAD")


def _same_basename_at(ref, relpath):
    """The path `relpath`'s basename occupies at `ref`, when the file sits elsewhere in that tree.

    ⛔ THE EXACT CASE THIS WHOLE SCRIPT EXISTS FOR, ARRIVING FROM THE OTHER DIRECTION. Its header
    records nine edits that died because "the documents moved underneath them". A reorganisation makes
    the same thing happen across REFS rather than across time: on 2026-08-12 the manuscripts were sorted
    into per-route folders, so an edit written against `research/manuscripts/degrader/x.md` cannot be
    read at `origin/main`, where that file is still `research/manuscripts/x.md`. Without this the script
    reports `UNREAD` — an unresolved state, i.e. a failure — for every edit whose document moved, which
    says "this edit is dead" about an edit that is perfectly applicable.

    ⚠ ONLY AN UNAMBIGUOUS MATCH IS ACCEPTED. Two files sharing a basename at that ref means the identity
    is a guess, and guessing which document an edit targets is worse than declaring it unread.
    """
    r = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", ref,
                        "research/manuscripts/"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    base = os.path.basename(relpath)
    hits = [p for p in r.stdout.splitlines() if os.path.basename(p) == base]
    return hits[0] if len(hits) == 1 else None


def _materialise(ref, relpath):
    """The file's content at `ref`, written to a temp path so `verify()` can open it. None if absent."""
    if ref == "WORKTREE":
        p = os.path.join(ROOT, relpath)
        return p if os.path.exists(p) else None
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (ref, relpath)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        moved = _same_basename_at(ref, relpath)
        if moved is None:
            return None
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (ref, moved)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return None
    fh = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    fh.write(r.stdout)
    fh.close()
    return fh.name


def _all_edit_dicts(doc):
    """Every dict that looks like a routed edit, regardless of shape or edit KIND."""
    blk = doc if isinstance(doc, list) else doc.get("map_edits_required", doc)
    if isinstance(blk, list):
        return [e for e in blk if isinstance(e, dict)]
    if isinstance(blk, dict):
        for v in blk.values():
            if isinstance(v, list) and any(isinstance(e, dict) for e in v):
                return [e for e in v if isinstance(e, dict)]
    return []


def edits_of(doc):
    """Both emitted shapes: a top-level list, and a list nested under `map_edits_required`.

    ⚠ AGENTS EMIT BOTH, and a reader that knows only one returns an empty list rather than failing --
    which this script would then print as "0 edits x 2 refs -- 0 unresolved", i.e. a clean bill of health
    for an artifact it never read. An absent reading is not a reading of absence.
    """
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


def main(artifact=None, refs=("origin/main", "WORKTREE")):
    artifact = artifact or DEFAULT_ARTIFACT
    if not os.path.exists(artifact):
        print("no such map-edits file: %s" % artifact, file=sys.stderr)
        return 2
    # ⭑ ECHO WHAT WAS ACTUALLY VERIFIED. A fourth independent fix to this file (2026-08-07) diagnosed the
    # class precisely: every session told to "verify your map-edits JSON with this script" could read a
    # green result that belonged to a DIFFERENT file, and nothing in the output distinguished the two.
    # The path argument is honoured above; printing the resolved artifact is what makes that CHECKABLE by
    # the reader rather than merely true. A pass a reader cannot attribute is not a pass.
    print("verifying %s" % os.path.relpath(artifact, ROOT))
    doc = json.load(open(artifact, encoding="utf-8"))
    edits = edits_of(doc)
    if not edits:
        # ⚠ TWO DIFFERENT STATES, AND CONFLATING THEM SENDS A READER HUNTING A BUG THAT IS NOT THERE.
        # A routed artifact may carry FIELD edits (`current_fields`/`proposed_fields` on a graph record)
        # rather than TEXT edits (`current_text` against a document anchor). This checker verifies text
        # anchors; a file of field edits is not malformed and not unverified-by-accident, it is simply
        # out of scope, and it must not be reported as "carries no applicable edits".
        n_field = sum(1 for e in _all_edit_dicts(doc) if "current_fields" in e)
        if n_field:
            print("%s: 0 text-anchor edits; %d FIELD edit(s) -- out of scope for this checker, "
                  "verify them against the graph schema instead" % (os.path.basename(artifact), n_field))
            return 0
        print("::error::%s carries no applicable edits" % artifact)
        return 1
    bad = 0
    for e in edits:
        for ref in refs:
            path = _materialise(ref, e["file"])
            if path is None:
                # ⚠ AN UNREADABLE FILE IS NOT A VERIFIED ANCHOR. Absent reading, absent verdict.
                print("FAIL %3s %-11s UNREAD      %s" % (e["id"], ref, e["file"].split("/")[-1]))
                bad += 1
                continue
            got, _ = mea.verify([e], path)
            st = got[0]["anchor_status"]
            if path != os.path.join(ROOT, e["file"]):
                os.unlink(path)
            ok = st not in UNRESOLVED
            if not ok:
                bad += 1
            print("%s %3s %-11s %-11s %s" % ("OK  " if ok else "FAIL", e["id"], ref, st,
                                             e["file"].split("/")[-1]))
    print()
    print("%s: %d edits x %d refs -- %d unresolved"
          % (os.path.basename(artifact), len(edits), len(refs), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
