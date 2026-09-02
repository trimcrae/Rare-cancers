#!/usr/bin/env python3
"""How far the published ASO archive is behind this tree — DERIVED, because a typed one went stale.

⛔⛔ THE EVENT THIS EXISTS FOR, AND IT IS THE THIRD IN A FAMILY. On 2026-09-02 the preprint
checklist's §3-vii declared "15 paths changed, 0 added, 0 removed". It was exactly true when it was
written at `19f9d2b41` and false one commit later at `05c1cac1e` — a commit about the COMMIT LOOP,
which happened to touch three files that are also deposited (`lint_citations.py`,
`pinned-figures.json`, and a `.docx` build stamp). The real figure was 18. Round 31's
citations-and-archive seat caught it; nothing else could have.

★ THE PATTERN, STATED ONCE: the count is a function of 515 deposited paths, so ANY commit anywhere
in the repository can move it, including a commit whose author has no idea the archive exists. A
number like that cannot be maintained by hand — CLAUDE.md §1: "A total is DERIVED, never typed —
regenerate it." Every previous attempt to hold this by hand failed the same way. §3-iv failed it in
August ("IT IS EXACTLY ONE FILE" while the real figure was fifteen); §3-vii failed it in September
within a single commit.

⭐ AND IT DOES NOT CHASE ITS OWN TAIL, WHICH IS THE FIRST THING TO CHECK OF ANY GENERATED COUNT AND
WHICH I GOT WRONG BEFORE MEASURING IT. The reasoning drafted here was "the checklist is itself a
deposited path, so it is already inside `changed` and rewriting it moves the count from N to N".
That conclusion was right and the premise was false: **the preprint checklist is NOT in the
manifest** — verified against the committed file list, 515 paths, and the checklist is not one of
them. Nor is this module. So writing this block changes no deposited byte and cannot move the
number it prints, which is a stronger guarantee than the one first written down, arrived at by
looking rather than by arguing.

⚠ THE ORDER STILL MATTERS, BECAUSE THIS READS THE MANIFEST'S RECORDED DIGESTS. Regenerate the
archive manifest first, then this. A stale manifest does not make this print a stale number — it
makes it print a confident WRONG one, which is worse, and is why `--check` runs in the commit loop
next to the manifest's own.

⚠ IT SAYS NOTHING ABOUT WHETHER THE DRIFT SHOULD BE FIXED. Drift between deposits is the normal
state and a gate demanding a current deposit would be red for weeks and would get switched off
(that argument is `test_a_declared_drift_states_the_size_it_actually_has`'s, and it still holds).
This only makes the stated size the measured one.

Usage:
    python3 research/manuscripts/aso_deposit_drift.py            # rewrite the block
    python3 research/manuscripts/aso_deposit_drift.py --check    # exit 1 if it is stale
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
STATE = os.path.join(HERE, "aso", "deposit-state.json")
MANIFEST_REL = "research/manuscripts/aso/fusion-junction-aso-archive-manifest.json"
MANIFEST = os.path.join(ROOT, MANIFEST_REL)
CHECKLIST = os.path.join(HERE, "aso", "fusion-junction-aso-preprint-checklist.md")

BEGIN = "<!-- BEGIN GENERATED deposit-drift · aso_deposit_drift.py · DO NOT EDIT BY HAND -->"
END = "<!-- END GENERATED deposit-drift -->"


def _git(args):
    return subprocess.run(["git", "-C", ROOT] + args, capture_output=True, text=True)


def _digests_at(rev):
    """`{path: sha256}` as the manifest recorded them at `rev`, or None if it cannot be read.

    ⛔ NONE, NEVER `{}`. An empty map would read as "the published record deposited nothing", which
    makes every path `added` and prints a confident, enormous, wrong number. Unreadable is a state
    this module reports; it is not a measurement.
    """
    shown = _git(["show", "%s:%s" % (rev, MANIFEST_REL)])
    if shown.returncode != 0:
        return None
    try:
        return {f["path"]: f["sha256"] for f in json.loads(shown.stdout)["files"]}
    except (ValueError, KeyError, TypeError):
        return None


def measure():
    """`(rev, changed, added, removed)` or `(rev, None, None, None)` when git cannot see `rev`."""
    state = json.load(open(STATE, encoding="utf-8"))
    rev = (state.get("published") or {}).get("git_revision")
    if not rev:
        return None, None, None, None
    was = _digests_at(rev)
    if was is None:
        # A targeted fetch, for the reason the sibling guard records: CI checks out at depth 1, so
        # a recorded revision is routinely absent until asked for, and a silent skip there means the
        # check never ran at all.
        _git(["fetch", "--quiet", "origin", rev])
        was = _digests_at(rev)
    if was is None:
        return rev, None, None, None
    now = {f["path"]: f["sha256"] for f in json.load(open(MANIFEST, encoding="utf-8"))["files"]}
    changed = sorted(p for p in was if p in now and was[p] != now[p])
    added = sorted(set(now) - set(was))
    removed = sorted(set(was) - set(now))
    return rev, changed, added, removed


def render(rev, changed, added, removed):
    if changed is None:
        return (BEGIN + "\n\n⚠ **The drift cannot be measured here**: git cannot produce the "
                "published record's revision `%s`, so the size of the gap is UNKNOWN — which is not "
                "the same as zero. Run `git fetch origin %s` and regenerate.\n\n" % (rev[:12], rev)
                + END)
    n = len(changed) + len(added) + len(removed)
    if n == 0:
        body = ("✅ **0 paths changed, 0 added, 0 removed** against the published record's manifest "
                "at `%s`. The published archive is what this tree would deposit." % rev[:12])
    else:
        # ⛔ THE TOTAL IS PRINTED FIRST, AND IT IS NOT DECORATION. `test_a_declared_drift_states_
        # the_size_it_actually_has` searches this block for changed+added+removed. While added and
        # removed are both zero that equals `changed` and the guard passes by COINCIDENCE — round
        # 32's regression seat simulated 16 changed + 4 added and the correctly generated block went
        # RED, because no standalone 20 appeared anywhere in it. A generated artifact whose own
        # guard fails the moment the data takes a shape it has not yet taken is a latent false red.
        body = ("⛔ **%d deposited path%s differ** from the published record: **%d changed, %d "
                "added, %d removed** against its own manifest at `%s`.\n\n<details><summary>every deposited path that differs</summary>"
                "\n\n%s\n\n</details>"
                % (len(changed) + len(added) + len(removed),
                   "" if len(changed) + len(added) + len(removed) == 1 else "s",
                   len(changed), len(added), len(removed), rev[:12],
                   "\n".join("* `%s`" % p for p in changed + ["+ " + p for p in added]
                             + ["− " + p for p in removed])))
    return BEGIN + "\n\n" + body + "\n\n" + END


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed block is stale")
    args = ap.parse_args(argv)

    text = open(CHECKLIST, encoding="utf-8").read()
    if BEGIN not in text or END not in text:
        print("::error::%s carries no generated deposit-drift block. The markers are\n  %s\n  %s\n"
              "Add them where the drift is declared; this module owns what goes between them."
              % (os.path.relpath(CHECKLIST, ROOT), BEGIN, END), file=sys.stderr)
        return 1
    head, rest = text.split(BEGIN, 1)
    _old, tail = rest.split(END, 1)
    block = render(*measure())
    new = head + block + tail
    if args.check:
        if new == text:
            return 0
        print("the declared deposit drift is not the measured one. This module owns that block; "
              "rerun it without --check and commit the result.\n"
              "⚠ REGENERATE THE ARCHIVE MANIFEST FIRST — this reads the manifest's digests, so a "
              "stale manifest makes this print a confident wrong number rather than a stale one.",
              file=sys.stderr)
        return 1
    open(CHECKLIST, "w", encoding="utf-8").write(new)
    rev, changed, added, removed = measure()
    print("wrote the deposit-drift block: %s changed, %s added, %s removed against %s"
          % (len(changed) if changed is not None else "UNKNOWN",
             len(added) if added is not None else "UNKNOWN",
             len(removed) if removed is not None else "UNKNOWN", str(rev)[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
