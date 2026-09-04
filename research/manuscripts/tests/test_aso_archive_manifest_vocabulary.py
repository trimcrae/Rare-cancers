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

@pytest.mark.parametrize("path_sep", ["/", "\\"])
def test_archive_inventory_matches_git_paths_on_either_platform(tmp_path, monkeypatch, path_sep):
    """Native separators must not silently drop tracked files from the deposit."""
    folder = tmp_path / "nested"
    folder.mkdir()
    for name in ("kept.json", "untracked.json", "kept-graded.json"):
        (folder / name).write_text("{}", encoding="utf-8")
    monkeypatch.setattr(m, "REPO", str(tmp_path))
    native_relpath = os.path.relpath
    with monkeypatch.context() as paths:
        paths.setattr(m.os, "sep", path_sep)
        paths.setattr(m.os.path, "relpath", lambda *args: native_relpath(*args).replace("\\", "/").replace("/", path_sep))
        result = m._resolve(["nested/*.json"], tracked={"nested/kept.json", "nested/kept-graded.json"})
    assert result == ["nested/kept.json"]


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
    """The vocabulary itself, over whatever is on disk now.

    ⚠ IN A CORRECT TREE THE THREE FIELDS ARE EMPTY, SO THE LOOP BELOW ITERATES NOTHING (noted
    2026-08-19). That is the state `test_every_junction_has_both_arms` asserts, and it means this
    test's own loop cannot fail today. The property is real and is carried by two other things: the
    checker is driven directly with the tags that got through, in
    `test_a_filename_tag_is_refused_rather_than_deposited`, and the vocabulary's DISCRIMINATION is
    asserted here — a pattern that matched everything would let the loop pass on a full field just
    as quietly as on an empty one.
    """
    assert m.JUNCTION_LABEL_RE.match(m.JUNCTION_LABEL_EXAMPLE), (
        f"the vocabulary pattern no longer matches its own example {m.JUNCTION_LABEL_EXAMPLE!r}")
    for tag in sorted(REGRESSED_TAGS):
        assert not m.JUNCTION_LABEL_RE.match(tag), (
            f"the vocabulary pattern now ACCEPTS {tag!r}, a filename tag from the 2026-08-14 "
            "regression. The loop below would then pass over exactly the values it exists to "
            "reject.")
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
    """⚠ THE DEPOSITED BYTES, not just the generator — the manifest is what actually ships.

    ⛔ AND IT COMPARES THE WHOLE BLOCK, BECAUSE IT USED TO COMPARE `[] == []` THREE TIMES
    (2026-08-19). The three `junctions_*` fields are empty in a correct tree — that is what
    `test_every_junction_has_both_arms` asserts one line above — so this test was three assertions
    that an empty list equals an empty list, and every OTHER field of the same generated block went
    unchecked: `n_screens_committed`, `n_screens_gap_resolved`, the orientation-filtered screen
    list, the gap-resolved screens with no committed rescore. Those are the fields a new screen
    artifact moves, so the one edit most likely to leave the deposited manifest stale — adding a
    screen — was invisible here.

    ⚠ COMPUTED IN PROCESS, NOT BY RUNNING THE GENERATOR. `_screen_coverage()` is the same function
    `aso_archive_manifest.py` writes the block from, so this compares the deposit against a fresh
    reading of the tree without a subprocess and without writing anything.
    """
    import hashlib  # noqa: PLC0415
    import json  # noqa: PLC0415

    path = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-archive-manifest.json")
    with open(path, encoding="utf-8") as fh:
        deposited = (json.load(fh).get("gaps") or {}).get("screen_coverage") or {}
    assert deposited, "the deposited manifest carries no screen_coverage block at all"

    def digest(block):
        return hashlib.sha256(
            json.dumps(block, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    if digest(deposited) != digest(coverage):
        differing = sorted(k for k in set(deposited) | set(coverage)
                           if deposited.get(k) != coverage.get(k))
        raise AssertionError(
            f"the deposited manifest's screen_coverage block differs from the tree in {differing}: "
            + "; ".join(f"{k}: deposited {deposited.get(k)!r} vs tree {coverage.get(k)!r}"[:220]
                        for k in differing[:4])
            + ". Re-run research/manuscripts/aso_archive_manifest.py.")
    #: the vocabulary fields are still named individually, so a future reader can see WHICH of them
    #: this file exists for even when the hash above is what fails
    for field in JUNCTION_FIELDS:
        assert deposited.get(field) == coverage[field], field
