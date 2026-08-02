#!/usr/bin/env python3
"""The two selcal systems as DeepTernary blind controls — the head-to-head against our own co-folds.

WHY. Our Boltz co-folds of these two systems score DockQ **0.023-0.046** on the degradation-target↔VHL
interface against the deposited ternaries (`selcal-cofold-dockq.json`, two independent instruments). The
question the fix turns on is whether a different generator does better ON THE SAME TWO TARGETS, scored by the
SAME instruments against the SAME references. That is a like-for-like comparison, not a new benchmark.

★ IT IS A VALID BLIND TEST, AND THIS WAS CHECKED BEFORE ANY OF IT WAS BUILT.
`deepternary-leakage-check.json`: 9DTY and 9DTX are absent from DeepTernary's disclosed 4,471-id exclusion set
(both deposited after its 2023-10-14 horizon). Had either been present, a good score would have proven
nothing and this file would not exist.

⚠ AND THE EXPECTED RESULT IS UNKNOWN — DO NOT QUOTE 0.62-0.83 FOR IT. Those qualification figures come from
5T35 / 6HAX / 6HR2 / 6BN7, every one of which IS in the exclusion set, so they measure reproduction of seen
structures rather than blind performance. Blind performance on a VHL neosubstrate interface has not been
measured by anyone here, and should be assumed worse. What makes the experiment worth running is not a
confident prior — it is that the incumbent sits at 0.023-0.046, so the bar to clear is low and the run is free.

⛔ WHAT A PASS WOULD AND WOULD NOT BUY. A better interface score licenses exactly one sentence: *a different
generator places this target against VHL closer to the crystal than the co-folds did.* It says NOTHING about
NR4A3, about degradation, about selectivity, or about whether the endpoint can rank paralogues — the panel
those co-folds fed returned a NULL whose bound is unchanged by anything here. It would mean the fix is worth
carrying into a re-run, and that is all.

INPUTS ARE SOURCED, NEVER GUESSED. DeepTernary's PROTAC mode needs, per arm, a target structure plus the
warhead fragment in that frame, and an E3 structure plus the anchor fragment in its frame — all from
structures that are NOT the native ternary. Candidates are queried from RCSB by UniProt accession
(`deepternary_blind_controls.source_input_structures`, reused as-is) and the final pick is curated. Guessing a
PDB id here is the integrity gate this program already tripped once, when memory-based E3 labels were wrong on
three of five entries.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "selcal-deepternary-controls.json")

#: VCB accessions, shared by both arms: VHL, Elongin C, Elongin B.
VCB_UNIPROTS = ["P40337", "Q15369", "Q15370"]

#: ⚠ BASE ACCESSIONS, deliberately. `selcal_stage` uses **P51531-2** (isoform 2) because the crystallographers'
#: construct numbering is isoform-specific and slicing the canonical entry would take a different span. RCSB's
#: accession search indexes the BASE accession, so the isoform suffix is dropped HERE and only here — the
#: construct definition is untouched and still lives in `selcal_stage.CONSTRUCTS`.
ARMS = [
    {"arm_id": "selcal_smarca2", "pdb": "9DTY", "e3": "VHL",
     "target_of_interest": "SMARCA2 bromodomain", "poi_uniprot_base": "P51531"},
    {"arm_id": "selcal_smarca4", "pdb": "9DTX", "e3": "VHL",
     "target_of_interest": "SMARCA4 bromodomain", "poi_uniprot_base": "P51532"},
]


def controls():
    """The two arms in the shape `deepternary_blind_controls.source_input_structures` consumes."""
    return [{"pdb": a["pdb"], "e3": a["e3"], "target_of_interest": a["target_of_interest"],
             "uniprots": [a["poi_uniprot_base"]] + VCB_UNIPROTS,
             "arm_id": a["arm_id"]} for a in ARMS]


def leakage_is_clear(path=None):
    """(ok, detail) — refuse to source inputs for an arm whose reference DeepTernary may have seen.

    A blind control that is not blind is worse than no control: it produces a number that looks like
    validation. So this is checked from the committed artifact at build time, not remembered."""
    path = path or os.path.join(HERE, "deepternary-leakage-check.json")
    if not os.path.exists(path):
        return False, "deepternary-leakage-check.json absent — blindness unverified, so nothing is sourced"
    doc = json.load(open(path))
    seen = {r["pdb"]: r["in_training_or_exclusion_set"] for r in doc.get("structures", [])}
    bad = [a["pdb"] for a in ARMS if seen.get(a["pdb"]) is not False]
    if bad:
        return False, ("%s is in (or absent from) DeepTernary's disclosed exclusion set — not established as "
                       "blind, so it may not be used as a blind control" % bad)
    return True, "9DTY and 9DTX are absent from the disclosed exclusion set (post-horizon)"


def source(exclude_native=None):
    """Query RCSB for candidate non-native binaries per arm. Network; CI only."""
    import deepternary_blind_controls as B
    ok, detail = leakage_is_clear()
    out = {
        "_what": "Candidate NON-NATIVE binary structures for DeepTernary blind inputs on the two selcal arms.",
        "_why": "Our co-folds score DockQ 0.023-0.046 on the target<->VHL interface of these very systems. "
                "This sets up the same-target, same-instrument, same-reference head-to-head.",
        "_licenses": "NOTHING about NR4A3, degradation or selectivity. A better score here would license one "
                     "sentence about generator placement and nothing more.",
        "_expected_performance": "UNKNOWN. The 0.62-0.83 qualification figures are on structures inside "
                                 "DeepTernary's exclusion set and do not predict this.",
        "blindness_verified": ok,
        "blindness_detail": detail,
        "arms": [{k: v for k, v in a.items()} for a in ARMS],
        "candidates": {},
    }
    if not ok:
        out["candidates"] = {"_refused": detail}
        return out
    excl = set(exclude_native or [])
    excl |= set(json.load(open(os.path.join(HERE, "deepternary_exclusion_set.json")))["ids"])
    out["candidates"] = B.source_input_structures(controls(), excl)
    out["_curation_required"] = ("These are CANDIDATES. The final per-arm pick is curated against the "
                                 "integrity gate — a guessed PDB id is the defect that put wrong E3 labels on "
                                 "three of five entries once already.")
    return out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Source DeepTernary blind inputs for the two selcal arms.")
    ap.add_argument("--out", default=OUT_JSON)
    args = ap.parse_args(argv)
    doc = source()
    json.dump(doc, open(args.out, "w"), indent=1)
    print("[selcal-dt] wrote %s" % args.out, flush=True)
    print("[selcal-dt] blindness verified: %s — %s" % (doc["blindness_verified"], doc["blindness_detail"]),
          flush=True)
    for pdb, c in (doc.get("candidates") or {}).items():
        if pdb.startswith("_"):
            print("  REFUSED:", c); continue
        print("  %s  POI=%s (%s): %d candidate binaries | E3=%s: %d"
              % (pdb, c.get("poi"), c.get("poi_uniprot"), len(c.get("poi_binary_candidates") or []),
                 c.get("e3"), len(c.get("e3_binary_candidates") or [])), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
