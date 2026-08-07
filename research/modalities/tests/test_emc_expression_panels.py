"""Offline tests for the six-read EMC expression panel module.

The derive half must be exercisable with NO network, because the fetch half only runs in CI and a
broken derive would otherwise be discovered after the GEO fetch had already spent its time — the
same reason `emc-expression-datasets.yml` runs its unit tests BEFORE the fetch step.

⛔ WHAT IS ACTUALLY PINNED HERE is not arithmetic. It is the two ways this module could LIE, both of
which have done real damage in this repository before (CLAUDE.md §4):

  1. **An absent reading rendering as a reading of absence.** A gene with no probe must come back
     `readable: false` with a verdict that says the READ could not be taken, and must NEVER produce
     a sentence that could be quoted as "the gene is not expressed in EMC".
  2. **A populated field rendering as a measured one.** A panel whose members mostly failed to map
     must NOT emit a score that looks identical to a fully-covered one. The coverage floor is the
     guard, and a score below it must be `None` with an UNDERPOWERED verdict.

Plus one guard of a different kind: the probe-mapping-rate PRIORS in `TARGETS` are quoted from
`emc-atr-vulnerability.json`, which is their one home (CLAUDE.md §1). If that artifact moves and
this file does not, the drift check in the artifact silently compares against a stale number — so
the agreement is asserted rather than assumed.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import emc_expression_panels as M  # noqa: E402

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------------------------
# A synthetic inputs cache. Two platforms, hand-built so every assertion below has a known answer.
#
# `PRESENT` is readable on both. `ONE_ONLY` is readable on the first platform only — the exact
# shape reads 1 and 6 are exposed to, where a gene can be missing because an EST accession did not
# resolve rather than because the array lacks it. `GHOST` is on neither.
# ---------------------------------------------------------------------------------------------
def _samples(n_emc, n_comp, tag="EMC"):
    s = [{"gsm": f"GSM_E{i}", "title": f"{tag} {i}",
          "annotation_verbatim": f"Extraskeletal myxoid chondrosarcoma {i}"}
         for i in range(n_emc)]
    s += [{"gsm": f"GSM_C{i}", "title": f"comparator {i}",
           "annotation_verbatim": f"Gastrointestinal stromal tumor {i}"} for i in range(n_comp)]
    return s


def _target(mf, plat, n_emc, n_comp, genes, mapping_rate=0.9, prior=0.9):
    n = n_emc + n_comp
    return {
        "gse": "GSE_TEST", "matrix_file": mf, "why": "synthetic",
        "prior_probe_mapping_rate": prior,
        "prior_source": "synthetic",
        "url": "synthetic", "compressed_bytes": 1,
        "platform": plat, "platform_expected": plat, "platform_matches_expected": True,
        "probe_symbol_mapping": {"platform": plat, "n_mapped": 100},
        "n_samples": n, "n_probes": 1000,
        "n_probes_mapped_to_a_symbol": int(1000 * mapping_rate),
        "measured_probe_mapping_rate": mapping_rate,
        "samples": _samples(n_emc, n_comp),
        "frac_negative_values": 0.0,
        "value_kind": "single-channel intensity (synthetic)",
        "background_per_sample": [{"mean": 0.0, "sd": 1.0, "n": 1000} for _ in range(n)],
        "genes": genes,
        "n_wanted_genes_measured": len(genes),
        "n_wanted_genes_requested": len(genes) + 1,
        "_status": "read",
    }


def _gene(n_emc, n_comp, emc_val, comp_val, n_probes=1):
    vals = [emc_val] * n_emc + [comp_val] * n_comp
    # a tiny deterministic spread so Welch has non-zero variance in both arms
    vals = [v + (0.01 * i) for i, v in enumerate(vals)]
    return {"probe_ids": [f"p{i}" for i in range(n_probes)], "n_probes_mapping": n_probes,
            "values": vals, "array_percentile": [0.8] * n_emc + [0.2] * n_comp}


def _inputs():
    n_emc, n_comp = 6, 5
    panel_genes = M.PANELS["cs_gag_paps"]["groups"]["cs_sulfotransferases_4O"]
    a_genes = {g: _gene(n_emc, n_comp, 2.0, 0.0) for g in panel_genes}
    a_genes["ASS1"] = _gene(n_emc, n_comp, -1.5, 0.5, n_probes=3)
    a_genes["NR2F1"] = _gene(n_emc, n_comp, 1.0, 0.9)
    a_genes["ENO3"] = _gene(n_emc, n_comp, 2.5, 0.0)
    # platform B: only ONE of the 4-O sulfotransferases maps, so its panel must go UNDERPOWERED
    b_genes = {panel_genes[0]: _gene(n_emc, n_comp, 2.0, 0.0)}
    b_genes["ASS1"] = _gene(n_emc, n_comp, -1.0, 0.5)

    # --- read 7's cross-platform board: one gene planted in each state that must be
    # distinguishable. CD248 up on both; CSPG4 up on A and DOWN on B (the real 2026-08-07
    # discordance, reproduced in miniature); CD276 readable on A only; PRAME on neither.
    a_genes["CD248"] = _gene(n_emc, n_comp, 2.0, 0.0)
    b_genes["CD248"] = _gene(n_emc, n_comp, 2.0, 0.0)
    a_genes["CSPG4"] = _gene(n_emc, n_comp, 2.0, 0.0)
    b_genes["CSPG4"] = _gene(n_emc, n_comp, 0.0, 2.0)
    a_genes["CD276"] = _gene(n_emc, n_comp, 1.0, 0.95)
    return {
        "_generated_utc": "2026-01-01T00:00:00+00:00",
        "signature_sets": {
            "_enrichr_library_diagnostics": {}, "_libraries_loaded": {},
            "n_slots_resolved": 1, "slots_unresolved": ["hypoxia_buffa"],
            "slots": {
                "hypoxia_hallmark": {
                    "read_id": "read_5_HYPOXIA", "role": "hypoxia_metagene", "what": "synthetic",
                    "resolved_set": "Hypoxia", "matched_term_verbatim": "Hypoxia",
                    "library": "MSigDB_Hallmark_2020", "citation": "synthetic",
                    "provenance": "synthetic", "n_genes": 4,
                    "genes": sorted(a_genes)[:4], "candidates_tried": []},
                "hypoxia_buffa": {
                    "read_id": "read_5_HYPOXIA", "role": "hypoxia_metagene", "what": "synthetic",
                    "candidates_tried": [{"msigdb": "BUFFA_HYPOXIA_METAGENE", "error": "404"}],
                    "unresolved": "⚠ NOT RETRIEVED."},
            },
        },
        "n_genes_wanted": 99, "genes_wanted": sorted(a_genes),
        "targets": {
            "A_series_matrix.txt.gz": _target("A_series_matrix.txt.gz", "GPL_A", n_emc, n_comp,
                                              a_genes),
            "B_series_matrix.txt.gz": _target("B_series_matrix.txt.gz", "GPL_B", n_emc, n_comp,
                                              b_genes),
        },
    }


@pytest.fixture(scope="module")
def res():
    return M.derive(_inputs())


# ---------------------------------------------------------------------------------------------
# 1 — AN ABSENT READING IS NOT A READING OF ABSENCE
# ---------------------------------------------------------------------------------------------
def test_a_gene_with_no_probe_is_not_readable_and_never_says_not_expressed(res):
    ghost = res["gene_reads"]["CHST13"]["B_series_matrix.txt.gz"]
    assert ghost["readable"] is False
    assert ghost["n_probes_mapping"] == 0
    assert "NOT READABLE" in ghost["verdict"]
    assert "could not be taken" in ghost["verdict"]
    # the sentence a future reader might quote must actively refuse the absence reading
    assert "NOTHING about whether" in ghost["verdict"]
    low = ghost["verdict"].lower()
    for forbidden in ("is not expressed", "is absent", "not present in emc", "no expression"):
        assert forbidden not in low, f"unreadable verdict implies absence: {forbidden!r}"


def test_every_unreadable_verdict_in_the_whole_artifact_refuses_the_absence_reading(res):
    seen = 0
    for gene, per in res["gene_reads"].items():
        for mf, r in per.items():
            if r.get("readable"):
                continue
            seen += 1
            assert "NOTHING about whether" in r["verdict"], (gene, mf)
    assert seen > 0, "the fixture must contain at least one unreadable gene or this proves nothing"


def test_an_unresolved_signature_set_scores_nothing_and_says_so(res):
    buffa = res["signature_scores"]["hypoxia_buffa"]
    assert buffa["resolved"] is False
    assert "NOT RETRIEVED" in buffa["verdict"]
    assert "per_platform" not in buffa
    # and the failed attempt is kept, so 'we could not fetch it' stays distinguishable from
    # 'we never tried'
    assert buffa["candidates_tried"]


def test_a_platform_that_failed_to_read_marks_every_gene_unread_not_absent():
    inp = _inputs()
    inp["targets"]["B_series_matrix.txt.gz"] = {
        "gse": "GSE_TEST", "matrix_file": "B_series_matrix.txt.gz",
        "_status": "fetch failed: HTTP 500"}
    out = M.derive(inp)
    p = out["platforms"]["B_series_matrix.txt.gz"]
    assert "NOT READ" in p["verdict"]
    assert "absent reading, not an absence" in p["verdict"]
    # a failed platform contributes no gene rows at all rather than false ones
    assert "B_series_matrix.txt.gz" not in out["gene_reads"]["ASS1"]


# ---------------------------------------------------------------------------------------------
# 2 — A POPULATED FIELD IS NOT A MEASURED ONE
# ---------------------------------------------------------------------------------------------
def test_a_panel_below_the_coverage_floor_emits_no_score(res):
    grp = res["panels"]["cs_gag_paps"]["groups"]["cs_sulfotransferases_4O"]["per_platform"]
    good = grp["A_series_matrix.txt.gz"]
    thin = grp["B_series_matrix.txt.gz"]
    assert good["coverage"] == 1.0 and good["score"] is not None
    assert thin["n_genes_readable"] == 1
    assert thin["score"] is None, "a 1-of-4 panel must not emit a number"
    assert "UNDERPOWERED" in thin["verdict"]
    assert "instrument limit, not a reading" in thin["verdict"]
    # and the coverage is reported EITHER WAY, so the reader can see why
    assert thin["coverage"] == 0.25
    assert set(thin["genes_not_readable"]) == set(
        M.PANELS["cs_gag_paps"]["groups"]["cs_sulfotransferases_4O"][1:])


def test_the_signature_floor_is_stricter_than_the_curated_panel_floor():
    assert M.MIN_GENES_FOR_A_SIGNATURE_SCORE > M.MIN_GENES_FOR_A_PANEL_SCORE


def test_a_readable_gene_carries_the_evidence_only_a_real_run_produces(res):
    r = res["gene_reads"]["ASS1"]["A_series_matrix.txt.gz"]
    assert r["readable"] is True
    assert r["n_probes_mapping"] == 3 and len(r["probe_ids"]) == 3
    # the percentile can only come from the full parsed probe distribution
    assert r["EMC"]["mean_array_percentile"] is not None
    assert r["per_sample"] and all("array_percentile" in s for s in r["per_sample"])


def test_a_group_below_the_minimum_n_gets_no_contrast():
    inp = _inputs()
    t = inp["targets"]["A_series_matrix.txt.gz"]
    # collapse the comparator arm to two samples
    t["samples"] = _samples(6, 2)
    t["n_samples"] = 8
    t["background_per_sample"] = t["background_per_sample"][:8]
    for g in t["genes"].values():
        g["values"] = g["values"][:8]
        g["array_percentile"] = g["array_percentile"][:8]
    out = M.derive(inp)
    r = out["gene_reads"]["ASS1"]["A_series_matrix.txt.gz"]
    assert r["welch_EMC_vs_comparator"] is None
    assert "n_comparator=2" in r["_underpowered"]


# ---------------------------------------------------------------------------------------------
# 3 — THE READS, THEIR IDENTITY AND THEIR READABILITY VERDICT
# ---------------------------------------------------------------------------------------------
def test_every_read_declared_in_PANELS_is_actually_assembled_and_addressable(res):
    """⛔ DERIVED, NEVER TYPED (CLAUDE.md §1). A hand-listed set of read ids was the previous
    version of this assertion, and it is exactly the copy that goes stale the moment a read is
    added: `PANELS` would gain a member, `_assemble_reads` could silently not, and a typed list
    would have to be edited in two files to notice. The set of reads has ONE home — `PANELS` —
    and this test asserts the assembler agrees with it."""
    declared = {p["read_id"] for p in M.PANELS.values()}
    assert set(res["reads"]) == declared, (
        "PANELS and _assemble_reads disagree about which reads exist")
    for k, v in res["reads"].items():
        if k == "control":
            continue
        assert v["read_id"] == k
        assert v["question"] and v["what_it_cannot_settle"]
        assert v["readability_verdict"]["state"] in ("TAKEN", "PARTIALLY TAKEN", "NOT TAKEN")


def test_every_panel_and_every_slot_declares_the_read_it_belongs_to():
    ids = {p["read_id"] for p in M.PANELS.values()}
    for name, p in M.PANELS.items():
        assert p["read_id"] in ids, name
    for name, s in M.SIGNATURE_SLOTS.items():
        assert s["read_id"] in ids, name


def test_the_consumer_map_points_at_keys_that_exist(res):
    for key in ("read_2_CS_GAG_PAPS", "read_3_PPARG_ACTIVITY", "read_6_NR2F1"):
        assert key in res["_consumers"]
        assert key in res["reads"]


def test_a_read_with_an_unscored_unit_is_never_reported_as_TAKEN(res):
    # read 2's 4-O panel is underpowered on platform B in the fixture
    assert res["reads"]["read_2_CS_GAG_PAPS"]["readability_verdict"]["state"] == "PARTIALLY TAKEN"
    assert res["reads"]["read_2_CS_GAG_PAPS"]["readability_verdict"]["n_unscored_units"] > 0


def test_NOT_TAKEN_is_explicitly_documented_as_not_a_negative(res):
    meaning = res["reads"]["read_1_ASS1"]["readability_verdict"]["_meaning"]
    assert "NOT TAKEN is never a biological negative" in meaning


# ---------------------------------------------------------------------------------------------
# 4 — READ 3 MUST NOT QUIETLY BECOME AN ABUNDANCE READ
# ---------------------------------------------------------------------------------------------
def test_pparg_abundance_is_flagged_as_context_and_not_as_the_read(res):
    r = res["reads"]["read_3_PPARG_ACTIVITY"]
    assert r["abundance_context_only"]["is_the_read"] is False
    assert "pparg-direction-emc.md" in r["abundance_context_only"]["_warning"]
    assert "already measured twice" in r["abundance_is_not_the_read"].lower()
    # the group that holds PPARG names itself as not-the-read
    assert "abundance_context_NOT_the_read" in M.PANELS["pparg_target_activity"]["groups"]


def test_pparg_target_sets_come_from_more_than_one_instrument_class():
    roles = [s for k, s in M.SIGNATURE_SLOTS.items()
             if s["read_id"] == "read_3_PPARG_ACTIVITY" and s["role"] == "pparg_target_set"]
    libs = {tuple(sorted({k for k, _ in s["enrichr"]})) for s in roles}
    assert len(roles) >= 3, "one PPARG set is a choice this file cannot defend; several is evidence"
    assert len(libs) >= 3, "the sets must come from independent libraries, not one library thrice"


def test_the_adipogenesis_slot_is_labelled_a_process_not_a_target_set():
    assert M.SIGNATURE_SLOTS["adipogenesis_process_proxy"]["role"] \
        == "process_proxy_NOT_a_target_set"


# ⛔ THE ONE THAT WOULD HAVE SHIPPED A DIFFERENT GENE'S SIGNATURE. `_norm` strips punctuation, so
# "PPARGC1A ..." normalises to "ppargc1a..." — which STARTS WITH "pparg". Without the exclusion,
# every PPARG slot could resolve to a PGC-1α set and be scored, labelled and consumed as the PPARγ
# ACTIVITY read. PGC-1α is a coactivator of a different family, and it is also the gene the 2005 EMC
# profiling study reports alongside PPARG — so the confusion has a ready-made path into a paper.
#
# ⚠ THIS TEST DRIVES `fetch_signature_sets` WITH THE NETWORK LOADER REPLACED, NOT THE SELECTION.
# The thing under test is the term SELECTION; the loader is only how terms arrive. Mock the thing
# under test and you test the mock (CLAUDE.md §6).
def _fake_libs(monkeypatch, terms):
    def loader(keys):
        return ({k: {"library": f"fake_{k}", "citation": "fake", "terms": terms} for k in keys},
                {})
    monkeypatch.setattr(M, "_load_enrichr_libraries", loader)
    monkeypatch.setattr(M, "_get_once", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("404")))


def test_a_ppargc1a_term_can_never_be_selected_as_a_pparg_target_set(monkeypatch):
    _fake_libs(monkeypatch, {
        "PPARGC1A 12345 ChIP-Seq Liver Human": ["AAA", "BBB", "CCC"],
        "PPARG 26074081 ChIP-Seq Adipocyte Human": ["FABP4", "CD36", "LPL"],
        "PPARG 19300518 ChIP-ChIP 3T3-L1 Mouse": ["PLIN1", "ADIPOQ"],
    })
    out = M.fetch_signature_sets()
    # every slot that resolved for read 3 — whatever the slot list happens to be — must not have
    # taken a PPARGC1A term. Enumerated from the module so a new PPARG slot inherits the guard
    # instead of quietly escaping it.
    read3 = [k for k, s in M.SIGNATURE_SLOTS.items()
             if s["read_id"] == "read_3_PPARG_ACTIVITY" and "ppargc" in (s.get("exclude") or [])]
    assert read3, "no PPARG slot carries the exclusion — the guard has been removed"
    for slot in read3:
        rec = out["slots"][slot]
        if not rec.get("resolved_set"):
            continue
        assert "PPARGC1A" not in rec["resolved_set"], (slot, rec["resolved_set"])
        for alt in rec.get("all_matching_terms_verbatim") or []:
            assert "PPARGC1A" not in alt, (slot, alt)


def test_a_human_experiment_is_preferred_over_a_mouse_one_and_the_rule_is_recorded(monkeypatch):
    _fake_libs(monkeypatch, {
        "PPARG 19300518 ChIP-ChIP 3T3-L1 Mouse": ["PLIN1", "ADIPOQ"],
        "PPARG 26074081 ChIP-Seq Adipocyte Human": ["FABP4", "CD36", "LPL"],
    })
    rec = M.fetch_signature_sets()["slots"]["pparg_chip_chea"]
    assert rec["resolved_set"].endswith("Human")
    assert "preferred a term containing" in rec["selection_rule"]
    # and the alternative is still visible, so the choice is auditable rather than hidden
    assert any("Mouse" in t for t in rec["all_matching_terms_verbatim"])


# ⛔ THE ARM THAT CAN FAIL. Read 3 is the flagship read of this module, and a read with no arm that
# could disagree is not a read. `pparg_perturbation_KO_UP_CONTROL` is that arm; these tests pin that
# it selects the OPPOSITE term to KO_DOWN and that the requirement is HARD, so a library missing the
# control arm leaves it UNRESOLVED rather than silently handing read 3 a near-miss as its falsifier.
PERTURB_TERMS = {
    "PPARG DEFICIENCY MOUSE GSE23421 CREEDSID GENE 1231 DOWN": ["AAA", "BBB", "CCC"],
    "PPARG DEFICIENCY MOUSE GSE23421 CREEDSID GENE 1231 UP": ["DDD", "EEE", "FFF"],
    "PPARG OE MOUSE GSE10192 CREEDSID GENE 2731 UP": ["GGG", "HHH", "III"],
    "PPARG OE MOUSE GSE10192 CREEDSID GENE 2731 DOWN": ["JJJ", "KKK"],
}


def test_the_three_perturbation_arms_select_three_different_terms(monkeypatch):
    _fake_libs(monkeypatch, PERTURB_TERMS)
    slots = M.fetch_signature_sets()["slots"]
    ko_down = slots["pparg_perturbation_KO_DOWN"]["resolved_set"]
    oe_up = slots["pparg_perturbation_OE_UP"]["resolved_set"]
    ko_up = slots["pparg_perturbation_KO_UP_CONTROL"]["resolved_set"]
    assert ko_down.endswith("DOWN") and "DEFICIENCY" in ko_down
    assert oe_up.endswith("UP") and " OE " in oe_up
    assert ko_up.endswith("UP") and "DEFICIENCY" in ko_up
    assert len({ko_down, oe_up, ko_up}) == 3, "the control must not be the same set as an arm"
    assert slots["pparg_perturbation_KO_UP_CONTROL"]["role"] \
        == "directional_control_NOT_a_target_set"


def test_the_control_arm_stays_unresolved_when_the_library_cannot_supply_it(monkeypatch):
    _fake_libs(monkeypatch, {k: v for k, v in PERTURB_TERMS.items() if not k.endswith("1231 UP")})
    slots = M.fetch_signature_sets()["slots"]
    assert "genes" not in slots["pparg_perturbation_KO_UP_CONTROL"]
    assert "NOT RETRIEVED" in slots["pparg_perturbation_KO_UP_CONTROL"]["unresolved"]
    # and it must NOT have quietly taken the OE_UP term instead
    assert slots["pparg_perturbation_KO_DOWN"].get("resolved_set", "").endswith("DOWN")


def test_a_mouse_sourced_set_carries_its_orthology_caveat(monkeypatch):
    _fake_libs(monkeypatch, PERTURB_TERMS)
    rec = M.fetch_signature_sets()["slots"]["pparg_perturbation_KO_DOWN"]
    sp = rec["species_of_the_source_experiment"]
    assert sp["species"] == "mouse"
    assert "ORTHOLOGY ASSUMPTION" in sp["caveat"]


def test_a_human_sourced_set_carries_no_orthology_caveat(monkeypatch):
    _fake_libs(monkeypatch, {"PPARG human": ["AAA", "BBB", "CCC", "DDD"]})
    rec = M.fetch_signature_sets()["slots"]["pparg_curated_trrust"]
    assert rec["species_of_the_source_experiment"]["species"] == "human"
    assert rec["species_of_the_source_experiment"]["caveat"] is None


def test_a_slot_with_no_matching_term_stays_unresolved_rather_than_taking_a_near_miss(monkeypatch):
    _fake_libs(monkeypatch, {"PPARGC1A 1 ChIP Human": ["AAA", "BBB"]})
    rec = M.fetch_signature_sets()["slots"]["pparg_chip_chea"]
    assert "genes" not in rec
    assert "NOT RETRIEVED" in rec["unresolved"]
    assert any(c.get("n_terms_excluded") for c in rec["candidates_tried"])


# ---------------------------------------------------------------------------------------------
# 5 — LANGUAGE DISCIPLINE, ASSERTED OVER THE WHOLE SERIALISED ARTIFACT
# ---------------------------------------------------------------------------------------------
# ⚠ A NAIVE SUBSTRING BAN CANNOT WORK HERE, and finding that out is the point of this comment.
# The first version of this test banned "is safe in" — and the artifact's own disclaimer says
# *"...asserts nothing about whether any CS-directed agent binds, works or is safe in EMC"*, which
# is a REFUSAL of exactly the claim being banned. A linter that cannot tell an assertion from its
# negation would push the file toward saying LESS about what it cannot conclude, which is backwards.
# So the rule is proximity: every efficacy/safety token must sit inside a window that also carries a
# negation. An unqualified one is the failure.
EFFICACY_TOKENS = ("efficacy", "efficacious", "safety", " safe ", "therapeutic window",
                   "clinically ready", "clinical readiness", "validated target")
NEGATORS = ("not ", "no ", "nothing", "never", "cannot", "n't", "without", "⛔", "⚠",
            "asserts nothing", "says nothing", "is not", "neither")
WINDOW = 200


def test_every_efficacy_or_safety_token_in_the_artifact_sits_inside_a_negation(res):
    blob = json.dumps(res).lower()
    offenders = []
    for tok in EFFICACY_TOKENS:
        start = 0
        while True:
            i = blob.find(tok, start)
            if i < 0:
                break
            start = i + 1
            ctx = blob[max(0, i - WINDOW): i + WINDOW]
            if not any(n in ctx for n in NEGATORS):
                offenders.append((tok, ctx))
    assert not offenders, (
        "an efficacy/safety token appears with no negation nearby:\n"
        + "\n".join(f"  {t}: ...{c}..." for t, c in offenders[:5]))


def test_the_artifact_states_its_own_framing_and_its_own_limits(res):
    assert "NOT evidence of efficacy" in res["_framing"]
    assert res["_what_this_cannot_conclude"] and res["_limits"]
    assert any("multiple-testing" in x.lower() or "multiple testing" in x.lower()
               for x in res["_limits"])
    assert "ABSENT READING IS NOT A READING OF ABSENCE" in res["_the_rule_that_governs_every_row"]


def test_the_artifact_is_json_serialisable_and_derive_is_deterministic():
    a = M.derive(_inputs())
    b = M.derive(_inputs())
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


# ---------------------------------------------------------------------------------------------
# 6 — ARITHMETIC, PINNED AGAINST A HAND-COMPUTED CASE
# ---------------------------------------------------------------------------------------------
def test_the_within_sample_z_is_value_minus_array_mean_over_array_sd():
    inp = _inputs()
    t = inp["targets"]["A_series_matrix.txt.gz"]
    t["background_per_sample"] = [{"mean": 1.0, "sd": 2.0, "n": 1000}
                                  for _ in range(t["n_samples"])]
    t["genes"]["ASS1"]["values"] = [5.0] * t["n_samples"]
    z = M._zrow(t, "ASS1")
    assert all(abs(x - 2.0) < 1e-9 for x in z)      # (5 - 1) / 2


def test_the_sign_convention_is_stated_and_correct(res):
    r = res["gene_reads"]["ASS1"]["A_series_matrix.txt.gz"]
    w = r["welch_EMC_vs_comparator"]
    assert w["delta_a_minus_b"] < 0, "ASS1 was built LOWER in EMC in the fixture"
    assert "LOWER in EMC" in r["verdict"]
    assert "delta_a_minus_b > 0 means HIGHER in EMC" in r["_sign"]


# ---------------------------------------------------------------------------------------------
# 7 — ONE FACT, ONE PLACE: the priors must agree with the artifact they are quoted from
# ---------------------------------------------------------------------------------------------
# ⛔ THE GUARD THAT CRIED DRIFT ON A CLEAN RUN (measured 2026-08-07, run 31182233077). The prior in
# `TARGETS` is an ACCESSION-resolution rate; this module also measures a PROBE-level rate. Comparing
# the two printed "MOVED by 22 points" on GPL6244 and "MOVED by 5 points" on GPL3290, while the
# like-for-like figures were 0.983 (better) and 0.582 (identical to the prior). A guard that fires on
# a clean run trains the next reader to skip the line that would have caught a real one.
def _target_with(acc_rate, probe_rate, prior):
    return {"probe_symbol_mapping": {"accession_resolution_rate": acc_rate},
            "measured_probe_mapping_rate": probe_rate,
            "prior_probe_mapping_rate": prior, "prior_source": "x"}


def test_the_drift_check_compares_the_accession_rate_not_the_probe_rate():
    # the real GPL3290 numbers from run 31182233077: accession rate identical to the prior, probe
    # rate 5 points away from it. The verdict must follow the accession rate.
    r = M._mapping_rate_reading(_target_with(0.582, 0.6326, 0.582))
    assert r["reading"] == "consistent with the prior characterisation"
    assert r["abs_difference_vs_prior"] == 0.0
    assert r["accession_resolution_rate"] == 0.582
    assert r["probe_level_rate"] == 0.6326


def test_both_rates_are_reported_and_each_says_what_it_measures():
    r = M._mapping_rate_reading(_target_with(0.983, 0.7109, 0.932))
    assert "probes ON THIS MATRIX" in r["_probe_level_rate_means"]
    assert "distinct GenBank accessions" in r["_accession_resolution_rate_means"]
    assert "comparable to the prior" in r["_accession_resolution_rate_means"]


# ⛔ A RATE THAT IMPROVED AND A RATE THAT DEGRADED MUST NOT RENDER ALIKE. The real GPL6244 numbers
# from run 31182233077 are 0.983 against a 0.932 prior — 5.1 points UP, so it flags, and the first
# wording sent the reader to "a failed UniGene fetch" for a run in which the UniGene archive had
# resolved 51,071 accessions. Same shape as the paying-vs-refused rule in CLAUDE.md §1: one glyph,
# one meaning.
def test_an_improved_rate_flags_but_says_it_improved():
    r = M._mapping_rate_reading(_target_with(0.983, 0.7109, 0.932))
    assert "MOVED UP" in r["reading"]
    assert "MORE accessions resolved" in r["reading"]
    assert "Not a failure" in r["reading"]
    assert r["direction_vs_prior"] == "more accessions resolved than the prior run"


def test_a_degraded_rate_flags_and_points_at_the_things_that_break():
    r = M._mapping_rate_reading(_target_with(0.30, 0.60, 0.582))
    assert "MOVED DOWN" in r["reading"]
    assert "FEWER accessions resolved" in r["reading"]
    assert "ncbi_global_budget_exhausted" in r["reading"]
    assert r["direction_vs_prior"] == "fewer accessions resolved than the prior run"


def test_a_missing_accession_rate_is_an_absent_reading_not_agreement():
    r = M._mapping_rate_reading(_target_with(None, 0.60, 0.582))
    assert "COULD NOT BE MADE" in r["reading"]
    assert "absent reading, not agreement" in r["reading"]
    assert "abs_difference_vs_prior" not in r


@pytest.mark.committed_artifact
def test_the_probe_mapping_priors_agree_with_emc_atr_vulnerability_json():
    path = os.path.join(MOD, "emc-atr-vulnerability.json")
    if not os.path.exists(path):
        pytest.skip("emc-atr-vulnerability.json is not present in this checkout")
    d = json.load(open(path))
    readability = d["part_b_emc_tumour_signature"]["series_readability"]
    for t in M.TARGETS:
        rates = readability[t["gse"]]["probe_mapping_rate_per_platform"]
        assert rates[t["platform_expected"]] == t["prior_probe_mapping_rate"], (
            f"{t['gse']}/{t['platform_expected']}: this module's prior "
            f"({t['prior_probe_mapping_rate']}) disagrees with its one home "
            f"({rates[t['platform_expected']]}). Update TARGETS, do not loosen the test.")


@pytest.mark.committed_artifact
def test_the_named_matrix_files_are_the_ones_that_series_actually_publishes():
    path = os.path.join(MOD, "emc-atr-vulnerability.json")
    if not os.path.exists(path):
        pytest.skip("emc-atr-vulnerability.json is not present in this checkout")
    d = json.load(open(path))
    readability = d["part_b_emc_tumour_signature"]["series_readability"]
    for t in M.TARGETS:
        assert t["matrix_file"] in readability[t["gse"]]["matrix_files"], t["matrix_file"]
        # and it must be one the prior run graded READABLE, or this module is reading a platform
        # that has already been measured not to carry a contrast
        assert t["matrix_file"] in readability[t["gse"]]["readable_platforms"], t["matrix_file"]


# ---------------------------------------------------------------------------------------------
# 6 — READ 7's CROSS-PLATFORM BOARD
#
# ⛔ WHAT IS PINNED HERE is the one way a surface-antigen board can do real damage: rendering an
# antigen nobody measured the same as an antigen that was measured and came back low. Five routes
# are blocked on "any measurement in EMC", so a row that reads as a measurement when it is not one
# would close a live route on nothing (CLAUDE.md §4 — an absent reading is not a reading of
# absence). The second guard is the discordance: two platforms disagreeing must not be silently
# resolved by whichever one the module happens to iterate first.
# ---------------------------------------------------------------------------------------------
def test_an_antigen_up_on_both_platforms_is_the_only_state_called_a_lead(res):
    board = res["reads"]["read_7_SURFACE_ANTIGEN"]["cross_platform_board"]
    assert board["per_gene"]["CD248"]["state"] == "CONCORDANT_UP_ON_BOTH"
    assert "CD248" in board["by_state"]["CONCORDANT_UP_ON_BOTH"]
    for mf, p in board["per_gene"]["CD248"]["per_platform"].items():
        assert p["readable"] is True and p["t"] is not None


def test_two_platforms_disagreeing_in_sign_is_reported_as_discordant_not_resolved(res):
    row = res["reads"]["read_7_SURFACE_ANTIGEN"]["cross_platform_board"]["per_gene"]["CSPG4"]
    assert row["state"] == "DISCORDANT_OPPOSITE_SIGNS"
    # BOTH readings survive into the artifact — neither platform is dropped
    ts = sorted(p["t"] for p in row["per_platform"].values())
    assert ts[0] < 0 < ts[-1], "a discordant gene must keep both signs"
    disc = res["reads"]["read_7_SURFACE_ANTIGEN"]["CSPG4_platform_discordance"]
    assert disc["cross_platform"]["state"] == "DISCORDANT_OPPOSITE_SIGNS"
    assert disc["what_would_actually_decide_it"]


def test_an_antigen_read_on_one_platform_only_is_an_instrument_statement(res):
    board = res["reads"]["read_7_SURFACE_ANTIGEN"]["cross_platform_board"]
    row = board["per_gene"]["CD276"]
    assert row["state"] == "READABLE_ON_ONE_PLATFORM_ONLY"
    assert row["platforms_readable"] == ["A_series_matrix.txt.gz"]
    assert "not a low reading" in row["_meaning"]["READABLE_ON_ONE_PLATFORM_ONLY"]


def test_an_unmeasured_antigen_never_renders_as_a_measured_negative(res):
    board = res["reads"]["read_7_SURFACE_ANTIGEN"]["cross_platform_board"]
    row = board["per_gene"]["PRAME"]
    assert row["state"] == "NOT_READABLE_ON_EITHER_PLATFORM"
    assert row["platforms_with_a_contrast"] == []
    for p in row["per_platform"].values():
        assert p["readable"] is False
        low = str(p["verdict"]).lower()
        for forbidden in ("is not expressed", "is absent", "no expression", "not present in emc"):
            assert forbidden not in low
    assert "never a biological" in row["_meaning"]["NOT_READABLE_ON_EITHER_PLATFORM"].lower()


def test_the_board_refuses_the_four_over_claims_a_surface_antigen_invites(res):
    entry = res["reads"]["read_7_SURFACE_ANTIGEN"]
    cannot = entry["what_it_cannot_settle"].lower()
    for must in ("not protein", "not surface localisation", "not tumour-restricted",
                 "not deconvolved"):
        assert must in cannot, must
    # the missing axis is named WITH the artifact that holds it, not left as a caveat
    assert "emc-surface-normal-window.json" in entry["the_missing_axis_and_where_it_lives"][
        "artifact"]


def test_PRAME_is_declared_not_a_surface_antigen_where_a_reader_would_see_it(res):
    """PRAME is an ImmTAC address reached through HLA class I, not through the cell surface. A
    board that lists it beside CD276 without saying so invites exactly the wrong modality."""
    ann = res["reads"]["read_7_SURFACE_ANTIGEN"]["group_annotations"]
    assert "PRAME IS NOT A SURFACE ANTIGEN" in ann[
        "hla_presented_intracellular_antigens_NOT_surface"]
    # and the presentation machinery is measured, so a PRAME number can never stand alone
    groups = M.PANELS["surface_antigen"]["groups"]["antigen_presentation_precondition"]
    assert {"B2M", "TAP1", "HLA-A"} <= set(groups)


def test_every_route_named_address_is_in_the_board(res):
    board = res["reads"]["read_7_SURFACE_ANTIGEN"]["cross_platform_board"]["per_gene"]
    for g in M.PANELS["surface_antigen"]["groups"]["route_named_addresses"]:
        assert g in board, f"{g} is named by a blocked route but is not on the board"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
