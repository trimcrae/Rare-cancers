"""The census's honesty properties — above all that it cannot invent a universe.

⛔ THE ASYMMETRY THAT DRIVES THESE TESTS. A census that under-reports costs a fusion pair nobody screens.
A census that FABRICATES a fusion -> disease -> citation row is the exact defect preflight gate 4
(`lint_citations.py`) was built for after an agent produced a PMID present in no committed source
anywhere in this repository — and it passed `lint_claims` twice. So the load-bearing tests here are about
the failure paths: no source answering, a source answering with a schema nobody expected, and a verdict
being emitted from counts that were never measured.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fusion_junction_census as fjc  # noqa: E402


# ── the universe is fetched, never typed ────────────────────────────────────────────────────────
def test_no_source_answering_yields_zero_rows_and_exit_3(monkeypatch, tmp_path):
    """⛔ The single most important property. Every source down must produce an empty, self-declaring
    artifact and a nonzero exit — never a fallback list, never a partial guess."""
    monkeypatch.setattr(fjc, "OUT", str(tmp_path / "census.json"))
    monkeypatch.setattr(fjc, "_get", lambda url, timeout=180, accept=None: ("", 503, "HTTPError 503"))

    blob, rc = fjc.run_census()

    assert rc == 3
    assert blob["status"] == "no_universe_fetched"
    assert blob["rows"] == []
    assert blob["summary"]["n_fusion_pairs"] == 0
    assert all(not s.get("parsed") for s in blob["sources"])


def test_module_holds_no_hardcoded_fusion_table():
    """A literal fusion pair in module source would be a typed universe wearing a parser's clothes.

    The one permitted `::` pattern is the regex that RECOGNISES a fusion name, not a fusion.
    """
    src = open(fjc.__file__).read()
    # strip the docstring block and the regex definition, then look for GENE::GENE literals
    body = src.split('FUSION_NAME_RE', 1)[1]
    literals = [m for m in __import__("re").findall(r'"[A-Z][A-Z0-9]{1,14}::[A-Z][A-Z0-9]{1,14}"', body)]
    assert literals == [], f"module carries hardcoded fusion literals: {literals}"


# ── parser discipline ───────────────────────────────────────────────────────────────────────────
def test_columns_are_located_by_name_not_position():
    """A schema that gains a column must not silently shift the parse."""
    header = "molecular_profile\tdisease\tunexpected_new_column\ttherapies\tcitation_id"
    row = "BCR::ABL1\tchronic myeloid leukemia\tXXX\timatinib\t12345678"
    pairs, stats = fjc.parse_civic_evidence(f"{header}\n{row}")

    assert "BCR::ABL1" in pairs
    e = pairs["BCR::ABL1"]
    assert e["donor_gene"] == "BCR" and e["acceptor_gene"] == "ABL1"
    assert e["diseases"] == ["chronic myeloid leukemia"]
    assert e["existing_therapies"] == ["imatinib"]
    assert e["source_identifiers"] == ["12345678"]
    assert stats["columns_used"]["variant"] == "molecular_profile"


def test_unknown_schema_reports_an_error_rather_than_zero_rows():
    """⚠ An absent reading is not a reading of absence. A payload with no variant column must SAY it
    could not be parsed, not quietly contribute nothing and let the run look successful."""
    pairs, stats = fjc.parse_civic_evidence("some\tother\tschema\nvalues\tgo\there")
    assert pairs == {}
    assert "error" in stats and "no variant column" in stats["error"]


@pytest.mark.parametrize("name", ["V600E-like", "Exon 14-skipping", "BCR-ABL1", "AMPLIFICATION", ""])
def test_non_fusion_variant_names_are_rejected(name):
    """The legacy hyphen form is deliberately NOT accepted — it matches variants that are not fusions,
    and a permissive pattern seeds the catalog with rows no design could ever be built for."""
    assert fjc.FUSION_NAME_RE.match(name) is None


def test_fusion_names_are_normalised_to_upper_case():
    pairs, _ = fjc.parse_civic_evidence("variant\tdisease\nEWSR1::NR4A3\textraskeletal myxoid chondrosarcoma")
    assert "EWSR1::NR4A3" in pairs


# ── verdicts may only come from measured counts ─────────────────────────────────────────────────
def _stub_counts(monkeypatch, denom, modality, junction, loose=None):
    """Four arms since 2026-08-13: the loose full-text count runs first and is context only."""
    seq = iter([denom if loose is None else loose, denom, modality, junction])

    def fake_query(query, page_size=25):
        c = next(seq)
        return {"query": query, "http_status": 200 if c is not None else 500,
                "error": None if c is not None else "boom", "hit_count": c, "identifiers": []}

    monkeypatch.setattr(fjc, "epmc_query", fake_query)
    monkeypatch.setattr(fjc.time, "sleep", lambda *_: None)


@pytest.mark.parametrize("counts,expected", [
    ((120, 4, 2), "attempted"),
    ((120, 4, 0), "modality_touched"),
    ((120, 0, 0), "orphan"),
    ((0, 0, 0), "orphan"),
])
def test_verdicts_follow_the_counts(monkeypatch, counts, expected):
    _stub_counts(monkeypatch, *counts)
    assert fjc.classify_pair("GENEA", "GENEB")["verdict"] == expected


def test_the_verdict_ignores_the_loose_fulltext_count(monkeypatch):
    """⛔ THE SHAKEOUT DEFECT, PINNED (run 31740571888). `ACT::FOSB` returned 322 supposed
    junction-directed records because `ACT` matches the English word "act" in full text. A huge loose
    count must not be able to drag a verdict — the sharpened arms decide, and the loose count is
    recorded only as the corpus the absence claim sits inside."""
    _stub_counts(monkeypatch, denom=0, modality=0, junction=0, loose=99999)
    out = fjc.classify_pair("ACT", "FOSB")
    assert out["verdict"] == "orphan"
    assert out["queries"]["denominator_loose_fulltext"]["hit_count"] == 99999


def test_short_symbols_are_flagged_for_a_human_read(monkeypatch):
    """A three-letter symbol is an English word too. The flag does not change the verdict; it names
    which verdicts cannot be trusted unread."""
    _stub_counts(monkeypatch, 50, 10, 5)
    out = fjc.classify_pair("ACT", "FOSB")
    assert out["ambiguous_symbols"] == ["ACT"]
    assert out["needs_human_read"] is True

    _stub_counts(monkeypatch, 50, 10, 5)
    clean = fjc.classify_pair("EWSR1", "NR4A3")
    assert clean["ambiguous_symbols"] == []
    assert clean["needs_human_read"] is False


def test_gene_tokens_are_restricted_to_title_and_abstract(monkeypatch):
    """The sharpening the shakeout forced: full-text co-occurrence is not evidence about a fusion."""
    _stub_counts(monkeypatch, 1, 0, 0)
    out = fjc.classify_pair("EWSR1", "NR4A3")
    assert 'TITLE_ABS:"EWSR1"' in out["queries"]["denominator"]["query"]
    assert '"EWSR1::NR4A3"' in out["queries"]["denominator"]["query"]
    assert "TITLE_ABS" not in out["queries"]["denominator_loose_fulltext"]["query"]


def test_a_failed_query_is_screen_failed_not_orphan(monkeypatch):
    """⛔ THE DANGEROUS DIRECTION. A query that did not run returns no hits, and 'no hits' is exactly what
    'orphan' looks like — so a network failure would silently manufacture the paper's headline finding."""
    _stub_counts(monkeypatch, 120, None, None)
    assert fjc.classify_pair("GENEA", "GENEB")["verdict"] == "screen_failed"


def test_every_verdict_carries_its_query_strings_verbatim(monkeypatch):
    """An absence claim a reader cannot re-run is not evidence."""
    _stub_counts(monkeypatch, 10, 0, 0)
    out = fjc.classify_pair("EWSR1", "NR4A3")
    for arm in ("denominator", "modality", "junction_directed"):
        q = out["queries"][arm]["query"]
        assert "EWSR1" in q and "NR4A3" in q
    assert "antisense" in out["queries"]["modality"]["query"]
    assert "breakpoint" in out["queries"]["junction_directed"]["query"]


# ── artifact integrity ──────────────────────────────────────────────────────────────────────────
def test_check_fails_when_summary_disagrees_with_rows(tmp_path, monkeypatch):
    """The summary is DERIVED, never typed (CLAUDE.md rule 1.1). --check is what enforces that."""
    p = tmp_path / "census.json"
    blob = fjc._envelope("ok", [{"fusion": "A::B", "verdict": "orphan"}], [])
    blob["summary"]["n_fusion_pairs"] = 999          # hand-carried drift
    p.write_text(json.dumps(blob))
    monkeypatch.setattr(fjc, "OUT", str(p))
    assert fjc.check() == 1


def test_check_refuses_rows_under_a_no_universe_status(tmp_path, monkeypatch):
    p = tmp_path / "census.json"
    blob = fjc._envelope("no_universe_fetched", [{"fusion": "A::B", "verdict": "orphan"}], [])
    p.write_text(json.dumps(blob))
    monkeypatch.setattr(fjc, "OUT", str(p))
    assert fjc.check() == 1


def test_envelope_states_what_a_verdict_is_not():
    """The EMC manuscript states this limit for its own first-in-kind claim; a catalog making the same
    claim N times must carry it in the artifact rather than leave it to the reader."""
    env = fjc._envelope("ok", [], [])
    assert "not proof that no such work exists" in env["⚠_what_a_verdict_is_not"]
    assert "no row is a clinical recommendation" in env["⚠_an_orphan_is_not_a_target"]


# ── measured against the real CIViC headers (probe run 31739900759, 2026-08-13) ─────────────────
CIVIC_EVIDENCE_HEADER = (
    "molecular_profile\tmolecular_profile_id\tdisease\tdoid\tphenotypes\ttherapies\t"
    "therapy_interaction_type\tevidence_type\tevidence_direction\tevidence_level\tsignificance\t"
    "evidence_statement\tcitation_id\tsource_type")
CIVIC_VARIANT_HEADER = (
    "variant_id\tvariant_civic_url\tfeature_type\tfeature_id\tfeature_name\tfeature_civic_url\t"
    "variant\tvariant_aliases\tis_flagged\tvariant_groups\tvariant_types\t"
    "single_variant_molecular_profile_id\tlast_review_date")


def test_real_civic_evidence_header_is_parsed():
    """Guards against a schema drift that would silently empty the universe."""
    row = ("BCR::ABL1 T315I\t123\tchronic myeloid leukemia\tDOID:8552\t\tponatinib\t\t"
           "Predictive\tSupports\tB\tSensitivity\tstatement\t12345678\tPubMed")
    pairs, stats = fjc.parse_civic_evidence(f"{CIVIC_EVIDENCE_HEADER}\n{row}")
    assert stats.get("error") is None
    assert stats["columns_used"]["variant"] == "molecular_profile"
    assert "BCR::ABL1" in pairs, "a fusion inside a compound molecular profile must still be found"
    assert pairs["BCR::ABL1"]["existing_therapies"] == ["ponatinib"]


def test_real_civic_variant_header_is_parsed():
    row = ("1\turl\tfusion\t7\tEWSR1::NR4A3\turl\tEWSR1::NR4A3\t\tFalse\t\ttranscript_fusion\t9\t2024")
    pairs, stats = fjc.parse_civic_variants(f"{CIVIC_VARIANT_HEADER}\n{row}")
    assert stats.get("error") is None
    assert "EWSR1::NR4A3" in pairs


def test_a_compound_profile_does_not_lose_its_fusion():
    """⛔ THE DIRECTION THAT MATTERS. A whole-string match drops `BCR::ABL1 T315I` on the floor, making
    the universe look SMALLER than it is — an under-count that reads as a clean measurement."""
    assert [t[2] for t in fjc._fusion_tokens("BCR::ABL1 T315I")] == ["BCR::ABL1"]
    assert [t[2] for t in fjc._fusion_tokens("EWSR1::NR4A3")] == ["EWSR1::NR4A3"]
    assert fjc._fusion_tokens("BRAF V600E") == []
    assert fjc._fusion_tokens("Exon 14-skipping") == []


def test_html_landing_page_is_not_counted_as_a_data_source(monkeypatch, tmp_path):
    """⚠ Measured: Mitelman and FusionGDB2 answer 200 with HTML. Two decorative arms must not read as
    live coverage."""
    monkeypatch.setattr(fjc, "OUT", str(tmp_path / "census.json"))
    monkeypatch.setattr(fjc, "_get",
                        lambda url, timeout=180, accept=None: ("<!DOCTYPE html><html></html>", 200, None))
    _universe, per_source = fjc.fetch_universe()
    parserless = [s for s in per_source if not s.get("parsed")]
    assert parserless, "expected the parserless arms to be reported"
    assert any(s.get("served_html_not_data") for s in parserless)


# ── the known-answer control, and the guards the first full run forced ───────────────────────────
def test_all_vocabularies_are_title_abs_restricted():
    """⛔ THE DEFECT THE CONTROL CAUGHT (run 31741055846). Gene tokens were TITLE_ABS-restricted but the
    modality and junction words matched anywhere in full text, so a paper mentioning "siRNA" in its
    methods and "breakpoint" in its discussion counted as an attempt on the junction. That scored
    EWSR1::NR4A3 as `attempted` against a published count of zero."""
    assert "TITLE_ABS" in fjc.MODALITY_TERMS
    assert "TITLE_ABS" in fjc.JUNCTION_TERMS
    for word in ("siRNA", "gapmer", "antisense"):
        assert f'TITLE_ABS:"{word}"' in fjc.MODALITY_TERMS
    for word in ("junction", "breakpoint"):
        assert f'TITLE_ABS:"{word}"' in fjc.JUNCTION_TERMS


def test_the_control_is_the_emc_pair_and_expects_orphan():
    """The one pair in this universe whose answer is independently known."""
    assert fjc.CONTROL_FUSION == ("EWSR1", "NR4A3")
    assert fjc.CONTROL_EXPECTED == "orphan"
    assert "5,153" in fjc.CONTROL_BASIS


def test_a_failing_control_changes_the_artifact_status(monkeypatch, tmp_path):
    """⛔ THE FIRST FULL RUN REPORTED `status: ok` WHILE FAILING THIS CONTROL. A census that disagrees
    with the only checkable case must say so in its own status, not leave it to a reader who happens
    to know the EMC literature."""
    monkeypatch.setattr(fjc, "OUT", str(tmp_path / "census.json"))
    monkeypatch.setattr(fjc, "fetch_universe",
                        lambda: ({"A::B": {"donor_gene": "A", "acceptor_gene": "B", "fusion": "A::B",
                                           "diseases": [], "existing_therapies": [],
                                           "source_identifiers": [], "universe_sources": ["x"]}},
                                 [{"name": "x", "parsed": True}]))
    monkeypatch.setattr(fjc, "classify_pair",
                        lambda d, a: {"verdict": "attempted", "ambiguous_symbols": [],
                                      "needs_human_read": False, "queries": {}})

    blob, rc = fjc.run_census(resume=False)

    assert blob["status"] == "ok_but_control_failed"
    assert blob["known_answer_control"]["passed"] is False
    assert blob["known_answer_control"]["observed_verdict"] == "attempted"


def test_a_passing_control_leaves_status_ok(monkeypatch, tmp_path):
    monkeypatch.setattr(fjc, "OUT", str(tmp_path / "census.json"))
    monkeypatch.setattr(fjc, "fetch_universe",
                        lambda: ({"A::B": {"donor_gene": "A", "acceptor_gene": "B", "fusion": "A::B",
                                           "diseases": [], "existing_therapies": [],
                                           "source_identifiers": [], "universe_sources": ["x"]}},
                                 [{"name": "x", "parsed": True}]))
    monkeypatch.setattr(fjc, "classify_pair",
                        lambda d, a: {"verdict": "orphan", "ambiguous_symbols": [],
                                      "needs_human_read": False, "queries": {}})
    blob, rc = fjc.run_census(resume=False)
    assert blob["status"] == "ok"
    assert blob["known_answer_control"]["passed"] is True


def test_transient_5xx_is_retried_before_being_called_a_failure(monkeypatch):
    """23 of 198 pairs were lost to Europe PMC 502/503/504 in one contiguous window. A throttled
    server must not read as an unscreenable fusion."""
    calls = {"n": 0}

    def flaky(url, timeout=180, accept=None):
        calls["n"] += 1
        if calls["n"] < 3:
            return "", 503, "HTTPError 503"
        return json.dumps({"hitCount": 0, "resultList": {"result": []}}), 200, None

    monkeypatch.setattr(fjc, "_get", flaky)
    monkeypatch.setattr(fjc.time, "sleep", lambda *_: None)
    out = fjc.epmc_query("anything")
    assert out["hit_count"] == 0 and out["error"] is None
    assert calls["n"] == 3


def test_non_gene_tokens_are_rejected_and_recorded(monkeypatch):
    """`ACT` is not an approved symbol. The rejection must be visible — a filter whose removals nobody
    can see is indistinguishable from a filter that is not running."""
    fjc.REJECTED_TOKENS.clear()
    monkeypatch.setattr(fjc, "_resolve_symbol",
                        lambda s: None if s == "ACT" else s)
    assert fjc._fusion_tokens("ACT::FOSB") == []
    assert "ACT::FOSB" in fjc.REJECTED_TOKENS
    fjc.REJECTED_TOKENS.clear()


def test_an_ambiguous_alias_is_rejected_rather_than_guessed(monkeypatch):
    fjc.REJECTED_TOKENS.clear()
    monkeypatch.setattr(fjc, "_resolve_symbol",
                        lambda s: "__AMBIGUOUS__" if s == "NOR1" else s)
    assert fjc._fusion_tokens("EWSR1::NOR1") == []
    assert "ambiguous" in fjc.REJECTED_TOKENS["EWSR1::NOR1"]
    fjc.REJECTED_TOKENS.clear()


def test_aliases_resolve_to_the_approved_symbol(monkeypatch):
    monkeypatch.setattr(fjc, "_resolve_symbol", lambda s: {"EWS": "EWSR1"}.get(s, s))
    assert [t[2] for t in fjc._fusion_tokens("EWS::NR4A3")] == ["EWSR1::NR4A3"]
