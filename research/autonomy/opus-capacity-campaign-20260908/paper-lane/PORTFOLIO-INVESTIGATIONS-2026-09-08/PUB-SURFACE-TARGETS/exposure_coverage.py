#!/usr/bin/env python3
"""Normal-tissue EXPOSURE-EVIDENCE COVERAGE for the EMC surface-antigen candidates.

Question this answers (offline, from committed artifacts only):
for each candidate antigen the manuscript names, in WHICH normal compartments does
any QUANTITATIVE observation exist at all, and which compartments have none?

It reads only two committed artifacts and derives nothing biological:
  research/modalities/emc-surface-normal-window.json   (HPA categorical labels; vital list)
  research/modalities/gse28866-tumour-vs-normal.json   (the only quantitative normal arm)

It is a COVERAGE census, not a target, safety, selectivity or window claim.
"""
import json, os, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
HPA = os.path.join(ROOT, "research/modalities/emc-surface-normal-window.json")
G28 = os.path.join(ROOT, "research/modalities/gse28866-tumour-vs-normal.json")

# GSE28866 organ vocabulary -> the vital-tissue terms it can speak to.
ORGAN_TO_VITAL = {
    "lung": "lung", "kidney": "kidney", "colon": "colon",
    "bowel": "small intestine", "breast": None, "uterus": None,
}

def main():
    hpa = json.load(open(HPA))
    g28 = json.load(open(G28))
    grouping = g28["sources"][0]["grouping"]
    normals = grouping["normal_columns"]

    per_lib = []
    for col in normals:
        parts = col.split("_")           # STT5425_Adult_normal_breast
        per_lib.append({"library": col, "age": parts[1].lower(), "organ": parts[-1].lower()})
    by_organ = collections.Counter((l["organ"], l["age"]) for l in per_lib)
    organs = sorted({l["organ"] for l in per_lib})
    adult_only = sorted({l["organ"] for l in per_lib if l["age"] == "adult"})
    fetal_n = sum(1 for l in per_lib if l["age"] == "fetal")

    vital = hpa["vital_tissues_flagged"]
    covered_vital = sorted({v for o in organs for v in [ORGAN_TO_VITAL.get(o)] if v in vital})
    covered_vital_adult = sorted({v for o in adult_only for v in [ORGAN_TO_VITAL.get(o)] if v in vital})
    uncovered_vital = [v for v in vital if v not in covered_vital]

    genes_quant = sorted(g28["per_gene"]["values"].keys())
    ants = hpa["antigens"]

    rows = {}
    for g in sorted(set(genes_quant) | set(ants.keys())):
        rec = ants.get(g, {})
        q = g28["per_gene"]["values"].get(g)
        rows[g] = {
            "hpa_label_window": rec.get("window"),
            "hpa_quantitative_nTPM_present": rec.get("rna_tissue_specific_nTPM") is not None,
            "hpa_blood_cell_specificity": rec.get("rna_blood_cell_specificity"),
            "quantitative_normal_observation": q is not None,
            "n_normal_libraries_pooled": (q or {}).get("_n_normal_libs"),
            "normal_summary_is_per_organ": False,
            "n_vital_tissues_with_any_quantitative_value": len(covered_vital) if q else 0,
            "n_vital_tissues_with_no_observation": len(uncovered_vital) if q else len(vital),
        }

    out = {
        "_what": ("Coverage census of the normal-tissue (on-target/off-tumour) evidence actually "
                  "available to the EMC surface-antigen candidates, per compartment."),
        "_not": ("Not a safety, selectivity, window, target or efficacy statement. No new expression "
                 "value is computed here; every number is a count over committed records."),
        "_inputs": {"hpa_labels": os.path.relpath(HPA, ROOT), "quantitative_normal_arm": os.path.relpath(G28, ROOT)},
        "quantitative_normal_arm": {
            "deposit": "GSE28866 (3SEQ), normal arm",
            "n_normal_libraries": len(per_lib),
            "n_adult": len(per_lib) - fetal_n,
            "n_fetal": fetal_n,
            "fetal_fraction": round(fetal_n / len(per_lib), 3),
            "organ_types": organs,
            "n_organ_types": len(organs),
            "libraries_per_organ_age": {f"{o}_{a}": n for (o, a), n in sorted(by_organ.items())},
            "organ_types_with_adult_libraries": adult_only,
            "summary_statistic_committed": "single pooled median across all 27 libraries per gene",
            "per_organ_values_available_in_repository": False,
        },
        "vital_tissue_coverage": {
            "vital_tissue_terms_flagged_by_the_heuristic": vital,
            "n_flagged": len(vital),
            "with_any_quantitative_normal_observation": covered_vital,
            "with_any_ADULT_quantitative_normal_observation": covered_vital_adult,
            "n_with_observation": len(covered_vital),
            "n_without_observation": len(uncovered_vital),
            "without_any_observation": uncovered_vital,
            "fraction_of_flagged_vital_tissues_observed": round(len(covered_vital) / len(vital), 3),
        },
        "hpa_instrument": {
            "n_antigen_records": len(ants),
            "n_with_quantitative_tissue_nTPM": sum(1 for v in ants.values() if v.get("rna_tissue_specific_nTPM") is not None),
            "n_with_quantitative_blood_nTPM": sum(1 for v in ants.values() if v.get("rna_blood_cell_specific_nTPM") is not None),
            "window_label_counts": dict(collections.Counter(v.get("window", "NO_RECORD") for v in ants.values())),
        },
        "per_gene": rows,
        "counts": {
            "n_genes_considered": len(rows),
            "n_with_any_quantitative_normal_observation": sum(1 for r in rows.values() if r["quantitative_normal_observation"]),
            "n_with_label_only": sum(1 for r in rows.values() if not r["quantitative_normal_observation"] and r["hpa_label_window"]),
        },
        "_limits": [
            "Counts of EVIDENCE, not of expression. Nothing here says an antigen is or is not present in any tissue.",
            "GSE28866 normal values are deposit-normalised, square-root-compressed 3SEQ summary scores; no test is defined on them.",
            "A tissue counted as 'observed' is observed only as a pooled median that mixes adult and fetal libraries.",
            "The ORGAN_TO_VITAL mapping is a literal string map over this deposit's six organ labels; 'bowel' is mapped to 'small intestine' conservatively.",
        ],
    }
    json.dump(out, sys.stdout, indent=1)
    print()

if __name__ == "__main__":
    main()
