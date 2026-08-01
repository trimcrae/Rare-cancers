"""THE PRUNE THAT KILLS THE O(n²) — pinned where it actually runs, on the live commit path.

`chk_prune` is the one home of the arithmetic that `chk_prune_roundtrip` proved (GH 30676071569: a pruned
`.chk` keeps the reader's index, returns bit-identical coordinates, is accepted by the UNMODIFIED
commit/restore path, resumes, runs on and chains; 25.88× on a real committed 5a-KS pair).

What is pinned here is everything that decides whether it is SAFE to have that on a path that a billing leg
depends on, because the netCDF half cannot run in the sandbox:

  * the switch is OFF by default and read at CALL time, so a leg already in flight is unaffected by this
    landing mid-run as a property of the code, not a promise about sequencing;
  * the prune never opens the source for writing, and `commit()` hands it a SNAPSHOT, so the worst a bug
    can do is a bad upload;
  * the pruned bytes are VALIDATED before they are adopted, and any failure keeps the unpruned snapshot —
    an optimisation may never cost a commit, which is the only thing standing between a preemption and lost
    GPU hours;
  * the chunk arithmetic puts one iteration per chunk, which IS the mechanism by which an unwritten frame
    costs no storage.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chk_prune as cp  # noqa: E402
import rbfe_spot_checkpoint as spot  # noqa: E402


# ---------------------------------------------------------------------------------------------
# the switch: OFF unless a dispatch asks, and never frozen at import
# ---------------------------------------------------------------------------------------------
def test_pruning_is_OFF_by_default():
    """The four 5a-KS legs in flight when this landed must be unaffected. Default-off makes that a fact
    about the code rather than a claim about who dispatched what."""
    assert cp.prune_enabled({}) is False
    assert cp.prune_enabled({"RBFE_PRUNE_CHK": ""}) is False
    assert cp.prune_enabled({"RBFE_PRUNE_CHK": "0"}) is False


@pytest.mark.parametrize("v", ["1", "true", "TRUE", "yes"])
def test_the_switch_turns_it_on(v):
    assert cp.prune_enabled({"RBFE_PRUNE_CHK": v}) is True


def test_the_switch_is_read_at_call_time_not_cached_at_import():
    """A value frozen by whoever imported the module first cannot be flipped by a single dispatch — and
    would make the default-off guarantee untestable."""
    src = open(cp.__file__).read()
    body = src[src.index("def prune_enabled"):src.index("# ------", src.index("def prune_enabled"))]
    assert "os.environ if env is None" in body


def test_commit_consults_the_switch_and_prunes_only_the_SNAPSHOT():
    """Source-text pin on the wiring: the prune must sit AFTER the two copy2 calls (so it is operating on
    the temp-dir snapshot) and BEFORE validate_reporter_pair (so a bad prune fails the commit rather than
    being persisted)."""
    src = open(spot.__file__).read()
    body = src[src.index("    def commit(self"):src.index("    def _persist(self")]
    i_copy = body.index("shutil.copy2(chk_path, snap_chk)")
    i_prune = body.index("prune_snapshot(snap_chk")
    i_valid = body.index("validate_reporter_pair(snap_nc, snap_chk")
    assert i_copy < i_prune < i_valid
    assert "prune_enabled()" in body
    assert "prune_snapshot(chk_path" not in body, "the LIVE reporter file must never be pruned"


def test_the_manifest_records_whether_a_generation_was_pruned():
    """A pruned generation and an unpruned one are indistinguishable by size once the interval changes, so
    a restore that cannot say which it is holding cannot diagnose anything about it later."""
    src = open(spot.__file__).read()
    body = src[src.index("    def commit(self"):src.index("    def _persist(self")]
    assert 'manifest["chk_pruned"]' in body


# ---------------------------------------------------------------------------------------------
# fail-safe: an optimisation may never cost a commit
# ---------------------------------------------------------------------------------------------
def test_prune_snapshot_never_raises(tmp_path):
    """Handed something that is not a netCDF file at all, it must report the failure and return — the
    caller then commits the unpruned snapshot exactly as before."""
    bad = tmp_path / "warmup.chk"
    bad.write_bytes(b"not a netcdf file")
    said = []
    out = cp.prune_snapshot(bad, log=said.append)
    assert out["pruned"] is False and "error" in out
    assert any("SKIPPED" in m for m in said), "a silent skip is how an optimisation stops being auditable"


def test_a_failed_prune_leaves_the_snapshot_byte_identical(tmp_path):
    bad = tmp_path / "warmup.chk"
    bad.write_bytes(b"not a netcdf file")
    before = bad.read_bytes()
    cp.prune_snapshot(bad, log=lambda *_: None)
    assert bad.read_bytes() == before


def test_a_failed_prune_leaves_no_temporary_behind(tmp_path):
    """`commit()` persists what is in the temp dir; a stray `prune-*.chk` would be uploaded alongside the
    real one."""
    bad = tmp_path / "warmup.chk"
    bad.write_bytes(b"not a netcdf file")
    cp.prune_snapshot(bad, log=lambda *_: None)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["warmup.chk"]


def test_the_pruned_bytes_are_validated_before_they_are_adopted():
    """Source-text pin: `os.replace` must come AFTER `validate_reporter_pair`, or a bad prune would be
    adopted and the outer validation would fail the whole commit instead of falling back."""
    src = open(cp.__file__).read()
    body = src[src.index("def prune_snapshot"):]
    assert body.index("validate_reporter_pair") < body.index("os.replace(tmp, snap_chk)")


def test_prune_snapshot_operates_in_place_on_a_path_the_caller_owns():
    src = open(cp.__file__).read()
    body = src[src.index("def prune_snapshot"):]
    assert "os.replace(tmp, snap_chk)" in body, "the result must land at the snapshot's own path"


# ---------------------------------------------------------------------------------------------
# the chunk arithmetic IS the mechanism
# ---------------------------------------------------------------------------------------------
def test_chunking_puts_exactly_one_iteration_per_chunk():
    ch = cp._chunk_for((25, 12, 147788, 3), 4)
    assert ch[0] == 1, "a chunk spanning >1 iteration would materialise frames we are trying to drop"


def test_a_chunk_is_kept_under_the_budget_at_the_real_shape():
    ch = cp._chunk_for((25, 12, 147788, 3), 4, budget_bytes=8 << 20)
    n = 4
    for c in ch:
        n *= c
    assert n <= (8 << 20), f"chunk {ch} = {n} B exceeds the budget"
    assert ch[-2:] == (147788, 3), "the trailing (atom, spatial) axes must stay contiguous for read speed"


def test_source_chunking_is_preserved_apart_from_the_iteration_axis():
    assert cp._chunk_for((25, 12, 100, 3), 4, src_chunking=(5, 6, 50, 3)) == (1, 6, 50, 3)


def test_no_chunk_for_a_scalar():
    assert cp._chunk_for((), 4) is None


# ---------------------------------------------------------------------------------------------
# netCDF4 is not uniform across variable kinds — the bug that killed the first run (GH 30674942072)
# ---------------------------------------------------------------------------------------------
class _FakeVar:
    def __init__(self, dtype, chunking=None, filters=None):
        self.dtype = dtype
        self._chunking, self._filters = chunking, filters

    def chunking(self):
        if self._chunking is None:
            raise RuntimeError("not chunked")
        return self._chunking

    def filters(self):
        if self._filters is None:
            raise RuntimeError("no filters")
        return self._filters


def test_a_VLEN_string_variable_is_recognised_as_one():
    """openmmtools checkpoints carry a VLEN `str` variable (`timestamp`) whose `dtype` is the Python TYPE,
    not a numpy dtype. Treating it as numeric asked netCDF4 for compression and chunking it cannot do, and
    killed the prune four lines in."""
    assert cp._is_vlen(_FakeVar(str))
    assert not cp._is_vlen(_FakeVar("f4"))


def test_itemsize_survives_a_dtype_that_is_not_a_numpy_dtype():
    assert cp._itemsize("f4") == 4
    assert cp._itemsize("f8") == 8
    assert cp._itemsize(str) >= 1          # must not raise — that was the exact crash
    assert cp._itemsize(object(), default=8) == 8


def test_chunking_and_filters_report_None_rather_than_raising():
    v = _FakeVar("f4")
    assert cp._chunking(v) is None
    assert cp._filters(v) == {}
    assert cp._chunking(_FakeVar("f4", chunking=[1, 2])) == [1, 2]


# ---------------------------------------------------------------------------------------------
# it must be unable to touch a live reporter file
# ---------------------------------------------------------------------------------------------
def test_the_prune_opens_the_source_read_only():
    """There is no cheap runtime assertion for 'did not write to the file I was given', and the
    consequence of getting it wrong is corrupting a running leg's reporter."""
    src = open(cp.__file__).read()
    body = src[src.index("def prune_to_last_frame"):src.index("def prune_snapshot")]
    assert 'Dataset(str(src_chk), "r")' in body
    assert 'Dataset(str(dst_chk), "w"' in body
    assert '"a"' not in body and '"r+"' not in body


def test_the_module_imports_without_the_MD_stack():
    """It is imported by `rbfe_spot_checkpoint`, which the CPU tests use; a netCDF4 import at module scope
    would drag the MD stack into every one of them."""
    src = open(cp.__file__).read()
    top = src[:src.index("def prune_enabled")]
    assert "import netCDF4" not in top


# ---------------------------------------------------------------------------------------------
# the switch has to reach a rented host, and it has to reach it OFF unless asked
# ---------------------------------------------------------------------------------------------
def test_the_launcher_defaults_the_switch_to_off():
    """`TVAST_PRUNE_CHK` unset must put `RBFE_PRUNE_CHK=0` in every leg's environment, whatever the mode."""
    import ternary_vast_launch as tv
    for m in list(tv.MODES) + ["a_mode_that_does_not_exist"]:
        assert tv.prune_chk_for_mode(m, {}) == "0"
        assert tv.prune_chk_for_mode(m, {"TVAST_PRUNE_CHK": "0"}) == "0"


# ---------------------------------------------------------------------------------------------
# ★★ THE LADDER GATE — the promise that four irreplaceable legs are untouched, made testable
# ---------------------------------------------------------------------------------------------
def test_the_switch_alone_cannot_reach_the_live_production_mode():
    """⚠ THE REASON THIS EXISTS. The switch reaches the lane as a REPOSITORY VARIABLE (the lane is at
    GitHub's 10-input cap so it cannot be a dispatch input), and a repository variable is GLOBAL to every
    run. This lane also SELF-DISPATCHES — `5aks-gate` fires `task=5aks` the moment the board clears, which
    re-places a stranded leg, and that leg RESUMES. So "set the variable for one experiment" is not
    something the switch alone can express: with the variable set, a gate firing overnight would have put a
    second change onto legs at 94/64/51/49 %. The allowlist is what makes the promise hold without
    depending on nobody dispatching the wrong task."""
    import ternary_vast_launch as tv
    assert tv.prune_chk_for_mode("5aks", {"TVAST_PRUNE_CHK": "1"}) == "0"
    assert tv.prune_chk_for_mode("5aks_smoke", {"TVAST_PRUNE_CHK": "1"}) == "1"


def test_only_the_shakeout_mode_is_eligible_at_this_rung():
    """CLAUDE.md §6: one variable at a time. Widening this set is a deliberate rung, so it is pinned — if
    a mode is added, this test fails and whoever added it has to say which rung was cleared."""
    import ternary_vast_launch as tv
    assert tv.PRUNE_ELIGIBLE_MODES == ("5aks_smoke",)


def test_no_mode_outside_the_allowlist_can_ever_prune():
    import ternary_vast_launch as tv
    on = {"TVAST_PRUNE_CHK": "1"}
    for m in tv.MODES:
        expected = "1" if m in tv.PRUNE_ELIGIBLE_MODES else "0"
        assert tv.prune_chk_for_mode(m, on) == expected, m


def test_the_jobspec_gets_the_gated_value_not_the_raw_env():
    """A jobspec that read the env directly would bypass the allowlist entirely — which is precisely the
    bug the allowlist exists to prevent, so it is pinned as source text."""
    import ternary_vast_launch as tv
    src = open(tv.__file__).read()
    assert '"RBFE_PRUNE_CHK": prune_chk_for_mode(mode)' in src
    assert '"RBFE_PRUNE_CHK": os.environ.get("TVAST_PRUNE_CHK")' not in src


def test_the_switch_is_forwarded_into_the_leg_command():
    """A variable in the jobspec that the `run_ternary_leg.sh` invocation does not carry is a setting that
    silently does nothing on the host."""
    import ternary_vast_launch as tv
    src = open(tv.__file__).read()
    assert 'RBFE_PRUNE_CHK="$RBFE_PRUNE_CHK"' in src


def test_the_switch_is_a_REPOSITORY_VARIABLE_and_never_a_dispatch_input():
    """★★ MEASURED THE HARD WAY. Adding it as a dispatch input made this lane declare 11, and the 11th does
    not fail — it silently EMPTIES every `-f` value on the lane (test_workflow_dispatch_input_cap, whose
    own docstring lists the three honest options: fold into an existing input, use an env/repo variable, or
    delete one first). `vars.*` costs no input, and unset reads as empty, which is the safe default."""
    import pathlib
    import yaml
    wf = pathlib.Path(__file__).resolve().parents[3] / ".github/workflows/gpu-ternary-fep-vast.yml"
    d = yaml.safe_load(wf.read_text())
    ins = d[True]["workflow_dispatch"]["inputs"]
    assert "prune_chk" not in ins, "this lane has no input headroom — route it through vars.* instead"
    body = wf.read_text()
    assert body.count("TVAST_PRUNE_CHK: ${{ vars.TVAST_PRUNE_CHK }}") >= 7, \
        "every job that launches or prices a leg must forward it, or the setting depends on which job ran"
