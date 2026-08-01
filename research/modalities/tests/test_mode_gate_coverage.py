"""Every mode this lane can LAUNCH must have a re-placement decision — a gate, or a recorded reason not to.

WHAT THIS PINS. On 2026-07-31 `5aks_d0_to_d__ternary_nr4a3_r0` lost its host to a capacity refusal on machine
145841. The lane destroyed the box, stopped billing and kept the checkpoint at `production/840`, then printed
"this pass dispatches the gate to re-place it" and dispatched nothing: the re-placement map was a hardcoded
shell `case` in the collect job carrying `triangle|triangle_smoke` and `edge_reps` only, and `5aks` — the mode
actually running that day — fell through to a `::warning::`. The supervisor's tick loop had the same gap from
the other side, hardcoding `task=market-gate` and `task=triangle-gate`. The ledger's 7:39 / 7:47 / 7:55 AM ET
rows show two gate evaluations each and no 5aks one.

A mode that can be launched but not re-placed is a TRAP: it works until its first preemption and then quietly
stops being a lane, while every readout stays green. Two lists that must be edited in lockstep with `MODES`,
and are checked against it by nothing, is the same shape as NR-V04's AUTHORIZED_STAGES prose-vs-code split.
So the map lives beside `MODES` and this file is the thing that makes adding a mode without a decision fail
the build.
"""
import os
import re
import sys

import pytest
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_vast_launch as tv  # noqa: E402

# Same resolution as tests/test_workflows_parse.py — tests/ -> modalities/ -> research/ -> repo root. Getting
# this wrong SKIPS every workflow assertion and the file passes green while checking nothing, which is the
# failure mode this whole test file is about.
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
WF_DIR = os.path.join(ROOT, ".github", "workflows")
LANE = os.path.join(WF_DIR, "gpu-ternary-fep-vast.yml")
SUPERVISOR = os.path.join(WF_DIR, "step1-fanout-supervisor.yml")


def _lane_text():
    if not os.path.exists(LANE):
        pytest.skip("gpu-ternary-fep-vast.yml absent")
    return open(LANE).read()


def _launchable_tasks():
    """The `task` values the launch job will actually rent for — read off its own `if:`, so this cannot
    drift from the workflow the way the two hardcoded lists did."""
    doc = yaml.safe_load(_lane_text())
    cond = doc["jobs"]["launch"]["if"]
    return sorted(set(re.findall(r"task == '([a-z0-9-]+)'", cond)))


def _mode_of(task):
    return task.replace("-", "_")


# ---------------------------------------------------------------------------------------------------------
# the core invariant
# ---------------------------------------------------------------------------------------------------------

def test_every_launchable_mode_has_a_replacement_decision():
    """The trap, closed. A mode must be in MODE_GATE_TASK (it has a gate) or NO_AUTOMATIC_REPLACEMENT (it
    deliberately has none, with the reason on the record). Being in neither is the 2026-07-31 defect."""
    undecided = []
    for task in _launchable_tasks():
        mode = _mode_of(task)
        try:
            tv.gate_task_for(mode)
        except KeyError:
            undecided.append(mode)
    assert not undecided, (
        f"these modes can be LAUNCHED but have no re-placement decision: {undecided}. A leg of such a mode "
        f"that loses its host stays stranded with an intact checkpoint and nothing looking for a new one — "
        f"add each to MODE_GATE_TASK (with a gate that prices THAT mode) or to NO_AUTOMATIC_REPLACEMENT "
        f"(with the reason).")


def test_5aks_specifically_has_a_gate():
    """The regression that cost a stranded leg. Named on its own so a future refactor cannot lose it inside
    the general rule above."""
    assert tv.gate_task_for("5aks") == "5aks-gate"


def test_a_mode_unknown_to_both_maps_raises_rather_than_returning_none():
    """None means "decided: no re-placement" and must never double as "never thought about". If an unknown
    mode returned None, `collect` would print the benign by-design notice for a real gap."""
    with pytest.raises(KeyError):
        tv.gate_task_for("a_mode_nobody_declared")


# ---------------------------------------------------------------------------------------------------------
# a map entry is a claim about the workflow — check it against the workflow
# ---------------------------------------------------------------------------------------------------------

def test_every_mapped_gate_task_is_dispatchable():
    """A map entry naming a task the workflow does not accept would silently downgrade to the free `test` —
    a green run that re-places nothing. Checks both the dispatch options and the resolve allowlist."""
    text = _lane_text()
    doc = yaml.safe_load(text)
    node = next((doc[k] for k in (True, "on", "On", "ON") if k in doc and isinstance(doc[k], dict)), None)
    options = ((node or {}).get("workflow_dispatch") or {}).get("inputs", {}).get("task", {}).get("options")
    assert options, "the task input lost its options list"
    m = re.search(r"case \"\$\{TASK:-test\}\" in\s*\n\s*([^)]+)\)", text)
    assert m, "could not find the task `case` allowlist"
    allowed = {t.strip() for t in m.group(1).split("|") if t.strip()}

    for mode, task in sorted(tv.MODE_GATE_TASK.items()):
        assert task in options, f"{mode} -> {task}, which is not a dispatchable option"
        assert task in allowed, (
            f"{mode} -> {task}, which is missing from the resolve allowlist and would fall back to `test`")


def test_every_mapped_gate_task_has_a_job_that_runs_it():
    """A task nothing gates on is a dispatch into an empty run."""
    doc = yaml.safe_load(_lane_text())
    guards = " ".join(str(j.get("if", "")) for j in doc["jobs"].values())
    for mode, task in sorted(tv.MODE_GATE_TASK.items()):
        assert f"'{task}'" in guards, f"{mode} -> {task}, but no job's `if:` selects that task"


def test_each_gate_job_prices_the_mode_it_claims():
    """★ THE CLAIM A MAP ENTRY ACTUALLY MAKES. Pointing a mode at a gate that runs `--mode` on a DIFFERENT
    unit set produces a green tick that re-places nothing — the bug being fixed, wearing a map entry as a
    disguise. So each gate task's job must invoke the launcher with the mode(s) that map to it."""
    text = _lane_text()
    by_task = {}
    for mode, task in tv.MODE_GATE_TASK.items():
        by_task.setdefault(task, set()).add(mode)
    doc = yaml.safe_load(text)
    for task, modes in sorted(by_task.items()):
        job = next((j for j in doc["jobs"].values() if f"'{task}'" in str(j.get("if", ""))), None)
        assert job, f"no job for {task}"
        body = yaml.safe_dump(job)
        priced = set(re.findall(r"--mode (\w+) --gate-for-mode", body))
        assert priced, f"{task}'s job never calls --gate-for-mode"
        # A smoke is allowed to ride its parent's gate (the established triangle_smoke idiom), so the
        # requirement is that the priced mode is one of the modes routed here, not all of them.
        assert priced & modes, (
            f"{task} prices {sorted(priced)} but the modes routed to it are {sorted(modes)} — a gate that "
            f"prices someone else's units cannot re-place these legs")


# ---------------------------------------------------------------------------------------------------------
# the supervisor is the other half: a gate nothing dispatches is a gate that never runs
# ---------------------------------------------------------------------------------------------------------

def test_the_supervisor_tick_dispatches_every_gate_task():
    """`collect`'s self-heal only fires when a unit is ALREADY seen hostless by a collect. The supervisor
    tick is what guarantees a gate is evaluated on a cadence at all — 5a-KS had a map entry in neither, and
    this half is why the 7:39/7:47/7:55 ticks could not have caught it either."""
    if not os.path.exists(SUPERVISOR):
        pytest.skip("step1-fanout-supervisor.yml absent")
    text = open(SUPERVISOR).read()
    for task in sorted(set(tv.MODE_GATE_TASK.values())):
        assert f"-f task={task}" in text, (
            f"the supervisor never dispatches `{task}`, so the modes routed to it are only ever re-placed "
            f"if some other path notices — which is exactly how 5a-KS was stranded.")


# ---------------------------------------------------------------------------------------------------------
# THE OTHER END OF A MODE'S LIFE: its reduction (added 2026-08-01)
# ---------------------------------------------------------------------------------------------------------
# A gate answers "who buys a new host when one dies". Nothing answered "who forms the number once the last
# leg lands", so a complete rung sat unreduced until a person dispatched `5aks-reduce` by hand. RUNG 5a-KS's
# S is a double difference over four legs that land ~20 h apart, the last of them overnight — the same
# lockstep-lists trap as the gate map, at the finishing end.

def test_every_launchable_mode_has_a_reduction_decision():
    undecided = []
    for task in _launchable_tasks():
        mode = _mode_of(task)
        try:
            tv.reduce_task_for(mode)
        except KeyError:
            undecided.append(mode)
    assert not undecided, (
        f"these modes can be LAUNCHED but have no reduction decision: {undecided}. Their last leg landing "
        f"would fire nothing — add each to MODE_REDUCE_TASK or to NO_AUTOMATIC_REDUCTION with the reason.")


def test_5aks_reduces_and_its_SMOKE_deliberately_does_not():
    """★ THE DANGEROUS HALF. A smoke leg writes a real `leg.json` with a real dG, so 'this mode is complete'
    is TRUE of `5aks_smoke` after its ONE leg — and the two unit ids differ only by a `_smoke` suffix. A
    completeness count that did not refuse it would emit a rung readout built from a dozen production
    iterations (CLAUDE.md §4b)."""
    assert tv.reduce_task_for("5aks") == "5aks-reduce"
    assert tv.reduce_task_for("5aks_smoke") is None
    assert "5aks_smoke" in tv.NO_AUTOMATIC_REDUCTION


def test_a_mode_unknown_to_both_reduction_maps_raises():
    with pytest.raises(KeyError):
        tv.reduce_task_for("a_mode_nobody_declared")


def test_every_mapped_reduce_task_is_dispatchable_and_has_a_job():
    """A reduce task the workflow does not accept downgrades to the free `test` — a green run that reduces
    nothing, which reads exactly like a rung that has been reduced."""
    text = _lane_text()
    doc = yaml.safe_load(text)
    node = next((doc[k] for k in (True, "on", "On", "ON") if k in doc and isinstance(doc[k], dict)), None)
    options = ((node or {}).get("workflow_dispatch") or {}).get("inputs", {}).get("task", {}).get("options")
    assert options, "the task input lost its options list"
    m = re.search(r"case \"\$\{TASK:-test\}\" in\s*\n\s*([^)]+)\)", text)
    allowed = {t.strip() for t in m.group(1).split("|") if t.strip()}
    guards = " ".join(str(j.get("if", "")) for j in doc["jobs"].values())
    for mode, task in sorted(tv.MODE_REDUCE_TASK.items()):
        assert task in options, f"{mode} -> {task}, which is not a dispatchable option"
        assert task in allowed, f"{mode} -> {task}, missing from the resolve allowlist — falls back to `test`"
        assert f"'{task}'" in guards, f"{mode} -> {task}, but no job's `if:` selects it"


def test_collect_actually_dispatches_the_completed_modes_reduction():
    """The map is inert unless something reads it. `collect` writes the marker; the workflow step reads it
    and dispatches — and LATCHES ONLY AFTER a successful dispatch, so a dispatch that never reached GitHub
    is retried instead of being marked done."""
    text = _lane_text()
    assert "/tmp/tvast-mode-complete.txt" in text, "nothing reads collect's mode-complete marker"
    assert "--latch-reduce-dispatched" in text
    step = text[text.index("Fire a mode's reduction"):]
    step = step[:step.index("- name: Summary LAST")]
    assert step.index("gh workflow run") < step.index("--latch-reduce-dispatched"), (
        "the latch must be written AFTER the dispatch succeeds — latching on intent swallows exactly the "
        "dispatch that failed")
