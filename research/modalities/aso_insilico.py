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

  4. siRNA seed-region off-target module. The same junction is targetable by RISC, whose
     delivery toolbox is more mature (the route's real gate is delivery, not chemistry).
     RNAi off-targeting is dominated by GUIDE SEED (positions g2-g8) complementarity, a
     different liability than the gapmer's full-length RNase-H off-target. For each
     candidate we treat the antisense as the RISC guide, extract the seed 7-mer, flag
     whether the seed STRADDLES the junction (a fusion-unique seed = the design goal; a
     seed lying wholly in one parent is a generic, promiscuous seed), and count its exact
     transcriptome occurrences (seed-match off-target load). Reuses the same RefSeq pass.

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

# Breakpoint is parameterisable (env) so the SAME uncapped full-transcriptome evaluation can be
# run on the canonical breakpoint OR on a favorable one identified by the per-breakpoint scan
# (mirrors junction_aso_offtarget.py). This lets us complete the evidence arc: does a favorable
# breakpoint's gapmer set also clear the uncapped off-target + accessibility + seed screen?
if os.environ.get("EWSR1_KEEP_AA"):
    ja.EWSR1_KEEP_AA = int(os.environ["EWSR1_KEEP_AA"])
if os.environ.get("NR4A3_KEEP_AA_FROM"):
    ja.NR4A3_KEEP_AA_FROM = int(os.environ["NR4A3_KEEP_AA_FROM"])
_SUFFIX = os.environ.get("OUT_SUFFIX", "")
OUT = os.path.join(os.path.dirname(__file__), f"aso-insilico-evaluation{_SUFFIX}.json")

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
# 4. siRNA seed-region module (no network; the off-target count is filled in the scan)
# ---------------------------------------------------------------------------
def sirna_seed(candidates):
    """Treat the antisense as the RISC guide; seed = guide positions g2-g8 (7 nt).

    The mRNA 7-mer the seed base-pairs to is target[L-8 : L-1]. The seed STRADDLES the
    junction (fusion-unique seed, the goal) iff that 7-mer spans the EWSR1|NR4A3 boundary
    at target index = bases_from_EWSR1.
    """
    L = ja.OLIGO_LEN
    lo, hi = L - 8, L - 1            # seed 7-mer occupies target[lo:hi]
    for c in candidates:
        t = c["target_mRNA_5to3"]
        seed7 = t[lo:hi]
        j = c["bases_from_EWSR1"]    # junction index within the target window
        spans = (lo < j) and (j <= hi - 1)   # >=1 EWSR1 base and >=1 NR4A3 base in seed
        c["sirna_guide_seed_7mer"] = seed7
        c["sirna_seed_spans_junction"] = bool(spans)
        c["_seed7"] = seed7          # internal, used by the scan; dropped from output
        c["sirna_seed_offtarget_sites"] = 0


# ---------------------------------------------------------------------------
# 1. Transcriptome-wide off-target screen (seed-and-extend, <=1 mismatch)
# ---------------------------------------------------------------------------
def _mismatches(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def _score_candidate_in_record(c, slist, acc, seq, L):
    """The per-candidate scoring logic, unchanged since the EMC panel was screened with it.

    Kept as its own function precisely BECAUSE it is unchanged: `offtarget_scan` below no longer calls
    it for every candidate on every record, only for the candidates a prefilter says could hit. Holding
    the arithmetic still while changing only WHICH candidates reach it is what makes the speed-up
    provably equivalent rather than merely tested-equivalent.
    """
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


def offtarget_scan(candidates, max_records=None):
    """Scan human RefSeq RNA for exact and <=1-mismatch matches to each target window.

    Seed = each 8-mer half of the 16-mer target; pigeonhole guarantees a <=1-mismatch
    16-mer shares an exact 8-mer half, so seeding on both halves finds every <=1mm hit.
    Streams the gz FASTA (constant memory). The chimeric fusion target is absent from
    RefSeq by construction, so any hit here is a genuine off-target.

    ⭐ INVERTED SEED INDEX — THE CHANGE THAT MAKES A CATALOG POSSIBLE (2026-08-13). The original loop
    ran `seq.find()` for EVERY candidate against EVERY record, i.e. O(n_designs x transcriptome). That
    is fine for one junction's 24 designs and impossible for a pan-fusion catalog: at ~19,000 designs it
    is ~2e9 string searches, which is where the "two weeks of wall clock" estimate came from.

    The fix is to invert the loop. One dict maps each candidate's two 8-mer half-seeds (and its siRNA
    seed 7-mer) to the candidates carrying them; each record is then walked ONCE, and only the
    candidates whose seed actually occurs are scored. Cost becomes O(transcriptome) — **independent of
    how many designs are in flight** — so the catalog's whole design set screens in one pass at the
    price the EMC panel alone used to pay.

    ⚠ AND IT IS SLOWER BELOW ~50 DESIGNS, WHICH IS STATED HERE BECAUSE REPORTING ONLY THE FAVOURABLE
    HALF OF A BENCHMARK IS HOW A "SPEED-UP" BECOMES FOLKLORE. Measured 2026-08-13 over a synthetic
    3,000-record / 7.5 Mbp transcriptome (random sequence, so hit density is lower than real RefSeq):

        designs      reference       inverted     speed-up
             24          0.99 s         1.57 s         0.6x
            100          4.28 s         1.88 s         2.3x
            400         16.91 s         3.02 s         5.6x

    The reference scales linearly in design count (4x designs -> 4.2x time) and the inverted walk is
    nearly flat, so the crossover sits near 50 designs and every catalog-scale run is far past it. The
    single-junction EMC lane runs 24 designs and therefore pays about 0.6 s per 7.5 Mbp more than it
    used to — immaterial beside the ~1.5 GB FASTA download in the same job, and worth one code path
    rather than two, since a rarely-taken second branch is a branch that rots. ⚠ The extrapolation to
    a full catalog run is an EXTRAPOLATION from this synthetic, not a measurement of RefSeq.

    ⛔ THE SEMANTICS ARE NOT "CLOSE ENOUGH", AND THAT WAS A DESIGN CONSTRAINT RATHER THAN A HOPE. The
    index decides only WHICH candidates are examined; `_score_candidate_in_record` above then does
    exactly what it always did, including the per-record `seen` de-duplication and the order in which
    the first five hits are recorded. A candidate the index skips would have found `seq.find(seed) ==
    -1` and contributed nothing, so skipping it cannot change a count. Likewise the siRNA seed load
    still comes from `str.count`, which counts NON-overlapping occurrences — a sliding-window count
    would silently differ on a self-overlapping 7-mer, which is the kind of quiet numeric drift this
    repository keeps paying for. `tests/test_aso_insilico_scan_equivalence.py` runs both implementations
    over the same synthetic transcriptome and asserts every emitted field matches.
    """
    L = ja.OLIGO_LEN
    half = L // 2
    # per candidate: two seeds and the position of each seed within the 16-mer
    seeds = []
    seed_index = {}
    seed7_index = {}
    for ci, c in enumerate(candidates):
        t = c["target_mRNA_5to3"]
        slist = [(t[:half], 0), (t[half:], half)]
        seeds.append((ci, slist))
        for s, _off in slist:
            seed_index.setdefault(s, set()).add(ci)
        seed7 = c.get("_seed7")
        if seed7:
            seed7_index.setdefault(seed7, set()).add(ci)
        c["offtarget_exact"] = 0
        c["offtarget_le1mm"] = 0
        c["offtarget_hits"] = []

    tmp = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "grch38_rna.fna.gz")
    if not os.path.exists(tmp):
        print(f"  downloading RefSeq RNA -> {tmp}", file=sys.stderr)
        urllib.request.urlretrieve(REFSEQ_RNA_URL, tmp)

    def scan_seq(acc, seq):
        n = len(seq)
        hit8, hit7 = set(), set()
        # one walk of the record; two O(1) lookups per position
        for i in range(n - 6):
            if seed7_index:
                v = seed7_index.get(seq[i:i + 7])
                if v:
                    hit7 |= v
            if i + half <= n:
                v = seed_index.get(seq[i:i + half])
                if v:
                    hit8 |= v
        for ci in hit7:
            c = candidates[ci]
            c["sirna_seed_offtarget_sites"] += seq.count(c["_seed7"])
        for ci in hit8:
            _score_candidate_in_record(candidates[ci], seeds[ci][1], acc, seq, L)

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
            -c.get("offtarget_le1mm", 0),         # fewer gapmer off-targets first (safety)
            round(acc, 3),                        # more accessible site (potency)
            1 if c.get("sirna_seed_spans_junction") else 0,  # fusion-unique siRNA seed
            -c.get("sirna_seed_offtarget_sites", 0),         # lower RISC seed-match load
            c["specificity_margin"],              # balanced junction
            -gc_pen,                              # mid GC
            0 if not c["has_G4_motif"] else -1,
            -c.get("cpg_count", 0),
        )
    return sorted(candidates, key=key, reverse=True)


def main():
    do_offtarget = os.environ.get("ASO_OFFTARGET", "1") != "0"
    max_records = os.environ.get("ASO_OFFTARGET_MAX")
    max_records = int(max_records) if max_records else None

    ews, nr4, left, right, fusion = ja.build_parents_and_fusion()
    label, prov = ja.junction_label()
    designs = ja.design(left, right, fusion)
    candidates = [dict(d) for d in designs[:N_EVAL]]

    acc_status = accessibility(fusion, candidates)
    liabilities(candidates)
    sirna_seed(candidates)

    ot_status = {"status": "skipped (ASO_OFFTARGET=0)"}
    if do_offtarget:
        try:
            ot_status = offtarget_scan(candidates, max_records=max_records)
        except Exception as e:  # noqa
            ot_status = {"status": f"error: {e}"}
            print(f"  off-target scan failed: {e}", file=sys.stderr)

    ranked = combine_rank(candidates)
    for c in candidates:
        c.pop("_seed7", None)  # internal scratch
    n_clean = sum(1 for c in candidates if c.get("offtarget_le1mm", 0) == 0)
    n_seed_specific = sum(1 for c in candidates if c.get("sirna_seed_spans_junction"))

    result = {
        "_note": "In-silico evaluation of EWSR1::NR4A3 junction gapmers: transcriptome "
                 "off-target screen + target-site accessibility + sequence liabilities. "
                 "EVALUATION ONLY — hypotheses for wet-lab testing, not a validated drug. "
                 "Does NOT address tumour delivery (the route's real bottleneck).",
        "junction_label": label,
        # ⛔ REAL MODE MUST CARRY THE MEASURED GRADING, NOT JUST A LABEL. A junction LABEL with no
        # graded offsets beside it is exactly how the retracted seam stayed invisible in every file
        # that depended on it (junction_aso.py, two-defect block). One home for the arithmetic:
        # `junction_aso.LAST_JUNCTION`, set by the real-mode builder that just ran.
        "breakpoint": {**prov, "junction_context_mRNA": (left[-12:] + "|" + right[:12]),
                       "_transcript_source": ja.transcript_source_provenance(),
                       **({"measured_junction": {k: v for k, v in ja.LAST_JUNCTION.items()
                                                 if not k.startswith("_")}}
                          if ja.LAST_JUNCTION else {})},
        "n_evaluated": len(candidates),
        "accessibility": acc_status,
        "offtarget_screen": ot_status,
        "n_candidates_zero_offtarget": n_clean if do_offtarget else None,
        "n_candidates_fusion_specific_sirna_seed": n_seed_specific,
        "sirna_note": "For a dedicated siRNA, design the duplex so the junction falls inside "
                      "the guide seed (g2-g8) — these gapmer-derived windows are evaluated "
                      "as-is, so seed-straddling is reported, not enforced.",
        "ranking_key": "fewest gapmer off-targets > most accessible site > fusion-specific "
                       "siRNA seed > lower RISC seed load > balanced junction > mid-GC > no G4 "
                       "> fewer CpG",
        "top_designs": [
            {k: c.get(k) for k in (
                "antisense_5to3", "target_mRNA_5to3", "architecture", "specificity_margin",
                "gc_percent", "site_accessibility", "offtarget_exact", "offtarget_le1mm",
                "offtarget_hits", "sirna_guide_seed_7mer", "sirna_seed_spans_junction",
                "sirna_seed_offtarget_sites", "cpg_count", "has_G4_motif", "max_homopolymer",
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
