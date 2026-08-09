#!/usr/bin/env python3
"""Tests for the modality census — the denominator the route board is a numerator of. ($0, stdlib + pytest)

⭐ WHY THIS FILE EXISTS AS TESTS AND NOT AS PROSE. The census makes one claim that prose cannot keep:
that it accounts for every ruling the three prior searches already made. A memo asserting that goes
stale the first time somebody adds a rejection somewhere else and nothing notices — which is precisely
how `emc-post-degrader-options.md` §3b came to be the only auditable record of a search whose
conclusions had since moved. So the reconciliation is a build failure, not a sentence.

⛔ AND THE COVERAGE CLAIM IS THE ONE MOST WORTH GUARDING. `verdict: on_board` says "the board already
handles this" — the exact shape of assertion the 2026-08-06 route audit found 35 times while the
checker was green, because nothing resolved the pointer underneath it.
"""
from __future__ import annotations

import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(HERE)
REPO = os.path.dirname(SYS)
sys.path.insert(0, SYS)

import systems_check as sc  # noqa: E402


@pytest.fixture(scope="module")
def graph():
    return sc.derive(sc.load_graph())


# ───────────────────────── the register is internally sound ─────────────────────────

def test_every_on_board_row_names_a_route_that_exists(graph):
    """An `on_board` verdict IS a coverage claim, and a coverage claim with no resolvable route is
    the unverifiable assertion this whole collection was built to make impossible."""
    routes = {r["id"] for r in graph["routes"]}
    bad = [(m["id"], m.get("route")) for m in graph["modalities"]
           if m["verdict"] == "on_board" and m.get("route") not in routes]
    assert bad == [], f"on_board rows naming a route that does not exist: {bad}"


def test_every_candidate_is_registered_as_a_route(graph):
    """A candidate that survives triage and is never registered is a finding with nowhere to live.

    trimcrae's call on 2026-08-09 was to register every viable survivor rather than a top slice, so
    this holds the census and the board to that decision in both directions: a new candidate row that
    nobody promotes fails the build, and a promoted route that loses its census row fails the pointer
    check above.
    """
    if not graph["modalities"]:
        pytest.skip("census not populated yet")
    routes = {r["id"] for r in graph["routes"]}
    bad = [(m["id"], m.get("route")) for m in graph["modalities"]
           if m["verdict"] == "candidate" and m.get("route") not in routes]
    assert bad == [], f"candidates not registered as a resolvable route: {bad}"


#: The grading artifact and the graph are two homes for one fact -- what a route's observation showed.
#: They MUST be kept in step, and on 2026-08-09 they were not: five routes carried a verdict here and
#: still read "Registered … nothing run" on the board, while seven census rows said `candidate` about
#: routes whose premise had already been tested and failed. Nothing caught either, because every
#: existing check ran in the opposite direction.
_GRADING = "research/modalities/census-route-expression-grading.json"


def _gradings():
    path = os.path.join(REPO, _GRADING)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh).get("routes", {})


def test_a_graded_route_carries_its_grading_as_evidence(graph):
    """⛔ FIVE ROUTES FAILED THIS WHEN IT WAS WRITTEN. A verdict that exists in the artifact and not on
    the route is a result the board cannot see -- and the board is what anyone reads to decide what to
    do next. The route may disagree with the artifact's framing; it may not be silent about it."""
    graded = _gradings()
    if not graded:
        pytest.skip("grading artifact absent")
    routes = {r["id"]: r for r in graph["routes"]}
    bad = []
    for rid in graded:
        r = routes.get(rid)
        if r is None:
            bad.append((rid, "route does not exist"))
            continue
        refs = {e.get("ref") for e in r.get("supporting_evidence") or []}
        if "ART-CENSUS-ROUTE-GRADING" not in refs:
            bad.append((rid, "graded in the artifact but cites it nowhere"))
    assert bad == [], f"routes whose grading never reached the board: {bad}"


def test_a_census_row_does_not_claim_candidate_against_its_own_route(graph):
    """A class whose route was tested and went against it is not a candidate, whatever the row says.

    ⚠ DELIBERATELY KEYED ON THE GRADE GLYPH, NOT ON `state.status`. A route can be `parked` because a
    capability is missing -- which leaves the class perfectly live -- so mirroring status would close
    rows that nothing has actually tested. What disqualifies `candidate` is a grade that opens with ⛔,
    which this repository uses for a premise that was checked and failed.
    """
    if not graph["modalities"]:
        pytest.skip("census not populated yet")
    routes = {r["id"]: r for r in graph["routes"]}
    bad = []
    for m in graph["modalities"]:
        if m["verdict"] != "candidate":
            continue
        r = routes.get(m.get("route") or "")
        if r and (r.get("grade") or {}).get("value", "").startswith("⛔"):
            bad.append((m["id"], m["route"]))
    assert bad == [], (
        f"census rows still claiming `candidate` while their route's premise was tested and failed: "
        f"{bad}. The census is the denominator; a stale row inflates it.")


def test_every_prior_ruling_pointer_resolves_to_a_real_file(graph):
    """`already_rejected` points at the document that owns the ruling and deliberately does NOT
    restate its reason (rule 1). That only works if the pointer resolves — otherwise the census has
    quietly become the home of a reason it declined to write down."""
    bad = []
    for m in graph["modalities"]:
        ref = m.get("prior_ref")
        if not ref:
            continue
        if not os.path.exists(os.path.join(REPO, ref["file"])):
            bad.append((m["id"], ref["file"]))
    assert bad == [], f"prior_ref pointing at a file that does not exist: {bad}"


#: An `already_rejected` row POINTS at a ruling it does not own, so its rationale is an index entry
#: (name the axis, one phrase) and never the argument. The structural tell is length, and 300 is set
#: just above the longest legitimate row rather than at a round number -- two rows need a second
#: sentence to scope what the ruling does NOT cover, which is exactly the kind of clause that stops a
#: narrow ruling being read wide.
_POINTER_MAX = 300


def test_a_pointing_verdict_points_rather_than_argues(graph):
    """⭐ FOUR ROWS FAILED THIS ON THE FIRST PASS and one of them reproduced its source's argument
    almost verbatim. That matters more than it looks: a restated argument reads as valid on its own,
    so if the owning document's reasoning were later corrected, the copy would survive the correction
    and go on being quoted. It is rule 1's exact failure mode, one collection over."""
    long = [(m["id"], len(m["rationale"])) for m in graph["modalities"]
            if m["verdict"] == "already_rejected" and len(m["rationale"]) > _POINTER_MAX]
    assert long == [], (
        f"already_rejected rationales long enough to be arguing rather than pointing: {long}. "
        f"Name the axis the ruling turned on in one phrase; the argument stays in the document that "
        f"owns it (systems/taxonomy/modality.md §4).")


def test_searched_before_is_never_claimed_without_a_pointer(graph):
    """⭐ THE DIRECTION THAT MATTERS. `never_searched` is the census's finding, so the dangerous edit
    is the one that quietly clears the flag. Requiring a resolvable document for `searched_before`
    means the flag can only be cleared by evidence, never by an opinion that somebody must have
    looked at it once."""
    bad = [m["id"] for m in graph["modalities"]
           if m["prior_coverage"] == "searched_before" and not m.get("prior_ref")]
    assert bad == [], f"claiming a prior search with no document behind it: {bad}"


def test_a_parked_class_names_a_way_back(graph):
    """Same discipline the blocker taxonomy applies: a park with no named reopening condition is
    indistinguishable from a closure nobody was willing to write."""
    techs = {t["id"] for t in graph["technologies"]}
    bad = []
    for m in graph["modalities"]:
        if m["verdict"] != "parked_capability":
            continue
        trg = m.get("revisit_trigger") or []
        unknown = [t for t in trg if t not in techs]
        if not trg or unknown:
            bad.append((m["id"], trg, unknown))
    assert bad == [], f"parked classes with no usable revisit_trigger: {bad}"


def test_every_referenced_blocker_exists(graph):
    blk = {b["id"] for b in graph["blockers"]}
    bad = [(m["id"], b) for m in graph["modalities"] for b in m.get("blockers", []) if b not in blk]
    assert bad == [], f"modality rows naming an unregistered blocker: {bad}"


def test_parents_resolve_and_do_not_cycle(graph):
    mods = {m["id"]: m for m in graph["modalities"]}
    for m in graph["modalities"]:
        seen, cur = set(), m
        while cur.get("parent"):
            assert cur["parent"] in mods, f"{cur['id']} names a parent that does not exist"
            assert cur["parent"] not in seen, f"parent cycle through {cur['id']}"
            seen.add(cur["parent"])
            cur = mods[cur["parent"]]


# ───────────────────────── reconciliation against the prior searches ─────────────────────────
#
# ⛔ THE POINT OF THESE TWO. Three sweeps ran before this census and each already settled a set of
# classes. A census that silently dropped one of those rulings would re-propose a closed idea as a
# fresh lead — the exact failure `emc-post-degrader-options.md` §3b was written to prevent, in its
# own words: "so that a class that was considered and rejected is not re-proposed as an unexplored
# idea." Making that mechanical is the difference between a claim and a check.

PRIOR_SEARCHES = [
    "research/manuscripts/emc-post-degrader-options.md",
    "research/manuscripts/emc-unexplored-treatment-lanes.md",
    "research/manuscripts/emerging-modalities-scan-emc.md",
]


def test_every_strategy_family_is_reached_by_the_census(graph):
    """⭐ THIS CHECK FOUND SIX REAL GAPS ON ITS FIRST RUN, WHICH IS WHY IT IS HERE. Covalent chemistry,
    ligand-binding-domain occupancy, low-complexity-domain ligands, DNA-binding-domain ligands,
    synthetic lethality and rational combination were all classes the board ALREADY pursues and the
    census had no row for -- the census's own failure mode running in reverse.

    ⚠ ASSERTED AT FAMILY LEVEL, NOT ROUTE LEVEL, AND DELIBERATELY. Several routes are not modality
    classes at all -- two are wet-lab asks, two are dissemination deliverables, one is a method and one
    is a selectivity requirement -- so a per-route assertion would need a hand-maintained allowlist,
    which is the construct this repository has repeatedly watched stop covering the model in silence.
    A family cannot be exempted the same way: if a whole strategy family has no census row, the census
    has a hole in it.
    """
    if not graph["modalities"]:
        pytest.skip("census not populated yet")
    routes = {r["id"]: r for r in graph["routes"]}
    covered = {m["route"] for m in graph["modalities"] if m.get("route")}
    reached = {routes[r]["strategy"] for r in covered if r in routes}
    missing = sorted({s["id"] for s in graph["strategies"]} - reached)
    assert missing == [], f"strategy families no census row reaches: {missing}"


def test_the_prior_searches_still_exist_where_the_census_says_they_do():
    """A reconciliation test whose inputs have moved passes vacuously and reports coverage it never
    checked. `parser_guard.py` exists for this failure mode across the repo; this is its local form."""
    missing = [p for p in PRIOR_SEARCHES if not os.path.exists(os.path.join(REPO, p))]
    assert missing == [], f"a prior-search document the census reconciles against has moved: {missing}"


#: Rows in the two rejection tables the census reconciled against on 2026-08-09, verified one by one.
#: ⭐ PINNED SO THE SOURCE CANNOT GROW IN SILENCE. Verifying 26 and 22 rulings by hand once is worth
#: little if the next ruling somebody adds to either table never gets a census row -- the census would
#: go on reporting complete reconciliation while a fresh closure sat outside it, which is exactly the
#: "a retraction that reaches some of its copies is not a retraction" shape this repository keeps
#: rediscovering. When this fires, the fix is a new MOD-* row pointing at the new ruling, then bump
#: the count in the same commit.
RECONCILED = {
    "research/manuscripts/emc-unexplored-treatment-lanes.md": ("## 6 · Considered and rejected", 26),
    "research/manuscripts/emc-post-degrader-options.md": ("## 3b · The technique classes searched", 22),
}


def _table_rows(rel, heading):
    text = open(os.path.join(REPO, rel), encoding="utf-8").read()
    assert heading in text, f"{rel} no longer contains the heading {heading!r}"
    section = text.split(heading, 1)[1]
    section = re.split(r"\n(?:---|## )", section, 1)[0]
    cells = [re.sub(r"[*~]", "", m).strip()
             for m in re.findall(r"^\|\s*([^|]+?)\s*\|", section, re.M)]
    return [c for c in cells
            if c and set(c) - set("- ") and "technique class" not in c.lower() and c.lower() != "lane"]


@pytest.mark.parametrize("rel", sorted(RECONCILED))
def test_a_prior_rejection_table_has_not_grown_past_the_census(rel):
    heading, expected = RECONCILED[rel]
    rows = _table_rows(rel, heading)
    assert len(rows) == expected, (
        f"{rel} now lists {len(rows)} rulings, not the {expected} the census reconciled against. "
        f"A ruling has been added or removed: give it a MOD-* row in systems/graph/modalities.json "
        f"with verdict `already_rejected` and a prior_ref pointing here, then update this count.")


def test_every_prior_search_is_actually_accounted_for(graph):
    """At least one census row must point at each prior search, or the reconciliation is a fiction.

    ⚠ DELIBERATELY A WEAK TEST, AND IT SAYS SO. It asserts that each prior document is REACHED, not
    that every row inside it was mapped — a per-row mapping would have to parse three hand-written
    markdown tables whose shapes differ, and a parser that silently matches nothing is worse than no
    parser (measured here twice: `fetch-literature.yml`'s decorative `query` path, and a checker
    whose scope shrank while its pass rate improved). The strong form is the census's own
    `prior_coverage` field, which is per-row and schema-enforced.
    """
    if not graph["modalities"]:
        pytest.skip("census not populated yet")
    reached = {m["prior_ref"]["file"] for m in graph["modalities"] if m.get("prior_ref")}
    missing = [p for p in PRIOR_SEARCHES if p not in reached]
    assert missing == [], (
        f"no census row points at these prior searches, so their rulings are unaccounted for: {missing}")


# ───────────────────────── the census cannot quietly become a claim register ─────────────────────────

_CLAIMY = re.compile(
    r"\b(?:cures?|will treat|efficacious|is safe|therapeutic window|clinically ready)\b", re.I)


def test_no_row_asserts_efficacy_safety_or_readiness(graph):
    """`lint_claims.py` covers the generated L0/L1/L2 views and L3-publications.md — and the census
    view is none of those, so its prose would otherwise be linted by nothing at all. That gap is the
    exact shape of the audit's X7 finding, where the entire route portfolio sat outside the language
    linter while its pass rate looked healthy."""
    bad = []
    for m in graph["modalities"]:
        for field in ("rationale", "zero_dollar_next_step", "name"):
            hit = _CLAIMY.search(m.get(field) or "")
            if hit:
                bad.append((m["id"], field, hit.group(0)))
    assert bad == [], f"modality rows asserting efficacy, safety or readiness: {bad}"


def test_the_census_view_is_registered_for_generation():
    """A view that is not in `all_views()` is not regenerated and not drift-checked — it becomes a
    hand-maintained file wearing a GENERATED banner, which is strictly worse than a hand-written one."""
    g = sc.derive(sc.load_graph())
    assert "modality-census.md" in sc.all_views(g)


#: ⛔ THE EIGHTH INSTANCE OF ONE DRIFT, AND THE FIRST THAT WAS SYSTEMATIC (2026-08-09). Every route
#: graded that day left its census row's `zero_dollar_next_step` describing work that had just been
#: taken. All twenty live rows were affected at once. Four went further and asserted that registry
#: FIELDS were "already curated" which do not exist at all — a row like that does not merely waste
#: the next session's time, it sends them looking for a table that was never written.
#: ⚠ THE CHECK IS DELIBERATELY NARROW. It cannot judge whether prose describes the same work as a
#: route's `⛔ TAKEN` entry — that is a reading task, not a string comparison. What it CAN hold is the
#: bookkeeping half: a row whose route records a taken step must acknowledge that the step was taken,
#: by carrying the marker this repository uses for it. A row that stays silent is the failure mode.
_TAKEN = "⛔ TAKEN"
_ACK = ("TAKEN", "ATTEMPTED", "PARTLY", "DOES NOT EXIST", "CANNOT BE", "MAY NOT BE",
        "STILL OPEN", "NOT COVERED")


def test_a_live_row_acknowledges_the_steps_its_route_records_as_taken(graph):
    """A `candidate` row whose route has taken a step may not read as though nothing has happened."""
    if not graph["modalities"]:
        pytest.skip("census not populated yet")
    routes = {r["id"]: r for r in graph["routes"]}
    bad = []
    for m in graph["modalities"]:
        if m["verdict"] != "candidate":
            continue
        r = routes.get(m.get("route") or "")
        if r is None:
            continue
        taken = [v for v in (r.get("required_validation") or [])
                 if str(v.get("what", "")).startswith(_TAKEN)]
        if not taken:
            continue
        step = str(m.get("zero_dollar_next_step") or "")
        if not any(tok in step for tok in _ACK):
            bad.append((m["id"], m["route"]))
    assert bad == [], (
        f"live census rows whose route records a ⛔ TAKEN step while the row still reads as though "
        f"nothing has run: {bad}. The row is what a session reads to decide what to do next; a stale "
        f"one buys re-running finished work.")
