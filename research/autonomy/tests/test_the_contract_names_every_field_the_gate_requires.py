"""The cycle contract must name every receipt field `receipt_schema.py` refuses a receipt for.

⛔⛔ WHY THIS EXISTS (AUT-PD-146, 2026-08-29). `receipt_schema.py` fails the commit of any receipt
from `FIRST_CCR_GOVERNED_CYCLE` onward that omits `ccr_session_id`. `.claude/skills/research-loop`
§2 step 10 — the text a cycle actually follows when it hand-authors that receipt — did not name the
field, nor say how to obtain it. **A cycle that followed the contract exactly wrote a receipt the
commit gate refused**, and found out only from a red build. CYC-0073-d4ccfde4 hit it and complied
only because it had opened `receipt_schema.py` for an unrelated reason: compliance by luck, which is
the same finding CLAUDE.md §1 records about `subagent_width` governing nothing for a fortnight.

⭐ AND THE ONE-SENTENCE FIX WOULD HAVE BEEN THE FOURTH SUCH SENTENCE. This repository has lost the
same writer/reader agreement four separate times — AUT-PD-013's `subagents.max_concurrent` (three
spellings in seventeen receipts), AUT-PROP-013's receipt ids, AUT-PD-037's ledger serialization, and
this one. `receipt_schema.py`'s own docstring states the lesson: *a field name agreed in PROSE
between a writer and a reader is not agreed at all — it is a hope, checked by nothing.* So this
suite pins the MECHANISM, not the sentence.

★ WHAT IS PINNED, AND WHY EACH PROPERTY IS HERE RATHER THAN LEFT TO THE `--check` EXIT CODE:
  1. the required set is DERIVED from the enforcer's behaviour, not listed — a list would be the
     same prose agreement one file over;
  2. it is NON-EMPTY and contains the fields whose absence is known to fail — a checker whose
     derivation silently collapsed to nothing would pass forever, which is the exact vacuous-green
     failure mode the module was written against;
  3. the fixtures still comply, which is the FAIL-CLOSED half: a new requirement in
     `receipt_schema.py` reds the build on the commit that adds it;
  4. every field name lives in a `*_KEY` constant, without which the constants direction is
     incomplete and a conditional requirement could hide in a string literal;
  5. an unreadable or renamed contract REFUSES rather than passes;
  6. the positive control — the guard still catches the exact 2026-08-29 defect when it is
     reintroduced into a copy of the contract. ⚠ Without (6) this file passes just as well on a
     matcher that matches nothing, which is what it was written to prevent in something else.
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import contract_check as C  # noqa: E402
import receipt_schema as S  # noqa: E402


# ---------------------------------------------------------------- the derivation is real

def test_the_required_set_is_derived_and_not_empty():
    """A derivation that collapsed to the empty set would pass every contract ever written."""
    required = C.required_paths()
    assert required, (
        "contract_check derived NO required fields from receipt_schema. A checker with an empty "
        "requirement set is vacuously green against any contract — including one that names "
        "nothing at all.")


@pytest.mark.parametrize("path", [
    ("route_advanced",),
    ("ccr_session_id",),
    ("subagents",),
    ("subagents", "max_concurrent"),
])
def test_each_field_the_gate_actually_refuses_is_in_the_derived_set(path):
    """⛔ Named explicitly, because the derivation must agree with the enforcer's real behaviour.

    Each of these is a field whose omission makes `problems()` complain today. If the derivation
    stops finding one, the contract could drop the name with nothing noticing.
    """
    assert path in C.required_paths(), f"`{'.'.join(path)}` is no longer derived as required"


def test_the_fixtures_still_comply_with_the_enforcer():
    """⭐ THE FAIL-CLOSED HALF, and the reason the derived set cannot go stale.

    A new requirement in `receipt_schema.py` makes every fixture non-compliant, so the build goes
    red on the commit that ADDS the requirement rather than on the cycle that later trips over it.
    The remedy is to add the field to `_fixtures()` — at which point the checker starts demanding
    the contract name it, which is the whole point.
    """
    assert C.fixtures_still_comply() == []


def test_the_fixtures_span_every_condition_the_enforcer_branches_on():
    """⛔ DIRECTION A IS ONLY AS COMPLETE AS THE FIXTURES, so the coverage is an assertion.

    ⚠ ADDED BECAUSE TWO MUTANTS SURVIVED THE FIRST PASS (2026-08-29). Dropping every CCR-governed
    fixture, and dropping the only fixture that records a non-zero fan-out, both left all 22 tests
    green — the first because `ccr_session_id` then stops being derived at all, the second because
    no requirement hangs off that branch TODAY. Neither is a bug in the checker; both silently
    remove the coverage that would catch the NEXT requirement, which is the one this file is for.
    `problems()` branches on the cycle number (the CCR cutoff) and on the recorded width, so both
    sides of both must be present.
    """
    seen = [(S.cycle_number(r[S.CYCLE_ID_KEY]), r[S.BLOCK_KEY][S.WIDTH_KEY])
            for _, r in C._fixtures()]
    assert any(n < S.FIRST_CCR_GOVERNED_CYCLE for n, _ in seen), "no pre-CCR-cutoff fixture"
    assert any(n >= S.FIRST_CCR_GOVERNED_CYCLE for n, _ in seen), "no CCR-governed fixture"
    assert any(w == 0 for _, w in seen), "no fixture records a fan-out of 0 — the case the contract "\
        "insists on for a cycle that spawned nobody"
    assert any(w > 0 for _, w in seen), "no fixture records a fan-out greater than 0"


def test_a_fixture_the_enforcer_rejects_is_reported(monkeypatch):
    """⛔ THE FAIL-CLOSED PROPERTY ITSELF, not just its current happy value.

    `fixtures_still_comply() == []` passes just as well on a function that returns `[]`
    unconditionally — mutation M11. This feeds it a fixture the enforcer really does reject and
    requires both the function AND `audit()` to say so, which is what makes a new requirement in
    `receipt_schema.py` red the build instead of reaching a cycle.
    """
    broken = [("CYC-9999-mutant.json", {S.CYCLE_ID_KEY: "CYC-9999-mutant"})]
    monkeypatch.setattr(C, "_fixtures", lambda: broken)
    reported = C.fixtures_still_comply()
    assert reported, "a fixture the enforcer rejects must be reported, never silently accepted"
    assert any("_fixtures" in line for line in reported), (
        "the report must name the remedy — adding the field to `_fixtures()` — or the next reader "
        "goes looking in receipt_schema for a bug that is not there")
    assert C.audit()["failures"], "audit() must surface a non-complying fixture"


def test_no_field_name_is_spelled_outside_a_constant():
    """Without this the `*_KEY` enumeration is merely probably complete."""
    assert C.no_literal_key_lookups() == []


def test_every_key_constant_is_a_field_the_contract_names():
    spelled = C.names(C.step_text())
    missing = {n: v for n, v in C.key_constants().items() if v not in spelled}
    assert not missing, (
        "receipt_schema names these receipt fields that §2 step 10 never spells: " + repr(missing))


# ---------------------------------------------------------------- the whole check, end to end

def test_the_contract_and_the_gate_agree_on_the_trunk():
    r = C.audit()
    assert r["failures"] == [], "\n".join(r["failures"])


def test_audit_reads_the_derived_required_set(monkeypatch):
    """⛔ WIRING, PINNED SEPARATELY FROM THE DERIVATION.

    `required_paths()` can be perfect and still be ignored by `audit()`, which is what preflight
    calls. Mutation M9 — deleting the direction-A loop from `audit` — survived the first pass
    precisely because every derived field is ALSO a `*_KEY` constant today, so direction B masked
    its removal. This kills it without relying on that overlap.
    """
    monkeypatch.setattr(C, "required_paths", lambda: [("no_such_field_xyz",)])
    failures = C.audit()["failures"]
    assert any("no_such_field_xyz" in f for f in failures), (
        "audit() no longer checks the derived required set against the contract")


def test_audit_reads_the_key_constants(monkeypatch):
    """The same wiring pin for direction B — the backstop for a requirement no fixture exercises."""
    monkeypatch.setattr(C, "key_constants", lambda: {"BOGUS_KEY": "no_such_constant_xyz"})
    failures = C.audit()["failures"]
    assert any("no_such_constant_xyz" in f for f in failures), (
        "audit() no longer checks receipt_schema's key constants against the contract")


def test_a_documented_but_unforced_field_is_still_required_to_be_named(tmp_path):
    """⭐ THE ONE PLACE THE TWO DIRECTIONS DIVERGE, AND THE REASON B IS NOT REDUNDANT.

    `cycle_id` is a `*_KEY` constant the enforcer reads, but deleting it from a receipt changes no
    verdict — `problems()` falls back to the filename — so direction A does NOT derive it. Only
    direction B demands the contract name it. A contract that drops it must therefore still fail.
    """
    body = open(C.CONTRACT, encoding="utf-8").read().replace(S.CYCLE_ID_KEY, "«removed»")
    q = tmp_path / "no_cycle_id.md"
    q.write_text(body, encoding="utf-8")
    assert ("cycle_id",) not in C.required_paths(), (
        "cycle_id is now derived as required; this test's premise has changed — re-derive it")
    failures = C.audit(str(q))["failures"]
    assert any(S.CYCLE_ID_KEY in f for f in failures), (
        "a field the enforcer reads but does not enforce may still be dropped from the contract "
        "unnoticed — direction B has stopped working")


def test_a_string_literal_key_in_the_enforcer_is_refused(tmp_path, monkeypatch):
    """The completeness premise of direction B, checked on a COPY rather than by trusting it."""
    mutant = tmp_path / "mutant_schema.py"
    mutant.write_text(
        "CYCLE_ID_KEY = 'cycle_id'\n"
        "def problems(receipt, path):\n"
        "    return receipt.get('sneaky_field'), receipt['other_field']\n", encoding="utf-8")

    class _Stub:
        __file__ = str(mutant)
    monkeypatch.setattr(C, "S", _Stub)
    found = " ".join(C.no_literal_key_lookups())
    assert "sneaky_field" in found and "other_field" in found, (
        "a field name spelled as a string literal is invisible to the constants enumeration and "
        "must be refused; neither `.get()` nor subscript form may slip through")


def test_the_enforcers_own_tables_are_not_mistaken_for_receipt_fields(tmp_path, monkeypatch):
    """⚠ A linter that flags true statements gets turned off (lint_claims.py's founding lesson).

    `DRIFTED_KEYS[k]["remedy"]` reads a module table and `r["failures"]` reads `audit`'s own result
    dict; neither is a receipt, and flagging them would make this check noise. ⚠ The first version of
    the rule DID flag the second one — nine times — so the pin here is that the rule stays structural
    (only a function's own PARAMETER is a receipt) rather than becoming an exemption list.
    """
    clean = tmp_path / "clean_schema.py"
    clean.write_text(
        "TABLE = {'a': {'remedy': 'x'}}\n"
        "import os\n"
        "def audit(k):\n"
        "    r = {'failures': []}\n"
        "    return TABLE[k]['remedy'], os.environ.get('HOME'), r['failures']\n",
        encoding="utf-8")

    class _Stub:
        __file__ = str(clean)
    monkeypatch.setattr(C, "S", _Stub)
    assert C.no_literal_key_lookups() == []


def test_step_10_still_names_how_to_obtain_the_ccr_id():
    """⚠ THE HONEST LIMIT OF THIS FILE, PINNED AS FAR AS IT CAN BE.

    The mechanism can prove the contract NAMES a field; it cannot prove what the contract says
    about it is true. The one substantive instruction — that the value is read from `get_session`
    rather than typed — is therefore pinned by its two identifying tokens, so deleting the
    instruction is a failing test even though rewriting it badly is not.
    """
    text = C.step_text()
    assert "get_session" in text and "ccr.id" in text, (
        "step 10 names `ccr_session_id` but no longer says how to obtain it. A required field with "
        "no stated source is how the literal 'scheduled-routine-session' got typed into `session_id` "
        "nine cycles running.")


def test_the_two_id_spaces_are_still_described_as_distinct():
    """AUT-PD-124's whole subject: the tempting fix is to collapse them, and it is wrong."""
    text = C.step_text()
    assert "CLAUDE_CODE_SESSION_ID" in text and S.CCR_ID_KEY in text, (
        "step 10 must name BOTH ids: `session_id` is the harness UUID that health.py and "
        "session_cap.py key on; `ccr_session_id` is the id the session list speaks and the only "
        "one session_reaper.py can join on.")


# ---------------------------------------------------------------- fail closed, and the control

def test_a_contract_that_cannot_be_read_refuses(tmp_path):
    missing = tmp_path / "nope.md"
    with pytest.raises(C.ContractUnreadable):
        C.step_text(str(missing))
    assert C.audit(str(missing))["failures"], "an unreadable contract must FAIL, never pass"


def test_a_renamed_step_refuses_rather_than_matching_the_wrong_one(tmp_path):
    """⛔ Anchoring on the number `10.` would silently read the wrong step once one is inserted."""
    body = open(C.CONTRACT, encoding="utf-8").read().replace(C.STEP_ANCHOR, "Compose the record")
    p = tmp_path / "renamed.md"
    p.write_text(body, encoding="utf-8")
    with pytest.raises(C.ContractUnreadable):
        C.step_text(str(p))


def test_a_stub_step_refuses_rather_than_checking_near_empty_text(tmp_path):
    p = tmp_path / "stub.md"
    p.write_text(f"1. **{C.STEP_ANCHOR}** — see the code.\n2. **Next**\n", encoding="utf-8")
    with pytest.raises(C.ContractUnreadable):
        C.step_text(str(p))


def test_the_guard_catches_the_2026_08_29_defect_when_it_is_reintroduced(tmp_path):
    """★ THE POSITIVE CONTROL. Strip every mention of `ccr_session_id` from a COPY of the contract
    — the state the trunk was actually in — and the checker must go red naming that field."""
    body = open(C.CONTRACT, encoding="utf-8").read().replace(S.CCR_ID_KEY, "«removed»")
    p = tmp_path / "pre_fix.md"
    p.write_text(body, encoding="utf-8")
    failures = C.audit(str(p))["failures"]
    assert failures, "the pre-2026-08-29 contract must not pass"
    assert any(S.CCR_ID_KEY in f for f in failures), (
        "the failure must NAME the missing field; a checker that says only 'disagreement' sends the "
        "reader back to the code it exists to save them from")


def test_the_step_boundary_stops_at_the_next_numbered_step():
    """The extracted step must be step 10 alone — not the rest of the file, which would make the
    check pass on any field named anywhere in the skill."""
    text = C.step_text()
    assert C.STEP_ANCHOR in text
    assert "Reap the finished sessions" not in text, (
        "the extractor ran past step 10 into step 11; a boundary that swallows the file makes "
        "every name look documented")
