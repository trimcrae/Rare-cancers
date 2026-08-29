"""A failed `PUBLISH_REGEN` must fail the step, not just warn inside an otherwise-green job (AUT-PD-159).

★★ THE INCIDENT. `method-watch-triggers.yml`'s commit step ran `PUBLISH_REGEN: python3
systems/systems_check.py --write-views` without `pyyaml` installed. `publish_artifacts.sh` caught the
failure, printed `::warning::`, and published the primary artifacts (the graph) anyway — which is right
for the graph and wrong for the generated view, because nothing distinguished "regen produced no change"
from "regen could not run". The job reported SUCCESS. Every session's preflight then failed gate 2 until
a human noticed the drift and hand-repaired it — THREE TIMES (8591224fd, 197770ccc, and the commit that
filed this fix).

The soft-fail on the PRIMARY artifacts is correct and must not change: a missing dependency in a DERIVED
convenience must never cost the real work. What must change is that the job itself goes red when that
happens, so CI catches the drift instead of a human's preflight several commits later.
"""
import os
import shutil
import subprocess

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
    """A bare origin plus one clone, seeded with the artifact the caller will publish."""
    origin = tmp_path / "origin.git"
    seed = tmp_path / "seed"
    _run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], cwd=str(tmp_path))
    _run(["git", "init", "-q", "-b", "main", str(seed)], cwd=str(tmp_path))
    _write(str(seed), ART, '{"landed": 0}\n')
    _run(["git", "add", "-A"], cwd=str(seed))
    _run(["git", "commit", "-qm", "seed"], cwd=str(seed))
    _run(["git", "remote", "add", "origin", str(origin)], cwd=str(seed))
    _run(["git", "push", "-q", "origin", "main"], cwd=str(seed))

    clone = tmp_path / "clone"
    _run(["git", "clone", "-q", str(origin), str(clone)], cwd=str(tmp_path))
    return str(origin), str(clone)


def _publish(cwd, msg, paths, env=None, check=True):
    return _run([PUBLISH, "main", msg, *paths], cwd=cwd, env=env, check=check)


def test_a_failing_regen_still_publishes_the_primary_artifact(world):
    """The soft-fail on the real work must not change: this is the part the incident report calls sound."""
    origin, clone = world
    _write(clone, ART, '{"landed": 5}\n')
    out = _publish(clone, "collect", [ART], env={"PUBLISH_REGEN": "false"}, check=False)
    assert '"landed": 5' in _read_origin(origin, ART), out.stdout + out.stderr


def test_a_failing_regen_fails_the_step(world):
    """This is the fix: the job must go red so CI, not a human's later preflight, catches the drift."""
    origin, clone = world
    _write(clone, ART, '{"landed": 5}\n')
    out = _publish(clone, "collect", [ART], env={"PUBLISH_REGEN": "false"}, check=False)
    assert out.returncode != 0, (
        "a failed PUBLISH_REGEN must fail the step, not report success:\n" + out.stdout + out.stderr)
    assert "PUBLISH REGEN FAILED" in (out.stdout + out.stderr)


def test_a_failing_regen_that_produces_a_derived_file_anyway_still_fails(world):
    """A regen command can partially succeed (produce output, then exit non-zero). The exit code is what
    the caller must trust, not "did some file appear" — mirrors the incident, where systems_check.py did
    partially run before dying on the missing import."""
    origin, clone = world
    derived = "research/modalities/selcal-verdict.json"
    regen = f"echo '{{\"tier\": \"PARTIAL\"}}' > {derived}; exit 1"
    out = _publish(clone, "collect", [ART], env={"PUBLISH_REGEN": regen, "PUBLISH_REGEN_ADD": derived},
                    check=False)
    assert out.returncode != 0, out.stdout + out.stderr
    assert '"tier": "PARTIAL"' in _read_origin(origin, derived), (
        "the partial output is still real work and must still publish:\n" + out.stdout + out.stderr)


def test_a_succeeding_regen_does_not_fail_the_step(world):
    """The opposite bug would be worse: every ordinary publish must stay green."""
    origin, clone = world
    _write(clone, ART, '{"landed": 5}\n')
    out = _publish(clone, "collect", [ART], env={"PUBLISH_REGEN": "true"}, check=False)
    assert out.returncode == 0, out.stdout + out.stderr


def test_no_regen_at_all_does_not_fail_the_step(world):
    """The overwhelming majority of callers set no PUBLISH_REGEN at all; nothing here may touch them."""
    origin, clone = world
    _write(clone, ART, '{"landed": 5}\n')
    out = _publish(clone, "collect", [ART], check=False)
    assert out.returncode == 0, out.stdout + out.stderr


def test_the_primitive_documents_the_incident():
    """The reasoning must live next to the code, not only in a test name."""
    with open(PUBLISH) as fh:
        src = fh.read()
    assert "AUT-PD-159" in src
    assert "REGEN_FAILED" in src
