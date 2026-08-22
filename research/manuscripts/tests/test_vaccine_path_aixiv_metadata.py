"""The aiXiv submission metadata must not drift from the manuscript, and must not be corrupted text.

⛔ WHY THIS EXISTS. The metadata is what a third party publishes as the version of record; the
manuscript is what a reader is told. Nothing else compares them — the metadata is not a "generated
deposit artifact", so it falls outside preflight gate 10.

⚠ AN EARLIER VERSION OF THIS FILE RE-IMPLEMENTED THE MARKDOWN TRANSFORM AND ASSERTED THE TWO AGREED.
That validates nothing: the same regex on both sides agrees with itself while corrupting the text
identically. It did, twice — a stripped `[9]` left "melanoma , which", and `HLA-B\\*15:01` lost its
asterisk and kept its backslash. Both passed. So the tests below assert **properties of the output**
and **reproducibility from the generator**, never equality with a second copy of the transform.
"""
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
MS = os.path.join(REPO, "research", "manuscripts", "neoantigen",
                  "emc-vaccine-development-path.md")
META = os.path.join(REPO, "research", "manuscripts", "neoantigen",
                    "emc-vaccine-path-aixiv-metadata.json")
GEN = os.path.join(REPO, "research", "manuscripts", "build_aixiv_metadata.py")

#: SubmissionCreate's required fields, from aiXiv's openapi.json (literature/aixiv-api-surface-2026-08-22/).
REQUIRED = ("title", "authorship_type", "authors", "corresponding_author",
            "category", "keywords", "license", "doc_type")


def _meta():
    with open(META) as fh:
        return json.load(fh)


def test_the_committed_metadata_reproduces_from_its_generator():
    """The one check that makes the others meaningful: the file is not hand-edited."""
    r = subprocess.run([sys.executable, GEN, "--paper", "vaccine-path", "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_every_field_aixiv_requires_is_present_and_non_empty():
    missing = [k for k in REQUIRED if not _meta().get(k)]
    assert not missing, f"aiXiv SubmissionCreate requires {missing}"


def test_the_abstract_carries_no_residual_markup():
    """⛔ Each probe is a defect that actually shipped into a dry-run payload."""
    a = _meta()["abstract"]
    assert not re.findall(r"\[[0-9]+\]", a), "citation markers survived into the abstract"
    assert "\\" not in a, "a backslash escape survived — see the HLA-B*15:01 incident"
    assert "  " not in a, "doubled space, usually the hole left by a deleted marker"
    assert not re.findall(r" [,.;:]", a), "orphaned punctuation left by a deleted marker"
    assert "**" not in a and "##" not in a, "markdown emphasis or heading survived"


def test_hla_allele_names_keep_their_asterisk():
    """The paper's subject IS allele coverage; a mangled allele name is a factual error."""
    alleles = re.findall(r"HLA-[A-Z]\*?[0-9]{2}:[0-9]{2}", _meta()["abstract"])
    assert alleles, "expected HLA allele names in this abstract"
    for a in alleles:
        assert "*" in a, f"{a} lost its asterisk"


def test_the_title_is_the_manuscripts_heading():
    with open(MS) as fh:
        heading = [l for l in fh.read().split("\n") if l.startswith("# ")][0][2:].strip()
    # Compared on alphanumerics only, so this does not become a second copy of the transform.
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())  # noqa: E731
    assert norm(_meta()["title"]) == norm(heading)


def test_the_corresponding_author_matches_the_manuscript_masthead():
    with open(MS) as fh:
        assert _meta()["corresponding_author"] in fh.read()


def test_authorship_is_declared_human_and_the_ai_use_section_carries_the_detail():
    """⚠ The author of record is a person; the tooling is disclosed in the paper, not in the badge.

    Declaring `ai` would attribute authorship to models that took no responsibility for the claims;
    declaring `human` while hiding the tooling would be the opposite failure. The honest combination
    is this field plus a standing AI-use declaration in the manuscript.
    """
    assert _meta()["authorship_type"] == "human"
    with open(MS) as fh:
        text = fh.read().lower()
    assert "ai use" in text or "use of ai" in text, (
        "authorship_type=human is only honest while the manuscript discloses its AI tooling")


def test_the_licence_is_the_one_the_checklist_commits_to():
    assert _meta()["license"] == "CC-BY-4.0"
