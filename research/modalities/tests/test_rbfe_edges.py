"""Unit tests for rbfe_edges.py — the pure RBFE cycle bookkeeping + edge/leg enumeration + map sanity."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rbfe_edges as re  # noqa: E402


def test_legs_shape():
    legs = re.rbfe_legs()
    assert legs[0] == ("solvent", "shared", "solvent")
    # one complex-morph leg per receptor
    complex_legs = [l for l in legs if l[2] == "complex"]
    assert len(complex_legs) == len(re.RECEPTORS)
    assert ("complex-nr4a3", "nr4a3", "complex") in legs


def test_ddg_cycle():
    # ΔΔG_bind = ΔG_complex(A->B) - ΔG_solvent(A->B)
    assert re.ddg_bind(-5.0, -2.0) == -3.0        # B binds 3 kcal/mol tighter than A here
    assert re.ddg_bind(2.0, 2.0) == 0.0           # no change


def test_absolute_anchoring():
    # B absolute = 401 anchor + RBFE increment
    assert re.absolute_dg_B(-4.0, "nr4a3") == re.ANCHOR_401_ABFE["nr4a3"] - 4.0


def test_selectivity_from_rbfe_direction():
    # If B improves NR4A3 binding by 4 and does nothing to paralogues, B is MORE NR4A3-selective than 401.
    ddg = {"nr4a3": -4.0, "nr4a1": 0.0, "nr4a2": 0.0}
    sel = re.selectivity_from_rbfe(ddg)
    # 401 selectivity vs NR4A1 = -1.2 - 8.5 = -9.7; B = -5.2 - 8.5 = -13.7 -> more negative = more selective
    assert sel["nr4a1"] < (re.ANCHOR_401_ABFE["nr4a3"] - re.ANCHOR_401_ABFE["nr4a1"])
    # anchor-free selectivity change should be negative (more selective) for NR4A1
    chg = re.selectivity_change_only(ddg)
    assert chg["nr4a1"] == -4.0 and chg["nr4a2"] == -4.0


def test_selectivity_change_is_anchor_free():
    # selectivity_change_only must not depend on the anchor at all
    ddg = {"nr4a3": -3.0, "nr4a1": -1.0, "nr4a2": 0.5}
    assert re.selectivity_change_only(ddg) == {"nr4a1": -2.0, "nr4a2": -3.5}


def test_map_sanity_congeneric():
    # 401 -> lo_m0_NCCO is a well-behaved single-edge morph (add ortho-acetamido, ~6 unique atoms)
    m = re.mapping_summary(re.SMILES["denovo_401"], re.SMILES["lo_m0_NCCO_gen"])
    if not m:                     # rdkit absent in this env
        return
    assert m["n_unique_A"] == 0                    # 401 is a subgraph of lo_m0_NCCO
    assert 3 <= m["n_unique_B"] <= 8               # the acetamido (NC(C)=O = 4 heavy atoms) region
    assert m["well_behaved_edge"] is True


def test_edge_plan_self_describing():
    p = re.edge_plan()
    assert p["ligand_A"] == "denovo_401" and p["ligand_B"] == "lo_m0_NCCO_gen"
    assert p["legs"][0][2] == "solvent"
    assert "map_sanity" in p       # rdkit present here


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print(f"ok {name}")
    print("all rbfe_edges tests passed")
