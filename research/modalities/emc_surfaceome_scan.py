#!/usr/bin/env python3
"""
EMC surfaceome discovery scan — find a candidate targeting antigen for oligo/cell-therapy delivery.

WHY. The fusion-junction ASO route's dominant gate is tumour DELIVERY (fusion-junction-aso-paper.md
§3c). The best systemic delivery vehicle is a receptor-targeted antibody-oligonucleotide conjugate
(AOC), but an AOC needs a TARGETING ARM: a surface antigen enriched on EMC cells. Today the only
antigen the paper can even name is B7-H3 (CD276), and that is an EXTRAPOLATION from other sarcomas
with NO EMC-specific evidence. This script does the one in-silico thing that advances delivery: an
UNBIASED scan of the whole surfaceome for antigens enriched in the EMC-surrogate sarcoma class, so a
delivery (and CAR-T/ADC) candidate can be NAMED from data rather than assumed.

This is distinct from depmap_target_expression.py, which checks a HAND-PICKED list of known targets.
Here we scan EVERY surface gene and let the enriched ones surface.

WHAT.
  1. Surfaceome gene set: fetch from UniProt REST — reviewed human proteins with a plasma-membrane
     subcellular location (SL-0039) AND a transmembrane (KW-0812) or GPI-anchor (KW-0336) topology,
     i.e. proteins that present an EXTRACELLULAR epitope an antibody/AOC/CAR can bind. Falls back to
     a curated seed list of clinically-actionable surface antigens if UniProt is unreachable, and
     always UNIONs the seed in so the actionable targets are scanned regardless.
  2. Expression: DepMap OmicsExpression (log2(TPM+1)) across sarcoma lines as an EMC surrogate (EMC
     has no DepMap line). For each surface gene, compute expression in the EMC-surrogate
     TRANSLOCATION-sarcoma class (Ewing/synovial/myxoid/alveolar/DSRCT/clear-cell — EMC is
     myxoid/translocation class), the myxoid subset specifically (closest to EMC), and the "rest of
     lineages" as a crude off-target proxy; then rank by class expression + selectivity.

SELF-VALIDATION. Housekeeping genes (ACTB/GAPDH) must be ABSENT from the surfaceome set (they are not
surface) — if they leak in, the surface filter is broken. Known surface markers (CD276) must read
high and broad, recovering depmap_target_expression's prior. If these don't hold, distrust the rest.

HONEST BOUNDS (stated in the output too).
  - SURROGATE, not EMC: sarcoma DepMap lines, not EMC. EMC has no line.
  - "rest" = other CANCER lineages, NOT normal tissue. An AOC's real safety window is tumour-vs-
    NORMAL (GTEx/HPA); that normal-tissue check on the top hits is the flagged next step, not done here.
  - Cell-line surface mRNA != primary-tumour surface PROTEIN density. mRNA is a lower bound / proxy.
  - This NAMES an antigen candidate. It does NOT solve delivery efficiency (blood->tumour->cell->
    endosomal escape) and does not confirm EMC surface expression — that needs EMC tissue IHC/proteomics.

Internet required (UniProt + figshare/DepMap) -> runs in CI, published to modalities-cache.
Output: emc-surfaceome-scan.json (+ .png)
"""

import io
import json
import os
import sys
import urllib.parse
import urllib.request

import depmap_sarcoma_dependency as dep  # reuse _get / _download / _article_files / KNOWN_RELEASES

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "emc-surfaceome-scan.json")
CHART = os.path.join(HERE, "emc-surfaceome-scan.png")

EXPR_FILE = "OmicsExpressionProteinCodingGenesTPMLogp1.csv"
DETECT = 1.0     # log2(TPM+1) >= 1  -> TPM>=1, detectable
EXPRESSED = 3.0  # log2(TPM+1) >= 3  -> TPM~7, clearly expressed

# EMC is a myxoid / translocation-driven sarcoma. These OncotreeSubtype substrings define the
# EMC-SURROGATE class (fusion/translocation sarcomas) and the myxoid subset closest to EMC.
TRANSLOCATION_SUBTYPES = ["ewing", "synovial", "myxoid", "alveolar", "desmoplastic small round",
                          "clear cell sarcoma", "extraskeletal"]
MYXOID_SUBTYPES = ["myxoid", "extraskeletal"]

# Curated seed of clinically-actionable / well-known surface antigens (ADC/CAR/bispecific space),
# always UNIONed into the scan so the actionable targets are covered even if the UniProt
# surfaceome fetch fails or misses one. (CD276 = B7-H3, NCAM1 = CD56, TNFRSF8 = CD30.)
SEED_SURFACE = ["CD276", "NCAM1", "FAP", "ERBB2", "ERBB3", "EGFR", "MET", "L1CAM", "MCAM",
                "ALCAM", "CD248", "CDH2", "CDH11", "PTK7", "ROR1", "ROR2", "EPHA2", "EPHB4",
                "FGFR1", "FGFR4", "IGF1R", "PDGFRA", "PDGFRB", "KIT", "AXL", "CD44", "CD70",
                "TNFRSF8", "MSLN", "GPC3", "GPC2", "ALK", "DLL3", "NECTIN4", "TACSTD2", "FOLR1",
                "MUC1", "CEACAM5", "STEAP1", "PVR", "ITGAV", "ITGB1", "SLC34A2", "CLDN6",
                "LRRC15", "CD200", "ENPP1"]

UNIPROT = "https://rest.uniprot.org/uniprotkb/search"
# reviewed human, plasma-membrane location (SL-0039), presenting an extracellular epitope
# (transmembrane KW-0812 OR GPI-anchor KW-0336).
UNIPROT_QUERY = ("(organism_id:9606) AND (reviewed:true) AND (cc_scl_term:SL-0039) "
                 "AND (keyword:KW-0812 OR keyword:KW-0336)")


def fetch_surfaceome():
    """Return (gene_set, provenance). UniProt REST, cursor-paginated TSV; seed union always applied."""
    genes = set()
    prov = {"source": "UniProt REST (SL-0039 plasma membrane + KW-0812/KW-0336 TM/GPI)",
            "query": UNIPROT_QUERY, "status": "ok"}
    try:
        url = (UNIPROT + "?" + urllib.parse.urlencode(
            {"query": UNIPROT_QUERY, "fields": "gene_primary", "format": "tsv", "size": "500"}))
        pages = 0
        while url and pages < 40:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                text = r.read().decode("utf-8", "replace")
                link = r.headers.get("Link", "")
            lines = text.splitlines()
            for ln in lines[1:]:  # skip header
                g = ln.strip().split("\t")[0].strip()
                # gene_primary can be blank or contain multiple names; take the first token
                if g:
                    genes.add(g.split()[0])
            nxt = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    nxt = part[part.find("<") + 1:part.find(">")]
            url = nxt
            pages += 1
        prov["n_pages"] = pages
    except Exception as e:  # noqa: BLE001
        prov["status"] = f"uniprot_failed: {e}"
    prov["n_from_uniprot"] = len(genes)
    genes |= set(SEED_SURFACE)
    prov["n_seed_unioned"] = len(SEED_SURFACE)
    prov["n_total"] = len(genes)
    # If UniProt gave us implausibly few, say so loudly (the scan degrades to ~seed only).
    if len(genes) < 800:
        prov["WARNING"] = ("surfaceome smaller than expected (~2000-5000 expected); UniProt fetch "
                           "likely degraded — results are effectively the curated seed only.")
    return genes, prov


def main():
    try:
        import pandas as pd
    except ImportError:
        json.dump({"_status": "pandas missing"}, open(OUT, "w"), indent=2)
        return

    surface_genes, surf_prov = fetch_surfaceome()
    print(f"  surfaceome: {len(surface_genes)} genes ({surf_prov['status']})", file=sys.stderr)

    urls = dep_discover({EXPR_FILE, "Model.csv"})
    release = urls["release"]
    model = pd.read_csv(io.BytesIO(dep._get(urls["Model.csv"], timeout=180)))
    id_col = "ModelID" if "ModelID" in model.columns else model.columns[0]
    lin_col = "OncotreeLineage" if "OncotreeLineage" in model.columns else "lineage"
    sub_col = "OncotreeSubtype" if "OncotreeSubtype" in model.columns else None
    model = model.set_index(id_col)
    sarcoma_ids = set(model.index[model[lin_col].isin(["Soft Tissue", "Bone"])])

    def subtype_ids(subs):
        if not sub_col:
            return set()
        s = model[sub_col].astype(str).str.lower()
        keep = set()
        for pat in subs:
            keep |= set(model.index[s.str.contains(pat, na=False)])
        return keep

    class_ids = subtype_ids(TRANSLOCATION_SUBTYPES)   # EMC-surrogate translocation-sarcoma class
    myxoid_ids = subtype_ids(MYXOID_SUBTYPES)
    print(f"  {len(model)} models | {len(sarcoma_ids)} sarcoma | "
          f"{len(class_ids)} translocation-class | {len(myxoid_ids)} myxoid", file=sys.stderr)

    # Read only the surfaceome columns from the big expression matrix.
    expr_path = dep._download(urls[EXPR_FILE], timeout=1200)
    cols = list(pd.read_csv(expr_path, nrows=0).columns)
    idx_col = cols[0]
    keep = {c.split(" (")[0]: c for c in cols[1:] if c.split(" (")[0] in surface_genes}
    print(f"  surfaceome genes present in expression matrix: {len(keep)}", file=sys.stderr)
    ex = pd.read_csv(expr_path, usecols=[idx_col] + list(keep.values()), index_col=0)
    ex.columns = [c.split(" (")[0] for c in ex.columns]

    class_ex = ex[ex.index.isin(class_ids)]
    myx_ex = ex[ex.index.isin(myxoid_ids)]
    rest_ex = ex[~ex.index.isin(sarcoma_ids)]   # non-sarcoma cancer lines = crude off-target proxy

    def stat(gene):
        c = class_ex[gene].dropna() if gene in class_ex else None
        if c is None or len(c) == 0:
            return None
        r = rest_ex[gene].dropna() if gene in rest_ex else None
        m = myx_ex[gene].dropna() if gene in myx_ex else None
        class_mean = float(c.mean())
        rest_mean = float(r.mean()) if r is not None and len(r) else None
        return {
            "gene": gene,
            "class_mean_log2tpm": round(class_mean, 2),
            "class_frac_expressed": round(float((c >= EXPRESSED).mean()), 2),
            "class_frac_detectable": round(float((c >= DETECT).mean()), 2),
            "n_class": int(len(c)),
            "myxoid_mean_log2tpm": round(float(m.mean()), 2) if m is not None and len(m) else None,
            "n_myxoid": int(len(m)) if m is not None else 0,
            "rest_mean_log2tpm": round(rest_mean, 2) if rest_mean is not None else None,
            "rest_frac_expressed": (round(float((r >= EXPRESSED).mean()), 2)
                                    if r is not None and len(r) else None),
            # selectivity vs other cancer lineages (NOT normal tissue — see caveats)
            "enrichment_vs_rest": (round(class_mean - rest_mean, 2)
                                   if rest_mean is not None else None),
        }

    rows = [s for g in sorted(keep) if (s := stat(g))]
    # Rank: expressed across most surrogate lines first, then selective, then high.
    def score(s):
        enr = s["enrichment_vs_rest"] if s["enrichment_vs_rest"] is not None else 0.0
        return (s["class_frac_expressed"], enr, s["class_mean_log2tpm"])
    rows.sort(key=score, reverse=True)

    # actionable-antigen callout: where the known ADC/CAR/bispecific targets landed
    actionable = {s["gene"]: s for s in rows if s["gene"] in set(SEED_SURFACE)}

    # self-validation
    hk_leak = [g for g in ("ACTB", "GAPDH") if g in keep]
    cd276 = next((s for s in rows if s["gene"] == "CD276"), None)
    validation = {
        "housekeeping_absent_from_surfaceome": (len(hk_leak) == 0),
        "housekeeping_leaked": hk_leak,
        "CD276_present_and_broad": bool(cd276 and cd276["class_frac_detectable"] >= 0.8),
        "CD276_stats": cd276,
        "_pass": ("surface filter excludes housekeeping AND CD276 recovers as broadly expressed "
                  "-> surfaceome + expression pipeline trustworthy"),
    }

    result = {
        "_note": ("UNBIASED surfaceome scan for an EMC delivery/CAR/ADC targeting antigen. Surface "
                  "genes (UniProt plasma-membrane + TM/GPI) ranked by expression in the EMC-surrogate "
                  "TRANSLOCATION-sarcoma DepMap class (EMC has no line). NAMES a candidate antigen; "
                  "does NOT confirm EMC surface expression or solve delivery efficiency."),
        "_caveats": [
            "SURROGATE: DepMap sarcoma lines, not EMC (no EMC line exists).",
            "'rest' = other CANCER lineages, NOT normal tissue; an AOC's real safety window is "
            "tumour-vs-NORMAL (GTEx/HPA) — the flagged next step, not done here.",
            "cell-line surface mRNA != primary-tumour surface PROTEIN density (mRNA is a proxy).",
            "expression enrichment != validated tumour-selective antigen; needs EMC tissue IHC.",
            "this advances the TARGETING ARM only; blood->tumour->cell->endosomal-escape delivery "
            "efficiency remains wet-lab and unsolved.",
        ],
        "data_source": f"DepMap {release} {EXPR_FILE} + Model.csv",
        "surfaceome_source": surf_prov,
        "class_definition": {"translocation_sarcoma_subtypes": TRANSLOCATION_SUBTYPES,
                             "myxoid_subtypes": MYXOID_SUBTYPES,
                             "n_class_lines": len(class_ids), "n_myxoid_lines": len(myxoid_ids),
                             "n_sarcoma_lines": len(sarcoma_ids)},
        "thresholds": {"detectable_log2tpm": DETECT, "expressed_log2tpm": EXPRESSED},
        "n_surface_genes_scanned": len(keep),
        "top_candidates": rows[:40],
        "actionable_antigens": actionable,
        "self_validation": validation,
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({"self_validation": {k: validation[k] for k in
                      ("housekeeping_absent_from_surfaceome", "CD276_present_and_broad")},
                      "n_surface_genes_scanned": len(keep),
                      "top10": [r["gene"] for r in rows[:10]]}, indent=2))
    render_chart(result)


def dep_discover(want):
    """Resolve DepMap download URLs for `want` filenames (mirror of depmap_target_expression)."""
    for label, aid in dep.KNOWN_RELEASES:
        by_name = {f["name"]: f["download_url"] for f in dep._article_files(aid)}
        if set(want) <= set(by_name):
            print(f"  DepMap {label} ({aid}) exposes all of {sorted(want)}", file=sys.stderr)
            return {"release": label, **{n: by_name[n] for n in want}}
    raise RuntimeError(f"no DepMap release exposes all of {want}")


def render_chart(result):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    rows = result["top_candidates"][:20]
    if not rows:
        return
    genes = [r["gene"] for r in rows]
    y = range(len(genes))
    fig, ax = plt.subplots(figsize=(8, max(4, 0.4 * len(genes))))
    ax.barh(list(y), [r["class_mean_log2tpm"] for r in rows], color="#2c7fb8",
            label="translocation-sarcoma class mean")
    ax.barh(list(y), [r["rest_mean_log2tpm"] or 0 for r in rows], color="#d95f0e",
            alpha=0.5, label="rest-of-lineages mean")
    ax.axvline(EXPRESSED, ls="--", c="gray", lw=1)
    ax.set_yticks(list(y))
    ax.set_yticklabels(genes)
    ax.invert_yaxis()
    ax.set_xlabel("Expression, log2(TPM+1)")
    ax.set_title("EMC-surrogate surfaceome scan — top surface antigens (class vs rest)")
    ax.legend(fontsize=8)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(CHART, dpi=130)
    print("wrote", CHART, file=sys.stderr)


if __name__ == "__main__":
    main()
