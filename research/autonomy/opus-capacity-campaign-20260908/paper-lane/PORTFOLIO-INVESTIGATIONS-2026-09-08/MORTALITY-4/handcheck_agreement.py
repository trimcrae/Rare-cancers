#!/usr/bin/env python3
"""Agreement between the pre-specified machine genre rule and the hand adjudication of the
40-paper random sample. Produces the confusion matrix, overall agreement, and the
per-stratum precision/recall that matters most here: the case_report_or_series stratum,
because the whole genre-confound question turns on whether case reports are identified.

No cue field, no rate: this runs before the stratified rate script."""
import json, math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from genre_classifier import classified_rows, STRATA  # noqa: E402

HAND = pathlib.Path(__file__).with_name("handcheck-labels.json")
OUT = pathlib.Path(__file__).with_name("handcheck-agreement.json")


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def main():
    by = {r["pmid"]: r for r in classified_rows()}
    hand = json.loads(HAND.read_text())["labels"]
    conf = {}
    disagreements = []
    for h in hand:
        m = by[h["pmid"]]["stratum"]
        conf.setdefault(m, {}).setdefault(h["hand"], 0)
        conf[m][h["hand"]] += 1
        if m != h["hand"]:
            disagreements.append({"pmid": h["pmid"], "machine": m, "hand": h["hand"],
                                  "note": h["note"], "title": by[h["pmid"]]["title"]})
    n = len(hand)
    agree = n - len(disagreements)
    per = {}
    for s in STRATA:
        tp = sum(1 for h in hand if h["hand"] == s and by[h["pmid"]]["stratum"] == s)
        mach = sum(1 for h in hand if by[h["pmid"]]["stratum"] == s)
        true = sum(1 for h in hand if h["hand"] == s)
        per[s] = {"machine_n": mach, "hand_n": true, "correct": tp,
                  "precision": round(tp / mach, 4) if mach else None,
                  "precision_wilson95": wilson(tp, mach) if mach else None,
                  "recall": round(tp / true, 4) if true else None,
                  "recall_wilson95": wilson(tp, true) if true else None}
    out = {"_what_this_is": __doc__.strip(),
           "n_sampled": n, "seed": 20260908,
           "overall_agreement": round(agree / n, 4),
           "overall_agreement_wilson95": wilson(agree, n),
           "disagreements": disagreements,
           "confusion_machine_rows_hand_cols": conf,
           "per_stratum": per,
           "_single_reader": "One reader, unblinded to EMC status (the disease name is in the title). No second reader, so no inter-rater kappa is available."}
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("n_sampled", "overall_agreement", "overall_agreement_wilson95", "per_stratum")}, indent=1))
    print("\ndisagreements:")
    for d in disagreements:
        print(f' {d["pmid"]}  machine={d["machine"]:22s} hand={d["hand"]:22s} {d["note"]}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
