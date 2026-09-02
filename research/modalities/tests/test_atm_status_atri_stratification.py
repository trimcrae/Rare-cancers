"""ATM-status stratification of the GDSC2 residuals: the properties that decide how it READS.

WHY THIS FILE EXISTS, AND WHY EACH TEST IS HERE RATHER THAN LEFT TO INSPECTION
------------------------------------------------------------------------------
This module's whole output is a set of signed contrasts, so a sign convention is not a detail — it
is the result. ⚠ THE FIRST TEST BELOW GUARDS A BUG THAT WAS ACTUALLY IN THE FIRST DRAFT: Cliff's
delta was negated on the way out, so a null arm sitting LOWER (more sensitive, the direction the
mechanism predicts) reported `cliffs_delta: +1.0` against a docstring promising negative. It was
caught by planting a strictly ordered pair and reading the number, which is exactly what
`test_cliffs_delta_is_negative_when_the_null_arm_is_more_sensitive` now does on every run.

The rest guard the three claims the artifact makes about its own honesty, each of which would fail
SILENTLY and look like a measurement:

  1. ⚠ AN ABSENT READING MUST NOT BECOME A READING OF ABSENCE (CLAUDE.md §4). A GDSC model DepMap
     never sequenced must land in NEITHER arm. Counting it as intact would inflate the comparator
     with un-genotyped lines and make every contrast look better-powered than it is.
  2. ⛔ THE POWER FLOOR MUST REFUSE, NOT REPORT. Below the pre-declared arm size the module must
     return the n and no contrast. The failure mode it prevents is a confident p-value computed on
     four cell lines.
  3. ⛔ A COPY-NUMBER SCALE THAT IS NOT RECOGNISED MUST DISABLE THE CN ARM, NOT GUESS. DepMap has
     shipped this matrix on more than one scale; a deep-deletion cut applied to the wrong one
     produces an empty arm or a nonsense one, and both look like data.
  4. ⚠ A COLUMN THAT IS PRESENT BUT BLANK IS NOT AN ANNOTATION. If the preferred damaging-call
     column exists in the header but is populated for no row, the module must fall through to the
     next candidate rather than report `n_models_damaging_mutation: 0`.

Also pinned: the framing string, because this module's numbers are about an instrument and must
never travel as evidence that an ATR inhibitor kills EMC cells.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import atm_status_atri_stratification as M  # noqa: E402


# ---------------------------------------------------------------------------------------------
# fixtures: a synthetic inputs cache and a synthetic part-D residual cache with a PLANTED answer
# ---------------------------------------------------------------------------------------------
def _models(n, prefix="ACH-9"):
    return [f"{prefix}{i:05d}" for i in range(n)]


def _inputs(damaged=(), sequenced=(), cn_models=(), cn_values=None, cn_median=1.02,
            mut_columns=None, extra_rows=None):
    cols = mut_columns or ["ModelID", "HugoSymbol", "LikelyLoF", "VariantInfo"]
    rows = [{"ModelID": m, "HugoSymbol": "ATM", "LikelyLoF": "True", "VariantInfo": "damaging"}
            for m in damaged]
    if extra_rows:
        rows = list(extra_rows)
    return {
        "_status": "read", "fetched_utc": "2026-09-02T00:00:00Z", "depmap_release": "TEST",
        "depmap_figshare_article": 1, "source_files": {"OmicsSomaticMutations.csv": "u"},
        "genes": list(M.GENES),
        "mutations": {"columns": cols, "model_id_column": "ModelID",
                      "gene_symbol_column": "HugoSymbol", "_status": "read",
                      "n_rows_scanned": 10, "profiled_models": sorted(sequenced),
                      "gene_rows": {"ATM": rows, "BRCA1": [], "BRCA2": []}},
        "copy_number": {"_status": "read", "profiled_models": sorted(cn_models),
                        "n_rows_scanned": len(cn_models),
                        "panel_median_sample": {"gene": "ATM", "n": len(cn_models),
                                                "median": cn_median},
                        "by_gene": {g: dict(cn_values or {}) for g in M.GENES}},
        "model_metadata": {"_status": "read", "n_models": 0, "by_model": {}},
    }


def _part_d(tmp_path, resid):
    p = tmp_path / "pd.json"
    p.write_text(json.dumps({"part_d": {"gdsc_residual_ln_ic50_by_drug": resid,
                                        "gdsc_meta": {"source": "TEST", "n_rows": 1}}}))
    return str(p)


@pytest.fixture()
def derive(tmp_path, monkeypatch):
    def _run(inp, resid):
        monkeypatch.setattr(M, "PART_D_INPUTS", _part_d(tmp_path, resid))
        return M.derive(inp)
    return _run


# ---------------------------------------------------------------------------------------------
# 1 · THE SIGN CONVENTION — the bug this file was written around
# ---------------------------------------------------------------------------------------------
def test_cliffs_delta_is_negative_when_the_null_arm_is_more_sensitive():
    """⛔ THE FIRST DRAFT GOT THIS BACKWARDS AND EVERY CONTRAST WOULD HAVE READ INVERTED.

    GDSC reports LN_IC50, so LOWER = MORE SENSITIVE. Cliff's delta is P(a>b) - P(a<b); with `a` the
    null arm, a null arm that is uniformly lower must give exactly -1.0.
    """
    out = M._mannwhitney([1.0, 1.1, 1.2], [5.0, 5.1, 5.2])
    assert out["cliffs_delta"] == -1.0, out
    flipped = M._mannwhitney([5.0, 5.1, 5.2], [1.0, 1.1, 1.2])
    assert flipped["cliffs_delta"] == 1.0, flipped


def test_the_hodges_lehmann_shift_agrees_in_sign_with_cliffs_delta():
    """The two effect measures must never disagree about direction — that is how an inverted sign
    survives review: one number says sensitive, the other says resistant, and a reader picks one."""
    a, b = [1.0, 1.4, 0.9, 1.2], [3.0, 3.4, 2.9, 3.2]
    mw, hl = M._mannwhitney(a, b), M._hodges_lehmann(a, b)
    assert mw["cliffs_delta"] < 0 and hl["shift"] < 0, (mw, hl)


def test_a_tiny_p_value_does_not_print_as_an_exact_zero():
    """A p rounded to 6 decimals prints 4e-16 as `0.0`, which reads as an exact zero rather than as
    'below what this normal approximation resolves'."""
    a, b = [float(i) for i in range(40)], [float(i) + 25 for i in range(40)]
    p = M._mannwhitney(a, b)["p_two_sided"]
    assert p > 0.0, "a p-value must never be reported as exactly zero"


# ---------------------------------------------------------------------------------------------
# 2 · AN ABSENT READING IS NOT A READING OF ABSENCE
# ---------------------------------------------------------------------------------------------
def test_a_gdsc_model_depmap_never_sequenced_enters_neither_arm(derive):
    seq = _models(30)
    unsequenced = _models(12, prefix="ACH-8")
    resid = {"azd6738": {m: 0.0 for m in seq + unsequenced}}
    art = derive(_inputs(damaged=seq[:12], sequenced=seq, cn_models=[]), resid)
    join = art["by_gene"]["ATM"]["join"]
    assert join["n_gdsc_models"] == len(seq) + len(unsequenced)
    assert join["n_gdsc_models_with_no_depmap_call"] == len(unsequenced)
    assert join["n_null_arm_primary"] + join["n_intact_arm_primary"] == len(seq), (
        "the un-sequenced models must be excluded from BOTH arms, not counted as intact")


def test_the_unprofiled_count_is_reported_rather_than_silently_dropped(derive):
    seq = _models(25)
    resid = {"azd6738": {m: 0.0 for m in seq + _models(9, prefix="ACH-7")}}
    art = derive(_inputs(damaged=seq[:11], sequenced=seq, cn_models=[]), resid)
    assert art["by_gene"]["ATM"]["join"]["n_gdsc_models_with_no_depmap_call"] == 9


# ---------------------------------------------------------------------------------------------
# 3 · THE POWER FLOOR REFUSES RATHER THAN REPORTS
# ---------------------------------------------------------------------------------------------
def test_an_arm_below_the_declared_floor_is_refused_and_returns_its_n(derive):
    seq = _models(60)
    resid = {"azd6738": {m: float(i % 7) for i, m in enumerate(seq)}}
    art = derive(_inputs(damaged=seq[:3], sequenced=seq, cn_models=[]), resid)
    row = art["by_gene"]["ATM"]["contrasts"][
        "primary_damaging_mutation_or_deep_deletion"]["by_drug"]["azd6738"]
    assert row["n_null_arm"] == 3
    assert "REFUSED" in row["_status"]
    assert "mannwhitney" not in row, "no test statistic may be computed below the floor"
    assert art["verdict"] == "UNDERPOWERED"


def test_the_power_floor_is_a_constant_and_not_derived_from_the_data():
    """⛔ A floor computed from the n it is judging is not a floor. It is pre-declared so it cannot
    be tuned to whatever the join happened to return."""
    assert isinstance(M.MIN_ARM_N, int) and M.MIN_ARM_N >= 2


def test_every_read_row_carries_the_minimum_detectable_effect(derive):
    """A null must be readable as 'no effect THIS LARGE is detectable here', which needs the MDE on
    the row rather than in a footnote."""
    seq = _models(80)
    resid = {"azd6738": {m: float(i % 5) for i, m in enumerate(seq)}}
    art = derive(_inputs(damaged=seq[:20], sequenced=seq, cn_models=[]), resid)
    row = art["by_gene"]["ATM"]["contrasts"][
        "primary_damaging_mutation_or_deep_deletion"]["by_drug"]["azd6738"]
    assert row["min_detectable_cliffs_delta_80pct_power"] is not None
    assert 0 < row["min_detectable_cliffs_delta_80pct_power"] < 2


# ---------------------------------------------------------------------------------------------
# 4 · THE COPY-NUMBER SCALE IS DETECTED, NEVER ASSUMED
# ---------------------------------------------------------------------------------------------
@pytest.mark.parametrize("median,expect_used", [(1.02, True), (0.02, False), (2.01, False),
                                                (7.7, False)])
def test_an_unrecognised_cn_scale_disables_the_cn_arm_rather_than_guessing(derive, median,
                                                                          expect_used):
    seq = _models(40)
    resid = {"azd6738": {m: 0.0 for m in seq}}
    inp = _inputs(damaged=seq[:12], sequenced=seq, cn_models=seq,
                  cn_values={m: 0.0 for m in seq}, cn_median=median)
    art = derive(inp, resid)
    assert art["by_gene"]["ATM"]["cn_used"] is expect_used, (
        f"panel median {median} must {'enable' if expect_used else 'disable'} the CN arm")


def test_a_deep_deletion_is_only_called_on_a_scale_with_a_declared_threshold(derive):
    """With every CN value at 0.0 and a recognised log2(CN+1) scale, all profiled models are deep
    deletions; with an unrecognised scale, none is — and the difference must be the SCALE, not the
    values."""
    seq = _models(40)
    resid = {"azd6738": {m: 0.0 for m in seq}}
    vals = {m: 0.0 for m in seq}
    known = derive(_inputs(damaged=[], sequenced=seq, cn_models=seq, cn_values=vals,
                           cn_median=1.02), resid)
    unknown = derive(_inputs(damaged=[], sequenced=seq, cn_models=seq, cn_values=vals,
                             cn_median=7.7), resid)
    assert known["by_gene"]["ATM"]["n_models_deep_deletion"] == len(seq)
    assert unknown["by_gene"]["ATM"]["n_models_deep_deletion"] == 0


# ---------------------------------------------------------------------------------------------
# 5 · A PRESENT-BUT-BLANK ANNOTATION COLUMN IS NOT AN ANNOTATION
# ---------------------------------------------------------------------------------------------
def test_a_present_but_unpopulated_call_column_falls_through_to_the_next_candidate(derive):
    """⛔ THE SILENT UNDER-COUNT. `LikelyLoF` is the preferred column; if a release ships it blank,
    stopping there would report zero damaging ATM models with total confidence."""
    seq = _models(40)
    rows = [{"ModelID": m, "HugoSymbol": "ATM", "LikelyLoF": "", "VariantInfo": "damaging"}
            for m in seq[:15]]
    resid = {"azd6738": {m: float(i % 6) for i, m in enumerate(seq)}}
    art = derive(_inputs(sequenced=seq, cn_models=[], extra_rows=rows), resid)
    g = art["by_gene"]["ATM"]
    assert g["damaging_call_column"] == "VariantInfo", g["damaging_call_candidate_audit"]
    assert g["n_models_damaging_mutation"] == 15


def test_no_populated_call_column_at_all_is_recorded_as_an_absent_annotation(derive):
    seq = _models(40)
    rows = [{"ModelID": m, "HugoSymbol": "ATM", "LikelyLoF": "", "VariantInfo": ""}
            for m in seq[:15]]
    resid = {"azd6738": {m: 0.0 for m in seq}}
    art = derive(_inputs(sequenced=seq, cn_models=[], extra_rows=rows), resid)
    g = art["by_gene"]["ATM"]
    assert g["damaging_call_column"] is None
    assert "ABSENCE OF ANNOTATION" in g["damaging_call_note"]


# ---------------------------------------------------------------------------------------------
# 6 · THE VERDICT MUST NOT SOFTEN THE OUTCOME THAT MATTERS MOST
# ---------------------------------------------------------------------------------------------
def test_a_working_instrument_and_a_flat_atm_row_is_not_the_same_verdict_as_a_dead_instrument(
        derive, tmp_path, monkeypatch):
    """⭐ THE WHOLE POINT OF THE MACHINERY CONTROL. 'ATM does nothing here' means something
    different depending on whether the same pipeline can see a known genotype-drug association."""
    seq = _models(120)
    resid = {d: {m: float((i * 7) % 11) / 3.0 for i, m in enumerate(seq)}
             for d in ("azd6738", "ve-822", "olaparib", "talazoparib", "paclitaxel", "bortezomib")}
    inp = _inputs(damaged=seq[:25], sequenced=seq, cn_models=[])
    # BRCA1 null lines, planted strongly PARP-sensitive
    inp["mutations"]["gene_rows"]["BRCA1"] = [
        {"ModelID": m, "HugoSymbol": "BRCA1", "LikelyLoF": "True", "VariantInfo": "damaging"}
        for m in seq[60:85]]
    for m in seq[60:85]:
        resid["talazoparib"][m] -= 4.0
        resid["olaparib"][m] -= 4.0
    art = derive(inp, resid)
    assert art["verdict"] == "NULL_WITH_WORKING_INSTRUMENT", art["verdict_reading"]
    assert art["detected"]["machinery_control_BRCA_vs_PARP"], art["detected"]


def test_a_dead_instrument_verdict_says_the_nulls_mean_less_and_does_not_hedge(derive):
    seq = _models(120)
    resid = {d: {m: float((i * 7) % 11) / 3.0 for i, m in enumerate(seq)}
             for d in ("azd6738", "ve-822", "olaparib", "talazoparib", "paclitaxel", "bortezomib")}
    art = derive(_inputs(damaged=seq[:25], sequenced=seq, cn_models=[]), resid)
    assert art["verdict"] == "INSTRUMENT_CANNOT_DETECT"
    assert "UNINFORMATIVE rather than NEGATIVE" in art["verdict_reading"]


def test_a_control_that_separates_as_hard_as_the_atr_inhibitors_blocks_a_mechanism_reading(derive):
    seq = _models(120)
    resid = {d: {m: float((i * 7) % 11) / 3.0 for i, m in enumerate(seq)}
             for d in ("azd6738", "ve-822", "olaparib", "talazoparib", "paclitaxel", "bortezomib")}
    for m in seq[:25]:          # the null arm is more sensitive to EVERYTHING
        for d in resid:
            resid[d][m] -= 4.0
    art = derive(_inputs(damaged=seq[:25], sequenced=seq, cn_models=[]), resid)
    assert art["verdict"] == "NON_SPECIFIC_SEPARATION", art["verdict_reading"]


# ---------------------------------------------------------------------------------------------
# 7 · THE FRAMING TRAVELS WITH THE NUMBERS
# ---------------------------------------------------------------------------------------------
def test_the_framing_and_the_cannot_conclude_list_are_in_the_artifact(derive):
    seq = _models(40)
    resid = {"azd6738": {m: 0.0 for m in seq}}
    art = derive(_inputs(damaged=seq[:12], sequenced=seq, cn_models=[]), resid)
    assert art["_framing"] == M.FRAMING
    assert "NOT evidence that an ATR inhibitor kills EMC cells" in art["_framing"]
    txt = " ".join(art["_what_this_cannot_conclude"])
    assert "Anything about a patient." in art["_what_this_cannot_conclude"]
    assert "fusion" in txt.lower(), (
        "the list must say that a mutation call cannot stand in for fusion-driven suppression")


def test_the_prediction_is_registered_in_the_artifact_before_any_number(derive):
    seq = _models(40)
    resid = {"azd6738": {m: 0.0 for m in seq}}
    art = derive(_inputs(damaged=seq[:12], sequenced=seq, cn_models=[]), resid)
    pred = art["_prediction_registered_before_the_numbers"]
    assert "delta < 0" in pred["ATR_inhibitors"]
    assert "NO PREDICTION" in pred["non_DDR_controls"]


def test_the_gdsc_residuals_are_read_from_part_d_and_never_recomputed(derive):
    seq = _models(40)
    resid = {"azd6738": {m: 0.0 for m in seq}}
    art = derive(_inputs(damaged=seq[:12], sequenced=seq, cn_models=[]), resid)
    assert "emc-atr-vulnerability-inputs.json" in art["gdsc_source"]["_from"]
    assert "READ, NOT RECOMPUTED" in art["gdsc_source"]["_note"]


# ---------------------------------------------------------------------------------------------
# 8 · A FAILED FETCH MUST NOT BE PUBLISHABLE OVER A GOOD ARTIFACT
# ---------------------------------------------------------------------------------------------
def test_an_unpopulated_inputs_cache_produces_something_the_stub_guard_will_drop(tmp_path,
                                                                                 monkeypatch):
    """⛔ THE PUBLISH-PATH DEFECT THIS REPOSITORY HAS ALREADY PAID FOR ONCE.

    `artifact_stub_guard.is_stub` defines a stub as a JSON object whose every top-level key starts
    with `_`. A NO_DATA object carrying `verdict` and `depmap_release` would sail through it and
    overwrite a real result after a network blip — which is exactly how `emc-fet-idr-census.json`
    became a two-key stub on `main`.
    """
    import artifact_stub_guard as G

    monkeypatch.setattr(M, "PART_D_INPUTS", str(tmp_path / "absent.json"))
    for inp in ({"_status": "inputs cache absent — run --refresh in CI"},
                {"_status": "read"}):
        art = M.derive(inp)
        p = tmp_path / "a.json"
        p.write_text(json.dumps(art))
        assert G.is_stub(str(p)), f"a failure artifact must be droppable by the guard: {art}"


def test_a_real_result_is_not_mistaken_for_a_stub(derive, tmp_path):
    """The other half — the guard must not drop a genuine artifact."""
    import artifact_stub_guard as G

    seq = _models(60)
    resid = {"azd6738": {m: float(i % 6) for i, m in enumerate(seq)}}
    art = derive(_inputs(damaged=seq[:20], sequenced=seq, cn_models=[]), resid)
    p = tmp_path / "b.json"
    p.write_text(json.dumps(art))
    assert not G.is_stub(str(p))


def test_main_refuses_to_overwrite_a_real_artifact_with_a_no_data_stub(tmp_path, monkeypatch,
                                                                       capsys):
    """⛔ THE STUB GUARD PROTECTS CI'S PUBLISH PATH, NOT THE WORKING TREE.

    Running the derive half in the dev sandbox — where the DepMap fetch cannot run, so the inputs
    cache is absent — must not overwrite a committed result with a NO_DATA stub that the next
    `git add` would carry.
    """
    real = tmp_path / "art.json"
    real.write_text(json.dumps({"verdict": "REAL", "by_gene": {}}))
    monkeypatch.setattr(M, "OUT", str(real))
    monkeypatch.setattr(M, "INPUTS", str(tmp_path / "absent-inputs.json"))
    monkeypatch.setattr(M, "PART_D_INPUTS", str(tmp_path / "absent-pd.json"))
    monkeypatch.setattr(sys, "argv", ["atm_status_atri_stratification.py"])
    rc = M.main()
    assert rc == 1
    assert json.loads(real.read_text())["verdict"] == "REAL", "the real artifact must survive"
    assert "REFUSING to overwrite" in capsys.readouterr().err


# ---------------------------------------------------------------------------------------------
# 9 · THE CONTROLS ARE JUDGED TWO-SIDED, AND THE AWKWARD DRUG IS ALWAYS REPORTED
# ---------------------------------------------------------------------------------------------
def test_a_control_separating_the_OTHER_way_still_blocks_a_mechanism_reading(derive):
    """⛔ THE ONE-SIDED CONTROL BUG. A null arm that is uniformly MORE RESISTANT to paclitaxel is
    exactly the lineage/growth-rate artefact the control exists to catch — but a control scored
    one-sided (shift < 0 only) reads it as clean and lets the ATR-inhibitor hit stand."""
    seq = _models(120)
    resid = {d: {m: float((i * 7) % 11) / 3.0 for i, m in enumerate(seq)}
             for d in ("azd6738", "ve-822", "olaparib", "talazoparib", "paclitaxel", "bortezomib")}
    for m in seq[:25]:
        resid["azd6738"][m] -= 4.0        # ATRi: null arm more SENSITIVE (predicted direction)
        resid["ve-822"][m] -= 4.0
        resid["paclitaxel"][m] += 4.0     # control: null arm more RESISTANT — no prediction, but
        resid["bortezomib"][m] += 4.0     # a separation all the same
    art = derive(_inputs(damaged=seq[:25], sequenced=seq, cn_models=[]), resid)
    assert art["detected"]["ATM_vs_non_DDR_controls"], (
        "a control separating upward must still register as a separation")
    assert art["verdict"] == "NON_SPECIFIC_SEPARATION", art["verdict_reading"]


def test_the_atr_inhibitors_stay_directional_so_a_resistant_null_arm_is_not_a_hit(derive):
    """The other half: `directional` must still apply where the mechanism predicts a sign. A null
    arm that is more RESISTANT to the ATR inhibitors is not mechanism support."""
    seq = _models(120)
    resid = {d: {m: float((i * 7) % 11) / 3.0 for i, m in enumerate(seq)}
             for d in ("azd6738", "ve-822", "olaparib", "talazoparib", "paclitaxel", "bortezomib")}
    for m in seq[:25]:
        resid["azd6738"][m] += 4.0
        resid["ve-822"][m] += 4.0
    art = derive(_inputs(damaged=seq[:25], sequenced=seq, cn_models=[]), resid)
    assert art["detected"]["ATM_vs_ATR_inhibitors"] == [], (
        "a null arm more RESISTANT to the ATR inhibitors must not count as a detection")


def test_the_wee1_near_neighbour_is_always_reported_and_enters_no_aggregate(derive):
    """⛔ THE HOLE PART D ALREADY FELL INTO. MK-1775 is neither an ATR inhibitor nor a clean non-DDR
    control, so before part D added a reporting-only group it was fetched, computed, stored and
    invisible to every printed summary."""
    seq = _models(120)
    drugs = ("azd6738", "ve-822", "olaparib", "talazoparib", "paclitaxel", "bortezomib", "mk-1775")
    resid = {d: {m: float((i * 7) % 11) / 3.0 for i, m in enumerate(seq)} for d in drugs}
    for m in seq[:25]:                      # a huge WEE1 effect and nothing else
        resid["mk-1775"][m] -= 6.0
    art = derive(_inputs(damaged=seq[:25], sequenced=seq, cn_models=[]), resid)
    reading = art["instrument_reading"]
    assert "mk-1775" in reading["ATM_vs_near_neighbour_DDR_reporting_only"]
    assert reading["ATM_vs_near_neighbour_DDR_reporting_only"]["mk-1775"]["status"] == "read"
    # it must not have moved any verdict aggregate
    assert art["detected"]["ATM_vs_ATR_inhibitors"] == []
    assert art["detected"]["ATM_vs_non_DDR_controls"] == []
    assert art["verdict"] == "INSTRUMENT_CANNOT_DETECT"


def test_every_drug_in_the_part_d_cache_is_assigned_a_group(derive):
    """A drug that matches no group would be computed and then never printed — the same disclosure
    hole as the WEE1 one, arriving through a release that adds a drug."""
    seq = _models(60)
    drugs = ("azd6738", "ve-822", "olaparib", "talazoparib", "paclitaxel", "bortezomib", "mk-1775")
    resid = {d: {m: float(i % 6) for i, m in enumerate(seq)} for d in drugs}
    art = derive(_inputs(damaged=seq[:20], sequenced=seq, cn_models=[]), resid)
    rows = art["by_gene"]["ATM"]["contrasts"][
        "primary_damaging_mutation_or_deep_deletion"]["by_drug"]
    ungrouped = [d for d, r in rows.items() if r["group"] == "ungrouped"]
    assert not ungrouped, f"these drugs are in no reported group: {ungrouped}"
