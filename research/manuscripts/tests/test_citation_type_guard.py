"""`lint_citation_types` must go RED on the 2026-08-26 defect and stay GREEN on honest prose.

⛔ WHY EVERY TEST HERE MUTATES RATHER THAN ASSERTS A CLEAN TREE. A guard that fails OPEN and a guard
that is genuinely satisfied render identically — the defect this repository keeps paying for. So each
test takes a REAL sentence out of a REAL committed file, mutates it into the shape the guard exists
to catch, and asserts the guard names that row. Every mutation asserts it LANDED (`count(old) == 1`)
before any result is read, because a mutation that silently missed produces a green run that reads
exactly like a caught one.

⛔ AND EVERY MUTATION IS ON A COPY. `claims()` takes its root, so the corpus under test is a tmp_path
tree, never the working tree. `research-loop` §3 added that rule on 2026-08-27 after a mutation
window in the SHARED tree let 13 inverted claims reach origin/main.

Attribution: the fixtures below quote `article_types` and DOIs retrieved from PubMed and cached in
`research/manuscripts/citation-article-types.json`; PubMed's terms require both to travel together.
"""
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MANUSCRIPTS))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MANUSCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lct = _load("lint_citation_types")


# --------------------------------------------------------------------------------------------
# the cache artifact
# --------------------------------------------------------------------------------------------

def test_the_cache_exists_and_every_record_carries_its_doi_link():
    """⚠ PubMed's terms require attribution AND a resolvable DOI wherever its metadata travels."""
    recs, index = lct.load_cache()
    assert recs, "the publication-type cache is the whole offline evidence base"
    for pmid, rec in recs.items():
        assert rec["article_types"], "%s has no article_types — an empty list is not a reading" % pmid
        assert rec["doi_url"] and rec["doi_url"].startswith("https://doi.org/"), \
            "%s carries no DOI link; PubMed metadata may not travel without one" % pmid
        assert rec.get("retrieved_utc"), "a cache row without a date cannot be judged stale"
    doc = json.load(open(lct.CACHE, encoding="utf-8"))
    assert "PubMed" in doc["_attribution"]


def test_the_four_incident_identifiers_are_cached_with_the_types_that_discriminate_them():
    """The 2026-08-26 misattribution, as data. Exactly one of the four is a Review."""
    recs, index = lct.load_cache()
    got = {p: recs[index[("PMCID", p)]]["article_types"]
           for p in ("PMC7563993", "PMC12398172", "PMC12376927", "PMC9131214")}
    assert "Review" in got["PMC7563993"]
    assert "Review" not in got["PMC12398172"]      # Japanese national-registry cohort, n = 171
    assert "Case Reports" in got["PMC12376927"]
    assert "Case Reports" in got["PMC9131214"]
    assert sum("Review" in v for v in got.values()) == 1


def test_the_cache_is_not_an_anchor_for_the_provenance_gate():
    """⛔ The 2026-08-07 self-anchoring defect, applied forward — see `lint_citations.survey`."""
    lc = _load("lint_citations")
    assert lc.TYPE_CACHE_REL == os.path.relpath(lct.CACHE, ROOT).replace(os.sep, "/")
    src = open(os.path.join(MANUSCRIPTS, "lint_citations.py"), encoding="utf-8").read()
    assert "TYPE_CACHE_REL)" in src, "the exclusion must be in survey()'s anchor filter"


# --------------------------------------------------------------------------------------------
# the scanner: what it binds and what it deliberately does not
# --------------------------------------------------------------------------------------------

def _corpus(tmp_path, text, name="doc.md"):
    (tmp_path / name).write_text(text, encoding="utf-8")
    return lct.claims(paths=[name], root=str(tmp_path))


@pytest.mark.parametrize("text", [
    "The 2025 comprehensive review (PMID 41055792) names it.",
    "a single review (PMC7563993 alone — the only actual review among the four).",
    "figures read from the 2025 review's full text, PMC12504171.",
    "It is from the 2012 two-case report, PMID 23058004.",
    "the only randomised placebo-controlled trial in an indolent tumour (desmoid, PMID 30575484).",
    #: ⛔⛔ THE SUBMISSION-MANUSCRIPT FORM, AND IT WAS ABSENT FROM THIS LIST WHILE THE GATE WAS BLIND
    #: TO EVERY PAPER WRITTEN IN IT. Round 21's citations seat measured `_SCAN` returning 0 matches
    #: on fusion-junction-aso-journal-article.md, 0 on the extended report and 0 on the SI — because
    #: `!` was excluded from the connector and every citation in those documents crosses `<!--` to
    #: reach its identifier. ★ THE FIXTURES SHARED THE CODE'S ASSUMPTION: all five shapes above are
    #: bare-inline, so nothing here could have falsified it. A positive fixture in the form the
    #: outgoing papers actually use is the only thing that makes the blindness detectable, which is
    #: why these two are the first entries a reviewer of this list should check still exist.
    "The 2025 comprehensive review<sup>3</sup><!--PMID:41055792--> names it.",
    "It is from the 2012 two-case report<sup>11</sup><!--PMID:23058004--> read in full.",
])
def test_the_attributive_shapes_this_repository_actually_writes_are_bound(tmp_path, text):
    assert _corpus(tmp_path, text), "a real committed shape must be seen as a type claim"


def test_the_submission_manuscripts_are_actually_reachable_by_this_gate(tmp_path):
    """⛔⛔ THE FIXTURE ABOVE PROVES THE SHAPE PARSES. THIS PROVES THE REAL DOCUMENTS ARE SEEN.

    A synthetic fixture can pass while the gate still returns nothing on the committed papers — the
    two are different claims, and it was the second that was false for as long as the comment form
    has been in use. So this asserts against the tree: the journal article must yield at least one
    type claim to `_SCAN`. If a future edit removes the last type word from that paper this test
    fails and should be RE-ANCHORED to whichever outgoing document carries one — never deleted,
    because a gate reporting `0 error(s)` over `0 claims` in the papers being posted is exactly the
    state this catches.
    """
    import re as _re
    art = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "aso", "fusion-junction-aso-journal-article.md")
    text = open(art, encoding="utf-8").read()
    n_comment_citations = len(_re.findall(r"<sup>\d+</sup><!--PMID:", text))
    assert n_comment_citations > 0, (
        f"{os.path.basename(art)} carries no comment-form citations, so this guard is watching for "
        "a shape the document no longer uses — re-anchor it rather than deleting it")
    seen = list(lct._SCAN.finditer(text))
    assert seen, (
        f"{os.path.basename(art)} has {n_comment_citations} comment-form citations and lint_citation_types "
        "binds NONE of them. The gate will report '0 error(s)' having examined nothing in a paper "
        "about to be posted. Check the connector class in _SCAN: it must let `<!--` through.")


@pytest.mark.parametrize("text,why", [
    ("Target nomination clears peer review at real journals (PMID 37997254).", "peer review"),
    ("It begins with the external review pass and ends at PMID 41055792.", "external review"),
    ("Found by a blind adversarial review seat, PMID 41055792.", "adversarial review"),
    ("Three of the four are not review literature — PMC12398172 is a cohort.", "negated"),
    ("(a *KIT* mutation in an EMC case report) and PMID: 25097177", "closed parenthetical"),
    ("| **`Review`** | review literature |\n| PMC12398172 | 40885991 |", "table cell boundary"),
    ("This is a review.\n\nSeparately, PMID 41055792 says otherwise.", "sentence boundary"),
    ("an 18-case series, PMID 12378528", "`case series` is NOT_BOUND"),
    ("a retrospective cohort study (PMID 40885991)", "`cohort study` is NOT_BOUND"),
    ("the pazopanib phase 2 trial NCT02066285 (PMID 31331701)", "bare `trial` is NOT_BOUND"),
])
def test_the_shapes_that_are_not_type_claims_are_not_bound(tmp_path, text, why):
    assert _corpus(tmp_path, text) == [], "false positive (%s): a gate that reds on honest prose " \
                                          "gets switched off" % why


def test_every_not_bound_word_carries_its_reason_and_is_not_silently_also_bound():
    """⛔ NOT_BOUND is a decision list. An entry with no reason is an omission wearing its costume."""
    for word, reason in lct.NOT_BOUND.items():
        assert len(reason) > 60, "%s: state WHY, so the next reader does not re-add it" % word
        assert word not in lct.TYPE_RULES


def test_every_bound_rule_names_only_real_mesh_publication_types():
    """A rule whose right-hand side is not a type PubMed assigns can never be satisfied."""
    real = {"Review", "Systematic Review", "Meta-Analysis", "Case Reports",
            "Randomized Controlled Trial"}
    for word, accepted in lct.TYPE_RULES.items():
        assert accepted and set(accepted) <= real, word


# --------------------------------------------------------------------------------------------
# the guard: it must go RED on the real defect
# --------------------------------------------------------------------------------------------

def _evaluate(tmp_path, text):
    recs, index = lct.load_cache()
    return lct.evaluate(_corpus(tmp_path, text), recs, index)


def test_the_2026_08_26_defect_itself_is_caught(tmp_path):
    """The sentence as it was written, with the three non-reviews restored."""
    errors, _ = _evaluate(
        tmp_path,
        "the metastasis claim rests on the review literature (PMC12398172), the review "
        "literature (PMC12376927) and the review literature (PMC9131214).")
    assert len(errors) == 3
    assert {e[0] for e in errors} == {"MISMATCH"}
    assert {e[4] for e in errors} == {"PMCID PMC12398172", "PMCID PMC12376927", "PMCID PMC9131214"}


def test_a_type_word_binds_every_identifier_in_its_LIST_not_only_the_first(tmp_path):
    """⛔⛔ THE INCIDENT SENTENCE'S OWN SHAPE — one type word, FOUR PMCIDs, three of them wrong.

    A scanner that stopped at the first identifier would have caught one third of the defect it was
    written for, and reported the other two thirds as clean.
    """
    errors, _ = _evaluate(
        tmp_path,
        "the review literature (PMC12398172, PMC12376927, PMC7563993 and PMC9131214) says so.")
    assert {e[4] for e in errors} == {
        "PMCID PMC12398172", "PMCID PMC12376927", "PMCID PMC9131214"}
    assert all(e[0] == "MISMATCH" for e in errors)


def test_a_list_run_stops_at_the_first_word_that_is_not_list_punctuation(tmp_path):
    """⚠ The continuation must not reach forward into the next clause and mis-type an innocent id."""
    found = _corpus(
        tmp_path, "one review (PMC7563993). Separately PMID 23058004 is discussed below.")
    assert [f[4] for f in found] == ["PMC7563993"]


def test_the_one_review_among_the_four_is_not_flagged(tmp_path):
    errors, _ = _evaluate(tmp_path, "the metastasis claim rests on one review (PMC7563993).")
    assert errors == []


def test_a_case_report_called_a_review_is_caught_and_the_reverse_too(tmp_path):
    errors, _ = _evaluate(tmp_path, "a review (PMID 23058004) and a case report (PMID 41055792).")
    assert {(e[0], e[3], e[4]) for e in errors} == {
        ("MISMATCH", "review", "PMID 23058004"),
        ("MISMATCH", "case report", "PMID 41055792"),
    }


def test_a_missing_cache_row_is_an_error_naming_the_fetch(tmp_path):
    """⛔ NEVER A SILENT PASS. A claim the guard has no metadata for FAILS, and says what to run."""
    errors, _ = _evaluate(tmp_path, "a 2024 review (PMID 99999999) says so.")
    assert len(errors) == 1 and errors[0][0] == "MISSING"
    assert "get_article_metadata" in lct._MISSING_HELP
    assert "THIS IS NOT A PASS" in lct._MISSING_HELP


def test_a_retraction_is_advisory_and_never_sets_the_exit_code(tmp_path):
    errors, advis = _evaluate(tmp_path, "the Safe 2025 review (PMC12263127) describes compounds.")
    assert errors == []
    assert len(advis) == 1 and "Retracted Publication" in advis[0][2]["article_types"]


def test_the_live_tree_is_green_with_no_baseline_and_no_amnesty():
    """⚠ There is deliberately NO ledger here. If this ever needs one, the count must be the finding."""
    assert not hasattr(lct, "LEDGER"), "no ledger module-level path means no place to hide a claim"
    src = open(os.path.join(MANUSCRIPTS, "lint_citation_types.py"), encoding="utf-8").read()
    assert "--baseline" not in src, "no amnesty flag: the guard was born green on 18/18 real claims"
    assert lct.check() == 0


def test_the_guard_is_reached_by_the_gate_that_runs_in_the_commit_loop():
    """⛔ A guard nothing executes is the defect this repository keeps paying for."""
    # ⛔ ASSERT THE BEHAVIOUR, NOT THE SPELLING. An earlier version of this test grepped for the
    # literal call `lint_citation_types.check()`; refactoring that import to load by path — which it
    # had to be, so a test loading the linter by `spec_from_file_location` does not hit ImportError —
    # broke the test while the wiring was intact. So load the gate's own module and drive it.
    lc = _load("lint_citations")
    assert lc.check() == 0, "gate 6 must be green on this tree, through the type guard as well"
    src = open(os.path.join(MANUSCRIPTS, "lint_citations.py"), encoding="utf-8").read()
    assert "lint_citation_types.py" in src, "gate 6's command must reach the type guard's module"
    pf = open(os.path.join(ROOT, "scripts", "preflight.sh"), encoding="utf-8").read()
    assert "lint_citations.py" in pf, "gate 6 is what carries this guard into the commit loop"
    ci = open(os.path.join(ROOT, ".github", "workflows", "tests.yml"), encoding="utf-8").read()
    assert "lint_citations.py" in ci and "research/manuscripts/tests" in ci
