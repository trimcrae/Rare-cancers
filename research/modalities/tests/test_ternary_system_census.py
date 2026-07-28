#!/usr/bin/env python3
"""Pin the census's PURE logic — the water/ion classifier and the cross-leg verdict.

These are the two places the module can be wrong in a way that would read as a confident answer: a water tally
that silently swallows a triatomic ion, and a verdict that calls two failed censuses "identical". Neither needs
openmm, a .nc, or a runner with the parity image, so both are pinned here rather than discovered in CI.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import ternary_system_census as T  # noqa: E402

FAILS = []
RUN = []


def check(cond, msg):
    RUN.append(msg)
    if not cond:
        FAILS.append(msg)
    print(("  ok   " if cond else "  FAIL ") + msg)


# --- the small-molecule classifier -------------------------------------------------------------------------
masses = {}


def _m(spec):
    """Build a masses list and a component index list for one hand-specified molecule."""
    base = len(masses)
    for i, v in enumerate(spec):
        masses[base + i] = v
    return list(range(base, base + len(spec)))


tip3p = _m([15.999, 1.008, 1.008])
tip4p = _m([15.999, 1.008, 1.008, 0.0])
hmr_water = _m([15.999, 1.008, 1.008])       # water is NOT repartitioned by HMR, but the classifier is generous
sodium = _m([22.99])
chloride = _m([35.45])
triatomic_not_water = _m([12.011, 15.999, 15.999])   # CO2-shaped: three real atoms, one heavy is not O-massed
ml = [masses[i] for i in sorted(masses)]

check(T._classify_small(tip3p, ml) == ("water", 3), "TIP3P water classified as water with 3 sites")
check(T._classify_small(tip4p, ml) == ("water", 4), "TIP4P/OPC water classified as water with 4 sites")
check(T._classify_small(hmr_water, ml)[0] == "water", "a second water is still water")
check(T._classify_small(sodium, ml) == ("ion", 22.99), "monatomic Na+ classified as an ion, by mass")
check(T._classify_small(chloride, ml) == ("ion", 35.45), "monatomic Cl- classified as an ion, by mass")
check(T._classify_small(triatomic_not_water, ml)[0] == "other",
      "a triatomic that is NOT one O and two H is NOT counted as water (a bare size-3 tally would be wrong)")


# --- the cross-leg verdict ----------------------------------------------------------------------------------
def rec(label, solute=7245, lig=110, chains=None, q=0.0, total=141968, waters=44800, ions=None, status="ok"):
    return {"label": label, "status": status, "n_solute_atoms": solute, "n_ligand_atoms": lig,
            "protein_chain_sizes": chains if chains is not None else [3000, 2000, 1200, 935],
            "net_charge_e": q, "n_particles": total, "n_water_molecules": waters,
            "ion_mass_histogram": ions if ions is not None else {"22.99": 60, "35.45": 55}}


same = T.compare([rec("a"), rec("b")])
check(same["verdict"].startswith("IDENTICAL"), "two identical censuses report IDENTICAL SYSTEMS")

solvent_only = T.compare([
    rec("2fs", total=141968, waters=44800, ions={"22.99": 60, "35.45": 55}),
    rec("4fs", total=142010, waters=44813, ions={"22.99": 62, "35.45": 57}),
])
check(solvent_only["solute_identical"] and not solvent_only["solvent_identical"],
      "same solute + different water/ion counts -> solute_identical, solvent differs")
check("SAME SOLUTE, DIFFERENT SOLVENT" in solvent_only["verdict"],
      "the solvent-only difference gets its own verdict, distinct from IDENTICAL and from SOLUTE DIFFERS")

solute_diff = T.compare([rec("2fs", solute=7245), rec("4fs", solute=7246)])
check("SOLUTE DIFFERS" in solute_diff["verdict"],
      "a one-atom solute difference is reported as a DIFFERENT SYSTEM, not rounded away")

lig_diff = T.compare([rec("a", lig=110), rec("b", lig=111)])
check("SOLUTE DIFFERS" in lig_diff["verdict"], "a ligand-size difference alone falsifies solute identity")

chain_diff = T.compare([rec("a", chains=[3000, 2000, 1200, 935]), rec("b", chains=[3000, 2000, 1200, 934])])
check("SOLUTE DIFFERS" in chain_diff["verdict"],
      "identical solute TOTAL but different chain sizes still falsifies identity (a total can coincide)")

# absence is never agreement
one_ok = T.compare([rec("a"), rec("b", status="census failed (OSError: truncated)")])
check(one_ok["verdict"].startswith("INSUFFICIENT"), "one usable census is not a comparison")
check(one_ok["uncensused"] == ["b"], "the failed leg is NAMED, not silently dropped")

two_bad = T.compare([rec("a", status="boom"), rec("b", status="boom")])
check(two_bad["verdict"].startswith("INSUFFICIENT"),
      "two FAILED censuses agree on nothing — they must never render as IDENTICAL")

print("\n%d checks, %d failures" % (len(RUN), len(FAILS)))
if FAILS:
    for f in FAILS:
        print("FAILED: " + f)
    sys.exit(1)
print("test_ternary_system_census: PASS")
