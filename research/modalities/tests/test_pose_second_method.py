"""Unit tests for `pose_second_method` — the scoring-independent second opinion on the pose.

The load-bearing assertions here are not the arithmetic. They are the four ways this module could
silently stop being what it claims to be:

  · **it could quietly become a criterion of its own.** `C14` is cited by BOTH `R5` and `R14`; the same
    2.0 A line produces `V3`'s INCONCLUSIVE and `V21`'s `panel_readable: false`. A second method that
    defined its own bands would look like corroboration while grading a different question. So every
    threshold it uses must be IMPORTED from `apo_pose_recovery`, and that is asserted by identity.
  · **it could stop being independent.** The whole point is the `V14` trap: BioEmu was orthogonal in its
    SAMPLING and shared the `C1`-`C5` detector chain, so a shared item moved both numbers together. The
    per-arm shared/unshared declaration must therefore stay honest and complete.
  · **it could reach into the pre-registered panel.** The hook must be OFF by default, must be invisible
    to `verdict()`, and must not be able to turn a NOT RECOVERED into a pass.
  · **it could re-align the ligands**, which would report ~0 A for two poses in different pockets and
    make any two methods look like they agree.
"""
import inspect
import os

import pytest

import apo_pose_recovery as APR
import pose_second_method as P


# ------------------------------------------------------------------ C14: imported, never redefined

def test_no_threshold_is_defined_in_this_module():
    """★ THE ONE THAT MATTERS. `C14` is frozen and shared by `R5` and `R14`; a second method that
    invented its own recovery line would repair a failing panel by lowering its own bar."""
    c = P.criterion()
    assert c["recovered_A"] is APR.RECOVER_RMSD_A
    assert c["partial_A"] is APR.PARTIAL_RMSD_A
    assert c["secondary_fnat"] is APR.FNAT_SUCCESS
    assert c["n_null"] is APR.N_NULL
    assert c["null_power_max"] is APR.NULL_POWER_MAX


def test_module_source_declares_no_rmsd_threshold_constant():
    """A literal 2.0/4.0 anywhere in this module's constants would be a second home for `C14`."""
    src = inspect.getsource(P)
    for banned in ("RECOVER_RMSD_A =", "PARTIAL_RMSD_A =", "FNAT_SUCCESS ="):
        assert banned not in src, "%s must live in apo_pose_recovery, not here" % banned


def test_band_is_the_pre_registered_banding():
    assert P.band(APR.RECOVER_RMSD_A - 0.01) == "RECOVERED"
    assert P.band(APR.RECOVER_RMSD_A) == "RECOVERED"
    assert P.band(APR.PARTIAL_RMSD_A) == "PARTIAL"
    assert P.band(APR.PARTIAL_RMSD_A + 0.01) == "NOT RECOVERED"
    assert P.band(None) is None


def test_partial_is_not_recovery_in_the_vocabulary():
    """The exact confusion this task was written to end: 3.142 A is PARTIAL, not 'the docking is fine'."""
    assert P.band(3.142) == "PARTIAL"
    assert P.criterion()["_vocabulary"].startswith("RECOVERED")
    assert "PARTIAL IS NOT RECOVERY" in P.criterion()["_vocabulary"]


# ------------------------------------------------------------------ the search volume is DERIVED

def test_site_matched_radius_is_half_the_pipeline_box_and_not_typed():
    r = P.site_matched_radius_A()
    p = APR.pipeline_dock_params()
    assert abs(r - max(float(p[k]) for k in ("size_x", "size_y", "size_z")) / 2.0) < 1e-9
    assert "SITE_MATCHED_RADIUS" not in inspect.getsource(P)


# ------------------------------------------------------------------ the independence declaration

def test_every_arm_declares_its_shared_and_unshared_configuration():
    for arm, decl in P.C_ITEMS_BY_ARM.items():
        assert set(decl) == {"REQUIRED", "AVOIDABLE", "NOT SHARED"}, arm
        # C14 and C15 are shared on purpose in EVERY arm — they are the yardstick, not the instrument.
        assert "C14" in decl["REQUIRED"], arm
        assert "C15" in decl["REQUIRED"], arm
        seen = set(decl["REQUIRED"]) | set(decl["AVOIDABLE"]) | set(decl["NOT SHARED"])
        assert not (set(decl["AVOIDABLE"]) & set(decl["NOT SHARED"])), arm
        assert len(seen) >= 5, arm


def test_the_receptor_wide_arm_shares_no_site_configuration():
    """★ THE ARM THAT MAKES THE INDEPENDENCE CLAIM CONCRETE. If `C5` ever appears anywhere but NOT
    SHARED here, this arm has stopped being the one that owes nothing to the pipeline's site step."""
    decl = P.C_ITEMS_BY_ARM["receptor_wide"]
    assert decl["AVOIDABLE"] == {}
    for item in ("C1", "C2", "C3", "C4", "C5"):
        assert item in decl["NOT SHARED"], item


def test_the_site_matched_arm_admits_that_it_shares_C5():
    """It is honest about the one it does share; a declaration that claimed full independence in the
    arm where the site is HANDED OVER would be exactly the `V14` over-read."""
    decl = P.C_ITEMS_BY_ARM["site_matched"]
    assert "C5" in decl["AVOIDABLE"]
    for item in ("C1", "C2", "C3", "C4"):
        assert item in decl["NOT SHARED"], item


def test_the_fpocket_arm_shares_C4_and_only_C4():
    """`apo_pose_recovery.fpocket_boxes` ranks by fpocket's own druggability — it applies neither `C1`'s
    D*, nor `C2`'s match rule, nor `C3`'s acceptance gate. Verified in source, not asserted in prose."""
    decl = P.C_ITEMS_BY_ARM["fpocket_box"]
    assert set(decl["AVOIDABLE"]) == {"C4"}
    src = inspect.getsource(APR.fpocket_boxes)
    assert "D_STAR" not in src and "match_pocket" not in src
    assert "druggability" in src


def test_C6_is_declared_as_a_receptor_property_not_an_engine_one():
    assert "C6" in P.C6_NOTE and "8XTT" in P.C6_NOTE and "CONTESTED" in P.C6_NOTE


# ------------------------------------------------------------------ the hook cannot reach the verdict

def test_hook_is_off_by_default():
    assert APR.SECOND_METHOD_HOOK is None


def test_verdict_reads_only_arms_and_the_null():
    """★ NO ADDED ARM MAY TURN A `NOT RECOVERED` INTO A PASS. Held by reading `verdict`'s own source:
    it must not mention the key the hook writes into."""
    src = inspect.getsource(APR.verdict)
    assert "second_method" not in src
    assert 'res.get("arms")' in src


def test_verdict_is_unchanged_by_a_second_method_block():
    base = {"arms": {"PRIMARY_blind_apo_pipeline_box": {"rmsd_A": 19.3},
                     "C1_self_dock_holo": {"rmsd_A": 19.5}},
            "C2_random_in_box_null": {"p_within_criterion": 0.0}}
    with_block = dict(base, second_method={"arms": {"anything": {"rmsd_A": 0.1, "verdict": "RECOVERED"}}})
    assert APR.verdict(base)["outcome"] == APR.verdict(with_block)["outcome"] == "INCONCLUSIVE"


def test_hook_failure_is_recorded_not_raised():
    """An exception inside the second method may never take down a pre-registered pair."""
    src = inspect.getsource(APR.run_benchmark)
    i = src.find("SECOND_METHOD_HOOK is not None")
    assert i > 0, "the hook call is gone"
    assert "except Exception" in src[i:i + 1200]
    assert src.find("SECOND_METHOD_HOOK is not None") < src.find('R_["verdict"] = verdict(R_)')


def test_hook_without_tools_returns_a_named_refusal():
    P._HOOK_STATE["tools"] = None
    got = P.second_method_hook({"cand": {}, "work": "/nonexistent"})
    assert got["_status"].startswith("UNRUN")


# ------------------------------------------------------------------ the RMSD primitive must not align

def test_in_frame_rmsd_measures_placement_not_shape():
    """A translated copy is 10 A away and must read as 10 A. `GetBestRMS` would say 0 and would make any
    two methods agree perfectly no matter where they put the molecule."""
    Chem = pytest.importorskip("rdkit.Chem")
    AllChem = pytest.importorskip("rdkit.Chem.AllChem")
    import pose_convergence_401 as PC
    m = Chem.AddHs(Chem.MolFromSmiles("CCOc1ccccc1"))
    assert AllChem.EmbedMolecule(m, randomSeed=11) == 0
    m = Chem.RemoveHs(m)
    moved = PC.transformed_copy(m, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], (10.0, 0.0, 0.0))
    rms, why = P.in_frame_rmsd(moved, m)
    assert why is None and abs(rms - 10.0) < 1e-6
    assert P.internal_rmsd(moved, m)[0] < 1e-3


# ------------------------------------------------------------------ the ligand is not seeded with the answer

def test_the_second_method_starts_from_a_fresh_conformer_not_the_pose():
    Chem = pytest.importorskip("rdkit.Chem")
    AllChem = pytest.importorskip("rdkit.Chem.AllChem")
    import tempfile
    m = Chem.AddHs(Chem.MolFromSmiles("CCCCOc1ccccc1C(=O)O"))
    assert AllChem.EmbedMolecule(m, randomSeed=7) == 0
    m.SetProp("_Name", "probe")
    with tempfile.TemporaryDirectory() as d:
        out, why = P._ligand_from_pose(m, os.path.join(d, "lig.sd"))
        assert why is None and os.path.exists(out)
        fresh = [x for x in Chem.SDMolSupplier(out, removeHs=True) if x is not None][0]
        # same molecule …
        assert Chem.MolToSmiles(fresh) == Chem.MolToSmiles(Chem.RemoveHs(m))
        # … and NOT the same coordinates, or the search would start inside the answer
        rms, _ = P.in_frame_rmsd(fresh, Chem.RemoveHs(m))
        assert rms is None or rms > 0.05


# ------------------------------------------------------------------ the confound is read from source

def test_pipeline_box_confound_names_the_transfer_and_the_regime():
    """★ POINT 4. If the pipeline's box is NR4A3's Pocket-5 dragged across by sequence alignment, then
    it missing a distant receptor's canonical site is close to EXPECTED — and that has to be established
    before any site number is interpreted, from the code, not from memory."""
    import nr4a3_8xtt_benchmark as bm
    import nr4a3_warhead as wh
    c = P.pipeline_box_confound()
    assert c["site_definition_C5"]["pocket5_lining_uniprot_Q92570"] == list(bm.POCKET5)
    assert c["transfer_kernel"]["function"] == "nr4a3_warhead.map_pocket_to_paralogue"
    assert c["regime"]["proteins_the_pipeline_actually_transfers_onto"] == sorted(wh.PARALOGUES)
    assert "OUT OF THE PIPELINE'S REGIME" in c["regime"]["_reads"]
    read = {r["function"]: r for r in c["_verified_by_reading"]}
    assert read["nr4a3_warhead.map_pocket_to_paralogue"].get("uses_pairwise_sequence_alignment") is True
    assert read["nr4a3_warhead.pocket_box"].get("centroid_of_CA") is True


# ------------------------------------------------------------------ the panel is read, not re-sourced

def test_panel_pool_is_read_from_the_committed_artifact():
    pool, why = P.panel_pool()
    if pool is None:
        pytest.skip(why)
    assert len(pool) >= 2
    assert all("apo" in c and "holo" in c for c in pool)


# ------------------------------------------------------------------ rollup arithmetic and vocabulary

def _fake_pair(apo, holo, ceiling, pipeline, fpocket, oracle, wide, inter=None, fit=None):
    return {"apo": apo, "holo": holo, "protein": "X", "induced_fit": fit or {},
            "second_method": {
                "arms": {
                    "C1c_self_dock_holo_oracle_box": {"rmsd_A": ceiling},
                    "blind_apo_pipeline_box": {"rmsd_A": pipeline, "verdict": P.band(pipeline)},
                    "blind_apo_fpocket_top_box": {"rmsd_A": fpocket, "verdict": P.band(fpocket)},
                    "C3_oracle_box_apo": {"rmsd_A": oracle, "verdict": P.band(oracle)},
                    "receptor_wide_own_cavity_apo": {"rmsd_A": wide, "verdict": P.band(wide)}},
                "cross_method": {"by_arm": {"C3_oracle_box_apo": {"inter_method_rmsd_A": inter}}}}}


def test_rollup_applies_the_inherited_ceiling_rule():
    """A pair whose own ceiling misses cannot grade the docking — the pre-registered C1/C1c logic. If it
    were counted anyway, a negative would be manufactured out of an untestable pair."""
    pairs = [_fake_pair("A", "B", 0.5, 1.2, 3.5, 1.9, 8.0, inter=1.1),
             _fake_pair("C", "D", 9.9, 1.0, 1.0, 1.0, 1.0, inter=2.0)]
    r = P._panel_rollup(pairs)
    assert r["n_pairs"] == 2 and r["n_with_ceiling"] == 2 and r["n_gradeable"] == 1
    b = r["bands_over_gradeable_pairs"]
    assert b["blind_apo_pipeline_box"]["RECOVERED"] == 1
    assert b["blind_apo_fpocket_top_box"]["PARTIAL"] == 1
    assert b["receptor_wide_own_cavity_apo"]["NOT RECOVERED"] == 1
    # the ungradeable pair contributes to NOTHING in the band counts
    assert sum(sum(v.values()) for v in b.values()) == 4


def test_rollup_inter_method_spread_counts_every_pair_gradeable_or_not():
    """Inter-method agreement is a fact about the two engines and does not need a known answer, so it is
    NOT filtered by the ceiling rule — and the artifact must not silently apply one."""
    pairs = [_fake_pair("A", "B", 0.5, 1.2, 3.5, 1.9, 8.0, inter=1.1),
             _fake_pair("C", "D", 9.9, 1.0, 1.0, 1.0, 1.0, inter=5.0)]
    r = P._panel_rollup(pairs)
    assert r["inter_method_rmsd_A"]["n"] == 2
    assert r["inter_method_bands"]["RECOVERED"] == 1
    assert r["inter_method_bands"]["NOT RECOVERED"] == 1


# ------------------------------------------------------------------ induced fit: point 5

def test_induced_fit_panel_states_the_limitation_even_when_a_large_pair_exists():
    pairs = [_fake_pair("A", "B", 0.5, 1, 1, 1, 1,
                        fit={"site_ca_rmsd_A": 0.142, "global_ca_rmsd_A": 0.457, "n_site": 9,
                             "large_rearrangement": False}),
             _fake_pair("C", "D", 0.5, 1, 1, 1, 1,
                        fit={"site_ca_rmsd_A": 6.46, "global_ca_rmsd_A": 2.775, "n_site": 22,
                             "large_rearrangement": True})]
    f = P.induced_fit_panel(pairs)
    assert f["n_pairs"] == 2 and f["n_with_large_rearrangement"] == 1
    assert f["panel_contains_a_large_rearrangement"] is True
    assert f["site_ca_rmsd_A"]["min"] == 0.142 and f["site_ca_rmsd_A"]["max"] == 6.46
    assert "WEAK TEST" in f["_limitation"]
    assert f["_threshold_A"] is APR.LARGE_INDUCED_FIT_A


def test_induced_fit_panel_says_so_when_nothing_rearranges():
    pairs = [_fake_pair("A", "B", 0.5, 1, 1, 1, 1,
                        fit={"site_ca_rmsd_A": 0.142, "large_rearrangement": False, "n_site": 9})]
    f = P.induced_fit_panel(pairs)
    assert f["panel_contains_a_large_rearrangement"] is False
    assert "limitation of the TEST" in f["_limitation"]


# ------------------------------------------------------------------ the verdict cannot over-claim

def test_verdict_never_says_the_pose_is_correct():
    doc = {"part_a": {"cross_method_same_frame": {
        "n_systems": 6, "bands": {"RECOVERED": 6, "PARTIAL": 0, "NOT RECOVERED": 0},
        "rmsd_A": {"median": 0.8}}}}
    v = P.verdict(doc)
    assert v["outcome"].startswith("TWO METHODS AGREE")
    assert v["R5_resolved"] is False
    assert "NOT CORRECTNESS" in v["sentence"]
    assert any("correct" in s for s in v["what_this_does_not_license"])
    assert any("binds" in s for s in v["what_this_does_not_license"])


def test_verdict_calls_a_partial_only_result_partial():
    doc = {"part_a": {"cross_method_same_frame": {
        "n_systems": 4, "bands": {"RECOVERED": 1, "PARTIAL": 3, "NOT RECOVERED": 0},
        "rmsd_A": {"median": 3.1}}}}
    v = P.verdict(doc)
    assert v["outcome"] == "PARTIAL AGREEMENT ONLY — NOT RECOVERY"
    assert "PARTIAL IS NOT RECOVERY" in v["sentence"]


def test_verdict_reports_what_would_resolve_R5_even_on_a_disagreement():
    doc = {"part_a": {"cross_method_same_frame": {
        "n_systems": 6, "bands": {"RECOVERED": 0, "PARTIAL": 1, "NOT RECOVERED": 5},
        "rmsd_A": {"median": 6.7}}}}
    v = P.verdict(doc)
    assert v["outcome"] == "THE TWO METHODS DISAGREE"
    assert v["R5_resolved"] is False
    items = [i["item"] for i in v["what_would_resolve_R5"]]
    assert any("induced" in i or "rearrangement" in i for i in items)
    assert any("co-fold" in i for i in items)


def test_verdict_says_still_none_when_the_second_method_did_not_run():
    v = P.verdict({"part_a": {"cross_method_same_frame": {"n_systems": 0, "bands": {}}}})
    assert v["outcome"] == "UNRUN"
    assert "STILL NONE" in v["cross_method_evidence"]


# ------------------------------------------------------------------ the decomposition reads honestly

def test_decompose_calls_a_flip_a_flip():
    """A large RMSD at a small centroid separation is the 'right place, backwards' failure, and the
    scale it is read against is the molecule's OWN measured flip cost, not a chosen threshold."""
    cm = {"rmsd_A": {"median": 6.8}, "centroid_distance_A": {"median": 1.5},
          "internal_conformer_rmsd_A": {"median": 1.4}}
    d = P._decompose(cm, {"flip_rmsd_A": 6.84, "random_reorient_mean_A": 5.11, "length_A": 10.4})
    assert "SAME LOCATION, DIFFERENT ORIENTATION" in d["_reads"]
    assert "conformer is NOT the explanation" in d["_reads"]


def test_decompose_calls_a_different_pocket_a_different_pocket():
    cm = {"rmsd_A": {"median": 12.0}, "centroid_distance_A": {"median": 11.0},
          "internal_conformer_rmsd_A": {"median": 1.0}}
    d = P._decompose(cm, {"flip_rmsd_A": 6.84, "random_reorient_mean_A": 5.11, "length_A": 10.4})
    assert "DIFFERENT LOCATION" in d["_reads"]


# ------------------------------------------------------------------ tooling refusals are named

def test_missing_tools_is_a_named_refusal_not_a_crash(monkeypatch):
    monkeypatch.setenv("RDOCK_ROOT", "/definitely/not/here")
    monkeypatch.setattr(P.shutil, "which", lambda *_a, **_k: None)
    tools, why = P.rdock_tools()
    assert tools is None
    assert "rbcavity" in why and "rbdock" in why and "UNRUN" in why


def test_cavity_parser_reads_rdock_own_output_format():
    """rbcavity prints `Vol=1376.88 A^3` — the unit is inside the token, and a naive float() of it
    raises, which would silently drop the volume from every row."""
    import types
    sample = ("DOCKING SITE\nTotal volume 1376.88 A^3\n"
              "Cavity #1\tSize=11015 points; Vol=1376.88 A^3; Min=(-22,-0.5,-27); "
              "Max=(1,21.5,-6); Center=(-11.5232,11.0842,-16.7371); Extent=(23,22,21)\n")

    def fake_run(*_a, **_k):
        return types.SimpleNamespace(stdout=sample, stderr="")

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        prm = os.path.join(d, "rec.prm")
        open(prm, "w").write("x")
        open(prm[:-4] + ".as", "w").write("y")
        real = P.subprocess.run
        P.subprocess.run = fake_run
        try:
            info, why = P.make_cavity(prm, {"rbcavity": "x", "env": {}}, d)
        finally:
            P.subprocess.run = real
    assert why is None
    assert info["n_cavities"] == 1
    assert info["cavity_volume_A3"] == 1376.88
    assert info["total_volume_A3"] == 1376.88
    assert info["cavity_center"] == [-11.523, 11.084, -16.737]
