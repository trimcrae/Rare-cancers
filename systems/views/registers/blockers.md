---
id: DOC-VIEW-BLOCKERS
title: Blocker register
level: cross-cutting
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Every reason work is stalled, typed, ordered by how much of the portfolio it holds down, and joined to the forecast band that would retire it.
scope: "All blockers. Vocabulary and selection rules: systems/taxonomy/blockers.md"
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-08
last_verified: 2026-08-08
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# Blocker register

Typed with [`taxonomy/blockers.md`](../../taxonomy/blockers.md). The kinds are **never conflated**:
*the biology forbids it*, *today's method cannot resolve it*, *nobody has run the assay* and
*we have not been given the decision* are four situations with four different remedies.

## By kind

| kind | n | permanent |
|---|---:|---|
| `fundamental_biological_limit` | 2 | **yes** |
| `insufficient_data` | 4 | no |
| `no_known_assay` | 2 | no |
| `requires_authorization` | 2 | no |
| `requires_better_simulation_accuracy` | 1 | no |
| `requires_better_structure_prediction` | 2 | no |
| `requires_external_collaboration` | 1 | no |
| `requires_future_technology` | 2 | no |
| `requires_wet_lab` | 3 | no |
| `scientific_uncertainty` | 1 | no |

## By fan-out — the portfolio's shape

**Reach** is derived from the strategy families a blocker spans, not from the route count alone: `portfolio-wide` ≥ 5 of 13 families, `cross-family` ≥ 2, `single-family` 1. Two blockers can hold the same number of routes and mean very different things — one concentrated in a single family is a route-selection problem, one spread across six is a program-level one.

| blocker | kind | routes held | families | reach | routes that retire it | what would retire it |
|---|---|---:|---:|---|---:|---|
| **BLK-NO-EMC-DATA**<br/>EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRIS | `insufficient_data` | 38 | 7 | portfolio-wide | 0 | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |
| **BLK-NO-WET-LAB**<br/>No wet lab and no collaborator — an ask needs a self-interested taker before its size matt | `requires_external_collaboration` | 16 | 7 | portfolio-wide | 2 | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-NOT-FUSION-SELECTIVE**<br/>The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half) | `fundamental_biological_limit` | 14 | 6 | portfolio-wide | 8 | **permanent — nothing** |
| **BLK-NO-CURATED-CLINICAL-DATA**<br/>The clinical facts these routes need are IN the published record and have never been extra | `insufficient_data` | 9 | 3 | cross-family | 0 | `TECH-RECONSTRUCTED-IPD` |
| **BLK-PARALOGUE-DDG**<br/>The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT) | `requires_better_simulation_accuracy` | 9 | 3 | cross-family | 24 | `TECH-FE-CRYPTIC-POCKET` |
| **BLK-CLASS-INHERITANCE**<br/>Class inheritance, not an EMC measurement — no NR4A3 fusion has been tested for the phenot | `insufficient_data` | 5 | 3 | cross-family | 0 | `TECH-VIRTUAL-CELL` |
| **BLK-ANTIGEN-COLD**<br/>EMC is antigen-cold, and the fusion junction is a weak peptide-HLA | `fundamental_biological_limit` | 10 | 2 | cross-family | 0 | **permanent — nothing** |
| **BLK-R4-BINDS**<br/>R4 — nothing is known to bind the cryptic pocket at all | `requires_wet_lab` | 8 | 2 | cross-family | 4 | `TECH-EMC-MODEL-ACCESS` |
| **BLK-UNSIZED-REQUIREMENT**<br/>The selectivity requirement is now STATED for all three routes, and three of its inputs ar | `requires_wet_lab` | 3 | 2 | cross-family | 0 | Obtain the three dose-responses named as MISSING-1, MISSING-2 and MISSING-4 in selectivity-requirement-sizing.md. Until … |
| **BLK-TERNARY-GEOMETRY**<br/>Ternary geometry — assembly, E3, exit vector, ubiquitin transfer | `requires_better_structure_prediction` | 5 | 1 | single-family | 24 | `TECH-COFOLD-ASSEMBLY`, `TECH-E3-RECRUITER-STRUCTURE`, `TECH-OBSERVED-CRL` |
| **BLK-INDUCED-COMPLEX**<br/>An induced ternary/bivalent complex is still required (a second protein must be placed) | `requires_better_structure_prediction` | 3 | 1 | single-family | 1 | `TECH-COFOLD-ASSEMBLY` |
| **BLK-VECTOR-DELIVERY**<br/>Vector delivery (gene-therapy payload into a solid tumour) | `requires_future_technology` | 3 | 1 | single-family | 0 | `TECH-VECTOR-DELIVERY` |
| **BLK-REACH-CATEGORICAL**<br/>The categorical (covalent) window at C397 does not survive the E3-arm-free reach enumerati | `scientific_uncertainty` | 2 | 1 | single-family | 0 | `TECH-EXPOSURE-CRITERION` |
| **BLK-DELIVERY**<br/>SYSTEMIC, antigen-dependent tumour delivery of an oligonucleotide or a vector — NOT delive | `requires_future_technology` | 1 | 1 | single-family | 0 | `TECH-OLIGO-DELIVERY` |
| **BLK-ENDPOINT-MD**<br/>Endpoint-MD selectivity readout (E1) returns null | `no_known_assay` | 1 | 1 | single-family | 0 | `TECH-E1-POWERED` |
| **BLK-FUNCTIONAL-ACTIONABILITY**<br/>Is the LBD a FUNCTIONAL handle in the chimera, whose other end is a strong independent act | `requires_wet_lab` | 1 | 1 | single-family | 1 | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-PARALOGUE-CONTROL**<br/>The paralogue-discrimination positive control (NR-V04) is discordant | `no_known_assay` | 1 | 1 | single-family | 0 | `TECH-NONCOVALENT-PARALOGUE-CONTROL` |
| **BLK-REGISTRY-DUA**<br/>Population cancer-registry microdata (SEER, NCDB) needs a signed data-use agreement | `requires_authorization` | 1 | 1 | single-family | 0 | An action only trimcrae can take: register for SEER research data and sign the agreement. ⚠ DO NOT DO THIS FIRST. The pr… |
| **BLK-SELECTIVITY-CONTROL-UNAUTHORIZED**<br/>The program's only binary selectivity known-answer control is built and staged and has nev | `requires_authorization` | 1 | 1 | single-family | 0 | Ask for the decision. This blocker is cheaper to retire than any other in the register and it gates the one control that… |
| **BLK-TCIP-INTERFACE-FLOOR**<br/>How much induced interface a transcriptional CIP needs is unsized, and the degrader-derive | `insufficient_data` | 1 | 1 | single-family | 0 | Find, for ANY chemically-induced transcriptional-proximity system, a relationship between a CHARACTERISED induced interf… |

## When each blocker could lift

⚠ **A band is a forecast, not a measurement, and `basis` is the part that says which.** `evidence_based` rests on something already partly landed; `extrapolated` on a trend; `speculative` on an event nobody has scheduled. A row's date means nothing without it.

⛔ **`basis` GRADES THE TECHNOLOGY'S CURRENT STATE, NOT THE DATE — read `confidence` for the date** (2026-08-08, after `evidence_based` on BLK-TERNARY-GEOMETRY was read as evidence for **2027** and is not). Its forecast is `evidence_based` because one arm HAS landed — high inter-chain accuracy when both binding sites are given. The 2027 band's own rationale is a pace argument about how fast the field iterates, and its `confidence` is `moderate`. A strong `basis` beside a soft band is the shape most likely to be misread here, so both columns are printed and neither is derived from the other.

⚠ **Earliest-wins.** Where several technologies claim the same blocker they are ALTERNATIVES, so the soonest `expected` band governs and the rest are upside. The full spread is in each blocker's detail section below.

⛔ **A coming capability justifies waiting and re-running. It never licences claiming the result before the method can support it.**

| blocker | routes held | reach | expected | band confidence | basis (of the STATE) | via |
|---|---:|---|---|---|---|---|
| **BLK-NO-CURATED-CLINICAL-DATA** | 9 | cross-family | **2026H2** | `moderate` | `evidence_based` | `TECH-RECONSTRUCTED-IPD` |
| **BLK-TERNARY-GEOMETRY** | 5 | single-family | **2027** | `moderate` | `evidence_based` | `TECH-COFOLD-ASSEMBLY`, `TECH-E3-RECRUITER-STRUCTURE`, `TECH-OBSERVED-CRL` |
| **BLK-INDUCED-COMPLEX** | 3 | single-family | **2027** | `moderate` | `evidence_based` | `TECH-COFOLD-ASSEMBLY` |
| **BLK-REACH-CATEGORICAL** | 2 | single-family | **2027H2** | `low` | `extrapolated` | `TECH-EXPOSURE-CRITERION` |
| **BLK-NO-EMC-DATA** | 38 | portfolio-wide | **2028** | `low` | `extrapolated` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |
| **BLK-PARALOGUE-DDG** | 9 | cross-family | **2028** | `low` | `extrapolated` | `TECH-FE-CRYPTIC-POCKET` |
| **BLK-CLASS-INHERITANCE** | 5 | cross-family | **2028** | `low` | `extrapolated` | `TECH-VIRTUAL-CELL` |
| **BLK-PARALOGUE-CONTROL** | 1 | single-family | **2028** | `low` | `speculative` | `TECH-NONCOVALENT-PARALOGUE-CONTROL` |
| **BLK-NO-WET-LAB** | 16 | portfolio-wide | **2029** | `low` | `extrapolated` | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-R4-BINDS** | 8 | cross-family | **2029** | `low` | `speculative` | `TECH-EMC-MODEL-ACCESS` |
| **BLK-DELIVERY** | 1 | single-family | **2029** | `low` | `extrapolated` | `TECH-OLIGO-DELIVERY` |
| **BLK-ENDPOINT-MD** | 1 | single-family | **2029** | `low` | `speculative` | `TECH-E1-POWERED` |
| **BLK-FUNCTIONAL-ACTIONABILITY** | 1 | single-family | **2029** | `low` | `extrapolated` | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-VECTOR-DELIVERY** | 3 | single-family | **2030** | `low` | `speculative` | `TECH-VECTOR-DELIVERY` |
| **BLK-UNSIZED-REQUIREMENT** | 3 | cross-family | *not forecast — an action, not an advance* | — | — | — |
| **BLK-TCIP-INTERFACE-FLOOR** | 1 | single-family | *not forecast — an action, not an advance* | — | — | — |
| **BLK-NOT-FUSION-SELECTIVE** | 14 | portfolio-wide | *never* | — | — | — |
| **BLK-ANTIGEN-COLD** | 10 | cross-family | *never* | — | — | — |
| **BLK-REGISTRY-DUA** | 1 | single-family | *on request* | — | — | — |
| **BLK-SELECTIVITY-CONTROL-UNAUTHORIZED** | 1 | single-family | *on request* | — | — | — |

✅ Every blocker resolves to a forecast band, a permanent verdict, a decision or an action — none is left as an unanalysed gap.

## Detail

### BLK-NO-EMC-DATA

**EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)**

- **kind:** `insufficient_data`
- **a statement about:** data availability — the repo-wide rate-limiter, not any one route
- **held by (38):** RT-6MP, RT-ALK-HIT, RT-APOPTOSIS-DEP, RT-ARGININE, RT-ASO-ASK, RT-ATR-ASSESS, RT-ATR-PANEL, RT-B7H3, RT-CARFILZOMIB, RT-CART-SURFACE, RT-CHAPERONE, RT-DNAPK, RT-EZH2, RT-FAP-RLT, RT-HORMONE-PARTNER, RT-HYPOXIA-PRODRUG, RT-ICI-TKI, RT-IMMUNOCYTOKINE, RT-JUNCTION-NEOANTIGEN, RT-MATRIX-ADDRESS, RT-MATRIX-SYNTHESIS, RT-MDM2, RT-MTAP-PRMT5, RT-NR2F1, RT-PARTNER-STRAT, RT-POLQ, RT-PPARG-DOWNSTREAM, RT-PRAME-IMMTAC, RT-RET, RT-SGK1, RT-SSTR2, RT-SYNLETH-DEP, RT-SYNPROMOTER, RT-TCRT-CTA, RT-TRABECTEDIN, RT-TRABECTEDIN-PPARG, RT-TXN-CDK, RT-VACCINE-COMBINATION
- **retired by route (0):** —
- **retired by technology:** TECH-EMC-EXPRESSION-DATA, TECH-VIRTUAL-CELL
- **⭐ retired by an action we can take:** NOT RETIRED, and the 2026-08-08 lead is recorded here so that it cannot be mistaken for a retirement. PRJNA1357027 / SRP640302 is a real, public, fourth EMC cohort — n = 12 FFPE tumours, downloadable since 2025-11-11, carrying per-sample EWSR1 break-apart FISH status, site, size, morphology and outcome-adjacent annotation, and larger than any of the three cohorts the manuscript reads (emc-fourth-cohort-sra-2026-08-08.md; artifact emc-sra-study.json, transport gate passed on three controls). It is TempO-Seq TARGETED-PANEL data, so its gene space is the panel's and the panel is not named anywhere in the archive metadata. This blocker's statement is about FUNCTIONAL-GENOMICS data — one DepMap line, no CRISPR — and a tumour expression panel is not a dependency screen, so nothing here touches it. What WOULD retire it is an EMC dependency or drug-response screen (a second EMC line in DepMap, a CRISPR screen, or an ex-vivo panel), none of which exists; TRG-SARCOMA-ATRI-RESPONSE-PANEL watches for it. The nearest $0 step on the cohort itself is naming the TempO-Seq panel, on which every read of it is gated.
- **evidence:** research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md / research/modalities/emc-sra-study.json / research/modalities/emc-sra-study-inputs.json
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-VIRTUAL-CELL` | `early_signals` | 2027H1 | **2028** | 2030 | `low` | `extrapolated` |
  | `TECH-EMC-EXPRESSION-DATA` | `early_signals` | 2027 | **2029** | beyond-2031 | `low` | `speculative` |

- **owner:** `research/IDEAS.md`

### BLK-NO-WET-LAB

**No wet lab and no collaborator — an ask needs a self-interested taker before its size matters**

- **kind:** `requires_external_collaboration`
- **a statement about:** the operating regime, not any route's science
- **held by (16):** RT-ALK-HIT, RT-ASO-ASK, RT-ATR-PANEL, RT-CHAPERONE, RT-COVALENT-PROBE, RT-DNAPK, RT-EZH2, RT-FAP-RLT, RT-MATRIX-ADDRESS, RT-RET, RT-RIPTAC, RT-SGK1, RT-SSTR2, RT-SYNLETH-DEP, RT-TCIP, RT-TRABECTEDIN-PPARG
- **retired by route (2):** RT-ENDPOINT-CHOICE, RT-METHODS-PAPER
- **retired by technology:** TECH-CLOUD-WET-LAB, TECH-EMC-MODEL-ACCESS
- **⭐ retired by an action we can take:** A collaborator who holds an EMC line — unchanged, and NOT retired by money. ⭐ WHAT CHANGED 2026-08-23 IS THAT THE ASK NOW HAS A SIZE. This blocker's own statement says 'an ask needs a self-interested taker before its size matters', and the size was genuinely unknown: what-a-civilian-can-buy.md §4.4 found every CRO quote-only and recorded F1 as unevaluable. Academic core facilities publish rate cards, so it is evaluable at $0 — the portfolio's SMALLEST ask (route 1b) prices at roughly $18k, of which the catalogue compounds the route memo emphasises are about 2%. ART-WETLAB-CONTRACTING-COSTS owns the numbers. ⛔ THIS DOES NOT WEAKEN THE BLOCKER AND MUST NOT BE READ AS PROGRESS TOWARDS RETIRING IT. The gate is eligibility, not price: the three EMC lines are institution-gated by policy and held under MTA by their originating groups, and every costed experiment except R4's binding half needs them. ⚠ NOR DOES LAB AUTOMATION RETIRE IT — measured against the model, hourly labour is 60.9% of the total, and with hands entirely FREE no experiment falls below $2,000 while the cell-engineering ones do not move at all. method-watch.md's remote-robotic-wet-lab row already held the correct form of this: a cloud lab flips the EXECUTION gate, not the MATERIAL gate. What a number does buy is a better outreach ask — 'this is ~$18k of your core's time and here is the preregistration' rather than 'would you run this?'
- **evidence:** research/manuscripts/modality-census/what-a-civilian-can-buy.md / research/manuscripts/modality-census/wet-lab-contracting-costs.md / research/modalities/wetlab-contracting-costs.json
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-CLOUD-WET-LAB` | `early_signals` | 2027H2 | **2029** | beyond-2031 | `low` | `extrapolated` |
  | `TECH-EMC-MODEL-ACCESS` | `absent` | 2027H2 | **2029** | beyond-2031 | `low` | `speculative` |

- **owner:** `research/manuscripts/modality-census/what-a-civilian-can-buy.md`

### BLK-NOT-FUSION-SELECTIVE

**The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)**

- **kind:** `fundamental_biological_limit` · **PERMANENT**
- **a statement about:** what the molecule can and cannot tell apart
- **held by (14):** RT-6MP, RT-B7H3, RT-CART-SURFACE, RT-COVALENT-PROBE, RT-DBD, RT-DEGRADER, RT-EWSR1-PROTEIN, RT-FET-LC-LIGAND, RT-GLUE, RT-MONOVALENT, RT-PRAME-IMMTAC, RT-RIPTAC, RT-SYNPROMOTER, RT-UBIQ-SELECTIVE
- **retired by route (8):** RT-ASO, RT-FAP-RLT, RT-ICI-TKI, RT-JUNCTION-NEOANTIGEN, RT-PANNR4A-EXVIVO, RT-RIBOZYME, RT-SSTR2, RT-TCR-IMMTAC
- **when it could lift:** **never** — a fact about what the objects are. No technology in the register claims to retire it, and [B1] fails the build if one ever does. What CAN change is whether it stays decisive for a given route: a route either sidesteps it by construction or it does not.
- **owner:** `research/manuscripts/program/target-route-options.md#3--what-genuinely-sidesteps-the-paralogue-problem-and-what-merely-relocates-it`

### BLK-ANTIGEN-COLD

**EMC is antigen-cold, and the fusion junction is a weak peptide-HLA**

- **kind:** `fundamental_biological_limit` · **PERMANENT**
- **a statement about:** the tumour's immunogenicity, shared by every antigen-directed route
- **held by (10):** RT-B7H3, RT-CART-SURFACE, RT-ICI-TKI, RT-IMMUNOCYTOKINE, RT-JUNCTION-NEOANTIGEN, RT-PRAME-IMMTAC, RT-TCR-IMMTAC, RT-TCRT-CTA, RT-VACCINE, RT-VACCINE-COMBINATION
- **retired by route (0):** —
- **when it could lift:** **never** — a fact about what the objects are. No technology in the register claims to retire it, and [B1] fails the build if one ever does. What CAN change is whether it stays decisive for a given route: a route either sidesteps it by construction or it does not.
- **owner:** `research/manuscripts/neoantigen/immunotherapy-options-emc.md`

### BLK-NO-CURATED-CLINICAL-DATA

**The clinical facts these routes need are IN the published record and have never been extracted into the registry**

- **kind:** `insufficient_data`
- **a statement about:** a curation gap in this repository, not a gap in the literature
- **held by (9):** RT-IPD-SURVIVAL, RT-LIMB-PERFUSION, RT-LUNG-DIRECTED, RT-METASTASECTOMY, RT-RISK-MODEL, RT-RT-INTENSIFY, RT-SEQUENCING, RT-SURGICAL-QUALITY, RT-SURVEILLANCE
- **retired by route (0):** —
- **retired by technology:** TECH-RECONSTRUCTED-IPD
- **⭐ retired by an action we can take:** ⭐ AN ACTION WE CAN TAKE, AND IT IS FREE. Extract the missing fields from the open-access series already cited here: margin status, primary anatomical site, metastatic site and burden, time-to-metastasis, treatment setting, and the Kaplan-Meier curves plus numbers-at-risk tables that research/modalities/emc_ipd_survival.py inverts into patient-level data.

⛔ THIS BLOCKER REPLACED A MISATTRIBUTION, AND THE CORRECTION WAS NOT UNIFORM — WHICH IS THE POINT. Six routes across ST-LOCOREGIONAL and ST-STRATEGY inherited BLK-NO-EMC-DATA, whose own record scopes it to FUNCTIONAL-GENOMICS data (one DepMap line, no CRISPR). None of the six needs a dependency screen, so all six lost it. Only FOUR gained this one: RT-LIMB-PERFUSION, RT-LUNG-DIRECTED and RT-RT-INTENSIFY, whose `readiness.missing` names site, burden or per-patient dose curation verbatim, and RT-SEQUENCING, whose timing rationale reads 'Only individual-patient data could change this, and it is not obtainable here'.

⭐ RT-SCHEDULING AND RT-TRIAL-REACH GAINED NOTHING AND ARE NOW UNBLOCKED OUTRIGHT. RT-SCHEDULING's `readiness.missing` says 'nothing to start — the inputs are committed', and RT-TRIAL-REACH's names non-US registry coverage needing an authenticated endpoint, which is an access condition and not a curation gap. Giving either of them a curation blocker would have swapped one mis-scoped blocker for another and left them reading as blocked when they are not. ⚠ RT-SCHEDULING still carries `status: blocked` from its own grade owner (research/manuscripts/endpoint/emc-systemic-therapy-pooling.json); that status was NOT edited here, because a route's grade belongs to its owner and this change belongs to the blocker model. It now shows a blocked route with no blocker, which is a real disagreement for that owner to settle rather than one to paper over.

Superseded, retained: all six routes previously inherited BLK-NO-EMC-DATA. Filing a free curation task behind a technology forecast to 2029 is how work that could be done today reads as work that cannot.
- **evidence:** research/modalities/emc-care-delivery-evidence.json / research/data/emc-clinical-registry.json
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-RECONSTRUCTED-IPD` | `partially_landed` | 2026H2 | **2026H2** | 2027 | `moderate` | `evidence_based` |

- **owner:** `systems/graph/blockers.json`

### BLK-PARALOGUE-DDG

**The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)**

- **kind:** `requires_better_simulation_accuracy`
- **a statement about:** a free-energy difference between two similar pockets, which this program has failed to measure four separate ways
- **held by (9):** RT-ANDGATE, RT-ASYMMETRIC, RT-COVALENT-PROBE, RT-DBD, RT-DEGRADER, RT-GLUE, RT-MONOVALENT, RT-RIPTAC, RT-TCIP
- **retired by route (24):** RT-ASO, RT-ATR-ASSESS, RT-B7H3, RT-CARFILZOMIB, RT-CART-SURFACE, RT-CRISPR-CAS13, RT-EWSR1-PROTEIN, RT-FAP-RLT, RT-FET-LC-LIGAND, RT-HDAC-BET, RT-ICI-TKI, RT-JUNCTION-NEOANTIGEN, RT-PANNR4A-EXVIVO, RT-PPARG-DOWNSTREAM, RT-PRAME-IMMTAC, RT-RIBOZYME, RT-SSTR2, RT-SYNLETH-DEP, RT-SYNPROMOTER, RT-TCR-IMMTAC, RT-TCRT-CTA, RT-TRABECTEDIN, RT-TRABECTEDIN-PPARG, RT-VACCINE
- **retired by technology:** TECH-FE-CRYPTIC-POCKET
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-FE-CRYPTIC-POCKET` | `absent` | 2027H1 | **2028** | 2030 | `low` | `extrapolated` |

- **owner:** `research/manuscripts/nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged`

### BLK-R4-BINDS

**R4 — nothing is known to bind the cryptic pocket at all**

- **kind:** `requires_wet_lab`
- **a statement about:** an unanswered requirement that needs a bench
- **held by (8):** RT-ANDGATE, RT-COVALENT-PROBE, RT-DEGRADER, RT-GLUE, RT-MONOVALENT, RT-RIPTAC, RT-TCIP, RT-UBIQ-SELECTIVE
- **retired by route (4):** RT-ATR-ASSESS, RT-PPARG-DOWNSTREAM, RT-SYNLETH-DEP, RT-TRABECTEDIN-PPARG
- **retired by technology:** TECH-EMC-MODEL-ACCESS
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-EMC-MODEL-ACCESS` | `absent` | 2027H2 | **2029** | beyond-2031 | `low` | `speculative` |

- **owner:** `research/manuscripts/nr4a3-program-map.md#32--the-rv-coverage-matrix--where-the-holes-are`

### BLK-CLASS-INHERITANCE

**Class inheritance, not an EMC measurement — no NR4A3 fusion has been tested for the phenotype**

- **kind:** `insufficient_data`
- **a statement about:** the strength of a transfer argument
- **held by (5):** RT-ATR-ASSESS, RT-FAP-RLT, RT-HDAC-BET, RT-SSTR2, RT-TXN-CDK
- **retired by route (0):** —
- **retired by technology:** TECH-VIRTUAL-CELL
- **⭐ retired by an action we can take:** State plainly, wherever the transfer argument is used, that no NR4A3 fusion has been tested for the phenotype. The blocker cannot be retired by us, but its misreading can. $0.
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-VIRTUAL-CELL` | `early_signals` | 2027H1 | **2028** | 2030 | `low` | `extrapolated` |

- **owner:** `research/manuscripts/program/emc-post-degrader-options.md#route-1---atr-inhibitor-synthetic-lethality-emc-inherits-a-class-vulnerability-it-has-never-been-tested-for`

### BLK-TERNARY-GEOMETRY

**Ternary geometry — assembly, E3, exit vector, ubiquitin transfer**

- **kind:** `requires_better_structure_prediction`
- **a statement about:** the DEGRADER ARCHITECTURE, not the target
- **held by (5):** RT-AF3-INTERFACE, RT-ANDGATE, RT-DEGRADER, RT-GLUE, RT-UBIQ-SELECTIVE
- **retired by route (24):** RT-ASO, RT-ATR-ASSESS, RT-B7H3, RT-CARFILZOMIB, RT-CART-SURFACE, RT-COVALENT-PROBE, RT-CRISPR-CAS13, RT-FAP-RLT, RT-HDAC-BET, RT-ICI-TKI, RT-JUNCTION-NEOANTIGEN, RT-MONOVALENT, RT-PPARG-DOWNSTREAM, RT-PRAME-IMMTAC, RT-RIBOZYME, RT-SSTR2, RT-SYNLETH-DEP, RT-SYNPROMOTER, RT-TCIP, RT-TCR-IMMTAC, RT-TCRT-CTA, RT-TRABECTEDIN, RT-TRABECTEDIN-PPARG, RT-VACCINE
- **retired by technology:** TECH-COFOLD-ASSEMBLY, TECH-E3-RECRUITER-STRUCTURE, TECH-OBSERVED-CRL
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-COFOLD-ASSEMBLY` | `partially_landed` | 2026H2 | **2027** | 2028 | `moderate` | `evidence_based` |
  | `TECH-E3-RECRUITER-STRUCTURE` | `absent` | 2027 | **2028** | 2030 | `low` | `speculative` |
  | `TECH-OBSERVED-CRL` | `absent` | 2027 | **2028** | beyond-2031 | `low` | `speculative` |

- **owner:** `research/manuscripts/nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language`

### BLK-INDUCED-COMPLEX

**An induced ternary/bivalent complex is still required (a second protein must be placed)**

- **kind:** `requires_better_structure_prediction`
- **a statement about:** the same generation problem as the degrader, with a different second terminus
- **held by (3):** RT-AF3-INTERFACE, RT-RIPTAC, RT-TCIP
- **retired by route (1):** RT-MONOVALENT
- **retired by technology:** TECH-COFOLD-ASSEMBLY
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-COFOLD-ASSEMBLY` | `partially_landed` | 2026H2 | **2027** | 2028 | `moderate` | `evidence_based` |

- **owner:** `research/manuscripts/occupancy/nr4a3-monovalent-pocket-route.md#1--the-route-stated-precisely--and-the-split-that-decides-it`

### BLK-UNSIZED-REQUIREMENT

**The selectivity requirement is now STATED for all three routes, and three of its inputs are unmeasured dose-responses that only a bench produces**

- **kind:** `requires_wet_lab`
- **a statement about:** an unmeasured input to a specification that now exists — no longer an absent specification
- **held by (3):** RT-ASYMMETRIC, RT-MONOVALENT, RT-TCIP
- **retired by route (0):** —
- **⭐ retired by an action we can take:** Obtain the three dose-responses named as MISSING-1, MISSING-2 and MISSING-4 in selectivity-requirement-sizing.md. Until then the thresholds stay as stated forms with an explicit range and no upper bound. ⛔ NOT retired by any computation: a genotype bounds developmental, complete, lifelong loss and cannot be inverted into an adult tolerated occupancy, and no in-silico instrument produces an occupancy-to-output transfer function.
- **evidence:** research/manuscripts/degrader/selectivity-requirement-sizing.md#22--what-cannot-be-sized-for-this-route-and-the-named-missing-inputs / research/manuscripts/degrader/selectivity-requirement-sizing.md#43--req-asym-3--the-defect-a-scalar-creates-stated-so-it-can-be-checked / research/modalities/nr4a2-sparing-bound.json
- **when it could lift:** **not forecast** — retired by an action we can take, not by an advance we wait for. The action is the row above.
- **owner:** `research/manuscripts/degrader/selectivity-requirement-sizing.md#5--the-requirement-register-in-one-checkable-table`

### BLK-VECTOR-DELIVERY

**Vector delivery (gene-therapy payload into a solid tumour)**

- **kind:** `requires_future_technology`
- **a statement about:** engineering, distinct from oligonucleotide delivery
- **held by (3):** RT-CRISPR-CAS13, RT-RIBOZYME, RT-SYNPROMOTER
- **retired by route (0):** —
- **retired by technology:** TECH-VECTOR-DELIVERY
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-VECTOR-DELIVERY` | `absent` | 2028 | **2030** | beyond-2031 | `low` | `speculative` |

- **owner:** `research/manuscripts/program/emc-post-degrader-options.md#routes-813--why-each-sits-in-tier-3`

### BLK-REACH-CATEGORICAL

**The categorical (covalent) window at C397 does not survive the E3-arm-free reach enumeration on the conservative convention**

- **kind:** `scientific_uncertainty`
- **a statement about:** geometry at one opened target frame — it can refute a route, it cannot license one
- **held by (2):** RT-COVALENT-PROBE, RT-MONOVALENT
- **retired by route (0):** —
- **retired by technology:** TECH-EXPOSURE-CRITERION
- **⭐ retired by an action we can take:** Re-run the reach enumeration under a criterion that passes its own positive control, and report the result as a rank rather than a verdict until one exists. $0.
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-EXPOSURE-CRITERION` | `absent` | 2026H2 | **2027H2** | 2029 | `low` | `extrapolated` |

- **owner:** `research/manuscripts/occupancy/nr4a3-monovalent-pocket-route.md#3--the-0-test-built-run-and-it-came-back-against-the-route`

### BLK-DELIVERY

**SYSTEMIC, antigen-dependent tumour delivery of an oligonucleotide or a vector — NOT delivery as such**

- **kind:** `requires_future_technology`
- **a statement about:** engineering, not biology; not in-silico-solvable today. ⛔ RESCOPED 2026-08-12, and the rescope is a correction rather than a softening. Superseded, retained: "Tumour delivery of an oligonucleotide or a vector", unqualified. As written this blocker took the hardest of three delivery routes and applied its requirement to the whole modality, and TECH-OLIGO-DELIVERY — the only thing that retires it — is defined in systemic terms ("a conjugate, tumour-penetrating peptide or ligand-targeted lipid nanoparticle — OR a characterised EMC-enriched surface antigen"). But the manuscript this blocker is owned by lists local/intratumoural administration FIRST in its own §3c, explicitly because it needs no EMC surface marker, and §3c-bis adds inhaled/pulmonary administration on the same footing. So an antigen the tumour-tissue data has refused (aso-delivery-antigen.json) was gating two routes that never required it. What the blocker still correctly holds: the systemic receptor-targeted route (AOC, ligand-targeted nanoparticle), which genuinely does wait on a named EMC antigen or a soft-tissue-sarcoma conjugate. What it must NOT be read as holding: that no delivery route for this modality can be attempted, or that the §4 wet-lab experiment waits on any of this — it does not, and a fusion-ASO that cannot silence the fusion in an EMC cell is not worth delivering by any route.
- **held by (1):** RT-ASO
- **retired by route (0):** —
- **retired by technology:** TECH-OLIGO-DELIVERY
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-OLIGO-DELIVERY` | `early_signals` | 2027H2 | **2029** | beyond-2031 | `low` | `extrapolated` |

- **owner:** `research/manuscripts/aso/fusion-junction-aso-working-record.md#3c-bis-delivery-is-three-routes-with-different-requirements-not-one-gate--and-only-one-of-them-needs-the-antigen-2026-08-12`

### BLK-ENDPOINT-MD

**Endpoint-MD selectivity readout (E1) returns null**

- **kind:** `no_known_assay`
- **a statement about:** an endpoint-MD instrument, not the target
- **held by (1):** RT-DEGRADER
- **retired by route (0):** —
- **retired by technology:** TECH-E1-POWERED
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-E1-POWERED` | `absent` | 2027H2 | **2029** | beyond-2031 | `low` | `speculative` |

- **owner:** `research/manuscripts/nr4a3-program-map.md#-gate-failed--the-smarca24-sensitivity-control-returns-null-on-an-adequately-powered-design-2026-08-02-1042-pm-et`

### BLK-FUNCTIONAL-ACTIONABILITY

**Is the LBD a FUNCTIONAL handle in the chimera, whose other end is a strong independent activator?**

- **kind:** `requires_wet_lab`
- **a statement about:** a functional cell assay nobody has run; not covered by the delegated dTAG test
- **held by (1):** RT-MONOVALENT
- **retired by route (1):** RT-COVALENT-PROBE
- **retired by technology:** TECH-CLOUD-WET-LAB, TECH-EMC-MODEL-ACCESS
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-CLOUD-WET-LAB` | `early_signals` | 2027H2 | **2029** | beyond-2031 | `low` | `extrapolated` |
  | `TECH-EMC-MODEL-ACCESS` | `absent` | 2027H2 | **2029** | beyond-2031 | `low` | `speculative` |

- **owner:** `research/manuscripts/occupancy/nr4a3-monovalent-pocket-route.md#2--the-crux-is-the-pocket-functionally-actionable--and-is-it-actionable-in-the-fusion`

### BLK-PARALOGUE-CONTROL

**The paralogue-discrimination positive control (NR-V04) is discordant**

- **kind:** `no_known_assay`
- **a statement about:** a positive control for paralogue discrimination
- **held by (1):** RT-DEGRADER
- **retired by route (0):** —
- **retired by technology:** TECH-NONCOVALENT-PARALOGUE-CONTROL
- **when it could lift:**

  | via | state | optimistic | **expected** | conservative | band confidence | basis (of the STATE) |
  |---|---|---|---|---|---|---|
  | `TECH-NONCOVALENT-PARALOGUE-CONTROL` | `absent` | 2027 | **2028** | beyond-2031 | `low` | `speculative` |

- **owner:** `research/manuscripts/nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language`

### BLK-REGISTRY-DUA

**Population cancer-registry microdata (SEER, NCDB) needs a signed data-use agreement**

- **kind:** `requires_authorization`
- **a statement about:** an access condition on a public dataset, not a scientific limit
- **held by (1):** RT-POPULATION-REGISTRY
- **retired by route (0):** —
- **⭐ retired by an action we can take:** An action only trimcrae can take: register for SEER research data and sign the agreement. ⚠ DO NOT DO THIS FIRST. The prior question is whether a SEER cohort keyed on ICD-O-3 9231/3 is an EMC cohort at all, and it is measured in emc-care-delivery-evidence.json -> icd_o_9231_3: two published SEER studies read that one morphology code as two mutually incompatible diseases. Access bought before that split is quantified buys a contaminated denominator.
- **evidence:** research/modalities/emc-care-delivery-evidence.json
- **when it could lift:** **on request** — this is waiting on a person, not a capability. No forecast applies, and it is the cheapest row in the register to retire.
- **owner:** `systems/graph/blockers.json`

### BLK-SELECTIVITY-CONTROL-UNAUTHORIZED

**The program's only binary selectivity known-answer control is built and staged and has never been run**

- **kind:** `requires_authorization`
- **a statement about:** a decision, not a capability and not the target -- nothing failed and nothing is missing
- **held by (1):** RT-DEGRADER
- **retired by route (0):** —
- **⭐ retired by an action we can take:** Ask for the decision. This blocker is cheaper to retire than any other in the register and it gates the one control that would tell the program whether its central quantitative claim is measurable at all.
- **evidence:** The instrument is registered with no result key: built and staged, never completed. / It is the highest-fan-out item in the portfolio that costs a conversation rather than a capability.
- **when it could lift:** **on request** — this is waiting on a person, not a capability. No forecast applies, and it is the cheapest row in the register to retire.
- **owner:** `research/manuscripts/nr4a3-program-map.md#31--the-instrument-table`

### BLK-TCIP-INTERFACE-FLOOR

**How much induced interface a transcriptional CIP needs is unsized, and the degrader-derived floor it inherits inverts the route's headline result when ablated**

- **kind:** `insufficient_data`
- **a statement about:** a parameter inherited from a different modality, whose calibration constant is a property of the recruited partner's mechanism
- **held by (1):** RT-TCIP
- **retired by route (0):** —
- **⭐ retired by an action we can take:** Find, for ANY chemically-induced transcriptional-proximity system, a relationship between a CHARACTERISED induced interface (size, cooperativity, or induced-complex residence time) and transcriptional output — MISSING-3. ⛔ Measured 2026-08-07 at $0 by reading the committed full text of the route's own motivating source on the literature-cache branch: `cooperativ*` 0 occurrences, `linker` 0, `contact residue` 0, `interface` only inside a reference title, and no structure of the induced complex. That source characterises the ternary complex functionally and not structurally, so it does not supply the input. Supporting Information was not in the cache and is the one place left to look before this escalates to requires_wet_lab. Until then REQ-TCIP-2 (report at both floors, assert only what holds at both) is the route's operative requirement.
- **evidence:** research/modalities/nr4a3-tcip-route-memo.md#4---the-finding-the-size-penalty-is-a-degraders-interface-floor-not-steric-bulk / research/modalities/nr4a3-tcip-reach.json / research/manuscripts/degrader/selectivity-requirement-sizing.md#31--req-tcip-1--the-induced-interface-floor--cannot-be-sized-today
- **when it could lift:** **not forecast** — retired by an action we can take, not by an advance we wait for. The action is the row above.
- **owner:** `research/manuscripts/degrader/selectivity-requirement-sizing.md#31--req-tcip-1--the-induced-interface-floor--cannot-be-sized-today`

[← L0](../L0-ecosystem.md)
