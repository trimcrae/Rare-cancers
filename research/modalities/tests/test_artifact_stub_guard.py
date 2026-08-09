"""The publish guard that ends the `main`-cites-a-stub failure (CLAUDE.md §7 harm #1).

Pins two things: what counts as a stub, and — the load-bearing half — that the three artifacts the
2026-08-03 port brought onto `main` are NOT classified as stubs, so a future edit to the heuristic
cannot quietly stop publishing them.
"""

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

from artifact_stub_guard import is_stub, stage  # noqa: E402


def _w(tmp_path, name, obj):
    p = tmp_path / name
    p.write_text(json.dumps(obj))
    return str(p)


def test_all_meta_keys_is_a_stub(tmp_path):
    # the exact shape that was committed on main as emc-fet-idr-census.json
    p = _w(tmp_path, "census.json", {
        "_status": "sequences missing, cannot compute: ['TAF15', 'FUS']",
        "_remedy": "run with --refresh from CI",
    })
    assert is_stub(p)


def test_any_data_key_is_not_a_stub(tmp_path):
    assert not is_stub(_w(tmp_path, "real.json", {"_what": "x", "depmap_release": "24Q4"}))


def test_empty_object_and_unparseable_are_stubs(tmp_path):
    assert is_stub(_w(tmp_path, "empty.json", {}))
    trunc = tmp_path / "trunc.json"
    trunc.write_text('{"a": ')
    assert is_stub(str(trunc))


def test_non_json_and_json_arrays_are_never_stubs(tmp_path):
    png = tmp_path / "chart.png"
    png.write_bytes(b"\x89PNG\r\n")
    assert not is_stub(str(png))
    assert not is_stub(_w(tmp_path, "arr.json", [1, 2, 3]))


@pytest.mark.committed_artifact
def test_the_ported_artifacts_are_publishable():
    for name in ("fet-ddr-axis-scan.json", "emc-fet-idr-census.json", "fet-sequences-cache.json"):
        p = os.path.join(MOD, name)
        assert os.path.exists(p), f"{name} must be committed on this branch, not only on modalities-cache"
        assert not is_stub(p), f"{name} is a stub — a document citing it would be citing nothing"


def test_stage_drops_stubs_and_keeps_the_rest(tmp_path):
    good = _w(tmp_path, "good.json", {"n": 1})
    bad = _w(tmp_path, "bad.json", {"_status": "failed"})
    dest = tmp_path / "res"
    kept, dropped = stage([good, bad, str(tmp_path / "never-ran.json")], str(dest))
    assert kept == [good] and dropped == [bad]
    assert os.listdir(dest) == ["good.json"]


# ⛔ THE INCIDENT THIS PAIR EXISTS FOR (2026-08-09). A figure-provenance stamp living under
# research/manuscripts/figures/ was added to a workflow's stage list. Staging is FLAT and the
# publishers rebuild each destination from the basename alone, so it was committed to
# research/modalities/figure-provenance.json while the stamp its test reads went untouched. Every
# step reported success and the build stayed red for a reason that looked unrelated to the change
# that caused it.
def test_a_path_the_publishers_cannot_deliver_is_refused_rather_than_misfiled(tmp_path):
    """The refusal must fire on the shape of the real mistake, not on a contrived one."""
    good = _w(tmp_path, "good.json", {"n": 1})
    with pytest.raises(SystemExit) as exc:
        stage([good], str(tmp_path / "res"), publishable_root="research/modalities")
    msg = str(exc.value)
    assert "REFUSING TO STAGE" in msg and good in msg, (
        "the refusal must NAME the offending path — a build failure that does not say which entry "
        "is wrong sends the reader back to the same guesswork the misfile already caused")


def test_the_refusal_is_opt_in_so_the_copy_itself_stays_unit_testable(tmp_path):
    """⚠ THE FIRST VERSION HARDCODED THE ROOT INTO stage() AND BROKE A LEGITIMATE TEST.

    Every unit test here stages from tmp_path, which is by construction not under the repo's publish
    directory. A guard that makes its own function untestable is too rigid to be correct, so the
    constraint lives at the CLI boundary the workflow actually calls and defaults OFF here.
    """
    good = _w(tmp_path, "good.json", {"n": 1})
    kept, dropped = stage([good], str(tmp_path / "res"))
    assert kept == [good] and dropped == []
