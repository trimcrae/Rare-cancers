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
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import vast_cost_model as vcm    # noqa: E402  the single source for throughput and cost

# ≳1.5× the basis is drift. Not a hard gate — the fleet-launch gate in the launcher is that — but the point at
# which a row must SAY it is drifting rather than leaving the reader to divide.
DRIFT_MULTIPLE = 1.5


def basis_usd_per_ns(planning_usd_per_ref_gpu_h):
    """The ladder's $/ns: its planning rate per REFERENCE GPU-hour ÷ the reference card's ns/h."""
    return float(planning_usd_per_ref_gpu_h) / vcm.REFERENCE_NS_PER_H


def row(gpu_name, dph_total, planning_usd_per_ref_gpu_h, storage_usd_h=0.0):
    """One board row's $/ns cell. Returns a dict; `cell` is the string to paste.

    `None` throughput (a card never benched) yields UNKNOWN rather than a guessed number — the same choice
    `usd_per_ns` makes, and for the same reason: a fabricated figure ranks an offer it cannot price.
    """
    nsh = vcm.ns_per_hour(gpu_name)
    if not nsh:
        return {"gpu": gpu_name, "usd_per_ns": None, "multiple": None,
                "cell": f"$/ns UNKNOWN — {gpu_name} is not in the throughput table, so it cannot be graded"}
    pn = vcm.usd_per_ns(float(dph_total), float(storage_usd_h), nsh)
    basis = basis_usd_per_ns(planning_usd_per_ref_gpu_h)
    mult = pn / basis
    cell = f"${pn:.5f}/ns · {mult:.2f}× basis"
    if mult >= DRIFT_MULTIPLE:
        cell += " ⚠ DRIFT"
    return {"gpu": gpu_name, "ns_per_h": nsh, "usd_per_ns": pn, "basis": basis,
            "multiple": mult, "drifting": mult >= DRIFT_MULTIPLE, "cell": cell}


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        print("usage: inflight_usd_per_ns.py <planning_usd_per_ref_gpu_h> <gpu_name>=<dph> [...]")
        return 2
    plan = float(argv[1])
    print(f"basis = ${basis_usd_per_ns(plan):.5f}/ns  "
          f"(${plan}/ref-GPU-h ÷ {vcm.REFERENCE_NS_PER_H:.2f} ns/h on {vcm.REFERENCE_CARD})\n")
    for spec in argv[2:]:
        name, _, dph = spec.rpartition("=")
        r = row(name, dph, plan)
        print(f"  {name:12} ${float(dph):.4f}/hr   {r['cell']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
