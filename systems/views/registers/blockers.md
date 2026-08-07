---
id: DOC-VIEW-BLOCKERS
title: Blocker register
level: cross-cutting
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Every reason work is stalled, typed, ordered by how much of the portfolio it holds down.
scope: "All blockers. Vocabulary and selection rules: systems/taxonomy/blockers.md"
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
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
| `insufficient_data` | 3 | no |
| `no_known_assay` | 2 | no |
| `requires_authorization` | 1 | no |
| `requires_better_simulation_accuracy` | 1 | no |
| `requires_better_structure_prediction` | 2 | no |
| `requires_external_collaboration` | 1 | no |
| `requires_future_technology` | 2 | no |
| `requires_wet_lab` | 3 | no |
| `scientific_uncertainty` | 1 | no |

## By fan-out — the portfolio's shape

| blocker | kind | routes held | routes that retire it | what would retire it |
|---|---|---:|---:|---|
| **BLK-NO-EMC-DATA**<br/>EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRIS | `insufficient_data` | 19 | 0 | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |
| **BLK-NOT-FUSION-SELECTIVE**<br/>The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half) | `fundamental_biological_limit` | 14 | 8 | **permanent — nothing** |
| **BLK-PARALOGUE-DDG**<br/>The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT) | `requires_better_simulation_accuracy` | 9 | 24 | `TECH-FE-CRYPTIC-POCKET` |
| **BLK-NO-WET-LAB**<br/>No wet lab and no collaborator — an ask needs a self-interested taker before its size matt | `requires_external_collaboration` | 9 | 2 | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-R4-BINDS**<br/>R4 — nothing is known to bind the cryptic pocket at all | `requires_wet_lab` | 8 | 4 | `TECH-EMC-MODEL-ACCESS` |
| **BLK-ANTIGEN-COLD**<br/>EMC is antigen-cold, and the fusion junction is a weak peptide-HLA | `fundamental_biological_limit` | 8 | 0 | **permanent — nothing** |
| **BLK-TERNARY-GEOMETRY**<br/>Ternary geometry — assembly, E3, exit vector, ubiquitin transfer | `requires_better_structure_prediction` | 5 | 24 | `TECH-COFOLD-ASSEMBLY`, `TECH-E3-RECRUITER-STRUCTURE`, `TECH-OBSERVED-CRL` |
| **BLK-CLASS-INHERITANCE**<br/>Class inheritance, not an EMC measurement — no NR4A3 fusion has been tested for the phenot | `insufficient_data` | 4 | 0 | `TECH-VIRTUAL-CELL` |
| **BLK-VECTOR-DELIVERY**<br/>Vector delivery (gene-therapy payload into a solid tumour) | `requires_future_technology` | 3 | 0 | `TECH-VECTOR-DELIVERY` |
| **BLK-INDUCED-COMPLEX**<br/>An induced ternary/bivalent complex is still required (a second protein must be placed) | `requires_better_structure_prediction` | 3 | 1 | `TECH-COFOLD-ASSEMBLY` |
| **BLK-UNSIZED-REQUIREMENT**<br/>The selectivity requirement is now STATED for all three routes, and three of its inputs ar | `requires_wet_lab` | 3 | 0 | Obtain the three dose-responses named as MISSING-1, MISSING-2 and MISSING-4 in selectivity-requirement-sizing.md. Until … |
| **BLK-REACH-CATEGORICAL**<br/>The categorical (covalent) window at C397 does not survive the E3-arm-free reach enumerati | `scientific_uncertainty` | 2 | 0 | `TECH-EXPOSURE-CRITERION` |
| **BLK-ENDPOINT-MD**<br/>Endpoint-MD selectivity readout (E1) returns null | `no_known_assay` | 1 | 0 | `TECH-E1-POWERED` |
| **BLK-PARALOGUE-CONTROL**<br/>The paralogue-discrimination positive control (NR-V04) is discordant | `no_known_assay` | 1 | 0 | `TECH-NONCOVALENT-PARALOGUE-CONTROL` |
| **BLK-FUNCTIONAL-ACTIONABILITY**<br/>Is the LBD a FUNCTIONAL handle in the chimera, whose other end is a strong independent act | `requires_wet_lab` | 1 | 1 | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-DELIVERY**<br/>Tumour delivery of an oligonucleotide or a vector | `requires_future_technology` | 1 | 0 | `TECH-OLIGO-DELIVERY` |
| **BLK-SELECTIVITY-CONTROL-UNAUTHORIZED**<br/>The program's only binary selectivity known-answer control is built and staged and has nev | `requires_authorization` | 1 | 0 | Ask for the decision. This blocker is cheaper to retire than any other in the register and it gates the one control that… |
| **BLK-TCIP-INTERFACE-FLOOR**<br/>How much induced interface a transcriptional CIP needs is unsized, and the degrader-derive | `insufficient_data` | 1 | 0 | Find, for ANY chemically-induced transcriptional-proximity system, a relationship between a CHARACTERISED induced interf… |

## Detail

### BLK-NO-EMC-DATA

**EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)**

- **kind:** `insufficient_data`
- **a statement about:** data availability — the repo-wide rate-limiter, not any one route
- **held by (19):** RT-6MP, RT-ASO-ASK, RT-ATR-ASSESS, RT-ATR-PANEL, RT-B7H3, RT-CARFILZOMIB, RT-CART-SURFACE, RT-FAP-RLT, RT-ICI-TKI, RT-JUNCTION-NEOANTIGEN, RT-PARTNER-STRAT, RT-PPARG-DOWNSTREAM, RT-PRAME-IMMTAC, RT-SSTR2, RT-SYNLETH-DEP, RT-SYNPROMOTER, RT-TCRT-CTA, RT-TRABECTEDIN, RT-TRABECTEDIN-PPARG
- **retired by route (0):** —
- **retired by technology:** TECH-EMC-EXPRESSION-DATA, TECH-VIRTUAL-CELL
- **owner:** `research/IDEAS.mdNone`

### BLK-NOT-FUSION-SELECTIVE

**The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)**

- **kind:** `fundamental_biological_limit` · **PERMANENT**
- **a statement about:** what the molecule can and cannot tell apart
- **held by (14):** RT-6MP, RT-B7H3, RT-CART-SURFACE, RT-COVALENT-PROBE, RT-DBD, RT-DEGRADER, RT-EWSR1-PROTEIN, RT-FET-LC-LIGAND, RT-GLUE, RT-MONOVALENT, RT-PRAME-IMMTAC, RT-RIPTAC, RT-SYNPROMOTER, RT-UBIQ-SELECTIVE
- **retired by route (8):** RT-ASO, RT-FAP-RLT, RT-ICI-TKI, RT-JUNCTION-NEOANTIGEN, RT-PANNR4A-EXVIVO, RT-RIBOZYME, RT-SSTR2, RT-TCR-IMMTAC
- **owner:** `research/manuscripts/target-route-options.md#3--what-genuinely-sidesteps-the-paralogue-problem-and-what-merely-relocates-it`

### BLK-PARALOGUE-DDG

**The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)**

- **kind:** `requires_better_simulation_accuracy`
- **a statement about:** a free-energy difference between two similar pockets, which this program has failed to measure four separate ways
- **held by (9):** RT-ANDGATE, RT-ASYMMETRIC, RT-COVALENT-PROBE, RT-DBD, RT-DEGRADER, RT-GLUE, RT-MONOVALENT, RT-RIPTAC, RT-TCIP
- **retired by route (24):** RT-ASO, RT-ATR-ASSESS, RT-B7H3, RT-CARFILZOMIB, RT-CART-SURFACE, RT-CRISPR-CAS13, RT-EWSR1-PROTEIN, RT-FAP-RLT, RT-FET-LC-LIGAND, RT-HDAC-BET, RT-ICI-TKI, RT-JUNCTION-NEOANTIGEN, RT-PANNR4A-EXVIVO, RT-PPARG-DOWNSTREAM, RT-PRAME-IMMTAC, RT-RIBOZYME, RT-SSTR2, RT-SYNLETH-DEP, RT-SYNPROMOTER, RT-TCR-IMMTAC, RT-TCRT-CTA, RT-TRABECTEDIN, RT-TRABECTEDIN-PPARG, RT-VACCINE
- **retired by technology:** TECH-FE-CRYPTIC-POCKET
- **owner:** `research/manuscripts/nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged`

### BLK-NO-WET-LAB

**No wet lab and no collaborator — an ask needs a self-interested taker before its size matters**

- **kind:** `requires_external_collaboration`
- **a statement about:** the operating regime, not any route's science
- **held by (9):** RT-ASO-ASK, RT-ATR-PANEL, RT-COVALENT-PROBE, RT-FAP-RLT, RT-RIPTAC, RT-SSTR2, RT-SYNLETH-DEP, RT-TCIP, RT-TRABECTEDIN-PPARG
- **retired by route (2):** RT-ENDPOINT-CHOICE, RT-METHODS-PAPER
- **retired by technology:** TECH-CLOUD-WET-LAB, TECH-EMC-MODEL-ACCESS
- **owner:** `research/manuscripts/what-a-civilian-can-buy.mdNone`

### BLK-R4-BINDS

**R4 — nothing is known to bind the cryptic pocket at all**

- **kind:** `requires_wet_lab`
- **a statement about:** an unanswered requirement that needs a bench
- **held by (8):** RT-ANDGATE, RT-COVALENT-PROBE, RT-DEGRADER, RT-GLUE, RT-MONOVALENT, RT-RIPTAC, RT-TCIP, RT-UBIQ-SELECTIVE
- **retired by route (4):** RT-ATR-ASSESS, RT-PPARG-DOWNSTREAM, RT-SYNLETH-DEP, RT-TRABECTEDIN-PPARG
- **retired by technology:** TECH-EMC-MODEL-ACCESS
- **owner:** `research/manuscripts/nr4a3-program-map.md#32--the-rv-coverage-matrix--where-the-holes-are`

### BLK-ANTIGEN-COLD

**EMC is antigen-cold, and the fusion junction is a weak peptide-HLA**

- **kind:** `fundamental_biological_limit` · **PERMANENT**
- **a statement about:** the tumour's immunogenicity, shared by every antigen-directed route
- **held by (8):** RT-B7H3, RT-CART-SURFACE, RT-ICI-TKI, RT-JUNCTION-NEOANTIGEN, RT-PRAME-IMMTAC, RT-TCR-IMMTAC, RT-TCRT-CTA, RT-VACCINE
- **retired by route (0):** —
- **owner:** `research/manuscripts/immunotherapy-options-emc.mdNone`

### BLK-TERNARY-GEOMETRY

**Ternary geometry — assembly, E3, exit vector, ubiquitin transfer**

- **kind:** `requires_better_structure_prediction`
- **a statement about:** the DEGRADER ARCHITECTURE, not the target
- **held by (5):** RT-AF3-INTERFACE, RT-ANDGATE, RT-DEGRADER, RT-GLUE, RT-UBIQ-SELECTIVE
- **retired by route (24):** RT-ASO, RT-ATR-ASSESS, RT-B7H3, RT-CARFILZOMIB, RT-CART-SURFACE, RT-COVALENT-PROBE, RT-CRISPR-CAS13, RT-FAP-RLT, RT-HDAC-BET, RT-ICI-TKI, RT-JUNCTION-NEOANTIGEN, RT-MONOVALENT, RT-PPARG-DOWNSTREAM, RT-PRAME-IMMTAC, RT-RIBOZYME, RT-SSTR2, RT-SYNLETH-DEP, RT-SYNPROMOTER, RT-TCIP, RT-TCR-IMMTAC, RT-TCRT-CTA, RT-TRABECTEDIN, RT-TRABECTEDIN-PPARG, RT-VACCINE
- **retired by technology:** TECH-COFOLD-ASSEMBLY, TECH-E3-RECRUITER-STRUCTURE, TECH-OBSERVED-CRL
- **owner:** `research/manuscripts/nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language`

### BLK-CLASS-INHERITANCE

**Class inheritance, not an EMC measurement — no NR4A3 fusion has been tested for the phenotype**

- **kind:** `insufficient_data`
- **a statement about:** the strength of a transfer argument
- **held by (4):** RT-ATR-ASSESS, RT-FAP-RLT, RT-HDAC-BET, RT-SSTR2
- **retired by route (0):** —
- **retired by technology:** TECH-VIRTUAL-CELL
- **⭐ retired by an action we can take:** State plainly, wherever the transfer argument is used, that no NR4A3 fusion has been tested for the phenotype. The blocker cannot be retired by us, but its misreading can. $0.
- **owner:** `research/manuscripts/emc-post-degrader-options.md#route-1---atr-inhibitor-synthetic-lethality-emc-inherits-a-class-vulnerability-it-has-never-been-tested-for`

### BLK-VECTOR-DELIVERY

**Vector delivery (gene-therapy payload into a solid tumour)**

- **kind:** `requires_future_technology`
- **a statement about:** engineering, distinct from oligonucleotide delivery
- **held by (3):** RT-CRISPR-CAS13, RT-RIBOZYME, RT-SYNPROMOTER
- **retired by route (0):** —
- **retired by technology:** TECH-VECTOR-DELIVERY
- **owner:** `research/manuscripts/emc-post-degrader-options.md#routes-813--why-each-sits-in-tier-3`

### BLK-INDUCED-COMPLEX

**An induced ternary/bivalent complex is still required (a second protein must be placed)**

- **kind:** `requires_better_structure_prediction`
- **a statement about:** the same generation problem as the degrader, with a different second terminus
- **held by (3):** RT-AF3-INTERFACE, RT-RIPTAC, RT-TCIP
- **retired by route (1):** RT-MONOVALENT
- **retired by technology:** TECH-COFOLD-ASSEMBLY
- **owner:** `research/manuscripts/nr4a3-monovalent-pocket-route.md#1--the-route-stated-precisely--and-the-split-that-decides-it`

### BLK-UNSIZED-REQUIREMENT

**The selectivity requirement is now STATED for all three routes, and three of its inputs are unmeasured dose-responses that only a bench produces**

- **kind:** `requires_wet_lab`
- **a statement about:** an unmeasured input to a specification that now exists — no longer an absent specification
- **held by (3):** RT-ASYMMETRIC, RT-MONOVALENT, RT-TCIP
- **retired by route (0):** —
- **⭐ retired by an action we can take:** Obtain the three dose-responses named as MISSING-1, MISSING-2 and MISSING-4 in selectivity-requirement-sizing.md. Until then the thresholds stay as stated forms with an explicit range and no upper bound. ⛔ NOT retired by any computation: a genotype bounds developmental, complete, lifelong loss and cannot be inverted into an adult tolerated occupancy, and no in-silico instrument produces an occupancy-to-output transfer function.
- **evidence:** research/manuscripts/selectivity-requirement-sizing.md#22--what-cannot-be-sized-for-this-route-and-the-named-missing-inputs / research/manuscripts/selectivity-requirement-sizing.md#43--req-asym-3--the-defect-a-scalar-creates-stated-so-it-can-be-checked / research/modalities/nr4a2-sparing-bound.json
- **owner:** `research/manuscripts/selectivity-requirement-sizing.md#5--the-requirement-register-in-one-checkable-table`

### BLK-REACH-CATEGORICAL

**The categorical (covalent) window at C397 does not survive the E3-arm-free reach enumeration on the conservative convention**

- **kind:** `scientific_uncertainty`
- **a statement about:** geometry at one opened target frame — it can refute a route, it cannot license one
- **held by (2):** RT-COVALENT-PROBE, RT-MONOVALENT
- **retired by route (0):** —
- **retired by technology:** TECH-EXPOSURE-CRITERION
- **⭐ retired by an action we can take:** Re-run the reach enumeration under a criterion that passes its own positive control, and report the result as a rank rather than a verdict until one exists. $0.
- **owner:** `research/manuscripts/nr4a3-monovalent-pocket-route.md#3--the-0-test-built-run-and-it-came-back-against-the-route`

### BLK-ENDPOINT-MD

**Endpoint-MD selectivity readout (E1) returns null**

- **kind:** `no_known_assay`
- **a statement about:** an endpoint-MD instrument, not the target
- **held by (1):** RT-DEGRADER
- **retired by route (0):** —
- **retired by technology:** TECH-E1-POWERED
- **owner:** `research/manuscripts/nr4a3-program-map.md#-gate-failed--the-smarca24-sensitivity-control-returns-null-on-an-adequately-powered-design-2026-08-02-1042-pm-et`

### BLK-PARALOGUE-CONTROL

**The paralogue-discrimination positive control (NR-V04) is discordant**

- **kind:** `no_known_assay`
- **a statement about:** a positive control for paralogue discrimination
- **held by (1):** RT-DEGRADER
- **retired by route (0):** —
- **retired by technology:** TECH-NONCOVALENT-PARALOGUE-CONTROL
- **owner:** `research/manuscripts/nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language`

### BLK-FUNCTIONAL-ACTIONABILITY

**Is the LBD a FUNCTIONAL handle in the chimera, whose other end is a strong independent activator?**

- **kind:** `requires_wet_lab`
- **a statement about:** a functional cell assay nobody has run; not covered by the delegated dTAG test
- **held by (1):** RT-MONOVALENT
- **retired by route (1):** RT-COVALENT-PROBE
- **retired by technology:** TECH-CLOUD-WET-LAB, TECH-EMC-MODEL-ACCESS
- **owner:** `research/manuscripts/nr4a3-monovalent-pocket-route.md#2--the-crux-is-the-pocket-functionally-actionable--and-is-it-actionable-in-the-fusion`

### BLK-DELIVERY

**Tumour delivery of an oligonucleotide or a vector**

- **kind:** `requires_future_technology`
- **a statement about:** engineering, not biology; not in-silico-solvable today
- **held by (1):** RT-ASO
- **retired by route (0):** —
- **retired by technology:** TECH-OLIGO-DELIVERY
- **owner:** `research/manuscripts/fusion-junction-aso-paper.mdNone`

### BLK-SELECTIVITY-CONTROL-UNAUTHORIZED

**The program's only binary selectivity known-answer control is built and staged and has never been run**

- **kind:** `requires_authorization`
- **a statement about:** a decision, not a capability and not the target -- nothing failed and nothing is missing
- **held by (1):** RT-DEGRADER
- **retired by route (0):** —
- **⭐ retired by an action we can take:** Ask for the decision. This blocker is cheaper to retire than any other in the register and it gates the one control that would tell the program whether its central quantitative claim is measurable at all.
- **evidence:** The instrument is registered with no result key: built and staged, never completed. / It is the highest-fan-out item in the portfolio that costs a conversation rather than a capability.
- **owner:** `research/manuscripts/nr4a3-program-map.md#31--the-instrument-table`

### BLK-TCIP-INTERFACE-FLOOR

**How much induced interface a transcriptional CIP needs is unsized, and the degrader-derived floor it inherits inverts the route's headline result when ablated**

- **kind:** `insufficient_data`
- **a statement about:** a parameter inherited from a different modality, whose calibration constant is a property of the recruited partner's mechanism
- **held by (1):** RT-TCIP
- **retired by route (0):** —
- **⭐ retired by an action we can take:** Find, for ANY chemically-induced transcriptional-proximity system, a relationship between a CHARACTERISED induced interface (size, cooperativity, or induced-complex residence time) and transcriptional output — MISSING-3. ⛔ Measured 2026-08-07 at $0 by reading the committed full text of the route's own motivating source on the literature-cache branch: `cooperativ*` 0 occurrences, `linker` 0, `contact residue` 0, `interface` only inside a reference title, and no structure of the induced complex. That source characterises the ternary complex functionally and not structurally, so it does not supply the input. Supporting Information was not in the cache and is the one place left to look before this escalates to requires_wet_lab. Until then REQ-TCIP-2 (report at both floors, assert only what holds at both) is the route's operative requirement.
- **evidence:** research/modalities/nr4a3-tcip-route-memo.md#4---the-finding-the-size-penalty-is-a-degraders-interface-floor-not-steric-bulk / research/modalities/nr4a3-tcip-reach.json / research/manuscripts/selectivity-requirement-sizing.md#31--req-tcip-1--the-induced-interface-floor--cannot-be-sized-today
- **owner:** `research/manuscripts/selectivity-requirement-sizing.md#31--req-tcip-1--the-induced-interface-floor--cannot-be-sized-today`

[← L0](../L0-ecosystem.md)
