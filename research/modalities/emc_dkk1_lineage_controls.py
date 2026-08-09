#!/usr/bin/env python3
"""DKK1 in EMC against each comparator class separately — the controls that were already in the data.

⭐ WHY THIS EXISTS. `DKK1` is the largest single-gene signal in this repository's expression census:
concordantly elevated on both readable platforms, every EMC sample above the comparator median on the
powered one. The census row that would own it — `MOD-WNT-BETA-CATENIN` — was `excluded` with
`prior_coverage: never_searched`, on the reasoning that "none is reported in EMC's quiet genome".
That is an exclusion argued from an assumption about the genome while the strongest transcript in the
pathway sat unread in the panel.

⛔ THE OBVIOUS CONFOUND CANNOT BE SETTLED HERE AND THIS FILE SAYS SO RATHER THAN WORKING AROUND IT.
EMC is a chondroid tumour and NO COMPARATOR IN EITHER SERIES IS CARTILAGE-LINEAGE — they are LGFMS,
desmoid fibromatosis, fibrosarcoma, DFSP and GIST. So "chondroid tumours express DKK1" is NOT excluded
by anything below, and no statement here may be read as excluding it.

⭐ WHAT THE POOLED CONTRAST HID, AND WHY PER-CLASS IS THE RIGHT CUT. Two of the comparator classes are
themselves controls for the two most obvious alternative explanations, and pooling them into one
"comparator" arm threw that away:

  * LGFMS is FUS::CREB3L2 — a FET-family fusion sarcoma. If DKK1 tracked "having a FET fusion", LGFMS
    would be high with EMC. It is the LOWEST of the four classes.
  * DESMOID FIBROMATOSIS is the canonical Wnt/beta-catenin-activated tumour. If DKK1 here were simply
    reporting Wnt pathway output, desmoid would be high. It reads LOW.

Neither is proof of anything; both are the kind of internal control that a pooled arm makes invisible.

⚠ AND THE READING IS NOT A MECHANISM. What elevated DKK1 implies about Wnt pathway STATE in this
disease is a literature question, deliberately not answered from recall here — see
research/literature/dkk1-wnt-2026-08-09.json for what was actually retrieved and read.

⛔ NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS for any agent in
this disease. It reports a transcript contrast in archival tissue.

$0 — reads a committed artifact, stdlib only, runs anywhere.
"""
from __future__ import annotations

import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.join(HERE, "emc-expression-panels.json")
OUT = os.path.join(HERE, "emc-dkk1-lineage-controls.json")

#: The gene this file is about, plus two neighbours read the same way so the DKK1 result is not the
#: only number on the page. NR4A1/NR4A2 are here because they sit in the same curated group that first
#: surfaced DKK1, and that group's score turned out to be carried by DKK1 rather than by them.
GENES = ("DKK1", "NR4A1", "NR4A2")

#: What each comparator class controls FOR. ⚠ Membership is a fact about the series; the control
#: interpretation is this repository's reading and is labelled as such.
CLASS_ROLE = {
    "LGFMS": "FET-fusion control — FUS::CREB3L2. Tests whether the reading tracks 'has a FET fusion'.",
    "desmoid_fibromatosis": "Wnt-activation control — the canonical beta-catenin-driven tumour. Tests "
                            "whether the reading is simply Wnt pathway output.",
    "fibrosarcoma": "fibroblastic comparator, no specific control role.",
    "DFSP": "fibroblastic comparator (COL1A1::PDGFB), no specific control role.",
    "GIST": "non-fibroblastic, non-cartilage comparator, no specific control role.",
    "EMC": "the disease.",
}


def per_class(panel, gene):
    out = {}
    for plat, v in (panel["gene_reads"].get(gene) or {}).items():
        if not isinstance(v, dict) or not v.get("readable"):
            out[plat] = {"_readable": False,
                         "_reading": "⛔ NOT READABLE on this platform — the read could not be taken. "
                                     "This says NOTHING about whether the gene is expressed."}
            continue
        groups, dropped = {}, 0
        for s in v["per_sample"]:
            z = s.get("z_vs_array")
            if z is None:            # ⚠ dropped, never zero-filled: a missing value is not a low one
                dropped += 1
                continue
            groups.setdefault(s["class"], []).append(z)
        rows = {}
        for k, vals in groups.items():
            rows[k] = {"n": len(vals), "median_z": round(st.median(vals), 3),
                       "min_z": round(min(vals), 3), "max_z": round(max(vals), 3),
                       "role": CLASS_ROLE.get(k, "unclassified")}
        emc = groups.get("EMC") or []
        others = {k: vs for k, vs in groups.items() if k != "EMC"}
        sep = {}
        for k, vs in others.items():
            sep[k] = {
                "emc_median_minus_class_median": round(st.median(emc) - st.median(vs), 3) if emc else None,
                "emc_min_above_class_max": (min(emc) > max(vs)) if emc and vs else None,
            }
        out[plat] = {"_readable": True, "platform": v.get("platform"),
                     "n_samples_dropped_for_no_value": dropped,
                     "by_class": rows, "separation_vs_each_class": sep}
    return out


def main():
    with open(PANEL, encoding="utf-8") as fh:
        panel = json.load(fh)
    res = {g: per_class(panel, g) for g in GENES}
    out = {
        "_what": "DKK1 (and two neighbours) in EMC against EACH comparator class separately, rather "
                 "than against a pooled comparator arm.",
        "_generated_by": "research/modalities/emc_dkk1_lineage_controls.py",
        "_source": "research/modalities/emc-expression-panels.json (gene_reads[*].per_sample)",
        "_this_computes_nothing_new": "Every z-score is lifted from the committed panel. What is new "
                                      "is the CUT — per comparator class instead of pooled.",
        "⛔_the_confound_this_cannot_settle": "NO COMPARATOR IN EITHER SERIES IS CARTILAGE-LINEAGE. "
            "EMC is a chondroid tumour and every comparator here is fibroblastic or GIST, so "
            "'chondroid tumours express DKK1' is NOT excluded by anything in this file and must not "
            "be described as excluded. Settling it needs a series containing conventional "
            "chondrosarcoma or normal cartilage, and none is on disk.",
        "⚠_what_a_z_score_is_here": "Each value is the sample's own z against that array's full probe "
            "distribution, so it is a within-array position, not a cross-platform quantity. Medians "
            "are compared within a platform only.",
        "_no_clinical_claim": "⛔ Nothing here asserts efficacy, safety, a therapeutic window or "
            "clinical readiness for any agent. It is a transcript contrast in archival tissue.",
        "class_roles": CLASS_ROLE,
        "genes": res,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}")
    for g, plats in res.items():
        for plat, r in plats.items():
            if not r.get("_readable"):
                print(f"  {g:7} {plat[:26]:28} NOT READABLE")
                continue
            order = sorted(r["by_class"].items(), key=lambda kv: -kv[1]["median_z"])
            desc = "  ".join(f"{k}={v['median_z']:+.2f}(n{v['n']})" for k, v in order)
            print(f"  {g:7} {plat[:26]:28} {desc}")


if __name__ == "__main__":
    main()
