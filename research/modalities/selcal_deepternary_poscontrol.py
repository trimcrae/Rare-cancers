#!/usr/bin/env python3
"""The positive ternary control: re-score DeepTernary's own benchmark case with OUR instruments. ($0 CPU)

★★ WHY THIS EXISTS. Our Boltz co-folds score DockQ 0.023–0.046 against the deposited ternaries 9DTY/9DTX,
measured twice by two independent implementations. A number that low invites exactly one objection, and it
is the right objection: **has anything ever scored HIGH through this harness?** Until something has, a
near-zero reading cannot be told apart from a broken pipeline, a mis-chosen reference, or a scorer that
returns ~0 for everything it is handed.

So: run the generator on a ternary it is known to recover, through this harness, and score it with the same
instruments we quote everywhere else. `output.zip` ships DeepTernary's OWN complete unbound inputs for its
22-case PROTAC benchmark, and `6HAX_B_A_FWZ` is a VHL/SMARCA2 PROTAC ternary — the same E3 and the same
target family as the two systems this lane cares about. Nothing needs preparing; the inputs are theirs.

✅ WHAT A HIGH SCORE HERE ESTABLISHES: that this CPU torch/dgl build, this checkpoint, this seed budget and
these two scoring instruments together produce and recognise a correct ternary complex. A near-zero score
elsewhere is then a statement about that input or that system, not about the plumbing.

⛔ WHAT IT DOES NOT ESTABLISH, AND MUST NEVER BE QUOTED AS: generalisation. 6HAX was deposited in 2018, far
inside DeepTernary's 2023-10-14 data horizon, so it is memorisation-permitting by construction. This is a
POSITIVE CONTROL ON THE INSTRUMENT. It says nothing about NR4A3, about degradation, about selectivity, and
nothing about blind performance on 9DTY/9DTX.

⚠ AND A LOW SCORE HERE IS THE MORE INFORMATIVE OUTCOME, not a run to retry quietly: it would mean the
near-zero co-fold readings are uninterpretable until the harness is fixed, and it would have to be reported
that way.
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))

#: DockQ's own CAPRI-style class boundary for "Acceptable". The field's threshold, not one chosen here.
ACCEPTABLE_DOCKQ = 0.23

#: What this control has to clear to be worth calling a positive control. A generator on an in-set case it
#: has memorised should be comfortably into DockQ's "Medium" class; anything less and the harness is the
#: suspect, which is the whole question being asked.
POSITIVE_CONTROL_DOCKQ = 0.49


def single_interface(dockq_doc):
    """(interface record, error) when the reference has exactly ONE protein–protein interface.

    ⚠ NOT `best_interface`. Picking the highest-scoring interface out of a multi-chain complex is the exact
    defect that once reported DockQ 0.95–0.97 for our co-folds by scoring Elongin B against Elongin C and
    briefly overturned a real finding. This control's reference is a two-chain complex, so there is one
    interface and no choosing to do — and if that ever stops being true, this REFUSES rather than picks."""
    per = (dockq_doc or {}).get("best_result") or (dockq_doc or {}).get("interfaces") or {}
    if not isinstance(per, dict):
        return None, "DockQ reported no per-interface results"
    scored = {k: v for k, v in per.items() if isinstance(v, dict) and "DockQ" in v}
    if len(scored) != 1:
        return None, ("DockQ scored %d interfaces %s, not 1 — this control refuses to choose one, because "
                      "choosing the best is how an Elongin B–Elongin C interface was once reported as the "
                      "answer" % (len(scored), sorted(scored)))
    return list(scored.values())[0], None


def score_predictions(pred_dir, native_path, case=None):
    import selcal_dockq_crosscheck as X
    case = case or "6HAX_B_A_FWZ"
    doc = {
        "_what": "positive control: DeepTernary's own benchmark case, re-scored by OUR instruments",
        "case": case,
        "case_is_in_set": True,
        "_case_is_in_set_means": ("6HAX was deposited in 2018, inside DeepTernary's 2023-10-14 data horizon. "
                                  "This controls the HARNESS AND THE INSTRUMENTS, never generalisation, and "
                                  "must not be quoted as blind performance."),
        "dockq_version": X.dockq_version(),
        "native": native_path,
        "acceptable_bar": ACCEPTABLE_DOCKQ,
        "positive_control_bar": POSITIVE_CONTROL_DOCKQ,
        "_bar_source": "DockQ's own CAPRI-style class boundaries (Acceptable 0.23, Medium 0.49).",
        "poses": [],
    }
    if not os.path.exists(native_path):
        doc["error"] = "reference %s absent" % native_path
        doc["sentence"] = ("No reference to score against — this is an UNREAD control, not a failed one.")
        return doc
    preds = sorted(glob.glob(os.path.join(pred_dir, "complex_pred_%s_*.pdb" % case)))
    if not preds:
        preds = sorted(glob.glob(os.path.join(pred_dir, "complex_pred_*.pdb")))
    doc["n_predictions"] = len(preds)
    if not preds:
        doc["error"] = "no predicted complexes under %s" % pred_dir
        doc["sentence"] = ("The positive control produced no predictions to score. Unrun is not a run that "
                           "scored zero, and nothing downstream may be read as if this had passed.")
        return doc

    for p in preds:
        d, err = X.run_dockq(p, native_path)
        if err:
            doc["poses"].append({"pose": os.path.basename(p), "error": err})
            continue
        iface, ierr = single_interface(d)
        if ierr:
            doc["poses"].append({"pose": os.path.basename(p), "error": ierr})
            continue
        doc["poses"].append({
            "pose": os.path.basename(p),
            "DockQ": X._first(iface, "DockQ"),
            "fnat": X._first(iface, "fnat"),
            "iRMSD_A": X._first(iface, "iRMSD", "iRMS"),
            "LRMSD_A": X._first(iface, "LRMSD", "LRMS"),
            "quality_class": X.quality_class(X._first(iface, "DockQ")),
        })

    ok = [r for r in doc["poses"] if r.get("DockQ") is not None]
    doc["n_scored"] = len(ok)
    if not ok:
        doc["sentence"] = ("Predictions exist but none could be scored — an instrument failure, reported as "
                           "one rather than as a score of zero.")
        return doc
    vals = [r["DockQ"] for r in ok]
    best = max(vals)
    doc["summary"] = {"best_DockQ": round(best, 4),
                      "median_DockQ": round(sorted(vals)[len(vals) // 2], 4),
                      "best_quality_class": X.quality_class(best),
                      "best_fnat": max(r["fnat"] for r in ok),
                      "best_iRMSD_A": min(r["iRMSD_A"] for r in ok if r["iRMSD_A"] is not None)}
    doc["positive_control_passes"] = bool(best >= POSITIVE_CONTROL_DOCKQ)
    doc["sentence"] = (
        "Positive control %s: DeepTernary on its own in-set case %s reaches DockQ %.3f (%s) over %d scored "
        "poses, measured by the same DockQ implementation that put our co-folds at 0.023–0.046. %s"
        % ("PASSES" if best >= POSITIVE_CONTROL_DOCKQ else "FAILS", case, best,
           doc["summary"]["best_quality_class"], len(ok),
           ("The harness and both instruments can therefore produce and recognise a correct ternary, so a "
            "near-zero reading elsewhere is about that input or that system — not about the plumbing. It "
            "says nothing about generalisation: this case is inside the model's data horizon."
            if best >= POSITIVE_CONTROL_DOCKQ else
            "Until that is fixed, the near-zero co-fold readings are UNINTERPRETABLE — a harness that cannot "
            "score a known-good complex cannot be used to grade a suspect one.")))
    return doc


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Positive ternary control on DeepTernary's own case ($0 CPU).")
    ap.add_argument("--pred-dir", required=True)
    ap.add_argument("--native", required=True)
    ap.add_argument("--case", default="6HAX_B_A_FWZ")
    ap.add_argument("--out", default=os.path.join(HERE, "selcal-deepternary-poscontrol.json"))
    args = ap.parse_args(argv)
    doc = score_predictions(args.pred_dir, args.native, args.case)
    json.dump(doc, open(args.out, "w"), indent=1)
    print(doc["sentence"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
