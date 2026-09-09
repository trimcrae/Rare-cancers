#!/usr/bin/env python3
"""Render CHARACTERISATION.md from neoantigen3-correspondence.json. No new numbers."""
import json, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "neoantigen3-correspondence.json")))
A, B = D["A_correspondence"], D["B_characterisation"]
V, R, P = B["validated"], B["repository_predicted"], B["allele_panel_comparison"]
L = []
w = L.append

w("---")
w("id: DOC-NEOANTIGEN-3-CHARACTERISATION")
w('title: "NEOANTIGEN-3 — validated fusion-junction epitopes vs. this repository\'s '
  'predicted EWSR1::NR4A3 junction peptides"')
w("level: L4")
w("kind: investigation-artifact")
w("status: live")
w("date: 2026-09-09")
w("last_verified: 2026-09-09")
w("---")
w("")
w("# Characterisation — rendered from `neoantigen3-correspondence.json`, do not hand-edit")
w("")
w("⛔ **Prediction is not presentation.** The 15 validated epitopes come from nine *other* fusion")
w("oncoproteins. Nothing here is evidence that any EWSR1::NR4A3 peptide is or is not presented.")
w("Nine fusions are not a sample of fusions; every comparison below is a statement about the")
w("**prediction set and its allele panel**, not about EMC.")
w("")

w("## 1 · Correspondence (each arm separate)")
w("")
w("| query set | reference set | exact | substring | isobaric exact (I=L) | isobaric substring |")
w("|---|---|---|---|---|---|")
for k, v in A["tests"].items():
    q, r = k.split("__vs__")
    w("| %s | %s | **%d** | **%d** | **%d** | **%d** |"
      % (q, r, v["exact"]["n"], v["substring"]["n"], v["isobaric_exact"]["n"],
         v["isobaric_substring"]["n"]))
w("")
w("Context-level arm (each reference sequence against the full 21-residue junction context of")
w("each of the 5 in-frame junctions, so an epitope lying wholly in a flank would be caught): "
  "**%d hit(s)** of %d reference sequences." % (A["context_level_arm"]["n_hits"],
                                                len(A["reference_sets"]["validated_junction_epitopes_15"])
                                                + len(A["reference_sets"]["non_junction_negative_controls"])
                                                + len(A["reference_sets"]["other_sequenced_records"])))
w("")
for h in A["context_level_arm"]["hits"]:
    w("* `%s` — %s (%s, set `%s`)%s" % (h["ref_seq"], h["ref_fusion"], h["ref_id"], h["ref_set"],
                                        " — **isobaric only**" if h["isobaric_only"] else ""))
for k, v in A["tests"].items():
    for hit in v["substring"]["hits"]:
        w("* substring: repo `%s` contains reference `%s` (%s, %s)"
          % (hit["query"], hit["ref_seq"], hit["ref_id"], hit["ref_fusion"]))
w("")
st = A["matcher_selftest"]
w("**Matcher self-test.** Exact arm recovers %d/%d running the reference set against itself; the"
  % (st["exact_arm_validated_vs_itself"]["n"], st["exact_arm_validated_vs_itself"]["expected_min"]))
w("isobaric arm recovers %d hits on %d I/L-swapped copies of the reference sequences. The one"
  % (st["isobaric_arm_IL_swapped_validated_vs_itself"]["n_isobaric_exact"],
     st["isobaric_arm_IL_swapped_validated_vs_itself"]["n_queries"]))
w("substring hit above is a live positive on the real query set. The zeros are therefore not a")
w("dead matcher.")
w("")

w("## 2 · What the 15 real ones look like")
w("")
w("| property | validated (n=%d) |" % V["n"])
w("|---|---|")
w("| length | %s |" % ", ".join("%s-mer ×%d" % (k, v) for k, v in V["length_distribution"].items()))
w("| allotype (epitope-allele pairs) | %s |"
  % ", ".join("%s ×%d" % (k, v) for k, v in V["allele_distribution"].items()))
w("| locus | %s |" % ", ".join("HLA-%s ×%d" % (k, v) for k, v in V["locus_distribution"].items()))
w("| distinct fusion oncoproteins | %d |" % len(V["fusion_distribution"]))
w("| C-terminal residue | %s |" % ", ".join("%s×%d" % (k, v) for k, v in V["cterminal_residue_distribution"].items()))
w("")
bp = V["breakpoint_position"]
w("### Breakpoint position inside the validated peptides")
w("")
w("Stated in the source record, or fixed by another record in the same fusion protein, for")
w("**%d of %d**. The remaining **%d are UNKNOWN**: a peptide sequence alone does not say where the"
  % (bp["n_with_stated_or_derivable_split"], V["n"], bp["n_unknown"]))
w("junction falls inside it, and this lane is offline. They are reported as unknown, not as zero.")
w("")
w("| id | fusion | peptide | len | donor residues | acceptor residues | C-terminal anchor from | basis |")
w("|---|---|---|---|---|---|---|---|")
for r in bp["rows"]:
    if r["confidence"] == "unknown":
        continue
    w("| %s | %s | `%s` | %d | %d | %d | %s | %s |"
      % (r["id"], r["fusion"], r["peptide"], r["len"], r["donor_residues"],
         r["acceptor_residues"], r["cterm_from"], r["confidence"]))
w("")
w("UNKNOWN: %s." % ", ".join(r["id"] for r in bp["rows"] if r["confidence"] == "unknown"))
w("")

w("## 3 · What this repository predicted")
w("")
w("The 174 distinct junction peptides are a **uniform sliding-window tiling** of each junction —")
w("every 8–11mer window that crosses the seam — so their donor/acceptor split is a property of the")
w("enumeration, not of the predictor. Only the ranked binders carry predictive content.")
w("")
w("| property | 174 junction peptides (%d instances over 5 junctions) | 11 ranked binders |"
  % R["n_peptide_instances_across_5_junctions"])
w("|---|---|---|")
w("| length | %s | %s |"
  % (", ".join("%s×%d" % (k, v) for k, v in R["length_distribution_instances"].items()),
     ", ".join("%s×%d" % (k, v) for k, v in R["ranked_binders"]["length_distribution"].items())))
w("| allotype | n/a (all 10 panel alleles screened) | %s |"
  % ", ".join("%s×%d" % (k, v) for k, v in R["ranked_binders"]["allele_distribution"].items()))
w("| contains the hybrid seam residue | %d/%d | 11/11 |"
  % (R["n_instances_containing_the_hybrid_seam_residue"], R["n_peptide_instances_across_5_junctions"]))
w("| C-terminal residue from | %s | %s |"
  % (", ".join("%s×%d" % (k, v) for k, v in R["cterminal_source_distribution"].items()),
     ", ".join("%s×%d" % (k, v) for k, v in
               Counter(r["cterm_from"] for r in R["ranked_binders"]["rows"]).most_common())))
w("")
w("### The 11 ranked binders, with their partner split")
w("")
w("| peptide | allele | len | EWSR1 residues | seam (hybrid) | NR4A3 residues | presentation percentile | class |")
w("|---|---|---|---|---|---|---|---|")
for r in R["ranked_binders"]["rows"]:
    w("| `%s` | %s | %d | %d | %d | %d | %s | %s |"
      % (r["peptide"], r["allele"], r["len"], r["donor_residues"], r["seam_hybrid_residue"],
         r["acceptor_residues"], r["presentation_percentile"], r["klass"]))
w("")
acc8 = sum(1 for r in R["ranked_binders"]["rows"] if r["acceptor_residues"] >= 8)
w("**%d of 11** ranked binders take **8 or more of their residues from NR4A3** and at most two from"
  % acc8)
w("EWSR1. ⛔ This says nothing about presentation; it is a property of where the predictor's scores")
w("landed on a tiling this repository generated.")
w("")

w("## 4 · Allele panel — the one comparison that is directly actionable")
w("")
w("| | |")
w("|---|---|")
w("| predictor panel (MHCflurry, 10 alleles) | %s |" % ", ".join(P["predictor_panel"]))
w("| allotypes carrying a validated junction epitope | %s |" % ", ".join(P["validated_allotypes"]))
w("| **in the panel** | %s |" % ", ".join(P["in_panel"]))
w("| **NOT in the panel** | %s |" % ", ".join(P["not_in_panel"]))
w("| validated epitope-allele pairs on-panel / off-panel | %d / %d |"
  % (P["n_validated_epitopes_on_in_panel_allotypes"], P["n_validated_epitopes_on_off_panel_allotypes"]))
w("| HLA-C in the panel | %s |" % (", ".join(P["hla_C_in_panel"]) or "**none**"))
w("| HLA-C among validated allotypes | %s |" % ", ".join(P["hla_C_in_validated"]))
w("| panel allotypes that returned **zero** ranked binders | %s |"
  % ", ".join(P["panel_allotypes_with_zero_ranked_binders"]))
w("")

open(os.path.join(HERE, "CHARACTERISATION.md"), "w").write("\n".join(L) + "\n")
print("wrote CHARACTERISATION.md (%d lines)" % len(L))
