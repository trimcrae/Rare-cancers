#!/usr/bin/env python3
"""A deposit field that names junctions must hold junctions.

★★ THE INSTANCE (2026-08-14). `aso_archive_manifest`'s three `junctions_*` fields were built by
slicing a prefix and `.json` off a basename, so they held FILENAME TAGS. That was invisible for as
long as every seam was screened exactly once under one name — 38 junctions, 38 tags, two
vocabularies agreeing by coincidence. The gap-length work broke the coincidence (93 tags against 38
labels) and `junctions_screened_by_blast_arm_only` went from `[]` to
`["fuse8n3-20mer-deep500-b2", "taf15e11n3-18mer-deep500-b2", "taf15e1n3-20mer-deep500-b2"]`, with
`junctions_screened_by_exhaustive_arm_only` picking up `e1n3-spanprobe` the same way. In a deposit
manifest those read as COVERAGE GAPS — junctions with only one arm of evidence. There are none:
every one of the 38 junctions carries a BLAST screen, an exhaustive panel and a design panel.

⛔ THE FIX IS THE ASSERTION, NOT THE NEW READER. Reading `junction_label` repairs today's values and
does nothing for tomorrow, because the next author to add a source sees a set of strings flowing
into a set of strings with no indication that the field has a vocabulary at all. So the vocabulary
is a checked property, and this file is what makes the check run.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MANUSCRIPTS))
sys.path.insert(0, MANUSCRIPTS)
sys.path.insert(0, os.path.join(REPO, "research", "modalities"))

import aso_archive_manifest as m  # noqa: E402

#: Every field in the manifest whose name promises junctions.
JUNCTION_FIELDS = ("junctions_with_a_design_panel_but_no_screen",
                   "junctions_screened_by_blast_arm_only",
                   "junctions_screened_by_exhaustive_arm_only")

#: The exact values the regression deposited, kept so the specific defect cannot come back quietly.
REGRESSED_TAGS = {"fuse8n3-20mer-deep500-b2", "taf15e11n3-18mer-deep500-b2",
                  "taf15e1n3-20mer-deep500-b2", "e1n3-spanprobe"}


@pytest.fixture(scope="module")
def coverage():
    return m._screen_coverage()


def test_every_junction_field_holds_junction_labels(coverage):
    """The vocabulary itself, over whatever is on disk now."""
    for field in JUNCTION_FIELDS:
        assert field in coverage, f"{field} is gone from the manifest"
        for value in coverage[field]:
            assert m.JUNCTION_LABEL_RE.match(value), (
                f"{field} holds {value!r}, which is not a junction label like "
                f"{m.JUNCTION_LABEL_EXAMPLE!r}. A filename tag in a junctions field reads as a "
                f"coverage gap in the deposit.")


def test_the_filename_tags_that_regressed_are_not_back(coverage):
    for field in JUNCTION_FIELDS:
        assert not (set(coverage[field]) & REGRESSED_TAGS), (
            f"{field} has the 2026-08-14 filename tags back: "
            f"{sorted(set(coverage[field]) & REGRESSED_TAGS)}")


def test_the_coverage_check_reports_a_real_vocabulary(coverage):
    """⚠ A guard over an empty vocabulary proves nothing, so the corpus has to be there."""
    assert coverage["ok"] is True, coverage.get("⛔_wrong_vocabulary")
    assert coverage["n_junctions_known"] == 38, coverage["n_junctions_known"]
    assert "⛔_wrong_vocabulary" not in coverage


def test_every_junction_has_both_arms(coverage):
    """The honest answer these three fields exist to give, stated once so a future gap is loud."""
    for field in JUNCTION_FIELDS:
        assert coverage[field] == [], (
            f"{field} is no longer empty: {coverage[field]}. If that is a real coverage gap it is "
            f"a finding; if the values are not junction labels the reader above them broke.")


def test_a_filename_tag_is_refused_rather_than_deposited():
    """⛔ THE GUARD ITSELF — driven with the exact tags that got through, not a synthetic string."""
    res = {"ok": True}
    kept = m._labels_only("junctions_screened_by_blast_arm_only",
                          {"EWSR1_e12__NR4A3_e3", "taf15e11n3-18mer-deep500-b2"}, res)
    assert kept == ["EWSR1_e12__NR4A3_e3"], kept
    assert res["ok"] is False, "a wrong-vocabulary value did not turn the coverage check red"
    rejected = res["⛔_wrong_vocabulary"]["junctions_screened_by_blast_arm_only"]
    assert rejected["rejected"] == ["taf15e11n3-18mer-deep500-b2"]
    assert rejected["n_rejected"] == 1


def test_the_committed_manifest_agrees_with_what_is_on_disk(coverage):
    """⚠ THE DEPOSITED BYTES, not just the generator — the manifest is what actually ships."""
    import json  # noqa: PLC0415

    path = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-archive-manifest.json")
    with open(path, encoding="utf-8") as fh:
        deposited = (json.load(fh).get("gaps") or {}).get("screen_coverage") or {}
    for field in JUNCTION_FIELDS:
        assert deposited.get(field) == coverage[field], (
            f"the deposited manifest's {field} is {deposited.get(field)!r} but the tree says "
            f"{coverage[field]!r}. Re-run research/manuscripts/aso_archive_manifest.py.")
