#!/usr/bin/env python3
"""INDEPENDENT re-derivation of the PUB-STRATEGY-ARCH keyword-screen table.

Written from the two committed deposits directly. It does NOT import
keyword_screen_benchmark.py; it re-reads the raw JSON, rebuilds the visible-field
text and the confusion matrices with its own code, and then compares its numbers
digit for digit against the numbers the prior lane published in
PUB-STRATEGY-ARCH/keyword-screen-benchmark.json. Any mismatch is a FAILURE.

Not medical advice, not a trial-matching service. Every label is a statement
about registry text on the retrieval dates recorded in the source deposits.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
FET = os.path.join(ROOT, "research/literature/fet-fusion-trial-eligibility-2026-08-07.json")
ADJ = os.path.join(ROOT, "research/literature/emc-trial-reachability-adjudication-2026-08-09.json")
PRIOR = os.path.join(HERE, "..", "PUB-STRATEGY-ARCH", "keyword-screen-benchmark.json")

# Ground truth, re-transcribed by this lane from the deposit fields, independently
# of the prior lane's table. verdict / recruiting / interventional and the exact
# deposit field each is read from.
TRUTH = {
    "NCT05918640": dict(v="admits",  rec=True,  itv=True,
        src="fet:task_2_widened_search.confirmed_fusion_family_defined[0]"
            ".assessment ('names the FET fusion FAMILY') + overall_status=RECRUITING"),
    "NCT06571734": dict(v="admits",  rec=True,  itv=True,
        src="adj:adjudications[NCT06571734].verdict ('ADMITS') "
            "+ overall_status=RECRUITING + study_type=INTERVENTIONAL"),
    "NCT04151342": dict(v="admits",  rec=True,  itv=False,
        src="adj:adjudications[NCT04151342].verdict ('ADMITS BY WORDING, BUT IT IS "
            "OBSERVATIONAL') + study_type=OBSERVATIONAL"),
    "NCT06094101": dict(v="refuses", rec=True,  itv=True,
        src="adj:adjudications[NCT06094101].verdict ('DOES NOT ADMIT') "
            "+ overall_status=RECRUITING"),
    "NCT07188532": dict(v="refuses", rec=True,  itv=True,
        src="adj:adjudications[NCT07188532].verdict ('DOES NOT ADMIT') "
            "+ overall_status=RECRUITING"),
    "NCT07695311": dict(v="refuses", rec=False, itv=True,
        src="fet:screened_and_excluded[NCT07695311].assessment ('EXCLUDED for EMC on "
            "the retrieved eligibility text') + overall_status=NOT_YET_RECRUITING"),
    "NCT07328425": dict(v="refuses", rec=True,  itv=True,
        src="fet:screened_and_excluded[NCT07328425].assessment ('EXCLUDED for EMC on "
            "the retrieved eligibility text') + overall_status=RECRUITING"),
    "NCT05275426": dict(v="admits",  rec=False, itv=True,
        src="fet:screened_and_excluded[NCT05275426].eligibility_basis ('would have "
            "admitted EMC') + overall_status=COMPLETED"),
}

LEXICONS = {
    "histology_only": ["extraskeletal", "extra-skeletal", "extra skeletal",
                       "myxoid", "chondrosarcoma"],
    "molecular_only": ["nr4a3", "ewsr1", "fet fusion", "fusion", "translocation"],
}
LEXICONS["union"] = LEXICONS["histology_only"] + LEXICONS["molecular_only"]


def visible_fields():
    """brief_title + official_title + listed_conditions, per record, from raw JSON.

    Where the later adjudication deposit (2026-08-09) carries a listed_conditions
    array or an official_title_verbatim for a record, that later reading wins --
    the same rule the prior lane used, restated here rather than imported.
    """
    fet = json.load(open(FET))["task_2_widened_search"]
    adj = json.load(open(ADJ))
    out = {}
    for key in ("confirmed_fusion_family_defined",
                "molecularly_defined_not_histology_defined",
                "candidates_requiring_eligibility_text_verification",
                "screened_and_excluded"):
        for r in fet[key]:
            d = out.setdefault(r["nct_id"], {"bt": "", "ot": "", "lc": []})
            d["bt"] = r.get("brief_title") or d["bt"]
            d["ot"] = r.get("official_title") or d["ot"]
            d["lc"] = r.get("listed_conditions") or d["lc"]
    for a in adj["adjudications"]:
        d = out.setdefault(a["nct_id"], {"bt": "", "ot": "", "lc": []})
        if not d["ot"] and a.get("official_title_verbatim"):
            d["ot"] = a["official_title_verbatim"]
        if a.get("listed_conditions"):
            d["lc"] = a["listed_conditions"]
    return {k: " | ".join([v["bt"], v["ot"]] + list(v["lc"])).lower()
            for k, v in out.items()}


def score(text_of, ids, lex):
    tp = fp = tn = fn = 0
    for i in ids:
        hit = any(t in text_of[i] for t in lex)
        adm = TRUTH[i]["v"] == "admits"
        if hit and adm: tp += 1
        elif hit and not adm: fp += 1
        elif (not hit) and adm: fn += 1
        else: tn += 1
    p = tp / (tp + fp) if (tp + fp) else None
    r = tp / (tp + fn) if (tp + fn) else None
    return dict(n=tp + fp + tn + fn, true_positive=tp, false_positive=fp,
                true_negative=tn, false_negative=fn, precision=p, recall=r)


def main():
    text_of = visible_fields()
    missing = [i for i in TRUTH if i not in text_of]
    if missing:
        print("FAIL: ids absent from deposits: %s" % missing, file=sys.stderr)
        return 2

    all_ids = list(TRUTH)
    ri_ids = [i for i in TRUTH if TRUTH[i]["rec"] and TRUTH[i]["itv"]]
    mine = {}
    for name, lex in LEXICONS.items():
        mine[name] = score(text_of, all_ids, lex)
        mine[name + "__recruiting_interventional"] = score(text_of, ri_ids, lex)

    prior = json.load(open(PRIOR))["results"]
    fails = []
    print("%-45s %-28s %-28s %s" % ("screen", "this lane", "PUB-STRATEGY-ARCH", "match"))
    for name in sorted(mine):
        m, p = mine[name], prior.get(name)
        fmt = lambda d: ("n=%d TP=%d FP=%d TN=%d FN=%d P=%s R=%s" % (
            d["n"], d["true_positive"], d["false_positive"], d["true_negative"],
            d["false_negative"],
            "undef" if d["precision"] is None else "%.4f" % d["precision"],
            "undef" if d["recall"] is None else "%.4f" % d["recall"]))
        if p is None:
            ok = False
        else:
            ok = all(m[k] == p[k] for k in ("n", "true_positive", "false_positive",
                                            "true_negative", "false_negative",
                                            "precision", "recall"))
        if not ok:
            fails.append(name)
        print("%-45s %-28s %-28s %s" % (name, fmt(m), fmt(p) if p else "ABSENT",
                                        "OK" if ok else "MISMATCH"))
    print("\nMISMATCHES:", len(fails), fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
