#!/usr/bin/env python3
"""THE ONE PROPERTY `proposal_dedup.py` EXISTS FOR: an id is not an identity.

⛔ THE THREAT MODEL IS NOT A DOUBLE-SUBMIT. It is a session three cycles from now, with no memory of
this one, reading the same survey, reaching the same conclusion, and filing it under a fresh id that
`ids.py` mints correctly. Every id-based check passes. So every test here that matters gives the
duplicate a DIFFERENT id — a suite whose duplicates share an id would be testing the check that
already works.

★ AND THE OPPOSITE ERROR IS TESTED JUST AS HARD, because this ledger contains byte-identical `what`
on different routes that is correctly distinct work (AUT-025/AUT-070, AUT-018/AUT-026). A dedup that
suppresses those is worse than none: it deletes real queue rows and reports a tidy number.

⚠ THE THRESHOLD IS TREATED AS A CALIBRATION, NOT A CONSTANT. `test_the_calibration_still_separates`
re-measures the two populations against the LIVE ledger on every run, so the day a genuinely distinct
pair reaches the threshold, this suite says so instead of the rule silently starting to eat rows.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import proposal_dedup as D  # noqa: E402

IDEA = ("PROPOSAL, GROUNDED IN the prior-art scan: give a route its own terminal 'out of ideas' "
        "condition, a two-clause rule with a wall-clock budget on the route or four consecutive "
        "attempts producing no measured improvement, as a companion to the stall clock rather than "
        "a replacement for it, computed from committed state and failing closed.")


def _row(entry_id, what=IDEA, kind="proposal", route="RT-AUTONOMY"):
    return {"id": entry_id, "kind": kind, "serves": {"route": route}, "what": what}


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE NEGATIVE CONTROL: the same idea, a new id.
# ---------------------------------------------------------------------------------------------

def test_the_same_idea_under_a_new_id_is_refused():
    adjudicator = D.Adjudicator()
    assert adjudicator.admit(_row("AUT-PROP-035")).admitted
    decision = adjudicator.admit(_row("AUT-PROP-061"))
    assert not decision.admitted, "a fresh id laundered the same idea straight back into the queue"
    assert decision.tier == "exact"
    assert decision.matched_id == "AUT-PROP-035"
    assert decision.similarity == 1.0


def test_a_provenance_clause_does_not_defeat_the_exact_tier():
    """⛔ A re-file characteristically wraps the same idea in a different provenance sentence. If
    normalization did not strip ids, cycle names and dates, tier 1 would miss every real re-file and
    only ever catch a copy-paste."""
    original = _row("AUT-PROP-035", "Filed by CYC-0030 on 2026-08-27. " + IDEA)
    refiled = _row("AUT-PROP-061", "Filed by CYC-0057 on 2026-09-14. " + IDEA + " (AUT-PD-055)")
    adjudicator = D.Adjudicator()
    adjudicator.admit(original)
    decision = adjudicator.admit(refiled)
    assert not decision.admitted, decision.reason
    assert decision.tier == "exact"


def test_a_reworded_idea_is_still_the_same_idea():
    """Tier 2. One-word changes must not buy admission."""
    reworded = (IDEA.replace("give a route", "grant each route")
                    .replace("terminal", "final")
                    .replace("failing closed", "which fails closed"))
    adjudicator = D.Adjudicator()
    adjudicator.admit(_row("AUT-PROP-035"))
    decision = adjudicator.admit(_row("AUT-PROP-061", reworded))
    assert not decision.admitted, f"a reworded re-file was admitted: {decision.reason}"
    assert decision.tier == "near"
    assert decision.similarity >= D.NEAR_DUPLICATE_JACCARD
    assert decision.shared_shingles and decision.shared_shingles > 0


def test_a_genuinely_different_proposal_is_admitted():
    """The positive control. A dedup that refuses everything is not a dedup."""
    other = ("PROPOSAL: pin the digest of every artifact under review in the review register so a "
             "restoration after a bad merge is a byte comparison instead of an argument about what "
             "the sentence used to say.")
    adjudicator = D.Adjudicator()
    adjudicator.admit(_row("AUT-PROP-035"))
    decision = adjudicator.admit(_row("AUT-PROP-062", other))
    assert decision.admitted, decision.reason
    assert decision.similarity < D.NEAR_DUPLICATE_JACCARD


# ---------------------------------------------------------------------------------------------
# Identity: what the key is, and what it deliberately is not.
# ---------------------------------------------------------------------------------------------

def test_identical_text_on_two_routes_is_two_proposals():
    """⛔ THE MEASUREMENT THAT PUT `route` IN THE KEY. The live ledger carries byte-identical `what`
    on different routes as correct, distinct, graph-generated work. Suppressing those would delete
    real rows — a text-only key would refuse 39 of 40."""
    adjudicator = D.Adjudicator()
    assert adjudicator.admit(_row("AUT-025", "Keep registered for automatic re-grade when EMC "
                                             "expression data lands.", "experiment",
                                  "RT-FAP-RLT")).admitted
    decision = adjudicator.admit(_row("AUT-070", "Keep registered for automatic re-grade when EMC "
                                                 "expression data lands.", "experiment",
                                      "RT-TCRT-CTA"))
    assert decision.admitted, (
        "the route boilerplate was suppressed. Those rows are distinct work; this is the failure "
        "mode that is worse than no dedup at all.")


def test_the_same_idea_on_a_different_route_is_REPORTED_even_though_it_is_admitted():
    """⛔ THE KNOWN HOLE IN THE KEY, AND THE REASON IT IS A HOLE AND NOT A SECRET. Re-filing under a
    different route dodges the primary key. It is surfaced as a cross-route echo — never blocked,
    because on this ledger those matches are usually legitimate boilerplate."""
    rows = [_row("AUT-PROP-035", route="RT-AUTONOMY"), _row("AUT-PROP-061", route="RT-LOOP")]
    echoes = D.cross_route_echoes(rows)
    assert echoes and echoes[0]["similarity"] >= D.NEAR_DUPLICATE_JACCARD
    assert {echoes[0]["a"], echoes[0]["b"]} == {"AUT-PROP-035", "AUT-PROP-061"}
    assert D.Adjudicator().seed([rows[0]]).consider(rows[1]).admitted, (
        "the cross-route echo must be a REPORT, not a block")


def test_the_id_is_not_an_input_to_the_fingerprint():
    """If the id ever reaches the fingerprint this becomes a slower way of comparing ids — the check
    that already passes on every real re-file."""
    assert D.fingerprint(_row("AUT-PROP-035")) == D.fingerprint(_row("AUT-PROP-999"))
    assert D.fingerprint(_row("AUT-PROP-035")) != D.fingerprint(_row("AUT-PROP-035",
                                                                    route="RT-LOOP"))
    assert D.fingerprint(_row("AUT-PROP-035")) != D.fingerprint(_row("AUT-PROP-035", kind="harden"))


# ---------------------------------------------------------------------------------------------
# ⛔⛔ FALSIFIABILITY: a suppression that cannot explain itself must not be constructible.
# ---------------------------------------------------------------------------------------------

def test_a_rejection_without_a_reason_cannot_be_built():
    """The mechanism that makes 'silently drop a row' impossible rather than discouraged."""
    with pytest.raises(ValueError):
        D.Decision(entry_id="AUT-X", admitted=False, fingerprint="abc", reason="")
    with pytest.raises(ValueError):
        D.Decision(entry_id="AUT-X", admitted=False, fingerprint="abc", reason="dupe")
    with pytest.raises(ValueError):
        D.Decision(entry_id="AUT-X", admitted=False, fingerprint="abc", reason="dupe", tier="exact")
    ok = D.Decision(entry_id="AUT-X", admitted=False, fingerprint="abc", reason="dupe",
                    tier="exact", matched_id="AUT-Y", matched_fingerprint="abc")
    assert not ok.admitted and ok.matched_id == "AUT-Y"


def test_every_suppression_is_retained_with_its_reason():
    adjudicator = D.Adjudicator()
    adjudicator.admit(_row("AUT-PROP-035"))
    for i in range(3):
        adjudicator.admit(_row(f"AUT-PROP-06{i}"))
    assert len(adjudicator.suppressed) == 3
    for decision in adjudicator.suppressed:
        assert decision.reason and decision.matched_id and decision.tier
        assert decision.as_dict()["matched_id"] == "AUT-PROP-035"


def test_a_refused_row_is_not_remembered_as_the_match_for_the_next_one():
    """If a rejection were recorded, the second re-file would collide with the first re-file and the
    report would name the wrong row — the audit trail would point at a row that was never filed."""
    adjudicator = D.Adjudicator()
    adjudicator.admit(_row("AUT-PROP-035"))
    adjudicator.admit(_row("AUT-PROP-061"))
    second = adjudicator.admit(_row("AUT-PROP-062"))
    assert second.matched_id == "AUT-PROP-035", (
        f"the second re-file was matched against a row that was refused: {second.matched_id}")


def test_consider_never_mutates_the_memory():
    adjudicator = D.Adjudicator()
    adjudicator.admit(_row("AUT-PROP-035"))
    before = len(adjudicator.seen)
    for _ in range(5):
        adjudicator.consider(_row("AUT-PROP-061"))
    assert len(adjudicator.seen) == before
    assert not adjudicator.suppressed, "consider() recorded a suppression it was only asked about"


# ---------------------------------------------------------------------------------------------
# The bound: NSLS-II's DequeSet(maxlen=100), and what it honestly forgets.
# ---------------------------------------------------------------------------------------------

def test_the_memory_is_bounded_and_says_what_it_forgot():
    memory = D.DequeSet(maxlen=3)
    for key in "abcde":
        memory.add(key)
    assert len(memory) == 3 and list(memory) == ["c", "d", "e"]
    assert memory.evictions == 2, "the bound evicted silently — the limit must be countable"
    assert D.DEDUP_MAXLEN == 100, "NSLS-II's bound is copied as-is; changing it is a decision"


def test_re_adding_a_key_does_not_evict_a_different_one():
    """⚠ Why a plain `deque(maxlen=)` is not enough: re-adding an existing key would push a duplicate
    and evict an unrelated idea, so the bound would mean 'the last N WRITES' instead of 'the last N
    DISTINCT ideas'."""
    memory = D.DequeSet(maxlen=3)
    for key in "abc":
        memory.add(key)
    for _ in range(10):
        memory.add("a")
    assert list(memory) == ["a", "b", "c"] and memory.evictions == 0


def test_an_evicted_idea_is_forgotten_by_BOTH_TIERS():
    """⛔ The near tier must never outlive the exact tier. If `_records` kept growing, the bound
    would be a fiction and the memory would leak — the exact thing NSLS-II's deque prevents."""
    adjudicator = D.Adjudicator(maxlen=2)
    adjudicator.admit(_row("AUT-PROP-001"))
    adjudicator.admit(_row("AUT-PROP-002", "an entirely unrelated second idea about pinning digests "
                                           "of artifacts under review in the register"))
    adjudicator.admit(_row("AUT-PROP-003", "a third idea about reading the rate limit rather than "
                                           "inferring it from a failure to dispatch anything"))
    assert len(adjudicator.seen) == 2 and len(adjudicator._records) == 2
    assert adjudicator.consider(_row("AUT-PROP-061")).admitted, (
        "an idea evicted from the bounded memory was still blocked — then the bound is not a bound")


# ---------------------------------------------------------------------------------------------
# The calibration, re-measured against the live ledger rather than quoted.
# ---------------------------------------------------------------------------------------------

def test_the_calibration_still_separates():
    """★ THE THRESHOLD IS A MEASUREMENT WITH A DATE ON IT. This re-runs both populations against the
    committed ledger: distinct in-bucket pairs must stay BELOW the threshold, and a row against a
    modified copy of itself must stay ABOVE it. When they meet, the threshold is wrong."""
    entries = D.load_entries()
    probe = D.calibration_probe(entries)
    assert probe["in_bucket_pairs"] > 100, "too few pairs to calibrate against"
    assert probe["false_positive_ceiling"] < D.NEAR_DUPLICATE_JACCARD, (
        f"a genuinely distinct pair ({probe['false_positive_pair']}) now scores "
        f"{probe['false_positive_ceiling']} at or above the threshold "
        f"{D.NEAR_DUPLICATE_JACCARD}. The rule would start eating real rows.")
    assert probe["reword_control"] > D.NEAR_DUPLICATE_JACCARD
    assert probe["truncation_control"] > D.NEAR_DUPLICATE_JACCARD


def test_the_live_ledger_scans_and_reports_what_it_would_refuse():
    """A smoke test that asserts no verdict about the ledger — only that the scan runs over every
    real field shape and that anything it refuses comes with a reason."""
    entries = D.load_entries()
    report = D.scan(entries, kinds=None)
    assert report["considered"] == len(entries)
    for decision in report["suppressed"]:
        assert decision.reason and decision.matched_id
    assert report["evictions"] > 0, (
        "187 entries did not evict anything from a 100-idea memory — the bound is not being applied")


def test_the_cli_exits_non_zero_only_when_it_would_refuse_something(tmp_path, capsys):
    ledger = tmp_path / "research" / "autonomy"
    ledger.mkdir(parents=True)
    path = os.path.join("research", "autonomy", "research-ledger.json")
    (tmp_path / path).write_text(json.dumps(
        {"entries": [_row("AUT-PROP-035"), _row("AUT-PROP-061")]}), encoding="utf-8")
    code = D.main(["--check", "--json", "--repo", str(tmp_path), "--fail-on-duplicate"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert len(payload["suppressed"]) == 1
    assert payload["suppressed"][0]["matched_id"] == "AUT-PROP-035"
    assert payload["suppressed"][0]["reason"]
