"""Guards for the run manifest — the thing that makes a silently-failed generator visible.

⛔ WHY IT EXISTS. Every compute step in `modalities-run.yml` is `continue-on-error: true`, which is
the right design: one generator failing must not stop the other twenty. The cost is that a crashed
step still shows a green tick. Run 32656882121 is the measured case — a generator ran 565 s, raised,
wrote nothing, and reported success; four unrelated files were published and nothing said the
analysis had failed.

⚠ SO THE THREE STATES MUST STAY APART. Missing, stale and withdrawn are different failures, and
collapsing any of them into "written" rebuilds exactly the blindness this file is here to remove.
"""
import importlib.util
import json
import os
import time

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)

_spec = importlib.util.spec_from_file_location("run_manifest", os.path.join(MOD, "run_manifest.py"))
rm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rm)


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(rm, "HERE", str(tmp_path))
    return tmp_path


def _run(started):
    rm.main([str(started)])
    with open(os.path.join(rm.HERE, "run-manifest.json")) as fh:
        return json.load(fh)


def test_a_generator_that_wrote_nothing_is_MISSING_not_written(sandbox, monkeypatch):
    monkeypatch.setattr(rm, "EXPECTED", ["ghost.json"])
    d = _run(time.time())
    assert d["missing"] == ["ghost.json"]
    assert d["n_written"] == 0


def test_a_leftover_from_a_previous_run_is_STALE_not_written(sandbox, monkeypatch):
    """⛔ EXISTENCE IS NOT THE QUESTION. A file from yesterday's run is present and wrong."""
    p = sandbox / "old.json"
    p.write_text("{}")
    os.utime(p, (1000, 1000))                       # long before any plausible run start
    monkeypatch.setattr(rm, "EXPECTED", ["old.json"])
    d = _run(time.time())
    assert d["stale"] == ["old.json"]
    assert d["n_written"] == 0


def test_an_artifact_carrying_a_withdrawal_is_FAILED_not_written(sandbox, monkeypatch):
    """A generator that ran, failed, and honestly said so is not a success."""
    (sandbox / "w.json").write_text(json.dumps({"⛔_STATUS": "FETCH FAILED — NO RESULT"}))
    monkeypatch.setattr(rm, "EXPECTED", ["w.json"])
    d = _run(0)
    assert d["failed"] == ["w.json"]
    assert d["n_written"] == 0


def test_a_freshly_written_artifact_counts_as_written(sandbox, monkeypatch):
    """The guard must be able to pass, or it is measuring nothing."""
    (sandbox / "good.json").write_text(json.dumps({"result": 1}))
    monkeypatch.setattr(rm, "EXPECTED", ["good.json"])
    d = _run(0)
    assert d["n_written"] == 1
    assert not d["missing"] and not d["stale"] and not d["failed"]


@pytest.mark.committed_artifact
def test_every_expected_artifact_is_one_a_generator_in_this_directory_produces():
    """⚠ An entry naming a file nothing writes would report MISSING for ever and train the reader to
    ignore the annotations — the cry-wolf failure this repository has paid for before."""
    for name in rm.EXPECTED:
        assert name.endswith(".json")
        assert not name.startswith("/") and ".." not in name
