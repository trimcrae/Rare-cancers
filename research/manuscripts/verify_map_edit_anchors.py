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

⚠ THE TWO CORRECTIONS ABOVE WERE MADE INDEPENDENTLY, IN PARALLEL, AND THEY CONFLICTED IN GIT. Keeping only
one would have been a real loss in either direction: the retired predicate makes every verdict wrong, and
the hard-wired path is why nobody ran it to notice. They are merged here deliberately, not reconciled by
picking a winner -- the failure mode this whole file exists to catch is an edit silently dropped because
two people touched the same lines.
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

DEFAULT_ARTIFACT = os.path.join(HERE, "three-row-audit-map-edits.json")

#: `NOT_FOUND`/`AMBIGUOUS`/`UNREAD` are the unresolved states -- see `map_edit_anchors.verify()`. `OK`
#: (applicable), `APPLIED` (landed) and `UNANCHORED` (deferred by contract) are all accounted for.
UNRESOLVED = ("NOT_FOUND", "AMBIGUOUS", "UNREAD")


def _materialise(ref, relpath):
    """The file's content at `ref`, written to a temp path so `verify()` can open it. None if absent."""
    if ref == "WORKTREE":
        p = os.path.join(ROOT, relpath)
        return p if os.path.exists(p) else None
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (ref, relpath)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    fh = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    fh.write(r.stdout)
    fh.close()
    return fh.name


def main(artifact=None, refs=("origin/main", "WORKTREE")):
    artifact = artifact or DEFAULT_ARTIFACT
    edits = json.load(open(artifact, encoding="utf-8"))["map_edits_required"]
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
