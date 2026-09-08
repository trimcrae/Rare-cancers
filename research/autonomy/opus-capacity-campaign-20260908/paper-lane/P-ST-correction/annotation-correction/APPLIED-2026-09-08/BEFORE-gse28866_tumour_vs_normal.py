#!/usr/bin/env python3
"""GSE28866 — the only tumour-vs-NORMAL EMC arm reachable at $0. ($0, stdlib + urllib, CI-only)

⭐ WHY THIS SERIES IS WORTH A DEDICATED READER. Every expression contrast this repository holds is
EMC vs OTHER SARCOMAS (GSE24369, GSE4303). That answers "is this gene higher in EMC than in a
fibrosarcoma?" and it cannot answer "is this gene higher in EMC than in normal tissue?" — which is
the question every surface-antigen, radioligand and immunotherapy claim actually depends on, because
on-target/off-tumour toxicity is a statement about NORMAL tissue. GSE28866 carries **4 named EMC
samples alongside 27 normal-tissue libraries** in one 3SEQ experiment, and this repository has never
read it.

⛔ WHY IT LOOKED EMPTY AND IS NOT. `GSE28866_series_matrix.txt.gz` reports `n_probes: 0` across 99
samples on GPL10999 with a 404 on the platform annotation. That is a PACKAGING fact about a
sequencing-platform deposit, not a statement that the deposit is empty: the data live in the SERIES
supplementary tables, which are indexed by 3SEQ PEAK rather than by probe. An absent reading is not
a reading of absence, and the earlier `n_probes: 0` was exactly that mistake waiting to be made.

⚠ WHAT IS GENUINELY UNKNOWN BEFORE THIS RUNS, and is the whole point of the header read: whether the
peak tables carry a GENE SYMBOL column at all. If they do, this is a direct tumour-vs-normal read on
named genes. If they do not, every row is a genomic interval and gene assignment needs a coordinate
map with its own build reconciliation — a different and much larger job. The verdict field says which
world we are in, and this module does NOT guess.

⛔ CEILINGS THAT TRAVEL WITH ANY READING THIS PRODUCES.
  · n = 4 EMC. That is four patients. No inference here survives being described as a distribution.
  · The 27 normals are a TISSUE PANEL, not matched adjacent tissue, so a tumour-vs-normal difference
    confounds lineage with disease exactly as the sarcoma-vs-sarcoma contrasts confound it the other
    way. The two contrasts are complementary and neither is a substitute for the other.
  · 3SEQ measures 3'-end read density. It is not an array intensity and is not directly comparable
    to GPL6244/GPL3290 values; nothing here may be pooled with those.
  · Transcript, not protein; no surface localisation; no statement about safety.
"""
from __future__ import annotations

import gzip
import io
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gse28866-tumour-vs-normal.json")

BASE = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE28nnn/GSE28866/suppl/"
NORMALIZED = BASE + "GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz"
RAW = BASE + "GSE28866_raw_counts_54511_peaks_cancer_and_normal.txt.gz"

#: The four EMC libraries, from this repo's own sample-level characterisation of the series
#: (`geo-gse28866-brunner-series.json`). Recorded here as the ONLY hard-coded sample identity;
#: every other column role is derived from the header the file actually carries.
#: ⚠ THAT CHARACTERISATION LIVED IN `atr-hrd-sarcoma-series.json` UNTIL 2026-08-27, WHICH IS A
#: FILENAME BELONGING TO ANOTHER SERIES: its producer declares `SERIES = "GSE299349"`, and the two
#: series overwrote each other there in both directions (325258cb8, then a8caba9). The GSE28866
#: bytes were restored verbatim under their own name; that name is what this points at now.
EMC_GSMS = ["GSM715466", "GSM715467", "GSM715470", "GSM715472"]

#: ⭐ THE COLUMN HEADERS ARE NOT GSMs. Measured by the first header read: the normalized table names
#: its columns `<Tissue>_<specimen>` (e.g. `Breast_STT5463`), so a GSM never appears and matching on
#: one finds nothing — which the first run reported honestly as `emc_gsms_found_in_header: []` rather
#: than as an absent EMC arm. The four EMC libraries carry the specimen ids below, resolved from this
#: repo's own sample-level characterisation of the series (`geo-gse28866-brunner-series.json` titles
#: `STT5525_EMC`, `STT5526_EMC`, `STT5527_EMC`, `STT5592_EMC`).
EMC_SPECIMENS = ["STT5525", "STT5526", "STT5527", "STT5592"]

#: ⛔ AND THE NORMAL ARM IS NOT DEFINED HERE, DELIBERATELY. The series says 66 cancer + 27 normal
#: libraries, and 66+27 = 93 matches the raw table's sample-column count exactly — but the committed
#: characterisation does not carry the 27 normals' titles, so which columns they are is UNKNOWN until
#: the full header is read. Hard-coding a guess (`Normal_*`, or "anything not STT") would define the
#: contrast by assumption and then measure it, which is how a comparator arm gets silently wrong.
#: This module therefore REPORTS every sample column and classifies none of them it cannot justify.

#: Genes the surface-antigen and matrix lanes are blocked on a normal-tissue comparison for.
WANTED = ["ALCAM", "CD248", "CSPG4", "PRAME", "SSTR2", "CD276", "FAP", "MSLN", "L1CAM",
          "GPC3", "CDH17", "VCAN", "BGN", "CD44", "RET", "ENO3", "SEMA3C", "PPARG", "NR4A3"]


def _fetch(url, max_bytes=None):
    """Bytes from `url`. Returns (data, error). Never raises — an unreachable file is a FACT."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (rare-cancers; $0 CI)"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = r.read(max_bytes) if max_bytes else r.read()
            return data, None
    except Exception as exc:                                          # noqa: BLE001
        return None, "%s: %s" % (type(exc).__name__, exc)


def _header_and_first_rows(data, n_rows=3):  # noqa: D401
    """The header line and a few data rows, gunzipped. Tolerates a truncated tail deliberately:
    a RANGE read of a gzip member ends mid-stream, and the header is all the first question needs."""
    rows, err = [], None
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as fh:
            for i, line in enumerate(fh):
                rows.append(line.decode("utf-8", errors="replace").rstrip("\n"))
                if i > n_rows:
                    break
    except (EOFError, OSError) as exc:
        err = "%s: %s (expected on a truncated read; header may still be present)" % (
            type(exc).__name__, exc)
    return rows, err


def _classify_columns(header_fields):
    """Which columns are SAMPLES, which are annotation, and is any of them a gene symbol?

    ⚠ Asserted by SHAPE, not by hoping for a column called `gene`. A symbol column is one whose
    name looks annotational AND whose values are not numeric; a sample column is one whose name
    carries a GSM id or a library name. Both are reported so a reader can disagree with the call.
    """
    ann_names = {"peak", "peakid", "peak_id", "chr", "chrom", "start", "end", "strand", "gene",
                 "gene_symbol", "symbol", "genesymbol", "gene_name", "annotation", "id", "name",
                 "nearest_gene", "refseq", "transcript"}
    ann, samples, gsm_cols = [], [], []
    for f in header_fields:
        key = f.strip().strip('"').lower().replace(" ", "_")
        if key in ann_names or any(k in key for k in ("gene", "symbol", "chr", "peak", "strand")):
            ann.append(f)
        else:
            samples.append(f)
        if "gsm" in key:
            gsm_cols.append(f)
    symbol_like = [f for f in ann
                   if any(k in f.strip().strip('"').lower() for k in ("gene", "symbol", "name"))]
    return {"annotation_columns": ann, "sample_columns_n": len(samples),
            "sample_columns": samples, "gsm_named_columns_n": len(gsm_cols),
            "symbol_like_columns": symbol_like}


def _groups(sample_cols):
    """Split the 93 libraries into the 66 cancers and the 27 normals, FROM THE HEADER.

    ⭐ THE GROUPING IS DERIVED AND THE DERIVATION IS TWO-SIDED, which is what makes it a reading
    rather than a guess. Tumour libraries are named `<Type>_STT####` (GIST_STT…, EMC_STT…) and
    normal libraries are a bare `STT####` with no tissue prefix. Counting the header gives 66
    prefixed and 27 bare — and the series description independently says 66 cancer and 27 normal.
    BOTH halves landing exactly is the evidence; either alone would be a coincidence worth
    distrusting. `_grouping_check` below re-derives those counts at runtime and the verdict refuses
    to emit a contrast if they ever stop matching.

    ⚠ Three annotation columns (`hg18_coords`, `classification`,
    `differentially_expressed_cancer_type`) sit among the sample columns because the header gives
    them no distinguishing shape. They are dropped by name, and dropping them is what turns 96
    into the 93 the series arithmetic requires.

    ⛔ AND THE DROP IS BY SHAPE AS WELL AS BY NAME, BECAUSE THIS FUNCTION HAS TWO CALLERS THAT HAND
    IT DIFFERENT THINGS. `main` passes the 96 columns `_classify_columns` called samples; `_extract`
    passes the raw 100-field header, which additionally carries `peak`, `gene_id`, `gene_symbol` and
    `peak_exon_gene_symbol`. A name-only drop therefore returned 93 libraries for one caller and 97
    for the other — same function, same file, two different groupings, and only one of them could be
    right. Every one of the 93 real libraries carries `STT` in its name and none of the seven
    annotation columns does, so requiring `STT` makes the derivation independent of which caller is
    asking. The two-sided count check below still guards it; this removes a way for the two callers
    to disagree silently.
    """
    ann = {"hg18_coords", "classification", "differentially_expressed_cancer_type"}
    # ⚠ STRIP \r FIRST. One column ends `..._Adult_normal_breast\r` — the table carries Windows line
    # endings, so the final field of the header keeps its carriage return. Matching `$` against it
    # silently drops that library, which on a 27-library arm is a 3.7 % loss nobody would notice.
    libs = [c.strip().strip('"') for c in sample_cols]
    libs = [c for c in libs if c not in ann and "STT" in c.upper()]
    # ⛔ NORMALS ARE NAMED `STT####_<Adult|Fetal>_normal_<tissue>`, NOT a bare `STT####`. My first
    # pattern assumed the bare form, matched ZERO normals, and the two-sided count check below
    # REFUSED to emit a contrast rather than proceeding on a broken grouping. That refusal is the
    # only reason this is right: a one-sided check would have accepted 57 tumours and said nothing.
    normal = [c for c in libs if "_normal_" in c.lower()]
    tumour = [c for c in libs if c not in normal]
    emc = [c for c in tumour if c.upper().startswith("EMC_")]
    # ⚠ TECHNICAL REPLICATES EXIST and are NOT independent samples: ESS_STT5520_rep1/_rep2 and
    # LMS_STT516_rep1/_rep2. They are reported so any statistic can decide how to treat them
    # instead of silently counting them twice. None is an EMC library.
    reps = sorted({c for c in libs if c.lower().endswith(("_rep1", "_rep2"))})
    return {"n_libraries": len(libs), "n_tumour": len(tumour), "n_normal": len(normal),
            "n_emc": len(emc), "emc_columns": sorted(emc), "normal_columns": sorted(normal),
            "technical_replicate_columns": reps,
            "normal_tissues": sorted({c.lower().split("_normal_")[-1] for c in normal}),
            "matches_series_description": len(tumour) == 66 and len(normal) == 27}


def _extract(data, wanted):
    """Per-gene EMC vs normal vs other-sarcoma from the normalized table. Median of peaks per gene.

    ⛔ WHAT THIS CONTRAST CAN AND CANNOT SETTLE, stated here because the panel's COMPOSITION decides
    it and no amount of arithmetic downstream can repair it. The 27 normals are bowel, breast, colon,
    kidney, lung and uterus — visceral organs. NONE is soft tissue, and only uterus carries much
    mesenchyme at all (myometrium), inside a whole-organ library dominated by other compartments.
    ⇒ A gene high in EMC against THESE normals is NOT thereby shown to be EMC-specific rather than
    mesenchymal-lineage-specific: the comparator has almost no mesenchymal tissue in it, so the
    lineage confound survives in a new costume. What this arm DOES give is a normal-ORGAN exposure
    reading, which is the on-target/off-tumour question, and that is worth having on its own terms.
    The sarcoma arm here (DDLPS, ESS, EWS, GIST, LMS, MLPS, SS) replicates the existing
    EMC-vs-sarcoma contrast on a third cohort and a different technology, which is robustness rather
    than a new axis.
    """
    rows, err = [], None
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as fh:
        header = fh.readline().decode("utf-8", "replace").rstrip("\r\n").split("\t")
        idx = {c.strip().strip('"'): i for i, c in enumerate(header)}
        sym_i = idx.get("gene_symbol")
        groups = _groups([c.strip().strip('"') for c in header])
        emc_i = [idx[c] for c in groups["emc_columns"] if c in idx]
        nrm_i = [idx[c] for c in groups["normal_columns"] if c in idx]
        sar = [c for c in header if any(c.startswith(p + "_STT") for p in
               ("DDLPS", "ESS", "EWS", "GIST", "LMS", "MLPS", "SS"))]
        sar_i = [idx[c] for c in sar if c in idx]
        want = {w.upper() for w in wanted}
        per = {}
        for line in fh:
            f = line.decode("utf-8", "replace").rstrip("\r\n").split("\t")
            if sym_i is None or sym_i >= len(f):
                continue
            g = f[sym_i].strip().strip('"').upper()
            if g not in want:
                continue
            def vals(ix):
                out = []
                for i in ix:
                    if i < len(f):
                        try:
                            out.append(float(f[i]))
                        except ValueError:
                            pass
                return out
            per.setdefault(g, []).append((vals(emc_i), vals(nrm_i), vals(sar_i)))
    def med(xs):
        xs = sorted(xs)
        return None if not xs else (xs[len(xs)//2] if len(xs) % 2 else
                                    (xs[len(xs)//2-1]+xs[len(xs)//2])/2)
    out = {}
    for g, peaks in per.items():
        e = [med(p[0]) for p in peaks if p[0]]
        n = [med(p[1]) for p in peaks if p[1]]
        s = [med(p[2]) for p in peaks if p[2]]
        out[g] = {"n_peaks": len(peaks), "emc_median": med([x for x in e if x is not None]),
                  "normal_median": med([x for x in n if x is not None]),
                  "sarcoma_median": med([x for x in s if x is not None]),
                  "_n_emc_libs": len(emc_i), "_n_normal_libs": len(nrm_i),
                  "_n_sarcoma_libs": len(sar_i)}
    missing = sorted(want - set(out))
    return out, missing, groups


# -------------------------------------------------------------------------------------------
# THE CALIBRATION. A ratio is not a reading until you know what an arbitrary gene does.
# -------------------------------------------------------------------------------------------
def _ratio(numerator, denominator):
    """EMC / comparator, or None when the comparator arm is zero or absent.

    A zero denominator is NOT a large ratio -- it is an unreadable one, and rendering it as a
    number would put every gene undetected in the comparator arm at the top of the ranking."""
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return numerator / denominator


def _percentile_of(value, distribution):
    """Fraction of the distribution at or below `value`, as a percentile in [0, 100].

    Reported to one decimal because the deposit carries ~10^4 genes; more would be false
    precision, and the quantity is a rank, not a measurement."""
    if value is None or not distribution:
        return None
    at_or_below = sum(1 for x in distribution if x <= value)
    return round(100.0 * at_or_below / len(distribution), 1)


def _calibrate(data, wanted):
    """Where the wanted genes' EMC/comparator ratios sit among EVERY gene in the deposit.

    WHY THIS EXISTS. The manuscript this arm feeds argues (§1.3) that no gene-set or per-gene read
    on a platform is interpretable until it is calibrated against what an arbitrary gene does on
    the same platform -- and then reported the 3SEQ arm as bare fold-changes, which is the one
    place its own thesis was not applied. A 2.5x ratio is a finding only if 2.5x is unusual here.

    WHAT IT IS NOT. This is a RANK within one deposit, not a test. n_EMC is 4; there is no
    p-value here and none should be inferred from a high percentile. It also cannot separate
    EMC-specific from mesenchymal-lineage-specific, for the reason `_extract` states at length."""
    per = {}
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as fh:
        header = fh.readline().decode("utf-8", "replace").rstrip("\r\n").split("\t")
        idx = {c.strip().strip('"'): i for i, c in enumerate(header)}
        sym_i = idx.get("gene_symbol")
        groups = _groups([c.strip().strip('"') for c in header])
        emc_i = [idx[c] for c in groups["emc_columns"] if c in idx]
        nrm_i = [idx[c] for c in groups["normal_columns"] if c in idx]
        sar = [c for c in header if any(c.startswith(p + "_STT") for p in
               ("DDLPS", "ESS", "EWS", "GIST", "LMS", "MLPS", "SS"))]
        sar_i = [idx[c] for c in sar if c in idx]
        if sym_i is None:
            return {"_status": "NO_GENE_SYMBOL_COLUMN",
                    "_means": "the deposit could not be ranked; this is an absent reading."}
        for line in fh:
            f = line.decode("utf-8", "replace").rstrip("\r\n").split("\t")
            if sym_i >= len(f):
                continue
            g = f[sym_i].strip().strip('"').upper()
            if not g or g in (".", "NA", "-"):
                continue

            def vals(ix):
                out = []
                for i in ix:
                    if i < len(f):
                        try:
                            out.append(float(f[i]))
                        except ValueError:
                            pass
                return out
            per.setdefault(g, []).append((vals(emc_i), vals(nrm_i), vals(sar_i)))

    def med(xs):
        xs = sorted(x for x in xs if x is not None)
        return None if not xs else (xs[len(xs)//2] if len(xs) % 2 else
                                    (xs[len(xs)//2-1]+xs[len(xs)//2])/2)

    dist_n, dist_s, gene_ratio = [], [], {}
    for g, peaks in per.items():
        e = med([med(p[0]) for p in peaks if p[0]])
        n = med([med(p[1]) for p in peaks if p[1]])
        s = med([med(p[2]) for p in peaks if p[2]])
        rn, rs = _ratio(e, n), _ratio(e, s)
        gene_ratio[g] = (rn, rs)
        if rn is not None:
            dist_n.append(rn)
        if rs is not None:
            dist_s.append(rs)
    dist_n.sort()
    dist_s.sort()

    def q(dist, p):
        return None if not dist else round(dist[min(len(dist) - 1, int(p * (len(dist) - 1)))], 4)

    out = {
        "_what": ("each wanted gene's EMC/comparator ratio expressed as a percentile of the same "
                  "ratio computed for EVERY gene in this deposit"),
        "_why": ("a fold-change is not a reading until an arbitrary gene's fold-change is known. "
                 "This is the manuscript's own §1.3 standard applied to the arm that lacked it."),
        "_not_a_test": ("a percentile is a RANK, not a p-value. n_EMC = 4 and no test is computed "
                        "or implied anywhere in this block."),
        "n_genes_in_deposit": len(per),
        "n_genes_with_a_normal_ratio": len(dist_n),
        "n_genes_with_a_sarcoma_ratio": len(dist_s),
        "_genes_without_a_ratio": ("a gene whose comparator median is zero has NO ratio and is "
                                   "excluded from the distribution rather than ranked at the top."),
        "distribution_emc_over_normal": {"median": q(dist_n, 0.50), "p75": q(dist_n, 0.75),
                                         "p90": q(dist_n, 0.90), "p95": q(dist_n, 0.95),
                                         "p99": q(dist_n, 0.99)},
        "distribution_emc_over_sarcoma": {"median": q(dist_s, 0.50), "p75": q(dist_s, 0.75),
                                          "p90": q(dist_s, 0.90), "p95": q(dist_s, 0.95),
                                          "p99": q(dist_s, 0.99)},
        "per_gene": {},
    }
    for w in sorted({x.upper() for x in wanted}):
        rn, rs = gene_ratio.get(w, (None, None))
        out["per_gene"][w] = {
            "emc_over_normal": None if rn is None else round(rn, 4),
            "emc_over_normal_percentile": _percentile_of(rn, dist_n),
            "emc_over_sarcoma": None if rs is None else round(rs, 4),
            "emc_over_sarcoma_percentile": _percentile_of(rs, dist_s),
            "_absent_means": ("null is an unreadable ratio -- no peak, or a zero comparator "
                              "median -- NOT a ratio of zero."),
        }
    return out


def main(argv=None):
    argv = argv or sys.argv[1:]
    doc = {
        "_what": "GSE28866 header read — does the only tumour-vs-NORMAL EMC deposit carry gene symbols?",
        "_status": ("$0, CI. A HEADER READ, deliberately. It answers one question — is this deposit "
                    "gene-indexed or interval-indexed — because the answer decides whether a "
                    "tumour-vs-normal EMC read is a parse or a coordinate-mapping project."),
        "_series": "GSE28866",
        "_why_the_series_matrix_looked_empty": (
            "n_probes: 0 across 99 samples on GPL10999 with a 404 on the platform annotation is a "
            "PACKAGING fact about a sequencing deposit, not empty data. The values are in the series "
            "SUPPLEMENTARY peak tables."),
        "_emc_samples_expected": EMC_GSMS,
        "_ceilings": [
            "n = 4 EMC patients. Nothing here is a distribution.",
            "The 27 normals are a tissue panel, NOT matched adjacent tissue.",
            "3SEQ 3'-end read density is not an array intensity; never pool with GPL6244/GPL3290.",
            "Transcript only. No protein, no surface localisation, no safety statement.",
        ],
        "sources": [],
    }

    # ⛔ THE HEADER READ AND THE EXTRACTION MUST SHARE ONE FETCH, AND THE PREVIOUS REVISION SHARED
    # NOTHING. `_groups` and `_extract` were both committed and `main` called NEITHER, so the artifact
    # kept reporting a header read while the commit message claimed a grouping — a function's
    # PRESENCE in a module is not evidence it ran, which is the same class as a populated field that
    # was never measured. Keeping the normalized bytes here is what lets both actually execute.
    fetched = {}
    for name, url in (("normalized_36048_peaks", NORMALIZED), ("raw_counts_54511_peaks", RAW)):
        data, err = _fetch(url, max_bytes=None if name.startswith("normalized") else 3_000_000)
        rec = {"id": name, "url": url}
        if err:
            # ⛔ UNREACHABLE IS A NETWORK FACT AND IS RECORDED AS ONE. It is never "no symbols".
            rec.update({"status": "UNREACHABLE", "error": err})
            doc["sources"].append(rec)
            continue
        rows, gzerr = _header_and_first_rows(data)
        rec["status"] = "READ"
        rec["bytes_read"] = len(data)
        rec["gzip_note"] = gzerr
        if not rows:
            rec["verdict"] = "no rows decoded"
            doc["sources"].append(rec)
            continue
        header = rows[0]
        sep = "\t" if "\t" in header else ("," if "," in header else None)
        rec["separator"] = {"\t": "tab", ",": "comma"}.get(sep, "UNKNOWN")
        fields = header.split(sep) if sep else [header]
        rec["n_header_fields"] = len(fields)
        rec["header_first20"] = fields[:20]
        rec["columns"] = _classify_columns(fields)
        rec["first_data_row_first8"] = (rows[1].split(sep)[:8] if len(rows) > 1 and sep else None)
        emc_present = [g for g in EMC_GSMS if any(g in f for f in fields)]
        rec["emc_gsms_found_in_header"] = emc_present
        rec["emc_gsms_missing_from_header"] = [g for g in EMC_GSMS if g not in emc_present]
        # ⭐ The columns are specimen-named, so resolve the EMC arm on the specimen id instead.
        rec["emc_columns_by_specimen"] = {
            s: [f for f in fields if s in f] for s in EMC_SPECIMENS}
        rec["n_emc_columns_resolved"] = sum(
            1 for v in rec["emc_columns_by_specimen"].values() if v)
        rec["grouping"] = _groups(rec["columns"]["sample_columns"])
        fetched[name] = data
        doc["sources"].append(rec)

    read = [s for s in doc["sources"] if s.get("status") == "READ"]
    sym = [s for s in read if s.get("columns", {}).get("symbol_like_columns")]
    if not read:
        doc["verdict"] = {
            "answer": "UNREACHABLE",
            "_reading": ("Neither peak table could be fetched. This is a statement about the network "
                         "from this runner, NOT about the deposit's contents, and it must not be "
                         "recorded as 'no gene symbols'."),
        }
    elif sym:
        doc["verdict"] = {
            "answer": "GENE_INDEXED",
            "symbol_columns": {s["id"]: s["columns"]["symbol_like_columns"] for s in sym},
            "_reading": ("A symbol-like column exists, so a tumour-vs-normal EMC read on named genes "
                         "is a parse rather than a coordinate-mapping project. ⛔ It is still n = 4 "
                         "against an unmatched normal-tissue panel."),
            "_next": "Extract WANTED against the EMC columns vs the 27 normal libraries.",
        }
    else:
        doc["verdict"] = {
            "answer": "INTERVAL_INDEXED",
            "_reading": ("The tables carry no symbol-like column, so every row is a 3SEQ peak "
                         "interval. A gene-level tumour-vs-normal read therefore needs a peak->gene "
                         "coordinate map with its own genome-build reconciliation — a different and "
                         "much larger job than a parse, and NOT something to fake with a nearest-TSS "
                         "guess."),
            "_next": ("Decide explicitly whether that mapping is worth building. Do not report a "
                      "gene-level number from this deposit until it is."),
        }
    doc["_genes_this_would_answer_for"] = WANTED

    # ⛔ THE EXTRACTION IS GATED ON THE GROUPING, NOT ON THE FETCH SUCCEEDING. The first grouping
    # attempt matched 57 tumours and ZERO normals; had the extraction been gated on "did the file
    # download", it would have emitted per-gene EMC-vs-nothing values with a populated
    # `normal_median: null` that a later reader would have taken for a measured absence. A contrast
    # whose comparator arm is empty is not a weak contrast, it is not a contrast.
    nrm = next((s for s in doc["sources"] if s["id"] == "normalized_36048_peaks"), None)
    grp = (nrm or {}).get("grouping") or {}
    if doc["verdict"].get("answer") == "GENE_INDEXED" and grp.get("matches_series_description") \
            and fetched.get("normalized_36048_peaks"):
        try:
            per_gene, missing, _ = _extract(fetched["normalized_36048_peaks"], WANTED)
            doc["per_gene"] = {
                "_contrast": ("Median across a gene's 3SEQ peaks, then median across libraries in "
                              "each arm. EMC n=4; normals n=27 (bowel/breast/colon/kidney/lung/"
                              "uterus); other sarcomas = DDLPS, ESS, EWS, GIST, LMS, MLPS, SS."),
                "_what_the_normal_arm_cannot_settle": (
                    "The normals are visceral organs with almost no soft tissue in them, so a gene "
                    "high in EMC against THIS panel is not thereby shown to be EMC-specific rather "
                    "than mesenchymal-lineage-specific. The normal arm is a normal-ORGAN EXPOSURE "
                    "reading — the on-target/off-tumour axis — and the sarcoma arm is the lineage "
                    "axis. Do not read either as the other."),
                "_ties_to_technical_replicates": grp.get("technical_replicate_columns"),
                "values": per_gene,
                "genes_with_no_peak_in_this_deposit": missing,
            }
        except Exception as exc:                                      # noqa: BLE001
            # An extraction failure is a FACT about the parse, never an absent gene.
            doc["per_gene"] = {"error": "%s: %s" % (type(exc).__name__, exc)}
        try:
            doc["ratio_calibration"] = _calibrate(fetched["normalized_36048_peaks"], WANTED)
        except Exception as exc:                                      # noqa: BLE001
            # A failed calibration must not be indistinguishable from a gene that ranked low.
            doc["ratio_calibration"] = {
                "error": "%s: %s" % (type(exc).__name__, exc),
                "_means": ("the ranking could not be computed. This is an ABSENT calibration, not "
                           "a finding that the wanted genes rank low.")}
    else:
        doc["per_gene"] = {"skipped_because": {
            "verdict": doc["verdict"].get("answer"),
            "grouping_matches_series_description": grp.get("matches_series_description"),
            "normalized_bytes": len(fetched.get("normalized_36048_peaks") or b""),
        }}

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(doc["verdict"], indent=2, ensure_ascii=False))
    for s in doc["sources"]:
        print("%-26s %-12s fields=%s symbols=%s emc_found=%s grouping=%s" % (
            s["id"], s.get("status"), s.get("n_header_fields"),
            s.get("columns", {}).get("symbol_like_columns"), s.get("emc_gsms_found_in_header"),
            {k: s.get("grouping", {}).get(k) for k in
             ("n_tumour", "n_normal", "n_emc", "matches_series_description")}))
    vals = (doc.get("per_gene") or {}).get("values") or {}
    if vals:
        print("\n%-8s %8s %8s %8s  %s" % ("gene", "EMC", "normal", "sarcoma", "peaks"))
        for g in sorted(vals):
            v = vals[g]
            print("%-8s %8s %8s %8s  %s" % (
                g,
                "-" if v["emc_median"] is None else "%.3f" % v["emc_median"],
                "-" if v["normal_median"] is None else "%.3f" % v["normal_median"],
                "-" if v["sarcoma_median"] is None else "%.3f" % v["sarcoma_median"],
                v["n_peaks"]))
        print("no peak in deposit: %s"
              % (doc["per_gene"].get("genes_with_no_peak_in_this_deposit") or "none"))
    else:
        print("\nper_gene: %s" % json.dumps(doc.get("per_gene"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
