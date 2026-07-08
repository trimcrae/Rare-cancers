#!/usr/bin/env python3
"""Split a funnel candidate JSON into N committed shards for a large sharded dock (e.g. the repurposing screen).

The de-novo dock funnel docks a whole candidate JSON in one smina pass per receptor with NO intra-job
checkpoint, so a multi-thousand-compound library must be split into many small self-contained jobs (each shard
= its own committed JSON + its own S3 output prefix; a failed shard simply re-runs). Sized so each shard job
finishes comfortably inside its SageMaker max_runtime.

Emits: <base>-shard-XX.json (0-padded) covering ALL candidates, plus <base>-shard-shakeout.json (the first
SHAKEOUT_N candidates) to measure smina throughput on one shard before fanning out the rest.
"""
import json
import os
import sys

IN = os.environ.get("IN_JSON", "nr4a3-repurpose-candidates.json")
BASE = os.environ.get("SHARD_BASE", "nr4a3-repurpose")
SHARD_SIZE = int(os.environ.get("SHARD_SIZE", "550"))
SHAKEOUT_N = int(os.environ.get("SHAKEOUT_N", "80"))


def _write(path, meta, cands):
    json.dump({**{k: v for k, v in meta.items() if k != "candidates"},
               "n_candidates": len(cands), "candidates": cands}, open(path, "w"), indent=1)


def main():
    d = json.load(open(IN))
    cands = d["candidates"]
    n = len(cands)
    n_shards = (n + SHARD_SIZE - 1) // SHARD_SIZE
    for i in range(n_shards):
        chunk = cands[i * SHARD_SIZE:(i + 1) * SHARD_SIZE]
        _write(f"{BASE}-shard-{i:02d}.json", d, chunk)
    _write(f"{BASE}-shard-shakeout.json", d, cands[:SHAKEOUT_N])
    print(f"{n} candidates -> {n_shards} shards of {SHARD_SIZE} (+ shakeout of {SHAKEOUT_N})")
    print(f"shards: {BASE}-shard-00.json .. {BASE}-shard-{n_shards - 1:02d}.json")


if __name__ == "__main__":
    main()
