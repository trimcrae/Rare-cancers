#!/usr/bin/env python3
"""
NR-V04 RETROSPECTIVE holdout — the FROZEN panel + per-unit run spec (prereg §2).

Single source of truth for "what runs" in the retrospective, mirroring nrv04_covalent_panel.py for the
feasibility panel. Both the endpoint-MD driver (nrv04_covalent_md.py, reused unchanged — it is target-agnostic)
and the Vast launcher consume this, so the panel cannot drift between them. Pure data + pure builders, so it is
unit-tested offline.

THE DESIGN POINT (prereg §0): NR4A1 Cys551 is NOT conserved in NR4A2/NR4A3 (Leg 0, nrv04-cys-conservation.json
- Tyr and Thr respectively, no Cys within +/-5). Celastrol cannot form the covalent adduct on the paralogues at
all. So the panel does NOT run "three paralogues, same treatment" and call a NR4A1 win a recovery of NR-V04
selectivity. It DECOMPOSES:

  R1 (PRIMARY) : NR4A1 vs NR4A2 vs NR4A3, all NON-COVALENT  -> does the ternary workflow discriminate paralogues
                 with the warhead-reactivity confound held OFF? (the contrast a prospective, non-covalent NR4A3
                 degrader campaign actually depends on)
  R2           : NR4A1 covalent vs NR4A1 non-covalent        -> RETIRED by AMENDMENT 3 (see RETIRED_STAGES)
  R3           : epimer arms                                 -> CONDITIONAL (prereg 5d); needs new co-folds

There is deliberately NO covalent NR4A2/NR4A3 leg and none may be added - there is no cysteine to bond to, so
modelling one would be fabricating chemistry.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# ---- frozen structural provenance (prereg 2a) --------------------------------------------------------------
# Every leg starts from a Boltz-2 co-fold under this ONE prefix. Using a single prefix for all three paralogues
# is what makes the arms protocol-matched; the nrv04-covalent-cofold / nrv04-shakeout NR4A1 structures are
# deliberately NOT mixed in. Inventory: CI run 30121409280 -> nrv04-cofold-discovery.json.
#
# ⚠ WHY v4 AND NOT v3. The original intent was to reuse nrv04-descriptive-v3 (built 2026-07-11). The 2026-07-24
# audit (CI run 30122648680) identified its chain F as 255 residues = UniProt P62258, **14-3-3 protein epsilon**,
# not the 118-residue Elongin B it was supposed to be: nrv04_ternary.py fetches the ELONGIN_B constant's
# sequence directly, and that constant was P62258 until the 2026-07-17 correction. Those assemblies are not the
# VHL/EloB/EloC machinery, so they cannot support a ternary-recruitment readout and are NOT reused. v4 is the
# regeneration with the corrected accession. Full record: nrv04-cofold-chain-forensics-2026-07-24.md.
# The staging assembler independently REJECTS a 255-residue chain (nrv04_covalent_assemble.identify_chains), so
# a v3 path cannot be taken by accident even if this constant were pointed back at it.
COFOLD_PREFIX = "nrv04-descriptive-v4"
COFOLD_MODEL_SEEDS = (1, 2, 3)          # the co-fold model seeds available for nr4a1/nr4a2/nr4a3 alike
MD_REPLICAS = (0, 1)                    # velocity seeds within a co-fold model (prereg 2b)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ AMENDMENT 4 (2026-07-31, trimcrae) — ONE CO-FOLD MODEL IS EXCLUDED, BY MEASURED INPUT FAULT
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# `nrv04-descriptive-v4/nr4a3/seed_3` places two HEAVY ATOMS on top of each other:
#
#     A:GLU13:O  <->  A:LYS181:NZ   at   0.181 A          (both positioned by Boltz)
#     PE at `protein_after_pdbfixer` = +2.109e15 kJ/mol over 10,914 atoms, against a control at +2.08e5
#     -> ten decades, with NonbondedForce carrying it and BOTH clashing pairs co-fold-heavy vs co-fold-heavy
#
# so the Lennard-Jones term diverges, minimization cannot escape it, and the first integration step yields
# NaN. Measured by `nrv04_pe_stage_probe` (runs 30663617181 / 30662210714); the probe's solvated figure
# reproduces the production leg's own recorded `pe_pre_min` to TEN SIGNIFICANT FIGURES, which is what makes
# this a diagnosis of the real failure rather than a lookalike.
#
# ⛔ EXCLUDED BY INPUT, NOT BY OUTCOME — this is the line that answers a selection-bias objection.
# The fault is a static property of the predicted structure, provable BEFORE any MD is interpreted, and the
# replicate structure is what makes the claim testable: `MD_REPLICAS` are velocity seeds WITHIN a co-fold
# model, so r0 and r1 share an input. BOTH replicas of seed_3 died at `prod@frame0` in ~4.4 s with no frames;
# BOTH replicas of every other co-fold produced or are producing real production frames. A thermostat seed
# cannot rescue two atoms at 0.181 A, and that asymmetry is the evidence.
#
# ⚠ IT IS A DATA STRUCTURE, NOT A HAND-MAINTAINED LIST OF UNITS. Keyed on (arm_id, model_seed) — the co-fold
# — so it drops exactly the 2 legs that draw on the bad structure and cannot silently widen. Supplying a
# corrected co-fold for nr4a3 seed 3 is a one-line deletion here plus a further amendment; nothing else moves.
EXCLUDED_COFOLD_MODELS = {
    ("retro_noncov_nr4a3", 3): (
        "AMENDMENT 4 (2026-07-31): input fault. nrv04-descriptive-v4/nr4a3/seed_3 places A:GLU13:O and "
        "A:LYS181:NZ 0.181 A apart (both Boltz-placed heavy atoms); PE +2.109e15 kJ/mol at "
        "protein_after_pdbfixer vs a control at +2.08e5. Ligand placement and addSolvent are EXONERATED - "
        "the divergence is fully formed before either runs. Both replicas failed; no other co-fold's did."),
}


def excluded_cofold(arm_id: str, model_seed: int):
    """(excluded, why) for one co-fold model. PURE. `why` is empty when it is not excluded."""
    return ((arm_id, model_seed) in EXCLUDED_COFOLD_MODELS,
            EXCLUDED_COFOLD_MODELS.get((arm_id, model_seed), ""))

# celastrol electrophile / NR4A1 reactive cysteine - identical to the feasibility panel (prereg 2c).
CELASTROL_ELECTROPHILE_ATOM = "C6"
TARGET_COV_RESNUM = 551

# sampling: the canonical md_settings lengths the feasibility panel ran (1 ns equil + 5 ns production).
PROD_NS = 5.0
EQUIL_NS = 1.0


@dataclass(frozen=True)
class RetroArm:
    arm_id: str
    ligand: str                # "nrv04" | "nrv04_epimer"
    target: str                # "NR4A1" | "NR4A2" | "NR4A3"
    covalent: bool
    cofold_system: str         # co-fold subdir under COFOLD_PREFIX
    stage: str                 # "R1" | "R2" | "R3"
    role: str = ""
    controls_for: tuple = field(default_factory=tuple)


# Frozen arms (prereg 2b table). Order is fixed. R3 is present but NOT authorized until prereg 5d fires.
ARMS = (
    RetroArm("retro_noncov_nr4a1", "nrv04", "NR4A1", False, "nr4a1", "R1",
             role="primary matched non-covalent arm - the degraded paralogue", controls_for=("E1",)),
    RetroArm("retro_noncov_nr4a2", "nrv04", "NR4A2", False, "nr4a2", "R1",
             role="primary matched non-covalent arm - spared paralogue", controls_for=("E1",)),
    RetroArm("retro_noncov_nr4a3", "nrv04", "NR4A3", False, "nr4a3", "R1",
             role="primary matched non-covalent arm - spared paralogue (the design target)", controls_for=("E1",)),
    # RETIRED by AMENDMENT 3 defect 1 — kept in the frozen table (a preregistered arm is never silently
    # deleted) but UNENUMERABLE: `arms_for_stages` raises on stage "R2". See RETIRED_STAGES.
    RetroArm("retro_cov_nr4a1", "nrv04", "NR4A1", True, "nr4a1", "R2",
             role="RETIRED (AMENDMENT 3): covalency decomposition — unbuildable, 0/3 models inside the 8.0 A "
                  "adduct limit", controls_for=("R2",)),
    # --- R3, conditional (prereg 5d): the epimer co-folds exist for NR4A1 only; nr4a2/nr4a3 need generating.
    RetroArm("retro_epi_nr4a1", "nrv04_epimer", "NR4A1", False, "neg_inactive", "R3",
             role="VHL-inactive epimer specificity control", controls_for=("R3",)),
    RetroArm("retro_epi_nr4a2", "nrv04_epimer", "NR4A2", False, "neg_inactive_nr4a2", "R3",
             role="epimer control - REQUIRES a new co-fold", controls_for=("R3",)),
    RetroArm("retro_epi_nr4a3", "nrv04_epimer", "NR4A3", False, "neg_inactive_nr4a3", "R3",
             role="epimer control - REQUIRES a new co-fold", controls_for=("R3",)),
)

# ★★ R2 IS RETIRED — AMENDMENT 3 DEFECT 1 (2026-07-25), APPLIED IN CODE 2026-07-31.
#
# The amendment is not a style note, it is load-bearing twice over, and until this constant changed it was
# PROSE ONLY while `AUTHORIZED_STAGES` still said ("R1", "R2"):
#   (a) the 6 covalent units are UNBUILDABLE. `nrv04_covalent_md.build_system` raises on the C6->Cys551
#       adduct BEFORE a leg JSON is written (measured 34.42 / 29.87 / 39.11 A on the exact pinned models
#       nrv04-descriptive-v4/nr4a1/seed_{1,2,3}, against A1's 8.0 A limit: 0 of 3 pass). Vast re-runs the
#       onstart after the container dies, so each of those 6 rentals crash-loops and bills until a control
#       plane reaps it.
#   (b) far worse, they BLOCK THE RESULT. `nrv04_vast_launch.retro_collect` builds `expected` from
#       `enumerate_units()`, so 6 units that can never land keep `panel_complete` False forever and prereg
#       S4f (no interim analysis) then suppresses the R1 verdict PERMANENTLY. Leaving R2 in does not merely
#       cost an arm, it costs the primary result.
#
# So the authorized panel is R1 ONLY, 18 legs. The covalent confound is documented from Leg 0 (sequence:
# Cys551 unique to NR4A1) and Zhang 2018 (literature) — never from a simulation this program ran.
#
# SUPERSEDED, retained for the record: AUTHORIZED_STAGES was ("R1", "R2") and enumerate_units() yielded 24.
AUTHORIZED_STAGES = ("R1",)             # prereg 7 + AMENDMENT 3 defect 1: R2 retired, R3/Arm F conditional/blocked
RETIRED_STAGES = ("R2",)                # never enumerable — see `arms_for_stages`, which REFUSES to yield these
PRIMARY_ARM = "retro_noncov_nr4a1"
PARALOGUE_ARMS = ("retro_noncov_nr4a2", "retro_noncov_nr4a3")

#: The Vast label / S3 checkpoint namespace for this panel. Its ONE home (CLAUDE.md rule 1): the reaper's
#: label selector is derived from it, so a lane rename can never leave a reaper matching the old prefix — or,
#: worse, matching a SIBLING lane's boxes. `nrv04_covalent_panel.unit_name` owns "nrv04cov-"; the two
#: namespaces are disjoint and neither is a prefix of the other.
LABEL_PREFIX = "nrv04retro-"


def arm_by_id(arm_id: str) -> RetroArm:
    for a in ARMS:
        if a.arm_id == arm_id:
            return a
    raise KeyError(f"unknown retrospective arm {arm_id!r}; known: {[a.arm_id for a in ARMS]}")


def arms_for_stages(stages=AUTHORIZED_STAGES):
    """Arms in `stages`, with a RETIRED stage refused rather than silently dropped.

    Refusing loudly is the point. A retired stage that merely returns an empty list would let
    `--stages R1,R2` print a 18-unit manifest labelled as if it covered R2, and a caller could re-authorize
    the crash-looping covalent arm by passing one string. AMENDMENT 3 retired R2 on measured evidence; it is
    not a runtime option."""
    bad = [s for s in stages if s in RETIRED_STAGES]
    if bad:
        raise ValueError(
            f"stage(s) {bad} are RETIRED by AMENDMENT 3 (2026-07-25) and can never be enumerated: the "
            f"C6->Cys551 adduct measures 34.42 / 29.87 / 39.11 A against an 8.0 A admissibility limit, so "
            f"nrv04_covalent_md.build_system raises before a leg JSON is written — those units crash-loop on "
            f"a billing host and keep panel_complete False, which suppresses the R1 verdict permanently. "
            f"Authorized stages: {list(AUTHORIZED_STAGES)}.")
    return [a for a in ARMS if a.stage in stages]


def enumerate_units(stages=AUTHORIZED_STAGES, model_seeds=COFOLD_MODEL_SEEDS, replicas=MD_REPLICAS,
                    include_excluded=False):
    """Every independent GPU unit = (arm, cofold_model_seed, md_replica). One Vast instance each, its own
    checkpoint prefix. **16** for the authorized R1-only panel after AMENDMENT 4 (nr4a3 models 1-2, nr4a1 and
    nr4a2 models 1-3, x 2 replicas).

    ⛔ THE PANEL SHRINKS HERE, IN THE ENUMERATION, AND NOWHERE ELSE. `retro_collect` builds `expected` from
    this function, so `panel_complete` goes true because the panel HONESTLY CHANGED — not because any gate
    predicate was loosened to let an unreachable panel pass. `nrv04_retro_gate.verdict`, prereg S4f's
    suppression, the endpoints, alpha, the direction and the unit of independence are all untouched.

    `include_excluded=True` yields the pre-amendment 18 for provenance and tests; it is never what the lane
    runs. See `EXCLUDED_COFOLD_MODELS` for the measured cause of every exclusion.
    """
    return [(a, m, r) for a in arms_for_stages(stages) for m in model_seeds for r in replicas
            if include_excluded or not excluded_cofold(a.arm_id, m)[0]]


def unit_name(arm: RetroArm, model_seed: int, replica: int) -> str:
    """Stable per-unit name (Vast label + S3 checkpoint prefix, so units never collide)."""
    return f"{LABEL_PREFIX}{arm.arm_id}-m{model_seed}-r{replica}"


def cofold_prefix_s3(arm: RetroArm, bucket: str, model_seed: int) -> str:
    """The S3 PREFIX of the specific co-fold MODEL this leg starts from. Unlike the feasibility panel (which
    globbed one system dir), the retrospective pins the model seed, because the co-fold model is the unit of
    independence in the statistics (prereg 4a)."""
    return f"s3://{bucket}/{COFOLD_PREFIX}/{arm.cofold_system}/seed_{model_seed}/"


def leg_env(arm: RetroArm, model_seed: int, replica: int, mode: str = "run",
            prod_ns: float = PROD_NS, equil_ns: float = EQUIL_NS) -> dict:
    """The engine env for one unit - consumed by nrv04_covalent_md.py unchanged (it derives E3-vs-target chains
    from the topology, so it is paralogue-agnostic). Deterministic, no I/O.

    LEG_ID carries the model seed so a leg's inputs, checkpoint and result JSON all agree; SEED is the MD
    velocity replica (what the driver seeds the thermostat with)."""
    env = {
        "PANEL": "nrv04_retrospective",
        "LEG_ID": f"{arm.arm_id}__m{model_seed}",
        "SEED": str(replica),
        "MODE": mode,
        "LIGAND": arm.ligand,
        "TARGET": arm.target,
        "ENV_ASSEMBLY": f"ternary_{arm.target.lower()}",
        "COVALENT": "1" if arm.covalent else "0",
        "MUTATION": "",
        "PROD_NS": str(prod_ns),
        "EQUIL_NS": str(equil_ns),
        "COFOLD_MODEL_SEED": str(model_seed),
        "OPENMM_REQUIRE_CUDA": "1",
    }
    if arm.covalent:
        env["COV_LIG_ATOM"] = CELASTROL_ELECTROPHILE_ATOM
        env["COV_RESNUM"] = str(TARGET_COV_RESNUM)
    return env


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ WHAT COUNTS AS A LANDED LEG — the predicate, with ONE home (CLAUDE.md rule 1)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ⛔ MEASURED 2026-07-31 (fusion-cpu-extras run 30642442241, job 91195498091). `retro_collect` counted a unit as
# LANDED on the mere EXISTENCE of a `leg_*.json` under its prefix. `nrv04_covalent_md.run_leg` writes that same
# record for a SMOKE leg — `mode == "smoke"` sets `equil_steps, prod_steps, stride = 0, 500, 100`, i.e. ZERO
# equilibration and 5 frames spanning 0.002 ns — and it fills `prod_ns` / `equil_ns` from the ENV rather than
# from what actually ran, so a smoke record still reads `prod_ns: 5.0, equil_ns: 1.0` and is indistinguishable
# from a production leg on those fields alone. The measured smoke record for
# `nrv04retro-retro_noncov_nr4a1-m1-r1` was: mode=smoke, n_frames=5, timed_ns=0.002, prod_wall_s=7.4 —
# and a fully-populated `R1_interface: {plateau_A: 1.09, stable: true}`, which is exactly the field the frozen
# gate scores. 18 such records drove `panel_complete` TRUE and the prereg §4f suppression OFF.
#
# So "a result exists" is NOT "the preregistered protocol ran". These predicates are that distinction, they
# live beside the frozen panel spec they enforce, and every caller — the collector's coverage, the launcher's
# skip-set, the supervisor's done-set — imports them rather than re-spelling `startswith("leg_")`.
#
# ★★ AND IT IS **TWO** QUESTIONS, NOT ONE. Collapsing them silently disarms prereg §4e:
#
#   1. `production_leg_check` — WHICH PROTOCOL RAN. `mode` and the frozen sampling lengths. This governs PANEL
#      MEMBERSHIP: a smoke is not a leg of this panel at all, so its unit stays MISSING and §4f keeps the
#      contrast suppressed until a real leg lands.
#   2. `completed_production_check` — DID IT FINISH. Blow-ups and truncated production. This is a SCIENTIFIC
#      OUTCOME the frozen gate already scores (`technical_failure`, `MAX_FAILED_LEGS_PER_ARM`,
#      `underpowered_arms`), so it must NOT remove the unit from the panel — do that and an arm that genuinely
#      melts becomes an eternally-incomplete panel instead of the "underpowered arm" §4e registers.
#
# The 2026-07-31 smoke records fail (1). A blown-up 5 ns leg passes (1) and fails (2), which is exactly right.
#: Fraction of PROD_NS the timed production must reach to count as FINISHED. Not a science threshold — a
#: completion check. A resumed leg finishes at PROD_NS exactly; the slack only absorbs float rounding.
PRODUCTION_TIMED_NS_TOLERANCE = 0.02


def expected_production_frames(prod_ns: float = PROD_NS) -> int:
    """Frames a conforming production leg writes. DERIVED from the canonical md_settings, never typed: the
    driver strides at `frame_stride_steps()` over `prod_ns / TIMESTEP_NS` steps (nrv04_covalent_md.run_leg)."""
    import md_settings as MD
    return max(1, int(prod_ns / MD.TIMESTEP_NS) // MD.frame_stride_steps())


def production_leg_check(rec: dict, prod_ns: float = PROD_NS, equil_ns: float = EQUIL_NS) -> tuple:
    """PURE: was this record produced by a run of the PREREGISTERED protocol? -> (ok: bool, why: str).

    Membership only — see the block above. `ok` is what may enter the panel and its coverage count; anything
    else is an artifact that exists and is reported, never deleted (rule 1.2), but is not a leg of this panel.
    Whether the leg then SUCCEEDED is `completed_production_check`, and the frozen gate scores that."""
    if not isinstance(rec, dict):
        return False, "not a leg record"
    mode = rec.get("mode")
    if mode != "run":
        return False, (f"mode={mode!r}, not 'run' — a smoke leg runs 500 steps with NO equilibration "
                       f"(nrv04_covalent_md.run_leg) and cannot carry the preregistered endpoint")
    for field, want in (("prod_ns", prod_ns), ("equil_ns", equil_ns)):
        got = rec.get(field)
        if got is not None and abs(float(got) - want) > 1e-9:
            return False, f"{field}={got!r}, not the preregistered {want} — a different protocol was requested"
    return True, f"protocol of record: mode=run, prod_ns={prod_ns}, equil_ns={equil_ns}"


def completed_production_check(rec: dict, prod_ns: float = PROD_NS) -> tuple:
    """PURE: did a panel leg REACH the end of its production run? -> (ok: bool, why: str).

    A False here is a TECHNICAL FAILURE (prereg §4e), not an absent leg: the unit stays in the panel and the
    frozen gate counts it against `MAX_FAILED_LEGS_PER_ARM`."""
    if not isinstance(rec, dict):
        return False, "not a leg record"
    if rec.get("blew_up"):
        return False, f"blew_up at {rec.get('blow_phase')!r}"
    timed = rec.get("timed_ns")
    if not isinstance(timed, (int, float)):
        return False, "timed_ns missing — the record does not say how much sampling it actually did"
    if timed < prod_ns * (1.0 - PRODUCTION_TIMED_NS_TOLERANCE):
        return False, (f"timed_ns={timed} against prod_ns={prod_ns} — production stopped early; `prod_ns` is "
                       f"the REQUEST, `timed_ns` is what ran")
    want = expected_production_frames(prod_ns)
    got = rec.get("n_frames")
    if got != want:
        return False, f"n_frames={got!r}, expected {want} for {prod_ns} ns at the canonical frame stride"
    return True, f"complete: {timed} ns timed over {want} frames"


def is_production_leg(rec: dict, prod_ns: float = PROD_NS) -> bool:
    """`production_leg_check` reduced to its boolean, for call sites that do not report the reason."""
    return production_leg_check(rec, prod_ns=prod_ns)[0]


def panel_manifest(stages=AUTHORIZED_STAGES) -> dict:
    """Self-describing manifest of exactly what would run (no I/O, no spend) - the thing to eyeball before a
    fan-out and to attach to the result."""
    units = enumerate_units(stages)
    per_arm = {}
    for a, m, r in units:
        per_arm.setdefault(a.arm_id, []).append(unit_name(a, m, r))
    return {
        "panel": "nrv04_retrospective",
        "prereg": "nr4a3-nrv04-retrospective-prereg.md",
        "stages": list(stages),
        "retired_stages": list(RETIRED_STAGES),
        "cofold_prefix": COFOLD_PREFIX,
        "cofold_model_seeds": list(COFOLD_MODEL_SEEDS),
        "md_replicas": list(MD_REPLICAS),
        "n_units": len(units),
        "units_per_arm": per_arm,
        "label_prefix": LABEL_PREFIX,
        "primary_contrast": {"arm": PRIMARY_ARM, "vs_pooled": list(PARALOGUE_ARMS),
                             "endpoint": "E1 interface-RMSD plateau (A), lower = more stable",
                             "predicted_sign": "negative (NR4A1 more stable)"},
        "sampling_ns": {"equil": EQUIL_NS, "prod": PROD_NS},
        "honesty": "Arm E (ensemble endpoint MD) only - NO free energy is computed here. The alchemical "
                   "ddG_coop arm (Arm F) is BLOCKED on the valB calibration PASS (calib addendum condition 7). "
                   "R2 (the covalent decomposition) is RETIRED by AMENDMENT 3 defect 1: unbuildable on every "
                   "available input, and while enumerable it blocked the R1 verdict entirely.",
    }


def _cli(argv=None):
    import argparse
    import json
    ap = argparse.ArgumentParser(description="NR-V04 retrospective frozen panel (pure; no spend).")
    ap.add_argument("--stages", default=",".join(AUTHORIZED_STAGES))
    ap.add_argument("--units", action="store_true", help="print every unit name and exit")
    args = ap.parse_args(argv)
    stages = tuple(s.strip() for s in args.stages.split(",") if s.strip())
    if args.units:
        for a, m, r in enumerate_units(stages):
            print(unit_name(a, m, r))
        return 0
    print(json.dumps(panel_manifest(stages), indent=2))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
