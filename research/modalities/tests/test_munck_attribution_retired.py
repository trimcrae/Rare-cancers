"""THE "Munck 2022" ATTRIBUTION IS RETIRED — pinned so it cannot come back by accident.

WHAT WAS WRONG. Five repo files attributed the field's one NR4A3/NOR-1 ligand-discovery campaign to
"Munck 2022" (one of them to "Munck JM et al."), always without a PMID. Measured in CI on 2026-08-03
(fetch-literature run 30858114744), against two independent indexes:

    AUTH:"Munck" AND (NR4A3 OR "NOR-1" OR "NOR1")          Europe PMC -> hitCount 0
    AUTH:"Munck" AND "nuclear receptor" AND PUB_YEAR:2022   Europe PMC -> hitCount 0
    Munck[Author] AND (NR4A3 OR "NOR-1")                    PubMed     -> count 0, "No items found."
    TITLE:"Druggability Evaluation" AND TITLE:"NOR-1"       Europe PMC -> exactly 1 hit, PMID 35704774

No paper by any author named Munck exists on this receptor. The title resolves uniquely to:

    Zaienne D, Arifi S, Marschner JA, Heering J, Merk D. "Druggability Evaluation of the Neuron Derived
    Orphan Receptor (NOR-1) Reveals Inverse NOR-1 Agonists." ChemMedChem 2022;17(16):e202200259.
    PMID 35704774; PMC9542104; doi 10.1002/cmdc.202200259.

WHY THIS IS WORTH A TEST RATHER THAN JUST A FIX. The cost of the error was not untidiness. Route 5 was
demoted in `emc-post-degrader-options.md` partly for lacking an experimental anchor, while the anchor sat
in IDEAS.md under a name that matches no paper and therefore could not be looked up by a future session --
and `target-route-options.md`'s reference table carried the SAME paper as two separate rows, "Zaienne 2022"
and "Munck 2022", which is what a misattribution looks like once it has propagated. A mis-cited source is
evidence the repo holds and cannot find.

WHAT THIS TEST ALLOWS. Per CLAUDE.md section 1.2 a superseded value is never silently dropped -- it stays
quotable. So the string "Munck" is permitted wherever it is explicitly marked as retained/superseded, and
forbidden as a live citation. The marker must appear NEAR the mention (same paragraph-ish window), not
merely somewhere in the file, or a single appendix line at the bottom would license the error above it.
"""
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# The correct citation must remain findable by its PMID. If someone re-titles or moves the record,
# this fails and they must re-point it deliberately.
CORRECT_PMID = "35704774"

# Files whose text is checked. Corpus/target JSONs are included because a search query that mentions
# the retired name is fine, but a citation in one would not be.
CHECKED_SUFFIXES = (".md",)

# A mention is CLEARED if one of these appears within RETENTION_WINDOW characters of it. These are the
# repo's standing vocabulary for "this is retained, not current" (CLAUDE.md section 1.2).
RETENTION_MARKERS = (
    "superseded",
    "retained",
    "retired",
    "names no paper",
    "citation error",
    "wrong author",
    "misattribution",
    "mis-attribut",
    "resolution item",
    "correction",
)
RETENTION_WINDOW = 700

# Where the correction itself lives. This file is allowed to discuss the error at length.
OWNER_DOC = os.path.join("research", "modalities", "nr4a3-druggability-reconciliation.md")


def _md_files():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", ".cache"}]
        for fn in files:
            if fn.endswith(CHECKED_SUFFIXES):
                yield os.path.join(root, fn)


def _uncleared_mentions(text):
    """Return (position, context) for every 'Munck' not covered by a nearby retention marker."""
    bad = []
    for m in re.finditer(r"Munck", text):
        lo = max(0, m.start() - RETENTION_WINDOW)
        hi = min(len(text), m.end() + RETENTION_WINDOW)
        window = text[lo:hi].lower()
        if not any(marker in window for marker in RETENTION_MARKERS):
            bad.append((m.start(), text[max(0, m.start() - 120):m.start() + 120]))
    return bad


def test_no_live_munck_citation_anywhere():
    """'Munck' may survive only as an explicitly-retained superseded attribution."""
    offenders = []
    for path in _md_files():
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        if "Munck" not in text:
            continue
        for pos, ctx in _uncleared_mentions(text):
            offenders.append(f"{os.path.relpath(path, REPO)}@{pos}: ...{ctx.strip()}...")
    assert not offenders, (
        "Live 'Munck' citation(s) found. No such paper exists on NR4A3/NOR-1 (measured, see this "
        "file's docstring). Cite Zaienne 2022, PMID " + CORRECT_PMID + ", and if you must keep the old "
        "name, mark it superseded/retained next to the mention:\n  " + "\n  ".join(offenders)
    )


def test_the_correction_has_a_home_and_carries_the_pmid():
    """The register must exist, name the retired string, and carry the PMID that replaces it."""
    path = os.path.join(REPO, OWNER_DOC)
    assert os.path.exists(path), f"the correction's one home is missing: {OWNER_DOC}"
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    assert "Munck" in text, "the superseded attribution must stay quotable in its register"
    assert CORRECT_PMID in text, "the register must carry the replacing PMID"
    assert "Zaienne" in text


def test_every_corrected_site_carries_the_pmid():
    """A bare 'Zaienne 2022' can regress into an unlookup-able citation the same way 'Munck' did.

    So every file that had the wrong attribution must now carry the PMID at least once. This is the
    part that stops the fix decaying back into the failure mode.
    """
    previously_wrong = [
        os.path.join("research", "IDEAS.md"),
        os.path.join("research", "manuscripts", "emc-treatment-roadmap.md"),
        os.path.join("research", "manuscripts", "degrader-vs-synthetic-lethal.md"),
        os.path.join("research", "manuscripts", "target-route-options.md"),
        os.path.join("research", "modalities", "nr4a3-degrader-design-spec.md"),
    ]
    missing = []
    for rel in previously_wrong:
        path = os.path.join(REPO, rel)
        if not os.path.exists(path):
            continue  # a file may legitimately be retired; absence is not this test's business
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            if CORRECT_PMID not in fh.read():
                missing.append(rel)
    assert not missing, (
        "these files carried the retired attribution and must now carry PMID "
        + CORRECT_PMID + " so the citation is lookup-able: " + ", ".join(missing)
    )
