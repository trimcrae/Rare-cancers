#!/usr/bin/env python3
"""Early-stop monitor for the parallel FEP — reads the pilot/partial returns and, if the run looks like it'll
fail, reclaims the whole spot fleet.

One poll = one decision:
  1. Load partial per-unit results (report_fep.load_results) and estimate provisional per-receptor ΔG_bind.
  2. If all three receptors have ≥ FEP_MIN_WINDOWS windows, apply:
       - fep_decision.early_stop  → stop_fail (provisional ΔΔG confidently not selective) / stop_success
       - fep_decision.convergence_flag(overlaps) → stop_unconverged (schedule too coarse to converge)
  3. On any stop verdict: write s3://<bucket>/<TAG>/STOP.json (record) and call StopTrainingJob on every
     InProgress job whose name contains <TAG> — the completed windows are already durable in the checkpoint
     prefix, so we lose only in-flight windows.

Meant to be polled (workflow mode=monitor, or a babysit loop). Env: FEP_TAG, FEP_TARGET_DDG (default -1.0),
FEP_Z (1.0), FEP_MIN_WINDOWS (6), FEP_SUCCESS_STOP (0), FEP_MONITOR_DRYRUN (1 = decide+print, no AWS actions).
"""
import json
import os
import sys

TAG = os.environ.get("FEP_TAG", "nr4a3-fep")
TARGET = float(os.environ.get("FEP_TARGET_DDG", "-1.0"))
Z = float(os.environ.get("FEP_Z", "1.0"))
MIN_WINDOWS = int(os.environ.get("FEP_MIN_WINDOWS", "6"))
SUCCESS_STOP = os.environ.get("FEP_SUCCESS_STOP", "0") == "1"
DRYRUN = os.environ.get("FEP_MONITOR_DRYRUN", "0") == "1"


def _collect_per_residue(results):
    """Per-receptor per-residue ligand-interaction map from the window-0 complex-leg results (the coupled
    endpoint carries the 'per_residue' decomposition — the WHY map)."""
    per = {}
    for r in results:
        if r.get("leg") == "complex" and r.get("window") == 0 and r.get("per_residue"):
            per[r["receptor"]] = {int(k): v for k, v in r["per_residue"].items()}
    return per


def decide(results):
    """One decision from partial results. CRUCIALLY: a selectivity fail (stop_fail) is GATED on the per-residue
    WHY-map being captured — we never reclaim the fleet on a fail without first knowing *why* it failed (so the
    next candidate can be designed from it). Returns {action, reason, ddg?, binding?, convergence?, why?, hint?}."""
    import fep_decision as fd
    import fep_decompose as fdc
    import report_fep as rf
    est = rf.estimate(results)
    needed = {"nr4a3", "nr4a1", "nr4a2"}
    have = {r for r, e in est.items() if e["n_windows"] >= MIN_WINDOWS}
    if not needed.issubset(have):
        return {"action": "continue", "reason": f"insufficient data (have ≥{MIN_WINDOWS} windows for "
                f"{sorted(have)}; need {sorted(needed)})", "binding": est}
    binding_se = {r: {"dg": est[r]["dg"], "se": est[r]["se"]} for r in needed}
    conv = fd.convergence_flag([o for r in needed for o in est[r]["overlaps"]])
    per_res = _collect_per_residue(results)
    diag_ready = fdc.diagnostic_ready(per_res)

    if not conv["ok"]:
        # convergence fail: the "why" is the overlap map itself; attach the per-residue attribution too if ready
        d = {"action": "stop_unconverged", "reason": conv["reason"], "binding": binding_se, "convergence": conv}
        if diag_ready:
            d["why"] = fdc.selectivity_attribution(per_res); d["hint"] = fdc.redesign_hint(d["why"])
        return d

    d = fd.early_stop(binding_se, "nr4a3", target_ddg=TARGET, z=Z, allow_success_stop=SUCCESS_STOP)
    d["binding"] = binding_se
    d["convergence"] = conv
    if d["action"] == "stop_fail":
        # ── the coupling the user required: do NOT stop a fail until we know WHY ──
        if not diag_ready:
            return {"action": "continue", "pending_diagnostic": True, "binding": binding_se, "convergence": conv,
                    "reason": ("FAIL signal present, but the per-residue WHY-map is not yet captured (need the "
                               "window-0 complex-leg per_residue decomposition for all three receptors) — "
                               "continuing sampling so we do NOT stop blind; will stop once the diagnostic lands")}
        d["why"] = fdc.selectivity_attribution(per_res)
        d["hint"] = fdc.redesign_hint(d["why"])
    return d


def _stop_fleet(reason, decision):
    import boto3
    sm = boto3.client("sagemaker")
    s3 = boto3.client("s3")
    bucket = f"sagemaker-{os.environ.get('AWS_DEFAULT_REGION','us-east-2')}-" \
             f"{boto3.client('sts').get_caller_identity()['Account']}"
    s3.put_object(Bucket=bucket, Key=f"{TAG}/STOP.json",
                  Body=json.dumps({"reason": reason, "decision": decision}).encode())
    stopped = []
    paginator = sm.get_paginator("list_training_jobs")
    for page in paginator.paginate(NameContains=TAG, StatusEquals="InProgress"):
        for j in page.get("TrainingJobSummaries", []):
            name = j["TrainingJobName"]
            try:
                sm.stop_training_job(TrainingJobName=name)
                stopped.append(name)
            except Exception as e:  # noqa: BLE001
                print(f"  (could not stop {name}: {e})", flush=True)
    print(f"[fep-monitor] wrote STOP sentinel + stopped {len(stopped)} spot jobs: {stopped}", flush=True)
    return stopped


def main():
    import report_fep as rf
    results = rf.load_results()
    d = decide(results)
    print(f"[fep-monitor] decision: {d['action']} — {d['reason']}", flush=True)
    if d.get("ddg"):
        print(f"[fep-monitor] provisional ΔΔG: {d['ddg']}", flush=True)
    if d.get("pending_diagnostic"):
        print("[fep-monitor] (fail signal held: NOT stopping until the per-residue WHY-map is captured)", flush=True)
    if d.get("why"):
        print("[fep-monitor] WHY (per-residue selectivity attribution):", flush=True)
        for para, hint in (d.get("hint") or {}).items():
            print(f"    {hint}", flush=True)
    if d["action"].startswith("stop"):
        if DRYRUN:
            print("[fep-monitor] DRYRUN — would stop the fleet now (why-map captured above).", flush=True)
        else:
            _stop_fleet(d["reason"], {k: d.get(k) for k in ("action", "reason", "ddg", "binding", "why", "hint")})
        # non-zero exit only for a genuine failure verdict (so a babysit loop can branch)
        sys.exit(0 if d["action"] == "stop_success" else 2)


if __name__ == "__main__":
    main()
