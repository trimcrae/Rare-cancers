#!/usr/bin/env python3
"""Is *RET* a target GENE of the EWSR1::NR4A3 fusion, and does RET in EMC clear the
"measured activation" bar that MET in clear cell sarcoma failed?

WHY THIS EXISTS
---------------
`emc-unexplored-treatment-lanes.md` §3.1 ranks RET first of twelve new lanes on two published
readings:

  * PMID 24703573 (Stacchiotti, Eur J Cancer 2014, n=10 sunitinib series, 6 PR / 2 SD / 2 PD),
    verbatim: *"Among putative sunitinib targets, only RET was expressed and activated in
    analysed samples"*.
  * PMID 28423517 (Oncotarget 2017): RET expression significantly higher in EMC than in other
    sarcomas except liposarcoma.

and it names the free next step as *"an NBRE-motif scan of its regulatory region, the same
bioinformatic approach that established PPARG and ENO3 as direct targets, plus a read across the
public EMC expression series"*, with the falsifier *"no NBRE at RET, PLUS evidence that RET
phosphorylation tracks stromal rather than tumour content"*.

This module is that instrument. It has three parts and each reports its own status separately,
because they fail for different reasons and an absent reading is not a reading of absence
(CLAUDE.md §4).

  PART 1  NBRE motif scan of RET's regulatory region, with TWO nulls.
  PART 2  RET expression across the public EMC series (GSE24369/GPL6244, GSE4303/GPL3290) and
          the stroma-vs-tumour covariation that the falsifier's second clause needs.
  PART 3  The activation-bar audit: what the primary sources actually MEASURED, read from the
          Europe PMC corpus fetched by `fetch-literature.yml` (the sandbox egress proxy answers
          403 to CONNECT for www.ebi.ac.uk, ftp.ncbi.nlm.nih.gov and rest.ensembl.org — measured
          2026-08-07 from the proxy's own `recentRelayFailures`).

⛔ WHAT A MOTIF SCAN CAN AND CANNOT SAY. An NBRE is an 8-mer. In random sequence of even base
composition the expected count in a 25 kb window read on both strands is <1, so ONE hit is not
a finding — it is what the genome does anyway. This module therefore never reports a raw count as
a result. It reports the count against (a) a dinucleotide-preserving shuffle null of the SAME
window, which controls GC and CpG exactly, and (b) the rank of that window among a background
panel of gene windows fetched identically. And even a strongly enriched window is a
PLAUSIBILITY FILTER, never evidence of occupancy: only ChIP establishes binding. This is stated
in the artifact's own `_what_this_cannot_conclude`, not left to the reader.

⛔ NO CLAIM OF SELECTIVITY, EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS FOR EMC
is made anywhere in this module or its artifact. Selpercatinib and pralsetinib are named only as
approved agents that exist; nothing here says they should be given to anyone.

MOTIF DEFINITIONS, WITH THEIR SOURCES (never invented here)
-----------------------------------------------------------
  NBRE   5'-AAAGGTCA-3'  — the NGFI-B response element, the NR4A monomer site.
                            Wilson TE et al., Science 1991;252:1296-1300 (PMID 1902986).
  NurRE  5'-TGATATTT(N6)AAATGCCA-3' — the everted-repeat NR4A dimer site.
                            Philips A et al., Mol Cell Biol 1997;17:5946-5951 (PMID 9315667).
  ⚠ NR4A3 homodimerisation on NurRE is weaker than NR4A1/NR4A2 — recorded in this repository's
    own `nr4a3-emc-biology-evidence.md`, and the reason NurRE is reported beside NBRE rather
    than pooled with it.

USAGE
-----
  python3 emc_ret_target_scan.py --selftest      # offline; proves the motif + null engine
  python3 emc_ret_target_scan.py --fetch         # CI ONLY: Ensembl + GEO. Needs egress.
  python3 emc_ret_target_scan.py                 # derive from the inputs cache, write artifact
  python3 emc_ret_target_scan.py --check         # re-derive and diff against the committed file
"""
from __future__ import annotations

import argparse
from collections import deque
import gzip
import json
import math
import os
import random
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-ret-target-scan.json")
INPUTS = os.path.join(HERE, "emc-ret-target-scan-inputs.json")

sys.path.insert(0, HERE)

# ---------------------------------------------------------------------------------------------
# Motifs.  One home; every consensus carries the PMID that defines it.
# ---------------------------------------------------------------------------------------------
NBRE = "AAAGGTCA"
NBRE_PMID = "1902986"
NURRE_LEFT = "TGATATTT"
NURRE_RIGHT = "AAATGCCA"
NURRE_SPACER = 6
NURRE_PMID = "9315667"

# ---------------------------------------------------------------------------------------------
# The window.  Frozen before any RET sequence was read, and RE-frozen once — on a published fact
# about RET's regulatory architecture, never on a result.
# ---------------------------------------------------------------------------------------------
# ⛔ THE FIRST CHOICE (TSS +/- 5 kb) WOULD HAVE MISSED THE ONLY EXPERIMENTALLY VALIDATED DISTAL
# ELEMENT RET HAS. HOXB5 binds a multi-species conserved sequence at **MCS+9.7, in RET's FIRST
# INTRON**, and deleting that site abolishes HOXB5 trans-activation of the RET promoter
# (PMID 24794774). Separately, ETV5 ChIP-seq identifies binding at the RET promoter AND an enhancer
# UPSTREAM of it (PMID 29321660). A symmetric 5 kb window is therefore not a neutral default for
# this gene -- it is a window chosen in ignorance of where this gene's regulation is known to live,
# and a null result from it would have been an artefact of the scope.
#
# ⚠ THE TIMING IS WHAT MAKES THIS LEGITIMATE RATHER THAN TUNING. No RET sequence has been fetched;
# `part_1_nbre_scan` reads NOT_RUN. The change is driven by two citations about the gene, not by
# any count this module produced. CLAUDE.md's rule is to scope a test up front and not to add rigour
# reactively under prodding -- widening on published architecture BEFORE the first read is the
# opposite of that failure. Superseded, retained: WINDOW_UPSTREAM = 5000, WINDOW_DOWNSTREAM = 5000.
WINDOW_UPSTREAM = 10000
WINDOW_DOWNSTREAM = 15000
KNOWN_RET_REGULATORY_ELEMENTS = [
    {"name": "MCS+9.7", "where": "RET first intron, ~+9.7 kb from the TSS",
     "bound_by": "HOXB5", "source_pmid": "24794774",
     "evidence": "binding confirmed; deletion of the site abolishes HOXB5 trans-activation of the "
                 "RET promoter in a RET mini-gene reporter",
     "inside_window": True},
    {"name": "upstream ETV5 enhancer", "where": "upstream of the RET promoter",
     "bound_by": "ETV5", "source_pmid": "29321660",
     "evidence": "ChIP-seq binding at the RET promoter plus an enhancer upstream of it",
     "inside_window": "position not given numerically in the retrieved abstract — ⚠ ABSENT "
                      "READING, so whether 10 kb reaches it is UNKNOWN, not assumed"},
]
N_SHUFFLES = 2000
SHUFFLE_SEED = 20260807

# Subject + the memo's own named positive controls + the family itself.
FOCUS_GENES = {
    "RET": "the subject: emc-unexplored-treatment-lanes.md §3.1",
    "ENO3": "named in §5 item 6 as the fusion's demonstrated direct target (PMID 26310886)",
    "PPARG": "named in §3.1 as an established direct target of the fusion",
    # ⭐ ADDED 2026-08-07. The THIRD and only remaining class-A gene — the one direct target
    # assayed with the EWSR1 chimera itself, in human cells, with a chromatin assay (ChAP-qPCR
    # against a predicted NBRE-like site; Brenca et al., J Pathol 2019, PMID 31020999). ENO3 and
    # PPARG were already here, so without SEMA3C the panel covered two thirds of the published
    # direct-target set and the third gene was the strongest of the three on assay quality.
    # `nr4a3-fusion-transcriptional-output.md` §4.2 item 4 names this scan as its free next step.
    "SEMA3C": "the third class-A direct target, and the only one assayed with EWSR1::NR4A3 in "
              "human cells with a chromatin assay (PMID 31020999)",
    "NR4A3": "the fusion's own 3' partner — autoregulation is an NBRE question too",
    "NR4A1": "the paralogue; a family-wide element should appear here as well",
    "VEGFA": "the conventional attribution for EMC's TKI activity — the alternative hypothesis",
    "KDR": "VEGFR2, same alternative hypothesis",
}

# ⭐ THE BACKGROUND PANEL IS NOT CHOSEN BY ME. It is read from a gene list this repository already
# committed for an unrelated purpose — the 1,299 symbols measured on GPL6244 in
# `emc-atr-vulnerability-inputs.json` (the ATR/DDR concept universe plus its myogenesis,
# adipogenesis and OXPHOS controls). Using a list assembled for a different question is the whole
# point: it cannot have been picked to make RET look good or bad. Its composition IS a bias —
# gene-set genes skew to CpG-island promoters — so the GC-matched subset rank is reported
# alongside the raw rank rather than instead of it.
BACKGROUND_SOURCE = "emc-atr-vulnerability-inputs.json:part_b.platforms.GSE24369_series_matrix.txt.gz.geneset_gene_values"
N_BACKGROUND = 200

# ---------------------------------------------------------------------------------------------
# PART 2 panels.  Every symbol is a marker with a stated role; nothing is a free parameter.
# ---------------------------------------------------------------------------------------------
STROMAL_PANEL = ["COL1A1", "COL1A2", "COL3A1", "COL5A1", "COL6A3", "LUM", "DCN", "POSTN",
                 "FN1", "THY1", "PDGFRB", "ACTA2", "FBN1", "SPARC"]
VASCULAR_PANEL = ["PECAM1", "CDH5", "VWF", "KDR", "TEK", "ENG"]
IMMUNE_PANEL = ["PTPRC", "CD68", "CD3E", "CSF1R"]
# EMC tumour-cell / fusion-programme markers as this repository already cites them
# (nr4a3-emc-biology-evidence.md; emc-unexplored-treatment-lanes.md §5 items 6 and 7).
TUMOUR_PANEL = ["NR4A3", "ENO3", "PPARG", "INSM1", "SYP", "CHGA", "S100B", "NKX2-2", "SOX9"]
PROLIF_PANEL = ["MKI67"]
RET_PARTNERS = ["RET", "GDNF", "GFRA1", "GFRA2", "GFRA3", "ARTN", "NRTN", "PSPN"]

SERIES = {
    # Sample counts below are DERIVED by running `_classify` over the verbatim annotations already
    # committed in emc-atr-vulnerability-inputs.json, not remembered.
    "GSE24369": {"platform": "GPL6244", "why": "42 samples — 6 EMC, 29 classified comparators "
                                               "(desmoid, LGFMS, myxofibrosarcoma), 7 unclassified "
                                               "(2 skeletal muscle, 5 solitary fibrous tumour). "
                                               "Single-channel intensity, so ABSOLUTE expression. "
                                               "⚠ The 7 unclassified are excluded from BOTH arms "
                                               "rather than guessed into one."},
    "GSE4303": {"platform": "GPL3290", "why": "16 samples — 10 EMC, 6 comparators (3 GIST, 3 DFSP). "
                                              "Two-colour log-ratio vs a reference pool, so "
                                              "RELATIVE only. ⚠ Its EMC samples are titled 'Myxoid "
                                              "Chondrosarcoma' with no 'extraskeletal', which is "
                                              "what an EMC-phrase-only classifier gets wrong."},
}

FRAMING = (
    "Asks whether RET is a TARGET GENE of the EWSR1::NR4A3 fusion and whether RET in EMC clears "
    "the measured-activation bar that MET in clear cell sarcoma failed. Motif enrichment is a "
    "plausibility filter, not evidence of occupancy; mRNA is not phosphorylation. No claim of "
    "selectivity, efficacy, safety, a therapeutic window or clinical readiness is made or implied."
)


# ---------------------------------------------------------------------------------------------
# Sequence utilities — pure stdlib, no numpy (the sandbox has none; CLAUDE.md preflight note).
# ---------------------------------------------------------------------------------------------
_COMP = str.maketrans("ACGTNacgtn", "TGCANtgcan")


def revcomp(s: str) -> str:
    return s.translate(_COMP)[::-1]


def find_all(seq: str, pattern: str, max_mismatch: int = 0):
    """Every start index at which `pattern` matches `seq` with <= max_mismatch substitutions.

    Deliberately naive: the windows are ~25 kb and the patterns are 8-mers, so an O(n*m) scan is
    microseconds and a clever implementation would only add a place for a bug to hide.
    """
    n, m = len(seq), len(pattern)
    hits = []
    for i in range(n - m + 1):
        mm = 0
        for j in range(m):
            if seq[i + j] != pattern[j]:
                mm += 1
                if mm > max_mismatch:
                    break
        else:
            hits.append(i)
    return hits


def scan_nbre(seq: str, max_mismatch: int = 0):
    """NBRE hits on BOTH strands, de-duplicated by genomic position.

    ⚠ A palindromic hit would otherwise be counted twice. NBRE is not palindromic, so this cannot
    fire for NBRE itself — the de-duplication is here so the function stays correct if a future
    caller passes a palindromic element, which is exactly the kind of silent double-count that
    would inflate an enrichment.
    """
    seq = seq.upper()
    fwd = [(i, "+") for i in find_all(seq, NBRE, max_mismatch)]
    rc = revcomp(seq)
    n = len(seq)
    rev = [(n - i - len(NBRE), "-") for i in find_all(rc, NBRE, max_mismatch)]
    seen, out = set(), []
    for pos, strand in sorted(fwd + rev):
        if pos in seen:
            continue
        seen.add(pos)
        out.append({"pos": pos, "strand": strand})
    return out


def scan_nurre(seq: str, spacer_tolerance: int = 2):
    """Everted-repeat NurRE: TGATATTT - N6 - AAATGCCA, on both strands.

    The spacer is allowed to vary by +/- `spacer_tolerance` because the published element is an
    everted repeat with a nominal 6-bp gap, not a fixed-length string.
    """
    seq = seq.upper()
    out = []
    for strand, s in (("+", seq), ("-", revcomp(seq))):
        lefts = find_all(s, NURRE_LEFT)
        rights = set(find_all(s, NURRE_RIGHT))
        for li in lefts:
            for gap in range(NURRE_SPACER - spacer_tolerance, NURRE_SPACER + spacer_tolerance + 1):
                ri = li + len(NURRE_LEFT) + gap
                if ri in rights:
                    pos = li if strand == "+" else len(seq) - ri - len(NURRE_RIGHT)
                    out.append({"pos": pos, "strand": strand, "spacer": gap})
    return sorted(out, key=lambda r: (r["pos"], r["strand"]))


def gc_fraction(seq: str) -> float:
    s = seq.upper()
    acgt = sum(s.count(b) for b in "ACGT")
    if not acgt:
        return 0.0
    return round((s.count("G") + s.count("C")) / acgt, 4)


def dinucleotide_shuffle(seq: str, rng: random.Random) -> str:
    """Altschul-Erikson dinucleotide-preserving shuffle (Euler-path form).

    ⭐ WHY NOT A PLAIN SHUFFLE. A mononucleotide shuffle preserves GC and destroys CpG, and CpG
    depletion is the single strongest compositional feature of mammalian promoters. An NBRE is
    A/T-rich in its first half, so a mononucleotide null systematically UNDERSTATES the chance
    count in a real promoter and would manufacture enrichment. Preserving dinucleotides removes
    that whole class of artefact.
    """
    s = [c for c in seq.upper() if c in "ACGT"]
    if len(s) < 4:
        return "".join(s)
    last = s[-1]
    edges = {}
    for a, b in zip(s, s[1:]):
        edges.setdefault(a, []).append(b)
    # Wilson's algorithm on the vertex set: build a random arborescence into `last`, then shuffle
    # the remaining out-edges freely. This is the standard correct construction.
    verts = list(edges)
    for _ in range(100):
        tree = {}
        ok = True
        for v in verts:
            if v == last:
                continue
            path, cur = [], v
            for _step in range(1000):
                if cur == last or cur in tree:
                    break
                nxt = rng.choice(edges[cur])
                tree[cur] = nxt
                path.append(cur)
                cur = nxt
            else:
                ok = False
                break
            # cycle check: the walk must terminate at `last` or at an already-resolved vertex
            seen, cur = set(), v
            while cur in tree and cur not in seen:
                seen.add(cur)
                cur = tree[cur]
            if cur != last and cur not in seen:
                ok = False
        if not ok:
            continue
        # every vertex must reach `last` through `tree`
        good = True
        for v in verts:
            if v == last:
                continue
            cur, steps = v, 0
            while cur != last and steps < len(verts) + 2:
                cur = tree.get(cur)
                if cur is None:
                    good = False
                    break
                steps += 1
            if cur != last:
                good = False
            if not good:
                break
        if not good:
            continue
        pool = {}
        for v, outs in edges.items():
            rest = list(outs)
            if v != last:
                rest.remove(tree[v])
            rng.shuffle(rest)
            if v != last:
                rest.append(tree[v])
            # ⚠ A `deque`, NOT a list, and the reason is asymptotic rather than stylistic.
            # `rest` is shuffled as a LIST above, so every rng call and the resulting order are
            # untouched by this line -- the deque only changes how the SAME sequence is consumed
            # below. `list.pop(0)` is O(len), so walking a 25 kb window pops ~25,000 times out of
            # four pools of ~6,250 and moves ~78 million elements PER SHUFFLE, times N_SHUFFLES.
            # Measured 2026-08-08: that one quadratic made
            # test_the_committed_artifact_rederives_from_its_inputs 3,718 s of a 3,842 s suite --
            # 96.8% of the whole run, against a 45 s second-place. `popleft()` is O(1).
            pool[v] = deque(rest)
        out, cur = [s[0]], s[0]
        for _ in range(len(s) - 1):
            nxt = pool[cur].popleft()
            out.append(nxt)
            cur = nxt
        return "".join(out)
    # ⚠ FALL BACK LOUDLY, NEVER SILENTLY. A failed Euler construction that quietly returned a
    # mononucleotide shuffle would produce a null with the wrong composition and no way to tell.
    raise RuntimeError("dinucleotide shuffle failed to build an Euler path")


def shuffle_null(seq: str, n: int, seed: int):
    """Empirical null for the NBRE count in THIS window, composition held fixed.

    ⭐ COMPUTES THE ONE-MISMATCH NULL ON THE SAME SHUFFLES (added 2026-08-08). An exact 8-mer is
    not the only site an NR4A protein reads: Brenca et al. report a predicted NBRE-**LIKE** site at
    SEMA3C, and this module's own exact scan finds zero exact NBREs there against 39 one-mismatch
    matches — the most of any window scanned. A bare count of 39 says nothing, because a degenerate
    8-mer with one substitution allowed occurs far more often by chance and its expected rate
    depends on composition; without a null it can be read as "plenty of sites" or "none", which is
    exactly the uncalibrated number this module exists to refuse.
    ⛔ The two counts are taken from the SAME shuffled sequences on purpose. It costs one extra scan
    per shuffle instead of a second 2,000-shuffle pass, and — because `dinucleotide_shuffle` is the
    only consumer of `rng` — the number and order of random draws is unchanged, so every EXACT
    figure this function already published is byte-identical. A cheaper null that perturbed the
    committed exact numbers would have been the wrong trade at any speed.
    """
    rng = random.Random(seed)
    obs = len(scan_nbre(seq))
    obs_1mm = len(scan_nbre(seq, max_mismatch=1))
    counts = []
    counts_1mm = []
    for _ in range(n):
        sh = dinucleotide_shuffle(seq, rng)
        counts.append(len(scan_nbre(sh)))
        counts_1mm.append(len(scan_nbre(sh, max_mismatch=1)))
    ge = sum(1 for c in counts if c >= obs)
    mean = sum(counts) / len(counts)
    var = sum((c - mean) ** 2 for c in counts) / (len(counts) - 1) if len(counts) > 1 else 0.0
    ge1 = sum(1 for c in counts_1mm if c >= obs_1mm)
    mean1 = sum(counts_1mm) / len(counts_1mm)
    var1 = (sum((c - mean1) ** 2 for c in counts_1mm) / (len(counts_1mm) - 1)
            if len(counts_1mm) > 1 else 0.0)
    one_mismatch = {
        "observed_nbre_1mm_count": obs_1mm,
        "n_shuffles": n,
        "null_mean": round(mean1, 4),
        "null_sd": round(math.sqrt(var1), 4),
        "n_shuffles_ge_observed": ge1,
        "empirical_p_one_sided": round((ge1 + 1) / (n + 1), 5),
        "_reading": ("the same null, for octamers matching the NBRE with AT MOST ONE substitution "
                     "— the class of site a 'predicted NBRE-like element' belongs to. ⛔ A "
                     "one-mismatch match is a WEAKER claim than an exact NBRE, not a stronger one: "
                     "it admits 24 sequences per position set, most of which no NR4A protein has "
                     "been shown to bind. This calibrates a count; it does not license calling any "
                     "hit a site."),
    }
    return {
        "one_mismatch": one_mismatch,
        "observed_nbre_count": obs,
        "n_shuffles": n,
        "null_mean": round(mean, 4),
        "null_sd": round(math.sqrt(var), 4),
        "n_shuffles_ge_observed": ge,
        # (ge + 1) / (n + 1) is the standard conservative empirical p; a bare ge/n can report 0,
        # which is a p-value no permutation test of n replicates is entitled to.
        "empirical_p_one_sided": round((ge + 1) / (n + 1), 5),
        "_reading": ("the probability of seeing at least this many NBRE octamers in a sequence "
                     "of identical length, base and DINUCLEOTIDE composition. It is a statement "
                     "about composition, not about binding."),
    }


# ---------------------------------------------------------------------------------------------
# Statistics — Welch, reused from the module that owns it rather than re-implemented.
# ---------------------------------------------------------------------------------------------
try:
    from fet_ddr_axis_scan import _welch  # noqa: E402
except Exception:  # noqa: BLE001  (numpy-less sandbox: that module imports pandas/numpy at top)
    def _welch(a, b):
        na, nb = len(a), len(b)
        if na < 2 or nb < 2:
            return None
        ma, mb = sum(a) / na, sum(b) / nb
        va = sum((x - ma) ** 2 for x in a) / (na - 1)
        vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
        if va == 0 and vb == 0:
            return None
        se = math.sqrt(va / na + vb / nb)
        if se == 0:
            return None
        t = (ma - mb) / se
        num = (va / na + vb / nb) ** 2
        den = (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
        return {"t": round(t, 3), "df": round(num / den, 1) if den else None,
                "mean_a": round(ma, 4), "mean_b": round(mb, 4),
                "delta_a_minus_b": round(ma - mb, 4)}


def _rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(a, b):
    if len(a) != len(b) or len(a) < 4:
        return None
    ra, rb = _rank(a), _rank(b)
    n = len(ra)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    if da == 0 or db == 0:
        return None
    return round(num / (da * db), 4)


def zscore_panel(values_by_gene, sample_index, panel):
    """Mean of per-gene z-scores across samples — the same within-dataset standardisation
    `emc_atr_vulnerability.derive_part_b` uses, so a panel score is dimensionless and comparable
    between panels measured on the same platform."""
    per_gene_z = []
    for g in panel:
        v = values_by_gene.get(g)
        if not v or len(v) != len(sample_index):
            continue
        m = sum(v) / len(v)
        sd = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) if len(v) > 1 else 0.0
        if sd == 0:
            continue
        per_gene_z.append([(x - m) / sd for x in v])
    if not per_gene_z:
        return None, []
    n = len(sample_index)
    score = [sum(row[i] for row in per_gene_z) / len(per_gene_z) for i in range(n)]
    used = [g for g in panel
            if g in values_by_gene and values_by_gene[g] and len(values_by_gene[g]) == n]
    return score, used


# ---------------------------------------------------------------------------------------------
# FETCH — CI only.  Every network call records what it asked and what came back.
# ---------------------------------------------------------------------------------------------
UA = {"User-Agent": "rare-cancers/1.0 (EMC RET target-gene scan)"}
ENSEMBL = "https://rest.ensembl.org"


def _get(url, timeout=120, tries=4, headers=None):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={**UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2 ** i)
    raise RuntimeError(f"{url[:110]}: {last}")


def background_symbols():
    """The background panel, read from the committed artifact named in BACKGROUND_SOURCE.

    Deterministic: sorted, then a fixed-seed sample. `--check` reproduces it exactly.
    """
    src = os.path.join(HERE, "emc-atr-vulnerability-inputs.json")
    if not os.path.exists(src):
        return [], {"_status": "absent", "path": src}
    with open(src, "r", encoding="utf-8") as fh:
        d = json.load(fh)
    vals = ((d.get("part_b") or {}).get("platforms") or {}) \
        .get("GSE24369_series_matrix.txt.gz", {}).get("geneset_gene_values") or {}
    syms = sorted(s for s in vals if re.match(r"^[A-Z][A-Z0-9-]{1,14}$", s))
    syms = [s for s in syms if s not in FOCUS_GENES]
    rng = random.Random(SHUFFLE_SEED)
    pick = sorted(rng.sample(syms, min(N_BACKGROUND, len(syms))))
    return pick, {"_status": "read", "source": BACKGROUND_SOURCE,
                  "n_available": len(syms), "n_sampled": len(pick), "seed": SHUFFLE_SEED}


def fetch_gene_window(symbol):
    """TSS-centred window for one gene, from Ensembl REST. Records the coordinates it used."""
    rec = {"symbol": symbol}
    try:
        raw = _get(f"{ENSEMBL}/lookup/symbol/homo_sapiens/{symbol}?content-type=application/json")
        g = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        rec["_status"] = "lookup_failed"
        rec["error"] = str(exc)[:200]
        return rec
    rec.update({"ensembl_id": g.get("id"), "assembly": g.get("assembly_name"),
                "chr": g.get("seq_region_name"), "gene_start": g.get("start"),
                "gene_end": g.get("end"), "strand": g.get("strand"),
                "biotype": g.get("biotype")})
    if not rec.get("chr"):
        rec["_status"] = "no_coordinates"
        return rec
    tss = g["start"] if g["strand"] == 1 else g["end"]
    if g["strand"] == 1:
        lo, hi = tss - WINDOW_UPSTREAM, tss + WINDOW_DOWNSTREAM
    else:
        lo, hi = tss - WINDOW_DOWNSTREAM, tss + WINDOW_UPSTREAM
    rec["tss"] = tss
    rec["window"] = [lo, hi]
    try:
        # strand=1 always: the window is reported on the FORWARD genomic strand and the scan reads
        # both strands, so a per-gene strand flip here would only make positions harder to check.
        url = (f"{ENSEMBL}/sequence/region/human/{rec['chr']}:{lo}..{hi}:1"
               "?content-type=text/x-fasta")
        fa = _get(url).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        rec["_status"] = "sequence_failed"
        rec["error"] = str(exc)[:200]
        return rec
    seq = "".join(ln.strip() for ln in fa.splitlines() if not ln.startswith(">"))
    rec["seq_len"] = len(seq)
    rec["gc"] = gc_fraction(seq)
    rec["sequence"] = seq.upper()
    rec["_status"] = "read"
    return rec


def _geo_matrix_urls(gse):
    n = re.sub(r"\D", "", gse)
    grp = f"GSE{n[:-3]}nnn" if len(n) > 3 else "GSEnnn"
    return f"https://ftp.ncbi.nlm.nih.gov/geo/series/{grp}/{gse}/matrix/"


def _parse_series_matrix(raw):
    text = gzip.decompress(raw).decode("utf-8", "replace")
    platform, samples, titles, chars = None, [], [], []
    probes, values, header = [], [], None
    in_tbl = False
    for ln in text.splitlines():
        if ln.startswith("!Series_platform_id"):
            platform = ln.split("\t")[-1].strip().strip('"')
        elif ln.startswith("!Sample_geo_accession"):
            samples = [x.strip().strip('"') for x in ln.split("\t")[1:]]
        elif ln.startswith("!Sample_title"):
            titles = [x.strip().strip('"') for x in ln.split("\t")[1:]]
        elif ln.startswith(("!Sample_source_name", "!Sample_characteristics")):
            chars.append([x.strip().strip('"') for x in ln.split("\t")[1:]])
        elif ln.startswith("!series_matrix_table_begin"):
            in_tbl = True
        elif ln.startswith("!series_matrix_table_end"):
            in_tbl = False
        elif in_tbl:
            parts = ln.split("\t")
            if header is None:
                header = [p.strip().strip('"') for p in parts]
                continue
            pid = parts[0].strip().strip('"')
            row = []
            for p in parts[1:]:
                p = p.strip().strip('"')
                try:
                    row.append(float(p))
                except ValueError:
                    row.append(None)
            probes.append(pid)
            values.append(row)
    ann = []
    for i in range(len(samples)):
        bits = [titles[i]] if i < len(titles) else []
        for c in chars:
            if i < len(c) and c[i]:
                bits.append(c[i])
        ann.append(" | ".join(bits))
    return {"platform": platform, "samples": samples, "annotations": ann,
            "probes": probes, "values": values}


def fetch_platform_annotation(platform_id, want_symbols, gene_coords):
    """probe -> symbol for the genes we want.

    TWO INDEPENDENT ROUTES, and they are cross-checked rather than tried in sequence:

      (a) the GEO-CURATED `.annot.gz`, which carries a real `Gene symbol` column;
      (b) for GPL6244 specifically, the platform's own `seqname` / `RANGE_START` / `RANGE_STOP`
          columns — a probe whose genomic range lies inside a gene's span IS that gene's probe.

    ⭐ (b) MATTERS AND IS NOT REDUNDANT. `emc_atr_vulnerability._gpl_symbols` records for GPL6244
    `symbol_column: null` and falls back to an EST accession bridge that costs a wall-clock budget
    and resolves a fraction of probes. For a handful of NAMED genes, coordinates answer the same
    question exactly, in one request, with no bridge. Where both routes fire they must agree; a
    disagreement is recorded, never silently resolved.
    """
    diag = {"platform": platform_id, "routes": {}}
    by_symbol, by_coord = {}, {}
    n = re.sub(r"\D", "", platform_id)
    grp = f"GPL{n[:-3]}nnn" if len(n) > 3 else "GPLnnn"
    # route (a)
    for url, gz in (
        (f"https://ftp.ncbi.nlm.nih.gov/geo/platforms/{grp}/{platform_id}/annot/"
         f"{platform_id}.annot.gz", True),
        (f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={platform_id}"
         "&targ=self&form=text&view=full", False),
    ):
        try:
            raw = _get(url, timeout=420, tries=1)
            text = (gzip.decompress(raw) if gz else raw).decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            diag["routes"].setdefault("annotation_files", []).append(
                {"url": url.rsplit("/", 1)[-1][:60], "error": str(exc)[:120]})
            continue
        header, sym_i, seq_i, s_i, e_i = None, None, None, None, None
        in_tbl = False
        for ln in text.splitlines():
            if ln.startswith("!platform_table_begin"):
                in_tbl = True
                continue
            if ln.startswith("!platform_table_end"):
                break
            if ln.startswith("#") and header is None:
                continue
            if not in_tbl and not ln.startswith("ID"):
                continue
            parts = ln.split("\t")
            if header is None:
                header = [p.strip() for p in parts]
                low = [h.lower() for h in header]
                for cand in ("gene symbol", "gene_symbol", "symbol"):
                    if cand in low:
                        sym_i = low.index(cand)
                        break
                for nm, tgt in (("seqname", "seq"), ("range_start", "s"), ("range_stop", "e")):
                    if nm in low:
                        if tgt == "seq":
                            seq_i = low.index(nm)
                        elif tgt == "s":
                            s_i = low.index(nm)
                        else:
                            e_i = low.index(nm)
                diag["routes"].setdefault("annotation_files", []).append(
                    {"url": url.rsplit("/", 1)[-1][:60], "header": header[:14],
                     "symbol_column": header[sym_i] if sym_i is not None else None,
                     "has_coordinates": None not in (seq_i, s_i, e_i)})
                continue
            pid = parts[0].strip()
            if sym_i is not None and len(parts) > sym_i:
                sym = parts[sym_i].strip().split("///")[0].split("//")[0].strip().upper()
                if sym in want_symbols:
                    by_symbol.setdefault(sym, []).append(pid)
            if None not in (seq_i, s_i, e_i) and len(parts) > max(seq_i, s_i, e_i):
                chrom = parts[seq_i].strip().replace("chr", "")
                try:
                    ps, pe = int(parts[s_i]), int(parts[e_i])
                except ValueError:
                    continue
                for sym, gc in gene_coords.items():
                    if gc.get("chr") != chrom:
                        continue
                    if ps >= gc["gene_start"] and pe <= gc["gene_end"]:
                        by_coord.setdefault(sym, []).append(pid)
        if by_symbol or by_coord:
            diag["source_used"] = url.rsplit("/", 1)[-1][:60]
            break
    diag["n_by_symbol"] = {k: len(v) for k, v in by_symbol.items()}
    diag["n_by_coordinate"] = {k: len(v) for k, v in by_coord.items()}
    both = set(by_symbol) & set(by_coord)
    diag["agreement"] = {s: sorted(set(by_symbol[s])) == sorted(set(by_coord[s])) for s in both}
    merged = {}
    for src in (by_symbol, by_coord):
        for s, ps in src.items():
            merged.setdefault(s, [])
            merged[s] += [p for p in ps if p not in merged[s]]
    return merged, diag


def fetch_series(gse, platform_hint, want_symbols, gene_coords):
    rec = {"gse": gse, "platform_wanted": platform_hint}
    base = _geo_matrix_urls(gse)
    try:
        listing = _get(base, timeout=120).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        rec["_status"] = "matrix_dir_unreachable"
        rec["error"] = str(exc)[:200]
        return rec
    files = sorted(set(re.findall(r'href="([^"]+_series_matrix\.txt\.gz)"', listing)))
    rec["matrix_files_found"] = files
    keep = [f for f in files if platform_hint in f] or files
    rec["matrix_files_read"] = keep
    rec["platforms"] = {}
    for f in keep:
        try:
            raw = _get(base + f, timeout=900)
        except Exception as exc:  # noqa: BLE001
            rec["platforms"][f] = {"_status": "fetch_failed", "error": str(exc)[:200]}
            continue
        m = _parse_series_matrix(raw)
        probe_map, diag = fetch_platform_annotation(m["platform"], want_symbols, gene_coords)
        idx = {p: i for i, p in enumerate(m["probes"])}
        gene_values = {}
        for sym, probes in probe_map.items():
            rows = [m["values"][idx[p]] for p in probes if p in idx]
            rows = [r for r in rows if r and all(x is not None for x in r)]
            if not rows:
                continue
            # probe-level mean, so a gene with several probes is one series, not several
            gene_values[sym] = [round(sum(r[i] for r in rows) / len(rows), 4)
                                for i in range(len(m["samples"]))]
        neg = sum(1 for row in m["values"][:4000] for x in row if x is not None and x < 0)
        tot = sum(1 for row in m["values"][:4000] for x in row if x is not None) or 1
        rec["platforms"][f] = {
            "_status": "read",
            "platform": m["platform"],
            "n_samples": len(m["samples"]),
            "n_probes": len(m["probes"]),
            "samples": [{"gsm": g, "annotation_verbatim": a}
                        for g, a in zip(m["samples"], m["annotations"])],
            "frac_negative_values": round(neg / tot, 3),
            "value_kind": ("two-colour log-ratio vs a reference pool (RELATIVE)"
                           if neg / tot > 0.2 else "single-channel intensity"),
            "probe_annotation_diagnostic": diag,
            "gene_values": gene_values,
            "n_genes_measured": len(gene_values),
        }
    rec["_status"] = "read"
    return rec


def collect(argv_focus=None):
    """Everything that needs the network. CI only."""
    inputs = {
        "_framing": FRAMING,
        "_generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_egress_note": ("The dev sandbox proxy answers 403 to CONNECT for rest.ensembl.org, "
                         "ftp.ncbi.nlm.nih.gov, www.ncbi.nlm.nih.gov and www.ebi.ac.uk — read "
                         "from the proxy's own recentRelayFailures on 2026-08-07, not assumed. "
                         "This function therefore runs on a GitHub Actions runner (CLAUDE.md §6)."),
    }
    bg, bg_diag = background_symbols()
    inputs["background_panel"] = {"symbols": bg, "diagnostic": bg_diag}

    seqs = {}
    for sym in list(FOCUS_GENES) + bg:
        seqs[sym] = fetch_gene_window(sym)
        time.sleep(0.08)          # Ensembl asks for <= 15 req/s; this is well under
    inputs["gene_windows"] = seqs

    coords = {s: r for s, r in seqs.items()
              if r.get("_status") == "read" and s in FOCUS_GENES}
    want = set(FOCUS_GENES) | set(STROMAL_PANEL) | set(VASCULAR_PANEL) | set(IMMUNE_PANEL) \
        | set(TUMOUR_PANEL) | set(PROLIF_PANEL) | set(RET_PARTNERS)
    inputs["expression_panel_requested"] = sorted(want)
    inputs["series"] = {}
    for gse, meta in SERIES.items():
        inputs["series"][gse] = fetch_series(gse, meta["platform"], want, coords)
        inputs["series"][gse]["_why_this_series"] = meta["why"]
    return inputs


# ---------------------------------------------------------------------------------------------
# DERIVE — offline, from the inputs cache.  Every verdict names the evidence that produced it.
# ---------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------
# Sample classification.
#
# ⛔ THIS WAS RE-IMPLEMENTED HERE ONCE AND IT WAS WRONG IN TWO WAYS AT ONCE (found 2026-08-07 by
# running it over the committed GSE4303/GPL3290 annotations before trusting it):
#
#   1. It required the phrase "EXTRASKELETAL myxoid chondrosarcoma". GSE4303 — the original EMC
#      series — titles its samples `STT3697-Myxoid Chondrosarcoma`, with no "extraskeletal". So
#      TEN OF SIXTEEN EMC SAMPLES classified as comparators, which would have produced a contrast
#      of EMC-vs-EMC and reported it as `n_EMC = 0, underpowered` — an instrument failure wearing
#      the costume of a data limitation.
#   2. It ended with `if low.strip(): return "comparator_sarcoma"`, so ANY unrecognised non-empty
#      annotation silently became a comparator. GSE24369's two `Skeletal muscle` samples are
#      NORMAL TISSUE and were being fed into the comparator arm of a tumour contrast.
#
# Both are the same root cause: a second copy of a classification this repository already owns.
# The patterns now come from `emc_atr_vulnerability`, which measured them against these very
# series — one fact, one home (CLAUDE.md rule 1).
#
# ⚠ AND THEY ARE READ WITHOUT IMPORTING THAT MODULE, deliberately: it pulls in pandas/numpy at
# import time and the dev sandbox has neither, so a plain import would fail HERE and pass in CI —
# the worst possible split. `ast.literal_eval` over its source gets the same literals with no
# execution, and RAISES if either name moves, so the coupling is loud rather than silent.
# ---------------------------------------------------------------------------------------------
def _owner_patterns():
    import ast
    src_path = os.path.join(HERE, "emc_atr_vulnerability.py")
    with open(src_path, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    got = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id in ("EMC_SAMPLE_PATTERNS", "COMPARATOR_BUCKETS"):
            got[node.targets[0].id] = ast.literal_eval(node.value)
    missing = {"EMC_SAMPLE_PATTERNS", "COMPARATOR_BUCKETS"} - set(got)
    if missing:
        raise RuntimeError(
            f"{os.path.basename(src_path)} no longer defines {sorted(missing)} as a module-level "
            "literal. This module reads them from there on purpose (one fact, one home); fix the "
            "reader rather than re-copying the patterns.")
    return got["EMC_SAMPLE_PATTERNS"], got["COMPARATOR_BUCKETS"]


EMC_SAMPLE_PATTERNS, COMPARATOR_BUCKETS = _owner_patterns()


def _classify(annotation):
    """Bucket a sample from its VERBATIM GEO annotation, using the owner module's patterns.

    Order matters and is the owner's: the two full EMC phrases are tested FIRST, so
    "low-grade fibromyxoid sarcoma" cannot be captured by a looser later rule; then the named
    comparator buckets; then the bare EMC/EXMC token, with `_`-and-digit boundaries because
    `\\b` does not sit between `5` and `E` in `STT5525_EMC`.
    """
    low = (annotation or "").lower()
    if any(p in low for p in EMC_SAMPLE_PATTERNS[:2]):
        return "EMC"
    for bucket, pats in COMPARATOR_BUCKETS.items():
        if any(p in low for p in pats):
            return "normal_or_reference" if bucket == "normal_or_reference" \
                else "comparator_sarcoma"
    if re.search(r"(?<![a-z])(emc|exmc)(?![a-z])", low):
        return "EMC"
    # ⛔ NEVER a catch-all comparator. An annotation this list does not recognise is an ABSENT
    # READING about that sample, not evidence that it is a comparator tumour.
    return "unclassified"


def derive_part1(inputs):
    d = {"_question": "Does RET's TSS-centred regulatory window carry NBRE/NurRE elements at a "
                      "rate a composition-matched null does not already explain?",
         # ⛔ `source` CARRIES THE `PMID <digits>` FORM ON PURPOSE, beside the bare `source_pmid`.
         # lint_citations matches `\bPMID[:\s]*(\d{6,9})\b`, and a JSON value of "1902986" under a
         # key named source_pmid does NOT match it — the quote characters sit between the word and
         # the digits. So an identifier this artifact genuinely sources read as prose-only and
         # unanchored the moment a manuscript cited it, which is the opposite of what the gate is
         # for: it would push an author to DROP a correctly-sourced citation to get a green build.
         "_motifs": {"NBRE": {"consensus": NBRE, "source_pmid": NBRE_PMID,
                              "source": f"PMID {NBRE_PMID}"},
                     "NurRE": {"consensus": f"{NURRE_LEFT}(N{NURRE_SPACER}){NURRE_RIGHT}",
                               "source_pmid": NURRE_PMID,
                               "source": f"PMID {NURRE_PMID}",
                               "caveat": "NR4A3 homodimerises on NurRE more weakly than "
                                         "NR4A1/NR4A2 — nr4a3-emc-biology-evidence.md"}},
         "_window": {"upstream_of_tss": WINDOW_UPSTREAM, "downstream_of_tss": WINDOW_DOWNSTREAM,
                     "_frozen_before_any_result": True,
                     "_why_asymmetric": ("RET's only experimentally validated distal element sits "
                                         "at ~+9.7 kb in the first intron (HOXB5, PMID 24794774), "
                                         "so a symmetric 5 kb window would have excluded it. "
                                         "Widened BEFORE any RET sequence was read — on published "
                                         "architecture, not on a count this module produced."),
                     "known_elements": KNOWN_RET_REGULATORY_ELEMENTS,
                     "⚠_still_bounded": ("a window is a scope choice and a distal enhancer outside "
                                         "it remains untested by construction. A null result here "
                                         "is a null WITHIN THIS WINDOW and must be quoted that "
                                         "way.")}}
    wins = inputs.get("gene_windows") or {}
    read = {s: r for s, r in wins.items() if r.get("_status") == "read" and r.get("sequence")}
    d["n_windows_requested"] = len(wins)
    d["n_windows_read"] = len(read)
    if not read:
        d["_status"] = "NOT_RUN"
        d["why"] = ("no regulatory sequence is present in the inputs cache. ⚠ ABSENT READING — "
                    "this says nothing about whether RET carries an NBRE. The fetch half needs "
                    "egress the dev sandbox does not have (see inputs._egress_note).")
        d["verdict"] = None
        return d
    focus = {}
    for sym in FOCUS_GENES:
        r = read.get(sym)
        if not r:
            focus[sym] = {"_status": (wins.get(sym) or {}).get("_status", "absent")}
            continue
        seq = r["sequence"]
        nb = scan_nbre(seq)
        nb1 = scan_nbre(seq, max_mismatch=1)
        nr = scan_nurre(seq)
        focus[sym] = {
            "why_this_gene": FOCUS_GENES[sym],
            "ensembl_id": r.get("ensembl_id"), "assembly": r.get("assembly"),
            "chr": r.get("chr"), "tss": r.get("tss"), "window": r.get("window"),
            "gc": r.get("gc"), "seq_len": r.get("seq_len"),
            "nbre_exact": {"n": len(nb),
                           "hits": [{**h, "offset_from_tss": _off(h["pos"], r)} for h in nb]},
            "nbre_1mm": {"n": len(nb1)},
            "nurre": {"n": len(nr),
                      "hits": [{**h, "offset_from_tss": _off(h["pos"], r)} for h in nr]},
            "shuffle_null": shuffle_null(seq, N_SHUFFLES, SHUFFLE_SEED),
        }
    d["focus_genes"] = focus
    bg_counts = []
    for sym, r in read.items():
        if sym in FOCUS_GENES:
            continue
        bg_counts.append({"symbol": sym, "gc": r.get("gc"),
                          "nbre_exact": len(scan_nbre(r["sequence"])),
                          # the one-mismatch count for the same window, so a focus gene's 1mm count
                          # can be ranked against real gene windows and not only against its own
                          # shuffles. One extra scan per background window; no extra fetch.
                          "nbre_1mm": len(scan_nbre(r["sequence"], max_mismatch=1))})
    d["background_panel"] = {
        "n": len(bg_counts),
        "source": BACKGROUND_SOURCE,
        "_why_this_panel": ("assembled for an unrelated question (the ATR/DDR concept universe), "
                            "so it cannot have been chosen to flatter or damage RET"),
        "mean_nbre_per_window": (round(sum(b["nbre_exact"] for b in bg_counts) / len(bg_counts), 4)
                                 if bg_counts else None),
        "counts": bg_counts,
    }
    ret = focus.get("RET") or {}
    if bg_counts and ret.get("nbre_exact"):
        obs = ret["nbre_exact"]["n"]
        ge = sum(1 for b in bg_counts if b["nbre_exact"] >= obs)
        d["ret_rank_in_background"] = {
            "observed": obs,
            "n_background_windows_with_at_least_as_many": ge,
            "n_background": len(bg_counts),
            "empirical_p_vs_panel": round((ge + 1) / (len(bg_counts) + 1), 4),
        }
        # GC-matched subset: +/- 0.05 around RET's window GC.
        gc = ret.get("gc")
        if gc is not None:
            sub = [b for b in bg_counts if b["gc"] is not None and abs(b["gc"] - gc) <= 0.05]
            ge2 = sum(1 for b in sub if b["nbre_exact"] >= obs)
            d["ret_rank_in_gc_matched_background"] = {
                "gc_window": [round(gc - 0.05, 4), round(gc + 0.05, 4)],
                "n_matched": len(sub),
                "n_at_least_as_many": ge2,
                "empirical_p": round((ge2 + 1) / (len(sub) + 1), 4) if sub else None,
            }
    # ⭐ THE SAME TWO RANKS FOR EVERY FOCUS GENE, NOT ONLY RET (added 2026-08-07).
    # The two blocks above answer "where does RET sit against the panel", because RET is this
    # module's subject. But the panel is read once and costs nothing more to reuse, and a second
    # lane now needs it: `nr4a3-fusion-transcriptional-output.md` §4.2 item 4 asks for exactly this
    # scan over the class-A direct targets (ENO3, PPARG, SEMA3C) against a matched background.
    # ⛔ The RET-specific keys above are LEFT EXACTLY AS THEY WERE — a reader or checker that
    # already reads `ret_rank_in_background` is unaffected, and the RET verdict is still computed
    # from them. This block only ADDS the same arithmetic for the other focus genes.
    ranks = {}
    for sym, rec in focus.items():
        nb = rec.get("nbre_exact")
        if not bg_counts or not nb:
            continue
        obs = nb["n"]
        ge = sum(1 for b in bg_counts if b["nbre_exact"] >= obs)
        row = {"observed_nbre_count": obs,
               "n_background_windows_with_at_least_as_many": ge,
               "n_background": len(bg_counts),
               "empirical_p_vs_panel": round((ge + 1) / (len(bg_counts) + 1), 4)}
        gc = rec.get("gc")
        sub = None
        if gc is not None:
            sub = [b for b in bg_counts if b["gc"] is not None and abs(b["gc"] - gc) <= 0.05]
            ge2 = sum(1 for b in sub if b["nbre_exact"] >= obs)
            row["gc_matched"] = {
                "gc_window": [round(gc - 0.05, 4), round(gc + 0.05, 4)],
                "n_matched": len(sub),
                "n_at_least_as_many": ge2,
                "empirical_p": round((ge2 + 1) / (len(sub) + 1), 4) if sub else None,
            }
        # The same two ranks for the ONE-MISMATCH count, which is the class of site a "predicted
        # NBRE-like element" belongs to and the only quantity on which SEMA3C is not simply zero.
        nb1 = rec.get("nbre_1mm")
        if nb1 and nb1.get("n") is not None and all(b.get("nbre_1mm") is not None
                                                    for b in bg_counts):
            o1 = nb1["n"]
            g1 = sum(1 for b in bg_counts if b["nbre_1mm"] >= o1)
            row["one_mismatch"] = {
                "observed_nbre_1mm_count": o1,
                "n_background_windows_with_at_least_as_many": g1,
                "n_background": len(bg_counts),
                "empirical_p_vs_panel": round((g1 + 1) / (len(bg_counts) + 1), 4),
            }
            if sub:
                g1g = sum(1 for b in sub if b["nbre_1mm"] >= o1)
                row["one_mismatch"]["gc_matched"] = {
                    "n_matched": len(sub),
                    "n_at_least_as_many": g1g,
                    "empirical_p": round((g1g + 1) / (len(sub) + 1), 4),
                }
        ranks[sym] = row
    d["focus_gene_ranks_in_background"] = {
        "_what": "for EVERY focus gene, the rank of its exact-NBRE count against the same 198-window "
                 "background panel, raw and GC-matched (+/-0.05). Same arithmetic as the two "
                 "RET-specific blocks above, which are retained unchanged.",
        "_reading": "a HIGH empirical p means the window carries no more NBREs than an arbitrary "
                    "gene window of similar composition. ⛔ Neither an enrichment nor its absence "
                    "is evidence about OCCUPANCY: only a chromatin experiment establishes binding.",
        "ranks": ranks,
    }

    d["_status"] = "derived"
    ret_null = (ret.get("shuffle_null") or {})
    d["verdict"] = _part1_verdict(ret, ret_null, d.get("ret_rank_in_background"))
    return d


def _off(pos, rec):
    win = rec.get("window") or [None, None]
    tss = rec.get("tss")
    if win[0] is None or tss is None:
        return None
    return (win[0] + pos) - tss


def _part1_verdict(ret, null, rank):
    if not ret or not ret.get("nbre_exact"):
        return None
    n = ret["nbre_exact"]["n"]
    p_shuf = null.get("empirical_p_one_sided")
    p_rank = (rank or {}).get("empirical_p_vs_panel")
    if n == 0 and (ret.get("nurre") or {}).get("n", 0) == 0:
        return {"call": "NO_ELEMENT_IN_WINDOW",
                "reading": (f"neither an exact NBRE nor a NurRE occurs in the frozen "
                            f"-{WINDOW_UPSTREAM}/+{WINDOW_DOWNSTREAM} bp window around RET's TSS "
                            "(which contains the HOXB5 MCS+9.7 element, PMID 24794774). "
                            "This satisfies the FIRST clause of the memo's falsifier. It does NOT "
                            "close the lane on its own: the second clause (phosphorylation "
                            "tracking stroma) is a separate measurement, and a distal enhancer "
                            "outside this window is untested by construction.")}
    if p_shuf is not None and p_shuf <= 0.05 and (p_rank is None or p_rank <= 0.10):
        return {"call": "ELEMENT_PRESENT_ABOVE_COMPOSITION_NULL",
                "reading": ("RET's window carries more NBRE octamers than a dinucleotide-matched "
                            "shuffle explains. ⚠ This is a PLAUSIBILITY FILTER. It is not evidence "
                            "that the fusion occupies the site, and no occupancy claim may be made "
                            "from it.")}
    return {"call": "ELEMENT_PRESENT_BUT_NOT_ABOVE_CHANCE",
            "reading": (f"{n} exact NBRE match(es) in the window, which a composition-matched null "
                        "already explains (empirical p = "
                        f"{p_shuf}). An 8-mer at chance frequency is not a target-gene argument.")}


def derive_part2(inputs):
    d = {"_question": "Is RET differentially expressed in EMC tumours versus other sarcomas, and "
                      "does it covary with stromal or with tumour-cell content?",
         "_what_this_is_not": ("mRNA. The memo's falsifier is about PHOSPHORYLATION, which no "
                               "expression series can measure. A covariation result here bounds "
                               "the falsifier; it cannot discharge it.")}
    series = inputs.get("series") or {}
    if not series or all(s.get("_status") != "read" for s in series.values()):
        d["_status"] = "NOT_RUN"
        d["why"] = ("no series matrix is present in the inputs cache. ⚠ ABSENT READING — it says "
                    "nothing about RET's expression in EMC. Needs the CI fetch.")
        d["verdict"] = None
        return d
    d["series"] = {}
    for gse, rec in series.items():
        if rec.get("_status") != "read":
            d["series"][gse] = {"_status": rec.get("_status"), "error": rec.get("error")}
            continue
        for fname, p in (rec.get("platforms") or {}).items():
            if p.get("_status") != "read":
                continue
            samples = p["samples"]
            classes = [_classify(s["annotation_verbatim"]) for s in samples]
            gv = p.get("gene_values") or {}
            emc = [i for i, c in enumerate(classes) if c == "EMC"]
            comp = [i for i, c in enumerate(classes) if c == "comparator_sarcoma"]
            row = {"platform": p.get("platform"),
                   "value_kind": p.get("value_kind"),
                   "n_samples": len(samples),
                   "class_counts": {c: classes.count(c) for c in sorted(set(classes))},
                   "genes_measured": sorted(gv),
                   "sample_annotations_verbatim": [
                       {"gsm": s["gsm"], "class": c, "annotation": s["annotation_verbatim"]}
                       for s, c in zip(samples, classes)],
                   }
            if len(emc) >= 3 and len(comp) >= 3:
                row["contrasts"] = {}
                for g in sorted(set(RET_PARTNERS + TUMOUR_PANEL + PROLIF_PANEL) & set(gv)):
                    a = [gv[g][i] for i in emc]
                    b = [gv[g][i] for i in comp]
                    row["contrasts"][g] = _welch(a, b)
            else:
                row["contrasts"] = {"_status": f"underpowered: EMC={len(emc)} comp={len(comp)}"}
            # --- the falsifier's second clause, in the only currency this data has -------------
            strom, s_used = zscore_panel(gv, samples, STROMAL_PANEL)
            tum, t_used = zscore_panel(gv, samples, TUMOUR_PANEL)
            vasc, v_used = zscore_panel(gv, samples, VASCULAR_PANEL)
            row["panels_used"] = {"stromal": s_used, "tumour": t_used, "vascular": v_used}
            if "RET" in gv and strom and tum:
                allidx = list(range(len(samples)))
                row["ret_covariation"] = {
                    "_reading": ("Spearman rho of RET against a stromal/ECM panel score and "
                                 "against an EMC tumour-cell panel score. If RET tracked STROMA "
                                 "rather than tumour, rho_stromal would exceed rho_tumour — that "
                                 "is the expression-level shadow of the memo's falsifier."),
                    "all_samples": {
                        "rho_vs_stromal": spearman([gv["RET"][i] for i in allidx],
                                                   [strom[i] for i in allidx]),
                        "rho_vs_tumour": spearman([gv["RET"][i] for i in allidx],
                                                  [tum[i] for i in allidx]),
                        "rho_vs_vascular": (spearman([gv["RET"][i] for i in allidx],
                                                     [vasc[i] for i in allidx])
                                            if vasc else None),
                        "n": len(allidx)},
                    "within_EMC": ({"rho_vs_stromal": spearman([gv["RET"][i] for i in emc],
                                                               [strom[i] for i in emc]),
                                    "rho_vs_tumour": spearman([gv["RET"][i] for i in emc],
                                                              [tum[i] for i in emc]),
                                    "n": len(emc)}
                                   if len(emc) >= 4 else
                                   {"_status": f"underpowered: n_EMC={len(emc)}"}),
                }
            d["series"].setdefault(gse, {})[fname] = row
    d["_status"] = "derived"
    d["verdict"] = _part2_verdict(d)
    return d


def _part2_verdict(d):
    best = None
    for gse, plats in (d.get("series") or {}).items():
        if not isinstance(plats, dict):
            continue
        for fname, row in plats.items():
            if not isinstance(row, dict):
                continue
            c = (row.get("contrasts") or {}).get("RET")
            if isinstance(c, dict) and c.get("t") is not None:
                if best is None or abs(c["t"]) > abs(best[2]["t"]):
                    best = (gse, fname, c, row)
    if best is None:
        return {"call": "RET_NOT_MEASURED",
                "reading": ("RET has no usable probe/contrast on any readable platform. ⚠ ABSENT "
                            "READING — not a reading of absence.")}
    gse, fname, c, row = best
    cov = (row.get("ret_covariation") or {}).get("all_samples") or {}
    rs, rt = cov.get("rho_vs_stromal"), cov.get("rho_vs_tumour")
    stroma_flag = (rs is not None and rt is not None and rs > rt + 0.2)
    return {"call": ("RET_HIGHER_IN_EMC" if c["t"] > 2 else
                     "RET_LOWER_IN_EMC" if c["t"] < -2 else "RET_NOT_DIFFERENTIAL"),
            "series": gse, "platform_file": fname, "welch": c,
            "covariation_favours_stroma": stroma_flag,
            "reading": ("Welch t of RET, EMC vs comparator sarcoma, on the platform with the "
                        "largest |t|. ⚠ mRNA, small n, no multiple-testing correction, and the "
                        "tumour is stroma-rich so a bulk value mixes compartments. "
                        + ("The stromal panel tracks RET MORE closely than the tumour panel — "
                           "that is the direction the memo's falsifier predicts."
                           if stroma_flag else
                           "The stromal panel does NOT track RET more closely than the tumour "
                           "panel, so this reading does not support the falsifier's second "
                           "clause."))}


def derive(inputs, literature=None):
    res = {
        "_what": ("Is RET a target GENE of EWSR1::NR4A3, and does RET in EMC clear the "
                  "measured-activation bar MET in clear cell sarcoma failed?"),
        "_framing": FRAMING,
        "_lane": "emc-unexplored-treatment-lanes.md §3.1 (ranked #1 of twelve)",
        "_generated_from": os.path.basename(INPUTS),
        "part_1_nbre_scan": derive_part1(inputs),
        "part_2_expression": derive_part2(inputs),
    }
    if literature is not None:
        res["part_3_activation_bar"] = literature
    res["_what_this_cannot_conclude"] = [
        "That the fusion OCCUPIES any site found here. A motif is a sequence; occupancy is a ChIP "
        "experiment. No enrichment result licenses the word 'target'.",
        "That RET is phosphorylated in EMC tumours. No expression series measures phosphorylation, "
        "and the memo's falsifier is stated in phospho terms.",
        "Anything about selectivity, efficacy, safety, a therapeutic window or clinical readiness "
        "of any RET inhibitor in EMC. No EMC patient has received a selective RET inhibitor.",
        "That a negative NBRE result closes the lane: only the FIRST of the falsifier's two "
        "clauses is addressable here, and they are joined by AND.",
    ]
    return res


# ---------------------------------------------------------------------------------------------
# Self-test — offline, and it exercises the parts that produce numbers.
# ---------------------------------------------------------------------------------------------
def selftest():
    bad = []
    # 1. the scanner finds a planted NBRE, on both strands, at the right offset
    rng = random.Random(1)
    filler = "".join(rng.choice("ACGT") for _ in range(500))
    seq = filler[:200] + NBRE + filler[200:400] + revcomp(NBRE) + filler[400:]
    hits = scan_nbre(seq)
    pos = sorted(h["pos"] for h in hits)
    if 200 not in pos:
        bad.append(f"forward NBRE not found at 200: {pos}")
    if (200 + len(NBRE) + 200) not in pos:
        bad.append(f"reverse NBRE not found at {200 + len(NBRE) + 200}: {pos}")
    if not any(h["strand"] == "-" for h in hits):
        bad.append("no minus-strand hit reported for a planted reverse-complement NBRE")

    # 2. one-mismatch is a superset of exact
    if len(scan_nbre(seq, 1)) < len(scan_nbre(seq, 0)):
        bad.append("1-mismatch scan returned fewer hits than the exact scan")

    # 3. NurRE with the nominal spacer is found; a 20-bp spacer is not
    good = "TT" + NURRE_LEFT + "ACGTAC" + NURRE_RIGHT + "TT"
    if len(scan_nurre(good)) < 1:
        bad.append("NurRE with the nominal 6-bp spacer was not found")
    far = "TT" + NURRE_LEFT + ("A" * 20) + NURRE_RIGHT + "TT"
    if scan_nurre(far):
        bad.append("NurRE matched across a 20-bp spacer, which the consensus does not allow")

    # 4. the dinucleotide shuffle preserves length, mononucleotide AND dinucleotide counts
    src = "".join(rng.choice("ACGT") for _ in range(3000))
    sh = dinucleotide_shuffle(src, random.Random(7))
    if len(sh) != len(src):
        bad.append("shuffle changed the sequence length")
    for b in "ACGT":
        if sh.count(b) != src.count(b):
            bad.append(f"shuffle changed the count of {b}")
    def dinuc(s):
        d = {}
        for a, b in zip(s, s[1:]):
            d[a + b] = d.get(a + b, 0) + 1
        return d
    if dinuc(sh) != dinuc(src):
        bad.append("shuffle did not preserve dinucleotide composition")
    if sh == src:
        bad.append("shuffle returned the input unchanged")

    # 5. the null actually detects a planted enrichment, and does NOT fire on plain sequence
    plain = "".join(rng.choice("ACGT") for _ in range(4000))
    n_plain = shuffle_null(plain, 200, 3)
    if n_plain["empirical_p_one_sided"] < 0.05:
        bad.append(f"null fired on unenriched sequence: p={n_plain['empirical_p_one_sided']}")
    loaded = plain
    for k in range(6):
        at = 300 * (k + 1)
        loaded = loaded[:at] + NBRE + loaded[at + len(NBRE):]
    n_load = shuffle_null(loaded, 200, 3)
    if n_load["empirical_p_one_sided"] > 0.05:
        bad.append(f"null failed to detect 6 planted NBREs: p={n_load['empirical_p_one_sided']}")

    # 6. spearman sanity
    if spearman([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]) != 1.0:
        bad.append("spearman of a monotone pair is not 1.0")
    if spearman([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) != -1.0:
        bad.append("spearman of a reversed pair is not -1.0")

    # 7. sample classification
    if _classify("Extraskeletal myxoid chondrosarcoma 1 | soft tissue") != "EMC":
        bad.append("EMC sample annotation did not classify as EMC")
    if _classify("Desmoid fibromatosis 1 | soft tissue") != "comparator_sarcoma":
        bad.append("a comparator annotation classified as something else")

    # 8. an empty inputs cache must derive to NOT_RUN, never to a biological verdict
    empty = derive({})
    if empty["part_1_nbre_scan"]["_status"] != "NOT_RUN":
        bad.append("part 1 on an empty cache did not report NOT_RUN")
    if empty["part_1_nbre_scan"]["verdict"] is not None:
        bad.append("part 1 emitted a verdict with no sequence read")
    if empty["part_2_expression"]["verdict"] is not None:
        bad.append("part 2 emitted a verdict with no series read")

    for b in bad:
        print("FAIL:", b)
    print(f"[selftest] {'OK' if not bad else str(len(bad)) + ' FAILURE(S)'}")
    return 1 if bad else 0


# ---------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fetch", action="store_true", help="CI only: Ensembl + GEO retrieval")
    ap.add_argument("--check", action="store_true", help="re-derive and diff the committed file")
    ap.add_argument("--selftest", action="store_true", help="offline engine test")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.fetch:
        inputs = collect()
        with open(INPUTS, "w", encoding="utf-8") as fh:
            json.dump(inputs, fh, indent=1, sort_keys=False)
        print(f"[fetch] wrote {INPUTS}")
    else:
        inputs = {}
        if os.path.exists(INPUTS):
            with open(INPUTS, "r", encoding="utf-8") as fh:
                inputs = json.load(fh)

    lit = None
    litpath = os.path.join(HERE, "emc-ret-activation-bar.json")
    if os.path.exists(litpath):
        with open(litpath, "r", encoding="utf-8") as fh:
            lit = json.load(fh)

    res = derive(inputs, lit)

    if args.check:
        if not os.path.exists(OUT):
            print(f"[check] {OUT} is absent")
            return 1
        with open(OUT, "r", encoding="utf-8") as fh:
            old = json.load(fh)
        a = json.dumps({k: v for k, v in old.items() if not k.startswith("_generated")},
                       sort_keys=True)
        b = json.dumps({k: v for k, v in res.items() if not k.startswith("_generated")},
                       sort_keys=True)
        if a == b:
            print("[check] OK — the committed artifact re-derives exactly from its inputs")
            return 0
        print("[check] DRIFT — the committed artifact does not re-derive from its inputs")
        return 1

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(f"[derive] wrote {OUT}")
    print("part 1:", res["part_1_nbre_scan"].get("_status"),
          res["part_1_nbre_scan"].get("verdict"))
    print("part 2:", res["part_2_expression"].get("_status"),
          res["part_2_expression"].get("verdict"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
