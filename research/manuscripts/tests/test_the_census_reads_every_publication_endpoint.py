"""⛔⛔ THE CENSUS'S DOCUMENT SET IS A PREDICATE. THIS IS WHAT STOPS IT BECOMING A LIST AGAIN.

Until 2026-08-26 `claim_coverage.PAPERS` was three hand-typed entries, all three belonging to one
submission. A second manuscript — `fusion-partner/emc-fusion-partner-stratification.md` — was a live
publication endpoint being hardened by blind review seats while the census did not list it at all,
so its coverage had never been measured, not even to say it was zero. Measured that day: 94 test
modules name `fusion-junction-aso` and 2 name `fusion-partner`, and the paper's blocker count across
four rounds went 3, 2, 9 — `paper-hardening` §8a's signature of sampling surfaces rather than fixing
a paper.

★★ THE STRUCTURAL RESULT BEHIND THE FIX, measured over 33 mutations in round 17 seat B: every fix
scoped to a PREDICATE held, six of eleven scoped to a LIST regressed at a sibling the fix did not
name, and in three of those six the missed sibling was named in the fix's own comment. Writing
"every" above a list does not make it one. So the document set is read from committed records, and
this file asserts three separable things about that:

  1. the set is DERIVED — a document a record names tomorrow is censused tomorrow, and that is proved
     by building a record and watching the derivation pick it up, not by reading the source;
  2. the set is the RIGHT ONE — it selects the fusion-partner manuscript, and it does not select the
     working notes, review backlogs, receipts and program memos that the first attempt at this class
     of predicate ("every .md in the submission directory") swept up on its way to reddening on a
     correct tree;
  3. the selectivity rule SURVIVED the widening — the census's first ever run reported 100 % coverage
     because `\\s+`, `\\d` and `[^.]{0,140}` match every sentence and bind none, and a widening that
     quietly relaxed that would report a bigger, falser number.

⚠ NOTE ON THIS FILE'S OWN STRING LITERALS. `claim_coverage._test_patterns` harvests regex-shaped
string literals out of every test module that names a document, and credits them to that document.
This module names several documents by path, so a literal here that looked like a regex would be
counted as coverage of a manuscript this module never checks a claim in — the census inflating
itself with its own guard. Literals here therefore avoid parentheses, brackets and backslash
escapes, which is the shape `_test_patterns` harvests on.
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import claim_coverage  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))

FUSION_PARTNER = "research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md"

#: ⛔ THE EXCLUSIONS ARE THE HALF THAT GOES WRONG QUIETLY. A gate that reds on true input is worse
#: than one that greens on false input, because the first thing anyone does is loosen it — and the
#: first attempt at a widened document set did exactly that by sweeping in working notes and a review
#: backlog that legitimately say things no artifact attests. Each row below is a real committed file
#: of a kind the census must never treat as a paper: a program memory, a review round, a working
#: record, a deposit receipt.
NOT_ENDPOINTS = [
    "research/manuscripts/nr4a3-program-map.md",
    "research/manuscripts/program/emc-treatment-strategy.md",
    "research/manuscripts/program/emc-post-degrader-options.md",
    "research/manuscripts/aso/fusion-junction-aso-working-record.md",
    "research/manuscripts/aso/fusion-junction-aso-paper-redteam-round5.md",
    "research/manuscripts/aso/fusion-junction-aso-submission-plan.md",
    "research/manuscripts/aso/fusion-junction-aso-preprint-checklist.md",
    "research/manuscripts/README.md",
]


def test_every_publication_endpoint_in_the_graph_is_censused():
    """⛔ THE RECORD IS THE SCOPE. Anything it calls a publication is read, or this is a list again.

    `systems/graph/publications.json` is this repository's source of truth for publication endpoints.
    If a paper it names is missing from the census, the census is scoped by somebody's memory of
    which papers matter — which is the state that left a live manuscript unread while it was being
    hardened.
    """
    graph = json.load(io.open(os.path.join(REPO, "systems", "graph", "publications.json"),
                              encoding="utf-8"))
    expected = {}
    for entry in graph:
        if entry.get("kind") != "publication":
            continue
        rel = entry.get("document", {}).get("file")
        if rel and rel.endswith(".md") and os.path.exists(os.path.join(REPO, rel)):
            expected[rel] = entry["id"]

    assert expected, (
        "no publication endpoint in the systems graph resolves to a file on disk, so this gate "
        "compared the census against an empty set and asserted nothing. Read the graph, not this "
        "failure message.")

    missing = sorted(rel for rel in expected if rel not in claim_coverage.PAPERS)
    assert not missing, (
        "the systems graph calls these documents publication endpoints and the census does not read "
        "them:\n  " + "\n  ".join(f"{expected[rel]}  {rel}" for rel in missing)
        + "\n\nThat is the defect this file exists to catch: the document set has been narrowed to "
          "something typed rather than something derived. Fix "
          "claim_coverage.endpoint_documents, never this expectation.")


def test_the_fusion_partner_manuscript_is_censused():
    """⭐ THE INSTANCE THE PREDICATE WAS WIDENED FOR, asserted separately from the class above.

    The class test would still pass if the graph stopped calling this paper an endpoint. This one
    says the specific document whose absence was the finding is in scope, so removing it takes a
    deliberate edit here and not just a graph edit somewhere else.
    """
    assert FUSION_PARTNER in claim_coverage.PAPERS, (
        "the fusion-partner stratification manuscript is not censused. It is a live publication "
        "endpoint, it was hardened for four blind review rounds with no instrument reading it, and "
        "measuring that was the whole reason the census stopped being a list of three files.")
    assert os.path.exists(claim_coverage.PAPERS[FUSION_PARTNER])


@pytest.mark.parametrize("rel", NOT_ENDPOINTS)
def test_the_predicate_does_not_sweep_up_notes_receipts_and_memos(rel):
    """⛔ A WIDENING IS ONLY A FIX ONCE YOU HAVE RUN IT, and this is the half that runs it backwards.

    Each of these is a committed markdown file living beside a manuscript. A predicate shaped like
    "markdown near a paper" takes all of them, and the census then reports hundreds of uncovered
    sentences from documents that were never claims — noise that buries the finding, in the
    instrument written to surface it.
    """
    assert os.path.exists(os.path.join(REPO, rel)), (
        f"{rel} is gone, so this exclusion is asserting nothing. Replace it with a file of the same "
        "kind — a program memo, a review round, a working record or a deposit receipt — rather than "
        "deleting the row, or the exclusion half of this predicate stops being tested.")
    assert rel not in claim_coverage.PAPERS, (
        f"the census has taken {rel} for a publication endpoint. It is a working document, not a "
        "paper. A predicate that reds or reports on true input is worse than a list, because the "
        "first thing anyone does is loosen it.")


def test_a_document_named_by_a_record_tomorrow_is_censused_tomorrow():
    """⛔⛔ THE ONE THAT CANNOT BE SATISFIED BY A LIST. Build a record; watch the derivation follow.

    Reading the source and seeing a loop proves nothing — round 17's finding was that three fixes
    whose own comments named the missed sibling still missed it. So this constructs a minimal
    repository: a publications graph naming a manuscript that did not exist a moment ago, and the
    manuscript beside it. If `endpoint_documents` is a derivation it returns the new file. If someone
    has replaced it with a literal set of paths, it returns nothing and this goes red.
    """
    with tempfile.TemporaryDirectory() as root:
        rel = "research/manuscripts/invented/a-paper-nobody-typed-into-a-list.md"
        os.makedirs(os.path.join(root, "systems", "graph"))
        os.makedirs(os.path.join(root, os.path.dirname(rel)))
        io.open(os.path.join(root, rel), "w", encoding="utf-8").write(
            "# A paper\n\nIt states a thing, and it states it in more than six words.\n")
        io.open(os.path.join(root, "systems", "graph", "publications.json"),
                "w", encoding="utf-8").write(json.dumps([
                    {"id": "PUB-INVENTED", "kind": "publication", "document": {"file": rel}}]))

        found = claim_coverage.endpoint_documents(repo=root)

    assert rel in found, (
        "a document registered as a publication endpoint in a records-only repository was not "
        "selected, so the census's document set is not derived from the record at all. Every "
        "manuscript added from now on would have to be remembered into a list by hand, which is the "
        "exact failure mode measured over 33 mutations: 6 of 11 list-scoped fixes regressed at a "
        "sibling, 3 of them at a sibling their own comment named.")
    assert found[rel].endswith("publications.json"), (
        "the derivation selected the new document but did not record which record named it. That "
        "provenance is what lets a reader see the predicate instead of trusting that one was used.")


def test_the_widening_did_not_relax_the_selectivity_rule():
    """⛔⛔ THE CENSUS'S FIRST EVER RUN REPORTED 100 %, AND THAT WAS THE BUG IT EXISTS TO FIND.

    Harvesting string literals picks up whitespace, single-digit and any-character patterns; they
    match every sentence and bind none. A census counting those is a gate reporting while measuring
    nothing, inside the instrument built to detect exactly that. Widening the document set is a
    change that could quietly buy a bigger number by relaxing this, so it is asserted separately from
    everything above.

    ⚠ BOTH DIRECTIONS. A rule that rejects everything is just as broken and is far harder to notice,
    because it makes the uncovered list longer, which reads as diligence.
    """
    sents = ["A sentence about a gapmer that runs to more than six words in total.",
             "A second sentence, also long enough to be counted, about something else.",
             "A third sentence, unrelated, and also long enough to survive the splitter.",
             "A fourth sentence, so that the share threshold has a population to act on.",
             "A fifth sentence, dated 2026-08-26, and carrying **a bold span** as well."]

    #: ⛔ THE STRUCTURE PATTERNS BELOW ARE NOT ALL CAUGHT THE SAME WAY, AND A MUTATION PROVED IT
    #: MATTERS. The first five match every sentence, so the SHARE half of the rule refuses them and a
    #: version of this test carrying only those stayed green while `_binds_literal_text` was disabled
    #: outright. The last two are the round-16 finding itself: an ISO date and a bold span match ONE
    #: sentence each — few, and binding nothing — so only the literal-text half can refuse them.
    for pattern in [r"\s+", r"\d", r"[^.]{0,140}", r"\w+", r".*",
                    r"\d{4}-\d{2}-\d{2}", r"\*\*[^*\n]+\*\*"]:
        assert not claim_coverage.is_selective(pattern, sents), (
            f"the pattern {pattern!r} was accepted as binding a sentence. It matches structure, not "
            "content, so every sentence it touches would be reported covered by a guard that would "
            "not go red if the claim inverted.")

    assert claim_coverage.is_selective(r"gapmer", sents), (
        "a literal word that appears in exactly one of four sentences was rejected as non-selective, "
        "so the rule now refuses real bindings and the uncovered list is inflated. An over-tight "
        "rule is the harder failure to see, because a longer uncovered list reads as diligence.")
    assert not claim_coverage.is_selective(r"sentence", sents), (
        "a word appearing in every sentence was accepted as binding one of them.")
    assert not claim_coverage.is_selective(r"gapmer", []), (
        "a pattern was called selective against a document with no sentences, which is a verdict "
        "fixed by the size of the population rather than by any reading.")


def test_this_module_does_not_credit_itself_as_coverage_of_any_manuscript():
    """⛔⛔ THE GUARD THAT WIDENS THE CENSUS MUST NOT BE COUNTED BY IT. Measured, not assumed.

    `claim_coverage._test_patterns` treats a test module as a reader of any document whose basename
    appears in its source — comments and bookkeeping constants included — and then credits that
    module's regex-shaped string literals to that document. This module names manuscripts on purpose,
    to assert what is in scope and what is not. If its literals were harvested, it would report
    coverage of papers whose claims it never checks: the census inflating itself with its own guard.

    ⚠ THIS IS NOT HYPOTHETICAL. On the day this file was written, moving four floor keys into a
    sibling test module took the cover letter from 10 covered sentences to 16 and gave the
    fusion-partner manuscript a witness that binds nothing in it. The rule that follows is that
    naming a manuscript in a test module is not free.
    """
    me = os.path.basename(__file__)
    credited = sorted({rel for rel in claim_coverage.PAPERS
                       for row in claim_coverage.census(rel)
                       for w in row["read_by"] if w.endswith(me)})
    assert not credited, (
        "the census credits this module with covering:\n  " + "\n  ".join(credited)
        + "\n\nA string literal here has taken a regex shape and is being counted as though it bound "
          "a claim. Rewrite it, or the widening this file guards would be paid for with a falsely "
          "larger coverage number.")


def test_every_ablation_exemption_names_a_censused_document_and_says_why():
    """⛔ AN EXEMPTION IS A RECORDED DEFECT, SO IT MUST NAME A REAL DOCUMENT AND CARRY ITS EVIDENCE.

    `claim_coverage.ABLATION_BLOCKED_BY_A_KNOWN_FALSE_POSITIVE` takes one document out of the
    ablation gate. That is the shape of thing that quietly becomes the way a red run is made green,
    so each row has to survive being read: it must name a document this census actually reads, that
    document must carry a floor, and the reason must be long enough to hold a sentence, a crediting
    pattern and the perturbation that proved nothing noticed. A bare path with an empty excuse fails
    here.
    """
    for rel, why in claim_coverage.ABLATION_BLOCKED_BY_A_KNOWN_FALSE_POSITIVE.items():
        assert rel in claim_coverage.PAPERS, (
            f"{rel} is exempted from ablation and is not a document the census reads at all. An "
            "exemption for a file nothing measures is a row nobody will ever be able to delete.")
        assert rel in claim_coverage.COVERAGE_FLOOR, (
            f"{rel} is exempted from ablation and carries no coverage floor, so nothing holds its "
            "coverage and nothing falsifies it. That is not an exemption from one gate, it is a "
            "document with no gate at all.")
        assert isinstance(why, str) and len(why) >= 60, (
            f"the exemption for {rel} does not say what was measured. Record the sentence, the "
            "pattern that credits it and the perturbation that turned nothing red, or delete the "
            "row: an exemption without its evidence is indistinguishable from a gate being "
            "switched off.")
