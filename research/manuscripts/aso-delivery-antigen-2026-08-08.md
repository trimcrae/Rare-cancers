---
id: DOC-ASO-DELIVERY-ANTIGEN
title: "Can the junction ASO's delivery arm be named yet? — both axes, recomputed against EMC tumour tissue"
level: L3
kind: memo
status: live
canonical_for:
  - whether a delivery antigen can be named for the fusion-junction ASO's AOC arm
  - the interpretation of `aso-delivery-antigen.json`
purpose: >
  readiness.md records RT-ASO's one missing item as "a named delivery candidate", and the ASO
  paper's §3c offers an antibody-oligonucleotide-conjugate arm whose antigen shortlist came from a
  translocation-sarcoma DepMap surrogate with no EMC and no normal tissue in it. Three EMC tumour
  cohorts now exist and one of them carries 27 normal-organ libraries. This memo states what
  happened when the question was re-asked on that basis, and what §3c may and may not now say.
scope: >
  Transcript only, three public cohorts, one HPA prior. Nothing here asserts protein expression,
  surface localisation, antigen density, internalisation, selectivity, efficacy, safety, a
  therapeutic window or clinical readiness, and no such quantity is computed anywhere in it or in
  the artifact it reads.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-08
last_verified: 2026-08-08
---

# Can the junction ASO's delivery arm be named yet?

**Every number lives in [`aso-delivery-antigen.json`](../modalities/aso-delivery-antigen.json),
produced by [`aso_delivery_antigen.py`](../modalities/aso_delivery_antigen.py) at $0 from committed
artifacts.** This memo re-types nothing that the artifact owns.

---

## 0 · The answer, in one paragraph

**No.** Of the **12** antigens that can be asked the two-axis question at all, **none** clears both
axes on every instrument that can read it, and **zero** are passed by *both* normal-tissue
instruments. Three — **CD44, CSPG4, RET** — clear both *measured* axes and are refused only by the
wider normal-tissue prior or by its absence. So `readiness.md`'s missing item, *"a named delivery
candidate"*, is **not discharged**.

⭐ **What has changed is the BASIS of the refusal, and that is the result.** Until today the ASO's
delivery gate was bounded by a **surrogate**: `fusion-junction-aso-working-record.md` §3c's targeting-arm
shortlist was ranked across a translocation-sarcoma DepMap class that contains no verified
*EWSR1::NR4A3* line and no normal tissue at all, and §3c says so honestly — *"the toxicity-relevant
tumour-vs-normal window (GTEx/HPA) is the flagged next filter"*. That filter has now been applied,
on **two** independent normal-tissue instruments, over **three EMC tumour cohorts**. The gate is now
bounded by a measurement in the disease's own tissue.

---

## 1 · What the exposure axis can and cannot resolve — read this before any row

The new axis is much narrower than "EMC versus normal", and every verdict below is capped by it.
One home: `aso-delivery-antigen.json` → `instrument_reach`.

**It can** say whether an EMC transcript's median sits above the median of 27 normal-organ
libraries from **six** organs (bowel, breast, colon, kidney, lung, uterus) on one 3′-end sequencing
deposit, for the **19** genes whose per-gene values are committed — and it can *grade* that ratio,
because the deposit's own `ratio_calibration` block places it in the distribution of the same ratio
across every gene it contains. That calibration is the reason "up" here means a defensible thing:
the deposit's **median** gene already moves ≈1.05× between arms, so a bare fold-change is not a
reading.

**It cannot** speak to any tissue outside those six — and the list of what is missing is the point:
no nerve, no thyroid, no adrenal, no brain, no heart, no skin, no marrow, no circulating cells,
no liver, no pancreas, and ⛔ **no normal soft tissue of any kind, in a soft-tissue tumour**. It
cannot speak to any gene without a committed row (an absent reading, never a reading of absence).
It cannot speak to protein, surface localisation, antigen density, epitope accessibility or
internalisation — every one of which an AOC needs. It cannot assign a **compartment**: bulk archival
tissue cannot say whether a transcript sits in the tumour cell, the stroma, the vasculature or an
entrapped nerve, and EMC is hypocellular and matrix-dominated. And with n = 4 EMC libraries and
medians rather than distributions, it carries no test and no confidence interval.

⇒ **The ceiling is therefore arithmetical and it is small.** Only genes that are a plausible
cell-surface antibody address *and* carry both a lineage reading and a measured exposure reading can
be scored: **12**. Every other surface antigen this repository has discussed — including **86** of
the 100 genes on the committed surface board — is **unscoreable on exposure**, which is an absent
reading and never a negative.

---

## 2 · The scoring, and why the thresholds are not this memo's inventions

Two axes, five instruments, and no value from one platform family is ever pooled with another.

| axis | instrument | rule |
|---|---|---|
| **lineage** (vs comparator sarcomas) | GSE24369 / GPL6244, 6 EMC vs 29 | Welch *t* ≥ 2 UP, ≤ −2 DOWN |
| | GSE4303 / GPL3290, 10 EMC vs 6 | same |
| | GSE28866 / 3SEQ, 4 EMC vs 32 sarcoma libraries | ratio at ≥ the 90th percentile of the deposit's own distribution |
| **exposure** (vs normal) | GSE28866 / 3SEQ, 4 EMC vs 27 normal-organ libraries | same percentile rule — a **contrast**, six organs |
| | Human Protein Atlas RNA | window must be `RESTRICTED` — a **distribution**, many tissues, no EMC |

**ELEVATED** requires ≥ 2 instruments UP and **0** DOWN. **NAMING** requires clearing both axes on
every instrument that can read the antigen *and* no decision-relevant instrument absent.

⚠ **Stated plainly: none of this was pre-registered.** The analysis was written after its inputs
were visible. Two things limit the freedom that gives, and both are checkable: the array rule
(|*t*| ≥ 2) is `emc_expression_panels._cross_platform_verdict`'s **own** rule and is reused rather
than chosen here, and the 3SEQ rule is the 90th percentile of a distribution that already existed in
the deposit artifact over 13,708 genes. Neither was tuned to the answer.

⛔ **The two normal-tissue instruments answer different questions and neither substitutes for the
other.** HPA asks *"is this antigen confined in normal tissue?"* over many tissues but sees no EMC
and no tumour. The 3SEQ arm asks *"is EMC above the normal-organ level?"* with real EMC but only six
organs. A usable address needs both true. A low measured ratio is **not** evidence against an HPA
verdict — it can simply mean EMC does not express the antigen, which is exactly what the negative
control GPC3 does.

---

## 3 · The result, gene by gene

| verdict | antigens |
|---|---|
| clears both axes on every instrument that can read it | ⛔ **none** |
| clears both **measured** axes, wider prior **absent** | **RET** |
| clears both **measured** axes, wider prior **refuses** | **CD44**, **CSPG4** |
| fails the exposure axis | **ALCAM**, **L1CAM** |
| fails the lineage axis — an instrument reads it **down** | CD248, CD276, CDH17, GPC3, MSLN |
| fails the lineage axis — **flat** on every instrument that read it | SSTR2 |
| lineage axis on one instrument only | FAP |

⚠ The last two rows are different failures and the artifact keeps them different: a **down** reading
is a contrary measurement, a **flat** one is an absence of separation, and a single-instrument
elevation is neither. Only the first is evidence against an antigen.

**Read the rows, not the count.**

- **ALCAM fails on the axis it was promoted on.** It is the one antigen the surface-target
  manuscript reports as concordantly elevated on both EMC arrays, and the HPA prior passes it as
  `RESTRICTED`. The measured contrast puts its EMC median **below** the normal-organ median, at the
  **33rd** percentile of all deposit ratios. ⭐ **So the single antigen a prior-only pipeline would
  have promoted is the one the measured exposure axis refuses** — the failure mode the exposure axis
  was wanted for, demonstrating itself on the first antigen it was pointed at. This does not touch
  ALCAM-as-a-marker, and it does not grade HPA; it establishes that a normal-tissue **prior** cannot
  stand in for a tumour-versus-normal **contrast**, and stage 1 had only the prior. The antigen's
  full precedent record, including the normal-tissue liabilities a bulk atlas cannot see, is
  [`alcam-precedent.json`](../modalities/alcam-precedent.json) and is unchanged by this.
- **CD276/B7-H3 — the antigen §3c names — is refused in EMC tissue itself.** Not on the surrogate's
  selectivity test, which is where the existing objection lives, but on the lineage axis of the
  disease's own tumour tissue: an instrument reads it **down**. ⚠ It is unreadable on GPL3290, which
  is an instrument statement and not a second negative.
- **RET is the ranked residual, and it is not a name.** It is UP on **all three** lineage
  instruments, and its EMC/normal-organ ratio sits at the **99.1st** percentile of every gene in the
  deposit — the largest exposure margin of any surface antigen here, on 4 peaks rather than 1.
  It cannot be named for three separate reasons, each recorded rather than argued away:
  **(a)** this repository holds **no** HPA row for RET at all, so its wider normal-tissue
  distribution is an **absent reading** — nothing committed here bounds it in either direction, and
  the only normal tissue it has been measured against is six visceral organs;
  **(b)** [`emc-ret-lane.md`](../modalities/emc-ret-lane.md) records the lane's own falsifier — bulk
  tissue cannot separate tumour-cell RET from stromal or **entrapped-nerve** RET in a hypocellular,
  matrix-rich tumour — and for a *delivery* antigen that confound is not a caveat but the whole
  question, because an AOC would be delivered wherever the antigen is;
  **(c)** transcript is not protein, density or internalisation.
  ⭑ **One asymmetry is worth recording, because it is easy to get backwards.** The RET lane's
  headline blocker is the **activation** bar — in that memo's own words, *expression common,
  activation of unknown frequency*, with no blinded phospho-RET tissue measurement carrying a stated
  denominator ever performed in EMC. **That bar does not gate this use.** An
  antibody-oligonucleotide conjugate needs a receptor that is present and internalises; it does not
  need a signalling-competent one, and it is not a kinase inhibitor. So the delivery-antigen
  question about RET is a *different* question from the one the lane is blocked on — and it is
  blocked on a different, smaller set of missing measurements. ⛔ This is not a claim that RET is a
  delivery antigen. It is a claim that the reason it is not yet one has been misattributed.
- **CD44 and CSPG4 clear the measured axes and the prior refuses them.** CD44 is `BROAD_LIABILITY`
  on HPA ("detected in all"); CSPG4 is `ENHANCED_BROAD`, rests on a **single peak** in the 3SEQ
  deposit, and is array-discordant — strongly up on GPL6244 and flat on GPL3290. Both stay open, and
  neither is promoted.
- **SSTR2 misses the exposure line rather than failing it** — 89.2nd percentile against a 90th
  percentile rule — and it is **flat**, not down, on the lineage axis, and unreadable on GPL3290.
  That is a borderline on one axis and an absence of separation on the other, and it is reported as
  both rather than collapsed into a rejection.

---

## 4 · Two instrument findings that fell out on the way

### 4a · ⛔ The vital-tissue override in the normal-tissue prior has never fired

`emc_surface_normal_window.classify` computes its vital-tissue liability by matching a list of
vital tissues against the HPA field `rna_tissue_specific_nTPM`. In the committed artifact **that
field is null for all 45 scored antigens**, so the match runs against an empty string every time and
that arm of the classifier **cannot ever have fired**. Every `vital_tissue: []` in that file is an
**absent reading wearing the costume of a clean pass**. The nine antigens that do reach
`VITAL_OR_IMMUNE_LIABILITY` all reach it through the independent blood-cell branch, which reads a
different field.

⚠ **What this does not establish:** whether HPA returns nothing for that column, or whether the
column key in the query is wrong. That is not decidable from the artifact and is not guessed here.
Either way, **no verdict in that file was ever informed by per-tissue nTPM** — so every
`RESTRICTED` means *"not low-specificity, not detected-in-all, not blood-confined"* and **not**
*"checked against vital tissue and found clear"*. This is why the prior is used here as a necessary
condition that is weaker than it reads, and why no antigen is named on it. The fix belongs to that
module's owner and is routed, not applied.

### 4b · ⭐ The antigens that clear the measured axes are the ones the surrogate never evaluated

[`surfaceome-instrument-limits.json`](../modalities/surfaceome-instrument-limits.json) records the
CSPG4 coverage gap (L4) as a one-gene defect. Applying the same membership test across this
12-antigen universe shows **four** genes with **no per-gene row anywhere in the stage-1 artifact** —
**CDH17, CSPG4, RET, SSTR2** — and **two of the three residuals are among them**.

⛔ **The stronger claim is refused, exactly as L4 refuses it.** "Absent from the outputs" is not
"not scanned": the scan unioned ≈2,820 UniProt genes and recorded only its top candidates and
curated seed, never the scanned list, so whether these genes entered the scanned set is
**undecidable**. What *is* decidable is that no per-gene number exists for them anywhere in the
surrogate record — the surrogate never measured them and never rejected them.

⇒ **This reframes the negative.** The known story was *"the surrogate's leads did not reproduce in
EMC tissue"*. The sharper version is that on the new basis the antigens which survive furthest are
**the ones the surrogate's coverage never reached**, which is a statement about the instrument's
gene set rather than about its ranking.

---

## 5 · Controls

All pass, and each read a real value (`aso-delivery-antigen.json` → `controls`).

- **NR4A3** is detected in the EMC arm with a median of `0.000` across the 32 other-sarcoma
  libraries, and is up on GPL6244. ⚠ A zero comparator median means NR4A3 has **no** EMC/sarcoma
  ratio — an undefined ratio, reported as unreadable rather than as an infinite score.
- **ENO3** — a published direct transactivation target of an NR4A3 fusion (PMID 26310886) — is up on
  both arrays and above both 3SEQ arms. It is a cytosolic enzyme and could never be a delivery
  antigen.
- **Negative exposure controls** — GPC3, MSLN, L1CAM and CDH17 all read below the normal-organ
  median, which is the exposure axis demonstrating that it can say "no".
- **Hard control** — PRAME's normal-organ median is `0.000`, so its EMC/normal ratio is
  **undefined**. An instrument that let that read as a perfect exposure score would name a candidate
  off a division by zero. It is excluded twice over, on topology and on readability.
- **Self-consistency** — every array *t* used above was re-derived from the committed per-sample z
  values; zero disagreements. This catches a stale artifact, and it is not a scientific control.

⛔ **A working control licenses reading the other rows and nothing more.**

---

## 6 · What PUB-ASO can now say, and what it must retire

**Can now say** — none of this was available to §3c when it was written:

1. The AOC targeting arm has been tested against **EMC tumour tissue and normal organ tissue**, not
   only against a surrogate. §3c's own flagged next filter has been applied, on both a prior and a
   measured contrast.
2. The delivery gate is bounded by a **negative with a named basis and a named ceiling**: of the 12
   antigens the instruments can score, none clears both axes on every instrument that can read it,
   and none is passed by both normal-tissue instruments.
3. **B7-H3/CD276**, the antigen §3c names by extrapolation, is refused **in the disease's own tumour
   tissue** and not merely on a surrogate selectivity test.
4. The **size of the answerable question** is measured — 12 antigens, against 86 surface-board genes
   the exposure axis cannot reach — and that ceiling belongs in the limitations of any delivery
   claim.
5. **Local / intratumoural administration keeps its place at the top of §3c's list**, and this
   analysis strengthens rather than weakens that ordering: it is the only delivery hypothesis there
   that needs no antigen at all.

**Must retire or amend in §3c** (this memo does not edit that manuscript; the changes are routed):

- ⛔ *"a data-ranked alternative shortlist"* / *"a nameable, prioritised targeting-arm shortlist for
  an EMC AOC"* — those members are surrogate ranks, and two of them, **FGFR1 and PTK7**, are
  concordantly **down** on both arrays in EMC tumour tissue
  ([`emc-surface-target-landscape.md`](./emc-surface-target-landscape.md) §3.5). The shortlist's
  leads point the wrong way in the disease.
- ⛔ *"A public real-EMC tumour dataset exists (GSE4303) but was tried and is UNUSABLE for this"* and
  *"the public-data route to real-EMC surface expression is exhausted"* — superseded by
  [`emc-surface-target-landscape.md`](./emc-surface-target-landscape.md) §3.10.
- ⚠ *"the toxicity-relevant tumour-vs-normal window (GTEx/HPA) is the flagged next filter … not done
  here"* — it is now done.

**Still cannot say:** that any antigen is a delivery handle (nothing here measures protein, surface
density, internalisation or endosomal escape); that naming an antigen would solve delivery
(blood→tumour distribution, myxoid-matrix penetration and endosomal escape are untouched); or that
the readiness register's missing item is discharged. It is not — this makes the reason **precise**
instead of open.

---

## 7 · What would move it, in cost order

1. **$0, one string per gene.** `emc_surface_normal_window.py` → `GENES_BY_SYMBOL` does not contain
   **RET** (nor BGN). Adding it and re-running the existing panels dispatch would give the ranked
   residual its wider normal-tissue prior, which is the single reason it cannot be graded. Not this
   memo's file to change — routed.
2. **$0, already fetched.** **GSM600968** and **GSM600969** in GSE24369 are *"Skeletal muscle pooled
   RNA"* libraries on GPL6244. `emc_expression_panels.py` classifies them `unclassified` and drops
   them — correctly, since feeding normal tissue into a tumour comparator arm was a real bug the RET
   lane found and fixed. But as **their own arm** they are the only normal **soft-tissue** libraries
   anywhere in the three cohorts, and the 3SEQ exposure panel has none. n = 2 and pooled, so a
   second exposure reading on a different normal-tissue class, never a test. Routed.
3. **$0.** Repair the inert vital-tissue override (§4a). Routed.
4. **Collaborator-held, not $0.** For any residual antigen: IHC or surface proteomics on archival
   EMC with a normal-tissue comparison, plus a single-cell or spatial EMC dataset to assign the
   compartment. Neither is obtainable from public deposits and neither is in hand — the ask is
   already stated in [`emc-surface-target-landscape.md`](./emc-surface-target-landscape.md) §7.

---

## 8 · What this memo does not claim

- That any antigen named or ranked here is on the EMC cell surface. **Every reading is transcript.**
- That any antigen is safe, selective, or has a therapeutic window in EMC. **No such quantity is
  computed** here or in any artifact this analysis reads, and no EMC patient has received any agent
  related to anything named here.
- That an antigen absent from the exposure deposit is low in EMC or absent from normal tissue. It
  **was not measured**.
- That the HPA `RESTRICTED` verdicts are vital-tissue-checked. They are not — §4a.
- That RET, CD44 or CSPG4 is a delivery candidate. **None is named.** They are what remains after
  the axes are applied, which is a work list and not a result.

---

*Provenance: a $0 CPU recompute over committed artifacts —
[`emc-expression-panels.json`](../modalities/emc-expression-panels.json) (both arrays, per-sample
values), [`gse28866-tumour-vs-normal.json`](../modalities/gse28866-tumour-vs-normal.json) (the
exposure axis and its ratio calibration),
[`emc-surface-normal-window.json`](../modalities/emc-surface-normal-window.json) (the HPA prior) and
[`emc-surfaceome-scan.json`](../modalities/emc-surfaceome-scan.json) (stage-1 coverage). No network,
no GPU, no fetch, nothing billed. Scorer and its 21 offline tests:
[`aso_delivery_antigen.py`](../modalities/aso_delivery_antigen.py),
`tests/test_aso_delivery_antigen.py`.*
