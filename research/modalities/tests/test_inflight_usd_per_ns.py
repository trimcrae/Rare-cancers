#!/usr/bin/env python3
"""The IN FLIGHT board's `$/ns` cell must DEFER to the cost model, not re-implement it.

This is a reporting path, which is exactly the kind that gets trusted without being checked. The invariants
worth pinning are not the arithmetic — `vast_cost_model` already owns that — but that this module stays a
reporter: no second throughput table, no fabricated figure for a card nobody benched, and a drift flag that
actually fires at the threshold the rule names.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, HERE)

from _skip_guard import skip_module    # noqa: E402

try:
    import vast_cost_model as vcm          # noqa: E402
    import inflight_usd_per_ns as R        # noqa: E402
except ImportError as e:                   # pragma: no cover - env probe
    skip_module(f"needs vast_cost_model: {e}")

fails = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


print("== it is a REPORTER: no second throughput table, no second cost function")
src = open(os.path.join(HERE, "..", "inflight_usd_per_ns.py")).read()
check("755.36" not in src and "MEASURED_NS_PER_DAY_84K = " not in src,
      "no card throughput number is hard-coded here — vast_cost_model is 'THE ONLY THROUGHPUT TABLE'")
check("vcm.ns_per_hour" in src and "vcm.usd_per_ns" in src,
      "throughput and cost both come from the cost model's own functions")
check("vcm.REFERENCE_NS_PER_H" in src,
      "the basis divides by the cost model's reference, not by a copy of it")

print("== the basis is the ladder rate over the reference card")
plan = 0.137
check(abs(R.basis_usd_per_ns(plan) - plan / vcm.REFERENCE_NS_PER_H) < 1e-12,
      "basis = $/ref-GPU-h ÷ REFERENCE_NS_PER_H, exactly")

print("== a card the cost model cannot price is UNKNOWN, never a number")
r = R.row("RTX 9999", 0.10, plan)
check(r["usd_per_ns"] is None and r["multiple"] is None,
      "an unbenched card yields no figure — the same choice usd_per_ns makes")
check("UNKNOWN" in r["cell"] and "cannot be graded" in r["cell"],
      "...and the cell says so rather than rendering a blank that reads as fine")

print("== the drift flag fires at the threshold the rule names, and not below it")
check(R.DRIFT_MULTIPLE == 1.5, "threshold is the 1.5x the CLAUDE.md rule states")
basis = R.basis_usd_per_ns(plan)
nsh = vcm.ns_per_hour("RTX 4090")
# Construct rates that land either side of the threshold, from the basis itself rather than by guessing.
just_under = R.row("RTX 4090", basis * 1.40 * nsh, plan)
just_over = R.row("RTX 4090", basis * 1.60 * nsh, plan)
check(not just_under["drifting"] and "DRIFT" not in just_under["cell"], "1.40x basis is not flagged")
check(just_over["drifting"] and "DRIFT" in just_over["cell"], "1.60x basis IS flagged")

print("== the multiple is present on every priced row — it is the gradeable part")
for card, dph in (("RTX 4090", 0.1391), ("RTX 4080S", 0.1307), ("RTX 3090", 0.0643)):
    c = R.row(card, dph, plan)
    check("basis" in c["cell"] and c["multiple"] is not None,
          f"{card} row carries a multiple, not just a $/ns nobody can grade")

print("== the real drift from 2026-07-26 reproduces")
# The observation that prompted the rule: three hosts at ~1x and the fan-out shakeout well above it.
hi = R.row("RTX 4080S", 0.2247, plan)
lo = R.row("RTX 3090", 0.0643, plan)
check(hi["drifting"] and not lo["drifting"],
      "the $0.2247 4080S flags while the $0.0643 3090 does not — the case $/hr alone could not distinguish")
check(hi["multiple"] > lo["multiple"] * 1.5,
      "and the gap is large, which is why $/hr made them look like an ordinary spread")

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print("all in-flight $/ns reporting tests passed")
