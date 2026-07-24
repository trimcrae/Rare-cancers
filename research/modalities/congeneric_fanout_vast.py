#!/usr/bin/env python3
"""
STEP 1 FAN-OUT (RUNG 4) — Vast.ai launcher for the cmpd19 congeneric RBFE map, N-wide.

One Vast instance per UNIT (= one map edge at its charge-conserving microstate leg, on the primary NR4A3
frame). Each instance clones the repo, pulls the pre-staged common-mode poses from S3, runs BOTH alchemical
legs of its edge through the unchanged OpenFE engine (`nr4a3_rbfe.py`, MODE=splittest, spot-safe S3
checkpoint/resume), reduces them to ddG_bind, uploads `ddg.json`, and self-stops.

Vast rents INDEPENDENT hosts, so N units are genuinely N-wide with no shared-quota wall. `FANOUT_WIDTH`
(default 8) is therefore a self-imposed cap on concurrent spend/blast-radius, not a provider quota — `launch`
tops the fleet UP to that width and is safe to re-run, so the poller drives wave 2 and 3 by calling it again.

Modes (env flags, set by the CI workflow):
  PLAN=1      dry plan: which units, cost band, wave shape, what is deliberately excluded. No API calls.
  STAGE=1     run the RDKit pose staging (free CPU on the runner) + upload the staged tree to S3.
  PRECHECK=1  verify the staged tree is in S3 and every unit's two endpoints are present in it. No spend.
  LAUNCH=1    top the fleet up to FANOUT_WIDTH with the next not-yet-finished units.
  COLLECT=1   pull finished ddg.json's -> map result + cycle closure + ranking; reap terminal/over-age hosts.
  MONITOR=1   one-line-per-instance liveness + per-unit phase, for the tight-cadence progress checks.
  DIAG=1      root-cause a failed unit: its S3 leg log + the container stdout pulled off the Vast instance.
  STOP=1      destroy every s1f-* instance (explicit cleanup; never touches other labels).

COST DISCIPLINE. `LAUNCH` refuses to submit unless FANOUT_CONFIRM=1 is set, prints the pinned cost band for
what it is about to submit, and skips any unit whose ddg.json is already in S3 (so a re-dispatch after a
preemption resumes the fleet rather than paying for it twice).
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from congeneric_fanout import (  # noqa: E402
    PRIMARY_FRAME, PRIMARY_RECEPTOR, checkpoint_prefix, cost_estimate, cycle_closure, default_units, plan,
    rank_by_ddg, result_key, unit_env, wave_plan,
)
from gpu_backend import JobSpec, ResourceSpec, _vast_request, get_backend  # noqa: E402

REPO = "https://github.com/trimcrae/Rare-cancers"
BUCKET = os.environ.get("VAST_CKPT_BUCKET", "")
STAGE_PREFIX = os.environ.get("STAGE_PREFIX", "nr4a3-step1-fanout/stage")
RESULT_PREFIX = os.environ.get("RESULT_PREFIX", "nr4a3-step1-fanout/results")
LABEL_PREFIX = "s1f-"
WIDTH = int(os.environ.get("FANOUT_WIDTH", "8"))
N_WINDOWS = int(os.environ.get("N_WINDOWS", "12"))

# The OpenFE image (openfe>=1.12 + ambertools/am1bcc + lomap/kartograf + OpenMM CUDA + awscli), built by the
# fusion-cpu-extras `fep_bake` task. Same image the firm RBFE probe measured ~3.6 GPU-h/complex-leg on.
FEP_IMAGE = os.environ.get("FEP_IMAGE") or "docker.io/triskit23/nr4a3fep:latest"

# 4090 is the $/ns winner at every system size we've benched (pricing.md section A). The RBFE hybrid box is
# ~35k atoms, so 24 GB VRAM is ample; host RAM matters for the CPU-bound setup unit.
FANOUT_RES = ResourceSpec(gpu=os.environ.get("VAST_GPU_MODEL") or "rtx4090",
                          min_vram_gb=24, vcpus=8, ram_gb=32, disk_gb=80, interruptible=True)

# A unit is two legs (~5-6 GPU-h) plus boot/setup; the ceiling must clear a full unit plus a resume, and must
# NOT reap mid-leg (a real HREX complex leg runs ~3 h).
MAX_RUNTIME_S = int(os.environ.get("FANOUT_MAX_RUNTIME_S", str(14 * 3600)))
REAP_AGE_MIN = int(os.environ.get("FANOUT_REAP_AGE_MIN", str(15 * 60)))


# ---- the per-instance pipeline ----------------------------------------------------------------------------

_PREAMBLE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
command -v curl >/dev/null 2>&1 || { apt-get update -q||true; apt-get install -y -q --no-install-recommends curl ca-certificates||true; }
export PATH=/opt/mamba/envs/rbfe/bin:$PATH
# conda-pack relocation breaks OpenMM's compiled-in plugin dir, so OpenFE's internal getPlatformByName("CUDA")
# fails with "no registered Platform called CUDA" (root-caused on the first firm run, 2026-07-23).
export OPENMM_PLUGIN_DIR=/opt/mamba/envs/rbfe/lib/plugins
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
PY=/opt/mamba/envs/rbfe/bin/python
AWS=/opt/mamba/envs/rbfe/bin/aws
command -v "$AWS" >/dev/null 2>&1 || AWS="$PY -m awscli"
mark() { echo "$1 $(date -u +%FT%TZ)" | $AWS s3 cp - "$RESULT_S3/phase.txt" 2>/dev/null || true; }
mark boot
$PY -c "import openfe,openmm;print('[s1f] openfe',openfe.__version__,'plats',[openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())])"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || true
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz
cd Rare-cancers-*/research/modalities
export IN=/tmp/s1f_in OUT=/tmp/s1f_out
mkdir -p "$IN" "$OUT"
# Common-mode poses + receptor, staged once on CI (congeneric_pose_stage.py) — every unit reads the SAME tree,
# which is what makes the 19 ddG values mutually comparable.
$AWS s3 cp "s3://$BUCKET/$STAGE_PREFIX/" "$IN/" --recursive --only-show-errors
test -s "$IN/ligand/docked_$RECEPTOR.sdf" || { echo "[s1f] FATAL: staged ligand SDF missing"; exit 3; }
test -s "$IN/receptor/$RECEPTOR-opened.pdb" || { echo "[s1f] FATAL: staged receptor PDB missing"; exit 3; }
mark staged
"""

# One alchemical leg. Idempotent across dispatches: a leg whose JSON is already in S3 is downloaded, not rerun
# (so a preempted unit resumes at leg granularity), and the sampler itself resumes from its S3 commit store.
_LEG = r"""
run_leg() {
  L="$1"
  if $AWS s3 cp "$RESULT_S3/leg_${RECEPTOR}_${L}.json" "$OUT/leg_${RECEPTOR}_${L}.json" --only-show-errors 2>/dev/null; then
    echo "[s1f] leg $L already in S3 — idempotent skip"; return 0
  fi
  mark "leg-$L-running"
  # `set -e` + `pipefail` is DISARMED around the engine on purpose. Previously the leg ran as
  # `... | tee log`, so a non-zero exit aborted the function immediately and the `s3 cp` of the log never
  # ran — the diagnostic was discarded in exactly the case it was needed (observed on s1f-04, which exited
  # 10 min into its complex leg leaving nothing behind). Capture the rc, ALWAYS ship the log, then fail.
  set +e
  env MODE=splittest RBFE_TINY=0 OPENMM_REQUIRE_CUDA=1 \
      RBFE_SPOT_SAFE=1 RBFE_SPOT_COMMIT_S3="s3://$BUCKET/$CKPT_PREFIX/$L" \
      RBFE_WARMUP_CKPT_ITERS=20 RBFE_PROD_CKPT_ITERS=40 \
      RECEPTOR="$RECEPTOR" LEG="$L" LIGAND_A="$LIGAND_A" LIGAND_B="$LIGAND_B" N_WINDOWS="$N_WINDOWS" \
      INPUT_DIR="$IN" OUTPUT_DIR="$OUT" CKPT_DIR="$OUT" \
      $PY nr4a3_rbfe.py > "/tmp/$L.log" 2>&1
  rc=$?
  set -e
  tail -60 "/tmp/$L.log" || true
  $AWS s3 cp "/tmp/$L.log" "$RESULT_S3/$L.log" --only-show-errors || true
  if [ "$rc" -ne 0 ]; then
    echo "[s1f] leg $L FAILED rc=$rc (full log at $RESULT_S3/$L.log)"
    mark "leg-$L-FAILED-rc$rc"
    return 1
  fi
  test -s "$OUT/leg_${RECEPTOR}_${L}.json" || {
    echo "[s1f] leg $L exited 0 but produced no result JSON"; mark "leg-$L-NORESULT"; return 1; }
  $AWS s3 cp "$OUT/leg_${RECEPTOR}_${L}.json" "$RESULT_S3/leg_${RECEPTOR}_${L}.json" --only-show-errors
  mark "leg-$L-done"
}
run_leg complex
run_leg solvent
"""

# The reduce is done HERE, not via nr4a3_rbfe.py's MODE=reduce: that path annotates its output with the
# denovo_401 ABFE anchor (rbfe_edges.ANCHOR_401_ABFE), which is a DIFFERENT scaffold and meaningless for a
# cmpd19 congeneric edge. Writing ddG_bind ourselves keeps the provenance honest — the thermodynamic cycle is
# still rbfe_edges.ddg_bind (dG_complex - dG_solvent), just without a borrowed absolute anchor.
_REDUCE = r"""
mark reduce
$PY - <<'PYEOF'
import json, os
import rbfe_edges as rb
out, rec = os.environ["OUT"], os.environ["RECEPTOR"]
cx = json.load(open(f"{out}/leg_{rec}_complex.json"))
sol = json.load(open(f"{out}/leg_{rec}_solvent.json"))
ddg = rb.ddg_bind(cx["dg_morph_kcal"], sol["dg_morph_kcal"])
unc = (cx.get("unc_kcal", 0.0) ** 2 + sol.get("unc_kcal", 0.0) ** 2) ** 0.5
r = {
    "unit_id": os.environ["UNIT_ID"], "edge_id": os.environ["EDGE_ID"], "leg_id": os.environ["LEG_ID"],
    "receptor": rec, "frame": os.environ["FRAME"],
    "ligand_a": cx["ligand_a"], "ligand_b": cx["ligand_b"],
    "ddg_bind_kcal": round(ddg, 3), "ddg_bind_unc_kcal": round(unc, 3),
    "dg_complex_morph_kcal": cx["dg_morph_kcal"], "complex_unc_kcal": cx.get("unc_kcal"),
    "dg_solvent_morph_kcal": sol["dg_morph_kcal"], "solvent_unc_kcal": sol.get("unc_kcal"),
    "n_mapped_atoms": cx.get("n_mapped_atoms"), "n_windows": int(os.environ["N_WINDOWS"]),
    "engine": "OpenFE RelativeHybridTopologyProtocol, HREX + MBAR (nr4a3_rbfe.py, MODE=splittest)",
    "uncertainty_note": "within-run MBAR standard errors, propagated in quadrature. NOT a replicate SD — a "
                        "single replicate per edge cannot report reproducibility.",
    "claim_ceiling": "CONDITIONAL relative binding free energy for a HYPOTHESIZED cmpd19 pose in ONE modeled "
                     "opened NR4A3 conformer. Not an affinity, not a selectivity claim.",
}
json.dump(r, open(f"{out}/ddg.json", "w"), indent=2)
print("S1F_RESULT", json.dumps(r))
PYEOF
$AWS s3 cp "$OUT/ddg.json" "$RESULT_S3/ddg.json" --only-show-errors
mark done
"""


def build_jobspec(unit, branch, bucket, idx):
    """JobSpec for ONE fan-out unit (both alchemical legs + reduce on a single rented 4090)."""
    label = f"{LABEL_PREFIX}{idx:02d}-{unit['ligand_b']}"[:64]
    result_s3 = f"s3://{bucket}/{RESULT_PREFIX}/{unit['unit_id']}"
    ckpt = checkpoint_prefix(unit, RESULT_PREFIX)
    pipeline = (_PREAMBLE + _LEG + _REDUCE).replace("{repo}", REPO)
    env = {
        "GIT_BRANCH": branch, "BUCKET": bucket, "STAGE_PREFIX": STAGE_PREFIX,
        "RESULT_S3": result_s3, "CKPT_PREFIX": ckpt,
        "UNIT_ID": unit["unit_id"], "EDGE_ID": unit["edge_id"], "LEG_ID": unit["leg_id"],
        "FRAME": unit["frame"], "N_WINDOWS": str(N_WINDOWS),
        **{k: v for k, v in unit_env(unit, "complex", N_WINDOWS).items()
           if k in ("RECEPTOR", "LIGAND_A", "LIGAND_B")},
    }
    return JobSpec(name=label, command=["bash", "-lc", pipeline], image=FEP_IMAGE,
                   checkpoint_uri=f"s3://{bucket}/{ckpt}", resume=True, resources=FANOUT_RES,
                   max_runtime_s=MAX_RUNTIME_S, env=env)


# ---- S3 helpers -------------------------------------------------------------------------------------------

def _s3():
    import boto3
    return boto3.client("s3")


def _exists(s3, bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except Exception:  # noqa: BLE001
        return False


def _get_json(s3, bucket, key):
    try:
        return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
    except Exception:  # noqa: BLE001
        return None


def _get_text(s3, bucket, key):
    try:
        return s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8", "replace").strip()
    except Exception:  # noqa: BLE001
        return None


def _live_instances(key):
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    return [i for i in insts if (i.get("label") or "").startswith(LABEL_PREFIX)]


def _age_min(inst):
    """Minutes since WE rented this instance.

    Uses `start_date` (epoch seconds, the rental start), NOT `duration` — on a Vast instance object `duration`
    is the HOST MACHINE's uptime, which reads in the hundreds of thousands of minutes for a long-lived
    community host. The collect reaper is age-based, so reading `duration` as our age would have destroyed
    every instance in the fleet on the first collect. Caught on the first live monitor (age_min 209141 = 145
    days on a box we had just rented)."""
    import time
    start = inst.get("start_date")
    if not start:
        return 0
    try:
        return max(0, round((time.time() - float(start)) / 60))
    except (TypeError, ValueError):
        return 0


def _require_bucket():
    if not BUCKET:
        raise SystemExit("[s1f] VAST_CKPT_BUCKET is required")
    return BUCKET


# ---- modes ------------------------------------------------------------------------------------------------

def mode_plan():
    p = plan(width=WIDTH)
    print(json.dumps(p, indent=2))
    print(f"\n[s1f] {p['n_units']} units, {WIDTH}-wide -> {p['waves']['waves']} waves "
          f"(~{p['waves']['wall_clock_h_est']} h wall-clock), ${p['cost_usd_est'][0]}-{p['cost_usd_est'][1]}")


def mode_stage():
    """Free CPU: build the common-mode poses on the runner and upload them. Fails loudly on QC."""
    os.environ.setdefault("S3_BUCKET", _require_bucket())
    os.environ.setdefault("OUT_PREFIX", STAGE_PREFIX)
    import congeneric_pose_stage
    congeneric_pose_stage.main()


def mode_precheck():
    """No-spend gate: the staged tree exists in S3 and covers every endpoint of every unit."""
    bucket, s3 = _require_bucket(), _s3()
    qc = _get_json(s3, bucket, f"{STAGE_PREFIX}/stage_qc.json")
    if qc is None:
        raise SystemExit(f"[s1f] no stage_qc.json under s3://{bucket}/{STAGE_PREFIX}/ — run STAGE=1 first")
    units = default_units()
    staged = {q["node"] for q in qc.get("qc", []) if q.get("status") == "ok"}
    needed = {u["ligand_a"] for u in units} | {u["ligand_b"] for u in units}
    missing = sorted(needed - staged)
    reval = [q["node"] for q in qc.get("qc", []) if q.get("needs_pose_revalidation")]
    for key in (f"{STAGE_PREFIX}/ligand/docked_{PRIMARY_RECEPTOR}.sdf",
                f"{STAGE_PREFIX}/receptor/{PRIMARY_RECEPTOR}-opened.pdb"):
        if not _exists(s3, bucket, key):
            raise SystemExit(f"[s1f] staged input missing: s3://{bucket}/{key}")
    print(f"[s1f] staged nodes OK: {len(staged)}/{len(needed)}  (method: {qc.get('_method', '?')[:80]}...)")
    print(f"[s1f] {'node':28s} {'status':10s} core rmsd    strain  soft severe  closest")
    for q in sorted(qc.get("qc", []), key=lambda x: x["node"]):
        print(f"[s1f] {q['node']:28s} {q['status']:10s} {str(q.get('core_atoms')):4s} "
              f"{str(q.get('core_rmsd_A')):8s} {str(q.get('core_geometry_strain_A')):7s} "
              f"{str(q.get('soft_contacts_lt_2.0A')):4s} {str(q.get('severe_clashes_lt_1.6A')):6s} "
              f"{q.get('closest_receptor_contact_A')}")
    strained = [q["node"] for q in qc.get("qc", []) if q.get("high_core_strain")]
    print(f"[s1f] high core strain (caveat on the edge, not blocking): {strained or 'none'}")
    print(f"[s1f] severe clash -> needs_pose_revalidation (caveat, not blocking): {reval or 'none'}")
    if missing:
        raise SystemExit(f"[s1f] PRECHECK FAIL — units reference unstaged nodes: {missing}")
    print("[s1f] PRECHECK OK — every unit's endpoints are staged from the common anchor pose")


def _pending(s3, bucket, units):
    """Units with no ddg.json in S3 yet, in map order."""
    return [u for u in units if not _exists(s3, bucket, result_key(u, RESULT_PREFIX))]


def mode_launch():
    bucket, s3 = _require_bucket(), _s3()
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("[s1f] VAST_API_KEY required to launch")
    units = default_units()
    idx_of = {u["unit_id"]: i for i, u in enumerate(units)}
    pending = _pending(s3, bucket, units)
    done = len(units) - len(pending)

    live = _live_instances(key)
    live_labels = {i.get("label") for i in live}
    # a unit whose instance is already up is not re-submitted (idempotent top-up)
    todo = [u for u in pending if f"{LABEL_PREFIX}{idx_of[u['unit_id']]:02d}-{u['ligand_b']}"[:64]
            not in live_labels]
    slots = max(0, WIDTH - len(live))
    batch = todo[:slots]

    lo, hi = cost_estimate(len(pending))
    print(f"[s1f] units={len(units)} done={done} pending={len(pending)} live={len(live)} "
          f"free_slots={slots} -> submitting {len(batch)}")
    print(f"[s1f] remaining fan-out cost band (all {len(pending)} pending units): ${lo}-{hi} "
          f"| {json.dumps(wave_plan(len(pending), WIDTH))}")
    for u in batch:
        print(f"[s1f]   queue {u['unit_id']}  ({u['ligand_a']} -> {u['ligand_b']}, {u['edge_class']})")
    if not batch:
        print("[s1f] nothing to submit (fleet already at width, or all units done)")
        return
    if os.environ.get("FANOUT_CONFIRM") != "1":
        print("[s1f] DRY — set FANOUT_CONFIRM=1 to actually rent instances")
        return

    backend, handles = get_backend("vast"), []
    for u in batch:
        spec = build_jobspec(u, os.environ.get("GIT_BRANCH", "main"), bucket, idx_of[u["unit_id"]])
        try:
            h = backend.submit(spec)
        except Exception as e:  # noqa: BLE001 — one host shortage must not abort the wave
            print(f"[s1f] SUBMIT FAILED {u['unit_id']}: {e}", flush=True)
            continue
        print(f"[s1f] submitted {spec.name} -> instance {h.job_id} dph≈${h.extra.get('dph')}/hr", flush=True)
        handles.append({"unit_id": u["unit_id"], "label": spec.name, "instance": h.job_id,
                        "dph": h.extra.get("dph")})
    with open("step1-fanout-handles.json", "w") as f:
        json.dump(handles, f, indent=2)
    # the label -> unit map, so a later collect/monitor can name instances without re-deriving the index
    try:
        _s3().put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_manifest.json",
                         Body=json.dumps({f"{LABEL_PREFIX}{i:02d}-{u['ligand_b']}"[:64]: u["unit_id"]
                                          for i, u in enumerate(units)}, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] manifest upload skipped: {e}")


def mode_monitor():
    """Tight-cadence PROGRESS check (not a liveness ping): per-unit phase + per-instance state, one line each."""
    bucket, s3 = _require_bucket(), _s3()
    units = default_units()
    key = os.environ.get("VAST_API_KEY")
    live = _live_instances(key) if key else []
    print(f"[s1f] live s1f-* instances: {len(live)}")
    for i in live:
        print(f"[s1f]   id={i.get('id')} label={i.get('label')} actual={i.get('actual_status')} "
              f"cur={i.get('cur_state')} dph=${i.get('dph_total')} gpu={i.get('gpu_name')} "
              f"util={i.get('gpu_util')}% age_min={_age_min(i)} msg={(i.get('status_msg') or '')[:120]!r}")
    n_done = 0
    for u in units:
        ddg = _get_json(s3, bucket, result_key(u, RESULT_PREFIX))
        if ddg:
            n_done += 1
            print(f"[s1f]   {u['unit_id']:56s} DONE ddG={ddg.get('ddg_bind_kcal')} "
                  f"± {ddg.get('ddg_bind_unc_kcal')}")
            continue
        phase = _get_text(s3, bucket, f"{RESULT_PREFIX}/{u['unit_id']}/phase.txt")
        legs = [L for L in ("complex", "solvent")
                if _exists(s3, bucket, f"{RESULT_PREFIX}/{u['unit_id']}/leg_{u['receptor']}_{L}.json")]
        print(f"[s1f]   {u['unit_id']:56s} {phase or 'not-started':28s} legs_done={legs}")
    # SELF-HEAL the create/start race before summarising. Creating a Vast ask does not reliably launch the
    # container: the start PUT can be lost while Vast is still finishing the create, leaving the box at
    # cur_state="stopped" forever, burning nothing but never running either (gpu_backend._ensure_running
    # documents the same race and retries only ~48 s at submit time, which is not always long enough).
    # Signature, seen on s1f-01: cur_state "stopped" AND an EMPTY status_msg — as opposed to the three
    # instances that were also "loading" but whose status_msg showed an image pull in progress.
    # Re-issuing the start is idempotent, so this runs on every progress check. A unit whose ddg.json is
    # already in S3 is never restarted — that box is finished, not stalled.
    if key:
        idx = {u["unit_id"]: i for i, u in enumerate(units)}
        label_to_unit = {f"{LABEL_PREFIX}{idx[u['unit_id']]:02d}-{u['ligand_b']}"[:64]: u for u in units}
        for i in live:
            u = label_to_unit.get(i.get("label") or "")
            if not u or i.get("cur_state") != "stopped":
                continue
            if _exists(s3, bucket, result_key(u, RESULT_PREFIX)):
                continue                       # finished, not stalled
            try:
                _vast_request("PUT", f"/instances/{i.get('id')}/", key, body={"state": "running"})
                print(f"[s1f] NUDGED {i.get('id')} ({i.get('label')}) — cur_state=stopped, no result yet; "
                      f"re-issued start (msg={(i.get('status_msg') or '')[:60]!r})")
            except Exception as e:  # noqa: BLE001
                print(f"[s1f] nudge {i.get('id')} failed: {e}")

    # Summary LAST: a CI log is read from its tail, and the per-instance detail above scrolls out of view.
    # This block is the tight-cadence progress check — instance states, GPU utilisation and the phase
    # histogram in one place, so "is it ADVANCING?" is answerable without paging back through the log.
    states, utils = {}, []
    for i in live:
        states[i.get("actual_status") or "?"] = states.get(i.get("actual_status") or "?", 0) + 1
        if i.get("gpu_util") is not None:
            utils.append(i.get("gpu_util"))
    phases = {}
    for u in units:
        p = "done" if _exists(s3, bucket, result_key(u, RESULT_PREFIX)) else \
            (_get_text(s3, bucket, f"{RESULT_PREFIX}/{u['unit_id']}/phase.txt") or "not-started").split()[0]
        phases[p] = phases.get(p, 0) + 1
    print("[s1f] ---------------- SUMMARY ----------------")
    print(f"[s1f] units {n_done}/{len(units)} complete | live instances {len(live)} {states or '{}'}")
    print(f"[s1f] phases {phases}")
    print(f"[s1f] gpu_util across live instances: {utils or 'n/a'}"
          + ("  <-- all idle; if unchanged next check, that is a STALL, not slowness"
             if utils and not any(utils) else ""))

    # Written to disk (and committed back to the branch by CI) because a GitHub job log is only readable from
    # its tail, and the tail is always the runner's own post-job boilerplate. A committed progress file is the
    # readout that survives, and it doubles as a timestamped trail of how the fleet advanced.
    snapshot = {
        "n_units": len(units), "n_complete": n_done,
        "live_instances": len(live), "instance_states": states,
        "gpu_util": utils, "phases": phases,
        # status_msg is what distinguishes a host still PULLING the ~6 GiB image (documented ~20-40 min on
        # cheap 4090 hosts, and normal) from a container that is genuinely wedged — both show actual_status
        # "loading". Without it, "loading for 29 minutes" is unreadable either way.
        "instances": [{"id": i.get("id"), "label": i.get("label"), "status": i.get("actual_status"),
                       "cur_state": i.get("cur_state"), "status_msg": (i.get("status_msg") or "")[:200],
                       "gpu": i.get("gpu_name"), "gpu_util": i.get("gpu_util"),
                       "inet_down": i.get("inet_down"),
                       "dph": i.get("dph_total"), "age_min": _age_min(i)}
                      for i in live],
        "units": [{"unit_id": u["unit_id"],
                   "phase": ("done" if _exists(s3, bucket, result_key(u, RESULT_PREFIX))
                             else _get_text(s3, bucket, f"{RESULT_PREFIX}/{u['unit_id']}/phase.txt")
                             or "not-started"),
                   "ddg_bind_kcal": (_get_json(s3, bucket, result_key(u, RESULT_PREFIX)) or {})
                   .get("ddg_bind_kcal")}
                  for u in units],
    }
    with open("step1-fanout-progress.json", "w") as f:
        json.dump(snapshot, f, indent=2)
    print("[s1f] wrote step1-fanout-progress.json")


def mode_collect():
    """Assemble the map result from finished units, run the internal-consistency checks, reap dead hosts."""
    bucket, s3 = _require_bucket(), _s3()
    units = default_units()
    results, ddg_by_edge = [], {}
    for u in units:
        r = _get_json(s3, bucket, result_key(u, RESULT_PREFIX))
        if not r:
            continue
        results.append(r)
        ddg_by_edge[u["edge_id"]] = r["ddg_bind_kcal"]

    closure = cycle_closure(ddg_by_edge)
    out = {
        "_what": "STEP 1 FAN-OUT — cmpd19 congeneric relative binding free-energy map (RUNG 4, tranche 1)",
        "_scope": "19 map edges at their charge-conserving microstate leg, on the PRIMARY nr4a3_design "
                  "druggable frame. Charge-changing microstate legs and the conformer/paralogue frame axis "
                  "are separate tranches and were NOT run — see congeneric_fanout.plan().",
        "_claim_ceiling": "CONDITIONAL relative free energies given a HYPOTHESIZED cmpd19 pose (no solved "
                          "NR4A3 cocrystal) in ONE modeled opened conformer, single replicate per edge. "
                          "NOT affinities, NOT a selectivity readout, NOT a sensitivity range. Accuracy is "
                          "not established here — it rests on valA_mini + OpenFE's published benchmark for "
                          "this protocol.",
        "n_units": len(units), "n_complete": len(results),
        "results": sorted(results, key=lambda r: r["unit_id"]),
        "cycle_closure": closure,
        "cycle_closure_note": "Internal consistency only: a closed cycle does not make the map accurate, but "
                              "an open one means at least one of its edges is unconverged or mis-mapped and "
                              "its ddG must not be quoted.",
        "ranking": rank_by_ddg(ddg_by_edge),
        "ranking_note": "anchor-rooted edges only; more negative = predicted tighter than cmpd19 in this "
                        "modeled conformer, conditional on the pose hypothesis.",
    }
    with open("step1-fanout-map.json", "w") as f:
        json.dump(out, f, indent=2)
    s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_map.json",
                  Body=json.dumps(out, indent=2).encode())
    print(json.dumps({k: v for k, v in out.items() if k != "results"}, indent=2))
    print(f"\n[s1f] {len(results)}/{len(units)} units complete -> step1-fanout-map.json")

    key = os.environ.get("VAST_API_KEY")
    if not key:
        return
    finished = {r["unit_id"] for r in results}
    idx_of = {u["unit_id"]: i for i, u in enumerate(units)}
    label_of = {f"{LABEL_PREFIX}{idx_of[u['unit_id']]:02d}-{u['ligand_b']}"[:64]: u["unit_id"] for u in units}
    for i in _live_instances(key):
        lab, st = i.get("label"), (i.get("actual_status") or "")
        age_min = _age_min(i)
        why = None
        if label_of.get(lab) in finished:
            why = "result in S3"
        elif st in ("exited", "offline", "error"):
            why = f"terminal state {st}"
        elif age_min > REAP_AGE_MIN:
            why = f"age {age_min} min > {REAP_AGE_MIN}"
        if not why:
            continue
        try:
            _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
            print(f"[s1f] reaped {i.get('id')} ({lab}): {why}")
        except Exception as e:  # noqa: BLE001
            print(f"[s1f] reap {i.get('id')} failed: {e}")


def mode_diag():
    """Root-cause a failed/exited unit: its S3 leg log if one was shipped, plus the container stdout pulled
    straight off the Vast instance (which survives even when the pipeline died before uploading anything).

    Output is ALSO written to step1-fanout-diag.txt and committed back to the branch: a job log is only
    readable from its tail, and a diagnostic dump is long enough that the part that matters never survives
    there. DIAG_UNIT selects a unit by substring (default: every LAUNCHED unit that has not finished)."""
    bucket, s3 = _require_bucket(), _s3()
    out_lines = []

    def emit(msg):
        print(msg, flush=True)
        out_lines.append(str(msg))

    key = os.environ.get("VAST_API_KEY")
    want = (os.environ.get("DIAG_UNIT") or "").strip()
    # Default scope is units that have actually BEEN launched (a phase marker in S3, or a live instance) and
    # are not finished. Without that, diag also reports every unit of the not-yet-launched later waves as
    # "gone", which buries the one unit that actually needs diagnosing.
    all_units = default_units()
    idx_all = {u["unit_id"]: i for i, u in enumerate(all_units)}

    def _launched(u):
        lbl = f"{LABEL_PREFIX}{idx_all[u['unit_id']]:02d}-{u['ligand_b']}"[:64]
        return bool(_get_text(s3, bucket, f"{RESULT_PREFIX}/{u['unit_id']}/phase.txt")) or lbl in _labels_live

    _labels_live = {(i.get("label") or "") for i in (_live_instances(key) if key else [])}
    units = [u for u in all_units
             if (want in u["unit_id"] if want
                 else (_launched(u) and not _exists(s3, bucket, result_key(u, RESULT_PREFIX))))]
    if not units:
        emit("[s1f-diag] nothing to diagnose: no launched-and-unfinished unit "
             + ("matching DIAG_UNIT=" + want if want else "(later waves are not launched yet)"))
    live = {(i.get("label") or ""): i for i in (_live_instances(key) if key else [])}
    idx_of = idx_all

    for u in units:
        uid = u["unit_id"]
        label = f"{LABEL_PREFIX}{idx_of[uid]:02d}-{u['ligand_b']}"[:64]
        phase = _get_text(s3, bucket, f"{RESULT_PREFIX}/{uid}/phase.txt")
        if not (phase and "FAIL" in phase.upper()) and want == "" and label in live \
                and live[label].get("actual_status") not in ("exited", "offline", "error"):
            continue                                  # healthy and still going — nothing to diagnose
        emit(f"\n[s1f-diag] ===== {uid} (label {label}) phase={phase} "
             f"vast_status={live.get(label, {}).get('actual_status', 'gone')} =====")
        for leg in ("complex", "solvent"):
            txt = _get_text(s3, bucket, f"{RESULT_PREFIX}/{uid}/{leg}.log")
            if txt:
                emit(f"[s1f-diag] --- S3 {leg}.log (tail) ---\n{txt[-4000:]}")
        inst = live.get(label)
        if inst and key:
            from nrv04_vast_launch import _vast_instance_logs
            emit(f"[s1f-diag] --- Vast container stdout for instance {inst.get('id')} ---")
            emit(_vast_instance_logs(key, inst.get("id")))
        elif not inst:
            emit("[s1f-diag] instance is gone from Vast — container stdout unrecoverable; the S3 leg log "
                 "above is the only record (this is why the leg now uploads its log even on failure)")

    with open("step1-fanout-diag.txt", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    print(f"[s1f-diag] wrote step1-fanout-diag.txt ({len(out_lines)} blocks)")


def mode_stop():
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("[s1f] VAST_API_KEY required to stop")
    live = _live_instances(key)
    print(f"[s1f] destroying {len(live)} s1f-* instances")
    for i in live:
        try:
            _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
            print(f"[s1f] destroyed {i.get('id')} ({i.get('label')})")
        except Exception as e:  # noqa: BLE001
            print(f"[s1f] destroy {i.get('id')} failed: {e}")


_MODES = [("PLAN", mode_plan), ("STAGE", mode_stage), ("PRECHECK", mode_precheck), ("LAUNCH", mode_launch),
          ("COLLECT", mode_collect), ("MONITOR", mode_monitor), ("DIAG", mode_diag), ("STOP", mode_stop)]


def main():
    for flag, fn in _MODES:
        if os.environ.get(flag) == "1":
            return fn()
    return mode_plan()


if __name__ == "__main__":
    main()
