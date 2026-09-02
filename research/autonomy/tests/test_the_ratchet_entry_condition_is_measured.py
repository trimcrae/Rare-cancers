#!/usr/bin/env python3
"""AUT-PD-145's entry condition 2 is a computation, and this is what holds it honest.

⛔⛔ THE DEFECT THIS SUITE ANSWERS: THE CONDITION THAT GATES A HELD BAR WAS ITSELF UNMEASURED.
`MAX_UNSCORED_OPEN` has been sitting on branch `s1-aut-pd-050-unscored-rows` @ d082c01a78 since
2026-08-28, held by a two-part entry condition written only in prose — in AUT-PD-145's `what`, in
CYC-0073-d4ccfde4's receipt, and in the held branch's own docstring. Three seats computed the
gating series by hand from that prose (s6: 253 commits, 82 open; CYC-0073: 120 commits, 85;
CYC-0074's s2: 9 commits, 85), each re-deriving the method. A bar whose ENTRY CONDITION is prose is
governed by whoever reads the prose last, which is the same failure `subagent_width` had for a
fortnight. `unscored_ratchet.entry_verdict` is now the computation; this suite is what stops it
being quietly loosened into a rubber stamp.

★ EVERY CASE HERE IS SYNTHETIC, ON PURPOSE. The decision is a pure function of a measured series,
so it is tested against constructed series and never against live trunk history — a guard that
needs today's git graph to be a particular shape is a guard that goes green or red for reasons that
have nothing to do with the code it guards.

⛔ THE ONE-OF-A-PAIR DOOR, NAMED: a window that rises and then falls back to its starting count has
the same endpoints as a flat one. Checking `last <= first` would pass it. It must not pass: the
rise IS a write that got into the open-unscored population past R5, and that is the event the
window exists to detect. `test_a_window_that_rises_and_recovers_is_not_flat` is that door.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
sys.path.insert(0, AUTONOMY)

import unscored_ratchet as R  # noqa: E402

DAY = "2026-08-29"


def _s(hours_and_counts):
    """[(hours_after_midnight, count), ...] -> the sample tuples the verdict function takes."""
    out = []
    for i, (h, n) in enumerate(hours_and_counts):
        mins = int(round(h * 60))
        out.append((f"{i:040x}", f"{DAY}T{mins // 60:02d}:{mins % 60:02d}:00+00:00", n))
    return out


# 1 -------------------------------------------------------------------------------------------
def test_a_long_flat_window_admits_and_pins_at_the_measured_count():
    """The condition met: >= 2 h after R5, every step <= 0. The pin is the count in the LAST
    commit — "the count measured in the same commit that lands it" — not the first."""
    v = R.entry_verdict(_s([(0, 85), (1, 85), (2.5, 85)]))
    assert v["verdict"] == R.ADMIT, v["why"]
    assert v["pin"] == 85
    assert v["rises"] == []


# 2 -------------------------------------------------------------------------------------------
def test_the_pin_follows_the_last_commit_when_the_series_falls():
    """⛔ A FALLING SERIES MUST NOT PIN AT ITS HIGH-WATER MARK. Pinning at the first count would
    hand the ratchet back exactly the slack that rows scored during the window just removed, and
    `test_the_ratchet_is_not_vacuous` on the held branch refuses a ceiling sitting more than 2
    above the real population — so the wrong pin is not merely generous, it lands red."""
    v = R.entry_verdict(_s([(0, 85), (1, 83), (2.5, 80)]))
    assert v["verdict"] == R.ADMIT, v["why"]
    assert v["pin"] == 80


# 3 -------------------------------------------------------------------------------------------
def test_a_short_window_holds_and_says_when_it_could_pass():
    """The measured state on 2026-08-29 at 01:44Z: flat, and 0.85 h long against a 2 h condition.
    ⛔ HOLD IS NOT A FAILURE AND MUST NOT READ AS ONE — the next cycle needs the CLOCK, and a
    verdict that says only "not yet" sends it to re-derive the series to find out when."""
    v = R.entry_verdict(_s([(0, 85), (0.5, 85), (0.85, 85)]))
    assert v["verdict"] == R.HOLD
    assert v["pin"] is None
    assert v["earliest_satisfiable_utc"] == f"{DAY}T02:00:00Z"


# 4 -------------------------------------------------------------------------------------------
def test_a_rising_series_holds_however_long_the_window_is():
    """Time cannot buy a rising series past this. A rise after R5 means a ledger write reached the
    open-unscored population, which `admissibility.refuse_population_growth` refuses — so it is a
    finding about R5, not a reason to wait longer."""
    v = R.entry_verdict(_s([(0, 85), (2, 86), (4, 86)]))
    assert v["verdict"] == R.HOLD
    assert v["pin"] is None
    assert len(v["rises"]) == 1 and v["rises"][0]["delta"] == 1
    assert "RISES" in v["why"]


# 5 -------------------------------------------------------------------------------------------
def test_a_window_that_rises_and_recovers_is_not_flat():
    """⛔⛔ THE ONE-OF-A-PAIR DOOR. Endpoints 85 -> 85 over 3 h, with an 86 in the middle. An
    end-to-end comparison admits this; the condition is "flat or falling", which is a statement
    about every step. The middle sample is a row that entered the population and was then scored —
    the population DID grow, and R5 is what is supposed to have made that impossible."""
    v = R.entry_verdict(_s([(0, 85), (1, 86), (3, 85)]))
    assert v["verdict"] == R.HOLD, "a rise that recovers is still a rise"
    assert len(v["rises"]) == 1


# 6 -------------------------------------------------------------------------------------------
def test_the_window_boundary_is_inclusive_at_exactly_the_minimum():
    """A window of exactly `MIN_WINDOW_HOURS` satisfies ">= 2 h". One second short does not.
    ⚠ Asserted as a PAIR because a `<` / `<=` slip is invisible to either case alone."""
    assert R.entry_verdict(_s([(0, 85), (R.MIN_WINDOW_HOURS, 85)]))["verdict"] == R.ADMIT
    short = R.entry_verdict([("a" * 40, f"{DAY}T00:00:00+00:00", 85),
                             ("b" * 40, f"{DAY}T01:59:59+00:00", 85)])
    assert short["verdict"] == R.HOLD


# 7 -------------------------------------------------------------------------------------------
def test_one_sample_is_not_a_series():
    """A single commit has no derivative. It cannot be flat, and calling it flat would admit the
    pin on one observation — the weakest possible reading dressed as the strongest.

    ⚠ THE REASON IS ASSERTED, NOT ONLY THE VERDICT, and a surviving mutant is why. Relaxing the
    guard to `len(rows) < 1` leaves one sample falling through to the normal path, where it reads
    as a flat window of 0.0 h and HOLDs anyway — the right answer from the wrong reasoning, which
    goes green today and admits the pin the day the window constant changes."""
    for samples in ([], _s([(0, 85)])):
        v = R.entry_verdict(samples)
        assert v["verdict"] == R.HOLD and v["pin"] is None
        assert "derivative" in v["why"], (
            f"a series of {len(samples)} must be refused for HAVING NO DERIVATIVE, not for being "
            f"a short flat window: {v['why']!r}")
        assert v["n_samples"] == len(samples)


# 8 -------------------------------------------------------------------------------------------
def test_the_series_is_sorted_before_it_is_differenced():
    """⚠ `git log` without `--reverse` runs newest-first, which inverts every delta: a RISING
    series would read as falling and admit the pin. The function sorts by timestamp rather than
    trusting its caller, because the caller that gets this wrong gets it wrong silently.

    ⚠ AGAIN THE REASON, NOT THE VERDICT. `sorted` is stable, so a mutant that sorts by a constant
    leaves the series reversed, and a reversed rising series has a NEGATIVE window — it HOLDs for
    being too short while every delta reads as falling. That mutant survived until this assertion
    named the rise."""
    rising = _s([(0, 85), (1, 86), (2.5, 87)])
    v = R.entry_verdict(list(reversed(rising)))
    assert v["verdict"] == R.HOLD
    assert v["rises"], "the rise must be SEEN, not hidden behind a window measured backwards"
    assert v["window_hours"] == 2.5


# 9 -------------------------------------------------------------------------------------------
def test_the_minimum_window_is_not_a_dial_this_repository_may_turn_quietly():
    """⛔ `MIN_WINDOW_HOURS` is AUT-PD-145's entry condition, and shortening it to fit the window a
    cycle happens to have is the instalment edit that row has already refused twice — once on
    2026-08-28 (pin at 80 against a population of 82) and once on 2026-08-29 (pin at 85 against a
    series rising ~6/h). This asserts the constant is load-bearing rather than decorative: a series
    that is flat for one hour must HOLD at the shipped value."""
    one_hour = _s([(0, 85), (0.5, 85), (1, 85)])
    assert R.entry_verdict(one_hour)["verdict"] == R.HOLD
    assert R.entry_verdict(one_hour, min_window_hours=0.5)["verdict"] == R.ADMIT, (
        "the parameter must be the thing the decision reads, not an unused argument")


# 10 ------------------------------------------------------------------------------------------
def test_the_verdict_never_pins_without_admitting():
    """One fact, one place: `pin` is the number a later cycle types into `MAX_UNSCORED_OPEN`, so a
    HOLD that still reports a pin is an invitation to land the bar the verdict just refused."""
    for samples in (_s([(0, 85), (1, 85)]), _s([(0, 85), (2, 86), (4, 86)]), _s([(0, 85)])):
        v = R.entry_verdict(samples)
        assert (v["pin"] is None) == (v["verdict"] == R.HOLD)


# 11 ------------------------------------------------------------------------------------------
def test_the_series_is_the_trunks_own_states_and_nothing_else(monkeypatch):
    """⛔⛔ `--first-parent`, AND THE MEASUREMENT THAT FOUND IT. On this tool's first real use the
    plain ancestry range over one 1.3 h window returned 17 commits and oscillated 84 -> 85 -> 84 ->
    85 inside four minutes; `--first-parent` returned 6 and was monotone. A side-branch commit's
    ledger is missing every other branch's rows, so its count is the population of a state the
    trunk was never in — counting it invents rises and falls that no writer ever made, in the one
    window whose entire job is to tell a real rise from none.

    ⚠ ALSO ASSERTED HERE: the window is cut by TIMESTAMP, not by ancestry. `git log <sha>..<ref>`
    is an ancestry range and returns commits that PREDATE <sha> when they arrived on a branch that
    merged later — two of them in the first window measured, one carrying a step that made the
    post-R5 series look as though it had risen when the rise predated R5."""
    calls = []

    def fake_git(*args):
        calls.append(args)
        if args[0] == "show" and args[1] == "-s":
            return "2026-08-29T00:49:39+00:00\n"
        if args[0] == "log":
            return ("aaa 2026-08-29T00:30:00+00:00\n"   # PREDATES the cut: ancestry, not time
                    "bbb 2026-08-29T01:00:00+00:00\n")
        return json.dumps({"entries": [{"id": "X", "state": "queued"}]})

    monkeypatch.setattr(R, "_git", fake_git)
    measured = R.series()

    log_args = next(a for a in calls if a[0] == "log")
    assert "--first-parent" in log_args, (
        "the series must walk the trunk's own states; a side-branch commit's ledger is a state the "
        "trunk was never in")
    assert [sha for sha, _, _ in measured] == ["bbb"], (
        "a commit timestamped before the cut is ancestry, not history after it")
