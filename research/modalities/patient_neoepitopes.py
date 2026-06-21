#!/usr/bin/env python3
"""
patient_neoepitopes.py — per-patient EWSR1::NR4A3 fusion-neoepitope shortlister.

Purpose: turn one EMC patient's *own* fusion breakpoint + HLA type into a ranked list of
candidate junction neoepitopes for a personalised peptide/mRNA vaccine or TCR-T. This is
the clinically-actionable form of the breakpoint-resolved analysis: the population study
(`fusion_breakpoints.py`) showed there is no off-the-shelf EMC epitope, so the target must
be generated per patient — which is exactly what this does.

NOT a medical device and NOT clinical advice. It is a hypothesis-generator: predicted MHC
binding is a screen, not proof of immunogenicity; every candidate needs wet-lab
confirmation (immunopeptidomics + T-cell reactivity) before any clinical use.

Inputs (you need two things a modern sarcoma work-up already produces):
  1. The fusion junction, EITHER:
       --junction-seq "LEFTAAS|RIGHTAAS"   protein context around the seam ('|' = junction),
                                            e.g. straight from an RNA-seq fusion report; OR
       --ewsr1-exon E --nr4a3-exon N        the exon junction (uses Ensembl, like the
                                            population analysis).
  2. --hla "A*02:01,A*11:01,B*07:02,B*08:01"   the patient's HLA class-I genotype.

Output: a ranked shortlist (JSON + printed table) of junction-spanning peptides predicted
to be presented on the patient's own alleles, with the tumour-specific (junction) residues
flagged.

Examples:
  python patient_neoepitopes.py --junction-seq "SSSYGQQ|IVRTDSLDLR" --hla "A*11:01,B*08:01"
  python patient_neoepitopes.py --ewsr1-exon 7 --nr4a3-exon 3 --hla "A*02:01,B*07:02" --out demo.json
"""

import argparse
import json
import os
import sys

LENGTHS = (8, 9, 10, 11)
RANK_STRONG, RANK_WEAK = 0.5, 2.0


def junction_from_seq(spec):
    if "|" not in spec:
        sys.exit("--junction-seq must contain '|' marking the seam, e.g. LEFT|RIGHT")
    left, right = spec.split("|", 1)
    left = "".join(left.split()).upper()
    right = "".join(right.split()).upper()
    return left, right


def junction_from_exons(e_exon, n_exon):
    """Build the in-frame junction context from Ensembl exon structure (reuses the
    population-analysis machinery). Returns (left, right) protein context around the seam."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from fusion_breakpoints import gene_model, translate  # type: ignore
    ews, nr4 = gene_model("EWSR1"), gene_model("NR4A3")
    if not (1 <= e_exon <= ews["n_coding_exons"]):
        sys.exit(f"EWSR1 exon {e_exon} out of range (1..{ews['n_coding_exons']})")
    if not (2 <= n_exon <= nr4["n_coding_exons"]):
        sys.exit(f"NR4A3 exon {n_exon} out of range (2..{nr4['n_coding_exons']})")
    p = ews["offsets"][e_exon - 1]
    q = nr4["offsets"][n_exon - 2]
    fusion_prot = translate(ews["cds"][:p] + nr4["cds"][q:])
    if not fusion_prot.endswith(nr4["protein"][-100:]):
        sys.exit(f"EWSR1 e{e_exon}::NR4A3 e{n_exon} is out of frame (NR4A3 C-terminus not "
                 "intact) — not a viable in-frame fusion; check the breakpoint.")
    j = p // 3
    return fusion_prot[:j], fusion_prot[j:]


def spanning_peptides(left, right):
    fusion = left + right
    j = len(left)
    peps = {}
    for L in LENGTHS:
        for start in range(max(0, j - L + 1), j):
            pep = fusion[start:start + L]
            if len(pep) == L and start < j < start + L:
                peps[pep] = {"length": L, "n_from_left": j - start,
                             "n_from_right": start + L - j}
    return peps


def main():
    ap = argparse.ArgumentParser(description="Per-patient EWSR1::NR4A3 neoepitope shortlister")
    ap.add_argument("--junction-seq", help="protein context 'LEFT|RIGHT' ('|' = seam)")
    ap.add_argument("--ewsr1-exon", type=int, help="EWSR1 coding-exon end (Ensembl mode)")
    ap.add_argument("--nr4a3-exon", type=int, help="NR4A3 coding-exon start (Ensembl mode)")
    ap.add_argument("--hla", required=True, help="comma-separated HLA-I, e.g. 'A*02:01,B*07:02'")
    ap.add_argument("--out", default=None, help="write JSON here (default: stdout only)")
    ap.add_argument("--no-novelty-filter", action="store_true",
                    help="skip removing peptides also present in wild-type EWSR1/NR4A3")
    args = ap.parse_args()

    if args.junction_seq:
        left, right = junction_from_seq(args.junction_seq)
        source = {"mode": "junction-seq"}
    elif args.ewsr1_exon and args.nr4a3_exon:
        left, right = junction_from_exons(args.ewsr1_exon, args.nr4a3_exon)
        source = {"mode": "exon", "EWSR1_exon": args.ewsr1_exon, "NR4A3_exon": args.nr4a3_exon}
    else:
        sys.exit("provide --junction-seq OR (--ewsr1-exon AND --nr4a3-exon)")

    alleles = []
    for a in args.hla.split(","):
        a = a.strip()
        if a:
            alleles.append(a if a.upper().startswith("HLA-") else "HLA-" + a)

    peps = spanning_peptides(left, right)
    if not peps:
        sys.exit("no junction-spanning peptides — check the seam position")

    # novelty: drop peptides that also occur in wild-type EWSR1 or NR4A3 (need parents)
    novelty_note = "not applied (offline / --no-novelty-filter)"
    if not args.no_novelty_filter:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from fusion_breakpoints import gene_model  # type: ignore
            ews_p = gene_model("EWSR1")["protein"]
            nr4_p = gene_model("NR4A3")["protein"]
            before = len(peps)
            peps = {p: m for p, m in peps.items() if p not in ews_p and p not in nr4_p}
            novelty_note = f"applied: {before - len(peps)} self-peptides removed, {len(peps)} novel"
        except Exception as e:  # noqa
            novelty_note = f"could not fetch parents ({e}); novelty NOT filtered"

    result = {
        "_note": "Per-patient EWSR1::NR4A3 junction neoepitope shortlist (MHCflurry-2.0). "
                 "Predicted presentation is a screen, NOT proof of immunogenicity; confirm "
                 "by immunopeptidomics + T-cell assay. Not medical advice.",
        "source": source,
        "junction_context": (left[-10:] + "|" + right[:10]),
        "patient_hla": alleles,
        "novelty_filter": novelty_note,
        "n_candidate_peptides": len(peps),
    }

    try:
        from mhcflurry import Class1PresentationPredictor
    except ImportError:
        result["error"] = "mhcflurry not installed; emitting candidate peptides only"
        result["candidate_peptides"] = sorted(peps)
        _emit(result, args.out)
        return

    predictor = Class1PresentationPredictor.load()
    plist = sorted(peps)
    df = predictor.predict(peptides=plist, alleles={a: [a] for a in alleles}, verbose=0)
    rank_col = "presentation_percentile" if "presentation_percentile" in df.columns else "affinity_percentile"
    rows = []
    for _, r in df.iterrows():
        rank = float(r[rank_col]); pep = r["peptide"]; m = peps[pep]
        rows.append({
            "peptide": pep, "allele": r["best_allele"],
            "affinity_nM": round(float(r["affinity"]), 1),
            "presentation_percentile": round(rank, 4),
            "presentation_score": round(float(r.get("presentation_score", 0)), 3),
            "call": "strong" if rank <= RANK_STRONG else ("weak" if rank <= RANK_WEAK else "non-binder"),
            "tumour_specific_residues": f"{m['n_from_left']} from EWSR1 + {m['n_from_right']} from NR4A3",
        })
    rows.sort(key=lambda x: x["presentation_percentile"])
    shortlist = [r for r in rows if r["call"] != "non-binder"]
    result["rank_column"] = rank_col
    result["n_presented_candidates"] = len(shortlist)
    result["n_strong"] = sum(1 for r in shortlist if r["call"] == "strong")
    result["shortlist"] = shortlist
    result["all_predictions"] = rows
    _emit(result, args.out)


def _emit(result, out):
    if out:
        with open(out, "w") as fh:
            json.dump(result, fh, indent=2)
        print("wrote", out, file=sys.stderr)
    # human-readable summary
    print(f"\nEWSR1::NR4A3 neoepitope shortlist — junction {result['junction_context']}")
    print(f"patient HLA: {', '.join(result['patient_hla'])}")
    print(f"novelty filter: {result['novelty_filter']}")
    sl = result.get("shortlist")
    if sl is None:
        print("(mhcflurry unavailable — candidate peptides only)")
        return
    print(f"\n{len(sl)} presented candidate(s); {result.get('n_strong',0)} strong:\n")
    print(f"  {'peptide':12} {'HLA':12} {'aff(nM)':>8} {'pres%ile':>9}  {'call':8} tumour-specific")
    for r in sl[:20]:
        print(f"  {r['peptide']:12} {r['allele']:12} {r['affinity_nM']:>8} "
              f"{r['presentation_percentile']:>9}  {r['call']:8} {r['tumour_specific_residues']}")
    if not sl:
        print("  (none predicted presented on the supplied alleles)")


if __name__ == "__main__":
    main()
