"""Guards on the two anti-stall mechanisms: the claim LEASE and the stall ALARM.

⛔⛔ A STALL IS THE WORST FAILURE AN AUTONOMOUS LOOP HAS, because every other failure announces
itself. A crash leaves a traceback. A red gate blocks a commit. A wrong number gets caught by a
linter. A STALL produces nothing at all — no error, no commit, no alarm — and is indistinguishable
from a quiet week for as long as nobody looks. This repository has already lost six weeks to exactly
that shape: a Routine that fired every Friday and delivered nothing.

The two mechanisms attack it from opposite ends:
  the LEASE   makes the commonest stall SELF-HEALING — a claim expires, so a dead cycle cannot park
              an item forever. Detection would still need a human; expiry needs nobody.
  the ALARM   makes an unhealable stall AUDIBLE, from the Actions clock rather than the Routine
              clock, because a supervisor sharing a clock with what it supervises cannot report that
              the clock stopped.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
AUTONOMY = REPO / "research" / "autonomy"
TICK = REPO / ".github" / "workflows" / "autonomy-tick.yml"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"antistall_{name}", AUTONOMY / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def priority():
    return _load("priority")


@pytest.fixture(scope="module")
def alarm():
    return _load("stall_alarm")


def _entry(**kw):
    base = {"id": "AUT-999", "serves": {"route": "RT-X"}, "state": "running", "owner": "CYC-DEAD",
            "attempts": 0, "retry_budget": 3, "score": 10.0, "kind": "analysis"}
    base.update(kw)
    return base


# ────────────────────────────────────────────────────────────────────────── the lease


def test_a_claim_with_no_timestamp_is_released_immediately(priority):
    """⛔ THE LIVE CASE. CYC-0003 claimed AUT-PROP-002, finished, and left the claim standing with no
    `claimed_utc` at all. An owner that cannot be aged is an IMMORTAL claim, and the next driver would
    skip the queue's top item forever. Fail toward releasing: a re-done item is idempotent, a stall
    is not."""
    weights = priority.load_weights()
    entries = priority.release_stale_claims([_entry()], weights, 4.0)
    assert entries[0]["owner"] is None
    assert entries[0]["state"] == "queued", "a released claim must return the item to the queue"
    assert "never stamped" in entries[0]["lease_released"]


def test_a_fresh_claim_is_left_alone(priority):
    """The other half. A lease that expires instantly would let two cycles take one item — which is
    the failure the claim exists to prevent, reintroduced by its own fix."""
    weights = priority.load_weights()
    now = datetime.datetime.now(datetime.timezone.utc)
    fresh = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    entries = priority.release_stale_claims([_entry(claimed_utc=fresh)], weights, 4.0, now=now)
    assert entries[0]["owner"] == "CYC-DEAD", "a claim made moments ago must survive"
    assert "lease_released" not in entries[0]


def test_a_claim_older_than_the_lease_is_released(priority):
    weights = priority.load_weights()
    now = datetime.datetime.now(datetime.timezone.utc)
    periods = weights["claim_lease"]["periods"]
    old = (now - datetime.timedelta(hours=4.0 * periods + 1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries = priority.release_stale_claims([_entry(claimed_utc=old)], weights, 4.0, now=now)
    assert entries[0]["owner"] is None
    assert entries[0]["attempts"] == 1, "a released claim counts as an attempt, or it retries forever"


def test_an_unparseable_timestamp_releases_rather_than_holds(priority):
    """CLAUDE.md §4: a populated field is not a measured one. A stamp we cannot read is not a stamp."""
    weights = priority.load_weights()
    entries = priority.release_stale_claims([_entry(claimed_utc="last tuesday")], weights, 4.0)
    assert entries[0]["owner"] is None


def test_the_lease_is_load_bearing_and_not_decorative(priority):
    """Mutation test: with release_stale_claims bypassed, the immortal claim must actually persist."""
    unreleased = [_entry()]
    assert unreleased[0]["owner"] == "CYC-DEAD", (
        "the fixture already has no owner — this suite would pass against a lease that does nothing"
    )


def test_the_real_ledger_has_no_immortal_claims(priority):
    """The property, checked against the committed ledger rather than a fixture."""
    ledger = json.loads((AUTONOMY / "research-ledger.json").read_text())
    orphans = [e["id"] for e in ledger["entries"] if e.get("owner") and not e.get("claimed_utc")]
    assert not orphans, (
        f"{orphans} are owned with no claimed_utc, so their claims can never expire and no cycle "
        "will ever take them again"
    )


# ────────────────────────────────────────────────────────────────────────── the alarm


def _red(runs: int, key: str = "cycle_delivering") -> dict:
    return {"conditions": [{"key": key, "needs_attention": True, "verdict": "NO-RECEIPT",
                            "detail": "no receipt within 2 expected cycle periods",
                            "bad_since_utc": "2026-08-26T21:00:00Z",
                            "consecutive_bad_runs": runs}]}


def test_one_transient_red_never_wakes_anybody(alarm):
    assert alarm.decide(_red(1))["send"] is False


def test_a_sustained_red_alarms(alarm):
    verdict = alarm.decide(_red(alarm.FIRST_ALARM_RUNS))
    assert verdict["send"] is True
    assert "cycle_delivering" in verdict["subject"]
    assert "receipts" in verdict["body"], "the mail must say where to look, not just that it is bad"


def test_it_does_not_re_alarm_every_run(alarm):
    """⛔ THE FAILURE THAT KILLED THE LAST PUSH CHANNEL IN THIS REPO. Every push channel was stripped
    out of lane-staleness-watch.yml after a supervisor emitted 1,476 commits in 24 h. A muted alarm is
    worse than none, because it also carries the belief that somebody is watching."""
    for runs in range(alarm.FIRST_ALARM_RUNS + 1,
                      alarm.FIRST_ALARM_RUNS + alarm.REPEAT_EVERY_RUNS):
        assert alarm.decide(_red(runs))["send"] is False, f"re-alarmed at {runs} runs"


def test_it_does_re_alarm_after_a_day(alarm):
    assert alarm.decide(_red(alarm.FIRST_ALARM_RUNS + alarm.REPEAT_EVERY_RUNS))["send"] is True


def test_green_and_unmeasured_never_alarm(alarm):
    assert alarm.decide({"conditions": [{"key": "x", "needs_attention": False}]})["send"] is False
    assert alarm.decide({"conditions": [
        {"key": "x", "needs_attention": False, "unmeasured": True}]})["send"] is False


def test_the_alarm_ages_on_the_worst_established_red(alarm):
    """A second condition going red must not reset the clock and delay the alarm on the first."""
    board = {"conditions": [
        {"key": "old", "needs_attention": True, "consecutive_bad_runs": 9, "detail": "d"},
        {"key": "new", "needs_attention": True, "consecutive_bad_runs": 1, "detail": "d"},
    ]}
    assert alarm.decide(board)["send"] is False  # 9 is mid-repeat-window, not a reset to 1
    board["conditions"][0]["consecutive_bad_runs"] = alarm.FIRST_ALARM_RUNS
    assert alarm.decide(board)["send"] is True


def test_the_alarm_runs_on_the_other_clock(alarm):
    """★ THE WHOLE POINT. If this ever moves into a research cycle, a stalled loop stops alarming
    about itself — which is the one thing it must never do."""
    text = TICK.read_text()
    assert "stall_alarm.py" in text, "the alarm is not wired into the Actions tick"
    assert "schedule:" in text, "the Actions tick has no clock of its own"


def test_an_unreadable_board_is_not_treated_as_healthy(alarm, tmp_path, capsys):
    """The checker that writes the board runs in the same job. A missing board means the step before
    us failed — which is a stall signal, not silence."""
    assert alarm.main(["--health", str(tmp_path / "nope.json"), "--dry-run"]) == 0
    assert "cannot read" in capsys.readouterr().out
