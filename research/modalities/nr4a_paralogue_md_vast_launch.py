#!/usr/bin/env python3
"""Launch the matched NR4A1 / NR4A2 conformer-ensemble legs on Vast.ai.

WHAT IT BUYS. The categorical selectivity axis — the basis Tier 2 passed on — asserts that the paralogues are
structurally INCAPABLE of the covalent step. That is a SEQUENCE fact at the aligned position and is not in
doubt. What was never tested is whether paralogue DYNAMICS open a COMPENSATING site: another cysteine, anywhere
in the fold, that a populated conformer brings within tether range of the same linker paths. Every paralogue
comparison in the repo so far is ONE static opened conformer. This launcher builds the matched ensembles.

MATCHED means the same protocol, not merely the same idea: `nr4a3_metad.py` unchanged (so the force field,
water model, cutoffs, constraints, thermostat, timestep, walls and well-tempered parameters are the SAME
objects that produced the NR4A3 ensemble), with the collective variable mapped onto each paralogue's
HOMOLOGOUS Pocket-5 lining by the module's own BLOSUM62 alignment; then `nr4a_paralogue_release.py` for the
unbiased replicas seeded at the same CV value. Every way the result is NOT matched is recorded in
release_summary.json rather than argued away.

SPEND. One interruptible host per paralogue, run CONCURRENTLY — there is no result NR4A1 could return that
would make us skip NR4A2 (the categorical claim is against BOTH), so serialising would be pure wall-clock for
zero decision value. Host selection ranks live offers by all-in $/ns (`vast_cost_model`), never by $/hr; the
bid is the floor plus a staleness tick, capped at that machine's on-demand price. A `resources_unavailable`
start refusal means DESTROY + exclude the machine + pick another, never wait and never raise the bid.

RESUME. Per-phase checkpoints stream to S3 continuously (small restart set every 2 min, trajectory every
10 min), so a preemption costs at most one interval and a re-dispatch with the same prefix resumes.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpu_backend import JobSpec, ResourceSpec, get_backend  # noqa: E402

REPO = "https://github.com/trimcrae/Rare-cancers"
VAST_IMAGE = os.environ.get("VAST_IMAGE") or "docker.io/triskit23/nr4a-metad:latest"
RESULT_PREFIX = os.environ.get("PDYN_RESULT_PREFIX", "nr4a-paralogue-ensemble")
DEFAULT_BUCKET = "sagemaker-us-east-2-646605541856"

# 24 GB is ample for a ~90k-particle solvated LBD; the leg is throughput-bound, not memory-bound, so the offer
# ranking (all-in $/ns over every benched card) is left free to pick 4090 / 4080 / 3090 on price. min_cuda
# mirrors the repo's settled host filter — this image's OpenMM PTX needs a modern driver to JIT.
def resources(gpu=None, exclude=()):
    return ResourceSpec(gpu=gpu or os.environ.get("PDYN_GPU", "rtx4090"),
                        min_vram_gb=int(os.environ.get("PDYN_VRAM", "16")),
                        vcpus=4, ram_gb=16, disk_gb=int(os.environ.get("PDYN_DISK", "60")),
                        min_cuda=13.0, interruptible=True,
                        exclude_machine_ids=tuple(exclude))


_PIPELINE = r"""
set -o pipefail
export HOME=/root
export PATH=/opt/mamba/envs/md/bin:$PATH
exec > >(tee /tmp/run.log) 2>&1
echo "[pdyn] $(date -u +%FT%TZ) start target=$TARGET metad_ns=$METAD_NS release_ns=$RELEASE_NS mode=$MODE"
push_log() { aws s3 cp /tmp/run.log "$RESULT_S3/run.log" --only-show-errors 2>/dev/null || true; }
# IDEMPOTENCY: Vast re-runs onstart after a container restart. If the deliverable is already in S3 there is
# nothing to do — exit so the box stops billing and waits for the CI reap.
if aws s3 ls "$RESULT_S3/$(echo $TARGET | tr A-Z a-z)-pocket-ensemble.tar.gz" >/dev/null 2>&1; then
  echo "[pdyn] result already in S3 -> nothing to do (awaiting CI reap)"; push_log; exit 0
fi
nvidia-smi || true
cd /root
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz || { echo "repo pull failed"; push_log; exit 3; }
cd Rare-cancers-*/research/modalities || { echo "repo layout unexpected"; push_log; exit 3; }
mkdir -p /work/ckpt
# stream the log to S3 every minute so a crash is READABLE after the host self-terminates
( while true; do sleep 60; push_log; done ) &
python nr4a_paralogue_md_job.py --target "$TARGET" --metad-ns "$METAD_NS" --release-ns "$RELEASE_NS" \
       --n-rep "$N_REP" --seed "$SEED" --segment-ns "$SEGMENT_NS"
rc=$?
echo "[pdyn] $(date -u +%FT%TZ) job exit=$rc"
push_log
exit $rc
"""


def build_jobspec(target, mode="real", metad_ns=None, release_ns=None, n_rep=None, git_branch=None,
                  bucket=None, exclude=()):
    """PURE construction of one paralogue's JobSpec (no network) — unit-testable, and the place every
    parameter that keys the checkpoint prefix is fixed."""
    target = target.upper()
    smoke = mode == "smoke"
    # A smoke runs the WHOLE chain (metad -> release -> export -> upload) at toy length, so it proves the
    # image, the CV mapping, PLUMED, the release seeding, mdtraj export and S3 — everything except duration.
    m_ns = float(metad_ns if metad_ns is not None else (0.4 if smoke else 60.0))
    r_ns = float(release_ns if release_ns is not None else (0.2 if smoke else 5.0))
    reps = int(n_rep if n_rep is not None else (1 if smoke else 3))
    branch = git_branch or os.environ.get("GIT_BRANCH") or "main"
    # `or`, NOT .get(key, default): CI passes a blank optional input as an EMPTY STRING, which is a SET
    # variable, so a .get default never fires and the URI comes out as "s3:///..." with every upload silently
    # failing behind `|| true`. Same hole that was fixed in protfep_vast_launch and bioemu_vast_launch.
    b = bucket or os.environ.get("VAST_CKPT_BUCKET") or DEFAULT_BUCKET
    name = f"nr4a-pdyn-{target.lower()}{'-smoke' if smoke else ''}"
    result_s3 = f"s3://{b}/{RESULT_PREFIX}/{name}"
    env = {
        "TARGET": target, "MODE": mode,
        "METAD_NS": f"{m_ns:g}", "RELEASE_NS": f"{r_ns:g}", "N_REP": str(reps),
        "SEED": os.environ.get("PDYN_SEED", "1"),
        "SEGMENT_NS": os.environ.get("PDYN_SEGMENT_NS", "0.2" if smoke else "20"),
        "GIT_BRANCH": branch,
        "RESULT_S3": result_s3,
        "CKPT_DIR": "/work/ckpt",
    }
    return JobSpec(
        name=name,
        command=["bash", "-lc", _PIPELINE.replace("{repo}", REPO)],
        image=VAST_IMAGE,
        checkpoint_uri=f"{result_s3}/ckpt",
        resume=True,
        resources=resources(exclude=exclude),
        # anti-idle hard cap. 60 ns metad + 3 x 5 ns release on a 4090 is ~5-6 h at this system size; a 3090
        # needs 2.10x that, so the cap has to cover the slow card or a legitimate leg would be torn down.
        max_runtime_s=int(os.environ.get("PDYN_MAX_RUNTIME_S", "3600" if smoke else "43200")),
        env=env,
    )


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Launch matched NR4A paralogue MD ensembles on Vast.ai")
    ap.add_argument("--targets", default=os.environ.get("PDYN_TARGETS", "NR4A1,NR4A2"))
    ap.add_argument("--mode", choices=["real", "smoke"], default=os.environ.get("PDYN_MODE", "real"))
    ap.add_argument("--metad-ns", type=float, default=None)
    ap.add_argument("--release-ns", type=float, default=None)
    ap.add_argument("--n-rep", type=int, default=None)
    ap.add_argument("--exclude-machines", default=os.environ.get("PDYN_EXCLUDE", ""))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    exclude = tuple(x.strip() for x in args.exclude_machines.split(",") if x.strip())
    targets = [t.strip().upper() for t in args.targets.split(",") if t.strip()]
    backend = get_backend("vast")
    launched = []
    used_machines = set(exclude)
    for tgt in targets:
        spec = build_jobspec(tgt, mode=args.mode, metad_ns=args.metad_ns, release_ns=args.release_ns,
                             n_rep=args.n_rep, exclude=tuple(used_machines))
        print(f"[launch] {spec.name}: image={spec.image} metad={spec.env['METAD_NS']} ns "
              f"release={spec.env['RELEASE_NS']} ns x {spec.env['N_REP']} result={spec.env['RESULT_S3']}")
        if args.dry_run:
            print(json.dumps({"name": spec.name, "image": spec.image, "env": spec.env,
                              "resources": spec.resources.__dict__,
                              "checkpoint_uri": spec.checkpoint_uri,
                              "max_runtime_s": spec.max_runtime_s}, indent=2))
            continue
        h = backend.submit(spec)
        mid = str(h.extra.get("machine_id"))
        # Never stack two legs of the same fleet on one machine: a host advertising slots it cannot
        # schedule accepts both rentals and then answers resources_unavailable for each (observed
        # 2026-07-25, machine 53989).
        if mid and mid != "None":
            used_machines.add(mid)
        print(f"[launch] {spec.name}: instance={h.job_id} machine={mid} offer={h.extra.get('offer')} "
              f"bid=${h.extra.get('bid')} floor=${h.extra.get('min_bid')} dph=${h.extra.get('dph')}")
        launched.append({"target": tgt, "name": spec.name, "instance": h.job_id, "machine_id": mid,
                         "bid": h.extra.get("bid"), "min_bid": h.extra.get("min_bid"),
                         "result_s3": spec.env["RESULT_S3"]})
    if launched:
        print(json.dumps({"launched": launched}, indent=2))


if __name__ == "__main__":
    main()
