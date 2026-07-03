import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nr4a3_fep as fep  # noqa: E402


class _FakePopen:
    """Minimal subprocess.Popen stand-in: emits `lines` on stdout, then exits with `rc`."""

    def __init__(self, lines, rc):
        self.stdout = iter(lines)
        self.returncode = rc

    def wait(self):
        return self.returncode


def _patch_popen(monkeypatch, scripted):
    """scripted = list of (lines, rc); each call to Popen pops the next scenario.
    _run_yank_resilient does a local `import subprocess`, so patching the real module suffices."""
    import subprocess
    calls = {"n": 0}

    def fake_popen(cmd, **kw):
        lines, rc = scripted[calls["n"]]
        calls["n"] += 1
        return _FakePopen(lines, rc)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    return calls


def test_clean_success_runs_once(tmp_path, monkeypatch):
    calls = _patch_popen(monkeypatch, [(["yank iter 1\n", "done\n"], 0)])
    rc = fep._run_yank_resilient("nr4a3", str(tmp_path / "exp.yaml"), str(tmp_path))
    assert rc == 0
    assert calls["n"] == 1                                   # no retry on success


def test_trailblaze_corruption_self_heals(tmp_path, monkeypatch):
    exp = tmp_path / "experiments"
    exp.mkdir()
    (exp / "corrupt.nc").write_text("garbage")               # the stale trailblaze checkpoint
    corrupt_msg = ["Traceback\n",
                   "RuntimeError: The trailblaze algorithm was interrupted while writing the checkpoint "
                   "file and it is now unable to resume. Please delete the files in .../experiments/\n"]
    calls = _patch_popen(monkeypatch, [(corrupt_msg, 1), (["fresh trailblaze\n", "done\n"], 0)])
    rc = fep._run_yank_resilient("nr4a1", str(tmp_path / "exp.yaml"), str(tmp_path))
    assert rc == 0                                           # recovered on the retry
    assert calls["n"] == 2                                   # ran twice
    assert not exp.exists()                                  # corrupt experiments/ was cleared


def test_trailblaze_dcd_variant_self_heals(tmp_path, monkeypatch):
    # the 2nd corruption signature: a resume that can't read the half-synced trailblaze trajectory
    exp = tmp_path / "experiments"
    exp.mkdir()
    (exp / "trailblaze").mkdir()
    dcd_msg = ["openmmtools.multistate warning\n",
               "dcdplugin) Could not access file "
               "'/opt/ml/checkpoints/nr4a3/experiments/trailblaze/solvent/coordinates.dcd'.\n"]
    calls = _patch_popen(monkeypatch, [(dcd_msg, 1), (["fresh trailblaze\n", "done\n"], 0)])
    rc = fep._run_yank_resilient("nr4a3", str(tmp_path / "exp.yaml"), str(tmp_path))
    assert rc == 0
    assert calls["n"] == 2
    assert not exp.exists()


def test_non_corruption_failure_does_not_retry(tmp_path, monkeypatch):
    (tmp_path / "experiments").mkdir()
    calls = _patch_popen(monkeypatch, [(["Some things went wrong with LEaP\n"], 1)])
    rc = fep._run_yank_resilient("nr4a2", str(tmp_path / "exp.yaml"), str(tmp_path))
    assert rc == 1                                           # a real error propagates
    assert calls["n"] == 1                                   # no retry — not a trailblaze corruption
    assert (tmp_path / "experiments").exists()               # untouched


def test_corruption_retry_capped(tmp_path, monkeypatch):
    (tmp_path / "experiments").mkdir()
    import subprocess
    msg = ["RuntimeError: The trailblaze algorithm was interrupted while writing the checkpoint file and "
           "it is now unable to resume.\n"]
    exp = tmp_path / "experiments"
    calls = {"n": 0}

    def fake_popen(cmd, **kw):
        calls["n"] += 1
        exp.mkdir(exist_ok=True)                             # yank rebuilds experiments/ each run, then fails
        return _FakePopen(list(msg), 1)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    # corrupt on every attempt → after max_restarts=2 (two retries) it must give up, not loop forever
    rc = fep._run_yank_resilient("nr4a1", str(tmp_path / "exp.yaml"), str(tmp_path))
    assert rc == 1
    assert calls["n"] == 3                                   # initial + exactly two retries (max_restarts=2)
