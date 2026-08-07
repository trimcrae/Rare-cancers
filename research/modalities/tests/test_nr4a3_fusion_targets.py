#!/usr/bin/env python3
"""Offline tests for `nr4a3_fusion_targets.py`.

⭐ WHY THEY RUN BEFORE THE FETCH. The derive half must be exercisable with no network, so a broken
reduction fails in seconds rather than after a GEO round trip — and, more to the point, so no
artifact can be emitted by a build whose arithmetic is unproven.

⛔ THE PROPERTIES UNDER TEST ARE THE HONESTY ONES, NOT THE ARITHMETIC ONES:
   1. an absent reading is never rendered as a reading of absence;
   2. a set that only rides the platform's global offset is REFUSED, not reported as a finding —
      this is the property the whole module exists for, and it is tested with a CONSTRUCTED
      offset whose right answer is known;
   3. the circularity flag is graded from a fetched record and says UNANSWERED when the record is
      missing, rather than defaulting to "clean";
   4. every literature row carries an assay, a citation with an identifier, and the verbatim
      sentence its classification rests on.
"""
import json
import os
import random
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import nr4a3_fusion_targets as M  # noqa: E402


# =============================================================================================
# A synthetic inputs cache whose right answers are known by construction.
# =============================================================================================
def _make_inputs(offset=0.0, spike=None, n_emc=6, n_comp=12, n_pool=400, seed=7):
    """EMC and comparator samples over `n_pool` background genes plus every named gene.

    `offset` shifts EVERY gene in the EMC arm — the platform-wide artefact this module exists to
    strip. `spike` maps gene -> extra shift applied ON TOP, i.e. genuine set-specific signal.
    """
    rng = random.Random(seed)
    spike = spike or {}
    named = sorted(M._wanted_genes())
    pool = [f"BG{i:05d}" for i in range(n_pool)]
    all_genes = named + pool
    samples = ([{"gsm": f"GSM_E{i}", "annotation_verbatim": f"extraskeletal myxoid chondrosarcoma {i}"}
                for i in range(n_emc)] +
               [{"gsm": f"GSM_C{i}", "annotation_verbatim": f"synovial sarcoma {i}"}
                for i in range(n_comp)])
    n_s = len(samples)
    genes, pool_vals = {}, {}
    for g in all_genes:
        vals = []
        for i in range(n_s):
            base = rng.gauss(0.0, 1.0)
            if i < n_emc:
                base += offset + spike.get(g, 0.0)
            vals.append(round(base, 4))
        if g in named:
            genes[g] = {"probe_ids": [f"p_{g}"], "n_probes_mapping": 1, "values": vals,
                        "array_percentile": [0.5] * n_s}
        else:
            pool_vals[g] = vals
    # background: mean 0, sd 1 per sample, so z == value and the arithmetic is checkable by hand
    bg = [{"mean": 0.0, "sd": 1.0, "n": len(all_genes)} for _ in range(n_s)]
    tot = [0.0] * n_s
    for g in all_genes:
        v = genes[g]["values"] if g in genes else pool_vals[g]
        for i in range(n_s):
            tot[i] += v[i]
    tgt = {
        "_status": "read", "gse": "GSEFAKE", "matrix_file": "FAKE_series_matrix.txt.gz",
        "platform": "GPLFAKE", "platform_expected": "GPLFAKE", "platform_matches_expected": True,
        "why": "synthetic", "prior_probe_mapping_rate": 0.9, "prior_source": "test",
        "n_samples": n_s, "n_probes": len(all_genes),
        "n_probes_mapped_to_a_symbol": len(all_genes),
        "measured_probe_mapping_rate": 1.0,
        "n_distinct_symbols_on_platform": len(all_genes),
        "probe_symbol_mapping": {"accession_resolution_rate": 0.9},
        "samples": samples, "background_per_sample": bg,
        "value_kind": "synthetic", "frac_negative_values": 0.5,
        "all_symbol_mean_z_per_sample": [round(tot[i] / len(all_genes), 6) for i in range(n_s)],
        "all_symbol_n_per_sample": [len(all_genes)] * n_s,
        "null_pool_spec": {"seed": 1, "requested": n_pool, "drawn": n_pool,
                           "universe": len(all_genes)},
        "genes": genes, "null_pool_values": pool_vals,
        "n_wanted_genes_measured": len(genes), "n_wanted_genes_requested": len(named),
    }
    return {"_generated_utc": "2026-08-07T00:00:00+00:00",
            "pparg_arms": {"slots": {}, "n_slots_resolved": 0, "diagnostics": []},
            "n_genes_wanted": len(named), "null_draws": 200,
            "series_records": {}, "targets": {"FAKE_series_matrix.txt.gz": tgt}}


@pytest.fixture(scope="module")
def flat():
    return M.derive(_make_inputs(offset=0.0))


# =============================================================================================
# 1 · The evidence table itself.
# =============================================================================================
def test_every_literature_row_names_an_assay_a_citation_and_a_verbatim_sentence():
    for row in M.LITERATURE_TARGETS:
        g = row["gene"]
        assert row.get("assays"), f"{g}: no assay recorded"
        assert row.get("citation"), f"{g}: no citation"
        assert row.get("verbatim"), f"{g}: no verbatim sentence"
        assert row.get("system"), f"{g}: no cell system"
        assert row.get("species_of_the_cells"), f"{g}: species not recorded"
        assert row.get("expected_direction_in_EMC"), f"{g}: no expected direction"
        assert row.get("why_that_direction"), f"{g}: direction asserted without a reason"


def test_every_citation_carries_a_resolvable_identifier():
    """A claim without a PMID/PMCID/DOI is not citable and must not be in the table."""
    import re
    pat = re.compile(r"(PMID\s*\d{5,9}|PMCID\s*PMC\d{5,9}|PMC\d{5,9}|doi\s*10\.\d{4,9}/)", re.I)
    for row in M.LITERATURE_TARGETS + [M.PUBLISHED_NEGATIVE]:
        assert pat.search(row["citation"]), f"{row['gene']}: citation has no identifier"


def test_evidence_classes_are_from_the_closed_vocabulary():
    ok = {M.FUSION_DNA_BINDING, M.NATIVE_DNA_BINDING, M.FUSION_EXPRESSION,
          M.EMC_TISSUE_EXPRESSION}
    for row in M.LITERATURE_TARGETS:
        assert row["evidence_class"] in ok, row["gene"]


def test_a_fusion_class_row_actually_names_a_fusion_and_a_native_class_row_does_not():
    """⛔ THE COLUMN THAT MATTERS. Class A exists to mean 'assayed with a chimera'. A row filed
    there that names only native NR4A3 would silently promote the weaker claim."""
    for row in M.LITERATURE_TARGETS:
        names = " ".join(row.get("factor_tested") or [])
        if row["evidence_class"] in (M.FUSION_DNA_BINDING, M.FUSION_EXPRESSION):
            assert "::" in names, f"{row['gene']} is filed as a FUSION row but names no fusion"
        if row["evidence_class"] == M.NATIVE_DNA_BINDING:
            assert "::" not in names, (f"{row['gene']} is filed as a NATIVE row but names a "
                                       f"fusion — it belongs in class A")


def test_the_transfer_assumption_is_recorded_as_falsified_not_assumed():
    """Filion et al. measured native NR4A3 FAILING to activate the PPARG promoter the fusion
    activates. If that sentence ever leaves the PPARG row, the table starts implying that a
    native-NR4A3 target list predicts fusion targets."""
    pparg = next(r for r in M.LITERATURE_TARGETS if r["gene"] == "PPARG")
    assert "do not activate PPARG" in pparg["note"]
    sema = next(r for r in M.LITERATURE_TARGETS if r["gene"] == "SEMA3C")
    assert "impaired by TAF15-NR4A3" in sema["verbatim"]


def test_ENO3_row_says_out_loud_that_the_fusion_assayed_was_not_EWSR1():
    eno3 = next(r for r in M.LITERATURE_TARGETS if r["gene"] == "ENO3")
    assert any("TFG::NR4A3" in f for f in eno3["factor_tested"])
    assert not any("EWSR1::NR4A3" in f for f in eno3["factor_tested"])
    assert "NOT EWSR1::NR4A3" in eno3["note"]


def test_SGK1_is_registered_as_a_transcript_level_discordance_not_an_up_prediction():
    """The published protein direction and transcript direction OPPOSE. A table that recorded only
    'SGK1 is induced by the fusion' would make a correct flat read look like a failure."""
    sgk1 = next(r for r in M.LITERATURE_TARGETS if r["gene"] == "SGK1")
    assert sgk1["expected_direction_in_EMC"] == "FLAT_OR_DOWN_AT_TRANSCRIPT_LEVEL"


def test_exactly_one_row_predicts_DOWN_and_it_is_PLAGL1():
    down = [r["gene"] for r in M.LITERATURE_TARGETS
            if r["expected_direction_in_EMC"] == "DOWN"]
    assert down == ["PLAGL1"], down


# =============================================================================================
# 2 · An absent reading is never a reading of absence.
# =============================================================================================
def test_an_unreadable_gene_says_the_read_could_not_be_taken(flat):
    inp = _make_inputs()
    tgt = inp["targets"]["FAKE_series_matrix.txt.gz"]
    del tgt["genes"]["PPARG"]
    res = M.derive(inp)
    r = res["gene_reads"]["PPARG"]["FAKE_series_matrix.txt.gz"]
    assert r["readable"] is False
    assert "NOT READABLE" in r["verdict"]
    assert "NOTHING about whether" in r["verdict"]
    assert "not expressed" not in r["verdict"]


def test_every_unreadable_verdict_anywhere_in_the_artifact_carries_its_refusal(flat):
    """Walk the whole serialised artifact: any verdict that reports a failure to read must say so
    in words a reader cannot mistake for a biological zero."""
    bad = []

    def walk(o, path=""):
        if isinstance(o, dict):
            v = o.get("verdict")
            if isinstance(v, str) and o.get("readable") is False:
                if "NOT READABLE" not in v or "NOTHING about" not in v:
                    bad.append(path)
            for k, vv in o.items():
                walk(vv, f"{path}/{k}")
        elif isinstance(o, list):
            for i, vv in enumerate(o):
                walk(vv, f"{path}[{i}]")

    walk(json.loads(json.dumps(flat)))
    assert not bad, bad


def test_an_unreadable_gene_with_a_documented_alias_says_the_alias_was_not_CHECKED():
    """⛔ THE SUBTLE HALF. Adding an alias to the wanted list without a re-fetch would emit a row
    whose stated reason ('no probe maps to it') the collector never checked. So an unreadable gene
    with a known former symbol must say UNKNOWN, and must say the alias was not requested."""
    inp = _make_inputs()
    tgt = inp["targets"]["FAKE_series_matrix.txt.gz"]
    del tgt["genes"]["PDP1"]
    r = M.derive(inp)["gene_reads"]["PDP1"]["FAKE_series_matrix.txt.gz"]
    assert r["readable"] is False
    assert r["alias_status"] == "UNKNOWN"
    assert "PPM2C" in r["documented_aliases"]
    assert "ALIAS UNCHECKED" in r["verdict"]
    assert "not\nabsent" in r["_alias_note"] or "not absent" in r["_alias_note"].replace("\n", " ")


def test_no_alias_is_smuggled_into_the_wanted_list_without_a_refetch():
    """The map is a DIAGNOSTIC, not a lookup. If a future edit adds these to `_wanted_genes`, the
    next inputs cache must be regenerated in the same change — this test fails first."""
    want = M._wanted_genes()
    for gene, aliases in M.SYMBOL_HISTORY.items():
        for a in aliases:
            if a in ("CSPG2", "C10orf116"):
                continue  # deliberately requested: they are the Filion-table spellings
            assert a not in want, (f"{a} is in the wanted list; if that is intended, the inputs "
                                   f"cache must be refetched in the same change")


def test_an_unread_platform_is_not_silently_dropped():
    inp = _make_inputs()
    inp["targets"]["FAKE_series_matrix.txt.gz"]["_status"] = "fetch failed: 404"
    res = M.derive(inp)
    p = res["platforms"]["FAKE_series_matrix.txt.gz"]
    assert p["_status"].startswith("fetch failed")
    assert "NOT READ" in p["_means"]


def test_an_absent_null_pool_refuses_to_call_a_set_specific():
    inp = _make_inputs()
    inp["targets"]["FAKE_series_matrix.txt.gz"]["null_pool_values"] = {}
    res = M.derive(inp)
    r = res["set_scores"]["A_plus_B_all_dna_binding"]["FAKE_series_matrix.txt.gz"]
    assert r["null_calibration"]["computed"] is False
    assert "NOT INTERPRETABLE" in r["verdict"]


def test_an_absent_all_symbol_vector_refuses_to_report_a_global_offset():
    inp = _make_inputs()
    inp["targets"]["FAKE_series_matrix.txt.gz"]["all_symbol_mean_z_per_sample"] = []
    res = M.derive(inp)
    go = res["platforms"]["FAKE_series_matrix.txt.gz"]["global_offset"]
    assert go["measured"] is False
    assert "NOT MEASURED" in go["why"]


# =============================================================================================
# 3 · ★★ THE PROPERTY THE MODULE EXISTS FOR: a global offset must not read as a finding.
# =============================================================================================
def test_a_pure_global_offset_produces_a_big_raw_delta_and_is_REFUSED_by_the_null():
    """Every gene in the EMC arm is shifted by +0.8 SD and NOTHING is set-specific. The raw
    contrast must be large and the null verdict must refuse it. This is the exact shape of the
    GPL3290 reading that motivated the module."""
    res = M.derive(_make_inputs(offset=0.8))
    mf = "FAKE_series_matrix.txt.gz"
    go = res["platforms"][mf]["global_offset"]
    assert go["measured"] and go["welch"]["delta_a_minus_b"] > 0.5
    r = res["set_scores"]["A_plus_B_all_dna_binding"][mf]
    assert r["score"]["delta_a_minus_b"] > 0.4, "the raw contrast should look impressive"
    assert "NOT DISTINGUISHABLE FROM A RANDOM GENE SET" in r["null_calibration"]["verdict"]
    assert r["null_calibration"]["p_empirical_two_sided"] > 0.05


def test_a_genuine_set_specific_signal_on_top_of_the_same_offset_IS_detected():
    """The other half of the same test — a guard that refuses everything is not a guard."""
    genes = sorted({r["gene"] for r in M.LITERATURE_TARGETS
                    if r["evidence_class"] in (M.FUSION_DNA_BINDING, M.NATIVE_DNA_BINDING)})
    res = M.derive(_make_inputs(offset=0.8, spike={g: 2.0 for g in genes}))
    r = res["set_scores"]["A_plus_B_all_dna_binding"]["FAKE_series_matrix.txt.gz"]
    assert "SET-SPECIFIC" in r["null_calibration"]["verdict"]
    assert r["null_calibration"]["p_empirical_two_sided"] < 0.05


def test_the_null_is_centred_on_the_offset_not_on_zero():
    """The whole mechanism: a random set carries the offset too, so the null's MEAN must track the
    offset. If it did not, the calibration would be doing nothing."""
    mf = "FAKE_series_matrix.txt.gz"
    lo = M.derive(_make_inputs(offset=0.0))["set_scores"]["A_plus_B_all_dna_binding"][mf]
    hi = M.derive(_make_inputs(offset=0.8))["set_scores"]["A_plus_B_all_dna_binding"][mf]
    assert abs(lo["null_calibration"]["null_mean_delta"]) < 0.25
    assert hi["null_calibration"]["null_mean_delta"] > 0.5


def test_the_empirical_p_can_never_be_zero():
    srt = sorted(random.Random(0).gauss(0, 1) for _ in range(500))
    _, _, p = M._empirical_p(srt, 99.0)
    assert p > 0
    _, _, p2 = M._empirical_p(srt, -99.0)
    assert p2 > 0


def test_a_set_below_the_coverage_floor_emits_UNDERPOWERED_and_no_number():
    inp = _make_inputs()
    tgt = inp["targets"]["FAKE_series_matrix.txt.gz"]
    for g in list(M.FILION_TABLE1)[:20]:
        tgt["genes"].pop(g, None)
    res = M.derive(inp)
    r = res["set_scores"]["D_filion_table1_emc_vs_137_sarcomas"]["FAKE_series_matrix.txt.gz"]
    assert r["score"] is None
    assert "UNDERPOWERED" in r["verdict"]
    assert "instrument limit, not a reading of the biology" in r["verdict"]


def test_every_emitted_set_score_carries_a_null_calibration(flat):
    for name, per in flat["set_scores"].items():
        for mf, r in per.items():
            if r.get("score") is not None:
                assert "null_calibration" in r, f"{name}/{mf} emitted a score with no null"


def test_the_raw_verdict_tells_the_reader_not_to_quote_it_alone(flat):
    for name, per in flat["set_scores"].items():
        for r in per.values():
            if r.get("raw_verdict"):
                assert "RAW" in r["raw_verdict"]


# =============================================================================================
# 4 · Circularity is graded from a record, and says UNANSWERED when there is none.
# =============================================================================================
def test_circularity_is_unanswered_when_the_series_record_was_not_read():
    res = M.derive(_make_inputs())
    c = res["circularity_reading"]
    assert c["graded"] is False
    assert "UNANSWERED" in c["verdict"]
    assert "POSSIBLY CIRCULAR" in c["verdict"]


def test_circularity_is_confirmed_when_the_record_names_the_study():
    inp = _make_inputs()
    inp["series_records"] = {"GSE4303": {
        "_status": "read",
        "fields_verbatim": {"!Series_title": ["Extraskeletal myxoid chondrosarcoma"],
                            "!Series_pubmed_id": ["15920699"],
                            "!Series_contributor": ["S,,Subramanian"]}}}
    c = M.derive(inp)["circularity_reading"]
    assert c["confirmed_same_cohort"] is True
    assert "CONFIRMED CIRCULAR" in c["verdict"]


def test_circularity_is_NOT_confirmed_when_the_record_names_someone_else():
    inp = _make_inputs()
    inp["series_records"] = {"GSE4303": {
        "_status": "read",
        "fields_verbatim": {"!Series_title": ["Some other sarcoma study"],
                            "!Series_pubmed_id": ["99999999"],
                            "!Series_contributor": ["A,,Nobody"]}}}
    c = M.derive(inp)["circularity_reading"]
    assert c["confirmed_same_cohort"] is False
    assert "NOT CONFIRMED" in c["verdict"]
    assert "suspect rather than clean" in c["verdict"]


def test_the_circular_set_carries_the_circularity_verdict_in_its_own_caveat(flat):
    d = flat["set_definitions"]["E_filion_table2_overlap_with_subramanian"]
    assert "CIRCULAR ON GPL3290" in d["caveat"]


def test_the_independent_replication_set_is_not_derived_from_either_readable_series(flat):
    d = flat["set_definitions"]["D_filion_table1_emc_vs_137_sarcomas"]
    assert "INDEPENDENT replication set" in d["expected"]
    assert "NOT a fusion target list" in d["caveat"]


# =============================================================================================
# 5 · Controls.
# =============================================================================================
def test_the_controls_block_is_emitted_before_any_biology_is_quotable(flat):
    c = flat["controls"]
    for name in ("positive_control_ENO3", "the_fusion_itself_NR4A3",
                 "directional_falsifier_PLAGL1", "prereg_discordance_SGK1"):
        assert name in c["checks"], name
        assert "expect" in c["checks"][name]


def test_a_failing_positive_control_flips_all_checks_pass_and_says_so():
    """⛔ The control must be able to FAIL. A control that cannot fail is decoration."""
    inp = _make_inputs(spike={"ENO3": -5.0})
    res = M.derive(inp)
    assert res["controls"]["checks"]["positive_control_ENO3"]["pass"] is False
    assert res["controls"]["all_checks_pass"] is False
    assert "DID NOT COME BACK AS PUBLISHED" in res["controls"]["_reading"]


def test_the_controls_pass_when_the_synthetic_data_is_built_to_the_published_directions():
    inp = _make_inputs(spike={"ENO3": 3.0, "NR4A3": 3.0, "PLAGL1": -3.0, "SGK1": -1.0})
    res = M.derive(inp)
    assert res["controls"]["all_checks_pass"] is True


def test_the_ENO3_control_points_at_the_one_home_of_its_prior(flat):
    e = flat["controls"]["checks"]["positive_control_ENO3"]
    assert "emc-expression-panels.json" in e["expect"]
    assert "0.808" in e["expect"] and "3.811" in e["expect"]


# =============================================================================================
# 6 · The honest frame travels with the artifact.
# =============================================================================================
def test_the_discriminator_section_names_a_dataset_with_an_accession(flat):
    txt = json.dumps(flat["_what_this_cannot_conclude"])
    assert "EGAS00001002795" in txt
    assert "zenodo.1483691" in txt
    assert "30664630" in txt


def test_the_discriminator_section_states_the_AciCC_caveat_rather_than_selling_the_dataset(flat):
    txt = json.dumps(flat["_what_this_cannot_conclude"])
    assert "NATIVE NR4A3" in txt and "NOT a fusion" in txt


def test_the_no_fusion_cistrome_finding_is_stated_as_a_bounded_search_not_as_absence(flat):
    """⛔ THE MOST QUOTABLE SENTENCE IN THE FILE AND THE EASIEST TO OVERSTATE. It must carry the
    corpus sizes it was measured over and must refuse the 'no such dataset exists' reading."""
    b = flat["_what_this_cannot_conclude"]["1b_no_fusion_cistrome_exists_in_the_retrieved_literature"]
    assert b["totals"]["fulltext_documents_scanned"] == 2276
    assert b["totals"]["documents_naming_both_a_cistrome_method_and_NR4A3_NOR1_TEC"] == 153
    assert "ZERO" in b["result"]
    txt = json.dumps(b)
    assert "not all of PubMed" in txt
    assert "ABSENT READING IS NOT A READING" in txt.upper()
    assert sum(v["fulltext_files"] for v in b["corpora_searched"].values()) == 2276


def test_the_coordination_note_says_what_is_needed_rather_than_fetching_it(flat):
    txt = flat["_what_this_cannot_conclude"]["3_coordination_note"]
    assert "does NOT fetch" in txt
    assert "genome build" in txt


def test_no_efficacy_or_selectivity_language_anywhere_in_the_artifact(flat):
    """R1-R5 in `lint_claims.py` guard the manuscripts. This guards the artifact, because a JSON
    field is quoted into prose more often than it is read."""
    txt = json.dumps(flat).lower()
    for bad in ("is effective", "efficacy in emc", "well tolerated", "therapeutic window for",
                "clinically ready", "safe and effective", "selectively kills"):
        assert bad not in txt, bad


def test_the_limits_name_the_sample_sizes_and_the_fusion_type_mixture(flat):
    txt = " ".join(flat["_limits"])
    assert "n = 6 EMC" in txt and "n = 10 EMC" in txt
    assert "Fusion type is not recorded" in txt


def test_the_null_limitation_is_stated_rather_than_hidden(flat):
    txt = " ".join(flat["_limits"])
    assert "gene-gene correlation" in txt
    assert "ANTI-CONSERVATIVE" in txt


# =============================================================================================
# 7 · The species rule: derived from the matched term, never assumed.
# =============================================================================================
@pytest.mark.parametrize("term,expect", [
    ("PPARG DEFICIENCY MOUSE GSE23421 CREEDSID GENE 1231 DOWN", "mouse"),
    ("PPARG 19300518 ChIP-PET 3T3-L1 Mouse", "mouse"),
    ("PPARG human", "human"),
    ("Adipogenesis", "unstated in the term"),
])
def test_species_is_derived_from_the_term(term, expect):
    assert M._species_of_term(term) == expect


def test_an_unresolved_pparg_arm_is_recorded_as_an_absent_reading_not_substituted():
    arms = {"slots": {"pparg_OE_UP": {"resolved": False, "why_not": "⛔ TERM NOT PRESENT VERBATIM"}},
            "n_slots_resolved": 0}
    inp = _make_inputs()
    inp["pparg_arms"] = arms
    res = M.derive(inp)
    assert "PPARG_pparg_OE_UP" not in res["set_definitions"]
    assert "pparg_OE_UP" in res["reads"]["read_4_pparg_ACTIVITY_resolved_or_bounded"][
        "arms_unresolved"]


def test_a_resolved_pparg_arm_is_scored_and_null_calibrated():
    named = sorted(M._wanted_genes())
    inp = _make_inputs()
    tgt = inp["targets"]["FAKE_series_matrix.txt.gz"]
    # give the arm real, readable members drawn from the null pool so coverage clears the floor
    members = sorted(tgt["null_pool_values"])[:40]
    for g in members:
        tgt["genes"][g] = {"probe_ids": [f"p_{g}"], "n_probes_mapping": 1,
                           "values": tgt["null_pool_values"][g],
                           "array_percentile": [0.5] * tgt["n_samples"]}
    inp["pparg_arms"] = {"slots": {"pparg_KO_DOWN": {
        "resolved": True, "genes": members, "n_genes": len(members),
        "matched_term_verbatim": M.PPARG_ARMS["pparg_KO_DOWN"]["term"],
        "species_derived_from_the_matched_term": "mouse",
        "citation": "test"}}, "n_slots_resolved": 1}
    res = M.derive(inp)
    r = res["set_scores"]["PPARG_pparg_KO_DOWN"]["FAKE_series_matrix.txt.gz"]
    assert r["score"] is not None
    assert r["null_calibration"]["computed"] is True
    assert named  # the named-gene reads still exist alongside


def test_read_4_records_the_species_of_every_arm_including_the_unresolved_ones(flat):
    r4 = flat["reads"]["read_4_pparg_ACTIVITY_resolved_or_bounded"]
    assert set(r4["species_of_each_arm"]) == set(M.PPARG_ARMS)
    assert "abundance" in r4["the_abundance_question_is_elsewhere"].lower()
    assert "pparg-direction-emc.md" in r4["the_abundance_question_is_elsewhere"]


# =============================================================================================
# 8 · Structural invariants.
# =============================================================================================
def test_the_set_definitions_and_the_scores_cover_the_same_sets(flat):
    assert set(flat["set_definitions"]) == set(flat["set_scores"])


def test_no_set_pools_a_fusion_assay_with_a_native_one_without_saying_so(flat):
    d = flat["set_definitions"]["A_plus_B_all_dna_binding"]
    assert "Pools a fusion assay with a native one" in d["caveat"]


def test_the_class_C_set_declares_that_it_has_no_aggregate_expectation(flat):
    d = flat["set_definitions"]["C_fusion_expression_only"]
    assert "NO AGGREGATE EXPECTATION" in d["expected"]


def test_gene_reads_cover_every_named_gene_in_the_evidence_table(flat):
    for row in M.LITERATURE_TARGETS + [M.PUBLISHED_NEGATIVE]:
        assert row["gene"] in flat["gene_reads"], row["gene"]


def test_the_artifact_serialises(flat):
    assert len(json.dumps(flat)) > 5000


def test_the_null_draw_is_reproducible_from_the_seed():
    a = M.derive(_make_inputs(offset=0.3))["set_scores"]["A_plus_B_all_dna_binding"]
    b = M.derive(_make_inputs(offset=0.3))["set_scores"]["A_plus_B_all_dna_binding"]
    ka = a["FAKE_series_matrix.txt.gz"]["null_calibration"]
    kb = b["FAKE_series_matrix.txt.gz"]["null_calibration"]
    assert ka["null_mean_delta"] == kb["null_mean_delta"]
    assert ka["p_empirical_two_sided"] == kb["p_empirical_two_sided"]
