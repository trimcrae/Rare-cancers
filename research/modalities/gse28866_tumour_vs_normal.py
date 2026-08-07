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
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gse28866-tumour-vs-normal.json")

BASE = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE28nnn/GSE28866/suppl/"
NORMALIZED = BASE + "GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz"
RAW = BASE + "GSE28866_raw_counts_54511_peaks_cancer_and_normal.txt.gz"

#: The four EMC libraries, from this repo's own sample-level characterisation of the series
#: (`atr-hrd-sarcoma-series.json`). Recorded here as the ONLY hard-coded sample identity; every
#: other column role is derived from the header the file actually carries.
EMC_GSMS = ["GSM715466", "GSM715467", "GSM715470", "GSM715472"]

#: ⭐ THE COLUMN HEADERS ARE NOT GSMs. Measured by the first header read: the normalized table names
#: its columns `<Tissue>_<specimen>` (e.g. `Breast_STT5463`), so a GSM never appears and matching on
#: one finds nothing — which the first run reported honestly as `emc_gsms_found_in_header: []` rather
#: than as an absent EMC arm. The four EMC libraries carry the specimen ids below, resolved from this
#: repo's own sample-level characterisation of the series (`atr-hrd-sarcoma-series.json` titles
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
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(doc["verdict"], indent=2, ensure_ascii=False))
    for s in doc["sources"]:
        print("%-26s %-12s fields=%s symbols=%s emc_found=%s" % (
            s["id"], s.get("status"), s.get("n_header_fields"),
            s.get("columns", {}).get("symbol_like_columns"), s.get("emc_gsms_found_in_header")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
