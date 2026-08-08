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
    assert nr4a2["n_peaksets_scored"] == 0
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


def test_an_absent_reading_may_not_overwrite_a_real_one(tmp_path):
    """Measured 2026-08-07: a CANCELLED ret-cistrome run reached the publish step (which is
    `always()` by design) and published its artifact. Nothing was lost that time because the tree
    still held the checked-out file — but a partial fetch that HAD rewritten it would have
    replaced a committed reading with an honest-looking null. CLAUDE.md §4."""
    real = M.derive(M._synthetic_cache(ret_peak=True, control_peak=True))
    p = tmp_path / "art.json"
    p.write_text(json.dumps(real), encoding="utf-8")

    empty = M.derive({})
    assert empty["part_2_intersection"]["_status"] == "NOT_RUN"
    assert M.would_downgrade(empty, str(p)) is True

    no_peaks = M.derive({"_generated_utc": "x", "genes": {}, "peaksets": {}})
    assert M.would_downgrade(no_peaks, str(p)) is True

    # A real reading replacing a real reading is fine — that is just a re-run.
    assert M.would_downgrade(real, str(p)) is False
    # And with nothing committed there is nothing to protect.
    assert M.would_downgrade(empty, str(tmp_path / "absent.json")) is False


def test_an_unreadable_committed_artifact_does_not_block_a_write(tmp_path):
    """Fail-open in this one direction on purpose: a corrupt file is not a reading, and refusing
    forever would leave the lane unable to recover from it."""
    p = tmp_path / "art.json"
    p.write_text("{not json", encoding="utf-8")
    assert M.would_downgrade(M.derive({}), str(p)) is False


@pytest.fixture
def no_network(monkeypatch):
    """⛔ These tests must not touch the network. Without this they take 67 s of failing DNS in a
    sandbox whose proxy 403s every one of these hosts — and a test suite that is slow because it is
    quietly making real requests is a test suite nobody runs before the fetch."""
    monkeypatch.setattr(M, "get", lambda *a, **k: b"chr10\t100\t200\tp\t9\n")
    return None


def test_a_retrieval_cap_is_recorded_and_never_silent(no_network):
    """Measured 2026-08-07 (run 31201656452): an arbitrary `[:40]` cut 92 ChIP-Atlas rows to 40
    and no field anywhere said so, so the artifact read as a complete survey of a truncated one."""
    exps = [{"srx": f"SRX{i}", "genome": "hg38", "antigen": "NR4A3", "cell_type": "x",
             "cell_type_class": "x"} for i in range(5)]
    got = M.fetch_chip_atlas_peaks(exps, max_experiments=2)
    assert "_TRUNCATION" in got
    assert got["_TRUNCATION"]["n_dropped"] == 3
    assert got["_TRUNCATION"]["n_experiments_offered"] == 5


def test_the_completeness_record_reaches_the_artifact():
    cache = M._synthetic_cache(ret_peak=True, control_peak=True)
    cache["peaksets"]["_TRUNCATION"] = {"_status": "truncated", "n_dropped": 7}
    a = M.derive(cache)
    assert a["part_2_intersection"]["⛔ retrieval_completeness"]["n_dropped"] == 7
    # ...and the truncation marker must never be counted as a peak set.
    ids = [r["peakset"] for r in a["part_2_intersection"]["ret_summary"]["rows"]]
    assert "_TRUNCATION" not in ids


def test_a_peakset_key_is_scoped_by_build_so_one_build_cannot_overwrite_the_other(no_network):
    """ChIP-Atlas lists each SRX once per genome. Keying on the bare SRX silently halved the data."""
    exps = [{"srx": "SRX1", "genome": "hg19", "antigen": "NR4A3", "cell_type": "x",
             "cell_type_class": "x"},
            {"srx": "SRX1", "genome": "hg38", "antigen": "NR4A3", "cell_type": "x",
             "cell_type_class": "x"}]
    got = M.fetch_chip_atlas_peaks(exps, max_experiments=10)
    assert "SRX1@hg19" in got and "SRX1@hg38" in got


def test_one_experiment_on_two_builds_is_counted_once_as_an_experiment():
    """⛔ A PEAK SET IS NOT AN EXPERIMENT. ChIP-Atlas reprocesses each SRX per genome build, so the
    same reads appear twice. Quoting the peak-set count would read as independent replication."""
    c = M._synthetic_cache(ret_peak=True, control_peak=True)
    c["genes"]["hg19"] = dict(c["genes"]["hg38"])
    only = c["peaksets"].pop("SYNTH")
    for build in ("hg38", "hg19"):
        c["peaksets"][f"SRX_ONE@{build}"] = dict(only, genome=build)
    s = M.derive(c)["part_2_intersection"]["ret_summary"]
    assert s["n_peaksets"] == 2
    assert s["⛔ n_distinct_experiments"] == 1
    assert s["n_distinct_experiments_with_a_RET_promoter_peak"] == 1
    assert s["_experiments_with_a_RET_promoter_peak"] == ["SRX_ONE"]


def test_the_headline_quotes_the_experiment_count_not_the_peakset_count():
    c = M._synthetic_cache(ret_peak=True, control_peak=True)
    c["genes"]["hg19"] = dict(c["genes"]["hg38"])
    only = c["peaksets"].pop("SYNTH")
    for build in ("hg38", "hg19"):
        c["peaksets"][f"SRX_ONE@{build}"] = dict(only, genome=build)
    v = M.derive(c)["verdict"]
    assert "1 OF 1 PUBLIC ChIP-seq EXPERIMENTS" in v["headline"]
    assert "2 of 2 peak sets" in v["headline"]


def test_a_build_whose_service_returned_the_wrong_assembly_yields_NO_coordinates(monkeypatch):
    """⛔ THE DEFECT THIS MODULE EXISTS TO PREVENT, COMMITTED BY THIS MODULE (run 31202485854).

    `rest.ensembl.org` serves only the CURRENT mouse assembly, so the `mm10` lookup returned
    GRCm39. `assembly_matches_expected` correctly went False — and the old code set a note and
    RETURNED THE COORDINATES ANYWAY, so seven ChIP-Atlas mm10 peak sets were intersected against
    GRCm39 loci and two reported `Ret` promoter-window peaks. A WARNING IS NOT A GUARD.
    `intersect_locus` cannot catch it, because by then both sides carry the same build string.
    """
    def fake_post(url, chunk, build, tries=4):
        return {sym: {"id": "ENSMUSGX", "assembly_name": "GRCm39", "seq_region_name": "6",
                      "start": 1, "end": 2, "strand": 1, "biotype": "protein_coding"}
                for sym in chunk}

    monkeypatch.setattr(M, "_post_symbols", fake_post)
    out, diag = M.fetch_gene_spans(list(M.LOCI), "mm10")
    assert diag["assembly_matches_expected"] is False
    assert out == {}, "coordinates from the wrong assembly must be DISCARDED, not flagged"
    assert "⛔ coordinates_discarded" in diag
    assert diag["n_resolved_before_discard"] > 0, (
        "the record must show how many were dropped, or the discard is invisible")

    # ...and the matching build must be unaffected.
    out2, diag2 = M.fetch_gene_spans(list(M.LOCI), "mm39")
    assert diag2["assembly_matches_expected"] is True
    assert out2, "a build whose assembly matches must still return coordinates"


def test_a_429_is_retryable_and_a_404_is_not():
    """A 429 is 'ask again later'; treating it as an answer is what silently disabled the
    independent second source for the genome build."""
    assert 429 in M.RETRYABLE_HTTP
    assert 500 in M.RETRYABLE_HTTP and 503 in M.RETRYABLE_HTTP
    assert 404 not in M.RETRYABLE_HTTP
    assert 403 not in M.RETRYABLE_HTTP


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


# =================================================================================================
# ZENODO — the deep, non-paralogue NR4A3 route (Haller 2019).
# =================================================================================================
def test_the_build_is_read_from_the_deposit_and_ambiguity_refuses():
    """A BED carries no build inside it, and on chr10 a wrong build does not throw — it silently
    reports another locus. So the build is READ from the deposit's own prose, and a deposit naming
    two builds yields None rather than a guess."""
    assert M._build_from_text("NR4A3 ChIP-seq peaks, hg19") == "hg19"
    assert M._build_from_text("aligned to GRCh38") == "hg38"
    assert M._build_from_text("NR4A3_ACC1_hg38_peaks.bed") == "hg38"
    assert M._build_from_text("mapped to hg19 and lifted to hg38") is None
    assert M._build_from_text("no build mentioned") is None
    assert M._build_from_text(None, "") is None


def test_the_zenodo_record_carries_its_not_the_fusion_caveat():
    """Acinic cell carcinoma is NATIVE NR4A3 by enhancer hijacking. A reader of the artifact must
    not be able to reach this peak set without meeting that sentence."""
    for rec, meta in M.ZENODO_RECORDS.items():
        assert "not_the_fusion" in " ".join(meta.keys()), rec
        caveat = meta["⛔ not_the_fusion"]
        assert "NATIVE" in caveat
        assert "never be cited as a fusion cistrome" in caveat
        assert meta["doi"] and meta["pmid"]


def test_zenodo_is_fetched_before_the_catalogue_sweeps_that_would_starve_it():
    """A source's ORDER inside a budget-paced fetch is part of whether it is reachable at all.

    Zenodo was appended at the end of `fetch()` when it was added, which put a few-MB download that
    a run may have been dispatched specifically to get last in line behind ChIP-Atlas and ReMap
    sweeps measured in hundreds of megabytes. The budget is real (`RET_CISTROME_BUDGET_S`) and
    `stream_lines` takes a share of it per catalogue, so the ordering silently made the highest-
    value source the first to record `budget_exhausted`. Nothing else here would catch that: the
    module would report success, the artifact would carry an honest "budget exhausted" line, and
    the one peak set the run existed for would simply be absent.

    Every other source degrades to a recorded partial and is already cached from previous runs.
    This one is the only deep non-paralogue NR4A3 peak set known to be reachable. It goes first.
    """
    import inspect
    src = inspect.getsource(M.fetch)
    z = src.index("fetch_zenodo_peaksets()")
    for later in ("fetch_chip_atlas_peaks(", "for tf, raw in remap_blobs.items()"):
        assert z < src.index(later), (
            f"`fetch_zenodo_peaksets()` now runs AFTER `{later}` — a budget-paced sweep can starve "
            "it, and a starved run reports success with the peak set missing")
    assert src.count("fetch_zenodo_peaksets()") == 1, "fetched twice would double-count peaksets"


def test_peak_like_matching_accepts_beds_and_rejects_prose():
    assert M.PEAKISH.search("NR4A3_peaks.bed.gz")
    assert M.PEAKISH.search("x.narrowPeak")
    assert not M.PEAKISH.search("readme.txt")
    assert not M.PEAKISH.search("figure1.pdf")


# =================================================================================================
# The write guard must protect COVERAGE, not only the presence of a reading
# =================================================================================================
def _art(status="read", n_read=0, n_other=0):
    per = {f"S{i}": {"_status": "read", "antigen": "NR4A1"} for i in range(n_read)}
    per.update({f"X{i}": {"_status": "budget_exhausted"} for i in range(n_other)})
    return {"part_2_intersection": {"_status": status, "per_peakset": per}}


def _write(tmp_path, art):
    p = tmp_path / "committed.json"
    p.write_text(json.dumps(art))
    return str(p)


def test_an_absent_reading_still_cannot_overwrite_a_real_one(tmp_path):
    old = _write(tmp_path, _art("read", n_read=86))
    assert M.would_downgrade(_art("NO_PEAK_SET_RETRIEVED"), out_path=old) is True
    assert M.would_downgrade(_art("NOT_RUN"), out_path=old) is True


def test_a_collapsed_reading_cannot_overwrite_a_full_one(tmp_path):
    """The regression a correct fix introduced, and the reason this test exists.

    `fetch()` used to run its slowest sources last, so a budget-starved run retrieved NOTHING,
    landed on NO_PEAK_SET_RETRIEVED and was refused -- the guard was safe by accident. Moving the
    small, high-value Zenodo fetch to the front (correct on its own terms: it was otherwise the
    first source the budget starved) removed that accident. A starved run now retrieves the five
    Zenodo sets, reports `_status: "read"`, and under the old binary check would have replaced an
    86-peak-set artifact with a five-peak-set one that looks entirely healthy.
    """
    old = _write(tmp_path, _art("read", n_read=86))
    assert M.would_downgrade(_art("read", n_read=5), out_path=old) is True, (
        "a five-peak-set run overwrote an eighty-six-peak-set artifact")
    assert M.would_downgrade(_art("read", n_read=40), out_path=old) is True


def test_ordinary_catalogue_churn_is_not_treated_as_a_partial_fetch(tmp_path):
    """A guard that fires on every re-run gets switched off. Losing one or two experiments to
    catalogue churn is normal; losing most of them is not."""
    old = _write(tmp_path, _art("read", n_read=86))
    assert M.would_downgrade(_art("read", n_read=86), out_path=old) is False
    assert M.would_downgrade(_art("read", n_read=90), out_path=old) is False
    assert M.would_downgrade(_art("read", n_read=80), out_path=old) is False   # ~7% loss
    assert M.COVERAGE_FLOOR == 0.9


def test_only_peaksets_actually_read_count_toward_coverage(tmp_path):
    """A run that ATTEMPTED 86 and read 5 must not pass by counting its failures."""
    old = _write(tmp_path, _art("read", n_read=86))
    assert M.would_downgrade(_art("read", n_read=5, n_other=81), out_path=old) is True


def test_nothing_is_protected_when_the_committed_artifact_is_itself_absent(tmp_path):
    old = _write(tmp_path, _art("NO_PEAK_SET_RETRIEVED"))
    assert M.would_downgrade(_art("read", n_read=5), out_path=old) is False
    assert M.would_downgrade(_art("NOT_RUN"), out_path=old) is False


def test_a_missing_committed_artifact_blocks_nothing(tmp_path):
    assert M.would_downgrade(_art("read", n_read=1),
                             out_path=str(tmp_path / "nope.json")) is False


def test_the_committed_artifact_would_not_refuse_itself():
    """A re-run that reproduces the committed coverage must be writable, or the lane is frozen."""
    if not os.path.exists(M.OUT):
        pytest.skip("cistrome artifact not in this checkout")
    with open(M.OUT) as fh:
        art = json.load(fh)
    assert M._n_peaksets_read(art) > 50, M._n_peaksets_read(art)
    assert M.would_downgrade(art) is False


def test_slowest_attempts_brackets_time_between_consecutive_stamps():
    """`budget_at_s` is a stamp, not a duration; the duration is the gap to the previous stamp.

    Added because a run spent its entire 3000 s budget and retrieved zero peak sets while the
    previous successful run spent 344 s of 2400 s -- and nothing in the artifact could say which
    endpoint absorbed the difference.
    """
    attempts = [{"url": "a", "status": 200, "budget_at_s": 1.0},
                {"url": "b", "status": 200, "budget_at_s": 3.0},
                {"url": "slow", "status": "truncated_at_budget", "budget_at_s": 2900.0},
                {"url": "d", "status": "budget_exhausted", "budget_at_s": 2900.5}]
    rows = M.slowest_attempts(attempts, n=2)
    assert rows[0]["url"] == "slow"
    assert rows[0]["took_s"] == 2897.0
    assert rows[1]["url"] == "b" and rows[1]["took_s"] == 2.0
    assert len(rows) == 2


def test_slowest_attempts_survives_attempts_with_no_stamp():
    """Every artifact committed before the stamp existed has none, and must not raise."""
    assert M.slowest_attempts([{"url": "old", "status": 200}]) == []
    mixed = [{"url": "old", "status": 200}, {"url": "new", "status": 200, "budget_at_s": 5.0}]
    assert [r["url"] for r in M.slowest_attempts(mixed)] == ["new"]


def test_every_recorded_attempt_carries_its_budget_stamp():
    M.ATTEMPTS.clear()
    M._record("https://example.invalid/x", 200, nbytes=10)
    assert "budget_at_s" in M.ATTEMPTS[-1]
    assert isinstance(M.ATTEMPTS[-1]["budget_at_s"], (int, float))
    M.ATTEMPTS.clear()


def test_the_failure_cache_has_its_own_path_and_is_not_the_real_inputs_cache():
    """A guard that protects one of the two files a result rests on protects neither.

    Measured 2026-08-08: the write guard refused a starved run and saved `emc-ret-cistrome.json`,
    the module then wrote its failure cache over `emc-ret-cistrome-inputs.json` "so the failure is
    diagnosable", and the workflow's `always()` publish committed that 2,097-line stub over the
    52 MB peak-coordinate cache (commit 5190923, 4,569,033 deletions). The occupancy module reads
    that cache, so the paper's whole occupancy axis went to DRIFT while the artifact the guard was
    watching stayed pristine. A diagnostic must never be written over the thing being diagnosed.
    """
    assert M.FAILED_INPUTS != M.INPUTS
    assert "FAILED" in os.path.basename(M.FAILED_INPUTS)
    import inspect
    src = inspect.getsource(M.main)
    refusal = src[src.index("REFUSING TO WRITE"):]
    refusal = refusal[:refusal.index("return 3")]
    assert "FAILED_INPUTS" in refusal, "the refusal branch does not use the failure path"
    assert "open(INPUTS" not in refusal, (
        "the refusal branch still writes the real inputs cache -- that is the incident, verbatim")


def test_the_workflow_uploads_the_failure_cache_but_never_publishes_it():
    """The two verbs are opposite here and the distinction is the whole fix.

    UPLOADING the failure cache is how it stays diagnosable with no commit -- the sandbox could not
    reach the last one, which is why the timing stamps had to be added at all. PUBLISHING it is the
    incident: the publish arm is `always()` by design, so any path named there ships whatever is on
    disk, and a 2,097-line failure stub shipped over 52 MB of peak coordinates.
    """
    wf = os.path.join(os.path.dirname(os.path.dirname(MOD)), ".github", "workflows",
                      "emc-expression-datasets.yml")
    if not os.path.exists(wf):
        pytest.skip("workflow not in this checkout")
    with open(wf) as fh:
        text = fh.read()
    name = os.path.basename(M.FAILED_INPUTS)
    assert name in text, "the failure cache is not uploaded, so a refused run is undiagnosable"
    publish = text[text.index("Publish the artifact and the inputs cache"):]
    publish = publish[:publish.index("publish_artifacts.sh")]
    assert name not in publish, (
        "the failure cache is named in the publish arm and would be committed over the real cache")


# =================================================================================================
# The Zenodo merge mode — adding ONE source without re-fetching everything
# =================================================================================================
def _cache_with(n_read, tmp_path, monkeypatch):
    """A committed inputs cache holding `n_read` readable peak sets, at a temp INPUTS path."""
    base = M._synthetic_cache(ret_peak=True, control_peak=True)
    for i in range(n_read):
        base["peaksets"][f"BASE{i}"] = {
            "antigen": "NR4A1", "genome": "hg38", "cell_type": "x", "cell_type_class": "x",
            "qc": None, "peaks": [("chr10", 43_000_000, 43_000_100, 5.0)],
            "diag": {"_status": "read"}, "_status": "read"}
    p = tmp_path / "inputs.json"
    p.write_text(json.dumps(base, default=str))
    monkeypatch.setattr(M, "INPUTS", str(p))
    monkeypatch.setattr(M, "OUT", str(tmp_path / "out.json"))
    monkeypatch.setattr(M, "FAILED_INPUTS", str(tmp_path / "failed.json"))
    return base, p


def test_the_merge_refuses_when_there_is_no_cache_to_merge_into(tmp_path, monkeypatch):
    """This mode ADDS a source to an existing retrieval; it cannot produce one."""
    monkeypatch.setattr(M, "INPUTS", str(tmp_path / "absent.json"))
    monkeypatch.setattr(M, "fetch_zenodo_peaksets", lambda: {"Z": {"_status": "read"}})
    assert M.fetch_zenodo_into_cache() == 4


def test_the_merge_refuses_to_build_on_a_cache_with_no_readable_peak_set(tmp_path, monkeypatch):
    p = tmp_path / "inputs.json"
    p.write_text(json.dumps({"peaksets": {"A": {"_status": "budget_exhausted", "peaks": []}}}))
    monkeypatch.setattr(M, "INPUTS", str(p))
    monkeypatch.setattr(M, "fetch_zenodo_peaksets", lambda: {"Z": {"_status": "read"}})
    assert M.fetch_zenodo_into_cache() == 4


def test_the_merge_refuses_when_the_zenodo_fetch_did_not_run_at_all(tmp_path, monkeypatch):
    """An empty return is not 'the deposit has no peaks' -- the loader emits a record-level refusal
    for that. Empty means it never executed, and merging nothing must not rewrite the cache."""
    _, p = _cache_with(5, tmp_path, monkeypatch)
    before = p.read_text()
    monkeypatch.setattr(M, "fetch_zenodo_peaksets", dict)
    assert M.fetch_zenodo_into_cache() == 4
    assert p.read_text() == before, "the cache was rewritten by a fetch that never ran"


def test_the_merge_keeps_every_existing_peakset_and_adds_the_new_ones(tmp_path, monkeypatch):
    base, p = _cache_with(6, tmp_path, monkeypatch)
    n_before = len(base["peaksets"])
    zen = {"ZENODO1483691:peaks.bed.gz": {
        "antigen": "NR4A3", "genome": "hg38", "cell_type": "acinic cell carcinoma",
        "cell_type_class": "author-deposited peak call (not uniformly reprocessed)", "qc": None,
        "peaks": [("chr10", 43_000_000, 43_000_100, 9.0)], "diag": {"_status": "read"},
        "_status": "read"}}
    monkeypatch.setattr(M, "fetch_zenodo_peaksets", lambda: dict(zen))
    assert M.fetch_zenodo_into_cache() == 0
    merged = json.loads(p.read_text())
    assert len(merged["peaksets"]) == n_before + 1
    for k in base["peaksets"]:
        assert k in merged["peaksets"], f"the merge dropped {k}"
    assert "ZENODO1483691:peaks.bed.gz" in merged["peaksets"]


def test_the_merge_records_that_the_artifact_now_has_two_fetch_dates(tmp_path, monkeypatch):
    """After a merge the artifact is not the product of one run, and a reader comparing dates would
    otherwise have no way to know."""
    base, p = _cache_with(6, tmp_path, monkeypatch)
    monkeypatch.setattr(M, "fetch_zenodo_peaksets", lambda: {"Z:x.bed": {
        "antigen": "NR4A3", "genome": "hg38", "cell_type": "x", "cell_type_class": "x",
        "qc": None, "peaks": [("chr10", 1, 100, 1.0)], "diag": {"_status": "read"},
        "_status": "read"}})
    assert M.fetch_zenodo_into_cache() == 0
    rec = json.loads(p.read_text())["_merged_sources"][-1]
    assert rec["source"] == "zenodo"
    assert rec["base_cache_generated_utc"] == base.get("_generated_utc")
    assert rec["fetched_utc"] and rec["fetched_utc"] != rec["base_cache_generated_utc"]
    assert "MERGE of two retrievals" in rec["⚠"]
    assert rec["peaksets_added"] == ["Z:x.bed"]


def test_the_merge_is_still_subject_to_the_coverage_guard(tmp_path, monkeypatch):
    """The merge cannot be a back door around the guard that the full fetch has to clear."""
    _, p = _cache_with(6, tmp_path, monkeypatch)
    rich = _art("read", n_read=86)
    with open(M.OUT, "w") as fh:
        json.dump(rich, fh)
    monkeypatch.setattr(M, "fetch_zenodo_peaksets", lambda: {"Z:x.bed": {
        "antigen": "NR4A3", "genome": "hg38", "cell_type": "x", "cell_type_class": "x",
        "qc": None, "peaks": [("chr10", 1, 100, 1.0)], "diag": {"_status": "read"},
        "_status": "read"}})
    before = p.read_text()
    assert M.fetch_zenodo_into_cache() == 3
    assert p.read_text() == before, "a refused merge rewrote the real inputs cache"
    assert os.path.exists(M.FAILED_INPUTS)
