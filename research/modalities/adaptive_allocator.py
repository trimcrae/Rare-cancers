#!/usr/bin/env python3
"""
Adaptive multi-fidelity compute ALLOCATOR (scheduling) for the NR4A3 selective-degrader screen.

Formalism (corrected per the 2026-07-12 methodology review):
  * Full-fleet mode  = constrained, multi-fidelity, FIXED-CONFIDENCE BEST-ARM IDENTIFICATION.
  * Champion modes   = FIXED-CONFIDENCE GOOD-ARM IDENTIFICATION WITH ABSTENTION (return the first arm PROVEN to
                       exceed a threshold; abstain/escalate otherwise) — NOT "satisficing BAI".
  * NOT regret-minimizing MAB: computational "pulls" yield information, not recurring reward.

**ALLOCATION vs CERTIFICATION ARE SEPARATE (hard rule).** Everything in THIS module only *schedules* the next
computation (Thompson sampling, confirmation-lock, futility, promotion). It must NOT decide whether a candidate
PASSES. The PASS decision lives solely in `adaptive_certify.py` (anytime-valid bounds, noncompensatory vector
of per-paralogue margins, pre-declared campaign-wide error budget, terminal-rung evidence only). Top-two
Thompson is an *allocator*, not a certifier; its guarantees assume a well-specified model and do NOT transfer
to heterogeneous, biased fidelity rungs — so it may choose what to run, never what to declare.

`run_champion_race` / `interruptible_champion_race` below are the SCHEDULING demonstrations; their internal
"declare on P(clears bar)" shortcut is retained only for the scheduling/behavior unit tests and MUST NOT be
used to certify a candidate. The certification-integrated driver is `adaptive_certify.certified_champion_race`.

Pure stdlib (random, math) — matches the repo's CPU convention; runs anywhere.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


# ---- normal-distribution helpers (stdlib only) ------------------------------------------------------------

def _normal_cdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    if sigma <= 0:
        return 1.0 if x >= mu else 0.0
    return 0.5 * (1.0 + math.erf((x - mu) / (sigma * math.sqrt(2.0))))


def bayes_normal_update(mu0: float, sigma0: float, obs: float, obs_sigma: float) -> tuple[float, float]:
    """Conjugate normal-normal posterior update for one observation."""
    if obs_sigma <= 0:
        return obs, 1e-6
    p0 = 1.0 / (sigma0 * sigma0)
    pobs = 1.0 / (obs_sigma * obs_sigma)
    post_var = 1.0 / (p0 + pobs)
    post_mu = post_var * (p0 * mu0 + pobs * obs)
    return post_mu, math.sqrt(post_var)


# ---- candidate state --------------------------------------------------------------------------------------

@dataclass
class Candidate:
    cid: str
    rung: int = 0
    alive: bool = True
    mu: float = 0.0            # posterior mean of the selective-hit score (higher = more promising)
    sigma: float = 1.0         # posterior sd (uncertainty)
    spent: float = 0.0         # realized spot-$ so far
    valid: bool = True         # convergence gate (hysteresis/overlap/cycle/pocket). False => killed regardless.
    history: list = field(default_factory=list)


@dataclass
class Decision:
    promote: list = field(default_factory=list)   # [(cid, next_rung)]
    kill: list = field(default_factory=list)       # [cid]
    hold: list = field(default_factory=list)       # [cid]


# ---- exploitation signal: P(i in top-k) via Monte-Carlo ---------------------------------------------------

def prob_top_k(cands: list[Candidate], top_k: int, n_mc: int = 2000, seed: int = 0) -> dict[str, float]:
    """Top-two Thompson style: probability each candidate is among the top-k by sampled score."""
    alive = [c for c in cands if c.alive and c.valid]
    if not alive:
        return {}
    if len(alive) <= top_k:
        return {c.cid: 1.0 for c in alive}
    rng = random.Random(seed)
    counts = {c.cid: 0 for c in alive}
    for _ in range(n_mc):
        draws = [(c.cid, rng.gauss(c.mu, max(c.sigma, 1e-9))) for c in alive]
        draws.sort(key=lambda t: t[1], reverse=True)
        for cid, _s in draws[:top_k]:
            counts[cid] += 1
    return {cid: counts[cid] / n_mc for cid in counts}


# ---- sequential within-rung futility / efficacy -----------------------------------------------------------

def futility_kill(mu: float, sigma: float, promotion_bar: float, eps_fut: float = 0.05) -> bool:
    """True => stop the remaining replicas: P(true score >= bar) is below the futility threshold."""
    p_pass = 1.0 - _normal_cdf(promotion_bar, mu, sigma)
    return p_pass < eps_fut


def efficacy_promote(mu: float, sigma: float, promotion_bar: float, eps_eff: float = 0.05) -> bool:
    """True => promote early: P(true score >= bar) is already near-certain."""
    p_pass = 1.0 - _normal_cdf(promotion_bar, mu, sigma)
    return p_pass > (1.0 - eps_eff)


# ---- the allocator ----------------------------------------------------------------------------------------

DEFAULT_RHO_SCHEDULE = {1: 0.5, 2: 0.33, 3: 0.2, 4: 0.1, 5: 0.0}  # exploration reserve by rung


# ---- env-load / job-packing economics ---------------------------------------------------------------------
# Every SageMaker job pays a FIXED overhead before productive compute: container pull + conda/import
# activation + S3 staging (env_overhead), plus a one-time-per-shared-system build cost (build_cost) that is
# cacheable and reused across every unit sharing that system. A naive "one job per (candidate, rung, replica)"
# allocator re-pays env_overhead on every unit and rebuilds the system every time — so finer granularity is
# silently penalized. plan_jobs() amortizes env_overhead by batching units that share an env key into one
# job; batch_cost() charges build_cost only for env keys not already cached.

def plan_jobs(promotions, env_key_fn, max_batch=8):
    """
    Pack promotions [(cid, rung), ...] into jobs, one job per (env_key, batch-of-<=max_batch). Units sharing
    an env key (e.g. same rung + same receptor/system) ride ONE container/conda load. Returns
    [ (env_key, [(cid,rung), ...]) , ... ].
    """
    groups: dict = {}
    for cid, rung in promotions:
        groups.setdefault(env_key_fn(cid, rung), []).append((cid, rung))
    jobs = []
    for key, items in groups.items():
        for i in range(0, len(items), max_batch):
            jobs.append((key, items[i:i + max_batch]))
    return jobs


# ---- cheap-first champion mode (satisficing: cheapest path to ANY bar-clearing candidate) -----------------
# Objective shift: not "find THE best of N" (expensive best-arm ID) but "find A candidate that clears the
# selectivity bar, as cheaply as possible; if the top-ranked one clears it, touch nothing else." Uses a
# near-free CPU prior only to ORDER a depth-first champion race; the PASS decision must be made on the
# trustworthy readout inside confirm_fn, never on the cheap prior.

def seed_prior(cands, prior_scores, prior_sigma=1.5):
    """Seed posterior means from a CHEAP prior (docking/MM-GBSA/co-fold triage). sigma stays WIDE because the
    prior is only weakly predictive of terminal selectivity — it buys ordering, not belief."""
    for c in cands:
        if c.cid in prior_scores:
            c.mu = prior_scores[c.cid]
            c.sigma = prior_sigma


def champion_order(cands, key=None):
    """Prior-best-first ordering of alive candidates (the depth-first race order)."""
    key = key or (lambda c: c.mu)
    return [c.cid for c in sorted((c for c in cands if c.alive), key=key, reverse=True)]


def run_champion_race(order, confirm_fn, budget_gate):
    """
    SCHEDULING DEMO — NOT a certifier (its pass shortcut must not declare a real candidate; use
    adaptive_certify.certified_champion_race). Depth-first good-arm search under a HARD budget gate.
    Walk candidates in prior order; confirm_fn(cid,
    remaining_budget) runs that ONE candidate's cheap-first confirm path (internally staged + mini-gated) and
    returns (cost, passes, valid). STOP + DECLARE at the first valid candidate that clears the bar — later
    candidates are never touched. STOP + ESCALATE (come-ask) if cumulative spend reaches budget_gate with no
    pass. Returns {declared, spent, touched, escalate}.
    """
    spent, touched = 0.0, []
    for cid in order:
        cost, passes, valid = confirm_fn(cid, budget_gate - spent)
        spent += cost
        touched.append(cid)
        if valid and passes:
            return {"declared": cid, "spent": round(spent, 2), "touched": touched, "escalate": False}
        if spent >= budget_gate:
            return {"declared": None, "spent": round(spent, 2), "touched": touched, "escalate": True}
    return {"declared": None, "spent": round(spent, 2), "touched": touched, "escalate": True}


def prob_clears(mu, sigma, bar):
    """Posterior probability the true score clears the selectivity bar."""
    return 1.0 - _normal_cdf(bar, mu, sigma)


def interruptible_champion_race(cands, step_fn, budget_gate, bar, switch_margin=0.0,
                                declare_conf=0.90, kill_conf=0.05, max_steps=2000, seed=0,
                                lock_conf=0.50, release_conf=0.30):
    """
    SCHEDULING DEMO — NOT a certifier (the "declare on P(clears bar)" step is a scheduling illustration; real
    declarations go through adaptive_certify.certified_champion_race). Preemptive good-arm search: re-rank after
    EVERY cheap increment and fund the current most-promising candidate, so a champion whose early returns are
    slipping gets PAUSED (its posterior/checkpoints preserved; resumable) rather than run to completion on sunk
    cost.

    - leader = **Thompson-sampled** best alive candidate (draw a score ~ N(mu, sigma) each and take the max).
      Thompson gives the right explore/exploit balance for free: a tight, observed-good posterior wins
      consistently (so we concentrate + drive it to a verdict), while an inflated-but-uncertain PRIOR wins only
      occasionally (so a mis-ranked #1 gets probed then dropped, not chased) — fixing the churn that plain
      argmax-mean causes. A hysteresis band (`switch_margin`, set ~ the env/reload cost) suppresses physical
      champion switches below the value that justifies a warm-worker reload, so we don't thrash env load.
    - step_fn(candidate) runs ONE cheap increment, mutates its (mu, sigma) posterior, returns the increment $.
    - DECLARE when the leader's P(clears bar) > declare_conf (enough trustworthy evidence accrued).
    - KILL a candidate when its P(clears bar) < kill_conf; then re-pick a leader.
    - ESCALATE (come-ask) when spend reaches budget_gate with no declaration.

    Returns {declared, spent, touched, escalate, switches}.
    """
    spent, touched, switches = 0.0, [], 0
    current = locked = None
    for step_i in range(max_steps):
        alive = [c for c in cands if c.alive]
        if not alive:
            break
        # CONFIRMATION LOCK: once a candidate looks genuinely promising (P(clears) >= lock_conf), concentrate
        # on it to drive it to a verdict — UNLESS it has slipped back below release_conf, in which case pause
        # it (release the lock) and go back to exploring. This is the "commit to confirming a promising one,
        # but don't overcommit to a slipping one" behavior.
        if locked is not None and locked.alive and prob_clears(locked.mu, locked.sigma, bar) >= release_conf:
            leader = locked
        else:
            locked = None
            rng = random.Random(seed * 100003 + step_i)
            leader = max(alive, key=lambda c: rng.gauss(c.mu, max(c.sigma, 1e-9)))   # Thompson draw
            # hysteresis: only pay a physical switch when the challenger's MEAN clears current by switch_margin
            # (a warm champion is cheap to continue; the margin ~ the env/reload cost avoids thrashing)
            if current is not None and current.alive and leader.cid != current.cid:
                if (leader.mu - current.mu) < switch_margin:
                    leader = current
        if current is None or leader.cid != current.cid:
            if current is not None:
                switches += 1
            current = leader

        spent += step_fn(leader)                       # one cheap increment; updates leader's posterior
        touched.append(leader.cid)
        if prob_clears(leader.mu, leader.sigma, bar) >= lock_conf:
            locked = leader                            # promising -> lock on and confirm

        p = prob_clears(leader.mu, leader.sigma, bar)
        if p > declare_conf:
            return {"declared": leader.cid, "spent": round(spent, 2), "touched": touched,
                    "escalate": False, "switches": switches}
        if p < kill_conf:
            leader.alive = False
            current = None
            if locked is leader:
                locked = None
        if spent >= budget_gate:
            return {"declared": None, "spent": round(spent, 2), "touched": touched,
                    "escalate": True, "switches": switches}
    return {"declared": None, "spent": round(spent, 2), "touched": touched,
            "escalate": True, "switches": switches}


def batch_cost(jobs, compute_cost_fn, env_overhead, build_cost=0.0, built_keys=None):
    """
    Total $ for a set of packed jobs: per job, env_overhead once + build_cost once per NOT-yet-cached env key
    + sum of per-unit productive compute. Mutates built_keys (a set) to mark systems now cached, so later
    jobs on the same system skip the build. Returns total cost.
    """
    built = built_keys if built_keys is not None else set()
    total = 0.0
    for key, items in jobs:
        total += env_overhead                       # container pull + conda + imports + staging, once/job
        if key not in built:
            total += build_cost                     # solvate/param/equilibrate the shared system, once
            built.add(key)
        for cid, rung in items:
            total += compute_cost_fn(cid, rung)     # productive GPU-$ per unit
    return total


def allocate(
    cands: list[Candidate],
    free_slots: int,
    top_k: int = 3,
    kill_threshold: float = 0.05,
    rho_schedule: dict[int, float] | None = None,
    max_rung: int = 5,
    n_mc: int = 2000,
    seed: int = 0,
) -> Decision:
    """
    One allocation cycle. Returns which candidates to promote (with next rung), kill, or hold.

    Exploitation: fund highest P(top-k). Exploration: reserve rho*slots for highest-sigma survivors
    (rho decays with rung). Kill: P(top-k) < kill_threshold. Validity fails are killed unconditionally.
    """
    rho_schedule = rho_schedule or DEFAULT_RHO_SCHEDULE
    dec = Decision()

    # 1. unconditional validity kills
    for c in cands:
        if c.alive and not c.valid:
            c.alive = False
            dec.kill.append(c.cid)

    alive = [c for c in cands if c.alive]
    if not alive or free_slots <= 0:
        dec.hold = [c.cid for c in alive]
        return dec

    # 2. exploitation signal
    p = prob_top_k(alive, top_k=top_k, n_mc=n_mc, seed=seed)

    # 3. promise-based kills (only where they cannot be top-k). Deferred severity is the caller's job via
    #    which rung's candidates it passes in; here a low p_i at any rung means "cannot win".
    survivors = []
    for c in alive:
        if p.get(c.cid, 0.0) < kill_threshold:
            c.alive = False
            dec.kill.append(c.cid)
        else:
            survivors.append(c)
    if not survivors:
        return dec

    # candidates that have reached the terminal rung are finalists, not promotable
    promotable = [c for c in survivors if c.rung < max_rung]
    finalists = [c for c in survivors if c.rung >= max_rung]
    dec.hold.extend(c.cid for c in finalists)
    if not promotable:
        dec.hold.extend(c.cid for c in promotable)
        return dec

    # 4. split free slots into exploit vs explore using the reserve of the CHEAPEST promotable rung in play
    cur_rung = min(c.rung for c in promotable)
    rho = rho_schedule.get(cur_rung + 1, 0.0)
    n_explore = int(round(rho * free_slots))
    n_exploit = free_slots - n_explore

    chosen: list[Candidate] = []
    by_promise = sorted(promotable, key=lambda c: p.get(c.cid, 0.0), reverse=True)
    chosen.extend(by_promise[:n_exploit])

    remaining = [c for c in promotable if c not in chosen]
    by_uncertainty = sorted(remaining, key=lambda c: c.sigma, reverse=True)
    chosen.extend(by_uncertainty[:n_explore])

    chosen_ids = {c.cid for c in chosen}
    for c in chosen:
        dec.promote.append((c.cid, c.rung + 1))
    dec.hold.extend(c.cid for c in promotable if c.cid not in chosen_ids)
    return dec
