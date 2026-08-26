"""Guards on the journal-fit table — research/autonomy/venue_fit.py.

⛔ WHY THIS SUITE IS DIFFERENT FROM THE OTHERS IN THIS DIRECTORY.

Every other generated artifact in this repository is read by the next session and fixed by the
next commit. This one feeds a JOURNAL SUBMISSION — the one act CLAUDE.md §6 says reaches an
outside reader, and the only one undone by a public correction against an identifier somebody may
already have cited. A fabricated APC in this table does not produce a wrong number in a report; it
produces a paper sent to a venue that bills four figures to an author with no grant, or a desk
rejection at a venue whose scope was remembered rather than read.

The repository has already paid for this lesson twice:

  * `research/literature/venue-fee-routes-2026-08-10.json` exists because TWO APC figures taken
    from search snippets were simply WRONG, and it says so in its own `⛔` key.
  * `research/manuscripts/program/preprint-host-decision-round2.md` §1 records a `status: None`
    row in a fetch corpus that was written about as though it had answered — "an unanswered
    question wearing the costume of a reading" — and it cost a declined preprint.

So the properties below are not style. Each one is a mechanism that makes the difference between
a read fact and an invented one VISIBLE in the output.

1. Two states and no third. A cell is a reading with its file and quote, or UNKNOWN with
   `evidence: null`. A cell with a confident value and no evidence is the failure mode.
2. Every quote is a real, contiguous, locatable slice of the file it names — checked by finding
   it in that file, not by trusting the emitter.
3. The $0 route is a FILTER, not a weight (architecture §6.4). Proven by relaxing the filter and
   watching a per-page-charging venue take first place on every endpoint.
4. No dollar figure exists in the output that is not verbatim in a source file.
5. The UNKNOWN guard is load-bearing — mutate a probe's anchor and the cell must COLLAPSE to
   UNKNOWN rather than keep the value the probe was declared with.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
VENUE_FIT_PY = REPO / "research" / "autonomy" / "venue_fit.py"
WEIGHTS_JSON = REPO / "research" / "autonomy" / "venue-fit-weights.json"


def _import_venue_fit():
    spec = importlib.util.spec_from_file_location("autonomy_venue_fit", VENUE_FIT_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def vf():
    return _import_venue_fit()


@pytest.fixture(scope="module")
def report(vf):
    return vf.build_report()


@pytest.fixture(scope="module")
def weights(vf):
    return vf.load_weights()


def _walk_cells(node, path="$"):
    """Yield every (path, dict) that is a venue FACT — a mapping carrying both `value` and
    `evidence`. That pair is the schema this suite polices."""
    if isinstance(node, dict):
        if "value" in node and "evidence" in node:
            yield path, node
        for key, value in node.items():
            yield from _walk_cells(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk_cells(value, f"{path}[{index}]")


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


# -------------------------------------------------------------------------------------------
# 1 · two states and no third
# -------------------------------------------------------------------------------------------
def test_every_venue_fact_is_either_evidenced_or_UNKNOWN_with_null_evidence(vf, report):
    cells = list(_walk_cells(report))
    assert len(cells) > 20, "fixture is degenerate — no facts to police"
    for path, cell in cells:
        has_evidence = cell["evidence"] is not None
        is_unknown = cell["value"] == vf.UNKNOWN
        assert has_evidence != is_unknown, (
            f"{path} is in the third state this table forbids: value={cell['value']!r} with "
            f"evidence={'present' if has_evidence else 'null'}. A venue fact is a reading with "
            "its source, or it is UNKNOWN with evidence null. Nothing in between — a confident "
            "value with no evidence is indistinguishable from a fabricated one."
        )


def test_both_states_actually_occur_so_the_previous_test_is_not_vacuous(vf, report):
    values = [cell["value"] for _, cell in _walk_cells(report)]
    assert vf.UNKNOWN in values, "no UNKNOWN cells — the guard would pass trivially"
    assert any(v != vf.UNKNOWN for v in values), "no evidenced cells — the table is empty"


def _dig(blob, path):
    node = blob
    for step in path:
        node = node[step]
    return node


def test_every_quote_is_locatable_in_the_file_it_names(report):
    """Provenance, checked rather than trusted. A quote the named file does not contain is a
    fabrication whether or not anyone meant it to be — so every quote is re-derived here from
    the file AND from the exact JSON path the evidence claims it came from."""
    checked = 0
    cache: dict[str, object] = {}
    for path, cell in _walk_cells(report):
        evidences = [cell["evidence"]] if cell["evidence"] else []
        evidences += cell.get("supporting_evidence") or []
        for evidence in evidences:
            source = REPO / evidence["file"]
            assert source.exists(), f"{path} cites a file that does not exist: {evidence['file']}"
            if evidence["file"] not in cache:
                raw = source.read_text(encoding="utf-8")
                cache[evidence["file"]] = (raw, json.loads(raw) if raw.lstrip()[:1] in "{[" else None)
            raw, parsed = cache[evidence["file"]]

            json_path = evidence["locator"].get("json_path")
            if json_path is not None:
                assert parsed is not None, f"{path} cites a json_path into a non-JSON file"
                field = _dig(parsed, json_path)
                haystack = field if isinstance(field, str) else json.dumps(field, ensure_ascii=False)
                where = f"{evidence['file']} at {json_path}"
            else:
                haystack, where = raw, evidence["file"]

            assert _normalise(evidence["quote"]) in _normalise(haystack), (
                f"{path} carries a quote that is NOT in {where}:\n"
                f"  {evidence['quote'][:160]!r}"
            )
            anchor = evidence["locator"].get("anchor")
            if anchor is not None:
                assert _normalise(anchor) in _normalise(evidence["quote"]), (
                    f"{path} claims an anchor its own quote does not contain"
                )
            checked += 1
    assert checked >= 10, f"only {checked} quotes checked — the corpus join produced almost nothing"


def test_an_anchor_probe_is_verified_against_the_file_and_not_asserted(vf):
    """The declared `value` on a probe is a licence, not a fact: it must never be emitted unless
    the locator resolved."""
    unresolvable = {
        "kind": "text_anchor",
        "source": "policy",
        "path": ["targets", "bjc_guide_to_authors", "text"],
        "anchor": "this sentence is not in any publisher page in this repository",
        "value": "FRIENDLY",
    }
    assert vf.resolve(unresolvable) is None
    fact = vf.read_fact([unresolvable])
    assert fact == {"value": vf.UNKNOWN, "evidence": None, "supporting_evidence": []}, (
        "an unresolvable probe leaked its declared value into a fact"
    )


# -------------------------------------------------------------------------------------------
# 2 · the $0 route is a FILTER, not a weight
# -------------------------------------------------------------------------------------------
def test_the_zero_dollar_route_is_never_a_scoring_term(weights):
    """architecture §6.4: 'Cheap first is the ask, so the $0-route clause is a filter, not a
    weight.' A weight is tradeable; a filter is not."""
    assert "zero_dollar_route" not in weights["terms"]
    assert "verified_zero_dollar_route" in weights["filters"]
    assert "zero_dollar_route" in weights["_forbidden_as_weight"]


def test_the_zero_dollar_cell_contributes_nothing_to_any_score(report):
    for short in report["shortlists"]:
        for candidate in short["candidates"]:
            cell = candidate["criteria"]["zero_dollar_route"]
            assert "contribution" not in cell and "weight" not in cell, (
                f"{candidate['venue']} scored its $0 route — it is a filter, not a term"
            )
            assert cell["role"].startswith("FILTER")
            total = sum(
                c["contribution"] for name, c in candidate["criteria"].items()
                if name != "zero_dollar_route"
            )
            assert round(total, 2) == candidate["score"], (
                "the score is not the sum of the scored criteria, so something else is being "
                "added to it"
            )


def test_a_venue_that_fails_the_filter_never_reaches_a_shortlist(report):
    failed = {row["venue"] for row in report["filter"]["failed"]}
    held = {row["venue"] for row in report["filter"]["needs_a_fetch"]}
    assert failed, "fixture is degenerate — no venue fails the $0 filter"
    for short in report["shortlists"]:
        listed = {c["venue"] for c in short["candidates"]}
        assert not (listed & failed), f"{short['publication']} shortlists a non-free venue"
        assert not (listed & held), (
            f"{short['publication']} shortlists a venue whose fee route was never read. "
            "The filter fails CLOSED: an unread fee route is an unanswered question."
        )


def test_the_filter_is_what_excludes_the_paid_venue_and_not_the_arithmetic(vf, weights):
    """⭐ The load-bearing half of criterion 3, and it is not a restatement of the one above.

    Cancer Gene Therapy charges a fixed per-page fee on its non-open-access route. It is also the
    BEST-EVIDENCED venue in the corpus — it is the one venue with a retrieved aims-and-scope, a
    retrieved indexing statement and a retrieved affiliation rule. So if the $0 clause were a
    weight, CGT would win: relax the filter and it takes rank 1 on every endpoint. That is the
    whole reason §6.4 makes it a filter, and this test is the proof.
    """
    relaxed = copy.deepcopy(weights)
    relaxed["filters"]["verified_zero_dollar_route"]["passing_values"].append("NOT_FREE")
    unfiltered = vf.build_report(weights=relaxed)

    paid = {row["venue"] for row in vf.build_report(weights=weights)["filter"]["failed"]}
    assert paid, "fixture is degenerate"

    took_first = 0
    for short in unfiltered["shortlists"]:
        if short["candidates"] and short["candidates"][0]["venue"] in paid:
            took_first += 1
    assert took_first == len(unfiltered["shortlists"]), (
        "with the filter relaxed a per-page-charging venue did NOT take first place, so the "
        "filter is not what is holding 'cheap first' — the arithmetic happens to agree today "
        "and this suite is blind to the day it stops agreeing."
    )


# -------------------------------------------------------------------------------------------
# 3 · no invented money
# -------------------------------------------------------------------------------------------
def test_no_money_figure_appears_that_is_not_verbatim_in_a_source_file(vf, report):
    """CLAUDE.md §7: never write an identifier — or a price — from recollection. Every currency
    amount in the table must be findable, character for character, in a committed source."""
    corpus = "\n".join(
        _normalise(path.read_text(encoding="utf-8")) for path in vf.SOURCES.values()
    )
    blob = json.dumps(report, ensure_ascii=False)
    figures = set(re.findall(r"[$£€]\s?[0-9][0-9,.]*", blob))
    assert figures, "no currency figures at all — this test would pass vacuously"
    for figure in sorted(figures):
        assert _normalise(figure) in corpus, (
            f"the table carries the money figure {figure!r}, which appears in NO source file. "
            "It was invented. research/literature/venue-fee-routes-2026-08-10.json exists "
            "because exactly this produced two wrong APCs."
        )


def test_the_table_states_no_derived_page_count_or_page_charge_total(report):
    """venue-typeset-geometry.json refuses to give a characters-per-page rate in its own words.
    Multiplying a per-page fee by a page count this repository cannot honestly compute would
    manufacture a total that looks measured."""
    blob = json.dumps(report, ensure_ascii=False)
    assert not re.search(r"(estimated|projected|total)[^\"]{0,40}(page charge|page fee)", blob, re.I)
    assert not re.search(r"pages? × |× \$|\$[0-9,]+ total", blob)


# -------------------------------------------------------------------------------------------
# 4 · mutation tests — the UNKNOWN guard must be load-bearing
# -------------------------------------------------------------------------------------------
def test_breaking_a_probes_anchor_collapses_the_cell_to_UNKNOWN(vf, weights):
    """⭐ THE MUTATION TEST. A guard that still passes with its mechanism removed is guarding
    nothing (`paper-hardening`: seven one-of-a-pair defects were found exactly this way).

    Here the mechanism is that a probe is a LOCATOR resolved at run time, never a stored fact.
    Point one probe at a sentence no publisher page contains and the cell must lose its value,
    lose its evidence, and cost the venue exactly that criterion's weight — not fall back to the
    reading it was declared with.
    """
    baseline = vf.build_report(weights=weights)
    bjc = baseline["venue_facts"]["BJC"]["criteria"]["preprint_friendly"]
    assert bjc["value"] == "FRIENDLY" and bjc["evidence"] is not None, (
        "the cell being mutated is not evidenced to begin with — this test would be vacuous"
    )

    mutated = copy.deepcopy(vf.VENUE_PROBES)
    mutated["BJC"]["preprint_friendly"][0]["anchor"] = "no publisher page contains this sentence"
    after = vf.build_report(probes=mutated, weights=weights)

    cell = after["venue_facts"]["BJC"]["criteria"]["preprint_friendly"]
    assert cell["value"] == vf.UNKNOWN, (
        f"a broken anchor left the value as {cell['value']!r}. The probe's declared value "
        "survived the loss of the thing that licensed it — which is fabrication with extra steps."
    )
    assert cell["evidence"] is None and cell["supporting_evidence"] == []

    before_score = next(c for c in baseline["shortlists"][0]["candidates"] if c["venue"] == "BJC")
    after_score = next(c for c in after["shortlists"][0]["candidates"] if c["venue"] == "BJC")
    assert round(before_score["score"] - after_score["score"], 2) == round(
        weights["terms"]["preprint_friendly"]["weight"], 2
    ), "the lost reading did not cost the venue its criterion's weight"
    assert after_score["n_unknown"] == before_score["n_unknown"] + 1
    assert after_score["evidence_coverage"] < before_score["evidence_coverage"]


def test_an_unreadable_fee_route_fails_CLOSED_rather_than_passing_as_free(vf, weights):
    """Second mutation, on the filter rather than a cell. CLAUDE.md §4: an absent reading is not
    a reading of absence. Break the probe that reads a venue's per-page charge and the venue must
    move to `needs_a_fetch` — never onto a shortlist as though it were free."""
    assert "CGT" in {row["venue"] for row in vf.build_report(weights=weights)["filter"]["failed"]}

    mutated = copy.deepcopy(vf.VENUE_PROBES)
    mutated["CGT"]["zero_dollar_route"][0]["anchor"] = "no publisher page contains this sentence"
    after = vf.build_report(probes=mutated, weights=weights)

    assert "CGT" not in {row["venue"] for row in after["filter"]["passed"]}
    assert "CGT" in {row["venue"] for row in after["filter"]["needs_a_fetch"]}
    for short in after["shortlists"]:
        assert "CGT" not in {c["venue"] for c in short["candidates"]}


def test_a_venue_whose_name_cannot_be_located_is_dropped_rather_than_named(vf, weights):
    """The identity probe is the same rule applied to the venue itself: a venue this repository
    cannot name from a committed file is one it does not know about."""
    mutated = copy.deepcopy(vf.VENUE_PROBES)
    mutated["GCC"]["identity"][0]["path"] = ["verdicts", "GCC", "no_such_field"]
    after = vf.build_report(probes=mutated, weights=weights)
    assert "GCC" not in after["venue_facts"]
    for short in after["shortlists"]:
        assert "GCC" not in {c["venue"] for c in short["candidates"]}


# -------------------------------------------------------------------------------------------
# 5 · shape, coverage and determinism
# -------------------------------------------------------------------------------------------
def test_every_criterion_named_in_the_architecture_spec_is_present(vf, report):
    expected = {
        "zero_dollar_route",
        "unaffiliated_author_permitted",
        "scope_match",
        "indexed_pubmed_or_europepmc",
        "preprint_friendly",
        "page_charge_exposure",
    }
    assert set(vf.CRITERIA) == expected, "the six criteria of §6.4 and the module have diverged"
    for venue in report["venue_facts"].values():
        assert set(venue["criteria"]) == expected


def test_every_weight_the_table_applies_is_declared_in_the_weights_file(vf, weights):
    """No weight, threshold or stopword may be typed in the module. Changing what a good cheap
    fit means must be a reviewable diff in one file."""
    declared = set(weights["terms"])
    assert declared == set(vf.CRITERIA) - {"zero_dollar_route"}
    source = VENUE_FIT_PY.read_text(encoding="utf-8")
    assert not re.search(r"^\s*[A-Z_]*WEIGHT\w*\s*=\s*[0-9]", source, re.M)
    for literal in ("0.4", "30.0", "25.0", "20.0", "-20.0"):
        assert f"= {literal}" not in source, f"weight {literal} is typed in the module"


def test_every_endpoint_targeting_a_journal_gets_a_shortlist(vf, report):
    endpoints = json.loads((REPO / "systems" / "graph" / "publications.json").read_text())
    expected = sorted(p["id"] for p in endpoints if p.get("target_venue") == "journal_submission")
    assert [s["publication"] for s in report["shortlists"]] == expected
    assert expected, "fixture is degenerate — no journal-submission endpoints"


def test_a_candidate_ranked_mostly_over_holes_says_so_at_the_point_of_use(report, weights):
    threshold = weights["unknown_policy"]["warn_below_coverage"]
    warned = 0
    for short in report["shortlists"]:
        for candidate in short["candidates"]:
            if candidate["evidence_coverage"] < threshold:
                assert "⚠_ranked_over_holes" in candidate, (
                    f"{candidate['venue']} is ranked on {candidate['n_unknown']} UNKNOWNs and "
                    "carries no warning. A rank built from holes reads as a finding."
                )
                warned += 1
    assert warned, "fixture is degenerate — no low-coverage candidates to warn about"


def test_the_table_selects_no_venue_and_authorises_no_submission(report, weights):
    """architecture §6.2 and CLAUDE.md §3. The output must not read as a decision — it carries
    the top three WITH their evidence, and never a recommendation alone."""
    assert "⛔_this_selects_nothing_and_authorises_nothing" in report
    cap = weights["escalation"]["carry_top_n"]
    for short in report["shortlists"]:
        assert "recommendation" not in short and "selected_venue" not in short
        assert len(short["escalation_carries"]) <= cap
        assert short["escalation_carries"] == [c["venue"] for c in short["candidates"][:cap]]


def test_the_table_is_deterministic(vf):
    first = json.dumps(vf.build_report(), ensure_ascii=False, sort_keys=True)
    second = json.dumps(vf.build_report(), ensure_ascii=False, sort_keys=True)
    assert first == second, "two runs disagree — every receipt built on this is unreadable"


def test_the_committed_artifact_matches_what_the_module_emits_today(vf):
    """A generated file that has drifted from its generator is a second home for the facts."""
    committed = REPO / "research" / "autonomy" / "venue-fit.json"
    if not committed.exists():
        pytest.skip("venue-fit.json not generated yet")
    on_disk = json.loads(committed.read_text(encoding="utf-8"))
    fresh = vf.build_report()
    assert on_disk["venue_facts"] == fresh["venue_facts"], (
        "research/autonomy/venue-fit.json is stale — re-run "
        "`python3 research/autonomy/venue_fit.py --write`"
    )
