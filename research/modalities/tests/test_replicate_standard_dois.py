"""The citation guard for the replicate/uncertainty field-standard harvest: HIT is not identity.

WHY THESE TESTS EXIST (2026-07-29). `replicate_standard_harvest` verifies every candidate DOI against
Crossref because "a DOI that 404s is a DOI that does not exist -- which is exactly the fabrication mode
the repo's golden rule forbids". The 2026-07-29 harvest (`_replicate_standard/harvest-summary.json` on
the `replicate-standard-cache` branch, generated 10:49:15Z) showed the guard has a hole one size larger
than the one it closes:

    bhati2022_largescale -> 10.1021/acs.jctc.1c00669 -> HIT
    title: "Residue-Residue Contact Changes during Functional Processes Define Allosteric
            Communication Pathways"

A real, resolvable DOI -- for a completely different paper than the large-scale RBFE study the key was
entered as. It printed `HIT`, it stayed out of the "unresolved (DO NOT CITE)" list, and a note author
reading that summary would have cited a paper nobody in this repo has read. The identifier existing and
the identifier naming the intended work are two claims, and only the first was ever measured.

What must never regress silently is therefore the RULE, which is pure and pinned here. The network half
(Crossref itself) is exercised by the workflow on a runner, as it must be -- the dev sandbox's egress
proxy 403s publisher domains.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import replicate_standard_harvest as h  # noqa: E402


# ---- _norm_title ------------------------------------------------------------------------------
def test_norm_title_survives_the_punctuation_crossref_actually_returns():
    # The real title uses an EN-DASH; a raw substring test would call a right paper wrong, and a
    # fabrication guard that cries wolf is a guard that gets switched off.
    assert h._norm_title("Large Scale Study of Ligand–Protein Relative Binding Free Energies") \
        .startswith("large scale study of ligand protein")


def test_norm_title_of_nothing_is_empty_not_a_crash():
    assert h._norm_title(None) == ""
    assert h._norm_title("") == ""


# ---- identity_verdict -------------------------------------------------------------------------
def test_a_miss_has_no_identity_question_to_answer():
    assert h.identity_verdict("gowers2023_openfe", "MISS", None) == "N/A"


def test_the_measured_wrong_paper_case_is_caught():
    """THE DEFECT THIS PINS, with the exact string Crossref returned on 2026-07-29."""
    v = h.identity_verdict(
        "bhati2022_largescale", "HIT",
        "Residue–Residue Contact Changes during Functional Processes Define Allosteric "
        "Communication Pathways")
    assert v == "WRONG-PAPER"


def test_the_replacement_doi_is_confirmed_by_the_same_rule():
    v = h.identity_verdict(
        "bhati2022_largescale_real", "HIT",
        "Large Scale Study of Ligand–Protein Relative Binding Free Energy Calculations: "
        "Actionable Predictions from Statistically Robust Enhanced Sampling Free Energy Simulations")
    assert v == "CONFIRMED"


def test_a_key_with_no_expected_title_is_UNCHECKED_and_never_CONFIRMED():
    # "We did not look" and "we looked and it was right" are different states. Reporting the first as
    # the second is the failure mode this repo keeps paying for.
    assert "baumann2023_cycleclosure" not in h.EXPECTED_TITLE
    assert h.identity_verdict("baumann2023_cycleclosure", "HIT", "Anything At All") == "UNCHECKED"


# ---- citable ----------------------------------------------------------------------------------
def test_only_a_confirmed_hit_is_citable():
    assert h.citable({"status": "HIT", "identity": "CONFIRMED"}) is True
    for row in ({"status": "HIT", "identity": "WRONG-PAPER"},
                {"status": "HIT", "identity": "UNCHECKED"},
                {"status": "HIT"},                      # pre-identity summary: not a licence
                {"status": "MISS", "identity": "N/A"}):
        assert h.citable(row) is False, row


# ---- the candidate list itself ----------------------------------------------------------------
def test_the_wrong_doi_is_retained_not_deleted():
    """Deleting it would let the same recollection be re-entered tomorrow with nothing to contradict
    it. It stays, graded WRONG-PAPER, beside the DOI that is actually correct."""
    assert h.CANDIDATE_DOIS["bhati2022_largescale"] == "10.1021/acs.jctc.1c00669"
    assert h.CANDIDATE_DOIS["bhati2022_largescale_real"] == "10.1021/acs.jctc.1c01288"
    assert h.CANDIDATE_DOIS["bhati2022_largescale"] != h.CANDIDATE_DOIS["bhati2022_largescale_real"]


def test_every_expected_title_belongs_to_a_real_candidate():
    orphans = sorted(set(h.EXPECTED_TITLE) - set(h.CANDIDATE_DOIS))
    assert orphans == [], f"EXPECTED_TITLE names keys that are not candidates: {orphans}"


def test_no_two_candidates_share_a_doi():
    seen = {}
    for k, d in h.CANDIDATE_DOIS.items():
        assert d.lower() not in seen, f"{k} duplicates {seen.get(d.lower())}"
        seen[d.lower()] = k
