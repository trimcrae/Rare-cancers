#!/usr/bin/env python3
"""
Fusion-junction neoantigen prediction for EWSR1::NR4A3 EMC.

Rationale. EMC is driven by an in-frame gene fusion and otherwise has a "quiet"
genome (few/no recurrent secondary mutations). That means the tumour's most
tumour-specific protein feature is the *fusion junction itself*: the short stretch
of amino acids that spans the seam between the EWSR1-derived and NR4A3-derived
portions is a sequence that exists in no normal protein. If junction-spanning
peptides can be presented on MHC-I, they are public-ish, truly tumour-specific
neoantigens — a rational basis for a fusion-directed vaccine or TCR-T, and a
modality that does NOT require drugging the (likely undruggable) oncoprotein.

What this does (real, reproducible — no invented sequences):
  1. Builds the canonical EWSR1 and NR4A3 TRANSCRIPT models (spliced cDNA, CDS,
     protein, per-exon lengths, 5'UTR length) via `junction_aso.transcript_model`,
     which reads Ensembl or the committed `emc-construct-inputs.json` and gates
     either against `nr4a3-exon-audit.json`. ⚠ Superseded, retained: "Fetches the
     canonical EWSR1 (Q01844) and NR4A3 (Q92570) protein sequences from UniProt" —
     two protein sequences are exactly what could not represent this junction.
  2. Constructs the in-frame chimera at a graded mRNA EXON junction (default
     EWSR1 transcript exon 7 :: NR4A3 transcript exon 3). Which exon pair a given
     patient carries is not decidable from exon structure and is not decided here;
     the pipeline accepts any pair, so a sequenced patient breakpoint drops in.
     ⚠ Superseded, retained: "a modelled breakpoint … FLAG it as an assumption."
  3. Enumerates every 8-, 9-, 10- and 11-mer carrying the junction — see the
     redefinition in point 2 of the ⛔ block below. ⚠ Superseded, retained:
     "that *spans* the junction (i.e. uses >=1 residue from each side)".
  4. Verifies each spanning peptide is absent from both parent proteins (true
     neo-sequence, not coincidentally present in EWSR1 or NR4A3).
  5. Predicts MHC-I binding with MHCflurry-2.0 across a panel of common HLA-A/-B
     alleles; reports predicted binders (%rank <= 2 strong/weak by netMHC-style
     convention) and affinities.

⛔⛔ THE MODELLED BREAKPOINT ABOVE IS RETIRED — THE CHIMERA IS NOW BUILT FROM THE mRNA JUNCTION
(2026-08-06). Read this before touching anything below.

The retracted `fusion-neoantigen-predictions.json` modelled `EWSR1(1-264) :: NR4A3(2-626)`: it
concatenated two UniProt PROTEIN sequences and started NR4A3 at residue 2. Its own retraction
banner graded the error as ONE residue — NR4A3's initiator Met1, dropped — and declared the
question of whether Met1 survives to be an unresolved splice-PHASE question.

⭐ IT IS RESOLVED, IT COST $0, AND IT IS TWO RESIDUES, NOT ONE. Measured from committed data
(`emc-construct-inputs.json`, cross-checked against `nr4a3-exon-audit.json`; no network):
NR4A3 transcript exon 3 begins at cDNA nt 697 and the ATG at 699, so a fusion transcript that
retains exon 3 whole carries exactly **U = 2** acceptor 5'UTR bases ahead of NR4A3's own ATG.
EWSR1 exon 7 ends at coding nt 793 = 264 whole residues + 1 nt. Those compose: (793 + 2) % 3 == 0,
so the chimeric ORF is in frame AND the leftover EWSR1 nucleotide plus the two retained UTR
nucleotides form a **novel codon that belongs to neither parent**. At e7::e3 that codon is `AAT`
= Asn. The corrected seam therefore reads

    ... S Q Q S S S Y G Q Q | N | M P C V Q A Q Y S P ...
        ^ EWSR1 1-264         ^ novel  ^ NR4A3 1-626

against the retracted artifact's `...SQQSSSYGQQ | PCVQAQYSPS...`. Every junction-spanning peptide
differs, and the retracted lead 10-mer `GQQPCVQAQY` does not occur in the corrected chimera at all.

Two consequences for the code below, both load-bearing:
  1. The chimera is built from the TRANSCRIPT (`junction_aso.transcript_model` +
     `junction_aso.mrna_junction`), never from two protein sequences — a protein-level splice
     cannot represent a codon split across the junction, so it CANNOT produce the novel residue.
  2. "Junction-spanning" is redefined as "contains the novel junction residue". The old
     left/right straddle test silently excluded peptides that begin AT the novel residue
     (`NMPCVQAQY` and friends), which are as tumour-specific as any peptide the old test kept.
     When a cut IS codon-aligned there is no novel residue and the classic straddle test applies;
     both cases are labelled in the output rather than conflated.

Output: fusion-neoantigen-predictions.json
"""

import json
import os
import sys


OUT = os.path.join(os.path.dirname(__file__), "fusion-neoantigen-predictions.json")

EWSR1 = "Q01844"
NR4A3 = "Q92570"

# The exon junction the chimera is built at. Defaults to the canonical EMC junction, EWSR1
# transcript exon 7 :: NR4A3 transcript exon 3 — the junction the retracted artifact was
# modelling when it wrote "EWSR1 kept to residue 264". TRANSCRIPT exon ranks, not coding-exon
# ranks; `junction_aso` refuses rather than slides if the acceptor carries no CDS.
EWSR1_EXON_END = int(os.environ.get("EWSR1_EXON_END") or 7)
NR4A3_EXON_START = int(os.environ.get("NR4A3_EXON_START") or 3)

# ⚠ SUPERSEDED, RETAINED (the values the retracted artifact was built on; do not reintroduce).
# EWSR1_KEEP_TO = 264 protein residues :: NR4A3_KEEP_FROM = 2. The EWSR1 half was right; 264 is
# still where the corrected chimera's EWSR1-derived stretch ends. What was wrong is everything
# from there on: no novel junction codon, and NR4A3 resumed at 2 instead of 1.
SUPERSEDED_PROTEIN_MODEL = {"EWSR1_KEEP_TO": 264, "NR4A3_KEEP_FROM": 2}

# Common HLA-I alleles (high global frequency) — MHCflurry-supported names.
ALLELES = [
    "HLA-A*01:01", "HLA-A*02:01", "HLA-A*03:01", "HLA-A*11:01", "HLA-A*24:02",
    "HLA-B*07:02", "HLA-B*08:01", "HLA-B*15:01", "HLA-B*35:01", "HLA-B*44:02",
]
LENGTHS = [8, 9, 10, 11]
RANK_WEAK = 2.0      # %rank <= 2 : weak binder (netMHCpan convention)
RANK_STRONG = 0.5    # %rank <= 0.5 : strong binder



def junction_peptides(fusion, j0, lengths, novel_residue):
    """All k-mers of `fusion` that carry the junction. ⛔ DELEGATES — see the one home.

    ⛔ MOVED TO `fusion_breakpoints.junction_peptides` 2026-08-07 (rule 1). The identical concept
    lived here AND in `fusion_breakpoints.py` with two DIFFERENT definitions, and the two
    artifacts about the same EWSR1 e7 :: NR4A3 e3 seam disagreed by four peptides because of it —
    the breakpoint panel dropped every k-mer beginning at the novel residue, including this
    module's own top-ranked `NMPCVQAQY`. This wrapper is kept so the call site reads unchanged and
    so nothing can reintroduce a private copy without deleting this comment first.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fusion_breakpoints as fb                           # type: ignore
    return fb.junction_peptides(fusion, j0, lengths, novel_residue=bool(novel_residue))


def build_chimera():
    """Build the chimeric protein at the graded mRNA exon junction. Returns a measured dict.

    Delegates to `junction_aso`, which owns the transcript model, the four self-checks and the
    `nr4a3-exon-audit.json` provenance gate — one home for the junction arithmetic, so this
    module cannot drift from the ASO lane's seam again. `junction_aso` RAISES rather than emits
    on a non-coding acceptor, a resume residue outside the corrected plausible range, or an
    out-of-frame register, so reaching the return statement is itself a grading.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import junction_aso as ja                                 # type: ignore
    import fusion_breakpoints as fb                           # type: ignore
    ews = ja.transcript_model("EWSR1")
    nr4 = ja.transcript_model("NR4A3")
    j = ja.mrna_junction(ews, nr4, EWSR1_EXON_END, NR4A3_EXON_START)
    if not j["nr4a3_acceptor_exon_is_coding"]:
        raise RuntimeError(f"NR4A3 transcript exon {NR4A3_EXON_START} carries no coding sequence")
    lo, hi = ja.plausible_nr4a3_resume_residues()
    if not (lo <= j["nr4a3_first_residue"] <= hi):
        raise RuntimeError(f"NR4A3 resumes at residue {j['nr4a3_first_residue']}, outside the "
                           f"corrected plausible range [{lo}, {hi}] — SEAM_NOT_PRODUCED")
    if not j["in_frame"]:
        raise RuntimeError(f"EWSR1 e{EWSR1_EXON_END} :: NR4A3 e{NR4A3_EXON_START} is not in frame "
                           f"((cut+acceptor 5'UTR) mod 3 = {j['frame_sum_mod3']}, must be 0)")
    prot = fb.translate(j["_fusion"][ews["utr5_len"]:])
    j0 = j["ewsr1_last_whole_residue"]                        # 0-based index of the first non-EWSR1 residue
    novel = j["ewsr1_coding_phase"] != 0                      # a split codon => a residue from neither parent
    if not prot.endswith(nr4["protein"][-30:]):               # belt-and-braces on top of in_frame
        raise RuntimeError("chimeric ORF does not end in the NR4A3 C-terminus")
    return {"chimera": prot, "j0": j0, "novel_residue": novel,
            "novel_residue_aa": prot[j0] if novel else None,
            "ews_parent": ews["protein"], "nr4_parent": nr4["protein"],
            "grading": {k: v for k, v in j.items() if not k.startswith("_")},
            "transcript_source": ja.transcript_source_provenance()}


def main():
    b = build_chimera()
    fusion, j0 = b["chimera"], b["j0"]
    ews, nr4 = b["ews_parent"], b["nr4_parent"]

    span = junction_peptides(fusion, j0, LENGTHS, b["novel_residue"])

    # novelty filter: a junction peptide must not occur in either parent protein
    novel = {p: L for p, L in span.items() if p not in ews and p not in nr4}

    g = b["grading"]
    result = {
        "_note": "MHC-I binding of EWSR1::NR4A3 junction peptides (MHCflurry-2.0). "
                 "%rank<=0.5 strong, <=2 weak (netMHC convention).",
        "_scope": "Sequence composition and predicted MHC-I binding only. Predicted binding is a "
                  "screen, not presentation and not immunogenicity; no efficacy, safety, "
                  "tolerability or clinical claim is made or implied.",
        "_supersedes": {
            "retracted_model": "EWSR1(1-264)::NR4A3(2-626), two UniProt protein sequences "
                               "concatenated (see SUPERSEDED_PROTEIN_MODEL in this module)",
            "why": "a protein-level splice cannot represent a codon split across the junction, so "
                   "it produced neither the novel junction residue nor NR4A3 Met1",
        },
        "_breakpoint_model": {
            "assumption": False,
            "junction_label": g["junction_label"],
            "built_from": "spliced transcript (junction_aso.transcript_model + mrna_junction)",
            "EWSR1_kept_residues": f"1-{g['ewsr1_last_whole_residue']} (UniProt {EWSR1})",
            "NR4A3_kept_residues": f"{g['nr4a3_first_residue']}-{len(nr4)} (UniProt {NR4A3})",
            "novel_junction_residue": b["novel_residue_aa"],
            "novel_junction_residue_origin": (
                f"{3 - g['ewsr1_coding_phase']} nt would be needed to complete EWSR1's last codon; "
                f"EWSR1 contributes {g['ewsr1_coding_phase']} nt past residue "
                f"{g['ewsr1_last_whole_residue']} and NR4A3's acceptor exon contributes "
                f"{g['nr4a3_acceptor_exon_5utr_nt_retained']} retained 5'UTR nt"
                if b["novel_residue"] else None),
            "caveat": "Which exon pair a given patient carries is not decidable from exon "
                      "structure and is not decided here; re-run with a sequenced breakpoint for "
                      "patient-specific peptides.",
            "junction_context_left10": fusion[max(0, j0 - 10):j0],
            "junction_context_right10": fusion[j0:j0 + 10],
            "measured_junction": g,
            "_transcript_source": b["transcript_source"],
        },
        "_spanning_definition": ("every k-mer containing the novel junction residue"
                                 if b["novel_residue"] else
                                 "every k-mer using >=1 residue from each parent (codon-aligned "
                                 "cut, so there is no novel junction residue)"),
        "n_spanning_peptides": len(span),
        "n_novel_spanning_peptides": len(novel),
        "alleles": ALLELES,
        "lengths": LENGTHS,
    }

    try:
        from mhcflurry import Class1PresentationPredictor
    except ImportError:
        print("  mhcflurry not installed; emitting peptides only", file=sys.stderr)
        result["binders"] = None
        result["novel_peptides"] = sorted(novel)
        _write(result)
        return

    predictor = Class1PresentationPredictor.load()
    # Predictor provenance, for the same reason `_rank_column_used` is recorded: a percentile is
    # only comparable against another run of the SAME predictor and the SAME model release, and a
    # rerun that silently picks up a different release would move every number in this file with
    # nothing in it saying so.
    import mhcflurry as _mf
    from mhcflurry.downloads import get_default_class1_presentation_models_dir
    _models_dir = get_default_class1_presentation_models_dir()
    result["_where_this_ran"] = (
        f"GitHub Actions run {os.environ['GITHUB_RUN_ID']} ({os.environ.get('GITHUB_WORKFLOW')})"
        if os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_RUN_ID")
        else "a local CPU (no GPU, no rental) — $0")
    result["_predictor"] = {
        "package": "mhcflurry", "version": getattr(_mf, "__version__", None),
        # The release string mhcflurry keys its downloads by (…/mhcflurry/<n>/<release>/<name>/…) —
        # the thing that actually pins which weights produced these percentiles.
        "downloads_release": next((p for p in reversed(os.path.normpath(_models_dir).split(os.sep))
                                   if p and p[0].isdigit() and "." in p), None),
        "models_dir": _models_dir,
    }
    peptides = sorted(novel)
    df = predictor.predict(
        peptides=peptides,
        alleles={a: [a] for a in ALLELES},
        verbose=0,
    )
    # Class1PresentationPredictor.predict columns (this MHCflurry build):
    #   peptide, peptide_num, sample_name, affinity, best_allele,
    #   processing_score, presentation_score, presentation_percentile
    # There is NO 'affinity_percentile' column here — rank on presentation_percentile
    # (lower = better presented); also report raw affinity (nM). We pick the rank column
    # defensively and record which was used (provenance against silent-default artifacts).
    cols = list(df.columns)
    result["_mhcflurry_columns"] = cols
    rank_col = ("presentation_percentile" if "presentation_percentile" in cols
                else "affinity_percentile" if "affinity_percentile" in cols else None)
    result["_rank_column_used"] = rank_col
    if rank_col is None:
        raise RuntimeError(f"no percentile column in MHCflurry output: {cols}")

    # Binding thresholds: percentile (netMHC-style) AND raw affinity (nM) as a cross-check.
    AFF_STRONG, AFF_WEAK = 50.0, 500.0  # nM, standard MHC-I binding cutoffs
    rows = []
    for _, row in df.iterrows():
        rank = float(row[rank_col])
        aff = float(row["affinity"])
        by_rank = "strong" if rank <= RANK_STRONG else ("weak" if rank <= RANK_WEAK else "non-binder")
        by_aff = "strong" if aff <= AFF_STRONG else ("weak" if aff <= AFF_WEAK else "non-binder")
        rows.append({
            "peptide": row["peptide"],
            "allele": row["best_allele"],
            "affinity_nM": round(aff, 1),
            "presentation_percentile": round(rank, 4),
            "presentation_score": round(float(row.get("presentation_score", 0)), 3),
            "class_by_percentile": by_rank,
            "class_by_affinity": by_aff,
        })
    rows.sort(key=lambda b: b["presentation_percentile"])
    binders = [r for r in rows if r["class_by_percentile"] != "non-binder"]
    aff_binders = [r for r in rows if r["class_by_affinity"] != "non-binder"]
    result["n_predicted_binders_by_percentile"] = len(binders)
    result["n_strong_binders_by_percentile"] = sum(1 for b in binders if b["class_by_percentile"] == "strong")
    result["n_predicted_binders_by_affinity_500nM"] = len(aff_binders)
    result["best_presentation_percentile"] = rows[0]["presentation_percentile"] if rows else None
    result["best_affinity_nM"] = min((r["affinity_nM"] for r in rows), default=None)
    result["top_predictions"] = rows[:12]
    result["binders"] = binders
    _write(result)


def _write(result):
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    skip = {"binders"}
    print(json.dumps({k: v for k, v in result.items() if k not in skip}, indent=2))


if __name__ == "__main__":
    main()
