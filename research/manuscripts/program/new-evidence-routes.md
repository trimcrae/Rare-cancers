---
id: DOC-NEW-EVIDENCE-ROUTES
title: Where a NEW FACT ABOUT THE DISEASE could come from — three routes, no wet lab
level: L4
kind: memo
status: live
purpose: "Answer one question: given no wet lab, what could produce a piece of evidence that is both NEW and ABOUT EMC — as opposed to about this programme's own instruments — and which of those routes is startable today at $0."
scope: "The EVIDENCE-SOURCE axis. Does not re-rank routes, does not restate the plan, does not price GPU work; the roadmap owns all three. Subordinate to nr4a3-program-map.md and to no-wet-lab-publication-archetypes.md, which owns the publication-ARCHETYPE axis this memo does not repeat."
date: 2026-08-23
last_verified: 2026-08-23
audience: ["maintainers", "autonomous research agents"]
---

# Where a new fact about the disease could come from

> **Why this exists** (trimcrae, 2026-08-23): *"I feel like all the paper paths in this repo end up
> iterating on reviewer feedback and changing narrative forever. I think the underlying reason for this
> is we don't actually have any new evidence to present for anything. Is there some way we can get this
> without a wet lab?"*
>
> ⛔ **Nothing here asserts efficacy, selectivity, safety, a therapeutic window or clinical readiness for
> any agent or route, and nothing here is a diagnosis.** No count below is a patient count.

---

## 0 · The diagnosis, sharpened — and the sharpening is what makes it actionable

**The premise is nearly right and the one word that is wrong is the word that matters.** This programme
has produced a great deal of new evidence. It has produced almost no new evidence *about the disease*.

Read what the [scoreboard](../nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language)
actually holds. A ranked congeneric ΔΔG map. The first forward/reverse hysteresis this programme ever
measured. A replicate SD set against per-leg MBAR standard errors. A preregistered null that came back
as a bound. Those are real measurements, honestly reported, and several are genuinely novel.

**Every one of them is a measurement about an INSTRUMENT.** Does our free-energy engine reproduce a known
answer; does a thermodynamic cycle close; does a control fire. That is methods-about-methods. It is worth
publishing and this repository publishes it. But it gives a reviewer nothing about extraskeletal myxoid
chondrosarcoma to agree or disagree with — so the only surface left to argue over is the framing, and
framing is infinitely revisable. **That is the mechanism behind the complaint, and it is not a reviewer
problem.**

⛔ **And the second half compounds it: three separate positive controls failed** (`valB_mini` wrong sign,
the `SMARCA2/4` sensitivity control null on an adequately-powered design, the `NR-V04` retrospective
discordant). The scoreboard's own words are that every paralogue-selectivity statement is therefore an
**unvalidated prediction**. A paper whose central claim is unvalidated by construction has nothing but
narrative to offer, and will be asked to change it every round, forever.

⚠ **The independent corroboration is on the record and it is unflattering.** The aiXiv history for the
one paper that has been iterated: **v1.4 rated 6, v1.5 rated 5 — down, after substantive edits** — and
the [`aixiv-submission`](../../../.claude/skills/aixiv-submission/SKILL.md) skill's own summary is that
four substantive revisions of one paper moved it nowhere while a *different* paper of the right shape
scored 7 on its first version. **Prose iteration is measurably not the lever.**

★ **So the question this memo answers is narrower and better than "how do we get evidence":
what could produce ONE new true statement about this disease, with no laboratory?**

---

## 1 · The structural blind spot — and it is documented in this repository's own code

Every EMC molecular count this programme holds descends from a search over **what a depositor wrote**.
`emc_cohort_search.py` asked GEO for a fourth EMC expression cohort, returned a bounded negative, and
states the bound in its own header:

> *"GEO's `esearch` matches depositor prose. A series whose title and summary never say 'extraskeletal
> myxoid chondrosarcoma' is invisible to every query below however many EMC samples it contains, and EMC
> samples sitting inside a pan-sarcoma deposit under a generic title are exactly the case that would be
> missed."*

⛔ **That case is not hypothetical, and this repository has already been bitten by it.** The docstring of
[`atr_hrd_sarcoma_series.py`](../../modalities/atr_hrd_sarcoma_series.py) records that **GSE24369 is
titled "low-grade fibromyxoid sarcoma" and silently contains six EMC tumours** — a substantial share of
every EMC sample the transcriptional-output manuscript reads, sitting under the name of a different
disease. It was found by accident, not by a query.

★ **The bound is the opening.** Nothing here has ever searched anything other than prose. Two things can
be searched instead, and neither has been tried: **the data itself**, and **a deposit that is in the
blind spot by construction**.

---

## 2 · ROUTE A1 · Search the reads, not the description — the public splice-junction index

**Snaptron** serves the exon-exon junctions of uniformly reprocessed public RNA-seq; its `srav3h`
compilation is drawn from the SRA arm of **recount3** and is documented as ~228 million junctions from
~316 thousand public human samples, queryable by gene symbol or coordinates over a plain HTTP interface
([recount3, *Genome Biology* 2021](https://link.springer.com/article/10.1186/s13059-021-02533-6);
[snaptron.cs.jhu.edu](https://snaptron.cs.jhu.edu/)).

**A junction is a property of the reads.** A sample whose depositor never typed "EMC" still contributes
its junctions. So a query over that index is *blind to the prose* and therefore reaches exactly the
population `emc_cohort_search.py` says it cannot.

- ⭐ **Never attempted here.** `snaptron`, `recount3` and `ARCHS4` return **zero** matches across the
  whole repository (measured 2026-08-23).
- **$0**, CPU, minutes. The dev sandbox's egress proxy 403s the host, so it runs on an Actions runner
  like every other fetch here.
- ⛔ **What it might find is not assumed.** Whether a splice index carries the junction classes a fusion
  transcript produces — a chimeric junction joining two loci is a different object from an intragenic
  one, and only one of them is certainly in a splice index — **is not answerable from documentation and
  must not be answered from recollection.** The instrument therefore **probes before it searches**: the
  first run measures the served columns, record counts and coordinate spans, and emits
  `PROBED_NOT_SEARCHED`. The searchable design is written against that measurement.
- **Even the null is a result**, and a publishable one: *every public human RNA-seq sample was queried
  for this disease's driver junction, and here is the census*. That is a statement no one has made.

---

## 3 · ROUTE A2 · A named deposit sitting in the blind spot — pan-sarcoma methylation

**GSE140686** is the reference set of Koelsche et al., *Sarcoma classification by DNA methylation
profiling*, [Nat Commun 2021;12:498](https://www.nature.com/articles/s41467-020-20603-4) — a classifier
trained across sarcoma methylation classes, with **extraskeletal myxoid chondrosarcoma among them**.
IDATs are open in GEO; **E-MTAB-9875** is the EBI mirror of the same study.

★ **Its title names no disease.** It is the textbook instance of the missed case in §1 — a pan-sarcoma
deposit under a generic title — and it is invisible to every query this repository has ever run.

- ⭐ **A modality this programme holds none of.** There is no DNA methylation data for this disease
  anywhere in this repository. The entire molecular substrate is expression, across three cohorts.
- **$0**, and the sample-level read that establishes how many EMC samples are actually in there is the
  same shape as reads this repo already does routinely.
- ⚠ **What a count from it would and would not be.** A sample counted from per-sample metadata is a
  **depositor claim**, exactly as a series title is — never a diagnosis. And a deposit may label by
  methylation-class code rather than by disease name, which a term match cannot see; that is a bound on
  the read, recorded as such rather than reported as an absence.

⚠ **Note what these two routes are NOT.** Neither is a new patient and neither is new follow-up. They are
existing measurements on existing material that nobody has pointed at this disease. That is the honest
ceiling and it should be stated in any paper's first paragraph, not left for a reviewer to find.

---

## 4 · ROUTE B · The in-silico axis that is highly regarded AND unexploited here

⛔ **First, what is NOT the answer: more of the simulation this programme already does.** The degrader
lane needs to resolve a paralogue ΔΔG of roughly one kilocalorie per mole with an engine that has
returned that class of quantity with the **wrong sign**. That is a request for a measurement below what
the method resolves, and no amount of additional sampling changes it. §5 of CLAUDE.md is explicit that
deepening a test past its field standard is a default NO.

★ **What is unexploited is a different axis entirely, and this repository has already written the paper
that needs it.** [`fusion-condensate-disruption-paper.md`](../fusion-direct/fusion-condensate-disruption-paper.md)
argues that the fusion's aberrant **biomolecular condensate** behaviour is the one handle that is
fusion-selective by construction — wild-type NR4A3 lacks the partner's low-complexity domain entirely,
so the behaviour is fusion-emergent. It is, by its own banner, the earliest-stage of the protein-level
routes. **Its entire first-party evidence is amino-acid composition counting** — SYGQ fraction, aromatic
content, Shannon entropy — which its own artifact correctly calls *sequence-derived proxies, not a
condensate measurement*.

**The field-standard instrument for exactly that claim exists, is well regarded, and appears nowhere in
this repository.** Residue-resolution coarse-grained models of disordered-protein phase behaviour —
`CALVADOS` and `Mpipi` — return **zero** matches repo-wide (measured 2026-08-23). CALVADOS 3 extends to
multi-domain proteins, was reoptimised against SAXS and PRE-NMR single-chain data, and was assessed
blind in **CASP16**; the family has been benchmarked head-to-head in
[PLOS Comput Biol](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1012737).

⭐ **And it has a specific new claim attached, which is what makes it worth doing rather than merely
respectable.** The partner distribution is not one fusion: EWSR1 is the commonest, TAF15 second, and
**TCF12 is not a FET protein at all** (the measured distribution has its one home in
[`no-wet-lab-publication-archetypes.md`](../no-wet-lab-publication-archetypes.md) §2, item 8, which also
records that a model treating "the EMC fusion" as the canonical one omits roughly one patient in five).
A condensate model makes a **differential** prediction across those chimeras. That is:

- a statement **about the disease**, not about our engine;
- **partner-stratified**, which is a clinically meaningful axis nobody has modelled;
- **falsifiable by a wet lab that is not ours**, which is the correct ceiling for computational work;
- **cheaper than it looks, and this is measured rather than assumed** (2026-08-23, from the package's own
  README): CALVADOS is open source, `pip`-installable, and **built on OpenMM — the engine this
  repository's MD stack already runs on** — and it runs on CPU as well as CUDA. Its founding result is
  that *single-chain* properties predict phase behaviour
  ([PNAS 2021](https://doi.org/10.1073/pnas.2111696118)), and the multi-domain extension is
  [Protein Science 2024](https://doi.org/10.1002/pro.5172). **So the single-chain arm — the one that
  carries the partner contrast — is a CI-runner job at $0, not a GPU purchase.** Only the slab
  phase-coexistence arm needs a card, and it is not needed to get the first differential read.

⚠ **Sequence in, sequence out.** This route consumes the fusion architecture the repo has already
audited ([`emc-fet-idr-census.json`](../../modalities/emc-fet-idr-census.json)); it needs no cohort, no
sample and no access. It is the one route on this page that is blocked on nothing but a decision to
scope it.

---

## 5 · What was built for this memo, and what it deliberately does not claim

[`emc_data_level_sweep.py`](../../modalities/emc_data_level_sweep.py) — the $0 CI instrument for routes
A1 and A2, wired as the `data-level-sweep` mode of
[`emc-expression-datasets.yml`](../../../.github/workflows/emc-expression-datasets.yml).

It is built to the discipline the rest of this repository is built to, and the guards are the deliverable
as much as the search is, because **this instrument's most likely output is a zero**:

- a **known-answer transport control** that must return records and an **absent control** that must
  return none; if either misbehaves the arm reports `TRANSPORT_FAILED` and its counts are withheld,
  because a null from an instrument that recovers no known positive is a broken search, not a negative;
- a header-only read reports `SAMPLE_LEVEL_NOT_READ`, never "no EMC samples" — an absent reading is not
  a reading of absence;
- the **skeletal** myxoid chondrosarcoma — a different tumour with a different driver — is counted in
  its own bucket and never summed into the extraskeletal count, because a substring search hits both;
- an empty cache cannot emit any verdict at all.

All four are asserted **offline, before one byte is fetched** (`--selftest`, 8 guard groups).

⛔ **It does not run a fusion search and does not claim one.** See §2.

### 5.1 · What the first run measured (2026-08-23, run `32671782752`, $0)

**Route A1 — the index answers, and it serves more than the design needed.** All three compilations
responded (`srav3h`, `gtexv2`, `tcgav2`); the transport control returned records and the absent control
returned none, so the arm's counts are admissible. Junction records at each locus: NR4A3 **5,011**,
EWSR1 **25,781**, TAF15 **24,012**, TCF12 **37,521**.

⭐ **The design-relevant finding is the served column list**, and it settles the question §2 refused to
answer from recollection. Each junction record carries `annotated`, **`left_annotated` and
`right_annotated` separately**, plus **`samples` and `samples_count`** — the list of samples the junction
was seen in. So a junction with one annotated end and one unannotated end is directly selectable, and
every such hit names the samples carrying it. ⚠ **And the negative half is equally informative:** every
record returned for a gene query sits on that gene's own chromosome, so this index does **not** carry
junctions joining two chromosomes. A search here must therefore key on the intragenic signature a fusion
leaves inside NR4A3, not on a chimeric junction. That is the design, and it is now written against a
measurement.

**Route A2 — the deposit is fully readable and carries no diagnoses at all.** All **1,505** declared
samples were read, on two array platforms (`GPL13534`, `GPL21145`). Samples naming this disease: **zero**
— and, ⛔ **this is not a reading of absence.** Every sample record is titled *"sarcoma classifier
reference case N"* with characteristics *"tissue: sarcoma"* and nothing further; the strings `EMC`,
`chondrosarcoma`, `myxoid` and `NR4A3` appear **zero times across the entire 1,505-sample stream**. The
GEO records simply do not state which case is which. The guard's `NO_SAMPLE_NAMES_EMC` verdict is
therefore correct and the route is **not** closed: the per-case diagnoses live in the paper's
supplementary table, and joining that table to the sample list is the next step. **A deposit that
withholds its labels in GEO is exactly why the arm was built to report what it could not read rather
than what it did not find.**

---

### 5.2 · What the SECOND run measured (2026-08-23, run `32672524143`, $0) — and what each one now needs

**Route A1 — the search RAN, its controls formally passed, and the honest reading is that the score is
not yet specific enough to report a candidate list.**

| gene | role | annotated junctions | samples expressing | candidates | rate |
|---|---|---:|---:|---:|---:|
| FLI1 | ⭐ positive control | 27 | 103,763 | 11,973 | **0.1154** |
| GAPDH | ⛔ negative control | 52 | 260,180 | 6,577 | **0.0253** |
| NR4A3 | target | 18 | 34,013 | 1,642 | 0.0483 |
| EWSR1 | context | 41 | 231,547 | 9,709 | 0.0419 |
| TAF15 | context | 39 | 185,331 | 1,589 | 0.0086 |
| TCF12 | context | 51 | 188,661 | 4,598 | 0.0244 |

⭐ **The positive control fires 4.6× the negative one, so the signature is real and detectable.** The gate
passed on its own terms and the strand was derived as `+` for every gene.

⛔ **But NR4A3's rate is only about 1.9× the negative control's, and the negative control itself returns
6,577 "candidates". So `1,642` is NOT 1,642 EMC candidates** — it is dominated by whatever background
also produces GAPDH's hits, and this memo must not quote it as a finding. **The next move is
specificity, not more searching**, and three levers are available before anything else: require the
depleted 5' junction to be well covered in OTHER samples (which separates a real absence from a sparsely
annotated 5' end); raise the downstream-coverage floor; and add a second, independent discriminator —
NR4A3 absolute expression, which in this disease is driven from a partner promoter and should be high.
⚠ **A candidate rate is only interpretable against the negative control's rate on the same day**, so
every tightening must be re-scored on all three genes together.

**Route A2 — the label source is still not located, and the reason is a measured transport failure
rather than an absence.** The article fetch returned **HTTP 200 in 3,038 bytes** — a stub, not a paper —
so **zero supplementary links were found and zero files were parsed.** The arm reported
`LABELS_NOT_LOCATED` exactly as designed; had it reported "no EMC" it would have closed a live route on
a page it never actually read.

⭐ **And the next route is already measured as open.** The EBI mirror `E-MTAB-9875` answered **HTTP 200
with a real BioStudies record** (title *"Methylation profiling (450K and EPIC array) for sarcoma
classification"*, release date 2021-05-01), and it was truncated only by this module's own 400,000-byte
cap. An ArrayExpress study carries an **SDRF** — the sample-and-data-relationship file whose whole
purpose is per-sample characteristics — and EBI did not serve a stub. **That, and PMC, are the two
routes to try before anything is concluded about this deposit.**

## 6 · Limits of this memo

- **§4's grade is a judgement about fit, not a measured result.** That the coarse-grained condensate
  models are well regarded, that they are obtainable and OpenMM-based, and that this repository has
  never used them are all measured; that they would produce a *discriminating* answer across the three
  fusion partners is a **hypothesis**, and the honest first step is a scoping pass that states, before
  anything runs, what the read would have to show to be worth reporting — and what result would make it
  a negative rather than an inconclusive.
- **Route A2's EMC sample count is unmeasured at the time of writing.** That the deposit exists, is open
  and includes this disease as a class is sourced; how many samples it holds is what the probe is for.
- **Nothing here reorders the plan.** The roadmap owns the ordering and the spend ladder. This memo adds
  an axis — *where would a new fact come from* — that no register on the board carries.
- ⚠ **And it does not claim these are the only three.** They are the ones that survived asking, of every
  route on the board, the single question in the title: **would this produce a new true statement about
  EMC, or another one about us?**
