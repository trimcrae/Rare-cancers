#!/usr/bin/env python3
"""
EMC Atlas — genetic-dependency evidence for the validation-panel targets (strategy step E).

WHY. The evidence score's `genetic_perturbation` axis was carried only for NR4A3/FLI1. This adds
DepMap CRISPR dependency for the actual TARGETS of the 12-compound validation panel across sarcoma
lines (EMC surrogate), to answer a decision-relevant question the pharmacology cannot: are these
targets a *selective genetic dependency*, or PAN-ESSENTIAL housekeeping genes whose therapeutic
window is purely a pharmacology/exposure question?

Expected & honest framing: proteasome (PSMB5), HSP90, core HDACs, XPO1, POLR2A are pan-essential in
ALL dividing cells -> their EMC "hits" are NOT sarcoma-selective dependencies; the window is set by
achievable exposure/selectivity, not genetics. The kinases (ALK/RET/KIT/VEGFRs/PDGFRs) test whether
any is a selective EMC-relevant dependency (expected: no -> supports the 'RET/ALK are markers, not
addictions' guards). Self-validation: BRD9 must be synovial-selective and POLR2A pan-essential.

Reuses the proven figshare/DepMap download in research/modalities/depmap_sarcoma_dependency.py.
Internet + pandas -> runs in CI. Output: research/atlas/_generated/panel-dependency.json (+ .md).
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "_generated")
os.makedirs(OUTDIR, exist_ok=True)
sys.path.insert(0, os.path.join(HERE, "..", "modalities"))
import depmap_sarcoma_dependency as D  # noqa: E402  (reuse discover/_get/_download)

# Panel compound -> target gene(s). Grouped by the axis each represents in the score.
PANEL_TARGETS = {
    "proteasome (carfilzomib/bortezomib)": ["PSMB5", "PSMB1", "PSMB2"],
    "HDAC (panobinostat/romidepsin/entinostat)": ["HDAC1", "HDAC2", "HDAC3", "HDAC6", "HDAC8"],
    "HSP90 (PU-H71)": ["HSP90AA1", "HSP90AB1"],
    "MDM2/p53 (HDM201)": ["MDM2", "MDM4", "TP53"],
    "BCL2 (venetoclax)": ["BCL2", "BCL2L1", "MCL1"],
    "XPO1 (selinexor)": ["XPO1"],
    "kinases (pazopanib/sunitinib/brigatinib)": ["ALK", "KIT", "KDR", "FLT1", "FLT4",
                                                 "PDGFRA", "PDGFRB", "RET", "FGFR1"],
}
SANITY = ["POLR2A", "BRD9", "SMARCB1", "NR4A3", "EWSR1"]  # pan-essential / selective / fusion controls
ALL = sorted({g for v in PANEL_TARGETS.values() for g in v} | set(SANITY))
DEP = -0.5  # gene effect below this = "dependent"


def main():
    try:
        import pandas as pd
    except ImportError:
        json.dump({"_status": "pandas missing"}, open(os.path.join(OUTDIR, "panel-dependency.json"), "w"), indent=2)
        return

    urls = D.discover_depmap_files()
    release = urls.get("release", "unknown")
    model = pd.read_csv(io.BytesIO(D._get(urls["Model.csv"], timeout=180)))
    id_col = "ModelID" if "ModelID" in model.columns else model.columns[0]
    lin_col = "OncotreeLineage" if "OncotreeLineage" in model.columns else "lineage"
    sub_col = "OncotreeSubtype" if "OncotreeSubtype" in model.columns else None
    model = model.set_index(id_col)
    sarcoma_ids = set(model.index[model[lin_col].isin(["Soft Tissue", "Bone"])])

    crispr_path = D._download(urls["CRISPRGeneEffect.csv"], timeout=900)
    cols = list(pd.read_csv(crispr_path, nrows=0).columns)
    idx_col = cols[0]
    keep = {c.split(" (")[0]: c for c in cols[1:] if c.split(" (")[0] in set(ALL)}
    ge = pd.read_csv(crispr_path, usecols=[idx_col] + list(keep.values()), index_col=0)
    ge.columns = [c.split(" (")[0] for c in ge.columns]
    n_lines = ge.shape[0]

    # subtype-level means (for selectivity) using OncotreeSubtype keyword buckets
    def subtype_mean(gene, kw):
        if sub_col is None or gene not in ge.columns:
            return None
        ids = set(model.index[model[sub_col].astype(str).str.contains(kw, case=False, na=False)])
        s = ge[gene][ge.index.isin(ids)].dropna()
        return round(float(s.mean()), 3) if len(s) else None

    def classify(gene):
        if gene not in ge.columns:
            return {"gene": gene, "status": "not_in_depmap"}
        v = ge[gene].dropna()
        mean = float(v.mean())
        frac_dep = float((v < DEP).mean())
        sar = ge[gene][ge.index.isin(sarcoma_ids)].dropna()
        rest = ge[gene][~ge.index.isin(sarcoma_ids)].dropna()
        sel = round(float(rest.mean() - sar.mean()), 3) if len(sar) and len(rest) else None
        # pan-essential if dependent in the large majority of ALL lines
        if frac_dep >= 0.8:
            status = "pan_essential"
        elif frac_dep >= 0.2 or (sel is not None and sel > 0.2):
            status = "context_dependency"
        else:
            status = "non_essential"
        return {"gene": gene, "mean_gene_effect": round(mean, 3), "frac_dependent": round(frac_dep, 3),
                "sarcoma_mean": round(float(sar.mean()), 3) if len(sar) else None,
                "selectivity_sarcoma_vs_rest": sel, "status": status,
                "synovial_mean": subtype_mean(gene, "synovial"),
                "ewing_mean": subtype_mean(gene, "ewing")}

    groups = {grp: [classify(g) for g in genes] for grp, genes in PANEL_TARGETS.items()}
    sanity = {g: classify(g) for g in SANITY}
    out = {
        "_note": "DepMap CRISPR dependency for validation-panel TARGETS across sarcoma (EMC surrogate). "
                 "Answers: selective dependency vs pan-essential (window = pharmacology). SURROGATE — no EMC line.",
        "release": release, "n_lines": n_lines, "n_sarcoma_lines": len(sarcoma_ids & set(ge.index)),
        "dependent_threshold": DEP, "groups": groups, "sanity_controls": sanity,
        "self_validation": {
            "POLR2A_should_be_pan_essential": sanity.get("POLR2A", {}).get("status"),
            "BRD9_synovial_selective": {"synovial": sanity.get("BRD9", {}).get("synovial_mean"),
                                        "overall_mean": sanity.get("BRD9", {}).get("mean_gene_effect")},
            "NR4A3_should_be_non_essential": sanity.get("NR4A3", {}).get("status"),
        },
    }
    json.dump(out, open(os.path.join(OUTDIR, "panel-dependency.json"), "w"), indent=2)

    lines = ["# Validation-panel genetic dependency (DepMap, CI)", "", out["_note"], "",
             f"Release {release}; {n_lines} lines ({out['n_sarcoma_lines']} sarcoma).", "",
             "| target | group | mean GE | %dep | status | sel(sar-rest) |", "|---|---|---|---|---|---|"]
    for grp, rows in groups.items():
        for r in rows:
            if r.get("status") == "not_in_depmap":
                lines.append(f"| {r['gene']} | {grp} | - | - | not_in_depmap | - |")
            else:
                lines.append(f"| {r['gene']} | {grp} | {r['mean_gene_effect']} | {r['frac_dependent']} "
                             f"| {r['status']} | {r['selectivity_sarcoma_vs_rest']} |")
    lines += ["", f"Self-validation: POLR2A={out['self_validation']['POLR2A_should_be_pan_essential']}, "
              f"NR4A3={out['self_validation']['NR4A3_should_be_non_essential']}, "
              f"BRD9 synovial={out['self_validation']['BRD9_synovial_selective']}."]
    open(os.path.join(OUTDIR, "panel-dependency.md"), "w").write("\n".join(lines) + "\n")
    print("wrote panel-dependency.json/.md", file=sys.stderr)


if __name__ == "__main__":
    main()
