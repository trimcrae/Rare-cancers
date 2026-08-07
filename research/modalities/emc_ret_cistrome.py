#!/usr/bin/env python3
"""
IS *RET* A DIRECT TRANSCRIPTIONAL TARGET OF NR4A3? — MEASURED OCCUPANCY, NOT A MOTIF STRING.

⭐ WHY THIS EXISTS, AND WHY IT IS NOT `emc_ret_target_scan.py`.
`emc_ret_target_scan.py` asks whether *RET*'s regulatory window carries an **NBRE octamer** at a
rate a composition-matched null does not. That is a sequence question. It was built first because
`emc-unexplored-treatment-lanes.md` §3.1 named a motif scan as the lane's free next step — and
[`emc-ret-lane.md`](./emc-ret-lane.md) §2a then established that the named precedent does not
support it: the ENO3 result was EMSA / ChIP / luciferase on **TFG::NR4A3**, not a motif scan on the
EMC-canonical fusion, so a motif scan can prioritise and can never conclude.

That memo's §2d found the better instrument and could not reach it: **wild-type NR4A3 ChIP-seq
exists**. A peak is measured protein occupancy in real chromatin; an NBRE octamer is an 8-mer that
occurs about once per 33 kb of random sequence. This module is that instrument. It is a SIBLING of
the motif scan, not a replacement — the two answer different questions and are allowed to disagree,
which is the point of running both.

⛔⛔ WHAT THIS INSTRUMENT CAN AND CANNOT CONCLUDE — READ BEFORE ANY NUMBER BELOW.
  * Every peak set reachable at $0 is **WILD-TYPE NR4A1/NR4A2/NR4A3 in a non-EMC cell type.**
    No `EWSR1::NR4A3` cistrome exists anywhere (`emc-ret-lane.md` §2d, 792-record Europe PMC
    corpus). So:
      - a peak at *RET* is a **PRIOR**, and a strong one, because it is measured occupancy by the
        protein whose DNA-binding domain the fusion retains intact. It is **NOT** a demonstration
        that the fusion binds *RET* in EMC, and this file never says it is;
      - **NO peak at *RET* is WEAK evidence**, because the locus may simply be closed in the cell
        type assayed. An absent peak in dendritic cells is an absent reading of dendritic-cell
        chromatin — CLAUDE.md §4: an absent reading is not a reading of absence.
  * A peak is not a function. Occupancy does not establish transactivation, and nothing here is a
    statement about efficacy, selectivity, safety, a therapeutic window or clinical readiness for
    any agent in EMC or any other disease. No EMC patient has received a selective RET inhibitor.

⛔ THE GENOME BUILD IS A FIRST-CLASS RESULT, NOT A FOOTNOTE. This lane has already been burned
twice by coordinate conventions that produced plausible-looking artifacts (the NR4A3 exon-numbering
hazard and the 2-nt acceptor 5'UTR — `junction-mrna-frame-audit.json`). The genome analogue is
worse, because *RET* sits on chr10 where GRCh37 and GRCh38 differ by roughly half a megabase: a
build mix-up does not throw, it silently reports the wrong locus. Three guards, all asserted rather
than described:
  1. **Nothing is lifted over.** Each build's *RET* span is fetched from that build's own service.
  2. **Two independent sources per build** (Ensembl REST + NCBI Gene), and the artifact records the
     disagreement rather than asserting agreement.
  3. **An intersection across builds is refused**, not corrected — `intersect_locus` raises if a
     peak file's build is not the locus's build.
  4. **BED is 0-based half-open; Ensembl and NCBI are 1-based inclusive.** One converter,
     `ens_to_bed`, unit-tested including the off-by-one and the adjacency case.

$0 — a GitHub-hosted CPU runner, pure stdlib, no pip. The dev sandbox's egress proxy answers 403 to
CONNECT for NCBI, EBI, Ensembl and dbcls, which is why this runs in CI (CLAUDE.md §6).

Usage:
    python emc_ret_cistrome.py --fetch      # CI: retrieve everything, derive, write both files
    python emc_ret_cistrome.py              # derive from the committed inputs cache (offline)
    python emc_ret_cistrome.py --check      # re-derive offline and diff against the artifact
    python emc_ret_cistrome.py --selftest   # interval algebra + verdict guards, no network
"""

import argparse
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-ret-cistrome.json")
INPUTS = os.path.join(HERE, "emc-ret-cistrome-inputs.json")

sys.path.insert(0, HERE)

# ⛔ ONE HOME FOR THE WINDOW (CLAUDE.md §1). The -10 kb / +15 kb asymmetry is not this module's
# choice and is not re-typed here: it was frozen in `emc_ret_target_scan.py` BEFORE any RET
# sequence had been fetched, because RET's only experimentally validated distal element (HOXB5 at
# MCS+9.7, PMID 24794774) sits in the first intron and a symmetric +/-5 kb window excludes it.
# Importing it means a future re-scope moves both instruments at once or fails loudly.
from emc_ret_target_scan import (  # noqa: E402
    FOCUS_GENES as MOTIF_FOCUS_GENES,
    WINDOW_DOWNSTREAM,
    WINDOW_UPSTREAM,
    background_symbols,
)

UA = {"User-Agent": "Rare-cancers-research/1.0 (EMC NR4A3 cistrome; contact via repo)"}

FRAMING = (
    "MEASURED TRANSCRIPTION-FACTOR OCCUPANCY FROM PUBLIC ChIP-seq, INTERSECTED WITH THE *RET* "
    "LOCUS. Every peak set here is WILD-TYPE NR4A1/NR4A2/NR4A3 in a cell type that is not EMC, "
    "because no EWSR1::NR4A3 cistrome exists. A peak at RET is a prior for the fusion, never a "
    "demonstration; no peak is weak evidence, because the locus may be closed in the cells "
    "assayed. Nothing here asserts efficacy, selectivity, safety, a therapeutic window or "
    "clinical readiness for any agent in extraskeletal myxoid chondrosarcoma. No EMC patient "
    "has received a selective RET inhibitor."
)

PARALOGUES = ["NR4A1", "NR4A2", "NR4A3"]

# ---------------------------------------------------------------------------------------------
# BUILDS. Each build is fetched from its OWN service. There is no liftover in this file and there
# must never be one: a hand-applied chr10 offset is exactly the class of defect this lane has been
# burned by twice.
# ---------------------------------------------------------------------------------------------
BUILDS = {
    "hg38": {
        "ensembl_rest": "https://rest.ensembl.org",
        "ensembl_assembly_expected": "GRCh38",
        "ncbi_chr_accession_prefix": "NC_000010.11",
        "why": "the current human reference; ChIP-Atlas serves hg38 peak sets for it",
    },
    "hg19": {
        "ensembl_rest": "https://grch37.rest.ensembl.org",
        "ensembl_assembly_expected": "GRCh37",
        "ncbi_chr_accession_prefix": "NC_000010.10",
        "why": "older ChIP-seq is archived only on hg19; a peak set on hg19 is intersected with "
               "the hg19 locus and never with the hg38 one",
    },
}

# ---------------------------------------------------------------------------------------------
# THE LOCI. RET is the question; everything else exists so the RET reading is COMPARATIVE rather
# than absolute — a single peak somewhere in a 25 kb window means nothing without knowing what the
# same instrument does at genes whose answer is already known and at genes chosen by nobody.
# ---------------------------------------------------------------------------------------------
LOCI = {
    "RET": "⭐ THE QUESTION. emc-unexplored-treatment-lanes.md §3.1 / emc-ret-lane.md.",
    # --- published direct targets of an NR4A3 protein: the positive controls -------------------
    "ENO3": "POSITIVE CONTROL. Direct transactivation target of TFG::NR4A3 shown by EMSA + ChIP + "
            "luciferase at two NBRE motifs upstream of the TSS (PMID 26310886). ⚠ The fusion "
            "there is TFG::NR4A3, not EWSR1::NR4A3.",
    "SEMA3C": "POSITIVE CONTROL, and the closest one that exists. MatInspector-predicted NBRE "
              "confirmed by ChAP-qPCR, with binding RETAINED by the EWSR1-NR4A3 chimera and "
              "IMPAIRED by TAF15-NR4A3 (PMID 31020999 / PMC6766969). This is the only published "
              "chromatin experiment on the EMC-canonical fusion at any locus.",
    "PPARG": "⚠ NAMED as an established direct target in emc-unexplored-treatment-lanes.md §3.1. "
             "emc-ret-lane.md §2a did not verify a direct-binding experiment for it, so it is "
             "scored as a CANDIDATE control and never as a known positive.",
    # --- autoregulation: an NBRE question in its own right -------------------------------------
    "NR4A1": "the paralogue's own locus — NR4A-family autoregulation, and the read that says "
             "whether a peak set has any signal at all at an expected site.",
    "NR4A2": "the second paralogue's locus — the same NR4A-family autoregulation question, and "
             "the third arm of the paralogue-overlap read.",
    "NR4A3": "the fusion's own 3' partner.",
    # --- the alternative hypothesis for EMC's TKI activity --------------------------------------
    "VEGFA": "ALTERNATIVE HYPOTHESIS. The conventional attribution for EMC's sunitinib/pazopanib "
             "activity is anti-angiogenic (the originating authors' own reading, PMID 23058004).",
    "KDR": "VEGFR2 — the same alternative hypothesis, and the receptor half of it. If NR4A "
           "occupancy is no more enriched at RET than at KDR, the occupancy argument does not "
           "discriminate between the two attributions.",
    # --- RET's own ligand/co-receptor module: relevant to whether RET could be engaged at all ---
    "GDNF": "RET ligand. The MET-in-clear-cell-sarcoma guard (PMID 34885165) failed on LIGAND "
            "absence as much as on phospho-absence, so the ligand module is part of the question.",
    "GFRA1": "GDNF-family co-receptor, obligate for RET engagement by GDNF.",
    "GFRA2": "GFRalpha-2, the co-receptor through which neurturin engages RET — part of the same "
             "ligand-availability question the clear cell sarcoma comparator failed on.",
    "NRTN": "neurturin — a second GDNF-family ligand, so a null on GDNF alone is not read as a "
            "null on the ligand module.",
}

# The two positive controls that a peak set must be graded against before RET is read from it.
KNOWN_POSITIVE_CONTROLS = ["SEMA3C", "ENO3"]

# ---------------------------------------------------------------------------------------------
# CATALOGUES. Every URL pattern below is ATTEMPTED and its HTTP status RECORDED. Not one of them
# is assumed to work: this module is written in a sandbox that cannot reach any of these hosts, so
# a pattern quoted from memory is a hypothesis. A 404 is a recorded reading, never a silent skip.
# ---------------------------------------------------------------------------------------------
CHIP_ATLAS_METADATA = [
    "https://chip-atlas.dbcls.jp/data/metadata/experimentList.tab",
    "https://chip-atlas.dbcls.jp/data/metadata/experimentList.tab.gz",
    "http://dbarchive.biosciencedbc.jp/kyushu-u/metadata/experimentList.tab",
]
CHIP_ATLAS_BED = (
    "https://chip-atlas.dbcls.jp/data/{genome}/eachData/bed{th}/{srx}.{th}.bed"
)
CHIP_ATLAS_THRESHOLD = "05"  # MACS2 q < 1e-05, ChIP-Atlas's uniform reprocessing
# ChIP-Atlas's own per-antigen TARGET-GENE table: one row per gene, one column per experiment,
# the value being the peak's MACS2 -10*log10(Q) within N kb of the TSS. It is a purpose-built
# answer to exactly this module's question and is fetched IN ADDITION to the peak files, never
# instead of them: it is a derived summary on somebody else's TSS definition, and this module's
# own intersection is the one that carries the window it can defend.
CHIP_ATLAS_TARGET = "https://chip-atlas.dbcls.jp/data/{genome}/target/{antigen}.{dist}.tsv"
CHIP_ATLAS_TARGET_DISTANCES = ["1", "5", "10"]  # kb from the TSS

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"

# GEO searches. Several, deliberately overlapping: a single query that returns nothing is
# indistinguishable from a dataset that does not exist, and these are cheap.
GEO_QUERIES = [
    ('NR4A3 AND ("chip seq" OR "chip-seq" OR chipseq)', "NR4A3 ChIP-seq, any organism"),
    ('NR4A1 AND ("chip seq" OR "chip-seq" OR chipseq)', "NR4A1 ChIP-seq, any organism"),
    ('NR4A2 AND ("chip seq" OR "chip-seq" OR chipseq)', "NR4A2 ChIP-seq, any organism"),
    ('(NR4A1 OR NR4A2 OR NR4A3) AND (cDC2 OR "conventional dendritic" OR "dendritic cell")',
     "the PMID 36482877 cDC2 three-paralogue dataset, whose accession is absent from the PMC "
     "rendering (emc-ret-lane.md §2d)"),
    ('NR4A3 AND (Schwann OR sciatic OR "peripheral nerve")',
     "the PMID 42028030 Schwann-cell dataset (GSA CRA032324) — is it mirrored in GEO?"),
    ('(NR4A1 OR NR4A2 OR NR4A3) AND "genome binding"', "GEO's own ChIP assay type string"),
]

# Papers whose data-availability we need. Europe PMC's `resultType=core` carries a CURATED
# dbCrossReferenceList, which is exactly the instrument for "the accession is not in the text".
PAPERS = {
    "PMC10108054": {
        "pmid": "36482877",
        "what": "human primary CD1c+ cDC2s, resting and stimulated; ChIP sequencing for NR4A1, "
                "NR4A2 AND NR4A3 in the same cells. ⭐ The three-paralogue human dataset — the "
                "single most valuable retrieval in this lane, because the repository's "
                "paralogue-selectivity problem has only ever been argued from domain sequence "
                "identity.",
    },
    "PMC13099357": {
        "pmid": "42028030",
        "what": "Schwann cells; integrated ChIP-seq + mRNA-seq identifying GLS2 as a direct NR4A3 "
                "target. Deposited in GSA (CRA032324 ChIP-seq, CRA032321 mRNA-seq), not GEO.",
    },
    "PMC6766969": {
        "pmid": "31020999",
        "what": "SEMA3C ChAP-qPCR — the only chromatin experiment on EWSR1-NR4A3 at any locus, "
                "and the source of this module's strongest positive control.",
    },
}

GSA_ACCESSIONS = {
    "CRA032324": "NR4A3 ChIP-seq, Schwann cells (PMID 42028030)",
    "CRA032321": "matched mRNA-seq (PMID 42028030)",
}

# Other catalogues of uniformly reprocessed human TF ChIP-seq. Tried, recorded, never assumed.
REMAP_PATTERNS = [
    "https://remap.univ-amu.fr/storage/remap2022/hg38/MACS2/TF/{tf}/"
    "remap2022_{tf}_all_macs2_hg38_v1_0.bed.gz",
    "https://remap.univ-amu.fr/storage/remap2022/hg38/MACS2/remap2022_{tf}_all_macs2_hg38_v1_0.bed.gz",
]
ENCODE_SEARCH = ("https://www.encodeproject.org/search/?type=Experiment&target.label={tf}"
                 "&frame=object&format=json&limit=all")

MAX_BYTES_METADATA = 1_600_000_000   # experimentList.tab is hundreds of MB; stream, never hold
MAX_BYTES_PEAKS = 400_000_000
NET_BUDGET_S = int(os.environ.get("RET_CISTROME_BUDGET_S", "3000"))


# =============================================================================================
# INTERVAL ALGEBRA — the part a coordinate defect would hide in. Every function here is
# exercised by --selftest with no network.
# =============================================================================================

def ens_to_bed(start_1based, end_1based_inclusive):
    """1-based inclusive (Ensembl / NCBI / GFF) -> 0-based half-open (BED).

    A 1-bp feature at position 100 is Ensembl [100, 100] and BED [99, 100): width 1 either way.
    Getting this wrong shifts every window by one base and shortens it by one — invisible against
    a 25 kb window and fatal against a summit.
    """
    if end_1based_inclusive < start_1based:
        raise ValueError(f"end {end_1based_inclusive} < start {start_1based}")
    return start_1based - 1, end_1based_inclusive


def bed_to_ens(start_0, end_0_exclusive):
    """The inverse. Present so a round trip is testable rather than argued."""
    if end_0_exclusive <= start_0:
        raise ValueError(f"empty or inverted BED interval [{start_0}, {end_0_exclusive})")
    return start_0 + 1, end_0_exclusive


def overlaps(a_start, a_end, b_start, b_end):
    """Half-open overlap. Adjacency ([0,10) and [10,20)) is NOT overlap, by construction."""
    return a_start < b_end and b_start < a_end


def overlap_bp(a_start, a_end, b_start, b_end):
    return max(0, min(a_end, b_end) - max(a_start, b_start))


def norm_chrom(c):
    """`chr10`, `10`, `CHR10` -> `chr10`. Ensembl says `10`; BED says `chr10`; a silent mismatch
    reports zero peaks everywhere, which reads exactly like a real negative."""
    c = str(c).strip()
    if not c:
        return ""
    c = c[3:] if c.lower().startswith("chr") else c
    return "chr" + c


def tss_of(gene):
    """TSS on the forward genomic strand, in the source's own 1-based coordinates."""
    return gene["start"] if int(gene["strand"]) == 1 else gene["end"]


def promoter_window_bed(gene):
    """The -10 kb / +15 kb TSS window, in BED coordinates, strand-aware.

    The asymmetry is `emc_ret_target_scan`'s and is imported, not re-typed (CLAUDE.md §1).
    """
    tss = tss_of(gene)
    if int(gene["strand"]) == 1:
        lo, hi = tss - WINDOW_UPSTREAM, tss + WINDOW_DOWNSTREAM
    else:
        lo, hi = tss - WINDOW_DOWNSTREAM, tss + WINDOW_UPSTREAM
    return ens_to_bed(lo, hi)


def genebody_window_bed(gene, flank=10000):
    """Gene body +/- a flank, in BED coordinates. Reported ALONGSIDE the promoter window so the
    reading cannot be an artefact of one window choice: RET's body is ~53 kb and a distal element
    inside it is exactly what the promoter window is scoped to miss."""
    return ens_to_bed(int(gene["start"]) - flank, int(gene["end"]) + flank)


def intersect_locus(peaks, locus, build_of_peaks, build_of_locus):
    """Peaks overlapping one window. REFUSES a cross-build intersection rather than correcting it.

    `peaks` is a list of (chrom, start0, end0, score). `locus` is (chrom, start0, end0).
    """
    if build_of_peaks != build_of_locus:
        raise ValueError(
            f"cross-build intersection refused: peaks are {build_of_peaks}, locus is "
            f"{build_of_locus}. Nothing in this module lifts over.")
    lc, ls, le = locus
    hits = []
    for (c, s, e, sc) in peaks:
        if c == lc and overlaps(s, e, ls, le):
            hits.append({"chrom": c, "start": s, "end": e, "score": sc,
                         "overlap_bp": overlap_bp(s, e, ls, le)})
    return hits


def nearest_peak_distance(peaks, chrom, point0):
    """Signed distance from a point (BED coordinate) to the nearest peak on the same chromosome.
    Negative = peak is upstream in genomic coordinates. `None` if the chromosome carries no peak —
    which is an ABSENT READING and is rendered as one, never as a large distance."""
    best = None
    for (c, s, e, _sc) in peaks:
        if c != chrom:
            continue
        d = 0 if s <= point0 < e else (s - point0 if s > point0 else e - point0)
        if best is None or abs(d) < abs(best):
            best = d
    return best


# =============================================================================================
# NETWORK — every attempt recorded with its status.
# =============================================================================================

class Budget:
    def __init__(self, seconds):
        self.t0 = time.time()
        self.seconds = seconds

    def left(self):
        return self.seconds - (time.time() - self.t0)

    def spent(self):
        return round(time.time() - self.t0, 1)


BUDGET = Budget(NET_BUDGET_S)
ATTEMPTS = []


def _record(url, status, nbytes=None, error=None, note=None):
    rec = {"url": url[:300], "status": status}
    if nbytes is not None:
        rec["bytes"] = nbytes
    if error:
        rec["error"] = str(error)[:300]
    if note:
        rec["note"] = note
    ATTEMPTS.append(rec)
    return rec


def get(url, timeout=120, tries=3, headers=None, max_bytes=MAX_BYTES_PEAKS):
    """One GET, bounded, recorded. Returns bytes or None; NEVER raises for a dead endpoint."""
    last = None
    for i in range(tries):
        if BUDGET.left() <= 5:
            _record(url, "budget_exhausted", note=f"{BUDGET.spent()}s spent")
            return None
        try:
            req = urllib.request.Request(url, headers={**UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                buf = io.BytesIO()
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    buf.write(chunk)
                    if buf.tell() > max_bytes:
                        _record(url, "truncated_at_cap", nbytes=buf.tell())
                        return None
                data = buf.getvalue()
            _record(url, getattr(r, "status", 200), nbytes=len(data))
            return data
        except urllib.error.HTTPError as exc:
            _record(url, exc.code, error=exc.reason)
            return None                      # a 404 is an answer; do not retry it
        except Exception as exc:             # noqa: BLE001
            last = exc
            time.sleep(2 ** i)
    _record(url, "failed", error=last)
    return None


def get_json(url, **kw):
    raw = get(url, **kw)
    if raw is None:
        return None
    try:
        return json.loads(raw.decode("utf-8", "replace"))
    except Exception as exc:                 # noqa: BLE001
        _record(url, "unparseable_json", error=exc)
        return None


def stream_lines(url, timeout=300):
    """Stream a very large tab file line by line. Never holds it in memory."""
    if BUDGET.left() <= 30:
        _record(url, "budget_exhausted", note=f"{BUDGET.spent()}s spent")
        return
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            gz = url.endswith(".gz")
            raw = gzip.GzipFile(fileobj=r) if gz else r
            total = 0
            for ln in io.TextIOWrapper(raw, encoding="utf-8", errors="replace"):
                total += len(ln)
                if total > MAX_BYTES_METADATA:
                    _record(url, "truncated_at_cap", nbytes=total)
                    return
                yield ln
        _record(url, 200, nbytes=total)
    except urllib.error.HTTPError as exc:
        _record(url, exc.code, error=exc.reason)
    except Exception as exc:                 # noqa: BLE001
        _record(url, "failed", error=exc)


# =============================================================================================
# PART 0 — the genome build, reconciled from two independent sources per build.
# =============================================================================================

def fetch_gene_spans(symbols, build):
    """Ensembl POST batch lookup for one build. Returns {symbol: record} plus a diagnostic."""
    base = BUILDS[build]["ensembl_rest"]
    url = f"{base}/lookup/symbol/homo_sapiens"
    body = json.dumps({"symbols": list(symbols)}).encode()
    out, diag = {}, {"build": build, "endpoint": url, "n_requested": len(symbols)}
    for i in range(3):
        if BUDGET.left() <= 5:
            diag["_status"] = "budget_exhausted"
            return out, diag
        try:
            req = urllib.request.Request(
                url, data=body,
                headers={**UA, "Content-Type": "application/json",
                         "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read().decode("utf-8", "replace"))
            _record(url, 200, nbytes=len(body), note=f"POST {len(symbols)} symbols, {build}")
            break
        except Exception as exc:                     # noqa: BLE001
            diag["error"] = str(exc)[:300]
            time.sleep(2 ** i)
    else:
        _record(url, "failed", error=diag.get("error"))
        diag["_status"] = "failed"
        return out, diag

    assemblies = set()
    for sym, g in (d or {}).items():
        if not isinstance(g, dict) or not g.get("seq_region_name"):
            continue
        assemblies.add(g.get("assembly_name"))
        out[sym] = {"ensembl_id": g.get("id"), "assembly_name": g.get("assembly_name"),
                    "chrom": norm_chrom(g.get("seq_region_name")),
                    "start": int(g["start"]), "end": int(g["end"]),
                    "strand": int(g.get("strand", 1)), "biotype": g.get("biotype")}
    diag["_status"] = "read"
    diag["n_resolved"] = len(out)
    diag["assemblies_returned"] = sorted(a for a in assemblies if a)
    exp = BUILDS[build]["ensembl_assembly_expected"]
    diag["assembly_expected"] = exp
    diag["assembly_matches_expected"] = (diag["assemblies_returned"] == [exp])
    if not diag["assembly_matches_expected"]:
        diag["⛔"] = ("the service returned an assembly this module did not ask for. Every "
                     "intersection on this build is refused rather than reported.")
    return out, diag


def fetch_ncbi_gene_spans(symbols):
    """NCBI Gene, the INDEPENDENT second source. Its `genomicinfo` carries `chraccver`, and a
    RefSeq chromosome accession VERSION is self-describing about the assembly (NC_000010.11 is
    GRCh38's chr10, .10 is GRCh37's), so the build is read off the data rather than assumed."""
    diag = {"endpoint": EUTILS, "n_requested": len(symbols)}
    term = " OR ".join(f'{s}[sym]' for s in symbols)
    q = urllib.parse.urlencode({"db": "gene", "retmax": "500", "retmode": "json",
                                "term": f"({term}) AND human[orgn]"})
    es = get_json(f"{EUTILS}/esearch.fcgi?{q}")
    if not es:
        diag["_status"] = "esearch_failed"
        return {}, diag
    ids = ((es.get("esearchresult") or {}).get("idlist") or [])
    diag["n_gene_ids"] = len(ids)
    if not ids:
        diag["_status"] = "no_ids"
        return {}, diag
    su = get_json(f"{EUTILS}/esummary.fcgi?db=gene&retmode=json&id={','.join(ids[:500])}")
    if not su:
        diag["_status"] = "esummary_failed"
        return {}, diag
    out = {}
    for gid, rec in (su.get("result") or {}).items():
        if gid == "uids" or not isinstance(rec, dict):
            continue
        sym = rec.get("name")
        if sym not in symbols:
            continue
        for gi in (rec.get("genomicinfo") or []):
            acc = str(gi.get("chraccver") or "")
            s, e = gi.get("chrstart"), gi.get("chrstop")
            if s is None or e is None:
                continue
            # ⚠ NCBI esummary genomicinfo is 0-BASED and start>stop on the minus strand. Both
            # are normalised here explicitly rather than silently.
            s, e = int(s), int(e)
            lo, hi = (s, e) if s <= e else (e, s)
            out.setdefault(sym, []).append(
                {"gene_id": gid, "chr_accession": acc, "start_0based": lo, "end_0based": hi,
                 "strand": 1 if s <= e else -1,
                 "_coordinate_convention": "NCBI esummary genomicinfo: 0-based; start>stop on "
                                           "the minus strand, normalised here"})
    diag["_status"] = "read"
    diag["n_resolved"] = len(out)
    return out, diag


def reconcile_builds(ens_by_build, ncbi):
    """The build result. Reports the chr10 offset between builds as a NUMBER, because a number is
    the only form in which a build mix-up is visible after the fact."""
    rec = {
        "_what": "The genome build, established from two independent sources per build and never "
                 "lifted over. This block is a RESULT, not metadata (CLAUDE.md §4: this lane has "
                 "twice been burned by a coordinate convention that produced a plausible file).",
        "_interval_conventions": {
            "ensembl_and_ncbi_gene_lookup": "1-based inclusive",
            "ncbi_esummary_genomicinfo": "0-based, start>stop on the minus strand",
            "BED_and_every_peak_file": "0-based half-open",
            "converter": "emc_ret_cistrome.ens_to_bed / bed_to_ens, exercised by --selftest "
                         "including the 1-bp and adjacency cases",
        },
        "per_build": {},
    }
    for build, genes in ens_by_build.items():
        g = genes.get("RET")
        rec["per_build"][build] = {
            "ensembl_assembly_expected": BUILDS[build]["ensembl_assembly_expected"],
            "RET_ensembl": g,
            "_status": "read" if g else "RET_not_resolved",
        }
    a = (ens_by_build.get("hg38") or {}).get("RET")
    b = (ens_by_build.get("hg19") or {}).get("RET")
    if a and b:
        rec["chr10_offset_hg19_minus_hg38_at_RET_start"] = int(b["start"]) - int(a["start"])
        rec["⛔ why_the_offset_is_printed"] = (
            "RET sits in a region where GRCh37 and GRCh38 differ by a large, non-obvious "
            "constant. A build mix-up does not raise; it silently reports another locus. The "
            "offset is printed so a future reader can check any coordinate in this file against "
            "the build it claims.")
    # Independent cross-check against NCBI Gene.
    cross = {}
    for sym, recs in (ncbi or {}).items():
        for r in recs:
            acc = r["chr_accession"]
            build = next((bd for bd, cfg in BUILDS.items()
                          if acc.startswith(cfg["ncbi_chr_accession_prefix"])), None)
            if build is None:
                continue
            e = (ens_by_build.get(build) or {}).get(sym)
            if not e:
                continue
            # Ensembl 1-based inclusive -> BED, then compare with NCBI's 0-based values.
            es, ee = ens_to_bed(e["start"], e["end"])
            cross.setdefault(sym, {})[build] = {
                "ncbi_chr_accession": acc,
                "ncbi_span_0based": [r["start_0based"], r["end_0based"]],
                "ensembl_span_bed": [es, ee],
                "start_delta_bp": r["start_0based"] - es,
                "end_delta_bp": r["end_0based"] - ee,
            }
    rec["independent_cross_check_ncbi_gene"] = {
        "_what": "Ensembl vs NCBI Gene on the SAME build, in the SAME coordinate frame. Small "
                 "deltas are expected — the two annotate transcript ends differently — and are "
                 "REPORTED rather than asserted away. A delta of order 10^5 would be a build "
                 "mix-up and is what this check exists to catch.",
        "per_gene": cross,
    }
    ret_ok = []
    for build, c in (cross.get("RET") or {}).items():
        ret_ok.append(abs(c["start_delta_bp"]) < 50000 and abs(c["end_delta_bp"]) < 50000)
    rec["RET_two_sources_agree_within_50kb_on_every_build"] = (bool(ret_ok) and all(ret_ok))
    return rec


# =============================================================================================
# PART 1 — dataset discovery and characterisation. NOTHING is intersected before this runs.
# =============================================================================================

CA_COLS = ["srx", "genome", "antigen_class", "antigen", "cell_type_class", "cell_type",
           "cell_type_description", "processing_logs", "title"]


def discover_chip_atlas():
    """Stream ChIP-Atlas's experiment list and keep only the NR4A rows.

    ⭐ This IS the characterisation CLAUDE.md §6 requires before anything is built on a series:
    every row carries the assay's genome build, cell type, cell-type class, and ChIP-Atlas's own
    processing log (read count, % mapped, % duplicates, peak count) — which is the QC a peak set
    has to be graded on before its peaks mean anything.
    """
    out = {"_what": "ChIP-Atlas: every public ChIP-seq experiment, uniformly reprocessed with "
                    "MACS2 against a fixed threshold. Antigen NR4A1 / NR4A2 / NR4A3, any genome, "
                    "any cell type.",
           "_peak_caller": f"MACS2, ChIP-Atlas threshold {CHIP_ATLAS_THRESHOLD} (q < 1e-"
                           f"{int(CHIP_ATLAS_THRESHOLD)})",
           "_citation": "Oki et al., EMBO Reports 2018, PMID 30413482 — ChIP-Atlas.",
           "experiments": [], "_status": "NOT_RUN"}
    want = {p.upper() for p in PARALOGUES}
    for url in CHIP_ATLAS_METADATA:
        n_lines, hits = 0, []
        for ln in stream_lines(url):
            n_lines += 1
            if not ln.strip():
                continue
            f = ln.rstrip("\n").split("\t")
            if len(f) < 6:
                continue
            if f[3].strip().upper() in want:
                rec = {CA_COLS[i]: (f[i].strip() if i < len(f) else None)
                       for i in range(len(CA_COLS))}
                rec["extra_attributes"] = [x for x in f[len(CA_COLS):] if x][:12]
                hits.append(rec)
        if n_lines:
            out["_status"] = "read"
            out["source_url"] = url
            out["n_experiments_searched"] = n_lines
            out["experiments"] = hits
            out["n_matching"] = len(hits)
            break
    if out["_status"] != "read":
        out["why"] = ("no ChIP-Atlas metadata endpoint answered. ⚠ ABSENT READING — this says "
                      "nothing about whether NR4A ChIP-seq exists in ChIP-Atlas.")
    else:
        # Parse the processing log into named QC fields. ChIP-Atlas's log is
        # "<#reads>,<%mapped>,<%duplicates>,<#peaks>".
        for e in out["experiments"]:
            parts = [p.strip() for p in (e.get("processing_logs") or "").split(",")]
            if len(parts) >= 4:
                def _num(x):
                    try:
                        return float(x)
                    except Exception:      # noqa: BLE001
                        return None
                e["qc"] = {"n_reads": _num(parts[0]), "pct_mapped": _num(parts[1]),
                           "pct_duplicates": _num(parts[2]), "n_peaks_reported": _num(parts[3])}
        out["by_antigen_and_genome"] = {}
        for e in out["experiments"]:
            k = f"{e['antigen']}|{e['genome']}"
            out["by_antigen_and_genome"].setdefault(k, []).append(e["srx"])
    return out


def discover_geo():
    """GEO DataSets search + per-series supplementary-file listing.

    ⚠ SAMPLE-LEVEL WHERE POSSIBLE, and titles are treated as CLAIMS. This repository has been
    bitten twice by reading a GEO series title as a measurement, which is why the series record is
    kept verbatim beside anything derived from it.
    """
    out = {"_what": "NCBI GEO DataSets, several deliberately overlapping queries. A query that "
                    "returns nothing is indistinguishable from a dataset that does not exist, "
                    "so more than one is run and every one is recorded.",
           "queries": [], "series": {}, "_status": "NOT_RUN"}
    seen = {}
    for term, why in GEO_QUERIES:
        q = urllib.parse.urlencode({"db": "gds", "retmax": "60", "retmode": "json",
                                    "term": term})
        es = get_json(f"{EUTILS}/esearch.fcgi?{q}")
        rec = {"term": term, "why": why}
        if not es:
            rec["_status"] = "failed"
            out["queries"].append(rec)
            continue
        ids = ((es.get("esearchresult") or {}).get("idlist") or [])
        rec["_status"] = "read"
        rec["count"] = int((es.get("esearchresult") or {}).get("count") or 0)
        rec["n_ids"] = len(ids)
        out["queries"].append(rec)
        if not ids:
            continue
        su = get_json(f"{EUTILS}/esummary.fcgi?db=gds&retmode=json&id={','.join(ids)}")
        for uid, r in ((su or {}).get("result") or {}).items():
            if uid == "uids" or not isinstance(r, dict):
                continue
            acc = r.get("accession")
            if not acc or acc in seen:
                continue
            seen[acc] = True
            out["series"][acc] = {
                "accession": acc, "title": r.get("title"), "gdsType": r.get("gdsType"),
                "taxon": r.get("taxon"), "n_samples": r.get("n_samples"),
                "gpl": r.get("GPL"), "gse": r.get("GSE"), "pubmed": r.get("PubMedIds"),
                "summary": (r.get("summary") or "")[:900],
                "ftp": r.get("FTPLink"),
                "supp_file_field": r.get("suppFile"),
                "_found_by": term,
                "⚠": "the title and summary are the depositors' CLAIM, not a measurement.",
            }
    out["_status"] = "read" if out["series"] or any(
        q.get("_status") == "read" for q in out["queries"]) else "NOT_RUN"
    out["n_series"] = len(out["series"])
    return out


PEAKISH = re.compile(r"\.(narrowPeak|broadPeak|bed|bedGraph|peaks?\.(txt|xls|tsv))(\.gz)?$",
                     re.I)


def list_geo_supplementary(gse):
    """Directory listing for one series' supplementary files. Peak calls live here or nowhere."""
    n = re.sub(r"\D", "", gse or "")
    if not n:
        return {"_status": "bad_accession"}
    grp = f"GSE{n[:-3]}nnn" if len(n) > 3 else "GSEnnn"
    url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{grp}/GSE{n}/suppl/"
    raw = get(url, timeout=90, max_bytes=8_000_000)
    if raw is None:
        return {"_status": "listing_failed", "url": url}
    html = raw.decode("utf-8", "replace")
    files = sorted(set(re.findall(r'href="([^"?/][^"]*)"', html)))
    return {"_status": "read", "url": url, "n_files": len(files), "files": files[:200],
            "peak_like": [f for f in files if PEAKISH.search(f)]}


def fetch_chip_atlas_target_tables():
    """ChIP-Atlas's per-antigen target-gene table, read for the LOCI only.

    ⭐ WHY IT IS HERE AND WHY IT IS NOT THE ANSWER. This table answers "which genes does antigen X
    bind" directly, across every experiment ChIP-Atlas holds, and it is one small fetch. But it is
    somebody else's TSS definition and somebody else's distance cut, so it is recorded as an
    INDEPENDENT CORROBORATION of this module's own intersection, never as a substitute for it.
    Two instruments agreeing is an argument; one instrument is a number.
    """
    out = {"_what": "ChIP-Atlas per-antigen target-gene tables. Value = MACS2 -10*log10(Q) of the "
                    "strongest peak within the stated distance of the gene's TSS, per experiment.",
           "_why_not_the_headline": "a derived summary on ChIP-Atlas's TSS definition and "
                                    "distance cut. This module's own intersection carries the "
                                    "window it can defend; this is the corroboration.",
           "per_antigen": {}, "_status": "read"}
    for ag in PARALOGUES:
        rec = {}
        for genome in BUILDS:
            for dist in CHIP_ATLAS_TARGET_DISTANCES:
                url = CHIP_ATLAS_TARGET.format(genome=genome, antigen=ag, dist=dist)
                raw = get(url, timeout=180, max_bytes=300_000_000)
                if raw is None:
                    continue
                txt = raw.decode("utf-8", "replace")
                lines = txt.splitlines()
                if not lines:
                    continue
                header = lines[0].split("\t")
                rows = {}
                for ln in lines[1:]:
                    f = ln.split("\t")
                    if len(f) < 2:
                        continue
                    sym = f[1].strip() if len(f) > 1 else ""
                    if sym in LOCI:
                        rows[sym] = {header[i] if i < len(header) else f"col{i}": f[i]
                                     for i in range(min(len(f), 60))}
                rec[f"{genome}_{dist}kb"] = {
                    "url": url, "n_columns": len(header), "n_genes": max(0, len(lines) - 1),
                    "columns": header[:60], "loci_rows": rows,
                    "RET_row_present": "RET" in rows,
                }
                break   # one distance per genome is enough to establish the table exists
        out["per_antigen"][ag] = rec or {"_status": "no_table_at_any_attempted_url"}
    return out


def geo_build_for_series(gse, gsms):
    """Establish a GEO series' genome build FROM ITS OWN RECORD, never by assumption.

    ⛔ THIS IS THE GUARD, NOT A CONVENIENCE. A supplementary peak BED carries no build inside the
    file. Intersecting one against an assumed build is precisely the coordinate defect that has
    already cost this lane twice, and on chr10 it would not throw — it would report another locus.
    GEO's `!Sample_data_processing` carries a `genome build:` line by MIAME requirement, so the
    build is READ. If it cannot be read, the peak set is not intersected.
    """
    rec = {"gse": gse, "_status": "not_established", "evidence": []}
    for gsm in (gsms or [])[:3]:
        url = (f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gsm}"
               "&targ=self&form=text&view=brief")
        raw = get(url, timeout=90, max_bytes=4_000_000)
        if raw is None:
            continue
        txt = raw.decode("utf-8", "replace")
        for m in re.findall(r"!Sample_data_processing\s*=\s*(.{0,300})", txt):
            if re.search(r"genome[_ ]build|assembly", m, re.I):
                rec["evidence"].append({"gsm": gsm, "line": m.strip()[:300]})
    blob = " ".join(e["line"] for e in rec["evidence"])
    for build, pat in (("hg38", r"\b(hg38|GRCh38)\b"), ("hg19", r"\b(hg19|GRCh37)\b")):
        if re.search(pat, blob, re.I):
            rec.setdefault("builds_named", []).append(build)
    named = rec.get("builds_named") or []
    if len(named) == 1:
        rec["_status"] = "read"
        rec["build"] = named[0]
    elif len(named) > 1:
        rec["_status"] = "ambiguous"
        rec["⛔"] = ("more than one build is named in the series' own processing description. The "
                    "peak sets from this series are NOT intersected; an assumed build is the "
                    "defect this module refuses.")
    return rec


def geo_series_gsms(gse):
    """Sample accessions for one series, from the series record itself."""
    url = (f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gse}"
           "&targ=self&form=text&view=brief")
    raw = get(url, timeout=90, max_bytes=8_000_000)
    if raw is None:
        return []
    return re.findall(r"!Series_sample_id\s*=\s*(GSM\d+)",
                      raw.decode("utf-8", "replace"))[:400]


def paper_cross_references():
    """Europe PMC `resultType=core` — the CURATED database cross-reference list.

    ⭐ THE INSTRUMENT THE PRIOR PASS DID NOT HAVE. emc-ret-lane.md §2d searched the PMC *rendering*
    of PMC10108054 for an accession string and found none. Europe PMC separately CURATES data
    cross-references for a record, and its supplementaryFiles endpoint serves the publisher's
    supplements — neither is in the rendered body text. Both are tried here.
    """
    out = {"_what": "Data-availability retrieval for the three chromatin papers, by two routes "
                    "that do not read the article body: Europe PMC's curated cross-reference "
                    "list, and the publisher supplement bundle.",
           "papers": {}, "_status": "NOT_RUN"}
    for pmcid, meta in PAPERS.items():
        rec = dict(meta)
        q = urllib.parse.urlencode({"query": f"PMCID:{pmcid}", "resultType": "core",
                                    "format": "json", "pageSize": "5"})
        d = get_json(f"{EPMC}/search?{q}")
        if d:
            res = ((d.get("resultList") or {}).get("result") or [])
            r0 = res[0] if res else {}
            xrefs = ((r0.get("dbCrossReferenceList") or {}).get("dbCrossReference") or [])
            rec["europepmc"] = {
                "title": r0.get("title"), "journal": (r0.get("journalInfo") or {})
                .get("journal", {}).get("title"),
                "year": r0.get("pubYear"), "doi": r0.get("doi"),
                "isOpenAccess": r0.get("isOpenAccess"),
                "db_cross_references": [
                    {"db": x.get("dbName"),
                     "ids": ((x.get("dbCrossReferenceInfo") or {}).get("dbCrossReferenceInfo")
                             if isinstance(x.get("dbCrossReferenceInfo"), list)
                             else x.get("dbCrossReferenceInfo"))}
                    for x in xrefs],
                "_status": "read",
            }
        else:
            rec["europepmc"] = {"_status": "failed"}
        # The supplement bundle. Only the FILE NAMES are read here; a supplement is not parsed.
        sup = get(f"{EPMC}/{pmcid}/supplementaryFiles", timeout=120, max_bytes=120_000_000)
        if sup is None:
            rec["supplementary_bundle"] = {"_status": "unavailable"}
        else:
            names = []
            try:
                import zipfile
                with zipfile.ZipFile(io.BytesIO(sup)) as z:
                    names = z.namelist()[:200]
                rec["supplementary_bundle"] = {"_status": "read", "n_files": len(names),
                                               "files": names}
            except Exception as exc:                 # noqa: BLE001
                rec["supplementary_bundle"] = {"_status": "not_a_zip", "error": str(exc)[:200],
                                               "bytes": len(sup)}
        # And the accession regex over the full text, which is the check the prior pass ran.
        ft = get(f"{EPMC}/{pmcid}/fullTextXML", timeout=120, max_bytes=40_000_000)
        if ft is None:
            rec["fulltext_accession_scan"] = {"_status": "unavailable"}
        else:
            txt = ft.decode("utf-8", "replace")
            pat = re.compile(r"\b(GSE\d{4,7}|E-[A-Z]{4}-\d+|PRJ[ENID][A-Z]\d+|SR[PXR]\d{5,9}|"
                             r"EGA[SD]\d{6,}|CRA\d{5,7}|HRA\d{5,7})\b")
            found = sorted(set(pat.findall(txt)))
            rec["fulltext_accession_scan"] = {
                "_status": "read", "n_chars": len(txt), "accessions_found": found,
                "⚠": "an accession absent from the rendered full text is an ABSENT READING about "
                     "the rendering, not a reading that no data were deposited.",
            }
        out["papers"][pmcid] = rec
    out["_status"] = "read"
    return out


def probe_gsa():
    """China National GenBank / NGDC GSA. Records what is DEPOSITED, and — the decision-relevant
    part — whether it is processed peaks or raw reads. Raw FASTQ is not analysable at $0 on a CPU
    runner and this file says so rather than implying the data were unavailable."""
    out = {"_what": "NGDC Genome Sequence Archive, the Schwann-cell NR4A3 ChIP-seq (PMID "
                    "42028030). ⚠ GSA archives RAW READS. Processed peak calls are deposited "
                    "only if the authors chose to; alignment + peak calling from FASTQ is not a "
                    "$0 CPU-runner operation and is recorded as an instrument limit, never as an "
                    "absence of data.",
           "accessions": {}, "_status": "NOT_RUN"}
    for acc, why in GSA_ACCESSIONS.items():
        rec = {"why": why}
        for url in (f"https://ngdc.cncb.ac.cn/gsa/browse/{acc}",
                    f"https://ngdc.cncb.ac.cn/gsa/search?searchTerm={acc}"):
            raw = get(url, timeout=90, max_bytes=20_000_000)
            if raw is None:
                continue
            html = raw.decode("utf-8", "replace")
            rec["_status"] = "read"
            rec["url"] = url
            rec["n_chars"] = len(html)
            rec["mentions_accession"] = acc in html
            rec["file_extensions_seen"] = sorted(set(
                m.lower() for m in re.findall(r"\.(fastq|fq|bam|bed|narrowPeak|bw|bigWig)\b",
                                              html, re.I)))
            rec["title_guess"] = (re.findall(r"<title>(.*?)</title>", html, re.S) or [""])[0
                                                                                          ][:200]
            break
        rec.setdefault("_status", "unreachable")
        out["accessions"][acc] = rec
    out["_status"] = "read"
    return out


def probe_other_catalogues():
    out = {"_what": "Other uniformly reprocessed human TF ChIP-seq catalogues. Attempted and "
                    "recorded so 'we did not look' and 'we looked and it is not there' are "
                    "different facts in this file.",
           "remap": {}, "encode": {}, "_status": "read"}
    for tf in PARALOGUES:
        got = None
        for pat in REMAP_PATTERNS:
            url = pat.format(tf=tf)
            raw = get(url, timeout=90, max_bytes=200_000_000)
            if raw is not None:
                got = {"url": url, "bytes": len(raw)}
                # keep the bytes for the peak loader
                out.setdefault("_remap_blobs", {})[tf] = raw
                break
        out["remap"][tf] = got or {"_status": "not_found_at_any_attempted_url"}
        d = get_json(ENCODE_SEARCH.format(tf=tf), timeout=90)
        if d is None:
            out["encode"][tf] = {"_status": "failed_or_none"}
        else:
            gr = d.get("@graph") or []
            out["encode"][tf] = {"_status": "read", "n_experiments": len(gr),
                                 "accessions": [g.get("accession") for g in gr][:40]}
    return out


# =============================================================================================
# PART 2 — peaks.
# =============================================================================================

def parse_bed(raw, source):
    """BED -> [(chrom, start0, end0, score)]. Rejects a header/track line rather than parsing it
    as a coordinate, and records how many lines it could not read."""
    if raw is None:
        return [], {"_status": "absent"}
    if raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except Exception as exc:                     # noqa: BLE001
            return [], {"_status": "ungzip_failed", "error": str(exc)[:200]}
    peaks, bad, n = [], 0, 0
    for ln in raw.decode("utf-8", "replace").splitlines():
        if not ln or ln.startswith(("#", "track", "browser")):
            continue
        n += 1
        f = ln.split("\t")
        if len(f) < 3:
            bad += 1
            continue
        try:
            s, e = int(f[1]), int(f[2])
        except ValueError:
            bad += 1
            continue
        if e <= s:
            bad += 1
            continue
        sc = None
        if len(f) > 4:
            try:
                sc = float(f[4])
            except ValueError:
                sc = None
        peaks.append((norm_chrom(f[0]), s, e, sc))
    return peaks, {"_status": "read", "source": source, "n_lines": n, "n_peaks": len(peaks),
                   "n_unparseable": bad,
                   "_coordinate_convention": "BED, 0-based half-open — as read, never shifted"}


def fetch_chip_atlas_peaks(experiments, max_experiments=40):
    """Per-SRX peak BEDs from ChIP-Atlas, for the experiments its metadata says exist."""
    out = {}
    for e in experiments[:max_experiments]:
        srx, genome = e.get("srx"), e.get("genome")
        if not srx or genome not in BUILDS:
            out[srx or "?"] = {"_status": "skipped",
                               "why": f"genome {genome!r} is not one this module intersects "
                                      f"({sorted(BUILDS)}); no liftover is performed"}
            continue
        url = CHIP_ATLAS_BED.format(genome=genome, th=CHIP_ATLAS_THRESHOLD, srx=srx)
        raw = get(url, timeout=180, max_bytes=200_000_000)
        peaks, diag = parse_bed(raw, url)
        out[srx] = {"antigen": e.get("antigen"), "genome": genome,
                    "cell_type": e.get("cell_type"),
                    "cell_type_class": e.get("cell_type_class"),
                    "qc": e.get("qc"), "peaks": peaks, "diag": diag,
                    "_status": diag["_status"]}
    return out


# =============================================================================================
# DERIVE — everything below runs offline from the inputs cache.
# =============================================================================================

def _score_locus(peaks, gene, build):
    """One peak set against one gene, in BOTH windows."""
    prom = promoter_window_bed(gene)
    body = genebody_window_bed(gene)
    chrom = gene["chrom"]
    tss0 = ens_to_bed(tss_of(gene), tss_of(gene))[0]
    p_hits = intersect_locus(peaks, (chrom,) + prom, build, build)
    b_hits = intersect_locus(peaks, (chrom,) + body, build, build)
    nearest = nearest_peak_distance(peaks, chrom, tss0)
    scores = [h["score"] for h in p_hits if h["score"] is not None]
    return {
        "chrom": chrom, "strand": gene["strand"],
        "promoter_window_bed": list(prom),
        "genebody_window_bed": list(body),
        "n_peaks_promoter_window": len(p_hits),
        "n_peaks_genebody_window": len(b_hits),
        "max_score_promoter_window": max(scores) if scores else None,
        "peaks_promoter_window": p_hits[:12],
        "nearest_peak_distance_to_tss_bp": nearest,
        "_nearest_is_absent_reading": nearest is None,
    }


def derive(cache):
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    art = {
        "_what": "Is RET a direct transcriptional target of NR4A3? Measured ChIP-seq occupancy "
                 "at the RET locus, with the paralogue overlap, on a stated genome build.",
        "_framing": FRAMING,
        "_lane": "emc-unexplored-treatment-lanes.md §3.1 / emc-ret-lane.md §2d next-step 1",
        "_sibling_instrument": "emc_ret_target_scan.py — the NBRE motif scan. Different question, "
                               "allowed to disagree.",
        "_generated_from": os.path.basename(INPUTS),
        "generated_utc": now,
        "_language_discipline": (
            "Nothing in this file asserts that any RET inhibitor is selective for, effective in, "
            "safe in, or ready for extraskeletal myxoid chondrosarcoma, and nothing here "
            "recommends giving any agent to any patient. No EMC patient has received a selective "
            "RET inhibitor."),
    }

    if not cache or cache.get("_status") == "NOT_RUN":
        art["part_0_genome_build"] = {"_status": "NOT_RUN"}
        art["part_1_datasets"] = {"_status": "NOT_RUN"}
        art["part_2_intersection"] = {
            "_status": "NOT_RUN",
            "why": "no inputs cache is present. ⚠ ABSENT READING — this says nothing about "
                   "whether NR4A3 binds RET.",
            "verdict": None}
        art["part_3_paralogue_overlap"] = {"_status": "NOT_RUN", "verdict": None}
        art["verdict"] = None
        return art

    art["part_0_genome_build"] = cache.get("build_reconciliation") or {"_status": "NOT_RUN"}
    art["part_1_datasets"] = {
        "_what": "Every catalogue queried, every dataset found, characterised BEFORE anything was "
                 "built on it (CLAUDE.md §6).",
        "chip_atlas": {k: v for k, v in (cache.get("chip_atlas") or {}).items()
                       if k != "experiments"} or {"_status": "NOT_RUN"},
        "chip_atlas_experiments": (cache.get("chip_atlas") or {}).get("experiments", []),
        "chip_atlas_target_tables": cache.get("chip_atlas_target_tables")
        or {"_status": "NOT_RUN"},
        "geo": cache.get("geo") or {"_status": "NOT_RUN"},
        "geo_supplementary": cache.get("geo_supplementary") or {},
        "geo_series_builds": cache.get("geo_series_builds") or {},
        "paper_data_availability": cache.get("papers") or {"_status": "NOT_RUN"},
        "gsa": cache.get("gsa") or {"_status": "NOT_RUN"},
        "other_catalogues": cache.get("other_catalogues") or {"_status": "NOT_RUN"},
        "_retrieval_attempts": cache.get("attempts", [])[-400:],
    }

    genes = cache.get("genes") or {}
    peaksets = cache.get("peaksets") or {}
    usable = {k: v for k, v in peaksets.items()
              if v.get("_status") == "read" and v.get("peaks")}

    if not usable:
        art["part_2_intersection"] = {
            "_status": "NO_PEAK_SET_RETRIEVED",
            "n_peaksets_attempted": len(peaksets),
            "why": ("no peak set was retrieved that this module can intersect. ⛔ THIS IS AN "
                    "ABSENT READING, NOT A NEGATIVE: it says the instrument found no reachable "
                    "peak file, and says nothing whatsoever about whether NR4A3 occupies RET. "
                    "The per-endpoint statuses are in part_1_datasets._retrieval_attempts."),
            "verdict": None}
        art["part_3_paralogue_overlap"] = {"_status": "NO_PEAK_SET_RETRIEVED", "verdict": None}
        art["verdict"] = None
        art["_what_this_cannot_conclude"] = _cannot_conclude()
        return art

    # ---- the per-peakset, per-locus table -----------------------------------------------------
    per_set = {}
    for sid, ps in sorted(usable.items()):
        build = ps.get("genome")
        gset = genes.get(build) or {}
        if build not in BUILDS or not gset:
            per_set[sid] = {"_status": "no_loci_on_this_build", "genome": build}
            continue
        rows, ctrl = {}, {}
        for sym in LOCI:
            g = gset.get(sym)
            if not g:
                rows[sym] = {"_status": "locus_not_resolved",
                             "⚠": "the gene's coordinates were not retrieved on this build; this "
                                  "is an absent reading, not an absence of binding"}
                continue
            rows[sym] = _score_locus(ps["peaks"], g, build)
            rows[sym]["_why_this_locus"] = LOCI[sym]
        for sym in KNOWN_POSITIVE_CONTROLS:
            r = rows.get(sym) or {}
            ctrl[sym] = r.get("n_peaks_promoter_window")
        bg = _background_rank(ps["peaks"], gset, build)
        per_set[sid] = {
            "_status": "read",
            "antigen": ps.get("antigen"), "genome": build,
            "cell_type": ps.get("cell_type"), "cell_type_class": ps.get("cell_type_class"),
            "qc": ps.get("qc"),
            "n_peaks_total": len(ps["peaks"]),
            "loci": rows,
            "positive_control_peak_counts": ctrl,
            "positive_control_verdict": _control_verdict(ctrl, rows),
            "background": bg,
        }

    art["part_2_intersection"] = {
        "_question": "Does a measured NR4A1/NR4A2/NR4A3 peak fall in RET's regulatory window?",
        "_windows": {
            "promoter": f"-{WINDOW_UPSTREAM} / +{WINDOW_DOWNSTREAM} around the TSS, strand-aware. "
                        f"⛔ Imported from emc_ret_target_scan, not re-typed: the asymmetry exists "
                        f"because RET's only validated distal element (HOXB5 MCS+9.7, PMID "
                        f"24794774) is in the first intron.",
            "genebody": "gene body +/- 10 kb — reported ALONGSIDE the promoter window so a "
                        "reading cannot be an artefact of one window choice.",
            "⚠_still_bounded": "a window is a scope choice; an element outside it is untested by "
                               "construction, and a null here is a null WITHIN this window.",
        },
        "_status": "read",
        "per_peakset": per_set,
        "ret_summary": _ret_summary(per_set),
    }
    art["part_3_paralogue_overlap"] = _paralogue_block(usable, per_set, genes)
    art["verdict"] = _verdict(art)
    art["_what_this_cannot_conclude"] = _cannot_conclude()
    return art


def _background_rank(peaks, gset, build):
    """RET's rank among the fixed-seed background panel, by promoter-window peak count.

    ⭐ THE PANEL IS NOT CHOSEN HERE. It is `emc_ret_target_scan.background_symbols()` — a
    fixed-seed sample of the 1,299 symbols this repository already committed for the ATR concept
    universe — so it cannot have been picked to flatter or damage RET.
    """
    bg_syms, bg_diag = background_symbols()
    resolved = [s for s in bg_syms if s in gset]
    counts = []
    for s in resolved:
        r = _score_locus(peaks, gset[s], build)
        counts.append((s, r["n_peaks_promoter_window"]))
    ret = gset.get("RET")
    ret_n = _score_locus(peaks, ret, build)["n_peaks_promoter_window"] if ret else None
    n_ge = sum(1 for _s, c in counts if ret_n is not None and c >= ret_n)
    n_hit = sum(1 for _s, c in counts if c > 0)
    return {
        "_what": "RET against a background panel nobody in this lane chose.",
        "panel_source": bg_diag,
        "n_panel_requested": len(bg_syms),
        "n_panel_resolved_on_this_build": len(resolved),
        "n_panel_genes_with_a_promoter_window_peak": n_hit,
        "fraction_of_panel_with_a_peak": round(n_hit / len(resolved), 4) if resolved else None,
        "RET_n_peaks_promoter_window": ret_n,
        "n_panel_genes_with_at_least_RETs_count": n_ge,
        "empirical_p_RET_vs_panel": (round((n_ge + 1) / (len(resolved) + 1), 4)
                                     if resolved and ret_n is not None else None),
        "_p_convention": "(ge+1)/(n+1), never ge/n — it can never print a 0 the panel size does "
                         "not support.",
        "⚠": "background genes differ in chromatin accessibility, mappability and GC. This rank "
             "is a comparison against genes chosen without reference to RET; it is not a "
             "composition-matched null.",
    }


def _control_verdict(ctrl, rows):
    hits = {k: v for k, v in ctrl.items() if v}
    if hits:
        return {"state": "A KNOWN POSITIVE IS RECOVERED",
                "recovered": sorted(hits),
                "reading": "this peak set puts a peak at a locus a published chromatin "
                           "experiment already placed an NR4A3 protein at, so a RET reading from "
                           "it is interpretable."}
    resolved = [k for k in KNOWN_POSITIVE_CONTROLS
                if (rows.get(k) or {}).get("_status") != "locus_not_resolved"]
    return {"state": "NO KNOWN POSITIVE RECOVERED",
            "controls_resolved": resolved,
            "⛔ reading": "this peak set does not put a peak at SEMA3C or ENO3 either. A NULL AT "
                         "RET FROM THIS PEAK SET IS THEREFORE UNINTERPRETABLE — it is equally "
                         "consistent with the assay, the cell type, or the threshold. It is NOT "
                         "evidence that NR4A3 does not bind RET."}


def _ret_summary(per_set):
    rows = []
    for sid, ps in sorted(per_set.items()):
        if ps.get("_status") != "read":
            continue
        r = (ps.get("loci") or {}).get("RET") or {}
        rows.append({
            "peakset": sid, "antigen": ps.get("antigen"), "genome": ps.get("genome"),
            "cell_type": ps.get("cell_type"),
            "n_peaks_total": ps.get("n_peaks_total"),
            "RET_promoter_window_peaks": r.get("n_peaks_promoter_window"),
            "RET_genebody_window_peaks": r.get("n_peaks_genebody_window"),
            "RET_nearest_peak_to_tss_bp": r.get("nearest_peak_distance_to_tss_bp"),
            "positive_control": (ps.get("positive_control_verdict") or {}).get("state"),
            "empirical_p_vs_background": (ps.get("background") or {})
            .get("empirical_p_RET_vs_panel"),
        })
    n_pos = sum(1 for r in rows if (r["RET_promoter_window_peaks"] or 0) > 0)
    n_interp = sum(1 for r in rows if r["positive_control"] == "A KNOWN POSITIVE IS RECOVERED")
    return {"rows": rows, "n_peaksets": len(rows),
            "n_with_a_RET_promoter_peak": n_pos,
            "n_peaksets_whose_null_is_interpretable": n_interp,
            "⛔": "a null from a peak set that recovers no known positive is uninterpretable and "
                 "is counted separately for exactly that reason."}


def _paralogue_block(usable, per_set, genes):
    """NR4A1 / NR4A2 / NR4A3 at RET, and the genome-wide sharing rate that makes it readable.

    ⭐ WHY THE GENOME-WIDE RATE IS PART OF THE ANSWER. 'All three paralogues have a peak at RET'
    means one thing if the three share 5 % of their peaks and something completely different if
    they share 80 %. This repository has only ever argued paralogue selectivity from domain
    sequence identity; a matched peak-set overlap is a DIRECT empirical measure and no identity
    calculation can produce it.
    """
    by_ag = {}
    for sid, ps in usable.items():
        ag = (ps.get("antigen") or "").upper()
        if ag in PARALOGUES:
            by_ag.setdefault(ag, []).append(sid)

    at_ret = {}
    for ag in PARALOGUES:
        rows = []
        for sid in by_ag.get(ag, []):
            r = ((per_set.get(sid) or {}).get("loci") or {}).get("RET") or {}
            rows.append({"peakset": sid,
                         "cell_type": (per_set.get(sid) or {}).get("cell_type"),
                         "genome": (per_set.get(sid) or {}).get("genome"),
                         "n_peaks_promoter_window": r.get("n_peaks_promoter_window"),
                         "positive_control": ((per_set.get(sid) or {})
                                              .get("positive_control_verdict") or {}).get(
                                                  "state")})
        at_ret[ag] = {"n_peaksets": len(rows), "rows": rows,
                      "any_promoter_peak_at_RET": any((x["n_peaks_promoter_window"] or 0) > 0
                                                      for x in rows) if rows else None}

    # Genome-wide pairwise sharing, computed only between peak sets on the SAME build.
    pair = {}
    for a in PARALOGUES:
        for b in PARALOGUES:
            if a >= b:
                continue
            best = None
            for sa in by_ag.get(a, []):
                for sb in by_ag.get(b, []):
                    pa, pb = usable[sa], usable[sb]
                    if pa.get("genome") != pb.get("genome"):
                        continue
                    frac = _fraction_overlapping(pa["peaks"], pb["peaks"])
                    cand = {"peakset_a": sa, "peakset_b": sb, "genome": pa.get("genome"),
                            "cell_type_a": pa.get("cell_type"), "cell_type_b": pb.get("cell_type"),
                            "n_peaks_a": len(pa["peaks"]), "n_peaks_b": len(pb["peaks"]),
                            "fraction_of_a_overlapped_by_b": frac,
                            "same_cell_type": pa.get("cell_type") == pb.get("cell_type")}
                    if best is None or (cand["same_cell_type"] and not best["same_cell_type"]):
                        best = cand
            pair[f"{a}_vs_{b}"] = best or {
                "_status": "not_computable",
                "why": "no pair of peak sets for these two antigens exists on the same genome "
                       "build. ⚠ ABSENT READING — it says nothing about how much the two share."}

    shared = [ag for ag in PARALOGUES if at_ret.get(ag, {}).get("any_promoter_peak_at_RET")]
    if not any(at_ret.get(ag, {}).get("n_peaksets") for ag in PARALOGUES):
        state = "NOT_MEASURED"
        reading = ("no paralogue peak set was retrieved. ⚠ ABSENT READING, not a reading of "
                   "absence.")
    elif len(shared) == 0:
        state = "NO PARALOGUE SHOWS A PROMOTER-WINDOW PEAK AT RET"
        reading = ("read this against each peak set's positive control: a null from a set that "
                   "recovers no known positive says nothing.")
    elif len(shared) == 3:
        state = "ALL THREE PARALOGUES OCCUPY RET'S PROMOTER WINDOW"
        reading = ("a family-shared element. This is the reading LEAST useful to a "
                   "paralogue-selective strategy and MOST useful to the biology: it says the "
                   "site is an NR4A-family site rather than an NR4A3-specific one. Grade it "
                   "against the genome-wide sharing rate below before calling it either.")
    else:
        state = f"OCCUPIED BY {'+'.join(shared)} AND NOT BY THE OTHERS"
        reading = ("the reading a paralogue-selective strategy would want. ⚠ It rests on peak "
                   "CALLING at a fixed threshold, so 'absent in paralogue X' can be a "
                   "sub-threshold peak. Grade it against the genome-wide sharing rate.")
    return {
        "_question": "Is a peak at RET shared by NR4A1/NR4A2/NR4A3, or is it NR4A3's alone?",
        "_why_it_matters": "a peak all three share says something different from one only NR4A3 "
                           "has — for the biology and for every paralogue-selectivity argument "
                           "this repository has so far made from sequence identity alone.",
        "at_RET": at_ret,
        "genome_wide_pairwise_sharing": pair,
        "state": state,
        "reading": reading,
        "⛔ what_this_is_not": "wild-type paralogues in a non-EMC cell type. It is not a "
                              "measurement of what EWSR1::NR4A3 binds, and not a selectivity "
                              "claim about any molecule.",
    }


def _fraction_overlapping(a, b, cap=400000):
    """Fraction of A's peaks overlapped by at least one of B's. Sweep-line, no numpy."""
    if not a or not b:
        return None
    from bisect import bisect_right
    byc = {}
    for (c, s, e, _sc) in b[:cap]:
        byc.setdefault(c, []).append((s, e))
    starts, maxend = {}, {}
    for c, iv in byc.items():
        iv.sort()
        starts[c] = [s for s, _e in iv]
        m, run = [], -1
        for _s, e in iv:
            run = max(run, e)
            m.append(run)
        maxend[c] = m
    hit = 0
    for (c, s, e, _sc) in a[:cap]:
        st = starts.get(c)
        if not st:
            continue
        i = bisect_right(st, e) - 1
        if i >= 0 and maxend[c][i] > s:
            hit += 1
    return round(hit / min(len(a), cap), 4)


def _verdict(art):
    """⛔ NO READING ⇒ NO VERDICT. Held by a test."""
    p2 = art.get("part_2_intersection") or {}
    if p2.get("_status") != "read":
        return None
    s = p2.get("ret_summary") or {}
    if not s.get("n_peaksets"):
        return None
    n_pos, n_interp = s.get("n_with_a_RET_promoter_peak", 0), \
        s.get("n_peaksets_whose_null_is_interpretable", 0)
    par = (art.get("part_3_paralogue_overlap") or {}).get("state")
    if n_pos > 0:
        headline = (f"MEASURED NR4A OCCUPANCY AT THE RET LOCUS IN {n_pos} OF "
                    f"{s['n_peaksets']} PUBLIC PEAK SETS.")
        strength = ("⭐ A PRIOR, NOT A DEMONSTRATION. The protein assayed is WILD-TYPE NR4A in a "
                    "cell type that is not EMC. It is the strongest form the question can take "
                    "at $0 — measured occupancy by the protein whose DNA-binding domain the "
                    "fusion retains — and it is not evidence that EWSR1::NR4A3 binds RET in an "
                    "EMC tumour, which no existing dataset can show.")
    elif n_interp > 0:
        headline = (f"NO NR4A PEAK AT THE RET LOCUS IN ANY OF {s['n_peaksets']} PUBLIC PEAK SETS, "
                    f"{n_interp} OF WHICH RECOVER A KNOWN POSITIVE CONTROL.")
        strength = ("A NEGATIVE AT ITS TRUE STRENGTH: RET is not occupied by wild-type NR4A in "
                    "the cell types assayed, by peak sets that do detect published NR4A3 target "
                    "loci. ⚠ It remains a statement about those cell types' chromatin. The RET "
                    "locus may be closed in them and open in EMC, and no public dataset can "
                    "settle that.")
    else:
        headline = (f"NO NR4A PEAK AT RET IN ANY OF {s['n_peaksets']} PEAK SETS — AND NONE OF "
                    f"THEM RECOVERS A KNOWN POSITIVE CONTROL.")
        strength = ("⛔ UNINTERPRETABLE, AND RECORDED AS UNINTERPRETABLE RATHER THAN AS A "
                    "NEGATIVE. An instrument that does not recover SEMA3C or ENO3 cannot be read "
                    "as having excluded RET.")
    return {"headline": headline, "strength": strength, "paralogue_state": par,
            "⛔ scope": "wild-type NR4A cistromes in non-EMC cells. No EWSR1::NR4A3 cistrome "
                       "exists (emc-ret-lane.md §2d), and nothing here is an efficacy, "
                       "selectivity, safety, therapeutic-window or clinical-readiness claim."}


def _cannot_conclude():
    return {
        "not_the_fusion": "every peak set is WILD-TYPE NR4A. PMID 31020999 measured that the "
                          "EWSR1 and TAF15 chimeras differ from each other in DNA binding at a "
                          "validated NBRE target, so wild-type occupancy is a prior for the "
                          "fusion and never a substitute for it.",
        "not_EMC_chromatin": "the cell types assayed are not EMC. A locus closed in them may be "
                             "open in EMC and the reverse.",
        "not_function": "occupancy is not transactivation. The ENO3 precedent needed luciferase "
                        "on top of ChIP (PMID 26310886).",
        "not_activation": "nothing here measures RET protein or phospho-RET in any EMC tumour. "
                          "The activation bar — the blinded TMA that decided MET in clear cell "
                          "sarcoma, PMID 34885165 — is still untaken for RET in EMC "
                          "(emc-ret-lane.md §3), and this module does not change that.",
        "not_clinical": "nothing here asserts efficacy, selectivity, safety, a therapeutic "
                        "window or clinical readiness for any agent in EMC.",
    }


# =============================================================================================
# FETCH — CI only.
# =============================================================================================

def fetch():
    cache = {"_generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
             "_budget_s": NET_BUDGET_S}

    # ---- part 1 first: characterise BEFORE building on anything ------------------------------
    cache["chip_atlas"] = discover_chip_atlas()
    cache["geo"] = discover_geo()
    cache["papers"] = paper_cross_references()
    cache["gsa"] = probe_gsa()
    other = probe_other_catalogues()
    remap_blobs = other.pop("_remap_blobs", {})
    cache["other_catalogues"] = other

    cache["chip_atlas_target_tables"] = fetch_chip_atlas_target_tables()

    # GEO supplementary listings for every series a query returned that looks like a ChIP series,
    # plus the build READ FROM THE SERIES' OWN RECORD for any that carries a peak-like file.
    sup, builds = {}, {}
    for acc, s in sorted((cache["geo"].get("series") or {}).items()):
        gse = acc if acc.startswith("GSE") else (s.get("gse") and f"GSE{s['gse']}")
        if not gse:
            continue
        blob = f"{s.get('title','')} {s.get('gdsType','')} {s.get('summary','')}".lower()
        if not any(t in blob for t in ("chip", "genome binding", "occupancy")):
            continue
        sup[gse] = list_geo_supplementary(gse)
        if sup[gse].get("peak_like"):
            builds[gse] = geo_build_for_series(gse, geo_series_gsms(gse))
        if len(sup) >= 25:
            break
    cache["geo_supplementary"] = sup
    cache["geo_series_builds"] = builds

    # ---- part 0: loci on every build, from two independent sources ---------------------------
    bg_syms, _ = background_symbols()
    want = sorted(set(list(LOCI) + list(MOTIF_FOCUS_GENES) + bg_syms))
    genes, gdiag = {}, {}
    for build in BUILDS:
        g, d = fetch_gene_spans(want, build)
        genes[build] = g
        gdiag[build] = d
    ncbi, ndiag = fetch_ncbi_gene_spans(sorted(LOCI))
    cache["genes"] = genes
    cache["gene_lookup_diagnostics"] = {"ensembl_per_build": gdiag, "ncbi_gene": ndiag}
    cache["build_reconciliation"] = reconcile_builds(genes, ncbi)

    # ---- part 2: the peaks --------------------------------------------------------------------
    peaksets = {}
    ca = cache["chip_atlas"]
    if ca.get("_status") == "read" and ca.get("experiments"):
        peaksets.update(fetch_chip_atlas_peaks(ca["experiments"]))
    for tf, raw in remap_blobs.items():
        peaks, diag = parse_bed(raw, f"ReMap2022 {tf}")
        peaksets[f"REMAP2022_{tf}"] = {
            "antigen": tf, "genome": "hg38", "cell_type": "ReMap 2022 merged catalogue",
            "cell_type_class": "merged across every ReMap dataset for this factor",
            "qc": None, "peaks": peaks, "diag": diag, "_status": diag["_status"]}
    # GEO supplementary peak files, if any series carried one. The build comes from the series'
    # OWN record (`geo_build_for_series`); a file whose build could not be read is retrieved,
    # recorded, and NOT intersected.
    for gse, s in sorted(sup.items()):
        b = (builds.get(gse) or {})
        for fn in (s.get("peak_like") or [])[:6]:
            raw = get(s["url"] + fn, timeout=180, max_bytes=200_000_000)
            peaks, diag = parse_bed(raw, f"{gse}:{fn}")
            if not peaks:
                continue
            ag = next((p for p in PARALOGUES if p.lower() in fn.lower()), None)
            ok = b.get("_status") == "read" and b.get("build") in BUILDS
            peaksets[f"{gse}:{fn}"] = {
                "antigen": ag,
                "genome": b.get("build") if ok else None,
                "cell_type": (cache["geo"].get("series") or {}).get(gse, {}).get("title"),
                "cell_type_class": "GEO supplementary peak call (the depositors' own, not "
                                   "uniformly reprocessed)",
                "qc": None, "peaks": peaks, "diag": diag,
                "build_evidence": b,
                "_status": "read" if ok else "read_but_build_unknown",
                "⛔": None if ok else
                     ("a GEO supplementary peak file carries no build inside the file. The "
                      "series record did not name one unambiguously, so this peak set is NOT "
                      "intersected — an intersection on an assumed build is the defect this "
                      "module refuses, and on chr10 it would not throw, it would silently "
                      "report another locus.")}
    cache["peaksets"] = peaksets
    cache["attempts"] = ATTEMPTS
    cache["_budget_spent_s"] = BUDGET.spent()
    return cache


# =============================================================================================
# SELFTEST
# =============================================================================================

def selftest():
    ok, fails = 0, []

    def check(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append(name)

    # --- the converter ------------------------------------------------------------------------
    check("1bp feature keeps width 1", ens_to_bed(100, 100) == (99, 100))
    check("width preserved", (lambda t: t[1] - t[0] == 11)(ens_to_bed(100, 110)))
    check("round trip", bed_to_ens(*ens_to_bed(1234, 5678)) == (1234, 5678))
    try:
        ens_to_bed(200, 100)
        check("inverted interval raises", False)
    except ValueError:
        check("inverted interval raises", True)
    try:
        bed_to_ens(10, 10)
        check("empty BED raises", False)
    except ValueError:
        check("empty BED raises", True)

    # --- overlap semantics ---------------------------------------------------------------------
    check("adjacency is not overlap", not overlaps(0, 10, 10, 20))
    check("1bp overlap is overlap", overlaps(0, 11, 10, 20))
    check("containment", overlaps(5, 6, 0, 100))
    check("overlap_bp exact", overlap_bp(0, 10, 5, 20) == 5)
    check("overlap_bp zero on adjacency", overlap_bp(0, 10, 10, 20) == 0)

    # --- chromosome naming ---------------------------------------------------------------------
    check("chrom norm", norm_chrom("10") == norm_chrom("chr10") == norm_chrom("CHR10") == "chr10")

    # --- cross-build refusal -------------------------------------------------------------------
    try:
        intersect_locus([("chr10", 1, 2, None)], ("chr10", 0, 10), "hg19", "hg38")
        check("cross-build intersection refused", False)
    except ValueError:
        check("cross-build intersection refused", True)

    # --- strand-aware window --------------------------------------------------------------------
    plus = {"chrom": "chr10", "start": 1_000_000, "end": 1_050_000, "strand": 1}
    minus = {"chrom": "chr10", "start": 1_000_000, "end": 1_050_000, "strand": -1}
    wp, wm = promoter_window_bed(plus), promoter_window_bed(minus)
    check("plus-strand window starts upstream of the TSS",
          wp[0] == 1_000_000 - WINDOW_UPSTREAM - 1)
    check("minus-strand window is mirrored about the TSS",
          wm[1] == 1_050_000 + WINDOW_UPSTREAM)
    check("both windows have the same width", (wp[1] - wp[0]) == (wm[1] - wm[0]))

    # --- an empty cache can never emit a verdict -------------------------------------------------
    a = derive({})
    check("empty cache -> no verdict", a["verdict"] is None)
    check("empty cache -> NOT_RUN", a["part_2_intersection"]["_status"] == "NOT_RUN")
    a2 = derive({"_generated_utc": "x", "peaksets": {}, "genes": {}})
    check("no peakset -> no verdict", a2["verdict"] is None)
    check("no peakset -> NO_PEAK_SET_RETRIEVED",
          a2["part_2_intersection"]["_status"] == "NO_PEAK_SET_RETRIEVED")

    # --- a peak set with no recovered control cannot produce a clean negative ---------------------
    synth = _synthetic_cache(ret_peak=False, control_peak=False)
    a3 = derive(synth)
    check("no control + no RET peak -> UNINTERPRETABLE",
          "UNINTERPRETABLE" in (a3["verdict"] or {}).get("strength", ""))
    synth2 = _synthetic_cache(ret_peak=False, control_peak=True)
    a4 = derive(synth2)
    check("control recovered + no RET peak -> a real negative",
          "NEGATIVE AT ITS TRUE STRENGTH" in (a4["verdict"] or {}).get("strength", ""))
    synth3 = _synthetic_cache(ret_peak=True, control_peak=True)
    a5 = derive(synth3)
    check("RET peak -> a prior, never a demonstration",
          "PRIOR, NOT A DEMONSTRATION" in (a5["verdict"] or {}).get("strength", ""))
    check("a RET peak is counted",
          a5["part_2_intersection"]["ret_summary"]["n_with_a_RET_promoter_peak"] == 1)

    print(f"selftest: {ok} passed, {len(fails)} failed")
    for f in fails:
        print("  FAIL:", f)
    return 0 if not fails else 1


def _synthetic_cache(ret_peak, control_peak):
    """A minimal cache used ONLY by --selftest, to prove the verdict logic cannot be bypassed."""
    genes = {"hg38": {
        "RET": {"chrom": "chr10", "start": 43_000_000, "end": 43_050_000, "strand": 1,
                "assembly_name": "GRCh38"},
        "SEMA3C": {"chrom": "chr7", "start": 80_000_000, "end": 80_100_000, "strand": 1,
                   "assembly_name": "GRCh38"},
        "ENO3": {"chrom": "chr17", "start": 4_900_000, "end": 4_910_000, "strand": 1,
                 "assembly_name": "GRCh38"},
    }}
    peaks = [("chr1", 1000, 1200, 100.0)]
    if ret_peak:
        peaks.append(("chr10", 43_000_000, 43_000_300, 250.0))
    if control_peak:
        peaks.append(("chr7", 79_999_900, 80_000_200, 300.0))
    return {"_generated_utc": "selftest", "genes": genes,
            "peaksets": {"SYNTH": {"antigen": "NR4A3", "genome": "hg38",
                                   "cell_type": "synthetic", "cell_type_class": "synthetic",
                                   "qc": None, "peaks": peaks,
                                   "diag": {"_status": "read"}, "_status": "read"}}}


# =============================================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.fetch:
        cache = fetch()
        with open(INPUTS, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=False, default=str)
        art = derive(cache)
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(art, fh, indent=1, sort_keys=False, default=str)
        print(json.dumps({"peaksets": len(cache.get("peaksets") or {}),
                          "chip_atlas": (cache.get("chip_atlas") or {}).get("n_matching"),
                          "budget_spent_s": cache.get("_budget_spent_s"),
                          "verdict": (art.get("verdict") or {}).get("headline")}, indent=1))
        return 0

    cache = {}
    if os.path.exists(INPUTS):
        with open(INPUTS, "r", encoding="utf-8") as fh:
            cache = json.load(fh)
    art = derive(cache)
    if args.check:
        if not os.path.exists(OUT):
            print("no artifact to check against")
            return 1
        with open(OUT, "r", encoding="utf-8") as fh:
            old = json.load(fh)
        a = {k: v for k, v in art.items() if k != "generated_utc"}
        b = {k: v for k, v in old.items() if k != "generated_utc"}
        same = json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True,
                                                                       default=str)
        print("REPRODUCES EXACTLY" if same else "DRIFT — the derive half is not reproducible")
        return 0 if same else 1
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(art, fh, indent=1, sort_keys=False, default=str)
    print(json.dumps({"verdict": (art.get("verdict") or {}).get("headline"),
                      "part_2": art["part_2_intersection"].get("_status")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
