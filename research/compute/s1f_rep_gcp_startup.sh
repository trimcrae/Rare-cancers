# shellcheck shell=bash
# ============================================================================================================
# The GCE startup script for ONE step-1 fan-out REPLICATE unit. Sourced by gpu-fanout-rep-gcp.yml, which
# prepends the per-run constants (UNIT_URI, STAGE_URI, CKPT_URI, IMAGE, RECEPTOR, GITREF, SMOKE).
#
# ⚠ THIS SCRIPT DOES NOT AND CANNOT TEAR DOWN ITS OWN VM. gcp-gpu-facts.md §6: the delete is REFUSED
# (`Required 'compute.instances.delete' permission`), measured, with three corroborations. There is
# deliberately NO self-delete here — not even a best-effort one — because the trap that "runs and no-ops"
# is exactly what made that failure invisible for five days. Teardown is:
#     (1) --max-run-duration + --instance-termination-action=DELETE, set at CREATE, enforced by GCE;
#     (2) the reap step at the head of every gpu-fanout-rep-gcp.yml dispatch, whose predicate is
#         gcp_fanout_rep.reap_decision — evidence, never age.
# What this script DOES owe the reaper is the evidence it keys on: the unit's ddg.json in GCS. That upload
# is the last thing it does, and everything before it is checkpointed so a boundary loses latency, not work.
#
# CHECKPOINTING (CLAUDE.md, standing rule): the engine's own GCSCommitStore writes each generation AS IT IS
# PRODUCED (manifest last, so a torn upload has no commit signal) — the "Continuous" shape, not an
# end-of-job sync. On top of that: run.log is re-uploaded every 120 s, phase.txt on every transition, and a
# finished leg's JSON goes up the moment it exists, so the second leg never re-runs the first.
# ============================================================================================================

exec > >(tee -a /tmp/run.log) 2>&1
GS=$(command -v gcloud || echo /snap/bin/gcloud)
PREFIX="$UNIT_URI"; [ "$SMOKE" = 1 ] && PREFIX="$UNIT_URI/smoke"

mark() {
  echo "[s1f-gcp] PHASE $1 $(date -u +%FT%TZ)"
  echo "$1 $(date -u +%FT%TZ)" | "$GS" storage cp - "$PREFIX/phase.txt" >/dev/null 2>&1 || true
  "$GS" storage cp /tmp/run.log "$PREFIX/run.log" >/dev/null 2>&1 || true
}

# --- the heartbeat, and the two ways it is guaranteed to die -------------------------------------------
# (1) parent-death poll: SIGKILL of this shell runs no trap, so the loop polls the PID it was handed and
#     exits when that shell is gone. (2) a hard TTL past the VM's own max-run cap. A heartbeat that outlives
#     its job keeps a log object fresh forever and would defeat any silence-based guard built on it later —
#     the Vast lane paid to learn that (congeneric_fanout_vast._PREAMBLE) and it is copied here on purpose.
_hb() { _p="$1"; _end=$(( $(date +%s) + 190000 ))
  while kill -0 "$_p" 2>/dev/null && [ "$(date +%s)" -lt "$_end" ]; do
    sleep 120; "$GS" storage cp /tmp/run.log "$PREFIX/run.log" >/dev/null 2>&1 || true
  done; }
_hb "$$" & HB=$!
trap '_rc=$?; kill "$HB" 2>/dev/null || true; "$GS" storage cp /tmp/run.log "$PREFIX/run.log" >/dev/null 2>&1 || true; exit $_rc' EXIT

mark boot
echo "[s1f-gcp] unit=$UNIT_URI smoke=$SMOKE image=$IMAGE"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || true

# --- docker + the NVIDIA runtime ------------------------------------------------------------------------
# DLVM common-cu* images ship both. VERIFY rather than assume: a CPU fallback here would produce a
# perfectly plausible ΔG at a fraction of the speed and file it as a GPU replicate. OPENMM_REQUIRE_CUDA=1
# in the leg env makes the engine raise instead of falling back, and this is the belt to that brace.
if ! docker info >/dev/null 2>&1; then
  echo "[s1f-gcp] docker not ready — waiting"; for i in $(seq 1 30); do sleep 10; docker info >/dev/null 2>&1 && break; done
fi
if ! docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi -L >/dev/null 2>&1; then
  echo "[s1f-gcp] --gpus all failed; installing nvidia-container-toolkit"
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    > /etc/apt/sources.list.d/nvidia-container-toolkit.list
  apt-get update -qq && apt-get install -y -qq nvidia-container-toolkit
  nvidia-ctk runtime configure --runtime=docker && systemctl restart docker && sleep 8
fi
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi -L \
  || { echo "[s1f-gcp] FATAL: no GPU inside docker"; mark "SMOKE-FAIL no-gpu-in-docker"; exit 3; }
mark docker-gpu-ok

# --- the image: PULL, DON'T SOLVE (CLAUDE.md §6) --------------------------------------------------------
# The SAME image the Vast fan-out runs, so openfe/openmmtools/pymbar are the versions that produced the
# n=0 edges this replicate is meant to be commensurable with.
docker pull "$IMAGE" || { echo "[s1f-gcp] FATAL: image pull failed"; mark "SMOKE-FAIL image-pull"; exit 3; }
mark image-pulled

# --- the repo code (the image supplies the ENV, the checkout supplies the CODE) --------------------------
mkdir -p /work && cd /work
curl -Ls "https://github.com/trimcrae/Rare-cancers/archive/refs/heads/${GITREF}.tar.gz" | tar xz
CODE=$(echo /work/Rare-cancers-*/research/modalities)
test -f "$CODE/nr4a3_rbfe.py" || { echo "[s1f-gcp] FATAL: no engine at $CODE"; mark "SMOKE-FAIL no-code"; exit 3; }

# --- the COMMON-MODE staged inputs, from GCS ------------------------------------------------------------
# A byte-verified mirror of the tree every n=0 edge read (gpu-fanout-rep-gcp.yml mode=mirror). This lane
# never re-stages: re-embedding the poses would move the shared core and quietly stop this being a replicate.
mkdir -p /work/in /work/out
"$GS" storage cp -r "$STAGE_URI/*" /work/in/ >/dev/null 2>&1
test -s "/work/in/ligand/docked_${RECEPTOR}.sdf"  || { echo "[s1f-gcp] FATAL: staged ligand SDF missing"; mark "SMOKE-FAIL no-ligand"; exit 3; }
test -s "/work/in/receptor/${RECEPTOR}-opened.pdb" || { echo "[s1f-gcp] FATAL: staged receptor PDB missing"; mark "SMOKE-FAIL no-receptor"; exit 3; }
mark staged

# --- the per-leg env, written by congeneric_fanout.unit_env on the control plane -------------------------
MD=http://metadata.google.internal/computeMetadata/v1/instance/attributes
curl -fs -H "Metadata-Flavor: Google" "$MD/s1f-env-complex" > /work/env.complex
curl -fs -H "Metadata-Flavor: Google" "$MD/s1f-env-solvent" > /work/env.solvent
UNIT_ID=$(curl -fs -H "Metadata-Flavor: Google" "$MD/s1f-unit-id")
echo "[s1f-gcp] unit_id=$UNIT_ID"; sed 's/^/  /' /work/env.complex

# --- google-cloud-storage inside the rbfe env -----------------------------------------------------------
# GCSCommitStore imports google.cloud.storage lazily. If the baked env lacks it (it was baked for an
# S3 lane) install THAT ONE PURE-PYTHON WHEEL. This is NOT the conda solve CLAUDE.md §6 forbids: it adds no
# compiled dependency and does not touch openfe/openmmtools/pymbar, so MBAR parity with the n=0 edges is
# untouched. Which of the two happened is printed, because "it worked" and "it was already there" are
# different facts and only one of them belongs in a Dockerfile change later.
if docker run --rm "$IMAGE" /opt/mamba/envs/rbfe/bin/python -c "from google.cloud import storage" 2>/dev/null; then
  echo "[s1f-gcp] google-cloud-storage: already in the image"
  GCSFIX=""
else
  echo "[s1f-gcp] google-cloud-storage: NOT in the image — installing the wheel into a derived layer"
  cat > /work/Dockerfile.gcs <<'DEOF'
ARG BASE
FROM ${BASE}
RUN /opt/mamba/envs/rbfe/bin/pip install --no-cache-dir google-cloud-storage
DEOF
  docker build -q --build-arg BASE="$IMAGE" -t s1frep:gcs -f /work/Dockerfile.gcs /work \
    || { echo "[s1f-gcp] FATAL: could not add google-cloud-storage"; mark "SMOKE-FAIL no-gcs-lib"; exit 3; }
  IMAGE=s1frep:gcs
  GCSFIX="google-cloud-storage was pip-installed on top of $IMAGE"
fi
mark env-ok

# --- ADC for the container ------------------------------------------------------------------------------
# GCSCommitStore authenticates with Application Default Credentials, which on a cloud-platform-scoped GCE VM
# resolve to the attached SA via the metadata server. The container reaches that server on the host network,
# so --network host is what makes keyless auth work inside docker; no key material anywhere.
DOCKER_COMMON="--rm --gpus all --network host -v /work:/work -w $CODE
  -e OPENMM_PLUGIN_DIR=/opt/mamba/envs/rbfe/lib/plugins
  -e INPUT_DIR=/work/in -e OUTPUT_DIR=/work/out -e CKPT_DIR=/work/out
  -e UNIT_ID=$UNIT_ID"

run_leg() {
  L="$1"
  if "$GS" storage cp "$UNIT_URI/leg_${RECEPTOR}_${L}.json" "/work/out/leg_${RECEPTOR}_${L}.json" >/dev/null 2>&1; then
    echo "[s1f-gcp] leg $L already in GCS — idempotent skip"; return 0
  fi
  mark "leg-$L-running"
  # set -e is deliberately NOT armed around the engine: the log must ship even (especially) when the leg
  # fails. The Vast lane lost a diagnostic exactly this way and the fix is copied rather than re-derived.
  # shellcheck disable=SC2086
  docker run $DOCKER_COMMON --env-file "/work/env.$L" "$IMAGE" \
      /opt/mamba/envs/rbfe/bin/python nr4a3_rbfe.py > "/tmp/$L.log" 2>&1
  rc=$?
  tail -80 "/tmp/$L.log" || true
  "$GS" storage cp "/tmp/$L.log" "$PREFIX/$L.log" >/dev/null 2>&1 || true
  if [ "$rc" -ne 0 ]; then echo "[s1f-gcp] leg $L FAILED rc=$rc"; mark "leg-$L-FAILED-rc$rc"; return 1; fi
  test -s "/work/out/leg_${RECEPTOR}_${L}.json" || {
    echo "[s1f-gcp] leg $L exited 0 with no result JSON"; mark "leg-$L-NORESULT"; return 1; }
  "$GS" storage cp "/work/out/leg_${RECEPTOR}_${L}.json" "$UNIT_URI/leg_${RECEPTOR}_${L}.json" >/dev/null 2>&1
  mark "leg-$L-done"
}

# ========================================================================================================
# SMOKE — the §6 shakeout. RBFE_TINY on the REAL edge, in the REAL container, on the L4, writing to a
# THROWAWAY prefix so it can never be mistaken for science or resumed into by the real leg.
# ========================================================================================================
if [ "$SMOKE" = 1 ]; then
  sed -i 's#^export RBFE_TINY=.*#export RBFE_TINY=1#; s#^export RBFE_SPOT_COMMIT_GCS=.*#export RBFE_SPOT_COMMIT_GCS='"$CKPT_URI"'/smoke#' /work/env.complex
  grep -qE '^export RBFE_TINY=1' /work/env.complex || echo "export RBFE_TINY=1" >> /work/env.complex
  echo "[s1f-gcp] SMOKE env:"; sed 's/^/  /' /work/env.complex
  mark smoke-running
  # shellcheck disable=SC2086
  docker run $DOCKER_COMMON --env-file /work/env.complex "$IMAGE" \
      /opt/mamba/envs/rbfe/bin/python nr4a3_rbfe.py > /tmp/smoke.log 2>&1
  rc=$?
  tail -120 /tmp/smoke.log || true
  "$GS" storage cp /tmp/smoke.log "$PREFIX/smoke.log" >/dev/null 2>&1 || true
  if [ "$rc" -eq 0 ] && [ -s "/work/out/leg_${RECEPTOR}_complex.json" ]; then
    # A COMMIT is part of the pass condition, not just an exit code. The whole point of the smoke is to
    # prove GCSCommitStore can WRITE — an "absent reading is not a reading of absence" (CLAUDE.md §4), and
    # a green rc with an empty commit prefix would be exactly that.
    NC=$("$GS" storage ls "$CKPT_URI/smoke/**" 2>/dev/null | wc -l)
    echo "[s1f-gcp] committed objects under the smoke prefix: $NC"
    if [ "$NC" -gt 0 ]; then mark "SMOKE-OK rc=0 commits=$NC ${GCSFIX}"; else mark "SMOKE-FAIL no-commit-written"; fi
  else
    mark "SMOKE-FAIL rc=$rc"
  fi
  exit 0
fi

# ========================================================================================================
# REAL — complex then solvent, then the reduce. Serial by design: GPUS_ALL_REGIONS=1.
# ========================================================================================================
run_leg complex || { echo "[s1f-gcp] complex leg did not finish — leaving checkpoints for a resume"; exit 1; }
run_leg solvent || { echo "[s1f-gcp] solvent leg did not finish — leaving checkpoints for a resume"; exit 1; }

mark reduce
# ⚠ The reduce is done HERE, not via nr4a3_rbfe.py MODE=reduce, for the reason congeneric_fanout_vast._REDUCE
# states: that path annotates its output with the denovo_401 ABFE anchor, a DIFFERENT scaffold, meaningless
# for a cmpd19 congeneric edge. The thermodynamic cycle is still rbfe_edges.ddg_bind. The schema below is
# the Vast lane's, field for field, PLUS a `provenance` block — because this draw ran on a different card
# and any SD built from it must say so rather than have a reader reconstruct it.
# shellcheck disable=SC2086
docker run $DOCKER_COMMON \
  -e RECEPTOR="$RECEPTOR" -e EDGE_ID="$EDGE_ID" -e LEG_ID="$LEG_ID" -e FRAME="$FRAME" \
  -e REPLICATE="$REPLICATE" -e SEED="$SEED" -e N_WINDOWS="$N_WINDOWS" -e MACHINE_TYPE="$MACHINE_TYPE" \
  -e BUCKET="$BUCKET" \
  "$IMAGE" /opt/mamba/envs/rbfe/bin/python - <<'PYEOF' > /tmp/reduce.log 2>&1
import json, os, subprocess, sys
sys.path.insert(0, os.getcwd())
import rbfe_edges as rb
import gcp_fanout_rep as gfr
out, rec = "/work/out", os.environ["RECEPTOR"]
cx = json.load(open(f"{out}/leg_{rec}_complex.json"))
sol = json.load(open(f"{out}/leg_{rec}_solvent.json"))
ddg = rb.ddg_bind(cx["dg_morph_kcal"], sol["dg_morph_kcal"])
unc = (cx.get("unc_kcal", 0.0) ** 2 + sol.get("unc_kcal", 0.0) ** 2) ** 0.5
unit = gfr.unit_for(os.environ["EDGE_ID"], int(os.environ["REPLICATE"]))
r = {
    "unit_id": os.environ["UNIT_ID"], "edge_id": os.environ["EDGE_ID"], "leg_id": os.environ["LEG_ID"],
    "receptor": rec, "frame": os.environ["FRAME"],
    "replicate": int(os.environ.get("REPLICATE") or 0), "seed": os.environ.get("SEED") or None,
    "ligand_a": cx["ligand_a"], "ligand_b": cx["ligand_b"],
    "ddg_bind_kcal": round(ddg, 3), "ddg_bind_unc_kcal": round(unc, 3),
    "dg_complex_morph_kcal": cx["dg_morph_kcal"], "complex_unc_kcal": cx.get("unc_kcal"),
    "dg_solvent_morph_kcal": sol["dg_morph_kcal"], "solvent_unc_kcal": sol.get("unc_kcal"),
    "n_mapped_atoms": cx.get("n_mapped_atoms"), "n_windows": int(os.environ["N_WINDOWS"]),
    "engine": "OpenFE RelativeHybridTopologyProtocol, HREX + MBAR (nr4a3_rbfe.py, MODE=splittest)",
    "uncertainty_note": "within-run MBAR standard errors, propagated in quadrature, for ONE independent "
                        "draw. NOT a replicate SD: a replicate SD exists only for an edge this lane ran at "
                        "more than one replicate index (see `replicate`).",
    "claim_ceiling": "CONDITIONAL relative binding free energy for a HYPOTHESIZED cmpd19 pose in ONE modeled "
                     "opened NR4A3 conformer. Not an affinity, not a selectivity claim.",
    "provenance": gfr.provenance(unit, os.environ.get("BUCKET", ""),
                                 machine_type=os.environ.get("MACHINE_TYPE")),
}
json.dump(r, open(f"{out}/ddg.json", "w"), indent=2)
print("S1F_RESULT", json.dumps(r))
PYEOF
tail -30 /tmp/reduce.log || true
"$GS" storage cp /tmp/reduce.log "$PREFIX/reduce.log" >/dev/null 2>&1 || true
test -s /work/out/ddg.json || { echo "[s1f-gcp] FATAL: reduce produced no ddg.json"; mark reduce-FAILED; exit 1; }

# THE LAST ACT, deliberately: this object is what the reaper keys on. Nothing may be written after it,
# because its presence is the assertion "there is no sampling left to lose".
"$GS" storage cp /work/out/ddg.json "$UNIT_URI/ddg.json" >/dev/null 2>&1
mark done
echo "[s1f-gcp] LEG DONE — ddg.json in $UNIT_URI. The VM cannot delete itself (gcp-gpu-facts.md §6); the"
echo "[s1f-gcp] reap step of gpu-fanout-rep-gcp.yml will remove it now that the result predates nothing."
