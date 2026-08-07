---
id: DOC-GSE28866-READING
title: What GSE28866 says — the first EMC-vs-normal-tissue expression contrast in this repository
level: L3
kind: reading
status: live
canonical_for:
  - the interpretation of `gse28866-tumour-vs-normal.json`
  - which of the four live paper candidates this deposit moves, and in which direction
purpose: >
  GSE28866 is the only deposit reachable at $0 that carries EMC libraries alongside NORMAL tissue.
  This file states what its per-gene medians do and do not settle. It re-types no figure: the
  artifact owns every number.
scope: >
  One deposit, 19 genes, n = 4 EMC. Transcript only. Nothing here asserts affinity, efficacy,
  safety, selectivity, a therapeutic window or clinical readiness, and no such quantity is computed.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-07
last_verified: 2026-08-07
---

# GSE28866 — what it settles, and what it moves

**Every number lives in [`gse28866-tumour-vs-normal.json`](../modalities/gse28866-tumour-vs-normal.json)
→ `per_gene.values`.** This file states only the reading.

---

## 1 · What the deposit actually gives — two axes, not one

⚠ **I got this wrong twice on the way in and both corrections matter.**

**First reading (too strong):** *"this decides whether ALCAM is a paper or a lineage artefact."* It does
not, on its own. The 27 normals are **bowel, breast, colon, kidney, lung and uterus** — visceral organs
with almost no soft tissue in them. A gene high in EMC against *that* panel is not thereby shown to be
EMC-specific rather than mesenchymal-lineage-specific.

**Second reading (too weak):** that the deposit therefore carries no lineage axis. It does — its own.
Alongside the 4 EMC and 27 normal libraries sit **32 non-EMC sarcoma libraries** (DDLPS, ESS, EWS, GIST,
LMS, MLPS, SS). So GSE28866 carries **both** contrasts on one technology in one experiment:

| arm | n | what it is the axis for |
|---|---|---|
| 27 normal organ libraries | 27 | **on-target/off-tumour exposure** — the question every surface-antigen claim rests on, and one this repository had never been able to ask |
| 32 other-sarcoma libraries | 32 | **lineage** — the same axis as GSE24369/GSE4303, on a **third cohort and a third technology** |

⭐ **That second arm is why the deposit is worth more than a robustness check.** A gene that moves the
same way on GPL6244, GPL3290 *and* 3SEQ is replicated across platform families, not just across cohorts.

## 2 · The internal control landed, which is why the rest is readable

**NR4A3 is detected in the EMC arm and its median across the 32 other sarcomas is `0.000`.** That is the
fusion's own 3′ partner behaving exactly as the disease definition requires, in a cohort this repository
did not choose and on an assay it did not design. Nothing was tuned to make that happen — the gene list
was fixed before the table was parsed.

⛔ **It is a control, not a result.** It does not license reading any *other* row as validated; it
licenses reading the rows at all.

## 3 · Ceilings that travel with every row

- **n = 4 EMC.** These are medians of four libraries. No confidence interval, no test, no distribution.
- **Medians of per-peak medians of 3SEQ read density.** Not array intensity — **never pool with
  GPL6244/GPL3290**, whose z-scores and percentiles measure a different thing.
- **Several genes rest on a single peak** (CSPG4, FAP, GPC3, L1CAM, PRAME). One peak has no internal
  replication; `n_peaks` is in the artifact for exactly this reason.
- **Transcript, not protein. No surface localisation.** A membrane protein's mRNA says nothing about how
  much of it is on the outside of a cell, which is the quantity a surface-directed agent would see.
- **The normals are a tissue panel, not matched adjacent tissue**, and six organs are not a body.

---

## 4 · What it does to the four live paper candidates

### ⛔ 4 · ALCAM — **demoted, and on the axis that mattered**

`emc_median` **0.578** against `normal_median` **0.631**: on this cohort ALCAM in EMC is **not above**
normal visceral tissue. Against other sarcomas it is up (0.377), directionally consistent with the
array cohorts — so the *lineage* half survives and the *exposure* half does not.

⇒ **ALCAM-as-a-marker is untouched. ALCAM-as-a-surface-target is materially weaker**, because the
exposure axis is the one a surface-directed modality lives or dies on, and this is the first time the
repository has been able to look at it at all. ⚠ This is a **single-cohort, n = 4, transcript-level**
reading and it is not a safety statement; it is a reason to stop treating the target axis as open.

⚠ **And ALCAM had a second problem that is not about GSE28866 at all.** The read that produced its
array effect sizes (`read_8_SURFACE_ANTIGEN`) is **absent from `emc_expression_panels.py` on this
branch** and ALCAM has **no `gene_reads` entry**, so those figures are not currently reproducible from
anything committed here. That is a provenance gap to close before the number is quoted again,
independent of anything this deposit says.

### ⭐ 3 · The fusion's transcriptional output — **strengthened, and it is the biggest beneficiary**

All three named genes move the right way on both axes, in a third cohort on a third technology:

| gene | EMC | vs normal | vs other sarcoma |
|---|---|---|---|
| **ENO3** | 1.772 | **2.5×** | **2.0×** |
| **SEMA3C** | 0.535 | 1.8× | 1.7× |
| **PPARG** | 0.394 | 1.4× | 2.1× |

ENO3 was already the strongest row on both arrays; it is now the strongest row on a platform that
shares no probe design with either. **PPARG's array evidence was the weakest of the three** (one cohort
significant, one not) and it is the row 3SEQ helps most, because a weak effect that reproduces on an
unrelated assay is a different object from a weak effect that does not.

### ○ 1 · Partner stratification — **essentially unmoved**

GSE28866 carries no fusion-partner annotation, so it cannot stratify. The one indirect contribution is
that **SEMA3C**, the mechanistic half of that candidate, replicates here — which supports the mechanism
without touching the clinical stratification claim that is the paper's actual subject.

### ○ 2 · "Response rate is the wrong endpoint" — **unmoved, correctly**

That candidate is a clinical-evidence argument built on trial and registry outcomes. No expression
deposit can move it, and it would be a category error for one to try.

---

## 5 · What the deposit produced that was not on the list

⭐ **CSPG4** is the largest signal in the panel: `emc_median` **8.730**, roughly **3.3× normal** and
**2.5× other sarcomas** — an order of magnitude above every other row in absolute terms, up on **both**
axes. **RET** (3.5× normal, 3.7× sarcoma) and **VCAN** (3.3× / 2.0×) also clear both.

⛔ **Read as a lead, not a finding.** CSPG4 rests on **one peak**, n = 4, transcript only, and HPA already
places it on the broad-liability list — so its normal-tissue behaviour beyond these six organs is
unaddressed here. What it earns is a place in the surface-antigen lane's next pass, not a claim.

✅ **And the panel's negatives are informative in the same breath:** GPC3, MSLN, L1CAM and CDH17 all read
**lower in EMC than in normal tissue**, which is what a working assay should say about antigens with no
reason to be there.
