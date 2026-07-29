#!/usr/bin/env python3
"""A lane that runs from a long-lived branch drifts, and the drift is a DATA-LOSS bug.

Measured 2026-07-29 (CLAUDE.md §7). `step1-fanout-autoscale.yml` checked out `claude/max-effort-2dq11l` and
wrote its map there, so `main` reported the fan-out at 1 of 19 edges / $22.62 while the branch — where the lane
actually ran — held 14 of 19 / $68.98 / 197 rentals. Three harms followed: the manuscript understated the work
by 13 computed edges; safety modules merged to `main` were inert on the lane; and re-pointing the lane would
have shown 13 finished edges as unrun and re-bought them (~$46) on a fleet that rents unattended.

These pin the remedy so it cannot quietly regrow.
"""
import os
import pathlib
import re

WF = pathlib.Path(__file__).resolve().parents[3] / ".github" / "workflows"
OLD = "claude/max-effort-2dq11l"


def _config_lines(path):
    """Lines that DEFAULT or FALL BACK to a branch — the only two shapes that can point a lane somewhere.

    Deliberately NOT every mention. Comments discuss the old branch at length (these files carry the incident
    notes), and `on.push.branches:` lists it on purpose — a trigger list only WIDENS what fires and cannot
    send a lane's code or checkpoints anywhere. Asserting on raw mentions failed on exactly that, which is the
    kind of false positive that gets a guard deleted.
    """
    out = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if line.strip().startswith("#"):
            continue
        if re.search(r"default:\s*['\"]", line) or "fleet_branch ||" in line or "FLEET_BRANCH:" in line:
            out.append((i, line))
    return out


def test_no_workflow_defaults_a_lane_onto_the_old_fleet_branch():
    bad = []
    for p in sorted(WF.glob("*.yml")):
        for i, line in _config_lines(p):
            # `-4fs`, `-paralogue`, `-e3` are distinct sibling branches, not the fleet branch.
            if re.search(re.escape(OLD) + r"(?![-\w])", line):
                bad.append(f"{p.name}:{i}: {line.strip()}")
    assert not bad, ("these still DEFAULT a lane onto the old fleet branch:\n  " + "\n  ".join(bad))


def test_every_fleet_branch_input_defaults_to_main():
    for p in sorted(WF.glob("*.yml")):
        text = p.read_text()
        if "fleet_branch:" not in text:
            continue
        for i, line in _config_lines(p):
            if "fleet_branch ||" in line:
                assert "'main'" in line, f"{p.name}:{i} falls back to something other than main: {line.strip()}"


def test_the_harvest_trigger_did_not_lose_main():
    # The lane now pushes to main; a trigger listening only to the old branch would stop firing.
    t = (WF / "replicate-standard-harvest.yml").read_text()
    m = re.search(r"branches:\s*\[([^\]]*)\]", t)
    assert m and "main" in m.group(1), "the harvest no longer fires on the branch the lane writes to"


def test_the_ported_map_is_the_lane_s_real_state_not_the_stale_one():
    # The specific artifact whose staleness caused the incident. If a future merge resurrects the 1-edge
    # copy, this fails loudly rather than silently understating the science again.
    import json
    p = pathlib.Path(__file__).resolve().parents[1] / "step1-fanout-map.json"
    d = json.loads(p.read_text())
    assert d["n_complete"] >= 14, (
        "step1-fanout-map.json has regressed to a stale copy (n_complete=%s). The lane's real state had 14 of "
        "19 edges; a lower number here means main is summing the wrong branch's artifact again."
        % d["n_complete"])
    assert len(d.get("realised_rentals") or []) >= 197
