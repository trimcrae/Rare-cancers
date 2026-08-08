#!/usr/bin/env python3
"""GSE243553 x the ENO3 NBRE sites — does the EWSR1-NR4A3 arm open chromatin where the motifs are?

═══════════════════════════════════════════════════════════════════════════════════════════════
THE QUESTION
═══════════════════════════════════════════════════════════════════════════════════════════════
`research/manuscripts/nr4a3-fusion-transcriptional-output.md` §3.10 reports a SEQUENCE reading:
*ENO3*'s -10 kb/+15 kb TSS window carries 4 exact NBREs (5'-AAAGGTCA-3', PMID 1902986), more than
its own dinucleotide composition predicts. That section's own first caveat is that **a motif is not
occupancy**, and §3.11 recorded that no genome-wide chromatin experiment with an NR4A3 fusion had
been retrieved.

That absence was OVERTURNED on 2026-08-08 (`research/manuscripts/nr4a3-cistrome-search-2026-08-08.md`):
**GEO GSE243553** (PMID 39048711) is a pooled single-cell ATAC screen of >100 oncofusions in
HEK293T carrying EWSR1-NR4A3, TAF15-NR4A3, TCF12-NR4A3 and TFG-NR4A3 **plus full-length wild-type
NR4A3 and the reciprocal NR4A3-EWSR1 as controls**. This module asks whether that instrument's
EWSR1-NR4A3 arm opens chromatin at the *ENO3* NBRE coordinates the motif scan found.

⛔ TWO CONSTRAINTS THAT TRAVEL WITH EVERY NUMBER THIS MODULE EMITS, AND ARE WRITTEN INTO THE
   ARTIFACT SO THEY CANNOT BE DROPPED BY A READER WHO QUOTES ONLY THE RESULT:
   1. **HEK293T is not EMC chromatin, and accessibility is not binding.** An open peak says a
      region became accessible in an engineered cell line ectopically expressing the fusion. It
      does not say the fusion protein binds there, and it says nothing directly about EMC tumour
      material.
   2. ***ENO3* is this paper's own designated POSITIVE CONTROL** (§2.4 — "UP on both platforms —
      the positive control"). A hit therefore **validates the instrument**; it is not an
      unexpected discovery and must never be written as one.

═══════════════════════════════════════════════════════════════════════════════════════════════
STAGE 1 — RECON. WHAT IS ACTUALLY DEPOSITED?
═══════════════════════════════════════════════════════════════════════════════════════════════
⛔ THIS STAGE EXISTS BECAUSE THE ANSWER MIGHT BE "THE DEPOSIT DOES NOT SUPPORT THE ANALYSIS", AND
   THAT IS A REAL RESULT RATHER THAN A FAILURE. The cistrome search read GEO's file list once and
   recorded `*_fullfusion_fragments-N.tsv.gz` + `*_SampleN_merged_associations.csv.gz` — i.e.
   FRAGMENTS and a barcode->variant map, with no sign of per-fusion peak calls. If that holds,
   there is no deposited peak set to intersect and the honest output names exactly which files
   exist. Manufacturing peaks by re-calling them here would be a different experiment wearing this
   one's name (CLAUDE.md §4).

   So recon reads, and RECORDS VERBATIM, four independent places a peak call could live:
     (a) the GEO series supplementary directory,
     (b) every GEO SAMPLE's supplementary directory and SOFT record — where the genome build is
         declared, in `!Sample_data_processing`,
     (c) the authors' analysis repository `mfrenkel16/OncofusionPRODATAC` (GitHub trees API), and
     (d) the preprint's supplementary media list (bioRxiv), because a differential-peak table is
         far more often a paper supplement than a GEO file.

   Every fetch's HTTP status is recorded. ⚠ AN ABSENT READING IS NOT A READING OF ABSENCE
   (CLAUDE.md §4): a non-200 is stored as `not_retrieved`, never as "no such file".

═══════════════════════════════════════════════════════════════════════════════════════════════
THE COORDINATES, AND WHY THEY ARE NOT TYPED HERE
═══════════════════════════════════════════════════════════════════════════════════════════════
Per CLAUDE.md §1 the *ENO3* NBRE coordinates have ONE home — `emc-ret-target-scan.json`
-> `part_1_nbre_scan.focus_genes.ENO3`, the committed output of the same scan §3.10/SI §S6
report. This module READS them from that artifact and derives genomic coordinates from the
window arithmetic; it never re-types a coordinate. `--selftest` asserts the derivation against
the artifact's own `offset_from_tss` field, so a drift in either breaks the build.

Build: that artifact declares `assembly: GRCh38` per focus gene. GSE243553's build is READ from
its own SOFT records in recon and is NOT assumed. ⛔ If the two disagree, the analysis stage
refuses to compute an overlap — an intersection across builds is meaningless.

Usage:
    python3 research/modalities/gse243553_eno3_overlap.py --selftest
    python3 research/modalities/gse243553_eno3_overlap.py --stage recon --fetch
    python3 research/modalities/gse243553_eno3_overlap.py --stage recon --check
"""

from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

MOTIF_SCAN_ARTIFACT = os.path.join(HERE, "emc-ret-target-scan.json")
RECON_OUT = os.path.join(HERE, "gse243553-eno3-overlap-recon.json")

SERIES = "GSE243553"
SERIES_PMID = "39048711"
SERIES_PMCID = "PMC13105821"
PREPRINT_DOI = "10.1101/2023.09.20.555752"
AUTHOR_REPO = "mfrenkel16/OncofusionPRODATAC"

# The NBRE consensus, quoted from the scan artifact's own `_motifs` block rather than typed.
NBRE_LEN = 8

UA = "Rare-cancers-research/1.0 (GSE243553 ENO3 NBRE overlap; +https://github.com/trimcrae/Rare-cancers)"

DEFAULT_BUDGET_S = float(os.environ.get("GSE243553_BUDGET_S", "1200"))


# ───────────────────────────────────────────────────────────────────────────────────────────────
# fetch plumbing — every response keeps its status, so a failure can never read as a zero
# ───────────────────────────────────────────────────────────────────────────────────────────────

class Budget:
    def __init__(self, seconds: float):
        self.seconds = float(seconds)
        self.t0 = time.time()

    def left(self) -> float:
        return self.seconds - (time.time() - self.t0)

    def exhausted(self) -> bool:
        return self.left() <= 0


def fetch(url: str, budget: Budget, timeout: int = 60, max_bytes: int = 8_000_000,
          headers: dict | None = None) -> dict:
    """Return a record that ALWAYS says what happened. Never raises for an HTTP problem."""
    rec = {"url": url, "http": None, "bytes": 0, "text": None, "error": None,
           "elapsed_s": None, "state": None}
    if budget.exhausted():
        rec["state"] = "budget_exhausted"
        rec["error"] = "network budget exhausted before this fetch was attempted"
        return rec
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=min(timeout, max(5, int(budget.left())))) as fh:
            rec["http"] = fh.status
            raw = fh.read(max_bytes)
            rec["bytes"] = len(raw)
            if url.endswith(".gz"):
                try:
                    raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read(max_bytes)
                except OSError as exc:          # truncated stream is expected on a Range read
                    rec["error"] = f"gunzip partial: {exc}"
            rec["text"] = raw.decode("utf-8", "replace")
            rec["state"] = "ok"
    except urllib.error.HTTPError as exc:
        rec["http"] = exc.code
        rec["error"] = f"HTTPError {exc.code} {exc.reason}"
        rec["state"] = "not_retrieved"
    except Exception as exc:                    # noqa: BLE001 — transport, DNS, timeout, reset
        rec["error"] = f"{type(exc).__name__}: {exc}"
        rec["state"] = "not_retrieved"
    rec["elapsed_s"] = round(time.time() - t0, 2)
    return rec


def _slim(rec: dict, keep_chars: int = 20000) -> dict:
    """Store the response, bounded, with the truncation MARKED rather than silent."""
    out = dict(rec)
    txt = out.get("text")
    if txt is not None and len(txt) > keep_chars:
        out["text"] = txt[:keep_chars]
        out["text_truncated_at_chars"] = keep_chars
        out["text_full_len"] = len(txt)
    return out


# ───────────────────────────────────────────────────────────────────────────────────────────────
# the ENO3 NBRE coordinates, derived from the committed motif scan — never typed
# ───────────────────────────────────────────────────────────────────────────────────────────────

def load_nbre_sites(gene: str = "ENO3", artifact: str = MOTIF_SCAN_ARTIFACT) -> dict:
    """Derive genomic NBRE intervals for `gene` from the committed motif-scan artifact.

    The scan stores, per focus gene: `assembly`, `chr`, `tss`, `window` = [start, end] and, per
    hit, `pos` (0-based offset into the window) and `offset_from_tss`.

    ⚠ STRAND IS DERIVED, NOT ASSUMED. The scan is strand-aware, so for a + strand gene the window
    is [tss - up, tss + down] and for a - strand gene it is [tss - down, tss + up]. Which one it
    is can be read off the window itself, and the derivation below is checked against the
    artifact's own `offset_from_tss` for every hit — a mismatch raises rather than emits a
    coordinate nobody verified.
    """
    with open(artifact, "r", encoding="utf-8") as fh:
        scan = json.load(fh)
    part1 = scan["part_1_nbre_scan"]
    win = part1["_window"]
    up, down = int(win["upstream_of_tss"]), int(win["downstream_of_tss"])
    g = part1["focus_genes"][gene]
    tss, w0, w1 = int(g["tss"]), int(g["window"][0]), int(g["window"][1])

    if (w0, w1) == (tss - up, tss + down):
        strand = "+"
    elif (w0, w1) == (tss - down, tss + up):
        strand = "-"
    else:
        raise AssertionError(
            f"{gene}: window {w0}-{w1} matches neither strand orientation of a "
            f"-{up}/+{down} window around TSS {tss}; refusing to guess a strand")

    sites = []
    for hit in g["nbre_exact"]["hits"]:
        pos = int(hit["pos"])
        start = w0 + pos                       # 0-based, half-open [start, end)
        end = start + NBRE_LEN
        # ⛔ THE ARTIFACT'S `offset_from_tss` IS A GENOMIC DIFFERENCE, NOT A STRAND-ORIENTED ONE,
        # and the first version of this check assumed the opposite. Measured against the committed
        # scan: KDR sits on the minus strand (its window is [tss-15000, tss+10000], the mirror of
        # ENO3's), and its hit at window offset 168 is recorded as `offset_from_tss: -14832` —
        # which is `(w0 + 168) - tss`, i.e. simply "14,832 bp lower in genomic coordinates". Under
        # a strand-oriented convention it would have been +14832, because a lower coordinate is
        # DOWNSTREAM of a minus-strand TSS. So the WINDOW is strand-aware (upstream 10 kb,
        # downstream 15 kb, mirrored for minus-strand genes) while the OFFSET is not. Both facts
        # are load-bearing and neither was written down anywhere; this check is what pins them.
        derived_offset = start - tss
        if derived_offset != int(hit["offset_from_tss"]):
            raise AssertionError(
                f"{gene}: derived offset_from_tss {derived_offset} != artifact's "
                f"{hit['offset_from_tss']} for pos {pos}; the coordinate derivation is wrong")
        sites.append({
            "chrom": f"chr{g['chr']}",
            "start": start,
            "end": end,
            "strand_of_motif": hit["strand"],
            "offset_from_tss": int(hit["offset_from_tss"]),
        })
    return {
        "gene": gene,
        "assembly": g["assembly"],
        "ensembl_id": g["ensembl_id"],
        "chrom": f"chr{g['chr']}",
        "tss": tss,
        "gene_strand_derived": strand,
        "window": [w0, w1],
        "window_spec": {"upstream_of_tss": up, "downstream_of_tss": down},
        "n_exact_nbre": int(g["nbre_exact"]["n"]),
        "sites": sites,
        "_source": os.path.relpath(artifact, REPO),
        "_source_note": (
            "one home for these coordinates: the committed output of the same NBRE scan the "
            "manuscript's §3.10 and SI §S6 report. Not re-typed here."),
    }


# ───────────────────────────────────────────────────────────────────────────────────────────────
# recon
# ───────────────────────────────────────────────────────────────────────────────────────────────

_HREF = re.compile(r'href="([^"?][^"]*)"')


def _dir_listing(rec: dict) -> list:
    if rec.get("state") != "ok" or not rec.get("text"):
        return []
    names = [h for h in _HREF.findall(rec["text"]) if not h.startswith("/")]
    return sorted({n for n in names if n not in ("../",)})


def _parse_soft(text: str) -> list:
    """Split a GEO SOFT text dump into per-sample dicts of the fields we care about."""
    samples, cur = [], None
    for line in (text or "").splitlines():
        if line.startswith("^SAMPLE"):
            if cur:
                samples.append(cur)
            cur = {"gsm": line.split("=", 1)[1].strip() if "=" in line else None}
        elif cur is not None and line.startswith("!Sample_"):
            k, _, v = line[1:].partition(" = ")
            cur.setdefault(k, []).append(v.strip())
    if cur:
        samples.append(cur)
    return samples


BUILD_TOKENS = [
    ("hg38", re.compile(r"\bhg38\b", re.I)),
    ("GRCh38", re.compile(r"\bGRCh38\b", re.I)),
    ("hg19", re.compile(r"\bhg19\b", re.I)),
    ("GRCh37", re.compile(r"\bGRCh37\b", re.I)),
    ("hg18", re.compile(r"\bhg18\b", re.I)),
]


def scan_for_build(text: str) -> dict:
    """Count every genome-build token in a blob. A COUNT, not a verdict — the caller decides."""
    return {name: len(rx.findall(text or "")) for name, rx in BUILD_TOKENS}


def run_recon(budget_s: float = DEFAULT_BUDGET_S) -> dict:
    budget = Budget(budget_s)
    fetches: dict = {}

    def go(name: str, url: str, **kw) -> dict:
        rec = fetch(url, budget, **kw)
        fetches[name] = _slim(rec)
        print(f"  [{rec['state']:>16}] http={rec['http']} {rec['bytes']:>9}B  {name}")
        return rec

    print(f"== recon {SERIES} ==  budget {budget_s:.0f}s")

    # (a) the GEO SERIES record + its supplementary directory
    series_soft = go(
        "geo_series_soft",
        f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={SERIES}&targ=self&form=text&view=brief")
    series_suppl = go(
        "geo_series_suppl_dir",
        f"https://ftp.ncbi.nlm.nih.gov/geo/series/{SERIES[:-3]}nnn/{SERIES}/suppl/")

    # (b) every SAMPLE's SOFT record — this is where !Sample_data_processing declares the build
    gsm_soft = go(
        "geo_all_samples_soft",
        f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={SERIES}&targ=gsm&form=text&view=brief",
        max_bytes=12_000_000)

    samples = _parse_soft(gsm_soft.get("text") or "")
    sample_rows = []
    for s in samples:
        sample_rows.append({
            "gsm": s.get("gsm"),
            "title": (s.get("Sample_title") or [None])[0],
            "organism": (s.get("Sample_organism_ch1") or [None])[0],
            "library_strategy": (s.get("Sample_library_strategy") or [None])[0],
            "instrument": (s.get("Sample_instrument_model") or [None])[0],
            "supplementary_file": s.get("Sample_supplementary_file_1")
                                  or s.get("Sample_supplementary_file") or [],
            "data_processing": s.get("Sample_data_processing") or [],
            "genome_build_field": s.get("Sample_data_processing") or [],
        })

    # (c) the authors' analysis repository — a differential-peak table often lives here
    go("github_author_repo_tree",
       f"https://api.github.com/repos/{AUTHOR_REPO}/git/trees/HEAD?recursive=1",
       headers={"Accept": "application/vnd.github+json"})

    # (d) the preprint's supplementary media list
    go("biorxiv_preprint_detail",
       f"https://api.biorxiv.org/details/biorxiv/{PREPRINT_DOI}")
    go("europepmc_suppfiles_probe",
       f"https://www.ebi.ac.uk/europepmc/webservices/rest/search"
       f"?query=EXT_ID:{SERIES_PMID}&resultType=core&format=json")

    # ── the per-sample supplementary directories: this is the file-level ground truth ──
    gsm_ids = [r["gsm"] for r in sample_rows if r.get("gsm")]
    per_gsm_dirs = {}
    for gsm in gsm_ids:
        if budget.exhausted():
            per_gsm_dirs[gsm] = {"state": "budget_exhausted"}
            continue
        url = f"https://ftp.ncbi.nlm.nih.gov/geo/samples/{gsm[:-3]}nnn/{gsm}/suppl/"
        rec = fetch(url, budget)
        per_gsm_dirs[gsm] = {"state": rec["state"], "http": rec["http"],
                             "files": _dir_listing(rec)}
        print(f"  [{rec['state']:>16}] http={rec['http']}  {gsm}: "
              f"{len(per_gsm_dirs[gsm]['files'])} file(s)")

    series_files = _dir_listing(series_suppl)

    # ── the build question, answered from the deposit's own words ──
    # ⛔ THIS LINE WAS `"\n".join(text)` AND THAT IS A REAL BUG, CAUGHT BY READING THE OUTPUT
    # (run 31276157603). `str.join` over a STRING interleaves the separator between every
    # CHARACTER, so `hg38` became `h\ng\n3\n8` and every `\bhg38\b` count came back 0 — while the
    # `data_processing_lines` printed beside it said `Assembly: hg38` in plain text. A scanner that
    # reports all zeros over a blob that visibly contains the token is fail-quiet: had the
    # per-line dump not been in the same artifact, "no build token found" would have read as "the
    # deposit does not declare a build". The tokens are now counted over the raw text.
    build_counts = scan_for_build(gsm_soft.get("text") or "")
    processing_lines = sorted({ln for r in sample_rows for ln in r["data_processing"]})

    # ── is there anything that could BE a peak call? ──
    all_deposited = sorted(set(series_files) | {f for d in per_gsm_dirs.values()
                                                for f in d.get("files", [])})
    peakish = [f for f in all_deposited
               if re.search(r"(peak|narrowPeak|broadPeak|bed(\.gz)?$|differential|da_|matrix)",
                            f, re.I)]

    out = {
        "_what": (f"Recon of {SERIES}: exactly what is deposited, on which genome build, and "
                  f"whether any per-fusion peak call exists to intersect."),
        "_question": ("Do EWSR1-NR4A3's differentially accessible peaks in GSE243553 overlap the "
                      "ENO3 NBRE sites reported by the manuscript's §3.10 motif scan?"),
        "_constraints_that_travel_with_every_result": [
            "HEK293T is not EMC chromatin, and ATAC accessibility is not protein binding. An open "
            "peak says a region became accessible in an engineered cell line ectopically "
            "expressing the fusion; it does not say the fusion binds there, and it says nothing "
            "directly about EMC tumour material.",
            "ENO3 is this manuscript's own designated POSITIVE CONTROL (§2.4). A hit VALIDATES "
            "THE INSTRUMENT and must never be written as an unexpected discovery.",
        ],
        "_no_claim": ("Retrieval and intersection only. Nothing here is an efficacy, selectivity, "
                      "safety, therapeutic-window or clinical-readiness statement about any agent, "
                      "target or gene."),
        "series": SERIES,
        "pmid": SERIES_PMID,
        "pmcid": SERIES_PMCID,
        "preprint_doi": PREPRINT_DOI,
        "author_repo": AUTHOR_REPO,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "budget_s": budget_s,
        "budget_left_s": round(budget.left(), 1),
        "eno3_nbre_sites": load_nbre_sites("ENO3"),
        "n_samples_parsed": len(sample_rows),
        "samples": sample_rows,
        "series_supplementary_files": series_files,
        "per_sample_supplementary_files": per_gsm_dirs,
        "all_deposited_filenames": all_deposited,
        "filenames_matching_a_peak_call_pattern": peakish,
        "deposit_supports_a_peak_overlap": bool(peakish),
        "genome_build": {
            "_how_established": ("token counts over every !Sample_* line of the series' own SOFT "
                                 "records — the deposit's own words, not an assumption"),
            "token_counts": build_counts,
            "data_processing_lines": processing_lines,
        },
        "fetches": fetches,
        "_absent_reading_rule": ("every fetch carries its HTTP status; a non-200 is recorded as "
                                 "`not_retrieved` and NEVER as an empty result (CLAUDE.md §4)."),
    }
    return out


# ───────────────────────────────────────────────────────────────────────────────────────────────
# STAGE 2 — THE ARMS, MEASURED; THE FILE SIZES, MEASURED; AND THE LAST TWO PLACES A PEAK
# TABLE COULD LIVE
# ───────────────────────────────────────────────────────────────────────────────────────────────
#
# Recon settled that GEO holds fragments + a barcode->variant map and NO peak call. Three things
# follow, all of them $0, and all of them needed before "the deposit does not support the
# analysis" is allowed to be the answer:
#
#   (1) THE SIZE MUST BE MEASURED, NOT REMEMBERED. "75G" appears in one FTP directory listing for
#       the bundled tar. Every per-file size is taken by HEAD here, so the statement about what a
#       re-analysis would cost is a reading rather than a recollection.
#   (2) THE ARMS MUST BE READ FROM THE DATA. The cistrome note quotes the paper's nuclei counts
#       (112 for EWSR1-NR4A3, 503 for the reciprocal) and says explicitly that the association
#       files "have not been opened". They are small. Opening them turns "the library contains
#       four NR4A3 fusions and two controls" from a quotation into a measurement.
#       ⚠ AND THE TWO NUMBERS ARE NOT THE SAME QUANTITY. What is counted here is BARCODES
#       ASSIGNED TO A VARIANT in the deposited association files. The paper's figure is nuclei
#       surviving ArchR QC. A barcode count that differs from 112 is not a contradiction and must
#       never be written as one.
#   (3) A PEAK TABLE IS FAR MORE OFTEN A PAPER SUPPLEMENT THAN A GEO FILE. Europe PMC's
#       supplementaryFiles endpoint and the bioRxiv supplementary-material page are the two
#       remaining places it could be, and both are free.

SUPPL_OUT = os.path.join(HERE, "gse243553-eno3-overlap-arms.json")

# The library members this manuscript's argument turns on. Matching is SUBSTRING and
# case-insensitive over the association file's variant column, and every distinct raw label that
# matched is recorded, so a rename in the deposit shows up as a label rather than as a silent zero.
NR4A3_ARMS = {
    "EWSR1-NR4A3": ["ewsr1-nr4a3", "ewsr1_nr4a3", "ewsr1nr4a3"],
    "TAF15-NR4A3": ["taf15-nr4a3", "taf15_nr4a3"],
    "TCF12-NR4A3": ["tcf12-nr4a3", "tcf12_nr4a3"],
    "TFG-NR4A3": ["tfg-nr4a3", "tfg_nr4a3"],
    "NR4A3-EWSR1 (reciprocal control)": ["nr4a3-ewsr1", "nr4a3_ewsr1"],
}


def _match_arm(label: str) -> str | None:
    low = (label or "").strip().lower()
    for arm, pats in NR4A3_ARMS.items():
        if any(p in low for p in pats):
            return arm
    # full-length wild-type NR4A3: NR4A3 with no partner on either side
    if re.fullmatch(r"[^a-z0-9]*nr4a3[^a-z0-9]*", low):
        return "NR4A3 (full-length wild type control)"
    return None


def head_size(url: str, budget: Budget) -> dict:
    """Content-Length only. A size we could not read is `None`, never 0."""
    rec = {"url": url, "http": None, "content_length": None, "state": None, "error": None}
    if budget.exhausted():
        rec["state"] = "budget_exhausted"
        return rec
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as fh:
            rec["http"] = fh.status
            cl = fh.headers.get("Content-Length")
            rec["content_length"] = int(cl) if cl and cl.isdigit() else None
            rec["state"] = "ok"
    except Exception as exc:                    # noqa: BLE001
        rec["error"] = f"{type(exc).__name__}: {exc}"
        rec["state"] = "not_retrieved"
    return rec


def run_arms(budget_s: float = DEFAULT_BUDGET_S) -> dict:
    if not os.path.exists(RECON_OUT):
        raise SystemExit(f"{RECON_OUT} missing — run --stage recon --fetch first")
    with open(RECON_OUT, "r", encoding="utf-8") as fh:
        recon = json.load(fh)

    budget = Budget(budget_s)
    fetches: dict = {}
    print(f"== arms {SERIES} ==  budget {budget_s:.0f}s")

    # ── (1) every deposited file's size, measured ──
    sizes = {}
    for gsm, r in recon["per_sample_supplementary_files"].items():
        for fn in r.get("files", []):
            if not fn.endswith(".gz"):
                continue
            url = f"https://ftp.ncbi.nlm.nih.gov/geo/samples/{gsm[:-3]}nnn/{gsm}/suppl/{fn}"
            sizes[fn] = {**head_size(url, budget), "gsm": gsm}
            print(f"  size {fn}: {sizes[fn]['content_length']}")

    # ── (2) the arms, read from the association files ──
    assoc_files = sorted(fn for fn in sizes if "associations" in fn)
    per_file, label_counts, header_seen = {}, {}, {}
    all_variants: set = set()
    total_rows = 0
    for fn in assoc_files:
        gsm = sizes[fn]["gsm"]
        url = f"https://ftp.ncbi.nlm.nih.gov/geo/samples/{gsm[:-3]}nnn/{gsm}/suppl/{fn}"
        rec = fetch(url, budget, timeout=180, max_bytes=120_000_000)
        fetches[f"assoc::{fn}"] = {k: v for k, v in _slim(rec, 400).items()}
        if rec["state"] != "ok" or not rec.get("text"):
            per_file[fn] = {"state": rec["state"], "error": rec.get("error")}
            print(f"  [{rec['state']}] {fn}")
            continue
        lines = rec["text"].splitlines()
        header = lines[0] if lines else ""
        header_seen[fn] = header
        # find the column that carries the variant label: the one whose values match an arm
        rows = [ln.split(",") for ln in lines[1:] if ln.strip()]
        ncol = max((len(r) for r in rows), default=0)
        best_col, best_hits = None, -1
        for c in range(ncol):
            hits = sum(1 for r in rows if len(r) > c and _match_arm(r[c]))
            if hits > best_hits:
                best_col, best_hits = c, hits
        counts: dict = {}
        raw_labels: dict = {}
        library: set = set()
        for r in rows:
            if best_col is None or len(r) <= best_col:
                continue
            raw = r[best_col].strip().strip('"')
            if raw:
                library.add(raw)
            arm = _match_arm(raw)
            if arm:
                counts[arm] = counts.get(arm, 0) + 1
                raw_labels.setdefault(arm, set()).add(raw)
        per_file[fn] = {
            "state": "ok",
            "header": header,
            "n_rows": len(rows),
            "variant_column_index": best_col,
            "variant_column_name": ([h.strip().strip('"') for h in header.split(",")][best_col]
                                    if best_col is not None
                                    and best_col < len(header.split(",")) else None),
            "n_distinct_variants": len(library),
            "arm_barcode_counts": counts,
            "raw_labels_matched": {k: sorted(v) for k, v in raw_labels.items()},
        }
        all_variants |= library
        for arm, n in counts.items():
            label_counts[arm] = label_counts.get(arm, 0) + n
        total_rows += len(rows)
        print(f"  [ok] {fn}: {len(rows)} rows, arms {counts}")

    # ── (3) the last two places a peak table could live ──
    def go(name: str, url: str, **kw) -> dict:
        rec = fetch(url, budget, **kw)
        fetches[name] = _slim(rec)
        print(f"  [{rec['state']:>16}] http={rec['http']} {rec['bytes']:>9}B  {name}")
        return rec

    go("europepmc_supplementary_files_zip",
       f"https://www.ebi.ac.uk/europepmc/webservices/rest/{SERIES_PMCID}/supplementaryFiles",
       max_bytes=60_000_000)

    # ⚠ A 429 IS NOT AN ANSWER. bioRxiv rate-limited the first attempt at this page (run
    # 31276419635) and the repository's own rule is that an NCBI/bioRxiv 429 is re-run until it
    # answers, never folded into a count as a zero. Backoff, then record whichever it was.
    for attempt, wait in ((1, 0), (2, 15), (3, 45)):
        if wait and not budget.exhausted():
            time.sleep(min(wait, max(0, budget.left())))
        r = go(f"biorxiv_supplementary_material_page_try{attempt}",
               f"https://www.biorxiv.org/content/{PREPRINT_DOI}v1.supplementary-material")
        if r["state"] == "ok":
            break

    # PMC renders supplementary materials as /articles/<PMCID>/bin/<file> links even for an
    # author-manuscript deposit, so the article page is the one place left to look.
    for host in ("https://pmc.ncbi.nlm.nih.gov/articles",
                 "https://europepmc.org/article/MED"):
        name = "pmc_article_page" if "pmc.ncbi" in host else "europepmc_article_page"
        ident = SERIES_PMCID if "pmc.ncbi" in host else SERIES_PMID
        r = go(name, f"{host}/{ident}/", max_bytes=6_000_000)
        if r["state"] == "ok" and r.get("text"):
            fetches[name + "::supplement_links"] = sorted({
                m for m in re.findall(r'[^"\']*(?:/bin/[^"\']+|supplement[^"\']*\.(?:xlsx|xls|csv|zip|pdf|txt|bed[^"\']*))',
                                      r["text"], re.I)})[:200]

    # the Europe PMC endpoint returns a ZIP; list its members with stdlib only
    suppl_zip_members = None
    z = fetches.get("europepmc_supplementary_files_zip") or {}
    if z.get("state") == "ok" and (z.get("http") == 200):
        try:
            import zipfile
            raw = fetch(
                f"https://www.ebi.ac.uk/europepmc/webservices/rest/{SERIES_PMCID}"
                f"/supplementaryFiles", budget, max_bytes=60_000_000)
            if raw["state"] == "ok":
                data = raw["text"].encode("utf-8", "surrogateescape")
                with zipfile.ZipFile(io.BytesIO(data)) as zf:
                    suppl_zip_members = [{"name": i.filename, "size": i.file_size}
                                         for i in zf.infolist()]
        except Exception as exc:                # noqa: BLE001
            suppl_zip_members = {"error": f"{type(exc).__name__}: {exc}"}

    total_bytes = sum(v["content_length"] or 0 for v in sizes.values())
    frag_bytes = sum(v["content_length"] or 0 for k, v in sizes.items() if "fragments" in k)

    out = {
        "_what": ("Stage 2: every deposited file's size MEASURED, the NR4A3 arms read from the "
                  "deposited barcode->variant maps rather than from the paper's prose, and the "
                  "two remaining places a differential-peak table could live."),
        "_constraints_that_travel_with_every_result":
            recon["_constraints_that_travel_with_every_result"],
        "_no_claim": recon["_no_claim"],
        "series": SERIES,
        "pmid": SERIES_PMID,
        "pmcid": SERIES_PMCID,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "file_sizes_bytes": sizes,
        "total_deposited_bytes": total_bytes,
        "fragment_bytes": frag_bytes,
        "arms": {
            "_what_is_counted": (
                "BARCODES ASSIGNED TO A VARIANT in the deposited *_merged_associations.csv.gz "
                "files, summed over the 12 technical-replicate samples."),
            "⛔_not_the_same_quantity_as_the_papers_nuclei_count": (
                "The paper reports nuclei that survive ArchR QC (112 for EWSR1-NR4A3, 503 for the "
                "reciprocal NR4A3-EWSR1). An association file is the assignment BEFORE that "
                "filtering, and a barcode can be assigned and then dropped. A different number "
                "here is not a contradiction of the paper and must never be written as one."),
            "barcode_counts_by_arm": label_counts,
            "n_barcode_rows_total": total_rows,
            "n_distinct_variants_in_library": len(all_variants),
            "library_variant_labels": sorted(all_variants),
            "per_file": per_file,
            "headers_seen": header_seen,
        },
        "supplementary_table_search": {
            "europepmc_zip_members": suppl_zip_members,
            "_why": ("a differential-peak table is far more often a paper supplement than a GEO "
                     "file; this is the last place one could be, and it is free to ask"),
        },
        "fetches": fetches,
        "_absent_reading_rule": recon["_absent_reading_rule"],
    }
    return out


# ───────────────────────────────────────────────────────────────────────────────────────────────
# STAGE 2b — THE PAPER'S SUPPLEMENT, WHICH IS WHERE THE PEAK TABLE ACTUALLY LIVES
# ───────────────────────────────────────────────────────────────────────────────────────────────
#
# ⭐ THIS IS THE STEP THAT CHANGED THE ANSWER, AND IT IS WORTH RECORDING WHY IT WAS NEARLY MISSED.
# GEO's deposit is 80.1 GB of fragments and no peak call, and it would have been easy to stop
# there and report "the deposit does not support the analysis". Europe PMC's supplementaryFiles
# endpoint agreed, in a way that reads like an absence and is not one: HTTP 200 carrying
# `Article with id PMC13105821 is not open access one`. bioRxiv answered 429 three times.
#
# But the article IS in PMC as an author manuscript (NIHMS2166785), and PMC serves author-
# manuscript supplements from `/articles/instance/<id>/bin/`. Scraping the article page for that
# path found six files, two of them `Supplementary_Data_*.zip`. ⛔ THREE "NO" ANSWERS FROM THREE
# SERVICES DID NOT MEAN THE DATA WAS ABSENT — they meant three doors were shut. CLAUDE.md §4.

SUPPL2_OUT = os.path.join(HERE, "gse243553-eno3-overlap-supplement.json")
PMC_BIN = "https://pmc.ncbi.nlm.nih.gov/articles/instance/13105821/bin/"

# Column names that make a table a genomic interval table. Matching is case-insensitive.
PEAKISH_COLS = ("chr", "chrom", "seqnames", "start", "end", "peak", "idx", "log2fc",
                "fdr", "fusion", "variant")


def _xlsx_overview(raw: bytes, max_rows: int = 6) -> dict:
    """Sheet names, the header row and a few data rows of an .xlsx — stdlib only.

    An .xlsx is a zip of XML, so this needs no third-party reader. It reads the shared-string
    table and then the first `max_rows` rows of every sheet.
    """
    import xml.etree.ElementTree as ET
    import zipfile
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    out = {"sheets": {}}
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = zf.namelist()
        shared = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall(f"{ns}si"):
                shared.append("".join(t.text or "" for t in si.iter(f"{ns}t")))
        titles = []
        if "xl/workbook.xml" in names:
            wb = ET.fromstring(zf.read("xl/workbook.xml"))
            titles = [s.get("name") for s in wb.iter(f"{ns}sheet")]
        sheets = sorted(n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        for i, sn in enumerate(sheets):
            root = ET.fromstring(zf.read(sn))
            rows, n_rows = [], 0
            for r in root.iter(f"{ns}row"):
                n_rows += 1
                if len(rows) >= max_rows:
                    continue
                vals = []
                for c in r.findall(f"{ns}c"):
                    v = c.find(f"{ns}v")
                    txt = v.text if v is not None else None
                    if c.get("t") == "s" and txt is not None and txt.isdigit():
                        txt = shared[int(txt)] if int(txt) < len(shared) else txt
                    vals.append(txt)
                rows.append(vals)
            out["sheets"][titles[i] if i < len(titles) else sn] = {
                "n_rows": n_rows, "first_rows": rows}
    return out


def run_suppl(budget_s: float = DEFAULT_BUDGET_S) -> dict:
    import zipfile
    budget = Budget(budget_s)
    files = ["NIHMS2166785-supplement-Supplementary_Data_1.zip",
             "NIHMS2166785-supplement-Supplementary_Data_2.zip",
             "NIHMS2166785-supplement-Supplementary_Table_1.xlsx",
             "NIHMS2166785-supplement-Supplementary_Table_2.xlsx",
             "NIHMS2166785-supplement-Supplementary_Table_3.xlsx"]
    got, saved = {}, {}
    cache = os.environ.get("GSE243553_SUPPL_DIR", "/tmp/gse243553_suppl")
    os.makedirs(cache, exist_ok=True)

    for fn in files:
        url = PMC_BIN + fn
        rec = {"url": url, "http": None, "bytes": 0, "state": None, "error": None}
        if budget.exhausted():
            rec["state"] = "budget_exhausted"
            got[fn] = rec
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=300) as fh:
                rec["http"] = fh.status
                raw = fh.read(400_000_000)
            rec["bytes"] = len(raw)
            rec["state"] = "ok"
            path = os.path.join(cache, fn)
            with open(path, "wb") as out_fh:
                out_fh.write(raw)
            saved[fn] = path
        except urllib.error.HTTPError as exc:
            rec["http"], rec["error"], rec["state"] = exc.code, str(exc), "not_retrieved"
        except Exception as exc:                # noqa: BLE001
            rec["error"], rec["state"] = f"{type(exc).__name__}: {exc}", "not_retrieved"
        got[fn] = rec
        print(f"  [{rec['state']:>16}] http={rec['http']} {rec['bytes']:>10}B  {fn}")

    contents: dict = {}
    for fn, path in saved.items():
        with open(path, "rb") as fh:
            raw = fh.read()
        try:
            if fn.endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                    members = [{"name": i.filename, "size": i.file_size}
                               for i in zf.infolist()]
                    contents[fn] = {"kind": "zip", "members": members}
                    # peek at every member small enough to peek at
                    peek = {}
                    for i in zf.infolist():
                        if i.file_size > 400_000_000 or i.is_dir():
                            continue
                        with zf.open(i) as mf:
                            head = mf.read(4096)
                        if i.filename.endswith(".gz"):
                            try:
                                head = gzip.GzipFile(fileobj=io.BytesIO(head)).read(4096)
                            except OSError:
                                pass
                        peek[i.filename] = head.decode("utf-8", "replace")[:600]
                    contents[fn]["first_bytes"] = peek
            else:
                contents[fn] = {"kind": "xlsx", **_xlsx_overview(raw)}
        except Exception as exc:                # noqa: BLE001
            contents[fn] = {"kind": "unreadable", "error": f"{type(exc).__name__}: {exc}"}

    # which of these, if any, is a genomic interval table?
    verdict = {}
    for fn, c in contents.items():
        found = []
        if c.get("kind") == "zip":
            for name, head in (c.get("first_bytes") or {}).items():
                first = (head.splitlines() or [""])[0].lower()
                cols = [p for p in PEAKISH_COLS if p in first]
                if len(cols) >= 2:
                    found.append({"member": name, "matched_columns": cols,
                                  "header": (head.splitlines() or [""])[0][:300]})
        elif c.get("kind") == "xlsx":
            for sheet, s in (c.get("sheets") or {}).items():
                hdr = " ".join(str(x or "") for x in (s.get("first_rows") or [[]])[0]).lower()
                cols = [p for p in PEAKISH_COLS if p in hdr]
                if len(cols) >= 2:
                    found.append({"sheet": sheet, "n_rows": s.get("n_rows"),
                                  "matched_columns": cols, "header": hdr[:300]})
        verdict[fn] = found

    return {
        "_what": ("The paper's supplementary files, from PMC's author-manuscript store — the "
                  "place a differential-peak table actually lives when GEO deposits only raw "
                  "fragments."),
        "_why_this_was_nearly_missed": (
            "Europe PMC's supplementaryFiles endpoint answers HTTP 200 with `Article with id "
            "PMC13105821 is not open access one`, and bioRxiv answered 429 three times. Neither "
            "is an absence. PMC serves author-manuscript supplements from "
            "/articles/instance/<id>/bin/, and scraping the article page for that path found "
            "six files."),
        "series": SERIES, "pmid": SERIES_PMID, "pmcid": SERIES_PMCID,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fetches": got,
        "contents": contents,
        "genomic_interval_tables_found": verdict,
        "_absent_reading_rule": ("every fetch carries its HTTP status; a non-200 is "
                                 "`not_retrieved`, never an empty result"),
    }


# ───────────────────────────────────────────────────────────────────────────────────────────────
# STAGE 3 — THE FRAGMENT READ. WHAT THE DEPOSIT *CAN* ANSWER.
# ───────────────────────────────────────────────────────────────────────────────────────────────
#
# ⛔ READ THIS BEFORE READING ANY NUMBER THIS STAGE PRODUCES.
#
# THE QUESTION AS POSED — "do EWSR1-NR4A3's differentially accessible PEAKS overlap the ENO3 NBRE
# sites" — CANNOT BE ANSWERED FROM THIS DEPOSIT, and stage 1 is why: GEO holds 12 fragment files
# and 12 barcode->variant maps and NOT ONE PEAK CALL. Re-calling peaks here would be a different
# experiment wearing this one's name.
#
# What the deposit CAN answer is strictly weaker and is stated as such everywhere it appears:
# **per-arm Tn5 insertion density at the NBRE coordinates, against two nulls.** That is
# accessibility measured directly from fragments rather than through the authors' peak caller. It
# is a real reading and it is NOT a peak overlap; the artifact's own field names say so.
#
# THREE THINGS MAKE IT WORTH TAKING ANYWAY:
#   * the arms carry their own controls — full-length wild-type NR4A3 and the reciprocal
#     NR4A3-EWSR1, both of which the paper reports at ZERO peaks. A signal that appears in the
#     fusion arm and not in those two is worth far more than a signal alone;
#   * the calibration is already built. `emc-ret-cistrome-inputs.json` carries the 198-gene
#     background panel this project assembled for an unrelated question, with hg38 coordinates.
#     The same panel calibrates §3.11's Table 9, so this read and that one are commensurable;
#   * it costs $0.
#
# ⚠ AND IT MAY WELL COME BACK UNINFORMATIVE. EWSR1-NR4A3 is 312 assigned barcodes. The repository's
# own rule (`nr4a3-fusion-targets-occupancy.json._uninformative_rule`) is that an instrument which
# recovers (almost) no ARBITRARY gene cannot fail to recover a chosen one, so its silence is an
# ABSENT READING and is never counted as evidence of non-occupancy. That rule is applied here,
# with the same thresholds, and an arm that fails it emits `informative: false` and NO verdict.

FRAG_OUT = os.path.join(HERE, "gse243553-eno3-overlap.json")
CISTROME_INPUTS = os.path.join(HERE, "emc-ret-cistrome-inputs.json")

SEED = 20260808
FLANK_BP = 250          # see `_why_this_flank` in the artifact
FOCUS_GENES = ("RET", "ENO3", "PPARG", "SEMA3C", "NR4A3", "NR4A1", "VEGFA", "KDR")

# Same thresholds as the occupancy artifact, so the two reads are graded on one rule.
MIN_PANEL_GENES = 50
MIN_PANEL_HIT_RATE = 0.02


def panel_windows(upstream: int, downstream: int) -> dict:
    """The 198-gene background panel's promoter windows, hg38, strand-aware.

    ⭐ THE PANEL IS NOT CHOSEN HERE AND COULD NOT HAVE BEEN. It was assembled for the ATR/DDR
    concept universe, long before this question existed, and it is the same panel §3.11's Table 9
    calibrates against — which is what makes a fragment reading and a peak reading commensurable.
    """
    with open(CISTROME_INPUTS, "r", encoding="utf-8") as fh:
        genes = json.load(fh)["genes"]["hg38"]
    out = {}
    for sym, g in genes.items():
        if sym in FOCUS_GENES:
            continue
        if not g.get("chrom") or g.get("start") is None:
            continue
        strand = int(g.get("strand", 1))
        tss = int(g["start"]) if strand >= 0 else int(g["end"])
        w = ((tss - upstream, tss + downstream) if strand >= 0
             else (tss - downstream, tss + upstream))
        out[sym] = {"chrom": g["chrom"], "start": w[0], "end": w[1], "tss": tss,
                    "strand": strand}
    return out


class WindowIndex:
    """Interval lookup over a few hundred windows. Half-open [start, end) throughout.

    ⚠ HALF-OPEN, EVERYWHERE. An inclusive/half-open mix is the classic silent off-by-one in
    exactly this kind of intersection, and the selftest below pins both boundaries.
    """

    def __init__(self):
        self._by_chrom: dict = {}

    def add(self, chrom: str, start: int, end: int, key: str) -> None:
        self._by_chrom.setdefault(chrom, []).append((int(start), int(end), key))

    def finalize(self) -> None:
        import bisect                                                  # noqa: F401
        for c in self._by_chrom:
            self._by_chrom[c].sort()

    def hits(self, chrom: str, pos: int):
        """Every window containing `pos` (half-open)."""
        ivs = self._by_chrom.get(chrom)
        if not ivs:
            return ()
        return tuple(k for s, e, k in ivs if s <= pos < e)


def _norm_chrom(c: str) -> str:
    c = c.strip()
    return c if c.startswith("chr") else "chr" + c


def run_frag(samples: int, budget_s: float, flank: int = FLANK_BP,
             probe_bytes: int = 0) -> dict:
    """Stream fragment files, keep only arm barcodes, and count Tn5 insertions per window.

    `probe_bytes > 0` reads only that many bytes of the FIRST file — the shakeout that proves the
    barcode join before an 80 GB read is attempted (CLAUDE.md §6: smoke -> one real leg -> fleet).
    """
    import bisect
    import random
    import subprocess

    if not os.path.exists(SUPPL_OUT):
        raise SystemExit(f"{SUPPL_OUT} missing — run --stage arms --fetch first")
    with open(SUPPL_OUT, "r", encoding="utf-8") as fh:
        arms_art = json.load(fh)

    budget = Budget(budget_s)
    eno3 = load_nbre_sites("ENO3")
    up = eno3["window_spec"]["upstream_of_tss"]
    down = eno3["window_spec"]["downstream_of_tss"]
    panel = panel_windows(up, down)

    # ── the windows we count into ──
    idx = WindowIndex()
    for i, s in enumerate(eno3["sites"]):
        idx.add(s["chrom"], s["start"] - flank, s["end"] + flank, f"ENO3_NBRE_{i + 1}")
    idx.add(eno3["chrom"], eno3["window"][0], eno3["window"][1], "ENO3_PROMOTER_WINDOW")
    for sym, w in panel.items():
        idx.add(w["chrom"], w["start"], w["end"], f"PANEL::{sym}")
    idx.finalize()

    # ── barcode -> arm, per sample, from the association files ──
    sizes = arms_art["file_sizes_bytes"]
    frag_files = sorted((fn for fn in sizes if "fragments" in fn),
                        key=lambda f: int(re.search(r"fragments-(\d+)", f).group(1)))
    assoc_by_n = {}
    for fn in sizes:
        m = re.search(r"Sample(\d+)_merged_associations", fn)
        if m:
            assoc_by_n[int(m.group(1))] = fn

    counts: dict = {}          # arm -> key -> insertions
    arm_depth: dict = {}       # arm -> total insertions retained (genome-wide, arm barcodes only)
    per_sample_diag = []
    join_examples = {}

    for frag_fn in frag_files[:samples]:
        n = int(re.search(r"fragments-(\d+)", frag_fn).group(1))
        assoc_fn = assoc_by_n.get(n)
        if not assoc_fn:
            per_sample_diag.append({"sample": n, "state": "no_association_file"})
            continue
        gsm_assoc = sizes[assoc_fn]["gsm"]
        gsm_frag = sizes[frag_fn]["gsm"]

        rec = fetch(f"https://ftp.ncbi.nlm.nih.gov/geo/samples/{gsm_assoc[:-3]}nnn/"
                    f"{gsm_assoc}/suppl/{assoc_fn}", budget, timeout=180,
                    max_bytes=120_000_000)
        if rec["state"] != "ok":
            per_sample_diag.append({"sample": n, "state": "assoc_" + rec["state"]})
            continue
        lines = rec["text"].splitlines()
        hdr = [h.strip().strip('"') for h in lines[0].split(",")]
        try:
            ci_cbc, ci_fus = hdr.index("CBC"), hdr.index("Fusion")
        except ValueError:
            per_sample_diag.append({"sample": n, "state": "assoc_columns_not_found",
                                    "header": hdr})
            continue
        bc2arm = {}
        for ln in lines[1:]:
            f = ln.split(",")
            if len(f) <= max(ci_cbc, ci_fus):
                continue
            arm = _match_arm(f[ci_fus].strip().strip('"'))
            if arm:
                bc2arm[f[ci_cbc].strip().strip('"')] = arm
        if not bc2arm:
            per_sample_diag.append({"sample": n, "state": "no_arm_barcodes"})
            continue

        # ── stream the fragments ──
        url = (f"https://ftp.ncbi.nlm.nih.gov/geo/samples/{gsm_frag[:-3]}nnn/"
               f"{gsm_frag}/suppl/{frag_fn}")
        bc_path = os.path.join("/tmp", f"bc_{n}.txt")
        with open(bc_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(bc2arm) + "\n")
        head = f"head -c {probe_bytes} | " if probe_bytes else ""
        # ⚠ `zcat` on a TRUNCATED gzip stream exits non-zero after emitting every complete block,
        # which is exactly what the probe wants; `|| true` keeps that from failing the pipeline.
        cmd = (f"curl -sL --max-time 5400 {url!r} | {head}"
               f"(zcat 2>/dev/null || true) | "
               f"awk -F'\\t' 'NR==FNR{{bc[$1]=1;next}} ($4 in bc)' {bc_path!r} -")
        t0 = time.time()
        n_lines = n_bad = 0
        proc = subprocess.Popen(["bash", "-o", "pipefail", "-c", cmd],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                                bufsize=1024 * 1024)
        for line in proc.stdout:
            f = line.rstrip("\n").split("\t")
            if len(f) < 4:
                n_bad += 1
                continue
            arm = bc2arm.get(f[3])
            if arm is None:
                continue
            try:
                chrom, s, e = _norm_chrom(f[0]), int(f[1]), int(f[2])
            except ValueError:
                n_bad += 1
                continue
            n_lines += 1
            arm_depth[arm] = arm_depth.get(arm, 0) + 2      # two Tn5 insertions per fragment
            for pos in (s, e - 1):
                for key in idx.hits(chrom, pos):
                    counts.setdefault(arm, {})
                    counts[arm][key] = counts[arm].get(key, 0) + 1
            if len(join_examples) < 3:
                join_examples[f[3]] = {"arm": arm, "line": line.rstrip("\n")[:120]}
        proc.wait()
        per_sample_diag.append({
            "sample": n, "state": "ok" if n_lines else "no_arm_fragments_matched",
            "gsm_fragments": gsm_frag, "gsm_associations": gsm_assoc,
            "n_arm_barcodes": len(bc2arm), "n_arm_fragments": n_lines,
            "n_unparseable_lines": n_bad, "elapsed_s": round(time.time() - t0, 1),
            "probe_bytes": probe_bytes or None,
        })
        print(f"  sample {n}: {n_lines} arm fragments from {len(bc2arm)} barcodes "
              f"in {time.time() - t0:.0f}s")
        try:
            os.unlink(bc_path)
        except OSError:
            pass

    # ── informativeness, on the repository's own rule ──
    per_arm = {}
    rng = random.Random(SEED)
    for arm, c in sorted(counts.items()):
        panel_hits = {k[7:]: v for k, v in c.items() if k.startswith("PANEL::")}
        n_panel = len(panel)
        hit_rate = len(panel_hits) / n_panel if n_panel else 0.0
        informative = (n_panel >= MIN_PANEL_GENES and hit_rate >= MIN_PANEL_HIT_RATE)
        eno3_window = c.get("ENO3_PROMOTER_WINDOW", 0)
        site_total = sum(c.get(f"ENO3_NBRE_{i + 1}", 0) for i in range(len(eno3["sites"])))
        # empirical p for the PROMOTER-WINDOW count, against the panel — the same convention and
        # the same panel as the occupancy artifact, so the two are directly comparable
        vals = [panel_hits.get(s, 0) for s in panel]
        n_ge = sum(1 for v in vals if v >= eno3_window)
        per_arm[arm] = {
            "n_arm_insertions_total": arm_depth.get(arm, 0),
            "panel": {
                "n_genes": n_panel,
                "n_genes_with_an_insertion_in_their_promoter_window": len(panel_hits),
                "fraction_with_an_insertion": round(hit_rate, 4),
            },
            "informative": informative,
            "⚠_if_not_informative": (None if informative else
                                     "this arm recovers too few ARBITRARY genes to be able to "
                                     "recover a chosen one, so its silence at ENO3 is an ABSENT "
                                     "READING and is NOT evidence of non-accessibility"),
            "ENO3": {
                "promoter_window_insertions": eno3_window,
                "nbre_site_insertions_total": site_total,
                "per_site": {f"ENO3_NBRE_{i + 1}": c.get(f"ENO3_NBRE_{i + 1}", 0)
                             for i in range(len(eno3["sites"]))},
                "empirical_p_promoter_window_vs_panel": (
                    round((n_ge + 1) / (n_panel + 1), 4) if informative and n_panel else None),
                "_p_convention": "(ge+1)/(n+1), never ge/n — it can never print a 0 the panel "
                                 "size does not support",
            },
        }

    out = {
        "_what": ("Per-arm Tn5 insertion density at the ENO3 NBRE coordinates in GSE243553, read "
                  "directly from the deposited fragments."),
        "⛔_this_is_not_a_peak_overlap": (
            "The question as posed asks whether EWSR1-NR4A3's differentially accessible PEAKS "
            "overlap these sites. GSE243553 deposits NO peak call (see the recon artifact), so "
            "that question cannot be answered from it. What is measured here is insertion "
            "density, which is weaker: it is accessibility read without the authors' peak caller, "
            "their QC, or their differential test."),
        "_constraints_that_travel_with_every_result":
            arms_art["_constraints_that_travel_with_every_result"],
        "_no_claim": arms_art["_no_claim"],
        "series": SERIES,
        "pmid": SERIES_PMID,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "genome_build": {
            "deposit": "hg38",
            "_how_established": ("the deposit's own !Sample_data_processing line reads "
                                 "`Assembly: hg38`; reads were aligned with cellranger-atac to "
                                 "hg38 (recon artifact)"),
            "nbre_coordinates": eno3["assembly"],
            "builds_agree_no_liftover_needed": True,
            "⛔_if_they_had_disagreed": ("an intersection computed across builds is meaningless; "
                                        "this field exists so the agreement is a reading rather "
                                        "than an assumption"),
        },
        "eno3_nbre_sites": eno3,
        "flank_bp": flank,
        "_why_this_flank": (
            f"±{flank} bp around each 8 bp NBRE, i.e. a {2 * flank + NBRE_LEN} bp interval. A "
            f"called ATAC peak in this assay class is a few hundred bp wide and a motif is 8 bp, "
            f"so a flank of this size asks 'is the motif inside an accessible region' at roughly "
            f"one peak width. It is a choice, it is stated, and it is fixed before any count is "
            f"read."),
        "seed": SEED,
        "samples_read": samples,
        "per_sample": per_sample_diag,
        "barcode_join_examples": join_examples,
        "per_arm": per_arm,
        "raw_counts": counts,
        "_panel_source": ("emc-ret-cistrome-inputs.json -> genes.hg38, the 198-gene background "
                          "panel assembled for the ATR/DDR concept universe and used unchanged by "
                          "§3.11's Table 9 — so this reading and that one are commensurable"),
        "_uninformative_rule": {"min_panel_genes": MIN_PANEL_GENES,
                                "min_panel_hit_rate": MIN_PANEL_HIT_RATE,
                                "_why": ("an instrument that recovers no arbitrary gene cannot "
                                         "fail to recover a chosen one")},
    }
    _ = (bisect, rng)
    return out


# ───────────────────────────────────────────────────────────────────────────────────────────────
# selftest — the arithmetic that can lie, asserted with no network
# ───────────────────────────────────────────────────────────────────────────────────────────────

def selftest() -> int:
    fails = []

    # 1. the coordinate derivation round-trips against the artifact's own offsets
    try:
        eno3 = load_nbre_sites("ENO3")
    except Exception as exc:                    # noqa: BLE001
        print(f"FAIL coordinate derivation: {exc}")
        return 1
    if eno3["n_exact_nbre"] != len(eno3["sites"]):
        fails.append(f"ENO3: n_exact_nbre={eno3['n_exact_nbre']} but {len(eno3['sites'])} sites")
    if eno3["assembly"] != "GRCh38":
        fails.append(f"ENO3 assembly is {eno3['assembly']!r}, not GRCh38 — the build handling "
                     f"below assumes the scan's declared build is read, not guessed")
    for s in eno3["sites"]:
        if s["end"] - s["start"] != NBRE_LEN:
            fails.append(f"site {s} is not {NBRE_LEN} bp")
        if not (eno3["window"][0] <= s["start"] < s["end"] <= eno3["window"][1] + 1):
            fails.append(f"site {s} falls outside the scanned window {eno3['window']}")

    # 2. every other focus gene derives too, so a strand assumption cannot hide in one gene
    for gene in ("PPARG", "SEMA3C", "RET", "VEGFA", "KDR"):
        try:
            load_nbre_sites(gene)
        except Exception as exc:                # noqa: BLE001
            fails.append(f"{gene}: {exc}")

    # 3. a non-200 must never render as an empty listing
    if _dir_listing({"state": "not_retrieved", "http": 502, "text": None}) != []:
        fails.append("_dir_listing returned content for a not_retrieved fetch")
    probe = {"state": "not_retrieved", "http": 404, "text": "<a href='peaks.bed'>"}
    if _dir_listing(probe):
        fails.append("_dir_listing parsed the body of a NON-OK response — an absent reading "
                     "would render as a reading of absence")

    # 4. the build scanner counts, it does not decide
    c = scan_for_build("aligned to hg38 using ... hg38 ... previously hg19")
    if c["hg38"] != 2 or c["hg19"] != 1:
        fails.append(f"scan_for_build mis-counted: {c}")

    # 4b. the arm matcher must separate the fusion from BOTH controls, in both orientations
    cases = {
        "EWSR1-NR4A3": "EWSR1-NR4A3",
        "ewsr1_nr4a3": "EWSR1-NR4A3",
        "NR4A3-EWSR1": "NR4A3-EWSR1 (reciprocal control)",
        "TAF15-NR4A3": "TAF15-NR4A3",
        "TCF12-NR4A3": "TCF12-NR4A3",
        "TFG-NR4A3": "TFG-NR4A3",
        "NR4A3": "NR4A3 (full-length wild type control)",
        " nr4a3 ": "NR4A3 (full-length wild type control)",
        "EWSR1-FLI1": None,
        "NR4A1": None,
        "": None,
    }
    for raw, want in cases.items():
        got = _match_arm(raw)
        if got != want:
            fails.append(f"_match_arm({raw!r}) -> {got!r}, expected {want!r}")
    # ⛔ THE ORIENTATION TEST IS THE ONE THAT MATTERS. `EWSR1-NR4A3` and `NR4A3-EWSR1` are the
    # fusion and its ZERO-PEAK reciprocal control; a substring matcher that collapsed them would
    # merge the arm with its own negative control and make any result meaningless.
    if _match_arm("NR4A3-EWSR1") == _match_arm("EWSR1-NR4A3"):
        fails.append("the fusion and its reciprocal control match the same arm")

    # 5. SOFT parsing keeps one record per ^SAMPLE
    soft = ("^SAMPLE = GSM1\n!Sample_title = a\n!Sample_data_processing = hg38\n"
            "^SAMPLE = GSM2\n!Sample_title = b\n")
    ss = _parse_soft(soft)
    if [s["gsm"] for s in ss] != ["GSM1", "GSM2"]:
        fails.append(f"_parse_soft: {ss}")

    for f in fails:
        print("FAIL:", f)
    if not fails:
        print(f"selftest OK — ENO3: {eno3['n_exact_nbre']} exact NBREs on "
              f"{eno3['chrom']} ({eno3['assembly']}), gene strand {eno3['gene_strand_derived']}")
        for s in eno3["sites"]:
            print(f"    {s['chrom']}:{s['start']}-{s['end']} "
                  f"({s['strand_of_motif']}) offset {s['offset_from_tss']:+d}")
    return 1 if fails else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", choices=["recon", "arms", "suppl"], default="recon")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--budget-s", type=float, default=DEFAULT_BUDGET_S)
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.check:
        if not os.path.exists(RECON_OUT):
            print(f"no committed recon at {RECON_OUT}")
            return 1
        with open(RECON_OUT, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        print(json.dumps({k: d[k] for k in
                          ("series", "n_samples_parsed", "deposit_supports_a_peak_overlap",
                           "filenames_matching_a_peak_call_pattern")}, indent=1))
        return 0

    if args.fetch and args.stage == "suppl":
        out = run_suppl(args.budget_s)
        with open(SUPPL2_OUT, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print(f"\nwrote {SUPPL2_OUT}")
        for fn, found in out["genomic_interval_tables_found"].items():
            print(f"  {fn}: {len(found)} interval-shaped table(s)")
            for f in found:
                print(f"      {f}")
        return 0

    if args.fetch and args.stage == "arms":
        out = run_arms(args.budget_s)
        with open(SUPPL_OUT, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print(f"\nwrote {SUPPL_OUT}")
        print(f"total deposited bytes: {out['total_deposited_bytes']:,}")
        print(f"arm barcode counts:    {out['arms']['barcode_counts_by_arm']}")
        return 0

    if args.fetch:
        out = run_recon(args.budget_s)
        with open(RECON_OUT, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print(f"\nwrote {RECON_OUT}")
        print(f"deposited filenames: {len(out['all_deposited_filenames'])}")
        print(f"peak-call-shaped:    {out['filenames_matching_a_peak_call_pattern']}")
        print(f"build token counts:  {out['genome_build']['token_counts']}")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
