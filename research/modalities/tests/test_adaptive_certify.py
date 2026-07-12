#!/usr/bin/env python3
"""
Certification-layer tests — the adoption gate from the 2026-07-12 methodology review. The centerpiece is a
NO-HIT campaign that repeatedly peeks at streamed replicas and must keep the campaign-wide FALSE-DECLARATION
rate under the pre-declared budget delta_total, proving the anytime-valid machinery controls optional-stopping
+ multiplicity risk.

Pure stdlib. Run: python -m pytest research/modalities/tests/test_adaptive_certify.py
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptive_certify import (  # noqa: E402
    ABSTAIN_ESCALATE, FUTILITY_STOP, GROSS_FAIL, PASS_CANDIDATE, PROMOTE, TECHNICAL_FAIL, TECHNICAL_STOP,
    VALID_FAVORABLE, CertCandidate, MarginEvidence, anytime_lower_bound, anytime_upper_bound,
    campaign_delta_split, certified_champion_race, certify_candidate, classify_result, replicas_independent,
    system_content_hash,
)


# ---- anytime-valid bound ----------------------------------------------------------------------------------

def test_anytime_lower_bound_is_below_mean_and_tightens_with_n():
    lb_small = anytime_lower_bound(1.0, n=3, sigma=1.0, delta=0.05)
    lb_large = anytime_lower_bound(1.0, n=300, sigma=1.0, delta=0.05)
    assert lb_small < 1.0 and lb_large < 1.0
    assert lb_large > lb_small                        # more data -> tighter (higher) lower bound
    assert anytime_upper_bound(1.0, 300, 1.0, 0.05) > 1.0


def test_anytime_bound_coverage_under_repeated_looks():
    """Empirical: P(exists n : true_mean < LB(n)) should stay <= delta across a stream of looks."""
    delta, true_mean, sigma = 0.05, 0.0, 1.0
    violations = 0
    trials = 400
    for s in range(trials):
        rng = random.Random(s)
        run_mean, n = 0.0, 0
        breached = False
        for _ in range(60):                           # 60 sequential looks per trial
            n += 1
            run_mean += (rng.gauss(true_mean, sigma) - run_mean) / n
            if anytime_lower_bound(run_mean, n, sigma, delta) > true_mean:
                breached = True
                break
        violations += breached
    # anytime-valid: violation rate <= delta (CS is conservative, so typically well under)
    assert violations / trials <= delta


# ---- certification cannot be reached from the prior or non-terminal evidence ------------------------------

def test_prior_cannot_enter_pass_predicate():
    # a candidate with a sky-high prior but NO terminal evidence must NOT pass
    c = CertCandidate(cid="x", prior=999.0)
    c.margins = {t: MarginEvidence(target=t) for t in ("NR4A1", "NR4A2")}
    assert certify_candidate(c.margins, bar=0.5, robustness=0.0, delta_candidate=0.025) == PROMOTE


def test_pass_requires_terminal_rung_evidence():
    margins = {t: MarginEvidence(target=t, sigma=0.3) for t in ("NR4A1", "NR4A2")}
    for t in margins:
        for i in range(6):                            # strong, tight evidence — but NOT flagged terminal
            margins[t].update(3.0, seed=i, start_state=i)
    assert certify_candidate(margins, bar=0.5, robustness=0.0, delta_candidate=0.025) == PROMOTE
    for t in margins:                                 # now mark terminal
        margins[t].from_terminal_rung = True
    assert certify_candidate(margins, bar=0.5, robustness=0.0, delta_candidate=0.025) == PASS_CANDIDATE


def test_noncompensatory_strong_margin_cannot_offset_weak():
    # NR4A1 margin excellent, NR4A2 margin at/below the bar -> must NOT pass (no averaging)
    strong = MarginEvidence(target="NR4A1", sigma=0.3, from_terminal_rung=True)
    weak = MarginEvidence(target="NR4A2", sigma=0.3, from_terminal_rung=True)
    for i in range(8):
        strong.update(4.0, seed=i, start_state=i)
        weak.update(0.0, seed=i, start_state=i)       # true margin ~0, bar 0.5
    assert certify_candidate({"NR4A1": strong, "NR4A2": weak}, bar=0.5, robustness=0.0,
                             delta_candidate=0.025) in (PROMOTE, FUTILITY_STOP)


def test_futility_when_upper_bound_below_bar():
    m = MarginEvidence(target="NR4A1", sigma=0.2, from_terminal_rung=True)
    for i in range(12):
        m.update(-2.0, seed=i, start_state=i)         # clearly far below the bar
    assert certify_candidate({"NR4A1": m}, bar=0.5, robustness=0.0, delta_candidate=0.025) == FUTILITY_STOP


def test_robustness_margin_makes_pass_stricter():
    # NOTE: anytime-valid certification is conservative — it needs enough tight independent replicas. With
    # sigma=0.2, n=12, true margin 1.0, the anytime lower bound clears bar 0.5 but NOT bar+0.5.
    margins = {t: MarginEvidence(target=t, sigma=0.2, from_terminal_rung=True) for t in ("NR4A1", "NR4A2")}
    for t in margins:
        for i in range(12):
            margins[t].update(1.0, seed=i, start_state=i)
    assert certify_candidate(margins, bar=0.5, robustness=0.0, delta_candidate=0.025) == PASS_CANDIDATE
    assert certify_candidate(margins, bar=0.5, robustness=0.5, delta_candidate=0.025) == PROMOTE


# ---- replica independence + content-addressed cache -------------------------------------------------------

def test_correlated_replicas_are_discounted():
    m = MarginEvidence(target="NR4A1")
    for i in range(6):                                # 6 replicas but all from ONE parent trajectory
        m.update(3.0, seed=i, start_state=i, parent_traj="P")
    assert m.effective_n() == 1                       # siblings of one parent count once
    assert not replicas_independent(m, need=3)
    m2 = MarginEvidence(target="NR4A1")
    for i in range(3):                                # 3 genuinely independent
        m2.update(3.0, seed=i, start_state=f"s{i}", parent_traj=f"P{i}")
    assert m2.effective_n() == 3 and replicas_independent(m2, need=3)


def test_content_hash_distinguishes_scientific_systems():
    base = {"structure": "8XTT", "ff": "ff19SB", "protonation": "HID", "coords": "c1", "env": "openfe-1.0"}
    same = dict(base)
    diff_prot = dict(base, protonation="HIE")         # scientifically distinct, same software env
    assert system_content_hash(base) == system_content_hash(same)
    assert system_content_hash(base) != system_content_hash(diff_prot)


def test_campaign_delta_split_union_bounds():
    # per-candidate slice; certify_candidate splits this again across margins (no double-count here)
    d = campaign_delta_split(0.05, n_candidates=10)
    assert abs(d - 0.05 / 10) < 1e-12


# ---- state machine: invalidity != candidate failure -------------------------------------------------------

def test_technical_fail_abstains_not_kills():
    c = CertCandidate(cid="x")

    def step(cid):
        return 10.0, {}, TECHNICAL_FAIL, True, {}
    res = certified_champion_race([c], step, budget_gate=100, bar=0.5, delta_total=0.05, max_technical_retries=2)
    # repeated technical failure -> ABSTAIN via TECHNICAL_STOP, NOT a scientific FUTILITY verdict
    assert c.state == TECHNICAL_STOP
    assert res["declared"] is None


def test_gross_fail_is_futility_not_technical():
    c = CertCandidate(cid="x")
    calls = {"n": 0}

    def step(cid):
        calls["n"] += 1
        return 10.0, {}, GROSS_FAIL, True, {}
    certified_champion_race([c], step, budget_gate=100, bar=0.5, delta_total=0.05)
    assert c.state == FUTILITY_STOP


def test_classify_result_taxonomy():
    assert classify_result(True, True, True, 0.9, margin_point=1.0, bar=0.5) == VALID_FAVORABLE
    assert classify_result(True, True, True, 0.9, margin_point=0.1, bar=0.5) == "VALID_UNFAVORABLE"
    assert classify_result(False, True, True, 0.9, margin_point=1.0, bar=0.5) == TECHNICAL_FAIL
    assert classify_result(True, True, True, 0.2, margin_point=1.0, bar=0.5) == GROSS_FAIL  # pocket loss = gross


# ---- THE centerpiece: no-hit campaign controls false declaration under repeated looks ---------------------

def _no_hit_campaign(seed, delta_total=0.05, bar=0.5, bias=0.0):
    """A campaign where NO candidate truly clears the bar; every declaration is FALSE. Streamed replicas are
    peeked at every step (optional stopping); true margins strictly below the bar. `bias` adds a SYSTEMATIC
    error to every observation (unmodeled by the confidence sequence)."""
    rng = random.Random(seed)
    N = 8
    KNOWN_SIGMA = 1.0
    true = {f"c{i}": {t: rng.uniform(bar - 1.2, bar - 0.1) for t in ("NR4A1", "NR4A2")} for i in range(N)}
    cands = [CertCandidate(cid=c, prior=rng.gauss(0, 1)) for c in true]
    for c in cands:                                    # certifying sigma is a KNOWN fixed bound
        c.margins = {t: MarginEvidence(target=t, sigma=KNOWN_SIGMA, sigma_fixed=True) for t in ("NR4A1", "NR4A2")}
    step_rng = random.Random(seed * 7 + 1)
    counter = {"i": 0}

    def step(cid):
        counter["i"] += 1
        obs = {t: step_rng.gauss(true[cid][t] + bias, KNOWN_SIGMA) for t in ("NR4A1", "NR4A2")}
        return 5.0, obs, VALID_FAVORABLE, True, {"seed": counter["i"], "start_state": counter["i"]}
    res = certified_champion_race(cands, step, budget_gate=6000, bar=bar, robustness=0.0,
                                  delta_total=delta_total, min_independent_replicas=3, seed=seed)
    return res["declared"] is not None                 # any declaration here is a FALSE declaration


def test_no_hit_campaign_controls_false_declaration_rate():
    delta_total = 0.05
    trials = 200
    false_decls = sum(_no_hit_campaign(s, delta_total=delta_total) for s in range(trials))
    rate = false_decls / trials
    # rule-of-3: with f false declarations in n trials, ~95% upper bound is (f + ~2)/n
    upper95 = (false_decls + 3) / trials
    print(f"no-hit false declarations: {false_decls}/{trials} (rate {rate:.4f}, ~95% upper {upper95:.4f}); "
          f"pre-declared delta_total={delta_total}")
    assert rate <= delta_total                         # campaign-wide false-declaration controlled


def test_systematic_bias_defeats_the_statistical_control():
    """HONEST failure-mode: the confidence sequence controls VARIANCE + optional-stopping, NOT bias. A shared
    systematic error inflates both margins and drives false declarations WELL ABOVE delta — which is exactly
    why (a) the claim ceiling is 'computationally qualified candidate' not 'selective degrader', and (b) fix 6
    (independent retrospective calibration + orthogonal controls) is mandatory. This test documents the
    vulnerability rather than pretending the allocator handles it."""
    trials = 120
    unbiased = sum(_no_hit_campaign(s, bias=0.0) for s in range(trials)) / trials
    biased = sum(_no_hit_campaign(s, bias=0.9) for s in range(trials)) / trials
    print(f"no-hit false-declaration rate: unbiased={unbiased:.3f}, with +0.9 systematic bias={biased:.3f}")
    assert unbiased <= 0.05                             # statistical control holds under its assumptions
    assert biased > unbiased + 0.10                     # bias breaks it — a limitation, not a bug


def _multi_hit_campaign(seed, bar=0.5, robustness=0.0):
    """Several TRUE bar-clearers exist. The race should declare one of them (a genuine bar-clearer), not a
    non-clearer, and not falsely eliminate all of them."""
    rng = random.Random(seed)
    N, KNOWN_SIGMA = 8, 0.6
    true = {f"c{i}": {t: rng.uniform(bar - 1.0, bar - 0.2) for t in ("NR4A1", "NR4A2")} for i in range(N)}
    hits = {"c0", "c3"}
    for h in hits:                                      # genuine bar-clearers, comfortably above bar+robustness
        true[h] = {t: bar + robustness + 0.8 for t in ("NR4A1", "NR4A2")}
    cands = [CertCandidate(cid=c, prior=rng.gauss(0, 1)) for c in true]
    for c in cands:
        c.margins = {t: MarginEvidence(target=t, sigma=KNOWN_SIGMA, sigma_fixed=True) for t in ("NR4A1", "NR4A2")}
    step_rng = random.Random(seed * 11 + 5)
    counter = {"i": 0}

    def step(cid):
        counter["i"] += 1
        obs = {t: step_rng.gauss(true[cid][t], KNOWN_SIGMA) for t in ("NR4A1", "NR4A2")}
        return 5.0, obs, VALID_FAVORABLE, True, {"seed": counter["i"], "start_state": counter["i"]}
    res = certified_champion_race(cands, step, budget_gate=8000, bar=bar, robustness=robustness,
                                  delta_total=0.05, min_independent_replicas=3, seed=seed)
    d = res["declared"]
    return d, (d in hits) if d is not None else None


def test_multiple_hits_declares_a_genuine_bar_clearer():
    trials = 60
    declared, correct = 0, 0
    for s in range(trials):
        d, ok = _multi_hit_campaign(s)
        if d is not None:
            declared += 1
            correct += ok
    print(f"multi-hit: declared {declared}/{trials}, of which genuine bar-clearers {correct}/{declared}")
    assert declared >= int(0.7 * trials)               # usually resolves to a declaration
    assert correct == declared                          # EVERY declaration is a genuine bar-clearer


def test_permutation_invariance_of_certify():
    def build(order):
        m = {t: MarginEvidence(target=t, sigma=0.2, from_terminal_rung=True) for t in order}
        for t in m:
            for i in range(10):
                m[t].update(1.5, seed=i, start_state=i)
        return m
    v1 = certify_candidate(build(("NR4A1", "NR4A2")), bar=0.5, robustness=0.0, delta_candidate=0.025)
    v2 = certify_candidate(build(("NR4A2", "NR4A1")), bar=0.5, robustness=0.0, delta_candidate=0.025)
    assert v1 == v2 == PASS_CANDIDATE


if __name__ == "__main__":
    print("no-hit false-declaration test:")
    fd = sum(_no_hit_campaign(s) for s in range(200))
    print(f"  {fd}/200 false declarations")
