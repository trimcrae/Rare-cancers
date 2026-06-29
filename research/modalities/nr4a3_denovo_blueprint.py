#!/usr/bin/env python3
"""De-novo plan STEP 1 — the NR4A3 selectivity blueprint (generation-conditioning spec).

Reads nr4a-selectivity.json (the AFDB-model + fpocket + BLOSUM62 NR4A1/2/3 pocket characterisation),
classifies the orthosteric Pocket-5 lining residues via the pure, unit-tested denovo_blueprint, and writes
nr4a3-denovo-blueprint.json: the conditioning spec for the two de-novo campaigns —
  - SELECTIVE campaign: condition generation on the engageable DIVERGENT handles (weighting handles that
    discriminate BOTH paralogues over single-paralogue levers), anchoring on the conserved core.
  - PAN campaign: condition on the CONSERVED core (a distinct molecule for ex-vivo/transient immuno-oncology
    triple-NR4A degradation).
Pure CPU/JSON — runs locally, no AWS/MD. This is design prep (a screening prior), not a validated lead.
"""
import json
import os
import sys

import denovo_blueprint as bp

HERE = os.path.dirname(os.path.abspath(__file__))
SELECTIVITY = os.path.join(HERE, "nr4a-selectivity.json")
# Engageable handles = the pocket-facing divergent residues confirmed by the handle-facing run
# (28249776934): mean 5.0/7 facing; T407/R412 splay outward. The realistic selectivity set is these five.
ENGAGEABLE = ["L406", "T410", "I484", "I531", "L534"]
POCKET = 5
OUT = os.environ.get("OUTPUT_PATH", os.path.join(HERE, "nr4a3-denovo-blueprint.json"))


def main():
    if not os.path.exists(SELECTIVITY):
        sys.exit(f"  ABORT: missing {SELECTIVITY}")
    sel = json.load(open(SELECTIVITY))
    pocket = bp.find_pocket(sel, POCKET)
    if not pocket:
        sys.exit(f"  ABORT: Pocket-{POCKET} not found in {SELECTIVITY}")

    cls = bp.classify_pocket(pocket["residues"], ENGAGEABLE)
    sel_nums = [h["num"] for h in cls["selective_handles"]]
    core_nums = [c["num"] for c in cls["conserved_core"]]
    both = [h["residue"] for h in cls["selective_handles"] if h["weight"] == 2]

    out = {
        "_note": "NR4A3 de-novo selectivity blueprint (generation-conditioning spec). Classifies the "
                 "orthosteric Pocket-5 lining residues into engageable divergent handles (selectivity "
                 "levers) vs the conserved core, from nr4a-selectivity.json + the handle-facing run. "
                 "Design prep / screening prior, NOT a validated lead. The receptor to condition on is the "
                 "druggable UNBIASED RELEASE sub-ensemble (Step 0 / nr4a3-release-druggable), not the "
                 "biased-metad frame.",
        "pocket": POCKET,
        "pocket_druggability_static": pocket.get("druggability"),
        "pocket_resid_span": pocket.get("resid_span"),
        "engageable_source": "handle-facing run 28249776934 (mean 5.0/7 facing; T407/R412 splay outward)",
        "classification": cls,
        "campaigns": {
            "selective": {
                "goal": "NR4A3-selective warhead (EMC/AciCC; NR4A3-overexpression-driven indications)",
                "condition_on_handles": sel_nums,
                "prioritise_handles_discriminating_both_paralogues": both,
                "anchor_on_conserved": core_nums,
                "note": "Weight contacts to both-paralogue handles (L406,T410,I484,L534) over the "
                        "NR4A1-only lever I531 (I531 is identical to NR4A2 — the 5-vs-NR4A1/4-vs-NR4A2 "
                        "asymmetry). Score generated molecules by engageable-handle contact + selectivity "
                        "margin downstream (matrix / MM-GBSA).",
            },
            "pan": {
                "goal": "pan-NR4A (triple-degrader) warhead for ex-vivo/transient immuno-oncology",
                "condition_on_conserved": core_nums,
                "note": "Distinct molecule; conditions on the conserved core so it engages all three "
                        "paralogues. Comparison/contrast campaign, not a contingency.",
            },
        },
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)
    s = cls["summary"]
    print(f"  Pocket-{POCKET} (static druggability {pocket.get('druggability')}): "
          f"{s['n_selective_handles']} engageable selective handles "
          f"({s['n_discriminate_both']} discriminate both paralogues, "
          f"{s['n_discriminate_nr4a1_only']} NR4A1-only, {s['n_discriminate_nr4a2_only']} NR4A2-only); "
          f"{s['n_conserved_core']} conserved-core residues; "
          f"{s['n_divergent_non_engageable']} divergent-but-splayed.", flush=True)
    print(f"  SELECTIVE conditioning handles: {sel_nums} (prioritise both-paralogue: {both})", flush=True)
    print(f"  PAN conditioning (conserved core): {core_nums}", flush=True)
    print(f"  wrote {OUT}", flush=True)


if __name__ == "__main__":
    main()
