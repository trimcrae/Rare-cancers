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
  1. Fetches the canonical EWSR1 (Q01844) and NR4A3 (Q92570) protein sequences
     from UniProt.
  2. Constructs an in-frame fusion at a modelled breakpoint (EWSR1 N-terminal
     transactivation fragment :: retained NR4A3). The exact junction residue is
     patient/transcript specific; we model the canonical fusion and FLAG it as an
     assumption. The pipeline accepts any breakpoint, so a sequenced patient
     breakpoint can be dropped in.
  3. Enumerates every 8-, 9-, 10- and 11-mer that *spans* the junction (i.e. uses
     >=1 residue from each side — these are the genuinely novel sequences).
  4. Verifies each spanning peptide is absent from both parent proteins (true
     neo-sequence, not coincidentally present in EWSR1 or NR4A3).
  5. Predicts MHC-I binding with MHCflurry-2.0 across a panel of common HLA-A/-B
     alleles; reports predicted binders (%rank <= 2 strong/weak by netMHC-style
     convention) and affinities.

Output: fusion-neoantigen-predictions.json
"""

import json
import os
import sys
import urllib.request

OUT = os.path.join(os.path.dirname(__file__), "fusion-neoantigen-predictions.json")

EWSR1 = "Q01844"
NR4A3 = "Q92570"

# --- modelled breakpoint (see docstring; this is an assumption, flagged in output) ---
# EWSR1 N-terminal transactivation fragment retained up to (and incl.) this residue.
# ~264 is the SYGQ-rich/exon-7 boundary commonly involved in EWSR1 fusions; cited in MS.
EWSR1_KEEP_TO = 264
# NR4A3 retained from this residue onward (keeps DBD+LBD). Modelled as near-full-length.
NR4A3_KEEP_FROM = 2

# Common HLA-I alleles (high global frequency) — MHCflurry-supported names.
ALLELES = [
    "HLA-A*01:01", "HLA-A*02:01", "HLA-A*03:01", "HLA-A*11:01", "HLA-A*24:02",
    "HLA-B*07:02", "HLA-B*08:01", "HLA-B*15:01", "HLA-B*35:01", "HLA-B*44:02",
]
LENGTHS = [8, 9, 10, 11]
RANK_WEAK = 2.0      # %rank <= 2 : weak binder (netMHCpan convention)
RANK_STRONG = 0.5    # %rank <= 0.5 : strong binder


def fetch_fasta(acc):
    url = f"https://rest.uniprot.org/uniprotkb/{acc}.fasta"
    print(f"  fetching {url}", file=sys.stderr)
    with urllib.request.urlopen(url) as r:
        text = r.read().decode()
    seq = "".join(l.strip() for l in text.splitlines() if not l.startswith(">"))
    return seq


def junction_peptides(left, right, lengths):
    """All k-mers spanning the seam between `left` (ends at junction) and `right`."""
    fusion = left + right
    j = len(left)  # index of first right-residue in the fused string
    peps = {}
    for L in lengths:
        for start in range(max(0, j - L + 1), j):
            pep = fusion[start:start + L]
            if len(pep) == L and start < j < start + L:
                # spans: uses left[start:j] and right[0:start+L-j]
                peps.setdefault(pep, L)
    return peps


def main():
    ews = fetch_fasta(EWSR1)
    nr4 = fetch_fasta(NR4A3)
    left = ews[:EWSR1_KEEP_TO]
    right = nr4[NR4A3_KEEP_FROM - 1:]

    span = junction_peptides(left, right, LENGTHS)

    # novelty filter: spanning peptide must not occur in either parent
    novel = {p: L for p, L in span.items() if p not in ews and p not in nr4}

    result = {
        "_note": "MHC-I binding of EWSR1::NR4A3 junction-spanning peptides "
                 "(MHCflurry-2.0). %rank<=0.5 strong, <=2 weak (netMHC convention).",
        "_breakpoint_model": {
            "assumption": True,
            "EWSR1_kept_residues": f"1-{EWSR1_KEEP_TO} (UniProt {EWSR1})",
            "NR4A3_kept_residues": f"{NR4A3_KEEP_FROM}-{len(nr4)} (UniProt {NR4A3})",
            "caveat": "Exact junction residue is transcript/patient specific; this "
                      "models the canonical fusion. Re-run with a sequenced breakpoint "
                      "to get patient-specific epitopes.",
            "junction_context_left10": left[-10:],
            "junction_context_right10": right[:10],
        },
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
    peptides = sorted(novel)
    df = predictor.predict(
        peptides=peptides,
        alleles={a: [a] for a in ALLELES},
        verbose=0,
    )
    # df columns: peptide, peptide_num, sample_name, affinity, best_allele,
    #             affinity_percentile, processing_score, presentation_score, presentation_percentile
    result["_mhcflurry_columns"] = list(df.columns)  # provenance: confirm the percentile col exists
    rows = []
    for _, row in df.iterrows():
        rank = float(row.get("affinity_percentile", 100.0))
        rows.append({
            "peptide": row["peptide"],
            "allele": row["best_allele"],
            "affinity_nM": round(float(row["affinity"]), 1),
            "affinity_percentile": round(rank, 3),
            "presentation_score": round(float(row.get("presentation_score", 0)), 3),
            "class": "strong" if rank <= RANK_STRONG else ("weak" if rank <= RANK_WEAK else "non-binder"),
        })
    rows.sort(key=lambda b: b["affinity_percentile"])
    binders = [r for r in rows if r["affinity_percentile"] <= RANK_WEAK]
    result["n_predicted_binders"] = len(binders)
    result["n_strong_binders"] = sum(1 for b in binders if b["class"] == "strong")
    # Always report the best predictions even if none pass threshold, so a NEGATIVE
    # result is concrete and verifiable (rules out a silent percentile-default artifact).
    result["best_affinity_percentile"] = rows[0]["affinity_percentile"] if rows else None
    result["best_affinity_nM"] = rows[0]["affinity_nM"] if rows else None
    result["top_predictions_any_rank"] = rows[:10]
    result["binders"] = binders
    _write(result)


def _write(result):
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    skip = {"binders", "top_predictions_any_rank"}
    print(json.dumps({k: v for k, v in result.items() if k not in skip}, indent=2))


if __name__ == "__main__":
    main()
