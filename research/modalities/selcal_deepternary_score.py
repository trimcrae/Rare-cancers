#!/usr/bin/env python3
"""Score the DeepTernary predictions with the SAME two instruments our own co-folds were scored by. ($0 CPU)

THE COMPARISON, and it is the only one this artifact makes: for each arm, DeepTernary's blind prediction
against the deposited native, versus OUR Boltz co-fold against the same native, on the same
degradation-target<->VHL interface, by the same two independent implementations. Our co-folds sit at
DockQ 0.023-0.046 with fnat 0.000.

⛔ WHAT A BETTER SCORE WOULD AND WOULD NOT BE. It would be a POSITIVE TERNARY CONTROL AT THE GENERATION
STAGE -- a known-answer test, run blind, that the workflow passes -- which this program does not currently
have in any form. It would NOT be a positive control for paralogue-selectivity DETECTION, which is a
different and harder claim about a different stage: the panel those co-folds fed returned a NULL whose bound
is unchanged by anything here. Conflating the two would be the most tempting error available and the paper's
language must not.

⚠ ONE ARM ONLY. The SMARCA4 arm was refused at input verification (its best available fragment shares 0.42 of
its heavy atoms with the degrader, below the 0.55 bar) so there is no SMARCA4 prediction to score and none
may be manufactured. A single-arm result is reported as a single-arm result.

⚠ AND THE COMPARISON IS NOT PERFECTLY MATCHED, which is stated here rather than discovered later: our
co-folds were generated from SEQUENCE ALONE, while DeepTernary is given pre-positioned binary poses from
separate crystals. That is DeepTernary's documented operating mode, not an advantage smuggled in -- but it
means a win says "this pipeline, with these inputs, places the complex better", not "this architecture is
better than that one".
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "selcal-deepternary-headtohead.json")

#: Our own co-folds' scores on the same interface, same references, same instruments. READ from the committed
#: artifact rather than typed, so the thing being beaten cannot drift from what was measured.
def incumbent():
    p = os.path.join(HERE, "selcal-cofold-dockq.json")
    if not os.path.exists(p):
        return None, "selcal-cofold-dockq.json absent — there is nothing to compare against"
    d = json.load(open(p))
    per_arm = {}
    for r in d.get("records", []):
        if r.get("dockq"):
            per_arm.setdefault(r["arm_id"], []).append(r["dockq"]["DockQ"])
    return {a: {"n": len(v), "min": round(min(v), 4), "max": round(max(v), 4),
                "mean": round(sum(v) / len(v), 4)} for a, v in per_arm.items()}, None


def score_arm(arm_name, pred_root, native_path):
    """Score every predicted pose for one arm against the sealed native, target<->VHL interface, by role."""
    import selcal_dockq_crosscheck as X
    import selcal_cofold_validate as V

    d = os.path.join(pred_root, arm_name)
    preds = sorted(glob.glob(os.path.join(d, "**", "*.pdb"), recursive=True))
    preds = [p for p in preds
             if os.path.basename(p) not in ("gt_complex.pdb", "unbound_protein1.pdb", "unbound_protein2.pdb",
                                            "unbound_lig1.pdb", "unbound_lig2.pdb", "ligand.pdb")]
    row = {"arm": arm_name, "n_predictions": len(preds), "native": os.path.basename(native_path),
           "scored": [], "error": None}
    if not preds:
        row["error"] = ("no predicted complex under %s — unrun, NOT a prediction that scored zero" % d)
        return row
    if not os.path.exists(native_path):
        row["error"] = "sealed native %s absent" % native_path
        return row

    # Roles on the native side come from the committed selcal chain map — the same convention every other
    # measurement in this lane uses, so the numbers stay comparable.
    import valb_frame_transfer_check as F
    pdb_id = os.path.splitext(os.path.basename(native_path))[0].upper()
    roles, rerr = F.roles_from_selcal_artifact(pdb_id)
    if rerr:
        row["error"] = "native chain roles unresolved: %s" % rerr
        return row
    row["native_roles"] = roles

    for p in preds:
        doc, err = X.run_dockq(p, native_path)
        if err:
            row["scored"].append({"pose": os.path.basename(p), "error": err})
            continue
        best, ierr = X.target_e3_interface(doc, roles["target"], roles["e3"][0])
        if ierr:
            row["scored"].append({"pose": os.path.basename(p), "error": ierr})
            continue
        row["scored"].append({"pose": os.path.basename(p), "DockQ": best["DockQ"], "fnat": best["fnat"],
                              "iRMSD_A": best["iRMS"],
                              "quality_class": X.quality_class(best["DockQ"])})
    ok = [s for s in row["scored"] if s.get("DockQ") is not None]
    if ok:
        vals = [s["DockQ"] for s in ok]
        row["summary"] = {"n_scored": len(ok), "best_DockQ": round(max(vals), 4),
                          "median_DockQ": round(sorted(vals)[len(vals) // 2], 4),
                          "best_quality_class": X.quality_class(max(vals)),
                          "best_fnat": max(s["fnat"] for s in ok)}
    return row


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Score the DeepTernary head-to-head ($0 CPU).")
    ap.add_argument("--pred-root", required=True)
    ap.add_argument("--native-dir", required=True)
    ap.add_argument("--prep", default=os.path.join(HERE, "selcal-deepternary-prep.json"))
    ap.add_argument("--out", default=OUT_JSON)
    args = ap.parse_args(argv)

    prep = json.load(open(args.prep))
    inc, inc_err = incumbent()
    doc = {
        "_what": "DeepTernary (blind) vs our own Boltz co-folds, same targets, same deposited references, "
                 "same two scoring instruments, same target<->VHL interface.",
        "_what_a_win_would_be": "a POSITIVE TERNARY CONTROL AT THE GENERATION STAGE — a known-answer test, "
                                "run blind, that the workflow passes. This program has none in any form.",
        "_what_a_win_would_NOT_be": "a positive control for paralogue-selectivity DETECTION. Different stage, "
                                    "harder claim; the panel those co-folds fed returned a NULL whose bound "
                                    "is unchanged by anything here.",
        "_not_perfectly_matched": "our co-folds were generated from SEQUENCE ALONE; DeepTernary is given "
                                  "pre-positioned binary poses from separate crystals. That is its documented "
                                  "operating mode, not an advantage smuggled in — but a win says 'this "
                                  "pipeline with these inputs places the complex better', not 'this "
                                  "architecture beats that one'.",
        "incumbent_our_cofolds": inc, "incumbent_error": inc_err,
        "arms_refused_at_input_verification": [a["name"] for a in prep["arms"] if not a["ok"]],
        "arms": [],
    }
    for cfg in prep.get("ready_configs", []):
        native = os.path.join(args.native_dir, "%s.cif" % cfg["native_pdb"])
        if not os.path.exists(native):
            native = os.path.join(args.native_dir, "%s.pdb" % cfg["native_pdb"])
        doc["arms"].append(score_arm(cfg["name"], args.pred_root, native))

    scored = [a for a in doc["arms"] if a.get("summary")]
    if not scored:
        doc["verdict"] = {"positive_ternary_control": None,
                          "sentence": "No arm produced a scored prediction. Unrun is not a failed run."}
    else:
        best = max(scored, key=lambda a: a["summary"]["best_DockQ"])
        b = best["summary"]["best_DockQ"]
        armname = best["arm"]
        ours = (inc or {}).get(armname, {}).get("max")
        beat = (ours is not None and b > ours)
        doc["verdict"] = {
            "arm": armname, "best_DockQ": b, "quality_class": best["summary"]["best_quality_class"],
            "our_cofold_best_DockQ": ours,
            "beats_our_cofold": beat,
            "positive_ternary_control": bool(beat and b >= 0.23),
            "sentence": (
                "DeepTernary, blind, reaches DockQ %.3f (%s) on the %s target<->VHL interface against our "
                "co-folds' %s. %s"
                % (b, best["summary"]["best_quality_class"], armname, ours,
                   ("That clears DockQ's 'Acceptable' bar (0.23) and beats the incumbent — a known-answer "
                    "ternary test the workflow passes, at the GENERATION stage only."
                    if (beat and b >= 0.23) else
                    "That does NOT clear DockQ's 'Acceptable' bar (0.23), so it is not a positive control; "
                    "it is a measured comparison between two generators."))),
            "_bar_source": "DockQ's own CAPRI-style class boundary, the field's threshold, not one set here.",
        }
    json.dump(doc, open(args.out, "w"), indent=1)
    print("[selcal-dt-score] wrote %s" % args.out, flush=True)
    print(json.dumps(doc["verdict"], indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
