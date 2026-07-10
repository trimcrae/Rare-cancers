"""Unit tests for the consolidated harmonized-detection aggregator (pure)."""
import pocket_tracking as pt
import nr4a3_pocket_reharmonize as rh


def test_detection_from_result_shapes():
    det = pt.detection_report([0.6, 0.4, 0.55], d_star=0.53, n_propagated=20)
    # 8xtt shape
    r8 = {"harmonized_detection": {"match_mode": "harmonized", "fpocket_version": "4.2.3", **det}}
    assert rh.detection_from_result("8xtt", r8)["n_propagated"] == 20
    assert rh.detection_from_result("8xtt", r8)["n_ge_dstar"] == 2
    # mdpocket / metad shape
    rm = {"druggability_timeseries": {"harmonized_detection": {"match_mode": "harmonized", **det}}}
    assert rh.detection_from_result("metad", rm)["n_detected"] == 3
    # af2 static
    ra = {"harmonized_orthosteric_match": {"detection": pt.detection_report([0.5], n_propagated=1)}}
    assert rh.detection_from_result("af2_static", ra)["n_propagated"] == 1
    # release_druggable
    rd = {"harmonized_detection": det}
    assert rh.detection_from_result("release_druggable", rd)["detection_fraction"] == det["detection_fraction"]
    # calibration NR4A3 -> single-frame synthesized
    rc = {"results": [{"id": "NR4A3_AF2_Q92570",
                       "harmonized_pocket5_match": {"matched_druggability": 0.6}}]}
    dc = rh.detection_from_result("calibration_nr4a3", rc)
    assert dc["n_propagated"] == 1 and dc["n_ge_dstar"] == 1


def test_detection_from_result_missing():
    assert rh.detection_from_result("8xtt", None) is None
    assert rh.detection_from_result("8xtt", {}) is None
    assert rh.detection_from_result("unknown_kind", {"x": 1}) is None


def test_pool_detection_sums_counts_and_recomputes_fractions():
    a = pt.detection_report([0.6, 0.4], d_star=0.53, n_propagated=10)     # det 2, ge 1
    b = pt.detection_report([0.55, 0.6, 0.2], d_star=0.53, n_propagated=15)  # det 3, ge 2
    pooled = rh.pool_detection([a, b])
    assert pooled["n_propagated"] == 25
    assert pooled["n_detected"] == 5
    assert pooled["n_ge_dstar"] == 3
    assert pooled["detection_fraction"] == 5 / 25
    assert pooled["frac_ge_among_propagated"] == 3 / 25
    assert rh.pool_detection([]) is None


def test_build_consolidated_table():
    entries = [
        {"ensemble": "af2_static", "kind": "af2_static",
         "result": {"harmonized_orthosteric_match": {"detection": pt.detection_report([0.495], n_propagated=1)}}},
        {"ensemble": "8xtt_20conf", "kind": "8xtt",
         "result": {"harmonized_detection": pt.detection_report([0.6, 0.4], d_star=0.53, n_propagated=20)}},
        {"ensemble": "metad_frames", "kind": "metad",
         "result": {"druggability_timeseries": {"harmonized_detection":
                    pt.detection_report([0.7, 0.5, 0.3], d_star=0.53, n_propagated=25)}}},
    ]
    tbl = rh.build_consolidated(entries, fpocket_version="4.2.3")
    assert tbl["fpocket_version"] == "4.2.3"
    names = [r["ensemble"] for r in tbl["rows"]]
    assert names == ["af2_static", "8xtt_20conf", "metad_frames"]
    row8 = next(r for r in tbl["rows"] if r["ensemble"] == "8xtt_20conf")
    assert row8["n_propagated"] == 20 and row8["n_detected"] == 2
    # a missing detection still produces a row (empty fields), never crashes
    entries.append({"ensemble": "release", "kind": "release_druggable", "result": {}})
    tbl2 = rh.build_consolidated(entries)
    assert tbl2["rows"][-1]["ensemble"] == "release"
    assert tbl2["rows"][-1]["n_propagated"] is None
