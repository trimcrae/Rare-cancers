#!/usr/bin/env python3
"""The acceptor guard must still refuse a coordinate slip, and must admit a published breakpoint.

⛔ WHAT IS BEING PROTECTED. `junction_aso.build_parents_and_fusion` raises on a non-coding acceptor
and calls it "Defect 1, and it is what produced the retracted seam": code once slid onto a
neighbouring exon and designed against a seam no patient has. The guard sees an EXON INDEX and
nothing else, so it cannot tell

    (a) a coordinate slip onto NR4A3 exon 2 when exon 3 was meant, from
    (b) a patient whose transcript genuinely joins NR4A3 exon 2 — the *EWSR1* type 2 transcript,
        placed in sequenced patients by three independent reports.

The waiver added 2026-08-15 admits (b) without admitting (a), by requiring TWO independent things:
an explicit caller intention (`PUBLISHED_BREAKPOINT_JUNCTION`) and membership of the curated
published-breakpoint whitelist. Every test below is one leg of that claim. ⚠ If the waiver is ever
loosened so that either half alone opens the guard, these fail — which is the point: the guard's
value is entirely in what it REFUSES, and a refusal nobody exercises is a hope.

⚠ NO MOCKS. Every case builds the real junction from the committed Ensembl transcript cache.
"""
from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.dirname(HERE)
sys.path.insert(0, MODALITIES)

os.environ.setdefault("TRANSCRIPT_SOURCE", "cache")

import junction_aso as ja  # noqa: E402

#: The junction this whole lane exists for, and the one the whitelist must carry.
TYPE2 = ("EWSR1", 7, "NR4A3", 2)

_ENV = ("DONOR_GENE", "EWSR1_EXON_END", "DONOR_EXON_END", "NR4A3_EXON_START",
        "PUBLISHED_BREAKPOINT_JUNCTION", "FUSION_JUNCTION_MODE")


def _build(donor_exon, acceptor_exon, published=False, donor="EWSR1"):
    """Run the real builder at one exon pair and return its `LAST_JUNCTION`, or raise."""
    saved = {k: os.environ.get(k) for k in _ENV}
    try:
        for k in _ENV:
            os.environ.pop(k, None)
        os.environ["FUSION_JUNCTION_MODE"] = "real"
        os.environ["DONOR_GENE"] = donor
        os.environ["EWSR1_EXON_END" if donor == "EWSR1" else "DONOR_EXON_END"] = str(donor_exon)
        os.environ["NR4A3_EXON_START"] = str(acceptor_exon)
        if published:
            os.environ["PUBLISHED_BREAKPOINT_JUNCTION"] = "1"
        ja.build_parents_and_fusion()
        return ja.LAST_JUNCTION
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_the_type_2_junction_is_on_the_whitelist_and_is_a_non_coding_acceptor():
    """The premise of every other test here, asserted rather than assumed."""
    wl = ja.published_noncoding_acceptor_junctions()
    assert TYPE2 in wl, sorted(wl)
    assert wl[TYPE2]["excluded_from_the_panel_by"] == "NON_CODING_ACCEPTOR"
    assert wl[TYPE2]["n_independent_sources"] >= 2, "a whitelist of one anecdote is not a whitelist"


def test_the_guard_still_refuses_the_coordinate_slip_it_was_built_for():
    """⛔ THE CENTRAL CASE. Without the flag, exon 2 is refused exactly as before the waiver existed
    — including at a junction that IS on the whitelist, because a slip and a real breakpoint are
    identical by exon index and only the caller can say which it meant."""
    with pytest.raises(RuntimeError, match="carries no coding sequence"):
        _build(7, 2)


def test_the_flag_alone_does_not_open_the_guard():
    """Intention without evidence is refused: the flag admits a NAMED seam, it does not create one."""
    with pytest.raises(RuntimeError, match="NOT on the published-breakpoint whitelist"):
        _build(12, 2, published=True)


def test_a_published_breakpoint_is_admitted_and_the_artifact_says_so():
    j = _build(TYPE2[1], TYPE2[3], published=True)
    assert j["junction_label"] == "EWSR1_e7__NR4A3_e2"
    assert j["nr4a3_acceptor_exon_is_coding"] is False
    w = j.get("⛔_published_breakpoint_waiver")
    assert w, "a waived junction must carry its waiver, or the artifact is exceptional and hides it"
    assert w["waived_grade"] == "NON_CODING_ACCEPTOR"
    assert w["n_independent_sources"] >= 2 and w["evidence"]


def test_SEAM_NOT_PRODUCED_is_not_waivable_even_with_the_flag():
    """⛔ THE ONE GRADE NO CITATION CAN WAIVE. NR4A3 exon 4 resumes the protein outside the corrected
    plausible range — the retraction's own grade. It is not on the whitelist, and the refusal must
    name the whitelist rather than silently degrade into a frame complaint."""
    with pytest.raises(RuntimeError, match="NOT on the published-breakpoint whitelist"):
        _build(7, 4, published=True)
    assert "SEAM_NOT_PRODUCED" not in ja.WAIVABLE_PUBLISHED_GRADES


def test_the_canonical_panel_junction_is_untouched_by_all_of_this():
    """Every existing caller must be bit-for-bit unaffected: no flag, no waiver, same seam."""
    j = _build(12, 3)
    assert j["junction_label"] == "EWSR1_e12__NR4A3_e3"
    assert j["in_frame"] is True
    assert "⛔_published_breakpoint_waiver" not in j


def test_the_flag_on_an_emittable_junction_is_a_refusal_not_a_silent_pass():
    """A junction that belongs in the ordinary panel must not be reachable through this door."""
    with pytest.raises(RuntimeError, match="NOT on the published-breakpoint whitelist"):
        _build(12, 3, published=True)


def test_a_whitelist_entry_whose_stated_grade_is_wrong_raises(monkeypatch):
    """⛔ THE GRADE IS ASSERTED, NEVER ASSUMED. Without this, the whitelist would become a general
    bypass the moment someone added a tuple with a plausible-sounding reason beside it."""
    import aso_noncoding_acceptor_designs as nca  # noqa: PLC0415

    wrong = dict(nca.PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS)
    wrong[TYPE2] = {**wrong[TYPE2], "excluded_from_the_panel_by": "OUT_OF_FRAME"}
    monkeypatch.setattr(nca, "PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS", wrong)
    with pytest.raises(RuntimeError, match="whitelisted as OUT_OF_FRAME"):
        _build(7, 2, published=True)


def test_the_seam_sweep_calls_the_published_acceptor_correct_rather_than_ungradeable():
    """⛔ WHY THIS IS NOT COSMETIC. `junction_seam_retraction.--check` treats UNGRADEABLE as a
    failure, and the CI publish that owns `modalities-cache` runs it as a hard gate. If the type 2
    acceptor seam were in neither reference set, every artifact of this junction would block that
    publish — a data-integrity guard converted into an outage against a real seam."""
    import junction_seam_retraction as JSR  # noqa: PLC0415

    correct = JSR.correct_acceptor_seams()
    assert 2 in correct, correct
    seam = _build(7, 2, published=True)["junction_context_mRNA"]
    assert seam.split("|")[1] == correct[2]
    doc = {"_breakpoint_model": {"mode": "real_exon_junction_mRNA",
                                 "junction_context_mRNA": seam}}
    assert JSR.grade(doc)[0] == JSR.GRADE_CORRECT
    # and the two reference sets must stay disjoint, or a seam could be graded either way
    assert set(correct.values()).isdisjoint(set(JSR.retracted_acceptor_seams().values()))
