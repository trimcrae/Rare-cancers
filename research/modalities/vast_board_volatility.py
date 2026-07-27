#!/usr/bin/env python3
"""HOW FAST DOES THE CHEAP END OF THE VAST BOARD ACTUALLY MOVE — and is hourly polling costing us anything?

★ THE QUESTION THIS EXISTS FOR (trimcrae, 2026-07-27): *"Is checking hourly enough? I would think the cheap
machines get gobbled up quick and would need to be acted on quickly."*

He was asking against a real observation: on 2026-07-27 the ternary market gate read **1.261× basis at
9:13:04 AM ET** and the launch job it dispatched re-read **2.436× at 9:16:28 AM ET**, 3m24s later, across an
image pull. The same thing happened again at 9:23 → 9:26 (1.455× → 1.904×). Read as market churn, that says
the cheap end turns over inside three minutes and hourly polling is hopeless.

**But "the board doubled in three minutes" is a HYPOTHESIS, not a diagnosis** (CLAUDE.md §4), and there are at
least three mechanisms that produce that observation and imply completely different fixes:

  H1  MARKET CHURN — the cheap hosts really were rented in those three minutes.  Fix: poll faster.
  H2  READ NOISE — the same query answered twice returns materially different offer sets.  Fix: poll faster
      does NOTHING; fix the read (or average it), because you are chasing your own measurement error.
  H3  COMPOSITION / TRUNCATION — `_vast_offer_query` sets **no `limit`**, and orders by `dph_total asc`. We
      then re-rank client-side by `$/ns`, and only cards in `vast_cost_model.MEASURED_NS_PER_DAY_84K` are
      priceable at all. So the window we see is "the cheapest-by-$/hr N offers", and which of those happen to
      be *gradeable* swings hard: the same snapshots show `priceable` moving 9 → 52 out of a stable ~46–63
      `qualifying`.  Fix: read the whole board and widen the bench table — cadence is irrelevant.

This module's job is to DISCRIMINATE, then to price the answer. It has three parts and each is separable:

  `--collect`   the measurement. A read-only, $0, rents-nothing sampler that runs inside ONE CI job and takes
                a **paired** board read every tick. The pairing is the whole point: two identical queries 20 s
                apart bound H2 directly. A third read per tick, with the launcher's own (unlimited, i.e.
                DEFAULT-limited) query, bounds H3 against the full `limit=512` board.

  `--analyse`   pure functions over the collected JSONL: the read-to-read noise floor, Kaplan–Meier survival
                of a below-the-line offer, how often the board is buyable at all, and the marginal value of
                each poll cadence expressed in **dollars per day**, which is the only form the question can
                actually be answered in.

  `--mine-git`  the free first pass: the same statistics recovered from every market snapshot this repo has
                already committed. Run this before spending any wall-clock on collection — and read its
                `sufficient` verdict, because that history is an IRREGULAR, SELF-SELECTED sample (a snapshot
                exists because a lane wanted to launch) and is close to useless for survival.

===============================================================================================================
WHAT IT DELIBERATELY DOES NOT DO
===============================================================================================================
**It never rents.** Every call is `GET /search/asks/`. No instance is created, no bid is placed, nothing is
destroyed, and the module imports no launcher entry point that could.

**It does not probe the rate limit by saturating it.** The obvious way to find Vast's throttle is to ramp
request rate until the edge answers 403 — and that is exactly what must NOT be done here: one API key drives
every lane, and a deliberate trip would take down the live fan-out's supervision tick, which is the failure
already on record (2026-07-27 11:08–11:10 AM ET and 1:21 PM ET). Headroom is therefore measured PASSIVELY:
every response's status and rate-limit-ish headers are recorded, and any 403 met while sampling gently is
itself the datum. See `--analyse`'s `rate_limit` block.

**It does not set the buy line.** `inflight_usd_per_ns.APPROVED_USD_PER_NS` owns it (CLAUDE.md §1); this
module imports it. A below-the-line offer here means an offer at or under **that** absolute $/ns.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://console.vast.ai/api/v0"

# Headers worth keeping if the edge ever sends them. Vast documents no rate-limit header, so this is
# speculative BY DESIGN: recording an absent header is how we learn it is absent, and a header that appears
# later is free evidence. Never assume one exists.
_HEADERS_OF_INTEREST = (
    "x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset", "ratelimit-limit",
    "ratelimit-remaining", "ratelimit-reset", "retry-after", "x-request-id", "server", "cf-ray",
)


# =============================================================================================================
# COLLECTION — CI only (the dev sandbox's egress proxy 403s console.vast.ai, CLAUDE.md §6)
# =============================================================================================================
def _read_board(key, query, limit=None, timeout=60):
    """ONE read of `/search/asks/`. Returns a record dict; never raises — a failed read IS an observation.

    Deliberately NOT `gpu_backend._vast_request`: that helper retries 403/429 internally with a back-off, which
    is right for a launcher and wrong for a measurement — it would silently paper over the very throttling this
    is trying to quantify. Here a 403 is recorded as a 403.
    """
    q = dict(query)
    if limit is not None:
        q["limit"] = int(limit)
    url = BASE + "/search/asks/?" + urllib.parse.urlencode({"q": json.dumps(q)})
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}",
                                               "Accept": "application/json"})
    t0 = time.time()
    rec = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "limit": limit}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode() or "{}")
            rec["status"] = r.status
            rec["headers"] = {k: v for k, v in
                              ((h.lower(), r.headers.get(h)) for h in _HEADERS_OF_INTEREST) if v}
            rec["offers"] = body.get("offers") or []
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode()[:300]
        except Exception:  # noqa: BLE001
            pass
        rec.update({"status": e.code, "err": detail, "offers": [],
                    # The discriminator from CLAUDE.md §6: nginx HTML => edge/WAF throttle; a JSON envelope
                    # => Vast's own application answering. Recorded rather than inferred later.
                    "err_is_html": detail.lstrip().lower().startswith("<html")})
    except Exception as e:  # noqa: BLE001
        rec.update({"status": None, "err": f"{type(e).__name__}: {e}", "offers": []})
    rec["elapsed_s"] = round(time.time() - t0, 3)
    rec["n_offers"] = len(rec.get("offers") or [])
    return rec


def _slim(offers, res):
    """Offer dicts -> the small rows we persist, each carrying its `$/ns` where the card is benched.

    `$/ns` is computed HERE, at collection time, by the launcher's own `rank_offers_by_usd_per_ns`, so the
    analysis is a pure function of the JSONL and can never disagree with what the launcher would have paid.
    """
    from gpu_backend import rank_offers_by_usd_per_ns  # noqa: PLC0415  (CI-only dependency)
    measured, capable = rank_offers_by_usd_per_ns(offers, res)
    upn = {id(o): (u, p) for u, p, o in measured}
    rows = []
    for price, o in capable:
        u, p = upn.get(id(o), (None, price))
        rows.append({"id": o.get("id"), "m": o.get("machine_id"), "gpu": o.get("gpu_name"),
                     "bid": round(float(price), 5) if price is not None else None,
                     "dph": o.get("dph_total"), "u": round(u, 6) if u is not None else None})
    return rows, len(capable), len(measured)


def collect(out_path, minutes=180, tick_s=60, pair_gap_s=20, push_branch=None, push_every_s=600):
    """The sampler. Read-only, $0. One JSONL line per board read.

    Three reads per tick, evenly spaced so the burst pattern that trips the edge (≈8 calls in seconds) is
    never produced — ~3 requests/minute, one every 20 s:

      R1  t+0             `limit=512`  the FULL board
      R2  t+pair_gap      `limit=512`  identical query, 20 s later -> the read-to-read NOISE FLOOR
      R3  t+2*pair_gap    no `limit`   exactly what the launcher's gate sees -> the TRUNCATION effect

    Checkpointed continuously (CLAUDE.md §6): the JSONL is flushed after every read and pushed to a cache
    branch every `push_every_s`, so a timeout or a cancelled run still yields every tick collected so far.
    """
    from gpu_backend import ResourceSpec, _vast_offer_query  # noqa: PLC0415
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("VAST_API_KEY is not set — this sampler only runs in CI (the dev sandbox 403s Vast)")
    res = ResourceSpec()
    query = _vast_offer_query(res)
    deadline = time.time() + minutes * 60
    fh = open(out_path, "a")
    tick, last_push, backoff = 0, time.time(), 0.0
    print(f"[collect] {minutes} min, tick {tick_s}s, pair gap {pair_gap_s}s -> {out_path}", flush=True)
    print(f"[collect] query = {json.dumps(query)}", flush=True)
    slots = (("R1", 512), ("R2", 512), ("R3", None))
    while time.time() < deadline:
        t_tick, throttled = time.time(), False
        for i, (slot, limit) in enumerate(slots):
            rec = _read_board(key, query, limit=limit)
            offers = rec.pop("offers", [])
            try:
                rec["rows"], rec["qualifying"], rec["priceable"] = _slim(offers, res)
            except Exception as e:  # noqa: BLE001  a ranking bug must not end a 3-hour collection
                rec["rows"], rec["rank_err"] = [], f"{type(e).__name__}: {e}"
            rec.update({"tick": tick, "slot": slot, "backoff_s": round(backoff, 1)})
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
            if rec.get("status") in (403, 429, 503):
                throttled = True
            best = min((r["u"] for r in rec["rows"] if r.get("u")), default=None)
            print(f"  t{tick:>3} {slot} {rec['utc']} status={rec.get('status')} n={rec.get('n_offers')} "
                  f"priceable={rec.get('priceable')} "
                  f"best={('$%.6f/ns' % best) if best else 'none'}", flush=True)
            if i < len(slots) - 1:
                time.sleep(max(0.0, t_tick + pair_gap_s * (i + 1) - time.time()))
        if push_branch and time.time() - last_push >= push_every_s:
            _push(out_path, push_branch)
            last_push = time.time()
        tick += 1
        # ★ BACK OFF ON A THROTTLE — A MEASUREMENT MUST NEVER BECOME THE OUTAGE IT IS MEASURING.
        # One API key drives every lane (CLAUDE.md §6), and a Vast edge 403 is a throttle verdict on the KEY,
        # not on this job. Continuing at the same rate while throttled therefore risks EXTENDING an outage
        # that the live fan-out's supervision tick and the ternary watchdog sit behind — which is the exact
        # failure already on record (2026-07-27 11:08-11:10 AM and 1:21 PM ET). A throttled tick doubles the
        # inter-tick sleep (from 60 s, capped at 8 min); a clean tick halves it back. The 403s are still
        # RECORDED — backing off changes our load, never the observation.
        backoff = min(480.0, max(60.0, backoff * 2)) if throttled else max(0.0, backoff / 2)
        time.sleep(max(0.0, t_tick + tick_s + backoff - time.time()))
    fh.close()
    if push_branch:
        _push(out_path, push_branch)
    print(f"[collect] done: {tick} ticks", flush=True)


def _push(path, branch):
    """Best-effort checkpoint of the series to a cache branch, via a SEPARATE clone.

    Never touches the job's own working tree. `vast-price-sample.yml` records what happens when a sampler
    checks out another branch on top of a modified tracked file: git refuses the switch and every run fails at
    the persist step. A throwaway clone cannot hit that, and a push failure must never end the collection.
    """
    work = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "volpush")
    try:
        if not os.path.isdir(os.path.join(work, ".git")):
            url = subprocess.run(["git", "-C", HERE, "remote", "get-url", "origin"],
                                 capture_output=True, text=True).stdout.strip()
            subprocess.run(["git", "clone", "--depth", "1", "--branch", branch, url, work],
                           capture_output=True, text=True, check=False)
            if not os.path.isdir(os.path.join(work, ".git")):
                subprocess.run(["git", "clone", "--depth", "1", url, work],
                               capture_output=True, text=True, check=False)
                subprocess.run(["git", "-C", work, "checkout", "--orphan", branch],
                               capture_output=True, text=True, check=False)
                subprocess.run(["git", "-C", work, "rm", "-rf", "."], capture_output=True, text=True)
        dst = os.path.join(work, "research", "modalities")
        os.makedirs(dst, exist_ok=True)
        subprocess.run(["cp", path, os.path.join(dst, os.path.basename(path))], check=False)
        for cmd in (["git", "-C", work, "config", "user.name", "github-actions[bot]"],
                    ["git", "-C", work, "config", "user.email",
                     "41898282+github-actions[bot]@users.noreply.github.com"],
                    ["git", "-C", work, "add", "-A"],
                    ["git", "-C", work, "commit", "-m",
                     f"vast board volatility sample {time.strftime('%FT%TZ', time.gmtime())}"],
                    ["git", "-C", work, "push", "origin", f"HEAD:{branch}"]):
            subprocess.run(cmd, capture_output=True, text=True, check=False)
        print(f"  [checkpoint] pushed {os.path.basename(path)} to {branch}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  [checkpoint] push failed ({e}) — collection continues", flush=True)


# =============================================================================================================
# ANALYSIS — PURE. Every function below is a function of the collected records only.
# =============================================================================================================
def _line():
    from inflight_usd_per_ns import APPROVED_USD_PER_NS  # noqa: PLC0415
    return APPROVED_USD_PER_NS


def load(path):
    out = []
    with open(path) as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except json.JSONDecodeError:
                    continue
    return out


def best_n_mean(rows, n):
    """The statistic the market gate actually decides on: the MEAN $/ns over the `n` cheapest priceable
    offers. Not the single best — a fleet of n buys the n best, and pricing off one host flatters a thin
    board exactly when thinness is what is being detected (`ternary_vast_launch.market_gate`)."""
    us = sorted(r["u"] for r in rows if r.get("u") is not None)
    if not us:
        return None
    take = us[:max(1, int(n))]
    return sum(take) / len(take)


def read_noise(records):
    """H2: how different are two IDENTICAL queries `pair_gap` apart?

    This is the noise floor every other number in this module must be read against. If reads 20 s apart move
    the decision statistic as much as reads an hour apart, then the cadence question is moot and the finding
    is that the gate is deciding on noise.
    """
    by_tick = defaultdict(dict)
    for r in records:
        if r.get("slot") in ("R1", "R2") and r.get("status") == 200:
            by_tick[r["tick"]][r["slot"]] = r
    pairs, out = 0, {"jaccard": [], "d_best4_frac": [], "d_n_offers": [], "gap_s": [],
                     "d_priceable": [], "vanished": [], "appeared": []}
    for _t, d in sorted(by_tick.items()):
        if "R1" not in d or "R2" not in d:
            continue
        a, b = d["R1"], d["R2"]
        sa = {r["m"] for r in a.get("rows", [])}
        sb = {r["m"] for r in b.get("rows", [])}
        if not (sa or sb):
            continue
        pairs += 1
        out["jaccard"].append(len(sa & sb) / len(sa | sb))
        out["vanished"].append(len(sa - sb))
        out["appeared"].append(len(sb - sa))
        out["d_n_offers"].append(abs((a.get("n_offers") or 0) - (b.get("n_offers") or 0)))
        out["d_priceable"].append(abs((a.get("priceable") or 0) - (b.get("priceable") or 0)))
        ba, bb = best_n_mean(a.get("rows", []), 4), best_n_mean(b.get("rows", []), 4)
        if ba and bb:
            out["d_best4_frac"].append(abs(ba - bb) / ((ba + bb) / 2))
        out["gap_s"].append(_dt(a["utc"], b["utc"]))
    return {"pairs": pairs, **{k: _stats(v) for k, v in out.items()}}


def _dt(a, b):
    f = "%Y-%m-%dT%H:%M:%SZ"
    return abs(time.mktime(time.strptime(b, f)) - time.mktime(time.strptime(a, f)))


def _stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    xs = sorted(xs)
    n = len(xs)
    return {"n": n, "mean": round(sum(xs) / n, 6), "p50": round(xs[n // 2], 6),
            "p90": round(xs[min(n - 1, int(0.9 * n))], 6), "max": round(xs[-1], 6)}


def series(records, slot="R1"):
    """The ground-truth time series: one entry per tick, `{t, utc, rows}` for successful reads of one slot."""
    out = []
    for r in sorted(records, key=lambda x: (x.get("tick", 0), x.get("slot", ""))):
        if r.get("slot") == slot and r.get("status") == 200:
            out.append({"t": r["tick"], "utc": r["utc"], "rows": r.get("rows", []),
                        "n_offers": r.get("n_offers"), "priceable": r.get("priceable"),
                        "qualifying": r.get("qualifying")})
    return out


def spells(ser, line=None, tick_s=60):
    """Every maximal run of consecutive ticks in which a machine sits AT OR BELOW the buy line.

    Returns [{machine, start, end, ticks, minutes, censored_left, censored_right, ended_by}]. `ended_by`
    separates the two mechanisms, which have opposite implications:

      "taken"     — the machine left the board entirely.        Faster polling would have helped.
      "repriced"  — still on the board, now above the line.     Faster polling would have helped.
      "gone_dark" — the read failed / the tick is missing.      Not evidence about the market.

    Left-censored spells (already open at the first observed tick) have an UNKNOWN true duration and are
    excluded from the duration distribution rather than being counted at their observed length, which would
    bias every quantile downward. They are counted and reported separately.
    """
    line = _line() if line is None else line
    seen = {}          # machine -> {"start": t, "last": t}
    done = []
    present_by_t = {}
    for s in ser:
        under = {r["m"]: r["u"] for r in s["rows"] if r.get("u") is not None and r["u"] <= line}
        allm = {r["m"] for r in s["rows"]}
        present_by_t[s["t"]] = (under, allm)
    ts = sorted(present_by_t)
    first_t, last_t = (ts[0], ts[-1]) if ts else (None, None)
    for t in ts:
        under, allm = present_by_t[t]
        for m in list(seen):
            if m not in under:
                sp = seen.pop(m)
                done.append({"machine": m, "start": sp["start"], "end": sp["last"],
                             "ticks": sp["last"] - sp["start"] + 1,
                             "ended_by": "repriced" if m in allm else "taken",
                             "censored_left": sp["start"] == first_t, "censored_right": False})
        for m in under:
            if m not in seen:
                seen[m] = {"start": t, "last": t}
            else:
                seen[m]["last"] = t
    for m, sp in seen.items():
        done.append({"machine": m, "start": sp["start"], "end": sp["last"],
                     "ticks": sp["last"] - sp["start"] + 1, "ended_by": "still_open",
                     "censored_left": sp["start"] == first_t, "censored_right": True})
    for d in done:
        d["minutes"] = round(d["ticks"] * tick_s / 60.0, 2)
    return done


def kaplan_meier(spell_list, tick_s=60):
    """S(t) for "an offer is still below the line after t minutes", right-censoring the spells still open.

    Plain KM, no scipy: at each observed failure time, S *= (1 - d/n). Left-censored spells are dropped (see
    `spells`). Returns {"median_minutes", "p25", "p75", "curve": [(minutes, S)], "n", "n_events"}.
    """
    obs = [s for s in spell_list if not s["censored_left"]]
    if not obs:
        return {"n": 0, "n_events": 0, "median_minutes": None, "curve": []}
    events = sorted({s["ticks"] for s in obs if not s["censored_right"]})
    n_at_risk = len(obs)
    surv, curve = 1.0, []
    for e in events:
        at_risk = sum(1 for s in obs if s["ticks"] >= e)
        d = sum(1 for s in obs if s["ticks"] == e and not s["censored_right"])
        if at_risk <= 0:
            break
        surv *= (1 - d / at_risk)
        curve.append((round(e * tick_s / 60.0, 2), round(surv, 4)))
    def _q(p):
        for mins, s in curve:
            if s <= p:
                return mins
        return None
    return {"n": n_at_risk, "n_events": sum(1 for s in obs if not s["censored_right"]),
            "median_minutes": _q(0.5), "p25_minutes": _q(0.75), "p75_minutes": _q(0.25),
            "curve": curve}


def availability(ser, line=None, needs=(1, 4, 19)):
    """How often the board carries at least k offers at or below the line, and what the best-k mean is."""
    line = _line() if line is None else line
    out = {}
    for k in needs:
        hits = 0
        for s in ser:
            us = sorted(r["u"] for r in s["rows"] if r.get("u") is not None)
            if len(us) >= k and (sum(us[:k]) / k) <= line:
                hits += 1
        out[f"fleet_of_{k}_buyable_frac"] = round(hits / len(ser), 4) if ser else None
    under = [sum(1 for r in s["rows"] if r.get("u") is not None and r["u"] <= line) for s in ser]
    out["ticks"] = len(ser)
    out["n_under_line"] = _stats(under)
    out["any_under_line_frac"] = round(sum(1 for u in under if u) / len(under), 4) if under else None
    return out


def cadence_value(ser, cadences_min, n_units=4, line=None, tick_s=60, wait_budget_min=None):
    """★ THE DELIVERABLE ARITHMETIC: what does each poll cadence actually buy, in $/ns?

    Model, stated so it can be argued with. A lane wants `n_units` hosts. It polls every `c` minutes. At each
    poll it sees the board and buys iff the best-`n_units` mean clears the line; otherwise it holds and
    re-checks at the next poll (CLAUDE.md §6 — a hold costs nothing, the work is checkpointed). So the price
    a cadence delivers is:

        E[ best_n mean at the FIRST polling instant that clears the line, within `wait_budget` ]

    averaged over every possible phase offset — because we do not get to choose when the work becomes ready,
    and evaluating one phase is how you accidentally measure luck. If no polling instant inside the budget
    clears, the launch does not happen in that window; that is reported as `miss_frac` rather than being
    quietly folded into the mean, since a miss is a delay, not a price.

    A cadence faster than the sampling interval cannot be evaluated from this data and is skipped rather than
    interpolated.
    """
    line = _line() if line is None else line
    stat = [(s["t"], best_n_mean(s["rows"], n_units)) for s in ser]
    stat = [(t, v) for t, v in stat if v is not None]
    if not stat:
        return {}
    ts = [t for t, _ in stat]
    val = dict(stat)
    horizon = max(ts) - min(ts)
    budget_ticks = int((wait_budget_min * 60 / tick_s)) if wait_budget_min else horizon
    out = {}
    for c in cadences_min:
        step = int(round(c * 60 / tick_s))
        if step < 1:
            continue
        prices, waits, misses, phases = [], [], 0, 0
        for phase in range(min(step, len(ts))):
            for start in ts:
                if (start - ts[0]) % max(1, step) != phase % max(1, step):
                    continue
                phases += 1
                got = None
                k = start
                while k <= start + budget_ticks and k <= ts[-1]:
                    v = val.get(k)
                    if v is not None and v <= line:
                        got = (v, k - start)
                        break
                    k += step
                if got:
                    prices.append(got[0])
                    waits.append(got[1] * tick_s / 60.0)
                else:
                    misses += 1
        n = len(prices)
        out[f"{c:g}min"] = {
            "poll_step_ticks": step,
            "opportunities": phases,
            "buy_frac": round(n / phases, 4) if phases else None,
            "miss_frac": round(misses / phases, 4) if phases else None,
            "mean_usd_per_ns_paid": round(sum(prices) / n, 6) if n else None,
            "p90_usd_per_ns_paid": round(sorted(prices)[min(n - 1, int(0.9 * n))], 6) if n else None,
            "mean_wait_min": round(sum(waits) / len(waits), 2) if waits else None,
            "p90_wait_min": round(sorted(waits)[min(len(waits) - 1, int(0.9 * len(waits)))], 2) if waits else None,
        }
    return out


def buyable_minutes(ser, cadences_min, n_units=4, line=None, tick_s=60):
    """"Buyable-offer-minutes" — the metric trimcrae's question implies, made concrete.

    Ground truth: the number of tick-minutes during which the best-`n_units` mean is under the line. A poller
    at cadence `c` can only ACT at its polling instants, so it captures at most `c` minutes of credit per
    clearing instant, and a clearing WINDOW shorter than `c` may be missed entirely. Reports, per cadence:
    windows seen vs windows that existed, and the fraction of buyable minutes a poller could act within.
    """
    line = _line() if line is None else line
    seq = [(s["t"], best_n_mean(s["rows"], n_units)) for s in ser]
    seq = [(t, v) for t, v in seq if v is not None]
    if not seq:
        return {}
    ts = [t for t, _ in seq]
    clear = {t: (v is not None and v <= line) for t, v in seq}
    windows, cur = [], None
    for t in ts:
        if clear[t] and cur is None:
            cur = [t, t]
        elif clear[t]:
            cur[1] = t
        elif cur is not None:
            windows.append(tuple(cur)); cur = None
    if cur is not None:
        windows.append(tuple(cur))
    total_buyable = sum(1 for t in ts if clear[t]) * tick_s / 60.0
    out = {"observed_minutes": round(len(ts) * tick_s / 60.0, 1),
           "buyable_minutes": round(total_buyable, 1),
           "buyable_frac": round(total_buyable / (len(ts) * tick_s / 60.0), 4) if ts else None,
           "n_windows": len(windows),
           "window_minutes": _stats([(b - a + 1) * tick_s / 60.0 for a, b in windows]),
           "by_cadence": {}}
    for c in cadences_min:
        step = int(round(c * 60 / tick_s))
        if step < 1:
            continue
        seen, tot = 0, 0
        for phase in range(step):
            polls = [t for t in ts if (t - ts[0]) % step == phase]
            tot += len(windows)
            seen += sum(1 for a, b in windows if any(a <= p <= b for p in polls))
        out["by_cadence"][f"{c:g}min"] = {
            "windows_seen_frac": round(seen / tot, 4) if tot else None,
            "windows_missed_per_day": round((1 - seen / tot) * len(windows) * (1440.0 /
                                            (len(ts) * tick_s / 60.0)), 2) if tot and ts else None,
        }
    return out


def dollars_per_day(cadence_block, ns_per_day, baseline="60min"):
    """Translate a cadence table into the only unit the decision can be made in: **$/day**.

    `ns_per_day` is how much simulated time the program actually buys in a day — supply it from the ladder,
    never from a guess. The saving of cadence c over the baseline is
    `(mean_$/ns[baseline] - mean_$/ns[c]) * ns_per_day`. A negative saving is reported as such.
    """
    base = (cadence_block.get(baseline) or {}).get("mean_usd_per_ns_paid")
    out = {}
    for k, v in cadence_block.items():
        m = v.get("mean_usd_per_ns_paid")
        out[k] = None if (base is None or m is None) else round((base - m) * ns_per_day, 2)
    return {"baseline": baseline, "ns_per_day": ns_per_day, "saving_usd_per_day_vs_baseline": out}


def truncation(records):
    """H3: what the launcher's DEFAULT-limited query misses against the full `limit=512` board.

    `gpu_backend._vast_offer_query` sets no `limit` and orders by `dph_total asc`. We then re-rank by `$/ns`.
    Those are different orderings, so a truncated cheapest-by-$/hr window is NOT the cheapest-by-$/ns window,
    and the offers it drops are systematically the fast expensive cards. This measures the gap directly.
    """
    by_tick = defaultdict(dict)
    for r in records:
        if r.get("status") == 200 and r.get("slot") in ("R1", "R3"):
            by_tick[r["tick"]][r["slot"]] = r
    full_n, dflt_n, d4, better = [], [], [], 0
    cmp_n = 0
    for _t, d in sorted(by_tick.items()):
        if "R1" not in d or "R3" not in d:
            continue
        f, g = d["R1"], d["R3"]
        full_n.append(f.get("n_offers") or 0)
        dflt_n.append(g.get("n_offers") or 0)
        bf, bg = best_n_mean(f.get("rows", []), 4), best_n_mean(g.get("rows", []), 4)
        if bf and bg:
            cmp_n += 1
            d4.append((bg - bf) / bf)
            if bf < bg - 1e-9:
                better += 1
    return {"ticks_compared": cmp_n,
            "n_offers_full": _stats(full_n), "n_offers_default": _stats(dflt_n),
            "default_best4_excess_frac": _stats(d4),
            "full_board_strictly_better_frac": round(better / cmp_n, 4) if cmp_n else None}


def rate_limit(records):
    """PASSIVE headroom: what the edge actually did while we sampled gently. No saturation probe (see module
    docstring — one key drives every lane and a deliberate trip would take down a live fleet's supervision)."""
    by_status = defaultdict(int)
    html403, hdrs = 0, {}
    for r in records:
        by_status[str(r.get("status"))] += 1
        if r.get("status") == 403 and r.get("err_is_html"):
            html403 += 1
        for k, v in (r.get("headers") or {}).items():
            hdrs.setdefault(k, v)
    n = len(records)
    span = 0.0
    ok = [r for r in records if r.get("utc")]
    if len(ok) > 1:
        span = _dt(ok[0]["utc"], ok[-1]["utc"])
    return {"reads": n, "by_status": dict(by_status), "html_403_edge_throttles": html403,
            "observed_req_per_min": round(n / (span / 60.0), 2) if span else None,
            "rate_limit_headers_seen": hdrs or "none — Vast sends no rate-limit header on this route",
            "elapsed_s": _stats([r.get("elapsed_s") for r in records])}


# =============================================================================================================
# THE FREE FIRST PASS — mine what is already committed
# =============================================================================================================
_SNAPSHOTS = (("research/modalities/ternary-vast-market-hold.json", "offers", "min_bid_usd_h"),
              ("research/modalities/step1-fanout-market-hold.json", "offers_priced", "min_bid"))


def mine_git(repo=None):
    """Recover the same panel from every committed market snapshot. FREE — no API call, no spend.

    Returns the panel plus an explicit `sufficient` verdict. Read that verdict before trusting anything else
    here: these snapshots are an IRREGULAR, SELF-SELECTED sample (one exists because a lane wanted to launch,
    and it records only the `n_units` offers the gate used), so they can bound persistence from below but
    cannot measure survival, and they cannot see an offer the gate did not need.
    """
    repo = repo or os.path.abspath(os.path.join(HERE, "..", ".."))
    def sh(*a):
        return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout
    snaps = []
    for path, key, pk in _SNAPSHOTS:
        for ln in sh("log", "--format=%H %aI", "--", path).strip().splitlines():
            h, _d = ln.split()
            try:
                o = json.loads(sh("show", f"{h}:{path}"))
            except Exception:  # noqa: BLE001
                continue
            rows = [{"m": x.get("machine_id"), "gpu": x.get("gpu"), "u": x.get("usd_per_ns"),
                     "bid": x.get(pk)} for x in (o.get(key) or [])]
            dep = o.get("depth") or o.get("board_depth") or {}
            snaps.append({"utc": o.get("utc"), "src": os.path.basename(path), "rows": rows,
                          "n_offers": dep.get("offers_returned"), "priceable": dep.get("priceable"),
                          "qualifying": dep.get("qualifying"), "truncated_to_used": len(rows)})
    snaps = [s for s in snaps if s["utc"]]
    snaps.sort(key=lambda s: s["utc"])
    line = _line()
    # Persistence lower bound: how long does a machine keep appearing under the line across snapshots?
    firstlast = {}
    for s in snaps:
        for r in s["rows"]:
            if r.get("u") is not None and r["u"] <= line:
                fl = firstlast.setdefault(r["m"], [s["utc"], s["utc"], 0])
                fl[1] = s["utc"]; fl[2] += 1
    spans = []
    for m, (a, b, k) in firstlast.items():
        if k > 1:
            spans.append({"machine": m, "first": a, "last": b, "appearances": k,
                          "span_minutes": round(_dt(a, b) / 60.0, 1)})
    spans.sort(key=lambda x: -x["span_minutes"])
    gaps = [round(_dt(snaps[i]["utc"], snaps[i + 1]["utc"]) / 60.0, 1) for i in range(len(snaps) - 1)]
    return {
        "_what": "committed market snapshots, mined for cheap-end persistence. FREE — no API call.",
        "n_snapshots": len(snaps),
        "span_hours": round(_dt(snaps[0]["utc"], snaps[-1]["utc"]) / 3600.0, 2) if len(snaps) > 1 else 0,
        "gap_minutes": _stats(gaps),
        "buy_line_usd_per_ns": line,
        "machines_seen_under_line": len(firstlast),
        "machines_under_line_more_than_once": len(spans),
        "persistence_lower_bound_minutes": _stats([s["span_minutes"] for s in spans]),
        "longest_persisting": spans[:12],
        "board_depth_swing": {"offers_returned": _stats([s["n_offers"] for s in snaps]),
                              "priceable": _stats([s["priceable"] for s in snaps]),
                              "qualifying": _stats([s["qualifying"] for s in snaps])},
        "sufficient": False,
        "why_not_sufficient":
            "These snapshots are irregular and SELF-SELECTED — one exists only because a lane wanted to "
            "launch — and each records just the n_units offers the gate consumed, not the board. They give a "
            "LOWER BOUND on persistence (a machine seen under the line at two times was under it at both) "
            "and nothing about when an offer actually vanished. Survival needs an even-cadence read-only "
            "sampler: `--collect`.",
        "panel": snaps,
    }


# =============================================================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--collect", action="store_true", help="run the read-only sampler (CI only, $0)")
    ap.add_argument("--minutes", type=float, default=180)
    ap.add_argument("--tick-s", type=float, default=60)
    ap.add_argument("--pair-gap-s", type=float, default=20)
    ap.add_argument("--out", default=os.path.join(HERE, "vast-board-volatility.jsonl"))
    ap.add_argument("--push-branch", default=None)
    ap.add_argument("--analyse", metavar="JSONL", default=None)
    ap.add_argument("--mine-git", action="store_true")
    ap.add_argument("--units", type=int, default=4, help="fleet size the cadence model prices")
    ap.add_argument("--ns-per-day", type=float, default=None,
                    help="simulated ns the programme buys per day, for the $/day translation")
    ap.add_argument("--cadences", default="1,2,5,10,15,30,60,120")
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args(argv)

    if a.collect:
        collect(a.out, minutes=a.minutes, tick_s=a.tick_s, pair_gap_s=a.pair_gap_s,
                push_branch=a.push_branch)
        return 0

    if a.mine_git:
        rep = mine_git()
        out = a.json_out or os.path.join(HERE, "vast-board-volatility-gitmine.json")
        with open(out, "w") as fh:
            json.dump(rep, fh, indent=1)
        slim = {k: v for k, v in rep.items() if k != "panel"}
        print(json.dumps(slim, indent=1))
        print(f"\n-> {out}  (full panel inside)")
        return 0

    if a.analyse:
        recs = load(a.analyse)
        ser = series(recs, "R1")
        cad = [float(x) for x in a.cadences.split(",") if x.strip()]
        sp = spells(ser, tick_s=a.tick_s)
        rep = {"_what": "Vast cheap-end volatility: does poll cadence matter, and what does hourly cost?",
               "buy_line_usd_per_ns": _line(),
               "reads": len(recs), "ticks_analysed": len(ser),
               "tick_seconds": a.tick_s, "fleet_units": a.units,
               "read_noise_floor": read_noise(recs),
               "truncation_default_vs_full_board": truncation(recs),
               "availability": availability(ser),
               "offer_survival_km": kaplan_meier(sp, tick_s=a.tick_s),
               "spell_endings": dict(_count([s["ended_by"] for s in sp])),
               "spells": sp,
               "buyable_minutes": buyable_minutes(ser, cad, n_units=a.units),
               "cadence_value": cadence_value(ser, cad, n_units=a.units, tick_s=a.tick_s),
               "rate_limit": rate_limit(recs)}
        if a.ns_per_day:
            rep["dollars"] = dollars_per_day(rep["cadence_value"], a.ns_per_day)
        out = a.json_out or os.path.join(HERE, "vast-board-volatility.json")
        with open(out, "w") as fh:
            json.dump(rep, fh, indent=1)
        print(json.dumps({k: v for k, v in rep.items() if k != "spells"}, indent=1))
        print(f"\n-> {out}")
        return 0

    ap.print_help()
    return 2


def _count(xs):
    d = defaultdict(int)
    for x in xs:
        d[x] += 1
    return d


if __name__ == "__main__":
    raise SystemExit(main())
