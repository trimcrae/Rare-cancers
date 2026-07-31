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
# ⚠ THE THRESHOLD IS AN ABSOLUTE RATE, NOT A MULTIPLE (trimcrae, 2026-07-27). It was `R.DRIFT_MULTIPLE == 1.5`
# here. When the throughput table was re-anchored the basis fell 22% WITHOUT ANY PRICE MOVING, so a typed
# multiple silently became a stricter rule than the one approved. The invariant is the approved $/ns; the
# multiple is derived from it and now reads ~1.92x — the SAME dollars. See tests/test_buy_line_invariant.py.
import congeneric_fanout as _cf   # noqa: E402  the ladder basis the multiple is expressed against
check(R.APPROVED_USD_PER_NS == 1.5 * (0.1372 / 31.473333333333333),
      "the approved absolute rate is exactly what 1.5x the basis-of-record meant at the time of the ruling")
check(abs(R.drift_multiple() * _cf.basis_usd_per_ns() - R.APPROVED_USD_PER_NS) < 1e-12,
      "and the derived multiple reproduces that same absolute rate against the LADDER basis")
basis = R.basis_usd_per_ns(plan)
nsh = vcm.ns_per_hour("RTX 4090")
# Either side of the threshold, derived FROM THE APPROVED ABSOLUTE RATE, which is what the flag tests.
just_under = R.row("RTX 4090", R.APPROVED_USD_PER_NS * 0.93 * nsh, plan)
just_over = R.row("RTX 4090", R.APPROVED_USD_PER_NS * 1.07 * nsh, plan)
check(not just_under["drifting"] and "⚠" not in just_under["cell"], "just under the line is not flagged")
# The marker's WORDING changed on 2026-07-27 (bare `⚠ DRIFT` -> `⚠ PAYING OVER THE ...× LINE`) so that a row
# we are being charged cannot render identically to one the gate refused.
check(just_over["drifting"] and "⚠" in just_over["cell"] and "OVER" in just_over["cell"],
      "just over the line IS flagged, and the flag says money is going out over the line")
# ⚠ THIS CHECKED FOR THE WORDS "approved rate" AND THAT WAS TESTING THE LABEL, NOT THE FACT (2026-07-31).
# The cell's job is to state the ABSOLUTE rate so the multiple cannot be misread as a loosening of the rule;
# the English around it is presentation. When the flag was shortened — it had been repeating the whole
# §1 re-expression ruling on every drifting row, which is a rule-1 duplication and made the board 250
# characters wide — the number stayed and the label went, and this check failed on a change that preserved
# everything it was protecting. It now asserts the RATE is present.
check(f"{R.APPROVED_USD_PER_NS:.6f}" in just_over["cell"],
      "...and it states the ABSOLUTE approved rate, so the multiple cannot be misread as a loosening")

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

print("== ★ PAYING AND REFUSING MUST NOT RENDER THE SAME (trimcrae, 2026-07-27)")
# The defect, exactly as it appeared: on that morning's board the fan-out at 3.25x and valB at 1.96x were
# HELD ($0 out) while the 5a-KS leg at 1.51x and the shakeout at 1.82x were money leaving the account. All
# four printed `⚠ DRIFT`. The question "are we not stopping those runs?" was the correct reading of a board
# that could not tell the two apart.
paying = R.row("RTX 4090", 0.2497, plan, stance=R.PAYING)          # the shakeout host, 1.82x
refused = R.row("RTX 4090", 0.4459, plan, stance=R.REFUSED)        # the 19-edge fan-out, 3.25x
check(paying["usd_per_ns"] > R.APPROVED_USD_PER_NS and refused["usd_per_ns"] > R.APPROVED_USD_PER_NS,
      "both rows are over the drift line — which is why the OLD format made them identical")
check(paying["cell"] != refused["cell"], "the two cells are not the same string")
check("⚠" in paying["cell"] and "⚠" not in refused["cell"],
      "⚠ appears on the PAYING row only — it means money is going out")
check("⛔" in refused["cell"] and "⛔" not in paying["cell"],
      "⛔ appears on the REFUSED row only — it means money is NOT going out")
check("$0 spent" in refused["cell"],
      "the refused row states $0 on its own line, so the multiple cannot be read as a bill")
check("REFUSED" in refused["cell"] and "PAYING OVER" in paying["cell"],
      "each row names its own stance in words, not only in a glyph")
check(paying["paying_over_line"] and not refused["paying_over_line"],
      "`paying_over_line` is true only when we are actually being charged over the line")
check(refused["refused"] and not paying["refused"], "`refused` is the machine-readable half of the same fact")
check(paying["drifting"] and refused["drifting"],
      "`drifting` still means only 'this rate is over the line', so existing callers are unaffected")

print("== a row held for a reason that is NOT price says so")
held_cheap = R.row("RTX 4090", 0.1300, plan, stance=R.REFUSED)
check(held_cheap["usd_per_ns"] < R.APPROVED_USD_PER_NS and "not on price" in held_cheap["cell"],
      "a hold at a sane rate is not labelled a price refusal — it would misdirect the reader to the market")
check("$0 spent" in held_cheap["cell"], "...and it still says nothing is being spent")

print("== the default is PAYING — an un-stanced row is money until proven otherwise")
check(R.row("RTX 4090", 0.2497, plan)["cell"] == paying["cell"],
      "omitting the stance renders the paying form, the safe direction for a spend report")

print("== an unrecognised stance RAISES rather than guessing")
try:
    R.row("RTX 4090", 0.2497, plan, stance="maybe")
    check(False, "a bogus stance must not be silently accepted")
except ValueError:
    check(True, "a bogus stance raises ValueError instead of defaulting into one of the two meanings")

print("== a rate taken from an OFFER quote is marked as a lower bound, not passed off as the billed rate")
# Measured 2026-07-27 (vast_rate_forensics, instance 46000463): the offer quoted $0.17922/hr and the instance
# is billed $0.20272/hr. Reporting the first as if it were the second is what made one host read 1.41x at
# rental and 1.82x while running, and look like a price rise.
quote = R.row("RTX 4090", 0.1792222222222222, plan, rate_basis=R.RATE_FROM_OFFER)
billed = R.row("RTX 4090", 0.20272222222222222, plan)
check("LOWER BOUND" in quote["cell"] and "offer quote" in quote["cell"],
      "the quote-derived row says what it is")
check("LOWER BOUND" not in billed["cell"], "the billed row carries no such caveat")
check(billed["multiple"] > quote["multiple"],
      "and the billed multiple really is the larger of the two, which is why the caveat is not decorative")

print("== the parsed CLI spec carries the stance, because one board mixes both")
check(R.parse_spec("RTX 4090=0.4459:refused") == ("RTX 4090", "0.4459", R.REFUSED, R.RATE_FROM_INSTANCE),
      "`gpu=dph:refused` parses to a refused row")
check(R.parse_spec("RTX 4090=0.2497") == ("RTX 4090", "0.2497", R.PAYING, R.RATE_FROM_INSTANCE),
      "a bare `gpu=dph` parses to a paying row on the billed rate")
check(R.parse_spec("RTX 4090=0.1792@offer")[3] == R.RATE_FROM_OFFER, "`@offer` marks the rate's provenance")

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print("all in-flight $/ns reporting tests passed")
