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
  2. `member_z` mis-decoding it, or treating an ABSENT block as an empty one WITHOUT saying so.
  3. The null's pool failing to grow with the cache. The verdict rests on the size-matched null, so
     a wide membership scored against a narrow null is the worst of both — more signal in the panel,
     the same easy bar to clear.
  4. ⛔ THE TWO READS RENDERING ALIKE. They produce different numbers under the same field names.
     Until a `panels` dispatch lands the block, this repository holds the NARROW read, and a reader
     who cannot tell which one they have has the worse of both. `panel_membership_source` is that
     tell, and it is asserted here rather than trusted.
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

def test_member_z_round_trips_the_block_it_was_written_from():
    b = _block(["s1", "s2"], {"A": [1.0, None]}, {"s": {"genes": ["A"]}})
    got = N.member_z({"signature_member_reads": {MATRIX: b}}, MATRIX)
    assert got == {"A": {"s1": 1.0}}, "a null must drop the sample, not impute it"


def test_an_absent_block_decodes_to_empty_rather_than_raising():
    assert N.member_z({}, MATRIX) == {}
    assert N.member_z({"signature_member_reads": {}}, MATRIX) == {}
    assert N.member_z({"signature_member_reads": {MATRIX: {"gsms": [], "z": {}}}}, MATRIX) == {}


# ---------------------------------------------------------------- the two reads must not look alike

def _src(with_block):
    src = {"gene_reads": {"X": {MATRIX: {"readable": True, "per_sample": [
                {"gsm": "s1", "z_vs_array": 1.0}]}}},
           "signature_scores": {}}
    if with_block:
        src["signature_member_reads"] = {MATRIX: {"gsms": ["s1"], "z": {"A": [1.0]}}}
    return src


def test_the_artifact_says_which_read_produced_it(monkeypatch):
    for with_block, expect in ((False, "gene_reads only"), (True, "gene_reads + signature_member_reads")):
        monkeypatch.setattr(N, "_load", lambda w=with_block: _src(w))
        out = N.build(n_draws=1)
        assert out["panel_membership_source"]["source"] == expect


def test_the_narrow_source_says_it_is_the_one_this_item_exists_to_replace(monkeypatch):
    monkeypatch.setattr(N, "_load", lambda: _src(False))
    means = N.build(n_draws=1)["panel_membership_source"]["means"]
    assert "AUT-PROP-051" in means
    assert "NOT comparable" in means, (
        "the two reads differ in the null's pool, so a reader must be told not to compare them")


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
    and the same easy bar to clear. The verdict rests entirely on the null, so the pool it is drawn
    from must widen with the cache. This is the mutation that would otherwise pass every other test
    in this file."""
    monkeypatch.setattr(N, "_load", lambda: _src_pool(False))
    narrow = N.build(n_draws=2)["series"][MATRIX]["readable_pool"]
    monkeypatch.setattr(N, "_load", lambda: _src_pool(True))
    wide = N.build(n_draws=2)["series"][MATRIX]["readable_pool"]
    assert narrow == 2, narrow
    assert wide == 8, f"the wide members never reached the null's pool (got {wide})"


def test_gene_reads_wins_where_both_sources_carry_a_gene(monkeypatch):
    """A widened run must not silently move a number already published from the curated block."""
    src = _src_pool(True)
    src["signature_member_reads"][MATRIX]["z"]["C1"] = [99.0] * 7
    monkeypatch.setattr(N, "_load", lambda: src)
    out = N.build(n_draws=2)
    assert out["series"][MATRIX]["readable_pool"] == 8, "C1 must not be counted twice"
