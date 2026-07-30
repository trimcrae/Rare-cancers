#!/usr/bin/env python3
"""Resolve the bid multiple a gate tick should carry, so an AUTHORISED retention bid can actually be aimed.

★ THE PROBLEM THIS SOLVES, MEASURED RATHER THAN ASSUMED (2026-07-30). `gpu-ternary-fep-vast.yml` exposes
`bid_floor_mult` to buy host retention on a leg that is churning -- trimcrae authorised exactly that for the
last ternary legs. But it is a `workflow_dispatch` input, and a SCHEDULED gate tick always passes it blank.
The tick re-places a dead host within minutes, so a hand dispatch only lands if it hits the gap between a host
dying and the next tick. It does not: T3 ternary was re-placed by an auto tick at 10:35 AM four minutes ahead
of a hand dispatch carrying the override, and three more times at 12:27/12:32/12:35 PM. The lever worked and
was simply unreachable.

★ WHY IT MATTERED HERE RATHER THAN BEING A TIDINESS COMPLAINT. T3's host lifetimes that day were 110, 12, 5
and 3 minutes against a ~25-minute cold start, so the last three placements DIED BEFORE FINISHING THEIR COLD
START -- each billed and produced no MD. Against ~43 minutes of remaining work, re-placing at the market floor
is not slow progress, it is NEGATIVE progress.

⛔ WHAT THIS DELIBERATELY IS NOT. It is not a lane-wide bid raise, and it must never become one -- the lever's
author set "PER-LAUNCH, NEVER STANDING" for a good reason: a higher bid on a leg whose hosts already hold buys
nothing and costs money. So an entry names ONE leg by substring, an explicit dispatch input always WINS over
the file, and an empty or disabled list resolves to "" -- byte-identical behaviour to today for every leg not
named. It also cannot cause a rental: it only supplies a multiple to a launch the gate has already cleared,
and both existing guards (Vast's min(bid, on-demand) charge, and the market gate's own $/ns ceiling) are
untouched.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "retention-bid.json")

# WHICH gate snapshot to read `units_needing_host` from. Overridable because each lane keeps its own: the
# closure triangle writes valb-triangle-market-hold.json, the valB_mini/5a-KS lane writes
# ternary-vast-market-hold.json. Env rather than a guess, so wiring a second lane is one line in the workflow
# and never a silent read of the WRONG lane's pending set -- which would aim a retention bid at a leg that is
# not the one churning.
GATE = os.environ.get("RETENTION_GATE_JSON") or os.path.join(HERE, "valb-triangle-market-hold.json")


def load_config(path=None):
    try:
        with open(path or CONFIG) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"retention": []}


def units_needing_host(path=None):
    """The units the gate says still need a host. Read from the gate's OWN committed snapshot rather than
    recomputed, so this can never disagree with the launch it is about to modify."""
    try:
        with open(path or GATE) as fh:
            return list(json.load(fh).get("units_needing_host") or [])
    except (OSError, ValueError):
        return []


def resolve(explicit=None, config_path=None, gate_path=None):
    """The multiple to pass as `bid_floor_mult`, as a string ("" = leave the lane's default policy alone).

    PRECEDENCE, and the order is deliberate:
      1. An EXPLICIT dispatch input always wins. A human aiming the lever by hand must never be silently
         overridden by a file, including by an entry someone forgot to retire.
      2. Otherwise, the first ENABLED entry whose `leg_substring` matches a unit that actually needs a host.
         Matching against units_needing_host (not against every unit) is what keeps a retention bid from
         being applied to a leg that is running happily -- the exact waste the per-launch rule guards against.
      3. Otherwise "" -- unchanged behaviour.
    """
    if explicit not in (None, "", "null"):
        return str(explicit)

    needing = units_needing_host(gate_path)
    if not needing:
        return ""

    for e in load_config(config_path).get("retention") or []:
        if not e.get("enabled"):
            continue
        sub = e.get("leg_substring") or ""
        if sub and any(sub in u for u in needing):
            return str(e.get("mult") or "")
    return ""


def explain(explicit=None, config_path=None, gate_path=None):
    """Human-readable, for the workflow annotation. A retention bid that is applied SILENTLY is the same
    reporting defect this repo already fixed once on the $/ns board: money moving with no line saying why."""
    val = resolve(explicit, config_path, gate_path)
    needing = units_needing_host(gate_path)
    if explicit not in (None, "", "null"):
        return val, "explicit dispatch input %s -- the file was not consulted" % val
    if not val:
        return "", ("no retention bid: %s" %
                    ("no unit needs a host" if not needing else
                     "no enabled entry matches %s" % needing))
    for e in load_config(config_path).get("retention") or []:
        if e.get("enabled") and (e.get("leg_substring") or "") and \
                any(e["leg_substring"] in u for u in needing):
            return val, ("retention bid %sx for %s (matched %s) -- authorised: %s"
                         % (val, e["leg_substring"], needing, e.get("_authorised_by", "UNRECORDED")))
    return val, "retention bid %s" % val


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # positional = the explicit dispatch input; flags must NEVER be mistaken for one, or `--explain` alone
    # would read as an explicit bid of "--explain" and suppress the file it was asked to explain.
    positional = [a for a in argv if not a.startswith("-")]
    explicit = positional[0] if positional else os.environ.get("BID_FLOOR_MULT_INPUT", "")
    val, why = explain(explicit)
    if "--explain" in argv:
        print(why)
    else:
        print(val)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
