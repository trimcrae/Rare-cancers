"""A blind seat's record is its FIRST act, and an unfinished record may never count as a clean look.

⛔⛔ THE DEFECT (AUT-PROP-006, filed by CYC-0005). That cycle ran two blind seats, ACTED ON BOTH, and
PERSISTED NEITHER — so the manuscript carries their fixes while `publish_bar`'s convergence clause
still has nothing to read. ★ THE FAILURE IS ONE-DIRECTIONAL, WHICH IS WHY IT IS WORTH A MECHANISM:
the CHANGE survives a context loss and the EVIDENCE FOR IT DOES NOT. The 2026-09-01 sprint charter
§3 makes the same argument from the 107-agent fan-out, whose loss was not the 67 errors but the 40
successes that had nowhere to land and had to be recovered by hand out of `journal.jsonl`.

★ THE ORDER IS OPEN, LOOK, CLOSE. `seat_scratch.py --open-seat-record` writes an honest EMPTY record
before the seat reads a line; `--close-seat-record` merges the findings in. `close` refuses when
nothing was opened, so the write-first rule is a mechanism rather than an instruction — a rule whose
trigger nobody computes is a rule that never fires (CLAUDE.md §1, `subagent_width`).

⛔⛔ AND THE HALF THAT MAKES THE PROPOSAL SAFE RATHER THAN A NEW HOLE IN THE BAR. An open record is
honestly `blind: true` and honestly names the commit it is about to read, so every filter in
`publish_bar._seat_records` admits it — and a seat that DIED would be counted as a look that found
nothing. Writing the record first would turn every dead seat into a clean one. So
`clause_1_hardening_converged` REFUSES any round with an open record at the commit it is grading.
The coupling is asserted here, in the same file as the tool, because the two halves are only safe
together.

⛔ DIRECTION. Every assertion below is a REFUSAL the bar or the tool did not previously make. This
suite was written by a seat of a sprint the bar is blocking, and `amendment_guard` forbids loosening
a bar under exactly that pressure; nothing here lets a paper past anything.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent.parent
AUTONOMY = REPO / "research" / "autonomy"

SHA = "e" * 40
OTHER = "d" * 40


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, AUTONOMY / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def scratch():
    return _load("autonomy_seat_scratch_records", "seat_scratch.py")


@pytest.fixture()
def bar():
    return _load("autonomy_publish_bar_openseat", "publish_bar.py")


# ------------------------------------------------------------------ the tool: open, look, close

def test_the_record_exists_before_the_seat_reads_anything(scratch, tmp_path):
    """The whole proposal in one assertion: after `open`, and before the seat has looked at a word,
    there is a file on disk saying which paper, which commit and which lens."""
    path, findings = scratch.open_seat_record(str(tmp_path), "PUB-X", SHA, "regression",
                                              document="research/manuscripts/x.md",
                                              document_sha256="a" * 64)
    assert findings == [], findings
    record = json.loads(pathlib.Path(path).read_text())
    assert pathlib.Path(path).name == f"PUB-X-{SHA}-seat-regression.json"
    assert record["status"] == "open"
    assert record["reviewed_commit"] == SHA
    assert record["blind"] is True
    assert record["blockers"] == [] and record["p1s"] == []
    assert record["verdict"] is None, (
        "an open record must not carry a verdict — a seat that dies must leave evidence that it "
        "LOOKED, never evidence of a conclusion it never reached")


def test_the_filename_is_the_one_the_bar_counts_as_a_seat(scratch, bar):
    """⛔ THE `-seat-` SEGMENT IS LOAD-BEARING. `publish_bar._is_seat_file` separates a seat from a
    round roll-up on this prefix and nothing else (AUT-PD-193). A tool that wrote the record under
    any other name would file evidence the bar reads as a synthesis, or does not read at all."""
    name = pathlib.Path(scratch.seat_record_path("/seats", "PUB-X", SHA, "arithmetic")).name
    assert bar._is_seat_file("PUB-X", SHA, name) is True


def test_closing_a_record_nobody_opened_is_refused(scratch, tmp_path):
    """⛔ THIS REFUSAL *IS* THE WRITE-FIRST RULE. Without it the tool would be a convenience a seat
    in a hurry skips, which is what CYC-0005's two seats did to the prose version."""
    path, findings = scratch.close_seat_record(str(tmp_path), "PUB-X", SHA, "regression",
                                               {"verdict": "supported", "blockers": [], "p1s": []})
    assert [k for k, _, _ in findings] == ["NO-OPEN-RECORD"], findings
    assert not pathlib.Path(path).exists(), (
        "the refusal wrote the record anyway, so closing without opening still produces evidence "
        "of a look that was never registered")


def test_open_then_close_carries_the_findings_and_marks_it_complete(scratch, tmp_path):
    """⭐ THE POSITIVE CONTROL. Without it every refusal here would pass equally well on a tool
    broken into refusing everything."""
    scratch.open_seat_record(str(tmp_path), "PUB-X", SHA, "regression")
    path, findings = scratch.close_seat_record(
        str(tmp_path), "PUB-X", SHA, "regression",
        {"verdict": "supported", "central_claim": "the claim under test",
         "blockers": [], "p1s": ["a coverage gap"]})
    assert findings == [], findings
    record = json.loads(pathlib.Path(path).read_text())
    assert record["status"] == "complete"
    assert record["p1s"] == ["a coverage gap"]
    assert record["verdict"] == "supported"
    assert record["opened_utc"] and record["closed_utc"]


def test_a_closed_record_is_evidence_and_is_never_overwritten(scratch, tmp_path):
    """⛔ RE-OPENING A CLOSED SEAT WOULD ERASE ITS FINDINGS WITH AN EMPTY SHELL — worse than losing
    them, because the shell looks exactly like a seat that found nothing. `paper-hardening` §7d:
    a seat that died leaves a board that looks exactly like a seat that is thinking."""
    scratch.open_seat_record(str(tmp_path), "PUB-X", SHA, "regression")
    scratch.close_seat_record(str(tmp_path), "PUB-X", SHA, "regression",
                              {"verdict": "supported", "blockers": ["a real defect"], "p1s": []})
    path, findings = scratch.open_seat_record(str(tmp_path), "PUB-X", SHA, "regression")
    assert [k for k, _, _ in findings] == ["CLOSED"], findings
    assert json.loads(pathlib.Path(path).read_text())["blockers"] == ["a real defect"]

    _, findings = scratch.close_seat_record(str(tmp_path), "PUB-X", SHA, "regression",
                                            {"verdict": "supported", "blockers": [], "p1s": []})
    assert [k for k, _, _ in findings] == ["NOT-OPEN"], findings
    assert json.loads(pathlib.Path(path).read_text())["blockers"] == ["a real defect"]


def test_a_seat_cannot_relabel_which_commit_it_read(scratch, tmp_path):
    """⛔ THE OPEN RECORD FIXES THE CONTRACT BEFORE THE SEAT LOOKS. `paper-hardening` §3 pins a
    commit precisely so that a seat which hit tree drift cannot say afterwards which version its
    quotation came from; letting the close rewrite `reviewed_commit` would hand that back."""
    scratch.open_seat_record(str(tmp_path), "PUB-X", SHA, "regression")
    path, findings = scratch.close_seat_record(
        str(tmp_path), "PUB-X", SHA, "regression",
        {"reviewed_commit": OTHER, "verdict": "supported", "blockers": [], "p1s": []})
    assert [k for k, _, _ in findings] == ["CONTRADICTS-THE-OPEN-RECORD"], findings
    record = json.loads(pathlib.Path(path).read_text())
    assert record["reviewed_commit"] == SHA and record["status"] == "open"


def test_an_open_record_is_reported_as_open_not_as_absent(scratch, tmp_path):
    """CLAUDE.md §4 — an absent reading is not a reading of absence, and this is the driver's read
    before it believes a round."""
    assert scratch.open_seat_records(str(tmp_path), "PUB-X", SHA) == []
    scratch.open_seat_record(str(tmp_path), "PUB-X", SHA, "regression")
    got = scratch.open_seat_records(str(tmp_path), "PUB-X", SHA)
    assert [k for k, _, _ in got] == ["OPEN"], got
    scratch.close_seat_record(str(tmp_path), "PUB-X", SHA, "regression",
                              {"verdict": "supported", "blockers": [], "p1s": []})
    assert scratch.open_seat_records(str(tmp_path), "PUB-X", SHA) == []


# ------------------------------------------------------------------ the coupling, at the bar

def _stand_up(bar, tmp_path, monkeypatch, seat_records):
    hardening, seats = tmp_path / "h", tmp_path / "s"
    for d in (hardening, seats):
        d.mkdir(exist_ok=True)
    monkeypatch.setattr(bar, "HARDENING_DIR", hardening)
    monkeypatch.setattr(bar, "SEATS_DIR", seats)
    names = []
    for lens, extra in seat_records:
        name = f"PUB-X-{SHA}-seat-{lens}.json"
        record = {"blind": True, "reviewed_commit": SHA, "blockers": [], "p1s": []}
        record.update(extra)
        (seats / name).write_text(json.dumps(record))
        names.append(name)
    (hardening / "PUB-X.json").write_text(json.dumps({
        "blockers": [], "p1s": [], "reviewed_commit": SHA, "seats": names, "last_round": 9}))


def test_a_round_with_an_open_seat_record_is_refused(bar, tmp_path, monkeypatch):
    """⛔⛔ THE ONE THAT MAKES WRITE-FIRST SAFE. Four seats reported; the fifth opened its record and
    died. Every filter in `_seat_records` admits that fifth record — it is blind, it names this
    commit, and its `blockers`/`p1s` are honestly empty — so before this refusal existed the round
    read as FIVE looks that found nothing, and the dead seat was the one that made it look widest.

    ⚠ The empty tallies are not a lie and could not be fixed by writing the record differently: at
    the moment it is written, the seat has genuinely found nothing. The record is unfinished, not
    dishonest, and only the bar can tell the difference between the two.
    """
    _stand_up(bar, tmp_path, monkeypatch,
              [(f"lens{i}", {}) for i in range(4)] + [("lens4", {"status": "open"})])
    got = bar.clause_1_hardening_converged("PUB-X", SHA)
    assert got["ok"] is False and got["verdict"] == bar.FAIL, got
    assert "still open" in got["evidence"], got
    assert f"PUB-X-{SHA}-seat-lens4.json" in got["evidence"], (
        f"the refusal must name which seat is unfinished, or nobody can act on it: {got['evidence']}")


def test_a_round_whose_seats_all_closed_still_passes(bar, tmp_path, monkeypatch):
    """⭐ THE POSITIVE CONTROL FOR THE COUPLING. `status: complete` — the value the tool writes on
    close — must clear, and so must a record with no `status` at all, because every seat record
    committed before AUT-PROP-006 has none. A gate that reds on true input is worse than one that
    greens on false input (`paper-hardening` §8b.1): the first thing anyone does to it is loosen it,
    and here that would mean deleting the refusal above.
    """
    _stand_up(bar, tmp_path, monkeypatch,
              [("lens0", {}), ("lens1", {"status": "complete"}), ("lens2", {})])
    got = bar.clause_1_hardening_converged("PUB-X", SHA)
    assert got["ok"] is True, got
    assert "0 blockers across 3 blind seat(s)" in got["evidence"], got
