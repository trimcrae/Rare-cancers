#!/usr/bin/env python3
"""The ledger has ONE serialization, and every writer is forced through it (AUT-PD-037).

⛔⛔ THE DEFECT: nothing pinned how `research-ledger.json` gets written to disk, so every writer
invented its own parameters. A driver's hand-writes used `json.dumps(d, indent=1)`; the file's own
documented "generator", `priority.py`, wrote `json.dump(ledger, fh, indent=2)` — `ensure_ascii`
DEFAULTS TO TRUE, so that call escapes every ⛔ ⭐ ⚠ ★ and em-dash the moment it runs after any
writer that left `ensure_ascii=False`. Measured 2026-08-27: neither matched what was actually
committed, and the mismatch turned a semantically five-row-vs-one-row delta into a rebase conflict
spanning the whole file, lines 2-9340.

⭐ THE FIX IS `research/autonomy/ledger_io.py`'s `write_ledger()`, ONE HOME FOR THE SERIALIZATION —
not a comment telling writers what to type, which is exactly the class of agreement-in-prose this
repository keeps re-discovering the cost of (AUT-PD-013's fan-out key, AUT-PROP-013's ids). This
suite is what makes that real:

  1. `write_ledger`'s output is byte-identical to the actually-committed file — pins the parameters
     to what was already the de facto standard, not a fresh preference.
  2. the parameters matter and are not vacuously satisfied — `json.dump`'s *default* `ensure_ascii`
     produces different bytes on the same payload, reproducing the exact regression by hand.
  3. `priority.py --write` and `claim.py apply_claim` both actually CALL `write_ledger` rather than
     re-implementing the serialization next to it — the two real writers this defect was filed
     against. A test that only checked (1) would go on passing forever if either one quietly went
     back to typing `json.dump(..., indent=2)` itself.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
sys.path.insert(0, AUTONOMY)

import claim as C  # noqa: E402
import ledger_io  # noqa: E402
import priority as P  # noqa: E402

LEDGER = os.path.join(AUTONOMY, "research-ledger.json")


# ---------------------------------------------------------------------------------------------
# (1) The canonical parameters, read from what is already committed — never invented.
# ---------------------------------------------------------------------------------------------

def test_write_ledger_reproduces_the_committed_file_byte_for_byte():
    """⛔⛔ THE GUARD. If `ledger_io`'s pinned `indent`/`ensure_ascii` ever drift from what this
    repository actually commits, this fails — which is the only thing that makes the convention
    real rather than a docstring nobody checks."""
    with open(LEDGER, "rb") as fh:
        raw = fh.read()
    with open(LEDGER, encoding="utf-8") as fh:
        data = json.load(fh)
    assert ledger_io.dumps_ledger(data).encode("utf-8") == raw, (
        "write_ledger()'s canonical serialization no longer matches the committed ledger byte for "
        "byte. Either the pinned parameters drifted from the real convention, or something wrote "
        "the committed file with different ones — in both cases the whole-file-diff defect is back.")


def test_the_committed_ledger_still_has_the_unicode_that_makes_this_matter():
    """★ A POSITIVE CONTROL. If nobody ever writes ⛔/⭐/⚠/★/— into this file again, an `ensure_ascii`
    regression would round-trip clean by accident and every test below would pass for the wrong
    reason — exactly the "vacuous mutation" trap AUT-PROP-007 already found once in this program."""
    with open(LEDGER, "rb") as fh:
        raw = fh.read()
    assert any(marker.encode("utf-8") in raw for marker in ("⛔", "⭐", "⚠", "★", "—")), (
        "the committed ledger carries no non-ASCII markers any more, so this suite cannot actually "
        "discriminate ensure_ascii=True from ensure_ascii=False")


# ---------------------------------------------------------------------------------------------
# (2) The parameters are not vacuous: json.dump's default really does produce different bytes.
# ---------------------------------------------------------------------------------------------

def test_pythons_own_default_would_have_escaped_the_unicode():
    """⛔⛔ THE REGRESSION, REPRODUCED DIRECTLY. This is `priority.py`'s old call — `json.dump(data,
    fh, indent=2)` with no `ensure_ascii` — applied to a payload shaped like a real ledger entry. It
    must NOT match `write_ledger`'s output, or this whole suite is protecting against a difference
    that does not exist."""
    payload = {"entries": [{"id": "AUT-PD-999", "what": "⛔⛔ a real marker, an em-dash — and one more ⭐"}]}
    default_json_dump = json.dumps(payload, indent=2) + "\n"  # ensure_ascii defaults to True here
    canonical = ledger_io.dumps_ledger(payload)
    assert default_json_dump != canonical, (
        "json.dumps with no ensure_ascii argument produced the same bytes as write_ledger — the "
        "positive control for this entire suite is broken")
    assert "\\u26d4" in default_json_dump or "\\u" in default_json_dump, (
        "expected the ASCII-default call to escape a non-ASCII marker as \\uXXXX")
    assert "\\u" not in canonical, "write_ledger's own output must never escape non-ASCII text"


def test_one_space_indent_would_also_have_failed_the_guard():
    """⚠ THE OTHER HALF OF THE INCIDENT. The driver's ad hoc hand-writes used `indent=1`, not the
    ensure_ascii default — a different wrong parameter, same failure mode (a whole-file diff)."""
    payload = {"entries": [{"id": "AUT-PD-999", "what": "x"}]}
    one_space = json.dumps(payload, indent=1, ensure_ascii=False) + "\n"
    assert one_space != ledger_io.dumps_ledger(payload)


# ---------------------------------------------------------------------------------------------
# (3) The real writers actually call write_ledger — not a look-alike that types the params again.
# ---------------------------------------------------------------------------------------------

def test_priority_write_calls_the_shared_serializer(tmp_path, monkeypatch):
    """⛔⛔ THE EXACT SITE THE LEDGER ENTRY NAMED: `priority.py:591-593` used to call `json.dump`
    itself. This fails if `--write` is ever changed back to serializing inline instead of going
    through `ledger_io.write_ledger` — even if someone got the inline parameters right, because a
    second correct-by-hand call site is exactly how this defect happened the first time (claim.py's
    own hand-typed `indent=2, ensure_ascii=False` sat right next to priority.py's wrong one)."""
    calls = []
    monkeypatch.setattr(ledger_io, "write_ledger", lambda path, data: calls.append((path, data)))
    fake_ledger_file = tmp_path / "research-ledger.json"
    monkeypatch.setattr(P, "LEDGER_FILE", fake_ledger_file)
    monkeypatch.setattr(P, "REPO", tmp_path)
    monkeypatch.setattr(P, "build_ledger",
                        lambda: {"entries": [], "n_clamped": 0, "n_by_kind": {}})

    rc = P.main(["--write"])

    assert rc == 0
    assert calls, ("priority.py --write returned 0 without calling ledger_io.write_ledger — it is "
                   "writing the file some other way again")
    assert calls[0][0] == fake_ledger_file
    assert not fake_ledger_file.exists(), (
        "the monkeypatched write_ledger was bypassed and the real file write happened anyway")


def test_priority_write_does_not_call_json_dump_on_the_ledger_directly(tmp_path, monkeypatch):
    """★ THE COMPLEMENT OF THE TEST ABOVE. Patching `write_ledger` to a no-op and then asserting
    nothing appears at the destination path closes the loophole where `--write` calls the shared
    function AND still writes the file itself with the old parameters."""
    monkeypatch.setattr(ledger_io, "write_ledger", lambda path, data: None)
    fake_ledger_file = tmp_path / "research-ledger.json"
    monkeypatch.setattr(P, "LEDGER_FILE", fake_ledger_file)
    monkeypatch.setattr(P, "REPO", tmp_path)
    monkeypatch.setattr(P, "build_ledger",
                        lambda: {"entries": [], "n_clamped": 0, "n_by_kind": {}})

    rc = P.main(["--write"])

    assert rc == 0
    assert not fake_ledger_file.exists(), (
        "research-ledger.json was written even though ledger_io.write_ledger was a no-op — "
        "priority.py is still serializing it a second way on the side")


def test_claim_apply_claim_calls_the_shared_serializer(tmp_path, monkeypatch):
    """⛔ THE SECOND WRITER. `apply_claim` already hand-typed the right parameters, which is exactly
    why the entry warns that a docstring saying 'use indent=2' is not a fix — a call site can be
    correct today and drift tomorrow with nothing to stop it. This pins that it goes through the
    shared function, not that its inline parameters happen to agree with it."""
    calls = []
    monkeypatch.setattr(C, "ledger_io", type("_", (), {"write_ledger": staticmethod(
        lambda path, data: calls.append((path, data)))})())

    ledger_path = tmp_path / "research-ledger.json"
    ledger_path.write_text(json.dumps({"entries": [{"id": "AUT-X-1", "owner": None}]}), encoding="utf-8")

    C.apply_claim(str(ledger_path), "AUT-X-1", "me", "2026-08-28T00:00:00Z")

    assert calls, "claim.py's apply_claim did not call ledger_io.write_ledger"
    assert calls[0][0] == str(ledger_path)
    assert calls[0][1]["entries"][0]["owner"] == "me"


def test_claim_apply_claim_produces_the_canonical_bytes_end_to_end(tmp_path):
    """⭐ NO MOCKING — the real function, the real filesystem, checked against `dumps_ledger`
    directly. This is the one that would have caught the incident: a real claim write whose bytes
    differ from what any other real writer produces is the whole-file diff, reproduced."""
    ledger_path = tmp_path / "research-ledger.json"
    before = {"entries": [{"id": "AUT-X-1", "owner": None, "what": "⛔ a real marker — kept as is"}]}
    ledger_path.write_text(ledger_io.dumps_ledger(before), encoding="utf-8")

    C.apply_claim(str(ledger_path), "AUT-X-1", "me", "2026-08-28T00:00:00Z")

    after = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert after["entries"][0]["owner"] == "me"
    assert ledger_path.read_bytes() == ledger_io.dumps_ledger(after).encode("utf-8"), (
        "apply_claim wrote bytes that do not match this repository's one canonical serialization")


# ---------------------------------------------------------------------------------------------
# The committed file itself: no duplicate ids, still loads, still the shape both writers expect.
# ---------------------------------------------------------------------------------------------

def test_the_committed_ledger_still_round_trips_through_json():
    """A basic sanity check that the re-serialization performed for this fix (if any) did not
    corrupt content — `json.load` must recover the identical structure either way."""
    with open(LEDGER, encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, dict) and "entries" in data and isinstance(data["entries"], list)
    assert len(data["entries"]) > 0
