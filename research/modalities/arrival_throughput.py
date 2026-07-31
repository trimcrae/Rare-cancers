#!/usr/bin/env python3
"""MEASURE WHAT A HOST ACTUALLY DELIVERS, AND DROP THE ONES THAT CANNOT BANK. PURE decision logic.

★★ WHY THIS AND NOT A BETTER THROUGHPUT TABLE (2026-07-31). The obvious response to "our `$/ns` uses a card
table" is to measure the table on the real assembly. The lane's own data says that answers the wrong question:
**host variance dwarfs card identity.** Thirteen paired RTX 3090-vs-RTX 4090 measurements taken within 60
minutes of each other, on one 147,788-particle system, span **0.50-2.67x** against a table prediction of
**1.745x** — and in 6 of the 13 the "slow" card won. A better table cannot fix selection when the spread
*within* a card is larger than the gap *between* cards. `vast_cost_model.verify_and_abandon_threshold` already
said so in prose — *"benchmark briefly on arrival and drop a bad draw"* — and was **wired to nothing**:
referenced only by its own unit tests.

★ THE ACTION TEST IS TIME, NOT DOLLARS, AND THAT IS DELIBERATE.
A host is a guaranteed loss when it cannot reach its next commit boundary inside a typical rental:

    seconds_to_next_commit = iterations_remaining_to_the_boundary x measured_s_per_iter

If that exceeds the session length we actually get, the host will bank **nothing** — it bills and commits
zero, which is precisely the 25 % of today's rentals that died before their first checkpoint. This test needs
no card table, no throughput bench and no unit conversion, so it is immune to every confound above. Measured
session distribution (27 rentals, 4 legs, 6.73 h): median <= 1.00 h, 25 % under 30 min.

★ AND THE DOLLAR VIEW, BECAUSE trimcrae ASKED WHETHER THIS IS THE BUY LINE AT A DIFFERENT TIME. **It is.**
    quoted   $/ns = billed $/hr / TABLE ns/h        <- what the gate checked before renting
    realised $/ns = billed $/hr / DELIVERED ns/h    <- what we are actually paying
Same quantity, different throughput term, so they share a home: the threshold is
`inflight_usd_per_ns.APPROVED_USD_PER_NS`, imported and never re-typed. This is the `bid_floor_mult` defect
one layer out — there we scored a price we would not pay, here we score a throughput we do not get.

⚠ THE UNIT TRAP, AND WHY `realised_usd_per_ns` IS A **RATIO** REBASE RATHER THAN A FRESH DIVISION. The buy
line lives in REFERENCE-GPU nanoseconds (the 84,534-particle water-box bench — STRATEGY Appendix A 61).
Dividing dollars by nanoseconds of a 147,788-particle HREX assembly would produce a number in a different
unit and compare it to that line, which is the exact error row 61 registers. So the realised figure is the
QUOTED figure scaled by the measured slowdown — dimensionless x index units — and stays comparable.

⛔ WHAT MAY NEVER CONDEMN A HOST, and each one has cost this repo real money:
  * **GPU idleness.** CLAUDE.md §6's inviolable rule. A legitimately CPU-bound staging phase looks identical
    to a dead one, so no GPU-side signal is read here at ALL — `tests/test_arrival_throughput.py` asserts the
    forbidden identifiers appear nowhere in this module's code.
  * **A missing measurement.** No `[timing]` line means the leg has not started integrating — that is an
    ABSENT reading, not a slow one (§4), and it returns `WATCHING`.
  * **One noisy sample.** `measured_s_per_iter` reports the last COMPLETED interval, so a single crossing is
    one interval, not one iteration; `MIN_SAMPLES` still requires the evidence to exist before acting.
The single fact that licenses a verdict is that MD is running and its own timing line says it is too slow.
"""
from __future__ import annotations

import os

from inflight_usd_per_ns import APPROVED_USD_PER_NS

# The session length a host must beat to be worth keeping. MEASURED, not chosen: 27 rentals across 4 legs in
# 6.73 h on 2026-07-31 gave a median session of <= 1.00 h — and that is an UPPER bound, because the
# reconstruction measures rental-to-rental and so includes the hostless gap. Using the median rather than the
# mean because the distribution is right-skewed (max 270 min) and the mean would flatter a bad host.
SESSION_MEDIAN_S = float(os.environ.get("TVAST_SESSION_MEDIAN_S") or 3600.0)

# How much of that session a host may spend reaching its next commit before it is a guaranteed loss. 1.0 would
# condemn a host that banks on the very last second of a median session; the margin makes the test "will
# comfortably bank" rather than "might just".
COMMIT_MARGIN = float(os.environ.get("TVAST_COMMIT_MARGIN") or 0.80)

# Evidence floor. `measured_s_per_iter` already returns the last COMPLETED interval (tens of iterations), so
# one reading is not one noisy iteration — but requiring the reading to EXIST is what keeps a cold host in
# WATCHING instead of being condemned for having produced nothing yet.
MIN_SAMPLES = 1

WATCHING, KEEP, ABANDON = "WATCHING", "KEEP", "ABANDON"


def seconds_to_next_commit(iteration, interval, s_per_iter):
    """Wall seconds until this host reaches its next checkpoint boundary. PURE, None if unknowable.

    The boundary is the next multiple of `interval` STRICTLY after `iteration` — a leg sitting exactly on a
    boundary has just committed and owes a full interval, not zero."""
    try:
        it, iv, spi = int(iteration or 0), int(interval or 0), float(s_per_iter or 0)
    except (TypeError, ValueError):
        return None
    if iv <= 0 or spi <= 0:
        return None
    return ((it // iv + 1) * iv - it) * spi


def realised_usd_per_ns(quoted_usd_per_ns, measured_s_per_iter, expected_s_per_iter):
    """The quoted index `$/ns` rebased onto what this host DELIVERS. PURE, None if unknowable.

    A RATIO rebase, never a fresh division — see the unit trap in the module docstring. `expected` is the rate
    the quote implicitly assumed; `measured` is what arrived; the quote scales by their ratio."""
    try:
        q, m, e = float(quoted_usd_per_ns), float(measured_s_per_iter), float(expected_s_per_iter)
    except (TypeError, ValueError):
        return None
    if q <= 0 or m <= 0 or e <= 0:
        return None
    return q * (m / e)


# Provenance of an expectation. `CARD` is like-for-like and may license a $/ns comparison; `POOLED` is the
# arm median across a mixed fleet and MAY NOT — see `expected_s_per_iter`.
PROV_CARD, PROV_POOLED, PROV_NONE = "card", "pooled", "none"


def expected_s_per_iter(arm, timestep_fs, card=None, rates=None):
    """(seconds, provenance_kind, note) this arm should take per iteration, from the lane's OWN measured table.

    ★★ THE PER-CARD FIGURE IS PREFERRED AND THAT IS LOAD-BEARING, NOT TIDINESS (2026-07-31). This function
    documented a per-card preference from the day it was written and IMPLEMENTED only the pooled arm median,
    which made every below-median card look broken by construction: the table's own RTX 4090/RTX 3090 ratio
    is 1.745, so a healthy 3090 reads ~1.75x "slower than expected". Caught on the live board within minutes
    of the guard shipping — two 3090s flagged at 1.86x and 2.00x, which rebased on their own card are 1.07x
    and 1.15x. Shipping report-only is what turned that into an observation instead of a reaped fleet.

    `None` when the timestep was never measured: an unmeasured expectation cannot condemn anything."""
    if rates is None and card:
        try:
            from ternary_vast_launch import arm_card_rate
            v = arm_card_rate(timestep_fs, arm, card)
            if v:
                return float(v), PROV_CARD, f"measured {arm} rate for {card} at {timestep_fs} fs"
        except Exception:  # noqa: BLE001 — fall through to the pooled figure
            pass
    if rates is None:
        try:
            from ternary_vast_launch import arm_iteration_rates
            rates = arm_iteration_rates(timestep_fs)
        except Exception:  # noqa: BLE001 — no table, no verdict
            return None, PROV_NONE, "no measured arm-rate table"
    v = (rates or {}).get(arm)
    if not v:
        return None, PROV_NONE, f"no measured rate for arm={arm} at {timestep_fs} fs"
    return (float(v), PROV_POOLED,
            f"arm median for {arm} at {timestep_fs} fs — POOLED ACROSS CARDS, so a slowdown against it is "
            f"partly the card and may not be read as this host underperforming")


def verdict(measured_s_per_iter, expected_s_per_iter_s, iteration=None, interval=None,
            quoted_usd_per_ns=None, session_s=None, margin=None, buy_line=None,
            provenance=PROV_CARD):
    """Whether to keep paying for this host. PURE. Returns a dict carrying every number behind the call.

    ⚠ THE ORDER OF THE GUARDS IS THE SAFETY ARGUMENT. Absence of evidence is checked FIRST and always returns
    WATCHING, so no path can reach ABANDON without a rate this host actually printed."""
    out = {"measured_s_per_iter": (measured_s_per_iter if isinstance(measured_s_per_iter, (int, float))
                                   else None),
           "expected_s_per_iter": expected_s_per_iter_s,
           "seconds_to_next_commit": None, "session_budget_s": None,
           "realised_usd_per_ns": None, "slowdown_vs_expected": None, "provenance": provenance,
           "buy_line_usd_per_ns": float(buy_line if buy_line is not None else APPROVED_USD_PER_NS)}

    try:
        _m = float(measured_s_per_iter)
    except (TypeError, ValueError):
        _m = 0.0
    if not _m or _m <= 0:
        out.update({"verdict": WATCHING,
                    "why": "no measured rate yet — the leg has not printed a completed timing interval, "
                           "which is an ABSENT reading and never a slow one (CLAUDE.md §4)"})
        return out

    sess = float(session_s if session_s is not None else SESSION_MEDIAN_S)
    marg = float(margin if margin is not None else COMMIT_MARGIN)
    budget = sess * marg
    out["session_budget_s"] = round(budget, 1)

    if expected_s_per_iter_s:
        out["slowdown_vs_expected"] = round(_m / float(expected_s_per_iter_s), 2)
        out["realised_usd_per_ns"] = realised_usd_per_ns(
            quoted_usd_per_ns, _m, expected_s_per_iter_s)

    tnc = seconds_to_next_commit(iteration, interval, _m)
    out["seconds_to_next_commit"] = None if tnc is None else round(tnc, 1)

    # THE ACTION TEST — time, not dollars. Table-free and therefore immune to the card-ratio question.
    if tnc is not None and tnc > budget:
        out.update({"verdict": ABANDON,
                    "why": ("cannot bank: %.1f min to its next commit boundary at a MEASURED %.1f s/iter, "
                            "against a %.1f min budget (%.0f%% of the %.1f min median session). A host that "
                            "cannot reach a boundary bills and commits nothing."
                            % (tnc / 60.0, _m, budget / 60.0, marg * 100,
                               sess / 60.0))})
        return out

    # THE DOLLAR VIEW — the buy line, evaluated on delivered throughput instead of quoted. Reported whenever
    # it can be computed; it does not trigger the action on its own, because a host may be over the line and
    # still bank real work, and abandoning that costs a ~28 min cold start for a strictly worse trade.
    r = out["realised_usd_per_ns"]
    if r is not None and provenance != PROV_CARD:
        # A pooled expectation cannot distinguish "this host is slow" from "this card is slower than the
        # fleet median", and the second is not a defect. Report the rate, withhold the verdict.
        out.update({"verdict": KEEP,
                    "why": "delivering %.1f s/iter; no per-card expectation for this card, so the realised "
                           "$/ns is not comparable and no slowdown verdict is offered"
                           % float(measured_s_per_iter)})
        return out
    if r is not None and r >= out["buy_line_usd_per_ns"]:
        out.update({"verdict": KEEP,
                    "why": ("⚠ realised $%.6f/ns is over the $%.6f/ns buy line (%.2fx slower than expected), "
                            "but it WILL reach its next boundary in %.1f min — banking beats a cold start, so "
                            "this is reported, not acted on."
                            % (r, out["buy_line_usd_per_ns"], out["slowdown_vs_expected"],
                               (tnc or 0) / 60.0))})
        return out

    out.update({"verdict": KEEP, "why": "delivering acceptably"})
    return out


def cell(v):
    """The board cell for a verdict. Terse — this column sits beside an already-wide `$/ns`."""
    if not v or v.get("verdict") == WATCHING:
        return "—"
    if v["verdict"] == ABANDON:
        return "⛔ CANNOT BANK %.1f s/iter (%.0f min to commit)" % (
            v["measured_s_per_iter"], (v["seconds_to_next_commit"] or 0) / 60.0)
    if v.get("provenance") == PROV_CARD and v.get("realised_usd_per_ns") \
            and v["realised_usd_per_ns"] >= v["buy_line_usd_per_ns"]:
        return "⚠ %.1f s/iter · realised $%.5f/ns (%.2fx expected)" % (
            v["measured_s_per_iter"], v["realised_usd_per_ns"], v["slowdown_vs_expected"] or 0)
    return "%.1f s/iter" % v["measured_s_per_iter"]
