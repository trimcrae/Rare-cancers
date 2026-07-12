#!/usr/bin/env python3
"""
Certification + error-control layer for the NR4A3 selective-degrader screen — DELIBERATELY SEPARATE from the
allocator (adaptive_allocator.py). This split is a hard requirement from the 2026-07-12 methodology review:

  * The ALLOCATOR (Thompson sampling, confirmation-lock, futility scheduling) may only choose WHAT to compute
    next. It must NEVER decide whether a candidate PASSES.
  * This module makes the PASS decision, and ONLY from terminal-rung evidence, using anytime-valid bounds that
    stay honest under repeated looks + data-dependent stopping, with a pre-declared campaign-wide error budget.

What this module does NOT claim: that a converged calculation is physically correct. A candidate that PASSES
here is a **"computationally qualified NR4A3-selectivity candidate"** — NOT a "selective hit" or "selective
degrader." Passing overlap/hysteresis/cycle-closure proves *numerical convergence*, not robustness to force
field / charge model / protonation / tautomer / pose / hidden slow modes / shared cross-paralogue bias, and
the terminal ternary score is itself only a surrogate for cellular degradation. Only wet-lab confirmation
upgrades the label.

Pure stdlib (math, hashlib, json). Deterministic. Runs anywhere.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass, field

# ---- result-status taxonomy (fix 4: invalidity != candidate failure) --------------------------------------
# A computation's outcome is NOT a boolean "valid". These four are scientifically distinct and must be
# recorded distinctly so a later report never treats missing evidence as negative evidence.
TECHNICAL_FAIL = "TECHNICAL_FAIL"        # no trustworthy estimate (bad overlap/hysteresis/cycle) -> abstain, retry
GROSS_FAIL = "GROSS_FAIL"                # a pre-defined scientific gross failure (e.g. stable dissociation)
FUTILITY = "FUTILITY"                    # calibrated evidence shows the bar is unattainable
VALID_UNFAVORABLE = "VALID_UNFAVORABLE"  # trustworthy estimate, does not clear the bar
VALID_FAVORABLE = "VALID_FAVORABLE"      # trustworthy estimate consistent with clearing the bar

# ---- candidate lifecycle states (fix 3: the clean state machine) ------------------------------------------
ORDER = "ORDER"                          # cheap prior only; not yet computed
PROMOTE = "PROMOTE"                      # preliminary data justify more compute
TECHNICAL_STOP = "TECHNICAL_STOP"        # computation unusable
FUTILITY_STOP = "FUTILITY_STOP"          # calibrated evidence: terminal bar unattainable
PASS_CANDIDATE = "PASS_CANDIDATE"        # independent/anytime-valid terminal evidence clears EVERY constraint
ABSTAIN_ESCALATE = "ABSTAIN_ESCALATE"    # budget exhausted without a valid decision


# ---- anytime-valid confidence sequence (fix 3: optional-stopping-safe) -------------------------------------

def anytime_lower_bound(xbar: float, n: int, sigma: float, delta: float, rho: float | None = None) -> float:
    """
    One-sided lower confidence bound on the true mean that is VALID UNIFORMLY over all sample sizes n (a
    confidence sequence), so repeatedly peeking at streamed replicas and stopping at a favorable crossing does
    NOT inflate the error. Sub-Gaussian normal-mixture boundary (Howard-Ramdas-style): with V_n = n*sigma^2
    and mixture variance rho, P(exists n : true_mean < LB(n)) <= delta.
    """
    if n <= 0:
        return float("-inf")
    sigma = max(sigma, 1e-9)
    Vn = n * sigma * sigma
    if rho is None:
        rho = sigma * sigma                      # tune the boundary to be tight near n≈1
    u = math.sqrt(2.0 * (Vn + rho) * math.log((1.0 / delta) * math.sqrt((Vn + rho) / rho)))
    return xbar - u / n


def anytime_upper_bound(xbar: float, n: int, sigma: float, delta: float, rho: float | None = None) -> float:
    """Symmetric anytime-valid UPPER bound (for futility: if the upper bound < bar, the bar is unattainable)."""
    return xbar + (xbar - anytime_lower_bound(xbar, n, sigma, delta, rho)) if n > 0 else float("inf")


def campaign_delta_split(delta_total: float, n_candidates: int) -> float:
    """
    PER-CANDIDATE slice of a PRE-DECLARED campaign-wide false-declaration budget (union bound over candidates).
    `certify_candidate` then splits THIS further across the candidate's anti-target margins, so the overall
    union over candidates x margins x all stopping times keeps the campaign false-declaration prob <=
    delta_total. Do NOT also divide by n_margins here — that double-counts the margin split and makes
    certification over-conservative (a strong winner can then never certify).
    """
    return delta_total / max(1, n_candidates)


# ---- per-margin evidence (fix 1.3: noncompensatory vector pass) --------------------------------------------

@dataclass
class MarginEvidence:
    """Running evidence for ONE paralogue-selectivity margin (e.g. NR4A3 - NR4A1). Selectivity is a VECTOR of
    such margins; they must NOT be averaged — a strong NR4A3-NR4A1 cannot compensate a weak NR4A3-NR4A2."""
    target: str
    n: int = 0
    mean: float = 0.0
    sigma: float = 1.0                       # sub-Gaussian variance proxy for the per-replica margin
    sigma_fixed: bool = True                 # keep sigma at a KNOWN conservative bound. A data-ESTIMATED sigma
                                             # breaks anytime-validity of the confidence sequence, so certifying
                                             # runs with a fixed known bound; estimation is heuristic only.
    m2: float = 0.0                          # running sum of squared deviations (Welford), for the heuristic est
    from_terminal_rung: bool = False         # only terminal-rung evidence may certify
    replicas: list = field(default_factory=list)   # dicts: {seed, start_state, parent_traj}

    def update(self, obs: float, seed=None, start_state=None, parent_traj=None):
        self.n += 1
        d = obs - self.mean
        self.mean += d / self.n
        self.m2 += d * (obs - self.mean)
        if not self.sigma_fixed and self.n >= 2:
            self.sigma = max(math.sqrt(self.m2 / (self.n - 1)), 1e-6)
        self.replicas.append({"seed": seed, "start_state": start_state, "parent_traj": parent_traj})

    def effective_n(self) -> int:
        """Discount correlated replicas: distinct seed AND start_state, and not sharing a parent trajectory
        (fix 4: replicas from one equilibrated parent are NOT fully independent)."""
        seen_keys, parents = set(), {}
        eff = 0
        for r in self.replicas:
            key = (r.get("seed"), r.get("start_state"))
            pt = r.get("parent_traj")
            if key in seen_keys:
                continue
            if pt is not None and parents.get(pt, 0) >= 1:
                parents[pt] += 1
                continue                     # sibling of an already-counted replica from the same parent
            seen_keys.add(key)
            if pt is not None:
                parents[pt] = parents.get(pt, 0) + 1
            eff += 1
        return eff


def replicas_independent(margin: MarginEvidence, need: int) -> bool:
    return margin.effective_n() >= need


# ---- certification (fix 1.2 + 1.3 + 3 + 7): the ONLY place a PASS is decided ------------------------------

def certify_candidate(margins: dict, bar: float, robustness: float, delta_candidate: float,
                      min_independent_replicas: int = 3, require_terminal: bool = True) -> str:
    """
    Decide a candidate's terminal state using ONLY terminal-rung margin evidence and anytime-valid bounds.
    Returns PASS_CANDIDATE only if, for EVERY required anti-target margin simultaneously (noncompensatory):
      * evidence is from the terminal rung (if require_terminal),
      * enough INDEPENDENT replicas (distinct seeds + starting states, not one parent),
      * the anytime-valid LOWER bound at delta_candidate/2 >= bar + robustness (a robustness margin above the
        nominal bar to absorb model uncertainty).
    Never reads the cheap prior or the allocator's scheduling posterior. Returns FUTILITY_STOP if any margin's
    anytime UPPER bound is already below the bar; else PROMOTE (needs more evidence).
    """
    if not margins:
        return PROMOTE
    delta_margin = delta_candidate / max(1, len(margins))
    all_pass = True
    for m in margins.values():
        if require_terminal and not m.from_terminal_rung:
            all_pass = False
            continue
        if m.n > 0 and anytime_upper_bound(m.mean, m.n, m.sigma, delta_margin) < bar:
            return FUTILITY_STOP                       # this margin can't reach the bar -> whole candidate futile
        if not replicas_independent(m, min_independent_replicas):
            all_pass = False
            continue
        lb = anytime_lower_bound(m.mean, m.n, m.sigma, delta_margin)
        if lb < bar + robustness:
            all_pass = False
    return PASS_CANDIDATE if all_pass else PROMOTE


# ---- content-addressed system identity (fix 4: cache scientific inputs, not just env) ---------------------

def system_content_hash(inputs: dict) -> str:
    """
    Content hash over ALL scientific inputs of a built system — structure, protonation/tautomer, force-field +
    parameters, restraints, atom mapping, starting coordinates, AND the software env. Two scientifically
    distinct systems (e.g. different protonation) MUST get different hashes even under an identical software
    stack, so a cached build is never wrongly reused.
    """
    canonical = json.dumps(inputs, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


# ---- result classification (fix 4) ------------------------------------------------------------------------

def classify_result(overlap_ok: bool, hysteresis_ok: bool, cycle_ok: bool, pocket_survival: float,
                    margin_point: float, bar: float, pocket_bar: float = 0.5,
                    gross_dissociation: bool = False) -> str:
    """
    Map raw diagnostics to a result STATUS. Distinguishes technical failure (no trustworthy estimate) from
    scientific gross failure from a valid-but-unfavorable result. Pocket loss is recorded as a GROSS scientific
    outcome (a real unfavorable mechanism), NOT lumped into estimator/technical failure.
    """
    if gross_dissociation or pocket_survival < pocket_bar:
        return GROSS_FAIL
    if not (overlap_ok and hysteresis_ok and cycle_ok):
        return TECHNICAL_FAIL                          # unusable estimate -> abstain/retry, NOT a chemistry verdict
    return VALID_FAVORABLE if margin_point >= bar else VALID_UNFAVORABLE


# ---- certification-integrated champion race (state machine; fixes 1-4, 7) ---------------------------------

@dataclass
class CertCandidate:
    cid: str
    prior: float = 0.0                                    # cheap prior score — SCHEDULING ONLY, never certifies
    state: str = ORDER
    spent: float = 0.0
    technical_fails: int = 0
    margins: dict = field(default_factory=dict)           # target -> MarginEvidence (terminal evidence)

    def promise(self) -> float:
        """Scheduling-only scalar: the WORST running margin mean (noncompensatory-aware). If no evidence yet,
        fall back to the cheap prior — for ORDERING the search only, never for certification."""
        if not self.margins:
            return self.prior
        return min(m.mean for m in self.margins.values())

    def sched_sigma(self) -> float:
        if not self.margins:
            return 1.5                                    # wide: cheap prior is weakly predictive
        return max((m.sigma / max(1, m.n) ** 0.5 for m in self.margins.values()), default=1.0)


def certified_champion_race(cands, step_fn, budget_gate, bar, robustness=0.0, delta_total=0.05,
                            targets=("NR4A1", "NR4A2"), min_independent_replicas=3, max_technical_retries=2,
                            lock_promise=None, release_promise=None, seed=0, max_steps=4000):
    """
    Champion race with allocation and certification SEPARATED (review fix 1.2). Scheduling (Thompson on the
    scheduling promise + a lock/release on that promise) decides WHO to compute next; the PASS decision is made
    ONLY by certify_candidate on terminal-rung margin evidence with a campaign-wide anytime-valid error budget.
    The cheap prior can order the search but can NEVER cause a declaration.

    step_fn(cid) -> (cost, {target: obs}, result_status, terminal_bool, meta) where meta carries
    seed/start_state/parent_traj for the independence check. Returns a dict incl. `declared` (a
    'computationally qualified NR4A3-selectivity candidate', not a 'hit'), `spent`, `touched`, `states`,
    and the per-candidate `delta` used.
    """
    delta_cand = campaign_delta_split(delta_total, len(cands))       # certify splits this across margins
    lock_promise = bar if lock_promise is None else lock_promise
    release_promise = (bar - 0.3) if release_promise is None else release_promise
    by = {c.cid: c for c in cands}
    for c in cands:
        for t in targets:
            c.margins.setdefault(t, MarginEvidence(target=t))

    spent, touched, locked = 0.0, [], None
    for step_i in range(max_steps):
        active = [c for c in cands if c.state in (ORDER, PROMOTE)]
        if not active:
            break
        # ---- SCHEDULING ONLY (never certifies) ----
        if locked is not None and by[locked].state in (ORDER, PROMOTE) and by[locked].promise() >= release_promise:
            leader = by[locked]
        else:
            locked = None
            rng = random.Random(seed * 100003 + step_i)
            leader = max(active, key=lambda c: rng.gauss(c.promise(), max(c.sched_sigma(), 1e-9)))
        # ---- run one increment ----
        cost, obs_by_target, status, terminal, meta = step_fn(leader.cid)
        spent += cost
        touched.append(leader.cid)
        meta = meta or {}

        if status == TECHNICAL_FAIL:
            leader.technical_fails += 1                    # no trustworthy estimate: abstain/retry, DO NOT kill
            if leader.technical_fails > max_technical_retries:
                leader.state = TECHNICAL_STOP             # abstain this arm (missing evidence != negative)
            if spent >= budget_gate:
                leader.state = leader.state if leader.state == TECHNICAL_STOP else PROMOTE
                break
            continue
        if status == GROSS_FAIL:
            leader.state = FUTILITY_STOP                  # real scientific gross failure (e.g. dissociation)
            continue
        # VALID_* : fold the margin observations into terminal evidence (only terminal counts for certification)
        for t, obs in (obs_by_target or {}).items():
            m = leader.margins[t]
            m.from_terminal_rung = m.from_terminal_rung or terminal
            m.update(obs, seed=meta.get("seed"), start_state=meta.get("start_state"),
                     parent_traj=meta.get("parent_traj"))
        if leader.promise() >= lock_promise:
            locked = leader.cid                           # scheduling lock (promising) — still not a pass

        # ---- CERTIFICATION (the ONLY pass authority) ----
        verdict = certify_candidate(leader.margins, bar=bar, robustness=robustness,
                                    delta_candidate=delta_cand,
                                    min_independent_replicas=min_independent_replicas, require_terminal=True)
        if verdict == PASS_CANDIDATE:
            leader.state = PASS_CANDIDATE
            return {"declared": leader.cid, "spent": round(spent, 2), "touched": touched,
                    "states": {c.cid: c.state for c in cands}, "delta": delta_cand, "escalate": False}
        if verdict == FUTILITY_STOP:
            leader.state = FUTILITY_STOP
            if locked == leader.cid:
                locked = None
        if spent >= budget_gate:
            break
    # no PASS under the gate
    return {"declared": None, "spent": round(spent, 2), "touched": touched,
            "states": {c.cid: c.state for c in cands}, "delta": delta_cand, "escalate": True}

