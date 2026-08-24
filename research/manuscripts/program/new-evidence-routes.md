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
  ⛔ **SUPERSEDED BY §5.4, retained because it is what the route was proposed on.** The null arrived
  and it is NOT a paper — the census the bullet imagines is a census of what the instrument can
  reach, not of the disease. The bullet is the reason the route was worth running; it is not a
  finding, and it must not be quoted as one.

---

## 3 · ROUTE A2 · A named deposit sitting in the blind spot — pan-sarcoma methylation

**GSE140686** is the reference set of Koelsche et al., *Sarcoma classification by DNA methylation
profiling*, [Nat Commun 2021;12:498](https://www.nature.com/articles/s41467-020-20603-4) — a classifier
trained across sarcoma methylation classes, with **extraskeletal myxoid chondrosarcoma among them**.
IDATs are open in GEO. ⛔ **A previous version of this line called `E-MTAB-9875` "the EBI mirror of the same study". That was an identifier written from recollection and it is wrong** — see §5.5, which records what the record actually serves.

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
- ✅ **ANSWERED — see §5.5.** The deposit states no diagnoses at all; the labels are in the paper, and
  the two are joined by an identifier **both sides declare**. ⚠ The caution above stands unchanged and
  now applies to the joined count: it is an author claim carried across a join, not a diagnosis.

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

⭐ **And the next route is already measured as open.** ⚠ *Superseded, retained: `E-MTAB-9875` is called
"the EBI mirror" here and is not one — §5.5.* It answered **HTTP 200
with a real BioStudies record** (title *"Methylation profiling (450K and EPIC array) for sarcoma
classification"*, release date 2021-05-01), and it was truncated only by this module's own 400,000-byte
cap. An ArrayExpress study carries an **SDRF** — the sample-and-data-relationship file whose whole
purpose is per-sample characteristics — and EBI did not serve a stub. **That, and PMC, are the two
routes to try before anything is concluded about this deposit.**

---

### 5.3 · The specificity revision (2026-08-24) — PRE-REGISTERED, written before the fetch

⭐ **This section states what the instrument will do and what would make it a negative, before the
run that answers it.** Nothing below is a result. The run's numbers land in
[`emc-data-level-sweep.json`](../../modalities/emc-data-level-sweep.json), which is their one home.

**What changed, and why the change is structural rather than a tuning pass.** §5.2's search fixed
one operating point in advance and reported one number per gene. When that number turned out not to
separate there was no way to ask what a tighter one would have done — and because a candidate rate
is only interpretable against the negative rate on the same day's compilation, a second fetch could
not answer it either. So the module now sweeps a **four-axis grid inside one fetch and scores every
gene at every cell from one parse.** Re-scoring every tightening on the controls and the target
together is now a property of the code, not something a future session has to remember.

**The five levers.** Three are the ones §5.2 named; two are added here.

| # | lever | what it separates |
|---|---|---|
| 1 | **5'-junction support** — the 5' junctions used in the ratio must be carried by a minimum fraction of the gene's own expressing samples | a real absence from a **sparsely annotated or alternatively-used 5' end**, which is the confound most likely to be producing the background |
| 2 | **downstream-coverage floor** | "5' end replaced" from "gene barely on" |
| 3 | **absolute expression**, as a within-gene percentile of downstream coverage | in this disease the 3' half is driven from a partner promoter, so it should be **abundant, not merely present**. A percentile rather than an absolute floor, because GAPDH's median and NR4A3's median are orders of magnitude apart |
| 4 | **promiscuity track** — drop candidates that are also candidates at an ordinary gene in the same cell | a **3'-biased library**, which looks 5'-depleted at every gene at once, from a gene-specific truncation. ⚠ A real EMC sample can also be a degraded library, so this is a *track* the selection may or may not pick, scored beside the unfiltered one |
| 5 | **breakpoint-rank concentration** — how tightly a gene's candidates agree on where, along the transcript, coverage starts | a **recurrent** rearrangement, which joins the partner to the same place in most tumours, from background that has no reason to start anywhere in particular. Reported as a contrast across all genes, never read alone |

⛔ **A negative PANEL replaces the single negative control, and this is the biggest change.** One
negative gene gives one number and no idea of its spread — and §5.2's own context row already ranged
over a factor of five between ordinary genes, which is why "above GAPDH" and "above what an ordinary
gene does" are different claims and only the second is worth anything. Seven genes spanning a wide
range of expression depth now define an **envelope, taken as the maximum**: the target has to clear
the hottest ordinary gene, not the average one. ⚠ Its one assumption is stated in the code — that no
panel gene is itself a recurrent 3' fusion partner — and the error is conservative by construction,
because a panel gene that *is* one fires more, raises the envelope, and makes the target harder to
call specific. A **second positive control** is added for the same reason: one positive tells you the
score can fire, not whether the rate it fires at is typical of the signature or a peculiarity of one
locus.

⛔⛔ **The operating point is chosen on the CONTROLS ALONE and the target is read at it afterwards.**
Sweeping a grid and then reading off the cell where the target looks best is how a null becomes a
finding. The selection function is handed the positive controls and the negative panel and is not
handed the target at all, and the offline suite asserts it by replacing every target number with
anything whatsoever and requiring the selected cell not to move.

★ **Why the selection rule is "drive the background to a ceiling, then keep the positive" and not
"maximise a ratio."** This disease is vanishingly rare and public RNA-seq is overwhelmingly not
sarcoma, so whatever the true number of EMC samples in the compilation is, it is *a number of
samples, not a percentage of them*. A background that calls even one sample in two hundred swamps
the signal however favourable the ratio looks. The pre-registered rule is therefore: among cells
where the negative-panel envelope sits at or under the ceiling **and** a positive control still
recovers a population, take the cell with the largest positive-control enrichment.

**The three pre-registered outcomes, and all three are reportable.** ⚠ **A FOURTH was added after
the run** — `TARGET_UNDERPOWERED_AT_THE_OPERATING_POINT` — because this list has a hole that only
showed up once the grid had been swept: it assumes the cell the controls select still leaves the
target enough samples to answer, and the run's did not. §5.4 records the amendment, what it reads
(pool size and background rate, never the target's count) and why the gap existed. **This paragraph
is left as it was written**, because what was pre-registered is part of the record.

- **`NO_SPECIFIC_REGIME`** — no cell holds the negative panel at the ceiling while a positive
  control survives. Target counts withheld. ⭐ This is a **result, not a failure**: it says the
  5'-depletion signature, scored over this index, cannot be made specific enough for a candidate
  list at any combination of these thresholds, and the whole trade-off surface is in the artifact so
  the shape of that limit is readable rather than asserted.
- **`TARGET_DOES_NOT_SEPARATE`** — a specific regime exists on the controls and the target does not
  clear the envelope by the pre-registered margin. No candidate list. ⭐ **This is the outcome the
  §5.2 numbers point at, and it is the publishable one:** every public human RNA-seq sample in this
  compilation scored for the intragenic signature a 5'-truncating rearrangement leaves, on an
  instrument whose positive controls fire and whose negative panel is held at the ceiling, and the
  target does not rise above what an ordinary gene does. Nobody has made that statement.
  ⛔ **"THE PUBLISHABLE ONE" IS SUPERSEDED BY §5.4 — retained because it is what was pre-registered,
  and a pre-registration is worthless if it is edited once the answer is in.** The outcome landed
  and it is not a paper. ⚠ Note WHERE the prediction failed: not on whether the outcome would be
  honest — it is — but on the assumption that an honest bounded null about a SIGNATURE is a
  statement about the DISEASE. It is not, and §5.4 says why.
- **`TARGET_SEPARATES`** — the 95% lower bound on the target's enrichment over the envelope exceeds
  the pre-registered bar. ⛔ **That would be an ENRICHMENT, NOT A DETECTION.** No individual sample
  in such a list is thereby a fusion, a tumour, or a diagnosis, and the bar is an effect size rather
  than a p-value precisely because with tens of thousands of samples in each denominator a lower
  bound above 1 is reachable on an effect far too small to be a candidate list.

⛔ **What §5.2's `1,642` is, and what it is not.** It is the count at what the grid now calls the
reference cell — the first search's operating point, retained so the two runs stay comparable. It is
dominated by whatever background also produces the negative control's thousands of hits. It is not a
candidate list, it is not a count of anything about this disease, and it must not be quoted as one.

---

### 5.4 · What the THIRD run measured (2026-08-24, run `32676239799`, $0) — the answer, and it is a negative

**The instrument works, the target does not separate, and the reason the second run looked like it
might is now measured.** Every figure below has its one home in
[`emc-data-level-sweep.json`](../../modalities/emc-data-level-sweep.json).

⭐ **First, the scorer reproduces the second run exactly at the reference cell** — FLI1, GAPDH,
NR4A3, EWSR1, TAF15 and TCF12 all return the counts and rates §5.2 records. The grid is a
superset of the old search, not a different one, so the two runs are directly comparable.

⛔⛔ **THE NEGATIVE PANEL SETTLES §5.2's QUESTION IMMEDIATELY: THE "1.9×" WAS MEASURING GAPDH, NOT
BACKGROUND.** At that same reference cell the ordinary genes run **TBP 0.0699 · RPL13A 0.0419 ·
PGK1 0.0399 · ACTB 0.0331 · POLR2A 0.0322 · GAPDH 0.0253 · SDHA 0.0158** — a 4.4-fold spread among
genes that have nothing in common with this disease. NR4A3's 0.0483 sits **inside** that spread,
under its top. GAPDH is the second-quietest gene in the panel, so scoring the target against it
alone manufactured a ratio out of where one arbitrary gene happens to fall. ⚠ **One negative control
was never measuring background; it was measuring one gene, and the spread is the whole point.**

⭐ **The controls do reach a specific regime, and comfortably.** Both positive controls fired; 28 of
384 cells hold the ordinary-gene envelope at or under the pre-registered ceiling while a positive
control survives. At the control-selected point ERG runs at **252× the envelope** and FLI1 at
**13.4×**, against panel rates of 0.0000–0.0011. The signature is real, and this instrument
separates it from background by more than two orders of magnitude.

⛔ **But the operating point cannot answer about the target, and this is the honest core of the
run.** The regime tight enough to hold the background down leaves NR4A3 only **219 samples**. At an
envelope of 0.0011, a target enriched at the pre-registered 3× would be expected to yield **0.73**
candidates there. NR4A3 returned zero — in that cell, and in all 28 — and **a zero in a pool of 219
excludes nothing.** The artifact reports `TARGET_UNDERPOWERED_AT_THE_OPERATING_POINT` and says what
pool it would have needed (~1,498). ⚠ *This power criterion was added after seeing the first grid
run land there;* it reads the target's pool size and the background rate and never its count, and
the offline suite asserts the operating point does not move under it.

★ **The statement that IS powered.** Asked of every cell at once, the weaker question — does the
target's rate exceed the ordinary-gene envelope **at all** — stays answerable at the loose cells,
where NR4A3 still has all 34,013 of its samples. **It does not, at any of the 288 comparable
cells.** At the best-powered comparison the envelope gene predicts 2,477 candidates and NR4A3
returns 1,665: a ratio of **0.67, 95% CI 0.64–0.71**.

⚠ **And the honest qualifier, which the artifact carries so it cannot be dropped: the envelope is a
MAXIMUM, and clearing it is a weaker result than being quiet.** At that same cell NR4A3 is above
**five of the six** scoreable panel genes and runs at **1.50× the panel median**. So the correct
reading is not "below background" — it is **inside the ordinary-gene distribution, under its top
and above its middle**, in a panel whose own genes span 4.5-fold. That is what no excess looks
like when the background is characterised properly instead of by one gene.

⛔ **What the run does and does not say.** At the loose end the target is indistinguishable from
ordinary genes; at the sharp end — where the instrument demonstrably resolves a real 5'-truncated
population at 13× and 252× — it returns zero but cannot be believed. **Neither end shows an
excess, and no candidate list exists here.** It does **not** say EMC is absent from this
compilation, and it is not a statement about the disease. The instrument's limit is now measured
from both sides rather than argued: the regime sharp enough to be specific is too sharp to leave
the target enough samples, and the regime loose enough to keep them cannot tell a truncation from
an alternative promoter. ★ **That limit — with the pool a decisive test would need, ~1,498 against
the 219 available — is the most useful thing this run produces**, because it says what would have
to change for the question to be answerable at all, and the whole 384-row surface behind it is in
the artifact.

⛔⛔ **THIS IS NOT A PAPER** (trimcrae, 2026-08-24, on being shown the result in plain language).
**SUPERSEDES the paragraph this replaces**, which argued it was worth publishing as it stands; that
was the agent's judgement and it was wrong. ⚠ **The claim that this arm's null is publishable
appears in three earlier places written before the answer existed — §2's last bullet, §5.3's
`TARGET_DOES_NOT_SEPARATE` row and this section. All three are now marked. Do not re-derive the
argument from any of them.**

★ **And the reason is diagnosable in this memo's own opening terms, which is what makes it worth
recording rather than merely obeying.** §0 says this programme's problem is that it keeps producing
measurements about its own INSTRUMENTS rather than about the disease. Read what this run actually
established, in order:

- the junction index answers, and what it serves — *about the index*;
- the 5'-depletion score fires on two known 5'-truncated genes and not on ordinary ones — **about
  the score**;
- the regime that makes the score specific leaves the target too few samples to test — **about the
  score's reach**;
- NR4A3 sits inside the ordinary-gene spread — about the target, and it is the only line here that
  is, but it is a null obtained at the setting where the instrument cannot tell a truncated 5' end
  from an ordinary alternative start.

⛔ **So the one statement about the disease is the one the instrument was least able to make.** A
paper built on this would be another paper about our own apparatus wearing a disease's name — the
exact thing §0 was written to stop, and the exact thing that makes a manuscript infinitely
revisable because there is nothing in it for a reviewer to disagree with.

✅ **What the run IS for, undiminished.** It is a **bound**, and bounds are how the next decision
gets made cheaply. ⚠ **Stated at exactly its strength, because the stronger version is tempting and
wrong:** this signature, scored over this index, **did not** reach this disease — *not* that it
cannot. The test that could have decided it was underpowered, and the price of powering it is now a
number rather than a guess: about **1,498** target samples where **219** exist. That is what belongs
in the record, and it is in the record. It **bounds** a route at $0 that would otherwise have been
re-proposed on the assumption the bullet in §2 was written on. ⚠ **The routes it does not touch** are
the ones that do not depend on this signature: a chimeric junction is not in this index at all
(§5.1), and the deposits in §3 and §5.5 are unaffected by this result.

⚠ **What would change the call** — stated so a later session tests it instead of re-arguing it:
a source that supplies enough NR4A3-expressing samples to power the sharp regime, or a signature
that does not degrade at the loose end. Neither is this run, and neither is a re-run of it.

⚠ **Route A2's status here is SUPERSEDED BY §5.5, retained because it was true when written.** This
run's Springer article fetch did again return a stub and the arm did again report
`LABELS_NOT_LOCATED`, both correctly and for the same measured reason. ⛔ **But the closing clause —
that the EBI and PMC routes "remain the next step and remain untried" — stopped being true about an
hour later.** They were tried, and §5.5 records what they returned: the labels are public, and the
route is open.

---

### 5.5 · What the ARM-2 runs measured (2026-08-24, runs `32676258708` / `32676775613` / `32677318919`, $0) — **Route A2 is OPEN**

⚠ **Numbered by ARM, not by a global run count.** §5.3–5.4 report arm 1 (the junction index) and were dispatched independently on the same day, so a single ordinal across both arms would name two different runs.

⭐⭐ **The labels are public, the join is exact, and the IDATs are downloadable.** Full record:
[`emc-data-level-sweep.json`](../../modalities/emc-data-level-sweep.json).

**First, this memo was wrong about the mirror, and the error was an identifier written from
recollection.** §3 called `E-MTAB-9875` "the EBI mirror of the same study". The record EBI actually
serves under that accession is **a different study** — *"Methylation profiling (450K and EPIC array)
for sarcoma classification"*, from UCL, **n=986**, whose own Description names its paper as a
**validation study of the DKFZ sarcoma classifier**. Koelsche et al. is the classifier it validates,
not the study it mirrors, and `Koelsche` and `GSE140686` appear **zero times** in it. Nothing had ever
checked. ⚠ The search that should have settled it was then run, and it found **no EBI mirror of this series
at all**: BioStudies returned **36** accessions for `GSE140686`, **34 of them Europe PMC *literature*
records — papers citing the deposit, not copies of it** — and the two that are not (`E-GEOD-57107`,
`E-GEOD-4560`) are other studies. The instrument's first pass called ten of the literature records
"mirrors" on a bare string match; a mirror must be a **data** record, and the rule is now enforced
rather than described. Both search controls hold (a known accession returns hits, a nonexistent one
returns none), so *"no mirror"* is a finding here and not a broken query.

★ **The correction is not a loss, because a second deposit is a second chance — and this one's labels
are open.** E-MTAB-9875's per-sample `disease` field is populated, its **54** categories sum to
**986 = its own declared sample count**, and **none of them is this disease.** That zero is admissible
precisely *because* the census is complete: every sample is accounted for by name. ⛔ Its **112**
`Chondrosarcoma`, **17** `Chondroblastoma` and **14** `Chondromyxoid Fibroma` are **skeletal tumours in
their own bucket and are never summed into an EMC count** — a substring search would have turned 143
cases of other diseases into a cohort that does not exist.

**And then GSE140686 itself opened.** The rungs, each recorded with its own outcome:

| rung | outcome |
|---|---|
| nature.com | **HTTP 200 in 3,038 bytes** — a stub. Zero links discoverable. |
| PMC article page | **a Google reCAPTCHA challenge page**, HTTP 200 in 21,246 bytes on the first attempt — which a byte-size stub test grades as healthy. It served the real article on a later attempt. |
| GEO series header | declares `!Series_pubmed_id` → **PMID 33479225** |
| `elink` (pubmed→pmc) | → **PMC7819999**. ⭐ Every identifier discovered from the one above it; none typed. |
| Europe PMC `supplementaryFiles` | **the route that worked** — 18 members, on the *second* candidate URL shape |

⭐ **Three of the paper's supplementary tables name this disease**, and they agree with each other:

- **MOESM4** (reference set) — **10** cases labelled *Extraskeletal myxoid chondrosarcoma*, each also
  carrying *methylation class extraskeletal myxoid chondrosarcoma*;
- **MOESM5** (class table) — the EMC methylation class, **n = 10**, median age 54 (39–79). That it
  matches MOESM4's row count is an internal consistency check, and it passes;
- **MOESM6** (validation set) — **2** further cases: one histologically EMC that the classifier called
  SEF, and one *"Sarcoma, NOS"* carrying an **EWSR1:NR4A3 fusion**.

⭐⭐ **The join is a lookup, not an alignment, and that is the whole value of the route.** GSE140686's
sample records name no disease — but each one carries `!Sample_description = REFERENCE_SAMPLE 259`,
and the paper's tables key their rows on **exactly that string**. Both sides declare the identifier,
so the join is a dictionary lookup. ⚠ Matching the two **by ordinal position** would have handed every
case a plausible-looking partner and been **invisible if wrong**; nothing does, and a label with no
deposited counterpart is reported unjoined rather than absorbed by a neighbour.

**All 12 join, and all 12 have downloadable IDATs — 24 files, Grn+Red per case; 9 on 450K
(`GPL13534`), 3 on EPIC (`GPL21145`).** ⭐ **"Downloadable" here is MEASURED, not listed:** every one
of the 24 was probed with a `HEAD` request and every one answered **200**, **122,009,911 bytes** in
total, none unreachable. That distinction is not pedantry — `!Sample_supplementary_file` is a string
in a metadata record, and a cohort described as downloadable on the strength of it would be a
populated field reported as a measured one.

⛔ **What this count is and is not.** It is what the paper's authors labelled, carried across a
declared join. **It is not a diagnosis, not a re-review of any case, and not a patient count.** The
reference and validation sets are reported separately and must not be pooled without saying so: the
reference set is the class the classifier was **trained on**, so it is enriched for cases that look
like the class by construction, and the validation set is held out. **Any claim resting on these
twelve inherits both bounds.**

★ **What is now true that was not this morning: this repository can hold DNA methylation data for
extraskeletal myxoid chondrosarcoma, a modality it had none of, in a deposit whose title names no
disease and which no prose search here could ever have found.** ⚠ **What it is not yet:** nothing has
been downloaded, nothing processed, and no methylation claim of any kind is made or implied here.
Twelve cases is a small n on a heterogeneous array platform, and what such a cohort could actually
answer — and what it could not — is the scoping question this route now owes, not a result it has.

### 5.6 · The paper judgement, and the decision — NOT a priority (trimcrae, 2026-08-24)

★ **The route can now name its paper, which is what §5 of CLAUDE.md asks of it. It was then
deprioritised on the merits, and that is a settled call — do not re-litigate it.**

⛔ **Locating the data is not a result.** *"We found which samples in a public deposit carry this
disease"* is a data-availability note. The paper, if there is one, is what the data then says.

**What is already published and cannot be claimed:** Koelsche et al. established that this disease
forms its own methylation class — that is what the classifier does, and their own class table reports
it at **n=10, 100% pure**. *"EMC has a distinct methylome"* is theirs.

**What is genuinely open:** a pan-sarcoma classifier paper establishes *that* classes separate; it
asks of no single class *what* is methylated. For this disease that is untouched. The specific hook
is **the NR4A3 locus itself** — the fusion drives the gene's 3' half from a partner promoter, so the
gene's own promoter is bypassed, and whether it is also epigenetically silenced is a mechanistic,
pre-registerable question. ⭐ **Its value is CROSS-MODALITY corroboration, not a second look at the
same data:** §5.3–5.4's arm-1 work measures 5' depletion from RNA, and methylation would say
independently whether that quiet 5' end is quiet *because it is switched off*. Two instruments, one
claim — which is the only thing that answers the complaint this memo opens with.

⛔ **And the bars, one of which nearly sinks it.** **n=12**, which no analysis fixes. **Ten of the
twelve are the classifier's own training set**, so anything about what *defines* the class is
circular by construction; the locus question escapes that only because the classifier clusters
genome-wide and never singles out that locus, and that escape is an argument a reviewer will probe.
Two array platforms across 12 samples forces the analysis onto shared probes. FFPE material is
noisier. The ~1,490 other sarcomas as a comparison group is the one thing here that is better than
typical.

**THE DECISION (trimcrae, 2026-08-24): not a priority paper. Documented and stopped here.** What
that does and does not mean:

- ⛔ It is **not** a finding that the route is dead, and it is **not** a negative result. Nothing was
  run. The cohort is real, open and still there.
- ✅ It **is** a ranking call against the rest of the board, made with the paper shape and its bars on
  the table rather than in the abstract.
- ⚠ **A broad *"methylation landscape of EMC"* paper is refused on the merits, separately from the
  ranking** — 12 samples on mixed platforms cannot carry it, and it would collapse into the
  circularity above. That refusal stands even if the route is later re-prioritised.
- **What would change the ranking:** more EMC methylation cases from any source, matched normals, or
  the arm-1 5'-depletion result landing in a state where an independent epigenetic read would settle
  something it otherwise cannot.

⚠ **One downstream record was wrong because of this and has been corrected:** `MOD-DNMT` in the
modality census was parked on the claim that *no methylation dataset for this disease is available to
this program in any form*. That premise is now false. ⛔ **The route stays parked anyway** — the
cohort is tumour-only, carries no drug response, and cannot say whether hypomethylating agents do
anything in this disease. **What changed is the premise, not the grade.** `BLK-NO-EMC-DATA` is
untouched: it is about functional-genomics data (one DepMap line, no CRISPR), and a methylation
reference set is not a dependency screen.

## 6 · Limits of this memo

- **§4's grade is a judgement about fit, not a measured result.** That the coarse-grained condensate
  models are well regarded, that they are obtainable and OpenMM-based, and that this repository has
  never used them are all measured; that they would produce a *discriminating* answer across the three
  fusion partners is a **hypothesis**, and the honest first step is a scoping pass that states, before
  anything runs, what the read would have to show to be worth reporting — and what result would make it
  a negative rather than an inconclusive.
- ✅ **Route A2's EMC sample count is no longer unmeasured — §5.5 answers it** (12 cases, 10 reference
  + 2 validation, 24 IDATs, joined on an identifier both the deposit and the paper declare). ⚠ What
  remains unmeasured is what such a cohort could *answer*; that is a scoping question, not a count.
- **Nothing here reorders the plan.** The roadmap owns the ordering and the spend ladder. This memo adds
  an axis — *where would a new fact come from* — that no register on the board carries.
- ⚠ **And it does not claim these are the only three.** They are the ones that survived asking, of every
  route on the board, the single question in the title: **would this produce a new true statement about
  EMC, or another one about us?**
