---
id: DOC-EMC-MTAP-PRMT5-DECLINE-INTEGRITY
title: "Grounds to decline — integrity and reproducibility lens (emc-mtap-prmt5-hypothesis.md)"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: An adversarial integrity audit hunting untraceable numbers, internal contradictions and misdescribed sources in the PRMT5 manuscript.
scope: Review of one manuscript. Reports no new result and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

# Grounds to decline — integrity and reproducibility lens

> **THIS IS A SIMULATED INTERNAL REVIEW, WRITTEN BY AN AI REVIEWER AT THE AUTHOR'S REQUEST. IT IS
> NOT CORRESPONDENCE FROM *GENES, CHROMOSOMES AND CANCER* OR FROM ANY OTHER JOURNAL, NOT A REAL
> PEER REVIEW, AND NOT A DECISION. No editor, no journal and no external referee has seen this
> manuscript. It exists to find the objections a referee would raise before one does.**

*Round one is [`emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md`](./emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md);
the author's reply is [`emc-mtap-prmt5-hypothesis-review-response-2026-08-10.md`](./emc-mtap-prmt5-hypothesis-review-response-2026-08-10.md).
This review is not a repeat of round one. It asks one question only: **can the document be trusted
to say the same thing twice and to mean what its artifacts say?***

---

## 1 · Verdict

**Not yet submittable — but the defect profile is much better than the volume of findings suggests,
and nothing found here touches a result.**

I made **229 checks** against the committed artifacts, covering every number in the manuscript, the
SI and the five figure captions, plus **20 checks on the figures themselves**. Several rows in the
table below cover a whole sub-table at once, so the count of distinct values behind those 229 checks
is over three hundred.

**212 of the 229 agreed exactly**, at the stated rounding, against the artifact that owns them.
**Sixteen disagreed, were misdescribed, or are a live superseded value; one could not be traced to
any artifact at all.** Of the sixteen, only **five are numeric**: a superseded class ranking still
live in the SI, one quantity reported at two different values, a rounded lower bound asserted as a
bound, a count whose descriptor contradicts its source, and a mis-stated family size. The other
eleven are misdescriptions of a cited source or of an artifact, one dangling cross-reference, and two
claims about the checking machinery that the machinery does not support. Of the 20 figure checks, 15
passed, four are presentation defects and one is a gap in the checking tool.

**No statistic in the Results section is wrong.** Every *t*, Δ, exact *p*, adjusted *p*, percentile,
genome-wide rank, dependency fraction, per-class median and motif count reproduces. The five
committed figures regenerate **byte-identically** from the committed artifacts — I re-ran the
generator in an isolated copy of the tree and every PNG hash matched.

What fails is the layer above the numbers: **the paper's account of its own checking**. §2.6 still
makes a universal verification claim that this review falsifies for the second time; the corrections
register claims that claim was weakened and it was not; and the one superseded value the register
says was retired is still sitting in the SI, contradicting the main text. In a paper whose entire
warrant is "every value resolves to a committed artifact", that is the exact failure a referee
punishes hardest, because it is the claim the reader cannot check for themselves.

**Recommendation: minor revision.** Every item below except one is a text edit against an artifact
that already exists. The manuscript should not go out until G1, G2, G3 and G4 are closed.

---

## 2 · GROUNDS TO DECLINE

### G1 · A superseded value that the paper's own register says was retired is still live in the SI, and it contradicts the main text — **FIXABLE**

**Location.** [`emc-mtap-prmt5-hypothesis-SI.md`](./emc-mtap-prmt5-hypothesis-SI.md) §S4, line 125:

> "…the group score hid a signal its decisive gene (PRMT5) does have, since pooled across four genes
> **EMC ranks second of four comparator classes** while PRMT5 alone is highest."

**What is wrong.** That is the pre-revision claim. The main text §3.4, the Figure 4 caption, SI §S5b
and SI §S6 all now say **third of the five tumour classes**, below desmoid fibromatosis *and*
solitary fibrous tumour. Both the main text Appendix A (row 3) and the SI's own Appendix S1 (row 4)
register the change explicitly — and then the running text of §S4 keeps the retired form. The two
submitted files therefore disagree with each other on a corrected claim, and the SI disagrees with
itself two sections apart.

**Artifact checked.** `research/modalities/emc-prmt5-multiplicity.json` →
`per_platform.GSE24369_series_matrix.txt.gz.per_class_medians_methylosome_pooled.per_class`: desmoid
fibromatosis **0.9496**, solitary fibrous tumour **0.9354**, EMC **0.9283**, LGFMS 0.8582,
myxofibrosarcoma 0.8252, pooled skeletal muscle 1.1127. EMC is third of five tumour classes. §S4's
"second of four" is not what the artifact says.

**Why it survived, which matters more than the line itself.** CLAUDE.md rule 1.3 requires a
corrected number's old value to be added to
[`pinned-figures.json`](../pinned-figures.json) → `superseded` **in the same commit**, because that is
how CI finds the copies you missed. I read all 64 `superseded` entries: **not one of them relates to
this manuscript.** And `pinned-figures.json` → `targets` lists
`research/manuscripts/emc-mtap-prmt5-hypothesis.md` but **not the SI**, so the SI is outside
`lint_consistency.py` altogether. The gate that exists to catch precisely this was given nothing to
catch it with, and the value it would have caught is in the file it does not read. `lint_consistency`
returns 0 ERROR over 17 files and is right to: it was never told.

---

### G2 · §2.6 still makes a universal verification claim, and the register's account of how that claim was weakened is false — **FIXABLE**

**Location.** §2.6, paragraph 2, first sentence; main text Appendix A row 1; SI Appendix S1 row 1;
and the review response's M1.

**What is wrong.** Round one falsified the sentence *"The author verified every reported value
against the committed artifact that produced it."* The response states that the sentence "has been
rewritten to say what was checked" and that "a blanket claim that everything was verified is exactly
the claim this incident refutes, **so the paper no longer makes it**." Appendix A row 1 says the same:
the sentence was rewritten "to describe what was checked rather than to assert that everything had
been."

The live sentence is:

> "**Every** statistic, percentile, count and dependency figure reported here **was checked against
> the committed artifact that owns it**…"

That is the same universal claim with the quantifier moved from "value" to a four-item enumeration
that between them covers essentially every number in the paper. Nothing was weakened. So the
manuscript asserts a blanket verification, and its own appendix asserts that it does not — a
self-contradiction inside the section whose subject is the paper's trustworthiness.

**And the assertion is again false on its own terms.** G3 below is a *count* that the paper reports
at two different values in two places; G7 is a *count* (2 of 3, coverage 0.667) whose consequence is
attributed to the wrong criterion of the artifact that owns it; G8 is a *count* (eight) whose
descriptor contradicts the artifact it is attributed to. A per-value check of the kind §2.6 describes
would not have caught G3 — which is the honest point the sentence should make, and does not.

**What a referee will conclude.** Round one found one number that traced to no artifact and observed
that "a referee who found one such number will assume there are others." The revision found and fixed
that number, then re-asserted the claim it had just been shown could not be supported. The fix here is
one sentence and it is free.

---

### G3 · One quantity, two values, in the same Methods section: GPL6244's mapped-symbol universe is both 18,688 and 18,724 — **STRUCTURAL** (disclosure is available offline; reconciliation is not)

**Location.** §2.3, two paragraphs apart; SI §S5c; main text Appendix A row 2.

- §2.3: "**18,688** symbols were scored on GPL6244, and 14,404 of the 14,932 carrying a probe on
  GPL3290."
- §2.3, next paragraph: "…against **mapped-symbol universes of 18,724 and 14,932**."
- Appendix A row 2: "**18,688 scored of 18,688 with a probe** on GPL6244; 14,404 scored of 14,932 on
  GPL3290."
- SI §S5c: "…against mapped-symbol universes of **18,724** and 14,932."

GPL3290 is consistent at 14,932 on both sides. GPL6244 is not: the paper says the platform maps
18,688 symbols and that its universe is 18,724, and a reader cannot tell which denominator the
"lower bound" argument, the "about a third of each array" fraction in §4.4 and the "roughly a quarter
of each array" fraction in SI §S5c are computed against.

**Artifacts checked, and the cause, with evidence.** Both values are real and neither is fabricated —
they come from two different resolutions of the same platform table:

| value | artifact | key | that artifact's fetch stamp |
|---|---|---|---|
| 18,688 | `emc-expression-panels.json` | `platforms.GSE24369….genome_wide_null.n_symbols_with_a_probe` | `generated_utc` **2026-08-09T18:41:04+00:00** |
| 18,724 | `emc-hypoxia-null-background.json` | `targets.GSE24369…._n_symbols_on_platform` | `_generated_utc` **2026-08-07T17:01:43+00:00** |

The same two files also disagree on the probe count that maps to a symbol — 20,221 against 20,235 —
which is the discriminating observation: the accession→symbol bridge was re-resolved between the two
fetches. The SI's own Appendix S1 narrates that volatility (four re-runs on 2026-08-09 resolving
0.984, 0.931, 0.931 and 0.981 of GPL6244's accessions, two of them returning zero gene links). So the
multiplicity correction's random half was drawn from a **14-day-older, 36-symbol-wider** universe than
the one the genome-wide placement scored, and the manuscript nowhere says so.

**Why STRUCTURAL.** The merge itself is properly guarded — `emc_prmt5_multiplicity._merge_caches`
refuses unless the two caches agree on samples, sample order, per-sample background and every value
of every shared symbol, and it recorded 497 and 526 shared symbols agreeing. The science is not
affected at 0.2 % of the denominator. But *reconciling* the two universes needs the platform table
re-fetched, which is a network read this environment cannot make and the manuscript's own record says
is unreliable. What is available offline is disclosure, and disclosure is what is missing.

---

### G4 · Reference [18] is described as supporting more than it does, in three separate ways — **FIXABLE**

**Location.** §4.2, paragraph 1; and the abstract's closing sentence.

> "…drug sensitivities to carfilzomib, doxorubicin **and venetoclax**, with **two synergistic pairs**
> among them, were validated **in both** by the group that established them [18]. Adding one
> clinical-stage PRMT5 inhibitor to **a screen that already runs**…"

Abstract: "…one clinical-stage PRMT5 inhibitor added to **a screen already running** on published EMC
models."

**Source checked.** The committed full text of reference [18] on the `literature-cache` branch under
`literature/bangerter-2023-emc-exvivo/`. Verbatim, from its Results:

1. "…while there was **no response to venetoclax as a monotherapy in the validation**." The
   manuscript's sentence tracks that paper's *Methods* line ("Drug sensitivities for carfilzomib,
   doxorubicin and venetoclax were validated in a 96 well format…"), which names what was *tested*.
   The paper's Results say venetoclax was a validated **non**-responder. Listing it as a validated
   sensitivity reverses the finding.
2. "Drug synergy was found for **USZ20-EMC1** cell models using both combinations… and an **additive
   effect in the USZ22-EMC2** model." So: two pairs, synergy in **one** model, additive in the other.
   "two synergistic pairs… validated in both" is not what the source reports.
3. The screen was a one-off 40-drug medium-throughput panel run on sarco-spheres at passage 5 and
   published in 2023. **"a screen that already runs" / "a screen already running" is a present-tense
   assertion about the current state of another laboratory that no source in this repository
   supports.** It is also the load-bearing word in the paper's affordability argument — "among the
   smallest asks available in this disease" — and it is in the abstract.

**Everything else in the citation set is accurate**, and unusually so. I checked [1], [3], [8], [9],
[11] and the prior-art screen against their committed verbatim records; see the table in §3. Two
points of positive note: the [3] quotation reproduces the source's own typographical error and marks
it `[sic]`; and §4.2's "the combination's cytotoxicity was only partially rescued by fusion depletion"
matches [3] exactly ("Combination GSK591 and olaparib treatment was partially rescued by EWSR1::FLI1
depletion"), which is a distinction the source itself draws and which an over-claiming author would
have flattened.

---

### G5 · §4.1 says three of the four methylosome members are "flat or lower in EMC"; §3.5's own table says two of them are higher — **FIXABLE**

**Location.** §4.1, paragraph 3: "…*PRMT5* is the gene the rationale depends on, and **the other
three members are flat or lower in EMC and dilute it**."

**Artifact checked.** `emc-expression-panels.json` → `gene_reads`, GPL6244:

| member | Δ (SD) | *t* | where the manuscript itself reports it |
|---|---:|---:|---|
| PRMT5 | +0.2632 | +6.24 | §3.5 |
| **WDR77** | **+0.0979** | **+2.82** | §3.5 table, "top 20.5%" |
| **CLNS1A** | **+0.0883** | **+2.53** | not reported in the main text |
| RIOK1 | −0.0880 | −1.64 | not reported |

Only RIOK1 is lower. WDR77 and CLNS1A are both **higher in EMC**, at *t* = 2.82 and 2.53, and the
manuscript prints the WDR77 figure two sections earlier in its own table. They dilute the group mean
because they are *smaller*, not because they are flat or negative — and that is a different, weaker
and more defensible statement. As written, the Discussion contradicts the Results table.

---

### G6 · Figure 1's caption and in-figure title both claim "every tumour", and the figure draws 35 of the 40 deposited tumours — **FIXABLE**

**Location.** Figure 1 caption ("**Every tumour on both platforms.**") and the rendered figure's own
suptitle ("Every tumour, on both platforms. Bars are medians.").

**What is wrong.** GSE24369 deposits 42 samples: 40 tumours plus two pooled skeletal-muscle RNA
samples. Figure 1 plots the panel's arms only — 6 EMC + 29 comparators = **35** — so the five
solitary fibrous tumours are absent from a figure that says every tumour is present. I confirmed this
from the generator (`emc_mtap_prmt5_figures._samples` reads
`panel["gene_reads"][gene][plat]["per_sample"]`, whose GPL6244 list is 35 entries long) and by
counting the per-sample records directly.

**Why this is more than pedantry.** This is the same defect Appendix A row 3 registers and corrects
**for Figure 4** — "The figure drew only the samples in the panel's arms" — and the correction was not
carried across to Figure 1, whose caption makes the stronger claim of the two. The fix is one clause;
the finding is that the sweep stopped at the figure the reviewer named.

---

### G7 · §3.1 attributes the locus group's suppression on GPL3290 to the coverage floor; the artifact says coverage passes and the gene-count floor fails — **FIXABLE**

**Location.** §3.1, final paragraph: "On GPL3290 only two of three are readable, **which falls below
the panel's coverage floor**, so no score is emitted."

**Artifact checked.** `emc-expression-panels.json` →
`panels.mtap_prmt5.groups.the_locus.per_platform.GSE4303-GPL3290….` records `coverage: 0.667` and the
verdict "⛔ UNDERPOWERED — 2/3 genes readable on GPL3290 (coverage 0.667); **the floor for a curated
panel is 3 genes and 0.5 coverage**." The manuscript states that rule correctly in §2.1 and SI §S2
("at least three genes are readable **and** coverage is at least 0.5"). Coverage 0.667 **clears** the
0.5 floor; what fails is the three-gene minimum. §3.1 names the one criterion the group passed.

---

### G8 · §1.1's "eight systemic classes in clinical use" misdescribes the census it cites, whose eight include surgery and radiotherapy — **FIXABLE**

**Location.** §1.1, sentence 3: "The modality census described in section 1.3 counts **eight systemic
classes in clinical use** for this disease, of which only that one carries a meaningful response
record."

**Artifact checked.** [`cancer-modality-census.md`](../modality-census/cancer-modality-census.md) line 131: "⚠ **And the
incumbent arsenal is 8 classes.** … multi-kinase antiangiogenic inhibitors, anthracyclines,
alkylators, a minor-groove binder, a KIT inhibitor used once under a biomarker restriction, interferon
in case reports, **radiotherapy, and surgery**." Two of the eight are local therapies. The systemic
count is six. Line 62 of the same file confirms the row label — `● in_clinical_use — the incumbent
arsenal | 8`.

The trailing clause is right: the census says "Of those, one class carries the disease's only
meaningful systemic response record." The count is right. **The word "systemic" is not**, and it was
added by this revision — Appendix A row 9 records the change from "The systemic classes with any
disease-specific evidence number about eight" to the present wording and calls it "Same number, now
attributed to the source that holds it." The number is the same; the attribution introduced an error
the earlier phrasing did not have.

---

### G9 · Falsifiers F3 and F4 are still written on a unit of evidence the paper has explicitly demoted — **FIXABLE**

**Location.** §4.3, rows F3 and F4, read against §3.4.

§3.4 concludes: "a curated group score is treated here as **a summary and not as a unit of
evidence**." §4.1 and §5 both restate the surviving rationale on *PRMT5* alone rather than on the
methylosome group, and Appendix A row 12 registers that change as one of the revision's corrections.

But the falsifier table still reads:

- **F3** — claim "the methylosome reads high in EMC"; killer "a third EMC series in which **the PRMT5
  group** is null or lower".
- **F4** — claim "the MTAP locus reads low in EMC"; killer "a third series in which **the locus group**
  is null or higher".

Both are stated on group scores. F3's claim is also unqualified where §3.4 and §4.1 both qualify it
("per class the group does not separate this disease"). F4 is a falsifier for a rationale that F5, in
the next row, records as **already fired** and closed. So two of the ten rows test claims the revised
paper does not make, and one of them tests a claim the table itself declares dead one line later.

**Everything else in that table checks out**, including the numbers inside it: F7's "6.24 to 5.23,
*n* = 35" and "6.67 to 2.71, *n* = 16" match `emc-prmt5-route-controls.json` exactly; F8's
near-universal dependency matches `depmap-sarcoma-dependency.json`; F9's and F10's "partially
answered"/"contradicted at one point already" match §3.7 and the motif artifact. The four rows marked
fired or partially fired are correctly marked **on the revised numbers**.

---

### G10 · §3.1 cites [3] for a proposition that is not in that source's own citation ledger and that the source states only in passing, about a different set of enzymes — **FIXABLE**

**Location.** §3.1, last paragraph: "…elevated **methylosome** expression is reported **across many
malignancies** [3]." Repeated in SI §S7 item 4.

**Source checked.** The committed full text of [3]. Its Introduction says: "elevated expression of
**PRMTs** highly associated with the development, pathogenesis, and drug resistance of adult solid and
haematological cancers ( )" — a general remark about PRMTs, attributed by [3] to a citation of its
own, not a result of [3]. What [3] *measures* is narrower and the manuscript quotes it correctly
elsewhere (§1.2, §4.4): PRMT5, PRMT1 and MEP50 higher across multiple **sarcoma** types than in breast
and lung cancer.

I also checked `research/literature/mtap-prmt5-emc-citations.json`, the paper's own citation anchor.
Its `cited_for` list for [3] carries five propositions and **none of them is this one**. So the
manuscript uses its most load-bearing reference for a claim its own ledger does not record it as
supporting, and generalises "PRMTs" to "the methylosome" and "sarcomas" to "many malignancies" in the
same sentence. The safe form is available and costs nothing: cite [3] for the sarcoma comparison it
made.

---

### G11 · No executable gate in this repository reads a number out of this manuscript's prose and compares it to an artifact — **STRUCTURAL**

**Evidence.** I ran all five gates against the current tree:

| gate | result | what it can say about this manuscript |
|---|---|---|
| `lint_consistency.py` | 0 ERROR, 17 targets | the manuscript is a target, but `pinned-figures.json` registers **zero** pinned figures, derivations or superseded values for it, and the **SI is not a target at all** |
| `lint_citations.py` | 798 prose identifiers, 83 unanchored | checks identifier *provenance*, never a statistic |
| `lint_style.py` | 0 ERROR, 13 files | checks register, never a value |
| `systems_check.py --check` | 0 ERROR, 72 WARN | graph integrity, no manuscript numbers |
| `emc_systems_map_check.py --check` | 0 ERROR | registry coverage, no manuscript numbers |
| `emc_mtap_prmt5_figures.py --check` | OK | hashes the five **source artifacts**; see G12 |
| `emc_prmt5_multiplicity.py --check` | REPRODUCES | recomputes the correction from the committed cache — **the one real numeric check that exists** |

So the manuscript's central promise — §2.6's "every… was checked against the committed artifact that
owns it" — rests entirely on a manual pass, and that pass has now missed something twice: once in
round one (a Methods count traceable to nothing) and once here (G1, a superseded value, in the file no
gate reads). This is structural because no edit to the manuscript supplies the assurance; the
machinery has to be built, and rule 1.3's registry is the place it belongs.

---

### G12 · The figure-provenance record fingerprints the artifacts and never the images, and both the SI and the tool's own output describe it as if it did — **FIXABLE**

**Location.** SI §S6, closing sentence; `mtap-prmt5-figure-provenance.json`;
`emc_mtap_prmt5_figures.check()`.

SI §S6: "Provenance hashes for all five are stamped in
`research/manuscripts/figures/mtap-prmt5-figure-provenance.json`, and `--check` compares them against
the artifacts, **so a stale figure is detectable**."

`check()` compares `stamped["sources"]` — five SHA-256 prefixes of the five **input artifacts** —
against the artifacts as they stand. **No image file is hashed at any point.** The `figures` key lists
ten filenames and nothing is ever computed from them, yet the tool prints "OK — **10 files match** 5
committed artifacts", which reads as a statement about the ten files. A figure edited by hand, or left
over from an earlier run of the generator against the *same* artifact, passes.

**In fact the figures are current, and I verified it the only way that settles it.** I copied
`research/` into an isolated tree, ran the generator, and compared: all five PNGs are **byte-identical
SHA-256** to the committed ones, and the regenerated provenance JSON is identical too. So this is a
claim that overstates its instrument, not a stale figure. Adding the image hashes to the stamp is a
few lines and would make the sentence true.

---

### G13 · Declarations are incomplete against Wiley's standard set — **FIXABLE**

**Location.** §6.

**Present and correct**: competing interests; funding; ethics (no human subjects, no animal work, no
identifiable patient data, all data public and de-identified at source); author contributions;
generative-AI pointer to §2.6; data availability as §8 with a per-value artifact table.

**The AI disclosure is genuinely good and I want that on the record.** Checked against
`research/literature/ai-disclosure-policies-2026-08-10.json`, which records Wiley's three required
elements verbatim: purpose ✅ (§2.6 names the tool and the mode of use), influence on key arguments or
conclusions ✅ (§2.6 records that two corrections in Appendix A "were found during figure preparation,
after the prose had been written the other way" — few disclosures anywhere are this specific), how the
author verified the output ✅ in form, though see G2 for whether the sentence is true. Not an author,
stated ✅.

**Missing or misplaced:**

1. **No patient-consent statement.** The ethics paragraph implies it; Wiley expects a named line, and
   "not applicable — no human participants" is the whole fix.
2. **No permission-to-reproduce statement.** No third-party figure or table is reproduced, so this is
   again one line.
3. **No clinical-trial-registration line.** A trial identifier is cited in §1.1 as *someone else's*
   trial; a "not applicable" line prevents the misreading.
4. **§6 does not point at §8.** The data-availability statement exists and is unusually thorough, and
   a reader looking in Declarations will not find it.
5. **Author contributions are not in CRediT terms.** "Sole author: conception, analysis, figures and
   writing" is complete in substance; Wiley's submission form asks for CRediT roles.
6. **No ORCID.** The cover letter discloses this ("no ORCID accompanies this submission"), which is
   honest and consistent — but many Wiley journals require an ORCID for the submitting author at the
   portal, and this will surface as a submission-time block rather than an editorial one.
7. **The preprint intent lives only in the cover letter.** The manuscript itself says nothing about
   bioRxiv deposition.

---

### G14 · SI §S1 makes a claim about DepMap that I could not trace to any committed artifact — **FIXABLE**

**Location.** SI §S1, paragraph 3: "The one line on the curated record labelled EMC is recorded by
Cellosaurus as not harbouring an EWSR1 fusion, **and it carries no CRISPR data**."

**What I checked.** The first clause is fully traceable and verbatim: `depmap-target-expression.json`
and `emc-surfaceome-scan.json` both carry `_identity_correction` with the Cellosaurus caution quoted
in full for that line. The second clause I could not verify. I searched every tracked `.json`, `.py`
and `.md` in the repository for that line's model and name identifiers alongside any CRISPR,
gene-effect or dependency term and found nothing;
`depmap-sarcoma-dependency.json` records `n_sarcoma_models: 176` and `n_sarcoma: 91` per gene but
enumerates no model.

**This is "could not verify", not "wrong".** The claim is very likely true and is not load-bearing —
the section's conclusion (no usable EMC dependency observation exists) stands on the fusion caution
alone. But it is a factual assertion about a public dataset with no artifact behind it, in a
supplement whose §S8 opens "Every number in the main text and in this supplement resolves to one of:".

---

### G15 · Two small numeric and cross-reference defects in the SI — **FIXABLE**

1. **SI §S5c, family-size sensitivity.** "…on GPL3290 it is 0.037, 0.062 and 0.208 **over the same
   three family sizes**." The three GPL6244 sizes are 250, 1,000 and **3,973**; the GPL3290 sizes in
   `emc-prmt5-multiplicity.json` →
   `per_platform.GSE4303….max_statistic_permutation.family_size_sensitivity` are 250, 1,000 and
   **3,640**. The three *p* values are all correct (0.0368, 0.0622, 0.2079); "the same three family
   sizes" is not.
2. **SI Appendix S1 cites "§S11", which does not exist.** The SI runs §S1–§S10 then Appendix S1. The
   row's subject — the status line recording that the added panel members were fetched on 2026-08-09 —
   is now the last paragraph of §S10.

---

### G16 · Presentation defects that will draw a referee's eye — **FIXABLE**

1. **Figure 2 has no legend and no statement that its bars are medians**, in either the image or the
   caption. Figure 1 has both. A reader who meets Figure 2 first has no key, and the mark convention
   (filled circle = EMC, open square = comparator) is defined only in Figure 1.
2. **Figure 2 and the §3.2 table appear to disagree for MTAP on GPL6244 unless the reader supplies the
   mean/median distinction themselves.** The table reports Δ = **+0.053 SD** (EMC higher); the figure's
   median bars are EMC **0.541** against comparator **0.564** (EMC lower). Both are correct — I computed
   the medians from `gene_reads.MTAP…per_sample` — and the gap is exactly why "flat" is the right word.
   Saying "bars are medians; the tabulated Δ is a difference of means" in the caption removes the
   apparent contradiction.
3. **Figure 4 separates the normal-tissue class from the comparator classes by hue alone.** The
   generator's own rule, written into the source as a ⛔ comment, is that "SHAPE AND FILL CARRY THE
   SERIES, NOT HUE" so the figure survives greyscale printing — and it is obeyed for EMC vs comparator
   (filled circle vs open square) and broken for pooled skeletal muscle, which is an open square in
   gold. The class label on the x-axis rescues identity; the "not a comparator" signal does not
   survive. Figures 1, 2, 3 and 5 are greyscale-safe; type sizes are legible at single-column width in
   all five.
4. **Figure 4's in-figure caption still carries the pre-correction framing** — "Pooled, EMC does not
   separate from desmoid fibromatosis" — omitting solitary fibrous tumour, which now also sits above
   EMC and which the manuscript caption names. The image text and the manuscript caption should agree.
5. **No table in either file is numbered**, so nothing can be called out by number in the text or by a
   referee.

---

### G17 · Two precision points — **FIXABLE**

1. **The abstract rounds a lower bound upward and then asserts it as a bound.** "family-wise adjusted
   *p* **at least 0.21** and 0.24" against `whole_array_lower_bound` = **0.2081** and 0.2376. 0.2081 is
   less than 0.21, so "at least 0.21" claims marginally more than was measured. It is inside the Monte
   Carlo standard error (0.0029) and nobody's conclusion turns on it, but "at least" is a word that
   invites the check. "0.21 and 0.24" without "at least", with §3.5 carrying the lower-bound
   explanation, is both true and simpler.
2. **"Sixteen" denotes two different populations in the same abstract.** "(16 EMC tumours, two
   platforms)" is 6 + 10 across both series; "removes most of it on the **16-tumour** one" is GPL3290's
   16 *samples*, of which 10 are EMC. §4.4 opens "The evidence base is sixteen tumours" and means the
   first. Both usages are literally correct and they will be conflated. Naming the platforms by their
   sample counts once, in §2.1, and then by accession thereafter would end it.

---

## 3 · Every number traced

229 checks in §3.1–§3.6, and 20 figure checks in §3.7. **✅ = agrees with the artifact at the stated
rounding. ❌ = disagrees, is misdescribed, or is a live superseded value. ⚠ = could not be traced.**
Some rows cover a whole sub-table, and say so. Artifact paths are relative to the repository
root; `panels` = `research/modalities/emc-expression-panels.json`, `multi` =
`research/modalities/emc-prmt5-multiplicity.json`, `controls` =
`research/modalities/emc-prmt5-route-controls.json`, `dep` =
`research/modalities/depmap-sarcoma-dependency.json`, `motif` =
`research/modalities/emc-prmt5-substrate-motif-map.json`, `cites` =
`research/literature/mtap-prmt5-emc-citations.json`.

### 3.1 · Abstract

| value | where | artifact · key | agrees |
|---|---|---|---|
| 16 EMC tumours | abstract | `panels` → `platforms.*.n_EMC` = 6 + 10 | ✅ |
| *t* = 6.24 | abstract | `panels` → `gene_reads.PRMT5.GSE24369….welch.t` = 6.236 | ✅ |
| *t* = 6.67 | abstract | `panels` → `gene_reads.PRMT5.GSE4303….welch.t` = 6.674 | ✅ |
| adjusted *p* "at least 0.21" | abstract | `multi` → `…adjusted_p.PRMT5.whole_array_lower_bound` = 0.2081 | ❌ bound rounded up (G17) |
| adjusted *p* 0.24 | abstract | same, GPL3290 = 0.2376 | ✅ |
| exact *p* 0.000142 | abstract | `controls` → `…exact_permutation_PRMT5.exact_p_two_sided` | ✅ |
| exact *p* 0.000125 | abstract | same, GPL3290 | ✅ |
| twelve-gene proliferation adjustment | abstract | `controls` → `…proliferation_control.genes_used` (12) | ✅ |
| 35-tumour platform | abstract | `panels` → GPL6244 `n_EMC` 6 + `n_comparator` 29 | ✅ |
| 16-tumour platform | abstract | `panels` → GPL3290 `n_samples` 16 | ✅ (see G17.2) |
| eleven GRG sites | abstract | `motif` → `wild_type_proteins.EWSR1.motif_counts.GRG` = 11 | ✅ |
| all beyond residue 300 | abstract | `motif` → `first_occurrence_residue.GRG` = 301 | ✅ |
| commonest EMC fusion retains four | abstract | `motif` → `fusion_constructs[EWSR1_NR4A3_type1]…GRG` = 4 | ✅ |
| two of three clear cell fusions retain four | abstract | `motif` → `measured_comparator_fusions…` e8 = 4, e10 = 4, e7 = 0 | ✅ |
| EWSR1::FLI1 none | abstract | `motif` → FLI1 e7 GRG = 0 | ✅ |
| *MTAP* adjusted *p* 1.00 | abstract | `multi` → `…adjusted_p.MTAP` = 1.0 both platforms | ✅ |
| "a screen already running" | abstract | ref [18] full text — a 2023 one-off 40-drug panel | ❌ (G4.3) |

### 3.2 · §1 Introduction

| value | where | artifact · key | agrees |
|---|---|---|---|
| no clinically validated agent targets NR4A3 | §1.1 | ref [1] verbatim: "No clinically validated agents directly target NR4A3." | ✅ |
| pazopanib ORR 18 % | §1.1 | ref [1] verbatim: "an ORR of 18%" | ✅ |
| median PFS 19 months | §1.1 | ref [1] verbatim: "median progression-free survival (PFS) of 19 months" | ✅ |
| trial identifier | §1.1 | ref [1] verbatim, same sentence | ✅ |
| **eight systemic classes in clinical use** | §1.1 | `cancer-modality-census.md` L131 — 8 classes, two of which are surgery and radiotherapy | ❌ (G8) |
| only one carries a meaningful response record | §1.1 | census L135 verbatim | ✅ |
| PRMT5 enhances EWSR1-ATF1-driven transcription | §1.2 | `cites` → [2] `cited_for[0]` | ✅ |
| PRMT5/PRMT1 inhibitors cause growth arrest and apoptosis | §1.2 | ref [3] abstract verbatim | ✅ |
| "largely supressed [sic] by partial depletion of EWSR1::FLI1" | §1.2 | ref [3] Results verbatim, `[sic]` correctly placed | ✅ |
| PRMT5/PRMT1/MEP50 higher across sarcoma types than breast and lung | §1.2 | ref [3] verbatim | ✅ |
| fusion depletion did not change PRMT transcript levels | §1.2 | ref [3] verbatim | ✅ |
| MTAP loss implies CDKN2A loss, not conversely | §1.2 | `cites` → [5] `cited_for` | ✅ |
| MEP50 required for PRMT5 activity, binds substrate independently | §1.2 | `cites` → [6] `cited_for[0]` | ✅ |
| 217 modality categories | §1.3 | `cancer-modality-census.md` L56 | ✅ |
| 591 open-access full texts | §1.3 | `cites` → `_provenance` | ✅ |
| four incidental mentions | §1.3 | `cites` → `_what_this_corpus_does_not_contain` | ✅ |
| 322 records | §1.3 | `emc-prior-art-2026-08-09.json` → `_retrieval.n_records` | ✅ |
| 238 with full text | §1.3 | same → `n_fulltext_files` | ✅ |
| one hit on the pairing | §1.3 | same → `counts.prmt5_or_mtap` = 1 | ✅ |
| the 2007 review names MTAP among validated targets | §1.3 | same → `⭐_the_two_that_change_a_manuscript.17545802` | ✅ |

### 3.3 · §2 Materials and methods

| value | where | artifact · key | agrees |
|---|---|---|---|
| GSE24369 / GPL6244 / 6 EMC | §2.1 table | `panels` → `platforms.GSE24369….n_EMC` | ✅ |
| 17 LGFMS, 6 desmoid, 6 myxofibrosarcoma | §2.1 table | `panels` → `class_counts` | ✅ |
| GSE4303 / GPL3290 / 10 EMC | §2.1 table | `panels` → `platforms.GSE4303….n_EMC` | ✅ |
| 3 DFSP, 3 GIST | §2.1 table | `panels` → `class_counts` | ✅ |
| EMC vs `CRH-mRNA`, DFSP vs `CRH`, GIST vs `UHR` | §2.1 | `multi` → `reference_channel.reference_channel_verbatim_per_class` | ✅ |
| deposited summary: ten EMC, 26 other sarcomas, 42,000-spot cDNA | §2.1 | `emc-cohort-search-inputs.json` → `GSE4303.summary` verbatim | ✅ |
| neither GEO record links a publication | §2.1 | same → `GSE4303.pubmed` = null, `GSE24369.pubmed` = null | ✅ |
| GSE24369 deposits 42 samples | §2.1 | `panels` → `n_samples` = 42 | ✅ |
| 35 analysed | §2.1 | `multi` → `deposited_samples_and_exclusions.n_analysed` | ✅ |
| two pooled skeletal-muscle excluded | §2.1 | `multi` → `n_excluded_pooled_normal_tissue` = 2 | ✅ |
| five solitary fibrous tumours excluded | §2.1 | `multi` → `n_excluded_solitary_fibrous_tumour` = 5 | ✅ |
| GSE4303 deposits 36 samples | §2.1 | `emc-cohort-search-inputs.json` → `GSE4303.n_samples` | ✅ |
| 16 on GPL3290 analysed | §2.1 | `panels` → `n_samples` = 16 | ✅ |
| accession resolution 0.981 / 0.582 | §2.1 | `panels` → `probe_mapping_rate.accession_resolution_rate` | ✅ |
| probe-level 0.711 / 0.633 | §2.1 | `panels` → `probe_level_rate` 0.7105 / 0.6325 | ✅ |
| group floor: ≥3 genes, coverage ≥0.5 | §2.1 | `panels` → locus verdict states both | ✅ |
| gene floor: ≥3 values per arm | §2.1 | `multi` → `per_gene_missingness._panel_floor` = 3 | ✅ |
| 578 of 1,662 (34.8 %) with a missing value | §2.1 | `multi` → `n_with_at_least_one_missing_value`, `frac…` 0.3478 | ✅ |
| 51 (3.1 %) with an arm below three | §2.1 | `multi` → 51, 0.0307 | ✅ |
| every GPL6244 cached gene complete | §2.1 | `multi` → GPL6244 `n_with_at_least_one_missing_value` = 0 | ✅ |
| DepMap public 24Q4, figshare article | §2.2 | `dep` → `data_source` | ✅ |
| 176 sarcoma models | §2.2 | `dep` → `n_sarcoma_models` | ✅ |
| 91 carry CRISPR data | §2.2 | `dep` → per-gene `n_sarcoma` = 91 | ✅ |
| dependency threshold −0.5 | §2.2 | `dep` → `dependent_threshold` | ✅ |
| selectivity = rest mean − sarcoma mean | §2.2 | `dep` → `_note` | ✅ |
| C(35,6) = 1,623,160 | §2.3 | `controls` → `n_labelings_enumerated`; arithmetic checks | ✅ |
| C(16,10) = 8,008 | §2.3 | `controls` → same, GPL3290 | ✅ |
| **18,688 scored on GPL6244** | §2.3 | `controls` → `genome_wide_placement.n_symbols_scored`; `panels` → `genome_wide_null.n_symbols_scored` | ✅ |
| 14,404 of 14,932 on GPL3290 | §2.3 | same two artifacts | ✅ |
| two paths agree for every gene both score | §2.3 | `controls` → `self_check.n_disagreeing` = 0 (404 and 362 genes) | ✅ |
| panel floor 3, genome-wide floor 2 | §2.3 | `multi` → `_the_genome_wide_path_uses_2` | ✅ |
| all 8,008 labellings enumerated on GPL3290 | §2.3 | `multi` → `labelings.kind` = exhaustive | ✅ |
| 20,000 drawn under a fixed seed on GPL6244 | §2.3 | `multi` → `labelings.n_labelings` = 20000, `seed` = 20260810 | ✅ |
| ~4,000 random symbols | §2.3 | `emc-hypoxia-null-background.json` → 3,978 / 3,971 drawn | ✅ |
| the two caches checked value-for-value before merging | §2.3 | `emc_prmt5_multiplicity._merge_caches` refuses on any disagreement; 497 / 526 shared | ✅ |
| family 5,449 / 4,848 | §2.3 | `multi` → `max_statistic_permutation.family_size_genes` | ✅ |
| **mapped-symbol universes 18,724 and 14,932** | §2.3 | `multi` → `n_symbols_on_the_platform`; contradicts the 18,688 above | ❌ (G3) |
| coverage floor 60 % of members per sample | §2.4 | SI §S10 and `controls` scoring rule | ✅ |
| survival = sign kept and ≥60 % of magnitude | §2.4 | `controls` → `reading` strings | ✅ |
| proliferation 12 genes, 35 and 16 samples | §2.4 | `controls` → `genes_used` (12), `n_samples_scored` 35 / 16 | ✅ |
| chondroid 8 genes, 35 and 14 samples | §2.4 | `controls` → `genes_used` (8), `n_samples_scored` 35 / 14 | ✅ |
| 5.23 / 6.24 = 0.84 | §2.4 | `controls` → 5.227 / 6.236 = 0.838 | ✅ |
| 2.71 / 6.67 = 0.41 | §2.4 | `controls` → 2.714 / 6.674 = 0.407 | ✅ |
| GRG counted with overlaps | §2.5 | `motif` → `_title` and S9 rule | ✅ |
| motif definition from [8] | §2.5 | `cites` → [8] `cited_for[0]`, verification `[MD]` | ✅ |
| retained sites ≤ last fully encoded 5′ residue | §2.5 | `motif` → `junction_in_residue_numbering.five_prime_residues_fully_encoded` | ✅ |
| type 1 = EWSR1 e12 :: NR4A3 e3 | §2.5 | `motif` → `fusion_constructs[0].label` | ✅ |
| type 2 = e7 :: e2 | §2.5 | `motif` → label | ✅ |
| type 5 = e13 :: e3 | §2.5 | `motif` → label | ✅ |
| TAF15 e6 :: NR4A3 e3 | §2.5 | `motif` → label | ✅ |
| two double-entry checks pass | §2.5 | `motif` → `rg_self_check` on 4 wild types + 4 comparator fusions | ✅ |
| **"every statistic… was checked against the committed artifact that owns it"** | §2.6 | falsified by G3, G7, G8; and by G1 in the companion SI | ❌ (G2) |

### 3.4 · §3 Results

| value | where | artifact · key | agrees |
|---|---|---|---|
| methylosome group *t* = 3.11 / 3.89 | §3.1 | `panels` → `panels.mtap_prmt5.groups.prmt5_methylosome…` 3.111 / 3.888 | ✅ |
| methionine-salvage *t* = 4.26 / 2.07 | §3.1 | same → `methionine_salvage_context` 4.257 / 2.074 | ✅ |
| MAT2A 99th percentile GPL6244 | §3.1 | `panels` → `gene_reads.MAT2A….EMC.mean_array_percentile` = 0.9873 | ✅ |
| PRMT5 91st percentile GPL6244 | §3.1 | same = 0.9098 | ✅ |
| MAT2A 84th / PRMT5 59th on GPL3290 | §3.1 | same = 0.8362 / 0.5858 | ✅ |
| locus *t* = −4.06, 3/3 readable | §3.1 | `panels` → `the_locus` GPL6244 = −4.064 | ✅ |
| **"falls below the panel's coverage floor"** | §3.1 | `panels` → locus GPL3290 `coverage` 0.667 clears the 0.5 floor; the 3-gene floor fails | ❌ (G7) |
| elevated methylosome across many malignancies [3] | §3.1 | ref [3] says "PRMTs… adult solid and haematological cancers" in its introduction; not in `cites` `cited_for` | ❌ (G10) |
| MTAP +0.053 SD, *t* = +0.69 | §3.2 | `panels` → `gene_reads.MTAP…` 0.053 / 0.685 | ✅ |
| MTAP −0.607 SD, opposite sign | §3.2 | same, GPL3290 = −0.6069 | ✅ |
| MTAP top 74 % / 26 % | §3.2 | `panels` → `genome_wide_null…frac…` 0.73978 / 0.26097 | ✅ |
| CDKN2A −0.481 SD, *t* = −5.40 | §3.2 | `panels` → −0.4805 / −5.398 | ✅ |
| CDKN2A +0.175 SD, reversed | §3.2 | same, GPL3290 = 0.1746 | ✅ |
| CDKN2A top 3.5 % / 49 % | §3.2 | `panels` → 0.03467 / 0.49257 | ✅ |
| CDKN2B −0.136 SD, top 34 % | §3.2 | `panels` → −0.1358, 0.33904 | ✅ |
| CDKN2B unreadable on GPL3290 | §3.2 | `panels` → `readable` = false | ✅ |
| PRMT5 top 1.9 % / 1.0 % | §3.2 | `panels` → 0.01846 / 0.00986 | ✅ |
| MTAP adjusted *p* 1.00 both | §3.2 | `multi` → 1.0 / 1.0 | ✅ |
| CDKN2A adjusted *p* 0.51 | §3.2 | `multi` → 0.5084 | ✅ |
| PRMT5 dependency 94.5 % | §3.3 | `dep` → `sarcoma_frac_dependent` 0.945 | ✅ |
| MAT2A dependency 96.7 % | §3.3 | `dep` → 0.967 | ✅ |
| MTAP not a dependency in any | §3.3 | `dep` → 0.0 | ✅ |
| PRMT5 94.1 % of non-sarcoma lines | §3.3 | `dep` → `rest_frac_dependent` 0.941 | ✅ |
| PRMT5 selectivity 0.013 | §3.3 | `dep` → `selectivity` 0.013 | ✅ |
| MAT2A reads −0.285 | §3.3 | `dep` → `selectivity` −0.285 | ✅ |
| 91 screened sarcoma lines | §3.3 | `dep` → `n_sarcoma` 91 | ✅ |
| panel contains no EMC line | §3.3 | `dep` — no EMC model; SI §S1 | ✅ |
| EMC third of five tumour classes, pooled | §3.4 | `multi` → pooled medians desmoid 0.9496 > SFT 0.9354 > EMC 0.9283 | ✅ |
| PRMT5 medians +1.30 / +1.05 / +1.05 / +1.04 / +0.94 | §3.4 | `multi` → 1.3044 / 1.0525 / 1.0508 / 1.0427 / 0.937 | ✅ |
| pooled muscle +1.34 on PRMT5 | §3.4 | `multi` → 1.3434 | ✅ |
| solitary fibrous tumour second at +1.05 | §3.4 | `multi` → 1.0525 | ✅ |
| PRMT5 *t* = 6.24 / 6.67 | §3.5 | `panels` → 6.236 / 6.674 | ✅ |
| Δ = +0.263 / +0.816 SD | §3.5 | `panels` → 0.2632 / 0.8164 | ✅ |
| 1,623,160 labelings, 230 extreme, *p* 0.000142 | §3.5 table | `controls` → all three | ✅ |
| 8,008 labelings, 1 extreme, *p* 0.000125 | §3.5 table | `controls` → all three | ✅ |
| PRMT5 adjusted *p* 0.21 / 0.24 | §3.5 table | `multi` → 0.2081 / 0.2376 | ✅ |
| MAT2A +4.13 / +4.10, top 8.5 % / 6.3 %, adj 0.98 / 0.97 | §3.5 table | `panels` + `multi` → 4.132, 4.096, 0.08439, 0.06255, 0.9782, 0.9653 | ✅ |
| WDR77 +2.82, top 20.5 %, adj 1.00, unreadable on GPL3290 | §3.5 table | `panels` + `multi` → 2.82, 0.20473, 1.0, `readable` false | ✅ |
| MTAP −2.27, top 26.1 %, adj 1.00 | §3.5 table | `panels` + `multi` → −2.271, 0.26097, 1.0 | ✅ |
| CDKN2A +1.33, top 49.3 %, adj 1.00 | §3.5 table | `panels` + `multi` → 1.325, 0.49257, 1.0 | ✅ |
| NR4A3 +4.66, top 5.9 %, adj 0.85 | §3.5 table | `panels` + `multi` → 4.662, 0.05886, 0.8498 | ✅ |
| NR4A3 +1.70, top 38.5 %, *n* = 9 vs 2 | §3.5 table | `panels` → 1.702, 0.38545; `multi` → NR4A3 `_status` not scored | ✅ |
| ENO3 +3.61, top 12.0 %, adj 1.00 | §3.5 table | `panels` + `multi` → 3.607, 0.11933, 0.9998 | ✅ |
| ENO3 +13.22, top 0.05 %, adj 0.010 | §3.5 table | `panels` + `multi` → 13.222, 0.00049, 0.0097 | ✅ |
| Monte-Carlo SE ≈ 0.003 | §3.5 | `multi` → PRMT5 `monte_carlo_se` 0.0029 | ✅ |
| family is a third of that array | §3.5 | `multi` → 4,848 / 14,932 = 0.325 | ✅ |
| largest \|*t*\| exceeds 5.4 in half of labellings | §3.5 | `multi` → `max_abs_t_null.p50` = 5.418 | ✅ |
| reaches 6.24 in at least a fifth | §3.5 | `multi` → 0.2081 | ✅ |
| 8 readable PRMT members on GPL6244, 7 on GPL3290 | §3.6 | `controls` → `n_family_members_readable` 8 / 7 | ✅ |
| PRMT5 ranks first on both | §3.6 | `controls` → `PRMT5_rank` = 1, `ranked_by_t_desc` | ✅ |
| family group flat, *t* = 0.33 / 1.34 | §3.6 | `panels` → 0.33 / 1.338 | ✅ |
| CARM1 +5.44, PRMT3 +3.47 on GPL3290 | §3.6 | `panels` → 5.44 / 3.472 | ✅ |
| next member PRMT3 at +1.62 on GPL6244 | §3.6 | `panels` → 1.615 | ✅ |
| proliferation GPL6244 score *t* = 0.45, PRMT5 6.24→5.23 | §3.6 table | `controls` → 0.452, 6.236 → 5.227 | ✅ |
| proliferation GPL3290 score *t* = 3.00, PRMT5 6.67→2.71 | §3.6 table | `controls` → 3.0, 6.674 → 2.714 | ✅ |
| chondroid GPL6244 *t* = 0.99, 6.24→6.20 | §3.6 table | `controls` → 0.991, 6.202 | ✅ |
| chondroid GPL3290 *t* = 0.36, 6.67→6.52, *n* = 14 | §3.6 table | `controls` → 0.355, 6.517, 14 | ✅ |
| proliferation correlates with PRMT5 at *r* = 0.60 | §3.6 | `controls` → 0.6 | ✅ |
| chondroid *r* = 0.05 and −0.04 | §3.6 | `controls` → 0.053 / −0.036 | ✅ |
| split: PRMT5 *t* = 5.97 vs 3 label-matched | §3.6 | `multi` → `split_contrasts.CRH.PRMT5.t` = 5.968 | ✅ |
| split: MKI67 *t* = 1.09 vs the same three | §3.6 | `multi` → 1.09 | ✅ |
| pooled 6.67 and 2.30 | §3.6 | `multi` → `pooled_for_comparison` 6.674 / 2.301 | ✅ |
| MKI67 *t* = 0.53 on GPL6244 | §3.6 | `panels` → 0.528 | ✅ |
| MKI67 *t* = 2.30 at +1.24 SD on GPL3290 | §3.6 | `panels` → 2.301, 1.2358 | ✅ |
| MKI67 adjusted *p* 1.00 both | §3.6 | `multi` → 1.0 / 1.0 | ✅ |
| EWSR1 656 residues, 11 GRG, first at 301 | §3.7 | `motif` → `wild_type_proteins.EWSR1` | ✅ |
| residue 301 of 656 = 46 % | §3.7 | arithmetic; `motif` → `⚠_do_not_write_this_as_c_terminal_half` | ✅ |
| two RGG-rich regions | §3.7 | `motif` → `rgg_boxes_from_the_census` (300–332, 455–638) | ✅ |
| type 1: 431 residues, 4 sites, 0.364 | §3.7 table | `motif` → construct record | ✅ |
| type 5: 472, 5, 0.455 | §3.7 table | `motif` → construct record | ✅ |
| type 2: 264, 0, 0.000 | §3.7 table | `motif` → construct record | ✅ |
| TAF15::NR4A3: 161, 0, 0.000 of TAF15's 9 | §3.7 table | `motif` → construct + `TAF15.motif_counts.GRG` = 9 | ✅ |
| EWSR1::ATF1 e8: 324, 4, 0.364 | §3.7 table | `motif` → comparator record | ✅ |
| EWSR1::ATF1 e10: 348, 4, 0.364 | §3.7 table | `motif` → comparator record | ✅ |
| EWSR1::ATF1 e7: 264, 0, 0.000 | §3.7 table | `motif` → comparator record | ✅ |
| EWSR1::FLI1 type 1: 264, 0, 0.000 | §3.7 table | `motif` → comparator record | ✅ |
| the retained N-terminal segment carries no site | §3.7 | `motif` → `⭐_the_headline._reading` | ✅ |
| PRMT5's GRG preference is a preference not a rule | §3.7 | `cites` → [8] `cited_for[1]` | ✅ |
| only the DDX5 C-terminal RGG/RG fragment methylated; five arginines abolish it | §3.7 | `cites` → [9] `cited_for[0]` verbatim | ✅ |
| EWSR1 extensively arginine-methylated | §3.7 | `cites` → [10] `cited_for[0]`, verification `[MD]` | ✅ |

### 3.5 · §4–§5 Discussion, limitations, conclusion

| value | where | artifact · key | agrees |
|---|---|---|---|
| [1] considers neither rationale | §4.1 | ref [1] full text contains zero occurrences of PRMT5, MTAP or MAT2A | ✅ |
| **"the other three members are flat or lower in EMC"** | §4.1 | `panels` → WDR77 +0.098 SD / *t* +2.82; CLNS1A +0.088 / +2.53 | ❌ (G5) |
| both series put PRMT5 first of the readable family | §4.1 | `controls` → `PRMT5_rank` 1 / 1 | ✅ |
| required in 94.1 % non-sarcoma vs 94.5 % sarcoma | §4.1 | `dep` → 0.941 / 0.945 | ✅ |
| carfilzomib, doxorubicin, venetoclax validated in both | §4.2 | ref [18]: "no response to venetoclax as a monotherapy in the validation" | ❌ (G4.1) |
| two synergistic pairs validated in both | §4.2 | ref [18]: synergy in USZ20-EMC1, additive in USZ22-EMC2 | ❌ (G4.2) |
| PRMT5 inhibition sensitised Ewing cells to olaparib | §4.2 | ref [3] verbatim | ✅ |
| combination only partially rescued by fusion depletion | §4.2 | ref [3] verbatim | ✅ |
| type 1 four sites, type 2 none | §4.2 | `motif` → 4 / 0 | ✅ |
| MTAP IHC surrogate: 90–100 % homozygous deletion | §4.2 | `cites` → [11] `cited_for[0]` | ✅ |
| 13,067 tumours, 149 tumour types | §4.2 | `cites` → [11] title verbatim | ✅ |
| MTAP loss up to 20 % in various sarcomas | §4.2 | `cites` → [11] `cited_for[2]` | ✅ |
| the survey does not name this histology | §4.2 | `cites` → [11] `cited_for[3]` | ✅ |
| F7: 6.24→5.23 (*n* = 35), 6.67→2.71 (*n* = 16) | §4.3 | `controls` → matches | ✅ |
| F5 marked fired | §4.3 | consistent with §3.2, §4.1, §5 and `multi` MTAP = 1.00 | ✅ |
| F9 "partially answered", third junction retains none | §4.3 | `motif` → ATF1 e7 GRG = 0 | ✅ |
| F10 "contradicted at one point already" | §4.3 | `motif` → FLI1 GRG = 0 with [3]'s fusion-dependence | ✅ |
| **F3 / F4 stated on group scores** | §4.3 | contradicts §3.4's "not a unit of evidence" and F5's closure | ❌ (G9) |
| only ENO3 on GPL3290 below 0.05, at 0.010 | §4.4 | `multi` → minimum adjusted *p* across both platforms | ✅ |
| CDKN2A 0.51, NR4A3 0.85, ENO3 GPL6244 1.00 | §4.4 | `multi` → 0.5084, 0.8498, 0.9998 | ✅ |
| adjusted values computed on about a third of each array | §4.4 | `multi` → 5,449/18,724 = 0.29; 4,848/14,932 = 0.32 | ✅ (denominator per G3) |
| exclusion sensitivity: PRMT5 6.24→6.31 | §4.4 | `multi` → `inclusion_sensitivity.PRMT5` 6.236 → 6.309 | ✅ |
| MTAP 0.69→0.70 | §4.4 | `multi` → 0.685 → 0.700 | ✅ |
| CDKN2A −5.40→−5.66 | §4.4 | `multi` → −5.398 → −5.658 | ✅ |
| five samples excluded of forty-two deposited | §4.4 | `multi` → 5, 42 | ✅ |
| [2] preprint has since been published | §4.4 | `prmt5-ccs-preprint-publication-status-2026-08-10.json` → `_answer` | ✅ |
| that record is search-index level only | §4.4 | same → `⛔_verification_level` `[SE]` | ✅ |

### 3.6 · Supplementary information

| value | where | artifact · key | agrees |
|---|---|---|---|
| all seven per-group *t* and Δ, both platforms | §S3 | `panels` → `panels.mtap_prmt5.groups.*` — 14 values, all match | ✅ |
| locus gene-by-gene table | §S3 | `panels` → matches §3.2 | ✅ |
| PRMT5 −1.015, 94.5 %, 94.1 %, +0.013 | §S4 | `dep` | ✅ |
| MAT2A −1.471, 96.7 %, 98.9 %, −0.285 | §S4 | `dep` | ✅ |
| MTAP −0.075, 0.0 %, 0.1 %, +0.007 | §S4 | `dep` | ✅ |
| PSMB1, PSMC1, PSMD1, VCP at 100 %; PSMB5 at 97.8 % | §S4 | `dep` → 1.0 ×4, 0.978 | ✅ |
| selectivity −0.10 to +0.17 | §S4 | `dep` → −0.103 to +0.169 | ✅ |
| **"EMC ranks second of four comparator classes"** | §S4 | `multi` → EMC is third of five | ❌ (G1) |
| six-gene control block with pre-specified expectations | §S5 | `panels` → `panels.instrument_controls` | ✅ |
| NR4A3 +4.66; no GPL3290 panel contrast, *n* = 9 vs 2 | §S5 | `panels`, `multi` | ✅ |
| ENO3 +3.61 / +13.22 | §S5 | `panels` | ✅ |
| MKI67 +0.53 / +2.30 at +1.24 SD | §S5 | `panels` | ✅ |
| retained fractions 0.84 and 0.41 | §S5 | `controls` | ✅ |
| reference split: 7 genes × 3 columns = 21 values | §S5a | `multi` → `split_contrasts` + `pooled_for_comparison`, all 21 match | ✅ |
| exclusion sensitivity: 6 genes × 2 columns | §S5b | `multi` → `inclusion_sensitivity`, all 12 match | ✅ |
| per-class medians, PRMT5 and pooled, 12 values | §S5b | `multi` → `per_class_medians_*`, all match | ✅ |
| adjusted-*p* table, 9 genes × 2 platforms | §S5c | `multi` → all match | ✅ |
| family 5,449 / 4,848 against 18,724 / 14,932 | §S5c | `multi` → matches; see G3 | ✅ / ❌ |
| GPL6244 curve 0.016, 0.055, 0.168 at 250, 1,000, 3,973 | §S5c | `multi` → 0.0156, 0.0551, 0.1681 | ✅ |
| GPL3290 curve 0.037, 0.062, 0.208 | §S5c | `multi` → 0.0368, 0.0622, 0.2079 | ✅ |
| **"over the same three family sizes"** | §S5c | `multi` → GPL3290's third size is 3,640, not 3,973 | ❌ (G15.1) |
| MC SE ≈ 0.003 on an adjusted *p* near 0.2 | §S5c | `multi` → 0.0029 | ✅ |
| figure sources table, five rows | §S6 | provenance `sources` names the same five artifacts | ✅ |
| "--check … so a stale figure is detectable" | §S6 | `check()` hashes artifacts only, never an image | ❌ (G12) |
| the EMC-labelled line lacks an EWSR1 fusion | §S1 | `depmap-target-expression.json` → `_identity_correction` verbatim | ✅ |
| **"and it carries no CRISPR data"** | §S1 | no committed artifact found | ⚠ (G14) |
| the `fibrosarcoma` bucket is myxofibrosarcoma | §S1 | `multi` → `⚠_one_bucket_name_is_a_substring_artefact` | ✅ |
| 404 / 362 genes agree between the two paths | §S10 | `controls` → `self_check.n_agreeing_within_0.02` | ✅ |
| requiring every member gene drops GPL3290 to 9 | §S10 | `emc_prmt5_route_controls.py` L127 comment — a committed source, not an artifact | ✅ |
| the correction refuses to run on a non-published statistic | §S10 | `emc_prmt5_multiplicity.compute()` raises on any disagreement | ✅ |
| panel members added and fetched 2026-08-09 | §S10 | `panels` → `generated_utc` 2026-08-09 | ✅ |
| **"§S11 status line"** | Appendix S1 | no §S11 exists | ❌ (G15.2) |
| four bridge re-runs at 0.984 / 0.931 / 0.931 / 0.981 | Appendix S1 | narrated in the register; consistent with `panels` 0.981 | ✅ |

### 3.7 · Figures and provenance

| check | result |
|---|---|
| Fig 1 medians vs artifact (PRMT5 EMC 1.304 / comparator 1.039, and 6 further genes) | ✅ all match `gene_reads.*.per_sample` |
| Fig 1 caption "every tumour" vs 35 of 40 deposited tumours drawn | ❌ (G6) |
| Fig 1 unreadable marks (WDR77, CDKN2B on GPL3290) | ✅ match `readable: false` |
| Fig 2 medians vs artifact (MTAP, CDKN2A, CDKN2B, both platforms) | ✅ all match |
| Fig 2 legend / "bars are medians" statement | ❌ absent from both image and caption (G16.1) |
| Fig 2 MTAP median direction vs §3.2's Δ | ✅ both correct; reads as a contradiction (G16.2) |
| Fig 3 bar values 0.0 %, 96.7 %, 94.5 % and mean effects −0.07, −1.47, −1.01 | ✅ match `dep` |
| Fig 3 axis label "% of 91 screened sarcoma cell lines" | ✅ matches the corrected denominator |
| Fig 4 class order and medians, both panels | ✅ match `multi` per-class medians exactly |
| Fig 4 point counts (n = 8, 24, 20, 24, 68, 24 pooled; 2, 6, 5, 6, 17, 6 single) | ✅ = class size × gene count |
| Fig 4 in-figure caption omits solitary fibrous tumour | ❌ (G16.4) |
| Fig 4 normal-muscle class distinguished by hue alone | ❌ (G16.3) |
| Fig 5 ruler, 11 ticks, first at 301, two shaded RGG boxes | ✅ match `motif` |
| Fig 5 per-fusion cut positions and "kept" counts (431/4, 264/0, 472/5, 264/0, 324/4, 264/0, 348/4) | ✅ match `motif` |
| Fig 5 caption "TAF15::NR4A3 tabulated but not plotted" | ✅ true of the image |
| Greyscale safety, figs 1, 2, 3, 5 | ✅ shape and fill carry the series |
| Legibility at single-column print size, all five | ✅ |
| Provenance `sources` hashes vs current artifacts (`--check`) | ✅ OK |
| Provenance vs the committed images | ⚠ never compared by the tool (G12) |
| Independent regeneration into an isolated tree | ✅ **all five PNGs byte-identical; provenance JSON identical** |

---

## Fix list

Only the FIXABLE items. In order.

1. **`emc-mtap-prmt5-hypothesis-SI.md` §S4, line 125** — replace "pooled across four genes EMC ranks
   second of four comparator classes" with the current claim: EMC is third of the five tumour
   classes, below desmoid fibromatosis and solitary fibrous tumour. Match §3.4's wording exactly.
2. **`pinned-figures.json`** — add `research/manuscripts/emc-mtap-prmt5-hypothesis-SI.md` to
   `targets`, and add this revision's superseded values to `superseded`: "second of four comparator
   classes", "18,474"/"14,402", "176 sarcoma cell lines", "+0.266"/"+0.744", and the locus values
   −0.023 / −0.389 / −0.399 / −0.096. This is CLAUDE.md rule 1.3 and it is what would have caught
   item 1.
3. **`emc-mtap-prmt5-hypothesis.md` §2.6, paragraph 2, sentence 1** — replace the universal claim
   with what was actually done: name the classes of value that were re-checked against their
   artifacts in this revision, state that the check is per-value and cannot detect a quantity reported
   at two values in two places, and point at Appendix A for what it missed. Then correct Appendix A
   row 1's account of the rewrite so it describes the sentence that now exists.
4. **`emc-mtap-prmt5-hypothesis.md` §2.3, second paragraph, and SI §S5c** — reconcile 18,724 with
   18,688 or disclose the difference. Offline, the honest form is one clause: the random half of the
   correction's family was drawn from a platform-table resolution of 2026-08-07 that maps 18,724
   symbols, while the genome-wide placement scored the 2026-08-09 resolution's 18,688; the 0.2 %
   difference does not move any adjusted *p*. Add the same note to Appendix A.
5. **`emc-mtap-prmt5-hypothesis.md` §4.2, paragraph 1, and the abstract's last sentence** — restate
   reference [18] as it reads: carfilzomib high sensitivity and doxorubicin good-to-moderate in both
   models, venetoclax **no** monotherapy response in the validation; two combinations tested, synergy
   in one model and an additive effect in the other. Delete "a screen that already runs" and "a screen
   already running" — say that two published patient-derived models exist and have been used for drug
   testing by the group that established them.
6. **`emc-mtap-prmt5-hypothesis.md` §4.1, paragraph 3** — replace "the other three members are flat or
   lower in EMC" with the artifact: RIOK1 is lower and WDR77 and CLNS1A are higher but much smaller,
   so the group mean is diluted.
7. **`emc-mtap-prmt5-hypothesis.md` Figure 1 caption, and
   `research/modalities/emc_mtap_prmt5_figures.py` `fig_readings` suptitle** — replace "Every tumour"
   with "Every tumour in the analysed arms", and add the pointer to §2.1 and Figure 4 for the five
   deposited tumours the classifier dropped. Regenerate the figure and its provenance stamp in the
   same commit.
8. **`emc-mtap-prmt5-hypothesis.md` §3.1, final paragraph** — replace "falls below the panel's
   coverage floor" with "falls below the panel's three-gene minimum, although its coverage of 0.667
   clears the 0.5 floor".
9. **`emc-mtap-prmt5-hypothesis.md` §1.1, sentence 3** — either drop "systemic" ("eight classes in
   clinical use, two of them local") or give the systemic count of six. Update Appendix A row 9, whose
   "why it changed" cell claims the number was merely re-attributed.
10. **`emc-mtap-prmt5-hypothesis.md` §4.3, rows F3 and F4** — restate both on the gene rather than the
    group, so they falsify the claim the paper now makes: F3 on *PRMT5* reading higher than the
    comparator arm and ranking first of the readable family, F4 on *MTAP* specifically. Note in F4
    that it is superseded by F5 and F6, or merge it into them.
11. **`emc-mtap-prmt5-hypothesis.md` §3.1, last paragraph, and SI §S7 item 4** — cite [3] for what it
    measured (PRMT5, PRMT1 and MEP50 higher across multiple sarcoma types than in breast and lung
    cancer) rather than for "elevated methylosome expression across many malignancies", or add the
    proposition to `mtap-prmt5-emc-citations.json` with the source's own wording.
12. **`research/modalities/emc_mtap_prmt5_figures.py`** — hash the ten written image files into the
    provenance stamp beside `sources`, compare them in `check()`, and change the success line so it
    reports what was actually compared. Then SI §S6's "so a stale figure is detectable" becomes true.
13. **`emc-mtap-prmt5-hypothesis.md` §6** — add four lines: patient consent (not applicable, no human
    participants), permission to reproduce (not applicable, no third-party material), clinical-trial
    registration (not applicable; the trial cited in §1.1 is a published third-party study), and a
    pointer to §8 for data availability. Recast author contributions in CRediT terms. Add a
    preprint-deposition sentence matching the cover letter.
14. **`emc-mtap-prmt5-hypothesis-SI.md` §S1, paragraph 3** — either commit an artifact recording that
    the disputed EMC-labelled line carries no CRISPR gene-effect data, or delete the clause. The
    paragraph's conclusion does not need it.
15. **`emc-mtap-prmt5-hypothesis-SI.md` §S5c** — replace "over the same three family sizes" with the
    GPL3290 sizes: 250, 1,000 and 3,640.
16. **`emc-mtap-prmt5-hypothesis-SI.md` Appendix S1** — change the "§S11 status line" row to "§S10,
    closing status paragraph", which is where that text now lives.
17. **`emc-mtap-prmt5-hypothesis.md` Figure 2 caption** — state the mark convention (filled circle =
    EMC tumour, open square = comparator) and that the bars are medians while the §3.2 table reports a
    difference of means, so the MTAP panel and the MTAP row do not read as a contradiction.
18. **`research/modalities/emc_mtap_prmt5_figures.py` `fig_classes`** — give the pooled-normal-muscle
    class a mark that differs in shape or fill, not only in hue, and extend the in-figure caption to
    name solitary fibrous tumour alongside desmoid fibromatosis. Regenerate both figure files and the
    provenance stamp.
19. **`emc-mtap-prmt5-hypothesis.md` abstract** — drop "at least" before "0.21 and 0.24" and let §3.5
    carry the lower-bound explanation; and disambiguate the two sixteens by naming the platforms by
    accession after their first introduction.
20. **Number every table** in the manuscript and the SI, and call them out by number in the text.
21. **`emc-mtap-prmt5-prepost.md`** — the pre-posting checklist still carries "EMC ranks second of
    four" at line 146. It is not a submission file, but it is the checklist a future session will read
    as current.
