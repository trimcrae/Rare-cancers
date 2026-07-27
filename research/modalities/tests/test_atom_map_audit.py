#!/usr/bin/env python3
"""The atom-map floor must FAIL LOUDLY below the provable minimum — it must never merely warn.

WHY THIS FILE EXISTS. On 2026-07-26 `nr4a3_rbfe._mapping` was found to have run `LomapAtomMapper(time=20)`
since the repo's first alchemical leg. `time` is LOMAP's MCS TIMEOUT in seconds, and a timed-out MCS returns
its best PARTIAL match SILENTLY. So the atom map — what the alchemical transformation actually IS — depended
on how fast the rented host happened to be, and a short map is a different experiment that still converges,
still produces tight MBAR statistics, and still returns a confident ΔG for a perturbation nobody designed.

Raising the budget to 300 s makes the failure rarer. It does not make it detectable. These tests pin the
detection, which is the part that has to survive the next host that is slower still:

  * a map below the provable floor RAISES (SystemExit), it does not warn and continue;
  * the floor is derived from the endpoints, never assumed, and never guessed when it cannot be derived;
  * an underivable floor yields UNVERIFIABLE, never CLEAN — absence of evidence is not evidence of a clean map;
  * the three real observations that exposed the bug are pinned as fixtures, so a future refactor that would
    have let any of them through fails here first.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

ama = pytest.importorskip("atom_map_audit")
Chem = pytest.importorskip("rdkit.Chem")

# ---- the real chemistry, read from the repo's own frozen artifacts (rule 1: one fact, one place) -------------
import json  # noqa: E402

_WURZ = json.load(open(os.path.join(HERE, "wurz-calib-frozen.json")))
_MAP = json.load(open(os.path.join(HERE, "congeneric-rbfe-map.json")))
_SMI = {n["id"]: n["smiles"] for n in _MAP["nodes"]}
_5AKS = json.load(open(os.path.join(HERE, "5aks_fep_inputs",
                                    "5aks_d0_to_d__ternary_nr4a3", "staging_manifest.json")))


def _b_wurz():
    return ama.edge_bounds("Wurz_cmpd1", _WURZ["calib_hi"]["smiles"],
                           "Wurz_cmpd4", _WURZ["calib_lo"]["smiles"])


def _b_5aks():
    s = _5AKS["ligand"]["stereo_smiles"]
    return ama.edge_bounds("5aks_d0", s, "5aks_d", s)


def _b_pilot():
    return ama.edge_bounds("zaienne_cmpd19", _SMI["zaienne_cmpd19"], "cw_ev_5nh2", _SMI["cw_ev_5nh2"])


# ---- the bound itself ---------------------------------------------------------------------------------------

def test_identity_edge_demands_a_complete_map():
    """5a-KS writes ONE pose twice, so the endpoints are literally the same molecule (111 atoms). The complete
    map is 111 and there is no chemistry that could justify fewer."""
    b = _b_5aks()
    assert b["complete_map_provable"] is True
    assert b["n_atoms_a"] == b["n_atoms_b"] == 111
    assert b["expected_n_mapped_atoms"] == 111
    assert b["total_floor_enforced"] == 111


def test_single_element_swap_is_recognised_as_isomorphic():
    """Wurz cmpd1 -> cmpd4 is one ring N -> CH. 59/59 heavy atoms, one element mismatch; the complete map is
    109 (all of A) with one dummy H on B."""
    b = _b_wurz()
    assert b["complete_map_provable"] is True
    assert (b["n_heavy_a"], b["n_heavy_b"]) == (59, 59)
    assert (b["n_atoms_a"], b["n_atoms_b"]) == (109, 110)
    assert b["n_element_mismatched_heavy"] == 1
    assert b["expected_n_mapped_atoms"] == 109


def test_enforced_floor_is_satisfiable_by_a_strict_element_map():
    """THE PROPERTY THAT MAKES THE FLOOR SAFE TO HARD-FAIL ON. An element-mismatched atom (and the H it
    carries) may legitimately go unmapped when LOMAP returns an element_change=False map, so the floor must
    sit strictly below the complete map by exactly that allowance — otherwise the guard would abort correct
    legs, which is the 'expectation no build can satisfy' failure this repo has already made once (the RUNG 2b
    anchor that demanded 2 fs of a build with no unconstrained X-H)."""
    for b in (_b_wurz(), _b_pilot()):
        assert b["total_floor_enforced"] < b["expected_n_mapped_atoms"]
        assert b["total_floor_enforced"] > 0


# ---- the three observations that exposed the bug ------------------------------------------------------------

def test_valb_r0_legs_are_clean():
    """All three valB_mini r0 legs recorded n_mapped_atoms = 109 (GH run 30155238348). That is the COMPLETE
    map. The wrong-sign ΔΔG_coop = -0.534 is therefore NOT a degenerate-map artifact."""
    v, why = ama.classify(109, _b_wurz())
    assert v == "CLEAN", why
    assert "complete" in why


def test_rung2b_timestep_scan_calib_anchor_is_degenerate():
    """congeneric-edge-timestep-table.json recorded n_mapped_atoms = 47 for the SAME edge the valB legs mapped
    at 109. 47 is below even the 59-heavy-atom count, so it cannot be chemistry."""
    v, why = ama.classify(47, _b_wurz())
    assert v == "DEGENERATE", why


def test_5aks_nr4a1_arm_is_degenerate_and_nr4a3_arm_is_not():
    b = _b_5aks()
    assert ama.classify(80, b)[0] == "DEGENERATE"
    assert ama.classify(111, b)[0] == "CLEAN"


# ---- UNVERIFIABLE is a real answer --------------------------------------------------------------------------

def test_absent_map_size_is_unverifiable_not_clean():
    assert ama.classify(None, _b_5aks())[0] == "UNVERIFIABLE"


def test_underivable_floor_is_unverifiable_not_clean():
    assert ama.classify(50, {"total_floor_enforced": None, "floor_note": "MCS timed out"})[0] == "UNVERIFIABLE"


# ---- the guard must RAISE, not warn -------------------------------------------------------------------------

class _FakeMol:
    def __init__(self, smiles):
        self._m = Chem.AddHs(Chem.MolFromSmiles(smiles))

    def to_rdkit(self):
        return self._m


def _lig(smiles):
    return _FakeMol(smiles)


def test_degenerate_map_raises_rather_than_warning():
    """THE HEADLINE INVARIANT. The 5a-KS NR4A1 arm's 80-of-111 map must ABORT inside `_check_mapping_sane`.
    Before this guard the only thing standing between an 80-atom map and a published ΔG was a print()."""
    rbfe = pytest.importorskip("nr4a3_rbfe")
    s = _5AKS["ligand"]["stereo_smiles"]
    a, b = _lig(s), _lig(s)
    with pytest.raises(SystemExit) as ei:
        rbfe._check_mapping_sane(None, a, b, 80)
    assert "degenerate" in str(ei.value).lower()
    assert "111" in str(ei.value)


def test_complete_map_passes_the_guard():
    rbfe = pytest.importorskip("nr4a3_rbfe")
    s = _5AKS["ligand"]["stereo_smiles"]
    rbfe._check_mapping_sane(None, _lig(s), _lig(s), 111)   # must not raise


def test_wurz_complete_map_passes_and_the_47_atom_map_aborts():
    rbfe = pytest.importorskip("nr4a3_rbfe")
    a, b = _lig(_WURZ["calib_hi"]["smiles"]), _lig(_WURZ["calib_lo"]["smiles"])
    rbfe._check_mapping_sane(None, a, b, 109)               # the real r0 map — must not raise
    with pytest.raises(SystemExit):
        rbfe._check_mapping_sane(None, a, b, 47)            # the timestep-scan map — must abort


def test_strict_element_map_on_a_congeneric_edge_is_not_aborted():
    """THE FALSE-POSITIVE GUARD, and it protects live spend: the step 1 fan-out's 19 edges run with
    prefer_element_change=False, so LOMAP is entitled to return the strict map that leaves the mutating atom
    unmapped. A guard that aborted those would kill the fan-out."""
    rbfe = pytest.importorskip("nr4a3_rbfe")
    a, b = _lig(_SMI["zaienne_cmpd19"]), _lig(_SMI["cw_ev_5nh2"])
    rbfe._check_mapping_sane(None, a, b, 21)                # 13 heavy + 8 H, the strict map — must not raise


def test_guard_is_never_silently_disabled_by_a_failure_to_derive_the_floor(monkeypatch):
    """If the floor cannot be derived the guard must SAY so and fall back to the old fractional check — not
    pass silently. A guard that no-ops on its own internal error is the failure mode this repo keeps hitting
    (a null read rendered as a benign one)."""
    rbfe = pytest.importorskip("nr4a3_rbfe")
    monkeypatch.setattr(ama, "edge_bounds", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    s = _5AKS["ligand"]["stereo_smiles"]
    with pytest.raises(SystemExit):
        # 1 mapped atom is below the pre-existing fractional floor, so the fallback must still abort.
        rbfe._check_mapping_sane(None, _lig(s), _lig(s), 1)


# ---- the identity-vs-MCS distinction (LANE 16 root cause, 2026-07-27) ---------------------------------------

def test_identity_edge_is_labelled_identity_and_mcs_edge_is_not():
    """THE DISTINCTION THAT KEEPS THE TABLE HONEST. RUNG 5a-KS writes ONE POSE TWICE, so `_load_ligands` hands
    the mapper the SAME MOLECULE twice and the correct answer is the identity permutation over all 111 atoms —
    there is no chemistry that could justify a shortfall, so every missing atom is a failed search. valB_mini
    and the fan-out edges have genuinely different endpoints and their expected count is a real MCS. One
    CLEAN/DEGENERATE column across both would read as more conclusive than the evidence supports."""
    ident = _b_5aks()
    assert ident["complete_map_provable"] is True
    assert ident["n_element_mismatched_heavy"] == 0          # -> IDENTITY
    mcs_edge = _b_wurz()
    assert mcs_edge["n_element_mismatched_heavy"] == 1        # -> a real element change, not an identity


def test_a_clean_sibling_never_upgrades_an_unrecorded_leg():
    """THE FAILURE IS HOST-DEPENDENT. LANE 16 retracted 'deterministic for this pose' — the same input mapped
    correctly on a CPU runner and short twice on Vast. So `classify` must depend ONLY on the observation it is
    given; there is no path by which another leg's clean reading can turn an absent one into CLEAN."""
    b = _b_5aks()
    assert ama.classify(111, b)[0] == "CLEAN"
    assert ama.classify(None, b)[0] == "UNVERIFIABLE"         # unchanged by the CLEAN sibling above


def test_the_5aks_fep_legs_110_of_111_is_degenerate():
    """The archived 5a-KS FEP legs recorded 110 mapped atoms of an identical 111-atom molecule — INCLUDING the
    attempts that ran after the budget was raised to 300 s. One atom short of an identity map is still a failed
    search, and the budget raise is therefore not by itself evidence that a leg ran clean."""
    assert ama.classify(110, _b_5aks())[0] == "DEGENERATE"
    assert ama.classify(80, _b_5aks())[0] == "DEGENERATE"
