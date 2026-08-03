"""`publish_artifacts.sh` must never push a file BACKWARDS on behalf of a job that did not write it.

★★ THE INCIDENT THIS REPRODUCES (measured 2026-08-01, a five-second window).

    22:16:43Z  selcal `collect`  publishes selcal-collect.json   landed: 5
    22:16:50Z  selcal `status`   publishes selcal-collect.json   landed: 0, utc 19:51:35Z

`status` does not compute collect. It had merely checked the file out three hours earlier and named it in its
publish path list, so it carried a stale copy forward over a fresh one. For the next tick the lane's official
state was "0 of 24 landed" while five legs sat banked in S3 — and nothing was red, because there was no
conflict: a clean older version of a file applies perfectly onto a newer one and reverts it silently.

⚠ THE REWRITE-ONTO-UPSTREAM LOOP CANNOT CATCH THIS, which is why this test is separate from the conflict
tests. That loop exists so a *concurrent* write cannot wedge a rebase; it says nothing about whether the
bytes we are about to push are ours to push. `PUBLISH_REGEN` covers the case where this job CAN rebuild a
derived file; it does not cover a file this job has no business touching at all.

The rule under test is the one with a single answer: **did this run change the file?** Not "is ours newer" —
that would be a timestamp race, and every heartbeat commit rewrites a timestamp.
"""
import os
import shutil
import subprocess
import textwrap

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))   # tests/ -> modalities/ -> research/ -> repo
PUBLISH = os.path.join(REPO, "research", "compute", "publish_artifacts.sh")

pytestmark = pytest.mark.skipif(not shutil.which("git"), reason="git is required")

ART = "research/modalities/selcal-collect.json"


def _run(cmd, cwd, env=None, check=True):
    e = dict(os.environ)
    e.update(env or {})
    e.setdefault("GIT_AUTHOR_NAME", "t")
    e.setdefault("GIT_AUTHOR_EMAIL", "t@e")
    e.setdefault("GIT_COMMITTER_NAME", "t")
    e.setdefault("GIT_COMMITTER_EMAIL", "t@e")
    p = subprocess.run(cmd, cwd=cwd, env=e, shell=isinstance(cmd, str),
                       capture_output=True, text=True)
    if check and p.returncode != 0:
        raise AssertionError(f"{cmd}\nrc={p.returncode}\n{p.stdout}\n{p.stderr}")
    return p


def _write(root, rel, body):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(body)


def _read_origin(origin, rel):
    return _run(["git", "show", f"main:{rel}"], cwd=origin).stdout


@pytest.fixture()
def world(tmp_path):
    """A bare origin plus two clones: `collect` (fresh) and `status` (checked out earlier, stale copy)."""
    origin = tmp_path / "origin.git"
    seed = tmp_path / "seed"
    _run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], cwd=str(tmp_path))
    _run(["git", "init", "-q", "-b", "main", str(seed)], cwd=str(tmp_path))
    _write(str(seed), ART, '{"landed": 0, "utc": "19:51:35Z"}\n')
    _write(str(seed), "research/modalities/selcal-verdict.json", '{"tier": "PENDING"}\n')
    _run(["git", "add", "-A"], cwd=str(seed))
    _run(["git", "commit", "-qm", "seed"], cwd=str(seed))
    _run(["git", "remote", "add", "origin", str(origin)], cwd=str(seed))
    _run(["git", "push", "-q", "origin", "main"], cwd=str(seed))

    clones = {}
    for name in ("collect", "status"):
        d = tmp_path / name
        _run(["git", "clone", "-q", str(origin), str(d)], cwd=str(tmp_path))
        clones[name] = str(d)
    return str(origin), clones


def _publish(cwd, msg, paths, env=None):
    return _run([PUBLISH, "main", msg, *paths], cwd=cwd, env=env)


def test_a_job_that_did_not_write_the_file_does_not_revert_it(world):
    """THE REGRESSION, exactly as it happened."""
    origin, c = world

    # `collect` measures S3 and publishes the real number.
    _write(c["collect"], ART, '{"landed": 5, "utc": "22:16:43Z"}\n')
    _publish(c["collect"], "selcal collect: lane tick (CI)", [ART])
    assert '"landed": 5' in _read_origin(origin, ART)

    # `status` checked out BEFORE that push, never touched collect, and lists it in its path list anyway.
    out = _publish(c["status"], "selcal status: lane tick (CI)", [ART])

    body = _read_origin(origin, ART)
    assert '"landed": 5' in body, (
        "the `status` job republished a file it never wrote, reverting `collect`'s measurement:\n" + body)
    assert "19:51:35Z" not in body, body
    # and it must SAY it declined, so this is never confused with a publish that failed to land.
    assert "not ours to publish" in out.stdout, out.stdout


def test_the_job_that_did_write_it_still_publishes(world):
    """The guard must not block real work — that would be the opposite bug, and a worse one."""
    origin, c = world
    _write(c["collect"], ART, '{"landed": 5, "utc": "22:16:43Z"}\n')
    _publish(c["collect"], "collect", [ART])

    # `status` pulls, then genuinely rewrites the file. Its version must win.
    _run(["git", "fetch", "-q", "origin", "main"], cwd=c["status"])
    _run(["git", "reset", "-q", "--hard", "FETCH_HEAD"], cwd=c["status"])
    _write(c["status"], ART, '{"landed": 6, "utc": "22:20:00Z"}\n')
    _publish(c["status"], "status", [ART])
    assert '"landed": 6' in _read_origin(origin, ART)


def test_a_file_created_by_this_run_publishes(world):
    """Absent at checkout means it is new work, not an untouched file."""
    origin, c = world
    new = "research/modalities/selcal-brand-new.json"
    _write(c["status"], new, '{"hello": 1}\n')
    _publish(c["status"], "status", [new])
    assert '"hello": 1' in _read_origin(origin, new)


def test_untouched_files_do_not_block_the_touched_ones_beside_them(world):
    """A mixed path list is the normal case: publish what is ours, keep upstream's for the rest."""
    origin, c = world
    verdict = "research/modalities/selcal-verdict.json"

    _write(c["collect"], ART, '{"landed": 5, "utc": "22:16:43Z"}\n')
    _publish(c["collect"], "collect", [ART])

    _write(c["status"], verdict, '{"tier": "RUNNING"}\n')       # ours
    _publish(c["status"], "status", [ART, verdict])             # ART is not

    assert '"landed": 5' in _read_origin(origin, ART)
    assert '"tier": "RUNNING"' in _read_origin(origin, verdict)


def test_the_heartbeat_commit_still_happens_when_everything_was_skipped(world):
    """⚠ The timestamp IS the heartbeat (see the primitive's header). A tick that had nothing of its own to
    say must still leave a commit, or a healthy idle job becomes byte-identical to a dead one — which is the
    landmine the `--allow-empty` rule exists to defuse."""
    origin, c = world
    _write(c["collect"], ART, '{"landed": 5, "utc": "22:16:43Z"}\n')
    _publish(c["collect"], "collect", [ART])
    before = _run(["git", "rev-parse", "main"], cwd=origin).stdout.strip()

    _publish(c["status"], "selcal status: lane tick (CI)", [ART])

    after = _run(["git", "rev-parse", "main"], cwd=origin).stdout.strip()
    assert after != before, "the tick left no commit at all — the heartbeat is gone"
    assert "selcal status" in _run(["git", "log", "-1", "--format=%s", "main"], cwd=origin).stdout


def test_the_escape_hatch_restores_the_old_behaviour(world):
    """`PUBLISH_STAMP_UNTOUCHED=1` for a caller that genuinely means "stamp my whole checkout" — an escape
    hatch for a diagnosis, not a setting to leave on."""
    origin, c = world
    _write(c["collect"], ART, '{"landed": 5, "utc": "22:16:43Z"}\n')
    _publish(c["collect"], "collect", [ART])
    _publish(c["status"], "status", [ART], env={"PUBLISH_STAMP_UNTOUCHED": "1"})
    assert '"landed": 0' in _read_origin(origin, ART)


def test_the_primitive_documents_the_incident():
    """The reasoning must live next to the code, not only in a test name."""
    with open(PUBLISH) as fh:
        src = fh.read()
    assert "_this_run_wrote_it" in src
    assert "22:16:43Z" in src and "22:16:50Z" in src, (
        "the measured five-second reversal is the evidence for this guard; keep it beside the guard")
    assert textwrap.dedent("").strip() == ""


# =============================================================================================================
# heartbeat publishes vs event publishes
# =============================================================================================================
def test_an_event_publish_writes_nothing_when_nothing_changed(world):
    """`triangle_freeze` commits "freeze cmpd4″ (two independent routes agree)". An `--allow-empty` commit on
    a run where nothing was frozen ASSERTS an event that did not happen, and a `git log` audit of when the
    molecule was frozen cannot tell it from the real one."""
    origin, c = world
    before = _run(["git", "rev-parse", "main"], cwd=origin).stdout.strip()
    _publish(c["status"], "valB closure triangle: freeze cmpd4 (CI)", [ART],
             env={"PUBLISH_IF_CHANGED": "1"})
    assert _run(["git", "rev-parse", "main"], cwd=origin).stdout.strip() == before


def test_an_event_publish_STILL_publishes_when_something_did_change(world):
    """The flag must not become a way to lose an event — only a way not to invent one."""
    origin, c = world
    _write(c["status"], ART, '{"landed": 3, "utc": "23:00:00Z"}\n')
    _publish(c["status"], "valB closure triangle: freeze cmpd4 (CI)", [ART],
             env={"PUBLISH_IF_CHANGED": "1"})
    assert '"landed": 3' in _read_origin(origin, ART)


def test_the_default_is_the_heartbeat_and_it_still_commits_empty(world):
    """⛔ THE DEFAULT MUST NOT MOVE. Everything that is a lane tick depends on the unconditional commit."""
    origin, c = world
    before = _run(["git", "rev-parse", "main"], cwd=origin).stdout.strip()
    _publish(c["status"], "selcal status: lane tick (CI)", [ART])
    assert _run(["git", "rev-parse", "main"], cwd=origin).stdout.strip() != before


def test_no_heartbeat_caller_sets_the_event_flag():
    """⛔ THE FLAG MUST NEVER REACH A TICK. That would be exactly the "optimisation" the primitive's header
    warns about — a healthy idle job becoming byte-identical to a dead one — arriving through an env var
    instead of through an inlined `git diff --cached --quiet`.

    Read from the workflows themselves, because the rule is only worth anything where it is applied.
    """
    import yaml

    wfdir = os.path.join(REPO, ".github", "workflows")
    offenders = []
    for fn in sorted(os.listdir(wfdir)):
        if not fn.endswith((".yml", ".yaml")):
            continue
        try:
            doc = yaml.safe_load(open(os.path.join(wfdir, fn)).read())
        except yaml.YAMLError:
            continue
        for job, j in (doc or {}).get("jobs", {}).items():
            for st in (j or {}).get("steps") or []:
                env = (st or {}).get("env") or {}
                run = str((st or {}).get("run") or "")
                if not isinstance(env, dict) or str(env.get("PUBLISH_IF_CHANGED", "")) != "1":
                    continue
                # The message is the second argument to the primitive; a heartbeat names itself.
                # ⚠ COMMENT LINES ARE STRIPPED FIRST, AND THAT IS A CORRECTNESS FIX, NOT A LOOSENING
                # (2026-08-03). YAML keeps `#` lines inside a `run: |` block, so this test was matching
                # the PROSE rather than the command — and the prose an event publish is supposed to carry
                # is precisely an explanation of why it is *not* a lane tick. `pose-recovery-check.yml`
                # was failing on the words "a lane tick whose" and "a conflicting sibling tick" in the
                # comment that documents the rule being obeyed, so the guard was red on a compliant
                # caller and, being the last assertion in this file, took the suite with it. A comment
                # can never be the message argument, so removing them cannot let a real heartbeat past;
                # the executable half of the run block is still scanned in full.
                code = "\n".join(ln for ln in run.splitlines()
                                 if not ln.lstrip().startswith("#"))
                if "tick" in code.lower() or "heartbeat" in code.lower():
                    offenders.append(f"{fn}:{job}:{st.get('name')}")
    assert not offenders, (
        "PUBLISH_IF_CHANGED=1 on what looks like a HEARTBEAT publish — the timestamp is the only signal a "
        f"staleness alarm has, so suppressing an unchanged tick makes a healthy job look dead: {offenders}")


def test_the_heartbeat_detector_still_fires_on_a_real_tick():
    """⛔ THE COMMENT STRIP ABOVE MUST NOT HAVE BLUNTED THE GUARD. A commented-out heartbeat is not a
    heartbeat; a real one — the message argument on an executable line — must still be caught."""
    def _offends(run):
        code = "\n".join(ln for ln in run.splitlines() if not ln.lstrip().startswith("#"))
        return "tick" in code.lower() or "heartbeat" in code.lower()

    assert _offends('bash publish_artifacts.sh main "selcal status: lane tick (CI)" a.json')
    assert _offends('  bash publish_artifacts.sh main "gcp heartbeat" a.json')
    assert not _offends('# this is not a lane tick and not a heartbeat\n'
                        'bash publish_artifacts.sh main "valB closure: freeze cmpd4 (CI)" a.json')


# =============================================================================================================
# a path may be a DIRECTORY
# =============================================================================================================
DIRPATH = "research/modalities/5aks_fep_inputs"


def test_a_directory_path_is_published(world):
    """⚠ CAUGHT CONVERTING `prime_5aks`, which hands over a DIRECTORY of per-leg staging manifests.

    `cp --parents` without `-a` dies on a directory ("with --parents, the destination must be a directory"),
    and every copy here is `|| true`-shaped — so the snapshot would come up EMPTY and the publish would push
    nothing while reporting success. That is the exact failure this whole primitive exists to end, so it
    must not be reachable through the primitive itself.
    """
    origin, c = world
    _write(c["status"], f"{DIRPATH}/leg_a/staging_manifest.json", '{"leg": "a"}\n')
    _write(c["status"], f"{DIRPATH}/leg_b/staging_manifest.json", '{"leg": "b"}\n')
    _publish(c["status"], "RUNG 5a-KS: staging manifests (CI)", [DIRPATH],
             env={"PUBLISH_IF_CHANGED": "1"})
    assert '"leg": "a"' in _read_origin(origin, f"{DIRPATH}/leg_a/staging_manifest.json")
    assert '"leg": "b"' in _read_origin(origin, f"{DIRPATH}/leg_b/staging_manifest.json")


def test_a_directory_is_replaced_not_nested_inside_itself(world):
    """`cp -a src parent/` with `parent/src` already present writes `parent/src/src`. The restore must
    replace the directory, or a second publish would bury the manifests one level deeper each time."""
    origin, c = world
    _write(c["status"], f"{DIRPATH}/leg_a/staging_manifest.json", '{"v": 1}\n')
    _publish(c["status"], "staging manifests (CI)", [DIRPATH], env={"PUBLISH_IF_CHANGED": "1"})

    _run(["git", "fetch", "-q", "origin", "main"], cwd=c["status"])
    _run(["git", "reset", "-q", "--hard", "FETCH_HEAD"], cwd=c["status"])
    _write(c["status"], f"{DIRPATH}/leg_a/staging_manifest.json", '{"v": 2}\n')
    _publish(c["status"], "staging manifests (CI)", [DIRPATH], env={"PUBLISH_IF_CHANGED": "1"})

    assert '"v": 2' in _read_origin(origin, f"{DIRPATH}/leg_a/staging_manifest.json")
    nested = _run(["git", "ls-tree", "-r", "--name-only", "main"], cwd=origin).stdout
    assert f"{DIRPATH}/5aks_fep_inputs" not in nested, nested


def test_the_ternary_lane_actually_passes_a_directory():
    """The regression above is only reachable because a real caller does this — pin that it still does, so
    the test above cannot quietly become hypothetical."""
    import yaml
    wf = os.path.join(REPO, ".github", "workflows", "gpu-ternary-fep-vast.yml")
    doc = yaml.safe_load(open(wf).read())
    runs = "\n".join(str(st.get("run") or "")
                     for j in doc["jobs"].values() for st in (j or {}).get("steps") or [])
    assert "publish_artifacts.sh" in runs and DIRPATH in runs
