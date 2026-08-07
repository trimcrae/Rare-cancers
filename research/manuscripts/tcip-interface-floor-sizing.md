---
id: DOC-TCIP-INTERFACE-FLOOR-SIZING
title: Sizing the induced-interface floor a transcriptional CIP actually needs — measured from deposited coordinates
level: L3
kind: manuscript
status: live
canonical_for:
  - the measured induced-interface size of deposited chemically-induced complexes under nr4a3_basin_search's own contact predicate
  - the disposition of BLK-TCIP-INTERFACE-FLOOR
purpose: >
  Retire or escalate BLK-TCIP-INTERFACE-FLOOR. The blocker's own retired_by_action asks for a
  characterised induced interface, in any chemically-induced transcriptional-proximity system, tied
  to a transcriptional readout. This file records the attempt to read the one source the blocker
  named, the widening that followed, and the measurement that resulted.
scope: >
  Geometry and provenance only. No binding, activity, degradation, potency, selectivity, efficacy,
  safety, therapeutic-window or clinical statement about any molecule, including every molecule whose
  crystal structure is measured below.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-07
last_verified: unverified
---

# Sizing the induced-interface floor a transcriptional CIP actually needs

> **$0.** No GPU, no rental, no purchase, nobody contacted. Every fetch went through
> `fetch-literature.yml` on a GitHub Actions runner, which is free, because the dev sandbox's egress
> proxy answers `403` on `CONNECT` to `pmc.ncbi.nlm.nih.gov`, `www.ebi.ac.uk`, `pubs.acs.org` and
> `files.rcsb.org` alike. All analysis is pure-stdlib CPU.
>
> **Every number below has its one home in
> [`nr4a3-induced-interface-census.json`](../modalities/nr4a3-induced-interface-census.json)**,
> produced by [`nr4a3_induced_interface_census.py`](../modalities/nr4a3_induced_interface_census.py).
> This file is the decision view over it and adds no measurement of its own.
>
> **Subordinate to [`nr4a3-program-map.md`](./nr4a3-program-map.md).** The graph edits this implies
> are **described and routed, never applied by hand** — [§7](#7--graph-edits--described-and-routed-not-applied).

---

## 1 · The one-line answer

**`BLK-TCIP-INTERFACE-FLOOR` retires on its own stated terms, and the floor is bounded far BELOW the
value the route inherited.**

The single deposited structure of a chemically induced **transcriptional**-proximity complex — PDB
**9MZA**, *"Chemically Hijacked BCL6–TCIP3–p300 Complex"*, X-ray **2.1 Å** — has an induced
BCL6·p300 interface of **6–7 contact points across 4 residues per side**, measured under
`nr4a3_basin_search.PARAMS`' own predicate. The route's inherited floor is
`min_contact_residues = 12`. **The real transcriptional CIP fails that floor in both directions, by
roughly a factor of two.**

⇒ The sign question [`selectivity-requirement-sizing.md` §3.1](./selectivity-requirement-sizing.md)
recorded as unknown — *"it could be smaller / it could be larger"* — now has one data point, and it
says **smaller**.

---

## 2 · Task 1 — the Supporting Information: what happened, stated as refusals rather than as a failure

The blocker names the SI of `EV-EB-TCIP-2025` (`10.1021/jacs.5c05634`, PMC12851799) as *"the one
place left to look before this escalates to `requires_wet_lab`"*. The cached main text names the
file itself: **`NIHMS2124316-supplement-Supporting_Information.pdf`, 10.8 MB**, described in the
article as *"Supporting Figures 1–11, Chemical Synthesis, Supporting Tables 1–11, RNA-seq
dendrograms, and additional references"*.

**It was not retrieved, and each host refused it for a different, identified reason.** Six URLs
across four hosts, over two CI rounds:

| route | HTTP | what came back |
|---|---|---|
| `pmc.ncbi.nlm.nih.gov/articles/instance/12851799/bin/…pdf` | **200** | an **85-character** body: *"Preparing to download … HHS Vulnerability Disclosure"* — PMC's download interstitial, not the file |
| … same, with `?download=true` | **200** | byte-identical 85-character interstitial |
| `www.ncbi.nlm.nih.gov/pmc/articles/PMC12851799/bin/…pdf` | 404 | — |
| Europe PMC `…/PMC12851799/supplementaryFiles` | 200 | *"Article with id PMC12851799 is not open access one"* |
| NCBI OA service `oa.fcgi?id=PMC12851799` | 200 | *"identifier 'PMC12851799' is not Open Access"* |
| `pubs.acs.org/doi/suppl/…/ja5c05634_si_001.pdf` | 403 | Cloudflare *"Just a moment…"* |

⛔ **Two of those are NCBI answering in its own words that this article is outside the open-access
subset.** That is a licence fact, not a fetch that merely failed, and it is the reason the interstitial
cannot be walked past: there is no open copy of that file to walk to. The article's own bioRxiv
preprint (which the main text says exists, posted 2025-03-17) is a possible open route; bioRxiv
answered **429** to every request from the runner in both rounds, which is a rate limit and remains
retryable.

### 2.1 · What WAS read, counted the same way, so the two are directly comparable

The 2026-08-07 $0 read counted terms in the committed PMC HTML copy. A **second, independent copy of
the same article** is also in the cache and had not been counted: the accepted-manuscript PDF from the
authors' own lab site (`labs.dana-farber.org/stegmaierlab/…/Bond-JACS-2025.pdf`), which **carries the
Methods** the HTML render also carries. Both were counted with one term list:

| term | PMC HTML copy | accepted-manuscript PDF |
|---|---|---|
| `cooperativ*` | 0 | 0 |
| `linker` | 0 | 0 |
| `contact residue` | 0 | 0 |
| `interface` | 1 | 1 |
| `crystal structure` | 0 | 0 |
| `co-crystal` | 0 | 0 |
| `cryo-EM` | 0 | 0 |
| `residence time` | 0 | 0 |
| `k_off` | 0 | 0 |
| `buried surface` | 0 | 0 |
| `ternary structure` | 0 | 0 |
| `PDB` / `Protein Data Bank` | 0 | 0 |

The single `interface` occurrence is the same one in both: a 1998 PNAS **reference title** about
redesigning an FKBP–ligand interface. **`PDB` / `Protein Data Bank` at zero in both copies is the
load-bearing new row**, and it is corroborated by the article's own Data Availability Statement,
which lists **GEO accessions only** (`GSE290895` RNA-seq, `GSE290894` ChIP-seq, `GSE290893`
ATAC-seq) and **no structural accession of any kind**. A paper that deposited a structure of its
induced complex would say so there. That materially reduces what the unread SI could have held —
without pretending it was read.

⚠ **An absent reading is not a reading of absence, and this section is a reading of absence in the
two copies that exist.** The SI itself remains unread. What follows does not depend on it.

---

## 3 · Task 2 — widening, and where the answer actually was

Two Europe PMC sweeps and one structural census, all in CI:

**(a) The modality-wide literature sweep.** `TITLE_ABS` search over *induced proximity / chemically
induced dimerization / chemical inducer of proximity / TCIP* **AND** *transcription / transcriptional
/ gene expression / transcription factor* returned **100 records, 20 with open-access full text**
(corpus `literature/induced-proximity-transcription-2026-08-07` on `literature-cache`; the run's
known-positive control PMID was required and returned). Across all 20 full texts, the terms *buried
surface area*, *interface area*, *contact residue*, *structure of the ternary/induced complex* and
*residence time* occur **0 times**; `cooperativit*` occurs in one file, twice. The modality's
literature does not characterise its own induced interface.

**(a′) And the asymmetry against degraders is measurable, not impressionistic.** A second sweep —
*cooperativity / residence time / buried surface area / interface area* **AND** *induced proximity /
molecular glue / PROTAC / ternary complex / degrader* — returned **300 records, 51 with open-access
full text** (corpus `literature/induced-interface-vs-output-2026-08-07`). Of those 51, **31 pair an
interface property with a DEGRADATION readout** (`DC50`/`Dmax`/ubiquitination/degradation
efficiency); **6** pair one with anything transcription-shaped, and reading those six, none is a
transcriptional-proximity system relating interface size to transcriptional output — they are
degrader papers that mention a reporter, an MD study of a DNA-binding cooperativity, and one
unrelated receptor paper. ⇒ **The field routinely relates the induced interface to output when the
output is degradation, and does not when it is transcription.** That is why the floor was
inheritable in one direction and unsized in the other, and it is what makes one deposited
transcriptional structure worth this much.

**(b) The one exception, found in an abstract.** *"A bivalent molecular glue linking lysine
acetyltransferases to oncogene-induced cell death"* (Nix et al., **Cell 2026**, PMID 42476129, DOI
`10.1016/j.cell.2026.06.037`; bioRxiv preprint `10.1101/2025.03.14.643404`) states, verbatim:

> *"The crystal structure of the chemically induced p300–BCL6 complex reveals how chance
> protein–protein interactions may be exploited to confer the potency and selectivity of KAT-TCIPs."*

That is `MISSING-3`'s object: a **structurally characterised** induced interface in a system whose
readout is transcriptional/epigenetic — and on **BCL6**, the same effector
[`nr4a3_effector_stage.py`](../modalities/nr4a3_effector_stage.py) already staged from 7LWG.

**(c) Finding the coordinates without the paper.** Neither the Cell article nor its preprint is open
access at Europe PMC (`isOpenAccess: N`, `inEPMC: N`), so the accession was sought from RCSB rather
than from the text. RCSB's search index, queried in CI:

- full-text `"KAT-TCIP"` → **HTTP 204, zero hits**
- full-text `"transcriptional chemical inducer of proximity"` → **HTTP 204, zero hits**
- full-text `"BCL6"` **AND** `"p300"` → **`total_count: 1`, identifier `9MZA`**

⚠ **Worth recording on its own:** the structure exists and is **invisible to the modality's own
name**. It is findable only by its two proteins.

**(d) The join was verified from the deposition, not assumed.** `9MZA`'s own
`rcsb_primary_citation` reads *"A Bivalent Molecular Glue Linking Lysine Acetyltransferases to
Oncogene-induced Cell Death."*, bioRxiv `10.1101/2025.03.14.643404`, PubMed `40166243`, authors
Nix · Gourisankar · Sarott · … · Crabtree; deposited 2025-01-22, released 2025-04-16, `struct.title`
*"Chemically Hijacked BCL6-TCIP3-p300 Complex"*. **The entry says which paper it belongs to.**

---

## 4 · The measurement

`nr4a3_induced_interface_census.py` applies `nr4a3_basin_search`'s **own** predicate to deposited
coordinates: per residue two query points (CA + side-chain centroid, exactly as
`load_arm_from_registry` builds them), classified by distance to the nearest heavy atom of the other
chain — `< 3.0 Å` hard, `< 3.6 Å` soft, `≤ 6.0 Å` **contact** — and `n_contact` is what
`min_contact_residues = 12` is compared against.

⚠ **`min_contact_residues` counts POINTS, not residues, despite its name.** There are two points per
residue, so **12 points is as few as 6 residues**. Every row below reports both.

**22 entries fetched, 22 parsed, every title and chain description verified from the file itself.**
Only pairs that are actually *induced* enter the summary: ligand-bridged pairs are read off the
coordinates; the ligand-dependent-but-not-ligand-bridged ones (an agonist inside a nuclear receptor's
pocket recruiting a coactivator NR box) are curated by name with a reason and labelled
`allosteric_curated`, so a reader can drop them and recompute.

| class | entries | induced pairs | contact points, smaller direction | fails the floor of 12 in ≥1 direction | in BOTH |
|---|---|---|---|---|---|
| **`tcip`** — 9MZA, BCL6·TCIP3·p300 | 1 | 2 | **6 – 6** | **2 of 2** | **2 of 2** |
| `induced_transcriptional` — incl. 9MZA and 5 nuclear-receptor/coactivator entries | 6 | 12 | 6 – 19 | 2 of 12 | 2 of 12 |
| `degrader_or_glue` — 8 PROTAC / molecular-glue ternaries | 8 | 15 | 5 – 23 | 6 of 15 | 1 of 15 |
| `cid_proximity` — rapamycin, auxin, ABA, gibberellin | 7 | 7 | 11 – 53 | 1 of 7 | 0 of 7 |
| `constitutive` — 7LWG BCL6 BTB homodimer (contrast, never pooled) | 1 | 1 | 64 | 0 | 0 |

### 4.1 · The row that decides the blocker

`9MZA` holds two crystallographically independent copies of the induced complex (chains A·D and
B·C). Both read **6 and 7 contact points, 4 residues on each side.** The bridging ligand `A1BUC`
(TCIP3) is **81 heavy atoms** and touches 33–42 atoms' worth of each partner — the molecule is
large and the protein–protein interface it creates is tiny. That is precisely what the paper's own
phrase *"chance protein–protein interactions"* describes.

⚠ **Not a truncation artefact, checked rather than assumed.** Both partners are substantially
resolved — the BCL6 chains contribute 244 and 246 query points (122–123 residues) and the p300
chains 224 and 226 (112–113 residues) — so the small count is a property of the interface, not of a
short chain. The same file's constitutive dimer, measured with the same points, reads an order of
magnitude higher (§4.2).

### 4.2 · The cross-check that says the instrument is not the story

`A1BUC` also spans the **two BCL6 protomers**, because the BTB lateral groove is formed *between*
them — the same fact `nr4a3_effector_stage` measured when it staged 7LWG as an `A+B` body. That pair
is constitutive, is excluded by name from the induced class, and serves as a control:

- the BCL6 BTB homodimer in **9MZA**: **66 / 71** contact points
- the same homodimer in the independent entry **7LWG**: **64 / 67** contact points

Two crystals, two depositions, one instrument, one number. **A method that reads 6–7 on the induced
interface and 64–71 on the obligate dimer in the same file is discriminating, not saturating.**

### 4.3 · The calibration nobody had done: the floor does not fit its own modality either

The floor came from degraders. Measured against real degrader ternaries, `12` rejects **6 of 15**
ligand-bridged pairs in at least one direction — including MZ1·BRD4-BD2·pVHL (5T35) at 10–11 and the
SMARCA2 PROTAC (6HAX) at 11. **The threshold is not a conservative floor for the modality it was
taken from; it sits inside that modality's own distribution.**

---

## 5 · Task 3 — the disposition, stated plainly

> ### ✅ `BLK-TCIP-INTERFACE-FLOOR` — **RETIRE**, not escalate.
>
> **The floor is BOUNDED by real data.**
> **Number:** an induced transcriptional-proximity interface of **6–7 contact points / 4 residues per
> side** is sufficient for a chemically induced p300·BCL6 complex to form as a crystallisable
> species.
> **Source:** PDB **9MZA**, X-ray 2.1 Å, released 2025-04-16, primary citation Nix et al.,
> `10.1101/2025.03.14.643404` → Cell `10.1016/j.cell.2026.06.037` (PMID 42476129).
> **Uncertainty, stated at its true weight:** **n = 1 system**, one crystal form, two
> crystallographically independent copies agreeing at 6/7. It bounds the floor from **above** — it
> shows 12 is *more* than a working transcriptional CIP's interface — and it does **not** establish a
> lower limit, a monotone relationship, or a threshold below which such a system stops working.
> **What it does NOT license:** nothing here says this molecule works, is selective, is safe, or is
> a therapeutic candidate; the census measures geometry in a deposited file and nothing else.

**Why this is a retirement and not a partial answer.** The blocker asked for a *characterised induced
interface in a chemically-induced transcriptional-proximity system, related to transcriptional
output*. All three now exist and are cited: the interface is characterised (2.1 Å coordinates, and
measured here), the system is transcriptional (KAT-TCIPs redirect p300/CBP to activate BCL6-repressed
genes), and the relationship is asserted by the authors of the structure — the interface is what they
say confers the behaviour they measure.

⚠ **The half that remains open is narrower, and it is not this blocker.** What does *not* exist is a
**series**: two or more induced interfaces of different size in one transcriptional system with
matched output, which is what would turn a bound into a calibration curve. That is a wet-lab or
medicinal-chemistry series and belongs to `BLK-NO-WET-LAB`, which the route already carries. Leaving
`BLK-TCIP-INTERFACE-FLOOR` open for it would make a blocker that has been answered look unanswered.

---

## 6 · Task 4 — what this does to the 0.896 → 1.121 → 1.254 ablation

The finding this blocker sat on is
[`nr4a3-tcip-route-memo.md` §4(b)](../modalities/nr4a3-tcip-route-memo.md), which owns the numbers
and is not restated here: the single-domain / multi-subunit acceptance ratio at the 12-atom linker
rung is **0.896 at `min_contact_residues = 12`**, **1.121 at 6**, **1.254 at 0**, and the sign
inverts across the floor.

**What changes.** The measured transcriptional-CIP interface — 6 to 7 contact points — lands **at the
`min_contact_residues = 6` ablation rung**, not at the committed 12. The rung that was included as a
sensitivity sweep turns out to be the one that describes the regime this route is actually in.

**What does NOT change, and must not be quietly promoted.**

1. ⛔ **`REQ-TCIP-2` stays the operative requirement.** Every geometric statement the route publishes
   is still reported at **both** floors and still asserts only what holds at both. Sizing the floor
   is not permission to drop the bracket: the bracket exists because the ratio is floor-dependent,
   and it still is. Retiring the requirement is a decision for
   [`selectivity-requirement-sizing.md`](./selectivity-requirement-sizing.md) and the roadmap, routed
   in [§7](#7--graph-edits--described-and-routed-not-applied) and **not taken here.**
2. ⛔ **The pooled ratio still may not be read as a size law, at any floor.** §4(a) of the route memo
   measured within-class spread exceeding the between-class contrast at all 8 rungs, and a seed
   defect that moved the ratio by ~0.13. Both are unaffected by anything in this file.
3. ⛔ **One structure does not license reading 1.121 as "the" TCIP answer.** The honest statement is
   that **the direction of the size penalty is floor-dependent, and the only measured transcriptional
   induced interface sits at the floor where the penalty is absent** — which is a statement about the
   instrument's inherited parameter, not a result about effector size.

**The publishable sentence this adds**, for whichever endpoint carries it: *the apparent
single-domain penalty in a bivalent-reach enumeration is an artefact of a contact floor inherited
from degraders, and the one chemically-induced transcriptional-proximity complex with deposited
coordinates has an interface about half that floor.*

---

## 7 · Graph edits — DESCRIBED AND ROUTED, NOT APPLIED

`systems/graph/*`, `nr4a3-program-map.md` and `path-family-synthesis.md` are not hand-edited by this
lane. The edits this file implies are in
[`tcip-interface-floor-map-edits.json`](./tcip-interface-floor-map-edits.json), to be applied by
whoever owns the graph.

---

## 8 · Limits

- **The SI was never read.** §2 is a record of refusals plus a reading of two copies of the main text.
- **`n = 1`** for the class that decides the blocker.
- **Deposited-pose bias.** A crystal structure is one favourable pose; the sampler counts contacts
  over *sampled* placements. The census measures the predicate on both, which is the comparison that
  was wanted, but the two are not the same statistic.
- **Peptide-length ceiling.** The nuclear-receptor coactivator rows are short NR-box peptides, so
  their contact count is capped by how many residues exist. They are reported, not leaned on.
- **`allosteric_curated` rows are a claim about the literature**, not a reading of the file, and are
  labelled so they can be dropped.
- **Crystal contacts are not filtered.** A pair is called induced only when a bridging ligand spans
  it or when it is curated, which excludes most lattice artefacts, but no lattice analysis was done.
- **Nothing here is a statement about efficacy, selectivity, safety, a therapeutic window, or
  clinical readiness**, for any molecule named — including TCIP3, EB-TCIP, MZ1, dBET6, lenalidomide,
  pomalidomide, rosiglitazone and rapamycin.

## Sources

- [`nr4a3-induced-interface-census.json`](../modalities/nr4a3-induced-interface-census.json) — every
  number above.
- `literature-cache` branch: `literature/tcip-interface-floor-2026-08-07/`,
  `literature/induced-proximity-transcription-2026-08-07/`,
  `literature/tcip-kat-structure-2026-08-07/`, `literature/tcip-9mza-2026-08-07/`.
- PDB **9MZA** (2.1 Å); PDB **7LWG** (1.30 Å, the staged BCL6 arm).
- Nix et al., *A bivalent molecular glue linking lysine acetyltransferases to oncogene-induced cell
  death*, Cell 2026, PMID 42476129 / bioRxiv `10.1101/2025.03.14.643404` — **abstract and deposition
  citation only; the full text is not open access and was not read.**
- `EV-EB-TCIP-2025`, `10.1021/jacs.5c05634`, PMC12851799 — **citation gate still OPEN**
  ([`nr4a3-tcip-route-memo.md` §6](../modalities/nr4a3-tcip-route-memo.md) owns that finding). No
  number in this file comes from it; §2 uses only the *absence* of terms in a committed text file.
