#!/usr/bin/env python3
"""
EMC Open Target & Drug Atlas — public expression reprocessing (GSE4303, GSE24369).

WHY. The atlas needs a reproduced, provenance-clean EMC expression signature (strategy Project 1,
step C). The dev sandbox blocks NCBI/GEO at the egress proxy, so this runs in GitHub Actions
(unrestricted internet). Pure stdlib (urllib) — no pip, no R.

WHAT it does, per dataset, PER PLATFORM (never merges platforms — strategy rule):
  1. Download the series matrix (author-normalized) + the GPL probe->symbol annotation.
  2. QC: platform type (two-colour log-ratio vs single-channel intensity, detected from the
     fraction of negative values), sample count, missing fraction.
  3. Label samples EMC vs non-EMC from !Sample_title / !Sample_characteristics (best-effort, and
     reported so a human can audit the labels).
  4. Rank-based EMC-vs-rest signature (AUC = P(EMC ranks above non-EMC) per gene) WHERE non-EMC
     comparators exist. Rank-based by design so it is robust to normalization/platform differences
     (strategy: "rank-based meta-analysis, never naive matrix merge").
  5. Reproduction check: where do KNOWN EMC markers (NMB, PPARG, CHRNA6, INSM1, NR4A3, ...) land?
     (A success criterion: the reprocessing should recover known EMC biology.)
  6. EWSR1-vs-TAF15 stratification IF metadata permit (usually they do NOT in these legacy sets —
     reported honestly, not forced).
  7. Leave-one-EMC-sample-out stability of the top-N signature (Jaccard) — the sample counts are
     tiny, so stability is a first-class output.

HONEST BOUNDS. Author-normalized series matrices (not raw-CEL RMA — a documented future upgrade
needing R/Bioconductor). Tiny n. Legacy arrays with limited gene coverage. Tumor tissue => myxoid
stroma dilutes tumor-cell reads. A gene absent from an array is "not measured", not "not expressed".

Output: research/atlas/_generated/emc-expression-reprocess.json (+ .md summary).
"""
import gzip
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "_generated")
os.makedirs(OUTDIR, exist_ok=True)

DATASETS = ["GSE4303", "GSE24369"]

# Known EMC-associated genes to look for as a reproduction check (up in EMC / lineage markers).
KNOWN_MARKERS = ["NR4A3", "NMB", "NMBR", "PPARG", "PPARGC1A", "CHRNA6", "INSM1", "SYP",
                 "NDRG2", "RET", "FOLR1", "S100B", "SOX9", "MUC4"]


def _get(url, timeout=240):
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-atlas/1.0"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa
            print(f"  retry {i+1} {url[:80]}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"failed: {url}")


def series_group(gse):
    n = re.sub(r"\D", "", gse)
    return f"GSE{n[:-3]}nnn" if len(n) > 3 else "GSEnnn"


def list_matrix_files(gse):
    grp = series_group(gse)
    base = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{grp}/{gse}/matrix/"
    html = _get(base).decode("utf-8", "replace")
    files = sorted(set(re.findall(r'href="([^"]*_series_matrix\.txt\.gz)"', html)))
    # hrefs may be relative; normalize to just the filename
    files = [f.split("/")[-1] for f in files]
    return base, files


def parse_series_matrix(raw):
    """Return dict: platform, samples, titles, characteristics(list per sample joined), probes, values."""
    text = gzip.decompress(raw).decode("utf-8", "replace")
    platform, samples, titles = None, [], []
    charac = {}  # sample_index -> list of characteristic strings
    probes, values, header = [], [], None
    in_tbl = False
    for ln in text.splitlines():
        if ln.startswith("!Series_platform_id") and platform is None:
            platform = ln.split("\t")[-1].strip().strip('"')
        elif ln.startswith("!Sample_geo_accession"):
            samples = [x.strip().strip('"') for x in ln.split("\t")[1:]]
        elif ln.startswith("!Sample_title"):
            titles = [x.strip().strip('"') for x in ln.split("\t")[1:]]
        elif ln.startswith("!Sample_characteristics") or ln.startswith("!Sample_source_name"):
            vals = [x.strip().strip('"') for x in ln.split("\t")[1:]]
            for i, v in enumerate(vals):
                charac.setdefault(i, []).append(v)
        elif ln.startswith("!series_matrix_table_begin"):
            in_tbl = True
            continue
        elif ln.startswith("!series_matrix_table_end"):
            break
        elif in_tbl:
            parts = ln.split("\t")
            if header is None:
                header = [p.strip().strip('"') for p in parts]
                continue
            pid = parts[0].strip().strip('"')
            row = []
            for x in parts[1:]:
                x = x.strip().strip('"')
                try:
                    row.append(float(x))
                except ValueError:
                    row.append(None)
            probes.append(pid)
            values.append(row)
    charac_joined = {i: " | ".join(v) for i, v in charac.items()}
    return {"platform": platform, "samples": samples, "titles": titles,
            "characteristics": charac_joined, "probes": probes, "values": values}


def parse_gpl_symbols(platform_id):
    if not platform_id:
        return {}
    n = re.sub(r"\D", "", platform_id)
    grp = f"GPL{n[:-3]}nnn" if len(n) > 3 else "GPLnnn"
    url = f"https://ftp.ncbi.nlm.nih.gov/geo/platforms/{grp}/{platform_id}/soft/{platform_id}_family.soft.gz"
    try:
        text = gzip.decompress(_get(url, timeout=360)).decode("utf-8", "replace")
    except Exception as e:  # noqa
        print(f"  GPL soft fetch failed ({e})", file=sys.stderr)
        return {}
    mapping = {}
    in_tbl = False
    header, id_i, sym_i = None, None, None
    for ln in text.splitlines():
        if ln.startswith("!platform_table_begin"):
            in_tbl = True
            continue
        if ln.startswith("!platform_table_end"):
            break
        if in_tbl:
            parts = ln.split("\t")
            if header is None:
                header = [p.strip() for p in parts]
                low = [h.lower() for h in header]
                id_i = 0
                for cand in ("gene symbol", "gene_symbol", "symbol", "ilmn_gene", "genesymbol"):
                    if cand in low:
                        sym_i = low.index(cand)
                        break
                continue
            if sym_i is not None and len(parts) > sym_i:
                pid = parts[id_i].strip()
                sym = parts[sym_i].strip().split("///")[0].strip()
                if pid and sym:
                    mapping[pid] = sym
    return mapping


def label_emc(titles, characteristics, samples):
    """Best-effort EMC vs non-EMC labels + a fusion-partner guess where explicit."""
    labels, fusion = [], []
    for i, s in enumerate(samples):
        blob = f"{titles[i] if i < len(titles) else ''} {characteristics.get(i, '')}".lower()
        is_emc = bool(re.search(r"myxoid chondrosarcoma|extraskeletal myxoid|\bemc\b|ewsr1.?nr4a3|taf15.?nr4a3|nr4a3", blob))
        labels.append("EMC" if is_emc else "other")
        fp = None
        if "taf15" in blob:
            fp = "TAF15"
        elif "ewsr1" in blob or "ews" in blob:
            fp = "EWSR1"
        fusion.append(fp)
    return labels, fusion


def ranks(xs):
    """Average ranks of values (None -> excluded, given rank NaN)."""
    idx = [i for i, v in enumerate(xs) if v is not None]
    order = sorted(idx, key=lambda i: xs[i])
    r = [None] * len(xs)
    j = 0
    while j < len(order):
        k = j
        while k + 1 < len(order) and xs[order[k + 1]] == xs[order[j]]:
            k += 1
        avg = (j + k) / 2.0 + 1.0
        for m in range(j, k + 1):
            r[order[m]] = avg
        j = k + 1
    return r


def auc_emc_up(vals, emc_idx, oth_idx):
    """AUC = P(EMC sample ranks above a non-EMC sample) for this gene. Robust rank statistic."""
    e = [vals[i] for i in emc_idx if vals[i] is not None]
    o = [vals[i] for i in oth_idx if vals[i] is not None]
    if not e or not o:
        return None
    r = ranks([vals[i] for i in emc_idx + oth_idx])
    ne = sum(1 for i in range(len(emc_idx)) if vals[emc_idx[i]] is not None)
    rank_e = [r[k] for k in range(len(emc_idx)) if vals[emc_idx[k]] is not None]
    if ne == 0:
        return None
    sum_e = sum(rank_e)
    u = sum_e - ne * (ne + 1) / 2.0
    return u / (ne * len(o))


def process(gse):
    out = {"gse": gse}
    try:
        base, files = list_matrix_files(gse)
    except Exception as e:  # noqa
        return {"gse": gse, "error": f"list matrix failed: {e}"}
    out["matrix_files"] = files
    platforms = []
    for fn in files:
        try:
            raw = _get(base + fn)
            sm = parse_series_matrix(raw)
        except Exception as e:  # noqa
            platforms.append({"file": fn, "error": str(e)})
            continue
        n = len(sm["samples"])
        # QC: two-colour detection
        flat = [v for row in sm["values"] for v in row if v is not None]
        neg_frac = (sum(1 for v in flat if v < 0) / len(flat)) if flat else 0.0
        two_colour = neg_frac > 0.15
        miss = sum(1 for row in sm["values"] for v in row if v is None)
        total = sum(len(row) for row in sm["values"]) or 1
        labels, fusion = label_emc(sm["titles"], sm["characteristics"], sm["samples"])
        emc_idx = [i for i, l in enumerate(labels) if l == "EMC"]
        oth_idx = [i for i, l in enumerate(labels) if l == "other"]
        gpl = parse_gpl_symbols(sm["platform"])
        # probe -> best symbol; gene value = max across probes per sample (collapse)
        gene_rows = {}
        for pi, pid in enumerate(sm["probes"]):
            sym = gpl.get(pid)
            if not sym:
                continue
            row = sm["values"][pi]
            if sym not in gene_rows:
                gene_rows[sym] = list(row)
            else:
                cur = gene_rows[sym]
                for j in range(min(len(cur), len(row))):
                    a, b = cur[j], row[j]
                    if b is not None and (a is None or b > a):
                        cur[j] = b
        pinfo = {"file": fn, "platform": sm["platform"], "n_samples": n,
                 "n_emc": len(emc_idx), "n_other": len(oth_idx),
                 "two_colour_relative": two_colour, "neg_fraction": round(neg_frac, 3),
                 "missing_fraction": round(miss / total, 3),
                 "n_genes_annotated": len(gene_rows),
                 "sample_labels": [{"acc": sm["samples"][i], "title": (sm["titles"][i] if i < len(sm["titles"]) else ""),
                                    "label": labels[i], "fusion": fusion[i]} for i in range(n)]}
        # EMC-vs-rest signature (needs both groups)
        if emc_idx and oth_idx:
            aucs = []
            for sym, vals in gene_rows.items():
                a = auc_emc_up(vals, emc_idx, oth_idx)
                if a is not None:
                    aucs.append((sym, a))
            aucs.sort(key=lambda x: -x[1])
            pinfo["signature_note"] = ("AUC = P(EMC ranks above non-EMC). Two-colour => AUC is on "
                                       "log-ratio-vs-reference, still rank-valid." if two_colour else
                                       "AUC = P(EMC ranks above non-EMC) on intensity ranks.")
            pinfo["top_emc_up"] = [{"gene": s, "auc": round(a, 3)} for s, a in aucs[:30]]
            pinfo["top_emc_down"] = [{"gene": s, "auc": round(a, 3)} for s, a in aucs[-15:]]
            marker_rank = {}
            rank_of = {s: k for k, (s, _) in enumerate(aucs)}
            for m in KNOWN_MARKERS:
                if m in rank_of:
                    a = dict(aucs)[m]
                    marker_rank[m] = {"auc": round(a, 3), "rank": rank_of[m] + 1, "of": len(aucs)}
                else:
                    marker_rank[m] = "not_measured"
            pinfo["known_marker_reproduction"] = marker_rank
            # leave-one-EMC-out stability of top-50
            topN = set(s for s, _ in aucs[:50])
            jac = []
            for drop in emc_idx:
                keep = [i for i in emc_idx if i != drop]
                if not keep:
                    continue
                a2 = []
                for sym, vals in gene_rows.items():
                    v = auc_emc_up(vals, keep, oth_idx)
                    if v is not None:
                        a2.append((sym, v))
                a2.sort(key=lambda x: -x[1])
                t2 = set(s for s, _ in a2[:50])
                inter = len(topN & t2)
                jac.append(inter / len(topN | t2))
            if jac:
                pinfo["leave_one_out_top50_jaccard"] = {"mean": round(sum(jac) / len(jac), 3),
                                                        "min": round(min(jac), 3), "n": len(jac)}
        else:
            # all-EMC (or no comparators): report highest-expressed genes + marker percentiles
            means = []
            for sym, vals in gene_rows.items():
                vv = [v for v in vals if v is not None]
                if vv:
                    means.append((sym, sum(vv) / len(vv)))
            means.sort(key=lambda x: -x[1])
            rank_of = {s: k for k, (s, _) in enumerate(means)}
            pinfo["signature_note"] = ("No non-EMC comparators in this platform's labeled samples -> "
                                       "reporting highest-mean-expression genes and known-marker percentiles"
                                       + (" (two-colour: RELATIVE to reference pool)." if two_colour else "."))
            pinfo["top_expressed"] = [{"gene": s, "mean": round(m, 2)} for s, m in means[:30]]
            pinfo["known_marker_reproduction"] = {
                m: ({"mean_rank_percentile": round(100 * (1 - rank_of[m] / max(1, len(means))), 1)}
                    if m in rank_of else "not_measured") for m in KNOWN_MARKERS}
        # EWSR1 vs TAF15 feasibility
        ew = [i for i in emc_idx if fusion[i] == "EWSR1"]
        ta = [i for i in emc_idx if fusion[i] == "TAF15"]
        pinfo["fusion_stratification"] = {
            "n_EWSR1_labeled": len(ew), "n_TAF15_labeled": len(ta),
            "feasible": bool(ew and ta),
            "note": ("EWSR1-vs-TAF15 differential feasible." if (ew and ta) else
                     "Fusion partner NOT recoverable from this dataset's public metadata -> "
                     "EWSR1-vs-TAF15 stratification NOT feasible here (honest limitation).")}
        platforms.append(pinfo)
    out["platforms"] = platforms
    return out


def main():
    results = {"_note": "EMC atlas expression reprocessing (author-normalized series matrices; rank-based; "
                        "per-platform, never merged). Run in CI (GEO reachable). See METHODS.md.",
               "_bounds": "Series-matrix (not raw-CEL RMA); tiny n; legacy arrays; stroma dilution; "
                          "AUC on two-colour data is relative-to-reference.",
               "datasets": []}
    for gse in DATASETS:
        print(f"processing {gse} ...", file=sys.stderr)
        try:
            results["datasets"].append(process(gse))
        except Exception as e:  # noqa
            results["datasets"].append({"gse": gse, "error": str(e)})
    with open(os.path.join(OUTDIR, "emc-expression-reprocess.json"), "w") as f:
        json.dump(results, f, indent=2)
    # brief markdown
    lines = ["# EMC expression reprocessing (generated in CI)", "",
             results["_note"], "", f"_Bounds:_ {results['_bounds']}", ""]
    for d in results["datasets"]:
        lines.append(f"## {d['gse']}")
        if d.get("error"):
            lines.append(f"- ERROR: {d['error']}")
            continue
        for p in d.get("platforms", []):
            if p.get("error"):
                lines.append(f"- {p['file']}: ERROR {p['error']}")
                continue
            lines.append(f"- **{p['platform']}** ({p['file']}): n={p['n_samples']} "
                         f"(EMC {p['n_emc']}, other {p['n_other']}), "
                         f"{'two-colour/relative' if p['two_colour_relative'] else 'single-channel'}, "
                         f"{p['n_genes_annotated']} genes.")
            km = p.get("known_marker_reproduction", {})
            hit = {k: v for k, v in km.items() if v != "not_measured"}
            lines.append(f"  - known-marker reproduction: {json.dumps(hit)}")
            if "leave_one_out_top50_jaccard" in p:
                lines.append(f"  - leave-one-out top50 Jaccard: {p['leave_one_out_top50_jaccard']}")
            lines.append(f"  - fusion stratification: {p['fusion_stratification']['note']}")
    with open(os.path.join(OUTDIR, "emc-expression-reprocess.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote emc-expression-reprocess.json/.md", file=sys.stderr)


if __name__ == "__main__":
    main()
