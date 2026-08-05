# The EMC systems map — routes, objects, evidence, instruments, artifacts, claims

> ⛔ **GENERATED FILE — DO NOT EDIT.** Its one home is [`emc-systems-map.json`](./emc-systems-map.json); regenerate with `python3 research/manuscripts/emc_systems_map_check.py --write-view`. CI fails if this file and the registry disagree (CLAUDE.md §1 — a derived view is regenerated, never hand-maintained).
>
> **Role: navigation and integrity, not analysis.** This page grades nothing, re-derives nothing and restates no figure that has a home elsewhere. Every grade cell names the file that owns it; every claim names the artifact field that owns it. To change a grade, edit the owning file — changing it here changes nothing and will be overwritten.
>
> **$0.** No GPU, no rental, no purchase, no contact, no wet lab. No efficacy, potency, safety, therapeutic-window or clinical-readiness claim is made for any route or molecule, and none follows from anything below.

## Why it exists

- One piece of evidence carried under two names. ⛔ SUPERSEDED ATTRIBUTION, RETAINED so it stays quotable and searchable: five repo files cited the NOR-1 druggability result under a wrong author name (a misattribution), always without a PMID, for the paper other places cite correctly as Zaienne et al., ChemMedChem 2022, PMID 35704774. A route was graded while its own supporting evidence sat in another file, unfindable under a name that matches no paper. ✅ The misattribution was measured, corrected and retired on 2026-08-03 — one home in `research/modalities/nr4a3-druggability-reconciliation.md` §5b, pinned by `research/modalities/tests/test_munck_attribution_retired.py`. THIS REGISTRY'S JOB IS THE STRUCTURAL HALF: every name a source travels under resolves to ONE evidence item, so the class of error cannot recur under a new name.
- One object carried under two incompatible definitions: 'the canonical EMC fusion' names a modelled EWSR1 e7 :: NR4A3 e3 construct that is NOT a reported fusion type, and the reported type 2 protein carries 59 extra UTR-encoded residues that fusion_cofold.py's protein-level model does not have.
- One grade applied to two different routes: the covalent probe at C397 and a monovalent reversible pocket modulator fail on OPPOSITE blockers and must never share a row or a demotion.
- A number quoted from an artifact that is a STUB on the branch a reader would open: emc-fet-idr-census.json is a 161-byte 'cannot compute' placeholder on `main` while emc-post-degrader-options.md on `main` prints a full results table out of it.

**Registry contents:** 40 routes · 19 objects · 14 evidence items · 31 instruments · 12 artifacts · 17 claims · 17 blockers · 3 open conflicts.

---

## 1 · Every route, its grade, and where that grade lives

One route, one grade, one owning section. Other files may **point** at a grade; a second assertion is a second home for the same fact and the checker fails on it.

| route | id | grade (as the owner words it) | ⚠ the grade lives HERE | also mentioned in |
|---|---|---|---|---|
| **6-mercaptopurine / AF-1 agonism of the fusion** | `RT-6MP` | ✕ CLOSED 2026-08-03 — 6-MP acts through the AF-1, the domain the fusion replaces | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#2--the-ranked-list) | [`IDEAS.md`](../IDEAS.md) |
| **AF3 on a druggable interface** | `RT-AF3-INTERFACE` | Deferred; method not strategy | [`IDEAS.md`](../IDEAS.md#emc-treatment-discovery--route-status-board-updated-2026-06-21) | — |
| **AND-gate bivalent degrader (avidity coincidence detection)** | `RT-ANDGATE` | ⏸ hold — arm-2 chemistry does not exist | [`fusion-selective-andgate-degrader-paper.md`](fusion-selective-andgate-degrader-paper.md) | [`target-route-options.md`](target-route-options.md) |
| **Fusion-junction ASO / siRNA (the deliverable)** | `RT-ASO` | Tier 1, rank 2 — DELIVERABLE | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#2--the-ranked-list) | [`IDEAS.md`](../IDEAS.md), [`target-route-options.md`](target-route-options.md) |
| **Junction knockdown + parental sparing in EMC lines (the ask behind the ASO)** | `RT-ASO-ASK` | Tier 2, rank 6 — ASK | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#2--the-ranked-list) | — |
| **Asymmetric selectivity — NR4A1-sparing mandatory, NR4A2-sparing best-effort** | `RT-ASYMMETRIC` | ★★ adopt now — free, and it changes the design brief | [`target-route-options.md`](target-route-options.md#route-1--asymmetric-selectivity-nr4a1-sparing-mandatory-nr4a2-sparing-best-effort--pk) | [`nr4a3-program-map.md`](nr4a3-program-map.md), [`IDEAS.md`](../IDEAS.md) |
| **The in-silico ATR vulnerability assessment (the computed half)** | `RT-ATR-ASSESS` | Tier 1, rank 3 — DELIVERABLE | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#2--the-ranked-list) | [`IDEAS.md`](../IDEAS.md) |
| **The ATR-inhibitor cell panel in EMC lines (the ask)** | `RT-ATR-PANEL` | Tier 2, rank 4 — ASK, best W1 in the portfolio | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#2--the-ranked-list) | [`IDEAS.md`](../IDEAS.md) |
| **B7-H3 (CD276) / CD56 → ADC, bispecific or CAR-T** | `RT-B7H3` | Tier 3 — already red-teamed in this repo: not selective (BH q = 1.0) | [`emc-surface-target-landscape.md`](emc-surface-target-landscape.md) | [`emc-post-degrader-options.md`](emc-post-degrader-options.md), [`IDEAS.md`](../IDEAS.md) |
| **Carfilzomib ± anthracycline (± venetoclax)** | `RT-CARFILZOMIB` | NEAR-TERM LEAD — best ex-vivo EMC evidence | [`repurposing-hypotheses.md`](repurposing-hypotheses.md) | [`IDEAS.md`](../IDEAS.md) |
| **CAR-T for EMC (surface-directed)** | `RT-CART-SURFACE` | Hard but not closed — among surface modalities, ADC/FAPI-RLT likely beat CAR-T to a patient | [`car-t-strategies-emc.md`](car-t-strategies-emc.md) | [`IDEAS.md`](../IDEAS.md) |
| **Covalent probe at C397 — as a REAGENT, not a drug** | `RT-COVALENT-PROBE` | Tier 3 — the largest single demotion; D ≈ 0 and P is negative rather than merely absent | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#route-5--the-covalent-probe-at-c397-proposed-as-a-reagent---the-largest-single-demotion) | [`target-route-options.md`](target-route-options.md), [`nr4a3-monovalent-pocket-route.md`](nr4a3-monovalent-pocket-route.md) |
| **CRISPR/Cas9 intron-targeted fusion disruption; Cas13 fusion-RNA knockdown** | `RT-CRISPR-CAS13` | Tier 3 — delivery, and Cas13 collateral activity | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#routes-813--why-each-sits-in-tier-3) | [`novel-modalities.md`](novel-modalities.md) |
| **Target the DBD / DNA binding** | `RT-DBD` | ✕ down, on arithmetic — 92.8 % / 98.6 % paralogue identity | [`target-route-options.md`](target-route-options.md#route-12--target-the-dbd--dna-binding) | [`emc-post-degrader-options.md`](emc-post-degrader-options.md) |
| **NR4A3-LBD PROTAC degrader** | `RT-DEGRADER` | LEADING driver-directed route; the program's north star — and the route whose four blocking failures reorganise every other row | [`nr4a3-program-map.md`](nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language) | [`IDEAS.md`](../IDEAS.md), [`emc-treatment-strategy.md`](emc-treatment-strategy.md) |
| **Target the EWSR1 half at the protein level** | `RT-EWSR1-PROTEIN` | ✕ down — relocates onto an essential gene | [`target-route-options.md`](target-route-options.md#route-11--target-the-ewsr1-half-at-the-protein-level) | — |
| **FAP-targeted radioligand therapy (FAPI-RLT)** | `RT-FAP-RLT` | Emerging, plausible | [`emerging-modalities-scan-emc.md`](emerging-modalities-scan-emc.md#2-fap-targeted-radioligand-therapy-fapi-rlt--emerging-plausibly-applies) | [`IDEAS.md`](../IDEAS.md) |
| **A ligand for the shared FET low-complexity half** | `RT-FET-LC-LIGAND` | Tier 3 — relocates selectivity somewhere worse | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#route-15---a-ligand-for-the-shared-fet-low-complexity-half) | — |
| **Molecular glue instead of a PROTAC** | `RT-GLUE` | ⏸ watch, do not build — removes handles and keeps the same ~1 kcal/mol claim | [`target-route-options.md`](target-route-options.md#route-10--a-molecular-glue-instead-of-a-protac) | [`emc-post-degrader-options.md`](emc-post-degrader-options.md), [`nr4a3-program-map.md`](nr4a3-program-map.md) |
| **HDAC / BET to lower fusion expression** | `RT-HDAC-BET` | Tier 3 — not fusion-selective; a class effect, not an EMC result | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#routes-813--why-each-sits-in-tier-3) | — |
| **Checkpoint inhibitor + anti-angiogenic TKI combination** | `RT-ICI-TKI` | TOP NEAR-TERM LEAD (best EMC evidence) | [`immunotherapy-options-emc.md`](immunotherapy-options-emc.md#2-checkpoint-inhibitor--anti-angiogenic-tki-combination--real-emc-signal-new-lead) | [`IDEAS.md`](../IDEAS.md) |
| **Fusion-junction neoantigen (the antigen, shared by three delivery routes)** | `RT-JUNCTION-NEOANTIGEN` | ○ drafted — and now carrying a correction owed | [`target-route-options.md`](target-route-options.md#route-7--junction-neoantigen-vaccine--tcr-t--soluble-tcr) | [`fusion-junction-neoantigen-paper.md`](fusion-junction-neoantigen-paper.md) |
| **The honest methods paper on the degrader program's own failure record** | `RT-METHODS-PAPER` | Tier 1, rank 1 — DELIVERABLE | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#route-3---publish-the-methods-result-the-program-has-already-earned--rank-1) | [`IDEAS.md`](../IDEAS.md) |
| **Monovalent LBD pocket modulation — a molecule that only OCCUPIES the NR4A3 LBD** | `RT-MONOVALENT` | REGISTERED, NOT PROMOTED — and specifically a DOWNGRADE of what the probe framing implies about a monovalent drug | [`nr4a3-monovalent-pocket-route.md`](nr4a3-monovalent-pocket-route.md#7--grade-against-the-failure-record) | [`IDEAS.md`](../IDEAS.md) |
| **Ex-vivo pan-NR4A pole (CAR-T manufacturing additive)** | `RT-PANNR4A-EXVIVO` | ★ already in the paper as pole 2; under-used as an ARGUMENT | [`target-route-options.md`](target-route-options.md#route-4--the-ex-vivo-pan-nr4a-pole-car-t-manufacturing-additive) | [`nr4a3-degrader-carT-and-family-druggability-framing.md`](nr4a3-degrader-carT-and-family-druggability-framing.md) |
| **PPARG downstream-effector (repurpose TZDs)** | `RT-PPARG-DOWNSTREAM` | ★ keep; direction unresolved | [`target-route-options.md`](target-route-options.md#route-5--downstream-of-the-fusion-pparg-and-the-transactivated-nodes) | [`IDEAS.md`](../IDEAS.md) |
| **PRAME-directed brenetafusp (ImmTAC) / PRAME CAR-TCR** | `RT-PRAME-IMMTAC` | NEW antigen-directed lead — best of the CTAs | [`IDEAS.md`](../IDEAS.md#emc-treatment-discovery--route-status-board-updated-2026-06-21) | [`immunotherapy-options-emc.md`](immunotherapy-options-emc.md) |
| **Trans-splicing ribozyme → suicide gene, triggered by the fusion transcript** | `RT-RIBOZYME` | Tier 3 — vector delivery; a 2000s-era technique with no modern solid-tumour clinical footing | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#routes-813--why-each-sits-in-tier-3) | — |
| **RIPTAC — bind the tumour protein, poison an essential one** | `RT-RIPTAC` | Tier 3 — needs paralogue selectivity AND a med-chem campaign; strictly worse than TCIP on both | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#routes-813--why-each-sits-in-tier-3) | — |
| **RXR-heterodimer modulation of the fusion** | `RT-RXR` | ✕ CLOSED 2026-08-03 — NR4A3 does not heterodimerise with RXR | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#2--the-ranked-list) | [`IDEAS.md`](../IDEAS.md) |
| **SSTR2 / neuroendocrine theranostic** | `RT-SSTR2` | Tier 3 — demoted; W2 is the smallest imaginable and W1 is the problem | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#route-7--sstr2--neuroendocrine-theranostic-the-cheapest-possible-confirm-and-the-clearest-case-of-cheapness-not-being-enough) | [`emc-surface-target-landscape.md`](emc-surface-target-landscape.md), [`IDEAS.md`](../IDEAS.md) |
| **Synthetic-lethal / dependency partner (BRD9 / ncBAF via EWSR1-prion→BAF)** | `RT-SYNLETH-DEP` | DOWNGRADED — DepMap 24Q4 transfer prior negative; ⏸ parked on data, not on ideas | [`degrader-vs-synthetic-lethal.md`](degrader-vs-synthetic-lethal.md) | [`target-route-options.md`](target-route-options.md), [`IDEAS.md`](../IDEAS.md) |
| **Fusion-driven synthetic promoter → suicide gene** | `RT-SYNPROMOTER` | Tier 3 — vector delivery, AND EMC lacks the neomorphic DNA-binding element the technique depends on | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#route-14---the-fusion-driven-synthetic-promoter-and-the-precise-reason-emc-is-a-harder-case-than-ewing) | — |
| **TCIP — transcriptional chemically-induced proximity on EWSR1::NR4A3** | `RT-TCIP` | Tier 3 — demoted from Tier 2; the cheapest promotion available in the memo | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#2--the-ranked-list) | [`target-route-options.md`](target-route-options.md), [`IDEAS.md`](../IDEAS.md) |
| **Fusion-junction TCR-T / soluble-TCR (ImmTAC) against the junction peptide-HLA** | `RT-TCR-IMMTAC` | Tier 3 — the weak-junction-pHLA problem; EMC is antigen-cold | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#routes-813--why-each-sits-in-tier-3) | [`immunotherapy-options-emc.md`](immunotherapy-options-emc.md), [`IDEAS.md`](../IDEAS.md) |
| **TCR-T / engineered T cells vs a cancer-testis antigen (synovial-sarcoma port)** | `RT-TCRT-CTA` | DOWNGRADED to weak — gating fact resolved, mostly negative | [`immunotherapy-options-emc.md`](immunotherapy-options-emc.md) | [`IDEAS.md`](../IDEAS.md) |
| **Trabectedin (± RT or combination)** | `RT-TRABECTEDIN` | NEAR-TERM LEAD — approved, mechanism-fit | [`IDEAS.md`](../IDEAS.md#emc-treatment-discovery--route-status-board-updated-2026-06-21) | [`emerging-modalities-scan-emc.md`](emerging-modalities-scan-emc.md) |
| **Trabectedin + a PPARγ agonist (all approved drugs)** | `RT-TRABECTEDIN-PPARG` | Tier 2, rank 5 — ASK with a good taker and a thin deliverable | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#route-6---trabectedin--a-pparγ-agonist-an-all-approved-drug-combination-on-emcs-own-documented-axis) | [`IDEAS.md`](../IDEAS.md) |
| **Fusion-selective ubiquitination — discriminate at the transfer step** | `RT-UBIQ-SELECTIVE` | ✕ closed by a measurement already committed | [`target-route-options.md`](target-route-options.md#route-13--fusion-selective-ubiquitination-closed-by-a-number-the-repo-already-owns) | — |
| **Fusion-junction vaccine / HLA-coverage paper** | `RT-VACCINE` | PARKED — done, not a treatment path; a self-adjacent junction in a cold tumour is a weak immunogen | [`hla-coverage-emc.md`](hla-coverage-emc.md) | [`IDEAS.md`](../IDEAS.md), [`emc-post-degrader-options.md`](emc-post-degrader-options.md) |

### 1a · Route aliases — the same route under every number the repo has given it

Route numbers are stable identifiers *inside* each memo and they are **not** the same numbering. This table is what stops "route 5" in one file being read as "route 5" in another.

| id | also called |
|---|---|
| `RT-6MP` | `Tier 4 closed — 6-MP` |
| `RT-AF3-INTERFACE` | `AF3 interface` |
| `RT-ANDGATE` | `target-route route 8`, `the AND-gate` |
| `RT-ASO` | `Fusion-junction ASO / siRNA`, `the junction ASO`, `post-degrader route 2`, `target-route route 3` |
| `RT-ASO-ASK` | `post-degrader route 2b`, `the ASO wet-lab ask` |
| `RT-ASYMMETRIC` | `target-route route 1`, `the asymmetric requirement` |
| `RT-ATR-ASSESS` | `post-degrader route 1a`, `the ATR assessment` |
| `RT-ATR-PANEL` | `post-degrader route 1b`, `the ATR cell panel` |
| `RT-B7H3` | `post-degrader route 13`, `B7-H3`, `CD276` |
| `RT-CARFILZOMIB` | `carfilzomib` |
| `RT-CART-SURFACE` | `CAR-T for EMC` |
| `RT-COVALENT-PROBE` | `post-degrader route 5`, `the covalent probe`, `the C397 probe` |
| `RT-CRISPR-CAS13` | `post-degrader route 9`, `Cas13` |
| `RT-DBD` | `target-route route 12` |
| `RT-DEGRADER` | `Degrader — NR4A3-LBD PROTAC`, `the degrader`, `the degrader program` |
| `RT-EWSR1-PROTEIN` | `target-route route 11` |
| `RT-FAP-RLT` | `FAPI-RLT`, `FAP-PET` |
| `RT-FET-LC-LIGAND` | `post-degrader route 15` |
| `RT-GLUE` | `target-route route 10`, `molecular glue` |
| `RT-HDAC-BET` | `post-degrader route 11` |
| `RT-ICI-TKI` | `ImmunoSarc`, `sunitinib + nivolumab` |
| `RT-JUNCTION-NEOANTIGEN` | `target-route route 7`, `junction neoantigen` |
| `RT-METHODS-PAPER` | `post-degrader route 3`, `the methods paper` |
| `RT-MONOVALENT` | `the monovalent route`, `monovalent LBD pocket modulation`, `the third framing of C397` |
| `RT-PANNR4A-EXVIVO` | `target-route route 4`, `pole 2`, `the pan-NR4A pole` |
| `RT-PPARG-DOWNSTREAM` | `target-route route 5`, `the PPARG/TZD row`, `downstream nodes the fusion transactivates` |
| `RT-PRAME-IMMTAC` | `PRAME-directed`, `brenetafusp` |
| `RT-RIBOZYME` | `post-degrader route 12` |
| `RT-RIPTAC` | `post-degrader route 8` |
| `RT-RXR` | `Tier 4 closed — RXR` |
| `RT-SSTR2` | `post-degrader route 7`, `SSTR2`, `⁶⁸Ga-DOTATATE / ¹⁷⁷Lu-DOTATATE` |
| `RT-SYNLETH-DEP` | `target-route route 9`, `BRD9 / ncBAF` |
| `RT-SYNPROMOTER` | `post-degrader route 14` |
| `RT-TCIP` | `post-degrader route 4`, `target-route route 6`, `TCIP`, `bivalent fusion-TF rewiring` |
| `RT-TCR-IMMTAC` | `post-degrader route 10`, `fusion-junction TCR / ImmTAC` |
| `RT-TCRT-CTA` | `afami-cel port`, `NY-ESO-1 / MAGE-A4 TCR-T` |
| `RT-TRABECTEDIN` | `trabectedin monotherapy` |
| `RT-TRABECTEDIN-PPARG` | `post-degrader route 6`, `trabectedin + pioglitazone` |
| `RT-UBIQ-SELECTIVE` | `target-route route 13` |
| `RT-VACCINE` | `the vaccine route`, `HLA-coverage paper` |

## 2 · What must never be conflated — and what each pair actually fails on

A distinctness that is asserted but not grounded collapses at the next edit, so every row carries the blockers that make the two routes different. **Two routes carrying the same grade and the same blockers are not two routes** — the checker fails on that shape, which is the covalent-probe / monovalent-modulator failure.

| route | must not be conflated with | axis | it fails on | why |
|---|---|---|---|---|
| `RT-6MP` | `RT-MONOVALENT` | which domain the mechanism lives in | `BLK-NOT-FUSION-SELECTIVE` | ⚠ SCOPED SO IT IS NOT OVER-READ: this closes 6-MP, NOT LBD-directed modulation generally. The published LBD-borne functional result was read out on a Gal4-NOR-1-LBD construct that is itself AF-1-less |
| `RT-ANDGATE` | `RT-DEGRADER` | what the second arm detects | `BLK-TERNARY-GEOMETRY` | ⚠ 'fusion-selective' is NOT automatically 'paralogue-free'. The AND-gate adds a fusion-vs-wild-type layer on top of the paralogue layer; arm 1 still carries the selectivity handles |
| `RT-ASO` | `RT-ASO-ASK` | deliverable vs ask | `BLK-NO-WET-LAB` | the manuscript is finished and needs nobody; the knockdown experiment needs a lab and has the portfolio's weakest taker. Grading them as one row is what the W1/W2/D correction exists to stop |
| `RT-ASO` | `RT-CRISPR-CAS13` | delivery class | `BLK-DELIVERY` | an oligonucleotide's delivery problem has clinical precedent in solid tumours; a vector's is a different engineering problem with different precedents, and Cas13 additionally carries collateral activity |
| `RT-ASO-ASK` | `RT-ASO` | deliverable vs ask | `BLK-DELIVERY` | the paper is unaffected by this ask failing — the one ask in the portfolio whose failure costs its route nothing |
| `RT-ATR-ASSESS` | `RT-ATR-PANEL` | deliverable vs ask | `BLK-CLASS-INHERITANCE` | the assessment produces a computed result whether or not one cell is ever plated; the panel is the experiment and this programme does not execute it. The corrected ranking SPLIT them for exactly this reason |
| `RT-ATR-ASSESS` | `RT-SYNLETH-DEP` | where the dependency comes from | `BLK-NO-EMC-DATA` | both are called 'synthetic lethality' and they are not the same route: the ATR axis is inherited from a FET-family class argument, the BRD9/ncBAF axis was a DepMap transfer prior and came back negative |
| `RT-ATR-PANEL` | `RT-ATR-ASSESS` | deliverable vs ask | `BLK-NO-WET-LAB` | its value is entirely in an experiment this programme cannot cause; the assessment's value is not |
| `RT-B7H3` | `RT-CART-SURFACE` | antigen vs modality | `BLK-NOT-FUSION-SELECTIVE` | B7-H3 is an ANTIGEN whose selectivity was measured and failed; CAR-T is a MODALITY that would use whichever antigen survives. Collapsing them hides that the modality is blocked by the antigen search, not by the cell product |
| `RT-B7H3` | `RT-SSTR2` | which antigen and how it was graded | `BLK-NOT-FUSION-SELECTIVE` | B7-H3's selectivity was MEASURED and failed (BH q = 1.0); SSTR2 is UNMEASURED in EMC. A measured negative and an unmeasured hope are not the same status |
| `RT-CART-SURFACE` | `RT-PANNR4A-EXVIVO` | where the NR4A molecule acts | `BLK-ANTIGEN-COLD` | ⚠ TWO DIFFERENT CAR-T ROUTES. This one treats EMC with a CAR against an EMC surface antigen. The pan-NR4A pole is a MANUFACTURING ADDITIVE applied ex vivo to the T cells, where the systemic-selectivity liability does not arise at all |
| `RT-CART-SURFACE` | `RT-B7H3` | antigen vs modality | `BLK-ANTIGEN-COLD`, `BLK-NO-EMC-DATA` | CAR-T is the modality; B7-H3 is one antigen it could use. The modality is blocked by the antigen search and by the cold myxoid stroma, not by the cell product |
| `RT-COVALENT-PROBE` | `RT-MONOVALENT` | what the molecule has to DO once bound | `BLK-NO-WET-LAB`, `BLK-R4-BINDS` | ⭐ THE FAILURE-3 PAIR. A probe needs only to BIND, so it inherits neither functional actionability nor a selectivity window; a monovalent DRUG needs the pocket to be a functional handle in the chimera and needs a selectivity requirement nobody has sized. Their in-silico halves fail on OPPOSITE things, so one demotion cannot cover both |
| `RT-CRISPR-CAS13` | `RT-ASO` | delivery class | `BLK-VECTOR-DELIVERY` | an oligonucleotide's delivery problem and a vector's delivery problem are different engineering problems with different precedents — BLK-DELIVERY vs BLK-VECTOR-DELIVERY |
| `RT-DEGRADER` | `RT-ANDGATE` | what the second arm detects | `BLK-TERNARY-GEOMETRY`, `BLK-PARALOGUE-DDG` | the AND-gate adds a fusion-vs-wild-type layer and LEAVES the paralogue layer exactly where it was — two orthogonal requirements, not one replaced |
| `RT-DEGRADER` | `RT-GLUE` | how proximity is induced | `BLK-PARALOGUE-DDG` | a glue faces the same discrimination with FEWER independent handles |
| `RT-DEGRADER` | `RT-MONOVALENT` | whether a degradation geometry is needed at all | `BLK-TERNARY-GEOMETRY` | the monovalent route deletes the ternary layer entirely; the degrader is defined by it |
| `RT-DEGRADER` | `RT-TCIP` | what the recruited partner does | `BLK-TERNARY-GEOMETRY`, `BLK-PARALOGUE-CONTROL` | the degrader's second partner is an E3 and its verdict is a degradation event; TCIP's is a transcriptional effector and its verdict is a rewired output — the ubiquitin-transfer geometry does not apply to it |
| `RT-EWSR1-PROTEIN` | `RT-FET-LC-LIGAND` | the same liability, arrived at from a different direction | `BLK-NOT-FUSION-SELECTIVE` | one targets EWSR1 as EWSR1; the other targets the FET low-complexity half as a shared class feature. Both land on wild-type EWSR1, so they share a blocker and are still separately registered because their entry points differ |
| `RT-FAP-RLT` | `RT-SSTR2` | which radioligand target | `BLK-NOT-FUSION-SELECTIVE` | both are theranostics and they target different things — FAP is the myxoid STROMA, SSTR2 is EMC's own neuroendocrine differentiation |
| `RT-FET-LC-LIGAND` | `RT-EWSR1-PROTEIN` | the same liability, arrived at from a different direction | `BLK-NO-WET-LAB` | a NEW route to this repo, proposed as a class-wide FET handle rather than as an EWSR1-specific one |
| `RT-GLUE` | `RT-DEGRADER` | how proximity is induced | `BLK-PARALOGUE-DDG`, `BLK-R4-BINDS` | a glue keeps the same ~1 kcal/mol paralogue claim with FEWER independent handles than a PROTAC — the registered reason it is watch-do-not-build rather than a cheaper degrader |
| `RT-JUNCTION-NEOANTIGEN` | `RT-VACCINE` | delivery of the same antigen | `BLK-ANTIGEN-COLD` | the antigen is one object; the vaccine, the TCR-T and the soluble TCR are three different products with different failure modes, and the board has graded them as one row |
| `RT-JUNCTION-NEOANTIGEN` | `RT-TCR-IMMTAC` | delivery of the same antigen | `BLK-ANTIGEN-COLD` | same antigen, engineered-cell or soluble-bispecific product rather than an immunisation |
| `RT-MONOVALENT` | `RT-COVALENT-PROBE` | what the molecule has to DO once bound | `BLK-FUNCTIONAL-ACTIONABILITY`, `BLK-UNSIZED-REQUIREMENT` | ⭐ THE FAILURE-3 PAIR. This route adds a make-or-break no other LBD route carries — functional actionability of the LBD IN THE CHIMERA — which cannot be computed, cannot be bought, and is not covered by the delegated dTAG test. The probe framing is untouched by all of it |
| `RT-MONOVALENT` | `RT-TCIP` | how many termini the molecule has | `BLK-FUNCTIONAL-ACTIONABILITY` | monovalent is strictly cleaner on the ternary axis — no second protein at all — while TCIP still inherits the induced-complex problem. The monovalent reach result therefore does not transfer to TCIP and vice versa |
| `RT-MONOVALENT` | `RT-6MP` | which domain the mechanism lives in | `BLK-FUNCTIONAL-ACTIONABILITY` | 6-MP is closed because it acts through the AF-1, the domain the disease deletes. That closure does NOT close LBD-directed modulation — the published LBD-borne functional result was read out on a Gal4-NOR-1-LBD construct that is itself AF-1-less |
| `RT-MONOVALENT` | `RT-DEGRADER` | whether a degradation geometry is needed at all | `BLK-FUNCTIONAL-ACTIONABILITY`, `BLK-UNSIZED-REQUIREMENT` | the degrader only has to BIND and be degraded; a monovalent modulator has to change what the chimera DOES, which is a make-or-break the degrader does not carry |
| `RT-PANNR4A-EXVIVO` | `RT-CART-SURFACE` | where the NR4A molecule acts | `BLK-NO-EMC-DATA` | it is not an EMC treatment route at all in the direct sense — it removes the selectivity requirement by changing the exposure regime, not by being cleverer about the pocket |
| `RT-PPARG-DOWNSTREAM` | `RT-TRABECTEDIN-PPARG` | whether the agonist acts alone | `BLK-NO-EMC-DATA` | this row is the agonist alone and its direction (agonism vs antagonism vs redundancy) is unresolved; the combination row's argument runs through promoter displacement and does not depend on resolving it the same way |
| `RT-PRAME-IMMTAC` | `RT-TCR-IMMTAC` | which peptide the TCR sees | `BLK-NOT-FUSION-SELECTIVE` | a cancer-testis antigen, not the junction; its access route is an existing basket trial rather than a bespoke product, and it sacrifices fusion-exclusivity |
| `RT-PRAME-IMMTAC` | `RT-TCRT-CTA` | which CTA | `BLK-ANTIGEN-COLD` | NY-ESO-1/MAGE-A4 TCR-T is DOWNGRADED on measured EMC CTA-low data; PRAME is the one CTA whose surrogate expression read came back favourable |
| `RT-RIBOZYME` | `RT-SYNPROMOTER` | what the fusion is sensed BY | `BLK-VECTOR-DELIVERY` | the ribozyme senses the fusion TRANSCRIPT by base-pairing; the synthetic promoter senses the fusion PROTEIN by DNA binding — and the second fails for an EMC-specific reason the first does not (EMC lacks a neomorphic DNA-binding element) |
| `RT-RIPTAC` | `RT-TCIP` | what the recruited partner does | `BLK-PARALOGUE-DDG`, `BLK-R4-BINDS` | a RIPTAC poisons an essential protein and therefore needs the paralogue selectivity a TCIP's effector recruitment can partly avoid; it is strictly worse on both axes and is registered so it is not re-proposed as 'TCIP-like' |
| `RT-SSTR2` | `RT-B7H3` | which antigen and how it was graded | `BLK-NO-EMC-DATA` | SSTR2 is UNMEASURED in EMC; B7-H3 was MEASURED and came back not selective (BH q = 1.0). 'Surface-target route' names both and they failed differently |
| `RT-SSTR2` | `RT-FAP-RLT` | which radioligand target | `BLK-NO-WET-LAB` | SSTR2 follows EMC's own neuroendocrine differentiation and its ask needs a clinician with an EMC patient; FAP targets the myxoid STROMA and its ask is an expression/avidity confirm |
| `RT-SYNLETH-DEP` | `RT-ATR-ASSESS` | where the dependency comes from | `BLK-NO-EMC-DATA` | 'synthetic lethality' names both. This one is a DepMap transfer prior that came back negative; the ATR route is a class inheritance from a published FET-family argument with its own structural precondition computed |
| `RT-SYNPROMOTER` | `RT-RIBOZYME` | what the fusion is sensed BY | `BLK-NOT-FUSION-SELECTIVE` | ⭐ the REASON this route fails is itself a computed-and-cited EMC result and belongs in a paper even though the route does not — EMC's fusion reads a normal NR4A response element, not a neomorphic one |
| `RT-TCIP` | `RT-MONOVALENT` | how many termini the molecule has | `BLK-INDUCED-COMPLEX`, `BLK-R4-BINDS` | a TCIP is still bivalent, so the reach result computed for the monovalent configuration DOES NOT TRANSFER to it — a different second terminus is a different enumeration, and running it is an open $0 item |
| `RT-TCIP` | `RT-DEGRADER` | what the recruited partner does | `BLK-INDUCED-COMPLEX` | TCIP recruits a transcriptional effector rather than an E3, so it retires the ubiquitin-transfer geometry while keeping the induced-complex problem |
| `RT-TCIP` | `RT-RIPTAC` | what the recruited partner does | `BLK-INDUCED-COMPLEX`, `BLK-R4-BINDS` | a TCIP recruits a transcriptional effector; a RIPTAC recruits an essential protein to poison it, which reinstates the full paralogue-selectivity requirement a TCIP can partly avoid |
| `RT-TCR-IMMTAC` | `RT-PRAME-IMMTAC` | which peptide the TCR sees | `BLK-ANTIGEN-COLD` | ⚠ BOTH ARE 'ImmTAC' AND THEY ARE NOT THE SAME ROUTE. This one targets the FUSION JUNCTION peptide-HLA (fusion-exclusive, weak junction). The PRAME route targets a cancer-testis antigen through an EXISTING tumour-agnostic basket product and is not fusion-exclusive at all |
| `RT-TCR-IMMTAC` | `RT-JUNCTION-NEOANTIGEN` | antigen vs product | `BLK-NO-EMC-DATA` | this is one of three products on the same antigen |
| `RT-TCRT-CTA` | `RT-PRAME-IMMTAC` | which CTA | `BLK-NO-EMC-DATA` | EMC is NY-ESO-1-rare and MAGE-A4-low on measured data; PRAME is separately expressed and separately graded |
| `RT-TRABECTEDIN` | `RT-TRABECTEDIN-PPARG` | combination vs monotherapy | `BLK-NO-EMC-DATA` | monotherapy rests on a reported EMC responder and a mechanism fit; the combination rests additionally on a published result in a sibling sarcoma and on the fusion→PPARG axis |
| `RT-TRABECTEDIN-PPARG` | `RT-TRABECTEDIN` | combination vs monotherapy | `BLK-NO-WET-LAB` | the board carried trabectedin and the PPARG axis as two separate rows for months and never joined them; joining them is what created THIS route, and the monotherapy row remains a distinct near-term lead with its own evidence |
| `RT-TRABECTEDIN-PPARG` | `RT-PPARG-DOWNSTREAM` | whether the agonist acts alone | `BLK-NO-EMC-DATA` | the downstream/TZD row is the agonist ALONE and carries an unresolved direction question that cuts AGAINST the naive version — in EMC the fusion turns PPARG on, so an agonist may be redundant. The combination's logic is promoter displacement unmasking a differentiation-competent receptor, which is a different argument |
| `RT-VACCINE` | `RT-JUNCTION-NEOANTIGEN` | antigen vs product | `BLK-NO-EMC-DATA` | the vaccine is one product built on the antigen; parking the product does not park the antigen, whose HLA-coverage output still feeds TCR-T eligibility |

## 3 · Load-bearing blockers — which one failure holds down how many routes

Read this as *redundancy*: a blocker on one route is a risk, a blocker on eleven is the portfolio's shape. A route that **retires** a blocker is the portfolio's answer to it.

| blocker | it is a statement about | one home | inherited by | retired by |
|---|---|---|---|---|
| **EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)** (`BLK-NO-EMC-DATA`) | data availability — the repo-wide rate-limiter, not any one route | [`IDEAS.md`](../IDEAS.md) | **15** — `RT-ASO-ASK`, `RT-ATR-ASSESS`, `RT-ATR-PANEL`, `RT-TRABECTEDIN-PPARG`, `RT-TRABECTEDIN`, `RT-PPARG-DOWNSTREAM`, `RT-SSTR2`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-PRAME-IMMTAC`, `RT-TCRT-CTA`, `RT-ICI-TKI`, `RT-CARFILZOMIB`, `RT-FAP-RLT`, `RT-SYNLETH-DEP` | — |
| **The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)** (`BLK-NOT-FUSION-SELECTIVE`) | what the molecule can and cannot tell apart | [`target-route-options.md`](target-route-options.md#3--what-genuinely-sidesteps-the-paralogue-problem-and-what-merely-relocates-it) | **9** — `RT-DEGRADER`, `RT-MONOVALENT`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-PRAME-IMMTAC`, `RT-FAP-RLT`, `RT-EWSR1-PROTEIN`, `RT-FET-LC-LIGAND`, `RT-HDAC-BET` | `RT-ASO`, `RT-SSTR2`, `RT-PANNR4A-EXVIVO`, `RT-JUNCTION-NEOANTIGEN`, `RT-TCR-IMMTAC`, `RT-ICI-TKI`, `RT-RIBOZYME` |
| **The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)** (`BLK-PARALOGUE-DDG`) | a free-energy difference between two similar pockets, which this program has failed to measure four separate ways | [`nr4a3-program-map.md`](nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged) | **7** — `RT-DEGRADER`, `RT-TCIP`, `RT-ASYMMETRIC`, `RT-ANDGATE`, `RT-GLUE`, `RT-DBD`, `RT-RIPTAC` | `RT-ASO`, `RT-ATR-ASSESS`, `RT-COVALENT-PROBE`, `RT-TRABECTEDIN-PPARG`, `RT-TRABECTEDIN`, `RT-PPARG-DOWNSTREAM`, `RT-SSTR2`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-PANNR4A-EXVIVO`, `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE`, `RT-TCR-IMMTAC`, `RT-PRAME-IMMTAC`, `RT-TCRT-CTA`, `RT-ICI-TKI`, `RT-CARFILZOMIB`, `RT-FAP-RLT`, `RT-SYNLETH-DEP`, `RT-EWSR1-PROTEIN`, `RT-FET-LC-LIGAND`, `RT-CRISPR-CAS13`, `RT-HDAC-BET`, `RT-RIBOZYME`, `RT-SYNPROMOTER` |
| **R4 — nothing is known to bind the cryptic pocket at all** (`BLK-R4-BINDS`) | an unanswered requirement that needs a bench | [`nr4a3-program-map.md`](nr4a3-program-map.md#32--the-rv-coverage-matrix--where-the-holes-are) | **7** — `RT-DEGRADER`, `RT-TCIP`, `RT-COVALENT-PROBE`, `RT-MONOVALENT`, `RT-ANDGATE`, `RT-GLUE`, `RT-RIPTAC` | `RT-ATR-ASSESS`, `RT-TRABECTEDIN-PPARG`, `RT-PPARG-DOWNSTREAM`, `RT-SYNLETH-DEP` |
| **No wet lab and no collaborator — an ask needs a self-interested taker before its size matters** (`BLK-NO-WET-LAB`) | the operating regime, not any route's science | [`what-a-civilian-can-buy.md`](what-a-civilian-can-buy.md) | **6** — `RT-ASO-ASK`, `RT-ATR-PANEL`, `RT-TCIP`, `RT-COVALENT-PROBE`, `RT-TRABECTEDIN-PPARG`, `RT-SSTR2` | `RT-METHODS-PAPER` |
| **EMC is antigen-cold, and the fusion junction is a weak peptide-HLA** (`BLK-ANTIGEN-COLD`) | the tumour's immunogenicity, shared by every antigen-directed route | [`immunotherapy-options-emc.md`](immunotherapy-options-emc.md) | **5** — `RT-CART-SURFACE`, `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE`, `RT-TCR-IMMTAC`, `RT-TCRT-CTA` | — |
| **Ternary geometry — assembly, E3, exit vector, ubiquitin transfer** (`BLK-TERNARY-GEOMETRY`) | the DEGRADER ARCHITECTURE, not the target | [`nr4a3-program-map.md`](nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language) | **5** — `RT-DEGRADER`, `RT-ANDGATE`, `RT-GLUE`, `RT-UBIQ-SELECTIVE`, `RT-AF3-INTERFACE` | `RT-ASO`, `RT-ATR-ASSESS`, `RT-TCIP`, `RT-COVALENT-PROBE`, `RT-MONOVALENT`, `RT-TRABECTEDIN-PPARG`, `RT-TRABECTEDIN`, `RT-PPARG-DOWNSTREAM`, `RT-SSTR2`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE`, `RT-TCR-IMMTAC`, `RT-PRAME-IMMTAC`, `RT-TCRT-CTA`, `RT-ICI-TKI`, `RT-CARFILZOMIB`, `RT-FAP-RLT`, `RT-SYNLETH-DEP`, `RT-CRISPR-CAS13`, `RT-HDAC-BET`, `RT-RIBOZYME`, `RT-SYNPROMOTER` |
| **Vector delivery (gene-therapy payload into a solid tumour)** (`BLK-VECTOR-DELIVERY`) | engineering, distinct from oligonucleotide delivery | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#routes-813--why-each-sits-in-tier-3) | **3** — `RT-CRISPR-CAS13`, `RT-RIBOZYME`, `RT-SYNPROMOTER` | — |
| **An induced ternary/bivalent complex is still required (a second protein must be placed)** (`BLK-INDUCED-COMPLEX`) | the same generation problem as the degrader, with a different second terminus | [`nr4a3-monovalent-pocket-route.md`](nr4a3-monovalent-pocket-route.md#1--the-route-stated-precisely--and-the-split-that-decides-it) | **2** — `RT-TCIP`, `RT-RIPTAC` | `RT-MONOVALENT` |
| **Class inheritance, not an EMC measurement — no NR4A3 fusion has been tested for the phenotype** (`BLK-CLASS-INHERITANCE`) | the strength of a transfer argument | [`emc-post-degrader-options.md`](emc-post-degrader-options.md#route-1---atr-inhibitor-synthetic-lethality-emc-inherits-a-class-vulnerability-it-has-never-been-tested-for) | **1** — `RT-ATR-ASSESS` | — |
| **Tumour delivery of an oligonucleotide or a vector** (`BLK-DELIVERY`) | engineering, not biology; not in-silico-solvable today | [`fusion-junction-aso-paper.md`](fusion-junction-aso-paper.md) | **1** — `RT-ASO` | — |
| **Endpoint-MD selectivity readout (E1) returns null** (`BLK-ENDPOINT-MD`) | an endpoint-MD instrument, not the target | [`nr4a3-program-map.md`](nr4a3-program-map.md#-gate-failed--the-smarca24-sensitivity-control-returns-null-on-an-adequately-powered-design-2026-08-02-1042-pm-et) | **1** — `RT-DEGRADER` | — |
| **Is the LBD a FUNCTIONAL handle in the chimera, whose other end is a strong independent activator?** (`BLK-FUNCTIONAL-ACTIONABILITY`) | a functional cell assay nobody has run; not covered by the delegated dTAG test | [`nr4a3-monovalent-pocket-route.md`](nr4a3-monovalent-pocket-route.md#2--the-crux-is-the-pocket-functionally-actionable--and-is-it-actionable-in-the-fusion) | **1** — `RT-MONOVALENT` | `RT-COVALENT-PROBE` |
| **The paralogue-discrimination positive control (NR-V04) is discordant** (`BLK-PARALOGUE-CONTROL`) | a positive control for paralogue discrimination | [`nr4a3-program-map.md`](nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language) | **1** — `RT-DEGRADER` | — |
| **Nobody has stated how much selectivity the route would need, so 'the requirement is smaller' is not a claim this repo can make** (`BLK-UNSIZED-REQUIREMENT`) | an absent specification, not a measured shortfall | [`nr4a3-monovalent-pocket-route.md`](nr4a3-monovalent-pocket-route.md#4--effect-on-the-paralogue-requirement--reshapes-into-a-requirement-of-unquantified-size) | **1** — `RT-MONOVALENT` | — |
| **The categorical (covalent) window at C397 does not survive the E3-arm-free reach enumeration on the conservative convention** (`BLK-REACH-CATEGORICAL`) | geometry at one opened target frame — it can refute a route, it cannot license one | [`nr4a3-monovalent-pocket-route.md`](nr4a3-monovalent-pocket-route.md#3--the-0-test-built-run-and-it-came-back-against-the-route) | **0** — — | — |
| **The program's only binary selectivity known-answer control is built and staged and has never been run** (`BLK-SELECTIVITY-CONTROL-UNAUTHORIZED`) | a decision, not a capability and not the target -- nothing failed and nothing is missing | [`nr4a3-program-map.md`](nr4a3-program-map.md#31--the-instrument-table) | **0** — — | — |

## 4 · Instruments — and which of them have no passing control

An instrument that has never recovered a known answer cannot support a claim, however good its output looks. A route may still *list* such an instrument — under **disclosed failing** — which is how the honest memos already write it. Citing one as **support** is a checker failure.

| instrument | known-answer control | state | cited as SUPPORT by | disclosed-failing on |
|---|---|---|---|---|
| **`V1`** Structural selectivity descriptor (selcal_interface_signature) | recover the published SMARCA2 Gln1469↔VCB hydrogen bond, unaided, from two crystals | ✓ passes | `RT-DEGRADER` | — |
| **`V2`** Ternary generator given both sites (assembly route) | rebuild 6HAX (in-set) and 9DTY (post-horizon) | ✓ passes | `RT-DEGRADER` | `RT-AF3-INTERFACE` |
| **`V3`** Ligand pose prediction (dock + MM-GBSA) | recover a known holo pose in a nuclear receptor from apo | ⚠ inconclusive | — | `RT-COVALENT-PROBE`, `RT-MONOVALENT` |
| **`V4`** Selectivity free energy (ABFE) — the selectivity known-answer test | CREBBP vs BRD4(1) / SGC-CBP30 | ⚠ no control | — | `RT-DEGRADER`, `RT-METHODS-PAPER` |
| **`V5`** Alchemical ternary cooperativity (valB_mini ΔΔG_coop) | reproduce a known cooperativity | ⛔ FAILS | — | `RT-DEGRADER`, `RT-METHODS-PAPER` |
| **`V6`** Relative FEP (OpenFE, the congeneric lane) | TYK2 ejm_31→ejm_42 benchmark | ✓ passes | `RT-DEGRADER` | — |
| **`V7`** ABFE engine, absolute | T4-lysozyme L99A + benzene | ⛔ FAILS | — | `RT-DEGRADER`, `RT-METHODS-PAPER` |
| **`V8`** ABFE engine, hydration | methane hydration free energy (FreeSolv) | ✓ passes | `RT-DEGRADER` | — |
| **`V9`** λ-overlap diagnostic on the standing ABFE block | a self-check, not a known answer | ⚠ no control | — | — |
| **`V10`** Interface-mutation physics (pmx/GROMACS) | barnase–barstar Y29A vs published ΔΔG | ✓ passes | — | — |
| **`V11`** Interface-stability endpoint (E1) | two attempts: NR-V04 retrospective, SMARCA2/4 sensitivity control | ⛔ FAILS | — | `RT-DEGRADER`, `RT-METHODS-PAPER` |
| **`V12`** Sequence-only co-folding (Boltz-2 ternary) | reproduce 9DTY/9DTX from sequence + ligand | ⛔ FAILS | — | `RT-DEGRADER`, `RT-METHODS-PAPER`, `RT-AF3-INTERFACE` |
| **`V13`** Cryptic-opening free-energy profile (metadynamics F(Rg)) | Gate 1: a genuine two-state cryptic opening | ⛔ FAILS | — | `RT-DEGRADER`, `RT-METHODS-PAPER` |
| **`V14`** BioEmu unbiased ensemble cross-check | ⛔ no in-repo known-answer test on this system | ⚠ no control | — | — |
| **`V15`** PocketMiner + four permutation nulls | the nulls are the control | ⚠ mixed | — | — |
| **`V16`** The causal matched-pair test S (RUNG 5a-KS) | ⛔ none — it has no known-answer calibrator | ⚠ no control | — | — |
| **`V17`** The exposure criterion EXPOSED_RSA = 0.25 | NR4A1 C551 — the one NR4A-family covalent site with literature support | ⛔ FAILS | — | `RT-DEGRADER`, `RT-METHODS-PAPER`, `RT-COVALENT-PROBE`, `RT-MONOVALENT` |
| **`V18`** The transfer-zone lysine-identity term | ⛔ none exists | ⚠ no control | — | `RT-UBIQ-SELECTIVE` |
| **`V19`** The generation-matched null (winner's-curse / generative confound) | the scrambled-objective arm | ⚠ mixed | — | — |
| **`V20`** Single-snapshot MM-GBSA margin > 0 as a selectivity verdict | 38 unrelated marketed drugs through the identical funnel | ⛔ FAILS | — | `RT-DEGRADER`, `RT-METHODS-PAPER` |
| **`V21`** The anti-target docking panel (antitarget_dock) | each target's own cognate crystallographic ligand re-docked through the identical protocol | ⛔ FAILS | — | `RT-DEGRADER`, `RT-METHODS-PAPER` |
| **`V22`** The scoring-independent second pose method (rDock) | ⛔ none of its own on this system — it is run BESIDE V3 and the comparison IS the test | ⚠ no control | — | — |
| **`INS-IDR-CENSUS`** FET N-terminal IDR / RGG retention census | the fusions in which ATM suppression was MEASURED (EWSR1::FLI1 type 1, EWSR1::ATF1 clear-cell types) are pushed through the identical pipeline as positive controls | ✓ passes | `RT-ATR-ASSESS` | — |
| **`INS-CONSTRUCT-DESIGNS`** Transcript-level fusion construct designer (frame computed at the nucleotide level) | each gene model must pass its own translate-and-sum self-check, and Ensembl translations are cross-checked against the UniProt cache | ✓ passes | `RT-ATR-ASSESS` | — |
| **`INS-FUSION-OBJECT-INVENTORY`** Fusion object sequence inventory + breakpoint enumeration | a REPRODUCED gate: five checks on exon coding status, boundaries and protein length, plus both exon maps' translate-and-sum self-checks | ✓ passes | — | — |
| **`INS-MONOVALENT-REACH`** Paired monovalent-vs-bivalent covalent reach enumeration (E3 arm removed) | its BIVALENT half must replicate the already-committed bivalent artifact cell-for-cell | ✓ passes | `RT-MONOVALENT` | — |
| **`INS-DDR-AXIS-SCAN`** ATRi/PARPi sensitivity re-cut by FET status (GDSC2) | a general-chemosensitivity correction — the ATRi effect must survive it, and the same lines' PARPi response is computed as the contrast arm | ✓ passes | `RT-ATR-ASSESS` | — |
| **`INS-DEPMAP-KO`** DepMap CRISPR-knockout dependency scan of the ATR axis | the FET-vs-non-FET sarcoma contrast must exceed the panel's own spread | ⛔ FAILS | — | `RT-ATR-ASSESS` |
| **`INS-FUSION-COFOLD`** Fusion protein-level co-folding model | ⛔ none of its own | ⚠ no control | — | — |
| **`INS-HLA-COVERAGE`** HLA population-coverage calculator | ⛔ no known-answer test recorded | ⚠ no control | — | `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE`, `RT-TCR-IMMTAC`, `RT-TCRT-CTA` |
| **`INS-GEO-SERIES-CHARACTERISE`** Sample-level GEO series characterisation + disease-label corroboration | Two-sided, on the expression half: housekeeping genes (ACTB, GAPDH) must read high in every sample AND tissue-restricted negatives (ALB, INS) must read near zero, or a low NR4A3 is unreadable rather than informative. Measured 4423.6 / 2574.7 against 0.474 / 0.000. | ✓ passes | — | — |

⛔ **18 of 31 instruments have no passing known-answer control:** `V3`, `V4`, `V5`, `V7`, `V9`, `V11`, `V12`, `V13`, `V14`, `V16`, `V17`, `V18`, `V20`, `V21`, `V22`, `INS-DEPMAP-KO`, `INS-FUSION-COFOLD`, `INS-HLA-COVERAGE`. That is decision-relevant and is the reason this column exists.

## 5 · Objects — every biological entity, at exon and residue level

Each fusion type is a **separate object**. The modelled construct that is not a reported type is registered as one too, because it is what several modules actually compute on.

| object | status | exon level | residue level | provenance |
|---|---|---|---|---|
| **EWSR1::NR4A3 type 1** (`OBJ-FUS-T1`) | reported | EWSR1 exon 12 :: NR4A3 exon 3 | EWSR1(1–431) :: 1 junction residue :: NR4A3(1–626) | `EV-PMC3335514`, `EV-PMC4055444`, `EV-PMC4015728`, `EV-PMC2395470`, `EV-PMC6766969` |
| **EWSR1::NR4A3 type 2** (`OBJ-FUS-T2`) | reported | EWSR1 exon 7 :: NR4A3 exon 2 | EWSR1(1–264) :: [59 UTR-encoded residues] :: NR4A3(1–626) | `EV-PMC3335514`, `EV-PMC4015728` |
| **EWSR1::NR4A3 type 5** (`OBJ-FUS-T5`) | reported | EWSR1 exon 13 :: NR4A3 exon 3 | EWSR1(1–472) :: 1 junction residue :: NR4A3(1–626) | `EV-PMC4055444`, `EV-PMC2395470` |
| **TAF15::NR4A3** (`OBJ-FUS-TAF15`) | reported | TAF15 exon 6 :: NR4A3 exon 3 — reported as the ONLY coding junction ("exclusively", "always") | TAF15(1–161) :: 1 junction residue :: NR4A3(1–626) | `EV-PMC3335514`, `EV-PMC4055444`, `EV-PMC2395470`, `EV-PMC6766969` |
| **FUS::NR4A3** (`OBJ-FUS-FUSNR4A3`) | reported_breakpoint_unpinned | ⛔ no exon-level breakpoint statement found in this repo's literature cache | ⛔ unpinned — answered as a FUNCTION of breakpoint by the sweep, never as a point | — |
| **TCF12::NR4A3** (`OBJ-FUS-TCF12`) | reported_breakpoint_unpinned | ⛔ genomic resolution only — "the breakpoint affects the region of intron 5" | ⛔ unpinned; TCF12 also has several alternatively-spliced isoforms and Ensembl/UniProt disagree on the canonical (706 aa vs 682 aa) | `EV-PMC4055444` |
| **The modelled EWSR1 e7 :: NR4A3 e3 construct** (`OBJ-MODEL-E7E3`) | modelled_not_reported | EWSR1 exon 7 :: NR4A3 exon 3 — ⛔ NOT A REPORTED FUSION TYPE. It pairs the 5′ half of reported type 2 with the 3′ half of reported type 1. | EWSR1(1–264) :: NR4A3(1–626), with no UTR-encoded segment | — |
| **NR4A3 / NOR-1 (wild type)** (`OBJ-NR4A3-WT`) | wild_type | ENST00000395097 — 8 transcript exons, 6 coding; exons 1 and 2 are NON-CODING (the cause of the off-by-two correction) | 626 aa | — |
| **NR4A1 / Nur77** (`OBJ-NR4A1-WT`) | wild_type | — | — | — |
| **NR4A2 / Nurr1** (`OBJ-NR4A2-WT`) | wild_type | — | — | — |
| **EWSR1 (wild type)** (`OBJ-EWSR1-WT`) | wild_type | ENST00000397938 — 17 transcript exons, 17 coding | 656 aa | — |
| **The modelled NR4A3 ligand-binding domain construct (NR4A3 373–626)** (`OBJ-NR4A3-LBD-MODELLED`) | domain | — | NR4A3 373–626 | — |
| **Catalogue recombinant NR4A3 LBD (Cayman 40344, UniProt aa 398–626)** (`OBJ-NR4A3-LBD-CATALOGUE`) | domain | — | UniProt 398–626 | — |
| **NR4A3 AF-1 (N-terminal activation function)** (`OBJ-NR4A3-AF1`) | domain | — | delimited to residues 1–112 for SRC-2 recruitment; the repo measures the swapped stretch as NR4A3 1–260 ↔ EWSR1-LC 1–264 | `EV-WANSA-2003` |
| **NR4A3 C4 zinc-finger DNA-binding domain** (`OBJ-NR4A3-DBD`) | domain | — | — | `EV-FILION-2009` |
| **NR4A3 C397** (`OBJ-RES-C397`) | residue | — | NR4A3 cysteine 397 | — |
| **NR4A3 C166** (`OBJ-RES-C166`) | residue | — | NR4A3 cysteine 166 — present in the fusion under every plausible breakpoint, absent from every structure in this program | — |
| **NR4A1 C551** (`OBJ-RES-NR4A1-C551`) | residue | — | NR4A1 cysteine 551 — the one NR4A-family covalent site with literature support | — |
| **ACH-001519 / H-EMC-SS** (`OBJ-LINE-HEMCSS`) | identity_disputed | — | — | — |

### 5a · ⚠ Contested names — a name that maps to more than one object

A name on this list may **not** appear in any object's aliases. That is enforced.

| name | maps to | conflict |
|---|---|---|
| **the canonical EMC fusion** | `OBJ-FUS-T1`, `OBJ-MODEL-E7E3` | `OC-2` — Live text in several files uses this phrase for the MODELLED e7::e3 construct; the 2026-08-03 correction assigns 'canonical' to reported type 1 (e12::e3). Both readings are currently in the repo, so the name is registered as CONTESTED rather than as an alias of either object. Per the invariant a contested name may not appear in any object's `aliases`. |
| **EMC's canonical fusion** | `OBJ-FUS-T1`, `OBJ-MODEL-E7E3` | `OC-2` — Same ambiguity, different wording; both forms are in live text. |

### 5b · ⛔ Disputed identity — a model whose label the curated record contradicts

A claim is only as good as the provenance of the thing it was read off. An entry here means the repository was, or could be, reading biology off a reagent whose identity the public record does not support. **Every file naming one of these is classified below, and a tracked file that names one without being classified fails the build (`O4`).**

#### ACH-001519 / H-EMC-SS (`OBJ-LINE-HEMCSS`) — verdict `NOT_FUSION_POSITIVE_PER_CURATED_RECORD`

- **Labelled as:** Extraskeletal Myxoid Chondrosarcoma (DepMap OncotreeSubtype)
- **Verdict lives in:** `ART-ATR-VULNERABILITY` → `/part_a_hemcss_identity/verdict` (this registry points at it and does not restate it)
- **Curated record, verbatim:** *"Caution: Does not harbor a gene fusion involving EWSR1 which is a hallmark of extraskeletal myxoid chondrosarcoma (PubMed=34413129)."*
- Cellosaurus CVCL_1238 curated CAUTION, verbatim above, citing a primary source.
- DepMap OmicsFusionFiltered.csv 24Q4: the model IS in the file (1,670 models) with 2 filtered calls -- AL158209.1--NEBL and VIM--RPS25 -- and NEITHER names NR4A3, EWSR1, TAF15 or FUS. The model being present is what makes this a reading of absence rather than an absent reading.
- DepMap expression: NR4A3 at 0.941 log2(TPM+1), 83rd percentile of 1,673 lines but against a panel median of 0.214. A fusion transcript carries the NR4A3 body under EWSR1's promoter and would read far higher. WEAK CORROBORATION ONLY -- expression alone can neither prove nor exclude a fusion.
- ⚠ **What this CANNOT settle:** Cell-line identity is settled by STR authentication against the donor and by RT-PCR for the fusion. Neither is in public data at the resolution needed and neither is something this programme can perform -- it has no bench. So this does NOT establish what the line is instead, that the original characterisation was wrong, or that the line is not EMC: a line can be misidentified, can drift in culture, or can be a genuine fusion-negative tumour of the same histology. What IS established is that the PUBLIC RECORD does not support the label this repository was applying.
- **Correction home:** [`emc-surface-target-landscape.md`](emc-surface-target-landscape.md) (marker `Amendment 1`)
- **May NOT ground:** any claim of the form 'EMC expresses X' / 'EMC's surface phenotype is Y'; any EMC-specific dependency, sensitivity or biomarker reading; any corroboration of EMC's neuroendocrine differentiation; the description of this repository as having a real EMC cell line in public data

| file | how it uses the model | classification |
|---|---|---|
| [`IDEAS.md`](../IDEAS.md) | the 2026-07-03 'DepMap DOES contain one EMC line' correction, and the surface-paper headline | ⛔ **invalidated** |
| [`README.md`](README.md) | manuscripts index entry for the surface-target preprint | ⛔ **invalidated** |
| [`emc-post-degrader-options.md`](emc-post-degrader-options.md) | route 1's $0 CRISPR-availability finding (unaffected); route 1's EMC-model list for the ATRi ask; route 6's D axis, whose only computable component was a PPARG read off this model | ⛔ **invalidated** |
| [`emc-surface-target-landscape.md`](emc-surface-target-landscape.md) | PREPRINT. Title/abstract framing, §2.2 class definition, §3.1 + Table 1, §3.5, §6, §7 | ⛔ **invalidated** |
| [`emc-surface-target-outreach.md`](emc-surface-target-outreach.md) | OUTWARD-FACING draft emails: 'the one EMC line in public data'; pre-send checklist | ⛔ **invalidated** |
| [`emc-surface-target-redteam.md`](emc-surface-target-redteam.md) | the 'reframing discovery' that introduced the EMC label into the preprint; finding M8 | ⛔ **invalidated** |
| [`depmap-insilico-findings.md`](../modalities/depmap-insilico-findings.md) | Findings 2 and 3 read the `myxoid` subtype column, which is this line at n=1. Finding 3 infers 'EMC is a myxoid-class tumour, so [PRAME 7.6] is the most promising antigen-directed signal' | ⛔ **invalidated** |
| [`depmap-target-expression.json`](../modalities/depmap-target-expression.json) | the artifact: `/surface_and_cta_by_subtype/*/myxoid`, every entry n=1 | ⛔ **invalidated** |
| [`depmap_target_expression.py`](../modalities/depmap_target_expression.py) | produces the `myxoid` column: `subtypes = [... 'myxoid' ...]` is a substring match on the Oncotree label, and 'Extraskeletal Myxoid Chondrosarcoma' contains it | ⛔ **invalidated** |
| [`emc-surfaceome-scan.json`](../modalities/emc-surfaceome-scan.json) | committed artifact carrying `myxoid_mean` / `emc_line_top_surface` and their captions | ⛔ **invalidated** |
| [`emc_surfaceome_scan.py`](../modalities/emc_surfaceome_scan.py) | produces `myxoid_mean` and `emc_line_top_surface` from this model | ⛔ **invalidated** |
| [`emc-treatment-roadmap.md`](emc-treatment-roadmap.md) | quotes the myxoid PRAME 7.6, B7-H3 4.4 and CD56 ~0 as 'myxoid liposarcoma' subtype reads | ⚠ survives, re-labelled |
| [`emc-treatment-strategy.md`](emc-treatment-strategy.md) | the tracker summary: 'PRAME ... high in myxoid (7.6)/synovial (7.2)'; B7-H3 'incl. myxoid' | ⚠ survives, re-labelled |
| [`nr4a3-degrader-paper-SI.md`](nr4a3-degrader-paper-SI.md) | named as an example EMC model in the 'no LOF experiment exists' statement | ⚠ survives, re-labelled |
| [`nr4a3-emc-biology-evidence.md`](nr4a3-emc-biology-evidence.md) | 'no LOF experiment in any EMC cell line (e.g. H-EMC-SS)' -- a literature-absence claim | ⚠ survives, re-labelled |
| [`nr4a3-program-map.md`](nr4a3-program-map.md) | Q14 in the open-question queue | ⚠ survives, re-labelled |
| [`target-route-options.md`](target-route-options.md) | route 9's park condition and queue item 7 -- 're-query DepMap for CRISPR data' | ⚠ survives, re-labelled |
| [`what-a-civilian-can-buy.md`](what-a-civilian-can-buy.md) | the JCRB repository row -- the line is named as what JCRB holds | ⚠ survives, re-labelled |
| [`emc-atri-prereg.md`](../modalities/emc-atri-prereg.md) | §3 names H-EMC-SS among candidate EMC models for the ATRi ask | ⚠ survives, re-labelled |
| [`emc-atr-vulnerability-assessment.md`](emc-atr-vulnerability-assessment.md) | PART A -- the assessment that established the verdict, and its repo-wide use inventory | ✅ unaffected — It is the document that ESTABLISHED the verdict; it asserts no EMC reading from the line. |
| [`emc-systems-map.json`](emc-systems-map.json) | this registry: two revival triggers name the line, plus this object | ✅ unaffected — TRG-EMC-MODEL-ACCESS already required an 'authenticated H-EMC-SS' before the verdict existed, and TRG-EMC-EXPRESSION-DATASET asks for data BEYOND this model. Neither asserts an EMC reading from it. |
| [`emc-systems-map.md`](emc-systems-map.md) | the generated view of this registry | ✅ unaffected — Generated from the registry; never hand-edited. |
| [`emc_systems_map_check.py`](emc_systems_map_check.py) | the O3/O4 guard itself -- its docstring names the model as the failure it comes from | ✅ unaffected — It is the guard. Naming the model in the guard that classifies uses of the model is not a use of the model; excluding it by name would instead be a silent hole in the sweep. |
| [`test_emc_systems_map_check.py`](tests/test_emc_systems_map_check.py) | the negative tests for O3/O4 -- they mutate this object's entry into the broken shapes | ✅ unaffected — Test fixtures asserting the guard fails when it should; they assert nothing about EMC. |
| [`method-watch-triggers.json`](../method-watch-triggers.json) | TRG-EMC-EXPRESSION-DATASET's _still_watching_for clause (a), which names this line's dispute as the reason a per-sample FUSION CONFIRMATION is what the trigger is still waiting for | ✅ unaffected — The trigger reads no data from this line and grades nothing with it. It cites the dispute as the STANDARD a future EMC dataset has to meet — an EMC LABEL is indistinguishable from an EMC FUSION without a call — which is a use the dispute creates rather than one it invalidates. |
| [`atr_hrd_sarcoma_series.py`](../modalities/atr_hrd_sarcoma_series.py) | a comment in the GSE299349 identity check, naming this line as the REASON that check exists and as the weaker comparator its own read improves on | ✅ unaffected — It reads no data from this line and grounds no claim on it. The line appears only as the precedent: an EMC LABEL is not an EMC FUSION, which is why the new EMC-labelled sample (GSM9037837 / USZ-23_EMC3) is corroborated against 67 sarcoma samples from the same deposit before anything is built on it. Citing a disputed identity as a cautionary precedent is the one use the dispute cannot invalidate. |
| [`depmap-sarcoma-dependency.json`](../modalities/depmap-sarcoma-dependency.json) | `/BRD9_by_fusion_sarcoma_subtype/Myxoid_liposarcoma` | ✅ unaffected — The field is `null` -- an empty group. It grounds nothing. |
| [`depmap_sarcoma_dependency.py`](../modalities/depmap_sarcoma_dependency.py) | its `Myxoid_liposarcoma` BRD9 comparator group is a substring match that would select this line | ✅ unaffected — The group is EMPTY -- the model has no CRISPR gene-effect data, so the committed artifact reads `"Myxoid_liposarcoma": null` and no dependency figure rests on it. Verified against the artifact, not assumed. The GROUP NAME is wrong and is corrected in place. |
| [`emc-atr-vulnerability-inputs.json`](../modalities/emc-atr-vulnerability-inputs.json) | the raw inputs behind `part_a_hemcss_identity` | ✅ unaffected — Raw inputs to the verdict, not a claim about EMC. |
| [`emc-atr-vulnerability.json`](../modalities/emc-atr-vulnerability.json) | `part_a_hemcss_identity` -- the artifact that owns the verdict | ✅ unaffected — It is the verdict's one home. |
| [`emc_atr_vulnerability.py`](../modalities/emc_atr_vulnerability.py) | the module that computes `part_a_hemcss_identity` | ✅ unaffected — It is the instrument that produced the verdict. |
| [`fet-ddr-axis-scan.json`](../modalities/fet-ddr-axis-scan.json) | the `/emc_line` block recording that the model has no CRISPR data | ✅ unaffected — A record of an absence of data about the model. It grounds no EMC claim, and the EMC group it would have joined is empty (`n_with_crispr: 0`). |
| [`fet_ddr_axis_scan.py`](../modalities/fet_ddr_axis_scan.py) | asks whether the model has CRISPR gene-effect data; defines EMC_MODEL_ID | ✅ unaffected — It reports DATA AVAILABILITY, and the answer was 'no CRISPR data' (`/emc_line/has_crispr_gene_effect: false`). Because `fet_ids` intersects with the CRISPR index the model was never in the FET group (`grouping.FET_rearranged.EMC.n_with_crispr: 0`), and it is absent from the fusion-call grouping too because neither of its 2 calls names a FET gene. So NO dependency, sensitivity or contrast number in this module rests on it. Verified, not assumed. |
| [`MIGRATION.md`](../../systems/MIGRATION.md) | §3.10 — the record of porting this object and its instrument into the graph during the merge | ✅ unaffected — A migration record: it says WHERE the object was ported and WHY the rich blocks stayed here. It reads no data from the line and grounds no EMC claim. |
| [`instruments.json`](../../systems/graph/instruments.json) | INS-GEO-SERIES-CHARACTERISE `characterises: [OBJ-LINE-HEMCSS]` — the typed form of what its legacy `serves` said in prose | ✅ unaffected — The same use the instrument's own legacy row already had and which is classified `unaffected` on atr_hrd_sarcoma_series.py: the line appears as the CAUTIONARY PRECEDENT that an EMC label is not an EMC fusion, which is why a new EMC-labelled sample is corroborated before anything is built on it. Citing a disputed identity as the reason for a check is the one use the dispute cannot invalidate. |
| [`objects.json`](../../systems/graph/objects.json) | the systems-model projection of this object — the eight fields the graph's object shape carries | ✅ unaffected — It is a REGISTRATION of the dispute, not a reading of the line. The `identity` verdict, `may_not_ground`, the 30-entry `read_by` sweep and `_sweep_limit` deliberately stay in this registry, because the O3/O4 guards that enforce them live in emc_systems_map_check.py — a second copy would be a second home for the fact those guards protect. The projection asserts nothing about EMC. |
| [`instruments.md`](../../systems/views/registers/instruments.md) | the generated instrument register — renders the `characterises` edge above | ✅ unaffected — Generated from systems/graph/instruments.json by systems_check.py and never hand-edited. It inherits that row's classification exactly as emc-systems-map.md inherits this registry's. |

> ⛔ Registered 2026-08-05 after the repo spent a month treating this as 'the one real EMC line in DepMap'. The `[to verify]` flag on its fusion status was written honestly and carried faithfully in four places -- carrying a flag is not resolving one, and the resolving observation was one free API call available the whole time. ⚠ A ROUTE GRADE INPUT MOVED AND IS NOT RE-GRADED HERE: route 6 (RT-TRABECTEDIN-PPARG) in emc-post-degrader-options.md had a D axis whose only computable component was a PPARG-axis read off this model. Re-grading is a separate call and belongs to that memo's owner.

## 6 · Evidence — keyed by a canonical identifier, with every name it travels under

This is the table that makes the *Munck / Zaienne* class of error structurally impossible: a wrong name is registered as a **misattribution of one evidence item**, so both names resolve to the same source and the checker fails if the wrong one spreads to a new file.

| evidence | canonical id | aliases | ⚠ misattributed as | cited in |
|---|---|---|---|---|
| `EV-ZAIENNE-2022` Zaienne D, Arifi S, Marschner JA, Heering J, et al. Druggability Evaluation of the Neuron Derived Orphan Recep… | PMID 35704774 · PMCID PMC9542104 · DOI 10.1002/cmdc.202200259 | `Zaienne 2022`, `Zaienne et al. ChemMedChem 2022`, `Zaienne, ChemMedChem 2022`, `Zaienne D, Arifi S, Marschner JA, Heering J, Merk D`, `Zaienne-19`, `Zaienne-2022` | **`Munck 2022`** | degrader-vs-synthetic-lethal.md, emc-post-degrader-options.md, emc-treatment-roadmap.md, nr4a3-congeneric-dock-shard.json, nr4a3-degrader-design-spec.md, nr4a3-druggability-reconciliation.md, nr4a3-monovalent-pocket-route.md, published-warhead-registry.json, rbfe_edges.py, safe2025_verify.py, target-route-options.md |
| `EV-ZETTERSTROM-1996` Zetterström RH et al. Mol Endocrinol 1996;10:1656–66.… | PMID 8961274 | `Zetterström et al., Mol Endocrinol 1996`, `Zetterstrom 1996`, `Zetterström et al., *Mol Endocrinol* 1996` | — | emc-post-degrader-options.md |
| `EV-WANSA-2003` Wansa KDSA et al. J Biol Chem 2003;278(27):24776–90.… | PMID 12709428 | `Wansa et al., J Biol Chem 2003`, `Wansa 2003`, `Wansa et al., *J Biol Chem* 2003` | — | emc-post-degrader-options.md |
| `EV-FET-ATR-2023` FET fusion oncoproteins impair ATM activation at double-strand breaks through their shared N-terminal IDR, lea… | PMID 37205599 · DOI 10.1101/2023.04.30.538578 | `PMID 37205599`, `the FET/ATR paper` | — | IDEAS.md, emc-fet-idr-census.json |
| `EV-FILION-2009` Filion C et al. (2009) — the EWSR1::NR4A3 fusion transactivates a PPARG-promoter response element.… | PMCID PMC4429309 | `Filion 2009`, `Filion 2009, PMC4429309`, `Filion et al.` | — | IDEAS.md, fusion-object-inventory.json, nr4a3-emc-biology-evidence.md |
| `EV-PMC3335514` "The most common fusion transcript contains exon 12 of EWSR1 fused to exon 3 of NR4A3 (type 1), whereas exon 7… | PMCID PMC3335514 | `PMC3335514` | — | emc-atr-collaborator-package.md, emc-fet-construct-designs.json |
| `EV-PMC4015728` Agaram NP et al. (2014) — RT-PCR primer design: an EWSR1 exon 12 forward primer with an NR4A3 exon 3 reverse f… | PMCID PMC4015728 | `Agaram 2014`, `PMC4015728`, `PMC4015728 (Agaram 2014)` | — | emc-atr-collaborator-package.md, emc-fet-construct-designs.json |
| `EV-PMC4055444` "The most frequent are: type 1, for the fusion between exons 12 of EWS and 3 of CHN, and type 5, between exons… | PMCID PMC4055444 | `PMC4055444` | — | emc-atr-collaborator-package.md, emc-fet-construct-designs.json |
| `EV-PMC2395470` A counted series: 10 of 15 EWS/CHN tumours were exon 12 :: exon 3; 2 of 15 were type 5.… | PMCID PMC2395470 | `PMC2395470` | — | emc-atr-collaborator-package.md |
| `EV-PMC6766969` "E-N, corresponding to EWSR1 (exons 1-12)-NR4A3 (exons 3-8)"; "T-N*, corresponding to the commonest TAF15 (exo… | PMCID PMC6766969 | `PMC6766969` | — | emc-atr-collaborator-package.md, emc-fet-construct-designs.json |
| `EV-EB-TCIP-2025` EB-TCIP on EWSR1::FLI1, JACS 2025 — bivalent transcriptional chemically-induced proximity that co-opts a fusio… | DOI 10.1021/jacs.5c05634 · PMCID PMC12851799 | `EB-TCIP`, `EB-TCIP on EWSR1::FLI1, JACS 2025`, `the TCIP paper` | — | IDEAS.md, emc-post-degrader-options.md |
| `EV-PIOGLITAZONE-TRABECTEDIN-2019` Pioglitazone + trabectedin induced adipocyte differentiation and overcame trabectedin resistance in myxoid lip… | DOI 10.1158/1078-0432.CCR-19-0976 | `Clin Cancer Res 2019;25:7565`, `the pioglitazone + trabectedin paper`, `Clin Cancer Res* 2019;25:7565` | — | IDEAS.md, emc-post-degrader-options.md |
| `EV-BANGERTER-2023` Bangerter 2023 — ex-vivo drug sensitivity across two patient-derived EMC models.… | URL https://pubmed.ncbi.nlm.nih.gov/?term=Bangerter+2023+extraskeletal+myxoid+chondrosarcoma | `Bangerter 2023`, `Bangerter` | — | IDEAS.md, repurposing-hypotheses.md |
| `EV-SARC-HRD-2026` Planas-Paz L, Zehnder M, Desboeufs N, Kollar S, Chen Y, Schneebeli S, Schenk R, Schmid MP, Lopes M, Weber A, P… | PMID 41651400 · DOI 10.1016/j.canlet.2026.218300 | `PMID 41651400`, `the SARC-HRD paper`, `GSE299349`, `the HRD/ATR sarcoma programme`, `10.1016/j.canlet.2026.218300` | — | atr-hrd-sarcoma-series.json, emc-atr-vulnerability-assessment.md |

## 7 · Artifacts — which module writes them, which workflow runs it, which ref they land on

⚠ **The ref matters.** An artifact on the wrong branch is a stale fact that reads as a current one (CLAUDE.md §7). Claims are checked against **`main`**, not against the working tree.

| artifact | produced by | workflow | published to | note |
|---|---|---|---|---|
| `ART-IDR-CENSUS` `research/modalities/emc-fet-idr-census.json` | `research/modalities/emc_fet_idr_census.py` | `.github/workflows/depmap-dependency.yml` | claude/emc-treatment-alternatives-jdmiwo, main (⛔ STUB — see note) | ⛔ THE FAILURE-4 ARTIFACT. On `main` this is a 161-byte {_status, _remedy} placeholder written by the module's own network-failure path, while a document on `main` prints a full results table from it. Root cause and the one-way fix: research/modalities/artifact_stub_guard.py. A stub is detected by 'every top-level key starts with _'. |
| `ART-CONSTRUCT-DESIGNS` `research/modalities/emc-fet-construct-designs.json` | `research/modalities/emc_fet_construct_designs.py` | `.github/workflows/depmap-dependency.yml` | claude/emc-treatment-alternatives-jdmiwo | The transcript-level constructs. Holds the exon-level and residue-level definition of every reported fusion OBJECT, including the 59 UTR-encoded residues. |
| `ART-DDR-AXIS-SCAN` `research/modalities/fet-ddr-axis-scan.json` | `research/modalities/fet_ddr_axis_scan.py` | `.github/workflows/depmap-dependency.yml` | claude/emc-treatment-alternatives-jdmiwo, modalities-cache | ⚠ emc-post-degrader-options.md on the feature branch says this is 'committed on `main`'. As of this registry's authoring it is NOT on `main` — the sentence becomes true only when the branch merges. Logged as OC-3. |
| `ART-MONOVALENT-REACH` `research/modalities/nr4a3-monovalent-reach.json` | `research/modalities/nr4a3_monovalent_reach.py` | — | claude/emc-treatment-alternatives-jdmiwo | The paired monovalent-vs-bivalent reach enumeration; 18 tests. Its bivalent half replicates the committed bivalent artifact cell-for-cell. |
| `ART-FUSION-OBJECT-INVENTORY` `research/modalities/fusion-object-inventory.json` | `research/modalities/fusion_object_inventory.py` | `.github/workflows/fusion-cpu-extras.yml` | main | Sequence inventory + the 18→9 breakpoint enumeration. Its gate reproduces OBJ-MODEL-E7E3, not a reported junction. |
| `ART-TARGET-ROUTE-CENSUS` `research/modalities/target-route-census.json` | `research/modalities/target_route_census.py` | `.github/workflows/fusion-cpu-extras.yml` | main | Paralogue identity by domain, the zinc-finger window, the AF1↔LC swap measurement, and the recorded fusion_model_disagreement. |
| `ART-DECOY-NULL-LBD` `research/modalities/categorical-decoy-null-lbd.json` | `research/modalities/categorical_decoy_null.py` | `.github/workflows/categorical-decoy-null.yml` | main | The second, independently pre-registered decoy-null scope — the one that DOES contain C397. |
| `ART-APO-POSE-SITE` `research/modalities/apo-pose-site-in-regime.json` | `research/modalities/apo_pose_recovery.py` | — | main | V3's in-regime site supplement. Emits no RMSD and by its own rule cannot change the pre-registered INCONCLUSIVE. |
| `ART-ATR-VULNERABILITY` `research/modalities/emc-atr-vulnerability.json` | `research/modalities/emc_atr_vulnerability.py` | `.github/workflows/depmap-dependency.yml` | claude/emc-treatment-alternatives-jdmiwo | The computed half of the ATR route, assembled as one module. |
| `ART-PUBLISHED-WARHEAD-REGISTRY` `research/modalities/published-warhead-registry.json` | — | — | main | Where the Zaienne series is recorded WITH its PMID/PMC — i.e. the record the files carrying the ⛔ superseded, retained "Munck 2022" attribution should have been pointing at. See EV-ZAIENNE-2022's misattribution_note; the correction is retired and pinned elsewhere. |
| `ART-HLA-COVERAGE` `research/modalities/hla-coverage.json` | `research/modalities/hla_coverage.py` | — | main | Class-II coverage is a FLOOR over a tested 3-allele DR panel, and the junction it is computed on is OBJ-MODEL-E7E3. |
| `ART-ATR-HRD-SERIES` `research/modalities/atr-hrd-sarcoma-series.json` | `research/modalities/atr_hrd_sarcoma_series.py` | `.github/workflows/emc-expression-datasets.yml` | main, claude/atr-gse299349 | The sample-level characterisation of GSE299349 and the three questions it was read to answer, plus the NR4A3 identity check on the EMC-labelled model. Offline-reproducible: --check re-derives it byte-identically from the committed inputs cache. |

## 8 · Claims — a quoted figure and the one field that is its home

The registry records **where** each figure lives, never the figure. The checker resolves each field against the artifact **on `main`** and fails if it is absent, a stub, or missing the field.

| claim | document | what it quotes | its one home |
|---|---|---|---|
| `CLM-IDR-EMC` | [`emc-post-degrader-options.md`](emc-post-degrader-options.md) | route 1's RGG-retention table row for EWSR1::NR4A3 | `ART-IDR-CENSUS` → `/emc_canonical_EWSR1_NR4A3/rg_dipeptides_retained` |
| `CLM-IDR-CONTROLS` | [`emc-post-degrader-options.md`](emc-post-degrader-options.md) | the positive-control rows beside it (the fusions in which ATM suppression was MEASURED) | `ART-IDR-CENSUS` → `/positive_controls_pass` |
| `CLM-IDR-COMPARATIVE` | [`IDEAS.md`](../IDEAS.md) | the ATR route row's 'structural precondition is COMPUTED and it holds' sentence | `ART-IDR-CENSUS` → `/emc_vs_measured_fusions_comparative/rows` |
| `CLM-CONSTRUCT-FRAME` | [`emc-atr-collaborator-package.md`](emc-atr-collaborator-package.md) | §7.2 'The four constructs — all four are in frame' | `ART-CONSTRUCT-DESIGNS` → `/n_constructs_in_frame` |
| `CLM-CONSTRUCT-TCF12` | [`emc-atr-collaborator-package.md`](emc-atr-collaborator-package.md) | §7.4 'TCF12 — the negative control checked out' | `ART-CONSTRUCT-DESIGNS` → `/tcf12_negative_control` |
| `CLM-MONOVALENT-VERDICT` | [`nr4a3-monovalent-pocket-route.md`](nr4a3-monovalent-pocket-route.md) | §3 'The result' — the E3-arm-free reach enumeration | `ART-MONOVALENT-REACH` → `/verdict/answer_on_the_conservative_convention` |
| `CLM-MONOVALENT-CROSSCHECK` | [`nr4a3-monovalent-pocket-route.md`](nr4a3-monovalent-pocket-route.md) | §3 'its bivalent half replicates the committed artifact cell-for-cell' | `ART-MONOVALENT-REACH` → `/cross_checks` |
| `CLM-ATRI-GDSC` | [`emc-post-degrader-options.md`](emc-post-degrader-options.md) | the ATRi-contrast section — the GDSC2 re-cut by FET status | `ART-DDR-AXIS-SCAN` → `/atr_inhibitor_sensitivity_gdsc/by_drug` |
| `CLM-KO-SATURATION` | [`emc-post-degrader-options.md`](emc-post-degrader-options.md) | the DepMap knockout scan reported as a FAILED instrument | `ART-DDR-AXIS-SCAN` → `/knockout_instrument_saturation` |
| `CLM-FUSION-MODEL-DISAGREEMENT` | [`target-route-options.md`](target-route-options.md) | §1.3 'the repo held two incompatible models of the fusion protein' | `ART-TARGET-ROUTE-CENSUS` → `/fusion_model_disagreement` |
| `CLM-AF1-LC-SWAP` | [`emc-post-degrader-options.md`](emc-post-degrader-options.md) | the 6-MP closure — 'NOR-1 residues 1–112 sit entirely inside the stretch the fusion replaces' | `ART-TARGET-ROUTE-CENSUS` → `/af1_to_lc_swap` |
| `CLM-BREAKPOINT-FILTER` | [`fusion-object-inventory.md`](../modalities/fusion-object-inventory.md) | 'Which chimeras are possible, and which are plausible' | `ART-FUSION-OBJECT-INVENTORY` → `/plausible_breakpoints/n_after_DBD_filter` |
| `CLM-C397-DECOY-NULL` | [`nr4a3-program-map.md`](nr4a3-program-map.md) | V17's row — the second, independently pre-registered decoy-null scope that DOES contain C397 | `ART-DECOY-NULL-LBD` → `/results` |
| `CLM-APO-SITE-IN-REGIME` | [`nr4a3-program-map.md`](nr4a3-program-map.md) | V3's row — the in-regime site panel by two independent transfer routes | `ART-APO-POSE-SITE` → `/site_panel_in_regime` |
| `CLM-ATR-HRD-COMPETING-BIOMARKER` | [`emc-atr-vulnerability-assessment.md`](emc-atr-vulnerability-assessment.md) | §8.2 Q3 and §8.4 -- 'a 2026 sarcoma ATR programme selects on HRD, not FET status' | `ART-ATR-HRD-SERIES` → `/q3_selection_biomarker/answer` |
| `CLM-ATR-HRD-EMC-SAMPLE` | [`emc-atr-vulnerability-assessment.md`](emc-atr-vulnerability-assessment.md) | §8.2 Q2 -- GSM9037837 / USZ-23_EMC3, the first EMC sample in an ATR-directed dataset | `ART-ATR-HRD-SERIES` → `/q2_emc_or_nr4a3_sample/samples_with_a_strong_EMC_or_NR4A3_term` |
| `CLM-ATR-HRD-NO-RESPONSE-DATA` | [`emc-atr-vulnerability-assessment.md`](emc-atr-vulnerability-assessment.md) | §8.2 Q1 -- the deposit supplies no ATR-inhibitor response readout | `ART-ATR-HRD-SERIES` → `/q1_atr_inhibitor_response_data/n_samples_with_a_NON_EMPTY_treatment_protocol_field` |

## 9 · ⭐ THE WATCH LIST — what would revive what, highest-leverage first

**Why this section is the point of the whole registry.** Many of these paths will be unblocked, and a register that files *a fact about a sequence* beside *a limitation of today's free-energy engine* under one word — "closed" — has destroyed the only distinction that decides what to watch for. So `closure_kind` is an enumerated field, and every non-permanent closure names, in searchable words, what has to land.

⭐ **Ordered by how many routes and instruments each trigger revives** — the top rows are the highest-leverage advances to watch for. Each `trigger` string is written to be usable **verbatim as a literature-search query**.

| # revived | trigger | what it would reopen | on the watch list? |
|---|---|---|---|
| **13** | **a free-energy method (FEP or ML free-energy) validated on cryptic / induced-fit pockets — an ABFE or RBFE engine that reproduces a public known-answer benchmark to within 1 kcal/mol on a pocket absent from the apo structure** <br>*The program's ABFE engine under-binds T4-lysozyme L99A/benzene by more than the entire selectivity margin it is used to compute, and the FEP tier the degrader needs is least reliable on exactly the cryptic, induced-fit pocket this target presents.* | `V4`, `V7`, `V9`, `R7`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-GLUE`, `RT-ANDGATE`, `RT-RIPTAC`, `RT-TCIP` | ✅ yes |
| **11** | **a fetchable public EMC RNA-seq or proteomics dataset deposited beyond the single DepMap model ACH-001519, enabling an NR4A3-target regulon-dominance readout and a per-antigen expression confirm on real EMC tissue** <br>*EMC is nearly absent from public functional-genomics data and the one line is n = 1 with no CRISPR data — the repo-wide rate-limiter. It is a DATA trigger, not a method one, and it fans out across every route whose in-silico half is bounded by n = 1.* | `RT-SYNLETH-DEP`, `RT-PPARG-DOWNSTREAM`, `RT-TRABECTEDIN-PPARG`, `RT-B7H3`, `RT-SSTR2`, `RT-PRAME-IMMTAC`, `RT-CART-SURFACE`, `RT-FAP-RLT`, `RT-CARFILZOMIB` | ✅ yes |
| **11** | **access to a patient-derived EMC model (NCC-EMC1-C1, USZ-EMC, or an authenticated H-EMC-SS) through a collaborator or a solo-affordable cloud/robotic wet-lab service with EMC-runnable scope** <br>*The cell-line repositories exclude individuals by published policy rather than by price, so every confirm-gated EMC row is gated on a collaborator and no budget reaches it. This trigger is about ACCESS, and it is the single highest-fan-out non-method trigger in the portfolio.* | `RT-ATR-PANEL`, `RT-ASO-ASK`, `RT-TRABECTEDIN-PPARG`, `RT-SSTR2`, `RT-COVALENT-PROBE`, `RT-SYNLETH-DEP`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-PPARG-DOWNSTREAM`, `RT-CARFILZOMIB`, `R4` | ✅ yes |
| **7** | **generative equilibrium-ensemble models (BioEmu, AlphaFlow, subsampled-MSA AlphaFold) validated against known cryptic pockets — recovering CryptoSite/PocketMiner benchmark sites without GPU-days of metadynamics** <br>*It collapses the per-target 'open the pocket' cost from GPU-days to pennies, which is what decides whether the cryptic-pocket druggability atlas is a focused target class or proteome-scale. ⚠ Its (a) arm already fired 2026-07-24; the calibration half has not.* | `V13`, `V14`, `R1`, `R2`, `R6`, `RT-DEGRADER`, `RT-MONOVALENT` | ✅ yes |
| **7** | **a pose-prediction protocol whose site transfer places the crystallographic ligand inside its own box in regime, and on which two scoring-independent methods converge in ORIENTATION as well as location on the same receptors** <br>*Two independent transfer routes both put the site at zero in regime, and two disjoint scoring functions disagree in orientation at a median far above their centroid separation — so the non-convergence is the system's, and a single better docker is not the trigger.* | `V3`, `V22`, `R5`, `R8`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-COVALENT-PROBE` | ⚠ **no — nobody is scanning for it** |
| **5** | **a sequence-only co-folder evaluated on ternary ASSEMBLY — inter-chain DockQ on post-training-horizon PROTAC ternaries — rather than on per-chain pocket accuracy** <br>*Boltz-2 failing is not the class failing: the same harness already recognises a correct ternary when both sites are given (DeepTernary reaches DockQ 0.839 on the same interface), so the plumbing is not what missed.* | `V12`, `R10`, `RT-DEGRADER`, `RT-ANDGATE`, `RT-AF3-INTERFACE` | ✅ yes |
| **5** | **a solvent-exposure or thiol-reactivity criterion that recovers NR4A1 C551 as engageable on a state-matched opened model — i.e. an exposure instrument that passes the one NR4A-family covalent positive control with literature support** <br>*The standing EXPOSED_RSA cutoff fails that positive control, so anything it adjudicates inherits a demonstrated false negative and only a threshold-free rank survives. A criterion that passes it makes the covalent screen readable again rather than rank-only.* | `V17`, `R8`, `R15`, `RT-COVALENT-PROBE`, `RT-MONOVALENT` | ⚠ **no — nobody is scanning for it** |
| **5** | **fusion-breakpoint-neoantigens.json regenerated against the corrected exon index, so that every predicted peptide-HLA binder spans a seam that a reported junction actually produces** <br>*The predicted binders currently span seams that do not exist, which is a defect of the input index rather than of the prediction method — so the trigger is a regeneration, and it is free.* | `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE`, `RT-TCR-IMMTAC` | ⚠ **no — nobody is scanning for it** |
| **5** | **an oligonucleotide tumour-delivery technology reaching non-hepatic solid tumours — an AOC/conjugate, tumour-penetrating peptide or ligand-targeted LNP platform — OR a characterised EMC-enriched surface antigen to serve as its targeting arm** <br>*Delivery is the ASO route's one remaining gate and it is engineering rather than biology, so it is watched two ways: a delivery PREDICTOR to score a candidate in silico, and a delivery TECHNOLOGY to be that candidate.* | `RT-ASO`, `RT-ASO-ASK`, `RT-CRISPR-CAS13`, `RT-RIBOZYME`, `RT-SYNPROMOTER` | ✅ yes |
| **4** | **a validated charge-change correction for alchemical free-energy edges — a co-alchemical-ion or PME finite-size treatment demonstrated to reproduce a known-answer set of charge-changing transformations** <br>*Charge-changing edges block legs of the step-1 fan-out and killed the high-contrast calibrator route. ⚠ The correction reopens the EDGES, not the P-series DESIGN, which stays a poor calibrator on perturbation size alone.* | `V5`, `V6`, `R7`, `R11` | ⚠ **no — nobody is scanning for it** |
| **4** | **a validated prospective molecular-glue design method or glue-interface selectivity predictor, demonstrated on a CRBN or DCAF neosubstrate interface that was not in its training set** <br>*A glue has no linker, so it has no covalent axis and no designed exit vector — the modality most likely to arrive from someone else's screen rather than from this program's design, which is why it is a watch trigger rather than a build item.* | `RT-GLUE`, `R7`, `R9`, `R10` | ✅ yes |
| **4** | **an OBSERVED rather than COMPOSED CRL RING / E2~Ub geometry — a deposited cryo-EM or crystallographic full-assembly structure that replaces a composed model carrying tens of angstroms of positional uncertainty** <br>*No degradation-geometry claim may rest on a RING or E2 that was composed rather than observed, and the E3-choice selectivity readout is not stable under restaging — both are statements about the geometry's provenance, which only an observed assembly changes.* | `V18`, `R12`, `RT-UBIQ-SELECTIVE`, `RT-DEGRADER` | ⚠ **no — nobody is scanning for it** |
| **4** | **a ternary alchemical free-energy method that PASSES the valB known-answer cooperativity control — recovering the reference ΔΔG_coop with the correct sign, not merely with more sampling of the present protocol** <br>*The closure triangle localises the present miss to an ENDPOINT-STATE error, which is a property of the model or the reference data; more sampling of the same endpoints cannot fix it.* | `V5`, `R11`, `RT-DEGRADER`, `RT-ANDGATE` | ⚠ **no — nobody is scanning for it** |
| **3** | **trimcrae authorizing the CREBBP versus BRD4(1) / SGC-CBP30 selectivity ABFE — the program's only binary selectivity control and its highest-leverage unrun item** <br>*Nothing failed and nothing is missing; it is built and staged with no result key. This is an authorization, not a capability — it could run tomorrow.* | `V4`, `R7`, `RT-DEGRADER` | ⚠ **no — nobody is scanning for it** |
| **3** | **an anti-target docking protocol in which every panel receptor recovers its own cognate crystallographic ligand inside the pre-registered 2.0 Angstrom criterion, with no receptor dropped, no box re-centred and no band lowered** <br>*Three of ten receptors miss, so `panel_readable` is false and all four SI scope clauses that are maximum-over-the-panel statements are unreadable. A failing target may not be dropped, which is what makes this a protocol trigger rather than a curation one.* | `V21`, `R14`, `RT-DEGRADER` | ⚠ **no — nobody is scanning for it** |
| **3** | **an atom mapper that reaches the 20-atom provable floor on the 19th congeneric edge WITHOUT a degenerate correspondence — i.e. without mapping a carbon onto a hydrogen** <br>*The best available map reaches 19 and the search budget is provably not binding (identical maps at t20 and t300), so more search time buys nothing; the one map that does reach 20 gets there by a chemically impossible correspondence.* | `V6`, `R7`, `RT-DEGRADER` | ⚠ **no — nobody is scanning for it** |
| **3** | **an interface-stability readout with power at achievable sampling, OR a different test system whose interface effect is large enough for the E1 endpoint to resolve** <br>*Two independent attempts returned no pass, the second on an adequately powered design — so the block is the readout's resolution against this system's effect size, not the sample size. ⚠ Two failures is strong evidence, not proof of impossibility.* | `V11`, `R11`, `RT-DEGRADER` | ⚠ **no — nobody is scanning for it** |
| **3** | **a deposited partner-free liganded structure for one of the blocked E3 recruiters (RNF114, DCAF16, DCAF15) — a handle pocket rather than a glue interface** <br>*Availability was the wrong constraint; structural stageability binds. RNF114 has no deposited structure at all and DCAF16's ligand is largely buried once its partner is removed.* | `R9`, `R12`, `RT-DEGRADER` | ⚠ **no — nobody is scanning for it** |
| **3** | **a paralogue-selectivity positive control whose selectivity is reproduced by a NON-covalent readout — i.e. not attributable to a covalent bond at a residue the off-target paralogues lack. A different test system, not more sampling of NR-V04** <br>*NR-V04's geometry readout passes for the wrong reason, and no sample size and no better method fixes a confound in the system. Only a different control compound or a different system does.* | `R7`, `R11`, `RT-DEGRADER` | ⚠ **no — nobody is scanning for it** |
| **2** | **a re-run of the ternary generation from a logged, bond-order-complete ligand definition — the QUESTION re-answered on a recorded input, never a recovery of the unrecoverable original result** <br>*⚠ THE DISTINCTION THIS REPO HAS CONFLATED. The specific artifact can never be replicated by anyone, us included, because the molecule folded is unrecoverable; the question it was asked of is open and is answerable on a properly logged input.* | `R10`, `RT-DEGRADER` | ⚠ **no — nobody is scanning for it** |
| **1** | **a primary report of NR4A3/NOR-1 forming a permissive or ligand-modulable heterodimer with RXR in cells, contradicting the published negative that NOR-1 is unable to promote RXR signaling** <br>*The whole closure turns on one measured biological fact about this receptor, so only a contradicting primary measurement of that same fact reopens it — no method advance does.* | `RT-RXR` | ⚠ **no — nobody is scanning for it** |
| **1** | **the TCIP-configuration linker enumeration executed — the same paired anchor-plus-effector-recruiter reach calculation already built for the E3-free configuration, run with a transcriptional-effector second terminus** <br>*A TCIP is still bivalent, so the monovalent result does not transfer; the machinery exists and takes one more anchor set, which makes this the cheapest promotion available in the options memo.* | `RT-TCIP` | ⚠ **no — nobody is scanning for it** |

### 9a · Every closure, by KIND — and which are permanent

⛔ **A `definitional` or `arithmetic_over_fixed_fact` closure is permanent and may carry NO revival trigger** — a fact about what the objects *are* is not waiting on a method. ⭐ **`instrument_limit` is the most revivable kind and is where most of this program's failures actually sit.** `permanently closed` below is DERIVED from the kind, never typed.

**`open`** — revivable. not closed at all

| id | kind | permanently closed (derived) | revival trigger(s) | would reopen (derived) |
|---|---|---|---|---|
| `INS-CONSTRUCT-DESIGNS` Transcript-level fusion construct designer (frame computed at the nucl | open | no | — | — |
| `INS-DDR-AXIS-SCAN` ATRi/PARPi sensitivity re-cut by FET status (GDSC2) | open | no | — | — |
| `INS-FUSION-OBJECT-INVENTORY` Fusion object sequence inventory + breakpoint enumeration | open | no | — | — |
| `INS-GEO-SERIES-CHARACTERISE` Sample-level GEO series characterisation + disease-label corroboration | open | no | — | — |
| `INS-IDR-CENSUS` FET N-terminal IDR / RGG retention census | open | no | — | — |
| `INS-MONOVALENT-REACH` Paired monovalent-vs-bivalent covalent reach enumeration (E3 arm remov | open | no | — | — |
| `RT-ASO` Fusion-junction ASO / siRNA (the deliverable) | open | no | — | — |
| `RT-ASYMMETRIC` Asymmetric selectivity — NR4A1-sparing mandatory, NR4A2-sparing best-e | open | no | — | — |
| `RT-ATR-ASSESS` The in-silico ATR vulnerability assessment (the computed half) | open | no | — | — |
| `RT-CARFILZOMIB` Carfilzomib ± anthracycline (± venetoclax) | open | no | — | — |
| `RT-FAP-RLT` FAP-targeted radioligand therapy (FAPI-RLT) | open | no | — | — |
| `RT-ICI-TKI` Checkpoint inhibitor + anti-angiogenic TKI combination | open | no | — | — |
| `RT-METHODS-PAPER` The honest methods paper on the degrader program's own failure record | open | no | — | — |
| `RT-PANNR4A-EXVIVO` Ex-vivo pan-NR4A pole (CAR-T manufacturing additive) | open | no | — | — |
| `RT-PRAME-IMMTAC` PRAME-directed brenetafusp (ImmTAC) / PRAME CAR-TCR | open | no | — | — |
| `RT-TRABECTEDIN` Trabectedin (± RT or combination) | open | no | — | — |
| `V1` Structural selectivity descriptor (selcal_interface_signature) | open | no | — | — |
| `V15` PocketMiner + four permutation nulls | open | no | — | — |
| `V2` Ternary generator given both sites (assembly route) | open | no | — | — |
| `V8` ABFE engine, hydration | open | no | — | — |

- `RT-ASO` — Its gate is delivery, which is engineering rather than a closure.
- `RT-ASYMMETRIC` — Adopted, free, and it changes the design brief.
- `RT-ATR-ASSESS` — Computed and complete on its own axis; its limit is stated inside the deliverable.
- `RT-CARFILZOMIB` — Best ex-vivo EMC evidence; nothing closed.
- `RT-FAP-RLT` — Emerging and unmeasured in EMC.
- `RT-ICI-TKI` — Approved drugs and the best EMC clinical signal on the board.
- `RT-METHODS-PAPER` — Nothing blocks it; it is finished when we stop typing.
- `RT-PANNR4A-EXVIVO` — It removes the selectivity requirement by changing the exposure regime; nothing is closed.
- `RT-PRAME-IMMTAC` — The one CTA whose surrogate expression came back favourable; its confirm is an ask, not a closure.
- `RT-TRABECTEDIN` — An approved drug with a reported EMC responder; nothing about it is closed.

**`definitional`** — ⛔ **PERMANENT — never revivable**. a fact about what the objects ARE — e.g. a residue the paralogues SHARE cannot discriminate between them, or a ligand whose mechanism lives in a domain the disease deletes. NEVER revivable.

| id | kind | permanently closed (derived) | revival trigger(s) | would reopen (derived) |
|---|---|---|---|---|
| `RT-6MP` 6-mercaptopurine / AF-1 agonism of the fusion | definitional | **yes** | — | — |
| `RT-EWSR1-PROTEIN` Target the EWSR1 half at the protein level | definitional | **yes** | — | — |
| `RT-FET-LC-LIGAND` A ligand for the shared FET low-complexity half | definitional | **yes** | — | — |
| `RT-HDAC-BET` HDAC / BET to lower fusion expression | definitional | **yes** | — | — |

- `RT-6MP` — 6-MP acts through the AF-1, and the fusion REPLACES the AF-1 with EWSR1's low-complexity region. A ligand whose whole mechanism lives in a domain the disease deletes cannot act on the chimera at any dose. ⚠ Scoped: this closes 6-MP, NOT LBD-directed modulation.
- `RT-EWSR1-PROTEIN` — The EWSR1 half of the fusion IS wild-type EWSR1 sequence, so a ligand for it engages an essential housekeeping protein BY CONSTRUCTION. No method changes what the sequence is.
- `RT-FET-LC-LIGAND` — A ligand for the SHARED FET low-complexity half binds wild-type EWSR1 by definition of 'shared'. Permanent for the same reason as the row above, reached from the other direction.
- `RT-HDAC-BET` — A class effect on fusion EXPRESSION is not fusion-selective by construction — the mechanism does not distinguish the chimera from anything else the class regulates.

**`arithmetic_over_fixed_fact`** — ⛔ **PERMANENT — never revivable**. an arithmetic consequence of a fixed measured fact — e.g. the zinc-finger DBD's paralogue identity against the LBD's. NEVER revivable.

| id | kind | permanently closed (derived) | revival trigger(s) | would reopen (derived) |
|---|---|---|---|---|
| `RT-DBD` Target the DBD / DNA binding | arithmetic_over_fixed_fact | **yes** | — | — |
| `V20` Single-snapshot MM-GBSA margin > 0 as a selectivity verdict | arithmetic_over_fixed_fact | **yes** | — | — |

- `RT-DBD` — The zinc-finger DBD is far more conserved between the paralogues than the LBD the program already targets. An arithmetic consequence of a fixed sequence fact — never revivable.
- `V20` — 38 unrelated marketed drugs score a positive margin through the identical funnel, above the de-novo set's own rate. A signal smaller than its own noise is not recoverable by any downstream method — an arithmetic consequence of a measured null distribution, and the reason §6a files it never-retry.

**`premise_false`** — revivable. a stated premise was measured and is not true. Revivable only if the measurement or the underlying fact changes.

| id | kind | permanently closed (derived) | revival trigger(s) | would reopen (derived) |
|---|---|---|---|---|
| `INS-DEPMAP-KO` DepMap CRISPR-knockout dependency scan of the ATR axis | premise_false | no | `TR-EMC-EXPRESSION-DATASET` | `RT-SYNLETH-DEP`, `RT-PPARG-DOWNSTREAM`, `RT-TRABECTEDIN-PPARG`, `RT-B7H3`, `RT-SSTR2`, `RT-PRAME-IMMTAC`, `RT-CART-SURFACE`, `RT-FAP-RLT`, `RT-CARFILZOMIB` |
| `INS-FUSION-COFOLD` Fusion protein-level co-folding model | premise_false | no | `TR-NEOANTIGEN-SEAMS-REGENERATED` | `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE`, `RT-TCR-IMMTAC` |
| `RT-B7H3` B7-H3 (CD276) / CD56 → ADC, bispecific or CAR-T | premise_false | no | `TR-EMC-EXPRESSION-DATASET`, `TR-EMC-MODEL-ACCESS` | `RT-SYNLETH-DEP`, `RT-PPARG-DOWNSTREAM`, `RT-TRABECTEDIN-PPARG`, `RT-B7H3`, `RT-SSTR2`, `RT-PRAME-IMMTAC`, `RT-CART-SURFACE`, `RT-FAP-RLT`, `RT-CARFILZOMIB`, `RT-ATR-PANEL`, `RT-ASO-ASK`, `RT-COVALENT-PROBE`, `R4` |
| `RT-PPARG-DOWNSTREAM` PPARG downstream-effector (repurpose TZDs) | premise_false | no | `TR-EMC-EXPRESSION-DATASET` | `RT-SYNLETH-DEP`, `RT-PPARG-DOWNSTREAM`, `RT-TRABECTEDIN-PPARG`, `RT-B7H3`, `RT-SSTR2`, `RT-PRAME-IMMTAC`, `RT-CART-SURFACE`, `RT-FAP-RLT`, `RT-CARFILZOMIB` |
| `RT-RXR` RXR-heterodimer modulation of the fusion | premise_false | no | `TR-NR4A3-RXR-HETERODIMER-REPORT` | `RT-RXR` |
| `RT-SYNLETH-DEP` Synthetic-lethal / dependency partner (BRD9 / ncBAF via EWSR1-prion→BA | premise_false | no | `TR-EMC-EXPRESSION-DATASET`, `TR-EMC-MODEL-ACCESS` | `RT-SYNLETH-DEP`, `RT-PPARG-DOWNSTREAM`, `RT-TRABECTEDIN-PPARG`, `RT-B7H3`, `RT-SSTR2`, `RT-PRAME-IMMTAC`, `RT-CART-SURFACE`, `RT-FAP-RLT`, `RT-CARFILZOMIB`, `RT-ATR-PANEL`, `RT-ASO-ASK`, `RT-COVALENT-PROBE`, `R4` |
| `RT-SYNPROMOTER` Fusion-driven synthetic promoter → suicide gene | premise_false | no | `TR-OLIGO-TUMOUR-DELIVERY` | `RT-ASO`, `RT-ASO-ASK`, `RT-CRISPR-CAS13`, `RT-RIBOZYME`, `RT-SYNPROMOTER` |
| `RT-TCR-IMMTAC` Fusion-junction TCR-T / soluble-TCR (ImmTAC) against the junction pept | premise_false | no | `TR-NEOANTIGEN-SEAMS-REGENERATED` | `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE`, `RT-TCR-IMMTAC` |
| `RT-TCRT-CTA` TCR-T / engineered T cells vs a cancer-testis antigen (synovial-sarcom | premise_false | no | `TR-EMC-EXPRESSION-DATASET` | `RT-SYNLETH-DEP`, `RT-PPARG-DOWNSTREAM`, `RT-TRABECTEDIN-PPARG`, `RT-B7H3`, `RT-SSTR2`, `RT-PRAME-IMMTAC`, `RT-CART-SURFACE`, `RT-FAP-RLT`, `RT-CARFILZOMIB` |
| `RT-VACCINE` Fusion-junction vaccine / HLA-coverage paper | premise_false | no | `TR-NEOANTIGEN-SEAMS-REGENERATED` | `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE`, `RT-TCR-IMMTAC` |

- `RT-B7H3` — The selectivity premise was MEASURED and failed on cell-line surrogates; real EMC tissue is what could change the measurement.
- `RT-PPARG-DOWNSTREAM` — ⚠ Scoped: the DIRECTION is unresolved, not refuted — in EMC the fusion turns PPARG on, so an agonist may be redundant. An EMC expression read settles it either way.
- `RT-RXR` — Closed on the receptor's own measured biology. Not definitional — it rests on a published measurement, so a contradicting primary measurement is the only thing that reopens it, and no method advance does.
- `RT-SYNLETH-DEP` — The DepMap transfer prior came back negative — a measured premise, revivable only by EMC-specific data, which is why it is parked on data and not on ideas.
- `RT-SYNPROMOTER` — ⭐ EMC lacks the neomorphic DNA-binding element the technique depends on — a measured premise about EMC's fusion, and the reason it fails is itself a computed EMC result worth publishing.
- `RT-TCR-IMMTAC` — The weak-junction peptide-HLA problem is a measured property of this junction, not of the modality.
- `RT-TCRT-CTA` — EMC is CTA-low on measured data; a real EMC series is what could change it.
- `RT-VACCINE` — Parked on immunogenicity — a self-adjacent junction in a cold tumour — and its HLA-coverage output is reusable and still feeds TCR-T eligibility.

**`unregenerable_artifact`** — revivable. ⚠ THE TWO HALVES THIS REPO HAS CONFLATED: the specific RESULT is unrecoverable forever, and the QUESTION it was asked of is OPEN. The trigger is what re-answers the question, never what recovers the result.

| id | kind | permanently closed (derived) | revival trigger(s) | would reopen (derived) |
|---|---|---|---|---|
| `RT-JUNCTION-NEOANTIGEN` Fusion-junction neoantigen (the antigen, shared by three delivery rout | unregenerable_artifact | no | `TR-NEOANTIGEN-SEAMS-REGENERATED` | `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE`, `RT-TCR-IMMTAC` |

- `RT-JUNCTION-NEOANTIGEN` — ⚠ THE TWO HALVES, KEPT APART: the 26 predicted binders are unusable because they span seams that do not exist — that RESULT is void. The QUESTION is open and one free regeneration answers it.

**`instrument_limit`** — revivable. ⭐ THE METHOD CANNOT RESOLVE IT TODAY — the most revivable category and the one most of this program's failures actually fall into. Filing these beside a definitional impossibility is precisely the information loss this field exists to prevent.

| id | kind | permanently closed (derived) | revival trigger(s) | would reopen (derived) |
|---|---|---|---|---|
| `INS-HLA-COVERAGE` HLA population-coverage calculator | instrument_limit | no | `TR-NEOANTIGEN-SEAMS-REGENERATED` | `RT-JUNCTION-NEOANTIGEN`, `RT-VACCINE`, `RT-TCR-IMMTAC` |
| `RT-AF3-INTERFACE` AF3 on a druggable interface | instrument_limit | no | `TR-COFOLD-ASSEMBLY` | `V12`, `R10`, `RT-DEGRADER`, `RT-ANDGATE`, `RT-AF3-INTERFACE` |
| `RT-ANDGATE` AND-gate bivalent degrader (avidity coincidence detection) | instrument_limit | no | `TR-TERNARY-ALCHEMY-PASSES-VALB`, `TR-COFOLD-ASSEMBLY` | `V5`, `R11`, `RT-DEGRADER`, `RT-ANDGATE`, `V12`, `R10`, `RT-AF3-INTERFACE` |
| `RT-CART-SURFACE` CAR-T for EMC (surface-directed) | instrument_limit | no | `TR-EMC-EXPRESSION-DATASET`, `TR-EMC-MODEL-ACCESS` | `RT-SYNLETH-DEP`, `RT-PPARG-DOWNSTREAM`, `RT-TRABECTEDIN-PPARG`, `RT-B7H3`, `RT-SSTR2`, `RT-PRAME-IMMTAC`, `RT-CART-SURFACE`, `RT-FAP-RLT`, `RT-CARFILZOMIB`, `RT-ATR-PANEL`, `RT-ASO-ASK`, `RT-COVALENT-PROBE`, `R4` |
| `RT-COVALENT-PROBE` Covalent probe at C397 — as a REAGENT, not a drug | instrument_limit | no | `TR-EXPOSURE-CRITERION-RECOVERS-C551`, `TR-POSE-METHODS-CONVERGE`, `TR-EMC-MODEL-ACCESS` | `V17`, `R8`, `R15`, `RT-COVALENT-PROBE`, `RT-MONOVALENT`, `V3`, `V22`, `R5`, `RT-DEGRADER`, `RT-ATR-PANEL`, `RT-ASO-ASK`, `RT-TRABECTEDIN-PPARG`, `RT-SSTR2`, `RT-SYNLETH-DEP`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-PPARG-DOWNSTREAM`, `RT-CARFILZOMIB`, `R4` |
| `RT-CRISPR-CAS13` CRISPR/Cas9 intron-targeted fusion disruption; Cas13 fusion-RNA knockd | instrument_limit | no | `TR-OLIGO-TUMOUR-DELIVERY` | `RT-ASO`, `RT-ASO-ASK`, `RT-CRISPR-CAS13`, `RT-RIBOZYME`, `RT-SYNPROMOTER` |
| `RT-DEGRADER` NR4A3-LBD PROTAC degrader | instrument_limit | no | `TR-FE-CRYPTIC-POCKET`, `TR-COFOLD-ASSEMBLY`, `TR-TERNARY-ALCHEMY-PASSES-VALB`, `TR-ABFE-AUTHORIZATION` | `V4`, `V7`, `V9`, `R7`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-GLUE`, `RT-ANDGATE`, `RT-RIPTAC`, `RT-TCIP`, `V12`, `R10`, `RT-AF3-INTERFACE`, `V5`, `R11` |
| `RT-GLUE` Molecular glue instead of a PROTAC | instrument_limit | no | `TR-GLUE-DESIGN-PREDICTOR`, `TR-FE-CRYPTIC-POCKET` | `RT-GLUE`, `R7`, `R9`, `R10`, `V4`, `V7`, `V9`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-ANDGATE`, `RT-RIPTAC`, `RT-TCIP` |
| `RT-MONOVALENT` Monovalent LBD pocket modulation — a molecule that only OCCUPIES the N | instrument_limit | no | `TR-FE-CRYPTIC-POCKET`, `TR-EXPOSURE-CRITERION-RECOVERS-C551`, `TR-POSE-METHODS-CONVERGE` | `V4`, `V7`, `V9`, `R7`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-GLUE`, `RT-ANDGATE`, `RT-RIPTAC`, `RT-TCIP`, `V17`, `R8`, `R15`, `RT-COVALENT-PROBE`, `V3`, `V22`, `R5` |
| `RT-RIBOZYME` Trans-splicing ribozyme → suicide gene, triggered by the fusion transc | instrument_limit | no | `TR-OLIGO-TUMOUR-DELIVERY` | `RT-ASO`, `RT-ASO-ASK`, `RT-CRISPR-CAS13`, `RT-RIBOZYME`, `RT-SYNPROMOTER` |
| `RT-RIPTAC` RIPTAC — bind the tumour protein, poison an essential one | instrument_limit | no | `TR-FE-CRYPTIC-POCKET` | `V4`, `V7`, `V9`, `R7`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-GLUE`, `RT-ANDGATE`, `RT-RIPTAC`, `RT-TCIP` |
| `RT-TCIP` TCIP — transcriptional chemically-induced proximity on EWSR1::NR4A3 | instrument_limit | no | `TR-TCIP-LINKER-ENUMERATION`, `TR-FE-CRYPTIC-POCKET` | `RT-TCIP`, `V4`, `V7`, `V9`, `R7`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-GLUE`, `RT-ANDGATE`, `RT-RIPTAC` |
| `RT-UBIQ-SELECTIVE` Fusion-selective ubiquitination — discriminate at the transfer step | instrument_limit | no | `TR-OBSERVED-CRL-GEOMETRY` | `V18`, `R12`, `RT-UBIQ-SELECTIVE`, `RT-DEGRADER` |
| `V10` Interface-mutation physics (pmx/GROMACS) | instrument_limit | no | `TR-FE-CRYPTIC-POCKET` | `V4`, `V7`, `V9`, `R7`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-GLUE`, `RT-ANDGATE`, `RT-RIPTAC`, `RT-TCIP` |
| `V11` Interface-stability endpoint (E1) | instrument_limit | no | `TR-E1-POWERED-SYSTEM` | `V11`, `R11`, `RT-DEGRADER` |
| `V12` Sequence-only co-folding (Boltz-2 ternary) | instrument_limit | no | `TR-COFOLD-ASSEMBLY` | `V12`, `R10`, `RT-DEGRADER`, `RT-ANDGATE`, `RT-AF3-INTERFACE` |
| `V13` Cryptic-opening free-energy profile (metadynamics F(Rg)) | instrument_limit | no | `TR-CHEAP-CRYPTIC-ENSEMBLE` | `V13`, `V14`, `R1`, `R2`, `R6`, `RT-DEGRADER`, `RT-MONOVALENT` |
| `V14` BioEmu unbiased ensemble cross-check | instrument_limit | no | `TR-CHEAP-CRYPTIC-ENSEMBLE` | `V13`, `V14`, `R1`, `R2`, `R6`, `RT-DEGRADER`, `RT-MONOVALENT` |
| `V16` The causal matched-pair test S (RUNG 5a-KS) | instrument_limit | no | `TR-FE-CRYPTIC-POCKET` | `V4`, `V7`, `V9`, `R7`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-GLUE`, `RT-ANDGATE`, `RT-RIPTAC`, `RT-TCIP` |
| `V17` The exposure criterion EXPOSED_RSA = 0.25 | instrument_limit | no | `TR-EXPOSURE-CRITERION-RECOVERS-C551` | `V17`, `R8`, `R15`, `RT-COVALENT-PROBE`, `RT-MONOVALENT` |
| `V18` The transfer-zone lysine-identity term | instrument_limit | no | `TR-OBSERVED-CRL-GEOMETRY` | `V18`, `R12`, `RT-UBIQ-SELECTIVE`, `RT-DEGRADER` |
| `V19` The generation-matched null (winner's-curse / generative confound) | instrument_limit | no | `TR-FE-CRYPTIC-POCKET` | `V4`, `V7`, `V9`, `R7`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-GLUE`, `RT-ANDGATE`, `RT-RIPTAC`, `RT-TCIP` |
| `V21` The anti-target docking panel (antitarget_dock) | instrument_limit | no | `TR-ANTITARGET-PANEL-RECOVERS` | `V21`, `R14`, `RT-DEGRADER` |
| `V22` The scoring-independent second pose method (rDock) | instrument_limit | no | `TR-POSE-METHODS-CONVERGE` | `V3`, `V22`, `R5`, `R8`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-COVALENT-PROBE` |
| `V3` Ligand pose prediction (dock + MM-GBSA) | instrument_limit | no | `TR-POSE-METHODS-CONVERGE` | `V3`, `V22`, `R5`, `R8`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-COVALENT-PROBE` |
| `V5` Alchemical ternary cooperativity (valB_mini ΔΔG_coop) | instrument_limit | no | `TR-TERNARY-ALCHEMY-PASSES-VALB`, `TR-CHARGE-CHANGE-CORRECTION` | `V5`, `R11`, `RT-DEGRADER`, `RT-ANDGATE`, `V6`, `R7` |
| `V6` Relative FEP (OpenFE, the congeneric lane) | instrument_limit | no | `TR-ATOM-MAPPER-FLOOR`, `TR-CHARGE-CHANGE-CORRECTION` | `V6`, `R7`, `RT-DEGRADER`, `V5`, `R11` |
| `V7` ABFE engine, absolute | instrument_limit | no | `TR-FE-CRYPTIC-POCKET` | `V4`, `V7`, `V9`, `R7`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-GLUE`, `RT-ANDGATE`, `RT-RIPTAC`, `RT-TCIP` |
| `V9` λ-overlap diagnostic on the standing ABFE block | instrument_limit | no | `TR-FE-CRYPTIC-POCKET` | `V4`, `V7`, `V9`, `R7`, `RT-DEGRADER`, `RT-MONOVALENT`, `RT-GLUE`, `RT-ANDGATE`, `RT-RIPTAC`, `RT-TCIP` |

- `RT-AF3-INTERFACE` — A method, not a route — it is waiting on a co-folder that assembles ternaries.
- `RT-ANDGATE` — Arm-2 chemistry does not exist and it inherits the degrader's ternary instruments.
- `RT-CART-SURFACE` — Blocked by the antigen search and the cold myxoid stroma, not by the cell product.
- `RT-COVALENT-PROBE` — Its in-silico half is not publishable BECAUSE its exposure instrument fails its own positive control — an instrument limit, not a statement about C397.
- `RT-CRISPR-CAS13` — Vector delivery, plus Cas13 collateral activity.
- `RT-DEGRADER` — ⭐ NOT closed — but every one of its four blocking failures is an INSTRUMENT LIMIT rather than a fact about the target, which is the options memo's organising finding restated as a field. Filing it beside a definitional impossibility would lose exactly that.
- `RT-GLUE` — ⚠ Graded ⏸ rather than ✕ because the block is a MISSING CAPABILITY — the modality most likely to arrive from someone else's screen.
- `RT-MONOVALENT` — ⚠ Its covalent sub-form's negative rests on a geometry computed with an exposure cutoff that fails its own control and a site question left INCONCLUSIVE — so the result can refute the route and cannot make the closure permanent. Its functional-actionability blocker is separate and needs a bench.
- `RT-RIBOZYME` — Vector delivery, and a technique with no modern solid-tumour clinical footing.
- `RT-RIPTAC` — It needs the paralogue selectivity the program cannot measure, plus a med-chem campaign.
- `RT-TCIP` — Demoted for an UNRUN computation, not a failed one — which is why it is the cheapest promotion in the memo.
- `RT-UBIQ-SELECTIVE` — ⚠ GRADED ⏸ NOT ✕, on the register's own caveat that this is a route closed by measurements that already exist rather than a proof of impossibility. The geometry does not reach FROM AN E3 ANCHORED AT THE CRYPTIC POCKET; a different anchor re-opens the measurement.

**`authorization`** — revivable. waiting on a person, not on nature.

| id | kind | permanently closed (derived) | revival trigger(s) | would reopen (derived) |
|---|---|---|---|---|
| `RT-ASO-ASK` Junction knockdown + parental sparing in EMC lines (the ask behind the | authorization | no | `TR-EMC-MODEL-ACCESS` | `RT-ATR-PANEL`, `RT-ASO-ASK`, `RT-TRABECTEDIN-PPARG`, `RT-SSTR2`, `RT-COVALENT-PROBE`, `RT-SYNLETH-DEP`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-PPARG-DOWNSTREAM`, `RT-CARFILZOMIB`, `R4` |
| `RT-ATR-PANEL` The ATR-inhibitor cell panel in EMC lines (the ask) | authorization | no | `TR-EMC-MODEL-ACCESS` | `RT-ATR-PANEL`, `RT-ASO-ASK`, `RT-TRABECTEDIN-PPARG`, `RT-SSTR2`, `RT-COVALENT-PROBE`, `RT-SYNLETH-DEP`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-PPARG-DOWNSTREAM`, `RT-CARFILZOMIB`, `R4` |
| `RT-SSTR2` SSTR2 / neuroendocrine theranostic | authorization | no | `TR-EMC-MODEL-ACCESS` | `RT-ATR-PANEL`, `RT-ASO-ASK`, `RT-TRABECTEDIN-PPARG`, `RT-SSTR2`, `RT-COVALENT-PROBE`, `RT-SYNLETH-DEP`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-PPARG-DOWNSTREAM`, `RT-CARFILZOMIB`, `R4` |
| `RT-TRABECTEDIN-PPARG` Trabectedin + a PPARγ agonist (all approved drugs) | authorization | no | `TR-EMC-MODEL-ACCESS`, `TR-EMC-EXPRESSION-DATASET` | `RT-ATR-PANEL`, `RT-ASO-ASK`, `RT-TRABECTEDIN-PPARG`, `RT-SSTR2`, `RT-COVALENT-PROBE`, `RT-SYNLETH-DEP`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-PPARG-DOWNSTREAM`, `RT-CARFILZOMIB`, `R4`, `RT-PRAME-IMMTAC`, `RT-FAP-RLT` |
| `V4` Selectivity free energy (ABFE) — the selectivity known-answer test | authorization | no | `TR-ABFE-AUTHORIZATION` | `V4`, `R7`, `RT-DEGRADER` |

- `RT-ASO-ASK` — Not refuted — waiting on a person with a bench.
- `RT-ATR-PANEL` — Best taker in the portfolio and still not something this programme executes.
- `RT-SSTR2` — Not refuted — a negative scan still kills it cheaply, and it stays on the ask list.
- `RT-TRABECTEDIN-PPARG` — Good taker, thin deliverable — the ask is the block.

## 10 · OPEN CONFLICTS — logged rather than decided

Each of these is a genuine disagreement in the record that this registry could not resolve from what is committed. Deciding them is the owning file's call, not a navigation layer's.

### `OC-2` · 'the canonical EMC fusion' names two incompatible objects, and one working module is built on the one that is not a reported fusion type.

**Files:** `research/modalities/fusion_cofold.py`, `research/modalities/emc_fet_idr_census.py`, `research/modalities/fusion_object_inventory.py`, `research/manuscripts/emc-post-degrader-options.md`, `research/manuscripts/target-route-options.md`, `research/manuscripts/emc-atr-collaborator-package.md`

- emc-atr-collaborator-package.md §2.2 + appendix: 'canonical' now belongs to reported type 1 (EWSR1 e12 :: NR4A3 e3); the e7::e3 combination is not a reported type. The e7::e3 ARITHMETIC remains valid and remains the right comparator for EWSR1::FLI1 type 1.
- Same file §7.2: reported type 2 carries 59 UTR-encoded residues, so fusion_cofold.py's protein-level model (EWS_CUT = 264, 'NR4A3 resumed at res 2') is not type 2 either.
- Same file, appendix: the §1.3 off-by-two correction is NOT superseded — both reported types retain NR4A3 from its first coding exon, so AF-1, the C4 zinc finger and the LBD are present under either.

**Why it is not decided here:** Changing which junction fusion_cofold.py models is a science decision with downstream reach (the neoantigen lane's seams, the IDR census's canonical row, R13's object) and at least three modules would have to move together. The registry's job is to make the three models nameable and separable; choosing between them is not a navigation-layer call.

**Owner:** research/manuscripts/nr4a3-program-map.md (R13 — 'real biological object')

### `OC-3` · emc-post-degrader-options.md states that fet-ddr-axis-scan.json is 'committed on `main`'. It is not on `main` as of this registry's authoring — it is on the feature branch and on `modalities-cache`.

**Files:** `research/manuscripts/emc-post-degrader-options.md`, `research/modalities/fet-ddr-axis-scan.json`

- The sentence is the FIX for an earlier instance of exactly this problem (numbers quoted off a branch), and it becomes true the moment the feature branch merges to `main`.
- Until then a reader on `main` follows a relative link to a file that is not there — the same shape of harm the sentence was written to close.

**Why it is not decided here:** The remedy is the merge itself, not a doc edit; editing the sentence to say something weaker would remove a true statement about the intended state. Logged so that if the merge is ever reverted, the claim is already registered as conditional on it.

**Owner:** CLAUDE.md §7 — keep everything synced to `main`

### `OC-4` · 'Bangerter 2023' — the only ex-vivo EMC drug-sensitivity evidence in the repo — carries no PMID or DOI anywhere.

**Files:** `research/IDEAS.md`, `research/manuscripts/repurposing-hypotheses.md`

- It is cited as load-bearing evidence for the carfilzomib route ('best ex-vivo EMC evidence', 'only 1 of 17 drugs with high sensitivity across 2 patient-derived EMC models').
- No canonical identifier is recorded, so it cannot be verified through `verify-refs` and is registered here with a search URL rather than an identifier.

**Why it is not decided here:** Resolving it needs a literature fetch from a CI runner (the dev sandbox's proxy 403s PubMed/PMC), which is a separate job. Registering the gap is what stops it reading as a verified citation.

**Owner:** research/manuscripts/fact-check-log.md

---

## Limits

- This registry asserts NO grade, NO tier and NO number of its own. Every grade cell names the file that owns it; every claim names the artifact field that owns it.
- It makes no efficacy, potency, safety, therapeutic-window or clinical-readiness claim for any route or molecule, and none follows from anything in it.
- It is not complete over the whole repo. Its scope is the EMC treatment-route portfolio plus the objects, evidence, instruments and artifacts those routes rest on.
- Where the record genuinely conflicts and the registry cannot resolve it from what is committed, the conflict is logged in `open_conflicts` rather than decided.

