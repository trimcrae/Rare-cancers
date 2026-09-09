---
id: DOC-PORTFOLIO-INVESTIGATION-ANDGATE-2-EVIDENCE-2026-09-09
title: "ANDGATE-2 — concentration evidence table for C_E, with per-source provenance and every conversion assumption"
level: L4
kind: evidence-table
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: ANDGATE-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# Concentration evidence for C_E — what the published record actually contains

`C_E` is the quantity the PUB-ANDGATE lane showed to be decisive: **the free concentration
of engageable wild-type EWSR1 low-complexity (LC) arm-2 sites in the compartment where the
ligand acts.** Retrieval was by the PubMed/PMC MCP route only; no direct HTTP fetch was
attempted (proxy-refused in this environment). Every attempt, including the ones that
returned nothing, is in `checks/` with a real exit code.

All bibliographic data below is from **PubMed**; DOI links are given for each source.

## 0. Headline

**No source measures `C_E`.** Not one of the retrieved papers reports the free engageable
wild-type EWSR1-LC site concentration, in bulk nucleoplasm or inside a condensate. What
exists is a set of **adjacent** measurements — one of them a direct in-cell concentration
of a FET-LC-bearing protein in the disease-relevant cell line — that together bound the
**bulk** regime by an order-of-magnitude argument, and leave the **intra-condensate**
regime, which is the regime the design proposes to act in, unmeasured.

## 1. Sources retrieved, with what each actually measured

### S1 — Chong et al. 2018, *Science* 361:eaar2555
PMID 29930090 · PMC6961784 · [DOI](https://doi.org/10.1126/science.aar2555)
Full text retrieved: `checks/06-pubmed-fulltext-PMC6961784-chong2018/`.

| item | value as published |
|---|---|
| **Intranuclear concentration of endogenously Halo-tagged EWS/FLI1 in A673 Ewing sarcoma cells** | **~200 nM** |
| method | fluorescence correlation spectroscopy **and** fluorescence-intensity measurement, each calibrated against standard concentration curves of purified EYFP/mCherry measured the same way; two orthogonal methods reported as consistent |
| tagging | HaloTag knocked in at the endogenous locus by CRISPR-Cas9, so expression is at native levels (the authors state this was essential because LCDs behave aberrantly when overexpressed) |
| median EWS/FLI1 copies per GGAA-microsatellite hub | 24 (vs ~8 accountable by direct DNA binding) |
| hubs per nucleus | >1000, same order as the ~6000 EWS/FLI1-bound GGAA microsatellites estimated by ChIP-seq |
| stated operating range of LCD transactivation hubs | **100 nM to 100 µM** (graphical abstract / abstract) |
| **discrepancy, reported not resolved** | the retrieved PMC **body text** prints "100 nM to 100 **mM**" at the corresponding Discussion sentence. The abstract and graphical abstract say **µM**. This lane uses µM and flags the inconsistency rather than picking silently. A reader relying on this number should check the published figure. |
| phase separation at endogenous levels | the authors state they did **not** obtain evidence of phase separation of EWS/FLI1 hubs at endogenous expression levels; apparent LLPS was seen only on gross overexpression |

**What must be assumed to use this as `C_E`:**
1. **Species substitution.** This is **EWS/FLI1**, the fusion, which carries the EWSR1 LC
   (approximately EWSR1 residues 1–265). It is **not wild-type EWSR1**. Wild-type EWSR1
   abundance in the same cells is not reported here or, so far as this retrieval found,
   anywhere. Wild-type EWSR1 is plausibly the more abundant species. **Stated explicitly:
   this is an anchor for the scale of a FET-LC-bearing nuclear protein in the right cell
   line, not a measurement of the wild-type pool.**
2. **No copy-number conversion is applied**, because none is needed — this is already a
   concentration measured in live cells. That removes the nuclear-volume assumption that
   dogs every proteomic route (see §2).
3. **Site multiplicity.** The model's `C_E` counts engageable **arm-2 sites**, not protein
   chains. Taking 200 nM as `C_E` assumes **one engageable site per chain**. Swept in
   `andgate2-literature-placement.json`.
4. **Free and engageable.** Total intranuclear concentration is an **upper bound** on the
   free engageable pool: chromatin-bound, RNA-bound, complexed and self-associated LC is
   not available to a ligand. Using it as `C_E` is therefore conservative *against* the
   design.

### S2 — Wang et al. 2018, *Cell* 174:688–699
PMID 29961577 · PMC6063760 · [DOI](https://doi.org/10.1016/j.cell.2018.06.006)
Full text retrieved: `checks/12-pubmed-fulltext-PMC6063760-wang2018/`.

| item | value as published (verbatim where quoted) |
|---|---|
| **FET-family cellular concentration ceiling** | assays were run at 5 µM and "**In most cases, this concentration lies above the physiological concentration in HeLa cells** … of these proteins" (22 FUS-family proteins assayed) |
| FUS full-length saturation concentration | "The measured saturation concentration of full-length FUS is **~2 µM in 75 mM KCl**" (in vitro, purified, tagged) |
| FUS PLD alone saturation concentration | **>120 µM** — an order of magnitude above the full-length protein |
| hnRNPA1 physiological concentration | **~8 µM** (a *different* protein, quoted by the authors from cited work; included only as a scale comparison) |
| EWSR1 Tyr+Arg count in disordered regions | **80** (FUS 69, TAF15 109) |
| client partitioning | 12 of 19 FUS-family clients partition into preformed FUS droplets; partition coefficients correlate with Tyr+Arg number — **protein** clients, not small molecules, and no numeric Kp is quoted in the retrieved text |

**What must be assumed to use this as `C_E`:**
1. The 5 µM statement is a **family-level statement citing other work**, not a new
   per-protein EWSR1 measurement in this paper, and not a number for a fusion-bearing
   cell. It functions as a **bulk ceiling**, not a value.
2. **Cellular → nucleoplasmic.** Treating a cellular concentration as a nucleoplasmic one
   assumes EWSR1 is predominantly nuclear **and uniformly distributed within the nucleus**.
   The second half is exactly what condensate formation violates, and is why the
   intra-condensate regime cannot be reached from a bulk number.
3. The `c_sat` numbers are **in vitro**, at 75 mM KCl, on purified tagged protein. The
   nucleus is not that buffer: RNA, crowding, PTMs and partners all move `c_sat`.
4. `c_sat` is used here **only** as a scale check on a physical argument (§3), never as a
   value of `C_E`.

### S3 — Klein et al. 2020, *Science* 368:1386–1392
PMID 32554597 · PMC7735713 · [DOI](https://doi.org/10.1126/science.aaz4427)
Full text retrieved: `checks/03-pubmed-fulltext-PMC7735713-klein2020/`.

This is the paper for target (c) — small-molecule partition coefficients into nuclear
condensates — and it is the **clearest negative** in this table.

| item | value as published |
|---|---|
| cisplatin partition coefficient into **MED1** condensates | **up to 600** |
| other drugs concentrating in MED1 condensates | mitoxantrone (also FIB1, NPM1), FLTX1 (tamoxifen analogue), THZ1; JQ1 in MED1, BRD4 and NPM1 |
| non-partitioning controls | fluorescein (332 Da), Hoechst (452 Da) and 4.4 kDa dextrans diffuse through all six condensates without substantial partitioning |
| physicochemical driver | aromatic rings; a MED1 aromatic-null mutant (all 30 aromatics → Ala) still forms droplets but no longer concentrates aromatic probes or cisplatin |
| **condensate scaffolds tested** | MED1, BRD4, SRSF2, HP1α, FIB1, NPM1 |
| **FET-family scaffold tested** | **none** |

**Consequence, stated plainly:** the published record contains a measured small-molecule
condensate partition coefficient of order 10²–10³ — **for a MED1 condensate**. It contains
**no** small-molecule partition coefficient for a FUS/EWSR1/TAF15 condensate. Adopting 600
as a `Kp` for a FET condensate would be adopting a number from a **different scaffold
protein**, and this lane does not do that. What the Klein result does license is the
weaker, mechanistic statement that the driver is aromatic π-interaction chemistry, and
that the EWSR1 LC is aromatic-rich (S2: 80 Tyr+Arg in EWSR1's disordered regions) — so a
FET-condensate `Kp` substantially above 1 is *plausible*, and that is a hypothesis to be
measured, not a value to be used.

### S4 — Wiśniewski, Hein, Cox & Mann 2014, *Mol Cell Proteomics* 13:3497
PMID 25225357 · PMC4256500 · [DOI](https://doi.org/10.1074/mcp.M113.037309)
Full text retrieved: `checks/10-pubmed-fulltext-PMC4256500-proteomic-ruler/`.

Retrieved for target (b). It is the **methodology** for turning proteomic signal into copy
numbers and concentrations; **it does not report EWSR1**.

| assumption the method requires | value / tolerance as published |
|---|---|
| DNA per diploid human cell | 6.5 pg |
| histone protein mass ≈ DNA mass | asserted as the ruler's basis |
| histone MS signal as % of total MS signal | 2.07–4.03% across four human lines |
| total protein per cell, ruler vs cell counting | agreement within a factor of **1.24 ± 0.29** |
| individual copy numbers, ruler vs PrEST-SILAC spike-in | average deviation **~1.5-fold** |
| overall claimed accuracy | "typically within a factor of 2" |
| total cellular protein concentration, used to convert mass ↔ volume | **200–300 g/L (20–30% w/v)** |
| depth needed for a stable readout | ≳12,000 peptides |

## 2. The conversion a copy number requires — stated, not buried

Target (b) asked for copy numbers convertible to a nuclear concentration. **No EWSR1 copy
number was retrieved** (`checks/07`, `checks/11`: zero hits). If one is obtained later, the
conversion is

&nbsp;&nbsp;&nbsp;&nbsp;`C = N / (N_A · V_nuc)`

and it carries **six** assumptions, every one of which can move the answer by more than the
factor that separates "negligible" from "materially degraded" on the cost curve:

1. **Nuclear volume `V_nuc`.** Not measured for the cell line of interest by any source
   retrieved here. This lane deliberately does **not** substitute a textbook value: a
   nucleus 2× larger in diameter is 8× lower in concentration, which alone spans most of
   the interesting part of the curve.
2. **Nuclear fraction.** Copy numbers from whole-cell proteomics are per *cell*. Converting
   to a nuclear concentration assumes a nuclear-localised fraction, which is a separate
   measurement (spatial proteomics or fractionation), not retrieved.
3. **Uniformity within the nucleus.** A single nucleoplasmic concentration presumes uniform
   distribution. For a condensate-forming protein this is false by construction, and it is
   precisely the failure that separates the two regimes of this analysis. **A bulk number
   can never answer the intra-condensate question.**
4. **Free vs bound.** The model needs *free engageable* sites. Total abundance is an upper
   bound; the bound fraction (chromatin, RNA, protein complexes, self-association) is
   unmeasured. Target (d) — any published measurement of free versus condensate-sequestered
   FET protein — returned **nothing** in this retrieval.
5. **Site multiplicity per chain.** `C_E` counts arm-2 sites. One site per chain is a
   choice, not a fact; the manuscript does not specify what arm 2 binds (and carries two
   incompatible readings of it, per the parent lane). EWSR1's disordered regions carry 80
   Tyr+Arg residues (S2). This multiplier is swept, and it is the single assumption most
   able to overturn the bulk verdict — see §4.
6. **Cell-type transfer.** A HeLa or U2OS copy number is not a Ewing-sarcoma or
   myxoid-liposarcoma number.

The proteomic-ruler route additionally inherits S4's own ~2-fold accuracy and its 200–300
g/L total-protein convention.

## 3. The one physical argument that constrains the bulk regime

Independent of any copy number, two retrieved measurements constrain the **free** bulk pool:

* In a system at two-phase equilibrium, the dilute-phase concentration is pinned near the
  saturation concentration. Full-length FUS `c_sat` ≈ **2 µM** in vitro (S2).
* Chong et al. report **no detectable phase separation** of endogenous EWS/FLI1 hubs at
  native expression (S1), i.e. that system sits **below** its `c_sat`, so its free
  concentration is its total concentration, ~**200 nM**.

These two point the same way: **the free bulk nucleoplasmic pool of FET-LC protein is
sub-micromolar to low-micromolar**, not tens or hundreds of micromolar. This is an
*inference from published measurements*, labelled as such — it is not itself a measurement
of `C_E`, and it says nothing about the inside of a condensate.

## 4. What is still missing — the named experimental requirement

| target | status after this retrieval |
|---|---|
| (a) absolute nuclear concentration of **EWSR1** or FET LCDs in human cells | **not found.** The closest is S1's ~200 nM for the *fusion* EWS/FLI1 in A673, and S2's family-level "<5 µM in HeLa" statement. |
| (b) proteomic **copy number** for EWSR1 convertible with a stated nuclear volume | **not found.** No EWSR1 copy number retrieved; no nuclear volume retrieved. S4 supplies only the conversion method and its assumptions. |
| (c) intra-condensate **partition coefficient for a small molecule** into a FET-family condensate | **not found.** S3 measures up to 600 for cisplatin into **MED1**; no FET scaffold was tested in it, and no other source was found. |
| (d) published measurement of **free vs condensate-sequestered FET protein** | **not found.** Zero hits. |

The decisive experiment is therefore nameable and small: **measure the free engageable
wild-type EWSR1-LC site concentration inside and outside FET condensates in a
fusion-bearing cell** — for instance by FCS on endogenously tagged wild-type EWSR1 with
in-hub versus nucleoplasmic segmentation, exactly the assay S1 already ran on the fusion,
plus a partition measurement for a candidate probe into a FET condensate of the kind S3 ran
on six non-FET scaffolds. Both are established methods in the cited papers. Neither
requires new chemistry, and neither requires the arm-2 ligand that does not exist.
