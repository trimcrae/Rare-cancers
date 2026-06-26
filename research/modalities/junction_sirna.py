#!/usr/bin/env python3
"""
Junction-spanning siRNA design for EWSR1::NR4A3 — a GC-tolerant alternative to the
GC-rich (75-81%) junction gapmers (junction_aso.py).

WHY: the committed gapmers sit at 75-81% GC, outside the comfort zone; RISC/Ago2 tolerates
sequence composition differently from RNase-H, so a junction-spanning siRNA is the parallel
route the ASO paper names. This script designs it on the same modelled fusion CDS.

DESIGN RULES (standard siRNA heuristics, applied here):
  - 19-nt guide-paired window straddling the breakpoint, with the junction near the centre
    (positions 8-12), i.e. spanning the Ago2 cleavage site (between sense positions 10/11) so
    a parent transcript with a central mismatch is NOT cleaved -> fusion specificity.
  - GC 30-52% (the point: avoid the gapmer's GC problem).
  - Thermodynamic asymmetry: the antisense (guide) 5' end should be the LESS stable (A/U) end
    so the guide strand is preferentially loaded into RISC.
  - No runs of >= 4 identical nucleotides (synthesis/immunostimulation heuristic).
  - fusion-specific: the 19-nt target window is not a perfect substring of either parent CDS.

INTERNET REQUIRED (NCBI E-utilities, via junction_aso.fetch_cds). Runs on a GitHub-hosted
runner; output published to modalities-cache. DESIGN ONLY — hypotheses for wet-lab testing.

Output: junction-sirna-designs.json
"""
import json
import os
import re
import sys

import junction_aso as ja

OUT = os.path.join(os.path.dirname(__file__), "junction-sirna-designs.json")
LEN = 19                       # guide-paired core length
GC_LO, GC_HI = 30.0, 52.0      # GC comfort window for siRNA
CENTER_LO, CENTER_HI = 8, 12   # junction must fall in these 1-based positions of the window


def has_run4(s):
    return bool(re.search(r"(.)\1\1\1", s))


def design(left, right, fusion):
    j = len(left)
    out = []
    for start in range(0, len(fusion) - LEN + 1):
        end = start + LEN
        jpos = j - start                       # 1-based-ish position of first NR4A3 base in window
        if not (CENTER_LO <= jpos <= CENTER_HI):
            continue
        target = fusion[start:end]             # sense (mRNA) window
        guide = ja.revcomp(target).replace("T", "U")   # antisense guide, 5'->3' (RNA)
        gc = ja.gc(target)
        # asymmetry: antisense-5' pairs with sense-3'; favour antisense-5' = A/U => sense-3' = U/A
        sense_3p = target[-1]
        antisense_5p = guide[0]
        asymmetry_ok = antisense_5p in "AU"
        spec_ok = (target not in ja.EWSR1_full) and (target not in ja.NR4A3_full)
        out.append({
            "guide_antisense_5to3": guide,
            "passenger_sense_5to3": target.replace("T", "U"),
            "target_DNA_window": target,
            "junction_pos_in_window": jpos,
            "gc_percent": gc,
            "gc_in_window": GC_LO <= gc <= GC_HI,
            "antisense_5prime": antisense_5p,
            "asymmetry_favours_guide_loading": asymmetry_ok,
            "no_run_of_4": not has_run4(target),
            "bases_from_EWSR1": jpos,
            "bases_from_NR4A3": LEN - jpos,
            "fusion_specific": spec_ok,
        })

    def score(o):
        center_pen = abs(o["junction_pos_in_window"] - 10)        # closest to the cut site
        gc_pen = 0 if o["gc_in_window"] else 1
        return (o["fusion_specific"], o["asymmetry_favours_guide_loading"],
                -gc_pen, o["no_run_of_4"], -center_pen)
    out.sort(key=score, reverse=True)
    return out


def main():
    ews = ja.fetch_cds(ja.EWSR1_MRNA)
    nr4 = ja.fetch_cds(ja.NR4A3_MRNA)
    ja.EWSR1_full, ja.NR4A3_full = ews, nr4
    left, right, fusion = ja.build_fusion_cds(ews, nr4)
    cands = design(left, right, fusion)

    fs = [o for o in cands if o["fusion_specific"]]
    good = [o for o in fs if o["gc_in_window"] and o["asymmetry_favours_guide_loading"]
            and o["no_run_of_4"]]
    result = {
        "_note": ("Junction-spanning siRNA designs (RISC/Ago2 mechanism) — a GC-TOLERANT "
                  "alternative to the 75-81% GC junction gapmers. DESIGN ONLY; hypotheses for "
                  "wet-lab knockdown + parental-sparing testing. Specificity is predicted "
                  "(central-cleavage-site discrimination), not validated."),
        "_breakpoint_model": {"assumption": True, "EWSR1_mRNA": ja.EWSR1_MRNA,
                              "NR4A3_mRNA": ja.NR4A3_MRNA,
                              "caveat": "modelled breakpoint; re-run on a sequenced patient fusion"},
        "guide_length": LEN, "gc_window": [GC_LO, GC_HI],
        "n_candidates": len(cands),
        "n_fusion_specific": len(fs),
        "n_passing_all_filters": len(good),
        "min_gc_among_fusion_specific": min((o["gc_percent"] for o in fs), default=None),
        "top_designs": (good or fs)[:12],
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: v for k, v in result.items() if k != "top_designs"}, indent=2))


if __name__ == "__main__":
    main()
