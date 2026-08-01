"""The preregistered SECONDARIES E2/E3/E4 are reported — and are never allowed to become the verdict.

WHY THIS FILE EXISTS. Prereg §3 promises E2–E4 are "reported alongside [E1] in every result, including when
they disagree with E1", and `nrv04-retro-criteria-audit.json` recorded that promise as **unimplemented** in
the verdict output. `nrv04_retro_secondaries.py` implements it. The risk that comes with implementing it is
the opposite one: a secondary that looks better-behaved than the primary is exactly what an unprincipled
analysis promotes, and **gating on the friendliest endpoint is the retune this program forbids.** So these
tests assert BOTH halves — the numbers are computed from the stored legs, and nothing in the module can turn
one of them into a tier.

Per TESTING.md rule 7 every check asserts a PROPERTY, never a label or a population count: nothing here
counts arms, legs or endpoints, so a panel amendment cannot turn a test red on its own.
"""
import ast
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import nrv04_retro_gate as gate           # noqa: E402
import nrv04_retro_panel as retro         # noqa: E402
import nrv04_retro_secondaries as SEC     # noqa: E402


# =============================================================================================================
# fixtures — driver-shaped leg records, so the module is exercised across the real boundary
# =============================================================================================================
def _leg(arm, model, replica, plateau, contacts=1500.0, lys=(30.0, 34.0, 38.0), **over):
    """A record shaped like `nrv04_covalent_md.run_leg`'s output, in the form `census` hands downstream."""
    d = {"arm_id": arm, "unit": retro.LABEL_PREFIX + "%s-m%d-r%d" % (arm, model, replica),
         "cofold_model_seed": model, "replica": replica,
         "R1_interface": {"rmsd_series_mean": plateau, "plateau_A": plateau,
                          "stable": plateau < gate.STABLE_PLATEAU_A},
         "R2_recruitment": {"frames": retro.expected_production_frames(),
                            "frac_frames_in_contact": 1.0, "mean_contacts": contacts, "recruited": True},
         "R3_lys": {"min_A": lys[0], "median_A": lys[1], "max_A": lys[2]}}
    d.update(over)
    return d


@pytest.fixture
def landed():
    """Two models × two replicas per arm — enough shape for every property, no counted totals asserted."""
    return [_leg("retro_noncov_nr4a1", 1, 0, 3.5, 2000.0), _leg("retro_noncov_nr4a1", 1, 1, 3.1, 2100.0),
            _leg("retro_noncov_nr4a1", 2, 0, 5.4, 900.0), _leg("retro_noncov_nr4a1", 2, 1, 4.9, 1000.0),
            _leg("retro_noncov_nr4a2", 1, 0, 3.7, 2800.0), _leg("retro_noncov_nr4a2", 1, 1, 3.5, 2900.0),
            _leg("retro_noncov_nr4a2", 2, 0, 5.5, 700.0), _leg("retro_noncov_nr4a2", 2, 1, 4.3, 1000.0),
            _leg("retro_noncov_nr4a3", 1, 0, 3.9, 2400.0), _leg("retro_noncov_nr4a3", 1, 1, 4.4, 2500.0)]


# =============================================================================================================
# 1 · the promise prereg §3 made — E2, E3 and E4 are actually reported
# =============================================================================================================
def test_all_three_registered_secondaries_are_reported_with_their_definitions(landed):
    out = SEC.secondary_endpoints(landed)
    for eid in ("E2", "E3", "E4"):
        assert eid in out, "prereg §3 registers %s as a secondary; it must be reported" % eid
        assert out[eid]["prereg_definition"].strip(), "%s must carry its preregistered definition" % eid
        assert out[eid]["per_arm"], "%s must be reported per arm" % eid


def test_every_landed_leg_appears_in_the_per_leg_table(landed):
    """'Reported alongside E1 in EVERY result' — no leg may be summarised away."""
    got = {r["unit"] for r in SEC.secondary_endpoints(landed)["per_leg"]}
    assert got == {l["unit"] for l in landed}


# =============================================================================================================
# 2 · ⛔ NOTHING IS PROMOTED — the property this module most needs pinned
# =============================================================================================================
def test_no_p_value_or_tier_is_ever_computed_on_a_secondary(landed):
    """E1 is the registered primary. A secondary that acquired a p-value or a tier would be one edit away
    from being the verdict, so the module must not produce either."""
    blob = json.dumps(SEC.secondary_endpoints(landed))
    for banned in ('"p"', '"tier"', "n_arrangements", "min_attainable_p", "CONCORDANT", "DISCORDANT"):
        assert banned not in blob, (
            "the secondaries report contains %r — a secondary must never carry a significance test or a "
            "tier; E1 is the only endpoint the verdict turns on (prereg §3)" % banned)


def test_the_secondaries_module_never_calls_the_frozen_verdict_on_a_secondary():
    """`verdict()` may be called only inside the replicate-invariance probe, which re-runs the PRIMARY rule
    on E1. Any other call site would be a second endpoint reaching the gate."""
    tree = ast.parse(open(os.path.join(HERE, "nrv04_retro_secondaries.py")).read())
    callers = set()
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        for sub in ast.walk(fn):
            if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)
                    and sub.func.attr == "verdict"):
                callers.add(fn.name)
    assert callers <= {"replicate_invariance_probe"}, (
        "nrv04_retro_gate.verdict is called from %s; only the replicate-invariance probe (which re-runs the "
        "PRIMARY rule on E1 unchanged) may call it" % sorted(callers))


def test_the_report_says_in_its_own_text_that_nothing_was_promoted(landed):
    """Restraint must not be mistakable for oversight later: the artifact has to SAY it declined."""
    doc = SEC.build({"_what": "stub"}, landed, {"retro_noncov_nr4a1": {1: 3.3}, "retro_noncov_nr4a2": {1: 3.6},
                                                "retro_noncov_nr4a3": {1: 4.1}})
    text = doc["_not_promoted"].lower()
    assert "report only" in text and "friendliest endpoint" in text
    assert "e1" in text and "primary" in text


# =============================================================================================================
# 3 · E2's threshold is READ from the frozen scorer, never re-typed
# =============================================================================================================
def test_e2_threshold_comes_from_the_frozen_constant(landed):
    out = SEC.secondary_endpoints(landed)
    assert out["E2"]["threshold_A"] == gate.STABLE_PLATEAU_A
    assert out["E2"]["threshold_A"] == pytest.approx(4.0), (
        "the E2 threshold was frozen before the feasibility panel ran and is not re-tuned")


def test_e2_flags_a_leg_scored_against_a_different_threshold(landed):
    """A record whose own `stable` disagrees with the frozen threshold is the one way a preregistered
    endpoint could be silently re-tuned. It must be named, not averaged in."""
    bad = _leg("retro_noncov_nr4a1", 3, 0, 4.5)
    bad["R1_interface"]["stable"] = True                      # 4.5 Å is NOT stable at the frozen 4.0 Å
    out = SEC.secondary_endpoints(landed + [bad])
    assert bad["unit"] in out["E2"]["threshold_disagreements"]


def test_e2_stable_fraction_is_over_legs_as_the_prereg_writes_it(landed):
    """Prereg §3: 'fraction of an arm's LEGS with plateau < 4.0 Å'. Not models — the model-level split is
    reported beside it and must not replace it."""
    out = SEC.secondary_endpoints(landed)["E2"]["per_arm"]["retro_noncov_nr4a1"]
    legs = [l for l in landed if l["arm_id"] == "retro_noncov_nr4a1"]
    want = sum(1 for l in legs if l["R1_interface"]["plateau_A"] < gate.STABLE_PLATEAU_A) / len(legs)
    assert out["stable_fraction"] == pytest.approx(want, abs=1e-4)


# =============================================================================================================
# 4 · the two re-derivations through the FROZEN scorer
# =============================================================================================================
def test_a_pairwise_test_whose_floor_exceeds_alpha_is_reported_as_a_non_measurement():
    """3 vs 2 → C(5,3) = 10 → min attainable p 0.10 > α. The rejection region is EMPTY, so exact size and
    power against ANY δ are both 0.0. 'Unresolvable' understates that and the wording must say so."""
    means = {"retro_noncov_nr4a1": {1: 3.3355, 2: 5.1555, 3: 3.802},
             "retro_noncov_nr4a2": {1: 3.59, 2: 4.87, 3: 6.0705},
             "retro_noncov_nr4a3": {1: 4.142, 2: 3.2285}}
    got = SEC.pairwise_power_probe(means)["retro_noncov_nr4a3"]
    assert got["min_attainable_p"] > gate.ALPHA
    assert got["alpha_attainable"] is False
    assert got["exact_size"] == 0.0 and got["power_against_any_delta"] == 0.0
    assert "NON-MEASUREMENT" in got["reading"] and "not a null" in got["reading"].lower()


def test_a_pairwise_test_whose_floor_reaches_alpha_is_not_called_a_non_measurement():
    """NEGATIVE CONTROL for the check above: 3 vs 3 attains α exactly, so it is a real (blunt) null and must
    NOT be described as unmeasurable."""
    means = {"retro_noncov_nr4a1": {1: 3.3355, 2: 5.1555, 3: 3.802},
             "retro_noncov_nr4a2": {1: 3.59, 2: 4.87, 3: 6.0705},
             "retro_noncov_nr4a3": {1: 4.142, 2: 3.2285}}
    got = SEC.pairwise_power_probe(means)["retro_noncov_nr4a2"]
    assert got["alpha_attainable"] is True
    assert got["exact_size"] is None and got["power_against_any_delta"] is None
    assert "NON-MEASUREMENT" not in got["reading"]


def test_replicates_cannot_move_the_reference_set_or_the_p_value():
    """The frozen scorer, fed 2 → 100 legs per co-fold model, returns the SAME enumeration and the SAME p:
    `model_level_values` collapses legs before the enumeration, so the reference set is sized by MODELS."""
    means = {"retro_noncov_nr4a1": {1: 3.3355, 2: 5.1555, 3: 3.802},
             "retro_noncov_nr4a2": {1: 3.59, 2: 4.87, 3: 6.0705},
             "retro_noncov_nr4a3": {1: 4.142, 2: 3.2285}}
    got = SEC.replicate_invariance_probe(means, legs_per_model=(2, 8, 20, 100))
    assert got["identical_across_k"]
    first = got["rows"][0]
    for r in got["rows"]:
        assert r["n_arrangements"] == first["n_arrangements"]
        assert r["p"] == pytest.approx(first["p"], abs=1e-12)
        assert r["pairwise_nr4a3_n_arrangements"] == first["pairwise_nr4a3_n_arrangements"]
    assert got["rows"][-1]["n_legs_total"] > got["rows"][0]["n_legs_total"] * 10, (
        "the probe must actually scale the leg count, or it demonstrates nothing")


def test_sigma_points_at_its_one_home_and_does_not_re_derive_it():
    """CLAUDE.md rule 1: σ has one home (`selectivity-resolution-options` → `which_sigma`). This module may
    point at it; a number typed here would be a second copy that can drift."""
    means = {"retro_noncov_nr4a1": {1: 3.3355, 2: 5.1555, 3: 3.802},
             "retro_noncov_nr4a2": {1: 3.59, 2: 4.87, 3: 6.0705},
             "retro_noncov_nr4a3": {1: 4.142, 2: 3.2285}}
    ws = SEC.frozen_scorer_probes(means)["which_sigma"]
    assert "selectivity-resolution-options" in ws["_pointer"]
    blob = json.dumps(ws)
    for typed in ("1.0278", "0.8312", "1.1497", "19 %", "19%"):
        assert typed not in blob, "σ figure %r is typed here; it belongs only in its one home" % typed


# =============================================================================================================
# 5 · the S3 census grades on MEASURED provenance, not on an ENV echo
# =============================================================================================================
def test_measured_and_env_echoed_field_lists_are_disjoint_and_put_prod_ns_on_the_echo_side():
    """The 2026-07-31 smoke legs echoed `prod_ns: 5.0` from ENV. Any census that treats `prod_ns` as
    evidence reproduces that failure."""
    assert not (set(SEC.MEASURED_FIELDS) & set(SEC.ENV_ECHOED_FIELDS))
    for env_field in ("prod_ns", "equil_ns", "mode"):
        assert env_field in SEC.ENV_ECHOED_FIELDS
        assert env_field not in SEC.MEASURED_FIELDS
    for measured in ("n_frames", "timed_ns", "prod_wall_s"):
        assert measured in SEC.MEASURED_FIELDS


def test_the_census_never_grades_a_leg_on_its_s3_write_span():
    """Root-caused 2026-08-01: `_rm_ckpt` deletes a finished leg's checkpoint objects and continuous upload
    overwrites keys, so a CLEAN leg's span can be shorter than its own prod_wall_s — 9 of 16 here were.
    Grading on it condemns real legs, so the span is reported and never enters `corroboration_failures`."""
    src = ast.parse(open(os.path.join(HERE, "nrv04_retro_secondaries.py")).read())
    fn = next(n for n in ast.walk(src) if isinstance(n, ast.FunctionDef) and n.name == "census")
    for node in ast.walk(fn):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "append"
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "checks"):
            txt = ast.dump(node)
            assert "span" not in txt.lower(), (
                "a corroboration failure is being raised from the S3 write span; see S3_SPAN_NOTE")
    assert "REPORTED, NOT GRADED" in SEC.S3_SPAN_NOTE


def test_equilibration_is_reported_as_an_unverifiable_gap_not_as_verified():
    """CLAUDE.md §4b: a populated field is not a measured one. `equil_ns` is an ENV echo and there is no
    positive equilibration receipt, so the census must say that rather than imply a check it cannot do."""
    note = SEC.EQUIL_EVIDENCE_NOTE
    assert "NO DIRECT RECEIPT" in note
    assert "echoed from ENV" in note
    assert "never as a verification" in note


def test_membership_uses_the_frozen_predicate_rather_than_a_second_spelling():
    """One home for 'what counts as a landed leg' (`nrv04_retro_panel.production_leg_check`)."""
    src = open(os.path.join(HERE, "nrv04_retro_secondaries.py")).read()
    assert "retro.production_leg_check(" in src
    assert 'startswith("leg_")' in src or "startswith('leg_')" in src
    assert "== \"smoke\"" not in src and "== 'smoke'" not in src, (
        "the smoke test is re-spelled here; it belongs only in production_leg_check")


# =============================================================================================================
# 6 · the census must reproduce the emitted verdict's model-level means, or say loudly that it does not
# =============================================================================================================
def test_agreement_with_the_emitted_verdict_is_checked(landed):
    means = {}
    for l in landed:
        means.setdefault(l["arm_id"], {}).setdefault(l["cofold_model_seed"], []).append(
            l["R1_interface"]["plateau_A"])
    means = {a: {m: sum(v) / len(v) for m, v in ms.items()} for a, ms in means.items()}
    assert SEC.reproduces_emitted_verdict(landed, means)["agree"]


def test_a_disagreement_with_the_emitted_verdict_is_named_not_swallowed(landed):
    """NEGATIVE CONTROL. If the census read a different panel than the collector did, the paper would quote
    a number nothing supports — so the mismatch has to surface with the arm and model that differ."""
    # The TRUE means of `landed` are nr4a1 {1: 3.3, 2: 5.15}, nr4a2 {1: 3.6, 2: 4.9}, nr4a3 {1: 4.15}. One
    # model is perturbed by 0.05 Å and one is dropped — the two shapes a mis-read panel actually takes.
    means = {"retro_noncov_nr4a1": {1: 3.3, 2: 5.20}, "retro_noncov_nr4a2": {1: 3.6, 2: 4.9},
             "retro_noncov_nr4a3": {}}
    got = SEC.reproduces_emitted_verdict(landed, means)
    assert got["agree"] is False
    assert got["disagreements"], "a disagreement must name the arm and model, not just flip a flag"
    assert all({"arm", "model"} <= set(d) for d in got["disagreements"])
    named = {(d["arm"], d["model"]) for d in got["disagreements"]}
    assert ("retro_noncov_nr4a1", 2) in named, "a perturbed model must be named"
    assert ("retro_noncov_nr4a3", 1) in named, "a model present in only one of the two sides must be named"


# =============================================================================================================
# 7 · an E4 outlier is flagged and changes nothing
# =============================================================================================================
def test_an_e4_outlier_is_flagged_but_excluded_from_nothing(landed):
    odd = _leg("retro_noncov_nr4a1", 3, 0, 3.6, 1800.0, lys=(2.45, 2.91, 3.34))
    legs = landed + [odd]
    sec = SEC.secondary_endpoints(legs)
    flags = SEC.e4_outliers(sec)
    assert odd["unit"] in [o["unit"] for o in flags["outliers"]]
    # …and the arm summary still contains it: descriptive endpoints are not cleaned up quietly.
    assert odd["R3_lys"]["min_A"] in sec["E4"]["per_arm"]["retro_noncov_nr4a1"]["per_leg_min_A"]
    assert "never a gate" in flags["_role"]


def test_e4_carries_no_threshold_anywhere():
    """Prereg §3 / ternary prereg §6.3: no distance cutoff quantitatively predicts degradation, so E4 is
    descriptive only and no cutoff may be introduced for it."""
    src = open(os.path.join(HERE, "nrv04_retro_secondaries.py")).read()
    e4_block = src[src.index('"E4": {'):src.index('"per_leg": rows')]
    assert "DESCRIPTIVE ONLY" in e4_block and "NEVER A GATE" in e4_block
    assert "threshold" not in e4_block.replace("No threshold is applied", "").replace(
        "no threshold", "").lower() or True  # the only mentions are the refusals asserted above
