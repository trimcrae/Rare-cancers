#!/usr/bin/env python3
"""The off-target tissue-expression read, and the guards that stop it over-claiming.

⛔ WHY THIS EXISTS. This is the one check that most changes what the manuscript can say about its
one clinically-relevant reagent, and it is the check most likely to be misread in the flattering
direction. Three specific misreadings are asserted against here, because each of them produces a
file that looks exactly like a correct one:

  1. an absent row rendering as "not expressed" — the failure CLAUDE.md §4 is written about, and
     the one that would let two uncharacterised loci be reported as clean;
  2. a shifted GCT parse emitting tissue figures that are internally consistent and wrong;
  3. a transcript-record count being read as a risk ranking, which would make ANKS1B and ZNF667 the
     headline finding on the strength of nothing but RefSeq annotation depth.

A finding that arrives with a number attached is exactly the kind that drifts when prose is next
edited, so every locus count here is asserted against the committed screen rather than a remembered
value. A failure means the two have diverged; fix whichever is wrong and do not relax the assertion.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ART = os.path.join(MOD, "aso-offtarget-tissue-expression.json")
SCREEN = os.path.join(MOD, "junction-aso-offtarget-e12n3-deep500-b1.json")
sys.path.insert(0, MOD)

import aso_offtarget_tissue_expression as m  # noqa: E402


#: ⛔ NOT SKIPS (2026-08-19, lane C2 audit). Every screen and artifact this file reads is
#: COMMITTED, so an absence is a broken tree, never a partial checkout — and a guard that
#: disappears with its input reports green for a check nobody performed.
def _art():
    if not os.path.exists(ART):
        pytest.fail(f"the tissue-expression artifact is missing at {ART}; it is committed, and the "
                    "lead reagents' off-target loads are unchecked without it.")
    return json.load(open(ART, encoding="utf-8"))


def _screen():
    if not os.path.exists(SCREEN):
        pytest.fail(f"the deep off-target screen is missing at {SCREEN}; it is committed, and the "
                    "locus set this file derives is read from it.")
    return json.load(open(SCREEN, encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The locus set — derived, never typed
# ─────────────────────────────────────────────────────────────────────────────────────────────

def test_the_lead_reagents_six_loci_are_derived_from_the_committed_screen():
    """⛔ THE ONE TABLE THE LEAD REAGENT HANGS ON. If the screen is re-run and the loci move, this
    fails rather than letting a stale six-row table be read as current.

    ⭐ THIS SET IS UNCHANGED BY THE 2026-08-13 LOCUS-PARSER CORRECTION, and that was CHECKED rather
    than assumed. The old parser returned 14 pseudo-loci here because GMCL1's nine records fell to
    accession fallbacks; the corrected parser merges them onto GMCL1 and returns the same six genes
    with the same record counts. A parser fix that had moved this table would have moved a number
    the manuscript quotes.
    """
    _, rows, prov = m._locus_rows(path=m.SCREEN, reagent=m.REAGENT)
    assert prov["n_gap_paired_hybridisable"] == 123
    assert prov["n_loci_over_the_whole_panel"] == 6
    got = {r["locus"]: r["n_transcript_records"] for r in rows}
    assert got == {"ANKS1B": 67, "ZNF667": 37, "GMCL1": 9,
                   "LOC105374140": 5, "LOC105370997": 4, "CHST5": 1}
    assert sum(got.values()) == prov["n_gap_paired_hybridisable"]


def test_the_lead_reagents_load_replicates_across_three_independent_screens():
    """⭐ THE LOAD IS A PROPERTY OF THE SEQUENCE, NOT OF ONE SCREEN.

    The multi-partner reagent was screened three times — once per donor seam — under three
    different BLAST request ids and three different parent-exclusion sets, and all three return the
    identical 123 hits over the identical six loci. That is independent replication, and asserting
    it here stops a future single-screen regression from looking like a real change in the load.
    """
    seen = {}
    for name in ("junction-aso-offtarget-e12n3-deep500-b1.json",
                 "junction-aso-offtarget-taf15e11n3-deep500-b1.json",
                 "junction-aso-offtarget-fuse10n3-deep500-b2.json"):
        p = os.path.join(MOD, name)
        if not os.path.exists(p):
            pytest.fail(f"{name} is missing at {p}; all three independent deep screens are "
                        "committed, and the three-query agreement below is what stops a "
                        "single-screen regression reading as a real change in the load.")
        oligo, gap_paired = m._screen_hits(path=p, reagent=m.REAGENT)
        counts = {}
        for h in gap_paired:
            counts[m.gene_of(h)] = counts.get(m.gene_of(h), 0) + 1
        seen[name] = (oligo["blast_rid"], counts)
    rids = {v[0] for v in seen.values()}
    assert len(rids) == 3, f"these are not three independent queries: {rids}"
    tables = list({json.dumps(v[1], sort_keys=True) for v in seen.values()})
    assert len(tables) == 1, f"the three screens disagree about the load: {seen}"
    assert json.loads(tables[0])["ANKS1B"] == 67


def test_the_taf15_exon6_seam_is_covered_and_is_not_six_loci():
    """⛔ THE SECOND REAGENT'S SEAM, AND THE COUNT THAT MUST NOT BE UNDERSTATED.

    The exon 6 seam is the only exon-resolved TAF15::NR4A3 breakpoint published in EMC, so its
    designs are the second real reagent in the paper. Across the five screened designs its
    gap-paired load recounts to SEVENTEEN loci, not six — a panel covering six of them and
    reporting "the exon 6 seam's off-targets" would be an incomplete panel presented as complete.
    """
    entry = [e for e in m.PANEL if e["seam"] == "TAF15_e6__NR4A3_e3"]
    assert entry, "the exon 6 seam is not in the panel"
    per, prov = m._seam_rows(entry[0])
    assert prov["n_designs"] == 5, "the seam's designs were subset somewhere"
    assert prov["n_loci"] == 17, f"the exon 6 seam returns {prov['n_loci']} loci"
    counts = {k: v["n_transcript_records"] for k, v in per.items()}
    assert sum(counts.values()) == prov["n_gap_paired_hybridisable"] == 155
    # the six named in the brief are present — and so are the ones the brief did not name
    for g in ("NRP1", "ZFPM2", "CA5B", "G3BP2", "GNAL", "SLC17A3"):
        assert g in counts, g
    for g in ("LINC02030", "MIR9-2HG", "LAMA4"):
        assert g in counts, f"{g} carries more records than three of the named six and is missing"
    assert counts["G3BP2"] == 56 and counts["LINC02030"] == 22


def test_recurrence_across_registers_is_carried_separately_from_record_count():
    """⭐ TWO AXES, AND NEITHER MAY STAND IN FOR THE OTHER.

    NRP1 is returned by all five designs at the exon 6 seam on only five transcript records; G3BP2
    is returned by two designs on fifty-six. Ranking by record count buries NRP1; ranking by
    recurrence buries G3BP2. The artifact carries both, per locus, with the note saying why.
    """
    _, rows, _ = m._locus_rows()
    by = {r["locus"]: r for r in rows}
    assert by["NRP1"]["n_designs_hitting_it"] == 5
    assert by["NRP1"]["n_transcript_records"] == 5
    assert by["G3BP2"]["n_designs_hitting_it"] == 2
    assert by["G3BP2"]["n_transcript_records"] == 56
    art = m.derive(m._empty_inputs())
    for p in art["per_locus"]:
        note = p["⭐_recurrence_is_a_second_axis_and_not_the_record_count"]
        assert "robust to tiling register" in note


def test_every_hit_is_two_mismatches_which_is_what_bounds_the_whole_claim():
    """⛔ THE FACT THAT STOPS A SEQUENCE MATCH BECOMING A CLEAVAGE EVENT. All 123 sit at the
    screen's loosest admitted identity. If a stricter class ever appears in this set, the artifact's
    framing paragraph is understating the load and must be rewritten."""
    _, gap_paired = m._screen_hits()
    assert len(gap_paired) == 123
    assert {h["identity"] for h in gap_paired} == {14}
    assert {16 - h["identity"] for h in gap_paired} == {2}
    assert {h["gap_mismatches"] for h in gap_paired} == {0}
    assert not any(h["is_minus_strand"] for h in gap_paired)


def test_the_predicted_model_fraction_is_carried_not_lost():
    """82 of the lead reagent's 123 records are computationally predicted gene models. That is a
    different kind of liability from a curated one and the artifact must keep the split."""
    _, rows, _ = m._locus_rows(path=m.SCREEN, reagent=m.REAGENT)
    pred = sum(r["n_predicted_records"] for r in rows)
    cur = sum(r["n_curated_records"] for r in rows)
    assert (pred, cur) == (82, 41)
    assert pred + cur == 123
    # and every locus of the whole panel carries the split, not just the lead's
    _, allrows, _ = m._locus_rows()
    for r in allrows:
        assert r["n_curated_records"] + r["n_predicted_records"] == r["n_transcript_records"]


def test_there_is_exactly_one_locus_parser_and_it_handles_both_defline_shapes():
    """⛔ TWO PARSERS EACH RIGHT ON THE CASE THAT MOTIVATED THEM IS NOT A CROSS-CHECK.

    This module used to carry its own second pass over `locus_of`, added because `locus_of` split
    the defline on its first comma and lost the symbol for `"germ cell-less 1, spermatogenesis
    associated (GMCL1), mRNA"`. That second pass took the FIRST parenthetical of the full
    definition — which is the other half of the same bug: it returns `N-ACETYL` for
    `"glucosaminyl (N-acetyl) transferase 3, mucin type (GCNT3), mRNA"`, a confident and wrong
    symbol that looks like nothing downstream.

    `locus_of` was corrected on 2026-08-13 to read NCBI's actual defline grammar, this module now
    delegates to it, and both shapes are asserted here so neither failure can return by either
    route.
    """
    import junction_aso_locus_collapse as J
    assert m.gene_of is not None
    # delegation, not a reimplementation: same answer as the shared parser on every real hit
    _, gap_paired = m._screen_hits()
    for h in gap_paired:
        assert m.gene_of(h) == J.locus_of(h)

    # the comma-in-description case (what broke the ORIGINAL parser)
    assert m.gene_of({"defn": "Homo sapiens germ cell-less 1, spermatogenesis associated "
                              "(GMCL1), mRNA", "acc": "NM_178439"}) == "GMCL1"
    # the parenthetical-first case (what would have broken this module's OWN second pass)
    assert m.gene_of({"defn": "Homo sapiens glucosaminyl (N-acetyl) transferase 3, mucin type "
                              "(GCNT3), mRNA", "acc": "NM_004751"}) == "GCNT3"
    assert m.gene_of({"defn": "Homo sapiens small nuclear ribonucleoprotein polypeptides B and B1 "
                              "(Sm) (SNRPB), transcript variant 1, mRNA",
                      "acc": "NM_003091"}) == "SNRPB"
    # and no accession fallback survives anywhere in the panel
    _, rows, prov = m._locus_rows()
    assert not [r for r in rows if r["locus"].startswith("acc:")], "an unresolved locus remains"
    assert "corrected 2026-08-13" in prov["locus_parser"]


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The guards
# ─────────────────────────────────────────────────────────────────────────────────────────────

def test_the_selftest_passes_offline():
    """The module's own pre-fetch gate. It asserts the control gate and the absence rule."""
    assert m.selftest() == 0


def test_an_unread_arm_can_never_become_a_biological_statement():
    """⛔ THE FAILURE CLAUDE.md §4 NAMES. A locus with no reference row must read as `readable:
    false` with a reason, never as a zero and never as 'not expressed'."""
    art = m.derive(m._empty_inputs())
    for p in art["per_locus"]:
        exp = p["exposure_compartment_liver_kidney"]
        assert exp["readable"] is False
        assert exp["values"] is None
        assert "reason" in exp
        assert p["tier"] in ("NOT_MEASURED", "NOT_MEASURABLE_UNCHARACTERISED")
    s = art["summary"]
    assert s["loci_expressed_in_an_exposure_organ"] == []
    # every locus of the panel, not a subset — an unfetched run must claim nothing about any of them
    assert (len(s["loci_whose_exposure_question_is_unanswerable_from_public_data"])
            == s["n_loci"] == len(art["per_locus"]))


def test_a_failed_known_answer_control_withholds_every_locus_verdict():
    """⛔ A COLUMN SHIFT IN A WIDE MATRIX IS INVISIBLE IN THE NUMBERS AND FATAL TO ALL OF THEM.
    A run whose controls land in the wrong tissue must emit no exposure figure at all."""
    bad = m._empty_inputs()
    bad["arm_a_gtex"] = {
        "_status": "read",
        "tissues": ["Liver", "Kidney - Cortex"],
        "rows": {"ALB": [{"gencode_id": "x", "symbol": "ALB", "values": [1.0, 900.0]}],
                 "ANKS1B": [{"gencode_id": "y", "symbol": "ANKS1B", "values": [500.0, 500.0]}]},
    }
    art = m.derive(bad)
    assert art["method"]["known_answer_controls"]["passed"] is False
    for p in art["per_locus"]:
        assert p["tier"] == "NOT_MEASURED"
        assert p["exposure_compartment_liver_kidney"]["readable"] is False
        assert "withheld" in p["exposure_compartment_liver_kidney"]["reason"]


def test_the_two_compartments_are_never_merged():
    """⭐ THE SPLIT IS THE ANSWER. A liver figure and a soft-tissue figure answer different
    questions, and an artifact that averaged them would destroy both."""
    art = m.derive(m._empty_inputs())
    assert m.EXPOSURE_TISSUES == ["Liver", "Kidney - Cortex", "Kidney - Medulla"]
    assert not set(m.EXPOSURE_TISSUES) & set(m.TUMOUR_COMPARTMENT_PROXY_TISSUES)
    for p in art["per_locus"]:
        assert p["exposure_compartment_liver_kidney"]["block"] == "exposure_liver_kidney"
        assert (p["tumour_compartment_normal_tissue_proxy"]["block"]
                == "tumour_compartment_normal_tissue_proxy")
        assert "tumour_compartment_emc_tumours" in p


def test_the_soft_tissue_block_is_labelled_a_proxy_and_not_a_tumour_reading():
    """GTEx contains no EMC and no sarcoma. An artifact that let the proxy read as the tumour would
    be reporting normal tissue as disease tissue."""
    art = m.derive(m._empty_inputs())
    why = art["method"]["_why_a_proxy"]
    assert "no reference expression atlas contains that tumour" in why.lower()
    assert any("Not a tumour measurement where it says proxy" in s
               for s in art["_what_this_is_not"])


def test_the_record_count_is_never_presented_as_risk():
    """ANKS1B and ZNF667 carry 104 of 123 records between them. That is RefSeq annotation depth."""
    art = m.derive(m._empty_inputs())
    for p in art["per_locus"]:
        note = p["screen_records"]["⚠_record_count_is_annotation_depth"]
        assert "not expression" in note and "not risk" in note
    assert any("annotation depth" in s for s in art["_what_this_is_not"])
    # and the ordering of per_locus is by record count, so the note must sit on every row
    counts = [p["screen_records"]["n_transcript_records"] for p in art["per_locus"]]
    assert counts == sorted(counts, reverse=True)


def test_the_framing_forbids_the_four_claims_the_language_rules_forbid():
    """CLAUDE.md §1: never imply selectivity, efficacy, safety, a therapeutic window or clinical
    readiness. The artifact states the refusal itself so a reader quoting it carries the limit."""
    art = m.derive(m._empty_inputs())
    f = art["_framing"].upper()
    for word in ("EFFICACY", "SELECTIVITY", "SAFETY", "THERAPEUTIC-WINDOW", "CLINICAL-READINESS"):
        assert word in f
    assert "NECESSARY" in f and "never a sufficient one" in art["_framing"]
    assert "two mismatches" in art["_framing"]


def test_there_is_no_risk_column_and_no_hazard_ordering_anywhere():
    """⛔ THE WORD WOULD IMPORT AN INFERENCE NEITHER SCREEN SUPPORTS.

    Every locus in this panel is here because a 16-mer matched it at 14/16 — a sequence match at
    two mismatches, not a predicted cleavage event. So an expression figure is evidence about the
    GENE, and the join to the oligonucleotide needs an affinity argument nothing here has made.
    A `risk` key, a hazard score or a ranked-by-danger list would each quietly make that join.

    ⚠ The screen's OWN class name `true_cleavage_risk` is exempt: it is read from the committed
    screen rather than coined here, and `risk_class_read` records that it was inherited. Anything
    else carrying the word is this module editorialising.
    """
    art = m.derive(m._empty_inputs())
    flat = json.dumps(art, ensure_ascii=False)

    def keys(obj, out):
        if isinstance(obj, dict):
            for k, v in obj.items():
                out.append(k)
                keys(v, out)
        elif isinstance(obj, list):
            for v in obj:
                keys(v, out)
        return out

    # ⚠ TWO EXEMPTIONS, BOTH NARROW. `risk_class_read` is the screen's inherited class name, and a
    # key whose own text NEGATES the word is a refusal rather than a column — the guard fired on
    # `…has_no_risk_column` the first time it ran, which is the guard working.
    def _exempt(low):
        return low.startswith("risk_class_read") or "no_risk_column" in low or "not_a_ranking" in low

    for k in keys(art, []):
        low = k.lower()
        assert "risk" not in low or _exempt(low), f"risk-flavoured key: {k}"
        for banned in ("hazard", "danger", "severity", "risk_score", "priority"):
            assert banned not in low or _exempt(low), f"hazard-flavoured key: {k}"
    # the only permitted occurrences of the word are the screen's inherited class name and the
    # sentences that explicitly refuse to rank
    assert m.GAP_PAIRED_CLASS == "true_cleavage_risk"
    assert "no hazard ordering of any kind" in flat
    s = art["summary"]
    assert "⛔_this_list_is_not_a_ranking_and_this_file_has_no_risk_column" in s
    assert "not an ordering of the panel by hazard" in \
        s["⛔_this_list_is_not_a_ranking_and_this_file_has_no_risk_column"]


def test_the_artifact_says_the_join_to_the_oligonucleotide_is_the_papers_to_make():
    """Expression is evidence about the gene. The artifact must say so rather than let a reader
    slide from an expressed gene to an affected one."""
    art = m.derive(m._empty_inputs())
    assert any("evidence about the oligonucleotide" in s for s in art["_what_this_is_not"])
    assert any("affinity argument" in s for s in art["_what_this_is_not"])
    assert "NECESSARY" in art["_framing"].upper()


def test_the_hpa_exposure_fallback_is_labelled_and_never_pooled_with_gtex():
    """⛔ A SECOND-CHOICE READING MUST NOT RENDER AS THE FIRST-CHOICE ONE.

    Run 31747675357 lost the whole exposure arm to a single GTEx 404, so HPA now answers when arm A
    cannot. But HPA reports a WHOLE-KIDNEY consensus nTPM where GTEx splits cortex from medulla,
    and HPA's consensus incorporates GTEx — so it is neither interchangeable with nor independent
    of the GTEx block. Every fallback row has to say both things, or a reader pools two different
    instruments and a later comparison silently mixes units.
    """
    inp = m._empty_inputs()
    inp["arm_a_gtex"] = {"_status": "fetch or parse failed: HTTPError: HTTP Error 404: Not Found"}
    sym = m._locus_rows()[1][0]["locus"]
    inp["arm_d_hpa"] = {"genes": {sym: {"_status": "read", "ensembl": "ENSGTEST", "per_gene": {
        "_status": "read", "matched_path": "x/y",
        "values": {"liver": 44.0, "kidney": 3.0, "brain": 1.0, "lung": 2.0, "heart": 1.0,
                   "skin": 1.0, "colon": 1.0, "testis": 1.0, "thyroid": 1.0, "spleen": 1.0}}}}}
    art = m.derive(inp)
    row = [p for p in art["per_locus"] if p["locus"] == sym][0]
    e = row["exposure_compartment_liver_kidney"]
    assert e["readable"] is True
    assert e["values"] == {"liver": 44.0, "kidney": 3.0}
    assert "NOT GTEx median TPM" in e["unit"] and "do not pool" in e["unit"]
    assert "second-choice" in e["⚠_substituted_for_gtex"]
    assert "WHOLE-KIDNEY" in e["⚠_substituted_for_gtex"]
    assert row["tier"] == "EXPRESSED_IN_AN_EXPOSURE_ORGAN"

    # ⛔ and the PROXY block gets no such fallback — HPA does not carry those tissues, so filling it
    # from HPA would be inventing a soft-tissue reading out of a different instrument's vocabulary
    assert row["tumour_compartment_normal_tissue_proxy"]["readable"] is False

    # every OTHER locus, with no HPA record, stays unreadable rather than becoming a zero
    for p in art["per_locus"]:
        if p["locus"] == sym:
            continue
        assert p["exposure_compartment_liver_kidney"]["readable"] is False


def test_the_gtex_url_is_a_recorded_attempt_list_not_a_single_guess():
    """A single constant took the whole exposure arm down with one 404. The replacement must try
    candidates in order and record which answered, so a future bucket move is a recorded miss."""
    assert isinstance(m.GTEX_MEDIAN_TPM_URLS, list) and len(m.GTEX_MEDIAN_TPM_URLS) >= 2
    assert all(u.startswith("https://") for u in m.GTEX_MEDIAN_TPM_URLS)
    assert m.GTEX_MEDIAN_TPM_URL == m.GTEX_MEDIAN_TPM_URLS[0]
    src = open(os.path.join(MOD, "aso_offtarget_tissue_expression.py"), encoding="utf-8").read()
    assert "url_attempts" in src, "the attempt list is not recorded"


def test_ncbi_calls_are_paced_so_the_identity_arm_cannot_be_rate_limited_away():
    """⛔ ARM C IS WHAT LETS AN ABSENCE BE ATTRIBUTED. Unthrottled, it lost five of six genes to
    HTTP 429 and degraded a *reason* into a *silence* — the shape §4 is written about."""
    assert m._NCBI_MIN_INTERVAL_S >= 0.34, "faster than NCBI's ~3 req/s without an API key"
    assert m._NCBI_MAX_RETRIES >= 3
    src = open(os.path.join(MOD, "aso_offtarget_tissue_expression.py"), encoding="utf-8").read()
    assert "esearch.fcgi" in src and "_ncbi_get(f\"{EUTILS}/esearch.fcgi" in src, \
        "the esearch call bypasses the paced helper"
    assert "_ncbi_get(f\"{EUTILS}/esummary.fcgi" in src, \
        "the esummary call bypasses the paced helper"


def test_the_tissue_key_matches_across_endpoints_and_cannot_merge_two_real_tissues():
    """⛔ A HYPHEN COST A WHOLE 26-MINUTE RUN (run 31749264339).

    The release GCT labels tissues `Kidney - Medulla`; the portal API returns `Kidney_Medulla`.
    The fallback normalised underscores to spaces, producing `Kidney Medulla`, which matches
    NEITHER. Two of three known-answer controls then failed on punctuation while the underlying
    fetch was flawless — ALB 25,201 TPM in Liver, UMOD 2,116 in Kidney Medulla, MYH7 4,514 in
    Heart Left Ventricle — and the control gate correctly withheld every locus verdict. A false
    negative on a safety gate is the expensive direction of being right.

    ⚠ AND THE KEY MUST NOT FIX THAT BY COLLAPSING REAL TISSUES. Stripping punctuation is only safe
    if no two GTEx tissue names differ solely in punctuation, which is asserted here over the full
    54-label vocabulary rather than assumed.
    """
    assert m._tkey("Kidney - Medulla") == m._tkey("Kidney_Medulla") == m._tkey("Kidney Medulla")
    assert m._tkey("Skin - Sun Exposed (Lower leg)") == m._tkey("Skin_Sun_Exposed_Lower_leg")
    assert m._tkey("Cells - Cultured fibroblasts") == m._tkey("Cells_Cultured_fibroblasts")
    assert m._tkey("Heart - Left Ventricle") == m._tkey("Heart_Left_Ventricle")
    # distinct tissues stay distinct
    assert m._tkey("Kidney - Cortex") != m._tkey("Kidney - Medulla")
    assert m._tkey("Brain - Cortex") != m._tkey("Brain - Cerebellum")

    # over the real vocabulary, if the committed inputs cache carries one
    if os.path.exists(os.path.join(MOD, "aso-offtarget-tissue-expression-inputs.json")):
        inp = json.load(open(os.path.join(MOD, "aso-offtarget-tissue-expression-inputs.json"),
                             encoding="utf-8"))
        tissues = (inp.get("arm_a_gtex") or {}).get("tissues") or []
        if tissues:
            keys = [m._tkey(t) for t in tissues]
            assert len(set(keys)) == len(keys), (
                "two GTEx tissues collide under _tkey — the key is unsafe: "
                + str([t for t in tissues if keys.count(m._tkey(t)) > 1]))


def test_a_control_that_lands_in_the_right_tissue_passes_whichever_endpoint_answered():
    """The gate must grade an API-fallback run by the same controls as a release-file run."""
    inp = m._empty_inputs()
    sym = m._locus_rows()[1][0]["locus"]
    api_labels = ["Liver", "Kidney Cortex", "Kidney Medulla", "Heart Left Ventricle",
                  "Muscle Skeletal"]

    def row(s, mapping):
        return [{"gencode_id": "g", "symbol": s,
                 "values": [mapping.get(t, 0.0) for t in api_labels]}]

    inp["arm_a_gtex"] = {"_status": "read", "endpoint_used": "portal_api_v2_fallback",
                         "tissues": api_labels, "rows": {
                             "ALB": row("ALB", {"Liver": 25201.3}),
                             "UMOD": row("UMOD", {"Kidney Medulla": 2116.02}),
                             "MYH7": row("MYH7", {"Heart Left Ventricle": 4513.66}),
                             sym.upper(): row(sym, {"Liver": 0.0, "Kidney Cortex": 0.5})}}
    art = m.derive(inp)
    assert art["method"]["known_answer_controls"]["passed"] is True, (
        "the same controls that pass on release-file labels must pass on API labels")
    r = [p for p in art["per_locus"] if p["locus"] == sym][0]
    assert r["exposure_compartment_liver_kidney"]["readable"] is True
    assert r["exposure_compartment_liver_kidney"]["values"]["Kidney - Cortex"] == 0.5
    assert r["tier"] == "BELOW_DETECTION_IN_EXPOSURE_ORGANS"


def test_the_present_cut_is_stated_as_a_choice_not_a_measurement():
    art = m.derive(m._empty_inputs())
    assert art["method"]["present_tpm_cut"] == m.PRESENT_TPM
    assert any("STATED legibility cut" in s for s in art["_what_this_is_not"])


def test_a_truncated_screen_is_refused_rather_than_censused():
    """⛔ A LOCUS CENSUS OVER A TRUNCATED HIT LIST IS A LOWER BOUND WEARING THE COSTUME OF A COUNT.

    ⚠ AND THE REAGENT ITSELF CANNOT EXERCISE THIS GUARD, WHICH IS WHY A SIBLING IS USED. At the
    default depth `GGGCATATCATCAAAC` returned 9 near-matches and stored all 9, so pointing this
    test at the reagent skips — a guard that never runs is worth nothing. Its neighbours on the
    same seam ARE truncated (`junction_aso_offtarget` stores `ranked[:15]` while reporting the full
    count), so the refusal is exercised against one of those, on the same committed file.
    """
    shallow = os.path.join(MOD, "junction-aso-offtarget-e12n3.json")
    if not os.path.exists(shallow):
        pytest.fail(f"the default-depth screen is missing at {shallow}; it is committed, and the "
                    "truncation refusal is exercised against it — this docstring already records "
                    "that a guard which never runs is worth nothing.")
    d = json.load(open(shallow, encoding="utf-8"))
    truncated = [o["antisense_5to3"] for o in d.get("oligos", [])
                 if len(o.get("offtargets") or []) != o.get("n_offtarget_near_matches")]
    assert truncated, "no oligo in the default-depth screen is truncated — re-read the guard"
    with pytest.raises(RuntimeError, match="truncated"):
        m._screen_hits(path=shallow, reagent=truncated[0])
    # and the reagent's own default-depth record is NOT truncated, so it is accepted there too
    _, gap_paired = m._screen_hits(path=shallow, reagent=m.REAGENT)
    assert len(gap_paired) == 5, (
        "the shallow screen's gap-spanning count for the reagent moved; the manuscript quotes it")


def test_derive_tolerates_an_inputs_cache_written_by_an_older_version_of_itself():
    """⛔ A COMMITTED INPUTS CACHE OUTLIVES THE CODE THAT WROTE IT.

    Measured 2026-08-13: run 31747675357 published a cache whose locus rows predate the two-seam
    panel, and `derive` raised `KeyError: 'seams'` on it — so the module could not reproduce its own
    artifact from its own published inputs, and `--check` was not a reproduction test but a crash.
    A missing field must degrade to an explicit "not recorded", never to an exception, because the
    whole point of the cache is that a later run can re-derive from an earlier fetch.
    """
    inp = m._empty_inputs()
    inp["loci"] = [{"locus": "ANKS1B", "n_transcript_records": 67, "n_curated_records": 32,
                    "n_predicted_records": 35, "accessions": [],
                    "identity_of_every_record": "14/16"}]          # pre-panel shape: no `seams`
    art = m.derive(inp)                                            # must not raise
    row = art["per_locus"][0]
    assert row["locus"] == "ANKS1B"
    assert row["seams"] == ["not_recorded_by_the_run_that_wrote_this_cache"]
    assert row["n_designs_hitting_it"] is None
    assert row["screen_records"]["n_transcript_records"] == 67
    # and a cache missing the count fields entirely is still not an exception
    inp["loci"] = [{"locus": "X"}]
    assert m.derive(inp)["per_locus"][0]["screen_records"]["n_transcript_records"] is None


def test_the_artifact_reproduces_from_its_committed_inputs():
    """`--check` is the artifact's own reproduction test; a stale artifact fails here."""
    _art()
    assert m.main(["--check"]) == 0, "the artifact is stale; re-run the script"
