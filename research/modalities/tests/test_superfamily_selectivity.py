import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nr4a_superfamily_selectivity as ss  # noqa: E402


# A tiny reference where the pocket positions are easy to reason about.
# positions (1-based):        1234567
REF = "ACDEFGH"               # pocket residues we'll probe: 1(A) 4(E) 7(H)


def test_similar_identity_and_group():
    assert ss._similar("L", "L")            # identical
    assert ss._similar("L", "I")            # both hydrophobic AVLIM
    assert ss._similar("F", "Y")            # both aromatic FWY
    assert ss._similar("D", "E")            # both negative DE
    assert not ss._similar("L", "D")        # hydrophobic vs negative
    assert not ss._similar("G", "P")        # each is its own singleton group
    assert not ss._similar("A", "-")        # gap is never similar


def test_pocket_conservation_all_identical():
    mapping = {1: "A", 4: "E", 7: "H"}      # perfect match at every probed position
    r = ss.pocket_conservation(REF, [1, 4, 7], mapping)
    assert r["n"] == 3
    assert r["pocket_identity"] == 1.0
    assert r["pocket_similarity"] == 1.0
    assert all(row["identical"] and row["similar"] for row in r["rows"])


def test_pocket_conservation_similar_not_identical():
    # A->V (hydrophobic, similar not identical); E->D (negative, similar); H->W (aromatic vs positive: neither)
    mapping = {1: "V", 4: "D", 7: "W"}
    r = ss.pocket_conservation(REF, [1, 4, 7], mapping)
    assert r["pocket_identity"] == 0.0                  # none identical
    assert round(r["pocket_similarity"], 3) == round(2 / 3, 3)   # A~V and E~D similar, H~W not


def test_pocket_conservation_gap_and_out_of_range():
    mapping = {1: "A"}                                  # positions 4,7 gapped; 99 is out of range
    r = ss.pocket_conservation(REF, [1, 4, 99], mapping)
    assert r["n"] == 2                                  # 99 excluded from the denominator
    assert r["pocket_identity"] == 0.5                  # only position 1 matches of the 2 in-range
    oor = [row for row in r["rows"] if row.get("_status") == "out of range"]
    assert len(oor) == 1 and oor[0]["position"] == 99


def test_handles_flagged():
    mapping = {p: "A" for p in ss.POCKET_RESIDUES}
    # build a ref long enough to contain the real pocket positions
    ref = "A" * (max(ss.POCKET_RESIDUES) + 1)
    r = ss.pocket_conservation(ref, ss.POCKET_RESIDUES, mapping)
    handle_rows = [row for row in r["rows"] if row.get("is_handle")]
    assert {row["position"] for row in handle_rows} == ss.HANDLES
