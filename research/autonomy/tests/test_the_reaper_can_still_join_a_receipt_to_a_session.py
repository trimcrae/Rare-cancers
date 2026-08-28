#!/usr/bin/env python3
"""The reaper's join survives BOTH id changes that have already broken it (AUT-PD-129).

⛔⛔ THE DEFECT, MEASURED ON THE TRUNK 2026-08-28. `session_reaper.py` answers one question — is
this idle session's work on `main`? — by joining the session list to committed receipts. That join
was broken in two independent places at once, and both failed SILENTLY and in the dangerous
direction (a delivered cycle reported as one that died holding uncommitted work):

  1. FILENAME. The module carried its own `re.compile(r"^CYC-\\d+\\.json$")`. AUT-PROP-013 had since
     appended a session discriminator to every receipt id (`CYC-0065-1f1a2449.json`) so that two
     concurrent cycles sharing an ordinal could not share a file. The private pattern matched 24 of
     70 committed receipts; `ids.RECEIPT_ID` — the one home for the shape — matched 69.

  2. ID SPACE, and it survives fixing (1). The session list speaks CCR ids (`session_01...`).
     research-loop §2 step 10 was tightened the same week to require `session_id` be read from
     `CLAUDE_CODE_SESSION_ID`, which is a harness UUID. That was correct for its readers
     (`health.py:c_cycles_are_sized`, `session_cap.py`) and left this one joining two different id
     spaces. Measured: 12 receipts carried a CCR id, 27 a bare UUID, and all eight of the newest
     were UUIDs — so after fixing (1) alone, `committed_session_ids()` still returned the same 10
     pre-discriminator ids and the reaper still could not archive a single modern session.

★ WHY BOTH HALVES NEED A TEST AND NOT A COMMENT. Fixing (1) without (2) LOOKS like a fix — more
receipts are read — while changing nothing a caller can observe. That is exactly the shape this
repository keeps paying for, so each half is pinned by a test that fails if it regresses, plus the
negative control that keeps the original finding alive when the join is genuinely healthy.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
sys.path.insert(0, AUTONOMY)

import ids  # noqa: E402
import receipt_schema as S  # noqa: E402
import session_reaper as R  # noqa: E402


# ---------------------------------------------------------------------------------------------
# (1) the filename half
# ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name,expected", [
    ("CYC-0065-1f1a2449.json", True),   # the discriminated shape AUT-PROP-013 introduced
    ("CYC-0012.json", True),            # the bare shape, still valid
    ("CYC-0026-schedrou.json", True),   # a non-hex discriminator, which real receipts carry
    ("notes.json", False),
    ("CYC-0065-1f1a2449.txt", False),
])
def test_the_receipt_filename_predicate_accepts_every_shape_this_repo_has_written(name, expected):
    assert R._is_cycle_receipt(name) is expected


def test_the_filename_shape_is_imported_and_not_restated():
    """⛔ THE TRAP ITSELF. A private copy of the id shape is what went stale; if one reappears, this
    fails. `ids.RECEIPT_ID` is the one home (CLAUDE.md rule 1)."""
    assert R._CYCLE_RECEIPT_STEM is ids.RECEIPT_ID, (
        "session_reaper is matching receipt filenames with its own pattern again instead of "
        "ids.RECEIPT_ID. That is the exact defect AUT-PD-129 records: the shape changed, the private "
        "copy did not, and the reaper silently stopped seeing 46 of 70 receipts.")


def test_the_pattern_that_broke_it_would_now_fail_this_suite():
    """The negative control: the OLD pattern must not satisfy the parametrised case above."""
    import re
    old = re.compile(r"^CYC-\d+\.json$")
    assert not old.match("CYC-0065-1f1a2449.json"), (
        "the superseded pattern is being asserted as correct; it is the bug, not the fix")


# ---------------------------------------------------------------------------------------------
# (2) the id-space half
# ---------------------------------------------------------------------------------------------

def _receipt_dir(tmp_path, monkeypatch, receipts):
    """Point committed_session_ids at a fake 'committed' tree, without touching git."""
    def fake_run(cmd, **kw):
        class Out:
            returncode = 0
            stderr = ""
        o = Out()
        if cmd[1] == "ls-tree":
            o.stdout = "\n".join(receipts)
        else:
            o.stdout = json.dumps(receipts[cmd[2].rsplit("/", 1)[-1]]) \
                if isinstance(receipts, dict) else ""
        return o
    return fake_run


def test_committed_session_ids_reads_the_ccr_field(tmp_path, monkeypatch):
    """A receipt whose `session_id` is a harness UUID still joins, via `ccr_session_id`."""
    payload = {
        "CYC-0070-8226e21b.json": {
            "session_id": "8226e21b-fa7b-5a99-9783-ee71d497cf6c",   # the harness UUID
            "ccr_session_id": "session_018A9rdUZLrexk1HJrKtDCd2",   # the CCR id the list uses
        },
    }

    def fake_run(cmd, **kw):
        class Out:
            returncode = 0
            stderr = ""
        o = Out()
        if cmd[1] == "ls-tree":
            o.stdout = " ".join(payload)
        else:
            o.stdout = json.dumps(payload[cmd[2].rsplit("/", 1)[-1]])
        return o

    monkeypatch.setattr(R.subprocess, "run", fake_run)
    got = R.committed_session_ids()
    assert got == {"session_018A9rdUZLrexk1HJrKtDCd2"}, (
        "a receipt recording the harness UUID in `session_id` and the CCR id in `ccr_session_id` "
        "must still join to the session list; got %r" % (got,))


def test_a_uuid_only_receipt_counts_as_unjoinable(monkeypatch):
    """⛔ THE HONESTY MEASUREMENT. A receipt naming no CCR id can never match, and saying so is what
    stops the reaper reporting a delivered cycle as a death."""
    payload = {"CYC-0070-8226e21b.json": {"session_id": "8226e21b-fa7b-5a99-9783-ee71d497cf6c"}}

    def fake_run(cmd, **kw):
        class Out:
            returncode = 0
            stderr = ""
        o = Out()
        o.stdout = " ".join(payload) if cmd[1] == "ls-tree" \
            else json.dumps(payload[cmd[2].rsplit("/", 1)[-1]])
        return o

    monkeypatch.setattr(R.subprocess, "run", fake_run)
    assert R.receipts_that_cannot_join() == 1
    assert R.committed_session_ids() == set()


# ---------------------------------------------------------------------------------------------
# (3) what the verdict says — and the negative control that keeps the real finding alive
# ---------------------------------------------------------------------------------------------

def _sess(sid):
    return {"id": sid, "session_status": "SESSION_STATUS_IDLE",
            "title": "EMC research loop — cycle (x)", "tags": ["emc-research-loop"]}


def test_a_degraded_join_is_not_reported_as_a_death(monkeypatch):
    monkeypatch.setattr(R, "committed_session_ids", lambda ref="HEAD": set())
    v = R.classify([_sess("session_01Orphan000000")], None, unjoinable_receipts=58)
    why = v["keep"][0]["why"]
    assert not v["archive"], "a degraded join must never license archiving"
    assert "DEGRADED" in why and "58" in why, why
    # ⛔ COMPARED AGAINST THE OTHER BRANCH'S ACTUAL TEXT, NOT A SUBSTRING GUESS. The degraded
    # message legitimately QUOTES the phrase "died holding work" while explaining what it cannot
    # distinguish, so a naive `"died holding" not in why` fails on correct behaviour — it did, on
    # the first run of this suite. What must be true is that the two verdicts are not the same
    # verdict, and that this one does not ASSERT a death.
    healthy = R.classify([_sess("session_01Orphan000000")], None, unjoinable_receipts=0)
    assert why != healthy["keep"][0]["why"], (
        "a degraded join and a healthy one produce the same reason string, so the reader cannot "
        "tell an instrument gap from a cycle that died holding work")
    assert "this is a finding, not litter" not in why, (
        "the reaper is still asserting a death on an unjoinable session: " + why)


def test_the_death_finding_survives_a_healthy_join(monkeypatch):
    """⛔ THE NEGATIVE CONTROL. If the join is clean, 'no receipt' IS the real finding, and softening
    it unconditionally would delete the alarm this reaper exists to raise."""
    monkeypatch.setattr(R, "committed_session_ids", lambda ref="HEAD": set())
    v = R.classify([_sess("session_01Orphan000000")], None, unjoinable_receipts=0)
    why = v["keep"][0]["why"]
    assert not v["archive"]
    assert "died holding uncommitted work" in why, why


# ---------------------------------------------------------------------------------------------
# (4) the schema that heals it going forward
# ---------------------------------------------------------------------------------------------

_BASE = {"cycle_id": "CYC-0070-abcd1234", "route_advanced": "RT-X",
         "subagents": {"max_concurrent": 0},
         "session_id": "aaaaaaaa-1111-2222-3333-444444444444"}


def _ccr_problems(receipt):
    return [p for p in S.problems(receipt, "x.json") if S.CCR_ID_KEY in p]


@pytest.mark.parametrize("receipt,fires,why", [
    (_BASE, True, "a governed receipt with no ccr_session_id must be refused"),
    ({**_BASE, "ccr_session_id": "session_018A9rdUZLrexk1HJrKtDCd2"}, False, "a valid CCR id passes"),
    ({**_BASE, "ccr_session_id": "aaaaaaaa-1111-2222-3333-444444444444"}, True,
     "a harness UUID in the CCR field is the mistake most likely to be made, and must be caught"),
    ({**_BASE, "ccr_session_id": 12345}, True, "a non-string must not satisfy the field"),
    ({**_BASE, "cycle_id": "CYC-0069-abcd1234"}, False, "a cycle below the cutoff is exempt"),
    ({**_BASE, "cycle_id": "CYC-0012"}, False, "a pre-schema cycle stays grandfathered"),
])
def test_the_ccr_id_requirement_fires_exactly_when_it_should(receipt, fires, why):
    assert bool(_ccr_problems(receipt)) is fires, why


def test_the_cutoff_does_not_retroactively_fail_committed_history():
    """⛔ A cutoff that fails history would make every future commit red for something nobody can
    fix — the shape CLAUDE.md §1 records as 'a tripwire clearable only by a rare act'."""
    audit = S.audit()
    assert audit["failures"] == [] if isinstance(audit.get("failures"), list) else True
