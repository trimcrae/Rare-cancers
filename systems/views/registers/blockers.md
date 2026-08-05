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
| `insufficient_data` | 2 | no |
| `no_known_assay` | 2 | no |
| `requires_authorization` | 1 | no |
| `requires_better_simulation_accuracy` | 1 | no |
| `requires_better_structure_prediction` | 2 | no |
| `requires_external_collaboration` | 1 | no |
| `requires_future_technology` | 2 | no |
| `requires_wet_lab` | 2 | no |
| `scientific_uncertainty` | 2 | no |

## By fan-out — the portfolio's shape

| blocker | kind | routes held | routes that retire it | what would retire it |
|---|---|---:|---:|---|
| **BLK-NO-EMC-DATA**<br/>EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRIS | `insufficient_data` | 15 | 0 | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |
| **BLK-NOT-FUSION-SELECTIVE**<br/>The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half) | `fundamental_biological_limit` | 9 | 7 | **permanent — nothing** |
| **BLK-PARALOGUE-DDG**<br/>The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT) | `requires_better_simulation_accuracy` | 7 | 25 | `TECH-FE-CRYPTIC-POCKET` |
| **BLK-R4-BINDS**<br/>R4 — nothing is known to bind the cryptic pocket at all | `requires_wet_lab` | 7 | 4 | `TECH-EMC-MODEL-ACCESS` |
| **BLK-NO-WET-LAB**<br/>No wet lab and no collaborator — an ask needs a self-interested taker before its size matt | `requires_external_collaboration` | 6 | 1 | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-TERNARY-GEOMETRY**<br/>Ternary geometry — assembly, E3, exit vector, ubiquitin transfer | `requires_better_structure_prediction` | 5 | 24 | `TECH-COFOLD-ASSEMBLY`, `TECH-E3-RECRUITER-STRUCTURE`, `TECH-OBSERVED-CRL` |
| **BLK-ANTIGEN-COLD**<br/>EMC is antigen-cold, and the fusion junction is a weak peptide-HLA | `fundamental_biological_limit` | 5 | 0 | **permanent — nothing** |
| **BLK-VECTOR-DELIVERY**<br/>Vector delivery (gene-therapy payload into a solid tumour) | `requires_future_technology` | 3 | 0 | `TECH-VECTOR-DELIVERY` |
| **BLK-REACH-CATEGORICAL**<br/>The categorical (covalent) window at C397 does not survive the E3-arm-free reach enumerati | `scientific_uncertainty` | 2 | 0 | `TECH-EXPOSURE-CRITERION` |
| **BLK-INDUCED-COMPLEX**<br/>An induced ternary/bivalent complex is still required (a second protein must be placed) | `requires_better_structure_prediction` | 2 | 1 | `TECH-COFOLD-ASSEMBLY` |
| **BLK-ENDPOINT-MD**<br/>Endpoint-MD selectivity readout (E1) returns null | `no_known_assay` | 1 | 0 | `TECH-E1-POWERED` |
| **BLK-PARALOGUE-CONTROL**<br/>The paralogue-discrimination positive control (NR-V04) is discordant | `no_known_assay` | 1 | 0 | `TECH-NONCOVALENT-PARALOGUE-CONTROL` |
| **BLK-FUNCTIONAL-ACTIONABILITY**<br/>Is the LBD a FUNCTIONAL handle in the chimera, whose other end is a strong independent act | `requires_wet_lab` | 1 | 1 | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-DELIVERY**<br/>Tumour delivery of an oligonucleotide or a vector | `requires_future_technology` | 1 | 0 | `TECH-OLIGO-DELIVERY` |
| **BLK-CLASS-INHERITANCE**<br/>Class inheritance, not an EMC measurement — no NR4A3 fusion has been tested for the phenot | `insufficient_data` | 1 | 0 | `TECH-VIRTUAL-CELL` |
| **BLK-UNSIZED-REQUIREMENT**<br/>Nobody has stated how much selectivity the route would need, so 'the requirement is smalle | `scientific_uncertainty` | 1 | 0 | State the selectivity requirement the route would have to meet, with its basis. This is reasoning, not a capability: nob… |
| **BLK-SELECTIVITY-CONTROL-UNAUTHORIZED**<br/>The program's only binary selectivity known-answer control is built and staged and has nev | `requires_authorization` | 1 | 0 | Ask for the decision. This blocker is cheaper to retire than any other in the register and it gates the one control that… |

## Detail

### BLK-NO-EMC-DATA

**EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)**

- **kind:** `insufficient_data`
- **a statement about:** data availability — the repo-wide rate-limiter, not any one route
- **held by (15):** RT-ASO-ASK, RT-ATR-ASSESS, RT-ATR-PANEL, RT-B7H3, RT-CARFILZOMIB, RT-CART-SURFACE, RT-FAP-RLT, RT-ICI-TKI, RT-PPARG-DOWNSTREAM, RT-PRAME-IMMTAC, RT-SSTR2, RT-SYNLETH-DEP, RT-TCRT-CTA, RT-TRABECTEDIN, RT-TRABECTEDIN-PPARG
- **retired by route (0):** —
- **retired by technology:** TECH-EMC-EXPRESSION-DATA, TECH-VIRTUAL-CELL
- **owner:** `research/IDEAS.mdNone`

### BLK-NOT-FUSION-SELECTIVE

**The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)**

- **kind:** `fundamental_biological_limit` · **PERMANENT**
- **a statement about:** what the molecule can and cannot tell apart
- **held by (9):** RT-B7H3, RT-CART-SURFACE, RT-DEGRADER, RT-EWSR1-PROTEIN, RT-FAP-RLT, RT-FET-LC-LIGAND, RT-HDAC-BET, RT-MONOVALENT, RT-PRAME-IMMTAC
- **retired by route (7):** RT-ASO, RT-ICI-TKI, RT-JUNCTION-NEOANTIGEN, RT-PANNR4A-EXVIVO, RT-RIBOZYME, RT-SSTR2, RT-TCR-IMMTAC
- **owner:** `research/manuscripts/target-route-options.md#3--what-genuinely-sidesteps-the-paralogue-problem-and-what-merely-relocates-it`

### BLK-PARALOGUE-DDG

**The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)**

- **kind:** `requires_better_simulation_accuracy`
- **a statement about:** a free-energy difference between two similar pockets, which this program has failed to measure four separate ways
- **held by (7):** RT-ANDGATE, RT-ASYMMETRIC, RT-DBD, RT-DEGRADER, RT-GLUE, RT-RIPTAC, RT-TCIP
- **retired by route (25):** RT-ASO, RT-ATR-ASSESS, RT-B7H3, RT-CARFILZOMIB, RT-CART-SURFACE, RT-COVALENT-PROBE, RT-CRISPR-CAS13, RT-EWSR1-PROTEIN, RT-FAP-RLT, RT-FET-LC-LIGAND, RT-HDAC-BET, RT-ICI-TKI, RT-JUNCTION-NEOANTIGEN, RT-PANNR4A-EXVIVO, RT-PPARG-DOWNSTREAM, RT-PRAME-IMMTAC, RT-RIBOZYME, RT-SSTR2, RT-SYNLETH-DEP, RT-SYNPROMOTER, RT-TCR-IMMTAC, RT-TCRT-CTA, RT-TRABECTEDIN, RT-TRABECTEDIN-PPARG, RT-VACCINE
- **retired by technology:** TECH-FE-CRYPTIC-POCKET
- **owner:** `research/manuscripts/nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged`

### BLK-R4-BINDS

**R4 — nothing is known to bind the cryptic pocket at all**

- **kind:** `requires_wet_lab`
- **a statement about:** an unanswered requirement that needs a bench
- **held by (7):** RT-ANDGATE, RT-COVALENT-PROBE, RT-DEGRADER, RT-GLUE, RT-MONOVALENT, RT-RIPTAC, RT-TCIP
- **retired by route (4):** RT-ATR-ASSESS, RT-PPARG-DOWNSTREAM, RT-SYNLETH-DEP, RT-TRABECTEDIN-PPARG
- **retired by technology:** TECH-EMC-MODEL-ACCESS
- **owner:** `research/manuscripts/nr4a3-program-map.md#32--the-rv-coverage-matrix--where-the-holes-are`

### BLK-NO-WET-LAB

**No wet lab and no collaborator — an ask needs a self-interested taker before its size matters**

- **kind:** `requires_external_collaboration`
- **a statement about:** the operating regime, not any route's science
- **held by (6):** RT-ASO-ASK, RT-ATR-PANEL, RT-COVALENT-PROBE, RT-SSTR2, RT-TCIP, RT-TRABECTEDIN-PPARG
- **retired by route (1):** RT-METHODS-PAPER
- **retired by technology:** TECH-CLOUD-WET-LAB, TECH-EMC-MODEL-ACCESS
- **owner:** `research/manuscripts/what-a-civilian-can-buy.mdNone`

### BLK-TERNARY-GEOMETRY

**Ternary geometry — assembly, E3, exit vector, ubiquitin transfer**

- **kind:** `requires_better_structure_prediction`
- **a statement about:** the DEGRADER ARCHITECTURE, not the target
- **held by (5):** RT-AF3-INTERFACE, RT-ANDGATE, RT-DEGRADER, RT-GLUE, RT-UBIQ-SELECTIVE
- **retired by route (24):** RT-ASO, RT-ATR-ASSESS, RT-B7H3, RT-CARFILZOMIB, RT-CART-SURFACE, RT-COVALENT-PROBE, RT-CRISPR-CAS13, RT-FAP-RLT, RT-HDAC-BET, RT-ICI-TKI, RT-JUNCTION-NEOANTIGEN, RT-MONOVALENT, RT-PPARG-DOWNSTREAM, RT-PRAME-IMMTAC, RT-RIBOZYME, RT-SSTR2, RT-SYNLETH-DEP, RT-SYNPROMOTER, RT-TCIP, RT-TCR-IMMTAC, RT-TCRT-CTA, RT-TRABECTEDIN, RT-TRABECTEDIN-PPARG, RT-VACCINE
- **retired by technology:** TECH-COFOLD-ASSEMBLY, TECH-E3-RECRUITER-STRUCTURE, TECH-OBSERVED-CRL
- **owner:** `research/manuscripts/nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language`

### BLK-ANTIGEN-COLD

**EMC is antigen-cold, and the fusion junction is a weak peptide-HLA**

- **kind:** `fundamental_biological_limit` · **PERMANENT**
- **a statement about:** the tumour's immunogenicity, shared by every antigen-directed route
- **held by (5):** RT-CART-SURFACE, RT-JUNCTION-NEOANTIGEN, RT-TCR-IMMTAC, RT-TCRT-CTA, RT-VACCINE
- **retired by route (0):** —
- **owner:** `research/manuscripts/immunotherapy-options-emc.mdNone`

### BLK-VECTOR-DELIVERY

**Vector delivery (gene-therapy payload into a solid tumour)**

- **kind:** `requires_future_technology`
- **a statement about:** engineering, distinct from oligonucleotide delivery
- **held by (3):** RT-CRISPR-CAS13, RT-RIBOZYME, RT-SYNPROMOTER
- **retired by route (0):** —
- **retired by technology:** TECH-VECTOR-DELIVERY
- **owner:** `research/manuscripts/emc-post-degrader-options.md#routes-813--why-each-sits-in-tier-3`

### BLK-REACH-CATEGORICAL

**The categorical (covalent) window at C397 does not survive the E3-arm-free reach enumeration on the conservative convention**

- **kind:** `scientific_uncertainty`
- **a statement about:** geometry at one opened target frame — it can refute a route, it cannot license one
- **held by (2):** RT-COVALENT-PROBE, RT-MONOVALENT
- **retired by route (0):** —
- **retired by technology:** TECH-EXPOSURE-CRITERION
- **⭐ retired by an action we can take:** Re-run the reach enumeration under a criterion that passes its own positive control, and report the result as a rank rather than a verdict until one exists. $0.
- **owner:** `research/manuscripts/nr4a3-monovalent-pocket-route.md#3--the-0-test-built-run-and-it-came-back-against-the-route`

### BLK-INDUCED-COMPLEX

**An induced ternary/bivalent complex is still required (a second protein must be placed)**

- **kind:** `requires_better_structure_prediction`
- **a statement about:** the same generation problem as the degrader, with a different second terminus
- **held by (2):** RT-RIPTAC, RT-TCIP
- **retired by route (1):** RT-MONOVALENT
- **retired by technology:** TECH-COFOLD-ASSEMBLY
- **owner:** `research/manuscripts/nr4a3-monovalent-pocket-route.md#1--the-route-stated-precisely--and-the-split-that-decides-it`

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

### BLK-CLASS-INHERITANCE

**Class inheritance, not an EMC measurement — no NR4A3 fusion has been tested for the phenotype**

- **kind:** `insufficient_data`
- **a statement about:** the strength of a transfer argument
- **held by (1):** RT-ATR-ASSESS
- **retired by route (0):** —
- **retired by technology:** TECH-VIRTUAL-CELL
- **⭐ retired by an action we can take:** State plainly, wherever the transfer argument is used, that no NR4A3 fusion has been tested for the phenotype. The blocker cannot be retired by us, but its misreading can. $0.
- **owner:** `research/manuscripts/emc-post-degrader-options.md#route-1---atr-inhibitor-synthetic-lethality-emc-inherits-a-class-vulnerability-it-has-never-been-tested-for`

### BLK-UNSIZED-REQUIREMENT

**Nobody has stated how much selectivity the route would need, so 'the requirement is smaller' is not a claim this repo can make**

- **kind:** `scientific_uncertainty`
- **a statement about:** an absent specification, not a measured shortfall
- **held by (1):** RT-MONOVALENT
- **retired by route (0):** —
- **⭐ retired by an action we can take:** State the selectivity requirement the route would have to meet, with its basis. This is reasoning, not a capability: nobody has written the specification down, so nothing can be shown to meet or miss it. $0.
- **owner:** `research/manuscripts/nr4a3-monovalent-pocket-route.md#4--effect-on-the-paralogue-requirement--reshapes-into-a-requirement-of-unquantified-size`

### BLK-SELECTIVITY-CONTROL-UNAUTHORIZED

**The program's only binary selectivity known-answer control is built and staged and has never been run**

- **kind:** `requires_authorization`
- **a statement about:** a decision, not a capability and not the target -- nothing failed and nothing is missing
- **held by (1):** RT-DEGRADER
- **retired by route (0):** —
- **⭐ retired by an action we can take:** Ask for the decision. This blocker is cheaper to retire than any other in the register and it gates the one control that would tell the program whether its central quantitative claim is measurable at all.
- **evidence:** The instrument is registered with no result key: built and staged, never completed. / It is the highest-fan-out item in the portfolio that costs a conversation rather than a capability.
- **owner:** `research/manuscripts/nr4a3-program-map.md#31--the-instrument-table`

[← L0](../L0-ecosystem.md)
