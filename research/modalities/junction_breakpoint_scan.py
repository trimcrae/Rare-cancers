#!/usr/bin/env python3
"""
Breakpoint-sensitivity scan for EWSR1::NR4A3 junction-targeting oligos (ASO + siRNA).

WHY. The off-target screen on the CANONICAL modelled breakpoint (EWSR1 kept to codon 264 ::
NR4A3 resumed from codon 2) flagged that *that particular* junction is GC-rich, low-complexity,
and off-target-prone — a bad neighbourhood for a gapmer/siRNA. But the canonical breakpoint is
only ONE of many in-frame EWSR1::NR4A3 fusions seen clinically (the companion exon work found
EWSR1 exons 7/9/10/11/12/13 -> predominantly NR4A3 exon 3). The question this script answers:
across the REAL set of plausible in-frame breakpoints, are SOME breakpoints far more favorable
(lower GC, lower complexity, more specific) for an ASO/siRNA than the canonical one? If so, this
directly informs breakpoint/patient selection — design against the favorable seams, not the
canonical guess.

HOW (all real; sequences fetched from NCBI via junction_aso.fetch_cds; nothing invented).
  ROBUST APPROACH — we deliberately do NOT depend on a fragile exon->CDS coordinate mapping.
  Instead we SWEEP the breakpoint directly in CDS-codon space:
    - EWSR1 kept-length (ja.EWSR1_KEEP_AA) over a plausible in-frame range covering EWSR1
      exons ~6-14 (codons ~200-300), and
    - NR4A3 retained start (ja.NR4A3_KEEP_AA_FROM) over its plausible small range (codons 2-30).
  For EACH (left_len, right_start) breakpoint we rebuild the fusion CDS (ja.build_fusion_cds
  after setting the two module globals) and, around the seam, compute:
    - junction-window GC (+/-10 nt),
    - best (min) gapmer GC by re-running ja.design,
    - best (min) siRNA GC by re-running junction_sirna.design,
    - a LOW-COMPLEXITY flag: Shannon entropy of the +/-12 nt junction window plus presence of a
      >=4 mono/di-nucleotide repeat, and
    - n_fusion_specific (gapmers whose target window is absent from both parent CDSs).
  A breakpoint is called FAVORABLE if a gapmer OR siRNA exists with GC in 40-60% AND the junction
  window entropy is above a threshold AND a fusion-specific design exists.

HONEST SCOPE. Breakpoints here are MODELLED positions (a sensitivity sweep in codon space), NOT
exon-exact: real clinical design needs the patient's actually-sequenced breakpoint. The
"specificity" used here is a GC/complexity/parent-substring triage, NOT the full BLAST
transcriptome off-target screen. This is a TRIAGE tool to rank seams, not a validated drug.

Output: junction-breakpoint-scan.json
"""

import json
import math
import os
import re
import sys

import junction_aso as ja
import junction_sirna as js

OUT = os.path.join(os.path.dirname(__file__), "junction-breakpoint-scan.json")

# --- breakpoint sweep ranges (codon / amino-acid space) ---------------------------------
# EWSR1 kept-length: codons ~200-300 cover EWSR1 exons ~6-14 (the FET-fusion breakpoint window).
EWSR1_KEEP_RANGE = range(200, 301, 4)      # 200,204,...,300  (26 values)
# NR4A3 retained start: small range, exons 2-4 resume early in the NR4A3 CDS.
NR4A3_FROM_RANGE = range(2, 31, 2)         # 2,4,...,30        (15 values)

# canonical modelled breakpoint (the off-target-prone one we are testing against)
CANON_LEFT = 264
CANON_RIGHT = 2

# favorability thresholds
GC_FAV_LO, GC_FAV_HI = 40.0, 60.0          # "comfortable" GC band for either modality
ENTROPY_MIN = 1.8                          # bits; below this the +/-12nt window is low-complexity
JWIN = 10                                  # +/-10 nt junction-window for GC
ENTWIN = 12                                # +/-12 nt window for the entropy/complexity flag


def gc(s):
    return round(100 * (s.count("G") + s.count("C")) / len(s), 1) if s else 0.0


def shannon_entropy(s):
    """Per-base Shannon entropy (bits) of a nucleotide string; max 2.0 for 4 equal bases."""
    if not s:
        return 0.0
    n = len(s)
    ent = 0.0
    for b in set(s):
        p = s.count(b) / n
        if p > 0:
            ent -= p * math.log2(p)
    return round(ent, 3)


def has_lowcomplexity_repeat(s):
    """True if s contains a run of >=4 identical bases OR a dinucleotide repeated >=4 times."""
    if re.search(r"(.)\1{3,}", s):                 # mono: e.g. GGGG, AAAA
        return True
    if re.search(r"(..)\1{3,}", s):                # di:   e.g. GCGCGCGC (4x repeat of a 2mer)
        return True
    return False


def scan_one(ews, nr4, left_len, right_start):
    """Evaluate a single (left_len, right_start) breakpoint. Returns a row dict.

    Sets the ja module globals so ja.build_fusion_cds / ja.design and js.design all see this
    breakpoint, then restores nothing (caller re-sets per iteration; globals are overwritten).
    """
    ja.EWSR1_KEEP_AA = left_len
    ja.NR4A3_KEEP_AA_FROM = right_start
    left, right, fusion = ja.build_fusion_cds(ews, nr4)
    j = len(left)                                   # first index of NR4A3 base in fused string

    # junction +/-10 nt window GC, and +/-12 nt window entropy / low-complexity flag
    win_gc = fusion[max(0, j - JWIN): j + JWIN]
    win_ent = fusion[max(0, j - ENTWIN): j + ENTWIN]
    jwin_gc = gc(win_gc)
    jwin_entropy = shannon_entropy(win_ent)
    lowcomplex = has_lowcomplexity_repeat(win_ent)

    # gapmer designs at this breakpoint (re-run ja.design on this fusion)
    gapmers = ja.design(left, right, fusion)
    gap_gcs = [o["gc_percent"] for o in gapmers]
    gap_fs = [o for o in gapmers if o["fusion_specific"]]
    best_gap_in_band = None
    for o in sorted(gapmers, key=lambda x: abs(x["gc_percent"] - 50)):
        if GC_FAV_LO <= o["gc_percent"] <= GC_FAV_HI and o["fusion_specific"]:
            best_gap_in_band = o
            break

    # siRNA designs at this breakpoint (re-run js.design on this fusion)
    sirnas = js.design(left, right, fusion)
    sir_gcs = [o["gc_percent"] for o in sirnas]
    sir_fs = [o for o in sirnas if o["fusion_specific"]]
    best_sir_in_band = None
    for o in sorted(sirnas, key=lambda x: abs(x["gc_percent"] - 50)):
        if GC_FAV_LO <= o["gc_percent"] <= GC_FAV_HI and o["fusion_specific"]:
            best_sir_in_band = o
            break

    fusion_specific = bool(gap_fs) or bool(sir_fs)
    has_band_design = (best_gap_in_band is not None) or (best_sir_in_band is not None)
    favorable = bool(has_band_design and jwin_entropy >= ENTROPY_MIN
                     and not lowcomplex and fusion_specific)

    # pick the single best oligo for this breakpoint (prefer in-band; gapmer or siRNA)
    best_oligo = None
    if best_gap_in_band or best_sir_in_band:
        cands = []
        if best_gap_in_band:
            cands.append(("gapmer", best_gap_in_band, best_gap_in_band["gc_percent"]))
        if best_sir_in_band:
            cands.append(("siRNA", best_sir_in_band, best_sir_in_band["gc_percent"]))
        modality, o, _ = min(cands, key=lambda c: abs(c[2] - 50))
        best_oligo = {"modality": modality, **o}

    return {
        "EWSR1_keep_aa": left_len,
        "NR4A3_from_aa": right_start,
        "is_canonical": (left_len == CANON_LEFT and right_start == CANON_RIGHT),
        "junction_context_mRNA": (left[-12:] + "|" + right[:12]),
        "junction_window_gc_pm10": jwin_gc,
        "junction_window_entropy_pm12_bits": jwin_entropy,
        "low_complexity_repeat": lowcomplex,
        "n_gapmer_candidates": len(gapmers),
        "min_gapmer_gc": min(gap_gcs) if gap_gcs else None,
        "n_gapmer_fusion_specific": len(gap_fs),
        "best_gapmer_in_band_gc": best_gap_in_band["gc_percent"] if best_gap_in_band else None,
        "n_sirna_candidates": len(sirnas),
        "min_sirna_gc": min(sir_gcs) if sir_gcs else None,
        "n_sirna_fusion_specific": len(sir_fs),
        "best_sirna_in_band_gc": best_sir_in_band["gc_percent"] if best_sir_in_band else None,
        "fusion_specific_design_exists": fusion_specific,
        "favorable": favorable,
        "best_oligo": best_oligo,
    }


def main():
    # save originals so we leave the imported modules as we found them
    orig_keep, orig_from = ja.EWSR1_KEEP_AA, ja.NR4A3_KEEP_AA_FROM

    ews = ja.fetch_cds(ja.EWSR1_MRNA)
    nr4 = ja.fetch_cds(ja.NR4A3_MRNA)
    # populate the parent-CDS globals used by both design()s for the specificity check
    ja.EWSR1_full, ja.NR4A3_full = ews, nr4

    rows = []
    # include the canonical breakpoint explicitly so the summary can always report it
    sweep = [(L, R) for L in EWSR1_KEEP_RANGE for R in NR4A3_FROM_RANGE]
    if (CANON_LEFT, CANON_RIGHT) not in sweep:
        sweep.append((CANON_LEFT, CANON_RIGHT))

    for (L, R) in sweep:
        try:
            rows.append(scan_one(ews, nr4, L, R))
        except Exception as e:  # noqa — one bad breakpoint must not kill the whole scan
            print(f"  breakpoint EWSR1={L}/NR4A3={R} failed: {e}", file=sys.stderr)
            rows.append({
                "EWSR1_keep_aa": L, "NR4A3_from_aa": R,
                "is_canonical": (L == CANON_LEFT and R == CANON_RIGHT),
                "error": str(e), "favorable": False,
            })

    # restore imported-module globals
    ja.EWSR1_KEEP_AA, ja.NR4A3_KEEP_AA_FROM = orig_keep, orig_from

    favorable = [r for r in rows if r.get("favorable")]
    # most-favorable = favorable, then lowest junction-window GC, then highest entropy
    def fav_rank(r):
        return (-r.get("junction_window_gc_pm10", 999),
                r.get("junction_window_entropy_pm12_bits", 0))
    most_fav = max(favorable, key=fav_rank) if favorable else None

    canon = next((r for r in rows if r.get("is_canonical")), None)
    canon_favorable = bool(canon and canon.get("favorable"))

    result = {
        "_note": ("Breakpoint-sensitivity scan for EWSR1::NR4A3 junction oligos (ASO gapmer + "
                  "siRNA). TRIAGE ONLY: ranks modelled in-frame breakpoints by how favorable "
                  "their junction is for an oligo (GC band, complexity, parent-specificity). Not "
                  "a validated drug; specificity here is a GC/complexity/parent-substring triage, "
                  "NOT the full BLAST off-target screen."),
        "_honest_caveats": [
            "Breakpoints are MODELLED positions (a codon-space sensitivity sweep), not exon-exact.",
            "The companion exon work found EWSR1 exons 7/9/10/11/12/13 -> predominantly NR4A3 "
            "exon 3; this sweep brackets that window in CDS-codon space rather than mapping exons.",
            "Real clinical design requires the patient's actually-sequenced breakpoint.",
            "Specificity = gapmer/siRNA target window absent from both parent CDSs (substring "
            "test); it is a triage, not the full transcriptome BLAST off-target screen.",
            "GC/entropy thresholds (40-60% GC, entropy>=1.8 bits, no >=4 mono/di repeat) are "
            "design heuristics, not validated cutoffs.",
        ],
        "_breakpoint_model": {
            "EWSR1_mRNA": ja.EWSR1_MRNA, "NR4A3_mRNA": ja.NR4A3_MRNA,
            "EWSR1_keep_aa_sweep": [EWSR1_KEEP_RANGE.start, EWSR1_KEEP_RANGE.stop,
                                    EWSR1_KEEP_RANGE.step],
            "NR4A3_from_aa_sweep": [NR4A3_FROM_RANGE.start, NR4A3_FROM_RANGE.stop,
                                    NR4A3_FROM_RANGE.step],
            "canonical_breakpoint": {"EWSR1_keep_aa": CANON_LEFT, "NR4A3_from_aa": CANON_RIGHT},
        },
        "_thresholds": {
            "gc_favorable_band_percent": [GC_FAV_LO, GC_FAV_HI],
            "junction_window_entropy_min_bits": ENTROPY_MIN,
            "gc_window_nt_each_side": JWIN,
            "entropy_window_nt_each_side": ENTWIN,
        },
        "gapmer_oligo_length": ja.OLIGO_LEN,
        "sirna_guide_length": js.LEN,
        "n_breakpoints_scanned": len(rows),
        "n_favorable": len(favorable),
        "canonical_breakpoint_favorable": canon_favorable,
        "canonical_breakpoint_row": canon,
        "most_favorable_breakpoint": most_fav,
        "rows": rows,
    }

    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    slim = {k: v for k, v in result.items() if k != "rows"}
    print(json.dumps(slim, indent=2)[:3500])


if __name__ == "__main__":
    main()
