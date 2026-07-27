#!/usr/bin/env python3
"""Dump the FULL Vast instance record for this lane's units — the exit reason, and the host's RAM.

WHY A FULL DUMP RATHER THAN THE FIELDS collect ALREADY PRINTS. `collect` shows `actual_status` and
`status_msg`, and on 2026-07-27 those said `success, running ...ternary-fep_latest/ssh` for a container that
had died — the status line describes the RENTAL, not the process. The evidence that distinguishes an OOM kill
from a preemption or a driver fault is elsewhere in the record, and since we do not know which field carries
it, the honest move is to print all of them once rather than guess a field name.

THE DISCRIMINATING NUMBERS, called out explicitly at the end:
  * host RAM vs the solvated system this leg builds (288,352 atoms for NR4A1). An OOM kill is a MISMATCH,
    and the fix for a mismatch is a bigger host — NOT a shorter commit interval, which would merely convert
    an unrecoverable loop into a leg that dies and restarts every ~15 min while paying container-start
    overhead on a board where images take 20+ minutes to pull.
  * anything naming an exit code, OOM, or a kill.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gpu_backend import _vast_request  # noqa: E402

# Fields worth surfacing even when the dump is long. Host memory is `cpu_ram` (MB, whole host) and the share
# this rental gets scales with the vCPU fraction — both matter for an OOM verdict.
_HIGHLIGHT = ("id", "label", "actual_status", "cur_state", "intended_status", "status_msg", "gpu_name",
              "num_gpus", "cpu_ram", "cpu_cores", "cpu_cores_effective", "mem_limit", "mem_usage",
              "gpu_util", "cpu_util", "disk_util", "disk_space", "duration", "start_date", "end_date",
              "machine_id", "dph_total", "host_id", "inet_down", "inet_up")


def main():
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("[vast-diag] VAST_API_KEY not set")
    sel = (os.environ.get("VAST_DIAG_SELECT") or "5aks").lower()
    rows = [i for i in _vast_request("GET", "/instances/", key).get("instances", [])
            if sel in str(i.get("label") or "").lower()]
    print(f"[vast-diag] {len(rows)} instance(s) whose label contains {sel!r}", flush=True)
    for i in rows:
        print("=" * 100, flush=True)
        print(json.dumps({k: i.get(k) for k in _HIGHLIGHT}, indent=1), flush=True)
        print("--- full record ---", flush=True)
        print(json.dumps(i, indent=1, default=str)[:6000], flush=True)
        ram_gb = (i.get("cpu_ram") or 0) / 1024.0
        print(f"\n>>> HOST RAM {ram_gb:.1f} GB | mem_limit={i.get('mem_limit')} "
              f"mem_usage={i.get('mem_usage')} | this leg solvates to ~288,352 atoms", flush=True)
        blob = json.dumps(i, default=str).lower()
        for needle in ("oom", "killed", "exit", "error", "memory"):
            if needle in blob:
                print(f">>> record mentions {needle!r} — inspect the full dump above", flush=True)
    if not rows:
        print("[vast-diag] none listed — a destroyed instance leaves no record here; "
              "use the archived attempts/ logs instead", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
