"""Every sequence in the deposited PDF must survive a copy-paste, and the PDF must say where the
canonical machine-readable copy is.

⛔ WHY, AND IT IS THE PROCESS GAP RATHER THAN A TYPO. Seven adversarial rounds, a firewalled cold
reader and an adversarial reviewer with artifact access all ran against the MARKDOWN. Not one read
the built PDF — which is the only artifact a depositor uploads and a screener opens. So an entire
defect class was structurally invisible, and the paper was called deposit-ready while it carried one.

MEASURED 2026-08-17 by extracting the text layer of the built manuscript PDF: a sequence in a table
cell arrives as a bare base string with NO `5′-`/`-3′` delimiters, immediately adjacent to a numeric
cell —

    CAGGGCATATCATCAAACCA   3   123   6   189 ...

so whether the sequence and the next column fuse is a property of the READER's extractor, not of the
document. One extractor returned `5′-GGGCATATCATCAAAC3′3 8 123 → 6`: a 16-mer carrying a trailing
digit with its delimiter lost. A reader who pastes that into a synthesis order has bought a molecule
about which nothing in this paper is true, and bioRxiv's own full-text conversion inherits the same
text layer.

⚠ THIS GUARD READS THE PDF, NOT THE MARKDOWN, ON PURPOSE. Checking the source is what missed it. The
markdown was correct at every point; the defect was created by typesetting.

⛔ IT MUST NOT SKIP WHEN ITS EXTRACTOR IS ABSENT. `tests.yml` already states this repository's
position, in the comment on its own install line: "The test CAN run anywhere — it needs no
credentials and touches no network — so the fix is to install the dependency, not to skip the test.
A guard that cannot run is not a guard that passed." `pdfminer.six` is installed in CI for exactly
that reason, and a missing import fails here rather than passing quietly.
"""
import csv
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASO = os.path.join(REPO, "research", "manuscripts", "aso")

#: The submission-format PDF is the one bioRxiv asks for and the one a depositor uploads.
PDF = os.path.join(ASO, "fusion-junction-aso-research-article-manuscript.pdf")
SEQ_CSV = os.path.join(ASO, "fusion-junction-aso-sequences.csv")


def _extract(path):
    try:
        from pdfminer.high_level import extract_text
    except Exception as exc:  # noqa: BLE001 - a missing extractor is a failure, never a skip
        pytest.fail(
            "pdfminer.six is not importable, so the deposited PDF's text layer is UNCHECKED. "
            "Install it (it is in tests.yml's install line) rather than skipping: a guard that "
            f"cannot run is not a guard that passed. Underlying error: {exc}")
    return extract_text(path)


def _canonical_sequences():
    with open(SEQ_CSV, encoding="utf-8") as fh:
        rows = list(csv.DictReader(ln for ln in fh if not ln.startswith("#")))
    assert rows, f"{SEQ_CSV} carries no rows"
    return {r["sequence"] for r in rows}


@pytest.fixture(scope="module")
def pdf_text():
    assert os.path.exists(PDF), (
        f"{PDF} is missing. It is the file a depositor uploads; its absence is not a reason to skip "
        "the check.")
    return _extract(PDF)


def test_no_sequence_in_the_pdf_is_fused_to_the_next_column(pdf_text):
    """A base string immediately followed by a digit is the wrong-reagent case.

    ⚠ NESTED SEQUENCES ARE NOT THE DEFECT AND MUST NOT FIRE HERE. `GGGCATATCATCAAAC` is a prefix of
    `GGGCATATCATCAAACC`, so "followed by another base" is legitimate and common. What is never
    legitimate is a base run followed by a DIGIT — no oligonucleotide continues into a number — and
    that is exactly the shape a fused table cell takes.
    """
    seqs = _canonical_sequences()
    bad = []
    for m in re.finditer(r"[ACGT]{12,}\d", pdf_text):
        run = m.group(0)[:-1]
        # Only report where the run ENDS a canonical sequence: an arbitrary base run bumping a
        # figure axis label is not this defect.
        if any(run.endswith(s) for s in seqs):
            bad.append(pdf_text[max(0, m.start() - 40):m.end() + 10].replace("\n", "⏎"))
    assert not bad, (
        f"{len(bad)} sequence(s) in the deposited PDF run directly into a numeric cell, so a reader "
        "copy-pasting one gets a base string with a trailing digit and orders the wrong molecule:\n"
        + "\n".join("  " + b for b in bad[:6])
        + "\nFix at the table GENERATOR by giving every sequence cell its 5′-/-3′ delimiters, and "
          "re-build the PDF.")


def test_every_sequence_in_the_pdf_carries_its_delimiters(pdf_text):
    """The extractor-INDEPENDENT form of the defect, and the one that actually generalises.

    ⛔ THE FUSION TEST ABOVE IS NECESSARY AND NOT SUFFICIENT, AND SAYING SO IS THE POINT. Measured
    2026-08-17: with `pdfminer` the Table 5 cells separate with newlines and nothing fuses, while
    the extractor that first reported this defect returned `...CAAAC3′3 8 123`. Same PDF, same
    bytes, opposite verdicts — so a guard written against one extractor's behaviour would have gone
    green on a document that corrupts sequences for somebody else's reader.

    What does not depend on the extractor is whether the DOCUMENT bounds the string. A sequence
    printed as `5′-XXXX-3′` is delimited whatever reads it; a bare base run sitting against a
    numeric cell is ambiguous to every reader, and merely happens to be resolved by the newline
    that one library inserts. So the property asserted here is the document's, not the tool's.
    """
    seqs = sorted(_canonical_sequences(), key=len, reverse=True)
    bare, seen = [], set()
    for s in seqs:
        for m in re.finditer(re.escape(s), pdf_text):
            span = (m.start(), m.end())
            # A nested match (a 16-mer inside the 18-mer that contains it) is one printed string,
            # not two, and must not be counted twice or reported as undelimited on its own.
            if any(a <= span[0] and span[1] <= b for a, b in seen):
                continue
            before = pdf_text[max(0, m.start() - 4):m.start()].rstrip()
            after = pdf_text[m.end():m.end() + 4].lstrip()
            if before.endswith(("5′-", "5'-")) or after.startswith(("-3′", "-3'")):
                seen.add(span)
                continue
            bare.append(pdf_text[max(0, m.start() - 30):m.end() + 22].replace("\n", "⏎"))
    assert not bare, (
        f"{len(bare)} sequence occurrence(s) are printed in the deposited PDF WITHOUT their 5′-/-3′ "
        "delimiters, so nothing in the document separates the bases from the cell beside them and "
        "whether they fuse is up to the reader's PDF extractor:\n"
        + "\n".join("  " + b for b in bare[:6])
        + "\nGive every sequence cell its delimiters at the table GENERATOR, then rebuild the PDF.")


def test_no_sequence_is_split_across_a_line_in_the_pdf(pdf_text):
    """Bases broken mid-string are unrecoverable by a reader who cannot see the original."""
    split = re.findall(r"5[′']-[ACGT]{1,19}\s*\n+\s*[ACGT]{1,19}-3[′']", pdf_text)
    assert not split, (
        f"{len(split)} sequence(s) have their BASES broken across a line in the deposited PDF, e.g. "
        f"{split[0]!r}. Set sequences non-breaking at the generator.")


def test_the_pdf_names_the_canonical_machine_readable_sequence_file(pdf_text):
    """The durable fix for a text layer is not needing to read it.

    ⭐ Padding table cells makes today's extractor behave; it does not make a PDF a machine-readable
    record, and the next extractor is not ours to control. The deposit therefore ships the sequences
    in a form that was never typeset — and that is worth nothing if the paper does not tell a reader
    it exists, because the reader who needs it is by definition the one reading the PDF.
    """
    flat = " ".join(pdf_text.split())
    assert "fusion-junction-aso-sequences" in flat, (
        "the deposited PDF never names the canonical machine-readable sequence file "
        "(fusion-junction-aso-sequences.csv / .fasta). A reader with only the PDF has no way to "
        "learn that a copy-paste-safe copy of every sequence travels with the archive.")


def test_every_sequence_the_pdf_prints_is_in_the_canonical_file(pdf_text):
    """The canonical file must be canonical — a sequence in the paper and not in it is a hole.

    ⚠ READ FROM THE PDF, WHICH IS WHAT THE READER HAS. The generator asserts the same contract
    against the markdown at build time; this asserts it survived typesetting, which is the step
    that has now been shown to change what a sequence IS.
    """
    seqs = _canonical_sequences()
    printed = set(re.findall(r"5[′']-([ACGT]{12,25})-3[′']", pdf_text))
    missing = sorted(printed - seqs)
    assert not missing, (
        f"{len(missing)} sequence(s) are printed in the deposited PDF and absent from the canonical "
        f"machine-readable file: {missing[:6]}. Re-run "
        "research/manuscripts/aso_sequence_manifest.py, or add the artifact the design comes from "
        "to its source list.")
