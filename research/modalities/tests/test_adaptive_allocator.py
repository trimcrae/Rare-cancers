#!/usr/bin/env python3
"""
Tests for the adaptive multi-fidelity allocator, incl. a synthetic-screen simulation that must (a) recover a
hidden selective winner in the top-k and (b) spend less than static successive-halving to do it.

Pure stdlib. Run: python -m pytest research/modalities/tests/test_adaptive_allocator.py
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptive_allocator import (  # noqa: E402
    Candidate, allocate, bayes_normal_update, efficacy_promote, futility_kill, prob_top_k,
)


# ---- unit tests: pure functions --------------------------------------------------------------------------

def test_bayes_update_moves_toward_obs_and_shrinks_sigma():
    mu, sig = bayes_normal_update(0.0, 1.0, obs=2.0, obs_sigma=1.0)
    assert 0.9 < mu < 1.1                       # equal-precision -> midpoint
    assert sig < 1.0                            # uncertainty shrinks


def test_bayes_update_precise_obs_dominates():
    mu, sig = bayes_normal_update(0.0, 1.0, obs=5.0, obs_sigma=0.01)
    assert mu > 4.9 and sig < 0.05


def test_futility_kills_hopeless_candidate():
    # far below the bar, tight posterior -> futile
    assert futility_kill(mu=-2.0, sigma=0.3, promotion_bar=0.0, eps_fut=0.05) is True
    # right at the bar with wide posterior -> not futile
    assert futility_kill(mu=0.0, sigma=1.0, promotion_bar=0.0, eps_fut=0.05) is False


def test_efficacy_promotes_clear_winner_early():
    assert efficacy_promote(mu=3.0, sigma=0.3, promotion_bar=0.0, eps_eff=0.05) is True
    assert efficacy_promote(mu=0.0, sigma=1.0, promotion_bar=0.0, eps_eff=0.05) is False


def test_prob_top_k_ranks_by_posterior():
    cands = [Candidate(cid=f"c{i}", mu=float(i), sigma=0.3) for i in range(5)]
    p = prob_top_k(cands, top_k=2, n_mc=4000, seed=1)
    # the two highest-mu candidates should own almost all the top-2 mass
    assert p["c4"] > 0.9 and p["c3"] > 0.7
    assert p["c0"] < 0.05


def test_prob_top_k_all_alive_when_fewer_than_k():
    cands = [Candidate(cid="a", mu=1.0), Candidate(cid="b", mu=0.0)]
    p = prob_top_k(cands, top_k=3)
    assert p == {"a": 1.0, "b": 1.0}


# ---- allocator behavior ----------------------------------------------------------------------------------

def test_validity_fail_is_killed_unconditionally():
    cands = [Candidate(cid="good", mu=2.0, sigma=0.3, valid=True),
             Candidate(cid="bad", mu=5.0, sigma=0.3, valid=False)]  # high promise but invalid
    dec = allocate(cands, free_slots=2, top_k=1)
    assert "bad" in dec.kill                      # invalid killed despite highest mu
    assert any(cid == "good" for cid, _ in dec.promote)


def test_low_promise_candidate_killed():
    cands = [Candidate(cid="win", mu=5.0, sigma=0.2)]
    cands += [Candidate(cid=f"lose{i}", mu=-3.0, sigma=0.2) for i in range(4)]
    dec = allocate(cands, free_slots=1, top_k=1, kill_threshold=0.05)
    assert set(dec.kill) >= {f"lose{i}" for i in range(4)}


def test_terminal_rung_candidates_are_held_not_promoted():
    cands = [Candidate(cid="fin", mu=3.0, sigma=0.2, rung=5)]
    dec = allocate(cands, free_slots=2, top_k=1, max_rung=5)
    assert "fin" in dec.hold and not dec.promote


def test_exploration_reserve_funds_uncertain_longshot_at_cheap_rung():
    # one clear leader + one uncertain long-shot; at rung 0->1 rho is high, so the long-shot gets a slot
    cands = [Candidate(cid="leader", mu=2.0, sigma=0.1, rung=0)]
    cands += [Candidate(cid="longshot", mu=0.5, sigma=2.5, rung=0)]
    cands += [Candidate(cid=f"mid{i}", mu=0.4, sigma=0.2, rung=0) for i in range(3)]
    dec = allocate(cands, free_slots=2, top_k=1, kill_threshold=0.0,
                   rho_schedule={1: 0.5}, seed=3)
    promoted = {cid for cid, _ in dec.promote}
    assert "leader" in promoted            # exploitation slot
    assert "longshot" in promoted          # exploration slot (highest sigma), not a low-sigma mid


# ---- end-to-end synthetic screen -------------------------------------------------------------------------

def _simulate(policy: str, seed: int):
    """
    N candidates, one hidden selective winner. Each rung yields a noisier-at-cheap-rungs observation of the
    true score; posteriors update Bayesian. 'static' = fixed top-half successive halving that runs the full
    top-k at the terminal rung. 'adaptive' = allocator-driven promotion + sequential futility kills before
    each expensive rung + terminal early-stop (run finalists at the $500 rung only until the leader is
    decisive). Returns (winner_in_final_topk, total_cost).
    """
    rng = random.Random(seed)
    N = 15
    true = {f"c{i}": rng.gauss(0.0, 1.0) for i in range(N)}
    winner = "c0"
    true[winner] = 3.5                                   # one clear selective hit
    # rung -> (obs_noise, cost per candidate). Cheap rungs are noisy; expensive rungs precise.
    rungs = {1: (1.6, 10.0), 2: (1.1, 30.0), 3: (0.8, 80.0), 4: (0.5, 120.0), 5: (0.25, 500.0)}
    top_k = 3

    cands = [Candidate(cid=c, mu=0.0, sigma=2.0, rung=0) for c in true]
    by_id = {c.cid: c for c in cands}

    def observe(c, rung):
        noise, cost = rungs[rung]
        obs = rng.gauss(true[c.cid], noise)
        c.mu, c.sigma = bayes_normal_update(c.mu, c.sigma, obs, noise)
        c.rung = rung
        c.spent += cost
        return cost

    total_cost = 0.0
    if policy == "adaptive":
        for c in cands:                                  # R1 floor for all
            total_cost += observe(c, 1)
        # R2..R4: allocator picks a halving-sized survivor set; futility prunes before the next rung.
        for rung in (2, 3, 4):
            alive = [c for c in cands if c.alive and c.rung == rung - 1]
            if not alive:
                continue
            n_slots = max(top_k, math.ceil(len(alive) * 0.55))   # halving discipline
            dec = allocate(cands, free_slots=n_slots, top_k=top_k, kill_threshold=0.05, seed=seed * 10 + rung)
            promoted_ids = {cid for cid, _ in dec.promote}
            for c in alive:                              # not promoted => killed (halving cut)
                if c.cid not in promoted_ids:
                    c.alive = False
            for cid, nr in dec.promote:
                total_cost += observe(by_id[cid], nr)
            # sequential futility: drop survivors that now can't clear the rung-k promotion bar
            surv = [c for c in cands if c.alive and c.rung == rung]
            if len(surv) > top_k:
                bar = sorted((c.mu for c in surv), reverse=True)[top_k - 1]
                for c in surv:
                    if futility_kill(c.mu, c.sigma, promotion_bar=bar, eps_fut=0.10):
                        c.alive = False
        # Terminal rung with EARLY-STOP: run finalists in promise order; stop once the leader owns the top-1.
        finalists = sorted((c for c in cands if c.alive and c.rung == 4), key=lambda c: c.mu, reverse=True)
        ran = []
        for c in finalists:
            total_cost += observe(c, 5)
            ran.append(c)
            if len(ran) >= 1:
                p1 = prob_top_k([x for x in cands if x.alive], top_k=1, n_mc=1500, seed=seed)
                leader = max(ran, key=lambda x: x.mu)
                if p1.get(leader.cid, 0.0) > 0.90:       # decisive winner -> stop paying for the rest
                    break
    else:  # static successive halving: keep top-half by posterior mean, run the full top-k at the terminal
        pool = list(cands)
        for rung in (1, 2, 3, 4, 5):
            for c in pool:
                total_cost += observe(c, rung)
            pool.sort(key=lambda c: c.mu, reverse=True)
            keep = max(top_k, len(pool) // 2)
            pool = pool[:keep]

    ranked = sorted((c for c in cands if c.alive), key=lambda c: c.mu, reverse=True)
    final_topk = {c.cid for c in ranked[:top_k]}
    return winner in final_topk, total_cost


def test_synthetic_adaptive_recovers_winner_and_costs_less_than_static():
    seeds = range(12)
    adaptive_hits, static_hits = 0, 0
    adaptive_cost, static_cost = 0.0, 0.0
    for s in seeds:
        a_hit, a_cost = _simulate("adaptive", s)
        st_hit, st_cost = _simulate("static", s)
        adaptive_hits += a_hit
        static_hits += st_hit
        adaptive_cost += a_cost
        static_cost += st_cost
    n = len(list(seeds))
    # (a) adaptive recovers the winner at least as reliably as static, and reliably in absolute terms
    assert adaptive_hits >= static_hits - 1
    assert adaptive_hits >= int(0.75 * n)
    # (b) adaptive spends materially less on average
    assert adaptive_cost < static_cost
    print(f"adaptive: {adaptive_hits}/{n} hits, ${adaptive_cost/n:.0f}/run | "
          f"static: {static_hits}/{n} hits, ${static_cost/n:.0f}/run")


if __name__ == "__main__":
    ok, cost = _simulate("adaptive", 0)
    print("adaptive recovered winner:", ok, "cost", cost)
