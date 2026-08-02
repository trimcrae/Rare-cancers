#!/usr/bin/env python3
"""RUNG 5b-T — the assembly-route ternary rebuild: its SPEC, its PRE-REGISTERED GATE, and its DERIVED cost.

⛔ THE GATE LIVES HERE, NOT ONLY IN PROSE. A criterion that exists only as a sentence in a plan document is
a criterion that gets re-read charitably after the result is in. Every threshold below is a number this
module emits before the rung runs, so "did it pass?" is a lookup rather than an argument — the same reason
`nrv04_retro_panel.production_leg_check` and the NR-V04 preregistration exist.

★ WHY THIS FILE EXISTS. The ternary rebuild is the program's largest open gap
([STRATEGY.md:500](../../STRATEGY.md): *"the whole remaining gap"*) and it sat **unpriced** — no rung, no
spine row, no decision-value rank — so it could not be scheduled, refused or costed. CLAUDE.md rule 1 says a
total is DERIVED, never typed. This module is that derivation, and `--check` is the checker that verifies it
sums.

⛔ THE ANSWER IS $0 IN GPU DOLLARS, AND THAT IS A MEASUREMENT RATHER THAN AN OPTIMISM. Every step of the
chain runs on CPU:

  * the ternary generator (`V2`, DeepTernary) is run through
    `.github/workflows/selcal-deepternary-headtohead.yml`, which patches `predict_cpu.py`'s hardcoded
    `device = 'cuda'` to `'cpu'` and `SEED_NUM = 40` to `16`, on a GitHub-hosted `ubuntu-latest` runner;
  * the selectivity descriptor (`V1`, `nr4a_ternary_signature.py`) is pure-Python contact-map work;
  * the construct check (`nr4a3_linker_design.py --chem-check`) is RDKit on CPU.

So the rung's reference-GPU-hour count is 0.0 and its dollar cost is 0.0 at ANY planning rate. The planning
rate is still READ (never typed) from the regenerated ladder so the arithmetic is explicit and so a future
reader can see that the pinned ladder total does not move.

⚠ WHAT IS PRICED HERE IS DOLLARS. WALL-CLOCK IS A LOWER BOUND AND SAYS SO. The per-arm seconds below were
measured on SMARCA2(bromodomain)+VHL/EloB/EloC and are used for an NR4A3 LBD (254 residues) against
CRBN/DDB1, which is a materially larger system; DeepTernary's cost grows with total residue count. The
dollar answer is unaffected (a GitHub-hosted runner on a public repository bills nothing), but the derived
minutes are a FLOOR, not an estimate, and the workflow's own `timeout-minutes: 120` is the real bound.

Usage:
    python3 ternary_rebuild_cost.py                # writes research/modalities/ternary-rebuild-cost.json
    python3 ternary_rebuild_cost.py --check        # re-derives and verifies it sums; non-zero on a mismatch
"""
from __future__ import annotations

import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ternary-rebuild-cost.json")
LADDER = os.path.join(HERE, "vast-ladder-repricing.json")

# =============================================================================================================
# THE MEASURED BASIS — per-step seconds read from COMPLETED CI records, never from a live poll
# =============================================================================================================
# ⏱ CLAUDE.md §6: the jobs API lags, and polling a live run manufactures a stall that is not there. Every
# figure below was read from `started_at`/`completed_at` AFTER the step completed.

#: `.github/workflows/selcal-deepternary-headtohead.yml`, the only end-to-end green run of the lane.
#: One positive-control arm (6HAX_B_A_FWZ, inputs shipped in DeepTernary's own output.zip) + one prepared arm
#: (selcal_smarca2), 16 seeds each, job total 144 s.
DT_RUN = {
    "run_id": 30755890247,
    "workflow": ".github/workflows/selcal-deepternary-headtohead.yml",
    "conclusion": "success",
    "runner": "ubuntu-latest (GitHub-hosted) — CPU only; predict_cpu.py device patched 'cuda' -> 'cpu'",
    "seeds_per_arm": 16,
    "job_total_s": 144,
    "steps_s": {
        # once per job, whatever the arm count
        "set_up_job": 1,
        "checkout": 6,
        "setup_python": 0,
        "deps": 19,
        "guards": 1,
        "resolve_chains_and_verify_fragments": 5,
        "clone_deepternary_and_cpu_deps": 50,
        # per positive-control arm (its six input files ship with the model)
        "poscontrol_predict": 19,
        "poscontrol_rescore_with_our_instruments": 6,
        # per prepared arm
        "prep_six_input_files": 2,
        "build_unbound_inputs_native_frame": 2,
        "predict_selcal_arm": 21,
        "score_against_sealed_native": 6,
        # once per job
        "publish": 3,
        "poscontrol_gate": 0,
    },
    "_arms_in_this_run": {"poscontrol": 1, "prepared": 1},
}

#: `.github/workflows/selcal-cofold-validate.yml`, run 30759720183 — the `V1` half of the chain.
#: `nr4a_ternary_signature.py` over 3 arms x 1 model each; and its own known-answer gate.
V1_RUN = {
    "run_id": 30759720183,
    "workflow": ".github/workflows/selcal-cofold-validate.yml",
    "conclusion": "success",
    "steps_s": {
        # the descriptor's known-answer test (`selcal_interface_signature`, SMARCA2 Gln1469<->VCB)
        "static_paralogue_interface_signature": 0,
        # `nr4a_ternary_signature.py` — 3 arms, 1 model per arm
        "ternary_signature_read": 4,
        # RCSB sourcing of the non-native binary inputs, which the E3 side of a prepared arm needs
        "source_non_native_binary_inputs": 40,
    },
    "_models_per_arm_in_this_run": 1,
    "_arms_in_this_run": 3,
}

# =============================================================================================================
# THE UNITS THIS RUNG BUYS
# =============================================================================================================
#: ★ FIVE ARMS, NOT THREE. Three paralogue arms are the deliverable; two are harness positive controls, and
#: dropping them is the failure this lane already paid for once — a near-zero score that cannot be told apart
#: from broken plumbing. 6HAX is VHL/SMARCA2; 6BN7 is the protac22 CRBN entry, and THIS rung's E3 is CRBN, so
#: a VHL-only harness control does not cover the assembly it is used for. Both are inside DeepTernary's
#: 2023-10-14 horizon and therefore control the HARNESS, never generalisation.
POSCONTROL_ARMS = ("6HAX_B_A_FWZ (VHL/SMARCA2, in-set)", "6BN7 (CRBN/BRD4, in-set)")
PARALOGUE_ARMS = ("NR4A1", "NR4A2", "NR4A3")

#: ⛔ ALL 16 SEEDS PER ARM ARE SCORED AND ALL 16 ARE READ BY `V1`. `nr4a_ternary_signature`'s own bar is
#: `MIN_MODELS_FOR_REPRODUCIBILITY = 3`, below which it refuses the word "reproducible" — the earlier pass
#: had 1 model per arm and printed "reproducible across ALL 1 models". 16 clears the bar five times over and
#: costs seconds of free CPU, so there is no reason to take the top 3.
MODELS_PER_ARM_READ = 16
MIN_MODELS_FOR_REPRODUCIBILITY = 3

#: The rung uses no GPU anywhere. This is the number the dollar figure is derived from.
REFERENCE_GPU_H = 0.0

#: A conditional $0 pre-step: re-enumerate at a basin that clears the 12-atom gate. RDKit on CPU. No
#: completed CI record isolates its wall-clock, so it is priced at $0 dollars with wall-clock UNPRICED
#: rather than at an invented number.
PRESTEP_WALL_CLOCK_UNPRICED = (
    "nr4a3_linker_design.py --chem-check re-enumeration at a <=12-atom basin: $0 dollars (RDKit, CPU), "
    "wall-clock UNPRICED — no completed CI record isolates the `nr4a_linker_chem` job's own seconds"
)


# =============================================================================================================
# THE SPEC — what runs, on what inputs, producing which artifact
# =============================================================================================================
#: ⛔ THE DEGRADER'S STRUCTURE IS RECORDED THIS TIME, AND THAT IS THE POINT OF THE WHOLE RUNG.
#: The existing NR4A ternaries are ✕ dead as evidence because their molecule cannot be recovered:
#: `nr4a-ternary-ligand-provenance.json` reports `n_recovered: 0` of 3 arms — no `_chem_comp_bond` loop in any
#: model, so bond orders would have to be perceived from coordinates, and a guessed molecule must never become
#: the input to another run. Every construct in `nr4a3-linker-library-chem.json` carries a `canonical_smiles`
#: AND an `inchikey`, RDKit-verified 54/54. The rung takes its degrader from there and from nowhere else.
DEGRADER_SOURCE = {
    "artifact": "research/modalities/nr4a3-linker-library-chem.json",
    "fields": ["constructs[].construct_id", "constructs[].canonical_smiles", "constructs[].inchikey",
               "constructs[].n_backbone_atoms_measured"],
    "why": ("the §2.5 ternaries are unrecoverable — nr4a-ternary-ligand-provenance.json n_recovered = 0 of 3, "
            "no `_chem_comp_bond` loop in any model — so a replicate can never be matched to them. Recording "
            "the SMILES is what makes this rung's output replicable at all."),
    "e3_arm_required": "crbn",
    "shortest_committed_backbone_atoms": 14,
    #: ⚠ ELECTROPHILE-BEARING ONLY. Six committed CRBN constructs sit at the shortest length; two of them
    #: (`..._none`) carry no pendant, so they cannot present a covalent handle at C397 and are not candidates
    #: for THIS rung whatever their length.
    "crbn_constructs_at_the_shortest_length_bearing_an_electrophile": [
        "crbnM0@ex_5amide_a2-a5_acrylamide", "crbnM0@ex_5amide_a2-a5_cyac_me",
        "crbnM0@ex_5amide_a2-a5_cyanoprop", "crbnM0@ex_5amide_a2-m2_cyac_me",
    ],
}

#: The six DeepTernary input slots, and the committed source of each. Nothing is invented and nothing is
#: fetched that the repo does not already know how to fetch.
INPUT_SLOTS = [
    {"slot": "unbound_protein1 (site 1)", "source": "results/nr4a3-matrix/nr4a{1,2,3}-opened.pdb",
     "note": "the matched opened LBD per paralogue — the same three the categorical lane measured on"},
    {"slot": "unbound_lig1 (site 1 fragment)", "source": "results/nr4a3-matrix/docked_nr4a{1,2,3}.sdf",
     "note": "⛔ INHERITS `R5`. The pose's own known-answer test (`V3`) is INCONCLUSIVE — the pipeline's SITE "
             "selection missed on 6 of 6 pairs — so every geometry downstream of this slot is conditional."},
    {"slot": "unbound_protein2 (site 2)", "source": "a CRBN+DDB1 BINARY IMiD deposit (e.g. 4TZ4)",
     "note": "⚠ the committed `nr4a3-e3-arm-registry.json` CRBN arm is staged on 6BOY, which is a TERNARY "
             "(DDB1-CRBN-BRD4/dBET6). A ternary-derived E3 conformer imports that ternary's induced fit, so "
             "site 2 is re-staged from a binary or the ternary provenance is declared on the result."},
    {"slot": "unbound_lig2 (site 2 fragment)", "source": "the IMiD of the same deposit, in its crystal pose",
     "note": "CIF->PDB conversion must source CONECT from the CCD `_chem_comp_bond` table, never from "
             "distances — the lane already does this and it is why its molecules are recoverable."},
    {"slot": "ligand.pdb (the degrader)", "source": DEGRADER_SOURCE["artifact"],
     "note": "a constrained embed of the recorded SMILES, with its warhead atoms pinned on the site-1 "
             "fragment and its IMiD atoms on the site-2 fragment, in one common frame."},
    {"slot": "the common frame", "source": "research/modalities/nr4a3-orientation-basins.json",
     "note": "⛔ THERE IS NO NATIVE NR4A3 TERNARY, so the published protocol's 'superpose both binaries into "
             "the native frame' step has no reference to use. The RUNG-5a orientation basin supplies a "
             "relative arrangement instead. It does NOT leak into the prediction — `predict_one_unbound` "
             "randomly rotates and translates protein 2 and the ligand before the forward pass — but it does "
             "decide whether the two-fragment embed is feasible at all."},
]

#: The pre-flight assertion that stops the failure this lane already paid two dead runs for.
PREFLIGHT = {
    "snap_masks_must_be_non_empty": True,
    "why": ("runs 30753431082 and 30754028742 died at `replace_to_unbound_coords` because the degrader was a "
            "CCD ideal conformer in an arbitrary frame, so ZERO atoms fell within 1 A of either fragment and "
            "the reduction over an empty mask raised. The reference construction gives 33 and 18. A build "
            "whose masks are empty is REFUSED before prediction, never run 'to see'."),
    "reference_masks": {"unbound_lig1": 33, "unbound_lig2": 18, "on": "6HAX_B_A_FWZ"},
}

# =============================================================================================================
# THE PRE-REGISTERED GATE — written before the rung runs, three arms, all three needed for GO
# =============================================================================================================
GATE = {
    "_registered": "2026-08-02, before any arm of this rung has been run",
    "_all_three_arms_must_pass": True,
    "A_sequence_encoded_not_a_placement_artifact": {
        "criterion": ("at least one discriminating position at which the ALIGNED RESIDUE ITSELF differs in "
                      "both NR4A1 and NR4A2"),
        "threshold": {"min_sequence_encoded_positions": 1},
        "why": ("the earlier pass returned 6 discriminating positions and 5 were placement artifacts — the "
                "IDENTICAL residue in all three paralogues, so they cannot encode a paralogue difference. "
                "`nr4a_ternary_signature` already partitions them; this arm makes the partition the gate."),
        "reading_if_it_fails": ("any number of same-residue positions is ZERO evidence of selectivity, and a "
                                "count of 'discriminating contacts' that includes them must never be quoted"),
    },
    "B_reproducible_not_one_models_accident": {
        "criterion": ("the position is present in >= 12 of 16 NR4A3 models AND in <= 4 of 16 models on EACH "
                      "comparator arm"),
        "threshold": {"models_per_arm": 16, "min_present_on_focus": 12, "max_present_on_each_comparator": 4},
        "null": ("a per-model independent coin flip (p0 = 0.5). Under it, >= 12 of 16 has one-sided binomial "
                 "p = 0.0384, and <= 4 of 16 has the mirror p = 0.0384."),
        "floor": ("fewer than 3 models on any arm and `nr4a_ternary_signature` refuses the word "
                  "'reproducible' outright — the earlier pass had 1 model per arm and printed 'reproducible "
                  "across ALL 1 models', which is n = 1 wearing the costume of a replication test"),
        "reading_if_between": ("INDETERMINATE, which is a third outcome and NOT a pass. The descriptor "
                               "result is then not established in either direction."),
    },
    "C_the_geometry_the_categorical_axis_depends_on_survives_assembly": {
        "criterion": ("in the accepted NR4A3 models, (C1) the median electrophile-carbon-to-C397-SG distance "
                      "is within the pendant-reach convention the construct was designed at, and (C2) the "
                      "construct's own backbone length still lies inside the assembled placement's C397 "
                      "chemoselectivity window — i.e. short of the first PARALOGUE cysteine to come into "
                      "reach"),
        "reads": ["research/modalities/nr4a3-linker-covalent-reach.json -> "
                  "★_family_wide_chemoselectivity_window.by_convention[*].cells[*] (window_lo, window_hi, "
                  "closed_by, closed_at_atoms)",
                  "research/modalities/nr4a-paralogue-dynamics.json -> categorical_verdict.by_scope"],
        "why": ("the categorical axis is what makes this candidate selective WITHOUT a validated free-energy "
                "instrument, and it is a function of tether length: on the landed 73,867-placement matched "
                "ensembles the raw-reach paralogue-collision probability climbs steeply with backbone atoms. "
                "A ternary that only assembles by effectively lengthening the tether past that knee has "
                "traded away the property it exists to exploit."),
        "reading_if_it_fails": "⛔ NO-GO, not a caveat. The assembled ternary is not the candidate's ternary.",
        "known_risk_registered_in_advance": (
            "⚠ THIS ARM IS AT RISK BEFORE THE RUNG RUNS, and saying so afterwards would be worthless. No "
            "construct in the committed 54-member library sits at or below 12 backbone atoms — the shortest "
            "is 14 — and the only CRBN basin in the CONFIRMED set (`crbn|M0`) has an exact C397 requirement "
            "of 13 backbone atoms, so it MISSES the 12-atom gate by construction. The CRBN basin that does "
            "clear it (`crbn|M17`, 12 atoms) is not in CONFIRMED, so nothing was ever enumerated against it. "
            "A $0 RDKit re-enumeration is the named way out; if it returns nothing buildable, the rung runs "
            "at 14 and CARRIES the measured collision bracket rather than claiming the 12-atom number."),
    },
    "STOP_conditions_that_are_refusals_not_results": [
        "empty snap mask or an infeasible two-fragment embed -> REFUSED. An unrun arm is never reported as a "
        "zero; both scorers already refuse this and say so.",
        "either harness positive control fails -> the whole run is uninterpretable and the workflow already "
        "goes red on it. A harness that cannot score a known-good ternary cannot grade a suspect one.",
        "fewer than 3 models on any arm -> no reproducibility statement is made in either direction.",
    ],
}

#: ⛔ WHAT A PASS WOULD AND WOULD NOT LICENSE. Stated with the gate, not after the result.
SCOPE = {
    "a_pass_licenses": [
        "a STRUCTURAL statement: these modelled interface contacts differ between the paralogues, at named "
        "positions, with a stated per-model frequency and a validated detector behind the descriptor.",
        "combined with the landed categorical axis (geometry + exposure, measured over matched ensembles), a "
        "TWO-MECHANISM structural case — selective engagement plus a paralogue-discriminating interface — "
        "which is materially stronger than either half alone.",
    ],
    "a_pass_does_NOT_license": [
        "any affinity, potency or N-fold statement. This rung computes no free energy and contains no "
        "thermodynamics; it cannot say one paralogue binds more tightly than another.",
        "discharging `R12` or the free-energy requirement. `R12` needs productive unique-lysine geometry and "
        "`V18` has no known-answer test at all; nothing here touches either.",
        "a degradation, efficacy, safety, therapeutic-window or clinical claim of any kind.",
        "calling the arm blind. DeepTernary is GIVEN which pocket each end of the degrader occupies, and a "
        "test in the lane enforces that this is never described otherwise.",
        "generalisation from the harness controls. 6HAX and 6BN7 are both inside the model's 2023-10-14 "
        "horizon, so they control the harness and the instruments and never the model's reach.",
    ],
    "inherited_limits_that_travel_with_every_result": [
        "`R5` is UNRESOLVED and site 1 inherits it: `V3`'s verdict is INCONCLUSIVE because the pipeline's "
        "site selection missed on 6 of 6 pairs, so the warhead sub-pose is conditional.",
        "`V1` validates ONE contact in ONE pair (SMARCA2 Gln1469<->VCB). It does not validate the "
        "interface-stability endpoint and it makes no NR4A prediction correct.",
        "`V2`'s post-horizon pass is ONE arm on a VHL/bromodomain system, best of 16 seeds with median 0.442; "
        "the SMARCA4 arm was refused and no SMARCA4 number exists. Nothing validates it on a CRBN ternary "
        "with a nuclear receptor, which is exactly what this rung assembles.",
        "every structure here is an isolated LBD construct — `R13`, the fusion-context object, is untouched.",
        "the exposure half of the categorical axis is adjudicated by `V17`'s EXPOSED_RSA = 0.25, which FAILS "
        "its own positive control (NR4A1 C551, RSA 0.165, 0 of 25 frames). Exposure-filtered paralogue "
        "collision probabilities of exactly 0 are therefore conditional on a cutoff known to under-call "
        "paralogue cysteines — in the direction that flatters the claim. The RAW-REACH constraint is the one "
        "that does not lean on it, which is why arm C is written on backbone length.",
    ],
}


def _once_per_job_s(steps):
    keys = ("set_up_job", "checkout", "setup_python", "deps", "guards",
            "resolve_chains_and_verify_fragments", "clone_deepternary_and_cpu_deps",
            "publish", "poscontrol_gate")
    return sum(steps[k] for k in keys)


def measured_unit_seconds():
    """Per-arm marginal seconds, backed out of the completed record — not assumed."""
    s = DT_RUN["steps_s"]
    poscontrol_arm_s = s["poscontrol_predict"] + s["poscontrol_rescore_with_our_instruments"]
    prepared_arm_s = (s["prep_six_input_files"] + s["build_unbound_inputs_native_frame"]
                      + s["predict_selcal_arm"] + s["score_against_sealed_native"])
    return {
        "fixed_per_job_s": _once_per_job_s(s),
        "poscontrol_arm_s": poscontrol_arm_s,
        "prepared_arm_s": prepared_arm_s,
        "_prepared_arm_also_needs_rcsb_source_s": V1_RUN["steps_s"]["source_non_native_binary_inputs"],
    }


def reconciliation():
    """★ THE CHECK THAT THE BASIS SUMS. Per-arm + fixed must reproduce the measured job total.

    A residual is expected and bounded: the API reports whole seconds per step, and 18 steps of independent
    rounding cannot sum exactly to the job's own start/finish delta. A residual outside the bound means the
    per-step attribution above is wrong, not that the run was slow.
    """
    u = measured_unit_seconds()
    a = DT_RUN["_arms_in_this_run"]
    derived = (u["fixed_per_job_s"]
               + a["poscontrol"] * u["poscontrol_arm_s"]
               + a["prepared"] * u["prepared_arm_s"])
    residual = DT_RUN["job_total_s"] - derived
    bound = len(DT_RUN["steps_s"]) // 3          # ~1 s of rounding per 3 steps; 5 s at 15 steps
    return {
        "derived_s": derived,
        "measured_job_total_s": DT_RUN["job_total_s"],
        "residual_s": residual,
        "residual_bound_s": bound,
        "sums": abs(residual) <= bound,
        "_why_a_residual_is_expected": (
            "the Actions API reports whole seconds per step; %d independently-rounded steps cannot sum "
            "exactly to the job's own start/finish delta" % len(DT_RUN["steps_s"])),
    }


def plan_rate():
    """The planning rate, READ from the regenerated ladder — never typed here (CLAUDE.md rule 1)."""
    try:
        with open(LADDER) as f:
            d = json.load(f)
    except (OSError, ValueError) as exc:
        return {"read": False, "why": "%s unreadable: %s" % (os.path.basename(LADDER), exc)}
    return {
        "read": True,
        "source": "research/modalities/vast-ladder-repricing.json (vast_cost_model.py)",
        "plan_usd_per_reference_gpu_h": d.get("plan_usd_per_reference_gpu_h"),
        "range_usd_per_reference_gpu_h": d.get("range_usd_per_reference_gpu_h"),
        "ladder_total_plan_usd_before_this_rung": d.get("total_plan_usd"),
    }


def derive():
    u = measured_unit_seconds()
    n_pos, n_par = len(POSCONTROL_ARMS), len(PARALOGUE_ARMS)

    v1_per_arm_per_model_s = (V1_RUN["steps_s"]["ternary_signature_read"]
                              / (V1_RUN["_arms_in_this_run"] * V1_RUN["_models_per_arm_in_this_run"]))
    v1_read_s = v1_per_arm_per_model_s * n_par * MODELS_PER_ARM_READ

    generator_s = (u["fixed_per_job_s"]
                   + n_pos * u["poscontrol_arm_s"]
                   + n_par * (u["prepared_arm_s"] + u["_prepared_arm_also_needs_rcsb_source_s"]))
    total_s = generator_s + v1_read_s

    rate = plan_rate()
    r = rate.get("plan_usd_per_reference_gpu_h")
    rng = rate.get("range_usd_per_reference_gpu_h") or [None, None]
    usd = None if r is None else REFERENCE_GPU_H * r
    usd_range = [None if x is None else REFERENCE_GPU_H * x for x in rng]

    rec = reconciliation()
    return {
        "_what": ("RUNG 5b-T — the assembly-route ternary rebuild, priced bottom-up from the DeepTernary "
                  "lane's own completed CI records. DERIVED; regenerate rather than quote."),
        "_status": ("COST AND GATE ONLY. Nothing here dispatches anything, and nothing here is a claim "
                    "about binding, degradation, selectivity, efficacy or safety."),
        "serves": {"requirements": ["R9", "R10", "R11"], "instruments": ["V2", "V1"],
                   "inherits_unresolved": ["R5"],
                   "does_not_discharge": ["R12", "R13", "R6", "R7 (the free-energy requirement)"]},
        "spec": {
            "what_runs": [
                "1. `nr4a3_linker_design.py --chem-check` (CONDITIONAL, $0 RDKit) — re-enumerate at a basin "
                "that clears the 12-atom gate; if nothing is buildable, proceed at the shortest committed "
                "length and carry the measured collision bracket.",
                "2. `selcal_deepternary_frame.py` — build DeepTernary's six unbound inputs per arm from the "
                "slots below, with the pre-flight snap-mask assertion.",
                "3. `predict_cpu.py` (DeepTernary, frozen commit, patched to CPU, 16 seeds) — 2 harness "
                "positive-control arms then 3 paralogue arms.",
                "4. `selcal_deepternary_score.py` / `selcal_deepternary_poscontrol.py` — score every pose "
                "with OUR two instruments against the same references.",
                "5. `nr4a_ternary_signature.py --root <models> --recursive` — the `V1` read over all 16 "
                "models per paralogue arm.",
            ],
            "input_slots": INPUT_SLOTS,
            "degrader_source": DEGRADER_SOURCE,
            "preflight": PREFLIGHT,
            "artifacts_produced": [
                "research/modalities/selcal-deepternary-poscontrol.json (the two harness controls)",
                "research/modalities/selcal-deepternary-frame.json (the built inputs + snap masks)",
                "research/modalities/nr4a-ternary-signature.json (the `V1` read, with per-model frequencies)",
                "research/modalities/nr4a-ternary-ligand-provenance.json (⛔ must come back n_recovered = 3)",
            ],
        },
        "gate": GATE,
        "scope": SCOPE,
        "measured_basis": {"generator": DT_RUN, "descriptor": V1_RUN},
        "unit_seconds": u,
        "basis_reconciliation": rec,
        "units": {
            "poscontrol_arms": list(POSCONTROL_ARMS),
            "paralogue_arms": list(PARALOGUE_ARMS),
            "seeds_per_arm": DT_RUN["seeds_per_arm"],
            "models_per_arm_read_by_V1": MODELS_PER_ARM_READ,
            "min_models_for_reproducibility": MIN_MODELS_FOR_REPRODUCIBILITY,
            "predicted_complexes": (n_pos + n_par) * DT_RUN["seeds_per_arm"],
        },
        "derived_wall_clock": {
            "generator_s": round(generator_s, 1),
            "v1_read_s": round(v1_read_s, 1),
            "total_s": round(total_s, 1),
            "total_min": round(total_s / 60.0, 1),
            "_is_a_floor_not_an_estimate": (
                "a FLOOR: the per-arm seconds were measured on a bromodomain+VCB system and are applied to an "
                "NR4A3 LBD (254 residues) against CRBN/DDB1, which is larger; DeepTernary's cost grows "
                "with total residue count. The workflow's own timeout-minutes: 120 is the real bound."),
        },
        "derived_cost": {
            "reference_gpu_h": REFERENCE_GPU_H,
            "plan_rate": rate,
            "usd_plan": usd,
            "usd_range": usd_range,
            "_derivation": "reference_gpu_h x plan_usd_per_reference_gpu_h = %s x %s = %s"
                           % (REFERENCE_GPU_H, r, usd),
            "_why_zero": ("no GPU appears anywhere in the chain: the generator is patched to CPU, the "
                          "descriptor is pure-Python contact maps, and the construct check is RDKit. A "
                          "GitHub-hosted runner on a public repository bills nothing."),
            "ladder_total_unchanged": True,
            "_ladder_consequence": ("this rung buys 0.0 reference GPU-hours, so the pinned ladder total "
                                    "and every cumulative figure downstream of it are unmoved. It adds a "
                                    "row to the plan and nothing to the spend."),
        },
        "unpriced": [
            PRESTEP_WALL_CLOCK_UNPRICED,
            ("the FALLBACK if the two-fragment constrained embed proves infeasible in the chosen frame: the "
             "only other route to a ternary here is generative (sequence-only co-folding is `V12`, PARKED "
             "and failing), and no completed run on this system gives it a basis. UNPRICED, and it is a "
             "different rung if it is ever needed."),
        ],
        "_provenance": ("every second above was read from a COMPLETED job record via the public Actions API "
                        "(CLAUDE.md §6: never time a step from a live poll)."),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Derive RUNG 5b-T's cost from measured CI records ($0).")
    ap.add_argument("--check", action="store_true",
                    help="re-derive and verify the basis sums; exit non-zero if it does not")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)

    doc = derive()
    rec = doc["basis_reconciliation"]
    if a.check:
        ok = rec["sums"] and doc["derived_cost"]["reference_gpu_h"] == 0.0
        print("basis: derived %s s vs measured %s s (residual %s s, bound %s) -> %s"
              % (rec["derived_s"], rec["measured_job_total_s"], rec["residual_s"],
                 rec["residual_bound_s"], "SUMS" if rec["sums"] else "DOES NOT SUM"))
        print("cost : %s reference GPU-h -> $%.2f (plan rate %s)"
              % (doc["derived_cost"]["reference_gpu_h"],
                 doc["derived_cost"]["usd_plan"] or 0.0,
                 doc["derived_cost"]["plan_rate"].get("plan_usd_per_reference_gpu_h")))
        return 0 if ok else 1

    with open(a.out, "w") as f:
        json.dump(doc, f, indent=1)
    print("wrote %s" % a.out)
    print("derived: %s min of free CPU (a FLOOR), %s reference GPU-h, $%.2f"
          % (doc["derived_wall_clock"]["total_min"], doc["derived_cost"]["reference_gpu_h"],
             doc["derived_cost"]["usd_plan"] or 0.0))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
