"""⛔ THE ACCOUNT-LEVEL VAST STAND-DOWN, AND THE FOUR WAYS IT COULD FAIL OPEN.

★ WHY IT LIVES AT `VastBackend.submit` AND NOT IN A LANE (trimcrae, 2026-08-26: Vast has not been used in a
month and is not to be driven at all). `submit` is the ONLY place in this repository that creates a Vast
rental — `PUT /asks/{id}/`, Vast's canonical create-instance endpoint. SIX lanes call it: ternary,
congeneric fan-out, protfep, nrv04, bioemu and the ternary watchdog. A per-lane hold has to be written six
times, and is wrong the moment a seventh lane appears. A hold at the door cannot be routed around.

⛔ CREATION ONLY. `destroy`, `stop`, `collect` and every reap path must stay reachable while held, because a
stood-down account must still tear down a host that somehow exists. Otherwise "stood down" quietly becomes
"billing unwatched" — the most expensive recurring failure in this repository's history. The last test below
pins that the hold is NOT consulted anywhere on a teardown path.

⛔ FAIL-SAFE, AND THE ASYMMETRY IS THE POINT: doubt about an instruction to STOP may never resolve to SPEND.
Every malformed hold shape HOLDS; only an explicit deletion resumes.
"""
from __future__ import annotations

import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import gpu_backend as gb  # noqa: E402

#: ⛔ THE REAL FUNCTION, BOUND AT IMPORT. `conftest.py` autouse-patches `gpu_backend.vast_rental_hold` to
#: None so the OTHER lanes' rental-mechanics tests can run past the committed stand-down. This module is the
#: one place that must measure the gate itself, so it keeps a reference taken BEFORE any patch can land —
#: otherwise these tests would assert against the neutraliser and pass no matter what the hold does.
_real_hold = gb.vast_rental_hold


def test_a_valid_hold_holds_and_carries_its_reason(tmp_path):
    (tmp_path / gb.VAST_RENTAL_HOLD).write_text('{"reason": "stood down for the test"}')
    got = _real_hold(root=str(tmp_path))
    assert got and "stood down for the test" in got["reason"], (
        "a well-formed hold must hold AND surface its reason — a pause whose cause does not travel with it "
        "is how an account stays parked long after the reason expired.")


@pytest.mark.parametrize("body,label", [
    ("{ not json at all", "unparseable"),
    ('["a", "list"]', "a list rather than an object"),
    ("", "empty"),
])
def test_a_malformed_hold_still_holds(tmp_path, body, label):
    (tmp_path / gb.VAST_RENTAL_HOLD).write_text(body)
    got = _real_hold(root=str(tmp_path))
    assert got is not None, (
        f"a hold file that is {label} returned None, so a rental would be created. An unreadable "
        "instruction to stop is not permission to spend.")
    assert got.get("reason"), "a holding verdict must still say why it is holding"


def test_no_hold_file_means_the_account_is_free_to_rent(tmp_path):
    assert _real_hold(root=str(tmp_path)) is None, (
        "with no hold file the account must be rentable, or the documented resume path — delete one file — "
        "could never lift the hold.")


def test_submit_refuses_while_held_and_before_any_network_call(monkeypatch):
    """The refusal must pre-empt the board read: a stood-down account prices nothing."""
    def _boom(*a, **k):
        raise AssertionError("submit reached the Vast API while the account was held")
    monkeypatch.setattr(gb, "_vast_request", _boom)
    monkeypatch.setattr(gb, "vast_rental_hold", lambda root=None: {"reason": "held for the test"})
    be = gb.VastBackend()
    spec = gb.JobSpec(name="p", image="i", command="true", resources=gb.ResourceSpec(), env={})
    with pytest.raises(gb.RentalHeldByOperator) as ei:
        be.submit(spec)
    assert "held for the test" in str(ei.value), "the refusal must name the reason on record"


def test_the_refusal_is_typed_as_a_correct_refusal_not_a_fault():
    """⛔ Every `submit` caller sorts NoQualifyingOffer into 'the guard worked', not 'the launcher broke'."""
    assert issubclass(gb.RentalHeldByOperator, gb.NoQualifyingOffer), (
        "RentalHeldByOperator must subclass NoQualifyingOffer, or a stood-down account turns six lanes red "
        "and re-creates the alarm fatigue this stand-down exists to end.")


def test_the_hold_is_not_consulted_on_any_teardown_path():
    """⛔ A held account must still be able to DESTROY. Creation is gated; teardown never is."""
    src = open(os.path.join(MOD, "gpu_backend.py"), encoding="utf-8").read().split("\n")
    calls = [i for i, l in enumerate(src) if re.search(r"^\s*_hold\s*=\s*vast_rental_hold\(", l)]
    assert calls, "the hold check has vanished from gpu_backend — the account can no longer be stood down"
    for i in calls:
        fn = next((src[j] for j in range(i, -1, -1) if re.match(r"\s*def ", src[j])), "")
        assert "def submit" in fn, (
            f"the rental hold is consulted inside `{fn.strip()[:60]}`. It may ONLY gate submit: gating a "
            "teardown path would leave a host billing that nothing is allowed to destroy.")
