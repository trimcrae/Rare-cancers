"""Read-only reconciliation of preserved science and the completed-cycle dispatch guard.

Writes only the requested report. No ownership, schedule, model, or network calls.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

BASE = "66c41277ec18cdbe1eb44450fd150292e21760d8"
RUN = "20260905T032612Z-df96afc413"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "scripts"))
    import research_cycle as cycle

    started = time.monotonic()
    bundle = root / cycle.HISTORY / RUN
    previous = cycle.read(bundle / "cycle.json")
    prefixes = ["research/release-candidates/PUB-ASO/2026-09-04/",
                "research/autonomy/qeios-v3-submission-2026-09-05.json",
                f"{cycle.HISTORY}/{RUN}/", *previous["artifact_sha256"]]
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASE, "--", *prefixes],
                                    cwd=root, text=True).splitlines()
    preserved = {}
    for name in paths:
        committed = subprocess.check_output(["git", "show", f"{BASE}:{name}"], cwd=root)
        expected = hashlib.sha256(committed).hexdigest()
        preserved[name] = {"sha256": cycle.digest(root / name), "matches_base": cycle.digest(root / name) == expected}
    mismatches = [name for name, record in preserved.items() if not record["matches_base"]]
    artifact_mismatches = [name for name, expected in previous["artifact_sha256"].items()
                           if cycle.digest(root / name) != expected]
    check_mismatches = []
    verification = cycle.read(bundle / "verification.json")
    for index, check in enumerate(verification["checks"], 1):
        if cycle.digest(bundle / f"check-{index}.log") != check["log_sha256"]:
            check_mismatches.append(index)

    contracts = cycle.read(root / cycle.CONTRACTS)["tasks"]
    plan_started = time.monotonic()
    plan = cycle.plan(root, contracts, cycle.history(root),
                      cycle.read(root / "research/autonomy/research-ledger.json"))
    planning_seconds = round(time.monotonic() - plan_started, 6)
    original = cycle.read(bundle / "plan.json")["contract"]
    guard_started = time.monotonic()
    try:
        cycle.require_current_plan(root, original, cycle.prompt(original))
        dispatch = {"refused": False}
    except cycle.runner.Refused as exc:
        dispatch = {"refused": True, "reason": str(exc)}
    dispatch["elapsed_seconds"] = round(time.monotonic() - guard_started, 6)
    result = {"schema": "emc-process-follow-through-replay/1", "base_revision": BASE,
              "checked_revision": cycle.runner.git(root, "rev-parse", "HEAD"),
              "preserved_files": preserved, "preserved_file_count": len(preserved),
              "base_mismatches": mismatches, "cycle_artifact_mismatches": artifact_mismatches,
              "cycle_check_log_mismatches": check_mismatches,
              "plan": plan, "planning_seconds": planning_seconds,
              "copied_completed_contract_guard": dispatch,
              "actual_scheduled_run": RUN, "new_model_dispatches": 0,
              "elapsed_seconds": round(time.monotonic() - started, 3),
              "scope": "Read-only current-state replay; preserved earlier unattended science, not a new scheduled run"}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in ("preserved_file_count", "base_mismatches",
        "cycle_artifact_mismatches", "cycle_check_log_mismatches", "planning_seconds",
        "copied_completed_contract_guard", "new_model_dispatches", "elapsed_seconds")}))
    return int(bool(mismatches or artifact_mismatches or check_mismatches) or not dispatch["refused"])


if __name__ == "__main__":
    raise SystemExit(main())
