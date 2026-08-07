"""The C05 / Q7 gate logic, exercised with NO network and NO retrieval.

⛔ WHAT THESE TESTS ARE FOR. Two of the three defects this module shipped with were found on a dry
run against the real corpus, not by reasoning, and BOTH pushed the verdict toward a false negative:

  (a) ubiquitin CHAIN-LINKAGE positions (K48/K63) were counted as substrate ubiquitination sites;
  (b) `\\bbrd4\\b` did not match `Brd4BD2`, so the two most decisive spans in the whole corpus — the
      eight mapped sites and the K456R single-mutant result — were dropped by the gate's own parser.

Both are pinned below, because a gate that quietly loses its best evidence and reports
STOP_NO_REFERENCE is the absent-reading-as-absence failure arriving from inside the parser rather
than from the network (CLAUDE.md §4).

The fixtures are SYNTHETIC sentences written to exercise the tokenizer. They assert no fact about any
real paper and none of them is evidence about anything.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import v18_lysine_reference_precheck as v18  # noqa: E402


GENES = ["BRD4", "SMARCA2", "SMARCA4"]


# -------------------------------------------------------------------------------------------------
# The tokenizer
# -------------------------------------------------------------------------------------------------
def test_a_span_needs_a_residue_a_ubiquitin_context_and_a_measurement():
    """Any two of the three is not a mapped site, and each omission has a distinct meaning."""
    residue_and_ubi_only = "Ubiquitination of the substrate was observed at K456 in these cells."
    ubi_and_measure_only = ("Mass spectrometry showed the substrate was ubiquitinated after "
                            "treatment with the degrader compound.")
    residue_and_measure_only = ("Mass spectrometry of the K456R mutant showed a reduced binding "
                                "affinity in the assay used throughout this work.")
    good = ("We identified by mass spectrometry a diGly remnant on K456 of Brd4BD2, confirming "
            "ubiquitination at that site.")
    assert v18.spans(residue_and_ubi_only) == []
    assert v18.spans(ubi_and_measure_only) == []
    assert v18.spans(residue_and_measure_only) == []
    assert len(v18.spans(good)) == 1


def test_span_length_bounds_are_the_pre_registered_ones():
    short = "K1 ubiquitin MS."
    assert len(short) < v18.PREREG["span_min_chars"]
    assert v18.spans(short) == []


# -------------------------------------------------------------------------------------------------
# DEFECT (a) — ubiquitin chain-linkage lysines are not substrate sites
# -------------------------------------------------------------------------------------------------
def test_a_k48_linked_chain_names_zero_substrate_lysines():
    """The first draft scored this sentence as naming a substrate site. It names none."""
    s = "The degrader promoted K48-linked polyubiquitin chain formation on the target protein."
    assert v18.linkage_lysines(s) == [48]
    assert v18.lysines_named(s) == []


def test_k48_and_k63_together_in_a_chain_context_are_both_excluded():
    s = ("Dual K48/K63 ubiquitin chain editing was detected by mass spectrometry after "
         "degrader treatment.")
    assert v18.lysines_named(s) == []


def test_a_substrate_lysine_that_happens_to_be_48_survives_without_a_linkage_cue():
    """⚠ The exclusion must not become a blacklist of numbers — a real Lys48 site must still count."""
    s = ("We mapped by mass spectrometry a diGly remnant at Lys48 of Brd4BD2, identifying it as an "
         "MZ1-induced ubiquitination site.")
    assert v18.linkage_lysines(s) == []
    assert v18.lysines_named(s) == [48]


def test_the_exclusion_is_reported_not_silently_applied():
    """A dropped number a reader cannot see is a number they cannot disagree with."""
    corpus = _one_record_corpus(
        "K48-linked polyubiquitin chains on Brd4BD2 were detected by mass spectrometry.")
    ternary = {"genes": GENES, "by_gene": {}, "_source": "x", "error": None}
    scanned = v18.scan(corpus, ternary)
    assert scanned["n_candidate_spans"] == 1
    row = scanned["candidates"][0]
    assert row["ubiquitin_linkage_lysines_excluded_from_that_count"] == [48]
    assert row["lysines_named_in_span"] == []
    # No substrate residue named -> G2 cannot pass on it, however on-substrate the sentence looks.
    assert row["passes_G2_ternary_solved_substrate"] is False


# -------------------------------------------------------------------------------------------------
# DEFECT (b) — the alias must match a suffixed structural domain
# -------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "eight ubiquitination sites on Brd4BD2 identified by mass spectrometry",
    "Lys346 on BRD4BD2 was mapped by mass spectrometry",
    "ubiquitination of Brd4 BD2 measured by mass spectrometry",
    "the SMARCA2BD construct was ubiquitinated, as shown by mass spectrometry",
])
def test_a_domain_suffixed_gene_name_still_matches_its_gene(text):
    """The plain-word-boundary version dropped every one of these — the decisive spans."""
    assert v18.substrate_hits(text, GENES)


def test_the_alias_does_not_match_an_unrelated_longer_word():
    """The suffix allowance is narrow on purpose; it must not turn into a substring match."""
    assert v18.substrate_hits("the brd4like pseudogene was not measured", GENES) == []


# -------------------------------------------------------------------------------------------------
# G2 is decided on the SPAN, never on the paper
# -------------------------------------------------------------------------------------------------
def test_a_substrate_named_only_elsewhere_in_the_paper_does_not_pass_g2():
    """The real false positive: an IRE1 measurement in a paper whose intro mentions BRD4."""
    body = ("BRD4 degraders such as MZ1 have been widely studied.\n"
            "We identified by mass spectrometry that ubiquitination of IRE1 occurs at K704.")
    corpus = _one_record_corpus(body)
    ternary = {"genes": GENES, "by_gene": {}, "_source": "x", "error": None}
    scanned = v18.scan(corpus, ternary)
    rows = [r for r in scanned["candidates"] if r["lysines_named_in_span"] == [704]]
    assert rows, "the IRE1 span should still be surfaced as a candidate"
    row = rows[0]
    assert row["ternary_solved_substrates_named_IN_THE_SPAN"] == []
    assert row["substrates_named_anywhere_in_paper"] == ["BRD4"]
    assert row["passes_G2_ternary_solved_substrate"] is False


# -------------------------------------------------------------------------------------------------
# The four-valued verdict, and the register's prediction
# -------------------------------------------------------------------------------------------------
def _one_record_corpus(body, slug="s1"):
    return [{"slug": slug, "why_this_query": "test", "loaded": True, "n_records": 1,
             "n_full_texts_on_disk": 1, "error": None,
             "records": [{"pmid": "1", "pmcid": "PMC1", "doi": None, "year": 2024,
                          "title": "t", "journal": "j", "abstract": "", "full_text": body,
                          "has_full_text": True}]}]


def _ternary_ok():
    return {"genes": GENES, "by_gene": {g: {"n_ternary": 1, "pdb_ids": []} for g in GENES},
            "_source": "s-calibrator-survey.json", "error": None}


def test_an_unloaded_corpus_is_undetermined_and_never_a_negative():
    """⛔ THE LOAD-BEARING ONE. A retrieval that did not land must not read as 'nothing exists'."""
    corpora = [{"slug": "s1", "loaded": False, "error": "not fetched"}]
    ternary = _ternary_ok()
    scanned = v18.scan(corpora, ternary)
    v = v18.verdict(corpora, ternary, scanned)
    assert v["decision"] == "UNDETERMINED"
    assert "STOP" not in v["decision"]


def test_a_partial_read_is_also_undetermined():
    """One of two corpora missing is a partial read; a negative off it would be a partial negative."""
    corpora = _one_record_corpus("nothing of interest here at all in this sentence.")
    corpora.append({"slug": "s2", "loaded": False, "error": "not fetched"})
    ternary = _ternary_ok()
    v = v18.verdict(corpora, ternary, v18.scan(corpora, ternary))
    assert v["decision"] == "UNDETERMINED"


def test_an_unreadable_survey_blocks_g2_rather_than_rejecting_everything():
    """If the gene list failed to load, G2's rejections are meaningless and must not produce a STOP."""
    corpora = _one_record_corpus("no relevant sentence.")
    ternary = {"genes": [], "by_gene": {}, "_source": "x", "error": "boom"}
    v = v18.verdict(corpora, ternary, v18.scan(corpora, ternary))
    assert v["decision"] == "UNDETERMINED"


def test_a_clean_read_with_nothing_in_it_is_stop_no_reference():
    corpora = _one_record_corpus("This paper contains no mapped ubiquitination site of any kind.")
    ternary = _ternary_ok()
    v = v18.verdict(corpora, ternary, v18.scan(corpora, ternary))
    assert v["decision"] == "STOP_NO_REFERENCE"
    assert v["prediction_outcome"].startswith("NOT REACHED")


def test_several_lysines_in_one_span_is_weakly_diagnostic_and_confirms_the_register():
    """⚠ The outcome the register PREDICTED. A find that every prediction hits is not a known answer."""
    corpora = _one_record_corpus(
        "We consistently identified eight ubiquitination sites on Brd4BD2 (K333, K346, K349, K355, "
        "K362, K368, K445, and K456), each identified by mass spectrometry.")
    ternary = _ternary_ok()
    v = v18.verdict(corpora, ternary, v18.scan(corpora, ternary))
    assert v["decision"] == "FOUND_BUT_WEAKLY_DIAGNOSTIC"
    assert v["prediction_outcome"] == "CONFIRMED"
    assert v["gates"]["G3_diagnosticity"]["pass"] is False


def test_a_source_reporting_redundancy_drops_a_single_lysine_find_to_weak():
    """One named lysine is not enough if the source says removing it changes nothing."""
    corpora = _one_record_corpus(
        "We mapped by mass spectrometry a single diGly remnant at K456 of Brd4BD2. "
        "Notably, the lysine-less construct was still degraded.")
    ternary = _ternary_ok()
    v = v18.verdict(corpora, ternary, v18.scan(corpora, ternary))
    assert v["decision"] == "FOUND_BUT_WEAKLY_DIAGNOSTIC"


def test_a_single_lysine_with_no_redundancy_is_the_only_diagnostic_outcome():
    corpora = _one_record_corpus(
        "We mapped by mass spectrometry a single diGly remnant at K1464 of SMARCA4.")
    ternary = _ternary_ok()
    v = v18.verdict(corpora, ternary, v18.scan(corpora, ternary))
    assert v["decision"] == "FOUND_AND_DIAGNOSTIC"
    assert v["prediction_outcome"].startswith("NOT CONFIRMED")


# -------------------------------------------------------------------------------------------------
# Contracts that must not drift
# -------------------------------------------------------------------------------------------------
def test_the_gene_list_is_read_from_the_survey_and_not_typed_into_this_module():
    """Rule 1: the ternary-solved substrate list has one home, and it is not here."""
    t = v18.ternary_solved_substrates()
    assert t["error"] is None, t["error"]
    assert t["genes"], "the survey must supply the gene list"
    src = open(v18.__file__, encoding="utf-8").read()
    # The module may name aliases, but must not carry its own list of which genes have ternaries.
    assert "n_ternary" in src  # it reads the field
    assert t["_source"] == "s-calibrator-survey.json"


def test_the_routed_map_edits_carry_every_field_verify_map_edits_requires():
    import verify_map_edits as vme
    for edit in v18.map_edits_required({"decision": "STOP_NO_REFERENCE"}):
        missing = [f for f in vme.REQUIRED_FIELDS if f not in edit]
        assert not missing, missing


def test_the_routed_map_edits_still_apply_to_the_live_map():
    """⛔ The categorical audit shipped nine edits and all nine were dead on arrival."""
    import verify_map_edits as vme
    with open(vme.DEFAULT_MAP, encoding="utf-8") as fh:
        map_text = fh.read()
    for edit in v18.map_edits_required({"decision": "STOP_NO_REFERENCE"}):
        row = vme.check_edit(edit, map_text)
        assert row.get("ok"), (row["status"], row.get("detail"))


def test_the_caveat_and_null_rule_exist_and_refuse_to_claim_a_pass():
    assert "not passing" in v18.caveat()
    assert "proposed" in v18.caveat()
    assert "REFUTES" in v18.null_rejection_rule()
