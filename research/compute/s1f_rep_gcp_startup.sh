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
# ⚠ AND THE SECOND PIECE OF EVIDENCE IT OWES: `BOOTSTRAP-FAIL <cause>`. Measured 2026-07-31 7:20 PM ET, on
# the first real leg: the parity guard refused, this script exited 3 — and the VM kept holding the account's
# ONE GPU with nothing on it, because a run writes no ddg.json and the reaper's only run-mode evidence was
# that object. Its bound was the 48 h create-time cap, for a job that died in four minutes. So every
# PRE-MD failure now marks `BOOTSTRAP-FAIL`, which is a DISTINCT prefix from the smoke's own SMOKE-OK /
# SMOKE-FAIL precisely so it is unambiguous in either mode: it can only be written before `run_leg` is ever
# called, so no sampling has started and no checkpoint exists, and the reaper may act on it in ANY mode.
#
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
#
# ★★ AND IT SHIPS THE **LEG'S** LOG AND THE GPU COUNTERS, NOT JUST THE WRAPPER'S (2026-08-01).
# `run_leg` redirects the engine to `/tmp/<leg>.log` and uploads it only AFTER `docker run` returns, so
# between `PHASE leg-complex-running` and the first `COMMITTED.json` there is NO live signal at all — and
# on the complex leg those are ~23-39 min apart, longer still across a system rebuild or a resume's
# checkpoint fetch. Over that whole window "healthy" and "wedged" produce the identical observation from
# outside the box. CLAUDE.md §4 requires a PROGRESS check — GPU busy, phase moved, iteration count up —
# and none of the three was observable. Two lines fix it, and engineering is free:
#
# ⚠ RETRACTED, IN THE SAME COMMIT THAT MADE IT: this comment first said "measured that morning: a resumed
# leg sat 56 min with nothing readable". That number was an ET mis-conversion of a leg that was ~19 min
# old — the gap it describes is real and is the reason for this code, but 56 min was never measured and
# must not be quoted. Superseded, retained (CLAUDE.md §1.2).
#   * the in-flight leg log goes up on the same 120 s tick, so `mode=tail` sees `Iteration n/2000` live;
#   * `nvidia-smi` utilisation/memory is appended to run.log each tick, so "the GPU is busy" is a READING
#     rather than an inference. ⚠ It is diagnostic ONLY: GPU idleness must never condemn a box (CLAUDE.md
#     §6 — the same rule `vast_idle_guard` is built on), because a legitimately CPU-bound OpenFE system
#     build reads 0 % for many minutes.
_hb() { _p="$1"; _end=$(( $(date +%s) + 190000 ))
  while kill -0 "$_p" 2>/dev/null && [ "$(date +%s)" -lt "$_end" ]; do
    sleep 120
    echo "[s1f-gcp] hb $(date -u +%FT%TZ) gpu=$(nvidia-smi --query-gpu=utilization.gpu,memory.used \
      --format=csv,noheader 2>/dev/null | tr '\n' ' ')" >> /tmp/run.log
    "$GS" storage cp /tmp/run.log "$PREFIX/run.log" >/dev/null 2>&1 || true
    # The leg's own stdout, WHILE it is running.
    # ⚠ THE CHANNEL IS A FILE, NOT A SHELL VARIABLE, AND THAT IS NOT STYLE. This loop is a BACKGROUND
    # SUBSHELL forked before `run_leg` ever executes, so it holds a COPY of the environment as it was at
    # fork time: a `_LEGLOG=...` assigned in the parent afterwards is invisible here forever, and the
    # upload would silently never happen while every line of it looked correct. A file is read fresh each
    # tick. (Caught by reading, not by an outage — which is the only way this one could have been caught.)
    _lg=$(cat /tmp/_leglog 2>/dev/null || true)
    if [ -n "${_lg}" ] && [ -s "${_lg}" ]; then
      "$GS" storage cp "${_lg}" "$PREFIX/$(basename "${_lg}")" >/dev/null 2>&1 || true
    fi
  done; }
_hb "$$" & HB=$!
trap '_rc=$?; kill "$HB" 2>/dev/null || true; "$GS" storage cp /tmp/run.log "$PREFIX/run.log" >/dev/null 2>&1 || true; exit $_rc' EXIT

mark boot
echo "[s1f-gcp] unit=$UNIT_URI smoke=$SMOKE image=$IMAGE"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || true

# --- docker + the NVIDIA container runtime --------------------------------------------------------------
# ⚠ MEASURED 2026-07-31 (run 30670712574, serial console + the leg's own run.log), and it retires the
# assumption this block was first written on:
#     /tmp/metadata-scripts…/startup-script: line 81: docker: command not found
#     Failed to restart docker.service: Unit docker.service not found.
# **The DLVM `common-cu129-ubuntu-2404-nvidia-580` image ships NO DOCKER.** The first version waited 300 s
# for a daemon that was never going to appear, then tried to configure a runtime for it. A second, separate
# fault came out of the same run:
#     gpg: cannot open '/dev/tty': No such device or address
#     E: Unable to correct problems, you have held broken packages.
# A startup script has no controlling terminal, so plain `gpg --dearmor` tries to prompt and writes no
# keyring — after which the NVIDIA repo is unusable and apt reports it as "held broken packages", which
# names neither cause. `--batch --yes` fixes it.
#
# So: DETECT, then INSTALL, and let every failure name itself in the phase marker. The driver itself is
# already on the image (`nvidia-smi` above reported the L4 and driver 580.173.02) — only the container
# plumbing is missing.
echo "[s1f-gcp] docker binary: $(command -v docker 2>/dev/null || echo ABSENT) | service: $(systemctl is-active docker 2>/dev/null || echo none)"
# The DLVM's own first-boot work holds the dpkg lock; apt would fail with a lock error that reads like a
# repo problem. Wait for it rather than race it.
for i in $(seq 1 60); do fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || break; sleep 10; done
export DEBIAN_FRONTEND=noninteractive
if ! command -v docker >/dev/null 2>&1; then
  echo "[s1f-gcp] installing docker.io (this image has none)"
  apt-get update -qq && apt-get install -y -qq docker.io \
    || { echo "[s1f-gcp] FATAL: docker.io install failed"; mark "BOOTSTRAP-FAIL docker-install"; exit 3; }
fi
systemctl enable --now docker >/dev/null 2>&1 || true
for i in $(seq 1 18); do docker info >/dev/null 2>&1 && break; sleep 5; done
docker info >/dev/null 2>&1 \
  || { echo "[s1f-gcp] FATAL: docker daemon will not start"; mark "BOOTSTRAP-FAIL docker-daemon"; exit 3; }
echo "[s1f-gcp] docker up: $(docker --version)"

if ! docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi -L >/dev/null 2>&1; then
  echo "[s1f-gcp] --gpus all failed; installing nvidia-container-toolkit"
  install -m 0755 -d /usr/share/keyrings
  # --batch --yes: no tty here (measured above). Without them the keyring is silently never written.
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
    | gpg --batch --yes --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    || { echo "[s1f-gcp] FATAL: could not write the NVIDIA keyring"; mark "BOOTSTRAP-FAIL nvidia-keyring"; exit 3; }
  test -s /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    || { echo "[s1f-gcp] FATAL: NVIDIA keyring is empty"; mark "BOOTSTRAP-FAIL nvidia-keyring-empty"; exit 3; }
  curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    > /etc/apt/sources.list.d/nvidia-container-toolkit.list
  apt-get update -qq && apt-get install -y -qq nvidia-container-toolkit \
    || { echo "[s1f-gcp] FATAL: nvidia-container-toolkit install failed"; mark "BOOTSTRAP-FAIL nvidia-toolkit"; exit 3; }
  nvidia-ctk runtime configure --runtime=docker && systemctl restart docker && sleep 8
fi
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi -L \
  || { echo "[s1f-gcp] FATAL: no GPU inside docker"; mark "BOOTSTRAP-FAIL no-gpu-in-docker"; exit 3; }
mark docker-gpu-ok

# --- the image: PULL, DON'T SOLVE (CLAUDE.md §6) --------------------------------------------------------
# The SAME image the Vast fan-out runs, so openfe/openmmtools/pymbar are the versions that produced the
# n=0 edges this replicate is meant to be commensurable with.
docker pull "$IMAGE" || { echo "[s1f-gcp] FATAL: image pull failed"; mark "BOOTSTRAP-FAIL image-pull"; exit 3; }
mark image-pulled

# --- the repo code (the image supplies the ENV, the checkout supplies the CODE) --------------------------
mkdir -p /work && cd /work
curl -Ls "https://github.com/trimcrae/Rare-cancers/archive/refs/heads/${GITREF}.tar.gz" | tar xz
CODE=$(echo /work/Rare-cancers-*/research/modalities)
test -f "$CODE/nr4a3_rbfe.py" || { echo "[s1f-gcp] FATAL: no engine at $CODE"; mark "BOOTSTRAP-FAIL no-code"; exit 3; }

# --- the COMMON-MODE staged inputs, from GCS ------------------------------------------------------------
# A byte-verified mirror of the tree every n=0 edge read (gpu-fanout-rep-gcp.yml mode=mirror). This lane
# never re-stages: re-embedding the poses would move the shared core and quietly stop this being a replicate.
mkdir -p /work/in /work/out
"$GS" storage cp -r "$STAGE_URI/*" /work/in/ >/dev/null 2>&1
test -s "/work/in/ligand/docked_${RECEPTOR}.sdf"  || { echo "[s1f-gcp] FATAL: staged ligand SDF missing"; mark "BOOTSTRAP-FAIL no-ligand"; exit 3; }
test -s "/work/in/receptor/${RECEPTOR}-opened.pdb" || { echo "[s1f-gcp] FATAL: staged receptor PDB missing"; mark "BOOTSTRAP-FAIL no-receptor"; exit 3; }
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
# ⚠ THE PROBE IS READ WITH STDERR VISIBLE AND ITS FAILURE IS A DIFFERENT CAUSE FROM A MOVED STACK.
# Measured 7:36 PM ET 2026-07-31: the first version of this probe used `openmmtools.version.version` etc.
# and swallowed stderr with `2>/dev/null`. Both readings came back EMPTY, the comparison saw
# "" != "" as unequal-and-unreadable, and the guard reported "MOVED the science stack" — a FALSE
# DIAGNOSIS of a probe that had simply raised. That is CLAUDE.md §4's "an ABSENT READING is not a reading
# of ABSENCE", committed by the very guard written to enforce provenance. Two fixes, both structural:
#   (1) `importlib.metadata.version` rather than guessed `__version__` attribute paths — it works for the
#       conda-installed packages here, and a missing distribution raises with a NAME in the message;
#   (2) stderr is KEPT, and "could not measure" gets its OWN refusal (`parity-unreadable`) distinct from
#       "measured and moved" (`parity-moved`). Conflating them is what made the first failure unreadable.
PARITY='import importlib.metadata as m; print("PARITY " + " ".join(n + "=" + m.version(n) for n in ("openfe","openmmtools","pymbar","numpy","scipy")))'
BASE_PARITY=$(docker run --rm "$IMAGE" /opt/mamba/envs/rbfe/bin/python -c "$PARITY" 2>/tmp/parity.err | grep -a '^PARITY ' | tail -1)
echo "[s1f-gcp] base image parity: ${BASE_PARITY:-<UNREADABLE>}"
if [ -z "$BASE_PARITY" ]; then
  echo "[s1f-gcp] FATAL: could not READ the base image's versions — this is not a parity failure, it is an"
  echo "[s1f-gcp] unreadable probe, and the two must never be conflated. Probe stderr:"
  sed 's/^/[s1f-gcp]   /' /tmp/parity.err | head -20
  mark "BOOTSTRAP-FAIL parity-unreadable"; exit 3
fi
if docker run --rm "$IMAGE" /opt/mamba/envs/rbfe/bin/python -c "from google.cloud import storage" 2>/dev/null; then
  echo "[s1f-gcp] google-cloud-storage: already in the image"
  GCSFIX=""
else
  echo "[s1f-gcp] google-cloud-storage: NOT in the image — adding the wheel in a derived layer"
  # ⚠ MEASURED 7:20 PM ET 2026-07-31: an UNCONSTRAINED `pip install google-cloud-storage` MOVES the science
  # stack. The parity check below caught it and refused, which is the guard working — but a check that
  # refuses still leaves the lane unable to run. The right tool is a pip CONSTRAINTS file built from the
  # env's OWN `pip list --format=freeze`: it forbids pip from changing any package that is already
  # installed, so the install either lands additively or FAILS. Parity then holds by CONSTRUCTION and the
  # check below becomes the belt to that brace rather than the only thing standing between us and a silent
  # protocol deviation. (`pip list --format=freeze` and not `pip freeze`: the latter emits
  # `pkg @ file:///…` direct references for conda-installed packages, which are not valid constraints.)
  cat > /work/Dockerfile.gcs <<'DEOF'
ARG BASE
FROM ${BASE}
RUN P=/opt/mamba/envs/rbfe/bin/python \
 && $P -m pip list --format=freeze 2>/dev/null | grep -E '^[A-Za-z0-9._-]+==' > /tmp/constraints.txt \
 && echo "constraints: $(wc -l < /tmp/constraints.txt) pinned packages" \
 && $P -m pip install --no-cache-dir -c /tmp/constraints.txt google-cloud-storage
DEOF
  BASE_IMAGE="$IMAGE"
  docker build -q --build-arg BASE="$BASE_IMAGE" -t s1frep:gcs -f /work/Dockerfile.gcs /work \
    || { echo "[s1f-gcp] FATAL: could not add google-cloud-storage"; mark "BOOTSTRAP-FAIL no-gcs-lib"; exit 3; }
  # ★★ PARITY IS THE SCIENTIFIC ARGUMENT (CLAUDE.md §6), SO PROVE IT RATHER THAN HOPE.
  # `pip install google-cloud-storage` drags in protobuf/grpcio/requests and is free to UPGRADE a shared
  # dependency while it is there. If it moved numpy, scipy, pymbar, openmmtools or openfe, this replicate
  # would no longer be running the stack that produced the n=0 edges — a silent protocol deviation, and the
  # exact class §6 says an ad-hoc environment change is. So the five versions are read BEFORE and AFTER and
  # any difference is a REFUSAL, not a warning: a replicate computed on a different stack is worse than no
  # replicate, because it looks like one.
  NEW_PARITY=$(docker run --rm s1frep:gcs /opt/mamba/envs/rbfe/bin/python -c "$PARITY" 2>/tmp/parity2.err | grep -a '^PARITY ' | tail -1)
  echo "[s1f-gcp] derived image parity: ${NEW_PARITY:-<UNREADABLE>}"
  if [ -z "$NEW_PARITY" ]; then
    echo "[s1f-gcp] FATAL: could not READ the derived image's versions (NOT a parity failure). stderr:"
    sed 's/^/[s1f-gcp]   /' /tmp/parity2.err | head -20
    mark "BOOTSTRAP-FAIL parity-unreadable"; exit 3
  fi
  if [ "$BASE_PARITY" != "$NEW_PARITY" ]; then
    echo "[s1f-gcp] FATAL: adding google-cloud-storage MOVED the science stack"
    echo "[s1f-gcp]   before: $BASE_PARITY"
    echo "[s1f-gcp]   after : $NEW_PARITY"
    echo "[s1f-gcp] Fix by adding google-cloud-storage to research/compute/Dockerfile.nr4a3fep and re-baking"
    echo "[s1f-gcp] ONCE, which is what CLAUDE.md §6 prescribes for a genuinely missing dep."
    mark "BOOTSTRAP-FAIL parity-moved"; exit 3
  fi
  IMAGE=s1frep:gcs
  GCSFIX="google-cloud-storage added on top of $BASE_IMAGE; openfe/openmmtools/pymbar/numpy/scipy VERIFIED unmoved ($NEW_PARITY)"
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

# ★ THE DISCRIMINATING PROBE, run in the LEG'S OWN CONTAINER with the LEG'S OWN env -----------------------
# Measured 7:51 PM ET 2026-07-31: the leg raised `openmm.OpenMMException: No compatible CUDA device is
# available` at openmmtools' first `openmm.Context(...)` — on a boot whose bootstrap check
# (`docker run --gpus all nvidia/cuda:…base nvidia-smi -L`) had PASSED, and after a smoke on the same
# machinery had produced a real ΔG. So "the host has a GPU" and "this container's OpenMM can open it" are
# DIFFERENT propositions and the bootstrap check only established the first.
#
# This probe closes that gap by asking the exact question, in the exact image, under the exact flags: can
# THIS process construct a CUDA context? It costs seconds, it runs before any leg is paid for, and its
# failure is a BOOTSTRAP-FAIL — i.e. terminal, reapable, and named — instead of a leg that dies minutes in
# and leaves the VM holding the account's only GPU on a refusal.
gpu_probe() {
  # shellcheck disable=SC2086
  docker run $DOCKER_COMMON --env-file /work/env.complex "$IMAGE" \
    /opt/mamba/envs/rbfe/bin/python -c '
import os, openmm
print("[probe] CUDA_VISIBLE_DEVICES=", os.environ.get("CUDA_VISIBLE_DEVICES", "<unset>"))
print("[probe] OPENMM_PLUGIN_DIR=", os.environ.get("OPENMM_PLUGIN_DIR", "<unset>"))
print("[probe] loaded plugins:", openmm.pluginLoadedLibNames)
print("[probe] load failures:", openmm.Platform.getPluginLoadFailures())
print("[probe] platforms:", [openmm.Platform.getPlatform(i).getName()
                             for i in range(openmm.Platform.getNumPlatforms())])
p = openmm.Platform.getPlatformByName("CUDA")
s = openmm.System(); s.addParticle(1.0)
c = openmm.Context(s, openmm.VerletIntegrator(0.001), p)
print("[probe] CUDA CONTEXT OK device=", p.getPropertyValue(c, "DeviceName"))
' 2>&1
}
echo "[s1f-gcp] --- CUDA probe in the leg container ---"
if ! gpu_probe | tee /tmp/probe.log | sed 's/^/[s1f-gcp]   /'; then
  echo "[s1f-gcp] FATAL: the leg container cannot build a CUDA context (see the probe output above)."
  "$GS" storage cp /tmp/probe.log "$PREFIX/cuda_probe.log" >/dev/null 2>&1 || true
  mark "BOOTSTRAP-FAIL cuda-not-in-leg-container"; exit 3
fi
grep -q "CUDA CONTEXT OK" /tmp/probe.log || {
  echo "[s1f-gcp] FATAL: probe returned 0 without a CUDA context — refusing rather than measuring on CPU."
  "$GS" storage cp /tmp/probe.log "$PREFIX/cuda_probe.log" >/dev/null 2>&1 || true
  mark "BOOTSTRAP-FAIL cuda-not-in-leg-container"; exit 3; }
"$GS" storage cp /tmp/probe.log "$PREFIX/cuda_probe.log" >/dev/null 2>&1 || true
mark cuda-probe-ok

run_leg() {
  L="$1"
  if "$GS" storage cp "$UNIT_URI/leg_${RECEPTOR}_${L}.json" "/work/out/leg_${RECEPTOR}_${L}.json" >/dev/null 2>&1; then
    echo "[s1f-gcp] leg $L already in GCS — idempotent skip"; return 0
  fi
  mark "leg-$L-running"
  # Tell the heartbeat which file is the LIVE leg log, so it ships while the leg runs rather than only
  # after it returns (see _hb). Cleared below whatever the outcome, so a finished leg's log is never
  # re-uploaded as if it were in flight.
  : > "/tmp/$L.log"; echo "/tmp/$L.log" > /tmp/_leglog
  # set -e is deliberately NOT armed around the engine: the log must ship even (especially) when the leg
  # fails. The Vast lane lost a diagnostic exactly this way and the fix is copied rather than re-derived.
  # shellcheck disable=SC2086
  docker run $DOCKER_COMMON --env-file "/work/env.$L" "$IMAGE" \
      /opt/mamba/envs/rbfe/bin/python nr4a3_rbfe.py > "/tmp/$L.log" 2>&1
  rc=$?
  : > /tmp/_leglog          # the leg has returned; stop shipping its log as if it were in flight
  tail -80 "/tmp/$L.log" || true
  "$GS" storage cp "/tmp/$L.log" "$PREFIX/$L.log" >/dev/null 2>&1 || true
  if [ "$rc" -ne 0 ]; then
    # ★★ THE POST-MORTEM, CAPTURED ON THE BOX WHILE THE BOX STILL EXISTS (2026-08-01).
    # The first real leg died with `openmm.OpenMMException: No compatible CUDA device is available` at the
    # FIRST context creation of the production phase — 16 s after committing warmup 400/400, on a GPU that
    # had just done 3 h 53 m of successful CUDA work. Localising it that far was possible from the leg log;
    # going further was NOT, because the only two things that could discriminate a driver/ECC/Xid event
    # from a resource limit live on the HOST and the VM is reaped minutes later. The container has already
    # exited by the time this runs, so nothing here can perturb the failure — it can only record it.
    # This is CLAUDE.md §4's "instrument the code and run a controlled reproduction", pre-armed: the next
    # occurrence arrives with its own evidence instead of another round of inference.
    { echo "=== post-mortem for leg $L (rc=$rc) at $(date -u +%FT%TZ) ==="
      echo "--- nvidia-smi -q (ECC, retired pages, memory, processes) ---"; nvidia-smi -q 2>&1
      echo "--- nvidia-smi (summary) ---"; nvidia-smi 2>&1
      echo "--- kernel ring buffer: NVRM / Xid / nvidia / OOM ---"
      dmesg 2>/dev/null | grep -iE 'xid|nvrm|nvidia|out of memory|oom-kill' | tail -60
      echo "--- free -m / df -h /var/lib/docker ---"; free -m 2>&1; df -h / /var/lib/docker 2>&1
      echo "--- docker ps -a (exit codes) ---"; docker ps -a 2>&1 | head -10
    } > "/tmp/postmortem.$L.txt" 2>&1
    "$GS" storage cp "/tmp/postmortem.$L.txt" "$PREFIX/postmortem_$L.txt" >/dev/null 2>&1 || true
    echo "[s1f-gcp] leg $L FAILED rc=$rc (post-mortem in $PREFIX/postmortem_$L.txt)"
    mark "leg-$L-FAILED-rc$rc"; return 1
  fi
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
  # RBFE_TINY=1 -> 2.5 ps / 10 ps MD (the engine's own plumbing shakeout length), and a THROWAWAY commit
  # prefix so nothing here can ever be resumed into by the real leg. The commit interval drops to 1 because
  # the pass condition below is "a generation actually reached GCS": at the real 20/40 a run this short
  # would legitimately commit nothing, and a green rc over an empty prefix is precisely the absent-reading-
  # read-as-a-reading-of-absence that CLAUDE.md §4 forbids.
  sed -i 's#^RBFE_TINY=.*#RBFE_TINY=1#
          s#^RBFE_SPOT_COMMIT_GCS=.*#RBFE_SPOT_COMMIT_GCS='"$CKPT_URI"'/smoke#
          s#^RBFE_WARMUP_CKPT_ITERS=.*#RBFE_WARMUP_CKPT_ITERS=1#
          s#^RBFE_PROD_CKPT_ITERS=.*#RBFE_PROD_CKPT_ITERS=1#' /work/env.complex
  grep -qE '^RBFE_TINY=1' /work/env.complex || echo "RBFE_TINY=1" >> /work/env.complex
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
# ⚠ `-i` IS LOAD-BEARING. `python -` reads the program from stdin, and without `-i` docker does not forward
# it: python sees EOF, exits 0 having done nothing, and the only symptom is "reduce produced no ddg.json"
# three lines later — after both legs have already been paid for. Caught by reading, not by an outage.
# shellcheck disable=SC2086
docker run -i $DOCKER_COMMON \
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
