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

    ★ `dph_total` IS `dph_base + storage_total_cost`, AND THE `inet_*_cost` PAIR IS NOT IN IT — measured, not
    assumed. The first pass of this probe summed the inet lines in too and every one of six live instances came
    back "residual = exactly minus the inet lines", which is not a coincidence but the answer: those fields are
    per-transfer prices, not an hourly charge. Left as an explicit `inet_usd_h` line reported ALONGSIDE the
    total rather than deleted, because "we checked and it is not in there" is worth more than silence.

    `residual` is `dph_total - (gpu + storage)`. Near zero means the total is fully explained by the two hourly
    lines, which is what lets the verdict attribute a gap to storage rather than to a price move. A residual
    that is NOT near zero is itself a finding — Vast would be charging something this split does not name, and
    no conclusion about drift could be drawn from the total.
    """
    def f(key):
        try:
            return float(inst.get(key) or 0.0)
        except (TypeError, ValueError):
            return 0.0
    gpu, storage = f("dph_base"), f("storage_total_cost")
    inet, total = f("inet_up_cost") + f("inet_down_cost"), f("dph_total")
    return {"gpu_usd_h": gpu, "storage_usd_h": storage, "all_in_usd_h": total,
            "inet_usd_h_not_in_total": inet,
            "residual_usd_h": round(total - (gpu + storage), 8),
            "explained": abs(total - (gpu + storage)) <= RATE_EPS_USD_H}


def offer_vs_instance(inst, ledger_row):
    """Why an offer's `dph_total` and an instance's `dph_total` are different numbers for the same rental. PURE.

    ★ THIS IS THE ACTUAL MECHANISM behind the apparent rise, and it is arithmetic. The launcher prints
    `dph≈$X/hr` at submit from the OFFER, where Vast quotes `dph_total = min_bid + a disk line for the disk the
    SEARCH priced`. The instance then reports `dph_total = our BID + the disk line for the volume we actually
    allocated`. Both are called "$/hr" and neither is the other:

        offer    dph_total  =  market FLOOR   +  disk line at the search's disk size
        instance dph_total  =  our agreed BID +  disk line at the REQUESTED disk size

    Two substitutions, both upward, neither a price move. `disk_line_ratio` is the size of the second one.
    """
    d = decompose(inst)
    out = {"offer_dph_total_usd_h": (ledger_row or {}).get("dph"),
           "offer_min_bid_usd_h": (ledger_row or {}).get("min_bid"),
           "bid_usd_h": (ledger_row or {}).get("bid"),
           "instance_dph_total_usd_h": d["all_in_usd_h"],
           "instance_disk_line_usd_h": d["storage_usd_h"],
           "instance_disk_gb": inst.get("disk_space")}
    try:
        offer_disk_line = float(out["offer_dph_total_usd_h"]) - float(out["offer_min_bid_usd_h"])
        out["offer_disk_line_usd_h"] = round(offer_disk_line, 8)
        if offer_disk_line > 0:
            out["disk_line_ratio_instance_over_offer"] = round(d["storage_usd_h"] / offer_disk_line, 4)
            # The disk size the offer's line implies, at the machine's own $/GB/month. If this is far below
            # `instance_disk_gb`, the search priced a volume we never rented.
            out["offer_disk_gb_implied"] = (
                round(float(inst.get("disk_space") or 0) / out["disk_line_ratio_instance_over_offer"], 2)
                if out["disk_line_ratio_instance_over_offer"] else None)
    except (TypeError, ValueError):
        pass
    try:
        out["apparent_rise_usd_h"] = round(d["all_in_usd_h"] - float(out["offer_dph_total_usd_h"]), 8)
        out["explained_by"] = {
            "floor_to_bid_usd_h": round(float(out["bid_usd_h"]) - float(out["offer_min_bid_usd_h"]), 8),
            "disk_line_growth_usd_h": round(d["storage_usd_h"] - out["offer_disk_line_usd_h"], 8)}
        out["fully_explained"] = abs(out["apparent_rise_usd_h"]
                                     - out["explained_by"]["floor_to_bid_usd_h"]
                                     - out["explained_by"]["disk_line_growth_usd_h"]) <= RATE_EPS_USD_H
    except (TypeError, ValueError, KeyError):
        pass
    return out


def verdict(inst, ledger_bid, eps=RATE_EPS_USD_H):
    """Did the GPU rate charged for this LIVE instance move away from the bid agreed at rental? PURE.

    Returns (moved, doc). `moved is None` means the question could not be answered — no bid on record, or a
    total this decomposition cannot account for — which is reported as UNKNOWN and never as "no".
    """
    d = decompose(inst)
    doc = {"instance": inst.get("id"), "machine_id": inst.get("machine_id"),
           "is_bid": inst.get("is_bid"), "ledger_bid_usd_h": ledger_bid, "lines": d,
           # ★ THE SECOND, INDEPENDENT DISCRIMINATOR. If the charged rate tracked the market, a live instance
           # whose `min_bid` has moved since rental would show `dph_base` moving with it. Reported on every row
           # so the reader can check the two against each other without taking this module's word for it.
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
        doc["verdict"] = (f"UNKNOWN — dph_total ${d['all_in_usd_h']:.6f}/hr is NOT the sum of the GPU and "
                          f"storage lines (residual ${d['residual_usd_h']:.6f}/hr). Vast is reporting a "
                          f"charge this decomposition does not name, so no conclusion about a rate move can "
                          f"be drawn from the total.")
        return None, doc
    delta = d["gpu_usd_h"] - bid
    doc["gpu_minus_bid_usd_h"] = round(delta, 8)
    if abs(delta) <= eps:
        doc.update({"verdict": (
            f"NO MOVE. The GPU line is ${d['gpu_usd_h']:.6f}/hr against a bid of ${bid:.6f}/hr agreed at "
            f"rental — identical within ${eps:.0e}/hr, while the market floor for this machine now stands at "
            f"${inst.get('min_bid')}/hr. The whole gap to the ${d['all_in_usd_h']:.6f}/hr all-in figure is "
            f"the storage line (${d['storage_usd_h']:.6f}/hr) for the {inst.get('disk_space')} GB volume, "
            f"fixed when that volume was allocated."),
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


def ledger_rows(bucket=None, s3=None, keys=None):
    """instance_id -> the rental row recorded at rental (bid, min_bid, offer dph), across every lane ledger.

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
            out[str(iid)] = r
    return out


READOUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vast-rate-forensics.json")


def probe(key=None, bucket=None, s3=None, readout_path=None):
    """The whole diagnostic: every live rental, its allow-listed record, its line split and its verdict.

    Written to a COMMITTED artifact as well as printed, for the reason every other guard in this lane is:
    a finding that exists only in a CI job log is a finding nobody will find — GitHub truncates a log from
    the tail and the tail is always runner boilerplate.
    """
    insts = live_instances(key)
    led = {}
    try:
        led = ledger_rows(bucket, s3)
    except Exception as e:  # noqa: BLE001
        print(f"[rate-forensics] no ledger rows available ({type(e).__name__}: {e})", flush=True)
    rows = []
    for i in insts:
        lr = led.get(str(i.get("id")))
        moved, doc = verdict(i, (lr or {}).get("bid"))
        rows.append({"record": safe_row(i), "moved": moved, **doc,
                     "offer_vs_instance": offer_vs_instance(i, lr)})
    out = {"_what": "Read-only forensics: does a Vast rental's CHARGED GPU rate move after rental, or is the "
                    "apparent rise the storage line in `dph_total`?",
           "_fields": ("allow-listed — see SAFE_FIELDS. Field NAMES are evidence; token/ssh/address VALUES "
                       "are credentials and never appear here."),
           "n_instances": len(insts), "instances": rows}
    moved_any = [r for r in rows if r.get("moved") is True]
    graded = [r for r in rows if r.get("moved") is not None]
    unknown = [r for r in rows if r.get("moved") is None]
    out["summary"] = (
        f"{len(moved_any)} of {len(graded)} gradeable live rental(s) show a GPU line differing from the bid "
        f"agreed at rental ({len(unknown)} of {len(rows)} carry no recorded bid and cannot be graded). "
        + ("A live rental's rate DOES move — the relaunch gate's 'never touch a running host' premise fails."
           if moved_any else
           "No graded rental's GPU rate has moved from its bid. An apparent rise on the board is an "
           "INSTANCE's `dph_total` (bid + the real volume's disk line) read against an OFFER's `dph_total` "
           "(market floor + the disk line the search priced) — two different quantities, not a price move."))
    try:
        with open(readout_path or READOUT_PATH, "w") as fh:
            json.dump(out, fh, indent=2, default=str)
            fh.write("\n")
    except OSError as e:
        print(f"[rate-forensics] readout not written: {e}", flush=True)
    print(json.dumps(out, indent=2, default=str))
    if moved_any:
        # ★ THIS IS THE WHOLE POINT OF RUNNING IT ON A SCHEDULE. CLAUDE.md §6 lets the relaunch gate ignore
        # live hosts because a rented rate cannot change. That is TRUE TODAY and measured, but it is a fact
        # about Vast's billing rather than about our code, so it can stop being true without anyone touching
        # this repo. `::error::` fails the job, and a failed job is the session-independent alert path the
        # watchdogs already rely on — a finding in a JSON nobody opens is not an alert.
        print(f"::error title=A LIVE VAST RENTAL'S CHARGED RATE HAS MOVED::"
              f"{len(moved_any)} live rental(s) are being billed a GPU rate that differs from the bid agreed "
              f"at rental: "
              + "; ".join(f"instance {r['instance']} ${r['lines']['gpu_usd_h']:.6f}/hr vs bid "
                          f"${r['ledger_bid_usd_h']}/hr" for r in moved_any)
              + ". CLAUDE.md §6's live-host boundary ('the gate acts at the moment of renting and must never "
                "be given reach over a live host') rests on this NOT happening. Re-open that rule before "
                "trusting any in-flight $/ns row. Snapshot: vast-rate-forensics.json.", flush=True)
    return out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--probe" in argv:
        out = probe()
        # Non-zero ONLY when a rate has actually moved. An ungradeable rental (no recorded bid) is not a
        # failure — most instances in this account were rented by lanes that keep no ledger, and failing on
        # those would turn the guard into noise, which is how a guard stops being read.
        return 1 if any(r.get("moved") is True for r in out["instances"]) else 0
    print(__doc__)
    print("usage: vast_rate_forensics.py --probe")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
