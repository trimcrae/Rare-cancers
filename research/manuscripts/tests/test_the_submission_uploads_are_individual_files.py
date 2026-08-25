"""The submission is a set of individual files, and each one was CUT from the manuscript.

⛔ WHY THIS EXISTS. Reviewer checklist item A7: "upload individual files, not one composed PDF."
The composed PDF is the artefact nearest to hand — it is what the build produces, it is what gets
linked in chat, and a submission assembled from it is returned before peer review. The packet's
upload manifest is the list that prevents that, and a list is worth nothing if the files on it do
not exist or have gone stale under the manuscript.

⛔⛔ AND THE EXPENSIVE FAILURE IS NOT AN ABSENT FILE, IT IS A PRESENT STALE ONE. A missing title
page is noticed at the portal in ten seconds. A title page carrying last week's disclosure is
noticed by nobody, and the portal states verbatim that "the author information you enter at
submission must exactly match what is included on your manuscript and/or title page". So the
checks below are, in order: the files exist; nothing on them was typed rather than cut; and every
identifier the blinded build strips out has a home on the page that replaces it.
"""
import hashlib
import io
import json
import os
import re
import sys
import zipfile

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import build_submission_parts as parts  # noqa: E402
import build_submission_pdf as bsp  # noqa: E402

PACKET = os.path.join(HERE, "SUBMISSION-PACKET.md")

#: Every (part, paper) pair the builder declares. Derived, so a part added there is tested here
#: with no edit — and a part REMOVED there stops being tested, which is the correct behaviour and
#: is why `test_the_packet_names_every_upload_and_each_one_exists` checks the packet separately.
CASES = [(part_name, paper)
         for part_name in sorted(parts.PARTS)
         for paper in parts.PARTS[part_name]["papers"]]
IDS = [f"{paper}-{part_name}" for part_name, paper in CASES]


def _docx_text(path):
    """Everything a reader of this .docx can see — its paragraph text AND its link targets.

    ⛔ THE LINK TARGET IS NOT IN THE TEXT, AND LEAVING IT OUT FAILED A CORRECT FILE. The ORCID is
    written `[0000-…](https://orcid.org/0000-…)`, so the converter puts the digits in
    `document.xml` and the URL in `document.xml.rels`; a check that read only the first reported a
    title page carrying a live ORCID link as missing `orcid.org`. What matters is what the file
    conveys, and a hyperlink conveys its target.
    """
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
        names = zf.namelist()
        rels = "".join(zf.read(n).decode("utf-8") for n in names if n.endswith(".rels"))
    text = re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", xml))
    return parts._normalise(text + "\n" + "\n".join(re.findall(r'Target="([^"]+)"', rels)))


@pytest.mark.parametrize("part_name,paper", CASES, ids=IDS)
def test_every_declared_submission_part_is_on_disk(part_name, paper):
    path = parts.out_path(paper, part_name)
    assert os.path.exists(path), (
        f"⛔ {os.path.relpath(path, REPO)} is declared by build_submission_parts.PARTS and is not "
        f"on disk. {parts.PARTS[part_name]['why']}. Build it: "
        f"`python3 research/manuscripts/build_submission_parts.py`.")


@pytest.mark.parametrize("part_name,paper", CASES, ids=IDS)
def test_no_submission_part_is_stale_against_its_manuscript(part_name, paper):
    """The stamp's manuscript hash still matches the manuscript. Hashes, never mtimes."""
    path = parts.out_path(paper, part_name)
    stamp_path = path + ".build-stamp.json"
    assert os.path.exists(stamp_path), f"{os.path.relpath(path, REPO)} has no build stamp"
    stamp = json.load(io.open(stamp_path, encoding="utf-8"))
    for rel, recorded in stamp["built_from"].items():
        actual = hashlib.sha256(io.open(os.path.join(HERE, rel), "rb").read()).hexdigest()
        assert actual == recorded, (
            f"⛔ {os.path.basename(path)} was cut from a different version of {rel}. Every edit "
            f"to the manuscript invalidates it, which is the whole reason it is a build step and "
            f"not a document. Rerun `python3 research/manuscripts/build_submission_parts.py`.")


@pytest.mark.parametrize("part_name,paper", CASES, ids=IDS)
def test_nothing_on_a_submission_part_was_typed_rather_than_cut(part_name, paper):
    """Every block on the shipped file is findable in the manuscript it claims to come from.

    ⛔ THIS IS THE ONE-OF-A-PAIR GUARD, and it reads the SHIPPED ARTEFACT rather than the builder's
    intent. `build_submission_parts` cuts each block out of the manuscript, so this holds by
    construction today — and holds by construction is exactly the claim that stops being true the
    first time somebody edits a .docx in Word to fix a typo before submitting. Then the submission
    carries two descriptions of one thing and the journal gets whichever was uploaded.
    """
    path = parts.out_path(paper, part_name)
    #: ⛔ NOT A SKIP, AND THE META-GUARD IS RIGHT ABOUT WHY. Every file this suite reads is
    #: committed, so "the file is missing" can only fire on a broken tree — which is exactly the
    #: moment a guard has to speak rather than go quiet. The existence test above says the same
    #: thing; two guards naming the same absent artifact is cheap, and one of them silently
    #: standing down is not.
    assert os.path.exists(path), (
        f"⛔ {os.path.relpath(path, REPO)} is not on disk, so nothing here compared it against "
        f"{bsp.PAPERS[paper]['manuscript']}. Build it: "
        f"`python3 research/manuscripts/build_submission_parts.py`.")
    shipped = _docx_text(path)
    #: ⚠ FLATTENED BY THE BUILDER'S OWN HELPER, not by a second copy of the same three regexes.
    #: `_probe` flattens markdown links; a manuscript normalised any other way disagrees with the
    #: probe on every block that carries one, and reports a correctly cut affiliation as typed.
    manuscript = parts.flatten(parts._manuscript(bsp.PAPERS[paper]))
    strays = []
    for label, block in parts.PARTS[part_name]["blocks"](bsp.PAPERS[paper]):
        probe = parts._probe(label, block, parts.PARTS[part_name]["min_probe_words"])
        if probe not in shipped:
            strays.append(f"{label or 'an unlabelled block'}: not in the shipped file")
        elif probe not in manuscript:
            strays.append(f"{label or 'an unlabelled block'}: on the file, not in the manuscript")
    assert not strays, (
        f"⛔ {os.path.basename(path)} and {bsp.PAPERS[paper]['manuscript']} disagree — "
        + "; ".join(strays))


def test_the_title_page_carries_every_identifier_the_blinded_copy_strips():
    """What `anonymise()` removes has to land somewhere, and the title page is that somewhere.

    ⛔ THE TWO FILES ARE ONE DECISION, NOT TWO. NAT's guidelines state single-anonymized twice and
    double-anonymized once on the same page, so a blinded manuscript may be what is uploaded. If it
    is, the author, the correspondence address and the ORCID reach the editor ONLY through the
    title page — and if the title page does not carry one of them, the redaction has deleted it
    from the submission rather than relocated it. That is a silent loss: both files build, both
    files verify, and the editor has no way to contact anybody.
    """
    paper = "aso-journal"
    path = parts.out_path(paper, "title-page")
    #: ⛔ NOT A SKIP — see the note in the test above. A missing title page under the
    #: double-anonymized reading means the submission names nobody at all, which is the loudest
    #: thing in this module, not the quietest.
    assert os.path.exists(path), (
        f"⛔ {os.path.relpath(path, REPO)} is not on disk, so nothing carries the identity the "
        f"blinded build strips out. Build it: "
        f"`python3 research/manuscripts/build_submission_parts.py`.")
    page = _docx_text(path)
    body = parts._manuscript(bsp.PAPERS[paper])
    blinded, applied = bsp.anonymise(body)
    assert applied, "anonymise() matched nothing — its own build gate reports that, not this one"

    #: ⚠ THE PROBE IS WHAT anonymise() ACTUALLY TOOK OUT, not a list of identifiers written here.
    #: A hand-written list is a second home for the redaction rules and goes stale the day one is
    #: added; this reads the difference between the two bodies instead.
    plain, blind = parts._normalise(body), parts._normalise(blinded)
    lost = [w for w in re.findall(r"[\w.@\-]{4,}", plain)
            if w not in blind and not w.startswith("[")]
    assert lost, "the blinded body lost no token at all — check bsp._ANON_RULES, not this test"

    #: ⚠ ONE CLASS OF REDACTED TOKEN DOES NOT BELONG ON THE TITLE PAGE, AND IT IS SUBTRACTED BY
    #: ADDRESS RATHER THAN BY NAME. `anonymise` also strips the Zenodo DOI — not because the DOI
    #: is a person, but because a reviewer who resolves it reaches a deposit that names one. Its
    #: home is `## Statements and Declarations`, which stays in the manuscript the editor reads;
    #: moving it to the title page would take the data-availability statement out of the paper.
    #: Subtracting the section rather than listing the DOI keeps this derived: a second
    #: identifier that lives in Declarations is handled with no edit here.
    _, decl_end, decl_after = bsp.section_span(body, "Statements and Declarations")
    declarations = parts._normalise(body[decl_after:decl_end])
    missing = sorted({w for w in lost if w not in page and w not in declarations})
    assert not missing, (
        f"⛔ the blinded build strips {', '.join(missing)} and the title page does not carry "
        f"{'it' if len(missing) == 1 else 'them'}. Under the double-anonymized reading the title "
        f"page is the only file that names the author; an identifier that is on neither is not "
        f"redacted, it is gone. Add it to the manuscript's front matter, which is where "
        f"_TITLE_PAGE_PARTS reads from.")


def test_the_packet_names_every_upload_and_each_one_exists():
    """The generated checklist a depositor reads at the portal has no MISSING file on it.

    ⚠ THE PACKET IS READ AT THE MOMENT THERE IS NO TIME TO VERIFY IT — that is why it carries a
    `--check` of its own. This is the other half: `--check` proves the file reproduces from its
    generator, and this proves the paths inside it resolve.
    """
    assert os.path.exists(PACKET), "SUBMISSION-PACKET.md is generated; run submission_packet.py"
    text = io.open(PACKET, encoding="utf-8").read()
    section = text.split("Nucleic Acid Therapeutics", 1)
    assert len(section) == 2, "the packet no longer has a Nucleic Acid Therapeutics section"
    block = section[1].split("\n## ", 1)[0]
    assert "**Files to upload, one per portal slot**" in block, (
        "⛔ the NAT section has no upload manifest. Checklist item A7 is that the submission is "
        "individual files rather than one composed PDF, and the manifest is where that list "
        "lives; without it the packet describes a document instead of an envelope.")
    rows = re.findall(r"^\| `([^`]+)` \|", block, re.M)
    assert len(rows) >= 5, f"only {len(rows)} upload row(s) — expected the whole envelope"
    absent = [r for r in rows if not os.path.exists(os.path.join(HERE, r))]
    assert not absent, (
        f"⛔ the upload manifest names {len(absent)} file(s) that do not exist: "
        f"{', '.join(absent)}. A checklist read at the portal must not send a depositor looking "
        f"for a file nothing builds.")
    assert "NOT BUILT" not in block, (
        "⛔ the NAT upload manifest carries a NOT BUILT row. Every deliverable it names is "
        "buildable here: `build_submission_parts.py` for the Word files, "
        "`figures/svg_to_print_formats.py` for the EPS and TIFF.")
