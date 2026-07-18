#!/usr/bin/env python3
"""Free-credit tracker: render a burn board for GCP + Modal from credit-status.json.

No provider exposes "free credit remaining" as an API, so this tracks
remaining = cap - spent, plus a countdown to each window's expiry. `spent` is
written by the credit-status CI job (Modal via `modal billing report`, GCP via
the BigQuery billing export if enabled) or set manually with the flags below.

Times are printed in US Eastern (ET), 12-hour AM/PM, per repo convention.
Stdlib only (matches the repo's CI-script convention).

Usage:
  python credit_status.py                         # print the board
  python credit_status.py --set-gcp-spent 12.40   # update GCP spend + stamp time
  python credit_status.py --set-modal-spent 3.10  # update this-month Modal spend
  python credit_status.py --set-gcp-expiry 2026-10-10 --set-gcp-start 2026-07-12
"""
import argparse
import datetime as dt
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "credit-status.json")
ET = dt.timezone(dt.timedelta(hours=-4), "EDT")  # US Eastern (EDT); repo is EDT-dated


def _load():
    with open(STATE) as f:
        return json.load(f)


def _save(d):
    with open(STATE, "w") as f:
        json.dump(d, f, indent=2)
        f.write("\n")


def _now_et():
    return dt.datetime.now(ET)


def _fmt_et(iso_utc):
    if not iso_utc:
        return "never"
    try:
        t = dt.datetime.fromisoformat(iso_utc.replace("Z", "+00:00")).astimezone(ET)
        return t.strftime("%b %-d, %-I:%M %p ET")
    except Exception:
        return iso_utc


def _days_left(expiry):
    try:
        exp = dt.date.fromisoformat(expiry)
    except Exception:
        return None
    return (exp - _now_et().date()).days


def _money(x):
    return "unknown" if x is None else f"${x:,.2f}"


def _bar(frac, width=20):
    if frac is None:
        return "?" * width
    frac = max(0.0, min(1.0, frac))
    n = int(round(frac * width))
    return "#" * n + "-" * (width - n)


def board(d):
    lines = []
    lines.append("=== FREE-CREDIT BURN BOARD ===")
    lines.append(f"as of {_now_et().strftime('%b %-d, %-I:%M %p ET')}  "
                 f"(last sync: {_fmt_et(d.get('updated_utc'))})")
    lines.append("")

    g = d["providers"]["gcp"]
    spent = g.get("spent")
    remain = None if spent is None else round(g["cap"] - spent, 2)
    frac = None if spent is None else remain / g["cap"]
    dl = _days_left(g.get("expiry"))
    lines.append(f"GCP free trial   cap {_money(g['cap'])}")
    lines.append(f"  credit  [{_bar(frac)}] {_money(remain)} left"
                 + ("" if spent is None else f"  (spent {_money(spent)})"))
    lines.append(f"  time    expiry {g.get('expiry')}"
                 + (f"  -> {dl} days left" if dl is not None else "  -> CONFIRM from console"))
    if spent is not None and dl and dl > 0 and remain is not None:
        lines.append(f"  budget  ${remain / dl:,.2f}/day to spend it all before expiry")
    lines.append("")

    m = d["providers"]["modal"]
    mspent = m.get("spent_this_month")
    mremain = None if mspent is None else round(m["cap"] - mspent, 2)
    mfrac = None if mspent is None else mremain / m["cap"]
    lines.append(f"Modal monthly    cap {_money(m['cap'])}/mo  (resets monthly - does NOT roll over)")
    lines.append(f"  credit  [{_bar(mfrac)}] {_money(mremain)} left this month"
                 + ("" if mspent is None else f"  (spent {_money(mspent)} in {m.get('month')})"))
    # days to month end
    today = _now_et().date()
    if today.month == 12:
        nextm = dt.date(today.year + 1, 1, 1)
    else:
        nextm = dt.date(today.year, today.month + 1, 1)
    lines.append(f"  time    {(nextm - today).days} days until monthly reset (unused $ is forfeited)")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set-gcp-spent", type=float)
    ap.add_argument("--set-modal-spent", type=float)
    ap.add_argument("--set-gcp-expiry")
    ap.add_argument("--set-gcp-start")
    ap.add_argument("--set-modal-month")
    args = ap.parse_args()

    d = _load()
    changed = False
    if args.set_gcp_spent is not None:
        d["providers"]["gcp"]["spent"] = args.set_gcp_spent
        changed = True
    if args.set_modal_spent is not None:
        d["providers"]["modal"]["spent_this_month"] = args.set_modal_spent
        changed = True
    if args.set_gcp_expiry:
        d["providers"]["gcp"]["expiry"] = args.set_gcp_expiry
        changed = True
    if args.set_gcp_start:
        d["providers"]["gcp"]["window_start"] = args.set_gcp_start
        changed = True
    if args.set_modal_month:
        d["providers"]["modal"]["month"] = args.set_modal_month
        changed = True
    if changed:
        d["updated_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        _save(d)

    print(board(d))


if __name__ == "__main__":
    main()
