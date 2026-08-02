#!/usr/bin/env python3
"""Score the DeepTernary predictions with the SAME two instruments our own co-folds were scored by. ($0 CPU)

THE COMPARISON, and it is the only one this artifact makes: for each arm, DeepTernary's prediction against
the deposited native, versus OUR Boltz co-fold against the same native, on the same degradation-target<->VHL
interface, by the same two independent implementations. Our co-folds sit at DockQ 0.023-0.046 with fnat 0.000.

⛔⛔ THE WORD "BLIND" IS NOT AVAILABLE FOR THIS ARM, and it was used here until DeepTernary's own shipped
data was read. `output.zip`'s `6HAX_B_A_FWZ` shows the published UNBOUND protocol superposes both unbound
binaries INTO THE NATIVE TERNARY FRAME and supplies the NATIVE degrader pose (`ligand.pdb` is byte-identical
to the native ligand: max deviation 0.000 A over 66 heavy atoms). See `selcal_deepternary_frame.py` for the
measurement. The model is still genuinely asked for the RELATIVE PLACEMENT of the two proteins -- protein 2
and the ligand are each randomly rotated and translated before the forward pass -- but it is GIVEN which
pocket on each protein the ligand occupies. That is a weaker question than our co-folds were asked (sequence
+ ligand, nothing else), and the two numbers must not be set side by side as though they were one test.

⛔ WHAT A BETTER SCORE WOULD AND WOULD NOT BE. It would be evidence that a dedicated ternary generator,
handed the two binding sites, places these complexes far better than our sequence-only co-folds do. It would
NOT be a positive control for paralogue-selectivity DETECTION, which is a different and harder claim about a
different stage: the panel those co-folds fed returned a NULL whose bound is unchanged by anything here.
Conflating the two would be the most tempting error available and the paper's language must not.
The positive control on the HARNESS lives in `selcal-deepternary-poscontrol.json`, not in this file.

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

    # ⚠ `predict_cpu.py` writes every predicted complex into `cfg.tmp_dir` — a `TemporaryDirectory` whose
    # last line is `cleanup()` — so unpatched, the predictions are DELETED before this ever runs and this
    # module would have recorded "no predictions" for a run that predicted perfectly well. The workflow
    # redirects that directory to `dt/predictions/`, which is the flat layout matched first below. The
    # per-arm-directory layout is kept as a fallback so an older tree still scores.
    d = os.path.join(pred_root, arm_name)
    preds = sorted(glob.glob(os.path.join(pred_root, "complex_pred_%s_*.pdb" % arm_name)))
    if not preds:
        preds = sorted(glob.glob(os.path.join(d, "**", "*.pdb"), recursive=True))
    preds = [p for p in preds
             if os.path.basename(p) not in ("gt_complex.pdb", "unbound_protein1.pdb", "unbound_protein2.pdb",
                                            "unbound_lig1.pdb", "unbound_lig2.pdb", "ligand.pdb",
                                            "protein1.pdb", "protein2.pdb")]
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
    #
    # ★ TWO REFERENCE SHAPES, ONE ROLE ASSIGNMENT. When the reference is the arm's own `gt_complex.pdb`, that
    # file is the SINGLE COPY `selcal_deepternary_frame.py` extracted USING that same committed map, written
    # as chain A = degradation target, chain B = VHL. Scoring against the whole deposit instead would let
    # DockQ map the prediction onto any of 9DTY's ~10 copies, and the named-interface lookup would then
    # refuse every pose — a refusal that would read as "no interface scored well".
    if os.path.basename(native_path) == "gt_complex.pdb":
        roles = {"target": "A", "e3": ["B"],
                 "_derived": "single-copy reference written by selcal_deepternary_frame.py from the committed "
                             "selcal chain map; chain A = target, chain B = VHL by construction"}
    else:
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
    ap.add_argument("--arm-root", default=None,
                    help="DeepTernary input root; each arm's single-copy gt_complex.pdb is preferred as the "
                         "reference when present, because it is the copy the prediction was built against")
    ap.add_argument("--prep", default=os.path.join(HERE, "selcal-deepternary-prep.json"))
    ap.add_argument("--out", default=OUT_JSON)
    args = ap.parse_args(argv)

    prep = json.load(open(args.prep))
    inc, inc_err = incumbent()
    doc = {
        "_what": "DeepTernary vs our own Boltz co-folds, same targets, same deposited references, same two "
                 "scoring instruments, same target<->VHL interface.",
        "_this_arm_is_not_blind": "MEASURED, not assumed: DeepTernary's published UNBOUND protocol superposes "
                                  "both unbound binaries into the NATIVE ternary frame and supplies the "
                                  "NATIVE degrader pose (its own 6HAX_B_A_FWZ ligand.pdb is byte-identical to "
                                  "the native ligand, max deviation 0.000 A over 66 heavy atoms). The model "
                                  "still predicts the RELATIVE PLACEMENT of the two proteins — both protein 2 "
                                  "and the ligand are randomly rotated and translated before the forward pass "
                                  "— but it is GIVEN which pocket on each protein the ligand occupies.",
        "_what_a_win_would_be": "evidence that a dedicated ternary generator, given the two binding sites, "
                                "places these two complexes far better than our sequence-only co-folds do.",
        "_what_a_win_would_NOT_be": "a positive control for paralogue-selectivity DETECTION (different stage, "
                                    "harder claim; the panel those co-folds fed returned a NULL whose bound "
                                    "is unchanged by anything here), and not a blind result.",
        "_the_positive_control_is_elsewhere": "selcal-deepternary-poscontrol.json — the same generator and the "
                                              "same instruments on 6HAX_B_A_FWZ, a case inside the model's "
                                              "data horizon. That controls the HARNESS; this file does not.",
        "_not_perfectly_matched": "our co-folds were generated from SEQUENCE ALONE; DeepTernary is given "
                                  "pre-positioned binary poses in the native frame. That is its documented "
                                  "operating mode, not an advantage smuggled in — but a win says 'this "
                                  "pipeline with these inputs places the complex better', not 'this "
                                  "architecture beats that one'.",
        "incumbent_our_cofolds": inc, "incumbent_error": inc_err,
        "arms_refused_at_input_verification": [a["name"] for a in prep["arms"] if not a["ok"]],
        "arms": [],
    }
    for cfg in prep.get("ready_configs", []):
        native = None
        if args.arm_root:
            cand = os.path.join(args.arm_root, cfg["name"], "gt_complex.pdb")
            if os.path.exists(cand):
                native = cand
        if native is None:
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
            "clears_acceptable": bool(b >= 0.23),
            "sentence": (
                "DeepTernary, given both binding sites in the native frame, reaches DockQ %.3f (%s) on the %s "
                "target<->VHL interface against our sequence-only co-folds' %s. %s"
                % (b, best["summary"]["best_quality_class"], armname, ours,
                   ("That clears DockQ's 'Acceptable' bar (0.23) and beats the incumbent — a generator given "
                    "the two sites places this complex where our co-folds did not."
                    if (beat and b >= 0.23) else
                    "That does NOT clear DockQ's 'Acceptable' bar (0.23); it is a measured comparison between "
                    "two generators and nothing more."))),
            "_bar_source": "DockQ's own CAPRI-style class boundary, the field's threshold, not one set here.",
        }
    json.dump(doc, open(args.out, "w"), indent=1)
    print("[selcal-dt-score] wrote %s" % args.out, flush=True)
    print(json.dumps(doc["verdict"], indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
