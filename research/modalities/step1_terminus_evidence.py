#!/usr/bin/env python3
"""STEP 1 FAN-OUT — the terminus question, answered from ARTIFACTS rather than from a workflow's summary text.

WHY THIS EXISTS. The 18 held congeneric edges are released by ONE machine condition: the shakeout unit's
`ddg.json` landing in S3 (`congeneric_fanout_vast.mode_launch`, `FANOUT_REQUIRE_PROVEN_TERMINUS=1`). Every
existing readout answers that question DERIVED — `step1-fanout-map.json` says `n_complete: 0`, the launch
readout says "TERMINUS NOT PROVEN". Both are the launcher reporting on itself. CLAUDE.md §4 wants the
observation that discriminates, so this prints the raw object store: every key under the results prefix with
its size and mtime, and the commit-store iteration census that produced it.

⚠ THE TRAP THIS IS BUILT AROUND, and the reason a filename is not evidence. `ddg.json` has ONE name whatever
produced it, and the reducer's record keys on `(leg_id, seed)` — which a `RBFE_TINY=1` plumbing shakeout and a
production leg SHARE. So a smoke ddG can occupy the exact key a production ddG would, and every downstream
consumer (map, ranking, cycle closure) would read it as the real thing. The discriminator is NOT the filename,
NOT the presence of the key, and NOT `phase.txt` — it is the ITERATION COUNT in the spot commit store, which
the sampler itself writes and which cannot be forged by a short run:

    RBFE_TINY=1 (smoke)   2.5 ps equilibration / 10 ps production   -> warmup@1,   production@<=4
    production            1.0 ns equilibration / 5.0 ns production   -> warmup@400, production@2000

    (nr4a3_rbfe.py sets both lengths; the MC move interval is 625 steps x 4 fs = 2.5 ps, so
     iterations = length / 2.5 ps. Committed every RBFE_WARMUP_CKPT_ITERS=20 / RBFE_PROD_CKPT_ITERS=40.)

Two orders of magnitude separate them, so the verdict is unambiguous and is COMPUTED here, never asserted.

SECOND JOB, same $0 run: the market snapshot the release would have to clear. Terminus MET does not authorise
a launch on its own — CLAUDE.md §6 gates every multi-unit fan-out on `$/ns` against the rung's own basis, and
a hold must be VISIBLE with the snapshot that caused it. So this prints board depth (offers visible vs the
~23 baseline, min and median floor), the best achievable fleet `$/ns` from the SAME ranking the launcher rents
with (`gpu_backend.rank_offers_by_usd_per_ns`), and its multiple of `congeneric_fanout.basis_usd_per_ns()`.
It DECIDES NOTHING and RENTS NOTHING — the gate lives in `congeneric_fanout_vast.market_hold`; this is the
reader's copy of its inputs.

Run: AWS creds + (optionally) VAST_API_KEY in env.  `SKIP_MARKET=1` drops the board read.
Output: stdout + `step1-terminus-evidence.txt`, committed back by the autoscale tick.
"""
import datetime
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BUCKET = os.environ.get("VAST_CKPT_BUCKET", "sagemaker-us-east-2-646605541856")
RESULT_PREFIX = os.environ.get("RESULT_PREFIX", "nr4a3-step1-fanout/results")

# Vast's typical visible board for this ResourceSpec, the baseline the thin-market rule is stated against
# (CLAUDE.md §6: "~23 independently-priced hosts visible at once"). Reported for context only — nothing keys
# a decision off it here.
BOARD_BASELINE_OFFERS = 23

# Iterations a leg reaches, derived from nr4a3_rbfe.py's MD lengths / the 2.5 ps MC move interval. See module
# docstring. Only the smoke CEILING is load-bearing: anything above it cannot have come from RBFE_TINY.
PS_PER_ITER = 2.5
SMOKE_PROD_ITERS = int(10.0 / PS_PER_ITER)          # 10 ps  -> 4
PROD_PROD_ITERS = int(5000.0 / PS_PER_ITER)         # 5 ns   -> 2000
PROD_WARMUP_ITERS = int(1000.0 / PS_PER_ITER)       # 1 ns   -> 400
# A commit above this could not have been written by a smoke leg. Generous multiple of the smoke ceiling so a
# settings change on the smoke side cannot quietly cross it.
SMOKE_IMPOSSIBLE_ABOVE = SMOKE_PROD_ITERS * 10      # 40

ET = datetime.timezone(datetime.timedelta(hours=-4))   # EDT. CLAUDE.md §1: always US Eastern, 12-hour.
_OUT = []


def say(msg=""):
    print(msg, flush=True)
    _OUT.append(str(msg))


def et(ts):
    """A UTC datetime as US-Eastern 12-hour text. The ONLY time format this repo reports in."""
    return ts.astimezone(ET).strftime("%-I:%M %p ET %b %-d, %Y")


def _s3():
    import boto3
    return boto3.client("s3", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-2"))


def list_prefix(s3, prefix):
    out = []
    pag = s3.get_paginator("list_objects_v2")
    for page in pag.paginate(Bucket=BUCKET, Prefix=prefix):
        for o in page.get("Contents", []):
            out.append((o["Key"], o["Size"], o["LastModified"]))
    return out


def census(keys, unit_id):
    """max committed iteration per (leg, phase) for one unit, straight off the raw key list.

    Deliberately re-derived here from the listing rather than calling `congeneric_fanout_vast.
    committed_progress`: that function returns the RANKED SCALAR the monitor uses, which collapses
    (leg, phase, iter) into one number and so cannot answer "did the SOLVENT leg run production too".
    A terminus needs BOTH legs, so both are kept separate.
    """
    best = {}
    marker = f"/{unit_id}/ckpt/"
    for k, _sz, _mt in keys:
        if marker not in k or not k.endswith("COMMITTED.json"):
            continue
        rest = k.split(marker, 1)[1].split("/")
        if len(rest) < 3 or not rest[2].startswith("iter-"):
            continue
        leg, phase = rest[0], rest[1]
        try:
            it = int(rest[2].split("iter-")[1])
        except (IndexError, ValueError):
            continue
        best[(leg, phase)] = max(best.get((leg, phase), 0), it)
    return best


def verdict_for(ddg_key_present, cen):
    """PRODUCTION / SMOKE-MASQUERADE / NO-TERMINUS for one unit, computed from iteration counts only."""
    if not ddg_key_present:
        return "NO-TERMINUS", "no ddg.json key exists for this unit"
    legs = {}
    for (leg, phase), it in cen.items():
        if phase == "production":
            legs[leg] = max(legs.get(leg, 0), it)
    missing = [L for L in ("complex", "solvent") if L not in legs]
    if missing:
        return "SUSPECT", (f"ddg.json exists but no production commits for leg(s) {missing} — "
                           f"a reduce that never sampled them")
    low = {L: n for L, n in legs.items() if n <= SMOKE_IMPOSSIBLE_ABOVE}
    if low:
        return "SMOKE-MASQUERADE", (f"production commits {low} are within RBFE_TINY range "
                                    f"(smoke ceiling {SMOKE_PROD_ITERS} iters) — this ddG is NOT production")
    # Both legs are two orders of magnitude past anything RBFE_TINY can reach, so this ddG is production.
    # A count just SHORT of the 2000 target is normal rather than suspicious: production commits land every
    # RBFE_PROD_CKPT_ITERS=40 iterations, so the last commit of a leg that ran to completion is 1960 or 2000
    # depending on where the final commit fell — and a ddg.json only exists at all once BOTH leg JSONs were
    # written, which requires both legs to have finished.
    short = {L: n for L, n in legs.items() if n < PROD_PROD_ITERS}
    note = (f" (last commit short of the {PROD_PROD_ITERS} target on {short} — expected, commits land every "
            f"40 iters)") if short else ""
    return "PRODUCTION", f"both legs committed real production sampling: {legs}{note}"


def market_block(n_units):
    """Board depth + best achievable fleet $/ns + multiple of basis. Reads; never rents."""
    import congeneric_fanout as cf
    from congeneric_fanout_vast import FANOUT_RES, _vast_request
    from gpu_backend import _vast_offer_query, rank_offers_by_usd_per_ns

    key = os.environ["VAST_API_KEY"]
    offers = _vast_request("GET", "/search/asks/", key,
                           params={"q": json.dumps(_vast_offer_query(FANOUT_RES))}).get("offers", [])
    measured, capable = rank_offers_by_usd_per_ns(offers, FANOUT_RES)
    floors = sorted(p for _upn, p, _o in measured)
    take = measured[:max(1, int(n_units))]
    best = (sum(u for u, _p, _o in take) / len(take)) if take else None
    basis = cf.basis_usd_per_ns()
    return {
        "offers_returned": len(offers), "qualifying": len(capable), "priceable": len(measured),
        "baseline_offers": BOARD_BASELINE_OFFERS,
        "needed": int(n_units), "used_for_mean": len(take),
        "min_floor_usd_h": round(floors[0], 4) if floors else None,
        "median_floor_usd_h": round(statistics.median(floors), 4) if floors else None,
        "best_fleet_usd_per_ns": round(best, 6) if best is not None else None,
        "basis_usd_per_ns": round(basis, 6),
        "ratio_vs_basis": round(best / basis, 2) if best else None,
        "projected_usd": cf.projected_tranche_usd(best, n_units),
        "ceiling_usd": cf.market_ceiling_usd(n_units),
        "rows": [{"gpu": o.get("gpu_name"), "machine_id": o.get("machine_id"),
                  "min_bid_usd_h": round(p, 4), "usd_per_ns": round(u, 6),
                  "multiple_of_basis": round(u / basis, 2)} for u, p, o in take[:12]],
    }


def main():
    import congeneric_fanout as cf
    # plan()["units"] is the unit_id LIST (strings) — the same order the launcher submits in.
    unit_ids = list(cf.plan()["units"])

    say(f"[s1f-terminus] bucket s3://{BUCKET}  prefix {RESULT_PREFIX}")
    say(f"[s1f-terminus] read at {et(datetime.datetime.now(datetime.timezone.utc))}")
    say("")

    s3 = _s3()
    keys = list_prefix(s3, RESULT_PREFIX + "/")
    say(f"[s1f-terminus] {len(keys)} object(s) under the results prefix")

    # --- 1. every ddg.json that exists, raw ---------------------------------------------------------------
    ddgs = [(k, sz, mt) for k, sz, mt in keys if k.endswith("/ddg.json")]
    say("")
    say("=== RAW ARTIFACT EVIDENCE — every ddg.json key in the object store ===")
    if not ddgs:
        say("  (none) — no unit has written a ddg.json, so reduce -> commit -> upload has never been observed "
            "on this lane.")
    for k, sz, mt in sorted(ddgs):
        say(f"  {sz:8d} B  {et(mt)}  s3://{BUCKET}/{k}")

    # --- 2. per-unit terminus census ---------------------------------------------------------------------
    say("")
    say("=== PER-UNIT CENSUS — furthest committed iteration per (leg, phase), from the spot commit store ===")
    say(f"    smoke ceiling = production@{SMOKE_PROD_ITERS}; production target = "
        f"warmup@{PROD_WARMUP_ITERS} + production@{PROD_PROD_ITERS} per leg")
    any_production = False
    verdicts = {}
    for uid in unit_ids:
        cen = census(keys, uid)
        has_ddg = any(k == f"{RESULT_PREFIX}/{uid}/ddg.json" for k, _s, _m in keys)
        v, why = verdict_for(has_ddg, cen)
        verdicts[uid] = {"verdict": v, "why": why, "census": {f"{a}/{b}": c for (a, b), c in sorted(cen.items())},
                         "has_ddg": has_ddg}
        if v == "PRODUCTION":
            any_production = True
        detail = ", ".join(f"{a}/{b}@{c}" for (a, b), c in sorted(cen.items())) or "no commits"
        say(f"  {uid[:58]:58s} ddg={'YES' if has_ddg else 'no ':3s} {v:18s} {detail}")

    # --- 3. the terminus answer --------------------------------------------------------------------------
    say("")
    say("=== TERMINUS ===")
    if any_production:
        say("  ✅ MET — at least one unit has a ddg.json whose BOTH legs committed real production sampling.")
        for uid, d in verdicts.items():
            if d["verdict"] == "PRODUCTION":
                say(f"     {uid}: {d['why']}")
                body = s3.get_object(Bucket=BUCKET, Key=f"{RESULT_PREFIX}/{uid}/ddg.json")["Body"].read()
                say("     ddg.json:")
                for line in json.dumps(json.loads(body), indent=2).splitlines():
                    say("       " + line)
    else:
        bad = {u: d for u, d in verdicts.items() if d["verdict"] in ("SMOKE-MASQUERADE", "SUSPECT")}
        if bad:
            say("  ⛔ NOT MET — a ddg.json exists but does NOT pass the iteration-count check:")
            for u, d in bad.items():
                say(f"     {u}: {d['verdict']} — {d['why']}")
        else:
            say("  ⛔ NOT MET — no ddg.json anywhere under the results prefix. The 18 edges stay held; "
                "the shakeout unit is the only thing that may be rented.")

    # --- 4. the market the release would have to clear ---------------------------------------------------
    say("")
    say("=== MARKET SNAPSHOT — what the 18-edge release would cost RIGHT NOW (read-only; rents nothing) ===")
    if os.environ.get("SKIP_MARKET") == "1" or not os.environ.get("VAST_API_KEY"):
        say("  skipped (SKIP_MARKET=1 or no VAST_API_KEY)")
    else:
        # Priced on the REMAINING TRANCHE, exactly as `market_hold` does — the authorisation is a
        # tranche-level dollar band, so a per-batch price would wave nineteen expensive units through one
        # at a time.
        n_release = max(1, len([u for u in unit_ids if not verdicts[u]["has_ddg"]]))
        # The buy line and its derived multiple come from the module that OWNS them, so this readout and the
        # launcher's refusal can never drift apart (tests/test_buy_line_invariant.py pins that).
        import inflight_usd_per_ns as inf
        try:
            m = market_block(n_release)
            say(f"  board depth      : {m['offers_returned']} offers visible "
                f"(baseline ~{m['baseline_offers']}), {m['qualifying']} qualifying, "
                f"{m['priceable']} priceable, {m['needed']} needed")
            say(f"  floors           : min ${m['min_floor_usd_h']}/hr, median ${m['median_floor_usd_h']}/hr")
            say(f"  best fleet $/ns  : ${m['best_fleet_usd_per_ns']}/ns  ·  "
                f"{m['ratio_vs_basis']}× basis (basis ${m['basis_usd_per_ns']}/ns)")
            say(f"  projected        : ${m['projected_usd']} against a ${m['ceiling_usd']} ceiling")
            # ★★ THE LINE IS THE ABSOLUTE RATE, NOT A HARDCODED 1.5× (CLAUDE.md §1, re-expression ruling).
            # This block used to test `ratio_vs_basis >= 1.5`. After the 2026-07-27 throughput re-anchor the
            # basis fell 22 % ($0.004359 -> $0.003412/ns) while NO PRICE MOVED, so a bare 1.5 became a much
            # STRICTER rule than the one agreed: at 1:41 PM ET this printed "⚠ DRIFT ... would be HELD on
            # price" for a board at 1.73× basis = $0.005908/ns — comfortably UNDER the $0.006539/ns buy line
            # the launcher actually enforces. A readout that reports a refusal the gate would not make is the
            # same defect class as one that hides a refusal it would. Both must be the same number, so the
            # threshold is imported and the multiple is DERIVED, never typed.
            _best, _line = m["best_fleet_usd_per_ns"], inf.APPROVED_USD_PER_NS
            if _best is not None and _best >= _line:
                say(f"  ⚠ DRIFT — ${_best}/ns is at or above the ${_line:.6f}/ns buy line "
                    f"(≈{inf.drift_multiple():.2f}× basis). A release into this board would be HELD on price.")
            elif _best is not None:
                say(f"  OK — under the ${_line:.6f}/ns buy line (≈{inf.drift_multiple():.2f}× basis); "
                    f"a release would clear the price gate.")
            for r in m["rows"]:
                say(f"    {str(r['gpu']):10s} m{r['machine_id']:<8} ${r['min_bid_usd_h']:.4f}/hr  "
                    f"${r['usd_per_ns']:.5f}/ns · {r['multiple_of_basis']:.2f}× basis")
        except Exception as e:  # noqa: BLE001
            say(f"  board UNREADABLE: {type(e).__name__}: {e} — an unreadable board is not a cheap board; "
                f"a release would be refused for lack of evidence (same discipline as market_hold).")

    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "step1-terminus-evidence.txt"), "w") as f:
            f.write("\n".join(_OUT) + "\n")
    except Exception as e:  # noqa: BLE001
        print(f"[s1f-terminus] could not write the evidence file: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
