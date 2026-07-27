#!/usr/bin/env python3
"""`$/ns` and its multiple of the ladder basis, for the IN FLIGHT board — derived, never typed.

WHY THIS EXISTS (trimcrae, 2026-07-26: *"add reporting $/ns to the in flight status update so that's easier to
catch in the future if it drifts"*). `$/hr` cannot show drift: a cheap slow card and an expensive fast one look
identical on that axis. On the night this was written, three live hosts sat at 0.99–1.02× the ladder basis and a
fourth at **1.76×**, and nothing on the board made that visible — the $/hr figures were $0.0643, $0.1307,
$0.1391 and $0.2247, which look like a normal spread until you divide by throughput.

WHAT THIS DELIBERATELY DOES NOT DO: compute anything. `vast_cost_model` owns the throughput table
(`MEASURED_NS_PER_DAY_84K` — "THIS IS THE ONLY THROUGHPUT TABLE"), `ns_per_hour`, and `usd_per_ns`. Per rule 1 a
second implementation of a number that already has a home is the bug, so this module is a REPORTER: it calls
those and formats the answer. If a figure here ever disagrees with the cost model, the cost model is right.

The multiple is the point. A bare `$/ns` is a number nobody can grade at 3 AM; `1.8× basis` is a judgement.

★★ AND SO IS THE STANCE (trimcrae, 2026-07-27: *"the $/ns column still shows several rows over 1.5x. Why? Are
we not stopping those runs? What's the point of tracking that if we don't act on it?"*). That question was
NECESSARY, and this format is why it had to be asked. On that morning's board the 19-edge fan-out showed
**3.25×** and valB **1.96×** — but both were HELD by the price gate: nothing rented, **$0 going out**. The
5a-KS leg at 1.51× and the shakeout at 1.82× were money actually leaving the account. All four printed the
same `⚠ DRIFT`.

**One glyph cannot mean both "we are paying this" and "we refused to pay this".** They are opposite outcomes
of the same guard working correctly, and rendering them identically made a working gate look broken. So a row
now declares its STANCE, and the two get marks that cannot be confused:

  * `⚠ PAYING OVER THE …× LINE` — money is going out at a rate the gate would refuse to buy today.
  * `⛔ REFUSED at …` — the gate declined; the multiple is what we DECLINED, and the row carries `$0 spent`.

`⚠` therefore always means spend and `⛔` always means no spend. The default is `paying`, because a row that
cannot say which it is should be read as money until proven otherwise.

★ A ROW ALSO DECLARES WHERE ITS RATE CAME FROM, which is the other half of the same morning's confusion. The
launcher prints `dph≈$X/hr` at submit from the OFFER, and Vast quotes that as the market FLOOR plus a disk
line for the disk the SEARCH priced — while the instance is billed our BID plus the disk line for the volume
actually allocated. Measured 2026-07-27 (`vast_rate_forensics.py`, live instance 46000463): the offer quoted
$0.17922/hr and the instance is billed $0.20272/hr — a $0.0235/hr gap that is exactly $0.0035 of floor→bid
plus $0.0200 of a disk line quoted at 8 GB for an **80 GB** volume, a 10.0× under-quote of the storage line.
A board row typed from the offer quote therefore UNDER-REPORTS its own multiple, which is why one host read
1.41× at rental and 1.82× while running and looked like a price rise. `rate_basis="offer"` makes the cell say
it is a quote instead of letting it pass as the billed rate.
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import vast_cost_model as vcm    # noqa: E402  the single source for throughput and cost

# ≳1.5× the basis is drift. Not a hard gate — the fleet-launch gate in the launcher is that — but the point at
# which a row must SAY it is drifting rather than leaving the reader to divide.
DRIFT_MULTIPLE = 1.5

# The two stances a priced row can have. There is no third: either money is going out at this rate or it is
# not, and every row on the board is one or the other.
PAYING = "paying"        # we are being billed this, right now
REFUSED = "refused"      # a gate declined to buy at this rate; nothing rented, nothing spent

# Where the rate handed to `row()` came from. `instance` is the authoritative billed rate (our bid + the real
# volume's disk line); `offer` is a search-time quote (market floor + the disk line the search priced) and is
# systematically LOW — see the module docstring for the measurement.
RATE_FROM_INSTANCE = "instance"
RATE_FROM_OFFER = "offer"


def basis_usd_per_ns(planning_usd_per_ref_gpu_h):
    """The ladder's $/ns: its planning rate per REFERENCE GPU-hour ÷ the reference card's ns/h."""
    return float(planning_usd_per_ref_gpu_h) / vcm.REFERENCE_NS_PER_H


def row(gpu_name, dph_total, planning_usd_per_ref_gpu_h, storage_usd_h=0.0,
        stance=PAYING, rate_basis=RATE_FROM_INSTANCE):
    """One board row's $/ns cell. Returns a dict; `cell` is the string to paste.

    `None` throughput (a card never benched) yields UNKNOWN rather than a guessed number — the same choice
    `usd_per_ns` makes, and for the same reason: a fabricated figure ranks an offer it cannot price.

    `stance` is `PAYING` or `REFUSED`; see the module docstring for why the distinction is load-bearing. An
    unrecognised stance RAISES rather than falling back to a default — a row that renders a refusal as a
    payment (or the reverse) is the exact defect this argument exists to close, and guessing would reopen it.
    """
    if stance not in (PAYING, REFUSED):
        raise ValueError(f"stance must be {PAYING!r} or {REFUSED!r}, not {stance!r} — a board row that "
                         f"cannot say whether money is going out is the defect this argument closes")
    nsh = vcm.ns_per_hour(gpu_name)
    if not nsh:
        return {"gpu": gpu_name, "usd_per_ns": None, "multiple": None, "stance": stance,
                "cell": f"$/ns UNKNOWN — {gpu_name} is not in the throughput table, so it cannot be graded"}
    pn = vcm.usd_per_ns(float(dph_total), float(storage_usd_h), nsh)
    basis = basis_usd_per_ns(planning_usd_per_ref_gpu_h)
    mult = pn / basis
    over = mult >= DRIFT_MULTIPLE
    if stance == REFUSED:
        # The multiple is what we DECLINED. `$0 spent` sits on the same line deliberately: the reader must not
        # have to remember which lanes were held in order to know whether the number in front of them is a bill.
        cell = (f"⛔ REFUSED at ${pn:.5f}/ns · {mult:.2f}× basis — $0 spent" if over else
                f"⛔ HELD (not on price) — best available ${pn:.5f}/ns · {mult:.2f}× basis — $0 spent")
    else:
        cell = f"${pn:.5f}/ns · {mult:.2f}× basis"
        if over:
            cell += f" ⚠ PAYING OVER THE {DRIFT_MULTIPLE:.1f}× LINE"
    if rate_basis == RATE_FROM_OFFER:
        # Not cosmetic. An offer quote is the market floor plus the disk line the search priced, so this
        # multiple is a LOWER BOUND on what the rental will be graded at once the instance exists.
        cell += " (offer quote — floor + the search's disk line, so a LOWER BOUND on the billed rate)"
    return {"gpu": gpu_name, "ns_per_h": nsh, "usd_per_ns": pn, "basis": basis, "multiple": mult,
            "stance": stance, "rate_basis": rate_basis,
            # `drifting` is kept as the plain "this rate is over the line" fact, unchanged, so existing
            # callers keep working. `paying_over_line` is the one that means "money is going out at it".
            "drifting": over,
            "paying_over_line": over and stance == PAYING,
            "refused": stance == REFUSED,
            "cell": cell}


def parse_spec(spec):
    """`<gpu>=<dph>[:refused][@offer]` -> (gpu, dph, stance, rate_basis). PURE.

    The stance is part of the SPEC rather than a global flag because a board mixes both on the same run —
    which is the whole reason this distinction exists.
    """
    body, _, basis_tag = spec.partition("@")
    body, _, stance_tag = body.partition(":")
    name, _, dph = body.rpartition("=")
    stance = REFUSED if stance_tag.strip().lower() in ("refused", "held", "refuse") else PAYING
    rate_basis = RATE_FROM_OFFER if basis_tag.strip().lower() == "offer" else RATE_FROM_INSTANCE
    return name, dph, stance, rate_basis


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        print("usage: inflight_usd_per_ns.py <planning_usd_per_ref_gpu_h> <gpu_name>=<dph>[:refused][@offer] ...")
        print("  e.g. inflight_usd_per_ns.py 0.137 'RTX 4090=0.2497' 'RTX 4090=0.4104:refused'")
        return 2
    plan = float(argv[1])
    print(f"basis = ${basis_usd_per_ns(plan):.5f}/ns  "
          f"(${plan}/ref-GPU-h ÷ {vcm.REFERENCE_NS_PER_H:.2f} ns/h on {vcm.REFERENCE_CARD})\n")
    for spec in argv[2:]:
        name, dph, stance, rate_basis = parse_spec(spec)
        r = row(name, dph, plan, stance=stance, rate_basis=rate_basis)
        print(f"  {name:12} ${float(dph):.4f}/hr   {r['cell']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
