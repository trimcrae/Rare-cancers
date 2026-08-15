#!/usr/bin/env python3
"""Recover NR4A3 fusion breakpoints from DEPOSITED RAW READS, not from published prose.

WHY THIS EXISTS. Junction-spanning ASOs need one reagent per distinct breakpoint, so patient
coverage is capped by how many breakpoints can be NAMED. Three literature sweeps (~1,030
open-access papers) produced seven exon-resolved junctions, and exactly one paper prints a
per-case exon table. Several cohorts report complete per-case PARTNER splits with no exons: the
assays resolved those breakpoints, the papers simply did not print them. Deposited reads are the
only remaining source that can add a junction, so this module reads them directly.

WHAT IT DOES. Targeted matching, not alignment. A read that crosses a fusion junction contains,
contiguously, the 3' end of a partner exon followed by the 5' start of an NR4A3 acceptor. Both
halves are already committed in this repository (`aso-premrna-sequences.json`: full pre-mRNA plus
exon spans for EWSR1, TAF15, TCF12, FUS, TFG and NR4A3), so the seam can be matched exactly with
no aligner, no index and no reference genome download.

⛔ WHAT IT IS NOT.
  * Not a fusion CALLER. It looks only for seams between a named partner exon and a named NR4A3
    acceptor. A novel partner, or a breakpoint inside an exon, is invisible to it BY DESIGN and
    a zero here is not evidence such a thing is absent.
  * Not a breakpoint DISTRIBUTION. One deposit is one or a few tumours; nothing here says how the
    next tumour breaks.
  * Not a coverage, efficacy, potency, safety, therapeutic-window or clinical-readiness claim.
  * Not a patient count. Runs are not samples and samples are not people.

⛔ THE FAILURE THIS MODULE IS BUILT AGAINST. "No junction read found" has two completely different
causes — the fusion is not there, or the deposit could not inform on it — and they must never
render alike. So every scan reports a DENOMINATOR: how many reads carry NR4A3 at all, and how many
carry each partner. A scan that saw no NR4A3 read whatsoever is UNINFORMATIVE, and says so; only a
scan with real NR4A3 depth and no seam is entitled to the word "absent", and even then only for
the seams it was looking for. An absent reading is not a reading of absence (CLAUDE.md §4).

⚠ AND THE ASSAY MUST BE READ BEFORE THE READS ARE. A processed expression matrix cannot carry a
breakpoint, and neither can a TARGETED probe assay: TempO-Seq emits one fixed ~50 nt amplicon per
probed gene, so no read in such a deposit can span from one gene into another however deep it is.
`assay_is_capable_of_spanning_a_junction()` is applied to a deposit's own metadata BEFORE any
scan, and refuses the scan rather than reporting a meaningless zero.

$0 — a GitHub-hosted CPU runner. Pure stdlib: no pip install, no aligner, no reference download.
The dev sandbox's egress proxy 403s NCBI/ENA on CONNECT, which is why this runs on a runner
(CLAUDE.md §6).
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
PREMRNA = os.path.join(HERE, "aso-premrna-sequences.json")
OUT = os.path.join(HERE, "emc-fusion-read-scan.json")
OUT_INPUTS = os.path.join(HERE, "emc-fusion-read-scan-inputs.json")
OUT_DEPOSITS = os.path.join(HERE, "emc-fusion-read-scan-deposits.json")

ENA_PORTAL = "https://www.ebi.ac.uk/ena/portal/api"
UA = "Rare-cancers/emc_fusion_read_scan (+https://github.com/trimcrae/Rare-cancers)"

# The partners this repository holds transcript sequence for. TCF12 is first on purpose: no
# exon-resolved TCF12::NR4A3 breakpoint exists in the literature at all.
PARTNERS = ["TCF12", "EWSR1", "TAF15", "FUS", "TFG"]
ACCEPTOR = "NR4A3"

# Acceptor sites. NR4A3 exon 3 is the common acceptor; exon 2 is used by at least one reported
# EWSR1 case; intron 2 is the acceptor of the TAF15 variant this repository prices an arm on.
# Exon numbers are 1-based against the committed transcript model.
ACCEPTOR_SITES = [
    ("NR4A3_exon2_start", "exon", 2),
    ("NR4A3_exon3_start", "exon", 3),
    ("NR4A3_intron2_start", "intron", 2),
]

MIN_FLANK = 16  # nt required on EACH side of the seam -> a 32 nt exact match
SEED = 16  # stage-A literal length
CHUNK = 8 << 20
CARRY = 4096


# ---------------------------------------------------------------------------- sequence utilities

_COMP = str.maketrans("ACGTNacgtn", "TGCANtgcan")


def revcomp(s: str) -> str:
    return s.translate(_COMP)[::-1]


def load_genes(path: str = PREMRNA) -> dict:
    with open(path) as fh:
        return json.load(fh)["genes"]


def exon_seq(gene: dict, exon_1based: int) -> str:
    """Exonic sequence of one exon, in transcript orientation."""
    spans = gene["exon_spans_0based_inclusive"]
    if not (1 <= exon_1based <= len(spans)):
        raise IndexError(f"exon {exon_1based} outside 1..{len(spans)}")
    a, b = spans[exon_1based - 1]
    return gene["sequence"][a : b + 1]


def intron_seq(gene: dict, intron_1based: int) -> str:
    """Intronic sequence FOLLOWING exon `intron_1based`, in transcript orientation."""
    spans = gene["exon_spans_0based_inclusive"]
    if not (1 <= intron_1based < len(spans)):
        raise IndexError(f"intron {intron_1based} outside 1..{len(spans) - 1}")
    end_prev = spans[intron_1based - 1][1]
    start_next = spans[intron_1based][0]
    if start_next <= end_prev + 1:
        return ""
    return gene["sequence"][end_prev + 1 : start_next]


def acceptor_starts(genes: dict, flank: int = MIN_FLANK) -> dict:
    """The first `flank` nt of every acceptor site, keyed by site name."""
    g = genes[ACCEPTOR]
    out = {}
    for name, kind, n in ACCEPTOR_SITES:
        seq = exon_seq(g, n) if kind == "exon" else intron_seq(g, n)
        if len(seq) >= flank:
            out[name] = seq[:flank].upper()
    return out


def donor_ends(genes: dict, flank: int = MIN_FLANK) -> dict:
    """The last `flank` nt of every exon of every partner, keyed 'GENE_exonN'."""
    out = {}
    for gname in PARTNERS:
        g = genes.get(gname)
        if not g:
            continue
        for i in range(1, len(g["exon_spans_0based_inclusive"]) + 1):
            seq = exon_seq(g, i)
            if len(seq) >= flank:
                out[f"{gname}_exon{i}"] = seq[-flank:].upper()
    return out


def wildtype_upstream(genes: dict, flank: int = MIN_FLANK) -> dict:
    """What legitimately precedes each acceptor site in the UNfused transcript.

    Without this the scan cannot tell a fusion read from an ordinary NR4A3 read, and ordinary
    NR4A3 reads are the common case in any NR4A3-expressing tumour.
    """
    g = genes[ACCEPTOR]
    out = {}
    for name, kind, n in ACCEPTOR_SITES:
        if kind == "exon":
            prev = exon_seq(g, n - 1) if n > 1 else ""
        else:
            prev = exon_seq(g, n)
        if len(prev) >= flank:
            out[name] = prev[-flank:].upper()
    return out


# ------------------------------------------------------------------------------- the assay gate


TARGETED_ASSAY_PATTERNS = [
    r"tempo[\s\-]?seq",
    r"targeted rna[\s\-]?seq",
    r"ampliseq",
    r"amplicon",
    r"\bpanel\b",
    r"capture[\s\-]?based",
]


def assay_is_capable_of_spanning_a_junction(metadata_blobs, read_length=None):
    """Decide, from a deposit's OWN metadata, whether a read could span a fusion junction.

    Returns (capable: bool|None, reason: str). None means CANNOT_DETERMINE — which is not the
    same as False and must not be rendered as one.
    """
    text = " ".join(str(b) for b in metadata_blobs if b).lower()
    if not text.strip():
        return None, "CANNOT_DETERMINE — no metadata text was readable"
    for pat in TARGETED_ASSAY_PATTERNS:
        m = re.search(pat, text)
        if m:
            return (
                False,
                "REFUSED — the deposit's own metadata names a TARGETED probe/amplicon assay "
                f"({m.group(0)!r}). Such a read is one fixed amplicon inside one gene and cannot "
                "cross into another gene, so a zero from scanning it would carry no information.",
            )
    if read_length is not None and read_length < 2 * MIN_FLANK:
        return (
            False,
            f"REFUSED — read length {read_length} nt cannot carry {MIN_FLANK} nt on each side of "
            f"a seam ({2 * MIN_FLANK} nt needed).",
        )
    if "rna-seq" in text or "transcriptomic" in text or "cdna" in text:
        return True, "whole-transcriptome RNA-seq; a read can in principle cross a junction"
    return None, "CANNOT_DETERMINE — metadata did not name an assay this module recognises"


# ------------------------------------------------------------------------------------- the scan


class JunctionScanner:
    """Two-stage targeted matcher.

    Stage A scans the decompressed byte stream for a small set of acceptor SEEDS with one
    compiled alternation, at C speed. Stage B runs only on the few hits, and is where the
    partner exon is actually identified. Doing it the other way round — enumerating every
    partner x acceptor seam and searching for all of them — is the same answer at ~50x the cost.
    """

    def __init__(self, genes, flank=MIN_FLANK):
        self.flank = flank
        self.acceptors = acceptor_starts(genes, flank)
        self.donors = donor_ends(genes, flank)
        self.wildtype = wildtype_upstream(genes, flank)
        # depth probes: an INTERNAL window of each gene, away from any boundary, so that a
        # negative result has a denominator.
        self.depth_probes = {}
        for gname in [ACCEPTOR] + PARTNERS:
            g = genes.get(gname)
            if not g:
                continue
            n_ex = len(g["exon_spans_0based_inclusive"])
            longest, seq = 0, ""
            for i in range(1, n_ex + 1):
                e = exon_seq(g, i)
                if len(e) > longest:
                    longest, seq = len(e), e
            if longest >= flank + 20:
                mid = len(seq) // 2
                self.depth_probes[gname] = seq[mid : mid + flank].upper()

        pats = {}
        for name, s in self.acceptors.items():
            pats[f"acc:{name}:+"] = s
            pats[f"acc:{name}:-"] = revcomp(s)
        for name, s in self.depth_probes.items():
            pats[f"depth:{name}:+"] = s
            pats[f"depth:{name}:-"] = revcomp(s)
        self.patterns = pats
        # longest-first so an alternation never prefers a shorter overlapping literal
        ordered = sorted(pats.items(), key=lambda kv: -len(kv[1]))
        self._names = [k for k, _ in ordered]
        self._rx = re.compile("|".join(f"({re.escape(v)})" for _, v in ordered).encode())
        self.reset()

    def reset(self):
        self.depth_counts = {k: 0 for k in self.depth_probes}
        self.acceptor_hits = {k: 0 for k in self.acceptors}
        self.junctions = {}
        self.wildtype_reads = {k: 0 for k in self.acceptors}
        self.n_stageA_hits = 0
        self.n_bytes = 0

    # -- stage B ------------------------------------------------------------------------------
    def classify(self, window: str, site: str, pos: int):
        """`window` is sequence context; `pos` is where the acceptor seed starts inside it."""
        upstream = window[:pos]
        if len(upstream) < self.flank:
            return None
        tail = upstream[-self.flank :].upper()
        wt = self.wildtype.get(site)
        if wt and tail == wt:
            self.wildtype_reads[site] += 1
            return None
        for dname, dseq in self.donors.items():
            if tail == dseq:
                return dname
        return None

    def _scan_text(self, text: str, offset_note=""):
        """Scan one decoded chunk. Sequence, header and quality lines are all present; a 16 nt
        ACGT literal cannot occur in a Phred line by construction of the alphabets, and every hit
        is re-verified against a parsed read window before it is counted as a junction."""
        b = text.encode()
        for m in self._rx.finditer(b):
            self.n_stageA_hits += 1
            idx = m.lastindex
            name = self._names[idx - 1] if idx else None
            if not name:
                continue
            kind, gene, strand = name.split(":")
            start = m.start()
            # recover the enclosing line, which for a FASTQ is the read
            ls = text.rfind("\n", 0, start) + 1
            le = text.find("\n", start)
            if le == -1:
                le = len(text)
            line = text[ls:le]
            if not line or set(line.upper()) - set("ACGTN"):
                continue  # not a sequence line
            if kind == "depth":
                self.depth_counts[gene] = self.depth_counts.get(gene, 0) + 1
                continue
            self.acceptor_hits[gene] = self.acceptor_hits.get(gene, 0) + 1
            read = line if strand == "+" else revcomp(line)
            seed = self.acceptors[gene]
            p = read.upper().find(seed)
            if p < 0:
                continue
            donor = self.classify(read.upper(), gene, p)
            if donor:
                key = f"{donor}__{gene}"
                rec = self.junctions.setdefault(
                    key,
                    {
                        "donor": donor,
                        "acceptor_site": gene,
                        "n_reads": 0,
                        "example_reads": [],
                        "seam_verbatim": self.donors[donor] + "|" + self.acceptors[gene],
                    },
                )
                rec["n_reads"] += 1
                if len(rec["example_reads"]) < 4:
                    rec["example_reads"].append(read.upper())

    def scan_stream(self, fh, budget_s=None, max_bytes=None, t0=None):
        t0 = t0 or time.time()
        carry = ""
        while True:
            if budget_s and (time.time() - t0) > budget_s:
                return "budget_exhausted"
            if max_bytes and self.n_bytes >= max_bytes:
                return "max_bytes_reached"
            raw = fh.read(CHUNK)
            if not raw:
                return "eof"
            self.n_bytes += len(raw)
            text = carry + raw.decode("ascii", "replace")
            self._scan_text(text)
            carry = text[-CARRY:]


# ------------------------------------------------------------------------------------- fetching


def http_get(url, timeout=120, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        return {
            "url": url,
            "http_status": r.status,
            "n_bytes": len(body),
            "body": body if binary else body.decode("utf-8", "replace"),
        }


def ena_run_table(accession, timeout=120):
    fields = ",".join(
        [
            "run_accession",
            "experiment_accession",
            "sample_accession",
            "study_accession",
            "instrument_platform",
            "instrument_model",
            "library_strategy",
            "library_source",
            "library_selection",
            "library_layout",
            "library_name",
            "read_count",
            "base_count",
            "fastq_ftp",
            "fastq_bytes",
            "fastq_md5",
            "submitted_ftp",
            "sra_ftp",
            "scientific_name",
            "sample_title",
            "sample_alias",
            "description",
            "experiment_title",
            "study_title",
        ]
    )
    url = (
        f"{ENA_PORTAL}/filereport?accession={accession}&result=read_run"
        f"&fields={fields}&format=tsv&limit=0"
    )
    rec = http_get(url, timeout=timeout)
    lines = [l for l in rec["body"].split("\n") if l.strip()]
    rows = []
    if lines:
        hdr = lines[0].split("\t")
        for l in lines[1:]:
            parts = l.split("\t")
            rows.append({hdr[i]: (parts[i] if i < len(parts) else "") for i in range(len(hdr))})
    rec["rows"] = rows
    rec.pop("body", None)
    return rec


def scan_run(run_row, genes, budget_s=3000, max_bytes=None, flank=MIN_FLANK):
    """Stream a run's FASTQ over HTTPS and scan it. Never writes the reads to disk."""
    sc = JunctionScanner(genes, flank)
    capable, reason = assay_is_capable_of_spanning_a_junction(
        [
            run_row.get("library_strategy"),
            run_row.get("library_source"),
            run_row.get("library_selection"),
            run_row.get("experiment_title"),
            run_row.get("study_title"),
            run_row.get("description"),
        ],
        read_length=_read_len(run_row),
    )
    out = {
        "run_accession": run_row.get("run_accession"),
        "library_strategy": run_row.get("library_strategy"),
        "library_layout": run_row.get("library_layout"),
        "experiment_title": run_row.get("experiment_title"),
        "read_count": run_row.get("read_count"),
        "base_count": run_row.get("base_count"),
        "derived_read_length_nt": _read_len(run_row),
        "assay_capable_of_spanning_a_junction": capable,
        "assay_gate_reason": reason,
    }
    if capable is False:
        out["state"] = "REFUSED_BY_ASSAY_GATE"
        out["⛔ note"] = (
            "No scan was run. This is a refusal, NOT a negative result — scanning would have "
            "produced a zero that means nothing."
        )
        return out

    ftp = (run_row.get("fastq_ftp") or "").split(";")
    urls = [f"https://{p}" for p in ftp if p.strip()]
    if not urls:
        out["state"] = "NO_PUBLIC_FILES"
        out["⛔ note"] = (
            "ENA lists no fastq file for this run. submitted_ftp="
            f"{run_row.get('submitted_ftp')!r} — a run with metadata and no file list is "
            "registered and NOT downloadable."
        )
        return out

    t0 = time.time()
    per_file = []
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                gz = gzip.GzipFile(fileobj=r)
                why = sc.scan_stream(gz, budget_s=budget_s, max_bytes=max_bytes, t0=t0)
            per_file.append({"url": u, "status": "read", "stopped_because": why})
        except Exception as e:  # noqa: BLE001 - the reason must reach the artifact
            per_file.append({"url": u, "status": f"ERROR {type(e).__name__}: {e}"})
        if budget_s and (time.time() - t0) > budget_s:
            break

    out.update(
        {
            "state": "SCANNED",
            "files": per_file,
            "wall_s": round(time.time() - t0, 1),
            "uncompressed_bytes_scanned": sc.n_bytes,
            "flank_nt_each_side": flank,
            "depth_counts_per_gene": sc.depth_counts,
            "acceptor_site_hits": sc.acceptor_hits,
            "wildtype_context_reads": sc.wildtype_reads,
            "junctions_found": sorted(sc.junctions.values(), key=lambda r: -r["n_reads"]),
        }
    )
    out["informative"] = bool(sc.depth_counts.get(ACCEPTOR, 0) > 0 or sum(sc.acceptor_hits.values()) > 0)
    if not out["informative"]:
        out["⛔ note"] = (
            "UNINFORMATIVE — not one read carried NR4A3 at all, so the absence of a junction read "
            "says nothing about this tumour. An absent reading is not a reading of absence."
        )
    elif not out["junctions_found"]:
        out["⛔ note"] = (
            "No seam matched among the partner x acceptor pairs this module looks for, in a scan "
            "that DID see NR4A3 reads. That is evidence against those specific seams only — a "
            "novel partner or an intra-exonic breakpoint is invisible to this method by design."
        )
    return out


def _read_len(row):
    try:
        rc, bc = int(row.get("read_count") or 0), int(row.get("base_count") or 0)
        if rc > 0:
            n = bc / rc
            if (row.get("library_layout") or "").upper() == "PAIRED":
                n /= 2.0
            return round(n, 1)
    except (TypeError, ValueError):
        pass
    return None


# ------------------------------------------------------------------------------------ selftest


def selftest():
    """Offline. Every way this module could lie is arithmetic over committed sequence."""
    genes = load_genes()
    sc = JunctionScanner(genes)
    fails = []

    def chk(cond, msg):
        if not cond:
            fails.append(msg)

    # 1. the sequence accessors agree with the committed exon spans
    n3 = genes[ACCEPTOR]
    chk(len(exon_seq(n3, 3)) > 0, "NR4A3 exon 3 empty")
    chk(len(intron_seq(n3, 2)) > 0, "NR4A3 intron 2 empty")
    chk(
        sum(len(exon_seq(n3, i)) for i in range(1, n3["n_exons"] + 1)) == n3["exonic_nt"],
        "exon lengths do not sum to the committed exonic_nt — the span convention is wrong",
    )

    # 2. POSITIVE CONTROL: a synthetic read carrying a known seam must be found, and must be
    #    named with the right exon pair.
    for donor_gene, donor_exon, site in [
        ("EWSR1", 12, "NR4A3_exon3_start"),
        ("TAF15", 6, "NR4A3_exon3_start"),
        ("TAF15", 6, "NR4A3_intron2_start"),
        ("TCF12", 5, "NR4A3_exon3_start"),
    ]:
        g = genes[donor_gene]
        left = exon_seq(g, donor_exon)[-60:]
        kind, n = ("exon", 3) if "exon3" in site else ("intron", 2)
        right = (exon_seq(n3, n) if kind == "exon" else intron_seq(n3, n))[:60]
        read = (left + right).upper()
        sc.reset()
        sc._scan_text(f"@r\n{read}\n+\n{'I' * len(read)}\n")
        found = {j["donor"] for j in sc.junctions.values()}
        chk(
            f"{donor_gene}_exon{donor_exon}" in found,
            f"POSITIVE CONTROL FAILED: {donor_gene} exon{donor_exon} -> {site} not recovered "
            f"(found {found or 'nothing'})",
        )
        # and on the reverse strand
        sc.reset()
        rc = revcomp(read)
        sc._scan_text(f"@r\n{rc}\n+\n{'I' * len(rc)}\n")
        chk(
            f"{donor_gene}_exon{donor_exon}" in {j["donor"] for j in sc.junctions.values()},
            f"POSITIVE CONTROL FAILED on the reverse strand: {donor_gene} exon{donor_exon}",
        )

    # 3. NEGATIVE CONTROL: the WILD-TYPE NR4A3 exon2->exon3 read must NOT be called a fusion.
    #    Without this the scanner would report a junction in every NR4A3-expressing sample.
    wt = (exon_seq(n3, 2)[-60:] + exon_seq(n3, 3)[:60]).upper()
    sc.reset()
    sc._scan_text(f"@r\n{wt}\n+\n{'I' * len(wt)}\n")
    chk(
        not sc.junctions,
        f"NEGATIVE CONTROL FAILED: wild-type NR4A3 exon2->exon3 was called a fusion "
        f"({list(sc.junctions)})",
    )
    chk(
        sc.wildtype_reads.get("NR4A3_exon3_start", 0) == 1,
        "wild-type NR4A3 read was not counted as wild-type context",
    )

    # 4. NEGATIVE CONTROL: random sequence must produce nothing.
    import random

    random.seed(7)
    rnd = "".join(random.choice("ACGT") for _ in range(4000))
    sc.reset()
    sc._scan_text(f"@r\n{rnd}\n+\n{'I' * len(rnd)}\n")
    chk(not sc.junctions, "NEGATIVE CONTROL FAILED: random sequence produced a junction")

    # 5. the assay gate must REFUSE a targeted assay and must not refuse whole-transcriptome
    cap, _ = assay_is_capable_of_spanning_a_junction(["Targeted RNA-seq (TempO-Seq) of EMC"], 50)
    chk(cap is False, "assay gate did not refuse TempO-Seq")
    cap, _ = assay_is_capable_of_spanning_a_junction(["RNA-Seq", "TRANSCRIPTOMIC"], 151)
    chk(cap is True, "assay gate refused ordinary RNA-seq")
    cap, _ = assay_is_capable_of_spanning_a_junction([], None)
    chk(cap is None, "assay gate returned a boolean where it could not determine")
    cap, _ = assay_is_capable_of_spanning_a_junction(["RNA-Seq"], 25)
    chk(cap is False, "assay gate accepted a read too short to carry the seam")

    # 6. a truncated read (junction present but < flank on one side) must NOT be called
    g = genes["EWSR1"]
    short = (exon_seq(g, 12)[-8:] + exon_seq(n3, 3)[:60]).upper()
    sc.reset()
    sc._scan_text(f"@r\n{short}\n+\n{'I' * len(short)}\n")
    chk(not sc.junctions, "a read with only 8 nt of donor was called a junction")

    if fails:
        print("SELFTEST FAILED")
        for f in fails:
            print("  ⛔", f)
        return 1
    print(
        f"selftest OK — {len(sc.donors)} donor exon ends, {len(sc.acceptors)} acceptor sites, "
        f"{len(sc.depth_probes)} depth probes, flank {MIN_FLANK} nt each side"
    )
    return 0


# ---------------------------------------------------------------------------------------- modes


def probe_deposits(targets, budget_s=600):
    """Characterise deposits WITHOUT downloading any reads. What is actually there?"""
    t0 = time.time()
    out = {
        "_what": "what each candidate deposit actually serves, read before anything is downloaded",
        "_cost": "$0 — metadata and one landing page per deposit, on a free CPU runner",
        "targets": [],
    }
    for t in targets:
        rec = {"target": t}
        try:
            if t.startswith(("SRR", "SRP", "PRJ", "ERR", "ERP", "SRX")):
                r = ena_run_table(t)
                rec["kind"] = "archive_accession"
                rec["http_status"] = r["http_status"]
                rec["n_runs"] = len(r["rows"])
                rec["runs"] = []
                for row in r["rows"]:
                    cap, why = assay_is_capable_of_spanning_a_junction(
                        [
                            row.get("library_strategy"),
                            row.get("library_source"),
                            row.get("library_selection"),
                            row.get("experiment_title"),
                            row.get("study_title"),
                        ],
                        _read_len(row),
                    )
                    fb = row.get("fastq_bytes") or ""
                    rec["runs"].append(
                        {
                            "run_accession": row.get("run_accession"),
                            "experiment_title": row.get("experiment_title"),
                            "library_strategy": row.get("library_strategy"),
                            "library_layout": row.get("library_layout"),
                            "read_count": row.get("read_count"),
                            "derived_read_length_nt": _read_len(row),
                            "fastq_ftp": row.get("fastq_ftp"),
                            "fastq_total_bytes": sum(
                                int(x) for x in fb.split(";") if x.strip().isdigit()
                            ),
                            "submitted_ftp": row.get("submitted_ftp"),
                            "downloadable": bool((row.get("fastq_ftp") or "").strip()),
                            "assay_capable_of_spanning_a_junction": cap,
                            "assay_gate_reason": why,
                        }
                    )
            else:
                r = http_get(t, timeout=90)
                rec["kind"] = "landing_page"
                rec["http_status"] = r["http_status"]
                rec["n_bytes"] = r["n_bytes"]
                body = r["body"]
                links = re.findall(r'href=["\']([^"\']+)["\']', body)
                rec["n_links"] = len(links)
                rec["file_like_links"] = sorted(
                    {
                        l
                        for l in links
                        if re.search(
                            r"\.(fastq|fq|bam|cram|sra|gz|zip|tar|xlsx?|csv|tsv|txt|pdf)(\?|$)",
                            l,
                            re.I,
                        )
                        or "bitstream" in l.lower()
                        or "download" in l.lower()
                    }
                )
                rec["title"] = (
                    re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I).group(1).strip()
                    if re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
                    else None
                )
                rec["mentions_fastq_or_bam"] = bool(re.search(r"fastq|\.bam\b|cram", body, re.I))
                rec["body_head"] = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))[:1500]
        except Exception as e:  # noqa: BLE001
            rec["status"] = f"ERROR {type(e).__name__}: {e}"
        out["targets"].append(rec)
        if time.time() - t0 > budget_s:
            out["⚠ budget"] = "budget exhausted; remaining targets not probed"
            break
    out["_wall_s"] = round(time.time() - t0, 1)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--probe", nargs="*", help="deposits/URLs to characterise without downloading")
    ap.add_argument("--scan", nargs="*", help="run accessions to stream and scan")
    ap.add_argument("--budget-s", type=int, default=3000)
    ap.add_argument("--max-bytes", type=int, default=0)
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    rc = selftest()
    if rc:
        print("⛔ refusing to fetch: the offline selftest failed")
        return rc

    if args.probe is not None:
        res = probe_deposits(args.probe, budget_s=min(args.budget_s, 900))
        res["_generated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(OUT_DEPOSITS, "w") as fh:
            json.dump(res, fh, indent=1)
        print(json.dumps(res, indent=1)[:6000])
        print(f"\nwrote {OUT_DEPOSITS}")

    if args.scan:
        genes = load_genes()
        results, inputs = [], []
        for acc in args.scan:
            tbl = ena_run_table(acc)
            inputs.append({"accession": acc, "http_status": tbl["http_status"], "rows": tbl["rows"]})
            for row in tbl["rows"]:
                print(f"--- scanning {row.get('run_accession')} ({row.get('experiment_title')})")
                r = scan_run(
                    row,
                    genes,
                    budget_s=args.budget_s,
                    max_bytes=args.max_bytes or None,
                )
                results.append(r)
                print(json.dumps(r, indent=1)[:3000])
        art = {
            "_title": "NR4A3 fusion breakpoints recovered from deposited raw reads",
            "_generated_by": "research/modalities/emc_fusion_read_scan.py",
            "_cost": "$0 — CPU only on a GitHub-hosted runner; reads are streamed, never stored",
            "_generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "_what_this_is_not": [
                "Not a fusion caller — only named partner x NR4A3 seams are looked for.",
                "Not a breakpoint distribution; one deposit is not a population.",
                "Not an efficacy, potency, safety, therapeutic-window or clinical claim.",
                "Not a patient count — runs are not samples and samples are not people.",
            ],
            "flank_nt_each_side": MIN_FLANK,
            "runs": results,
        }
        with open(OUT, "w") as fh:
            json.dump(art, fh, indent=1)
        with open(OUT_INPUTS, "w") as fh:
            json.dump(
                {
                    "_generated_utc": art["_generated_utc"],
                    "_what": "the ENA run tables the scan above was driven from",
                    "queries": inputs,
                },
                fh,
                indent=1,
            )
        print(f"\nwrote {OUT} and {OUT_INPUTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
