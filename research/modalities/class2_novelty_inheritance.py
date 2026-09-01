#!/usr/bin/env python3
"""
Whether the class II (CD4) junction peptides are novel proteome-wide, decided without a new search.

⛔ WHY THIS EXISTS. §B5 of the vaccine manuscript reports proteome-wide sequence novelty for 170 of
174 junction peptides. Every one of those 174 is a class I candidate, 8 to 11 residues long
(`junction-proteome-novelty.json`). The class II arm — 13 junction-spanning 15-mers carrying 44
predicted binder calls and the single strong call the manuscript's B4 rests on
(`patient-cd4-demo.json`) — was never put through that search. So the paper's novelty statement and
its class II statement are about disjoint peptide sets, and a reader could reasonably take the first
as covering the second. It does not.

★ THE DERIVATION, AND WHY IT NEEDS NO PROTEOME FETCH. The class I search is an EXACT SUBSTRING
search: a peptide is "novel proteome-wide" when it occurs in no reviewed human protein sequence. That
property is inherited upward and only upward:

    if a peptide P does not occur anywhere in the proteome, then no string CONTAINING P occurs either.

So a class II 15-mer that contains any already-certified-absent 8- to 11-mer is itself certified
absent, by the search that has already been run and paid for. This is a proof over committed data,
not a new prediction.

⛔ AND THE INFERENCE RUNS IN ONE DIRECTION ONLY. If every tested substring of a 15-mer was FOUND in
the proteome, that says nothing about the 15-mer, which may still be absent. Those rows are reported
as UNKNOWN, never as "present" and never as "not novel". An absent reading is not a reading of
absence.

⛔ WHAT THIS IS NOT.
  - Not an immunogenicity, presentation or safety result. The class II calls it operates on are
    MHCnuggets binding PREDICTIONS, and the manuscript already records that class II prediction is
    substantially less accurate than class I. Sequence novelty is a necessary condition for tumour
    specificity and nowhere near a sufficient one.
  - Not a near-self search. `junction-selfsimilarity.json` searched proteome neighbours within two
    substitutions for the ELEVEN class I binders only. No equivalent exists for the class II
    peptides, and this module does not supply one: a 15-mer certified absent here may still have a
    near neighbour in a normal protein. That gap is stated in the output rather than left implicit.
  - Not a claim about the two candidate 15-mers that carry no predicted binder. The committed
    artifact enumerates only the 13 peptides with at least one binder call, so those two are outside
    what this can read, and they are reported as such rather than counted either way.

Inputs:  patient-cd4-demo.json          (committed; class II screen, MHCnuggets)
         junction-proteome-novelty.json (committed; exact-substring proteome search, UP000005640)
Output:  class2-novelty-inheritance.json
Cost:    $0 — local set logic over two committed artifacts. No network, no predictor, no GPU.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CD4 = os.path.join(HERE, "patient-cd4-demo.json")
NOVELTY = os.path.join(HERE, "junction-proteome-novelty.json")
OUT = os.path.join(HERE, "class2-novelty-inheritance.json")


def load(path, what):
    if not os.path.exists(path):
        raise SystemExit(
            f"{what} is missing at {path}. It is committed, so regenerate it rather than writing an "
            "artifact that reports an inheritance over inputs nothing produced."
        )
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    cd4 = load(CD4, "patient-cd4-demo.json")
    novelty = load(NOVELTY, "junction-proteome-novelty.json")

    novel = {p["peptide"]: p for p in novelty["peptides_novel_proteome_wide"]}
    found = {p["peptide"]: p for p in novelty["peptides_found_in_proteome"]}

    strong_peptides = {p["peptide"] for p in cd4["all_predictions"] if p.get("call") == "strong"}
    by_peptide = {}
    for p in cd4["all_predictions"]:
        rec = by_peptide.setdefault(p["peptide"], {"alleles": [], "best_ic50_nM": None,
                                                   "strong_on": []})
        rec["alleles"].append(p["allele"])
        if rec["best_ic50_nM"] is None or p["ic50_nM"] < rec["best_ic50_nM"]:
            rec["best_ic50_nM"] = p["ic50_nM"]
        if p.get("call") == "strong":
            rec["strong_on"].append(p["allele"])

    rows = []
    for pep in sorted(by_peptide):
        certifying = sorted(
            (s for s in novel if s in pep), key=lambda s: (-len(s), s))
        also_found = sorted((s for s in found if s in pep), key=lambda s: (-len(s), s))
        certified = len(certifying) > 0
        rows.append({
            "peptide": pep,
            "length": len(pep),
            "n_alleles_with_a_binder_call": len(by_peptide[pep]["alleles"]),
            "alleles_with_a_binder_call": sorted(by_peptide[pep]["alleles"]),
            "best_ic50_nM": by_peptide[pep]["best_ic50_nM"],
            "strong_on": sorted(by_peptide[pep]["strong_on"]),
            "verdict": "CERTIFIED_ABSENT_FROM_THE_REVIEWED_PROTEOME" if certified else
                       "UNKNOWN — no tested substring of this peptide was certified absent",
            "certifying_substrings": certifying,
            "n_certifying_substrings": len(certifying),
            "shortest_certifying_substring": certifying[-1] if certifying else None,
            "tested_substrings_that_were_FOUND_in_the_proteome": also_found,
            "⚠": None if certified else
                 "UNKNOWN is not 'present'. It means no substring of this peptide was in the tested "
                 "set, so the exact-substring search has never spoken about it.",
        })

    n_certified = sum(1 for r in rows if r["verdict"].startswith("CERTIFIED"))
    strong_rows = [r for r in rows if r["strong_on"]]

    out = {
        "_what": "Proteome-wide sequence novelty of the class II (CD4) junction peptides, inherited "
                 "from the committed class I exact-substring search rather than re-searched.",
        "_why": "The manuscript's §B5 novelty result covers 174 class I peptides of length 8 to 11. "
                "The class II arm's 15-mers were never in that set, so the paper's novelty statement "
                "and its class II statement are about disjoint peptide sets.",
        "⛔_what_this_is_not": (
            "NOT an immunogenicity, presentation or safety result — the class II calls are MHCnuggets "
            "binding PREDICTIONS, and class II prediction is less accurate than class I. NOT a "
            "near-self search: junction-selfsimilarity.json covered the 11 class I binders only, and "
            "a 15-mer certified absent here may still have a near neighbour in a normal protein. NOT "
            "a statement about the two candidate 15-mers that carry no binder call, which the "
            "committed class II artifact does not enumerate."
        ),
        "_method": "a peptide absent from the proteome cannot occur inside any longer string, so a "
                   "15-mer containing an already-certified-absent 8- to 11-mer is certified absent "
                   "by the same search. The inference runs upward only: a 15-mer whose tested "
                   "substrings were all FOUND is UNKNOWN, never 'present'.",
        "_inputs": {
            "class_ii": {
                "file": "patient-cd4-demo.json",
                "junction_context": cd4.get("junction_context"),
                "junction_label": (cd4.get("source") or {}).get("junction_label"),
                "predictor": cd4.get("_predictor"),
                "n_alleles_screened": cd4.get("n_alleles_screened"),
                "n_candidate_15mers_enumerated_by_that_run": cd4.get("n_candidate_15mers"),
                "n_predicted_binders": cd4.get("n_predicted_binders"),
                "n_strong": cd4.get("n_strong"),
            },
            "novelty": {
                "file": "junction-proteome-novelty.json",
                "proteome": novelty.get("_proteome"),
                "method": novelty.get("_method"),
                "n_peptides_tested": novelty.get("n_peptides_tested"),
                "n_novel_proteome_wide": novelty.get("n_novel_proteome_wide"),
                "n_found_in_proteome": novelty.get("n_found_in_proteome"),
            },
        },
        "_cost": "$0 — set logic over two committed artifacts; no network, no predictor, no GPU.",
        "n_class_ii_peptides_with_a_binder_call": len(rows),
        "n_certified_absent_from_the_reviewed_proteome": n_certified,
        "n_unknown": len(rows) - n_certified,
        "n_class_ii_candidates_not_enumerated_by_the_committed_artifact": (
            (cd4.get("n_candidate_15mers") or 0) - len(rows)),
        "the_strong_call": {
            "peptides": sorted(strong_peptides),
            "rows": strong_rows,
            "⚠_weight": "One strong call, on one allele, from a class II predictor the manuscript "
                        "already grades as less accurate than its class I counterpart. Certifying "
                        "its sequence novelty removes one failure mode and adds no evidence that it "
                        "is processed, presented or seen by a T cell.",
        },
        "⛔_the_gap_this_does_not_close": (
            "No near-self search has been run for any class II peptide. The class I near-self search "
            "(junction-selfsimilarity.json) found that every near-self neighbour of every class I "
            "binder lies in an NR4A3 or NR4A1 isoform or in EWSR1 itself — the same gene family the "
            "class II peptides are drawn from — so the class II peptides have no reason to be "
            "expected clean and have simply not been asked."
        ),
        "rows": rows,
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}")
    print(f"  class II peptides with a binder call: {len(rows)}")
    print(f"  certified absent from the reviewed proteome: {n_certified}")
    print(f"  UNKNOWN: {len(rows) - n_certified}")
    for r in strong_rows:
        print(f"  strong call {r['peptide']} on {r['strong_on']} at {r['best_ic50_nM']} nM "
              f"-> {r['verdict']}")


if __name__ == "__main__":
    main()
