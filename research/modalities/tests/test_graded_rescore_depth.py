"""Search DEPTH is a property of a graded re-score, and it must be measured rather than assumed.

★★ THE INSTANCE (2026-08-14). `submission_tables._graded_loads` keys the residual-cleavage-load
column on `(source_screen, sequence)` and carried no depth. Step 0 of
`scripts/regenerate_aso_chain.sh` re-scores every screen it finds, which produces 53 graded
artifacts of the DEEP re-screens alongside the 39 committed default-depth ones. A default and a
deep re-score of the same seam and the same design then wrote to the same key, and the "if the two
MODELS disagree, say so" fold joined them: the clean-designs table read `31.4 / 101 / 0 / 0` for
`GGGCATATCTCTATAA` — the deep screen's two bounds and the default screen's two bounds in one cell,
in a table whose legend's first sentence says it is the default-depth result. Six of the nine rows
moved that way.

⛔⛔ AND THE OBVIOUS FIX WAS A NO-OP, WHICH IS THE REAL LESSON HERE. `aso_screen_sets.is_deep` read
`artifact["method"]["parameters"]` and `artifact["oligos"]` — the shape of a BLAST SCREEN. A graded
re-score has NEITHER key: it holds per-design loads and no hits at all. So the fallback
`max(..., default=0) > 15` evaluated `0 > 15` and returned **False for every graded artifact ever
written**. Measured before the fix: 77 sixteen-mer graded artifacts all reporting default-depth,
derived from 78 sixteen-mer screens of which 38 are deep. Passing `select=ass.is_default_depth`
would therefore have kept all 92, changed nothing, and looked correct in the diff.

So this file pins the two halves that have to hold together:
  1. a graded re-score RECORDS the depth of the screen it re-scored, because nothing in its own
     shape can recover it (`grade_panel` writes `source_screen_depth`); and
  2. `is_deep` REFUSES where it cannot read, so the failure can never again be a silent `False`.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

MODALITIES = Path(__file__).resolve().parents[1]
REPO = MODALITIES.parents[1]
MOD = str(MODALITIES)
sys.path.insert(0, MOD)
sys.path.insert(0, str(REPO / "research" / "manuscripts"))

import aso_screen_sets as ass  # noqa: E402
import junction_aso_offtarget as jo  # noqa: E402

#: A seam that was screened at BOTH depths, so the two really can collide on one key.
DEFAULT_SCREEN = "junction-aso-offtarget-e12n3.json"
DEEP_SCREEN = "junction-aso-offtarget-e12n3-deep500-b1.json"


def _rescore_into(tmp: Path, *screens: str) -> Path:
    """Copy screens into `tmp` and write their `-graded.json` beside them. Offline, $0."""
    paths = []
    for name in screens:
        src = MODALITIES / name
        if not src.exists():
            pytest.skip(f"{name} is not in this checkout")
        shutil.copy(src, tmp / name)
        paths.append(str(tmp / name))
    jo.rescore(paths)
    return tmp


def _committed_graded_names():
    """The graded re-scores git is tracking. ⚠ NOT the disk — a chain run adds 53 more to it."""
    out = subprocess.run(["git", "ls-files", "research/modalities"], cwd=REPO,
                         capture_output=True, text=True, timeout=20)
    if out.returncode != 0:
        pytest.skip("git cannot answer in this checkout")
    return {os.path.basename(p) for p in out.stdout.split("\n") if p.endswith("-graded.json")}


# ═════════════════════════════════════════════════════════════════════════════════════════════
# 1 · the predicate refuses instead of voting "default"
# ═════════════════════════════════════════════════════════════════════════════════════════════
def test_is_deep_refuses_a_family_that_has_no_depth_axis():
    """A design-evaluation panel is an exhaustive local scan — it has no ceiling to raise.

    ⚠ THE `-deep500` IN ITS FILENAME DESCRIBES THE CAMPAIGN, NOT THE FILE. Measured 2026-08-14:
    `aso-insilico-evaluation-e1n3-clean9-deep500.json` and `aso-insilico-evaluation-e1n3.json` are
    identical in content. Answering `False` would report that filename's claim as a measurement.
    """
    panels = [s for _g, ss in ass.iter_geometries(ass.DESIGN_EVALUATION, root=MOD) for s in ss]
    assert panels, "no design-evaluation panels were read at all"
    with pytest.raises(ass.DepthError, match="no search-depth axis"):
        ass.is_deep(panels[0])
    # and the complement must inherit the refusal rather than swallowing it into a bool
    with pytest.raises(ass.DepthError):
        ass.is_default_depth(panels[0])


def test_is_deep_refuses_a_graded_rescore_that_records_no_depth(tmp_path):
    """The regression guard for the exact silent-False that made this whole defect invisible."""
    _rescore_into(tmp_path, DEFAULT_SCREEN)
    graded = tmp_path / DEFAULT_SCREEN.replace(".json", "-graded.json")
    art = json.loads(graded.read_text())
    del art["source_screen_depth"]                       # a pre-2026-08-14 graded artifact
    graded.write_text(json.dumps(art))

    screens = [s for _g, ss in ass.iter_geometries(ass.GRADED_RESCORE, root=str(tmp_path))
               for s in ss]
    assert len(screens) == 1
    with pytest.raises(ass.DepthError, match="UNKNOWN, not default"):
        ass.is_deep(screens[0])


def test_every_committed_graded_rescore_records_the_depth_it_inherited():
    """All 39 in the deposit answer the question, so no consumer meets the refusal above."""
    committed = _committed_graded_names()
    graded = [s for _g, ss in ass.iter_geometries(ass.GRADED_RESCORE, root=MOD) for s in ss
              if s.name in committed]
    assert graded, "no graded re-scores were read at all"
    missing = [s.name for s in graded if s.artifact.get("source_screen_depth") is None]
    assert not missing, (
        f"{len(missing)} committed graded re-score(s) record no source-screen depth, so their "
        f"depth is unrecoverable: {missing[:5]}. Re-run step 0 of regenerate_aso_chain.sh.")
    # every one of them answers, and the committed corpus is the default-depth one
    assert all(ass.is_default_depth(s) for s in graded), (
        "a committed graded re-score reads as DEEP. The Methods release the deeper re-screens "
        "ungraded, so a deep graded artifact in the deposit contradicts the paper's inventory.")


# ═════════════════════════════════════════════════════════════════════════════════════════════
# 2 · the depth a re-score reports is the depth of the screen it re-scored
# ═════════════════════════════════════════════════════════════════════════════════════════════
def test_a_graded_rescore_inherits_the_depth_of_the_screen_it_rescored(tmp_path):
    """Measured against the SOURCE screen's own reading, not against a filename or a constant."""
    _rescore_into(tmp_path, DEFAULT_SCREEN, DEEP_SCREEN)

    src_depth = {}
    for _g, ss in ass.iter_geometries(ass.BLAST_SCREEN, root=str(tmp_path)):
        for s in ss:
            src_depth[s.name] = ass.is_deep(s)
    assert src_depth == {DEFAULT_SCREEN: False, DEEP_SCREEN: True}, src_depth

    for _g, ss in ass.iter_geometries(ass.GRADED_RESCORE, root=str(tmp_path)):
        for s in ss:
            origin = s.artifact["_generated_from"]
            assert ass.is_deep(s) is src_depth[origin], (
                f"{s.name} reports deep={ass.is_deep(s)} but was derived from {origin}, which "
                f"reads deep={src_depth[origin]}")


# ═════════════════════════════════════════════════════════════════════════════════════════════
# 3 · the clean-designs table's column, which is what the defect actually corrupted
# ═════════════════════════════════════════════════════════════════════════════════════════════
def test_table3_residual_loads_are_default_depth_only_when_both_depths_are_present(tmp_path,
                                                                                   monkeypatch):
    """⛔ THE END-TO-END ONE. With both depths on disk, the column must be the default-depth one.

    The two depths genuinely disagree for this seam — asserted below rather than assumed, because a
    test in which they happened to agree would pass whether or not the filter existed.
    """
    import submission_tables as st  # noqa: PLC0415

    _rescore_into(tmp_path, DEFAULT_SCREEN, DEEP_SCREEN)
    monkeypatch.setattr(st, "MOD", str(tmp_path))
    both = st._graded_loads()

    # the same tree with only the default-depth re-score in it
    only_default = tmp_path / "default_only"
    only_default.mkdir()
    for n in (DEFAULT_SCREEN, DEFAULT_SCREEN.replace(".json", "-graded.json")):
        shutil.copy(tmp_path / n, only_default / n)
    monkeypatch.setattr(st, "MOD", str(only_default))
    default_only = st._graded_loads()

    assert both, "no residual loads were read at all"
    assert both == default_only, (
        "the clean-designs table's residual-load column changed when the deeper re-scores appeared on disk. It is "
        "the default-depth result by its own legend, so it must not.")

    # ⚠ THE TEST ONLY PROVES SOMETHING IF THE TWO DEPTHS DIFFER. Show that they do — read straight
    # off the deep re-score, since `_graded_loads` is default-depth-only by construction now and
    # rightly refuses a tree holding nothing else.
    deep = json.loads((tmp_path / DEEP_SCREEN.replace(".json", "-graded.json")).read_text())
    deep_loads = {}
    for oligos in (deep["per_oligo"] or {}).values():
        for seq, rec in (oligos or {}).items():
            lo, hi = rec.get("residual_cleavage_load_lo"), rec.get("residual_cleavage_load_hi")
            if lo is not None:
                deep_loads.setdefault((deep["source_screen"], seq), set()).add((lo, hi))
    shared = {k for k in default_only if k in deep_loads}
    assert shared, "the two depths share no (seam, design) key, so nothing could ever have collided"
    assert any(f"{lo:g}" != default_only[k] for k in shared for lo, hi in deep_loads[k]
               if lo == hi) or any(lo != hi for k in shared for lo, hi in deep_loads[k]), (
        "the default and deep re-scores agree on every shared key here, so this test would pass "
        "with the depth filter removed. Pick a seam whose depths differ.")


def test_no_residual_load_cell_pools_two_depths():
    """The committed table, read as a reader reads it: one number or one model-disagreement pair.

    ⚠ `a / b` IS THE *MODEL* DISAGREEMENT FORM and is legitimate. `a / b / c / d` is two depths
    wearing that costume, which is exactly how `31.4 / 101 / 0 / 0` got into the clean-designs table.
    """
    tables = REPO / "research/manuscripts/aso/fusion-junction-aso-submission-tables.md"
    rows = [ln for ln in tables.read_text().splitlines() if ln.startswith("| 5′-")]
    assert rows, "no clean-designs table rows were found"
    for ln in rows:
        cells = [c.strip() for c in ln.split("|")]
        for c in cells:
            assert c.count(" / ") <= 1, f"a table cell pools more than two values: {c!r} in {ln!r}"


# ═════════════════════════════════════════════════════════════════════════════════════════════
# 4 · the deposit inventory the manuscript states
# ═════════════════════════════════════════════════════════════════════════════════════════════
@pytest.mark.committed_artifact
def test_the_deeper_rescores_are_not_committed():
    """⛔ THE METHODS SAY SO IN SO MANY WORDS, so committing them would falsify the paper.

    "all 38 junction screens, and 39 of the 93 screens released in total … and the 53 deeper
    re-screens, which are released ungraded." They are reproducible outputs of step 0 of the chain
    and are deliberately not part of the deposit.

    ⚠ ASSERTED AGAINST GIT, NOT AGAINST THE DISK, and the difference is the point. A chain run
    legitimately materialises all 92 in the working tree — that is what step 0 does — so a
    disk-count assertion would go red on a developer who had just run the chain and would say
    nothing about what is actually deposited. What must stay true is that the deposit ships 39.
    Both consumers that read these files are invariant to the other 53 being present: that table
    filters on measured depth, and the archive manifest lists tracked files only.
    """
    committed = _committed_graded_names()
    assert len(committed) == 39, (
        f"{len(committed)} graded re-scores are COMMITTED, not 39. The Methods state the deposit "
        f"ships 39 and releases the 53 deeper re-screens ungraded; changing that means changing "
        f"the paper's release inventory, not just the tree.")
