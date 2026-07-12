#!/usr/bin/env python3
"""
Pure RBFE (relative binding free energy) definitions + ΔΔG-cycle bookkeeping for the NR4A3 lead-opt series.

WHY RBFE (not ABFE) here. The FEP question is "does lo_m0_NCCO bind NR4A3 *better than* denovo_401, and does
it stay selective?" lo_m0_NCCO = denovo_401 + one ortho-acetamido group — a congeneric pair — so the affinity
DIFFERENCE is a small alchemical morph (grow the acetamido) with the shared scaffold cancelling by
construction. RBFE gives ΔΔG = ΔG_bind(B) − ΔG_bind(A) per receptor at a fraction of ABFE's cost + variance,
and (unlike ABFE) needs NO Boresch restraint / standard-state correction (both ligands share the pose →
those cancel). The absolute for B, if wanted, is anchored on denovo_401's *existing* ABFE.

This module is the PURE core (no OpenMM / OpenFE / IO): the edge/leg enumeration, the ΔΔG-cycle bookkeeping
(ΔΔG_bind = ΔG_complex(A→B) − ΔG_solvent(A→B)), the anchoring onto 401's ABFE, the selectivity read-out, and
an optional RDKit-MCS atom-map sanity check. It is unit-tested directly; the GPU engine (nr4a3_rbfe.py) and
the SageMaker submitter consume it. Mirrors the role fep_sharding.py plays for the ABFE engine.
"""

LIGAND_A = "denovo_401"                        # reference (its ABFE is already run)
LIGAND_B = "lo_m0_NCCO_gen"                    # lead (401 + ortho-acetamido)
RECEPTORS = ["nr4a3", "nr4a1", "nr4a2"]

SMILES = {
    "denovo_401":     "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1",
    "lo_m0_NCCO_gen": "COC[C@H](c1ccccc1NC(C)=O)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1",
    "lo_m0_CC":       "CCc1ccccc1[C@@H](COC)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1",   # ethyl sibling (2nd edge)
    # congeneric binary-RBFE pilot edge (Zaienne-19 anchor -> 5-NH2 exit vector; both neutral, single-site)
    "zaienne_cmpd19": "COC(=O)c1c[nH]c2ccc(Br)cc12",
    "cw_ev_5nh2":     "COC(=O)c1c[nH]c2ccc(N)cc12",
}

# denovo_401 ABFE anchor (per-receptor ΔG_bind, kcal/mol) — the numbers RBFE rides to convert its ΔΔG into B's
# absolute. UPDATED 2026-07-06 to the CONVERGED r1 (n_iter=2000, 2 ns/window) + the engine CALIBRATION
# (nr4a3-abfe-calibration.json): the openmmtools ABFE engine UNDER-BINDS by a measured +7.1 kcal/mol (T4-lysozyme
# ·benzene zero), so the raw-engine absolutes are recontextualized. Values below are OFFSET-CORRECTED
# (raw − 7.1): NR4A3 is a FAVOURABLE binder (~−4.5), both paralogues do NOT bind (positive). Derived from the
# converged selectivity ΔΔG (−6.9 vs NR4A1, −5.5 vs NR4A2) + NR4A3 corrected −4.5.
#   ⚠ These absolutes are ONE-SIDED (conservative/least-binding): the +7.1 offset is from a RIGID cavity; the
#   cryptic NR4A3 pocket under-samples reorganization MORE, so the true NR4A3 binding is likely ≥ this favourable.
#   The SELECTIVITY ΔΔG is OFFSET-FREE and is the load-bearing anchor; never quote a raw engine absolute as
#   "doesn't bind". See paper §4 + nr4a3-abfe-calibration.json "go_forward_rule".
ANCHOR_401_ABFE = {"nr4a3": -4.5, "nr4a1": 2.4, "nr4a2": 1.0}      # offset-corrected converged r1
ANCHOR_401_ABFE_RAW = {"nr4a3": 2.6, "nr4a1": 9.5, "nr4a2": 8.1}   # raw engine (add +7.1 offset)
ANCHOR_401_SELECTIVITY_DDG = {"nr4a1": -6.9, "nr4a2": -5.5}        # offset-FREE (NR4A3 − paralogue); load-bearing
ABFE_ENGINE_OFFSET = 7.1                                            # under-binding, from T4L·benzene calibration


def rbfe_legs(receptors=RECEPTORS):
    """The RBFE legs = alchemical MORPH legs (A→B), NOT absolute-decoupling legs. One SHARED solvent-morph leg
    (identical A→B in water, cancels common-mode ligand error) + one complex-morph leg per receptor. Returns
    [(name, receptor, leg_kind)] — the same shape nr4a3_abfe_sagemaker._legs() emits, so the spot-Training
    submitter + sharding reuse unchanged."""
    return [("solvent", "shared", "solvent")] + [(f"complex-{r}", r, "complex") for r in receptors]


def ddg_bind(dg_complex_morph, dg_solvent_morph):
    """RBFE thermodynamic cycle for ONE receptor:
        ΔΔG_bind(A→B) = ΔG_complex(A→B) − ΔG_solvent(A→B)
    (both are alchemical A→B free energies; their difference is the change in binding free energy). More
    negative ⇒ B binds that receptor tighter than A."""
    return dg_complex_morph - dg_solvent_morph


def absolute_dg_B(ddg_bind_value, receptor, anchor=ANCHOR_401_ABFE):
    """B's absolute ΔG_bind for a receptor = A's ABFE anchor + the RBFE increment. Only as good as the anchor;
    the increment (better-than-401 by how much) is anchor-free and is the primary result."""
    return anchor[receptor] + ddg_bind_value


def selectivity_from_rbfe(ddg_by_receptor, anchor=ANCHOR_401_ABFE, target="nr4a3",
                          paralogues=("nr4a1", "nr4a2")):
    """B's selectivity ΔΔG (target vs each paralogue), built from the per-receptor RBFE increments + the 401
    anchor. Returns {paralogue: ΔG_bind(B,target) − ΔG_bind(B,paralogue)} — more NEGATIVE = more target-selective
    (B binds the target tighter than the paralogue). Note ΔG_bind(B,t) − ΔG_bind(B,p) = [anchor_t − anchor_p]
    (= 401's selectivity) + [ΔΔG_t − ΔΔG_p] (= the RBFE selectivity change), so the anchor's *selectivity* (its
    better-behaved part) carries, and RBFE supplies the change."""
    dgB = {r: absolute_dg_B(ddg_by_receptor[r], r, anchor) for r in ddg_by_receptor}
    return {p: round(dgB[target] - dgB[p], 3) for p in paralogues}


def selectivity_change_only(ddg_by_receptor, target="nr4a3", paralogues=("nr4a1", "nr4a2")):
    """The anchor-FREE selectivity read: how much MORE (or less) target-selective B is than A, from RBFE alone
    (ΔΔG_target − ΔΔG_paralogue). Negative ⇒ B is more target-selective than 401. Reported alongside the
    anchored absolute so a shaky anchor never contaminates the *relative* selectivity claim."""
    return {p: round(ddg_by_receptor[target] - ddg_by_receptor[p], 3) for p in paralogues}


def mapping_summary(smi_a, smi_b):
    """RDKit-MCS sanity check on the A↔B atom map (optional; the production map is OpenFE/LOMAP at runtime).
    Confirms the two ligands share a large common scaffold and differ only by a small unique region (here the
    ortho-acetamido) — a well-behaved single-edge RBFE morph. Returns {} if RDKit is unavailable."""
    try:
        from rdkit import Chem
        from rdkit.Chem import rdFMCS
    except ImportError:
        return {}
    ma, mb = Chem.MolFromSmiles(smi_a), Chem.MolFromSmiles(smi_b)
    if ma is None or mb is None:
        return {"error": "unparseable SMILES"}
    res = rdFMCS.FindMCS([ma, mb], completeRingsOnly=True, ringMatchesRingOnly=True, timeout=30)
    n_common = res.numAtoms
    return {
        "mcs_smarts": res.smartsString,
        "n_common_atoms": n_common,
        "n_unique_A": ma.GetNumAtoms() - n_common,
        "n_unique_B": mb.GetNumAtoms() - n_common,
        "well_behaved_edge": bool(n_common >= 0.7 * min(ma.GetNumAtoms(), mb.GetNumAtoms())
                                  and (mb.GetNumAtoms() - n_common) <= 10),
    }


def edge_plan(ligand_a=LIGAND_A, ligand_b=LIGAND_B, receptors=RECEPTORS):
    """A self-describing plan for one RBFE edge: the ligands, the legs, and (if RDKit present) the map sanity.
    Used by mode=plan (dry-run, no GPU) to show exactly what would run."""
    plan = {"edge": f"{ligand_a} -> {ligand_b}", "ligand_A": ligand_a, "ligand_B": ligand_b,
            "receptors": list(receptors), "legs": rbfe_legs(receptors),
            "anchor_A_abfe": ANCHOR_401_ABFE,
            "note": "RBFE morph A->B; ΔΔG_bind = ΔG_complex - ΔG_solvent per receptor; no Boresch/SSC "
                    "(cancels); absolute for B anchored on A's existing ABFE."}
    if ligand_a in SMILES and ligand_b in SMILES:
        plan["map_sanity"] = mapping_summary(SMILES[ligand_a], SMILES[ligand_b])
    return plan
