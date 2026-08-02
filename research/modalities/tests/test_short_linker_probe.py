"""Tests for the <=12-backbone-atom C397 probe.

Each pins a way this answer could be wrong WITHOUT looking wrong — which is the failure mode the repo keeps
paying for, not a crash:

  * the candidate basin set being a hard-coded guess rather than DERIVED from the artifact (the whole gap was
    that `crbn|M17` had never been enumerated against because `CONFIRMED` is a fixed five-name list);
  * the finding string zipping a name order against a differently-sorted value order and publishing three
    basins with each other's atom counts (this happened, and is what `_basin_finding` is a lookup for);
  * a single reach convention deciding the verdict — the categorical audit caught `verdict()` building its
    refuted list from `best_corridor` alone while `best_through_space` two fields away disagreed, and the
    opposite error is equally available here;
  * a collision figure quoted at a length the measurement grid has no point at;
  * a molecule with no recoverable structure, which is exactly why the §2.5 ternary result is dead.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nr4a3_linker_design as LDD          # noqa: E402
import nr4a3_short_linker_probe as P       # noqa: E402

ART = os.path.join(os.path.dirname(__file__), "..", "nr4a3-short-linker-probe.json")


@pytest.fixture(scope="module")
def doc():
    with open(ART, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def basins():
    with open(os.path.join(os.path.dirname(__file__), "..", "nr4a3-orientation-basins.json"),
              encoding="utf-8") as fh:
        return json.load(fh)


# ----------------------------------------------------------------------------------------------------------
# the candidate set is DERIVED
# ----------------------------------------------------------------------------------------------------------
def test_candidate_basins_are_derived_from_the_artifact_not_listed(basins):
    """Every basin at or below the gate is selected, and nothing above it is — including basins the
    committed `CONFIRMED` list does not contain. This is the check that would have caught the original gap."""
    gate = 12
    got = {m["meta_basin_id"] for m in P.candidate_basins(basins, gate)}
    want = {m["meta_basin_id"] for m in basins["meta_basins_ranked"]
            if ((m.get("term_a_union") or {}).get("C397") or {}).get("min_linker_atoms", 99) <= gate}
    assert got == want and got, got
    assert not got <= set(LDD.CONFIRMED), \
        "the point of deriving the set is that it is NOT a subset of the hard-coded CONFIRMED list"


def test_a_basin_one_atom_over_the_gate_is_not_selected(basins):
    """`crbn|M0`'s exact C397 requirement is 13 — one over. Selecting it would silently answer a different
    question, and 13 is precisely the number rung `5b-T` flags as missing the gate by one."""
    sel = {m["meta_basin_id"] for m in P.candidate_basins(basins, 12)}
    assert "crbn|M0" not in sel
    assert "crbn|M0" in {m["meta_basin_id"] for m in P.candidate_basins(basins, 13)}


def test_the_gate_is_read_from_the_ensemble_artifact_not_typed(doc):
    with open(os.path.join(os.path.dirname(__file__), "..", "nr4a-paralogue-dynamics.json"),
              encoding="utf-8") as fh:
        dyn = json.load(fh)
    assert doc["gate"]["backbone_atoms"] == dyn["categorical_verdict"]["gate_atoms"]


# ----------------------------------------------------------------------------------------------------------
# the finding string is a LOOKUP, not a positional zip
# ----------------------------------------------------------------------------------------------------------
def test_the_basin_finding_pairs_each_id_with_its_own_number():
    """★ REGRESSION. The first version zipped `sorted(cands, key=meta_basin_id)` against a hand-written name
    order and gave every basin its neighbour's atom count. Built so the two orders DISAGREE, which is the
    only condition under which the bug is visible."""
    cands = [{"meta_basin_id": "zzz|M1", "term_a_union": {"C397": {"min_linker_atoms": 10}}},
             {"meta_basin_id": "aaa|M2", "term_a_union": {"C397": {"min_linker_atoms": 12}}}]
    s = P._basin_finding(cands)
    assert "`zzz|M1` at 10" in s and "`aaa|M2` at 12" in s
    assert "`zzz|M1` at 12" not in s and "`aaa|M2` at 10" not in s


# ----------------------------------------------------------------------------------------------------------
# the four floors, and which one binds
# ----------------------------------------------------------------------------------------------------------
def test_the_one_branch_chemistry_floor_is_basin_independent_and_matches_the_assembler():
    """n = 1 + |SEG1| + 1 + 3 + 1 + |SEG2| + tail. The floor is enumerated, not derived from that formula,
    so it stays right if a building block is added — but it must still agree with the assembler."""
    f = P.chemistry_floor_one_branch()
    smi, n, k = LDD.build_smiles("crbn", f["warhead_handle"], f["linker_segments"][0],
                                 f["linker_segments"][1], f["pendant"])
    assert n == f["n_backbone_atoms"] and 1 <= k < n
    assert n == 11, "the committed grid's shortest one-branch chain"
    # no shorter chain is assemblable at ANY handle/segment/pendant combination
    for wh in LDD.WARHEAD_HANDLE:
        for s1 in LDD.LINKER_SEGMENT:
            for s2 in LDD.LINKER_SEGMENT:
                for pk in P.C397_PENDANTS:
                    try:
                        _, m, kk = LDD.build_smiles("vhl", wh, s1, s2, pk)
                    except ValueError:
                        continue
                    if kk is not None and 1 <= kk < m:
                        assert m >= n


def test_the_geometry_answer_and_the_filter_answer_are_reported_separately(doc):
    """The whole deliverable is that these disagree. Collapsing them in either direction is the bug."""
    a = doc["answer"]["does_a_construct_at_or_below_12_atoms_exist"]
    assert a["geometry_and_chemistry"] == "YES"
    assert a["under_the_preregistered_rung_5b_filter"] == "NO"
    assert a["and_under_BOTH_reach_conventions"] in ("YES", "NO")


def test_the_binding_filter_term_is_named_and_is_not_strain_everywhere(doc):
    """A floor forced by chain strain is physics; a floor forced by basin-member coverage is policy. They
    must never render alike, and the artifact must say which one binds at every basin."""
    t = doc["answer"]["the_true_floor_and_what_forces_it"]
    assert t["binding_at_every_gate_clearing_basin"] == ["min_member_fraction_comfortable"]
    per = t["filter_terms_binding_at_the_gate_per_basin"]
    assert any("max_strain_kT_at_placement" not in v for v in per.values()), \
        "if strain bound everywhere the floor WOULD be physics and the reading would be wrong"


def test_no_preregistered_threshold_was_relaxed():
    """★ The answer is 'it fails one term', never 'we moved the term'. Pinned against the committed values
    so a future rescue-by-tuning breaks a test rather than passing quietly."""
    assert LDD.FILTER["min_member_fraction_comfortable"] == 0.25
    assert LDD.FILTER["max_strain_kT_at_placement"] == 3.0
    assert LDD.MAX_STRAIN_KT == 3.0
    assert LDD.CHEM_MAX_ATOMS == 24


# ----------------------------------------------------------------------------------------------------------
# both conventions, never merged
# ----------------------------------------------------------------------------------------------------------
def test_every_reach_cell_carries_both_conventions(doc):
    rows = doc["reach_margin_both_conventions"]["nr4a3_unique"] \
        + doc["reach_margin_both_conventions"]["conserved_competitors"]
    assert rows
    for r in rows:
        for pend, v in r["by_pendant"].items():
            assert "through_space_atoms" in v and "corridor_atoms_at_3.0A" in v, (r["placement"], pend)


def test_corridor_is_never_shorter_than_through_space(doc):
    """The corridor candidate set is a SUBSET of the through-space one, so its answer cannot be shorter.
    A violation is a genuine rule drift and the artifact records it rather than swallowing it."""
    assert doc["reach_margin_both_conventions"]["invariant_violations"] == []
    for r in doc["reach_margin_both_conventions"]["nr4a3_unique"]:
        for v in r["by_pendant"].values():
            ts, co = v["through_space_atoms"], v["corridor_atoms_at_3.0A"]
            if ts is not None and co is not None:
                assert co >= ts


def test_the_candidate_reports_a_margin_under_both_conventions(doc):
    c = doc["the_candidate"]
    assert c is not None
    m = c["reach_margin_at_its_own_length"]["by_pendant_reach"]
    for pend in ("rung5a_convention", "dab_branch"):
        for conv in ("through_space", "corridor"):
            assert m[pend][conv]["reach_margin_atoms"] is not None
            assert m[pend][conv]["reaches"] is True


def test_the_crbn_answer_is_stated_as_convention_dependent(doc):
    """crbn|M17 reaches at the gate under through-space and NOT under corridor. Ranking that away — in
    either direction — is the error the categorical audit found in the sibling lane."""
    alt = doc["the_crbn_alternative"]
    m = alt["construct"]["reach_margin_at_its_own_length"]["by_pendant_reach"]
    assert m["dab_branch"]["through_space"]["reaches"] is True
    assert m["dab_branch"]["corridor"]["reaches"] is False
    assert "CORRIDOR" in alt["⛔_the_crbn_answer"]


# ----------------------------------------------------------------------------------------------------------
# the molecule must be recoverable
# ----------------------------------------------------------------------------------------------------------
def test_the_candidate_has_a_recorded_and_reparsed_structure(doc):
    """⛔ §2.5's ternary result is dead because its molecule cannot be recovered. Every construct emitted
    here carries a SMILES, an InChIKey and a backbone length RE-DERIVED from the parsed molecule."""
    from rdkit import Chem
    everything = [doc["the_candidate"], doc["the_crbn_alternative"]["construct"]] \
        + doc["the_candidates_matched_set"]["constructs"] \
        + doc["the_crbn_alternative"]["matched_set"]
    assert len(everything) >= 4
    for c in everything:
        assert c["inchikey"] and c["canonical_smiles"] and c["rdkit_ok"] is True, c["construct_id"]
        assert c["n_backbone_atoms_measured_by_rdkit"] == c["n_backbone_atoms_intended"], c["construct_id"]
        mol = Chem.MolFromSmiles(c["canonical_smiles"])
        assert mol is not None and Chem.MolToInchiKey(mol) == c["inchikey"], c["construct_id"]


def test_the_candidate_is_at_the_gate_and_carries_a_reversible_electrophile(doc):
    c = doc["the_candidate"]
    assert c["n_backbone_atoms_intended"] == doc["gate"]["backbone_atoms"]
    assert c["pendant_reversible"] is True, "rung 5b PREFERS reversible-covalent; the acrylamide is the " \
                                            "irreversible comparator and must not be the design"
    assert c["branch_target"] == "C397 SG"
    kinds = {x["pendant"] for x in doc["the_candidates_matched_set"]["constructs"]}
    assert {"acrylamide", "cyanoprop"} <= kinds, "the comparator and the saturated control must travel with it"


# ----------------------------------------------------------------------------------------------------------
# the collision figure is read at the achieved length, and only where measured
# ----------------------------------------------------------------------------------------------------------
def test_collision_is_read_at_the_constructs_own_length_and_flags_unmeasured_lengths():
    with open(os.path.join(os.path.dirname(__file__), "..", "nr4a-paralogue-dynamics.json"),
              encoding="utf-8") as fh:
        dyn = json.load(fh)
    at12 = P.collision_at(dyn, 12)
    assert at12["is_a_measured_grid_point"] is True
    assert at12["by_scope"]["unbiased_release"]["reach_only_collision"] == 0.00124
    at13 = P.collision_at(dyn, 13)
    assert at13["is_a_measured_grid_point"] is False
    assert at13["reach_only_collision_band_across_scopes"] is None, \
        "13 is not on the grid, so there is no value to band — only a bracket"
    assert at13["by_scope"]["unbiased_release"]["bracket_atoms"] == [12, 14]
    at11 = P.collision_at(dyn, 11)
    assert at11["is_a_measured_grid_point"] is False, \
        "★ nothing BELOW 12 is measured; that is why the candidate sits AT the gate rather than under it"


def test_the_reported_collision_matches_its_one_home(doc):
    with open(os.path.join(os.path.dirname(__file__), "..", "nr4a-paralogue-dynamics.json"),
              encoding="utf-8") as fh:
        dyn = json.load(fh)
    n = doc["the_candidate"]["n_backbone_atoms_intended"]
    for scope, v in doc["paralogues_at_its_own_length"]["by_scope"].items():
        src = dyn["categorical_verdict"]["by_scope"][scope]["by_linker_atoms"][str(n)]
        assert v["reach_only_collision"] == src["P_paralogue_also_labelled_given_nr4a3"]


# ----------------------------------------------------------------------------------------------------------
# scope discipline
# ----------------------------------------------------------------------------------------------------------
def test_the_artifact_refuses_the_claims_it_cannot_make(doc):
    text = json.dumps(doc["what_this_licenses"]).lower()
    for forbidden in ("degradation", "efficacy", "safety", "affinity", "ternary"):
        assert forbidden in text, "the does-NOT-license list must name %r explicitly" % forbidden
    carried = json.dumps(doc["carried_honestly"])
    assert "C420" in carried and "C559" in carried, "the refuted/surviving split must travel"
    assert "site selection" in carried.lower() or "SITE-selection" in carried
    assert "68 of 75" in carried, "NR4A1 C465 inside the envelope more often than C397 itself"


def test_the_probe_reproduces_its_committed_artifact():
    """`--check` regenerates and diffs, ignoring only the timestamp. A drifted artifact is a stale fact that
    reads as a current one (CLAUDE.md §7)."""
    assert P.main(["--check"]) == 0
