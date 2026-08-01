"""THE SETUP TAX PARSER — a cache whose effectiveness is unobservable is one we cannot tell from an absent one.

trimcrae, 2026-07-31: *"What do we have to do to get back to the good throughput we had in prior sessions?"*
The comparison rules out the obvious answer: the step 1 fan-out churned HARDER than 5a-KS (208 rentals for 19
units, median 7 each, max 37) and still landed 18 of 19. What differs is how much of each rental is
PRODUCTIVE — fan-out median 1.62 h per rental against <= 1.00 h here, against a ~28 min time-to-first-commit,
so 25 % of this lane's sessions bank nothing at all.

⚠ THE TRI-STATE IS THE WHOLE POINT. HIT / MISS / ABSENT are three different findings:
  * HIT    — the work was skipped.
  * MISS   — the cache is configured and cold; pre-bake it.
  * ABSENT — the line was never printed, so we cannot say. That is a REPORTING defect, not a cost, and
             folding it into MISS would invent a number while folding it into HIT would hide one.
CLAUDE.md §4: an absent reading is not a reading of absence.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import setup_tax as tax  # noqa: E402

HIT_LOG = """[tvast] stage cache HIT -> s3://b/p/stage.tar
[tvast] pre-equil cache HIT -> s3://b/p/pe.tar (relaxed complex.pdb + ligands.sdf overlaid)
  [spot-safe] SETUP RESTORED from cache s3://b/p/setupcache/leg__nagl__v1pe — skipped the ~460s solvate
[spot-driver] restore: production took 12.4s
[restore] production: list_committed returned 7 generation(s) in 0.9s
[restore] production iter 1360 gen abcdef12 fetched 41231344 B in 11.2s
[timing] iter 5: 33.9 s/iter
"""

MISS_LOG = """[tvast] stage cache MISS -> staging leg from 1abc
[tvast] pre-equil cache MISS -> running ternary_preequil.py (1.0 ns)
  [spot-safe] SETUP begin (solvate + parameterize the hybrid system)…
  [spot-safe] SETUP done in 512s
"""

SILENT_LOG = "[tvast] recipe+engine sha256[:12]=c22be929a990 branch=main\n"


def test_a_hit_is_read_as_a_hit_on_every_cache():
    p = tax.parse_log(HIT_LOG)
    assert p["caches"] == {"stage": True, "preequil": True, "setup": True}
    assert p["setup_restored_from"].endswith("v1pe")
    assert p["setup_built"] is False and p["setup_seconds"] is None


def test_a_miss_is_read_as_a_miss_and_carries_what_it_cost():
    p = tax.parse_log(MISS_LOG)
    assert p["caches"] == {"stage": False, "preequil": False, "setup": False}
    assert p["setup_built"] is True and p["setup_seconds"] == 512.0
    assert "rebuilt the hybrid system ON THE RENTED GPU" in tax.verdict(p)


def test_a_log_that_says_NOTHING_is_ABSENT_and_never_a_hit_or_a_miss():
    p = tax.parse_log(SILENT_LOG)
    assert p["caches"] == {"stage": None, "preequil": None, "setup": None}
    v = tax.verdict(p)
    assert v.count("ABSENT(unobservable)") == 3
    assert "HIT" not in v and "MISS" not in v


def test_the_fail_fast_branch_is_distinguished_from_an_ordinary_miss():
    """`RBFE_REQUIRE_PRIMED_SETUP=1` makes a cold setup cache KILL the leg rather than rebuild on the GPU.
    That is a dead rented host, not a slow one, and it needs its own line in the readout."""
    p = tax.parse_log("  [spot-safe] SETUP CACHE MISSING at s3://b/p/setupcache/leg__nagl__v1pe — refusing\n")
    assert p["caches"]["setup"] is False
    assert p["setup_cache_missing"].endswith("v1pe")
    assert "FAILS FAST" in tax.verdict(p)
    assert p["setup_built"] is False, "a fail-fast leg did NOT pay for a rebuild — do not bill it for one"


def test_the_restore_timings_are_split_into_list_and_fetch():
    """The 5a-KS wedge was inside one of those two and the log could not say which — that is the whole reason
    both lines exist."""
    p = tax.parse_log(HIT_LOG)
    assert p["restore_seconds"] == {"production": 12.4}
    assert p["restore_list"] == [{"phase": "production", "n_gen": 7, "seconds": 0.9}]
    assert p["restore_fetch"][0]["bytes"] == 41231344


def test_the_iteration_rate_is_the_median_not_the_first():
    p = tax.parse_log("[timing] iter 1: 90.0 s/iter\n[timing] iter 2: 34.0 s/iter\n[timing] iter 3: 33.0 s/iter\n")
    assert p["s_per_iter"] == 34.0, "the first iteration includes warm-up cost and is not the rate"


@pytest.mark.parametrize("text", ["", "\n\n", "garbage without any anchor at all"])
def test_it_never_raises_on_a_log_it_does_not_understand(text):
    """This runs over archived logs from every past protocol version. A parser that throws on an old format
    would take the whole forensic down with it."""
    p = tax.parse_log(text)
    assert set(p["caches"].values()) == {None}


# =============================================================================================================
# THE COLD-START SPLIT — the most expensive unknown on this lane, and it was unmeasurable by construction
# =============================================================================================================
# `mark()` wrote its timestamp ONLY to `phase.txt`, which it OVERWRITES, so the history was destroyed at every
# transition and the run.log carried exactly two clocks: `start` and `EXIT`. The ~28 min cold start could be
# measured as a TOTAL and never split. Median session is ~1.00 h, so that is ~47 % of every rental, and any
# session shorter than it banks NOTHING — 25 % of today's. Measure-on-arrival showed the MD itself is fine
# (the worst host today still reaches a commit boundary in ~39 min of a 48 min budget), so this is the
# constraint. `mark()` now echoes `[tvast] <utc> phase=<name>` and the line items record themselves.
FULL = """[tvast] 2026-07-31T12:00:00Z start unit=x leg=y seed=0 dir=fwd dt=4.0fs warmup_dt=1.0fs
[tvast] 2026-07-31T12:00:30Z phase=start
[tvast] 2026-07-31T12:01:10Z phase=staging
[tvast] 2026-07-31T12:06:40Z phase=preequil
[tvast] 2026-07-31T12:13:20Z phase=md-running
[tvast] 2026-07-31T12:58:00Z EXIT rc=0
"""


def test_the_split_is_derived_from_the_logs_OWN_stamps():
    tl = tax.timeline(FULL)
    assert tl["complete"] is True
    s = tl["spans"]
    assert s["staging->preequil"] == 330.0            # 5.5 min of STAGE
    assert s["preequil->md-running"] == 400.0         # 6.7 min of PRE-EQUIL
    assert s["container-start->start"] == 30.0


def test_a_log_from_BEFORE_the_marks_were_timestamped_is_incomplete_not_zero():
    """The retroactive trap: every attempt logged before 2026-07-31 has no phase marks. Reporting those as
    zero-length phases would invent a split that was never measured — the same shape as
    `pooled_across_systems` reporting a median that describes no assembly."""
    tl = tax.timeline("[tvast] 2026-07-31T12:00:00Z start unit=x\n[tvast] 2026-07-31T12:58:00Z EXIT rc=0\n")
    assert tl["complete"] is False
    assert "staging->preequil" not in tl["spans"]


def test_a_container_restart_does_not_double_count_a_phase():
    """Vast re-runs onstart on a restart, so a phase can be marked twice in one log. Identical marks collapse;
    a genuinely repeated phase at a NEW time is kept, because that is a real second pass through it."""
    dup = FULL + "[tvast] 2026-07-31T12:01:10Z phase=staging\n"
    assert len(tax.timeline(dup)["marks"]) == len(tax.timeline(FULL)["marks"])


def test_the_timeline_rides_the_ordinary_parse_so_every_attempt_carries_it():
    assert tax.parse_log(FULL)["timeline"]["complete"] is True


def test_a_malformed_stamp_does_not_take_the_parse_down():
    assert tax.timeline("[tvast] not-a-date phase=staging")["spans"] == {}
    assert tax.parse_log("[tvast] not-a-date phase=staging")["timeline"]["complete"] is False


# =============================================================================================================
# THE LIVE COLD START — measurable NOW, without waiting for a re-placement
# =============================================================================================================
class _S3:
    def __init__(self, objs):
        self.objs = objs

    def get_object(self, Bucket=None, Key=None):  # noqa: N803
        import io
        if Key not in self.objs:
            raise KeyError(Key)
        return {"Body": io.BytesIO(self.objs[Key].encode())}


def test_the_current_phase_start_survives_even_though_the_history_does_not():
    """`mark()` OVERWRITES phase.txt, so the history is gone — but the CURRENT phase's start time is still
    there, and the log has always carried `[tvast] <utc> start`. For a leg that has reached `md-running` the
    difference is its whole cold start, on the attempt that is billing now. That is how the headline question
    gets answered without waiting for a re-placement."""
    s3 = _S3({"pfx/legs/u/phase.txt": "md-running 2026-07-31T12:24:00Z\n",
              "pfx/legs/u/run.log": "[tvast] 2026-07-31T12:00:00Z start unit=u leg=l seed=0 dir=fwd\n"})
    secs, span = tax.live_cold_start("u", "b", "pfx", s3)
    assert secs == 1440.0 and "md-running" in span


@pytest.mark.parametrize("objs,expect", [
    ({}, "no phase.txt"),
    ({"pfx/legs/u/phase.txt": "md-running 2026-07-31T12:24:00Z"}, "no run.log"),
    ({"pfx/legs/u/phase.txt": "md-running", "pfx/legs/u/run.log": "[tvast] 2026-07-31T12:00:00Z start x"},
     "absent"),
    ({"pfx/legs/u/phase.txt": "md-running nonsense",
      "pfx/legs/u/run.log": "[tvast] 2026-07-31T12:00:00Z start x"}, "unparseable"),
])
def test_a_missing_clock_returns_None_and_says_which(objs, expect):
    """Never a zero. An unmeasured cold start reported as 0 min would be the most flattering possible lie
    about the exact number this whole thread turns on."""
    secs, why = tax.live_cold_start("u", "b", "pfx", _S3(objs))
    assert secs is None and expect in why


# ── THE LINE-ITEM SPLIT: where the rental's wall time actually goes ──────────────────────────────────────
#
# "~28 min before the first commit" is a number nobody can act on. Staging, image pull, minimisation and
# warmup MD have completely different remedies, and spending on the wrong one buys nothing. What the split
# has to guarantee is that it never invents a segment it did not measure.

def _att(marks_spans, ci=None, spi=None, name="a.log", complete=True):
    marks, spans = marks_spans
    return {"attempt": name, "checkpoint_interval": ci, "s_per_iter": spi,
            "timeline": {"marks": marks, "spans": spans, "complete": complete}}


_MARKS = [("container-start", "t0"), ("start", "t1"), ("cloned", "t2"), ("staging", "t3"),
          ("preequil", "t4"), ("md-running", "t5")]
_SPANS = {"container-start->start": 6.0, "start->cloned": 18.0, "cloned->staging": 6.0,
          "staging->preequil": 6.0, "preequil->md-running": 6.0}      # 42 s = 0.7 min


def test_provisioning_is_None_and_NEVER_zero():
    """★★ THE ONE THAT MATTERS MOST. Host boot and the image pull happen BEFORE the container's first log
    line, so the container's own log physically cannot see them. Reporting 0 would make the split sum to the
    wrong total and quietly exonerate the one segment nobody has measured — §4, an absent reading is not a
    reading of absence."""
    r = tax.attempt_line_items(_att((_MARKS, _SPANS)))
    assert r["provision_to_container"] is None
    agg = tax.line_items({"u": {"attempts": [_att((_MARKS, _SPANS))]}})["aggregate"]
    assert agg["provision_to_container"]["median_min"] is None
    assert agg["provision_to_container"]["n"] == 0
    assert "NOT MEASURED" in agg["provision_to_container"]["why_none"]


def test_the_in_container_setup_is_summed_from_the_logs_own_stamps():
    r = tax.attempt_line_items(_att((_MARKS, _SPANS)))
    assert r["container_to_md_running"] == 0.7
    assert set(r["setup_breakdown"]) == set(_SPANS)


def test_a_missing_span_yields_None_rather_than_a_short_total():
    """A partial timeline must not read as a FAST setup — that is the direction that would exonerate the
    segment it failed to measure."""
    bad = dict(_SPANS)
    del bad["cloned->staging"]
    assert tax.attempt_line_items(_att((_MARKS, bad)))["container_to_md_running"] is None


def test_an_attempt_that_never_reached_md_running_has_no_setup_figure():
    r = tax.attempt_line_items(_att((_MARKS[:4], _SPANS)))
    assert r["container_to_md_running"] is None and r["setup_breakdown"] == {}


def test_time_to_first_commit_is_DERIVED_and_says_so():
    """The `[barrier] commit` line carries a persist duration but no wall-clock stamp, so this segment is
    reconstructed as interval x s/iter. A reconstructed number that does not announce itself is the kind
    that later gets quoted as a measurement."""
    r = tax.attempt_line_items(_att((_MARKS, _SPANS), ci=40, spi=55.5))
    assert r["md_running_to_first_commit"] == round(40 * 55.5 / 60.0, 2)
    assert r["first_commit_is_derived"] is True
    agg = tax.line_items({"u": {"attempts": [_att((_MARKS, _SPANS), ci=40, spi=55.5)]}})["aggregate"]
    assert "reconstructed" in agg["md_running_to_first_commit"]["derived"]


def test_no_interval_or_no_rate_yields_None_not_a_guess():
    for ci, spi in ((None, 55.5), (40, None), (None, None)):
        assert tax.attempt_line_items(_att((_MARKS, _SPANS), ci=ci, spi=spi))["md_running_to_first_commit"] is None


def test_the_verdict_names_the_DOMINANT_term_because_that_is_the_only_actionable_part():
    agg = tax.line_items({"u": {"attempts": [_att((_MARKS, _SPANS), ci=40, spi=55.5)]}})["aggregate"]
    v = agg["verdict"]
    assert "TIME TO THE FIRST COMMIT DOMINATES" in v
    assert "CHECKPOINT INTERVAL" in v
    assert "Provisioning is still unmeasured" in v, "the unmeasured segment must be named in the verdict too"


def test_the_verdict_is_INCONCLUSIVE_rather_than_confident_when_the_split_is_incomplete():
    agg = tax.line_items({"u": {"attempts": [_att((_MARKS, _SPANS))]}})["aggregate"]
    assert agg["verdict"].startswith("INCONCLUSIVE")


def test_the_interval_comes_from_the_drivers_RESOLVED_line_not_the_modes_config():
    """A leg resumed from an older checkpoint runs the OLD grid whatever the env now says, so timing it
    against the requested interval would mis-time every resumed leg."""
    src = open(tax.__file__).read()
    assert "interval_for_phase(text" in src
    assert "_ib" in src, "the interval parser has one home in inflight_board and must be imported, not retyped"


# ── THE DOMINANT SEGMENT IS NOW MEASURED AS WELL AS DERIVED (2026-08-01) ────────────────────────────────
#
# `md_running_to_first_commit` is this module's biggest term and the one its verdict turns on, and it was
# RECONSTRUCTED — checkpoint_interval x s_per_iter — because `[barrier] commit` carries a persist duration
# and no wall clock. A reconstruction nobody ever checks against a clock is one nobody can grade.
#
# There is a clock: S3 stamps every commit generation with `LastModified`, and `phase.txt` carries the
# `md-running` boundary. `md_to_first_commit` reads the first object written after that mark.

def test_the_measured_value_lands_BESIDE_the_derived_one_not_in_a_second_block():
    """CLAUDE.md §1. Two dicts holding the same segment by two routes is how they start disagreeing with
    nobody noticing which is quoted."""
    agg = tax.line_items({"u": {"attempts": [_att((_MARKS, _SPANS), ci=40, spi=55.5)],
                                "md_to_first_commit_s": 1800.0}})["aggregate"]
    seg = agg["md_running_to_first_commit"]
    assert seg["measured_median_min"] == 30.0
    assert seg["measured_n_units"] == 1
    assert seg["derived"], "the derived value must survive — it is the only one available retrospectively"
    assert "md_window_split" not in agg


def test_no_unit_inside_md_running_reads_as_UNKNOWN_never_as_fast():
    """`phase.txt` is OVERWRITTEN, so a unit contributes a measurement only while it is inside md-running.
    Zero units is 'we cannot see it right now', which is not a small number (§4a)."""
    agg = tax.line_items({"u": {"attempts": [_att((_MARKS, _SPANS), ci=40, spi=55.5)]}})["aggregate"]
    seg = agg["md_running_to_first_commit"]
    assert seg["measured_median_min"] is None and seg["measured_n_units"] == 0
    assert "NOT the same as a fast segment" in seg["measured_how"]


def test_the_two_self_timed_pieces_inside_the_window_are_reported_so_a_reader_can_subtract():
    att = _att((_MARKS, _SPANS), ci=40, spi=55.5)
    att["setup_seconds"] = 240.0
    att["restore_seconds"] = {"warmup": 30.0}
    seg = tax.line_items({"u": {"attempts": [att]}})["aggregate"]["md_running_to_first_commit"]
    assert seg["of_which_setup_build_min"] == 4.0
    assert seg["of_which_setup_restore_min"] == 0.5
    assert "RESIDUAL, not a measurement of minimisation" in seg["_residual_is"]


def test_an_unprinted_line_item_is_None_not_zero():
    seg = tax.line_items({"u": {"attempts": [_att((_MARKS, _SPANS), ci=40, spi=55.5)]}}
                         )["aggregate"]["md_running_to_first_commit"]
    assert seg["of_which_setup_build_min"] is None and seg["of_which_setup_restore_min"] is None


def test_md_to_first_commit_refuses_a_phase_txt_that_is_not_md_running():
    """The boundary is only in the record while the unit is inside that phase — `phase.txt` is overwritten.
    A leg that has moved on must return 'cannot measure', never a span against the wrong mark."""
    class _S3:
        def get_object(self, Bucket, Key):
            import io
            return {"Body": io.BytesIO(b"md-done 2026-08-01T02:00:00Z")}
    s, why = tax.md_to_first_commit("u", "b", "p", _S3())
    assert s is None and "md-done" in why and "not md-running" in why
