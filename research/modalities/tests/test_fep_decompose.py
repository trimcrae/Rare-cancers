import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import fep_decompose as fd  # noqa: E402


def _maps():
    # NR4A3 strongly stabilized at 410 (a handle) and 484; a paralogue residue 600 erodes selectivity.
    return {
        "nr4a3": {406: -1.0, 410: -3.0, 484: -2.0, 531: -1.5, 600: -0.5},
        "nr4a1": {406: -0.9, 410: -0.5, 484: -1.8, 531: -1.4, 600: -3.0},   # 600 favors NR4A1 (eroder); 410 favors NR4A3
        "nr4a2": {406: -1.0, 410: -2.8, 484: -2.1, 531: -1.5, 600: -0.4},   # ~matched -> selectivity-clean vs NR4A2
    }


def test_attribution_drivers_and_eroders():
    a = fd.selectivity_attribution(_maps())
    # vs NR4A1: 410 is a driver (Δ = -3.0 - (-0.5) = -2.5), 600 is an eroder (Δ = -0.5 - (-3.0) = +2.5)
    n1 = a["nr4a1"]
    assert n1["drivers"][0]["resid"] == 410 and n1["drivers"][0]["delta"] < 0
    assert n1["eroders"][0]["resid"] == 600 and n1["eroders"][0]["delta"] > 0
    assert n1["drivers"][0]["handle"] == "T410"          # handle annotation present


def test_attribution_clean_paralogue_has_small_net():
    a = fd.selectivity_attribution(_maps())
    assert abs(a["nr4a2"]["net_delta"]) < abs(a["nr4a1"]["net_delta"])   # NR4A2 better matched


def test_redesign_hint_names_the_culprit():
    hint = fd.redesign_hint(fd.selectivity_attribution(_maps()))
    assert "600" in hint["nr4a1"]                        # names the eroding residue
    assert "T410" in hint["nr4a1"] or "410" in hint["nr4a1"]


def test_diagnostic_ready_gate():
    good = _maps()
    assert fd.diagnostic_ready(good) is True
    # missing NR4A2 map -> not ready (must not stop-fail yet)
    assert fd.diagnostic_ready({"nr4a3": good["nr4a3"], "nr4a1": good["nr4a1"]}) is False
    # too few residues -> not ready
    assert fd.diagnostic_ready({"nr4a3": {1: -1}, "nr4a1": {1: -1}, "nr4a2": {1: -1}}) is False


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
