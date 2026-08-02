#!/usr/bin/env python3
"""Ternary cooperativity FEP — Vast.ai lane (RUNG 2b: the 4 fs adoption test, and every ternary leg after it).

WHY THIS LANE EXISTS
--------------------
trimcrae's 2026-07-25 directive is that **all production GPU runs go on Vast**. Until now the ternary
cooperativity FEP had exactly two execution paths — `gpu-ternary-fep-gcp.yml` (the L4 lane valB_mini ran
on, pinned to a 1-GPU quota) and a dormant SageMaker one — plus a *script-shaped* Vast path buried in
`nrv04_vast_launch.py firm`, which rents one host, runs a 60-iteration timing probe, and has no
checkpoint/resume, no stage/pre-equil cache, no reap policy and no watchdog. None of that is a lane you
can put a 10-hour science leg on.

This module is that lane. It is deliberately modelled on `protfep_vast_launch.py`, whose selection, bid,
reap and blocked-machine policies were paid for in real money on 2026-07-24/25; where a policy already
exists there, this file imports it rather than writing a second copy that can disagree.

WHAT IT RUNS, AND WHY THE INVOCATION LOOKS LIKE THAT
---------------------------------------------------
One Vast instance == one alchemical leg, via `run_ternary_leg.sh` — the single-source-of-truth recipe.
This file must NEVER re-implement that invocation: a hand-copied duplicate is precisely what made the
last Vast ternary attempt run 16 λ-windows and NaN where the proven recipe uses 12.

The RUNG 2b question is whether ternary production is stable at **4 fs** instead of 2 fs. Iterations are
timestep-independent (OpenFE derives them as production_length / time_per_iteration, and `time_per_iteration`
is fixed), so 4 fs halves the force evaluations *in production*. It does NOT halve the leg: the warmup runs
at 1 fs and its iteration count is derived from the WARMUP integrator's dt, so a 1 ns equilibration is 1e6
steps at either production timestep. See `ternary_cost_model()` below — this is the reason the naive
"~$8.8 -> ~$4.4" halving is optimistic, and the reason this lane measures the two phases separately.

Three flags carry the experiment, all load-bearing:
  use_preequil (implicit here: this lane ALWAYS pre-equilibrates)  — 4 fs held in the runbook's §1c
        demonstration *only because* the physical complex was relaxed by plain MD first. Without it every
        prior attempt died at warmup iteration 1.
  timestep_fs=4.0 / warmup_timestep_fs=1.0                          — the thing under test.
  a dt-keyed commit prefix                                          — OpenFE refuses to resume a checkpoint
        whose protocol timestep differs ("Sampler in checkpoint does not match Protocol settings"), so a dt
        change MUST start clean. Keying the prefix by dt makes that structural rather than a flag someone
        has to remember; there is no `reset_commits` to forget.

CACHES (all S3, all keyed so a wrong-dt or wrong-seed artefact can never be silently reused)
  stagecache/     the RCSB fetch + SMARCA2 homology model + assembly (~15 min)
  preequilcache/  the relaxed complex.pdb + ligands.sdf (~10 min of GPU MD)
  commits/        the per-interval MultiState checkpoints (the science; written by the engine itself)
A preempted leg restores all three and resumes from its last committed iteration.

DE-CONFLICTION. Everything this lane writes lives under a `ternary-vast/` S3 prefix and a `tvast-` Vast
label, and it never touches GCS, so it cannot collide with the GCP ternary lane running concurrently in
another session.
"""

from __future__ import annotations

import calendar
import hashlib
import inspect
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpu_backend import JobSpec, ResourceSpec, _vast_request, get_backend, measured_min_cuda  # noqa: E402
# Pure policy helpers, imported rather than duplicated. `stall_minutes` and
# `_record_is_newer_than_instance` encode two lessons that cost real money on the protfep lane (a frozen
# image pull is only distinguishable from a queued one by how long the SAME status_msg has been showing;
# and a stale `failed` record in S3 will reap a freshly launched host if you do not check whose attempt
# wrote it). Re-deriving them here would mean two policies that can drift apart.
from protfep_vast_launch import (  # noqa: E402
    _record_is_newer_than_instance,
    stall_minutes,
)
# The anti-idle verdict and the "has this box's container ever run" bit, both imported rather than
# re-derived here. `collect` is the only place with the evidence AND the API key, so it is where the verdict
# gets acted on; the reasoning for the verdict itself lives in one module so a second lane cannot grow a
# second, disagreeing definition of "this rental is doing nothing".
import vast_idle_guard as vig                                   # noqa: E402
import ternary_billed_ledger as _tbl                            # noqa: E402
import leg_failure_breaker as lfb                                # noqa: E402
import vast_stopped_resume_measure as _srm                      # noqa: E402
# The ONE table trimcrae reads: name · % done · ETA · $/ns · running-or-stalled-and-why. It lives in its own
# module and is PURE, so the board can be tested without S3, a Vast key or a clock; `collect` supplies the
# facts it already read and prints what comes back. See `inflight_board.__doc__` for why it exists at all —
# the short version is that the board used to be assembled BY HAND out of this job's log every time it was
# reported, which is a second home for every number in it.
import inflight_board as ifb                                    # noqa: E402
import inflight_usd_per_ns as _ifn                              # noqa: E402
from watchdog_policy import container_started_from_phase        # noqa: E402


def _planning_usd_per_ref_gpu_h():
    """The planning $/reference-GPU-hour, READ from the repricing artifact — never typed here.

    CLAUDE.md §1: a total is DERIVED, and the ladder repricing JSON is its one home. Returns None if the
    artifact is unreadable, and the caller then renders `—` rather than a rate nobody can trace.
    """
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "vast-ladder-repricing.json")) as fh:
            return float(json.load(fh)["plan_usd_per_reference_gpu_h"])
    except Exception:  # noqa: BLE001
        return None


def _usd_per_ns_cell(gpu_name, dph_total, is_bid=None):
    """The board's `$/ns` cell for one live host: `$0.005119/ns · 1.50x basis [bid]`, or None.

    Delegates entirely to `inflight_usd_per_ns.row()` — the one home for the rate, its multiple of basis, the
    PAYING/REFUSED distinction and, since 2026-07-31, the TIER. A card that has never been benched yields
    UNKNOWN there and `—` here, which is deliberate: a fabricated figure ranks an offer it cannot price.

    `is_bid` is passed straight through to `tier_of`, which is where "absent is not bid" is decided. This
    function must never test it itself — a truthiness check here would collapse `None` (we did not look) and
    `False` (uninterruptible) into the same branch, and those are opposite answers.
    """
    rate = _planning_usd_per_ref_gpu_h()
    if rate is None or gpu_name is None or dph_total is None:
        return None
    try:
        return _ifn.row(gpu_name, float(dph_total), rate, tier=_ifn.tier_of(is_bid)).get("cell")
    except Exception:  # noqa: BLE001
        return None

REPO = "https://github.com/trimcrae/Rare-cancers"

# NOTE THE `or`, NOT `.get(key, default)`: CI passes an unset workflow input as an EMPTY STRING, which is
# a *set* variable, so a .get() default never fires. That hole once rented a 4090 whose result prefix
# resolved to `s3:///...` and which therefore produced nothing retrievable.
VAST_IMAGE = os.environ.get("TVAST_IMAGE") or "docker.io/triskit23/ternary-fep:latest"
DEFAULT_BUCKET = os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
RESULT_PREFIX = os.environ.get("TVAST_PREFIX") or "ternary-vast"
# The object `_persist` writes LAST, and therefore the only one whose presence proves a generation is
# complete. Named here rather than imported so this module keeps its "no MD stack needed" property; the
# two are pinned equal by tests/test_commit_manifest_name_matches_the_store.py.
COMMIT_MANIFEST = "COMMITTED.json"
LABEL_PREFIX = "tvast"

# Backstops. The reap normally fires on "result in S3"; these bound the pathological cases.
MAX_INSTANCE_HOURS = float(os.environ.get("TVAST_MAX_INSTANCE_HOURS") or "22")
# ★★ DERIVED FROM A MEASUREMENT, NOT FROM ONE INCIDENT (2026-07-28). This was `45`, hard-typed, with no
# derivation anywhere — it is the duration of the single 2026-07-25 incident where a +26 % bid raise left a
# box queued `stopped` for 45 min. n=1, promoted to a policy, and since `teardown_decision.decide()` it also
# governs how long a CAPACITY-REFUSED box is HELD when no replacement clears the buy line, where the
# economics are lopsided: holding costs storage only (~$0.016/hr at the 60 GB this lane requests) while a
# teardown forfeits the staged disk and buys a ~$0.10-0.28 cold start.
# `vast_stopped_resume_measure` mined every committed revision of the fleet census (949 observations of 111
# instances) and measured the missing input, P(a never-started box ever resumes): **15 of 55 episodes
# resumed**, Kaplan-Meier 34 % by 45 min and 61 % by 90 min, with three resumes observed at 87.4, 89.0 and
# 93.0 min — i.e. past the point the old constant destroyed them. The one home of the figure and of the rule
# that derives it is `vast_stopped_resume_measure.hold_minutes()`; `45` survives only as its fallback.
MAX_STOPPED_MIN = float(os.environ.get("TVAST_MAX_STOPPED_MIN") or _srm.hold_minutes(default=45))
MAX_FROZEN_MIN = float(os.environ.get("TVAST_MAX_FROZEN_MIN") or "20")

# HOST SPEC. Setup (openff `interchange` parameterising the ~146k-atom solvated hybrid) is CPU+RAM bound,
# and the GCP lane measured a 4x slowdown on a 16 GB / 4 vCPU box versus 32 GB / 8 vCPU — swapping, not
# GPU. Since this lane builds setup on the rented host (there is no S3 setup cache yet), under-specifying
# RAM buys a cheap host and then pays for it in GPU-idle minutes. min_cuda 13.0 is the repo's settled host
# filter: the baked env's PTX is CUDA-13-class and older drivers hit CUDA_ERROR_UNSUPPORTED_PTX_VERSION.
def resource_spec(gpu=None, disk_gb=None, max_usd_per_ns=None):
    """The host filter for a ternary leg. Kept a function so a caller (or a test) can vary the card
    without mutating a module-level singleton that another call already holds a reference to.

    `max_usd_per_ns` defaults to None — UNSET — because the two callers want opposite things. The GATE must
    see the expensive offers in order to report them and say how far above the line the board sits; only the
    spec handed to `submit` carries the cap. That is `ResourceSpec.max_usd_per_ns`'s own documented contract,
    and setting it here by default would make the gate blind to exactly the offers it exists to price."""
    return ResourceSpec(
        gpu=gpu or os.environ.get("TVAST_GPU") or "rtx4090",
        min_vram_gb=int(os.environ.get("TVAST_VRAM") or "24"),
        vcpus=int(os.environ.get("TVAST_VCPUS") or "8"),
        ram_gb=int(os.environ.get("TVAST_RAM_GB") or "32"),
        disk_gb=int(disk_gb or os.environ.get("TVAST_DISK_GB") or "60"),
        # ★★ MEASURED, NOT TYPED (2026-07-31). Was the constant 13.0 on the strength of a comment claiming
        # the baked env's PTX was CUDA-13-class. `probe_image_cuda.py`, run inside `VAST_IMAGE` itself, says
        # nvrtc 12.6 / cudart 12.6 / cuda-version 12.6 — the `cuda-version=12.6` pin DID take. The ablation
        # priced the difference: 119 -> 134 offers surviving and 6.2 % better $/ns, on every read. The whole
        # argument and the artifact are at `gpu_backend.measured_min_cuda`; `TVAST_MIN_CUDA` still overrides.
        min_cuda=float(os.environ.get("TVAST_MIN_CUDA") or measured_min_cuda(VAST_IMAGE)),
        # THE DEADLINE FLOOR. Unset by default — see `ResourceSpec.min_ns_per_h` for why naming a card class
        # could not do this job, and why leaving a floor on standing would quietly replace the lane's cost
        # discipline with a speed preference. Set per-launch, from the workflow's `min_ns_per_h` input, when
        # one leg has become the critical path on a deadline the others are already inside.
        min_ns_per_h=float(os.environ.get("TVAST_MIN_NS_PER_H") or "0"),
        # ★★ THE EVICTION ESCAPE HATCH — `TVAST_ON_DEMAND=1` RENTS THE UNINTERRUPTIBLE TIER (2026-07-30).
        # Vast's community bid tier is interruptible BY DESIGN, and no bid makes it safe: `gpu_backend`
        # records the documented rule that an on-demand renter preempts an interruptible one REGARDLESS of
        # bid. So raising VAST_BID_FLOOR_MULT buys priority within the bid tier and nothing more — it cannot
        # stop the eviction it is aimed at.
        # That distinction stopped being academic on this leg: five hosts in 2.5 hours, none surviving the
        # ~28 min it needs to stage and reach ONE 40-iteration commit boundary, so the census sat at
        # production/1840 all afternoon while every rental was correctly priced and correctly re-placed.
        # When mean host lifetime is below time-to-first-commit, faster recovery cannot converge — only a
        # host that cannot be taken away can.
        # ⚠ IT IS OFF BY DEFAULT AND MUST STAY OFF. On-demand costs multiples of the bid floor, and the whole
        # ladder is built on interruptible pricing plus per-unit checkpointing; standing on-demand would
        # quietly rewrite the cost model. This is for a single leg that is the critical path, and the $/ns
        # buy line still applies to it unchanged — an on-demand offer over the line is REFUSED like any
        # other, which is the point: it converts "we cannot keep a host" into a priced question.
        interruptible=not (str(os.environ.get("TVAST_ON_DEMAND") or "").strip().lower()
                           in ("1", "true", "yes")),
        max_usd_per_ns=max_usd_per_ns,
    )


# =============================================================================================================
# unit planning — PURE (no network, no AWS); this is what the tests exercise
# =============================================================================================================
# A "unit" is one (leg, seed, direction) at one timestep pair. `probe` is the RUNG 2b stage-1 survival test;
# `edge` is stage 2, the full matched re-calibration edge.
#
# WHY THE PROBE USES A SHORT WARMUP. The question stage 1 asks is "does 4 fs production survive well past the
# 40 iterations the runbook demonstrated?", and warmup is 1 fs — it tests nothing about the production
# timestep while costing ~3.5 GPU-hours. Cutting it to 48 iterations reproduces exactly the warmup length of
# the runbook's §1c demonstration (48/48) and makes the probe a STRICTLY HARSHER test of 4 fs than the full
# leg: less equilibrated coordinates entering production. A pass therefore carries over; a fail is
# unambiguous. Stage 2 runs the full derived warmup, matched to the 2 fs run.
#
# WARMUP CHECKPOINT INTERVAL, and why it is per-mode rather than a constant. A checkpoint costs a reporter
# sync plus an ~25 MB .nc/.chk pair copied and PUT to S3, so its cost is fixed per commit while the MD
# between commits is `interval x seconds-per-iteration`. The GCP lane's 8 was chosen against a 2 fs
# warmup; at 4 fs the derived warmup is ~1600 iterations (n_steps per iteration halves, so covering the
# same 1 ns takes twice as many of them), and an interval of 8 would mean ~200 commits — plausibly a
# double-digit percentage of the leg spent committing. `edge` therefore uses 64 (1600/64 = 25 commits,
# first resumable snapshot ~8 min in, which is still far inside a preemption window). `probe` keeps 8,
# both because 48 iterations must stay a multiple of the interval and because a short interval is exactly
# what MEASURES the commit overhead — the probe is where that number comes from rather than a guess.
MODES = {
    "probe": {
        "prod_iters": "200", "warmup_iters": "48", "warmup_ckpt_iters": "8", "prod_ckpt_iters": "40",
        "max_runtime_s": 4 * 3600,
        "legs": [("calib_hi_to_lo__ternary_vhl", 0, "fwd")],
    },
    "edge": {
        "prod_iters": "", "warmup_iters": "",          # empty = full derived science length
        "warmup_ckpt_iters": "64", "prod_ckpt_iters": "40",
        "max_runtime_s": 20 * 3600,
        "legs": [("calib_hi_to_lo__ternary_vhl", 0, "fwd"),
                 ("calib_hi_to_lo__binary_vhl", 0, "fwd"),
                 ("calib_hi_to_lo__solvent", 0, "fwd")],
    },
    # A 12-iteration end-to-end shakeout: proves image + repo pull + stage + pre-equil + setup + commit-store
    # + upload on a real host for ~$0.15, before a real leg is paid for. Its dG is meaningless by construction.
    "smoke": {
        "prod_iters": "12", "warmup_iters": "8", "warmup_ckpt_iters": "8", "prod_ckpt_iters": "4",
        "max_runtime_s": 3 * 3600,
        # See SHAKEOUT_EVIDENCE_MAX_AGE_H: this mode's product is an OBSERVATION about today, not a result,
        # so a stale `done` record must not suppress a re-run the way a production unit's correctly does.
        "shakeout": True,
        "legs": [("calib_hi_to_lo__ternary_vhl", 0, "fwd")],
    },
    # ---------------------------------------------------------------------------------------------------
    # valB_mini REPLICATES r1 + r2 — the two independent seeds the frozen gate needs before it can return
    # anything but INDETERMINATE. Seed 0 alone gives n=1, and `calibration_gate` refuses n<2 outright:
    # "need >=2 independent replicates for a cycle SD."
    #
    # ⚠ FOUR LEGS, NOT SIX — AND THE MISSING TWO ARE A CORRECT SAVING, NOT A CORNER CUT. Read
    # `ternary_fep_reduce.per_replicate_ddg_coop`: it pairs legs BY SEED and forms
    # ΔΔG_coop(r) = ΔG_ternary(r) − ΔG_binary(r). The solvent morph enters ΔΔG_alch,binary and
    # ΔΔG_alch,ternary with the SAME sign and therefore cancels EXACTLY inside each replicate's cycle, so a
    # per-replicate solvent leg contributes nothing to ΔΔG_coop and nothing to the between-replicate cycle SD
    # the gate reads. One solvent leg already exists at seed 0 for the full-cycle summary (`coop_for_morph`).
    # Buying two more would be two full rentals spent on a term that algebraically drops out.
    #
    # ⚠⚠ AND FOUR LEGS, NOT TWO — THE MATCHED BINARY LEGS ARE LOAD-BEARING, NOT OPTIONAL (2026-07-27, ruling
    # on the proposal to buy TERNARY-ONLY replicates because the binary arm is contaminated).
    #
    # The proposal was reasonable on its face: audit §L.3c shows the unrestrained binary arm's ligand departs
    # irreversibly (8 of 12 replicas at 16.6 Å, 7 of 8 initiating in the interior), a restrained re-run is
    # already live, and replicating a number we have decided is bad looks like waste. It is refused anyway,
    # for a reason that is in the code rather than in a judgement call:
    #
    #   `ternary_fep_reduce.per_replicate_ddg_coop` computes `seeds = set(ternary) & set(binary)` and returns
    #   ΔΔG_coop(r) = ΔG_ternary(r) − ΔG_binary(r) over that INTERSECTION. Drop the binary legs and the
    #   intersection stays {0}, n_paired = 1, and `calibration_gate` returns the SAME
    #   "need >=2 independent replicates for a cycle SD" INDETERMINATE it returns today. **A ternary-only
    #   replicate set does not move the verdict one step.** The gate's quantity is the CYCLE, not the arm.
    #
    # And the SD a ternary-only set would produce is not merely insufficient, it is BIASED LOW in the one
    # direction that matters: for independent seeds σ_cycle² = σ_ternary² + σ_binary², and the arm expected to
    # dominate σ is precisely the contaminated one — a ligand that leaves in 8 of 12 replicas is a large
    # seed-to-seed variance term. Reporting σ_ternary as though it were the cycle's error bar is the
    # fake-tight-SD failure wearing different clothes.
    #
    # What the matched pair BUYS, stated so it is not mistaken for replicating a bad number: the deliverable
    # is σ_cycle, not another ΔΔG_coop point estimate. σ_cycle is the direct measurement of σ_leg, which
    # `valb_triangle_closure.binary_departure_prereg` currently knows only to a factor of ~15 and on which its
    # own power statement (~0.22 at σ_leg = 0.5) depends. One lane's error bar is another lane's power
    # analysis. The point estimate remains uninterpretable until the restrained re-run lands, and nothing here
    # claims otherwise.
    #
    # SEEDS ARE INDEPENDENT TRAJECTORIES — AND THE HOMOLOGY POSE IS NOT FULLY RESAMPLED AT n=3. MEASURED,
    # 2026-07-27, because this comment previously asserted the strong form and the strong form is false.
    # SEED keys four things: the sampler (`nr4a3_ternary_fep` sets simulation/integrator `random_seed` =
    # SEED, so 0/1/2 are genuinely different velocity/sampler streams), the pre-equilibration cache, the
    # commit prefix, and `rbfe_spot_checkpoint.SYSTEM_FINGERPRINT_ENV` — which LISTS "SEED", so a re-used seed
    # cannot silently resume into another replicate's trajectory. That much holds for every leg, both arms.
    #
    # ⚠ BUT the stage cache is the exception, and it is a REAL limitation of the n=3 cycle SD.
    # `ternary_pdb_stage` builds the SMARCA2 homology ensemble with **n_models=2** and takes
    # `starting_model_index = seed % len(model_pdbs)`. So: seed 0 -> model 0, seed 1 -> model 1,
    # **seed 2 -> model 0 again, the same relaxed pose r0 started from.** Reviewer condition #3 ("each ternary
    # REPLICATE uses an INDEPENDENTLY relaxed SMARCA2 model, so a coop result is not an artifact of one
    # homology pose") is therefore met for 2 of the 3 ternary replicates and not the third, and the cycle SD
    # UNDERSTATES the homology-model component of the variance. Note the binary arm is untouched by this —
    # it stages E3 machinery only, with no SMARCA2 model at all, so its three seeds differ by sampler stream
    # and nothing else.
    #
    # NOT FIXED IN FLIGHT, deliberately. Rebuilding with n_models=3 re-relaxes the ensemble, so "model 0"
    # would no longer be the pose r0 and r1 were computed on — the fix would break comparability with the two
    # replicates that already exist in order to improve the third. It is recorded here, reported with the SD,
    # and pinned by `tests/test_edge_reps_seed_independence.py` so the claim cannot silently drift back to the
    # strong form. It becomes decision-relevant only if `calibration_gate` returns BORDERLINE and takes its
    # "extend to 5 replicates" branch, at which point seeds 3 and 4 would land on models 1 and 0 and the
    # ensemble genuinely does need widening BEFORE that round is bought.
    #
    # RUN IN PARALLEL, ALL FOUR AT ONCE. The litmus test from CLAUDE.md §6 — "is there a result this shard
    # could return that would make me NOT run the rest?" — answers NO here: the deliverable is a cycle SD
    # ACROSS seeds, so r1 is not decision-relevant without r2. Serialising would buy zero decision value at
    # identical GPU-$.
    "edge_reps": {
        "prod_iters": "", "warmup_iters": "",          # empty = full derived science length, matched to r0
        "warmup_ckpt_iters": "64", "prod_ckpt_iters": "40",
        "max_runtime_s": 20 * 3600,
        # STRICT PROVENANCE, and only here. `fingerprint_mismatch_reason` accepts an UNSTAMPED committed
        # generation unless this is set, because refusing one would make any leg ALREADY RUNNING with
        # pre-stamping generations throw away paid GPU hours on its next preemption. These units' commit
        # prefixes do not exist yet, so every generation they ever restore will have been written by the
        # same configuration that stamps it — the concession has nothing to buy here, and turning it off
        # closes the "resume silently accepted a generation from another configuration" hole for free.
        # Scoped per-mode rather than lane-wide precisely so it cannot refuse another lane's live resume.
        "strict_provenance": True,
        # ★★ PER-ARM CHECKPOINT CADENCE, DERIVED — see `warmup_ckpt_iters_for`. The `64` above is the
        # REFERENCE arm's (binary) interval and the ternary arm gets its own, finer, computed one, so that
        # both arms lose the SAME NUMBER OF SECONDS to a host reclaim rather than the same number of
        # iterations. Opt-in per mode, so this cannot silently re-cadence a lane nobody measured — `edge`
        # (seed 0, already DONE) and `5aks` stay byte-identical to what they ran with.
        "per_arm_ckpt": True,
        "legs": [("calib_hi_to_lo__ternary_vhl", 1, "fwd"),
                 ("calib_hi_to_lo__binary_vhl", 1, "fwd"),
                 ("calib_hi_to_lo__ternary_vhl", 2, "fwd"),
                 ("calib_hi_to_lo__binary_vhl", 2, "fwd")],
    },
    # ---------------------------------------------------------------------------------------------------
    # RUNG 5a-KS — the ligand-side causal kill-switch. S = dG_tern(NR4A3) - dG_tern(NR4A1) over the RUNG-5b
    # matched pair (phenyl d0 -> 3-pyridyl d at T407). TWO ternary legs, and only two: the binary and
    # solvent legs are paralogue-independent and cancel ALGEBRAICALLY out of the double difference
    # (nr4a3_5aks_reduce refuses one if it ever appears).
    #
    # ⚠ THESE LEGS DO NOT STAGE FROM A CRYSTAL. There is no PDB entry for a CRBN + NR4A-LBD + this-construct
    # ternary — the whole point of the rung is that it does not exist. Their inputs are built by
    # `nr4a3_5aks_stage.py` from a Boltz-2 co-fold on a free CI runner and PRE-SEEDED into this lane's
    # stage cache, so the on-host `stage` phase is a cache HIT and `ternary_pdb_stage.py` (RCSB, crystal
    # templates, SMARCA2 homology modelling — none of which applies here) is never reached. `template_pdb`
    # is therefore a CACHE-KEY LABEL, not a PDB id, and `stage_required` makes a cache MISS a hard failure
    # rather than a silent fall-through into the crystal stager.
    "5aks": {
        "prod_iters": "", "warmup_iters": "",          # empty = full derived science length
        # ★★ WARMUP INTERVAL HALVED 64 -> 32 (trimcrae, 2026-07-31). THE MEASUREMENT THAT JUSTIFIES IT, and
        # it is not the one this lane spent the day chasing. Container start -> `md-running` is **0.3-0.6
        # min** on all four legs (phase.txt's own timestamp against the log's `start`) — MD begins within ~30
        # seconds because all three caches hit. The "~28 min cold start" everyone quoted is TIME TO FIRST
        # COMMIT, and it is one checkpoint interval of MD:
        #     nr4a3_r0  64 x 33.5 s/iter = 35.7 min      nr4a1_r0  64 x 18.3 = 19.5 min
        #     nr4a3_r1  64 x 31.1 s/iter = 33.1 min      nr4a1_r1  64 x 17.8 = 19.0 min
        # Against a ~1.00 h median session, a 3090 leg at 64 needs ~60 % of a whole rental to bank ANYTHING —
        # a coin flip whether a rental produces a checkpoint at all. At 32 that is ~30 %.
        # STRATEGY Appendix A 62 registers the retracted "cold start" reading.
        #
        # ⚠ NEW LEGS ONLY, AND THE RUNNING FOUR ARE UNTOUCHED — this is not a policy, it is arithmetic:
        # `rbfe_spot_checkpoint` fixes the interval when the .nc is CREATED and `effective_interval` prefers
        # the committed manifest, using the env only as a last-resort fallback for pre-2026-07-21 files. The
        # four in-flight legs sit on 64-grids (1088/1152/1536 warmup, 1400 production) and keep them.
        # Pinned by `tests/test_ckpt_cadence_is_new_legs_only.py`, which fails if a running leg's grid could
        # move. Breaking their resume validation would cost 91 %, 58 %, 43 % and 41 % of four legs.
        #
        # ⚠ 32 DIVIDES THE TARGET, WHICH 64 DOES NOT ALWAYS. `warmup_target_iters(4.0, 1.0)` is 1600 and
        # 1600/32 = 50 exactly. (At 2 fs the target is 800 and 800/64 = 12.5 — the triangle's flat 64 is
        # ALREADY off-grid, a pre-existing gap pinned as `KNOWN_DIVISIBILITY_GAP`; 32 would close it, and it
        # is deliberately NOT changed here because that lane is finished.)
        #
        # ⚠ NOT the per-arm derivation (`per_arm_ckpt` is unset for this mode and stays unset) — the rate
        # table's card ratios are not trustworthy enough to cadence off, and that is a separate open item.
        # ⛔⛔ AND THEN REVERTED TO 64 THE SAME EVENING, ON THE MEASUREMENT THE APPROVAL WAS CONDITIONED ON.
        # trimcrae's instruction was explicit: *"Price the upload, do not assume it … If the write is slow
        # enough that 32 costs more in pauses than it saves in banked work, say so and stop; the arithmetic
        # above assumes the write is cheap and I have not verified that."* It is not cheap.
        #
        # WHAT THE REAL S3 OBJECTS SAY (`setup-tax-5aks.json`, measured 7:25 PM ET, 158 committed
        # generations across the four legs). The `.nc` is CUMULATIVE — every commit re-uploads the whole
        # trajectory so far, so the payload is a curve, not a constant:
        #     nr4a3_r0   iter   40 =  76.3 MiB  ->  iter 1720 = 5461.8 MiB   (72x)
        #     nr4a1_r1   iter   64 = 106.6 MiB  ->  iter 1600 = 1353.7 MiB
        #     nr4a1_r0   iter   64 = 105.6 MiB  ->  iter 1600 = 1341.3 MiB
        #     nr4a3_r1   iter   40 =  77.0 MiB  ->  iter 1600 =  984.4 MiB
        # Median across all generations: **699.5 MiB per commit** — 28x the "~25 MB .nc/.chk pair" that
        # `COMMIT_OVERHEAD_S = 23.0` was measured on, which makes that constant stale by a large factor.
        #
        # WHY THAT KILLS THE TRADE. Halving the interval doubles the NUMBER of commits while each one carries
        # the cumulative payload, so total upload roughly DOUBLES (~17.5 GiB more per leg over warmup alone).
        # A late-warmup commit is ~1.3 GiB; against 32 x 18.3 s/iter = 586 s of MD between commits, any
        # upload slower than ~30 s puts the overhead past this lane's OWN tolerance,
        # `MAX_COMMIT_OVERHEAD_FRAC = 0.05` — and at 1.3 GiB that is nearly certain.
        #
        # ⚠ REVERTING COSTS NOTHING RIGHT NOW, which is why this is the safe direction. The four legs in
        # flight resume on the 64-grids baked into their own .nc files whatever this value says
        # (`effective_interval`), so 32 was INERT for the current campaign and would only have applied to a
        # genuinely fresh leg. No banked work is affected either way.
        #
        # WHAT WOULD SETTLE IT: `rbfe_spot_checkpoint.commit` now self-times and prints
        # `[barrier] commit <phase>@<iter> persisted N MiB in Ns`, and `setup_tax` parses it into
        # `commit_cost`. One re-placement produces the number. If the pause turns out small against the MD
        # between commits, 32 becomes correct and this comment is the evidence trail for re-applying it.
        #
        # ★ AND THE LARGER PRIZE THIS UNCOVERED: a commit that re-uploads the entire trajectory every time
        # makes total bytes O(n^2) in the number of commits. That, not the interval, is the expensive
        # property — and fixing it would make a SHORTER interval nearly free.
        # SUPERSEDED, retained: the 2026-07-31 change to `"32"`.
        "warmup_ckpt_iters": "64", "prod_ckpt_iters": "40",
        "max_runtime_s": 20 * 3600,
        "template_pdb": "boltz5aks",
        "stage_required": True,
        # ★★ FOUR LEGS — n = 2 SEEDS PER ARM (trimcrae go, 2026-07-30; STRATEGY Open decision 11). At ONE seed
        # per arm `S` has no replicate SD at all and resolves only the TOP of its own designed 0.5-1.5 kcal/mol
        # effect (valb_failure_propagation.s_error_bar_scope), so the PRE-REGISTERED LIKELY OUTCOME — a null —
        # would have been uninterpretable, which is valB_mini's n=1 defect on the lane that was meant to have
        # learned it. The second seed is what turns a null into a BOUND.
        #
        # ⚠ THE SEEDS ARE INDEPENDENT SAMPLING, NOT INDEPENDENT STRUCTURES, AND THAT IS BY DESIGN. The
        # `starting_model_index = SEED % n_models` wrap that makes valB's seeds different STRUCTURES lives in
        # `ternary_pdb_stage` behind `target_acc == "P51532"` (the SMARCA4 template) and cannot reach this
        # lane, which stages from ONE co-fold per species on purpose (`nr4a3_5aks_stage`: both endpoints from
        # one pose, so the alchemical transformation does not absorb a pose difference). `nr4a3_ternary_fep`
        # seeds each replica's sampler, so seed 1 is a genuinely independent trajectory from the same start.
        # Consequence to declare rather than hide: an `S` replicate SD measures sampling scatter WITHIN one
        # co-fold pose, and the pose stays a stated conditional.
        #
        # Seed 0's two legs are PARKED with intact checkpoints and resume byte-identically — nothing above
        # them changed (`per_arm_ckpt` is still off for this mode, deliberately). Seeds 1 are cold starts.
        "legs": [("5aks_d0_to_d__ternary_nr4a3", 0, "fwd"),
                 ("5aks_d0_to_d__ternary_nr4a1", 0, "fwd"),
                 ("5aks_d0_to_d__ternary_nr4a3", 1, "fwd"),
                 ("5aks_d0_to_d__ternary_nr4a1", 1, "fwd")],
    },
    # A 12-iteration end-to-end shakeout of the 5a-KS legs specifically: proves the pre-seeded stage cache,
    # the co-fold-derived complex.pdb, the aza-scan endpoint build and the commit store all work on a real
    # host for ~$0.15 before the ~$12 pair is bought. Same plumbing-shakeout ladder as `smoke` -> `edge`.
    "5aks_smoke": {
        "prod_iters": "12", "warmup_iters": "8", "warmup_ckpt_iters": "8", "prod_ckpt_iters": "4",
        "max_runtime_s": 4 * 3600,
        "template_pdb": "boltz5aks",
        "stage_required": True,
        # ⚠ THIS IS THE MODE THE STALE-CERTIFICATE DEFECT WAS MEASURED ON — see SHAKEOUT_EVIDENCE_MAX_AGE_H.
        "shakeout": True,
        "legs": [("5aks_d0_to_d__ternary_nr4a3", 0, "fwd")],
    },
    # ---------------------------------------------------------------------------------------------------
    # THE valB SYNTHETIC CLOSURE TRIANGLE — 4 NEW LEGS, and the third edge is FREE because r0 IS T1.
    #
    # WHAT IT BUYS, and it is the only thing on this lane that buys it: the closure residual
    #     R = ddG_coop(T1) + ddG_coop(T2) - ddG_coop(T3)
    # is IDENTICALLY ZERO for any error that is a function of the endpoint STATE — force field, the
    # SMARCA4->SMARCA2 homology substitution, NAGL charges, protonation — because each of those is a
    # per-endpoint bias eps(x) and sum_cycle [eps(B)-eps(A)] telescopes to exactly zero
    # (`valb_triangle_closure.state_function_blindness`, demonstrated to 3.6e-15 over 2000 draws). R is
    # non-zero ONLY for PATH error. So R decides whether r0's 1.478 kcal/mol miss is fixable by sampling at
    # all.
    #
    # ⚠ AND THE MAPPING RUNS THE OTHER WAY FROM WHAT THIS COMMENT USED TO SAY (corrected 2026-07-27; the
    # retired sentence was "R ~ 0 says the miss is path error and therefore fixable by sampling; R materially
    # non-zero says otherwise", which contradicted the three lines directly above it):
    #
    #   * R ~ 0                  -> the error is a function of the endpoint STATE. It telescopes out of any
    #                               cycle, so it is invisible to R *because* it is not a path error, and
    #                               MORE SAMPLING WILL NOT FIX THE MISS.
    #   * R materially non-zero  -> a PATH error, the one thing R can see, and therefore the case where the
    #                               miss IS fixable by the protocol changes that address it.
    #
    # That is a discriminating experiment, not a confirmation, which is why it is worth buying. One home for
    # the mapping in prose: nr4a3-program-map.md's IN FLIGHT board, "WHAT R DECIDES"; the retraction is Appendix A 41.
    #
    # ⚠ 2 fs / 1 fs, PINNED BY THE MODE, NOT INHERITED FROM THE LANE. r0 is a 2 fs leg and this lane's
    # default is RUNG 2b's 4 fs. `build_jobspec` resolves the timestep mode-first for exactly this reason:
    # the workflow exports TVAST_TIMESTEP_FS lane-wide, so an env-first order would silently buy a 4 fs
    # triangle around a 2 fs T1, and R would then measure the TIMESTEP difference. Same argument as the
    # binary legs running UNRESTRAINED (`valb_triangle_legs`): anything that makes T2/T3's protocol differ
    # from T1's converts R from a path-error detector into a protocol-difference detector, which destroys
    # the experiment's only claim.
    #
    # ⚠ SEED 0 ON ALL FOUR, matching r0. Ternary seed s selects the s%n-th relaxed SMARCA2 model, so a
    # mixed-seed triangle is computed on different Hamiltonians, the edges stop sharing endpoint states, and
    # |R| becomes a homology-model sensitivity measure (`valb_triangle_closure.same_seed_requirement`).
    #
    # ⚠ NO SOLVENT LEGS. The solvent morph enters ddG_alch,ternary and ddG_alch,binary with the SAME sign and
    # cancels EXACTLY inside ddG_coop, so a triangle whose deliverable is R needs 2 legs per edge, not 3.
    # `expand_pilot_legs()` would add one per morph unconditionally — ~$1.31 of legs that algebraically drop
    # out (`valb_triangle_closure.leg_accounting`). They are simply not listed here.
    #
    # FAN OUT ALL FOUR AT ONCE. CLAUDE.md §6's litmus test — "is there a result this shard could return that
    # would make me NOT run the rest?" — answers NO: R needs all six legs, so no single one is decision-
    # relevant alone. Serialising would buy zero decision value at identical GPU-$.
    "triangle": {
        "prod_iters": "", "warmup_iters": "",          # empty = full derived science length, matched to r0
        "warmup_ckpt_iters": "64", "prod_ckpt_iters": "40",
        "max_runtime_s": 20 * 3600,
        "timestep_fs": "2.0", "warmup_timestep_fs": "1.0",
        # Same reasoning as edge_reps: these commit prefixes do not exist yet, so every generation they will
        # ever restore was written by the configuration that stamps it. The concession has nothing to buy
        # here, and turning it off closes the "resume accepted a generation from another configuration" hole.
        "strict_provenance": True,
        "legs": [("calib_lo_to_lo2__ternary_vhl", 0, "fwd"),
                 ("calib_lo_to_lo2__binary_vhl", 0, "fwd"),
                 ("calib_hi_to_lo2__ternary_vhl", 0, "fwd"),
                 ("calib_hi_to_lo2__binary_vhl", 0, "fwd")],
    },
    # The plumbing shakeout for the triangle, at the SAME 2 fs the real legs run: proves image + repo pull +
    # stage + pre-equil + the DOUBLE-swap endpoint build + setup + commit store + upload on a real host for
    # ~$0.15. It runs T3's TERNARY leg specifically — the CLOSING edge, whose cmpd1 -> cmpd4" endpoint is the
    # ring-nitrogen 1,2-shift that no single-atom swap can build. If the new pose path is broken, that is the
    # leg it breaks on, so the shakeout is aimed at the one thing this rung added rather than at plumbing
    # three earlier rungs already proved.
    "triangle_smoke": {
        "prod_iters": "12", "warmup_iters": "8", "warmup_ckpt_iters": "8", "prod_ckpt_iters": "4",
        "max_runtime_s": 3 * 3600,
        "timestep_fs": "2.0", "warmup_timestep_fs": "1.0",
        # See SHAKEOUT_EVIDENCE_MAX_AGE_H. This one had already landed (2026-07-27T22:56:27Z), so it was
        # equally unable to re-run and equally unable to say so.
        "shakeout": True,
        "legs": [("calib_hi_to_lo2__ternary_vhl", 0, "fwd")],
    },
}

# Modes whose spend band comes from `valb_triangle_closure.price_triangle()` rather than from the ladder
# JSON. Per CLAUDE.md rule 1 the triangle's price has exactly ONE home and it is that function: the ladder
# carries no triangle rung, and adding one would give the same fact two homes free to disagree.
TRIANGLE_MODES = ("triangle", "triangle_smoke")

# =============================================================================================================
# EVERY LAUNCHABLE MODE'S RE-PLACEMENT GATE — ONE HOME, AND A MODE CANNOT BE ADDED WITHOUT DECIDING
# =============================================================================================================
# ★★ THE DEFECT THIS CLOSES, MEASURED 2026-07-31. `5aks_d0_to_d__ternary_nr4a3_r0` lost its host to a capacity
# refusal on machine 145841 at ~7:5x AM ET. The lane behaved correctly in every respect but one: it destroyed
# the box, stopped billing, kept the checkpoint at `production/840`, and printed
#     "…this pass dispatches the gate to re-place it"
# — and then dispatched nothing, because there was no gate for `5aks` to dispatch. The re-placement map was a
# hardcoded shell `case` in the collect job reading
#     triangle|triangle_smoke) TASK=triangle-gate ;;  edge_reps) TASK=market-gate ;;
#     *) echo "::warning title=NO GATE FOR MODE::…"; continue ;;
# so the mode that was actually running that day fell through to a `::warning::` nobody was awake to read.
# The ledger proves the consequence: the 7:39, 7:47 and 7:55 AM ticks each recorded a `market-gate` and a
# `triangle-gate` evaluation and no 5aks one at all. The leg would have sat stranded overnight with an intact
# checkpoint and nothing looking for a host for it.
#
# ⚠ WHY IT IS A MAP IN PYTHON AND NOT A `case` IN YAML. Two hardcoded lists — the shell `case` here and the
# supervisor's tick loop — had to be edited in lockstep with `MODES` and neither was checked against it, which
# is the same shape as NR-V04's `AUTHORIZED_STAGES` prose-vs-code split. A mode that can be LAUNCHED but not
# RE-PLACED is a trap: it works until the first preemption and then silently stops being a lane. So the map
# lives beside `MODES`, `gate_task_for` is its only reader, and `tests/test_mode_gate_coverage.py` fails the
# build if a launchable mode appears in neither dict below.
#
# ⚠ AND THE GATE MUST PRICE THE SAME MODE. A map entry is a claim that dispatching that task prices THESE
# units: `market-gate` runs `--mode edge_reps`, `triangle-gate` runs `--mode triangle`, `5aks-gate` runs
# `--mode 5aks`. Pointing a mode at a gate that prices a different unit set would produce a green tick that
# re-places nothing — the failure being fixed, wearing a map entry as a disguise.
MODE_GATE_TASK = {
    "edge_reps": "market-gate",
    "triangle": "triangle-gate",
    # A smoke maps to its parent mode's gate. This is the ESTABLISHED idiom (triangle_smoke has done so since
    # the triangle gate existed) and its known limit is recorded rather than quietly fixed: if the parent's
    # units are all done the gate exits 3 "nothing to launch" and the shakeout is not re-placed. That is
    # acceptable for a ~$0.15 one-shot whose loss costs a re-dispatch, and unacceptable for a science leg —
    # which is exactly why the science modes above each have a gate that prices their own units.
    "triangle_smoke": "triangle-gate",
    "5aks": "5aks-gate",
    "5aks_smoke": "5aks-gate",
}

# Launchable modes that deliberately have NO autonomous re-placement, each with the reason. Being in this
# dict is a DECISION, not an omission — the coverage test accepts a mode here or in the map above and
# rejects it in neither, so adding a mode to `MODES` forces the question to be answered.
NO_AUTOMATIC_REPLACEMENT = {
    "probe": "RUNG 2b stage 1, landed 2026-07-26 and never to be re-bought — a gate here could only re-rent "
             "a finished result. There is no live unit for it to re-place.",
    "edge": "RUNG 2b stage 2, all three legs landed. Same as `probe`: finished, not parked.",
    "smoke": "the RUNG 2b shakeout, landed. Its parent `edge` is finished too, so a gate would have nothing "
             "to price; a re-run is a deliberate hand dispatch (and now re-runnable — see "
             "SHAKEOUT_EVIDENCE_MAX_AGE_H).",
}


# ★★ THE TERMINUS OF A MODE IS ITS REDUCTION, AND NOTHING WAS ARMING IT (2026-08-01).
#
# WHAT WAS MISSING. `collect` already notices when a leg lands — it retires the landed unit's watch entry on
# the same pass. What it did NOT do is notice when the LAST leg of a mode lands, which is the only moment
# that matters scientifically: RUNG 5a-KS's readout S is a DOUBLE DIFFERENCE over four legs, so three landed
# legs are worth nothing and the fourth is worth the whole rung. Until now the reduction fired only when a
# person remembered to dispatch `task=5aks-reduce`. A rung whose terminus depends on somebody being awake at
# the right minute is a rung that sits finished-but-unreduced, and the four legs of this one land ~20 hours
# apart — the last of them overnight.
#
# SAME SHAPE AS `MODE_GATE_TASK`, DELIBERATELY. A hardcoded shell `case` for the gate is what stranded a
# 5a-KS leg on 2026-07-31, so this is a map beside that one, covered by the same style of test: a launchable
# mode must appear here or in NO_AUTOMATIC_REDUCTION, and never in neither.
MODE_REDUCE_TASK = {
    "edge": "reduce",
    "edge_reps": "reduce-reps",
    "triangle": "triangle-reduce",
    "5aks": "5aks-reduce",
}

# Launchable modes with no reduction of their own, each with the reason. A SHAKEOUT IS THE INTERESTING CASE:
# a smoke leg writes a real `leg.json` with a real dG (the 5a-KS smoke's is -9.24 kcal/mol), so "this mode is
# complete" is TRUE of a smoke the moment its one leg lands — and reducing it would form a rung's readout out
# of 12 production iterations. The refusal is therefore about scientific validity, not about plumbing.
NO_AUTOMATIC_REDUCTION = {
    "probe": "a survival test, not a measurement: it asks whether 4 fs holds, and its dG is read by eye "
             "against the edge that follows. There is no double difference to form from one probe leg.",
    "smoke": "a shakeout. Its leg.json is real but its sampling is not — reducing it would emit a rung "
             "readout built from a dozen production iterations.",
    "triangle_smoke": "same as `smoke`, for the closure triangle.",
    "5aks_smoke": "same as `smoke`, for RUNG 5a-KS. ⚠ This one is the reason the refusal is explicit: the "
                  "smoke's unit id differs from the science leg's only by its `_smoke` suffix and its "
                  "leg.json carries a genuine-looking dG, so a completeness count that did not exclude it "
                  "would find mode `5aks_smoke` complete after ONE leg and reduce it (CLAUDE.md §4b — a "
                  "record that looks plausible is more dangerous than one that looks empty).",
}


def reduce_task_for(mode):
    """The `task=` that reduces `mode` once every one of its units is done, or None when it has none by
    decision. PURE — same contract and same failure mode as `gate_task_for`, on purpose.
    """
    if mode in MODE_REDUCE_TASK:
        return MODE_REDUCE_TASK[mode]
    if mode in NO_AUTOMATIC_REDUCTION:
        return None
    raise KeyError(
        f"mode {mode!r} has no entry in MODE_REDUCE_TASK and none in NO_AUTOMATIC_REDUCTION. A launchable "
        f"mode must be in exactly one: either landing its last leg fires a reduction, or there is a recorded "
        f"reason it does not. Silence here means a finished rung waits for a hand dispatch.")


# ★★ THE CARD FLOOR IS PER-MODE, AND IT HAS EXACTLY ONE HOME (2026-07-31).
#
# `collect`'s self-heal used to dispatch `-f min_ns_per_h=28` to WHATEVER gate the map returned, so a floor
# argued for the closure triangle was silently applied to RUNG 5a-KS as well — including after trimcrae
# reverted the 5a-KS floor on the supervisor tick. Two dispatchers disagreeing about one lane's card policy is
# how a reverted decision keeps running.
#
# WHY 5a-KS HAS NO FLOOR, and the evidence that settled it: the step 1 fan-out's own 208-rental ledger shows
# 3090-class hosts (<= $0.12/hr) held a **1.50 h median with 62 % over an hour**, against 1.65 h / 67 % for the
# 4090/5090 class. Card class does not predict host lifetime here, so a floor buys narrowness and not
# retention — and trimcrae asked explicitly that 3090s stay in the pool.
#
# WHY THE TRIANGLE KEEPS ITS FLOOR: a different, direct observation — `calib_hi_to_lo2__ternary_vhl` sat at
# production/1720 for over two hours across three hosts and advanced on the very next cycle once it landed on
# a 5090. That is a measurement of THAT unit's interval against THAT card, and it is not transferable.
#
# 0 = unset, which is what `resource_spec` already means by it.
MODE_MIN_NS_PER_H = {
    "triangle": 28.0,
    "triangle_smoke": 28.0,
}


def mode_min_ns_per_h(mode):
    """The card floor a re-placement of `mode` should carry, as a float (0 = none). PURE."""
    return float(MODE_MIN_NS_PER_H.get(mode) or 0.0)


def gate_task_for(mode):
    """The `task=` that re-places a dead host for `mode`, or None when the mode has none by decision. PURE.

    None is a DECISION and the caller must render it as one — `collect`'s self-heal prints the recorded
    reason rather than a bare "no gate", so an operator can tell "nobody thought about this mode" (which
    the coverage test now makes impossible) from "this mode is finished and must not be re-bought".
    """
    if mode in MODE_GATE_TASK:
        return MODE_GATE_TASK[mode]
    if mode in NO_AUTOMATIC_REPLACEMENT:
        return None
    raise KeyError(
        f"mode {mode!r} has no entry in MODE_GATE_TASK and none in NO_AUTOMATIC_REPLACEMENT. A launchable "
        f"mode with no re-placement decision is the 2026-07-31 stranded-leg trap: it runs until its first "
        f"preemption and then silently stops being a lane. Add it to one of the two.")

# ★★ WHICH LEGS THE $0 POSE/CONVERGENCE DIAGNOSTIC ANALYSES — ONE HOME, AND IT IS HERE (2026-07-30).
# `gpu-ternary-fep-vast.yml`'s converge job hardcoded `--mode edge` on its `--fetch-trajectories` call, so
# the diagnostic could only ever look at the RUNG 2b legs. `unit_id` embeds BOTH the timestep and the mode,
# and the closure triangle runs at a pinned 2 fs under mode `triangle`
# (`calib_{lo,hi}_to_lo2__{ternary,binary}_vhl_r0_dt2.0fs_wu1.0_triangle`), so a triangle leg looked up as
# `edge` resolves to `..._dt4.0fs_wu1.0_edge` — a prefix that does not exist. That is exactly the failure
# `resolve_timesteps.__doc__` names: "a mode that ran at 2 fs looked up at 4 fs returns an empty directory,
# and an empty reduction is the 'reports success while measuring nothing' shape this lane keeps paying for."
#
# WHY A TASK->MODE MAP RATHER THAN AN 11th DISPATCH INPUT. GitHub caps `workflow_dispatch` at 10 inputs and
# going over is SILENT — every `-f` then arrives empty (tests/test_workflow_dispatch_input_cap.py, "the most
# expensive hour of 2026-07-30"). This lane sits at exactly 10. So the mode rides on the `task` input that
# already exists, the same way `reduce`/`reduce-reps` and `triangle-reduce` do, and `task=converge` keeps
# meaning `edge` byte-for-byte so the published RUNG 2b comparison stays reproducible.
CONVERGE_TASK_MODES = {
    "converge": "edge",                 # RUNG 2b's 4 fs cycle — the published comparison. DO NOT REPOINT.
    "triangle-converge": "triangle",    # the valB closure triangle's 4 legs, 2 fs, seed 0.
}


def converge_mode_for_task(task, env=None):
    """The MODES key whose units the converge job must fetch, for one dispatched task. PURE apart from env.

    Raises rather than defaulting. A wrong answer here is not a crash — it is a green run that lists an S3
    prefix nobody ever wrote, finds no `simulation.nc`, and reports a clean convergence summary over zero
    legs. Silence is the expensive outcome on this lane, so an unknown task is a hard error.

    `TVAST_CONVERGE_MODE` is the escape hatch, in the lane's own `TVAST_*` idiom: it points the diagnostic at
    any mode without spending a dispatch-input slot. It is validated against `MODES` (an unknown value is an
    error, never a silent fallback) and the caller is expected to say loudly that an override was in force —
    a sticky repository variable that quietly changed what `task=converge` measures would be this same bug
    wearing a different hat.
    """
    env = os.environ if env is None else env
    override = (env.get("TVAST_CONVERGE_MODE") or "").strip()
    if override:
        if override not in MODES:
            raise ValueError(f"TVAST_CONVERGE_MODE={override!r} is not a known mode; expected one of "
                             f"{sorted(MODES)}")
        return override
    key = str(task or "").strip()
    if key not in CONVERGE_TASK_MODES:
        raise ValueError(f"no converge mode is registered for task {key!r}; expected one of "
                         f"{sorted(CONVERGE_TASK_MODES)} (or set TVAST_CONVERGE_MODE)")
    return CONVERGE_TASK_MODES[key]

DEFAULT_TIMESTEP_FS = "4.0"
DEFAULT_WARMUP_TIMESTEP_FS = "1.0"


def resolve_timesteps(mode, timestep_fs=None, warmup_timestep_fs=None):
    """(production dt, warmup dt) as strings, for one mode. PURE apart from reading the env.

    ⚠ A MODE MAY PIN ITS OWN TIMESTEP, AND THE PIN BEATS THE ENV — the same precedence, for the same reason,
    as `template_pdb` in `build_jobspec`. The workflow exports `TVAST_TIMESTEP_FS` lane-wide and this lane's
    default is RUNG 2b's 4 fs, while the closure triangle must run at r0's 2 fs because **r0 IS its T1 edge**:
    a 4 fs T2/T3 around a 2 fs T1 would make the closure residual R measure the TIMESTEP DIFFERENCE rather
    than the path error, which is the one thing R exists to isolate. An env-first order lets a lane-wide
    export do exactly that inside a green run. An EXPLICIT argument still wins over the pin, so a deliberate
    re-run at another dt stays possible — and it lands in a different `unit_id` (dt is in the id), so it can
    never resume into the pinned run's checkpoints.

    ★ ONE EXPRESSION, THREE CALLERS. `build_jobspec` decides what is RUN; `fetch_legs` and
    `fetch_trajectories` reconstruct the unit ids of what was run. If those disagree the launch is fine and
    the reduction silently finds nothing — a mode that ran at 2 fs looked up at 4 fs returns an empty
    directory, and an empty reduction is the "reports success while measuring nothing" shape this lane keeps
    paying for.
    """
    sizing = MODES.get(mode) or {}
    dt = str(timestep_fs or sizing.get("timestep_fs") or os.environ.get("TVAST_TIMESTEP_FS")
             or DEFAULT_TIMESTEP_FS)
    wdt = str(warmup_timestep_fs or sizing.get("warmup_timestep_fs")
              or os.environ.get("TVAST_WARMUP_TIMESTEP_FS") or DEFAULT_WARMUP_TIMESTEP_FS)
    return dt, wdt


def unit_id(leg_id, seed, direction, timestep_fs, warmup_timestep_fs, mode):
    """The identity of one unit of work. PURE.

    Everything downstream is keyed off this string — the S3 result prefix, the Vast label, the commit
    prefix, the watchdog entry — so it must contain every parameter that makes two runs scientifically
    different. The timestep is in it because an MD checkpoint is timestep-specific: OpenFE refuses to
    resume a checkpoint built at another dt, and a prefix that omitted dt would either crash on resume or,
    worse, be "fixed" by someone wiping it. The MODE is in it because probe and edge differ in iteration
    count, and a probe's 200-iteration production must never be mistaken for (or resumed into) a full leg.
    """
    dirsuf = "" if direction == "fwd" else f"_dir{direction}"
    return (f"{leg_id}_r{seed}{dirsuf}_dt{timestep_fs}fs_wu{warmup_timestep_fs}_{mode}")


def _mode_of_unit(uid):
    """The MODE a unit id ends with, or None. PURE.

    Matched as a LONGEST suffix against `MODES`, never split on the last underscore: `edge_reps`,
    `triangle_smoke` and `5aks_smoke` all contain one, so a naive rsplit would return `reps`/`smoke` and
    silently pick the wrong gate. Used to decide which gate can re-place a hostless unit, so a wrong answer
    would wake the wrong lane's launcher.
    """
    if not uid:
        return None
    for m in sorted(MODES, key=len, reverse=True):
        if str(uid).endswith("_" + m):
            return m
    return None


def unit_label(uid):
    """Vast instance label. PURE. Vast caps labels at 60 chars and we match label->unit by re-deriving,
    never by parsing back — the protfep lane lost a reap to a lossy label that could not round-trip.

    ⚠ A BARE `[:60]` TRUNCATION IS ITSELF THE LOSSY ENCODING THIS DOCSTRING WARNS ABOUT, and RUNG 5a-KS
    walked straight into it: `5aks_d0_to_d__ternary_nr4a3 ... _5aks_smoke` renders to exactly 61 characters
    and was silently cut to `...-5aks-smok`. Re-deriving still "matched", so the round-trip test passed —
    but two DIFFERENT units whose labels agree in their first 60 characters then share one label, and
    `collect` reaps on that match. The consequence is not cosmetic: it either reaps the wrong host or fails
    to reap the right one, and a GPU then bills until the runtime backstop hours later. The test that caught
    it is the one asserting a label must NOT match a different unit id.

    So an over-long label ends in a digest of the WHOLE unit id instead of losing its tail. Labels that
    already fit are returned byte-identical, so no unit that has ever run gets a new label.
    """
    lab = f"{LABEL_PREFIX}-{uid}".replace("_", "-").replace(".", "p").lower()
    if len(lab) <= 60:
        return lab
    import hashlib
    return lab[:51] + "-" + hashlib.sha256(uid.encode()).hexdigest()[:8]


def label_matches_unit(label, uid):
    """Does this instance label belong to this unit? PURE, and one-directional on purpose.

    A missed match is not cosmetic: `collect` reaps on it, so a failure to pair a finished leg with its
    host leaves a GPU billing until the runtime backstop hours later.
    """
    if not label or not uid:
        return False
    return str(label).strip().lower() == unit_label(uid)


def units_for(mode):
    """The (leg_id, seed, direction) tuples this mode runs. PURE."""
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {sorted(MODES)}")
    return list(MODES[mode]["legs"])


def commit_prefix(bucket, uid, prefix=None):
    """S3 prefix for this unit's MultiState commit store. PURE."""
    return f"s3://{bucket}/{(prefix or RESULT_PREFIX).rstrip('/')}/commits/{uid}"


def result_prefix_for(bucket, uid, prefix=None):
    """S3 prefix for this unit's artefacts (leg JSON, status, phase marker, log). PURE."""
    return f"s3://{bucket}/{(prefix or RESULT_PREFIX).rstrip('/')}/legs/{uid}"


# =============================================================================================================
# the on-host pipeline
# =============================================================================================================
# Structure: idempotency check -> repo -> stage (cached) -> pre-equilibrate (cached) -> overlay -> MD.
# Every phase writes a marker to S3 so an outside observer can tell WHICH phase is slow, which is the
# distinction that three separate silent stalls on the GCP ternary lane turned on.
_PIPELINE = r"""
set -o pipefail
export HOME=/root
export PATH=/opt/mamba/envs/rbfe/bin:$PATH
# The rbfe env carries no CA bundle for python SSL, so ternary_pdb_stage.py's RCSB fetch fails with
# CERTIFICATE_VERIFY_FAILED and silently yields an EMPTY ligands.sdf (root-caused on the first Vast firm
# run, 2026-07-23). Point SSL at the bundle the Dockerfile's apt ca-certificates installs.
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
exec > >(tee /tmp/run.log) 2>&1
echo "[tvast] $(date -u +%FT%TZ) start unit=$UNIT_ID leg=$LEG_ID seed=$SEED dir=$DIRECTION dt=${RBFE_TIMESTEP_FS}fs warmup_dt=${RBFE_WARMUP_TIMESTEP_FS}fs"

AWSC=$(command -v aws || echo /opt/mamba/envs/rbfe/bin/aws)
# ★★ THE PHASE MARK IS ECHOED INTO THE LOG, WITH ITS TIMESTAMP (2026-07-31). It was written ONLY to
# `phase.txt`, which `mark` OVERWRITES — so S3 held the current phase and its start time, and the history was
# destroyed on every transition. The run.log carried exactly two clocks, `start` and `EXIT`, which means the
# ~28 min cold start could be measured as a TOTAL and never split.
#
# WHY THAT TOTAL IS THE MOST EXPENSIVE UNKNOWN ON THIS LANE. Median session is ~1.00 h, so a cold start of
# tens of minutes is a large fraction of every rental, and any session shorter than it banks NOTHING — 25 %
# of today's rentals. Measure-on-arrival showed the MD itself is fine (the worst host today still reaches a
# commit boundary in ~39 min of a 48 min budget), so the cold start is the constraint.
#
# ⚠ AND THE "~28 min" THIS LANE KEEPS QUOTING IS INHERITED, NOT MEASURED ON IT. Its one home is the
# `ternary-4fs-vast-findings.md` cold-start budget, which is a MEASURED ~25 min TOTAL — 2.8 min image pull,
# ~8 min staging, 456 s pre-equilibration, ~6 min setup — and which says **~15 min of that is cached and
# will not repeat**. `setup_tax.py` then measured the caches HITTING on 23 of 27 attempts. So the expected
# cold start on this lane is nearer ~10 min than ~28, and the ~28 has never been measured on a 5a-KS leg with
# warm caches. Which of those two the lane is actually paying is exactly what the marks below now record —
# do not re-quote either figure as if it were this lane's measurement until one attempt has produced a split.
#
# One `echo` per transition, into a file that is already being tee'd and synced. It costs nothing and it
# makes every future attempt yield a complete line-item split: image pull -> stage -> pre-equil -> MD start.
mark() { echo "[tvast] $(date -u +%FT%TZ) phase=$1"
         printf '%s %s\n' "$1" "$(date -u +%FT%TZ)" | $AWSC s3 cp - "$RESULT_S3/phase.txt" >/dev/null 2>&1 || true
         $AWSC s3 cp /tmp/run.log "$RESULT_S3/run.log" >/dev/null 2>&1 || true; }
# WHICH FAILURES ARE THE HOST'S FAULT, AND WHICH ARE OURS. This distinction decides whether the watchdog
# relaunches, so it has to be made here where the phase is known — not inferred later from a log.
#   cuda-probe  -> THIS HOST cannot run the job (no CUDA platform, wrong driver). Relaunching ELSEWHERE is
#                  exactly right, so leave no `leg.json`: the unit reads DIED and the launcher picks a
#                  different machine. Only a `status.json` breadcrumb is left, for a human reading the board.
#   anything else -> the code or the data failed, and it will fail identically on the next host. Write
#                  `leg.json` with status=failed so the watchdog's FAILED verdict fires and REFUSES to
#                  relaunch. Without this, a staging or pre-equil bug would buy a fresh rental per attempt,
#                  up to the daily cap, every one dying the same way.
fail() { echo "[tvast] FAILED at $1"
         printf '{"unit_id":"%s","status":"failed","phase":"%s","rc":1,"nan_seen":false,"utc":"%s","updated_utc":"%s"}\n' \
           "$UNIT_ID" "$1" "$(date -u +%FT%TZ)" "$(date -u +%FT%TZ)" > /tmp/status.json
         $AWSC s3 cp /tmp/status.json "$RESULT_S3/status.json" >/dev/null 2>&1 || true
         if [ "$1" != cuda-probe ]; then
           $AWSC s3 cp /tmp/status.json "$RESULT_S3/leg.json" >/dev/null 2>&1 || true
         else
           echo "[tvast] host-side failure ($1) — deliberately NOT writing leg.json so a relaunch picks a different machine"
         fi
         $AWSC s3 cp /tmp/run.log "$RESULT_S3/run.log" >/dev/null 2>&1 || true; exit 1; }
# PRESERVE THE PREVIOUS ATTEMPT'S LOG BEFORE OVERWRITING IT. `exec > >(tee /tmp/run.log)` starts a fresh
# file, and the sync loop then overwrites `$RESULT_S3/run.log` — so on a resume after preemption the only
# record of WHY the last attempt ended is destroyed by the attempt that replaces it. Lane 3's census of the
# NR-V04 panel is the cost of that pattern: three analysis defects were uncorrectable because nothing
# survived. Costs one S3 copy of a text file.
#
# ⚠ THIS BLOCK MUST RUN BEFORE THE FIRST `mark`, AND IT DID NOT. `mark()` uploads /tmp/run.log — which the
# `exec > >(tee ...)` above has just TRUNCATED — to $RESULT_S3/run.log. With `mark start` ordered first, the
# fresh ~170-byte log overwrote the previous attempt's in S3, and the archive below then dutifully copied
# the stub. Measured 2026-07-26 on the first 5a-KS smoke: seventeen archived attempts, every one 168 bytes,
# and the log of the attempt that actually failed was gone. The status.json written by fail() survived and
# named the phase, which is the only reason the failure was diagnosable at all. Archive first, then mark.
if $AWSC s3 ls "$RESULT_S3/run.log" >/dev/null 2>&1; then
  $AWSC s3 cp "$RESULT_S3/run.log" "$RESULT_S3/attempts/run-$(date -u +%Y%m%dT%H%M%SZ).log" >/dev/null 2>&1 \
    && echo "[tvast] archived the previous attempt's run.log under attempts/" || true
fi
mark start

# IDEMPOTENCY. Vast re-runs onstart when a container restarts, and CI may re-dispatch a unit whose leg
# already landed. Re-running would overwrite a finished result with a fresh (and, at a different commit
# generation, possibly worse) one. Checked BEFORE any GPU work.
# ⚠ A FAILED leg.json MUST NOT BLOCK ITS OWN RETRY. This tested only for EXISTENCE, and `fail()` writes a
# leg.json with status=failed — so once a leg had failed, every re-dispatch rented a host that immediately
# exited "nothing to do", produced nothing, and reported green. The 5a-KS smoke leg failed in preequil on
# 2026-07-26 and left exactly that record, so the very next re-launch after the fix would have been a
# wasted rental. Short-circuit only on a leg that actually FINISHED.
if $AWSC s3 cp "$RESULT_S3/leg.json" /tmp/prev_leg.json >/dev/null 2>&1; then
  if grep -q '"status"[[:space:]]*:[[:space:]]*"done"' /tmp/prev_leg.json; then
    echo "[tvast] a DONE leg.json is already in S3 -> nothing to do (awaiting CI reap)"; exit 0
  fi
  echo "[tvast] previous leg.json is NOT done (a failed attempt) -> re-running rather than exiting"
fi

# CUDA REALITY CHECK, up front and fatal. OpenMM silently falling back to the CPU platform on a rented
# GPU is the worst possible outcome: it bills a 4090 to run ~200x slower and looks alive the whole time.
# OPENMM_REQUIRE_CUDA=1 makes the engine refuse, but by then we have already paid for stage + pre-equil.
python - <<'PYEOF' || fail cuda-probe
import openmm, os
plats = [openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())]
print("[tvast] openmm", openmm.__version__, "platforms", plats)
if "CUDA" not in plats:
    # A conda-pack/relocated env loses OpenMM's compiled-in plugin dir; pointing OPENMM_PLUGIN_DIR at this
    # env's plugins restores auto-load for BOTH our driver and OpenFE's internal getPlatformByName("CUDA").
    os.environ["OPENMM_PLUGIN_DIR"] = "/opt/mamba/envs/rbfe/lib/plugins"
    openmm.Platform.loadPluginsFromDirectory(os.environ["OPENMM_PLUGIN_DIR"])
    plats = [openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())]
    print("[tvast] after plugin reload:", plats)
raise SystemExit(0 if "CUDA" in plats else 3)
PYEOF
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true
# WHICH CARD actually ran, recorded into the result. This lane is the first ternary leg on Vast and its
# per-iteration rate is a deliverable; a rate with no card attached cannot be compared to the 4090/3090
# grid and is therefore not a measurement of anything.
export TVAST_GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)"

cd /root
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz || fail repo-pull
cd Rare-cancers-*/research/modalities || fail repo-pull
# WHICH CODE actually ran. The host pulls a codeload tarball, so there is no git sha on disk and the branch
# may have moved between dispatch and container start. A content hash of the two files that define the run
# is the only fingerprint that cannot lie.
export TVAST_CODE_SHA="$(cat run_ternary_leg.sh nr4a3_ternary_fep.py | sha256sum | cut -c1-12)"
echo "[tvast] recipe+engine sha256[:12]=$TVAST_CODE_SHA branch=$GIT_BRANCH image=$VAST_IMAGE_TAG"
mark cloned

export IN=/tmp/tin OUT=/tmp/tout
mkdir -p "$IN" "$OUT"

# --- continuous log/phase sync (every 2 min). The SCIENCE checkpoints do not go through here: the engine's
#     commit store writes them straight to S3 per interval. This loop exists so an outside monitor can read
#     the phase and the log tail of a live host without SSH, which is what makes the watchdog possible. ---
( while true; do sleep 120; $AWSC s3 cp /tmp/run.log "$RESULT_S3/run.log" >/dev/null 2>&1 || true; done ) &
SYNC_PID=$!

# --- STAGE (cached). RCSB fetch + SMARCA4->SMARCA2 homology model + assembly, ~15 min. Seed-keyed because
#     ternary_pdb_stage picks starting_model_index = seed % n_models, so seeds are DIFFERENT structures. ---
mark staging
if $AWSC s3 cp "$STAGE_CACHE" /tmp/stage.tar >/dev/null 2>&1 && tar -C "$IN" -xf /tmp/stage.tar 2>/dev/null; then
  echo "[tvast] stage cache HIT -> $STAGE_CACHE"
else
  # STAGE_REQUIRED=1: this leg's inputs were built off-host (a Boltz co-fold staged on CI and pre-seeded
  # into the cache) and CANNOT be re-derived here. Falling through to the crystal stager would hand it a
  # leg id it has never heard of and a template label that is not a PDB entry.
  [ "$STAGE_REQUIRED" = "1" ] && { echo "[tvast] stage cache MISS at $STAGE_CACHE and STAGE_REQUIRED=1 -- this leg stages off-host; seed the cache first"; fail staging; }
  echo "[tvast] stage cache MISS -> staging $LEG_ID from $TEMPLATE_PDB"
  SEED=$SEED python ternary_pdb_stage.py --leg-id "$LEG_ID" --template-pdb "$TEMPLATE_PDB" --out "$IN" || fail staging
  tar -C "$IN" -cf /tmp/stage.tar "$LEG_ID" && $AWSC s3 cp /tmp/stage.tar "$STAGE_CACHE" >/dev/null 2>&1 || true
fi
ls -la "$IN/$LEG_ID" || true

# --- PRE-EQUILIBRATION (cached). THE fix for the softcore warmup NaN (runbook 1c): relax the fully
#     interacting physical complex with plain MD before any alchemy. Deterministic given SEED, so a cache
#     hit is byte-identical to a fresh run. A solvent leg has no protein complex to relax, so it is
#     skipped there — and skipping is CORRECT, not a shortcut: the NaN mechanism is the softcore region in
#     a large rough assembly, which a ligand in a water box does not have. ---
if [ "$NEEDS_PREEQUIL" = "1" ]; then
  mark preequil
  if $AWSC s3 cp "$PE_CACHE" /tmp/pe.tar >/dev/null 2>&1 && tar -C "$IN/$LEG_ID" -xf /tmp/pe.tar 2>/dev/null; then
    echo "[tvast] pre-equil cache HIT -> $PE_CACHE (relaxed complex.pdb + ligands.sdf overlaid)"
  else
    echo "[tvast] pre-equil cache MISS -> running ternary_preequil.py (${PREEQUIL_NS} ns)"
    env LEG_ID="$LEG_ID" SEED="$SEED" CHARGE_METHOD="$CHARGE_METHOD" PREEQUIL_NS="$PREEQUIL_NS" \
        PREEQUIL_EXACT_FF=1 OPENMM_PLATFORM=CUDA OPENMM_REQUIRE_CUDA=1 \
        INPUT_DIR="$IN" OUTPUT_DIR="$OUT" python ternary_preequil.py || fail preequil
    cp "$OUT/$LEG_ID/complex.pdb" "$OUT/$LEG_ID/ligands.sdf" "$IN/$LEG_ID/" || fail preequil-overlay
    tar -C "$IN/$LEG_ID" -cf /tmp/pe.tar complex.pdb ligands.sdf \
      && $AWSC s3 cp /tmp/pe.tar "$PE_CACHE" >/dev/null 2>&1 || true
  fi
fi

# --- MD. `run_ternary_leg.sh` is the SINGLE SOURCE OF TRUTH for the recipe; this lane calls it and does not
#     re-implement it (a hand-copied duplicate is what made the last Vast ternary attempt run 16 windows and
#     NaN). SKIP_PREEQUIL=1 because we have already overlaid the relaxed structure above, with a cache.
#     `timeout` rather than autoteardown.py so the runtime cap kills the MD but still lets the final upload
#     below run — wrapping the driver in autoteardown races the poweroff against the deliverable. ---
mark md-running
set +e
timeout -k 120 "${MD_TIMEOUT_S}" env \
  IN="$IN" OUT="$OUT" LEG_ID="$LEG_ID" SEED="$SEED" DIRECTION="$DIRECTION" PY="$(command -v python)" \
  SKIP_PREEQUIL=1 CHARGE_METHOD="$CHARGE_METHOD" N_WINDOWS="$N_WINDOWS" \
  RBFE_TIMESTEP_FS="$RBFE_TIMESTEP_FS" RBFE_WARMUP_TIMESTEP_FS="$RBFE_WARMUP_TIMESTEP_FS" \
  RBFE_MIN_STEPS="$RBFE_MIN_STEPS" RBFE_WARMUP_ITERS="$RBFE_WARMUP_ITERS" RBFE_PROD_ITERS="$RBFE_PROD_ITERS" \
  RBFE_POSITIONS_WRITE_PS="$RBFE_POSITIONS_WRITE_PS" RBFE_VELOCITIES_WRITE_PS="$RBFE_VELOCITIES_WRITE_PS" \
  RBFE_SETUP_CACHE_S3="$RBFE_SETUP_CACHE_S3" SETUP_CACHE_VERSION="$SETUP_CACHE_VERSION" \
  RBFE_REQUIRE_PRIMED_SETUP="$RBFE_REQUIRE_PRIMED_SETUP" \
  RBFE_SPOT_SAFE=1 RBFE_SPOT_COMMIT_S3="$COMMIT_S3" \
  RBFE_WARMUP_CKPT_ITERS="$WARMUP_CKPT_ITERS" RBFE_PROD_CKPT_ITERS="$PROD_CKPT_ITERS" \
  RBFE_PRUNE_CHK="$RBFE_PRUNE_CHK" \
  bash run_ternary_leg.sh
export RC=$?      # EXPORTED: the summariser below reads it from the environment, and an unexported RC
                  # silently defaults to 1 there, marking a perfectly good leg `failed`.
# `set -e` is deliberately NOT restored. Everything from here on is the DELIVERABLE path — summarise the
# result, upload it, upload the log — and it must run to completion even when the MD failed. That is
# precisely the case where the log is the only thing worth having, and an -e abort would discard it.
kill $SYNC_PID 2>/dev/null || true
mark md-done
echo "[tvast] MD exit rc=$RC"

# --- DELIVERABLE. The engine writes leg_<leg>_<dir>_r<seed>.json into CKPT_DIR (= $OUT). Normalise it to a
#     single well-known key plus a status record, so `collect` and the watchdog have ONE thing to look for
#     and cannot be fooled by a partial upload. ---
LJ=$(ls "$OUT"/leg_*.json 2>/dev/null | head -1)
python - <<'PYEOF'
import json, os, re, glob
out = os.environ["OUT"]; uid = os.environ["UNIT_ID"]
lj = sorted(glob.glob(os.path.join(out, "leg_*.json")))
doc = {}
if lj:
    try:
        doc = json.load(open(lj[0]))
    except Exception as e:            # noqa: BLE001
        doc = {"_unreadable": repr(e)}
# Per-iteration wall time, straight from the driver's own [timing] lines. This lane is the FIRST ternary
# leg on Vast, and STRATEGY carries the ternary cost base as an 8G1Q rate being reused for NR4A — flagged
# as not transferable until a leg is timed. So the rate is a DELIVERABLE, not a log line, and it is
# recorded per phase because warmup (1 fs) and production (4 fs) have different step counts per iteration.
# PHASE IS TRACKED FROM THE DRIVER'S OWN TRANSITION LINES, not by keyword-sniffing the timing line.
# Warmup runs at 1 fs and production at the leg's dt, so they have DIFFERENT steps per iteration —
# ~2500 vs ~625 at 4 fs. Pooling them would report a meaningless average and would make the 4 fs
# speedup unmeasurable, which is the entire point of this run. `[timing]` also carries the phase
# TARGET (`at iteration 8/48`), captured so a reader can see how far each phase actually got.
timing = {"warmup": [], "production": []}
reached = {"warmup": [0, 0], "production": [0, 0]}
phase = "warmup"
try:
    for ln in open("/tmp/run.log", errors="replace"):
        if "[spot-driver]" in ln and ("PRODUCTION created" in ln or "resume PRODUCTION" in ln
                                      or "FRESH production" in ln):
            phase = "production"
        elif "[spot-driver]" in ln and ("WARMUP from iter" in ln or "RESUME warmup" in ln
                                        or "warmup FRESH" in ln):
            phase = "warmup"
        m = re.search(r"\[timing\]\s+(\d+)\s+iters in\s+([\d.]+)s\s*=\s*([\d.]+)\s*s/iter"
                      r".*?at iteration\s+(\d+)/(\d+)", ln)
        if m:
            timing[phase].append(float(m.group(3)))
            reached[phase] = [int(m.group(4)), int(m.group(5))]
except OSError:
    pass
def _stats(v):
    if not v:
        return None
    s = sorted(v)
    return {"n": len(s), "median_s_per_iter": s[len(s) // 2],
            "min_s_per_iter": s[0], "max_s_per_iter": s[-1],
            "mean_s_per_iter": round(sum(s) / len(s), 3)}
nan_seen = False
try:
    log = open("/tmp/run.log", errors="replace").read()
    nan_seen = ("SimulationNaNError" in log) or ("resulted in a NaN" in log)
except OSError:
    log = ""
rec = {
    "unit_id": uid,
    "leg_id": os.environ.get("LEG_ID"), "seed": int(os.environ.get("SEED", "0")),
    "direction": os.environ.get("DIRECTION"), "mode": os.environ.get("TVAST_MODE"),
    "timestep_fs": float(os.environ.get("RBFE_TIMESTEP_FS", "0") or 0),
    "warmup_timestep_fs": float(os.environ.get("RBFE_WARMUP_TIMESTEP_FS", "0") or 0),
    "n_windows": int(os.environ.get("N_WINDOWS", "12")),
    "charge_method": os.environ.get("CHARGE_METHOD"),
    "warmup_iters_requested": os.environ.get("RBFE_WARMUP_ITERS") or "derived",
    "prod_iters_requested": os.environ.get("RBFE_PROD_ITERS") or "derived",
    "rc": int(os.environ.get("RC", "1")),
    "nan_seen": nan_seen,
    "code_sha256": os.environ.get("TVAST_CODE_SHA"),
    "gpu": os.environ.get("TVAST_GPU_NAME"),
    "timing": {k: _stats(v) for k, v in timing.items()},
    "iters_reached": {k: {"iteration": v[0], "target": v[1]} for k, v in reached.items()},
    "dg_morph_kcal": doc.get("dg_morph_kcal"), "mbar_se_kcal": doc.get("mbar_se_kcal"),
    "protocol_hash": doc.get("protocol_hash"), "starting_model": doc.get("starting_model"),
    # SYSTEM IDENTITY, LIFTED OUT OF engine_record. A cross-leg difference (ddG_coop, and RUNG 5a-KS's S) is
    # meaningless unless the legs describe the same SYSTEM, and protocol_hash by construction does not cover
    # the system. The engine records these; this normalised record did not carry them, so every reducer
    # reading leg.json saw them as UNRECORDED and — correctly — refused to call that agreement. That is the
    # hole the RUNG 2b cycle reached its verdict through. Promoted, not re-derived: one home, in the engine.
    "n_particles": doc.get("n_particles"),
    "setup_cache_version": doc.get("setup_cache_version"),
    "setup_cache_dir": doc.get("setup_cache_dir"),
    "engine_record": doc or None,
    "status": "done" if (doc.get("dg_morph_kcal") is not None and os.environ.get("RC") == "0") else "failed",
    "updated_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
}
if rec["status"] != "done":
    tail = [l for l in log.splitlines() if l.strip()][-40:]
    rec["log_tail"] = tail
json.dump(rec, open("/tmp/leg.json", "w"), indent=2)
print("TVAST_RESULT", json.dumps({k: rec[k] for k in
      ("unit_id", "status", "dg_morph_kcal", "mbar_se_kcal", "nan_seen", "timing", "rc")}))
PYEOF
[ -n "$LJ" ] && $AWSC s3 cp "$LJ" "$RESULT_S3/engine_leg.json" >/dev/null 2>&1 || true
$AWSC s3 cp /tmp/leg.json "$RESULT_S3/leg.json" || echo "[tvast] RESULT UPLOAD FAILED"
$AWSC s3 cp /tmp/run.log "$RESULT_S3/run.log" || true
mark done
echo "[tvast] $(date -u +%FT%TZ) EXIT rc=$RC"
exit $RC
"""


# ★ VAST CAPS THE ONSTART SCRIPT AT 16,384 CHARACTERS, AND SAYS SO ONLY AT RENTAL TIME.
# Diagnosed 2026-07-25 from the API's own reply, not inferred: re-launching the probe after a preemption
# returned HTTP 400
#   {"success":false,"error":"invalid_args",
#    "msg":"error 400/3471: Invalid args: len(image) > 1024, or len(args) > 16384, or len(label) > 256"}
# The rendered onstart had reached 17,017 characters — over by 633 — because the pipeline had grown by three
# safety fixes since the launch that worked. Nothing in the code was wrong; it was simply too long, and the
# failure surfaces as a *submitted-nothing launch that reports success*, which is the worst possible shape:
# the job is green, the watch list is armed, and no GPU is running.
#
# THE FIX IS NOT TO WRITE FEWER COMMENTS. 6,122 of those characters were full-line comments — the part that
# explains why each step exists, which is exactly what this repo has repeatedly paid for losing. So the
# comments stay in the SOURCE and are stripped at RENDER: the annotated pipeline lives in the file, the
# host receives the executable subset. `#`-leading lines are comments in both bash and Python, so the same
# rule is safe inside the embedded heredocs.
MAX_ONSTART_CHARS = 16384


def _render_pipeline(body):
    """Strip full-line comments and blank runs from the shell body. PURE.

    Only lines whose FIRST non-space character is `#` are dropped, so an inline `#` inside a string or a
    command is never touched. Both languages in this script (bash, and the Python heredocs) treat such a
    line as a comment, so the executable meaning is unchanged.
    """
    out, blank = [], False
    for ln in body.splitlines():
        if ln.lstrip().startswith("#"):
            continue
        if not ln.strip():
            if blank:
                continue
            blank = True
        else:
            blank = False
        out.append(ln)
    return "\n".join(out)


def onstart_length(spec):
    """Characters Vast will actually receive for this spec, including the env exports and teardown trap.

    The check has to be on the RENDERED onstart, not on the pipeline: `_vast_onstart` prepends an `export`
    line per env var plus the self-destroy trap, which was ~1.9 kB on the probe. Measuring the pipeline
    alone would have passed at 15,136 characters while the real payload was 17,017.
    """
    from gpu_backend import _object_store_env, _vast_onstart
    from gpu_backend import VastBackend
    return len(_vast_onstart(spec, VastBackend().self_terminate_cmd(), extra_env=dict(_object_store_env())))


def build_jobspec(leg_id, seed=0, direction="fwd", mode="probe", timestep_fs=None,
                  warmup_timestep_fs=None, git_branch=None, bucket=None, prefix=None,
                  charge_method=None, n_windows=None, template_pdb=None, image=None):
    """PURE construction of one unit's JobSpec (no network, no AWS). Unit-tested."""
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {sorted(MODES)}")
    sizing = MODES[mode]
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    dt, wdt = resolve_timesteps(mode, timestep_fs, warmup_timestep_fs)
    branch = git_branch or os.environ.get("GIT_BRANCH") or "main"
    charge = charge_method or os.environ.get("CHARGE_METHOD") or "nagl"
    nwin = str(n_windows or os.environ.get("TVAST_N_WINDOWS") or "12")
    # A mode that stages from something other than a crystal carries its own cache-key label, and it must
    # WIN over the env default: `TVAST_TEMPLATE_PDB` is exported lane-wide by the workflow, so an env-first
    # order would silently key the 5a-KS legs' stage cache to `8G1Q` and, on a miss, hand a Boltz-derived
    # leg id to the RCSB crystal stager.
    tpl = template_pdb or sizing.get("template_pdb") or os.environ.get("TVAST_TEMPLATE_PDB") or "8G1Q"
    if not b or not p:
        raise ValueError(
            f"refusing to launch with an incomplete result location (bucket={b!r}, prefix={p!r}). A blank "
            f"CI input arrives as an EMPTY STRING, not unset, so a .get() default does not fire — that hole "
            f"once rented a 4090 whose uploads went to 's3:///...' and produced nothing retrievable.")
    uid = unit_id(leg_id, seed, direction, dt, wdt, mode)
    solvent = leg_id.endswith("__solvent")
    env = {
        # ★ THE PROGRESS LINES ARE BLOCK-BUFFERED WITHOUT THIS. Diagnosed on the stage-1 probe, 2026-07-25,
        # by differential rather than by guess: at 2:03 PM ET the S3 run.log carried every line printed with
        # `flush=True` (`[tfep] timestep=4.0 fs`, `[hmr-diag]`, `[spot-safe] commit store`) and NOT ONE line
        # from `rbfe_spot_driver`, which uses a bare `log=print` and contains zero `flush=True` (verified by
        # grep) — same process, same stdout, the only difference being the flush. Python block-buffers stdout
        # at ~8 KB when it is a pipe, and this pipeline pipes into `tee`.
        # Why it matters: `[timing] N iters in Ns = X s/iter` and `[barrier] committed checkpoint at
        # iteration N` are the driver's lines, i.e. exactly the progress signal an unproven pipeline is
        # monitored on. Buffered, they arrive in delayed bursts, so a monitor sees a frozen log during the
        # single riskiest window (warmup iteration 1, where every prior 4 fs attempt died) and cannot tell a
        # stall from a buffer. One env var fixes the whole class without touching a file the GCP lane runs.
        "PYTHONUNBUFFERED": "1",
        "TVAST_MODE": mode,
        "UNIT_ID": uid,
        "LEG_ID": leg_id,
        "SEED": str(seed),
        "DIRECTION": direction,
        "GIT_BRANCH": branch,
        "VAST_IMAGE_TAG": image or VAST_IMAGE,
        "RESULT_S3": result_prefix_for(b, uid, p),
        "COMMIT_S3": commit_prefix(b, uid, p),
        # Stage cache is seed-keyed: ternary_pdb_stage sets starting_model_index = seed % n_models, so two
        # seeds are genuinely different starting structures and sharing one cache would silently collapse
        # the replicate spread this program uses as its error bar.
        "STAGE_CACHE": f"s3://{b}/{p}/stagecache/{leg_id}__{tpl}__seed{seed}__v1.tar",
        # Pre-equil cache is keyed by seed AND charge AND length: all three change the relaxed coordinates.
        "PE_CACHE": f"s3://{b}/{p}/preequilcache/{leg_id}__seed{seed}__{charge}__ns{os.environ.get('TVAST_PREEQUIL_NS') or '0.5'}__v1.tar",
        # A stage-cache MISS is fatal for a mode whose inputs cannot be re-derived on the host. Without this
        # the pipeline falls through to `ternary_pdb_stage.py --leg-id 5aks_... --template-pdb boltz5aks`,
        # which is a crystal stager being handed a label that is not a PDB id.
        "STAGE_REQUIRED": "1" if sizing.get("stage_required") else "0",
        "NEEDS_PREEQUIL": "0" if solvent else "1",
        "PREEQUIL_NS": os.environ.get("TVAST_PREEQUIL_NS") or "0.5",
        "TEMPLATE_PDB": tpl,
        "CHARGE_METHOD": charge,
        "N_WINDOWS": nwin,
        "RBFE_TIMESTEP_FS": dt,
        "RBFE_WARMUP_TIMESTEP_FS": wdt,
        # ★ THE MCS BUDGET IS A CORRECTNESS PARAMETER (2026-07-26). `LomapAtomMapper(time=N)` is an MCS
        # TIMEOUT in seconds and a timed-out MCS returns its best PARTIAL match SILENTLY — so the atom map,
        # i.e. what the alchemical transformation actually is, was a function of how fast the rented host
        # happened to be. Measured: one edge mapped 111 atoms on two hosts and 80-with-31-dummies on a third.
        # Set EXPLICITLY here rather than left to the engine's default so the value is part of the rented
        # unit's recorded environment, not a property of whichever commit the host's tarball happened to pull.
        "RBFE_LOMAP_TIME_S": os.environ.get("TVAST_LOMAP_TIME_S") or "300",
        # See the note on the mode: only safe where no unstamped generation can need resuming.
        "RBFE_STRICT_PROVENANCE": "1" if sizing.get("strict_provenance") else "0",
        # ★★ KILL THE O(n²) COMMIT — GATED ON THE LADDER RUNG, NOT ONLY ON A SWITCH. See
        # `prune_chk_for_mode`: a repository variable is GLOBAL, and this lane self-dispatches, so the
        # switch alone cannot promise the four live legs are untouched. The mode allowlist can.
        "RBFE_PRUNE_CHK": prune_chk_for_mode(mode),
        # ...and fail CLOSED if the map still comes back short. `nr4a3_ternary_fep.assert_map_not_degenerate`
        # derives the required heavy-atom count from the endpoints' own MCS and aborts before any sampling is
        # billed. Explicit for calibration legs because their expectation is verified at $0 in CI first.
        "RBFE_MAP_ASSERT": os.environ.get("TVAST_MAP_ASSERT") or ("1" if leg_id.startswith("calib_") else "0"),
        # 5000, not the engine default 25000: the GCP lane measured 25000 steps spending ~20-60 min at ~0%
        # GPU across 12 replicas for NO NaN benefit (the NaN survives 25000 — see runbook 1b/1c).
        "RBFE_MIN_STEPS": os.environ.get("TVAST_MIN_STEPS") or "5000",
        # STRIDED HEAVY-ATOM TRAJECTORY — set explicitly here, not left to an engine default, because this is
        # the property that decides whether a leg can ever be re-analysed. The NR-V04 covalent panel's
        # read-only census found 72 objects across 19 units and ZERO trajectories, which made three known
        # analysis defects permanently uncorrectable and forced the panel to be re-run or abandoned. 50 ps is
        # a 20-iteration stride at the 2.5 ps time_per_iteration: ~50 MB over a full leg, against the ~112 MB
        # System XML this same driver already uploads. Velocities stay off — they double the size and no
        # geometric re-analysis needs them.
        "RBFE_POSITIONS_WRITE_PS": os.environ.get("TVAST_POSITIONS_WRITE_PS") or "50",
        "RBFE_VELOCITIES_WRITE_PS": os.environ.get("TVAST_VELOCITIES_WRITE_PS") or "",
        # S3 SETUP CACHE. Solvating + parameterising the ~146k-atom hybrid is ~6-15 min of GPU-idle time,
        # rebuilt on EVERY resume because it is the one expensive step that was not cached. Keyed by
        # (leg, direction, seed, charge, version); the built System is timestep-independent, so it is
        # deliberately NOT dt-keyed — but it IS pre-equilibration-dependent, hence the `pe` in the version.
        "RBFE_SETUP_CACHE_S3": f"s3://{b}/{p}/setupcache",
        "SETUP_CACHE_VERSION": os.environ.get("TVAST_SETUP_CACHE_VERSION") or "v1pe",
        # The engine FAILS FAST when a setup cache is configured but missing, to enforce the GCP lane's
        # CPU-prime-then-GPU process. This lane has no CPU prime for SETUP (only for stage), so the first
        # run of each leg must be allowed to build it — after which every resume restores it.
        "RBFE_REQUIRE_PRIMED_SETUP": "0",
        "RBFE_WARMUP_ITERS": sizing["warmup_iters"],
        "RBFE_PROD_ITERS": sizing["prod_iters"],
        # Checkpoint granularity == the maximum work a preemption can cost, traded against per-commit
        # overhead. Per-mode; see the note on MODES. The engine rounds each phase's target DOWN to a
        # multiple of its interval, so an interval larger than a short phase's target would silently
        # shorten the run — which is why probe and edge do not share one value.
        # ★★ AND PER-ARM, NOT ONLY PER-MODE, WHEREVER A MODE OPTS IN. "The maximum work a preemption can
        # cost" is a WALL-CLOCK quantity, so one iteration count buys two arms two DIFFERENT exposures
        # whenever their systems sample at different seconds-per-iteration. `warmup_ckpt_iters_for` derives
        # it from the measured rates; the mode's own value is the reference arm's.
        "WARMUP_CKPT_ITERS": (os.environ.get("TVAST_WARMUP_CKPT_ITERS")
                              or warmup_ckpt_iters_for(leg_id, mode, sizing, dt, wdt)),
        "PROD_CKPT_ITERS": os.environ.get("TVAST_PROD_CKPT_ITERS") or sizing["prod_ckpt_iters"],
        # The MD's own cap, inside the instance runtime cap, so the deliverable upload still runs.
        "MD_TIMEOUT_S": str(int(sizing["max_runtime_s"] * 0.92)),
    }
    spec = JobSpec(
        name=unit_label(uid),
        command=["bash", "-lc", _render_pipeline(_PIPELINE.replace("{repo}", REPO))],
        image=image or VAST_IMAGE,
        checkpoint_uri=result_prefix_for(b, uid, p),
        resume=True,
        # ⛔ THE BINDING BUY LINE, TRAVELLING WITH THE SPEC (see `buy_ceiling_usd_per_ns`). Every rental this
        # lane makes — fan-out, resume, or a single cold unit after a preemption — is refused above 1.5x
        # basis at SELECTION, which is what CLAUDE.md §6's "a relaunch is a new purchase" actually requires.
        resources=resource_spec(max_usd_per_ns=buy_ceiling_usd_per_ns()),
        max_runtime_s=int(os.environ.get("TVAST_MAX_RUNTIME_S") or sizing["max_runtime_s"]),
        env=env,
    )
    # FAIL HERE, NOT AT THE RENTAL. Over the cap, Vast answers the create with a 400 and the launcher's
    # per-unit `except` turns it into a printed line inside a GREEN job — a launch that rents nothing and
    # reports success. Raising during construction makes it a build-time error a unit test can catch.
    try:
        n = onstart_length(spec)
    except Exception:  # noqa: BLE001 — no credentials in a pure/unit context; the length check is advisory
        n = None
    if n is not None and n > MAX_ONSTART_CHARS:
        raise ValueError(
            f"rendered onstart is {n} characters, over Vast's {MAX_ONSTART_CHARS} limit by "
            f"{n - MAX_ONSTART_CHARS}. Vast rejects the create with HTTP 400 'invalid_args', which the "
            f"launcher would otherwise report as a printed failure inside a green job. Shorten the "
            f"pipeline (comments are already stripped at render) or move a step into a repo script the "
            f"host runs after the clone.")
    return spec


# =============================================================================================================
# cost model — the arithmetic RUNG 2b is actually testing
# =============================================================================================================
def ternary_cost_model(s_per_iter_prod_2fs, warmup_iters=400, prod_iters=2000,
                       warmup_dt_fs=1.0, prod_dt_fs=2.0, time_per_iteration_ps=2.5):
    """Wall time for one ternary leg, and what changing the PRODUCTION timestep does to it. PURE.

    THE POINT, because the headline number in STRATEGY is optimistic. OpenFE derives an iteration count as
    `sim_length / timestep / n_steps_per_iteration`, and `n_steps_per_iteration = time_per_iteration / dt`.
    The two dt's cancel, so the ITERATION COUNT is timestep-independent — which is where "4 fs is exactly
    half the force evaluations" comes from. But that is only true of the phase whose dt actually changed.
    The warmup runs at 1 fs and its iteration count is derived from the WARMUP integrator, so a 1 ns
    equilibration costs 1e6 steps whether production is 2 fs or 4 fs. It does not shrink at all.

    So for the as-run protocol (1 ns warmup @1 fs + 5 ns production, 12 windows):
        2 fs: 1e6 + 2.5e6 = 3.5e6 steps/replica
        4 fs: 1e6 + 1.25e6 = 2.25e6 steps/replica     -> 1.56x, NOT 2x.
    Returns both so a caller reports the measured ratio rather than the assumed one.
    """
    steps_per_iter_prod = time_per_iteration_ps * 1000.0 / prod_dt_fs
    steps_per_iter_warm = time_per_iteration_ps * 1000.0 / warmup_dt_fs
    # wall time is proportional to force evaluations; calibrate the constant off the measured 2 fs rate
    s_per_step = s_per_iter_prod_2fs / (time_per_iteration_ps * 1000.0 / 2.0)
    warm_s = warmup_iters * steps_per_iter_warm * s_per_step
    prod_s = prod_iters * steps_per_iter_prod * s_per_step
    return {
        "warmup_h": warm_s / 3600.0, "production_h": prod_s / 3600.0,
        "leg_h": (warm_s + prod_s) / 3600.0,
        "steps_per_iter_production": steps_per_iter_prod,
        "steps_per_iter_warmup": steps_per_iter_warm,
    }


def speedup_2fs_to_4fs(warmup_iters=400, prod_iters=2000, warmup_dt_fs=1.0, time_per_iteration_ps=2.5):
    """Leg-level speedup of moving production 2 fs -> 4 fs, with the warmup held at its own dt. PURE."""
    a = ternary_cost_model(1.0, warmup_iters, prod_iters, warmup_dt_fs, 2.0, time_per_iteration_ps)
    b = ternary_cost_model(1.0, warmup_iters, prod_iters, warmup_dt_fs, 4.0, time_per_iteration_ps)
    return a["leg_h"] / b["leg_h"] if b["leg_h"] else None


# =============================================================================================================
# PER-ARM CHECKPOINT CADENCE — the same exposure, in SECONDS, for arms that sample at different rates
# =============================================================================================================
# ★★ WHAT IS WRONG WITH ONE SHARED `warmup_ckpt_iters`, STATED IN THE UNIT THAT MATTERS. Host churn is the
# dominant cost of wall-clock on this lane, and the checkpoint interval is the single lever that decides how
# much work each churn event destroys. What a reclaim costs is
#
#       EXPOSURE = warmup_ckpt_iters x seconds_per_iteration        [SECONDS, not iterations]
#
# and `seconds_per_iteration` is a property of the ARM (how big the solvated system is), while
# `warmup_ckpt_iters` was a property of the MODE. So one number in `MODES` buys the two arms DIFFERENT
# exposures, and nothing in the readout said so.
#
# ★ MEASURED ON `edge_reps` (`ternary-reps-diag.json`, 2026-07-28), and the arithmetic is the argument:
#
#     binary  r1  production/2000  DONE    over 19 archived attempts   ~105 iterations banked per attempt
#     binary  r2  production/2000  DONE    over  8 archived attempts   ~250 iterations banked per attempt
#     ternary r1  warmup/832       failed  over 26 archived attempts    ~32 iterations banked per attempt
#     ternary r2  warmup/320       failed  over  5 archived attempts    ~64 iterations banked per attempt
#
# BOTH arms are churning on the same market. The binary arm finished its entire leg through it; the ternary
# arm is still in warmup — and at the shared interval of 64, r1's AVERAGE ATTEMPT DID NOT REACH ONE
# CHECKPOINT BOUNDARY (13 commits across 26 attempts), so about half of the hosts it rented banked nothing
# at all. That is the failure mode a shared iteration count produces on a slower arm, in the lane's own
# numbers. `warmup_ckpt_iters_for` gives the slower arm the finer interval so both arms bank on the same
# WALL-CLOCK cadence rather than the same iteration count.
#
# ⛔ WHAT THIS DOES **NOT** CLAIM (CLAUDE.md §4). The ternary units' leg records read `status=failed`, and
# this function is not a diagnosis of why. Exposure is one lever — the one that decides what each churn
# event costs — and it is worth pulling on its own measured terms; the setup-side failure is
# `reps-setup-rss`'s subject. SUPERSEDED, RETAINED (CLAUDE.md §1.2): the 2026-07-27T23:00Z snapshot of the
# same artifact, on which this note was first drafted, read both ternary units at committed iteration 0 with
# a last line of `No CMAPTorsionForce found` — they have since committed 832 and 320.
#
# ⛔ AND DO NOT "TIDY" THE ARMS BACK TO ONE SHARED VALUE. That is the bug, not the untidiness: a single
# iteration count cannot express "the same exposure" for two arms whose iterations cost different seconds.
# `tests/test_ternary_ckpt_exposure.py` fails if the two arms' exposures diverge.
#
# SAFE TO CHANGE MID-EXPERIMENT, for two reasons that were checked rather than assumed. (1) The interval is a
# COMMIT CADENCE, not a sampling parameter — it selects when sampler state is written to the commit store and
# touches neither the integrator, the moves nor the random stream, so the trajectory is unchanged and a
# matched cycle against r0 stays matched. (2) `rbfe_spot_driver` rounds each phase target DOWN to a multiple
# of the interval (`warmup_target = (warmup_iters // warmup_checkpoint_iters) * warmup_checkpoint_iters`), so
# an interval that did NOT divide the target would SHORTEN this leg's equilibration relative to r0's — a
# protocol difference inside a matched cycle. Every interval derived below divides the target exactly. It
# also only ever applies to a unit with nothing committed: on a resume the interval baked into the committed
# .nc OVERRIDES the environment (the driver's single-interval invariant).

# The arm whose interval the mode's own `warmup_ckpt_iters` was chosen for; every other arm is derived
# against it. `MODES["edge"]["warmup_ckpt_iters"] = 64` was reasoned about on this arm and it is the arm that
# demonstrably banks progress on these hosts, so it is the reference rather than a candidate for change.
CKPT_REFERENCE_ARM = "binary"

# ★ MEASURED PER-COMMIT OVERHEAD. `ternary-4fs-vast-findings.md` §4, stage-1 probe on a Vast 4090: pure MD
# ~6.6-8.5 s/iter, commit-inclusive at `warmup_ckpt_iters=8` 11.4 s/iter (iterations 24->32 committed in
# 91 s) => (11.4 - 8.5) x 8 ~= 23 s per commit. That is one reporter sync plus an ~25 MB .nc/.chk pair copied
# and PUT to S3. ONE HOME: this constant, pointing at that section — not re-derived anywhere else.
# ⚠ STALE BY ~28x AND KNOWN TO BE (2026-07-31). The pair is NOT ~25 MB: measured across 158 real committed
# generations the median is **699.5 MiB**, because the `.chk` accumulates one full-coordinate frame per
# checkpoint interval and every commit re-uploads all of them (12 replicas x 147,788 atoms x 3 x 4 B x 2 =
# 40.6 MiB predicted per frame, 49.2-49.7 MiB observed). MAX_COMMIT_OVERHEAD_FRAC below is evaluated against
# this number, so every overhead judgement it feeds is currently wrong in the OPTIMISTIC direction.
#
# NOT REPLACED WITH A GUESS (rule 1: derived, never typed). `rbfe_spot_checkpoint.commit` now self-times and
# prints `[barrier] commit <phase>@<iter> persisted N MiB in Ns`, and `setup_tax.commit_cost` parses it; this
# constant is re-derived the moment one commit is observed. No re-placement has happened since the
# instrumentation landed, so no measurement exists yet. Design for removing the O(n^2) that causes it:
# `commit-payload-design.md`.
COMMIT_OVERHEAD_S = 23.0

# ★ AND THE TOLERANCE IT IS JUDGED AGAINST, WHICH IS NOT A NEW THRESHOLD. It is the one this lane already
# chose `edge`'s interval with, quoted from the same section: "at the edge's ci=64 it is ~0.4 s/iter, under
# 5 %". Recorded so the trade-off is auditable rather than remembered.
MAX_COMMIT_OVERHEAD_FRAC = 0.05

# The measured seconds-per-iteration per arm, per PRODUCTION TIMESTEP. NOT TYPED HERE — read from
# `ternary-arm-iteration-rates.json`, which `ternary_arm_rates.py` regenerates from the legs' own leg.json
# timing blocks (CLAUDE.md §1: a measured input is DERIVED and has one home). Two poolings that file refuses,
# both of which have already been made by hand in this repo and both of which would corrupt this derivation:
#   * across TIMESTEP — a 2 fs iteration is 1250 MD steps and a 4 fs one is 625, so the same physics costs
#     ~2x the seconds (`ternary-4fs-vast-findings.md` §1/§2);
#   * across PHASE — pricing.md's superseded "~2.06x" L4->4090 card ratio compared a WARMUP rate against a
#     PRODUCTION one, and production-to-production the true ratio is ~3.53x.
# A production median IS a valid warmup rate at the same timestep, and that is the only cross-phase step
# taken: `rbfe_spot_driver` builds the warmup move by overriding `.timestep` on a move whose `n_steps` was
# already fixed at the PRODUCTION dt, so a warmup iteration and a production iteration are the same number of
# force evaluations (findings §4: "warmup and production cost the same wall time per iteration here").
_ARM_RATES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "ternary-arm-iteration-rates.json")
_ARM_RATES_CACHE = {}


def arm_iteration_rates(timestep_fs, path=None):
    """{arm: s_per_iter} measured at this PRODUCTION timestep, or {} if that timestep was never measured.

    PURE apart from one cached file read. Returning {} rather than a guessed rate is deliberate: an
    unmeasured timestep falls back to the mode's flat interval, which is exactly today's behaviour, whereas
    an invented rate would silently re-cadence a lane nobody measured.
    """
    p = path or _ARM_RATES_PATH
    if p not in _ARM_RATES_CACHE:
        try:
            with open(p) as fh:
                _ARM_RATES_CACHE[p] = json.load(fh)
        except (OSError, ValueError) as e:  # noqa: BLE001
            print(f"[tvast] WARN no measured arm rates at {p} ({type(e).__name__}: {e}); "
                  f"per-arm checkpoint cadence disabled, every arm keeps its mode's flat interval")
            _ARM_RATES_CACHE[p] = {}
    rates = (_ARM_RATES_CACHE[p].get("rates") or {}).get(f"{float(timestep_fs):.1f}") or {}
    return {arm: float(v["s_per_iter"]) for arm, v in rates.items() if v.get("s_per_iter")}


def arm_card_rate(timestep_fs, arm, gpu_name, path=None):
    """Measured s/iter for THIS arm on THIS card at this timestep, or None. PURE apart from one cached read.

    ★★ WHY A PER-CARD FIGURE IS NOT OPTIONAL FOR A GUARD (2026-07-31). `arm_iteration_rates` returns the arm
    median POOLED ACROSS CARDS, and comparing a specific host to it makes every below-median card look broken
    by construction: the table's own RTX 4090/RTX 3090 ratio is 1.745, so a perfectly healthy 3090 reads
    ~1.75x "slower than expected". Measured on the live board the moment the arrival guard shipped — two
    3090s flagged at 1.86x and 2.00x against the pooled median, which after rebasing on their own card is
    1.07x and 1.15x, i.e. normal. A guard that fires on every cheap card would have condemned the whole
    class.

    `by_gpu` is written by `ternary_arm_rates.aggregate` for exactly this — it exists precisely so an arm
    ratio can be re-checked without the card mix inside it — and nothing was reading it."""
    p = path or _ARM_RATES_PATH
    if p not in _ARM_RATES_CACHE:
        arm_iteration_rates(timestep_fs, path=p)          # populates the cache, or leaves {}
    doc = _ARM_RATES_CACHE.get(p) or {}
    entry = ((doc.get("rates") or {}).get(f"{float(timestep_fs):.1f}") or {}).get(arm) or {}
    by = entry.get("by_gpu") or {}
    if not by or not gpu_name:
        return None
    import vast_cost_model as _v
    want = _v.card_of(gpu_name)
    if want is None:
        return None
    for k, v in by.items():                               # keys are marketplace names ("NVIDIA GeForce ...")
        if _v.card_of(k) == want and v:
            return float(v)
    return None


def arm_of_leg(leg_id):
    """binary | ternary | solvent for a leg id. PURE. ONE HOME for the arm split — `ternary_arm_rates.py`,
    `ternary_reps_diag.py`'s readout and the cadence derivation all key off this and nothing re-implements it.
    """
    if "__solvent" in (leg_id or ""):
        return "solvent"
    return "ternary" if "__ternary" in (leg_id or "") else "binary"


def warmup_target_iters(timestep_fs, warmup_timestep_fs):
    """The warmup iteration count `rbfe_spot_driver` will derive, which every interval must divide exactly.

    DERIVED FROM CODE, NOT OBSERVED, and NOT a constant — it is a function of BOTH timesteps, which is why
    this lane cannot carry one hardcoded number: `edge`/`edge_reps` run 4 fs and `triangle` runs 2 fs.

        warmup steps      = EQUILIBRATION_NS / warmup_dt          (the warmup integrator's own dt)
        steps_per_iter    = time_per_iteration / production_dt    (`n_steps`, fixed at the PRODUCTION dt)
        warmup_iters      = warmup steps / steps_per_iter

    so 1.0 ns at 1 fs is 1e6 steps, and at 4 fs production (625 steps/iter) that is 1600 iterations while at
    2 fs (1250 steps/iter) it is 800. Both protocol lengths are IMPORTED rather than typed: `EQUILIBRATION_NS`
    from `nr4a3_ternary_fep`, and `time_per_iteration` from `ternary_cost_model`'s own default, which is the
    OpenFE default this lane never overrides (`openfe_introspect`). Returns None if the engine module cannot
    be imported, which disables the derivation rather than guessing at it.
    """
    try:
        import nr4a3_ternary_fep as _tfep
        equil_ns = float(_tfep.EQUILIBRATION_NS)
    except Exception as e:  # noqa: BLE001 — no engine module => no derivation, never a made-up target
        print(f"[tvast] WARN cannot read EQUILIBRATION_NS ({type(e).__name__}: {e}); "
              f"per-arm checkpoint cadence disabled")
        return None
    tpi_ps = inspect.signature(ternary_cost_model).parameters["time_per_iteration_ps"].default
    steps_per_iter = float(tpi_ps) * 1000.0 / float(timestep_fs)
    return int((equil_ns * 1e6 / float(warmup_timestep_fs)) / steps_per_iter)


def _divisors_up_to(n, cap):
    return [d for d in range(1, int(cap) + 1) if n % d == 0]


# ★★ THE PRUNE LADDER — WHICH MODES MAY COMMIT A SINGLE-FRAME `.chk`, AND WHY IT IS A CODE GATE.
#
# The prune replaces the committed checkpoint with its LAST frame only: 1231.1 MiB per commit down to the
# 47.6 MiB a resume actually reads. It was proven offline before it was wired -- bit-identical coordinates
# against an unpruned resume of the same run, the UNMODIFIED commit/restore path, a pruned CHAIN, and
# 25.88x on a real committed 5a-KS pair (GH 30676071569, $0, no rental).
#
# ⚠ WHY AN ALLOWLIST AND NOT A REPOSITORY VARIABLE. The switch could only reach this lane as a repository
# variable (the lane is at GitHub's 10-input cap, so it cannot be a dispatch input), and a repository
# variable is GLOBAL to every run of every workflow. This lane also SELF-DISPATCHES: `5aks-gate` fires
# `task=5aks` the moment the board clears, which re-places a stranded leg -- and that leg RESUMES. So "set
# the variable for one experiment" is not a thing a variable can express: the promise that the four legs at
# 94/64/51/49 % are untouched would have rested on nobody dispatching the wrong task for as long as the
# variable stayed set. It rests on this tuple instead, which a test can hold, and `TVAST_PRUNE_CHK` is
# demoted to a kill switch -- see `prune_chk_for_mode`.
#
# ⚠ AND IT IS ONE VARIABLE AT A TIME (CLAUDE.md §6). Widen this by exactly one rung, after the rung below
# it has been observed reaching its real success terminus -- never as a convenience while something else is
# also changing. The interval-32 retest in particular is a SECOND change and must not ride along.
#
# LADDER POSITION: rung 2 of 3 — the plumbing shakeout only.
#   rung 1  offline round-trip .................. DONE (GH 30676071569)
#   rung 2  `5aks_smoke` ........................ LAUNCHED, NOT PASSED — and now HELD, see below
#   rung 3  one genuinely FRESH production leg .. requires a fresh unit to exist; never a resume
#
# ⛔⛔ BOTH REMAINING RUNGS ARE HELD FOR WANT OF A SUBJECT (2026-08-01). Two separate blockers, one of
# which was mistaken for the other and cost a rental.
#
# RUNG 2 — the smoke unit is EXHAUSTED, and that is a different failure from the one it looked like.
#   The 2026-07-31 10:02 PM ET attempt produced nothing, and the visible cause was our own reaper
#   destroying it 2 min 23 s in on a five-day-old `done` record (fixed — see `finished_record` in
#   `collect`). But fixing that does NOT make the rung runnable, because of a second, independent fact:
#   `MODES["5aks_smoke"]` is `warmup_iters=8, prod_iters=12`, and this unit's commit store already stands
#   at `production/12` — its target. `run_to_target`'s loop is `while _sampler_iteration(sampler) <
#   target_iteration:`, so a resume at target never enters the body, never reaches `on_boundary`, and
#   therefore NEVER COMMITS — and the prune fires at commit. A re-run would restore, write `leg.json` and
#   exit having emitted no `[prune]` line at all. That is code, not inference.
#
#   Giving it a subject needs one of three things, and two of them are forbidden here:
#     * supersede the `done` record — `supersede-failed` refuses a `status=done` leg.json BY DESIGN;
#     * raise the smoke's iteration count — a SECOND change riding with the prune, which is exactly what
#       the "one variable at a time" note above forbids;
#     * a COMMIT SALT for this lane, which is the clean answer and the one the GCP lane already has
#       ("pair with a fresh commit_salt so it does not resume stale checkpoints"). `commit_prefix` here
#       is keyed on the unit id alone, so there is no way to ask for a fresh store. Building it means
#       touching prefix keying — the thing `_required_keys_are_enforced` exists to protect — so it is
#       work for a moment when this lane is NOT billing, not a change to make with legs in flight.
#
# RUNG 3 — no fresh 5a-KS leg is due. All four exist: nr4a3 r0 and r1 have landed, nr4a1 r0 and r1 are
#   running. A leg bought only to exercise this feature is the spend §5 forbids, so the rung waits for a
#   leg the science needs anyway rather than manufacturing one.
PRUNE_ELIGIBLE_MODES = ("5aks_smoke",)


def prune_chk_for_mode(mode, env=None):
    """`"1"` iff `mode` is at or below the ladder rung the prune has reached, and nobody has forced it off.

    ★ THE ALLOWLIST IS THE ENABLE; `TVAST_PRUNE_CHK` IS ONLY A KILL SWITCH. The first design had it the
    other way round -- allowlist AND a repository variable set to 1 -- and that was worse in the direction
    that matters, because the variable is the part nobody can constrain: it is GLOBAL, it stays set until
    someone remembers to unset it, and it therefore has to be trusted for as long as it exists. Membership
    in this tuple is a commit, with a test that fails when it changes, which is a far better fit for "one
    rung at a time" than a value living in repository settings. Setting `TVAST_PRUNE_CHK=0` forces it off
    everywhere without a deploy, which is the only direction worth having a remote control for.

    Returns the string the jobspec carries, because that is what a host reads. Never raises on an unknown
    mode -- an unknown mode is simply not on the allowlist, which is the safe answer."""
    env = os.environ if env is None else env
    if str(env.get("TVAST_PRUNE_CHK", "")).strip() in ("0", "false", "FALSE", "no"):
        return "0"
    return "1" if mode in PRUNE_ELIGIBLE_MODES else "0"


def warmup_ckpt_iters_for(leg_id, mode, sizing=None, timestep_fs=None, warmup_timestep_fs=None):
    """This leg's warmup checkpoint interval, as a str. Derived per ARM wherever a mode opts in. PURE.

    THE DERIVATION, in one line: the reference arm's exposure is the BUDGET, and every other arm gets the
    LARGEST interval that fits inside it and still divides the warmup target exactly.

        budget_s = MODES[mode]["warmup_ckpt_iters"] x rate[CKPT_REFERENCE_ARM]
        interval = max{ d : d divides warmup_target, d <= reference interval, d x rate[arm] <= budget_s }

    Capped at the reference interval so this can only ever REFINE an arm's cadence. Equalising a fast arm
    UPWARD would buy exposure nobody asked for on an arm that is not failing, and the mode's own value is the
    coarsest cadence that was ever authorised.

    ★ AND THE COMMIT-OVERHEAD FLOOR IS SATISFIED FOR FREE — it is not a second selection constraint, it is a
    consequence, and the proof is worth writing down because the obvious way to "protect" against
    over-committing is to add a clamp that cannot fire. Per-commit overhead is a fixed `COMMIT_OVERHEAD_S`
    against `interval x rate` seconds of MD, so

        overhead fraction = COMMIT_OVERHEAD_S / EXPOSURE_S

    — a function of the EXPOSURE alone, falling monotonically as the interval grows. This picks the LARGEST
    interval inside the budget, i.e. the one with the SMALLEST overhead of any admissible choice, so if any
    admissible interval clears `MAX_COMMIT_OVERHEAD_FRAC` then the one returned does. Overhead can therefore
    only be a problem if the BUDGET ITSELF is too small, which is a fact about the reference arm's interval
    and not about this derivation — so it is asserted by `ckpt_overhead_fraction` and pinned by a test rather
    than silently clamped here.

    An unmeasured timestep, an unmeasured arm, or a mode that has not opted in all return the mode's own flat
    value — the current behaviour, never a guess.
    """
    sizing = MODES[mode] if sizing is None else sizing
    ref = str(sizing.get("warmup_ckpt_iters") or "64")
    if not sizing.get("per_arm_ckpt"):
        return ref
    dt, wdt = resolve_timesteps(mode, timestep_fs, warmup_timestep_fs)
    rates = arm_iteration_rates(dt)
    arm = arm_of_leg(leg_id)
    rate, ref_rate = rates.get(arm), rates.get(CKPT_REFERENCE_ARM)
    if arm == CKPT_REFERENCE_ARM or not rate or not ref_rate:
        return ref
    target = warmup_target_iters(dt, wdt)
    if not target:
        return ref
    budget_s = int(ref) * ref_rate
    fits = [d for d in _divisors_up_to(target, int(ref)) if d * rate <= budget_s]
    # `or [1]` cannot fire while any single iteration fits the budget; an arm slower than the whole budget
    # per iteration would otherwise raise, and a crash in a launcher is worse than one commit per iteration.
    return str(max(fits or [1]))


def ckpt_exposure_s(leg_id, mode, sizing=None, timestep_fs=None, warmup_timestep_fs=None):
    """SECONDS of warmup sampling this leg can lose to a host reclaim before its first commit — the quantity
    the per-arm split exists to equalise, and the one the readout should print. PURE.

    Returns None where no rate was measured for this arm at this timestep, because a fabricated exposure is
    worse than an absent one.
    """
    sizing = MODES[mode] if sizing is None else sizing
    dt, wdt = resolve_timesteps(mode, timestep_fs, warmup_timestep_fs)
    rate = arm_iteration_rates(dt).get(arm_of_leg(leg_id))
    if not rate:
        return None
    return int(warmup_ckpt_iters_for(leg_id, mode, sizing, timestep_fs, warmup_timestep_fs)) * rate


def ckpt_overhead_fraction(leg_id, mode, sizing=None, timestep_fs=None, warmup_timestep_fs=None):
    """Fraction of this leg's warmup wall-clock spent committing, at the interval it will actually run.

    `COMMIT_OVERHEAD_S / EXPOSURE_S` — see `warmup_ckpt_iters_for`. This is the other half of the trade-off
    the interval sits in: SMALL interval => little work at risk but a large fixed cost paid often; LARGE
    interval => cheap but a reclaim destroys more. Reported rather than clamped, so a re-measurement that
    pushes it past `MAX_COMMIT_OVERHEAD_FRAC` fails a test in front of a human instead of being absorbed.
    """
    e = ckpt_exposure_s(leg_id, mode, sizing, timestep_fs, warmup_timestep_fs)
    return None if not e else COMMIT_OVERHEAD_S / e


# =============================================================================================================
# live operations (need credentials)
# =============================================================================================================
def _s3():
    import boto3
    return boto3.client("s3")


def _split_uri(uri):
    body = uri.split("://", 1)[1]
    bucket, _, key = body.partition("/")
    return bucket, key


def blocked_machine_ids(bucket=None, prefix=None):
    """Machines observed refusing starts, THIS lane's ∪ the SHARED cross-lane set. [] if unavailable.

    Recorded by collect() and consumed by submit() so a host that cannot schedule us stops winning
    selection. It is the availability term the $/ns ranking cannot express: a machine that never starts has
    infinite realised cost per ns yet reads as the cheapest offer on the board.

    ⚠ THE UNION WAS ADDED 2026-07-27, after the step 1 fan-out rented machine 46392 — already on THIS lane's
    list — because the two lanes kept separate sets and neither could see the other's. A capacity refusal is a
    property of the machine, so every lane may act on it; see `vast_machine_blacklist` for the scope split.
    """
    # ⛔ RETIRED (trimcrae, 2026-07-31: "You've gotta just stop doing the blacklist"). The switch and the
    # evidence live in `vast_machine_blacklist` — one home. Checked HERE as well as inside `union` because
    # this function's own `except` fallback returns `local`, i.e. the lane's durable ids, on any error
    # reaching the shared set: without this line a transient S3 blip would quietly re-enable the very list
    # that has been starving the board. Bounded protection is untouched — `submit`'s in-call capacity-refusal
    # skip and the `used` set that stops two legs of one wave landing on one box.
    try:
        import vast_machine_blacklist as _vmb0
        if not _vmb0.durable_enabled():
            return []
    except Exception:  # noqa: BLE001 — if the module cannot even be imported, exclude nothing
        return []
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    local, s3 = [], None
    try:
        s3 = _s3()
        st = json.loads(s3.get_object(Bucket=b, Key=f"{p}/_lane_state.json")["Body"].read())
        local = [str(m) for m in (st.get("_blocked_machines") or [])]
    except Exception:  # noqa: BLE001 — no state yet, or unreadable; fall through to the shared set alone
        pass
    try:
        import vast_machine_blacklist as vmb
        # ⛔⛔ THE BACKFILL IS GONE, AND ITS REMOVAL IS THE FIX (measured 2026-07-28).
        #
        # This used to call `vmb.backfill(s3, b, local, lane="rung5a_ks")` on EVERY read, on the argument
        # that "every id on `_blocked_machines` is a start refusal, i.e. host-scoped by construction". Both
        # halves of that were false, and together they were the one route by which a perishable refusal
        # became a permanent cross-lane exclusion:
        #
        #   1. `backfill` synthesised its own reason string ("backfilled from …'s refuse-to-start list"),
        #      which carries none of `vast_machine_blacklist._CAPACITY_MARKERS` — so `classify_reason` filed
        #      it CLASS_HOST and `publish`'s capacity refusal never fired. 32 of the 41 entries in
        #      `vast-blacklist-snapshot-before-clear.json` are that exact string.
        #   2. `_blocked_machines` is now WAVE-SCOPED and, per `collect`'s own note, "the ONLY thing that
        #      adds to `blocked` is the `resources_unavailable` branch, i.e. the whole set is the PERISHABLE
        #      capacity class". Promoting this tick's busy hosts to a permanent set is the exact inversion of
        #      what the wave-scoping was for — and it ran on every read, so clearing the shared set could
        #      not stick: the next collect refilled it.
        #
        # Nothing replaces it. The durable path is unchanged and still fires where the evidence is: the
        # `resources_unavailable` branch in `collect` calls `vmb.publish` with the REAL reason, which
        # classifies as capacity and is correctly refused. A genuine host verdict would be published the
        # same way and would be accepted.
        return vmb.union(local, s3, b)
    except Exception:  # noqa: BLE001 — the shared set is an optimisation and must never block a launch
        return local


def committed_progress(uid, bucket=None, prefix=None):
    """(phase, iteration, monotonic_scalar) of the furthest COMMITTED iteration for this unit.

    This is the progress signal, and it is deliberately the commit store rather than "an instance exists".
    On Vast a rented box can sit up with a dead container or an idle GPU and look perfectly healthy; three
    separate silent stalls on the GCP ternary lane all presented as a live VM. The commit store is the only
    durable evidence that the SCIENCE advanced, and it survives the instance.

    The scalar orders production above warmup so a warmup->production transition can never read as a
    regression. Returns (None, 0, 0) when nothing is committed yet (setup / pre-equil / minimise).

    ★★ IT COUNTS A GENERATION ONLY ONCE ITS `COMMITTED.json` MANIFEST EXISTS (2026-07-30). This used to
    count a generation the moment ANY object appeared under `iter-N/`, which is NOT the rule the restorer
    uses: `_BaseCommitStore.restore_latest` walks `list_committed`, and that returns only generations that
    have their manifest — because `_persist` uploads the .nc, then the .chk, then "manifest LAST",
    precisely so a torn upload is never mistaken for a durable commit.

    The two rules disagreeing is not cosmetic. Measured on the closure triangle's T3 ternary leg: the board
    printed `committed: production/1800` while the host rented seconds later printed
    `restore -> production@iter 1760`. Both were reading the same prefix correctly. The leg then re-ran the
    same 40 iterations, and because the BOARD's number went up each time, the rework was invisible — it
    presented as "the host is slow", then as a wedge, and cost a morning of diagnosis pointed at hardware.
    Reporting the frontier a host would actually resume from makes that rework show as what it is: no
    progress. Which generations are excluded, and why, is `commit_store_audit.py`.

    ⚠ Manifest PRESENCE is all a listing can prove. A generation whose manifest exists but whose
    `system_fingerprint` belongs to another configuration is also refused by `restore_latest`, and
    detecting that needs a GET per manifest — too expensive for a poll that runs every few minutes, so it
    stays in the audit tool. This function is therefore still an UPPER bound on restorable progress; it is
    simply no longer an upper bound that a half-finished upload can move.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    base = f"{p}/commits/{uid}"
    best = {"warmup": 0, "production": 0}
    counted = {"warmup": 0, "production": 0}
    try:
        pag = _s3().get_paginator("list_objects_v2")
        for page in pag.paginate(Bucket=b, Prefix=f"{base}/"):
            for obj in page.get("Contents", []):
                m = re.search(r"/(warmup|production)/iter-(\d+)/", obj["Key"])
                if not m:
                    continue
                ph, it = m.group(1), int(m.group(2))
                counted[ph] = max(counted[ph], it)
                if obj["Key"].endswith("/" + COMMIT_MANIFEST):
                    best[ph] = max(best[ph], it)
    except Exception as e:  # noqa: BLE001 — a listing failure must not be read as "no progress"
        print(f"[progress] could not list {base}: {type(e).__name__}: {e}")
        return (None, 0, -1)
    # Never silent: a gap here is bytes in S3 that no host will ever resume from, and saying so is the
    # whole point of the change above.
    for ph in ("production", "warmup"):
        if counted[ph] > best[ph]:
            print(f"[progress] {uid}: {ph} has objects at iter {counted[ph]} but the newest generation "
                  f"with a {COMMIT_MANIFEST} is {best[ph] or 'none'} — a host resuming here starts at "
                  f"{best[ph] or 0}, not {counted[ph]}. Torn or in-flight upload; "
                  f"commit_store_audit.py says which.")
    if best["production"]:
        return ("production", best["production"], 1_000_000 + best["production"])
    if best["warmup"]:
        return ("warmup", best["warmup"], best["warmup"])
    return (None, 0, 0)


def marker_predates_host(marker_age_min, instance_up_h):
    """Does this unit's phase marker belong to an EARLIER attempt than the host we are looking at? PURE.

    The marker and run.log live at a per-UNIT S3 key, never a per-attempt one, so a freshly rented host shows
    its predecessor's marker until it writes its own. Comparing the marker's age against the instance's own
    uptime is the whole test, and it is the same shape as `_record_is_newer_than_instance` — which exists
    because the launch side learned this lesson first, on a stale `failed` record that would have reaped a
    freshly launched host.

    Returns False whenever it cannot tell (no marker age, or an instance with no usable start date). Failing
    towards "not stale" is deliberate: a spurious ⚠ on a genuinely current marker would teach the reader to
    ignore the flag, which is the same alarm-fatigue failure `reap_landed` was built to end.
    """
    if marker_age_min is None or instance_up_h is None:
        return False
    try:
        up_min = float(instance_up_h) * 60.0
        if up_min <= 0:
            return False
        return float(marker_age_min) > up_min
    except (TypeError, ValueError):
        return False


def phase_and_log(uid, bucket=None, prefix=None, tail=8):
    """(phase_marker, age_minutes, log_tail_lines) for a unit, from S3. [] if not written yet.

    WHY THIS IS NOT OPTIONAL. The commit-store census (`committed_progress`) is the durable progress signal,
    but it reads ZERO for the whole cold start — stage, pre-equilibrate, solvate+parameterise, minimise —
    which is tens of minutes and is exactly where the GCP lane's three silent stalls lived (an am1bcc
    cold-cache wait at 0 % GPU, a 25000-step minimise, and a warmup NaN). Without the phase marker and the
    log tail, every one of those looks identical to a healthy leg that has simply not committed yet. The
    marker says WHICH phase; the age of the marker says whether that phase is moving.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    base = f"{p}/legs/{uid}"
    s3 = _s3()
    phase, age_min, lines, log_age = None, None, [], None
    try:
        o = s3.get_object(Bucket=b, Key=f"{base}/phase.txt")
        phase = o["Body"].read().decode(errors="replace").strip()
        age_min = (time.time() - o["LastModified"].timestamp()) / 60.0
    except Exception:  # noqa: BLE001 — not written yet (image still pulling)
        pass
    try:
        o = s3.get_object(Bucket=b, Key=f"{base}/run.log")
        log = o["Body"].read().decode(errors="replace")
        raw = [ln for ln in log.splitlines() if ln.strip()]
        # SURFACE THE DIAGNOSTIC LINES, not just the tail. The lines that answer "is this advancing and is it
        # healthy" — the per-chunk `[timing]`, the `[barrier] committed checkpoint at iteration N`, the
        # spot-driver's phase transitions and targets, and any NaN traceback — are emitted rarely and are
        # immediately buried by hundreds of openff/openmmtools INFO lines. A pure tail therefore shows the
        # noise and hides the signal, which is how a leg can look uninformative while its log says exactly
        # what is happening.
        keys = ("[timing]", "[barrier]", "[spot-driver]", "[tfep]", "NaN", "Traceback", "ERROR", "ABORT")
        hits = [ln for ln in raw if any(k in ln for k in keys)]
        # ★★ THE TARGETS LINE IS PINNED, BECAUSE `hits[-tail:]` EVICTS IT AS A LEG AGES (measured
        # 2026-07-29, 7:02 PM ET). `[spot-driver] warmup_target=N (ci=..) prod_target=M (ci=..)` is printed
        # ONCE, at driver start, and it is the ONE home for the denominator of "% complete" — the driver
        # computes it from OpenFE settings no reader here has an MD stack to re-derive.
        #
        # It is not scrolling out of a byte window: the whole object is in `log` above. It is being evicted
        # from the KEYWORD selection, which keeps only the last `tail` matches. Production emits a
        # `[timing]` and a `[barrier]` every 40 iterations, so ~75 lines accumulate over 1500 iterations and
        # push the startup lines off the front. `valB r2 ternary` had rendered a percentage and an ETA all
        # evening and then went to `— / —`: every other cell fine, the leg advancing, only the denominator
        # gone. Every leg does this as it ages, so the overnight board would have blanked one row at a time.
        #
        # Pinning is the correct fix rather than a bigger `tail` (which only moves the age at which it
        # happens) or a remembered copy in the lane state (which would be a SECOND HOME for a number this
        # log already owns — CLAUDE.md rule 1 — and would go stale across a re-scope). One line, read from
        # the driver's own output, on every poll.
        _targets_line = next((ln for ln in raw if "warmup_target=" in ln), None)
        lines = (hits[-tail:] + ["--- raw tail ---"] + raw[-4:]) if hits else raw[-tail:]
        if _targets_line and _targets_line not in lines:
            lines = [_targets_line] + lines
        # The openmmtools per-chunk progress line, which is the ONLY thing emitted between the driver's
        # (buffered) [timing] lines during a chunk. Pulled out separately so the compact summary can carry
        # it: "Iteration 3/8" is the difference between watching a live warmup and watching a frozen log.
        it_lines = [ln for ln in raw if "Iteration " in ln and "/" in ln]
        if it_lines:
            lines.append("LAST-ITER " + it_lines[-1].strip()[:80])
        # The log's OWN mtime, separately from the phase marker's. The marker is written only when the
        # phase CHANGES, so inside a long phase its age just grows and says nothing. The sync loop pushes
        # the log every 2 min, so a log older than ~4 min means the uploader stopped — which is a different
        # (and worse) fact than "this phase is taking a while", and the two are indistinguishable without it.
        log_age = (time.time() - o["LastModified"].timestamp()) / 60.0
    except Exception:  # noqa: BLE001
        pass
    return phase, age_min, lines, log_age


def leg_records(bucket=None, prefix=None):
    """{unit_id: leg.json} for every unit that has written one."""
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    out = {}
    try:
        s3 = _s3()
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=b, Prefix=f"{p}/legs/"):
            for obj in page.get("Contents", []):
                if not obj["Key"].endswith("/leg.json"):
                    continue
                try:
                    d = json.loads(s3.get_object(Bucket=b, Key=obj["Key"])["Body"].read().decode())
                except Exception as e:  # noqa: BLE001
                    print(f"[collect] unreadable {obj['Key']}: {e}")
                    continue
                d["_s3_last_modified"] = obj["LastModified"].strftime("%Y-%m-%dT%H:%M:%SZ")
                out[d.get("unit_id") or obj["Key"]] = d
    except Exception as e:  # noqa: BLE001
        print(f"[collect] could not list leg records: {type(e).__name__}: {e}")
    return out


def supersede_failed_record(match, bucket=None, prefix=None, dry_run=False):
    """ARCHIVE-AND-CLEAR a unit's `status=failed` leg.json, once its cause is fixed and it has been relaunched.

    ★ WHY A STALE FAILED RECORD IS ACTIVELY DANGEROUS, not untidy. `watchdog_policy.classify` returns FAILED
    only when `has_failed_record AND not instance_alive`, and `has_failed_record` is read straight off the
    live `leg.json`. So relaunching a fixed leg does not clear the old record — it merely SUPPRESSES it for
    as long as an instance happens to be alive. Two consequences, both bad and both overnight:

      1. **It masks a real failure.** The moment the new attempt exits without writing a leg.json (a
         preemption, say), the watchdog goes red again on the OLD record, with the old rc and the old empty
         log tail — an alert indistinguishable from a genuine new failure, pointing at a cause already fixed.
      2. **It blocks the recovery it is supposed to trigger.** The watchdog deliberately refuses to relaunch a
         unit carrying a failed record (a code/data fault would just fail again on the next host). With a
         stale record present, that refusal fires against a leg whose fault is gone — so the automatic
         overnight recovery does not happen and nobody is awake to notice.

    Observed on RUNG 5a-KS: the NR4A1 leg recorded `status=failed` at 5:37 PM ET from the pre-mapper-fix
    abort; the watchdog went red at 6:39 PM and green again at 7:40 PM purely because a relaunch made an
    instance alive. Nothing had been cleared.

    THE RECORD IS ARCHIVED, NEVER DELETED OUTRIGHT: it moves to `<unit>/superseded/leg-<utc>.json`, the same
    discipline as the `attempts/` log archive, so the forensic trail of a failure survives the clearing of its
    operational effect. A `status=done` record is REFUSED — this must never be able to destroy a result.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    s3 = _s3()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    cleared, skipped = [], []
    for uid, rec in sorted(leg_records(bucket=b, prefix=p).items()):
        if match not in uid:
            continue
        status = rec.get("status")
        if status == "done":
            skipped.append({"unit_id": uid, "why": "status=done — a RESULT, never superseded"})
            continue
        if status != "failed":
            skipped.append({"unit_id": uid, "why": f"status={status!r} — nothing to clear"})
            continue
        base = f"{p}/legs/{uid}"
        moved = []
        for name in ("leg.json", "status.json"):
            key = f"{base}/{name}"
            try:
                s3.head_object(Bucket=b, Key=key)
            except Exception:  # noqa: BLE001 — absent is fine; status.json need not exist
                continue
            dest = f"{base}/superseded/{name.replace('.json', '')}-{stamp}.json"
            if not dry_run:
                s3.copy_object(Bucket=b, CopySource={"Bucket": b, "Key": key}, Key=dest)
                s3.delete_object(Bucket=b, Key=key)
            moved.append({"from": key, "to": dest})
        cleared.append({"unit_id": uid, "rc": rec.get("rc"), "phase": rec.get("phase"),
                        "recorded_utc": rec.get("updated_utc"), "archived": moved})
        print(f"[supersede] {uid}: status=failed (rc={rec.get('rc')}, phase={rec.get('phase')}) "
              f"-> archived under superseded/ and cleared" + (" [DRY RUN]" if dry_run else ""), flush=True)
    for sk in skipped:
        print(f"[supersede] skip {sk['unit_id']}: {sk['why']}", flush=True)
    if not cleared:
        print(f"[supersede] no failed record matched {match!r} — nothing to clear", flush=True)
    return {"cleared": cleared, "skipped": skipped, "dry_run": dry_run}


# =============================================================================================================
# WHICH UNITS STILL NEED A HOST — one definition, used by the launcher AND by the gate in front of it
# =============================================================================================================
# ★★ WHY THIS IS A FUNCTION AND NOT TWO COPIES (2026-07-27; it cost three launches and a false alarm).
#
# `submit()` has always skipped units that are already done or already running — correctly, and it is why the
# 12:29 PM and 12:39 PM ET ticks rented NOTHING. But the MARKET GATE in front of it had no such notion: the
# workflow called `--market-gate 4` with a hardcoded 4, so once all four units were live the gate went on
# pricing a four-unit purchase every tick, clearing, and DISPATCHING a launch whose only possible outcome was
# "nothing to rent". Three launch jobs in 25 minutes, each recorded `launched`.
#
# That is not merely wasteful CI. It put a board reading of 2.032x basis — over trimcrae's buy line — directly
# beside the word `launched` in the lane's own ledger, which reads as "we bought at 2.032x". We did not; we
# bought nothing. But a ledger that has to be disbelieved is worse than no ledger, and the only durable fix is
# for the gate to ask the same question the launcher asks, from the same code.
#
# So: ONE home for "which units still need renting" (CLAUDE.md §1), consulted by both.
def unit_hosts(uids, key=None):
    """{"live": {uid: inst}, "dead": {uid: inst}} — every labelled instance for these units, SPLIT on whether
    it is still working. Read-only, one API call.

    ★★ THE SPLIT IS THE WHOLE POINT, AND ITS ABSENCE COST THREE RUNG 2b REPLICATES A NIGHT (measured
    2026-07-27). This function used to return one dict, into which ANY labelled instance went "whatever state
    it is in", justified as the conservative direction: mistaking a dead host for a live one merely delays a
    relaunch, while mistaking a live one for dead rents a second GPU. That trade is real and the second half
    of it is still honoured (see `vast_instance_occupies_slot`: a fresh rental still pulling its image counts
    as occupied). The first half is what was wrong — the "delay" has no upper bound. At 6:17 PM ET
    `task=collect` printed `up=exited` for three of four replicate hosts; at 6:12 PM the gate in front of it
    had already declined to price the market at all, on the grounds that "4 already running". Nothing in the
    loop would ever have re-placed those three: the count that decides whether to look at the board was made
    from instance EXISTENCE, and an exited instance exists forever until something destroys it.

    A `stopped` box also bills its volume at a HIGHER rate than a running one, so the dead half is not inert —
    which is why it is returned rather than dropped. `submit` destroys the dead host of any unit it is about
    to re-place, so the fix cannot produce the duplicate the old comment feared.
    """
    key = key or os.environ.get("VAST_API_KEY")
    if not key:
        return {"live": {}, "dead": {}, "occupied_machines": set()}
    # IMPORTED, NOT RE-TYPED (CLAUDE.md §1). A local `!= "stopped"` here would be a fourth private copy of
    # "is this box working", free to disagree with the watchdog's and the collector's — and disagreeing
    # copies of exactly this predicate are what produced both of today's incidents.
    from gpu_backend import vast_instance_occupies_slot
    live, dead, occupied = {}, {}, set()
    for i in _vast_request("GET", "/instances/", key).get("instances", []) or []:
        # ★★ OCCUPANCY IS COUNTED FIRST, ACROSS *EVERY* INSTANCE THIS ACCOUNT HOLDS — before the label
        # filter, so it sees the step 1 fan-out's boxes as well as this lane's. See `occupied_machines` in
        # the return value for why this exists; the short version is that a machine we are already sitting on
        # is a machine that will refuse our second rental, and it does not stop being that because a
        # different lane rented it.
        mid = i.get("machine_id")
        if mid is not None:
            occupied.add(str(mid))
        lab = i.get("label") or ""
        if not str(lab).startswith(LABEL_PREFIX):
            continue
        for uid in uids:
            if label_matches_unit(lab, uid):
                (live if vast_instance_occupies_slot(i) else dead)[uid] = i
    return {"live": live, "dead": dead,
            # ★★ MACHINES WE ARE ALREADY ON — THE EXCLUSION THAT WAS MISSING (measured 2026-07-29, 9:25 AM
            # ET, and it is the reason r2 could not stay placed).
            #
            # WHAT HAPPENED. r1 was running on machine 28164 (instance 46191306, advancing to warmup/1024).
            # The gate priced the board, machine 28164 came back as the cheapest offer on it, and the
            # launcher rented r2 there too — instance 46197224, the SAME machine. Twelve minutes later that
            # host answered `resources_unavailable` and `collect` destroyed it: `⛔ DESTROYED this pass
            # (capacity refusal on machine 28164; ...)`. The machine had room for one of our GPUs, not two.
            # It is in the committed record twice over: `ternary-vast-market-hold.json` @ 2026-07-29T13:01:41Z
            # prices exactly one offer, machine 28164, in the same file that names our own instance 46191306
            # on machine 28164.
            #
            # WHY NOTHING STOPPED IT. `submit` already spreads units ONE PER MACHINE — but only within a
            # single launch (`used` starts from `blocked_machine_ids()` and grows as that call rents). It has
            # no notion of a machine occupied by a host rented on an EARLIER tick, and `blocked_machine_ids`
            # cannot supply one: its only source is the `resources_unavailable` branch. So nothing in the
            # rental path could exclude a machine merely for already carrying our own work. This is
            # CLAUDE.md §6's named failure — "a host that never starts has infinite realised $/ns, invisible
            # to $/ns ranking, so without the exclusion it keeps winning selection and keeps failing" —
            # arriving through occupancy rather than through a refusal.
            #
            # ⚠ IT DELIBERATELY COUNTS *EVERY* INSTANCE, INCLUDING TERMINAL-LOOKING ONES. `exited` on Vast is
            # routinely transient (`submit` refuses to destroy on one observation for exactly that reason,
            # and r1's own instance read `exited` at 13:01 and `running` at 13:05), and a `stopped` box can be
            # restarted and reclaim its GPU. A machine carrying an instance we have not destroyed is a
            # machine that may take its slot back, so it is not a place to put a second unit. Using
            # `vast_instance_occupies_slot` here instead would re-open the hole every time a live host
            # happened to be observed mid-flicker.
            #
            # ⚠ AND IT IS NOT A BLACKLIST. Nothing is written down and nothing is remembered: this set is
            # recomputed from the live instance list on every tick, so the moment a corpse is reaped its
            # machine is purchasable again. That keeps trimcrae's 2026-07-27 ruling intact — a capacity
            # refusal must stay PERISHABLE and must never become a durable cross-lane exclusion — because
            # this is not a refusal record at all, it is a statement about where we are sitting right now.
            #
            # COST OF THE TRADE, stated honestly: we may skip a machine that genuinely had a second free
            # GPU. That is the same trade `submit`'s existing one-unit-per-machine rule already makes, on
            # the same evidence (machine 53989 took two legs on 2026-07-25 and refused both starts), and §6's
            # measured premise applies — ~23 independently-priced hosts with a flat floor, so the next host
            # costs what this one does. A refused rental costs a teardown and a cold start; a slightly
            # different host costs nothing.
            "occupied_machines": occupied}


def live_unit_hosts(uids, key=None):
    """{unit_id: instance record} for every unit whose host is still WORKING. Thin view over `unit_hosts`."""
    return unit_hosts(uids, key=key)["live"]


def rented_usd_per_ns(inst):
    """The $/ns a LIVE instance is actually being billed. PURE (given the record). None if ungradeable.

    ★★ THIS — NOT A BOARD MEAN, AND NOT THE LAUNCHER'S `dph≈` LINE — IS THE NUMBER THAT ANSWERS "what are we
    paying?" (CLAUDE.md §1). The `dph≈` printed at rental is the OFFER's `dph_total`: the market floor plus
    the disk line the *search* priced, which reads LOW against the rate the instance is actually billed
    (`vast_rate_forensics.py`). A gate's `mean_usd_per_ns` is a different thing again — the mean over the n
    cheapest offers on the board at some instant, which is a property of the MARKET and not of any purchase.
    Filing either one next to an outcome of `launched` is how a lane comes to report a rate it never paid.

    The instance's own `dph_total` is bid + the real volume's disk line, i.e. what Vast charges per hour, so
    dividing it by the card's benched throughput gives the rate we are truly paying per nanosecond.
    """
    import vast_cost_model as vcm
    try:
        nsph = vcm.ns_per_hour(inst.get("gpu_name"))
        dph = float(inst.get("dph_total"))
    except (TypeError, ValueError, KeyError):
        return None
    if not nsph or dph <= 0:
        return None
    return dph / (nsph * max(1, int(inst.get("num_gpus") or 1)))


def rented_rate_row(uid, inst):
    """One allow-listed 'what this host actually costs' row for the ledger. PURE.

    Allow-listed for the same reason `vast_rate_forensics.SAFE_FIELDS` is: a Vast instance record carries
    `jupyter_token`, `ssh_host` and `public_ipaddr`, and this row gets COMMITTED to a public repo. Field
    names are evidence; several field values are credentials.
    """
    import congeneric_fanout as cf
    upn = rented_usd_per_ns(inst)
    basis = cf.basis_usd_per_ns()
    row = {"unit_id": uid, "instance": inst.get("id"), "machine_id": inst.get("machine_id"),
           "gpu": inst.get("gpu_name"), "dph_total_usd_h": inst.get("dph_total"),
           "dph_base_usd_h": inst.get("dph_base"), "cur_state": inst.get("cur_state"),
           "actual_status": inst.get("actual_status")}
    if upn is None:
        # Never a fabricated zero in a PRICE field — the failure mode this repo keeps paying for.
        row["usd_per_ns"] = None
        row["verdict"] = "UNGRADEABLE — no benched throughput for this card, or no rate on the record"
        return row
    row["usd_per_ns"] = round(upn, 6)
    row["x_basis"] = round(upn / basis, 3)
    row["over_buy_line"] = upn > buy_ceiling_usd_per_ns()
    return row


def breaker_verdicts(uids, records, bucket=None, prefix=None):
    """{unit_id: verdict} for every unit the failure breaker has an OPINION about. THE one call site.

    ★★ ONE CALL SITE, NOT TWO (CLAUDE.md §1; the property this restores was asserted by a test that could
    not see it break). `outstanding_units` and `submit` each used to build their own `lfb.decide(...)` loop,
    and `tests/test_leg_failure_breaker.py` pinned that with `src.count("lfb.decide(") >= 2` — a source-text
    assertion that counts CALLS and cannot compare ARGUMENTS. Two loops that pass different inputs satisfy
    it perfectly while returning different answers, which is exactly the drift the test was written to stop.
    Now there is one loop, both callers use it, and the same-verdict test runs both paths and compares the
    sets they withhold.

    Returns only the units with a verdict worth carrying — blocked, or blocked-but-superseded — because a
    unit the breaker has nothing to say about must not appear in a readout as though it did.

    Fails OPEN throughout (an unreadable attempt listing or commit store yields no block), deliberately
    opposite to `submit`'s instance-list check: guessing wrong here costs at most one rental of a unit that
    may well now succeed, whereas guessing wrong there double-buys on top of running work.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    out = {}
    s3 = None
    for u in uids:
        rec = (records or {}).get(u)
        # Cheap exit: only a `failed` record can possibly be blocked, so only that costs S3 calls.
        if (rec or {}).get("status") != "failed":
            continue
        if s3 is None:
            s3 = _s3()
        # ONE read of the commit store, used for BOTH questions it answers: whether work landed after the
        # failed record (supersession), and where the current failure STREAK starts (`since_utc`). Attempts
        # older than the last commit were survived and are not part of the streak — see `count_attempts`.
        _commit_utc = lfb.newest_commit_utc(s3, b, p, u)
        d = lfb.decide(
            rec,
            lfb.count_attempts(s3, b, p, u, since_utc=_commit_utc),
            superseding=lfb.superseding_evidence(
                rec,
                newest_commit_utc=_commit_utc,
                eviction=lfb.read_eviction(s3, b, p, u)))
        if d["block"] or d.get("superseded_by"):
            out[u] = d
    return out


# =============================================================================================================
# A SHAKEOUT'S EVIDENCE HAS A SHELF LIFE. A PRODUCTION UNIT'S RESULT DOES NOT.
# =============================================================================================================
# ★★ THE DEFECT THIS CLOSES, MEASURED 2026-07-31 ON THIS LANE AND SEEN THE SAME MORNING ON NR-V04.
# `task=5aks-smoke` was dispatched at 7:01 AM ET to shake the 5a-KS pipeline out before the four real legs.
# It rented NOTHING and reported green. The ledger row is unambiguous —
#     outcome "nothing-to-launch" … "no unit of mode 5aks_smoke needs a host — 1 done, 0 already running"
#     n_requested 0, n_rented 0, PAID $0
# — because `outstanding_units` found the smoke unit's `leg.json` already `status=done` in S3, written by the
# smoke of **2026-07-26**, five days earlier. The launch job nonetheless printed
# `[verify-armed] 5aks_smoke: all 1 unit(s) present and enabled`, which reads exactly like a shakeout that
# passed. NR-V04's Arm E pilot printed its own version of the same thing the same morning
# (`[skip] … — result already in S3`), so this is a SHAPE, not a one-lane slip.
#
# ⚠ THE IDEMPOTENT SKIP ITSELF IS CORRECT AND MUST NOT BE REMOVED. For a PRODUCTION unit, "a done result is
# already in S3" is exactly the right reason not to rent: it is what makes a spot re-dispatch RESUME rather
# than pay twice, and deleting it would re-buy landed work on every tick (CLAUDE.md §6, and the 13-edge
# near-miss in §7). The bug is narrower: a SHAKEOUT is keyed the same way as a result.
#
# WHY A SHAKEOUT IS DIFFERENT IN KIND. Its product is not the ΔG — `smoke`'s ΔG is meaningless by
# construction and this file already says so. Its product is the OBSERVATION that today's image, today's
# credential, today's stage cache and today's commit store work together on a real host. That observation is
# about a moment. Stored as a durable artifact with no expiry it becomes a CERTIFICATE, and a certificate
# that never expires turns §6's `smoke -> one real leg -> fleet` ladder into a permanent no-op after its
# first success — the "reports success while measuring nothing" shape the ladder exists to prevent.
#
# THE SHELF LIFE IS A JUDGEMENT CALL AND IS NAMED AS ONE. Six hours: long enough that a smoke followed by its
# real legs inside one working session does not re-rent, short enough that a shakeout standing in front of a
# spend is always evidence about the pipeline being bought into rather than about last week's. It is not
# derived from anything measured, so it is a constant with a rationale rather than a computed value.
SHAKEOUT_EVIDENCE_MAX_AGE_H = 6.0


def is_shakeout(mode):
    """True when `mode` is a plumbing shakeout rather than a science unit. PURE."""
    return bool((MODES.get(mode) or {}).get("shakeout"))


def shakeout_evidence_is_stale(record, now_utc=None, max_age_h=None):
    """True when a shakeout's `done` record is too old to still be evidence about today's pipeline. PURE.

    `record` is a `leg.json` dict as returned by `leg_records`. A record with NO usable timestamp is treated
    as STALE, deliberately: the only way to be wrong in that direction is to re-run a ~$0.15 shakeout, while
    being wrong in the other direction is exactly the silent no-op above. Cheap side, safe side.

    ★★ THE RECORD'S OWN STAMP DECIDES; THE S3 OBJECT'S MTIME IS ONLY A FALLBACK — and getting that
    precedence backwards made this whole guard inert (measured 2026-08-01). `updated_utc` is written by the
    HOST at the moment the leg finished, so it is a property of the RUN. `_s3_last_modified` is a property
    of the OBJECT, and an object's mtime moves for reasons that have nothing to do with the science: a
    re-upload, a copy, an archival sweep, a lifecycle transition. This function used to read the object
    mtime FIRST, so a six-day-old certificate whose object had been touched recently read as fresh — and
    `task=5aks-smoke` returned `nothing-to-launch` against a `leg.json` whose own content says
    `2026-07-26T21:07:19Z`. That is CLAUDE.md §4's rule exactly: **a populated field is not a measured one**,
    and here the populated field belonged to the storage layer rather than to the run. `unit_row` at the
    bottom of this file already had the precedence right; this was the odd one out.

    ⚠ KNOWN LIMIT, stated rather than silently accepted: freshness is measured in TIME, not in CODE. A
    shakeout that ran 30 minutes before a change still certifies the pipeline as it was BEFORE that change.
    Six hours is short enough that this rarely bites, but a certificate does not know what commit it
    certified, so a shakeout standing in front of a spend should be dispatched AFTER the change it is meant
    to shake out, not merely recently.
    """
    if not isinstance(record, dict):
        return False
    stamp = record.get("updated_utc") or record.get("_s3_last_modified")
    if not stamp:
        return True
    try:
        t = time.strptime(str(stamp), "%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError):
        return True
    now = time.time() if now_utc is None else now_utc
    age_h = (now - calendar.timegm(t)) / 3600.0
    return age_h > (SHAKEOUT_EVIDENCE_MAX_AGE_H if max_age_h is None else max_age_h)


def done_units(mode, records=None, uids=None):
    """Unit ids whose stored result counts as DONE for `mode` — THE ONE ANSWER both the gate and `submit`
    use, so that "already done, no rental" cannot mean two different things in one dispatch.

    ★★ WHY THIS IS A FUNCTION AND NOT TWO SET COMPREHENSIONS (measured 2026-08-01). It WAS two. The
    shakeout expiry below was added to the gate's copy (`outstanding_units`) and not to `submit`'s, so the
    gate correctly decided the unit needed a host and `submit` then printed
    `[launch] skipping (already done, no rental)` and rented nothing — the shakeout rung stayed inert
    THROUGH ITS OWN FIX, and the run was green both times. Exactly the drift
    `test_the_gate_and_the_launcher_share_ONE_breaker_call_site` exists to stop for the failure breaker;
    the same discipline now applies to the fact next to it.

    ⏳ THE SHAKEOUT CLAUSE. Scoped to shakeout modes, so no real result can ever be expired by it — that
    would re-buy landed science. `uids` limits the expiry to the units this dispatch is actually about.
    """
    recs = leg_records() if records is None else records
    done = {u for u, d in (recs or {}).items() if (d or {}).get("status") == "done"}
    if not is_shakeout(mode):
        return done
    scope = set(uids) if uids is not None else set(done)
    for u in list(done):
        if u not in scope:
            continue
        r = recs.get(u) or {}
        # BOTH STAMPS, ALWAYS, IN BOTH BRANCHES. A shakeout that SKIPS is the dangerous outcome — it reads
        # as a shakeout that passed — and it used to print nothing at all, while the expiry printed only
        # the object mtime, i.e. only the field that was making the wrong call.
        st = f"content_updated_utc={r.get('updated_utc')} s3_object_mtime={r.get('_s3_last_modified')}"
        if shakeout_evidence_is_stale(r):
            done.discard(u)
            print(f"[launch] ⏳ {u}: this is a SHAKEOUT and its `done` record is older than "
                  f"{SHAKEOUT_EVIDENCE_MAX_AGE_H} h, so it is NOT evidence about today's pipeline ({st}). "
                  f"Treating the unit as needing a host — a stale certificate must not stand in for a "
                  f"shakeout that never ran.")
        else:
            print(f"[launch] ✅ {u}: SHAKEOUT certificate accepted as current "
                  f"(< {SHAKEOUT_EVIDENCE_MAX_AGE_H} h; {st}). Not renting. ⚠ Freshness is measured in "
                  f"TIME, not in CODE — this does not certify anything committed since that stamp.")
    return done


def outstanding_units(mode, legs=None, timestep_fs=None, warmup_timestep_fs=None, key=None):
    """Which of this mode's units still need a host — the ONE answer both the gate and `submit` use.

    Returns {"needed": [...], "done": [...], "live": [...], "live_hosts": {uid: record},
             "dead_hosts": {uid: record}}. `needed` is what a launch would actually rent, so
    `len(needed) == 0` means a launch is pointless and the gate in front of it must not fire one.

    ★ A UNIT WHOSE HOST HAS EXITED IS `needed`, AND ITS CORPSE IS RETURNED ALONGSIDE. Before 2026-07-27 a
    dead instance kept its unit out of `needed` forever (see `unit_hosts`), which is how three replicates sat
    unreplaced. `dead_hosts` carries the instance records that no longer occupy a slot so `submit` can destroy
    them at the moment it re-places the unit — the reap and the re-place have to be the same decision, or the
    lane is briefly paying for two instances on one unit.
    """
    specs = list(legs or units_for(mode))
    jobs = [build_jobspec(l, s, d, mode=mode, timestep_fs=timestep_fs,
                          warmup_timestep_fs=warmup_timestep_fs) for (l, s, d) in specs]
    uids = [j.env["UNIT_ID"] for j in jobs]
    _recs = leg_records()
    done = done_units(mode, records=_recs, uids=uids)
    live_hosts, dead_hosts, occupied = {}, {}, set()
    listing_error = None
    try:
        hosts = unit_hosts(uids, key=key)
        live_hosts, dead_hosts = hosts["live"], hosts["dead"]
        occupied = set(hosts.get("occupied_machines") or ())
    except Exception as e:  # noqa: BLE001 — reported, not swallowed; callers must FAIL CLOSED on it
        listing_error = f"{type(e).__name__}: {e}"
        print(f"[launch] could not list live instances ({listing_error}); "
              "cannot tell which units already hold a host")
    # ⛔ A UNIT THAT HAS DIED ON N HOSTS IN A ROW IS NOT `needed` — IT IS BROKEN.
    # Measured 2026-07-29: the ternary edge_reps replicates and all four triangle legs died at rc=1 in warmup
    # on host after host while the market gate cleared and re-rented each tick. `needed` is what the gate
    # prices and the launcher buys, so this is the one place that can stop the loop without touching the
    # on-host retry rule (which must stay permissive, or no fix could ever be validated).
    # Blocked units are RETURNED, not dropped — the readout has to show them (CLAUDE.md §6).
    _verdicts = breaker_verdicts([u for u in uids if u not in done and u not in live_hosts], leg_records())
    _blocked = {u: d for u, d in _verdicts.items() if d["block"]}
    # ↻ A LIFTED BLOCK IS A DECISION AND IS PRINTED AS ONE. Renting a unit that carries 51 strikes must not
    # look like a unit the breaker never considered — see `lfb.render`.
    _unblocked = {u: d for u, d in _verdicts.items() if not d["block"]}
    for _u, _d in sorted(_verdicts.items()):
        print(lfb.render(_u, _d))
    return {"needed": [u for u in uids if u not in done and u not in live_hosts and u not in _blocked],
            "blocked": _blocked,
            "unblocked": _unblocked,
            "done": [u for u in uids if u in done],
            "live": [u for u in uids if u in live_hosts and u not in done],
            "live_hosts": live_hosts,
            "dead_hosts": {u: i for u, i in dead_hosts.items() if u not in done and u not in live_hosts},
            # Passed through so the GATE prices a board the LAUNCHER would actually buy from. Pricing a
            # machine we are sitting on is how the 13:01:41Z snapshot came to quote $0.052 on machine 28164
            # and then have that exact rental refused.
            "occupied_machines": sorted(occupied),
            # ★★ THE FIELD EVERY CALLER MUST CHECK BEFORE RENTING. `needed` is only trustworthy when the
            # instance list was actually read: on a listing failure NOTHING looks live, so `needed` silently
            # becomes "every unit" — and renting on that is how this lane would genuinely double-buy on top
            # of four running hosts. Not hypothetical: the provider answered 403 on `/search/asks/` at
            # 11:10 AM ET today (`board-unreadable`), and the instance endpoint is the same API.
            "listing_ok": listing_error is None, "listing_error": listing_error}


RECEIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ternary-vast-rental-receipt.json")


def receipt_path():
    """Where the rental receipt goes. Overridable via `TVAST_RECEIPT_PATH`.

    ⚠ READ AT CALL TIME, NOT IMPORT TIME, and it exists because the first version of this file made the test
    suite write a real receipt into the working tree — a test that mutates the repo it is testing is how a
    fabricated artifact gets committed by accident. `conftest.py` redirects it per-session.
    """
    return os.environ.get("TVAST_RECEIPT_PATH") or RECEIPT_PATH


def write_rental_receipt(mode, requested, submitted, failed, live_rates=(), note=None, path=None,
                         withheld=(), skipped=(), unblocked=()):
    """What this launch ACTUALLY rented, and at what rate per host. Written on every path.

    ⛔ THE FILE THAT DECIDES THE LEDGER'S OUTCOME WORD. Before it existed, the workflow inferred the word
    from `steps.rent.outcome`, so "the rent step exited 0" produced `launched` — "hosts were actually
    rented" — for a tick that rented nothing at all. The rental is a fact the launcher knows and the shell
    does not; writing it down is what stops the shell guessing.

    ★★ AND IT IS THE ONE PLACE THAT DECIDES *WHY* NOTHING WAS RENTED (measured 2026-07-29). This branch used
    to be handed a hard-coded note, `"every unit for this mode is already done or running — no rental
    attempted"`, and it wrote that sentence whenever `keep` was empty — regardless of WHY it was empty.
    `keep` is emptied by two completely different things: units that really are done or running, and units
    the failure BREAKER withheld. On the 13:05:24Z tick the mode's two remaining units were one of each —
    r1 genuinely running, r2 withheld on 51 strikes — and the receipt asserted that both were "done or
    running". r2 was neither: its checkpoint sat at warmup/576 and nothing would ever re-place it. A receipt
    that names a unit's state wrongly is worse than one that says nothing, because it is quotable. So the
    wording is DERIVED here from `withheld` and `skipped` rather than asserted by the caller, and every
    withheld unit is NAMED with its reason (CLAUDE.md §6 — never silently drop a unit).
    """
    withheld, skipped = list(withheld), list(skipped)
    doc = {"_what": "what the last ternary launch actually rented, per host, at the rate the instance is "
                    "billed — NOT a board mean and NOT the launcher's `dph≈` line (both read low or price a "
                    "market rather than a purchase). This is the number that answers 'what are we paying?'",
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "mode": mode,
           "n_requested": len(requested), "n_rented": len(submitted),
           "requested": list(requested), "rented": list(submitted), "failed": list(failed),
           "already_live": list(live_rates)}
    if withheld:
        doc["n_withheld"] = len(withheld)
        doc["withheld"] = withheld
    if skipped:
        doc["skipped"] = skipped
    if unblocked:
        # ↻ WE RENTED A UNIT THAT WOULD OTHERWISE BE BLOCKED. That is a decision with money attached, so it
        # goes in the artifact with the evidence that authorised it — never only in a log line.
        doc["unblocked"] = list(unblocked)
    if not note:
        if withheld:
            # NOT "nothing to do". A withheld unit is a STALLED unit, and the difference has to survive into
            # the artifact — this is the same defect as a blocked lane reporting `nothing-to-launch`.
            note = ("⛔ %d unit(s) WITHHELD by the failure breaker and NOT rented — this lane is NOT "
                    "finished. %s%s Withheld: %s"
                    % (len(withheld),
                       ("%d unit(s) rented. " % len(submitted)) if submitted else "$0 spent this tick. ",
                       ("%d needed no rental (%s). "
                        % (len(skipped), ", ".join("%s: %s" % (k.get("unit_id"), k.get("why"))
                                                   for k in skipped))) if skipped else "",
                       "; ".join("%s (%s)" % (w.get("unit_id"), w.get("why") or w.get("verdict"))
                                 for w in withheld)))
        elif not requested and not submitted:
            note = ("every unit for this mode is already done or running — no rental attempted"
                    + (" (%s)" % ", ".join("%s: %s" % (s.get("unit_id"), s.get("why")) for s in skipped)
                       if skipped else ""))
    if note:
        doc["note"] = note
    try:
        with open(path or receipt_path(), "w") as fh:
            json.dump(doc, fh, indent=2, default=str)
            fh.write("\n")
    except OSError as e:
        print(f"[launch] rental receipt not written: {e}", flush=True)
    return doc


def submit(mode="probe", dry_run=False, timestep_fs=None, warmup_timestep_fs=None, legs=None,
           git_branch=None):
    """Rent one instance per unit for this mode, skipping units already done or already running.

    SKIPPING HAPPENS BEFORE THE RENTAL. The on-host pipeline has an idempotency check, but it only runs
    after the image pull and repo clone, so a re-dispatch was renting a GPU for ~25 minutes just to
    discover the work was finished. The launcher has S3 access; the cheap check belongs here.
    """
    specs = [(l, s, d) for (l, s, d) in (legs or units_for(mode))]
    # ★ `git_branch` IS EXPLICIT HERE BECAUSE THE WATCHDOG RELAUNCH HAD NO WAY TO PASS IT (found 2026-07-26).
    # The host pulls its code as `archive/refs/heads/$GIT_BRANCH.tar.gz`, and the watch list records a
    # `git_branch` per entry for exactly that reason — but `submit()` took no such argument, so a relaunch
    # fell through to `os.environ["GIT_BRANCH"]`, which the cron watchdog sets to `github.ref_name` = **main**.
    # A leg launched from a feature branch would therefore be resumed onto a host running MAIN's code: a
    # DIFFERENT engine against the same checkpoint. That is not hypothetical today — main still carries
    # `LomapAtomMapper(time=20)`, the timeout that silently produces a partial atom map, so a relaunch could
    # quietly finish a leg under a different alchemical transformation than the one it started.
    jobs = [build_jobspec(l, s, d, mode=mode, timestep_fs=timestep_fs,
                          warmup_timestep_fs=warmup_timestep_fs, git_branch=git_branch)
            for (l, s, d) in specs]
    if dry_run:
        print(json.dumps([{"name": j.name, "image": j.image, "max_runtime_s": j.max_runtime_s,
                           "env": j.env} for j in jobs], indent=2))
        submit.last_requested = 0
        return []

    done = done_units(mode, uids=[j.env["UNIT_ID"] for j in jobs])
    inflight = set()
    live_hosts, dead_hosts = {}, {}
    key = os.environ.get("VAST_API_KEY")
    if key:
        try:
            _hosts = unit_hosts([j.env["UNIT_ID"] for j in jobs], key=key)
            live_hosts, dead_hosts = _hosts["live"], _hosts["dead"]
            inflight = set(live_hosts)
        except Exception as e:  # noqa: BLE001
            # ⛔ FAIL CLOSED — DO NOT RENT WHEN WE CANNOT SEE WHAT WE ALREADY HOLD (2026-07-27).
            #
            # This used to print "duplicates are possible" and rent anyway. That is the ONE path by which
            # this lane could genuinely over-buy, and it is not hypothetical: an unreadable instance list
            # makes the skip set empty, so every unit looks unhosted and a four-unit mode re-rents all four
            # ON TOP of four already running. The provider answered 403 on the sibling `/search/asks/`
            # endpoint at 11:10 AM ET the same day, so "the API refuses us sometimes" is measured, not
            # imagined — and the tick that follows would have been the one paying for it.
            #
            # Refusing costs a delayed launch that the next tick recovers from checkpoints at no loss.
            # Proceeding costs a duplicate GPU-hour bill for work already in flight. §6's whole framing is
            # that waiting is cheap here and buying twice is not.
            msg = f"{type(e).__name__}: {e}"
            print(f"[launch] could not list live instances ({msg}) — REFUSING TO RENT. Every unit would "
                  f"look unhosted, so a launch now could double-buy on top of running legs. "
                  f"Nothing rented, nothing billing; the next tick re-checks.")
            print("::error title=TVAST LAUNCHER FAULT::could not read the live instance list "
                  f"({msg}), so the launcher cannot tell which units already hold a host. Refused to rent "
                  "rather than risk renting duplicates on top of running legs.")
            submit.last_requested = len(jobs)
            submit.last_failure_kind = "fault"
            submit.last_live_rates = []
            write_rental_receipt(mode, requested=[j.env["UNIT_ID"] for j in jobs], submitted=[],
                                 failed=[{"unit_id": j.env["UNIT_ID"], "error": msg,
                                          "kind": "fault"} for j in jobs],
                                 note="instance list unreadable — refused to rent (would risk duplicates)")
            return []
    busy = done | inflight
    # ⛔ THE BREAKER GATES THE PURCHASE, NOT JUST THE QUOTE (measured 2026-07-29, and it cost a rental).
    #
    # `outstanding_units` filters `needed`, and `gate_for_mode` prices that — so the GATE correctly reported
    # `n_units 1` with r2 blocked on 49 failed hosts. But this function never called it: `busy` is only
    # `done | inflight`, so the launch the gate self-dispatched rebuilt its own list and rented BOTH r1 and
    # r2. A guard that filters the quote and not the purchase is not a guard; the blocked unit was bought
    # 6 minutes after the readout said it would not be.
    #
    # Same fail-OPEN direction as the module's other breaker call (an unreadable attempt listing must not be
    # able to halt the lane) — deliberately opposite to the instance-list check above, which fails CLOSED
    # because guessing wrong THERE double-buys on top of running work, whereas guessing wrong here costs at
    # most one rental of a unit that may well now succeed.
    #
    # ⛔ AND IT ASKS THROUGH `breaker_verdicts`, THE SAME FUNCTION `outstanding_units` ASKS THROUGH. Two
    # loops calling `lfb.decide` with independently-gathered arguments is a difference the old source-text
    # test could not see; one function is the only form of "the same verdict" that cannot drift.
    _verdicts = breaker_verdicts([j.env["UNIT_ID"] for j in jobs if j.env["UNIT_ID"] not in busy],
                                 leg_records())
    _brk = {u: d for u, d in _verdicts.items() if d["block"]}
    for _u, _d in sorted(_verdicts.items()):
        print(lfb.render(_u, _d))
    keep = [j for j in jobs if j.env["UNIT_ID"] not in busy and j.env["UNIT_ID"] not in _brk]
    # WHAT THIS LAUNCH IS NOT RENTING, AND WHY — carried to the receipt rather than left in a log line the
    # tail-truncation eats. `withheld` and `skipped` are different facts and must never be merged: one is a
    # unit that is stalled, the other a unit that is fine.
    _withheld_rows = [{"unit_id": u, "reason": "failure-breaker", "n_attempts": d.get("n_attempts"),
                       "threshold": d.get("threshold"), "status": d.get("status"),
                       "verdict": d.get("verdict"), "why": d.get("why")}
                      for u, d in sorted(_brk.items())]
    _skipped_rows = ([{"unit_id": u, "why": "done"} for u in sorted(done & {j.env["UNIT_ID"] for j in jobs})]
                     + [{"unit_id": u, "why": "running"}
                        for u in sorted(inflight & {j.env["UNIT_ID"] for j in jobs})])
    _unblocked_rows = [{"unit_id": u, "n_attempts": d.get("n_attempts"),
                        "superseded_by": d.get("superseded_by"), "why": d.get("why")}
                       for u, d in sorted(_verdicts.items()) if not d["block"]]
    # ★ WHAT THE UNITS WE ARE *NOT* RENTING ALREADY COST US, priced off the LIVE INSTANCE RECORD. Without
    # this, a tick that rents nothing has nothing to say about money at all, and the only $/ns figure
    # anywhere near it is a board mean — the substitution that made 12:39 PM ET read as a 2.032x purchase.
    submit.last_live_rates = [rented_rate_row(u, live_hosts[u]) for u in sorted(live_hosts)]
    for j in jobs:
        if j.env["UNIT_ID"] in done:
            print(f"[launch] skipping (already done, no rental): {j.env['UNIT_ID']}")
        elif j.env["UNIT_ID"] in inflight:
            print(f"[launch] skipping (already running, no rental): {j.env['UNIT_ID']}")
    # HOW MANY UNITS THIS LAUNCH ACTUALLY WANTED, recorded so the caller can tell "nothing needed renting"
    # (green) from "wanted units, rented none" (red). Both return an empty handle list, and conflating them
    # is what let a launch that rented nothing report success. A function attribute rather than a signature
    # change so every existing caller and test keeps working.
    submit.last_requested = len(keep)
    submit.last_failure_kind = None
    # ⚰⚠ THE LAUNCHER NAMES THE CORPSE IT IS STEPPING OVER — AND DOES NOT DESTROY IT.
    #
    # ★★ THIS FUNCTION DESTROYED IT UNTIL 7:05 PM ET, AND THAT WAS WRONG. `exited` ON VAST IS ROUTINELY A
    # TRANSIENT STATUS, NOT A DEAD CONTAINER — measured on the step 1 fan-out the same evening (423fa606):
    # three instances read a terminal status, and twenty-one minutes later all three were `running` again at
    # ages 114/112/45 min, with the committed-iteration census proving they had never stopped WORKING across
    # the whole window (one advanced warmup@380 -> production@40, another added 80 production iterations).
    # Destroying on a single terminal observation would therefore have killed a leg that was mid-flight and
    # thrown away everything since its last checkpoint. That lane's reaper already refuses to act on one
    # observation and demands two consecutive terminal ticks; this one has no tick history at all, so it must
    # not act.
    #
    # THE ASYMMETRY IS WHY THE SLOT RULE ABOVE STILL STANDS. "Should this unit be re-submitted?" and "should
    # this instance be destroyed?" are different questions with opposite costs. Re-submitting a unit whose
    # host turns out to be alive costs one duplicate that `collect`'s dedupe kills on its next pass, on work
    # that is checkpointed in S3 and idempotent to resume — minutes of one GPU. Destroying a live advancing
    # leg costs the hours since its last commit and cannot be undone. So: free the SLOT on a terminal status,
    # never free the BOX on one.
    #
    # The reap stays where the evidence is: `collect` re-issues the start, reads the reply, and separates
    # "outbid, restartable" from "GPU gone, destroy it" — none of which is knowable here.
    for u in [u for u in dead_hosts if u in {j.env["UNIT_ID"] for j in keep}]:
        i = dead_hosts[u]
        print(f"[launch] re-placing {u}: its host {i.get('id')} (machine {i.get('machine_id')}, "
              f"{i.get('gpu_name')}) reads actual_status={i.get('actual_status')!r} / "
              f"cur_state={i.get('cur_state')!r}, so it does not hold the unit's slot. NOT destroying it — "
              f"a terminal status on Vast is often transient, and `collect` is the one that nudges, reads "
              f"the reply and reaps on real evidence.")
    if not keep:
        if _brk:
            print("[launch] NOTHING RENTED, and it is NOT because the mode is finished: %d unit(s) were "
                  "withheld by the failure breaker (%s). $0 spent this tick."
                  % (len(_brk), ", ".join(sorted(_brk))))
        else:
            print("[launch] every unit for this mode is already done or running — nothing to rent")
        # ★★ SAY SO IN A FILE, NOT ONLY IN A LOG LINE (2026-07-27). This branch is the one the 12:29 PM and
        # 12:39 PM ET ticks took, and because it left no artifact the ledger step downstream could only see
        # "the rent step exited 0" — which it filed as `launched`, meaning "hosts were actually rented".
        # Zero were. The receipt is what lets the outcome word be derived from the RENTAL rather than from
        # an exit code, and it is written on every path so its ABSENCE is itself diagnostic.
        # ⛔ NO `note=` HERE ANY MORE. The caller used to assert "every unit is already done or running" from
        # this branch unconditionally, which is false the moment the breaker withheld one. The wording is
        # DERIVED from `withheld`/`skipped` inside `write_rental_receipt` — its one home.
        write_rental_receipt(mode, requested=[], submitted=[], failed=[],
                             live_rates=getattr(submit, "last_live_rates", []),
                             withheld=_withheld_rows, skipped=_skipped_rows,
                             unblocked=_unblocked_rows)
        return []

    bad = set(blocked_machine_ids())
    if bad:
        print(f"[launch] excluding {len(bad)} machine(s) known to refuse starts: {sorted(bad)}")
    # ⛔ AND THE MACHINES WE ARE ALREADY SITTING ON. Separate from `bad` and printed separately, because they
    # are different facts with different lifetimes: `bad` is a refusal we recorded, this is where our own
    # instances are RIGHT NOW, recomputed every tick and never written down. Merging them into one line is
    # how a self-collision would come to read as a blacklist entry. Full argument: `unit_hosts`.
    occupied = set(_hosts.get("occupied_machines") or ()) if key else set()
    if occupied:
        print(f"[launch] excluding {len(occupied)} machine(s) this account already occupies "
              f"(a second unit on a machine we are already on is what got r2 capacity-refused on 28164 at "
              f"9:37 AM ET on 2026-07-29): {sorted(occupied)}")
    backend = get_backend("vast")
    handles = []
    # ONE UNIT PER MACHINE. Offers are per GPU slot, so selection happily picks the same cheapest-$/ns
    # machine for several units — but a host advertising slots it cannot actually schedule accepts every
    # rental and then refuses every start (observed 2026-07-25: machine 53989 took two legs and answered
    # resources_unavailable for both). Spreading costs ~nothing: the market shows ~23 hosts and the floor
    # is flat day-to-day.
    used = set(bad) | occupied
    failures = []

    def _record_start_refusals(unit_id, rows):
        """Put every host that refused THIS submit's start into the perishable 24 h window.

        ★★ WHY THIS EXISTS HERE AND NOT ONLY IN `collect` (2026-07-29). Until `gpu_backend.submit` learned to
        read the start reply, a capacity refusal was only ever discovered by the next `collect` tick — 15-35
        minutes and one wasted launch later — so `capacity_refusal_trend` could only ever see the subset of
        refusals that survived long enough to be nudged. Now the launcher sees them the moment they happen,
        and a trend that misses the ones we recovered from inside a single submit is a trend that
        systematically under-counts exactly when the fix is working.

        ⛔ READOUT ONLY. `capacity_refusal_trend` returns counts and never a verdict, and nothing here reads
        the result back — the machine is excluded for THIS submit only, by `gpu_backend`, and that exclusion
        dies with the call. A durable per-machine count is the blacklist trimcrae struck down ("a claim about
        a moment, not about the host"); see `capacity_refusal_trend.__doc__` and its tests.
        Best-effort throughout: instrumentation must never break a launch that otherwise succeeded."""
        if not rows:
            return
        try:
            import capacity_refusal_trend as _crt
            s3c, tr = _s3(), None
            for r in rows:
                tr = _crt.record(s3c, DEFAULT_BUCKET, r.get("machine_id"), unit_id, lane="ternary",
                                 why=r.get("why") or "resources_unavailable on start")
            if tr:
                print(_crt.render(tr))
        except Exception as _e:  # noqa: BLE001
            print(f"[launch] (capacity-refusal trend unavailable: {type(_e).__name__}: {_e})")

    for j in keep:
        try:
            j.resources.exclude_machine_ids = tuple(used)
            h = backend.submit(j)
            mid = h.extra.get("machine_id")
            if mid is not None:
                used.add(str(mid))
            # Hosts this submit tried and destroyed BEFORE landing. They are already $0, but they must not
            # be silently absorbed: a launch that quietly burned through three hosts to place one unit is
            # the market thinning, and §6 says a thinning market is a thing to SURFACE, not to swallow.
            _ref = h.extra.get("start_refusals") or []
            if _ref:
                used |= {str(r["machine_id"]) for r in _ref}
                print(f"[launch] {j.name}: {len(_ref)} host(s) refused the start before this one and were "
                      f"destroyed ($0 each): {', '.join(str(r['machine_id']) for r in _ref)}")
                _record_start_refusals(j.env["UNIT_ID"], _ref)
            print(f"[launch] {j.name}: instance={h.job_id} machine={mid} "
                  f"floor=${h.extra.get('min_bid')} bid=${h.extra.get('bid')} dph=${h.extra.get('dph')}")
            handles.append({"unit_id": j.env["UNIT_ID"], "instance": h.job_id,
                            "machine_id": mid, "bid": h.extra.get("bid"), "dph": h.extra.get("dph")})
        except Exception as e:  # noqa: BLE001 — one unrentable unit must not abort the rest
            # ★ CLASSIFY AT THE POINT OF FAILURE, where the exception type is still available. Upstream this
            # collapsed to one string and the caller had to guess between "the market had nothing under our
            # line" and "the provider 403'd us" — the ambiguity that made a correct refusal and a broken
            # launcher produce identical CI output on 2026-07-27.
            from gpu_backend import CapacityRefusedAtStart, NoQualifyingOffer
            market = isinstance(e, NoQualifyingOffer)
            # ★ AND NAME WHICH KIND OF "market" IT WAS. "NOTHING AFFORDABLE" and "every host we rented
            # refused to start" are both non-faults, but they have opposite remedies — wait for a cheaper
            # board vs. wait for CAPACITY — and printing them with one word is what made the 2026-07-29
            # morning read as a price problem while every board snapshot was 1.04x-1.34x basis.
            refused = isinstance(e, CapacityRefusedAtStart)
            print(f"[launch] {j.name}: "
                  f"{'HOSTS REFUSED TO START' if refused else 'NOTHING AFFORDABLE' if market else 'SUBMIT FAILED'} "
                  f"{type(e).__name__}: {e}")
            if refused:
                used |= {str(r["machine_id"]) for r in getattr(e, "refusals", [])}
                _record_start_refusals(j.env["UNIT_ID"], getattr(e, "refusals", []))
            failures.append({"unit_id": j.env["UNIT_ID"], "error": f"{type(e).__name__}: {e}"[:400],
                             "kind": "capacity" if refused else "market" if market else "fault"})
    # WHY THIS LAUNCH CAME UP SHORT, in one word, for the caller's exit code and the ledger. A single FAULT
    # dominates: if any unit died on a provider error we cannot claim the market refused us, because we never
    # got a clean answer from it. Only when every shortfall is "nothing affordable" is this the guard working.
    # ★ THREE KINDS NOW, IN PRECEDENCE ORDER. `capacity` sits between them because it is more specific than
    # `market` and less alarming than `fault`: the launcher worked, the provider answered cleanly, and the
    # board was cheap — there was simply no slot. Reporting it as `market` would print "HELD ON PRICE" over
    # a 1.04x board, which is the 2026-07-29 misdiagnosis; reporting it as `fault` would redden the lane for
    # the most routine failure Vast has (CLAUDE.md §6).
    if failures:
        submit.last_failure_kind = ("fault" if any(f["kind"] == "fault" for f in failures) else
                                    "capacity" if any(f["kind"] == "capacity" for f in failures) else
                                    "market")
    # ★★ READ BACK WHAT WE JUST BOUGHT, AT THE RATE THE INSTANCE IS BILLED. The `dph` in `h.extra` above is
    # the OFFER's figure — market floor plus the disk line the SEARCH priced — and CLAUDE.md §1 is explicit
    # that it reads LOW against the real charge. One GET turns a quote into the actual rate, and the ledger
    # then records a number nobody has to caveat.
    if handles:
        try:
            back = live_unit_hosts([h["unit_id"] for h in handles], key=key)
            for h in handles:
                inst = back.get(h["unit_id"])
                if inst is not None:
                    h.update({k: v for k, v in rented_rate_row(h["unit_id"], inst).items()
                              if k in ("usd_per_ns", "x_basis", "over_buy_line", "gpu",
                                       "dph_total_usd_h", "dph_base_usd_h")})
        except Exception as e:  # noqa: BLE001 — a missing rate must never fail a launch that succeeded
            print(f"[launch] could not read back the rented rates ({type(e).__name__}: {e}); "
                  "the receipt will carry the offer quote only")
    write_rental_receipt(mode, requested=[j.env["UNIT_ID"] for j in keep], submitted=handles,
                         failed=failures, live_rates=getattr(submit, "last_live_rates", []),
                         withheld=_withheld_rows, skipped=_skipped_rows, unblocked=_unblocked_rows)
    if handles:
        json.dump(handles, open("ternary-vast-handles.json", "w"), indent=2)
    print(f"[launch] {len(handles)}/{len(keep)} unit(s) submitted -> "
          f"s3://{DEFAULT_BUCKET}/{RESULT_PREFIX}/legs/")
    # PERSIST THE RENT OUTCOME WHERE A MONITOR CAN READ IT. A per-unit failure is currently only a printed
    # line inside a green job, and GitHub's job-log API truncates from the tail — so on 2026-07-25 an `edge`
    # launch that rented nothing reported success and its `[launch]` lines could not be retrieved at all,
    # leaving "did it rent?" answerable only by the absence of instances. Writing the outcome to S3 makes it
    # part of the lane's durable state, which is where every other monitoring signal in this lane already
    # lives. Best-effort: failing to record a diagnostic must never fail a launch.
    try:
        s3 = _s3()
        key = f"{(RESULT_PREFIX).rstrip('/')}/_last_launch.json"
        s3.put_object(Bucket=DEFAULT_BUCKET, Key=key, Body=json.dumps({
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "mode": mode, "requested": [j.env["UNIT_ID"] for j in keep],
            "submitted": handles, "failed": failures,
            "withheld": _withheld_rows, "unblocked": _unblocked_rows,
            "excluded_machines": sorted(bad), "occupied_machines": sorted(occupied),
        }, indent=2).encode())
    except Exception as e:  # noqa: BLE001
        print(f"[launch] could not persist the launch record: {type(e).__name__}: {e}")
    return handles


# =============================================================================================================
# market gate ($/ns) — CLAUDE.md §6, applied to THIS rung's own band
# =============================================================================================================
# ⛔ *"A THIN, EXPENSIVE MARKET IS A REASON TO PAUSE, NOT TO PAY"* (trimcrae, 2026-07-26: "I'd rather pause
# until availability opens than pay double per ns"). LANE 21 implemented this for the STEP 1 fan-out. This is
# the SAME rule on the ternary lane, and the two things that must not be duplicated are imported, not copied:
#
#   * `gpu_backend.rank_offers_by_usd_per_ns` — the qualify+score filter, which is literally the one the
#     renting path uses, so the guard cannot price a fleet the launcher would not actually buy; and
#   * `congeneric_fanout.basis_usd_per_ns` — the ladder basis, which is a property of the MARKET, not of a
#     rung, and is deliberately the ladder's rather than a recent night's (anchoring to observations is
#     self-ratcheting: a bad night raises the ceiling until the guard permits the market it exists to refuse).
#
# WHAT IS *NOT* SHARED, AND WHY THAT MATTERS HERE. LANE 21's `market_snapshot` prices against the fan-out's
# ResourceSpec and its `market_ceiling_usd` against the fan-out's per-unit GPU-hours and its $15-80 band. Both
# are wrong for this lane: a ternary leg needs 32 GB RAM / 8 vCPU / 24 GB VRAM (setup is CPU+RAM bound and a
# 16 GB box measured 4x slower), and its band is valB's, not STEP 1's. Reusing those numbers would price two
# replicates against a nineteen-edge authorisation — a guard that refuses a small authorised spend for a
# reason that does not apply to it. So the SPEC and the BAND are this lane's, and both are DERIVED from the
# ladder artifact rather than typed.
def triangle_ns_per_unit():
    """Reference-GPU nanoseconds in ONE closure-triangle leg. DERIVED, never typed.

    `valb_triangle_closure.ternary_leg_ref_gpu_h()` is the triangle's one home for leg size: 3.5e6 steps
    (800 warmup iterations at 1 fs + 2000 production at 2 fs, 1250 force evaluations each) at the measured
    ~16 s/iteration on a Vast 4090. Priced in STEPS because iteration counts are not comparable across
    protocols — that is the correction which turned the design's 2400-iteration basis into 2800."""
    import vast_cost_model as _vcm
    import valb_triangle_closure as _tri
    return _tri.ternary_leg_ref_gpu_h() * _vcm.REFERENCE_NS_PER_H


def triangle_band_usd(n_units):
    """(plan, ceiling) dollars for `n_units` closure-triangle legs.

    ★ THE ONE HOME IS `price_triangle()`, NOT THE LADDER. Every other mode on this lane prices itself off
    `vast-ladder-repricing.json`, which is right for a ladder rung. The triangle is not one: it REPLACED the
    valB_mini rescope, and its price already has a single derived home in
    `valb_triangle_closure.price_triangle()` — the function carrying the three corrections to the design's
    ~$5.9 (the 2800-iteration basis, the solvent legs that cancel, and T1's non-existent replicates). Adding
    a ladder row would give the same fact a second home free to disagree with the first, which is exactly
    CLAUDE.md rule 1's failure mode, and it would move the ladder TOTAL — a pinned figure — for a rung that
    is not on the ladder.

    The CEILING is the top of the triangle's own published range, i.e. exactly the authorisation the pre-gate
    costed and nothing of this guard's own invention. PER LEG, so it scales to a partial fan-out: CLAUDE.md
    §6 permits buying the units the board can supply under the line and leaving the rest to the next tick,
    and an all-or-nothing ceiling would forbid that.
    """
    import valb_triangle_closure as _tri
    v = _tri.price_triangle()["variants"]
    scout = next(v[k] for k in v if k.startswith("n1_scout_R_only"))
    n_legs_in_scout = 4.0                       # `price_triangle` prices this variant as 4 * ternary_leg
    per_leg_plan = scout["plan_usd"] / n_legs_in_scout
    per_leg_hi = scout["range_usd"][1] / n_legs_in_scout
    return round(per_leg_plan * n_units, 2), round(per_leg_hi * n_units, 2)


def rung_ns_per_unit(entry="ternary_4fs_recalibration (1 matched edge)", legs_in_entry=3):
    """Reference-GPU nanoseconds in one leg of this rung. DERIVED from the ladder, never typed."""
    import vast_cost_model as _vcm
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "vast-ladder-repricing.json")) as fh:
        e = json.load(fh)["ladder"][entry]
    lo, hi = e["ref_gpu_h"]
    return (lo + hi) / 2.0 / float(legs_in_entry) * _vcm.REFERENCE_NS_PER_H


def rung_band_usd(n_units, entry="ternary_4fs_recalibration (1 matched edge)", legs_in_entry=3):
    """(plan, ceiling) dollars for `n_units` legs of this rung. The ceiling is the TOP OF THE RUNG'S OWN
    BAND — the same number the ladder publishes — so the guard enforces exactly the authorisation and
    nothing of its own invention, and it re-derives itself whenever the ladder is repriced."""
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "vast-ladder-repricing.json")) as fh:
        e = json.load(fh)["ladder"][entry]
    per_leg_plan = e["plan_usd"] / float(legs_in_entry)
    per_leg_hi = e["range_usd"][1] / float(legs_in_entry)
    return round(per_leg_plan * n_units, 2), round(per_leg_hi * n_units, 2)


# ★ TWO CEILINGS, AND THE RATIO ONE BINDS FIRST (2026-07-27).
# The dollar ceiling is the rung's own authorisation — "do not spend past what was approved". The RATIO
# ceiling is trimcrae's stated preference, in his words: *"I'd rather pause until availability opens than pay
# double per ns."* Those are different tests, and on the night this was written the difference decided the
# launch: 4 legs at 2.05x basis projected $17.99 against a $22.28 authorisation, i.e. it CLEARED the dollars
# and was still double per ns.
#
# 1.5 is the repo's own number, not one invented for this gate — CLAUDE.md §1 already calls ">=1.5x basis"
# drift and requires every in-flight row to say so. A guard that buys at a multiple the reporting rules
# classify as drift would be contradicting the same document twice on one line.
#
# It is also demonstrably reachable rather than aspirational: the board ran ~1.0x earlier the same evening
# (a 3090 at $0.0643/hr) and improved 3.16x -> 2.05x in three hours unaided. Waiting is cheap HERE
# specifically — the calibrator gates spend on valB_full, and r0's reverse leg does not land until Monday
# midday, so nothing downstream can move in the meantime.
# IMPORTED, NOT TYPED (rule 1, tightened 2026-07-27 when the relaunch gate became the third caller of the
# same number). `inflight_usd_per_ns.DRIFT_MULTIPLE` is the drift line's one home; a literal here would be a
# second copy free to disagree with the board that reports against it.
from inflight_usd_per_ns import DRIFT_MULTIPLE as _DRIFT_MULTIPLE  # noqa: E402
# The buy line, DERIVED not typed (CLAUDE.md §1: never a multiple of a correctable basis). It gates the
# teardown decision for the same reason it gates a rental — see teardown_decision.py.
from inflight_usd_per_ns import APPROVED_USD_PER_NS as _BUY_LINE_USD_PER_NS  # noqa: E402
import teardown_decision as tdd  # noqa: E402

MARKET_MAX_RATIO_VS_BASIS = float(os.environ.get("TVAST_MAX_RATIO_VS_BASIS") or _DRIFT_MULTIPLE)


def buy_ceiling_usd_per_ns():
    """The highest $/ns this lane may PAY for one host, in dollars. DERIVED: the 1.5x drift line times the
    ladder basis, both of which have exactly one home elsewhere.

    ★★ WHY A PER-OFFER LINE AND NOT THE GATE'S MEAN (2026-07-27, after the 9:12 AM window was lost).
    The gate's test is the MEAN of the n cheapest offers, which is the right question for "is a fan-out of n
    worth buying" and the WRONG one for "may we rent THIS box": a mean under the line can contain a host
    over it, pulled down by cheaper siblings. That is trimcrae's own complaint — *"Why are there so many
    high $/ns rows that are flagged but you're still paying for them?"* — and no amount of board-level
    gating fixes it, because the board is not what gets rented.

    Handing this to `submit`'s ResourceSpec makes overpaying STRUCTURALLY impossible instead of
    procedurally discouraged: `rank_offers_by_usd_per_ns` drops every offer above the cap before selection
    sees it, on every fallback after a capacity refusal too. `congeneric_fanout_vast.build_jobspec` has done
    this since 2026-07-27; this lane simply never adopted it, and the whole-board veto it used instead is
    what refused two authorised launches today."""
    from congeneric_fanout import basis_usd_per_ns
    return MARKET_MAX_RATIO_VS_BASIS * basis_usd_per_ns()


def _gate_what(mode=None):
    """The readout's own description of WHICH purchase it priced.

    ⚠ NOT COSMETIC. This string used to say "for the valB_mini replicates" unconditionally, and the hold
    snapshot is the artifact a hold gets read from hours later by someone who was not here. A snapshot naming
    the wrong experiment is worse than one with no label: it makes a triangle hold look like a replicate hold
    that had already been decided. CLAUDE.md §6 requires a hold to be VISIBLE, and visible means legible.
    """
    what = {"triangle": "the valB closure TRIANGLE (T2+T3, 4 new legs; r0 reused as T1)",
            "triangle_smoke": "the valB closure triangle's plumbing shakeout",
            "edge_reps": "the valB_mini replicates", "edge": "the RUNG 2b matched re-calibration edge",
            "probe": "the RUNG 2b stage-1 4 fs survival probe", "smoke": "the lane's plumbing shakeout",
            "5aks": "RUNG 5a-KS's two ternary legs", "5aks_smoke": "RUNG 5a-KS's plumbing shakeout",
            }.get(mode, "the valB_mini replicates" if mode is None else "mode=%s" % mode)
    return "ternary lane $/ns market gate (CLAUDE.md §6) for %s" % what


# =============================================================================================================
# ★★ TIER PREFERENCE — TAKE THE UNINTERRUPTIBLE HOST WHENEVER IT CLEARS BOTH CEILINGS (trimcrae, 2026-07-31)
# =============================================================================================================
# HIS WORDS: *"Maybe add a new rule where if anything on-demand comes in under the buy line, we just take it
# to avoid the outage."*
#
# THE OUTAGE HE MEANS, measured. 24 rentals across 4 legs in 6.73 h that day (7:12 AM - 1:56 PM ET,
# reconstructed from the git history of `ternary-vast-rental-receipt.json`): median session 60 min, mean 76,
# min 12, max 270; 25 % under 30 min, 50 % under 60 min — and those are UPPER bounds, because the
# reconstruction measures rental-to-rental and so includes the hostless gap. Against the step 1 fan-out's
# 208-rental baseline (median 1.62 h, 9 % under 0.5 h) this lane churns about twice as fast. A ternary leg
# needs ~28 min to stage and reach its first commit boundary, so **a quarter of the day's rentals died before
# buying a single checkpoint**: they billed and produced nothing.
#
# WHY A BID CANNOT FIX IT AND ONLY THIS TIER CAN. Vast's documented rule is that an on-demand renter preempts
# an interruptible one REGARDLESS of bid. `VAST_BID_FLOOR_MULT` therefore buys priority WITHIN the cheap tier
# and cannot stop the eviction it is aimed at. The uninterruptible tier is the only thing that can.
#
# WHY IT IS AFFORDABLE NOW AND WAS NOT THIS MORNING. `vast-filter-ablation.json` (1:36 PM ET) priced both
# boards in the same minute: bid best 0.883x basis, on-demand best 1.778x — BOTH under the 1.9166x line.
# Earlier the same day on-demand priced 2.13-2.25x and was correctly refused. So the rule is a PREFERENCE
# among offers that already clear, evaluated fresh every tick, not a standing decision to pay more.
#
# ⛔ WHAT IT DOES NOT DO, and the review will look for exactly this: it does not move, soften or bypass either
# ceiling. `choose_tier` can only ever select a block whose `clears` is True, and `clears` is computed by
# `_price_tier` from the SAME dollar band and the SAME `$/ns` buy line as before. An on-demand board over the
# line is refused as it always was; a tranche over the rung's band is refused as it always was. Exhaustively
# pinned by `tests/test_tier_preference.py`.
TIER_BID, TIER_ONDEMAND = "bid", "on-demand"

# Off switch, because a behaviour change this consequential must not require editing the gate to undo.
PREFER_UNINTERRUPTIBLE = str(os.environ.get("TVAST_PREFER_ONDEMAND") or "1").strip().lower() \
    not in ("0", "false", "no", "off")


def _tier_failure(blk):
    """Which ceiling this tier hit, in words. PURE. A refusal that does not NAME its ceiling is the
    unreadable-hold failure CLAUDE.md §1 already made this repo fix once — and the two ceilings mean
    different things ('was this authorised' vs 'is this a rate we will pay at all'), so they never merge."""
    if blk.get("board_error"):
        return "board unreadable (%s)" % blk["board_error"]
    why = []
    if blk.get("fails_dollar_ceiling"):
        why.append("over the rung's dollar ceiling (projected $%s)" % blk.get("projected_usd"))
    if blk.get("fails_ratio_ceiling"):
        # "drift line" is the repo-wide name for this ceiling (CLAUDE.md §1) and the word every other
        # readout uses. A refusal that invents a synonym is a refusal a reader has to translate.
        why.append("over the $/ns drift line (the buy line) at %sx basis" % blk.get("ratio_vs_basis"))
    return "; ".join(why) or "no priceable offer"


def choose_tier(bid, ondemand, prefer_uninterruptible=None):
    """(tier, hold, why) given both tiers' priced blocks. PURE — no network, no env beyond the default.

    THE WHOLE RULE, in four lines of logic and one paragraph of reason. `clears` is the conjunction of both
    ceilings, computed once in `_price_tier`, so this function cannot accidentally admit a block that failed
    one of them — the property `tests/test_tier_preference.py` checks exhaustively."""
    prefer = PREFER_UNINTERRUPTIBLE if prefer_uninterruptible is None else bool(prefer_uninterruptible)
    if prefer and (ondemand or {}).get("clears"):
        return TIER_ONDEMAND, False, (
            "on-demand clears BOTH ceilings at %sx basis, so we take it: an uninterruptible host cannot be "
            "preempted, and preemption — not price — is what has been costing this lane (25%% of the day's "
            "rentals died before their first checkpoint). bid tier was %sx."
            % ((ondemand or {}).get("ratio_vs_basis"), (bid or {}).get("ratio_vs_basis")))
    if (bid or {}).get("clears"):
        return TIER_BID, False, (
            "bid tier clears at %sx basis; on-demand was NOT taken because it is %s"
            % ((bid or {}).get("ratio_vs_basis"),
               ("disabled by TVAST_PREFER_ONDEMAND=0" if not prefer else _tier_failure(ondemand or {}))))
    return None, True, (
        "HOLD — neither tier clears. bid: %s. on-demand: %s."
        % (_tier_failure(bid or {}), _tier_failure(ondemand or {})))


def market_gate(n_units, key=None, excluded=(), entry=None, legs_in_entry=3, max_ratio=None, mode=None):
    """(hold, readout) for renting `n_units` legs of this rung right now. Reads the LIVE board.

    HOLDS unless BOTH tests pass: projected dollars within the rung's own band top, AND the achievable $/ns
    within `MARKET_MAX_RATIO_VS_BASIS` of the ladder basis. An UNREADABLE or UNPRICEABLE board is a HOLD, not
    a launch: the one case where guessing is worst is the case where nobody is awake to check."""
    from congeneric_fanout import basis_usd_per_ns
    from gpu_backend import _vast_offer_query, rank_offers_by_usd_per_ns
    # WHICH AUTHORISATION THIS PURCHASE IS BEING JUDGED AGAINST. The dollar ceiling is meaningless unless it
    # is the band of the thing actually being bought: pricing four closure-triangle legs against the 4 fs
    # recalibration edge's band would judge one experiment's spend by another's approval. The triangle's band
    # is `price_triangle()`'s (see `triangle_band_usd`); everything else keeps the ladder.
    if mode in TRIANGLE_MODES:
        ns_unit = triangle_ns_per_unit()
        plan_usd, ceiling = triangle_band_usd(n_units)
        ceiling_basis = ("top of the valB closure triangle's OWN costed range "
                         "(valb_triangle_closure.price_triangle), scaled to %d legs" % n_units)
    else:
        kw = {} if entry is None else {"entry": entry}
        ns_unit = rung_ns_per_unit(legs_in_entry=legs_in_entry, **kw)
        plan_usd, ceiling = rung_band_usd(n_units, legs_in_entry=legs_in_entry, **kw)
        ceiling_basis = "top of this rung's OWN ladder band, scaled to %d legs" % n_units
    basis = basis_usd_per_ns()
    res = resource_spec()
    if excluded:
        res.exclude_machine_ids = tuple(str(m) for m in excluded)
    # ★★ THE TIER IS PART OF THE READOUT, BECAUSE A HOLD THAT DOES NOT NAME IT IS UNREADABLE
    #    (measured 2026-07-31 — the misreading this closes).
    # `collect`'s self-heal escalates a unit that has burned `_ESCALATE_AFTER` hosts to `on_demand=1`, so on a
    # churning lane MOST gate ticks price the UNINTERRUPTIBLE tier — which is small and dear by construction.
    # The committed 5a-KS snapshots that day therefore interleave two series: bid-tier ticks clearing at
    # 1.13-1.54x, and on-demand ticks holding at 2.04-2.28x, both writing the same file and both printing the
    # same "RUNG 5a-KS is HELD on price". Read from a distance that says the MARKET is at 2x basis. It was
    # not: the market was fine and the expensive tier was being priced.
    # Same principle as CLAUDE.md §1's "a row we are paying and a row the gate refused must never render
    # alike", one level up: two holds about DIFFERENT MARKETS must not render alike either.
    cap = MARKET_MAX_RATIO_VS_BASIS if max_ratio is None else float(max_ratio)
    out = {"_what": _gate_what(mode),
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "n_units": n_units,
           "basis_usd_per_ns": round(basis, 6), "plan_usd": plan_usd, "ceiling_usd": ceiling,
           "ceiling_basis": ceiling_basis, "max_ratio_vs_basis": cap,
           "usd_per_ns_at_max_ratio": round(cap * basis, 6),
           "breakeven_usd_per_ns": round(ceiling / (ns_unit * n_units), 6)}

    def _price_tier(interruptible):
        """One tier's board, priced against BOTH ceilings. `clears` is their conjunction and is the ONLY
        thing `choose_tier` may select on, so a preference can never admit a block that failed a ceiling."""
        import dataclasses as _dc
        r = _dc.replace(res, interruptible=interruptible)
        blk = {"tier": TIER_BID if interruptible else TIER_ONDEMAND, "interruptible": bool(interruptible)}
        try:
            offers = _vast_request("GET", "/search/asks/", key or os.environ["VAST_API_KEY"],
                                   params={"q": json.dumps(_vast_offer_query(r))}).get("offers", [])
            measured, capable = rank_offers_by_usd_per_ns(offers, r)
        except Exception as e:  # noqa: BLE001 — an unreadable board is NOT a cheap one, but nor is it a
            # reason to refuse the OTHER tier: `choose_tier` treats it as "not an option", never as a veto.
            blk.update({"clears": False, "board_error": "%s: %s" % (type(e).__name__, e)})
            return blk
        take = measured[:max(1, int(n_units))]
        # The MEAN over the n cheapest, not the single best: a fleet of n buys the n best offers, and pricing
        # it off the one cheapest host would flatter a thin board exactly when thinness is what we detect.
        best = (sum(u for u, _p, _o in take) / len(take)) if take else None
        blk["depth"] = {"offers_returned": len(offers), "qualifying": len(capable),
                        "priceable": len(measured), "needed": n_units, "used_for_mean": len(take)}
        blk["offers"] = [{"gpu": o.get("gpu_name"), "machine_id": o.get("machine_id"),
                          "min_bid_usd_h": p, "usd_per_ns": round(u, 6)} for u, p, o in take]
        if best is None:
            blk.update({"clears": False, "board_error": None,
                        "reason": "board offered nothing priceable (no benched card, or no offer)"})
            return blk
        projected = round(best * ns_unit * n_units, 2)
        ratio = best / basis
        blk.update({"mean_usd_per_ns": round(best, 6), "ratio_vs_basis": round(ratio, 3),
                    "projected_usd": projected,
                    "fails_dollar_ceiling": projected > ceiling, "fails_ratio_ceiling": ratio > cap})
        blk["clears"] = not (blk["fails_dollar_ceiling"] or blk["fails_ratio_ceiling"])
        return blk

    # ⚠ AN EXPLICIT `TVAST_ON_DEMAND=1` IS STILL AN OPERATOR OVERRIDE AND STILL WINS. It now means "price
    # ONLY the uninterruptible tier", which is what it always meant; the new rule is what happens when nobody
    # has forced a tier. Keeping the override is what lets a human pin a tier for a one-off without editing
    # policy, and it is why the forced case must not silently acquire a bid-tier fallback.
    forced_od = not res.interruptible
    bid_blk = None if forced_od else _price_tier(True)
    od_blk = _price_tier(False)
    tier, hold, why = choose_tier(bid_blk or {"clears": False, "board_error": "not priced (TVAST_ON_DEMAND=1)"},
                                  od_blk, prefer_uninterruptible=True if forced_od else None)

    # BOTH boards go in the snapshot, not just the winner's. A reader who cannot see the tier we did NOT buy
    # cannot grade why we paid the dearer one — and that is precisely the question a rising ladder spend
    # raises. Same discipline as the $/ns column: the number that explains a decision travels with it.
    out["tiers"] = {TIER_BID: bid_blk, TIER_ONDEMAND: od_blk}
    out["chosen_tier"] = tier
    out["prefer_uninterruptible"] = PREFER_UNINTERRUPTIBLE
    out["hold"] = hold
    out["reason"] = why

    # LEGACY TOP-LEVEL FIELDS, mirrored from the CHOSEN tier (or from the cheaper-clearing view on a hold) so
    # every existing reader — the launcher's readout, `relaunch_market_gate`, the board, the tests — keeps
    # working unchanged. They are a PROJECTION of `tiers`, never a second home: nothing writes them
    # independently, and `tier`/`interruptible` say which block they came from.
    src = (out["tiers"].get(tier) if tier else None) or od_blk or bid_blk or {}
    out["tier"] = ("bid (interruptible)" if src.get("interruptible") else
                   "on-demand (UNINTERRUPTIBLE — cannot be preempted; taken only when it clears BOTH "
                   "ceilings, per trimcrae 2026-07-31)")
    out["interruptible"] = bool(src.get("interruptible"))
    for k in ("depth", "offers", "mean_usd_per_ns", "ratio_vs_basis", "projected_usd",
              "fails_dollar_ceiling", "fails_ratio_ceiling"):
        if k in src:
            out[k] = src[k]
    return hold, out


def _withheld_rows_for_gate(out):
    """The gate readout's rows for units the breaker withheld. PURE (given `outstanding_units`'s answer).

    ★★ EMITTED ON EVERY BRANCH, NOT JUST `n == 0` (measured 2026-07-29, the THIRD readout gap of the same
    shape). `units_blocked` used to be built inside the `n == 0` branch alone, so a breaker withholding one
    unit while ANOTHER still needed a host produced a readout in which the withheld unit did not appear at
    all — not in `units_done`, not in `units_live`, not in `units_needing_host`, not in `units_blocked`. It
    simply vanished. The committed snapshots show it twice: at 11:46:13Z and again at 13:01:41Z, both
    `n_units 1` CLEAR ticks, `calib_hi_to_lo__ternary_vhl_r2_...` is absent from every list in the file
    while r1 is named in `units_needing_host`. A reader could only conclude the mode had three units.

    That is CLAUDE.md §6's prohibition — a withheld unit must be VISIBLE with its reason — and it was
    invisible by construction on the branch the lane spends most of its time in.
    """
    return [{"unit_id": u, "n_attempts": d.get("n_attempts"), "threshold": d.get("threshold"),
             "status": d.get("status"), "why": d.get("why")}
            for u, d in sorted((out.get("blocked") or {}).items())]


def _unblocked_rows_for_gate(out):
    """Units carrying a would-be block that durable evidence has SUPERSEDED — see `leg_failure_breaker`."""
    return [{"unit_id": u, "n_attempts": d.get("n_attempts"),
             "superseded_by": d.get("superseded_by"), "why": d.get("why")}
            for u, d in sorted((out.get("unblocked") or {}).items())]


def gate_for_mode(mode, key=None, excluded=(), max_ratio=None, legs=None):
    """(action, readout) — price ONLY the units of `mode` that still need a host.

    ★★ THE FIX FOR A GATE THAT RE-BOUGHT A SATISFIED LANE EVERY TICK (2026-07-27).

    The workflow used to call `market_gate(4)` with a literal 4. That number was the SIZE OF THE MODE, not
    the size of the purchase, so it stayed 4 after all four units were rented — and the gate went on pricing
    a four-unit fleet, clearing, and dispatching a launch that could only print "nothing to rent". Between
    12:08 and 12:39 PM ET it did that three times, and the third one recorded a 2.032x board reading beside
    the word `launched`, which is how a lane comes to look like it bought over trimcrae's buy line when it
    bought nothing at all.

    `action` is one of:
      * `"nothing-to-launch"` — every unit is done or already hosted. NOT a hold (the market was never the
        obstacle, and filing it as one would corrupt the hold clock and the hold readout), and NOT a clear:
        the caller must not dispatch a launch. This is the state the lane is in whenever it is working.
      * `"hold"`  — units need renting and the board is too expensive or unreadable.
      * `"blocked"` — units need renting but are withheld by the failure breaker (they have died on several
        hosts in a row). NOT `nothing-to-launch`: the lane is STALLED, not finished, and saying otherwise is
        the §6 prohibition. NOT `hold` either: the board was never consulted, so it must not run the hold
        clock or fire the hold warning, which exist for an expensive market rather than a broken unit.
      * `"clear"` — units need renting and the board is within both ceilings.

    A launch is dispatched on `"clear"` and on nothing else.
    """
    out = outstanding_units(mode, legs=legs, key=key)
    # ⛔ FAIL CLOSED WHEN WE CANNOT SEE WHAT WE ALREADY HOLD. An unreadable instance list makes every unit
    # look unhosted, so clearing the gate on it would dispatch a launch that re-rents units already running.
    # Filed as a HOLD (do not dispatch) rather than "nothing to launch", because something almost certainly
    # DOES need attention — we just cannot say what. Same discipline as the market gate's own
    # "an unreadable market is not a cheap one": the one case where guessing is worst is the case where
    # nobody is awake to check.
    if not out["listing_ok"]:
        readout = {
            "_what": _gate_what(mode),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "mode": mode, "hold": True, "nothing_to_launch": False,
            "reason": ("could not list live instances (%s) — so we cannot tell which units already hold a "
                       "host, and every unit would look unhosted. Refusing to dispatch: renting on this "
                       "would double-buy on top of running legs. The next tick re-checks."
                       % out["listing_error"]),
        }
        # Withheld units are named even here: the reason this tick is holding is the unreadable listing, but
        # a unit the breaker is withholding is a SECOND, independent fact and must not be lost behind it.
        if out.get("blocked"):
            readout["units_blocked"] = _withheld_rows_for_gate(out)
        return "hold", readout
    n = len(out["needed"])
    if n == 0:
        # ★★ A LANE THAT FINISHED AND A LANE THAT IS BLOCKED MUST NOT RENDER ALIKE (measured 2026-07-29,
        # the failure-breaker's first live tick). The breaker removes a repeatedly-failing unit from
        # `needed`, which drops `n` to 0 and lands here — and this branch said "every unit already done or
        # hosted" over a mode where 2 of 4 units were blocked on repeated failure. `2 done, 0 running` did
        # not even sum to 4, and the outcome word was `nothing-to-launch`, i.e. the lane read as FINISHED.
        # That is precisely CLAUDE.md §6's named failure mode — a hold indistinguishable from a completion —
        # and the fix belongs here rather than in the breaker, because ANY future reason for withholding a
        # unit will arrive through this same branch.
        blocked = out.get("blocked") or {}
        readout = {
            "_what": _gate_what(mode),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "mode": mode, "n_units": 0, "nothing_to_launch": not blocked, "hold": False,
            "units_done": out["done"], "units_live": out["live"],
            # The rate we are ALREADY PAYING on the hosts this lane holds — the only $/ns figure that means
            # anything on a tick that is not buying. A board mean here would be pricing a market we have no
            # intention of entering, which is precisely the number that got misread as a purchase.
            "live_host_rates": [rented_rate_row(u, out["live_hosts"][u]) for u in out["live"]],
        }
        if out.get("unblocked"):
            readout["units_unblocked"] = _unblocked_rows_for_gate(out)
        if blocked:
            # NOT a price hold — the market was never consulted — so it must not borrow the price-hold
            # vocabulary either. Its own outcome word, and every blocked unit named with its evidence.
            readout["units_blocked"] = _withheld_rows_for_gate(out)
            readout["reason"] = (
                "⛔ %d of mode %s's units are BLOCKED on repeated failure and were NOT rented — %d done, "
                "%d running, %d blocked. $0 spent this tick. This lane is NOT finished and NOT price-held: "
                "it is stalled on a code/data fault that another host cannot fix. Units: %s"
                % (len(blocked), mode, len(out["done"]), len(out["live"]), len(blocked),
                   ", ".join("%s (%s failed hosts)" % (u, (blocked[u] or {}).get("n_attempts"))
                             for u in sorted(blocked))))
            return "blocked", readout
        readout["reason"] = ("no unit of mode %s needs a host — %d done, %d already running. The market was "
                             "not consulted because nothing is for sale to us right now; this is NOT a price "
                             "hold." % (mode, len(out["done"]), len(out["live"])))
        return "nothing-to-launch", readout
    # ⛔ THE GATE MUST PRICE A BOARD THE LAUNCHER WOULD ACTUALLY BUY FROM (measured 2026-07-29). Its whole
    # justification is that `gate_for_mode` and `submit` ask the same question from the same code — and the
    # exclusion set is part of that question. `ternary-vast-market-hold.json` @ 13:01:41Z priced exactly one
    # offer, machine 28164, in the same file that names our own instance 46191306 on machine 28164: the gate
    # quoted $0.052/hr on a machine that could not take a second unit from us, and the rental that followed
    # was capacity-refused. A quote for a host we cannot use is not a cheap board, it is a wrong number.
    _occ = set(out.get("occupied_machines") or ())
    hold, readout = market_gate(n, key=key, excluded=tuple(set(excluded or ()) | _occ),
                                max_ratio=max_ratio, mode=mode)
    if _occ:
        readout["machines_we_already_occupy"] = sorted(_occ)
    readout.update({"mode": mode, "nothing_to_launch": False,
                    "units_done": out["done"], "units_live": out["live"],
                    "units_needing_host": out["needed"],
                    # ★ NAME THE UNITS THAT ARE ONLY FOR SALE BECAUSE THEIR LAST HOST DIED. Without this the
                    # snapshot cannot distinguish "this cohort was never launched" from "this cohort was
                    # launched and three of its hosts are corpses", and those want different reactions from
                    # whoever reads it. Each row carries the state that condemned the box, so the judgement is
                    # auditable rather than asserted.
                    "units_replacing_a_dead_host": [
                        {"unit_id": u, "dead_instance": i.get("id"), "machine_id": i.get("machine_id"),
                         "gpu": i.get("gpu_name"), "actual_status": i.get("actual_status"),
                         "cur_state": i.get("cur_state")}
                        for u, i in sorted((out.get("dead_hosts") or {}).items())]})
    # ⛔ THE WITHHELD UNITS, ON THIS BRANCH TOO. `n > 0` means SOME unit is being priced — it does not mean
    # every other unit is accounted for, and until now this branch listed only done/live/needed, so a
    # withheld unit disappeared from the snapshot entirely. See `_withheld_rows_for_gate`.
    _wr, _ur = _withheld_rows_for_gate(out), _unblocked_rows_for_gate(out)
    if _ur:
        readout["units_unblocked"] = _ur
    if _wr:
        readout["units_blocked"] = _wr
        readout["reason"] = (
            "%s ⛔ SEPARATELY: %d unit(s) of this mode are WITHHELD by the failure breaker and are NOT part "
            "of this quote — %s. Those units are STALLED, not finished; this gate priced only the %d unit(s) "
            "that can actually be rented."
            % (readout.get("reason", ""), len(_wr),
               ", ".join("%s (%s failed hosts)" % (w["unit_id"], w["n_attempts"]) for w in _wr), n))
    return ("hold" if hold else "clear"), readout


# =============================================================================================================
# THE TVAST-SUMMARY ROW'S STATE TOKEN — ONE GLYPH, ONE MEANING
# =============================================================================================================
# ★★ A HOST WE TORE DOWN AND A HOST WE ARE STILL PAYING FOR MUST NOT RENDER ALIKE (2026-07-28). This is
# CLAUDE.md §1's `⚠ PAYING` / `⛔ REFUSED` ruling applied to the teardown decision instead of to the buy line,
# and it is the defect the 11:14 PM ET board of 2026-07-27 actually had (run 30325339528, job 90169487825).
#
# WHAT THAT BOARD REALLY SHOWED, because the received account of it is wrong in three ways and the wrong
# account keeps generating the wrong fix:
#   * FIVE of eight instance rows carried `☠ UNIT status=failed`, and **every one of the five was a TRUE
#     POSITIVE** — each unit's `leg.json` was written by the host it was printed against, not by an earlier
#     attempt. The recency gate was working.
#   * **All five were DESTROYED in that same pass** (`-> destroying <id> (unit FAILED — nothing left to
#     produce)`), so no money was burning on any of them. The board simply never said so: the destroy verdict
#     is 40 lines up in the per-instance detail, which is exactly the part GitHub truncates, while the summary
#     — printed last precisely BECAUSE it survives truncation — still showed `up=running … dph=$0.193 ☠`,
#     which reads as a live rental on a dead leg. A reader of that board concluded money was burning on dead
#     hosts, and the board gave them no way to conclude otherwise.
#   * Instance 46057228 (`calib_hi_to_lo__ternary_vhl_r2…edge_reps`) is the case usually cited as the false
#     positive, on the strength of a census that "advanced" 192→320 while it printed ☠. Its census on the
#     9:17 PM ET board (run 30319800231) was `warmup/128`, not 192 — the 192 belongs to instance 46055595 on
#     the same board — and its leg genuinely died ON IT at 02:13:05Z, 61 minutes before the poll, against a
#     host started at ≈00:16Z. Record newer than instance ⇒ ☠ correct ⇒ destroy correct.
#
# SUPERSEDED, retained so it is not re-argued: "the DESTROY decision is already recency-gated and the
# RENDERING is not; a previous agent fixed only the decision side." Both halves are backwards. The decision
# side has carried `_record_is_newer_than_instance` since before the marker existed, and commit 65889ed9
# ("The dead-unit marker must not label a fresh retry host", 9:06 PM ET) re-keyed the RENDERING onto that same
# per-instance verdict — which is why the 11:14 PM board printed no false ☠ at all.
#
# So the marker did not need a recency gate added; it needed to stop being the only thing on the row. Three
# states shared one rendering and a fourth was invisible:
#   ☠ = this host's OWN leg died on it (record newer than the instance)   — the recency-gated fact, reused
#   ⏳ = a failed record exists but PREDATES this host — deliberately ignored, the box is cold-starting
#   ▲ = the committed census rose on this poll — the box is doing work
#   ⛔ = we destroyed this box in this pass: billing STOPPED, $0 further   (§1's "$0 spent" sense)
#   ⚠ = money is STILL GOING OUT on this row                              (§1's "PAYING" sense)
# `⏳` is not cosmetic: the recency gate's correct answer used to render as SILENCE, so "there is a stale
# failed record here that we are knowingly ignoring" was indistinguishable from "this unit is clean", and the
# operator could not tell a suppressed stale record from an absent one.
def summary_marker(record, *, leg_died_on_this_host, destroyed=None, progress_advanced=False):
    """The ONE renderer for a TVAST-SUMMARY row's state token. PURE — no S3, no Vast, no clock.

    `record`               the unit's `leg.json` dict as read by `leg_records`, or None if it has none.
    `leg_died_on_this_host` the DECISION PATH's OWN verdict — the `crashed` boolean that gates the teardown,
                           i.e. `status == "failed" AND _record_is_newer_than_instance(record, instance)`.
                           It is PASSED IN, never recomputed here: CLAUDE.md §1, one fact one place. A second
                           derivation in the renderer is exactly how a board could print ☠ on a host the
                           guard had spared, or spare a host it had condemned.
    `destroyed`            None if this pass did not try to tear the box down, else {"ok": bool, "why": str}
                           — the OUTCOME, because a destroy that raised leaves the meter running and must not
                           render like one that stopped it.
    `progress_advanced`    whether the committed-iteration census rose since the previous poll.

    Returns "" or a leading-space-prefixed token string, so the caller can concatenate it unconditionally.
    """
    failed = bool(record) and record.get("status") == "failed"
    stamp = (record or {}).get("updated_utc") or (record or {}).get("_s3_last_modified") or "unknown time"
    dead = bool(leg_died_on_this_host)
    out = []
    if dead:
        out.append(f"☠ LEG DIED ON THIS HOST at {stamp} (rc={(record or {}).get('rc')}) — "
                   f"the record was written AFTER this instance started, so it is this host's own failure")
    elif failed:
        out.append(f"⏳ STALE failed record ({stamp}) PREDATES this host — NOT dead, this box is cold-starting "
                   f"or working; the record belongs to an earlier attempt and is being ignored")
    if progress_advanced and not dead:
        out.append("▲ ADVANCING — committed census rose since the last poll")
    if destroyed and destroyed.get("ok"):
        out.append(f"⛔ DESTROYED this pass ({destroyed.get('why')}) — billing STOPPED, $0 further")
    elif destroyed:
        out.append(f"⚠ DESTROY FAILED ({destroyed.get('why')}) — STILL BILLING")
    elif dead:
        out.append("⚠ STILL BILLING — nothing tore this host down on this pass")
    return (" " + " | ".join(out)) if out else ""


def collect(bucket=None, prefix=None, autostop=True):
    """Status board + PROGRESS check + anti-idle reap. Returns (n_instances_up, n_done).

    "Progress", not "liveness": for every live instance this prints the furthest committed iteration and
    compares it against the previous poll's, because an instance being up says nothing about whether the
    MD is advancing.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    s3 = _s3()
    recs = leg_records(b, p)
    done = {u: d for u, d in recs.items() if d.get("status") == "done"}
    other = {u: d for u, d in recs.items() if d.get("status") != "done"}

    key = os.environ.get("VAST_API_KEY")
    mine = []
    # ★★ WHETHER THE LIST WAS READABLE IS ITSELF A FACT THE BOARD NEEDS (measured 2026-07-29, 4:04 PM ET).
    # `mine = []` is the right DEGRADATION for the reap loop below — an unreadable list must reap nothing —
    # but it is a lossy one, because an empty list means "no hosts" and an unreadable list means "we do not
    # know", and downstream those two produced the SAME six `NO HOST` rows. Six legs appearing to die at once
    # is a 3 AM emergency; a throttled read is nothing at all. So the error is kept, not just printed, and
    # the board renders UNKNOWN with this text as the reason. `None` = the list was read.
    _inst_unreadable = None
    if key:
        try:
            mine = [i for i in _vast_request("GET", "/instances/", key).get("instances", [])
                    if (i.get("label") or "").startswith(LABEL_PREFIX)]
        except Exception as e:  # noqa: BLE001
            _inst_unreadable = f"{type(e).__name__}: {e}"
            print(f"[collect] could not list instances: {_inst_unreadable}")
    else:
        # No key is a different unreadability with the same consequence: we cannot see hosts, so we must not
        # claim there are none. It is stated separately because the remedy is a missing secret, not patience.
        _inst_unreadable = "VAST_API_KEY is not set in this environment"

    # ★ THE LAUNCH-ATTEMPT LEDGER, FIRST. `_last_launch.json` below is written by the LAUNCHER, so it is
    # silent about exactly the failure that misled a reader on 2026-07-27: a gate that cleared, dispatched,
    # and was refused by a price check before the launcher ever ran. The ledger is written by CI at the
    # moment of the event and therefore covers that case. Printed here because `collect` is the command
    # anyone debugging this lane already runs.
    try:
        import ternary_launch_ledger as _tll
        print(_tll.summary_line())
    except Exception as e:  # noqa: BLE001 — a diagnostic must never break the board it is printed on
        print(f"[ledger] unavailable: {type(e).__name__}: {e}")

    # The last launch's own record — what it asked for, what it rented, and why anything failed. A launch
    # that rents nothing currently exits 0, and GitHub truncates a job log from the tail, so without this
    # the only evidence is the absence of instances.
    try:
        ll = json.loads(s3.get_object(Bucket=b, Key=f"{p}/_last_launch.json")["Body"].read())
        print(f"[collect] last launch {ll.get('utc')} mode={ll.get('mode')}: "
              f"{len(ll.get('submitted') or [])} rented, {len(ll.get('failed') or [])} FAILED "
              f"of {len(ll.get('requested') or [])} requested; excluded={ll.get('excluded_machines')}")
        for f_ in (ll.get("failed") or []):
            print(f"    LAUNCH-FAILED {f_.get('unit_id')}: {f_.get('error')}")
    except Exception:  # noqa: BLE001 — no launch recorded yet
        pass
    print(f"[collect] {len(done)} finished unit(s), {len(other)} other record(s), {len(mine)} instance(s) up")
    for u, d in sorted(done.items()):
        t = (d.get("timing") or {}).get("production") or {}
        print(f"  DONE  {u}: dG_morph = {d.get('dg_morph_kcal')} +/- {d.get('mbar_se_kcal')} kcal/mol "
              f"| NaN={d.get('nan_seen')} | prod {t.get('median_s_per_iter')} s/iter (n={t.get('n')})")
    for u, d in sorted(other.items()):
        print(f"  ....  {u}: status={d.get('status')} rc={d.get('rc')} NaN={d.get('nan_seen')} "
              f"updated={d.get('updated_utc')} s3_mtime={d.get('_s3_last_modified')}")
        for ln in (d.get("log_tail") or [])[-15:]:
            print(f"      T| {ln[:200]}")

    # previous poll's per-instance clocks + blocked machines
    prev_state = {}
    try:
        prev_state = json.loads(s3.get_object(Bucket=b, Key=f"{p}/_lane_state.json")["Body"].read())
    except Exception:  # noqa: BLE001 — first run
        prev_state = {}
    new_state, blocked = {}, set()
    # Machines already known bad from PREVIOUS passes. The replacement check must exclude them or it would
    # price a board including hosts that have already refused us — and then destroy a live box on the
    # strength of an offer we could not actually take.
    _prior_blocked = {str(m) for m in (prev_state.get("_blocked_machines") or [])}
    # Boxes this pass HELD instead of destroying, so the readout can show them with their snapshot.
    held_boxes = []

    # DEDUPE before anything else: two instances on one unit write the same S3 keys, do the same work and
    # bill twice. Keep the oldest (most progress, checkpoints already committed) — but a WORKING host beats an
    # older dead one every time.
    #
    # ⚠ "OLDEST" ALONE BECAME WRONG THE MOMENT THE LAUNCHER STARTED RE-PLACING DEAD UNITS (2026-07-27). The
    # ordering was written when a corpse kept its unit off the launch list forever, so a duplicate could only
    # ever be two live boxes. Now a unit whose host has `exited` is re-placed, and for the seconds or minutes
    # before the reap lands there are two records under one label — with the OLDEST being the dead one. Sorting
    # on age alone would destroy the replacement that was just paid for and leave the corpse, which is the
    # failure this whole change exists to end, arriving through the cleanup path instead.
    if key and mine:
        from gpu_backend import vast_instance_occupies_slot
        by_label = {}
        for i in mine:
            by_label.setdefault(i.get("label") or "", []).append(i)
        for lab, group in by_label.items():
            if len(group) < 2:
                continue
            group.sort(key=lambda x: (not vast_instance_occupies_slot(x), float(x.get("start_date") or 0)))
            print(f"  DUPLICATE {lab}: {len(group)} instances; keeping {group[0].get('id')}, "
                  f"destroying {[g.get('id') for g in group[1:]]}")
            for d_ in group[1:]:
                # ★ RECORDED, LIKE EVERY OTHER TEARDOWN (2026-08-01). This loop runs BEFORE `_destroy` is
                # defined, so it had its own DELETE and therefore its own hole in the billed-hours ledger —
                # and a duplicate is a host we genuinely rented and genuinely paid for, which is the whole
                # reason destroying it is worth doing. Before the ledger, the money spent on a double
                # rental left no trace anywhere once this line ran.
                try:
                    _tbl.record(d_, unit_id=lab, reason="duplicate")
                except Exception as _e:  # noqa: BLE001 — the ledger must never block a teardown
                    print(f"    [ledger] could not record duplicate {d_.get('id')}: {type(_e).__name__}: {_e}")
                try:
                    _vast_request("DELETE", f"/instances/{d_.get('id')}/", key)
                except Exception as e:  # noqa: BLE001
                    print(f"    destroy {d_.get('id')} failed: {e}")
            mine = [x for x in mine if x not in group[1:]]

    dead_instances = set()
    # PER-ROW FACTS FOR THE SUMMARY, captured where they are DERIVED rather than re-derived at render time.
    # `summary_marker` is pure and is handed these; nothing in the rendering block recomputes a verdict.
    row_record = {}        # iid -> the unit's leg.json (or None). The VERDICT on it is `dead_instances`.
    row_advanced = {}      # iid -> committed census rose since the previous poll
    destroyed_this_pass = {}   # iid -> {"ok": bool, "why": str}
    _board_rows = []           # one entry per LIVE leg, for the in-flight board printed at the end

    def _destroy(iid, why, inst=None, unit_id=None):
        """Issue the teardown AND record its OUTCOME, so the summary can say whether billing actually stopped.

        Every teardown in this function goes through here. A destroy that raises used to print one line deep
        in the per-instance detail and then render, in the summary, exactly like a successful one — i.e. a box
        still on the meter looked identical to a box that is off it.

        ★★ AND IT IS WHERE THE BILLED HOURS ARE RECORDED (2026-08-01). Destroy is the LAST moment the
        instance record exists — after this the rate, the start_date and the machine are unrecoverable, and
        this lane's only per-rental artifact (`ternary-vast-rental-receipt.json`) is overwritten by the next
        launch. That is how a rental could bill and leave no trace: the prune smoke's instance 46459452 did
        exactly that overnight. Recorded BEFORE the DELETE, because a row written only on success would miss
        precisely the boxes whose teardown failed — the ones still on the meter."""
        try:
            _tbl.record(inst or {"id": iid}, unit_id=unit_id, reason=why)
        except Exception as _e:  # noqa: BLE001 — the ledger must never be able to block a teardown
            print(f"    [ledger] could not record rental {iid}: {type(_e).__name__}: {_e}")
        try:
            _vast_request("DELETE", f"/instances/{iid}/", key)
            destroyed_this_pass[iid] = {"ok": True, "why": why}
            return True
        except Exception as e:  # noqa: BLE001 — a failed teardown is a REPORTABLE state, never a crash
            destroyed_this_pass[iid] = {"ok": False, "why": f"{why}; DELETE raised {type(e).__name__}: {e}"}
            print(f"    destroy failed: {e}")
            return False

    for i in mine:
        iid, lab = i.get("id"), i.get("label")
        uid = next((u for u in list(recs) + [j for j in _known_unit_ids()] if label_matches_unit(lab, u)), None)
        up_h = 0.0
        try:
            up_h = (time.time() - float(i.get("start_date") or time.time())) / 3600.0
        except (TypeError, ValueError):
            pass
        cost = up_h * float(i.get("dph_total") or 0)
        print(f"  vast {iid} ({lab}) {i.get('actual_status')} up={up_h:.2f}h "
              f"dph=${i.get('dph_total')} spent~${cost:.2f} gpu={i.get('gpu_name')}")

        # ★ THE UNIT'S OWN VERDICT IS EVIDENCE, AND IT HAS TO BE READ BEFORE THE HOST IS JUDGED
        # (2026-07-27). `crashed` used to be computed BELOW the idle-guard call, so the guard inferred a
        # mechanism from log silence while this stronger, direct fact was already available three lines
        # later — and printed "the host has lost its write path" about two boxes whose last successful act
        # was writing to S3. Same destroy, wrong sentence. Hoisted so the guard is told, not left to guess.
        # ★★ A `done` RECORD THAT PREDATES THIS HOST IS NOT EVIDENCE THIS HOST HAS NOTHING TO DO
        # (2026-08-01, and it cost the `.chk` prune shakeout its entire rental).
        #
        # WHAT HAPPENED, verbatim from the 10:04:46 PM ET collect of 2026-07-31 (run 30679242052, job
        # 91312781129). The prune smoke rented instance 46459452 (machine 12976, RTX 4090, $0.12531/h,
        # $0.00374/ns = 1.10x basis — correctly gated) at 10:02 PM. Two minutes and twenty-three seconds
        # later, while the container was still pulling its image:
        #
        #     vast 46459452 (...-f495e0fc) loading up=0.04h ... msg='0eee12ace5f3: Verifying Checksum'
        #       -> destroying 46459452 (unit done)
        #
        # `finished = uid in done` was true because that unit's `leg.json` had said `status=done` since
        # 2026-07-26 — the ORIGINAL smoke, five days earlier. So the reaper killed a host that had not yet
        # executed one line of `run_ternary_leg.sh`, and the shakeout produced no `[prune]` line, no
        # `chk_pruned` manifest, no `run.log`, not even a `status.json`. Every artifact a reader could reach
        # was byte-identical to "no rental ever happened", which is why it took a forensic to find.
        #
        # IT IS GENERAL, NOT A SMOKE QUIRK: any deliberate re-run of a unit that already landed — a
        # shakeout, a re-measurement, a supersede-and-recompute — is destroyed by the next tick, before it
        # can do anything. The launcher decides to buy and the reaper immediately decides the purchase was
        # pointless; two components disagreeing about one rental.
        #
        # THE FIX IS THE PREDICATE THAT WAS ALREADY THERE. `crashed` has been guarded by
        # `_record_is_newer_than_instance` since the protfep lane learned the same lesson about stale FAILED
        # records; `finished` never was. It is the identical question — *did THIS host write that record?* —
        # and in the normal case the answer is yes, because a leg writes its `leg.json` while its own host
        # is up. Same shape as `_finalizable` in the price ledger, which refuses to latch a cost on a result
        # that predates the rental.
        #
        # ⚠ AND NOT DESTROYING IS THE SAFE DIRECTION HERE, WHICH IS WHY THIS IS NOT A NEW LEAK RISK. A truly
        # finished host that survives this branch is still caught by `MAX_INSTANCE_HOURS` and by
        # `vast_idle_guard` (~15 min of no writes), so the cost of being wrong is minutes of one box. The
        # cost of the old behaviour was an entire authorised experiment, silently, with no artifact saying so.
        finished_record = uid in done
        _done_rec = done.get(uid) if uid else None
        _done_is_ours = bool(_done_rec and _record_is_newer_than_instance(_done_rec, i))
        finished = bool(finished_record and _done_is_ours)
        if finished_record and not finished:
            # ⚠ SAID OUT LOUD. A guard that silently stops firing is indistinguishable from a guard that was
            # removed, and this one used to destroy — so the pass has to state that it saw a done record and
            # declined to act on it, or the next reader re-derives this whole forensic.
            print(f"      ⓘ this unit has a `done` leg.json, but it was written BEFORE this host started "
                  f"— so it is the PREVIOUS attempt's result, not this one's. NOT destroying on "
                  f"'unit done'; a deliberate re-run (shakeout, re-measurement) is allowed to proceed. "
                  f"The runtime backstop and the idle guard still cover this box.")
        _rec = other.get(uid) if uid else None
        _newer = bool(_rec and _record_is_newer_than_instance(_rec, i))
        crashed = bool(_rec and _rec.get("status") == "failed" and _newer)
        if crashed:
            dead_instances.add(iid)
        # The record itself, kept for the summary's TEXT (its timestamp and rc). The VERDICT on it stays in
        # `dead_instances` and is never re-derived at render time — a stale failed record (present, but older
        # than this host) is the case the summary used to render as silence.
        row_record[iid] = _rec

        # PROGRESS, not liveness.
        idle_verdict, idle_why = vig.UNKNOWN, "no unit could be mapped to this instance's label"
        if uid:
            phase, it, scalar = committed_progress(uid, b, p)
            prev = (prev_state.get(f"prog:{uid}") or [0, 0])
            pprog = prev[0] if isinstance(prev, (list, tuple)) else 0
            pstall = prev[1] if isinstance(prev, (list, tuple)) and len(prev) > 1 else 0
            stall = 0 if scalar > pprog else int(pstall) + 1
            new_state[f"prog:{uid}"] = [scalar, stall]
            row_advanced[iid] = bool(scalar > pprog)
            # THE ESCALATION IS EVIDENCE-DRIVEN IN BOTH DIRECTIONS. A census that MOVED is proof the
            # current tier can hold this leg, so the lost-host counter goes back to zero and the next
            # re-placement is priced on the cheap tier again. Without this reset the counter would only
            # ever rise and one bad afternoon would put a unit on on-demand permanently.
            if scalar > pprog:
                new_state[f"replaced:{uid}"] = 0
            print(f"      committed: {phase or 'none yet'}"
                  f"{('/' + str(it)) if phase else ''}  scalar={scalar} prev={pprog} "
                  f"no-advance-polls={stall}")
            # The commit census is blind for the whole cold start, so pair it with the on-host phase
            # marker and log tail — that is what turns a liveness ping into a progress check.
            # ⚠ 60 LINES, NOT 8, AND THE PRINTED TAIL IS STILL 8. The in-flight board needs two lines the
            # driver emits ONCE at startup and never repeats — `[spot-driver] warmup_target=N ... prod_target=M`
            # — because those are the denominator of "% complete" and this process has no MD stack to
            # re-derive them with. At tail=8 they scroll away the moment MD starts, so the board would show
            # `—` for every advancing leg, which is the useless-column failure again. Reading more costs
            # nothing (one S3 GET either way, a few KB) and the operator-facing tail below is unchanged.
            mark, mark_age, tail, log_age = phase_and_log(uid, b, p, tail=60)
            # ★★ A MARKER OLDER THAN THE HOST BELONGS TO A DIFFERENT ATTEMPT, AND SAYING SO IS THE WHOLE
            # POINT (2026-07-29, 11:37 AM ET). The phase marker and run.log live at a per-UNIT key, not a
            # per-attempt one, so a freshly rented host inherits whatever the unit's LAST attempt left there
            # until it writes its own. `calib_lo_to_lo2__ternary_vhl` was two minutes into a clean start and
            # this line read:
            #
            #     phase: done 2026-07-28T10:39:56Z  (marker 1737 min old, log 1737.0 min old)
            #     | Traceback (most recent call last):
            #
            # — the "done" and the traceback both belonging to yesterday's partial-charge death, printed
            # against a leg that had not yet produced a single iteration. Read at a glance that is a finished
            # leg, or a leg that has already crashed again; it is neither.
            #
            # ⚠ NOTHING IS BEING FIXED IN THE CONTROL PATH HERE, AND THAT IS THE MEASURED FINDING RATHER THAN
            # AN ASSUMPTION. Every clause that can act was checked against this box: `reap_landed` keys on a
            # `status == "done"` leg.json (this unit's was archived by `--supersede-failed`, so there is no
            # record at all), the crash/reap clause is already guarded by `_record_is_newer_than_instance`,
            # and the frozen clause keys on the VAST status message tracked across polls (`unchanged_for=0min`
            # here), not on marker age. The idle guard abstained on its own. So this is a READOUT defect and
            # is fixed as one — but it is exactly the class CLAUDE.md §1 legislates against, because the
            # cheapest way for a stale fact to become a wrong decision is for it to render as a current one.
            _mark_stale = marker_predates_host(mark_age, up_h)
            print(f"      phase: {mark or '(no marker yet — image pull / container start)'}"
                  + (f"  (marker {mark_age:.0f} min old" if mark_age is not None else "  (")
                  + (f", log {log_age:.1f} min old" if log_age is not None else ", no log yet") + ")"
                  + (f"  ⚠ PREVIOUS ATTEMPT'S MARKER — older than this host ({up_h * 60.0:.0f} min); "
                     f"this leg has written nothing yet, and the phase and log lines below describe the "
                     f"attempt before it" if _mark_stale else ""))
            for ln in tail[-8:]:
                print(f"      | {ln[:170]}")
            # ── one row for the in-flight board. Every cell is DERIVED from facts already read on this
            # pass; nothing here re-reads S3 and nothing here is typed. `_board_log` keeps the full 60-line
            # text so the board can find the startup target line the printed tail deliberately drops.
            _board_log = "\n".join(tail)
            # ── CONTENT IDENTITY OF THE LOG, for the idle guard's condemnation 3. Hashed from the text
            # already in hand, so this costs no S3 call. The mtime cannot serve: run_ternary_leg.sh syncs
            # run.log from a background timer every ~120 s whether or not a byte changed, which is why a
            # host that wedged inside a checkpoint persist billed 77 min while the guard called it alive.
            # `first_seen` is the epoch at which THIS content first appeared; it survives across polls in
            # the lane state, so the age is measured, never assumed from a poll count (poll cadence is not
            # a knowable duration — CLAUDE.md §6 on throttled crons).
            _log_id = hashlib.sha256(_board_log.encode()).hexdigest()[:16]
            _prev_log = prev_state.get(f"logid:{uid}") or []
            _now = time.time()
            _first_seen = (_prev_log[1] if len(_prev_log) > 1 and _prev_log[0] == _log_id else _now)
            new_state[f"logid:{uid}"] = [_log_id, _first_seen]
            _log_unchanged_min = (_now - float(_first_seen)) / 60.0
            _board_rows.append({
                "uid": uid, "iid": iid, "log": _board_log,
                "phase": phase, "iteration": it,
                "advanced": bool(scalar > pprog), "no_advance_polls": stall,
                "up_h": up_h, "gpu": i.get("gpu_name"), "dph": i.get("dph_total"),
                # ★ WHICH TIER THIS HOST IS ON (trimcrae, 2026-07-31: "Update the status table to show on
                # demand / interruptible too."). `is_bid` is the instance record's OWN field — already in
                # `vast_rate_forensics._FIELDS`, so this costs nothing extra from the API. `.get` yields None
                # when the field is absent, and `inflight_usd_per_ns.tier_of` renders None as UNKNOWN rather
                # than as bid: an absent reading is not a reading of absence (CLAUDE.md §4), and the tier this
                # column exists to attribute spend to is exactly the one a silent default would hide.
                "is_bid": i.get("is_bid"),
                "marker_stale": _mark_stale, "mark": mark, "log_age": log_age,
            })
            # ANTI-IDLE VERDICT. Everything it needs has just been read, so this costs one extra S3 LIST.
            # It is the ONLY clause in this function that can act on a box that is `running` and looks
            # healthy — see vast_idle_guard for why GPU idleness alone is never allowed to condemn one.
            idle_verdict, idle_why = vig.classify_idle(
                instance_running=(i.get("actual_status") == "running"),
                container_started=container_started_from_phase(mark, i),
                gpu_util=i.get("gpu_util"),
                progress_advanced=(scalar > pprog),
                log_age_min=log_age,
                log_unchanged_min=_log_unchanged_min,
                start_ages_min=vig.start_ages_min(s3, b, f"{p}/legs/{uid}/attempts/"),
                instance_age_min=up_h * 60.0,
                unit_failed=crashed)
            print(f"      idle-guard: {idle_verdict} — {idle_why}")
            # ★★ HAND THE BOARD THE GUARD'S OWN SENTENCE (2026-07-29, 1:39 PM ET). The board's `_why` chain
            # covered a stale marker, a leg with no first checkpoint, missing targets and a missing rate —
            # but NOT the one case that actually matters: a leg that HAS committed and then stopped
            # advancing. That fell through with an empty reason, `state_of` refused to render an
            # unexplained STALLED (correctly), and the `except` around the board swallowed the whole table.
            # So the one poll where a leg genuinely stalled is the one poll that printed no board at all.
            #
            # `vast_idle_guard` has already composed exactly the sentence needed, from the same facts, and
            # it is the repo's one home for "what is this rental doing" — so the board reuses it rather than
            # growing a second, weaker explanation of the same state.
            if _board_rows and _board_rows[-1].get("iid") == iid:
                _board_rows[-1]["idle_why"] = f"{idle_verdict} — {idle_why}"
                _board_rows[-1]["idle_working"] = (idle_verdict == vig.WORKING)
                # SHIELDING = the guard looked and declined to condemn. Derived from `should_destroy`, not
                # from a list of verdict names typed here, so the board and the reaper cannot drift about
                # which verdicts are benign. See `state_of`'s `guard_shielding` note for the STALLED row
                # this produced on a leg the guard was actively vouching for.
                _board_rows[-1]["idle_shielding"] = (
                    idle_verdict == vig.WATCHING and not vig.should_destroy(idle_verdict))

        msg = str(i.get("status_msg") or "").strip()
        frozen_min, new_state[str(iid)] = stall_minutes(prev_state, iid, msg, time.time())
        if i.get("actual_status") != "running":
            print(f"      why: cur_state={i.get('cur_state')} intended={i.get('intended_status')} "
                  f"msg={msg[:180]!r} unchanged_for={frozen_min:.0f}min")

        # WHY THE IDLE VERDICT IS LAST IN THIS CHAIN. `finished` and `crashed` are stronger facts about the
        # same box — a leg that landed its result stops writing its log by design, so on the very next poll
        # it would ALSO read WEDGED. Ordering them first keeps the destroy REASON honest ("unit done", not
        # "the host went quiet"), which is what a reader of this board is actually trying to learn.
        why = ("unit done" if finished else
               "unit FAILED — nothing left to produce" if crashed else
               "runtime backstop" if up_h > MAX_INSTANCE_HOURS else
               f"idle guard: {idle_verdict} — {idle_why}" if vig.should_destroy(idle_verdict) else None)
        if autostop and why:
            print(f"    -> destroying {iid} ({why})")
            _destroy(iid, why, inst=i, unit_id=uid)
        elif (i.get("actual_status") != "running" and i.get("cur_state") == "running"
              and frozen_min > MAX_FROZEN_MIN):
            print(f"    -> destroying {iid} (status frozen {frozen_min:.0f} min at {msg[:60]!r}; "
                  f"the image pull is dead, not queued)")
            _destroy(iid, f"status frozen {frozen_min:.0f} min — the image pull is dead, not queued",
                     inst=i, unit_id=uid)
        elif i.get("cur_state") == "stopped":
            # A stopped box has two causes that demand OPPOSITE actions, and only the start response
            # separates them. Re-issue the start (idempotent) and read the reply.
            #
            # ⚠ THIS NUDGE IS DELIBERATELY NOT $/ns-GATED, and that is the ONE genuine exemption the relaunch
            # gate names (`relaunch_market_gate.EXEMPTIONS["already_held_instance"]`). Re-starting an instance
            # this account ALREADY HOLDS is not a purchase: the rate was fixed when the instance was created
            # and cannot move under us, and a stopped Vast box is billing for its disk in the meantime — so
            # holding here would cost money and save none. Everything that RENTS A NEW HOST is gated; this
            # resumes one we are already paying for.
            err = None
            try:
                resp = _vast_request("PUT", f"/instances/{iid}/", key, body={"state": "running"})
                err = (resp or {}).get("error")
                print(f"    -> NUDGED {iid}: cur_state=stopped; vast replied {str(resp)[:240]}")
            except Exception as e:  # noqa: BLE001
                print(f"    nudge failed: {e}")
            if err == "resources_unavailable":
                # NOT something to wait out ON THIS HOST. Vast is a market of independently priced hosts,
                # not a pool, and raising the bid was tested on 2026-07-25 (+26% to the value ceiling) and
                # changed nothing. So the machine is blacklisted unconditionally and the next placement
                # goes elsewhere.
                #
                # ★★ BUT THE TEARDOWN IS NOW CONDITIONAL (trimcrae, 2026-07-27: "we should only do that if
                # we know we have a better alternative"). The old rule destroyed immediately on the premise
                # that "a different host today costs what this one will tomorrow" — which assumed a
                # replacement was always purchasable. The buy line broke that premise: at 8:32 PM ET the
                # step 1 board's cheapest was 1.96x basis and ALL 12 units were refused. Destroying into
                # that market forfeits the instance's DISK (the staged inputs — the checkpoint itself is
                # safe in S3) and buys back only ~$0.011/hr of storage, while the gate declines to replace
                # what we just tore down. Full argument and the measured dollars: teardown_decision.py.
                blocked.add(str(i.get("machine_id")))
                print(f"    (machine {i.get('machine_id')} has no free GPU and no bid fixes it — blocked)")
                # ⓘ TREND, NOT A GATE. On 2026-07-29 this lane rented four hosts in 36 minutes — machines
                # 29711, 28164, 12227, 41950 — and every one refused on start while every board read was
                # CHEAP (1.04x-1.34x basis). CLAUDE.md §6 asks for the TREND in exactly that case, and there
                # was none to bring: `vast_machine_blacklist.publish` correctly refuses CLASS_CAPACITY, so a
                # sustained availability failure left no trace anywhere but four CI logs. This records the
                # event in a PERISHABLE 24 h window so the pattern is visible. It can never withhold a
                # rental — see capacity_refusal_trend.__doc__ and its tests.
                try:
                    import capacity_refusal_trend as _crt
                    _tr = _crt.record(s3, b, i.get("machine_id"), uid, lane="ternary",
                                      why="resources_unavailable on start")
                    if _tr:
                        print(_crt.render(_tr))
                except Exception as _e:  # noqa: BLE001 — instrumentation must never break a teardown
                    print(f"    (capacity-refusal trend unavailable: {_e})")
                # scope="host": nothing about OUR workload enters this verdict, so every lane may act on it.
                # Publishing here is what stops the fan-out paying its own rental to rediscover the same box.
                try:
                    import vast_machine_blacklist as vmb
                    vmb.publish(s3, b, i.get("machine_id"),
                                f"resources_unavailable on start (instance {iid}, {i.get('gpu_name')})",
                                lane="ternary")
                except Exception as _e:  # noqa: BLE001 — a monitoring aid must never fail a collect
                    print(f"    (shared blacklist publish failed: {_e})")
                # Is a replacement actually purchasable? Asked through the SAME gate that would authorise
                # the replacement rental, so the two answers can never disagree — a board this refuses to
                # buy from is a board we must not tear down into. It reads the live market; on any failure
                # we fail CLOSED (treat it as "no replacement") rather than destroy blind, which is the
                # documented Vast-403-under-throttling hazard.
                repl = None
                try:
                    import relaunch_market_gate as _rmg
                    _hold, _gdoc = _rmg.gate("ternary", uid or str(iid),
                                             resource_spec(),
                                             key=key, excluded=tuple(blocked | _prior_blocked), s3=s3,
                                             state_bucket=b, state_prefix=p)
                    if not _hold:
                        repl = _gdoc.get("best_usd_per_ns")
                except Exception as _e:  # noqa: BLE001 — an unreadable board is NOT permission to destroy
                    print(f"    (replacement check failed, failing CLOSED: {type(_e).__name__}: {_e})")

                # disk_gb from the LANE'S OWN spec: storage is what a hold costs, and it scales with the
                # disk we requested. The 40 GB headline in bid-strategy.md F4 is stale for every live lane.
                _td = tdd.decide(replacement_usd_per_ns=repl,
                                 buy_line_usd_per_ns=_BUY_LINE_USD_PER_NS,
                                 stopped_min=up_h * 60.0, max_stopped_min=MAX_STOPPED_MIN,
                                 disk_gb=resource_spec().disk_gb)
                print(tdd.render(_td, instance_id=iid, machine_id=i.get("machine_id")))
                if _td["destroy"]:
                    # ★★ RECORD THAT *WE* ENDED THIS ATTEMPT, BEFORE ENDING IT (2026-07-29). Without this
                    # receipt the failure breaker sees only the unit's stale `status=failed` record plus a
                    # growing attempt archive, and files our own correct teardown as another strike — so the
                    # conditional-teardown ruling slowly poisons every unit it evicts. r2 reached 51 strikes
                    # and a permanent block this way while its checkpoint sat at warmup/576, advancing.
                    #
                    # ⛔ GUARDED, because this receipt can lift a block. It is written ONLY when the unit did
                    # not die on this host — `crashed` is False, which this branch already implies, since a
                    # crashed unit is destroyed by the `why` chain above and never reaches here — AND only
                    # when the record can be POSITIVELY dated to before this host started. A unit whose
                    # record we cannot date gets no receipt: `record_predates_host` returns None there, and
                    # crediting an eviction on a guess is how the 84-rental loop would come back.
                    if uid:
                        # Only a FAILED record can be superseded, so only a failed record needs dating.
                        _pre = (lfb.record_predates_host(_rec, i.get("start_date"))
                                if (_rec or {}).get("status") == "failed" else True)
                        if _pre is True:
                            try:
                                lfb.record_eviction(
                                    s3, b, p, uid,
                                    why=(f"capacity refusal on machine {i.get('machine_id')}; "
                                         f"{_td.get('verdict')}"),
                                    instance=iid, machine_id=i.get("machine_id"))
                                print(f"    -> ↻ EVICTION RECORDED for {uid}: this teardown was OUR "
                                      f"decision (market), not this unit failing — the failure breaker "
                                      f"will not count it as a strike.")
                            except Exception as _e:  # noqa: BLE001 — never fail a teardown on bookkeeping
                                print(f"    (eviction receipt not written: {type(_e).__name__}: {_e})")
                        else:
                            print(f"    (no eviction receipt for {uid}: its failed record cannot be dated "
                                  f"before this host started ({_pre!r}) — refusing to credit an eviction "
                                  f"on a guess)")
                    _destroy(iid, f"capacity refusal on machine {i.get('machine_id')}; "
                                  f"{_td.get('verdict')}", inst=i, unit_id=uid)
                else:
                    # VISIBLE, with the snapshot that caused it (CLAUDE.md §6) — a silent hold is
                    # indistinguishable from a lane that finished.
                    held_boxes.append({"instance": iid, "machine_id": i.get("machine_id"), **_td})
            elif up_h * 60 > MAX_STOPPED_MIN:
                print(f"    -> destroying {iid} (stopped {up_h * 60:.0f} min, not a capacity wait)")
                _destroy(iid, f"stopped {up_h * 60:.0f} min, not a capacity wait", inst=i, unit_id=uid)

    # ONE COMPACT LINE PER UNIT, LAST. GitHub truncates a job log from the tail, and this board's per-instance
    # detail is long enough that on a busy poll the verdict scrolls out of a 25-line fetch — which is exactly
    # when a monitor most needs it. So repeat the decision-relevant facts in one grep-able line each.
    # ⛔ HELD BOXES, BEFORE the summary. A capacity-refused box we KEPT is money not being spent on a GPU and
    # a decision that must be auditable; printing nothing would make it indistinguishable from a teardown.
    if held_boxes:
        print(f"---- TVAST-HELD ({len(held_boxes)} capacity-refused box(es) kept, not destroyed) ----")
        for h in held_boxes:
            print(f"TVAST-HELD instance={h['instance']} machine={h['machine_id']} "
                  f"stopped={h['stopped_min']:.0f}min storage=${h['hold_cost_usd_h']:.3f}/hr "
                  f"best_replacement={h['replacement_usd_per_ns']} buy_line={h['buy_line_usd_per_ns']} "
                  f"-> {h['verdict']}")
    print("---- TVAST-SUMMARY ----")
    for u, d in sorted(recs.items()):
        t = (d.get("timing") or {}).get("production") or {}
        print(f"TVAST {u} status={d.get('status')} dG={d.get('dg_morph_kcal')} se={d.get('mbar_se_kcal')} "
              f"NaN={d.get('nan_seen')} prod_s_per_iter={t.get('median_s_per_iter')}")
    for i in mine:
        uid = next((u for u in list(recs) + _known_unit_ids() if label_matches_unit(i.get("label"), u)), None)
        ph, it, sc = committed_progress(uid, b, p) if uid else (None, 0, 0)
        # ★★ A DEAD LEG AND A HEALTHY COLD START MUST NOT RENDER ALIKE (2026-07-27). `committed=none/0` is
        # the CORRECT and expected reading for a leg in `start`/`cloned`/`staging`/`preequil`, and the
        # documented grace before zero counts as a stall is ~90 min — so `up=running committed=none/0` on
        # its own is unreadable: it is the same string for "staging normally" and for "died with a
        # traceback 38 minutes ago". On this lane it cost a diagnostic turn: two legs that had exited rc=1
        # at 7:59 PM ET were still being read as possibly-healthy cold starts at 8:37 PM ET, because the
        # unit's `status=failed` appeared only in a different section of the board. The unit's own verdict
        # belongs on the unit's own line. Same rule as §1's "paying" vs "refused" glyphs: one state, one
        # rendering.
        # ★ AND IT KEYS ON THE PER-INSTANCE VERDICT, NOT ON THE UNIT RECORD (caught within the hour, by
        # this very marker, on run 30319083631). A unit's `status=failed` is a fact about the LAST attempt,
        # not about the host in front of you: two fresh retry hosts were rented at 8:59 PM ET for the two
        # dead units and this line labelled BOTH of them dead while they were still pulling their image.
        # That is exactly the stale-record trap `_record_is_newer_than_instance` exists for, so reuse its
        # answer from the loop above rather than re-deriving a weaker one here.
        # ★★ AND IT NOW ALSO SAYS WHAT WE DID ABOUT IT. Every fact below was DERIVED in the loop above and is
        # merely handed to the renderer — see `summary_marker` for why a row we tore down and a row we are
        # still paying for must not look the same, and for what the 11:14 PM ET board of 2026-07-27 actually
        # showed. `dead_instances` stays the keying fact for ☠; it is `crashed`, i.e. recency-gated.
        _iid = i.get("id")
        dead = summary_marker(row_record.get(_iid),
                              leg_died_on_this_host=(_iid in dead_instances),
                              destroyed=destroyed_this_pass.get(_iid),
                              progress_advanced=row_advanced.get(_iid, False))
        # INSTANCE ID ON EVERY PROGRESS LINE. A progress reading is only worth anything if it is
        # attributable to the box you actually rented: a monitor that reports "advancing" from the wrong
        # job is the same silent-success class this lane's watchdog exists to prevent, and it is more
        # expensive here than elsewhere because the wrong reading leaves a billed GPU unwatched.
        print(f"TVAST {uid or i.get('label')} instance={i.get('id')} machine={i.get('machine_id')} "
              f"up={i.get('actual_status')} committed={ph or 'none'}/{it} "
              f"gpu={i.get('gpu_name')} dph=${i.get('dph_total')}{dead}")
    print("---- END TVAST-SUMMARY ----")

    # ── THE IN-FLIGHT BOARD ────────────────────────────────────────────────────────────────────────────
    # One table, one row per GPU leg (trimcrae, 2026-07-29, after asking three times for a simpler one).
    # Everything below is DERIVED from what this pass already read; the reporting agent copies this block
    # instead of rebuilding a table, which is what stopped it drifting in shape and losing its ETA column.
    #
    # ⚠ A ROW IS NEVER DROPPED FOR BEING UNKNOWABLE. An unknown percentage or ETA renders `—` with the WHY
    # column saying which fact was missing. Omitting the row instead would make a leg we cannot measure
    # look like a leg that does not exist, which is the same "silent hold" failure §6 prohibits for a fleet.
    try:
        _rows = []
        # Units this pass has established have NO host and are NOT done. Populated by the two branches that
        # already make that judgement, so the repair dispatch below and the board answer from one fact.
        _hostless_units = set()
        for _b in _board_rows:
          # ⚠ PER-ROW, NOT PER-TABLE. On 2026-07-29 a single row that could not explain its own
          # STALLED state raised, and the table-level `except` below swallowed EVERY row — so the
          # one poll where a leg genuinely stalled is the one poll that showed no board. A row that
          # cannot be built now degrades to a visible UNKNOWN row naming the failure, because a
          # missing row reads as a leg that does not exist.
          try:
              # The denominator comes from the driver's own startup line, which `phase_and_log` PINS into
              # every window for exactly this reason — see the note there. Nothing is remembered or
              # recomputed here: a persisted copy would be a second home for a number that log owns.
              _tg = ifb.parse_targets(_b["log"])
              _spi = ifb.measured_s_per_iter(_b["log"])
              _pct = ifb.pct_complete(_b["phase"], _b["iteration"], _tg)
              _eta = ifb.eta_seconds(_b["phase"], _b["iteration"], _tg, _spi)
              # ★★ MEASURE-ON-ARRIVAL (2026-07-31). `_spi` is what THIS host, on ITS card, with the REAL
              # 147,788-particle assembly, is actually delivering — strictly better evidence than any card
              # table, and it has been computed here for the ETA all along without ever being TESTED.
              # `vast_cost_model.verify_and_abandon_threshold` argued for exactly this and was wired to
              # nothing. Costs one dict build per row: no S3 read, no API call.
              #
              # ⚠ REPORT-ONLY FOR NOW, DELIBERATELY. `arrival_throughput.verdict` can say ABANDON, and acting
              # on it would make this the lane's SECOND destroyer beside `vast_idle_guard`. §6's ladder is
              # smoke -> one real leg -> fleet, and the honest equivalent here is to publish the verdict on a
              # live fleet first and read the numbers it produces before letting it destroy anything. The
              # action is one line (`retire_host(uid)`) once the readout has been graded.
              _arr = None
              try:
                  import arrival_throughput as _at
                  # Every input comes from THIS host's own 60-line window or its unit id — no S3 read, no API
                  # call, nothing remembered. The timestep is in the unit id; the checkpoint interval is the
                  # one the driver RESOLVED to (a resumed leg runs the grid baked into its .nc, not the one
                  # the mode requests); the quote is the same `$/ns` the board's own cell renders.
                  _dtm = re.search(r"_dt([\d.]+)fs_", _b["uid"] or "")
                  _dtv = float(_dtm.group(1)) if _dtm else None
                  # THE CARD IS PASSED, so the expectation is like-for-like. Without it the comparison is
                  # against a card-POOLED median and every below-median card reads as broken (measured: two
                  # healthy 3090s flagged at 1.86x / 2.00x, which are 0.97x / 1.04x against their own card).
                  # ★★ AND THE UNIT ID, so the expectation is like-for-SYSTEM as well as like-for-card
                  # (2026-08-01, closing the residual the provenance work named rather than left silent).
                  # The 4 fs ternary figure is POOLED ACROSS TWO SYSTEMS on every card but the 5090
                  # (nr4a3 x3 + vhl x4), and no `nr4a1` leg exists in the table at all — so without the
                  # unit id a live nr4a1 row is graded against a median half-composed of a different
                  # assembly and reads as ~2.6x drift that is pure arithmetic. trimcrae, this morning:
                  # "if it's a bigger molecule than our estimates are based on, it's gonna be more
                  # expensive… it's more important that we rank based on relative price per ns than
                  # actual". Ranking on QUOTED $/ns is unaffected — the offset cancels in a comparison —
                  # so this touches the readout only, never the purchase gate.
                  # ⚠ The size guard cannot substitute: `pooled_across_systems` reads FALSE here because
                  # 141,740–149,308 particles collapse into one bucket at its 15 % tolerance. IDENTITY,
                  # not size, is the discriminator, which is why the unit id is what has to travel.
                  _exp, _eprov, _expwhy = _at.expected_s_per_iter(
                      arm_of_leg(_b["uid"]), _dtv, card=_b.get("gpu"), unit_id=_b["uid"]) if _dtv \
                      else (None, _at.PROV_NONE, "timestep not in the unit id")
                  _qrow = _ifn.row(_b["gpu"], float(_b["dph"]), _planning_usd_per_ref_gpu_h(),
                                   tier=_ifn.tier_of(_b.get("is_bid"))) \
                      if (_b.get("gpu") and _b.get("dph") and _planning_usd_per_ref_gpu_h()) else None
                  _arr = _at.verdict(_spi, _exp, iteration=_b["iteration"],
                                     interval=ifb.interval_for_phase(_b["log"], _b["phase"]),
                                     quoted_usd_per_ns=(_qrow or {}).get("usd_per_ns"),
                                     provenance=_eprov)
                  _arr["expected_provenance"] = _expwhy
              except Exception as _e:  # noqa: BLE001 — a READOUT must never break a monitoring pass
                  _arr = {"verdict": "WATCHING", "why": "arrival check unavailable: %s: %s"
                                                        % (type(_e).__name__, _e)}
              # WHY, in priority order: the most specific true statement about this leg, so a STALLED row can
              # never be rendered without one (`state_of` raises if it would be).
              _why = ""
              if _b["marker_stale"]:
                  _why = "fresh host — the marker and log below belong to the previous attempt"
              elif _b["phase"] is None:
                  _why = ("no committed checkpoint yet; host up %.0f min and the first warmup boundary is one "
                          "checkpoint interval of MD after the image pull" % ((_b["up_h"] or 0) * 60.0))
              elif _tg is None:
                  _why = "targets not in the retained log window — %% and ETA unknowable this pass"
              elif _spi is None:
                  _why = "no openmmtools rate line in the log window — ETA unknowable, progress is real"
              else:
                  # The genuinely-stalled case: committed before, not advancing now. The idle guard's own
                  # sentence IS the reason; falling back to a generic string would be the unexplained stall
                  # `state_of` exists to refuse.
                  _why = _b.get("idle_why") or ""

              # The cold-start floor is IMPORTED, not typed. `vast_idle_guard.MIN_INSTANCE_AGE_MIN` is the one
              # home for "too young to have proved anything either way", and the board must agree with the
              # guard by construction — a board that called a box stalled while the guard was still shielding
              # it would be two definitions of the same thing, free to disagree at 3 AM.
              _cold = (_b["up_h"] or 0) * 60.0 < vig.MIN_INSTANCE_AGE_MIN
              # A leg that has NEVER committed has nothing to advance from, so the poll counter cannot judge
              # it — see `state_of`'s `pre_first_commit` note for the STALLED row this produced on the board's
              # first live run. Both thresholds are IMPORTED: the setup grace is `vig.SETUP_GRACE_MIN`, itself
              # `watchdog_policy.DEFAULT_SETUP_GRACE_MIN`, so the board, the idle guard and the watchdog all
              # answer "is this leg merely slow to start?" from one number.
              _pre_first = (_b["phase"] is None and (_b["up_h"] or 0) * 60.0 < vig.SETUP_GRACE_MIN)
              # ★★ THE CENSUS TICKS AT CHECKPOINT BOUNDARIES; POLLS ARE FASTER THAN THAT. A warmup
              # checkpoint lands every 64 iterations, and `collect` runs every few minutes, so "did not
              # advance in THIS poll" is the ordinary state of a perfectly healthy leg — it is not news.
              # Rendering it as STARTING put three legs on the 1:43 PM board in a not-running state whose
              # own reason read `WORKING — gpu_util=91.9999% and the host is still writing`, which is the
              # guard saying the opposite. So the idle guard's WORKING verdict counts as advancement here:
              # it is a direct observation that this box is doing work, and it is the same authority the
              # board already defers to for the cold-start floor and the setup grace.
              _working = bool(_b["advanced"] or _b.get("idle_working"))
              _state, _swhy = ifb.state_of(True, _working, _b["no_advance_polls"], _cold,
                                           why_not_running=_why or None, pre_first_commit=_pre_first,
                                           guard_shielding=bool(_b.get("idle_shielding")))
              # ★ WHY EXPLAINS ANY `—` CELL, NOT ONLY A NON-RUNNING STATE (trimcrae, 2026-07-29, 4:24 PM
              # ET: "it's missing an ETA"). `state_of` returns ("RUNNING", "") by design — a leg that is
              # working owes no excuse for its STATE — and the row was taking that empty string as its whole
              # WHY, discarding the sentence that explains an unknowable % or ETA. So a RUNNING leg with no
              # rate line in its log window rendered `—` with nothing beside it, which is the same
              # empty-column complaint the ETA itself drew earlier. An unknown cell must always say what is
              # missing; only a row with every cell known is allowed a blank WHY.
              # ★★ A HOST TORN DOWN ON THIS VERY PASS MUST NOT RENDER AS `RUNNING` (measured 2026-07-29,
              # 9:58 PM ET). `calib_lo_to_lo2__binary_vhl` — T2 binary, FORTY production iterations from
              # finishing — hit a capacity refusal on machine 55559, collect destroyed it, and the
              # TVAST-SUMMARY said so exactly as designed:
              #
              #   up=exited ... ▲ ADVANCING | ⛔ DESTROYED this pass (capacity refusal on machine 55559)
              #                               — billing STOPPED, $0 further
              #
              # ...while the BOARD, one block below, printed `T2 binary 98.6% 10:07 PM RUNNING`. Both were
              # reading the same pass. The board says RUNNING because `advanced` is true — the census DID
              # rise before the box died — so the freshest evidence about the leg (it has no host) lost to
              # the stalest (it was computing a minute ago). At 3 AM that row promises a result at 10:07 PM
              # from a machine that no longer exists, which is the same class of defect as an unreadable
              # instance list rendering as six deaths: the board stating something it does not know.
              #
              # `destroyed_this_pass` is keyed by instance id and is COMPLETE by the time the board is
              # built — the teardown loop has already run — so this is a lookup, not a re-derivation, and
              # the summary and the board now answer from ONE fact (CLAUDE.md §1).
              #
              # ⚠ THE TWO OUTCOMES ARE NOT THE SAME EVENT. A destroy that SUCCEEDED stopped the meter and
              # leaves an ordinary no-host leg for the next gate tick to re-place. A destroy that RAISED
              # left a dead box BILLING, which §6 is explicit the host cannot stop by itself — that is the
              # alarming case and it must not be softened into "no host".
              _destroyed = destroyed_this_pass.get(_b.get("iid"))
              if _destroyed and _destroyed.get("ok"):
                  # ⚠ A TEARDOWN BECAUSE THE UNIT FINISHED IS NOT A TEARDOWN THAT NEEDS REPLACING, and the
                  # first version of this branch said it was (2026-07-29, 10:38 PM ET). T2 binary reached
                  # production/2000, `reap_landed` correctly destroyed its host, and the row read "...the
                  # next gate tick re-places it" — inviting exactly the re-rental the ladder must not make,
                  # and telling a 3 AM reader a finished leg is still owed work. The reaper already
                  # distinguishes the two cases in the `why` it writes; the board must not flatten them.
                  _done_reason = "done" in str(_destroyed.get("why") or "").lower()
                  _next = ("nothing further is owed — this leg is FINISHED"
                           if _done_reason else "this pass dispatches the gate to re-place it")
                  if not _done_reason and _b.get("uid"):
                      _hostless_units.add(_b["uid"])
                  _state, _swhy = ifb.state_of(
                      False, False, 0, False,
                      why_not_running="host DESTROYED this pass (%s) — billing stopped, $0 further; "
                                      "checkpoint at %s/%s is intact in S3 and %s"
                                      % (_destroyed.get("why"), _b["phase"] or "none", _b["iteration"], _next))
                  _eta = None          # an ETA off a dead host's rate is a promise nothing can keep
              elif _destroyed:
                  _state, _swhy = ifb.STALLED, (
                      "⚠ DESTROY FAILED (%s) — this box is STILL BILLING and the host cannot stop its own "
                      "meter; only the control plane can" % _destroyed.get("why"))
                  _eta = None
              _cell_unknown = (_pct is None or _eta is None)
              # THE VERDICT IS VISIBLE WITH THE NUMBER THAT CAUSED IT, or it is a decision nobody can grade.
              # ⚠ IT MUST NOT RIDE `_why`'s SUPPRESSION. `why` is emitted only when `_cell_unknown` — i.e.
              # when % or ETA could not be computed — so appending there hid the delivered rate on exactly
              # the rows that HAVE one: a healthy RUNNING leg. Measured on the 5:29 PM ET board, where both
              # RUNNING rows rendered an empty `why` and the arrival cell vanished. It is composed into the
              # final string below instead, unconditionally.
              _acell = _at.cell(_arr) if _arr else "—"
              _wtxt = _swhy or (_why if _cell_unknown else "")
              if _acell and _acell != "—":
                  _wtxt = (_wtxt + " · " if _wtxt else "") + _acell
              _rows.append({"name": ifb.short_name(_b["uid"]), "pct": _pct, "eta_s": _eta,
                            "arrival": _arr,
                            "usd_per_ns": _usd_per_ns_cell(_b["gpu"], _b["dph"], _b.get("is_bid")),
                            "state": _state,
                            "why": _wtxt})
          except Exception as _e:  # noqa: BLE001
              _rows.append({"name": ifb.short_name(_b.get("uid")), "pct": None, "eta_s": None,
                            "usd_per_ns": None, "state": "UNKNOWN",
                            "why": "row could not be built: %s: %s" % (type(_e).__name__, _e)})
        # ── AND A ROW FOR EVERY UNIT THAT HAS NO HOST AT ALL ──────────────────────────────────────────
        # ★★ THE BOARD'S OWN DOCSTRING PROMISED THIS AND THE CODE DID NOT DO IT (2026-07-29, 2:45 PM ET).
        # `_board_rows` is built inside the loop over LIVE instances, so a unit whose host has died produces
        # no row at all — and `inflight_board.NO_HOST` was defined but never once emitted. Measured cost:
        # `calib_hi_to_lo2__binary_vhl` lost its host around 2:30 PM and was ABSENT from two consecutive
        # boards while its three siblings rendered normally. A leg with no host is the single most important
        # thing a progress board can say, and it was the one thing this one could not.
        #
        # The expectation set is the WATCH LIST's enabled entries — the repo's existing answer to "which
        # units are we supposed to be working on" — so a unit that is deliberately parked (`enabled: false`
        # + `_parked_why`, e.g. the 5a-KS legs) correctly does NOT appear as a missing row.
        try:
            import ternary_vast_watchdog as _tvw
            _expected = {e.get("unit_id") for e in _tvw.enabled_entries(_tvw.load_watch())}
            _hosted = {r["uid"] for r in _board_rows if r.get("uid")}
            for _uid in sorted(_expected - _hosted - set(done)):
                _ph, _it, _ = committed_progress(_uid, b, p)
                _tg = ifb.parse_targets("\n".join(phase_and_log(_uid, b, p, tail=60)[2]))
                # ⚠ A UNIT IS ONLY "MISSING" IF WE COULD SEE THE HOSTS THAT ARE THERE. When the instance
                # list did not read, EVERY enabled unit lands in this set — which is the 4:04 PM failure —
                # so the readability of that read decides which verdict this row is even allowed to carry.
                _st, _w = ifb.state_of(False, False, 0, False,
                                       host_list_readable=(_inst_unreadable is None),
                                       why_not_running=(
                                           "host state UNKNOWN — the Vast instance list did not read this "
                                           "pass (%s), so this is NOT a host death; checkpoint at %s/%s is "
                                           "intact in S3 and the next poll re-reads"
                                           % (_inst_unreadable, _ph or "none", _it)
                                           if _inst_unreadable else
                                           "no live host — checkpoint at %s/%s is intact in S3; "
                                           "this pass dispatches the gate to re-place it"
                                           % (_ph or "none", _it)))
                # ⚠ ONLY when the instance list READ. If it did not, every enabled unit lands in this set
                # and auto-replacement would rent a second host for legs that already have one — the 4:04 PM
                # failure turned into a spend. Unreadable means UNKNOWN, and UNKNOWN never buys.
                if _inst_unreadable is None:
                    _hostless_units.add(_uid)
                _rows.append({"name": ifb.short_name(_uid), "pct": ifb.pct_complete(_ph, _it, _tg),
                              "eta_s": None, "usd_per_ns": None, "state": _st, "why": _w})
        except Exception as _e:  # noqa: BLE001
            print(f"[board] could not add no-host rows: {type(_e).__name__}: {_e}")

        print()
        print("---- TVAST-BOARD ----")
        print(ifb.render(_rows), end="")
        print("---- END TVAST-BOARD ----")

        # ★★ THE SAME ROWS, ALSO AS STRUCTURED CELLS (2026-08-01). This lane was the only one that published
        # its board as TEXT ONLY: `merge_board` transcludes the rendered block verbatim, which is right for
        # the merged document — the block is the rows' one home and re-deriving it there could disagree with
        # it. But it left every OTHER consumer with a fixed-width table to parse, and the consumer that
        # matters is the one that reports to trimcrae. On 2026-08-01 that meant leg state was transcribed by
        # hand out of this block, and a hand-copied row is a row that survives on inertia: a leg reported
        # RUNNING at 98.9% had already landed, and the ETA quoted for it was 11 minutes in the past.
        #
        # ⚠ THIS IS ONE DERIVATION, TWO SERIALIZATIONS — NOT A SECOND HOME (CLAUDE.md §1). Both come from
        # `_rows`, in this call, so they cannot drift; the fragment is the same object the other three lanes
        # already publish. `write_fragment`, deliberately NOT `publish`: the merged board transcludes this
        # lane from `inflight-board.md`, which the WORKFLOW writes from the block above after this process
        # exits, so merging here would merge against the previous collect's text. The workflow re-merges
        # once it has written that file — that is the correct merge point and the only one.
        try:
            print(f"[board] fragment -> {ifb.write_fragment(ifb.TERNARY, _rows)}")
        except Exception as _e:  # noqa: BLE001
            print(f"[board] could not write the structured fragment: {type(_e).__name__}: {_e}")

        # ★★ DETECTION AND REPAIR IN THE SAME RUN (2026-07-30). Every no-host row above ends with "the next
        # gate tick re-places it" — and that sentence WAS the gap. `collect` is what notices a host died;
        # the gate is what buys a new one; they were different workflow runs, so the floor on recovery time
        # was one tick even when the board was healthy and the money was authorised. Measured that
        # lunchtime: the T3 ternary leg took two capacity refusals in a row and sat NO HOST for ~20 minutes
        # across three separate runs, and each repair attempt had to be hand-dispatched to be prompt.
        # Refusals are ROUTINE on Vast (§6: pick another host, never queue), so a recovery path that costs a
        # tick per refusal is a recovery path that does not work unattended — which is the whole point of it.
        #
        # So the pass that detects the gap NAMES it, in a file the workflow reads, and the workflow
        # self-dispatches the matching gate immediately. This does NOT decide to buy anything: the gate it
        # wakes still prices the board, still applies the rung ceiling and the $/ns buy line, and still
        # HOLDS if the market is bad. It only removes the waiting.
        # ★★ ESCALATE TO THE UNINTERRUPTIBLE TIER WHEN THE CHEAP ONE DEMONSTRABLY CANNOT HOLD THE LEG.
        # (2026-07-30.) Re-placing faster does not converge when mean host lifetime is below
        # time-to-first-commit: this leg went through FIVE bid-tier hosts in 2.5 hours and committed
        # nothing, every rental correctly priced and correctly re-placed. And no bid fixes it — an
        # on-demand renter preempts an interruptible one regardless of bid.
        # So the decision is made from EVIDENCE, per unit, and it is self-limiting in both directions:
        # the counter rises only when a unit is found hostless AGAIN, and `advanced` resets it to zero the
        # moment the census moves — so a leg that starts committing drops straight back to the cheap tier
        # and the ladder's pricing is untouched for everything that is working. The escalated rental is
        # still gated: it faces the same $0.006539/ns buy line, so this buys RELIABILITY, never an
        # exemption. (Measured the first time it ran: an on-demand RTX 5090 priced at 1.08x basis, below
        # the interruptible 4080S it replaced — the expensive TIER is not the expensive OFFER.)
        _ESCALATE_AFTER = int(os.environ.get("TVAST_ESCALATE_AFTER") or "3")
        _escalated = set()
        for _u in sorted(_hostless_units):
            _n = int((prev_state.get(f"replaced:{_u}") or 0)) + 1
            new_state[f"replaced:{_u}"] = _n
            if _n >= _ESCALATE_AFTER:
                _escalated.add(_mode_of_unit(_u))
                print(f"[replace] {_u} has now lost {_n} hosts without committing (>= {_ESCALATE_AFTER}) "
                      f"-> ESCALATING this re-placement to the uninterruptible tier; it still faces the "
                      f"buy line and drops back to the bid tier the moment the census advances")
        _needs = sorted({_mode_of_unit(_u) for _u in _hostless_units if _mode_of_unit(_u)})
        if _needs:
            print(f"[replace] {len(_hostless_units)} unit(s) have no host and are not done: "
                  f"{', '.join(sorted(_hostless_units))} -> gate mode(s) {', '.join(_needs)}")
            try:
                with open(os.environ.get("TVAST_REPLACE_FILE") or "/tmp/tvast-needs-replacement.txt",
                          "w") as _fh:
                    # "<mode> <on_demand 0|1>" — the workflow reads the second field.
                    _fh.write("\n".join(f"{m} {1 if m in _escalated else 0}" for m in _needs) + "\n")
            except Exception as _e:  # noqa: BLE001 — a readout must never break the monitoring pass
                print(f"[replace] could not write the marker: {type(_e).__name__}: {_e}")
        else:
            print("[replace] every enabled unit either has a host or is done — nothing to re-place")

        # ── AND THE OPPOSITE QUESTION: DID THIS PASS SEE A MODE'S *LAST* LEG LAND? ────────────────────
        # ★★ A MODE'S TERMINUS IS ITS REDUCTION, AND NOTHING WAS ARMING IT (2026-08-01). `collect` already
        # retires a landed leg's watch entry; it had no notion of the moment that actually matters, which is
        # the LAST leg landing. RUNG 5a-KS's S is a double difference over four legs — three landed legs are
        # worth nothing — and its four legs land ~20 h apart, the last of them overnight, so "somebody
        # dispatches 5aks-reduce when they notice" is not a mechanism.
        #
        # ⚠ COMPLETENESS IS COUNTED FROM `units_for`, NOT FROM THE WATCH LIST. The watch list is the right
        # source for "which units should have a host" and the WRONG one here, because `--reap-landed` sets a
        # landed unit `enabled=false` on this very pass — so by the time a mode is complete its enabled set
        # is EMPTY, and an all-of-an-empty-set test is vacuously true for every mode that never ran.
        #
        # The latch is a FINGERPRINT of the done set rather than a boolean, so the reduction re-fires when
        # its inputs change (a superseded leg re-landing, a seed added) and stays quiet when they do not.
        # It is written by the workflow AFTER a successful dispatch (`--latch-reduce-dispatched`), never
        # here: latching on intent rather than on delivery would swallow the one dispatch that failed.
        try:
            import hashlib as _hl
            _ready = []
            for _m in sorted(MODE_REDUCE_TASK):
                try:
                    _muids = [build_jobspec(_l, _s, _d, mode=_m).env["UNIT_ID"]
                              for (_l, _s, _d) in units_for(_m)]
                except Exception as _e:  # noqa: BLE001 — one unenumerable mode must not hide the others
                    print(f"[reduce] mode {_m}: cannot enumerate its units ({type(_e).__name__}: {_e}) — "
                          f"NOT reporting it complete, because an unreadable list is not an empty one")
                    continue
                if not _muids:
                    continue
                _short = [u for u in _muids if u not in done]
                if _short:
                    print(f"[reduce] {_m}: {len(_muids) - len(_short)}/{len(_muids)} legs landed — waiting "
                          f"on {', '.join(ifb.short_name(u) for u in sorted(_short))}")
                    continue
                _fp = _hl.sha256("\n".join(sorted(_muids)).encode()).hexdigest()[:16]
                _was = prev_state.get(f"reduce_dispatched:{_m}")
                if _was == _fp:
                    print(f"[reduce] {_m}: all {len(_muids)} legs landed and {MODE_REDUCE_TASK[_m]} was "
                          f"already dispatched for this exact set ({_fp}) — nothing to do")
                    continue
                print(f"[reduce] ✅ {_m}: ALL {len(_muids)} legs have landed -> dispatching "
                      f"{MODE_REDUCE_TASK[_m]} (set {_fp}, previously {_was or 'never'})")
                _ready.append((_m, MODE_REDUCE_TASK[_m], _fp))
            if _ready:
                with open(os.environ.get("TVAST_REDUCE_FILE") or "/tmp/tvast-mode-complete.txt",
                          "w") as _fh:
                    # "<mode> <task> <fingerprint>" — the workflow dispatches field 2 and latches field 3.
                    _fh.write("\n".join(f"{m} {t} {f}" for (m, t, f) in _ready) + "\n")
        except Exception as _e:  # noqa: BLE001 — arming a reduction must never break a monitoring pass
            print(f"[reduce] completeness not evaluated: {type(_e).__name__}: {_e}")
    except Exception as e:  # noqa: BLE001 — the board is a READOUT; it must never break a monitoring pass
        print(f"[board] not rendered: {type(e).__name__}: {e}")

    try:
        # ★★ WAVE-SCOPED, NOT CUMULATIVE (trimcrae, 2026-07-27: "only add someone back if you have a real
        # reason"). This used to be `sorted(prior | blocked)` — a union with every previous tick, so the
        # list only ever grew. The ONLY thing that adds to `blocked` is the `resources_unavailable` branch
        # above, i.e. the whole set is the PERISHABLE capacity class: "this machine's GPU was busy on this
        # tick", not a property of the host.
        #
        # Carrying that forward is what produced 33 lane-local + 41 shared exclusions and made our own
        # filter, not price, the binding constraint on placement — 2 of 2 authorised units failed with
        # `no rentable verified offer` against a 189-offer board at healthy prices. Clearing the shared set
        # without this would have regrown it from here within a day.
        #
        # Now a refusal excludes the machine for THIS wave and is forgotten next tick unless it refuses
        # again. Re-testing is nearly free: a failed submit costs no rental and no billing. Durable host
        # verdicts are a different path entirely — they go to the shared set via
        # `vast_machine_blacklist.publish`, which refuses the capacity class outright.
        prior = set(prev_state.get("_blocked_machines") or [])   # read for the readout only; NOT re-persisted
        new_state["_blocked_machines"] = sorted(blocked)
        # carry forward progress entries for units with no live instance, so the stall clock is not reset
        # by a preemption (which is exactly when you want to know how far it had got).
        for k, v in prev_state.items():
            new_state.setdefault(k, v)
        s3.put_object(Bucket=b, Key=f"{p}/_lane_state.json",
                      Body=json.dumps(new_state, indent=2).encode())
    except Exception as e:  # noqa: BLE001 — a monitoring aid must never fail a collect
        print(f"[collect] could not persist lane state: {e}")
    return len(mine), len(done)


def fetch_legs(dest, mode="edge", bucket=None, prefix=None, timestep_fs=None, warmup_timestep_fs=None):
    """Download this mode's engine leg JSONs into `dest` under the filenames the reducer expects.

    `ternary_fep_reduce._find_leg_files` globs `leg_<leg_id>_<direction>_r<seed>.json` under CKPT_DIR/INPUT_DIR,
    so the S3 objects (which live at `legs/<unit_id>/engine_leg.json`) have to be renamed back. Reconstructing
    the name from the unit's own parameters — rather than trusting whatever the object happened to be called —
    is what keeps a 4 fs leg from ever being reduced as if it were a 2 fs one.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    dt, wdt = resolve_timesteps(mode, timestep_fs, warmup_timestep_fs)
    os.makedirs(dest, exist_ok=True)
    s3 = _s3()
    got = {}
    for (leg, seed, direction) in units_for(mode):
        uid = unit_id(leg, seed, direction, dt, wdt, mode)
        name = f"leg_{leg}_{direction}_r{seed}.json"
        try:
            body = s3.get_object(Bucket=b, Key=f"{p}/legs/{uid}/engine_leg.json")["Body"].read()
        except Exception as e:  # noqa: BLE001
            print(f"[fetch-legs] MISSING {uid}: {type(e).__name__}")
            continue
        with open(os.path.join(dest, name), "wb") as fh:
            fh.write(body)
        d = json.loads(body.decode())
        got[leg] = d
        # ★ PRINT THE ATOM MAP NEXT TO THE ΔG. `protocol_hash` hashes the string "lomap_prefer_element_change"
        # and NOTHING about the MCS budget, so two legs whose maps differ — i.e. which ran DIFFERENT
        # alchemical transformations — share a hash and read as one protocol. The map size is the only field
        # that distinguishes them, and a reduction that does not show it invites a cycle to be formed across
        # legs that are not comparable. Legs written before the map was recorded print `?`, which is the
        # honest answer: unmeasured, not fine.
        _m = d.get("atom_map") or {}
        _map = ("%s heavy/%s expected @%ss budget" % (_m.get("n_heavy_mapped"), _m.get("expected_heavy_mapped"),
                                                      _m.get("lomap_time_s"))
                if _m else "n_mapped=%s, heavy/budget UNRECORDED" % d.get("n_mapped_atoms"))
        print(f"[fetch-legs] {name}: dG_morph={d.get('dg_morph_kcal')} +/- {d.get('mbar_se_kcal')} "
              f"(MBAR SE) protocol_hash={str(d.get('protocol_hash'))[:12]} atom_map[{_map}]")
    return got


def fetch_trajectories(dest, mode="edge", bucket=None, prefix=None, timestep_fs=None,
                       warmup_timestep_fs=None):
    """Download each unit's NEWEST committed MultiState generation into `dest` for convergence analysis.

    WHY THIS EXISTS. `fetch_legs` brings back the leg JSONs — one ΔG each — which is everything the reducer
    needs and nothing the *pose* diagnostics need. Those read the trajectory: `ternary_fep_convergence.py`
    computes the MBAR overlap matrix, replica mixing, dG(t) plateau and the contact-moiety pose RMSD from the
    committed `simulation.nc` / `checkpoint.nc`.

    THE QUESTION IT IS FOR. The 2 fs r0 cycle's BINARY leg has a confirmed pose failure — its
    receptor-contacting moiety leaves and does not return in 8 of 12 replicas, while the ternary leg in the same
    cycle is 12/12 stable (audit §L.3–L.3c). RUNG 2b's 4 fs cycle agrees with it to |Δ| = 0.0215 kcal/mol. If 2b's
    binary leg carries the SAME departure, that agreement is a genuine timestep reproduction on a shared-broken-arm
    basis. If 2b's binary leg holds its pose, then a contaminated arm and a clean one agree to 0.02 kcal/mol, and
    the claim that the departure invalidates ΔG_binary needs substantial softening. Either way it is decided by
    looking, and looking needs the trajectories — hence this.

    LAYOUT-AGNOSTIC ON PURPOSE. It lists everything under `commits/<uid>/` and finds the `simulation.nc` keys
    rather than constructing a path. A guessed prefix that misses returns "no commits", which is indistinguishable
    from "the trajectory is gone" — the GCP lane's converge step learned that the expensive way, and the same
    reasoning applies here.

    Directories are named `<leg_id>_sim_shared` because `ternary_fep_convergence._find_nc_files` keys each leg by
    its parent directory name minus that suffix, so the report comes out tagged by leg rather than by unit id.
    """
    b = bucket or DEFAULT_BUCKET
    p = (prefix or RESULT_PREFIX).rstrip("/")
    dt, wdt = resolve_timesteps(mode, timestep_fs, warmup_timestep_fs)
    os.makedirs(dest, exist_ok=True)
    s3 = _s3()
    out = {}
    for (leg, seed, direction) in units_for(mode):
        uid = unit_id(leg, seed, direction, dt, wdt, mode)
        root = f"{p}/commits/{uid}/"
        keys = []
        token = None
        while True:
            kw = {"Bucket": b, "Prefix": root}
            if token:
                kw["ContinuationToken"] = token
            try:
                page = s3.list_objects_v2(**kw)
            except Exception as e:  # noqa: BLE001
                print(f"[fetch-traj] LIST FAILED {uid}: {type(e).__name__}: {e}")
                break
            keys.extend(o["Key"] for o in page.get("Contents", []) or [])
            if not page.get("IsTruncated"):
                break
            token = page.get("NextContinuationToken")
        ncs = [k for k in keys if k.endswith("/simulation.nc")]
        if not ncs:
            print(f"[fetch-traj] NO simulation.nc under s3://{b}/{root} — nothing to analyse for {leg}")
            out[leg] = None
            continue

        def _iter_of(key):
            m = re.search(r"iter-(\d+)", key)
            return int(m.group(1)) if m else -1

        # PRODUCTION generations only, and the newest of them. A warmup generation would be analysed as if it
        # were production and reported without complaint — the phase is part of the identity, not a detail.
        prod = [k for k in ncs if "/production/" in k]
        pick_from = prod or ncs
        if not prod:
            print(f"[fetch-traj] WARNING {leg}: no /production/ generation; falling back to the newest of ANY "
                  f"phase, which may be WARMUP — read the report's iterations_compared before trusting it")
        newest = max(pick_from, key=_iter_of)
        gen = newest.rsplit("/", 1)[0]
        dstdir = os.path.join(dest, f"{leg}_sim_shared")
        os.makedirs(dstdir, exist_ok=True)
        pulled = []
        for k in keys:
            if not k.startswith(gen + "/"):
                continue
            name = k.rsplit("/", 1)[-1]
            if not (name.endswith(".nc") or name.endswith(".chk") or name.endswith(".json")):
                continue
            try:
                s3.download_file(b, k, os.path.join(dstdir, name))
                pulled.append(name)
            except Exception as e:  # noqa: BLE001
                print(f"[fetch-traj] download failed {k}: {type(e).__name__}")
        out[leg] = {"unit_id": uid, "generation": f"s3://{b}/{gen}", "iteration": _iter_of(newest),
                    "files": sorted(pulled), "phase": ("production" if prod else "UNKNOWN/warmup")}
        print(f"[fetch-traj] {leg}: iter {_iter_of(newest)} ({out[leg]['phase']}) -> {dstdir} {sorted(pulled)}")
        # POSITIONS live in the checkpoint, not in simulation.nc. Without it the pose/ligand-escape diagnostic is
        # unavailable by construction, so say which case we are in rather than letting the report look complete.
        if not any("checkpoint" in f.lower() for f in pulled):
            print(f"[fetch-traj] {leg}: NO checkpoint file in this generation — the pose / contact-moiety "
                  f"diagnostic will be UNAVAILABLE for this leg (positions are stored separately from "
                  f"simulation.nc), which is not the same as it passing")
    return out


def ddg_coop_identity(legs):
    """ΔΔG_coop from the legs in hand, by the identity the engine defines. PURE.

    `nr4a3_ternary_fep`'s own docstring: ΔΔG_coop = ΔΔG_alch,ternary − ΔΔG_alch,binary
    = (ternary − solvent) − (binary − solvent) = **ternary − binary**. The solvent leg cancels EXACTLY, so it
    is not needed for this number and its absence is not a gap. It is still run and reported, because each
    environment's ΔΔG is only a relative *binding* free energy with it.

    Computed here as well as by `ternary_fep_reduce` deliberately. The reducer's gating machinery had seven
    defects found in one day, every one of them reporting success while measuring nothing; a two-term
    subtraction that can be checked by eye is the right cross-check for a number this load-bearing.
    """
    tern = next((v for k, v in legs.items() if "__ternary" in k), None)
    bina = next((v for k, v in legs.items() if "__binary" in k), None)
    solv = next((v for k, v in legs.items() if k.endswith("__solvent")), None)
    if not tern or not bina:
        return {"ddg_coop_kcal": None,
                "reason": "need both a ternary and a binary leg; solvent cancels and is optional"}
    t, bn = tern.get("dg_morph_kcal"), bina.get("dg_morph_kcal")
    if t is None or bn is None:
        return {"ddg_coop_kcal": None, "reason": "a leg has no dg_morph_kcal"}
    ddg = float(t) - float(bn)
    big = max(abs(float(t)), abs(float(bn)))
    hashes = {k: v.get("protocol_hash") for k, v in legs.items()}
    return {
        "ddg_coop_kcal": ddg,
        "dg_ternary_kcal": float(t), "dg_binary_kcal": float(bn),
        "dg_solvent_kcal": (float(solv["dg_morph_kcal"]) if solv and solv.get("dg_morph_kcal") is not None
                            else None),
        # How much of each leg survives the subtraction. r0's was 0.0111 — the answer was 1.1 % of the
        # numbers being subtracted, which is why its systematic miss was ~33x its statistical error.
        "cancellation_ratio": (abs(ddg) / big) if big else None,
        "protocol_hashes": hashes,
        "protocol_hashes_consistent": len(set(v for v in hashes.values() if v)) <= 1,
    }


def stage_cache_key(leg_id, mode, seed=0, bucket=None, prefix=None):
    """The S3 URI of one leg's stage cache, DERIVED from the same expression build_jobspec uses. PURE-ish.

    ⚠ THIS FUNCTION IS WHY THE SEEDER CANNOT DRIFT FROM THE CONSUMER. Pre-seeding writes a tar to a key
    that the on-host pipeline must then find; a hand-copied key that differs by one character produces a
    silent cache MISS, which for a `stage_required` mode is a failed leg and for any other mode is a
    wrong-inputs leg that runs to completion. The key is built by calling `build_jobspec` and reading the
    env it produced, so there is exactly one expression for it in the repo.
    """
    spec = build_jobspec(leg_id, seed=seed, mode=mode, bucket=bucket, prefix=prefix)
    return spec.env["STAGE_CACHE"]


def seed_stage_cache(staged_dir, mode="5aks", seed=None, bucket=None, prefix=None, dry_run=False):
    """Upload CI-staged leg inputs (`<staged_dir>/<leg_id>/{complex.pdb,ligands.sdf,...}`) into this lane's
    stage cache, in the `tar -C $IN -cf stage.tar <LEG_ID>` shape the on-host extractor expects.

    Refuses to upload a leg whose directory is missing either file the engine mounts: a tar carrying a
    complex and no ligands would be a cache HIT that skips staging and then dies inside the engine, which
    is strictly worse than a miss.

    ★ `seed=None` (the default, and what both prime jobs pass) seeds EVERY seed the mode declares, not just
    seed 0. This changed on 2026-07-30 when `5aks` went to n = 2 seeds per arm: the stage-cache key is
    seed-scoped, so a seed-1 leg would have MISSED — and `5aks` sets `stage_required: True`, making a miss a
    hard failure on a rented host rather than a silent fall-through. The staged directory is keyed by LEG ID
    and carries no seed, which is correct here: 5a-KS is one co-fold per species by design, so every seed of
    a leg starts from the same structure and differs only in its sampler seed. Pass an explicit `seed` only
    to re-seed one.
    """
    import subprocess
    import tempfile
    out = []
    want = {sd for (_l, sd, _d) in units_for(mode)} if seed is None else {seed}
    for (leg_id, sd, _dir) in units_for(mode):
        if sd not in want:
            continue
        src = os.path.join(staged_dir, leg_id)
        need = [f for f in ("complex.pdb", "ligands.sdf") if not os.path.isfile(os.path.join(src, f))]
        if need:
            raise SystemExit(f"[seed-stage] {leg_id}: staged dir {src} is missing {need} — refusing to seed a "
                             f"cache that would HIT and then fail inside the engine")
        # ★ THE KEY IS PER-SEED, so it must use THIS unit's seed (`sd`), not the caller's filter. Passing
        # `seed=seed` here was correct only while `seed` was a single value; with `seed=None` meaning "every
        # declared seed" it would have written every leg to the seed-None key and left BOTH real seeds
        # missing — a silent cache miss that `stage_required` turns into a dead rented host.
        uri = stage_cache_key(leg_id, mode, seed=sd, bucket=bucket, prefix=prefix)
        tar = os.path.join(tempfile.mkdtemp(), "stage.tar")
        subprocess.run(["tar", "-C", staged_dir, "-cf", tar, leg_id], check=True)
        size = os.path.getsize(tar)
        print(f"[seed-stage] {leg_id} r{sd}: {size} B -> {uri}")
        if not dry_run:
            b, k = _split_uri(uri)
            _s3().upload_file(tar, b, k)
        out.append({"leg_id": leg_id, "seed": sd, "uri": uri, "bytes": size, "uploaded": not dry_run})
    if not out:
        raise SystemExit(f"[seed-stage] mode {mode!r} has no leg at seed {seed} — nothing to seed")
    return out


def _known_unit_ids():
    """Every unit id this module can currently launch — used to pair a live label with a unit before that
    unit has written any record. Without it a freshly launched host has no progress line at all, which is
    the exact window (setup / pre-equil) where a stall is most likely and least visible."""
    out = []
    for mode in MODES:
        for (l, s, d) in units_for(mode):
            for dt in (DEFAULT_TIMESTEP_FS, "2.0", "3.0"):
                out.append(unit_id(l, s, d, dt, DEFAULT_WARMUP_TIMESTEP_FS, mode))
    return out


def stop_all():
    """Destroy every instance of this lane (anti-idle backstop).

    ★ AND RECORD WHAT EACH ONE COST FIRST (2026-08-01). `task=stop` is the path taken when something has
    gone wrong enough that the whole lane is being torn down — i.e. precisely the rentals whose cost someone
    will want afterwards — and it was the last DELETE in this file with no ledger row. Recorded BEFORE the
    DELETE, because after it the rate, `start_date` and machine are unrecoverable."""
    key = os.environ["VAST_API_KEY"]
    n = 0
    for i in _vast_request("GET", "/instances/", key).get("instances", []):
        if (i.get("label") or "").startswith(LABEL_PREFIX):
            print(f"destroying {i.get('id')} ({i.get('label')})")
            try:
                _tbl.record(i, unit_id=i.get("label"), reason="stop_all")
            except Exception as e:  # noqa: BLE001 — the ledger must never block a teardown
                print(f"  [ledger] could not record {i.get('id')}: {type(e).__name__}: {e}")
            try:
                _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
                n += 1
            except Exception as e:  # noqa: BLE001
                print(f"  failed: {e}")
    print(f"destroyed {n}")
    return n


def retire_host(match, dry_run=False):
    """Destroy the host of every unit whose id contains `match`, LEAVING the checkpoint. Returns the list.

    ★★ WHY A LANE NEEDS THIS, AND WHY IT IS NOT `--stop` (trimcrae, 2026-07-29, 2:30 PM ET: *"can we get T2
    ternary on a faster chip … or at least subvert the ranking to filter on only faster chips"*).

    THE MEASURED CASE. `calib_lo_to_lo2__ternary_vhl` was delivering **34.5 s/iter** against the **16.0
    s/iter** median MEASURED on a Vast RTX 4090 for this exact 146,284-particle assembly — 2.2x slower than
    its own card class, and ~3x slower than the 5090-class hosts on the same lane (9.2-12.6 s/iter). Its ETA
    was 25 h against 11-15 h for its three siblings, so it alone set when the closure residual R could be
    computed.

    ⚠ AND THE BOARD COULD NOT SEE IT, which is the part worth remembering. `$/ns` is derived from each card's
    TABLE throughput, not from what the host actually delivers, so that leg rendered `$0.00533/ns · 1.56x` —
    comfortably under the buy line — while its REALISED rate was ~2.2x that, around 3.4x basis and well over
    the line. Retiring it is therefore not an override of the price gate; it is the gate's own intent, applied
    with a number the gate does not have. (Same family as `vast_rate_forensics`' complaint that a launcher's
    `dph≈` line reads low against what the instance is billed.)

    ⚠ NOT `--stop`. That destroys every instance this lane holds, which here would have thrown away three
    healthy legs at 9-32 % to fix one. The selector is the unit id, and `submit`'s ordinary path re-places it.

    ⚠ AND IT DESTROYS A HOST, NEVER A RESULT. The commit store is in S3 and survives; the next rental resumes
    from the same checkpoint, so the cost of retiring is one image pull, not the work done so far. It refuses
    to touch a unit whose leg record is already `done`.
    """
    key = os.environ["VAST_API_KEY"]
    done = {u for u, d in (leg_records() or {}).items() if (d or {}).get("status") == "done"}
    out = []
    for i in _vast_request("GET", "/instances/", key).get("instances", []) or []:
        lab = str(i.get("label") or "")
        if not lab.startswith(LABEL_PREFIX):
            continue
        uid = next((u for u in _known_unit_ids() if label_matches_unit(lab, u)), None)
        if not uid or match not in uid:
            continue
        if uid in done:
            print(f"  skipping {uid}: leg record is status=done — a RESULT is never retired")
            continue
        row = {"unit_id": uid, "instance": i.get("id"), "machine_id": i.get("machine_id"),
               "gpu": i.get("gpu_name"), "dph_total": i.get("dph_total")}
        # ★★ READ THE CHECKPOINT BEFORE DESTROYING THE HOST, AND REFUSE ON AN UNREADABLE STORE
        #    (2026-07-31). This function's own docstring promises "it DESTROYS A HOST, NEVER A RESULT" and
        #    "the commit store is in S3 and survives" — but it never LOOKED. It asserted the property it was
        #    relying on. CLAUDE.md §4: an absent reading is not a reading of absence.
        #
        # The rule is deliberately asymmetric, because the two unknowns are not symmetric:
        #   * NOTHING COMMITTED is a fine reason to retire — a cold host has banked no work, so retiring it
        #     loses nothing. Refusing there would strand exactly the hosts most worth replacing.
        #   * AN UNREADABLE STORE is a refusal. We cannot then distinguish "no work banked" from "work
        #     banked and we cannot see it", and destroying on that is destroying blind.
        try:
            _ph, _it, _sc = committed_progress(uid)
            row.update({"committed_phase": _ph, "committed_iteration": _it, "commit_store_read": True})
            print(f"  checkpoint for {uid}: {_ph or 'none'}/{_it} (scalar {_sc}) — VERIFIED in S3 before "
                  f"touching the host")
        except Exception as e:  # noqa: BLE001
            row.update({"commit_store_read": False, "commit_store_error": f"{type(e).__name__}: {e}"})
            print(f"  ⛔ REFUSING to retire {uid}: the commit store is UNREADABLE ({type(e).__name__}: {e}). "
                  f"That is not evidence the checkpoint is absent, and destroying on it would be destroying "
                  f"blind. Fix the read, then retry.")
            out.append(row)
            continue
        if dry_run:
            print(f"  WOULD retire {row}")
        else:
            try:
                try:
                    _tbl.record(i, unit_id=uid, reason="retire_host")
                except Exception as _e:  # noqa: BLE001 — never block a retirement on bookkeeping
                    print(f"  [ledger] could not record rental {i.get('id')}: {type(_e).__name__}: {_e}")
                _vast_request("DELETE", f"/instances/{i.get('id')}/", key)
                print(f"  RETIRED host {i.get('id')} (machine {i.get('machine_id')}, {i.get('gpu_name')}) "
                      f"for {uid} — checkpoint intact; the next `collect` finds it hostless and dispatches "
                      f"the gate itself")
            except Exception as e:  # noqa: BLE001
                print(f"  failed to retire {i.get('id')}: {e}")
                continue
        out.append(row)
    if not out:
        print(f"  no live host matched {match!r} — nothing retired")
    return out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Ternary cooperativity FEP on Vast.ai (RUNG 2b lane)")
    ap.add_argument("--retire-host", metavar="SUBSTRING",
                    help="destroy the HOST of every unit whose id contains SUBSTRING, leaving the checkpoint "
                         "so the next `collect` detects it hostless and dispatches the gate. For a host "
                         "measurably underperforming its own "
                         "card class — see `retire_host` for the case that motivated it.")
    ap.add_argument("--mode", choices=sorted(MODES), default=os.environ.get("TVAST_MODE") or "probe")
    ap.add_argument("--timestep-fs", default=None)
    ap.add_argument("--warmup-timestep-fs", default=None)
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--stop", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fetch-legs", metavar="DIR",
                    help="download this mode's engine leg JSONs into DIR under the reducer's filenames, "
                         "then print the ΔΔG_coop identity as a cross-check")
    # ★ RELAUNCH ONE ARM OF A PAIR. Without this, recovering a single preempted leg means dispatching the
    # whole mode, which also re-rents its sibling. That is exactly wrong when the sibling has a KNOWN,
    # DETERMINISTIC defect: on 2026-07-26 NR4A3 was preempted (routine, resumes) while NR4A1 had aborted on
    # endpoint verification for a reason that would reproduce identically — so a whole-mode relaunch would
    # have bought a second NR4A1 rental that ran the full 0.5 ns pre-equilibration and failed the same way.
    ap.add_argument("--supersede-failed", metavar="SUBSTRING",
                    help="archive-and-clear the status=failed leg.json of every unit whose id contains "
                         "SUBSTRING, after its cause is fixed and it has been relaunched. A stale FAILED both "
                         "masks a real failure of the new attempt and blocks the watchdog's own recovery.")
    ap.add_argument("--only", metavar="SUBSTRING",
                    help="restrict this launch to units whose LEG ID contains SUBSTRING (e.g. `nr4a3`), so a "
                         "single preempted arm can be recovered without re-renting its sibling")
    # `--only` filters by LEG id, which cannot separate two replicates of the SAME leg — and `edge_reps`
    # carries exactly that: ternary at seed 1 and ternary at seed 2. Without a seed filter, recovering one
    # of them means re-dispatching the mode and (harmlessly but pointlessly) re-listing all four.
    ap.add_argument("--only-seed", metavar="N", type=int, default=None,
                    help="restrict this launch to units at SEED N; combines with --only")
    # The gate is a SEPARATE, VISIBLE step rather than something buried inside submit(), for the reason the
    # rule itself names: a silent hold is indistinguishable from a finished fleet. It prints the snapshot and
    # writes it to a file CI commits, so a reader at 3 AM gets the projected cost, the ceiling, the board
    # depth and the offers that were priced — not "nothing to submit".
    ap.add_argument("--market-gate", metavar="N", type=int, default=None,
                    help="price N units against this rung's own ladder ceiling and exit 1 to HOLD")
    # ★ PREFER THIS OVER `--market-gate N` IN ANY AUTOMATED CALLER. `N` is a number someone typed once; this
    # derives it from the units that actually still need a host, so a satisfied lane cannot keep clearing the
    # gate and dispatching launches that rent nothing (2026-07-27 — it did exactly that three times).
    # Exit codes: 0 = CLEAR (dispatch), 1 = HOLD (do not dispatch), 3 = NOTHING TO LAUNCH (do not dispatch,
    # and it is not a hold — the market was never asked).
    ap.add_argument("--gate-for-mode", action="store_true",
                    help="price ONLY this mode's units that still need a host; exit 3 when none do")
    ap.add_argument("--gate-out", metavar="FILE", default=None,
                    help="write the market-gate readout here (committed by CI so a hold is never silent)")
    ap.add_argument("--seed-stage-cache", metavar="DIR",
                    help="upload CI-staged leg inputs from DIR/<leg_id>/ into this mode's stage cache, so a "
                         "leg whose inputs cannot be built on the host (a Boltz co-fold) finds them there")
    ap.add_argument("--fetch-trajectories", metavar="DIR",
                    help="download each unit's NEWEST committed production generation (.nc/.chk) into DIR as "
                         "<leg>_sim_shared/, ready for ternary_fep_convergence.py")
    # Printed on stdout as a BARE MODE NAME so the workflow can do MODE=$(... --converge-mode-for-task "$T").
    # It exists so the converge job's `--mode` is derived from the dispatched task instead of hardcoded: the
    # hardcoded `edge` meant the diagnostic could only ever see RUNG 2b's legs. See CONVERGE_TASK_MODES.
    ap.add_argument("--converge-mode-for-task", metavar="TASK",
                    help="print the MODES key whose units `task=<TASK>` must analyse, then exit. Errors "
                         "(non-zero) on an unregistered task rather than guessing — guessing here yields an "
                         "empty directory and a green run.")
    # Printed as a BARE TASK NAME so `collect`'s self-heal can do TASK=$(... --gate-task-for "$mode"), which
    # is what replaced the hardcoded shell `case` that stranded the 5a-KS leg on 2026-07-31. Exit 0 with a
    # task on stdout = dispatch it; exit 3 with the reason on stderr = this mode has no re-placement BY
    # DECISION; any other non-zero = the mode is unknown to the map, which is the trap and must be loud.
    ap.add_argument("--gate-task-for", metavar="MODE",
                    help="print the task= that re-places a dead host for MODE, then exit")
    # The card floor that mode's re-placement should carry, printed separately so the shell can pass it
    # through verbatim. It is DERIVED from `MODE_MIN_NS_PER_H` rather than typed into a `gh workflow run`
    # line — a floor typed in shell is how a floor reverted on one dispatcher kept running on the other.
    ap.add_argument("--min-ns-per-h-for", metavar="MODE",
                    help="print the min_ns_per_h a re-placement of MODE should carry (0 = none), then exit")
    # Every mode that HAS a re-placement, space-separated. Exists so a shell loop (the mode-wide forensic in
    # `reps-diag`) iterates the SAME map that decides re-placement, instead of a second list that goes stale —
    # which is precisely how the 5a-KS leg was stranded and then how its wedge went unexamined.
    ap.add_argument("--replaceable-modes", action="store_true",
                    help="print every mode with a re-placement gate, space-separated, then exit")
    # Same contract as `--gate-task-for`, for the OTHER end of a mode's life: 0 = a reduce task on stdout,
    # 3 = this mode has no reduction BY DECISION, anything else = the mode is unknown to both maps.
    ap.add_argument("--reduce-task-for", metavar="MODE",
                    help="print the task= that reduces MODE once all its legs land, then exit")
    # Written only AFTER the dispatch succeeded, so a dispatch that never reached GitHub is retried on the
    # next tick instead of being silently marked done. MODE:FINGERPRINT, exactly as `collect` emitted it.
    ap.add_argument("--latch-reduce-dispatched", metavar="MODE:FINGERPRINT",
                    help="record in the lane state that MODE's reduction was dispatched for that done-set")
    # `1` when the gate snapshot named the UNINTERRUPTIBLE tier, else `0`. The gate's self-dispatch reads it
    # so the launch buys the tier the gate priced and cleared; forwarding the operator input instead would let
    # a gate that cleared on-demand dispatch a bid launch, i.e. price one market and buy another.
    # Fails CLOSED to `0`: an unreadable snapshot must not silently buy the dearer tier.
    ap.add_argument("--gate-chose-on-demand", metavar="HOLD_JSON",
                    help="print 1 if that gate snapshot chose the on-demand tier, else 0, then exit")
    a = ap.parse_args(argv)
    if a.gate_chose_on_demand:
        try:
            with open(a.gate_chose_on_demand) as _fh:
                _d = json.load(_fh)
            print("1" if (_d.get("chosen_tier") == TIER_ONDEMAND and not _d.get("hold")) else "0")
        except Exception:  # noqa: BLE001 — fail closed, and say nothing more than the answer
            print("0")
        return 0
    if a.replaceable_modes:
        print(" ".join(sorted(MODE_GATE_TASK)))
        return 0
    if a.reduce_task_for:
        try:
            rtask = reduce_task_for(a.reduce_task_for)
        except KeyError as e:
            print(str(e), file=sys.stderr)
            return 1
        if rtask is None:
            print(f"{a.reduce_task_for}: no automatic reduction BY DECISION — "
                  f"{NO_AUTOMATIC_REDUCTION[a.reduce_task_for]}", file=sys.stderr)
            return 3
        print(rtask)
        return 0
    if a.latch_reduce_dispatched:
        _m, _, _fp = a.latch_reduce_dispatched.partition(":")
        if not _m or not _fp:
            print("--latch-reduce-dispatched wants MODE:FINGERPRINT", file=sys.stderr)
            return 1
        _b = DEFAULT_BUCKET
        _p = RESULT_PREFIX.rstrip("/")
        _s3c = _s3()
        try:
            _st = json.loads(_s3c.get_object(Bucket=_b, Key=f"{_p}/_lane_state.json")["Body"].read())
        except Exception:  # noqa: BLE001 — no state yet is the normal first-run case
            _st = {}
        _st[f"reduce_dispatched:{_m}"] = _fp
        _s3c.put_object(Bucket=_b, Key=f"{_p}/_lane_state.json",
                        Body=json.dumps(_st, indent=2).encode())
        print(f"[reduce] latched reduce_dispatched:{_m} = {_fp}")
        return 0
    if a.min_ns_per_h_for:
        v = mode_min_ns_per_h(a.min_ns_per_h_for)
        print("%g" % v)
        return 0
    if a.gate_task_for:
        try:
            task = gate_task_for(a.gate_task_for)
        except KeyError as e:
            print(str(e), file=sys.stderr)
            return 1
        if task is None:
            print(f"{a.gate_task_for}: no automatic re-placement BY DECISION — "
                  f"{NO_AUTOMATIC_REPLACEMENT[a.gate_task_for]}", file=sys.stderr)
            return 3
        print(task)
        return 0
    if a.converge_mode_for_task:
        print(converge_mode_for_task(a.converge_mode_for_task))
        return 0
    if a.gate_for_mode:
        action, readout = gate_for_mode(a.mode, excluded=blocked_machine_ids())
        print(json.dumps(readout, indent=2))
        if a.gate_out:
            with open(a.gate_out, "w") as fh:
                json.dump(readout, fh, indent=2)
                fh.write("\n")
        mark = {"clear": "✅ CLEAR", "hold": "⛔ HOLD", "nothing-to-launch": "⏭ NOTHING TO LAUNCH",
                "blocked": "⛔ BLOCKED ON REPEATED FAILURE"}[action]
        print("[market-gate] %s — %s" % (mark, readout["reason"]))
        # 4, not 3 and not 1. A blocked lane must be distinguishable from a finished one (3) AND from a
        # price hold (1) by the caller, because all three want different ledger words and only the price hold
        # runs the hold clock.
        return {"clear": 0, "hold": 1, "nothing-to-launch": 3, "blocked": 4}[action]
    if a.market_gate is not None:
        hold, readout = market_gate(a.market_gate, excluded=blocked_machine_ids())
        print(json.dumps(readout, indent=2))
        if a.gate_out:
            with open(a.gate_out, "w") as fh:
                json.dump(readout, fh, indent=2)
                fh.write("\n")
        print("[market-gate] %s — %s" % ("⛔ HOLD" if hold else "✅ CLEAR", readout["reason"]))
        return 1 if hold else 0
    if a.supersede_failed:
        print(json.dumps(supersede_failed_record(a.supersede_failed, dry_run=a.dry_run), indent=1))
    elif a.seed_stage_cache:
        print(json.dumps(seed_stage_cache(a.seed_stage_cache, mode=a.mode, dry_run=a.dry_run), indent=2))
    elif a.fetch_trajectories:
        got = fetch_trajectories(a.fetch_trajectories, mode=a.mode, timestep_fs=a.timestep_fs,
                                 warmup_timestep_fs=a.warmup_timestep_fs)
        print(json.dumps(got, indent=2))
        # A leg with no trajectory is a REAL gap in the analysis, not a quiet skip: the pose diagnostic that
        # motivated this cannot be run for it, and the cycle's verdict would silently rest on fewer legs.
        missing = [k for k, v in got.items() if not v]
        if missing:
            print("::warning title=TVAST CONVERGE INCOMPLETE::no committed trajectory for %s — the convergence "
                  "and pose diagnostics cannot cover %s of %d legs"
                  % (",".join(missing), len(missing), len(got)))
        # ★★ ALL of them missing is a DIFFERENT failure from some of them missing, and it must be RED.
        # A warning is the right weight for a partial fetch; it is the wrong weight for a fetch that got
        # nothing, because the steps after this one then run happily over an empty directory and print a
        # convergence summary covering zero legs. That is precisely how `--mode edge` pointed at the 2 fs
        # triangle would have looked: green, fast, and measuring nothing. The mode/timestep mismatch is
        # named in the message because it is the overwhelmingly likely cause — the prefix is keyed on both.
        if got and not any(got.values()):
            print("::error title=TVAST CONVERGE MEASURED NOTHING::mode=%s (dt=%s) matched a committed "
                  "trajectory for 0 of %d legs. Every unit id is keyed on BOTH the timestep and the mode, so "
                  "the usual cause is analysing one mode's legs under another's id. Nothing was analysed."
                  % (a.mode, resolve_timesteps(a.mode, a.timestep_fs, a.warmup_timestep_fs)[0], len(got)))
            return 1
    elif a.fetch_legs:
        legs = fetch_legs(a.fetch_legs, mode=a.mode, timestep_fs=a.timestep_fs,
                          warmup_timestep_fs=a.warmup_timestep_fs)
        print(json.dumps(ddg_coop_identity(legs), indent=2))
    elif a.retire_host:
        print(json.dumps(retire_host(a.retire_host, dry_run=a.dry_run), indent=1))
    elif a.stop:
        stop_all()
    elif a.collect:
        collect()
    else:
        legs = None
        if a.only or a.only_seed is not None:
            legs = [u for u in units_for(a.mode)
                    if (not a.only or a.only in u[0]) and (a.only_seed is None or u[1] == a.only_seed)]
            if not legs:
                raise SystemExit(f"--only {a.only!r} --only-seed {a.only_seed!r} matched no unit in mode "
                                 f"{a.mode!r}; available: {units_for(a.mode)}")
            print(f"[launch] --only {a.only!r} --only-seed {a.only_seed!r} -> {legs}")
        got = submit(mode=a.mode, dry_run=a.dry_run, timestep_fs=a.timestep_fs,
                     warmup_timestep_fs=a.warmup_timestep_fs, legs=legs)
        # ★ RENTING NOTHING IS A FAILURE, NOT A QUIET SUCCESS (2026-07-27). `submit` catches per-unit submit
        # errors so one unrentable unit cannot abort the rest — correct — but the whole launch then exited 0
        # with an empty handle list, which is indistinguishable in CI from a launch that worked. Now that the
        # per-offer buy line can legitimately refuse EVERY offer on a thin board, that ambiguity would turn
        # the price guard itself into a silent no-op. A launch that wanted units and got none is red.
        if getattr(submit, "last_requested", 0) and not got:
            # ★★ TWO OUTCOMES, TWO SIGNALS (2026-07-27, after one red run meant both on the same morning).
            # An "either X or Y" error message trains everyone to ignore the alert, which is precisely how
            # the 9:13 AM miss went unnoticed for an hour. The launcher knows which it was, so it says so.
            kind = getattr(submit, "last_failure_kind", None)
            if kind == "market":
                # The guard WORKING. Green, like the market_gate job's hold — a correct refusal is a normal
                # state of this lane, and a recurring red build is the most persistent kind of noise there
                # is. The ledger row and this warning are what make it visible instead of silent.
                print("::warning title=TVAST HELD ON PRICE::correctly refused — no offer on the board was "
                      "within the buy line ($%.6f/ns = %.2fx the ladder basis). Nothing was rented and "
                      "nothing is billing. This is the price guard doing its job; the next tick re-checks."
                      % (buy_ceiling_usd_per_ns(), MARKET_MAX_RATIO_VS_BASIS))
                return 0
            if kind == "capacity":
                # ★★ THE THIRD SIGNAL, AND IT EXISTS BECAUSE NEITHER OF THE OTHER TWO WAS TRUE ON
                # 2026-07-29. Green, like the price hold — a `resources_unavailable` is CLAUDE.md §6's
                # routine case and reddening the lane for it is the noise that makes real alerts ignorable —
                # but it must NOT borrow the price hold's sentence. Every board read that morning was
                # 1.04x-1.34x basis, so "no offer was within the buy line" would have sent a reader to
                # re-examine a market that was doing nothing wrong. The trend that makes this countable is
                # `capacity_refusal_trend`, written by the launcher above; it is a readout and never a gate.
                print("::warning title=TVAST NO CAPACITY::the launcher wanted %d unit(s), rented none, and "
                      "every host it did rent answered `resources_unavailable` on start and was destroyed "
                      "($0 billing). This is NOT a price hold — the board was read and priced fine — and "
                      "NOT a launcher fault. It is the market having no free slot; the next tick re-checks."
                      % getattr(submit, "last_requested", 0))
                return 0
            print("::error title=TVAST LAUNCHER FAULT::the launcher wanted %d unit(s) and rented none, and "
                  "at least one failed on a PROVIDER/CODE error rather than on price — so we never got a "
                  "clean answer from the market. This is a real defect, not a hold. See the [launch] lines "
                  "above for the exception." % getattr(submit, "last_requested", 0))
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
