#!/usr/bin/env python3
"""
DOES A <=12-BACKBONE-ATOM, ONE-BRANCH CONSTRUCT REACHING NR4A3 C397 EXIST?   $0 CPU (RDKit + stdlib).

★ WHY THIS RUN EXISTS. The program has a measured selectivity mechanism and a rung that wants to exploit it,
and one thing sits between them: rung `5b-T`'s gate arm (C) is registered AT RISK because **no committed
construct sits at or below 12 backbone atoms -- the shortest is 14**. The mechanism
(`nr4a-paralogue-dynamics.json`, 73,867 matched placements over three conformer scopes) puts reach-only
paralogue collision at **0.000 / 0.00124 / 0.00290 at the 12-atom gate** and at **0.054-0.133 at 16** and
**0.263-0.383 at 20** -- so a short linker is not merely more tractable, it IS the selectivity. Rung `5b-T`
names "a $0 RDKit re-enumeration" as the way out. This is that re-enumeration.

★★ WHAT WAS NEVER RUN, AND WHY THAT WAS THE WHOLE GAP. `nr4a3_linker_design.CONFIRMED` is a FIVE-basin list
   fixed by the rung-5a term-(b) decision, and the enumerator refuses to design against anything else. The
   basin whose exact C397 requirement actually sits AT the gate -- `crbn|M17`, at 12 -- is not in it, so no
   molecule was ever enumerated against it. The candidate set here is therefore DERIVED from the artifact
   (`term_a_union.C397.min_linker_atoms <= 12` over all 58 ranked meta-basins) rather than assumed to be one
   basin, which is what turns "nobody ran it" into an answer either way.

WHAT THIS MODULE DOES NOT DO. It does not re-fit, re-cluster or re-rank anything; it does not relax, retune
or re-weight the preregistered rung-5b downselect; it does not edit the committed library. It calls the
COMMITTED machinery -- `nr4a3_linker_design.basin_requirements` / `.enumerate_library` / `.apply_filter` /
`.build_smiles`, and `linker_design.branch_position_window` / `.min_linker_atoms_exact` -- on a basin set the
committed driver's hard-coded `CONFIRMED` list excludes, and reports what those rules return.

★ AND IT REPORTS THE FILTER SEPARATELY FROM THE GEOMETRY, BECAUSE THEY GIVE DIFFERENT ANSWERS AND BOTH ARE
  TRUE. "Can a 12-atom one-branch construct be drawn that spans this basin's anchors and presents an
  electrophile on C397's SG?" and "does that construct pass the preregistered basin-fidelity downselect?" are
  two questions, and collapsing them -- in either direction -- is how a floor of 14 came to read as a
  geometric fact when it is a downselect consequence. Four independent floors are emitted per basin:
      floor_chemistry     the shortest one-branch backbone the committed building-block grid can assemble
      floor_span          the shortest chain that merely CONNECTS the two anchors (no pendant substitutes)
      floor_reach         the shortest chain with a feasible integer branch position onto C397 SG
      floor_filter        the shortest that also clears every preregistered fidelity threshold
  and the answer NAMES which of the four binds.

⛔ SCOPE, UP FRONT AND UNCONDITIONAL. Geometry and chemistry only. Nothing here is a claim about binding,
   affinity, reactivity, thiol pKa, adduct stability, permeability, degradation, efficacy, a therapeutic
   window or safety. A construct here is a PREDICTED SELECTIVE CANDIDATE, never a selective hit, and
   target-engagement selectivity is the ONLY axis it can speak to -- a PROTAC also needs a productive
   ternary, which is rung `5b-T`'s job and not this one's.

Usage:
    python3 nr4a3_short_linker_probe.py            # writes nr4a3-short-linker-probe.json
    python3 nr4a3_short_linker_probe.py --check    # regenerate and diff against the committed artifact
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G                       # noqa: E402
import linker_design as LD                   # noqa: E402  THE reach engine — never reimplemented here
import nr4a3_linker_design as NLD            # noqa: E402  THE enumerator — never reimplemented here
import nr4a3_linker_covalent_reach as CR     # noqa: E402  THE corridor convention — never reimplemented here

BASINS = os.path.join(HERE, "nr4a3-orientation-basins.json")
REGISTRY = os.path.join(HERE, "nr4a3-e3-arm-registry.json")
ATLAS = os.path.join(HERE, "nr4a3-differential-surface-atlas.json")
SERIES = os.path.join(HERE, "congeneric-warhead-series.json")
STRUCT = os.path.join(REPO, "results", "nr4a3-matrix", "nr4a3-opened.pdb")
DYNAMICS = os.path.join(HERE, "nr4a-paralogue-dynamics.json")
LIBRARY_CHEM = os.path.join(HERE, "nr4a3-linker-library-chem.json")
OUT = os.path.join(HERE, "nr4a3-short-linker-probe.json")

# The electrophile pendants that target C397 SG. Read from the enumerator's own PENDANT table rather than
# retyped, so a pendant added there cannot be silently missed here.
C397_PENDANTS = tuple(k for k, v in NLD.PENDANT.items() if v["reach_key"] == "dab_branch")


def _et(dt):
    """US Eastern, 12-hour — CLAUDE.md §1. EDT = UTC-4 for every date this repo has run on."""
    return (dt - datetime.timedelta(hours=4)).strftime("%Y-%m-%d %-I:%M %p ET")


# ==========================================================================================================
# THE GATE, AND THE CANDIDATE BASIN SET — both DERIVED, neither typed
# ==========================================================================================================
def gate_atoms(dyn):
    """The 12-atom gate, read from the ensemble artifact that owns it."""
    return dyn["categorical_verdict"]["gate_atoms"]


def candidate_basins(basins, gate):
    """Every ranked meta-basin whose EXACT C397 requirement is at or below the gate.

    ⚠ `term_a_union.C397.min_linker_atoms` is the exact three-ball rule at the `rung5a_convention` arm reach
    (3.0 A), taken as a MINIMUM over the basin's sampled member placements — a best-of-N, i.e. the optimistic
    end of the basin. That is the right selector for this question (it asks whether ANY member of the basin
    could carry a short construct) and it is the wrong number to quote as a property of the basin, so every
    downstream record carries the achieving placement rather than the statistic.
    """
    out = []
    for m in basins["meta_basins_ranked"]:
        rec = (m.get("term_a_union") or {}).get("C397") or {}
        n = rec.get("min_linker_atoms")
        if n is None or n > gate:
            continue
        out.append(m)
    return out


# ==========================================================================================================
# THE FOUR FLOORS
# ==========================================================================================================
def chemistry_floor_one_branch():
    """The shortest ONE-BRANCH backbone the committed building-block grid can assemble, and how.

    `build_smiles` fixes the branched chain as
        E3-NH -C(=O)- [SEG1] -C(=O)-NH- CH(pendant) -C(=O)-NH- [SEG2] - <warhead tail>
    so n = 1 + |SEG1| + 1 + 3 + 1 + |SEG2| + tail_atoms. Enumerated rather than derived from that formula, so
    the answer stays correct if a building block is added or a constraint changes.
    """
    best = None
    for wh_key, wh in NLD.WARHEAD_HANDLE.items():
        for s1 in NLD.LINKER_SEGMENT:
            for s2 in NLD.LINKER_SEGMENT:
                for pk in C397_PENDANTS:
                    try:
                        smi, n, k = NLD.build_smiles("crbn", wh_key, s1, s2, pk)
                    except ValueError:
                        continue
                    if k is None or k < 1 or k >= n:
                        continue
                    if best is None or n < best["n_backbone_atoms"]:
                        best = {"n_backbone_atoms": n, "warhead_handle": wh_key,
                                "linker_segments": [s1, s2], "pendant": pk,
                                "branch_k_from_warhead": k}
    return best


def floors_for(req, enumerated):
    """The four floors at ONE placement, plus the filter terms that bind at the gate length."""
    bid = req["meta_basin_id"]
    cs = [c for c in enumerated
          if c["designed_for_basin"] == bid and c["pendant"] in C397_PENDANTS]
    reach_ns = sorted({c["n_backbone_atoms_intended"] for c in cs})
    return {
        "floor_span_atoms": req["endpoint_distance"]["span_floor_atoms"],
        "floor_reach_atoms": reach_ns[0] if reach_ns else None,
        "one_branch_c397_lengths_enumerated": reach_ns,
        "_floor_reach_reading": (
            "the shortest backbone that BOTH spans this placement's anchors AND has an integer branch "
            "position whose Dab-type pendant ball meets C397's SG — the exact three-ball rule, on a chain "
            "the committed building-block grid can actually assemble."),
    }


def filter_terms_at(req, enumerated, n_atoms):
    """Every preregistered fidelity term, with its VALUE, for the shortest construct at `n_atoms`.

    ⚠ Emitted as terms-with-values rather than as a verdict, because the interesting answer here is not
    pass/fail but WHICH term binds: a floor forced by chain strain is a statement about physics, and a floor
    forced by basin-member coverage is a statement about a downselect policy. They must never read alike.
    """
    cs = sorted((c for c in enumerated
                 if c["designed_for_basin"] == req["meta_basin_id"]
                 and c["pendant"] in C397_PENDANTS
                 and c["n_backbone_atoms_intended"] == n_atoms),
                key=lambda c: (c["basin_fidelity"]["strain_kT_at_placement_span"],
                               -c["basin_fidelity"]["member_fraction_comfortable"]))
    if not cs:
        return None
    c = cs[0]
    f = c["basin_fidelity"]
    terms = [
        {"term": "must_span_the_floor", "threshold": ">= %d backbone atoms"
         % req["endpoint_distance"]["span_floor_atoms"],
         "value": n_atoms, "passes": bool(f["spans_the_floor"])},
        {"term": "max_strain_kT_at_placement", "threshold": "<= %.1f kT" % NLD.MAX_STRAIN_KT,
         "value": f["strain_kT_at_placement_span"],
         "passes": f["strain_kT_at_placement_span"] <= NLD.MAX_STRAIN_KT},
        {"term": "min_member_fraction_comfortable",
         "threshold": ">= %.2f" % NLD.FILTER["min_member_fraction_comfortable"],
         "value": f["member_fraction_comfortable"],
         "passes": f["member_fraction_comfortable"] >= NLD.FILTER["min_member_fraction_comfortable"]},
        {"term": "max_backbone_atoms", "threshold": "<= %d" % NLD.CHEM_MAX_ATOMS,
         "value": n_atoms, "passes": n_atoms <= NLD.CHEM_MAX_ATOMS},
    ]
    return {"representative_construct_id": c["construct_id"],
            "n_backbone_atoms": n_atoms,
            "terms": terms,
            "binding_terms": [t["term"] for t in terms if not t["passes"]],
            "passes_all": all(t["passes"] for t in terms)}


# ==========================================================================================================
# RDKit — a construct with no recoverable molecule is not a construct
# ==========================================================================================================
def rdkit_verify(construct):
    """Canonical SMILES + InChIKey + a RE-DERIVED backbone length and branch index, from the parsed molecule.

    ⛔ THIS IS NOT OPTIONAL AND IT IS NOT PAPERWORK. §2.5's ternary result is dead — not weak, dead — because
    its molecule cannot be recovered from any of the three deposited models, so no replicate can ever be
    matched to it. A candidate emitted here without a recorded structure would repeat that exactly. The
    re-derivation is `linker_chem_check.check_one`'s: the backbone is the topological shortest path between
    the two anchor atoms found STRUCTURALLY (truncated cores, then the first atom outside each core on the
    path between them), never from a hand-written SMARTS with a positional index.
    """
    import linker_chem_check as CHEM          # imported here so the module stays importable without RDKit
    from rdkit import Chem

    rec = CHEM.check_one(construct)
    mol = Chem.MolFromSmiles(construct["smiles"])
    rec["canonical_smiles"] = Chem.MolToSmiles(mol) if mol is not None else None
    rec["inchikey"] = Chem.MolToInchiKey(mol) if mol is not None else None
    return rec


# ==========================================================================================================
# THE PARALOGUES, AT THE LENGTH ACTUALLY ACHIEVED
# ==========================================================================================================
def collision_at(dyn, n_atoms):
    """The measured paralogue-collision reading at EXACTLY `n_atoms`, or the bracket if it was not measured.

    ⚠ THE GRID IS {12, 14, 16, 20}. A construct at 13 has no measurement, only a bracket, and a curve drawn
    through four points and read off at 13 is not a measurement — see
    `nr4a3_linker_design.PARALOGUE_COLLISION_BY_LINKER_ATOMS`'s own warning. A construct at 12 has one, which
    is the single strongest reason to prefer 12 over 11 even though 11 is buildable.
    """
    scopes = dyn["categorical_verdict"]["by_scope"]
    grid = sorted(int(k) for k in next(iter(scopes.values()))["by_linker_atoms"])
    exact = n_atoms in grid
    per_scope = {}
    for scope, sv in scopes.items():
        tbl = sv["by_linker_atoms"]
        if exact:
            row = tbl[str(n_atoms)]
            per_scope[scope] = {
                "measured_at": n_atoms,
                "n_frames": sv["n_frames"],
                "reach_only_collision": row["P_paralogue_also_labelled_given_nr4a3"],
                "reach_and_exposed_collision": row["P_paralogue_also_labelled_given_nr4a3_EXPOSED"],
                "P_categorical_given_nr4a3": row["P_categorical_given_nr4a3"],
                "n_placements_with_any_nr4a3_hit": row["n_placements_with_any_nr4a3_hit"],
                "mean_P_nr4a3_unique": row["mean_P_nr4a3_unique"],
            }
        else:
            lo_x = max([x for x in grid if x <= n_atoms], default=grid[0])
            hi_x = min([x for x in grid if x >= n_atoms], default=None)
            per_scope[scope] = {
                "measured_at": None,
                "bracket_atoms": [lo_x, hi_x],
                "reach_only_collision_bracket": [
                    tbl[str(lo_x)]["P_paralogue_also_labelled_given_nr4a3"],
                    (tbl[str(hi_x)]["P_paralogue_also_labelled_given_nr4a3"] if hi_x else None)],
                "_reading": "NOT interpolated — the measurement grid has no point at this length.",
            }
    band = None
    if exact:
        vals = [v["reach_only_collision"] for v in per_scope.values()]
        band = [min(vals), max(vals)]
    return {
        "n_backbone_atoms": n_atoms,
        "is_a_measured_grid_point": exact,
        "measurement_grid_atoms": grid,
        "reach_only_collision_band_across_scopes": band,
        "by_scope": per_scope,
        "_one_home": ("research/modalities/nr4a-paralogue-dynamics.json -> "
                      "categorical_verdict.by_scope[*].by_linker_atoms"),
        "⚠_reach_only_is_the_number_that_does_not_depend_on_the_exposure_criterion": (
            "the `reach_and_exposed` column is adjudicated by EXPOSED_RSA = %.2f, the criterion that fails "
            "its own positive control (NR4A1 Cys551, the literature-anchored celastrol site, at RSA 0.165 on "
            "the state-matched opened model). At the 12-atom gate the categorical statement does NOT rest on "
            "it — reach-only collision there is already <= 0.3 %% — whereas at 16 and 20 atoms it does."
            % dyn["categorical_verdict"]["exposed_rsa_cutoff"]),
    }


# ==========================================================================================================
# REACH MARGIN UNDER BOTH CONVENTIONS
# ==========================================================================================================
def both_conventions(reqs, dyn_unused=None, cutoffs=CR.CLASH_SWEEP_A):
    """`through_space` and `corridor` side by side for every candidate placement, in nr4a3-opened.pdb.

    ⚠ REPORTED SIDE BY SIDE AND NEVER MERGED. The audit found `verdict()` in the covalent-reach lane building
    its refuted-cysteine list from `best_corridor` alone while its own `best_through_space` field two keys
    away disagreed — so C559, which survives at one through-space cell, was labelled refuted. Both numbers
    are carried here for every cell, and any statement that uses one says which.
    """
    basins = json.load(open(BASINS))
    unique_labels = {"C%d" % c["uniprot_resid"] for c in basins["target_frame"]["unique_cysteines"]}
    model = CR.BS.load_paralogue(STRUCT)
    placements = [{"meta_basin_id": r["meta_basin_id"], "placement_label": r["placement_label"],
                   "_a": r["_a"], "_b": r["_b"],
                   "span_A": round(G.dist(r["_a"], r["_b"]), 3)} for r in reqs]
    return CR.reach_one_frame(model, placements, unique_labels, CR.OFFSET, cutoffs,
                              label="nr4a3-opened")


def margin_row(row, pendant, cutoff=CR.CLASH_PRIMARY_A):
    """One (placement x cysteine x pendant) cell, under BOTH conventions and across the clash sweep."""
    e = row["by_pendant"][pendant]
    return {"through_space_atoms": e["through_space_atoms"],
            "corridor_atoms_at_%.1fA" % cutoff: e["corridor_atoms"]["%.1f" % cutoff],
            "corridor_atoms_sweep": e["corridor_atoms"],
            "corridor_branch_k": e.get("corridor_branch_k")}


def windows_at(rows, placement_key, pendant, gate, cutoff=CR.CLASH_PRIMARY_A):
    """The chemoselectivity window for C397 at one placement, under BOTH conventions, and whether the gate
    length sits inside each.

    The window is the interval of backbone-atom counts over which C397 is in reach and NO conserved cysteine
    is — the decision quantity, computed by the committed `chemoselectivity_margin` (never reimplemented).
    A conserved cysteine is one both paralogues keep, so a window of width 0 refutes the route at that
    geometry.
    """
    def n_of(row, conv):
        e = row["by_pendant"][pendant]
        return e["through_space_atoms"] if conv == "through_space" \
            else e["corridor_atoms"]["%.1f" % cutoff]

    here = [r for r in rows if r["placement"] == placement_key]
    uniq = next((r for r in here if r["cysteine"] == "C397"), None)
    if uniq is None:
        return None
    out = {}
    for conv in ("through_space", "corridor"):
        conserved = {r["cysteine"]: n_of(r, conv) for r in here if not r["unique"]}
        w = CR.chemoselectivity_margin(n_of(uniq, conv), conserved)
        w["c397_required_atoms"] = n_of(uniq, conv)
        w["gate_length_is_inside_the_window"] = bool(
            w["lo"] is not None and w["hi"] is not None and w["lo"] <= gate <= w["hi"])
        out[conv] = w
    out["_convention_note"] = (
        "`through_space` is an UPPER bound on reachability — it will place a branch atom inside the protein. "
        "`corridor` at %.1f A additionally requires a non-clashing branch position with a clash-free straight "
        "arm to the SG; it is NECESSARY, not sufficient. A construct that clears only one of them must say so."
        % cutoff)
    out["clears_the_gate_under_both_conventions"] = bool(
        out["through_space"]["gate_length_is_inside_the_window"]
        and out["corridor"]["gate_length_is_inside_the_window"])
    return out


# ==========================================================================================================
# BUILD
# ==========================================================================================================
def build():
    t_utc = datetime.datetime.utcnow()
    basins = json.load(open(BASINS))
    dyn = json.load(open(DYNAMICS))
    gate = gate_atoms(dyn)

    ctx = NLD.load_context(BASINS, REGISTRY, ATLAS, STRUCT, SERIES)
    sites = NLD.reactive_sites(ctx)
    ctx["_c397"] = sites["unique_cysteines"]["C397"]["xyz"]

    cands = candidate_basins(basins, gate)
    reqs_rep, reqs_ex = [], []
    for m in cands:
        r_rep, r_ex = NLD.basin_requirements(ctx, m, sites)
        reqs_rep.append(r_rep)
        if r_ex is not None:
            reqs_ex.append(r_ex)

    chem_floor = chemistry_floor_one_branch()

    per_placement = []
    all_at_or_below_gate = []
    for label, reqs in (("term_a_exemplar", reqs_ex), ("representative", reqs_rep)):
        if not reqs:
            continue
        enumerated = NLD.enumerate_library(reqs, ctx)
        kept, _rej = NLD.apply_filter(enumerated)
        kept_ids = {c["construct_id"] for c in kept}
        for r in reqs:
            bid = r["meta_basin_id"]
            fl = floors_for(r, enumerated)
            passing = sorted(c["n_backbone_atoms_intended"] for c in kept
                             if c["designed_for_basin"] == bid and c["pendant"] in C397_PENDANTS)
            rec = {
                "meta_basin_id": bid,
                "arm_id": r["arm_id"],
                "e3": NLD.E3_HANDLE[r["arm_id"]]["name"],
                "placement_label": label,
                "placement_is_a_best_of_N": label == "term_a_exemplar",
                "pose_id": r["designed_on"]["pose_id"],
                "basin_id": r["designed_on"]["basin_id"],
                "in_the_committed_CONFIRMED_set": bid in NLD.CONFIRMED,
                "term_b_exceeds_background": r["term_b_exceeds_background"],
                "term_b_max_enrichment_over_background": r["term_b_max_enrichment_over_background"],
                "pose_surviving_fraction": r["pose_surviving_fraction"],
                "placement_span_A": r["endpoint_distance"]["placement_span_A"],
                "member_span_A": r["endpoint_distance"]["member_span_A"],
                "c397_exact_atoms_by_pendant": {
                    k: v["exact_atoms"]
                    for k, v in r["electrophile_reach"]["C397"]["by_pendant"].items()},
                "floor_chemistry_atoms": chem_floor["n_backbone_atoms"],
                "floor_filter_atoms": passing[0] if passing else None,
                "n_atoms_for_comfortable_span": r["accessibility"]["n_atoms_for_comfortable_span"],
            }
            rec.update(fl)
            rec["at_the_gate"] = filter_terms_at(r, enumerated, gate)
            rec["at_its_reach_floor"] = (filter_terms_at(r, enumerated, fl["floor_reach_atoms"])
                                         if fl["floor_reach_atoms"] else None)
            rec["clears_the_gate_geometrically"] = bool(
                fl["floor_reach_atoms"] is not None and fl["floor_reach_atoms"] <= gate)
            rec["clears_the_gate_under_the_preregistered_filter"] = bool(
                passing and passing[0] <= gate)
            per_placement.append(rec)

            if rec["clears_the_gate_geometrically"]:
                for c in enumerated:
                    if (c["designed_for_basin"] == bid and c["pendant"] in C397_PENDANTS
                            and c["n_backbone_atoms_intended"] <= gate):
                        all_at_or_below_gate.append(dict(c, _placement_label=label,
                                                         _kept_by_filter=c["construct_id"] in kept_ids))

    # ---- both reach conventions, on every placement that produced a gate-clearing construct
    conv_reqs = [r for r in reqs_ex if any(
        p["meta_basin_id"] == r["meta_basin_id"] and p["placement_label"] == "term_a_exemplar"
        and p["clears_the_gate_geometrically"] for p in per_placement)]
    conv = both_conventions(conv_reqs) if conv_reqs else {"rows": [], "anchor_clearance": {},
                                                          "invariant_violations": [], "cysteines": {}}
    unique_labels = {"C%d" % c["uniprot_resid"] for c in basins["target_frame"]["unique_cysteines"]}
    conventions, conserved = [], []
    for row in conv["rows"]:
        rec = {"placement": row["placement"], "cysteine": row["cysteine"],
               "by_pendant": {p: margin_row(row, p) for p in row["by_pendant"]}}
        if row["unique"]:
            rec.update({"e3_projects_to_solvent": row["e3_projects_to_solvent"],
                        "warhead_anchor_has_room": row["warhead_anchor_has_room"],
                        "d_warhead_anchor_A": row["d_warhead_anchor_A"],
                        "d_e3_anchor_A": row["d_e3_anchor_A"]})
            conventions.append(rec)
        else:
            conserved.append(rec)

    # ★★ THE WINDOW TEST IS WHAT SEPARATES THE THREE BASINS, AND IT IS RUN AT TWO PENDANT REACHES.
    #    `dab_branch` (8.75 A) is what the electrophile constructs actually carry; `rung5a_convention`
    #    (3.0 A) is the PREREGISTERED gate value and is shorter, i.e. conservative. A construct that clears
    #    both conventions at BOTH reaches is a materially stronger statement than one that clears the
    #    permissive combination, so both are computed and the candidate ranking uses the conservative one.
    windows = {}
    for p in per_placement:
        if p["placement_label"] != "term_a_exemplar" or not p["clears_the_gate_geometrically"]:
            continue
        key = "%s@term_a_exemplar" % p["meta_basin_id"]
        windows[key] = {pend: windows_at(conv["rows"], key, pend, gate)
                        for pend in ("rung5a_convention", "dab_branch")}
        p["gate_clears_both_conventions_dab_branch"] = bool(
            (windows[key]["dab_branch"] or {}).get("clears_the_gate_under_both_conventions"))
        p["gate_clears_both_conventions_rung5a_convention"] = bool(
            (windows[key]["rung5a_convention"] or {}).get("clears_the_gate_under_both_conventions"))

    # ---- the candidate
    # ★ AT the gate, not below it. Below 12 the collision measurement grid has no point at all, so an
    #   11-atom construct trades a MEASURED number for an extrapolated one — a worse deal than one backbone
    #   atom. Then, in order: it must clear the gate under BOTH reach conventions (the audit's finding was a
    #   verdict built from `best_corridor` alone, and the opposite error is just as available); it must pass
    #   the chain-strain term, which is physics rather than policy; it must carry the REVERSIBLE-covalent
    #   electrophile, which is rung 5b's stated preference and the property that preserves catalytic
    #   turnover; and it should sit on the basin with the most pose evidence. Ties break on the id so the
    #   artifact is reproducible.
    strain_ok = {p["meta_basin_id"]: (p["at_the_gate"] or {}).get("terms", [{}, {}])[1].get("passes", False)
                 for p in per_placement if p["placement_label"] == "term_a_exemplar"}
    pose_frac = {p["meta_basin_id"]: p["pose_surviving_fraction"]
                 for p in per_placement if p["placement_label"] == "term_a_exemplar"}
    both_conv = {p["meta_basin_id"]: p.get("gate_clears_both_conventions_rung5a_convention", False)
                 for p in per_placement if p["placement_label"] == "term_a_exemplar"}

    def rank(c):
        bid = c["designed_for_basin"]
        pend = NLD.PENDANT[c["pendant"]]
        return (-c["n_backbone_atoms_intended"],
                0 if both_conv.get(bid) else 1,
                0 if strain_ok.get(bid) else 1,
                0 if (pend["kind"] == "electrophile" and pend["reversible"]) else 1,
                -(pose_frac.get(bid) or 0.0),
                c["construct_id"])

    candidate = min(all_at_or_below_gate, key=rank) if all_at_or_below_gate else None
    # the CRBN answer, carried separately because rung `5b-T`'s E3 is CRBN and a VHL candidate does not
    # answer it — the honest CRBN reading is a different one and must not be buried in a ranking.
    crbn_pool = [c for c in all_at_or_below_gate if c["e3_handle"] == "crbn"]
    crbn_alt = min(crbn_pool, key=rank) if crbn_pool else None

    chem = rdkit_verify(candidate) if candidate is not None else None
    crbn_chem = rdkit_verify(crbn_alt) if crbn_alt is not None else None

    # the matched controls, because a covalent design without its comparators is not usable evidence
    def controls_for(c):
        if c is None:
            return []
        out = []
        for k in all_at_or_below_gate:
            if (k["designed_for_basin"] == c["designed_for_basin"]
                    and k["designed_at_placement"] == c["designed_at_placement"]
                    and k["warhead_handle"] == c["warhead_handle"]
                    and k["linker_segments"] == c["linker_segments"]
                    and k["n_backbone_atoms_intended"] == c["n_backbone_atoms_intended"]
                    and k["pendant"] != c["pendant"]):
                kc = rdkit_verify(k)
                out.append({"construct_id": k["construct_id"], "pendant": k["pendant"],
                            "pendant_name": NLD.PENDANT[k["pendant"]]["name"],
                            "kind": NLD.PENDANT[k["pendant"]]["kind"],
                            "reversible": NLD.PENDANT[k["pendant"]]["reversible"],
                            "why": NLD.PENDANT[k["pendant"]]["why"],
                            "n_backbone_atoms_intended": k["n_backbone_atoms_intended"],
                            "n_backbone_atoms_measured_by_rdkit": kc.get("n_backbone_atoms_measured"),
                            "smiles": k["smiles"], "canonical_smiles": kc.get("canonical_smiles"),
                            "inchikey": kc.get("inchikey"), "rdkit_ok": kc.get("ok")})
        return sorted(out, key=lambda r: r["construct_id"])

    answer = _answer(gate, per_placement, candidate, chem, chem_floor, crbn_alt, crbn_chem)

    out = {
        "_title": "Does a <=%d-backbone-atom, ONE-BRANCH construct reaching NR4A3 C397 exist?" % gate,
        "_question": (
            "Rung `5b-T` gate arm (C) is registered AT RISK because no committed construct sits at or below "
            "the %d-atom gate — the shortest is 14 — and `crbn|M0`, the only CRBN basin in the confirmed "
            "set, has an exact C397 requirement of 13. `5b-T` names a $0 RDKit re-enumeration as the way "
            "out. This is it." % gate),
        "_status": ("GEOMETRY AND CHEMISTRY ONLY. $0 — RDKit and stdlib on CPU, no GPU, no rental. Nothing "
                    "here is a claim about binding, affinity, reactivity, degradation, efficacy or safety."),
        "_one_fact_one_place": (
            "Every threshold, pendant reach, building block and filter term is IMPORTED from "
            "`nr4a3_linker_design` / `linker_design` / `nr4a3_linker_covalent_reach`, and every collision "
            "figure is read from `nr4a-paralogue-dynamics.json`. This file is not a second home for any of "
            "them. Only the VERDICT strings are authored, and each names the field that decided it."),
        "_generated": {"utc": t_utc.strftime("%Y-%m-%dT%H:%M:%SZ"), "et": _et(t_utc),
                       "generator": "research/modalities/nr4a3_short_linker_probe.py",
                       "rdkit_version": _rdkit_version()},
        "_inputs": {
            "research/modalities/nr4a3-orientation-basins.json":
                "the 58 ranked meta-basins, their placements, spans and term-(a) C397 reach records",
            "research/modalities/nr4a-paralogue-dynamics.json":
                "the matched NR4A1/2/3 ensembles — the gate length and the collision table",
            "research/modalities/nr4a3-e3-arm-registry.json": "each E3 arm's rigid body and exit atom",
            "research/modalities/nr4a3-differential-surface-atlas.json": "per-residue divergence (wedge sites)",
            "research/modalities/congeneric-warhead-series.json": "the cmpd19 exit-vector handles",
            "results/nr4a3-matrix/nr4a3-opened.pdb": "the matched opened NR4A3 LBD every anchor lives in",
        },
        "gate": {
            "backbone_atoms": gate,
            "_source": "nr4a-paralogue-dynamics.json -> categorical_verdict.gate_atoms",
            "why_it_is_the_gate": (
                "reach-only paralogue collision at %d atoms is %s across the three matched conformer scopes, "
                "and climbs to %s at 16 and %s at 20. The gate figure is the one that does NOT depend on the "
                "exposure criterion, so it is the durable part of the mechanism."
                % (gate, _band(dyn, gate), _band(dyn, 16), _band(dyn, 20))),
        },
        "candidate_basins": {
            "_rule": ("DERIVED, not listed: every meta-basin in `meta_basins_ranked` whose "
                      "`term_a_union.C397.min_linker_atoms` is <= the gate. Deriving it is the point — the "
                      "premise that only `crbn|M17` qualifies had never been checked."),
            "n_meta_basins_scanned": len(basins["meta_basins_ranked"]),
            "selected": [{"meta_basin_id": m["meta_basin_id"], "arm_id": m["arm_id"],
                          "c397_min_linker_atoms": m["term_a_union"]["C397"]["min_linker_atoms"],
                          "in_the_committed_CONFIRMED_set": m["meta_basin_id"] in NLD.CONFIRMED,
                          "term_b_exceeds_background": m["term_b_exceeds_background"],
                          "pose_surviving_fraction": m["pose_surviving_fraction"],
                          "total_members": m["total_members"]}
                         for m in cands],
            "committed_CONFIRMED_set": NLD.CONFIRMED,
            "_finding": _basin_finding(cands),
        },
        "the_four_floors": {
            "_why_four": (
                "'no construct exists at 12' can be true for four different reasons and they have four "
                "different remedies. Naming which one binds is the whole deliverable."),
            "floor_chemistry": dict(chem_floor, _reading=(
                "the shortest ONE-BRANCH backbone the committed building-block grid can assemble at all: "
                "%d atoms = 1 acyl C + %s + 1 acyl C + a 3-atom branch residue + 1 amide N + %s + %d "
                "warhead-tail atom(s). Basin-independent."
                % (chem_floor["n_backbone_atoms"], chem_floor["linker_segments"][0],
                   chem_floor["linker_segments"][1],
                   NLD.WARHEAD_HANDLE[chem_floor["warhead_handle"]]["tail_atoms"]))),
            "floor_span": "per placement — the anchor-anchor distance / 1.25 A per atom. See per_placement.",
            "floor_reach": "per placement — the exact three-ball rule onto C397 SG. See per_placement.",
            "floor_filter": ("per placement — the preregistered rung-5b downselect. See per_placement. "
                             "Thresholds imported: %s" % json.dumps(
                                 {k: v for k, v in NLD.FILTER.items()
                                  if k in ("min_member_fraction_comfortable", "max_strain_kT_at_placement",
                                           "max_backbone_atoms", "must_span_the_floor")})),
        },
        "per_placement": per_placement,
        "answer": answer,
        "the_candidate": _with_margin(_candidate_record(candidate, chem, gate), windows, gate)
                         if candidate else None,
        "the_candidates_matched_set": {
            "_why": ("a covalent DESIGN without its comparators is not usable evidence. Same basin, same "
                     "placement, same handle, same segments, same backbone length: `acrylamide` is the "
                     "IRREVERSIBLE comparator the reversible preference is argued against, `cyanoprop` is "
                     "`cyac_me` with the Michael acceptor reduced and nothing else changed, and `cyac_ph` is "
                     "the beta-aryl residence-time sibling — a second design, not a control."),
            "constructs": controls_for(candidate),
        },
        "the_crbn_alternative": {
            "_why_carried_separately": (
                "rung `5b-T`'s E3 is CRBN, so a VHL candidate does not answer its question. This is the best "
                "CRBN construct at the gate; its shortfall is STATED, not ranked away."),
            "⛔_the_crbn_answer": _crbn_reading(crbn_alt, windows, gate),
            "construct": _with_margin(_candidate_record(crbn_alt, crbn_chem, gate), windows, gate)
                         if crbn_alt else None,
            "matched_set": controls_for(crbn_alt),
        },
        "chemoselectivity_windows_at_the_gate": {
            "_what": ("per gate-clearing placement: the interval of backbone-atom counts over which C397 is "
                      "in reach and NO conserved cysteine is, under BOTH conventions and at TWO pendant "
                      "reaches — the preregistered `rung5a_convention` (3.0 A, conservative) and the "
                      "`dab_branch` (8.75 A) the electrophile constructs actually carry."),
            "computed_by": "nr4a3_linker_covalent_reach.chemoselectivity_margin (never reimplemented here)",
            "by_placement": windows,
        },
        "paralogues_at_its_own_length": (collision_at(dyn, candidate["n_backbone_atoms_intended"])
                                         if candidate else None),
        "reach_margin_both_conventions": {
            "_what": ("`through_space` (the committed three-ball rule — an UPPER bound on reachability) and "
                      "`corridor` (additionally requires a non-clashing branch position with a clash-free "
                      "straight arm to the SG — a NECESSARY condition, still not sufficient), for every "
                      "unique cysteine at every gate-clearing placement, in nr4a3-opened.pdb."),
            "clash_cutoffs_A": list(CR.CLASH_SWEEP_A),
            "primary_cutoff_A": CR.CLASH_PRIMARY_A,
            "unique_cysteines": sorted(unique_labels),
            "nr4a3_unique": conventions,
            "conserved_competitors": conserved,
            "anchor_clearance": conv["anchor_clearance"],
            "invariant_violations": conv["invariant_violations"],
            "⚠_never_merge_them": (
                "the categorical audit found the covalent-reach lane's `verdict()` building its refuted list "
                "from `best_corridor` alone while `best_through_space` two fields away disagreed — which is "
                "how C559 came to be labelled refuted when it survives at one through-space cell. Every "
                "statement here names its convention."),
        },
        "what_this_licenses": _licences(),
        "carried_honestly": _carried(dyn),
        "_limits": _limits(),
        "flagged_not_fixed": _flagged(),
    }
    return out


def _rdkit_version():
    try:
        import rdkit
        return rdkit.__version__
    except Exception:                                     # pragma: no cover - RDKit is present in CI
        return None


def _with_margin(rec, windows, gate):
    """Attach the construct's own REACH MARGIN under both conventions and both pendant reaches.

    margin = (backbone atoms the construct HAS) - (backbone atoms C397 REQUIRES). Negative means the
    construct does not reach under that convention, and it is reported as a negative number rather than as
    an absence, because "does not reach" and "was not computed" must never render alike.
    """
    if rec is None:
        return None
    key = "%s@%s" % (rec["designed_for_basin"], rec["designed_at_placement"])
    n = rec["n_backbone_atoms_intended"]
    marg = {}
    for pend, w in (windows.get(key) or {}).items():
        if not w:
            continue
        marg[pend] = {
            conv: {"c397_required_atoms": w[conv]["c397_required_atoms"],
                   "reach_margin_atoms": (n - w[conv]["c397_required_atoms"]
                                          if w[conv]["c397_required_atoms"] is not None else None),
                   "reaches": bool(w[conv]["c397_required_atoms"] is not None
                                   and n >= w[conv]["c397_required_atoms"]),
                   "chemoselectivity_window_atoms": [w[conv]["lo"], w[conv]["hi"]],
                   "construct_is_inside_the_window": bool(
                       w[conv]["lo"] is not None and w[conv]["hi"] is not None
                       and w[conv]["lo"] <= n <= w[conv]["hi"]),
                   "first_conserved_cysteine_in_reach": w[conv]["blocked_by"],
                   "first_conserved_cysteine_at_atoms": w[conv]["blocked_at_atoms"]}
            for conv in ("through_space", "corridor")}
        marg[pend]["clears_under_both_conventions"] = bool(
            marg[pend]["through_space"]["construct_is_inside_the_window"]
            and marg[pend]["corridor"]["construct_is_inside_the_window"])
    rec["reach_margin_at_its_own_length"] = {
        "_what": ("backbone atoms the construct HAS minus what C397 REQUIRES, under both conventions, at "
                  "the preregistered `rung5a_convention` pendant reach (3.0 A, conservative) and at the "
                  "`dab_branch` reach (8.75 A) this molecule actually carries. Corridor cutoff %.1f A."
                  % CR.CLASH_PRIMARY_A),
        "by_pendant_reach": marg,
    }
    return rec


def _crbn_reading(crbn_alt, windows, gate):
    if crbn_alt is None:
        return "no CRBN construct exists at or below the gate."
    key = "%s@%s" % (crbn_alt["designed_for_basin"], crbn_alt["designed_at_placement"])
    w = (windows.get(key) or {})
    ts = w.get("dab_branch", {}).get("through_space", {})
    co = w.get("dab_branch", {}).get("corridor", {})
    ts_c = w.get("rung5a_convention", {}).get("through_space", {})
    co_c = w.get("rung5a_convention", {}).get("corridor", {})
    return (
        "A %d-atom CRBN construct on `%s` EXISTS and reaches C397 under the THROUGH-SPACE convention "
        "(C397 required %s atoms at the dab pendant, %s at the conservative preregistered reach; the "
        "chemoselective window is [%s, %s] and %d sits at its top edge). ⛔ It does NOT reach under the "
        "CORRIDOR convention at %.1f A, which needs %s atoms (dab) / %s atoms (conservative) — so requiring "
        "a non-clashing branch position with a clash-free arm to the SG puts the CRBN floor at %s, not %d. "
        "**The honest CRBN answer is therefore convention-dependent, and the two conventions must not be "
        "merged.** Rung `5b-T` should read this as: a gate-length CRBN degrader is available on an "
        "upper-bound reach rule only, and its corridor floor is above the gate."
        % (gate, crbn_alt["designed_for_basin"],
           ts.get("c397_required_atoms"), ts_c.get("c397_required_atoms"),
           ts.get("lo"), ts.get("hi"), gate, CR.CLASH_PRIMARY_A,
           co.get("c397_required_atoms"), co_c.get("c397_required_atoms"),
           co.get("c397_required_atoms"), gate))


def _basin_finding(cands):
    """The candidate-set reading, built from a LOOKUP rather than a positional zip.

    ⚠ The first version of this string zipped a name order against a differently-sorted value order and
    published three basins with each other's atom counts — a populated field that was never measured
    (CLAUDE.md §4b). Every number below is fetched by id.
    """
    by_id = {m["meta_basin_id"]: m["term_a_union"]["C397"]["min_linker_atoms"] for m in cands}
    already = sorted(b for b in by_id if b in NLD.CONFIRMED)
    novel = sorted(b for b in by_id if b not in NLD.CONFIRMED)
    fmt = lambda ids: ", ".join("`%s` at %d" % (b, by_id[b]) for b in ids)     # noqa: E731
    return (
        "%d basin(s) qualify, not one — and the composition is the finding. %s %s ALREADY in the committed "
        "CONFIRMED set and %s already enumerated against, so the missing 12-atom molecule was never a "
        "missing basin: it was a downselect outcome. %s the enumerator's hard-coded `CONFIRMED` list "
        "excludes."
        % (len(by_id),
           fmt(already) or "No basin is",
           "are" if len(already) != 1 else "is",
           "were" if len(already) != 1 else "was",
           ("%s %s what" % (fmt(novel), "are" if len(novel) != 1 else "is")) if novel
           else "No qualifying basin is one"))


def _band(dyn, n):
    vals = [sv["by_linker_atoms"][str(n)]["P_paralogue_also_labelled_given_nr4a3"]
            for sv in dyn["categorical_verdict"]["by_scope"].values()]
    return "%.5g-%.5g" % (min(vals), max(vals)) if min(vals) != max(vals) else "%.5g" % vals[0]


def _candidate_record(c, chem, gate):
    f = c["basin_fidelity"]
    return {
        "construct_id": c["construct_id"],
        "designed_for_basin": c["designed_for_basin"],
        "designed_at_placement": c["designed_at_placement"],
        "placement_basin_id": c["placement_basin_id"],
        "placement_pose_id": c["placement_pose_id"],
        "e3": NLD.E3_HANDLE[c["e3_handle"]]["name"],
        "e3_handle": c["e3_handle"],
        "warhead_handle": c["warhead_handle"],
        "warhead_handle_name": NLD.WARHEAD_HANDLE[c["warhead_handle"]]["name"],
        "linker_segments": c["linker_segments"],
        "linker_blocks": [NLD.LINKER_SEGMENT[s]["block"] for s in c["linker_segments"]],
        "linker_class": c["linker_class"],
        "pendant": c["pendant"],
        "pendant_name": NLD.PENDANT[c["pendant"]]["name"],
        "pendant_reversible": NLD.PENDANT[c["pendant"]]["reversible"],
        "branch_residue": c["branch_residue"],
        "stereocentre": c["stereocentre"],
        "branch_target": c["branch_target"],
        "branch_k_from_warhead": c["branch_k_from_warhead"],
        "branch_window": c["branch_window"],
        "n_backbone_atoms_intended": c["n_backbone_atoms_intended"],
        "n_backbone_atoms_measured_by_rdkit": (chem or {}).get("n_backbone_atoms_measured"),
        "smiles": c["smiles"],
        "canonical_smiles": (chem or {}).get("canonical_smiles"),
        "inchikey": (chem or {}).get("inchikey"),
        "rdkit_ok": (chem or {}).get("ok"),
        "rdkit_errors": (chem or {}).get("errors"),
        "rdkit_warnings": (chem or {}).get("warnings"),
        "descriptors": (chem or {}).get("descriptors"),
        "synthetic_route": c["synthetic_route"],
        "basin_fidelity": f,
        "span_window_A": c["span_window_A"],
        "_kept_by_the_preregistered_filter": c["_kept_by_filter"],
        "_why_this_one": (
            "AT the gate (%d atoms), not below it — below 12 the collision measurement grid has no point at "
            "all, so a shorter construct would trade a MEASURED number for an extrapolated one, which is a "
            "worse deal than one backbone atom. Then, in order: clears the gate under BOTH reach "
            "conventions at the conservative preregistered pendant reach; passes the chain-strain term "
            "(physics, not policy); carries the REVERSIBLE-covalent electrophile, which is rung 5b's stated "
            "preference and the property that preserves catalytic turnover; sits on the basin with the most "
            "pose evidence. Ties break on the construct id so this artifact is reproducible." % gate),
    }


def _answer(gate, per_placement, candidate, chem, chem_floor, crbn_alt, crbn_chem):
    geo = [p for p in per_placement if p["clears_the_gate_geometrically"]]
    filt = [p for p in per_placement if p["clears_the_gate_under_the_preregistered_filter"]]
    both = [p for p in geo if p.get("gate_clears_both_conventions_rung5a_convention")]
    floors = {p["meta_basin_id"] + "@" + p["placement_label"]:
              {"floor_span_atoms": p["floor_span_atoms"],
               "floor_chemistry_atoms": p["floor_chemistry_atoms"],
               "floor_reach_atoms": p["floor_reach_atoms"],
               "floor_filter_atoms": p["floor_filter_atoms"]}
              for p in per_placement}
    binding = {p["meta_basin_id"]: p["at_the_gate"]["binding_terms"]
               for p in geo if p["at_the_gate"]}
    union = sorted({t for v in binding.values() for t in v})
    universal = sorted(set.intersection(*[set(v) for v in binding.values()])) if binding else []
    return {
        "does_a_construct_at_or_below_%d_atoms_exist" % gate: {
            "geometry_and_chemistry": "YES" if geo else "NO",
            "and_under_BOTH_reach_conventions": "YES" if both else "NO",
            "under_the_preregistered_rung_5b_filter": "YES" if filt else "NO",
            "⚠_these_are_three_questions_not_one": (
                "(1) can a molecule be DRAWN that spans the anchors and puts an electrophile on C397's SG? "
                "(2) does it still reach when the branch position must avoid the protein and the pendant arm "
                "must be clash-free — the CORRIDOR convention? (3) does it clear a downselect designed to "
                "keep constructs that hold a WHOLE BASIN? They give different answers, and which one is "
                "being quoted has to travel with the number."),
        },
        "shortest_backbone_per_basin_and_placement": floors,
        "which_basins_clear_the_gate_under_both_conventions": [p["meta_basin_id"] for p in both],
        "the_true_floor_and_what_forces_it": {
            "geometric_and_chemical_floor_atoms": min(
                [p["floor_reach_atoms"] for p in per_placement if p["floor_reach_atoms"]], default=None),
            "forced_by": ("the building-block grid: a one-branch chain cannot be shorter than %d atoms "
                          "(%s), and that bound is basin-independent — it is 1 acyl C + SEG1 + 1 acyl C + "
                          "a 3-atom branch residue + 1 amide N + SEG2 + the warhead tail"
                          % (chem_floor["n_backbone_atoms"], "+".join(chem_floor["linker_segments"]))),
            "filter_floor_atoms": min([p["floor_filter_atoms"] for p in per_placement
                                       if p["floor_filter_atoms"]], default=None),
            "filter_terms_binding_at_the_gate_per_basin": binding,
            "binding_at_every_gate_clearing_basin": universal,
            "binding_at_at_least_one": union,
            "_reading": (
                "★ THE COMMITTED LIBRARY'S FLOOR OF 14 IS NOT A GEOMETRIC FACT AND NOT A CHEMICAL ONE. "
                "The one term that binds at EVERY gate-clearing basin is %s — a basin-BREADTH policy, not "
                "physics. Chain strain binds at only one of them. And the breadth policy is in direct "
                "tension with the selectivity mechanism: comfortably covering more of a basin's member "
                "placements requires a LONGER chain, and a longer chain is exactly what raises paralogue "
                "collision (%s). ⛔ Reported, NOT relaxed — moving a preregistered threshold after seeing "
                "the answer is the tuning rung 5b forbids. The right consumer of this is rung `5b-T`'s arm "
                "(C), which can now be run at the gate length with a named molecule and the trade stated, "
                "instead of at the shortest committed length with the 12-atom figure unclaimable."
                % (", ".join("`%s`" % t for t in universal) or "no single term",
                   "the same artifact's `by_linker_atoms` table")),
        },
        "candidate_construct_id": candidate["construct_id"] if candidate else None,
        "candidate_inchikey": (chem or {}).get("inchikey"),
        "crbn_alternative_construct_id": crbn_alt["construct_id"] if crbn_alt else None,
        "crbn_alternative_inchikey": (crbn_chem or {}).get("inchikey"),
    }


def _licences():
    return {
        "licenses": [
            "TARGET-ENGAGEMENT SELECTIVITY ONLY, and only as a geometric statement: at this backbone length "
            "a construct that reaches an NR4A3-unique cysteine is measured not to reach a paralogue one in "
            "matched placements.",
            "A design ORDERING — shorter backbone is better on the selectivity axis, with the cost curve "
            "measured rather than assumed.",
            "A molecule that can be drawn, named and re-parsed: SMILES + InChIKey + an RDKit-re-derived "
            "backbone length and branch index.",
        ],
        "does_NOT_license": [
            "binding affinity of anything, to anything",
            "electrophile reactivity, thiol pKa, adduct stability or chemoproteomic selectivity",
            "ternary complex formation, cooperativity or a productive geometry — that is rung `5b-T`, and "
            "this rung does not address it",
            "degradation, efficacy, a therapeutic window, safety or clinical readiness",
            "proteome-wide selectivity of any kind: the paralogue comparison is NR4A1/NR4A2 and nothing else",
            "synthetic feasibility beyond a retrosynthetic annotation over catalogue building blocks",
        ],
    }


def _carried(dyn):
    cv = dyn["categorical_verdict"]
    return [
        {"claim": "C420 is refuted; C559 is NOT",
         "detail": ("C420 is refuted at 0 of 60 (placement x pendant) cells under both conventions. C559 is "
                    "refuted under the corridor convention everywhere and at 59 of 60 through-space cells, "
                    "surviving in exactly one — `vhl|M3@term_a_exemplar | dab_branch`, in 2 of that cell's "
                    "19 conformers. That is the optimistic best-of-N anchor with the longest pendant, i.e. "
                    "the weakest form of a survival — and it is still not zero. **C397 is the only clean "
                    "target**, which is why this probe is scoped to it."),
         "source": "research/modalities/categorical-axis-audit.json -> branch_1b_claim_verdicts"},
        {"claim": "the paralogues are not out of REACH — they are out of the EXPOSED set",
         "detail": ("NR4A1 C465 sits inside the %d-atom envelope in 68 of 75 unbiased frames — MORE often "
                    "than NR4A3's own C397 at 65 of 75. It is excluded only by an RSA that never exceeds "
                    "0.2126 against the %.2f cutoff. So 'reach-only collision ~0 at the gate' is a statement "
                    "about MATCHED PLACEMENTS — same warhead exit anchor, same E3 anchor, same budget — and "
                    "NOT a statement about envelopes. The distinction is load-bearing and must survive every "
                    "quotation of the number." % (cv["gate_atoms"], cv["exposed_rsa_cutoff"])),
         "source": "research/modalities/nr4a-paralogue-dynamics.json + categorical-axis-audit.json"},
        {"claim": "the exposure criterion fails its own positive control",
         "detail": ("`EXPOSED_RSA = %.2f` scores NR4A1 Cys551 — the literature-anchored celastrol site — as "
                    "not exposed, at RSA 0.165 on the state-matched opened model and in 0 of 25 "
                    "metadynamics frames. Every `reach_and_exposed` figure inherits that demonstrated false "
                    "negative. ★ At the %d-atom gate the categorical statement does not rest on it: "
                    "reach-only collision there is already <= 0.3 %%. At 16 and 20 atoms it does."
                    % (cv["exposed_rsa_cutoff"], cv["gate_atoms"])),
         "source": "research/modalities/nr4a-paralogue-dynamics.json -> categorical_verdict"},
        {"claim": "this inherits V3's SITE-selection failure, not a pose-accuracy one",
         "detail": ("The warhead exit vector is MARGINALISED over 12 pocket-mouth anchors sampled in a shell "
                    "around the cryptic-pocket centroid, precisely because no cmpd19 pose exists in this "
                    "frame (`nr4a3-orientation-basins.json` `_limits[0]`; "
                    "`nr4a3_basin_search.build_pose_ensemble`). So a POSE-accuracy failure is already "
                    "absorbed — no docked pose is consumed. A SITE-selection failure voids every reach "
                    "number here, and site selection is exactly what `V3` returned INCONCLUSIVE on, 6 of 6 "
                    "pairs. **This probe depends on the site, not on the pose.**"),
         "source": "research/modalities/categorical-axis-audit.json -> pose_dependency_split"},
        {"claim": "the reach statistic that selected these basins is a best-of-N",
         "detail": ("`term_a_union.C397.min_linker_atoms` is a MINIMUM over a basin's sampled member "
                    "placements. The achieving member is not the basin's representative — at the "
                    "representative geometry the same basins need 16-35 atoms. Every record here carries "
                    "BOTH placements for that reason, and the candidate is labelled with which one it was "
                    "designed at."),
         "source": "research/modalities/nr4a3-linker-design.json -> _corrections_to_rung_5a"},
    ]


def _limits():
    return [
        "GEOMETRY AND CHEMISTRY ONLY. No energy of any kind is computed — not binding, not reaction, not "
        "solvation. A construct that clears every test here may still not bind, react, form a ternary or "
        "degrade anything.",
        "One static opened NR4A3 conformer carries the anchors and the corridor test. The paralogue "
        "collision numbers come from the matched MD ensembles; the reach margins do not.",
        "The `term_a_exemplar` placement is a BEST-OF-N over a basin's members and is the optimistic end of "
        "that basin. Every candidate designed at it inherits that, and it is labelled on every record.",
        "`crbn|M17` is NOT in the rung-5a CONFIRMED set. It exceeds the term-(b) background (3.87x) but "
        "persists in only 3 of 12 poses (0.25 pose-surviving fraction) against `crbn|M0`'s 0.917. It is a "
        "geometrically-qualifying basin with WEAKER basin evidence, and that trade is the candidate's "
        "central liability — not a footnote.",
        "The corridor convention is a NECESSARY condition, not a sufficient one: it tests one branch "
        "position and a straight arm, and does not thread the backbone, score torsions, or check that a "
        "clash-free pocket is connected to bulk solvent.",
        "The collision measurement grid is {12, 14, 16, 20}. Nothing between those points is measured, and "
        "nothing BELOW 12 is measured at all.",
        "The covalent handle is an unresolved liability, not an upgrade: electrophile promiscuity cannot be "
        "assessed without chemoproteomics, and it must be reported alongside the parent warhead's published "
        "MYC induction.",
        "A one-branch construct carries the electrophile OR a wedge element, not both. This probe enumerates "
        "the electrophile branch onto C397; the matched-pair wedge is a separate design.",
    ]


def _flagged():
    return [
        {"finding": "the committed `nr4a3-linker-design.json` no longer reproduces from its own code",
         "measured": ("regenerating with the current `nr4a3_linker_design.py` gives 57 constructs against "
                      "the committed 54, and 3,852 enumerated against 3,544. The difference is the wedge "
                      "site: `crbnM0@ex_5amide_e4-a2_pyr3` becomes `crbnM0@ex_5amide_a9-a2_pyr3`, and "
                      "`vhl|M14` gains three pyr3/ph constructs it did not have."),
         "why_it_matters": ("rung `5b-T` takes its degrader SMILES from the committed library, so the "
                            "library being stale relative to its generator is a provenance problem for that "
                            "rung, not a cosmetic one."),
         "not_fixed_here_because": ("regenerating it would rewrite a preregistered enumeration on a lane "
                                    "this probe does not own, and the drift is unrelated to the question "
                                    "asked. Flagged with the evidence; the fix belongs to whoever owns the "
                                    "wedge-site change."),
         "how_to_reproduce": "python3 research/modalities/nr4a3_linker_design.py --out /tmp/regen.json"},
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true",
                    help="regenerate and compare against the committed artifact (ignoring the timestamp)")
    args = ap.parse_args(argv)
    doc = build()
    if args.check:
        with open(args.out, encoding="utf-8") as fh:
            old = json.load(fh)
        a, b = dict(old), dict(doc)
        a.pop("_generated", None)
        b.pop("_generated", None)
        same = json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
        print("[short-linker-probe] --check: %s" % ("IDENTICAL" if same else "DIFFERS"))
        return 0 if same else 1
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    ans = doc["answer"]["does_a_construct_at_or_below_%d_atoms_exist" % doc["gate"]["backbone_atoms"]]
    print("[short-linker-probe] geometry+chemistry: %s | preregistered filter: %s"
          % (ans["geometry_and_chemistry"], ans["under_the_preregistered_rung_5b_filter"]))
    print("[short-linker-probe] candidate: %s  %s" % (doc["answer"]["candidate_construct_id"],
                                                      doc["answer"]["candidate_inchikey"]))
    print("[short-linker-probe] wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
