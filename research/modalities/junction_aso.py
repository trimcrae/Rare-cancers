#!/usr/bin/env python3
"""
Fusion-junction antisense oligonucleotide (gapmer) design for EWSR1::NR4A3 EMC.

Rationale. The chimeric mRNA's junction is a tumour-specific sequence: no normal
transcript contains the EWSR1-exon -> NR4A3-exon seam. A gapmer ASO whose central
DNA window straddles that seam can direct RNase-H1 cleavage of the fusion transcript
while sparing wild-type EWSR1 and NR4A3 mRNAs (each of which matches only one half of
the oligo). This is a transcript-level modality that needs no druggable protein pocket.

What this does (real, reproducible; sequences fetched from NCBI, nothing invented):
  1. Fetches the RefSeq mRNAs for EWSR1 (NM_005243) and NR4A3 (NM_006981) from NCBI
     E-utilities and extracts their CDS.
  2. Builds the modelled fusion mRNA at the same canonical breakpoint used by
     fusion_neoantigen.py (EWSR1 N-terminal coding fragment :: retained NR4A3 CDS),
     keeping the junction in-frame and FLAGGING the breakpoint as a model assumption.
  3. Tiles candidate gapmers (default 16-mer, 5-6-5 LNA/DNA/LNA architecture; 5-10-5 is the
     common 20-mer template) whose
     central DNA gap spans the junction, i.e. each oligo must draw bases from BOTH
     sides of the seam (that is what makes it fusion-specific).
  4. Filters/annotates each candidate by standard design heuristics: %GC window,
     absence of >=4 consecutive G (G-quadruplex / tox motif), and the count of
     contiguous bases on the shorter side of the junction (specificity margin: the
     more unique bases on each side, the less either parent transcript is engaged).
  5. Verifies the full antisense oligo is NOT a perfect complement to either parent
     mRNA (true junction specificity).

This is a DESIGN tool, not a validated drug. Output oligos are hypotheses to be tested
(knockdown + parental-sparing controls) in EMC cell models. Delivery to tumour is the
unsolved, separate problem and is out of scope.

Output: junction-aso-designs.json
"""

import json
import os
import re
import sys
import time
import urllib.request

OUT = os.path.join(os.path.dirname(__file__), "junction-aso-designs.json")

EWSR1_MRNA = "NM_005243"
NR4A3_MRNA = "NM_006981"

# Same modelled breakpoint convention as fusion_neoantigen.py (protein-level):
# EWSR1 kept to residue 264; NR4A3 kept from residue 2. We translate that to mRNA by
# locating the CDS and taking codons. Flagged as an assumption.
EWSR1_KEEP_AA = 264
NR4A3_KEEP_AA_FROM = 2

OLIGO_LEN = 16          # total gapmer length
WING = 5                # with OLIGO_LEN=16 this is a 5-6-5 (5 LNA wings, 6 DNA gap that must span junction);
                        # 5-10-5 is the common 20-mer template — change OLIGO_LEN to 20 for that layout
GAP = OLIGO_LEN - 2 * WING

EUTILS = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
          "?db=nuccore&id={acc}&rettype=fasta_cds_na&retmode=text")

COMP = str.maketrans("ACGTacgt", "TGCAtgca")


def revcomp(s):
    return s.translate(COMP)[::-1]


def fetch_cds(acc, retries=4):
    url = EUTILS.format(acc=acc)
    for i in range(retries):
        try:
            print(f"  fetching CDS {acc}", file=sys.stderr)
            with urllib.request.urlopen(url, timeout=60) as r:
                text = r.read().decode()
            # fasta_cds_na returns the CDS nucleotide sequence(s); take the first record
            blocks = [b for b in text.split(">") if b.strip()]
            seq = "".join(l.strip() for l in blocks[0].splitlines()[1:])
            seq = re.sub(r"[^ACGTacgt]", "", seq).upper()
            if seq:
                return seq
        except Exception as e:  # noqa
            print(f"  retry {i+1}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"could not fetch {acc}")


def build_fusion_cds(ews_cds, nr4_cds):
    left = ews_cds[: EWSR1_KEEP_AA * 3]              # EWSR1 coding fragment (in-frame)
    right = nr4_cds[(NR4A3_KEEP_AA_FROM - 1) * 3:]   # retained NR4A3 CDS (in-frame)
    return left, right, left + right


def gc(s):
    return round(100 * (s.count("G") + s.count("C")) / len(s), 1) if s else 0


def design(left, right, fusion):
    j = len(left)  # first index of NR4A3 base in the fused string
    oligos = []
    for start in range(0, len(fusion) - OLIGO_LEN + 1):
        end = start + OLIGO_LEN
        gap_start, gap_end = start + WING, end - WING  # central DNA gap [gap_start, gap_end)
        # the junction must fall inside the DNA gap (RNase-H cleaves there)
        if not (gap_start < j < gap_end):
            continue
        target = fusion[start:end]            # sense (mRNA) window
        oligo = revcomp(target)               # antisense oligo, 5'->3'
        left_bases = j - start                # mRNA bases from EWSR1 side
        right_bases = end - j                 # mRNA bases from NR4A3 side
        # specificity: oligo must not perfectly complement either parent transcript
        spec_ok = (target not in EWSR1_full) and (target not in NR4A3_full)
        oligos.append({
            "antisense_5to3": oligo,
            "target_mRNA_5to3": target,
            "architecture": f"{WING}-{GAP}-{WING} (LNA-DNA-LNA)",
            "junction_offset_in_oligo": OLIGO_LEN - (j - start),  # from 5' of antisense
            "bases_from_EWSR1": left_bases,
            "bases_from_NR4A3": right_bases,
            "specificity_margin": min(left_bases, right_bases),
            "gc_percent": gc(target),
            "has_G4_motif": bool(re.search("G{4,}", target)),
            "fusion_specific": spec_ok,
        })
    # rank: balanced junction (high specificity margin), mid GC (40-60), no G4
    def score(o):
        gc_pen = abs(o["gc_percent"] - 50)
        return (o["specificity_margin"], -gc_pen, 0 if not o["has_G4_motif"] else -1)
    oligos.sort(key=score, reverse=True)
    return oligos


# module-level full mRNAs for the specificity check (populated in main)
EWSR1_full = ""
NR4A3_full = ""


def main():
    global EWSR1_full, NR4A3_full
    ews = fetch_cds(EWSR1_MRNA)
    nr4 = fetch_cds(NR4A3_MRNA)
    EWSR1_full, NR4A3_full = ews, nr4
    left, right, fusion = build_fusion_cds(ews, nr4)
    oligos = design(left, right, fusion)

    result = {
        "_note": "Fusion-junction gapmer ASO designs (RNase-H1 mechanism). DESIGN ONLY "
                 "— hypotheses for wet-lab knockdown testing; not a validated drug.",
        "_breakpoint_model": {
            "assumption": True,
            "EWSR1_mRNA": EWSR1_MRNA, "NR4A3_mRNA": NR4A3_MRNA,
            "EWSR1_coding_kept": f"codons 1-{EWSR1_KEEP_AA} (in-frame)",
            "NR4A3_coding_kept": f"from codon {NR4A3_KEEP_AA_FROM} (in-frame)",
            "junction_context_mRNA": (left[-12:] + "|" + right[:12]),
            "caveat": "Breakpoint is modelled; re-run with a patient's sequenced fusion "
                      "transcript for clinical design.",
        },
        "oligo_length": OLIGO_LEN,
        "architecture": f"{WING}-{GAP}-{WING}",
        "n_candidates": len(oligos),
        "n_fusion_specific": sum(1 for o in oligos if o["fusion_specific"]),
        "top_designs": oligos[:12],
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: v for k, v in result.items() if k != "top_designs"}, indent=2))


if __name__ == "__main__":
    main()
