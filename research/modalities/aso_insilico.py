#!/usr/bin/env python3
"""
In-silico evaluation of the EWSR1::NR4A3 junction gapmer ASOs (advance the ASO route).

`junction_aso.py` DESIGNS fusion-junction gapmers and checks they are not perfect
complements of either parent transcript. This script EVALUATES those designs with the
analyses that decide whether a gapmer is worth synthesising — all sequence/RNA problems
that need no protein structure and no wet lab:

  1. Transcriptome-wide off-target screen (the load-bearing one). Gapmer toxicity is
     driven by hybridization-dependent off-target RNase-H cleavage of UNINTENDED
     transcripts. We scan every candidate's target window against the whole human RefSeq
     transcriptome (GRCh38) for exact and <=1-mismatch matches (seed-and-extend; by the
     pigeonhole principle a <=1-mismatch 16-mer shares an exact 8-mer half). A candidate
     with off-target hits is hybridization-promiscuous regardless of how fusion-specific
     it looked against the two parents alone. Fewer hits = safer. [Needs internet ->
     runs in CI; downloads the RefSeq RNA FASTA.]

  2. Target-site accessibility (potency). RNase-H1 needs a single-stranded target. We
     fold the fusion mRNA around the junction (ViennaRNA partition function) and score
     each candidate site by its mean per-base unpaired probability. Buried sites are
     poor knockdown sites; this RANKS the designs by predicted potency.

  3. Sequence-liability filters (tox/immunostimulation). CpG-dinucleotide count (TLR9
     immunostimulation), G-quadruplex (G>=4), and homopolymer runs — standard ASO triage
     heuristics.

We then combine these into a ranked shortlist. What this CANNOT do: solve delivery to
tumour (the route's real bottleneck, named in the roadmap paper). This advances
specificity + potency-site selection, not deliverability.

Output: aso-insilico-evaluation.json   (consumed by emc-treatment-roadmap.md)

DESIGN/EVALUATION ONLY — hypotheses for wet-lab testing, not a validated drug.
"""

import gzip
import json
import os
import re
import sys
import urllib.request

import junction_aso as ja  # reuse fetch_cds / build_fusion_cds / design (same dir)

OUT = os.path.join(os.path.dirname(__file__), "aso-insilico-evaluation.json")

# Human RefSeq RNA (GRCh38.p14) — curated transcripts; stable NCBI FTP path.
REFSEQ_RNA_URL = ("https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/"
                  "GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_rna.fna.gz")

N_EVAL = 24   # evaluate the top-N junction-spanning candidates from junction_aso


# ---------------------------------------------------------------------------
# 2. Target-site accessibility (ViennaRNA partition function)
# ---------------------------------------------------------------------------
def accessibility(fusion, candidates, pad=80):
    """Mean unpaired probability over each candidate's target window.

    Folds a local window of the fusion mRNA centred on the junction (the only region
    candidates occupy), so the fold is tractable and reflects local structure.
    """
    try:
        import RNA  # ViennaRNA
    except ImportError:
        for c in candidates:
            c["site_accessibility"] = None
        return {"status": "ViennaRNA missing (pip install ViennaRNA) — accessibility skipped"}

    # window spanning all candidate sites + padding
    starts = [fusion.index(c["target_mRNA_5to3"]) for c in candidates]
    ends = [s + len(c["target_mRNA_5to3"]) for s, c in zip(starts, candidates)]
    wstart = max(0, min(starts) - pad)
    wend = min(len(fusion), max(ends) + pad)
    window = fusion[wstart:wend]

    fc = RNA.fold_compound(window)
    fc.pf()  # partition function -> base-pair probability matrix
    n = len(window)
    bpp = fc.bpp()  # 1-indexed [n+1][n+1]
    paired = [0.0] * (n + 1)
    for i in range(1, n + 1):
        s = 0.0
        for j in range(1, n + 1):
            s += bpp[i][j] if j > i else bpp[j][i]
        paired[i] = min(1.0, s)
    unpaired = [1.0 - paired[i] for i in range(1, n + 1)]  # 0-indexed over window

    for c, st in zip(candidates, starts):
        a = st - wstart
        b = a + len(c["target_mRNA_5to3"])
        seg = unpaired[a:b]
        c["site_accessibility"] = round(sum(seg) / len(seg), 3) if seg else None
    return {"status": "ok", "window_mRNA_span": [wstart, wend], "window_len": n}


# ---------------------------------------------------------------------------
# 3. Sequence-liability filters
# ---------------------------------------------------------------------------
def liabilities(candidates):
    for c in candidates:
        anti = c["antisense_5to3"]
        c["cpg_count"] = len(re.findall(r"CG", anti))           # TLR9 immunostim proxy
        c["has_G4_motif"] = bool(re.search(r"G{4,}", c["target_mRNA_5to3"]))
        c["max_homopolymer"] = max(len(m.group()) for m in re.finditer(r"(.)\1*", anti))


# ---------------------------------------------------------------------------
# 1. Transcriptome-wide off-target screen (seed-and-extend, <=1 mismatch)
# ---------------------------------------------------------------------------
def _mismatches(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def offtarget_scan(candidates, max_records=None):
    """Scan human RefSeq RNA for exact and <=1-mismatch matches to each target window.

    Seed = each 8-mer half of the 16-mer target; pigeonhole guarantees a <=1-mismatch
    16-mer shares an exact 8-mer half, so seeding on both halves finds every <=1mm hit.
    Streams the gz FASTA (constant memory). The chimeric fusion target is absent from
    RefSeq by construction, so any hit here is a genuine off-target.
    """
    L = ja.OLIGO_LEN
    half = L // 2
    # per candidate: two seeds and the position of each seed within the 16-mer
    seeds = []
    for ci, c in enumerate(candidates):
        t = c["target_mRNA_5to3"]
        seeds.append((ci, [(t[:half], 0), (t[half:], half)]))
        c["offtarget_exact"] = 0
        c["offtarget_le1mm"] = 0
        c["offtarget_hits"] = []

    tmp = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "grch38_rna.fna.gz")
    if not os.path.exists(tmp):
        print(f"  downloading RefSeq RNA -> {tmp}", file=sys.stderr)
        urllib.request.urlretrieve(REFSEQ_RNA_URL, tmp)

    def scan_seq(acc, seq):
        for ci, slist in seeds:
            c = candidates[ci]
            t = c["target_mRNA_5to3"]
            seen = set()
            for seed, off in slist:
                idx = seq.find(seed)
                while idx != -1:
                    wstart = idx - off
                    if 0 <= wstart and wstart + L <= len(seq):
                        if wstart not in seen:
                            seen.add(wstart)
                            mm = _mismatches(seq[wstart:wstart + L], t)
                            if mm <= 1:
                                c["offtarget_le1mm"] += 1
                                if mm == 0:
                                    c["offtarget_exact"] += 1
                                if len(c["offtarget_hits"]) < 5:
                                    c["offtarget_hits"].append({"acc": acc, "mm": mm})
                    idx = seq.find(seed, idx + 1)

    acc, parts, nrec = None, [], 0
    with gzip.open(tmp, "rt") as fh:
        for line in fh:
            if line.startswith(">"):
                if acc is not None:
                    scan_seq(acc, "".join(parts))
                    nrec += 1
                    if max_records and nrec >= max_records:
                        acc = None
                        break
                acc = line[1:].split()[0]
                parts = []
            else:
                parts.append(line.strip().upper())
        if acc is not None:
            scan_seq(acc, "".join(parts))
            nrec += 1
    return {"status": "ok", "transcripts_scanned": nrec, "source": REFSEQ_RNA_URL}


# ---------------------------------------------------------------------------
def combine_rank(candidates):
    """Combined shortlist: prefer no off-targets, accessible site, balanced GC, no
    liabilities. Off-target count dominates (safety), then accessibility (potency)."""
    def key(c):
        acc = c.get("site_accessibility")
        acc = acc if acc is not None else 0.0
        gc_pen = abs(c["gc_percent"] - 50)
        return (
            -c.get("offtarget_le1mm", 0),     # fewer off-targets first
            round(acc, 3),                    # more accessible
            c["specificity_margin"],          # balanced junction
            -gc_pen,                          # mid GC
            0 if not c["has_G4_motif"] else -1,
            -c.get("cpg_count", 0),
        )
    return sorted(candidates, key=key, reverse=True)


def main():
    do_offtarget = os.environ.get("ASO_OFFTARGET", "1") != "0"
    max_records = os.environ.get("ASO_OFFTARGET_MAX")
    max_records = int(max_records) if max_records else None

    ews = ja.fetch_cds(ja.EWSR1_MRNA)
    nr4 = ja.fetch_cds(ja.NR4A3_MRNA)
    ja.EWSR1_full, ja.NR4A3_full = ews, nr4
    left, right, fusion = ja.build_fusion_cds(ews, nr4)
    designs = ja.design(left, right, fusion)
    candidates = [dict(d) for d in designs[:N_EVAL]]

    acc_status = accessibility(fusion, candidates)
    liabilities(candidates)

    ot_status = {"status": "skipped (ASO_OFFTARGET=0)"}
    if do_offtarget:
        try:
            ot_status = offtarget_scan(candidates, max_records=max_records)
        except Exception as e:  # noqa
            ot_status = {"status": f"error: {e}"}
            print(f"  off-target scan failed: {e}", file=sys.stderr)

    ranked = combine_rank(candidates)
    n_clean = sum(1 for c in candidates if c.get("offtarget_le1mm", 0) == 0)

    result = {
        "_note": "In-silico evaluation of EWSR1::NR4A3 junction gapmers: transcriptome "
                 "off-target screen + target-site accessibility + sequence liabilities. "
                 "EVALUATION ONLY — hypotheses for wet-lab testing, not a validated drug. "
                 "Does NOT address tumour delivery (the route's real bottleneck).",
        "n_evaluated": len(candidates),
        "accessibility": acc_status,
        "offtarget_screen": ot_status,
        "n_candidates_zero_offtarget": n_clean if do_offtarget else None,
        "ranking_key": "fewest off-targets > most accessible site > balanced junction > "
                       "mid-GC > no G4 > fewer CpG",
        "top_designs": [
            {k: c.get(k) for k in (
                "antisense_5to3", "target_mRNA_5to3", "architecture", "specificity_margin",
                "gc_percent", "site_accessibility", "offtarget_exact", "offtarget_le1mm",
                "offtarget_hits", "cpg_count", "has_G4_motif", "max_homopolymer",
                "fusion_specific")}
            for c in ranked[:12]
        ],
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: result[k] for k in
                      ("n_evaluated", "accessibility", "offtarget_screen",
                       "n_candidates_zero_offtarget")}, indent=2))


if __name__ == "__main__":
    main()
