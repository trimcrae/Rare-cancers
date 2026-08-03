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
(a scan that never ran has nothing to publish). Prints one line per decision and exits 0 always —
the guard must never be the reason a publish step fails.
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


def stage(paths, dest):
    os.makedirs(dest, exist_ok=True)
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
    args = ap.parse_args(argv)
    stage(args.paths, args.stage)
    return 0


if __name__ == "__main__":
    sys.exit(main())
