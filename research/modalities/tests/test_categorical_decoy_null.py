"""Pure-function tests for the C02 cross-system decoy null and the C04 pocket contrast.

Everything exercised here is dependency-free: no fpocket, no network, no structures beyond the two-line PDB
fragments built inline. The heavy scientific steps are IMPORTED from already-tested modules
(`nr4a3_basin_search`, `nr4a_paralogue_dynamics`, `nr4a_differential_atlas`, `pocket_tracking`) and are not
re-tested here — what is new in these two modules is the DRIVER, and that is what these tests pin.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import categorical_decoy_null as CDN     # noqa: E402
import paralogue_pocket_contrast as PPC  # noqa: E402


def _atom(rid, name="CA", b=80.0, x=0.0, y=0.0, z=0.0, res="ALA"):
    return (f"ATOM  {rid*4:5d}  {name:<3s} {res} A{rid:4d}    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00{b:6.2f}           C  ")


# ---------------------------------------------------------------------------------------------------------
# pLDDT parsing and the domain trim
# ---------------------------------------------------------------------------------------------------------
def test_parse_plddt_reads_one_entry_per_residue_from_CA():
    text = "\n".join([_atom(1, "N", 10.0), _atom(1, "CA", 91.5), _atom(2, "CA", 44.25),
                      _atom(3, "CA", 70.0)])
    assert CDN.parse_plddt(text) == [(1, 91.5), (2, 44.25), (3, 70.0)]


def test_largest_confident_segment_picks_the_longest_run_and_respects_min_len():
    plddt = [(i, 90.0) for i in range(1, 6)] + [(i, 10.0) for i in range(6, 8)] \
        + [(i, 95.0) for i in range(8, 20)]
    assert CDN.largest_confident_segment(plddt, min_plddt=70.0, min_len=5) == (8, 19)
    # the same data with a min_len above the best run must REFUSE rather than return a short segment
    assert CDN.largest_confident_segment(plddt, min_plddt=70.0, min_len=50) is None


def test_largest_confident_segment_breaks_on_a_numbering_gap():
    plddt = [(1, 90.0), (2, 90.0), (3, 90.0), (10, 90.0), (11, 90.0)]
    assert CDN.largest_confident_segment(plddt, min_plddt=70.0, min_len=2) == (1, 3)


def test_largest_confident_segment_boundary_is_inclusive_at_the_cutoff():
    plddt = [(1, 69.999), (2, 70.0), (3, 70.0)]
    assert CDN.largest_confident_segment(plddt, min_plddt=70.0, min_len=2) == (2, 3)


def test_trim_pdb_text_keeps_only_the_window_and_terminates():
    text = "\n".join([_atom(1), _atom(5), _atom(9), "HETATM 9999  O   HOH A 500       0.000   0.000   0.000"])
    out = CDN.trim_pdb_text(text, 5, 9)
    assert " A   5" in out and " A   9" in out and " A   1 " not in out
    assert "HETATM" not in out                      # waters/ligands never enter the analysis
    assert out.strip().endswith("END")


# ---------------------------------------------------------------------------------------------------------
# identity / coverage and the PRE-REGISTERED pair selection
# ---------------------------------------------------------------------------------------------------------
def test_alignment_identity_and_coverage():
    a, b = "ACDEF", "ACDEF"
    aln = [(i, i) for i in range(5)]
    assert CDN.alignment_identity(a, b, aln) == (1.0, 1.0)
    aln2 = [(0, 0), (1, 1), (2, None), (None, 2)]
    idn, cov = CDN.alignment_identity(a, b, aln2)
    assert idn == 1.0 and cov == 2 / 5


def test_alignment_identity_empty_alignment_is_zero_not_a_crash():
    assert CDN.alignment_identity("AAA", "BBB", [(0, None), (None, 0)]) == (0.0, 0.0)


def _pair(a, b, identity, coverage=0.9):
    return {"a": a, "b": b, "identity": identity, "coverage": coverage}


def test_select_pairs_applies_band_coverage_ranking_and_the_per_protein_cap():
    entries = [
        _pair("P1", "P2", 0.60),        # |0.60-0.62| = 0.02 -> rank 2
        _pair("P1", "P3", 0.65),        # |0.65-0.62| = 0.03 -> rank 3, but P1 is capped by then
        _pair("P1", "P4", 0.63),        # |0.63-0.62| = 0.01 -> rank 1
        _pair("P5", "P6", 0.20),        # below band
        _pair("P7", "P8", 0.95),        # above band
        _pair("P9", "PA", 0.70, 0.10),  # coverage too low
    ]
    sel, rej = CDN.select_pairs(entries, 0.62, (0.35, 0.90), 0.60, max_pairs=10, max_per_protein=2)
    keys = [(s["a"], s["b"]) for s in sel]
    assert keys == [("P1", "P4"), ("P1", "P2")]              # ranked by |identity - ref|, then P1 capped
    assert ("P1", "P3") not in keys
    why = {(r["a"], r["b"]): r["rejected_because"] for r in rej}
    assert "outside band" in why[("P5", "P6")] and "outside band" in why[("P7", "P8")]
    assert "coverage" in why[("P9", "PA")]


def test_select_pairs_honours_max_pairs():
    entries = [_pair(f"X{i}", f"Y{i}", 0.60) for i in range(20)]
    sel, _ = CDN.select_pairs(entries, 0.60, (0.35, 0.90), 0.60, max_pairs=4, max_per_protein=2)
    assert len(sel) == 4


def test_select_pairs_is_deterministic_under_input_order():
    entries = [_pair("B", "C", 0.60), _pair("A", "D", 0.60)]
    s1, _ = CDN.select_pairs(entries, 0.60, (0.35, 0.90), 0.60, 10, 2)
    s2, _ = CDN.select_pairs(list(reversed(entries)), 0.60, (0.35, 0.90), 0.60, 10, 2)
    assert [(s["a"], s["b"]) for s in s1] == [(s["a"], s["b"]) for s in s2] == [("A", "D"), ("B", "C")]


# ---------------------------------------------------------------------------------------------------------
# background arithmetic
# ---------------------------------------------------------------------------------------------------------
def test_percentile_of_counts_ties_as_at_or_below():
    assert CDN.percentile_of(0.0, [0.0, 0.0, 0.5, 1.0]) == 0.5
    assert CDN.percentile_of(0.5, [0.0, 0.0, 0.5, 1.0]) == 0.75
    assert CDN.percentile_of(0.0, []) is None


def test_summarise_background_reports_the_zero_fraction():
    rows = [{"p": 0.0}, {"p": 0.0}, {"p": 0.2}, {"p": 0.4}, {"p": None}]
    s = CDN.summarise_background(rows, "p")
    assert s["n"] == 4 and s["n_exactly_zero"] == 2 and s["frac_exactly_zero"] == 0.5
    assert s["min"] == 0.0 and s["max"] == 0.4 and s["median"] == 0.1


def test_summarise_background_empty_is_none():
    assert CDN.summarise_background([{"p": None}], "p") is None


# ---------------------------------------------------------------------------------------------------------
# the statistic itself, on synthetic anchors — the arithmetic must match categorical_verdict's reduction
# ---------------------------------------------------------------------------------------------------------
def _cys(label, xyz, rsa=1.0, partner_cys=False):
    return {"label": label, "local_resid": int(label[1:]), "xyz": xyz, "rsa": rsa,
            "partner_aligned_resid": 1, "partner_has_cys_here": partner_cys, "fit_deviation_A": 0.0}


def _anchor(a_t, a_e, pose):
    return {"arm": "vhl", "pose": pose, "xyz": a_e, "a_t": a_t, "a_e": a_e}


def test_ordered_decoy_statistic_is_undefined_without_a_target_unique_cysteine():
    anchors = [_anchor((0, 0, 0), (0, 0, 0), i) for i in range(5)]
    out = CDN.ordered_decoy_statistic(anchors, [_cys("C10", (0, 0, 0), partner_cys=True)], [], None)
    assert out["status"] == "UNDEFINED_no_target_unique_cysteine"
    assert out["n_target_unique_cysteines"] == 0
    assert "P_gate" not in out            # never a zero standing in for an undefined conditional


def test_ordered_decoy_statistic_zero_and_one_collision_limits():
    # budget at 12 atoms = contour(12) + 2*electrophile_arm ~ 21.9 A; put the target Cys at the anchor and
    # the paralogue Cys either on top of it (certain collision) or far away (none).
    anchors = [_anchor((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), i) for i in range(40)]
    tgt = [_cys("C10", (0.0, 0.0, 0.0))]
    near = [_cys("C99", (0.0, 0.0, 0.0))]
    far = [_cys("C99", (500.0, 0.0, 0.0))]
    hot = CDN.ordered_decoy_statistic(anchors, tgt, near, None)
    cold = CDN.ordered_decoy_statistic(anchors, tgt, far, None)
    assert hot["status"] == "GRADED" and hot["P_gate"] == 1.0
    assert cold["status"] == "GRADED" and cold["P_gate"] == 0.0
    assert hot["n_conditioning_events_gate"] == 40 == cold["n_conditioning_events_gate"]
    # a Wilson interval is attached to both, so a 0/40 is never read as an exact zero
    assert hot["by_linker_atoms"]["12"]["P_paralogue_also_labelled_wilson95"][1] == 1.0
    assert cold["by_linker_atoms"]["12"]["P_paralogue_also_labelled_wilson95"][1] > 0.0


def test_ordered_decoy_statistic_flags_underpowered_rows():
    anchors = [_anchor((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), i) for i in range(5)]
    out = CDN.ordered_decoy_statistic(anchors, [_cys("C10", (0.0, 0.0, 0.0))],
                                      [_cys("C99", (500.0, 0.0, 0.0))], None)
    assert out["status"].startswith("UNDERPOWERED")
    assert out["n_conditioning_events_gate"] == 5


def test_ordered_decoy_statistic_exposure_filter_can_remove_a_buried_paralogue_thiol():
    anchors = [_anchor((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), i) for i in range(40)]
    tgt = [_cys("C10", (0.0, 0.0, 0.0))]
    buried = [_cys("C99", (0.0, 0.0, 0.0), rsa=0.01)]
    out = CDN.ordered_decoy_statistic(anchors, tgt, buried, None)
    assert out["P_gate"] == 1.0 and out["P_gate_EXPOSED"] == 0.0


# ---------------------------------------------------------------------------------------------------------
# C04 helpers
# ---------------------------------------------------------------------------------------------------------
def test_pool_detections_recomputes_fractions_rather_than_averaging_them():
    a = {"n_propagated": 25, "n_detected": 25, "n_ge_dstar": 10}
    b = {"n_propagated": 25, "n_detected": 20, "n_ge_dstar": 0}
    p = PPC.pool_detections([a, b])
    assert p["n_propagated"] == 50 and p["n_detected"] == 45 and p["n_ge_dstar"] == 10
    assert p["frac_ge_among_detected"] == 10 / 45          # NOT (10/25 + 0/20)/2
    assert p["frac_ge_among_propagated"] == 10 / 50


def test_pool_detections_of_nothing_is_none():
    assert PPC.pool_detections([None, None]) is None


def test_contrast_rows_emits_every_species_subset_plus_the_unbiased_pool():
    det = {"n_propagated": 25, "n_detected": 25, "n_ge_dstar": 5, "detection_fraction": 1.0,
           "frac_ge_among_detected": 0.2, "frac_ge_among_propagated": 0.2, "d_star": 0.53}
    by = {sp: {s: dict(det) for s in PPC.SUBSETS} for sp in PPC.SPECIES}
    rows = PPC.contrast_rows(by)
    assert len(rows) == len(PPC.SPECIES) * (len(PPC.SUBSETS) + 1)
    pooled = [r for r in rows if r["ensemble"] == "release_unbiased_pooled"]
    assert len(pooled) == 3 and all(r["n_propagated"] == 75 for r in pooled)   # metad is NEVER pooled in
    assert all(r["biased"] for r in rows if r["ensemble"] == "metad")


def test_ca_by_resseq_reads_angstrom_coordinates(tmp_path):
    p = tmp_path / "f.pdb"
    p.write_text("\n".join([_atom(1, "CA", 50.0, 1.0, 2.0, 3.0), _atom(1, "CB", 50.0, 9.0, 9.0, 9.0),
                            _atom(2, "CA", 50.0, 4.0, 5.0, 6.0)]))
    ca = PPC.ca_by_resseq(str(p))
    assert ca == {1: (1.0, 2.0, 3.0), 2: (4.0, 5.0, 6.0)}


# ---------------------------------------------------------------------------------------------------------
# regression: the selfcheck summary line must not be able to fail the step it summarises
# ---------------------------------------------------------------------------------------------------------
def test_selfcheck_summary_only_reads_keys_the_checks_block_defines():
    """Run 30773415505: `mode_selfcheck` wrote its artifact and then died on
    `KeyError: 'gate12_collision_reproduced'` — a key renamed in the checks block and not in the print — which
    took the Reduce and Publish steps down with it. A cosmetic line must never fail a measured step, so the
    summary is asserted to be `.get`-based over exactly the keys the block emits."""
    import inspect
    src = inspect.getsource(CDN.mode_selfcheck)
    summary = src[src.index('print(f"  [cdn] selfcheck'):]
    assert "['" not in summary.split(")")[0], "the selfcheck summary must use .get(), not [] indexing"
    for key in ("unique_set_reproduced", "n_conditioning_events", "gate12_collision_abs_diff",
                "atoms20_collision_abs_diff"):
        assert f"'{key}'" in src, f"{key} is printed but never defined in the checks block"


# =========================================================================================================
# `C24` — the SECOND pre-registered scope (the reference-anchored LBD window)
#
# What these pin is exactly the property the second scope exists to have: that it is a MATCHED STRUCTURAL
# REGION chosen by a rule with no confidence criterion and no reference to any outcome, and that the two
# scopes cannot contaminate each other's artifacts.
# =========================================================================================================
def test_sw_align_is_local_and_finds_a_domain_inside_a_long_chain():
    """The whole reason this is Smith-Waterman and not the frozen global `nw_align`: a full-length chain
    against a short reference must align only the homologous SEGMENT, not smear across the chain."""
    ref = "ACDEFGHIKLMNPQRSTVWY" * 3
    query = "GGGGGGGGGGGGGGGGGGGG" + ref + "PPPPPPPPPPPPPPPPPPPP"
    aln, score = CDN.sw_align(query, ref)
    cols = [(i, j) for i, j in aln if i is not None and j is not None]
    assert len(cols) == len(ref) and score > 0
    assert min(i for i, _ in cols) == 20 and max(i for i, _ in cols) == 20 + len(ref) - 1


def test_sw_align_never_scores_below_zero_and_returns_an_empty_alignment_for_no_similarity():
    aln, score = CDN.sw_align("WWWWWWWWWW", "PPPPPPPPPP")
    assert score >= 0
    assert all(i is None or j is None for i, j in aln) or score > 0


def test_lbd_window_returns_the_span_of_residues_aligned_to_the_reference():
    ref = "ACDEFGHIKLMNPQRSTVWY" * 7            # 140 residues — above the pre-registered 120 floor
    query = "GGGGG" + ref + "PPPPP"
    residues = [(i + 101, aa) for i, aa in enumerate(query)]      # non-1-based numbering, as AF models are
    win = CDN.lbd_window(residues, query, ref)
    assert win["accepted"] is True
    assert win["first"] == 106 and win["last"] == 106 + len(ref) - 1
    assert win["window_len"] == len(ref)
    assert win["reference_coverage"] == 1.0 and win["identity_to_reference"] == 1.0


def test_lbd_window_refuses_on_coverage_and_on_length_and_says_which():
    ref = "ACDEFGHIKLMNPQRSTVWY" * 7
    win = CDN.lbd_window([(i + 1, a) for i, a in enumerate(ref[:10])], ref[:10], ref)
    assert win["accepted"] is False
    assert "coverage" in win["reason"] or "window" in win["reason"]
    # the observables are present EVEN ON A REFUSAL — a refusal must be diagnosable from the artifact
    assert "reference_coverage" in win and "sw_score" in win


def test_lbd_window_is_a_pure_span_and_keeps_insertions_inside_it():
    """An insertion in the query between two aligned positions stays in the window: the window is a
    contiguous structural span, not a set of aligned residues."""
    ref = "ACDEFGHIKLMNPQRSTVWY" * 7
    query = ref[:70] + "GGGGGGGG" + ref[70:]
    residues = [(i + 1, aa) for i, aa in enumerate(query)]
    win = CDN.lbd_window(residues, query, ref)
    assert win["accepted"] is True
    assert win["window_len"] == len(query)


def test_plddt_profile_is_reported_never_applied():
    prof = CDN.plddt_profile([(1, 90.0), (2, 40.0), (3, 80.0), (9, 95.0)], 1, 3)
    assert prof["n_residues_with_plddt"] == 3
    assert prof["frac_at_or_above_70"] == round(2 / 3, 4)
    assert "NOT APPLIED" in prof["_reading"]


def test_set_scope_gives_every_scope_its_own_plan_shard_and_output_paths():
    """⛔ THE ONE MISTAKE HERE THAT WOULD BE SILENT: a scoped run writing over the other scope's artifact,
    or a reduce pooling two scopes' shards into one background. Paths must be disjoint."""
    try:
        CDN.set_scope("plddt")
        p0 = (CDN.PLAN, CDN.OUT, CDN.SHARD_DIR, CDN.TRIMMED_DIR)
        CDN.set_scope("lbd")
        p1 = (CDN.PLAN, CDN.OUT, CDN.SHARD_DIR, CDN.TRIMMED_DIR)
        assert len(set(p0) | set(p1)) == 8, "the two scopes share a path"
        for a, b in zip(p0, p1):
            assert a != b
        assert CDN.OUT.endswith("categorical-decoy-null-lbd.json")
        assert CDN.PLAN.endswith("categorical-decoy-null-lbd-plan.json")
    finally:
        CDN.set_scope("plddt")


def test_the_alphafold_model_cache_is_shared_between_scopes():
    """The models are the same files. Sharing them is what makes it impossible for the two scopes to
    disagree about which model an accession has."""
    try:
        CDN.set_scope("plddt")
        a = CDN.af_path("Q92570")
        CDN.set_scope("lbd")
        assert CDN.af_path("Q92570") == a
    finally:
        CDN.set_scope("plddt")


def test_the_lbd_scope_holds_every_other_preregistered_constant_identical_to_C16():
    """The claim `PREREG_LBD._held_identical_to_C16` makes is checkable, so it is checked. If someone
    changes a threshold for one scope only, this fails."""
    held = CDN.PREREG_LBD["_held_identical_to_C16"]
    assert held["gate_atoms"] == CDN.GATE == CDN.PREREG["statistic"]["gate_atoms"]
    assert held["exposure_cutoff_EXPOSED_RSA"] == CDN.EXPOSED_RSA
    assert held["identity_band"] == CDN.PREREG["pair_formation"]["identity_band"]
    assert held["alignment_coverage_min"] == CDN.PREREG["pair_formation"]["alignment_coverage_min"]
    assert held["max_per_protein"] == CDN.PREREG["pair_formation"]["max_per_protein"]
    assert held["placements"] == CDN.PREREG["placements"]
    assert held["gradeability_min_conditioning_events"] \
        == CDN.PREREG["gradeability"]["min_conditioning_events"]
    # the coverage floor and the length floor are BORROWED, not invented
    assert CDN.LBD_MIN_REF_COVERAGE == CDN.PREREG["pair_formation"]["alignment_coverage_min"]
    assert CDN.LBD_MIN_WINDOW_LEN == CDN.MIN_DOMAIN_LEN


def test_prereg_lbd_inherits_rather_than_copies_the_shared_blocks():
    """One fact, one place: the shared pre-registration blocks are the SAME objects, so the two plans
    cannot drift apart in wording."""
    p = CDN.prereg_lbd()
    inherited = p["_inherited_verbatim_from_the_C16_preregistration"]
    for key in CDN._LBD_INHERITED:
        assert inherited[key] is CDN.PREREG[key]


def test_the_lbd_scopes_only_budget_change_is_max_pairs_and_it_nests():
    assert CDN.SCOPES["lbd"]["max_pairs"] == CDN.LBD_MAX_PAIRS
    assert CDN.LBD_MAX_PAIRS > CDN.PREREG["pair_formation"]["max_pairs"]
    # nesting: the greedy selection is deterministic, so a wider cap's first N are a narrower cap's N
    entries = [{"a": f"P{i}", "b": f"Q{i}", "identity": 0.5 + i * 0.01, "coverage": 0.9} for i in range(30)]
    narrow, _ = CDN.select_pairs(entries, 0.5, [0.35, 0.90], 0.6, 10, 2)
    wide, _ = CDN.select_pairs(entries, 0.5, [0.35, 0.90], 0.6, 20, 2)
    assert [p["a"] for p in wide[:10]] == [p["a"] for p in narrow]


def test_nr4a3_scope_check_reports_C397_in_or_out_and_never_stays_silent():
    out_of_scope = CDN.nr4a3_scope_check({CDN.NR4A3_ACC: {"first": 427, "last": 570, "n_residues": 144}},
                                         scope="plddt")
    assert out_of_scope["headline_residue_C397_in_scope"] is False
    assert out_of_scope["inside_the_trimmed_window"] == [559]
    assert 397 in out_of_scope["⛔_outside_and_therefore_INVISIBLE_to_this_harness"]
    assert "not_relaxed_after_the_fact" in "".join(out_of_scope)
    in_scope = CDN.nr4a3_scope_check({CDN.NR4A3_ACC: {"first": 373, "last": 626, "n_residues": 254}},
                                     scope="lbd")
    assert in_scope["headline_residue_C397_in_scope"] is True
    assert in_scope["⛔_outside_and_therefore_INVISIBLE_to_this_harness"] == []
    assert "ALPHAFOLD-MODEL row" in in_scope["★_reading"]


def test_window_spread_reports_the_factor_that_makes_a_scope_matched_or_not():
    sp = CDN.window_spread({"a": {"n_residues": 122}, "b": {"n_residues": 144}, "c": {"n_residues": 247}})
    assert sp["min"] == 122 and sp["max"] == 247 and sp["n_proteins"] == 3
    assert sp["max_over_min"] == round(247 / 122, 3)


def test_compare_scopes_says_so_when_the_sibling_artifact_is_absent(tmp_path, monkeypatch):
    """An absent reading is not a reading of absence — a missing sibling must not render as 'no difference'."""
    monkeypatch.setattr(CDN, "HERE", str(tmp_path))
    out = CDN.compare_scopes("lbd", {}, {}, {}, {}, {}, 0)
    assert "NOT ON DISK" in out["status"]
    assert "not a finding of no difference" in out["status"]


def test_grade_uses_one_rule_for_both_scopes_and_reports_C397_separately():
    res = {"results": {
        "n_graded": 8,
        "background_at_gate_12": {"reach_only": {"frac_exactly_zero": 0.125},
                                  "exposed": {"frac_exactly_zero": 0.33}},
        "nr4a3_harness_matched": {"NR4A1": {"percentile_reach_only": 0.125, "percentile_exposed": None}},
        "★_cysteine_level_background_at_gate_12": {"n_graded": 12,
                                                   "reach_only": {"frac_exactly_zero": 0.25}},
        "★_nr4a3_per_cysteine_vs_that_background": {
            "C397_vs_NR4A1": {"percentile_reach_only": 0.0833}},
    }}
    g = CDN.grade(res)
    assert g["verdict"] == "DISTINGUISHED"
    assert g["c397_verdict"] == "DISTINGUISHED"
    # and a scope with no C397 must say NOT MEASURED rather than inherit the row-level grade
    res["results"]["★_nr4a3_per_cysteine_vs_that_background"] = {"C559_vs_NR4A1": {}}
    assert CDN.grade(res)["c397_verdict"].startswith("NOT MEASURED")


def test_summarise_background_carries_an_interval_and_a_resolution_not_a_bare_point_estimate():
    """`frac_exactly_zero` is the headline of the whole exercise and was a bare point estimate over a
    single-digit n. A number that invites over-reading must carry its own bounds."""
    rows = [{"P": v} for v in (0.0, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.9)]
    s = CDN.summarise_background(rows, "P")
    assert s["n"] == 8 and s["n_exactly_zero"] == 2 and s["frac_exactly_zero"] == 0.25
    lo, hi = s["frac_exactly_zero_wilson95"]
    assert 0.0 <= lo < 0.25 < hi <= 1.0
    assert s["percentile_resolution"] == 1 / 8
    ex = s["★_what_this_n_can_and_cannot_exclude"]
    assert "CAN_exclude" in ex and "CANNOT_exclude" in ex and "CANNOT_report" in ex
    assert "1/n" in ex["CANNOT_report"] or "0.125" in ex["CANNOT_report"]


def test_what_n_excludes_refuses_to_speak_at_n_zero():
    assert CDN.what_n_excludes(0, 0) is None


def test_compare_scopes_derives_C397_in_scope_for_an_artifact_that_predates_the_field(tmp_path, monkeypatch):
    """⚠ An absent field is not an unknown answer. `C16`'s committed artifact predates
    `headline_residue_C397_in_scope`, but it records `inside_the_trimmed_window` — so the answer is known
    and must not render as null."""
    monkeypatch.setattr(CDN, "HERE", str(tmp_path))
    (tmp_path / "categorical-decoy-null.json").write_text(json.dumps({"results": {
        "background_at_gate_12": {"reach_only": {"n": 8}},
        "nr4a3_harness_matched": {},
        "⛔_nr4a3_harness_scope": {"trimmed_window_uniprot": [427, 570],
                                   "inside_the_trimmed_window": [559]},
        "precondition_has_a_target_unique_cysteine": {},
    }}))
    out = CDN.compare_scopes("lbd", {}, {}, {}, {}, {"trimmed_window_uniprot": [373, 626]}, 0)
    other = out["what_the_NR4A3_row_actually_scored"]["other_scope"]
    assert other["C397_in_scope"] is False, "a knowable false must not render as null"
    assert "DERIVED" in other["_C397_in_scope_source"]


def test_placement_budget_saturation_counts_the_rows_the_sampler_cap_bound():
    """Measured on the first C24 shard to land: `pilot_rate=0.00104`, budget at the 6,000,000 cap, and
    13,091 placements against a 45,000 target. A background that shrank because the SAMPLER ran out of
    budget must never read like one that shrank because the BIOLOGY was uniform."""
    cap = CDN.PREREG["placements"]["max_samples_per_arm_pose"]
    target = CDN.PREREG["placements"]["target_n_placements"]
    rows = [
        {"target": "P62508", "gene_target": "ESRRG", "n_placements": 13091,
         "placement_budget_per_arm_pose": cap, "n_poses": 12},
        {"target": "P62508", "gene_target": "ESRRG", "n_placements": 13091,   # 2nd orientation, same target
         "placement_budget_per_arm_pose": cap, "n_poses": 12},
        {"target": "P10589", "gene_target": "NR2F1", "n_placements": target + 500,
         "placement_budget_per_arm_pose": 250000, "n_poses": 12},
    ]
    s = CDN.placement_budget_saturation(rows)
    assert s["n_targets"] == 2, "targets must be de-duplicated across a pair's two orientations"
    assert s["n_targets_at_the_sampler_cap"] == 1
    assert s["n_targets_below_the_placement_target"] == 1
    assert s["targets_at_cap"] == ["ESRRG"]
    assert s["placements_min"] == 13091
    assert "not_repaired_after_the_fact" in "".join(s)


def test_placement_budget_saturation_is_none_when_there_is_nothing_to_summarise():
    assert CDN.placement_budget_saturation([]) is None


def test_the_artifact_declares_its_configuration_and_names_the_defective_one():
    """§3b's declaration rule, discharged by the artifact rather than by a page that quotes it. The two
    items that are NOT merely frozen must be visible without following a link."""
    for scope, other in (("lbd", "C16"), ("plddt", "C24")):
        try:
            CDN.set_scope(scope)
            d = CDN.configuration_declaration()
            it = d["items"]
            assert CDN.SCOPES[scope]["configuration_id"] in it, "the run must declare its own scope"
            assert {"C7", "C8", "C9"} <= set(it), "the gate, the reach convention and the cutoff"
            assert other in it and "NOT USED by this run" in it[other]["status"]
            assert "KNOWN-DEFECTIVE" in it["C7"]["status"]
            assert "CONTESTED" in it["C9"]["status"]
            assert str(CDN.EXPOSED_RSA) in it["C7"]["what_it_fixes"]
        finally:
            CDN.set_scope("plddt")


def test_the_licence_travels_with_every_per_cysteine_percentile():
    """A caveat 400 lines above a figure is a caveat that gets dropped when the figure is quoted — that is
    the whole reason §3.4 fact 4 exists. So the licence is attached to the percentile itself."""
    refs = [{"gene_paralogue": "NR4A1", "per_unique_cysteine": {
        "C397": {"rsa": 0.3, "status": "GRADED", "n_conditioning_events_gate": 100,
                 "P_gate": 0.0, "P_gate_EXPOSED": None}}}]
    decoys = [{"gene_target": "X", "gene_paralogue": "Y", "target": "T", "per_unique_cysteine": {
        f"C{i}": {"rsa": 0.2, "status": "GRADED", "n_conditioning_events_gate": 50,
                  "P_gate": i / 10.0, "P_gate_EXPOSED": i / 10.0} for i in range(1, 6)}}]
    _bg, n3 = CDN.cysteine_level_background(decoys, refs)
    row = n3["C397_vs_NR4A1"]
    lic = row["★_what_a_favourable_value_here_licenses"]
    assert lic is CDN.LICENCE, "one home — the licence must not be copied per row"
    assert "SCREEN" in lic["★_it_licenses"]
    joined = " ".join(lic["⛔_it_does_NOT_license"])
    for must in ("binding", "reactivity", "degradation", "proteome-wide", "R5", "8XTT"):
        assert must in joined, must
    assert row["percentile_reach_only"] == 0.0        # 0.0 beats every strictly-positive background point
    assert row["⚠_percentile_resolution"] == round(1 / 5, 4)


def test_a_zero_percentile_is_flagged_as_the_same_number_as_the_background_zero_rate():
    """⚠ When the target's own P is exactly 0 — the case this whole lane is about — the percentile IS
    P(background <= 0) = `frac_exactly_zero`. Quoting both as independent findings double-counts one
    measurement, so the row says so."""
    decoys = [{"gene_target": "X", "gene_paralogue": "Y", "target": "T", "per_unique_cysteine": {
        "C1": {"status": "GRADED", "n_conditioning_events_gate": 50, "P_gate": 0.0, "P_gate_EXPOSED": 0.0},
        "C2": {"status": "GRADED", "n_conditioning_events_gate": 50, "P_gate": 0.4, "P_gate_EXPOSED": 0.4}}}]
    zero = [{"gene_paralogue": "NR4A1", "per_unique_cysteine": {
        "C397": {"status": "GRADED", "n_conditioning_events_gate": 90, "P_gate": 0.0,
                 "P_gate_EXPOSED": None}}}]
    bg, n3 = CDN.cysteine_level_background(decoys, zero)
    row = n3["C397_vs_NR4A1"]
    assert row["percentile_reach_only"] == bg["reach_only"]["frac_exactly_zero"]
    msg = row["⚠_percentile_equals_the_background_zero_rate"]
    assert "one measurement, not two" in msg and "frac_exactly_zero" in msg
    # ...and a NON-zero target must NOT carry the flag, or it would read as boilerplate
    nonzero = [{"gene_paralogue": "NR4A1", "per_unique_cysteine": {
        "C397": {"status": "GRADED", "n_conditioning_events_gate": 90, "P_gate": 0.2,
                 "P_gate_EXPOSED": None}}}]
    _bg2, n3b = CDN.cysteine_level_background(decoys, nonzero)
    assert n3b["C397_vs_NR4A1"]["⚠_percentile_equals_the_background_zero_rate"] is None
