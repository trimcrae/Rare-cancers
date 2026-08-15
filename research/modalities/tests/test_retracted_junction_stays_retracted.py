"""A junction this repository WITHDREW must not come back as designs, in any artifact.

⛔ WHY THIS IS A TEST AND NOT A COMMENT ON THE RETRACTION RECORD.
`EWSR1_e11__NR4A3_e3` was withdrawn on 2026-08-15 (see
`aso_noncoding_acceptor_designs.RETRACTED_PUBLISHED_BREAKPOINTS` for the verdict and the five
numbering anchors behind it). Removing it from the whitelist stops the DESIGN lane from reaching it,
and `_assert_no_retracted_junction_is_whitelisted()` stops it being re-added there. Neither of those
protects the OTHER direction: a screen artifact generated from the whitelist BEFORE the retraction,
sitting in a working tree, and committed afterwards. That artifact would carry oligo sequences at a
seam this repository has concluded no patient has, with a full screen record behind them making them
look better evidenced than anything else in the lane — which is precisely the shape of the defect the
2026-08-08 retracted-seam sweep was built for, arriving from the opposite side.

⚠ WHAT THIS DELIBERATELY DOES NOT FLAG. A retracted junction may legitimately appear as:
  · a GRADE ROW in an exon-pair atlas or frame audit — those enumerate every arithmetic
    possibility and grading e11 OUT_OF_FRAME is exactly the evidence the retraction rests on;
  · the retraction record itself, wherever it is carried.
So the test looks for DESIGNS (an oligo sequence attached to the junction), not for the string.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.dirname(HERE)
sys.path.insert(0, MODALITIES)

import aso_noncoding_acceptor_designs as nca  # noqa: E402
import junction_aso as ja  # noqa: E402


def _labels():
    return {f"{d}_e{de}__{a}_e{ae}" for (d, de, a, ae) in nca.RETRACTED_PUBLISHED_BREAKPOINTS}


def test_the_retraction_record_is_not_empty_and_names_what_would_reopen_it():
    """A retraction that cannot say what would overturn it is an assertion, not a finding."""
    assert nca.RETRACTED_PUBLISHED_BREAKPOINTS, "the retraction registry is empty"
    for key, rec in nca.RETRACTED_PUBLISHED_BREAKPOINTS.items():
        for field in ("retracted_utc", "verdict", "the_claim_that_was_withdrawn",
                      "what_would_reopen_it", "one_home_for_the_evidence"):
            assert rec.get(field), f"{key} retraction is missing {field!r}"
        # ⭐ THE HONEST RESIDUAL IS MANDATORY. A retraction that states only the evidence FOR itself
        # is the same overclaim as the entry it replaces, in the opposite direction.
        assert any(k.endswith("what_this_does_NOT_establish") for k in rec), (
            f"{key} retraction states no limit on itself")


def test_a_retracted_junction_is_not_on_the_whitelist():
    assert not (set(nca.RETRACTED_PUBLISHED_BREAKPOINTS)
                & set(nca.PUBLISHED_NONCODING_ACCEPTOR_JUNCTIONS))
    nca._assert_no_retracted_junction_is_whitelisted()


def test_opting_in_at_a_retracted_seam_raises_and_NAMES_the_retraction():
    """The refusal must not degrade into the generic 'nobody sequenced this'.

    Those two states are indistinguishable to the guard and completely different to a reader: one
    sends them to find a case report, the other tells them the case report was already read. This is
    the assertion that keeps them apart.
    """
    ews, nr4 = ja.transcript_model("EWSR1"), ja.transcript_model("NR4A3")
    for (d_sym, d_end, a_sym, a_start) in nca.RETRACTED_PUBLISHED_BREAKPOINTS:
        donor = ews if d_sym == "EWSR1" else ja.transcript_model(d_sym)
        acceptor = nr4 if a_sym == "NR4A3" else ja.transcript_model(a_sym)
        j = ja.mrna_junction_generic(donor, acceptor, d_end, a_start)
        with pytest.raises(RuntimeError, match="RETRACTED"):
            ja.published_breakpoint_waiver(d_sym, d_end, a_sym, a_start, j, opt_in=True)


def _designs_in(doc):
    """Every (junction_label, oligo) pair an artifact carries, however it nests them.

    Shape-tolerant on purpose: the ASO lane's artifacts nest designs under `junctions`, under
    `graded_pairs`, under `panels` and at top level, and a checker that knew only one shape would
    pass the artifact that used another.
    """
    found = []

    def walk(node, label):
        if isinstance(node, dict):
            label = node.get("junction_label") or node.get("junction") or label
            for key in ("antisense_5to3", "aso_5to3", "sequence_5to3"):
                if isinstance(node.get(key), str) and label:
                    found.append((label, node[key]))
            for v in node.values():
                walk(v, label)
        elif isinstance(node, list):
            for v in node:
                walk(v, label)

    walk(doc, None)
    return found


def _tracked_lane_artifacts():
    """The lane's artifacts that git actually TRACKS.

    ⛔ TRACKED, NOT ON DISK, AND THE DIFFERENCE IS THE WHOLE POINT OF THE SCOPE. A glob over the
    working tree makes this gate's verdict depend on whatever half-finished JSON another session
    happens to have lying in the checkout — it would fire on a scratch file nobody intends to keep,
    and a gate that cries wolf about untracked scratch is a gate the next session learns to ignore.
    What this test exists to catch is a pre-retraction artifact entering the RECORD, and the moment
    that happens is `git add`. So the scope is the index: the file is invisible here right up to the
    instant it is staged, and red from that instant on.
    """
    import subprocess                                                   # noqa: PLC0415
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--cached", "--", "*.json"],
                             cwd=MODALITIES, capture_output=True, text=True, timeout=60)
    except Exception:                                                   # noqa: BLE001
        return []
    if out.returncode != 0:
        return []
    return sorted(os.path.join(MODALITIES, p) for p in out.stdout.split("\0")
                  if p and "noncoding-acceptor" in p)


@pytest.mark.parametrize("path", _tracked_lane_artifacts())
def test_no_noncoding_acceptor_artifact_carries_designs_at_a_retracted_junction(path):
    """⛔ THE ONE THAT CATCHES A PRE-RETRACTION ARTIFACT COMMITTED AFTERWARDS.

    Scoped to this lane's artifacts because this lane is the only one whose whitelist can reach a
    withdrawn seam at all — the ordinary panel is gated on the atlas grade and never could.

    ⚠ AN EMPTY PARAMETER LIST IS A REAL ANSWER HERE ("this lane has no tracked artifact yet"), and it
    is why `test_the_detector_actually_detects` below exists: without it, a collection that found
    nothing and a scan that found nothing clean would look identical.
    """
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    # the retraction record itself legitimately names the junction; designs never do
    doc.pop("retracted_junctions", None)
    offenders = sorted({lab for lab, _seq in _designs_in(doc) if lab in _labels()})
    assert not offenders, (
        f"{os.path.relpath(path, MODALITIES)} carries designs at RETRACTED junction(s) {offenders}. "
        "Regenerate it from the current whitelist — the seam was withdrawn, so its oligos are "
        "designs against a junction this repository concluded no patient carries. See "
        "aso_noncoding_acceptor_designs.RETRACTED_PUBLISHED_BREAKPOINTS.")


def test_the_detector_actually_detects():
    """⛔ A SCAN THAT CANNOT FIND THE THING IT LOOKS FOR REPORTS CLEAN FOREVER.

    `_designs_in` is shape-tolerant, which is the same as saying it is easy to get silently wrong:
    rename one key and every artifact passes. This feeds it the two nestings the lane actually uses —
    a `junctions[].designs[]` list and a flat `graded_pairs[]` row — with a retracted label on both,
    and requires that they are found. Measured against the real defect this was written for: the
    pre-retraction screen artifacts in the working tree on 2026-08-15 carried EWSR1_e11__NR4A3_e3
    designs in exactly these two shapes, and this detector found them.
    """
    label = sorted(_labels())[0]
    nested = {"junctions": [{"junction_label": label,
                             "designs": [{"antisense_5to3": "GGGCATATCTTAACAA"}]}]}
    flat = {"graded_pairs": [{"junction": label, "antisense_5to3": "GGGCATATCTTAACAA"}]}
    for doc in (nested, flat):
        hits = [lab for lab, _seq in _designs_in(doc) if lab in _labels()]
        assert hits == [label], (doc, hits)
    # and it must NOT fire on a grade row that carries no oligo — that is the atlas's normal content
    grade_row = {"graded_pairs": [{"junction_label": label, "grade": "OUT_OF_FRAME"}]}
    assert not [lab for lab, _s in _designs_in(grade_row) if lab in _labels()]
