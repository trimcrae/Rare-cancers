#!/usr/bin/env python3
"""
Pull Vast's OFFICIAL historical GPU market metrics — the price history we were about to reconstruct by hand.

WHY THIS EXISTS. The adaptive bidding policy (`vast_bid_optimizer.py`) needs a distribution of prices over TIME.
An earlier version of the plan asserted that no such history was available and that we would have to accumulate
one hour-by-hour with a sampler, or back it out of our own CI logs. **That was wrong and was never checked.**
Vast publishes market metrics directly, at hourly granularity, with P10 / median / P90 pricing:

    https://console.vast.ai/api/v0/metrics/gpu/current/      current snapshot
    https://console.vast.ai/api/v0/metrics/gpu/history/      historical time series (gpu_name, time range, step)
    https://console.vast.ai/api/v0/metrics/gpu/locations/    geography

So the policy does not need to wait to leave its cold-start phase: it can start with real history today. The
hourly sampler remains useful as a cross-check and to capture the exact offer set we can actually rent (market
metrics are platform-wide; our filtered, verified, CUDA-capable subset is narrower), but it is no longer the
critical path.

RUNS ON CI. The dev sandbox's egress proxy 403s console.vast.ai, per the standing rule; this is written
pure-stdlib so a GitHub Actions runner can execute it with no pip install.

DEFENSIVE BY DESIGN. The exact response schema is not documented in a form we have verified, so this script
DUMPS what it receives before parsing, and its parser tries several plausible field spellings rather than
assuming one. If it cannot find prices it says so and prints the shape it got, instead of silently writing an
empty series — a fabricated history is far worse than a missing one.

Output: vast-price-history.jsonl (same schema the sampler writes, tagged source=vast_market_metrics)
        vast-price-history-raw.json (the raw payload, so the parse can be audited/corrected)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://console.vast.ai/api/v0/metrics/gpu"

# Sources, in preference order. Vast's own metrics are the most relevant (it IS our market) but are gated to a
# logged-in console session — the API key is refused with `auth_error: This action requires login`, established
# by running it (CI run 30130107337). gpuwatch is a documented public tracker with 400-day retention, free
# during beta. IMPORTANT CAVEAT for any third-party source: it prices the PLATFORM-WIDE market, whereas we rent
# a narrower filtered subset (verified, rentable, CUDA-capable, RAM/disk floors). Treat an external series as a
# good prior for the SHAPE and DYNAMICS of the distribution, and calibrate its LEVEL against our own offer
# observations before letting it set an absolute reservation price.
GPUWATCH_HISTORY = "https://gpu.watchworks.dev/api/history"
GPUWATCH_PRICES = "https://gpu.watchworks.dev/api/prices"
HERE = os.path.dirname(os.path.abspath(__file__))

# Field spellings we will accept for the price series, cheapest-first ordering preserved.
PRICE_KEYS = ("p10", "P10", "price_p10", "dph_p10", "percentile_10", "q10",
              "min_price", "minPrice", "low", "min",
              "median", "p50", "price_median", "dph_median",
              "avg_price", "avgPrice", "price", "usd_per_hour", "price_per_hour")
TIME_KEYS = ("ts", "time", "timestamp", "t", "date", "bucket", "period")


def _get(path, params=None, api_key=None, timeout=60, base=None):
    url = (base if base is not None else BASE) + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"Accept": "application/json", "User-Agent": "rare-cancers/1.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode() or "{}"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode()[:400]}"
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


def _walk_for_series(obj, depth=0):
    """Find the first list-of-dicts that carries something price-shaped. The schema is unverified, so we search
    rather than assume; returns (path, list) or (None, None)."""
    if depth > 6:
        return None, None
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        keys = set(obj[0].keys())
        if any(k in keys for k in PRICE_KEYS):
            return "", obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            p, found = _walk_for_series(v, depth + 1)
            if found:
                return (k if p == "" else f"{k}.{p}"), found
    return None, None


def _first(d, keys):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


SOURCE_TAG = ["external_price_tracker"]


def parse_series(payload):
    """-> (records, diagnostic). Each record matches the sampler's JSONL schema so both sources can be pooled."""
    path, series = _walk_for_series(payload)
    if not series:
        return [], {"found": False, "top_level_keys": list(payload)[:20] if isinstance(payload, dict) else None,
                    "note": "no price-shaped list-of-dicts found; inspect vast-price-history-raw.json"}
    out = []
    for row in series:
        price = _first(row, PRICE_KEYS)
        ts = _first(row, TIME_KEYS)
        try:
            price = float(price)
        except (TypeError, ValueError):
            continue
        if price <= 0:
            continue
        out.append({"ts": ts, "source": SOURCE_TAG[0], "n_offers": None,
                    "min_floor": price, "median_floor": _num(_first(row, ("median", "p50"))),
                    "floors": []})
    return out, {"found": True, "series_path": path, "n_rows": len(series), "n_parsed": len(out),
                 "sample_row_keys": sorted(series[0].keys())[:25]}


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--gpu", default="RTX 4090")
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--step", default="hour")
    ap.add_argument("--out", default=os.path.join(HERE, "vast-price-history.jsonl"))
    ap.add_argument("--raw", default=os.path.join(HERE, "vast-price-history-raw.json"))
    args = ap.parse_args(argv)
    key = os.environ.get("VAST_API_KEY") or None

    # (base, path, params, auth_mode) — auth_mode: "bearer" | "query" | "none"
    attempts = [
        (BASE, "/history/", {"gpu_name": args.gpu, "days": args.days, "step": args.step}, "bearer"),
        (BASE, "/history/", {"gpu_name": args.gpu, "days": args.days, "step": args.step}, "query"),
        (BASE, "/current/", {"gpu_name": args.gpu}, "query"),
        ("", GPUWATCH_HISTORY, {"gpu": args.gpu, "days": args.days}, "none"),
        ("", GPUWATCH_HISTORY, {"gpu": args.gpu.replace(" ", "+"), "days": args.days}, "none"),
        ("", GPUWATCH_PRICES, {"gpu": args.gpu}, "none"),
    ]
    payload, used, errors = None, None, []
    for base, path, params, mode in attempts:
        p = dict(params)
        k = None
        if mode == "bearer":
            k = key
        elif mode == "query" and key:
            p["api_key"] = key
        data, err = _get(path, p, k, base=base)
        if data:
            payload = data
            used = {"base": base or "(absolute)", "path": path,
                    "params": {kk: vv for kk, vv in p.items() if kk != "api_key"}, "auth_mode": mode}
            break
        errors.append({"path": (base or "") + path, "auth_mode": mode, "error": err})

    if payload is None:
        print(json.dumps({"ok": False, "errors": errors[:8],
                          "note": "every endpoint/parameter combination failed — record the errors and "
                                  "reconsider before assuming the data does not exist"}, indent=1))
        return 1

    SOURCE_TAG[0] = ("vast_market_metrics" if "vast.ai" in (used.get("base", "") + used.get("path", ""))
                     else "gpuwatch_tracker")
    with open(args.raw, "w") as f:
        json.dump({"_source": used, "payload": payload}, f, indent=1)
    records, diag = parse_series(payload)
    if records:
        with open(args.out, "a") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
    prices = sorted(r["min_floor"] for r in records)
    summary = {"ok": True, "endpoint": used, "parse": diag, "n_records": len(records),
               "price_min": prices[0] if prices else None,
               "price_p10": prices[int(0.10 * (len(prices) - 1))] if prices else None,
               "price_median": prices[len(prices) // 2] if prices else None,
               "price_max": prices[-1] if prices else None,
               "wrote": os.path.basename(args.out) if records else None,
               "raw": os.path.basename(args.raw)}
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
