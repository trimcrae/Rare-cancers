#!/usr/bin/env python3
"""
THE VAST COST MODEL — one objective, measured inputs, and the bid/selection policy that falls out of it.

This module replaces a pile of mutually contradictory heuristics (`min_bid x 1.9`, `x1.5`, `x1.25`, a
reservation price, a duty-cycle quantile, an adaptive UCB) with a single cost function and the decision rule
that minimises it. Everything it needs is either MEASURED (throughput, price, storage) or explicitly a prior
that the output labels as such (the preemption hazard).

===============================================================================================================
1. THE FACTS IT IS BUILT ON  (all verified 2026-07-25 — see `vast-docs-raw.json`, `vast-market-intel.json`,
   `vast-bid-semantics-probe-ladder.json`)
===============================================================================================================

F1. YOU PAY YOUR BID, CAPPED AT THE MACHINE'S ON-DEMAND PRICE. Measured, not read off a doc page: the same
    offer was rented at three bid multiples and the charged rate was bid, bid, and then a constant ceiling —
    x1.0 -> $0.00930 charged on a $0.00930 bid (exactly), x2.5 -> $0.02133 on a $0.02330 bid, x8.0 ->
    $0.02133 on a $0.07470 bid. So the charge tracks the bid and then saturates. Every dollar of bid premium
    below the cap is a dollar spent, on every hour, whether or not it is ever needed.

F2. A HIGHER BID CANNOT BUY SAFETY FROM ON-DEMAND RENTERS. Vast's own documentation: "On-demand instances
    will always take precedence over interruptible instances." So the hazard has a floor no bid can reach
    under, and the premium is buying protection against only part of the risk.

F3. BEING OUTBID PAUSES, IT DOES NOT DESTROY. "Lower-priority instances are paused until their bid is raised
    enough to regain the highest priority or until a higher bid finishes up." Disk survives. So a preemption
    costs the work since the last checkpoint plus downtime — NOT a ~6 GiB image reload. (The reload that
    justified `x1.9` was self-inflicted: our own reaper deleted paused boxes.)

F4. STORAGE BILLS CONTINUOUSLY, RUNNING OR PAUSED. "Billed continuously while your instance exists,
    regardless of running state ... typically higher for stopped instances." Measured median $0.20/GB/month,
    i.e. ~$0.011/hr at the 40 GB our launcher requests. This is the term that stops an arbitrarily low bid
    from being free, and it is the only reason waiting is not costless.

F5. THE MARKET IS IN DEEP EXCESS SUPPLY. Of 445 interruptible offers pulled across the cards we can use,
    essentially none were rented. On an idle machine `min_bid` is the host's RESERVE price, not a competing
    bid — there is nobody there to outbid. Substitutes are abundant: ~148 offers passed our launch filters.

===============================================================================================================
2. THE OBJECTIVE
===============================================================================================================

We buy delivered science, not hours, so the objective is dollars per nanosecond of MD.

    T_run  = (W/theta) / (1 - lam*R)          billed running hours, inflated by work redone after preemption
    T_wall = T_run * (1 + lam*D)              wall clock, inflated by paused time (storage still billing)
    C      = c*T_run + s*T_wall

                       W       c + s*(1 + lam*D)
        =>     C  =  -----  *  -----------------
                     theta        1 - lam*R

  c     = compute $/hr        = our bid (F1)
  s     = storage $/hr        = storage_cost * disk_gb / 730 (F4)
  theta = ns/hr on THIS host  = measured card throughput / 24
  lam   = preemptions per running hour       PRIOR, not measured — every output says so
  R     = work lost per preemption (h)       ~ half the checkpoint interval (F3, no image reload)
  D     = downtime per preemption (h)        re-dispatch latency, since substitutes are abundant (F5)

===============================================================================================================
3. WHAT THE MODEL SAYS TO DO  (each result is a theorem about the cost function above, not a preference)
===============================================================================================================

R1. RANK OFFERS BY $/ns, NEVER BY $/hr. C is proportional to c/theta, so an offer's merit is its price per unit
    throughput. Ranking by $/hr picks a $0.103/hr RTX 3090 over a $0.149/hr RTX 4090 and pays 45% more per ns.

R2. BID AT THE FLOOR (plus a staleness tick), NOT A MULTIPLE OF IT. With lam roughly flat in b — which is what
    F5 implies, since the machines we rent are idle and have no competing bidder — C is strictly increasing in
    b, so the optimum is the lowest bid that wins, i.e. the floor. `premium_breakeven_dlam_db` computes how
    steeply the hazard would have to fall with bid to overturn this; at our numbers it is ~47 preemptions per
    hour per $/hr of premium, which no market in excess supply delivers.

R3. THE OFFER IS THE LEVER, NOT THE CARD AND NOT THE MULTIPLE. Measured spread on the live board: 4.25x between
    the best offer and the best RTX 4090, 2.3x within the 4090 class alone. The `1.9 -> 1.25` multiple change
    that this repo shipped was worth 1.34x. Selection dominates bidding by roughly an order of magnitude.

R4. INTERRUPTIBLE ESSENTIALLY ALWAYS. `breakeven_hazard_vs_ondemand` returns the lam at which on-demand becomes
    cheaper; on today's board that is ~2 preemptions per hour. Take on-demand only for a leg that genuinely
    cannot be paused at all.

R5. SPEND ENGINEERING, NOT DOLLARS, ON RETENTION. R enters as 1/(1-lam*R) and is ours to shrink for free by
    checkpointing more often; b enters linearly and costs money. When churn hurts, tighten checkpointing.

R6. ASK FOR THE DISK THE JOB NEEDS. Storage bills on the allocation, continuously, running or paused (F4).

===============================================================================================================
4. WHAT IS *NOT* CLAIMED
===============================================================================================================

`lam` and `D` are PRIORS. Nothing here measures them, and no output pretends otherwise: `usd_per_ns` reports
`hazard_is_prior: True` and the ranking is stable under wide variation in lam precisely because (R2) the bid
term dominates. If a launch ledger ever accumulates real preemption counts, `fit_hazard` turns them into a
measurement and the priors go away.

The throughput table is measured per CARD, not per HOST, and host variance is real (the covalent panel spanned
19-116 ns/day). `verify_and_abandon_threshold` is the correct response: benchmark briefly on arrival and drop
a host whose realised throughput makes it worse than the next candidate.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

# --- measured throughput ------------------------------------------------------------------------------------
# ns/day at 84,534 particles from the VALIDATED 2026-07-24 Vast grid: 3 x ~20 s independent timed blocks per
# leg, physics-checked (final T 298.7-301.0 K), CV < 1.4%, with a rejection gate that threw out a contended
# host (CV 18.5%) and a mislabelled card. Cards absent from this table were never benched and are ranked LAST
# rather than given a dlperf guess — a spec-sheet proxy is what produced two retracted rankings on 2026-07-24.
#
# THIS IS THE ONLY THROUGHPUT TABLE. `gpu_backend._MEASURED_NS_PER_DAY_84K` and the retracted
# `vast_bid_optimizer.MEASURED_NS_PER_DAY` (which still carried the withdrawn 669 ns/day figure) both defer
# here, so the repo cannot disagree with itself about how fast a card is.
MEASURED_NS_PER_DAY_84K = {
    "RTX4090": 755.36,   # CV 0.14%   blocks 756.55 / 754.56 / 754.98
    "RTX4080": 703.51,   # CV 0.18%   blocks 702.93 / 704.93 / 702.66
    "RTX3090": 359.36,   # CV 1.31%   blocks 364.02 / 359.45 / 354.62
}
REFERENCE_CARD = "RTX4090"
REFERENCE_NS_PER_H = MEASURED_NS_PER_DAY_84K[REFERENCE_CARD] / 24.0   # 31.47 ns per reference GPU-hour

HOURS_PER_MONTH = 730.0

# Priors, flagged as such wherever they surface. See section 4.
DEFAULT_HAZARD_PER_H = 0.10     # preemptions per running hour on an idle host in an over-supplied market
DEFAULT_DOWNTIME_H = 0.25       # re-dispatch to one of ~148 substitutes, not "wait for priority to return"
# Staleness tick only. NOT a priority premium: on an idle machine there is no incumbent to outbid (F5), so
# this exists solely so a quote that moves between search and rent still clears the floor. A bid at or below
# min_bid can leave the box created-but-stopped (verified 2026-07-23), so it must be strictly above.
BID_STALENESS_EPS = 0.02
BID_MIN_TICK_USD = 0.0005


def card_of(gpu_name):
    """Longest-first match of an offer's gpu_name against the benched cards. None if never benched. PURE."""
    n = str(gpu_name or "").replace(" ", "").replace("_", "").upper()
    n = n.replace("SUPER", "S")
    for k in sorted(MEASURED_NS_PER_DAY_84K, key=len, reverse=True):
        if k in n:
            return k
    return None


def ns_per_hour(gpu_name):
    """Measured ns/hr for this card at the ternary system size, or None if never benched. PURE."""
    c = card_of(gpu_name)
    return None if c is None else MEASURED_NS_PER_DAY_84K[c] / 24.0


def storage_usd_per_h(storage_cost_usd_gb_month, disk_gb):
    """$/hr of storage. Bills continuously while the instance EXISTS — running or paused (F4). PURE."""
    try:
        return max(0.0, float(storage_cost_usd_gb_month) * float(disk_gb) / HOURS_PER_MONTH)
    except (TypeError, ValueError):
        return 0.0


# =============================================================================================================
# the cost function
# =============================================================================================================
def usd_per_ns(compute_usd_h, storage_usd_h, ns_per_h, hazard_per_h=DEFAULT_HAZARD_PER_H,
               restart_h=0.0, downtime_h=DEFAULT_DOWNTIME_H):
    """Expected $ per delivered nanosecond of MD — the objective of section 2.

        C/W = [ c + s*(1 + lam*D) ] / [ theta * (1 - lam*R) ]

    Returns None when throughput is unknown (never benched) so callers rank such offers last instead of
    inventing a number for them. Raises on lam*R >= 1, which means preemptions arrive faster than the job can
    make progress between them — a configuration to fix (checkpoint more often), not to price. PURE."""
    if not ns_per_h or ns_per_h <= 0:
        return None
    lam = max(0.0, float(hazard_per_h))
    R, D = max(0.0, float(restart_h)), max(0.0, float(downtime_h))
    useful = 1.0 - lam * R
    if useful <= 0:
        raise ValueError(f"lam*R = {lam * R:.3f} >= 1: work is lost faster than it is done — checkpoint more often")
    return (float(compute_usd_h) + float(storage_usd_h) * (1.0 + lam * D)) / (ns_per_h * useful)


def restart_overhead_h(checkpoint_interval_h):
    """Work lost per preemption. Uniform arrival within a checkpoint interval => half of it on average.

    NOTE what is absent: an image-reload term. The ~20-minute reload that justified a large bid premium was
    caused by our own reaper DELETING paused instances; with pause/resume intact the disk survives (F3). PURE."""
    return max(0.0, float(checkpoint_interval_h)) / 2.0


# =============================================================================================================
# R2 — why the bid is the floor, stated as a falsifiable threshold rather than an opinion
# =============================================================================================================
def premium_breakeven_dlam_db(compute_usd_h, storage_usd_h, hazard_per_h=DEFAULT_HAZARD_PER_H,
                              restart_h=0.0, downtime_h=DEFAULT_DOWNTIME_H):
    """How fast the hazard must FALL with the bid for a premium to pay for itself, in preemptions/hour per $/hr.

    Differentiating C(b) with c = b (F1: you pay your bid) and setting dC/db < 0:

        |dlam/db|  >  (1 - lam*R) / [ (b + s*(1 + lam*D))*R + s*D*(1 - lam*R) ]

    Above this slope a premium is worth paying; below it, every cent of premium is waste. Quoting the number is
    the honest way to hold the policy: it can be refuted by a hazard measurement, and until one exists the
    market's excess supply (F5) makes a slope this steep implausible. PURE."""
    lam = max(0.0, float(hazard_per_h))
    R, D = max(0.0, float(restart_h)), max(0.0, float(downtime_h))
    useful = 1.0 - lam * R
    if useful <= 0:
        return 0.0
    denom = (float(compute_usd_h) + float(storage_usd_h) * (1.0 + lam * D)) * R + float(storage_usd_h) * D * useful
    return float("inf") if denom <= 0 else useful / denom


def breakeven_hazard_vs_ondemand(bid_usd_h, ondemand_usd_h, storage_usd_h,
                                 restart_h=0.0, downtime_h=DEFAULT_DOWNTIME_H):
    """The hazard at which on-demand becomes the cheaper buy (R4). Solves

        (d + s)  =  [ b + s*(1 + lam*D) ] / (1 - lam*R)

    for lam. Returns inf when interruptible wins at every hazard (i.e. even a continuously-preempted box is
    cheaper), and 0.0 when on-demand already wins outright. PURE."""
    d, b, s = float(ondemand_usd_h), float(bid_usd_h), float(storage_usd_h)
    R, D = max(0.0, float(restart_h)), max(0.0, float(downtime_h))
    lhs0 = d + s
    if b + s >= lhs0:                       # on-demand already at least as cheap with zero preemptions
        return 0.0
    # (d+s)(1 - lam R) = b + s + s lam D   ->   lam [ s D + (d+s) R ] = (d+s) - (b+s)
    denom = s * D + lhs0 * R
    return float("inf") if denom <= 0 else max(0.0, (lhs0 - (b + s)) / denom)


# =============================================================================================================
# the bid
# =============================================================================================================
def recommended_bid(min_bid, ondemand_base=None, eps=BID_STALENESS_EPS, tick=BID_MIN_TICK_USD):
    """THE BID. The floor, lifted by a staleness tick, capped at the machine's on-demand price.

    Three clamps, each with a reason and none of them a market multiple:
      * >= min_bid, strictly — a bid at or below the floor can leave the instance created-but-stopped
        (verified 2026-07-23), which costs a whole launch to save a fraction of a cent.
      * + a small tick — the quote can move between the search call and the rent call. This is the ONLY thing
        the margin is for. It is not buying priority: the machines we rent are idle, so there is no incumbent
        bid to beat (F5).
      * <= on-demand — Vast enforces this ceiling itself (F1: the charge saturated at it), but bidding into
        the cap still wastes money on every hour up to it, so we clamp on our side too.
    PURE."""
    try:
        floor = float(min_bid)
    except (TypeError, ValueError):
        return None
    if floor <= 0:
        return None
    bid = max(floor * (1.0 + eps), floor + tick)
    try:
        cap = float(ondemand_base or 0.0)
    except (TypeError, ValueError):
        cap = 0.0
    if cap > 0:
        bid = max(floor, min(bid, cap))          # never below the floor even if the cap sits under it
    return round(bid, 4)


# =============================================================================================================
# offer scoring and selection
# =============================================================================================================
@dataclass
class JobProfile:
    """What the job needs, in the terms the cost function actually uses."""
    disk_gb: float = 40.0
    checkpoint_interval_h: float = 0.5
    # A leg that cannot tolerate any pause at all (the covalent tail needed continuous ~4 h runs) should be
    # priced against on-demand rather than bid for. 0 = pauses are fine, which is the normal case.
    # EXPRESSED IN REFERENCE-CARD HOURS and rescaled per offer: a card at half the throughput needs twice the
    # uninterrupted wall-clock for the same leg, so a continuity requirement penalises slow cards and the
    # cheap-3090 tail is NOT automatically the answer for a leg that must run through.
    min_uninterrupted_h: float = 0.0
    hazard_per_h: float = DEFAULT_HAZARD_PER_H
    downtime_h: float = DEFAULT_DOWNTIME_H
    min_vram_gb: float = 24.0
    min_reliability: float = 0.90
    min_cuda: float = 12.6

    @property
    def restart_h(self):
        return restart_overhead_h(self.checkpoint_interval_h)


@dataclass
class OfferScore:
    offer_id: object
    machine_id: object
    gpu_name: str
    card: str
    min_bid: float
    bid: float
    storage_usd_h: float
    ns_per_h: float
    usd_per_ns: float
    usd_per_reference_gpu_h: float
    ondemand_base: float = None
    breakeven_hazard: float = None
    notes: list = field(default_factory=list)


def score_offer(offer, job: JobProfile, ondemand_base=None, billed_usd_h=None):
    """Expected $/ns for one offer, with the bid we would place on it. None if the card was never benched.

    `billed_usd_h` overrides the bid derivation for rentals that are not bid-priced — an ON-DEMAND offer is
    billed at `dph_total` and has no meaningful `min_bid`, so scoring it off the bid floor would rank the
    on-demand board by a number nobody pays."""
    nsph = ns_per_hour(offer.get("gpu_name"))
    if not nsph:
        return None
    if billed_usd_h is not None:
        try:
            bid = float(billed_usd_h)
        except (TypeError, ValueError):
            return None
        if bid <= 0:
            return None
        floor = bid
    else:
        try:
            floor = float(offer.get("min_bid") or 0)
        except (TypeError, ValueError):
            return None
        if floor <= 0:
            return None
        bid = recommended_bid(floor, ondemand_base)
        if bid is None:
            return None
    s = storage_usd_per_h(offer.get("storage_cost"), job.disk_gb)
    upn = usd_per_ns(bid, s, nsph, job.hazard_per_h, job.restart_h, job.downtime_h)
    if upn is None:
        return None
    notes = []
    if ondemand_base:
        be = breakeven_hazard_vs_ondemand(bid, ondemand_base, s, job.restart_h, job.downtime_h)
        if be == 0.0:
            notes.append("on-demand is cheaper here even with zero preemptions — buy on-demand")
    else:
        be = None
    if job.min_uninterrupted_h > 0 and job.hazard_per_h > 0:
        # The requirement is stated in reference-card hours; on THIS card the same leg occupies
        # t = t_ref * (theta_ref / theta), so a slow card needs a proportionally longer clean window.
        t = job.min_uninterrupted_h * (REFERENCE_NS_PER_H / nsph)
        p = math.exp(-job.hazard_per_h * t)     # P(no preemption in t) under a Poisson hazard
        if p < 0.5:
            notes.append(f"leg needs {t:.1f} h uninterrupted on this card ({job.min_uninterrupted_h:.1f} h on "
                         f"the reference card); P(clean run) ~ {p:.2f} — consider on-demand for this leg")
    return OfferScore(
        offer_id=offer.get("id"), machine_id=offer.get("machine_id"),
        gpu_name=offer.get("gpu_name"), card=card_of(offer.get("gpu_name")),
        min_bid=round(floor, 5), bid=bid, storage_usd_h=round(s, 5), ns_per_h=round(nsph, 3),
        usd_per_ns=round(upn, 6), usd_per_reference_gpu_h=round(upn * REFERENCE_NS_PER_H, 5),
        ondemand_base=ondemand_base, breakeven_hazard=(None if be is None else round(be, 3)), notes=notes)


def passes_filters(offer, job: JobProfile):
    """The hard constraints — VRAM, reliability, CUDA, single GPU, rentable. PURE."""
    if offer.get("rentable") is False:
        return False
    try:
        if int(offer.get("num_gpus", 1) or 1) != 1:
            return False
    except (TypeError, ValueError):
        return False
    ram = float(offer.get("gpu_ram", 0) or 0)
    if (ram / 1024.0 if ram > 1000 else ram) + 0.5 < job.min_vram_gb:
        return False
    if float(offer.get("reliability2") or 0) < job.min_reliability:
        return False
    cmg = float(offer.get("cuda_max_good") or 0)
    if cmg and cmg + 1e-6 < job.min_cuda:
        return False
    return True


def rank_offers(offers, job: JobProfile, ondemand_by_machine=None):
    """All qualifying offers, cheapest expected $/ns first. Unbenched cards are excluded, not guessed at."""
    od = ondemand_by_machine or {}
    out = []
    for o in offers:
        if not passes_filters(o, job):
            continue
        s = score_offer(o, job, od.get(str(o.get("machine_id"))))
        if s is not None:
            out.append(s)
    out.sort(key=lambda r: (r.usd_per_ns, r.min_bid))
    return out


def verify_and_abandon_threshold(ranked, k=1):
    """Realised $/ns above which a rented host should be dropped for the next candidate.

    The throughput table is per CARD; a specific HOST can be much slower (the covalent panel spanned 19-116
    ns/day). Because re-dispatch is cheap and substitutes are abundant (F5), the right response to that
    uncertainty is to measure on arrival and abandon a bad draw — a Pandora's-box stopping rule, where the
    threshold is simply the next-best candidate's expected cost. Returns None if there is no fallback."""
    if len(ranked) <= k:
        return None
    return ranked[k].usd_per_ns


def summarise_market(ranked, top=10):
    """The three numbers a cost estimate should be quoted from: the best offer, a robust best-k mean, and the
    median. Planning off the single cheapest offer is fragile; planning off the median forgoes the whole
    point of ranking. The best-k mean is what a policy that always takes one of the top k actually achieves."""
    if not ranked:
        return None
    u = [r.usd_per_ns for r in ranked]
    k = min(top, len(u))
    best_k = sum(u[:k]) / k
    mid = u[len(u) // 2]
    return {
        "n_offers": len(u),
        "best_usd_per_ns": round(u[0], 6),
        f"best{k}_mean_usd_per_ns": round(best_k, 6),
        "median_usd_per_ns": round(mid, 6),
        "best_usd_per_reference_gpu_h": round(u[0] * REFERENCE_NS_PER_H, 4),
        f"best{k}_mean_usd_per_reference_gpu_h": round(best_k * REFERENCE_NS_PER_H, 4),
        "median_usd_per_reference_gpu_h": round(mid * REFERENCE_NS_PER_H, 4),
        "spread_best_to_median": round(mid / u[0], 2) if u[0] > 0 else None,
        "cards_in_top10": sorted({r.card for r in ranked[:k]}),
        "hazard_is_prior": True,
    }
