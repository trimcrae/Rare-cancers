#!/usr/bin/env python3
"""Disable GCP ternary-watch entries whose leg has already FINISHED — instead of printing that a human should.

★ THE BUG THIS CLOSES. `ternary-leg-watchdog.yml`'s own header states the contract:

    result JSON present  -> DONE      (nothing to do; disable the entry)

Nothing disabled anything. The terminal branch of `watchdog_run.sh` printed

    "Nothing left to do: set enabled=false in ternary-watch.json."

and then looped, so a finished unit stayed `enabled: true` for as long as nobody happened to read a cron log.
Measured 2026-07-28 6:46 AM ET (GH run 30352035203): `calib_hi_to_lo__ternary_vhl` dir=rev had its result JSON
in GCS and BOTH follow-ups already dispatched, and was still enabled — it had been in that terminal state
since its result landed at 4:03 PM ET the day before, ~14 h of the watchdog re-deriving "done" every pass.

WHY IT IS NOT MERELY UNTIDY. A stale enabled entry is a lie told to two different readers:
  * `lane_staleness_watch` counts enabled units to decide whether a lane has unfinished work, so a finished
    lane reads as a stalled one — and a lane that always looks stalled is a supervision signal nobody trusts.
  * The operator-facing count ("enabled watch entries: 2") is the number an agent reports as work in flight.
    On the pass above, one of those 2 had been finished for 14 h.
It is the exact defect already fixed on the Vast side by `ternary_vast_watchdog.reap_landed`; this is that fix
for the OTHER watch list, which is a different file, a different store (GCS, not S3) and a different proof.

WHAT COUNTS AS PROOF HERE — deliberately stricter than the Vast side. `reap_landed` reaps on `status == "done"`
alone, because the Vast lane's follow-up analysis is idempotent and on-host. This lane's DONE state fans out to
two further dispatches (mode=converge, then mode=reduce on the NEXT pass), so "the result exists" is NOT the
end of the unit's work. Reaping there would disable the entry BEFORE the pass that dispatches the reducer, and
the reduce would then never happen — turning a bookkeeping fix into a lost verdict. So the caller may only
name a unit here once it has reached the TERMINAL branch: result JSON present AND both GCS markers written.
That is why this module takes the units to reap as an argument rather than re-deriving them; the shell already
holds the marker facts, and duplicating that logic in Python is how the two copies drift apart.

WHY `_disabled_why` CARRIES A POINTER TO THE VERDICT. The old instruction was "set enabled=false once you have
READ it", so disabling automatically must not become a way to lose the thing that was meant to be read. Every
entry this touches records the run URL that dispatched the reducer, so the science is one click away from the
line that silenced the unit. A reap that hides an unread result would be worse than the stale entry.

SAFE BY CONSTRUCTION: it only ever moves `enabled: true -> false`, never the reverse; it cannot dispatch,
provision or rent anything; and it rewrites the file only when something actually changed, so a steady state
produces no commit and no churn.
"""
from __future__ import annotations

import argparse
import json
import sys
import time

DEFAULT_PATH = "research/modalities/ternary-watch.json"


def unit_key(leg_id, direction, seed):
    """The identity of a watch entry. Seed is compared as a STRING because the watch file stores it as one
    ("seed": "0") while a shell variable arrives as `0` — normalising both ends here stops a reap silently
    matching nothing, which would look exactly like "there was nothing to reap"."""
    return "%s|%s|%s" % (str(leg_id), str(direction), str(seed))


def entry_key(w):
    return unit_key(w.get("leg_id"), w.get("direction"), w.get("seed"))


def reap(doc, keys, verdict_url=None, now=None):
    """Disable every ENABLED entry named in `keys`. Returns the list of keys actually disabled.

    Unknown keys are ignored rather than raising: the caller builds them from a live loop, and a unit that was
    already disabled on an earlier pass is the normal steady state, not an error.
    """
    stamp = now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    want = set(keys)
    done = []
    for w in doc.get("watch") or []:
        if not w.get("enabled"):
            continue
        k = entry_key(w)
        if k not in want:
            continue
        w["enabled"] = False
        w["_disabled_why"] = (
            "LANDED %s: the result JSON is in GCS and BOTH follow-ups (mode=converge, mode=reduce) were "
            "dispatched, which is this lane's terminal state. Auto-reaped by gcp_watch_reap — this unit is "
            "FINISHED, not parked. The verdict it produced is NOT lost: %s"
            % (stamp, verdict_url or "see the [REDUCE-VERDICT] annotation on the mode=reduce run for this leg."))
        done.append(k)
    return done


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv   # NOT `[] if argv is None` — that silently ate every flag
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--path", default=DEFAULT_PATH)
    ap.add_argument("--verdict-url", default=None,
                    help="URL of the run whose annotation carries the verdict, recorded in _disabled_why")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("units", nargs="*",
                    help="one or more leg_id|direction|seed keys, as written by watchdog_run.sh")
    a = ap.parse_args(argv)

    keys = [u.strip() for u in a.units if u.strip()]
    if not keys:
        print("[reap] nothing named — no landed unit reached the terminal state this pass.")
        return 0

    with open(a.path) as fh:
        doc = json.load(fh)
    done = reap(doc, keys, verdict_url=a.verdict_url)
    if not done:
        print("[reap] the %d named unit(s) are already disabled — steady state, nothing written." % len(keys))
        return 0
    if a.dry_run:
        print("[reap] DRY RUN — would disable: %s" % ", ".join(done))
        return 0
    with open(a.path, "w") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    for k in done:
        leg, direction, seed = k.split("|")
        print("::notice title=WATCHDOG REAPED A LANDED UNIT::%s dir=%s seed=%s — its result is in GCS and both "
              "follow-ups ran, so its watch entry is now enabled=false. The lane no longer reads as having an "
              "unfinished unit." % (leg, direction, seed))
    print("[reap] disabled %d landed entr(ies): %s" % (len(done), ", ".join(done)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
