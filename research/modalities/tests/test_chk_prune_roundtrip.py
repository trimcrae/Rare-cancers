"""THE RUNG-1 PRUNE EXPERIMENT MUST NOT BE ABLE TO PASS VACUOUSLY.

`chk_prune_roundtrip` decides whether the O(n²) commit fix (`commit-payload-design.md`) is buildable. Its
answer is only worth anything if a *wrong* prune makes it say no, so what is pinned here is the
DISCRIMINATION, not the happy path: the verdict function, the check set, and the chunk arithmetic that is
the entire storage mechanism.

The netCDF/openmmtools halves cannot run in the sandbox (no `netCDF4`, no `openmmtools`) — they run in the
`triskit23/ternary-fep` parity image via CI. Everything asserted below is deliberately pure Python, so the
part that decides "safe / not safe" is under test everywhere, including here.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chk_prune_roundtrip as cpr  # noqa: E402


# ---------------------------------------------------------------------------------------------
# the chunk arithmetic IS the mechanism: one iteration per chunk, or an unwritten frame costs bytes
# ---------------------------------------------------------------------------------------------
def test_chunking_puts_exactly_one_iteration_per_chunk():
    ch = cpr._chunk_for((25, 12, 147788, 3), 4)
    assert ch[0] == 1, "a chunk spanning >1 iteration would materialise frames we are trying to drop"


def test_a_chunk_is_kept_under_the_budget_at_the_real_shape():
    # 1 x 12 x 147788 x 3 x 4 B = 21.3 MiB, over the budget -> the replica axis must be split.
    ch = cpr._chunk_for((25, 12, 147788, 3), 4, budget_bytes=8 << 20)
    n = 4
    for c in ch:
        n *= c
    assert n <= (8 << 20), f"chunk {ch} = {n} B exceeds the budget"
    assert ch[-2:] == (147788, 3), "the trailing (atom, spatial) axes must stay contiguous for read speed"


def test_source_chunking_is_preserved_apart_from_the_iteration_axis():
    ch = cpr._chunk_for((25, 12, 100, 3), 4, src_chunking=(5, 6, 50, 3))
    assert ch == (1, 6, 50, 3)


def test_no_chunk_for_a_scalar():
    assert cpr._chunk_for((), 4) is None


# ---------------------------------------------------------------------------------------------
# the verdict must be driven by the checks, and must refuse when the harness has no power
# ---------------------------------------------------------------------------------------------
def _passing_resume(ci=2, target=8):
    return {
        "checkpoint_interval": ci, "target": target,
        "before": {"iteration_dim": 5, "frames_with_data": [0, 1, 2, 3, 4], "bytes": 1000},
        "after": {"iteration_dim": 5, "frames_with_data": [4], "bytes": 200},
        "restored_chk_report": {"frames_with_data": [4]},
        "shrink_x": 5.0, "naive_prune_rejected": True,
        "pruned_commit_ok": True, "restore_ok": True,
        "from_storage_iteration": target,
        "max_delta_vs_unpruned_resume_nm": 0.0, "max_delta_vs_live_state_nm": 1e-7,
        "replica_state_indices_match": True,
        "interval_readback": ci, "effective_interval": ci,
        "ran_on_from_pruned": True, "chain_restore_ok": True,
        "chain_restored_iteration": target + 2, "chain_from_storage_iteration": target + 2,
        "still_rejects_a_wrong_iteration": True,
    }


def _passing_doc():
    b = _passing_resume()
    return {"storage": {"shrink_chunked_x": 5.9, "checks": {"chunked_saves_about_n_x": True,
                                                            "contiguous_does_NOT_save": True}},
            "resume": b, "resume_checks": cpr.resume_checks(b)}


def test_the_all_green_case_reads_SAFE():
    assert cpr.verdict(_passing_doc()).startswith("PRUNING IS SAFE")


def test_every_single_check_is_load_bearing():
    """Flip each check false in turn; every one must break the verdict. A check nobody consults is worse
    than no check, because it reads as coverage."""
    base = _passing_doc()
    for name in cpr.resume_checks(_passing_resume()):
        doc = dict(base)
        doc["resume_checks"] = dict(base["resume_checks"], **{name: False})
        assert not cpr.verdict(doc).startswith("PRUNING IS SAFE"), f"{name} does not affect the verdict"


def test_a_failed_negative_control_is_INCONCLUSIVE_not_merely_unsafe():
    """If the naive index-0 prune VALIDATED, the validator is not reading the frame — so the good prune's
    pass is meaningless too. That is a different statement from 'pruning is unsafe' and must read as one."""
    b = dict(_passing_resume(), naive_prune_rejected=False)
    doc = {"resume": b, "resume_checks": cpr.resume_checks(b)}
    assert cpr.verdict(doc).startswith("INCONCLUSIVE")


def test_a_storage_probe_failure_also_blocks_SAFE():
    doc = _passing_doc()
    doc["storage"] = dict(doc["storage"], checks={"chunked_saves_about_n_x": False,
                                                  "contiguous_does_NOT_save": True})
    assert not cpr.verdict(doc).startswith("PRUNING IS SAFE")


def test_the_contiguous_control_must_NOT_save_or_the_probe_is_measuring_an_artefact():
    doc = _passing_doc()
    doc["storage"] = dict(doc["storage"], checks={"chunked_saves_about_n_x": True,
                                                  "contiguous_does_NOT_save": False})
    v = cpr.verdict(doc)
    assert not v.startswith("PRUNING IS SAFE")
    assert "contiguous_does_NOT_save" in v


def test_no_resume_data_is_INCONCLUSIVE_rather_than_a_pass():
    assert cpr.verdict({"storage": {}, "resume": {}, "resume_checks": {}}).startswith("INCONCLUSIVE")


# ---------------------------------------------------------------------------------------------
# the specific vacuous-pass shapes the design doc warned about
# ---------------------------------------------------------------------------------------------
def test_keeping_frame_zero_instead_of_the_last_one_fails():
    b = dict(_passing_resume())
    b["after"] = dict(b["after"], frames_with_data=[0])
    assert not cpr.resume_checks(b)["kept_the_LAST_frame"]


def test_a_prune_that_shortens_the_iteration_dimension_fails():
    """The whole design is 'preserve the index, drop the bytes'. A shorter dimension breaks the reader's
    `iteration // checkpoint_interval` arithmetic, which is the load-bearing unknown."""
    b = dict(_passing_resume())
    b["after"] = dict(b["after"], iteration_dim=1)
    assert not cpr.resume_checks(b)["iteration_dim_preserved"]


def test_a_no_op_prune_fails_rather_than_passing_quietly():
    b = dict(_passing_resume(), shrink_x=1.0)
    assert not cpr.resume_checks(b)["actually_smaller"]


def test_resuming_at_iteration_zero_fails():
    b = dict(_passing_resume(), from_storage_iteration=0)
    ck = cpr.resume_checks(b)
    assert not ck["did_NOT_reset_to_zero"] and not ck["resumed_at_the_right_iteration"]


def test_fill_values_coming_back_as_coordinates_fails():
    b = dict(_passing_resume(), max_delta_vs_unpruned_resume_nm=9.97e36,
             max_delta_vs_live_state_nm=9.97e36)
    ck = cpr.resume_checks(b)
    assert not ck["coordinates_identical_to_unpruned_resume"]
    assert not ck["coordinates_are_the_real_state"]


def test_an_absent_coordinate_comparison_is_not_treated_as_a_pass():
    """§4: an absent reading is not a reading of absence. A None delta means the comparison did not happen."""
    b = dict(_passing_resume(), max_delta_vs_unpruned_resume_nm=None)
    assert not cpr.resume_checks(b)["coordinates_identical_to_unpruned_resume"]


def test_losing_the_interval_fails_because_effective_interval_depends_on_it():
    b = dict(_passing_resume(), interval_readback=None)
    assert not cpr.resume_checks(b)["interval_survives"]


def test_a_chain_that_only_restores_the_first_generation_fails():
    """One pruned hop is not the proposal — every generation is pruned, so the SECOND must work too."""
    b = dict(_passing_resume(), chain_restore_ok=False)
    assert not cpr.resume_checks(b)["pruned_CHAIN_restores"]


# ---------------------------------------------------------------------------------------------
# PART D — the real committed pair. Optional, so its ABSENCE must be named rather than assumed passed.
# ---------------------------------------------------------------------------------------------
def test_no_real_pair_means_the_verdict_says_the_real_layout_is_untested():
    """§4: an absent reading is not a reading of absence. A SAFE verdict with no real pair must not read as
    if the 12-replica layout had been checked."""
    v = cpr.verdict(_passing_doc())
    assert v.startswith("PRUNING IS SAFE")
    assert "NOT yet run against a real committed pair" in v


def test_a_real_pair_that_fails_blocks_SAFE_even_when_everything_synthetic_passes():
    doc = dict(_passing_doc())
    doc["real_pairs"] = [{"shrink_x": 24.0, "checks": {"real_pruned_pair_validates": False,
                                                       "real_index_preserved": True}}]
    v = cpr.verdict(doc)
    assert not v.startswith("PRUNING IS SAFE")
    assert "real_pruned_pair_validates" in v


def test_a_passing_real_pair_is_named_in_the_verdict():
    doc = dict(_passing_doc())
    doc["real_pairs"] = [{"shrink_x": 24.0, "checks": {"real_pruned_pair_validates": True}}]
    v = cpr.verdict(doc)
    assert v.startswith("PRUNING IS SAFE") and "1 REAL committed" in v and "24.0x" in v


def test_one_failing_real_pair_among_several_still_blocks():
    doc = dict(_passing_doc())
    doc["real_pairs"] = [{"shrink_x": 24.0, "checks": {"real_index_preserved": True}},
                         {"shrink_x": 22.0, "checks": {"real_index_preserved": False}}]
    assert not cpr.verdict(doc).startswith("PRUNING IS SAFE")


_LISTING = [
    "2026-07-31 01:02:03  1234 ternary-vast/commits/5aks_nr4a3_r0_dt4/warmup/iter-00000064/abc123/COMMITTED.json",
    "2026-07-31 01:02:03  1234 ternary-vast/commits/5aks_nr4a3_r0_dt4/warmup/iter-00001600/def456/COMMITTED.json",
    "2026-07-31 01:02:03  1234 ternary-vast/commits/5aks_nr4a3_r0_dt4/warmup/iter-00001600/def456/warmup.nc",
    "2026-07-31 01:02:03  1234 ternary-vast/commits/5aks_nr4a1_r1_dt4/warmup/iter-00000512/aaa111/COMMITTED.json",
    "2026-07-31 01:02:03  1234 ternary-vast/commits/5aks_nr4a3_r0_dt4/production/iter-00000080/bbb222/COMMITTED.json",
    "2026-07-31 01:02:03  1234 ternary-vast/commits/5aks_smoke_leg/warmup/iter-00000064/ccc333/COMMITTED.json",
]


def test_pair_targets_picks_the_NEWEST_generation_per_leg():
    got = cpr.pair_targets(_LISTING, "s3://bucket/", phase="warmup", limit=5)
    by_label = {t["label"]: t for t in got}
    assert by_label["5aks_nr4a3_r0_dt4"]["iteration"] == 1600, "an older generation would understate the shrink"


def test_pair_targets_ignores_the_wrong_phase():
    """Production `.nc` files are GiB-scale (design doc §1); a runner cannot hold them, and warmup is where
    the O(n²) lives anyway."""
    got = cpr.pair_targets(_LISTING, "s3://bucket/", phase="warmup", limit=5)
    assert all("production" not in t["dir_uri"] for t in got)
    assert cpr.pair_targets(_LISTING, "s3://bucket/", phase="production", limit=5)[0]["iteration"] == 80


def test_pair_targets_excludes_smoke_legs():
    got = cpr.pair_targets(_LISTING, "s3://bucket/", phase="warmup", limit=5)
    assert all("smoke" not in t["label"] for t in got)


def test_pair_targets_builds_the_generation_DIRECTORY_uri_not_the_manifest():
    got = cpr.pair_targets(_LISTING, "s3://bucket/", phase="warmup", limit=1)[0]
    assert got["dir_uri"].endswith("/warmup/iter-00001600/def456")
    assert not got["dir_uri"].endswith("COMMITTED.json")


def test_pair_targets_on_an_empty_listing_returns_nothing_rather_than_raising():
    assert cpr.pair_targets([], "s3://bucket/") == []
    assert cpr.pair_targets(["", "   "], "s3://bucket/") == []


# ---------------------------------------------------------------------------------------------
# the experiment must not be able to touch a live file
# ---------------------------------------------------------------------------------------------
def test_nothing_in_the_module_opens_a_path_for_writing_that_it_did_not_create():
    """`prune_to_last_frame` and `naive_prune` open the SOURCE read-only. Pinned as source text because the
    consequence of getting it wrong is corrupting a running leg's reporter, and there is no cheap runtime
    assertion for 'did not write to the file I was given'."""
    src = open(cpr.__file__).read()
    body = src[src.index("def prune_to_last_frame"):src.index("# PART A")]
    # both writers (the real prune and its negative control) open the SOURCE read-only...
    assert body.count('Dataset(str(src_chk), "r")') == 2
    # ...and only ever open a DESTINATION for writing.
    assert body.count('Dataset(str(dst_chk), "w"') == 2
    assert '"a"' not in body and '"r+"' not in body, "the source must never be opened for writing"


def test_the_module_documents_that_it_rents_nothing():
    assert "$0" in (cpr.__doc__ or "")


def test_the_pruned_copy_snapshots_before_it_prunes():
    """The design prunes `commit()`'s TEMP-DIR SNAPSHOT, never the live reporter. Reading the live file with
    a second HDF5 handle is both unfaithful to that and a way to trip file locking mid-run."""
    src = open(cpr.__file__).read()
    body = src[src.index("def _pruned_copy"):src.index("def resume_semantics")]
    assert "shutil.copy2(chk_path, snap)" in body
    assert "prune_to_last_frame(snap," in body, "the prune must read the snapshot, not the live file"


def test_the_real_pair_probe_validates_a_PRUNED_chk_beside_a_COPIED_nc():
    """⚠ THE VACUOUS-PASS TRAP. `validate_reporter_pair` opens the checkpoint by NAME, resolved next to the
    `.nc`. Pruning into a sibling directory while validating against the ORIGINAL `.nc` would silently
    validate the unpruned checkpoint sitting beside it — a pass that never touched a pruned byte."""
    src = open(cpr.__file__).read()
    body = src[src.index("def real_pair_probe"):src.index("# verdict")]
    assert "p_nc, p_chk = tmp / nc.name, tmp / chk.name" in body
    assert "shutil.copy2(nc, p_nc)" in body
    assert "validate_reporter_pair(nc, p_chk" not in body, \
        "validating the pruned .chk against the ORIGINAL .nc resolves to the UNPRUNED checkpoint"


@pytest.mark.parametrize("mod", ["netCDF4", "openmmtools"])
def test_the_heavy_dependencies_are_imported_lazily(mod):
    """Importing this module must not require the MD stack — the pure half has to be testable everywhere,
    which is what lets the checks above run in ordinary CI."""
    assert mod not in sys.modules or True  # importing cpr above already proves it did not fail
    src = open(cpr.__file__).read()
    top = src[:src.index("REAL_N_REPLICAS")]
    assert f"import {mod}" not in top
