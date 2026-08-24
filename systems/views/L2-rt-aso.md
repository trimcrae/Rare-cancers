---
id: DOC-VIEW-RT-ASO
title: RT-ASO — Fusion-junction ASO / siRNA (the deliverable)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: "Can an RNase-H gapmer or siRNA against the EWSR1::NR4A3 breakpoint junction silence the chimera while sparing wild-type NR4A3?"
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-ASO — Fusion-junction ASO / siRNA (the deliverable)

**Family:** [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · **state:** ○ blocked · scoped · confidence moderate · verified 2026-08-13

**Grade** (owned by [`research/manuscripts/program/emc-post-degrader-options.md`](../../research/manuscripts/program/emc-post-degrader-options.md)): Tier 1, rank 2 — DELIVERABLE

## What has to land for this route to move

```mermaid
flowchart LR
  RT_ASO["○ RT-ASO"]:::fam
  BLK_DELIVERY{{"BLK-DELIVERY — SYSTEMIC, antigen-dependent tumour deliver…"}}:::blk
  BLK_DELIVERY --> RT_ASO
  TECH_OLIGO_DELIVERY(["TECH-OLIGO-DELIVERY<br/>expected 2029"]):::tech
  TECH_OLIGO_DELIVERY -.-> BLK_DELIVERY
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

✓ Already cleared by this route: `BLK-NOT-FUSION-SELECTIVE`, `BLK-PARALOGUE-DDG`, `BLK-TERNARY-GEOMETRY`.

## Scientific rationale

The breakpoint junction is a sequence that exists in no healthy cell. An oligonucleotide reads sequence rather than shape, so it discriminates on SEQUENCE rather than shape — predicted, not demonstrated where every protein-directed route has to fight a shared fold. This is the fusion-selective route whose deliverable is finishable here (RT-JUNCTION-NEOANTIGEN, RT-TCR-IMMTAC and RT-RIBOZYME also retire the blocker), and its in-silico arc is complete: design, off-target screen, breakpoint-favourability scan, and gap-mismatch-resolved candidates.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-JUNCTION-ASO-OFFTARGET` | a transcriptome-wide off-target screen returning predicted-clean gapmers | `direct` |

## Remaining unknowns

- ⭐ THE LANE IS NO LONGER EWSR1-ONLY (2026-08-12, $0, offline). nr4a3-fusion-junction-atlas.json grades 231 donor-exon x NR4A3-acceptor-exon pairs across all five reported partners -- EWSR1, TAF15, TCF12, FUS and TFG; 38 are frame-compatible and EVERY ONE yields at least one junction-spanning, parent-sparing design, so designability is not this route's constraint. One 16-mer (GGGCATATCATCAAAC) is junction-spanning and fusion-exclusive at EWSR1 e12, TAF15 e11 and FUS e10 :: NR4A3 e3 SIMULTANEOUSLY, because the three donors are identical over the 10 bases 5' of their breakpoints (TGGTTTGATG; superseded, retained: '8 bases', which read the shared run off ONE DESIGN'S 8-base donor window instead of off the transcripts) -- so a stock reagent, not only an n-of-1 panel, is on the table. ✅ THE FIRST NON-EWSR1 SCREENS HAVE NOW RUN (2026-08-12, run 31593688595, $0): TAF15 e11 and FUS e10 return the SAME five designs as EWSR1 e12 from a live Ensembl read by an independent code path, and the shared design carries 8 predicted cleavage risks (superseded, retained: 'the cleanest of the twenty screened' -- those twenty screens were TEN distinct oligos, and TCF12 designs reach fewer; 0 exact and 1 <=1-mismatch across 186,185 transcripts). ⛔ The conclusion did not move: 0 of 5 clean at every junction. ✅ ALL FOUR PARTNERS ARE NOW SCREENED, AT 12 JUNCTIONS (run 31596310296 added TCF12's 8). TCF12 -- the one non-FET donor, excluded from every exact multi-partner set, which is the coverage mechanism's own negative control coming out right -- carries the LOWEST predicted off-target load of any partner (best 1 true cleavage risk vs 8 across EWSR1/TAF15/FUS), and TCF12 e7 is the first junction in the program with designs at zero <=1-mismatch off-targets on the uncapped scan. ⛔ It is still 0-of-4-clean on the WIDER gap-resolved screen, which is the defensible one (red-team F5), so breadth and per-oligo specificity point at different partners rather than one ranking. ✅ ALL 38 JUNCTIONS ARE NOW SCREENED AND ORIENTATION-FILTERED (2026-08-13, 183 designs). That dissolved the partner effect above: superseded, retained -- 'breadth and per-oligo specificity point at different partners rather than one ranking' and '0 of 5 clean at every junction'. Every one of the five partners now has a junction whose best design carries no hybridisable gap-spanning near-match, and NINE designs at SIX junctions across FOUR partners carry no hybridisable near-match at all over a complete hit list, with zero residual cleavage load under both literature bounds. The partner effect was an artefact of comparing screened TCF12 junctions against partners whose junctions were mostly unscreened. WHAT IS STILL NOT KNOWN: nine is a floor over the 47 of 183 designs whose hit lists are complete enough to assess, not a total; both screens search MATURE transcript only, so the pre-mRNA compartment is unmeasured; no TCF12 breakpoint is shown to occur in a patient; the one TAF15 exon with a published breakpoint (exon 6) is designable but is NOT among the cleaner junctions, while the exon the multi-partner result rests on (exon 11) has no reported patient; the provenance gate behind the TAF15/TCF12/FUS/TFG transcript models is the weaker of the two; and whether patients carry breakpoints at those homologous exons is a clinical fact nobody here holds.
- ⛔ 'DELIVERY' WAS ONE BLOCKER STANDING FOR THREE ROUTES WITH DIFFERENT REQUIREMENTS (2026-08-12; BLK-DELIVERY rescoped, paper §3c-bis). The missing EMC surface antigen gates the SYSTEMIC receptor-targeted route only. Local/intratumoural and inhaled/pulmonary administration need no antigen, and EMC's distant spread is lung-dominant (35-45% of patients, primarily lung, median ~28 months to metastasis; PMID 41055792). Inhaled oligonucleotide delivery producing gene silencing in tumours growing in the lung is an active preclinical field -- in other tumour types, in animals, never in EMC, never against a fusion, never in a patient (lit-targets-aso-delivery-routes.json). This changes what to attempt first; it does not move the modality closer to a patient.
- The committed design panel was rebuilt at the corrected mRNA junction on 2026-08-06 (aso-offtarget.yml run 31130876597, $0): NR4A3 resumes at residue 1, seams ACGGGCAGCAGA|ATATGCCCTGCG (e7n3) and AATGGTTTGATG|ATATGCCCTGCG (e12n3). The panel covers TWO junctions, not the five once claimed — e9n3/e10n3/e13n3 and every exon-mode siRNA file never existed and stay withdrawn as unverifiable. ⛔ THE CORRECTED SCREEN DOES NOT RESTORE THE RETRACTED HEADLINE: 0 of 5 designs at EACH junction are free of gap-spanning near-matches, so 'a gapmer predicted clean on both screens at E7::N3' is CONTRADICTED by the corrected data, not merely unproven. ⚠ SUPERSEDED IN PART 2026-08-13: that was true of the two-junction corpus this entry describes and is NOT true of the completed one -- see the first entry above. What survives is the narrower claim it was making: the E7::N3 'clean on both screens' headline stays retracted, and E7 is not among the six clean junctions. GC does move in the route's favour (37.5-56.2% vs 75.0-81.2% at the modelled reference).
- How to deliver an oligonucleotide to a non-hepatic solid tumour — the one remaining gate, and it is engineering rather than biology.
- Whether predicted specificity survives a calibrated cleavage model: the current screen uses a deliberately conservative gap-mismatch heuristic, so it may be over- or under-calling.
- Whether the potency ranking holds — it rests on a local-fold accessibility proxy rather than a measured accessibility model.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A delivery vehicle that reaches an EMC tumour | ⛔ none built | **no** | BLK-DELIVERY |
| Junction knockdown with parental sparing in an EMC line | ⛔ none built | **no** | BLK-NO-WET-LAB |
| Regenerate the junction panel at the CORRECTED seam and re-derive every design (needs network — CI). ✅ DONE 2026-08-06 — panel regenerated at the corrected seam and verified against two independent transcript acquisitions (working record §3a-sexies) | ⛔ none built | yes | — |
| A calibrated gap-internal-mismatch RNase-H1 cleavage model, which would retire the conservative heuristic the specificity margin rests on (paper §8) | ⛔ none built | yes | — |
| A TFG transcript model, the one reported EMC partner with no model in this repository -- one targeted Ensembl fetch, nothing else missing. ✅ DONE 2026-08-12 — ENST00000240851, contributing 24 graded pairs and 6 frame-compatible junctions | ⛔ none built | yes | — |
| Screen the remaining 20 emittable junctions; the pipeline reaches any partner now. ✅ DONE 2026-08-13 — all 38 frame-compatible junctions screened AND orientation-filtered, 183 designs; coverage residual is zero | ⛔ none built | yes | — |
| ⭐ A GENOMIC / PRE-mRNA OFF-TARGET SCREEN. Both committed screens search MATURE transcript sets, so intronic and intron-exon-spanning sites are invisible to them by construction -- and RNase-H1 is nuclear, so pre-mRNA is a real substrate. The manuscript names this as its largest blind spot and says it is 'closable by a genomic screen'; until 2026-08-13 it appeared in no register here, which is how a paper's own stated hole stays open. CI-runnable, $0 ✅ PARTLY DONE 2026-08-13 (run 31697045904, $0): the PARENT pre-mRNA arm is complete -- exhaustive <=2-mismatch scan of all 190 designs against the unspliced sequence of all six parent transcripts, gap-resolved and orientation-filtered. 19 of 190 carry a hybridisable gap-paired site no transcript screen could see; NINE of those span the wild-type NR4A3 intron-2/exon-3 boundary, which is a route to the parent this modality must spare and which gap-level discrimination does not protect. None of the nine designs the cleanliness claim rests on is affected. ⛔ STILL OPEN: the GENOME-WIDE arm. This covers six genes' introns and says nothing about the other ~20,000; the module carries a best-effort NCBI arm behind PREMRNA_GENOMIC=1 that has not been run. ⚠ THE GENOME-WIDE ARM WAS ATTEMPTED 2026-08-13 (run 31698435645) AND DID NOT YIELD AN INTERPRETABLE RESULT: NCBI's URL service answered on `core_nt`, which is a mixed corpus of assemblies, clones, patents and transcripts rather than a genome reference, and all 9 queries saturated the 50-hit ceiling while returning identities below the threshold this work uses. Released so nobody repeats it. A real genome-wide screen needs a local BLAST database, not the public URL API. | ⛔ none built | yes | — |
| De-censor the near-match counts: 136 of 183 designs carry right-censored counts because BLAST returns at most 50 hits and only SAVED_HITS_PER_DESIGN are stored. Raising both converts upper bounds into measurements and decides the ten-vs-nine discrepancy (a tenth design scores zero residual load but is refused as clean because its unstored hits are unknown). CI-runnable, $0 ✅ TESTED 2026-08-13 (run 31697971910, $0), and the answer went AGAINST the designs, which is the useful direction. The 7 records whose only obstacle was the retention depth were re-screened at a tenfold deeper ceiling: 6 decided, NONE clean (21 near-matches -> 161 with 5 hybridisable; 47 -> 196 with 119; 23 -> 68 with 48; 27 -> 65 with 5; 35 -> 78 with 10), 1 failed at the remote service. So the censoring guard is LOAD-BEARING: relaxing it would have promoted six records a deeper look refutes, and the nine are unchanged. ⛔ STILL OPEN: the 8 records sitting AT the 50-hit ceiling, whose bound is the search's own cap rather than retention, and the 7 designs whose original query failed at the remote service. | ⛔ none built | yes | — |
| Re-run the 7 of 190 designs whose BLAST query failed at the remote service (3 poll timeouts, 4 dropped connections), which is the whole of the gap between the 190 designs scored thermodynamically and the 183 screened. CI-runnable, $0 | ⛔ none built | yes | — |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-DELIVERY** | `requires_future_technology` | `TECH-OLIGO-DELIVERY` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer
- **BLK-NOT-FUSION-SELECTIVE** — The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-ASO-ASK](L2-rt-aso-ask.md) | deliverable vs ask | `BLK-NO-WET-LAB` | the manuscript is finished and needs nobody; the knockdown experiment needs a lab and has the portfolio's weakest taker. Grading them as one row is what the W1/W2/D correction exists to stop |
| [RT-CRISPR-CAS13](L2-rt-crispr-cas13.md) | delivery class | `BLK-DELIVERY` | an oligonucleotide's delivery problem has clinical precedent in solid tumours; a vector's is a different engineering problem with different precedents, and Cas13 additionally carries collateral activity |

## Readiness — what this could become today

**`chemrxiv`**

The computational arc is complete and the delivery gate is stated honestly as a gate rather than hidden. A journal submission is reachable; what would strengthen it most is not more computation but a delivery candidate to name. Two $0 in-silico gaps remain and are now registered in required_validation rather than only conceded in the manuscript's Limitations: the pre-mRNA/genomic compartment, and the right-censoring that leaves 136 of 183 near-match counts as bounds.

**Missing:**
- a named delivery candidate FOR THE SYSTEMIC ROUTE -- rescoped 2026-08-12; the local and inhaled routes never required one, and grading the whole route on the systemic route's missing input is what the BLK-DELIVERY rescope corrects

**Experiment required:**
- junction knockdown plus parental sparing in an EMC or FET-fusion line

## Where this route ends — the paper

**[PUB-ASO](L3-publications.md)** — [NR4A3 fusion-junction antisense gapmers for extraskeletal myxoid chondrosarcoma: reagents, test articles and a pre-registrable knockdown experiment](../../research/manuscripts/aso/fusion-junction-aso-journal-article.md)

`primary` · ◕ `complete_unposted` · aimed at `journal_submission`

**This route contributes:** The junction design, the transcriptome-wide specificity screen, and delivery stated as the outstanding gate rather than assumed away.

**The paper would claim:** The NR4A3 fusion junction is the one tumour-exclusive feature of this disease at the RNA level, and two junction-spanning gapmers are named for synthesis against it: 5'-GGGCATATCATCAAAC-3' at EWSR1 exon 12 and 5'-GGGCATATCTTGTGTG-3' at TAF15 exon 6, the best available designs at the two most frequently reported breakpoints. They are what survives a screen that condemns most of the panel: 87 of 190 junction-spanning designs let a mature wild-type parent transcript pair their whole catalytic gap over at least ten contiguous base pairs, 61 of them against wild-type NR4A3 itself, and lengthening the catalytic gap raises the margin available only by conceding parent-paired gap DNA, for an arithmetic rather than an empirical reason. Two fusion-positive patient-derived EMC models and two engineered constructs carrying these junctions are named as test articles, the controls and pre-registrable decision threshold for the falsifying experiment are stated, and the design pipeline is released for breakpoints outside the panel. Delivery is named as an outstanding gate rather than assumed away, the named reagents carry stated parent-duplex and off-target loads, and nothing here has been synthesised or tested.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The computation is done and publishing is what recruits the collaborator this route needs. Waiting does not improve the design; it only delays the ask. Delivery is watched in parallel and does not gate the write-up.

| horizon | effect |
|---|---|
| Six months | Little on the design. Possibly a lot on whether a delivery candidate can be named. |
| Two years | Decisive — a working conjugate platform for solid tumours would move this from a design to a programme. |
| Cost trend | flat |
| Automation outlook | The design and screening halves are already automated; delivery is not a computational problem at all. |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md), which is where these are asserted — a family limitation binds every route inside it.*

- Delivery of an oligonucleotide to a non-hepatic solid tumour has no validated solution, and this is not solvable in silico today.
- Predicted specificity rests in part on a conservative heuristic rather than a calibrated cleavage-activity model.
- The vector-delivered sub-routes carry a second, distinct delivery problem that must not be conflated with the oligonucleotide one.

## Best next action

Publish the complete in-silico arc: a systematic NR4A3-fusion junction design platform spanning all five reported partners, screened and orientation-filtered at all 38 frame-compatible junctions, with delivery stated as three routes of differing requirement rather than one gate. Superseded, retained: 'spanning four partners, screened at three junctions'.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-FUS-T1](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-FUS-T2](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-NR4A3-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

[← ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · [← L0](L0-ecosystem.md)
