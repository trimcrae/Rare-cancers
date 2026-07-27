#!/usr/bin/env python3
"""Does a Vast rental's rate MOVE after you rent it? Read-only forensics on the live instance record.

★ WHY THIS EXISTS (trimcrae, 2026-07-27). The board showed the Step 1 shakeout rented on instance 45996071 at
**$0.1926/hr = 1.41x basis** (under the drift line) and, 43 minutes later, the same instance reported at
**$0.2497/hr = 1.82x basis** (`⚠ DRIFT`). The obvious reading is "the bid rate rose while it ran, and nothing
re-checked" — which would make CLAUDE.md §6's *"work already executing is never touched"* a rule resting on a
false premise, and would demand a live-host re-check.

That reading is LOAD-BEARING, so it gets a diagnostic instead of a story (CLAUDE.md §4). The competing
hypotheses are:

  H1  THE RATE ROSE. The interruptible rate charged for a running instance tracks the market and can climb
      above the bid agreed at rental. If true, a live rental can drift past the ceiling and the gate must
      re-check running hosts.
  H2  THE TWO NUMBERS ARE DIFFERENT QUANTITIES. `$0.1926` is the OFFER's `dph_total` at search time (the
      market FLOOR plus the search's own disk line) and `$0.2497` is the INSTANCE's `dph_total` (our agreed
      BID plus the disk line for the volume actually allocated). Nothing moved; two different things were
      compared and the difference was read as a rise.

★ THE ONE OBSERVATION THAT DISCRIMINATES, and it is arithmetic rather than a judgement call.
Vast reports an instance's rate as three separable lines — `dph_base` (the GPU), `storage_total_cost` (the
volume) and the `inet_*_cost` pair — with `dph_total` their sum. So:
  * under H1, `dph_base` on the live instance is ABOVE the bid recorded in the lane's rental ledger;
  * under H2, `dph_base` EQUALS that bid to the cent and the entire gap to `dph_total` is the storage line.
`decompose()` computes exactly that split and `verdict()` reads it. No interpretation is needed: the two
hypotheses predict different numbers in the same field of the same record.

★ WHAT THIS DELIBERATELY DOES NOT PRINT. An allow-list, not a redaction list — `SAFE_FIELDS` below. A Vast
instance record carries `jupyter_token`, `ssh_host`/`ssh_port` and `public_ipaddr`, and an earlier probe in
this repo committed a full record verbatim into a tracked JSON. Field NAMES are evidence; several field
VALUES are credentials. Anything not on the allow-list never reaches the output, so a new field Vast adds
tomorrow is excluded by default rather than leaked by default.

Read-only: `GET` only. It rents nothing, destroys nothing and touches no running host.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The ONLY fields that may leave this module. Prices, identity and state — never a token, host or address.
SAFE_FIELDS = (
    "id", "machine_id", "label", "gpu_name", "num_gpus", "gpu_frac", "disk_space",
    "is_bid", "cur_state", "actual_status", "intended_status", "start_date", "duration",
    "dph_base", "dph_total", "storage_cost", "storage_total_cost",
    "inet_up_cost", "inet_down_cost", "min_bid", "gpu_util",
)

# Two rates are "the same rate" within this many $/hr. Vast returns repeating decimals (0.1904 vs
# 0.19039999999999999), so an equality test on floats would manufacture a rise out of float representation —
# which is the very error class this module exists to rule out. A tenth of a cent per hour is far below any
# drift worth acting on and far above any rounding artifact.
RATE_EPS_USD_H = 1e-4


def safe_row(inst):
    """The allow-listed view of one instance record. PURE.

    Missing keys are simply absent rather than filled with a placeholder: a fabricated zero in a PRICE field
    is exactly the failure mode this repo keeps paying for.
    """
    return {k: inst.get(k) for k in SAFE_FIELDS if inst.get(k) is not None}


def decompose(inst):
    """Split an instance's `dph_total` into the lines Vast bills separately. PURE.

    `residual` is `dph_total - (gpu + storage + inet)`. A residual near zero means the reported total is fully
    explained by the named lines, which is what lets the verdict below attribute a gap to storage rather than
    to a price move. A residual that is NOT near zero is itself a finding — it would mean Vast is charging
    something this decomposition does not name, and no conclusion about drift could be drawn from the total.
    """
    def f(key):
        try:
            return float(inst.get(key) or 0.0)
        except (TypeError, ValueError):
            return 0.0
    gpu, storage = f("dph_base"), f("storage_total_cost")
    inet, total = f("inet_up_cost") + f("inet_down_cost"), f("dph_total")
    return {"gpu_usd_h": gpu, "storage_usd_h": storage, "inet_usd_h": inet, "all_in_usd_h": total,
            "residual_usd_h": round(total - (gpu + storage + inet), 8),
            "explained": abs(total - (gpu + storage + inet)) <= RATE_EPS_USD_H}


def verdict(inst, ledger_bid, eps=RATE_EPS_USD_H):
    """Did the GPU rate charged for this LIVE instance move away from the bid agreed at rental? PURE.

    Returns (moved, doc). `moved is None` means the question could not be answered — no bid on record, or a
    total this decomposition cannot account for — which is reported as UNKNOWN and never as "no".
    """
    d = decompose(inst)
    doc = {"instance": inst.get("id"), "machine_id": inst.get("machine_id"),
           "is_bid": inst.get("is_bid"), "ledger_bid_usd_h": ledger_bid, "lines": d,
           "live_min_bid_usd_h": inst.get("min_bid")}
    if ledger_bid in (None, ""):
        doc["verdict"] = ("UNKNOWN — no bid on record for this instance, so the rate it is being charged "
                          "cannot be compared with the rate it was rented at.")
        return None, doc
    try:
        bid = float(ledger_bid)
    except (TypeError, ValueError):
        doc["verdict"] = f"UNKNOWN — the recorded bid {ledger_bid!r} is not a number."
        return None, doc
    if not d["explained"]:
        doc["verdict"] = (f"UNKNOWN — dph_total ${d['all_in_usd_h']:.6f}/hr is NOT the sum of the GPU, "
                          f"storage and inet lines (residual ${d['residual_usd_h']:.6f}/hr). Vast is "
                          f"reporting a charge this decomposition does not name, so no conclusion about a "
                          f"rate move can be drawn from the total.")
        return None, doc
    delta = d["gpu_usd_h"] - bid
    doc["gpu_minus_bid_usd_h"] = round(delta, 8)
    if abs(delta) <= eps:
        doc.update({"verdict": (
            f"NO MOVE. The GPU line is ${d['gpu_usd_h']:.6f}/hr against a bid of ${bid:.6f}/hr agreed at "
            f"rental — identical within ${eps:.0e}/hr. The whole gap to the ${d['all_in_usd_h']:.6f}/hr "
            f"all-in figure is the storage line (${d['storage_usd_h']:.6f}/hr) plus inet "
            f"(${d['inet_usd_h']:.6f}/hr), both of which were fixed when the volume was allocated. A rate "
            f"quoted from `dph_total` and compared against an offer's `dph_total` is comparing a rented "
            f"{inst.get('disk_space')} GB volume against whatever disk the search quoted."),
            "hypothesis_supported": "H2 (two different quantities)"})
        return False, doc
    doc.update({"verdict": (
        f"MOVED. The GPU line is ${d['gpu_usd_h']:.6f}/hr against a bid of ${bid:.6f}/hr — a change of "
        f"${delta:+.6f}/hr on a LIVE rental. The rate agreed at rental is not the rate being charged."),
        "hypothesis_supported": "H1 (the charged rate tracks the market)"})
    return True, doc


# =============================================================================================================
# the live read — GET only
# =============================================================================================================
def live_instances(key=None):
    """Every instance this account holds, as raw records. Read-only."""
    from gpu_backend import _vast_request
    api = key or os.environ.get("VAST_API_KEY")
    if not api:
        raise RuntimeError("no VAST_API_KEY — the instance list cannot be read")
    return (_vast_request("GET", "/instances/", api, params={"owner": "me"}) or {}).get("instances") or []


def ledger_bids(bucket=None, s3=None, keys=None):
    """instance_id -> the bid recorded when it was rented, across every lane ledger that keeps one.

    DERIVED from each lane's own module rather than typed here (CLAUDE.md §1), so a lane that repoints its
    result prefix cannot leave this probe reading a stale key.
    """
    if s3 is None:
        import boto3
        s3 = boto3.client("s3")
    b = bucket or os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
    if keys is None:
        keys = []
        try:
            import congeneric_fanout_vast as cfv
            keys.append(cfv._LEDGER_KEY)
        except Exception:  # noqa: BLE001 — a lane that cannot be imported simply contributes no bids
            pass
    out = {}
    for k in keys:
        try:
            doc = json.loads(s3.get_object(Bucket=b, Key=k)["Body"].read())
        except Exception as e:  # noqa: BLE001
            print(f"[rate-forensics] ledger {k} unreadable ({type(e).__name__}: {e})", flush=True)
            continue
        for iid, r in (doc.get("rentals") or {}).items():
            if r.get("bid") is not None:
                out[str(iid)] = r["bid"]
    return out


def probe(key=None, bucket=None, s3=None):
    """The whole diagnostic: every live rental, its allow-listed record, its line split and its verdict."""
    insts = live_instances(key)
    bids = {}
    try:
        bids = ledger_bids(bucket, s3)
    except Exception as e:  # noqa: BLE001
        print(f"[rate-forensics] no ledger bids available ({type(e).__name__}: {e})", flush=True)
    rows = []
    for i in insts:
        moved, doc = verdict(i, bids.get(str(i.get("id"))))
        rows.append({"record": safe_row(i), "moved": moved, **doc})
    out = {"_what": "Read-only forensics: does a Vast rental's CHARGED GPU rate move after rental, or is the "
                    "apparent rise the storage line in `dph_total`?",
           "_fields": ("allow-listed — see SAFE_FIELDS. Field NAMES are evidence; token/ssh/address VALUES "
                       "are credentials and never appear here."),
           "n_instances": len(insts), "instances": rows}
    moved_any = [r for r in rows if r.get("moved") is True]
    unknown = [r for r in rows if r.get("moved") is None]
    out["summary"] = (
        f"{len(moved_any)} of {len(rows)} live rental(s) show a GPU line differing from the bid agreed at "
        f"rental ({len(unknown)} could not be graded). "
        + ("A live rental's rate DOES move — the relaunch gate's 'never touch a running host' premise fails."
           if moved_any else
           "No live rental's GPU rate has moved from its bid. An apparent rise on the board is `dph_total` "
           "(GPU + storage) being compared against an offer's `dph_total` (floor + the search's disk line)."))
    print(json.dumps(out, indent=2, default=str))
    return out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--probe" in argv:
        probe()
        return 0
    print(__doc__)
    print("usage: vast_rate_forensics.py --probe")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
