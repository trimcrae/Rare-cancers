---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT-SUBMISSION-CHECKLIST
title: "Submission checklist and journal-fit rationale — EWSR1::NR4A3 transcriptional-output manuscript"
level: L3
kind: memo
status: live
canonical_for: []
purpose: >
  Record the journal recommendation and its reasoning, confirm the manuscript meets the target
  journals' author standards, and list the residual author-only steps that must be completed before
  the manuscript is actually submitted — so that "submission-ready" is auditable rather than asserted.
scope: >
  Submission logistics and standards compliance for the transcriptional-output manuscript. Contains no
  scientific result.
audience: [maintainers, external reviewers, collaborators]
related: [DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT]
date: 2026-08-07
last_verified: 2026-08-07
---

# Submission checklist and journal-fit rationale

Companion to [`nr4a3-fusion-transcriptional-output.md`](./nr4a3-fusion-transcriptional-output.md) and
[`nr4a3-fusion-transcriptional-output-cover-letter.md`](./nr4a3-fusion-transcriptional-output-cover-letter.md).

## 1 · Recommended venue

**Primary: *Genes, Chromosomes & Cancer* (Wiley), Original Research Article.** It is the field's
dedicated journal for the genetics and genomics of neoplasia, and specifically for fusion-driven
sarcomas — the exact audience that reads and cites EMC fusion biology. It is receptive to focused
genomic re-analyses of the kind this manuscript is, which makes it a realistic home for a careful,
explicitly incremental result. Crucially, it is a **hybrid** journal: open access is optional (an
article-processing charge of roughly US$4,810 applies *only if* the open-access option is chosen), and
the traditional subscription route carries **no author charge**. Publishing via the subscription route,
with a free bioRxiv preprint as the open copy, satisfies the standing constraint that the author pays
nothing.

**Aspirational alternative: *The Journal of Pathology* (Wiley).** This is the natural home in one
respect — it published the three primary papers this manuscript synthesises (Subramanian 2005, Filion
2009, Brenca 2019). It is also hybrid (subscription route free; open access optional at ~US$5,450), so
the $0 constraint is met. It carries a higher desk-reject risk for an explicitly incremental,
single-author re-analysis and a tighter length preference (see §3), so it is the second choice, not the
first.

**Realistic fallback: *British Journal of Cancer* (Springer Nature)** — hybrid, subscription route
free, broad cancer-genomics scope.

**Preprint (open copy, free): bioRxiv**, Cancer Biology / Genomics. bioRxiv accepts computational
re-analyses of public data at no charge, and both Wiley journals above permit bioRxiv preprints.

> **Why not the obvious open-access venues.** Several journals that would fit topically have moved to
> gold open access with a mandatory APC and are therefore excluded by the $0 constraint unless a full
> waiver is granted: e.g. *BMC Cancer*, *Cancer Medicine*, *ESMO Open*, and — verified 2026-08-07 —
> *The Oncologist* (~US$3,668) and the *Journal of Cancer Research and Clinical Oncology* (~US$4,390),
> both of which flipped from hybrid to full OA. Journal fee models change; confirm the subscription/no-
> APC route in writing at submission.

## 2 · Standards compliance (target: GCC; also satisfies J Pathol)

| requirement | target | status in manuscript |
|---|---|---|
| Article type | Original Research Article | ✔ declared |
| Abstract | GCC: flexible · J Pathol: unstructured ≤300 words | ✔ unstructured, 298 words (trim further if a stricter venue is chosen) |
| Keywords | 5–7 | ✔ 7 keywords |
| Structure | Introduction · Methods · Results · Discussion · Conclusion | ✔ full IMRaD |
| References | GCC: any consistent style · J Pathol/EJC: ≤40–50 | ✔ 10 primary + gene-set resources, Vancouver style |
| Data availability statement | required | ✔ public accessions + open code repository, Zenodo archive planned |
| Funding statement | required | ✔ "None" |
| Competing-interests statement | required | ✔ "None" |
| Ethics / consent statement | required | ✔ not required — public de-identified data only, stated |
| Author contributions | required | ✔ sole author |
| Generative-AI disclosure | required (Wiley/Elsevier policy) | ✔ explicit statement; AI not an author; author takes responsibility |
| Reproducibility | encouraged | ✔ seeded, offline `--check`, independent second implementation |

## 3 · Element counts

- **Abstract:** 298 words (unstructured). Compliant with J Pathol (≤300) and GCC (flexible).
- **Main text:** ~5,900 words excluding tables and references. GCC sets no fixed limit; **for *The
  Journal of Pathology* this would need trimming toward ~4,000** (candidate cuts: condense §3.9 PPARγ
  detail and §2 method prose, moving the full PPARγ arm table and the 22-row evidence catalogue to
  Supplementary Information).
- **Display items:** 1 figure (the evidence-convergence matrix, §3.13) and 12 tables in the body, plus 2 tables in Data availability.
- **References:** 10 numbered primary references plus separately listed gene-set resources and the GEO
  series record.

## 4 · Reporting-guideline note

This is a re-analysis of previously published, publicly deposited datasets, not a de-novo systematic
review, so no single EQUATOR checklist applies in full. Study/dataset selection is stated transparently
in Methods §2.2 (three EMC cohorts on three platform families, with the comparator arm of each named and
the exclusions accounted for). The synthesis is a cross-platform sign-concordance reading rather than a
pooled effect estimate, and the manuscript states in Limitation 2 that the three cohorts are never
pooled. Where a reviewer requests it, a MOOSE- or SWiM-style summary of dataset identification can be
added as a supplementary item.

## 5 · In-silico strengthening — done, and still available

### Done (2026-08-07, offline, $0)

A robustness package was added as Methods §2.10 and Results §3.12, produced by
`nr4a3_fusion_targets_robustness.py` → `nr4a3-fusion-targets-robustness.json` with a `--check` mode.
It closes two of the manuscript's own stated limitations and adds two orthogonal axes:

- **Exact sample-label permutation test** — the self-contained null that preserves gene–gene
  correlation, which the size-matched (competitive) null cannot see. Because the arms are 6-vs-29 and
  10-vs-6, all 1,623,160 and 8,008 label assignments were **enumerated completely**, so the p-values are
  exact rather than sampled. This is the single most reviewer-relevant addition: it directly answers
  Limitation 9, which had conceded the empirical p was "a screen, not a test".
- **Leave-one-out jackknife** over the EMC arm — no row in the panel changes sign when any single EMC
  tumour is dropped.
- **Rank-based re-read** on within-array percentiles — every row keeps its sign, so nothing rests on the
  z-scoring convention.
- **Benjamini–Hochberg** q-values across the per-gene permutation p-values (Limitation 8).

⚠ **It was not uniformly flattering, and the manuscript now says so.** *ENO3* survives everything
(q = 0.0004 / 0.0006); *PPARG* survives on GPL3290; **SEMA3C does not reach significance under the
permutation test on either platform**, and the **PPARγ KO_UP falsifier does not either**. Those two
demotions are stated in §3.12 and back-referenced from §3.5 and §3.9 rather than left in the artifact.

### Also done (2026-08-07) — the NBRE motif scan, via CI

Discussion §4.2 item 4 named an NBRE scan as the paper's free next step. The scanner already existed
(`emc_ret_target_scan.py`, built for the RET lane) with a dinucleotide-preserving shuffle null and a
198-window background panel — but it had **never been run**: its artifact read `_status: NOT_RUN`,
because the Ensembl fetch needs egress the dev sandbox does not have. It was one $0 CI dispatch away.

`SEMA3C` was added to the scanner's focus panel (`ENO3` and `PPARG` were already there), the workflow
was dispatched with `ref=<branch>` so the run used this branch's code, and the module was then extended
to compute the background-panel rank for **every** focus gene rather than for RET alone — the
RET-specific keys and verdict are untouched. Results are Methods §2.11 and Results §3.13:

- ***ENO3*** carries 4 exact NBREs and clears **both** nulls (shuffle p = 0.034; panel p = 0.025;
  GC-matched p = 0.018) — the only class-A gene enriched above its own composition.
- ***PPARG*** carries 3, not above composition. ***SEMA3C*** carries **none**.
- So the sequence axis converges with §3.12: *ENO3* is supported by every instrument applied,
  *SEMA3C* by neither the permutation test nor the motif scan.
- ⚠ Stated in the paper: a motif is not occupancy; *SEMA3C*'s zero does not contradict Brenca *et al.*,
  who reported an NBRE-**like** site; and the hit positions do not reproduce the published coordinates
  for either *ENO3* or *PPARG*.

*(Side finding for the RET lane, not this paper: RET's own window scores `ELEMENT_PRESENT_BUT_NOT_ABOVE_CHANCE`
— 1 NBRE, shuffle p = 0.577, panel p = 0.663. That is the RET lane's answer to its own question and is
recorded in its artifact.)*

### Still available (needs a CI fetch — the sandbox proxy blocks these hosts)

| test | what it would add | cost | gate |
|---|---|---|---|
| **A one-mismatch (NBRE-like) scan with its own null** | The form of site *SEMA3C* was actually reported to carry. Its window has 39 one-mismatch matches, the most of any gene scanned, but no null was computed for that count so it is currently uncalibrated | $0, CPU | sequences already cached — this one is now offline-doable |
| **Intersect with the Haller 2019 NR4A3 ChIP-seq peaks** (Zenodo doi 10.5281/zenodo.1483691, open) | Whether the NR4A3 DNA-binding domain reaches these genes in a human tumour. ⛔ Must be framed exactly as §4.2 frames it — acinic cell carcinoma carries *native* NR4A3, not a fusion, so it can never be cited as a fusion cistrome | $0, CPU | Zenodo blocked in-sandbox (403 at the egress proxy); routable through GitHub Actions |
| **A fourth EMC expression cohort**, if one exists | A further independent replication | $0 | a GEO re-search |

## 6 · Optional presentation work (not required for submission)

- ✅ **A headline figure now exists** — the evidence-convergence matrix (Figure 1, §3.13), dependency-free
  SVG generated from the committed artifacts with a `--check` mode. Converting the instrument-control
  panel (§3.3) into a second figure remains optional.
- **A promoter NBRE-motif scan** of the up-in-EMC genes (Discussion §4.2, item 4) is a no-new-data
  analysis that would add an orthogonal line of evidence; it is named in the manuscript as future work
  and is not required for this submission.
- **In-text citation style.** The manuscript uses a consistent author-name + PMID inline style with a
  full numbered reference list — accepted by GCC at initial submission ("any consistent style"). The
  PMID on each inline citation is a deliberately robust provenance anchor. Converting the in-text
  citations to the journal's numbered superscript (Vancouver) format is a one-pass reference-manager
  step at submission or first revision, and journals reformat references at production regardless.

## 7 · Residual author-only steps before clicking "submit"

These are outward-facing or identity-bound actions that only the author can take; the manuscript
content itself is submission-ready.

1. **Add an ORCID** to the title page and cover letter (bracketed placeholder present).
2. **Mint a Zenodo DOI** by archiving the code repository at the submitted commit, and paste it into the
   Data and code availability section (the section already states this is planned at acceptance; some
   journals prefer the DOI at submission).
3. **Verify the remaining gene-set-resource identifiers** (Enrichr, ChEA, TRRUST, MSigDB Hallmark)
   against their primary sources and add full bibliographic identifiers; the manuscript currently cites
   them to the depth the held source supplies and flags this explicitly, in line with the project's
   citation-provenance discipline.
4. **Elect the subscription (non-open-access) route** at the fee step so no APC is charged, unless a
   full waiver for open access has been secured.
5. **Fill the bracketed fields** in the cover letter (date, ORCID) and confirm the current editor
   addressee on the journal masthead.
6. **Deposit the bioRxiv preprint** and, after it posts, add the preprint DOI to the cover letter.
