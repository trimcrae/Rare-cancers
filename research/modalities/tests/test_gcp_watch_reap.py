#!/usr/bin/env python3
"""A watchdog whose DONE branch only PRINTS an instruction is a watchdog that never finishes anything.

These pin the fix and, just as importantly, its limit: the reap fires on the TERMINAL state only. Reaping a
unit whose reducer has not been dispatched yet would disable the entry before the pass that computes its
verdict, converting a bookkeeping tidy-up into a lost result.
"""
import ast
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gcp_watch_reap as r  # noqa: E402

MOD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gcp_watch_reap.py")
SH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "watchdog_run.sh")
WF = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                  ".github", "workflows", "ternary-leg-watchdog.yml")


def _doc():
    return {"watch": [
        {"enabled": True, "leg_id": "legA", "direction": "rev", "seed": "0"},
        {"enabled": True, "leg_id": "legB", "direction": "fwd", "seed": "0"},
        {"enabled": False, "leg_id": "legC", "direction": "fwd", "seed": "1"},
    ]}


# ---------------------------------------------------------------- it actually disables
def test_a_landed_unit_is_disabled():
    d = _doc()
    done = r.reap(d, ["legA|rev|0"])
    assert done == ["legA|rev|0"]
    assert d["watch"][0]["enabled"] is False
    assert d["watch"][1]["enabled"] is True, "it must not touch a unit that was not named"


def test_the_seed_matches_across_the_shell_python_boundary():
    # watchdog_run.sh builds "$LEG|$DIR|$SEED" from shell strings; the file stores "seed": "0". An int/str
    # mismatch here would match nothing and be indistinguishable from "there was nothing to reap".
    d = {"watch": [{"enabled": True, "leg_id": "legA", "direction": "rev", "seed": 0}]}
    assert r.reap(d, [r.unit_key("legA", "rev", 0)]) == ["legA|rev|0"]


def test_an_already_disabled_unit_is_a_no_op_not_an_error():
    d = _doc()
    assert r.reap(d, ["legC|fwd|1"]) == []


def test_an_unknown_unit_is_ignored():
    assert r.reap(_doc(), ["nosuch|fwd|0"]) == []


# ---------------------------------------------------------------- it can only ever silence, never arm
def test_it_never_re_enables_anything():
    d = _doc()
    r.reap(d, ["legA|rev|0", "legC|fwd|1"])
    assert [w["enabled"] for w in d["watch"]] == [False, True, False]


def test_the_module_cannot_dispatch_provision_or_rent():
    src = open(MOD).read()
    for banned in ("subprocess", "gcloud", "gh workflow", "boto3", "requests", "urllib"):
        assert banned not in src, banned


# ---------------------------------------------------------------- the verdict must not be lost
def test_the_disable_reason_points_at_the_verdict():
    # The instruction it replaces was "set enabled=false ONCE YOU HAVE READ IT". Disabling automatically must
    # not become a way to lose the thing that was meant to be read.
    d = _doc()
    r.reap(d, ["legA|rev|0"], verdict_url="https://example/run/1")
    why = d["watch"][0]["_disabled_why"]
    assert "https://example/run/1" in why
    assert "FINISHED, not parked" in why, "a landed unit must not read as abandoned"


def test_the_reason_still_points_somewhere_with_no_url():
    d = _doc()
    r.reap(d, ["legA|rev|0"])
    assert "REDUCE-VERDICT" in d["watch"][0]["_disabled_why"]


# ---------------------------------------------------------------- the CLI works AS A SCRIPT
def test_argv_is_not_discarded():
    # The exact bug that made vast_machine_blacklist --clear a silent no-op twice: an empty-list default
    # parses nothing, so every flag vanishes while the run still "succeeds".
    #
    # Asserted against the PARSED default, not a substring: the module's own comment names the bad form, and
    # a plain scan would trip over the warning against it — which is how this test failed the first time it
    # was written, for the second time in one session.
    tree = ast.parse(open(MOD).read())
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "main")
    first = next(n for n in fn.body if isinstance(n, ast.Assign))
    assert isinstance(first.value, ast.IfExp)
    assert ast.unparse(first.value.body).startswith("sys.argv["), \
        "main() must fall back to the real argv, not []"


def test_nothing_is_defined_after_the_main_guard():
    # A helper defined below `if __name__ == "__main__"` imports fine and NameErrors as a script — all unit
    # tests pass and the workflow step still dies.
    tree = ast.parse(open(MOD).read())
    guard = next(i for i, n in enumerate(tree.body)
                 if isinstance(n, ast.If) and "__main__" in ast.dump(n.test))
    assert not [n for n in tree.body[guard + 1:]
                if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Assign))]


def test_it_runs_end_to_end_the_way_the_workflow_runs_it(tmp_path):
    p = tmp_path / "watch.json"
    p.write_text(json.dumps(_doc()))
    out = subprocess.run([sys.executable, MOD, "--path", str(p), "legA|rev|0"],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert json.loads(p.read_text())["watch"][0]["enabled"] is False
    assert "REAPED A LANDED UNIT" in out.stdout


def test_naming_nothing_writes_nothing(tmp_path):
    p = tmp_path / "watch.json"
    before = json.dumps(_doc())
    p.write_text(before)
    out = subprocess.run([sys.executable, MOD, "--path", str(p)], capture_output=True, text=True)
    assert out.returncode == 0
    assert p.read_text() == before, "a steady-state pass must produce no diff and therefore no commit"


# ============================================================================================================
# ★ THE CALL SITE. A reaper nothing calls is the same defect in a new file.
# ============================================================================================================
def _sh():
    return open(SH).read()


def test_only_the_terminal_branch_queues_a_reap():
    # THE important one. The DONE state fans out to converge, then reduce on the NEXT pass. Queuing a reap
    # from either of those branches disables the entry before the reducer is ever dispatched.
    src = _sh()
    assert src.count('>> "$REAP"') == 1, "exactly one branch may queue a reap — the terminal one"
    idx = src.index('>> "$REAP"')
    # It must sit AFTER the branch that dispatches the reducer (so the reducer has already been sent) and
    # inside the branch whose message reports the terminal state.
    assert src.index("mode=reduce next pass") < idx, \
        "the reap is queued before the converge branch — the reducer would never be dispatched"
    tail = src[idx:idx + 800]
    assert "both converge+reduce already dispatched" in tail, \
        "the reap is not in the terminal branch — it must accompany the both-dispatched message"


def test_the_shell_actually_invokes_the_reaper():
    assert "gcp_watch_reap.py" in _sh()


def test_the_old_do_it_yourself_instruction_is_gone():
    # Its return means the automation was reverted and the manual step is back.
    body = "\n".join(l for l in _sh().splitlines() if not l.strip().startswith("#"))
    assert "Nothing left to do: set enabled=false" not in body


def test_a_failed_push_warns_rather_than_paging():
    # Failing the job fires the workflow-failure notification reserved for a leg in trouble. A push race is
    # expected, and costs only a stale entry the next pass retries.
    src = _sh()
    assert "WATCHDOG REAP NOT PERSISTED" in src
    assert 'echo "REAP' not in src, "a reap problem must never be appended to $ALERT"


def test_the_workflow_can_commit_what_it_reaps():
    # contents: read would make every reap local to a throwaway runner — it would appear to work, forever.
    wf = open(WF).read()
    assert "contents: write" in wf
    assert "contents: read" not in wf


# ============================================================================================================
# ★ THE REAP MUST NOT BLIND THE ORPHAN CHECK.
#
# Before auto-reaping existed, entries stayed enabled forever, so the watchdog's VM listing always ran. The
# reap removed that accident: the first pass after the last unit lands now sees an EMPTY list, and that is
# exactly the pass that should ask whether the finished unit's VM survived it. A GCP VM cannot delete itself
# and GPUS_ALL_REGIONS=1, so one orphan blocks the whole lane with nothing billing to make it noticeable.
# ============================================================================================================
def _idle_branch(src):
    """The `N = 0` branch, up to its own closing `fi`."""
    i = src.index('if [ "$N" = "0" ]')
    return src[i:src.index("\nfi\n", i)]


def _orphan_sweep(src):
    """orphan_sweep()'s body — where the idle branch's work now actually happens."""
    i = src.index("orphan_sweep() {")
    return src[i:src.index("\n}\n", i)]


def test_the_idle_exit_still_looks_for_an_orphan_vm():
    # ⚠ THE CHECK FOLLOWS THE DELEGATION. The listing used to be inline in this branch; it now lives in
    # orphan_sweep(), which the branch calls. Asserting on the inline text would have failed a correct
    # refactor — and, worse, an assertion scoped to a text window that no longer contains the relevant code
    # passes vacuously in the other direction, which is how a guard quietly stops guarding.
    src = _sh()
    assert "orphan_sweep" in _idle_branch(src), \
        "the empty-watch-list branch exits without ever checking for a VM holding the single GPU"
    assert "gcloud compute instances list" in _orphan_sweep(src)


def test_an_orphan_raises_an_alert_rather_than_exiting_clean():
    src = _sh()
    sweep, idle = _orphan_sweep(src), _idle_branch(src)
    assert "WATCHDOG ORPHAN VM" in sweep
    assert '>> "$ALERT"' in sweep, "an unreapable orphan must trip the alert file"
    assert "exit 1" in idle, "an orphan must fail the job so the workflow-failure notification fires"
    assert '-s "$ALERT"' in idle, "the idle branch must decide its exit code from what the sweep raised"


def test_the_idle_branch_never_destroys_what_it_does_not_recognise():
    """A VM the sweep cannot IDENTIFY is still never touched — the rule is bounded, not weakened.

    The sweep may now delete, but only a VM that (a) carries its own tfep-* labels, (b) is mode=run,
    (c) has its own restraint-keyed result object already in GCS, and (d) predates that object. Age is
    never consulted, which is the property that matters: a healthy ternary leg legitimately runs ~44 h, so
    "old" is evidence it is WORKING. This asserts the structure; the BEHAVIOUR — every refusal path issuing
    zero deletes — is driven against a stubbed gcloud in tests/test_watchdog_orphan_sweep.sh.
    """
    sweep = _orphan_sweep(_sh())
    for guard in ('[ "$_leg" = "-" ]',          # unlabelled -> refuse
                  '[ "$_mode" != "run" ]',      # no leg result exists for it -> refuse
                  '[ -z "${_ort:-}" ]',         # result not in GCS -> refuse
                  '[ "$_ce" -ge "$_oe" ]'):     # VM newer than the result -> spare
        assert guard in sweep, f"the orphan sweep lost its {guard} refusal"
    assert "age" not in sweep.lower().split("message")[0] or "AGE_MIN" not in sweep, \
        "the orphan sweep must never reap on age — a healthy leg legitimately runs ~44 h"
    # and the delete must be downstream of every one of those refusals
    assert sweep.index("instances delete") > max(sweep.index(g) for g in (
        '[ "$_leg" = "-" ]', '[ "$_mode" != "run" ]', '[ -z "${_ort:-}" ]', '[ "$_ce" -ge "$_oe" ]'))
