"""GitHub caps `workflow_dispatch` at 10 inputs, and going over is SILENT.

★★ THE MOST EXPENSIVE HOUR OF 2026-07-30. Adding an 11th input (`on_demand`) to the ternary lane did not
fail, did not warn, and did not appear anywhere in the run's UI. What it did was make the dispatched
inputs arrive EMPTY: a launch explicitly dispatched with `-f on_demand=1 -f min_ns_per_h=33` ran with

    TVAST_MIN_NS_PER_H:
    TVAST_ON_DEMAND:

and rented an interruptible RTX 4090 — exactly the tier the dispatch existed to avoid. Every placement
decision made in that window was silently discarded: the card floor, the bid escalation, and the
uninterruptible tier all looked correct in the logs that CHOSE them and none of them reached the launcher.
The visible symptom was "the escalation fired and then the cheap host appeared anyway", which reads as a
race and sent an hour of diagnosis to the wrong place.

A cap that is enforced by silence has to be enforced by a test instead.
"""
from pathlib import Path

import pytest
import yaml

# The documented limit. Not a style preference: exceeding it discards input VALUES at dispatch time.
MAX_DISPATCH_INPUTS = 10

WORKFLOWS = sorted((Path(__file__).resolve().parents[3] / ".github/workflows").glob("*.yml"))


def _dispatch_inputs(path):
    d = yaml.safe_load(path.read_text())
    # PyYAML parses the bare key `on:` as the boolean True, which is why this is not `d["on"]`.
    on = d.get(True, d.get("on")) if isinstance(d, dict) else None
    if not isinstance(on, dict):
        return None
    wd = on.get("workflow_dispatch")
    if not isinstance(wd, dict):
        return None
    return wd.get("inputs") or {}


# ⚠ PRE-EXISTING DEBT, MEASURED 2026-07-30 AND FROZEN HERE — not an exemption, a register.
# These workflows were already over the cap before the cap was understood, so every one of them silently
# discards dispatched inputs today. They are recorded rather than quietly skipped because the failure mode
# is invisible at runtime: a `-f` flag on any of them is accepted, ignored, and the job runs on defaults.
# The number is pinned so the debt can shrink but not grow, and so a lane joining this list is a RED build
# rather than a discovery made hours into an incident.
# Fix one by moving its rarely-changed knobs to repository `vars.` entries, as gpu-ternary-fep-vast.yml did.
KNOWN_OVER_CAP = {
    "fep-status-aws.yml": 13, "fusion-cpu-extras.yml": 25, "generation-matched-null-aws.yml": 16,
    "gpu-8xtt-seed-md-aws.yml": 11, "gpu-abfe-aws.yml": 21, "gpu-denovo-dock-aws.yml": 12,
    "gpu-fep-aws.yml": 18, "gpu-rbfe-aws.yml": 20, "gpu-release-aws.yml": 11,
    "gpu-repurpose-dock-aws.yml": 11, "gpu-ternary-aws.yml": 11, "gpu-ternary-fep-aws.yml": 12,
    "gpu-ternary-fep-gcp.yml": 25, "mmgbsa-aws.yml": 12, "slow-cv-aws.yml": 12,
}


@pytest.mark.parametrize("wf", WORKFLOWS, ids=[w.name for w in WORKFLOWS])
def test_no_workflow_exceeds_the_dispatch_input_cap(wf):
    ins = _dispatch_inputs(wf)
    if ins is None:
        pytest.skip(f"{wf.name} has no workflow_dispatch inputs")
    if wf.name in KNOWN_OVER_CAP:
        # The debt may shrink, never grow. A lane that gains an input while already over the cap is
        # actively losing a NEW control, which is the incident this file exists to prevent repeating.
        assert len(ins) <= KNOWN_OVER_CAP[wf.name], (
            f"{wf.name} grew from {KNOWN_OVER_CAP[wf.name]} to {len(ins)} dispatch inputs while ALREADY "
            f"over GitHub's cap of {MAX_DISPATCH_INPUTS} — the new input will silently arrive empty.")
        return
    assert len(ins) <= MAX_DISPATCH_INPUTS, (
        f"{wf.name} declares {len(ins)} workflow_dispatch inputs, over GitHub's cap of "
        f"{MAX_DISPATCH_INPUTS}: {', '.join(ins)}. This does not fail at dispatch — it silently delivers "
        f"EMPTY values, so every -f flag is discarded and the job runs on defaults. Remove or consolidate "
        f"an input; a repository `vars.` entry is the usual home for a rarely-changed knob.")


def test_the_ternary_lane_still_carries_the_inputs_placement_depends_on():
    """Freeing a slot must not be paid for out of the placement controls — those are the ones whose
    silent loss rented the wrong tier."""
    wf = Path(__file__).resolve().parents[3] / ".github/workflows/gpu-ternary-fep-vast.yml"
    ins = _dispatch_inputs(wf)
    for k in ("task", "min_ns_per_h", "on_demand", "bid_floor_mult", "leg_only"):
        assert k in ins, f"{k} is load-bearing for placement and must stay a dispatch input"


def test_the_ternary_lane_is_AT_the_cap_so_a_new_knob_must_not_become_an_input():
    """★★ THE CAP IS NOT SLACK — THIS LANE HAS NONE (2026-07-30).

    It sits at exactly `MAX_DISPATCH_INPUTS`, so the next feature that wants a knob has three honest
    options and only three: fold it into an existing input, route it through an env var / repository
    variable, or delete an input first. It does NOT have the option of adding one — the 11th does not fail,
    it empties every value silently, which is the incident at the top of this file.

    Pinned rather than left to the generic assertion above because the generic one passes just as happily
    at 3 inputs, and it is the *absence of headroom* that a future author needs told.
    """
    wf = Path(__file__).resolve().parents[3] / ".github/workflows/gpu-ternary-fep-vast.yml"
    ins = _dispatch_inputs(wf)
    assert len(ins) == MAX_DISPATCH_INPUTS, (
        f"gpu-ternary-fep-vast.yml now declares {len(ins)} dispatch inputs, not {MAX_DISPATCH_INPUTS}: "
        f"{sorted(ins)}. If this GREW, every -f flag on this lane is now silently empty. If it SHRANK, "
        f"good — lower the number here in the same commit and say which knob moved and where to.")


def test_the_converge_mode_did_not_buy_itself_a_dispatch_input():
    """The pose/convergence diagnostic needed to be pointed at a mode other than RUNG 2b's `edge`. The
    obvious fix — a `converge_mode` input — would have been the 11th on a lane already at the cap, i.e. it
    would have silently emptied `min_ns_per_h`, `on_demand` and the rest at the same moment.

    It rides on the existing `task` input instead (`ternary_vast_launch.CONVERGE_TASK_MODES`), with
    `TVAST_CONVERGE_MODE` as the env-var escape hatch in the lane's own `TVAST_*` idiom. This asserts the
    shape stayed that way, because "just add an input" is the reflex this file exists to interrupt.
    """
    wf = Path(__file__).resolve().parents[3] / ".github/workflows/gpu-ternary-fep-vast.yml"
    ins = _dispatch_inputs(wf)
    strays = [k for k in ins if "converge" in k.lower() or k.lower() in ("mode", "fep_mode")]
    assert not strays, (
        f"{strays} became dispatch input(s) on a lane already at GitHub's cap of {MAX_DISPATCH_INPUTS} — "
        f"the converge mode belongs on the `task` input (CONVERGE_TASK_MODES) or in TVAST_CONVERGE_MODE.")
    text = wf.read_text()
    assert "TVAST_CONVERGE_MODE" in text, "the env-var route the fix depends on is gone"
    # the task input is a choice list, so the converge tasks must be dispatchable from it
    opts = (ins.get("task") or {}).get("options") or []
    assert "converge" in opts and "triangle-converge" in opts, (
        f"both converge tasks must stay dispatchable from the `task` input; options are {opts}")
