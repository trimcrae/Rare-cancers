#!/usr/bin/env python3
"""$0 PRE-FLIGHT: prove the atom map is complete BEFORE a single GPU-second is billed.

WHY THIS IS A SEPARATE, MANDATORY STEP AND NOT A COMMENT IN A RUNBOOK
--------------------------------------------------------------------
`openfe.setup.LomapAtomMapper(time=N)` — `N` is the MCS **timeout in seconds** — does not raise when it runs
out of budget. It returns the best PARTIAL match found so far, silently. So the atom map, which *is* the
definition of the alchemical transformation, was a function of how fast the rented host happened to be.
Measured on RUNG 5a-KS (2026-07-26): one edge whose two ligands differ by a single atom, and which therefore
admits a complete 111-atom 1:1 map, mapped 111 atoms on two hosts and **80 atoms with 31 dummies** on a
third — at `element_change` both True and False, which is the signature of a timeout rather than of chemistry.

A short map is not a slow answer. It is a DIFFERENT EXPERIMENT: atoms that should have mapped 1:1 become
dummies that are annihilated and recreated, the leg converges perfectly well, and it returns a confident ΔG
for a perturbation nobody designed. Nothing downstream can see it:

  * `protocol_hash` covers the OpenFE SETTINGS, not the map.
  * `system_identity_consistency` covers particle counts, which dummy-isation leaves unchanged.
  * the 5-part pre-spend gate's item 2 asks whether there is "a real perturbation", and unmapped atoms
    SATISFY that — so a degenerate map makes the gate greener, not redder.

Hence this file: derive what the map MUST be from the endpoints themselves, run the production mapper under
the production budget, and refuse to launch on a mismatch. It runs on a free CI runner inside the parity
image (`docker.io/triskit23/ternary-fep`), which is the same RDKit/OpenFE the rented hosts will use, so a
pass here is evidence about the run and not about a lookalike environment.

USAGE (inside the image, with the stage cache already extracted under --input-dir):
    python valb_map_preflight.py --input-dir /tmp/tin \
        --leg-id calib_hi_to_lo__ternary_vhl --leg-id calib_hi_to_lo__binary_vhl --out report.json

Exit status is the gate: 0 = every leg's map is complete, 1 = at least one is short (or could not be built).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_leg(tf, rbfe, openfe, Chem, leg_id):
    """Build this leg's two endpoints and audit the map the production mapper returns for them.

    The ligands are read from the leg's staged `ligands.sdf` and the environment is forced to `solvent`, so
    the multi-megabyte assembled `complex.pdb` is never parsed. That is not a shortcut: reviewer item 3
    requires the binary and ternary legs to use the SAME atom map, and the map is a function of the two
    SmallMoleculeComponents alone — `threed=False` makes it explicitly pose-independent, which is the whole
    reason the binary lane uses 2D MCS. Checking the ligand pair therefore checks every environment's map.
    """
    leg = tf.leg_spec(leg_id)[0]
    endpoints = tf._morph_endpoints(leg)
    a, b, sa, sb = endpoints
    tf.assert_constitutional_edge(sa, sb)
    ligA, ligB, _ = tf._build_components(openfe, Chem, leg, "solvent", endpoints)
    mapping = rbfe._mapping(openfe, ligA, ligB, prefer_element_change=True)
    audit = tf.atom_map_audit(Chem, ligA, ligB, mapping)
    audit["leg_id"] = leg_id
    audit["morph"] = "%s->%s" % (a, b)
    return audit


def main(argv=None):
    ap = argparse.ArgumentParser(description="$0 atom-map pre-flight for the valB_mini calibration legs")
    ap.add_argument("--input-dir", default=os.environ.get("INPUT_DIR", "/tmp/tin"),
                    help="directory holding <leg_id>/ligands.sdf (an extracted stage cache)")
    ap.add_argument("--leg-id", action="append", required=True)
    ap.add_argument("--out", default=None, help="write the audit JSON here")
    a = ap.parse_args(argv)

    # The engine reads INPUT_DIR at import time into a module global, so set it before importing rather than
    # after — assigning the global afterwards would work today and break the first time the read moves.
    os.environ["INPUT_DIR"] = a.input_dir
    os.environ.setdefault("RBFE_LOMAP_TIME_S", "300")

    import openfe                                   # noqa: F401 — presence is part of what this proves
    from rdkit import Chem

    import nr4a3_rbfe as rbfe
    import nr4a3_ternary_fep as tf
    tf.IN = a.input_dir

    print("[preflight] LOMAP MCS budget RBFE_LOMAP_TIME_S=%ss" % os.environ["RBFE_LOMAP_TIME_S"], flush=True)
    audits, bad = [], []
    for leg_id in a.leg_id:
        try:
            audit = check_leg(tf, rbfe, openfe, Chem, leg_id)
        except Exception as e:  # noqa: BLE001 — an un-buildable endpoint is a launch blocker, not a warning
            print("[preflight] %s: COULD NOT BUILD — %s: %s" % (leg_id, type(e).__name__, e), flush=True)
            bad.append({"leg_id": leg_id, "error": "%s: %s" % (type(e).__name__, e)})
            continue
        audits.append(audit)
        verdict = "SHORT" if audit["degenerate"] else ("UNCHECKED" if audit["mcs_timed_out"] else "COMPLETE")
        print("[preflight] %-34s %s: %d/%d heavy atoms mapped (expected %s from the endpoint MCS), "
              "%d total mapped, A=%d atoms B=%d atoms"
              % (leg_id, verdict, audit["n_heavy_mapped"], audit["heavy_atoms_A"],
                 audit["expected_heavy_mapped"], audit["n_mapped_atoms"],
                 audit["n_atoms_A"], audit["n_atoms_B"]), flush=True)
        if audit["degenerate"]:
            bad.append({"leg_id": leg_id, "error": "degenerate map: %d heavy mapped, %d expected"
                        % (audit["n_heavy_mapped"], audit["expected_heavy_mapped"])})
        # An expectation that could not be computed is NOT a pass. It means the check did not run, and a
        # check that reports success while measuring nothing is the failure mode this lane keeps paying for.
        elif audit["mcs_timed_out"]:
            bad.append({"leg_id": leg_id, "error": "the RDKit MCS timed out, so no expectation exists to "
                                                   "check the LOMAP map against"})

    report = {"_what": "atom-map pre-flight for the valB_mini calibration edge (Wurz cmpd1 -> cmpd4)",
              "_why": "LomapAtomMapper(time=N) silently returns a PARTIAL map on MCS timeout; a short map is "
                      "a different alchemical transformation that still converges and still returns a "
                      "confident dG. protocol_hash does not cover the map and the 5-part gate reads unmapped "
                      "atoms as evidence of a real perturbation.",
              "lomap_time_s": int(os.environ["RBFE_LOMAP_TIME_S"]),
              "legs": audits, "blocking": bad, "pass": not bad}
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(report, fh, indent=2)
            fh.write("\n")
    if bad:
        print("[preflight] ❌ REFUSING TO LAUNCH — %d leg(s) blocked: %s"
              % (len(bad), json.dumps(bad)), flush=True)
        return 1
    print("[preflight] ✅ every leg's atom map is complete at the production budget — safe to rent.",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
