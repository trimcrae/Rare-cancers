#!/usr/bin/env python3
"""
Vast market intelligence — one CI-routed pull of everything the bid policy needs to be set from EVIDENCE.

WHY. The repo's Vast pricing/bid strategy was set from a sequence of one-off snapshots, and the docs that
describe it disagree with each other and with the code (x1.9 / x1.5 / x1.25 all appear as "the" multiplier).
Re-deriving the policy needs four things this repo has never captured in one place:

  1. THE AUCTION'S OWN RULES, from Vast's documentation. Everything downstream rests on "on Vast you pay your
     bid" and "being outbid PAUSES rather than destroys". Both are asserted throughout the repo; neither has a
     quoted primary source in it. If either is wrong the whole policy inverts, so we fetch the pages and keep
     the raw text.
  2. THE NON-COMPUTE COST LINES. `storage_cost` ($/GB/month) bills while an instance is PAUSED, which is the
     term that makes an arbitrarily low bid stop being free. It appears in every offer payload and the repo has
     never recorded it.
  3. A MATCHED bid vs on-demand CROSS-SECTION, per machine_id, wide enough to be a distribution rather than an
     anecdote (the previous n=1 "18% discount" was quoted for a day as if it were a rate).
  4. WHAT `min_bid` ACTUALLY IS — a host-set floor, or the current clearing price. The distinction decides
     whether a "bid" is a limit order in a live auction or just a discount off list. Testable from the data:
     if min_bid/dph_base is a constant, it is a floor; if it varies with occupancy, it is a clearing price.

Pure stdlib so a GitHub Actions runner needs no pip install. Read-only: search + docs only, never rents.

Outputs (all under research/modalities/):
  vast-market-intel.json        parsed + summarised, the analysis input
  vast-market-offers-raw.json   every raw offer row, both rental types, so any parse can be re-audited
  vast-docs-raw.json            raw text of each documentation page fetched
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics as st
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

VAST_API = "https://console.vast.ai/api/v0"
HERE = os.path.dirname(os.path.abspath(__file__))

# Primary sources for the auction rules. Multiple URLs because vast.ai has moved this content between
# vast.ai/article/*, docs.vast.ai/* and a CDN-hosted FAQ; we take whichever answer.
DOC_URLS = [
    "https://docs.vast.ai/documentation/instances/pricing",
    "https://docs.vast.ai/guides/instances/pricing",
    "https://docs.vast.ai/documentation/instances/interruptible-instances",
    "https://docs.vast.ai/documentation/reference/faq",
    "https://vast.ai/article/Rental-Types",
    "https://vast.ai/faq",
    "https://cdn.vast.ai/faq/",
    "https://vast.ai/pricing",
]

# Cards worth pricing: the three we have MEASURED MD throughput for, plus the near neighbours that a $/ns
# ranking could plausibly select if they are cheap enough. Anything else is noise for this decision.
DEFAULT_GPUS = ["rtx4090", "rtx3090", "rtx4080", "rtx4080s", "rtx5090", "rtx3090ti",
                "a10", "l4", "a4000", "a5000", "a6000", "l40s"]

GPUWATCH = "https://gpu.watchworks.dev/api"


def _fetch(url, params=None, api_key=None, timeout=60, want_json=True):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    headers = {"Accept": "application/json, text/html;q=0.9",
               "User-Agent": "Mozilla/5.0 (compatible; rare-cancers-research/1.0)"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
        return (json.loads(raw or "{}") if want_json else raw), None
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")[:2000]
        except Exception:  # noqa: BLE001
            pass
        return None, f"HTTP {e.code}: {body[:400]}"
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


def _html_to_text(html):
    """Crude tag strip — enough to read prose and quote it. We keep the raw HTML too."""
    html = re.sub(r"(?is)<(script|style|nav|footer|svg)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?is)<br[^>]*>|</p>|</div>|</li>|</h[1-6]>", "\n", html)
    txt = re.sub(r"(?s)<[^>]+>", " ", html)
    txt = (txt.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<")
              .replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'"))
    txt = re.sub(r"[ \t]+", " ", txt)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", txt).strip()


# Sentences that decide the policy. We extract them rather than making a human read 8 pages, but we keep the
# full text so the extraction can be checked.
KEY_PATTERNS = [
    r"[^.]*\binterruptible\b[^.]*\.",
    r"[^.]*\bbid\b[^.]*\.",
    r"[^.]*\boutbid\b[^.]*\.",
    r"[^.]*\bpaus\w+[^.]*\.",
    r"[^.]*\bstorage\b[^.]*\.",
    r"[^.]*\bbandwidth\b[^.]*\.",
    r"[^.]*\bstopped\b[^.]*\.",
]


def fetch_docs():
    out = {}
    for url in DOC_URLS:
        body, err = _fetch(url, want_json=False, timeout=45)
        rec = {"url": url, "error": err}
        if body:
            text = _html_to_text(body)
            rec["chars"] = len(text)
            rec["text"] = text[:60000]
            hits = []
            for pat in KEY_PATTERNS:
                for m in re.findall(pat, text, flags=re.I):
                    s = " ".join(m.split())
                    if 30 < len(s) < 400 and s not in hits:
                        hits.append(s)
            rec["key_sentences"] = hits[:60]
        out[url] = rec
        time.sleep(0.5)
    return out


def _query(gpu, rental_type, api_key, limit=512, min_vram_gb=16.0):
    """One offer search. Filters kept DELIBERATELY LOOSE (VRAM + rentable only) so the returned set is the
    market, not our launch filter — a policy calibrated only on hosts we would launch on cannot see the
    distribution it is choosing a quantile of."""
    q = {
        "gpu_name": {"eq": gpu} if False else {},   # placeholder; matched client-side, see below
        "num_gpus": {"eq": 1},
        "gpu_ram": {"gte": min_vram_gb * 1024},
        "rentable": {"eq": True},
        "order": [["dph_total", "asc"]],
        "type": rental_type,
        "limit": limit,
    }
    q.pop("gpu_name")
    data, err = _fetch(f"{VAST_API}/search/asks/", params={"q": json.dumps(q)}, api_key=api_key)
    if err:
        return [], err
    return (data or {}).get("offers", []) or [], None


def _norm_gpu(name):
    return re.sub(r"[^a-z0-9]", "", str(name or "").lower())


KEEP_FIELDS = ("id", "machine_id", "gpu_name", "num_gpus", "gpu_ram", "min_bid", "dph_base", "dph_total",
               "storage_cost", "storage_total_cost", "inet_up_cost", "inet_down_cost", "credit_discount_max",
               "discount_rate", "reliability2", "dlperf", "dlperf_per_dphtotal", "cuda_max_good", "rented",
               "rentable", "duration", "disk_space", "cpu_cores_effective", "cpu_ram", "verified",
               "hosting_type", "geolocation", "inet_up", "inet_down", "start_date", "end_date",
               "bw_nvlink", "compute_cap", "total_flops", "gpu_frac", "is_bid", "search")


def collect_offers(api_key, gpus, min_vram_gb=16.0):
    """One bid query + one on-demand query, then match by machine_id. Two queries, not 2xN: the search returns
    the whole market and we slice client-side, which is both cheaper and avoids per-card query bias."""
    raw = {"bid": [], "on-demand": []}
    errs = {}
    for rtype in ("bid", "on-demand"):
        offers, err = _query(None, rtype, api_key, min_vram_gb=min_vram_gb)
        if err:
            errs[rtype] = err
        raw[rtype] = [{k: o.get(k) for k in KEEP_FIELDS if k in o} for o in offers]
    return raw, errs


def summarise(raw, gpus):
    """Per-card price distributions + the matched bid/on-demand join. Every number here is a summary of rows
    kept in vast-market-offers-raw.json, so nothing below is unauditable."""
    def rows_for(rtype, gpu):
        g = _norm_gpu(gpu)
        return [o for o in raw[rtype] if g and g in _norm_gpu(o.get("gpu_name"))]

    per_card = {}
    for gpu in gpus:
        b = rows_for("bid", gpu)
        d = rows_for("on-demand", gpu)
        if not b and not d:
            continue
        floors = sorted(float(o["min_bid"]) for o in b if o.get("min_bid"))
        od = sorted(float(o["dph_base"]) for o in d if o.get("dph_base"))
        stor = sorted(float(o["storage_cost"]) for o in b if o.get("storage_cost") is not None)
        rec = {
            "n_bid_offers": len(b), "n_ondemand_offers": len(d),
            "floor_usd_h": _dist(floors),
            "ondemand_base_usd_h": _dist(od),
            "storage_usd_gb_month": _dist(stor),
            "n_rented_bid": sum(1 for o in b if o.get("rented")),
        }
        per_card[gpu] = rec

    # --- matched join: the ONLY valid instrument for the interruptible discount --------------------------
    od_by_machine = {}
    for o in raw["on-demand"]:
        try:
            od_by_machine[str(o["machine_id"])] = o
        except (KeyError, TypeError):
            continue
    matched = []
    for o in raw["bid"]:
        m = od_by_machine.get(str(o.get("machine_id")))
        if not m:
            continue
        try:
            floor = float(o["min_bid"]); base = float(m["dph_base"])
        except (KeyError, TypeError, ValueError):
            continue
        if floor <= 0 or base <= 0:
            continue
        matched.append({
            "machine_id": o.get("machine_id"), "gpu": o.get("gpu_name"),
            "floor": round(floor, 5), "ondemand_base": round(base, 5),
            "ratio_od_over_floor": round(base / floor, 4),
            "bid_dph_base": o.get("dph_base"),
            "bid_query_base_equals_floor": abs(float(o.get("dph_base") or 0) - floor) < 1e-6,
            "rented_bid_side": o.get("rented"), "rented_od_side": m.get("rented"),
            "storage_cost": o.get("storage_cost"),
            "reliability2": o.get("reliability2"), "dlperf": o.get("dlperf"),
        })

    ratios = sorted(r["ratio_od_over_floor"] for r in matched)
    # --- IS min_bid A FLOOR OR A CLEARING PRICE? --------------------------------------------------------
    # If min_bid is a fixed host discount off list, ratio is CONSTANT and independent of occupancy.
    # If it is the current clearing price, rented machines should clear HIGHER than idle ones.
    idle = [r["ratio_od_over_floor"] for r in matched if not r.get("rented_bid_side")]
    busy = [r["ratio_od_over_floor"] for r in matched if r.get("rented_bid_side")]
    floor_or_clearing = {
        "n_idle": len(idle), "n_rented": len(busy),
        "median_ratio_idle": round(st.median(idle), 4) if idle else None,
        "median_ratio_rented": round(st.median(busy), 4) if busy else None,
        "distinct_ratio_values": len({round(r, 3) for r in ratios}),
        "interpretation": None,
    }
    if ratios:
        if floor_or_clearing["distinct_ratio_values"] <= 2:
            floor_or_clearing["interpretation"] = (
                "ratio is near-CONSTANT -> min_bid behaves as a fixed host-set floor (a listed discount), "
                "not a live clearing price. A 'bid' is then a discount tier, and bidding above the floor buys "
                "priority against other bidders only.")
        elif idle and busy and st.median(busy) < st.median(idle) - 0.05:
            floor_or_clearing["interpretation"] = (
                "RENTED machines show a LOWER on-demand/floor ratio, i.e. a HIGHER floor -> min_bid rises with "
                "occupancy, consistent with a live clearing price set by the incumbent renter's bid.")
        else:
            floor_or_clearing["interpretation"] = (
                "ratio varies across hosts but shows no clean occupancy signal in this snapshot — per-host "
                "pricing policy dominates. Treat min_bid as host-specific, and compare hosts, not multiples.")

    return {
        "per_card": per_card,
        "matched_n": len(matched),
        "matched_ratio_dist": _dist(ratios),
        "matched_rows": matched,
        "min_bid_semantics": floor_or_clearing,
        "storage_all_cards_usd_gb_month": _dist(
            sorted(float(o["storage_cost"]) for o in raw["bid"] if o.get("storage_cost") is not None)),
    }


def _dist(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    xs = sorted(xs)
    def q(p):
        if len(xs) == 1:
            return xs[0]
        i = p * (len(xs) - 1)
        lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
        return xs[lo] + (i - lo) * (xs[hi] - xs[lo])
    return {"n": len(xs), "min": round(xs[0], 5), "p10": round(q(0.10), 5), "p25": round(q(0.25), 5),
            "median": round(q(0.50), 5), "p75": round(q(0.75), 5), "p90": round(q(0.90), 5),
            "max": round(xs[-1], 5), "mean": round(sum(xs) / len(xs), 5)}


def fetch_history(gpus=("RTX 4090", "RTX 3090", "RTX 4080"), days=90):
    out = {}
    for g in gpus:
        data, err = _fetch(f"{GPUWATCH}/history", params={"gpu": g, "days": days}, timeout=45)
        out[g] = {"error": err} if err else data
        time.sleep(0.4)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpus", default=",".join(DEFAULT_GPUS))
    ap.add_argument("--min-vram-gb", type=float, default=16.0)
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--skip-docs", action="store_true")
    ap.add_argument("--out-dir", default=HERE)
    a = ap.parse_args()

    api_key = os.environ.get("VAST_API_KEY", "").strip()
    gpus = [g.strip() for g in a.gpus.split(",") if g.strip()]
    result = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "has_api_key": bool(api_key), "gpus_requested": gpus}

    if not a.skip_docs:
        print("[intel] fetching Vast documentation ...", flush=True)
        docs = fetch_docs()
        with open(os.path.join(a.out_dir, "vast-docs-raw.json"), "w") as f:
            json.dump(docs, f, indent=1)
        result["docs"] = {u: {"error": d.get("error"), "chars": d.get("chars"),
                              "key_sentences": d.get("key_sentences", [])[:40]}
                          for u, d in docs.items()}
        ok = [u for u, d in docs.items() if not d.get("error")]
        print(f"[intel]   {len(ok)}/{len(docs)} doc pages fetched", flush=True)

    if api_key:
        print("[intel] querying live offers (read-only) ...", flush=True)
        raw, errs = collect_offers(api_key, gpus, a.min_vram_gb)
        with open(os.path.join(a.out_dir, "vast-market-offers-raw.json"), "w") as f:
            json.dump({"generated_utc": result["generated_utc"], "errors": errs, "offers": raw}, f, indent=1)
        result["offer_query_errors"] = errs
        result["n_offers"] = {k: len(v) for k, v in raw.items()}
        if raw["bid"] or raw["on-demand"]:
            result["market"] = summarise(raw, gpus)
        print(f"[intel]   bid={len(raw['bid'])} on-demand={len(raw['on-demand'])}", flush=True)
    else:
        result["offer_query_errors"] = {"all": "VAST_API_KEY not set"}

    print("[intel] fetching external price history ...", flush=True)
    result["history"] = fetch_history(days=a.days)

    path = os.path.join(a.out_dir, "vast-market-intel.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=1)
    print(f"[intel] wrote {path}", flush=True)

    m = result.get("market") or {}
    if m.get("matched_ratio_dist"):
        d = m["matched_ratio_dist"]
        print(f"[intel] matched n={m['matched_n']}  on-demand/floor  median={d['median']}  "
              f"p25={d['p25']}  p75={d['p75']}", flush=True)
        print(f"[intel] min_bid semantics: {(m.get('min_bid_semantics') or {}).get('interpretation')}",
              flush=True)
    if m.get("storage_all_cards_usd_gb_month"):
        print(f"[intel] storage $/GB/month: {m['storage_all_cards_usd_gb_month']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
