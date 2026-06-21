# Internal review — repurposing-hypotheses.md (draft v0.2)

A critical self-review of the EMC drug-repurposing manuscript, written as a peer
reviewer/editor would, to drive it toward submission quality. Not part of the manuscript.
Reviewer: AI-assisted internal pass (2026-06-20). **This does not substitute for external
clinician and statistical review.**

## Overall judgement
A genuinely useful, unusually transparent hypothesis-generating paper. Its core novelty is
*methodological*: three independent lead-finding methods (mechanism curation, reproducible
target→drug enumeration, and a graph foundation model) reported with their agreements **and**
a frank negative/divergent result from the model. Evidence is honestly tiered and the
patient-firewall is principled. It is **not yet submittable** — it needs named human
authorship (incl. a sarcoma clinician), reference completion, figures, and a few accuracy
confirmations.

## Strengths
- Honest evidence grading (T0–T3) and a no-efficacy stance held consistently.
- The triangulation framing, including the TxGNN divergence reported as a limitation rather
  than buried — this is the paper's most original contribution and is reproducible (code +
  outputs in-repo).
- Every clinical/biological claim is cited; an automated check enforces zero unresolved claims.
- Realistic, disease-appropriate path-to-testing (biomarker-matched n-of-1, basket trials,
  model validation, registry/CURE ID).

## Major issues (must resolve before submission)
1. **Authorship & accountability.** No named authors. A hypothesis paper proposing drugs for
   patients *requires* a sarcoma clinician/researcher as author, with explicit
   AI-assistance disclosure (the draft says this — it must be actioned).
2. **References to full journal style.** Entries are abbreviated ("et al.", no volume/pages).
   Expand author lists from the primary sources (do **not** infer co-authors), add
   volume/issue/pages, and confirm every DOI/PMID resolves.
3. **Figures.** **Mostly addressed:** Figure 1 (candidate landscape — score × tier) and Figure 2
   (three-method triangulation + firewall schematic) are now in `figures/`. Still optional: a
   TxGNN rank figure (our leads vs its top hits / the sparsity stress-test) once that data lands.
   All are draft figures for the human authors to finalize to journal style.
4. **Reproducibility of "not reported in EMC."** State the search strategy and dates used to
   judge that each candidate is genuinely untried in EMC (databases, queries, last-searched
   date) — currently implicit.

## Minor issues / improvements
- Some background facts lean on the 2025 review (Remiszewski) and registry (Masunaga) as
  secondary sources; where feasible, cite the **primary** pazopanib/sunitinib EMC reports for
  the "most active class" claim.
- ~~Confirm the CD117/KIT proportion and the "~5%" KIT figure.~~ **Resolved (pass 3):** the
  earlier "CD117 expressed in roughly half (Huang SC 2023)" was wrong and mis-cited — CD117 IHC
  positivity is ≈84% (Giner et al. 2023, now ref 17); the unsupported "~5%" KIT figure was
  replaced with "rare / no more than a few percent" (Huang SC 2023, 48-case sequencing), and the
  expression-vs-activating-mutation distinction is now made explicit (it underpins the imatinib
  rationale).
- The mRNA-vaccine candidate (T0) is the most speculative; keep its analogy-only framing and
  consider whether it belongs in the main table or a "frontier ideas" footnote.
- Consider a one-line plain-language summary / "key points" box for the target journal.
- "Approved > investigational" feasibility wording: make sure every Tranche-2 agent listed is
  actually approved somewhere (fruquintinib/tivozanib approvals vary by region) — note region.

## TxGNN result — stress-tested (done; overturned a claim)
The divergence was stress-tested by re-running the model on two commoner relatives
(chondrosarcoma, soft-tissue sarcoma; `txgnn-relatives-comparison.json`). The result
**overturned our initial "EMC-sparsity" explanation**: the relatives ranked the same oncology
leads slightly *worse* (median ≈17–18th vs EMC's ≈21st percentile) with identical implausible
top hits. The manuscript, METHODOLOGY and findings doc now state the divergence is a general
property of the released checkpoint, **not** an EMC-rarity effect — and transparently note the
revision. Remaining optional rigor: run the full-graph / `disease_eval` checkpoint to test the
held-out-split caveat; optionally add a small cross-disease rank figure.

## Accuracy items verified in this pass
- All 14 candidates' ranks/tiers/priority scores in §3 match `candidates.json`; every
  `priorityScore` equals the sum of its six sub-criteria (0–18).
- TxGNN ranks cited in text match `txgnn-emc-predictions.json` (pazopanib #6422, sunitinib
  #6382, imatinib #5951 of 7,957 → bottom quartile).
- Two earlier author misattributions were corrected (Kim 2016, not "Yoshimura"; Huang SC 2023,
  not "Warmke"). All 16 references are cited inline.
- Efficacy-language sweep clean (only "no effective therapy" usages).
- **All 12 EMC references cross-checked against the PubMed corpus** (PMID/PMCID → matching title,
  DOI, year): all pass.
- Imatinib case verified verbatim (Jennings 2021: "KIT exon 11 ... c.1669 T>G", "on imatinib …
  for 3 years with stable disease"); CDK4 100% and CDKN2A/2B-loss bases verified (Giner 2023;
  Davis 2017); Iwata 2025's 221-drug screen (brigatinib, panobinostat, romidepsin) verified —
  it corroborates the screen-hit candidates.
- **Accuracy corrections made this pass:** CD117 figure (was a single cherry-picked number) now
  given as a verified range (≈53% Huang SC 2023; ≈84% of 31 Giner 2023); KIT-mutation
  frequency given as verified fractions (1/20 Urbini; 2/48 ≈4% Huang SC); imatinib's "bottom
  quartile" corrected (it sits at the 25th percentile, just above the bottom quartile — text now
  says 19th–25th percentile and reserves "bottom quartile" for pazopanib/sunitinib).

## Required human actions before submission (checklist)
*(Full verification trail: `fact-check-log.md`.)*
- [ ] Confirm the Bangerter 2023 venetoclax/carfilzomib/doxorubicin identities against the
      paper's full-text figures — its **abstract** reports a functional screen with synergies but
      does not name these drugs (underpins candidates #8, #10, #11).
- [ ] Recruit named authors incl. a sarcoma specialist; complete §8–§10.
- [ ] Independent clinical review of each candidate and of the imatinib patient-page decision.
- [ ] Expand references to full journal style; verify all identifiers resolve.
- [ ] Add figures.
- [ ] Document the "untried in EMC" search strategy + dates.
- [ ] Choose target venue (e.g., a sarcoma/oncology *hypothesis/perspective* section, or a
      rare-disease journal) and reformat to its style.
