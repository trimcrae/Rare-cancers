#!/usr/bin/env python3
"""
Refuse to publish a FAILURE STUB over a real artifact.

WHY (2026-08-03). `depmap-dependency.yml` runs most of its scans behind
`|| echo "... soft-fail (network); non-blocking"`, so a step that could not reach its data source
still exits 0 — and several of those scripts write a *placeholder* JSON on the way out
(`emc_fet_idr_census.py` writes `{"_status": "sequences missing, cannot compute: [...]",
"_remedy": "..."}`). The publish step then committed that placeholder on top of the good artifact.
That is how `research/modalities/emc-fet-idr-census.json` came to be a 2-key stub on `main` while
`research/manuscripts/emc-post-degrader-options.md` on `main` printed a full results table out of it
— CLAUDE.md §7 harm #1, an artifact that reads as a current fact and is not one.

THE TEST, deliberately the dumbest one that works: **a JSON object whose every top-level key starts
with `_` carries no data.** Every real artifact in this folder has data keys (`depmap_release`,
`positive_controls`, `wild_type_annotation`, gene names, ...); the meta/provenance keys these
modules write are `_`-prefixed by convention. So "all keys are meta" == "nothing was computed".
No size heuristic, no threshold to tune, and nothing to keep in sync with the scripts.

⚠ It is a ONE-WAY guard. It can only stop a stub from landing; it can never delete or shrink what is
already committed. A dropped file simply is not staged, so the previously-published version survives
on the branch untouched.

Usage (from the workflow):
    python3 research/modalities/artifact_stub_guard.py --stage "$RUNNER_TEMP/res" \
        research/modalities/foo.json research/modalities/bar.png
Copies each existing path into the staging dir, skipping stubs. Missing paths are skipped quietly
(a scan that never ran has nothing to publish). Prints one line per decision.

⚠ EXIT CODE, AND A DELIBERATE AMENDMENT (2026-08-09). This said "exits 0 always — the guard must
never be the reason a publish step fails", and for its original job that is still exactly right: a
soft-failed scan writing a stub is a normal RUNTIME condition, the previous artifact survives, and
failing the publish over it would help nobody.
⛔ A MISCONFIGURED PATH LIST IS NOT A RUNTIME CONDITION — it is an authoring error, and the two must
not share an exit code. `--publishable-root` makes the CLI refuse, loudly and non-zero, a path this
mechanism provably cannot deliver (see PUBLISHABLE_ROOT below for the incident). Stubs still exit 0.
"""

import argparse
import json
import os
import shutil
import sys


def is_stub(path):
    """True if `path` is a JSON object carrying only `_`-prefixed meta keys (see module docstring).

    Non-JSON files (charts) and JSON that is not an object are never stubs. Unparseable JSON IS
    treated as a stub — a truncated write is not something to publish either.
    """
    if not path.endswith(".json"):
        return False
    try:
        with open(path) as fh:
            doc = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"  STUB (unparseable JSON: {exc}) {path}", file=sys.stderr)
        return True
    if not isinstance(doc, dict):
        return False
    if not doc:
        return True
    return all(str(k).startswith("_") for k in doc)


#: ⛔ THIS STAGING IS FLAT, AND THE PUBLISHERS THAT CONSUME IT REBUILD THE DESTINATION PATH FROM THE
#: BASENAME ALONE — `cp "$p" "research/modalities/$(basename "$p")"`. So an artifact that does not
#: LIVE under research/modalities/ cannot survive a round trip: it is staged fine, published fine,
#: and lands in the wrong directory while every step reports success.
#: ⚠ MEASURED 2026-08-09. A figure-provenance stamp whose real home is
#: research/manuscripts/figures/ was added to a stage list. The run went green, the file was
#: committed to research/modalities/figure-provenance.json, the stamp at the path its test reads was
#: never touched, and the build stayed red for a reason that now looked unrelated to the change that
#: caused it. The publish mechanism had no way to honour the path and no way to say so.
#: ⭐ The fix is the REFUSAL, not a smarter copy. Making staging preserve paths would change a
#: contract two publish blocks and every lane depend on; refusing a path the mechanism provably
#: cannot deliver costs nothing and turns a silent misfile into a build failure at the point of the
#: mistake. Anything living elsewhere needs its own publish step (see depmap-dependency.yml).
PUBLISHABLE_ROOT = "research/modalities"


def _publishable(p, root=PUBLISHABLE_ROOT):
    """Is this a path the flat stage->publish round trip can actually deliver?"""
    return os.path.dirname(os.path.normpath(p)).replace(os.sep, "/") == root


def stage(paths, dest, publishable_root=None):
    """Copy non-stub artifacts into `dest`.

    ⚠ `publishable_root` IS OPT-IN AND DEFAULTS OFF, WHICH IS A CORRECTION. The first version of
    this check was hardcoded into the function body, and it immediately failed
    `test_stage_drops_stubs_and_keeps_the_rest` — a legitimate unit test that stages from a tmp_path.
    A guard that makes its own function untestable is too rigid to be right: the constraint belongs
    to the CLI boundary the workflow calls, not to the copy itself. `main()` supplies it.
    """
    os.makedirs(dest, exist_ok=True)
    # ⛔ Checked BEFORE anything is copied, so a bad list fails the step whole rather than publishing
    # the good half and misfiling the rest — a partial publish is the harder failure to spot.
    misplaced = [p for p in paths if publishable_root and not _publishable(p, publishable_root)] \
        if publishable_root else []
    if misplaced:
        raise SystemExit(
            "⛔ REFUSING TO STAGE: these paths are not under "
            f"{publishable_root}/, and the publishers rebuild every destination from the basename "
            "alone — so they would be committed to the wrong directory while every step reported "
            f"success:\n  " + "\n  ".join(misplaced) +
            "\nGive anything outside that directory its own publish step; do not add it here.")
    kept, dropped = [], []
    for p in paths:
        if not os.path.exists(p):
            print(f"  absent, nothing to publish: {p}")
            continue
        if is_stub(p):
            print(f"  ⛔ STUB — NOT published, the committed version survives: {p}")
            dropped.append(p)
            continue
        shutil.copy2(p, os.path.join(dest, os.path.basename(p)))
        print(f"  staged: {p}")
        kept.append(p)
    print(f"staged {len(kept)} artifact(s); dropped {len(dropped)} stub(s)")
    return kept, dropped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True, help="staging directory to copy non-stub artifacts into")
    ap.add_argument("paths", nargs="*", help="candidate artifact paths")
    ap.add_argument("--publishable-root", default=PUBLISHABLE_ROOT,
                    help="refuse any path not directly under this directory, because the publishers "
                         "rebuild every destination from the basename alone. Pass an empty string to "
                         "disable (unit tests stage from tmp_path and legitimately need that).")
    args = ap.parse_args(argv)
    stage(args.paths, args.stage, publishable_root=args.publishable_root or None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
