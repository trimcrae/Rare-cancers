"""THE VOLATILITY ANALYSIS MUST BE RIGHT BEFORE THE DATA ARRIVES — it is what decides the poll cadence.

★ WHY THIS FILE EXISTS. `vast_board_volatility.py` answers a question trimcrae asked directly (*"Is checking
hourly enough? I would think the cheap machines get gobbled up quick"*) and its answer is a RECOMMENDATION TO
SPEND OR NOT SPEND ENGINEERING AND API BUDGET. A survival curve that quietly counts left-censored spells at
their observed length, or a cadence model evaluated at one lucky phase offset, would produce a confident wrong
number that nobody could catch by eye. So every pure function gets a synthetic series whose true answer is
known by construction.

The three traps asserted against, all of which the first draft could have fallen into:

  1. **Left censoring.** A spell already open at the first observed tick has an UNKNOWN start. Counting its
     observed length as its duration biases every quantile DOWNWARD — i.e. it would manufacture exactly the
     "cheap offers evaporate fast" conclusion we are trying to test.
  2. **Phase luck.** A cadence is only as good as its average over start times. Evaluating one offset measures
     luck; the model must average over all of them.
  3. **Mechanism conflation.** An offer that LEFT the board and one that merely REPRICED above the line are
     different events. They happen to imply the same fix here, but reporting them as one hides the case where
     the board is stable and only our own pricing moved.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import vast_board_volatility as vbv  # noqa: E402

LINE = 0.006539          # local literal ONLY so the fixtures are readable; the module derives its own


def _ser(spec, tick_s=60):
    """spec: list of {machine: usd_per_ns} per tick -> the `series()` shape."""
    return [{"t": i, "utc": "2026-07-27T%02d:%02d:00Z" % (12 + i // 60, i % 60),
             "rows": [{"m": m, "u": u, "gpu": "RTX 4090", "bid": 0.1} for m, u in d.items()],
             "n_offers": len(d), "priceable": len(d), "qualifying": len(d)}
            for i, d in enumerate(spec)]


# =============================================================================================================
# best_n_mean — the statistic the gate actually decides on
# =============================================================================================================
def test_best_n_mean_is_the_mean_of_the_n_cheapest_not_the_single_best():
    rows = [{"u": 0.001}, {"u": 0.003}, {"u": 0.005}, {"u": 0.100}]
    assert vbv.best_n_mean(rows, 1) == pytest.approx(0.001)
    assert vbv.best_n_mean(rows, 3) == pytest.approx((0.001 + 0.003 + 0.005) / 3)
    # A fleet of 4 must feel the expensive tail — this is the whole reason the gate uses a mean.
    assert vbv.best_n_mean(rows, 4) == pytest.approx((0.001 + 0.003 + 0.005 + 0.100) / 4)


def test_best_n_mean_ignores_unpriceable_offers_rather_than_guessing_them():
    rows = [{"u": None}, {"u": 0.004}, {"u": None}]
    assert vbv.best_n_mean(rows, 2) == pytest.approx(0.004)
    assert vbv.best_n_mean([{"u": None}], 2) is None


# =============================================================================================================
# spells + Kaplan-Meier — trap 1 (left censoring) and trap 3 (mechanism)
# =============================================================================================================
def test_a_spell_open_at_the_first_tick_is_marked_left_censored():
    # Machine A is under the line from the very first observation: we cannot know when it arrived.
    ser = _ser([{"A": 0.003}, {"A": 0.003}, {"A": 0.003}, {}])
    sp = vbv.spells(ser, line=LINE)
    a = [s for s in sp if s["machine"] == "A"][0]
    assert a["censored_left"] is True
    assert a["ticks"] == 3


def test_kaplan_meier_drops_left_censored_spells_so_it_cannot_bias_survival_downward():
    # A: left-censored, looks short (2 ticks).  B and C: fully observed at 5 ticks each.
    # Including A would drag the median down to 5 ... and in a real board the long-lived offers are
    # exactly the ones most likely to be open at t0, which is what makes this bias so dangerous.
    ser = _ser([{"A": 0.003}, {"A": 0.003},
                {"B": 0.003, "C": 0.003}, {"B": 0.003, "C": 0.003}, {"B": 0.003, "C": 0.003},
                {"B": 0.003, "C": 0.003}, {"B": 0.003, "C": 0.003}, {}])
    km = vbv.kaplan_meier(vbv.spells(ser, line=LINE), tick_s=60)
    assert km["n"] == 2                      # A excluded
    assert km["n_events"] == 2
    assert km["median_minutes"] == pytest.approx(5.0)


def test_km_right_censors_a_spell_still_open_at_the_end_instead_of_calling_it_a_death():
    # B dies at 2 ticks; C is still under the line when observation stops. Treating C as a death at 4 would
    # understate survival; right-censoring keeps S(4) above 0.
    # Tick 0 carries neither, so B and C both ARRIVE under observation and are not left-censored — otherwise
    # this test would silently assert nothing, because KM would have dropped both spells.
    ser = _ser([{}, {"B": 0.003, "C": 0.003}, {"B": 0.003, "C": 0.003},
                {"C": 0.003}, {"C": 0.003}])
    sp = vbv.spells(ser, line=LINE)
    c = [s for s in sp if s["machine"] == "C"][0]
    assert c["censored_right"] is True and c["ended_by"] == "still_open"
    km = vbv.kaplan_meier(sp, tick_s=60)
    assert km["n_events"] == 1
    assert km["curve"][-1][1] > 0.0


def test_spell_ending_separates_taken_from_repriced():
    # A leaves the board entirely; B stays but its price rises through the line.
    ser = _ser([{"A": 0.003, "B": 0.003}, {"B": 0.020}])
    ends = {s["machine"]: s["ended_by"] for s in vbv.spells(ser, line=LINE)}
    assert ends["A"] == "taken"
    assert ends["B"] == "repriced"


def test_a_machine_that_dips_under_the_line_twice_is_two_spells_not_one_long_one():
    ser = _ser([{"A": 0.003}, {"A": 0.020}, {"A": 0.003}])
    sp = [s for s in vbv.spells(ser, line=LINE) if s["machine"] == "A"]
    assert len(sp) == 2
    assert sorted(s["ticks"] for s in sp) == [1, 1]


# =============================================================================================================
# availability
# =============================================================================================================
def test_availability_requires_the_best_k_MEAN_to_clear_not_merely_k_offers_to_exist():
    # Four offers exist, but one is far above the line, so a fleet of 4 does NOT clear — while a fleet of 1
    # does. Conflating "k offers exist" with "k offers are buyable" is how a thin board reads as a full one.
    ser = _ser([{"A": 0.001, "B": 0.001, "C": 0.001, "D": 0.900}])
    av = vbv.availability(ser, line=LINE, needs=(1, 4))
    assert av["fleet_of_1_buyable_frac"] == 1.0
    assert av["fleet_of_4_buyable_frac"] == 0.0
    assert av["any_under_line_frac"] == 1.0


# =============================================================================================================
# cadence_value — trap 2 (phase luck)
# =============================================================================================================
def test_a_perfectly_stable_cheap_board_makes_every_cadence_identical():
    # The null the whole investigation must be able to return: if the price never moves, polling faster buys
    # NOTHING, and the model must say so rather than rewarding speed.
    ser = _ser([{"A": 0.001, "B": 0.001, "C": 0.001, "D": 0.001}] * 60)
    cv = vbv.cadence_value(ser, [1, 5, 30], n_units=4, line=LINE, tick_s=60)
    paid = {k: v["mean_usd_per_ns_paid"] for k, v in cv.items()}
    assert len(set(round(p, 9) for p in paid.values())) == 1
    assert all(v["miss_frac"] == 0.0 for v in cv.values())


def test_a_short_cheap_window_is_captured_by_fast_polling_and_missed_by_slow_polling():
    # One 2-minute buyable window in an hour of an otherwise unbuyable board. A 1-minute poller always finds
    # it; a 30-minute poller usually does not. This is the shape trimcrae's hypothesis predicts, and the
    # model must be able to detect it when it is true.
    spec = [{"A": 0.020, "B": 0.020, "C": 0.020, "D": 0.020} for _ in range(60)]
    for i in (30, 31):
        spec[i] = {"A": 0.001, "B": 0.001, "C": 0.001, "D": 0.001}
    ser = _ser(spec)
    bm = vbv.buyable_minutes(ser, [1, 30], n_units=4, line=LINE)
    assert bm["n_windows"] == 1
    assert bm["by_cadence"]["1min"]["windows_seen_frac"] == 1.0
    assert bm["by_cadence"]["30min"]["windows_seen_frac"] < 0.2


def test_cadence_value_averages_over_every_phase_offset():
    # Same one short window. A model evaluated at a single lucky offset would report the 30-min poller as
    # perfect; averaged over offsets it must show a large miss fraction.
    spec = [{"A": 0.020, "B": 0.020, "C": 0.020, "D": 0.020} for _ in range(60)]
    for i in (30, 31):
        spec[i] = {"A": 0.001, "B": 0.001, "C": 0.001, "D": 0.001}
    cv = vbv.cadence_value(_ser(spec), [30], n_units=4, line=LINE, tick_s=60)["30min"]
    assert cv["opportunities"] > 1                     # more than one phase was evaluated
    assert cv["miss_frac"] > 0.5


# =============================================================================================================
# dollars — the deliverable unit
# =============================================================================================================
def test_dollars_per_day_is_the_price_gap_times_the_work_and_reports_no_saving_as_zero():
    block = {"60min": {"mean_usd_per_ns_paid": 0.005}, "2min": {"mean_usd_per_ns_paid": 0.004}}
    d = vbv.dollars_per_day(block, ns_per_day=1000.0)
    assert d["saving_usd_per_day_vs_baseline"]["2min"] == pytest.approx(1.0)
    assert d["saving_usd_per_day_vs_baseline"]["60min"] == pytest.approx(0.0)


def test_dollars_per_day_reports_a_NEGATIVE_saving_rather_than_hiding_it():
    # Faster polling can genuinely look worse in a finite sample. The honest answer is a negative number,
    # not a clamp to zero — a clamp would let noise masquerade as a benefit.
    block = {"60min": {"mean_usd_per_ns_paid": 0.004}, "2min": {"mean_usd_per_ns_paid": 0.005}}
    d = vbv.dollars_per_day(block, ns_per_day=1000.0)
    assert d["saving_usd_per_day_vs_baseline"]["2min"] == pytest.approx(-1.0)


# =============================================================================================================
# read_noise + truncation + rate_limit — the H2 / H3 discriminators
# =============================================================================================================
def _rec(tick, slot, machines, limit=512, status=200, n=None):
    return {"tick": tick, "slot": slot, "status": status, "limit": limit,
            "utc": "2026-07-27T12:%02d:%02dZ" % (tick, 0 if slot == "R1" else 20),
            "n_offers": len(machines) if n is None else n, "priceable": len(machines),
            "rows": [{"m": m, "u": u, "gpu": "RTX 4090", "bid": 0.1} for m, u in machines.items()]}


def test_read_noise_is_zero_when_two_identical_reads_agree():
    recs = [_rec(0, "R1", {"A": 0.003, "B": 0.004}), _rec(0, "R2", {"A": 0.003, "B": 0.004})]
    rn = vbv.read_noise(recs)
    assert rn["pairs"] == 1
    assert rn["jaccard"]["mean"] == 1.0
    assert rn["d_best4_frac"]["mean"] == 0.0


def test_read_noise_detects_a_board_that_disagrees_with_itself_20_seconds_apart():
    # This is hypothesis H2. If the real data looks like this, poll cadence is the wrong lever entirely and
    # the finding is that the gate has been deciding on its own measurement error.
    recs = [_rec(0, "R1", {"A": 0.003, "B": 0.004}), _rec(0, "R2", {"C": 0.009, "D": 0.010})]
    rn = vbv.read_noise(recs)
    assert rn["jaccard"]["mean"] == 0.0
    assert rn["d_best4_frac"]["mean"] > 0.5


def test_read_noise_ignores_failed_reads_rather_than_scoring_them_as_an_empty_board():
    # A 403 is not "the board went empty". Scoring it as one would invent enormous fake volatility.
    recs = [_rec(0, "R1", {"A": 0.003}), _rec(0, "R2", {}, status=403)]
    assert vbv.read_noise(recs)["pairs"] == 0


def test_truncation_measures_what_the_default_limited_gate_query_misses():
    # H3: the full board carries a cheaper best-4 than the launcher's default-limited window.
    full = {"A": 0.001, "B": 0.001, "C": 0.001, "D": 0.001}
    dflt = {"A": 0.001, "B": 0.001, "C": 0.001, "E": 0.009}
    tr = vbv.truncation([_rec(0, "R1", full), _rec(0, "R3", dflt, limit=None)])
    assert tr["ticks_compared"] == 1
    assert tr["full_board_strictly_better_frac"] == 1.0
    assert tr["default_best4_excess_frac"]["mean"] > 0


def test_rate_limit_counts_edge_html_403s_separately_from_vast_json_errors():
    # CLAUDE.md §6's discriminator: an nginx HTML body is a WAF/edge throttle; a JSON envelope is Vast's own
    # application answering. They mean different things and must never be pooled.
    recs = [{"status": 200, "utc": "2026-07-27T12:00:00Z", "elapsed_s": 0.4},
            {"status": 403, "err_is_html": True, "utc": "2026-07-27T12:01:00Z", "elapsed_s": 0.1},
            {"status": 403, "err_is_html": False, "utc": "2026-07-27T12:02:00Z", "elapsed_s": 0.1}]
    rl = vbv.rate_limit(recs)
    assert rl["by_status"]["403"] == 2
    assert rl["html_403_edge_throttles"] == 1
    assert rl["observed_req_per_min"] == pytest.approx(1.5)


# =============================================================================================================
# the buy line is IMPORTED, never typed (CLAUDE.md §1)
# =============================================================================================================
# =============================================================================================================
# APPENDED SERIES — the two ways a resumed collection corrupts its own analysis
# =============================================================================================================
def test_annotate_separates_runs_so_a_restart_cannot_be_read_as_market_noise():
    # The series is appended across runs and `tick` restarts at 0 each time. Grouping on tick alone pairs
    # run 0's R1 with run 1's R2 — eight minutes apart — and reports it as a 20-second read-to-read gap.
    recs = [{"tick": 0, "slot": "R1", "utc": "2026-07-27T12:00:00Z", "status": 200, "rows": []},
            {"tick": 0, "slot": "R2", "utc": "2026-07-27T12:00:20Z", "status": 200, "rows": []},
            {"tick": 0, "slot": "R1", "utc": "2026-07-27T12:30:00Z", "status": 200, "rows": []},
            {"tick": 0, "slot": "R2", "utc": "2026-07-27T12:30:20Z", "status": 200, "rows": []}]
    out = vbv.annotate(recs)
    assert [r["run"] for r in out] == [0, 0, 1, 1]


def test_read_noise_pairs_within_a_run_not_across_runs():
    # Two runs, each internally identical. Cross-run pairing would compare run 0's cheap board with run 1's
    # expensive one and report enormous "noise"; correct pairing reports none.
    recs = vbv.annotate([
        _rec(0, "R1", {"A": 0.003}), _rec(0, "R2", {"A": 0.003}),
        {**_rec(0, "R1", {"Z": 0.030}), "utc": "2026-07-27T13:00:00Z"},
        {**_rec(0, "R2", {"Z": 0.030}), "utc": "2026-07-27T13:00:20Z"}])
    rn = vbv.read_noise(recs)
    assert rn["pairs"] == 2
    assert rn["jaccard"]["mean"] == 1.0
    assert rn["d_best4_frac"]["max"] == 0.0


def test_series_indexes_on_the_wall_clock_so_two_runs_do_not_collide():
    recs = vbv.annotate([_rec(0, "R1", {"A": 0.003}),
                         {**_rec(0, "R1", {"B": 0.003}), "utc": "2026-07-27T13:00:00Z"}])
    ts = [s["t"] for s in vbv.series(recs, "R1")]
    assert len(set(ts)) == 2, "a per-run tick counter would fold both onto index 0"


def test_a_spell_is_not_bridged_across_an_observation_gap():
    # Machine A is cheap before a 30-minute blackout and cheap after it. We did not watch the gap, so this is
    # NOT one 32-minute spell — crediting it as one invents survival we never observed.
    ser = [{"t": 0, "utc": "x", "rows": [{"m": "A", "u": 0.003}]},
           {"t": 1, "utc": "x", "rows": [{"m": "A", "u": 0.003}]},
           {"t": 31, "utc": "x", "rows": [{"m": "A", "u": 0.003}]},
           {"t": 32, "utc": "x", "rows": [{"m": "A", "u": 0.003}]}]
    sp = vbv.spells(ser, line=LINE)
    assert len(sp) == 2
    assert {s["ended_by"] for s in sp} == {"gone_dark", "still_open"}
    assert max(s["ticks"] for s in sp) == 2


# =============================================================================================================
# ROTATING-SAMPLE CORRECTION — the confound that made the first survival curve meaningless
# =============================================================================================================
def test_miss_probability_measures_the_sampler_not_the_market():
    # Two identical reads, 20 s apart: A is in both, B only in the first, C only in the second. The endpoint
    # omitted one of two machines each way, so p = 0.5 symmetrised.
    recs = [_rec(0, "R1", {"A": 0.003, "B": 0.003}), _rec(0, "R2", {"A": 0.003, "C": 0.003})]
    assert vbv.miss_probability(vbv.annotate(recs)) == pytest.approx(0.5)


def test_miss_probability_is_zero_for_a_stable_endpoint():
    recs = [_rec(0, "R1", {"A": 0.003}), _rec(0, "R2", {"A": 0.003})]
    assert vbv.miss_probability(vbv.annotate(recs)) == 0.0


@pytest.mark.parametrize("p,expected", [(0.0, 1), (0.245, 3), (0.5, 6)])
def test_tolerance_is_derived_from_the_measured_miss_rate(p, expected):
    # Never hand-picked. At the measured p=0.245, three consecutive misses put the false-"gone" rate at
    # 0.245**3 = 1.5 %, under the 2 % target; two would leave it at 6 %.
    assert vbv.tolerance_for(p) == expected


def test_a_single_missed_read_does_not_end_a_spell():
    # A is cheap throughout; the endpoint simply fails to list it at tick 1. With tolerance 2 that is one
    # spell of 4 ticks, not two spells of 1 and 2 — and the difference is the whole survival result.
    ser = _ser([{"A": 0.003}, {}, {"A": 0.003}, {"A": 0.003}])
    sp = vbv.spells(ser, line=LINE, miss_tolerance=2)
    assert len(sp) == 1
    assert sp[0]["ticks"] == 4


def test_the_naive_rule_splits_that_same_spell_which_is_why_it_understates_survival():
    ser = _ser([{"A": 0.003}, {}, {"A": 0.003}, {"A": 0.003}])
    sp = vbv.spells(ser, line=LINE, miss_tolerance=1)
    assert len(sp) == 2
    assert max(s["ticks"] for s in sp) == 2


def test_tolerance_dates_the_end_at_the_last_SIGHTING_not_the_last_tolerated_tick():
    # A vanishes for good after tick 0. With tolerance 3 the spell closes at tick 3, but its length must be
    # 1 tick — otherwise the tolerance would inflate exactly the lifetime it exists to protect.
    ser = _ser([{"A": 0.003}, {}, {}, {}, {}])
    sp = [s for s in vbv.spells(ser, line=LINE, miss_tolerance=3) if s["machine"] == "A"]
    assert len(sp) == 1
    assert sp[0]["ticks"] == 1


def test_the_module_takes_its_buy_line_from_the_one_place_that_owns_it():
    from inflight_usd_per_ns import APPROVED_USD_PER_NS
    assert vbv._line() == APPROVED_USD_PER_NS


def test_mine_git_declares_itself_insufficient_for_survival():
    # The committed snapshots are self-selected and irregular. The module must SAY so rather than letting a
    # reader take its persistence figures for a survival measurement — that verdict is the reason the
    # collector exists at all.
    rep = vbv.mine_git()
    assert rep["sufficient"] is False
    assert "self-selected" in rep["why_not_sufficient"].lower()
