"""Measure the same cold-cache ablations against a Git revision or the working tree.

Run with the project's Python and scientific dependencies on PYTHONPATH. This driver
does not write the tracked ablation cache or change manuscript bytes. JSON retains
each result and subprocess timing so parity is checked on evidence, not test count.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "research/manuscripts/claim_ablation.py"
sys.path.insert(0, str(SOURCE.parent))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", default="working-tree")
    parser.add_argument("--per-paper", type=int, default=3)
    parser.add_argument("--paper", help="Limit to one floored document path")
    parser.add_argument("--offset", type=float, default=0.5,
                        help="Position within each evenly spaced bin; 0 selects its first row")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = (SOURCE.read_text(encoding="utf-8") if args.revision == "working-tree" else
              subprocess.check_output(["git", "show", f"{args.revision}:research/manuscripts/claim_ablation.py"],
                                      cwd=ROOT).decode("utf-8"))
    module = types.ModuleType("ablation_benchmark_subject")
    module.__file__ = str(SOURCE)
    exec(compile(source, str(SOURCE), "exec"), module.__dict__)
    module._cache.load = lambda: {}  # Every verdict is computed in both runs.
    os.environ.pop(module._cache.WRITE_ENV, None)
    cc = module.cc
    checksums = {p: hashlib.sha256(Path(cc.PAPERS[p]).read_bytes()).hexdigest()
                 for p in cc.COVERAGE_FLOOR}
    calls, rows = [], []
    real_run = module._run

    def timed_run(command, workspace):
        start = time.perf_counter()
        red = real_run(command, workspace)
        calls.append({"command": [s.replace(workspace, "<clone>") for s in command],
                      "seconds": round(time.perf_counter() - start, 6), "red": red})
        with args.output.with_suffix(".calls.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(calls[-1]) + "\n")
        return red

    module._run = timed_run
    start = time.perf_counter()
    for paper in cc.COVERAGE_FLOOR:
        if args.paper and args.paper != paper:
            continue
        covered = [r for r in cc.census(paper) if r["covered"]
                   and module.states_a_quantity(r["sentence"])
                   and not cc.ablation_exempt(paper, r["sentence"])]
        selected = [covered[int((i + args.offset) * len(covered) / min(len(covered), args.per_paper))]
                    for i in range(min(len(covered), args.per_paper))]
        for row in selected:
            before_calls, row_start = len(calls), time.perf_counter()
            result = module.ablate(paper, row)
            record = {"paper": paper, "sentence": row["sentence"], "result": result,
                      "seconds": round(time.perf_counter() - row_start, 6),
                      "subprocesses": calls[before_calls:]}
            rows.append(record)
            print(json.dumps({"paper": paper, "seconds": record["seconds"],
                              "status": result["status"], "red": bool(result["red"]),
                              "baseline": result.get("baseline")}), flush=True)
    elapsed = time.perf_counter() - start
    unchanged = all(hashlib.sha256(Path(cc.PAPERS[p]).read_bytes()).hexdigest() == digest
                    for p, digest in checksums.items())
    report = {"schema": "emc-ablation-performance/1", "revision": args.revision,
              "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
              "python": sys.version, "platform": platform.platform(),
              "command": sys.argv, "cache": "forced cold; writes disabled",
              "elapsed_seconds": round(elapsed, 6), "subprocess_count": len(calls),
              "manuscript_sha256": checksums, "manuscripts_unchanged": unchanged,
              "rows": rows}
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"elapsed_seconds": report["elapsed_seconds"],
                      "subprocess_count": len(calls), "output": str(args.output)}), flush=True)
    return 0 if unchanged and all(r["result"]["status"] == "applied" for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
