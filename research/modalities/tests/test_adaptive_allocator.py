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
    Candidate, allocate, batch_cost, bayes_normal_update, efficacy_promote, futility_kill, plan_jobs,
    prob_top_k,
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


# ---- env-load economics: packing + costing ---------------------------------------------------------------

def test_plan_jobs_batches_shared_env_key():
    promos = [("a", 2), ("b", 2), ("c", 2), ("d", 3)]
    # env key = rung (same-rung units share the container/system)
    jobs = plan_jobs(promos, env_key_fn=lambda cid, r: r, max_batch=8)
    assert len(jobs) == 2                              # rung-2 batch + rung-3 batch
    sizes = sorted(len(items) for _k, items in jobs)
    assert sizes == [1, 3]


def test_plan_jobs_splits_oversized_batches():
    promos = [(f"c{i}", 2) for i in range(10)]
    jobs = plan_jobs(promos, env_key_fn=lambda cid, r: r, max_batch=4)
    assert len(jobs) == 3                              # 4 + 4 + 2
    assert sum(len(items) for _k, items in jobs) == 10


def test_batch_cost_amortizes_env_and_caches_build():
    promos = [("a", 2), ("b", 2), ("c", 2)]
    jobs = plan_jobs(promos, env_key_fn=lambda cid, r: r, max_batch=8)
    built = set()
    cost = batch_cost(jobs, compute_cost_fn=lambda cid, r: 10.0,
                      env_overhead=5.0, build_cost=12.0, built_keys=built)
    # ONE job: env 5 + build 12 (first time) + 3*10 compute = 47
    assert cost == 47.0
    # second call, same system already built -> no rebuild
    cost2 = batch_cost(jobs, compute_cost_fn=lambda cid, r: 10.0,
                       env_overhead=5.0, build_cost=12.0, built_keys=built)
    assert cost2 == 35.0                               # env 5 + 3*10, build skipped


def test_atomic_pays_env_per_unit_batched_pays_once():
    promos = [("a", 2), ("b", 2), ("c", 2), ("d", 2)]
    atomic = plan_jobs(promos, env_key_fn=lambda cid, r: cid, max_batch=1)   # every unit its own env key+job
    batched = plan_jobs(promos, env_key_fn=lambda cid, r: r, max_batch=8)     # one shared job
    cc = lambda cid, r: 10.0  # noqa: E731
    atomic_cost = batch_cost(atomic, cc, env_overhead=5.0, build_cost=12.0, built_keys=set())
    batched_cost = batch_cost(batched, cc, env_overhead=5.0, build_cost=12.0, built_keys=set())
    assert atomic_cost == 4 * (5.0 + 12.0 + 10.0)     # 108: env+build re-paid every unit
    assert batched_cost == 5.0 + 12.0 + 4 * 10.0      # 57: env+build once
    assert batched_cost < atomic_cost


def _simulate_env(policy: str, seed: int, env_overhead=6.0, build_cost=15.0):
    """
    As _simulate but charges realistic per-JOB env overhead + a one-time-per-receptor system build.
    Variants:
      'static'          : successive halving, one job per rung (batched), full top-k at terminal.
      'adaptive_atomic' : adaptive policy but ONE JOB PER PROMOTED UNIT (naive granular) -> env re-paid each.
      'adaptive_batched': adaptive policy + batch each rung-cohort into one job + cached system build.
    Returns (winner_in_final_topk, total_cost).
    """
    rng = random.Random(seed)
    N = 15
    true = {f"c{i}": rng.gauss(0.0, 1.0) for i in range(N)}
    winner = "c0"
    true[winner] = 3.5
    rungs = {1: (1.6, 10.0), 2: (1.1, 30.0), 3: (0.8, 80.0), 4: (0.5, 120.0), 5: (0.25, 500.0)}
    top_k = 3
    cands = [Candidate(cid=c, mu=0.0, sigma=2.0, rung=0) for c in true]
    by_id = {c.cid: c for c in cands}
    built = set()                                        # cached system builds (env key = rung here: one receptor)

    def obs_only(c, rung):
        noise, _cost = rungs[rung]
        c.mu, c.sigma = bayes_normal_update(c.mu, c.sigma, rng.gauss(true[c.cid], noise), noise)
        c.rung = rung

    def charge(promotions, atomic):
        if atomic:
            jobs = plan_jobs(promotions, env_key_fn=lambda cid, r: (cid, r), max_batch=1)
        else:
            jobs = plan_jobs(promotions, env_key_fn=lambda cid, r: r, max_batch=8)
        return batch_cost(jobs, compute_cost_fn=lambda cid, r: rungs[r][1],
                          env_overhead=env_overhead, build_cost=build_cost, built_keys=built)

    total = 0.0
    atomic = (policy == "adaptive_atomic")
    if policy in ("adaptive_atomic", "adaptive_batched"):
        r1 = [(c.cid, 1) for c in cands]
        total += charge(r1, atomic)
        for c in cands:
            obs_only(c, 1)
        for rung in (2, 3, 4):
            alive = [c for c in cands if c.alive and c.rung == rung - 1]
            if not alive:
                continue
            n_slots = max(top_k, math.ceil(len(alive) * 0.55))
            dec = allocate(cands, free_slots=n_slots, top_k=top_k, kill_threshold=0.05, seed=seed * 10 + rung)
            promoted = {cid for cid, _ in dec.promote}
            for c in alive:
                if c.cid not in promoted:
                    c.alive = False
            total += charge(list(dec.promote), atomic)
            for cid, nr in dec.promote:
                obs_only(by_id[cid], nr)
            surv = [c for c in cands if c.alive and c.rung == rung]
            if len(surv) > top_k:
                bar = sorted((c.mu for c in surv), reverse=True)[top_k - 1]
                for c in surv:
                    if futility_kill(c.mu, c.sigma, bar, eps_fut=0.10):
                        c.alive = False
        finalists = sorted((c for c in cands if c.alive and c.rung == 4), key=lambda c: c.mu, reverse=True)
        ran = []
        for c in finalists:
            total += charge([(c.cid, 5)], atomic)
            obs_only(c, 5)
            ran.append(c)
            p1 = prob_top_k([x for x in cands if x.alive], top_k=1, n_mc=1500, seed=seed)
            leader = max(ran, key=lambda x: x.mu)
            if p1.get(leader.cid, 0.0) > 0.90:
                break
    else:  # static: one batched job per rung
        pool = list(cands)
        for rung in (1, 2, 3, 4, 5):
            total += charge([(c.cid, rung) for c in pool], atomic=False)
            for c in pool:
                obs_only(c, rung)
            pool.sort(key=lambda c: c.mu, reverse=True)
            pool = pool[:max(top_k, len(pool) // 2)]

    ranked = sorted((c for c in cands if c.alive), key=lambda c: c.mu, reverse=True)
    return winner in {c.cid for c in ranked[:top_k]}, total


def test_env_aware_batching_beats_atomic_and_static():
    seeds = range(12)
    hits = {"static": 0, "adaptive_atomic": 0, "adaptive_batched": 0}
    cost = {"static": 0.0, "adaptive_atomic": 0.0, "adaptive_batched": 0.0}
    for s in seeds:
        for pol in hits:
            h, c = _simulate_env(pol, s)
            hits[pol] += h
            cost[pol] += c
    n = len(list(seeds))
    for pol in hits:
        print(f"{pol:18s}: {hits[pol]:2d}/{n} hits, ${cost[pol]/n:.0f}/run")
    # batching amortizes env load: strictly cheaper than the naive atomic-granular allocator ...
    assert cost["adaptive_batched"] < cost["adaptive_atomic"]
    # ... and still beats static on cost while recovering the winner at least as well
    assert cost["adaptive_batched"] < cost["static"]
    assert hits["adaptive_batched"] >= hits["static"] - 1
    # and the naive granular allocator's env overhead can erase its compute savings (the whole point)
    assert cost["adaptive_atomic"] > cost["adaptive_batched"]


if __name__ == "__main__":
    for pol in ("static", "adaptive_atomic", "adaptive_batched"):
        hs = [_simulate_env(pol, s) for s in range(12)]
        print(pol, sum(h for h, _ in hs), "/12 hits, $", round(sum(c for _, c in hs) / 12))
