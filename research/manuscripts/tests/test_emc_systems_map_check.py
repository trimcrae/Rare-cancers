"""The systems-map guards must FAIL on the things they exist to catch.

WHY NEGATIVE TESTS AND NOT JUST A GREEN RUN. A guard that fails OPEN leaves no trace: a check that
silently passes everything and a check that is genuinely satisfied render identically. Every
invariant below corresponds to a failure that really happened in this repo, so each one is exercised
by MUTATING a copy of the live registry into the broken shape and asserting the specific error code
comes back. A test that only asserts "the current registry is clean" would still pass if someone
deleted the check.

The mutations are in-memory only; nothing is written.
"""
import copy
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))                       # research/manuscripts/tests
MANUSCRIPTS = os.path.dirname(HERE)                                     # research/manuscripts
MODULE = os.path.join(MANUSCRIPTS, "emc_systems_map_check.py")

_spec = importlib.util.spec_from_file_location("emc_systems_map_check", MODULE)
chk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chk)


@pytest.fixture()
def m():
    with open(chk.MAP_PATH) as fh:
        return json.load(fh)


def codes(mapping):
    f = chk.Findings()
    for check in chk.ALL_CHECKS:
        check(mapping, f)
    return {c for c, _ in f.errors}


def route(mapping, rid):
    return next(r for r in mapping["routes"] if r["id"] == rid)


def instrument(mapping, iid):
    return next(i for i in mapping["instruments"] if i["id"] == iid)


# --- failure 1: one piece of evidence under two names ----------------------------------------

def test_evidence_cited_under_an_unregistered_name_fails(m):
    ev = next(e for e in m["evidence"] if e["id"] == "EV-ZAIENNE-2022")
    ev["cited_in"].append({"file": "research/IDEAS.md", "as": "Someone Else 2019", "role": "assertion"})
    assert "E1" in codes(m)


def test_two_evidence_entries_sharing_a_pmid_fails(m):
    dup = copy.deepcopy(next(e for e in m["evidence"] if e["id"] == "EV-ZAIENNE-2022"))
    dup["id"] = "EV-DUPLICATE"
    dup["aliases"] = ["A Different Name 2022"]
    dup["misattributed_as"] = []
    dup["cited_in"] = []
    m["evidence"].append(dup)
    assert "E2" in codes(m)


def test_one_name_resolving_to_two_evidence_entries_fails(m):
    other = next(e for e in m["evidence"] if e["id"] == "EV-FILION-2009")
    other["aliases"].append("Zaienne 2022")
    assert "E3" in codes(m)


def test_a_misattribution_with_no_guard_fails(m):
    ev = next(e for e in m["evidence"] if e["id"] == "EV-ZAIENNE-2022")
    ev.pop("retired_by")
    assert "E1" in codes(m)


def test_a_registered_occurrence_that_is_no_longer_in_its_file_fails(m):
    ev = next(e for e in m["evidence"] if e["id"] == "EV-FILION-2009")
    ev["aliases"].append("a string that is definitely not in that file 12345")
    ev["cited_in"].append({"file": "research/IDEAS.md",
                           "as": "a string that is definitely not in that file 12345",
                           "role": "assertion"})
    assert "E4" in codes(m)


# --- failure 2: one object under two incompatible definitions --------------------------------

def test_a_name_mapping_to_two_objects_fails(m):
    obj = next(o for o in m["objects"] if o["id"] == "OBJ-FUS-T1")
    obj["aliases"].append("EWSR1::NR4A3 type 2")
    assert "O1" in codes(m)


def test_claiming_a_contested_name_as_an_alias_fails(m):
    obj = next(o for o in m["objects"] if o["id"] == "OBJ-FUS-T1")
    obj["aliases"].append("the canonical EMC fusion")
    assert "O1" in codes(m)


def test_a_reported_fusion_with_no_exon_definition_fails(m):
    obj = next(o for o in m["objects"] if o["id"] == "OBJ-FUS-T2")
    obj["definition"]["exon_level"] = ""
    assert "O2" in codes(m)


# --- failure 3: one grade over two different routes ------------------------------------------

def test_two_routes_owning_their_grade_at_the_same_section_fails(m):
    a, b = route(m, "RT-MONOVALENT"), route(m, "RT-COVALENT-PROBE")
    a["grade"]["owner"] = copy.deepcopy(b["grade"]["owner"])
    assert "R1" in codes(m)


def test_a_grade_asserted_in_two_places_fails(m):
    r = route(m, "RT-DEGRADER")
    r["grade_pointers"][0]["asserts_grade"] = True
    assert "R2" in codes(m)


def test_distinctness_with_no_blocker_grounding_fails(m):
    r = route(m, "RT-MONOVALENT")
    next(d for d in r["distinct_from"] if d["route"] == "RT-COVALENT-PROBE")["fails_on"] = []
    assert "R3" in codes(m)


def test_same_grade_and_same_blockers_but_declared_distinct_fails(m):
    """The covalent-probe / monovalent-modulator shape, made to collapse on purpose."""
    a, b = route(m, "RT-MONOVALENT"), route(m, "RT-COVALENT-PROBE")
    b["grade"]["value"] = a["grade"]["value"]
    shared = ["BLK-NO-WET-LAB"]
    next(d for d in a["distinct_from"] if d["route"] == "RT-COVALENT-PROBE")["fails_on"] = shared
    next(d for d in b["distinct_from"] if d["route"] == "RT-MONOVALENT")["fails_on"] = shared
    assert "R3" in codes(m)


# --- instruments: a failing control cannot be support ----------------------------------------

def test_citing_a_failing_instrument_as_support_fails(m):
    r = route(m, "RT-COVALENT-PROBE")
    r["instruments"]["support"].append("V17")          # V17 fails its own positive control
    assert "I1" in codes(m)


def test_an_instrument_with_no_control_is_also_not_support(m):
    r = route(m, "RT-DEGRADER")
    r["instruments"]["support"].append("V18")          # V18 has no known-answer test at all
    assert "I1" in codes(m)


# --- failure 4: a claim quoting an absent or stubbed artifact --------------------------------

def test_a_claim_on_an_absent_artifact_fails(m):
    art = next(a for a in m["artifacts"] if a["id"] == "ART-IDR-CENSUS")
    art["path"] = "research/modalities/this-artifact-does-not-exist.json"
    f = chk.Findings()
    chk.check_claims(m, f)
    # assert on the MESSAGE, not just the code: C1 may legitimately be firing for other rows, and a
    # test that passes because of somebody else's failure is not testing anything.
    assert any(c == "C1" and "this-artifact-does-not-exist.json" in msg for c, msg in f.errors)


def test_a_claim_on_a_missing_field_fails(m):
    c = next(c for c in m["claims"] if c["id"] == "CLM-FUSION-MODEL-DISAGREEMENT")
    c["field"] = "/no/such/field"
    assert "C3" in codes(m)


def test_the_stub_test_matches_the_artifact_stub_guard(m):
    """One rule, one meaning -- this must agree with research/modalities/artifact_stub_guard.py."""
    assert chk.is_stub_bytes(b'{"_status": "cannot compute", "_remedy": "run with --refresh"}')
    assert not chk.is_stub_bytes(b'{"_status": "ok", "rg_dipeptides_retained": 0}')
    assert chk.is_stub_bytes(b"{ truncated")


# --- closure kinds and revival triggers ------------------------------------------------------

def test_a_non_permanent_closure_with_no_revival_trigger_fails(m):
    instrument(m, "V12")["revival_trigger"] = []
    assert "Z2" in codes(m)


def test_a_permanent_closure_carrying_a_revival_trigger_fails(m):
    """The category error in the direction that matters: a fixed sequence fact filed as temporary."""
    route(m, "RT-DBD")["revival_trigger"] = ["TR-FE-CRYPTIC-POCKET"]
    assert "Z3" in codes(m)


def test_a_definitional_closure_carrying_a_revival_trigger_fails(m):
    route(m, "RT-6MP")["revival_trigger"] = ["TR-CHEAP-CRYPTIC-ENSEMBLE"]
    assert "Z3" in codes(m)


@pytest.mark.parametrize("vague", [
    "better methods for ternary prediction",
    "improved free-energy calculations become available",
    "a more accurate co-folder is released for ternary assembly prediction work",
])
def test_a_vague_revival_trigger_fails(m, vague):
    m["revival_triggers"][0]["trigger"] = vague
    assert "Z4" in codes(m)


def test_a_trigger_naming_nothing_it_would_reopen_fails(m):
    m["revival_triggers"][0]["would_reopen"] = []
    assert "Z7" in codes(m)


def test_an_unknown_closure_kind_fails(m):
    route(m, "RT-DEGRADER")["closure_kind"] = "sort_of_closed"
    assert "Z1" in codes(m)


def test_typing_a_derived_field_into_the_registry_fails(m):
    """`permanently_closed` and `revival_would_reopen` are DERIVED (CLAUDE.md 1)."""
    route(m, "RT-DBD")["permanently_closed"] = True
    assert "Z6" in codes(m)
    m2 = copy.deepcopy(m)
    route(m2, "RT-DBD").pop("permanently_closed")
    route(m2, "RT-DEGRADER")["revival_would_reopen"] = ["R7"]
    assert "Z6" in codes(m2)


def test_an_unevidenced_watch_list_claim_fails(m):
    """A populated field is not a measured one (CLAUDE.md 4)."""
    t = next(t for t in m["revival_triggers"] if t.get("on_watch_list"))
    t.pop("watch_list_evidence")
    assert "Z5" in codes(m)


def test_a_stale_watch_list_claim_fails(m):
    t = next(t for t in m["revival_triggers"] if t.get("on_watch_list"))
    t["watch_list_evidence"] = "a row that method-watch.md does not contain 98765"
    assert "Z5" in codes(m)


def test_permanence_is_derived_from_the_kind_not_from_the_row(m):
    assert chk.is_permanent(m, "definitional")
    assert chk.is_permanent(m, "arithmetic_over_fixed_fact")
    assert not chk.is_permanent(m, "instrument_limit")
    assert not chk.is_permanent(m, "confound_in_the_system")
    assert not chk.is_permanent(m, "unregenerable_artifact")


def test_instrument_limit_is_the_biggest_bucket_and_is_revivable(m):
    """Not a numerical assertion about the science -- a structural one about the registry.

    The whole reason `closure_kind` exists is that most of this program's failures are limitations
    of today's methods rather than facts about the target. If that ever stopped being true the
    watch list would be near-empty and this test would say so.
    """
    items = m["routes"] + m["instruments"]
    limited = [i for i in items if i.get("closure_kind") == "instrument_limit"]
    permanent = [i for i in items if chk.is_permanent(m, i.get("closure_kind"))]
    assert len(limited) > len(permanent)
    assert all(i.get("revival_trigger") for i in limited)


# --- the derived view may not drift from its source -------------------------------------------

def test_the_committed_view_matches_what_the_registry_generates(m):
    with open(chk.VIEW_PATH) as fh:
        assert fh.read() == chk.render_view(m), (
            "research/manuscripts/emc-systems-map.md is DERIVED. Regenerate it with "
            "`python3 research/manuscripts/emc_systems_map_check.py --write-view`; never edit it."
        )
