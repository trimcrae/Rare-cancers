"""⛔ THE LAB-SUPPLIED LANE MOVED A GATE. THIS IS WHAT STOPS IT FROM REMOVING ONE.

`aso_noncoding_acceptor_designs` emits designs at NR4A3 exon-2 acceptor seams, and until 2026-08-24
it could only reach a seam named in `PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS`. That whitelist is what
lets this repository say every seam it PUBLISHES designs for is one a published report places a
patient at — the guard against designing at a junction nobody has sequenced, which is the class of
error this work's own withdrawn version arose from.

⭐ THE LAB LANE EXISTS BECAUSE THE WHITELIST WAS A PROXY, NOT THE THING ITSELF. A laboratory that has
sequenced its own cells' breakpoint holds better evidence than a report about someone else's, and the
manuscript already requires nucleotide-resolution confirmation in test material before any
oligonucleotide is ordered. Refusing that lab a design enforced the proxy against what it stood for.

⛔ SO THE GATE MOVED FROM "is it published?" TO "is it sequenced, and does the sequence agree?" — and
each of the four things below is a way that move could have become a removal instead. Each test names
the specific bad outcome, because a guard whose failure message says only "assert False" gets deleted
by the next person who trips it.
"""
from __future__ import annotations

import json
import os

import pytest

import aso_noncoding_acceptor_designs as m

#: A seam that IS on the published whitelist, so the tests below isolate the lane's own behaviour
#: rather than incidentally testing whether a transcript model exists.
_SEAM = ("EWSR1", 13, "NR4A3", 2)
_ATTEST = "RT-PCR/Sanger across the seam; lab record 2026-08-24/A"


def _designs(**kw):
    kw.setdefault("sequenced_by", _ATTEST)
    return m.lab_supplied_designs(*_SEAM, **kw)


def test_an_unattested_breakpoint_gets_no_designs():
    """⛔ THE ATTESTATION IS THE WHOLE GATE. Without it this lane is a bypass of the whitelist."""
    for empty in ("", "   ", None):
        with pytest.raises(ValueError, match="sequenced_by is required"):
            m.lab_supplied_designs(*_SEAM, sequenced_by=empty)


def test_the_attestation_travels_with_the_sequences_it_warrants():
    """A design whose only warrant is an attestation must not be separable from that attestation."""
    rec = _designs()
    warrant = rec["⛔_the_warrant_for_these_sequences_is_this_and_nothing_else"]
    assert warrant["sequenced_by"] == _ATTEST
    assert rec["designs"], "the lane returned no designs, so there is nothing to warrant"
    # ⛔ AND IT MUST NOT CLAIM THE SCREENS RAN. Absent from the screened table is unmeasured, and
    # unmeasured is never clean — the distinction this module's own docstring is built on.
    assert all("⚠_offtarget_screens_run" in d for d in rec["designs"])


def test_a_seam_the_caller_reads_differently_is_refused_rather_than_designed():
    """⛔ THE ONE FAILURE THIS LANE CAN ACTUALLY CAUSE: sequences built on the wrong seam.

    A caller numbering exons under the coding-exon convention names a different junction by the same
    label. Emitting designs anyway hands them oligonucleotides that do not span their breakpoint —
    which is this repository's retracted-version defect, reproduced on someone else's material.
    """
    with pytest.raises(ValueError, match="does not match the seam"):
        _designs(observed_junction_mrna="AAAAAAAAAAAA|TTTTTTTTTTTT")


def test_a_seam_the_caller_confirms_is_accepted_however_they_spell_it():
    """A guard that refuses correct input in a different notation gets switched off, not obeyed."""
    seam = _designs()["junction_context_mRNA"]
    for spelling in (seam, seam.replace("|", ""), seam.lower(), seam.replace("T", "U")):
        rec = _designs(observed_junction_mrna=spelling)
        assert rec["⛔_the_warrant_for_these_sequences_is_this_and_nothing_else"][
            "checked_against_the_transcript_models"] is True


def test_a_withdrawn_seam_is_not_reopened_by_a_callers_say_so():
    """⛔ A RETRACTION IS EVIDENCE THIS REPOSITORY WENT AND GOT. An attestation does not overturn it."""
    if not m.RETRACTED_PUBLISHED_BREAKPOINTS:
        pytest.skip("nothing is retracted, so there is nothing to try to reopen")
    donor, d_end, acceptor, a_start = next(iter(m.RETRACTED_PUBLISHED_BREAKPOINTS))
    with pytest.raises(ValueError, match="WITHDRAWN seam"):
        m.lab_supplied_designs(donor, d_end, acceptor, a_start, sequenced_by=_ATTEST)


def test_the_lane_cannot_write_the_published_breakpoint_artifact():
    """⛔ THE COMMITTED ARTIFACT STAYS WHITELIST-ONLY, WHATEVER THE CALLER ASKS FOR."""
    argv = ["--lab-breakpoint", "EWSR1:13::NR4A3:2", "--sequenced-by", _ATTEST,
            "--lab-out", m.OUT]
    with pytest.raises(SystemExit, match="refusing to write"):
        m.main(argv)


def test_the_lane_does_not_add_itself_to_the_whitelist(tmp_path):
    """⛔ A SEAM PASSING THROUGH THIS LANE MUST LEAVE NO TRACE IN THE PUBLISHED SET.

    The whitelist is a module-level dict, so a lane that mutated it would silently promote a
    caller-attested seam into the next `build()` — and from there into the committed artifact, the
    deposit and the paper's claim about its own evidence.
    """
    before = dict(m.PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS)
    out = tmp_path / "lab.json"
    assert m.main(["--lab-breakpoint", "EWSR1:13::NR4A3:2",
                   "--sequenced-by", _ATTEST, "--lab-out", str(out)]) == 0
    assert m.PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS == before
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["_lane"] == "lab-supplied"
    assert os.path.exists(m.OUT), "the published artifact should be untouched, not removed"


def test_the_output_says_what_it_is_not():
    """A record that can be read on its own must carry its own limits, not rely on the module doc."""
    rec = _designs()
    joined = " ".join(rec["⛔_this_is_not"]).upper()
    for must in ("NOT PUBLISHED EVIDENCE", "NOT SCREENED", "NOT A COVERAGE CLAIM"):
        assert must in joined, f"the lab-lane record does not state that it is {must.lower()}"
