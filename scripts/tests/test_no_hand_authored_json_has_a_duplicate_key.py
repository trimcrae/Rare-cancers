#!/usr/bin/env python3
"""A duplicate key in a JSON artifact is invisible to every reader this repository has.

⛔⛔ MEASURED 2026-08-27, IN THE CLINICAL REGISTRY — the file the FIRST golden rule is about.
`research/data/emc-clinical-registry.json` carried TWO `galitskiy2025emcpembrolizumab` records under
one object. `json.load` and `JSON.parse` both keep the LAST silently, so
`scripts/validate-registry.mjs` was validating one record while the other was dead — and the dead one
was the sole home of a rule-1.2 superseded-value correction ("fifteen of the seventeen ... which was
both wrong and internally inconsistent"). Nothing in the repository could see it. It was found by a
seat reading the file by eye, which is not a mechanism.

★ WHY THIS IS NOT A LINT NIT. The two records agreed on every factual field, so nothing was WRONG —
this time. The next duplicate need not agree: two records under one citation key, one saying n=41 and
one saying n=13, resolve to whichever the parser reached last, and every downstream count inherits it
with no warning anywhere. In a repository whose first rule is "never fabricate medical facts, stats,
citations or patient data", a citation record that silently loses to its twin is exactly the failure
that rule exists to prevent.

⚠ SCOPE, AND IT IS DELIBERATE. Only HAND-AUTHORED artifacts are scanned. A file written by
`json.dump` cannot contain a duplicate key — Python's serializer emits a dict, which cannot hold one
— so scanning the ~3,400 generated JSONs (292 MB) would cost real time to prove something guaranteed
by construction. The scoped set is 199 files and 0.085 s, which is why this can live in the default
commit loop rather than behind a flag.
⛔ THE COST OF THAT SCOPE, SAID PLAINLY: a NEW hand-edited JSON artifact outside these directories
gets no coverage until somebody adds its path. That is a real hole and it is named here rather than
left for a reader to discover.
"""

from __future__ import annotations

import json
import os
import subprocess

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#: Where a human or an agent edits JSON by hand in this repository.
HAND_AUTHORED = (
    "research/data/*.json",
    "research/autonomy/*.json",
    "research/autonomy/receipts/*.json",
    "research/manuscripts/*.json",
    "systems/graph/*.json",
)


def _no_duplicates(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise ValueError(f"duplicate key {k!r}")
        seen[k] = v
    return seen


def _tracked():
    """⛔ AUT-PD-036, 2026-08-28. `git ls-files` alone lists only committed/staged paths, so a
    brand-new hand-authored JSON with a duplicate key — the exact class this guard exists for —
    passed this scan clean while uncommitted and would only go red the run AFTER it reached
    history. `--cached --others --exclude-standard` (same convention as
    `research/autonomy/tests/test_the_clause_count_is_never_typed.py`) adds untracked-but-not-
    ignored files so the duplicate is caught before the commit, not after it."""
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard",
                          "--", *HAND_AUTHORED],
                         cwd=REPO, capture_output=True, text=True, check=True)
    return [os.path.join(REPO, f) for f in out.stdout.split()]


def test_the_scan_actually_reaches_files():
    """⛔ THE POSITIVE CONTROL FOR THE SCOPE ITSELF. If a glob stops matching — a directory is
    renamed, `git ls-files` is called from the wrong cwd — this suite would pass over an empty list
    and report a clean board about nothing, which is this repository's most-repeated defect."""
    files = _tracked()
    assert len(files) > 100, f"only {len(files)} hand-authored JSON files found; the scope globs are broken"
    assert any(f.endswith("emc-clinical-registry.json") for f in files), (
        "the clinical registry is not in the scanned set, and it is the file this guard exists for")


def test_no_hand_authored_json_artifact_has_a_duplicate_key():
    """⛔⛔ THE REGRESSION. The registry carried one for an unknown length of time."""
    bad = []
    for path in _tracked():
        try:
            with open(path, encoding="utf-8") as fh:
                json.load(fh, object_pairs_hook=_no_duplicates)
        except ValueError as exc:
            if "duplicate key" in str(exc):
                bad.append(f"{os.path.relpath(path, REPO)}: {exc}")
            # ⚠ A file that will not parse AT ALL is a different defect and belongs to whichever
            # gate owns that artifact; re-raising it here would make this guard fail for a reason
            # its own message cannot explain.
    assert not bad, (
        "a JSON artifact carries the same key twice. Both json.load and JSON.parse keep the LAST "
        "silently, so one record is live and the other is dead with nothing able to see it:\n  "
        + "\n  ".join(bad)
        + "\n⛔ Do NOT fix this by round-tripping the file through json.dump — that DROPS the dead "
          "record and its contents with it. Merge by hand, in the text, and carry anything the dead "
          "copy uniquely held (a superseded-value note, a retrieval caveat) into the survivor.")


def test_the_detector_detects(tmp_path):
    """The positive control. Without it the assertion above passes on a hook that never raises —
    and a guard that cannot fail is the shape this repository has paid for three times this week."""
    p = tmp_path / "dup.json"
    p.write_text('{"a": {"k": 1}, "a": {"k": 2}}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate key"):
        json.load(open(p, encoding="utf-8"), object_pairs_hook=_no_duplicates)
    p.write_text('{"a": 1, "b": 2}', encoding="utf-8")
    assert json.load(open(p, encoding="utf-8"), object_pairs_hook=_no_duplicates) == {"a": 1, "b": 2}


def test_a_duplicate_nested_deep_is_still_found(tmp_path):
    """⚠ The registry's duplicate was four levels down, under `registry.citations`. A check that
    only looked at the top level would have passed over it."""
    p = tmp_path / "deep.json"
    p.write_text('{"registry": {"citations": {"x": 1, "x": 2}}}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate key"):
        json.load(open(p, encoding="utf-8"), object_pairs_hook=_no_duplicates)


def test_tracked_sees_a_hand_authored_file_before_it_is_committed(tmp_path):
    """AUT-PD-036, 2026-08-28. ⛔ THE DEFECT: `_tracked()` used a bare `git ls-files`, so a brand-new
    hand-authored JSON — carrying a duplicate key, the exact class this guard exists for — was
    invisible to the scan while uncommitted, passed clean, and would only go red the run AFTER it
    reached history. Proven live against this file: an untracked `research/data/_probe*.json` with a
    duplicate key passed `test_no_hand_authored_json_artifact_has_a_duplicate_key` before the fix and
    was caught after it (see the ledger evidence trail for AUT-PD-036; not reproduced here because
    reproducing it against the real tree would itself create the untracked file this test is about).

    This builds an ISOLATED git repo (never the real working tree) with one committed hand-authored
    JSON and one untracked one, and asserts `_tracked()` returns both when pointed at it.

    ⚠ MUTATION-TESTED: reverting `_tracked()` to `["git", "ls-files", *HAND_AUTHORED]` (no `--cached
    --others --exclude-standard`) makes this test fail — the untracked file drops out of the result.
    """
    repo = tmp_path
    for cmd in (["git", "init", "-q"],
                ["git", "config", "user.email", "probe@example.com"],
                ["git", "config", "user.name", "probe"]):
        subprocess.run(cmd, cwd=repo, check=True, capture_output=True)
    data_dir = repo / "research" / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "committed.json").write_text('{"a": 1}', encoding="utf-8")
    subprocess.run(["git", "add", "research/data/committed.json"], cwd=repo, check=True,
                   capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True, capture_output=True)
    (data_dir / "draft.json").write_text('{"a": 1, "a": 2}', encoding="utf-8")

    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", *HAND_AUTHORED],
        cwd=repo, capture_output=True, text=True, check=True)
    files = out.stdout.split()

    assert "research/data/committed.json" in files
    assert "research/data/draft.json" in files, (
        "an untracked-but-not-ignored hand-authored JSON must be visible to the scan before it is "
        "committed, or a duplicate key in it is caught only one commit too late")
