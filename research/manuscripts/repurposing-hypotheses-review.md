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
3. **No figures.** At least two would materially help: (a) a schematic of the three-method
   triangulation/firewall; (b) a candidate "landscape" (axis × tier × priority score), and
   optionally (c) the TxGNN rank distribution of our leads vs its top hits.
4. **Reproducibility of "not reported in EMC."** State the search strategy and dates used to
   judge that each candidate is genuinely untried in EMC (databases, queries, last-searched
   date) — currently implicit.

## Minor issues / improvements
- Some background facts lean on the 2025 review (Remiszewski) and registry (Masunaga) as
  secondary sources; where feasible, cite the **primary** pazopanib/sunitinib EMC reports for
  the "most active class" claim.
- Confirm the exact CD117/KIT-positive proportion attributed to Huang SC 2023 ("roughly half")
  and the "~5%" KIT-mutant figure against their reported numbers.
- The mRNA-vaccine candidate (T0) is the most speculative; keep its analogy-only framing and
  consider whether it belongs in the main table or a "frontier ideas" footnote.
- Consider a one-line plain-language summary / "key points" box for the target journal.
- "Approved > investigational" feasibility wording: make sure every Tranche-2 agent listed is
  actually approved somewhere (fruquintinib/tivozanib approvals vary by region) — note region.

## Strengthening the TxGNN result (optional, raises rigor)
The divergence claim currently rests on one model, one disease node, the `complex_disease`
checkpoint. To pre-empt "you used it wrong": (a) re-run on a *non-sparse* relative
(chondrosarcoma / soft-tissue-sarcoma node) and show oncology drugs rank appropriately there —
isolating sparsity as the cause; (b) optionally try the `disease_eval` split. If done, add as a
short supplementary note. (Scaffold exists: `txgnn_predict.py` + `txgnn-run.yml`.)

## Accuracy items verified in this pass
- All 14 candidates' ranks/tiers/priority scores in §3 match `candidates.json`; every
  `priorityScore` equals the sum of its six sub-criteria (0–18).
- TxGNN ranks cited in text match `txgnn-emc-predictions.json` (pazopanib #6422, sunitinib
  #6382, imatinib #5951 of 7,957 → bottom quartile).
- Two earlier author misattributions were corrected (Kim 2016, not "Yoshimura"; Huang SC 2023,
  not "Warmke"). All 16 references are cited inline.
- Efficacy-language sweep clean (only "no effective therapy" usages).

## Required human actions before submission (checklist)
- [ ] Recruit named authors incl. a sarcoma specialist; complete §8–§10.
- [ ] Independent clinical review of each candidate and of the imatinib patient-page decision.
- [ ] Expand references to full journal style; verify all identifiers resolve.
- [ ] Add figures.
- [ ] Document the "untried in EMC" search strategy + dates.
- [ ] Choose target venue (e.g., a sarcoma/oncology *hypothesis/perspective* section, or a
      rare-disease journal) and reformat to its style.
