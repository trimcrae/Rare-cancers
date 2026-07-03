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

# Oligo geometry is env-configurable so the SAME tiler runs the 16-mer 5-6-5 (default) OR the common
# 20-mer 5-10-5 layout (OLIGO_LEN=20, WING=5) — the longer gap is the paper's lever to convert
# residual-off-target junctions into clean designs.
OLIGO_LEN = int(os.environ.get("OLIGO_LEN", "16"))   # total gapmer length
WING = int(os.environ.get("WING", "5"))              # 5-6-5 at len 16; set OLIGO_LEN=20 for 5-10-5
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


def junction_label():
    """Human-readable label + provenance dict for the active breakpoint mode."""
    if os.environ.get("FUSION_JUNCTION_MODE") == "real":
        e = int(os.environ.get("EWSR1_EXON_END", "12"))
        n = int(os.environ.get("NR4A3_EXON_START", "3"))
        return f"EWSR1_e{e}__NR4A3_e{n}", {
            "mode": "real_exon_junction",
            "source": "Ensembl MANE/canonical exon structure (fusion_breakpoints.gene_model)",
            "EWSR1_exon_end": e, "NR4A3_exon_start": n,
            "note": ("Real in-frame EWSR1::NR4A3 exon junction (self-checked translate(CDS)==Ensembl "
                     "protein; NR4A3 C-terminus intact). NOT the codon-space modelled reference."),
        }
    return "reference_codon264_from2", {
        "mode": "modelled_reference_codon_space",
        "EWSR1_coding_kept": f"codons 1-{EWSR1_KEEP_AA} (in-frame)",
        "NR4A3_coding_kept": f"from codon {NR4A3_KEEP_AA_FROM} (in-frame)",
        "note": ("Codon-space modelled reference breakpoint (junction_aso.py default; a label of "
                 "convenience, NOT a validated clinical breakpoint)."),
    }


def build_parents_and_fusion():
    """Return (ews_cds, nr4_cds, left, right, fusion) for either the codon-space modelled
    reference breakpoint (default) or a REAL exon-level junction (env-selected), and set the
    module parent-CDS globals used by design()'s specificity check.

    Real mode (FUSION_JUNCTION_MODE=real): fetch Ensembl gene models via
    fusion_breakpoints.gene_model (self-checked translate(CDS)==Ensembl protein; exon offsets
    sum to CDS length), then cut EWSR1 at the coding end of exon EWSR1_EXON_END and resume
    NR4A3 at the coding start of exon NR4A3_EXON_START — the same construction the companion
    neoantigen work uses. The fusion is validated in-frame (NR4A3 C-terminus intact)."""
    global EWSR1_full, NR4A3_full
    if os.environ.get("FUSION_JUNCTION_MODE") == "real":
        import fusion_breakpoints as fb
        e_end = int(os.environ.get("EWSR1_EXON_END", "12"))
        n_start = int(os.environ.get("NR4A3_EXON_START", "3"))
        ews = fb.gene_model("EWSR1")
        nr4 = fb.gene_model("NR4A3")
        ews_cds, nr4_cds = ews["cds"], nr4["cds"]
        p = ews["offsets"][e_end - 1]        # coding nt through end of EWSR1 exon e_end
        q = nr4["offsets"][n_start - 2]      # coding nt before start of NR4A3 exon n_start
        left, right = ews_cds[:p], nr4_cds[q:]
        fusion = left + right
        if not fb.translate(fusion).endswith(nr4["protein"][-100:]):
            raise RuntimeError(f"EWSR1 e{e_end} :: NR4A3 e{n_start} is not in-frame "
                               "(NR4A3 C-terminus not intact) — choose a valid exon pair")
        EWSR1_full, NR4A3_full = ews_cds, nr4_cds
        return ews_cds, nr4_cds, left, right, fusion
    # default: codon-space modelled reference breakpoint (NCBI RefSeq CDS)
    ews_cds = fetch_cds(EWSR1_MRNA)
    nr4_cds = fetch_cds(NR4A3_MRNA)
    EWSR1_full, NR4A3_full = ews_cds, nr4_cds
    left, right, fusion = build_fusion_cds(ews_cds, nr4_cds)
    return ews_cds, nr4_cds, left, right, fusion


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
        # GAP-LEVEL discrimination (red-team F3): RNase-H1 cleaves only where the central DNA
        # gap [gap_start, gap_end) is base-paired, so fusion-vs-parent discrimination is set by
        # junction-unique bases INSIDE the gap on each side, not across the whole 16-mer. The
        # oligo-wide specificity_margin (min(left_bases, right_bases)) OVERSTATES true discrimination
        # (a parent can share up to WING wing bases plus part of the gap). Report the gap-level
        # margin as the honest operative metric.
        gap_left = j - gap_start              # junction-unique EWSR1 bases within the gap
        gap_right = gap_end - j               # junction-unique NR4A3 bases within the gap
        gap_margin = min(gap_left, gap_right)
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
            "gap_bases_from_EWSR1": gap_left,
            "gap_bases_from_NR4A3": gap_right,
            "gap_specificity_margin": gap_margin,          # operative metric (junction-unique bases in the gap)
            "gap_centered": gap_margin >= 2,               # >=2 junction-unique gap bases each side
            "gc_percent": gc(target),
            "has_G4_motif": bool(re.search("G{4,}", target)),
            "fusion_specific": spec_ok,
        })
    # rank: gap-centred discrimination first (the operative metric), then oligo-wide margin,
    # then mid GC (40-60), then no G4. Prefers designs whose junction-unique bases fall inside
    # the catalytic gap on both sides (red-team F3 gap-centred design rule).
    def score(o):
        gc_pen = abs(o["gc_percent"] - 50)
        return (o["gap_specificity_margin"], o["specificity_margin"], -gc_pen,
                0 if not o["has_G4_motif"] else -1)
    oligos.sort(key=score, reverse=True)
    return oligos


# module-level full mRNAs for the specificity check (populated in main)
EWSR1_full = ""
NR4A3_full = ""


def main():
    ews, nr4, left, right, fusion = build_parents_and_fusion()
    oligos = design(left, right, fusion)
    label, prov = junction_label()
    suffix = os.environ.get("OUT_SUFFIX", "")
    out = os.path.join(os.path.dirname(__file__), f"junction-aso-designs{suffix}.json")

    result = {
        "_note": "Fusion-junction gapmer ASO designs (RNase-H1 mechanism). DESIGN ONLY "
                 "— hypotheses for wet-lab knockdown testing; not a validated drug.",
        "_breakpoint_model": {
            "assumption": prov["mode"] != "real_exon_junction",
            "junction_label": label,
            "EWSR1_mRNA": EWSR1_MRNA, "NR4A3_mRNA": NR4A3_MRNA,
            "junction_context_mRNA": (left[-12:] + "|" + right[:12]),
            "caveat": "Re-run with a patient's sequenced fusion transcript for clinical design.",
            **prov,
        },
        "oligo_length": OLIGO_LEN,
        "architecture": f"{WING}-{GAP}-{WING}",
        "n_candidates": len(oligos),
        "n_fusion_specific": sum(1 for o in oligos if o["fusion_specific"]),
        "n_gap_centered": sum(1 for o in oligos if o["fusion_specific"] and o["gap_centered"]),
        "_gap_margin_note": ("gap_specificity_margin = junction-unique bases INSIDE the 6-nt "
                             "catalytic gap on the shorter side; it is the operative "
                             "fusion-vs-parent discriminator (RNase-H cleaves only across the "
                             "gap). The oligo-wide specificity_margin overstates discrimination "
                             "(red-team F3). gap_centered = >=2 unique gap bases each side."),
        "top_designs": oligos[:12],
    }
    with open(out, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", out, file=sys.stderr)
    print(json.dumps({k: v for k, v in result.items() if k != "top_designs"}, indent=2))


if __name__ == "__main__":
    main()
