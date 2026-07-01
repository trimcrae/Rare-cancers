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


def _bucket():
    import boto3
    return f"sagemaker-{os.environ.get('AWS_DEFAULT_REGION','us-east-2')}-" \
           f"{boto3.client('sts').get_caller_identity()['Account']}"


def _inflight_jobs():
    """Names of in-flight <TAG> spot training jobs (empty if none)."""
    import boto3
    sm = boto3.client("sagemaker")
    names = []
    for page in sm.get_paginator("list_training_jobs").paginate(NameContains=TAG, StatusEquals="InProgress"):
        names += [j["TrainingJobName"] for j in page.get("TrainingJobSummaries", [])]
    return names


def _already_stopped():
    import boto3
    try:
        boto3.client("s3").head_object(Bucket=_bucket(), Key=f"{TAG}/STOP.json")
        return True
    except Exception:  # noqa: BLE001
        return False


def _run_once():
    """One robust monitor tick. Safe to call repeatedly (cron): no-ops when there's no active fleet, is
    idempotent once a STOP has been issued, and NEVER stops on incomplete/erroring data."""
    import report_fep as rf
    local = bool(os.environ.get("FEP_LOCAL_DIR"))       # local dry-run: skip AWS-dependent guards
    # (1) if we already decided to stop, just mop up any stragglers (idempotent) and leave.
    if not local and _already_stopped():
        strag = _inflight_jobs()
        if strag and not DRYRUN:
            _stop_fleet("re-affirm prior STOP (idempotent straggler cleanup)", {"action": "stop_idempotent"})
        print(f"[fep-monitor] STOP already issued; {len(strag)} straggler(s) handled — no-op.", flush=True)
        return 0
    # (2) the monitor only STOPS a *running* fleet; if nothing is in-flight there's nothing to reclaim (final
    #     analysis is report_fep's job). This self-limits a standing cron to cheap no-ops when idle.
    inflight = ["local"] if local else _inflight_jobs()
    if not inflight:
        print("[fep-monitor] no in-flight FEP jobs — nothing to monitor (no-op).", flush=True)
        return 0
    results = rf.load_results()
    d = decide(results)
    print(f"[fep-monitor] decision: {d['action']} — {d['reason']} (in-flight jobs: {len(inflight)})", flush=True)
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
        return 0 if d["action"] == "stop_success" else 2
    return 0


def main():
    """Self-healing wrapper for the scheduled cron: ANY unexpected error in a tick is logged and swallowed
    (exit 0) so a transient failure never (a) hard-fails the schedule or (b) stops the fleet blind — the NEXT
    scheduled tick simply retries. The only decisive actions (StopTrainingJob) live behind the conservative,
    diagnostic-gated decision in _run_once and are idempotent."""
    # cheap fast-path for the cron: is a fleet in-flight? (boto3 only — lets an idle tick skip the MBAR install)
    if "--check-active" in sys.argv:
        try:
            n = len(_inflight_jobs())
        except Exception as e:  # noqa: BLE001 — if we can't tell, assume active so we don't skip monitoring
            print(f"[fep-monitor] check-active error ({e}) — assuming active.", flush=True)
            return 0
        print(f"[fep-monitor] in-flight FEP jobs: {n}", flush=True)
        return 0 if n > 0 else 3          # 0 = active (run full monitor); 3 = idle (skip)
    if not os.environ.get("AWS_ACCESS_KEY_ID") and not os.environ.get("FEP_LOCAL_DIR"):
        print("[fep-monitor] no AWS creds — skipping tick.", flush=True)
        return 0
    try:
        return _run_once()
    except Exception as e:  # noqa: BLE001 — a failed poll must self-heal, not crash the schedule
        import traceback
        print(f"[fep-monitor] tick error (self-healing; next scheduled tick retries): {e}", flush=True)
        traceback.print_exc()
        return 0


if __name__ == "__main__":
    sys.exit(main())
