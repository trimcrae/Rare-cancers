#!/usr/bin/env python3
"""
CONGENERIC RBFE PERTURBATION-MAP GENERATOR for the NR4A3 warhead campaign (ternary-first strategy).

WHAT THIS IS. A pure-stdlib, CPU-only DESIGN generator. It reads the two frozen inputs
    congeneric-warhead-series.json   (the 19 enumerated congeneric warhead NODES)
    nr4a3-conformer-panel.json       (the frozen receptor-state AXIS: design/validation/stress + anti-targets)
and EMITS
    congeneric-rbfe-map.json         (the machine-readable relative-binding-free-energy perturbation map).

It does NOT run MD, docking, FEP, GPU, AWS, or the network. It asserts NO affinities, NO ΔΔG values, NO
GPU-hours, NO convergence. Every energetic/cost quantity in the emitted map is a placeholder marked
"TBD — calibrate from the pilot". The abort thresholds are PRE-REGISTERED design parameters (decided a
priori), not measurements.

WHY RBFE (not ABFE) is the primary tool here (strategy: nr4a3-degrader-strategy-ternary-first.md §2). Within a
congeneric series the affinity DIFFERENCE between two analogues sharing a binding-mode-preserving core is a
small alchemical morph with the shared scaffold cancelling by construction — far more tractable and lower
variance than absolute binding of unrelated scaffolds. So the map is a GRAPH whose nodes are congeneric
analogues and whose edges are single-site perturbations that keep the common binding mode.

MAP TOPOLOGY (the science — see the accompanying spec nr4a3-congeneric-rbfe-plan.md).
  * exit_vector_sub class -> a STAR (hub-and-spoke) from the anchor (compound 19, 5-Br) to each 5-substituent.
    Small single-site 5-position swaps; the well-behaved backbone of the map. (microstate_variant 5-NHAc rides
    this 5-position star too.)
  * bioisostere class -> a SECOND star from the anchor varying the SAR-critical 3-carboxylate. FLAGGED
    higher-risk for the common-mode assumption: every bioisostere edge is needs_pose_revalidation=true (an
    endpoint pose check, not RBFE alone). (microstate_variant 3-CO2H / 3-CH2OH ride this 3-position star.)
  * a few explicit CYCLE-CLOSURE edges (closed loops of >=3 edges whose ΔΔG must sum to ~0) as an internal
    consistency/convergence check. Each closing edge is itself a SINGLE-site change (not a double mutation).
  * NO cross-class double-mutation edges (two simultaneous changes break common-mode). The denovo_401
    comparators are a SEPARATE, non-congeneric scaffold: they get ABFE (absolute) as secondary calibration,
    NOT RBFE edges into the indole series. Recorded explicitly.

RECEPTOR-STATE AXIS per edge. Pilot runs on ONE nr4a3_design frame. The fleet runs each edge on the
nr4a3_validation panel (held-out 8XTT + release held-out) + matched nr4a1_antitarget + nr4a2_antitarget
frames. Frames are referenced by PANEL ROLE (not fixed indices — indices resolve at panel-build time via the
panel's selection_rules / pocket_tracking.py). Per-edge selectivity readout = ΔΔG_bind(NR4A3 frame) −
ΔΔG_bind(paralogue frame); rank by the WORST conformer and apply the existing |receptor effect| > |conformer
effect| criterion. The per-(receptor, conformer) endpoints feed ensemble_robust_score.py (robust_score /
beats_benchmark / advancement_verdict) — this map does NOT introduce a new scorer.

MICROSTATES. The 7 microstate_ambiguous compounds carry SEPARATE legs per dominant species at pH 7.4 (both
members of an ambiguous pair), so a protonation flip cannot silently move ΔΔG. Charge-changing legs are
flagged so the pipeline applies the appropriate co-alchemical / analytical correction.

POSE UNCERTAINTY. Compound 19 has NO solved NR4A3 pose (functional target engagement only), so the
5-position exit-vector attachment is a HYPOTHESIS. The map therefore treats the binding pose as an ENSEMBLE
input (run across the conformer frames) and does NOT assume a single fixed pose — a first-class caveat in
both this JSON and the spec.

PURITY. stdlib only (json/os/sys + a hand-rolled SMILES heavy-atom counter). Unit-tested in
tests/test_rbfe_map.py without any chemistry/MD stack.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES_PATH = os.path.join(HERE, "congeneric-warhead-series.json")
PANEL_PATH = os.path.join(HERE, "nr4a3-conformer-panel.json")
OUT_PATH = os.path.join(HERE, "congeneric-rbfe-map.json")

MAP_VERSION = "1.0.0"
ANCHOR_ID = "zaienne_cmpd19"
TARGET = "nr4a3"
PARALOGUES = ("nr4a1", "nr4a2")

# ---------------------------------------------------------------------------
# receptor-state axis (referenced by PANEL ROLE, not fixed indices)
# ---------------------------------------------------------------------------
# Pilot: a single nr4a3_design frame (the crux abort question is CONVERGENCE, not selectivity, so one
# on-target frame is enough to decide whether RBFE-primary is viable). Fleet: held-out validation + matched
# anti-targets. These strings name panel ROLES in nr4a3-conformer-panel.json; the exact frame indices resolve
# at panel-build time per that panel's selection_rules.
PILOT_FRAMES = {"nr4a3": ["nr4a3_design:top_druggable_frame_1"]}
FLEET_FRAMES = {
    "nr4a3": ["nr4a3_validation:8xtt_druggable_1", "nr4a3_validation:8xtt_druggable_2",
              "nr4a3_validation:8xtt_druggable_3", "nr4a3_validation:release_heldout_rank4_6"],
    "nr4a1": ["nr4a1_antitarget:matched_open_frame"],
    "nr4a2": ["nr4a2_antitarget:matched_open_frame"],  # I531 conserved NR4A3=NR4A2 -> hardest to spare
}

# ---------------------------------------------------------------------------
# PRE-REGISTERED abort criteria (design parameters, NOT measurements)
# ---------------------------------------------------------------------------
ABORT_CRITERIA = {
    "_meaning": "PRE-REGISTERED go/no-go thresholds decided a priori. The pilot edge must pass ALL of these on "
                "the single nr4a3_design frame BEFORE any fleet edge is scheduled. Failure => the RBFE-primary "
                "strategy is called into question on this dynamic, low-population cryptic pocket; do NOT fan out.",
    "hysteresis_kcal_max": 0.5,
    "hysteresis_note": "|ΔG_forward − ΔG_reverse| per alchemical leg; above this the morph has not converged.",
    "cycle_closure_kcal_max": 1.0,
    "cycle_closure_note": "|Σ ΔΔG around any closed cycle| must be ~0; above this = internally inconsistent maps.",
    "mbar_overlap_min": 0.03,
    "mbar_overlap_note": "minimum adjacent-lambda phase-space overlap; below this = insufficient window spacing.",
    "pocket_survival_frac_min": 0.5,
    "pocket_survival_note": "fraction of alchemical windows in which the HARMONIZED Pocket-5 lining (fixed lining "
                            "set; fpocket 4.0; D*=0.53; pocket_tracking.py) remains DETECTED. Below this the "
                            "cryptic pocket is collapsing during the alchemical MD.",
    "pocket_volume_collapse": "if the Pocket-5 volume falls below the apo-open reference across >half the windows, "
                              "the pocket is collapsing under the perturbation -> ABORT the fleet and reassess "
                              "RBFE-primary (the pocket may be too transient for congeneric RBFE).",
    "decision_rule": "pilot passes hysteresis AND mbar_overlap AND pocket_survival on one nr4a3_design frame => "
                     "calibrate n_windows/GPU-h from it and schedule the fleet; pilot FAILS any => halt, the "
                     "RBFE-primary premise is in doubt, escalate as a strategy fork (do not silently fan out).",
    "all_values_status": "TBD-tunable design parameters; NOT results. No convergence is claimed.",
}

COST_TBD = {"n_windows": None, "est_gpu_h": None, "status": "TBD — calibrate from the pilot; "
            "the repo forbids trusting stub GPU-hour numbers."}

POSE_UNCERTAINTY_CAVEAT = (
    "Compound 19 (the anchor) has NO solved NR4A3 cocrystal — only functional target engagement "
    "(SMRT/NCoR1 blockade). The binding pose, and with it the '5-position is the linker exit vector' "
    "assignment, are HYPOTHESES. This map therefore treats the binding pose as an ENSEMBLE input: every edge "
    "is scored across the conformer panel frames and NEVER against a single fixed pose. A per-edge result that "
    "holds only in one frame is treated as a geometry artefact (the |receptor effect| > |conformer effect| "
    "criterion in ensemble_robust_score.py)."
)

COMMON_MODE_ASSUMPTION = (
    "RBFE assumes both endpoints of an edge share the SAME binding mode so the common scaffold cancels. Edges "
    "exist ONLY between analogues sharing a binding-mode-preserving core (single-site swaps off the anchor). "
    "The 3-substituent (bioisostere/microstate 3-position) edges perturb the SAR-critical carboxylate H-bond "
    "and are flagged higher-risk: needs_pose_revalidation=true (an endpoint pose check gates trusting the ΔΔG)."
)

# ---------------------------------------------------------------------------
# per-node microstate species at pH 7.4 (both members of every ambiguous pair)
# ---------------------------------------------------------------------------
# Keyed by compound id. Only microstate_ambiguous compounds get >1 species. Charge is inferred from the
# species name suffix (anionic -> -1, cationic -> +1, else 0) so a leg's net-charge change is explicit.
MICROSTATE_SPECIES = {
    "cw_ev_5cooh": ["neutral_acid", "anionic_carboxylate"],
    "cw_ev_5ch2nh2": ["neutral_amine", "cationic_ammonium"],
    "cw_ev_5piperazine": ["neutral", "cationic_monoprotonated"],
    "cw_ev_5pegamine": ["neutral_amine", "cationic_ammonium"],
    "cw_bio_tetrazole": ["neutral", "anionic_tetrazolate"],
    "cw_bio_acylsulfonamide": ["neutral", "anionic"],
    "cw_ms_free_acid": ["neutral_acid", "anionic_carboxylate"],
}


def species_charge(species_name):
    """Net formal charge implied by a microstate species name. Pure string rule (no chemistry backend)."""
    s = species_name.lower()
    if "anionic" in s:
        return -1
    if "cationic" in s:
        return 1
    return 0


def node_species(compound_id):
    """Microstate species list for a node. Ambiguous compounds -> both members; everything else -> ['neutral']."""
    return list(MICROSTATE_SPECIES.get(compound_id, ["neutral"]))


# ---------------------------------------------------------------------------
# stdlib SMILES heavy-atom counter (sanity metric only; NOT the alchemical atom map)
# ---------------------------------------------------------------------------
_TWO_LETTER = {"Cl", "Br"}
_ORGANIC_UPPER = set("BCNOPSFI")
_AROMATIC_LOWER = set("bcnops")


def heavy_atom_count(smiles):
    """Count heavy (non-H) atoms in a SMILES string with pure stdlib. Handles bracket atoms (e.g. [nH], the
    indole/tetrazole N-H), the two-letter organic subset (Cl/Br), the single-letter organic subset, and
    aromatic lowercase atoms. This is a coarse SANITY metric emitted alongside each node; the authoritative
    alchemical atom-count per edge comes from the RDKit/LOMAP MCS at map-BUILD time, not here."""
    count = 0
    i = 0
    n = len(smiles)
    while i < n:
        c = smiles[i]
        if c == "[":
            j = smiles.index("]", i)
            token = smiles[i + 1:j]
            k = 0
            while k < len(token) and token[k].isdigit():  # skip isotope
                k += 1
            el = ""
            if k < len(token) and token[k].isalpha():
                el = token[k]
                if k + 1 < len(token) and (el + token[k + 1]) in _TWO_LETTER:
                    el += token[k + 1]
            if el and el.upper() != "H":
                count += 1
            i = j + 1
            continue
        if c in "BC" and i + 1 < n and smiles[i:i + 2] in _TWO_LETTER:  # Br / Cl before single-letter C
            count += 1
            i += 2
            continue
        if c in _ORGANIC_UPPER or c in _AROMATIC_LOWER:
            count += 1
            i += 1
            continue
        i += 1
    return count


# ---------------------------------------------------------------------------
# per-perturbation curated design metadata (site / risk / pose-reval / approx atoms changed)
# ---------------------------------------------------------------------------
# n_atoms_changed = APPROXIMATE count of heavy atoms in the alchemical (unique) region of the single-site swap
# (mapped/common atoms excluded). Curated structural facts of each substituent swap — NOT measurements — and
# authoritative values come from the RDKit/LOMAP MCS at build time. site: which position is perturbed.
_STAR5 = "star_5position"    # exit-vector / linker-handle region (well-behaved backbone)
_STAR3 = "star_3position"    # SAR-critical 3-carboxylate region (higher common-mode risk)

# node_b id -> (site, common_mode_risk, needs_pose_revalidation, n_atoms_changed, perturbation-text)
EDGE_META = {
    # ---- 5-position star (exit_vector_sub + the 5-NHAc microstate_variant) ----
    "cw_ev_5nh2":        (_STAR5, "low", False, 2, "5-Br -> 5-NH2 (neutral aryl amine; amide/urea vector)"),
    "cw_ev_5oh":         (_STAR5, "low", False, 2, "5-Br -> 5-OH (neutral phenol; ether/carbamate vector)"),
    "cw_ev_5cooh":       (_STAR5, "low", False, 4, "5-Br -> 5-COOH (amide-coupling vector; ionizable)"),
    "cw_ev_5alkyne":     (_STAR5, "low", False, 3, "5-Br -> 5-C#CH (neutral terminal alkyne; click handle)"),
    "cw_ev_5ch2nh2":     (_STAR5, "low", False, 3, "5-Br -> 5-CH2NH2 (benzylic amine; basic/ionizable)"),
    "cw_ev_5opropargyl": (_STAR5, "med", False, 5, "5-Br -> 5-O-CH2-C#CH (neutral propargyl ether)"),
    "cw_ev_5piperazine": (_STAR5, "med", False, 7, "5-Br -> 5-piperazin-1-yl (linker node; basic/ionizable)"),
    "cw_ev_5pegamine":   (_STAR5, "med", False, 8, "5-Br -> 5-O-PEG2-NH2 (PEG-amine stub; basic/ionizable)"),
    "cw_ms_5acetamido_ester": (_STAR5, "low", False, 5, "5-Br -> 5-NHAc (neutral capped amide exit vector)"),
    # ---- 3-position star (bioisostere + the 3-CO2H / 3-CH2OH microstate_variants) -- higher risk ----
    "cw_bio_primary_amide":  (_STAR3, "med",  True, 3, "3-CO2Me -> 3-C(=O)NH2 (primary carboxamide)"),
    "cw_bio_nmethyl_amide":  (_STAR3, "med",  True, 2, "3-CO2Me -> 3-C(=O)NHMe (N-methyl carboxamide)"),
    "cw_bio_tetrazole":      (_STAR3, "high", True, 9, "3-CO2Me -> 3-(1H-tetrazol-5-yl) (anionic isostere)"),
    "cw_bio_acylsulfonamide": (_STAR3, "high", True, 7, "3-CO2Me -> 3-C(=O)NHSO2Me (anionic acylsulfonamide)"),
    "cw_bio_hydroxamic":     (_STAR3, "high", True, 4, "3-CO2Me -> 3-C(=O)NHOH (hydroxamic acid)"),
    "cw_ms_free_acid":       (_STAR3, "high", True, 1, "3-CO2Me -> 3-CO2H (free acid; ionizable microstate pair)"),
    "cw_ms_carbinol":        (_STAR3, "high", True, 4, "3-CO2Me -> 3-CH2OH (carbinol; drops the 3-carbonyl SAR)"),
}

# Explicit cycle-closure edges: each is a SINGLE-site change between two NON-anchor analogues that, with their
# two anchor spokes, closes a >=3-edge loop (Σ ΔΔG ~ 0). (node_a, node_b, site, risk, pose_reval, n_atoms, text)
CYCLE_EDGES = [
    ("cw_ev_5nh2", "cw_ms_5acetamido_ester", _STAR5, "low", False, 3,
     "5-NH2 -> 5-NHAc (acetylation; single-site)", "cycle_exitvector_aniline"),
    ("cw_ev_5oh", "cw_ev_5opropargyl", _STAR5, "med", False, 3,
     "5-OH -> 5-O-CH2-C#CH (O-propargylation; single-site)", "cycle_exitvector_ether"),
    ("cw_ms_free_acid", "cw_bio_primary_amide", _STAR3, "high", True, 2,
     "3-CO2H -> 3-C(=O)NH2 (acid->amide; single-site)", "cycle_3carbonyl"),
]

PILOT_NODE_B = "cw_ev_5nh2"  # 5-Br -> 5-NH2: small, single-site, both neutral, well-behaved -> the pilot


def edge_id(node_a, node_b):
    return "e_%s__%s" % (node_a, node_b)


# ---------------------------------------------------------------------------
# microstate leg enumeration per edge
# ---------------------------------------------------------------------------
def microstate_legs(node_a, node_b):
    """Legs to run for one edge = cartesian product of each endpoint's dominant pH-7.4 species. Each leg holds
    a defined protonation for both ends so a flip cannot silently move ΔΔG. Charge-changing legs are FLAGGED
    (net_charge != 0) so the pipeline applies the co-alchemical / analytical charge correction. Pure."""
    legs = []
    for sa in node_species(node_a):
        for sb in node_species(node_b):
            dq = species_charge(sb) - species_charge(sa)
            legs.append({
                "leg_id": "%s__%s" % (sa, sb),
                "state_a": sa, "state_b": sb,
                "net_charge_change": dq, "charge_change": dq != 0,
            })
    return legs


# ---------------------------------------------------------------------------
# edge construction
# ---------------------------------------------------------------------------
def _make_edge(node_a, node_b, node_b_class, site, risk, pose_reval, n_atoms, perturbation,
               is_pilot=False, is_cycle_closure=False, cycle_id=None):
    frames = {"pilot": PILOT_FRAMES if is_pilot else None, "fleet": FLEET_FRAMES}
    return {
        "edge_id": edge_id(node_a, node_b),
        "class": node_b_class,
        "star": site,
        "node_a": node_a,
        "node_b": node_b,
        "perturbation": perturbation,
        "single_site": True,
        "n_atoms_changed": n_atoms,
        "n_atoms_changed_note": "approximate heavy atoms in the alchemical region; authoritative value = "
                                "RDKit/LOMAP MCS at build time",
        "common_mode_risk": risk,
        "needs_pose_revalidation": pose_reval,
        "receptor_frames": frames,
        "microstate_legs": microstate_legs(node_a, node_b),
        "is_pilot": is_pilot,
        "is_cycle_closure": is_cycle_closure,
        "cycle_id": cycle_id,
        "cost": dict(COST_TBD),
    }


def build_edges(compounds_by_id):
    """Build the full edge list: two anchor-rooted stars (one spoke per non-comparator non-anchor compound) +
    the explicit cycle-closure edges. Returns (edges, cycles). Pure over the compound table."""
    edges = []
    # star spokes: anchor -> each non-comparator non-anchor compound (single site off the anchor)
    for cid, comp in compounds_by_id.items():
        if cid == ANCHOR_ID or comp.get("is_comparator"):
            continue
        meta = EDGE_META.get(cid)
        if meta is None:
            raise KeyError("no EDGE_META for congeneric compound %r" % cid)
        site, risk, pose_reval, n_atoms, text = meta
        edges.append(_make_edge(
            ANCHOR_ID, cid, comp["class"], site, risk, pose_reval, n_atoms, text,
            is_pilot=(cid == PILOT_NODE_B)))

    # cycle-closure edges (single-site, between two non-anchor analogues)
    cycles = {}
    for node_a, node_b, site, risk, pose_reval, n_atoms, text, cyc_id in CYCLE_EDGES:
        e = _make_edge(node_a, node_b, "cycle_closure", site, risk, pose_reval, n_atoms, text,
                       is_cycle_closure=True, cycle_id=cyc_id)
        edges.append(e)
        # the closed loop = anchor->node_a, anchor->node_b, node_a->node_b
        member_ids = [edge_id(ANCHOR_ID, node_a), edge_id(ANCHOR_ID, node_b), edge_id(node_a, node_b)]
        cycles[cyc_id] = {
            "cycle_id": cyc_id, "region": site, "edge_ids": member_ids,
            "constraint": "sum of signed ΔΔG around the loop ~ 0",
            "tol_kcal": ABORT_CRITERIA["cycle_closure_kcal_max"],
        }

    # tag participating star edges with their cycle_id (closing edge already carries it)
    cyc_by_edge = {}
    for cyc in cycles.values():
        for eid in cyc["edge_ids"]:
            cyc_by_edge.setdefault(eid, cyc["cycle_id"])
    for e in edges:
        if e["cycle_id"] is None and e["edge_id"] in cyc_by_edge:
            e["cycle_id"] = cyc_by_edge[e["edge_id"]]

    return edges, list(cycles.values())


def build_nodes(series):
    """Node list = anchor + all enumerated compounds, with microstate species + heavy-atom sanity metric.
    in_rbfe_map=False for comparators (they get ABFE, not RBFE)."""
    nodes = []
    anchor = series["anchor"]
    nodes.append({
        "id": anchor["id"], "class": "anchor", "smiles": anchor["smiles"],
        "is_comparator": False, "in_rbfe_map": True,
        "microstate_species": node_species(anchor["id"]),
        "heavy_atoms": heavy_atom_count(anchor["smiles"]),
        "role": "RBFE hub (both stars root here)",
    })
    for comp in series["compounds"]:
        nodes.append({
            "id": comp["id"], "class": comp["class"], "smiles": comp["smiles"],
            "is_comparator": bool(comp.get("is_comparator")),
            "in_rbfe_map": not bool(comp.get("is_comparator")),
            "microstate_species": node_species(comp["id"]),
            "heavy_atoms": heavy_atom_count(comp["smiles"]),
        })
    return nodes


def build_map(series, panel):
    """Assemble the full perturbation-map dict from the series + panel inputs. Pure."""
    compounds_by_id = {c["id"]: c for c in series["compounds"]}
    nodes = build_nodes(series)
    edges, cycles = build_edges(compounds_by_id)

    comparator_nodes = [n["id"] for n in nodes if n["is_comparator"]]
    by_class = {}
    by_star = {}
    n_legs = 0
    for e in edges:
        by_class[e["class"]] = by_class.get(e["class"], 0) + 1
        by_star[e["star"]] = by_star.get(e["star"], 0) + 1
        n_legs += len(e["microstate_legs"])

    return {
        "_schema": "congeneric_rbfe_perturbation_map",
        "version": MAP_VERSION,
        "_generated_by": "rbfe_map.py",
        "_status": "DESIGN ONLY — no MD/FEP/GPU run. No affinity, ΔΔG, GPU-hour, or convergence is asserted. "
                   "All energetic and cost quantities are placeholders (TBD — calibrate from the pilot).",
        "_inputs": {"nodes_from": "congeneric-warhead-series.json",
                    "receptor_axis_from": "nr4a3-conformer-panel.json"},
        "anchor": ANCHOR_ID,
        "target": TARGET,
        "paralogues": list(PARALOGUES),
        "feeds_scorer": "ensemble_robust_score",
        "feeds_scorer_note": "per-(receptor, conformer) ΔΔG endpoints feed ensemble_robust_score.robust_score / "
                             "beats_benchmark / advancement_verdict. This map introduces NO new scorer.",
        "denovo401_gets_abfe_not_rbfe": True,
        "pilot_edge_id": edge_id(ANCHOR_ID, PILOT_NODE_B),
        "common_mode_assumption": COMMON_MODE_ASSUMPTION,
        "pose_uncertainty_caveat": POSE_UNCERTAINTY_CAVEAT,
        "selectivity_readout": "per edge, per conformer: ΔΔG_bind(NR4A3 frame) − ΔΔG_bind(paralogue frame). "
                               "Rank by the WORST conformer; a preference is trusted only if |receptor effect| > "
                               "|conformer effect| (ensemble_robust_score.receptor_vs_conformer).",
        "receptor_frames_spec": {
            "pilot": PILOT_FRAMES,
            "fleet": FLEET_FRAMES,
            "note": "strings name PANEL ROLES in nr4a3-conformer-panel.json; exact frame indices resolve at "
                    "panel-build time from that panel's selection_rules / pocket_tracking.py (NOT hardcoded here).",
        },
        "microstate_policy": "the 7 microstate_ambiguous compounds run SEPARATE legs per dominant pH-7.4 species "
                             "(both members of the ambiguous pair); charge-changing legs are flagged for the "
                             "co-alchemical / analytical charge correction.",
        "comparator_calibration": {
            "nodes": comparator_nodes,
            "method": "ABFE (absolute) as SECONDARY calibration — NOT RBFE edges into the indole series.",
            "reason": "denovo_401 comparators are a different scaffold; the RBFE common-mode assumption is "
                      "invalid across scaffolds, so no RBFE edge connects them to the congeneric hub.",
            "anchor_ref": "nr4a3_rbfe.py ANCHOR_401_ABFE (the existing denovo_401 ABFE anchor).",
        },
        "abort_criteria": ABORT_CRITERIA,
        "cost_note": "per-edge cost {n_windows, est_gpu_h} are TBD — calibrated from the pilot. The repo forbids "
                     "trusting stub GPU-hour numbers.",
        "cycles": cycles,
        "summary": {
            "n_nodes": len(nodes),
            "n_nodes_in_rbfe_map": sum(1 for n in nodes if n["in_rbfe_map"]),
            "n_comparator_nodes": len(comparator_nodes),
            "n_edges": len(edges),
            "edges_by_class": by_class,
            "edges_by_star": by_star,
            "n_cycles": len(cycles),
            "n_microstate_legs_total": n_legs,
            "n_edges_needing_pose_revalidation": sum(1 for e in edges if e["needs_pose_revalidation"]),
        },
        "nodes": nodes,
        "edges": edges,
    }


# ---------------------------------------------------------------------------
# validation (used by tests + as a self-check before emitting)
# ---------------------------------------------------------------------------
def validate_map(m):
    """Return a list of human-readable problems (empty => valid). Enforces the map's design invariants:
      * exactly one node flagged anchor, matching m['anchor'];
      * every in_rbfe_map non-anchor node has >=1 edge; comparators have NO edges;
      * every non-cycle edge is incident to the anchor (star property) and single_site;
      * every edge is single_site (no double mutations); cycle-closure edges are the ONLY non-anchor-incident
        edges;
      * every bioisostere (3-position) edge is needs_pose_revalidation=true;
      * every ambiguous compound has >=2 microstate species; edges touching them carry >=2 legs;
      * the pilot edge exists, is single-site, both endpoints neutral, and on exactly one nr4a3_design frame;
      * every cycle references exactly 3 existing edges."""
    problems = []
    nodes = {n["id"]: n for n in m["nodes"]}
    edges = {e["edge_id"]: e for e in m["edges"]}
    anchor = m["anchor"]

    anchors = [n for n in m["nodes"] if n["class"] == "anchor"]
    if len(anchors) != 1 or anchors[0]["id"] != anchor:
        problems.append("expected exactly one anchor node matching m['anchor']")

    # edges incident-to-anchor unless cycle-closure; all single-site
    incident = {nid: 0 for nid in nodes}
    for e in m["edges"]:
        if not e.get("single_site"):
            problems.append("edge %s is not single_site (double mutation forbidden)" % e["edge_id"])
        if not e["is_cycle_closure"] and anchor not in (e["node_a"], e["node_b"]):
            problems.append("non-cycle edge %s is not incident to the anchor (star violation)" % e["edge_id"])
        incident[e["node_a"]] += 1
        incident[e["node_b"]] += 1

    for nid, n in nodes.items():
        if n["is_comparator"]:
            if incident[nid] != 0:
                problems.append("comparator node %s has edges (must get ABFE, not RBFE)" % nid)
        elif nid != anchor:
            if incident[nid] == 0:
                problems.append("congeneric node %s has no edge" % nid)

    # bioisostere edges need pose revalidation
    for e in m["edges"]:
        if e["class"] == "bioisostere" and not e["needs_pose_revalidation"]:
            problems.append("bioisostere edge %s must be needs_pose_revalidation=true" % e["edge_id"])

    # ambiguous compounds -> >=2 species, and edges touching them -> >=2 legs
    for nid, n in nodes.items():
        if nid in MICROSTATE_SPECIES and len(n["microstate_species"]) < 2:
            problems.append("ambiguous compound %s must carry >=2 microstate species" % nid)
    for e in m["edges"]:
        touches_ambiguous = e["node_a"] in MICROSTATE_SPECIES or e["node_b"] in MICROSTATE_SPECIES
        if touches_ambiguous and len(e["microstate_legs"]) < 2:
            problems.append("edge %s touches an ambiguous compound but has <2 microstate legs" % e["edge_id"])

    # pilot edge sanity
    pilot_id = m["pilot_edge_id"]
    pe = edges.get(pilot_id)
    if pe is None:
        problems.append("pilot_edge_id %s not present in edges" % pilot_id)
    else:
        if not pe["is_pilot"]:
            problems.append("pilot edge %s not flagged is_pilot" % pilot_id)
        if not pe["single_site"]:
            problems.append("pilot edge %s must be single-site" % pilot_id)
        for end in (pe["node_a"], pe["node_b"]):
            if node_species(end) != ["neutral"]:
                problems.append("pilot edge endpoint %s must be neutral (unambiguous microstate)" % end)
        pf = pe["receptor_frames"].get("pilot") or {}
        n_pilot_frames = sum(len(v) for v in pf.values())
        if n_pilot_frames != 1:
            problems.append("pilot edge must run on exactly ONE nr4a3_design frame (got %d)" % n_pilot_frames)

    # cycles reference exactly 3 existing edges
    for cyc in m["cycles"]:
        if len(cyc["edge_ids"]) != 3:
            problems.append("cycle %s must have exactly 3 edges" % cyc["cycle_id"])
        for eid in cyc["edge_ids"]:
            if eid not in edges:
                problems.append("cycle %s references missing edge %s" % (cyc["cycle_id"], eid))

    return problems


def load_inputs(series_path=SERIES_PATH, panel_path=PANEL_PATH):
    with open(series_path) as fh:
        series = json.load(fh)
    with open(panel_path) as fh:
        panel = json.load(fh)
    return series, panel


def main(out_path=OUT_PATH):
    series, panel = load_inputs()
    m = build_map(series, panel)
    problems = validate_map(m)
    if problems:
        raise SystemExit("map validation FAILED:\n  " + "\n  ".join(problems))
    with open(out_path, "w") as fh:
        json.dump(m, fh, indent=2)
        fh.write("\n")
    s = m["summary"]
    print("wrote %s" % out_path)
    print("  nodes=%d (in_map=%d, comparators=%d)  edges=%d  cycles=%d  microstate_legs=%d"
          % (s["n_nodes"], s["n_nodes_in_rbfe_map"], s["n_comparator_nodes"], s["n_edges"],
             s["n_cycles"], s["n_microstate_legs_total"]))
    print("  edges_by_class=%s" % s["edges_by_class"])
    print("  pilot=%s" % m["pilot_edge_id"])
    return m


if __name__ == "__main__":
    main()
