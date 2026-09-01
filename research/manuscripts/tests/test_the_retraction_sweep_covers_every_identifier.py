"""The repository-wide retraction pass must see EVERY prose identifier, and must never call an
identifier it could not read "clean".

⛔ WHY THIS FILE EXISTS, AND IT IS A COVERAGE DEFECT RATHER THAN A CORRECTNESS ONE (measured
2026-09-01, seat S27-RETRACTIONS). `lint_citation_types.evaluate()` raised its retraction advisory
only for identifiers a TYPE CLAIM reached — the attributive `review (PMID X)` shape `_SCAN` binds.
The run that prompted this printed *"23 type claim(s) checked against 13 cached record(s),
1 retraction advisory"* against a repository holding **1,077 prose identifiers**. The guard was
correct about the 23 and silent about the other 1,054, and its own summary line reported the 23.
Two things the narrow pass could not see, both found the day the wide pass was written:

  * PMID 36062197 (Oxid Med Cell Longev 2022, `Retracted Publication`) — cited in
    `no-wet-lab-publication-archetypes.md` with no type word anywhere near it.
  * PMID 40646688 (the Safe 2025 review) inside **`degrader/nr4a3-degrader-paper.md`**, a
    submission manuscript. The narrow advisory named only the modalities file, because only that
    file happens to put the identifier after the word "review".

⛔ AND WHY EVERY TEST HERE MUTATES A COPY. A guard that fails open and a guard that is satisfied
print the same green. Each test below feeds `retraction_sweep()` a synthetic prose map and a
tmp_path artifact, mutates the artifact into the shape the guard exists to catch, and asserts the
guard's answer changes. Nothing touches the working tree — `research-loop` §3, after the 2026-08-27
mutation window that pushed 13 inverted claims to origin/main.

Attribution: the retraction rows quoted here come from PubMed via
`research/manuscripts/citation-retraction-sweep.json`; PubMed's terms require its metadata to travel
with a resolvable DOI link, which that artifact carries per record.
"""
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MANUSCRIPTS))
SWEEP = os.path.join(MANUSCRIPTS, "citation-retraction-sweep.json")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MANUSCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lct = _load("lint_citation_types")

#: One retracted identifier, one identifier with no row at all, one identifier PubMed cannot reach.
#: The third is the case the artifact records as `unknown`, and it must NOT be reported as a gap in
#: the sweep — it is a gap in what PubMed can answer, which is a different sentence.
PROSE = {
    "PMID": {"40646688": {"paper.md"}, "12345678": {"other.md"}},
    "ARXIV": {"2501.00001": {"methods.md"}},
}


@pytest.fixture()
def artifact(tmp_path):
    """A minimal sweep artifact built from the REAL retracted row, written to tmp_path."""
    real = json.load(open(SWEEP, encoding="utf-8"))
    doc = {
        "swept_utc": real["swept_utc"],
        "records": {"PMID:40646688": real["records"]["PMID:40646688"]},
        "retracted_detail": real["retracted_detail"],
        "unknown": {"ARXIV:2501.00001": "outside PubMed entirely"},
        "acknowledged": [{"file": "paper.md", "identifiers": ["PMID 40646688"], "why": "fixture"}],
    }

    def write(mutate=None):
        d = json.loads(json.dumps(doc))
        if mutate:
            mutate(d)
        path = tmp_path / "sweep.json"
        path.write_text(json.dumps(d), encoding="utf-8")
        lct.SWEEP = str(path)
        return lct.retraction_sweep(prose=PROSE)

    original = lct.SWEEP
    yield write
    lct.SWEEP = original


def test_a_retracted_identifier_is_reported_wherever_it_is_cited(artifact):
    hits, not_swept, cov = artifact()
    assert [(h[0], h[1]) for h in hits] == [("PMID", "40646688")]
    assert hits[0][2] == ["paper.md"], "the hit must name the file, so a human can read the sentence"
    assert hits[0][4] is True, "the fixture acknowledges it"
    assert cov["swept"] == 1 and cov["unreachable"] == 1


def test_the_verdict_comes_from_the_artifact_and_not_from_a_hardcoded_identifier(artifact):
    # ⛔ The one mutation that would make this guard a decoration: if the PMID were baked into the
    # code, flipping the artifact would change nothing and the "sweep" would be a constant.
    hits, _, _ = artifact(lambda d: d["records"]["PMID:40646688"].update(status="clean"))
    assert hits == []


def test_an_identifier_with_no_row_is_NOT_SWEPT_and_never_silently_clean(artifact):
    # ⛔⛔ THE LOAD-BEARING TEST. "Not in the record" means the collector could not read it, not that
    # it is fine. A sweep that counts an unread identifier as clean is the exact defect this
    # repository keeps paying for, and it fails green, which is why it survives.
    hits, not_swept, cov = artifact(lambda d: d["records"].clear())
    assert sorted(n[1] for n in not_swept) == ["12345678", "40646688"]
    assert cov["not_swept"] == 2 and cov["swept"] == 0
    assert hits == []


def test_an_identifier_outside_pubmed_is_unreachable_rather_than_unswept(artifact):
    # An arXiv id has no PubMed retraction status by construction. That is honestly UNKNOWN, and it
    # must not be laundered into the swept count — nor be reported as a sweep the operator forgot.
    _, not_swept, cov = artifact()
    assert "2501.00001" not in [n[1] for n in not_swept]
    assert cov["unreachable"] == 1


def test_a_missing_artifact_fails_rather_than_passes(artifact, tmp_path):
    # ⛔ The guard cannot check what it has no data for, so absence must be loud. `check()` turns
    # this None into rc 2; a silent pass here would be a gate that reports while measuring nothing.
    lct.SWEEP = str(tmp_path / "absent.json")
    assert lct.retraction_sweep(prose=PROSE) == (None, None, None)


def test_acknowledgement_is_read_from_the_artifact_not_assumed(artifact):
    hits, _, _ = artifact(lambda d: d.__setitem__("acknowledged", []))
    assert hits[0][4] is False, "an unacknowledged retracted citation must say so"


def test_the_committed_sweep_accounts_for_every_committed_prose_identifier():
    """On the REAL tree: every identifier lands in exactly one of checked / unreachable / not-swept.

    ⛔ WHAT THIS DELIBERATELY DOES NOT ASSERT, AND WHY. An earlier draft demanded
    `not_swept == []`, i.e. that the artifact be perfectly current with the tree. That is a gate
    that goes red for a reason unrelated to the change in front of it — cite one new paper and the
    trunk is red until somebody with PubMed access refreshes an artifact, which in a sandbox with
    NCBI blocked at the egress proxy is not a fix a committing session can perform. CLAUDE.md §6
    names that cascade as the real cost of an over-eager gate. ★ THE PROPERTY THAT MATTERS IS NOT
    "the sweep is current", IT IS "an unread identifier is never counted as clean" — so what is
    pinned is the arithmetic (nothing falls between the three buckets) and the fact that not-swept
    rows come back NAMED, for the linter to print. Escalating staleness to a hard failure belongs
    with the ADVISORY→ERROR flip argued in S27-RETRACTIONS.md §5, as one decision and not two.
    """
    hits, not_swept, cov = lct.retraction_sweep()
    assert cov is not None, "the sweep artifact must be committed"
    assert cov["swept"] + cov["unreachable"] + cov["not_swept"] == cov["total"], \
        "an identifier fell between the buckets — that is how an unread one becomes 'clean'"
    assert cov["not_swept"] == len(not_swept)
    for kind, ident, files in not_swept:
        assert kind and ident and files, "a not-swept row must name itself and where it is cited"


def test_every_retracted_row_carries_the_doi_link_pubmed_requires():
    real = json.load(open(SWEEP, encoding="utf-8"))
    for pmid, rec in real["retracted_detail"].items():
        assert rec.get("doi_url", "").startswith("https://doi.org/"), pmid
        assert "Retracted Publication" in rec["article_types"] or \
               "Expression of Concern" in rec["article_types"], pmid


def test_the_sweep_artifact_does_not_anchor_the_provenance_ledger():
    # ⛔ MEASURED, NOT ASSUMED (2026-09-01). The artifact's `records` map is keyed by every prose
    # identifier in the repository, so leaving it inside `lint_citations.survey()`'s anchor scan
    # took the unanchored counts to ZERO for all six identifier kinds — a green readout bought by
    # adding a file, which is the 2026-08-07 self-anchoring incident again.
    # ⭐ ASSERTED AS BEHAVIOUR, NOT AS A SPELLING. A first draft grepped the source for the exact
    # tuple text — the same coupling that made this seat's one-token edit red a neighbouring guard
    # whose property was untouched, and the coupling `test_citation_type_guard.py` already records
    # paying for once. What matters is that identifiers living only in prose and in this artifact
    # stay UNANCHORED, so the provenance ledger keeps measuring something.
    lc = _load("lint_citations")
    assert lc.SWEEP_ARTIFACT_REL == os.path.relpath(SWEEP, ROOT).replace(os.sep, "/")
    prose, anchors = lc.survey()
    un = lc.unanchored(prose, anchors)
    assert un, ("every prose identifier is anchored, which is what happens when a tracked .json "
                "listing all of them joins the anchor scan — the 2026-08-07 self-anchoring defect")
    swept = json.load(open(SWEEP, encoding="utf-8"))["records"]
    assert any("%s:%s" % (kind, ident) in swept for kind, ident, _f in un), \
        "no unanchored identifier has a sweep row, so this test is no longer measuring the overlap"
