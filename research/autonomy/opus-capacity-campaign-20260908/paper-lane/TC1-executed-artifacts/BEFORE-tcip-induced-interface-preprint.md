---
id: DOC-TCIP-INDUCED-INTERFACE-PREPRINT
title: The induced-interface floor that proximity design inherits from degraders is about twice the interface of the one solved transcriptional CIP
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: The manuscript for publication endpoint PUB-TCIP. A modality-general parameter result — the minimum induced-interface size proximity-design tooling applies by default is inherited from degraders, ablating it inverts the sign of an apparent size penalty, and the only solved transcriptional CIP measures roughly half the inherited floor.
scope: Rigid-body geometric enumeration and contact counting on deposited coordinates. It covers what an inherited parameter costs a modality it was not written for. It is NOT a disease-specific result and makes no binding, potency, selectivity, transcriptional-output, efficacy, safety, therapeutic-window or clinical claim.
audience: [external reviewers, maintainers, autonomous research agents]
date: 2026-08-07
last_verified: 2026-08-07
---

# The induced-interface floor that proximity design inherits from degraders is about twice the interface of the one solved transcriptional CIP

**Preprint draft — not submitted, not posted.**

> **Role: the manuscript for publication endpoint
> [`PUB-TCIP`](../../../systems/views/L3-publications.md).** Every number is read at write time from the
> artifact that owns it: the geometric enumeration from
> [`nr4a3-tcip-reach.json`](../../modalities/nr4a3-tcip-reach.json), the structural census from
> [`nr4a3-induced-interface-census.json`](../../modalities/nr4a3-induced-interface-census.json) with its
> decision view [`tcip-interface-floor-sizing.md`](./tcip-interface-floor-sizing.md). This manuscript
> adds no measurement of its own. Methods and full tables: [SI](./tcip-induced-interface-preprint-si.md).

> ⛔ **THIS IS A MODALITY-GENERAL PARAMETER RESULT, NOT A DISEASE-SPECIFIC ONE.** The enumeration was
> computed in an EWSR1::NR4A3 setting because that is the program it arose in, and **that is the
> setting, not the claim**. Both load-bearing structural results are free of NR4A3 entirely: the
> 6–7-contact measurement is on a BCL6·p300 lymphoma system, and the calibration is over published
> degrader/glue ternaries, none of them NR4A3. Nothing here is evidence about any disease.

---

## Abstract

Chemically induced proximity is increasingly designed with tooling built for targeted protein
degradation. That tooling carries a parameter most users never see: a minimum induced-interface size,
below which a candidate placement is scored as a tethered pair rather than a complex. The parameter is
a **degrader's** requirement — a PROTAC must build a cooperative target·E3 interface across which
ubiquitin is transferred — and it is applied unchanged when the recruited partner is a transcriptional
effector instead of a ligase.

We show that this inherited floor, and not steric bulk, produces the apparent geometric penalty against
smaller second termini. In a paired rigid-body enumeration run from identical anchors, single-domain
bodies accept **0.896×** the orientation space of multi-subunit bodies at the committed floor; ablating
the floor inverts the ratio to **1.254×**. On excluded volume alone the smaller body gets *more*
orientation space, not less.

We then size the floor against deposited structures. Measured under the sampler's own contact predicate
across 22 entries, the **only deposited chemically-induced transcriptional-proximity complex** — the
chemically hijacked BCL6·TCIP3·p300 complex, PDB 9MZA, X-ray 2.1 Å — presents an induced interface of
**6–7 contact points across 4 residues per side**, in both crystallographically independent copies.
The committed floor is **12**, so the real transcriptional CIP fails it in both directions by roughly a
factor of two. Applied to the modality it was actually written for, the same floor rejects **6 of 15**
solved degrader/molecular-glue ternaries, including MZ1·BRD4-BD2·pVHL at **10–11**.

**What this does not establish.** It does not establish a lower limit on induced-interface size, a
monotone relationship between interface size and transcriptional output, or any threshold below which
such a system stops working: the structural bound is **n = 1 system in one crystal form and bounds the
floor from above only**. It does not establish that the apparent size penalty is real — a within-class
control refutes it, since the spread between two bodies of the *same* size exceeds the between-class
contrast at **8 of 8** rungs, so the pooled contrast is confounded and may not be reported as a size
law. The geometric test reports whether a body is *admitted* by excluded volume, a gate no tested body
has ever failed — including a 1 183-residue CRBN–DDB1 assembly — so admitting refutes nothing on its
own; and the bodies are isolated ligand-binding or BTB domains with no DNA and no chromatin, making any
admitting answer an **upper** bound. It establishes nothing about binding, potency, selectivity,
transcriptional output, efficacy, safety, therapeutic window or clinical readiness, and it is not a
disease-specific result. The selectivity requirement for this modality is **not** smaller than a
degrader's, and its anti-target ceiling has no candidate source.

---

## 1 · The parameter nobody re-derived

A bivalent molecule that recruits a transcriptional effector to a target — a transcriptional chemical
inducer of proximity, TCIP — is geometrically a PROTAC with the ligase swapped out. That similarity is
why proximity-design tooling transfers to it, and it is also the trap.

Rigid-body proximity samplers score a candidate placement on excluded volume plus a **minimum induced
interface**. In the sampler used here the parameter is `min_contact_residues = 12`, carrying the comment
*"below this it is a tethered pair, not an interface"*. The justification is a degrader's: ubiquitin
transfer requires a cooperative, buried target·E3 interface, and a placement that merely holds two
proteins near each other will not deliver it.

A TCIP's productive event is not ubiquitin transfer. Whether it requires a comparable induced interface,
a smaller one, or a different quantity altogether had not been established. The requirement is properly
a **residence time** at an occupied locus; a contact count is a proxy for it whose calibration constant
is a property of the recruited partner's mechanism, and the degrader's constant may not be inherited.

This paper does not size that requirement. It shows what the inherited parameter **costs**, and it
bounds the floor from above with a real structure.

## 2 · The sign inverts across the floor

We ran a paired rigid-body enumeration: six staged bodies, identical warhead anchors, an identical
target frame, an identical distance field, and one linker-length ladder — 576 cells at 300 000 samples
each. Two bodies are single-domain E3 recruiters (`birc2`, 92 residues; `mdm2`, 94), two are
multi-subunit E3s (`crbn`, 1 183; `vhl`, 340). Pooled acceptance by size class is the paired contrast.

At the committed floor the single-domain pool accepts **less** orientation space than the multi-subunit
pool at every rung. Taken alone that reads as *"an effector-size terminus is geometrically harder"* —
the opposite of the intuition that a smaller second terminus is a smaller problem.

**Re-running the identical cells with only the interface floor changed inverts it.**

| `min_contact_residues` | single-domain | multi-subunit | ratio |
|---|---|---|---|
| **12 (committed)** | 0.000810 | 0.000904 | **0.896** |
| 6 | 0.008771 | 0.007822 | **1.121** |
| **0 (pure steric)** | 0.080079 | 0.063875 | **1.254** |

*(12-atom linker rung, 30 000 samples per arm per pose;
[`nr4a3-tcip-reach.json`](../../modalities/nr4a3-tcip-reach.json) → `★_interface_floor_ablation`.)*

On excluded volume alone the smaller body gets **25 % more** admissible orientation space. The entire
measured penalty is the induced-interface requirement, and it is monotone in the floor. The result
reproduces at two sample counts and across a determinism fix (SI §S1).

**So a TCIP scored at the committed floor is charged for an induced interface nobody has shown the
modality needs.** Which floor is correct is not settled by this ablation, and the enumeration declines
to pick one: the operative discipline is to report at **both** floors and assert only what holds at
both.

### 2a · The size axis does not survive a re-draw, and we do not claim it

The pooled contrast must not be read as a size law, and the same artifact that produces it refutes that
reading. Across the 8 rungs the single/multi ratio spans **0.858–0.972**, with 95 % intervals
overlapping at 2 rungs; at the 12-atom gate it is **0.877**. But the **spread within a size class
exceeds the between-class contrast at 8 of 8 rungs**: two ~90-residue single-domain bodies differ from
each other by up to **1.421×**, while the classes differ by at most **1.165×**. `birc2` outperforms
`crbn` at every rung despite being 13× smaller.

⇒ **Body size is not the controlling variable; the individual body's shape and exit-vector geometry
is.** The pooled contrast is confounded. What survives is not the size ranking but the **sign inversion
across the floor**, which is a statement about the parameter and is measured on the same bodies in both
arms.

## 3 · The floor is bounded from above by a real structure

If a real chemically-induced *transcriptional* complex exists whose induced interface is smaller than
the floor, the floor is not a necessary property of induced proximity.

22 deposited entries were measured under the sampler's own predicate — the same three distance bands
and the same query points the placement loop uses
([`nr4a3-induced-interface-census.json`](../../modalities/nr4a3-induced-interface-census.json)). Because
the predicate is one-sided — an arm is sampled against a target, not the reverse — every pair is
measured **both ways** and both numbers are reported; no orientation is promoted.

**PDB 9MZA** — *"Chemically Hijacked BCL6–TCIP3–p300 Complex"*, X-ray **2.1 Å** — is the only deposited
chemically-induced transcriptional-proximity complex found. Its induced BCL6·p300 interface measures:

| copy | contact points (both directions) | residues with a contact point, per side |
|---|---|---|
| A/D | **6 / 7** | 4 and 4 |
| B/C | **7 / 6** | 4 and 4 |

**6–7 contact points across 4 residues per side, identical in both crystallographically independent
copies, failing the floor of 12 in both directions by roughly a factor of two.**

**Two controls make that number mean what it says.**

*Saturation.* The same predicate, in the same coordinate file, reads the constitutive BCL6 BTB
homodimer at **66–71** contact points across 39–42 residues per side; in the independent 7LWG crystal
the same homodimer reads **64–67**. The instrument reads large interfaces as large — an order of
magnitude above the induced one — so the small number is a property of the interface, not of the
instrument.

*Truncation.* Both partners are substantially resolved: the BCL6 chains contribute 122–123 residues
(244–246 query points) and the p300 chains 112–113 (224–226). The small count is therefore a property of
the interface rather than of a short chain. The bridging ligand is itself **81 heavy atoms** and contacts
33–42 atoms' worth of each partner — a large molecule creating a tiny protein–protein interface.

## 4 · The floor also misfits the modality it came from

The floor is a degrader's parameter. Measured against 15 solved degrader/molecular-glue induced pairs,
it rejects **6 of 15** in at least one direction — including **MZ1·BRD4-BD2·pVHL** (5T35), which reads
**10–11** on the weaker side across its two copies, and **6SIS** at 10–11.

A threshold that would reject a substantial share of its own modality's solved ternaries is not a
calibrated requirement being applied outside its range; it is an uncalibrated one. This is a statement
about the parameter and **not** a claim about whether those degraders work — they demonstrably do.

## 5 · What this does not establish

Stated plainly, because each has a specific and non-obvious reach.

1. **The structural bound bounds from ABOVE only.** It shows the floor is not necessary. It does **not**
   establish a lower limit, a monotone size-to-output relationship, or a threshold below which such a
   system stops working. **n = 1 system, one crystal form**; two crystallographically independent copies
   are not two systems.
2. **"Admits" is an excluded-volume statement, and no tested body has ever failed it** — including a
   1 183-residue CRBN–DDB1 assembly. A gate that cannot fail carries no information when it passes.
3. **The bodies are isolated ligand-binding or BTB domains, not proteins**, with no DNA and no
   chromatin. Any admitting answer is therefore an **upper** bound on what a nucleus would allow.
4. **One staged body is not comparable and is not pooled.** `brd4_bd1`'s exit-atom exposure is 13.65 Å,
   outside the committed E3 range of 5.00–5.79 Å; `bcl6` at 5.44 Å is inside. `brd4_bd1`'s acceptance
   may not be pooled with or ranked against the others, and it is excluded from every pooled figure.
5. **The named-effector result is narrower than it looks.** `bcl6` (7LWG, 243 residues) and `brd4_bd1`
   (4ZC9, 127) admit at every rung down to a 6-atom linker. But the paired size comparison, the
   within-class control and the floor ablation are computed on the **four committed bodies only**;
   `birc2` and `mdm2` remain size-and-shape proxies there, and nothing about a named effector may be
   read off them. The ablation is a statement about the sampler's inherited parameter, not about any
   effector.
6. **The selectivity requirement is not smaller here.** It needs the same odds-product difference in
   induced-complex-fraction space that a degrader needs, and its anti-target ceiling has **no candidate
   source**. Recruiting an effector rather than a ligase does not relax it.
7. **No biological claim whatsoever.** Nothing here says any effector binds any target, is recruited, is
   retained on chromatin, or changes transcription. No binding, potency, selectivity, efficacy, safety,
   therapeutic-window or clinical claim is made or implied, for any molecule whose structure is measured
   here.
8. **This is not a disease-specific result.** The setting in which the enumeration was computed is not
   part of the claim.

### 5a · What would settle it

A **series**: two or more induced interfaces of different size, within one transcriptional system, with
matched transcriptional output. That is what converts a bound into a calibration curve, and no such
series exists for any transcriptional CIP — the modality's literature does not characterise its own
induced interface (SI §S7). Building one is wet-lab work.

## 6 · A discrepancy inside the parameter itself

`min_contact_residues` reads as a count of residues. The placement loop does not count residues: it
iterates a query set built as **two points per residue** — the CA and the side-chain centroid — and
increments per **point**. It is also a three-band `if/elif` chain, so a probe scores as contact only in
the shell between the soft-clash and contact radii; closer than that it is a clash. The committed floor
of 12 is therefore **12 points, as few as 6 residues**, not 12 residues.

We do not resolve which reading was intended, and the conclusion does not need it: the headline
comparison is like-for-like on both sides — **6–7 points against a 12-point floor**, or **4 residues per
side against a floor of at most 6 residues' worth of probes**. Roughly half either way.

## 7 · Methods, in one paragraph

Geometry: rigid-body enumeration from fixed warhead exit-vector anchors against a target distance field,
with acceptance on hard clash, a soft-clash budget and the interface floor; 576 cells at 300 000 samples
for the paired comparison, 30 000 per arm per pose for the ablation. Structures: mmCIF fetched in CI
from `files.rcsb.org`, parsed with a pure-stdlib reader; every entry verified from its own `_struct.title`
and `_entity.pdbx_description` rather than from its accession, so a mis-remembered identifier surfaces as
a mismatched title rather than as a number attributed to the wrong complex. Both analyses are
deterministic and offline. Full methods, tables and controls: [SI](./tcip-induced-interface-preprint-si.md).

## 8 · Figures

| # | figure | source artifact |
|---|---|---|
| **1** | The sign inversion — pooled acceptance by size class at floors 12 / 6 / 0 with 95 % intervals, the ratio annotated on each pair | `nr4a3-tcip-reach.json` → `★_interface_floor_ablation` |
| **2** | Why the size axis is confounded — per-arm acceptance at each of the 8 rungs, arms coloured by size class, with within-class spread and between-class contrast drawn as bars | `nr4a3-tcip-reach.json` → `★_paired_body_size_comparison` |
| **3** | The bound — measured contact points for every induced pair in the census, ordered, with the floor of 12 as a horizontal line and both directions shown as a range; 9MZA and the 15 degrader pairs distinguished | `nr4a3-induced-interface-census.json` |
| **4** | 9MZA against its own control — the induced BCL6·p300 interface (6–7) beside the constitutive BCL6 BTB homodimer measured in the same file (66–71) and in independent 7LWG (64–67) | `nr4a3-induced-interface-census.json` |
| **S1** | Saturation — every constitutive pair in the corpus on the same predicate, showing the dynamic range | SI §S6 |
| **S2** | The literature gap — term counts across the modality-wide open-access corpus against the degrader corpus | SI §S7 |

## Appendix A · Corrections and superseded numbers

Superseded values are registered rather than silently dropped; the live text carries only current values.

1. **Pooled size-axis figures.** [`nr4a3-tcip-route-memo.md`](../../modalities/nr4a3-tcip-route-memo.md) §4
   records the pooled ratio as spanning **0.865–0.997**, non-overlapping at **5 of 8** rungs, and
   **0.867** at the 12-atom gate. Recomputed from the primary per-rung data in
   [`nr4a3-tcip-reach.json`](../../modalities/nr4a3-tcip-reach.json) → `★_paired_body_size_comparison`, the
   values are **0.858–0.972**, non-overlapping at **6 of 8**, and **0.877** at the gate — which is also
   what that artifact's own `verdict.★_the_size_axis` block reports. The artifact is the one home and is
   used above. Neither set is registered in
   [`pinned-figures.json`](../pinned-figures.json), which is why `lint_consistency.py` could not catch
   the drift.
2. **An independent re-implementation of the census, discarded.** While this manuscript was being
   written, the census was re-implemented from scratch against the same coordinates as a cross-check.
   It reproduced 9MZA at 6–7 and 5T35 at 10–11, and independently recovered the point-versus-residue
   discrepancy of §6. It disagreed on two counts — **7 of 15** degrader pairs rejected rather than 6,
   and the BCL6 BTB homodimer at 62–64 rather than 66–71 — because it used the literal **CB atom** as
   the second query point. The sampler's arm loader builds that point as the **side-chain centroid**
   (the variable is named `cb` but holds a centroid), which reaches further. The re-implementation was
   wrong on that point and was discarded rather than reconciled; the committed census is the one home.

## Appendix B · Citation provenance for 9MZA

The deposition's `rcsb_primary_citation` names a **bioRxiv preprint** — *"A Bivalent Molecular Glue
Linking Lysine Acetyltransferases to Oncogene-induced Cell Death"*, Nix et al., DOI
`10.1101/2025.03.14.643404`, PubMed `40166243`. The bioRxiv API records that preprint as published at
DOI `10.1016/j.cell.2026.06.037` (Cell). ⚠ The forward link to the journal version is read from bioRxiv,
**not** from the PDB entry, which carries the preprint citation only. A EuropePMC full-text search for
`"9MZA"` returns **hitCount 0**, so no citing full text was available to cross-check. Volume, pages and
PMCID for the journal version are **not verified**.

⚠ **A structure can exist and be invisible to the search terms a reader would try first.** RCSB
full-text searches for *"KAT-TCIP"* and *"transcriptional chemical inducer of proximity"* each returned
zero hits; 9MZA is findable only by its two proteins.

The route's motivating source, DOI `10.1021/jacs.5c05634`, cleared `verify-refs` (run 31175823997, 7/7
DOIs, 0 parse errors). ⚠ That moved one permission and **zero measurements**: no number in this paper
derives from that citation.
