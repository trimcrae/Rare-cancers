#!/usr/bin/env python3
"""Keyword-screen benchmark for PUB-STRATEGY-ARCH (RT-TRIAL-REACH).

Question: the manuscript argues that a keyword-built reachability map is worse than
no map, because two of its adjudicated records would have "passed an automated
screen". That asymmetry is stated as "an argument from the adjudications rather
than a quantity measured here". This script MEASURES the half of it that the
committed deposit can support -- the screen's precision and recall against the
eligibility-read adjudications -- and leaves the cost half explicitly unmeasured.

Inputs (committed, read-only; nothing is fetched):
  research/literature/fet-fusion-trial-eligibility-2026-08-07.json
  research/literature/emc-trial-reachability-adjudication-2026-08-09.json

Ground truth = the admit/refuse verdict reached by READING the record's posted
eligibility text. Only records for which such a verdict exists in the deposit are
scored. Every label below is transcribed from the deposit, not inferred here.

NOT a matching service, not medical advice, and not a statement about who enrols.
"""
import json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
FET = os.path.join(ROOT, "research/literature/fet-fusion-trial-eligibility-2026-08-07.json")
ADJ = os.path.join(ROOT, "research/literature/emc-trial-reachability-adjudication-2026-08-09.json")

# --- ground truth, each cell transcribed from a named field of a named file ---
# verdict: "admits" / "refuses" on the posted eligibility criteria, as adjudicated.
GROUND_TRUTH = [
    dict(nct="NCT05918640", verdict="admits",
         source=("fet-fusion-trial-eligibility-2026-08-07.json",
                 "task_2_widened_search.confirmed_fusion_family_defined[0].eligibility_basis"),
         basis="fusion-family-defined (FET: EWSR1 / FUS / TAF15)",
         interventional=True, recruiting=True),
    dict(nct="NCT06571734", verdict="admits",
         source=("emc-trial-reachability-adjudication-2026-08-09.json", "adjudications[].verdict"),
         basis="cohort for translocation-associated soft tissue sarcoma",
         interventional=True, recruiting=True),
    dict(nct="NCT04151342", verdict="admits",
         source=("emc-trial-reachability-adjudication-2026-08-09.json", "adjudications[].verdict"),
         basis="observational basket, rare molecular alterations",
         interventional=False, recruiting=True),
    dict(nct="NCT06094101", verdict="refuses",
         source=("emc-trial-reachability-adjudication-2026-08-09.json", "adjudications[].verdict"),
         basis="fusion-framed title, histology-restricted criteria",
         interventional=True, recruiting=True),
    dict(nct="NCT07188532", verdict="refuses",
         source=("emc-trial-reachability-adjudication-2026-08-09.json", "adjudications[].verdict"),
         basis="'extra-skeletal' means extraskeletal Ewing sarcoma",
         interventional=True, recruiting=True),
    dict(nct="NCT07695311", verdict="refuses",
         source=("fet-fusion-trial-eligibility-2026-08-07.json",
                 "task_2_widened_search.screened_and_excluded[].assessment"),
         basis="partner-restricted (EWSR1-FLI1 / EWSR1-ERG / EWSR1-WT1)",
         interventional=True, recruiting=False),   # NOT_YET_RECRUITING per deposit
    dict(nct="NCT07328425", verdict="refuses",
         source=("fet-fusion-trial-eligibility-2026-08-07.json",
                 "task_2_widened_search.screened_and_excluded[].assessment"),
         basis="partner-restricted (EWSR1-WT1)",
         interventional=True, recruiting=True),
    dict(nct="NCT05275426", verdict="admits",
         source=("fet-fusion-trial-eligibility-2026-08-07.json",
                 "task_2_widened_search.screened_and_excluded[].eligibility_basis"),
         basis="'rearrangement between EWSR1 and a non-ETS family gene'",
         interventional=True, recruiting=False),   # COMPLETED per deposit
]

# --- the screens, defined a priori, over the fields a string matcher can see ---
LEXICONS = {
    "histology_only": ["extraskeletal", "extra-skeletal", "extra skeletal",
                       "myxoid", "chondrosarcoma"],
    "molecular_only": ["nr4a3", "ewsr1", "fet fusion", "fusion", "translocation"],
    "union": ["extraskeletal", "extra-skeletal", "extra skeletal", "myxoid",
              "chondrosarcoma", "nr4a3", "ewsr1", "fet fusion", "fusion", "translocation"],
}

def visible_text(rec):
    """Fields a keyword matcher reads: titles + listed conditions. NOT eligibility text."""
    parts = [rec.get("brief_title") or "", rec.get("official_title") or ""]
    parts += list(rec.get("listed_conditions") or [])
    return " | ".join(parts).lower()

def load_records():
    fet = json.load(open(FET))["task_2_widened_search"]
    adj = json.load(open(ADJ))
    by_nct = {}
    for key in ("confirmed_fusion_family_defined", "molecularly_defined_not_histology_defined",
                "candidates_requiring_eligibility_text_verification", "screened_and_excluded"):
        for r in fet[key]:
            by_nct.setdefault(r["nct_id"], {}).update(
                {k: v for k, v in r.items() if v not in (None, [], "")})
    for a in adj["adjudications"]:
        d = by_nct.setdefault(a["nct_id"], {})
        if a.get("official_title_verbatim"):
            d.setdefault("official_title", a["official_title_verbatim"])
        if a.get("listed_conditions"):
            d["listed_conditions"] = a["listed_conditions"]   # adjudication date is later
    return by_nct

def main():
    recs = load_records()
    missing = [g["nct"] for g in GROUND_TRUTH if g["nct"] not in recs]
    if missing:
        print("FAIL: ground-truth ids absent from deposit: %s" % missing, file=sys.stderr)
        return 2
    rows, results = [], {}
    # stratum: all adjudicated records, and the decision-relevant slice a patient
    # could actually join today (recruiting AND interventional).
    for name, lex, stratum in ([(n, l, "all_adjudicated") for n, l in LEXICONS.items()]
                               + [(n + "__recruiting_interventional", l,
                                   "recruiting_interventional") for n, l in LEXICONS.items()]):
        tp = fp = tn = fn = 0
        for g in GROUND_TRUTH:
            if stratum == "recruiting_interventional" and not (g["recruiting"] and g["interventional"]):
                continue
            text = visible_text(recs[g["nct"]])
            hits = [t for t in lex if t in text]
            carried = bool(hits)
            admits = g["verdict"] == "admits"
            if carried and admits: tp += 1
            elif carried and not admits: fp += 1
            elif not carried and admits: fn += 1
            else: tn += 1
            if name == "union" and stratum == "all_adjudicated":
                rows.append(dict(nct=g["nct"], truth=g["verdict"], basis=g["basis"],
                                 interventional=g["interventional"], recruiting=g["recruiting"],
                                 visible_fields=visible_text(recs[g["nct"]]),
                                 hits_union=hits, source_field=list(g["source"])))
        n = tp + fp + tn + fn
        prec = tp / (tp + fp) if (tp + fp) else None
        rec_ = tp / (tp + fn) if (tp + fn) else None
        results[name] = dict(lexicon=lex, stratum=stratum, n=n, true_positive=tp, false_positive=fp,
                             true_negative=tn, false_negative=fn,
                             precision=prec, recall=rec_)
        print("%-45s n=%d  TP=%d FP=%d TN=%d FN=%d  precision=%s recall=%s"
              % (name, n, tp, fp, tn, fn,
                 "%.2f" % prec if prec is not None else "undefined",
                 "%.2f" % rec_ if rec_ is not None else "undefined"))

    out = dict(
        _what="Keyword-screen precision/recall against eligibility-read adjudications, EMC.",
        _not_medical_advice=("Not medical advice, not a trial-matching service. Every label is a "
                             "statement about registry text on the retrieval dates in the source "
                             "deposit. No patient, enrolment, referral or outcome is involved."),
        generated_by="research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                     "PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-STRATEGY-ARCH/keyword_screen_benchmark.py",
        inputs=[os.path.relpath(FET, ROOT), os.path.relpath(ADJ, ROOT)],
        ground_truth_definition=("admit/refuse on the record's POSTED eligibility text as adjudicated "
                                 "in the cited deposit field; records without such a verdict are "
                                 "excluded from scoring rather than assumed negative."),
        screen_definition=("case-insensitive substring match over brief_title + official_title + "
                           "listed_conditions only -- the fields a string matcher sees. Eligibility "
                           "text is deliberately NOT given to the screen."),
        denominator_is_a_floor=("The candidate pool came from screens one of which returned at its "
                                "page limit, so the eight scored records are not a sample of the "
                                "registry and these rates are not registry-wide rates."),
        results=results, records=rows)
    dest = os.path.join(os.path.dirname(__file__), "keyword-screen-benchmark.json")
    json.dump(out, open(dest, "w"), indent=2)
    print("wrote", os.path.relpath(dest, ROOT))
    return 0

if __name__ == "__main__":
    sys.exit(main())
