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
        for r in rows:
            if best_col is None or len(r) <= best_col:
                continue
            raw = r[best_col].strip().strip('"')
            arm = _match_arm(raw)
            if arm:
                counts[arm] = counts.get(arm, 0) + 1
                raw_labels.setdefault(arm, set()).add(raw)
        per_file[fn] = {
            "state": "ok",
            "header": header,
            "n_rows": len(rows),
            "variant_column_index": best_col,
            "arm_barcode_counts": counts,
            "raw_labels_matched": {k: sorted(v) for k, v in raw_labels.items()},
        }
        for arm, n in counts.items():
            label_counts[arm] = label_counts.get(arm, 0) + n
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
    go("biorxiv_supplementary_material_page",
       f"https://www.biorxiv.org/content/{PREPRINT_DOI}v1.supplementary-material")

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
    ap.add_argument("--stage", choices=["recon", "arms"], default="recon")
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
