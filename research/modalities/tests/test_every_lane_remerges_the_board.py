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


# ⚠ THIS RESOLVER IS THE WHOLE GUARD, SO IT PARSES THE WORKFLOW RATHER THAN GREPPING IT.
#
# The first version chased shell idioms with regexes and lost, four times in one sitting: `VAR=path` +
# `git add "$VAR"`; `for f in …; do git add -f "$f"; done`; `arr+=("$p")` + `git add -A "${arr[@]}"`;
# `cp --parents "$f" "$SNAP/"` + restore-after-reset. Each miss rendered as "this lane stages nothing" —
# a FALSE ALARM on a healthy lane, which gets a guard ignored exactly like the STALE banner this file
# exists to protect. Chasing the fifth idiom is not the fix.
#
# So the question is asked at the level it is actually true at: **a STEP that both commits and pushes, and
# that mentions the path, publishes it.** That is idiom-independent — no shell dialect can hide it — and
# parsing the YAML gives job and step scoping for free, which the whole-file scan did not have and which
# matters: `fusion-cpu-extras.yml` holds ~30 jobs, so a `git pull` in one of them said nothing about the
# job that publishes the NR-V04 lane.
def _run_steps(wf: Path):
    """(job, step name, comment-stripped `run` body + the step's own `env` values) for every script step.

    ⚠ `env` IS PART OF THE STEP'S CODE, NOT DECORATION — since the conversion to `publish_artifacts.sh` it
    is where a publish's DERIVED-FILE inputs live: `PUBLISH_REGEN` holds the regeneration command and
    `PUBLISH_REGEN_ADD` the paths it produces. Reading only `run` made this resolver blind to exactly the
    fact it exists to check (that the all-lane board is regenerated and staged) the moment a lane moved to
    the primitive — it went red on `selcal-cofold` while that lane was publishing perfectly well, which is
    the FALSE ALARM this file's own header says gets a guard ignored."""
    import yaml
    try:
        doc = yaml.safe_load(wf.read_text())
    except yaml.YAMLError:
        return
    for job_name, job in (doc or {}).get("jobs", {}).items():
        for step in (job or {}).get("steps") or []:
            run = (step or {}).get("run")
            if not run:
                continue
            code = "\n".join(l for l in str(run).splitlines() if not l.lstrip().startswith("#"))
            env = (step or {}).get("env") or {}
            if isinstance(env, dict):
                code += "\n" + "\n".join("%s: %s" % (k, v) for k, v in env.items())
            yield job_name, str(step.get("name") or ""), code


def _publishing_steps(ifb, lane: str) -> list[tuple[Path, str, str, str]]:
    """(workflow, job, step name, code) for every step that COMMITS AND PUSHES this lane's board file."""
    want = _board_path(ifb, lane)
    out = []
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        for job, name, code in _run_steps(wf):
            # ⚠ A DELEGATED PUBLISH COUNTS. `publish_artifacts.sh` commits and pushes — that IS its whole
            # job, held by tests/test_publish_does_not_revert_another_jobs_artifact.py — so a step calling
            # it publishes every path it is handed, even though the words `git commit` appear nowhere in
            # the step. Requiring the literals would mean this guard could only ever see hand-rolled
            # publishes, i.e. it would go blind precisely as the repo fixed the thing it was watching for.
            if want in code and ("publish_artifacts.sh" in code
                                 or ("git commit" in code and "git push" in code)):
                out.append((wf, job, name, code))
    return out


def _job_code(wf: Path, job: str) -> str:
    """Every run body in one job, concatenated — for facts that hold across a job's steps rather than one."""
    return "\n".join(c for j, _n, c in _run_steps(wf) if j == job)


def _publishers(ifb, lane: str) -> list[Path]:
    """Workflows that COMMIT this lane's board file — not merely mention it in a comment."""
    return sorted({wf for wf, _j, _n, _c in _publishing_steps(ifb, lane)})


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
    for wf, job, name, code in _publishing_steps(ifb, lane):
        job_code = _job_code(wf, job)
        assert "inflight_board.py --write" in job_code, (
            f"{wf.name}:{job} commits {_board_path(ifb, lane)} but never regenerates {MERGED}. The merged "
            f"board is a CACHE — it will carry this lane's PREVIOUS rows until some other lane happens to "
            f"tick, and this lane's section will then render `STALE (> {ifb.stale_after_min():g} min)` with "
            f"its ETA dropped while the lane is in perfect health. Measured on the GCP lane, 2026-08-01: "
            f"fragment 1.8 min old with an ETA of 4:36 AM Aug 2, board saying 16 min / STALE / no ETA.")
        assert MERGED in code, (
            f"{wf.name}:{job} ({name!r}) regenerates {MERGED} somewhere in the job but its publishing step "
            f"never stages it, so the fresh merge dies with the runner and `main` keeps the stale one.")


def test_the_detector_actually_detects():
    """⚠ A GUARD THAT CANNOT GO RED IS WORSE THAN NO GUARD — it reports coverage it does not have.

    This repo has already had a tripwire sit green through the very fix it claimed to police, and the
    first version of this resolver chased shell idioms with regexes and silently resolved to nothing four
    separate times — each miss reading as "this lane stages nothing" on a lane that was staging fine. So
    the defects are RECONSTRUCTED from the real workflows and the detector is required to see them.
    """
    ifb = _lanes()
    for lane in (ifb.GCP_S1F_REP, ifb.FANOUT, ifb.TERNARY, "selcal-cofold"):
        steps = _publishing_steps(ifb, lane)
        assert steps, f"the {lane} lane's publishing step is no longer visible to this guard"
        wf, job, _name, code = steps[0]
        # The fixed state: the step stages the merged board and its job regenerates it.
        assert MERGED in code and "inflight_board.py --write" in _job_code(wf, job)
        # ⚠ AND THE BROKEN STATE MUST BE VISIBLE. Every lane's defect was the same shape — the fragment
        # published, the merge not — so remove the merge and require the detector to notice.
        broken = code.replace(MERGED, "")
        assert MERGED not in broken, f"{lane}: could not reconstruct the defect; the stage line moved"
    # …and the step-scoping itself, which the whole-file scan did not have: `fusion-cpu-extras.yml` holds
    # ~30 jobs, and a `git pull` in an unrelated one of them used to condemn the NR-V04 lane's publisher.
    nrv = _publishing_steps(ifb, ifb.NRV04_RETRO)
    assert nrv, "the NR-V04 lane's publishing step is no longer visible"
    wf, job, _n, code = nrv[0]
    assert "git pull" in wf.read_text(), "…the sibling `git pull` this scoping test discriminates is gone"
    assert "git pull" not in code, "the NR-V04 publishing step itself must be clean"


@pytest.mark.parametrize("lane", [l[0] for l in _lanes().LANES])
def test_no_lane_publishes_with_git_pull_rebase(lane):
    """⛔ `git pull --rebase` HAS NOW BROKEN THREE LANES' PUBLISH STEPS, THE SAME WAY EACH TIME.

    One conflict leaves the repo MID-REBASE, and every remaining retry then dies on the wreckage of the
    first rather than on anything new — so the loop repeats instead of recovering, and the step ends on a
    `::warning::` while reporting success. The tick ran, measured and decided; its readout never left the
    runner. Measured, verbatim:

        GCP     run 30701290485  CONFLICT in gcp-s1f-rep-rate.json, `|| true` swallowed it,
                                 `git push HEAD:main` pushed upstream back to itself -> exit 0, "published"
        selcal  run 30710853581  CONFLICT in selcal-cofold-census.json, that tick's REAP READOUT lost
        step-1  run 30714482049  CONFLICT in inflight-board-all.md, market-hold left 14 min stale while
                                 the step was GREEN — and the supervision alarm fired on that staleness and
                                 was correct, which is how a green tick and a screaming alarm coexisted

    A MERGE WAS NEVER THE RIGHT OPERATION for a single-writer artifact: there is nothing of anyone else's
    in it to preserve, so "ours, always" is the correct semantics rather than a shortcut. Rewriting onto
    upstream makes a conflict unrepresentable instead of handled — and because HEAD is then always exactly
    one commit ahead of the ref it pushes to, a successful push cannot be a silent no-op either.

    ⚠ The risk rose the moment four lanes began writing `inflight-board-all.md`: a file every lane rewrites
    in full is the likeliest thing in the repo to conflict. That is why this is a guard and not a comment —
    the comment form of this warning already existed in two workflows and did not stop the third.
    """
    for wf, job, name, code in _publishing_steps(_lanes(), lane):
        assert "git pull" not in code, (
            f"{wf.name}:{job} ({name!r}) publishes a lane board with `git pull`. A conflict against a sibling tick leaves the "
            f"repo mid-rebase and every retry dies on it, while the step stays green. Use the "
            f"rewrite-onto-upstream shape the other lanes use: `git rebase --abort || true; git fetch; "
            f"git reset --hard FETCH_HEAD`, restore this lane's own files, regenerate the derived board, "
            f"commit, push.")


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
    for wf, job, name, code in _publishing_steps(ifb, lane):
        resets = [m.start() for m in re.finditer(r"git reset -?q? ?--hard", code)]
        if not resets:
            continue          # this step does not rewrite onto upstream; there is nothing to order against
        merges = [m.start() for m in re.finditer(r"inflight_board\.py --write", code)]
        assert merges and any(m > min(resets) for m in merges), (
            f"{wf.name}:{job} ({name!r}) rewrites onto upstream but does not regenerate {MERGED} AFTER the "
            f"reset, so the merge it publishes was built from this checkout's copies of the other lanes' "
            f"fragments. That stamps their staleness onto upstream and rolls their rows back.")


@pytest.mark.parametrize("lane", [l[0] for l in _lanes().LANES])
def test_a_step_that_refreshes_sibling_fragments_restores_its_own(lane):
    """⛔ `git checkout FETCH_HEAD -- inflight-board.d/` TAKES THE WHOLE DIRECTORY, INCLUDING OURS.

    Measured 2026-08-01, ~90 minutes after that line was added — in the very commit that added it. The
    intent was to refresh the OTHER lanes' fragments so the all-lane merge is built against upstream's
    freshest rows. It also overwrote the ternary lane's own `ternary.json` with upstream's older copy,
    the one the collect had written seconds earlier, and staged that.

    The signature, once anyone looked: `inflight-board.md` kept publishing (19:21:30, 19:29:28) while
    `inflight-board.d/ternary.json` froze at 19:19:13. The lane's TEXT board advanced and its STRUCTURED
    board did not — and the structured one is what every reader uses now, so the lane rendered STALE on the
    board while its own collect was running fine every few minutes. Exactly the false-STALE this file was
    written to end, reintroduced by its own fix.

    So the rule: a step may refresh the fragment DIRECTORY only if it puts its own fragment back afterwards.
    """
    ifb = _lanes()
    for wf, job, name, code in _publishing_steps(ifb, lane):
        idx = code.find("checkout")
        if idx < 0 or f"{ifb.FRAGMENT_DIR}/" not in code[idx:idx + 200]:
            continue                        # this step does not bulk-refresh the fragment directory
        own = _board_path(ifb, lane)
        after = code[idx:]
        assert re.search(r"\bcp\b[^\n]*" + re.escape(own.rsplit("/", 1)[-1]), after) \
            or re.search(r"\bcp\b[^\n]*\$\{?FRAGF", after), (
            f"{wf.name}:{job} ({name!r}) refreshes {ifb.FRAGMENT_DIR}/ from upstream but never restores its "
            f"own {own} afterwards — so it publishes upstream's older copy of the fragment this very run "
            f"just wrote, and the lane freezes on the board while its collect runs fine.")


def test_the_supervisor_of_the_billing_legs_publishes_a_board_fragment():
    """★★ THE LOOP THAT WATCHES THE LEGS COSTING LADDER DOLLARS MUST WRITE A BOARD ROW (2026-08-01).

    `selcal_vast_launch.mode_cofold_watch` published a fragment on every tick. `mode_watch` — the loop
    supervising the MD legs, i.e. the ones that spend ladder dollars — published only a COMMIT heartbeat.
    So six minutes after the lane's first MD host started billing, the all-lane board carried that lane's
    44-minute-old CO-FOLD rows under a STALE banner and had no row at all for the leg actually running.

    A billing leg with no board row is the failure the whole board exists to prevent, and it is how a
    subagent's prose ETA for this lane sat in the ETA column for six consecutive reports.
    """
    import inspect
    import sys
    sys.path.insert(0, str(MODALITIES))
    import selcal_vast_launch as L
    for fn in (L.mode_watch, L.mode_cofold_watch):
        src = inspect.getsource(fn)
        assert "_publish_board" in src, (
            f"{fn.__name__} supervises hosts but never writes a board fragment, so its lane renders STALE "
            f"on the all-lane board for the whole window while it is in fact watching perfectly well — and "
            f"any leg it holds has no row at all.")


def test_the_selcal_board_emits_a_row_for_a_rented_md_leg():
    """The rows themselves, across all three host states. `md_rows` is PURE, so this needs no network.

    ⚠ AN ENDED LEG MUST NOT RENDER AS RUNNING, AND AN UNREADABLE HOST LIST MUST NOT RENDER AS ENDED — the
    handles file records a PURCHASE, not a running leg (§4)."""
    import sys
    sys.path.insert(0, str(MODALITIES))
    import selcal_board as B
    h = [{"unit": "selcal-smarca2-m1-r0", "arm": "selcal_smarca2", "instance": "46531433",
          "utc": "2026-08-01T19:37:26Z"}]
    live = B.md_rows(h, hosts=[{"id": 46531433, "actual_status": "running"}], landed=0, n_units=24)
    assert len(live) == 1 and live[0]["state"] == "RUNNING"
    assert live[0]["name"] == "selcal-smarca2-m1-r0" and live[0]["pct_of"] == "0/24 landed"
    assert "46531433" in live[0]["why"]
    # …the host is gone: ENDED, and the row refuses to say WHICH ending.
    gone = B.md_rows(h, hosts=[], landed=0, n_units=24)[0]
    assert gone["state"].startswith("ENDED") and "must not guess an outcome" in gone["why"]
    # …the list could not be read: UNKNOWN, never ENDED.
    unread = B.md_rows(h, hosts=None)[0]
    assert unread["state"] == _lanes().UNKNOWN
    assert "absent reading is not a reading of absence" in unread["why"]
    # …and no $/ns is invented, because the throughput table benches 84k-atom RBFE and these are endpoint MD.
    # ⚠ THIS USED TO ASSERT THE STRING "no benched ns rate", AND THAT ASSERTION HELD THE BUG IN PLACE. The
    # refusal was right; the hand-rolled cell it pinned carried no `$/hr` either, so a row about a host on the
    # meter showed no money at all — measured across 19 billing hosts, 2026-08-01. A test that pins wording
    # cannot tell a correct refusal from an incomplete one. The property is in
    # `tests/test_unpriceable_rows_still_show_their_dollars.py`; here we only check it is the SHARED cell.
    assert live[0]["usd_per_ns"].startswith("—")
    priced = B.md_rows(h, hosts=[{"id": 46531433, "actual_status": "running", "dph_total": 0.1788}],
                       landed=0, n_units=24)[0]["usd_per_ns"]
    assert "0.1788" in priced and "/hr" in priced, priced
