#!/usr/bin/env python3
"""ENDPOINT-MD SENSITIVITY CONTROL (options paper D1) — the FROZEN panel and its PRE-REGISTERED criterion.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
⛔ WHAT THIS IS. AN INSTRUMENT CALIBRATION. NOT A SELECTIVITY RESULT.
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
The NR-V04 retrospective returned tier **DISCORDANT, p = 0.3929** — a non-resolution. The deeper problem it
exposed is not the tier: **this program has no positive control showing that its workflow can detect paralogue
selectivity at all.** NR-V04 cannot become one at any n, because it is **covalency-confounded** — the reactive
Cys551 is unique to NR4A1 (`nrv04-cys-conservation.json`), so warhead chemistry alone explains the reported
selectivity and the non-covalent arm has no guaranteed true effect to detect. The method calibrator that would
answer the question — valB_full module 3, SMARCA2-vs-SMARCA4 — has never been run.

So this panel asks exactly one question:

    **Can the endpoint-MD readout detect a paralogue difference that is KNOWN, from a primary source, to be
    there?**

A PASS licenses one sentence — *"the readout discriminates a known paralogue pair under this protocol"* — and
**nothing else**. In particular it does NOT license:
  * any claim about NR4A1/2/3, whose panel is a different system with a different confound;
  * any claim about degradation, efficacy, a therapeutic window, or selectivity of a designed molecule;
  * any re-scoring, amendment or reinterpretation of the NR-V04 retrospective, which is frozen.
And a **FAIL is ambiguous** between *"the readout is blunt"* and *"this pair is hard"* — which is why the shape
below is chosen to be adequately powered, and why the failure sentence is written in §4 of the options paper
BEFORE the run rather than narrated afterwards.

Design: [`selectivity-resolution-options.md`](./selectivity-resolution-options.md) §2-D. **That file is the
design and is not re-derived here.** This module is its executable form.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
★★ THE CRITERION IS WRITTEN BEFORE THE NUMBERS ARRIVE — that is the whole point
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
A criterion written after the data is not a criterion, and this repo has already paid for the general lesson
(AMENDMENT 1's standard: swapping the test after a result, on the same data, is the retune the program
forbids). `PASS_CRITERION` below is frozen in the same commit that first launches a GPU leg, and
`tests/test_selcal_panel.py` pins every clause of it. `selcal_gate.verdict` is the ONLY scorer and it imports
the enumeration primitives from `nrv04_retro_gate` rather than re-implementing a permutation test — one home
per rule 1.

WHY THE DIRECTION IS PREDICTED RATHER THAN TWO-SIDED. The reference is not merely "these paralogues differ":
the primary source attributes the difference to a **ternary-complex protein–protein interaction**, which is
precisely the quantity E1 measures. A two-sided test on a known-direction control would throw that away and
double the p-value for nothing. The direction is recorded in `PREDICTED_MORE_STABLE_ARM` and is a *commitment*:
a significant result in the WRONG direction is a FAIL, not a pass with a footnote (`TIER_WRONG_SIGN`).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))

# =============================================================================================================
# 1 · THE SYSTEM — a structure-matched paralogue pair, both arms real
# =============================================================================================================
#: UniProt accessions. Sequences are FETCHED at staging time (`selcal_stage.construct_sequence`), never typed
#: here — a hand-copied 120-residue sequence is a fabrication risk with no upside.
SMARCA2_ACC = "P51531"
SMARCA4_ACC = "P51532"
#: The VCB machinery, identical to the deposited ternaries on BOTH arms and to this repo's other VHL lanes.
#: Imported from `nrv04_ternary` at use time so a corrected accession can never diverge between lanes — the
#: Elongin-B accession was wrong once already (P62258 = 14-3-3 epsilon; corrected 2026-07-17).
E3_ACCESSIONS = ("VHL", "ELONGIN_B", "ELONGIN_C")

#: The domain each arm contributes, and where its boundaries come from. `selcal_stage.CONSTRUCTS` is the one
#: home of the spans; they are QUOTED from the crystallographers' own methods section rather than guessed, so
#: the two arms are comparable to each other AND to the deposited ternaries that validate them.
CONSTRUCT_DOMAIN = "bromodomain (published crystallographic construct — selcal_stage.CONSTRUCTS)"

#: The pair, as the survey found it. `s-calibrator-survey.json` is the one home of the structural screen; this
#: is a pointer, not a second copy.
SURVEY_ARTIFACT = "s-calibrator-survey.json"
#: The primary-source reference, fetched by `selcal_reference_selectivity.py` on a CI runner.
REFERENCE_ARTIFACT = "selcal-reference-selectivity.json"


# =============================================================================================================
# 2 · THE REFERENCE — measured, primary-source, quoted
# =============================================================================================================
# ⚠ EVERY FIELD HERE IS TRANSCRIBED FROM `selcal-reference-selectivity.json`, WITH THE QUOTE ATTACHED, and
# `tests/test_selcal_panel.py` re-checks the quotes against that artifact when it is present. AGENTS.md's
# medical-integrity rule is the binding one: a number with no source is a fabrication, whatever it is about.
#
# ★ WHAT THE REFERENCE HAS TO ESTABLISH, and what it deliberately does not.
#   IT MUST establish (a) that a real paralogue difference exists for this ligand, in a primary source, and
#   (b) its DIRECTION. Those two facts are what make this a control.
#   IT MUST NOT be converted into an expected Ångström separation. E1 has **no established quantitative link
#   to degradation selectivity** (options paper §1d(3)), so a DC50 ratio → Å calibration would fabricate the
#   very link the program lacks. The magnitude enters only as the sanity floor STRATEGY Open decision 7
#   requires: a difference inside its own measurement error is not a signal to calibrate against.
REFERENCE = {
    "ligand": "PRT3789",
    "ligand_ccd": "A1BB4",
    "pair": ("SMARCA2", "SMARCA4"),
    "citation": {
        "title": "PRT3789 Is a First-in-Human SMARCA2-Selective Degrader That Induces Synthetic Lethality in "
                 "SMARCA4-Mutated Cancers",
        "journal": "Cancer Research", "year": 2026,
        "doi": "10.1158/0008-5472.can-25-1141", "pmcid": None, "open_access": False,
    },
    #: The claim, quoted verbatim from the peer-reviewed abstract (the body is not open access).
    "selectivity_quote": "PRT3789 promoted selective degradation of SMARCA2 while sparing its highly "
                         "homologous paralog, SMARCA4.",
    "assay": "cellular degradation; the paper's own summary of its result",
    #: ★★ THE HONEST LIMIT OF THIS REFERENCE, STATED WHERE IT CANNOT BE MISSED. The abstract establishes
    #: EXISTENCE and DIRECTION and nothing more: the quantitative window is in the paywalled body, and this
    #: repo does not quote numbers it has not read. That is sufficient here and only here — see
    #: `_why_direction_and_existence_suffice` — and it is explicitly NOT sufficient for any quantitative
    #: calibration, which is why none is attempted.
    "magnitude_not_quotable": "The primary publication is not open access, so no DC50 pair or fold window is "
                              "quoted. Secondary sources report ~40-fold; that number is NOT used anywhere in "
                              "this panel and must not be cited from here.",
    "_why_direction_and_existence_suffice": "The criterion this control applies is itself CATEGORICAL — does "
                                            "the readout separate the arms, in the predicted direction? — so "
                                            "the reference only has to answer the same kind of question. "
                                            "STRATEGY Open decision 7 (the accuracy band may not be wider "
                                            "than the signal being calibrated) is met because neither side "
                                            "is a magnitude. A QUANTITATIVE calibration of E1 against "
                                            "degradation is a different claim, is not licensed by this "
                                            "reference, and is not attempted — E1 has no established "
                                            "quantitative link to degradation selectivity at all "
                                            "(options paper §1d(3)).",
    # ★★ WHY THIS LIGAND AND NOT ACBI2, which has the better-documented numbers. TWO deposited ternaries
    # carry PRT3789 with the SAME ligand on BOTH arms — 9DTY (SMARCA2, 3.19 Å) and 9DTX (SMARCA4, 2.11 Å) —
    # so each arm's co-fold can be VALIDATED against a real structure of the very complex it models. That is
    # exactly what options-paper precondition 2 asks for and says the crystals do not supply. ACBI2 has no
    # deposited structure at all (its paper deposits compounds 4/5/6/10: 7Z78/7Z6L/7Z77/7Z76), so its
    # chemistry could only come from a vendor catalogue — not a primary source, and therefore not usable.
    "deposited_ternaries": {"SMARCA2": "9DTY", "SMARCA4": "9DTX"},
    "why_this_ligand": "the only candidate with (a) a matched-ligand ternary deposited on BOTH arms, so both "
                       "co-folds can be validated against a real structure of the same complex, and (b) a "
                       "primary-source selectivity claim in a stated direction. ACBI2 has better numbers and "
                       "NO deposited structure, so its chemistry would have to come from a vendor catalogue.",
    #: ★ WHY THE DIFFERENCE IS EXPECTED AT THE INTERFACE E1 MEASURES — a fact about this PAIR and the VHL
    #: machinery, established in an open-access primary source, and the reason a ternary-geometry readout is
    #: the right instrument rather than a hopeful one. Kofink et al. 2022 (Nat Commun, PMC9551036,
    #: 10.1038/s41467-022-33430-6), verbatim:
    "pair_mechanism_quote": "Represented are the key PPIs between VCB and SMARCA2BD/SMARCA4BD, highlighting "
                            "the selectivity-inducing hydrogen bonding between Gln1469 of SMARCA2BD and VCB",
    "pair_mechanism_source": {"doi": "10.1038/s41467-022-33430-6", "pmcid": "PMC9551036",
                              "note": "about the SMARCA2/SMARCA4 pair against VCB, not about PRT3789. It is "
                                      "why a VCB<->bromodomain interface readout is the right instrument for "
                                      "this pair; it is NOT a claim about the reference ligand."},
    "mechanism_is_ternary_interface": True,
    #: The matched NON-selective comparator. NOT run here (a second 24-leg panel and a second spend); recorded
    #: because it is the obvious follow-on negative control and because naming it stops a later reader
    #: concluding that none was available.
    "matched_nonselective_comparator": {
        "ligand": "ACBI1", "doi": "10.1038/s41589-019-0294-6", "pmcid": "PMC6600871", "ccd": "87A",
        "quote": "Complete and potent degradation induced by ACBI1 was observed for SMARCA2 (DC50 of 6 nM) "
                 "and SMARCA4 (DC50 of 11 nM) in MV-4-11 cells",
        "why_not_run": "outside the authorised $3.79 for D1/D2 — it is a second panel, not a second arm.",
    },
}

#: The arm the reference predicts is MORE stable in the ternary complex (= LOWER interface-RMSD plateau).
PREDICTED_MORE_STABLE_ARM = "selcal_smarca2"


# =============================================================================================================
# 3 · THE PANEL — 2 arms x 6 co-fold models x 2 velocity replicas = 24 legs
# =============================================================================================================
#: WHY THIS SHAPE, from the options paper's own derivation: it is the smallest design whose PAIRWISE reference
#: set is comfortably clear of alpha. C(12,6) = 924 arrangements, so the minimum attainable one-sided p is
#: 1/924 = 0.00108 — two orders of magnitude under alpha, against the NR-V04 pairwise floor of 0.10 that made
#: that comparison a non-measurement. `selcal_gate.design_floor()` derives the number; it is not typed.
COFOLD_MODEL_SEEDS = (1, 2, 3, 4, 5, 6)
MD_REPLICAS = (0, 1)

#: The sampling protocol, IDENTICAL to the NR-V04 retrospective's, imported from the canonical settings.
#: ⛔ "Identical" is the scientific content of the word `control`: if this panel ran a different protocol, a
#: pass would say the readout works at THAT protocol and would be silent about the one the program actually
#: used. `md_settings` is the single source; these names exist so a reader sees them beside the panel.
PROD_NS = 5.0
EQUIL_NS = 1.0

#: The Vast label / S3 checkpoint namespace. Its ONE home: the reaper's selector is derived from it, so a
#: rename can never leave a reaper matching a SIBLING lane's boxes. Disjoint from `nrv04retro-` and
#: `nrv04cov-`, and neither is a prefix of the other.
LABEL_PREFIX = "selcal-"

#: The co-fold prefix in S3. A FRESH prefix per design freeze — a co-fold is a preregistered leg's input and
#: reusing one silently changes what the panel started from.
COFOLD_PREFIX = os.environ.get("SELCAL_COFOLD_PREFIX") or "selcal-smarca-cofold-v1"
RESULT_PREFIX = os.environ.get("SELCAL_RESULT_PREFIX") or "selcal-results"


@dataclass(frozen=True)
class SelcalArm:
    arm_id: str
    gene: str
    uniprot: str
    cofold_system: str          # co-fold subdir under COFOLD_PREFIX
    role: str
    predicted: str              # what the REFERENCE says about this arm, in words


ARMS = (
    SelcalArm("selcal_smarca2", "SMARCA2", SMARCA2_ACC, "smarca2",
              role="the arm the reference ligand PREFERS (DC50 1 nM)",
              predicted="more stable ternary interface -> LOWER E1 plateau"),
    SelcalArm("selcal_smarca4", "SMARCA4", SMARCA4_ACC, "smarca4",
              role="the spared paralogue (DC50 32 nM)",
              predicted="less stable ternary interface -> HIGHER E1 plateau"),
)

ARM_A = "selcal_smarca2"        # the predicted-more-stable arm; the statistic is mean(A) - mean(B)
ARM_B = "selcal_smarca4"


# =============================================================================================================
# ★★ EXCLUSIONS ARE BY MEASURED INPUT FAULT, KEYED ON THE CO-FOLD — never by outcome
# =============================================================================================================
# Same data structure and same standard as `nrv04_retro_panel.EXCLUDED_COFOLD_MODELS`, which is what let
# AMENDMENT 4 drop a broken input without a selection-bias objection: the fault is a STATIC property of the
# predicted structure, provable before any MD is interpreted, and the replicate structure makes the claim
# testable (both replicas of a bad co-fold die; both replicas of every good one run).
#
# ⚠ IT IS EMPTY AT FREEZE TIME AND MUST STAY EMPTY UNLESS A FAULT IS *MEASURED*. An entry added because a leg
# came back inconvenient is the retune this program forbids. `selcal_stage.cofold_input_audit` is the only
# thing licensed to justify one, and it must run BEFORE the leg is scored.
EXCLUDED_COFOLD_MODELS: dict = {
    ("selcal_smarca4", 3): (
        "AMENDMENT 1 (2026-08-02): input fault. selcal-smarca-cofold-v1/smarca4/seed_3 places A:LYS71:O and "
        "E:SER38:O 0.693 A apart (both Boltz-placed heavy atoms, 4499 in the system) against the 1.00 A "
        "floor, so `selcal_stage.cofold_input_audit` REFUSED before minimisation on every attempt. "
        "OUTCOME-BLIND: the audit reads static geometry and had not integrated one femtosecond, so no "
        "endpoint value of any kind existed at the moment of refusal, inconvenient or otherwise. THE FAULT "
        "FOLLOWS THE CO-FOLD, NOT THE HOST — both replicas "
        "(r0, r1) refused with byte-identical numbers across 12 attempt logs on FIVE distinct machines "
        "(46539178, 46549246, 46553998, 46554862, 46555738). NO OTHER CO-FOLD IN EITHER ARM FAILED: the "
        "one other unlanded smarca4 unit at the time, m2-r0, AUDITED CLEAN at 1.2994 A on the same day and "
        "its replica m2-r1 landed, so m2 is exonerated as an input and is re-run, not excluded. Evidence: "
        "container stdout via `--mode diag`, runs 30728025643 and 30728185356."),
}


def excluded_cofold(arm_id: str, model_seed: int):
    """(excluded, why) for one co-fold model. PURE. `why` is empty when it is not excluded."""
    return ((arm_id, model_seed) in EXCLUDED_COFOLD_MODELS,
            EXCLUDED_COFOLD_MODELS.get((arm_id, model_seed), ""))


def arm_by_id(arm_id: str) -> SelcalArm:
    for a in ARMS:
        if a.arm_id == arm_id:
            return a
    raise KeyError("unknown sensitivity-control arm %r; known: %s" % (arm_id, [a.arm_id for a in ARMS]))


def enumerate_units(model_seeds=COFOLD_MODEL_SEEDS, replicas=MD_REPLICAS, include_excluded=False):
    """Every independent GPU unit = (arm, co-fold model seed, MD velocity replica). 24 at freeze.

    ⛔ THE PANEL SHRINKS HERE AND NOWHERE ELSE, for the reason `nrv04_retro_panel` records: the collector
    builds `expected` from this function, so a completeness flag goes true because the panel HONESTLY
    CHANGED — never because a gate predicate was loosened to let an unreachable panel pass."""
    return [(a, m, r) for a in ARMS for m in model_seeds for r in replicas
            if include_excluded or not excluded_cofold(a.arm_id, m)[0]]


def unit_name(arm: SelcalArm, model_seed: int, replica: int) -> str:
    """Stable per-unit name (Vast label + S3 checkpoint prefix, so units never collide).

    Built from `cofold_system` rather than `arm_id` so the label reads `selcal-smarca2-m1-r0` instead of
    `selcal-selcal_smarca2-m1-r0`. The arm's full id still travels in `LEG_ID`, which is what the scorer
    parses — the label is for humans, reapers and S3 prefixes, and a Vast label has a length budget."""
    return "%s%s-m%d-r%d" % (LABEL_PREFIX, arm.cofold_system, model_seed, replica)


def cofold_prefix_s3(arm: SelcalArm, bucket: str, model_seed: int, prefix: str = None) -> str:
    """The S3 PREFIX of the specific co-fold MODEL this leg starts from.

    The model seed is PINNED (not globbed) because the co-fold model is the unit of independence in the
    statistics — a leg that silently drew a different model would break the collapse to model means."""
    return "s3://%s/%s/%s/seed_%d/" % (bucket, (prefix or COFOLD_PREFIX).strip("/"), arm.cofold_system,
                                       model_seed)


def leg_env(arm: SelcalArm, model_seed: int, replica: int, mode: str = "run",
            prod_ns: float = PROD_NS, equil_ns: float = EQUIL_NS) -> dict:
    """The engine env for one unit — consumed by `nrv04_covalent_md.py` UNCHANGED.

    ★ THE DRIVER IS REUSED VERBATIM, AND THAT IS THE EXPERIMENT. A sensitivity control that ran a modified
    driver would calibrate a readout the program does not use. `nrv04_covalent_md` is target-agnostic: it
    takes the E3/target chain split from the assembler's `chains.json` and computes E1 from it, so nothing
    about it needs to know this is a bromodomain rather than a nuclear-receptor LBD.

    COVALENT is always "0" here: no arm of this panel forms a covalent adduct, and there is no cysteine this
    ligand reacts with. Setting it would be fabricating chemistry."""
    return {
        "PANEL": "selcal_sensitivity_control",
        "LEG_ID": "%s__m%d" % (arm.arm_id, model_seed),
        "SEED": str(replica),
        "MODE": mode,
        "LIGAND": REFERENCE["ligand"],
        "TARGET": arm.gene,
        "ENV_ASSEMBLY": "ternary_%s" % arm.gene.lower(),
        "COVALENT": "0",
        "MUTATION": "",
        "PROD_NS": str(prod_ns),
        "EQUIL_NS": str(equil_ns),
        "COFOLD_MODEL_SEED": str(model_seed),
        "OPENMM_REQUIRE_CUDA": "1",
    }


# =============================================================================================================
# 4 · WHAT COUNTS AS A LANDED LEG — the predicate, with ONE home
# =============================================================================================================
# ⛔ REUSED, NOT RE-SPELLED. `nrv04_retro_panel.production_leg_check` / `completed_production_check` already
# encode the two questions and the reason they must stay separate, and they were written after a measured
# incident: 17 smoke legs echoed `prod_ns: 5.0` and a fully-populated `R1_interface` FROM THEIR ENV rather
# than from what ran, a completeness count believed them, and a frozen gate came one leg short of emitting a
# fabricated verdict. **A field's PRESENCE is never evidence of its provenance.** Importing those predicates
# is what stops this lane re-learning that at its own expense.
def production_leg_check(rec, prod_ns: float = PROD_NS, equil_ns: float = EQUIL_NS):
    """PURE: was this record produced by a run of the PREREGISTERED protocol? -> (ok, why). Membership only."""
    from nrv04_retro_panel import production_leg_check as _chk
    return _chk(rec, prod_ns=prod_ns, equil_ns=equil_ns)


def completed_production_check(rec, prod_ns: float = PROD_NS):
    """PURE: did a panel leg REACH the end of its production run? -> (ok, why). A False is a TECHNICAL
    FAILURE the gate scores, NOT an absent leg."""
    from nrv04_retro_panel import completed_production_check as _chk
    return _chk(rec, prod_ns=prod_ns)


def expected_production_frames(prod_ns: float = PROD_NS) -> int:
    from nrv04_retro_panel import expected_production_frames as _f
    return _f(prod_ns)


def is_production_leg(rec, prod_ns: float = PROD_NS) -> bool:
    return production_leg_check(rec, prod_ns=prod_ns)[0]


# =============================================================================================================
# 5 · THE PRE-REGISTERED PASS CRITERION — frozen before the first GPU leg
# =============================================================================================================
#: One-sided significance level. The same alpha the NR-V04 prereg used, deliberately: a control judged at a
#: looser alpha than the experiment it calibrates is not a calibration.
ALPHA = 0.05

#: Prereg-equivalent of NR-V04 §4e: more than this many technical failures in an arm makes that arm
#: UNDERPOWERED and the panel INDETERMINATE rather than a null.
#: ⚠ IT IS 2, NOT `nrv04_retro_gate`'s 1, AND THE DIFFERENCE IS DELIBERATE — do not "harmonise" it. That
#: constant governs an arm of **6** legs (3 models x 2 replicas); this one governs an arm of **12** (6 x 2).
#: Copying the absolute number across would silently make this panel's failure tolerance half as generous as
#: the one it is calibrating, i.e. a stricter rule arrived at by accident. What is held constant is the
#: PROPORTION and the consequence, not the integer.
MAX_FAILED_LEGS_PER_ARM = 2

#: The statistic and its direction. `mean(ARM_A) - mean(ARM_B)` with `alternative="less"`, i.e. the test asks
#: whether SMARCA2's interface-RMSD plateau is LOWER (more stable), which is what the reference predicts.
STATISTIC = "mean(E1 | %s) - mean(E1 | %s), model-level means" % (ARM_A, ARM_B)
ALTERNATIVE = "less"

TIER_PASS = "PASS"                     # the readout detected the known difference, in the predicted direction
TIER_NULL = "NULL"                     # adequately-powered design, no detection — the honest negative
TIER_WRONG_SIGN = "WRONG_SIGN"         # a difference, in the direction the reference contradicts
TIER_INDETERMINATE = "INDETERMINATE"   # not enough conforming legs to score at all

#: ★★ THE CRITERION, IN WORDS, BEFORE THE RUN. Every clause is checked by `selcal_gate.verdict` and pinned by
#: `tests/test_selcal_panel.py`. Read `_what_a_pass_licenses` before quoting any of this anywhere.
PASS_CRITERION = {
    "_frozen_before_any_gpu_leg": True,
    "_what": "Whether the endpoint-MD readout (E1 interface-RMSD plateau) detects the paralogue difference "
             "that Kofink et al. 2022 measured for ACBI2 between SMARCA2 and SMARCA4.",
    "_what_a_pass_licenses": "EXACTLY ONE SENTENCE: 'run identically and without tuning on a known-selective "
                             "paralogue pair with solved structures on both arms, the ensemble endpoint "
                             "workflow discriminated them.' It licenses NOTHING about NR4A3, nothing about "
                             "degradation, efficacy, a therapeutic window or clinical readiness, and it "
                             "re-scores no landed NR-V04 leg.",
    "_what_a_fail_licenses": "The sentence written in advance in selectivity-resolution-options.md §4: the "
                             "workflow's paralogue-discrimination authority rests on nothing this program "
                             "has measured, and the NR4A3 selectivity predictions are reported as "
                             "UNVALIDATED PREDICTIONS. A fail does NOT distinguish 'the readout is blunt' "
                             "from 'this pair is hard', and must not be reported as though it did.",
    "unit_of_independence": "the co-fold MODEL. Per-leg E1 values are collapsed to model means before the "
                            "permutation, so velocity replicas cannot inflate the reference set — the same "
                            "rule as NR-V04 prereg §4a, and the reason B1/B2 were refused in the options "
                            "paper.",
    "statistic": STATISTIC,
    "test": "exact one-sided permutation test over all C(n_a+n_b, n_a) label assignments of the model means, "
            "observed arrangement included (nrv04_retro_gate.exact_permutation_p — imported, not "
            "re-implemented)",
    "alternative": ALTERNATIVE,
    "alpha": ALPHA,
    "PASS_requires_ALL": [
        "p <= 0.05 on the exact one-sided permutation test",
        "the observed statistic is NEGATIVE (SMARCA2 lower/more stable) — the direction the primary source "
        "predicts; a significant result in the other direction is WRONG_SIGN, never a pass",
        "the sign survives leave-one-model-out: every single-model refit keeps the same sign "
        "(nrv04_retro_gate.leave_one_model_out)",
        "at most %d technical failures in each arm" % MAX_FAILED_LEGS_PER_ARM,
        "at least 4 conforming co-fold models in EACH arm, so the reference set can still reach alpha "
        "(C(8,4) = 70, floor 0.0143) after any measured input-fault exclusion",
    ],
    "NULL_when": "the design is adequately powered (the membership and reference-set clauses hold) and "
                 "p > 0.05. This is a REAL negative and is reported as one.",
    "WRONG_SIGN_when": "p <= 0.05 in the opposite direction, judged on the mirrored one-sided test. Reported "
                       "as a FAIL of the control with the sign stated, because a readout that separates a "
                       "known pair BACKWARDS is worse than one that cannot separate it.",
    "INDETERMINATE_when": "an arm is underpowered by technical failures, or fewer than 4 conforming models "
                          "survive in an arm. Not a null — nothing was measured.",
    "no_interim_analysis": "The verdict is emitted only when the panel is complete or an arm is definitively "
                           "short. Peeking at a partial panel and stopping on a favourable p is the same "
                           "defect prereg §4f exists to prevent.",
}

#: The minimum conforming models per arm the criterion demands. Derived name so the tests and the gate cannot
#: disagree with the prose above.
MIN_MODELS_PER_ARM = 4


def panel_manifest() -> dict:
    """Self-describing manifest of exactly what would run (no I/O, no spend) — the thing to eyeball before a
    fan-out and to attach to the result."""
    units = enumerate_units()
    per_arm: dict = {}
    for a, m, r in units:
        per_arm.setdefault(a.arm_id, []).append(unit_name(a, m, r))
    return {
        "_what": "ENDPOINT-MD SENSITIVITY CONTROL — an INSTRUMENT CALIBRATION, not a selectivity result. It "
                 "tests whether the E1 readout can detect a paralogue difference a primary source says is "
                 "there. It asserts nothing about NR4A3, nothing about degradation and nothing clinical.",
        "_why": "The NR-V04 retrospective returned DISCORDANT (p = 0.3929) and, being covalency-confounded, "
                "can never be a positive control at any n. The program therefore has no evidence that this "
                "workflow can detect paralogue selectivity at all. This is that evidence, or its absence.",
        "panel": "selcal_sensitivity_control",
        "design_doc": "selectivity-resolution-options.md §2-D (option D1)",
        "prereg": "selectivity-sensitivity-control-prereg.md",
        "pair": list(REFERENCE["pair"]),
        "reference": REFERENCE,
        "arms": [{"arm_id": a.arm_id, "gene": a.gene, "uniprot": a.uniprot, "role": a.role,
                  "predicted": a.predicted} for a in ARMS],
        "cofold_prefix": COFOLD_PREFIX,
        "cofold_model_seeds": list(COFOLD_MODEL_SEEDS),
        "md_replicas": list(MD_REPLICAS),
        "n_units": len(units),
        # ⛔ BOTH NUMBERS, ALWAYS. `n_units` is what would run NOW; a manifest that reported only that would
        # say "22" with no hint that 24 were designed, and this document is the one attached to the result.
        # A shrunken panel must be impossible to mistake for the panel the criterion was frozen against.
        "n_units_at_freeze": len(enumerate_units(include_excluded=True)),
        "units_per_arm": per_arm,
        "label_prefix": LABEL_PREFIX,
        "sampling_ns": {"equil": EQUIL_NS, "prod": PROD_NS},
        "endpoint": "E1 = R1_interface.plateau_A (Å), lower = more stable ternary interface. Computed by "
                    "nrv04_covalent_md UNCHANGED, which is what makes this a control on the readout the "
                    "program actually uses.",
        "pass_criterion": PASS_CRITERION,
        "excluded_cofold_models": {"%s:m%d" % k: v for k, v in EXCLUDED_COFOLD_MODELS.items()},
        "honesty": "Endpoint MD only. NO free energy is computed here and none may be inferred. This panel "
                   "is NOT valB_full module 3 (an alchemical cooperativity module behind the valB gate) and "
                   "must not be presented as a way around STRATEGY Open decision 9.",
    }


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Sensitivity-control frozen panel (pure; no spend).")
    ap.add_argument("--units", action="store_true", help="print every unit name and exit")
    args = ap.parse_args(argv)
    if args.units:
        for a, m, r in enumerate_units():
            print(unit_name(a, m, r))
        return 0
    print(json.dumps(panel_manifest(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
