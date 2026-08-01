#!/usr/bin/env python3
"""MEASURE WHAT A HOST ACTUALLY DELIVERS, AND DROP THE ONES THAT CANNOT BANK. PURE decision logic.

★★ THE COLD START IS NOT THE PROBLEM, AND I SAID IT WAS — MEASURED AND RETRACTED (2026-07-31, 6:47 PM ET).

I reported that "legs are not failing because MD is slow; they die during the ~28 min cold start, before MD
begins." **The mechanism in that sentence is wrong.** Reading `phase.txt`'s own timestamp against the log's
`[tvast] <utc> start` on all four live legs:

    container start -> md-running:  0.3, 0.4, 0.5, 0.6 min   (median 0.4 min)

MD begins within ~30 SECONDS of the container starting, because all three caches are hitting (23 of 27
attempts). The `ternary-4fs-vast-findings.md` budget predicted exactly this — "~15 min of that is cached and
will not repeat" — and the cached line items (staging ~8 min, pre-equilibration 456 s, and the ~460 s
solvate+parameterise, which is RESTORED not rebuilt) really have gone to nearly zero.

WHAT THE "~28 min" ACTUALLY IS: **time to the first COMMIT**, which is dominated by one checkpoint interval
of MD, not by setup. 64 warmup iterations x the measured rate:

    leg          staging   s/iter   64 x s/iter   = first commit
    nr4a3_r0       0.6 m     33.5      35.7 m         36.4 m
    nr4a3_r1       0.5 m     31.1      33.1 m         33.6 m
    nr4a1_r0       0.3 m     18.3      19.5 m         19.8 m
    nr4a1_r1       0.4 m     17.8      19.0 m         19.4 m

(plus the ~2.8 min image pull, which happens BEFORE the log's first line and is not in these figures.)

⚠ WHY THE CORRECTION CHANGES THE RECOMMENDATION. A staging problem would be fixed by faster staging or a
bigger host; this is not one. The lever is the CHECKPOINT INTERVAL — halving it halves time-to-first-commit
directly — and that is a change for NEW legs only, because the interval is fixed when the .nc is created
(`rbfe_spot_checkpoint.effective_interval`; `tests/test_ckpt_cadence_is_new_legs_only.py`). It also explains
why measure-on-arrival would have condemned nobody: the MD rate is fine, the INTERVAL is long.

⚠ NOT MEASURED, AND NOT CLAIMED: minimisation and the setup RESTORE both sit inside `md-running`, before the
first `[timing]` line, so the figures above bound them together rather than separating them. The `[spot-driver]
restore: <label> took Ns` instrumentation and the timestamped phase marks will separate them on the next
re-placement; until one lands, "0.4 min of staging" is a statement about the SHELL phases only.


★★ A SYSTEM THIS TABLE HAS NEVER MEASURED CANNOT BE "SLOWER THAN EXPECTED" — MEASURED AND FIXED
(trimcrae, 2026-08-01, 9:47 AM ET): *"Don't get too hung up on expected vs actual $/ns. If it's a bigger
molecule than our estimates are based on, it's gonna be more expensive. It's more important that we rank
based on relative price per ns than actual."*

He is right and the arithmetic says why. Every offer is scored against the SAME throughput table, so a
systematic offset cancels out of a RANKING and the quoted `$/ns` stays a valid comparator whatever the
assembly costs. **It stops cancelling the moment a REALISED rate is compared against a QUOTED prediction** —
which is exactly what `realised_usd_per_ns` does. A bigger system costs more seconds per iteration by
ARITHMETIC, and reporting that arithmetic as drift is crying wolf.

⚠ THE PROVENANCE HOLE, READ OFF THE ARTIFACT RATHER THAN ASSUMED (`ternary-arm-iteration-rates.json`,
generated 2026-08-01, 16 leg records). Grouping each figure's OWN contributing legs by the system token in
their unit ids:

    dt   arm      figure   contributing systems          per-card composition
    2.0  binary    17.0    vhl x2                        3090 vhl · 5090 vhl
    2.0  ternary   18.2    vhl x3                        4080S vhl · 4090 vhl · 5090 vhl
    4.0  binary    10.9    vhl x3                        4080S vhl · 4090 vhl · 5090 vhl
    4.0  solvent    1.7    (no system token) x1          4090 —
    4.0  ternary   17.0    nr4a3 x3 + vhl x4             3090 nr4a3+vhl · 4090 nr4a3+vhl · 5090 vhl

Two facts, both load-bearing. **(1) There is NO `nr4a1` leg anywhere in the table**, yet `nr4a1_r0`/`nr4a1_r1`
are live on this lane — so every `nr4a1` row was graded against a system it has never been. **(2) The 4 fs
ternary figure is POOLED ACROSS TWO SYSTEMS on every card but the 5090**, so even an `nr4a3` row is graded
against a median half-composed of a different assembly. `ternary_arm_rates`'s `_never_pool` already forbids
pooling across system SIZE and its `pooled_across_systems` flag reads **false** here, because 141,740-149,308
particles collapse into one bucket at the 15 % relative tolerance. **SIZE CANNOT SEE THIS. IDENTITY CAN** —
which is why the check below is on the system TOKEN in the unit id and not on a particle count.

WHAT CHANGED, AND WHAT DELIBERATELY DID NOT.
  * A figure that cannot be shown to describe THIS leg's own assembly now returns `PROV_OFFSYSTEM`, and that
    provenance asserts **neither drift nor the buy line** — it states the delivered s/iter and says what the
    expectation was actually measured on. Structurally it is the pooled-across-CARDS branch one axis over.
  * ⛔ **THE PURCHASE GATE IS UNTOUCHED.** `inflight_usd_per_ns.APPROVED_USD_PER_NS` binds on the **quoted**
    rate at the moment of renting, where the offset cancels; this file is a POST-HOC readout and always was.
    Nothing here changes what the lane is willing to buy.
  * ⛔ **THE TIME TEST IS UNTOUCHED**, and it is the only test that ACTS. `seconds_to_next_commit` needs no
    table, no card and no expectation, so the host-to-host spread that actually matters (0.50-2.67x on ONE
    system, against a 1.745x card prediction) is measured exactly as before — and now without a systematic
    system offset drowning it.
⚠ WHAT IS NOT CLOSED, AND IT IS ONE ARGUMENT WIDE. `ternary_vast_launch.collect` calls
`expected_s_per_iter(arm_of_leg(uid), dt, card=...)` without the unit id, so the live board gets the weaker
of the two rules below — "this figure pools several systems, so it describes none of them". That covers 4 fs
ternary on the 3090 and 4090 (both `nr4a3`+`vhl`) and therefore every live `nr4a1` row on those cards. It
does NOT cover the 5090, whose 4 fs ternary figure is `vhl`-only: single-system, wrong system, and without
the leg's id nothing here can tell. Passing `unit_id=_b["uid"]` at that call site closes it on every card;
the exact check is built and pinned by `tests/test_arrival_throughput.py`, which fails when the gap shuts.

SUPERSEDED, RETAINED (CLAUDE.md §1.2): until this ruling, any per-card expectation licensed a realised-$/ns
comparison, so `nr4a1 r1` — quoted $0.00412/ns, 1.21x basis — printed `⚠ realised $0.00889/ns`, i.e. ~2.6x
"drift" on a lane where an offset is arithmetic. That reading no longer stands and must not be quoted.


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
import re

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


# Provenance of an expectation, and the ONLY one that may license a $/ns comparison is `CARD`.
#   CARD       — measured on THIS card AND on THIS leg's own molecular system. Like-for-like.
#   POOLED     — the arm median across a mixed FLEET; a slowdown against it is partly the card (2026-07-31).
#   OFFSYSTEM  — measured on a DIFFERENT ASSEMBLY, or pooled across several. A slowdown against it is partly
#                the molecule, which is arithmetic and not drift (trimcrae, 2026-08-01 — module docstring).
#   NONE       — no expectation at all.
PROV_CARD, PROV_POOLED, PROV_NONE = "card", "pooled", "none"
PROV_OFFSYSTEM = "off_system"


def licenses_dollar_comparison(provenance):
    """May an expectation of this provenance be compared against the buy line? PURE.

    ONE HOME for that question (CLAUDE.md §1). `verdict` and `cell` each used to spell it out as
    `provenance == PROV_CARD`, which is two copies of one rule and free to drift the moment a third
    provenance kind appears — which is exactly what `PROV_OFFSYSTEM` is."""
    return provenance == PROV_CARD


# The molecular system token in a ternary-lane unit id: `<edge>__<arm>_<system>_r<N>_dt<X>fs_wu<Y>_<mode>`,
# e.g. `5aks_d0_to_d__ternary_nr4a1_r0_dt4.0fs_wu1.0_5aks` -> `nr4a1`. The `solvent` arm carries no system
# token (`..__solvent_r0_dt4.0fs..`) and correctly yields None.
_UNIT_SYSTEM_RE = re.compile(r"__[a-z]+_([a-z0-9]+)_r\d+_dt")
# The same id truncated to a leg (`5aks_d0_to_d__ternary_nr4a3`), which is what `leg_id` records carry.
_LEG_SYSTEM_RE = re.compile(r"__[a-z]+_([a-z0-9]+)$")

# The label a leg with no system token in its id is grouped under, so "one system, and it is the unnamed one"
# stays distinguishable from "no legs at all". NOT folded into a neighbour: guessing which assembly an
# unlabelled leg ran is the same guess that produced the pooled figure in the first place.
SYSTEM_UNSPECIFIED = "unspecified"


def system_of_unit(unit_id):
    """The molecular system a unit id names (`nr4a1`, `nr4a3`, `vhl`), or None. PURE.

    ⚠ IDENTITY, NOT SIZE, AND THAT IS THE WHOLE POINT. `ternary_arm_rates.system_buckets` already clusters
    legs by particle count, and on this lane it CANNOT separate these systems: the 4 fs ternary legs span
    141,740-149,308 particles, which is one bucket at the 15 % relative tolerance, so `pooled_across_systems`
    reads false on a figure pooled across `nr4a3` and `vhl`. Two different assemblies of nearly equal size are
    still two different assemblies."""
    if not unit_id:
        return None
    m = _UNIT_SYSTEM_RE.search(unit_id) or _LEG_SYSTEM_RE.search(unit_id)
    return m.group(1) if m else None


def contributing_systems(timestep_fs, arm, card=None, path=None):
    """{system: n_legs} that PRODUCED the measured figure for this (timestep, arm[, card]), or {} if the
    composition cannot be read. PURE apart from one cached file read.

    ⚠ PROVENANCE ONLY — THIS FUNCTION NEVER RETURNS A RATE. The rate has one home and it is
    `ternary_vast_launch.arm_card_rate` / `arm_iteration_rates` (CLAUDE.md §1); all that is read here is WHICH
    LEGS went into the number those functions return, off the same document, through the same cache, so a
    regenerated artifact moves both together and neither can describe the other's contents.

    `source_phase` is READ from the entry rather than re-derived: `ternary_arm_rates.aggregate` picks
    production-over-warmup once per (timestep, arm) and builds `by_gpu` from that same choice, so a leg that
    measured only the other phase contributed nothing and must not be counted as evidence that it did.

    ⚠ AN EMPTY RETURN IS AN ABSENT READING, NOT A READING OF ABSENCE (CLAUDE.md §4a). `{}` means the
    composition could not be established — never "this figure has no legs behind it" — and callers must
    therefore leave the provenance they already had rather than downgrading it."""
    try:
        import ternary_vast_launch as tv
        p = path or tv._ARM_RATES_PATH
        if p not in tv._ARM_RATES_CACHE:
            tv.arm_iteration_rates(timestep_fs, path=p)   # populate via the module's OWN reader, not a 2nd one
        doc = tv._ARM_RATES_CACHE.get(p) or {}
        entry = ((doc.get("rates") or {}).get(f"{float(timestep_fs):.1f}") or {}).get(arm) or {}
        legs, src = doc.get("legs") or [], entry.get("source_phase")
        if not legs or not src:
            return {}
        want = None
        if card:
            import vast_cost_model as _v
            want = _v.card_of(card)
            if want is None:
                return {}
        out = {}
        for lg in legs:
            try:
                same_dt = float(lg.get("timestep_fs")) == float(timestep_fs)
            except (TypeError, ValueError):
                continue
            if not same_dt or lg.get("arm") != arm or not lg.get(f"{src}_median_s_per_iter"):
                continue
            if want is not None:
                import vast_cost_model as _v
                if not lg.get("gpu") or _v.card_of(lg["gpu"]) != want:
                    continue
            key = system_of_unit(lg.get("unit_id") or lg.get("leg_id")) or SYSTEM_UNSPECIFIED
            out[key] = out.get(key, 0) + 1
        return out
    except Exception:  # noqa: BLE001 — a provenance read must never break a monitoring pass
        return {}


def expected_s_per_iter(arm, timestep_fs, card=None, rates=None, unit_id=None):
    """(seconds, provenance_kind, note) this arm should take per iteration, from the lane's OWN measured table.

    ★★ THE PER-CARD FIGURE IS PREFERRED AND THAT IS LOAD-BEARING, NOT TIDINESS (2026-07-31). This function
    documented a per-card preference from the day it was written and IMPLEMENTED only the pooled arm median,
    which made every below-median card look broken by construction: the table's own RTX 4090/RTX 3090 ratio
    is 1.745, so a healthy 3090 reads ~1.75x "slower than expected". Caught on the live board within minutes
    of the guard shipping — two 3090s flagged at 1.86x and 2.00x, which rebased on their own card are 1.07x
    and 1.15x. Shipping report-only is what turned that into an observation instead of a reaped fleet.

    ★★ AND IT IS DOWNGRADED WHEN THE MOLECULE UNDERNEATH IT IS NOT THIS LEG'S (2026-08-01 — see the module
    docstring for the ruling and the artifact read that motivated it). `card` fixes the SILICON; it says
    nothing about the ASSEMBLY, and the 4 fs ternary figure is a median over `nr4a3` and `vhl` legs with no
    `nr4a1` leg anywhere in it. `unit_id` is optional and additive: given one, the check is exact ("was any
    leg of THIS system in the figure?"); without one it still refuses a figure that pools several systems,
    because such a figure describes no single assembly and therefore cannot be a like-for-like expectation
    for whichever assembly is in front of it.

    `None` when the timestep was never measured: an unmeasured expectation cannot condemn anything."""
    v, prov, note = _raw_expected(arm, timestep_fs, card=card, rates=rates)
    if v is None or rates is not None or prov not in (PROV_CARD, PROV_POOLED):
        # An injected `rates` table carries no leg records, so its composition is the caller's to vouch for;
        # PROV_NONE has nothing to downgrade.
        return v, prov, note
    systems = contributing_systems(timestep_fs, arm, card=(card if prov == PROV_CARD else None))
    if not systems:
        # ABSENT READING (§4a): the composition could not be established, which is NOT a finding that it is
        # wrong. Keep the provenance that was earned and say the check could not run, so a silent artifact
        # problem cannot quietly switch the warning off.
        return v, prov, note + " — system provenance UNREAD (no leg records for this figure)"
    # ⚠ THE SYSTEM CLAUSE IS APPENDED, NEVER SUBSTITUTED. "Pooled across CARDS" and "pooled across SYSTEMS"
    # are two independent defects in one figure and a note that reported only the newer one would have
    # deleted the older one's evidence from the board.
    named = ", ".join(f"{k} x{n}" for k, n in sorted(systems.items()))
    mine = system_of_unit(unit_id)
    if len(systems) > 1:
        return v, PROV_OFFSYSTEM, note + (
            f" — and POOLED ACROSS SYSTEMS ({named}), so it describes no single assembly and is UNVALIDATED "
            f"for this leg: a slowdown against it is partly the molecule, which is arithmetic and not drift")
    only = next(iter(systems))
    if mine and mine != only:
        return v, PROV_OFFSYSTEM, note + (
            f" — but measured on {named} and containing no {mine} leg, so it is UNVALIDATED for {mine}: a "
            f"slowdown against it is partly the molecule, which is arithmetic and not drift")
    return v, prov, note + f" — measured on {named}"


def _raw_expected(arm, timestep_fs, card=None, rates=None):
    """The measured figure and its CARD-level provenance, before the system check. PURE-ish; see caller.

    Split out so the system downgrade is a separate, readable step rather than four early returns that each
    have to remember to apply it — the shape that let the card preference be documented-but-unimplemented
    for a whole day."""
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
    # ⚠ NOT GATED ON A QUOTE EXISTING, unlike the two branches below. "This expectation was not measured on
    # this leg's molecule" is true whether or not a `$/ns` was quotable, and gating it on `r` would leave a
    # row whose CELL says off-system and whose WHY says "delivering acceptably" — one row, two stories.
    if provenance == PROV_OFFSYSTEM:
        # ★★ THE EXPECTATION IS NOT FOR THIS MOLECULE. A bigger or simply different assembly costs different
        # seconds per iteration by ARITHMETIC (trimcrae, 2026-08-01), and the offset only cancels inside a
        # RANKING of offers scored against one table — never in a realised-vs-quoted comparison. So the
        # delivered rate is stated and NOTHING is asserted about drift or the buy line.
        out.update({"verdict": KEEP,
                    "why": "delivering %.1f s/iter; the expectation it would be graded against was not "
                           "measured on this leg's own system, so it is UNVALIDATED here — no drift and no "
                           "buy-line comparison is asserted. Ranking offers on QUOTED $/ns is unaffected: "
                           "every offer is scored against the same table, so the offset cancels there."
                           % float(measured_s_per_iter)})
        return out
    if r is not None and not licenses_dollar_comparison(provenance):
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
    """The board cell for a verdict. Terse — this column sits beside an already-wide `$/ns`.

    ⚠ AN OFF-SYSTEM ROW SAYS SO EVEN WHEN IT IS FAST. The same rule as §1's `⚠ PAYING` vs `⛔ REFUSED`: a
    number nobody can grade is worse than no number, so a rate compared against an expectation for a
    different assembly must never render like a rate that cleared a like-for-like one."""
    if not v or v.get("verdict") == WATCHING:
        return "—"
    if v["verdict"] == ABANDON:
        return "⛔ CANNOT BANK %.1f s/iter (%.0f min to commit)" % (
            v["measured_s_per_iter"], (v["seconds_to_next_commit"] or 0) / 60.0)
    if v.get("provenance") == PROV_OFFSYSTEM:
        return "%.1f s/iter · no like-for-like expectation (not measured on this system)" % (
            v["measured_s_per_iter"],)
    if licenses_dollar_comparison(v.get("provenance")) and v.get("realised_usd_per_ns") \
            and v["realised_usd_per_ns"] >= v["buy_line_usd_per_ns"]:
        return "⚠ %.1f s/iter · realised $%.5f/ns (%.2fx expected)" % (
            v["measured_s_per_iter"], v["realised_usd_per_ns"], v["slowdown_vs_expected"] or 0)
    return "%.1f s/iter" % v["measured_s_per_iter"]
