#!/usr/bin/env python3
"""
GSE4303 cross-check — does the surrogate surfaceome shortlist hold up in REAL EMC tumours?

WHY. emc_surfaceome_scan.py ranks surface antigens in an EMC-*surrogate* sarcoma class (DepMap has no
EMC line). The EMC data probe (emc_line_data_probe.py) found the new EMC cell lines have not deposited
public transcriptomes, but a public real-EMC *tumour* expression dataset exists: **GSE4303** ("Gene
expression profile of extraskeletal myxoid chondrosarcoma"). This script cross-checks the surrogate's
shortlist against that real EMC data: do the surrogate's picks (CDH11/FGFR1/GPC2/PTK7/MCAM/…) actually
read high in real EMC tumours?

PLATFORM GATE (the honest guard the user asked for). GSE4303 is an *older microarray*; if it is a
**two-colour** platform its values are log-ratios vs a reference pool — RELATIVE, not ABSOLUTE
expression — so "is this gene highly expressed" is not directly answerable. We DETECT this (fraction of
negative values) and, if two-colour, report the shortlist as *relative-to-reference* (sign/rank of the
log-ratio) with a loud caveat rather than force a meaningless absolute-expression ranking. If
single-channel (intensities), we report percentile rank among all measured genes.

HONEST BOUNDS. Real EMC *tumour* (not cell line), so surface reads are diluted by the abundant myxoid
STROMA; old array with limited gene coverage; small n; a DIFFERENT platform/normalisation from the
DepMap surrogate (so this is a corroboration cross-check, not a merge). A gene absent from the old array
is "not measured", not "not expressed".

Internet required (GEO FTP) -> runs in CI. Output: emc-gse4303-crosscheck.json
"""
import gzip
import io
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "emc-gse4303-crosscheck.json")

GSE = "GSE4303"
MATRIX_DIR = f"https://ftp.ncbi.nlm.nih.gov/geo/series/GSE4nnn/{GSE}/matrix/"

# The surrogate winners to validate (from emc-surfaceome-scan.json) + the USZ-paper-mentioned markers.
SHORTLIST = {
    "CDH11": "surrogate most-selective (+3.18 vs rest)",
    "FGFR1": "surrogate top (+1.99; highest in the 1 myxoid line)",
    "GPC2": "surrogate selective (+1.49); CAR/ADC target",
    "PTK7": "surrogate (+1.24); ADC target",
    "MCAM": "surrogate (+1.09); CD146",
    "EPHB4": "surrogate (+1.0)",
    "CD276": "B7-H3: broad but NON-selective (+0.14) in surrogate — expect broad here too",
    "NCAM1": "CD56; EMC neuroendocrine-phenotype angle",
    "EGFR": "mentioned in the USZ-EMC paper text (verify)",
    "KIT": "mentioned in the USZ-EMC paper text (verify)",
}


def _get(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0"})
    import time
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa
            print(f"  retry {i+1} {url[:70]}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"failed: {url}")


def parse_series_matrix(raw):
    """Return (platform_id, sample_ids, probe_ids, value_matrix[list per probe])."""
    text = gzip.decompress(raw).decode("utf-8", "replace")
    platform, samples = None, []
    lines = text.splitlines()
    in_tbl = False
    header, probes, values = None, [], []
    for ln in lines:
        if ln.startswith("!Series_platform_id"):
            platform = ln.split("\t")[-1].strip().strip('"')
        elif ln.startswith("!Sample_geo_accession"):
            samples = [x.strip().strip('"') for x in ln.split("\t")[1:]]
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
            vals = []
            for x in parts[1:]:
                x = x.strip().strip('"')
                try:
                    vals.append(float(x))
                except ValueError:
                    vals.append(None)
            probes.append(pid)
            values.append(vals)
    return platform, samples, probes, values


def parse_gpl_symbols(platform_id):
    """Map probe ID -> gene symbol from the GPL soft annotation. Best-effort."""
    if not platform_id:
        return {}
    n = re.sub(r"\D", "", platform_id)
    # GEO groups platforms into dirs of GPL{all-but-last-3-digits}nnn (e.g. GPL96->GPLnnn, GPL10558->GPL10nnn)
    grp = f"GPL{n[:-3]}nnn" if len(n) > 3 else "GPLnnn"
    url = f"https://ftp.ncbi.nlm.nih.gov/geo/platforms/{grp}/{platform_id}/soft/{platform_id}_family.soft.gz"
    try:
        raw = _get(url, timeout=300)
        text = gzip.decompress(raw).decode("utf-8", "replace")
    except Exception as e:  # noqa
        print(f"  GPL soft fetch failed ({e})", file=sys.stderr)
        return {}
    lines = text.splitlines()
    in_tbl = False
    header = None
    id_i, sym_i = None, None
    m = {}
    for ln in lines:
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
                # try exact gene-symbol column names first, then substring fallbacks — old custom
                # cDNA arrays (GPL2937 etc.) label the symbol column variously.
                for cand in ("gene symbol", "gene_symbol", "symbol", "genesymbol", "ilmn_gene",
                             "gene", "orf", "gene name", "gene_name", "gene title", "name",
                             "unigene symbol", "clone name"):
                    if cand in low:
                        sym_i = low.index(cand)
                        break
                if sym_i is None:
                    for i, h in enumerate(low):
                        if "symbol" in h or ("gene" in h and "id" not in h):
                            sym_i = i
                            break
                continue
            if sym_i is not None and len(parts) > sym_i:
                pid = parts[id_i].strip()
                sym = parts[sym_i].strip().split("///")[0].split("//")[0].strip()
                if pid and sym and sym not in (".", "---", ""):
                    m[pid] = sym.upper()
    print(f"  GPL {platform_id}: mapped {len(m)} probes -> symbols", file=sys.stderr)
    return m


def main():
    result = {"_note": ("Cross-check of the surrogate surfaceome shortlist against REAL EMC TUMOUR "
                        "expression (GEO GSE4303). Corroboration only — real EMC tumour, but old "
                        "microarray, bulk-tumour (stromal dilution), small n, different platform from "
                        "the DepMap surrogate. Not a merge."),
              "dataset": GSE}
    # Old two-colour series name their matrix with a platform suffix
    # (GSE4303-GPLxxxx_series_matrix.txt.gz), so list the matrix dir and take whatever exists
    # rather than assume the bare GSE4303_series_matrix.txt.gz name.
    matrix_files = []
    try:
        listing = _get(MATRIX_DIR, timeout=120).decode("utf-8", "replace")
        matrix_files = sorted(set(re.findall(r"GSE4303[\w\-.]*?series_matrix\.txt\.gz", listing)))
    except Exception as e:  # noqa
        result["matrix_dir_list_error"] = str(e)
    if not matrix_files:
        matrix_files = [f"{GSE}_series_matrix.txt.gz"]  # fallback to the canonical name
    result["matrix_files_found"] = matrix_files

    platform = samples = probes = values = None
    fetch_errs = []
    for mf in matrix_files:
        try:
            platform, samples, probes, values = parse_series_matrix(_get(MATRIX_DIR + mf))
            # The matrix FILENAME (GSE4303-GPLxxxx_series_matrix) is the authoritative platform for the
            # data in THIS file; the parsed !Series_platform_id can list a different subseries platform.
            m = re.search(r"(GPL\d+)", mf)
            if m:
                platform = m.group(1)
            result["matrix_file_used"] = mf
            break
        except Exception as e:  # noqa
            fetch_errs.append(f"{mf}: {e}")
    if values is None:
        result["status"] = f"matrix_fetch_failed: {fetch_errs}"
        json.dump(result, open(OUT, "w"), indent=2)
        print(json.dumps(result, indent=2))
        return

    n_samples = len(samples)
    # PLATFORM GATE: two-colour (log-ratios, many negatives) vs single-channel (intensities).
    flat = [v for row in values for v in row if v is not None]
    frac_neg = (sum(1 for v in flat if v < 0) / len(flat)) if flat else 0.0
    two_colour = frac_neg > 0.15  # log-ratio data has a large negative fraction
    value_kind = ("log-ratio (two-colour; RELATIVE to reference pool — NOT absolute expression)"
                  if two_colour else "intensity (single-channel; absolute-ish expression)")

    sym = parse_gpl_symbols(platform)
    # collapse probes -> gene mean across samples
    gene_vals = {}
    for pid, row in zip(probes, values):
        g = sym.get(pid)
        if not g:
            continue
        present = [v for v in row if v is not None]
        if not present:
            continue
        gene_vals.setdefault(g, []).append(sum(present) / len(present))
    gene_mean = {g: sum(v) / len(v) for g, v in gene_vals.items()}
    # rank all genes by mean (for percentile)
    ordered = sorted(gene_mean.items(), key=lambda kv: kv[1])
    rank_of = {g: i for i, (g, _) in enumerate(ordered)}
    ntot = len(ordered)

    shortlist_out = {}
    for g, why in SHORTLIST.items():
        if g in gene_mean:
            pct = round(100 * rank_of[g] / max(1, ntot - 1), 1)
            shortlist_out[g] = {
                "measured": True, "why_flagged": why,
                "mean_value": round(gene_mean[g], 3),
                "percentile_among_all_genes": pct,
                "high_in_EMC_tumour": pct >= 75,
                "sign": ("above_reference" if (two_colour and gene_mean[g] > 0)
                         else "below_reference" if two_colour else None),
            }
        else:
            shortlist_out[g] = {"measured": False, "why_flagged": why,
                                "note": "not on this old array (not measured != not expressed)"}

    validated = [g for g, s in shortlist_out.items()
                 if s.get("measured") and s.get("high_in_EMC_tumour")]
    result.update({
        "status": "ok",
        "platform_id": platform,
        "n_emc_samples": n_samples,
        "value_kind": value_kind,
        "two_colour_ratio_data": two_colour,
        "frac_negative_values": round(frac_neg, 3),
        "n_genes_measured": ntot,
        "n_probes_mapped": len(sym),
        "platform_gate": (
            "TWO-COLOUR RATIO DATA — shortlist percentiles are ranks of the log-ratio (higher = more "
            "above the reference pool), a RELATIVE signal; read 'high_in_EMC_tumour' as 'high relative "
            "to the array's reference', NOT absolute expression." if two_colour else
            "single-channel intensities — percentiles approximate absolute expression rank in EMC tumours."),
        "shortlist_in_real_EMC_tumour": shortlist_out,
        "validated_high_in_EMC": validated,
        "verdict": (f"{len(validated)} of {sum(1 for s in shortlist_out.values() if s.get('measured'))} "
                    "measured surrogate-shortlist antigens rank high (>=75th pct) in real EMC tumour "
                    "expression"
                    + (" — but as RELATIVE two-colour ratios; treat as weak corroboration."
                       if two_colour else ".")),
    })
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: result[k] for k in ("status", "platform_id", "n_emc_samples", "value_kind",
                      "two_colour_ratio_data", "n_genes_measured", "validated_high_in_EMC",
                      "verdict")}, indent=2))


if __name__ == "__main__":
    main()
