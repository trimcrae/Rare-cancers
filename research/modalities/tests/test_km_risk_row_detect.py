"""Guards for `km_risk_row_detect.py` -- the numbers-at-risk row detector.

WHAT EACH GUARD CAN FAIL, which is the only property that makes one worth having:

  * the control guard fails if the detector stops separating a synthetic figure that prints a risk
    row from one that does not;
  * each of the four DISCRIMINATION guards is a real defect this detector had, reproduced as a
    synthetic figure -- a misaligned band, a band of wide words, a row of drawn tick marks, and a
    tick row far below what was taken for the axis. Each was found on a real paper in this
    repository's own corpus and each would have produced an INVENTED risk row or a lost figure;
  * the mutation guards fail if the rule stops depending on the thing it claims to depend on:
    remove the alignment and it must not fire, widen the marks and it must not fire;
  * the committed-artifact guards fail if `km-risk-row-detection.json` loses its control block,
    ships a control that did not pass, or reports a verdict outside the closed set;
  * the refusal guard fails if an undecodable figure is ever recorded as a NEGATIVE rather than as
    `undetermined` -- a missing reading is not a reading of absence.

⛔ EVERY FIGURE IN THIS FILE IS SYNTHETIC. Nothing here is a published figure, a patient or a
series, and nothing here may be cited as data. The real-figure readings live in the committed
artifact, whose inputs are named by digest because their licences forbid committing them.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import km_risk_row_detect as krd  # noqa: E402

ARTIFACT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "km-risk-row-detection.json")
VERDICTS = {"present", "absent", "undetermined"}


def _verdict(**kwargs) -> dict:
    img = krd.synthetic_figure(**kwargs)
    axis = krd.find_axis_row(img)
    assert axis is not None, "the synthetic figure draws an axis; not finding one is the bug"
    y, x0, x1 = axis
    toks = krd.pixel_tokens(img, y, x0, x1)
    return krd.decide(toks, max(1, x1 - x0), axis_y=y,
                      max_tick_gap=krd.MAX_TICK_GAP * img.height,
                      max_risk_gap=krd.MAX_RISK_GAP * img.height)


# ---------------------------------------------------------------------------
# the control the module runs on itself
# ---------------------------------------------------------------------------
def test_the_synthetic_control_passes():
    ctl = krd.run_control()
    assert ctl["passed"], ctl["cases"]
    assert len(ctl["cases"]) >= 6


def test_the_control_is_capable_of_failing():
    """A control that cannot fail is decoration. Break the rule and it must go red."""
    saved = krd.MIN_MATCHED_TICKS
    try:
        krd.MIN_MATCHED_TICKS = 0          # alignment no longer required -> a title fires
        assert not krd.run_control()["passed"]
    finally:
        krd.MIN_MATCHED_TICKS = saved
    assert krd.run_control()["passed"]


# ---------------------------------------------------------------------------
# the four discriminations, each a defect measured on a real paper
# ---------------------------------------------------------------------------
def test_a_risk_row_is_detected():
    assert _verdict(risk_row=True)["verdict"] == "present"


def test_a_figure_without_one_is_refused():
    assert _verdict(risk_row=False)["verdict"] == "absent"


def test_an_unaligned_band_is_not_a_risk_row():
    """An axis title is a band of marks below the axis too; only alignment separates them."""
    assert _verdict(risk_row=True, aligned=False)["verdict"] == "absent"


def test_a_band_of_wide_marks_is_not_a_risk_row():
    """A risk row is numbers. Words are wider, and that is the whole discrimination."""
    assert _verdict(risk_row=True, narrow=False)["verdict"] == "absent"


def test_drawn_tick_marks_are_not_read_as_the_tick_labels():
    """masunaga2025 Fig. 3: ticks below the axis made the LABELS look like a risk row."""
    assert _verdict(risk_row=False, tick_marks=True)["verdict"] == "absent"
    assert _verdict(risk_row=True, tick_marks=True)["verdict"] == "present"


def test_tick_labels_far_from_the_axis_are_undetermined_not_negative():
    """martinbroto2020's swimmer plot: a BAR is the bottom-most long horizontal run."""
    res = _verdict(risk_row=False, label_drop=120)
    assert res["verdict"] == "undetermined"
    assert "⚠" in res


def test_an_aligned_band_far_below_the_ticks_is_not_a_risk_row():
    assert _verdict(risk_row=True, risk_drop=260)["verdict"] == "absent"


# ---------------------------------------------------------------------------
# the axis finder
# ---------------------------------------------------------------------------
def test_a_grey_axis_is_still_an_axis():
    """masunaga2025 draws its axis in grey; at the glyph threshold its figures had no axis at all,
    and a figure that never reaches the rule reads afterwards like one nobody had to refuse."""
    img = krd.synthetic_figure(risk_row=False)
    for x in range(100, 861):                       # repaint the axis in mid grey
        for y in range(500, 504):
            img.px[y][x] = (215, 215, 215)
    assert krd.find_axis_row(img) is not None


def test_the_axis_is_taken_from_the_bottom():
    img = krd.synthetic_figure(risk_row=True)
    y, _x0, _x1 = krd.find_axis_row(img)
    assert y > img.height // 2


# ---------------------------------------------------------------------------
# the text arm's own anchor
# ---------------------------------------------------------------------------
def test_an_x_axis_signature_needs_increasing_evenly_spaced_numbers():
    def band(vals, xs):
        return [krd.Token(x, 0, x + 6, 8, str(v)) for v, x in zip(vals, xs)]

    even = band([0, 5, 10, 15], [100, 200, 300, 400])
    assert krd.looks_like_an_x_axis(even, 200)
    assert not krd.looks_like_an_x_axis(band([0, 5, 10, 15], [100, 130, 300, 400]), 200)
    assert not krd.looks_like_an_x_axis(band([0, 5, 3, 15], [100, 200, 300, 400]), 200)
    assert not krd.looks_like_an_x_axis(band(["a", "b", "c", "d"], [100, 200, 300, 400]), 200)
    assert not krd.looks_like_an_x_axis(even, 500)          # too short a span for the page


# ---------------------------------------------------------------------------
# the committed artifact
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not os.path.exists(ARTIFACT), reason="artifact not generated in this checkout")
def test_the_artifact_carries_a_control_and_it_passed():
    doc = json.load(open(ARTIFACT, encoding="utf-8"))
    assert doc["control"]["passed"] is True
    assert doc["control"]["cases"]


@pytest.mark.skipif(not os.path.exists(ARTIFACT), reason="artifact not generated in this checkout")
def test_every_verdict_is_in_the_closed_set_and_every_source_is_digested():
    doc = json.load(open(ARTIFACT, encoding="utf-8"))
    assert doc["sources"], "an empty corpus is not a reading"
    for src in doc["sources"]:
        assert len(src["pdf_sha256"]) == 64
        for fig in src["figures"]:
            assert fig["verdict"] in VERDICTS


@pytest.mark.skipif(not os.path.exists(ARTIFACT), reason="artifact not generated in this checkout")
def test_an_unreadable_figure_is_never_recorded_as_a_negative():
    """The refusal that must not be manufactured: 'we could not read it' is not 'it has none'."""
    doc = json.load(open(ARTIFACT, encoding="utf-8"))
    for src in doc["sources"]:
        for fig in src["figures"]:
            if fig.get("⛔"):
                assert fig["verdict"] == "undetermined", (src["source_id"], fig.get("page"))


@pytest.mark.skipif(not os.path.exists(ARTIFACT), reason="artifact not generated in this checkout")
def test_the_inputs_are_named_well_enough_to_re_derive():
    doc = json.load(open(ARTIFACT, encoding="utf-8"))
    inputs = doc["inputs"]
    assert inputs.get("cache_branch") and inputs.get("cache_path")
    assert inputs.get("cache_commit") and len(inputs["cache_commit"]) == 40
