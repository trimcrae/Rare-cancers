#!/usr/bin/env python3
"""AUT-PD-166: the successor's prompt must describe `origin/main`, and must refuse to discard work.

⛔⛔ THE INCIDENT. `handoff.py`'s module docstring promised that "every fact here is read from a
committed artifact at build time: the queue from `research-ledger.json`". `build()` read that file
off DISK. On 2026-08-29 CYC-0079 filed a ledger row, built its handoff before pushing it, and handed
CYC-0080 a queue whose TOP ITEM — `AUT-PD-165`, score 134.0 — had never existed in any committed
copy of the ledger. `ids.next_entry_id` had already re-issued the id.

⭐ AND THE ROW CAME BACK, WHICH IS THE PART WORTH BEING PRECISE ABOUT. Forty minutes later that same
predecessor session returned and pushed it (origin/main 1684f79f9), so the content was not lost — and
the two rows then COLLIDED on the id, which is why this one is AUT-PD-166. ⛔ THAT IS LUCK, NOT A
MECHANISM: a handoff happens because a session is at its cap and its container is about to be
reclaimed, so the ordinary case is that it does NOT come back. The guard below assumes the ordinary
case.

⚠ AND THE SUCCESSOR WAS PRE-LOADED WITH THE WRONG DIAGNOSIS. The prompt's own stale-checkout
paragraph describes exactly this symptom ("its re-score produced a ledger in which the queue's top
item DID NOT EXIST") and attributes it to a detached HEAD. A successor that verifies HEAD against
`origin/main`, as that paragraph instructs, clears the named cause and is left with a symptom the
prompt says cannot happen — so it must either doubt its own verification or invent a third story.

★ WHAT THIS MUST CATCH, and the two halves fail differently on purpose:
  (1) a `build()` that goes back to reading the working tree — the prompt's provenance sentence
      becomes false again, and an unpushed row is offered to a session that cannot see it;
  (2) a `main()` that emits a prompt over unpushed rows — reading the trunk alone would have HIDDEN
      this incident rather than prevented it: the lost row simply stops being mentioned, and a
      silent omission leaves nothing for anyone to notice. The refusal is the half that saves work.

⛔ IT IS NOT ENOUGH TO ASSERT THE REFUSAL EXISTS. The escape hatch must still NAME what it drops
(a deliberate loss stays legible), and the fallback must not quietly re-acquire the original defect:
when the trunk cannot be read at all, the prompt has to SAY the working tree was used rather than
keep claiming committed provenance — CLAUDE.md §4, an absent reading is not a reading of absence.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import handoff as HF  # noqa: E402

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _cadence_is_not_this_suites_subject(monkeypatch):
    """⛔ HERMETICITY, ADDED 2026-08-29 WITH THE CADENCE GATE. `handoff.main` now ALSO refuses when a
    handoff would breach the cadence — a handoff CREATES A SESSION, and CYC-0088 spent $5.39 proving
    that a successor spawned minutes after its parent is a cadence event nobody was checking.

    That refusal reads the LIVE `autonomy-state.json`. Without this fixture every test below would
    grade the DIVERGENCE guard against whatever the budget governor currently says — the same defect
    the stuck-clock suite carried the same day, where four assertions got weaker every time a config
    file moved. This suite's subject is the divergence refusal alone.

    ⛔ THE CADENCE HALF IS NOT LEFT UNTESTED BY THIS: `test_a_handoff_is_a_cadence_event.py` owns it
    and is deliberately NOT neutralised there.
    """
    monkeypatch.setattr(HF, "cadence_verdict", lambda: (0, "cadence not under test in this suite", {}))



def _row(rid, score=100.0, **kw):
    r = {"id": rid, "kind": "process_defect", "state": "queued", "owner": None,
         "retry_budget": 3, "score": score, "what": f"row {rid}"}
    r.update(kw)
    return r


def _ledger(*rows):
    return {"entries": list(rows)}


# ---------------------------------------------------------------- the divergence detector

def test_a_row_only_in_the_working_tree_is_reported_lost():
    working = _ledger(_row("AUT-1"), _row("AUT-165"))
    trunk = _ledger(_row("AUT-1"))
    assert HF.unpushed_rows(working, trunk) == ["AUT-165"]


def test_a_row_on_the_trunk_and_not_on_disk_is_not_a_loss():
    """The successor CAN see it. Only the working-tree-only direction is work about to die."""
    working = _ledger(_row("AUT-1"))
    trunk = _ledger(_row("AUT-1"), _row("AUT-2"))
    assert HF.unpushed_rows(working, trunk) == []


def test_content_drift_alone_is_deliberately_not_a_loss():
    """⚠ NARROW ON PURPOSE. A re-scored derived field regenerates on the successor's own step 3; a
    row whose ID is absent cannot regenerate from anything. A check that fired on every re-score
    would be ignored within a week."""
    working = _ledger(_row("AUT-1", score=999.0))
    trunk = _ledger(_row("AUT-1", score=100.0))
    assert HF.unpushed_rows(working, trunk) == []


def test_an_unreadable_trunk_fails_open_rather_than_blocking_every_handoff():
    """A builder that cannot reach git must still hand off; `build` then says so in the prompt."""
    assert HF.unpushed_rows(_ledger(_row("AUT-1")), None) == []
    assert HF.unpushed_rows(None, _ledger(_row("AUT-1"))) == []


# ---------------------------------------------------------------- the prompt's provenance

def test_the_prompt_states_the_ref_it_was_built_from():
    p = HF.build("why", ledger=_ledger(_row("AUT-1")), state={})
    assert f"read from `{HF.TRUNK}` when this prompt was built" in p
    assert "read from the committed ledger when this prompt was built" not in p, (
        "the old wording named no ref, so it could not be checked against one")


def test_the_fallback_prompt_admits_the_working_tree_instead_of_claiming_the_trunk(monkeypatch):
    """⛔ THE FALLBACK IS WHERE THE DEFECT WOULD COME BACK. Reading disk is acceptable; reading disk
    under a committed-provenance heading is the original bug."""
    monkeypatch.setattr(HF, "_committed", lambda rel: (None, "fatal: not a git repository"))
    p = HF.build("why")
    assert "WORKING TREE" in p
    assert "fatal: not a git repository" in p
    assert f"read from `{HF.TRUNK}` when this prompt was built" not in p


def test_the_stale_checkout_warning_names_the_second_cause():
    """A warning that names one of two causes sends the next session after the wrong one."""
    p = HF.build("why", ledger=_ledger(_row("AUT-1")), state={})
    assert "STALE CHECKOUT IS ONLY ONE OF THE TWO CAUSES" in p


def test_a_deliberate_loss_is_named_in_the_prompt_it_survives_into():
    p = HF.build("why", ledger=_ledger(_row("AUT-1")), state={}, lost=["AUT-165"])
    assert "NOT HANDED OVER AND ALREADY LOST" in p
    assert "AUT-165" in p


def test_no_loss_block_appears_when_nothing_was_lost():
    p = HF.build("why", ledger=_ledger(_row("AUT-1")), state={}, lost=[])
    assert "NOT HANDED OVER AND ALREADY LOST" not in p


def test_the_named_receipts_are_the_ones_the_successor_will_find(monkeypatch):
    """⛔ THE SAME DEFECT ONE FILE OVER, AND IT NEEDS ITS OWN BINDING. The prompt tells the successor
    to READ these rather than ask what happened, so a receipt written and not pushed costs it its
    first act on a missing file. The disk here holds a name the trunk does not."""
    monkeypatch.setattr(HF, "committed_receipts", lambda n=3: (["CYC-0001-aaaa.json"], None))
    monkeypatch.setattr(HF, "RECEIPTS", pathlib.Path("/nonexistent-on-purpose"))
    assert HF.recent_receipts(3) == ["CYC-0001-aaaa.json"]


def test_receipts_fall_back_to_disk_only_when_the_trunk_cannot_be_read(monkeypatch, tmp_path):
    (tmp_path / "CYC-0002-bbbb.json").write_text("{}")
    monkeypatch.setattr(HF, "committed_receipts", lambda n=3: ([], "fatal: not a git repository"))
    monkeypatch.setattr(HF, "RECEIPTS", tmp_path)
    assert HF.recent_receipts(3) == ["CYC-0002-bbbb.json"]


# ---------------------------------------------------------------- the refusal

def _fake_trunk(monkeypatch, trunk_ledger, receipts_on_trunk=None):
    # ⛔ AUT-165 OUTSCORES AUT-1 DELIBERATELY. With equal scores a stable sort puts AUT-1 first
    # either way, so a mutant that read the working tree still produced the right answer and
    # SURVIVED — the fixture, not the code, was doing the passing. Found by mutation M6.
    monkeypatch.setattr(HF, "_read",
                        lambda p: (_ledger(_row("AUT-1"), _row("AUT-165", score=999.0)), None))
    monkeypatch.setattr(HF, "_committed", lambda rel: (trunk_ledger, None))
    monkeypatch.setattr(HF, "unpushed_receipt_files", lambda: list(receipts_on_trunk or []))
    monkeypatch.setattr(HF, "recent_receipts", lambda n=3: ["CYC-0000-aaaa.json"])
    monkeypatch.setattr(HF, "terminal_ids", lambda **kw: frozenset())


def test_main_refuses_to_build_a_handoff_that_would_discard_a_filed_row(monkeypatch, capsys):
    _fake_trunk(monkeypatch, _ledger(_row("AUT-1")))
    assert HF.main(["--reason", "x"]) == 3
    err = capsys.readouterr().err
    assert "REFUSED" in err and "AUT-165" in err
    assert "commit and push them" in err, "a refusal without its remedy is an obstacle, not a guard"


def test_main_refuses_over_an_unpushed_receipt_too(monkeypatch, capsys):
    """Same defect one file over: the prompt tells the successor to READ these receipts."""
    _fake_trunk(monkeypatch, _ledger(_row("AUT-1"), _row("AUT-165")),
                receipts_on_trunk=["CYC-0099-zzzz.json"])
    assert HF.main(["--reason", "x"]) == 3
    assert "CYC-0099-zzzz.json" in capsys.readouterr().err


def test_the_escape_emits_the_prompt_and_names_what_it_drops(monkeypatch, capsys):
    _fake_trunk(monkeypatch, _ledger(_row("AUT-1")))
    assert HF.main(["--reason", "x", "--allow-divergence"]) == 0
    out = capsys.readouterr().out
    assert "NOT HANDED OVER AND ALREADY LOST" in out and "AUT-165" in out


def test_a_clean_tree_hands_off_without_complaint(monkeypatch, capsys):
    _fake_trunk(monkeypatch, _ledger(_row("AUT-1"), _row("AUT-165")))
    assert HF.main(["--reason", "x"]) == 0
    assert "REFUSED" not in capsys.readouterr().err


def test_the_handed_queue_comes_from_the_trunk_not_from_disk(monkeypatch, capsys):
    """⛔ THE INCIDENT ITSELF. The working tree holds AUT-165; the trunk does not. Even on the escape
    path — the only path that emits at all here — it must not be offered as takeable work."""
    _fake_trunk(monkeypatch, _ledger(_row("AUT-1")))
    HF.main(["--reason", "x", "--allow-divergence"])
    out = capsys.readouterr().out
    assert "AUT-165  score" not in out, "an unpushed row was handed over as takeable work"
    assert "AUT-1  score" in out


def test_the_json_payloads_focus_title_also_comes_from_the_trunk(monkeypatch, capsys):
    """⛔ FOUND BY MUTATION, NOT BY DESIGN — the `--json` branch re-reads the ledger to name the
    session, and a fallback to disk there titles the successor's session after a row that does not
    exist. That is precisely how this session came to be called "cycle (AUT-PD-165)" for an id the
    trunk had never carried: the title is the first thing anyone reads about a cycle."""
    _fake_trunk(monkeypatch, _ledger(_row("AUT-1")))
    assert HF.main(["--reason", "x", "--allow-divergence", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["title"] == "EMC research loop — cycle (AUT-1)"
    assert "AUT-165" not in payload["title"]
