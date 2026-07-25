#!/usr/bin/env python3
"""
DECISIVE EXPERIMENT: on a Vast interruptible rental, do you pay YOUR BID or a CLEARING PRICE?

WHY THIS EXISTS. Every bid decision in this repo rests on "on Vast you PAY YOUR BID" — it is the reason a
higher multiple is treated as costly, the reason the reservation-price/limit-order framing works, and the
reason `x1.9` was called an overpayment. **The claim has never been verified.** Vast's own documentation
(fetched 2026-07-25, `vast-docs-raw.json`) describes the auction — "clients set a bid price ... the current
highest bid determines the instance that runs; any others are paused" — but nowhere states what you are
CHARGED. Meanwhile at least one secondary source asserts the opposite ("you pay what's needed to maintain the
highest bid"), which would make the policy invert: under second-price billing, bidding high buys priority
nearly for free and the correct bid is your full reservation value.

A plausible reading of ambiguous prose is a hypothesis, not a diagnosis. This is the controlled reproduction.

METHOD. Rent the single cheapest rentable interruptible offer on the market with a bid deliberately set to
`OVERBID_MULT x min_bid` (default 4x) — far enough above the floor that the two hypotheses cannot be confused
by rounding or by the storage line. Then read the instance's own billing fields back from the API and compare:

    charged compute rate ~= our bid       -> PAY-YOUR-BID (first price). Repo assumption CONFIRMED.
    charged compute rate ~= min_bid       -> CLEARING PRICE (second price). Repo assumption REFUTED; bidding
                                             high is nearly free and the whole policy must be re-derived.

COST. The cheapest offer on the market is typically $0.01-0.05/hr; 4x that for a few minutes is well under one
cent. A tiny image is used so nothing large is pulled, and the instance is DESTROYED in a `finally` block that
also sweeps for any instance carrying our label — an orphaned box is the only real risk here and it is guarded
twice.

Runs on CI (the dev sandbox's egress proxy 403s console.vast.ai). Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gpu_backend import _vast_request  # noqa: E402

LABEL = "bid-semantics-probe"
# A ~5 MB image: we are measuring a PRICE, not running anything, so the container should pull in seconds. A
# fat CUDA image would add minutes of paid time for no information.
TINY_IMAGE = "alpine:latest"


def cheapest_offer(key, max_price=0.20, min_price=0.004):
    """The cheapest rentable single-GPU interruptible offer. Card is irrelevant — we are probing BILLING."""
    q = {"num_gpus": {"eq": 1}, "rentable": {"eq": True},
         "order": [["dph_total", "asc"]], "type": "bid", "limit": 128}
    offers = (_vast_request("GET", "/search/asks/", key, params={"q": json.dumps(q)}) or {}).get("offers", [])
    cands = []
    for o in offers:
        try:
            mb = float(o.get("min_bid") or 0)
        except (TypeError, ValueError):
            continue
        # A floor of ~0 makes the ratio test meaningless (4 x 0 = 0), and an expensive box wastes money.
        if not (min_price <= mb <= max_price):
            continue
        if (o.get("reliability2") or 0) < 0.95:      # a flaky host may never start, burning the run for nothing
            continue
        cands.append((mb, o))
    cands.sort(key=lambda t: t[0])
    return cands[0][1] if cands else None


def instance_record(key, inst_id):
    resp = _vast_request("GET", "/instances/", key, params={"owner": "me"}) or {}
    for i in resp.get("instances", []):
        if str(i.get("id")) == str(inst_id):
            return i
    return None


def destroy(key, inst_id):
    try:
        _vast_request("DELETE", f"/instances/{inst_id}/", key)
        print(f"[probe] destroyed {inst_id}", flush=True)
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[probe] WARN destroy {inst_id} failed: {e}", flush=True)
        return False


def sweep_label(key):
    """Belt-and-braces teardown: destroy anything wearing our label, whatever happened above."""
    try:
        resp = _vast_request("GET", "/instances/", key, params={"owner": "me"}) or {}
    except Exception as e:  # noqa: BLE001
        print(f"[probe] WARN sweep list failed: {e}", flush=True)
        return
    for i in resp.get("instances", []):
        if str(i.get("label") or "") == LABEL:
            print(f"[probe] sweep: found stray {i.get('id')} — destroying", flush=True)
            destroy(key, i.get("id"))


def rent_at(key, offer_id, bid, poll_s, max_wait_s, note=""):
    """Rent one offer at `bid`, capture the FULL instance record, destroy. Returns the record + charged rate.

    The full record matters: the single-shot probe found a charged rate equal to NEITHER the bid NOR the floor,
    so the field that explains it may be one we were not keeping."""
    inst_id = None
    out = {"bid_usd_h": bid, "note": note, "polls": [], "full_record": None}
    try:
        body = {"client_id": "me", "image": TINY_IMAGE, "disk": 8.0,
                "onstart": "echo probe", "runtype": "args", "label": LABEL,
                "target_state": "running", "price": bid}
        created = _vast_request("PUT", f"/asks/{offer_id}/", key, body=body) or {}
        inst_id = created.get("new_contract") or created.get("id")
        out["create_response"] = {k: created.get(k) for k in ("success", "new_contract", "error", "msg")}
        if not inst_id:
            out["error"] = f"create returned no id: {created}"
            return out
        waited = 0
        while waited <= max_wait_s:
            rec = instance_record(key, inst_id)
            if rec:
                out["polls"].append({"t_s": waited, "dph_base": rec.get("dph_base"),
                                     "dph_total": rec.get("dph_total"), "min_bid": rec.get("min_bid"),
                                     "actual_status": rec.get("actual_status")})
                if rec.get("dph_base") is not None:
                    out["full_record"] = rec
                    out["charged_dph_base"] = float(rec["dph_base"])
                    break
            time.sleep(poll_s)
            waited += poll_s
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"
    finally:
        if inst_id:
            destroy(key, inst_id)
    return out


def ladder(key, a):
    """THE DISCRIMINATING EXPERIMENT. Rent the SAME offer at several bid multiples and compare what we are
    charged each time.

        charged tracks the bid                 -> PAY-YOUR-BID (first price)
        charged identical across all bids      -> the bid is a MAX PRICE and we pay a market clearing rate
                                                  (AWS-spot semantics). Raising the bid is then FREE in $/hr
                                                  and only buys retention — the opposite of the repo's policy.

    Same offer each time, so host, card, disk and storage rate are all held constant; the bid is the only
    thing that varies. One rental per rung, a couple of minutes each, pennies total."""
    offer = cheapest_offer(key)
    if not offer:
        return {"error": "no suitable cheap offer"}
    # Re-read the floor immediately before renting: a stale min_bid is a live alternative explanation for the
    # single-shot result and has to be ruled out rather than assumed away.
    fresh = cheapest_offer(key)
    res = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "experiment": "bid ladder on ONE offer — does the charged rate track the bid?",
           "offer": {k: offer.get(k) for k in ("id", "machine_id", "gpu_name", "min_bid", "dph_base",
                                               "dph_total", "storage_cost", "search", "gpu_frac", "num_gpus")},
           "floor_at_select": float(offer["min_bid"]),
           "floor_on_recheck": float(fresh["min_bid"]) if fresh else None,
           "rungs": []}
    floor = float(offer["min_bid"])
    for mult in [float(x) for x in a.ladder.split(",")]:
        bid = round(floor * mult, 4)
        print(f"\n[probe] === rung x{mult}: bid ${bid:.5f} on offer {offer['id']} "
              f"(floor ${floor:.5f}) ===", flush=True)
        r = rent_at(key, offer["id"], bid, a.poll_s, a.max_wait_s, note=f"x{mult}")
        r["mult"] = mult
        res["rungs"].append(r)
        print(f"[probe] rung x{mult}: bid ${bid:.5f} -> charged {r.get('charged_dph_base')}", flush=True)
        time.sleep(5)

    charged = [(r["mult"], r["bid_usd_h"], r.get("charged_dph_base")) for r in res["rungs"]
               if r.get("charged_dph_base") is not None]
    res["charged_by_rung"] = charged
    if len(charged) < 2:
        res["verdict"] = "INCONCLUSIVE — fewer than two rungs returned a price"
    else:
        vals = [c for _, _, c in charged]
        spread = (max(vals) - min(vals)) / max(min(vals), 1e-9)
        tracks = all(abs(c - b) <= max(0.002, 0.10 * b) for _, b, c in charged)
        if tracks:
            res["verdict"] = "PAY-YOUR-BID: charged tracked the bid at every rung."
        elif spread < 0.05:
            res["verdict"] = (f"MAX-PRICE / CLEARING-RATE: charged was {vals[0]:.5f} at every rung despite "
                              f"bids spanning {charged[0][1]:.5f}-{charged[-1][1]:.5f}. The bid is a CEILING, "
                              f"not a price. Raising it costs nothing per hour and only buys retention.")
        else:
            res["verdict"] = (f"NEITHER: charged varies ({min(vals):.5f}-{max(vals):.5f}) but does not track "
                              f"the bid. Inspect full_record for the governing field.")
    return res


def verify_cap(key, machine_id):
    """Read-only ($0): what is THIS machine's on-demand price? The ladder showed the charge saturating at a
    hard cap; the obvious candidate is the on-demand rate, and 'obvious candidate' is not a measurement. An
    unfiltered on-demand query for the one machine settles it."""
    q = {"machine_id": {"eq": int(machine_id)}, "rentable": {"eq": True},
         "type": "on-demand", "limit": 64}
    offers = (_vast_request("GET", "/search/asks/", key, params={"q": json.dumps(q)}) or {}).get("offers", [])
    rows = [{k: o.get(k) for k in ("id", "machine_id", "gpu_name", "num_gpus", "dph_base", "dph_total",
                                   "min_bid", "search")} for o in offers]
    for r in rows:
        print(f"[cap] on-demand offer {r['id']} {r['gpu_name']} x{r['num_gpus']} "
              f"dph_base={r['dph_base']} dph_total={r['dph_total']}", flush=True)
    return {"machine_id": machine_id, "on_demand_offers": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--overbid-mult", type=float, default=4.0)
    ap.add_argument("--verify-cap", default="", help="machine_id: read-only lookup of its on-demand price")
    ap.add_argument("--ladder", default="", help="comma-separated bid multiples, e.g. 1.0,2.0,6.0")
    ap.add_argument("--poll-s", type=int, default=15)
    ap.add_argument("--max-wait-s", type=int, default=180)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "vast-bid-semantics-probe.json"))
    a = ap.parse_args()

    key = os.environ.get("VAST_API_KEY", "").strip()
    if not key:
        print("FAIL: VAST_API_KEY not set", flush=True)
        return 2

    if a.verify_cap:
        out = verify_cap(key, a.verify_cap.replace("cap:", "").strip())
        path = a.out.replace(".json", "-cap.json")
        with open(path, "w") as f:
            json.dump(out, f, indent=1)
        print(f"[cap] wrote {path}", flush=True)
        return 0

    if a.ladder:
        try:
            res = ladder(key, a)
        finally:
            sweep_label(key)
        print(f"\n[probe] VERDICT: {res.get('verdict')}", flush=True)
        with open(a.out.replace(".json", "-ladder.json"), "w") as f:
            json.dump(res, f, indent=1, default=str)
        print(f"[probe] wrote {a.out.replace('.json', '-ladder.json')}", flush=True)
        return 0

    offer = cheapest_offer(key)
    if not offer:
        print("FAIL: no suitable cheap offer found", flush=True)
        return 3

    floor = float(offer["min_bid"])
    bid = round(floor * a.overbid_mult, 4)
    result = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hypothesis_A_pay_your_bid": "charged compute rate ~= bid",
        "hypothesis_B_clearing_price": "charged compute rate ~= min_bid (floor)",
        "offer": {k: offer.get(k) for k in
                  ("id", "machine_id", "gpu_name", "min_bid", "dph_base", "dph_total", "storage_cost",
                   "search", "rented", "reliability2", "gpu_frac")},
        "floor_usd_h": floor, "bid_usd_h": bid, "overbid_mult": a.overbid_mult,
        "polls": [],
    }
    print(f"[probe] offer {offer['id']} ({offer.get('gpu_name')}) floor=${floor:.5f}/hr "
          f"-> bidding ${bid:.5f}/hr ({a.overbid_mult}x)", flush=True)

    inst_id = None
    try:
        body = {"client_id": "me", "image": TINY_IMAGE, "disk": 8.0,
                "onstart": "echo probe", "runtype": "args", "label": LABEL,
                "target_state": "running", "price": bid}
        created = _vast_request("PUT", f"/asks/{offer['id']}/", key, body=body) or {}
        inst_id = created.get("new_contract") or created.get("id")
        result["create_response"] = {k: created.get(k) for k in ("success", "new_contract", "error", "msg")}
        if not inst_id:
            result["verdict"] = f"INCONCLUSIVE — create returned no instance id: {created}"
            print(f"FAIL: {result['verdict']}", flush=True)
            return 4
        print(f"[probe] created instance {inst_id}", flush=True)

        waited = 0
        while waited <= a.max_wait_s:
            rec = instance_record(key, inst_id)
            if rec:
                snap = {k: rec.get(k) for k in
                        ("dph_base", "dph_total", "min_bid", "is_bid", "actual_status", "intended_status",
                         "cur_state", "storage_cost", "storage_total_cost", "search", "start_date", "gpu_name")}
                snap["t_s"] = waited
                result["polls"].append(snap)
                print(f"[probe] t={waited:>3}s status={rec.get('actual_status')}/{rec.get('intended_status')} "
                      f"dph_base={rec.get('dph_base')} dph_total={rec.get('dph_total')} "
                      f"min_bid={rec.get('min_bid')} is_bid={rec.get('is_bid')}", flush=True)
                # dph_base is populated as soon as the contract exists; no need to wait for the container.
                if rec.get("dph_base") is not None:
                    break
            time.sleep(a.poll_s)
            waited += a.poll_s
    finally:
        if inst_id:
            destroy(key, inst_id)
        sweep_label(key)

    # ---- verdict ------------------------------------------------------------------------------------------
    charged = None
    for p in result["polls"]:
        if p.get("dph_base") is not None:
            charged = float(p["dph_base"])
            break
    result["charged_dph_base"] = charged
    if charged is None:
        result["verdict"] = "INCONCLUSIVE — instance never reported a price before teardown"
    else:
        near_bid = abs(charged - bid) <= max(0.002, 0.10 * bid)
        near_floor = abs(charged - floor) <= max(0.002, 0.10 * floor)
        if near_bid and not near_floor:
            result["verdict"] = (f"PAY-YOUR-BID CONFIRMED: charged ${charged:.5f}/hr == our bid ${bid:.5f}/hr "
                                 f"(floor was ${floor:.5f}). A higher bid is paid on EVERY hour.")
        elif near_floor and not near_bid:
            result["verdict"] = (f"CLEARING-PRICE: charged ${charged:.5f}/hr == the floor ${floor:.5f}/hr "
                                 f"despite bidding ${bid:.5f}. Bidding high is ~free — REDERIVE THE POLICY.")
        else:
            result["verdict"] = (f"AMBIGUOUS: charged ${charged:.5f}/hr vs bid ${bid:.5f} / floor ${floor:.5f}")
    print(f"\n[probe] VERDICT: {result['verdict']}", flush=True)

    with open(a.out, "w") as f:
        json.dump(result, f, indent=1)
    print(f"[probe] wrote {a.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
