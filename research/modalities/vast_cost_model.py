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
    ⚠ **DISPUTED BY OBSERVATION, 2026-07-25** — see
    `research/compute/vast-churn-observations-2026-07-25.md`. F3 is quoted from the vendor docs and describes
    the OUTBID path. On the 5a-KS benchmark run the dominant failure was NOT that path: boxes went to
    `cur_state=stopped` with `intended_status=stopped` and answered a start with
    `{"error": "resources_unavailable"}`, i.e. the host could not schedule us at all. Those did NOT resume on
    their own and could not be made to — a bid raised 26% to its value ceiling changed nothing — so each one
    cost a destroy plus a full image pull on a different machine. **The reload term is therefore real for this
    failure mode even though F3 correctly describes the outbid one.** Both exist; only one is priced below.

F4. STORAGE BILLS CONTINUOUSLY, RUNNING OR PAUSED. "Billed continuously while your instance exists,
    regardless of running state ... typically higher for stopped instances." Measured median $0.20/GB/month,
    i.e. ~$0.011/hr at the 40 GB our launcher requests. This is the term that stops an arbitrarily low bid
    from being free, and it is the only reason waiting is not costless.

F5. THE MARKET IS IN DEEP EXCESS SUPPLY. Of 445 interruptible offers pulled across the cards we can use,
    essentially none were rented. On an idle machine `min_bid` is the host's RESERVE price, not a competing
    bid — there is nobody there to outbid. Substitutes are abundant: ~148 offers passed our launch filters.
    ⚠ **THE INFERENCE, NOT THE COUNT, IS DISPUTED (2026-07-25).** F5 is measured by counting OFFERS; it is
    used to conclude that a rented machine is idle. On the 5a-KS run roughly HALF of actual RENTAL ATTEMPTS
    were refused with `resources_unavailable` across 8+ distinct machines — so "an offer is listed" does not
    imply "the GPU is free", and the step from the offer census to "there is nobody there" does not carry.
    The excess-supply claim may well hold in aggregate (substitutes were indeed always available); what fails
    is using it as evidence that an acquired machine has no competing occupant.

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
    steeply the hazard would have to fall with bid to overturn this; at the policy's own operating point on
    the 2026-07-25 board it is 105 preemptions/hour per $/hr of premium, which no market in excess supply
    delivers. On that same board the retired rules cost 1.12x (x1.25), 1.26x (x1.5) and 1.48x (x1.9) the
    policy, on the very offer their own min_bid ranking selects.

R3. THE OFFER IS THE LEVER, NOT THE CARD AND NOT THE MULTIPLE. Measured on the 2026-07-25 board, all-in $/ns:
    5.43x from the best offer to the median, and 2.61x between the best offer overall and the best RTX 4090.
    Against 1.48x for the whole x1.9 -> floor bid change. Selection is worth several times what bidding is.

R4. INTERRUPTIBLE ESSENTIALLY ALWAYS. `breakeven_hazard_vs_ondemand` returns the lam at which on-demand becomes
    cheaper; on today's board that is ~2-3 preemptions per hour. Take on-demand only for a leg that genuinely
    cannot be paused at all.

R5. SPEND ENGINEERING, NOT DOLLARS, ON RETENTION. R enters as 1/(1-lam*R) and is ours to shrink for free by
    checkpointing more often; b enters linearly and costs money. When churn hurts, tighten checkpointing.

R6. ASK FOR THE DISK THE JOB NEEDS. Storage bills on the allocation, continuously, running or paused (F4), and
    at the cheap end of the board it is not a rounding error: on the best offer (a $0.0147/hr RTX 3090) the
    40 GB our launcher requests costs $0.0110/hr against a $0.0152 bid — 42% of the total. Halving the disk
    there cuts all-in cost by ~21% ($0.0570 -> $0.0449 per reference GPU-hour), which is more than the entire
    bid change is worth. It is also why the best 3090's advantage over the best 4090 shrinks from 4.25x on
    $/ns-before-storage to 2.61x all-in: cheap compute makes the fixed storage line proportionally larger.

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
#
# ★★ RE-ANCHORED 2026-07-27 — ONE ESTIMATOR FOR EVERY ENTRY: THE MEDIAN OVER N INDEPENDENT HOSTS.
#
# ⛔ WHAT WAS WRONG BEFORE, AND IT WAS NOT A 4090 PROBLEM. The previous three figures were ONE HOST EACH, and
# by accident they sampled different parts of their own distributions: the RTX 4080's host sat within 0.3 % of
# the best of four, while the RTX 4090's sat 6.7 % below the best of five. **They were therefore not the same
# statistic**, and every card RATIO in this repo inherited that: the old table said 4090/4080 = 1.074 while a
# same-tool, same-environment, multi-host measurement says 1.160. A single-host bench is one draw from a
# distribution whose width nobody had measured — and the widths are not small or uniform (RTX 5080 spans 14 %,
# RTX 3090 9.5 %, RTX 4090 4.1 %, RTX 4080 4.0 %).
#
# The estimator is `vast_bench_sweep.median_over_hosts` — MEDIAN, not max (which ratchets upward with every
# host added and drifts anti-conservative) and not mean (dragged by the throttled tail). N >= 3 makes it
# robust to one bad host. Two entries below could not reach N >= 3 on the board that day and SAY SO rather
# than pretending: an under-sampled entry errs conservatively (confounders are one-sided downward, so it
# understates throughput and OVERSTATES `$/ns`, and we under-buy).
#
# ★ AND A SECOND, INDEPENDENT CAUSE THAT IS LARGER THAN HOST SAMPLING FOR ONE CARD. The retired figures were
# measured in the conda-pack'd `md` environment; these are measured in the `nr4a3fep` image's `rbfe`
# environment — **the one the production lanes actually run**. The gap is not uniform across cards
# (RTX 4080 unchanged, RTX 4090 +6 %, RTX 3090 +28 %), so it is not a simple scale factor and cannot be
# corrected for. The rule that resolves it is the one this lane was built on: *a bench must measure the
# CUDA/OpenMM build the SCIENCE runs on, or its ns/day prices a stack we do not use.* The old numbers priced
# a stack we no longer run.
#
# Full evidence, including the retired values and the reconciliation that produced this change:
# `throughput-bench-provenance.json`. Old values are registered in
# `research/manuscripts/pinned-figures.json`; the correction is an APPENDIX line in
# `research/compute/pricing.md`, and `vast-ladder-repricing.json` was REGENERATED, never hand-edited.
MEASURED_NS_PER_DAY_84K = {
    # card            ns/day     estimator                 the independent hosts it is the median of
    "RTX5090":       1034.58,  # median of 3 hosts         1003.24 / 1034.58 / 1067.80
    "RTX4090":        804.06,  # median of 6 hosts          777.03 / 792.70 / 799.15 / 808.96 / 809.82 / 810.37
    "RTX5080":        752.32,  # median of 3 hosts          683.12 / 752.32 / 793.79
    "RTX4080":        693.35,  # median of 4 hosts          675.74 / 692.51 / 694.18 / 703.87
    "A100PCIE":       524.43,  # ** 2 hosts, provisional ** 523.82 / 525.05   <- board has only 2 offers
    "RTX3090TI":      481.96,  # median of 3 hosts          481.78 / 481.96 / 530.20
    "RTXPRO4000":     471.63,  # median of 3 hosts          464.54 / 471.63 / 482.34
    "RTX3090":        460.91,  # median of 3 hosts          426.51 / 460.91 / 471.18
    "RTX5060TI":      389.16,  # median of 4 hosts          385.40 / 387.78 / 390.55 / 400.01
    "RTXA4000":       246.30,  # median of 3 hosts          242.20 / 246.30 / 252.33
}
# ★★ WHAT THE TABLE ACTUALLY BENCHES — one home, because the docstring below used to claim otherwise
#    (2026-07-31).
#
# `vast_bench_sweep` records the protocol verbatim: *"gpu_md_bench.py TIP3P/PME 84,534 particles, 4 fs HMR,
# 3 timed blocks ~60 s total"*. So every ns in this repo's `$/ns` is a nanosecond of **plain, single-replica
# MD on a pure water box of 84,534 particles** — NOT a nanosecond of any lane's science. RUNG 5a-KS's ternary
# assembly is 147,788 particles (measured, `ternary-arm-iteration-rates.json`) run as a 12-window HREX RBFE;
# the valB ternary legs are 141,458-144,447. The protocol difference is larger than the size difference.
#
# ⚠ THIS IS AN INDEX, AND IT IS SOUND AS ONE — the arithmetic is what makes that true rather than the
# intention. `basis_usd_per_ns = plan_$/ref-GPU-h / REFERENCE_NS_PER_H` and `rung_ns_per_unit = ref_gpu_h *
# REFERENCE_NS_PER_H`, so `REFERENCE_NS_PER_H` CANCELS out of both gate tests: `ratio_vs_basis` and
# `projected_usd` are exactly invariant to a uniform change in system size. Verified by re-deriving both under
# a 3.37x and a 10x uniform slowdown — identical to 1e-9 (`tests/test_throughput_is_an_index.py`). Nothing has
# ever been bought over a ceiling because of the size gap.
#
# ⚠ WHAT THE INDEX DOES REST ON, AND IT IS UNTESTED: that card-to-card THROUGHPUT RATIOS transfer from the
# water box to the real assemblies. The cancellation is exact only for a UNIFORM factor. The repo already has
# evidence that such gaps need not be uniform — the conda-env re-anchor moved RTX 4080 by 0 %, RTX 4090 by
# +6 % and RTX 3090 by +28 %. It cannot be tested from today's data: across every 4 fs ternary leg there is
# exactly ONE production point per card, no two cards share a leg, and the only card with several points
# (RTX 4090: 7.9 / 16.6 / 17.0 s/iter) has them on different legs with one from a 12-iteration smoke. Closing
# that is what a system-keyed rate table is for; until then this is a stated assumption, not a measurement.
BENCH_PARTICLES = 84534
BENCH_PROTOCOL = ("gpu_md_bench.py TIP3P/PME 84,534 particles, 4 fs HMR, plain single-replica MD, "
                  "3 timed blocks ~60 s total")
REFERENCE_CARD = "RTX4090"
# DERIVED, never typed: whatever the reference card's entry says, divided by 24.
REFERENCE_NS_PER_H = MEASURED_NS_PER_DAY_84K[REFERENCE_CARD] / 24.0

# =============================================================================================================
# ★★ VARIANT SKUs — THREE BENCHED CARDS, AND AN ALLOW-LIST OF WHO MAY BORROW THEIR NUMBER (2026-07-27)
# =============================================================================================================
# THE DEFECT THIS REPLACES. `card_of` used to be a LONGEST-FIRST SUBSTRING match over the three keys above, so
# any marketplace name containing one of them silently inherited that card's throughput. Verified at source:
#
#     RTX 3090 Ti -> RTX3090 (14.973 ns/h)   RTX 4080S -> RTX4080 (29.313)   RTX 4090D -> RTX4090 (31.473)
#
# That is worse than being unpriceable. An UNKNOWN is visibly absent from the ranking; a substitution produces
# a confident-looking `$/ns` that is wrong and that nothing downstream can distinguish from a measurement. It
# is the same failure shape as a fabricated constant, arriving through string normalisation instead of through
# a typed number — and the repo has already retracted two rankings built on guessed throughput.
#
# ★ AND THE ACCIDENT WAS NOT EVEN CONSISTENT IN DIRECTION. That is what settles the design:
#
#   * `RTX 3090 Ti` is a STRICT SPEC SUPERSET of the 3090 (same GA102: 10752 vs 10496 CUDA cores, 1008 vs
#     936 GB/s, higher TGP). Borrowing the 3090's number therefore UNDERSTATES its throughput, which
#     OVERSTATES its `$/ns`. We under-buy it. Safe direction.
#   * `RTX 4080 SUPER` is likewise a strict superset of the 4080 (same AD103: 10240 vs 9728 cores, 736.3 vs
#     716.8 GB/s). Same safe direction — and it matters today, because the cheapest gradeable offer on the
#     2026-07-27 board is a 4080S, i.e. exactly the offer a per-unit gate would place FIRST. The rate we
#     think we are buying is a conservative one; the rate we get can only be better.
#   * `RTX 4090D` is the CUT-DOWN China SKU of the 4090 (14592 vs 16384 CUDA cores, ~11 % fewer). Borrowing
#     the 4090's number OVERSTATES its throughput and UNDERSTATES its `$/ns` — it makes a slower card look
#     like the reference and lures a rental in. **Unsafe direction, and it was on the live board.**
#
# THE RULE. A variant may borrow a benched figure ONLY IF it is a strict spec superset of that base SKU, so
# the borrowed value is a LOWER BOUND on its true throughput and the resulting `$/ns` is an UPPER BOUND on its
# true cost. Then the estimate can only ever make a card look WORSE than it is; it can never lure us into a
# bad rental, only cause us to skip a good one. Anything else — a cut-down SKU, a different die, a card we
# simply have not benched — resolves to None and is excluded from ranking exactly like an RTX 5090.
#
# ⚠ A CONSERVATIVE ALIAS IS A DERIVED FIGURE, NOT A MEASUREMENT. `throughput_provenance()` says which, every
# caller that reports a rate is expected to carry it, and both entries below are on the bench shortlist so the
# alias is a bridge rather than a resting place. The bound is one-sided and the size is small — the spec
# deltas above cap the understatement at roughly 5-10 % — but it is not zero and must not be quoted as one.
#
# WHY NOT SIMPLY None FOR EVERYTHING UNBENCHED (the strictly-honest option)? Because it would delete the
# CHEAP END of an already-thin board: on the 2026-07-27 8:29 AM ET board it drops `priceable` from 11 to 9 and
# removes the single cheapest gradeable offer, at the exact moment a per-unit gate needs cheap gradeable
# supply to place units against. A one-sided, labelled, spec-argued bound keeps that supply while making the
# error impossible to be in our favour. Deleting it would be caution pointed at the wrong risk.
CONSERVATIVE_ALIASES = {
    # variant  : (benched base, why the base is a LOWER bound on this SKU's throughput)
    # ★ `RTX3090TI` WAS HERE AND HAS BEEN RETIRED BY A MEASUREMENT (2026-07-27) — which is the hand-off this
    # block's own text describes ("both entries below are on the bench shortlist so the alias is a bridge
    # rather than a resting place"). `vast_bench_sweep` benched it at the anchors' protocol and it is now a
    # MEASURED entry above. The retirement also VALIDATES the alias's central claim: the borrowed RTX 3090
    # figure was a genuine lower bound, and the real card is ~34% faster than the number it was borrowing.
    # An alias and a measurement for the same key must never coexist — the measurement wins, always.
    "RTX4080S":  ("RTX4080", "same AD103 die, strict superset: 10240 vs 9728 CUDA cores, 736.3 vs 716.8 GB/s"),
}
# Known-unsafe substrings, recorded so the removal cannot be undone by someone re-adding a substring match
# without reading the argument above. Purely documentation for a test to assert against.
ANTI_CONSERVATIVE_VARIANTS = {
    "RTX4090D": ("RTX4090", "CUT-DOWN China SKU: 14592 vs 16384 CUDA cores — the base OVERSTATES it"),
}

HOURS_PER_MONTH = 730.0

# Priors, flagged as such wherever they surface. See section 4.
# ⚠ BOTH PRIORS ARE DISPUTED BY THE 2026-07-25 5a-KS RUN — see
# `research/compute/vast-churn-observations-2026-07-25.md`. They are left at their original values on
# purpose: one night on one lane justifies flagging them, NOT refitting them to a new invented number.
# Pass explicit values, or fit them with `fit_lambda_ref`, rather than trusting these.
DEFAULT_HAZARD_PER_H = 0.10     # preemptions per running hour on an idle host in an over-supplied market
                                # ⚠ looked 2.5-4x LOW over ~15-20 observed running hours (2026-07-25)
DEFAULT_DOWNTIME_H = 0.25       # re-dispatch to one of ~148 substitutes, not "wait for priority to return"
                                # ⚠ assumes an AUTOMATIC re-dispatch loop. None exists: on 2026-07-25 two
                                # legs sat hostless for 203 and 276 min because a human had to notice.
# Staleness tick only. NOT a priority premium: on an idle machine there is no incumbent to outbid (F5), so
# this exists solely so a quote that moves between search and rent still clears the floor. A bid at or below
# min_bid can leave the box created-but-stopped (verified 2026-07-23), so it must be strictly above.
BID_STALENESS_EPS = 0.02
BID_MIN_TICK_USD = 0.0005


def normalise_gpu_name(gpu_name):
    """A marketplace `gpu_name` reduced to the form the tables are keyed on. PURE."""
    return str(gpu_name or "").replace(" ", "").replace("_", "").replace("-", "").upper().replace("SUPER", "S")


def _model_key(gpu_name):
    """The table key this name resolves to (a benched key or an alias key), or None. PURE.

    SUFFIX-ANCHORED, longest key first — the one rule that gets every real name right:

      * a VENDOR PREFIX is free, because the same card is called `RTX 4090` on the marketplace and
        `NVIDIA GeForce RTX 4090` by the CUDA driver, and both must resolve to the same measurement;
      * a TRAILING QUALIFIER is fatal, because that is exactly what distinguishes a different SKU —
        `RTX 4090D` (cut-down), `RTX 3090 Ti` (faster), `RTX 4080 SUPER` (faster), a laptop part. Those may
        only resolve through the explicit `CONSERVATIVE_ALIASES` allow-list, never by falling off the end of
        a substring sweep.

    The old rule was an unanchored substring match, which is how `RTX 4090D` came to be priced as a full
    RTX 4090 — understating its `$/ns` in the direction that BUYS."""
    n = normalise_gpu_name(gpu_name)
    if not n:
        return None
    for k in sorted(set(MEASURED_NS_PER_DAY_84K) | set(CONSERVATIVE_ALIASES), key=len, reverse=True):
        if n.endswith(k):
            return k
    return None


def card_of(gpu_name):
    """The benched card whose throughput this offer may use, or None. PURE.

    See the block above `CONSERVATIVE_ALIASES`: a variant may borrow a benched figure only when it is a strict
    spec superset of that base SKU, so the borrowed value is a LOWER bound and the resulting `$/ns` an UPPER
    bound. Everything else is unbenched and excluded from ranking."""
    k = _model_key(gpu_name)
    if k is None:
        return None
    if k in MEASURED_NS_PER_DAY_84K:
        return k
    return CONSERVATIVE_ALIASES[k][0]


def throughput_provenance(gpu_name):
    """('measured'|'conservative_alias'|'unbenched', base_card, note) for this offer's throughput. PURE.

    Exists so that no caller can report a `$/ns` without being able to say where its ns/h came from. A
    conservative alias is a DERIVED figure with a known one-sided direction (it can only overstate cost), and
    the whole reason the allow-list is safe is that everybody downstream can see it is an alias."""
    k = _model_key(gpu_name)
    if k in MEASURED_NS_PER_DAY_84K:
        return "measured", k, "validated 2026-07-24 grid @84,534 particles"
    if k in CONSERVATIVE_ALIASES:
        base, why = CONSERVATIVE_ALIASES[k]
        return ("conservative_alias", base,
                f"DERIVED lower bound: borrows {base} because {why}; true $/ns can only be LOWER")
    return "unbenched", None, "never benched — excluded from $/ns ranking rather than guessed at"


def ns_per_hour(gpu_name):
    """ns/hr for this card **on the 84,534-particle water-box bench** (`BENCH_PROTOCOL`), or None if it may
    not borrow a benched figure. PURE.

    ⚠ THE DOCSTRING USED TO SAY "at the ternary system size" AND THAT WAS FALSE (corrected 2026-07-31). No
    caller passes a system, and none ever has: this is a REFERENCE-GPU index, not a physical rate for any
    lane's assembly. RUNG 5a-KS is 147,788 particles as a 12-window HREX RBFE; the bench is 84,534 particles
    of plain single-replica MD. Multiplying a `$/ns` from here by a leg's REAL nanosecond target gives a
    wrong dollar figure — the ladder never does that (`rung_ns_per_unit` is in the same reference unit, which
    is why the two cancel), but a reader of a board row easily might.

    For a `CONSERVATIVE_ALIASES` entry this is a LOWER BOUND, not a measurement — ask `throughput_provenance`
    before quoting it as a rate."""
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


def restart_overhead_h(checkpoint_interval_h, reload_h=0.0):
    """Work lost per preemption. Uniform arrival within a checkpoint interval => half of it on average.

    `reload_h` is the image-reload cost, and it defaults to 0.0 for the OUTBID path only. F3 is right that a
    paused-and-resumed box keeps its disk, so that path pays no reload — and the ~20-minute reload which once
    justified `x1.9` really was self-inflicted by a reaper deleting paused boxes.

    ⚠ BUT THAT IS NOT THE ONLY PATH, and on 2026-07-25 it was not the common one. A host that answers
    `resources_unavailable` cannot be resumed at any bid; the leg has to be re-rented elsewhere and pays a
    full multi-GB pull. Observed repeatedly on the 5a-KS run (see
    `research/compute/vast-churn-observations-2026-07-25.md`). For that mode pass the real reload — ~0.1-0.25 h
    on the hosts seen — instead of taking the default.

    This matters to the BID CONCLUSION, not just to a cost readout: `premium_breakeven_dlam_db` asks how fast
    the hazard must fall with the bid for a premium to pay, and that threshold moves with how expensive a
    preemption is. Pricing every preemption as reload-free makes preemption look cheap, which makes a premium
    look unjustified. PURE."""
    return max(0.0, float(checkpoint_interval_h)) / 2.0 + max(0.0, float(reload_h))


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
    # If set (0..1), an offer whose P(clean run of min_uninterrupted_h) falls below this is EXCLUDED, not just
    # noted. Without it, ranking on $/ns alone hands a continuity-sensitive leg to the cheapest — and therefore
    # usually slowest — card, which is exactly backwards: a 3090 needs 2.10x the wall clock, so it is 2.10x
    # more exposed. Default 0 = no constraint, because most legs checkpoint and genuinely do not care.
    min_clean_run_prob: float = 0.0
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
    clean_run_prob: float = None
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
    clean_p = None
    if job.min_uninterrupted_h > 0 and job.hazard_per_h > 0:
        clean_p = math.exp(-job.hazard_per_h * job.min_uninterrupted_h * (REFERENCE_NS_PER_H / nsph))
    if ondemand_base:
        be = breakeven_hazard_vs_ondemand(bid, ondemand_base, s, job.restart_h, job.downtime_h)
        if be == 0.0:
            notes.append("on-demand is cheaper here even with zero preemptions — buy on-demand")
    else:
        be = None
    if clean_p is not None:
        # The requirement is stated in reference-card hours; on THIS card the same leg occupies
        # t = t_ref * (theta_ref / theta), so a slow card needs a proportionally longer clean window.
        t = job.min_uninterrupted_h * (REFERENCE_NS_PER_H / nsph)
        if clean_p < max(0.5, job.min_clean_run_prob):
            notes.append(f"leg needs {t:.1f} h uninterrupted on this card ({job.min_uninterrupted_h:.1f} h on "
                         f"the reference card); P(clean run) ~ {clean_p:.2f} — consider on-demand for this leg")
    return OfferScore(
        offer_id=offer.get("id"), machine_id=offer.get("machine_id"),
        gpu_name=offer.get("gpu_name"), card=card_of(offer.get("gpu_name")),
        min_bid=round(floor, 5), bid=bid, storage_usd_h=round(s, 5), ns_per_h=round(nsph, 3),
        usd_per_ns=round(upn, 6), usd_per_reference_gpu_h=round(upn * REFERENCE_NS_PER_H, 5),
        ondemand_base=ondemand_base, breakeven_hazard=(None if be is None else round(be, 3)), notes=notes,
        clean_run_prob=(None if clean_p is None else round(clean_p, 4)))


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
        if s is None:
            continue
        # A continuity constraint is a CONSTRAINT, not a cost: ranking on $/ns alone would hand a leg that must
        # run through to the cheapest and therefore slowest card. Excluded here rather than merely noted.
        if job.min_clean_run_prob > 0 and s.clean_run_prob is not None \
                and s.clean_run_prob < job.min_clean_run_prob:
            continue
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


# =============================================================================================================
# CLI — planning numbers and a repriced ladder, from a market snapshot
# =============================================================================================================
# The point of this entry point is that every cost figure in pricing.md / nr4a3-program-map.md can be REGENERATED rather
# than hand-carried. Hand-carried numbers are how the repo ended up quoting "$12-26" for a fan-out whose own
# footnote said "$91-101" three lines later.

# GPU-hours per stage, expressed on the REFERENCE card. These are the repo's own measured/derived work
# estimates (pricing.md section B/C); this module reprices them, it does not re-estimate them.
# ENDPOINT-MD LEG, in reference-card hours, BACKED OUT OF THE ONE COMPLETED MULTI-LEG MEASUREMENT: the NR-V04
# covalent panel ran 18 legs on RTX 3090s at a realised dph_total of ~$0.10-0.21/hr for a mean ~$0.43/leg, i.e.
# ~2.9 h/leg on a 3090. Divided by the measured 2.102x card ratio that is ~1.38 reference GPU-hours per leg.
# Derived this way rather than from a 466k-atom throughput number because the only validated bench is at 84,534
# particles — the 175.6 / 72.5 ns/day figures at 444k come from the withdrawn grid and must not be used.
ENDPOINT_MD_REF_GPU_H_PER_LEG = 1.38

# ---------------------------------------------------------------------------------------------------
# ★ TERNARY LEG LENGTH CORRECTED 2026-07-25 (Lane 4), verified against rbfe_spot_driver source.
#
# Every 2 fs ternary figure below was previously derived from a 2400-iteration leg ("400 equil + 2000
# production at 2.5 ps/iter"). That 400 assumes the warmup runs at the PRODUCTION timestep. It does not:
# `rbfe_spot_driver` derives warmup_iters from the WARMUP integrator (`_iters_from_time`, and the comment
# there says so outright -- "more iters at a smaller dt"), and the as-run protocol overrides the warmup to
# 1.0 fs. So 1 ns of equilibration is 1e6 steps / 1250 steps-per-iteration = **800** warmup iterations, not
# 400, each costing the SAME 1250 force evaluations as a production iteration.
#
#   as-run 2 fs leg = 800 warmup + 2000 production = 2800 equal-cost iterations, not 2400  (+16.7%)
#
# Pricing at 2400 understated every 2 fs ternary stage by ~17%. The measured ~16 s/iter is unchanged --
# this is arithmetic on the existing rate, not a new measurement.
TERNARY_LEG_ITER_CORRECTION = 2800.0 / 2400.0  # 1.1667

# ★ And the 4 fs saving is 1.56x, NOT 2x. Halving the timestep halves the force evaluations only in the
# phase whose dt changed. The warmup is pinned at 1 fs either way, so per replica:
#     2 fs: 1.0e6 (warmup) + 2.5e6 (production) = 3.5e6 steps
#     4 fs: 1.0e6 (warmup) + 1.25e6 (production) = 2.25e6 steps
# ratio 2.25/3.5 = 0.643. A "2x cheaper at 4 fs" claim overstates the saving by ~36%.
TERNARY_4FS_CONVERSION = 2.25 / 3.5  # 0.643

def _t(lo, hi):
    """A 2 fs ternary stage, corrected from the 2400-iteration basis to the as-run 2800."""
    return (round(lo * TERNARY_LEG_ITER_CORRECTION, 1), round(hi * TERNARY_LEG_ITER_CORRECTION, 1))


LADDER_REFERENCE_GPU_H = {
    "step1_pilot (1-2 RBFE edges)": (13.7, 27.4),
    "step1_fanout (19 RBFE edges @ ~13.7 GPU-h)": (260.0, 260.0),
    "valB_mini (1 ternary edge, 3 replicas)": _t(56.0, 72.0),
    "valB_full (2-3 ternary edges + CRL-MD)": _t(112.0, 216.0),
    "nrv04_retrospective (3 ternary legs + shared binary/solvent)": _t(84.0, 216.0),
    # the 4 fs edge is the corrected 2 fs edge x 0.643, not x 0.5
    "ternary_4fs_recalibration (1 matched edge)": (round(_t(56.0, 72.0)[0] * TERNARY_4FS_CONVERSION, 1),
                                                  round(_t(56.0, 72.0)[1] * TERNARY_4FS_CONVERSION, 1)),
    # ★ 2026-07-30: FOUR ternary legs, not two — n = 2 SEEDS PER ARM (trimcrae go, STRATEGY Open decision 11).
    # At one seed per arm S has NO replicate SD and resolves only the TOP of its own designed 0.5-1.5 kcal/mol
    # effect (valb_failure_propagation.s_error_bar_scope), so the PRE-REGISTERED LIKELY OUTCOME — a null —
    # would have been uninterpretable, exactly as valB_mini's n=1 was. Doubling the leg count is what buys a
    # readable bound. The per-leg basis is unchanged; only the COUNT moved, which is why this is a GPU-hour
    # edit and not a reprice.
    "5a-KS primary (ligand-side double difference, 2 seeds x 2 arms)": _t(56.0, 288.0),
    "5c ensemble refinement (24-200 endpoint-MD legs)": (24 * ENDPOINT_MD_REF_GPU_H_PER_LEG,
                                                        200 * ENDPOINT_MD_REF_GPU_H_PER_LEG),
    "local within-basin FEP (3-6 ternary comparisons)": _t(56.0, 260.0),
}


def _main(argv=None):
    import argparse
    import json as _json
    ap = argparse.ArgumentParser(description="Vast planning numbers + repriced ladder from a market snapshot")
    ap.add_argument("--offers", default="vast-market-offers-raw.json",
                    help="vast_market_intel.py output (raw offers)")
    ap.add_argument("--disk-gb", type=float, default=40.0)
    ap.add_argument("--checkpoint-h", type=float, default=0.5)
    ap.add_argument("--hazard", type=float, default=DEFAULT_HAZARD_PER_H)
    ap.add_argument("--card", default="", help="restrict to one card, e.g. RTX4090 (default: all benched)")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--json-out", default="")
    a = ap.parse_args(argv)

    with open(a.offers) as f:
        blob = _json.load(f)
    raw = blob.get("offers", blob)
    bid_offers = raw.get("bid", [])
    od = {str(o["machine_id"]): float(o["dph_base"]) for o in raw.get("on-demand", [])
          if o.get("machine_id") and o.get("dph_base")}
    if a.card:
        bid_offers = [o for o in bid_offers if card_of(o.get("gpu_name")) == a.card.upper()]

    job = JobProfile(disk_gb=a.disk_gb, checkpoint_interval_h=a.checkpoint_h, hazard_per_h=a.hazard)
    ranked = rank_offers(bid_offers, job, od)
    summ = summarise_market(ranked, top=a.top)
    if not summ:
        print("no qualifying offers")
        return 1

    key_best_k = f"best{min(a.top, len(ranked))}_mean_usd_per_reference_gpu_h"
    plan = summ[key_best_k]                       # what a policy that always takes a top-k offer achieves
    lo = summ["best_usd_per_reference_gpu_h"]     # the cheap tail, if we land on it
    hi = summ["median_usd_per_reference_gpu_h"]   # what ignoring the ranking costs

    print(f"=== MARKET ({len(ranked)} qualifying offers{', ' + a.card if a.card else ''}) ===")
    for k, v in summ.items():
        print(f"  {k:44s} {v}")
    print(f"\n=== PLANNING RATE: ${plan:.4f} per reference GPU-hour "
          f"(range ${lo:.4f} best offer .. ${hi:.4f} median) ===")
    print(f"\n{'stage':58s} {'ref GPU-h':>14} {'plan $':>9} {'range $':>16}")
    tot = [0.0, 0.0, 0.0]
    for name, (g_lo, g_hi) in LADDER_REFERENCE_GPU_H.items():
        mid = (g_lo + g_hi) / 2
        tot[0] += mid * plan
        tot[1] += g_lo * lo
        tot[2] += g_hi * hi
        print(f"{name:58s} {g_lo:6.0f}-{g_hi:<7.0f} {mid * plan:9.2f} "
              f"{g_lo * lo:7.2f}-{g_hi * hi:<8.2f}")
    print(f"{'TOTAL (priceable ladder stages)':58s} {'':>14} {tot[0]:9.2f} {tot[1]:7.2f}-{tot[2]:<8.2f}")
    print("\nNOTE: reference GPU-hours are the repo's own work estimates (pricing.md B/C) — this reprices "
          "them, it does not re-derive them. The hazard is a prior; the ranking is stable in it.")
    if a.json_out:
        with open(a.json_out, "w") as f:
            _json.dump({"market": summ, "plan_usd_per_reference_gpu_h": plan,
                        "range_usd_per_reference_gpu_h": [lo, hi],
                        "ladder": {k: {"ref_gpu_h": v, "plan_usd": (v[0] + v[1]) / 2 * plan,
                                       "range_usd": [v[0] * lo, v[1] * hi]}
                                   for k, v in LADDER_REFERENCE_GPU_H.items()},
                        "total_plan_usd": tot[0], "total_range_usd": [tot[1], tot[2]]}, f, indent=1)
        print(f"wrote {a.json_out}")
    return 0


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(_main())
