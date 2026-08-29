#!/usr/bin/env python3
"""AUT-PROP-051: a panel scored over a tenth of itself must not render like one scored over all of it.

⛔⛔ THE NARROWING, MEASURED. `signature_scores` in the panels artifact already scores each published
set over its FULL readable membership — that half was never narrow. The narrowing is downstream:
`ndrg1_panel_attribution.py` re-derives a per-sample panel score from `gene_reads`, and `gene_reads`
is the union of `PANELS`' hand-curated groups (479 genes). So each published set was correlated
against NDRG1 over `curated ∩ published` — 11 of 49 readable members for the Buffa metagene, 18 of
188 for `pparg_chip_chea`. Roughly a tenth of each panel, wearing the panel's name.

★ WHAT THIS FILE MUST CATCH, and the last one is the reason it exists at all:

  1. `_signature_member_reads` emitting rows that are not positionally aligned to their `gsms`, or
     silently dropping a readable member — the block is a positional encoding, so an off-by-one is
     invisible in the JSON and fatal in the arithmetic.
  2. The decoder mis-reading it, or treating an ABSENT block as an empty one WITHOUT saying so.
     ⛔ THE DECODER IS `signature_member_z`, AND SINCE AUT-PD-167 IT IS NOT `member_z` (AUT-PD-182).
     `member_z` is that decoder PLUS the pin, so under `curated_only` it returns `{}` however well
     the decoding works. A round-trip pointed at it asserts the pin and proves nothing about the
     encoding — which is exactly how the five assertions below went red on `main` and stayed red.
  3. The null's pool failing to grow with the cache. The verdict rests on the size-matched null, so
     a wide membership scored against a narrow null is the worst of both — more signal in the panel,
     the same easy bar to clear.
  4. ⛔ THE TWO READS RENDERING ALIKE. They produce different numbers under the same field names,
     and a reader who cannot tell which one they hold has the worse of both.
     `panel_membership_source` is that tell, and it is asserted here rather than trusted.
     ⛔⛔ THE TELL KEYS OFF THE PIN, NEVER OFF WHETHER THE BLOCK HAPPENED TO BE THERE (AUT-PD-167).
     It once keyed off block presence, which is how a scheduled CI fetch reversed a committed
     verdict with no commit, no gate and no argument. So every test below that varies the read
     holds the block PRESENT in both arms and moves `MEMBERSHIP_SOURCE` instead — varying presence
     would re-assert the inheritance behaviour AUT-PD-167 deleted on purpose.

★ WHAT THIS FILE DELIBERATELY DOES NOT ASSERT, so the pair does not drift again: that the pin
DECLINES a block it can read, and what the COMMITTED artifact's pin is, both belong to
test_the_panel_read_is_pinned_not_inherited.py. These two files are one pair and AUT-PD-182 is
what it cost to leave one half of it behind.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.dirname(HERE)
sys.path.insert(0, MODALITIES)

import ndrg1_panel_attribution as N  # noqa: E402
import emc_expression_panels as P  # noqa: E402

MATRIX = "M1.txt.gz"


def _tgt(gsms, values):
    """A minimal `tgt`: `values` maps gene -> per-sample raw value, background fixed so z == value."""
    n = len(gsms)
    return {
        "platform": "GPL-TEST",
        "n_samples": n,
        "samples": [{"gsm": g} for g in gsms],
        "background_per_sample": [{"mean": 0.0, "sd": 1.0}] * n,
        "genes": {g: {"values": v} for g, v in values.items()},
    }


# ---------------------------------------------------------------- the emitted block

def _block(gsms, values, slots):
    live = {MATRIX: (_tgt(gsms, values), None, None, None)}
    return P._signature_member_reads({"slots": slots}, live)[MATRIX]


def test_every_readable_member_of_every_resolved_set_is_emitted():
    b = _block(["s1", "s2"], {"A": [1.0, 2.0], "B": [3.0, 4.0], "C": [5.0, 6.0]},
               {"set1": {"genes": ["A", "B"]}, "set2": {"genes": ["C"]}})
    assert sorted(b["z"]) == ["A", "B", "C"], "a resolved set's readable member was dropped"
    assert b["n_members_readable"] == 3


def test_a_member_with_no_probe_is_absent_rather_than_zero():
    """⛔ An absent reading is not a reading of absence (CLAUDE.md §4)."""
    b = _block(["s1"], {"A": [1.0]}, {"set1": {"genes": ["A", "NOT_ON_ARRAY"]}})
    assert "NOT_ON_ARRAY" not in b["z"]
    assert b["n_members_requested"] == 2 and b["n_members_readable"] == 1


def test_rows_are_positionally_aligned_to_the_gsms_they_are_read_against():
    """The whole encoding rests on this, and an off-by-one is invisible in the JSON."""
    b = _block(["s1", "s2", "s3"], {"A": [1.0, 2.0, 3.0]}, {"s": {"genes": ["A"]}})
    assert b["gsms"] == ["s1", "s2", "s3"]
    assert b["z"]["A"] == [1.0, 2.0, 3.0]


def test_a_sample_with_no_value_is_a_null_in_the_row_not_a_shortened_row():
    b = _block(["s1", "s2"], {"A": [None, 2.0]}, {"s": {"genes": ["A"]}})
    assert b["z"]["A"] == [None, 2.0], "a dropped null would shift every later sample"


def test_an_unresolved_set_contributes_nothing():
    b = _block(["s1"], {"A": [1.0]}, {"ok": {"genes": ["A"]}, "failed": {"genes": None}})
    assert sorted(b["z"]) == ["A"]


# ---------------------------------------------------------------- the decoder

def test_signature_member_z_round_trips_the_block_it_was_written_from():
    """⛔ THE DECODER IS `signature_member_z`, AND IT IS THE ONE ASSERTED HERE BECAUSE IT IS THE ONE
    THAT ALWAYS DECODES (AUT-PD-182). `member_z` is the decoder PLUS the pin, so under a narrow pin
    it returns `{}` however well the decoding works — pointing a round-trip at it would assert the
    pin and prove nothing about the encoding. That the pin declines a block it CAN read is a
    separate property and lives in test_the_panel_read_is_pinned_not_inherited.py."""
    b = _block(["s1", "s2"], {"A": [1.0, None]}, {"s": {"genes": ["A"]}})
    got = N.signature_member_z({"signature_member_reads": {MATRIX: b}}, MATRIX)
    assert got == {"A": {"s1": 1.0}}, "a null must drop the sample, not impute it"


def test_an_absent_block_decodes_to_empty_rather_than_raising():
    for decode in (N.signature_member_z, N.member_z):
        assert decode({}, MATRIX) == {}
        assert decode({"signature_member_reads": {}}, MATRIX) == {}
        assert decode({"signature_member_reads": {MATRIX: {"gsms": [], "z": {}}}}, MATRIX) == {}


# ---------------------------------------------------------------- the two reads must not look alike

def _src(with_block):
    src = {"gene_reads": {"X": {MATRIX: {"readable": True, "per_sample": [
                {"gsm": "s1", "z_vs_array": 1.0}]}}},
           "signature_scores": {}}
    if with_block:
        src["signature_member_reads"] = {MATRIX: {"gsms": ["s1"], "z": {"A": [1.0]}}}
    return src


def test_the_artifact_says_which_read_produced_it(monkeypatch):
    """⛔ THE TELL KEYS OFF THE PIN, NOT OFF WHETHER THE BLOCK HAPPENED TO BE THERE (AUT-PD-167).
    It used to key off block presence, which is precisely how a scheduled CI fetch reversed a
    committed verdict with no commit and no gate. The block is held PRESENT across both rows below
    so that the only thing varying is the pinned choice."""
    monkeypatch.setattr(N, "_load", lambda: _src(True))
    for pin, expect in (("curated_only", "gene_reads only"),
                        ("curated_plus_signature_members", "gene_reads + signature_member_reads")):
        monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", pin)
        out = N.build(n_draws=1)
        assert out["panel_membership_source"]["source"] == expect
        assert out["panel_membership_source"]["pinned"] == pin
        assert out["panel_membership_source"]["wide_block_present"] is True


def test_the_narrow_source_says_it_is_a_decline_and_not_an_absence(monkeypatch):
    """★ A READ DECLINED ON PURPOSE AND A READ THAT COULD NOT BE TAKEN ARE DIFFERENT FACTS
    (CLAUDE.md §4), and under the narrow pin the artifact must say which one it holds."""
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "curated_only")
    monkeypatch.setattr(N, "_load", lambda: _src(True))
    ms = N.build(n_draws=1)["panel_membership_source"]
    assert "AUT-PD-167" in ms["means"]
    assert "DECLINED" in ms["means"], (
        "the narrow read must state that the wide block was declined, not that it was missing")
    assert "NOT comparable" in ms["not_comparable"], (
        "the two reads differ in the null's pool, so a reader must be told not to compare them")
    assert ms["why_pinned"], "a pin with no recorded argument is a preference"


def test_the_committed_artifact_declares_its_own_source():
    """⚠ Today this is the NARROW read. The assertion is that it SAYS so — not that it is wide."""
    with open(os.path.join(MODALITIES, "ndrg1-panel-attribution.json"), encoding="utf-8") as fh:
        art = json.load(fh)
    assert art["panel_membership_source"]["source"] in (
        "gene_reads only", "gene_reads + signature_member_reads")


# ---------------------------------------------------------------- the null's pool

def _src_pool(with_block, n_wide=6):
    """Subject plus two curated genes; the wide block adds `n_wide` more."""
    gsms = ["s1", "s2", "s3", "s4", "s5", "s6", "s7"]
    def ps(vals):
        return [{"gsm": g, "class": "EMC" if i < 4 else "comparator", "z_vs_array": v}
                for i, (g, v) in enumerate(zip(gsms, vals))]
    gr = {N.SUBJECT: {MATRIX: {"readable": True, "per_sample": ps([1, 2, 3, 4, 5, 6, 7])}},
          "C1": {MATRIX: {"readable": True, "per_sample": ps([2, 1, 4, 3, 6, 5, 7])}},
          "C2": {MATRIX: {"readable": True, "per_sample": ps([7, 6, 5, 4, 3, 2, 1])}}}
    src = {"gene_reads": gr, "signature_scores": {}}
    if with_block:
        src["signature_member_reads"] = {MATRIX: {
            "gsms": gsms,
            "z": {f"W{i}": [float(i + j) for j in range(len(gsms))] for i in range(n_wide)}}}
    return src


def test_the_nulls_pool_grows_with_the_widened_membership(monkeypatch):
    """⛔ A WIDE PANEL SCORED AGAINST A NARROW NULL IS THE WORST OF BOTH — more genes in the panel
    and the same easy bar to clear. Under the first two reads the null's pool IS the scored pool, so
    the pool must move with the read. This is the mutation that would otherwise pass every other
    test in this file.

    ⚠ THE BLOCK IS HELD PRESENT IN BOTH ARMS AND ONLY THE PIN MOVES (AUT-PD-182). Varying block
    presence instead would assert the inheritance behaviour AUT-PD-167 deleted on purpose, and that
    is what left this file red on `main`."""
    monkeypatch.setattr(N, "_load", lambda: _src_pool(True))
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "curated_only")
    narrow = N.build(n_draws=2)["series"][MATRIX]["readable_pool"]
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "curated_plus_signature_members")
    wide = N.build(n_draws=2)["series"][MATRIX]["readable_pool"]
    assert narrow == 2, narrow
    assert wide == 8, f"the wide members never reached the null's pool (got {wide})"


def test_gene_reads_wins_where_both_sources_carry_a_gene(monkeypatch):
    """A widened run must not silently move a number already published from the curated block.

    ⛔⛔ THE ASSERTION IS ON THE VALUES, AND IT USED TO BE ON THE COUNT (AUT-PD-182). `readable_pool`
    is 8 whichever source wins — the SET of genes is the same and only the numbers differ — so the
    count-only version of this test passed a mutation that deleted the precedence entirely. It was
    checking that C1 is not counted twice, which is a weaker claim wearing this one's name."""
    src = _src_pool(True)
    src["signature_member_reads"][MATRIX]["z"]["C1"] = [99.0] * 7
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "curated_plus_signature_members")
    cache = N.scoring_cache(src["gene_reads"], src, MATRIX)
    curated = N.sample_z(src["gene_reads"], "C1", MATRIX)
    assert cache["C1"] == curated, "the wide block overwrote a gene gene_reads already carried"
    assert 99.0 not in cache["C1"].values(), "the wide value reached the scoring cache"
    assert len(cache) == 9, "subject + 2 curated + 6 wide-only, each exactly once"

    monkeypatch.setattr(N, "_load", lambda: src)
    assert N.build(n_draws=2)["series"][MATRIX]["readable_pool"] == 8, "C1 must not be counted twice"
