#!/usr/bin/env python3
"""Should a capacity-refused host be DESTROYED right now, or HELD until we have somewhere to go?

★★ THE RULING (trimcrae, 2026-07-27, ~9:00 PM ET): *"Reevaluate if we want to tear down immediately when a
host goes away. That's probably something we should only do if we know we have a better alternative."*

WHAT THE OLD RULE SAID, AND WHY IT WAS RIGHT WHEN WRITTEN. CLAUDE.md §6: on
`{"success": false, "error": "resources_unavailable"}` the machine's GPU is taken, so *destroy the instance
and launch elsewhere — do not queue, do not raise the bid.* Both alternatives were measured and both failed:
a +26 % bid raise (2026-07-25) left the box queued, and it sat `stopped` for 45 min across ~13 start
attempts. The rule's stated premise was **"Vast is ~23 independently-priced hosts and the floor is flat, so
a different host today costs what this one will tomorrow."**

WHY THAT PREMISE NO LONGER HOLDS. It assumed re-placement was always available. It is not, because a LATER
ruling — the `$/ns` buy line, CLAUDE.md §1/§6 — can refuse to buy anything at all. Measured 8:32 PM ET on
2026-07-27: the step 1 board returned 182 offers, 176 qualifying, 100 priceable, and the cheapest was
`$0.006683/ns` = 1.96x basis, above the `$0.006539/ns` line — so **all 12 withheld units were refused and
$0 was authorised.** A teardown at that moment would have destroyed a host and bought nothing, because the
gate that decides the replacement would have declined it. "Destroy, then re-place" silently became
"destroy, then hope."

THE ASYMMETRY, IN MEASURED DOLLARS. Holding is cheap and teardown is not free:

  * HOLDING costs storage only — `bid-strategy.md` F4, measured across 445 offers: median $0.20/GB/month
    (p90 $0.467) => **~$0.011/hr** at the 40 GB the launcher requests. Billed whether running or stopped.
  * DESTROYING forfeits the instance's DISK, and the disk is the staged inputs. The checkpoint is safe
    either way (it is in S3), so no science is lost — but the replacement must redo the cold start: stage
    ~15 min, then parameterise/solvate the ~146k-particle hybrid, then minimise 12 replicas, all billed on
    the new GPU at $0.13-0.28/hr before one FEP iteration is committed.

THIS EXACT MISTAKE HAS ALREADY COST US ONCE. `bid-strategy.md` F3: being outbid PAUSES an instance, it does
not destroy it, and the disk survives — *"our own reaper listed `stopped` as terminal and DELETEd paused
instances, forcing a fresh pull on re-rent. The premium was insuring against our own bug."* That was the
outbid case, which this module does not touch; but it is the same shape, and it is why "stopped" must never
be treated as "gone" without asking what teardown actually buys.

WHAT THIS MODULE CHANGES, PRECISELY. Not *whether* to swap hosts — swapping is still right, and a machine
that refused is still blacklisted so selection cannot pick it again. Only the ORDER: **secure the
replacement first, then destroy.** Re-ordering a swap costs nothing and removes the window where we hold
neither the old host nor a new one.

WHAT THIS MODULE DELIBERATELY DOES NOT DO:
  * It never raises a bid. That was measured to change nothing (+26 %, still queued).
  * It never waits on the SAME host to free up — a HOLD here keeps the box for its DISK, and the machine is
    blacklisted at the same moment, so the next placement goes elsewhere.
  * It cannot hold forever: with no replacement in sight the existing `MAX_STOPPED_MIN` backstop still
    reaps, so the storage line cannot bleed unbounded.
  * It never reads `gpu_util` and never reasons about GPU idleness (CLAUDE.md §6 — idleness must never
    condemn a box).
"""
from __future__ import annotations

# The three verdicts. Strings rather than an enum so they survive a round trip through the JSON snapshot
# that every hold must carry.
DESTROY_HAVE_REPLACEMENT = "destroy: a qualifying replacement is on the board"
DESTROY_BACKSTOP = "destroy: no replacement, but the stopped-storage backstop expired"
HOLD_NO_REPLACEMENT = "hold: nothing on the board clears the buy line, so teardown would buy nothing"


def decide(*, replacement_usd_per_ns, buy_line_usd_per_ns, stopped_min, max_stopped_min,
           storage_usd_h=0.011):
    """Destroy this capacity-refused instance, or hold it? PURE — no I/O, no clock, no API.

    `replacement_usd_per_ns` is the best price at which we could rent a REPLACEMENT right now, already
    excluding blacklisted machines; `None` means the board offered nothing priceable at all.

    Returns a dict carrying the decision AND the snapshot that produced it, because CLAUDE.md §6 requires
    every hold to be visible with its evidence — a silent hold is indistinguishable from a lane that
    finished.
    """
    have = (replacement_usd_per_ns is not None
            and buy_line_usd_per_ns is not None
            and replacement_usd_per_ns <= buy_line_usd_per_ns)

    if have:
        verdict, destroy = DESTROY_HAVE_REPLACEMENT, True
    elif stopped_min is not None and max_stopped_min is not None and stopped_min >= max_stopped_min:
        # The backstop is what stops a hold becoming a permanent storage bill. It is deliberately the SAME
        # constant the old code already used for a non-capacity stop, so this change adds no new tunable.
        verdict, destroy = DESTROY_BACKSTOP, True
    else:
        verdict, destroy = HOLD_NO_REPLACEMENT, False

    out = {
        "destroy": destroy,
        "verdict": verdict,
        "replacement_usd_per_ns": replacement_usd_per_ns,
        "buy_line_usd_per_ns": buy_line_usd_per_ns,
        "replacement_clears_buy_line": have,
        "stopped_min": stopped_min,
        "max_stopped_min": max_stopped_min,
        "storage_usd_h_while_held": storage_usd_h,
    }
    if not destroy:
        # The number that makes the hold auditable at a glance: what the decision is costing per hour. It is
        # the storage line and nothing else — a held box runs no GPU, so there is no $/ns to quote and
        # quoting one would be a fabricated figure.
        out["hold_cost_usd_h"] = storage_usd_h
        out["hold_why"] = (
            f"the best replacement on the board is "
            f"{('$%.6f/ns' % replacement_usd_per_ns) if replacement_usd_per_ns is not None else 'nothing priceable'}"
            f", against a buy line of ${buy_line_usd_per_ns:.6f}/ns"
            if buy_line_usd_per_ns is not None else "no buy line could be derived")
    return out


def render(d, instance_id=None, machine_id=None):
    """One operator-readable line. `⛔ REFUSED` vs `⚠ PAYING` discipline per CLAUDE.md §1: a box we are
    HOLDING is not a purchase, so it must never render like one."""
    who = f"{instance_id or '?'} (machine {machine_id or '?'})"
    if d["destroy"]:
        if d["verdict"] == DESTROY_BACKSTOP:
            return (f"    -> destroying {who}: no replacement cleared the buy line, but it has been stopped "
                    f"{d['stopped_min']:.0f} min (backstop {d['max_stopped_min']:.0f} min) — "
                    f"holding it any longer is a pure storage bill")
        return (f"    -> destroying {who}: a replacement is available at "
                f"${d['replacement_usd_per_ns']:.6f}/ns, at or under the "
                f"${d['buy_line_usd_per_ns']:.6f}/ns line — swapping now costs nothing extra")
    return (f"    -> ⛔ HOLDING {who} — $0 GPU going out, ~${d['hold_cost_usd_h']:.3f}/hr storage only. "
            f"{d['hold_why']}. Destroying would forfeit the staged disk and buy NOTHING, because the gate "
            f"would refuse the replacement. Machine is blacklisted; re-checked next tick "
            f"(backstop {d['max_stopped_min']:.0f} min, now {d['stopped_min']:.0f} min).")
