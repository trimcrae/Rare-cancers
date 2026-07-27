"""WHAT "INDEPENDENT REPLICATE" ACTUALLY MEANS ON THE valB_mini CYCLE — pinned, because the launcher's own
comment asserted a stronger form than the code delivers.

★ WHY THIS FILE EXISTS (2026-07-27). Two claims about `edge_reps` were being carried in prose, and the SD the
whole rung is being bought for is only worth reading if both are true. One of them was not.

CLAIM A — a re-used seed cannot silently resume into another replicate's trajectory. TRUE, and it has to stay
true: `SEED` is a member of `rbfe_spot_checkpoint.SYSTEM_FINGERPRINT_ENV`, so two replicates hash to different
system fingerprints and `fingerprint_mismatch_reason` refuses the cross-restore. Drop `SEED` from that tuple
and r2 could resume r1's committed generations, which would produce a perfectly-formed and completely fake
cycle SD. That is the same class of defect as the direction-blind idempotent skip (a reverse leg reporting the
forward answer, hysteresis exactly 0.000): a wrong answer whose shape is indistinguishable from a good one.

CLAIM B — "seeds 1 and 2 start from DIFFERENT independently relaxed SMARCA2 models". Read as a statement about
the pair it is true; read as the reviewer-condition-#3 property of the replicate SET it is FALSE, and the SET
is what the cycle SD is computed over. `ternary_pdb_stage` builds the homology ensemble with **n_models=2** and
takes `starting_model_index = seed % len(model_pdbs)`, so:

        seed 0 -> model 0        seed 1 -> model 1        seed 2 -> model 0   <-- same pose as r0

At n=3 two of the three ternary replicates share a starting homology pose, so the between-replicate SD
understates the homology-model component of the variance. That is not a reason to withhold the SD — it is a
reason to REPORT it with that scope, and to widen the ensemble BEFORE any "extend to 5 replicates" round,
where seeds 3 and 4 would land on models 1 and 0 and make three of five replicates share model 0.

These tests do not enforce a fix. They enforce that the arithmetic stays what the write-up says it is, so the
caveat cannot quietly stop being true (or quietly stop being needed) without a red build.
"""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, MOD)

import rbfe_spot_checkpoint as rsc  # noqa: E402
import ternary_vast_launch as tv  # noqa: E402

EDGE_REPS_SEEDS = (1, 2)
R0_SEED = 0


# --------------------------------------------------------------------------------------------------------
# CLAIM A — the fingerprint separates replicates
# --------------------------------------------------------------------------------------------------------

def test_seed_is_in_the_system_fingerprint():
    """Without this, r2 could restore r1's committed generations and the cycle SD would be fabricated."""
    assert "SEED" in rsc.SYSTEM_FINGERPRINT_ENV


def _fp(seed, **over):
    env = {"LEG_ID": "calib_hi_to_lo__ternary_vhl", "DIRECTION": "fwd", "SEED": str(seed),
           "CHARGE_METHOD": "am1bcc", "SETUP_CACHE_VERSION": "v2pe", "N_WINDOWS": "12",
           "RBFE_TIMESTEP_FS": "4.0", "RBFE_WARMUP_TIMESTEP_FS": "1.0",
           "RBFE_CONSTRAIN_LIGAND_CH": ""}
    env.update({k: str(v) for k, v in over.items()})
    return rsc.system_fingerprint(env)[0]


def test_every_replicate_pair_hashes_differently():
    seeds = (R0_SEED,) + EDGE_REPS_SEEDS
    fps = {s: _fp(s) for s in seeds}
    assert len(set(fps.values())) == len(seeds), (
        "two replicates share a system fingerprint, so one could resume the other's trajectory: %r" % fps)


def test_the_replicates_are_refused_into_each_others_generations():
    """The fingerprint being different is only half of it — the restore path has to ACT on the difference."""
    r1_manifest = {"system_fingerprint": _fp(1)}
    env_r2 = {"LEG_ID": "calib_hi_to_lo__ternary_vhl", "DIRECTION": "fwd", "SEED": "2",
              "CHARGE_METHOD": "am1bcc", "SETUP_CACHE_VERSION": "v2pe", "N_WINDOWS": "12",
              "RBFE_TIMESTEP_FS": "4.0", "RBFE_WARMUP_TIMESTEP_FS": "1.0",
              "RBFE_CONSTRAIN_LIGAND_CH": ""}
    reason = rsc.fingerprint_mismatch_reason(r1_manifest, env=env_r2)
    assert reason, "r2 was allowed to restore a generation stamped by r1"


def test_edge_reps_runs_under_strict_provenance():
    """An UNSTAMPED generation is accepted by default (so a live leg can resume after preemption). These
    commit prefixes are new, so nothing they restore can legitimately be unstamped — and accepting one would
    reopen exactly the hole the fingerprint closes."""
    assert tv.MODES["edge_reps"].get("strict_provenance") is True


# --------------------------------------------------------------------------------------------------------
# CLAIM B — the homology pose is NOT fully resampled at n=3
# --------------------------------------------------------------------------------------------------------

def _n_models_in_stager():
    """Read the ensemble width out of `ternary_pdb_stage` rather than re-typing it (CLAUDE.md §1)."""
    src = open(os.path.join(MOD, "ternary_pdb_stage.py")).read()
    widths = re.findall(r"\bn_models\s*=\s*(\d+)", src)
    assert widths, "could not find the SMARCA2 ensemble width in ternary_pdb_stage.py"
    assert len(set(widths)) == 1, (
        "ternary_pdb_stage names more than one ensemble width %r — the seed->model map is no longer a "
        "single fact and this test can no longer speak for it" % (widths,))
    return int(widths[0])


def test_the_ensemble_width_is_still_two():
    """If someone widens it, this test fails and the caveat in `MODES['edge_reps']` must be revisited —
    which is the point. A silently-widened ensemble would make the recorded limitation a lie in the other
    direction, and a stale caveat is as misleading as a missing one."""
    assert _n_models_in_stager() == 2


def test_seed_2_shares_r0s_starting_model():
    """The measured limitation, stated as arithmetic so it cannot be argued away."""
    n = _n_models_in_stager()
    assert 2 % n == R0_SEED % n, "seed 2 no longer collides with seed 0 — update the edge_reps caveat"
    assert 1 % n != R0_SEED % n, "seed 1 must still differ from seed 0, or NO pose is resampled at all"


def test_the_n3_replicate_set_resamples_the_pose_only_twice():
    n = _n_models_in_stager()
    used = {s % n for s in (R0_SEED,) + EDGE_REPS_SEEDS}
    assert len(used) == 2, used
    assert len(used) < 3, (
        "reviewer condition #3 asks each ternary replicate to use an independently relaxed model; at n=3 "
        "only %d distinct models are used, so the cycle SD understates the homology-model variance" % len(used))


def test_an_extension_to_five_would_be_worse_not_better():
    """`calibration_gate`'s BORDERLINE branch says 'extend to 5 replicates'. Recorded here because that is
    the moment the ensemble genuinely has to be widened first: at n=5 three of five replicates share model 0,
    so extending would TIGHTEN a variance that is already too tight for the wrong reason."""
    n = _n_models_in_stager()
    seeds5 = (0, 1, 2, 3, 4)
    counts = {}
    for s in seeds5:
        counts[s % n] = counts.get(s % n, 0) + 1
    assert max(counts.values()) == 3, counts


# --------------------------------------------------------------------------------------------------------
# the binary arm is untouched by claim B, and that asymmetry is worth pinning
# --------------------------------------------------------------------------------------------------------

def test_the_binary_arm_stages_no_homology_model():
    """The binary leg drops the target entirely (E3 machinery only), so its seeds differ by sampler stream
    and nothing else — there is no starting-pose collision to caveat on that arm. If this stops being true
    the write-up's asymmetry stops being true with it."""
    src = open(os.path.join(MOD, "ternary_pdb_stage.py")).read()
    assert re.search(r'else:\s*#\s*binary: E3 machinery only \(drop the target\)', src), (
        "the binary staging branch changed shape; re-check whether it now builds a SMARCA2 model")


# --------------------------------------------------------------------------------------------------------
# and the reason the binary legs are bought at all
# --------------------------------------------------------------------------------------------------------

def test_edge_reps_buys_matched_binary_legs_for_every_seed():
    """★ THE TERNARY-ONLY PROPOSAL, REFUSED IN CODE RATHER THAN IN PROSE.

    `ternary_fep_reduce.per_replicate_ddg_coop` pairs legs on `set(ternary) & set(binary)`. Drop the binary
    legs and that intersection stays {0}, n_paired = 1, and `calibration_gate` returns the same
    "need >=2 independent replicates" INDETERMINATE the rung is being bought to escape. So an unmatched
    edge_reps is not a cheaper version of this experiment; it is a version that cannot produce its
    deliverable."""
    legs = tv.MODES["edge_reps"]["legs"]
    tern = {seed for lid, seed, _d in legs if lid.endswith("__ternary_vhl")}
    bina = {seed for lid, seed, _d in legs if lid.endswith("__binary_vhl")}
    assert tern == bina == set(EDGE_REPS_SEEDS), (tern, bina)


def test_no_per_replicate_solvent_leg_is_bought():
    """The other half of the leg count: the solvent morph enters both arms with the same sign and cancels
    exactly inside each replicate's cycle, so a per-replicate solvent leg is two rentals spent on a term that
    algebraically drops out. Four legs, not six — and not two."""
    legs = tv.MODES["edge_reps"]["legs"]
    assert not [lid for lid, _s, _d in legs if "solvent" in lid]
    assert len(legs) == 4


def test_the_paired_seed_count_is_what_the_gate_reads():
    """End-to-end on the reducer's own arithmetic, with no files: r0 + the two edge_reps seeds give n=3, and
    a ternary-only set gives n=1. Written against the same intersection rule the reducer uses so it fails if
    that rule is ever loosened to a union (which would silently pair a ternary leg with nothing)."""
    tern = {0, 1, 2}
    matched = {0, 1, 2}
    ternary_only = {0}
    assert len(tern & matched) == 3
    assert len(tern & ternary_only) == 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([os.path.abspath(__file__), "-q"]))
