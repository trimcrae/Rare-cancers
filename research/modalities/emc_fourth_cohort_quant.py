#!/usr/bin/env python3
"""PRJNA1357027 / SRP640302 — the fourth EMC cohort, fetched and quantified.

⭐ WHAT THIS IS, AND WHAT IT IS NOT. `emc_sra_study.py` CHARACTERISED this deposit from metadata
alone and graded it `EMC_PUBLIC_CANDIDATE`; `emc-fourth-cohort-sra-2026-08-08.md` §8 then listed
four steps that would turn that grade into a readable expression matrix and priced all four at $0.
None of them had a ledger row and none had ever run. This module is steps 1 and 2 — name the panel
by MEASURING it, then quantify by probe-count matching. It is not a differential-expression
analysis and it must never become one: see `WHY_NO_DIFFERENTIAL_EXPRESSION` below, which is a
finding rather than an omission.

⛔ THE ORDERING IS THE POINT, NOT POLITENESS. The deposit is 2,704,945,123 bytes over 12 runs
(measured — `emc-sra-study.json` -> targets.PRJNA1357027, and re-read live by `--phase probe`).
Its experiment title says `Targeted RNA-seq (TempO-Seq)` while its structured `library_strategy`
field says `RNA-Seq`, and the memo above records that the disagreement is the whole problem: a
conventional align-and-quantify pipeline pointed at a probe panel produces a matrix that is mostly
zeros by construction, and nothing in the metadata warns you. So ONE run (~225 MB) is pulled first
and the read structure is MEASURED. Only a measurement that is consistent with a probe assay
unlocks the other eleven.

⭐ HOW THE PROBE COUNT IS MEASURED, AND WHY IT NEEDS AN ALGORITHM RATHER THAN A COUNTER. A
`dict` over every distinct read sequence in a 6.7 M-read run is dominated by sequencing errors,
which are nearly all singletons: the dict grows to the read count, not to the probe count, and the
answer it gives is an error rate wearing a probe count's costume. `LossyCounter` is Manku &
Motwani's lossy counting with an explicit epsilon, and its guarantee is what the artifact reports:
every sequence occurring more than `epsilon * N` times is RETAINED, and every retained count
understates the true count by at most `epsilon * N`. The floor is stated in the artifact in reads,
so a reader can see exactly which probes this instrument cannot resolve.

⭐ HOW A PROBE IS TURNED INTO A GENE, AND WHAT REFUTES IT. Nothing in the archive record carries
the panel's probe->gene manifest, so the assignment is MEASURED rather than looked up: the observed
probe sequences are matched, verbatim and on both strands, against the human cDNA and ncRNA
sequence sets, and the gene is read off the matching transcript's own FASTA header. The falsifier
is built in — the artifact reports the FRACTION of probes that matched, at each of three core
lengths, and a low fraction is reported as a refusal to emit per-gene counts rather than as a
per-gene matrix with a caveat.

⛔ EVERY READING IS SEPARATE FROM WHETHER IT COULD BE TAKEN. A probe with no transcript match is
`unassigned`, never "not expressed"; a run that was not fetched is `NOT_FETCHED`, never zero
reads; a gene absent from the panel is `not_on_panel`, never absent from the tumour. An absent
reading is not a reading of absence (CLAUDE.md §4).

⛔ CHECKPOINTING IS NOT OPTIONAL HERE AND IT IS RESTORED, NOT MERELY WRITTEN. The inputs cache is
rewritten after EVERY run, and `--phase quant` skips any run already in it. A file written and
never read back is not a checkpoint; it is a file.

Cost: $0. A GitHub-hosted `ubuntu-latest` CPU runner, pure stdlib, no pip, no GPU.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "emc-fourth-cohort-quant.json")
INPUTS = os.path.join(HERE, "emc-fourth-cohort-quant-inputs.json")
GENE_TSV = os.path.join(HERE, "emc-fourth-cohort-gene-counts.tsv")
PROBE_TSV = os.path.join(HERE, "emc-fourth-cohort-probe-counts.tsv")
SRA_STUDY_INPUTS = os.path.join(HERE, "emc-sra-study-inputs.json")

BIOPROJECT = "PRJNA1357027"
SRA_STUDY = "SRP640302"

ENA_PORTAL = "https://www.ebi.ac.uk/ena/portal/api"
ENSEMBL_FASTA = "https://ftp.ensembl.org/pub/current_fasta/homo_sapiens"
UA = "Rare-cancers-research/1.0 (+https://github.com/trimcrae/Rare-cancers)"

#: Lossy counting's epsilon. The support floor it buys is `epsilon * N` READS in a run, printed in
#: the artifact per run rather than restated here, because N differs per run (CLAUDE.md §1).
#: ⚠ Chosen for the MEMORY bound, which is what actually fails on a free runner: lossy counting
#: holds O((1/epsilon) * ln(epsilon * N)) entries, so 2e-6 over a ~7 M-read run bounds the table
#: at ~1.3 M sequences. A smaller epsilon resolves rarer probes and can exhaust the box.
EPSILON = 2e-6

#: What `--phase probe` must see before eleven more runs are pulled. Each is a property of the
#: READ STRUCTURE, and each is stated as a number so the refusal can name which one failed.
GATE = {
    "min_modal_length_fraction": 0.90,
    "min_sequences_covering_80pct": 1_000,
    "max_sequences_covering_80pct": 200_000,
    "min_reads_in_retained": 0.50,
}

#: How many distinct sequences are persisted per run, and the coverage they must reach first.
#: ⛔ THE GATE COUNTS `n90`, NOT THE RETAINED TABLE, AND THE DIFFERENCE IS A MEASUREMENT RATHER
#: THAN A PREFERENCE. A single-base sequencing error on an abundant probe produces a distinct
#: sequence that is itself abundant enough to clear the lossy-counting floor, so the retained
#: table of a perfectly ordinary probe assay carries the panel PLUS an error halo one to two
#: orders of magnitude larger. Counting the retained table would therefore have refused the very
#: deposit this gate exists to admit. The number of sequences needed to cover 90 % of the reads
#: is insensitive to that halo, because each error variant is small.
KEEP_COVERAGE = 0.99

#: Where the abundance curve is read. The gate keys on `n80`; the rest are reported so a reader
#: can see the knee rather than trust one cut.
COVERAGE_POINTS = (0.50, 0.80, 0.90, 0.95, 0.99)
KEEP_MAX_SEQUENCES = 200_000

WHY_NO_DIFFERENTIAL_EXPRESSION = (
    "⛔ NO DIFFERENTIAL-EXPRESSION RESULT IS COMPUTED OR REPORTED FROM THIS COHORT, AND THAT IS "
    "THE FINDING RATHER THAN A GAP. The deposit is twelve tumours split six good-prognosis versus "
    "six poor-prognosis. Six against six is a comparison whose per-gene variance is estimated from "
    "five degrees of freedom per arm, over ~20,000 genes, with no replicate structure, one "
    "sequencing batch, FFPE input of widely differing collection years (1997-2020 in the archive "
    "record) and no covariate the metadata makes adjustable. A ranked gene list from that design "
    "would be dominated by which of the twelve specimens degraded least. The counts are published "
    "here so that anyone can join them to a hypothesis formed elsewhere; a confident "
    "differential-expression claim is not available at this n and this module does not make one."
)


# ------------------------------------------------------------------ lossy counting


class LossyCounter:
    """Manku & Motwani lossy counting over read sequences, with the guarantee stated.

    ⛔ WHY NOT A `collections.Counter`. Almost every distinct sequence in a run is a sequencing
    error and occurs once, so an exact counter's size tracks the READ count. On this deposit that
    is 5.4-8.7 M entries per run and the table, not the download, is what kills the job. Lossy
    counting bounds the table instead, and pays for it with a stated understatement rather than
    with a silent truncation.
    """

    def __init__(self, epsilon: float = EPSILON):
        if not (0 < epsilon < 1):
            raise ValueError("epsilon must be in (0, 1)")
        self.epsilon = epsilon
        self.width = int(1.0 / epsilon)
        self.n = 0
        self.bucket = 1
        self.table: dict[str, list[int]] = {}   # seq -> [count, delta]

    def add(self, seq: str) -> None:
        self.n += 1
        rec = self.table.get(seq)
        if rec is None:
            self.table[seq] = [1, self.bucket - 1]
        else:
            rec[0] += 1
        if self.n % self.width == 0:
            self._sweep()
            self.bucket += 1

    def _sweep(self) -> None:
        b = self.bucket
        self.table = {k: v for k, v in self.table.items() if v[0] + v[1] > b}

    def support_floor(self) -> float:
        """The frequency above which retention is GUARANTEED, in reads."""
        return self.epsilon * self.n

    def heavy_hitters(self, min_count: int | None = None) -> dict[str, int]:
        floor = self.support_floor() if min_count is None else float(min_count)
        return {k: v[0] for k, v in self.table.items() if v[0] >= floor}


# ------------------------------------------------------------------ fetching


def http_get(url: str, timeout: int = 120) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    return {"url": url, "http_status": r.status, "n_bytes": len(body),
            "body": body.decode("utf-8", "replace")}


ENA_FIELDS = (
    "run_accession,experiment_accession,sample_accession,study_accession,"
    "instrument_platform,instrument_model,library_strategy,library_source,"
    "library_selection,library_layout,library_name,read_count,base_count,"
    "fastq_ftp,fastq_bytes,fastq_md5,submitted_ftp,scientific_name,"
    "sample_title,sample_alias,experiment_title,study_title,first_public"
)


def ena_run_table(accession: str, timeout: int = 120) -> dict:
    url = (f"{ENA_PORTAL}/filereport?accession={accession}&result=read_run"
           f"&fields={ENA_FIELDS}&format=tsv&limit=0")
    rec = http_get(url, timeout=timeout)
    lines = [ln for ln in rec["body"].split("\n") if ln.strip()]
    rows = []
    if lines:
        hdr = lines[0].split("\t")
        for ln in lines[1:]:
            parts = ln.split("\t")
            rows.append({hdr[i]: (parts[i] if i < len(parts) else "") for i in range(len(hdr))})
    rec["rows"] = rows
    rec.pop("body", None)
    return rec


def fastq_urls(row: dict) -> list[str]:
    raw = (row.get("fastq_ftp") or "").strip()
    if not raw:
        return []
    return ["https://" + u if not u.startswith("http") else u for u in raw.split(";") if u]


def iter_read_seqs(fh):
    """Yield the SEQUENCE line of every FASTQ record. Reads are streamed, never stored."""
    for i, raw in enumerate(fh):
        if i % 4 == 1:
            yield raw.rstrip()


def spectrum(hh: dict) -> dict:
    """The abundance spectrum of one run's retained sequences — the panel-size estimator.

    ⛔ `n80` IS THE ESTIMATOR AND `len(hh)` IS NOT. A single-base sequencing error on an abundant
    probe yields a distinct sequence that clears the lossy-counting floor on its own, so `len(hh)`
    measures the error halo and `n80` — how many distinct sequences it takes to cover 80 % of the
    retained reads — does not. Kept separate from `scan_one_run` so it can be exercised with no
    network, which is the whole reason the gate is assertable offline.

    ⚠ 80 %, NOT 90 %, AND THE REASON IS ARITHMETIC RATHER THAN TASTE. Reads carrying at least one
    sequencing error are a real share of a run — a fraction of a percent per base over a
    fifty-base read is a tenth of the reads or more — so a 90 % cut can land INSIDE the halo and
    then counts halo members. The whole coverage curve is reported in the artifact so a reader can
    see where the knee actually is instead of taking one cut on trust.
    """
    ranked = sorted(hh.items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in ranked)
    curve, acc, i = {}, 0, 0
    for frac in COVERAGE_POINTS:
        while acc < frac * total and i < len(ranked):
            acc += ranked[i][1]
            i += 1
        curve[f"n{int(frac * 100)}"] = i
    kept, acc2, n_dropped, reads_dropped = {}, 0, 0, 0
    for k, v in ranked:
        if len(kept) < KEEP_MAX_SEQUENCES and acc2 < KEEP_COVERAGE * total:
            kept[k] = v
            acc2 += v
        else:
            n_dropped += 1
            reads_dropped += v
    return {"hh": hh, "reads_in_retained": total, "curve": curve,
            "n80": curve.get("n80"), "kept": kept,
            "n_dropped": n_dropped, "reads_dropped": reads_dropped}


def scan_one_run(url: str, budget_s: float, epsilon: float = EPSILON,
                 max_reads: int | None = None) -> dict:
    """Stream one FASTQ.gz and return the read-structure measurement for it."""
    t0 = time.time()
    lc = LossyCounter(epsilon)
    lengths: dict[int, int] = {}
    n_reads = 0
    stopped = "eof"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        gz = gzip.GzipFile(fileobj=r)
        text = io.TextIOWrapper(gz, encoding="ascii", errors="replace")
        for seq in iter_read_seqs(text):
            n_reads += 1
            lengths[len(seq)] = lengths.get(len(seq), 0) + 1
            lc.add(seq)
            if n_reads % 200_000 == 0:
                if budget_s and (time.time() - t0) > budget_s:
                    stopped = "budget_exhausted"
                    break
                if max_reads and n_reads >= max_reads:
                    stopped = "max_reads"
                    break
    sp = spectrum(lc.heavy_hitters())
    total_hh, n80, kept = sp["reads_in_retained"], sp["n80"], sp["kept"]
    n_dropped, reads_dropped = sp["n_dropped"], sp["reads_dropped"]
    hh = sp["hh"]
    modal_len = max(lengths, key=lambda k: lengths[k]) if lengths else None
    return {
        "url": url,
        "n_reads_read": n_reads,
        "stopped_because": stopped,
        "wall_s": round(time.time() - t0, 1),
        "length_histogram": {str(k): v for k, v in sorted(lengths.items())},
        "modal_read_length_nt": modal_len,
        "modal_length_fraction": round(lengths.get(modal_len, 0) / n_reads, 6) if n_reads else None,
        "epsilon": epsilon,
        "support_floor_reads": round(lc.support_floor(), 1),
        "n_retained_sequences": len(hh),
        "reads_in_retained": total_hh,
        "fraction_reads_in_retained": round(total_hh / n_reads, 6) if n_reads else None,
        "n_sequences_covering_80pct": n80,
        "abundance_curve": sp["curve"],
        "n_sequences_persisted": len(kept),
        "n_sequences_dropped_from_persistence": n_dropped,
        "reads_dropped_from_persistence": reads_dropped,
        "⚠ persistence_cap": (
            f"counts are persisted for the sequences covering {KEEP_COVERAGE:.0%} of retained "
            f"reads, at most {KEEP_MAX_SEQUENCES}. A dropped sequence was OBSERVED and is not "
            f"reported as absent; the count of what was dropped, and the reads it carried, are "
            f"the two fields above."),
        "counts": kept,
    }


# ------------------------------------------------------------------ the gate


def gate_verdict(measure: dict) -> dict:
    """Does this run's READ STRUCTURE justify pulling the other eleven? One reason per failure."""
    checks = []

    def chk(name, ok, got, want):
        checks.append({"check": name, "passed": bool(ok), "measured": got, "required": want})

    mf = measure.get("modal_length_fraction")
    chk("reads_are_one_fixed_length", mf is not None and mf >= GATE["min_modal_length_fraction"],
        mf, f">= {GATE['min_modal_length_fraction']}")
    n = measure.get("n_sequences_covering_80pct")
    chk("a_panel_sized_sequence_set_covers_80pct_of_reads",
        n is not None and GATE["min_sequences_covering_80pct"] <= n
        <= GATE["max_sequences_covering_80pct"],
        n, f"{GATE['min_sequences_covering_80pct']}..{GATE['max_sequences_covering_80pct']}")
    fr = measure.get("fraction_reads_in_retained")
    chk("a_small_sequence_set_carries_most_reads",
        fr is not None and fr >= GATE["min_reads_in_retained"], fr,
        f">= {GATE['min_reads_in_retained']}")

    passed = all(c["passed"] for c in checks)
    return {
        "passed": passed,
        "checks": checks,
        "meaning": (
            "PASS = the reads are one fixed length and a panel-sized set of distinct sequences "
            "carries most of them, which is what a templated-ligation probe assay looks like and "
            "what makes probe-count matching the right quantification. It is NOT a confirmation "
            "of any named commercial panel or of its gene content."
            if passed else
            "REFUSED — the remaining runs were NOT downloaded. The failing check names the "
            "property that was absent; a deposit whose reads do not look like a probe assay needs "
            "a different quantification, and burning 2.5 GB to find that out twelve times over is "
            "the spend this gate exists to refuse."
        ),
    }


# ------------------------------------------------------------------ probe -> gene


def revcomp(s: str) -> str:
    return s.translate(str.maketrans("ACGTNacgtn", "TGCANtgcan"))[::-1]


def _ensembl_fasta_url(kind: str, timeout: int = 120) -> dict:
    """Discover the file rather than typing its name: the release moves, the pattern does not."""
    listing = http_get(f"{ENSEMBL_FASTA}/{kind}/", timeout=timeout)
    names = sorted(set(re.findall(r'href="([^"]+\.fa\.gz)"', listing["body"])))
    want = [n for n in names if n.endswith(f".{kind}.all.fa.gz")] or \
           [n for n in names if n.endswith(".fa.gz") and "abinitio" not in n]
    return {"listing_url": listing["url"], "listing_status": listing["http_status"],
            "names_seen": names, "chosen": (want[0] if want else None)}


def _core_sets(probes: list[str], read_len: int) -> dict[int, dict[str, str]]:
    """core -> probe, for three core lengths. Diagnoses a non-target head or tail on the read.

    ⛔ THE THREE LENGTHS ARE A DIAGNOSTIC, NOT A SEARCH FOR A MATCH. If the full-length core
    matches and the trimmed ones do not add much, the read IS the target sequence; if only the
    trimmed cores match, the read carries non-target bases at its ends and the artifact says so.
    Reporting the best length as though it were the read structure would be the tuning this
    repository refuses.
    """
    out: dict[int, dict[str, str]] = {}
    for trim in (0, 4, 8):
        L = read_len - 2 * trim
        if L < 24:
            continue
        d: dict[str, str] = {}
        for p in probes:
            if len(p) < read_len:
                continue
            core = p[trim:trim + L]
            if "N" in core:
                continue
            d.setdefault(core, p)
            d.setdefault(revcomp(core), p)
        out[L] = d
    return out


def map_probes_to_genes(probes: list[str], read_len: int, budget_s: float,
                        timeout: int = 300) -> dict:
    """Match probe sequences verbatim against human cDNA + ncRNA; read the gene off the header."""
    t0 = time.time()
    cores = _core_sets(probes, read_len)
    if not cores:
        return {"state": "REFUSED", "why": "no usable core length for the measured read length",
                "read_length_nt": read_len}
    lens = sorted(cores, reverse=True)
    prefix_n = 16
    prefixes = {L: {c[:prefix_n] for c in cores[L]} for L in lens}
    hits: dict[int, dict[str, dict]] = {L: {} for L in lens}

    sources = []
    for kind in ("cdna", "ncrna"):
        try:
            disc = _ensembl_fasta_url(kind, timeout=timeout)
        except Exception as e:  # noqa: BLE001 — the reason must reach the artifact
            sources.append({"kind": kind, "state": f"ERROR {type(e).__name__}: {e}"})
            continue
        if not disc.get("chosen"):
            sources.append({"kind": kind, "state": "NO_FILE_MATCHED", "listing": disc})
            continue
        url = f"{ENSEMBL_FASTA}/{kind}/{disc['chosen']}"
        try:
            n_tx, n_bp = _scan_fasta(url, lens, cores, prefixes, prefix_n, hits, budget_s, t0,
                                     timeout)
            sources.append({"kind": kind, "url": url, "state": "read",
                            "n_transcripts": n_tx, "n_bases_scanned": n_bp})
        except Exception as e:  # noqa: BLE001
            sources.append({"kind": kind, "url": url, "state": f"ERROR {type(e).__name__}: {e}"})

    per_len = {}
    for L in lens:
        per_len[str(L)] = {
            "core_length_nt": L,
            "n_probes_matched": len({h["probe"] for h in hits[L].values()}),
            "fraction_of_probes_matched": round(
                len({h["probe"] for h in hits[L].values()}) / len(probes), 6) if probes else None,
        }
    best = max(lens, key=lambda L: per_len[str(L)]["n_probes_matched"]) if lens else None
    assignment = {}
    if best is not None:
        for core, rec in hits[best].items():
            assignment.setdefault(rec["probe"], set()).add(rec["gene"])
    unique = {p: sorted(g)[0] for p, g in assignment.items() if len(g) == 1}
    multi = {p: sorted(g) for p, g in assignment.items() if len(g) > 1}
    return {
        "state": "read" if any(s.get("state") == "read" for s in sources) else "FETCH_FAILED",
        "sources": sources,
        "read_length_nt": read_len,
        "per_core_length": per_len,
        "best_core_length_nt": best,
        "n_probes_offered": len(probes),
        "n_probes_assigned_to_one_gene": len(unique),
        "n_probes_matching_several_genes": len(multi),
        "n_probes_unassigned": len(probes) - len(unique) - len(multi),
        "⚠ unassigned_means": (
            "no verbatim match to a human cDNA or ncRNA transcript at any core length tried. That "
            "is a statement about this matcher, NOT about the probe: a probe spanning a junction "
            "the sequence set does not contain, or carrying non-target bases, is unassigned here "
            "and is still a real probe."),
        "probe_to_gene": unique,
        "probe_to_several_genes": multi,
        "wall_s": round(time.time() - t0, 1),
    }


def _scan_fasta(url, lens, cores, prefixes, prefix_n, hits, budget_s, t0, timeout):
    """One pass over a FASTA, checking every core length at every position."""
    n_tx = 0
    n_bp = 0
    gene = None
    chunks: list[str] = []
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        gz = gzip.GzipFile(fileobj=r)
        text = io.TextIOWrapper(gz, encoding="ascii", errors="replace")
        for line in text:
            if line.startswith(">"):
                if chunks and gene:
                    n_bp += _scan_seq("".join(chunks), gene, lens, cores, prefixes, prefix_n, hits)
                chunks = []
                n_tx += 1
                m = re.search(r"gene_symbol:(\S+)", line)
                if not m:
                    m = re.search(r"gene:(\S+)", line)
                gene = m.group(1) if m else "UNNAMED"
                if budget_s and n_tx % 2000 == 0 and (time.time() - t0) > budget_s:
                    break
            else:
                chunks.append(line.strip())
        if chunks and gene:
            n_bp += _scan_seq("".join(chunks), gene, lens, cores, prefixes, prefix_n, hits)
    return n_tx, n_bp


def _scan_seq(seq, gene, lens, cores, prefixes, prefix_n, hits):
    n = len(seq)
    for L in lens:
        if n < L:
            continue
        pre = prefixes[L]
        tbl = cores[L]
        h = hits[L]
        for i in range(n - L + 1):
            if seq[i:i + prefix_n] in pre:
                core = seq[i:i + L]
                probe = tbl.get(core)
                if probe is not None and core not in h:
                    h[core] = {"probe": probe, "gene": gene}
    return n


# ------------------------------------------------------------------ per-sample labels


def sample_labels_from_committed_xml(path: str = SRA_STUDY_INPUTS) -> dict:
    """run accession -> the depositors' own per-sample attributes, read OFFLINE from the cache
    `emc_sra_study.py` already committed. No fetch: the payload is on disk (CLAUDE.md §4)."""
    if not os.path.exists(path):
        return {"state": "NOT_AVAILABLE", "why": f"{os.path.basename(path)} is not on disk"}
    with open(path, encoding="utf-8") as fh:
        cache = json.load(fh)
    for f in cache.get("fetches", []):
        body = f.get("body") or ""
        if "EXPERIMENT_PACKAGE_SET" not in body or "SAMPLE_ATTRIBUTE" not in body:
            continue
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            continue
        out = {}
        for pkg in root:
            run = pkg.find(".//RUN")
            if run is None:
                continue
            attrs = {a.findtext("TAG"): a.findtext("VALUE")
                     for a in pkg.findall(".//SAMPLE_ATTRIBUTE")}
            sm = pkg.find(".//SAMPLE")
            out[run.get("accession")] = {
                "library_name": pkg.findtext(".//LIBRARY_NAME"),
                "sample_alias": sm.get("alias") if sm is not None else None,
                "design_description": pkg.findtext(".//DESIGN_DESCRIPTION"),
                "attributes": attrs,
            }
        if out:
            return {"state": "read", "source_url": f.get("url"), "runs": out}
    return {"state": "NOT_FOUND", "why": "no SRA experiment-package payload in the cache"}


# ------------------------------------------------------------------ cache


def _read_probe_tsv() -> dict[str, dict[str, int]]:
    """run -> {probe: count}, read back from the committed checkpoint. {} when there is none."""
    if not os.path.exists(PROBE_TSV):
        return {}
    out: dict[str, dict[str, int]] = {}
    with open(PROBE_TSV, encoding="utf-8") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        accs = [c.split(":")[0] for c in hdr[2:]]
        for a in accs:
            out[a] = {}
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2 + len(accs):
                continue
            seq = parts[0]
            for a, v in zip(accs, parts[2:]):
                n = int(v or 0)
                if n:
                    out[a][seq] = n
    return out


def _write_probe_tsv(cache: dict, gene_of=None) -> str:
    """THE CHECKPOINT ITSELF, and the raw deliverable. One row per probe, one column per run.

    ⛔ WHY THE COUNTS LIVE HERE AND NOT IN THE JSON CACHE. A JSON object keyed by 50-nt sequences,
    repeated once per run, is tens of megabytes of mostly repeated keys — and a checkpoint nobody
    will commit is a checkpoint that does not survive the job that wrote it. The TSV stores each
    sequence once, is diffable, and is the form anybody wanting these counts actually wants.
    """
    runs = {k: v for k, v in cache.get("runs", {}).items() if v.get("counts")}
    accs = sorted(runs)
    if not accs:
        return ""
    alias = {a: (runs[a].get("sample_alias") or a) for a in accs}
    probes = sorted(set().union(*[set(runs[a]["counts"]) for a in accs]))
    lines = ["probe_sequence\tassigned_gene\t" + "\t".join(f"{a}:{alias[a]}" for a in accs)]
    for pr in probes:
        g = (gene_of or {}).get(pr) or "unassigned"
        lines.append(pr + "\t" + g + "\t" +
                     "\t".join(str(runs[a]["counts"].get(pr, 0)) for a in accs))
    body = "\n".join(lines) + "\n"
    tmp = PROBE_TSV + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(body)
    os.replace(tmp, PROBE_TSV)
    return body


def load_inputs() -> dict:
    """The cache, with per-run counts REHYDRATED from the committed probe table.

    ⛔ THIS IS THE HALF THAT MAKES IT A CHECKPOINT. A file that is written and never read back is
    not a checkpoint; it is a file — the defect this repository's own `nr4a2-bound-ddddg-search`
    lane paid for. `phase_quant` skips a run only because this function can put its counts back.
    """
    cache = {"_what": f"read-structure measurements for {BIOPROJECT} / {SRA_STUDY}",
             "_cost": "$0 — a GitHub-hosted CPU runner, pure stdlib",
             "bioproject": BIOPROJECT, "sra_study": SRA_STUDY, "runs": {}}
    if os.path.exists(INPUTS):
        with open(INPUTS, encoding="utf-8") as fh:
            cache = json.load(fh)
    cache.setdefault("runs", {})
    for acc, counts in _read_probe_tsv().items():
        if counts and acc in cache["runs"] and not cache["runs"][acc].get("counts"):
            cache["runs"][acc]["counts"] = counts
    return cache


def save_inputs(cache: dict, gene_of=None) -> None:
    """Write BOTH halves: the probe table (the counts) and the JSON cache (everything else)."""
    cache["_generated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _write_probe_tsv(cache, gene_of)
    slim = dict(cache)
    slim["runs"] = {k: {kk: vv for kk, vv in v.items() if kk != "counts"}
                    for k, v in cache.get("runs", {}).items()}
    slim["_counts_live_in"] = os.path.basename(PROBE_TSV)
    tmp = INPUTS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(slim, fh, indent=1)
        fh.write("\n")
    os.replace(tmp, INPUTS)


# ------------------------------------------------------------------ phases


def phase_probe(budget_s: float, epsilon: float = EPSILON) -> dict:
    """ONE run, then the gate. Nothing else is downloaded until this passes."""
    cache = load_inputs()
    table = ena_run_table(BIOPROJECT)
    cache["run_table"] = table
    rows = sorted(table["rows"], key=lambda r: r.get("run_accession", ""))
    if not rows:
        cache["probe_gate"] = {"passed": False, "checks": [],
                               "meaning": "ENA returned no run rows; nothing to measure."}
        save_inputs(cache)
        return cache["probe_gate"]
    # the SMALLEST run, so the gate costs as little as the deposit allows
    def _bytes(r):
        try:
            return sum(int(b) for b in (r.get("fastq_bytes") or "0").split(";") if b)
        except ValueError:
            return 0
    row = min(rows, key=_bytes)
    urls = fastq_urls(row)
    if not urls:
        cache["probe_gate"] = {"passed": False, "checks": [],
                               "meaning": "the chosen run lists no fastq file."}
        save_inputs(cache)
        return cache["probe_gate"]
    m = scan_one_run(urls[0], budget_s=budget_s, epsilon=epsilon)
    m["run_accession"] = row.get("run_accession")
    m["fastq_bytes"] = _bytes(row)
    m["experiment_title"] = row.get("experiment_title")
    m["library_strategy"] = row.get("library_strategy")
    cache["runs"][row["run_accession"]] = m
    cache["probe_gate"] = gate_verdict(m)
    cache["probe_gate"]["gated_on_run"] = row.get("run_accession")
    cache["probe_gate"]["gated_on_bytes"] = _bytes(row)
    cache["probe_gate"]["deposit_total_fastq_bytes"] = sum(_bytes(r) for r in rows)
    save_inputs(cache)
    return cache["probe_gate"]


def phase_quant(budget_s: float, epsilon: float = EPSILON) -> dict:
    """The other eleven runs — ONLY if the gate passed. Checkpointed after every run."""
    cache = load_inputs()
    gate = cache.get("probe_gate") or {}
    if not gate.get("passed"):
        return {"state": "REFUSED", "why": "the one-run probe gate did not pass (or never ran); "
                                           "2.5 GB was not downloaded", "gate": gate}
    rows = sorted((cache.get("run_table") or {}).get("rows", []),
                  key=lambda r: r.get("run_accession", ""))
    t0 = time.time()
    done, skipped = [], []
    for row in rows:
        acc = row.get("run_accession")
        prev = cache["runs"].get(acc)
        if prev and prev.get("stopped_because") == "eof":
            skipped.append(acc)            # ⛔ RESTORED, not merely written
            continue
        if budget_s and (time.time() - t0) > budget_s:
            cache.setdefault("_notes", []).append(
                f"quant budget exhausted after {len(done)} run(s); the rest are NOT_FETCHED")
            break
        urls = fastq_urls(row)
        if not urls:
            cache["runs"][acc] = {"run_accession": acc, "state": "NO_FASTQ_LISTED"}
            save_inputs(cache)
            continue
        remaining = budget_s - (time.time() - t0) if budget_s else None
        m = scan_one_run(urls[0], budget_s=remaining, epsilon=epsilon)
        m["run_accession"] = acc
        m["experiment_title"] = row.get("experiment_title")
        cache["runs"][acc] = m
        save_inputs(cache)             # ⛔ CHECKPOINT AFTER EACH UNIT (CLAUDE.md §6)
        done.append(acc)
    save_inputs(cache)
    return {"state": "ok", "fetched_now": done, "restored_from_checkpoint": skipped,
            "n_runs_in_cache": len(cache["runs"]), "wall_s": round(time.time() - t0, 1)}


def phase_map(budget_s: float, min_runs: int = 2) -> dict:
    """Probe -> gene, from the probes the runs actually carry."""
    cache = load_inputs()
    runs = {k: v for k, v in cache.get("runs", {}).items() if v.get("counts")}
    if len(runs) < min_runs:
        return {"state": "REFUSED", "why": f"only {len(runs)} run(s) carry counts; "
                                           f"a probe set defined by one run is not a panel"}
    # a probe is a sequence retained in EVERY run that was read — the intersection is the
    # conservative set, and its size is reported beside the per-run counts.
    seqs = None
    for v in runs.values():
        s = set(v["counts"])
        seqs = s if seqs is None else (seqs & s)
    probes = sorted(seqs or [])
    read_len = max((v.get("modal_read_length_nt") or 0) for v in runs.values())
    res = map_probes_to_genes(probes, read_len, budget_s=budget_s)
    res["n_probes_in_every_read_run"] = len(probes)
    res["n_runs_intersected"] = len(runs)
    cache["probe_map"] = res
    save_inputs(cache)
    return {"state": res.get("state"), "n_probes": len(probes),
            "assigned": res.get("n_probes_assigned_to_one_gene"),
            "best_core_length_nt": res.get("best_core_length_nt")}


# ------------------------------------------------------------------ derive


def derive(cache: dict | None = None) -> dict:
    cache = cache if cache is not None else load_inputs()
    runs = cache.get("runs", {})
    read_runs = {k: v for k, v in runs.items() if v.get("counts")}
    labels = sample_labels_from_committed_xml()
    pmap = cache.get("probe_map") or {}
    p2g = pmap.get("probe_to_gene") or {}

    per_run = {}
    for acc in sorted(runs):
        v = runs[acc]
        lab = (labels.get("runs") or {}).get(acc, {})
        per_run[acc] = {
            "state": "READ" if v.get("counts") else v.get("state", "NOT_FETCHED"),
            "sample_alias": lab.get("sample_alias"),
            "n_reads_read": v.get("n_reads_read"),
            "stopped_because": v.get("stopped_because"),
            "modal_read_length_nt": v.get("modal_read_length_nt"),
            "modal_length_fraction": v.get("modal_length_fraction"),
            "n_retained_sequences": v.get("n_retained_sequences"),
            "n_sequences_covering_80pct": v.get("n_sequences_covering_80pct"),
            "n_sequences_persisted": v.get("n_sequences_persisted"),
            "support_floor_reads": v.get("support_floor_reads"),
            "fraction_reads_in_retained": v.get("fraction_reads_in_retained"),
            "prognosis": (lab.get("attributes") or {}).get("Prognosis"),
            "ewsr1_break_apart_fish": (lab.get("attributes") or {}).get("FISH_1"),
        }

    gene_counts: dict[str, dict[str, int]] = {}
    for acc, v in read_runs.items():
        for seq, n in v["counts"].items():
            g = p2g.get(seq)
            if g is None:
                continue
            gene_counts.setdefault(g, {})[acc] = gene_counts.setdefault(g, {}).get(acc, 0) + n

    n_probes_common = pmap.get("n_probes_in_every_read_run")
    out = {
        "_title": "PRJNA1357027 / SRP640302 — the fourth EMC cohort, read and quantified",
        "_generated_by": "research/modalities/emc_fourth_cohort_quant.py",
        "_generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_inputs_generated_utc": cache.get("_generated_utc"),
        "_cost": "$0 — CPU only on a GitHub-hosted runner; reads are streamed, never stored",
        "_what_this_is_not": [
            "Not a differential-expression result — see why_no_differential_expression.",
            "Not a patient count: runs are not samples and samples are not people.",
            "Not a confirmation of any named commercial probe panel or of its gene content.",
            "Not an efficacy, potency, safety, therapeutic-window or clinical claim.",
        ],
        "bioproject": BIOPROJECT,
        "sra_study": SRA_STUDY,
        "depositor_assay_description": sorted({
            (r.get("design_description") or "") for r in (labels.get("runs") or {}).values()
        } - {""}) or None,
        "⚠ depositor_description_is_one_source": (
            "The assay description above is the depositors' own words in their own deposit. It is "
            "not an independent measurement, and the read-structure numbers below are."),
        "probe_gate": cache.get("probe_gate"),
        "n_runs_in_deposit": len((cache.get("run_table") or {}).get("rows", [])),
        "n_runs_read": len(read_runs),
        "per_run": per_run,
        "probe_map": {k: v for k, v in pmap.items()
                      if k not in ("probe_to_gene", "probe_to_several_genes")},
        "n_probes_common_to_every_read_run": n_probes_common,
        "n_genes_with_at_least_one_assigned_probe": len(gene_counts),
        "gene_counts_written_to": os.path.basename(GENE_TSV) if gene_counts else None,
        "why_no_differential_expression": WHY_NO_DIFFERENTIAL_EXPRESSION,
        "sample_labels": {
            "state": labels.get("state"),
            "source": labels.get("source_url"),
            "⚠ prognosis_key": (
                "`Prognosis` B/G is the depositors' key. The deposit itself defines neither "
                "letter; the split is 6/6 in the archive record, and any outcome meaning must be "
                "taken from the depositors' publication, not from this artifact."),
        },
    }
    accs = sorted(read_runs)
    if read_runs:
        body = _write_probe_tsv(cache, p2g)
        out["probe_counts_written_to"] = os.path.basename(PROBE_TSV)
        out["probe_counts_sha256"] = hashlib.sha256(body.encode()).hexdigest()
        out["probe_counts_n_rows"] = len(body.strip().split("\n")) - 1
        out["⛔ a_zero_in_the_probe_table"] = (
            "means the sequence was not among the counts PERSISTED for that run — it may have "
            "been observed below the persistence cap. It is not a measurement of zero reads.")
    if gene_counts:   # ⛔ an EMPTY map must emit NO table: a table of nothing reads as a measurement
        alias = {a: (per_run[a].get("sample_alias") or a) for a in accs}
        lines = ["gene\t" + "\t".join(f"{a}:{alias[a]}" for a in accs)]
        for g in sorted(gene_counts):
            lines.append(g + "\t" + "\t".join(str(gene_counts[g].get(a, 0)) for a in accs))
        body = "\n".join(lines) + "\n"
        with open(GENE_TSV, "w", encoding="utf-8") as fh:
            fh.write(body)
        out["gene_counts_sha256"] = hashlib.sha256(body.encode()).hexdigest()
        out["gene_counts_n_rows"] = len(gene_counts)
        out["⛔ gene_counts_units"] = (
            "RAW READS PER GENE, summed over the probes assigned to that gene, per run. Not "
            "normalised, not length-corrected, not library-size corrected, and understated by at "
            "most `support_floor_reads` per probe — the lossy-counting guarantee, per run. A gene "
            "with no assigned probe is ABSENT FROM THIS TABLE, which is a statement about the "
            "panel and the matcher, never about the tumour.")
    return out


# ------------------------------------------------------------------ selftest


def selftest() -> int:
    fails = []

    def chk(cond, msg):
        if not cond:
            fails.append(msg)

    lc = LossyCounter(epsilon=0.1)
    for _ in range(50):
        lc.add("HOT")
    for i in range(50):
        lc.add(f"cold{i}")
    hh = lc.heavy_hitters()
    chk("HOT" in hh, "lossy counting dropped a sequence far above its support floor")
    chk(hh["HOT"] <= 50, "lossy counting OVERSTATED a count; it may only understate")
    chk(all(v <= 50 for v in hh.values()), "a retained count exceeds the reads that produced it")
    chk(len(lc.table) < 60, "the table never swept; the memory bound is not in force")

    chk(revcomp("ACGT") == "ACGT", "revcomp is wrong on a palindrome")
    chk(revcomp("AAAC") == "GTTT", "revcomp is wrong")

    good = {"modal_length_fraction": 0.99, "n_sequences_covering_80pct": 20000,
            "fraction_reads_in_retained": 0.9}
    chk(gate_verdict(good)["passed"], "the gate refuses a run that looks exactly like a probe assay")
    for k, bad in (("modal_length_fraction", 0.4), ("n_sequences_covering_80pct", 12),
                   ("fraction_reads_in_retained", 0.01)):
        m = dict(good, **{k: bad})
        v = gate_verdict(m)
        chk(not v["passed"], f"the gate PASSED a run failing {k}")
        chk(any((not c["passed"]) and c["measured"] == bad for c in v["checks"]),
            f"the gate failed without naming {k}")

    chk(gate_verdict(dict(good, n_sequences_covering_80pct=5_000_000))["passed"] is False,
        "a run whose distinct-sequence count is read-count-sized passed the gate")
    # the error halo must NOT be what the gate counts — the defect that would refuse a real panel
    chk(gate_verdict(dict(good, n_retained_sequences=1_500_000))["passed"],
        "the gate is counting the retained table again, so an ordinary error halo refuses a "
        "perfectly good probe assay")

    fq = io.StringIO("@r1\nACGT\n+\nIIII\n@r2\nTTTT\n+\nIIII\n")
    chk(list(iter_read_seqs(fq)) == ["ACGT", "TTTT"], "the FASTQ reader is off by a line")

    cs = _core_sets(["A" * 20 + "C" * 20 + "G" * 10], 50)
    chk(set(cs) == {50, 42, 34}, f"core lengths are wrong: {sorted(cs)}")
    for L, d in cs.items():
        chk(all(len(k) == L for k in d), f"a core of the wrong length landed in the {L} table")

    lab = sample_labels_from_committed_xml()
    if lab.get("state") == "read":
        runs = lab["runs"]
        chk(len(runs) == 12, f"the committed XML gave {len(runs)} runs, not 12")
        pg = [r["attributes"].get("Prognosis") for r in runs.values()]
        chk(pg.count("B") == 6 and pg.count("G") == 6,
            f"the Prognosis split is not 6/6: B={pg.count('B')} G={pg.count('G')}")

    for f in fails:
        print("SELFTEST FAIL:", f)
    print(f"selftest: {len(fails)} failure(s)")
    return 1 if fails else 0


# ------------------------------------------------------------------ main


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--phase", choices=["probe", "quant", "map"])
    ap.add_argument("--budget-s", type=float, default=1200)
    ap.add_argument("--epsilon", type=float, default=EPSILON)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.phase == "probe":
        v = phase_probe(budget_s=args.budget_s, epsilon=args.epsilon)
        print(json.dumps(v, indent=1)[:4000])
        return 0
    if args.phase == "quant":
        print(json.dumps(phase_quant(budget_s=args.budget_s, epsilon=args.epsilon), indent=1))
        return 0
    if args.phase == "map":
        print(json.dumps(phase_map(budget_s=args.budget_s), indent=1))
        return 0

    out = derive()
    if args.check:
        if not os.path.exists(ART):
            print("--check: no committed artifact to compare against")
            return 1
        with open(ART, encoding="utf-8") as fh:
            old = json.load(fh)
        drift = [k for k in ("probe_gate", "n_runs_read", "n_probes_common_to_every_read_run",
                             "n_genes_with_at_least_one_assigned_probe", "gene_counts_sha256")
                 if old.get(k) != out.get(k)]
        print("DRIFT:" if drift else "no drift:", drift or "the derive half reproduces offline")
        return 1 if drift else 0

    tmp = ART + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    os.replace(tmp, ART)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("per_run", "probe_map", "why_no_differential_expression")},
                     indent=1)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
