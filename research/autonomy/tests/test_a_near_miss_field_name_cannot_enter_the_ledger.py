#!/usr/bin/env python3
"""A ledger field name one edit from a real one is a typo, not a new field (AUT-PD-030).

⛔⛔ THE DEFECT, REPRODUCED BEFORE IT WAS FIXED. Every row in `research-ledger.json` is hand-authored
JSON and several readers key off exact field names; no whitelist existed anywhere. On a scratch COPY
of the committed ledger (never the live file), a row was appended whose `what` names no outward verb
and which carries `require_trimcrae: true` — one deletion from `requires_trimcrae`, the field
CLAUDE.md §3 exists to protect. Against that copy:

    continuity.ready()                 -> offers the row as READY TO RUN
    continuity.unclassified_outward()  -> does NOT flag it (the rescue is a regex over `what`)
    prepush_ledger_guard.py            -> exit 0, silent (it checks duplicate ids only)

`test_the_sharpest_edge_is_reproduced_and_then_refused` is that reproduction, run against the schema
so it fails on any tree where the schema stops catching it.

⭐ WHAT THIS SUITE IS ACTUALLY FOR, since the schema's vocabulary is a snapshot of the committed
ledger and would otherwise pass itself trivially:
  1. the sharpest edge is refused, and refused for the reason given (the message names the reader);
  2. every committed field name is run back through the detectors AS IF UNKNOWN, so the snapshot
     cannot silently bless a near-miss it inherited — this is what found `_closed_by` and `_outcome`;
  3. a genuinely NEW field far from every governed name is ALLOWED without registration, which is
     the half of the design that keeps the gate from being switched off;
  4. `ledger_io.write_ledger` actually calls the schema, so the binding cannot rot the way the
     serialization did before AUT-PD-037.
"""

from __future__ import annotations

import copy
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.abspath(os.path.join(HERE, ".."))
LEDGER = os.path.join(AUTONOMY, "research-ledger.json")
sys.path.insert(0, AUTONOMY)

import ledger_schema  # noqa: E402
import ledger_io  # noqa: E402


@pytest.fixture(scope="module")
def ledger():
    with open(LEDGER, encoding="utf-8") as fh:
        return json.load(fh)


def test_the_committed_ledger_passes_the_schema(ledger):
    """The gate is turned on green. A gate that lands red is a gate somebody switches off."""
    assert ledger_schema.problems(ledger) == []


def test_the_sharpest_edge_is_reproduced_and_then_refused():
    """`require_trimcrae` — one deletion — must be refused, and the message must name the reader.

    ⛔ THE ASSERTION IS NOT MERELY "it fails". A refusal that says `unknown field` teaches the reader
    nothing and gets read as noise; CLAUDE.md §4 wants the observation that discriminates, so the
    message has to say WHICH governed field this is a near-miss of and WHO reads it.
    """
    row = {"id": "AUT-PD-999", "kind": "process_defect", "state": "queued",
           "what": "Regenerate the route-expression grading table and refresh the derived counts.",
           "require_trimcrae": True}
    found = ledger_schema.field_problems(row)
    assert len(found) == 1, found
    assert "require_trimcrae" in found[0]
    assert "requires_trimcrae" in found[0]
    assert "continuity" in found[0]


@pytest.mark.parametrize("typo,governed", [
    ("require_trimcrae", "requires_trimcrae"),      # a deletion
    ("requires_trimcrea", "requires_trimcrae"),     # a transposition
    ("_requires_trimcrae", "requires_trimcrae"),    # the `_`-commentary spelling on a read field
    ("requiresTrimcrae", "requires_trimcrae"),      # camelCase
    ("trimcrae_requires", "requires_trimcrae"),     # reordered tokens
    ("owned_by", "owner"),                          # ⛔ AUT-PD-030's own worked example: FOUR edits
    ("blockedBy", "blocked_by"),                    # from `owner`, reachable only by the stem rule
    ("blocked_evidenc", "blocked_evidence"),
    ("notified_utd", "notified_utc"),               # the escalation hook's falsifiable send record
    ("closes_clauses", "closes_clause"),
    ("claim_worker", "claim_workers"),
    ("retry_budgets", "retry_budget"),
])
def test_a_near_miss_of_a_read_field_is_refused(typo, governed):
    hits = dict(ledger_schema.near_misses(typo, ledger_schema.GOVERNED_FIELDS))
    assert governed in hits, f"{typo} slipped past every detector: {hits}"


@pytest.mark.parametrize("new_field", [
    "blocked_since", "review_round", "gpu_hours", "aixiv_version", "seat", "wave",
    "expected_finish_utc", "subagent_seat", "_sprint_2026_09_01", "_S10_note",
])
def test_a_genuinely_new_field_needs_no_registration(new_field):
    """⭐ THE OTHER HALF OF THE DESIGN. A schema that refuses every unknown field breaks the next
    legitimate one and gets switched off — so a name that looks like nothing already read must pass
    with no edit to `ledger_schema.py` at all."""
    assert ledger_schema.near_misses(new_field, ledger_schema.GOVERNED_FIELDS) == []


def test_no_committed_field_name_is_a_near_miss_of_a_governed_one(ledger):
    """⛔ THE ANTI-CIRCULARITY TEST. The vocabulary was read off the committed ledger, so it passes
    itself by construction. This runs every committed name back through the detectors as if it were
    unknown; anything that fires is a near-miss the snapshot would otherwise have blessed.

    ⚠ `LIVE_ALIASES` is the two that DID fire and could not be fixed in the same change (the ledger
    is off-limits to a sprint seat — AUT-PD-171's id allocator collides across concurrent writers).
    They are grandfathered by NAME, so the set can only shrink: a third drifted spelling fails here.
    """
    observed = {k for e in ledger["entries"] if isinstance(e, dict) for k in e}
    fired = {}
    for name in sorted(observed):
        if name in ledger_schema.GOVERNED_FIELDS:
            continue
        hits = ledger_schema.near_misses(name, ledger_schema.GOVERNED_FIELDS)
        if hits:
            fired[name] = hits
    unexpected = {k: v for k, v in fired.items()
                  if k not in ledger_schema.LIVE_ALIASES and k not in _DISMISSED}
    assert unexpected == {}, (
        "a committed field name is a near-miss of a field some reader keys off, and it is not in "
        f"LIVE_ALIASES: {unexpected}")


#: ⭐ NAMED, NOT INFERRED. `_CLOSED_2026_09_01` trips the stem rule against `closes_clause`
#: (`closed` is one edit from `closes`) and is plainly a dated one-off note rather than a
#: misspelling of it — a real false positive of the stem detector, which is the price of reaching
#: `owned_by`/`owner`. It is dismissed HERE, by name and with the reason, rather than by a
#: heuristic predicate that would quietly dismiss the next one too.
_DISMISSED = {"_CLOSED_2026_09_01"}


def test_a_live_alias_is_reported_rather_than_hidden(ledger):
    """⛔ receipt_schema.py's precedent, applied: the item that commissioned this module was filed
    against a checker that HID what it could not read, so drift must be PRINTED rather than buried in
    the descriptive vocabulary.

    ⭐⭐ RENAMED AND REPOINTED 2026-09-01, BECAUSE THE DRIFT IT PINNED IS REPAIRED. This was
    `test_the_two_live_aliases_are_reported_rather_than_hidden` and it asserted, against the
    COMMITTED ledger, that `AUT-PD-146` still carried `_closed_by` and `AUT-PD-099` still carried
    `_outcome`. Both are now spelt correctly: the driver's sweep renamed **22 drifted fields across
    22 rows** — 16 `_lease_released`, 5 `_outcome`, 3 `_closed_by` — which is more than the eight
    `ledger_schema`'s own note counted. `LIVE_ALIASES` is consequently empty, exactly as that note
    prescribed (*"rename the rows onto the governed spelling, then delete this block"*).
    ⛔ SO THE OLD ASSERTIONS PINNED A DEFECT'S EXISTENCE AND FIXING IT BROKE THEM. That is a test
    whose fixture was the bug, and the honest repair is to keep what it was really guarding — that
    the reporting path WORKS — while removing its dependence on production still being broken.
    ⚠ AND THE NEW VERSION IS NOT VACUOUS, which is the trap this file names elsewhere: an empty
    `LIVE_ALIASES` would make `set(found) == set(LIVE_ALIASES)` pass for a `live_aliases_in` that
    had been emptied out or deleted. So the mechanism is exercised on a CONSTRUCTED ledger — the
    same device `test_the_ranked_table_survives_a_row_with_no_score` uses, and for the same reason:
    a suite whose subject is emptying the committed ledger must not need the committed ledger to be
    dirty.
    """
    found = ledger_schema.live_aliases_in(ledger)
    assert set(found) == set(ledger_schema.LIVE_ALIASES), (
        "the committed ledger's live aliases disagree with the registry. If a row reintroduced a "
        "drifted spelling, rename it; if an alias was retired, empty the registry entry too.")

    # ⛔ The mechanism, on a ledger built here, so this test still fails if `live_aliases_in` stops
    # looking. Registering an alias must make a row carrying it REPORTED, by id.
    constructed = {"entries": [
        {"id": "AUT-X-900", "state": "queued", "_closed_by": "CYC-0001"},
        {"id": "AUT-X-901", "state": "queued", "closed_by": "CYC-0002"},
    ]}
    reported = ledger_schema.live_aliases_in(constructed, aliases={"_closed_by": "closed_by"})
    assert "AUT-X-900" in reported["_closed_by"], (
        "a row carrying a registered alias was not reported — the drift would be invisible again")
    assert "AUT-X-901" not in reported.get("_closed_by", []), (
        "the correctly-spelt row was reported as drifted; the check is matching the wrong name")


@pytest.mark.parametrize("value", [None, "true", "false", 1, 0, ""])
def test_requires_trimcrae_must_be_a_real_bool(value):
    """⛔ `continuity._why_not_ready` tests this for TRUTHINESS, so `null`, `0` and `""` fall through
    to "ready" exactly as an absent key does — the right name with a wrong value reads green in the
    same way the wrong name does."""
    row = {"id": "AUT-PD-999", "state": "queued", "requires_trimcrae": value}
    assert ledger_schema.value_problems(row), f"{value!r} passed as a bool"


@pytest.mark.parametrize("row_id", [
    "AUT-PD-030",             # the bare shape
    "AUT-PD-204-6b009680",    # ⭐ the discriminated shape ids.next_entry_id mints as of 2026-09-01
    "AUT-003",
    "AUT-PROP-055",
    "AUT-BIX-002",
])
def test_both_id_shapes_are_legal(row_id):
    """⛔ THE ID FORMAT MOVED THE NIGHT THIS SCHEMA WAS WRITTEN. A session discriminator is now
    appended because two concurrent sessions provably minted `AUT-PD-204` from one committed ledger.
    A validator that accepts only the old shape would refuse every row filed from now on."""
    assert ledger_schema.id_problems({"id": row_id}) == []


@pytest.mark.parametrize("row_id", ["AUT_PD_030", "AUT-PD-", "", None, 7])
def test_an_id_that_is_not_an_id_is_refused(row_id):
    assert ledger_schema.id_problems({"id": row_id})


def test_the_id_shape_is_read_from_its_one_home(monkeypatch):
    """⛔ `id_problems` must call `ids.parse_entry_id` rather than carry its own regex — a second
    home for the id format is the exact defect this module is about. Proved by breaking the one
    home and watching the schema's verdict follow it, which a private copy could not do."""
    import ids

    monkeypatch.setattr(ids, "parse_entry_id", lambda _rid: None)
    assert ledger_schema.id_problems({"id": "AUT-PD-030"}), (
        "the schema still accepted an id after `ids.parse_entry_id` was made to refuse it — it is "
        "not reading the format from ids.py")


def test_a_near_miss_id_prefix_is_refused():
    """A prefix is a NAMESPACE: `ids.next_entry_id` counts ordinals within one, so `AUT-PDD-201`
    opens a private namespace that collides with nothing and is read by nobody."""
    found = ledger_schema.id_problems({"id": "AUT-PDD-201"})
    assert found and "AUT-PD" in found[0]
    assert ledger_schema.id_problems({"id": "AUT-PROPP-201"})
    # A genuinely distinct new series is allowed without registration, same as a new field name.
    assert ledger_schema.id_problems({"id": "AUT-SEC-001"}) == []


def test_the_write_path_tolerates_a_fixture_id_but_not_an_invented_namespace():
    """⚠ MEASURED, NOT ASSUMED. Enforcing the id SHAPE inside `write_ledger` refused seven existing
    tests at once — all of them laying `AUT-X` / `AUT-TEST-APPEND` fixtures on a temp path. A fixture
    id is not a ledger id and there is nothing to protect there, because a real writer takes its id
    from `ids.next_entry_id`. ⛔ THE RELAXATION IS EXACTLY ONE THING AND THIS PINS IT: the near-miss
    PREFIX — the defect this module is actually about — is still refused on the write path."""
    assert ledger_schema.id_problems({"id": "AUT-X"}, require_parseable=False) == []
    assert ledger_schema.id_problems({"id": "AUT-X"})  # ...but the committed-file gate refuses it
    assert ledger_schema.id_problems({"id": "AUT-PDD-201"}, require_parseable=False)


def test_every_committed_id_parses(ledger):
    """⚠ Run before the check was wired in, so the gate could not be turned on red: all 344
    committed ids parse, and none carries a discriminator yet (the mint changed tonight)."""
    assert [e for e in ledger["entries"] if ledger_schema.id_problems(e)] == []


def test_a_state_no_reader_recognises_is_refused():
    assert ledger_schema.value_problems({"id": "X", "state": "in-progress"})
    assert ledger_schema.value_problems({"id": "X", "state": "closed"})
    assert ledger_schema.value_problems({"id": "X", "state": "queued"}) == []


def test_the_headers_typed_totals_are_checked_against_the_rows(ledger):
    """CLAUDE.md §1(1): a total is DERIVED, never typed. The five header counters are written by
    `priority.py --write`; a hand-added row that skips that step leaves them describing a ledger
    that no longer exists, and nothing measured the agreement."""
    assert ledger_schema.header_problems(ledger) == []
    drifted = copy.deepcopy(ledger)
    drifted["n_unscored"] = drifted["n_unscored"] + 1
    found = ledger_schema.header_problems(drifted)
    assert found and "n_unscored" in found[0] and "priority.py --write" in found[0]


def test_write_ledger_actually_calls_the_schema(tmp_path, ledger):
    """⛔ THE BINDING, NOT THE CHECKER. `ledger_io.write_ledger` is the one place every programmatic
    writer passes through; a schema nothing calls is the `subagent_width` failure again — recorded
    is not enforced. This asserts the refusal happens AT THE WRITE and that no partial file lands.
    """
    payload = copy.deepcopy(ledger)
    payload["entries"] = [dict(payload["entries"][0])]
    payload["entries"][0]["require_trimcrae"] = True
    out = tmp_path / "research-ledger.json"
    with pytest.raises(ledger_schema.SchemaViolation) as exc:
        ledger_io.write_ledger(out, payload)
    assert "require_trimcrae" in str(exc.value)
    assert not out.exists(), "a refused write left a file on disk"


def test_check_false_still_writes_because_tests_need_to_lay_one_down(tmp_path, ledger):
    """`check=False` is the documented escape for a test constructing a deliberately bad ledger. It
    must keep working, and it must remain the ONLY way past — the assertion above is what says so."""
    payload = copy.deepcopy(ledger)
    payload["entries"] = [dict(payload["entries"][0])]
    payload["entries"][0]["require_trimcrae"] = True
    out = tmp_path / "research-ledger.json"
    ledger_io.write_ledger(out, payload, check=False)
    assert out.exists()
