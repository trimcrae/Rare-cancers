#!/usr/bin/env python3
"""
NR4A3 screen instantiation of the corrected allocate/certify architecture (2026-07-12).

This is the "set it up properly on our actual problem" layer. It does NOT reinvent an optimizer: SCHEDULING is
delegated to a maintained library (see nr4a3_scheduler.py — Optuna successive-halving/Hyperband for our fixed
congeneric candidate set; continuous multi-fidelity BO à la Ax/BoTorch is the right tool only if/when we move
to a GENERATIVE candidate space, not for a fixed 19-compound set). CERTIFICATION is the one genuinely novel
piece (adaptive_certify.py) and is what this module binds to the real NR4A3 quantities:

  * the real congeneric candidate set (congeneric-warhead-series.json, anchor zaienne_cmpd19),
  * the real multi-fidelity rung ladder (docking -> binary RBFE -> paralogue RBFE -> ternary-pilot ->
    ternary-terminal), with only the TERMINAL rung allowed to certify,
  * the two anti-target margins NR4A3-NR4A1 and NR4A3-NR4A2 as a NONCOMPENSATORY vector (both must clear),
  * certification thresholds mapped onto the PRE-REGISTERED frozen criteria in
    nr4a3-ternary-coop-prereg.json (RT at 298.15 K; the family-transfer "each_difference_min_kcal",
    "each_difference_interval_pct_excludes_zero", "joint_prob_nr4a1_best_min", and pose/conformer-sensitivity
    survival), so nothing here is a new invented bar.

HARD PRECONDITION: the NR-V04 retrospective control (prereg §3 retrospective_bar) must PASS before any
prospective certification is trusted — bias, not variance, is the dominant risk (see the design doc §12 bias
result), and only the retrospective calibration controls it. OFFLINE until that + the stress suite + a
code-level review are complete.

Pure stdlib. Domain data + certification wiring only.
"""
from __future__ import annotations

import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
RT_298 = 0.5924849                                  # kcal/mol at 298.15 K (frozen in the prereg)

# ---- the real NR4A3 multi-fidelity rung ladder --------------------------------------------------------------
# cost_usd is a spot-GPU order-of-magnitude per candidate (design doc §3); fidelity is ordinal. SAMPLING LENGTH
# IS ITSELF A FIDELITY KNOB (trimcrae, 2026-07-12): early rungs run SHORT sampling for cheap triage (a candidate
# that can't even show NR4A3 preference dies on a short run), and full field-standard sampling is reserved for
# candidates that earn it. `sampling_ns` = production ns/window; `replicas` = independent replicas. Only the
# terminal rung may CERTIFY (fix 1.4: the ternary-pilot promotes, it does not declare), and it MUST use the
# FULL field-standard suite — so any candidate published as a wet-lab candidate has, by construction, the full
# 5 ns x 3 replicas x 3 paralogues, never a short triage run.
FULL_SUITE_SAMPLING_NS = 5.0                        # OpenFE/FEP+ field standard for RBFE production/window
RUNGS = [
    {"rung": 0, "name": "prior_dock",      "measures": "geometry + cheap selectivity prior", "cost_usd": 0.0,
     "sampling_ns": None, "replicas": 0, "can_certify": False,
     "note": "ensemble/consensus docking + IFP divergence over divergent residues + co-fold triage "
             "(feasibility filter only) + linker-strain/Lys scan"},
    {"rung": 1, "name": "binary_rbfe",     "measures": "NR4A3 engagement, validity",         "cost_usd": 10,
     "sampling_ns": 2.0, "replicas": 1, "can_certify": False, "note": "SHORT 2 ns triage, NR4A3, 1 conformer"},
    {"rung": 2, "name": "binary_rbfe_rep", "measures": "tightened NR4A3 ΔΔG_bind",           "cost_usd": 30,
     "sampling_ns": 2.0, "replicas": 3, "can_certify": False, "note": "2 ns x 3 replicas + conformer panel"},
    {"rung": 3, "name": "paralogue_rbfe",  "measures": "binary paralogue preference",        "cost_usd": 80,
     "sampling_ns": 3.0, "replicas": 2, "can_certify": False,
     "note": "3 ns, matched NR4A1 + NR4A2 conformers — first selectivity signal"},
    {"rung": 4, "name": "ternary_pilot",   "measures": "first ΔΔG_coop (PROMOTE only)",      "cost_usd": 120,
     "sampling_ns": 2.0, "replicas": 1, "can_certify": False,
     "note": "SHORT ternary, NR4A3 + key paralogue, VHL — MAY PROMOTE, MAY NOT DECLARE"},
    {"rung": 5, "name": "ternary_terminal", "measures": "certifiable ΔΔG_coop selectivity",  "cost_usd": 500,
     "sampling_ns": FULL_SUITE_SAMPLING_NS, "replicas": 3, "can_certify": True,
     "note": "FULL SUITE: 5 ns x >=3 independent replicas x 3 paralogues + geometry — the ONLY certifying rung"},
]
TERMINAL_RUNG = max(r["rung"] for r in RUNGS if r["can_certify"])
# invariant: every certifying rung runs the full field-standard sampling (no certifying on a short triage run)
assert all(r["sampling_ns"] == FULL_SUITE_SAMPLING_NS for r in RUNGS if r["can_certify"])

# ---- certification config, mapped onto the prereg's frozen family-transfer criteria -------------------------
# Selectivity is a VECTOR of per-paralogue margins (kcal/mol of relative ternary stability, NR4A3 favored).
# Both must clear simultaneously (noncompensatory). Thresholds reference the prereg; values marked PROVISIONAL
# are finalized during the retrospective calibration, NOT invented here.
ANTI_TARGETS = ("NR4A1", "NR4A2")                   # NR4A3 must be favored over BOTH
CERT = {
    "targets": ANTI_TARGETS,
    "bar_kcal": None,                               # := prereg family_transfer "each_difference_min_kcal"
    "robustness_kcal": 0.5,                         # PROVISIONAL model-uncertainty margin above the bar
    "delta_total": 0.05,                            # PRE-DECLARED campaign-wide false-declaration budget
    "min_independent_replicas": 3,                  # distinct seeds AND starting poses/states, not one parent
    "require_terminal": True,
    "interval_excludes_zero": True,                 # prereg: each difference's CI must exclude zero
    "survives_pose_and_conformer_sensitivity": True,  # prereg: ranking robust to starting pose + conformer
    "cofold_role": "architecture_feasibility_filter_only",  # NOT a favorable score (epimer control forbids it)
    "full_suite_sampling_ns": FULL_SUITE_SAMPLING_NS,  # a wet-lab-publishable candidate MUST have the full suite;
                                                       # short-sampling triage rungs can PROMOTE/kill but never certify
}

# ---- NR-V04 retrospective precondition (bias control) -------------------------------------------------------
CALIBRATION_GATE = {
    "control": "NR-V04 (Wang 2024) — degrades NR4A1, not NR4A2/NR4A3",
    "must_pass_before_prospective_certification": True,
    "prereg_ref": "nr4a3-ternary-coop-prereg.json -> retrospective_bar",
    "freeze_prior_before_unmasking": True,
    "controls": ["active NR-V04", "inactive Hyp epimer", "matched null / nonselective", "near-negatives"],
    "adversarial": ["paralogue-label swaps", "shuffled divergent-residue masks", "leave-one-control-out"],
}

OFFLINE = True                                      # do not wire to the live fleet (design doc §13 disposition)


def load_candidates(path: str | None = None) -> list:
    """The real fixed congeneric candidate set (anchor + enumerated analogs). Returns list of dicts with id +
    class. Falls back to the known ids if the JSON is unavailable."""
    path = path or os.path.join(_HERE, "congeneric-warhead-series.json")
    try:
        d = json.load(open(path))
        cands = [{"id": d["anchor"]["id"], "class": "anchor"}]
        cands += [{"id": c["id"], "class": c.get("class")} for c in d.get("compounds", [])]
        return cands
    except (OSError, KeyError, json.JSONDecodeError):
        return [{"id": "zaienne_cmpd19", "class": "anchor"}]


def prereg_bar_kcal(path: str | None = None) -> float | None:
    """Read the certification bar from the prereg's frozen family-transfer criterion (each_difference_min_kcal).
    Returns None if not yet frozen there (then the bar must be set during calibration, never guessed)."""
    path = path or os.path.join(_HERE, "nr4a3-ternary-coop-prereg.json")
    try:
        d = json.load(open(path))
        ft = d.get("retrospective_bar", {}).get("nr4a_family_transfer", {})
        return ft.get("each_difference_min_kcal")
    except (OSError, json.JSONDecodeError):
        return None


def build_config() -> dict:
    """Assemble the offline screen config, pulling the certification bar from the prereg (not invented)."""
    cert = dict(CERT)
    cert["bar_kcal"] = prereg_bar_kcal()
    return {
        "offline": OFFLINE,
        "rungs": RUNGS,
        "terminal_rung": TERMINAL_RUNG,
        "candidates": load_candidates(),
        "certification": cert,
        "calibration_gate": CALIBRATION_GATE,
        "claim_ceiling": "computationally qualified NR4A3-selectivity candidate (NOT a selective degrader)",
        "scheduling": "delegated to a maintained library (Optuna successive-halving); see nr4a3_scheduler.py",
        "RT_kcal_per_mol": RT_298,
    }


if __name__ == "__main__":
    import pprint
    pprint.pp(build_config())
