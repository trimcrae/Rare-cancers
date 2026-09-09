---
id: DOC-TCIP-INDUCED-INTERFACE-PREPRINT
title: An inherited minimum-contact filter controls the acceptance ordering of one rigid-body proximity sampler — a toolchain audit and sensitivity analysis
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: The manuscript for publication endpoint PUB-TCIP. A narrow toolchain audit and parameter-sensitivity result. One rigid-body placement sampler applies a minimum induced-interface filter whose only committed provenance is a degrader-recruitment sampler and for which no derivation is recorded; changing only that filter reverses the pooled acceptance ordering of four staged bodies; the parameter is named for residues but compared against a probe count. A separately defined exact-distance census of selected deposited structures is reported beside it as a descriptive comparison, not as a calibration.
scope: Rigid-body geometric enumeration inside one toolchain, and exact-distance contact counting on a selected set of deposited coordinates in one crystal form each. It does NOT calibrate, bound or validate any interface floor, and it establishes no equivalence between the sampler's predicate and the census predicate. It is NOT a disease-specific result and makes no binding, potency, selectivity, transcriptional-output, efficacy, safety, therapeutic-window or clinical claim.
audience: [external reviewers, maintainers, autonomous research agents]
date: 2026-08-07
revised: 2026-09-08
last_verified: 2026-09-08
---

# An inherited minimum-contact filter controls the acceptance ordering of one rigid-body proximity sampler

**A toolchain audit and parameter-sensitivity analysis. Preprint draft — not submitted, not posted.**

**Tristan D. McRae**

Independent researcher, unaffiliated. Correspondence: trimcrae@gmail.com. ORCID 0000-0002-1823-1451.

*Study type: a computational audit of one analysis toolchain, plus contact counting on publicly
deposited macromolecular coordinates and reading of public literature records. No experiment was
performed, no wet-lab work of any kind was carried out, and no new recruitment, sampling or
intervention took place.*

> **Revision of 2026-09-08.** This is a narrowed rewrite. The earlier version of this manuscript —
> repository revision `f43f1495f40d8aff7b4f34bd385d55aac521a500`, 28,068 bytes — claimed that the
> measured crystal complexes would be rejected by this sampler's predicate, that the result bounded
> a transcriptional interface floor from above, that the acceptance ratio measured orientation-space
> volume, that body size was not the controlling variable, that the literature searches established
> an absence in the field, and that this modality's selectivity requirement is not smaller than a
> degrader's. **Those claims are withdrawn, not softened.** Appendix A registers each withdrawal
> against the sentence it replaces. The frozen version is retained unchanged in repository history;
> nothing in the underlying artifacts, counts or source bytes was altered by this revision.

> **Role: the manuscript for publication endpoint
> [`PUB-TCIP`](../../../systems/views/L3-publications.md).** Every number is read at write time from
> the artifact that owns it: the geometric enumeration from
> [`nr4a3-tcip-reach.json`](../../modalities/nr4a3-tcip-reach.json), the structural census from
> [`nr4a3-induced-interface-census.json`](../../modalities/nr4a3-induced-interface-census.json). This
> manuscript adds no measurement of its own. Methods, full tables and provenance:
> [SI](./tcip-induced-interface-preprint-si.md). The dated decision view
> [`tcip-interface-floor-sizing.md`](./tcip-interface-floor-sizing.md) is a historical 2026-08-07
> record that still carries the wider framing withdrawn here, and is cited below only for the
> retrieval operations it records, never for a claim this paper makes.

> **This is a parameter and measurement-definition result, not a disease-specific one.** The
> enumeration was computed in an EWSR1::NR4A3 setting because that is the program it arose in, and
> that is the setting rather than the claim. Both structural results are free of NR4A3: the
> contact-count census is on a BCL6·p300 system and on published degrader/glue ternaries, none of
> them NR4A3. Nothing here is evidence about any disease.

---

## Abstract

Chemically induced proximity is often designed with tooling built for targeted protein degradation.
The rigid-body proximity sampler audited here is one such instance, and it carries a parameter with
no recorded derivation: `min_contact_residues = 12`, a minimum induced-interface size below which a
candidate placement is scored, in that code's comment, as a tethered pair rather than an interface.
Its only committed provenance inside this toolchain is a degrader-recruitment sampler. How widely
other proximity samplers impose a filter of this kind was not surveyed, so the inheritance reported
here is a property of one toolchain and not a measured feature of any field.

We report three things that the retained records support. First, the parameter is named for residues
but is compared against a count of scoring probes: the query set holds up to two probes per residue,
the CA and the side-chain centroid, and the placement loop increments per probe. Exactly twelve
contacting probes can therefore come from between six and twelve distinct residues; acceptance at a
threshold of at least 12 probes requires at least six contributing residues, a condition that is
necessary but not sufficient, is not an equivalent residue-count rule, and imposes no upper bound of
twelve residues. No single residue-count conversion exists. Second, in a paired enumeration from fixed anchors, changing only
this filter reverses the pooled acceptance ordering of four staged bodies: single-domain bodies
accept 583 of 720,000 proposals against 651 of 720,000 for multi-subunit bodies at the committed
floor of 12, a ratio of 0.896, while at floor 6 the counts are 6,315 against 5,632 (ratio 1.121) and
at floor 0 they are 57,657 against 45,990 (ratio 1.254). These are observed proposal-acceptance
fractions under one non-uniform proposal with shared random streams, conditional on twelve fixed
anchors and one target model. Third, a separately defined exact-distance census of 22 selected
deposited entries records small contact-band scores for two chain pairs of PDB 9MZA, the chemically
hijacked BCL6·TCIP3·p300 complex (X-ray, 2.1 Å): 6 and 7 contact-band probes across 4 distinct
residues per side, in two related interface instances of one deposited A2B2 assembly.

**What this does not establish.** The census uses exact nearest-atom distances; the sampler uses a
grid lower bound with a 0.7794 Å cell slack, a different scoring unit and a full admission predicate.
The two are not equivalent, and nothing here shows that the sampler would admit or reject any
deposited complex. Comparing a census score of 6 or 7 against the number 12 is arithmetic between two
differently defined quantities; it does not calibrate or bound the sampler's filter, and it does not
measure a requirement biology imposes. The acceptance fractions are not orientation-space volumes,
equilibrium probabilities or linker-feasibility estimates. The four-body design cannot identify a
controlling variable, and it neither establishes nor refutes an effect of body size. The literature
searches are bounded retrieval observations that cannot establish an absence in the field. No
selectivity requirement was estimated. Nothing here is a binding, potency, selectivity,
transcriptional-output, efficacy, safety, therapeutic-window or clinical claim, and no interface
reported here was experimentally validated by this work.

---

## 1 · The parameter, and what its provenance actually shows

A bivalent molecule that recruits a transcriptional effector to a target — a transcriptional chemical
inducer of proximity, TCIP — is geometrically similar to a PROTAC with the ligase exchanged. That
similarity is why proximity-design tooling is reused for it.

The rigid-body sampler audited here scores a candidate placement on excluded volume plus a minimum
induced interface. The parameter is `min_contact_residues = 12` in `nr4a3_basin_search.PARAMS`,
carrying the comment *"below this it is a tethered pair, not an interface"*. Two facts about it are
established by the source and nothing more. The comment records no derivation. And the parameter's
only committed provenance inside this repository is a degrader-recruitment sampler, from which
`nr4a3_tcip_reach.py` takes its scoring unchanged (SI §S1).

An earlier version of this manuscript offered a reconstruction of the intent — that ubiquitin
transfer requires a cooperative, buried target·E3 interface — and attributed the parameter to it as a
hypothesis. That reconstruction is not derived by the cited source, which has separate
transfer-geometry machinery, and it is withdrawn here. What the source establishes is narrower and
sufficient for this paper: the value has no recorded derivation of any kind.

Two limits follow and hold throughout. How widely other proximity samplers impose a filter of this
kind was not surveyed, so this is documented inheritance inside one toolchain rather than a property
of the field. And the filter is operational: it decides which candidate placements this code admits.
No result below converts it into a requirement that induced proximity biologically imposes, and this
paper does not size such a requirement.

## 2 · Two different predicates, stated separately

The central definitional point of this audit is that the placement sampler and the structural census
apply different predicates to the same numerical radii. They are set out here separately, because the
earlier version of this paper described the census as *the sampler's own predicate* and that
description is withdrawn.

**The sampler's placement admission predicate** (`nr4a3_basin_search`, placement loop):

| step | what the code does |
|---|---|
| distance source | a cubic grid distance field over the target's heavy atoms, cell 0.9 Å, clamped at 8.0 Å |
| distance used | `field.min_dist(point) - field.cell_slack`, a **lower bound**, with `cell_slack = sqrt(3) × 0.9 / 2 = 0.7794228634 Å` |
| anchor clearance | the proposed exit point must clear `pose_min_clearance_A` on that same lower bound, or the proposal is discarded before scoring |
| per-probe bands | lower bound `< 3.0 Å` hard clash (loop breaks, placement rejected); `3.0–3.6 Å` soft clash; `3.6–6.0 Å` contact, counted |
| admission | reject if any hard clash, or more than 6 soft clashes, or fewer than 12 contact probes |
| unit | the whole staged body, which may be multichain, against one target frame |

**The census scoring predicate** (`nr4a3_induced_interface_census.contact_profile`):

| step | what the code does |
|---|---|
| distance source | exact nearest heavy-atom distance, computed through a cell hash, with no slack |
| bands | the same numerical radii, 3.0 / 3.6 / 6.0 Å, applied to the **exact** distance |
| admission | none: the census counts probes and makes no accept/reject decision |
| unit | one chain against one other chain, scored in both directions and reported both ways |

Identical radii and an identical query-point construction do not make these predicates identical, and
the difference is not an order-preserving offset. A probe sitting at a grid-cell centre whose true
nearest-atom distance is 4.0 Å is a contact under the census and a soft clash under the sampler,
whose lower bound for it is approximately 3.2206 Å. In the other direction, probes lying outside the
exact 6.0 Å boundary can enter the sampler's contact band. This is an analytic example about the two
definitions; no structure was remeasured for it, and it is not an assertion about any particular
atom.

The unit of comparison differs as well. A chain-pair contact score is not a placement admission
decision: admission also depends on anchor clearance, the hard-clash break, the soft-clash budget and
the body's multichain extent.

**Consequence, stated once and relied on throughout.** The census scores reported in §5 are exact
nearest-atom contact-band probe counts. They are not the sampler's score, and nothing in this paper
demonstrates how the implemented sampler would score or admit any deposited complex.

## 3 · What the acceptance fraction actually is

The sampler draws a linker-end radius as

`r = L_min + (L_max - L_min) * U^(1/3)`,

under a source comment that describes the draw as uniform in the shell volume. For a non-zero inner
radius, a draw uniform in shell volume instead requires
`r = (L_min^3 + U*(L_max^3 - L_min^3))^(1/3)`. At the committed 12-atom rung, `L_min = 3.75 Å` and
`L_max = 15 Å`; at the midpoint radius 9.375 Å the implemented proposal places probability 0.125
inside that radius, where a uniform-volume proposal would place 0.232142857. Direction and
orientation are drawn uniformly on the sphere and over unit quaternions respectively, but the joint
placement proposal is not uniform in translation volume.

This is recorded here as a code-comment-to-implementation discrepancy in the audit. The retained run
is **not** relabelled as having used the corrected formula, and no rerun was performed.

What the reported numbers therefore are: **observed proposal-acceptance fractions**, conditional on
the implemented proposal, on twelve fixed warhead anchors selected by a geometric-eligibility and
spacing construction around a modelled pocket, on one target frame and distance field, and on one
linker rung. They are not fractions of orientation space, not measured admissible volume, not
equilibrium or binding probabilities, and not linker-realizability estimates. The claim in the
earlier version that ablating the floor gives the smaller body "25 % more admissible orientation
space" is withdrawn; the retained arithmetic supports a ratio of proposal-acceptance fractions and
nothing about volume.

The enumeration also relates acceptance to a body-free grid-volume denominator elsewhere in the
artifact. Those two quantities use different measures, and their quotient is not a conditional
survival probability or a physical cost; no such reading is made here.

## 4 · The sensitivity result

The paired enumeration stages six bodies from deposited coordinates and places them by rigid-body
Monte Carlo from fixed anchors: 576 cells (body × anchor × linker rung) at 300,000 draws each,
172,800,000 draws in total. The floor ablation re-runs the identical cells at the 12-atom rung with
only `min_contact_residues` changed, at 30,000 draws per arm per anchor. Two bodies are single-domain
E3 recruiters (`birc2`, 92 residues; `mdm2`, 94) and two are multi-subunit E3s (`crbn`, 1,183;
`vhl`, 340). Two further staged bodies, `bcl6` and `brd4_bd1`, ran in the same pass and are excluded
from every pooled figure (SI §S1, §S4).

**Retained counts, and the ratios they give.**

| `min_contact_residues` | single-domain accepted / drawn | multi-subunit accepted / drawn | ratio of pooled fractions |
|---|---|---|---|
| 12 (committed) | 583 / 720,000 | 651 / 720,000 | 0.895545 |
| 6 | 6,315 / 720,000 | 5,632 / 720,000 | 1.121271 |
| 0 (no contact filter) | 57,657 / 720,000 | 45,990 / 720,000 | 1.253686 |

*(12-atom linker rung, 30,000 draws per arm per anchor;
[`nr4a3-tcip-reach.json`](../../modalities/nr4a3-tcip-reach.json) → `★_interface_floor_ablation`.
Displayed rounded elsewhere as 0.896, 1.121 and 1.254.)*

**The observation.** Changing one filter inside an otherwise fixed computation reverses which pooled
class accepts more proposals. That is a controlled software intervention, and it is the paper's
sensitivity result: this ordering is a property of the filter setting, not a stable property of the
bodies.

**What the design does not license.**

*Uncertainty.* The ablation reuses `random.Random(777 + pose_index)` across arms and across floors.
This is a common-random-number design: the arms share proposals and are not independent observations.
The artifact stores marginal Wilson intervals formed from pooled accepted/drawn counts — at floor 12
approximately [0.0007466, 0.0008781] for the single-domain pool and [0.0008374, 0.0009763] for the
multi-subunit pool — and these overlap. **Neither the overlap nor the intervals test the ratio.** The cross-arm joint acceptance counts were not retained, so the empirical cross-arm covariance
cannot be estimated from the retained marginal counts; no ratio interval is reported for this
ablation. Missing empirical covariance does not establish that every conservative interval or bound
is unavailable. This missing joint record belongs to the shared-proposal ablation. It is not a statement about the separate eight-rung
enumeration of §4a, which is a different object: its four pooled arms use distinct random streams and
its marginal cell counts are retained, and for it this paper reports no ratio interval and no
significance test (SI §S5). The counts are also conditional on heterogeneous fixed anchor strata
rather than on biologically sampled units, so a pooled-binomial interval would not quantify uncertainty across
proteins, target conformations or source structures in any case. The rounded sign change is reported
as an observed point-estimate ordering and is not offered as a significance claim.

*Independence across the main enumeration.* Per-cell seeds in the main run are built as
`20260725 + 1000×rung + crc32(arm) % 997 + anchor index`. The truncated salts collide for `bcl6` and
`vhl`, which share seven anchor streams per rung, 56 collisions across the eight rungs. The four
pooled arms have distinct streams, so the four-body pooled comparison is not affected; the collisions
do mean that the 576 cells are not all independent. They are a documented design property and are not
evidence that any retained count is wrong.

*Monotonicity.* Each individual body's acceptance count is non-decreasing as an otherwise identical
minimum-count filter is relaxed, and the retained marginal counts are nested accordingly. A ratio of
two such functions need not be monotone. The earlier claim that the ratio "is monotone in the floor"
is withdrawn: three sampled floors are three points, and they do not establish behaviour at
intermediate thresholds or at other rungs.

*Historical checks, labelled by their evidence status.* The route memo reports 0.894 for the same
contrast at 40,000 draws per arm per anchor, and reports two full runs under `PYTHONHASHSEED=0` and
`PYTHONHASHSEED=99` producing byte-identical JSON after the seed construction was fixed from
`hash(arm_id)` to `zlib.crc32`. Those are historical author-reported checks. The separately retained
40,000-draw counts and the two compared outputs were not available to this revision, so neither is
presented as an independently inspected record here. Because the seeding is stable, a larger run may
contain a shorter run's prefix; agreement between them would then not be an independent replication.
Stable seeds establish reproducibility of the random input; they do not establish convergence and are
not a biological validation.

### 4a · The size axis: what this design can and cannot say

Across the eight rungs the single/multi ratio spans 0.858–0.972, with 95 % marginal intervals
overlapping at 2 rungs; at the 12-atom rung it is 0.877 in the 300,000-draw paired run against 0.896
for the same contrast in the 30,000-draw ablation. The spread within a size class exceeds the
between-class contrast at 8 of 8 rungs: two roughly 90-residue single-domain bodies differ from each
other by up to 1.421×, while the classes differ by at most 1.165×. `birc2` accepts more than `crbn`
at every rung despite being far smaller.

The pooled contrast is therefore confounded and may not be reported as a size law. The earlier
version went further and concluded that body size is not the controlling variable and that individual
shape and exit-vector geometry is; **both halves of that are withdrawn.** There are two bodies per
class, and they differ in shape, multimeric extent, ligand pivot and exit geometry as well as in
residue count. Within-class spread larger than a between-class contrast does not refute a size
contribution — it is equally compatible with a size effect plus stronger variation from other
properties — and no comparison here isolates shape or exit geometry as a cause. **This design
identifies no controlling variable.** What survives is the sensitivity of the observed pooled
ordering to the filter setting, measured on the same bodies in both arms.

## 5 · The census: a descriptive exact-distance comparison

22 deposited mmCIF entries were fetched in CI, parsed, and had their identity verified from each
file's own `_struct.title` and `_entity.pdbx_description` rather than from the accession. Every chain
pair is scored in both directions under the exact-distance predicate of §2, and both numbers are
reported; no orientation is promoted.

### 5a · How a pair reaches the reported set

The selection has five stages, and the fourth is selection on the measured outcome. It is stated
explicitly because this is a paper about a minimum contact score.

| stage | rule | effect |
|---|---|---|
| 1 · entry | 22 fetched, 22 parsed, identity verified from the file | 22 entries |
| 2 · chain eligibility | a chain is kept when at least half its atoms are amino-acid atoms and it has at least 40 of them | protein chains only |
| 3 · ligand eligibility | a heteroatom group that is not water or a listed buffer species and has at least 12 heavy atoms; a chain is *touched* when a ligand heavy atom lies within 4.5 Å, and *spanned* when at least three do | bridging-ligand candidates |
| 4 · zero-score filter | every chain pair is scored both ways first, and a pair with **zero** contact-band probes in **both** directions is dropped before induced pairs are chosen | removes pairs on their measured score |
| 5 · induced-pair selection | a surviving pair is induced when a spanning ligand covers both chains, or when it is curated by name as allosteric; named constitutive pairs are excluded | the reported set |

### 5b · 9MZA, mapped completely

PDB 9MZA is *"Chemically Hijacked BCL6-TCIP3-p300 Complex"*, X-ray, 2.1 Å, deposited 2025-01-22 and
released 2025-04-16. Entity 1 is B-cell lymphoma 6 protein and occupies chains A and C; entity 2 is
histone acetyltransferase p300 and occupies chains B and D; `A1BUC` is the non-polymer ligand, present
in two copies of 81 heavy atoms each. The author-defined assembly is a hetero 4-mer of stoichiometry
A2B2 over chains A–D under the identity operation, with fluorescence resonance energy transfer
recorded in the source metadata as author-provided assembly evidence — a source assertion, not an
experiment inspected here.

Five chain pairs are ligand-spanned candidates. Their disposition:

| candidate pair | chains | disposition |
|---|---|---|
| A/B | BCL6-A + p300-B | dropped at stage 4: zero contact-band probes in both directions. Its full profile is not retained |
| A/C | BCL6-A + BCL6-C | the constitutive BCL6 BTB homodimer, excluded by name from the induced class; retained as a control at 71 / 66 |
| A/D | BCL6-A + p300-D | retained and reported: 6 / 7 |
| B/C | p300-B + BCL6-C | retained and reported: 7 / 6 |
| C/D | BCL6-C + p300-D | dropped at stage 4: zero contact-band probes in both directions. Its full profile is not retained |

The omission of A/B and C/D is inferred from the displayed code and the retained record, which lists
them as ligand-spanned candidates and does not carry them in the scored pairs. Their profiles were
not retained and are not reconstructed here. **They must not be recoded as absent source, as a parse
failure, as an absent ligand bridge, or as biological inactivity.** What they show is that the
reported denominator for this entry is two of four non-constitutive ligand-spanned pairs, and that
the two omitted ones were removed by a zero-score rule.

The two reported interfaces are therefore two related interface instances inside one deposited
tetrameric assembly that shares a BCL6 dimer. They are not two independent functional systems, and
the earlier phrase "two crystallographically independent copies" is kept only in that
crystallographic sense.

**Ligand contacts, corrected.** The earlier version stated that the bridging ligand "contacts 33–42
atoms' worth of each partner" while displaying the A/D and B/C interfaces. Those counts describe the
dominant attachments, which belong to the two pairs dropped at stage 4. The retained per-copy counts
are:

| ligand copy | BCL6-A | p300-B | BCL6-C | p300-D |
|---|---|---|---|---|
| `A1BUC` on chain A | 33 | 42 | 18 | — |
| `A1BUC` on chain C | 16 | — | 33 | 40 |

So the 33/42 pair describes the A/B attachment and the 33/40 pair the C/D attachment. For the two
**reported** interfaces the directional ligand-contact counts are 16 (BCL6-A) and 40 (p300-D) for
A/D, and 42 (p300-B) and 18 (BCL6-C) for B/C.

### 5c · What the retained scores are, and the hypothetical cutoff arithmetic

| reported pair | contact-band probes, both directions | distinct residues with a contact probe, per side |
|---|---|---|
| A/D | 6 / 7 | 4 and 4 |
| B/C | 7 / 6 | 4 and 4 |

The sampler's parameter is 12. The numbers 6 and 7 are below 12. **That is arithmetic between two
differently defined quantities, and it is reported as nothing more.** It does not show that the
sampler would reject this complex, it does not calibrate or bound the sampler's filter, and it is not
a measurement of any requirement that induced proximity imposes. The earlier version's statement that
the real transcriptional CIP "fails the floor" — defined there as *would be rejected by this
sampler's predicate* — is withdrawn, together with the claim that this bounds the floor from above.

### 5d · Dynamic range and construct coverage, described as such

The same census predicate reads the constitutive BCL6 BTB homodimer at 71 / 66 contact-band probes in
9MZA (chains A then C) and at 67 / 64 in the independent entry 7LWG (chains A then B). This shows the score takes large values on that
large interface in those two files. It does not establish the score's accuracy, its resolution at
small interfaces, or its biological relevance, and a coarse CA/centroid shell count can separate a
large interface while describing a small one poorly. The score also counts only probes in the
3.6–6.0 Å shell: probes closer than that are counted as clashes rather than contacts, so this is not
a count of atomic contacts, a buried surface area, or an interaction network.

For construct coverage, the BCL6 chains contribute 122–123 residues (244 and 246 query probes) and
the p300 chains 112–113 (224 and 226). Source metadata sharpens this: the deposited alignment maps
BCL6 to UniProt residues 5–129 and p300 to residues 1040–1161, with construct tags, and records BCL6
sequence conflicts against the reference at positions 8, 67 and 84; the entry reports 470 modeled and
76 unmodeled polymer monomers out of 546 deposited. These describe how much of each construct
contributed to the score. They do **not** establish that the relevant full-length interface is
complete, that no unresolved segment matters, or that construct and crystal-context effects are
excluded; the earlier version's conclusion that the small count is therefore "a property of the
interface, not of the instrument" and "not of a short chain" is withdrawn.

### 5e · The selected degrader and glue pairs

Among the 15 selected degrader/molecular-glue induced pairs across 8 entries, 6 have a smaller
direction below 12, including 5T35 (MZ1·BRD4-BD2·pVHL) at 10 / 14 and 11 / 14 across its two copies,
6HAX at 11 / 18 in both copies, 7Q2J at 5 / 12, and 6SIS at 10 / 11 in one copy while reading 13 / 16
in the other. The full table is SI §S4.

This is a descriptive result about a selected list. It is **not** a population false-rejection rate:
the entry list was selected, repeated copies and related complexes within it are dependent, and the
comparison is again between a census score and a parameter value, not a re-run of the sampler. That
the six below-cutoff rows cluster among the VHL- and SMARCA2-recruiting entries is an observation; it
does not by itself distinguish an uncalibrated cutoff from structural, construct or score-specific
variation, and it is not a noise test. The earlier version's inference that this shows the threshold
is "uncalibrated rather than noisy" is withdrawn.

## 6 · The naming discrepancy inside the parameter

`min_contact_residues` reads as a count of residues. The placement loop does not count residues. It
iterates a query set built as up to two probes per residue — the CA and the side-chain centroid, with
the CA reused for glycine — and increments per probe. It is also a three-band `if/elif` chain, so a
probe scores as a contact only in the shell between the soft-clash and contact radii; closer than
that it is a clash.

The committed value of 12 is therefore **12 probes**, and **exactly twelve** probes could be
supplied by between six and twelve distinct residues. Three statements follow, and they are
distinct.

1. **The residue condition is necessary.** A residue supplies at most two probes, so a placement
   accepted at a threshold of at least 12 probes must draw those probes from **at least six**
   contributing residues.
2. **It is not sufficient, and it is not an equivalent rule.** Six or more contributing residues do
   not imply 12 scoring probes: a residue scores only for those of its two query points that fall in
   the contact band, so it may contribute two, one or none. No residue-count threshold reproduces the
   probe threshold, and the probe rule may not be restated as one.
3. **There is no upper bound of twelve residues.** Six to twelve is the range of residues that could
   supply *exactly* twelve probes. Acceptance requires twelve **or more**, so an accepted placement
   may involve more than twelve contributing residues; the cutoff alone imposes no twelve-residue
   upper bound.

The earlier version's reading — "12 points, as few as 6 residues" combined with "a floor of at most 6
residues' worth of probes" and "roughly half either way" — reversed that inequality and is withdrawn,
and so is the assertion that a threshold on probes imposes no threshold at all on residues: it
imposes the necessary lower bound in statement 1. For completeness: the retained 4 distinct residues
per side divided by six is 2/3, and divided by twelve is 1/3; there is no single residue conversion,
and the paper does not attempt one. A probe count is also not a
count of interatomic contacts, since a side-chain centroid is a geometric proxy and the same CA
position contributes twice for glycine.

This discrepancy — a parameter named for residues, compared against a probe count — is a code finding
in its own right and does not depend on any structure.

## 7 · Prior art and search scope

The searches behind this work are bounded retrieval observations, run in CI on 2026-08-07 and
recorded in the dated decision view. They are reported as such, and no conclusion about the field is
drawn from them. The earlier version stated that the absence of a size-to-output relationship for
transcriptional proximity is "a property of the field rather than of this search", inferred from a
term asymmetry why the floor was inheritable in one direction, and stated that 9MZA is findable only
by its two proteins. **All three are withdrawn.**

**What the retained search records establish.** The two retained index files are inventories: the
induced-proximity-transcription index holds 100 records, 20 of them with a full-text file pointer;
the induced-interface-versus-output index holds 300 records, 51 with a pointer. Those are retained
record and pointer counts, verified at metadata level. Neither index carries a query string, a
request date, a total-hit count, a requested limit, a pagination history or the original response
envelope. **They therefore cannot establish whether 100 and 300 are complete result totals or
retrieval caps, and they cannot establish an absence in any field.**

The term counts previously reported from those corpora — zero occurrences of *buried surface area*,
*interface area*, *contact residue*, *structure of the ternary/induced complex* and *residence time*
across the 20 open-access full texts, `cooperativit*` in one file twice, and a 31 / 6 split of the 51
full texts by readout — are historical author-reported results. The text files and their
classifications are not in the source set retained for this revision, so they are carried with that
status and nothing is inferred from them. The two queries are in any case not matched searches: one
selects proximity and transcription terms and the other interface, cooperativity and residence-time
terms, each chosen before its output was examined, and each result set is selected again by
open-access availability. Exact-term non-occurrence is not proof that a concept or an equivalent
measurement is absent.

**What original retained source bytes do establish**, and what this paper cites them for: the
identity, title, method and resolution of 9MZA; its deposition and release dates; the BCL6 and p300
entity-to-chain assignments; the A2B2 author-defined assembly; and the primary-citation join from the
deposition to the bioRxiv preprint `10.1101/2025.03.14.643404` / PubMed `40166243`, with a Europe PMC
record showing the Cell article `10.1016/j.cell.2026.06.037` (PMID 42476129) as an update of the
preprint record. See Appendix B.

**What the primary abstract establishes.** The abstracts describe recruitment of p300/CBP to
BCL6-associated repressed gene networks, epigenetic reprogramming and cell-death outcomes, and
attribute functional relevance to interactions visible in the induced p300–BCL6 crystal structure.
The primary work therefore already discusses the functional relevance of this induced interface; the
contribution claimed here is the specific computational and measurement observation, not the
discovery of that connection. The abstracts state nothing about the CA/centroid shell score, a
12-probe cutoff, equivalence to a gridded sampler, a minimum necessary interface size, or an
interface-size-to-output calibration. Only the abstracts were read; the full text is not open access
at Europe PMC and was not read here.

**Biological roles, kept straight.** In the cited KAT-TCIP setting, p300/CBP are the recruited
activators and BCL6 is the oncogenic regulator being redirected. The `bcl6` body staged in this
toolchain is a size-and-shape proxy from a different structure and does not become a matched
transcriptional effector because a protein name is shared.

## 8 · Selectivity: withdrawn, not restated

The earlier version stated that this modality's selectivity requirement is not smaller than a
degrader's, requiring the same odds-product difference in induced-complex-fraction space. **That
claim is withdrawn.**

The identity it relied on is derived in
[`selectivity-requirement-sizing.md`](../degrader/selectivity-requirement-sizing.md) for binary
Langmuir occupancy, `theta_i(D) = D/(D + K_i)`, at a shared dose. Its transfer to a ternary
induced-complex fraction, and its use as a sufficient condition for a ternary window, are not derived
there. A simple fixed-free-effector model with equal effector binding and no cooperativity has
`f_i = D/(K_i + 2D)` when `E/K_E = 1`, which never reaches 0.5; hypothetical `K_on = 1`,
`K_anti = 100`, `A = 0.8`, `B = 0.2` clears the binary selectivity-ratio threshold of 16 and still
cannot reach `A` in that ternary model. This is algebra over a specified model, not a biological
calculation and not a statement about any real parameters. A general ternary treatment would require
the species, concentrations, cooperativities, mass balance and dose regime to be specified.

This paper estimates no selectivity requirement, makes no ordering claim between modalities, and
sourced no anti-target ceiling. Unknown requirements are not evidence of equal or greater
requirements.

## 9 · What this paper does not establish

1. **No predicate equivalence.** The census and the sampler use different distance definitions,
   different units and different admission rules (§2). Nothing here shows how the implemented sampler
   would score or admit any deposited complex, and no claim of rejection is made.
2. **No calibration and no bound.** Comparing a census score against the value 12 is hypothetical
   arithmetic. It does not calibrate the filter, does not bound it from above or below, and does not
   establish a lower limit, a monotone interface-size-to-output relationship, or a threshold below
   which any system stops working.
3. **The acceptance fractions are proposal-weighted** and conditional on the implemented radial
   proposal, twelve fixed anchors, one target model and one distance field (§3). They are not
   volumes, probabilities of binding, or linker-feasibility estimates.
4. **The four-body design identifies no controlling variable** and neither establishes nor refutes an
   effect of body size (§4a). No ratio interval and no significance test are reported for the
   eight-rung enumeration, whose four pooled arms use distinct random streams. Separately, in the
   shared-proposal floor ablation the arms share proposals and no cross-arm joint acceptance counts
   were retained, so its empirical cross-arm covariance cannot be estimated from the retained
   marginal counts; no ratio interval is reported for that ablation.
5. **The census is a selected-structure description.** Its entry list was selected, a zero-score
   filter is applied before induced-pair selection, repeated copies and related complexes are
   dependent, and the 6-of-15 result is not a population rate.
6. **n = 1 for the transcriptional system**, in one crystal form, and the two reported interfaces are
   two related instances inside one deposited A2B2 assembly rather than two independent systems.
7. **Admission by excluded volume is a statement about this model's rules.** The bodies are isolated
   ligand-binding or BTB domains with no DNA and no chromatin, and conformational states, anchor
   geometry and other interactions are not represented. The earlier version's claims that no tested
   body has ever failed the gate, that a gate that cannot fail carries no information, and that any
   admitting answer is therefore an upper bound on what a nucleus would allow are withdrawn: no
   observed failures is not impossibility of failure, and omitting constraints in a fixed-coordinate
   model does not establish a quantitative universal bound.
8. **The cross-run comparison is unresolved** and its recorded status is `DISAGREES` (SI §S1).
9. **The literature searches are bounded retrieval observations** (§7) and establish no absence in
   any field.
10. **No selectivity requirement is estimated** (§8).
11. **Original geometry reproduction is not closed.** Published tables reproduce from the retained
    JSON; the coordinate, registry and helper input closure needed to re-run the original geometry is
    not retained (SI §S8).
12. **No biological claim whatsoever.** Nothing here says any molecule binds any target, is
    recruited, is retained on chromatin, or changes transcription. No binding, potency, selectivity,
    efficacy, safety, therapeutic-window or clinical claim is made or implied, for any molecule whose
    structure is measured here. There is no wet-lab component of any kind.
13. **This is not a disease-specific result.** The setting in which the enumeration was computed is
    not part of the claim.

### 9a · What would settle the parked questions

Two of them, stated so a reader can see what is missing rather than being told it is unknowable. A
claim that real complexes are admitted or rejected by this sampler needs results produced under the
same grid construction, query construction, body and target units, excluded constitutive contacts and
full admission rules — or a demonstrated equivalence between the two predicates. A calibration of an
interface requirement needs an explicitly defined necessary property, an appropriate measurement of
it in a relevant functional complex, and an outcome-linked or positive/negative dataset with a stated
calibration procedure. Neither a large-interface control nor a literature count supplies that. This
paper commissions neither, and both would be new work.

## 10 · Methods and reproduction

**Code revision.** All source references are to repository revision
`f43f1495f40d8aff7b4f34bd385d55aac521a500`.

**Geometry.** Rigid-body enumeration from fixed warhead exit-vector anchors against a target distance
field, with acceptance on the predicate tabulated in §2; 576 cells at 300,000 draws for the paired
comparison, 30,000 per arm per anchor for the ablation. Entry point:

```
python3 research/modalities/nr4a3_tcip_reach.py [--samples N] [--arms ID,ID] [--ablation-samples N] [--out PATH]
```

It additionally requires staged target and arm coordinates, both arm registries, helper modules and
model-derived anchor inputs. Those are not enumerated by the settlement's eight dependency hashes,
and `literature-cache` and `ci-input/tcip-interface-floor-2026-08-07` are branch names rather than
immutable versions of every input.

**Structures.** mmCIF fetched in CI from `files.rcsb.org` and parsed with a pure-stdlib reader; every
entry verified from its own `_struct.title` and `_entity.pdbx_description` rather than from its
accession. The census requires a corpus directory of files named `cif_<PDBID>.txt`:

```
python3 research/modalities/nr4a3_induced_interface_census.py <corpus-dir> [out.json]
```

Invoked with no argument it prints its usage and returns exit code 2. The command given in the
earlier SI omitted that argument and therefore did not run the census; this is corrected here and in
SI §S8.

**What reproduces and what does not.** The published tables reproduce from the retained JSON
artifacts by arithmetic. Reproduction of the original geometry and sampling does not close, because
the coordinate and helper inputs are not retained as an immutable set. Stable seeding does not by
itself make full JSON byte-identical between processes, since runtime and date fields are written
into the output. No claim of public archiving or of complete computational closure is made.

## Declarations

**Funding.** None. No grant, contract, sponsor or institutional support of any kind supported this
work.

**Competing interests.** None.

**Ethics.** This work analyses publicly deposited macromolecular coordinates and public literature
records. It involved no new recruitment, no new sampling and no intervention, and generated no new
human data. No ethics approval was sought and none was obtained; no institutional determination of
exemption was requested or issued, and none is reported here.

**Use of artificial intelligence.** Claude (Anthropic) and OpenAI models were used, under the
author's direction, to write and check the analysis code, to run the checks, and to draft and revise
this manuscript. The author directed the work, reviewed the outputs and is responsible for the
content, including any error.

**Author contributions.** Sole author: conception, direction of the analyses, verification of the
outputs and writing.

**Data and code availability.** Every number is read from a committed artifact:
[`nr4a3-tcip-reach.json`](../../modalities/nr4a3-tcip-reach.json) (produced by
`nr4a3_tcip_reach.py`) and
[`nr4a3-induced-interface-census.json`](../../modalities/nr4a3-induced-interface-census.json)
(produced by `nr4a3_induced_interface_census.py`), at the code revision named in §10. Both analyses
are pure-stdlib and offline at analysis time. The coordinate corpus is the set of deposited mmCIF
entries named in the census, originally fetched from `files.rcsb.org`; the exact input corpus is not
retained as an immutable manifest, so independent re-execution of the original geometry is not
claimed. No new data were generated, and nothing here has been publicly archived.

**Scope.** This is a code audit, a parameter-sensitivity analysis and a contact-counting description.
It makes no claim of binding, potency, selectivity, transcriptional output, efficacy, safety,
therapeutic window or clinical readiness for any molecule named here, and no interface reported here
has been experimentally validated by this work.

---

## Appendix A · Corrections and superseded numbers

Superseded values are registered rather than silently dropped; the live text carries only current
values.

1. **Pooled size-axis figures.** [`nr4a3-tcip-route-memo.md`](../../modalities/nr4a3-tcip-route-memo.md)
   recorded in its §4 a pooled ratio spanning **0.865–0.997**, non-overlapping at **5 of 8** rungs,
   and **0.867** at the 12-atom gate; that §4 now carries the corrected values, and the memo's own
   `Appendix · Superseded numbers` holds the retired ones. Recomputed from the primary per-rung data
   in [`nr4a3-tcip-reach.json`](../../modalities/nr4a3-tcip-reach.json) →
   `★_paired_body_size_comparison`, the values are **0.858–0.972**, non-overlapping at **6 of 8**,
   and **0.877** at the gate — which is also what that artifact's own `verdict.★_the_size_axis` block
   reports. The artifact is the one home and is used above. Neither set is registered in
   [`pinned-figures.json`](../pinned-figures.json), which is why `lint_consistency.py` could not
   catch the drift.
2. **An independent re-implementation of the census, discarded.** While the first version of this
   manuscript was being written, the census was re-implemented from scratch against the same
   coordinates as a cross-check. It reproduced 9MZA at 6–7 and 5T35 at 10–11, and independently
   recovered the probe-versus-residue discrepancy of §6. It disagreed on two counts — **7 of 15**
   degrader pairs below the cutoff rather than 6, and the BCL6 BTB homodimer at 62–64 rather than
   66–71 — because it used the literal **CB atom** as the second query point. The sampler's arm
   loader builds that point as the **side-chain centroid** (the variable is named `cb` but holds a
   centroid), which reaches further. The re-implementation was wrong on that point and was discarded
   rather than reconciled; the committed census is the one home. That cross-check was scratch work:
   it was never committed and is absent from this repository's history, so its three disagreeing
   numbers cannot be re-derived from anything retained here and are recorded as a note on the check
   rather than as measurements a reader can verify. What is checkable is the cause it turned on:
   `nr4a3_basin_search.load_arm_from_registry` builds the second query point as `G.centroid(side)`
   over every non-backbone atom, falling back to CA for glycine — a centroid, not the CB atom,
   despite the variable name.
3. **2026-09-08 · Claims withdrawn in this revision.** The frozen version of this manuscript is
   repository revision `f43f1495f40d8aff7b4f34bd385d55aac521a500` (main 28,068 bytes, SHA256
   `2e2b7862c3c6412ff4ae9086fd2acca799ae8999511ca607d1a49e416e82d9a9`; SI 16,663 bytes, SHA256
   `3483c0bbcbd94e4faa5b3de38da8010130b189336b79ac27cd08101c56748ba3`). Every retained count, rate,
   interval and source byte is unchanged by this revision; what changed is what is claimed from them.
   Withdrawn outright, with the section that now covers the subject:
   - that the census applies the sampler's own predicate, and that the measured complexes "would be
     rejected by this sampler's predicate" (§2, §5c);
   - that the structural result bounds the inherited floor from above (§5c);
   - that the acceptance ratio measures orientation-space volume, and the "25 % more admissible
     orientation space" reading (§3);
   - that the ratio is monotone in the floor (§4);
   - that a level offset between the two runs cancels in every within-run ratio (SI §S1);
   - that body size is not the controlling variable and that shape and exit-vector geometry is (§4a);
   - that no tested body has ever failed the excluded-volume gate, that a gate that cannot fail
     carries no information, and that any admitting answer is an upper bound on what a nucleus would
     allow (§9.7);
   - that the literature sweeps establish an absence in the field, a matched prevalence asymmetry, or
     why the floor was inheritable (§7);
   - that 9MZA is findable only by its two proteins (§7, Appendix B);
   - that this modality's selectivity requirement is not smaller than a degrader's, and the general
     ternary-window sufficiency of the binary odds identity (§8);
   - that the small count is a property of the interface rather than of the instrument or of a short
     chain (§5d);
   - that the recruiter clustering of below-cutoff rows shows the threshold is uncalibrated rather
     than noisy (§5e);
   - the reconstruction that the parameter encodes a PROTAC's need for a cooperative buried
     target·E3 interface (§1).
   Corrected rather than withdrawn: the residue interpretation of a 12-probe threshold, which is six
   to twelve residues and not "at most six" (§6); the "roughly half either way" comparison, deleted
   (§6); the ligand-contact counts of 33–42 atoms, which describe the two pairs dropped by the
   zero-score filter and not the two reported interfaces (§5b); the census reproduction command,
   which requires a corpus-directory argument (§10); and the search counts, relabelled as retained
   record and pointer inventories and historical author-reported results (§7).
4. **2026-09-08 · Figure specifications removed.** The frozen version carried a table of six
   unrendered figure specifications. No figure had been drawn, and a specification is not visual
   evidence, so the table is removed rather than carried into a submitted artifact. The numbers those
   specifications pointed at are in §4, §5 and the SI tables. The specification table itself remains
   in repository history at the frozen revision named in item 3.
5. **2026-09-09 · Four interpretation corrections from the root adjudication of the focused
   verification (dated 2026-09-08).** No number, table, status or measured result changes.
   (a) §1, §6 and SI §S2 now state the probe/residue relation as three distinct propositions: at
   least 12 probes *requires* at least six contributing residues; that condition is *not sufficient*
   and is not an equivalent residue-count rule; and there is *no upper bound* of twelve residues, the
   six-to-twelve range being the residues that could supply *exactly* twelve probes. The previous
   sentence "a threshold on probes does not impose any threshold on residues" was false and is
   withdrawn. (b) §4, §9 item 4, SI §S1 and SI §S5 now scope the unavailable cross-arm joint
   acceptance counts, and the shared-stream covariance they would be needed for, to the
   shared-proposal floor ablation. The eight-rung enumeration is a separate object with distinct
   streams for its four pooled arms and retained marginal cell counts; for it, this paper reports no
   ratio interval and no significance test. The former universal phrasing is withdrawn. (c) SI §S1
   now separates the nominal expected count 24 × 0.05 = 1.20, which follows from linearity of
   expectation and assumes 5 % noncoverage per comparison against an exact reference, from the
   separate at-most-two-exclusions rule that labels the family, which was never calibrated as a
   family-level replication test. The `DISAGREES` status, the 19 inside / 5 outside counts, the draw
   counts and the illustrative five-to-three diagnostic are unchanged. (d) The publication-graph
   `PUB-TCIP` current-claim field retires its unqualified modality-general opening; that field is
   parent-owned and is delivered as an unapplied patch, not edited here.

## Appendix B · Citation and source provenance for 9MZA

The deposition's own `rcsb_primary_citation`, read from the retained mmCIF, names a bioRxiv preprint
— *"A Bivalent Molecular Glue Linking Lysine Acetyltransferases to Oncogene-induced Cell Death"*,
Nix et al., DOI `10.1101/2025.03.14.643404`, PubMed `40166243`. The retained RCSB entry response
independently carries `/struct/title`, `/rcsb_primary_citation`, `/rcsb_accession_info` and
`/rcsb_entry_info/resolution_combined`, and records deposition on 2025-01-22 and release on
2025-04-16. The retained Europe PMC response for its DOI query returns two results — the Cell article
(PMID `42476129`, DOI `10.1016/j.cell.2026.06.037`) and the preprint — and its
`commentCorrectionList` records the Cell record as an update of the earlier preprint record. That
join is therefore read from retained original responses rather than from a memo or from a third-party
API. Volume, pages and PMCID for the journal version are not verified.

**A retained file whose label must not be over-read.** The retained record named
`rcsb_cite_pubmed_42476129.txt` is **not** a successful citation object. Its header reports **HTTP
400**, and its body states that search is not enabled on the requested
`rcsb_primary_citation.pdbx_database_id_PubMed` attribute. It is an **invalid-request outcome about
an unsupported search attribute**. It is not a negative search result, it is not an access denial or
an egress refusal, and nothing may be inferred from it about whether any structure or publication
exists. No retry was made and none is required: the valid citation join is the successful entry
response above.

**Experimental method.** The census artifact does not carry `_exptl.method` for this entry — that
field holds the literal string `_details ?`, which is the parser landing on the next mmCIF item
rather than on a method. X-ray diffraction and the 2.1 Å refinement high resolution are read directly
from the retained mmCIF itself. The two reported interfaces are read from the coordinates.

**Availability flags, read narrowly.** Both Europe PMC records carry `isOpenAccess: N` and
`inEPMC: N`; the preprint additionally has a free DOI-link entry and a `cc by` license field. Those
describe Europe PMC's indexing and availability state for those records. They do not mean the
preprint is inaccessible everywhere or unlicensed, and no acquisition route was followed.

**Search outcomes recorded as author narrative.** The RCSB full-text searches for *"KAT-TCIP"* and
*"transcriptional chemical inducer of proximity"* returning zero hits, and the successful
`"BCL6" AND "p300"` search, are recorded in the dated decision view as author-narrative outcomes; the
original response envelopes for those three queries are not in the retained source set. They show
what those queries returned as reported. They do not show that protein names are the only possible
discovery route, and the earlier exclusivity claim is withdrawn.

**One citation gate, and what it moved.** The route's motivating source, DOI `10.1021/jacs.5c05634`,
cleared `verify-refs` (run 31175823997, 7/7 DOIs, 0 parse errors). That moved one permission and zero
measurements: no number in this paper derives from that citation.
