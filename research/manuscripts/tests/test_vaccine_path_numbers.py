#!/usr/bin/env python3
"""Every headline quantity in the EMC VACCINE PATH paper, tied to the artifact that produces it.

⛔ WHY THIS EXISTS — THE EIGHTH ONE-OF-A-PAIR GUARD, AND THE FIRST FOR THIS DOCUMENT AT ALL.
`test_journal_article_numbers.py` binds the ASO journal article's prose to its artifacts, and
`research/modalities/tests/test_aso_submission_numbers.py` binds the extended report's. Measured on
2026-08-22 at the first adversarial review of `emc-vaccine-development-path.md`: **0 of 48 modules in
this directory and 0 of 410 in the modalities suite named that file.** Roughly thirty printed figures,
eleven of them stated at three or more sites, had no binding to any artifact whatsoever — a value could
drift there, contradict the JSON that produces it, and every test in the repository would still pass.

That is not hypothetical for this document. The review found the abstract stating the *EWSR1* e7::e3
junction was "presented on HLA-B*15:01 alone" — true of the ten-allele screen and false against the
committed 34-allele screen, which finds the same lead peptide strong on HLA-A*30:02 as well. Nothing
was reading either artifact for the prose.

⛔ THE ASSERTIONS ARE ON DERIVED VALUES, NEVER ON REMEMBERED ONES. Each block loads the artifact,
computes what the prose should say, and looks for that. A failure means the paper and its evidence have
diverged — fix whichever is wrong, but do not relax the assertion, and do not paste the artifact's
current value in as a literal to make it green.
"""
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MANUSCRIPTS))
MOD = os.path.join(REPO, "research", "modalities")

PAPER = os.path.join(MANUSCRIPTS, "neoantigen", "emc-vaccine-development-path.md")
BREAKPOINTS = os.path.join(MOD, "fusion-breakpoint-neoantigens.json")
COVERAGE = os.path.join(MOD, "hla-coverage.json")
CURVE = os.path.join(MOD, "coverage-curve.json")
THRESHOLD_CURVE = os.path.join(MOD, "coverage-threshold-curve.json")
MATRIX = os.path.join(MOD, "epitope-allele-matrix.json")
NOVELTY = os.path.join(MOD, "junction-proteome-novelty.json")
CD4 = os.path.join(MOD, "patient-cd4-demo.json")
CONSTRUCT = os.path.join(MOD, "vaccine-construct.json")
UNCERTAINTY = os.path.join(MOD, "coverage-uncertainty.json")


def _required(path, what):
    """⛔ An artifact that is not there is a finding, never a silent pass.

    Every path here is `git ls-files`-tracked, so its absence is a broken tree rather than a partial
    checkout, and a guard that disappears with its input is indistinguishable from one that never ran.
    """
    if not os.path.exists(path):
        pytest.fail(f"{what} is missing at {path}. It is committed, so regenerate it rather than "
                    "passing over the assertions that depend on it.")
    return path


def _load(path, what):
    return json.load(open(_required(path, what), encoding="utf-8"))


@pytest.fixture(scope="module")
def prose():
    return open(_required(PAPER, "the vaccine-path manuscript"), encoding="utf-8").read()


@pytest.fixture(scope="module")
def flat(prose):
    """The prose with its hard wrapping collapsed.

    The manuscript is wrapped at ~100 columns, so nearly every construction worth binding straddles a
    line break. Matching against flattened text keeps the patterns readable as sentences.
    """
    return re.sub(r"\s+", " ", prose)


@pytest.fixture(scope="module")
def breakpoints():
    return _load(BREAKPOINTS, "the junction screen")


@pytest.fixture(scope="module")
def coverage():
    return _load(COVERAGE, "the population-coverage artifact")


@pytest.fixture(scope="module")
def curve():
    return _load(CURVE, "the broad-panel coverage curve")


@pytest.fixture(scope="module")
def threshold_curve():
    return _load(THRESHOLD_CURVE, "the coverage-versus-threshold curve")


@pytest.fixture(scope="module")
def matrix():
    return _load(MATRIX, "the 34-allele epitope/allele matrix")


@pytest.fixture(scope="module")
def novelty():
    return _load(NOVELTY, "the proteome novelty search")


@pytest.fixture(scope="module")
def cd4():
    return _load(CD4, "the class II screen")


@pytest.fixture(scope="module")
def construct():
    return _load(CONSTRUCT, "the candidate construct")


def _every_site(flat, pattern, expected, what):
    """⛔⛔ EVERY SITE THAT STATES THE QUANTITY, NOT WHETHER IT APPEARS SOMEWHERE.

    An `in`-style assertion walks straight through single-site drift: this paper states its coverage
    percentages at up to five sites each, so corrupting ONE leaves the others standing and a
    "value in prose" check still passes — while the document now says two different things about the
    same measurement. That is the ONE FACT, ONE PLACE defect exactly.

    So `pattern` captures the number from the CONSTRUCTION that states it, and EVERY match is checked.
    At least one match is required: a pattern that has stopped matching is a guard that has silently
    stopped guarding, which is the failure mode this whole file exists for.
    """
    found = re.findall(pattern, flat)
    assert found, (f"nothing in the manuscript matches the construction that states {what} "
                   f"(/{pattern}/) — either the sentence was reworded and this guard must follow it, "
                   "or the claim was dropped")
    wrong = [f for f in found if f != expected]
    assert not wrong, (f"{what} is {expected!r} in the artifact, and the manuscript states "
                       f"{wrong!r} at {len(wrong)} of its {len(found)} site(s)")


def _pct1(x):
    """The share as the manuscript prints it — one decimal place, percent."""
    return f"{round(x * 100, 1):.1f}"


def test_the_junction_grading_is_the_screens_grading(flat, breakpoints):
    """27 declared exon pairs, 5 in frame, and the 22 that are not, graded as the artifact grades them."""
    pairs = breakpoints["n_candidate_exon_pairs"]
    inframe = breakpoints["n_inframe_junctions"]
    grades = breakpoints["grade_counts"]
    assert sum(grades.values()) == pairs, (
        f"the grade counts {grades} sum to {sum(grades.values())} and the artifact declares {pairs} "
        "candidate exon pairs; the screen disagrees with itself before the prose is even consulted")
    _every_site(flat, r"Of (\d+) declared exon pairs", str(pairs), "the declared exon-pair count")
    _every_site(flat, r"declared exon pairs, (\d+) are in frame", str(inframe),
                "the in-frame junction count")
    _every_site(flat, r"non-coding acceptor \((\d+)\)", str(grades["NON_CODING_ACCEPTOR"]),
                "the non-coding-acceptor grade count")
    _every_site(flat, r"out of frame \((\d+)\)", str(grades["OUT_OF_FRAME"]),
                "the out-of-frame grade count")
    _every_site(flat, r"not producing the seam \((\d+)\)", str(grades["SEAM_NOT_PRODUCED"]),
                "the seam-not-produced grade count")


def test_the_binder_counts_are_the_ten_allele_screens(flat, breakpoints):
    """11 distinct binders and 4 strong, over the panel the artifact actually ran."""
    peptides, strong = set(), set()
    for j in breakpoints["junctions"]:
        for b in j["binders"]:
            peptides.add(b["peptide"])
            if b["class"] == "strong":
                strong.add(b["peptide"])
    _every_site(flat, r"returns (\d+) distinct predicted binders", str(len(peptides)),
                "the distinct predicted-binder count")
    _every_site(flat, r"predicted binders of which (\d+) are strong", str(len(strong)),
                "the strong-binder count as the Abstract states it")
    _every_site(flat, r"predicted binders, (\d+) of them strong", str(len(strong)),
                "the strong-binder count as Section 2.2 states it")


def test_the_panel_the_paper_names_is_the_panel_that_ran(flat, breakpoints, matrix):
    """⭐ THE DEFECT THAT MADE THIS FILE NECESSARY.

    Every binder figure comes from the ten-allele MHCflurry run; the coverage scan is 34 alleles. The
    manuscript said "the class I allele panel is 34" while quoting ten-allele results, and stated
    "presented on HLA-B*15:01 alone" without naming which panel that was true of. Both panel sizes are
    now bound to the artifacts that define them, and the predictor version is bound too — the paper
    said "MHCflurry 2.0" where the artifact records 2.1.4.
    """
    ten = breakpoints["_predictor"]["alleles"]
    assert len(ten) == 10, f"the junction screen's panel is {len(ten)} alleles, not 10"
    _every_site(flat, r"screened with MHCflurry ([\d.]+), models", breakpoints["_predictor"]["version"],
                "the MHCflurry version that produced the binders")
    # ⚠ the trailing `[\d.]+` swallowed the sentence-ending full stop at one of the four sites and
    # reported "2.2.0." as drift. Anchor the shape of a version instead of a run of digits and dots.
    _every_site(flat, r"models release (\d+\.\d+\.\d+)", breakpoints["_predictor"]["models_release"],
                "the MHCflurry models release")
    for allele in ten:
        assert allele.replace("HLA-", "").replace("*", "\\*") in flat, (
            f"{allele} is in the screen's panel and the manuscript does not list it; the panel is "
            "named in full precisely so a reader can see which instrument produced the binders")
    _every_site(flat, r"a (\d+)-allele screen of the same peptides", str(matrix["panel"].__len__()),
                "the broad panel size as Section 2.2 states it")
    assert matrix["rank_column"] == breakpoints["_rank_column_used"], (
        "the two screens rank on different columns, so their strong calls are not comparable and the "
        "manuscript's side-by-side presentation of them would be a unit conflation")


def test_the_broad_panel_adds_exactly_the_allele_the_paper_says_it_adds(flat, matrix, curve):
    """A*30:02 is the whole difference between 27.4% and 30.4%, and between 8.5% and 12.3%."""
    ten_alleles = {r["allele"] for r in matrix["strong_binders"]}
    assert set(curve["presenting_alleles"]) == ten_alleles, (
        "the coverage curve's presenting alleles and the matrix's strong-binder alleles have diverged")
    assert "HLA-A*30:02" in curve["presenting_alleles"], (
        "the manuscript's account of why the broad panel raises coverage names HLA-A*30:02; the "
        "artifact no longer carries it, so that account is now wrong")
    lead = [r for r in matrix["strong_binders"] if r["allele"] == "HLA-A*30:02"]
    assert lead and lead[0]["peptide"] == "NMPCVQAQY", (
        "the manuscript says the SAME lead peptide is what A*30:02 presents; the matrix now says "
        f"{lead[0]['peptide'] if lead else 'nothing'}")
    # ⛔ AND THE PROSE MUST NAME IT. Everything above interrogates the artifacts; a mutation that
    # changed the manuscript's "also strong on HLA-A*30:02" to a different allele passed every
    # assertion in this test, because none of them read the manuscript. The paper's whole account of
    # why 8.5% becomes 12.3% rests on this one allele being the one the broad panel adds.
    added = set(curve["presenting_alleles"]) - {"HLA-A*01:01", "HLA-B*07:02", "HLA-B*15:01"}
    assert len(added) == 1, f"the broad panel now adds {sorted(added)}, and Section 2.2 names one allele"
    _every_site(flat, r"also strong on HLA-(A\\\*\d\d:\d\d)",
                added.pop().replace("HLA-", "").replace("*", "\\*"),
                "the allele the broad panel adds, as Section 2.2 names it")


def test_every_coverage_figure_is_the_artifacts(flat, coverage, curve):
    """The four coverage percentages, each bound to the computation that produces it."""
    g = coverage["global"]
    _every_site(flat, r"junction covers ([\d.]+)% on ten alleles", _pct1(g["coverage_e7e3_public"]),
                "the e7::e3 coverage on the ten-allele screen")
    _every_site(flat, r"gives ([\d.]+)% and [\d.]+% on those two panels",
                _pct1(g["coverage_any_strong_binder_allele"]),
                "the pooled coverage on the ten-allele screen")
    _every_site(flat, r"gives [\d.]+% and ([\d.]+)% on those two panels",
                _pct1(curve["global_max_coverage"]),
                "the pooled coverage on the 34-allele screen")
    # the 12.3% figure is DERIVED here rather than read: it is the union of the two alleles the broad
    # panel presents the lead peptide on, and no artifact field stores it.
    af = {a: v["allele_frequency"] for a, v in g["allele_frequencies"].items()}
    afc = {e["allele_added"]: e["af"] for e in curve["global_curve"]}
    both = 1.0
    for a in ("HLA-B*15:01", "HLA-A*30:02"):
        both *= (1 - afc[a]) ** 2
    _every_site(flat, r"and ([\d.]+)% on 34, where the same lead", _pct1(1 - both),
                "the e7::e3 coverage on the 34-allele screen, re-derived from the allele frequencies")
    assert abs(af["HLA-B*15:01"] - afc["HLA-B*15:01"]) < 1e-9, (
        "the two artifacts disagree on the frequency of HLA-B*15:01, so the coverage figures they "
        "produce are not on the same footing")


def test_no_confidence_interval_survives_in_the_prose(prose, coverage):
    """⛔ THE WITHDRAWAL IS A GUARD, NOT A ONE-TIME EDIT.

    The Wilson intervals were withdrawn because they pool every reference population into one binomial
    while the same records show the frequency ranging from 0 to 0.40 between those populations. The
    artifact still carries them, so a later edit could re-quote one in perfect good faith.
    """
    lo, hi = coverage["global"]["coverage_e7e3_public_95ci"]
    for value in (lo, hi, *coverage["global"]["coverage_any_strong_binder_allele_95ci"]):
        printed = f"{round(value * 100, 2):.2f}"
        assert printed not in prose, (
            f"{printed} is a Wilson interval bound from hla-coverage.json and it is back in the "
            "manuscript. Section 2.3 states why these intervals are not reported; re-quoting one "
            "reinstates a claim the paper withdraws two paragraphs earlier")
    assert "95% CI 8.26" not in prose and "95% CI 26.6" not in prose, \
        "a withdrawn coverage confidence interval has returned to the prose"


def test_the_threshold_sensitivity_ladder_is_recomputed_not_typed(flat, matrix, curve,
                                                                  threshold_curve):
    """⭐ The ladder that shows the headline figure is a threshold artifact, re-derived here.

    ⭐ EXTENDED 2026-08-23 WHEN §2.3 STOPPED SAMPLING THE FUNCTION AND STARTED PUBLISHING IT. The
    section used to state three round-number rungs; it now walks the staircase step by step below the
    conventional cut and reports the function above it as well. Two of the old bindings stopped
    matching, which is the guard telling the truth — the sentences they were bound to no longer
    exist. They are rebound to the sentences that replaced them, and the figures the new prose adds
    are bound too, because an unbound number in this document is the whole reason this file exists.

    ⛔ THE TWO SPANS ARE DIFFERENT QUANTITIES AND MUST NOT BE CONFLATED — the first draft of this
    guard did exactly that. `step_span` is the distance from the weakest call to the last one that
    ADDS AN ALLELE (0.3736 to 0.4580), which is what "every step falls inside a window N wide"
    claims. `reach` is the distance from the acceptance threshold DOWN to the weakest call, which is
    how far a cut has to move to remove every allele. A third, `span`, is weakest-to-strongest call
    including the one that adds nothing. Each is bound to the sentence that states it and to no
    other.
    """
    afc = {e["allele_added"]: e["af"] for e in curve["global_curve"]}
    rows = matrix["strong_binders"]

    def cov_at(cut):
        alleles = {r["allele"] for r in rows if r["percentile"] <= cut}
        p = 1.0
        for a in alleles:
            p *= (1 - afc[a]) ** 2
        return round((1 - p) * 100, 1)

    _every_site(flat, r"0\.45 leaves three alleles and ([\d.]+)%", f"{cov_at(0.45):.1f}",
                "the coverage at a 0.45 percentile cut")
    _every_site(flat, r"to 0\.40 leaves one and ([\d.]+)%", f"{cov_at(0.40):.1f}",
                "the coverage at a 0.40 percentile cut")
    assert cov_at(0.37) == 0.0, (
        "the manuscript states that a 0.37 cut leaves nothing; the matrix now has a call at or below "
        "0.37, so that sentence is false")
    lowest = min(r["percentile"] for r in rows)
    cut = threshold_curve["conventional_threshold"]
    reach = round(cut - lowest, 4)
    _every_site(flat, r"it reaches zero ([\d.]+) below it", f"{reach:g}",
                "the distance from the acceptance threshold down to the weakest call")
    _every_site(flat, r"a best in-frame call of ([\d.]+)", f"{lowest:g}",
                "the weakest surviving in-frame call, as Section 2.2 states it")
    _every_site(flat, r"the least permissive call it\s?makes is ([\d.]+)", f"{lowest:g}",
                "the same call, as B1 states it")

    # ⭐ THE STAIRCASE ITSELF. Each step below the conventional cut is one peptide-allele call, and
    # Section 2.3 names every one with its percentile, its peptide and the coverage after it.
    steps = [st for st in threshold_curve["steps"] if st["threshold"] <= cut]
    assert steps, "the threshold curve reports no steps below the conventional cut"
    for st in steps:
        for allele in st["alleles_added"]:
            escaped = re.escape(allele.replace("*", "\\*"))
            _every_site(flat,
                        rf"{escaped}[^.;]{{0,40}}?at\s?(?:presentation percentile\s?)?([\d.]+) on ",
                        # ⚠ FOUR DECIMALS, NOT `:g`. These are MHCflurry percentiles and the prose
                        # prints them as the predictor gives them — 0.4580 keeps its trailing zero
                        # beside 0.3736 and 0.4033. `:g` strips it and the guard then argues with
                        # correct prose about a digit that carries no information either way.
                        f"{st['threshold']:.4f}",
                        f"the percentile at which {allele} enters")
        # ⛔ ANCHORED ON THE ALLELE, NOT THE PEPTIDE. Two steps share NMPCVQAQY — it enters on
        # HLA-B*15:01 at 0.3736 and on HLA-A*30:02 at 0.4033 — so a peptide-keyed pattern matches
        # the first step's sentence twice and reports the second step's coverage as drift. The
        # allele is what makes a step unique; the prose for the second one says "the same peptide".
        for allele in st["alleles_added"]:
            escaped = re.escape(allele.replace("*", "\\*"))
            _every_site(flat,
                        rf"{escaped}[^;]{{0,120}}?"
                        rf"(?:taking coverage from zero to |reaching )([\d.]+)%",
                        f"{st['coverage_after'] * 100:.1f}",
                        f"the coverage after {allele} enters")
    width = round(max(x["threshold"] for x in steps) - min(x["threshold"] for x in steps), 4)
    _every_site(flat, r"a window ([\d.]+) units\s?wide", f"{width:g}",
                "the width of the window every step falls inside, as Section 2.3 states it")
    _every_site(flat, r"a window ([\d.]+)\s?percentile units wide", f"{width:g}",
                "the same window, as the Abstract states it")

    def at(t):
        r = next((x for x in threshold_curve["curve"] if abs(x["threshold"] - t) < 1e-9), None)
        assert r is not None, f"the threshold curve has no point at {t}"
        return r

    # ⛔ THE UPPER HALF IS THE PART A READER COULD MISTAKE FOR AN ARGUMENT FOR A LOOSER CUT, so it is
    # the part that must not drift by a digit. Section 2.3 states these four and the artifact owns
    # them; the 0.2 tier is asserted rather than pattern-matched because its claim is that the tier
    # is EMPTY, and an empty tier has no percentage to bind.
    assert at(0.2)["n_presenting_alleles"] == 0, (
        "Section 2.3 and B1 both state that a conservative 0.2 cut leaves no presenting allele; the "
        "curve now disagrees")
    _every_site(flat, r"(\d+) presenting alleles and [\d.]+% at a cut of 1\.0",
                str(at(1.0)["n_presenting_alleles"]), "the allele count at a cut of 1.0")
    for t, phrase in ((1.0, r"([\d.]+)% at a cut of 1\.0"),
                      (2.0, r"([\d.]+)% at\s?2\.0"),
                      (5.0, r"([\d.]+)% at 5\.0")):
        _every_site(flat, phrase, f"{at(t)['coverage'] * 100:.1f}",
                    f"the coverage at a percentile cut of {t}")


def test_the_novelty_result_is_the_searchs_result(flat, novelty):
    """170 of 174, the four that collide, and the one binder withdrawn."""
    # ⛔ ALL THREE SITES. "170 of 174" is stated in the Abstract, in the Section 3 limit table, and in
    # Section 6.1's conditions for revision. A mutation run corrupting only the Abstract's copy is the
    # single-site case an `in` test cannot see, and this figure is the paper's one clean positive
    # result, so a document disagreeing with itself about it is the worst version of this defect.
    novel, tested = novelty["n_novel_proteome_wide"], novelty["n_peptides_tested"]
    _every_site(flat, r"(\d+) of \d+ (?:peptides are absent from the reviewed|novel proteome-wide)",
                str(novel), "the proteome-novel count, at every site that states it")
    _every_site(flat, r"\d+ of (\d+) (?:peptides are absent from the reviewed|novel proteome-wide)",
                str(tested), "the peptides-tested count, at every site that states it")
    _every_site(flat, r"novelty for (\d+) of \d+ peptides", str(novel),
                "the proteome-novel count, as Section 6.1 states it")
    _every_site(flat, r"novelty for \d+ of (\d+) peptides", str(tested),
                "the peptides-tested count, as Section 6.1 states it")
    _every_site(flat, r"the (\d+) that do not occur in an \*NR4A3\* isoform",
                str(novelty["n_found_in_proteome"]), "the count found in the proteome")
    hits = novelty["peptides_found_in_proteome"]
    for h in hits:
        assert h["peptide"] in flat, (
            f"{h['peptide']} collides with a normal protein and the manuscript does not name it; "
            "Section B5 names all four deliberately, because the design consequence is per-peptide")
    # ⛔ EVERY SITE. `acc in flat` was blind to a single-site corruption: the accession is stated more
    # than once, so changing one left the others standing and the membership test still passed. The
    # mutation run that found this changed Q92570-3 to Q92570-2 at one site and the guard was silent.
    accessions = {p["accession"] for h in hits for p in h["proteome_hits"]}
    assert len(accessions) == 1, (
        f"the collisions now span {len(accessions)} isoforms; B5's account of a single isoform "
        "boundary needs rewriting before this guard can bind it")
    _every_site(flat, r"(Q\d{5}-\d)", accessions.pop(),
                "the accession of the isoform carrying the colliding peptides")
    binders = [h for h in hits if h["predicted_binder"]]
    assert len(binders) == novelty["n_predicted_binders_found_in_proteome"], \
        "the artifact's own count of withdrawn binders disagrees with its own peptide records"


def test_the_class_ii_arm_is_the_screens_arm(flat, cd4, coverage):
    """⭐ REWRITTEN 2026-08-23 WHEN THE PANEL WIDENED FROM 3 ALLELES TO 23 AND THE ARM TURNED POSITIVE.

    The previous version of this guard asserted `n_strong == 0` with the message "every sentence in B4
    and the Abstract that reports this arm as negative is now false". That assertion fired on the
    widened run, which is exactly what it was for — a guard that encodes today's result and breaks
    loudly when the result moves is doing its job, and the fix is to rebind it to the new prose, never
    to loosen it. What is bound now is the POSITIVE and its size, because a single strong call on 23
    alleles is easy to overstate by a sentence and impossible to overstate past these assertions.
    """
    _every_site(flat, r"(\d+) candidate 15-mers were screened", str(cd4["n_candidate_15mers"]),
                "the class II candidate count")
    _every_site(flat, r"against (\d+) class II alleles", str(len(cd4["patient_class2_hla"])),
                "the class II panel width, as B4 states it")
    _every_site(flat, r"(\d+) peptide-allele pairs\s?bind", str(cd4["n_predicted_binders"]),
                "the class II binder count")
    # ⛔ AN ALLELE WITHOUT A MODEL IS NOT AN ALLELE THAT FAILED. B4 claims every declared allele
    # returned a score; if that stops being true the sentence must change before the count does.
    assert not cd4.get("alleles_without_a_model"), (
        "B4 states that no allele was unscreenable; the screen now reports "
        f"{cd4['alleles_without_a_model']}")
    strong = [r for r in cd4["all_predictions"] if r["call"] == "strong"]
    assert len(strong) == cd4["n_strong"]
    assert cd4["n_strong"] == 1, (
        "B4 reports exactly one strong class II call; the screen now returns "
        f"{cd4['n_strong']} and every sentence stating 'one' is false")
    lead = strong[0]
    for probe in (lead["peptide"], lead["allele"].replace("*", "\\*")):
        assert probe in flat, f"B4 does not name {probe}, which carries its only strong call"
    _every_site(flat, rf"{lead['peptide']} on {re.escape(lead['allele'].replace('*', chr(92) + '*'))} "
                      r"at ([\d.]+) nM", f"{lead['ic50_nM']:g}",
                "the IC50 of the only strong class II call")
    n_alleles_with_a_binder = len({r["allele"] for r in cd4["shortlist"]})
    _every_site(flat, r"spread over (\d+) of the 23 alleles", str(n_alleles_with_a_binder),
                "how many alleles returned at least one class II binder")
    # ⭐ THE CONTINUITY CHECK IS PART OF THE CLAIM. B4 argues the widening was ADDITIVE — that the
    # earlier three-allele negative was a property of the panel and not of a different computation —
    # and it argues that by printing the two old IC50s and saying they reproduce. If they stop
    # reproducing, that argument is gone and the sentence is wrong.
    old_panel = {"DRB1*15:01", "DRB1*03:01", "DRB1*07:01"}
    for row in [r for r in cd4["shortlist"] if r["allele"] in old_panel]:
        _every_site(flat, rf"{row['peptide']}\s?at ([\d.]+) nM", f"{row['ic50_nM']:g}",
                    f"the reproduced three-allele-panel IC50 of {row['peptide']}")
    g = coverage["global"]
    _every_site(flat, r"class II coverage\s?is ([\d.]+)%", f"{g['coverage_cd4_classii'] * 100:.1f}",
                "class II coverage, as B4 states it")
    _every_site(flat, r"of each\s?class is ([\d.]+)%",
                f"{g['coverage_cd8_and_cd4_combined'] * 100:.1f}",
                "combined CD8 and CD4 coverage, as B4 states it")


def test_the_construct_is_the_generated_construct(flat, construct):
    """The minimal SLP's length and the epitopes it carries — both arms since the panel widened."""
    lead = construct["lead_public_construct"]
    slp = lead["minimal_SLP"]
    length = slp.get("length") or len(slp.get("peptide", ""))
    # ⛔ ALL THREE SITES: the Abstract, B4's consequence paragraph, and Appendix A's current-value
    # column. Appendix A is the register CLAUDE.md rule 1.2 requires, so a stale value there is a
    # retraction table that misreports what the retraction landed on.
    _every_site(flat, r"construct is a (\d+)-residue synthetic long peptide", str(length),
                "the minimal synthetic long peptide length, as the Abstract states it")
    _every_site(flat, r"synthetic long peptide is (\d+) residues", str(length),
                "the minimal synthetic long peptide length, as B4 states it")
    # ⚠ ROW-ANCHORED, because Appendix A's superseded column ALSO reads "N residues, both arms" — the
    # retracted-seam construct carried both arms too. An unanchored pattern matches both cells and
    # reports the superseded 27 as a drift, which is a guard arguing with the register it is reading.
    _every_site(flat, r"Candidate minimal synthetic long peptide \| [^|]+\| (\d+) residues",
                str(length), "the minimal synthetic long peptide length, as Appendix A states it")
    for ep in lead["cd8_strong_epitopes"] + lead["cd4_strong_epitopes"]:
        pep = ep["peptide"] if isinstance(ep, dict) else ep
        assert pep in flat, f"the construct carries {pep} and B4 does not name it"
    # ⛔ WAS `assert not lead["cd4_strong_epitopes"]` UNTIL 2026-08-23, and that assertion fired when
    # the widened class II panel found one. The direction that now needs guarding is the opposite:
    # B4 and the Abstract both say the construct carries BOTH arms, so an empty class II list would
    # make those sentences false without any prose changing.
    assert lead["cd4_strong_epitopes"], (
        "the construct carries no class II epitope; B4's statement that it carries both arms, and "
        "the Abstract's 15-residue both-arms SLP, are false")


def test_the_lead_binder_is_quoted_with_the_number_that_classified_it(flat, breakpoints):
    """⚠ Percentile classifies; affinity does not. The paper says so, so the guard checks both."""
    e7 = next(j for j in breakpoints["junctions"] if j["junction_label"] == "EWSR1_e7__NR4A3_e3")
    lead = min((b for b in e7["binders"] if b["class"] == "strong"),
               key=lambda b: b["presentation_percentile"])
    _every_site(flat, r"a presentation percentile of ([\d.]+) and a predicted affinity",
                f"{lead['presentation_percentile']:.2f}".rstrip("0").rstrip("."),
                "the lead candidate's presentation percentile")
    _every_site(flat, r"predicted affinity of ([\d.]+) nM", f"{lead['affinity_nM']:g}",
                "the lead candidate's predicted affinity")
    assert lead["peptide"] in flat, "the lead candidate peptide is not named in Section 2.2"


def test_no_reference_still_says_citation_to_verify(prose):
    """⛔ A submission-bound manuscript may not carry a self-declared unverified citation.

    Two entries shipped reading literally "[citation to verify]" while the Methods depended on both.
    The one reference that genuinely has no record says so in its own words instead, and names the
    consequence, which is a different thing from a placeholder.
    """
    refs = prose.split("## 10. References")[-1].split("## Appendix")[0]
    assert "[citation to verify]" not in refs, (
        "a reference has reverted to a '[citation to verify]' placeholder. Either resolve it against "
        "a fetch record, or state in the entry itself what is missing and what it costs. "
        "⚠ Scoped to Section 10 deliberately: Appendix B QUOTES the phrase when recording that those "
        "placeholders were withdrawn, and a whole-document search reads that record as the defect.")


def test_the_author_block_carries_no_placeholder(prose):
    """⛔ `[Name]` and `[City, Country]` shipped in a document being prepared for posting."""
    for placeholder in ("[Name]", "[City, Country]", "[Affiliation]", "TBD"):
        assert placeholder not in prose, (
            f"the author block carries the placeholder {placeholder!r}; a preprint is posted under a "
            "real identity or not at all")
    assert "0000-0002-1823-1451" in prose, "the author's ORCID iD is not in the manuscript"


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE REPLACEMENT FOR A WITHDRAWN INTERVAL NEEDS A TIGHTER BINDING THAN THE INTERVAL DID.
# `test_no_confidence_interval_survives_in_the_prose` above guards the withdrawal. Section 2.3 now
# prints three quantities in its place — the exact within-locus form, the Fréchet bounds on the
# between-locus dependence, and the between-population spread — and a bare number in prose is exactly
# how the withdrawn interval got there. Every one of them is bound to `coverage-uncertainty.json`
# here, so the paragraph cannot outlive a regeneration that moves it.

@pytest.fixture(scope="module")
def uncertainty():
    return _load(UNCERTAINTY, "the coverage uncertainty analysis")


def _pct(x):
    """The manuscript's own rendering of a fraction: one decimal place, as a percentage."""
    return f"{round(x * 100, 1):.1f}%"


def test_the_within_locus_correction_is_the_artifacts(flat, uncertainty):
    """The exact form and its DIRECTION. The direction is the load-bearing half: the paper claims no
    coverage figure can be too high for this reason, which is only true while exact >= published."""
    rec = uncertainty["sets"]["class_i_any_strong_binder"]
    exact, published = rec["coverage_within_locus_exact"], rec["coverage_published_form"]
    assert exact >= published, (
        "the within-locus form came out BELOW the published form, which inverts the claim §2.3 "
        "makes about the direction of the approximation. Fix the paragraph, not this assertion.")
    assert _pct(exact) in flat, (
        f"§2.3 states the exact within-locus coverage; the artifact says {_pct(exact)}")
    gap = rec["understatement_of_published_form_pp"]
    assert f"{gap:.2f} percentage points" in flat, (
        f"the size of the correction ({gap:.2f} pp) is not the artifact's")


def test_the_ld_bounds_are_the_artifacts(flat, uncertainty):
    """Fréchet bounds are exact, so a typed pair that drifts from the artifact is simply wrong —
    there is no modelling slack in which a difference could be defensible."""
    rec = uncertainty["sets"]["class_i_any_strong_binder"]
    lo, hi = rec["ld_bounds_across_loci"]
    assert f"[{_pct(lo)}, {_pct(hi)}]" in flat, (
        f"§2.3's dependence bounds must be the artifact's [{_pct(lo)}, {_pct(hi)}]")
    width = rec["ld_bound_width_pp"]
    assert f"{width:.1f} percentage points" in flat, (
        f"the width attributed to the independence assumption ({width:.1f} pp) is not the artifact's")
    for locus, p in rec["per_locus_carrier_frequency"].items():
        assert _pct(p) in flat, (
            f"the per-locus carrier frequency at HLA-{locus} ({_pct(p)}) is quoted in §2.3 as the "
            "input to the bounds and must be the artifact's")


def test_the_between_population_spread_is_the_artifacts(flat, uncertainty):
    """The widest of the three, and the one §2.3 tells the reader to carry away."""
    rec = uncertainty["sets"]["class_i_any_strong_binder"]
    bp = rec["between_population"]
    complete = bp["complete_panel"]
    for key in ("median", "p25", "p75", "max"):
        assert _pct(complete[key]) in flat, (
            f"the complete-panel {key} ({_pct(complete[key])}) is not the artifact's")
    assert str(complete["n"]) in flat, "the number of complete-panel populations is not the artifact's"
    floor = bp["absent_scored_zero_floor"]
    assert _pct(floor["median"]) in flat, "the absent-as-zero floor median is not the artifact's"
    assert str(floor["n"]) in flat, "the size of the absent-as-zero population set is not the artifact's"


def test_the_floor_reading_is_never_offered_as_the_estimate(flat, uncertainty):
    """⛔ THE TWO READINGS MUST STAY LABELLED APART. An allele missing from a population's AFND record
    was not measured there; scoring it zero manufactures low-coverage populations out of a reporting
    gap. The floor is therefore a bound on the database's coverage of the panel, not on HLA, and the
    paper must say so wherever it prints it — this is the same failure mode as
    §4's 'an absent reading is not a reading of absence', arriving through a percentile."""
    floor = uncertainty["sets"]["class_i_any_strong_binder"]["between_population"][
        "absent_scored_zero_floor"]
    printed = _pct(floor["median"])
    where = flat.find(printed)
    assert where >= 0, f"the floor median {printed} is not in the manuscript"
    window = flat[where:where + 400]
    assert "floor" in window and "reporting gap" in window, (
        f"{printed} is printed without the sentence that makes it a floor. A reader meeting it bare "
        "would take a database gap for a population with no presenting allele.")


def test_the_combined_figures_dependence_ceiling_is_the_artifacts(flat, uncertainty):
    """⛔ AN INTERSECTION, NOT A UNION, AND THE BOUNDS INVERT. §B4's combined CD8-and-CD4 figure is a
    product of two coverages; §2.3's Fréchet argument applies to it, but a reader who carried the
    union form across would get a lower bound where the useful statement is an upper one. The
    ceiling — a both-arms construct can never reach more patients than its scarcer arm — is the half
    that constrains the design, so it is the half bound here."""
    comb = uncertainty["combined_class_i_and_class_ii"]
    lo, hi = comb["bounds_under_any_dependence"]
    assert hi == pytest.approx(min(comb["coverage_class_i"], comb["coverage_class_ii"])), (
        "the intersection ceiling must be the scarcer arm; if it is not, the generator has the "
        "union bounds where it needs the intersection ones")
    assert lo <= comb["product_under_independence"] <= hi + 1e-9, (
        "the independence product falls outside its own dependence bounds")
    assert f"[{_pct(lo)}, {_pct(hi)}]" in flat, (
        f"§B4's dependence bounds must be the artifact's [{_pct(lo)}, {_pct(hi)}]")
    ratio = comb["coverage_class_ii"] / comb["product_under_independence"]
    assert f"{ratio:.1f} times the product" in flat, (
        f"the distance from product to ceiling ({ratio:.1f}x) is not the artifact's")
