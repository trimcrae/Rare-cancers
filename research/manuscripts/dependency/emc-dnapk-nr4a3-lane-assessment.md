---
id: DOC-EMC-DNAPK-LANE
title: DNA-PK as an indirect NR4A3 destabiliser — primary-source verification of lane 3.9
level: L3
kind: memo
status: live
canonical_for: ["the DNA-PK / NR4A3 lane's primary evidence and its 2026-08-07 grade"]
purpose: >
  Verify at primary-record level the claim that DNA-PK acts on NR4A3, state exactly what was
  measured and in what system, decide honestly whether it transfers to EWSR1::NR4A3, and grade the
  clinical-stage DNA-PK inhibitor class as a class without asserting anything about EMC.
scope: >
  L3. Covers lane 3.9 of emc-unexplored-treatment-lanes.md only. It does not re-grade the ATR
  routes, does not touch the degrader program, and asserts nothing about efficacy, safety or a
  therapeutic window in any disease. Graph changes are proposed in a routed map-edits JSON, not
  applied here.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-07
last_verified: 2026-08-07
---

# DNA-PK as an indirect NR4A3 destabiliser — primary-source verification of lane 3.9

> ⛔ **NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS, FOR EMC OR
> FOR ANY OTHER DISEASE.** Every measurement below was taken in vascular smooth muscle or in
> DNA-repair cell biology. No experiment described here was performed on a sarcoma, on an NR4A3
> fusion protein, or on any EMC material.

**One-line result.** The mechanism is real, independently replicated and stronger than the source
memo recorded — and it is **pan-NR4A with demonstrated paralogue redundancy**, measured only on
**wild-type NOR1 in vascular smooth muscle**, and the two most advanced DNA-PK inhibitors both have
published reports of terminated or toxicity-limited clinical development. The lane survives as a
registrable route and does **not** survive at rank 9.

---

## 1 · What the primary source actually says

**Medunjanin S, Daniel JM, Weinert S, Dutzmann J, Burgbacher F, Brecht S, Bruemmer D, Kähne T,
Naumann M, Sedding DG, Zuschratter W, Braun-Dullaeus RC. "DNA-dependent protein kinase (DNA-PK)
permits vascular smooth muscle cell proliferation through phosphorylation of the orphan nuclear
receptor NOR1." *Cardiovascular Research* 2015. PMID 25852083, DOI 10.1093/cvr/cvv126.**

⚠ **Verification level: [API] — Europe PMC structured record + abstract, retrieved 2026-08-07.**
The record carries `isOpenAccess: false` and **no PMCID**, so Europe PMC serves no full-text XML for
it and the Methods are not reachable at $0. Everything quoted below is from the abstract.

| the memo's question | what the paper reports, verbatim where it matters |
|---|---|
| **which cells** | *"Cultured human aortic SMC"* — primary human aortic smooth muscle cells. Plus *"human atherosclerotic tissue specimens"* and a **mouse** wire-injury model. **No sarcoma. No EMC. No cancer cell of any kind.** |
| **fusion or wild type** | **Wild type.** Endogenous NOR1/NR4A3 in vascular smooth muscle. The word "fusion" does not appear; EWSR1 does not appear. |
| **protein level or activity** | **Protein level.** *"FCS-stimulated up-regulation of NOR1 protein … [was] prevented by DNA-PK inhibition"*, alongside PCNA, cyclin D1 and Rb hyperphosphorylation. |
| **the mechanism claimed** | *"Mutational analysis and kinase assays demonstrated that NOR1 is a substrate of DNA-PK and is phosphorylated **in the N-terminal domain**. Phosphorylation resulted in post-transcriptional stabilization of the protein through **prevention of its ubiquitination**."* |
| **the perturbation** | *"the specific DNA-PK inhibitor NU7026 (or siRNA), which resulted in a 70% inhibition of FCS-induced proliferation as measured by BrdU incorporation"* |
| **the interaction** | *"Co-immunoprecipitation studies from VSM cell lysates demonstrated that DNA-PK forms a complex with NOR1."* |

⛔ **THE RESIDUE IS NOT PINNED AND CANNOT BE PINNED AT $0.** The abstract says only *"in the
N-terminal domain"*. The specific serine or threonine is in the paywalled body. Any manuscript
sentence naming a residue would be fabricating it. This is the lane's first hard blocker and it is a
paywall, not a capability.

### 1a · An independent replication the memo did not have

**Liu YY, Zhang WY, Zhang ML, Wang YJ, Ma XY, Jiang JH, Wang R, Zeng DX. "DNA-PKcs participated in
hypoxic pulmonary hypertension." *Respiratory Research* 2022. PMID 36114572, PMC9479248,
DOI 10.1186/s12931-022-02171-x.** [API]

A second, unrelated group, in **human pulmonary artery smooth muscle cells**, using both siRNA and
the same tool compound NU7026: *"DNA-PKcs affected proliferation by regulating NOR1 protein
synthesis followed by the expression of cyclin D1. Co-immunoprecipitation of NOR1 with DNA-PKcs was
severely increased in hypoxia."*

⭐ Two independent groups, two smooth-muscle systems, the same directional result: **DNA-PK activity
supports NOR1 protein levels, and DNA-PK inhibition lowers them.** That is a materially stronger
evidence base than a single 2015 paper.
⚠ **But they do not agree on the mechanism.** 2015 says post-transcriptional stabilisation by
prevention of ubiquitination; 2022 says regulation of *protein synthesis*. Those are different
claims about where in the lifecycle the effect lands, and the difference matters here — a
degradation-brake mechanism is what makes this lane interesting, and a synthesis mechanism is not.
Neither paper adjudicates the other.

---

## 2 · The paper the memo missed, and it is the one that decides the lane

**Malewicz M, Kadkhodaei B, Kee N, Volakakis N, Hellman U, Viktorsson K, Leung CY, Chen B,
Lewensohn R, van Gent DC, Chen DJ, Perlmann T. "Essential role for DNA-PK-mediated phosphorylation
of NR4A nuclear orphan receptors in DNA double-strand break repair." *Genes & Development* 2011.
PMID 21979916, PMC3197202, DOI 10.1101/gad.16872411 — 70 citations.** [API]

This is four years **earlier** than the paper UniProt cites and carries **70 citations against that
paper's 24**, and its subject is the **family**, not NR4A3: *"NR4A proteins interact with the
DNA-PK catalytic subunit … At DNA repair foci, NR4A is phosphorylated by DNA-PK and promotes DSB
repair. Notably, NR4A transcriptional activity is entirely dispensable in this function … Thus,
NR4As represent an entirely novel component of DNA damage response and are substrates of DNA-PK in
the process of DSB repair."*

**Munnur D, Somers J, Skalka G, Weston R, Jukes-Jones R, Bhogadia M, Dominguez C, Cain K, Ahel I,
Malewicz M. "NR4A Nuclear Receptors Target Poly-ADP-Ribosylated DNA-PKcs Protein to Promote DNA
Repair." *Cell Reports* 2019. PMID 30784586, PMC6381605, DOI 10.1016/j.celrep.2019.01.083.**
[FT — open-access full text read]

Two sentences from that full text settle the selectivity question before any modelling is done:

- *"PAR-binding ability extends to **all NR4A family members**, including the Drosophila NR4A homolog
  DHR38."*
- *"We conclude that **NR4A1 and NR4A2 are redundant** in facilitating DNA repair via c-NHEJ and
  control the levels of phDNA-PKcs on chromatin."*

⛔ **THIS IS WORSE FOR THE LANE THAN "NOT SELECTIVE".** The memo already recorded that DNA-PK
inhibition *"would lower wild-type NR4A3 too, and whether NR4A1/NR4A2 are similarly regulated is
untested."* It is not untested. It is tested, and the answer is that the axis is a **family axis**,
conserved to *Drosophila*, in which the paralogues are **functionally redundant** for the repair
output. So the axis delivers:

1. **no NR4A3 selectivity** — the interaction is a property of the NR4A DNA-binding domain, which all
   three paralogues share;
2. **no fusion selectivity** — the site is in NR4A3 sequence the fusion shares with wild type;
3. **and a buffered phenotype** — with NR4A1/NR4A2 redundant, removing NR4A3's contribution to
   repair is compensable, so even the repair readout is not a clean NR4A3 assay.

The 2019 paper's own therapeutic framing is *"pharmacological targeting of NR4A in cancer therapy"* —
targeting the receptor's PAR-binding pocket, which is a **different route** (it needs a binder, so it
re-imports `BLK-R4-BINDS`) and is not what lane 3.9 proposes.

Related and consistent: **Jagirdar K et al., *PLoS One* 2013, PMID 24223135, PMC3819332,
DOI 10.1371/journal.pone.0078075** — NR4A2 is recruited to UV-induced nuclear foci and participates
in nucleotide excision repair. Again a paralogue, again the family.

---

## 3 · Does it transfer to EWSR1::NR4A3?

Three separate questions, and they have three different answers.

### 3a · Is the domain retained in the fusion? ✅ Yes — and this is checkable from repo evidence

From the repository's own object registry ([`systems/graph/objects.json`](../../../systems/graph/objects.json)):

- `OBJ-NR4A3-WT` records *"ENST00000395097 — 8 transcript exons, 6 coding; exons 1 and 2 are
  NON-CODING"*, protein length 626 aa.
- `OBJ-FUS-T1` (the commonest reported type) is defined at residue level as
  *"EWSR1(1–431) :: 1 junction residue :: NR4A3(1–626)"*.

So the commonest fusion carries the **entire NR4A3 coding region**, N-terminal domain included. The
region the 2015 paper localises the phosphorylation to is **not deleted**. This is the same
observation the source memo already made for the SUMO sites, and it holds here for the same reason.

⭐ **And it is not a property of one breakpoint.** Every fusion object in the registry whose residue
boundaries are pinned carries `NR4A3(1–626)` whole:

| object | definition | NR4A3 retained |
|---|---|---|
| `OBJ-FUS-T1` | `EWSR1(1–431) :: 1 junction residue :: NR4A3(1–626)` | whole |
| `OBJ-FUS-T2` | `EWSR1(1–264) :: [59 UTR-encoded residues] :: NR4A3(1–626)` | whole |
| `OBJ-FUS-T5` | `EWSR1(1–472) :: 1 junction residue :: NR4A3(1–626)` | whole |
| `OBJ-FUS-TAF15` | `TAF15(1–161) :: 1 junction residue :: NR4A3(1–626)` | whole |
| `OBJ-FUS-FUSNR4A3` | ⛔ registry records the breakpoint as **unpinned** | not determinable here |
| `OBJ-FUS-TCF12` | ⛔ registry records genomic resolution only, and isoform disagreement | not determinable here |

⚠ So the honest statement is **four of four pinned reported types retain it; two remain unpinned in
this repository's own registry** — not "all reported breakpoints", which is a stronger sentence than
the evidence supports.

⚠ **Retention of a domain is not retention of a regulation.** The fusion places a 431-residue EWSR1
low-complexity region *upstream* of that N-terminal domain, and EWSR1 fusion proteins are known to
behave as condensate-forming, differently-regulated species. Whether a DNA-PK site sitting downstream
of an EWSR1 LC domain is still accessible, still phosphorylated, and still coupled to the same E3 is
**unmeasured in any system**.

### 3b · Is the *degradation brake* the same? ❌ Unknown, and it is the load-bearing unknown

The lane's entire proposition is: *phosphorylation blocks ubiquitination → inhibit the kinase →
lose the block → the protein is degraded.* Every step of that chain was measured on **wild-type NOR1
in a non-transformed vascular cell**. For EWSR1::NR4A3 the repository holds no reading of:

- whether the fusion is ubiquitinated at all;
- which E3 does it;
- whether the fusion's steady-state level is set by degradation rather than by the partner's
  promoter — and note that EMC's defining lesion places NR4A3 under the 5′ partner's promoter, so
  the **transcriptional** input to fusion abundance is the one thing about this system that IS
  established.

### 3c · Has anyone ever connected the two? ❌ No — measured, not assumed

Europe PMC forward-citation retrieval, 2026-08-07, via `CITES:25852083_MED OR CITES:21979916_MED`
(the two foundational papers together): **73 records**. Screened by title: **no EMC record, no NR4A3-fusion
sarcoma record, no chondrosarcoma record.** A separate sweep,
`(NR4A3 OR "NOR-1" OR NOR1 OR "neuron-derived orphan receptor") AND (PRKDC OR "DNA-PK" OR
"DNA-dependent protein kinase" OR Ku70 OR Ku80 OR XRCC5 OR XRCC6)`, returned **140 records** with the
same result.

⭐ So the memo's framing is correct on this point and it is now evidenced rather than asserted:
**the NR4A × DNA-PK axis has never been examined in EMC.** That is a real gap. It is also a gap
nobody can close from a keyboard.

---

## 4 · The DNA-PK inhibitor class, graded as a class

⛔ **No statement in this section is about EMC.** These are published trial reports in other
diseases, recorded because the memo's case rested on the words "DNA-PK inhibitors are clinical-stage"
and that phrase, while true, hides the class's actual trajectory.

| agent | most advanced public report retrieved | what it says |
|---|---|---|
| **AZD7648** (AstraZeneca) | Yap TA, LoRusso P, Miller RE, Kristeleit R, *et al.*, *British Journal of Cancer* 2025. **PMID 40382524, PMC12304285**, DOI 10.1038/s41416-025-03053-x. First-in-human Phase I/IIa, **NCT03907969**, n = 30 | *"No responses to AZD7648 monotherapy were observed."* … *"Toxicity of AZD7648 + PLD was greater than expected and antitumour activity was limited, **leading to early study termination**."* |
| **Peposertib / nedisertib (M3814)** | Zambare W, *et al.*, *Clinical and Translational Radiation Oncology* 2026. **PMID 41693813, PMC12906130**, DOI 10.1016/j.ctro.2026.101109. Post-hoc analysis of a phase Ib rectal chemoradiation trial, n = 6 | *"Combining peposertib with capecitabine-based chemoradiation was associated with **disproportionately high risks of severe late rectal toxicities**, particularly in patients entering WW."* |
| **Peposertib**, development status | Lange M, Kühn C, Nair A, Fuchß T, Saal C, *Eur J Pharm Sci* 2025. **PMID 40545054**, DOI 10.1016/j.ejps.2025.107174 | *"currently being evaluated in clinical trials in patients with advanced solid tumours"* — the compound is live; the paper is about solid-form work done to enable first-in-human dosing at all. |

**In-repo cross-check.** [`nr4a3-repurpose-candidates.json`](../../modalities/nr4a3-repurpose-candidates.json)
(Broad Drug Repurposing Hub extract) already carries this class: `peposertib` at
`phase: "Phase 1/Phase 2"`, and **`NU-7026` — the exact tool compound used in both smooth-muscle
papers above — at `phase: "Preclinical"`**, alongside `NU-7441`, `KU-55933`, `compound-401`,
`LY294002`, `PIK-75`, `PI-103`, `PP-121` and `wortmannin`. So the repository already held the
chemical matter for this lane and had never connected it to NR4A3.

**Honest reading.** "Clinical-stage" is accurate. It is also true that the class's furthest-advanced
monotherapy programme was **terminated early for limited activity and greater-than-expected
toxicity**, and that the furthest-advanced combination programme reported **severe late toxicity** in
the radiosensitisation setting the class was designed for. Neither fact says anything about EMC.
Both bear directly on whether a route that depends on systemic DNA-PK inhibition is a plausible
therapeutic proposition, and the memo could not weigh them because it did not have them.

---

## 5 · What the repository can and cannot read here

| question | can this repo answer it at $0? |
|---|---|
| Is the phosphorylated domain retained across reported breakpoints? | ✅ **In all four pinned types**, read off [`systems/graph/objects.json`](../../../systems/graph/objects.json) in §3a. ⚠ Two objects (`OBJ-FUS-FUSNR4A3`, `OBJ-FUS-TCF12`) are recorded there as **unpinned**, so this is four of four pinned, not six of six reported. |
| Which residue is phosphorylated? | ❌ **No.** Paywalled. Both papers are outside Europe PMC's open-access full-text set. |
| Is that residue conserved across NR4A1/2/3? | ❌ Blocked on the line above, and the 2019 full text makes the answer near-certain in the unhelpful direction. |
| Is *PRKDC* a dependency in sarcoma lines? | ❌ **No reading exists, and the absence is the collector's, not DepMap's.** [`fet-ddr-axis-scan.json`](../../modalities/fet-ddr-axis-scan.json) lists `PRKDC` under `genes_requested_but_absent` and reports `other_druggable_ddr_nodes.PRKDC` as `{FET_mean: null, non_FET_sarcoma_mean: null}` — measured on its own run, alongside `POLR2A`. ⚠ **`POLR2A` is a canonical pan-essential and its absence from the same column set is a reason to treat this as an instrument reading needing confirmation, not as a fact about *PRKDC*.** An absent reading is not a reading of absence. |
| Is *PRKDC* elevated in EMC tumours? | ✅ **YES, ANSWERABLE — and it was answerable all along. See §5a.** |
| Does DNA-PK inhibition lower EWSR1::NR4A3 protein? | ❌ **No.** This is a western blot in a cell that has the fusion. It needs a bench, and it is the only experiment that would settle the lane. |

### 5a · *PRKDC* in real EMC tumours — measured here, from data the repository already had

⭐ **This was written down as "no reading exists" and that was wrong.**
[`emc-atr-vulnerability-inputs.json`](../../modalities/emc-atr-vulnerability-inputs.json) →
`/part_b/platforms/<platform>/geneset_gene_values` holds **per-sample values for a 1,299-gene panel**
across every EMC-bearing GEO series this repository has characterised, with the sample titles beside
them — and **`PRKDC` is in that panel.** The answer was on disk. One home for the numbers:
[`emc-kinase-lane-panel-read.json`](../../modalities/emc-kinase-lane-panel-read.json), produced by
[`emc_kinase_lane_panel_read.py`](../../modalities/emc_kinase_lane_panel_read.py). **$0, no network, no
dispatch.**

| series · platform | n EMC / comparators | value kind | *PRKDC* Δ (EMC − comparators) | percentile of that Δ among the **same panel genes' own Δs on the same samples** |
|---|---|---|---|---|
| `GSE24369` · `GPL6244` | 6 / 36 | single-channel intensity | **−0.129** (9.436 vs 9.566) | **21.7** (of 1,299 genes ranked) |
| `GSE4303` · `GPL3290` | 10 / 6 | two-colour log-ratio (**relative**) | **+0.549** (−1.388 vs −1.937) | **71.0** (of 1,206 genes ranked) |

⚠ **The two rows may not be pooled and no combined number is offered**: one is a single-channel
intensity and the other a ratio against a reference pool. The percentile column is what makes them
comparable at all, because it is each platform's own contrast distribution, not a shared scale.

Panel background of the Δ distribution: mean +0.084, SD 0.479 on `GSE24369`; mean +0.113, SD 0.969
on `GSE4303`. Both *PRKDC* Δs sit inside about half an SD of their panel's own mean.

⛔ **Reading: the two independent series DISAGREE ON THE SIGN, and both magnitudes are inside the
panel's own background spread. There is no EMC-specific *PRKDC* elevation in either readable
series.** This is the first time *PRKDC* has been read in EMC tumour material in this repository.

⚠ **What this does and does not bear on.** It does **not** test the mechanism — the 2015 claim is
post-translational, and a transcript level says nothing about whether DNA-PK is phosphorylating
NOR1. What it removes is the one thing a reader would otherwise reach for: there is no *PRKDC*
overexpression in EMC that could supply a tumour-versus-normal index for a systemic DNA-PK
inhibitor. Combined with §2's paralogue redundancy, the route has no selectivity argument available
to it from any layer that has been measured.

⚠ **And a same-artifact orientation reading, recorded because it is free and because a reader will
ask:** `ATR` sits at the **47.8th** percentile on `GSE24369` and the **28.5th** on `GSE4303` — i.e.
at or below its panel's median on both. That is a reading about *ATR transcript abundance* only; the
ATR route's argument is about replication-stress phenotype, not about *ATR* mRNA, and this neither
supports nor undercuts it. It is placed here so the number is not later discovered and mistaken for
one.

---

## 6 · Verdict

**SURVIVES AS A ROUTE. DOES NOT SURVIVE AT RANK 9.**

What the memo got right, and what the primary records say about it:

- there **is** curated experimental evidence that DNA-PK acts on NR4A3 protein, and it is
  **stronger** than the memo recorded — two independent groups, two systems, plus a well-cited
  family-level mechanism paper the memo did not cite;
- the route genuinely **needs no NR4A3 binder** (`BLK-R4-BINDS`) and **no induced ternary geometry**
  (`BLK-INDUCED-COMPLEX`). Both really are retired by not being needed;
- the domain carrying the site really is **retained** in the commonest fusion.

What changes the grade:

1. **The axis is pan-NR4A and paralogue-redundant**, stated by the primary literature rather than
   left open. Selectivity is not "untested" — it is measured, at the family level, in the wrong
   direction for this program.
2. **It is a vascular-smooth-muscle mechanism**, replicated only within vascular smooth muscle. No
   transformed cell, no sarcoma, no fusion protein.
3. **The two mechanism claims disagree** (stabilisation-by-blocked-ubiquitination vs protein
   synthesis), and only the first supports the lane's logic.
4. **The clinical class carries two published negative-to-troubling development reports.**
5. **The one free question is paywalled** (the residue), and the one decisive question needs a bench.
6. **⭐ *PRKDC* is not elevated in EMC tumours** — measured here for the first time, on both readable
   series, which disagree on the sign and are both inside their panel's own noise (§5a). So no layer
   that has been measured — paralogue, fusion-vs-wild-type, or tumour-vs-comparator abundance —
   offers this route a selectivity argument.

**Its remaining value is real but narrow, and it is a sentence in someone else's paper rather than a
paper of its own:** the observation that EMC's driver is a substrate of a clinically-drugged kinase,
that the modified region survives the translocation, and that nobody in twenty-five years of NR4A
DNA-repair biology or thirty years of EMC biology has looked. That belongs in the DDR assessment
this repository already owns
([`emc-atr-vulnerability-assessment.md`](emc-atr-vulnerability-assessment.md)), as a contributing
observation with its limits stated inside it, exactly as that document handles class inheritance.

**Proposed registration** (routed, not applied):
[`kinase-lanes-map-edits.json`](kinase-lanes-map-edits.json) → `RT-DNAPK-NR4A3`.

---

## 7 · Limits of this memo

- **Two of the four primary papers were read at abstract level only** (PMID 25852083, PMID 21979916).
  Both are outside Europe PMC's open-access full-text set. Every quotation above is from the
  structured Europe PMC record, and the memo says so at each point rather than in a footnote.
- **The forward-citation screen was by title.** A citing paper could discuss EMC in its body without
  saying so in its title. The claim "nobody has connected the two" is therefore a claim about
  73 titles, which is what it says it is.
- **Nothing here was computed.** No structure was built, no residue was mapped, no alignment was run.
  Every retention statement is read off the repository's existing object definitions.
- **`SEQUENCE-LEVEL WORK IS DELIBERATELY NOT DONE HERE.`** Mapping a site that has not been
  identified would be mapping a guess.
