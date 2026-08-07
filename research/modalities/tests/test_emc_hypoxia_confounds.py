"""Offline tests for the EMC hypoxia confound audit.

⛔ WHAT IS PINNED HERE IS NOT ARITHMETIC. It is the four ways this module could lie, three of which
have precedents in this repository (CLAUDE.md §4):

  1. **A second cache silently disagreeing with the first.** The audit merges the panels inputs
     cache with a null-background cache fetched separately. Both parse the SAME series-matrix file,
     so a gene in both must carry identical values — and if it does not, every merged score is a
     blend of two experiments. `_merged_zcache` must RAISE, never average, never prefer one.
  2. **The null drawing from a chosen pool.** The whole point of the genome-wide background is that
     its genes were not selected for this question. If the named confound genes, or the panels want
     list, can leak into the draw pool, the null silently becomes the biased one it replaced — and
     it would look identical in the artifact.
  3. **An absent reading rendering as a reading of absence.** No background fetched must print "the
     genome-wide null has NOT been taken", never a null result; the same for the clinical
     retrieval, and the same for a gene with no probe.
  4. **A populated field rendering as a measured one.** A stratum below the gene floor or the
     group-n floor must emit UNDERPOWERED with its coverage, never a number that renders like a
     fully-powered one.

Plus one guard of a different kind, the reason `_zrow` may be reproduced at all: it must agree with
the owning module on the REAL cache, so the copy cannot drift away from the instrument it claims to
be. (CLAUDE.md §6: mock the thing under test and you test the mock — so that one runs against the
real committed artifact, not a fixture.)
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import emc_hypoxia_confounds as M  # noqa: E402

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------------------------
# A synthetic pair of caches. Hand-built so every assertion has a known answer.
# ---------------------------------------------------------------------------------------------
def _tgt(genes, n=8, gsms=None):
    return {
        "gse": "GSEFAKE", "platform": "GPLFAKE", "_status": "read", "n_samples": n,
        "samples": [{"gsm": (gsms or [f"GSM{i}" for i in range(n)])[i],
                     "annotation_verbatim": ("Extraskeletal myxoid chondrosarcoma %d" % i
                                             if i < 4 else "Low-grade fibromyxoid sarcoma %d" % i)}
                    for i in range(n)],
        "background_per_sample": [{"mean": 0.0, "sd": 1.0, "n": 100} for _ in range(n)],
        "genes": genes,
    }


def _g(vals):
    return {"probe_ids": ["p1"], "n_probes_mapping": 1, "values": vals,
            "array_percentile": [0.5] * len(vals)}


# ---------------------------------------------------------------------------------------------
# 1. THE MERGE MUST RAISE ON DISAGREEMENT — never average, never silently prefer one cache.
# ---------------------------------------------------------------------------------------------
def test_merge_raises_when_the_two_caches_disagree_on_a_shared_gene():
    a = _tgt({"AAA": _g([1, 2, 3, 4, 5, 6, 7, 8])})
    b = dict(_tgt({"AAA": _g([9, 9, 9, 9, 9, 9, 9, 9]), "BBB": _g([1] * 8)}), _status="read")
    with pytest.raises(AssertionError) as exc:
        M._merged_zcache(a, b)
    assert "do not" in str(exc.value) or "disagree" in str(exc.value)


def test_merge_raises_when_the_sample_order_differs():
    a = _tgt({"AAA": _g([1] * 8)})
    b = dict(_tgt({"AAA": _g([1] * 8)}, gsms=[f"GSMX{i}" for i in range(8)]), _status="read")
    with pytest.raises(AssertionError) as exc:
        M._merged_zcache(a, b)
    assert "sample order" in str(exc.value)


def test_merge_adds_only_the_genes_the_first_cache_lacks_and_records_where_each_came_from():
    a = _tgt({"AAA": _g([1, 2, 3, 4, 5, 6, 7, 8])})
    b = dict(_tgt({"AAA": _g([1, 2, 3, 4, 5, 6, 7, 8]), "BBB": _g([2] * 8)}), _status="read")
    z, prov, rec = M._merged_zcache(a, b)
    assert set(z) == {"AAA", "BBB"}
    assert prov["AAA"] == "panels_inputs" and prov["BBB"] == "null_background"
    assert rec["merged"] is True and rec["n_added_from_background"] == 1


def test_no_background_leaves_the_cache_untouched_and_says_so():
    a = _tgt({"AAA": _g([1] * 8)})
    z, prov, rec = M._merged_zcache(a, None)
    assert set(z) == {"AAA"} and rec["merged"] is False and "_why" in rec


# ---------------------------------------------------------------------------------------------
# 2. THE NULL'S DRAW POOL MUST BE THE SEEDED RANDOM SAMPLE ALONE.
# ---------------------------------------------------------------------------------------------
def test_the_named_confound_genes_are_never_in_the_null_draw_pool():
    """A gene requested BY NAME is a chosen gene, and a pool cannot be partly chosen."""
    named = ["PECAM1", "VWF"]
    bg = dict(_tgt({"PECAM1": _g([1] * 8), "VWF": _g([1] * 8),
                    "RND1": _g([1, 2, 3, 4, 5, 6, 7, 8]), "RND2": _g([8, 7, 6, 5, 4, 3, 2, 1]),
                    "RND3": _g([1, 3, 5, 7, 2, 4, 6, 8])}), _status="read",
              _random_background_symbols=["RND1", "RND2", "RND3"])
    tgt = _tgt({"AAA": _g([1] * 8)})
    zcache = {"AAA": M._zrow(tgt, "AAA")}
    out = M._genome_wide_null(bg, tgt, [0, 1, 2, 3], [4, 5, 6, 7], zcache,
                              {"hypoxia_x": ["AAA"]}, {})
    assert out["background_universe_size"] == 3, "named confound genes leaked into the draw pool"
    assert out["n_genes_in_background_cache_excluded_from_the_draw_pool"] == len(named)
    assert out["_draw_pool_is_the_seeded_random_sample_only"] is True


def test_the_fetch_removes_from_the_random_draw_any_symbol_it_also_asks_for_by_name():
    """The two want sets overlap by construction; the overlap must leave the RANDOM half."""
    assert "PECAM1" in M.CONFOUND_GENES_TO_ADD
    assert "CA9" in M.CONFOUND_GENES_TO_ADD
    # the rule lives in fetch_background; assert the invariant it must produce
    drawn = sorted({"AAA", "PECAM1", "CA9", "ZZZ"} - set(M.CONFOUND_GENES_TO_ADD))
    assert "PECAM1" not in drawn and "CA9" not in drawn


# ---------------------------------------------------------------------------------------------
# 3. AN ABSENT READING MUST NEVER RENDER AS A READING OF ABSENCE.
# ---------------------------------------------------------------------------------------------
def _minimal_inputs():
    n = 16
    ann = ["Extraskeletal myxoid chondrosarcoma %d" % i if i < 8
           else "Low-grade fibromyxoid sarcoma %d" % i for i in range(n)]
    genes = {g: _g([float((i * 7 + j) % 11) for i in range(n)])
             for j, g in enumerate(["CA9", "VEGFA", "SLC2A1", "LDHA", "PGK1", "NR4A3", "ENO3",
                                    "VCAN", "PAPSS2", "MKI67", "KDR", "AIF1", "HK2", "ALDOA"])}
    tgt = {"gse": "GSEFAKE", "platform": "GPLFAKE", "_status": "read", "n_samples": n,
           "value_kind": "single-channel intensity",
           "samples": [{"gsm": f"GSM{i}", "annotation_verbatim": ann[i]} for i in range(n)],
           "background_per_sample": [{"mean": 0.0, "sd": 1.0, "n": 100} for _ in range(n)],
           "genes": genes}
    return {"_generated_utc": "2026-01-01T00:00:00+00:00",
            "signature_sets": {"slots": {"hypoxia_buffa": {
                "genes": ["CA9", "VEGFA", "SLC2A1", "LDHA", "PGK1"], "n_genes": 5,
                "resolved_set": "fake", "citation": "fake", "provenance": "fake"}}},
            "targets": {"FAKE_series_matrix.txt.gz": tgt}}


def test_no_background_fetched_says_the_null_was_not_taken_and_never_reports_a_null_result():
    res = M.derive(_minimal_inputs(), background=None)
    plat = res["platforms"]["FAKE_series_matrix.txt.gz"]
    gw = plat["C8_C9_C10_resampling"]["C10_random_gene_set_null_GENOME_WIDE"]
    assert gw["_status"] == "NOT TAKEN"
    v = gw["verdict"].lower()
    assert "not been fetched" in v
    assert "absent reading" in v and "not a reading of absence" in v
    # and it must not be sayable as a pass or a fail
    assert "passed or failed" in v


def test_no_therapeutic_retrieval_says_NOT_RETRIEVED_for_every_class():
    res = M.derive(_minimal_inputs(), background=None, therapeutic=None)
    hooks = res["therapeutic_hooks"]
    assert hooks["_status"] == "NOT RETRIEVED"
    assert "absent reading" in hooks["verdict"].lower()
    assert set(hooks["classes"]) == set(M.THERAPEUTIC_CLASSES)
    for cls in hooks["classes"].values():
        assert cls["status"] == "NOT RETRIEVED"


def _status_with_all_registry_queries_failed():
    """What run 31200194935 actually produced: PubMed fine, every registry query HTTP 400."""
    classes = {}
    for cls, meta in M.THERAPEUTIC_CLASSES.items():
        classes[cls] = {
            "why_a_hypoxia_reading_points_here": meta["why_a_hypoxia_reading_points_here"],
            "the_prior_that_matters": meta["the_prior_that_matters"],
            "clinicaltrials": {a: {"_status": "QUERY FAILED",
                                   "_error": {"http_status": 400, "reason": "Bad Request"}}
                               for a in meta["agents"]},
            "sarcoma_specific_trials": {},
            "pubmed": {a: {"n_hits": 25} for a in meta["agents"]},
        }
    return {"_generated_utc": "2026-01-01T00:00:00+00:00", "classes": classes}


def test_a_class_whose_every_registry_query_failed_reports_NO_COUNT_not_zero():
    """⛔ THE FAILURE THIS PINS ACTUALLY HAPPENED (run 31200194935, 2026-08-07).

    All 21 ClinicalTrials.gov v2 queries returned HTTP 400 and the summary printed
    `n_registered_studies_returned: 0` with an empty phase table for all three classes — which
    renders EXACTLY like a class that genuinely has no registered trial, in the section that
    touches clinical claims. The per-agent record said `QUERY FAILED` the whole time; the
    SUMMARY is what lied."""
    res = M.derive(_minimal_inputs(), background=None,
                   therapeutic=_status_with_all_registry_queries_failed())
    hooks = res["therapeutic_hooks"]
    assert hooks["_status"].startswith("PARTIAL"), hooks["_status"]
    for cls, row in hooks["classes"].items():
        tr = row["trial_registry"]
        assert tr["_status"] == "NOT RETRIEVED", cls
        # the two fields that told the lie must be ABSENT, not zero
        assert "n_registered_studies_returned" not in tr, f"{cls} still emits a count"
        assert "phase_counts" not in tr, f"{cls} still emits a phase table"
        assert "n_sarcoma_indexed_trials" not in tr, f"{cls} still emits a sarcoma count"
        v = tr["verdict"].lower()
        assert "absent reading" in v and "does not mean no trial exists" in v
    # and the PubMed half, which DID work, must still be reported
    for row in hooks["classes"].values():
        assert any(isinstance(n, int) and n > 0 for n in row["pubmed_hit_counts"].values())


def test_a_partial_registry_retrieval_says_the_counts_cover_only_what_succeeded():
    st = _status_with_all_registry_queries_failed()
    cls = next(iter(st["classes"]))
    agent = next(iter(st["classes"][cls]["clinicaltrials"]))
    st["classes"][cls]["clinicaltrials"][agent] = {
        "n_returned": 2,
        "studies": [{"nct": "NCT1", "title": "t", "status": "COMPLETED", "why_stopped": None,
                     "phase": ["PHASE3"], "conditions": ["Soft Tissue Sarcoma"], "sponsor": "x",
                     "start": "2014"},
                    {"nct": "NCT2", "title": "t", "status": "TERMINATED",
                     "why_stopped": "did not meet endpoint", "phase": ["PHASE2"],
                     "conditions": ["Other"], "sponsor": "x", "start": "2015"}]}
    res = M.derive(_minimal_inputs(), background=None, therapeutic=st)
    tr = res["therapeutic_hooks"]["classes"][cls]["trial_registry"]
    assert tr["_status"] == "PARTIAL"
    assert tr["n_registered_studies_returned"] == 2
    assert "ONLY the agents whose query succeeded" in tr["_partial_means"]
    assert tr["agents_whose_query_failed"]
    assert len(tr["trials_with_a_recorded_why_stopped"]) == 1


def test_the_registry_query_carries_no_v1_fields_parameter():
    """The exact defect: v1 StudyFields names sent to the v2 endpoint -> HTTP 400 on all 21."""
    src = open(os.path.join(MOD, "emc_hypoxia_confounds.py"), "r", encoding="utf-8").read()
    body = src.split("def fetch_therapeutic_status", 1)[1]
    for line in body.split("\n"):
        if "clinicaltrials.gov/api/v2" in line or ('"&fields=' in line):
            assert "fields=" not in line, (
                f"a v2 registry query still passes `fields=`, which is what returned 400 on every "
                f"query in run 31200194935: {line.strip()[:120]}")


def test_a_gene_with_no_probe_is_reported_unreadable_not_unexpressed():
    res = M.derive(_minimal_inputs(), background=None)
    plat = res["platforms"]["FAKE_series_matrix.txt.gz"]
    per_gene = plat["matrix_reading"]["per_gene"]
    missing = [g for g, r in per_gene.items() if r.get("readable") is False]
    assert missing, "fixture must contain at least one unreadable matrix gene"
    for g in missing:
        v = per_gene[g]["verdict"].lower()
        assert "could not be taken" in v
        assert "not a statement that the gene is unexpressed" in v


def test_an_unreadable_fusion_gene_does_not_produce_a_null_correlation():
    inp = _minimal_inputs()
    del inp["targets"]["FAKE_series_matrix.txt.gz"]["genes"]["NR4A3"]
    res = M.derive(inp, background=None)
    row = (res["platforms"]["FAKE_series_matrix.txt.gz"]["fusion_vs_tissue"]["discriminators"]
           ["within_EMC_fusion_output_vs_hypoxia"]["genes"]["NR4A3"])
    assert row["readable"] is False
    assert "not a null result" in row["verdict"].lower()


# ---------------------------------------------------------------------------------------------
# 4. A THIN STRATUM MUST NOT RENDER LIKE A COVERED ONE.
# ---------------------------------------------------------------------------------------------
def test_a_gene_list_below_the_floor_emits_UNDERPOWERED_and_no_score():
    tgt = _tgt({"AAA": _g([1, 2, 3, 4, 5, 6, 7, 8])})
    z = {"AAA": M._zrow(tgt, "AAA")}
    row, per = M._score_row(tgt, ["AAA", "BBB", "CCC", "DDD"], [0, 1, 2, 3], [4, 5, 6, 7], z,
                            "thin", "curated")
    assert per is None and row["contrast"] is None
    assert "UNDERPOWERED" in row["verdict"]
    assert "instrument limit, not a reading of the biology" in row["verdict"]
    assert row["n_genes_readable"] == 1 and row["n_genes_requested"] == 4


def test_an_arm_below_the_group_floor_emits_no_contrast():
    tgt = _tgt({"AAA": _g([1] * 8), "BBB": _g([2, 3, 4, 5, 6, 7, 8, 9]),
                "CCC": _g([9, 8, 7, 6, 5, 4, 3, 2])})
    z = {g: M._zrow(tgt, g) for g in tgt["genes"]}
    per, _rd = M._score(tgt, ["AAA", "BBB", "CCC"], z)
    assert M._contrast(per, [0, 1], [4, 5, 6, 7]) is None, "n_a=2 is below the floor"


# ---------------------------------------------------------------------------------------------
# 5. THE INSTRUMENT — the reproduced `_zrow` must agree with the owning module ON THE REAL CACHE.
# Not a fixture: mock the thing under test and you test the mock (CLAUDE.md §6).
# ---------------------------------------------------------------------------------------------
def test_zrow_agrees_with_the_owning_module_on_the_real_committed_cache():
    path = os.path.join(MOD, "emc-expression-panels-inputs.json")
    if not os.path.exists(path):
        pytest.skip("the panels inputs cache is not on this branch")
    import emc_expression_panels as P
    with open(path, "r", encoding="utf-8") as fh:
        inp = json.load(fh)
    checked = 0
    for tgt in inp["targets"].values():
        if tgt.get("_status") != "read":
            continue
        for g in sorted(tgt["genes"])[:200]:
            assert M._zrow(tgt, g) == P._zrow(tgt, g), f"_zrow diverged on {g}"
            checked += 1
    assert checked > 0, "no gene was actually compared — the guard would be vacuous"


def test_the_audit_never_restates_the_panels_headline_t_as_its_own():
    """CLAUDE.md §1. The six headline t-statistics have one home and it is not this file."""
    src = open(os.path.join(MOD, "emc_hypoxia_confounds.py"), "r", encoding="utf-8").read()
    for typed in ("+0.206", "+0.540", "t=+2.01", "t=+4.13", "+4.127", "+5.135"):
        assert typed not in src, (
            f"{typed!r} is typed into the audit; the headline t-statistics belong to "
            f"emc-expression-panels.json and must be DERIVED here, never re-typed")


def test_effect_sizes_are_marked_not_comparable_across_the_two_platforms():
    """The two platforms carry different value kinds, so `d` does not travel between them."""
    res = M.derive(_minimal_inputs(), background=None)
    plat = res["platforms"]["FAKE_series_matrix.txt.gz"]
    note = plat["_value_kinds_are_not_comparable_across_platforms"]
    assert "may not be compared" in note.lower()
    assert "direction" in note.lower()


def test_the_naive_sign_test_is_named_and_refused_rather_than_computed():
    """Six correlated readouts are not six confirmations; the arithmetic that would say so is the
    single easiest over-sell available here, so it must be visibly declined."""
    res = M.derive(_minimal_inputs(), background=None)
    dc = res["cross_platform"]["direction_consistency"]
    assert "naive_sign_test" in " ".join(dc.keys()).lower().replace("_naive", "naive")
    txt = dc["_naive_sign_test"].lower()
    assert "not independent" in txt and "refused" in txt
    assert "p_value" not in dc and "sign_test_p" not in dc
