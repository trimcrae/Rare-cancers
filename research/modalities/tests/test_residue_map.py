"""Tests for residue_map.resolve_positions — both numbering schemes, incl. the renumbered-from-1 case
that silently matched zero residues in the first SASA run."""
import residue_map as rm

LBD_FIRST = 373
# The LBD trimmed contiguously from 373: 254 residues numbered 373..626 (preserved) or 1..254 (renumbered).
PRESERVED = list(range(373, 627))
RENUMBERED = list(range(1, 255))
TARGETS = [406, 407, 410, 412, 484, 531, 534]   # the selectivity handles, AF2 numbering


def test_preserved_numbering():
    pos, label = rm.resolve_positions(PRESERVED, TARGETS, LBD_FIRST)
    assert label == "resSeq-preserved"
    # original residue r is at ordinal r-373 in the contiguous LBD
    assert pos == [r - 373 for r in TARGETS]


def test_renumbered_from_one():
    pos, label = rm.resolve_positions(RENUMBERED, TARGETS, LBD_FIRST)
    assert label.startswith("renumbered-from-373")
    # same physical residues, recovered by position despite resSeq being 1..254
    assert pos == [r - 373 for r in TARGETS]


def test_both_schemes_select_same_residues():
    pos_pre, _ = rm.resolve_positions(PRESERVED, TARGETS, LBD_FIRST)
    pos_re, _ = rm.resolve_positions(RENUMBERED, TARGETS, LBD_FIRST)
    assert pos_pre == pos_re == [r - 373 for r in TARGETS]
    assert len(pos_pre) == len(TARGETS)   # all targets matched (the zero-match bug would fail here)


def test_empty_and_no_targets():
    assert rm.resolve_positions([], TARGETS, LBD_FIRST) == ([], "empty")
    assert rm.resolve_positions(PRESERVED, [], LBD_FIRST) == ([], "no-targets")
