#!/usr/bin/env python3
"""
DepMap transfer prior: is the chromatin / transcriptional machinery that the EWSR1 prion-like
domain recruits SELECTIVELY essential in sarcomas?

WHY. EMC has no cell line in DepMap, so its dependencies cannot be mined directly. But the
synthetic-lethal hypothesis (degrader-vs-synthetic-lethal.md) is that EWSR1::NR4A3, through the
*same* EWSR1 prion-like domain that retargets BAF in EWS-FLI1 [Boulay 2017], creates a
chromatin-remodeling dependency — sharpest at ncBAF/BRD9, which already has clinical-stage
degraders. This script tests whether that machinery is *selectively* essential across the
sarcoma lineages that ARE in DepMap (Ewing, synovial, etc.), as a transfer prior for EMC.

SELF-VALIDATION (the honesty check). If the method is sound it must recover two textbook
dependencies: BRD9 selectively essential in synovial sarcoma, and SMARCB1 selectively essential
in rhabdoid tumour. We compute and print those explicitly; if they don't fall out, distrust the
rest.

DATA (public DepMap CRISPR Chronos gene effect + model metadata), discovered via the figshare
API so no per-release file IDs are hard-coded. Gene effect: more negative = more essential
(~ -1 is the median common-essential gene; < -0.5 we call "dependent").

Output: depmap-sarcoma-dependency.json (+ .png chart). Internet required -> runs in CI.
"""

import io
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "depmap-sarcoma-dependency.json")
CHART = os.path.join(HERE, "depmap-sarcoma-dependency.png")

# Genes the EWSR1-prion / fusion-transactivation hypothesis implicates, grouped.
GENE_GROUPS = {
    "ncBAF (primary hypothesis)": ["BRD9", "BICRA", "BICRAL"],
    "BAF / SWI-SNF core": ["SMARCA4", "SMARCA2", "SMARCB1", "ARID1A", "ARID1B", "SMARCC1", "PBRM1"],
    "BET / transcriptional": ["BRD4", "BRD2", "BRD3", "CDK9", "CDK7", "EP300", "CREBBP"],
}
ALL_GENES = sorted({g for v in GENE_GROUPS.values() for g in v})
# context genes for sanity (a pan-essential and the fusion gene itself)
CONTEXT_GENES = ["POLR2A", "NR4A3", "EWSR1", "FLI1"]
DEPENDENT_THRESHOLD = -0.5

# Known DepMap public-release figshare article IDs (newest first). Gene essentiality is stable
# across releases, so an older but reliably-hosted release is an acceptable transfer prior.
# 24Q4 is on Figshare+ (plus.figshare.com); 23Q2 (22765112) is on regular figshare and is the
# confirmed reliable anchor — both expose CRISPRGeneEffect.csv + Model.csv.
KNOWN_RELEASES = [("24Q4", 27993248), ("24Q4-alt", 27993966), ("23Q2", 22765112)]
WANT_FILES = {"CRISPRGeneEffect.csv", "Model.csv"}


def _get(url, timeout=120, data=None, headers=None):
    h = {"User-Agent": "rare-cancers/1.0", "Accept": "application/json"}
    if headers:
        h.update(headers)
    for i in range(4):
        try:
            req = urllib.request.Request(url, data=data, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa
            print(f"  retry {i+1} {url[:80]}: {e}", file=sys.stderr)
            import time
            time.sleep(2 ** i)
    raise RuntimeError(f"failed: {url}")


def _article_files(aid):
    try:
        return json.loads(_get(f"https://api.figshare.com/v2/articles/{aid}")).get("files", [])
    except Exception as e:  # noqa
        print(f"  article {aid}: {e}", file=sys.stderr)
        return []


def discover_depmap_files():
    """Resolve CRISPRGeneEffect.csv + Model.csv download URLs from a known DepMap release."""
    for label, aid in KNOWN_RELEASES:
        by_name = {f["name"]: f["download_url"] for f in _article_files(aid)}
        have = WANT_FILES & set(by_name)
        print(f"  DepMap {label} (figshare {aid}): exposes {sorted(have)}", file=sys.stderr)
        if WANT_FILES <= set(by_name):
            print(f"  using DepMap {label} (figshare {aid})", file=sys.stderr)
            return {"release": label, **{n: by_name[n] for n in WANT_FILES}}
    # fallback: search the regular figshare repo by the distinctive filename token
    try:
        arts = json.loads(_get("https://api.figshare.com/v2/articles?search_for=CRISPRGeneEffect"
                               "&page_size=20&order=published_date&order_direction=desc"))
        for art in arts:
            by_name = {f["name"]: f["download_url"] for f in _article_files(art["id"])}
            if WANT_FILES <= set(by_name):
                print(f"  using searched article {art['id']}", file=sys.stderr)
                return {"release": f"searched:{art['id']}", **{n: by_name[n] for n in WANT_FILES}}
    except Exception as e:  # noqa
        print(f"  search fallback failed: {e}", file=sys.stderr)
    raise RuntimeError("no DepMap article exposes both CRISPRGeneEffect.csv and Model.csv")


def main():
    try:
        import pandas as pd
    except ImportError:
        print("  pandas missing", file=sys.stderr)
        json.dump({"_status": "pandas missing"}, open(OUT, "w"), indent=2)
        return

    urls = discover_depmap_files()
    release = urls.get("release", "unknown")

    # Model metadata (small)
    model = pd.read_csv(io.BytesIO(_get(urls["Model.csv"], timeout=180)))
    id_col = "ModelID" if "ModelID" in model.columns else model.columns[0]
    lin_col = "OncotreeLineage" if "OncotreeLineage" in model.columns else "lineage"
    dis_col = "OncotreePrimaryDisease" if "OncotreePrimaryDisease" in model.columns else None
    sub_col = "OncotreeSubtype" if "OncotreeSubtype" in model.columns else None
    model = model.set_index(id_col)
    is_sarcoma = model[lin_col].isin(["Soft Tissue", "Bone"])
    sarcoma_ids = set(model.index[is_sarcoma])
    print(f"  {len(model)} models, {len(sarcoma_ids)} sarcoma (Soft Tissue/Bone)", file=sys.stderr)

    # CRISPR gene effect — read header, keep only target columns (memory-safe)
    raw = _get(urls["CRISPRGeneEffect.csv"], timeout=600)
    header = pd.read_csv(io.BytesIO(raw), nrows=0)
    cols = list(header.columns)
    idx_col = cols[0]
    want = set(ALL_GENES) | set(CONTEXT_GENES)
    keep = {c.split(" (")[0]: c for c in cols[1:] if c.split(" (")[0] in want}
    ge = pd.read_csv(io.BytesIO(raw), usecols=[idx_col] + list(keep.values()), index_col=0)
    ge.columns = [c.split(" (")[0] for c in ge.columns]
    print(f"  gene-effect: {ge.shape[0]} lines x {ge.shape[1]} target genes "
          f"(found {sorted(ge.columns)})", file=sys.stderr)

    sar = ge[ge.index.isin(sarcoma_ids)]
    rest = ge[~ge.index.isin(sarcoma_ids)]

    def stats(gene):
        if gene not in ge.columns:
            return None
        s, r = sar[gene].dropna(), rest[gene].dropna()
        if len(s) == 0 or len(r) == 0:
            return None
        return {
            "gene": gene,
            "sarcoma_mean": round(float(s.mean()), 3),
            "rest_mean": round(float(r.mean()), 3),
            "selectivity": round(float(r.mean() - s.mean()), 3),  # >0 = more essential in sarcoma
            "sarcoma_frac_dependent": round(float((s < DEPENDENT_THRESHOLD).mean()), 3),
            "rest_frac_dependent": round(float((r < DEPENDENT_THRESHOLD).mean()), 3),
            "n_sarcoma": int(len(s)),
        }

    genes_out = {grp: [x for g in gl if (x := stats(g))] for grp, gl in GENE_GROUPS.items()}
    context_out = [x for g in CONTEXT_GENES if (x := stats(g))]

    # --- self-validation on known selective dependencies -----------------------------------
    def subtype_mean(gene, predicate):
        if gene not in ge.columns or not (sub_col or dis_col):
            return None
        col = sub_col or dis_col
        ids = set(model.index[model[col].astype(str).str.contains(predicate, case=False, na=False)])
        vals = ge[gene].reindex([i for i in ge.index if i in ids]).dropna()
        if len(vals) == 0:
            return None
        return {"subtype_match": predicate, "n": int(len(vals)),
                "mean_gene_effect": round(float(vals.mean()), 3),
                "frac_dependent": round(float((vals < DEPENDENT_THRESHOLD).mean()), 3)}

    validation = {
        "BRD9_in_synovial": subtype_mean("BRD9", "synovial"),
        "SMARCB1_in_rhabdoid": subtype_mean("SMARCB1", "rhabdoid"),
        "_pass_criterion": "each should show clearly more-negative mean_gene_effect / high "
                           "frac_dependent vs the gene's rest_mean above",
    }

    # closest analogues to EMC: FET-fusion / translocation sarcomas
    analogues = {name: subtype_mean("BRD9", pat) for name, pat in
                 {"Ewing": "ewing", "Synovial": "synovial",
                  "Myxoid_liposarcoma": "myxoid", "Alveolar_RMS": "alveolar"}.items()}

    result = {
        "_note": "DepMap CRISPR (Chronos) selective-essentiality transfer prior for EWSR1::NR4A3 "
                 "EMC, which has no DepMap line. Gene effect: more negative = more essential; "
                 "< -0.5 = dependent; selectivity = rest_mean - sarcoma_mean (>0 = sarcoma-"
                 "selective). A PRIOR from related sarcomas, NOT EMC data. See "
                 "degrader-vs-synthetic-lethal.md.",
        "data_source": f"DepMap public release {release} (figshare) CRISPRGeneEffect.csv + Model.csv",
        "n_models_total": int(len(model)),
        "n_sarcoma_models": len(sarcoma_ids),
        "dependent_threshold": DEPENDENT_THRESHOLD,
        "genes_by_group": genes_out,
        "context_genes": context_out,
        "self_validation": validation,
        "BRD9_by_fusion_sarcoma_subtype": analogues,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    # concise summary to stdout
    print(json.dumps({
        "n_sarcoma_models": len(sarcoma_ids),
        "BRD9": stats("BRD9"), "BICRA": stats("BICRA"),
        "self_validation": validation,
    }, indent=2))
    render_chart(result)


def render_chart(result):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib absent; skipping chart", file=sys.stderr)
        return
    rows = [x for grp in result["genes_by_group"].values() for x in grp]
    if not rows:
        return
    rows.sort(key=lambda r: r["selectivity"], reverse=True)
    genes = [r["gene"] for r in rows]
    y = range(len(genes))
    fig, ax = plt.subplots(figsize=(8, max(4, 0.45 * len(genes))))
    ax.barh(list(y), [r["sarcoma_mean"] for r in rows], height=0.38, label="Sarcoma", color="#c0392b")
    ax.barh([i + 0.4 for i in y], [r["rest_mean"] for r in rows], height=0.38,
            label="All other lineages", color="#7f8c8d")
    ax.axvline(DEPENDENT_THRESHOLD, ls="--", c="gray", lw=1)
    ax.set_yticks([i + 0.2 for i in y])
    ax.set_yticklabels(genes)
    ax.invert_yaxis()
    ax.set_xlabel("Mean CRISPR gene effect (more negative = more essential)")
    ax.set_title("Chromatin/transcriptional dependency in sarcoma vs other lineages (DepMap)\n"
                 "EWSR1::NR4A3 EMC transfer prior — sorted by sarcoma-selectivity")
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(CHART, dpi=130)
    print("wrote", CHART, file=sys.stderr)


if __name__ == "__main__":
    main()
