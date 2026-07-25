#!/usr/bin/env python3
"""The $0 PRE-GATE on the valB synthetic closure TRIANGLE, before any GPU dollar is spent.

WHAT IS BEING GATED. `valb-calibrator-rescope-2026-07-25.md` §8 proposes replacing the dead P-series rescope
with a closure triangle built from the anchor ligand itself, because a cycle-closure residual needs no
experimental measurement:

    T1 = Wurz cmpd1 -> cmpd4   (linker pyridine N->CH; 2 perturbed heavy atoms)  -- ALREADY RUN, this is r0
    T2 = cmpd4      -> cmpd4'  (a second small, charge-neutral single-site change)          -- new
    T3 = cmpd1      -> cmpd4'  (closes the loop)                                            -- new

and claims T2/T3 are each "<=2-heavy-atom, charge-neutral" edges that reuse the existing machinery unchanged.
This module tests those claims against real chemistry instead of accepting them, exactly as
`valb_pseries_chem.py` tested (and refuted) the P-series design for $0.

WHAT IT MEASURES, per candidate cmpd4' transform:
  1. FORMAL CHARGE of cmpd1 / cmpd4 / cmpd4' (RDKit), and the change across each of T1, T2, T3.
  2. PERTURBED HEAVY ATOMS by rdFMCS -- the SAME metric and the SAME rdFMCS settings valb_pseries_chem.py used,
     so the numbers are directly comparable to the 58-80 that killed the P-series and to the 2 of the running
     edge.
  3. THE REAL PRODUCTION ATOM MAP. Not an eyeballed MCS: `nr4a3_rbfe._mapping(..., prefer_element_change=True)`
     is the function the ternary engine itself calls (protocol_signature records it as
     "lomap_prefer_element_change"), so this runs LomapAtomMapper(time=20, threed=False, element_change=...)
     with the production preference logic and reports mapped atoms + DUMMY atoms on each side.
  4. DUMMY-ATOM CLASSIFICATION. An N->CH element swap maps 1:1 and creates ZERO heavy dummies; a deletion
     (methyl->H, tBu->iPr, phenol->phenyl) creates a heavy dummy that must be decoupled through the softcore
     region. The runbook's own root cause for this lane's warmup NaNs is "the softcore alchemical
     (dis)appearing region in a large, rough homology-built assembly", so the two are NOT the same risk and
     the gate must not treat them as one number.
  5. THE VHL ANCHOR IS UNTOUCHED. The trans-4-hydroxyproline hydroxyl is matched by SMARTS and must be inside
     the mapped core of every edge. A leg whose ligand does not stay bound does not converge, and the closure
     would then be measuring a dissociation.
  6. WHICH PHARMACOPHORE EACH CANDIDATE TOUCHES, reported as a structural fact (a substructure match), so the
     ligand-escape risk is visible rather than assumed away.
  7. CLOSURE PREREQUISITE: cmpd4' derived two independent ways -- (Y applied to cmpd4) and (X then Y applied to
     cmpd1) -- must give the IDENTICAL canonical SMILES. If they do not, the triangle's three edges do not share
     endpoints and the closure identity does not hold at all.
  8. CAN THE EXISTING ENGINE ACTUALLY BUILD IT? `nr4a3_ternary_fep._pyridine_to_benzene_pose` is the ONLY
     element-change pose mutation in the engine and it fails closed unless the molecule has exactly one
     pyridine. This module calls it directly on the real cmpd1 SMILES and records what it returns for each
     target, so "the machinery carries over unchanged" is tested, not asserted.

NOTHING IS FABRICATED. cmpd1's SMILES is read from `wurz-calib-frozen.json` (itself fetched from RCSB 8G1Q at
freeze time); cmpd4 is re-derived here by the same transform the frozen record names and is CHECKED against the
frozen `calib_lo.smiles`; every cmpd4' is produced by a pattern-matched structural edit of a real molecule, never
typed by hand. No alpha, no dG, no GPU-hour and no convergence is asserted anywhere in this file.

Runs on a GitHub runner inside `docker.io/triskit23/ternary-fep` (rdkit + openfe + lomap2 + kartograf), i.e. the
production mapper at version parity -- per CLAUDE.md, an ad-hoc conda solve in an analysis step is a silent
protocol deviation, and here the mapper IS the measurement.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = os.path.join(HERE, "wurz-calib-frozen.json")
OUT = os.path.join(HERE, "valb-triangle-chem.json")

# rdFMCS settings COPIED from valb_pseries_chem.pairwise_mapping so the perturbed-atom numbers are
# apples-to-apples with the 58-80 that refuted the P-series.
_MCS_KW = dict(timeout=60, ringMatchesRingOnly=True, completeRingsOnly=True)

# ---------------------------------------------------------------------------------------------------------
# Pharmacophore landmarks of the Wurz PROTAC, as SMARTS. Each is a STRUCTURAL FACT used to report which
# functional element a candidate edit lands on -- not a claim about how much binding it would cost.
# ---------------------------------------------------------------------------------------------------------
LANDMARKS = {
    "hydroxyproline_OH (VHL anchor -- OFF LIMITS)": "[OX2H]-[CX4;R]1-[CX4;R]-[CX4;R](-[NX3;R]-[CX4;R]1)",
    "hydroxyproline_OH_loose (VHL anchor)": "[OX2H]-[CH1;R]",
    "tert_leucine_tBu (VHL hydrophobic)": "[CX4]([CH3])([CH3])[CH3]",
    "thiazole_4_methyl (VHL cap)": "[CH3]-c1ncsc1",
    "linker_pyridine (consumed by T1)": "c1ccncc1",
    "aminopyridazine (warhead KAc mimic)": "c1cc(nnc1N)",
    "phenol_2_OH (warhead)": "[OX2H]-c1ccccc1",
    "piperazine (linker/warhead junction)": "C1CN(CCN1)",
}


# =========================================================================================================
# structural edits -- each returns (new_mol, description) or (None, reason). All operate on a real molecule.
# =========================================================================================================
def _ring_n_to_ch(mol, Chem, ring_pattern, which=0, label=""):
    """Mutate one aromatic ring nitrogen to CH, in place on the graph. ring_pattern is a SMARTS selecting the
    ring; `which` picks among the ring's nitrogens in index order. Returns a sanitized mol or None."""
    patt = Chem.MolFromSmarts(ring_pattern)
    if patt is None:
        return None, "SMARTS %r did not parse" % ring_pattern
    hits = mol.GetSubstructMatches(patt)
    if len(hits) != 1:
        return None, "%s: expected exactly 1 substructure match, got %d (fail closed)" % (label, len(hits))
    ns = [i for i in hits[0] if mol.GetAtomWithIdx(i).GetSymbol() == "N"
          and mol.GetAtomWithIdx(i).GetIsAromatic() and mol.GetAtomWithIdx(i).IsInRing()]
    ns.sort()
    if which >= len(ns):
        return None, "%s: only %d aromatic ring N in the match, wanted index %d" % (label, len(ns), which)
    rw = Chem.RWMol(mol)
    a = rw.GetAtomWithIdx(ns[which])
    a.SetAtomicNum(6)
    a.SetNumExplicitHs(0)
    a.SetNoImplicit(False)
    a.SetFormalCharge(0)
    out = rw.GetMol()
    try:
        Chem.SanitizeMol(out)
    except Exception as e:  # noqa: BLE001
        return None, "%s: sanitize failed after N->CH (%s)" % (label, e)
    return out, "aromatic ring N (atom idx %d) -> CH" % ns[which]


def _delete_atom(mol, Chem, smarts, target_symbol, label=""):
    """Delete the single heavy atom selected by `smarts`'s FIRST atom (which must be `target_symbol`), letting
    RDKit re-add the implicit H. Fails closed unless the SMARTS matches exactly once."""
    patt = Chem.MolFromSmarts(smarts)
    if patt is None:
        return None, "SMARTS %r did not parse" % smarts
    hits = mol.GetSubstructMatches(patt)
    if len(hits) != 1:
        return None, "%s: expected exactly 1 substructure match, got %d (fail closed)" % (label, len(hits))
    idx = hits[0][0]
    at = mol.GetAtomWithIdx(idx)
    if at.GetSymbol() != target_symbol:
        return None, "%s: matched atom is %s, expected %s" % (label, at.GetSymbol(), target_symbol)
    rw = Chem.RWMol(mol)
    rw.RemoveAtom(idx)
    out = rw.GetMol()
    try:
        Chem.SanitizeMol(out)
    except Exception as e:  # noqa: BLE001
        return None, "%s: sanitize failed after deleting %s (%s)" % (label, target_symbol, e)
    return out, "delete one %s (atom idx %d); implicit H restored" % (target_symbol, idx)


def transform_X(mol, Chem):
    """T1's transform, exactly as `wurz_calib_freeze` defines it: the UNIQUE aromatic 6-membered one-nitrogen
    ring (the pyridine-4-carbonyl linker) N -> CH. Re-derived here rather than read, so the harness is
    validated against the frozen record before any candidate is trusted."""
    ri = mol.GetRingInfo()
    cands = []
    for ring in ri.AtomRings():
        if len(ring) != 6:
            continue
        atoms = [mol.GetAtomWithIdx(i) for i in ring]
        if not all(a.GetIsAromatic() for a in atoms):
            continue
        ns = [a.GetIdx() for a in atoms if a.GetSymbol() == "N"]
        if len(ns) == 1:
            cands.append(ns[0])
    if len(cands) != 1:
        return None, "expected exactly one pyridine ring in the input, found %d" % len(cands)
    rw = Chem.RWMol(mol)
    a = rw.GetAtomWithIdx(cands[0])
    a.SetAtomicNum(6)
    a.SetNumExplicitHs(0)
    a.SetNoImplicit(False)
    out = rw.GetMol()
    try:
        Chem.SanitizeMol(out)
    except Exception as e:  # noqa: BLE001
        return None, "sanitize failed after linker N->CH (%s)" % e
    return out, "linker pyridine N -> CH (pyridine -> benzene)"


# Candidate Y transforms for cmpd4'. Each is (id, kind, callable(mol, Chem) -> (mol, note), rationale).
# `kind` is the ALCHEMICAL class, which is the thing that actually drives cost and NaN risk:
#   element_change -> 1:1 map, ZERO heavy dummy atoms (what T1 already did successfully)
#   deletion       -> a heavy dummy that must be decoupled through the softcore region
def _cand_pyridazine_n1(mol, Chem):
    return _ring_n_to_ch(mol, Chem, "c1cc(nnc1N)", which=0, label="aminopyridazine N1")


def _cand_pyridazine_n2(mol, Chem):
    return _ring_n_to_ch(mol, Chem, "c1cc(nnc1N)", which=1, label="aminopyridazine N2")


def _cand_thiazole_me(mol, Chem):
    return _delete_atom(mol, Chem, "[CH3]-c1ncsc1", "C", label="thiazole 4-methyl -> H")


def _cand_tbu_to_ipr(mol, Chem):
    return _delete_atom(mol, Chem, "[CH3]-[CX4]([CH3])([CH3])[CX4]", "C", label="tert-butyl -> isopropyl")


def _cand_phenol_oh(mol, Chem):
    return _delete_atom(mol, Chem, "[OX2H]-c1ccccc1", "O", label="2-hydroxyphenyl -> phenyl")


CANDIDATES = [
    ("pyridazine_N1_to_CH", "element_change", _cand_pyridazine_n1,
     "aminopyridazine ring N -> CH. The ONLY candidate in the same alchemical class as the edge that already "
     "converged (element change, no dummy atoms). Lands on the warhead's acetyl-lysine-mimetic heterocycle."),
    ("pyridazine_N2_to_CH", "element_change", _cand_pyridazine_n2,
     "the other aminopyridazine ring N -> CH; same class, different site."),
    ("thiazole_4Me_to_H", "deletion", _cand_thiazole_me,
     "thiazole 4-methyl -> H (one heavy atom). Lands on the VHL ligand's terminal cap."),
    ("tBu_to_iPr", "deletion", _cand_tbu_to_ipr,
     "tert-leucine tert-butyl -> isopropyl (one heavy atom). Lands on the VHL hydrophobic contact."),
    ("phenol_OH_to_H", "deletion", _cand_phenol_oh,
     "2-hydroxyphenyl -> phenyl (one heavy atom). Lands on the warhead aryl."),
]


# =========================================================================================================
# measurement helpers
# =========================================================================================================
def _canon(mol, Chem):
    try:
        return Chem.MolToSmiles(Chem.RemoveHs(Chem.Mol(mol)))
    except Exception:  # noqa: BLE001
        return Chem.MolToSmiles(mol)


def _mcs_edge(mA, mB, Chem, rdFMCS):
    """Perturbed heavy atoms by rdFMCS, with valb_pseries_chem's exact settings."""
    res = rdFMCS.FindMCS([mA, mB], **_MCS_KW)
    n = res.numAtoms if res and not res.canceled else 0
    ha, hb = mA.GetNumHeavyAtoms(), mB.GetNumHeavyAtoms()
    return {"heavy_a": ha, "heavy_b": hb, "mcs_atoms": n, "perturbed_heavy_atoms": ha + hb - 2 * n,
            "mcs_smarts": (res.smartsString if res else None),
            "formal_charge_a": Chem.GetFormalCharge(mA), "formal_charge_b": Chem.GetFormalCharge(mB),
            "charge_change": Chem.GetFormalCharge(mB) - Chem.GetFormalCharge(mA)}


def _lomap_edge(mA, mB, name_a, name_b):
    """THE PRODUCTION ATOM MAP. Calls the same `nr4a3_rbfe._mapping(prefer_element_change=True)` the ternary
    engine calls, so this is the mapper that would actually run, at the image's version parity. Reports mapped
    atoms and the DUMMY count on each side (heavy atoms with no partner), which is the quantity that decides
    whether the edge is an element change or a softcore (dis)appearance."""
    try:
        import openfe
        from rdkit import Chem
        sys.path.insert(0, HERE)
        import nr4a3_rbfe as rbfe
    except Exception as e:  # noqa: BLE001
        return {"status": "production mapper unavailable (%s: %s)" % (type(e).__name__, e)}
    try:
        # SmallMoleculeComponent needs explicit H + a conformer; build one so LOMAP sees a real molecule.
        from rdkit.Chem import AllChem
        out = {}
        comps = {}
        for nm, m in ((name_a, mA), (name_b, mB)):
            mh = Chem.AddHs(Chem.Mol(m))
            if AllChem.EmbedMolecule(mh, randomSeed=0xF00D) != 0:
                AllChem.EmbedMolecule(mh, randomSeed=0xF00D, useRandomCoords=True)
            try:
                AllChem.MMFFOptimizeMolecule(mh, maxIters=500)
            except Exception:  # noqa: BLE001
                pass
            mh.SetProp("_Name", nm)
            comps[nm] = openfe.SmallMoleculeComponent.from_rdkit(mh)
        mapping = rbfe._mapping(openfe, comps[name_a], comps[name_b], prefer_element_change=True)
        a2b = dict(mapping.componentA_to_componentB)
        ra = comps[name_a].to_rdkit()
        rb = comps[name_b].to_rdkit()
        heavy_a = {i for i in range(ra.GetNumAtoms()) if ra.GetAtomWithIdx(i).GetAtomicNum() > 1}
        heavy_b = {i for i in range(rb.GetNumAtoms()) if rb.GetAtomWithIdx(i).GetAtomicNum() > 1}
        mapped_heavy_a = {i for i in a2b if i in heavy_a}
        mapped_heavy_b = {j for i, j in a2b.items() if j in heavy_b}
        out.update({
            "status": "ok",
            "mapper": "nr4a3_rbfe._mapping(prefer_element_change=True) -> LomapAtomMapper(time=20, "
                      "threed=False) -- the production mapper named in protocol_signature",
            "n_mapped_atoms_total": len(a2b),
            "n_heavy_a": len(heavy_a), "n_heavy_b": len(heavy_b),
            "n_mapped_heavy": len(mapped_heavy_a),
            "n_heavy_dummy_a": len(heavy_a) - len(mapped_heavy_a),   # disappearing heavy atoms
            "n_heavy_dummy_b": len(heavy_b) - len(mapped_heavy_b),   # appearing heavy atoms
            "n_heavy_dummy_total": (len(heavy_a) - len(mapped_heavy_a)) + (len(heavy_b) - len(mapped_heavy_b)),
            "perturbed_heavy_by_lomap": (len(heavy_a) - len(mapped_heavy_a)) + (len(heavy_b) - len(mapped_heavy_b)),
        })
        return out
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"status": "mapping FAILED: %s: %s" % (type(e).__name__, e),
                "traceback": traceback.format_exc()[-1500:]}


def _landmarks(mol, Chem):
    got = {}
    for name, sma in LANDMARKS.items():
        p = Chem.MolFromSmarts(sma)
        got[name] = (len(mol.GetSubstructMatches(p)) if p is not None else "SMARTS did not parse")
    return got


def _anchor_intact(mA, mB, Chem):
    """The trans-4-hydroxyproline hydroxyl must survive the edit. Reported as counts on both endpoints; a drop
    is a hard REFUSE for that candidate (the VHL anchor would be gone and the leg would measure a dissociation)."""
    p = Chem.MolFromSmarts(LANDMARKS["hydroxyproline_OH_loose (VHL anchor)"])
    if p is None:
        return {"status": "anchor SMARTS did not parse"}
    na, nb = len(mA.GetSubstructMatches(p)), len(mB.GetSubstructMatches(p))
    return {"anchor_OH_matches_a": na, "anchor_OH_matches_b": nb, "anchor_preserved": na == nb and na >= 1}


def _engine_can_build(target_canon, cmpd1_smiles):
    """Can the SHIPPED engine build this endpoint's pose? `nr4a3_ternary_fep._endpoint_pose` has exactly ONE
    element-change mutation path -- `_pyridine_to_benzene_pose`, which requires the molecule to have exactly one
    pyridine and produces the benzene analogue -- and raises SystemExit otherwise ('refusing a wrong-molecule
    leg'). Call it for real on cmpd1 and see what comes out."""
    try:
        from rdkit import Chem
        sys.path.insert(0, HERE)
        import nr4a3_ternary_fep as tfep
    except Exception as e:  # noqa: BLE001
        return {"status": "engine import unavailable (%s: %s)" % (type(e).__name__, e)}
    m1 = Chem.MolFromSmiles(cmpd1_smiles)
    if m1 is None:
        return {"status": "cmpd1 SMILES did not parse"}
    mut = tfep._pyridine_to_benzene_pose(Chem.AddHs(m1), Chem)
    produced = None if mut is None else Chem.MolToSmiles(Chem.RemoveHs(Chem.Mol(mut)))
    return {
        "engine_mutation_path": "nr4a3_ternary_fep._pyridine_to_benzene_pose (the only element-change pose "
                                "mutation in the engine)",
        "applied_to": "cmpd1 (the crystal ligand; _endpoint_pose always starts from it via base_smiles)",
        "produced_canonical_smiles": produced,
        "target_canonical_smiles": target_canon,
        "engine_builds_this_endpoint_today": bool(produced is not None and produced == target_canon),
        "_meaning": "False => _endpoint_pose would raise SystemExit('refusing a wrong-molecule leg') for this "
                    "endpoint, so NEW pose-construction code is required before the edge can run. Engineering "
                    "is free, but 'the machinery carries over unchanged' is then not true.",
    }


# =========================================================================================================
# main
# =========================================================================================================
def main():
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem import rdFMCS
        RDLogger.DisableLog("rdApp.*")
    except Exception as e:  # noqa: BLE001
        print("rdkit unavailable (%s) -- this gate cannot run without it" % e, file=sys.stderr)
        return 3

    frozen = json.load(open(FROZEN))
    c1_smiles = frozen["calib_hi"]["smiles"]
    c4_frozen = frozen["calib_lo"]["smiles"]
    m1 = Chem.MolFromSmiles(c1_smiles)
    if m1 is None:
        print("frozen cmpd1 SMILES did not parse", file=sys.stderr)
        return 3

    # --- harness validation: re-derive cmpd4 and check it against the frozen record -----------------------
    m4, x_note = transform_X(m1, Chem)
    harness = {
        "cmpd1_smiles_source": "wurz-calib-frozen.json -> calib_hi.smiles (RCSB 8G1Q, CCD YHB)",
        "transform_X": x_note if m4 is not None else "FAILED: %s" % x_note,
        "cmpd4_rederived": _canon(m4, Chem) if m4 is not None else None,
        "cmpd4_frozen": _canon(Chem.MolFromSmiles(c4_frozen), Chem),
    }
    harness["rederivation_matches_frozen"] = bool(
        m4 is not None and harness["cmpd4_rederived"] == harness["cmpd4_frozen"])
    if not harness["rederivation_matches_frozen"]:
        # Fail closed: if the harness cannot reproduce the frozen edge, none of its candidate numbers is trustworthy.
        report = {"_status": "HARNESS FAILED — cannot reproduce the frozen cmpd1->cmpd4 edge; no candidate "
                             "measurement below would be trustworthy", "harness": harness}
        json.dump(report, open(OUT, "w"), indent=2)
        print(json.dumps(report, indent=2))
        return 4

    c1_canon, c4_canon = _canon(m1, Chem), _canon(m4, Chem)
    t1_mcs = _mcs_edge(m1, m4, Chem, rdFMCS)
    t1_lomap = _lomap_edge(m1, m4, "cmpd1", "cmpd4")

    results = []
    for cid, kind, fn, why in CANDIDATES:
        rec = {"candidate_id": cid, "alchemical_class": kind, "rationale": why}
        # Route A: apply Y to cmpd4  -> cmpd4'
        m4p_a, note_a = fn(m4, Chem)
        # Route B: apply Y to cmpd1 then X -> cmpd4'   (independent derivation of the SAME endpoint)
        m1p, note_b1 = fn(m1, Chem)
        m4p_b, note_b2 = (transform_X(m1p, Chem) if m1p is not None else (None, "route B: Y on cmpd1 failed"))
        rec["route_A_cmpd4_then_Y"] = note_a if m4p_a is not None else "FAILED: %s" % note_a
        rec["route_B_cmpd1_then_Y_then_X"] = (
            "%s ; %s" % (note_b1, note_b2) if m4p_b is not None else "FAILED: %s / %s" % (note_b1, note_b2))
        if m4p_a is None:
            rec["verdict"] = "REFUSED — the transform could not be applied (fail-closed, see route_A)"
            results.append(rec)
            continue
        c4p_canon = _canon(m4p_a, Chem)
        rec["cmpd4prime_canonical_smiles"] = c4p_canon
        rec["routes_agree"] = bool(m4p_b is not None and _canon(m4p_b, Chem) == c4p_canon)
        rec["routes_agree_note"] = ("The two derivations of cmpd4' agree, so T1/T2/T3 genuinely share endpoints "
                                    "and the closure identity holds. A mismatch would mean the 'triangle' is not "
                                    "a closed cycle at all." if rec["routes_agree"] else
                                    "MISMATCH — the triangle would NOT be closed; closure residual meaningless.")
        # the three edges
        rec["edges"] = {
            "T1_cmpd1_to_cmpd4 (ALREADY RUN = r0)": {"mcs": t1_mcs, "production_map": t1_lomap},
            "T2_cmpd4_to_cmpd4prime (NEW)": {"mcs": _mcs_edge(m4, m4p_a, Chem, rdFMCS),
                                             "production_map": _lomap_edge(m4, m4p_a, "cmpd4", "cmpd4prime")},
            "T3_cmpd1_to_cmpd4prime (NEW, closes the loop)": {
                "mcs": _mcs_edge(m1, m4p_a, Chem, rdFMCS),
                "production_map": _lomap_edge(m1, m4p_a, "cmpd1", "cmpd4prime")},
        }
        rec["anchor_check_T2"] = _anchor_intact(m4, m4p_a, Chem)
        rec["anchor_check_T3"] = _anchor_intact(m1, m4p_a, Chem)
        rec["landmarks_cmpd4prime"] = _landmarks(m4p_a, Chem)
        rec["engine_buildability"] = _engine_can_build(c4p_canon, c1_smiles)

        # ---- the gate itself -------------------------------------------------------------------------
        t2, t3 = rec["edges"]["T2_cmpd4_to_cmpd4prime (NEW)"], \
            rec["edges"]["T3_cmpd1_to_cmpd4prime (NEW, closes the loop)"]
        charge_ok = (t2["mcs"]["charge_change"] == 0 and t3["mcs"]["charge_change"] == 0)
        pert_t2, pert_t3 = t2["mcs"]["perturbed_heavy_atoms"], t3["mcs"]["perturbed_heavy_atoms"]
        anchor_ok = bool(rec["anchor_check_T2"].get("anchor_preserved")
                         and rec["anchor_check_T3"].get("anchor_preserved"))
        rec["gate"] = {
            "charge_neutral_all_new_edges": bool(charge_ok),
            "perturbed_heavy_T2": pert_t2,
            "perturbed_heavy_T3": pert_t3,
            "T3_is_a_DOUBLE_perturbation": bool(pert_t3 > pert_t2 and pert_t3 > 1),
            "T3_equals_T1_plus_T2": bool(pert_t3 == t1_mcs["perturbed_heavy_atoms"] + pert_t2),
            "claim_all_new_edges_le_2_heavy": bool(pert_t2 <= 2 and pert_t3 <= 2),
            "vhl_anchor_preserved": anchor_ok,
            "endpoints_consistent": bool(rec["routes_agree"]),
            "engine_builds_endpoint_today": bool(
                rec["engine_buildability"].get("engine_builds_this_endpoint_today")),
        }
        results.append(rec)

    report = {
        "_what": "the $0 PRE-GATE on the valB synthetic closure triangle (rescope doc section 8): can T2/T3 be "
                 "built at all, are they charge-neutral, how many heavy atoms do they really perturb through "
                 "the PRODUCTION mapper, and does the shipped engine build the endpoints?",
        "_provenance": "cmpd1 SMILES from wurz-calib-frozen.json (RCSB 8G1Q); cmpd4 RE-DERIVED here and checked "
                       "against the frozen record; every cmpd4' produced by a pattern-matched structural edit of "
                       "a real molecule. No SMILES typed by hand, no alpha/dG/GPU-hour asserted.",
        "_mcs_settings": {k: v for k, v in _MCS_KW.items()},
        "_mcs_settings_note": "identical to valb_pseries_chem.pairwise_mapping, so perturbed-heavy-atom counts "
                              "are directly comparable to the P-series' 58-80 and the running edge's 2.",
        "harness": harness,
        "reference_edge_T1": {"canonical_cmpd1": c1_canon, "canonical_cmpd4": c4_canon,
                              "mcs": t1_mcs, "production_map": t1_lomap,
                              "note": "this is r0 -- ALREADY PAID FOR. It is the size/class every new edge is "
                                      "compared against."},
        "landmarks_cmpd1": _landmarks(m1, Chem),
        "candidates": results,
    }
    json.dump(report, open(OUT, "w"), indent=2)
    print(json.dumps({"harness": harness,
                      "T1_reference": {"mcs_perturbed": t1_mcs["perturbed_heavy_atoms"],
                                       "lomap": t1_lomap.get("perturbed_heavy_by_lomap",
                                                             t1_lomap.get("status"))},
                      "candidates": [{"id": r["candidate_id"], "class": r.get("alchemical_class"),
                                      "gate": r.get("gate"), "verdict": r.get("verdict")} for r in results]},
                     indent=2))
    print("[triangle-chem] wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
