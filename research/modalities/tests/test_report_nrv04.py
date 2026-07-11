"""Unit tests for report_nrv04 decision logic — moiety split, aggregation, and the pilot/full verdict gates.

Geometry parsing from CIFs needs gemmi (GPU/CI); here we test the pure logic by feeding sample dicts + the
moiety-split core directly."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import report_nrv04 as r  # noqa: E402

CUT = ["%.1f" % c for c in r.CUTOFFS]  # ["4.0","4.5","5.0"]


def _control(seated_flags, lig_iptm):
    samples = [{"seed": "seed_%d" % i, "rank": 0, "confidence": {"ligand_iptm": v, "iptm": v},
                "geometry": {"seated": s}} for i, (s, v) in enumerate(zip(seated_flags, lig_iptm), 1)]
    return {"system": "control", "kind": "control", "samples": samples,
            "ensemble": r._aggregate(samples, "control")}


def _ternary(moiety_bridge_flags, lig_iptm, lys_d=None, wrong=None, name="nr4a1"):
    """Build a ternary system from per-sample moiety-bridge flags (assumed same at all cutoffs unless a dict)."""
    n = len(moiety_bridge_flags)
    lys_d = lys_d or [10.0] * n
    wrong = wrong or [False] * n
    samples = []
    for i, (b, v, d, w) in enumerate(zip(moiety_bridge_flags, lig_iptm, lys_d, wrong), 1):
        br = b if isinstance(b, dict) else {c: bool(b) for c in CUT}
        samples.append({"seed": "seed_%d" % i, "rank": 0, "confidence": {"ligand_iptm": v, "iptm": v},
                        "geometry": {"bridges": bool(br[CUT[1]]),
                                     "closest_exposed_lys": {"resnum": 590, "dist_A": d, "counts": {}}},
                        "moiety": {"moiety_bridges": br, "moiety_bridges_default": br[CUT[1]], "wrong_end": w}})
    return {"system": name, "kind": "ternary", "samples": samples, "ensemble": r._aggregate(samples, "ternary")}


# --- moiety split core (no gemmi) ------------------------------------------------------------------------
def test_split_ligand_ends_uses_unique_sulfur():
    # Linear chain: S at one end (VH032 anchor), C's trailing away; farthest C = celastrol terminus.
    atoms = [("S", (0, 0, 0)), ("C", (1, 0, 0)), ("C", (2, 0, 0)), ("C", (9, 0, 0)), ("O", (10, 0, 0))]
    vhl_end, nr4a_end, note = r.split_ligand_ends(atoms)
    assert (0, 0, 0) in vhl_end and (1, 0, 0) in vhl_end          # near S
    assert (10, 0, 0) in nr4a_end and (9, 0, 0) in nr4a_end       # near far terminus
    assert "sulfur-anchor" in note


def test_split_ligand_ends_falls_back_without_one_sulfur():
    atoms = [("C", (0, 0, 0)), ("C", (1, 0, 0)), ("C", (2, 0, 0))]   # zero S
    vhl_end, nr4a_end, note = r.split_ligand_ends(atoms)
    assert vhl_end is None and nr4a_end is None and "FAIL-CLOSED" in note


def test_dist_stats():
    d = r._dist([0.4, 0.6, 0.5])
    assert d["n"] == 3 and d["mean"] == 0.5


# --- aggregation -----------------------------------------------------------------------------------------
def test_aggregate_control_seated_fraction():
    c = _control([True, True, False], [0.7, 0.65, 0.2])
    e = c["ensemble"]
    assert e["n_seated"] == 2 and e["n_scored"] == 3
    assert e["seated_fraction"] == round(2 / 3, 3)


def test_aggregate_moiety_bridged_and_lys_relabelled():
    t = _ternary([True, True, True], [0.6, 0.55, 0.62], lys_d=[9.0, 11.0, 10.0])
    e = t["ensemble"]
    assert e["seed_bridged_fraction"] == 1.0
    assert e["pose_level_fraction"][CUT[1]]["n_bridged"] == 3
    assert e["lys_nz_to_vhl_A"]["mean"] == 10.0        # relabelled field
    assert "closest_lys_A" not in e                     # old name gone
    assert "SASA" in e["lys_caveat"]


def test_aggregate_wrong_end_fraction():
    t = _ternary([True, True, True], [0.6, 0.6, 0.6], wrong=[True, False, False])
    assert t["ensemble"]["wrong_end_fraction"] == round(1 / 3, 3)


# --- pilot gate ------------------------------------------------------------------------------------------
def test_pilot_gate_proceed_on_moiety_bridging():
    c = _control([True, True, True], [0.7, 0.68, 0.66])
    t = _ternary([True, True, False], [0.6, 0.58, 0.3])   # moiety-bridged 2/3
    v = r.pilot_verdict(c, t)
    assert v["verdict"] == "PROCEED" and v["control_ok"] and v["nr4a1_ok"]


def test_pilot_gate_abort_when_nr4a1_not_moiety_productive():
    c = _control([True, True, True], [0.7, 0.7, 0.7])
    t = _ternary([False, False, True], [0.2, 0.25, 0.5])  # moiety-bridged 1/3
    v = r.pilot_verdict(c, t)
    assert v["verdict"] == "ABORT" and v["nr4a1_ok"] is False


# --- full verdict (exploratory concordance) --------------------------------------------------------------
def test_full_gate_exploratory_concordance_on_moiety_separation():
    systems = {
        "nr4a1": _ternary([True, True, True], [0.62, 0.60, 0.64], name="nr4a1"),
        "nr4a2": _ternary([False, False, False], [0.40, 0.42, 0.38], name="nr4a2"),
        "nr4a3": _ternary([False, False, False], [0.35, 0.37, 0.36], name="nr4a3"),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "exploratory-architecture-concordance"
    assert v["primary_basis"] == "correct_half_dual_surface_proximity_SEED_level"
    assert v["cutoff_robust"] is True
    assert v["leave_one_seed_out_robust"] is True
    assert "not validation" in v["basis"].lower()


def test_full_gate_concordance_holds_even_when_ligand_iptm_inverts():
    # Real NR-V04 shape: moiety-separation clean, but ligand-iPTM higher for a spared paralogue.
    systems = {
        "nr4a1": _ternary([True, True, True], [0.82, 0.91, 0.84], name="nr4a1"),
        "nr4a2": _ternary([False, False, False], [0.91, 0.92, 0.90], name="nr4a2"),
        "nr4a3": _ternary([False, False, False], [0.92, 0.87, 0.84], name="nr4a3"),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "exploratory-architecture-concordance"
    assert v["ligand_iptm_note"] and "did not reproduce" in v["ligand_iptm_note"].lower()


def test_full_gate_discordant_when_degraded_does_not_bridge():
    systems = {
        "nr4a1": _ternary([False, False, False], [0.35, 0.4, 0.38], name="nr4a1"),
        "nr4a2": _ternary([False, False, False], [0.60, 0.6, 0.62], name="nr4a2"),
        "nr4a3": _ternary([False, False, False], [0.58, 0.5, 0.55], name="nr4a3"),
    }
    assert r.full_verdict(systems)["verdict"] == "discordant"


def test_full_gate_inconclusive_when_spared_also_bridges():
    systems = {
        "nr4a1": _ternary([True, True, True], [0.5, 0.5, 0.5], name="nr4a1"),
        "nr4a2": _ternary([True, True, False], [0.5, 0.5, 0.4], name="nr4a2"),   # spared also bridges majority
        "nr4a3": _ternary([False, False, False], [0.4, 0.4, 0.4], name="nr4a3"),
    }
    assert r.full_verdict(systems)["verdict"] == "inconclusive"


def test_full_gate_cutoff_not_robust_flagged():
    # Bridged at 4.5/5.0 but not 4.0 for NR4A1 -> cutoff_robust False, still concordant at default.
    perc = {"4.0": False, "4.5": True, "5.0": True}
    systems = {
        "nr4a1": _ternary([perc, perc, perc], [0.6, 0.6, 0.6], name="nr4a1"),
        "nr4a2": _ternary([False, False, False], [0.4, 0.4, 0.4], name="nr4a2"),
        "nr4a3": _ternary([False, False, False], [0.4, 0.4, 0.4], name="nr4a3"),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "exploratory-architecture-concordance"
    assert v["cutoff_robust"] is False


# --- review-v2 honesty behaviours -----------------------------------------------------------------------
def test_pilot_not_evaluated_when_control_absent_by_design():
    t = _ternary([True, True, True], [0.6, 0.6, 0.6])
    v = r.pilot_verdict(None, t)                       # control absent (fan-out / --skip-control)
    assert v["verdict"] == "not-evaluated" and v["control_ok"] is None


def test_unmapped_sample_fails_closed_not_counted_as_bridge():
    # A sample whose moiety mapping failed (moiety_bridges None) is counted as unmapped, never as a bridge.
    samples = [{"seed": "seed_1", "rank": 0, "confidence": {"ligand_iptm": 0.5, "iptm": 0.5},
                "geometry": {"bridges": False, "closest_exposed_lys": None},
                "moiety": {"moiety_bridges": None, "unmapped": True}}]
    e = r._aggregate(samples, "ternary")
    assert e["n_unmapped"] == 1 and e["seed_bridged_fraction"] is None


def test_seed_is_primary_unit_not_pose_pool():
    # 2 seeds x 2 poses; seed_1 both bridge, seed_2 neither -> seed-level 0.5, NOT pose-pool 0.5-of-4-"independent".
    def s(seed, br):
        return {"seed": seed, "rank": 0, "confidence": {"ligand_iptm": 0.5, "iptm": 0.5},
                "geometry": {"bridges": br, "closest_exposed_lys": None},
                "moiety": {"moiety_bridges": {c: br for c in CUT}, "wrong_end": False}}
    samples = [s("seed_1", True), s("seed_1", True), s("seed_2", False), s("seed_2", False)]
    e = r._aggregate(samples, "ternary")
    assert e["n_seeds"] == 2 and e["n_poses"] == 4
    assert e["seed_bridged_fraction"] == 0.5
    assert "seeds=2, poses=4" in e["denominator"]


# --- atom-mapped moieties (review fix #2) + intended-site occupancy (review fix #3), RDKit --------------
import pytest  # noqa: E402

rdkit = pytest.importorskip("rdkit")
from rdkit import Chem  # noqa: E402
from rdkit.Chem import AllChem  # noqa: E402


def _cif_atoms(smiles, seed=1, scramble=False):
    """Emit (element, (x,y,z)) heavy atoms in SMILES order (mimics Boltz's order-preserving CIF ligand block)."""
    m = Chem.RemoveHs(Chem.MolFromSmiles(smiles))
    mh = Chem.AddHs(m)
    assert AllChem.EmbedMolecule(mh, randomSeed=seed) == 0
    mh = Chem.RemoveHs(mh)
    c = mh.GetConformer()
    atoms = [(a.GetSymbol(), (c.GetAtomPosition(a.GetIdx()).x, c.GetAtomPosition(a.GetIdx()).y,
                              c.GetAtomPosition(a.GetIdx()).z)) for a in mh.GetAtoms()]
    if scramble:
        import random
        random.seed(7); random.shuffle(atoms)
    return atoms


def test_atom_map_protac_atom_order_identity():
    ca = _cif_atoms(r.NRV04_PROTAC_SMILES)
    am = r.atom_map_moieties(r.NRV04_PROTAC_SMILES, ca)
    assert am["ok"] and am["method"] == "atom_order"
    assert am["mapping"] == list(range(len(ca)))         # identity map (SMILES order == CIF order)
    assert am["has_warhead"] and am["has_recruiter"]
    # warhead (celastrol) and recruiter (VH032) ends are disjoint and each non-trivial
    assert set(am["warhead_cif"]).isdisjoint(am["recruiter_cif"])
    assert len(am["warhead_cif"]) >= 25 and len(am["recruiter_cif"]) >= 10 and len(am["linker_cif"]) >= 10


def test_atom_map_free_celastrol_flags_no_recruiter():
    ca = _cif_atoms(r.FREE_CELASTROL_SMILES)
    am = r.atom_map_moieties(r.FREE_CELASTROL_SMILES, ca)
    assert am["ok"] and am["has_warhead"] and am["has_recruiter"] is False
    assert am["recruiter_cif"] == []


def test_atom_map_bond_perception_fallback_on_scrambled_order():
    # If the CIF heavy-atom order does NOT match SMILES order, the atom_order identity map is refused and the
    # bond-perception graph match is used instead (never a silent identity assumption).
    ca = _cif_atoms(r.FREE_CELASTROL_SMILES, scramble=True)
    am = r.atom_map_moieties(r.FREE_CELASTROL_SMILES, ca)
    assert am["ok"] and am["method"] == "bond_perception"
    # every mapped index points to a CIF atom of the correct element
    ref_elems = [a.GetSymbol().upper() for a in Chem.RemoveHs(Chem.MolFromSmiles(r.FREE_CELASTROL_SMILES)).GetAtoms()]
    for ref_i, cif_i in enumerate(am["mapping"]):
        assert ca[cif_i][0].upper() == ref_elems[ref_i]


def test_atom_map_fail_closed_element_mismatch():
    am = r.atom_map_moieties(r.FREE_CELASTROL_SMILES, [("C", (0, 0, 0)), ("C", (1, 0, 0))])
    assert am["ok"] is False and am["mapping"] is None and "element composition mismatch" in am["reason"]


def test_atom_map_fail_closed_bad_smiles():
    am = r.atom_map_moieties("Xnot-a-smiles", _cif_atoms(r.FREE_CELASTROL_SMILES))
    assert am["ok"] is False and am["mapping"] is None


def test_moiety_ref_sets_required_substructures_and_disjoint():
    mol = Chem.RemoveHs(Chem.MolFromSmiles(r.NRV04_PROTAC_SMILES))
    sets = r._moiety_ref_sets(mol)
    assert sets["has_warhead"] and sets["has_recruiter"]
    assert sets["warhead"].isdisjoint(sets["recruiter"])
    assert sets["warhead"] and sets["recruiter"] and sets["linker"]


# --- pure geometry core: intended-site occupancy (review fix #3) -----------------------------------------
def test_moiety_metrics_correct_half_bridge_and_pocket_occupancy():
    warh, rec, lnk = [(0, 0, 0)], [(10, 0, 0)], [(5, 0, 0)]
    nr4a, vhl, pocket = [(1, 0, 0)], [(11, 0, 0)], [(10.5, 0, 0)]   # recruiter next to the Hyp pocket
    m = r._moiety_metrics(warh, rec, lnk, warh + rec + lnk, nr4a, vhl, pocket, True, True)
    assert m["moiety_bridges"]["4.5"] is True and m["moiety_bridges_default"] is True
    assert m["recruiter_pocket_occupancy"] is True and m["warhead_site_occupancy"] is True
    assert m["warhead_site_defined"] is False                        # NR4A site not defined -> LBD-contact proxy
    assert m["linker_only_contact"] is False and m["wrong_end"] is False


def test_moiety_metrics_linker_only_nonspecific():
    # warhead & recruiter far from every protein atom; only the linker touches -> linker-only flag, no bridge.
    warh, rec, lnk = [(0, 0, 0)], [(30, 0, 0)], [(15, 0, 0)]
    nr4a, vhl, pocket = [(15, 1, 0)], [(15, 2, 0)], [(15, 5, 0)]
    m = r._moiety_metrics(warh, rec, lnk, warh + rec + lnk, nr4a, vhl, pocket, True, True)
    assert m["linker_only_contact"] is True
    assert m["moiety_bridges"]["4.5"] is False
    assert m["recruiter_pocket_occupancy"] is False


def test_moiety_metrics_wrong_end_flag():
    # warhead sits on VHL, recruiter sits on NR4A -> ends swapped.
    warh, rec, lnk = [(11, 0, 0)], [(1, 0, 0)], [(6, 0, 0)]
    nr4a, vhl, pocket = [(0, 0, 0)], [(12, 0, 0)], [(30, 0, 0)]
    m = r._moiety_metrics(warh, rec, lnk, warh + rec + lnk, nr4a, vhl, pocket, True, True)
    assert m["wrong_end"] is True


def test_moiety_metrics_fail_closed_bridge_when_no_recruiter_but_occupancy_reported():
    # free-warhead architecture negative: has_recruiter False -> moiety_bridges None (fail-closed) but the
    # warhead-site occupancy is still computed.
    warh, lnk = [(0, 0, 0)], [(5, 0, 0)]
    nr4a, vhl, pocket = [(1, 0, 0)], [(20, 0, 0)], [(20, 0, 0)]
    m = r._moiety_metrics(warh, [], lnk, warh + lnk, nr4a, vhl, pocket, True, False)
    assert m["moiety_bridges"] is None and m["moiety_bridges_default"] is None
    assert m["warhead_site_occupancy"] is True
    assert m["recruiter_pocket_occupancy"] is False


def test_moiety_metrics_counts_steric_clashes():
    warh, rec, lnk = [(0, 0, 0)], [(10, 0, 0)], [(5, 0, 0)]
    nr4a = [(0.5, 0, 0)]                                             # 0.5 Å from a warhead atom -> clash (<2.0)
    vhl, pocket = [(10, 0, 0)], [(10, 0, 0)]
    m = r._moiety_metrics(warh, rec, lnk, warh + rec + lnk, nr4a, vhl, pocket, True, True)
    assert m["steric_clashes"] >= 1
    assert m["linker_strain_proxy"]["n_linker_atoms"] == 1


def test_aggregate_summarises_occupancy_fields():
    def s(seed, pocket, site, linker_only, clashes):
        return {"seed": seed, "rank": 0, "confidence": {"ligand_iptm": 0.5, "iptm": 0.5},
                "geometry": {"bridges": True, "closest_exposed_lys": None},
                "moiety": {"moiety_bridges": {c: True for c in CUT}, "wrong_end": False,
                           "atom_map": {"ok": True, "method": "atom_order"},
                           "recruiter_pocket_occupancy": pocket, "warhead_site_occupancy": site,
                           "linker_only_contact": linker_only, "steric_clashes": clashes}}
    samples = [s("seed_1", True, True, False, 0), s("seed_2", False, True, True, 3)]
    e = r._aggregate(samples, "ternary")
    assert e["recruiter_pocket_occupancy_fraction"]["fraction"] == 0.5
    assert e["warhead_site_occupancy_fraction"]["fraction"] == 1.0
    assert e["linker_only_contact_fraction"]["fraction"] == 0.5
    assert e["steric_clashes"]["mean"] == 1.5
