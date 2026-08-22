"""Every gene-shaped identifier in a submitted document is one a committed artifact names.

⛔⛔ WHY THIS EXISTS — `NR4A3` -> `NR4A7` PASSED EVERY SEMANTIC GATE (measured 2026-08-22, round 16).

Found by ablation, not by review: `claim_ablation` perturbs the first digit-run of a censused
sentence, and in "Selectivity is the wild-type *NR4A3* half-maximal knockdown concentration ..." the
first digit-run is the 3 of the program's central gene. The full sweep with that one character
changed:

    lint_consistency  rc=0        lint_claims  rc=0        lint_citations  rc=0
    research/manuscripts/tests    877 passed
    research/modalities  -k aso   354 passed, 2 skipped

The only failures were STALENESS detectors — the PDF no longer matched its source — so a rebuild
would have shipped it. `RNase-H1` -> `RNase-H7` behaves the same way.

⚠ THIS IS THE PROVENANCE AXIS, NOT THE STRENGTH AXIS, AND CLAUDE.md §7 SAYS THEY ARE ORTHOGONAL: a
hedged sentence on a fabricated identifier passes `lint_claims`. Every numeric guard in this suite
reads QUANTITIES; an identifier is neither a quantity nor a claim word, so nothing was looking. It is
the same "surface with zero instruments" shape the whole review has been closing, in the one place
where being wrong is unrecoverable — a reader ordering against the wrong gene.

★ THE RULE: an identifier earns its place by appearing in a committed artifact. Anything else is
either a typo or a fact from the literature, and a fact from the literature must be declared here
with the citation that carries it — never left to look like an artifact-backed symbol.
"""
from __future__ import annotations

import io
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")

DOCUMENTS = {
    "journal-article": os.path.join(ASO, "fusion-junction-aso-journal-article.md"),
    "journal-tables": os.path.join(ASO, "fusion-junction-aso-journal-tables.md"),
    "cover-letter": os.path.join(ASO, "fusion-junction-aso-cover-letter.md"),
    "extended-report": os.path.join(ASO, "fusion-junction-aso-research-article.md"),
}

#: Where an identifier may be attested: every committed machine-readable artifact in the research
#: tree. ⚠ THAT IS DELIBERATELY PERMISSIVE AND STILL BITES, WHICH IS THE POINT — the corpus holds
#: ~126,500 distinct identifier-shaped tokens, and `NR4A7`, `NR4A9`, `EWSR7` and `TAF19` are in none
#: of them (measured 2026-08-22). Real symbols are a SPARSE set, so a one-digit slip lands outside it.
#: A narrow whitelist would have been stricter and far more brittle: the first version listed five
#: files and flagged 23 honest identifiers in the extended report — GenBank accessions, a GEO series,
#: microsatellite markers and comparator genes — every one of which the wider corpus attests.
ARTIFACT_ROOTS = [os.path.join(REPO, "research", d) for d in ("modalities", "data", "literature")]
ARTIFACT_SUFFIXES = (".json", ".csv", ".jsonl")
#: A file bigger than this is a bulk screen dump; reading it would dominate the gate's runtime.
MAX_ARTIFACT_BYTES = 8_000_000

#: A gene symbol, a cell-line code, an enzyme with a family number: two or more capitals with a digit.
_IDENTIFIER = re.compile(r"\b[A-Z][A-Z0-9]{1,6}[0-9][A-Z0-9]*\b")
_RNASE = re.compile(r"\bRNase-H[0-9]+\b")

#: ⛔ AN IDENTIFIER NO ARTIFACT NAMES IS ALLOWED ONLY WITH THE CITATION THAT CARRIES IT, AND THE
#: CITATION IS CHECKED — a bare allowlist would re-open the hole this file exists to close, and
#: CLAUDE.md §7 forbids writing an identifier from recollection. Each entry: why it is not in an
#: artifact, and a PMID that must appear in the same document.
CITED_ONLY = {
    "NAB2": "the NAB2::STAT6 fusion of solitary fibrous tumour, named only as a comparator",
    "STAT6": "the NAB2::STAT6 fusion of solitary fibrous tumour, named only as a comparator",
    "NR4A1": "the NR4A paralogue, named to say the panel does NOT target it",
}

#: ⛔ NOT AN ALLOWLIST — A FLOOR. These must be PRESENT; their absence means a document lost the
#: identifier its whole result is about, which no "unknown symbol" check would notice.
MUST_APPEAR = {
    "journal-article": ("NR4A3", "EWSR1", "TAF15"),
    "journal-tables": ("NR4A3",),
    "extended-report": ("NR4A3", "EWSR1"),
}

#: Markdown/typesetting tokens that match the identifier shape without being identifiers.
_NOT_AN_IDENTIFIER = {"H1", "H2", "H3", "P1", "P2", "P3", "R1", "R2", "R3", "R4", "R5",
                      "T1", "T2", "S1", "S2", "S3", "S4", "UTF8", "ISO8601"}


_ATTESTED_CACHE = None


def _attested():
    """Every identifier-shaped token any committed artifact uses. ~1.3 s over ~820 files, memoised."""
    global _ATTESTED_CACHE
    if _ATTESTED_CACHE is not None:
        return _ATTESTED_CACHE
    seen = set(_IDENTIFIER.findall(
        io.open(os.path.join(ASO, "fusion-junction-aso-sequences.csv"), encoding="utf-8").read()))
    for root in ARTIFACT_ROOTS:
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(ARTIFACT_SUFFIXES):
                    continue
                path = os.path.join(dirpath, name)
                try:
                    if os.path.getsize(path) > MAX_ARTIFACT_BYTES:
                        continue
                    seen |= set(_IDENTIFIER.findall(
                        io.open(path, encoding="utf-8", errors="ignore").read()))
                except OSError:
                    continue
    _ATTESTED_CACHE = seen
    return seen


def _text(key):
    return io.open(DOCUMENTS[key], encoding="utf-8").read()


@pytest.mark.parametrize("key", sorted(DOCUMENTS))
def test_every_gene_identifier_is_attested_by_an_artifact_or_a_citation(key):
    """⛔ A ONE-CHARACTER SLIP IN A GENE SYMBOL IS UNRECOVERABLE AND WAS UNGUARDED."""
    assert os.path.exists(DOCUMENTS[key]), (
        f"{key} ({os.path.basename(DOCUMENTS[key])}) is not in this checkout. Every document this "
        "suite reads is committed, so a missing one is a broken tree — which is exactly when this "
        "guard has to speak, not stand down.")
    text = _text(key)
    attested = _attested()
    found = {t for t in _IDENTIFIER.findall(text) if t not in _NOT_AN_IDENTIFIER}
    unknown = sorted(t for t in found if t not in attested and t not in CITED_ONLY)
    assert not unknown, (
        f"{key} names identifier(s) that no committed artifact uses and that are not declared as "
        f"cited-only: {', '.join(unknown)}\n\n"
        "Either the symbol is a typo — check it character by character against the artifact, because "
        "a gene symbol off by one digit reads as a real gene — or it is a fact from the literature, "
        f"in which case add it to CITED_ONLY in {os.path.basename(__file__)} with its reason and the "
        "PMID that carries it. Never write an identifier from recollection.")


@pytest.mark.parametrize("key", sorted(MUST_APPEAR))
def test_the_document_still_names_the_gene_its_result_is_about(key):
    """⛔ THE UNKNOWN-SYMBOL CHECK ABOVE CANNOT SEE AN IDENTIFIER THAT IS SIMPLY GONE."""
    assert os.path.exists(DOCUMENTS[key]), (
        f"{key} ({os.path.basename(DOCUMENTS[key])}) is not in this checkout, so the gene this "
        "document's result is about cannot be checked at all.")
    text = _text(key)
    missing = [g for g in MUST_APPEAR[key] if not re.search(rf"\b{g}\b", text)]
    assert not missing, (
        f"{key} no longer names {', '.join(missing)}. That is the gene this document's result is "
        "about; if it has genuinely been renamed, MUST_APPEAR is the one place to say so.")


def test_the_rnase_family_number_is_the_one_the_mechanism_needs():
    """⛔ `RNase-H1` -> `RNase-H7` ALSO PASSED EVERYTHING. The gapmer mechanism names one enzyme."""
    # ⛔ EVERY DOCUMENT, NOT THE TWO OBVIOUS ONES. The cover letter names RNase-H1 too — in the
    # reviewer-expertise paragraph — and ablation found `RNase-H1` -> `RNase-H7` passing there while
    # the same edit was caught in the article. One-of-a-pair, inside the fix for one-of-a-pair.
    for key in sorted(DOCUMENTS):
        assert os.path.exists(DOCUMENTS[key]), f"{key} is not in this checkout"
        forms = set(_RNASE.findall(_text(key)))
        wrong = sorted(f for f in forms if f != "RNase-H1")
        assert not wrong, (
            f"{key} names {', '.join(wrong)}. A gapmer recruits RNase-H1; any other family number "
            "states a different mechanism, and nothing else in this suite reads enzyme names.")


def test_the_attestation_set_is_not_empty_so_this_guard_is_not_vacuous():
    """⛔⛔ EVERY ASSERTION ABOVE IS AN ARGUMENT FROM A GREEN RUN, AND A MISSING ARTIFACT WOULD MAKE
    `attested` EMPTY — at which point the unknown-symbol check would flag EVERYTHING, not nothing.
    That direction is loud. The quiet failure is the opposite: `_IDENTIFIER` stops matching, `found`
    goes empty, and the check passes while reading nothing. Assert it sees the symbols it must."""
    attested = _attested()
    for gene in ("NR4A3", "EWSR1", "TAF15", "TCF12"):
        assert gene in attested, (
            f"{gene} is in no committed artifact, so this guard cannot attest it. An artifact root in "
            "ARTIFACT_ROOTS has moved, or the corpus is not being read.")
    # ⛔ AND THE SET MUST STILL DISCRIMINATE. A corpus this wide is only worth having if a one-digit
    # slip in the central symbols still falls outside it. If one of these ever becomes attested — a
    # new screen dump listing every paralogue, say — this guard has gone quietly vacuous and the
    # attestation source needs narrowing, not this assertion relaxing.
    for slip in ("NR4A7", "NR4A9", "EWSR7", "TAF19"):
        assert slip not in attested, (
            f"{slip} is attested by some committed artifact, so a one-character corruption of a "
            "central gene symbol would now PASS the check above. The corpus has become too wide to "
            "discriminate; narrow ARTIFACT_ROOTS rather than deleting this assertion.")
    found = {t for t in _IDENTIFIER.findall(_text("journal-article")) if t not in _NOT_AN_IDENTIFIER}
    assert "NR4A3" in found, (
        "_IDENTIFIER no longer matches NR4A3 in the journal article, so the check above is reading "
        "an empty set and passing vacuously.")
