"""A lane that publishes its own rows must ALSO re-merge the all-lane board, in the same step.

★★ WHY THIS EXISTS (measured 2026-08-01, 2:44 PM ET). `inflight-board-all.md` is a CACHE: it is derived in
full from the per-lane fragments, and it is regenerated only by whoever calls `inflight_board --write`.
Two of the four lanes did that; the GCP lane called `ib.write_fragment`, which writes the fragment and
nothing else, and the ternary lane's collect wrote `inflight-board.md` and stopped.

So a lane could be in perfect health and still render as broken. Verbatim, that afternoon:

  * `inflight-board.d/gcp-s1f-rep.json` — 1.8 min old, carrying `eta_epoch` → **4:36 AM Aug 2**
  * the same lane's section of `inflight-board-all.md` — **"16 min ago, STALE (> 15 min)"**, ETA blank

Nothing was wrong with the lane. The merge had last run when a DIFFERENT lane happened to tick, and
`stale_rows` had then done exactly its job: refuse to project a completion time from a reading nobody had
re-taken. Both cells were correct about a stale input that only the plumbing had made stale.

⚠ THE DAMAGE IS THE ALARM, NOT THE SIXTEEN MINUTES. `STALE` is this board's alarm for *a lane stopped
reporting while it was billing* — a real condition here, because CLAUDE.md §6 records that this repo's
schedules are throttled and that an agent has been dispatching the ticks by hand. A lane that raises that
alarm about ITSELF, from full health, on every tick, is that alarm being trained into background noise. It
is the same failure the board's own design notes keep naming: **a healthy state and a broken state that
render alike.**

WHAT IS CHECKED, and why it is the workflow rather than the module. `publish` vs `write_fragment` is the
right call in Python, but it is not the invariant: the ternary lane deliberately uses `write_fragment`,
because the file the merge transcludes for it (`inflight-board.md`) is written by the WORKFLOW from the
collect's stdout, after the process has exited — merging inside the collect would merge the previous
tick's text. So the property that actually holds for all four lanes is at the workflow level: **the step
that commits a lane's board file also regenerates and commits the merged board.**
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

MODALITIES = Path(__file__).resolve().parents[1]
WORKFLOWS = MODALITIES.parents[1] / ".github" / "workflows"
MERGED = "research/modalities/inflight-board-all.md"


def _lanes():
    import sys
    sys.path.insert(0, str(MODALITIES))
    import inflight_board as ifb
    return ifb


def _board_path(ifb, lane: str) -> str:
    """The file this lane's workflow commits for it — its fragment, or the ternary lane's own board file."""
    if lane == ifb.TERNARY:
        return f"research/modalities/{ifb.TERNARY_BOARD_MD}"
    return f"research/modalities/{ifb.FRAGMENT_DIR}/{lane}.json"


#: ⚠ FOUR STAGING IDIOMS, AND NOT ONE LANE USES A BARE LITERAL. This resolver is the whole guard: a
#: `git add` it cannot follow reads as "this lane stages nothing", which is a FALSE POSITIVE — and a guard
#: that cries wolf on a healthy lane gets ignored exactly like the STALE banner this file exists to protect.
#: Each idiom below is in live use and each one broke this resolver once during development:
#:
#:   VAR=path            … git add "$VAR"                 gpu-fanout-rep-gcp, gpu-ternary-fep-vast
#:   for f in a b c; do  … git add -f "$f"; done           step1-fanout-autoscale
#:   for p in a b c; do arr+=("$p"); done … git add -A "${arr[@]}"    selectivity-control-vast
#:   git add path                                          (a literal, for completeness)
_FOR_LOOP = re.compile(r"for\s+(\w+)\s+in\s+(.*?)\bdo\b(.*?)\bdone\b", re.S)
_ARRAY_APPEND = re.compile(r"(\w+)\+=\(\s*\"?\$\{?(\w+)\}?\"?\s*\)")
_GIT_ADD = re.compile(r"git add\s+((?:-\w+\s+)*)(\S+)")


def _staged_paths(text: str) -> set[str]:
    """Every path a workflow actually `git add`s, through any idiom the lanes use."""
    var: dict[str, set[str]] = {}
    for m in re.finditer(r"^\s*([A-Z_][A-Z0-9_]*)=(\S*inflight-board\S*?)\s*$", text, re.M):
        var.setdefault(m.group(1), set()).add(m.group(2))
    for m in _FOR_LOOP.finditer(text):
        loop_var, items, body = m.group(1), m.group(2), m.group(3)
        # `; do` fuses onto the LAST item (`…/selcal-cofold.json; do`), so the final path in every list
        # would be the one this resolver could not see — and the final path is where a board file sits.
        paths = {t.strip('"\';') for t in items.replace("\\\n", " ").split()
                 if t.strip('"\';').startswith("research/")}
        if not paths:
            continue
        var.setdefault(loop_var, set()).update(paths)
        # …and any array the loop appends the loop variable into carries the same set.
        for a in _ARRAY_APPEND.finditer(body):
            if a.group(2) == loop_var:
                var.setdefault(a.group(1), set()).update(paths)
    out = set()
    for m in _GIT_ADD.finditer(text):
        # `;` and `&&` ride along in `git add -f "$f"; done`, and `[@]` in `"${paths[@]}"`; an unresolvable
        # token reads exactly like "this lane stages nothing".
        tok = m.group(2).strip('"\';&|').strip('"\'')
        if tok.startswith("$"):
            out |= var.get(tok.lstrip("${").rstrip("}").removesuffix("[@]"), {tok})
        else:
            out.add(tok)
    return out


def _publishers(ifb, lane: str) -> list[Path]:
    """Workflows that COMMIT this lane's board file — not merely mention it in a comment."""
    want = _board_path(ifb, lane)
    return [p for p in sorted(WORKFLOWS.glob("*.yml")) if want in _staged_paths(p.read_text())]


@pytest.mark.parametrize("lane", [l[0] for l in _lanes().LANES])
def test_every_lane_has_a_workflow_that_publishes_it(lane):
    """A lane nobody commits is a lane that reads STALE forever — the same defect as a registered lane with
    no publisher (`test_lane_registry_contract.py`), arriving through CI instead of through the registry."""
    ifb = _lanes()
    pubs = _publishers(ifb, lane)
    assert pubs, (
        f"no workflow stages {_board_path(ifb, lane)}, so lane {lane!r} can never update on `main`. Its "
        f"section will render `As of: NEVER` or age past {ifb.stale_after_min():g} min and stay there.")


@pytest.mark.parametrize("lane", [l[0] for l in _lanes().LANES])
def test_publishing_a_lane_also_re_merges_the_all_lane_board(lane):
    """The invariant this file exists for. Commit the lane's rows, re-merge the board, in the same run."""
    ifb = _lanes()
    for wf in _publishers(ifb, lane):
        text = wf.read_text()
        assert "inflight_board.py --write" in text, (
            f"{wf.name} commits {_board_path(ifb, lane)} but never regenerates {MERGED}. The merged board "
            f"is a CACHE — it will carry this lane's PREVIOUS rows until some other lane happens to tick, "
            f"and this lane's section will then render `STALE (> {ifb.stale_after_min():g} min)` with its "
            f"ETA dropped while the lane is in perfect health. Measured on the GCP lane, 2026-08-01: "
            f"fragment 1.8 min old with an ETA of 4:36 AM Aug 2, board saying 16 min / STALE / no ETA.")
        assert MERGED in _staged_paths(text), (
            f"{wf.name} regenerates {MERGED} but does not `git add` it, so the fresh merge dies with the "
            f"runner and `main` keeps the stale one.")


def test_the_detector_actually_detects():
    """⚠ A GUARD THAT CANNOT GO RED IS WORSE THAN NO GUARD — it reports coverage it does not have.

    This repo has already had a tripwire sit green through the very fix it claimed to police, and the
    resolver here is three shell idioms deep (`VAR=path`, `for f in …; do git add "$f"`, and a literal),
    each of which has already silently resolved to nothing once during development. So the defect is
    reconstructed from a real workflow and the detector is required to see it.
    """
    ifb = _lanes()
    live = _publishers(ifb, ifb.GCP_S1F_REP)
    assert live, "the GCP lane's publisher moved; this self-test has lost its subject"
    text = live[0].read_text()
    assert MERGED in _staged_paths(text)                      # the fixed state
    broken = text.replace(f'git add {MERGED} || true', "")    # the state measured on 2026-08-01
    assert MERGED not in _staged_paths(broken), \
        "removing the stage line must make the lane read as un-merged, or this guard proves nothing"
    # …and the same for the loop idiom, which is how the step-1 lane stages its board.
    s1 = _publishers(ifb, ifb.FANOUT)
    assert s1, "the step-1 lane's publisher moved"
    assert MERGED in _staged_paths(s1[0].read_text())
    assert MERGED not in _staged_paths(s1[0].read_text().replace(f"{MERGED} \\\n", ""))
    # …and the ARRAY idiom (`arr+=("$p")` … `git add -A "${arr[@]}"`), which broke this resolver twice:
    # once by not following the array at all, and once because `; do` fuses onto the LAST item of the list
    # — and the last item is exactly where a board path sits. Both failures rendered as "this lane stages
    # nothing", i.e. a false alarm on a healthy lane.
    sc = _publishers(ifb, "selcal-cofold")
    assert sc, "the selcal lane's publisher moved"
    text = sc[0].read_text()
    assert "inflight-board.d/selcal-cofold.json; do" in text, \
        "this self-test's subject is the trailing-`; do` item; the list was reformatted"
    assert "research/modalities/inflight-board.d/selcal-cofold.json" in _staged_paths(text)
    assert MERGED not in _staged_paths(text.replace(f"git add {MERGED} 2>/dev/null || true", ""))


@pytest.mark.parametrize("lane", [l[0] for l in _lanes().LANES])
def test_the_merge_runs_after_the_reset_that_fetches_the_other_lanes_fragments(lane):
    """⚠ ORDERING IS A SAFETY PROPERTY HERE, NOT STYLE.

    The merged board is derived from EVERY lane's fragment. Both live publish steps rewrite onto upstream
    (`reset --hard`) so that a conflict against a sibling tick is unrepresentable rather than handled — and
    that reset is also what puts the OTHER three lanes' freshest fragments in the tree. Merging before it
    would read this checkout's copies of those three, which are as old as the checkout, and stamp their
    staleness onto upstream: a fix for one lane's false STALE that manufactures three lanes' real one.
    """
    ifb = _lanes()
    for wf in _publishers(ifb, lane):
        code = "\n".join(l for l in wf.read_text().splitlines() if not l.lstrip().startswith("#"))
        if "reset -q --hard" not in code and "reset --hard" not in code:
            continue                      # no rewrite-onto-upstream in this workflow; nothing to order against
        merges = [m.start() for m in re.finditer(r"inflight_board\.py --write", code)]
        resets = [m.start() for m in re.finditer(r"git reset -?q? ?--hard", code)]
        assert merges, f"{wf.name} lost its re-merge"
        assert any(m > min(resets) for m in merges), (
            f"{wf.name} regenerates {MERGED} only BEFORE its `reset --hard`, so the merge it publishes was "
            f"built from this checkout's copies of the other lanes' fragments. That stamps their staleness "
            f"onto upstream and rolls their rows back.")
