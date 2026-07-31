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

# ≳1.5× the basis is drift — and since trimcrae's 2026-07-27 ruling it is also the HARD BUY LINE, not
# only the point at which a row must say it is drifting: *"What's the point of tracking that if we don't
# act on it?"* A row that prints ⚠ DRIFT is a row the launcher refuses to rent (the effective ceiling is
# the lower of this and the rung's derived dollar ceiling — congeneric_fanout.unit_ceiling_components).
# SUPERSEDED, retained for the record: this constant was previously documented here as "not a hard gate
# — the fleet-launch gate in the launcher is that". That framing no longer stands. It remains the point at
# which a row must SAY it is drifting rather than leaving the reader to divide.
# ★★ THE APPROVED RATE IS AN ABSOLUTE $/ns. THE MULTIPLE IS DERIVED FROM IT (trimcrae, 2026-07-27).
#
# WHAT WENT WRONG, and it is the failure mode this constant now exists to prevent. The buy line was typed as
# a MULTIPLE of the ladder basis. On 2026-07-27 the basis moved — the reference card's throughput was
# re-measured and the widened throughput table admitted 97 more gradeable offers, so the best-10 mean rate
# fell — and the basis dropped 22 % ($0.004359 -> $0.003412/ns). **No price moved. The yardstick did.** A
# multiple pinned to a moving denominator silently became a much stricter rule than the one agreed: every
# board seen that day failed a line it had been passing.
#
# So the invariant is the thing trimcrae actually approved — an absolute dollars-per-nanosecond — and the
# multiple falls out of it. A future basis change now RE-DERIVES the multiple instead of silently changing
# the rule, which is the whole point of the fix.
#
# ⚠ ≈1.92x IS NOT A LOOSENING OF "1.5x". It is the same dollars per nanosecond expressed against a corrected
# basis: 1.5 x $0.004359 and 1.92 x $0.003412 are both $0.006539/ns. Anyone reading the multiple alone will
# reach the wrong conclusion, which is why both expressions and the basis change travel together everywhere
# this number is printed.
#
# The approved rate is itself DERIVED (rule 1) from the two constants that defined it at the moment of
# approval. Those are retired as CURRENT values and registered in pinned-figures.json; they are kept here
# only as the historical definition of the approved rate, which is a fact about the approval and does not
# change when the throughput table does.
_APPROVAL_PLAN_USD_PER_REF_GPU_H = 0.1372     # the ladder's planning rate at the time of the ruling
_APPROVAL_REFERENCE_NS_PER_H = 31.473333333333333  # the RETIRED reference rate, ns per reference GPU-hour
#                                                   (kept in ns/h form: this module must contain no card
#                                                    throughput figure — vast_cost_model is the only table)
_APPROVAL_MULTIPLE = 1.5                      # "1.5x basis", as the ruling stated it

#: THE INVARIANT — the absolute rate per nanosecond that was approved. Everything else derives from it.
APPROVED_USD_PER_NS = _APPROVAL_MULTIPLE * (_APPROVAL_PLAN_USD_PER_REF_GPU_H / _APPROVAL_REFERENCE_NS_PER_H)


def drift_multiple():
    """The buy/drift line as a multiple of the CURRENT ladder basis. DERIVED, never typed.

    Read the block above before concluding the rule was loosened: the multiple moves only because the basis
    was corrected, and the product is invariant."""
    from congeneric_fanout import basis_usd_per_ns
    b = basis_usd_per_ns()
    return (APPROVED_USD_PER_NS / b) if b > 0 else _APPROVAL_MULTIPLE


def __getattr__(name):
    """`DRIFT_MULTIPLE` survives as a NAME for the modules that import it, but is re-derived on every read.

    A module-level float would freeze the multiple against whatever basis the ladder artifact held at import
    — the same staleness bug one level down. NOTE: PEP 562 module `__getattr__` does not cover global name
    lookup inside THIS module, so code here calls `drift_multiple()` directly."""
    if name == "DRIFT_MULTIPLE":
        return drift_multiple()
    raise AttributeError(name)

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


# ★★ WHICH TIER THIS ROW IS RENTING ON (trimcrae, 2026-07-31: *"Update the status table to show on demand /
# interruptible too."*). It belongs in THIS cell rather than in a column each lane formats for itself, for the
# same reason the rate does: one home, one rendering, no two lanes free to disagree about what a tier looks
# like. It also became load-bearing the same day, when the gate started PREFERRING the uninterruptible tier
# whenever it clears both ceilings — a policy that can buy the dearer tier, on a board that could not show
# which rows took it, is the unreadable-hold failure one level up: a rising ladder spend with no attributable
# cause.
#
# ⚠ ABSENT IS NOT BID. `TIER_UNKNOWN` is a THIRD value, never a default to interruptible. The instance
# record's `is_bid` may be missing, or the record may not have been read at all, and CLAUDE.md §4 is explicit
# that an absent reading is not a reading of absence. A row that silently claims "bid" when nobody looked is
# how a ledger becomes fiction — and it would understate exactly the spend this column exists to attribute.
TIER_BID = "bid"                 # interruptible: cheap, preemptible
TIER_ONDEMAND = "on-demand"      # uninterruptible: dearer, cannot be preempted
TIER_UNKNOWN = "unknown"         # we did not look, or the field was absent — NOT a synonym for bid

# Terse on purpose: this column is already the widest on the board and `inflight_board.render()` sizes it from
# the rows, so every character here costs width on every row.
_TIER_TAG = {TIER_BID: "[bid]", TIER_ONDEMAND: "[ON-DEMAND]", TIER_UNKNOWN: "[tier?]"}


def tier_of(is_bid):
    """`is_bid` from a Vast instance record -> one of the three tiers. PURE.

    Deliberately NOT truthiness: `None` (absent) and `False` (on-demand) are opposite answers and truthiness
    collapses them into the same branch — which is precisely the "absent is not bid" error, arriving through
    a `if is_bid:` that looks harmless."""
    if is_bid is None:
        return TIER_UNKNOWN
    if isinstance(is_bid, str):
        v = is_bid.strip().lower()
        if v in ("true", "1", "yes"):
            return TIER_BID
        if v in ("false", "0", "no"):
            return TIER_ONDEMAND
        return TIER_UNKNOWN
    return TIER_BID if bool(is_bid) else TIER_ONDEMAND


def row(gpu_name, dph_total, planning_usd_per_ref_gpu_h, storage_usd_h=0.0,
        stance=PAYING, rate_basis=RATE_FROM_INSTANCE, tier=None):
    """One board row's $/ns cell. Returns a dict; `cell` is the string to paste.

    `tier` is one of `TIER_BID` / `TIER_ONDEMAND` / `TIER_UNKNOWN` (or None = do not render a tier at all,
    which is what a REFUSED row wants: nothing was rented, so there is no tier we are on).

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
        return {"gpu": gpu_name, "usd_per_ns": None, "multiple": None, "stance": stance, "tier": tier,
                "cell": (f"$/ns UNKNOWN — {gpu_name} is not in the throughput table, so it cannot be graded"
                         + (" " + _TIER_TAG.get(tier, _TIER_TAG[TIER_UNKNOWN]) if tier else ""))}
    pn = vcm.usd_per_ns(float(dph_total), float(storage_usd_h), nsh)
    basis = basis_usd_per_ns(planning_usd_per_ref_gpu_h)
    mult = pn / basis
    # Called directly: PEP 562's module `__getattr__` does not cover global lookup inside this module. It
    # also re-derives per row, which is the point — the flag and the buy line must be the same number at the
    # same instant.
    line_x = drift_multiple()
    # ★ THE COMPARISON IS ON THE ABSOLUTE RATE, NOT ON THE MULTIPLE. `mult` is computed against the CALLER's
    # `planning_usd_per_ref_gpu_h`, while `line_x` is derived from the LADDER's basis — comparing them is
    # apples to oranges whenever a caller passes its own planning rate, and would make the flag depend on an
    # argument rather than on the rule. The approved rate is a dollars-per-nanosecond, so that is what the
    # flag tests; the multiple is presentation.
    over = pn >= APPROVED_USD_PER_NS
    if stance == REFUSED:
        # The multiple is what we DECLINED. `$0 spent` sits on the same line deliberately: the reader must not
        # have to remember which lanes were held in order to know whether the number in front of them is a bill.
        cell = (f"⛔ REFUSED — {gpu_name} at ${pn:.5f}/ns · {mult:.2f}× basis — $0 spent" if over else
                f"⛔ HELD (not on price) — best available {gpu_name} "
                f"at ${pn:.5f}/ns · {mult:.2f}× basis — $0 spent")
    else:
        # ★ THE CARD IS PART OF THE CELL (trimcrae, 2026-07-31). $/hr cannot show drift because a cheap slow
        # card and an expensive fast one look identical — that is why this column is $/ns at all. But $/ns
        # alone cannot say WHICH of those a row is, so a rate that moved is undiagnosable without going to
        # another artifact for the card. Naming it here makes the whole diagnosis readable in one cell.
        cell = f"{gpu_name} ${pn:.5f}/ns · {mult:.2f}× basis"
        if tier:
            # After the rate, before the drift flag: the flag must stay the last and most prominent thing on
            # a drifting row, which is the whole reason it was made terse.
            cell += " " + _TIER_TAG.get(tier, _TIER_TAG[TIER_UNKNOWN])
        if over:
            # Terse ON PURPOSE. This used to append ~100 characters re-explaining that the line is the same
            # dollars as the original 1.5×, re-expressed against a corrected basis — on EVERY drifting row.
            # That explanation is the CLAUDE.md §1 ruling, which is its one home; repeating it per row is a
            # rule-1 duplication, and with the column now sized to its widest cell it dragged the whole
            # board past 250 characters, so the flag it exists to make prominent became the thing that made
            # the board unreadable. The row states the fact and the threshold; the reasoning lives once.
            cell += f" ⚠ PAYING OVER THE {line_x:.2f}× LINE (${APPROVED_USD_PER_NS:.6f}/ns)"
    if rate_basis == RATE_FROM_OFFER:
        # Not cosmetic. An offer quote is the market floor plus the disk line the search priced, so this
        # multiple is a LOWER BOUND on what the rental will be graded at once the instance exists.
        cell += " (offer quote — floor + the search's disk line, so a LOWER BOUND on the billed rate)"
    return {"gpu": gpu_name, "ns_per_h": nsh, "usd_per_ns": pn, "basis": basis, "multiple": mult,
            "stance": stance, "rate_basis": rate_basis, "tier": tier,
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
