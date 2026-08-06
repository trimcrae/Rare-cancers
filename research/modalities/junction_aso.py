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

⛔ REAL-EXON MODE IS mRNA-LEVEL, AND THAT IS NOT A DETAIL. `FUSION_JUNCTION_MODE=real` builds the
chimera from the spliced TRANSCRIPTS (cDNA + exon boundaries in transcript coordinates), not from
the CDSs, because a fusion transcript retains the acceptor exon whole — 5'UTR included — and those
retained bases sit immediately 3' of the seam that the oligo hybridises to. Building this from CDS
concatenation produced two separate wrong answers in one day (see the two-defect block below).

Outputs:
  junction-aso-designs[SUFFIX].json  — the design panel for ONE graded junction
  junction-mrna-frame-audit.json     — `--audit`: every declared breakpoint graded, designing
                                       nothing. Run this FIRST; a panel may only be emitted for a
                                       row this table grades EMITTABLE.
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
            "mode": "real_exon_junction_mRNA",
            "source": ("Ensembl MANE/canonical TRANSCRIPT structure (junction_aso.transcript_model): "
                       "spliced cDNA, exon boundaries in transcript coordinates, CDS located inside "
                       "the cDNA. Cross-checked exon-for-exon against the committed "
                       "nr4a3-exon-audit.json before anything is emitted."),
            "EWSR1_exon_end": e, "NR4A3_exon_start": n,
            "note": ("Real in-frame EWSR1::NR4A3 exon junction built at the mRNA level — the acceptor "
                     "exon is taken WHOLE, including any 5'UTR it carries, because that is what a "
                     "fusion transcript contains and what an ASO hybridises to. Self-checked: exon "
                     "lengths sum to the cDNA, the CDS is a unique substring of the cDNA, "
                     "translate(CDS)==Ensembl protein, and the chimeric ORF retains the NR4A3 "
                     "C-terminus. NOT the codon-space modelled reference."),
        }
    return "reference_codon264_from2", {
        "mode": "modelled_reference_codon_space",
        "EWSR1_coding_kept": f"codons 1-{EWSR1_KEEP_AA} (in-frame)",
        "NR4A3_coding_kept": f"from codon {NR4A3_KEEP_AA_FROM} (in-frame)",
        "note": ("Codon-space modelled reference breakpoint (junction_aso.py default; a label of "
                 "convenience, NOT a validated clinical breakpoint)."),
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────
# ⛔⛔ TWO DEFECTS, ONE SEAM. Read both before touching the real-mode builder below.
#
# DEFECT 1 (found 2026-08-06 by the route framing audit; fixed the same day).
#   The old code did `fb.gene_model(...)["offsets"][n - 2]` — it indexed a table keyed by CODING
#   exon with a TRANSCRIPT exon number. NR4A3 ENST00000395097 has 8 transcript exons of which 1
#   and 2 carry no coding sequence, so the label "NR4A3 exon 3" addressed the THIRD CODING exon
#   (transcript exon 5) instead. MEASURED: the committed seam `TTGTCCGTACAG` sits at NR4A3 CDS
#   nt 1081 = residue 361 — bit-for-bit the `nr4_cds_nt: 1081` / `nr4a3_resumes_at_residue: 361`
#   that `fusion-neoantigen-retraction.json` grades SEAM_NOT_PRODUCED, against a corrected
#   `nr4a3_resume_range_across_plausible_breakpoints` of [1, 1] in `fusion-object-inventory.json`.
#   The EWSR1 side reproduced correctly throughout (EWSR1 exon 1 IS coding, so rank == coding
#   index), which is why nothing caught it: the e7n3 and e12n3 panels agreed with each other and
#   the paper read that agreement as confirmation. Two artifacts agreeing is not evidence when
#   one defect produces both.
#
# DEFECT 2 (found 2026-08-06 in this task, from the SAME committed exon audit, $0, no network).
#   ⚠ THE FIX FOR DEFECT 1 WAS ARITHMETICALLY RIGHT AND STILL COULD NOT REGENERATE THE PANEL.
#   It concatenated CDS to CDS: `nr4_cds[resume_offset(nr4, n)]`, i.e. it resumed NR4A3 at its
#   ATG and DISCARDED the 5'UTR that transcript exon 3 carries ahead of that ATG. A real fusion
#   transcript retains the acceptor exon WHOLE, UTR included — those bases are physically in the
#   mRNA, are read in the donor's frame, and are the bases immediately 3' of the seam that an ASO
#   actually hybridises to. Dropping them is wrong twice over:
#     (a) the reported seam context is wrong for an mRNA-level modality, and
#     (b) the in-frame self-check then fails for every donor whose cut is not a multiple of 3.
#   MEASURED from `nr4a3-exon-audit.json` (committed; no network needed to see this):
#     EWSR1 cut offsets mod 3 — e6 581→2 · e7 793→1 · e8 974→2 · e9 1012→1 · e10 1045→1 ·
#     e11 1164→0 · e12 1294→1 · e13 1417→1 · e14 1580→2.
#   With NR4A3 resuming at CDS nt 0, ONLY e11 is a multiple of 3. So the Defect-1 fix would have
#   RAISED "not in-frame" on **e7n3 and e12n3 — the two junctions the manuscript leads with** —
#   and silently admitted only e11n3, a junction the manuscript does not use. A regeneration run
#   before this was found would have reported the lane as broken for the wrong reason.
#   ⭐ The frame is closed by the acceptor exon's own 5' phase, not by the donor alone. Let U be
#   the number of NR4A3 transcript-exon-3 bases 5' of the ATG; the chimeric ORF is in frame iff
#   (cut + U) % 3 == 0. e7 and e12 are both ≡1, so BOTH are in frame for the same U ≡ 2 (mod 3),
#   which is a PREDICTION this module tests against Ensembl rather than an assumption it makes.
#   U is not knowable from any artifact in this repo — `nr4a3-exon-audit.json` records coding nt
#   per exon only — so it is UNKNOWN here and is measured by the CI fetch.
#
# THE RULE THAT FALLS OUT: a nucleotide-level fusion model for an RNA-targeting modality must be
# built from the TRANSCRIPT (cDNA + exon boundaries in transcript coordinates), never from the
# CDS. `fusion_breakpoints.gene_model` is a CDS/protein instrument and is correct for the
# neoantigen lane, which asks a protein question. It is the wrong instrument for this one.
# ─────────────────────────────────────────────────────────────────────────────────────────────

ENS = "https://rest.ensembl.org"
_TX_CACHE = {}


def transcript_model(symbol):
    """mRNA-level model of `symbol`'s canonical transcript — the instrument this module needs.

    Returns cdna (spliced transcript), cds, protein, exon lengths and cumulative exon ends in
    TRANSCRIPT coordinates, and utr5_len (transcript nt 5' of the ATG). Every field is measured;
    nothing is assumed. Four self-checks, all of which RAISE:
      1. exon lengths sum to len(cdna)          — the exon list really is this transcript's
      2. the CDS occurs EXACTLY ONCE in the cdna — so utr5_len is unambiguous
      3. translate(cds) == Ensembl protein       — the reading frame is the annotated one
      4. per-exon coding nt reproduce the committed `nr4a3-exon-audit.json` exon-for-exon
    Check 4 is the provenance gate: if today's Ensembl read does not reproduce the exon index
    this repo's corrections were derived from, NOTHING downstream may be emitted, because a
    design panel built on an exon map nobody has graded is worse than no panel.
    """
    if symbol in _TX_CACHE:
        return _TX_CACHE[symbol]
    import fusion_breakpoints as fb
    look = fb.get(f"{ENS}/lookup/symbol/homo_sapiens/{symbol}?expand=1")
    tr = next((t for t in look["Transcript"] if t.get("is_canonical") == 1), look["Transcript"][0])
    strand = tr["strand"]
    exons = sorted(tr["Exon"], key=lambda e: e["start"], reverse=(strand == -1))
    exon_lens = [e["end"] - e["start"] + 1 for e in exons]
    tx_ends, cum = [], 0
    for L in exon_lens:
        cum += L
        tx_ends.append(cum)
    cdna = fb.get_text(f"{ENS}/sequence/id/{tr['id']}?type=cdna").replace("\n", "").upper()
    cds = fb.get_text(f"{ENS}/sequence/id/{tr['id']}?type=cds").replace("\n", "").upper()
    protein = fb.get_text(f"{ENS}/sequence/id/{tr['Translation']['id']}?type=protein").replace("\n", "")
    if cum != len(cdna):
        raise RuntimeError(f"{symbol}: exon lengths sum to {cum} != cdna length {len(cdna)}")
    if cdna.count(cds) != 1:
        raise RuntimeError(f"{symbol}: CDS occurs {cdna.count(cds)} times in the cdna — the 5'UTR "
                           "length would be ambiguous, so no seam may be emitted")
    utr5 = cdna.index(cds)
    if fb.translate(cds) != protein.replace("*", "").rstrip("X"):
        raise RuntimeError(f"{symbol}: translate(CDS) != Ensembl protein")
    model = {"symbol": symbol, "transcript": tr["id"], "strand": strand, "cdna": cdna, "cds": cds,
             "protein": protein, "exon_lens": exon_lens, "tx_ends": tx_ends, "utr5_len": utr5,
             "n_transcript_exons": len(exons)}
    _cross_check_against_committed_exon_audit(model)
    _TX_CACHE[symbol] = model
    return model


def coding_nt_per_exon(model):
    """Coding nt contributed by each TRANSCRIPT exon, derived from the transcript model alone."""
    lo, hi = model["utr5_len"], model["utr5_len"] + len(model["cds"])   # [lo, hi) in tx coords
    out, start = [], 0
    for end in model["tx_ends"]:
        out.append(max(0, min(end, hi) - max(start, lo)))
        start = end
    return out


def _cross_check_against_committed_exon_audit(model):
    """Check 4 — the provenance gate. Refuses on ANY disagreement with `nr4a3-exon-audit.json`."""
    path = os.path.join(os.path.dirname(__file__), "nr4a3-exon-audit.json")
    if not os.path.exists(path):                     # the gate cannot run; say so, do not pass
        raise RuntimeError("nr4a3-exon-audit.json is missing — the exon-index provenance gate "
                           "cannot run, so no seam may be emitted")
    with open(path) as fh:
        audit = json.load(fh)
    ref = audit.get(model["symbol"])
    if not ref:
        raise RuntimeError(f"{model['symbol']} absent from nr4a3-exon-audit.json")
    if ref["transcript"] != model["transcript"]:
        raise RuntimeError(f"{model['symbol']}: Ensembl canonical is {model['transcript']} but the "
                           f"committed audit graded {ref['transcript']} — different exon maps")
    got = coding_nt_per_exon(model)
    want = [e["coding_nt_in_exon"] for e in ref["exons"]]
    if got != want:
        raise RuntimeError(f"{model['symbol']}: per-exon coding nt {got} != committed audit {want}")
    if len(model["protein"].replace("*", "").rstrip("X")) != ref["protein_length"]:
        raise RuntimeError(f"{model['symbol']}: protein length disagrees with the committed audit")


def exon_tx_end(model, rank):
    """Transcript nt through the END of transcript exon `rank` (1-based)."""
    if not 1 <= rank <= len(model["tx_ends"]):
        raise ValueError(f"{model['symbol']}: no transcript exon {rank} "
                         f"(has {len(model['tx_ends'])})")
    return model["tx_ends"][rank - 1]


def exon_tx_start(model, rank):
    """0-based transcript index at which transcript exon `rank` BEGINS."""
    if not 1 <= rank <= len(model["tx_ends"]):
        raise ValueError(f"{model['symbol']}: no transcript exon {rank} "
                         f"(has {len(model['tx_ends'])})")
    return 0 if rank == 1 else model["tx_ends"][rank - 2]


def mrna_junction(ews, nr4, e_end, n_start):
    """Build the chimeric mRNA for EWSR1 exon `e_end` :: NR4A3 exon `n_start` and grade it.

    Returns a dict that is a READING, never an assertion: `in_frame` may be False and
    `nr4a3_first_residue` may be a value no plausible breakpoint produces. `main()` refuses to
    emit designs on either — but the grading itself is always reported, because a refusal that
    cannot say what it refused is the failure mode this whole module is a correction for.
    """
    import fusion_breakpoints as fb
    left = ews["cdna"][:exon_tx_end(ews, e_end)]
    right = nr4["cdna"][exon_tx_start(nr4, n_start):]
    fusion = left + right
    orf = fusion[ews["utr5_len"]:]                 # the chimeric ORF starts at EWSR1's own ATG
    prot = fb.translate(orf)
    in_frame = prot.endswith(nr4["protein"][-100:])
    # where the acceptor exon's coding actually starts, in that exon's own transcript coordinates
    coding = coding_nt_per_exon(nr4)
    acceptor_utr = max(0, nr4["utr5_len"] - exon_tx_start(nr4, n_start))
    nr4_cds_nt = max(0, exon_tx_start(nr4, n_start) - nr4["utr5_len"])
    first_res = (nr4_cds_nt // 3) + 1 if coding[n_start - 1] else None
    ews_coding_nt = sum(coding_nt_per_exon(ews)[:e_end])
    return {
        "junction_label": f"EWSR1_e{e_end}__NR4A3_e{n_start}",
        "EWSR1_exon_end": e_end, "NR4A3_exon_start": n_start,
        "ewsr1_coding_nt_through_cut": ews_coding_nt,
        "ewsr1_last_whole_residue": ews_coding_nt // 3,
        "ewsr1_coding_phase": ews_coding_nt % 3,
        "nr4a3_acceptor_exon_is_coding": bool(coding[n_start - 1]),
        "nr4a3_acceptor_exon_5utr_nt_retained": acceptor_utr,
        "nr4a3_cds_nt_at_resume": nr4_cds_nt,
        "nr4a3_first_residue": first_res,
        "frame_sum_mod3": (ews_coding_nt + acceptor_utr) % 3,
        "in_frame": bool(in_frame),
        "chimeric_protein_length": len(prot),
        "junction_context_mRNA": left[-12:] + "|" + right[:12],
        "_left": left, "_right": right, "_fusion": fusion,
    }


# The corrected resume residues a plausible breakpoint can produce. ONE HOME: read out of
# `fusion-object-inventory.json` at run time, never typed here — that file is the graded record and
# a copy of its numbers in this module is exactly how the retracted seam survived.
def plausible_nr4a3_resume_residues():
    path = os.path.join(os.path.dirname(__file__), "fusion-object-inventory.json")
    with open(path) as fh:
        inv = json.load(fh)
    lo, hi = inv["inventory"]["excluded_span"][
        "nr4a3_resume_range_across_plausible_breakpoints"]
    return lo, hi


def build_parents_and_fusion():
    """Return (ews_parent, nr4_parent, left, right, fusion) for either the codon-space modelled
    reference breakpoint (default) or a REAL exon-level junction (env-selected), and set the
    module parent globals used by design()'s specificity check.

    Real mode (FUSION_JUNCTION_MODE=real) is built at the mRNA level — see the two-defect block
    above. The parents used for the specificity substring test become the full cDNAs rather than
    the CDSs, which is both more correct (an ASO meets the whole transcript, UTRs included) and
    strictly stricter (a superset)."""
    global EWSR1_full, NR4A3_full
    if os.environ.get("FUSION_JUNCTION_MODE") == "real":
        e_end = int(os.environ.get("EWSR1_EXON_END", "12"))
        n_start = int(os.environ.get("NR4A3_EXON_START", "3"))
        ews = transcript_model("EWSR1")
        nr4 = transcript_model("NR4A3")
        j = mrna_junction(ews, nr4, e_end, n_start)
        if not j["nr4a3_acceptor_exon_is_coding"]:
            raise RuntimeError(
                f"NR4A3 transcript exon {n_start} carries no coding sequence — refusing to slide "
                "onto a neighbour (this is Defect 1, and it is what produced the retracted seam)")
        lo, hi = plausible_nr4a3_resume_residues()
        if not (lo <= j["nr4a3_first_residue"] <= hi):
            raise RuntimeError(
                f"EWSR1 e{e_end} :: NR4A3 e{n_start} resumes NR4A3 at residue "
                f"{j['nr4a3_first_residue']}, outside the corrected plausible range [{lo}, {hi}] "
                "in fusion-object-inventory.json — this is the exact grade "
                "fusion-neoantigen-retraction.json calls SEAM_NOT_PRODUCED. Refusing to emit.")
        if not j["in_frame"]:
            raise RuntimeError(
                f"EWSR1 e{e_end} :: NR4A3 e{n_start} is not in-frame at the mRNA level "
                f"(EWSR1 coding nt {j['ewsr1_coding_nt_through_cut']} phase "
                f"{j['ewsr1_coding_phase']} + acceptor 5'UTR "
                f"{j['nr4a3_acceptor_exon_5utr_nt_retained']} nt => "
                f"(cut+UTR) mod 3 = {j['frame_sum_mod3']}, must be 0); NR4A3 C-terminus not "
                "retained. This is a READING about that exon pair, not a code failure.")
        globals()["LAST_JUNCTION"] = j
        EWSR1_full, NR4A3_full = ews["cdna"], nr4["cdna"]
        return ews["cdna"], nr4["cdna"], j["_left"], j["_right"], j["_fusion"]
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
# The measured grading of the junction the last real-mode build accepted. None in default mode.
LAST_JUNCTION = None


# Declared breakpoint windows. ONE HOME: read out of `fusion_breakpoints`, never re-typed here.
def declared_windows():
    import fusion_breakpoints as fb
    return list(fb.EWSR1_EXON_WINDOW), list(fb.NR4A3_EXON_WINDOW)


def audit_window():
    """Grade EVERY declared breakpoint at the mRNA level and emit the table, designing nothing.

    This is the diagnostic the lane did not have. It answers, per exon pair and from measured
    Ensembl sequence: is the acceptor exon coding, where does NR4A3 resume, how many acceptor
    5'UTR bases the fusion retains, whether the chimeric ORF is in frame, and what the real mRNA
    seam is. A design panel may be emitted only for a row this table grades EMITTABLE.
    """
    ews = transcript_model("EWSR1")
    nr4 = transcript_model("NR4A3")
    lo, hi = plausible_nr4a3_resume_residues()
    e_win, n_win = declared_windows()
    rows = []
    for e in e_win:
        for n in n_win:
            try:
                j = mrna_junction(ews, nr4, e, n)
            except Exception as exc:                      # noqa — a refusal is a reading
                rows.append({"junction_label": f"EWSR1_e{e}__NR4A3_e{n}",
                             "grade": "UNREADABLE", "why": str(exc)})
                continue
            j = {k: v for k, v in j.items() if not k.startswith("_")}
            if not j["nr4a3_acceptor_exon_is_coding"]:
                j["grade"], j["why"] = "NON_CODING_ACCEPTOR", "acceptor exon carries no CDS"
            elif not (lo <= j["nr4a3_first_residue"] <= hi):
                j["grade"] = "SEAM_NOT_PRODUCED"
                j["why"] = (f"NR4A3 resumes at residue {j['nr4a3_first_residue']}, outside the "
                            f"corrected plausible range [{lo}, {hi}]")
            elif not j["in_frame"]:
                j["grade"] = "OUT_OF_FRAME"
                j["why"] = (f"(EWSR1 coding nt {j['ewsr1_coding_nt_through_cut']} + acceptor 5'UTR "
                            f"{j['nr4a3_acceptor_exon_5utr_nt_retained']}) mod 3 = "
                            f"{j['frame_sum_mod3']}")
            else:
                j["grade"], j["why"] = "EMITTABLE", "in frame, resume residue inside the corrected range"
            rows.append(j)
    out = os.path.join(os.path.dirname(__file__), "junction-mrna-frame-audit.json")
    res = {
        "_title": "EWSR1::NR4A3 chimeric-mRNA junction audit at the CORRECTED exon index",
        "_cost": "$0 — a GitHub-hosted CPU runner and two Ensembl reads. No GPU, no rental.",
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_what_this_is": (
            "The instrument the ASO lane was missing. `fusion_breakpoints.gene_model` is a "
            "CDS/protein instrument — correct for the neoantigen lane, wrong for an RNA-targeting "
            "modality, because it cannot see the acceptor exon's 5'UTR, which a fusion transcript "
            "retains and an ASO hybridises to. Every row here is measured from the spliced cDNA."),
        "_limits": [
            "Exon arithmetic and sequence composition only. No potency, no knockdown, no delivery, "
            "no tolerability and no clinical claim is made or implied.",
            "Canonical transcripts only. A different transcript gives a different exon map, and EMC "
            "breakpoints are reported against specific transcripts.",
            "Which exon pair a given PATIENT carries is not decidable from exon structure and is "
            "not decided here.",
        ],
        "transcripts": {g["symbol"]: {"transcript": g["transcript"], "cdna_nt": len(g["cdna"]),
                                      "cds_nt": len(g["cds"]), "utr5_nt": g["utr5_len"],
                                      "protein_aa": len(g["protein"].replace("*", "").rstrip("X")),
                                      "n_transcript_exons": g["n_transcript_exons"]}
                        for g in (ews, nr4)},
        "plausible_nr4a3_resume_range": [lo, hi],
        "_plausible_range_source": ("fusion-object-inventory.json -> reactive_residue_inventory."
                                    "excluded_span.nr4a3_resume_range_across_plausible_breakpoints"),
        "n_rows": len(rows),
        "grade_counts": {g: sum(1 for r in rows if r.get("grade") == g)
                         for g in sorted({r.get("grade") for r in rows})},
        "rows": rows,
    }
    with open(out, "w") as fh:
        json.dump(res, fh, indent=2)
    print("wrote", out, file=sys.stderr)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=2))
    for r in rows:
        print(f"  {r['junction_label']:<24} {r.get('grade'):<19} "
              f"resume_res={r.get('nr4a3_first_residue')} "
              f"utr={r.get('nr4a3_acceptor_exon_5utr_nt_retained')} "
              f"in_frame={r.get('in_frame')} seam={r.get('junction_context_mRNA')}")
    return res


def main():
    if "--audit" in sys.argv:
        audit_window()
        return
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
            # The measured grading of the accepted junction — present ONLY in real mode, and only
            # because every gate in `build_parents_and_fusion` passed. A reader must be able to see
            # WHICH seam these designs are for without re-deriving it, which is the whole lesson of
            # the retraction: the old artifacts carried a junction LABEL and no graded offsets, so
            # the wrong seam was invisible in the file that depended on it.
            **({"measured_junction": {k: v for k, v in LAST_JUNCTION.items()
                                      if not k.startswith("_")}} if LAST_JUNCTION else {}),
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
