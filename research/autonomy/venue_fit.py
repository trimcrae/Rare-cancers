#!/usr/bin/env python3
"""Join this programme's publication endpoints to the venue data the repository actually holds.

The deterministic half of the publication ladder. No model, no network, stdlib only, $0 — so a
cycle rebuilds the table from the committed corpus every time rather than trusting a shortlist it
inherited (research/manuscripts/program/emc-autonomy-architecture.md §6.4).

WHAT THIS IS FOR
    `research/literature/venue-fee-*.json`, `venue-policy-browser-fetch.json` and
    `venue-typeset-geometry.json` already hold primary-source readings of publisher pages — the
    $0 route, the page charges, the affiliation rules, the aims and scope. `systems/graph/
    publications.json` already holds every endpoint and what it would claim. NOTHING JOINS THEM.
    This does, on the six criteria §6.4 names, and it emits the evidence for every cell.

⛔⛔ THE ONE RULE THIS FILE EXISTS TO OBEY — READ THIS BEFORE ADDING A VENUE OR A CRITERION
    A venue fact that is not in the committed data is emitted as `"value": "UNKNOWN"` with
    `"evidence": null`. There is no third state. It is NEVER filled in from what a model
    remembers about a journal — not an APC, not an indexing status, not a scope, not even
    something the author of this file was certain of.

    Why, concretely: this table's output goes into a submission decision, and a submission is the
    one act in this repository that reaches an outside reader and is undone only by a public
    correction (CLAUDE.md §6). A remembered APC that is two years stale sends a paper to a venue
    that bills four figures; a remembered scope sends it to a desk rejection. The repository has
    already measured this failure — venue-fee-routes-2026-08-10.json records TWO APC figures taken
    from search snippets that were simply WRONG, which is why that file was built. And
    preprint-host-decision-round2.md §1 records the sharper version: a `status: None` row in a
    fetch corpus is "an unanswered question wearing the costume of a reading", and the prose
    written above it cost this programme a declined preprint.

    An honest UNKNOWN costs nothing. It says which $0 fetch would close it. An invented fact
    costs the route and cannot be told apart from a real one afterwards.

    ⭐ THE MECHANISM, NOT JUST THE INTENTION: no fact below is written as a literal in this file.
    Every one is a PROBE — a JSON path or an anchor string that must be located in a named source
    file at run time. A probe that does not resolve yields UNKNOWN; it never falls back to the
    value it was declared with. `systems/tests/test_autonomy_venue_fit.py` mutates a probe's
    anchor and asserts the fact collapses to UNKNOWN, so the guard is load-bearing rather than
    stated.

WHAT IT IS NOT
    Not a venue recommendation and not an authorisation. §6.2: a journal submission ALWAYS
    escalates, and CLAUDE.md §3 reserves choosing and submitting to trimcrae, per paper, per act.
    This emits a ranked table with its evidence attached; the ranking is arithmetic over recorded
    readings, not a judgement about a journal.

USAGE
    python3 research/autonomy/venue_fit.py                  # the table to stdout
    python3 research/autonomy/venue_fit.py --json           # the report, to stdout
    python3 research/autonomy/venue_fit.py --write          # write venue-fit.json
    python3 research/autonomy/venue_fit.py --explain PUB-X  # one endpoint's shortlist, in full
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
WEIGHTS_FILE = HERE / "venue-fit-weights.json"
OUT_FILE = HERE / "venue-fit.json"

LIT = REPO / "research" / "literature"
GRAPH = REPO / "systems" / "graph"

# Every source this table may read. A probe naming anything else is a bug: the point of the
# exercise is that the corpus already holds these readings and nothing joined them.
SOURCES: dict[str, pathlib.Path] = {
    "fee_routes": LIT / "venue-fee-routes-2026-08-10.json",
    "fee_pages": LIT / "venue-fee-pages-2026-08-24.json",
    "policy": LIT / "venue-policy-browser-fetch.json",
    "geometry": LIT / "venue-typeset-geometry.json",
    "nat_capture": LIT / "nat-submission-guidelines-2026-08-23.md",
    "publications": GRAPH / "publications.json",
}

# The rubric's criteria, in §6.4's order. `zero_dollar_route` heads the list and is NOT scored —
# venue-fit-weights.json carries it under `filters`, and _forbidden_as_weight explains why.
CRITERIA = [
    "zero_dollar_route",
    "unaffiliated_author_permitted",
    "scope_match",
    "indexed_pubmed_or_europepmc",
    "preprint_friendly",
    "page_charge_exposure",
]

UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------------------------
# Probe registry.
#
# Each entry is a LOCATOR, not a fact. `value` is the reading this locator licenses IF the
# locator resolves against the committed file; if it does not resolve, the criterion is UNKNOWN
# and `value` is discarded unused. Probes are tried in order and the first that resolves wins,
# which is how a caveated reading ("VERIFIED ... with one real caveat") is allowed to pre-empt
# the plain one.
#
# ⛔ A criterion with NO probe here is UNKNOWN by construction. Do not add a probe you cannot
#    point at a line in a committed file.
# ---------------------------------------------------------------------------------------------
VENUE_PROBES: dict[str, dict[str, Any]] = {
    "GCC": {
        "identity": [
            {"kind": "json_field", "source": "fee_routes", "path": ["verdicts", "GCC", "journal"]}
        ],
        "issn": [
            {"kind": "text_anchor", "source": "fee_routes", "path": None,
             "anchor": "api.openalex.org/sources/issn:1098-2264", "before": 0, "after": 0}
        ],
        "zero_dollar_route": [
            {"kind": "json_field", "source": "fee_routes",
             "path": ["verdicts", "GCC", "zero_dollar_route"],
             "expect_contains": ["VERIFIED"], "value": "VERIFIED",
             "supporting": [
                 {"kind": "json_field", "source": "fee_routes",
                  "path": ["verdicts", "GCC", "evidence", 0, "verbatim"]},
                 {"kind": "json_field", "source": "fee_routes",
                  "path": ["verdicts", "GCC", "reasoning"]},
             ]}
        ],
        # unaffiliated / scope / indexing / preprint / page charge: every gcc_* target in
        # venue-policy-browser-fetch.json returned 403 under a real headless Chromium. Nothing
        # to probe, so nothing is claimed.
    },
    "CROH": {
        "identity": [
            {"kind": "json_field", "source": "fee_routes", "path": ["verdicts", "CROH", "journal"]}
        ],
        "issn": [
            {"kind": "text_anchor", "source": "fee_routes", "path": None,
             "anchor": "api.openalex.org/sources/issn:1040-8428", "before": 0, "after": 0}
        ],
        "zero_dollar_route": [
            {"kind": "json_field", "source": "fee_routes",
             "path": ["verdicts", "CROH", "zero_dollar_route"],
             "expect_contains": ["VERIFIED"], "value": "VERIFIED",
             "supporting": [
                 {"kind": "json_field", "source": "fee_routes",
                  "path": ["verdicts", "CROH", "evidence", 0, "verbatim"]},
                 {"kind": "json_field", "source": "fee_routes",
                  "path": ["verdicts", "CROH", "reasoning"]},
             ]}
        ],
    },
    "BJC": {
        "identity": [
            {"kind": "json_field", "source": "fee_routes", "path": ["verdicts", "BJC", "journal"]}
        ],
        "issn": [
            {"kind": "text_anchor", "source": "fee_routes", "path": None,
             "anchor": "api.openalex.org/sources/issn:0007-0920", "before": 0, "after": 0}
        ],
        "zero_dollar_route": [
            # Tried first: the caveated reading. Both tokens must be present in the field, so the
            # classification is derived from the record rather than asserted over it.
            {"kind": "json_field", "source": "fee_routes",
             "path": ["verdicts", "BJC", "zero_dollar_route"],
             "expect_contains": ["VERIFIED", "caveat"], "value": "VERIFIED_WITH_CAVEAT",
             "supporting": [
                 {"kind": "text_anchor", "source": "policy",
                  "path": ["targets", "bjc_guide_to_authors", "text"],
                  "anchor": "Standard licence to publish", "before": 0, "after": 60},
                 {"kind": "json_field", "source": "fee_routes",
                  "path": ["verdicts", "BJC", "evidence", 0, "verbatim"]},
                 {"kind": "json_field", "source": "fee_routes",
                  "path": ["verdicts", "BJC",
                           "⚠_the_colour_charge_is_real_and_is_now_confirmed_at_primary_source",
                           "consequence"]},
             ]},
            {"kind": "json_field", "source": "fee_routes",
             "path": ["verdicts", "BJC", "zero_dollar_route"],
             "expect_contains": ["VERIFIED"], "value": "VERIFIED"},
        ],
        "scope_match": [
            {"kind": "scope_text", "source": "policy",
             "path": ["targets", "bjc_guide_to_authors", "text"],
             "anchor": "Research articles describing novel findings",
             "before": 0, "after": 130}
        ],
        "preprint_friendly": [
            {"kind": "text_anchor", "source": "policy",
             "path": ["targets", "bjc_guide_to_authors", "text"],
             "anchor": "has not been previously published (except as a preprint",
             "before": 90, "after": 120, "value": "FRIENDLY"}
        ],
        "page_charge_exposure": [
            {"kind": "json_field", "source": "fee_routes",
             "path": ["verdicts", "BJC",
                      "⚠_the_colour_charge_is_real_and_is_now_confirmed_at_primary_source",
                      "verbatim"],
             "expect_contains": ["charge if authors choose"],
             "value": "AVOIDABLE_BY_AUTHOR_CHOICE",
             "supporting": [
                 {"kind": "json_field", "source": "fee_routes",
                  "path": ["verdicts", "BJC",
                           "⚠_the_colour_charge_is_real_and_is_now_confirmed_at_primary_source",
                           "consequence"]},
             ]}
        ],
        # unaffiliated_author_permitted: the BJC guide requires a cover letter carrying "the
        # affiliation and contact information for the corresponding author". That is a
        # requirement to STATE an affiliation; it does not say whether an author without one may
        # submit, which is the criterion. Reading it either way would be inference, so: UNKNOWN.
        # indexed_pubmed_or_europepmc: no BJC indexing statement is in the corpus.
    },
    "CGT": {
        "identity": [
            {"kind": "json_field", "source": "policy", "path": ["targets", "cgt_journal_home", "title"]}
        ],
        "issn": [
            {"kind": "text_anchor", "source": "policy", "path": ["targets", "cgt_about", "text"],
             "anchor": "The international standard serial number (ISSN)", "before": 0, "after": 150}
        ],
        "zero_dollar_route": [
            {"kind": "text_anchor", "source": "fee_pages",
             "path": ["targets", "cgt-guide-to-authors", "text"],
             "anchor": "each page of an article will incur a fixed charge",
             "before": 60, "after": 120, "value": "NOT_FREE",
             "supporting": [
                 {"kind": "text_anchor", "source": "fee_pages",
                  "path": ["targets", "cgt-guide-to-authors", "text"],
                  "anchor": "Page charges will NOT apply to authors who choose",
                  "before": 0, "after": 80},
                 {"kind": "text_anchor", "source": "fee_pages",
                  "path": ["targets", "cgt-open-access-fees", "text"],
                  "anchor": "The current APC, subject to VAT", "before": 0, "after": 90},
             ]}
        ],
        "unaffiliated_author_permitted": [
            {"kind": "text_anchor", "source": "policy", "path": ["targets", "cgt_gta", "text"],
             "anchor": "All authors must provide an institutional email address",
             "before": 0, "after": 300, "value": "CONDITIONAL",
             "supporting": [
                 {"kind": "text_anchor", "source": "policy",
                  "path": ["targets", "cgt_journal_home", "text"],
                  "anchor": "Requirement of a cover letter in an institutional letterhead",
                  "before": 55, "after": 120},
             ]}
        ],
        "scope_match": [
            {"kind": "scope_text", "source": "policy", "path": ["targets", "cgt_about", "text"],
             "anchor": "Cancer Gene Therapy is the essential gene and cellular therapy resource",
             "before": 0, "after": 900}
        ],
        "indexed_pubmed_or_europepmc": [
            {"kind": "text_anchor", "source": "policy", "path": ["targets", "cgt_about", "text"],
             "anchor": "Abstracted/indexed in", "before": 0, "after": 230,
             "expect_contains": ["Medline"], "value": "INDEXED"}
        ],
        "page_charge_exposure": [
            {"kind": "text_anchor", "source": "fee_pages",
             "path": ["targets", "cgt-guide-to-authors", "text"],
             "anchor": "each page of an article will incur a fixed charge",
             "before": 60, "after": 120, "value": "CHARGES_PER_PAGE"}
        ],
    },
    "NAT": {
        "identity": [
            {"kind": "json_field", "source": "geometry", "path": ["journal"]}
        ],
        "issn": [
            {"kind": "text_anchor", "source": "policy",
             "path": ["targets", "sage_nat_uk_journal_page", "text"],
             "anchor": "ISSN: 21593337", "before": 0, "after": 20}
        ],
        "zero_dollar_route": [
            {"kind": "text_anchor", "source": "nat_capture", "path": None,
             "anchor": "will be assessed the following mandatory Publishing Services Fees",
             "before": 60, "after": 80, "value": "NOT_FREE"}
        ],
        "scope_match": [
            {"kind": "scope_text", "source": "policy",
             "path": ["targets", "sage_nat_uk_journal_page", "text"],
             "anchor": "this journal focuses on cutting-edge basic research",
             "before": 40, "after": 420}
        ],
        "preprint_friendly": [
            {"kind": "text_anchor", "source": "nat_capture", "path": None,
             "anchor": "The journal will consider submissions of manuscripts that have been posted",
             "before": 0, "after": 60, "value": "FRIENDLY"}
        ],
        "page_charge_exposure": [
            {"kind": "text_anchor", "source": "nat_capture", "path": None,
             "anchor": "Page Charges (assessed upon acceptance)", "before": 0, "after": 20,
             "value": "CHARGES_PER_PAGE",
             "supporting": [
                 # venue-typeset-geometry.json exists precisely because this charge makes the
                 # PRINTED page count a cost. It is carried as evidence of what is measured —
                 # and the file's own refusal to give a characters-per-page rate is carried with
                 # it, so no page count and no total is derived here from something it disclaims.
                 {"kind": "json_field", "source": "geometry", "path": ["_why"]},
                 {"kind": "json_field", "source": "geometry", "path": ["⚠_what_this_is_not"]},
                 {"kind": "json_field", "source": "geometry", "path": ["consensus"]},
             ]}
        ],
        # unaffiliated_author_permitted: the capture requires "institutional affiliations" in the
        # author list, which is again a statement requirement rather than a permission rule.
        # indexed_pubmed_or_europepmc: no indexing statement in the capture.
    },
}


# ---------------------------------------------------------------------------------------------
# Loading and probe resolution
# ---------------------------------------------------------------------------------------------
_CACHE: dict[str, Any] = {}


def _raw(source: str) -> str:
    key = f"raw:{source}"
    if key not in _CACHE:
        _CACHE[key] = SOURCES[source].read_text(encoding="utf-8")
    return _CACHE[key]


def _parsed(source: str) -> Any:
    key = f"json:{source}"
    if key not in _CACHE:
        _CACHE[key] = json.loads(_raw(source))
    return _CACHE[key]


def _dig(blob: Any, path: list) -> Any:
    """Walk a JSON path. Returns None the moment the path stops existing — a missing path is an
    unresolved probe, never an exception and never a default."""
    node = blob
    for step in path:
        try:
            node = node[step]
        except (KeyError, IndexError, TypeError):
            return None
    return node


def normalise(text: str) -> str:
    """Collapse whitespace. The ONLY transformation applied to a quote — a quote is otherwise a
    contiguous slice of the source, so a reader can grep for it."""
    return re.sub(r"\s+", " ", text).strip()


SNAP_LIMIT = 40  # never widen a quote window by more than this to reach a word boundary


def _snap_back(text: str, index: int) -> int:
    """Widen a quote's left edge to the nearest word boundary. The quote stays a CONTIGUOUS
    SLICE of the source — that is what makes it greppable, and what the suite asserts."""
    if index <= 0:
        return 0
    limit = max(0, index - SNAP_LIMIT)
    while index > limit and not text[index - 1].isspace():
        index -= 1
    return index


def _snap_forward(text: str, index: int) -> int:
    if index >= len(text):
        return len(text)
    limit = min(len(text), index + SNAP_LIMIT)
    while index < limit and not text[index].isspace():
        index += 1
    return index


def _source_ref(source: str) -> str:
    return str(SOURCES[source].relative_to(REPO))


def resolve(probe: dict) -> dict | None:
    """Resolve one probe against the committed corpus, or return None.

    ⛔ Returning None is the honest answer, and every caller must treat it as UNKNOWN. This
    function must never synthesise a value, and it must never return the probe's declared
    `value` without having located the thing that licenses it.
    """
    source = probe["source"]
    if source not in SOURCES or not SOURCES[source].exists():
        return None

    kind = probe["kind"]
    if kind == "json_field":
        found = _dig(_parsed(source), probe["path"])
        if found is None:
            return None
        rendered = found if isinstance(found, str) else json.dumps(found, ensure_ascii=False)
        for token in probe.get("expect_contains", []):
            if token.lower() not in rendered.lower():
                return None
        return {
            "file": _source_ref(source),
            "locator": {"json_path": probe["path"]},
            "quote": normalise(rendered),
        }

    if kind in {"text_anchor", "scope_text"}:
        text = _raw(source) if probe["path"] is None else _dig(_parsed(source), probe["path"])
        if not isinstance(text, str):
            return None
        index = text.find(probe["anchor"])
        if index < 0:
            return None
        start = _snap_back(text, max(0, index - probe.get("before", 0)))
        end = _snap_forward(text, min(len(text), index + len(probe["anchor"])
                                      + probe.get("after", 0)))
        quote = normalise(text[start:end])
        for token in probe.get("expect_contains", []):
            if token.lower() not in quote.lower():
                return None
        locator: dict[str, Any] = {"anchor": probe["anchor"]}
        if probe["path"] is not None:
            locator["json_path"] = probe["path"]
        return {"file": _source_ref(source), "locator": locator, "quote": quote}

    raise ValueError(f"unknown probe kind {kind!r}")


def read_fact(probes: list[dict] | None) -> dict:
    """Resolve a criterion to {value, evidence, supporting_evidence}.

    Two states and no third: a located reading with its evidence, or UNKNOWN with evidence null.
    """
    for probe in probes or []:
        evidence = resolve(probe)
        if evidence is None:
            continue
        supporting = [s for s in (resolve(p) for p in probe.get("supporting", [])) if s]
        return {
            "value": probe.get("value", evidence["quote"]),
            "evidence": evidence,
            "supporting_evidence": supporting,
        }
    return {"value": UNKNOWN, "evidence": None, "supporting_evidence": []}


# ---------------------------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------------------------
def load_weights() -> dict:
    with WEIGHTS_FILE.open() as fh:
        return json.load(fh)


def _tokens(text: str, weights: dict) -> set[str]:
    method = weights["scope_match_method"]
    stop = {w.lower() for w in method["stopwords"]}
    minimum = method["min_token_length"]
    words = re.findall(r"[A-Za-z][A-Za-z\-]+", text.lower())
    return {w for w in words if len(w) >= minimum and w not in stop}


def score_scope(scope_fact: dict, claim: str, weights: dict) -> dict:
    """Lexical overlap between a venue's own scope text and the endpoint's recorded claim.

    Emits the matched WORDS, not just a number: §6.4 requires evidence, and a bare 0.62 is
    exactly the recommendation-without-evidence the spec forbids.
    """
    if scope_fact["evidence"] is None:
        return {"value": UNKNOWN, "multiplier": 0.0, "matched_terms": [],
                "evidence": None, "supporting_evidence": []}
    method = weights["scope_match_method"]
    matched = sorted(_tokens(scope_fact["evidence"]["quote"], weights) & _tokens(claim, weights))
    multiplier = min(1.0, len(matched) / float(method["saturation_at"]))
    return {
        "value": round(multiplier, 3),
        "multiplier": multiplier,
        "matched_terms": matched,
        "method": method["kind"],
        "⛔_what_this_is_not": method["⛔_what_it_is_NOT"],
        "evidence": scope_fact["evidence"],
        "supporting_evidence": scope_fact["supporting_evidence"],
    }


def multiplier_for(term: str, value: Any, weights: dict) -> float:
    table = weights["terms"][term].get("values")
    if table is None:
        return float(value) if isinstance(value, (int, float)) else 0.0
    return float(table.get(str(value), weights["unknown_policy"]["score_contribution"]))


def venue_facts(probes: dict | None = None) -> dict[str, dict]:
    """Every venue's six criteria, read from the corpus. Independent of any endpoint."""
    probes = VENUE_PROBES if probes is None else probes
    out: dict[str, dict] = {}
    for key in sorted(probes):
        spec = probes[key]
        identity = read_fact(spec.get("identity"))
        if identity["evidence"] is None:
            # A venue whose very NAME cannot be located in a committed file is not a venue this
            # table knows about. Dropping it is the honest move; naming it from memory is not.
            continue
        facts = {name: read_fact(spec.get(name)) for name in CRITERIA}
        out[key] = {
            "venue": key,
            "name": identity["value"],
            "name_evidence": identity["evidence"],
            "issn": read_fact(spec.get("issn")),
            "criteria": facts,
        }
    return out


def _filter_verdict(fact: dict, weights: dict) -> tuple[str, str]:
    spec = weights["filters"]["verified_zero_dollar_route"]
    value = str(fact["value"])
    if value in spec["passing_values"]:
        return "pass", f"{value} — a $0 route is verified at primary source"
    if value in spec["failing_values"]:
        return "fail", f"{value} — the free route carries a charge, so it is not a cheap fit"
    if spec["fail_closed_on_unknown"]:
        return "needs_a_fetch", (
            "UNKNOWN — no fee-route reading for this venue is in the committed corpus. "
            "Held out of every shortlist and listed here because CLAUDE.md §0 holds that a "
            "blocked row usually waits on a $0 observation."
        )
    return "pass", value


def rank_for_endpoint(endpoint: dict, facts: dict[str, dict], weights: dict) -> dict:
    terms = weights["terms"]
    claim = str(endpoint.get("what_it_would_claim") or "")
    scored: list[dict] = []

    for key, venue in facts.items():
        verdict, _ = _filter_verdict(venue["criteria"]["zero_dollar_route"], weights)
        if verdict != "pass":
            continue

        criteria: dict[str, Any] = {
            "zero_dollar_route": dict(venue["criteria"]["zero_dollar_route"],
                                      role="FILTER — passed; not scored")
        }
        total = 0.0
        for term in terms:
            if term == "scope_match":
                cell = score_scope(venue["criteria"]["scope_match"], claim, weights)
                multiplier = cell["multiplier"]
            else:
                fact = venue["criteria"][term]
                multiplier = multiplier_for(term, fact["value"], weights)
                cell = dict(fact, multiplier=multiplier)
            contribution = terms[term]["weight"] * multiplier
            cell["weight"] = terms[term]["weight"]
            cell["contribution"] = round(contribution, 2)
            criteria[term] = cell
            total += contribution

        scored_criteria = [c for c in CRITERIA if c != "zero_dollar_route"]
        n_unknown = sum(1 for c in scored_criteria if criteria[c]["evidence"] is None)
        coverage = round(1.0 - n_unknown / float(len(scored_criteria)), 3)
        candidate = {
            "venue": key,
            "name": venue["name"],
            "score": round(total, 2),
            "n_unknown": n_unknown,
            "evidence_coverage": coverage,
            "criteria": criteria,
        }
        if coverage < weights["unknown_policy"]["warn_below_coverage"]:
            candidate["⚠_ranked_over_holes"] = (
                f"{n_unknown} of {len(scored_criteria)} scored criteria are UNKNOWN for this "
                "venue. The rank is arithmetic over what the corpus holds, not a reading of the "
                "venue. Close the UNKNOWNs before this row carries any weight in a decision."
            )
        scored.append(candidate)

    scored.sort(key=lambda c: (-c["score"], c["venue"]))
    for position, candidate in enumerate(scored, start=1):
        candidate["rank"] = position

    top_n = weights["escalation"]["carry_top_n"]
    return {
        "publication": endpoint["id"],
        "document": (endpoint.get("document") or {}).get("file"),
        "state": endpoint.get("state"),
        "claim": claim,
        "n_candidates": len(scored),
        "candidates": scored,
        "escalation_carries": [c["venue"] for c in scored[:top_n]],
        "_escalation_rule": weights["escalation"]["_why"],
    }


def build_report(probes: dict | None = None, weights: dict | None = None) -> dict:
    weights = weights or load_weights()
    facts = venue_facts(probes)

    buckets: dict[str, list[dict]] = {"pass": [], "fail": [], "needs_a_fetch": []}
    for key, venue in facts.items():
        fact = venue["criteria"]["zero_dollar_route"]
        verdict, reason = _filter_verdict(fact, weights)
        buckets[verdict].append({
            "venue": key,
            "name": venue["name"],
            "zero_dollar_route": fact["value"],
            "reason": reason,
            "evidence": fact["evidence"],
            "supporting_evidence": fact["supporting_evidence"],
        })

    endpoints = [
        p for p in json.loads(SOURCES["publications"].read_text(encoding="utf-8"))
        if p.get("target_venue") == "journal_submission"
    ]
    endpoints.sort(key=lambda p: p["id"])
    shortlists = [rank_for_endpoint(e, facts, weights) for e in endpoints]

    scored_criteria = [c for c in CRITERIA if c != "zero_dollar_route"]
    cells = [(k, c) for k, v in facts.items() for c in scored_criteria
             if v["criteria"][c]["evidence"] is not None]
    gaps = {
        criterion: sorted(k for k, v in facts.items()
                          if v["criteria"][criterion]["evidence"] is None)
        for criterion in CRITERIA
    }

    return {
        "_schema": "emc-venue-fit/1",
        "_role": (
            "The join §6.4 says is missing: manuscript endpoint -> ranked journal venues, on the "
            "six criteria, with the evidence for every cell. GENERATED by "
            "research/autonomy/venue_fit.py — re-run it rather than hand-editing a row."
        ),
        "_owner": (
            "research/manuscripts/program/emc-autonomy-architecture.md"
            "#64--journal-fit--researchautonomyvenue-fitjson"
        ),
        "_generated_by": "python3 research/autonomy/venue_fit.py --write",
        "_weights": "research/autonomy/venue-fit-weights.json — the one home of every weight",
        "⛔_this_selects_nothing_and_authorises_nothing": (
            "§6.2: a journal submission ALWAYS escalates. CLAUDE.md §3: trimcrae names the paper "
            "and the act, per paper, per act. A rank here is arithmetic over recorded readings."
        ),
        "⛔_UNKNOWN_means_the_corpus_does_not_say": (
            "Every cell is either a reading with its file and quote attached, or UNKNOWN with "
            "evidence: null. No cell is ever filled from a model's knowledge of a journal. A "
            "venue fact with no evidence is an unanswered question, not a fact — "
            "research/literature/venue-fee-routes-2026-08-10.json records two APC figures taken "
            "from search snippets that were WRONG, which is why that file exists."
        ),
        "sources": [
            {
                "key": key,
                "file": str(path.relative_to(REPO)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for key, path in sorted(SOURCES.items())
        ],
        "filter": {
            "criterion": "zero_dollar_route",
            "_why_a_filter": weights["filters"]["verified_zero_dollar_route"]["_role"],
            "passed": buckets["pass"],
            "failed": buckets["fail"],
            "needs_a_fetch": buckets["needs_a_fetch"],
        },
        "venue_facts": facts,
        "shortlists": shortlists,
        "coverage": {
            "venues_known": len(facts),
            "venues_on_shortlists": len(buckets["pass"]),
            "endpoints_targeting_journal_submission": len(shortlists),
            "scored_cells_total": len(facts) * len(scored_criteria),
            "scored_cells_with_evidence": len(cells),
            "unknown_by_criterion": gaps,
            "⚠_read_this_as_a_worklist": (
                "Each venue listed under a criterion is one fetch away from a real cell. Every "
                "gap here has the same cause on record: the publisher page returned 403 to plain "
                "HTTP, to CI and to a real headless Chromium alike "
                "(venue-policy-browser-fetch.json), so closing it needs a human browser read of "
                "the kind that produced nat-submission-guidelines-2026-08-23.md."
            ),
        },
    }


# ---------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------
def _table(report: dict) -> str:
    lines = []
    filt = report["filter"]
    lines.append("FILTER — verified $0 route (a filter, never a weight)")
    for bucket, label in (("passed", "pass"), ("failed", "FAIL"), ("needs_a_fetch", "?")):
        for row in filt[bucket]:
            lines.append(f"  [{label:^4}] {row['venue']:<5} {row['name'][:46]:<46} {row['reason'][:60]}")
    lines.append("")
    for short in report["shortlists"]:
        lines.append(f"{short['publication']}  ({short['n_candidates']} candidates)")
        lines.append(f"  {'rank':>4}  {'score':>7}  {'venue':<6} {'cover':>6}  {'unk':>3}  name")
        for candidate in short["candidates"]:
            lines.append(
                f"  {candidate['rank']:>4}  {candidate['score']:>7.1f}  {candidate['venue']:<6} "
                f"{candidate['evidence_coverage']:>6.2f}  {candidate['n_unknown']:>3}  "
                f"{candidate['name'][:44]}"
            )
        lines.append("")
    cov = report["coverage"]
    lines.append(
        f"{cov['venues_known']} venues known · {cov['venues_on_shortlists']} pass the $0 filter · "
        f"{cov['scored_cells_with_evidence']}/{cov['scored_cells_total']} scored cells carry "
        "evidence; the rest are UNKNOWN"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--write", action="store_true", help="write venue-fit.json")
    parser.add_argument("--explain", metavar="PUB_ID", help="one endpoint's shortlist, in full")
    args = parser.parse_args(argv)

    report = build_report()

    if args.explain:
        match = [s for s in report["shortlists"] if s["publication"] == args.explain]
        if not match:
            known = ", ".join(s["publication"] for s in report["shortlists"])
            print(f"no journal-submission endpoint {args.explain}. Known: {known}", file=sys.stderr)
            return 2
        print(json.dumps(match[0], indent=2, ensure_ascii=False))
        return 0

    if args.write:
        with OUT_FILE.open("w") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(
            f"wrote {OUT_FILE.relative_to(REPO)}: {len(report['shortlists'])} endpoints, "
            f"{report['coverage']['venues_on_shortlists']} venues past the $0 filter, "
            f"{report['coverage']['scored_cells_with_evidence']}/"
            f"{report['coverage']['scored_cells_total']} scored cells with evidence"
        )
        return 0

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    print(_table(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
