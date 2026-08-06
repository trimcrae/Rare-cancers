"""Tests for `nr4a3_effector_stage.py` — the transcriptional-effector second-terminus staging path.

What is worth testing here, and why it is not the network. The fetch is one `urllib` call and RCSB is not
ours to hold still. The part that can be silently wrong is the part `nr4a3_e3_stage` could NOT do: choosing
the rigid body when the ligand site spans two protomers. A one-chain body is not an error anything downstream
raises — it just understates the excluded volume and can put the exit vector on the face where the missing
protomer used to be, and every distance after that still looks reasonable. So these tests build coordinates
whose right answer is known by construction and check that the selector returns it, that it REFUSES rather
than guesses when the answer is ambiguous, and that the record it emits is loadable by the consumer the reach
enumeration actually uses.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, MOD)

import basin_geom as G                       # noqa: E402
import nr4a3_basin_search as BS              # noqa: E402
import nr4a3_e3_stage as E3                  # noqa: E402
import nr4a3_effector_stage as EF            # noqa: E402


# ---------------------------------------------------------------------------------------------------------
# synthetic coordinates with a known right answer
# ---------------------------------------------------------------------------------------------------------
def _residue(chain, resid, centre, resname="ALA"):
    """One pseudo-residue: N, CA, C, O and a CB offset, so the body loads through parse_multichain_pdb."""
    x, y, z = centre
    return [
        {"name": "N", "resname": resname, "chain": chain, "resid": resid, "icode": " ",
         "xyz": (x, y, z), "elem": "N"},
        {"name": "CA", "resname": resname, "chain": chain, "resid": resid, "icode": " ",
         "xyz": (x + 0.5, y, z), "elem": "C"},
        {"name": "C", "resname": resname, "chain": chain, "resid": resid, "icode": " ",
         "xyz": (x + 1.0, y, z), "elem": "C"},
        {"name": "O", "resname": resname, "chain": chain, "resid": resid, "icode": " ",
         "xyz": (x + 1.0, y + 0.8, z), "elem": "O"},
        {"name": "CB", "resname": resname, "chain": chain, "resid": resid, "icode": " ",
         "xyz": (x + 0.5, y - 1.2, z), "elem": "C"},
    ]


def _slab(chain, x0, n=40, dy=0.0):
    """A slab of residues along +y at x = x0, so two slabs at different x face each other."""
    out = []
    for i in range(n):
        out += _residue(chain, i + 1, (x0, dy + i * 2.5, 0.0))
    return out


def _dimer_with_groove_ligand():
    """Two chains 6 A apart with a 20-atom ligand in the gap touching BOTH, plus a distant decoy chain.

    Right answer by construction: the body is {A, B}; C is far away and must not be selected.
    """
    prot = _slab("A", 0.0) + _slab("B", 6.0) + _slab("C", 90.0)
    het = []
    for i in range(20):
        het.append({"name": f"C{i}", "resname": "LIG", "chain": "A", "resid": 900, "icode": " ",
                    "xyz": (3.0, 20.0 + i * 0.9, 0.0), "elem": "C"})
    return prot, het


# ---------------------------------------------------------------------------------------------------------
# 1 · the body is the ligand's own contacts
# ---------------------------------------------------------------------------------------------------------
def test_a_groove_ligand_spanning_two_protomers_selects_both_chains():
    prot, het = _dimer_with_groove_ligand()
    chains = {"A", "B", "C"}
    lig = E3.pick_ligand(prot, het, chains, chains)
    assert lig is not None
    body, info = EF.select_ligand_body(prot, chains, lig, max_chains=2)
    assert body is not None, info
    assert sorted(body) == ["A", "B"], info
    assert info["n_chains_the_ligand_spans"] == 2
    assert info["completed_through_interface"] is False
    assert "C" not in info["chains_the_ligand_touches"]


def test_the_one_chain_body_that_would_have_been_staged_is_measurably_smaller():
    """The defect this module exists to avoid, made numeric rather than argued."""
    prot, het = _dimer_with_groove_ligand()
    chains = {"A", "B", "C"}
    lig = E3.pick_ligand(prot, het, chains, chains)
    two, _ = EF.select_ligand_body(prot, chains, lig, max_chains=2)
    one, _ = EF.select_ligand_body(prot, chains, lig, max_chains=1)
    n_two = len([a for a in prot if a["chain"] in set(two)])
    n_one = len([a for a in prot if a["chain"] in set(one)])
    assert n_two == 2 * n_one


def test_a_single_chain_ligand_site_stays_a_single_chain():
    prot = _slab("A", 0.0) + _slab("B", 60.0)
    het = [{"name": f"C{i}", "resname": "LIG", "chain": "A", "resid": 900, "icode": " ",
            "xyz": (-3.0, 20.0 + i * 0.9, 0.0), "elem": "C"} for i in range(20)]
    lig = E3.pick_ligand(prot, het, {"A", "B"}, {"A", "B"})
    body, info = EF.select_ligand_body(prot, {"A", "B"}, lig, max_chains=1)
    assert sorted(body) == ["A"], info


# ---------------------------------------------------------------------------------------------------------
# 2 · it refuses rather than guessing
# ---------------------------------------------------------------------------------------------------------
def test_a_partner_chain_that_only_brushes_the_body_is_refused_not_completed():
    """A ligand buried in one chain, with the declared unit asking for two and no real interface anywhere."""
    prot = _slab("A", 0.0) + _slab("B", 60.0)
    het = [{"name": f"C{i}", "resname": "LIG", "chain": "A", "resid": 900, "icode": " ",
            "xyz": (-3.0, 20.0 + i * 0.9, 0.0), "elem": "C"} for i in range(20)]
    lig = E3.pick_ligand(prot, het, {"A", "B"}, {"A", "B"})
    body, info = EF.select_ligand_body(prot, {"A", "B"}, lig, max_chains=2)
    assert body is None
    assert "interface" in info["reason"]
    assert info["candidate_partner_chains"][0]["interface_residues"] < EF.MIN_INTERFACE_RESIDUES


def test_two_equally_good_partner_chains_are_refused_as_ambiguous():
    """Crystal packing that looks exactly like a biological dimer must not be resolved by picking one."""
    prot = _slab("A", 0.0) + _slab("B", 6.0) + _slab("C", -6.0)
    het = [{"name": f"C{i}", "resname": "LIG", "chain": "A", "resid": 900, "icode": " ",
            "xyz": (0.0, 20.0 + i * 0.9, 3.5), "elem": "C"} for i in range(20)]
    lig = E3.pick_ligand(prot, het, {"A", "B", "C"}, {"A", "B", "C"})
    body, info = EF.select_ligand_body(prot, {"A", "B", "C"}, lig, max_chains=2)
    assert body is None, info
    assert "AMBIGUOUS" in info["reason"]


# ---------------------------------------------------------------------------------------------------------
# 3 · the record the reach enumeration will consume
# ---------------------------------------------------------------------------------------------------------
def test_a_staged_record_loads_through_the_consumer_the_reach_enumeration_uses(tmp_path):
    prot, het = _dimer_with_groove_ligand()
    lig = E3.pick_ligand(prot, het, {"A", "B"}, {"A", "B"})
    body, _ = EF.select_ligand_body(prot, {"A", "B", "C"}, lig, max_chains=2)
    pdb = tmp_path / "synthetic-receptor.pdb"
    with open(pdb, "w") as fh:
        for i, a in enumerate([a for a in prot if a["chain"] in set(body)], 1):
            fh.write("ATOM  %5d %-4s %3s %s%4d    %8.3f%8.3f%8.3f  1.00  0.00          %2s\n"
                     % (i, a["name"][:4], a["resname"], a["chain"], a["resid"],
                        a["xyz"][0], a["xyz"][1], a["xyz"][2], a["elem"][:2]))
    rec = {"arm_id": "synthetic_effector", "recruiter": "SYNTH", "crl": None,
           "partner_class": "transcriptional effector",
           "receptor_pdb": os.path.relpath(str(pdb), EF.REPO), "ligand": lig, "ring": None}
    arm = BS.load_arm_from_registry(rec)
    assert arm["n_ca"] == 80
    assert arm["ring"] is None and arm["cullin"] is None
    assert arm["tanchor"] is None
    assert arm["anchor"] == tuple(lig["exit_atom_xyz"])


def test_the_self_check_refuses_a_record_whose_coordinates_are_missing():
    rec = {"arm_id": "ghost", "recruiter": "GHOST", "receptor_pdb": "results/does-not-exist.pdb",
           "ligand": {"exit_atom_xyz": [0.0, 0.0, 0.0], "ligand_centroid": [0, 0, 0], "het_code": "X",
                      "atoms": [{"xyz": [0.0, 0.0, 0.0]}]}, "ring": None}
    out = EF.self_check(rec, lambda m: None)
    assert out["ok"] is False


# ---------------------------------------------------------------------------------------------------------
# 4 · the effector choice is carried with its evidence, and is not an E3
# ---------------------------------------------------------------------------------------------------------
def test_every_effector_spec_carries_a_chemical_handle_and_its_evidence():
    """A body with no small-molecule ligand cannot supply `b` at all, so the handle is not optional."""
    for aid, spec in EF.EFFECTORS.items():
        assert spec["partner_class"] == "transcriptional effector", aid
        assert spec["chemical_handle"], aid
        assert spec["evidence"], aid
        assert spec["accession"] and spec["accession"][0].isalpha(), aid
        assert spec["max_body_chains"] >= 1, aid


def test_the_bcl6_choice_quotes_the_paper_that_motivates_the_route():
    """The effector is chosen on the prior art's own words, not on a recollection of them."""
    ev = EF.EFFECTORS["bcl6"]["evidence"]
    assert ev["doi"] == "10.1021/jacs.5c05634"
    assert "BCL6" in ev["quote_recruits"]
    assert "BI3812" in ev["quote_ligand"]
    assert "⚠_citation_gate" in ev


def test_no_effector_spec_supplies_a_pdb_id():
    """Non-fabrication: a recalled PDB ID is the plausible-and-wrong input this repo has been bitten by."""
    blob = json.dumps(EF.EFFECTORS)
    assert "seed_ids" not in blob
    assert "pdb_id" not in blob


@pytest.mark.parametrize("aid", sorted(EF.EFFECTORS))
def test_the_offline_plan_touches_no_network(aid, monkeypatch, capsys):
    def boom(*a, **k):                                                  # noqa: ANN001
        raise AssertionError("the offline plan made a network call")
    monkeypatch.setattr(E3, "_get", boom)
    monkeypatch.setattr(E3, "_post_json", boom)
    assert EF.main(["--plan", "--arms", aid]) == 0
    assert EF.EFFECTORS[aid]["accession"] in capsys.readouterr().out
