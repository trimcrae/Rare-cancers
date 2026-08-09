#!/usr/bin/env python3
"""Guards for the PRMT5 substrate-motif map.

⭐ THE ONE THAT MATTERS is `test_the_rg_counts_agree_with_the_artifacts_that_already_own_them`.
This module recomputes, from raw sequence, a quantity two committed artifacts already carry. That
overlap is the whole reason to trust the NEW quantity (GRG), which nothing else computes and
nothing else can check — if the shared half disagrees, the unshared half is worthless.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MOD)

import emc_prmt5_substrate_motif_map as M  # noqa: E402


@pytest.fixture(scope="module")
def res():
    return M.build()


def test_overlapping_occurrences_are_counted(  # a poly-RG tract must not be silently halved
):
    assert M._positions("GRGRG", "GRG") == [1, 3]
    assert M._positions("AAA", "GRG") == []
    assert M._positions("RGRG", "RG") == [1, 3]


def test_the_rg_counts_agree_with_the_artifacts_that_already_own_them(res):
    """⛔ DOUBLE ENTRY. Every RG figure here is recomputed from sequence; `emc-fet-idr-census.json`
    and `emc-fet-construct-designs.json` computed theirs by a different route. A disagreement means
    one counter is wrong and neither may be quoted."""
    for name, w in res["wild_type_proteins"].items():
        assert w["rg_self_check"].startswith("✅"), f"{name}: {w['rg_self_check']}"
    for c in res["measured_comparator_fusions_on_the_same_ruler"]:
        assert c["rg_self_check"].startswith("✅"), f"{c['comparator']}: {c['rg_self_check']}"


def test_the_whole_fusion_count_equals_the_retained_five_prime_half_plus_nr4a3(res):
    """A second, independent identity: the fusion protein's own RG count must equal what the 5'
    partner contributes plus what NR4A3 contributes. It exercises the construct SEQUENCES, which
    the check above never touches."""
    nr4a3 = res["wild_type_proteins"]["NR4A3"]["motif_counts"]
    for f in res["fusion_constructs"]:
        kept = f["five_prime_motif_sites_retained"]
        whole = f["whole_fusion_protein"]["motif_counts"]
        for m in ("GRG", "RG"):
            assert whole[m] == kept[m] + nr4a3[m], (
                f"{f['id']} {m}: fusion carries {whole[m]}, but the retained 5' half has "
                f"{kept[m]} and NR4A3 has {nr4a3[m]}. A junction-spanning site or a wrong "
                f"boundary is the likeliest cause — do not adjust the tolerance.")


def test_no_grg_site_lies_in_ewsr1s_first_300_residues(res):
    """The claim the manuscript makes in one sentence, stated as precisely as the sequence supports.

    ⚠ WRITTEN FIRST AS "entirely C-terminal", AND THE TEST REFUSED IT. EWSR1 is 656 residues and
    the first GRG is at 301 — residue 301 is at 46% of the protein, so "C-terminal half" is false
    by ~27 residues. The true statement is narrower and just as useful: the N-terminal 300 residues
    — the transactivation segment every EWSR1 fusion retains — contain NO site, and all 11 lie
    beyond it. The manuscript must use this wording, not the one that failed here."""
    e = res["wild_type_proteins"]["EWSR1"]
    assert min(e["positions"]["GRG"]) == 301
    assert not [p for p in e["positions"]["GRG"] if p <= 300]


def test_the_commonest_emc_fusion_and_the_commonest_clear_cell_fusion_match_on_the_motif(res):
    """⭐ THE TRANSFER THE MANUSCRIPT RESTS ON, ASSERTED. If a future breakpoint correction moves
    either one, the paper's central quantitative claim has changed and this test is where that
    surfaces — not in a reader's spot-check."""
    emc = next(f for f in res["fusion_constructs"] if f["id"] == "EWSR1_NR4A3_type1")
    ccs = next(c for c in res["measured_comparator_fusions_on_the_same_ruler"]
               if "commonest type" in (c["comparator"] or ""))
    assert emc["five_prime_motif_sites_retained"]["GRG"] == \
        ccs["five_prime_motif_sites_retained"]["GRG"]


def test_the_motif_is_not_presented_as_necessary(res):
    """⛔ THE HONESTY GUARD. EWSR1::FLI1 retains zero sites and PRMT5 inhibition still acts in a
    fusion-dependent way there, so the artifact must carry that limit in its own text. A future
    edit that quietly drops it turns a falsifiable prediction into a claim."""
    limits = " ".join(res["⛔_the_limits"])
    assert "NOT NECESSARY" in limits and "40823091" in limits
    fli1 = next(c for c in res["measured_comparator_fusions_on_the_same_ruler"]
                if "FLI1" in (c["comparator"] or ""))
    assert fli1["five_prime_motif_sites_retained"]["GRG"] == 0


def test_no_efficacy_language(res):
    blob = json.dumps(res, ensure_ascii=False).lower()
    for banned in ("is effective", "will respond", "therapeutic window in", "safe in patients"):
        assert banned not in blob
