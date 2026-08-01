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
