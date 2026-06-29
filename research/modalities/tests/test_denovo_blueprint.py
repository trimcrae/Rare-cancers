"""Tests for denovo_blueprint — the pure selectivity classification behind the de-novo conditioning spec.

Proves the selective/conserved partition, the per-handle paralogue-discrimination tagging + weighting, and
the engageable filter are correct without any structure/IO (TESTING.md #3).
"""
import denovo_blueprint as bp

# A faithful subset of the orthosteric Pocket-5 residues from nr4a-selectivity.json.
POCKET5 = [
    {"nr4a3": "L406", "nr4a1": "H", "nr4a2": "H", "divergent": True},   # both
    {"nr4a3": "T407", "nr4a1": "L", "nr4a2": "V", "divergent": True},   # both, but splays out
    {"nr4a3": "T410", "nr4a1": "G", "nr4a2": "N", "divergent": True},   # both
    {"nr4a3": "P411", "nr4a1": "P", "nr4a2": "P", "divergent": False},  # conserved
    {"nr4a3": "R412", "nr4a1": "A", "nr4a2": "T", "divergent": True},   # both, but splays out
    {"nr4a3": "R481", "nr4a1": "R", "nr4a2": "R", "divergent": False},  # conserved
    {"nr4a3": "I484", "nr4a1": "Y", "nr4a2": "Y", "divergent": True},   # both
    {"nr4a3": "R485", "nr4a1": "R", "nr4a2": "R", "divergent": False},  # conserved
    {"nr4a3": "I531", "nr4a1": "V", "nr4a2": "I", "divergent": True},   # NR4A1 only (I == NR4A2)
    {"nr4a3": "L534", "nr4a1": "F", "nr4a2": "F", "divergent": True},   # both
]
ENGAGEABLE = {"L406", "T410", "I484", "I531", "L534"}   # handle-facing run: T407/R412 splay out


def test_resnum():
    assert bp._resnum("I531") == 531
    assert bp._resnum("L406") == 406
    assert bp._resnum("xyz") is None


def test_selective_handles_are_divergent_and_engageable():
    out = bp.classify_pocket(POCKET5, ENGAGEABLE)
    sel = {h["residue"] for h in out["selective_handles"]}
    assert sel == {"L406", "T410", "I484", "I531", "L534"}     # the 5 engageable divergent handles
    assert out["summary"]["n_selective_handles"] == 5


def test_splayed_divergent_handles_excluded_from_selective():
    out = bp.classify_pocket(POCKET5, ENGAGEABLE)
    non = {h["residue"] for h in out["divergent_non_engageable"]}
    assert non == {"T407", "R412"}                              # divergent but not engageable


def test_conserved_core():
    out = bp.classify_pocket(POCKET5, ENGAGEABLE)
    core = {h["residue"] for h in out["conserved_core"]}
    assert core == {"P411", "R481", "R485"}
    assert out["summary"]["n_conserved_core"] == 3


def test_paralogue_discrimination_asymmetry():
    out = bp.classify_pocket(POCKET5, ENGAGEABLE)
    by_res = {h["residue"]: h for h in out["selective_handles"]}
    assert by_res["I531"]["discriminates"] == ["NR4A1"]        # I == NR4A2, so NR4A1-only
    assert by_res["I531"]["weight"] == 1
    assert set(by_res["L406"]["discriminates"]) == {"NR4A1", "NR4A2"}
    assert by_res["L406"]["weight"] == 2
    # The recorded asymmetry: 5 engageable vs NR4A1, only 4 vs NR4A2.
    assert out["summary"]["n_discriminate_both"] == 4
    assert out["summary"]["n_discriminate_nr4a1_only"] == 1


def test_both_discriminating_handles_rank_first():
    out = bp.classify_pocket(POCKET5, ENGAGEABLE)
    weights = [h["weight"] for h in out["selective_handles"]]
    assert weights == sorted(weights, reverse=True)            # weight-2 handles precede weight-1
    assert out["selective_handles"][-1]["residue"] == "I531"   # the only weight-1 handle sorts last


def test_engageable_accepts_numeric_or_label():
    out = bp.classify_pocket(POCKET5, {406, 410, 484, 531, 534})
    assert out["summary"]["n_selective_handles"] == 5          # numeric engageable set matches by number


def test_find_pocket():
    sel = {"nr4a3_lbd_pockets": [{"pocket": 5, "residues": POCKET5}, {"pocket": 1, "residues": []}]}
    assert bp.find_pocket(sel, 5)["pocket"] == 5
    assert bp.find_pocket(sel, 99) is None
