#!/usr/bin/env python3
"""Every workflow must stay under GitHub's hard `workflow_dispatch` input cap.

WHY THIS EXISTS. On 2026-07-24 `fusion-cpu-extras.yml` reached **26** inputs — two concurrent sessions each
added a few — and GitHub rejected every dispatch with:

    422 failed to parse workflow: you may only define up to 25 `inputs` for a `workflow_dispatch` event

The workflow was the control plane for the whole Vast lane, so it took the retrospective, the co-fold lane,
diag and the targeted kill down with it, and the only symptom was a 422 at dispatch time — long after the
commit that caused it. The cap is a property of the file, so it is checkable offline: this test turns "the
next person to add an input silently bricks the workflow" into a failing test in the same commit.

If this test fails: MERGE two related inputs rather than deleting a capability (e.g. `vast_kill` + `diag_filter`
became one `vast_selector` — same kind of value, mutually exclusive modes).
"""
import glob
import os

import pytest

yaml = pytest.importorskip("yaml")

# tests/ -> modalities/ -> research/ -> repo root
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_WORKFLOW_DIR = os.path.join(_REPO_ROOT, ".github", "workflows")

GITHUB_MAX_DISPATCH_INPUTS = 25


def _workflows():
    return sorted(glob.glob(os.path.join(_WORKFLOW_DIR, "*.yml")) +
                  glob.glob(os.path.join(_WORKFLOW_DIR, "*.yaml")))


def test_workflow_dir_is_found():
    assert _workflows(), f"no workflows found under {_WORKFLOW_DIR}"


@pytest.mark.parametrize("path", _workflows(), ids=lambda p: os.path.basename(p))
def test_workflow_dispatch_inputs_under_github_cap(path):
    with open(path) as f:
        doc = yaml.safe_load(f)
    if not isinstance(doc, dict):
        pytest.skip("not a mapping")
    # PyYAML parses the bare key `on:` as the boolean True, so accept both spellings.
    on = doc.get("on", doc.get(True)) or {}
    if not isinstance(on, dict):
        pytest.skip("no workflow_dispatch")
    inputs = ((on.get("workflow_dispatch") or {}) or {}).get("inputs") or {}
    n = len(inputs)
    assert n <= GITHUB_MAX_DISPATCH_INPUTS, (
        f"{os.path.basename(path)} defines {n} workflow_dispatch inputs; GitHub rejects the whole workflow "
        f"above {GITHUB_MAX_DISPATCH_INPUTS} and EVERY dispatch of it fails with a 422. Merge two related "
        f"inputs instead of removing a capability.")


def test_the_control_plane_workflow_keeps_headroom_visible():
    """fusion-cpu-extras is the Vast control plane and sits nearest the cap, so its count is asserted
    explicitly — a reader should be able to see how many slots are left without running anything."""
    path = os.path.join(_WORKFLOW_DIR, "fusion-cpu-extras.yml")
    with open(path) as f:
        doc = yaml.safe_load(f)
    on = doc.get("on", doc.get(True))
    n = len(on["workflow_dispatch"]["inputs"])
    assert n <= GITHUB_MAX_DISPATCH_INPUTS
    # Informational: prints the remaining headroom when run with -s.
    print(f"[input-cap] fusion-cpu-extras.yml: {n}/{GITHUB_MAX_DISPATCH_INPUTS} "
          f"({GITHUB_MAX_DISPATCH_INPUTS - n} slot(s) free)")
