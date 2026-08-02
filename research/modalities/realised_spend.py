#!/usr/bin/env python3
"""REALISED SPEND — the one home for "what have we actually paid?", DERIVED from the lanes' own ledgers.

★★ WHY THIS EXISTS (trimcrae, 2026-07-27: the scoreboard headline read **$0.74 spent** while the step 1
fan-out alone had realised twenty times that).

STRATEGY.md's scoreboard carried a hand-typed realised total. Rule 1.1 says a total is DERIVED, never typed,
and this is exactly why: the lanes bill continuously, three of them at once, and nobody re-adds a sentence.
The number was not merely stale — it was stale in the direction that matters, understating spend while the
fleet was billing. So the total moves out of prose and into arithmetic over the artifacts the lanes already
write, and STRATEGY.md points at the artifact instead of restating it.

WHAT IT IS AND IS NOT
---------------------
It is a SUMMARISER. It owns no cost, no rate and no threshold. Every dollar it prints is copied out of a
lane's own ledger, which is the only thing that measured it; if a figure here disagrees with a lane's ledger,
the ledger is right. Adding a lane means adding a row to `LANES`, not adding arithmetic.

THREE LEDGERS, AND THEY ARE NEVER ADDED TOGETHER
------------------------------------------------
  1. REALISED, MACHINE-LEDGERED  — real dollars, counted by a machine from observed billed hours. This is
     the authoritative figure and the only one that should be quoted bare.
  2. REALISED, ATTESTED-ONLY     — real dollars a lane genuinely spent that NO machine ledger counts,
     because that lane has never had one. Reported separately and never folded into (1) silently; each
     entry names where its figure was read and what would close the gap. A lane in here is a DEFECT with a
     remediation, not an accounting category to settle into.
  3. FREE CREDIT                 — GCP trial credit (expires 2026-10-10) and Modal's monthly allowance.
     CLAUDE.md §6: a separate ledger, NEVER summed into realised or ladder spend. It is reported here only
     so that "we ran that for free" stays checkable, and the code refuses to add it to anything.

And a fourth number that is not spend at all: the LADDER total (`vast-ladder-repricing.json`) is what the
plan is authorised to cost. Comparing realised against it is the point; conflating them is not. This module
does not restate the ladder total — [pricing.md](../compute/pricing.md) and the repricing JSON own it.

WHY A MIRROR IS NOT A SECOND LANE
---------------------------------
`step1-fanout-progress.json` also carries a realised figure (`realised_usd_so_far`), written at the START of
a tick, before that tick's collect reconciles the rentals. `step1-fanout-map.json` is written after. They are
the same money at two moments and adding both would double-count the whole lane. Every lane therefore
declares exactly ONE source key here, and `MIRRORS` records the copies deliberately not read, so a future
reader does not "fix" the omission.

WHY THE COMMITTED SNAPSHOT IS DELIBERATE, AND WHY IT MAY LAG
------------------------------------------------------------
The lanes bill continuously — `step1-fanout-map.json` is rewritten by every autoscale tick — so a live figure
changes several times an hour. A document cannot quote a number like that and stay true, and a CI rule
demanding it match would be red almost always, which is the linter-nobody-listens-to failure.

So there are two things, on purpose. `summary()` always reads the lanes LIVE. `--write` freezes that reading
into `realised-spend.json` with the moment it was taken. **STRATEGY.md quotes the SNAPSHOT**, and
`lint_consistency.py` holds the doc to the snapshot — a check that only fires when someone deliberately
refreshes the snapshot and forgets the doc, which is the actual failure mode rule 1 is about. `--check`
prints how far the snapshot has drifted from live, so the lag is visible rather than assumed.

Stdlib only. No network, no S3, no Vast API: it reads committed artifacts, so it runs anywhere and its answer
is reproducible from the repo alone.

Usage:
    python3 research/modalities/realised_spend.py            # human readout, live
    python3 research/modalities/realised_spend.py --json     # machine-readable
    python3 research/modalities/realised_spend.py --write    # refresh the snapshot (then update STRATEGY.md)
    python3 research/modalities/realised_spend.py --check    # how stale is the committed snapshot?
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(_HERE))
READOUT_PATH = os.path.join(_HERE, "realised-spend.json")

# --------------------------------------------------------------------------------------------------------
# LEDGERED LANES — a machine counted these from observed billed hours.
#
# `key` is a dotted path into the artifact. `provider` is who was paid. Nothing else belongs here: the
# per-rental detail stays in the lane's own ledger, which is where a dispute is settled.
# --------------------------------------------------------------------------------------------------------
LANES = [
    {
        "lane": "step1_fanout",
        "what": "LANE 17/21 — the 19-edge congeneric RBFE fan-out",
        "artifact": "research/modalities/step1-fanout-map.json",
        "key": "realised_usd",
        "provider": "vast",
        "ledger": "s3://<ckpt-bucket>/nr4a3-step1-fanout/_rentals.json, reconciled into the map by "
                  "congeneric_fanout_vast.mode_collect (bid $/hr x observed billed hours)",
    },
    {
        "lane": "vast_bench_sweep",
        "what": "LANE 18 — the $/ns throughput bench sweep that re-anchored the ladder basis",
        "artifact": "research/modalities/vast-bench-spend-ledger.json",
        "key": "cumulative_usd",
        "provider": "vast",
        "ledger": "vast_bench_sweep.realised_spend() — cumulative per cal-* instance, keyed on instance id "
                  "so a destroyed rental cannot vanish from the total",
    },
    {
        # ★★ ADDED 2026-08-02, and it had been missing for the lane's whole life. The selectivity-control
        # lane keeps a PER-RENTAL ledger keyed on instance id — exactly the shape this file calls
        # authoritative, and the shape the NR-V04 rows below are attested-only for LACKING — and it was
        # simply never registered here. So the "machine-counted floor" omitted every dollar this lane spent
        # (58 rentals) while the file's own docstring called that figure the authoritative one.
        # ⚠ THAT IS THE FAILURE MODE THIS FILE EXISTS TO PREVENT, arriving through the registry rather than
        # through a lane: a total that is honest about what it counted is still wrong if nobody added the
        # lane. `test_realised_spend_registry_covers_every_price_ledger` now fails when a
        # `*-price-ledger.json` exists that no row reads.
        "lane": "selcal",
        "what": "LANE 22 — the SMARCA2/4 endpoint-MD sensitivity control (co-folds + the 22-leg MD panel)",
        "artifact": "research/modalities/selcal-price-ledger.json",
        "key": "total_billed_usd",
        "provider": "vast",
        "ledger": "selcal_vast_launch._ledger_record — written BEFORE the DELETE for every rental, keyed on "
                  "instance id, so a destroyed host cannot vanish from the total",
    },
]

# Realised figures deliberately NOT read, and why. Reading one of these as a second lane double-counts.
MIRRORS = [
    {
        "artifact": "research/modalities/step1-fanout-progress.json",
        "key": "realised_usd_so_far",
        "why": "the same money as step1-fanout-map.json, snapshotted at the START of a tick before that "
               "tick's collect reconciles. The map is the post-collect value and is the lane's one home.",
    },
    {
        "artifact": "research/modalities/vast-bench-sweep-results.json",
        "key": "realised_usd",
        "why": "the bench sweep's results file copies its own ledger's cumulative_usd. The ledger is the "
               "source; the results file is a report of it.",
    },
]

# --------------------------------------------------------------------------------------------------------
# ATTESTED-ONLY LANES — real money, no machine ledger. THIS LIST IS A DEFECT REGISTER.
#
# ⚠ Every entry here is spend that the arithmetic above CANNOT see. The honest total is therefore a FLOOR
# plus this, and the readout says so in those words rather than quietly adding them.
#
# `usd` is the best measured figure available and `read_from` says where it was measured — it is a
# CITATION, not a fresh assertion. `closes_when` is the remediation: give the lane the same `_rentals.json`
# the fan-out has, and the entry deletes itself.
# --------------------------------------------------------------------------------------------------------
ATTESTED = [
    {
        "lane": "ternary_vast_valb_reps",
        "what": "LANE 19 — valB_mini replicate cohorts (r1+r2), 4 legs per cohort",
        "usd": 0.81,
        "provider": "vast",
        "read_from": "the destroyed cohort-2 hosts' own instance records at teardown (0.09/0.27/0.18/0.27); "
                     "STRATEGY.md Appendix A row 38. LANE 19 CLOSED at n=3 on 2026-07-30 and every host "
                     "is gone, so this figure can no longer grow — but it also cannot be completed: the "
                     "cohorts after the second were never ledgered and their instance records are "
                     "unreadable now, so 0.81 is a FLOOR on this lane, not its cost.",
        "closes_when": "ternary_vast_launch writes a per-rental ledger keyed on instance id, as "
                       "congeneric_fanout_vast._LEDGER_KEY does for the fan-out",
    },
    {
        "lane": "ternary_vast_5aks",
        "what": "RUNG 5a-KS — the two ligand-side kill-switch ternary legs, destroyed 2026-07-27 8:20 AM ET",
        "usd": 1.5,
        "provider": "vast",
        "read_from": "STRATEGY.md Appendix A row 35, which records it as the realised cost of the "
                     "relaunch-gate hole; the legs' hosts are gone and cannot be re-read",
        "closes_when": "same remediation as the row above — one ledger serves every unit of the ternary lane",
    },
    {
        "lane": "vast_bench_sweep_orphans",
        "what": "5 cal-* throughput-calibration rentals ORPHANED by the 2026-07-27 re-anchor sweep and not "
                "found until 2026-07-31 — instances 46013066 / 46014321 / 46014425 / 46014544 / 46014594, "
                "aged 5519-5537 min at reap. One (46013066) was still cur_state=running at gpu_util 0.0 "
                "for ~3.85 days; the other four were stopped but still billing storage.",
        "usd": 20.0,
        "provider": "vast",
        "read_from": "⚠ THIS FIGURE IS A LOWER BOUND WITH REAL UNCERTAINTY, AND SAYING SO IS THE POINT. It "
                     "is age x rate ASSUMING CONTINUOUS RUNNING, which was never observed — no ledger "
                     "covers these rentals. The rate is the one this sweep's own ledger records for its "
                     "A100 PCIE rentals, $0.2151/hr (vast-bench-spend-ledger.json, instances 46008409 and "
                     "46013005). A reading of the live instance record at reap gave $0.4213/hr all-in, "
                     "which is plausibly dph_total (base + storage) against that ledger's base rate and "
                     "would put the leak nearer $39. The boxes are destroyed and a destroyed instance "
                     "vanishes from the Vast API, so the true figure is NOT RECOVERABLE. Quote the range "
                     "$20-$39, never a point estimate.",
        "closes_when": "vast_bench_sweep writes its rental ledger for EVERY rental rather than stopping "
                       "mid-sweep. The mechanism that hid this: the bench ledger's last entry is instance "
                       "46013005 stamped 11:27 AM ET 2026-07-27, while the sweep went on renting ids "
                       "46013066-46014594 afterwards — so the lane's spend record died before its rentals "
                       "did. Nothing then saw them, because vast_idle_guard is LABEL-SCOPED and runs only "
                       "inside a lane's own collect: a lane that stops being dispatched stops being "
                       "guarded, and nothing anywhere says so. An account-wide sweep is the real fix.",
    },
    {
        "lane": "nrv04_retro_orphan",
        "what": "LANE 11 / RUNG 4 — instance 45749905, the ONE genuine Arm E leg's host "
                "(nrv04retro-retro_noncov_nr4a2-m1-r0), rented 6:59 PM ET Fri Jul 24 2026 and not destroyed "
                "until 6:59 AM ET Fri Jul 31 2026. 156.0 h = 6.50 days of rental against a leg that computed "
                "for 1.04 h (its own record: prod_wall_s 3730.5). Same class as the cal-* orphans above and "
                "found the same day: a lane stopped being dispatched, so nothing reaped its host.",
        "usd": 25.83,
        "provider": "vast",
        "read_from": "MEASURED, both halves, from the instance's own record at reap — but NOT a precise "
                     "figure, and saying so is the point. Span: start_date -> destroy, 561615 s, the value "
                     "the lane's own S3 ledger froze at that poll "
                     "(s3://sagemaker-us-east-2-646605541856/nrv04-retro-results/_price_ledger.json; dumped "
                     "into research/modalities/nrv04-retro-price-forensics.json). Rate: $0.16555555555555557"
                     "/hr, logged verbatim by retro-reap in run 30625438729 job 91139494243 at 10:59:45 UTC, "
                     "one second before the same pass destroyed it ('auto-stopped 45749905 — result-in-S3'). "
                     "⚠ THE UNCERTAINTY IS WHETHER THE METER RAN THE WHOLE TIME. The host's last S3 write is "
                     "11:20 AM ET Sun Jul 26 and its last observed state was `exited` after a container "
                     "start failure, so 25.83 assumes Vast billed the rented rate for the ~4.8 idle days as "
                     "well — which is the repo's own measured position (CLAUDE.md §6: only the control plane "
                     "stops the meter; a crash-looping container never returns) but was never measured for "
                     "the `exited` state specifically. If the meter stopped at the exit the figure is as low "
                     "as $6.68 (the 40.3 h to its last write). The host is destroyed and a destroyed "
                     "instance vanishes from the Vast API, so the true figure is NOT RECOVERABLE. Quote the "
                     "range $6.68-$25.83; 25.83 is the reading the lane's own ledger produces.",
        "closes_when": "nrv04_vast_launch writes a per-RENTAL ledger keyed on instance id, committed to the "
                       "repo the way step1-fanout-map.json is, instead of an S3-only per-LABEL file no "
                       "machine ledger reads. Two defects made this invisible for five days and both are "
                       "now closed in code: the ledger row carried no instance id, start_date or status, so "
                       "reconstructing it needed CI logs that expire (fixed: _update_price_ledger records "
                       "provenance); and a rental outliving any plausible leg was averaged into the per-leg "
                       "mean instead of being called a leak (fixed: ledger_entry_reading + LEAK_ABOVE_S, "
                       "pinned by tests/test_price_ledger_uptime_semantics.py). What remains is that "
                       "nothing dispatches this lane's collect on a cadence — the same 'a lane that stops "
                       "being dispatched stops being guarded' as the row above.",
    },
    {
        "lane": "nrv04_retro_smoke_fanout",
        "what": "LANE 11 / RUNG 4 — the 17 rentals of the 2026-07-31 smoke fan-out, the legs STRATEGY.md "
                "Appendix A row 57 withdraws (mode=smoke, 2 ps after zero equilibration — not panel legs). "
                "Rentals of 7-38 min at $0.18-$0.20/hr. Listed separately from nrv04_retro_orphan above "
                "because the two have different provenance and different error direction; together they are "
                "this lane's whole outlay and sum to the $26.5733 its own S3 ledger reports, which is the "
                "cross-check that says nothing is missing.",
        "usd": 0.75,
        "provider": "vast",
        "read_from": "the per-label rows of s3://sagemaker-us-east-2-646605541856/nrv04-retro-results/"
                     "_price_ledger.json read 12:07 PM ET 2026-07-31 (17 rows, $0.0124-$0.1142, summing to "
                     "$0.7460), dumped into research/modalities/nrv04-retro-price-forensics.json. ⚠ THIS IS "
                     "A FLOOR, and for the OPPOSITE reason to the row above. Those rows were frozen by the "
                     "same defect that hid the orphan, running the other way: `final` latched on the mere "
                     "existence of a leg_*.json, and every one of these units already had one, so each cost "
                     "froze at the FIRST poll after launch — minutes — while its host went on billing. The "
                     "hosts are destroyed, so the excess is not recoverable. Fixed in "
                     "nrv04_vast_launch._finalizable (a result must postdate the rental), pinned by "
                     "tests/test_price_ledger_uptime_semantics.py.",
        "closes_when": "same remediation as the row above — a per-RENTAL ledger keyed on instance id, "
                       "committed to the repo, replaces the S3-only per-LABEL file. Both entries then "
                       "delete themselves together.",
    },
]

# --------------------------------------------------------------------------------------------------------
# FREE CREDIT — a SEPARATE LEDGER (CLAUDE.md §6). Never summed into realised or ladder spend.
# --------------------------------------------------------------------------------------------------------
CREDIT_ARTIFACT = "research/compute/credit-status.json"

SEPARATE_LEDGER_NOTE = (
    "GCP trial credit and Modal's monthly allowance are a SEPARATE LEDGER and are never added to realised "
    "spend (CLAUDE.md §6). Free credit buys wall clock, not headroom: it cannot pay a Vast bill and it "
    "expires whether or not it is used."
)


def _now_utc(now=None):
    n = now or datetime.datetime.now(datetime.timezone.utc)
    return n.strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_et(now=None):
    """US Eastern, 12-hour — CLAUDE.md §1. EDT = UTC-4 for this program's whole calendar."""
    n = now or datetime.datetime.now(datetime.timezone.utc)
    et = n - datetime.timedelta(hours=4)
    return et.strftime("%-I:%M %p ET %b %-d, %Y")


def _read(path):
    with open(os.path.join(REPO, path), encoding="utf-8") as fh:
        return json.load(fh)


def _dig(doc, dotted):
    cur = doc
    for part in dotted.split("."):
        cur = cur[part]
    return cur


def ledgered(lanes=None):
    """[(row, usd_or_None, error_or_None)] for each machine-ledgered lane. PURE apart from the file reads.

    A lane whose artifact is missing or malformed yields an ERROR row rather than a zero. A total that
    silently drops an unreadable lane is the same fabricated all-clear `load_ledger_strict` exists to
    prevent — an unreadable ledger is not an empty one.
    """
    out = []
    for row in (lanes if lanes is not None else LANES):
        try:
            usd = float(_dig(_read(row["artifact"]), row["key"]))
            out.append((row, round(usd, 4), None))
        except Exception as e:  # noqa: BLE001 — every failure mode is reported, none is swallowed to 0
            out.append((row, None, f"{type(e).__name__}: {str(e)[:160]}"))
    return out


def credit(artifact=CREDIT_ARTIFACT):
    """Free-credit state, per provider. Reported beside realised spend and never added to it."""
    doc = _read(artifact)
    out = {}
    for name, p in (doc.get("providers") or {}).items():
        spent = p.get("spent", p.get("spent_this_month"))
        cap = p.get("cap")
        rec = {"label": p.get("label"), "cap_usd": cap, "spent_usd": spent,
               "spent_source": p.get("spent_source"), "expiry": p.get("expiry"),
               "resets": p.get("resets")}
        if isinstance(cap, (int, float)) and isinstance(spent, (int, float)):
            rec["remaining_usd"] = round(cap - spent, 2)
        out[name] = rec
    return out


def summary(lanes=None, attested=None, credit_artifact=CREDIT_ARTIFACT):
    """The whole picture, as three ledgers that are never added together.

    `realised_usd_ledgered` is the only figure that may be quoted bare. `realised_usd_best_estimate` exists
    because the alternative — quoting the floor as if it were the total while a lane with no ledger bills
    beside it — is the same understatement this module was written to stop; it is labelled every time it is
    printed, and it is not the headline.
    """
    rows = ledgered(lanes)
    att = list(ATTESTED if attested is None else attested)
    good = [(r, u) for r, u, e in rows if u is not None]
    errs = [(r, e) for r, u, e in rows if u is None]
    led_total = round(sum(u for _, u in good), 2)
    att_total = round(sum(float(a["usd"]) for a in att), 2)
    return {
        "_what": "Realised spend, DERIVED from each lane's own ledger. STRATEGY.md's scoreboard quotes this "
                 "SNAPSHOT and lint_consistency.py holds it to it; the figure is never typed fresh.",
        "_generated_by": "research/modalities/realised_spend.py --write",
        "_as_of_utc": _now_utc(),
        "_as_of_et": _now_et(),
        "realised_usd_ledgered": led_total,
        "realised_usd_ledgered_meaning": "real dollars, counted by a machine from observed billed hours. "
                                         "The authoritative figure, and a FLOOR on total spend while any "
                                         "lane below has no ledger.",
        "lanes": [{"lane": r["lane"], "what": r["what"], "usd": u, "provider": r["provider"],
                   "artifact": r["artifact"], "key": r["key"], "ledger": r["ledger"]}
                  for r, u in good],
        "unreadable_lanes": [{"lane": r["lane"], "artifact": r["artifact"], "error": e} for r, e in errs],
        "attested_unledgered_usd": att_total,
        "attested_unledgered_meaning": "real dollars no machine ledger counts, because these lanes have "
                                       "never had one. A DEFECT REGISTER, not an accounting category — "
                                       "each entry names the remediation that deletes it.",
        "attested_unledgered": att,
        "realised_usd_best_estimate": round(led_total + att_total, 2),
        "realised_usd_best_estimate_meaning": "ledgered + attested. Quote it only with the split; the "
                                              "attested part is a citation of a past reading, not a live "
                                              "measurement.",
        "free_credit_separate_ledger": credit(credit_artifact),
        "free_credit_note": SEPARATE_LEDGER_NOTE,
        "mirrors_deliberately_not_summed": MIRRORS,
        "ladder_total_is_elsewhere": "research/modalities/vast-ladder-repricing.json — what the plan is "
                                     "AUTHORISED to cost. A different question from what was paid; this "
                                     "module does not restate it.",
    }


def render(doc):
    """The human readout. One line per lane, then the three ledgers, kept visibly apart."""
    L = []
    L.append("REALISED SPEND — derived from the lanes' own ledgers, never typed")
    L.append("")
    L.append("  MACHINE-LEDGERED (real dollars, counted from observed billed hours)")
    for r in doc["lanes"]:
        L.append(f"    ${r['usd']:>8.2f}  {r['lane']:<22s} {r['what']}")
    for r in doc.get("unreadable_lanes") or []:
        L.append(f"    {'UNREADABLE':>9s}  {r['lane']:<22s} {r['error']}")
    L.append(f"    ${doc['realised_usd_ledgered']:>8.2f}  TOTAL — authoritative, and a FLOOR while any lane below is unledgered")
    L.append("")
    if doc["attested_unledgered"]:
        L.append("  ATTESTED ONLY — real money NO machine ledger counts. This block is a defect register.")
        for a in doc["attested_unledgered"]:
            L.append(f"    ${a['usd']:>8.2f}  {a['lane']:<22s} {a['what']}")
            L.append(f"    {'':>9s}  read from: {a['read_from']}")
            L.append(f"    {'':>9s}  closes when: {a['closes_when']}")
        L.append(f"    ${doc['attested_unledgered_usd']:>8.2f}  TOTAL attested-only")
        L.append("")
        L.append(f"  BEST ESTIMATE  ${doc['realised_usd_best_estimate']:.2f} "
                 f"(= ${doc['realised_usd_ledgered']:.2f} ledgered + "
                 f"${doc['attested_unledgered_usd']:.2f} attested)")
        L.append("")
    L.append("  FREE CREDIT — SEPARATE LEDGER, never added to the above")
    for name, c in doc["free_credit_separate_ledger"].items():
        rem = c.get("remaining_usd")
        rem_s = f"${rem:.2f} left" if isinstance(rem, (int, float)) else "remaining unknown"
        exp = c.get("expiry") or c.get("resets") or "—"
        L.append(f"    {name:<8s} {c.get('label','')}: spent ${c.get('spent_usd')}, {rem_s}, expires/resets {exp}")
    L.append(f"    {doc['free_credit_note']}")
    return "\n".join(L)


def drift(live=None, snapshot_path=READOUT_PATH):
    """How far the committed snapshot has fallen behind the lanes. Reporting only — never a failure.

    The snapshot is SUPPOSED to lag: it is what STRATEGY.md quotes, and it moves only when someone runs
    `--write`. This makes the lag a printed number instead of an assumption, so "the doc says $23.60 and
    the fleet has been billing for six hours" is a thing a reader can see rather than deduce.
    """
    live = live or summary()
    try:
        with open(snapshot_path, encoding="utf-8") as fh:
            snap = json.load(fh)
    except Exception as e:  # noqa: BLE001
        return {"snapshot_readable": False, "error": f"{type(e).__name__}: {str(e)[:160]}"}
    d = round(live["realised_usd_ledgered"] - snap.get("realised_usd_ledgered", 0.0), 2)
    return {"snapshot_readable": True,
            "snapshot_as_of_et": snap.get("_as_of_et"),
            "snapshot_ledgered_usd": snap.get("realised_usd_ledgered"),
            "live_ledgered_usd": live["realised_usd_ledgered"],
            "drift_usd": d,
            "action": ("in step" if abs(d) < 0.005 else
                       "run --write, then update the figure STRATEGY.md quotes IN THE SAME COMMIT")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="machine-readable")
    ap.add_argument("--write", action="store_true", help="refresh realised-spend.json from the live lanes")
    ap.add_argument("--check", action="store_true", help="how far has the committed snapshot drifted?")
    a = ap.parse_args(argv)
    doc = summary()
    if a.check:
        print(json.dumps(drift(doc), indent=1))
        return 0
    if a.write:
        with open(READOUT_PATH, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=1)
            fh.write("\n")
        print(f"[realised-spend] wrote {os.path.relpath(READOUT_PATH, REPO)} — now update the figure "
              f"STRATEGY.md quotes, in the same commit (CLAUDE.md rule 1.3)")
    if a.json:
        print(json.dumps(doc, indent=1))
    else:
        print(render(doc))
    return 1 if doc.get("unreadable_lanes") else 0


if __name__ == "__main__":
    sys.exit(main())
