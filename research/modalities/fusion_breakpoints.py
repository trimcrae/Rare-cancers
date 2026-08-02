#!/usr/bin/env python3
"""
Breakpoint-resolved fusion-junction neoantigen analysis for EWSR1::NR4A3 EMC.

WHY. The earlier neoantigen result (`fusion_neoantigen.py`) used ONE modelled junction
(EWSR1 kept to residue 264 :: NR4A3 from residue 2) — an assumption, not a sourced
breakpoint. The lead epitope GQQPCVQAQY spans that guessed seam, so it could be an
artifact of the guess. This script removes the guess: it derives the *real* set of
in-frame EWSR1::NR4A3 junctions from actual exon structure and asks whether any predicted
neoepitope is robust across breakpoints.

HOW (all real, fetched from Ensembl; no invented sequence or breakpoint).
  1. For EWSR1 and NR4A3, fetch the MANE/canonical transcript (exons + CDS + protein)
     from the Ensembl REST API and compute the cumulative coding-nucleotide offset at
     every exon boundary. Self-check: translate(CDS) must equal the Ensembl protein and
     the offsets must sum to the CDS length (asserts the exon mapping is correct).
  2. Enumerate candidate fusions = (EWSR1 cut at the coding end of exon e) :: (NR4A3
     resumed at the coding start of exon n), over the documented breakpoint windows
     (EWSR1 exons ~6-14, NR4A3 exons 2-4 — the FET-fusion / EMC literature). Working at
     the *nucleotide* level makes the reading frame exact.
  3. Keep only biologically valid, in-frame fusions: the chimeric protein must retain an
     intact NR4A3 C-terminus (its last 100 aa, which include the ligand-binding domain).
     This filter handles exon phase automatically, regardless of UTRs/phase.
  4. For each valid junction, take junction-spanning 8-11mers absent from both parents
     and predict MHC-I binding with MHCflurry-2.0 across common HLA-A/-B alleles.
  5. Report, per junction, the lead epitopes; and ACROSS junctions, which epitopes recur
     (robust) vs. are breakpoint-specific.

Output: fusion-breakpoint-neoantigens.json
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


def junction_peptides(fusion_prot, j, lengths):
    peps = {}
    for L in lengths:
        for start in range(max(0, j - L + 1), j):
            pep = fusion_prot[start:start + L]
            if len(pep) == L and start < j < start + L:
                peps[pep] = L
    return peps


def main():
    ews = gene_model("EWSR1")
    nr4 = gene_model("NR4A3")
    print(f"  EWSR1 {ews['transcript']} {ews['n_coding_exons']} coding exons, "
          f"{len(ews['protein'])} aa; NR4A3 {nr4['transcript']} {nr4['n_coding_exons']} "
          f"coding exons, {len(nr4['protein'])} aa", file=sys.stderr)

    nr4_tail = nr4["protein"][-100:]  # LBD-containing C-terminus; intact => in-frame
    ews_cds, nr4_cds = ews["cds"], nr4["cds"]

    # Candidate cut/resume nucleotide offsets, addressed by TRANSCRIPT exon rank (see the
    # corrected helpers above). A window entry that names a non-coding exon is skipped loudly
    # rather than sliding onto a neighbour.
    ews_cuts = []
    for e in EWSR1_EXON_WINDOW:
        try:
            ews_cuts.append((e, cut_offset(ews, e)))
        except ValueError as exc:
            print(f"  skip EWSR1 exon {e}: {exc}", file=sys.stderr)
    nr4_resumes = []
    for n in NR4A3_EXON_WINDOW:
        try:
            nr4_resumes.append((n, resume_offset(nr4, n)))
        except ValueError as exc:
            print(f"  skip NR4A3 exon {n}: {exc}", file=sys.stderr)
    # Regression guard for the off-by-two: the resume point of the exon the EMC literature names
    # must land inside NR4A3's own N-terminus, not past its DNA-binding domain.
    for n, q in nr4_resumes:
        print(f"  NR4A3 exon {n} resumes at CDS nt {q} = residue {q // 3 + 1}", file=sys.stderr)
    assert any(q // 3 + 1 <= 2 for _, q in nr4_resumes), (
        "NR4A3 resume window no longer contains a junction that retains the DBD - the exon "
        "index is wrong again (see nr4a3-exon-audit.json)")

    junctions = []
    for e, p in ews_cuts:
        for n, q in nr4_resumes:
            fusion_cds = ews_cds[:p] + nr4_cds[q:]
            fp = translate(fusion_cds)
            if not fp.endswith(nr4_tail):
                continue  # not in-frame / NR4A3 C-terminus not intact
            j = p // 3  # approx seam residue (peptides span it)
            peps = junction_peptides(fp, j, LENGTHS)
            novel = {k: v for k, v in peps.items()
                     if k not in ews["protein"] and k not in nr4["protein"]}
            junctions.append({
                "EWSR1_exon_end": e, "NR4A3_exon_start": n,
                "ews_cds_nt": p, "nr4_cds_nt": q,
                "junction_context": fp[max(0, j-6):j] + "|" + fp[j:j+6],
                "n_novel_peptides": len(novel),
                "novel_peptides": sorted(novel),
            })
    print(f"  {len(junctions)} in-frame junctions from "
          f"{len(ews_cuts)}x{len(nr4_resumes)} candidate exon pairs", file=sys.stderr)

    result = {
        "_note": "Breakpoint-resolved EWSR1::NR4A3 junction neoantigens. Junctions derived "
                 "from real Ensembl exon structure (no assumed breakpoint); only in-frame "
                 "fusions with an intact NR4A3 C-terminus are kept. MHCflurry-2.0; "
                 "presentation_percentile<=0.5 strong, <=2 weak.",
        "EWSR1": {"transcript": ews["transcript"], "length": len(ews["protein"])},
        "NR4A3": {"transcript": nr4["transcript"], "length": len(nr4["protein"])},
        "windows": {"EWSR1_exons": list(EWSR1_EXON_WINDOW), "NR4A3_exons": list(NR4A3_EXON_WINDOW)},
        "n_inframe_junctions": len(junctions),
        "junctions": junctions,
    }

    try:
        from mhcflurry import Class1PresentationPredictor
    except ImportError:
        print("  mhcflurry missing; emitting junctions only", file=sys.stderr)
        _write(result)
        return

    predictor = Class1PresentationPredictor.load()
    all_peps = sorted({p for jn in junctions for p in jn["novel_peptides"]})
    if not all_peps:
        result["binders"] = []
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
    slim = {k: v for k, v in result.items() if k not in ("junctions",)}
    print(json.dumps(slim, indent=2)[:3000])


if __name__ == "__main__":
    main()
