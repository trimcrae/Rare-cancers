#!/usr/bin/env python3
"""
In-silico target-expression mining for EMC candidates (public DepMap data, no wet lab).

WHY. The treatment tracker's open gates (B7-H3/CD56/FAP surface targets; CTA-low TCR-T verdict;
degrader fusion-addiction) all hinge on EMC expression data we cannot generate in a wet lab. EMC
has no DepMap line, so we use the **sarcoma lineages that ARE in DepMap as a surrogate** and mine
expression of every candidate target. This is the "public-data expression mining" arm of the
in-silico work program (emc-treatment-strategy.md).

WHAT. For each candidate gene, report expression (DepMap OmicsExpression, log2(TPM+1)) across
sarcoma vs all other lineages, the fraction of sarcoma lines expressing it, and a per-fusion-
sarcoma-subtype breakdown (Ewing/synovial/...) for context. EMC is closest to the
fusion/translocation sarcomas.

SELF-VALIDATION. Housekeeping genes (ACTB/GAPDH) must read high everywhere; and the cancer-testis
antigens (CTAG1B/MAGEA4) must read high in synovial sarcoma (the afami-cel/letetresgene context) —
recovering that both validates the pipeline and gives the contrast that frames EMC's CTA-low
expectation. If those don't hold, distrust the rest.

A SURROGATE PRIOR, not EMC data — flagged throughout. Internet required -> runs in CI.
Output: depmap-target-expression.json (+ .png).
"""

import io
import json
import os
import sys

import depmap_sarcoma_dependency as dep  # reuse figshare _get / _article_files / KNOWN_RELEASES

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "depmap-target-expression.json")
CHART = os.path.join(HERE, "depmap-target-expression.png")

EXPR_FILE = "OmicsExpressionProteinCodingGenesTPMLogp1.csv"

GENE_GROUPS = {
    "surface targets (ADC/CAR/bispecific)": ["CD276", "NCAM1", "FAP", "ERBB2", "L1CAM", "MCAM", "EGFR"],
    "cancer-testis antigens (TCR-T/ImmTAC)": ["MAGEA4", "CTAG1B", "PRAME", "MAGEA1", "MAGEA3"],
    "downstream effector": ["PPARG"],
    "drivers / fusion partners": ["NR4A3", "EWSR1", "FLI1", "TAF15"],
    "housekeeping (sanity control)": ["ACTB", "GAPDH"],
}
ALL_GENES = sorted({g for v in GENE_GROUPS.values() for g in v})
DETECT = 1.0   # log2(TPM+1) >= 1  -> TPM>=1, detectable
EXPRESSED = 3.0  # log2(TPM+1) >= 3 -> TPM~7, clearly expressed


def discover_files(want):
    """Resolve download URLs for `want` filenames from a known DepMap release."""
    for label, aid in dep.KNOWN_RELEASES:
        by_name = {f["name"]: f["download_url"] for f in dep._article_files(aid)}
        have = set(want) & set(by_name)
        print(f"  DepMap {label} ({aid}): exposes {sorted(have)}", file=sys.stderr)
        if set(want) <= set(by_name):
            return {"release": label, **{n: by_name[n] for n in want}}
    raise RuntimeError(f"no DepMap release exposes all of {want}")


def main():
    try:
        import pandas as pd
    except ImportError:
        json.dump({"_status": "pandas missing"}, open(OUT, "w"), indent=2)
        return

    urls = discover_files({EXPR_FILE, "Model.csv"})
    release = urls["release"]

    model = pd.read_csv(io.BytesIO(dep._get(urls["Model.csv"], timeout=180)))
    id_col = "ModelID" if "ModelID" in model.columns else model.columns[0]
    lin_col = "OncotreeLineage" if "OncotreeLineage" in model.columns else "lineage"
    sub_col = "OncotreeSubtype" if "OncotreeSubtype" in model.columns else None
    model = model.set_index(id_col)
    sarcoma_ids = set(model.index[model[lin_col].isin(["Soft Tissue", "Bone"])])
    print(f"  {len(model)} models, {len(sarcoma_ids)} sarcoma", file=sys.stderr)

    expr_path = dep._download(urls[EXPR_FILE], timeout=900)
    cols = list(pd.read_csv(expr_path, nrows=0).columns)
    idx_col = cols[0]
    keep = {c.split(" (")[0]: c for c in cols[1:] if c.split(" (")[0] in set(ALL_GENES)}
    ex = pd.read_csv(expr_path, usecols=[idx_col] + list(keep.values()), index_col=0)
    ex.columns = [c.split(" (")[0] for c in ex.columns]
    print(f"  expression: {ex.shape[0]} lines x {ex.shape[1]} genes "
          f"(found {sorted(ex.columns)})", file=sys.stderr)

    sar = ex[ex.index.isin(sarcoma_ids)]
    rest = ex[~ex.index.isin(sarcoma_ids)]

    def stats(gene):
        if gene not in ex.columns:
            return None
        s, r = sar[gene].dropna(), rest[gene].dropna()
        if len(s) == 0:
            return None
        return {
            "gene": gene,
            "sarcoma_mean_log2tpm": round(float(s.mean()), 2),
            "rest_mean_log2tpm": round(float(r.mean()), 2) if len(r) else None,
            "sarcoma_frac_detectable": round(float((s >= DETECT).mean()), 2),
            "sarcoma_frac_expressed": round(float((s >= EXPRESSED).mean()), 2),
            "n_sarcoma": int(len(s)),
        }

    groups_out = {grp: [x for g in gl if (x := stats(g))] for grp, gl in GENE_GROUPS.items()}

    def by_subtype(gene, predicate):
        if gene not in ex.columns or not sub_col:
            return None
        ids = set(model.index[model[sub_col].astype(str).str.contains(predicate, case=False, na=False)])
        vals = ex[gene].reindex([i for i in ex.index if i in ids]).dropna()
        if len(vals) == 0:
            return None
        return {"n": int(len(vals)), "mean_log2tpm": round(float(vals.mean()), 2),
                "frac_expressed": round(float((vals >= EXPRESSED).mean()), 2)}

    subtypes = ["ewing", "synovial", "myxoid", "alveolar", "rhabdo", "lipo"]
    surface_and_cta = GENE_GROUPS["surface targets (ADC/CAR/bispecific)"] + \
        GENE_GROUPS["cancer-testis antigens (TCR-T/ImmTAC)"]
    subtype_table = {g: {st: by_subtype(g, st) for st in subtypes}
                     for g in surface_and_cta if g in ex.columns}

    validation = {
        "ACTB_should_be_high": stats("ACTB"),
        "GAPDH_should_be_high": stats("GAPDH"),
        "CTAG1B_in_synovial_should_be_high": by_subtype("CTAG1B", "synovial"),
        "MAGEA4_in_synovial_should_be_high": by_subtype("MAGEA4", "synovial"),
        "_pass": "housekeeping high everywhere; CTAs high in synovial -> pipeline trustworthy",
    }

    result = {
        "_note": "In-silico expression mining (DepMap OmicsExpression, log2(TPM+1)) of EMC "
                 "treatment-candidate targets across SARCOMA lines as an EMC surrogate (EMC has no "
                 "DepMap line). detectable=log2tpm>=1; expressed>=3. A SURROGATE PRIOR, not EMC "
                 "data. Closes the surface-target/CTA expression gate in-silico per "
                 "emc-treatment-strategy.md.",
        "data_source": f"DepMap {release} {EXPR_FILE} + Model.csv",
        "n_sarcoma_lines": len(sarcoma_ids),
        "thresholds": {"detectable_log2tpm": DETECT, "expressed_log2tpm": EXPRESSED},
        "genes_by_group": groups_out,
        "surface_and_cta_by_subtype": subtype_table,
        "self_validation": validation,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({"self_validation": validation,
                      "CD276": stats("CD276"), "NCAM1": stats("NCAM1"),
                      "FAP": stats("FAP"), "PPARG": stats("PPARG")}, indent=2))
    render_chart(result)


def render_chart(result):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    rows = [x for grp, gl in result["genes_by_group"].items() for x in gl
            if grp != "housekeeping (sanity control)"]
    if not rows:
        return
    rows.sort(key=lambda r: r["sarcoma_mean_log2tpm"], reverse=True)
    genes = [r["gene"] for r in rows]
    y = range(len(genes))
    fig, ax = plt.subplots(figsize=(8, max(4, 0.4 * len(genes))))
    ax.barh(list(y), [r["sarcoma_mean_log2tpm"] for r in rows], color="#2c7fb8")
    ax.axvline(EXPRESSED, ls="--", c="gray", lw=1, label="expressed (log2tpm=3)")
    ax.axvline(DETECT, ls=":", c="gray", lw=1, label="detectable (=1)")
    ax.set_yticks(list(y))
    ax.set_yticklabels(genes)
    ax.invert_yaxis()
    ax.set_xlabel("Mean expression in sarcoma lines, log2(TPM+1)")
    ax.set_title("EMC candidate-target expression in DepMap sarcoma lines (EMC surrogate)")
    ax.legend(fontsize=8)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(CHART, dpi=130)
    print("wrote", CHART, file=sys.stderr)


if __name__ == "__main__":
    main()
