"""No workflow step may hand-roll "commit these artifacts and push them". There is ONE primitive.

★★ WHY THIS EXISTS — trimcrae, 2026-08-01: *"Whenever you find a bug like that, you need to fix the
underlying root cause, not just address it as a one off. I'm sick of having so many bugs all the time."*

He is right, and the evidence is in that day's own commit messages. Every bug fixed on 2026-08-01 was a rule
this repo had ALREADY LEARNED, fixed at one site, and recorded as a COMMENT at that site:

  * `git pull --rebase` in a publish step  — fixed on the GCP lane, then selcal, then step-1. THIRD time.
  * a fixed-width column sized by a constant — fixed for LEG, then `$/ns`, then STATE. THIRD time.
  * a gate's `pip install` missing an import of the file it gates — PyYAML 2026-07-27, numpy 2026-08-01.
    The PyYAML fix wrote *"pyyaml is NOT optional here … it passed locally only because the dev sandbox
    happens to have PyYAML"*, and four days later numpy did the identical thing ON THE SAME LINE.
  * a diagnostic that raises and kills its run — `_frozen_cys_by_construct` 2026-07-31, then
    `_electrophile_and_neighbour` 2026-08-01, in the SAME function, one call earlier.

**A comment cannot enforce itself at the other sites.** That is the generator: fix the instance, write down
the rule, and wait for every remaining instance to fail in production one at a time. So the rule stops being
prose and becomes a checked invariant over ALL sites — which is what this file is.

WHAT THE RULE PROTECTS. `git pull --rebase` against a conflicting sibling tick leaves the repo MID-REBASE;
every retry then dies on the wreckage of the first (`fatal: Exiting because of an unresolved conflict.`)
rather than on anything new, and in the retry-loop shape the step ends on a warning while reporting SUCCESS.
Reproduced end to end in a scratch repo, including that exact fatal line, before the primitive was written.

⚠ AND THE DANGEROUS SET IS THE SUPERVISION LAYER. Measured across the repo when this guard was written:
20 of the 56 that still use `git pull` fail SILENTLY (108 steps hand-roll the publish in all), and they include `vast-account-reaper`,
`vast-watchdog`, `ternary-vast-watchdog`, `lane-staleness-watch` and `account-orphan-alarm` — the jobs that
stop a fleet billing unsupervised. Their heartbeat commits are the very artifacts whose staleness the alarms
grade, so a wedge there freezes the evidence and the supervisor looks alive while publishing nothing.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

MODALITIES = Path(__file__).resolve().parents[1]
REPO = MODALITIES.parents[1]
WORKFLOWS = REPO / ".github" / "workflows"
PRIMITIVE = "research/compute/publish_artifacts.sh"

#: ⛔ THE REGISTERED BACKLOG — NOT AN ALLOW-LIST, AND NOT AN EXEMPTION.
#: Every entry is a step that still hand-rolls the publish. They are recorded so this guard can land GREEN
#: while naming the remaining work, so that (a) no NEW hand-rolled publish can be added, and (b) converting
#: one is exactly one line deleted from here. A test below asserts each entry still describes reality, so an
#: entry cannot outlive the defect it names and quietly become a permanent pardon.
#: Order: the SILENT ones (a wedge reports success) are converted first — they are the ones that lie.
KNOWN_HAND_ROLLED: set[tuple[str, str]] = {
    ("abfe-diagnostics-aws.yml", "diagnostics"),
    ("abfe-plot-aws.yml", "plot"),
    ("abfe-progress-aws.yml", "snap"),
    ("af-crystal-rmsd-aws.yml", "run"),
    ("af2-nmr-rmsd-aws.yml", "run"),
    ("archive-results-aws.yml", "archive"),
    ("aso-breakpoint-scan.yml", "run"),
    ("aso-offtarget.yml", "run"),
    ("build-preprint.yml", "build"),
    ("credit-status.yml", "refresh"),
    ("deepternary-blind-controls.yml", "audit"),
    ("deepternary-inspect-io.yml", "inspect"),
    ("deepternary-qualify.yml", "qualify"),
    ("deepternary-source-inputs.yml", "source"),
    ("depmap-dependency.yml", "run"),
    ("enumerate-drugs.yml", "enumerate"),
    ("fetch-literature.yml", "fetch"),
    ("fusion-cpu-extras.yml", "nrv04_cys"),
    ("fusion-cpu-extras.yml", "run"),
    ("gpu-bench-gcp.yml", "gcp-bench"),
    ("gpu-nr4a-paralogue-md-vast.yml", "ops"),
    ("gpu-protfep-vast.yml", "collect"),
    ("gpu-protfep-vast.yml", "stage-test"),
    ("gpu-ternary-fep-gcp.yml", "gcp-ternary"),
    # ⚠ `launch` and `collect` each hold TWO publishing steps. Their small ones (arming the watchdog,
    # retiring landed watch entries) are converted; the large ones — the 128-line rental ledger and
    # the 106-line in-flight board commit — are not, because in both the publish is interleaved with
    # the logic that produces it and needs its own pass. Registered until then.
    ("gpu-ternary-fep-vast.yml", "launch"),
    ("gpu-ternary-fep-vast.yml", "collect"),
    ("gpu-ternary-fep-vast.yml", "gate_5aks"),
    ("gpu-ternary-fep-vast.yml", "market_gate"),
    ("gpu-ternary-fep-vast.yml", "triangle_gate"),
    ("method-watch.yml", "watch"),
    ("modalities-run.yml", "run"),
    ("nr4a3-dock.yml", "run"),
    ("openfe-introspect.yml", "introspect"),
    ("pose-figure-aws.yml", "render"),
    ("protac-feasibility.yml", "run"),
    ("published-warhead-registry.yml", "run"),
    ("rbfe-edge-timestep-scan.yml", "scan"),
    ("rbfe-progress-aws.yml", "snap"),
    ("rbfe-split-shakeout.yml", "shakeout"),
    ("render-figures.yml", "render"),
    ("replicate-standard-harvest.yml", "harvest"),
    ("report-fm-push.yml", "report"),
    ("report-nrv04-aws.yml", "report"),
    ("ternary-calib-freeze.yml", "freeze"),
    ("ternary-calib-freeze.yml", "triangle"),
    ("txgnn-run.yml", "run"),
    ("vast-board-volatility.yml", "collect"),
    ("vast-price-sample.yml", "sample"),
    ("warhead-chem-profile.yml", "run"),
}


def _run_steps(wf: Path):
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
            yield job_name, str(step.get("name") or ""), code


def _pushes_outside_primitive(code: str) -> bool:
    """True if the step issues a `git push` of its own, whatever else it also calls."""
    return any("git push" in ln for ln in code.splitlines())


def _hand_rolled():
    """(workflow, job, step name) for every step that commits AND pushes without the primitive."""
    out = []
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        for job, name, code in _run_steps(wf):
            if "git commit" not in code or "git push" not in code:
                continue
            # ⚠ "CONTAINS THE PRIMITIVE" IS NOT "USES THE PRIMITIVE" — and the difference produced a FALSE
            # PASS the first time this guard was run against a conversion. The converter appended the
            # `publish_artifacts.sh` call and left the old hand-rolled `git pull` + retry block underneath;
            # the step then contained the primitive, this filter skipped it, and 106 tests went green over a
            # step that would still have run the broken code in CI. A guard that can be satisfied by ADDING
            # text rather than REMOVING the defect is worse than no guard.
            # So the test is on what SURVIVES: any `git push` outside the primitive call is hand-rolled.
            if _pushes_outside_primitive(code):
                out.append((wf.name, job, name))
    return out


def test_the_primitive_exists_and_is_executable():
    p = REPO / PRIMITIVE
    assert p.is_file(), f"{PRIMITIVE} is the one home for this operation and it is missing"
    body = p.read_text()
    for must, why in (
            ("git rebase --abort", "a wedge left by an earlier step must be cleared before anything else"),
            ("git reset -q --hard FETCH_HEAD", "rewrite onto upstream — a conflict must be unrepresentable"),
            ("--allow-empty", "the timestamp IS the heartbeat; a no-diff tick must still publish"),
            ("::error title=ARTIFACTS NOT PUBLISHED", "a publish that did not happen must not read like one"),
            ("PUBLISH_REGEN", "derived many-writer files are regenerated after the reset, never stamped")):
        assert must in body, f"the primitive lost the property that {why}"
    # ⚠ COMMENTS STRIPPED FIRST. The primitive's header explains, at length, why `git pull --rebase` is the
    # wrong operation and quotes the three runs it broke — so a naive scan finds the string it is testing for
    # and fails on the documentation rather than on the code. The incident record must survive; the CODE
    # must not contain the operation.
    code = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))
    assert "git pull" not in code, "the primitive must not contain the operation it exists to replace"


@pytest.mark.parametrize("wf,job,name", _hand_rolled(),
                         ids=[f"{w}:{j}" for w, j, _n in _hand_rolled()])
def test_no_new_hand_rolled_publish(wf, job, name):
    """⛔ THE GUARD. A step that commits and pushes must go through the primitive.

    If this fails on a step you just wrote: do not re-implement the retry loop. Call

        bash research/compute/publish_artifacts.sh "$BRANCH" "<message>" <path>...

    which rewrites onto upstream so a conflict cannot wedge it, publishes unconditionally so the timestamp
    keeps working as a heartbeat, and reports a failed publish as an `::error::` instead of a warning on a
    green step.
    """
    assert (wf, job) in KNOWN_HAND_ROLLED, (
        f"{wf}:{job} ({name!r}) hand-rolls commit+push. That shape has silently failed to publish on three "
        f"separate lanes (GCP 30701290485, selcal 30710853581, step-1 30714482049): one conflict leaves the "
        f"repo mid-rebase, every retry dies on it, and the step reports SUCCESS. Use {PRIMITIVE}.")


def test_a_registered_entry_cannot_outlive_the_defect_it_names():
    """⚠ A registered violation that has been fixed but not deregistered is a lie the guard tells forever —
    and it would let a NEW hand-rolled publish slip in under a stale entry's name."""
    live = {(w, j) for w, j, _n in _hand_rolled()}
    stale = sorted(KNOWN_HAND_ROLLED - live)
    assert not stale, (
        f"these entries no longer describe a hand-rolled publish — delete them so the guard tightens: {stale}")


def test_the_converted_lanes_stay_converted():
    """The board publishers were converted first because their staleness drives every alarm. They must not
    regress, and this is the assertion that would have caught the step-1 lane before it wedged."""
    for wf, job in (("gpu-fanout-rep-gcp.yml", "s1f-rep"),
                    ("step1-fanout-autoscale.yml", "tick"),
                    ("selectivity-control-vast.yml", "cpu"),
                    ("selectivity-control-vast.yml", "gpu")):
        code = "\n".join(c for j, _n, c in _run_steps(WORKFLOWS / wf) if j == job)
        assert "git pull" not in code, f"{wf}:{job} has regressed to `git pull` in a publishing job"
        # …and every one of them is now on the primitive, so "converted" means the stronger thing: they
        # also cannot stamp a file this run never wrote, which is the OTHER way a publish reverts someone.
        assert "publish_artifacts.sh" in code, (
            f"{wf}:{job} no longer publishes through research/compute/publish_artifacts.sh — it may avoid "
            f"the rebase wedge and still revert another job's measurement by stamping its whole checkout")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# THE SAME GENERATOR, ONE LEVEL UP: TWO REGISTRIES THAT NAME THE SAME FACT
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_orphan_alarm_CANNOT_TYPE_A_BOARD_FRAGMENT_PATH():
    """★★ THE SECOND HOME IS DELETED, SO DIVERGENCE IS UNREPRESENTABLE — NOT MERELY DETECTED.

    THE BUG (2026-08-01, 4:37 PM ET). `account_orphan_alarm.ACCOUNT_LANES` typed the artifact whose
    freshness proves a lane reported; `inflight_board.LANES` says where that lane publishes. They drifted,
    and the alarm fired **UNSUPERVISED-BILLING** — its loudest verdict, reserved for money moving with
    nothing watching it — on two lanes that were reporting normally:

        ternary-vast    graded ternary-vast-watch.json      6:32 PM   real heartbeat moved  8:43 PM
        selcal-cofold   graded selcal-cofold-census.json    6:39 PM   real heartbeat moved  8:44 PM

    ⚠ THE FIRST FIX WAS NOT A ROOT-CAUSE FIX, AND THIS TEST REPLACES IT. It re-pointed the four typed
    strings and asserted the two registries AGREE. But a typed path can still diverge; the agreement test
    only *noticed*, and it had three escape hatches — a `fragment: None` entry, a lane id absent from the
    board registry, and a hand-maintained alias map — each of which silently skipped the check. The bug was
    two registries naming one fact with only one updated; adding a third artefact that must be kept in step
    is more of the same disease.

    So the path is DERIVED (`lane_fragment`) and this test forbids the second home from coming back: no
    entry may TYPE a board-fragment path. A new lane is covered the moment it declares `board_lane`, with
    no list to remember to update — which is the property the agreement test could never have.
    """
    import sys
    sys.path.insert(0, str(MODALITIES))
    import account_orphan_alarm as A
    import inflight_board as ifb

    src = (MODALITIES / "account_orphan_alarm.py").read_text()
    code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
    assert f'"{ifb.FRAGMENT_DIR}/' not in code, (
        f"a board-fragment path is TYPED in account_orphan_alarm. It must be DERIVED — declare "
        f"`board_lane` on the entry and let `lane_fragment()` compute it, or the two registries can drift "
        f"again and the alarm will fire UNSUPERVISED-BILLING on a healthy lane.")

    board_ids = {l[0] for l in ifb.LANES}
    for lane in A.ACCOUNT_LANES:
        bl = lane.get("board_lane")
        if bl is None:
            # Genuinely artifact-less lanes are allowed, but they must not fake it with a typed path.
            assert ifb.FRAGMENT_DIR not in str(lane.get("fragment") or ""), lane.get("key")
            continue
        assert bl in board_ids, (
            f"lane {lane.get('key')!r} declares board_lane={bl!r}, which is not a registered board lane — "
            f"its fragment would be derived to a path nothing writes, and the alarm would read the lane as "
            f"silent. Register it in inflight_board.LANES or drop the declaration.")
        assert A.lane_fragment(lane) == f"{ifb.FRAGMENT_DIR}/{bl}.json"


def test_a_new_board_lane_needs_no_second_registration():
    """The property the agreement test could not have: coverage without a list to remember.

    Every lane the alarm watches that has a board fragment must reach it THROUGH `lane_fragment`, so adding
    a lane to `inflight_board.LANES` and pointing an alarm entry at it is the whole job."""
    import sys
    sys.path.insert(0, str(MODALITIES))
    import account_orphan_alarm as A
    import inflight_board as ifb
    covered = {l["board_lane"] for l in A.ACCOUNT_LANES if l.get("board_lane")}
    assert covered, "no alarm lane derives its fragment — the derivation has been bypassed"
    for lane in covered:
        assert A.lane_fragment({"board_lane": lane}) == f"{ifb.FRAGMENT_DIR}/{lane}.json"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ⛔ THE REGISTRY ABOVE SCANS YAML. A PUBLISHER CAN ALSO LIVE IN PYTHON.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _python_modules():
    import pathlib
    return sorted(pathlib.Path(MODALITIES).glob("*.py"))


def _reset_and_stamp_publishers():
    """Functions that wipe the working tree to the remote and lay their own bytes back, then push.

    That shape is a PUBLISHER regardless of whether it lives in a workflow, and it carries the reversal
    exposure in its most dangerous form: after the reset, whatever bytes the process holds become the truth.
    """
    import ast
    out = []
    for path in _python_modules():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, ValueError, OSError):
            continue
        src = path.read_text(encoding="utf-8")
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            seg = ast.get_source_segment(src, node) or ""
            code = "\n".join(l for l in seg.splitlines() if not l.lstrip().startswith("#"))
            pushes = '"push"' in code or "'push'" in code or "git push" in code
            resets = ("reset" in code and "--hard" in code)
            if pushes and resets:
                out.append((path.name, node.name, code))
    return out


def test_every_python_publisher_that_stamps_also_guards_on_the_checkout():
    """★★ MEASURED 2026-08-02, and the guard that should have caught it was structurally blind.

        00:41:37Z  a `collect` tick measured S3 and published `landed: 17`
        00:42:44Z  `selcal_vast_launch._tick_publish`, inside a watch started at 23:05 whose checkout held
                   `landed: 0`, stamped it back to 0 with a five-hour-old timestamp

    It had already done that once at 22:16:50Z, leaving the lane's official census reading ZERO for five
    hours while seventeen legs sat banked in S3.

    ⚠ THE POINT OF THIS TEST IS THE BLIND SPOT, NOT THE BUG. `KNOWN_HAND_ROLLED` and its scanner read
    workflow YAML, so a publisher living inside a long-running python loop was never in their field of view
    — and the registry's green therefore VOUCHED for a path it could not inspect. A guard that cannot see a
    whole class of the thing it guards is worse than one that admits the gap.

    The rule is the same one the shell primitive enforces, asked of the process instead of the job: compare
    against the commit this checkout is on, and if our copy is identical, we did not write it.
    """
    offenders = []
    for mod, fn, code in _reset_and_stamp_publishers():
        if "rev-parse" not in code:
            offenders.append(f"{mod}:{fn}")
    assert not offenders, (
        "these functions reset the tree to the remote and stamp their own bytes back, with no check that "
        "this run actually wrote them — so each can silently revert another job's measurement: "
        + ", ".join(offenders))


def test_the_python_publisher_scanner_actually_finds_the_known_one():
    """⚠ A GUARD THAT CANNOT GO RED IS WORSE THAN NO GUARD. If the AST walk stops resolving these functions
    the test above passes vacuously, which is exactly how the YAML-only registry came to vouch for python."""
    found = {(m, f) for m, f, _ in _reset_and_stamp_publishers()}
    assert ("selcal_vast_launch.py", "_tick_publish") in found, (
        "the scanner no longer sees the publisher this test was written for — it is passing vacuously")


def test_a_skipped_path_is_announced_not_silently_dropped():
    """A path silently dropped from a publish looks exactly like the reverse bug. Both directions must be
    visible in the log, or an operator cannot tell 'declined, correctly' from 'lost'."""
    src = (MODALITIES / "selcal_vast_launch.py").read_text(encoding="utf-8")
    body = src[src.index("def _tick_publish("):]
    body = body[:body.index("\ndef ", 10)]
    assert "unchanged since checkout, upstream's kept" in body


def test_the_heartbeat_survives_every_path_being_skipped():
    """⚠ THE TRAP IN THE FIX. If every artifact belonged to somebody else, the naive guard returns early and
    commits nothing — and a healthy loop that happened to write nothing becomes byte-identical to one that
    stopped. The tick must still be dated."""
    src = (MODALITIES / "selcal_vast_launch.py").read_text(encoding="utf-8")
    body = src[src.index("def _tick_publish("):]
    body = body[:body.index("\ndef ", 10)]
    tail = body[body.index("if not keep:"):]
    assert "--allow-empty" in tail, "a tick that skipped everything must still leave a dated commit"
    assert "STILL A HEARTBEAT" in tail
