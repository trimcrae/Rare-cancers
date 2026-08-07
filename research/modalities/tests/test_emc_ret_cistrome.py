"""Tests for the RET cistrome instrument.

⛔ WHAT THESE EXIST TO CATCH, in order of how much damage each would do:

  1. **A COORDINATE CONVENTION DEFECT.** This lane has already been burned twice by one (the NR4A3
     exon-numbering hazard and the 2-nt acceptor 5'UTR). The genome analogue is worse: RET is on
     chr10, where GRCh37 and GRCh38 differ by a large constant, so a build mix-up does not raise —
     it silently reports another locus, and the artifact looks perfectly plausible. Half of this
     file is interval algebra for that reason.
  2. **A VERDICT FROM NO READING.** The failure CLAUDE.md §4 is written about: a populated field
     that was never measured. An empty cache, an empty peak set and a peak set that recovers no
     positive control must all be incapable of producing a biological call.
  3. **A NULL RENDERING AS A NEGATIVE.** A peak set that finds nothing at SEMA3C or ENO3 has not
     excluded RET; it has failed to detect anything. Those two states must never render alike.

Everything here is offline. No network, no fixtures that a real run could not produce.
"""

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import emc_ret_cistrome as M  # noqa: E402
import emc_ret_target_scan as MOTIF  # noqa: E402


# =============================================================================================
# 1 — THE INTERVAL ALGEBRA
# =============================================================================================

def test_the_module_selftest_passes_in_full():
    """The selftest is what CI runs before one byte is fetched; it must not be able to rot."""
    assert M.selftest() == 0


@pytest.mark.parametrize("start,end", [(1, 1), (100, 100), (1, 2), (43_000_000, 43_050_000)])
def test_ensembl_to_bed_preserves_width_and_round_trips(start, end):
    s0, e0 = M.ens_to_bed(start, end)
    assert e0 - s0 == end - start + 1
    assert M.bed_to_ens(s0, e0) == (start, end)


def test_a_one_base_feature_is_one_base_wide_in_both_frames():
    """The classic off-by-one. A 1-bp Ensembl feature is [100,100]; BED is [99,100)."""
    assert M.ens_to_bed(100, 100) == (99, 100)


def test_adjacent_intervals_do_not_overlap():
    """Half-open semantics. If this flips, every window gains a spurious boundary peak."""
    assert not M.overlaps(0, 10, 10, 20)
    assert M.overlaps(0, 11, 10, 20)
    assert M.overlap_bp(0, 10, 10, 20) == 0


def test_chromosome_naming_is_normalised_both_ways():
    """Ensembl says `10`, BED says `chr10`. An unnormalised comparison reports zero peaks
    EVERYWHERE, which is indistinguishable from a real genome-wide negative."""
    assert M.norm_chrom("10") == M.norm_chrom("chr10") == M.norm_chrom("CHR10") == "chr10"


def test_a_cross_build_intersection_is_refused_not_corrected():
    with pytest.raises(ValueError) as e:
        M.intersect_locus([("chr10", 1, 2, None)], ("chr10", 0, 10), "hg19", "hg38")
    assert "cross-build" in str(e.value)


def test_the_window_is_imported_from_the_motif_scan_and_not_re_typed():
    """CLAUDE.md §1. The -10 kb / +15 kb asymmetry has ONE home; if a future session re-scopes it
    there, this module must move with it or fail loudly rather than diverge silently."""
    assert M.WINDOW_UPSTREAM is MOTIF.WINDOW_UPSTREAM
    assert M.WINDOW_DOWNSTREAM is MOTIF.WINDOW_DOWNSTREAM
    assert M.WINDOW_UPSTREAM != M.WINDOW_DOWNSTREAM, (
        "the asymmetry is the point — it exists to contain RET's MCS+9.7 element")


def test_the_promoter_window_is_strand_aware_and_mirrored():
    plus = {"chrom": "chr10", "start": 1_000_000, "end": 1_050_000, "strand": 1}
    minus = {"chrom": "chr10", "start": 1_000_000, "end": 1_050_000, "strand": -1}
    wp, wm = M.promoter_window_bed(plus), M.promoter_window_bed(minus)
    assert wp[1] - wp[0] == wm[1] - wm[0]
    # On the plus strand the TSS is the gene start; the window reaches UPSTREAM by WINDOW_UPSTREAM.
    assert wp[0] == 1_000_000 - M.WINDOW_UPSTREAM - 1
    # On the minus strand the TSS is the gene END and upstream is to the RIGHT.
    assert wm[1] == 1_050_000 + M.WINDOW_UPSTREAM


def test_a_peak_exactly_at_the_window_edge_is_handled_by_half_open_rules():
    gene = {"chrom": "chr10", "start": 1_000_000, "end": 1_050_000, "strand": 1}
    lo, hi = M.promoter_window_bed(gene)
    just_inside = [("chr10", hi - 1, hi, 10.0)]
    just_outside = [("chr10", hi, hi + 100, 10.0)]
    assert len(M.intersect_locus(just_inside, ("chr10", lo, hi), "hg38", "hg38")) == 1
    assert len(M.intersect_locus(just_outside, ("chr10", lo, hi), "hg38", "hg38")) == 0


def test_nearest_peak_on_another_chromosome_is_an_absent_reading_not_a_big_number():
    peaks = [("chr7", 100, 200, 1.0)]
    assert M.nearest_peak_distance(peaks, "chr10", 1000) is None


# =============================================================================================
# 2 — NO READING ⇒ NO VERDICT
# =============================================================================================

def test_an_empty_cache_never_produces_a_biological_verdict():
    a = M.derive({})
    assert a["verdict"] is None
    assert a["part_2_intersection"]["_status"] == "NOT_RUN"
    assert a["part_2_intersection"]["verdict"] is None
    assert "ABSENT READING" in a["part_2_intersection"]["why"]


def test_a_cache_with_no_retrievable_peak_set_never_produces_a_verdict():
    a = M.derive({"_generated_utc": "x", "genes": {}, "peaksets": {}})
    assert a["verdict"] is None
    assert a["part_2_intersection"]["_status"] == "NO_PEAK_SET_RETRIEVED"
    assert "ABSENT READING, NOT A NEGATIVE" in a["part_2_intersection"]["why"]


def test_a_peakset_that_failed_to_download_is_not_counted_as_an_empty_one():
    """A 404 and 'this factor binds nothing' must not render alike."""
    cache = M._synthetic_cache(ret_peak=True, control_peak=True)
    cache["peaksets"]["DEAD"] = {"antigen": "NR4A3", "genome": "hg38", "cell_type": "x",
                                 "cell_type_class": "x", "qc": None, "peaks": [],
                                 "diag": {"_status": "absent"}, "_status": "absent"}
    a = M.derive(cache)
    ids = [r["peakset"] for r in a["part_2_intersection"]["ret_summary"]["rows"]]
    assert "DEAD" not in ids


# =============================================================================================
# 3 — A NULL WITHOUT A POSITIVE CONTROL IS NOT A NEGATIVE
# =============================================================================================

def test_no_control_recovered_makes_a_null_uninterpretable():
    a = M.derive(M._synthetic_cache(ret_peak=False, control_peak=False))
    v = a["verdict"]
    assert v is not None
    assert "UNINTERPRETABLE" in v["strength"]
    assert "NEGATIVE" not in v["headline"].replace("NO NR4A PEAK", "")


def test_control_recovered_makes_a_null_a_real_negative_but_still_scoped():
    a = M.derive(M._synthetic_cache(ret_peak=False, control_peak=True))
    v = a["verdict"]
    assert "NEGATIVE AT ITS TRUE STRENGTH" in v["strength"]
    # ...and it must still say what it is a statement ABOUT.
    assert "cell type" in v["strength"] or "chromatin" in v["strength"]


def test_a_ret_peak_is_reported_as_a_prior_and_never_as_a_demonstration():
    a = M.derive(M._synthetic_cache(ret_peak=True, control_peak=True))
    v = a["verdict"]
    assert "PRIOR, NOT A DEMONSTRATION" in v["strength"]
    assert "not evidence that EWSR1::NR4A3 binds RET" in v["strength"]
    assert a["part_2_intersection"]["ret_summary"]["n_with_a_RET_promoter_peak"] == 1


def test_the_positive_control_verdict_names_which_control_was_recovered():
    a = M.derive(M._synthetic_cache(ret_peak=True, control_peak=True))
    ps = a["part_2_intersection"]["per_peakset"]["SYNTH"]
    assert ps["positive_control_verdict"]["state"] == "A KNOWN POSITIVE IS RECOVERED"
    assert "SEMA3C" in ps["positive_control_verdict"]["recovered"]


# =============================================================================================
# 4 — LANGUAGE DISCIPLINE, SCOPE AND PROVENANCE
# =============================================================================================

def test_every_locus_declares_why_it_is_in_the_panel():
    for sym, why in M.LOCI.items():
        assert isinstance(why, str) and len(why) > 20, sym


def test_the_two_known_positive_controls_are_in_the_locus_panel():
    for sym in M.KNOWN_POSITIVE_CONTROLS:
        assert sym in M.LOCI


def test_the_sema3c_control_carries_the_only_fusion_chromatin_citation():
    """PMID 31020999 is the ONLY published chromatin experiment on the EMC-canonical fusion. If
    that citation ever leaves this file, the strongest control in the panel becomes unattributed."""
    assert "31020999" in M.LOCI["SEMA3C"]
    assert "26310886" in M.LOCI["ENO3"]


def test_no_locus_or_verdict_string_asserts_efficacy_or_clinical_readiness():
    blob = json.dumps({"loci": M.LOCI, "framing": M.FRAMING,
                       "cannot": M._cannot_conclude(),
                       "v1": M.derive(M._synthetic_cache(True, True))["verdict"],
                       "v2": M.derive(M._synthetic_cache(False, True))["verdict"]}).lower()
    for banned in ("is effective", "will work", "safe in patients", "ready for the clinic",
                   "should be given", "recommend treating", "therapeutic window in emc"):
        assert banned not in blob, banned
    # And the scope disclaimer must actually be present rather than merely not contradicted.
    assert "no emc patient has received a selective ret inhibitor" in blob \
        or "no emc patient has ever received" in blob


def test_the_artifact_always_says_what_it_cannot_conclude():
    for cache in (M._synthetic_cache(True, True), M._synthetic_cache(False, True)):
        a = M.derive(cache)
        c = a["_what_this_cannot_conclude"]
        for k in ("not_the_fusion", "not_EMC_chromatin", "not_function", "not_activation",
                  "not_clinical"):
            assert k in c and len(c[k]) > 40


def test_the_background_panel_is_not_chosen_by_this_module():
    """It is a fixed-seed sample of a committed artifact, so it cannot have been picked to flatter
    or damage RET — and it must be reproducible offline or `--check` is meaningless."""
    a, _ = MOTIF.background_symbols()
    b, _ = MOTIF.background_symbols()
    assert a == b and len(a) > 50
    assert "RET" not in a


def test_the_derive_half_is_deterministic():
    cache = M._synthetic_cache(ret_peak=True, control_peak=True)
    one = M.derive(cache)
    two = M.derive(cache)
    strip = lambda d: json.dumps({k: v for k, v in d.items() if k != "generated_utc"},  # noqa: E731
                                 sort_keys=True, default=str)
    assert strip(one) == strip(two)


# =============================================================================================
# 5 — THE PARALOGUE READ
# =============================================================================================

def _two_paralogue_cache(ret_in_nr4a1):
    c = M._synthetic_cache(ret_peak=True, control_peak=True)
    peaks = [("chr7", 79_999_900, 80_000_200, 300.0), ("chr1", 1000, 1200, 100.0)]
    if ret_in_nr4a1:
        peaks.append(("chr10", 43_000_000, 43_000_300, 200.0))
    c["peaksets"]["SYNTH_NR4A1"] = {"antigen": "NR4A1", "genome": "hg38",
                                    "cell_type": "synthetic", "cell_type_class": "synthetic",
                                    "qc": None, "peaks": peaks,
                                    "diag": {"_status": "read"}, "_status": "read"}
    return c


def test_a_peak_only_nr4a3_has_is_reported_as_the_selective_reading():
    a = M.derive(_two_paralogue_cache(ret_in_nr4a1=False))
    p3 = a["part_3_paralogue_overlap"]
    assert "NR4A3" in p3["state"] and "NOT BY THE OTHERS" in p3["state"]
    # ...and the reading must warn that peak calling is thresholded.
    assert "sub-threshold" in p3["reading"]


def test_a_peak_two_paralogues_share_is_reported_differently():
    a = M.derive(_two_paralogue_cache(ret_in_nr4a1=True))
    p3 = a["part_3_paralogue_overlap"]
    assert "NR4A1" in p3["state"] and "NR4A3" in p3["state"]


def test_the_paralogue_block_reports_the_genome_wide_sharing_rate():
    """'All three share RET' means one thing at 5 % background sharing and another at 80 %."""
    a = M.derive(_two_paralogue_cache(ret_in_nr4a1=True))
    pair = a["part_3_paralogue_overlap"]["genome_wide_pairwise_sharing"]["NR4A1_vs_NR4A3"]
    assert pair["fraction_of_a_overlapped_by_b"] is not None
    assert 0.0 <= pair["fraction_of_a_overlapped_by_b"] <= 1.0


def test_a_paralogue_with_no_peakset_is_an_absent_reading():
    a = M.derive(_two_paralogue_cache(ret_in_nr4a1=False))
    nr4a2 = a["part_3_paralogue_overlap"]["at_RET"]["NR4A2"]
    assert nr4a2["n_peaksets"] == 0
    assert nr4a2["any_promoter_peak_at_RET"] is None    # None, NOT False
    pair = a["part_3_paralogue_overlap"]["genome_wide_pairwise_sharing"]["NR4A1_vs_NR4A2"]
    assert pair.get("_status") == "not_computable"
    assert "ABSENT READING" in pair["why"]


def test_fraction_overlapping_is_correct_on_a_hand_checkable_case():
    a = [("chr1", 0, 100, None), ("chr1", 1000, 1100, None), ("chr2", 0, 100, None)]
    b = [("chr1", 50, 60, None)]        # overlaps only A's first interval
    assert M._fraction_overlapping(a, b) == pytest.approx(1 / 3, abs=1e-4)
    assert M._fraction_overlapping(a, []) is None


# =============================================================================================
# 6 — THE BED PARSER
# =============================================================================================

def test_the_bed_parser_rejects_headers_and_records_what_it_could_not_read():
    raw = b"\n".join([
        b'track name="x"',
        b"# a comment",
        b"chr10\t100\t200\tpeak1\t55.5\t.",
        b"chr10\tNOT_A_NUMBER\t200",
        b"chr10\t300\t250",                 # inverted
        b"10\t400\t500\tpeak2\t12",         # unprefixed chromosome
    ])
    peaks, diag = M.parse_bed(raw, "test")
    assert diag["_status"] == "read"
    assert diag["n_peaks"] == 2 and diag["n_unparseable"] == 2
    assert peaks[0] == ("chr10", 100, 200, 55.5)
    assert peaks[1][0] == "chr10", "an unprefixed chromosome must normalise, not be dropped"


def test_the_bed_parser_reports_absence_rather_than_returning_a_silent_empty_list():
    peaks, diag = M.parse_bed(None, "test")
    assert peaks == [] and diag["_status"] == "absent"


def test_a_gzipped_bed_is_read():
    import gzip
    raw = gzip.compress(b"chr10\t100\t200\tp\t9\n")
    peaks, diag = M.parse_bed(raw, "test")
    assert diag["_status"] == "read" and peaks == [("chr10", 100, 200, 9.0)]


# =============================================================================================
# 7 — MOUSE IS AN ORTHOLOGUE READING AND MUST NEVER POOL WITH HUMAN
# =============================================================================================

def _mouse_cache():
    c = M._synthetic_cache(ret_peak=True, control_peak=True)
    c["genes"]["mm10"] = {
        "RET": {"chrom": "chr6", "start": 118_150_000, "end": 118_200_000, "strand": 1,
                "assembly_name": "GRCm38", "species": "mus_musculus", "queried_symbol": "Ret"},
        "SEMA3C": {"chrom": "chr5", "start": 17_600_000, "end": 17_700_000, "strand": 1,
                   "assembly_name": "GRCm38", "species": "mus_musculus",
                   "queried_symbol": "Sema3c"},
    }
    c["peaksets"]["SYNTH_MOUSE"] = {
        "antigen": "NR4A1", "genome": "mm10", "cell_type": "synthetic mouse",
        "cell_type_class": "synthetic", "qc": None,
        "peaks": [("chr6", 118_150_000, 118_150_400, 90.0),
                  ("chr5", 17_599_900, 17_600_300, 90.0)],
        "diag": {"_status": "read"}, "_status": "read"}
    return c


def test_a_mouse_peakset_is_tagged_as_an_orthologue_and_counted_separately():
    a = M.derive(_mouse_cache())
    s = a["part_2_intersection"]["ret_summary"]
    assert s["human"]["n_peaksets"] == 1
    assert s["mouse_orthologue"]["n_peaksets"] == 1
    assert s["human"]["n_with_a_RET_promoter_peak"] == 1
    assert s["mouse_orthologue"]["n_with_a_Ret_promoter_peak"] == 1
    # ...and the verdict must SAY the two are separate rather than merely storing them apart.
    assert "never pooled" in a["verdict"]["by_species"]
    rows = {r["peakset"]: r["species"] for r in s["rows"]}
    assert rows["SYNTH_MOUSE"] == "mouse" and rows["SYNTH"] == "human"


def test_a_mouse_peakset_reports_no_background_rank_rather_than_a_fabricated_one():
    """The 200-gene panel is human and is deliberately not translated. A rank it cannot compute
    must read NOT_COMPUTED with the reason, never as a p-value."""
    a = M.derive(_mouse_cache())
    bg = a["part_2_intersection"]["per_peakset"]["SYNTH_MOUSE"]["background"]
    assert bg["_status"] == "NOT_COMPUTED"
    assert bg["empirical_p_RET_vs_panel"] is None
    assert "ABSENT READING" in bg["why"]


def test_mouse_and_human_builds_cannot_be_intersected_with_each_other():
    with pytest.raises(ValueError):
        M.intersect_locus([("chr6", 1, 2, None)], ("chr6", 0, 10), "mm10", "hg38")


def test_every_mouse_build_declares_its_species_and_every_human_build_does_not():
    for build, cfg in M.BUILDS.items():
        if cfg.get("ensembl_species") == "mus_musculus":
            assert cfg.get("species") == "mouse", build
        else:
            assert cfg.get("species", "human") == "human", build


def test_the_mouse_symbol_map_covers_ret_and_both_positive_controls():
    for sym in ["RET"] + M.KNOWN_POSITIVE_CONTROLS:
        assert sym in M.HUMAN_TO_MOUSE_SYMBOL, sym
        assert M.HUMAN_TO_MOUSE_SYMBOL[sym] == sym.capitalize(), sym


# =============================================================================================
# 8 — THE GPL6244 BUILD CROSS-CHECK
# =============================================================================================
#
# ⚠ The two spans used below are FIXTURE VALUES, not a claim about where RET is. They exist only
# to exercise the containment logic, and the real run fetches both from their own services. If
# they were wrong the test would still be a valid test of the algebra — which is the point of
# keeping every real coordinate out of this file.

_ENS_FIXTURE = {
    "hg38": {"RET": {"chrom": "chr10", "start": 43_077_069, "end": 43_130_351, "strand": 1}},
    "hg19": {"RET": {"chrom": "chr10", "start": 43_572_517, "end": 43_625_797, "strand": 1}},
}


def test_gpl_containment_is_decisive_not_merely_corroborating():
    """RET's two human spans on chr10 are far apart, so a probe range can be inside at most one.
    If this ever reports 'consistent with both', nothing may be read as build-verified through
    it, and the record must SAY so rather than picking one."""
    probes = {"RET": [{"probe_id": "p1", "seqname": "chr10", "range_gb": "NC_000010.10",
                       "start": 43_580_000, "stop": 43_580_100}]}
    out = M._gpl_containment({}, probes, _ENS_FIXTURE)
    assert out["RET_build_is_unambiguous"] is True
    assert out["RET_consistent_with"] == ["hg19"]
    assert out["per_gene"]["RET"]["⛔"] is None


def test_gpl_containment_refuses_to_certify_an_ambiguous_probe():
    probes = {"RET": [{"probe_id": "p1", "seqname": "chr10", "range_gb": "?",
                       "start": 1, "stop": 2}]}          # inside neither
    out = M._gpl_containment({}, probes, _ENS_FIXTURE)
    assert out["RET_build_is_unambiguous"] is False
    assert "may be read as build-verified" in out["per_gene"]["RET"]["⛔"]


def test_gpl_containment_ignores_mouse_builds():
    """GPL6244 is a HUMAN array. A mouse span must never be offered as a build its probes are
    consistent with, however well the numbers happen to line up."""
    ens = {"hg38": _ENS_FIXTURE["hg38"],
           "mm10": {"RET": {"chrom": "chr6", "start": 118_150_000, "end": 118_200_000,
                            "strand": 1}}}
    probes = {"RET": [{"probe_id": "p1", "seqname": "chr6", "range_gb": "x",
                       "start": 118_160_000, "stop": 118_160_100}]}
    out = M._gpl_containment({}, probes, ens)
    assert "mm10" not in (out["RET_consistent_with"] or [])
