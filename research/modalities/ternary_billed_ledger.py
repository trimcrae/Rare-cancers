#!/usr/bin/env python3
"""WHAT EACH TERNARY RENTAL ACTUALLY COST — per instance, in the fan-out's field names.

★★ WHY THIS EXISTS. `billed_h` appeared in exactly ONE committed artifact repo-wide
(`step1-fanout-map.json`), so answering "how long do this lane's hosts live, and what did they cost?"
required reconstructing it from the GIT HISTORY of `ternary-vast-rental-receipt.json` — a file that is
OVERWRITTEN by every launch and therefore holds one tick, not a record. That reconstruction was done by hand
twice; the second time it was needed to establish that a rental which produced nothing had in fact billed.

⚠ AND THE HOLE IS NOT HYPOTHETICAL ON THIS LANE. The 5a-KS prune smoke rented instance 46459452 at
10:02 PM ET on 2026-07-31, produced ZERO host-side artifacts — `run.log`, the `attempts/` archive,
`status.json` and `leg.json` all still carried their 2026-07-26 contents the next morning — and the instance
was gone. Nothing anywhere recorded that money had been spent, because the only per-rental artifact this
lane had is overwritten on the next launch. A rental that bills and leaves no trace is the orphan shape.

★ THE FIELD NAMES AND SEMANTICS ARE THE FAN-OUT'S, DELIBERATELY (`congeneric_fanout_vast.ledger_cost`):
`instance`, `unit_id`, `machine_id`, `rate_usd_h`, `billed_h`, `usd`. One analysis then works across lanes,
which is the whole point of matching rather than inventing a fourth schema.

⚠ AND `billed_h` IS RENTAL TIME, NOT LEG TIME — the distinction
[`tests/test_price_ledger_uptime_semantics.py`](./tests/test_price_ledger_uptime_semantics.py) exists to
pin. A retrospective row read 156.0 h for a leg whose own record says 1.04 h of production MD; the field was
not broken, it was measuring the HOST's billed life. The dollars were real. This module inherits that
reading rather than re-deciding it, and the arithmetic is imported from `nrv04_vast_launch.leg_cost_usd`
rather than retyped (CLAUDE.md §1).

WHERE ROWS COME FROM — both, because the second is where a wedged host's cost lands:
  * TEARDOWN — the normal path, when a leg finishes and its host is retired.
  * THE IDLE GUARD'S DESTROY — the path a box takes when it is up and producing no evidence of work. That
    is exactly the smoke's shape above, and recording only the happy path would leave the expensive case
    unrecorded for the same reason it is expensive.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "ternary-billed-hours.json"

# Keep the file bounded, newest last. The cap is generous because a row is ~120 bytes and the history is the
# product; the launch ledger's cap once deleted the OLDEST row on every write, so this trims in ONE place
# and only when over.
MAX_ROWS = 4000


def _rate_of(inst):
    """$/hr the INSTANCE is billed at. `dph_total` first — it includes storage and the bid, which is what
    Vast actually charges — falling back to the bid alone only when the total is absent.

    ⚠ NEVER a launcher `dph≈` line: that is the market floor plus the search's disk line and reads LOW
    against the rate the instance is really billed (`vast_rate_forensics.py`)."""
    if not isinstance(inst, dict):
        return None
    for k in ("dph_total", "dph_base", "bid", "min_bid"):
        v = inst.get(k)
        try:
            if v is not None and float(v) > 0:
                return float(v)
        except (TypeError, ValueError):
            continue
    return None


def billed_hours(inst, now_epoch=None):
    """Hours this instance has been alive, from ITS OWN `start_date`. None when it cannot be read.

    None, not 0: a rental whose age is unknown is a hole in the total, and a total that hides holes is
    worse than one that admits them (the fan-out's rule, kept)."""
    if not isinstance(inst, dict):
        return None
    start = inst.get("start_date")
    try:
        start = float(start)
    except (TypeError, ValueError):
        return None
    if start <= 0:
        return None
    now = time.time() if now_epoch is None else now_epoch
    h = (now - start) / 3600.0
    return round(h, 4) if h >= 0 else None


def row_for(inst, unit_id=None, reason="teardown", now_epoch=None):
    """One ledger row, in the fan-out's field names. PURE given `inst` and `now_epoch`."""
    rate = _rate_of(inst)
    h = billed_hours(inst, now_epoch=now_epoch)
    usd = round(rate * h, 4) if (rate is not None and h is not None) else None
    return {
        "instance": str((inst or {}).get("id") or (inst or {}).get("instance") or ""),
        "unit_id": unit_id or (inst or {}).get("label") or None,
        "machine_id": (inst or {}).get("machine_id"),
        "rate_usd_h": rate,
        "billed_h": None if h is None else round(h, 2),
        "usd": usd,
        # beyond the shared schema, and only things a later reader cannot recover once the box is gone:
        "gpu": (inst or {}).get("gpu_name"),
        "reason": reason,
        "actual_status": (inst or {}).get("actual_status"),
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now_epoch or time.time())),
        "unpriced": rate is None or h is None,
    }


def load(path=None):
    p = Path(path or LEDGER)
    if not p.is_file():
        return {"_what": __doc__.split("\n")[0], "schema": 1, "rentals": []}
    try:
        d = json.loads(p.read_text())
        d.setdefault("rentals", [])
        return d
    except Exception:  # noqa: BLE001 — a corrupt ledger must not stop a teardown recording the next row
        return {"_what": __doc__.split("\n")[0], "schema": 1, "rentals": [], "_recovered_from_corrupt": True}


def record(inst, unit_id=None, reason="teardown", path=None, now_epoch=None):
    """Append one rental to the ledger, idempotently on (instance, reason). Returns the row.

    IDEMPOTENT ON PURPOSE: teardown and the idle guard can both fire for one box, and two rows for one
    rental would double-count the money. Keyed on reason as well as instance so a box destroyed by the guard
    AFTER a teardown attempt is still distinguishable from a clean retirement.
    """
    doc = load(path)
    r = row_for(inst, unit_id=unit_id, reason=reason, now_epoch=now_epoch)
    key = (r["instance"], r["reason"])
    for i, old in enumerate(doc["rentals"]):
        if (old.get("instance"), old.get("reason")) == key:
            # keep the LONGER billed time: a later observation of the same rental saw more of its life.
            if (old.get("billed_h") or 0) >= (r["billed_h"] or 0):
                return old
            doc["rentals"][i] = r
            break
    else:
        doc["rentals"].append(r)
    if len(doc["rentals"]) > MAX_ROWS:
        doc["rentals"] = doc["rentals"][-MAX_ROWS:]
    doc["updated_utc"] = r["utc"]
    p = Path(path or LEDGER)
    p.write_text(json.dumps(doc, indent=1, sort_keys=False))
    return r


def totals(doc):
    """(total_usd, n_rentals, n_unpriced, total_billed_h). PURE.

    Unpriced rentals contribute 0 and are COUNTED — the fan-out's rule, because a total that hides holes is
    worse than one that admits them."""
    total, hours, unpriced = 0.0, 0.0, 0
    for r in (doc or {}).get("rentals") or []:
        if r.get("unpriced") or r.get("usd") is None:
            unpriced += 1
            continue
        total += float(r["usd"])
        hours += float(r.get("billed_h") or 0)
    return round(total, 2), len(((doc or {}).get("rentals") or [])), unpriced, round(hours, 2)


def render(doc):
    t, n, unpriced, hours = totals(doc)
    L = ["TERNARY BILLED-HOURS LEDGER — %d rental(s), %.2f h, $%.2f%s"
         % (n, hours, t, ("  ⚠ %d UNPRICED (not in the total)" % unpriced) if unpriced else "")]
    for r in (doc.get("rentals") or [])[-25:]:
        L.append("  %-10s %-46s %-9s $%-8s %-6sh $%-7s %s"
                 % (r.get("instance"), str(r.get("unit_id"))[:46], r.get("gpu"), r.get("rate_usd_h"),
                    r.get("billed_h"), r.get("usd"), r.get("reason")))
    return "\n".join(L)


def _main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--print", action="store_true")
    ap.add_argument("--path", default=None)
    a = ap.parse_args(argv)
    print(render(load(a.path)))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
