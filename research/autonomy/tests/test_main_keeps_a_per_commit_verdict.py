#!/usr/bin/env python3
"""A commit on `main` must be able to get its own CI verdict (AUT-PD-130).

⛔⛔ THE OUTAGE THIS SUITE WAS WRITTEN AGAINST, MEASURED 2026-08-28. The nine most recent completed
`tests` runs on `main` were ALL `cancelled`, each within 1-3 s of the next run on main being
created. `tests.yml` is what CLAUDE.md §6 names as *the authority* for the two large suites — the
ones preflight deliberately does NOT run, on the stated grounds that "CI runs both on push and it
is the authority" — so while this held, NOTHING ran them and the trunk went over twenty minutes
with no verdict at all.

⭐ THE OBSERVATION THAT NAMES THE CAUSE, AND IT REFUTES THE OBVIOUS GUESS. Run 33207278897 on
86098c2 was `pending`, not running, when it was cancelled. `cancel-in-progress` only ever cancels a
RUNNING run, so that flag was never the mechanism — and the workflow's `cancel-in-progress` already
evaluated to false on main. A concurrency group holds at most ONE running and ONE pending run, and
a third arrival EVICTS THE PENDING ONE whatever the flag says. Every push to main shared one
ref-keyed group, and this loop pushes every 2-4 minutes against a ~17-minute suite.

⛔ SO THE FIX IS TO THE GROUP AND THIS SUITE GUARDS THE GROUP. Asserting `cancel-in-progress` is
false on main would have passed throughout the outage — it was already false. That is why test 2
below is written against the group expression and not against the flag.

★ WHY THIS IS WORTH A GUARD AT ALL: the failure is SILENT and self-concealing. A cancelled run is
not red, so nothing alarms; `gates_verdict.py` correctly reports `_no_verdict` (its own line 96:
"`cancelled` and `skipped` are NOT verdicts. A cancelled run says the trunk was never tested"), and
health.py's `gates_green` then reads NO-GATE-VERDICT — which it had, for 47.2 h, while every cycle
read that board before starting.

⚠ WHAT THIS SUITE CANNOT SEE. It reads the workflow file, not GitHub. It cannot tell whether runs
are actually completing — only that the configuration does not force them to evict one another.
The live half is `gates_verdict.py`, and an absent reading there is not a reading of absence.
"""

from __future__ import annotations

import os
import re

import pytest
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORKFLOW = os.path.join(REPO, ".github", "workflows", "tests.yml")


@pytest.fixture(scope="module")
def wf():
    with open(WORKFLOW) as fh:
        return yaml.safe_load(fh)


# --- 1. positive control -------------------------------------------------------------------------

def test_the_workflow_is_readable_and_declares_concurrency(wf):
    """If the parse silently returned nothing, every other test here would pass vacuously."""
    assert isinstance(wf, dict)
    assert isinstance(wf.get("concurrency"), dict), "no concurrency block to guard"
    assert "group" in wf["concurrency"]


# --- 2. the real assertion: main runs must not share a group --------------------------------------

def test_a_run_on_main_gets_a_group_of_its_own(wf):
    """⛔ THE REGRESSION. Two commits on main sharing one group means the second evicts the first.

    The group expression must make a main run's group unique per run. `github.run_id` is the only
    value available at concurrency-evaluation time that is unique per run; `github.sha` would be
    unique per COMMIT, which is also acceptable — a re-run of one commit may legitimately supersede
    itself. Either satisfies this; a group keyed only on `github.ref` does not.
    """
    group = str(wf["concurrency"]["group"])
    assert "github.ref" in group or "head_ref" in group, (
        "the group no longer varies by ref at all — feature branches would now collapse together")
    assert re.search(r"github\.(run_id|sha)", group), (
        "a run on `main` shares its concurrency group with every other run on `main`, so a third "
        "push evicts the pending one and the trunk gets no verdict. Key main's group on "
        f"github.run_id (or github.sha). Group is: {group}")
    assert "refs/heads/main" in group or "default_branch" in group, (
        "the uniquifier is not conditioned on main, so feature branches lose their collapsing "
        f"behaviour too. Group is: {group}")


# --- 3. the branch saving that motivated the block must survive -----------------------------------

def test_feature_branches_still_collapse_to_the_tip(wf):
    """⚠ THE FIX MUST NOT BUY main's VERDICT BY SPENDING EVERY BRANCH'S RUNNER TIME.

    The block exists because one feature branch once had 12 runs in flight at once, fourteen of
    fifteen obsolete the moment the next commit landed.
    """
    cip = str(wf["concurrency"].get("cancel-in-progress"))
    assert cip != "False" and cip != "false", (
        "cancel-in-progress is off for every ref — feature branches no longer collapse")
    assert "refs/heads/main" in cip or cip == "True" or cip == "true"
