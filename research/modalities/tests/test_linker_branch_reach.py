#!/usr/bin/env python3
"""Guards for the two-mechanism reach diagnostic.

WHY THESE ASSERTIONS AND NOT OTHERS. This diagnostic exists because a claim sat in nr4a3-program-map.md for days
saying the blocker was grid resolution at one chain length, and the committed enumeration disagrees with
every clause of it. The tests that matter are therefore the ones that would fail if the diagnosis quietly
drifted BACK toward the comfortable version: that both targets really are built at a shared length (so
"the grid cannot build it" stays refuted), that the k floor is derived from the assembler rather than
remembered, and that the module refuses to re-enumerate.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import linker_branch_reach as BR  # noqa: E402


@pytest.fixture(scope="module")
def rep():
    return BR.build_report()


def test_both_mechanisms_ARE_built_at_a_shared_chain_length(rep):
    """★ THE CLAIM THIS REFUTES. STRATEGY said a chain carrying both 'needs 16, and the segment grid cannot
    build it'. The grid builds BOTH targets, separately, at more than one shared length. If this ever comes
    back empty the old framing was right after all and the verdict below must be re-derived, not kept."""
    shared = rep["chain_lengths_carrying_BOTH_targets_separately"]
    assert shared, "the grid builds both targets at some shared length -- that is the whole refutation"
    assert 16 in shared, "including at n = 16, the length the superseded claim said was unreachable"


def test_no_committed_window_is_the_k_2_to_3_that_was_quoted(rep):
    """The other clause of the superseded claim. No recorded T407 window has k_max <= 3; the real ones are
    wider and the enumerator builds inside them."""
    wed = [v for v in rep["reach_table"].values() if v["target"] == BR.WEDGE_TARGET]
    assert wed, "there are T407 constructs at all"
    assert not [v for v in wed if v["window_k_max"] and max(v["window_k_max"]) <= 3], \
        "a k in [2,3] window would vindicate the superseded reason; none exists"
    for v in wed:
        for k in v["k_built"]:
            assert min(v["window_k_min"]) <= k <= max(v["window_k_max"]), \
                f"{v['target']}@n{v['n_backbone']}: built k={k} outside its own recorded window"


def test_the_k_floor_is_DERIVED_from_the_assembler_not_remembered(rep):
    """k = BRANCH_NODE_ATOMS + SEG2 + tail, so the floor follows from the assembler's own constants and its
    own admissibility guards. A test that hard-coded 6 would pass even if the assembler changed underneath."""
    import nr4a3_linker_design as LD
    f = rep["branch_floor"]
    seg2 = [v["n"] for k, v in LD.LINKER_SEGMENT.items() if not v.get("acyl_only") and v["n"] > 0]
    tail = min(v["tail_atoms"] for v in LD.WARHEAD_HANDLE.values())
    assert f["floor_k"] == LD.BRANCH_NODE_ATOMS + min(seg2) + tail
    assert f["floor_k"] >= LD.BRANCH_NODE_ATOMS + 1, "no grid can go below the branch residue's own 3 atoms + 1"


def test_the_floor_formula_is_independent_of_SEG1_and_of_chain_length():
    """The non-obvious half, and the reason 'make the chain longer' was never going to help: k cancels SEG1
    and n exactly. Asserted against build_smiles itself rather than against the formula's restatement."""
    import nr4a3_linker_design as LD
    ks = {}
    for s1 in ("a2", "a5", "e4"):
        if LD.LINKER_SEGMENT[s1].get("amine_only"):
            continue
        _smi, n, k = LD.build_smiles("crbn", "5amide", s1, "a2", "cyac_me")
        ks[s1] = (n, k)
    assert len({k for _n, k in ks.values()}) == 1, f"k must not depend on SEG1: {ks}"
    assert len({n for n, _k in ks.values()}) > 1, "and the chain lengths really were different"


def test_the_blocker_is_named_as_the_template_not_the_grid(rep):
    v = rep["verdict"]
    assert "TEMPLATE" in v["blocker"].upper() and "ONE PENDANT" in v["blocker"].upper()
    assert any("grid resolution" in s for s in v["not_the_blocker"])


def test_a_two_branch_template_is_constructible_with_the_EXISTING_segments(rep):
    """The actionable half. If the minimum length needed new segments, the fix would be a re-grid after all;
    it does not, so the fix is a template."""
    t = rep["two_pendant_minimum_length"]
    assert t["min_n_with_the_EXISTING_grid"] >= t["min_n_if_1_atom_segments_existed"]
    assert t["min_n_with_the_EXISTING_grid"] <= 20, "it must be inside the enumerated length range to matter"


def test_the_module_re_enumerates_NOTHING(rep):
    """It reads a preregistered enumeration and must not emit into it. A diagnostic that quietly grew a
    two-pendant construct would be the drive-by amendment this repo forbids."""
    assert "_not_done_here" in rep and "PREREGISTERED" in rep["_not_done_here"]
    lib_before = BR.load_library()
    BR.build_report()
    assert len(BR.load_library()) == len(lib_before), "the library must be untouched by running this"
