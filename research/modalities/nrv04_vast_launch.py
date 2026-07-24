#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — Vast.ai launcher (prereg §6; runs on CI with VAST_API_KEY + AWS creds).

One Vast instance per (leg, seed) unit → genuinely N-wide parallel (no shared-pool wall). Each instance:
clones the repo, builds the MD env, stages its leg from the co-fold CIF in S3 (nrv04_covalent_assemble),
runs the endpoint-MD driver (nrv04_covalent_md) wrapped by autoteardown, uploads the leg JSON to S3, and
self-destroys. GPU/bid targeting come from ResourceSpec + the tuned VastBackend (RTX-4090-class, >=32 GB host
RAM for the 146k-atom ternary, midpoint spot bid).

PILOT-ONE-LEG-FIRST (standing rule): with PILOT_ONLY=1 we submit ONLY the highest-abort-information unit
(cov_nr4a1 seed 0) to calibrate real GPU-h -> $ before fanning out the other 17. The build_jobspec construction
is pure + unit-tested; submit() needs live creds.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpu_backend import JobSpec, ResourceSpec, _vast_request, get_backend, s3_checkpoint_uri  # noqa: E402
from nrv04_covalent_panel import PANEL, enumerate_units, leg_env, unit_name  # noqa: E402
from nrv04_ligands import LIGANDS  # noqa: E402

REPO = "https://github.com/trimcrae/Rare-cancers"
# co-fold outputs in the reused S3 bucket (nrv04_ternary.py --run --negatives writes one subdir per system).
COFOLD_PREFIX = os.environ.get("NRV04_COFOLD_PREFIX", "nrv04-covalent-cofold")
RESULT_PREFIX = os.environ.get("NRV04_RESULT_PREFIX", "nrv04-covalent-results")

# panel ligand -> the co-fold SYSTEM subdir it comes from (nrv04_ternary.py naming).
_LIGAND_TO_SYSTEM = {"nrv04": "nr4a1", "nrv04_epimer": "neg_inactive", "celastrol": "neg_celastrol"}

# Endpoint-MD host: 4090 24 GB. The solvated complex here is ~50-70k atoms (NOT the 146k-atom FEP hybrid), so
# it does NOT need the FEP's beefy host — over-specifying RAM/vCPU/disk excludes the cheap 4090s and leaves only
# high-demand hosts where the spot floor (min_bid) ~= on-demand. Modest requirements let the bid find a cheap
# 4090 (~$0.10-0.15/hr spot). reliability filter kept (a crash, unlike preemption, we don't tolerate).
# RTX 3090 (24 GB Ampere) is the price/perf sweet spot for these endpoint-MD legs: probe_offers (2026-07-22)
# showed 3090s bidding ~$0.07-0.09/hr vs the cheapest 4090 at $0.144 and the host we first landed at $0.264.
# A 466k-atom system needs <4 GB VRAM so 24 GB is ample, and Ampere/cuda-13 hosts have no PTX-version issue.
# We're not racing (endpoint-MD, checkpointed, parallel), so the 3090's ~0.6x-4090 throughput is fine and it's
# ~70% cheaper than the first host + under GCP L4 spot. _select_cheapest_offer still falls back to any capable
# 24 GB card if 3090s are scarce, always ranked by the true interruptible cost (min_bid).
TERNARY_RES = ResourceSpec(gpu="rtx3090", min_vram_gb=24, vcpus=4, ram_gb=16, disk_gb=60, interruptible=True)

# Boot image. Vast's cheap 4090 hosts have catastrophically slow BOOT-TIME PROVISIONING (Vast apt-installs
# python3/openssh/systemd from archive.ubuntu.com at container start — ~40 min on these hosts, diag-confirmed
# across 4+ hosts; it's Vast's own container init, not our onstart). A Vast-READY base image (ssh + python +
# the provisioning tooling already baked, and commonly cached on Vast hosts) makes that a no-op. Overridable via
# $VAST_IMAGE for A/B testing. The packed conda MD env is still curled from S3 into /opt/mamba/envs/md — we do
# NOT use the image's python, so the image only has to boot fast.
VAST_IMAGE = os.environ.get("VAST_IMAGE") or "docker.io/triskit23/nrv04vast:latest"

# The onstart pipeline. $VARS are exported by _vast_onstart (leg env + forwarded AWS creds + CHECKPOINT_URI +
# ENV_TARBALL_URL). THE BOTTLENECK FIX: instead of a ~25-min `micromamba create` MD solve PER instance (the
# diagnosed stall), each instance extracts a PRE-PACKED conda env (built once on CI via conda-pack, cached in
# S3) from a presigned URL in ~1-2 min. Repo code comes from the public codeload tarball (no git in the base
# image). Everything after that (aws, python) runs out of the extracted env. Phase markers land in S3 for
# `collect`/`diag`.
_PIPELINE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
# curl is already present on the Vast base image (its ssh provisioning installs it) -> only apt if it's genuinely
# missing, and never let a flaky ubuntu mirror abort the boot (diag saw archive.ubuntu.com time out on one host).
command -v curl >/dev/null 2>&1 || { apt-get update -q || true; apt-get install -y -q --no-install-recommends curl ca-certificates || true; }
# --- MD conda env: BAKED into the pre-provisioned image (skip); else fall back to the S3-packed tarball ---
if [ ! -x /opt/mamba/envs/md/bin/python ]; then
  mkdir -p /opt/mamba/envs/md
  curl -Ls "$ENV_TARBALL_URL" | tar xz -C /opt/mamba/envs/md
  /opt/mamba/envs/md/bin/conda-unpack || true
fi
export PATH=/opt/mamba/envs/md/bin:$PATH
PY=/opt/mamba/envs/md/bin/python
AWS=/opt/mamba/envs/md/bin/aws
mark() { echo "$1 $(date -u +%FT%TZ)" | $AWS s3 cp - "$RESULT_S3/phase.txt" 2>/dev/null || true; }
mark env-ready
# --- repo code (public codeload tarball; the base image has no git) ---
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz
cd Rare-cancers-*/research/modalities
mark cloned
mkdir -p /tmp/in /tmp/out /tmp/cofold
export INPUT_DIR=/tmp/in OUTPUT_DIR=/tmp/out CKPT_DIR=/tmp/out
# --- stage this leg from its co-fold system in S3 -> INPUT_DIR/<LEG_ID>/{complex.pdb,ligand.sdf} ---
$AWS s3 cp "$COFOLD_PREFIX_S3" /tmp/cofold/ --recursive --exclude '*' --include '*_model_0.cif'
export COFOLD_CIF=$(find /tmp/cofold -name '*_model_0.cif' | sort | head -1)
test -n "$COFOLD_CIF" || { echo "no co-fold CIF found under $COFOLD_PREFIX_S3"; exit 3; }
$PY -c "import os; from nrv04_covalent_panel import leg_by_id; from nrv04_ligands import LIGANDS; \
from nrv04_covalent_assemble import assemble_leg; lg=leg_by_id(os.environ['LEG_ID']); \
assemble_leg(os.environ['COFOLD_CIF'], lg, LIGANDS[lg.ligand], os.environ['INPUT_DIR'])"
mark staged
# Ligand charging is NAGL (md_settings.CHARGE_METHOD) — deterministic + ~seconds even on the 166-atom recruiter,
# assigned in-process by the driver. No charge cache is needed (am1bcc/sqm — the ~40-min bottleneck — is not used).
# --- endpoint-MD driver, teardown-guarded + per-unit checkpointed ---
mark md-running
$PY autoteardown.py $PY nrv04_covalent_md.py
mark md-done
# --- publish the leg readout JSON ---
$AWS s3 cp /tmp/out/ "$RESULT_S3/" --recursive --exclude '*' --include 'leg_*.json'
mark uploaded
"""

# The pre-packed conda MD env, built once by the build_env CI job and cached here (conda-pack tar.gz).
MDENV_KEY = os.environ.get("MDENV_KEY", "mdenv/nrv04md.tar.gz")


def cofold_prefix_s3(leg, bucket):
    """The S3 PREFIX of the co-fold system that feeds this leg (the onstart globs it for *_model_0.cif, robust to
    Boltz's nested predictions/ layout). nrv04->nr4a1, celastrol->neg_celastrol, epimer->neg_inactive."""
    system = _LIGAND_TO_SYSTEM[leg.ligand]
    return f"s3://{bucket}/{COFOLD_PREFIX}/{system}/"


def stage_test(bucket):
    """De-risk the staging on REAL Boltz output (free CI, no Vast): pull the cov_nr4a1 co-fold CIF from S3 and
    run assemble_leg, verifying complex.pdb + a bond-order-correct ligand.sdf are produced. Proves the assembler
    handles a real multi-chain co-fold CIF before we rent a GPU."""
    import boto3
    from nrv04_covalent_assemble import assemble_leg
    from nrv04_covalent_panel import leg_by_id
    base = os.environ.get("NRV04_COFOLD_PREFIX", COFOLD_PREFIX).rstrip("/")
    s3 = boto3.client("s3")
    leg = leg_by_id("cov_nr4a1")
    system = _LIGAND_TO_SYSTEM[leg.ligand]
    cifs = _s3_list(s3, bucket, f"{base}/{system}/", suffix="_model_0.cif")
    if not cifs:
        raise SystemExit(f"[stage-test] no co-fold CIF under {base}/{system}/")
    key = sorted(cifs)[0]
    os.makedirs("/tmp/cofold", exist_ok=True)
    s3.download_file(bucket, key, "/tmp/cofold/model_0.cif")
    print(f"[stage-test] pulled {key}", flush=True)
    res = assemble_leg("/tmp/cofold/model_0.cif", leg, LIGANDS[leg.ligand], "/tmp/staged")
    import os.path as _p
    cpdb = _p.join(res["out"], "complex.pdb"); lsdf = _p.join(res["out"], "ligand.sdf")
    n_atom = sum(1 for line in open(cpdb) if line.startswith(("ATOM", "HETATM")))
    print(f"[stage-test] OK: {res['ligand_atoms']} ligand atoms, complex.pdb {n_atom} atoms, "
          f"sdf {_p.getsize(lsdf)} bytes", flush=True)
    if n_atom < 500:
        raise SystemExit(f"[stage-test] complex.pdb too small ({n_atom} atoms) — chain surgery failed")
    print("STAGE-TEST PASS — assembler handles the real co-fold CIF.", flush=True)


def _vast_instance_logs(key, iid, tail=400):
    """Fetch a running instance's onstart/container stdout via Vast's request-logs flow (PUT triggers collection
    to a URL, then we poll that URL). Returns the log text or a status note."""
    import time
    import urllib.request
    r = _vast_request("PUT", f"/instances/request_logs/{iid}/", key, body={"tail": str(tail)})
    url = r.get("result_url")
    if not url:
        return f"(no result_url: {r})"
    for _ in range(12):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                txt = resp.read().decode(errors="replace")
            if txt.strip():
                return txt[-6000:]
        except Exception:  # noqa: BLE001 — log not written yet
            pass
        time.sleep(4)
    return "(logs not ready after polling)"


def leg_cost_usd(uptime_s, dph_total):
    """PURE (unit-tested): measured $ a leg cost = wall-clock hours on the rented instance x the ACTUAL bid rate
    paid (dph_total, the interruptible bid we won — NOT dph_base on-demand). Returns None if inputs are missing."""
    try:
        return round((float(uptime_s) / 3600.0) * float(dph_total), 4)
    except (TypeError, ValueError):
        return None


_PRICE_LEDGER_KEY_SUFFIX = "_price_ledger.json"


def _update_price_ledger(insts, done_units, bucket=None, path="nrv04-price-ledger.json"):
    """Maintain a per-leg measured-cost ledger ACROSS collect() polls (the deliverable = a MEASURED price). For
    each instance we see, record uptime x dph_total; once its leg has a result in S3 we FINALIZE that cost (an
    instance is torn down right after, so the last live observation is the billed wall-clock to within one poll).
    The ledger is PERSISTED IN S3 (each collect runs on a fresh ephemeral runner, so a local file would reset every
    poll and only ever see one leg) -> finalized legs accumulate into the true 18-leg panel mean + total.
    Returns a summary: finalized per-leg costs, measured mean $/leg, and the projected full-panel (18-unit) total."""
    import time
    ledger = {}
    ledger_key = f"{RESULT_PREFIX}/{_PRICE_LEDGER_KEY_SUFFIX}"
    s3c = None
    def _unwrap(obj):                                          # the persisted doc is {"ledger":..., "summary":...}
        return obj.get("ledger", obj) if isinstance(obj, dict) else {}
    if bucket:
        try:
            import boto3
            s3c = boto3.client("s3")
            ledger = _unwrap(json.loads(s3c.get_object(Bucket=bucket, Key=ledger_key)["Body"].read().decode()))
        except Exception:  # noqa: BLE001 — first poll (no ledger yet) or transient
            ledger = {}
    if not ledger:                                             # fall back to a local file if S3 unavailable
        try:
            ledger = _unwrap(json.load(open(path)))
        except Exception:  # noqa: BLE001
            ledger = {}
    now = time.time()
    for i in insts:
        label = i.get("label")
        if not label:
            continue
        try:
            up_s = now - float(i.get("start_date") or now)
        except (TypeError, ValueError):
            up_s = 0
        cost = leg_cost_usd(up_s, i.get("dph_total"))
        prev = ledger.get(label, {})
        if prev.get("final"):
            continue                                            # already finalized; don't overwrite
        ledger[label] = {"uptime_s": round(up_s), "dph_total": i.get("dph_total"),
                         "cost_usd": cost, "final": label in done_units}
    finals = {k: v["cost_usd"] for k, v in ledger.items() if v.get("final") and v.get("cost_usd") is not None}
    n_units = len(units_to_run())
    mean = round(sum(finals.values()) / len(finals), 4) if finals else None
    summary = {
        "measured_legs": len(finals),
        "per_leg_usd": finals,
        "measured_mean_usd_per_leg": mean,
        "measured_total_so_far_usd": round(sum(finals.values()), 4) if finals else 0.0,
        "projected_panel_total_usd": round(mean * n_units, 2) if mean is not None else None,
        "panel_units": n_units,
    }
    doc = {"ledger": ledger, "summary": summary}
    json.dump(doc, open(path, "w"), indent=2)
    if s3c is not None:                                        # persist so the next poll accumulates, not resets
        try:
            s3c.put_object(Bucket=bucket, Key=ledger_key, Body=json.dumps(doc).encode())
        except Exception as e:  # noqa: BLE001
            print(f"[price] WARN could not persist ledger to S3: {e}", flush=True)
    return summary


def diag():
    """Print the onstart log + the FULL status record of each running instance — the diagnostic for a stuck/slow
    Vast run. The status fields (status_msg, cur_state, intended_status, inet_down, image pull state) reveal
    whether a long 'loading' is an image pull on a slow host, a scheduler wait, or an error."""
    key = os.environ.get("VAST_API_KEY")
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    print(f"[diag] {len(insts)} instance(s)", flush=True)
    # keys most informative about why an instance is stuck in 'loading'
    status_keys = ["id", "label", "actual_status", "cur_state", "intended_status", "status_msg", "gpu_name",
                   "cuda_max_good", "cuda_version", "driver_version", "inet_down", "reliability2", "start_date",
                   "image_uuid", "image_runtype", "cur_gpu_util", "cpu_util", "disk_util", "dlperf"]
    for i in insts:
        print(f"\n===== instance {i.get('id')} ({i.get('label')}) status={i.get('actual_status')} =====", flush=True)
        print("[diag] status: " + json.dumps({k: i.get(k) for k in status_keys}), flush=True)
        print(_vast_instance_logs(key, i.get("id")), flush=True)


def collect(bucket, autostop=None):
    """Monitor the panel run: list MY Vast instances (confirm running / torn down — no idle bleed) and the leg
    JSONs already in the result prefix. Prints a status board so we can watch the pilot + fan-out from CI.
    AUTO-STOP (default on, AUTOSTOP=0 disables): destroys any instance whose unit already has a leg_*.json in S3
    — the CI-side anti-idle-GPU teardown, so the API key stays on the trusted CI runner, never on the untrusted
    community hosts. Returns (n_up, n_results) so a monitor loop can decide when the fleet has drained."""
    import boto3
    autostop = (os.environ.get("AUTOSTOP", "1") == "1") if autostop is None else autostop
    key = os.environ.get("VAST_API_KEY")
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", []) if key else []
    print(f"[collect] Vast instances up: {len(insts)}", flush=True)
    for i in insts:
        msg = (i.get("status_msg") or "").strip().replace("\n", " ")[-90:]
        print(f"[collect]   id={i.get('id')} status={i.get('actual_status')} label={i.get('label')} "
              f"dph=${i.get('dph_total')}/hr :: {msg}", flush=True)
    s3 = boto3.client("s3")
    phases = {}
    for pk in _s3_list(s3, bucket, f"{RESULT_PREFIX}/", suffix="phase.txt"):
        unit = pk.split("/")[-2]
        phases[unit] = s3.get_object(Bucket=bucket, Key=pk)["Body"].read().decode().strip()
    keys = _s3_list(s3, bucket, f"{RESULT_PREFIX}/", suffix=".json")
    done_units = {k.split("/")[-2] for k in keys if k.rsplit("/", 1)[-1].startswith("leg_")}
    results = []
    for k in keys:                                             # ONLY the completed leg_*.json are 'results';
        if not k.rsplit("/", 1)[-1].startswith("leg_"):        # skip in-progress ckpt_*.ckpt.json (huge per-frame
            continue                                           # arrays) so the collect output stays compact
        body = s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode()
        try:
            results.append(json.loads(body))
        except Exception:  # noqa: BLE001
            results.append({"key": k, "bytes": len(body)})
    # compact in-progress checkpoint summary (proves checkpointing + shows per-leg production progress + the
    # covalent-pull energies, WITHOUT dumping the giant per-frame arrays the checkpoint JSON carries)
    ckpt_progress = {}
    for ck in keys:
        if not ck.rsplit("/", 1)[-1].endswith(".ckpt.json"):
            continue
        unit = ck.split("/")[-2]
        if unit in done_units:                                 # leg already finished -> checkpoint is stale
            continue
        try:
            cj = json.loads(s3.get_object(Bucket=bucket, Key=ck)["Body"].read().decode())
        except Exception:  # noqa: BLE001
            continue
        dfr, frm = cj.get("done_frames"), cj.get("frames")
        wall, tns = cj.get("wall_accum"), cj.get("timed_ns_accum")
        nsday = round(tns / (wall / 86400.0), 1) if (wall and tns) else None
        ckpt_progress[unit] = {"done_frames": dfr, "frames": frm,
                               "pct": round(100.0 * dfr / frm, 1) if (dfr and frm) else None,
                               "ns_per_day": nsday, "pe_pre_min_kj": cj.get("e_pre"),
                               "pe_post_min_kj": cj.get("e_min")}
    stopped = []
    if autostop and key:                                       # CI-side anti-idle teardown (key stays on CI)
        import time
        now = time.time()
        max_leg_s = int(os.environ.get("MAX_LEG_MIN", "240")) * 60   # backstop: a real leg finishes well under this;
        # (240 min: a 6 ns leg at the MEASURED ~44-61 ns/day = ~2.3-2.6 h + ~20 min load ~= 155 min, so 240 leaves
        #  margin for a spot-wait; the earlier 100 was PREMATURELY killing healthy legs — checkpoints made them
        #  recoverable but a re-dispatch was needed. Do NOT drop this below ~180.)
        # A label with >1 live instance is a DUPLICATE (relaunching a leg whose 'exited' container lingered under
        # the mock teardown, then Vast re-scheduled the old one) -> two instances double-compute the same leg and
        # clobber its S3 checkpoint. Keep ONE per label (a 'running' one, else the newest) and reap the rest.
        _by_label = {}
        for i in insts:
            _by_label.setdefault(i.get("label"), []).append(i)
        _keep_ids = set()
        for _lab, _grp in _by_label.items():
            _best = sorted(_grp, key=lambda x: ((x.get("actual_status") != "running"), -(x.get("start_date") or 0)))[0]
            _keep_ids.add(id(_best))
        _terminal = ("exited", "offline", "stopped")           # dead containers (mock teardown never destroyed them)
        _stop_throttle = 0
        for i in insts:                                             # a crashed/idle instance (driver failed at build,
            label = i.get("label")                                  # teardown fell through) would otherwise bleed
            try:
                up_s = now - float(i.get("start_date") or now)
            except (TypeError, ValueError):
                up_s = 0
            done = label in done_units
            over_age = up_s > max_leg_s
            terminal = (i.get("actual_status") or "") in _terminal
            extra = id(i) not in _keep_ids                         # a duplicate (not the kept instance for its label)
            if done or over_age or terminal or extra:
                if _stop_throttle:
                    time.sleep(0.5)                                # stay under Vast's ~3 req/s DELETE limit
                _stop_throttle += 1
                try:
                    _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
                    stopped.append(i.get("id"))
                    why = ("result-in-S3" if done else "terminal-state" if terminal else "duplicate-instance"
                           if extra else f"exceeded {max_leg_s // 60}min (idle/crashed backstop)")
                    print(f"[collect] auto-stopped {i.get('id')} ({label}) — {why}", flush=True)
                except Exception as e:  # noqa: BLE001
                    print(f"[collect] WARN auto-stop {i.get('id')} failed: {e}", flush=True)
    price = _update_price_ledger(insts, done_units, bucket=bucket)   # MEASURED per-leg $ ledger (S3-persisted)
    status = {
        "vast_instances": [{"id": i.get("id"), "status": i.get("actual_status"), "label": i.get("label"),
                            "is_bid": i.get("is_bid"), "dph_total": i.get("dph_total"),
                            "dph_base": i.get("dph_base"), "min_bid": i.get("min_bid"),
                            "gpu_name": i.get("gpu_name"), "start_date": i.get("start_date"),
                            "duration": i.get("duration")} for i in insts],
        "phases": phases, "auto_stopped": stopped, "ckpt_progress": ckpt_progress,
        "n_results": len(done_units), "results": results, "price": price,
    }
    json.dump(status, open("nrv04-collect-status.json", "w"), indent=2)
    print("[collect] " + json.dumps(status, indent=2), flush=True)
    if price.get("measured_mean_usd_per_leg") is not None:
        print(f"[price] MEASURED ${price['measured_mean_usd_per_leg']}/leg over {price['measured_legs']} leg(s) "
              f"-> projected panel ({price['panel_units']} units) ≈ ${price['projected_panel_total_usd']}", flush=True)
    return len(insts), len(done_units)


def monitor(bucket):
    """One CI job babysits the whole fan-out: loop collect()+auto-stop every MONITOR_EVERY_S until every unit has
    a result (and its instance is torn down) or MONITOR_MAX_S elapses. Bounded so it can never run forever; the
    stop-hook's own timeout is the outer guard. Pure-ish (sleeps + collect)."""
    import time
    n_units = len(units_to_run())
    every = int(os.environ.get("MONITOR_EVERY_S", "60"))
    max_s = int(os.environ.get("MONITOR_MAX_S", "3000"))       # < the job's timeout-minutes
    waited = 0
    while True:
        n_up, n_done = collect(bucket)
        print(f"[monitor] {n_done}/{n_units} results, {n_up} instance(s) up, {waited}s elapsed", flush=True)
        if n_done >= n_units and n_up == 0:
            print("[monitor] fleet drained — all results in, no instances up.", flush=True)
            return
        if waited >= max_s:
            print(f"[monitor] max wait {max_s}s reached ({n_done}/{n_units} done, {n_up} up) — exiting; re-dispatch to continue.", flush=True)
            return
        time.sleep(every); waited += every


def stop_all():
    """Destroy every one of MY Vast instances (stop the bleed). Prints each id it tears down."""
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("[stop] VAST_API_KEY not set")
    import time
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    print(f"[stop] {len(insts)} instance(s) to destroy", flush=True)
    failed = []
    for n, i in enumerate(insts):
        iid = i.get("id")
        if n:
            time.sleep(0.5)                                    # stay under Vast's ~3 req/s DELETE limit (the 429
        try:                                                   # retry in _vast_request is the backstop for this)
            _vast_request("DELETE", f"/instances/{iid}/", key)
            print(f"[stop] destroyed {iid} ({i.get('label')})", flush=True)
        except Exception as e:  # noqa: BLE001 — don't let one failed DELETE abort the whole sweep
            failed.append(iid); print(f"[stop] WARN destroy {iid} failed: {e}", flush=True)
    print(f"[stop] done ({len(insts) - len(failed)}/{len(insts)} destroyed"
          + (f", {len(failed)} FAILED: {failed}" if failed else "") + ")", flush=True)


def build_jobspec(leg, seed, mode, branch, bucket, env_tarball_url=None):
    """PURE: the JobSpec for one (leg, seed) unit. No I/O -> unit-tested. `env_tarball_url` (a presigned S3 GET
    for the pre-packed conda env) is injected when submitting; the pure unit tests omit it."""
    name = unit_name(leg, seed)
    env = leg_env(leg, seed, mode=mode)
    env.update({
        "GIT_BRANCH": branch,
        "COFOLD_PREFIX_S3": cofold_prefix_s3(leg, bucket),
        "RESULT_S3": f"s3://{bucket}/{RESULT_PREFIX}/{name}",
    })
    if env_tarball_url:
        env["ENV_TARBALL_URL"] = env_tarball_url
    pipeline = _PIPELINE.replace("{repo}", REPO)      # not .format(): the bash has literal {a,b} brace-expansion
    return JobSpec(
        name=name,
        command=["bash", "-lc", pipeline],
        image=VAST_IMAGE,
        checkpoint_uri=s3_checkpoint_uri(name, bucket=bucket),
        resume=True,
        resources=TERNARY_RES,
        max_runtime_s=int(os.environ.get("MAX_RUNTIME_S", "43200")),
        env=env,
    )


def presign_env_tarball(bucket, expires_s=None):
    """Return a presigned S3 GET URL for the pre-packed conda MD env (so instances curl it without awscli, which
    lives inside the env). Fails loudly if the env hasn't been built yet (run the build_env CI job first)."""
    import boto3
    from botocore.exceptions import ClientError
    s3 = boto3.client("s3")
    try:
        head = s3.head_object(Bucket=bucket, Key=MDENV_KEY)
    except ClientError as e:
        raise SystemExit(f"[launch] pre-packed MD env s3://{bucket}/{MDENV_KEY} not found ({e}); "
                         f"run the build_env task first (task=nrv04_vast_launch, mode not needed — see workflow).")
    size_mb = head["ContentLength"] / 1e6
    ttl = expires_s or (int(os.environ.get("MAX_RUNTIME_S", "43200")) + 3600)
    url = s3.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": MDENV_KEY}, ExpiresIn=ttl)
    print(f"[launch] pre-packed MD env: s3://{bucket}/{MDENV_KEY} ({size_mb:.0f} MB), presigned {ttl}s", flush=True)
    return url


def units_to_run():
    """Pilot-one-leg-first: PILOT_ONLY=1 -> just cov_nr4a1 seed 0 (highest abort info: it's the primary covalent
    ternary model + the R4 sensitivity numerator). Else the full 18-unit fan-out."""
    if os.environ.get("PILOT_ONLY", "1") == "1":
        pilot = next(lg for lg in PANEL if lg.leg_id == "cov_nr4a1")
        return [(pilot, int(os.environ.get("PILOT_SEED", "0")))]   # PILOT_SEED distinguishes parallel bench runs
    return enumerate_units()


def _s3_list(s3, bucket, prefix, suffix=None, limit=None):
    keys, tok = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            if suffix is None or o["Key"].endswith(suffix):
                keys.append(o["Key"])
        if limit and len(keys) >= limit:
            return keys[:limit]
        if not r.get("IsTruncated"):
            return keys
        tok = r["NextContinuationToken"]


def discover_cofold(bucket, base=None):
    """List the reused co-fold prefix and report which *_model_0.cif exist (reuse ValB's structures, no regen).
    Also dumps the RAW prefix layout so we can see the actual subdir names if they differ from expected."""
    import boto3
    base = (base or os.environ.get("NRV04_COFOLD_PREFIX", COFOLD_PREFIX)).rstrip("/")
    s3 = boto3.client("s3")
    all_cifs = _s3_list(s3, bucket, base + "/", suffix="_model_0.cif")
    sample = _s3_list(s3, bucket, base + "/", limit=25)
    found = {}
    for lig, system in _LIGAND_TO_SYSTEM.items():
        keys = [k for k in all_cifs if f"/{system}/" in k]
        found[system] = sorted(keys)
    out = {"bucket": bucket, "base": base, "total_model0_cifs": len(all_cifs),
           "per_system": found, "raw_sample_keys": sample, "all_cif_keys": all_cifs[:40]}
    json.dump(out, open("nrv04-cofold-discovery.json", "w"), indent=2)
    print("[discover] " + json.dumps(out, indent=2), flush=True)
    return out


def probe_offers():
    """Evidence for 'can we get cheaper?': list the cheapest eligible Vast offers under several filter variants so
    we can see the true interruptible price floor and which constraint (reliability / cuda_max_good / GPU model) is
    binding. Read-only — no rent. Ranks by min_bid (the interruptible cost) and shows what our bid would be."""
    import copy
    from gpu_backend import (_vast_request, _vast_offer_query, _vast_bid_price, _vast_gpu_ram_gb)
    key = os.environ.get("VAST_API_KEY")
    res = TERNARY_RES

    def _mb(o):
        try:
            return float(o.get("min_bid") if o.get("min_bid") is not None else 1e9)
        except (TypeError, ValueError):
            return 1e9

    def run(q, label, topn=8, only_4090=False):
        offers = _vast_request("GET", "/search/asks/", key, params={"q": json.dumps(q)}).get("offers", [])
        offers = [o for o in offers if int(o.get("num_gpus", 1) or 1) == 1]
        if only_4090:
            offers = [o for o in offers if "4090" in str(o.get("gpu_name", ""))]
        offers.sort(key=_mb)
        print(f"\n=== {label}: {len(offers)} single-GPU offers ===", flush=True)
        for o in offers[:topn]:
            try:
                rel = float(o.get("reliability2") or 0)
            except (TypeError, ValueError):
                rel = 0.0
            print(f"  {str(o.get('gpu_name'))[:16]:16} min_bid=${_mb(o):.3f} base=${float(o.get('dph_base') or 0):.3f} "
                  f"OURBID=${_vast_bid_price(o)} cuda_max={o.get('cuda_max_good')} rel={rel:.2f} "
                  f"vram={_vast_gpu_ram_gb(o):.0f}GB dc={o.get('geolocation')}", flush=True)
        if offers:
            ch = offers[0]
            print(f"  -> cheapest here: {ch.get('gpu_name')} OURBID=${_vast_bid_price(ch)}/hr", flush=True)

    full = _vast_offer_query(res)
    run(full, "FULL query (verified, rel>=%.2f, cuda>=%.1f, vram>=%dGB)" % (res.min_reliability, res.min_cuda, res.min_vram_gb - 1))
    run(full, "FULL query, RTX 4090 only", only_4090=True)
    no_rel = copy.deepcopy(full); no_rel.pop("reliability2", None)
    run(no_rel, "drop reliability filter (see if cheap hosts are low-reliability)")
    no_cuda = copy.deepcopy(full); no_cuda.pop("cuda_max_good", None)
    run(no_cuda, "drop cuda_max_good filter (see the PTX-risky cheap hosts we exclude)")
    relaxed = copy.deepcopy(full); relaxed.pop("reliability2", None); relaxed.pop("cuda_max_good", None)
    run(relaxed, "drop BOTH reliability + cuda (absolute floor for 24GB single-GPU)")


# ---- throughput bench mode: run gpu_md_bench on a chosen Vast card to PRICE $/ns (3090-vs-4090 decision) ----
# Reuses the proven Vast submit + self-destroy EXIT trap (VastBackend._vast_onstart): each bench instance tears
# ITSELF down on exit by its own unique label, so it is safe alongside the live covalent panel (no stop_all).
# gpu_md_bench builds a self-contained TIP3P water box sized by BENCH_EDGE_NM (7.1nm≈36k atoms≈an RBFE complex
# leg; larger edges bracket the ternary ~100k and covalent ~466k systems) and prints one ns_per_day line.
_BENCH_PREFIX = os.environ.get("VAST_BENCH_PREFIX", "vast-bench-results")

_BENCH_PIPELINE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
command -v curl >/dev/null 2>&1 || { apt-get update -q || true; apt-get install -y -q --no-install-recommends curl ca-certificates || true; }
if [ ! -x /opt/mamba/envs/md/bin/python ]; then
  mkdir -p /opt/mamba/envs/md
  curl -Ls "$ENV_TARBALL_URL" | tar xz -C /opt/mamba/envs/md
  /opt/mamba/envs/md/bin/conda-unpack || true
fi
export PATH=/opt/mamba/envs/md/bin:$PATH
PY=/opt/mamba/envs/md/bin/python
AWS=/opt/mamba/envs/md/bin/aws
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz
cd Rare-cancers-*/research/modalities
export OPENMM_REQUIRE_CUDA=1
$PY autoteardown.py $PY gpu_md_bench.py 2>&1 | tee /tmp/bench.out || true
grep BENCH_RESULT /tmp/bench.out | tail -1 > /tmp/bench.line || true
$PY - <<'PYEOF'
import json, os
line = open("/tmp/bench.line").read().strip()
d = {}
for kv in line.split():
    if "=" in kv:
        k, v = kv.split("=", 1)
        d[k] = v
d["_raw"] = line
d["gpu"] = os.environ.get("VAST_GPU_MODEL", "")
d["edge_nm"] = os.environ.get("BENCH_EDGE_NM", "")
json.dump(d, open("/tmp/bench.json", "w"), indent=2)
PYEOF
$AWS s3 cp /tmp/bench.json "$RESULT_S3/bench.json" || true
$AWS s3 cp /tmp/bench.out "$RESULT_S3/bench.out" || true
"""


def build_bench_jobspec(tag, branch, bucket, env_tarball_url=None):
    """PURE: JobSpec for one throughput bench (one card × one system size). No staging, no checkpoint/resume —
    gpu_md_bench is seconds of compute; the instance self-destroys on exit."""
    gpu = os.environ.get("VAST_GPU_MODEL") or "rtx4090"
    env = {
        "GIT_BRANCH": branch,
        "RESULT_S3": f"s3://{bucket}/{_BENCH_PREFIX}/{tag}",
        "BENCH_EDGE_NM": os.environ.get("BENCH_EDGE_NM", "7.1"),
        "BENCH_STEPS": os.environ.get("BENCH_STEPS", "4000"),
        "BENCH_WARMUP": os.environ.get("BENCH_WARMUP", "1000"),
        "BENCH_TAG": tag,
        "VAST_GPU_MODEL": gpu,
    }
    if env_tarball_url:
        env["ENV_TARBALL_URL"] = env_tarball_url
    pipeline = _BENCH_PIPELINE.replace("{repo}", REPO)
    return JobSpec(
        name=tag,
        command=["bash", "-lc", pipeline],
        image=VAST_IMAGE,
        checkpoint_uri=f"s3://{bucket}/{_BENCH_PREFIX}/{tag}/ckpt",
        resume=False,
        resources=ResourceSpec(gpu=gpu, min_vram_gb=24, vcpus=4, ram_gb=16, disk_gb=40, interruptible=True),
        max_runtime_s=int(os.environ.get("BENCH_MAX_RUNTIME_S", "2400")),
        env=env,
    )


def bench(bucket):
    """Submit throughput bench leg(s) to Vast. BENCH_GRID (comma-sep 'gpu:edge_nm' pairs, e.g.
    'rtx4090:9.5,rtx3090:9.5,rtx4090:16.5') submits the whole grid in ONE dispatch (avoids the workflow's
    concurrency group cancelling rapid single dispatches). Else a single (VAST_GPU_MODEL, BENCH_EDGE_NM) leg.
    Each leg self-destroys on exit; idempotent enough for a bench (a stale same-tag bench.json is overwritten)."""
    branch = os.environ.get("GIT_BRANCH", "claude/next-expansion-priorities-t64njy")
    dry = os.environ.get("DRY_RUN", "0") == "1"
    grid_env = (os.environ.get("BENCH_GRID") or "").strip()
    if grid_env:
        grid = []
        for pair in grid_env.split(","):
            pair = pair.strip()
            if not pair:
                continue
            gpu, _, edge = pair.partition(":")
            grid.append((gpu.strip() or "rtx4090", edge.strip() or "7.1"))
    else:
        grid = [(os.environ.get("VAST_GPU_MODEL") or "rtx4090", os.environ.get("BENCH_EDGE_NM", "7.1"))]
    be = get_backend("vast")
    env_url = None if dry else presign_env_tarball(bucket)
    handles = []
    for gpu, edge_nm in grid:
        tag = f"bench-{gpu}-{edge_nm}nm".replace(".", "p")
        # per-leg overrides consumed by build_bench_jobspec via env
        os.environ["VAST_GPU_MODEL"] = gpu
        os.environ["BENCH_EDGE_NM"] = edge_nm
        spec = build_bench_jobspec(tag, branch, bucket, env_tarball_url=env_url)
        if dry:
            print(f"[bench-dry] {spec.name}: gpu={gpu} edge={edge_nm}nm steps={spec.env['BENCH_STEPS']} "
                  f"-> {spec.env['RESULT_S3']}", flush=True)
            continue
        h = be.submit(spec)
        print(f"[bench-submit] {spec.name} -> instance {h.job_id} gpu={gpu} edge={edge_nm}nm "
              f"dph≈${h.extra.get('dph')}/hr", flush=True)
        handles.append({"unit": spec.name, "gpu": gpu, "edge_nm": edge_nm, "instance": h.job_id,
                        "dph": h.extra.get("dph")})
    if handles:
        json.dump(handles, open("nrv04-vast-bench-handles.json", "w"), indent=2)
    return 0


def bench_collect(bucket):
    """Read every vast-bench-results/*/bench.json + list live bench-* instances, and print a $/ns table
    (ns_per_day is stamped by gpu_md_bench; combine with the live per-card $/hr from probe_offers for $/ns)."""
    import boto3
    s3 = boto3.client("s3")
    key = os.environ.get("VAST_API_KEY")
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", []) if key else []
    bench_up = [i for i in insts if (i.get("label") or "").startswith("bench-")]
    print(f"[bench-collect] live bench-* instances: {len(bench_up)} "
          f"(each self-destroys on exit; covalent panel untouched)", flush=True)
    for i in bench_up:
        print(f"[bench-collect]   id={i.get('id')} status={i.get('actual_status')} label={i.get('label')} "
              f"dph=${i.get('dph_total')}/hr", flush=True)
    rows = []
    done_tags = set()
    for k in _s3_list(s3, bucket, f"{_BENCH_PREFIX}/", suffix="bench.json"):
        try:
            d = json.loads(s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode())
        except Exception:  # noqa: BLE001
            continue
        rows.append(d)
        done_tags.add(d.get("tag") or k.split("/")[-2])
    print(f"[bench-collect] {len(rows)} bench result(s):", flush=True)
    for d in sorted(rows, key=lambda r: (str(r.get("gpu")), str(r.get("edge_nm")))):
        print(f"  gpu={d.get('gpu')} edge={d.get('edge_nm')}nm atoms={d.get('atoms')} "
              f"device={d.get('device')} platform={d.get('platform')} "
              f"ns_per_day={d.get('ns_per_day')} status={d.get('status')}", flush=True)
        if d.get("status") != "OK":                    # root-cause: the full BENCH_RESULT line (incl err=...)
            print(f"    raw: {d.get('_raw')}", flush=True)
    # TARGETED anti-idle teardown, scoped to the bench-* label namespace (covalent panel NEVER touched, no
    # stop_all). Destroy ONLY: (a) terminal instances (a finished bench self-exits -> exited/stopped), or (b) an
    # over-age instance (stuck/crashed backstop). Do NOT key off "has a bench.json" — a STALE result from a prior
    # run of the same tag would otherwise kill a freshly-LOADING re-dispatch mid-boot (observed 2026-07-23).
    if os.environ.get("BENCH_NO_STOP") != "1" and key:
        import time
        now = time.time()
        max_age = int(os.environ.get("BENCH_MAX_AGE_MIN", "40")) * 60
        _terminal = ("exited", "offline", "stopped")
        for i in bench_up:
            lab = i.get("label") or ""
            try:
                age = now - float(i.get("start_date") or now)
            except (TypeError, ValueError):
                age = 0
            terminal = (i.get("actual_status") or "") in _terminal
            if terminal or age > max_age:
                try:
                    _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
                    print(f"[bench-collect] destroyed {i.get('id')} ({lab}) — "
                          f"{'terminal' if terminal else f'over-age {int(age//60)}min'}", flush=True)
                except Exception as e:  # noqa: BLE001
                    print(f"[bench-collect] WARN destroy {i.get('id')} failed: {e}", flush=True)
    return 0


# ---- FIRM mode: run ONE real RBFE edge + ONE real ternary edge on the Vast RTX 4090 (OpenFE nr4a3fep image) to
# replace the ~1.7x alchemical-overhead ASSUMPTION with a MEASURED per-edge ns/day + confirm the pipelines launch
# on Vast. Both self-stage (RBFE: valA_bench_stage.py public TYK2 edge; ternary: ternary_pdb_stage.py from 8G1Q),
# so no S3 input dependency. The image bakes the rbfe env (openfe+ambertools+lomap/kartograf+gemmi+pdbfixer+awscli).
FEP_IMAGE = os.environ.get("FEP_IMAGE") or "docker.io/triskit23/nr4a3fep:latest"
_FIRM_PREFIX = os.environ.get("VAST_FIRM_PREFIX", "vast-firm-results")

_FIRM_PREAMBLE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
command -v curl >/dev/null 2>&1 || { apt-get update -q||true; apt-get install -y -q --no-install-recommends curl ca-certificates||true; }
export PATH=/opt/mamba/envs/rbfe/bin:$PATH
# conda-pack relocation breaks OpenMM's compiled-in plugin dir -> OpenFE's internal getPlatformByName("CUDA")
# fails ("no registered Platform called CUDA"). Point OPENMM_PLUGIN_DIR at this env's plugins so auto-load works
# for BOTH our driver AND OpenFE's internal calls (verified root cause on the first firm run, 2026-07-23).
export OPENMM_PLUGIN_DIR=/opt/mamba/envs/rbfe/lib/plugins
# The rbfe conda env has no CA bundle for Python SSL, so ternary_pdb_stage.py's RCSB fetch fails with
# CERTIFICATE_VERIFY_FAILED -> empty ligands.sdf (root-caused on the first firm run, 2026-07-23). Point SSL at
# the system CA bundle the Dockerfile's apt `ca-certificates` installs.
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
PY=/opt/mamba/envs/rbfe/bin/python
AWS=/opt/mamba/envs/rbfe/bin/aws
command -v "$AWS" >/dev/null 2>&1 || AWS="$PY -m awscli"
$PY -c "import openfe,openmm;print('[firm] openfe',openfe.__version__,'plats',[openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())])" || true
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz
cd Rare-cancers-*/research/modalities
export IN=/tmp/fin OUT=/tmp/fout; mkdir -p "$IN" "$OUT"
"""

_FIRM_RBFE_BODY = r"""
mkdir -p "$IN/ligand" "$IN/receptor"
echo "[firm] staging public TYK2 edge (valA_bench_stage.py)"
VALA_NO_UPLOAD=1 VALA_WORKDIR=/tmp/valA $PY valA_bench_stage.py 2>&1 | tail -12 || true
cp /tmp/valA/staged/docked_nr4a3.sdf "$IN/ligand/" 2>/dev/null || echo "[firm] no docked sdf"
cp /tmp/valA/staged/nr4a3-opened.pdb "$IN/receptor/" 2>/dev/null || echo "[firm] no receptor pdb"
cp /tmp/valA/staged/valA_manifest.json "$IN/" 2>/dev/null || true
export T0=$(date +%s)
env MODE=splittest RBFE_TINY=0 N_WINDOWS="${N_WINDOWS:-12}" N_ITER="${N_ITER:-150}" OPENMM_REQUIRE_CUDA=1 \
    RECEPTOR=nr4a3 LEG=complex LIGAND_A=tyk2_ejm_31 LIGAND_B=tyk2_ejm_42 \
    INPUT_DIR="$IN" OUTPUT_DIR="$OUT" CKPT_DIR="$OUT" $PY nr4a3_rbfe.py 2>&1 | tee /tmp/firm.log || true
export T1=$(date +%s)
"""

_FIRM_TERNARY_BODY = r"""
export T0=$(date +%s)
{
  echo "[firm] staging ternary leg from 8G1Q (ternary_pdb_stage.py)"
  $PY ternary_pdb_stage.py --leg-id "${LEG_ID:-calib_hi_to_lo__ternary_vhl}" --template-pdb 8G1Q --out "$IN" 2>&1 \
    || echo "[firm] STAGING FAILED rc=$?"
  echo "[firm] staged tree (name + bytes):"
  find "$IN" -type f \( -name '*.sdf' -o -name '*.pdb' -o -name '*.json' \) -printf '  %s B  %p\n' 2>/dev/null || true
  echo "[firm] --- ternary MD ---"
  env MODE=run LEG_ID="${LEG_ID:-calib_hi_to_lo__ternary_vhl}" SEED=0 DIRECTION=fwd N_WINDOWS="${N_WINDOWS:-16}" \
      CHARGE_METHOD=nagl RBFE_TIMESTEP_FS=2.0 RBFE_CONSTRAIN_LIGAND_CH=0 N_ITER="${N_ITER:-120}" OPENMM_REQUIRE_CUDA=1 \
      INPUT_DIR="$IN" OUTPUT_DIR="$OUT" CKPT_DIR="$OUT" $PY nr4a3_ternary_fep.py 2>&1 || true
} | tee /tmp/firm.log
export T1=$(date +%s)
"""

_FIRM_SUMMARY = r"""
export FIRM_KIND N_WINDOWS N_ITER
$PY - <<'PYEOF'
import json, os, glob
out = os.environ["OUT"]; kind = os.environ.get("FIRM_KIND", "?")
js = sorted(glob.glob(os.path.join(out, "**", "*.json"), recursive=True))
nsd = dg = leg = src = None
for p in js:
    try:
        d = json.load(open(p))
    except Exception:
        continue
    if not isinstance(d, dict):
        continue
    td = d.get("timing_diagnostics") or {}
    cand = td.get("ns_per_day") or d.get("ns_per_day")
    if cand:
        nsd, src, leg = cand, os.path.basename(p), d.get("leg")
        dg = d.get("dg_morph_kcal") or d.get("ddg_coop_kcal") or d.get("dg_kcal")
try:
    wall = int(os.environ.get("T1", "0")) - int(os.environ.get("T0", "0"))
except ValueError:
    wall = None
r = {"kind": kind, "ns_per_day": nsd, "leg": leg, "dg": dg, "result_json": src,
     "n_windows": os.environ.get("N_WINDOWS"), "n_iter": os.environ.get("N_ITER"),
     "wall_s": wall, "n_json": len(js), "status": "OK" if nsd is not None else "NORESULT"}
json.dump(r, open("/tmp/firm.json", "w"), indent=2)
print("FIRM_RESULT", json.dumps(r))
PYEOF
$AWS s3 cp /tmp/firm.json "$RESULT_S3/firm.json" || true
$AWS s3 cp /tmp/firm.log "$RESULT_S3/firm.log" || true
"""


def build_firm_jobspec(kind, branch, bucket):
    """JobSpec for one real firming leg on the OpenFE nr4a3fep image (RTX 4090). kind = rbfe | ternary."""
    body = _FIRM_RBFE_BODY if kind == "rbfe" else _FIRM_TERNARY_BODY
    pipeline = (_FIRM_PREAMBLE + body + _FIRM_SUMMARY).replace("{repo}", REPO)
    tag = f"firm-{kind}-rtx4090"
    env = {
        "GIT_BRANCH": branch,
        "RESULT_S3": f"s3://{bucket}/{_FIRM_PREFIX}/{tag}",
        "FIRM_KIND": kind,
        "N_WINDOWS": os.environ.get("N_WINDOWS") or ("12" if kind == "rbfe" else "16"),
        # short production is enough for a stable ns/day (throughput is length-independent) and finishes fast.
        "N_ITER": os.environ.get("N_ITER") or ("60" if kind == "rbfe" else "60"),
        "LEG_ID": os.environ.get("LEG_ID", "calib_hi_to_lo__ternary_vhl"),
    }
    return JobSpec(
        name=tag,
        command=["bash", "-lc", pipeline],
        image=FEP_IMAGE,
        checkpoint_uri=f"s3://{bucket}/{_FIRM_PREFIX}/{tag}/ckpt",
        resume=False,
        resources=ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=32, disk_gb=60, interruptible=True),
        # a real 12-window HREX leg runs ~2h+ on one GPU; the old 90-min watchdog reaped it mid-run. 4h ceiling.
        max_runtime_s=int(os.environ.get("FIRM_MAX_RUNTIME_S", "86400")),
        env=env,
    )


def firm(bucket):
    """Launch one or more real firming legs (FIRM_KIND = rbfe | ternary | 'rbfe,ternary') on Vast RTX 4090."""
    branch = os.environ.get("GIT_BRANCH", "claude/next-expansion-priorities-t64njy")
    kinds = [k.strip() for k in (os.environ.get("FIRM_KIND") or "rbfe").split(",") if k.strip()]
    dry = os.environ.get("DRY_RUN", "0") == "1"
    be = get_backend("vast")
    handles = []
    for k in kinds:
        spec = build_firm_jobspec(k, branch, bucket)
        if dry:
            print(f"[firm-dry] {spec.name}: image={spec.image} gpu={spec.resources.gpu} "
                  f"N_WINDOWS={spec.env['N_WINDOWS']} N_ITER={spec.env['N_ITER']} -> {spec.env['RESULT_S3']}", flush=True)
            continue
        h = be.submit(spec)
        print(f"[firm-submit] {spec.name} -> instance {h.job_id} gpu=rtx4090 dph≈${h.extra.get('dph')}/hr", flush=True)
        handles.append({"unit": spec.name, "kind": k, "instance": h.job_id, "dph": h.extra.get("dph")})
    if handles:
        json.dump(handles, open("nrv04-vast-firm-handles.json", "w"), indent=2)
    return 0


def firm_collect(bucket):
    """Read vast-firm-results/*/firm.json (measured ns_per_day per real edge) + reap terminal/over-age firm-*
    instances (scoped to firm-* labels; covalent panel untouched)."""
    import boto3
    s3 = boto3.client("s3")
    key = os.environ.get("VAST_API_KEY")
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", []) if key else []
    firm_up = [i for i in insts if (i.get("label") or "").startswith("firm-")]
    print(f"[firm-collect] live firm-* instances: {len(firm_up)}", flush=True)
    for i in firm_up:
        print(f"[firm-collect]   id={i.get('id')} status={i.get('actual_status')} label={i.get('label')} "
              f"dph=${i.get('dph_total')}/hr", flush=True)
    for k in _s3_list(s3, bucket, f"{_FIRM_PREFIX}/", suffix="firm.json"):
        try:
            d = json.loads(s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode())
        except Exception:  # noqa: BLE001
            continue
        print(f"  kind={d.get('kind')} ns_per_day={d.get('ns_per_day')} n_windows={d.get('n_windows')} "
              f"n_iter={d.get('n_iter')} wall_s={d.get('wall_s')} dg={d.get('dg')} status={d.get('status')} "
              f"(from {d.get('result_json')}, {d.get('n_json')} json)", flush=True)
        if d.get("status") != "OK":                          # root-cause: dump the run log tail from S3
            logkey = k.rsplit("/", 1)[0] + "/firm.log"
            try:
                log = s3.get_object(Bucket=bucket, Key=logkey)["Body"].read().decode(errors="replace")
                tail = "\n".join(log.splitlines()[-60:])
                print(f"    --- firm.log tail ({logkey}) ---\n{tail}\n    --- end ---", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"    (no firm.log: {e})", flush=True)
    if os.environ.get("BENCH_NO_STOP") != "1" and key:
        import time
        now = time.time()
        max_age = int(os.environ.get("FIRM_MAX_AGE_MIN", "260")) * 60   # > a real ~2h HREX leg + boot; don't reap mid-run
        _terminal = ("exited", "offline", "stopped")
        # keep the NEWEST instance per label; older same-label instances are stale duplicates (an errored run that
        # lingered while a fresh re-dispatch started) -> reap. Also reap terminal + over-age. FIRM_STOP=1 reaps ALL
        # firm-* (explicit cleanup). Never touches non-firm labels.
        force_all = os.environ.get("FIRM_STOP") == "1"
        newest = {}
        for i in firm_up:
            lab = i.get("label")
            if lab not in newest or (i.get("start_date") or 0) > (newest[lab].get("start_date") or 0):
                newest[lab] = i
        keep = {id(v) for v in newest.values()} if not force_all else set()
        for i in firm_up:
            try:
                age = now - float(i.get("start_date") or now)
            except (TypeError, ValueError):
                age = 0
            dup = id(i) not in keep
            if force_all or dup or (i.get("actual_status") or "") in _terminal or age > max_age:
                try:
                    _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
                    why = "force" if force_all else ("duplicate" if dup else "terminal/over-age")
                    print(f"[firm-collect] destroyed {i.get('id')} ({i.get('label')}) — {why}", flush=True)
                except Exception as e:  # noqa: BLE001
                    print(f"[firm-collect] WARN destroy {i.get('id')} failed: {e}", flush=True)
    return 0


def main():
    bucket = os.environ.get("VAST_CKPT_BUCKET")
    if not bucket:
        raise SystemExit("[nrv04-launch] set VAST_CKPT_BUCKET (the reused S3 bucket)")
    if os.environ.get("BENCH") == "1":
        return bench(bucket)
    if os.environ.get("BENCH_COLLECT") == "1":
        return bench_collect(bucket)
    if os.environ.get("FIRM") == "1":
        return firm(bucket)
    if os.environ.get("FIRM_COLLECT") == "1":
        return firm_collect(bucket)
    if os.environ.get("DISCOVER") == "1":
        discover_cofold(bucket)
        return 0
    if os.environ.get("STAGE_TEST") == "1":
        stage_test(bucket)
        return 0
    if os.environ.get("COLLECT") == "1":
        collect(bucket)
        return 0
    if os.environ.get("MONITOR") == "1":
        monitor(bucket)
        return 0
    if os.environ.get("STOP_ALL") == "1":
        stop_all()
        return 0
    if os.environ.get("DIAG") == "1":
        diag()
        return 0
    if os.environ.get("PROBE_OFFERS") == "1":
        probe_offers()
        return 0
    branch = os.environ.get("GIT_BRANCH", "claude/alternative-gpu-providers-wx4r2c")
    mode = os.environ.get("MODE", "run")
    dry = os.environ.get("DRY_RUN", "0") == "1"
    gpu_override = os.environ.get("VAST_GPU_MODEL")               # e.g. rtx8000 for the $/ns bench (default: rtx3090)
    if gpu_override:
        TERNARY_RES.gpu = gpu_override
        print(f"[nrv04-launch] GPU override -> {gpu_override}", flush=True)

    be = get_backend("vast")
    units = units_to_run()
    # IDEMPOTENT launch: skip units that already have a result in S3 (done) or a live Vast instance (running).
    # So re-dispatching 'full' safely RESUMES only the killed/preempted legs (from their S3 checkpoints) without
    # duplicating the ones still running — no two instances ever share a leg's checkpoint (which would race).
    skip_done, skip_live = set(), set()
    if not dry:
        vk = os.environ.get("VAST_API_KEY")
        try:
            live = _vast_request("GET", "/instances/", vk, params={"owner": "me"}).get("instances", [])
            # only skip ACTIVELY-alive instances; an 'exited'/'stopped' one isn't doing the work (the mock
            # teardown leaves crashed/preempted containers lingering as 'exited'), so it SHOULD be relaunched
            _alive = ("running", "loading", "created", "scheduling", "starting")
            skip_live = {i.get("label") for i in live if i.get("label") and (i.get("actual_status") or "") in _alive}
        except Exception as e:  # noqa: BLE001
            print(f"[nrv04-launch] WARN could not list live instances ({e}); not skipping any", flush=True)
        try:
            import boto3
            s3 = boto3.client("s3")
            dk = _s3_list(s3, bucket, f"{RESULT_PREFIX}/", suffix=".json")
            skip_done = {k.split("/")[-2] for k in dk if k.rsplit("/", 1)[-1].startswith("leg_")}
        except Exception as e:  # noqa: BLE001
            print(f"[nrv04-launch] WARN could not list S3 results ({e}); not skipping any", flush=True)
    # presign the pre-packed env once (all instances share it); skipped on dry runs (no live submit).
    env_url = None if dry else presign_env_tarball(bucket)
    print(f"[nrv04-launch] {len(units)} unit(s), mode={mode}, dry_run={dry}, "
          f"skip_done={len(skip_done)}, skip_live={len(skip_live)}", flush=True)
    handles = []
    for leg, seed in units:
        name = unit_name(leg, seed)
        if not dry and name in skip_done:
            print(f"[skip] {name} — result already in S3", flush=True); continue
        if not dry and name in skip_live:
            print(f"[skip] {name} — live instance already running", flush=True); continue
        spec = build_jobspec(leg, seed, mode, branch, bucket, env_tarball_url=env_url)
        if dry:
            print(f"[dry] {spec.name}: gpu={spec.resources.gpu} ram>={spec.resources.ram_gb}GB "
                  f"ckpt={spec.checkpoint_uri} cofold={spec.env['COFOLD_PREFIX_S3']}", flush=True)
            continue
        h = be.submit(spec)
        print(f"[submit] {spec.name} -> instance {h.job_id} dph≈${h.extra.get('dph')}/hr", flush=True)
        handles.append({"unit": spec.name, "instance": h.job_id, "offer": h.extra.get("offer")})
    if handles:
        json.dump(handles, open("nrv04-vast-handles.json", "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
