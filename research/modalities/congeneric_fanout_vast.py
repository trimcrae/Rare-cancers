#!/usr/bin/env python3
"""
STEP 1 FAN-OUT (RUNG 4) — Vast.ai launcher for the cmpd19 congeneric RBFE map, N-wide.

One Vast instance per UNIT (= one map edge at its charge-conserving microstate leg, on the primary NR4A3
frame). Each instance clones the repo, pulls the pre-staged common-mode poses from S3, runs BOTH alchemical
legs of its edge through the unchanged OpenFE engine (`nr4a3_rbfe.py`, MODE=splittest, spot-safe S3
checkpoint/resume), reduces them to ddG_bind, uploads `ddg.json`, and self-stops.

Vast rents INDEPENDENT hosts, so N units are genuinely N-wide with no shared-quota wall. `FANOUT_WIDTH` is
therefore a self-imposed cap on concurrent spend/blast-radius, not a provider quota — `launch` tops the fleet
UP to that width and is safe to re-run. The CI workflow sets it to the whole 19-unit tranche, because
parallel costs the same GPU-dollars as serial and a congeneric map has no result that would cancel the rest.

Modes (env flags, set by the CI workflow):
  PLAN=1      dry plan: which units, cost band, wave shape, what is deliberately excluded. No API calls.
  STAGE=1     run the RDKit pose staging (free CPU on the runner) + upload the staged tree to S3.
  PRECHECK=1  verify the staged tree is in S3 and every unit's two endpoints are present in it. No spend.
  LAUNCH=1    top the fleet up to FANOUT_WIDTH with the next not-yet-finished units.
  COLLECT=1   pull finished ddg.json's -> map result + cycle closure + ranking + REALISED SPEND; reap hosts.
  MONITOR=1   PROGRESS check: committed-iteration census per unit, GPU utilisation, the starved-host guard.
  DIAG=1      root-cause a failed unit: its S3 leg log + the container stdout pulled off the Vast instance.
  STOP=1      destroy every s1f-* instance (explicit cleanup; never touches other labels).

SELECTIVE LAUNCH — `FANOUT_ONLY` (comma-separated unit_id / ligand substrings) launches a NAMED subset. This
is the shakeout lever, and it exists because of an asymmetry: wave 1 proved this lane SAMPLES (three hosts at
95-99 % GPU on the real cmpd19/NR4A3 system), but 0 of 19 units has ever produced a ddG, so the TERMINUS —
reduce both legs, write ddg.json, upload — is unproven. Fanning 19 wide into an unproven terminus risks
paying 19x for zero results. One deliberately-chosen unit (the most-advanced checkpoint, i.e. the one closest
to the terminus) runs first; the rest go out together the moment it lands a ddG.

WHAT THE DRIVER NOW KEEPS IN S3, so that a CI run inherits what a previous CI run learned with no agent awake:
  <results>/_rentals.json            the rental ledger — bid x billed hours = REALISED spend
  <results>/_excluded_machines.json  machines this lane refuses to re-rent (capacity refusal / starvation)
  <results>/_progress_prev.json      last check's committed-iteration census, so "did it ADVANCE" is answerable
  <results>/_util_state.json         consecutive low-utilisation strikes per instance

COST DISCIPLINE. `LAUNCH` refuses to submit unless FANOUT_CONFIRM=1 is set, prints the DERIVED cost of exactly
what it is about to submit (never a hand-typed constant — see congeneric_fanout's cost block), and skips any
unit whose ddg.json is already in S3, so a re-dispatch after a preemption resumes rather than paying twice.
"""
from __future__ import annotations

import calendar
import dataclasses
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from congeneric_fanout import (  # noqa: E402
    PRIMARY_FRAME, PRIMARY_RECEPTOR, checkpoint_prefix, cost_estimate, cost_plan, cycle_closure,
    default_units, plan, rank_by_ddg, result_key, unit_env, wave_plan,
)
# The market guard's arithmetic is PURE and lives in the core module with the rest of the cost block, so it
# is unit-tested without a Vast key and cannot drift from the ladder figures it is derived from.
from congeneric_fanout import (  # noqa: E402
    basis_usd_per_ns as market_basis, market_verdict as cost_verdict)
from gpu_backend import JobSpec, ResourceSpec, _vast_request, get_backend  # noqa: E402

REPO = "https://github.com/trimcrae/Rare-cancers"
BUCKET = os.environ.get("VAST_CKPT_BUCKET", "")
STAGE_PREFIX = os.environ.get("STAGE_PREFIX", "nr4a3-step1-fanout/stage")
RESULT_PREFIX = os.environ.get("RESULT_PREFIX", "nr4a3-step1-fanout/results")
LABEL_PREFIX = "s1f-"
# Set True by `market_hold()` once it has actually taken a snapshot and decided. The interim belt in
# `mode_launch` refuses any multi-unit launch that reaches it with this still False.
_MARKET_GUARD_RAN = False
_MARKET_HOLD_ESCALATED = False
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


def build_jobspec(unit, branch, bucket, idx, exclude_machine_ids=()):
    """JobSpec for ONE fan-out unit (both alchemical legs + reduce on a single rented 4090).

    `exclude_machine_ids` is applied to a PER-JOB COPY of FANOUT_RES, never to the module-level object: the
    fleet loop widens the exclusion set as it goes (so 18 units land on 18 distinct hosts instead of stacking
    on the single cheapest one and contending for its GPU), and mutating a shared dataclass would make every
    already-built spec change under it."""
    import dataclasses
    label = f"{LABEL_PREFIX}{idx:02d}-{unit['ligand_b']}"[:64]
    res = dataclasses.replace(FANOUT_RES, exclude_machine_ids=tuple(sorted(str(m) for m in
                                                                          exclude_machine_ids)))
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
                   checkpoint_uri=f"s3://{bucket}/{ckpt}", resume=True, resources=res,
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


# Expected sampler throughput, from the MEASURED cmpd19/NR4A3 rate: three independent wave-1 hosts at
# 12.76 / 13.70 / 14.42 s per HREX iteration (all 12 windows advanced 2.5 ps) => ~250-282 iterations/hour.
EXPECTED_ITER_PER_H = 3600.0 / 13.6


def _iter_rate(prev_entry, scalar):
    """Realised committed-iterations/hour since the previous check, or None if not computable.

    ★ THIS, NOT `gpu_util`, IS THE THROUGHPUT SIGNAL THAT ACTUALLY BINDS. `$/ns` ranking is blind to a host
    slower than its card because it multiplies a CARD CONSTANT (pricing.md A.1), and the obvious fix —
    watching `gpu_util` — turns out to depend on a field the Vast payload does not always carry (observed
    None on instance 45936074 at 20 minutes in, under BOTH spellings, while the box was demonstrably up and
    advancing). A monitor whose only health signal can silently go absent is a monitor that watches nothing.

    The committed-iteration rate has neither weakness: it comes from OUR OWN object store rather than the
    provider's telemetry, and it measures the realised throughput of THIS workload rather than a proxy for it.
    A host at half the expected rate is half as good per dollar whatever its `gpu_util` says.

    Deliberately reports rather than acts. Any single interval can be depressed by a legitimate freeze — MBAR
    analysis at the end of a leg, a phase transition, a checkpoint sync — so a rate is evidence for the
    stall/starvation judgement, not the judgement itself."""
    if not prev_entry or scalar < 0:
        return None
    was, when = prev_entry.get("scalar"), prev_entry.get("utc")
    if was is None or when is None or scalar <= was:
        return None
    try:
        import datetime
        t0 = datetime.datetime.strptime(when, "%Y-%m-%dT%H:%M:%SZ")
        hours = (datetime.datetime.utcnow() - t0).total_seconds() / 3600.0
    except (TypeError, ValueError):
        return None
    if hours <= 0:
        return None
    return round((scalar - was) / hours)


def _arm_watchdog(unit_ids, branch):
    """Add a watch entry for each unit this launch actually rented, so nothing is billed unwatched.

    WHY THIS IS DONE BY THE LAUNCHER AND NOT BY HAND. The fan-out can now fire from a cron the moment the
    terminus is proven, with no agent awake — and an 18-unit wave that arms nothing would put eighteen billed
    GPUs beyond any monitoring. The launcher is the only thing that knows what it just rented, so it is the
    only thing that can arm correctly. Entries are built by `vast_watchdog.step1_fanout_entry`, never
    hand-shaped, and the pass is idempotent: re-launching a unit already in the list re-enables it rather than
    duplicating it (two entries for one unit means two relaunchers on one checkpoint prefix).

    Failure here is logged, never raised: an arming problem must not abort a launch that has already spent
    money, and the CI step that commits the file reports an unchanged file plainly.
    """
    try:
        import vast_watchdog as vw
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vast-watch.json")
        with open(path) as fh:
            doc = json.load(fh)
        by_uid = {e.get("unit_id"): e for e in doc.get("watch", [])}
        added, rearmed = [], []
        for uid in unit_ids:
            if uid in by_uid:
                by_uid[uid]["enabled"] = True
                by_uid[uid].pop("_disabled_why", None)
                rearmed.append(uid)
            else:
                doc["watch"].append(vw.step1_fanout_entry(uid, git_branch=branch))
                added.append(uid)
        with open(path, "w") as fh:
            json.dump(doc, fh, indent=2)
        print(f"[s1f] watchdog armed: +{len(added)} new, {len(rearmed)} re-enabled "
              f"({len(doc['watch'])} entries total)")
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] ⚠ COULD NOT ARM THE WATCHDOG ({type(e).__name__}: {e}) — the units above are running "
              f"UNWATCHED. Add them to vast-watch.json by hand.")


def _gpu_util(inst):
    """GPU utilisation %, or None if the host is not reporting it.

    READ BOTH SPELLINGS. The Vast instance payload carries the live figure as `gpu_util` on some responses and
    `cur_gpu_util` on others (`nrv04_vast_launch`'s field list names the latter). Reading only one silently
    yields None on the other, and a starved-host guard that always sees None is a guard that watches nothing —
    which is exactly the defect class this repo keeps paying for. Observed on instance 45936074 at 7 min in:
    `gpu_util` absent while the box was demonstrably up.

    None is NOT zero and must never be treated as an idle GPU: 'the host is not telling us' and 'the GPU is
    idle' are different facts, and only the second is evidence of a problem."""
    for k in ("gpu_util", "cur_gpu_util"):
        v = inst.get(k)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
    return None


def _require_bucket():
    if not BUCKET:
        raise SystemExit("[s1f] VAST_CKPT_BUCKET is required")
    return BUCKET


# ---- committed progress: the ONLY durable evidence that the science advanced -------------------------------
#
# WHY THIS EXISTS AND WHY IT IS NOT `phase.txt`. `phase.txt` says WHICH phase a unit reached; it says nothing
# about whether that phase is still moving. A rented Vast box can sit up with a wedged container, a dead
# sampler or an idle GPU and keep reporting `leg-complex-running` forever, which is precisely the "monitoring
# that watches nothing" failure this repo has paid for repeatedly. The spot commit store is written by the
# sampler itself every RBFE_WARMUP_CKPT_ITERS / RBFE_PROD_CKPT_ITERS iterations, survives the instance, and
# its iteration number only goes UP — so it is the progress scalar, and `phase.txt` is context around it.
#
# Layout, from rbfe_spot_checkpoint.S3CommitStore:
#     <ckpt_prefix>/<leg>/<phase>/iter-XXXXXXXX/<generation>/COMMITTED.json
# The scalar ranks production above warmup so the warmup->production transition can never read as a
# regression, and ranks the solvent leg above the complex leg for the same reason (a unit runs complex first,
# so its committed iteration count RESETS when the solvent leg starts).
_PHASE_RANK = {"warmup": 0, "production": 1}
_LEG_RANK = {"complex": 0, "solvent": 1}
_PHASE_STRIDE = 1_000_000
_LEG_STRIDE = 10_000_000


def committed_progress(s3, bucket, unit):
    """(scalar, detail) of the furthest committed iteration of this unit. scalar < 0 means UNREADABLE.

    `readable=False` is emphatically not "zero progress": treating a listing failure as zero manufactures a
    stall out of a network blip. Callers must skip, not act, on a negative scalar."""
    base = f"{checkpoint_prefix(unit, RESULT_PREFIX)}"
    best = {}
    try:
        pag = s3.get_paginator("list_objects_v2")
        for page in pag.paginate(Bucket=bucket, Prefix=f"{base}/"):
            for obj in page.get("Contents", []):
                # .../<leg>/<phase>/iter-XXXXXXXX/<generation>/COMMITTED.json
                rest = obj["Key"][len(base):].lstrip("/").split("/")
                if len(rest) < 3 or not rest[2].startswith("iter-"):
                    continue
                leg, phase = rest[0], rest[1]
                if leg not in _LEG_RANK or phase not in _PHASE_RANK:
                    continue
                try:
                    it = int(rest[2].split("iter-")[1])
                except (IndexError, ValueError):
                    continue
                k = (leg, phase)
                best[k] = max(best.get(k, 0), it)
    except Exception as e:  # noqa: BLE001
        return -1, f"commit store unlistable: {type(e).__name__}: {e}"
    if not best:
        return 0, "no commit yet (boot / stage / setup / minimise)"
    (leg, phase), it = max(best.items(),
                           key=lambda kv: (_LEG_RANK[kv[0][0]], _PHASE_RANK[kv[0][1]], kv[1]))
    scalar = _LEG_RANK[leg] * _LEG_STRIDE + _PHASE_RANK[phase] * _PHASE_STRIDE + it
    return scalar, f"{leg}/{phase}@{it}"


# ---- host exclusion: realised throughput fed back into selection -------------------------------------------
#
# `$/ns` ranking multiplies a CARD CONSTANT (vast_cost_model.MEASURED_NS_PER_DAY_84K), so it is structurally
# blind to a host that is slower than its card — a starved host scores as if healthy, wins selection, and
# keeps winning (pricing.md section A.1). Same blind spot as a host that never starts: infinite realised
# $/ns, invisible to the ranking, which is why `ResourceSpec.exclude_machine_ids` exists at all.
#
# The exclusion set therefore lives in S3, NOT in this process: a launch in one CI run must see what a
# monitor in a different CI run learned, with no agent awake in between.
#
# ⚠ SCOPE, and it is narrower than the rule pricing.md A.1 first proposed and then WITHDREW. Excluding on low
# `gpu_util` alone was wrong there because the low utilisation was PLUMED's CPU-side metadynamics bias, and
# the same host ran at 74 % on the very next (unbiased) phase — so it would have discarded a host that is
# perfectly good for every non-metadynamics leg. What survives is the narrower statement: for a workload with
# NO per-step host-side work, the card constant IS the throughput model, so a sustained shortfall against it
# is a real defect in the host. This lane is plain RBFE — no PLUMED, no bias, no per-step CPU coupling — so
# the narrow rule applies here and the withdrawn broad one is not being re-adopted.
_EXCLUDE_KEY = f"{RESULT_PREFIX}/_excluded_machines.json"
# Healthy hosts on this class of work sit ~70-95 %. 40 % is well below the healthy band and well above the
# ~0 % an idle box reports, so it separates "starved" from both "fine" and "not started".
STARVED_UTIL_PCT = float(os.environ.get("FANOUT_STARVED_UTIL_PCT", "40"))
# Two CONSECUTIVE observations, because a single sample can catch a checkpoint sync, an S3 upload or the gap
# between two chunks. One sample is noise; two spaced ticks is the host.
STARVED_TICKS = int(os.environ.get("FANOUT_STARVED_TICKS", "2"))
# Nothing is judged before the box has had time to pull a ~6 GiB image and build the hybrid system. Below
# this age a low utilisation is a cold start, not starvation.
STARVED_MIN_AGE_MIN = float(os.environ.get("FANOUT_STARVED_MIN_AGE_MIN", "75"))


# ---- rental ledger: realised spend, measured rather than reconstructed ------------------------------------
#
# WHY A LEDGER AND NOT `step1-fanout-handles.json`. That file is REWRITTEN by every launch, so a two-stage
# fan-out (one shakeout unit, then the remaining eighteen) loses the first stage's rental the moment the
# second one runs — and "what did this actually cost" then has to be reconstructed from memory, which is
# exactly how this lane's cost estimate came to be wrong by ~4x in the first place. The ledger is in S3,
# append-only, and carries the BID (what Vast charges, up to the on-demand cap) rather than `dph_total`, so
# realised spend is bid x billed-hours and not an inference from a rate card.
#
# Billed hours come from `_age_min`, refreshed on every progress check and frozen at reap. A preempted box
# that never comes back still has its last observed age, so its hours are counted, not lost.
_LEDGER_KEY = f"{RESULT_PREFIX}/_rentals.json"


def _load_ledger(s3, bucket):
    return _get_json(s3, bucket, _LEDGER_KEY) or {"_what": "every s1f-* rental: bid $/hr x observed billed "
                                                           "hours = realised spend for this lane",
                                                  "rentals": {}}


def _save_ledger(s3, bucket, doc):
    try:
        s3.put_object(Bucket=bucket, Key=_LEDGER_KEY, Body=json.dumps(doc, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] ledger save failed: {e}")


def _utcnow():
    import datetime
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def ledger_cost(doc):
    """(total_usd, n_rentals, detail_rows). PURE, so the arithmetic is unit-testable.

    Uses the BID, falling back to `dph_total` only when no bid was recorded (an older entry). Missing rate or
    missing hours contribute 0 and are COUNTED as unpriced rather than silently dropped — an unpriced rental
    is a hole in the number, and a total that hides holes is worse than one that admits them."""
    total, rows, unpriced = 0.0, [], 0
    for iid, r in sorted((doc.get("rentals") or {}).items()):
        rate = r.get("bid") or r.get("dph")
        hours = (r.get("billed_min") or 0) / 60.0
        try:
            usd = float(rate) * hours
        except (TypeError, ValueError):
            usd, unpriced = 0.0, unpriced + 1
            rate = None
        total += usd
        rows.append({"instance": iid, "unit_id": r.get("unit_id"), "machine_id": r.get("machine_id"),
                     "rate_usd_h": rate, "billed_h": round(hours, 2), "usd": round(usd, 3)})
    return round(total, 2), len(rows), rows, unpriced


def _load_excluded(s3, bucket):
    """This lane's exclusions ∪ the SHARED cross-lane set of hosts that refuse to start.

    ⚠ THE UNION IS THE POINT (2026-07-27). Before it, this lane's set held exactly one machine while the 5a-KS
    lane knew nine — so the 6:37 AM tick resumed the shakeout onto machine 46392, which that lane had already
    condemned. A host that never starts has infinite realised $/ns and is invisible to $/ns ranking, so each
    lane was paying a rental to rediscover what the other already knew. See `vast_machine_blacklist` for what
    is shared (host-scoped only) and what deliberately is not.
    """
    doc = _get_json(s3, bucket, _EXCLUDE_KEY) or {}
    env = os.environ.get("FANOUT_EXCLUDE_MACHINES", "")
    ids = {str(m) for m in (doc.get("machine_ids") or [])}
    ids |= {m.strip() for m in env.split(",") if m.strip()}
    import vast_machine_blacklist as vmb
    return vmb.union(ids, s3, bucket), doc


def _record_exclusion(s3, bucket, machine_id, why, scope="lane"):
    """Record a machine this lane will not re-rent. `scope="host"` ALSO publishes it cross-lane.

    The default is `lane` on purpose: a verdict that mixes this workload with the machine (the starved-host
    rule below) must not be exported, because `pricing.md` A.1 withdrew exactly that reasoning once already.
    Only a failure that is about the MACHINE — it refuses starts, its container never executes — is shared."""
    ids, doc = _load_excluded(s3, bucket)
    mid = str(machine_id)
    if scope == "host":
        import vast_machine_blacklist as vmb
        vmb.publish(s3, bucket, mid, why, lane="step1_fanout")
    if mid in ids:
        return False
    hist = doc.get("history") or []
    import datetime
    hist.append({"machine_id": mid, "why": why,
                 "utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
    try:
        s3.put_object(Bucket=bucket, Key=_EXCLUDE_KEY,
                      Body=json.dumps({"_what": "Vast machine_ids this lane refuses to re-rent. Realised "
                                                "throughput is not fed back into $/ns ranking, so without "
                                                "this a bad host keeps winning selection (pricing.md A.1).",
                                       "machine_ids": sorted(set(ids) | {mid}),
                                       "history": hist}, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] could not persist exclusion of machine {mid}: {e}")
        return False
    return True


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


_LAUNCH_LOG = []


def _lprint(msg):
    """print + retain, so the launch DECISION survives the CI log.

    monitor, collect and diag all write their readouts to committed files precisely because a GitHub job log
    is only readable from its tail and the tail is always runner boilerplate. `launch` was the one mode with
    no durable record — and it is the mode that spends money. It cost two diagnostic cycles on 2026-07-26 to
    answer "did the tick relaunch the preempted unit or not", a question the readout answers in one line."""
    print(msg, flush=True)
    _LAUNCH_LOG.append(str(msg))


def _write_launch_readout():
    try:
        with open("step1-fanout-launch-readout.txt", "w") as f:
            f.write("\n".join(_LAUNCH_LOG) + "\n")
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] could not write the launch readout: {e}")


_MARKET_HOLD_KEY_SUFFIX = "_market_hold.json"
# How long a hold may persist before it stops being a routine pause and becomes trimcrae's decision.
# ★ ELAPSED TIME, NOT A TICK COUNT, and that is deliberate: this repo's crons are throttled to roughly one
# run per workflow per hour whatever they ask for (measured 56-97 min for a */15), so "3 ticks" is not a
# knowable duration and a tick-based escalation would fire anywhere between 30 min and 5 hours.
MARKET_HOLD_ESCALATE_H = float(os.environ.get("FANOUT_MARKET_ESCALATE_H", "6"))


def market_snapshot(key, n_units, excluded=()):
    """(best_usd_per_ns, depth, rows) for a fleet of `n_units` from a LIVE Vast board read.

    `best_usd_per_ns` is the MEAN over the `n_units` cheapest qualifying offers, not the single best one —
    a fleet of 19 buys the 19 best offers, and pricing it off the one cheapest host would flatter a thin
    board exactly when the board being thin is the thing we are trying to detect. If fewer than `n_units`
    qualify, the mean is over what exists and `depth` records the shortfall, because a board that cannot
    fill the fleet is decision-relevant on its own even when its prices look fine.

    Ranking is delegated to `gpu_backend.rank_offers_by_usd_per_ns`, which is the same filter+score the
    renting path uses, so the guard cannot price a fleet the launcher would not actually buy."""
    from gpu_backend import _vast_offer_query, rank_offers_by_usd_per_ns
    res = FANOUT_RES
    if excluded:
        res = dataclasses.replace(res, exclude_machine_ids=tuple(str(m) for m in excluded))
    offers = _vast_request("GET", "/search/asks/", key,
                           params={"q": json.dumps(_vast_offer_query(res))}).get("offers", [])
    measured, capable = rank_offers_by_usd_per_ns(offers, res)
    take = measured[:max(1, int(n_units))]
    rows = [{"gpu": o.get("gpu_name"), "machine_id": o.get("machine_id"),
             "min_bid": p, "usd_per_ns": round(upn, 6)} for upn, p, o in take]
    depth = {"offers_returned": len(offers), "qualifying": len(capable), "priceable": len(measured),
             "needed": int(n_units), "used_for_mean": len(take)}
    best = (sum(r["usd_per_ns"] for r in rows) / len(rows)) if rows else None
    return best, depth, rows


def market_hold(n_units, n_pending, bucket, s3, key, excluded=()):
    """Decide whether a fleet launch may proceed. Returns True to HOLD.

    ⛔ CLAUDE.md §6: *"A THIN, EXPENSIVE MARKET IS A REASON TO PAUSE, NOT TO PAY."* trimcrae, 2026-07-26:
    *"I'd rather pause until availability opens than pay double per ns."*

    The exposure this exists for is not a single host — it is the 18-edge release, which fires AUTOMATICALLY
    on the shakeout unit's ddg.json. On the night the rule was written the board had thinned to 5 offers from
    a ~23 baseline at a $0.333/hr median floor, which prices this tranche at ~$87 against the $15-80 that was
    authorised. An automatic release into that market would have spent past its own authorisation with nobody
    choosing to.

    TWO FAILURE MODES THE RULE NAMES, both worse than the problem, and how each is answered here:
      * **A silent hold is indistinguishable from a finished fleet.** So every hold is written to the launch
        readout AND to `<results>/_market_hold.json` AND to a committed `step1-fanout-market-hold.json`, each
        carrying the snapshot that caused it. A reader at 3 AM gets the projected cost, the ceiling, the
        board depth and the offers that were priced — not "nothing to submit".
      * **A ceiling nobody can clear turns into an idle night.** The first hold records `first_held_utc`; once
        the hold has persisted past `MARKET_HOLD_ESCALATE_H` the readout stops being a notice and becomes a
        hard `::error::` that FAILS the job, which fires GitHub's own workflow-failure notification — the
        same session-independent alert path the watchdogs already rely on, so it reaches trimcrae with no
        agent awake. The guard never buys in on its own; the escalation hands him the decision.

    The gate is evaluated on the REMAINING TRANCHE, not on this tick's batch, because the authorisation is a
    tranche-level band and a per-batch test would wave through nineteen expensive units one at a time.
    """
    global _MARKET_GUARD_RAN
    hkey = f"{RESULT_PREFIX}/{_MARKET_HOLD_KEY_SUFFIX.lstrip('_')}"
    prev = _get_json(s3, bucket, hkey) or {}
    try:
        best, depth, rows = market_snapshot(key, n_pending, excluded)
    except Exception as e:  # noqa: BLE001
        # A board we could not READ is not a board we may assume is cheap. Same discipline as the watchdog's
        # "unreadable is not zero": refuse, and say the refusal was for lack of evidence.
        _MARKET_GUARD_RAN = True
        _lprint(f"[s1f] ⛔ MARKET GUARD COULD NOT READ THE BOARD ({type(e).__name__}: {e}) — HOLDING. An "
                f"unreadable market is not a cheap one, and this gate exists precisely for the case where "
                f"nobody is awake to check.")
        return True

    ok, projected, ceiling, ratio = cost_verdict(best, n_pending)
    _MARKET_GUARD_RAN = True
    basis = market_basis()
    head = (f"[s1f] MARKET GUARD ($/ns, CLAUDE.md §6): board {depth['offers_returned']} offers -> "
            f"{depth['qualifying']} qualifying, {depth['priceable']} priceable; mean $/ns over the "
            f"{depth['used_for_mean']} cheapest = "
            + (f"${best:.6f}" if best is not None else "UNPRICEABLE")
            + f" against a rung basis of ${basis:.6f}"
            + (f" ({ratio}x)" if ratio is not None else "")
            + f". Projected for the {n_pending} remaining unit(s): "
            + (f"${projected}" if projected is not None else "n/a")
            + f" against a ceiling of ${ceiling} (the TOP of this rung's own authorised band, derived from "
              f"cost_estimate — not a number typed here).")
    _lprint(head)

    doc = {"_what": "Why the step 1 fan-out did or did not launch, priced in $/ns. Written on EVERY guard "
                    "pass, because a silent hold is indistinguishable from a finished fleet.",
           "_rule": "CLAUDE.md §6 — a thin, expensive market is a reason to PAUSE, not to pay.",
           "utc": _utcnow(), "held": (not ok), "n_pending": n_pending,
           "mean_usd_per_ns_over_fleet": (round(best, 6) if best is not None else None),
           "basis_usd_per_ns": round(basis, 6), "ratio_vs_basis": ratio,
           "projected_usd": projected, "ceiling_usd": ceiling,
           "board_depth": depth, "offers_priced": rows,
           "first_held_utc": (prev.get("first_held_utc") if (not ok and prev.get("held")) else
                              (_utcnow() if not ok else None))}

    held_h = 0.0
    if doc["first_held_utc"]:
        try:
            t0 = calendar.timegm(time.strptime(doc["first_held_utc"], "%Y-%m-%dT%H:%M:%SZ"))
            held_h = max(0.0, (time.time() - t0) / 3600.0)
        except (ValueError, TypeError):
            held_h = 0.0
    doc["held_hours"] = round(held_h, 2)

    try:
        s3.put_object(Bucket=bucket, Key=hkey, Body=json.dumps(doc, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        _lprint(f"[s1f] market-hold state not persisted: {e}")
    try:
        with open("step1-fanout-market-hold.json", "w") as fh:
            json.dump(doc, fh, indent=2)
    except Exception as e:  # noqa: BLE001
        _lprint(f"[s1f] market-hold readout not written: {e}")

    if ok:
        _lprint(f"[s1f] MARKET GUARD PASSED — the fleet is buyable inside the authorised band. Launching.")
        return False

    _lprint(f"[s1f] ⛔ FLEET LAUNCH HELD ON PRICE. Nothing was rented and no unit was silently dropped; the "
            f"next scheduled tick re-checks. Offers priced this pass: {json.dumps(rows)}")
    if held_h >= MARKET_HOLD_ESCALATE_H:
        # The escalation. Not a decision the guard is allowed to make for him — a notification that one is
        # now needed. `::error::` also fails the job, which is what actually reaches a phone.
        print(f"::error title=STEP1 FAN-OUT HELD {held_h:.1f} H ON A BAD MARKET::The $/ns guard has refused "
              f"the 18-edge release for {held_h:.1f} h (since {doc['first_held_utc']}). Best achievable is "
              f"{ratio}x the rung basis, projecting ${projected} against a ${ceiling} ceiling. The guard will "
              f"NOT buy in on its own — this needs a decision: wait longer, re-price the ladder against a "
              f"changed market, or authorise the higher spend. Snapshot: step1-fanout-market-hold.json.",
              flush=True)
        _lprint(f"[s1f] ESCALATED — held {held_h:.1f} h (> {MARKET_HOLD_ESCALATE_H:.0f} h). This is now "
                f"trimcrae's call, not the guard's; the job fails so GitHub notifies.")
        globals()["_MARKET_HOLD_ESCALATED"] = True
    return True


def mode_launch():
    global _MARKET_GUARD_RAN
    bucket, s3 = _require_bucket(), _s3()
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("[s1f] VAST_API_KEY required to launch")
    units = default_units()
    idx_of = {u["unit_id"]: i for i, u in enumerate(units)}
    pending = _pending(s3, bucket, units)
    done = len(units) - len(pending)

    live = _live_instances(key)
    # ⚠ AN `exited` INSTANCE DOES NOT HOLD ITS UNIT'S SLOT. Vast teardown is two-layer: the container's EXIT
    # trap halts GPU billing key-free, but only CI can DESTROY the instance, so an exited box LINGERS in the
    # listing doing nothing. Counting it as occupying the unit would make every relaunch a silent no-op —
    # which is exactly what happened to the shakeout unit when it was preempted at 4:31 PM ET on 2026-07-26:
    # the container was gone, 260 committed iterations sat banked in S3, and the launcher would have reported
    # "nothing to submit" because the corpse still carried the label. This is the same lesson
    # vast_watchdog.ParalogueMdKind already encodes ("an `exited` container is NOT alive"); the fan-out
    # launcher simply did not have it yet.
    _TERMINAL = ("exited", "offline", "error")
    live_labels = {i.get("label") for i in live if (i.get("actual_status") or "") not in _TERMINAL}
    _dead = [i.get("label") for i in live if (i.get("actual_status") or "") in _TERMINAL]
    if _dead:
        _lprint(f"[s1f] {len(_dead)} instance(s) in a terminal state do NOT hold their unit's slot "
              f"(collect destroys them; their checkpoints are in S3 and a relaunch resumes): {_dead}")
    # a unit whose instance is already up is not re-submitted (idempotent top-up)
    todo = [u for u in pending if f"{LABEL_PREFIX}{idx_of[u['unit_id']]:02d}-{u['ligand_b']}"[:64]
            not in live_labels]

    # ---- FANOUT_ONLY: launch a NAMED subset, not "the next N in map order" --------------------------------
    # THE SHAKEOUT RULE NEEDS THIS. 0 of 19 units of this lane has ever produced a ddG: sampling is proven
    # (three hosts at 95-99 % GPU on the real system in wave 1) but the TERMINUS — reduce both legs, write
    # ddg.json, upload it — is not. CLAUDE.md's litmus test says a congeneric map has no result that would
    # cancel the rest, so there is no SCIENTIFIC reason to serialise; but "a pipeline is unproven until you
    # have watched it reach its real success terminus at least once" still bites, and fanning 19 wide into an
    # unproven terminus risks paying 19x for zero results. So exactly ONE unit runs first, and it is chosen
    # DELIBERATELY (the most-advanced checkpoint, i.e. the one closest to the terminus, so the proof costs the
    # least wall-clock) rather than by map position. Without this flag "one unit" would mean unit 00.
    only = [t.strip() for t in (os.environ.get("FANOUT_ONLY") or "").split(",") if t.strip()]
    if only:
        matched = [u for u in todo if any(t in u["unit_id"] or t in u["ligand_b"] for t in only)]
        skipped = len(todo) - len(matched)
        _lprint(f"[s1f] FANOUT_ONLY={only!r} -> {len(matched)} of {len(todo)} pending units selected "
              f"({skipped} held back)")
        if not matched:
            raise SystemExit(f"[s1f] FANOUT_ONLY={only!r} matched no pending unit — refusing to launch "
                             f"something other than what was asked for")
        todo = matched

    # ---- the terminus gate --------------------------------------------------------------------------------
    # THE WHOLE POINT OF THE ONE-THEN-EIGHTEEN SHAPE, expressed as a machine condition rather than as an
    # agent remembering to come back. `FANOUT_REQUIRE_PROVEN_TERMINUS=1` refuses to submit until at least one
    # unit's ddg.json exists in S3 — i.e. until reduce->commit->upload has actually been observed once.
    #
    # WHY IT IS A GATE AND NOT A DECISION I MAKE LATER. A gate can be put on a cron, so the fan-out fires the
    # MINUTE the terminus is proven instead of the next time somebody looks. That is strictly more parallel
    # than waiting for a human or an agent, and strictly safer than launching early, which is the combination
    # the shakeout rule is actually asking for. Serialising costs wall-clock and buys nothing else.
    #
    # ⚠⚠ THE GATE HOLDS BACK THE FAN-OUT. IT MUST NEVER BLOCK THE SHAKEOUT UNIT'S OWN RESUME.
    # As first written it returned outright whenever no ddg.json existed — which is a DEADLOCK, and not a
    # theoretical one: the shakeout unit was preempted at 4:31 PM ET on 2026-07-26 with 260 iterations banked,
    # and a gate that refuses to launch anything until a ddg.json exists would never have restarted the one
    # unit whose entire job is to produce that ddg.json. The cron would have ticked all night launching
    # nothing. So while the terminus is unproven the gate NARROWS to the shakeout unit instead of returning:
    # the fifteen cold units stay held, and the unit that is already paid for keeps going.
    if os.environ.get("FANOUT_REQUIRE_PROVEN_TERMINUS") == "1":
        proven = [u["unit_id"] for u in units if _exists(s3, bucket, result_key(u, RESULT_PREFIX))]
        if proven:
            _lprint(f"[s1f] terminus PROVEN by {len(proven)} unit(s) ({proven[0]}) — fan-out released")
        else:
            shakeout = (os.environ.get("FANOUT_SHAKEOUT_UNIT") or "").strip()
            if not shakeout:
                _lprint("[s1f] TERMINUS NOT PROVEN and no FANOUT_SHAKEOUT_UNIT named — holding everything. "
                      "Set FANOUT_SHAKEOUT_UNIT so the gate can keep the shakeout unit alive while it holds "
                      "the other units back.")
                _write_launch_readout()
                return
            keep = [u for u in todo if shakeout in u["unit_id"] or shakeout in u["ligand_b"]]
            _lprint(f"[s1f] TERMINUS NOT PROVEN — no unit has a ddg.json, so reduce/commit/upload has never "
                  f"been observed on this lane. Holding {len(todo) - len(keep)} unit(s); RESUMING the "
                  f"shakeout unit ({shakeout}) if it needs it: {len(keep)} to submit.")
            todo = keep

    # Slots count only instances actually DOING something, for the same reason live_labels does: a fleet of
    # exited corpses would otherwise report zero free slots and silently launch nothing.
    _busy = [i for i in live if (i.get("actual_status") or "") not in _TERMINAL]
    slots = max(0, WIDTH - len(_busy))
    batch = todo[:slots]

    lo, hi = cost_estimate(len(batch))
    _lprint(f"[s1f] units={len(units)} done={done} pending={len(pending)} live={len(live)} "
          f"free_slots={slots} -> submitting {len(batch)}")
    _lprint(f"[s1f] cost of THIS submission ({len(batch)} units): plan ${cost_plan(len(batch))} "
          f"(band ${lo}-{hi}) | whole remaining tranche ({len(pending)} units): "
          f"plan ${cost_plan(len(pending))} (band ${'-'.join(str(x) for x in cost_estimate(len(pending)))})")
    _lprint(f"[s1f] wave shape: {json.dumps(wave_plan(len(pending), WIDTH))}")
    for u in batch:
        _lprint(f"[s1f]   queue {u['unit_id']}  ({u['ligand_a']} -> {u['ligand_b']}, {u['edge_class']})")
    if not batch:
        _lprint("[s1f] nothing to submit (fleet already at width, or all units done)")
        _write_launch_readout()
        return
    # ⛔ THE $/ns MARKET GUARD (CLAUDE.md §6). EVERY launch must clear a price gate — fleet or single unit.
    #
    # Placed here, AFTER the batch is known and BEFORE `FANOUT_CONFIRM`, for two reasons. It needs the batch
    # size to know what it is pricing; and putting it before the confirm check means a DRY run exercises the
    # guard and prints its snapshot without renting anything, so the readout can be inspected on demand.
    #
    # ★★ WHY `len(batch) > 1` IS NO LONGER THE TEST (trimcrae, 2026-07-27: *"Why are there so many high $/ns
    # rows that are flagged but you're still paying for them?"*). The rule's original last line exempted "a
    # single unit already running", and this branch was where that exemption was cashed — so the shakeout
    # unit's resume passed through unpriced every time spot churn killed its host, and it was running at
    # **1.76x the ladder basis with `⚠ DRIFT` on the board** while the eighteen-edge fan-out at 2.05x was
    # correctly refused. The exemption was cut on the wrong axis: a RESUME ONTO A NEW HOST IS A NEW PURCHASE.
    # The right axis is "would waiting lose work?", and for a checkpointed unit it does not — the host is
    # already gone and the commit store is a durable S3 object. So both paths are gated, with the ceiling each
    # one deserves:
    #   * a FLEET buys a whole tranche at once, so it is measured against that tranche's authorised DOLLAR
    #     band (`market_hold` -> `congeneric_fanout.market_ceiling_usd`);
    #   * a SINGLE HOST re-enters a leg at an unknown fraction of its work, so a dollar projection would be
    #     the full unit's cost and meaningless. It is measured against the RATE instead — the drift line the
    #     board already prints (`relaunch_market_gate`, CLAUDE.md §1's 1.5x).
    _excluded_for_guard, _ = _load_excluded(s3, bucket)
    if os.environ.get("FANOUT_MARKET_OVERRIDE") == "1":
        _lprint("[s1f] ⚠ FANOUT_MARKET_OVERRIDE=1 — the $/ns guard is BYPASSED for this launch. That is a "
                "deliberate, recorded choice to spend outside the rung's authorised band.")
        _MARKET_GUARD_RAN = True
    elif len(batch) > 1:
        if market_hold(len(batch), len(pending), bucket, s3, key, _excluded_for_guard):
            _write_launch_readout()
            return
    else:
        import relaunch_market_gate as rmg
        _held, _gdoc = rmg.gate("step1_fanout", batch[0]["unit_id"], FANOUT_RES, key=key,
                                excluded=_excluded_for_guard, s3=s3, state_bucket=bucket,
                                state_prefix=RESULT_PREFIX)
        _MARKET_GUARD_RAN = True
        for _ln in (f"[s1f] SINGLE-HOST $/ns GATE: {'⛔ HELD' if _held else '✅ CLEAR'} — {_gdoc['reason']}",
                    f"[s1f]   board={json.dumps(_gdoc.get('board_depth'))} "
                    f"priced={json.dumps(_gdoc.get('offers_priced'))}"):
            _LAUNCH_LOG.append(_ln)
        if _held:
            _lprint("[s1f] Nothing was rented and no unit was dropped; the checkpoint is untouched in S3 and "
                    "the next scheduled tick re-checks.")
            if _gdoc.get("escalated"):
                # A ceiling nobody can clear must become trimcrae's decision, not an idle night. Reuse the
                # lane's existing escalation flag rather than inventing a second exit path.
                globals()["_MARKET_HOLD_ESCALATED"] = True
            _write_launch_readout()
            return

    # BELT, not braces. If a future edit ever routes a batch past the block above, this refuses rather than
    # renting: by CLAUDE.md §6 a rental that has not consulted the market is a bug, and the safe failure is
    # to hold. Widened from `len(batch) > 1` with the exemption it was protecting.
    if batch and not _MARKET_GUARD_RAN:
        _lprint(f"[s1f] ⛔ LAUNCH HELD ({len(batch)} unit(s)) — the $/ns market guard did not run. "
                f"Refusing to rent what was never priced.")
        _write_launch_readout()
        return

    if os.environ.get("FANOUT_CONFIRM") != "1":
        _lprint("[s1f] DRY — set FANOUT_CONFIRM=1 to actually rent instances")
        _write_launch_readout()
        return

    # Machines this lane has already learned are bad — a capacity refusal, or a sustained shortfall against
    # the card constant the ranking assumes. Read from S3 so a launch in one CI run inherits what a monitor in
    # a different CI run discovered, with no agent awake in between.
    excluded, _ = _load_excluded(s3, bucket)
    if excluded:
        _lprint(f"[s1f] excluding {len(excluded)} machine(s) from offer selection: {excluded}")

    backend, handles = get_backend("vast"), []
    _ledger = _load_ledger(s3, bucket)
    # Machines used by THIS wave are also excluded as we go, so an 18-wide fan-out lands on 18 distinct hosts
    # rather than stacking on the single cheapest one and contending for its GPU.
    used_machines = set(excluded)
    for u in batch:
        spec = build_jobspec(u, os.environ.get("GIT_BRANCH", "main"), bucket, idx_of[u["unit_id"]],
                             exclude_machine_ids=used_machines)
        try:
            h = backend.submit(spec)
        except Exception as e:  # noqa: BLE001 — one host shortage must not abort the wave
            # Same `flush=True`-to-`_lprint` defect as the submit-success line below, and worse here: this
            # handler's entire job is to keep the wave going through a Vast capacity refusal
            # ({"success": false, "error": "resources_unavailable"}), which CLAUDE.md records as routine.
            # Raising TypeError from inside the except block turned "skip this host, try the next" into
            # "abort the whole wave", on the most-expected failure this launcher has.
            _lprint(f"[s1f] SUBMIT FAILED {u['unit_id']}: {e}")
            continue
        # Print the FLOOR, the BID and the premium separately. The fan-out's cost estimate was built from a
        # single instance's realized $/hr with no visibility into how much of that was our own bid premium.
        # Making it visible at submit time is what stops the next estimate inheriting it silently — this is the
        # lane whose realized $0.35-0.39/hr was later mistaken for "the 4090 market" when it was really
        # x1.5 on a min_bid-ranked offer. Report the premium we ACTUALLY bid rather than a hardcoded multiple:
        # under the derived policy (floor + a staleness tick) it should now be a fraction of a cent.
        _dph = h.extra.get("dph")
        _floor = h.extra.get("min_bid")
        _bid = h.extra.get("bid")
        _prem = (f" (floor ${_floor}/hr -> bid ${_bid}/hr"
                 f"{f', +${round(float(_bid) - float(_floor), 4)}/hr premium' if _bid else ''})"
                 if _floor else "")
        _mid = h.extra.get("machine_id")
        if _mid is not None:
            used_machines.add(str(_mid))
        # NO `flush=True` HERE. `_lprint` is not `print` — it flushes internally — and passing print's kwarg
        # to it raised TypeError on the FIRST SUCCESSFUL SUBMISSION, i.e. only ever on the money path.
        # Observed 2026-07-26 7:54 PM ET (autoscale run 30226203566): instance 45951628 was rented and the
        # process then died on this line, BEFORE the rental ledger entry, before `_save_ledger`, before
        # `_arm_watchdog` and before the launch readout. So the box billed while being absent from realised
        # spend and absent from the watch list. Fanned 19 wide it would have submitted exactly one unit per
        # tick, none of them ledgered or watched. tests/test_congeneric_fanout.py now binds every internal
        # call in this module against its callee's signature, statically, so this class cannot recur.
        _lprint(f"[s1f] submitted {spec.name} -> instance {h.job_id} machine {_mid} dph≈${_dph}/hr{_prem}")
        handles.append({"unit_id": u["unit_id"], "label": spec.name, "instance": h.job_id,
                        "machine_id": _mid, "dph": h.extra.get("dph"),
                        "min_bid": _floor, "bid": _bid})
        _ledger.setdefault("rentals", {})[str(h.job_id)] = {
            "unit_id": u["unit_id"], "label": spec.name, "machine_id": _mid,
            "bid": _bid, "min_bid": _floor, "dph": _dph, "billed_min": 0,
            "launched_utc": _utcnow(), "last_seen_utc": None}
    _save_ledger(s3, bucket, _ledger)
    _arm_watchdog([h["unit_id"] for h in handles], os.environ.get("GIT_BRANCH", "main"))
    with open("step1-fanout-handles.json", "w") as f:
        json.dump(handles, f, indent=2)
    # the label -> unit map, so a later collect/monitor can name instances without re-deriving the index
    try:
        _s3().put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_manifest.json",
                         Body=json.dumps({f"{LABEL_PREFIX}{i:02d}-{u['ligand_b']}"[:64]: u["unit_id"]
                                          for i, u in enumerate(units)}, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        _lprint(f"[s1f] manifest upload skipped: {e}")
    _write_launch_readout()


def mode_monitor():
    """Tight-cadence PROGRESS check (not a liveness ping): per-unit phase + per-instance state, one line each."""
    bucket, s3 = _require_bucket(), _s3()
    units = default_units()
    key = os.environ.get("VAST_API_KEY")
    # ⚠ THREE STATES, NOT TWO: N instances, ZERO instances, and COULD-NOT-ASK. Dropping the early `return`
    # here was right — the committed-iteration census below reads S3 and does not need the Vast key, so a
    # missing key should not cost us the progress check. But `live = []` then prints "live s1f-* instances: 0",
    # which reads as "nothing is billing" when it actually means "nothing was measured". Reporting an
    # unmeasured state as a measured zero is this repo's most expensive defect class, and a false zero on a
    # RENTAL board is the version of it that costs money. `_live_instances` returning None is likewise
    # "the API call failed", never "none".
    live = _live_instances(key) if key else None
    if live is None:
        print("[s1f] ⚠ live s1f-* instances: UNKNOWN — "
              + ("no VAST_API_KEY in this environment" if not key else "the instance list could not be read")
              + ". This is NOT 'zero': any rental is unobserved here and could still be billing. "
                "The per-unit progress census below is unaffected — it reads S3.")
        live = []
    else:
        print(f"[s1f] live s1f-* instances: {len(live)}")
    for i in live:
        print(f"[s1f]   id={i.get('id')} label={i.get('label')} actual={i.get('actual_status')} "
              f"cur={i.get('cur_state')} dph=${i.get('dph_total')} gpu={i.get('gpu_name')} "
              f"util={_gpu_util(i)}% age_min={_age_min(i)} msg={(i.get('status_msg') or '')[:120]!r}")
    # PROGRESS, not liveness. The committed-iteration census is the durable evidence the science advanced;
    # `phase.txt` and the leg JSONs are context around it. `prev` is the previous check's census, so this
    # block can answer "did it move SINCE LAST TIME" — which is the only question worth asking of a running
    # sampler, and the one a phase marker structurally cannot answer.
    prev = (_get_json(s3, bucket, f"{RESULT_PREFIX}/_progress_prev.json") or {})
    cur, n_done = {}, 0
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
        scalar, detail = committed_progress(s3, bucket, u)
        was = (prev.get(u["unit_id"]) or {}).get("scalar")
        if scalar >= 0:
            cur[u["unit_id"]] = {"scalar": scalar, "detail": detail, "utc": _utcnow()}
        rate = _iter_rate(prev.get(u["unit_id"]), scalar)
        if scalar < 0:
            delta = "UNREADABLE (skipped, NOT counted as zero)"
        elif was is None:
            delta = "first census"
        elif scalar > was:
            delta = f"+{scalar - was} since last check" + (f", {rate} iter/h" if rate else "")
        elif phase and not phase.startswith(("boot", "staged")):
            delta = "NO ADVANCE since last check"
        else:
            delta = "no commit yet (cold start)"
        slow = (rate is not None and rate < 0.5 * EXPECTED_ITER_PER_H
                and (phase or "").startswith("leg-"))
        print(f"[s1f]   {u['unit_id']:56s} {phase or 'not-started':28s} legs_done={legs} "
              f"committed={detail} [{delta}]"
              + (f"  <-- {rate} iter/h is under half the measured {EXPECTED_ITER_PER_H:.0f}; "
                 f"if it holds across checks and is not an end-of-leg MBAR pause, this host is slower than "
                 f"its card and should be re-rented elsewhere" if slow else ""))
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

    # ---- billed hours + the starved-host guard ------------------------------------------------------------
    # Two jobs, one pass over the live fleet, because both need the same `age_min` / `gpu_util` sample.
    if key:
        ledger = _load_ledger(s3, bucket)
        util_state = _get_json(s3, bucket, f"{RESULT_PREFIX}/_util_state.json") or {}
        new_state = {}
        # Recomputed here rather than borrowed from the nudge block above: the backfill below needs it, and a
        # name that only exists because an earlier `if key:` block happened to run is a NameError waiting for
        # someone to move a block.
        _idx = {u["unit_id"]: n for n, u in enumerate(units)}
        label_to_unit = {f"{LABEL_PREFIX}{_idx[u['unit_id']]:02d}-{u['ligand_b']}"[:64]: u for u in units}
        for i in live:
            iid, age = str(i.get("id")), _age_min(i)
            row = (ledger.get("rentals") or {}).get(iid)
            if row is None:
                # ★ BACKFILL — A LIVE RENTAL MISSING FROM THE LEDGER IS BILLING INVISIBLY (2026-07-26).
                # The ledger row is written by `mode_launch` immediately after `backend.submit`, so anything
                # that kills the launcher between the two leaves a rented, running, BILLING host that
                # realised-spend arithmetic cannot see — and, because the update above is gated on the row
                # already existing, could never later see. That is not hypothetical: the `_lprint(...,
                # flush=True)` TypeError did exactly this to instance 45951628 at 7:54 PM ET.
                # `monitor` is the one mode that meets every live instance on every pass, so it is where the
                # ledger is reconciled against reality. Priced from the LIVE listing (dph is what Vast is
                # charging now), and flagged, because a backfilled row is a repair and its bid/floor
                # provenance is genuinely unknown — an honest gap beats a fabricated one.
                row = {"unit_id": (label_to_unit.get(i.get("label") or "") or {}).get("unit_id"),
                       "label": i.get("label"), "machine_id": i.get("machine_id"),
                       "bid": None, "min_bid": None, "dph": i.get("dph_total"), "billed_min": 0,
                       "launched_utc": None, "last_seen_utc": None,
                       "_backfilled": "not recorded at launch (launcher died between submit and ledger "
                                      "write); reconciled from the live Vast listing by monitor"}
                ledger.setdefault("rentals", {})[iid] = row
                print(f"[s1f] LEDGER BACKFILL: instance {iid} ({i.get('label')}) was billing at "
                      f"${i.get('dph_total')}/hr with no ledger row — realised spend was under-reporting "
                      f"it. Row created; bid/floor unknown for this rental.")
            if row is not None:
                # MAX, not last: a paused/preempted box can report a smaller age on resume, and billed
                # minutes only ever go up.
                row["billed_min"] = max(int(row.get("billed_min") or 0), int(age))
                row["last_seen_utc"] = _utcnow()
            util = _gpu_util(i)
            running = (i.get("actual_status") == "running")
            if util is None or not running or age < STARVED_MIN_AGE_MIN:
                continue
            strikes = int((util_state.get(iid) or {}).get("strikes", 0))
            if float(util) < STARVED_UTIL_PCT:
                strikes += 1
            else:
                strikes = 0
            new_state[iid] = {"strikes": strikes, "util": util, "utc": _utcnow()}
            if strikes < STARVED_TICKS:
                continue
            # STARVED. This lane is plain RBFE — no PLUMED, no per-step host-side work — so the card constant
            # the $/ns ranking uses IS the throughput model here, and a host sustaining <40 % against a
            # healthy 70-95 % is not doing the work we are paying for. (pricing.md A.1's WITHDRAWN broad rule
            # was "exclude any low-util machine"; it was withdrawn because a metadynamics leg is CPU-bound
            # and the same host ran at 74 % once the bias was gone. That escape does not exist for this
            # workload, which is why the narrow rule is applied here and only here.)
            mid = i.get("machine_id")
            print(f"[s1f] STARVED HOST: instance {iid} (machine {mid}, {i.get('label')}) held "
                  f"gpu_util={util}% < {STARVED_UTIL_PCT}% for {strikes} consecutive checks at age "
                  f"{age} min — destroying and excluding. Checkpoints are in S3; a relaunch resumes.")
            try:
                _vast_request("DELETE", f"/instances/{iid}/", key)
            except Exception as e:  # noqa: BLE001
                print(f"[s1f] destroy {iid} failed: {e}")
            if mid is not None and _record_exclusion(s3, bucket, mid,
                                                     f"gpu_util {util}% for {strikes} checks on a plain-RBFE "
                                                     f"leg (healthy band 70-95%); instance {iid}"):
                print(f"[s1f] machine {mid} added to the lane exclusion set")
            new_state.pop(iid, None)
        _save_ledger(s3, bucket, ledger)
        try:
            s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_util_state.json",
                          Body=json.dumps(new_state, indent=2).encode())
        except Exception as e:  # noqa: BLE001
            print(f"[s1f] util state save failed: {e}")

    # The census is written AFTER the guard, so "did it advance since last check" compares against the
    # previous CHECK and not against something this pass just wrote.
    try:
        s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_progress_prev.json",
                      Body=json.dumps(cur, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] progress census save failed: {e}")

    # Summary LAST: a CI log is read from its tail, and the per-instance detail above scrolls out of view.
    # This block is the tight-cadence progress check — instance states, GPU utilisation and the phase
    # histogram in one place, so "is it ADVANCING?" is answerable without paging back through the log.
    states, utils = {}, []
    for i in live:
        states[i.get("actual_status") or "?"] = states.get(i.get("actual_status") or "?", 0) + 1
        if _gpu_util(i) is not None:
            utils.append(_gpu_util(i))
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
        # ⚠ WHERE IN THE TICK THIS WAS TAKEN, because it misled a reader (me) twice in one session. The
        # autoscale tick runs monitor -> collect -> launch, and `live` is fetched ONCE at the top of this
        # function, so this snapshot is a BEFORE picture: it cannot show instances this tick's launch went on
        # to create, instances its collect went on to reap, or the effect of the nudge below. Reading
        # "live_instances: 1" here and concluding "the launch did nothing" is exactly the wrong inference —
        # the launch had not run yet. A second snapshot after the launch would be more current but would
        # destroy the advance diff, since _progress_prev.json would be overwritten seconds after it was set.
        "_snapshot_point": "START of the tick — before this tick's collect, nudge and launch",
        "n_units": len(units), "n_complete": n_done,
        "live_instances": len(live), "instance_states": states,
        "gpu_util": utils, "phases": phases,
        # status_msg is what distinguishes a host still PULLING the ~6 GiB image (documented ~20-40 min on
        # cheap 4090 hosts, and normal) from a container that is genuinely wedged — both show actual_status
        # "loading". Without it, "loading for 29 minutes" is unreadable either way.
        "instances": [{"id": i.get("id"), "label": i.get("label"), "status": i.get("actual_status"),
                       "cur_state": i.get("cur_state"), "status_msg": (i.get("status_msg") or "")[:200],
                       "gpu": i.get("gpu_name"), "gpu_util": _gpu_util(i),
                       "inet_down": i.get("inet_down"),
                       "dph": i.get("dph_total"), "age_min": _age_min(i)}
                      for i in live],
        "units": [{"unit_id": u["unit_id"],
                   "phase": ("done" if _exists(s3, bucket, result_key(u, RESULT_PREFIX))
                             else _get_text(s3, bucket, f"{RESULT_PREFIX}/{u['unit_id']}/phase.txt")
                             or "not-started"),
                   # The committed-iteration census, carried into the artifact so the progress trail this
                   # file leaves is a record of ADVANCE and not just of phase labels.
                   "committed": (cur.get(u["unit_id"]) or {}).get("detail"),
                   "committed_scalar": (cur.get(u["unit_id"]) or {}).get("scalar"),
                   "committed_prev_scalar": (prev.get(u["unit_id"]) or {}).get("scalar"),
                   "ddg_bind_kcal": (_get_json(s3, bucket, result_key(u, RESULT_PREFIX)) or {})
                   .get("ddg_bind_kcal")}
                  for u in units],
        "realised_usd_so_far": ledger_cost(_load_ledger(s3, bucket))[0],
        "plan_usd_whole_tranche": cost_plan(len(units)),
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
    finished = {r["unit_id"] for r in results}
    idx_of = {u["unit_id"]: i for i, u in enumerate(units)}
    label_of = {f"{LABEL_PREFIX}{idx_of[u['unit_id']]:02d}-{u['ligand_b']}"[:64]: u["unit_id"] for u in units}
    ledger = _load_ledger(s3, bucket)
    # Consecutive-terminal-observation state, in S3 so one CI run inherits what the previous one saw.
    _terminal = _get_json(s3, bucket, f"{RESULT_PREFIX}/_terminal_state.json") or {}
    _terminal_next = {}
    for i in (_live_instances(key) if key else []):
        lab, st = i.get("label"), (i.get("actual_status") or "")
        age_min = _age_min(i)
        # FREEZE billed minutes BEFORE the reap. After the DELETE the instance is unreadable, so an
        # unrecorded final age is lost forever and the realised-cost total silently under-reports.
        _row = (ledger.get("rentals") or {}).get(str(i.get("id")))
        if _row is not None:
            _row["billed_min"] = max(int(_row.get("billed_min") or 0), int(age_min))
            _row["last_seen_utc"] = _utcnow()
        why = None
        if label_of.get(lab) in finished:
            why = "result in S3"
        elif st in ("exited", "offline", "error"):
            # ⚠ A TRANSIENT `exited` IS NOT A FAILURE, and this reaper became dangerous the moment it moved
            # onto a 20-minute cron. s1f-04 read `exited` at 10 minutes in wave 1 and came back `running` on
            # its own (lane record section 8). Destroying on a single observation would throw away a host
            # that was about to recover — survivable, because the checkpoint resumes, but it costs a boot and
            # a fresh rental EVERY time it misfires, across a 19-host fleet, unattended, all night.
            #
            # So a terminal state must be seen on TWO CONSECUTIVE ticks before it is believed. The finished
            # case above is unaffected: a unit with its ddg.json in S3 is destroyed on sight, because there
            # the evidence is the result itself and not the instance's mood.
            seen = int((_terminal.get(str(i.get("id"))) or {}).get("ticks", 0)) + 1
            _terminal_next[str(i.get("id"))] = {"ticks": seen, "state": st, "utc": _utcnow()}
            if seen < 2:
                print(f"[s1f] {i.get('id')} ({lab}) reads {st} — first observation, NOT reaping. A transient "
                      f"`exited` recovered on its own in wave 1; two consecutive ticks are required.")
                continue
            why = f"terminal state {st} on {seen} consecutive checks"
        elif age_min > REAP_AGE_MIN:
            why = f"age {age_min} min > {REAP_AGE_MIN}"
        if not why:
            continue
        try:
            _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
            print(f"[s1f] reaped {i.get('id')} ({lab}): {why}")
            if _row is not None:
                _row["reaped_utc"], _row["reaped_why"] = _utcnow(), why
        except Exception as e:  # noqa: BLE001
            print(f"[s1f] reap {i.get('id')} failed: {e}")
    _save_ledger(s3, bucket, ledger)
    # Rewritten, not merged: an instance absent from this pass is gone or recovered, and either way its
    # streak is over. A streak that persisted across a recovery would reap a healthy host on its next blip.
    try:
        s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_terminal_state.json",
                      Body=json.dumps(_terminal_next, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[s1f] terminal-state save failed: {e}")

    # ---- realised spend against the estimate -------------------------------------------------------------
    # Reported HERE, at collect, and written into the map artifact — not left to be reconstructed later. The
    # ~4x cost error this lane already made was possible precisely because the realised number lived only in
    # a memory of what a few instances had cost.
    total, n_rent, rows, unpriced = ledger_cost(ledger)
    plan_all, plan_run = cost_plan(len(units)), cost_plan(max(1, len(results)))
    print(f"\n[s1f] REALISED SPEND: ${total} over {n_rent} rental(s)"
          + (f"  ⚠ {unpriced} rental(s) carried no usable rate and contribute 0" if unpriced else ""))
    print(f"[s1f] against plan: whole 19-unit tranche ${plan_all}; "
          f"{len(results)} completed unit(s) would plan at ${plan_run}")
    for r in rows:
        print(f"[s1f]   {r['instance']:>12} {str(r['unit_id'])[:44]:44s} machine={r['machine_id']} "
              f"${r['rate_usd_h']}/hr x {r['billed_h']}h = ${r['usd']}")
    out["realised_usd"] = total
    out["realised_rentals"] = rows
    out["plan_usd_whole_tranche"] = plan_all
    out["cost_note"] = ("realised = recorded BID $/hr x observed billed hours (Vast charges the bid up to the "
                        "machine's on-demand price). Plan = vast_cost_model.LADDER_REFERENCE_GPU_H repriced "
                        "at the best-10-mean $/reference-GPU-hour from vast-ladder-repricing.json.")
    with open("step1-fanout-map.json", "w") as f:
        json.dump(out, f, indent=2)
    s3.put_object(Bucket=bucket, Key=f"{RESULT_PREFIX}/_map.json", Body=json.dumps(out, indent=2).encode())


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
        # Every launched unit is dumped, not only the terminal ones. The container stdout carries the
        # per-iteration sampling RATE, which is the number the whole cost model rests on — and reading it off
        # ONE preempted host cannot distinguish a slow host from a systematically slow system. Bounded by the
        # launched set (<= FANOUT_WIDTH), so this stays cheap.
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


def mode_reap():
    """CONDEMN a host: destroy the selected s1f-* instance(s) AND blacklist their machines for this lane.

    WHY THIS IS NOT `stop`. `stop` is cleanup — it destroys and says nothing about the machine, so the very
    next `launch` is free to rent the same box back. That is correct for "I am done spending" and wrong for
    "this host is bad", and the difference is the whole content of CLAUDE.md's Vast rule: a host that never
    starts (or never advances) has infinite realised $/ns, is therefore invisible to $/ns ranking, and
    without an explicit exclusion keeps winning selection and keeps failing. The lane already has the
    exclusion set and `launch` already consults it; what was missing was any way for an operator who has
    just diagnosed a bad host to put one in it. Only the starved-host guard could, and only for the single
    symptom it measures.

    WHAT THIS DOES NOT DO: relaunch. Reaping and re-renting are deliberately two dispatches so the exclusion
    is durable in S3 *before* anything picks a host, and so a reap can never be the thing that silently
    starts spending. Follow it with `launch_confirm`.

    SELECTOR IS MANDATORY. `stop`'s blank-means-everything default is a documented footgun on a shared
    account; a mode that also writes a permanent blacklist must not inherit it.
    """
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("[s1f] VAST_API_KEY required to reap")
    want = (os.environ.get("DIAG_UNIT") or os.environ.get("FANOUT_ONLY") or "").strip()
    if not want:
        raise SystemExit("[s1f-reap] refusing a blank selector: name the instance id or a label substring. "
                         "Blank would condemn every host this lane is running and blacklist their machines.")
    why = (os.environ.get("REAP_REASON") or "").strip()
    if not why:
        raise SystemExit("[s1f-reap] REAP_REASON is required — an exclusion with no recorded cause is a "
                         "machine nobody can ever justify un-excluding.")
    bucket, s3 = _require_bucket(), _s3()
    live = _live_instances(key) or []
    sel = [i for i in live if want == str(i.get("id")) or want in (i.get("label") or "")]
    if not sel:
        print(f"[s1f-reap] nothing matches {want!r} among {[i.get('label') for i in live]} — no action")
        return
    for i in sel:
        iid, mid = i.get("id"), i.get("machine_id")
        try:
            _vast_request("DELETE", f"/instances/{iid}/", key)
            print(f"[s1f-reap] destroyed {iid} ({i.get('label')}) on machine {mid}")
        except Exception as e:  # noqa: BLE001
            print(f"[s1f-reap] destroy {iid} failed: {e} — NOT recording an exclusion for a box that may "
                  f"still be billing; fix the destroy first")
            continue
        if mid is None:
            print(f"[s1f-reap] {iid} has no machine_id in the listing — destroyed, but nothing to exclude")
        elif _record_exclusion(s3, bucket, mid, why):
            print(f"[s1f-reap] machine {mid} added to the lane exclusion set: {why}")
        else:
            print(f"[s1f-reap] machine {mid} was already excluded (or the write failed) — see the log above")
    print(f"[s1f-reap] reaped {len(sel)} instance(s). Re-rent with launch_confirm; the exclusion is in S3 "
          f"and binds it with no agent awake.")


_MODES = [("PLAN", mode_plan), ("STAGE", mode_stage), ("PRECHECK", mode_precheck), ("LAUNCH", mode_launch),
          ("COLLECT", mode_collect), ("MONITOR", mode_monitor), ("DIAG", mode_diag), ("REAP", mode_reap),
          ("STOP", mode_stop)]


def main():
    for flag, fn in _MODES:
        if os.environ.get(flag) == "1":
            rc = fn()
            # A HELD-TOO-LONG fan-out exits NON-ZERO on purpose. `::error::` alone is an annotation nobody
            # opens; a failed job is what fires GitHub's own workflow-failure notification, which is the
            # alert path that does not depend on an agent or a session. Only the ESCALATED hold does this —
            # a routine hold is a normal, expected outcome and stays green.
            if _MARKET_HOLD_ESCALATED:
                raise SystemExit(2)
            return rc
    return mode_plan()


if __name__ == "__main__":
    main()
