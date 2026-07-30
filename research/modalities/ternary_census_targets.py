#!/usr/bin/env python3
"""Pick ONE trajectory per commit prefix — the newest committed generation — from an object listing.

WHY A FILE AND NOT SHELL. The first cut did this with `sed`/`grep`/`awk` inside the workflow and it failed on
the real listing for two reasons at once, both invisible until it ran against production paths:

  1. The commit path is `<prefix>/<phase>/iter-<N>/<uuid>/simulation.nc` — there is a UUID directory BETWEEN
     the iteration and the file. The `sed` that stripped `/iter-N/simulation.nc` therefore matched nothing, so
     every "prefix" was a full object path and no group ever had more than one member.
  2. `NEW=$(grep ... | ...)` under `set -eo pipefail` takes the pipeline's status as the assignment's status,
     so the first prefix that matched nothing killed the whole step — after printing a listing that looked
     complete. (GH run 30353268519, exit 1.)

Both are the same class of bug as the `head`-closes-the-pipe trap this repo has already paid for twice. Pure
stdlib, no network: it reads a listing on stdin or from a file and writes `label<TAB>uri` lines, so it is
testable without either cloud.
"""
from __future__ import annotations

import argparse
import re
import sys

# `<prefix>/<warmup|production>/iter-<N>/...`. The iteration number is the ordering key; everything to its left
# is the commit prefix, which is what identifies the SYSTEM (it is keyed by leg, seed, dt, warmup dt and salt).
ITER_RX = re.compile(r"^(?P<prefix>.+?)/(?P<phase>warmup|production)/iter-(?P<iter>\d+)/")

# Production beats warmup at equal iteration index: they are different phases of the same leg and the
# production generation is the one every downstream analysis uses.
PHASE_RANK = {"warmup": 0, "production": 1}


def pick(lines, include=(), exclude=()):
    """{prefix: (phase, iter, path)} keeping the newest generation per prefix. PURE."""
    best = {}
    for raw in lines:
        path = raw.strip()
        if not path or not path.endswith(".nc"):
            continue
        m = ITER_RX.match(path)
        if not m:
            continue
        pfx = m.group("prefix")
        if include and not any(tok in pfx for tok in include):
            continue
        if any(tok in pfx for tok in exclude):
            continue
        key = (PHASE_RANK.get(m.group("phase"), 0), int(m.group("iter")))
        cur = best.get(pfx)
        if cur is None or key > cur[0]:
            best[pfx] = (key, path)
    return {k: v[1] for k, v in best.items()}


def label_for(prefix):
    """A label that IDENTIFIES the leg, not just its last path segment. PURE.

    ⚠ THE LAST SEGMENT IS NOT UNIQUE, AND ASSUMING IT WAS DESTROYED TWO MEASUREMENTS (GH run 30353705917).
    The GCP lane's layout is `valB-6hax/commits/<leg>/<seed>_dt…_wu…[_salt]/…`, so the ternary, binary and
    solvent legs of one cycle ALL end in the same `0_dt2.0fs_clig0_wu1.0_v2pe` segment. Labelling on that
    segment gave three legs one name, and since each census writes `census__<label>.json` the binary and
    solvent records were silently overwritten by the ternary one — the run reported a confident table with
    two of its rows missing and nothing said so. The Vast lane happens not to collide (its leg id is the last
    segment), which is exactly why the bug was invisible on one store and fatal on the other.

    So the label is everything AFTER the `commits/` segment, joined by `__`.
    """
    parts = [p for p in prefix.split("/") if p]
    if "commits" in parts:
        parts = parts[parts.index("commits") + 1:]
    else:
        parts = parts[-2:]
    return "__".join(parts) or prefix


def main(argv=None):
    ap = argparse.ArgumentParser(description="newest committed .nc per commit prefix, from a listing")
    ap.add_argument("--listing", default="-", help="file of object paths, or - for stdin")
    ap.add_argument("--uri-prefix", default="", help="prepended to each path to form a fetchable URI")
    ap.add_argument("--label-prefix", default="", help="prepended to each emitted label")
    ap.add_argument("--include", default="", help="comma-separated substrings a prefix must contain (any)")
    ap.add_argument("--exclude", default="", help="comma-separated substrings that disqualify a prefix")
    ap.add_argument("--limit", type=int, default=0, help="0 = no cap")
    a = ap.parse_args(argv)

    src = sys.stdin if a.listing == "-" else open(a.listing)
    inc = tuple(t for t in a.include.split(",") if t)
    exc = tuple(t for t in a.exclude.split(",") if t)
    chosen = pick(src, inc, exc)
    for i, (pfx, path) in enumerate(sorted(chosen.items())):
        if a.limit and i >= a.limit:
            break
        sys.stdout.write("%s%s\t%s%s\n" % (a.label_prefix, label_for(pfx), a.uri_prefix, path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
