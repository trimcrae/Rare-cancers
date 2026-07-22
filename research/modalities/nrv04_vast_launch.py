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
TERNARY_RES = ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=4, ram_gb=16, disk_gb=40, interruptible=True)

# The onstart pipeline. $VARS are exported by _vast_onstart (leg env + forwarded AWS creds + CHECKPOINT_URI +
# ENV_TARBALL_URL). THE BOTTLENECK FIX: instead of a ~25-min `micromamba create` MD solve PER instance (the
# diagnosed stall), each instance extracts a PRE-PACKED conda env (built once on CI via conda-pack, cached in
# S3) from a presigned URL in ~1-2 min. Repo code comes from the public codeload tarball (no git in the base
# image). Everything after that (aws, python) runs out of the extracted env. Phase markers land in S3 for
# `collect`/`diag`.
_PIPELINE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -q && apt-get install -y -q --no-install-recommends curl ca-certificates
# --- pre-packed MD conda env (built once on CI; ~1-2 min extract vs ~25-min per-host solve) ---
mkdir -p /opt/mamba/envs/md
curl -Ls "$ENV_TARBALL_URL" | tar xz -C /opt/mamba/envs/md
/opt/mamba/envs/md/bin/conda-unpack || true
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


def diag():
    """Print the onstart log of each running instance — the diagnostic for a stuck/slow Vast run."""
    key = os.environ.get("VAST_API_KEY")
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    print(f"[diag] {len(insts)} instance(s)", flush=True)
    for i in insts:
        print(f"\n===== instance {i.get('id')} ({i.get('label')}) status={i.get('actual_status')} =====", flush=True)
        print(_vast_instance_logs(key, i.get("id")), flush=True)


def collect(bucket):
    """Monitor the panel run: list MY Vast instances (confirm running / torn down — no idle bleed) and the leg
    JSONs already in the result prefix. Prints a status board so we can watch the pilot + fan-out from CI."""
    import boto3
    key = os.environ.get("VAST_API_KEY")
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", []) if key else []
    print(f"[collect] Vast instances up: {len(insts)}", flush=True)
    for i in insts:
        print(f"[collect]   id={i.get('id')} status={i.get('actual_status')} label={i.get('label')} "
              f"dph=${i.get('dph_total')}/hr", flush=True)
    s3 = boto3.client("s3")
    phases = {}
    for pk in _s3_list(s3, bucket, f"{RESULT_PREFIX}/", suffix="phase.txt"):
        unit = pk.split("/")[-2]
        phases[unit] = s3.get_object(Bucket=bucket, Key=pk)["Body"].read().decode().strip()
    keys = _s3_list(s3, bucket, f"{RESULT_PREFIX}/", suffix=".json")
    results = []
    for k in keys:
        body = s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode()
        try:
            results.append(json.loads(body))
        except Exception:  # noqa: BLE001
            results.append({"key": k, "bytes": len(body)})
    status = {
        "vast_instances": [{"id": i.get("id"), "status": i.get("actual_status"), "label": i.get("label"),
                            "is_bid": i.get("is_bid"), "dph_total": i.get("dph_total"),
                            "dph_base": i.get("dph_base"), "min_bid": i.get("min_bid"),
                            "gpu_name": i.get("gpu_name"), "start_date": i.get("start_date"),
                            "duration": i.get("duration")} for i in insts],
        "phases": phases,
        "n_results": len(keys), "results": results,
    }
    json.dump(status, open("nrv04-collect-status.json", "w"), indent=2)
    print("[collect] " + json.dumps(status, indent=2), flush=True)


def stop_all():
    """Destroy every one of MY Vast instances (stop the bleed). Prints each id it tears down."""
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("[stop] VAST_API_KEY not set")
    insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    print(f"[stop] {len(insts)} instance(s) to destroy", flush=True)
    for i in insts:
        iid = i.get("id")
        _vast_request("DELETE", f"/instances/{iid}/", key)
        print(f"[stop] destroyed {iid} ({i.get('label')})", flush=True)
    print("[stop] done", flush=True)


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
        image="nvidia/cuda:12.4.1-runtime-ubuntu22.04",
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
        return [(pilot, 0)]
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


def main():
    bucket = os.environ.get("VAST_CKPT_BUCKET")
    if not bucket:
        raise SystemExit("[nrv04-launch] set VAST_CKPT_BUCKET (the reused S3 bucket)")
    if os.environ.get("DISCOVER") == "1":
        discover_cofold(bucket)
        return 0
    if os.environ.get("STAGE_TEST") == "1":
        stage_test(bucket)
        return 0
    if os.environ.get("COLLECT") == "1":
        collect(bucket)
        return 0
    if os.environ.get("STOP_ALL") == "1":
        stop_all()
        return 0
    if os.environ.get("DIAG") == "1":
        diag()
        return 0
    branch = os.environ.get("GIT_BRANCH", "claude/alternative-gpu-providers-wx4r2c")
    mode = os.environ.get("MODE", "run")
    dry = os.environ.get("DRY_RUN", "0") == "1"

    be = get_backend("vast")
    units = units_to_run()
    # presign the pre-packed env once (all instances share it); skipped on dry runs (no live submit).
    env_url = None if dry else presign_env_tarball(bucket)
    print(f"[nrv04-launch] {len(units)} unit(s), mode={mode}, dry_run={dry}", flush=True)
    handles = []
    for leg, seed in units:
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
