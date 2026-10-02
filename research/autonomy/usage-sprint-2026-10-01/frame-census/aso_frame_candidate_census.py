#!/usr/bin/env python3
"""Candidate vetting over committed transcript models; no efficacy or patient evidence.

Reuses the independent verifier's arithmetic instrument. This census is not a third independent
implementation: it exposes native gate ordering, donor strata and fixed-offset stop witnesses.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "research/modalities"))
import aso_independent_verification as verifier  # noqa: E402

OUT = Path(__file__).with_name("aso-frame-candidate-census.json")


def _counts(rows):
    return dict(sorted(Counter(row["grade"] for row in rows.values()).items()))


def build():
    checked = verifier.run()
    if checked["verdict"] != "AGREES":
        raise RuntimeError("Candidate census requires clean verifier agreement: " +
                           "; ".join(checked["problems"]))
    genomic = verifier.splice_from_genomic()
    models = {}
    for gene, record in sorted(genomic.items()):
        offset, cds_nt, protein = verifier.longest_orf(record["cdna"])
        models[gene] = dict(record, utr5=offset, cds_nt=cds_nt, protein=protein,
                           coding=verifier.coding_vector(record["exon_lengths"], offset, cds_nt))
    atlas = json.loads(Path(verifier.ATLAS).read_text(encoding="utf-8"))
    inventory = json.loads(Path(verifier.INVENTORY).read_text(encoding="utf-8"))
    lo, hi = inventory["inventory"]["excluded_span"]["nr4a3_resume_range_across_plausible_breakpoints"]
    window = atlas["acceptor_exon_window"]
    declared = verifier.grade_all_pairs(models, lo, hi, window)
    all_pairs = verifier.grade_all_pairs(
        models, lo, hi, range(1, len(models["NR4A3"]["exon_lengths"]) + 1))
    acc = models["NR4A3"]
    diagnostics = []
    register_candidates = []
    for label, row in sorted(declared.items()):
        eligible_register = (row["nr4a3_acceptor_exon_is_coding"] and
                             lo <= row["nr4a3_first_residue"] <= hi and
                             row["arithmetic_in_frame"])
        if eligible_register:
            register_candidates.append(label)
        if not (row["arithmetic_in_frame"] and not row["translated_in_frame"]):
            continue
        donor, acceptor = label.split("__")
        gene, donor_exon = donor.rsplit("_e", 1)
        acceptor_exon = int(acceptor.rsplit("_e", 1)[1])
        don = models[gene]
        cut = sum(don["exon_lengths"][:int(donor_exon)])
        resume = sum(acc["exon_lengths"][:acceptor_exon - 1])
        chimera = don["cdna"][:cut] + acc["cdna"][resume:]
        protein = verifier.translate(chimera[don["utr5"]:])
        stop = don["utr5"] + 3 * len(protein)
        codon = chimera[stop:stop + 3]
        if verifier.CODONS.get(codon) != "*":
            raise RuntimeError(f"{label}: no actual terminating codon at the recorded stop")
        origin = "donor" if stop + 3 <= cut else (
            "NR4A3" if stop >= cut else "junction")
        diagnostics.append({
            "junction": label, "grade": row["grade"], "donor": gene,
            "donor_exon": int(donor_exon), "acceptor_exon": acceptor_exon,
            "donor_cut_cdna_0based_exclusive": cut,
            "nr4a3_resume_cdna_0based": resume,
            "frame_sum_mod3": row["frame_sum_mod3"],
            "nr4a3_first_residue": row["nr4a3_first_residue"],
            "passes_declared_resume_gate": lo <= row["nr4a3_first_residue"] <= hi,
            "otherwise_eligible_register": eligible_register,
            "native_donor_start_retained": cut >= don["utr5"] + 3,
            "translation_offset_cdna_0based": don["utr5"],
            "translated_aa_before_stop": len(protein),
            "stop_codon": codon, "stop_cdna_0based": stop, "stop_origin": origin,
            "stop_parent_cdna_0based": stop if origin == "donor" else (
                resume + stop - cut if origin == "NR4A3" else None),
        })
    inputs = [Path(verifier.GENOMIC), Path(verifier.CDNA), Path(verifier.ATLAS),
              Path(verifier.INVENTORY), Path(verifier.SCREEN4),
              Path(verifier.__file__), Path(__file__)]
    return {
        "schema": "aso-frame-candidate-census/1",
        "question": "Which register-correct declared rows terminate under fixed-offset translation, and does this exclude any additional candidate under the current native gate ladder?",
        "scope": "Committed reference transcript models; computational candidate vetting, not observed patient junctions or therapeutic validation.",
        "method": "Reuse the independent genomic-splicing/longest-ORF/frame instrument; locate each terminating codon directly in its chimeric cDNA.",
        "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in inputs},
        "declared_acceptor_exons": window, "nr4a3_resume_residue_range": [lo, hi],
        "declared_pairs": len(declared), "declared_grade_counts": _counts(declared),
        "unrestricted_pairs": len(all_pairs), "unrestricted_grade_counts": _counts(all_pairs),
        "emittable_outside_declared_window": sorted(
            label for label, row in all_pairs.items()
            if label not in declared and row["grade"] == "EMITTABLE"),
        "declared_grade_counts_by_donor": {
            gene: _counts({label: row for label, row in declared.items()
                           if label.startswith(gene + "_")})
            for gene in sorted(models) if gene != "NR4A3"},
        "otherwise_eligible_register": len(register_candidates),
        "new_exclusions_at_translation_gate": sum(row["otherwise_eligible_register"] for row in diagnostics),
        "translation_eligible": sum(row["grade"] == "EMITTABLE" for row in declared.values()),
        "register_correct_translation_terminations": diagnostics,
        "limitations": [
            "The candidate window and NR4A3 residue range are declared inputs, not independently inferred scope.",
            "Reference isoforms do not establish which transcript junction occurs in a tumor.",
            "Fixed donor-CDS-offset translation does not establish biological initiation when the donor start codon is absent.",
            "Agreement bounds implementation error; it cannot validate a shared method assumption.",
            "No binding, delivery, safety, efficacy or therapeutic window is established.",
        ],
    }


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    result = build()
    rendered = json.dumps(result, indent=2) + "\n"
    if "--check" in argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != rendered:
            print("Candidate census is stale", file=sys.stderr)
            return 1
        print("Candidate census is current")
        return 0
    OUT.write_text(rendered, encoding="utf-8")
    print(f"{result['otherwise_eligible_register']} otherwise-eligible register candidates; "
          f"{result['translation_eligible']} translation-eligible; "
          f"{len(result['register_correct_translation_terminations'])} fixed-offset terminations; "
          f"{result['new_exclusions_at_translation_gate']} added exclusions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
