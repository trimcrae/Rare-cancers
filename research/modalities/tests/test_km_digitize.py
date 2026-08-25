"""Guards for `km_digitize.py` -- the raster Kaplan-Meier reader.

WHAT EACH GUARD CAN FAIL, which is the only property that makes one worth having:

  * the round-trip guard fails if the PNG codec loses a pixel;
  * the reading guard fails if the reader's error against a KNOWN cohort exceeds a stated bound --
    and it is shown capable of failing by feeding the SAME image a calibration that is wrong by ten
    pixels, which must blow the bound;
  * each refusal guard is paired with its NEGATIVE case, because a function that refuses everything
    passes every refusal test. Two black curves refuse; two coloured curves must NOT;
  * the censor-tick guard fails if a mark drawn ON the curve is read as an event -- the specific
    defect that produced 393 monotonicity corrections on the first implementation;
  * the floor-quote guard fails if this module's copy of the admissibility floor drifts from
    `emc_ipd_survival`, which owns it;
  * the `--check` guard perturbs the REAL committed artifact and asserts the REAL check refuses it
    AND writes nothing. Mocking the seam there would test the mock (CLAUDE.md §6).

⛔ EVERY COHORT IN THIS FILE IS SYNTHETIC ARITHMETIC. None of it is a patient, a series or a
published figure, and nothing here may be cited as data.
"""

from __future__ import annotations

import importlib
import json
import os
import shutil
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import emc_ipd_survival as ipd_mod  # noqa: E402
import km_digitize as kd  # noqa: E402


def _truth():
    cohort = kd._emc_shaped_cohort()
    km = ipd_mod.kaplan_meier(cohort)
    return cohort, [(r["time"], r["survival"]) for r in km]


# ---------------------------------------------------------------------------
# the codec
# ---------------------------------------------------------------------------
def test_png_roundtrip_is_lossless(tmp_path):
    img = kd.Image.blank(37, 23)
    for y in range(23):
        for x in range(37):
            img.px[y][x] = ((x * 7) % 256, (y * 11) % 256, (x * y) % 256)
    path = str(tmp_path / "rt.png")
    kd.write_png(path, img)
    back = kd.read_png(path)
    assert (back.width, back.height) == (37, 23)
    assert back.px == img.px


def test_read_png_refuses_a_truncated_file(tmp_path):
    path = str(tmp_path / "bad.png")
    with open(path, "wb") as fh:
        fh.write(b"not a png at all")
    with pytest.raises(ValueError):
        kd.read_png(path)


# ---------------------------------------------------------------------------
# the reading, against a cohort the reader never sees
# ---------------------------------------------------------------------------
def test_reads_a_rendered_curve_within_a_stated_bound():
    _cohort, steps = _truth()
    fig = kd.render_km(steps, t_max=180.0)
    read = kd.extract_series(fig.img, fig.calib, kd.dark_matcher(), series_label="t")
    assert read["ok"], read.get("refusal")
    err = kd.curve_error(read["digitized"], steps, 180.0)
    # The OFF-STEP error is the reader's vertical accuracy with time quantisation removed. The
    # whole-curve max is dominated by a one-column timing error at a dense cluster of events and is
    # bounded by the figure's resolution rather than by the reader -- see cohort_size_sensitivity.
    assert err["max_abs_curve_error_off_step"] < 0.01, err
    assert err["max_abs_curve_error"] < ipd_mod.MAX_KM_DEVIATION * 2, err


def test_the_reading_bound_is_capable_of_failing():
    """The same pixels, a calibration wrong by ten pixels: the bound must blow."""
    _cohort, steps = _truth()
    fig = kd.render_km(steps, t_max=180.0)
    bad = kd.Calibration(
        x_pix=(fig.calib.x_pix[0], fig.calib.x_pix[1]), x_val=fig.calib.x_val,
        y_pix=(fig.calib.y_pix[0] - 40, fig.calib.y_pix[1] - 40), y_val=fig.calib.y_val,
        box=fig.calib.box)
    read = kd.extract_series(fig.img, bad, kd.dark_matcher(), min_start_survival=None,
                             series_label="t")
    assert read["ok"]
    err = kd.curve_error(read["digitized"], steps, 180.0)
    assert err["max_abs_curve_error_off_step"] > 0.05, err


def test_events_are_recovered_exactly_from_a_clean_render():
    cohort, steps = _truth()
    risk_times = [0.0, 24.0, 48.0, 72.0, 96.0, 120.0, 144.0, 168.0]
    risk_table = [[t, sum(1 for r in cohort if r["time"] >= t)] for t in risk_times]
    fig = kd.render_km(steps, t_max=180.0)
    read = kd.extract_series(fig.img, fig.calib, kd.dark_matcher(), series_label="t")
    rec = ipd_mod.reconstruct({
        "id": "t", "source_id": "control", "endpoint": "os", "population": "p",
        "time_unit": "months", "digitized": read["digitized"], "risk_table": risk_table,
        "total_events": None, "digitized_by": "test"})
    assert rec["n_events"] == sum(1 for r in cohort if r["event"])


# ---------------------------------------------------------------------------
# the refusals -- each paired with the case it must NOT refuse
# ---------------------------------------------------------------------------
def test_two_black_curves_are_refused_but_two_coloured_curves_are_not():
    _cohort, steps = _truth()
    second = [(t, s * 0.8) for t, s in steps]

    same = kd.render_km(steps, t_max=180.0, second_curve=second, second_rgb=(0, 0, 0))
    read_same = kd.extract_series(same.img, same.calib, kd.dark_matcher(), series_label="same")
    assert read_same["ok"] is False
    assert read_same["refusal"] == "two_black_curves"

    diff = kd.render_km(steps, t_max=180.0, second_curve=second, second_rgb=(200, 30, 30))
    read_diff = kd.extract_series(diff.img, diff.calib, kd.dark_matcher(), series_label="diff")
    assert read_diff["ok"] is True, read_diff.get("refusal")


def test_an_occluding_block_is_refused_but_the_same_figure_without_it_is_read():
    _cohort, steps = _truth()
    fig = kd.render_km(steps, t_max=180.0)
    clean = kd.extract_series(fig.img, fig.calib, kd.dark_matcher(), series_label="clean")
    assert clean["ok"] is True

    x0, y0, x1, y1 = fig.calib.box
    blocked = fig.img.copy()
    for y in range(y0, y1 + 1):
        for x in range(x0 + 200, x0 + 260):
            blocked.px[y][x] = (255, 255, 255)
    read = kd.extract_series(blocked, fig.calib, kd.dark_matcher(), series_label="blocked")
    assert read["ok"] is False
    assert read["refusal"] == "gap"


def test_a_reading_that_does_not_start_at_one_is_refused():
    _cohort, steps = _truth()
    fig = kd.render_km(steps, t_max=180.0)
    # A calibration that claims the top of the box is S = 0.3 makes every reading start low.
    wrong = kd.Calibration(x_pix=fig.calib.x_pix, x_val=fig.calib.x_val,
                           y_pix=fig.calib.y_pix, y_val=(0.0, 0.3), box=fig.calib.box)
    read = kd.extract_series(fig.img, wrong, kd.dark_matcher(), series_label="low")
    assert read["ok"] is False
    assert read["refusal"] == "does_not_start_at_one"
    # ...and the SAME calibration is accepted when the caller declares a landmark plot.
    read2 = kd.extract_series(fig.img, wrong, kd.dark_matcher(), min_start_survival=None,
                              series_label="low")
    assert read2["ok"] is True


def test_a_censoring_tick_is_not_read_as_an_event():
    """The tick straddles the curve; a drop only ever goes down. Direction is the discriminator."""
    cohort, steps = _truth()
    censor_times = sorted(r["time"] for r in cohort if not r["event"])
    plain = kd.render_km(steps, t_max=180.0)
    ticked = kd.render_km(steps, t_max=180.0, censor_times=censor_times)
    a = kd.extract_series(plain.img, plain.calib, kd.dark_matcher(), series_label="plain")
    b = kd.extract_series(ticked.img, ticked.calib, kd.dark_matcher(), series_label="ticked")
    assert a["ok"] and b["ok"]
    assert b["diagnostics"]["monotonicity_fixes"] <= 2, b["diagnostics"]
    assert b["digitized"] == a["digitized"]


# ---------------------------------------------------------------------------
# one fact, one place
# ---------------------------------------------------------------------------
def test_the_quoted_floor_matches_the_module_that_owns_it():
    assert kd.FLOOR_MAX_ABS_KM_DEVIATION == ipd_mod.MAX_KM_DEVIATION


def test_the_floor_quote_assertion_can_actually_fire(monkeypatch):
    monkeypatch.setattr(ipd_mod, "MAX_KM_DEVIATION", 0.123456)
    with pytest.raises(AssertionError):
        kd._assert_floor_matches_the_reconstructor()


# ---------------------------------------------------------------------------
# the artifact guard, exercised against the real file and the real entry point
# ---------------------------------------------------------------------------
@pytest.mark.committed_artifact
def test_check_refuses_a_perturbed_artifact_and_writes_nothing(tmp_path):
    if not os.path.exists(kd.OUT):
        pytest.skip("artifact not built in this checkout")
    backup = str(tmp_path / "backup.json")
    shutil.copy(kd.OUT, backup)
    try:
        with open(kd.OUT, encoding="utf-8") as fh:
            doc = json.load(fh)
        doc["control"]["summary"]["worst_max_abs_curve_error"] = 999.0
        with open(kd.OUT, "w", encoding="utf-8") as fh:
            json.dump(doc, fh)
        before = os.path.getmtime(kd.OUT)
        assert kd.main(["--check"]) == 1
        with open(kd.OUT, encoding="utf-8") as fh:
            after_doc = json.load(fh)
        assert after_doc["control"]["summary"]["worst_max_abs_curve_error"] == 999.0
        assert os.path.getmtime(kd.OUT) == before
    finally:
        shutil.copy(backup, kd.OUT)


def test_module_imports_cleanly_twice():
    """The floor assertion runs at import; a reload must not leave a half-imported module."""
    importlib.reload(kd)


# ---------------------------------------------------------------------------
# the swimmer-plot reader, against patients it never sees
# ---------------------------------------------------------------------------
def _swimmer_truth():
    """SYNTHETIC. Not a patient, not a trial, not a figure anyone published."""
    pal = {"alpha": (47, 85, 151), "beta": (0, 176, 240), "gamma": (255, 0, 0)}
    bars = [
        {"histology": "beta", "months": 23.2, "censored": True, "responded": True},
        {"histology": "alpha", "months": 19.3, "censored": True},
        {"histology": "gamma", "months": 16.6, "censored": False, "responded": True},
        {"histology": "alpha", "months": 15.5, "censored": False, "responded": True},
        {"histology": "beta", "months": 11.6, "censored": True},
        {"histology": "alpha", "months": 7.4, "censored": False},
        {"histology": "gamma", "months": 5.2, "censored": False},
        {"histology": "beta", "months": 3.1, "censored": False},
        {"histology": "alpha", "months": 1.4, "censored": False},
    ]
    return pal, bars


def _swimmer_recipe(pal, tmp_path):
    return {
        "id": "control_swimmer", "source_id": "control", "figure": "synthetic",
        "endpoint": "pfs", "time_unit": "months",
        "x_zero_px": 120.0, "px_per_month": 30.0,
        "scan_box": [100, 20, 1000, 400],
        "bridge_px": 14, "arrow_min_run_px": 15,
        "palette": {k: list(v) for k, v in pal.items()},
        "subgroup_of_interest": "alpha",
        "external_checks": {},
        "read_by": "test",
    }


def test_swimmer_reader_recovers_bars_it_never_saw(tmp_path):
    pal, bars = _swimmer_truth()
    img = kd.render_swimmer(bars, pal, median_line_at=7.4)
    path = str(tmp_path / "swim.png")
    kd.write_png(path, img)
    recipe = _swimmer_recipe(pal, tmp_path)
    recipe["scan_box"] = [100, 20, img.width - 5, img.height - 20]
    out = kd.read_swimmer_plot(recipe, path)
    assert out["n_patients"] == len(bars), out["n_patients"]
    read = sorted((p["histology"], round(p["months"], 1), p["censored"]) for p in out["patients"])
    want = sorted((b["histology"], b["months"], bool(b.get("censored"))) for b in bars)
    assert read == want, (read, want)


def test_the_dashed_median_line_does_not_truncate_a_bar(tmp_path):
    """Without the bridge, every bar crossing the median line reports the LINE's position."""
    pal, bars = _swimmer_truth()
    img = kd.render_swimmer(bars, pal, median_line_at=7.4)
    path = str(tmp_path / "swim.png")
    kd.write_png(path, img)
    recipe = _swimmer_recipe(pal, tmp_path)
    recipe["scan_box"] = [100, 20, img.width - 5, img.height - 20]
    ok = kd.read_swimmer_plot(recipe, path)
    assert max(p["months"] for p in ok["patients"]) > 20

    recipe["bridge_px"] = 0
    broken = kd.read_swimmer_plot(recipe, path)
    truncated = [p for p in broken["patients"] if abs(p["months"] - 7.4) < 0.3]
    assert len(truncated) > 2, "the bridge guard is untested: nothing was truncated without it"


def test_a_response_star_is_not_read_as_a_censoring_arrow(tmp_path):
    """The 12-13 px glyph cluster must stay below the arrow threshold; 45-48 px must clear it."""
    pal, bars = _swimmer_truth()
    img = kd.render_swimmer(bars, pal)
    path = str(tmp_path / "swim.png")
    kd.write_png(path, img)
    recipe = _swimmer_recipe(pal, tmp_path)
    recipe["scan_box"] = [100, 20, img.width - 5, img.height - 20]
    out = kd.read_swimmer_plot(recipe, path)
    starred_not_censored = [b for b in bars if b.get("responded") and not b.get("censored")]
    assert starred_not_censored, "the control has no bar that is starred but not censored"
    for b in starred_not_censored:
        got = next(p for p in out["patients"] if abs(p["months"] - b["months"]) < 0.3)
        assert got["censored"] is False, got


def test_the_committed_swimmer_reading_passed_every_external_check():
    """⚠ A committed-artifact test: its source image is CC BY-NC and cannot live in this repo, so
    the three checks the paper itself supplies are the only evidence the reading is right."""
    path = kd.SWIMMER_OUT
    if not os.path.exists(path):
        pytest.skip("no swimmer reading in this checkout")
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    reading = doc["reading"]
    assert reading["all_external_checks_pass"], reading["external_checks"]
    assert doc["recipe"]["image_committed"] is False
    assert doc["recipe"]["regenerate"]["pdf_url"]
