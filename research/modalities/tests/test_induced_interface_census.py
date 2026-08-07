"""The induced-interface census must measure the SAMPLER's predicate, and must parse real mmCIF.

WHY THIS FILE EXISTS. `nr4a3_induced_interface_census.py` exists to answer one question with
coordinates instead of prose: how big is the induced interface of a real chemically-induced complex,
measured by the SAME rule that `nr4a3_basin_search` uses to decide whether a sampled placement is an
interface at all? Two ways that can go quietly wrong, and both did during development:

  1. THE THRESHOLDS DRIFT. If the census hard-codes 6.0 A / 12 points instead of reading
     `nr4a3_basin_search.PARAMS`, then the day the sampler's floor changes the census keeps
     reporting against the old one and the comparison silently stops being a comparison.
  2. THE PARSER SILENTLY DROPS THE FIELD THAT NAMES THE CHAINS. mmCIF puts a loop ROW across
     several lines and a description inside a `;`-delimited block. A line-by-line reader returns a
     perfectly clean table of "chain A vs chain B" with every description missing — and a table
     nobody can read invites guessing which chain was the effector. That is a wrong answer wearing
     the costume of a parse.

So the tests below pin the predicate against hand-placed points at KNOWN distances (no fixture, no
mock: if the classification is wrong the arithmetic is wrong), and run the real parser over an mmCIF
fragment carrying all three shapes that broke it.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
if MOD not in sys.path:
    sys.path.insert(0, MOD)

C = pytest.importorskip("nr4a3_induced_interface_census")
BS = pytest.importorskip("nr4a3_basin_search")


def test_the_predicate_is_the_samplers_and_is_not_re_typed():
    """The census must read its thresholds from the sampler, not carry its own copy."""
    assert C.PARAMS is BS.PARAMS
    for key in ("hard_clash_A", "soft_clash_A", "contact_A", "min_contact_residues"):
        assert key in C.PARAMS


def test_contact_classification_matches_the_samplers_three_bands():
    """One target atom at the origin; arm points placed at distances that sit in each band."""
    p = C.PARAMS
    hard, soft, contact = p["hard_clash_A"], p["soft_clash_A"], p["contact_A"]
    target = [(0.0, 0.0, 0.0)]
    pts = [
        (hard - 0.5, 0.0, 0.0),                 # hard clash
        ((hard + soft) / 2.0, 0.0, 0.0),        # soft clash
        ((soft + contact) / 2.0, 0.0, 0.0),     # contact
        (contact + 2.0, 0.0, 0.0),              # too far to count at all
    ]
    owners = [("A", str(i), "") for i in range(len(pts))]
    prof = C.contact_profile(target, pts, owners)
    assert prof["n_hard_points"] == 1
    assert prof["n_soft_points"] == 1
    assert prof["n_contact_points"] == 1
    assert prof["n_query_points"] == 4
    # The residue count and the POINT count are different numbers and must never be swapped: there
    # are two query points per residue, so a floor of 12 points is as few as 6 residues.
    assert prof["n_residues_with_a_contact_point"] == 1


MINI_CIF = """data_TEST
#
_entry.id TEST
_struct.title
'A deliberately awkward test entry'
#
loop_
_entity.id
_entity.type
_entity.pdbx_description
1 polymer
;First protein, described in a semicolon block
that wraps onto a second line
;
2 polymer 'Second protein'
#
loop_
_entity_poly.entity_id
_entity_poly.type
_entity_poly.pdbx_strand_id
1 'polypeptide(L)' A
2 'polypeptide(L)' B
#
loop_
_atom_site.group_PDB
_atom_site.id
_atom_site.type_symbol
_atom_site.label_atom_id
_atom_site.label_alt_id
_atom_site.label_comp_id
_atom_site.label_asym_id
_atom_site.label_seq_id
_atom_site.pdbx_PDB_ins_code
_atom_site.Cartn_x
_atom_site.Cartn_y
_atom_site.Cartn_z
_atom_site.occupancy
_atom_site.B_iso_or_equiv
_atom_site.auth_seq_id
_atom_site.auth_asym_id
_atom_site.pdbx_PDB_model_num
ATOM 1 N N . ALA A 1 ? 0.000 0.000 0.000 1.00 10.0 1 A 1
ATOM 2 C CA . ALA A 1 ? 1.500 0.000 0.000 1.00 10.0 1 A 1
ATOM 3 C CB . ALA A 1 ? 2.500 1.000 0.000 1.00 10.0 1 A 1
ATOM 4 H H . ALA A 1 ? 2.500 2.000 0.000 1.00 10.0 1 A 1
ATOM 5 N N . GLY B 1 ? 8.000 0.000 0.000 1.00 10.0 1 B 1
ATOM 6 C CA . GLY B 1 ? 6.500 0.000 0.000 1.00 10.0 1 B 1
ATOM 7 C CA . GLY B 1 ? 99.000 0.000 0.000 1.00 10.0 1 B 2
#
"""


def test_the_parser_reads_a_next_line_title_a_wrapped_loop_row_and_a_semicolon_block():
    st = C.parse_cif(MINI_CIF)
    meta = st["meta"]
    assert meta["title"] == "A deliberately awkward test entry"
    # The description that names chain A lives in a `;` block spanning two lines inside a loop row.
    # If the reader is line-based this comes back empty and the chain is anonymous.
    assert "First protein" in (meta["chain_descriptions"].get("A") or "")
    assert meta["chain_descriptions"].get("B") == "Second protein"


def test_hydrogens_and_models_beyond_the_first_are_dropped():
    st = C.parse_cif(MINI_CIF)
    names = [(a["chain"], a["name"]) for a in st["atoms"]]
    assert ("A", "H") not in names, "hydrogens must be dropped; every threshold is heavy-atom"
    # The second model's CA sits at x=99 and must not appear.
    assert all(abs(a["xyz"][0] - 99.0) > 1e-6 for a in st["atoms"])


def test_query_points_are_ca_plus_side_chain_centroid_exactly_as_the_arm_loader_builds_them():
    st = C.parse_cif(MINI_CIF)
    pts, owners = C.query_points(st["atoms"], ["A"])
    assert len(pts) == 2, "one residue must contribute exactly two query points (CA + side chain)"
    assert pts[0] == (1.5, 0.0, 0.0)          # the CA
    assert pts[1] == (2.5, 1.0, 0.0)          # the sole non-backbone heavy atom, CB
    # Glycine has no side chain, so its second point falls back to the CA rather than vanishing.
    gly_pts, _ = C.query_points(st["atoms"], ["B"])
    assert len(gly_pts) == 2 and gly_pts[0] == gly_pts[1]


def test_every_curated_class_row_names_a_reason():
    """`ENTRY_CLASSES` is the file's only judgement call; a row without a stated reason is an
    unattributable opinion sitting inside a measurement."""
    for pdb_id, spec in C.ENTRY_CLASSES.items():
        assert spec.get("classes"), pdb_id
        assert spec.get("why"), pdb_id
        if spec.get("allosteric_pairs"):
            assert spec.get("allosteric_reason"), pdb_id
        if spec.get("exclude_pairs"):
            assert spec.get("exclude_reason"), pdb_id


def test_a_curated_pair_is_labelled_as_curated_and_never_as_measured():
    """The two kinds of induced pair must stay distinguishable in the output, so a reader can drop
    the curated rows and recompute."""
    entry = {
        "pdb_id": "3KDJ",
        "chain_pairs": [
            {"pair": ["A", "B"], "ligand_bridged_by": [], "n_contact_points_min": 34,
             "n_contact_points_max": 36},
        ],
    }
    got = C.induced_pairs(entry)
    assert len(got) == 1
    assert got[0]["induced_basis"] == "allosteric_curated"
    assert got[0]["induced_basis_reason"]


def test_an_excluded_pair_is_dropped_entirely():
    entry = {
        "pdb_id": "9MZA",
        "chain_pairs": [
            {"pair": ["A", "C"], "ligand_bridged_by": ["A1BUC"], "n_contact_points_min": 66,
             "n_contact_points_max": 71},
            {"pair": ["A", "D"], "ligand_bridged_by": ["A1BUC"], "n_contact_points_min": 6,
             "n_contact_points_max": 7},
        ],
    }
    got = C.induced_pairs(entry)
    assert [p["pair"] for p in got] == [["A", "D"]], (
        "the BCL6 BTB homodimer is spanned by the same bivalent ligand and is still constitutive; "
        "letting it into the induced class would move every summary")


def test_the_committed_artifact_still_measures_against_the_live_floor():
    """The artifact is read by the memo and the blocker record. If the sampler's floor ever moves and
    the artifact is not regenerated, the comparison it carries stops being true — and it would look
    exactly as it does now."""
    import json
    path = os.path.join(MOD, "nr4a3-induced-interface-census.json")
    if not os.path.exists(path):
        pytest.skip("census artifact not present on this branch")
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    assert doc["_floor_under_test"]["min_contact_residues"] == BS.PARAMS["min_contact_residues"]
    assert doc["summary_over_induced_pairs"]["floor_under_test"] == \
        BS.PARAMS["min_contact_residues"]
