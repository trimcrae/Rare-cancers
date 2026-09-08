---
id: DOC-TCIP-INDUCED-INTERFACE-PREPRINT-SI
title: Supporting Information — the induced-interface floor that proximity design inherits from degraders
level: L4
kind: manuscript
status: live
canonical_for: []
purpose: Methods, complete tables and every control for the PUB-TCIP manuscript, so each headline number can be traced to the artifact that owns it and re-derived.
scope: Methods and tables for the geometric enumeration and the structural census. It covers reproduction and controls. It covers no binding, potency, selectivity, transcriptional-output, efficacy, safety or clinical statement.
audience: [external reviewers, maintainers, autonomous research agents]
date: 2026-08-07
last_verified: 2026-08-07
---

# Supporting Information

**Companion to [`tcip-induced-interface-preprint.md`](./tcip-induced-interface-preprint.md).**
Every number is read from a committed artifact; this file adds no measurement of its own. The decision
view over the structural census, with the full provenance narrative, is
[`tcip-interface-floor-sizing.md`](./tcip-interface-floor-sizing.md).

---

## S1 · Methods — the geometric enumeration

**Artifact:** [`nr4a3-tcip-reach.json`](../../modalities/nr4a3-tcip-reach.json).
**Code:** [`nr4a3_tcip_reach.py`](../../modalities/nr4a3_tcip_reach.py), scoring inherited unchanged from
[`nr4a3_basin_search.py`](../../modalities/nr4a3_basin_search.py).

Six bodies are staged from deposited coordinates and placed by rigid-body Monte Carlo from **fixed
warhead exit-vector anchors** against a target distance field. A placement is accepted when it has no
hard clash, no more than the permitted soft clashes, and at least `min_contact_residues` query points in
the contact band.

The paired comparison covers **576 cells** (body × warhead anchor × linker length) at **300 000 samples**
per cell. The floor ablation re-runs the identical cells at the 12-atom rung with **only**
`min_contact_residues` changed, at 30 000 samples per arm per pose.

**Pooling.** The size contrast pools `single_domain = [birc2, mdm2]` against
`multi_subunit = [crbn, vhl]`. `bcl6` and `brd4_bd1` are staged named effectors and are **excluded from
every pooled figure** — `bcl6` because the pooled contrast is a proxy statement a named effector may not
be read into, `brd4_bd1` additionally because its exit vector is not comparable (§S4).

**Determinism.** Per-cell seeds were originally derived from `hash(arm_id)`, which Python salts per
process, so the artifact did not reproduce between runs. Fixed to `zlib.crc32` and verified: two full
runs under `PYTHONHASHSEED=0` and `PYTHONHASHSEED=99` produce byte-identical JSON. The committed numbers
are from the deterministic run. The ~0.13-wide swing that the defect produced is a fair estimate of how
little the pooled ratio is worth, and is one reason §2a of the manuscript declines to report it as a
size law.

## S2 · Methods — the structural census

**Artifact:** [`nr4a3-induced-interface-census.json`](../../modalities/nr4a3-induced-interface-census.json).
**Code:** [`nr4a3_induced_interface_census.py`](../../modalities/nr4a3_induced_interface_census.py).

22 mmCIF entries were fetched in CI from `files.rcsb.org` (the development sandbox's egress proxy
answers `403` on `CONNECT` to RCSB) and cached on the `literature-cache` branch. mmCIF rather than PDB
format is used because the fetch pipeline passes bodies through an HTML stripper that collapses runs of
spaces — harmless to whitespace-delimited mmCIF, fatal to the fixed-column PDB layout.

**The predicate is the sampler's, taken rather than restated.** For each of an arm's query points, the
distance to the nearest heavy atom of the other chain is binned:

| band | outcome |
|---|---|
| `d < hard_clash_A` (3.0 Å) | hard clash — placement rejected outright |
| `hard_clash_A ≤ d < soft_clash_A` (3.6 Å) | soft clash — a budget applies |
| `soft_clash_A ≤ d ≤ contact_A` (6.0 Å) | **contact**, counted into `n_contact` |
| `n_contact < min_contact_residues` (12) | rejected: *"a tethered pair, not an interface"* |

**Query points are two per residue: the CA and the side-chain centroid**, exactly as
`load_arm_from_registry` builds them (`query = ca_list + cb_list`, where the second list holds the
centroid of every non-backbone atom and falls back to CA for glycine).

> ⚠ **`min_contact_residues` counts POINTS, not residues, despite its name — so 12 points is as few as
> 6 residues.** Every row below reports both. This is the discrepancy §6 of the manuscript declines to
> resolve and reports at both readings.

**The predicate is one-sided** — an arm is sampled against a target, not the reverse — so every pair is
measured **both ways** and both numbers are reported. No orientation is promoted.

**Two kinds of induced pair, kept distinguishable.** *Ligand-bridged* pairs (one molecule touches both
partners — a PROTAC, a glue, rapamycin) are read off the coordinates. *Allosteric* pairs (an agonist
inside one partner's pocket recruiting a coactivator, which no single structure can prove is
ligand-dependent) are curated by name with a stated reason and labelled `allosteric_curated`, so a
reader can drop them and recompute. Every entry's identity is verified from its own `_struct.title` and
`_entity.pdbx_description` rather than from its accession.

## S3 · Table S1 — the census by class

**22 entries fetched, 22 parsed**, every title and chain description verified from the file itself.

| class | entries | induced pairs | contact points, smaller direction | fails floor 12 in ≥1 direction | in BOTH |
|---|---|---|---|---|---|
| **`tcip`** — 9MZA, BCL6·TCIP3·p300 | 1 | 2 | **6 – 6** | **2 of 2** | **2 of 2** |
| `induced_transcriptional` — incl. 9MZA and 5 nuclear-receptor/coactivator entries | 6 | 12 | 6 – 19 | 2 of 12 | 2 of 12 |
| `degrader_or_glue` — 8 PROTAC / molecular-glue ternaries | 8 | 15 | 5 – 23 | **6 of 15** | 1 of 15 |
| `cid_proximity` — rapamycin, auxin, ABA, gibberellin | 7 | 7 | 11 – 53 | 1 of 7 | 0 of 7 |
| `constitutive` — 7LWG BCL6 BTB homodimer (contrast, never pooled) | 1 | 1 | 64 | 0 | 0 |

## S4 · Table S2 — the 15 degrader/glue induced pairs

All ligand-bridged and measured from coordinates; none curated. Ordered by the smaller direction.

| entry | chains | contact points (min / max) | partners |
|---|---|---|---|
| **7Q2J** | C/D | **5 / 12** | pVHL + WD-repeat-containing protein |
| **6SIS** | A/D | **10 / 11** | BRD4 + pVHL |
| **5T35** | E/H | **10 / 14** | BRD4 BD2 + pVHL (MZ1) |
| **5T35** | A/D | **11 / 14** | BRD4 BD2 + pVHL (MZ1) |
| **6HAX** | A/B | **11 / 18** | SMARCA2/SNF2L2 + pVHL |
| **6HAX** | E/F | **11 / 18** | SMARCA2/SNF2L2 + pVHL |
| 6SIS | E/H | 13 / 16 | BRD4 + pVHL |
| 6BN7 | B/C | 17 / 19 | cereblon + BRD4 |
| 6BOY | B/C | 18 / 23 | cereblon + BRD4 |
| 5FQD | B/C | 21 / 22 | cereblon + CK1α |
| 5FQD | E/F | 21 / 22 | cereblon + CK1α |
| 6H0F | E/F | 21 / 22 | cereblon + Ikaros |
| 6H0F | K/L | 22 / 22 | cereblon + Ikaros |
| 6H0F | B/C | 22 / 23 | cereblon + Ikaros |
| 6H0F | H/I | 23 / 25 | cereblon + Ikaros |

**Bold = below the floor of 12 in at least one direction: 6 of 15.** The rejected set is entirely the
VHL-recruiting and SMARCA2 series; every cereblon ternary clears it. That the floor's failures cluster
by recruiter rather than scattering is itself evidence it is uncalibrated rather than noisy.

### Exit-vector comparability (enumeration bodies)

Committed E3 exposure range: **5.00–5.79 Å**.

| arm | partner class | exit exposure (Å) | inside range |
|---|---|---|---|
| `bcl6` | transcriptional effector | 5.44 | yes |
| `birc2` | E3 recruiter | 5.04 | yes |
| `brd4_bd1` | transcriptional effector | **13.65** | **no** |
| `crbn` | E3 recruiter | 5.11 | yes |
| `mdm2` | E3 recruiter | 5.79 | yes |
| `vhl` | E3 recruiter | 5.00 | yes |

The exit-atom offset displaces a body relative to the target before any rotation, so an arm outside the
committed range is **not comparable** and its acceptance may not be pooled with or ranked against the
others. ⚠ The sign of that effect is not predictable and is not claimed: a larger offset both moves the
body clear of the target (easier) and pushes it out of the shell it must occupy (harder). This bounds
what may be said with `brd4_bd1`; it does not invalidate the arm.

## S5 · Table S3 — the 8 ladder rungs, and why the size axis is confounded

| linker atoms | shell hi (Å) | single/multi ratio | between-class contrast | within > between | 95 % CI overlap |
|---|---|---|---|---|---|
| 6 | 7.5 | 0.928 | 1.077 | **yes** | no |
| 8 | 10.0 | 0.970 | 1.031 | **yes** | yes |
| 10 | 12.5 | 0.891 | 1.122 | **yes** | no |
| 12 | 15.0 | **0.877** | 1.140 | **yes** | no |
| 14 | 17.5 | 0.858 | 1.165 | **yes** | no |
| 16 | 20.0 | 0.890 | 1.124 | **yes** | no |
| 20 | 25.0 | 0.936 | 1.069 | **yes** | no |
| 24 | 30.0 | 0.972 | 1.029 | **yes** | yes |

**The within-class spread exceeds the between-class contrast at 8 of 8 rungs** — up to **1.421×** within
a class against at most **1.165×** between them. ⇒ the pooled contrast is confounded by individual body
shape and may not be reported as a size law.

### Floor ablation, per arm (12-atom rung, 30 000 samples/arm/pose)

| arm | n_res | class | floor 12 | floor 6 | floor 0 |
|---|---|---|---|---|---|
| `bcl6` | 243 | multi_subunit | 0.000778 | 0.006183 | 0.059336 |
| `birc2` | 92 | single_domain | 0.000917 | 0.009511 | 0.092311 |
| `brd4_bd1` | 127 | single_domain | 0.000453 | 0.008356 | 0.237936 |
| `crbn` | 1183 | multi_subunit | 0.000783 | 0.006697 | 0.047200 |
| `mdm2` | 94 | single_domain | 0.000703 | 0.008031 | 0.067847 |
| `vhl` | 340 | multi_subunit | 0.001025 | 0.008947 | 0.080550 |

⚠ `bcl6` and `brd4_bd1` appear here because they ran in the same pass. They are **not** in the pooled
rows of the manuscript's §2 table, and the ablation is a statement about the sampler's inherited
parameter, not about any named effector.

## S6 · Controls

### Saturation — the instrument is not the story

`A1BUC` (TCIP3, **81 heavy atoms**) also spans the **two BCL6 protomers**, because the BTB lateral
groove is formed *between* them. That pair is constitutive, is excluded by name from the induced class,
and serves as the control:

| pair | contact points |
|---|---|
| BCL6 BTB homodimer in **9MZA** (same file as the induced pair) | **66 / 71** |
| the same homodimer in independent entry **7LWG** | **64 / 67** |
| the induced BCL6·p300 pair in 9MZA | **6 / 7** |

Two crystals, two depositions, one instrument, one answer: the constitutive interface reads an order of
magnitude above the induced one. A predicate that could not read a large number would not have.

### Truncation — checked rather than assumed

Both partners are substantially resolved. The BCL6 chains contribute **244 and 246** query points
(**122–123** residues); the p300 chains **224 and 226** (**112–113** residues). The small count is a
property of the interface, not of a short chain. The bridging ligand contacts **33–42** atoms' worth of
each partner — a large molecule creating a tiny protein–protein interface.

### Independent copies

9MZA holds two crystallographically independent copies of the induced complex (chains A·D and B·C).
Both read **6 and 7 contact points, 4 residues on each side**. Copies are reported separately and never
averaged, so a single-copy artefact cannot hide.

## S7 · Why no calibration curve exists — the literature, counted

Two Europe PMC sweeps, both run in CI, establish that the absence of a size-to-output relationship for
transcriptional proximity is a property of the field rather than of this search.

**(a) The modality-wide sweep.** *Induced proximity / chemically induced dimerization / chemical inducer
of proximity / TCIP* **AND** *transcription / transcriptional / gene expression / transcription factor*
returned **100 records, 20 with open-access full text**. Across all 20 full texts the terms *buried
surface area*, *interface area*, *contact residue*, *structure of the ternary/induced complex* and
*residence time* occur **0 times**; `cooperativit*` occurs in one file, twice.

**(b) The asymmetry against degraders, measured rather than asserted.** *Cooperativity / residence time /
buried surface area / interface area* **AND** *induced proximity / molecular glue / PROTAC / ternary
complex / degrader* returned **300 records, 51 with open-access full text**. Of those 51, **31** pair an
interface property with a **degradation** readout; **6** pair one with anything transcription-shaped, and
none of those six relates interface size to transcriptional output.

⇒ **The field routinely relates the induced interface to output when the output is degradation, and does
not when it is transcription.** That asymmetry is why the floor was inheritable in one direction and
unsized in the other, and it is what makes a single deposited transcriptional structure worth this much.

## S8 · Reproduction

```
python3 research/modalities/nr4a3_induced_interface_census.py   # structural census, offline, $0
python3 research/modalities/nr4a3_tcip_reach.py                 # geometric enumeration, CPU, $0
```

Both are deterministic and offline at analysis time. The coordinate corpus is on the `literature-cache`
branch; the fetch inputs are on `ci-input/tcip-interface-floor-2026-08-07`.

## S9 · Scope ceiling, restated

This SI documents contact counting on deposited coordinates and rigid-body excluded-volume enumeration.
It makes **no** claim about binding, potency, selectivity, transcriptional output, efficacy, safety,
therapeutic window or clinical readiness, for any molecule whose structure is measured here. The
structural bound is **n = 1 transcriptional CIP system in one crystal form** and bounds the inherited
floor from **above only**: it does not establish a lower limit, a monotone relationship between interface
size and transcriptional output, or a threshold below which such a system stops working. It is a
modality-general parameter result and is not evidence about any disease.
