"""The step 1 atom-map diagnostic, and the chemistry it root-caused.

These tests do NOT need openfe. The verdict logic is pure, and the chemistry claim — that the strict-element
MCS is severed by the ester-O -> amide-N substitution while the element-agnostic one is complete — is
reproducible with rdkit alone, which is exactly why it is a diagnosis and not a story.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import step1_map_diag as smd  # noqa: E402


def _row(ec0, ec1, floor=20, prod=None, walls=None):
    """One matrix row at the module's own budgets, with everything else held benign."""
    lo, hi = min(smd.BUDGETS), max(smd.BUDGETS)
    walls = walls or {}
    cells = {}
    for ec, vals in ((0, ec0), (1, ec1)):
        for b, n in zip((lo, hi), vals):
            cells[f"ec{ec}_t{b}"] = {"n_mapped": n, "wall_s": walls.get((ec, b), 0.1), "error": None}
    prod = ec0[0] if prod is None else prod
    return {"matrix": cells, "provable_floor": floor, "production_n_mapped": prod,
            "production_clears_floor": (None if (floor is None or prod is None) else prod >= floor)}


# --------------------------------------------------------------------------------------------------------
# the verdict logic — the thing that decides which fix a failed edge gets
# --------------------------------------------------------------------------------------------------------

def test_element_change_signature_is_reported_as_such():
    """Settings separate, neither moves with the budget, ec=True clears the floor -> H2, not a timeout."""
    v, why = smd.verdict(_row(ec0=(17, 17), ec1=(22, 22), floor=20, prod=17))
    assert v == "ELEMENT_CHANGE"
    assert "budget is not binding" in why


def test_a_map_that_grows_with_the_budget_is_a_timeout():
    """The one signature that means 'raise RBFE_LOMAP_TIME_S'. It must never be mislabelled ELEMENT_CHANGE,
    because the two fixes are opposite and the wrong one wastes a rental."""
    v, why = smd.verdict(_row(ec0=(14, 21), ec1=(15, 22), floor=20, prod=14))
    assert v == "TIMEOUT"


def test_a_search_that_burns_its_budget_is_a_timeout_even_without_growth():
    """A search pinned at its budget is a timeout whether or not the longer budget happened to help — the
    map is then a function of the host's speed, which is the defect regardless of this run's number."""
    lo = min(smd.BUDGETS)
    v, _ = smd.verdict(_row(ec0=(17, 17), ec1=(22, 22), floor=20, prod=17,
                            walls={(0, lo): lo * 0.9}))
    assert v == "TIMEOUT"


def test_a_clean_map_is_clean_and_no_mechanism_is_invented_for_it():
    v, why = smd.verdict(_row(ec0=(21, 21), ec1=(22, 22), floor=20, prod=21))
    assert v == "CLEAN"
    assert "21" in why


def test_an_underivable_floor_is_UNVERIFIABLE_never_clean():
    """This repo has repeatedly had a null reading rendered as a benign one. An absent floor is an absent
    reading, and the guard must say so rather than pass the edge."""
    v, _ = smd.verdict(_row(ec0=(17, 17), ec1=(22, 22), floor=None, prod=17))
    assert v == "UNVERIFIABLE"


def test_a_mapper_that_cannot_reach_the_floor_at_any_setting_says_so():
    """★ THE ACTUAL cw_bio_nmethyl_amide RESULT, measured on the production staged components: ec=False 17,
    ec=True 19, identical at both budgets, against a floor of 20. The budget is provably not binding and no
    setting clears the floor — which is a statement about the MAPPERS, not about a rented host, and means
    the edge is not a retry candidate. Filing that as a generic UNEXPLAINED would invite exactly the retry
    it must not get."""
    row = _row(ec0=(17, 17), ec1=(19, 19), floor=20, prod=19)
    row["kartograf_n_mapped"] = None
    v, why = smd.verdict(row)
    assert v == "MAPPER_CANNOT_REACH_FLOOR"
    assert "not a retry candidate" in why


def test_a_signature_matching_neither_mechanism_is_UNEXPLAINED():
    """Production is short, no setting separates, the budget is not binding — and yet a mapper DOES clear
    the floor, so "the mappers cannot reach it" is false and nothing else fits either. Genuinely unreadable,
    so it must reach a human rather than be filed under whichever label is nearest."""
    row = _row(ec0=(17, 17), ec1=(17, 17), floor=20, prod=17)
    row["kartograf_n_mapped"] = 25          # a mapper DOES clear the floor, so "cannot reach" is false
    v, why = smd.verdict(row)
    assert v == "UNEXPLAINED"
    assert "human" in why


def test_kartograf_clearing_the_floor_is_not_reported_as_unmappable():
    """If the geometric fallback reaches the floor the edge IS mappable and the finding is that production
    does not reach that mapper — a different, actionable conclusion."""
    row = _row(ec0=(17, 17), ec1=(19, 19), floor=20, prod=19)
    row["kartograf_n_mapped"] = 22
    v, _ = smd.verdict(row)
    assert v != "MAPPER_CANNOT_REACH_FLOOR"


def test_element_change_verdict_requires_the_escalated_map_to_ACTUALLY_clear_the_floor():
    """ec=True larger is not enough — if it is still under the floor, escalating would not fix the edge and
    calling it ELEMENT_CHANGE would send the next reader to a fix that does not work. (It lands on
    MAPPER_CANNOT_REACH_FLOOR, which is the correct, more specific answer; what matters here is that it is
    NOT the one that recommends escalating.)"""
    v, _ = smd.verdict(_row(ec0=(14, 14), ec1=(18, 18), floor=20, prod=14))
    assert v == "MAPPER_CANNOT_REACH_FLOOR"


# --------------------------------------------------------------------------------------------------------
# the chemistry — the actual root cause of s1f-09's leg-complex-FAILED-rc1
# --------------------------------------------------------------------------------------------------------

ESTER = "COC(=O)c1c[nH]c2ccc(Br)cc12"          # zaienne_cmpd19
NME_AMIDE = "CNC(=O)c1c[nH]c2ccc(Br)cc12"      # cw_bio_nmethyl_amide


def _mcs(smi_a, smi_b, agnostic):
    from rdkit import Chem
    from rdkit.Chem import rdFMCS
    a, b = Chem.AddHs(Chem.MolFromSmiles(smi_a)), Chem.AddHs(Chem.MolFromSmiles(smi_b))
    cmp_ = rdFMCS.AtomCompare.CompareAny if agnostic else rdFMCS.AtomCompare.CompareElements
    r = rdFMCS.FindMCS([a, b], atomCompare=cmp_, bondCompare=rdFMCS.BondCompare.CompareAny, timeout=60)
    return r.numAtoms, r.canceled


def test_the_strict_map_is_severed_by_the_ester_to_amide_substitution():
    """THE ROOT CAUSE, reproduced. The strict-element MCS loses exactly the ester O, the methyl C and its
    three H — 5 atoms — because it cannot cross the O->N substitution, while the element-agnostic MCS is
    complete at 22. These are the numbers the failing leg logged (17), and the floor it missed (20)."""
    strict, cancelled_s = _mcs(ESTER, NME_AMIDE, agnostic=False)
    loose, cancelled_l = _mcs(ESTER, NME_AMIDE, agnostic=True)
    assert strict == 17
    assert loose == 22
    assert loose - strict == 5, "the O, the methyl C and its 3 H"
    # NEITHER search timed out, which is what refutes the budget hypothesis the abort message used to assert.
    assert not cancelled_s and not cancelled_l


def test_the_provable_floor_condemns_the_strict_map_and_admits_the_agnostic_one():
    import atom_map_audit as ama
    b = ama.edge_bounds("zaienne_cmpd19", ESTER, "cw_bio_nmethyl_amide", NME_AMIDE)
    floor = b["total_floor_enforced"]
    assert floor == 20
    assert b["expected_n_mapped_atoms"] == 22
    assert 17 < floor <= 22, "the strict map is below the floor; the element-agnostic map clears it"


@pytest.mark.parametrize("smi_a,smi_b,ligand_b", [
    (ESTER, "COC(=O)c1c[nH]c2ccc(N)cc12", "cw_ev_5nh2"),
    (ESTER, "COC(=O)c1c[nH]c2ccc(O)cc12", "cw_ev_5oh"),
])
def test_the_escalation_is_dead_code_for_edges_whose_strict_map_already_clears_its_floor(
        smi_a, smi_b, ligand_b):
    """★ THE SAFETY ARGUMENT FOR LANDING THE FIX UNDER A LIVE FLEET.

    `_mapping`'s escalation fires ONLY when the strict map is below the provable floor. Any leg that is
    RUNNING has already passed `_check_mapping_sane`, i.e. sits at or above that same floor — so for it the
    clause is unreachable and the returned mapping is unchanged. If this ever fails, the fix has become
    capable of changing the perturbation of a leg that is mid-flight, which is a silent protocol deviation.
    """
    import atom_map_audit as ama
    strict, _ = _mcs(smi_a, smi_b, agnostic=False)
    floor = ama.edge_bounds("A", smi_a, "B", smi_b)["total_floor_enforced"]
    assert strict >= floor, f"{ligand_b}: strict {strict} < floor {floor} would newly trigger escalation"


def test_exactly_one_fanout_edge_has_a_strict_map_below_its_floor():
    """The blast radius, pinned. If a future map edit makes this two, the safety argument above has to be
    re-made rather than assumed — and a second edge is also a second aborted rental nobody expected."""
    import atom_map_audit as ama
    import congeneric_fanout as cf
    below = []
    for u in cf.default_units():
        floor = ama.edge_bounds(u["ligand_a"], u["smiles_a"],
                                u["ligand_b"], u["smiles_b"])["total_floor_enforced"]
        if floor is None:
            continue
        strict, _ = _mcs(u["smiles_a"], u["smiles_b"], agnostic=False)
        if strict < floor:
            below.append(u["ligand_b"])
    assert below == ["cw_bio_nmethyl_amide"]
