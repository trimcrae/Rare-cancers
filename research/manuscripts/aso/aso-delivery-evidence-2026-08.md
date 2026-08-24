---
id: DOC-ASO-DELIVERY-EVIDENCE-2026-08
title: "Did the delivery gate move? — the August-2026 ASO/siRNA press items traced to their primary sources"
level: L3
kind: memo
status: live
canonical_for:
  - the evidence grade of the 2026-08 press-level ASO/siRNA items held in research/method-watch-backfill-2026-08.md
  - whether the 2026-08-11 antisense-delivery report moves BLK-DELIVERY
purpose: >
  research/method-watch-backfill-2026-08.md carries three ASO/siRNA items as bare `[PRESS]` headlines
  under a section whose own title says "the gate is delivery", and marks the first of them "worth
  reading the primary source". This memo does that reading, grades each item traced-to-primary-source
  or press-only, and states what it does and does not do to the ASO route's dominant blocker.
scope: >
  Retrieval and grading only. Nothing here re-grades a route, unparks anything, or edits
  research/method-watch.md — the proposed trigger-table change is written out below for whoever owns
  that file to apply. Nothing here asserts or implies efficacy, safety, a therapeutic window,
  selectivity or clinical readiness for any agent named, in EMC or in any other disease.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
---

# Did the delivery gate move?

## 0 · The answer, in one line

**No.** The primary paper behind the 2026-08-11 headlines is **cell-level uptake-and-escape mechanism**;
it names no delivery vehicle, no EMC-enriched targeting antigen, and no demonstrated biodistribution to
a non-hepatic solid tumour — which is precisely and only what
[`BLK-DELIVERY`](../../../systems/graph/blockers.json) requires as it was rescoped on 2026-08-12.
**`BLK-DELIVERY` stands. `RT-ASO` stays parked.**

The honest partial credit is worth stating in the same breath, because it is not nothing: the delivery
problem has three barriers stacked — *get to the tumour*, *get into the cell*, *get out of the
endosome* — the blocker is written around the **first**, and this paper is the first mechanistic handle
this repository holds on the **third**. That is upstream biology on a barrier every route shares. It is
not the gate.

Every identifier below is anchored in
[`aso-delivery-evidence-2026-08.json`](./aso-delivery-evidence-2026-08.json), which records the runner
job that returned it. Nothing here was typed from recollection.

---

## 1 · Item 1 — the antisense-delivery paper · **traced to primary source**

**Verified citation.** Marco S, Walsh PJ, Revenko AS, Schmidt T, Thomason PA, McGarry L, MacLeod AR,
Ansel S, Tataran D, Bushell M, Braconi C, Norman JC. *EPHA2/CD44-directed trafficking enhances endosomal
leakiness and antisense therapy delivery.* **J Cell Biol** 2026;225(9):e202507217.
**PMID 42578958**, **doi:10.1083/jcb.202507217**. Europe PMC reports it **not** open access.
An earlier version exists as a bioRxiv preprint, **doi:10.1101/2025.02.05.635637** (Europe PMC
`PPR974551`, open access).

**What was actually found**, from the returned abstract — quoted in full in the JSON, paraphrased here:
direct ASO engagement with the **scavenger receptor CD44** activates the **ERK–RSK** axis, which
serine-phosphorylates the receptor tyrosine kinase **EPHA2**; that phosphorylation permits endocytosis
and accumulation of ASOs in **nuclear-captured endosomes**, which then undergo **lipid peroxidation**,
become leaky, and let the ASO out to suppress its target mRNA. Blocking **stress-granule-mediated repair**
of those leaky endosomes increases the effect further. The authors' own framing is *"an endocytic route
to the nucleus which may be exploited"* — a mechanism offered as exploitable, not a delivery technology
demonstrated.

⚠ Two of the twelve authors (Revenko, MacLeod) publish from an antisense-therapeutics company; the
ASO chemistry studied is a cET gapmer against KRAS. Recorded because it tells you what the reagent was,
not as a comment on the work.

### What system — and this is the question the grade turns on

| Question | Answer | Basis |
|---|---|---|
| Cell lines? | **Yes** — the work is described throughout in cellular terms (endocytosis, endosomes, receptor phosphorylation). Press accounts name pancreatic cancer cells. | abstract + press |
| Mouse / any in vivo experiment? | **UNKNOWN** | see below |
| Human tissue? | **UNKNOWN** | see below |
| Tumour biodistribution / delivery to a tumour in an animal? | **NOT CLAIMED ANYWHERE WE COULD READ** — neither abstract mentions an animal, a tumour, a route of administration, or biodistribution | abstract of both versions |

⛔ **The UNKNOWNs are real UNKNOWNs, not a polite way of saying "cell-only".** The body of this paper
is **not retrievable at $0 today**, and that is a measured result rather than an assumption — four
distinct routes were tried from a GitHub runner with unrestricted egress and each was refused, with the
refusal read from the job log rather than guessed:

| Route tried | Result |
|---|---|
| Europe PMC record for the journal version | `isOpenAccess: false` — paywalled |
| bioRxiv preprint PDF (runs `32726803048`, `32727869107`) | **HTTP 429**, after paced retries, twice |
| Europe PMC preprint `fullTextXML` for `PPR974551` | **HTTP 404** |
| Europe PMC OA-repository PDF for `PPR974551` (the URL Europe PMC's own `fullTextUrlList` advertises as *Open access*) | **HTTP 403** |
| Publisher article page and DOI landing page at `rupress.org` | **HTTP 403** |

So the body of the paper has not been read here. What *is* established is narrower and sufficient for the
grading: **neither abstract makes a tumour-delivery claim**, and an in-vivo result that a paper does not
put in its abstract is not one this repository may lean on.

### Does it bear on delivery to a SOLID TUMOUR specifically?

**No — and the distinction matters more here than usual, so say it plainly.** This is not a hepatocyte
result either; it is a *third* thing, and conflating it with either would be wrong:

- It is **not** hepatocyte-centric. The receptors studied are CD44 and EPHA2, not ASGPR, and the
  chemistry is a free-uptake gapmer, not a GalNAc conjugate. So it does **not** belong to the
  "most ASO delivery advances are liver advances" pattern the ASO route has learned to discount.
- It is **not** solid-tumour delivery either. **Cellular uptake and endosomal escape are what happens
  after an oligonucleotide has already arrived.** Nothing in it addresses whether an ASO given to an
  animal reaches a non-hepatic tumour nodule — the plasma half-life, the vasculature, the interstitial
  pressure, or, for EMC specifically, a hypocellular myxoid matrix.

The one-sentence version: **it explains why free ASO works in the cells where it works. It does not
explain how to get free ASO to an EMC nodule, and it does not claim to.**

---

## 2 · The $0 on-disk cross-check this paper makes possible

A mechanism paper naming two specific receptors is testable against artifacts this repository already
holds, at no cost, and that is the only genuinely new thing here. **Both receptors are already in our
EMC surface work** — they were put there for a different purpose (an AOC targeting arm), and this
paper gives them a second, unrelated meaning (the endogenous machinery of free uptake).

Read from [`emc-expression-panels.json`](../../modalities/emc-expression-panels.json) and
[`emc-surface-normal-window.json`](../../modalities/emc-surface-normal-window.json) — those files own
the numbers; this memo re-types none of them:

- **CD44** — the cross-platform surface-antigen board grades it `CONCORDANT_UP_ON_BOTH` platforms in
  EMC tumour tissue, and it is one of the three antigens
  [`aso-delivery-antigen.json`](../../modalities/aso-delivery-antigen.json) records as clearing both
  *measured* axes before the normal-tissue prior refuses it. HPA window: `BROAD_LIABILITY`.
- **EPHA2** — graded `MOVED_ON_ONE_FLAT_ON_THE_OTHER`. HPA window: `VITAL_OR_IMMUNE_LIABILITY`.

⛔ **Read the direction of that carefully, because it inverts.** In
[`aso-delivery-antigen.md`](./aso-delivery-antigen-2026-08-08.md) a "liability" window is a **refusal**:
an antigen expressed broadly or on vital/immune tissue is a bad *address* to aim a conjugate at.
For *this* paper's mechanism the receptors are not an address at all — they are the cell's own uptake
apparatus, and broad expression is **permissive rather than disqualifying**. The same two rows mean
opposite things in the two uses, and a future reader who carries the liability label across will get
it backwards.

⚠ **What this cross-check does and does not license.** It licenses one sentence: *the two receptors
this mechanism requires are transcriptionally present in EMC tumour tissue on the instruments we have.*
It does not license: that the mechanism operates in EMC, that the receptors are present as **protein on
the cell surface** (these are transcript reads), that surface density is sufficient, or that any ASO
would be taken up by an EMC cell. Those are experiments, and we have no wet lab.

---

## 3 · Item 2 — Silexion / SIL204 in locally advanced pancreatic cancer · **press-only**

**Grade: press-only. NCT number: UNKNOWN — and the zero behind that is qualified.**

Four ClinicalTrials.gov API queries were run on the runner (all HTTP 200): `query.term=SIL204`,
`query.term=SIL-204 OR SIL204`, `query.term=Silexion`, `query.spons=Silexion`. **All four returned zero
studies.** Controls were then run on the same endpoint, and they split:

- ✅ `query.spons=Silence Therapeutics` returned **8** studies and partial-matched two distinct legal
  entities. So the sponsor endpoint answers non-empty and would have matched a sponsor named
  "Silexion Therapeutics …". **That zero is a real absence from this registry.**
- ⛔ `query.term=divesiran` returned **zero** — for a drug whose trial *is* in the registry, under its
  code name SLN124. **The control failed, so every `query.term` zero above is uninformative**, and only
  the sponsor zero carries weight. Recorded rather than quietly dropped: a zero whose control failed is
  an unanswered question wearing the costume of a finding.

**So:** no ClinicalTrials.gov record for this programme as of 2026-08-24. That is *not* evidence the
trial does not exist — the press describes activation at a site in Israel with a German authorisation,
and neither the EU CTIS nor the Israeli MoH register was queried here. **NCT: UNKNOWN.**

**Why it would matter if it were traced.** Press accounts describe **dual intratumoural and systemic**
administration. Intratumoural is route **R1** in
[`lit-targets-aso-delivery-routes.json`](./lit-targets-aso-delivery-routes.json) — the route that
**needs no surface antigen**, which is exactly why the 2026-08-12 rescope pulled it out from under
`BLK-DELIVERY`. A randomised trial with a traced registry record, giving an siRNA intratumourally in a solid tumour,
would be a genuine precedent for that route. **It is not confirmed, so nothing is claimed from it**, and
in any case a precedent in pancreatic cancer is a prior for EMC, never a solution: an EMC nodule's
myxoid matrix is not a pancreatic primary, and no efficacy of any kind is asserted here.

---

## 4 · Item 3 — Silence Therapeutics' siRNA in a rare blood cancer · **trial registry-verified, result press-only**

**The trial is real and traced.** `NCT05499013` — *Study to Assess SLN124 in Patients With Polycythemia
Vera*, official title a **Phase 1/2** open-label dose-escalation followed by a randomised double-blind
phase; sponsor Silence Therapeutics plc; secondary ID **SANRECO**; actual enrolment 69; status
`ACTIVE_NOT_RECRUITING`. The registry describes SLN124 in its own words as *"a double-stranded small
interfering ribonucleic acid (siRNA) targeting transmembrane protease, serine 6 (TMPRSS6) messenger
ribonucleic acid"*.

**Two corrections to the press line as this repository held it**, both from the registry record:

1. The press says "Phase 2". The registry study is **Phase 1/2**; the randomised portion is its phase-2
   part.
2. **`hasResults` is `false`** and the record was last updated **2025-12-19**, before the reported
   readout. There is no registry results record and no peer-reviewed publication was traced. **The
   reported outcome is press-only.** No response figure from the press is repeated here, because none
   of them could be traced to a primary source and this file does not launder a company statistic into
   the repository by quoting it.

**Bearing on our gate: none, and it is the cleanest negative of the three.** Divesiran/SLN124 is a
**GalNAc-conjugated siRNA whose target, TMPRSS6, is a liver gene**; the disease is treated by silencing
a hepatocyte transcript to move iron. It is the canonical hepatocyte-delivery paradigm working exactly
as designed. **A haematological malignancy treated through a liver target is the *opposite* of the
problem the ASO route has** — there is no solid tumour anywhere in it. ⚠ The phrase "rare blood cancer"
in the headline is what made this look adjacent to a rare-cancer programme; the mechanism is what makes
it irrelevant to ours.

### ⭐ The genuinely on-gate thing the same $0 query surfaced

The sponsor control query returned two studies **nobody was looking for**, both by the same sponsor and
both squarely on the ASO route's actual gate — a **systemically administered siRNA in a non-hepatic
solid tumour**:

- **`NCT00938574`** — *Study With Atu027 in Patients With Advanced Solid Cancer*, Phase 1, `COMPLETED`.
- **`NCT01808638`** — *Atu027 Plus Gemcitabine in Advanced or Metastatic Pancreatic Cancer*, Phase 1/2,
  `COMPLETED`.

**Registry existence and status only** — no outcome, efficacy or safety was read or is implied, and
neither trial is recent. They are recorded because they are the shape of evidence
[`TECH-OLIGO-DELIVERY`](../../../systems/graph/technologies.json) is waiting for and the press item was
not, and because a route parked on "no validated way to deliver an oligo to a solid tumour exists"
should know that clinical attempts at exactly that have been registered and completed. **Reading their
results is a follow-up, not a finding** — see §7.

---

## 5 · Grading against the trigger table (proposed — **not applied**)

⛔ `research/method-watch.md` is untouched by this memo; it is the one home for the capability→action
pairing and another agent is working nearby. The proposal is written out here to be applied there.

| Row in `research/method-watch.md` | Does item 1 satisfy it? |
|---|---|
| **oligonucleotide tumour-delivery TECHNOLOGY / candidate** (`TRG-OLIGO-DELIVERY-TECH`) — *"an AOC/conjugate, tumour-penetrating peptide or ligand-targeted LNP that reaches non-hepatic solid tumours, OR a characterised EMC-enriched surface antigen"* | **NO — and it fails conspicuously, on every clause.** No conjugate, no peptide, no LNP; no non-hepatic solid tumour; and CD44/EPHA2 are not offered as an EMC-enriched targeting antigen — our own artifacts already refuse both in that role (§2). Its `on_fire` action, *"name a concrete junction-oligo delivery candidate"*, **cannot be executed from this paper.** |
| **in-silico oligonucleotide/nanoparticle tumour-delivery predictor** (`TRG-OLIGO-DELIVERY-PREDICTOR`) | **NO.** It is a wet-lab mechanism, not a predictor, and it produces nothing scoreable in silico. |
| **vector tumour-delivery** (`TRG-VECTOR-DELIVERY-SOLID-TUMOUR`) | **NO.** Not a vector. |

**⭐ The finding is the gap, not the grade.** A result landed **directly on the ASO route's stated
bottleneck**, in a top cell-biology journal, naming two receptors this repository has already
characterised in EMC — and **no row in the table can catch it**, because both delivery rows require a
*vehicle or an address* and this is *cellular machinery*. That is the same defect shape §4 of
[`method-watch-backfill-2026-08.md`](../../method-watch-backfill-2026-08.md) recorded two days ago: a
row that catches one kind of object and structurally cannot catch another, while looking like coverage.

**Proposed row, for whoever owns that file** — a third delivery row, deliberately narrow:

> | **oligonucleotide CELLULAR-UPTAKE / ENDOSOMAL-ESCAPE mechanism** — a named receptor, trafficking step or escape mechanism governing productive ASO/siRNA uptake, in any cell type | **check the named genes against our EMC surface and expression artifacts at $0** (`emc-expression-panels.json`, `emc-surface-normal-window.json`, `aso-delivery-antigen.json`) and record whether EMC carries the machinery. ⛔ **This row NEVER moves `BLK-DELIVERY`** — it is the third barrier (escape), the blocker is the first (arrival at the tumour). It exists so a mechanism result is *read and cross-checked* rather than mistaken for a gate event or missed entirely. |

If that row is not wanted, the alternative is explicit: record that mechanism-level delivery biology is
**deliberately out of scope**, so the next agent does not re-discover the gap. What must not happen is
the current state, where it is neither watched nor declared unwatched.

---

## 6 · What remains UNKNOWN

1. **Whether the JCB paper contains any in vivo experiment at all** — mouse, xenograft, or otherwise.
   *Neither abstract claims one*, and all five $0 retrieval routes were refused (§1 table). ⚠ The
   Europe PMC OA-repository PDF is the notable one: Europe PMC's own metadata advertises `PPR974551`
   as `isOpenAccess: Y` with a PDF URL, and that URL returns **403**. **The next attempt is not another
   retry** — it is a different door: an institutional or interlibrary copy, or a polite author request.
   Until then this stays UNKNOWN and no sentence anywhere may round it to "cell-only".
2. **Whether the mechanism generalises beyond the cell type studied**, and in particular whether it
   operates in a mesenchymal/sarcoma cell at all. Untested anywhere we can read.
3. **Whether CD44 and EPHA2 are present as surface PROTEIN on EMC cells** at any density. Our reads are
   transcript-level; §2 is a presence check, not a protein measurement.
4. **The NCT (or CTIS / Israeli MoH) registration for Silexion's SIL204 Phase 2/3.** Absent from
   ClinicalTrials.gov on a sponsor query whose control passed; no other registry queried.
5. **Any peer-reviewed report of the divesiran readout.** None traced; the registry carries no results.
6. **What the two completed Atu027 solid-tumour siRNA trials actually showed** — registry status only
   was read. This is the one UNKNOWN on the list that sits on the gate itself.
7. **Whether ISRIB or any endosomal-escape enhancer is a usable adjunct in any setting.** The paper
   reports it as a cell-level manipulation. Nothing about tolerability, exposure or use in an animal or
   a person is known here, and none is implied.

---

## 7 · Recommendation

1. **Do not unpark `RT-ASO`, and do not re-grade `BLK-DELIVERY`.** Nothing retrieved meets
   `TECH-OLIGO-DELIVERY`. This memo is evidence plus a recommendation; the re-grade is not this
   agent's to make.
2. **Add the mechanism row to the trigger table** (§5), or explicitly declare the class out of scope.
3. **Chase the two Atu027 records** — UNKNOWN 6 is the only item here on the gate itself, and it is a
   $0 registry-plus-Europe-PMC read, not a spend. A completed Phase 1/2 of a systemic siRNA in a solid
   tumour is either a precedent or a cautionary result, and either is worth more to this route than all
   three press items combined.
4. **Do not keep retrying the preprint full text** — five routes were refused today and a sixth retry
   buys nothing (UNKNOWN 1). Close cell-only vs in-vivo through a different door or leave it UNKNOWN.
5. **Leave the EMC receptor cross-check where it is** — in §2, as a presence check with its limits
   attached. It does not belong in the ASO manuscript: a mechanism shown in another cell type plus a
   transcript read in EMC tissue is not a delivery claim, and §3c of the manuscript must not acquire
   one.

---

## Appendix · Grades at a glance

| Item | Grade | Moves `BLK-DELIVERY`? |
|---|---|---|
| Antisense delivery pathway (2026-08-11 press) → J Cell Biol 225(9):e202507217 | **traced to primary source** (abstract level; body not retrieved) | **No.** Third barrier, not the first. |
| Silexion SIL204 Phase 2/3, locally advanced pancreatic cancer (2026-07-29 press) | **press-only**; no ClinicalTrials.gov record found on a controlled sponsor query | **No** — and unverified besides. |
| Silence Therapeutics siRNA in a rare blood cancer (2026-08 press) | **trial registry-verified (`NCT05499013`), result press-only** | **No.** Hepatocyte target, no solid tumour. |
| *(unsought)* Atu027 solid-tumour siRNA trials `NCT00938574`, `NCT01808638` | **registry-verified existence and status only** | **Not yet read** — the one on-gate follow-up. |
