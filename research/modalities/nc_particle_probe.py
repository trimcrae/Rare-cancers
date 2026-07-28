#!/usr/bin/env python3
"""Print the PARTICLE COUNT of every committed MultiState `.nc` in a directory.

WHY THIS IS THE DECISIVE ARTIFACT. "Which system did this leg actually run?" has been answered three different
wrong ways on this lane, all of them inferences rather than measurements:

  * from which setup caches happen to EXIST in the bucket (an absence is not a measurement);
  * from the leg result JSON, which only gained `setup_cache_dir`/`n_particles` on 2026-07-25, so every leg
    that landed before that records neither;
  * from the commit manifest, which only carries `SETUP_CACHE_VERSION` from schema 2 onward — the older
    prefixes are schema 1 and carry nothing.

The trajectory itself is the one artifact that cannot be silent about it. Its `atom` dimension IS the particle
count, and the two builds genuinely differ: pre-equilibration RE-SOLVATES the complex rather than merely
relaxing it, so v1 and v2pe are 146,020 vs 141,968 particles for the ternary. That difference is what
`assert_multistate_system_equality` uses to refuse a cross-restore, and it is what audit sections J.2-J.5 are
the record of getting wrong — four reverse-leg attempts ran a 146,020-particle v1 build against a forward leg
built at 141,968, and every one died at warmup iteration 1.

WHY A FILE AND NOT AN INLINE `python -c` IN THE WORKFLOW. Two independent reasons, both already paid for once
in this repo. (1) Python lines written at column 0 inside a YAML `run: |` block scalar dedent out of it and
make the whole workflow UNPARSEABLE — and GitHub reports that as a MISSING TRIGGER rather than a syntax error,
so a cron on the file silently never fires. That is why `watchdog_validate.py` exists as a file at all, and
the first cut of this probe reproduced it. (2) A heredoc cannot fix it either: a `<<'EOF'` terminator must sit
at column 0, which is the same collision. A real file is mounted into the pre-baked image and simply run.

READS THE HEADER ONLY — it opens the dataset and reads dimension metadata, never the coordinate arrays, so it
is fast and memory-flat regardless of trajectory length.
"""
import glob
import os
import sys


def particle_count(path):
    """(count, note) for one .nc. Returns (None, reason) rather than raising or guessing — a probe that
    invents a number is worse than one that declines, because this value is used to decide comparability."""
    try:
        import netCDF4
    except ImportError as e:  # pragma: no cover - depends on the image, not on logic
        return None, "netCDF4 unavailable (%s)" % e
    try:
        ds = netCDF4.Dataset(path, "r")
    except Exception as e:  # noqa: BLE001
        return None, "unreadable (%s: %s)" % (type(e).__name__, e)
    try:
        if "atom" in ds.dimensions:
            return len(ds.dimensions["atom"]), "atom dimension"
        # openmmtools writes positions as (iteration, replica, atom, 3); fall back to its shape rather than
        # failing, but SAY which route produced the number so the two are never conflated in a log.
        if "positions" in ds.variables and len(ds.variables["positions"].shape) >= 3:
            return int(ds.variables["positions"].shape[2]), "positions.shape[2]"
        return None, "no atom dimension and no positions variable (dims=%s)" % list(ds.dimensions)
    finally:
        ds.close()


def main(argv):
    root = argv[1] if len(argv) > 1 else "/tmp/nc"
    files = sorted(glob.glob(os.path.join(root, "*.nc")))
    if not files:
        print("  (no .nc files under %s)" % root)
        return 0
    seen = {}
    for f in files:
        n, note = particle_count(f)
        name = os.path.basename(f)[:-3]
        print("  %-70s atoms=%-10s (%s)" % (name, n if n is not None else "UNKNOWN", note))
        if n is not None:
            seen.setdefault(n, []).append(name)
    # Report the grouping, but do NOT rule on it here. Which trajectories are *supposed* to match is a
    # per-leg question (the binary and ternary arms are different systems by construction — the ternary
    # carries a whole extra protein), and that judgement has one home, in the workflow's per-leg verdict.
    # A probe that also adjudicates would be a second place for the rule to drift.
    if len(seen) > 1:
        print("  --- distinct particle counts present: %s ---" % sorted(seen))
        print("      (grouping only — whether any PAIR is supposed to match is decided per leg, not here)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
