---
id: DOC-VACCINE-PATH-2-FINDING
title: "VACCINE-PATH-2 — the calibration material section B1 names is half inadmissible, and the missing half is inadmissible three times over"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# VACCINE-PATH-2 — §B1's own exemplars: 5 of 10 named items can enter a class I benchmark, and the four *EWSR1*::*FLI1* peptides are 17-mers designed without HLA restriction

Writes confined to this directory. Nothing added, committed or pushed; `scripts/preflight.sh` not
run; no manuscript, graph entry, producer, guard, gate, pin or test touched; no subagents; no GPU,
no paid API, no publication act, no outreach; cost $0.

⛔ **No immunogenicity, presentation, tolerance, efficacy, safety, selectivity, therapeutic-window
or clinical-readiness claim is made or implied anywhere in this lane, in either direction.**
A prediction is not a presented epitope. "Admissible" below is a statement about a **record's fit to
a benchmark's inclusion rule** — a bookkeeping property — and never about a peptide, a tumour or a
patient. Route **B8 (HLA-C) stays closed**: no HLA-C data was fetched, derived, substituted or
relabelled here; the one C-restricted census record is *read as already committed by a sibling lane*
and no population quantity is attached to it.

## 1 · The question, and the boundary I drew against the two concurrent lanes

> The vaccine-path manuscript's §B1 does not merely say a benchmark is missing — it **names the
> material** it believes a class I calibration would be built from: "the HLA-A\*24:02-restricted
> SYT-SSX junction peptide [17,18], the four *EWSR1*::*FLI1* breakpoint peptides of the Ewing
> sarcoma case report [20] and the fusion neoantigens of a head and neck series [21]".
> **How many of those named items can enter a class I presentation-percentile benchmark at all** —
> judged from each item's own cited source, against the length window the screen's own predictor is
> configured for?

**Boundary.** HLA-COVERAGE-3 is on producer-drift staleness and NEOANTIGEN-5 on the
`junction_proteome_novelty` guard accession defect. Both are about **this repository's machinery**.
This lane asks nothing about machinery: it audits **a citation-level claim in the manuscript prose**
against the primary sources the manuscript itself cites. No producer, artifact date, guard,
accession or novelty test is read, re-derived or touched here, and no drift or accession question is
answered. The only overlap is the shared, already-committed `epitope-records.json`, which this lane
**re-derives from and does not modify**.

It is also not a restatement of the 15-vs-93 shortfall, not a new baseline review, and not a re-run
of the epitope screen.

## 2 · Paper-level merit

EPITOPE-BENCHMARK settled the *aggregate*: 15 validated class I junction epitopes against 93 needed.
It left standing a **specific, checkable claim in the manuscript's own prose** — and flagged its own
inability to resolve it as limitation (iii): nine PubMed queries returned **no** validated
*EWSR1*::*FLI1* junction epitope, an "unresolved discrepancy with §B1, not a refutation of it".
Resolving it matters at paper level for two reasons. First, an unresolved discrepancy between a
manuscript sentence and a census of the literature is exactly the kind of thing a reviewer finds,
and the resolution here is decisive rather than probabilistic. Second, and more usefully: a reader
of §B1 counts "1 + 4 + a series" and comes away believing the shortfall is one of *degree*. Half of
that count cannot enter a class I benchmark on any reading, which makes the shortfall one of
**kind** in part. Patient relevance is indirect and honest: this changes what a sentence in a
manuscript is entitled to say, and nothing else.

## 3 · The exact evidence gap

Named exactly, and none of it previously retrieved by any lane: **manuscript reference [20],
PMID 42570981** (Calukovic *et al.*, *npj Precision Oncology* 2026;10(1):305,
[DOI](https://doi.org/10.1038/s41698-026-01642-4)) — **absent from EPITOPE-BENCHMARK's entire PMID
set**, which is why that census could not see it; **references [17] / [18]**, PMIDs 15647119 /
22726592, likewise absent from that PMID set (the census reached the same SYT-SSX peptide through
*different* primary papers, PMID 12133991 / 15240740); and the `_predictor` block of
`research/modalities/fusion-breakpoint-neoantigens.json`, whose **length window** had never been
brought into contact with the §B1 exemplar list.

So the discrepancy EPITOPE-BENCHMARK reported was **not** a recall failure of its search. Its search
never had the manuscript's own citation in front of it.

## 4 · Every prior number re-derived before use

| quantity | prior lane | re-derived here | verdict |
|---|---|---|---|
| screen panel sha256 | HLA-COVERAGE-2 `ae1ba4f7…3eec0c` | `ae1ba4f7216a11a956ed978035557c9226826dd93c09a5bcec3421a39d3eec0c` | reproduces |
| panel size / loci | 10 alleles, A and B only, no HLA-C | 10, loci `["A","B"]`, HLA-C count 0 | reproduces |
| predictor length window | 8–11 | `[8, 9, 10, 11]` | reproduces |
| validated set size | EPITOPE-BENCHMARK n = 15 | **15**, same 15 record ids | reproduces |
| Wilson n, width ≤ 0.20 | 93 / 78 / 60 / **34** | **93 / 78 / 60 / 34** (k=round); 93/76/58/**34** (k=ceil); 93/79/60/**38** (k=floor) | reproduces, and matches the parent arbitration on 34 |

**One divergence, and it was mine.** This lane's *first* run (`checks/04-`) added a filter of its own
— requiring `sens*n` to be an exact integer — and returned **94 / 80 / 60 / 40**. That filter is not
part of the criterion and is this lane's defect, not a prior lane's. It is preserved in `checks/04-`
rather than deleted, and `checks/05-` is the corrected run. Nothing in §5 rests on the first run.

## 5 · Result — `b1-exemplar-admissibility.json`

**Rule, fixed before the sources were read** (and identical in substance to EPITOPE-BENCHMARK's):
natural, non-anchor-modified, **sequence known** · spans the junction · **length 8–11**, the window
`_predictor.lengths` actually declares · a named class I allotype · at least one class I measurement.

| §B1 clause | items | admissible | why |
|---|---|---|---|
| SYT-SSX junction peptide [17,18] | 1 | **1** | `GYDQIMPKK`, 9-mer, HLA-A\*24:02, class I-restricted CTL + tetramer |
| four *EWSR1*::*FLI1* peptides [20] | 4 | **0** | see below |
| head-and-neck series [21] | 5 | **4** | `QFIDSSWYL`, `MMYSPICLTQT`, `SLASPLQPT`, `DKESEEEVS`; `SLASPLQSWYL` is binding-only and excluded |
| **total** | **10** | **5** | |

### The four *EWSR1*::*FLI1* peptides fail on three independent grounds, from the paper's own Methods

According to PubMed, reference [20]'s full text (PMC13452805,
[DOI](https://doi.org/10.1038/s41698-026-01642-4)) states, verbatim:

* *"four overlapping **17-mer** peptides by a sliding-window approach"* — **outside** the predictor's
  declared 8–11 window; the screen could not score them even in principle;
* *"To ensure broad applicability, the vaccine was designed **without HLA restriction**"* — there is
  **no class I allotype** to calibrate against;
* immune monitoring *"detects … T-cells in an **HLA-independent** manner"*, the reported responses
  are *"de novo polyfunctional **CD4⁺** T-cell responses against all four fusion-derived peptides"*,
  and the Discussion attributes the absence of CD8⁺ reactivity to *"the **class II** binding
  properties of the selected peptides"* — **no class I measurement exists** to admit.

Any one of the three is disqualifying. **EPITOPE-BENCHMARK's limitation (iii) is therefore
resolved, and in the direction that leaves its n = 15 intact**: its search did not miss four class I
epitopes; there are no class I *EWSR1*::*FLI1* junction epitopes in [20] to have missed. The census
count does not move.

### What it does to the reading of §B1

§B1 offers these three clauses as *the* experimentally validated material a class I threshold could
be calibrated on. **Five of the ten named items qualify**, and the largest single contributor —
the item the sentence quantifies as "four" — contributes **zero**. Set against the criterion already
preregistered by the run itself, the position is:

| | n | achievable 95% CI half-width regime at sensitivity 0.5 |
|---|---|---|
| §B1's own admissible exemplars | **5** | width **0.6517** |
| full census (EPITOPE-BENCHMARK) | **15** | width **0.4507** |
| preregistered floor | 30 | width **0.3369** — *the floor itself fails the width criterion* |
| required (k=round) | **93** | ≤ 0.20 |

The third row is worth one sentence on its own: **the preregistered `min_n = 30` cannot satisfy the
preregistered width ≤ 0.20 at the sensitivity where the cut is actually decided.** That is an
internal inconsistency in the run's own gate, re-derived here, and it is independent of how many
epitopes the literature holds.

**No conclusion is drawn about whether any peptide is presented, immunogenic or tolerated.** That
[20]'s peptides are class II-shaped says nothing about *EWSR1*::*NR4A3*, about EMC, or about whether
class I junction epitopes exist for any fusion. It says only that these four cannot serve as class I
calibration material.

## 6 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `b1-exemplar-admissibility.json`, `b1_exemplar_admissibility.py`, and `checks/`
  (5 attempts, all preserved, including the divergent `checks/04-`).
* **Validation / baseline.** Baseline is the manuscript's own §B1 sentence and its own references.
  Validation is (i) full re-derivation of five prior-lane quantities from their underlying artifacts
  before any use (§4, all five reproduce); (ii) the admissibility rule is executed in code over the
  committed census and returns **the same 15 records** EPITOPE-BENCHMARK reported, so the rule is
  calibrated against a known answer before being applied to the §B1 list; (iii) the disqualifying
  facts for [20] are **verbatim quotations from its own Methods and Discussion**, not inference from
  its abstract; (iv) the rule discriminates — it rejects an anchor-modified peptide (E27), a
  binding-only peptide (E17), and two measured records whose sequences were never recovered
  (E29, E30) — so it is not a rule that says "yes".
* **Provenance.** PubMed/PMC MCP server (the admitted route), 2026-09-09: metadata for PMIDs
  42570981, 15647119, 22726592, 31011208, 23252384; full text for PMC13452805. According to PubMed.
  `research/modalities/fusion-breakpoint-neoantigens.json` (sha256 recorded in the artifact);
  `…/EPITOPE-BENCHMARK/epitope-records.json`; `research/manuscripts/neoantigen/emc-vaccine-development-path.md`
  §B1 and references 17–21. No direct HTTP was attempted, so no refusal was encountered or worked
  around. No HLA-C data acquired.
* **Limitations.** (i) The E1–E4 **sequences** sit in a table not carried in the PMC text body, so
  they are **UNKNOWN** to this lane — not zero, not empty. Their length (17) and the absence of any
  HLA restriction are stated in the running text and are the only facts the rule needs; if a future
  reader recovers the sequences, nothing here changes, because a 17-mer is outside the window
  whatever it spells. (ii) Admissibility is judged **as reported**; I did not re-verify that any
  cited assay was correctly performed. (iii) The head-and-neck attributions are taken from
  EPITOPE-BENCHMARK's committed records, which flag partial gene-symbol redaction in PMC for three
  ACC peptides; that caveat travels with row 3. (iv) `n = 5` and `n = 15` are **lower bounds**, since
  both censuses are bounded by search recall — the safe direction for a shortfall reading.
  (v) Nothing here is evidence about IEDB's contents; IEDB was never reached.
* **Stop condition.** Reached, and this lane stops. The named discrepancy is resolved decisively
  from the manuscript's own citation, and the resolution needs no further retrieval. What remains is
  a **paper-owner prose decision**, not a computation.

## 7 · Proposed, UNAPPLIED — no shared file was edited

No manuscript, graph entry or shared script was modified, and this lane proposes no diff to any
guard, gate, matcher, pin or test. One prose correction is offered for the paper owner's judgement,
to replace the §B1 sentence beginning "The experimentally validated fusion-junction epitopes in the
literature are individual sequences across a few fusions":

> *"The experimentally validated class I fusion-junction epitopes in the literature are individual
> sequences across a few fusions: the HLA-A\*24:02-restricted SYT-SSX junction peptide [17,18] and
> four class I-restricted junction neoantigens of a head and neck series [21]. The off-the-shelf
> Ewing sarcoma construct [20] cannot serve as calibration material for a class I cut: its four
> breakpoint peptides are 17-mers designed without HLA restriction, monitored by an HLA-independent
> assay, and the responses reported are CD4⁺, which its authors attribute to the class II binding
> properties of the peptides. A handful of epitopes is not a set against which a threshold can be
> calibrated."*

Whether it belongs in the manuscript is the paper owner's call; §6's limitations travel with it.

## 8 · Next credible independent work (not done here, not authorised here)

1. **The `min_n = 30` inconsistency in §5** is a one-line prereg observation the paper owner may want
   recorded: a floor that cannot meet the run's own width criterion can pass a set that fails it.
2. Recover the E1–E4 sequences from the reference [20] supplementary table on the CI runner. This is
   completeness only; it cannot change the admissibility verdict.
3. §B2 cites [17,18,20] together for the weakness of vaccination-based presentation evidence. That
   use of [20] is sound and is **not** affected by anything above.
