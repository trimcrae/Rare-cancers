#!/usr/bin/env python3
"""
Breakpoint-resolved fusion-junction neoantigen SCREEN for EWSR1::NR4A3 EMC.

WHY. The earlier neoantigen result (`fusion_neoantigen.py`) used ONE modelled junction
(EWSR1 kept to residue 264 :: NR4A3 from residue 2) — an assumption, not a sourced
breakpoint. This script removes the guess: it derives the *real* set of in-frame
EWSR1::NR4A3 junctions from actual exon structure and asks whether any predicted
MHC-I binder is robust across breakpoints.

⛔ PREDICTED MHC-I BINDING IS A SCREEN. It is not presentation, not immunogenicity, not
efficacy and not a clinical claim. Nothing here is a vaccine, a TCR or a therapy.

HOW (all measured; no invented sequence and no invented breakpoint).
  1. For EWSR1 and NR4A3, take the MANE/canonical **TRANSCRIPT** model — spliced cDNA,
     exon boundaries in TRANSCRIPT coordinates, CDS located inside the cDNA, `utr5_len`
     measured — via `junction_aso.transcript_model`. That function is the ONE
     implementation of this arithmetic in the repo; it self-checks the model four ways
     and gates it against the committed `nr4a3-exon-audit.json` before returning it.
     Source is `TRANSCRIPT_SOURCE=auto|ensembl|cache`; `cache` reads the committed
     `emc-construct-inputs.json` and needs no network, so this whole lane is $0 CPU up to
     the MHCflurry call.
  2. Enumerate candidate fusions over the documented breakpoint windows (EWSR1 exons
     ~6-14, NR4A3 exons 2-4 — the FET-fusion / EMC literature) and grade EVERY pair:
     `junction_aso.graded_window`. A refusal is a row, never a silent omission.
  3. Build peptides only for rows graded EMITTABLE — in frame at the mRNA level AND
     resuming NR4A3 inside the corrected plausible range owned by
     `fusion-object-inventory.json`.
  4. For each emitted junction, take junction-spanning 8-11mers absent from both parent
     proteins and screen MHC-I binding with MHCflurry-2.0 across common HLA-A/-B alleles.
  5. Report, per junction, the top-ranked peptides; and ACROSS junctions, which recur.

Output: fusion-breakpoint-neoantigens.json

⛔⛔ THE COORDINATE DEFECT THIS MODULE IS A CORRECTION FOR — THREE GENERATIONS, READ ALL THREE.
  GEN 1 (the committed artifact, retracted 2026-08-03). `gene_model` returns `offsets`
  indexed by CODING exon; the windows are TRANSCRIPT exon numbers, and NR4A3's first two
  transcript exons are non-coding. `offsets[n - 2]` therefore resumed NR4A3 at transcript
  exon 5 (CDS nt 1081 = residue 361) for the label "exon 3". 7 junctions, 26 predicted
  binders, all at seams that do not exist.
  GEN 2 (`resume_offset`/`cut_offset`, 2026-08-02). Arithmetically right and still wrong,
  because `main()` built the chimera as `ews_cds[:p] + nr4_cds[q:]` — CDS onto CDS. A real
  fusion transcript retains the ACCEPTOR EXON WHOLE, 5'UTR included, and those retained
  bases are translated in the donor's frame. NR4A3 transcript exon 3 carries **U = 2** nt
  5' of its ATG, so dropping them shifts the register by 2.
  ⭐ MEASURED CONSEQUENCE, and it is not a near miss: with `q = 0`, `fp.endswith(nr4_tail)`
  reduces to `p % 3 == 0`; the correct predicate is `(p + U) % 3 == 0`, i.e. `p % 3 == 1`.
  U is not a multiple of 3, so the two predicates select **DISJOINT** residue classes of
  `p`. Run over the declared windows against the committed cache, the CDS instrument emits
  exactly {e11n3, e11n4} and the transcript model emits exactly {e7n3, e9n3, e10n3, e12n3,
  e13n3} — symmetric difference = all seven, intersection = EMPTY. The CDS instrument
  would have refused e7 and e12, the two junctions the manuscripts lead with, and admitted
  e11, which no manuscript uses. Two wrong answers, not a rounding error.
  GEN 3 (this module, 2026-08-07). Built on the transcript model throughout. U is
  MEASURED, twice over, from `emc-construct-inputs.json`: `utr5_len 699 − (exon1 523 +
  exon2 174) = 2`, and `exon3 length 953 − exon3 coding 951 = 2`.
  ⭐ AND THE SEAM CARRIES A CODON BELONGING TO NEITHER PARENT. Every in-frame junction here
  has EWSR1 ending 1 nt past a codon boundary, which composes with the 2 retained acceptor
  5'UTR nt into one novel codon, and NR4A3 Met1 follows it as an internal residue. The
  novel residue is junction-SPECIFIC (`AAT`=Asn at e7; `GAT`=Asp at e9/e10/e12/e13),
  because the leftover EWSR1 base differs — a fact no CDS-space model can express at all.

⚠ `gene_model` / `resume_offset` / `cut_offset` are RETAINED and are still correct as a
CDS/protein instrument; `fusion_neoantigen_invalidation.py`, `patient_neoepitopes.py` and
`fusion_object_inventory.py` import them. They are no longer how this module builds a
fusion, and nothing should build one from them again — see GEN 2 above.
"""

import json
import os
import sys
import time
import urllib.request

OUT = os.path.join(os.path.dirname(__file__), "fusion-breakpoint-neoantigens.json")
ENS = "https://rest.ensembl.org"

GENES = {"EWSR1": "EWSR1", "NR4A3": "NR4A3"}
# Documented breakpoint windows (1-based exon numbers in transcription order). EWSR1
# breaks in the central exons in FET fusions; NR4A3 is retained from exon 2/3 in EMC.
EWSR1_EXON_WINDOW = range(6, 15)   # ends of these EWSR1 coding exons are candidate cuts
NR4A3_EXON_WINDOW = range(2, 5)    # starts of these NR4A3 coding exons are candidate resumes

ALLELES = [
    "HLA-A*01:01", "HLA-A*02:01", "HLA-A*03:01", "HLA-A*11:01", "HLA-A*24:02",
    "HLA-B*07:02", "HLA-B*08:01", "HLA-B*15:01", "HLA-B*35:01", "HLA-B*44:02",
]
LENGTHS = [8, 9, 10, 11]
RANK_WEAK, RANK_STRONG = 2.0, 0.5

CODON = {
    'TTT':'F','TTC':'F','TTA':'L','TTG':'L','CTT':'L','CTC':'L','CTA':'L','CTG':'L',
    'ATT':'I','ATC':'I','ATA':'I','ATG':'M','GTT':'V','GTC':'V','GTA':'V','GTG':'V',
    'TCT':'S','TCC':'S','TCA':'S','TCG':'S','CCT':'P','CCC':'P','CCA':'P','CCG':'P',
    'ACT':'T','ACC':'T','ACA':'T','ACG':'T','GCT':'A','GCC':'A','GCA':'A','GCG':'A',
    'TAT':'Y','TAC':'Y','TAA':'*','TAG':'*','CAT':'H','CAC':'H','CAA':'Q','CAG':'Q',
    'AAT':'N','AAC':'N','AAA':'K','AAG':'K','GAT':'D','GAC':'D','GAA':'E','GAG':'E',
    'TGT':'C','TGC':'C','TGA':'*','TGG':'W','CGT':'R','CGC':'R','CGA':'R','CGG':'R',
    'AGT':'S','AGC':'S','AGA':'R','AGG':'R','GGT':'G','GGC':'G','GGA':'G','GGG':'G',
}


def get(url):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"Content-Type": "application/json",
                                                       "User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa
            print(f"  retry {i+1} {url}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"failed: {url}")


def get_text(url):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"Content-Type": "text/plain",
                                                       "User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode()
        except Exception as e:  # noqa
            print(f"  retry {i+1} {url}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"failed: {url}")


def translate(cds):
    aa = []
    for i in range(0, len(cds) - 2, 3):
        c = CODON.get(cds[i:i+3], 'X')
        if c == '*':
            break
        aa.append(c)
    return "".join(aa)


def gene_model(symbol):
    """Return dict: cds (str), protein (str), exon_cds_offsets (cumulative coding nt)."""
    look = get(f"{ENS}/lookup/symbol/homo_sapiens/{symbol}?expand=1")
    transcripts = look["Transcript"]
    # prefer MANE Select / canonical
    tr = None
    for t in transcripts:
        if t.get("is_canonical") == 1:
            tr = t
            break
    tr = tr or transcripts[0]
    strand = tr["strand"]
    exons = sorted(tr["Exon"], key=lambda e: e["start"], reverse=(strand == -1))
    trans = tr["Translation"]
    cds_lo, cds_hi = trans["start"], trans["end"]  # genomic, lo<hi
    cum = 0
    offsets = []       # cumulative coding nt through end of each coding-CONTAINING exon
    coding_ranks = []  # TRANSCRIPT exon rank of each entry in `offsets`, same index
    for rank, ex in enumerate(exons, start=1):
        cstart = max(ex["start"], cds_lo)
        cend = min(ex["end"], cds_hi)
        clen = max(0, cend - cstart + 1)
        if clen:
            cum += clen
            offsets.append(cum)
            coding_ranks.append(rank)
    cds = get_text(f"{ENS}/sequence/id/{tr['id']}?type=cds").replace("\n", "").upper()
    protein = get_text(f"{ENS}/sequence/id/{trans['id']}?type=protein").replace("\n", "")
    # self-checks
    assert offsets[-1] == len(cds), f"{symbol}: exon offsets {offsets[-1]} != CDS len {len(cds)}"
    tp = translate(cds)
    assert tp == protein.replace("*", "").rstrip("X"), f"{symbol}: CDS translation != Ensembl protein"
    return {"symbol": symbol, "transcript": tr["id"], "n_coding_exons": len(offsets),
            "cds": cds, "protein": protein, "offsets": offsets,
            "coding_ranks": coding_ranks, "n_transcript_exons": len(exons)}


# ⛔ CORRECTED 2026-08-02 — `offsets` is indexed by CODING exon, and the windows above are
# TRANSCRIPT exon numbers. For a gene whose leading exons are non-coding the two differ, and the
# old `offsets[e - 1]` / `offsets[n - 2]` arithmetic silently resumed at the wrong exon.
# ⚠ SUPERSEDED AS A FUSION BUILDER 2026-08-07, RETAINED AS A CDS INSTRUMENT. Fixing the index did
# not fix the coordinate system: see the module docstring, GEN 2. These helpers are still imported
# by three modules and are correct for the question they answer (where does a CODING exon start /
# end inside a CDS). They must never again be used to CONCATENATE two transcripts.
# MEASURED on the canonical transcripts (`nr4a3_exon_audit.py` -> nr4a3-exon-audit.json):
#   EWSR1 ENST00000397938 -- exon 1 IS coding, so rank == coding index and the EWSR1 half was right.
#   NR4A3 ENST00000395097 -- 8 transcript exons, **exons 1 and 2 are entirely non-coding**, so the
#   first coding exon is TRANSCRIPT EXON 3 and it encodes residues 1-317. The old index therefore
#   mapped the label "NR4A3 exon 3" onto transcript exon 5 (residue 361) -- an OFF-BY-TWO. Every
#   junction it emitted deleted NR4A3's AF1 and the first zinc finger of the C4 DBD (which opens at
#   C292), i.e. modelled a chimera that could not transactivate the PPARG response element the
#   fusion is reported to act through (Filion 2009, PMC4429309).
#   The EMC literature's "NR4A3 exon 3" is transcript exon 3, which resumes at residue 1 -- which is
#   what `fusion_cofold.py` assumed all along and what `junction_breakpoint_scan.py` brackets.
# ⚠ `fusion-breakpoint-neoantigens.json` as committed PREDATES this fix and its 7 junctions and 26
# predicted binders are at seams that do not exist. Regenerate before quoting any of them.
def resume_offset(model, transcript_exon_rank):
    """CDS nt offset at which `transcript_exon_rank` begins (0 = start of the CDS).

    Raises if the requested exon carries no coding sequence, rather than silently sliding to a
    neighbour -- the failure mode that produced the off-by-two above.
    """
    ranks = model["coding_ranks"]
    if transcript_exon_rank not in ranks:
        raise ValueError(
            f"{model['symbol']}: transcript exon {transcript_exon_rank} carries no coding "
            f"sequence (coding exons are {ranks})")
    i = ranks.index(transcript_exon_rank)
    return 0 if i == 0 else model["offsets"][i - 1]


def cut_offset(model, transcript_exon_rank):
    """CDS nt offset at which `transcript_exon_rank` ENDS (i.e. a 5'-partner cut point)."""
    ranks = model["coding_ranks"]
    if transcript_exon_rank not in ranks:
        raise ValueError(
            f"{model['symbol']}: transcript exon {transcript_exon_rank} carries no coding "
            f"sequence (coding exons are {ranks})")
    return model["offsets"][ranks.index(transcript_exon_rank)]


def junction_peptides(fusion_prot, j0, lengths, novel_residue=False):
    """All k-mers of `fusion_prot` that carry the junction. THE ONE HOME of this definition.

    `j0` is the 0-based index of the first NON-EWSR1-derived residue. If the donor cut splits a
    codon there IS a novel residue at `j0` (belonging to neither parent) and the tumour-specific
    set is every k-mer CONTAINING it — including k-mers that BEGIN at it, which the old
    left/right straddle test dropped. If the cut is codon-aligned there is no novel residue and
    the classic straddle test (>=1 residue from each side) is the right one.

    ⛔ CONSOLIDATED 2026-08-07 (rule 1). This function and `fusion_neoantigen.junction_peptides`
    were two different definitions of "junction-spanning" for the SAME seam: the corrected
    single-junction artifact counted 38 spanning peptides at EWSR1 e7 :: NR4A3 e3 and this module
    counted 34 at the identical junction, because this one required a residue strictly 5' of `j0`.
    Under the corrected model `j0` IS the novel codon, so demanding a residue before it excludes
    `NMPCVQAQY` — the single-junction artifact's own top-ranked peptide. Two artifacts about one
    seam disagreeing by four peptides is exactly the defect class this lane is a correction for,
    so there is now one definition and `fusion_neoantigen.py` imports it.
    ⚠ `novel_residue` defaults to False so any caller that has NOT graded the seam keeps the
    classic straddle behaviour rather than silently widening its own peptide set.
    """
    peps = {}
    for L in lengths:
        for start in range(max(0, j0 - L + 1), j0 + 1):
            pep = fusion_prot[start:start + L]
            if len(pep) != L:
                continue
            if novel_residue:
                peps.setdefault(pep, L)                      # contains fusion_prot[j0], the novel residue
            elif start < j0 < start + L:
                peps.setdefault(pep, L)                      # classic straddle
    return peps


def chimeric_protein(ews, junction):
    """Translate the chimeric ORF of one graded junction, starting at EWSR1's OWN ATG.

    `junction` is a `junction_aso.mrna_junction` reading built with `keep_sequences=True`, so
    `_fusion` is the chimeric mRNA — donor transcript up to the donor exon's 3' end, then the
    acceptor exon WHOLE and everything after it. The ORF opens at `ews["utr5_len"]` because the
    fusion transcript keeps the donor's own 5'UTR and initiator codon.
    """
    return translate(junction["_fusion"][ews["utr5_len"]:])


def emit_junction(ews, nr4, j):
    """Peptide-level reading for ONE junction the grader passed. Self-checks, then peptides.

    ⛔ THE SELF-CHECKS RAISE. A junction that reaches this function has already been graded
    EMITTABLE from exon arithmetic; these three checks test the SEQUENCE that arithmetic implies,
    which is a different question and the one the retracted artifact got wrong:
      · the chimeric protein's N-terminal block IS EWSR1's, residue for residue
      · it ends in NR4A3's own C-terminus (the LBD-containing last 100 aa)
      · NR4A3 Met1 survives as an internal residue immediately 3' of the seam codon
    """
    prot = chimeric_protein(ews, j)
    j0 = j["ewsr1_last_whole_residue"]            # 0-based index of the first non-pure-EWSR1 residue
    ews_prot = ews["protein"].replace("*", "").rstrip("X")
    nr4_prot = nr4["protein"].replace("*", "").rstrip("X")
    if prot[:j0] != ews_prot[:j0]:
        raise RuntimeError(f"{j['junction_label']}: chimeric N-terminus is not EWSR1's")
    if not prot.endswith(nr4_prot[-100:]):
        raise RuntimeError(f"{j['junction_label']}: NR4A3 C-terminus not retained")
    # the seam codon: present exactly when EWSR1's cut leaves a partial codon to complete
    has_novel = bool(j["ewsr1_coding_phase"])
    novel_aa = prot[j0] if has_novel else None
    nr4_first_idx = j0 + (1 if has_novel else 0)  # where NR4A3's own residue 1 lands
    if prot[nr4_first_idx] != nr4_prot[0]:
        raise RuntimeError(f"{j['junction_label']}: NR4A3 residue 1 is {prot[nr4_first_idx]!r}, "
                           f"not {nr4_prot[0]!r} — the seam register is wrong")

    peps = junction_peptides(prot, j0, LENGTHS, novel_residue=has_novel)
    novel = sorted(k for k in peps if k not in ews_prot and k not in nr4_prot)
    # ⚠ `chimeric_protein_length` already comes from the grading; do not add a second copy of it
    # under another name (rule 1). `junction_context_mRNA` likewise is the mRNA seam and stays as-is;
    # the two fields added here are the PROTEIN seam, which the mRNA one does not carry.
    row = {k: v for k, v in j.items() if not k.startswith("_")}
    assert row["chimeric_protein_length"] == len(prot)
    row.update({
        "seam_codon_residue": novel_aa,
        "seam_codon_composition": (
            f"{j['ewsr1_coding_phase']} leftover EWSR1 nt + "
            f"{j['nr4a3_acceptor_exon_5utr_nt_retained']} retained acceptor 5'UTR nt"
            if has_novel else "none — EWSR1 cuts on a codon boundary"),
        "nr4a3_met1_is_internal_residue": nr4_first_idx + 1,
        # `junction_context` keeps the key name every downstream reader already uses; the seam form
        # below is the same 21 residues with the novel codon set off, and is what the banner gate
        # compares against.
        "junction_context": prot[max(0, j0 - 10):j0] + "|" + prot[j0:j0 + 11],
        "junction_context_protein_seam": (
            prot[max(0, j0 - 10):j0] + ("-%s-" % novel_aa if has_novel else "-") +
            prot[j0 + 1:j0 + 11]),
        "n_novel_peptides": len(novel),
        "novel_peptides": novel,
    })
    return row


def superseded_cds_selection(ews_tx, nr4_tx):
    """What the SUPERSEDED CDS-concatenation model would have selected, computed here, now.

    ⛔ DERIVED, NEVER TYPED (rule 1). The docstring's central claim — that the CDS instrument and
    the transcript model select DISJOINT junction sets — is the reason this module was rebuilt, so
    it must be a reading the artifact carries and a future reader can check, not a sentence.
    Exercises the RETAINED `cut_offset`/`resume_offset` helpers over a CDS/protein model built
    from the same transcript model, so the two sides cannot drift apart on their inputs.
    """
    def cds_model(tx):
        import junction_aso as ja
        coding = ja.coding_nt_per_exon(tx)
        cum, offsets, ranks = 0, [], []
        for rank, c in enumerate(coding, start=1):
            if c:
                cum += c
                offsets.append(cum)
                ranks.append(rank)
        return {"symbol": tx["symbol"], "cds": tx["cds"],
                "protein": tx["protein"].replace("*", "").rstrip("X"),
                "offsets": offsets, "coding_ranks": ranks}

    ews, nr4 = cds_model(ews_tx), cds_model(nr4_tx)
    tail = nr4["protein"][-100:]
    selected, skipped = [], []
    for e in EWSR1_EXON_WINDOW:
        for n in NR4A3_EXON_WINDOW:
            try:
                p, q = cut_offset(ews, e), resume_offset(nr4, n)
            except ValueError as exc:
                # ⚠ The predecessor printed this to stderr and emitted NO row at all.
                skipped.append({"junction_label": f"EWSR1_e{e}__NR4A3_e{n}", "why": str(exc)})
                continue
            if translate(ews["cds"][:p] + nr4["cds"][q:]).endswith(tail):
                selected.append(f"EWSR1_e{e}__NR4A3_e{n}")
    return selected, skipped


def main():
    import junction_aso as ja                                     # transcript model, one home

    ews = ja.transcript_model("EWSR1")
    nr4 = ja.transcript_model("NR4A3")
    print(f"  EWSR1 {ews['transcript']} {ews['n_transcript_exons']} transcript exons, "
          f"{len(ews['protein'])} aa; NR4A3 {nr4['transcript']} {nr4['n_transcript_exons']} "
          f"transcript exons, {len(nr4['protein'])} aa", file=sys.stderr)

    # ⛔ EVERY DECLARED EXON PAIR GETS A GRADED ROW, refusals included. The predecessor printed a
    # non-coding acceptor to stderr and left NO row, so "considered and refused" and "never
    # considered" were indistinguishable in the artifact.
    graded = ja.graded_window(ews, nr4, keep_sequences=True)
    lo, hi = ja.plausible_nr4a3_resume_residues()
    junctions = [emit_junction(ews, nr4, j) for j in graded if j["grade"] == ja.EMITTABLE]
    grade_counts = {g: sum(1 for r in graded if r["grade"] == g)
                    for g in sorted({r["grade"] for r in graded})}
    for r in graded:
        print(f"  {r['junction_label']:<24} {r['grade']:<20} {r['why']}", file=sys.stderr)
    print(f"  {len(junctions)} EMITTABLE junctions out of {len(graded)} declared exon pairs",
          file=sys.stderr)

    utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    et = time.strftime("%Y-%m-%d %I:%M %p ET", time.gmtime(time.time() - 4 * 3600)).replace(" 0", " ")
    result = {
        "_utc": utc, "_et": et,
        "_cost": ("$0 — CPU only, no GPU and no rental. The transcript model is offline "
                  "(committed emc-construct-inputs.json) and MHCflurry runs locally."),
        "_note": "Breakpoint-resolved EWSR1::NR4A3 junction neoantigen SCREEN. Junctions derived "
                 "from the real spliced TRANSCRIPTS (no assumed breakpoint), so the acceptor exon "
                 "is retained WHOLE, 5'UTR included, as a fusion transcript does. Only junctions "
                 "graded EMITTABLE — in frame at the mRNA level AND resuming NR4A3 inside the "
                 "corrected plausible range — carry peptides. MHCflurry-2.0; "
                 "presentation_percentile<=0.5 strong, <=2 weak.",
        "⛔_what_this_is_not": (
            "PREDICTED MHC-I BINDING IS A SCREEN. It is not presentation, not immunogenicity, not "
            "efficacy, not safety and not a clinical claim. Which exon pair a given PATIENT "
            "carries is not decidable from exon structure and is not decided here."),
        "_coordinate_system": (
            "TRANSCRIPT coordinates throughout (junction_aso.transcript_model / mrna_junction). "
            "The superseded CDS-concatenation model dropped the acceptor exon's retained 5'UTR "
            "and therefore selected a DISJOINT junction set — see fusion_breakpoints.py's "
            "docstring, GEN 1/2/3."),
        "_transcript_source": ja.transcript_source_provenance(),
        "EWSR1": {"transcript": ews["transcript"], "length": len(ews["protein"])},
        "NR4A3": {"transcript": nr4["transcript"], "length": len(nr4["protein"])},
        "windows": {"EWSR1_exons": list(EWSR1_EXON_WINDOW), "NR4A3_exons": list(NR4A3_EXON_WINDOW)},
        "plausible_nr4a3_resume_range": [lo, hi],
        "_plausible_range_source": ("fusion-object-inventory.json -> reactive_residue_inventory."
                                    "excluded_span.nr4a3_resume_range_across_plausible_breakpoints "
                                    "(read at run time, never re-typed)"),
        "n_candidate_exon_pairs": len(graded),
        "grade_counts": grade_counts,
        "junctions_graded": [{k: v for k, v in r.items() if not k.startswith("_")} for r in graded],
        "n_inframe_junctions": len(junctions),
        "junctions": junctions,
    }

    # The diagnosis, as a READING taken at run time rather than a sentence in a docstring.
    cds_sel, cds_skipped = superseded_cds_selection(ews, nr4)
    tx_sel = [r["junction_label"] for r in junctions]
    result["_superseded_cds_model_comparison"] = {
        "what": ("what the pre-2026-08-07 CDS-concatenation builder (`ews_cds[:p] + nr4_cds[q:]`, "
                 "in-frame test `translate(...).endswith(NR4A3[-100:])`) selects, computed HERE "
                 "from the same transcript model so the two sides cannot differ on their inputs"),
        "cds_model_selects": cds_sel,
        "transcript_model_selects": tx_sel,
        "intersection": sorted(set(cds_sel) & set(tx_sel)),
        "sets_are_disjoint": not (set(cds_sel) & set(tx_sel)),
        "why_disjoint": (
            "with the acceptor's 5'UTR discarded the predicate reduces to (EWSR1 coding nt) mod 3 "
            "== 0; retaining it makes the predicate (EWSR1 coding nt + acceptor 5'UTR) mod 3 == 0. "
            "NR4A3 transcript exon 3 retains 2 nt, and 2 is not a multiple of 3, so the two "
            "predicates select different residue classes of the cut offset and can share nothing."),
        "exon_pairs_the_cds_model_dropped_without_a_row": cds_skipped,
        "⚠_this_is_not_the_committed_retracted_artifact": (
            "the retracted artifact predates even that builder — it used the CODING-exon index "
            "(`offsets[n-2]`), so it carries a THIRD junction set again. Its grading has its one "
            "home in fusion-neoantigen-retraction.json."),
    }

    # ⛔ NO MHCflurry ⇒ NO WRITE. This artifact is under retraction, and the only thing that lifts
    # the banner is a re-derivation gate that checks BOTH the seams and the predictions
    # (`fusion_neoantigen_invalidation.breakpoint_banner`). Emitting a junctions-only file here
    # would replace a bannered artifact with an unscreened one that still fails the gate — a
    # strictly worse state than leaving the retracted file alone, and it would look like progress.
    try:
        import mhcflurry
        from mhcflurry import Class1PresentationPredictor
    except ImportError:
        raise SystemExit(
            "REFUSED: MHCflurry is not importable, so no predictions can be produced. This "
            "artifact is under retraction and is NOT overwritten with a junctions-only file. "
            "Install mhcflurry (pip) or run this on a runner that has it, then re-run.")

    predictor = Class1PresentationPredictor.load()
    from mhcflurry.downloads import get_current_release
    result["_predictor"] = {
        "tool": "MHCflurry", "version": mhcflurry.__version__,
        "models_release": get_current_release(),
        "alleles": list(ALLELES), "peptide_lengths": list(LENGTHS),
        "thresholds": {"strong_presentation_percentile": RANK_STRONG,
                       "weak_presentation_percentile": RANK_WEAK},
        "⛔": "a percentile is a SCREEN rank, not a statement that a peptide is presented",
    }
    all_peps = sorted({p for jn in junctions for p in jn["novel_peptides"]})
    if not all_peps:
        result["predicted_binders_ranked"] = []
        result["n_distinct_binders"] = 0
        _write(result)
        return
    df = predictor.predict(peptides=all_peps, alleles={a: [a] for a in ALLELES}, verbose=0)
    cols = list(df.columns)
    rank_col = "presentation_percentile" if "presentation_percentile" in cols else "affinity_percentile"
    result["_rank_column_used"] = rank_col
    # best presentation per peptide (across alleles)
    best = {}
    for _, row in df.iterrows():
        pep = row["peptide"]; rank = float(row[rank_col]); aff = float(row["affinity"])
        if pep not in best or rank < best[pep]["presentation_percentile"]:
            best[pep] = {"peptide": pep, "allele": row["best_allele"],
                         "affinity_nM": round(aff, 1), "presentation_percentile": round(rank, 4),
                         "presentation_score": round(float(row.get("presentation_score", 0)), 3),
                         "class": "strong" if rank <= RANK_STRONG else ("weak" if rank <= RANK_WEAK else "non-binder")}
    # attach binders per junction + count how many junctions each binder spans (robustness)
    pep_junction_count = {}
    for jn in junctions:
        jb = [best[p] for p in jn["novel_peptides"] if best[p]["class"] != "non-binder"]
        jb.sort(key=lambda b: b["presentation_percentile"])
        jn["binders"] = jb
        jn["n_binders"] = len(jb)
        for p in jn["novel_peptides"]:
            if best[p]["class"] != "non-binder":
                pep_junction_count[p] = pep_junction_count.get(p, 0) + 1
    robust = sorted(({**best[p], "in_n_junctions": c} for p, c in pep_junction_count.items()),
                    key=lambda b: (-b["in_n_junctions"], b["presentation_percentile"]))
    result["predicted_binders_ranked"] = robust
    result["n_distinct_binders"] = len(robust)
    _write(result)


def _write(result):
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    slim = {k: v for k, v in result.items() if k not in ("junctions", "junctions_graded")}
    print(json.dumps(slim, indent=2, ensure_ascii=False)[:3500])


if __name__ == "__main__":
    main()
