#!/usr/bin/env python3
"""Rung `R13-b`'s own pre-launch market read — $0, rents nothing, dispatches nothing.

⛔ WHY THIS FILE EXISTS RATHER THAN A CALL TO `relaunch_market_gate.gate()`. That function is a WRITER: it
persists to `research/modalities/relaunch-market-hold.json`, which is the **step-1 fan-out lane's** one home
for its per-unit hold state — the file's own `_what` says it is written every pass "because a silent hold is
indistinguishable from a finished unit". Invoking it for an ad-hoc read replaced that lane's per-unit history
with a single `lane: "adhoc"` row. That happened on 2026-08-06 and was reverted from git. So this module calls
the gate's PURE parts (`price_offers`, `verdict`) and writes its own artifact. **Do not point this at the
shared file.**

⛔ AND THE CEILING THAT BINDS HERE IS DOLLARS, NOT `$/ns`. A co-fold is structure INFERENCE — it integrates no
dynamics, so there is no nanosecond denominator and a `$/ns` figure would be fabricated in the one column
CLAUDE.md §1 exists to make gradeable (`scope-rung-cost.json` -> `R13-b` -> `_why_no_usd_per_ns`). The rate
line therefore CANNOT bind on this rung, and any refusal must name the DOLLAR ceiling. The `$/ns` block below
is reported as CONTEXT ONLY — it is what the board would cost a dynamics lane right now, and it is explicitly
NOT this rung's gate.

⚠ BOARD DEPTH IS REPORTED WHETHER OR NOT IT COULD BE READ, and a read FAILURE is labelled as such rather than
as a thin market: `qualifying: 0` from an unread board and `qualifying: 0` from a filtered board look
identical and have opposite remedies (CLAUDE.md §6 — "a hold on price must report board width, or it cannot
be told from a filter bug").
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "r13b-market-gate.json")
RUNG_KEY = "R13-b · apo co-fold of the two corrected fusion constructs"


def dollar_ceiling():
    """DERIVED from scope-rung-cost.json. Never typed here (CLAUDE.md §1: one fact, one place)."""
    with open(os.path.join(HERE, "scope-rung-cost.json")) as fh:
        r = json.load(fh)["rungs"][RUNG_KEY]
    lo, hi = r["range_usd"]
    return {"plan_usd": r["plan_usd"], "band_usd": [lo, hi], "units": r["units"], "unit": r["unit"],
            "ceiling_usd_total": hi, "ceiling_usd_per_model": round(hi / r["units"], 6),
            "usd_per_ns": r["usd_per_ns"], "_why_no_usd_per_ns": r["_why_no_usd_per_ns"],
            "_source": "research/modalities/scope-rung-cost.json -> rungs -> %s" % RUNG_KEY}


def read_board():
    """(offers, error). A failure returns (None, 'Type: msg') — never an empty list, which would read as a
    market that returned nothing rather than a board nobody could see."""
    try:
        from gpu_backend import _vast_offer_query, _vast_request
        from ternary_vast_launch import resource_spec
        res = resource_spec()
        api = os.environ.get("VAST_API_KEY")
        if not api:
            raise RuntimeError("no VAST_API_KEY — the board cannot be read")
        offers = (_vast_request("GET", "/search/asks/", api,
                                params={"q": json.dumps(_vast_offer_query(res))}) or {}).get("offers", [])
        return offers, res, None
    except Exception as exc:  # noqa: BLE001
        try:
            from ternary_vast_launch import resource_spec
            res = resource_spec()
        except Exception:  # noqa: BLE001
            res = None
        return None, res, "%s: %s" % (type(exc).__name__, exc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    offers, res, err = read_board()
    doc = {
        "_what": "Rung R13-b's pre-launch market read. $0. Rents nothing, dispatches nothing, and writes "
                 "ONLY this file.",
        "_rung": RUNG_KEY,
        "_not_the_shared_hold_file": "research/modalities/relaunch-market-hold.json belongs to the step-1 "
                                     "fan-out lane and must never be written from here.",
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dollar_ceiling": dollar_ceiling(),
        "which_ceiling_binds": "DOLLAR. The $/ns rate line has no denominator on a co-fold and does not "
                               "apply; a refusal on this rung must name the dollar ceiling.",
        "board_error": err,
    }

    if offers is None:
        doc["board_depth"] = {"offers_returned": 0, "qualifying": 0, "priceable": 0,
                              "needed": 1, "used_for_mean": 0}
        doc["board_depth_meaning"] = ("⚠ THESE ZEROS ARE AN UNREAD BOARD, NOT AN EMPTY ONE. An absent "
                                      "reading is not a reading of absence (CLAUDE.md §4). This is not a "
                                      "thin market and it is not a filter bug — it is a missing credential.")
        doc["usd_per_ns_context"] = None
        doc["verdict"] = "NO READING — the board could not be read from here, so no market verdict exists."
    else:
        from relaunch_market_gate import price_offers, verdict
        best, depth, rows = price_offers(offers, res, n_hosts=1)
        hold, ratio, basis, reason = verdict(best)
        doc["board_depth"] = depth
        doc["board_depth_meaning"] = (
            "offers_returned -> qualifying -> priceable -> used_for_mean. `qualifying` far below "
            "`offers_returned` is a FILTER diagnosis wearing a price label, not a thin market. A low "
            "`used_for_mean` is NOT a symptom — it is min(needed, priceable) and is 1 by design here.")
        doc["usd_per_ns_context"] = {
            "best_usd_per_ns": (round(best, 6) if best else None),
            "basis_usd_per_ns": round(basis, 6),
            "ratio_vs_basis": ratio,
            "would_a_DYNAMICS_lane_hold": hold,
            "reason": reason,
            "⛔_NOT_THIS_RUNGS_GATE": "reported as market context only; R13-b is gated on dollars.",
        }
        doc["offers_priced"] = rows
        doc["verdict"] = ("board readable; R13-b's dollar ceiling is $%.4f total / $%.6f per model and is "
                          "the only ceiling that applies"
                          % (doc["dollar_ceiling"]["ceiling_usd_total"],
                             doc["dollar_ceiling"]["ceiling_usd_per_model"]))

    with open(args.out, "w") as fh:
        json.dump(doc, fh, indent=2)
    print(json.dumps(doc, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
