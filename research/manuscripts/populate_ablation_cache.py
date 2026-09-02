#!/usr/bin/env python3
"""Fill the claim-ablation cache, once, in parallel — the only way to make it hit.

⛔⛔ WITHOUT THIS FILE THE CACHE IS UNMAINTAINABLE, AND THAT IS THE REASON IT IS COMMITTED RATHER
THAN LEFT IN A SCRATCHPAD. `claim_ablation_cache` keys every verdict on the guard SOURCES behind it,
so editing any guard — a real assertion, or a docstring, the key cannot tell them apart and must not
try — makes every sentence that guard witnesses a miss. The sweep is then as slow as it was before
the cache existed, silently, and the only remedy is to run it again. A remedy that lives in one
session's `/tmp` is not a remedy.

★ WHAT IT COSTS AND WHY IT IS SHARDED. One ablation is 17.4 s (clone the tree, perturb the sentence,
re-run every credited witness); 184 covered sentences is 53 minutes serially. Four processes take
**18 minutes** on a 4-core box, measured 2026-09-02.
⛔ FOUR PROCESSES, NEVER FOUR THREADS, AND NEVER ONE PROCESS WRITING FOUR SHARDS. `claim_ablation`
holds its mutation workspace in a module global and `claim_ablation_cache.save` rewrites the whole
file, so two shards in one interpreter would share a workspace and two shards on one path would
clobber each other. Separate processes have neither problem, and the merge at the end is the only
write to the real cache.

⚠ THE TREE MUST NOT MOVE UNDER IT. A guard edited while this runs re-keys everything recorded before
the edit, so the run finishes and the cache still misses. Measured twice on the day this was written:
once by adding a comment to a guard mid-sweep, once by merging a trunk that had touched
`pinned-figures.json`. **Merge first, settle the tree, then populate.**

Usage:
    CLAIM_ABLATION_CACHE_WRITE=1 python3 research/manuscripts/populate_ablation_cache.py [shards]

    # then check it, and commit research/manuscripts/claim-ablation-cache.json
    python3 research/manuscripts/claim_ablation_cache.py --stats
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SHARD_DIR = os.path.join(tempfile.gettempdir(), "claim-ablation-shards")


def rows():
    """Every sentence the ablation gate would ablate at publication depth, in the gate's own terms.

    ⛔ THE POPULATION IS READ FROM THE GATE'S PREDICATES, NEVER RESTATED. `covered`, `states_a_
    quantity` and `ablation_exempt` are the three the gate applies; a copy of them here would drift
    and the cache would then be warm for a set nobody asks about and cold for the set they do.
    """
    import claim_coverage as cc
    import claim_ablation as ca
    out = []
    for paper in cc.COVERAGE_FLOOR:
        for row in cc.census(paper):
            if (row.get("covered") and ca.states_a_quantity(row["sentence"])
                    and not cc.ablation_exempt(paper, row["sentence"])):
                out.append((paper, row))
    return out


def _shard(args):
    index, items = args
    os.environ["CLAIM_ABLATION_CACHE_WRITE"] = "1"
    sys.path.insert(0, HERE)
    import claim_ablation as ca
    import claim_ablation_cache as cache
    cache.CACHE = os.path.join(SHARD_DIR, "shard-%02d.json" % index)
    done = []
    for paper, row in items:
        start = time.time()
        result = ca.ablate(paper, row)
        done.append((paper, row["sentence"], result["status"], bool(result["red"]),
                     result.get("quantity_kind"), result.get("reason", "")[:300]))
        print("[%02d] %5.1fs %-11s %-5s %s"
              % (index, time.time() - start, result["status"],
                 "RED" if result["red"] else "blind" if result["status"] == ca.APPLIED else "-",
                 row["sentence"][:80]), flush=True)
    return done


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    shards = int(argv[0]) if argv else max(1, (os.cpu_count() or 2))
    import claim_ablation_cache as cache
    if not cache.writes_enabled():
        print("REFUSED: set %s=1. This run costs ~18 minutes and would write nothing without it."
              % cache.WRITE_ENV, file=sys.stderr)
        return 2
    os.makedirs(SHARD_DIR, exist_ok=True)
    for stale in os.listdir(SHARD_DIR):
        os.unlink(os.path.join(SHARD_DIR, stale))

    work = rows()
    print("%d covered numbered sentence(s) across %d document(s), %d shard(s)"
          % (len(work), len({p for p, _ in work}), shards), flush=True)
    buckets = [[] for _ in range(shards)]
    for i, item in enumerate(work):
        buckets[i % shards].append(item)

    started = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=shards) as pool:
        for done in pool.map(_shard, list(enumerate(buckets))):
            results.extend(done)
    print("\nsweep wall clock: %.1f min" % ((time.time() - started) / 60), flush=True)

    merged = cache.load()
    for name in sorted(os.listdir(SHARD_DIR)):
        with open(os.path.join(SHARD_DIR, name), encoding="utf-8") as fh:
            merged.update(json.load(fh).get("entries", {}))
    cache.save(merged, note="populated by a %d-way sharded sweep of %d sentence(s)"
                            % (shards, len(work)))
    held = len(cache.load())
    print("cache now holds %d verdict(s)" % held)
    # ⛔ AN EMPTY CACHE AFTER A FULL SWEEP IS THE FAILURE THIS LINE EXISTS FOR, and it is not
    # hypothetical: the first build recorded ZERO entries because `pin:*` was unkeyable, after
    # ablating all 184 sentences correctly. Nothing failed and nothing looked wrong.
    if held < len(work):
        print("::error::%d sentence(s) ablated but only %d verdict(s) cached — some witness set "
              "could not be keyed, so those sentences will re-ablate forever. Run "
              "`claim_ablation_cache.witness_sources` over the gate's witness sets and find the "
              "kind it cannot read." % (len(work), held), file=sys.stderr)

    blind = [r for r in results if r[2] == "applied" and not r[3]]
    not_applied = [r for r in results if r[2] != "applied"]
    print("\n%d applied, %d RED, %d BLIND, %d not-applied"
          % (len(results) - len(not_applied), sum(1 for r in results if r[3]),
             len(blind), len(not_applied)))
    for row in blind:
        print("\nBLIND  %s\n  %s\n  %s" % (row[0], row[1][:220], row[5][:220]))
    for row in not_applied:
        print("\nNOT-APPLIED  %s\n  %s\n  %s" % (row[0], row[1][:160], row[5][:200]))
    return 0 if held >= len(work) else 1


if __name__ == "__main__":
    sys.exit(main())
