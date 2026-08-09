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


def test_the_prior_searches_still_exist_where_the_census_says_they_do():
    """A reconciliation test whose inputs have moved passes vacuously and reports coverage it never
    checked. `parser_guard.py` exists for this failure mode across the repo; this is its local form."""
    missing = [p for p in PRIOR_SEARCHES if not os.path.exists(os.path.join(REPO, p))]
    assert missing == [], f"a prior-search document the census reconciles against has moved: {missing}"


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
