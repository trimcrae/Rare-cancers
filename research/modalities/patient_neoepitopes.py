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

⚠ READ THE EXON FLAGS BEFORE COPYING THAT LINE (route framing audit, 2026-08-06).
`--ewsr1-exon` / `--nr4a3-exon` are **CODING**-exon ranks, and the arithmetic below
(`offsets[e-1]` / `offsets[n-2]`) is correct for that reading. But "EWSR1 e7 :: NR4A3 e3" is how
this repo names the reported fusion types by their **TRANSCRIPT** exons, and the example above
passes those labels straight in. Where a leading exon is non-coding the two numbering schemes
differ, so the example silently specifies a different junction from the one its name implies.

⛔ THIS IS THE SAME CONFUSION THAT PRODUCED THE 2026-08-03 OFF-BY-TWO — a coding-exon offset table
indexed with a transcript exon number, sliding to a neighbour instead of raising. There it reached
committed artifacts (see `fusion-neoantigen-retraction.json`, and `junction_aso.py`, fixed
2026-08-06). Here the INTERFACE is right and only the example is misleading — which is why nothing
caught it: a correct function with a wrong worked example fails no test and lints clean.
`fusion_breakpoints.resume_offset`/`cut_offset` are the canonical raising helpers; this module is
deliberately pure-stdlib and standalone, so it cannot import them.
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


def junction_reading(partner, e_exon, n_exon):
    """The chimeric protein and its seam for `partner` exon `e_exon` :: NR4A3 exon `n_exon`.

    ⛔ TRANSCRIPT MODEL, AND THE EXON NUMBERS ARE TRANSCRIPT RANKS. Superseded, retained: this
    was `junction_from_exons`, which built `partner_cds[:p] + NR4A3_cds[q:]` — pure CDS
    concatenation on CODING-exon ranks. That model discards the acceptor exon's retained 5'UTR,
    and a fusion transcript does not: it splices the acceptor exon in WHOLE. The two models
    therefore select DISJOINT seams, which is the 2026-08-07 correction
    (`fusion-breakpoint-neoantigens.json` -> `_coordinate_system`). Regenerating the artifacts
    could never repair the two callers of this function, because the defect was here rather than
    in their inputs: the class-II demo still read `QYSQQSSSYGQQ|IVRTDSLKGRRG` after a green
    pipeline run, against the corrected `SQQSSSYGQQ|NMPCVQAQYSP`.

    One builder, one grader (rule 1): the junction comes from `junction_aso.mrna_junction_generic`
    and the verdict from `junction_aso.grade_junction` — the same two functions that produced the
    corrected population artifact. Nothing about frame or seam position is re-derived here.

    Returns the reading dict, with `_prot` (chimeric protein), `_j0` (0-based index of the first
    non-pure-donor residue) and `_has_novel` (whether that residue is a seam codon belonging to
    neither parent) added. Exits non-zero on any junction the grader does not pass — callers,
    including the TAF15 exon sweep in `modalities-run.yml`, depend on that exit code to mean
    "not a viable in-frame fusion, try the next exon".
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import junction_aso as ja  # type: ignore
    from fusion_breakpoints import chimeric_protein  # type: ignore

    donor, nr4 = ja.transcript_model(partner), ja.transcript_model("NR4A3")
    try:
        j = ja.mrna_junction_generic(donor, nr4, e_exon, n_exon)
    except Exception as exc:  # noqa: BLE001 — a refusal is a reading, and it must say why
        sys.exit(f"{partner} e{e_exon}::NR4A3 e{n_exon} is unreadable: {exc}")
    lo, hi = ja.plausible_nr4a3_resume_residues()
    grade, why = ja.grade_junction(j, lo, hi)
    if grade != ja.EMITTABLE:
        sys.exit(f"{partner} e{e_exon}::NR4A3 e{n_exon} graded {grade}: {why} — "
                 "not a viable in-frame fusion; check the breakpoint.")
    j["_prot"] = chimeric_protein(donor, j)
    j["_j0"] = j["donor_last_whole_residue"]
    j["_has_novel"] = bool(j["donor_coding_phase"])
    j["_grade"] = grade
    return j


def junction_from_exons(partner, e_exon, n_exon):
    """(left, right) protein context around the seam, on the transcript model.

    `right` OPENS with the seam codon when there is one, so `len(left)` is the index of the
    first residue that is not purely the donor's. Peptide enumeration must go through
    `fusion_breakpoints.junction_peptides(..., novel_residue=...)` rather than a plain straddle
    test, or every peptide that starts at the seam codon is silently dropped.
    """
    j = junction_reading(partner, e_exon, n_exon)
    return j["_prot"][:j["_j0"]], j["_prot"][j["_j0"]:]


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


def junction_peptide_context(prot, j0, has_novel, peps):
    """Describe where each selected peptide sits relative to the seam.

    ⛔ SELECTION IS NOT REDONE HERE. `peps` comes from `fusion_breakpoints.junction_peptides`,
    the one enumerator, which under the corrected model admits peptides that BEGIN at the seam
    codon — a plain straddle test drops those, and they include the strongest binders the
    population artifact reports. This function only locates the seam-covering occurrence of each
    peptide and counts donor / seam / acceptor residues in it.
    """
    out = {}
    for pep, L in peps.items():
        start = next((s for s in range(max(0, j0 - L + 1), j0 + 1) if prot[s:s + L] == pep), None)
        if start is None:
            continue
        n_seam = 1 if has_novel else 0
        out[pep] = {"length": L,
                    "n_from_left": j0 - start,
                    "n_from_right": max(0, (start + L) - (j0 + n_seam)),
                    "seam_codon_included": bool(has_novel)}
    return out


def main():
    ap = argparse.ArgumentParser(description="Per-patient EWSR1::NR4A3 neoepitope shortlister")
    ap.add_argument("--junction-seq", help="protein context 'LEFT|RIGHT' ('|' = seam)")
    ap.add_argument("--partner", default="EWSR1", choices=["EWSR1", "TAF15"],
                    help="5' FET fusion partner for exon mode (default EWSR1; ~16%% are TAF15)")
    ap.add_argument("--ewsr1-exon", "--partner-exon", dest="partner_exon", type=int,
                    help="5' partner coding-exon end (Ensembl mode)")
    ap.add_argument("--nr4a3-exon", type=int, help="NR4A3 coding-exon start (Ensembl mode)")
    ap.add_argument("--hla", required=True, help="comma-separated HLA-I, e.g. 'A*02:01,B*07:02'")
    ap.add_argument("--out", default=None, help="write JSON here (default: stdout only)")
    ap.add_argument("--no-novelty-filter", action="store_true",
                    help="skip removing peptides also present in wild-type EWSR1/NR4A3")
    args = ap.parse_args()

    if args.junction_seq:
        left, right = junction_from_seq(args.junction_seq)
        source = {"mode": "junction-seq", "partner": "unspecified",
                  "coordinate_system": "caller-supplied seam — not derived here"}
        peps = spanning_peptides(left, right)
        seam_context = left[-10:] + "|" + right[:10]
    elif args.partner_exon and args.nr4a3_exon:
        j = junction_reading(args.partner, args.partner_exon, args.nr4a3_exon)
        prot, j0, has_novel = j["_prot"], j["_j0"], j["_has_novel"]
        left, right = prot[:j0], prot[j0:]
        source = {"mode": "exon", "partner": args.partner,
                  "partner_exon": args.partner_exon, "NR4A3_exon": args.nr4a3_exon,
                  "exon_rank_basis": "TRANSCRIPT exon ranks (junction_aso.transcript_model)",
                  "coordinate_system": "TRANSCRIPT (junction_aso.mrna_junction_generic)",
                  "junction_label": j["junction_label"], "grade": j["_grade"],
                  "seam_codon_residue": prot[j0] if has_novel else None,
                  "acceptor_5utr_nt_retained": j["nr4a3_acceptor_exon_5utr_nt_retained"]}
        from fusion_breakpoints import junction_peptides  # type: ignore
        peps = junction_peptide_context(
            prot, j0, has_novel, junction_peptides(prot, j0, LENGTHS, novel_residue=has_novel))
        seam_context = prot[max(0, j0 - 10):j0] + "|" + prot[j0:j0 + 10]
    else:
        sys.exit("provide --junction-seq OR (--partner-exon AND --nr4a3-exon)")

    alleles = []
    for a in args.hla.split(","):
        a = a.strip()
        if a:
            alleles.append(a if a.upper().startswith("HLA-") else "HLA-" + a)

    if not peps:
        sys.exit("no junction-spanning peptides — check the seam position")

    # novelty: drop peptides that also occur in the wild-type 5' partner or NR4A3
    novelty_note = "not applied (offline / --no-novelty-filter)"
    if not args.no_novelty_filter:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from fusion_breakpoints import gene_model  # type: ignore
            partners = ["EWSR1", "TAF15"] if source["partner"] == "unspecified" else [source["partner"]]
            parent_seqs = [gene_model(g)["protein"] for g in partners] + [gene_model("NR4A3")["protein"]]
            before = len(peps)
            peps = {p: m for p, m in peps.items() if all(p not in s for s in parent_seqs)}
            novelty_note = f"applied vs {partners}+NR4A3: {before - len(peps)} self removed, {len(peps)} novel"
        except Exception as e:  # noqa
            novelty_note = f"could not fetch parents ({e}); novelty NOT filtered"

    result = {
        "_note": "Per-patient (EWSR1|TAF15)::NR4A3 junction neoepitope shortlist (MHCflurry-2.0). "
                 "Predicted presentation is a screen, NOT proof of immunogenicity; confirm "
                 "by immunopeptidomics + T-cell assay. Not medical advice.",
        "source": source,
        "junction_context": seam_context,
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
            "tumour_specific_residues": (
                f"{m['n_from_left']} from {source['partner']} + "
                + ("1 seam codon + " if m.get("seam_codon_included") else "")
                + f"{m['n_from_right']} from NR4A3"),
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
