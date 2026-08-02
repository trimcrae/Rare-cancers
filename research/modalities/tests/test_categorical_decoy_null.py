"""Pure-function tests for the C02 cross-system decoy null and the C04 pocket contrast.

Everything exercised here is dependency-free: no fpocket, no network, no structures beyond the two-line PDB
fragments built inline. The heavy scientific steps are IMPORTED from already-tested modules
(`nr4a3_basin_search`, `nr4a_paralogue_dynamics`, `nr4a_differential_atlas`, `pocket_tracking`) and are not
re-tested here — what is new in these two modules is the DRIVER, and that is what these tests pin.
"""
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
