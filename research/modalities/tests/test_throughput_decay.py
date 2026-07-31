"""THE APPARENT THROUGHPUT DECAY IS COMPOSITION, NOT DEGRADATION — and the tests say what would change that.

Measured `s/iter` on the 5a-KS legs looked like it degraded ~2.5-4x across the day. If real that would have
been worth more than every other fix on this lane combined, so it was tested rather than acted on.

⛔ PHASE IS REFUTED TWICE, and neither refutation needed a new run — the point the repo's own `_never_pool`
note anticipated (*"pricing.md's superseded ~2.06x card ratio was a warmup/production mix-up"*):
  (a) `phase_cross_check` measures warmup/production = 0.834 (range 0.734-1.013, n=6). Warmup is FASTER, so
      a warmup->production shift can only slow a leg by ~1.2-1.36x, against an observed 2.5-4.6x.
  (b) `ternary_nr4a1_r1` rose 8.1 -> 36.9 s/iter while the committed forensic still showed warmup/1152 — the
      whole rise happened inside ONE phase.

★ WHAT THE DATA DOES SUPPORT: card mix. Pooled Spearman is significant, per-card it is not, and the RTX 5090
attempts all precede every RTX 3090 attempt.

⚠ WHAT IT DOES NOT SUPPORT EITHER WAY: a residual within-card trend. Every card points the same direction and
every p is ~0.34 at n = 3-9. That is a POWER limit. These tests are written so that if more data arrives and a
within-card trend becomes significant, the verdict string CHANGES rather than the tests failing — the study
must be able to change its mind.
"""
import datetime
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import throughput_decay as td  # noqa: E402

T0 = datetime.datetime(2026, 7, 31, 12, 0, 0)


def _pts(spec):
    return [(T0 + datetime.timedelta(hours=h), card, s, "u") for h, card, s in spec]


# =============================================================================================================
# the statistics, on cases with a known answer
# =============================================================================================================
def test_a_perfect_monotone_sequence_is_rho_one():
    assert td.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert td.spearman([1, 2, 3, 4], [40, 30, 20, 10]) == pytest.approx(-1.0)


def test_spearman_is_rank_based_so_one_outlier_cannot_manufacture_a_trend():
    """Why not Pearson: s/iter spans 6.85 to 36.9 across hosts, and a single 36.9 would dominate a linear fit.
    The rank correlation is unchanged by how extreme the last point is."""
    mild = td.spearman([1, 2, 3, 4], [10, 11, 12, 13])
    wild = td.spearman([1, 2, 3, 4], [10, 11, 12, 900])
    assert mild == pytest.approx(wild)


def test_the_permutation_test_calls_pure_noise_insignificant():
    import random
    rnd = random.Random(7)
    xs = list(range(12))
    ys = [rnd.random() for _ in xs]
    assert td.permutation_p(xs, ys, n=4000, seed=3) > 0.05


def test_the_permutation_test_is_reproducible():
    xs, ys = [1, 2, 3, 4, 5, 6], [2, 1, 4, 3, 6, 5]
    assert td.permutation_p(xs, ys, n=2000, seed=11) == td.permutation_p(xs, ys, n=2000, seed=11)


# =============================================================================================================
# the discrimination this whole module exists to make
# =============================================================================================================
def test_a_pure_COMPOSITION_effect_is_reported_as_composition():
    """Two cards, each perfectly flat, but the fast one rented early and the slow one late. The pooled trend
    is strong and entirely artefactual — exactly today's shape."""
    pts = _pts([(0, "FAST", 10), (1, "FAST", 10), (2, "FAST", 10), (3, "FAST", 10),
                (4, "SLOW", 30), (5, "SLOW", 30), (6, "SLOW", 30), (7, "SLOW", 30)])
    doc = td.analyse(pts)
    assert doc["pooled"]["rho"] > 0.8 and doc["pooled"]["p"] < 0.05
    assert "EXPLAINED BY CARD MIX" in doc["verdict"]
    for card in ("FAST", "SLOW"):
        assert doc["by_card"][card]["rho"] == pytest.approx(0.0)


def test_a_REAL_within_card_trend_is_reported_as_one():
    """The study must be able to reach the opposite conclusion, or it is not a test. One card, strong trend,
    no composition available to explain it."""
    pts = _pts([(h, "ONE", 10 + 4 * h) for h in range(10)])
    doc = td.analyse(pts)
    assert doc["by_card"]["ONE"]["p"] < 0.05
    assert "WITHIN-CARD TREND SURVIVES" in doc["verdict"]


def test_a_card_with_too_few_points_says_so_rather_than_being_tested():
    pts = _pts([(0, "A", 10), (1, "A", 11), (2, "A", 12), (3, "B", 50)])
    doc = td.analyse(pts)
    assert doc["by_card"]["B"]["note"] == "too few to test"
    assert "p" not in doc["by_card"]["B"]


def test_too_few_observations_overall_refuses_to_conclude():
    assert "too few" in td.analyse(_pts([(0, "A", 1), (1, "A", 2)]))["verdict"]


# =============================================================================================================
# the committed artifact
# =============================================================================================================
ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "throughput-decay.json")


@pytest.mark.skipif(not os.path.exists(ART), reason="analysis not yet run")
def test_the_committed_verdict_carries_the_phase_refutation():
    import json
    d = json.load(open(ART))
    assert "0.834" in d["_phase_refutation"], "the number that refutes phase must travel with the verdict"
    assert "warmup/1152" in d["_phase_refutation"], "and so must the leg that never changed phase"
    assert d["n"] >= 10, "a verdict on fewer than ~10 attempts is not worth committing"
