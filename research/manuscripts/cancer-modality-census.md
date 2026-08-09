---
id: DOC-MODALITY-CENSUS
title: What oncology can do, and what reaches extraskeletal myxoid chondrosarcoma — a modality census
level: L3
kind: manuscript
status: live
canonical_for: ["the 2026-08-09 modality census and its triage", "the census-versus-search distinction"]
purpose: >
  Answer one question asked on 2026-08-09: the portfolio reasons about a handful of treatment
  categories, so how large is the space it was chosen from, and which parts of it have never been
  looked at? Enumerate every category of cancer treatment, grade each against this disease, and name
  the residue.
scope: >
  L3. This document explains and ranks; it does not own the census rows, which live in
  systems/graph/modalities.json and render to systems/views/modality-census.md. It grades MODALITY
  CLASSES and never targets. It re-grades no existing route, and it restates the reasoning of no prior
  ruling — where a class was already settled, the row points at the document that settled it.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-09
last_verified: 2026-08-09
related: [DOC-TAX-MODALITY, DOC-EMC-UNEXPLORED-LANES, DOC-ARCHITECTURE]
---

# What oncology can do, and what reaches EMC

> **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness — for any class,
> in any verdict, including the ones that survive.** Every candidate below is a hypothesis with a named
> cheapest next observation, and several will not survive that observation.

---

## 1 · Why this is not another search

Three sweeps ran before this one. Each was a **search**: it issued queries and reported what came back.
A search's silence is ambiguous in a way that matters — a class absent from its output may have been
considered and dismissed, or may never have been pointed at, and those two situations call for opposite
responses. No prior document here could tell them apart.

The 2026-08-07 sweep measured what that ambiguity had cost, from the inside. Four whole categories had
been invisible to every previous search, and its diagnosis was not oversight but **instrument shape**:
the portfolio's searches had all been molecular-modality-centric, so physical and locoregional
treatment, the matrix as an address rather than an obstacle, non-cancer diseases sharing the phenotype,
and treatment strategy as distinct from new agents were each outside the shape of every query anyone
had written.

A **census** enumerates the space first and grades second. Its product is a denominator, and a
denominator is what turns *"nobody has looked at this"* from a recollection into a field that a checker
can verify. That is the whole methodological claim of this document, and it is a modest one.

⚠ **This is not a claim to have enumerated oncology.** It claims that the enumeration is explicit, that
every prior ruling is accounted for, and that the residue is named. Rows are certainly missing; the
register is built so adding one is an edit rather than a re-derivation.

## 2 · What the enumeration returned

**215 modality classes across 19 groups and 4 bands.** The full register, with every row's verdict and
pointer, is [`systems/views/modality-census.md`](../../systems/views/modality-census.md).

| verdict | classes | of which never searched here |
|---|---:|---:|
| ✓ `on_board` — a route already covers it | 41 | 0 |
| ● `in_clinical_use` — the incumbent arsenal | 8 | 0 |
| ✕ `already_rejected` — a prior document settled it | 31 | 0 |
| ✕ `excluded` — this census closes it | 84 | 84 |
| ⭑ `candidate` | 31 | 23 |
| ⏸ `parked_capability` | 9 | 9 |
| — `not_applicable` | 11 | 11 |

**⭑ 127 of 215 classes had never been pointed at by any prior sweep here, and 32 of those are live.**

Two readings of that number are wrong and worth heading off. It is **not** a claim that 127 opportunities
were missed — 84 of them are closed by this census on first inspection, which is what a denominator is
for. And it is **not** a criticism of the prior sweeps, which found things a census would not have: a
search goes deep where it points, and this went wide everywhere. The complaint is only that width had
never been measured.

The band breakdown behaves exactly as the 2026-08-07 diagnosis predicts, which is the closest thing
here to a validation of the method:

| band | classes | never searched | share |
|---|---:|---:|---:|
| `drug_mechanism` | 161 | 94 | 58 % |
| `delivery_and_conjugate` | 26 | 18 | 69 % |
| `physical_locoregional` | 15 | 8 | 53 % |
| `strategy_and_architecture` | 13 | 7 | 54 % |

⚠ **And the incumbent arsenal is 8 classes.** That is the answer to the framing that produced this work
— *"a pretty small arsenal"* — stated as a count rather than an impression: multi-kinase antiangiogenic
inhibitors, anthracyclines, alkylators, a minor-groove binder, a KIT inhibitor used once under a
biomarker restriction, interferon in case reports, radiotherapy, and surgery. Of those, one class carries
the disease's only meaningful systemic response record.

## 3 · The live residue

Thirty-one classes survive. They group into seven themes, and every one of them is registered as a route
so that it inherits blockers, names an endpoint and can be argued with.

### 3.1 · Transcriptional and proteostatic dependency

The largest single gap the census found, and it is in the place it should least have been.

**Transcriptional CDK inhibition.** The driver is a transcriptional oncoprotein whose entire mechanism is
transactivation, and transcriptional CDK dependency is the best-established vulnerability of
fusion-driven sarcomas as a class. No route, no prior sweep and no technique-class table here has ever
named it. ⚠ The class is broadly cytotoxic, so what is being asked about is a window rather than an
effect.

**Chaperone dependency.** A chimeric protein is a folding problem — two domains that never evolved to sit
together — and chaperone dependence is the general consequence. That is a way to lower fusion protein
levels needing no pocket ligand, no assembled ternary complex and no paralogue discrimination, which are
the three blockers holding the portfolio's largest family down. ⚠ The class has a long record of clinical
failure on toxicity, and any assessment has to lead with it.

### 3.2 · Biomarker-selected classes, readable from data already on disk

Six classes are selected by a molecular state rather than by a growth rate, and in every case the
selecting feature is readable in expression data this repository already holds. That makes the whole
theme unusually cheap: these are lookups, not experiments.

| class | what selects it | why it was never asked |
|---|---|---|
| PRMT5 / MAT2A | co-deletion of a metabolic locus | the copy state has never been read in this disease |
| arginine deprivation | silencing of one biosynthetic enzyme | the class reads as "metabolic", and metabolic classes were dismissed as a group |
| MDM2 antagonism | wild-type p53 and a quiet genome | the profile is unusual enough that the class rarely finds it |
| MCL-1 / BCL-xL | which anti-apoptotic protein a model depends on | the result implying it was already held and never followed |
| EZH2 / PRC2 | a chromatin-remodeller defect | a neighbouring chromatin hypothesis exists and was never connected to it |
| POLθ | a replication-repair state | the class-inheritance argument was built and never extended |

⭐ **The MCL-1 row is the sharpest of these because the evidence is already in the building.** BCL-2
inhibition was inactive as monotherapy and active only in combination in patient-derived models of this
disease. That pattern is the signature of dependence on a different member of the same family, and
nobody has asked which one.

⚠ **A shared caveat these six inherit together.** Expression is a surrogate for most of what selects
them — a transcript floor is not a copy-number call, and abundance is not activity. Each answer will be a
triage, and the honest output of the theme is which classes are *excluded* by the lookup rather than
which ones survive it.

### 3.3 · Kinase leads with EMC-specific evidence that nobody followed

Four classes where an observation in this disease already exists and has simply been left. Three were
surfaced by the 2026-08-07 sweep as lanes and never became routes; registering them is the follow-on that
sweep itself named.

- **RET** — the only kinase reported as both expressed and activated in this disease, from independent
  groups, with selective inhibitors approved elsewhere, unfollowed for over a decade.
- **SGK1** — positive across a full small series of tumours with an internal negative control, published
  two decades ago, never followed by anyone.
- **DNA-PK** — curated interaction evidence on the driver protein itself, and it needs neither a pocket
  ligand nor a ternary complex.
- **ALK / ROS1** — an inhibitor of this class was among the low-IC50 hits of a drug screen run on a
  patient-derived line of this disease. ⚠ The hit does not establish which target produced it, because
  that agent inhibits several kinases, and the first step separates the observation from the hypothesis.

### 3.4 · The matrix as an address

The myxoid matrix is this disease's defining phenotype, and the portfolio's prose has treated it almost
entirely as an obstacle to delivery. Four classes take it as the target instead.

Two of them route around a limitation this repository has already flagged in its own instrument: the
surfaceome screen ranks tumour-cell monoculture transcripts, so it cannot see glycans and has no stromal
compartment in it at all. Its conclusion that no selective surface antigen exists is therefore a statement
about classic protein antigens and is narrower than it reads.

⭐ **One of the four is a question nobody appears to have asked in this disease at all.** The matrix has
been considered as a barrier, and once as an address. The third option is to stop the tumour building
it — the gel is a manufactured product with a named biosynthetic pathway. ⚠ That pathway is shared with
normal chondrogenesis, so selectivity is the open question rather than an assumption, and the relevant
expression read is **already committed here** and has never been graded for this purpose.

### 3.5 · Locoregional and radiation

The portfolio contains no physical intervention of any kind. That is the cleanest instance of the
instrument-shape problem, and it matters here more than it would in most diseases, because this one is
indolent, extremity-primary and lung-metastasis-dominant — the exact profile regional and local therapy
was developed for.

- **Isolated limb perfusion**, with an approved agent and an established role in unresectable extremity
  sarcoma, against a disease whose most common primary site is deep soft tissue of the thigh and lower
  limb.
- **Lung-directed local therapy** — regional perfusion, inhaled delivery, percutaneous ablation — against
  a metastatic pattern the curated record describes as mostly lung, in a disease where removing isolated
  metastases is already documented to give long disease-free intervals.
- **Radiotherapy intensification** — particle therapy, brachytherapy, radiosensitisation, regional
  hyperthermia. This one attaches to a contradiction already live in this repository's record, where two
  registries and the largest series disagree about whether radiotherapy does anything. No prior sweep
  considered that the answer might be dose *quality* rather than dose.

⚠ **One negative generalises across this whole theme and is carried rather than rediscovered.** Boron
neutron capture was declined on boron atoms per unit volume in a matrix-dominated tumour. That
cells-per-volume correction applies to every modality dosed per volume but delivered per cell, and it now
carries to the Auger-emitter and radioimmunoconjugate rows as well.

### 3.6 · Strategy and reachability

Not new agents — changes to what a patient receives. Scheduling (adaptive and metronomic), sequencing,
and the two reachability routes: eligibility defined by fusion family rather than histology, and the
access pathways by which a published hypothesis becomes a treated patient.

⭐ **The last of those closes a gap in the portfolio's own logic.** Every route here names publication as
its endpoint, on the correct reasoning that with no wet lab and no clinic the published record is the only
channel to a patient. But the mechanism by which a paper becomes a treatment — single-patient access,
off-label use, an outcome registry that captures the result — had never been registered as a route. The
portfolio had an endpoint and no next step after it.

### 3.7 · Nuclear receptors outside NR4A3

Two lanes from the 2026-08-07 sweep, neither of which became a route. A hormone-responsive 5′ partner can
import a druggable transcriptional input the driver does not otherwise have, and there is a reported
instance of exactly that with durable benefit. Separately, an orphan nuclear receptor implicated in
dormancy has a published tool compound — which is the known-answer control the program's own receptor
never had, and the reason this lane is worth more than its biology alone suggests.

### 3.8 · The first grading pass, and what it cost

Six of the routes registered above turned out not to need their cheapest observation **run** at all.
The genes were already read and committed in the repository's targeted expression panel, and nobody
had graded them against these routes because the routes did not exist when the panel was built. That
is the census doing the one thing a census is for: the reading was on disk, and only the denominator
made anyone go and look at it.

Verdicts, which live in
[`census-route-expression-grading.json`](../modalities/census-route-expression-grading.json) and are
not restated here:

| route | verdict |
|---|---|
| hypoxia-activated prodrugs | **supported** — and the only one supported concordantly on both platforms |
| arginine deprivation | **against** — the selecting biomarker is not low in this disease on either platform |
| matrix biosynthesis | **against as stated** — the sulfate-donor module is lower, not higher, than in comparator sarcomas |
| RET | **split** — the receptor holds; the module that switches it on is depleted on both platforms |
| matrix-targeted immunocytokines | **present, not selective** — and the isoform that decides it is unreadable here |
| orphan-receptor dormancy | **unread** — no probe maps to the receptor on either platform |

⭐ **Two of these are worth more than a positive would have been.** The RET result qualifies the lane
this census and the 2026-08-07 sweep both ranked highest: canonical signalling through that receptor
needs a ligand and a co-receptor, and relative to comparator sarcomas this disease has less of both.
That does not close the lane — ligand-independent activation exists, and bulk tumour transcript cannot
exclude a paracrine supply — but it moves the claim the lane may make from *activated* to *expressed*,
which is a different and much weaker sentence than the one it was registered on.

⚠ **And one returned nothing, which is recorded as nothing.** The dormancy receptor has no probe on
either platform. An unreadable gene is not an absent gene, and the pass reports it as unread rather
than letting a missing probe become a negative — the failure mode the source artifact's own governing
rule exists to prevent.

⚠ **Five of the six biomarker-selected classes in §3.2 are NOT in this pass**, because their selecting
genes are not among the 243 the panel currently reads. Extending it is a free CI job and is the
immediate next step; until it runs, those five rows are unexamined rather than open.

## 4 · What the census closes, and why that is the larger half

Eighty-four classes are closed here on first inspection, and that is the census working rather than the
census failing. Most fall into four recurring shapes, and naming the shapes is more useful than listing
the rows:

1. **Proliferation-coupled classes** — mitotic kinases, antimetabolites, dietary restriction, most
   cytotoxics. Their effect scales with division rate, and this tumour is slow-cycling with an indolent
   course. This is the same ground on which a physical modality was already declined here.
2. **Classes gated on an antigen** — allogeneic and NK cell therapy, trispecifics, masked antibodies,
   alternative scaffolds, radioimmunoconjugates, peptide conjugates. Each changes format, effector,
   payload or safety margin, and none supplies an address. The gate is upstream of all of them.
3. **Classes gated on an existing immune response** — checkpoint combinations, costimulatory agonists,
   adenosine and IDO blockade, regulatory T-cell depletion, innate agonists. ⚠ The innate agonists needed
   a specific reason rather than the general one, since they are explicitly built for cold tumours: they
   supply priming, not antigens, and a genome this quiet is short of antigens.
4. **Classes selecting on a lesion this genome does not have** — MAPK, PI3K, FGFR, HER2, CDK4/6, WRN,
   RAS. A quiet clonal genome with a single founding translocation is a poor place to look for a second
   driver.

⭐ **Three closures are worth more than the rest, because they are new classes killed by facts the
repository already owned.** Splice-switching antisense, response-element decoy oligonucleotides and
oligonucleotide-directed degradation all look like clean fits for a DNA-binding fusion driver, and all
three fail on rulings already on the books — the splice acceptor at the junction is not fusion-unique, and
the paralogues' DNA-binding domains are near-identical. None had been named here before; each is now a
closed row with its argument attached.

## 5 · Reconciliation with the three prior searches

Every ruling made by a prior sweep is accounted for by a row that **points at it and does not restate its
reasoning**. That is a deliberate constraint rather than brevity: a second home for an argument is an
argument that drifts, and this repository has measured that failure enough times to build checkers
against it.

Thirty-one rows carry `already_rejected` with a resolvable pointer into the owning document. The pointer
is checked by the same machinery that checks every other pointer in the model, and a test asserts that
each of the three prior searches is reached by at least one row — so a ruling cannot fall out of the
record silently and reappear later as a fresh idea.

⚠ **The reconciliation test is deliberately weak and says so.** It asserts that each prior document is
reached, not that every row inside it was individually mapped. The strong form of that guarantee is the
per-row `prior_coverage` field, which is schema-enforced and requires a resolvable document before a class
may be called previously searched.

## 6 · Limits

- **A census is only as good as its taxonomy.** Nineteen groups is a choice, and a class that falls
  between two of them is a class that can be missed. The bands were chosen to make the previously
  invisible categories visible, which fixes the failure that was measured and not the general problem.
- **Most verdicts are judgements, not measurements.** The `excluded` rows in particular rest on a
  mechanism-versus-biology argument, and a mechanism argument is exactly the kind that a single
  measurement can overturn. They are recorded so they can be argued with, which is the most a document
  like this can offer.
- **`never_searched` is a statement about this repository, not about the field.** It says no sweep here
  pointed at a class. Others may have looked at it in this disease, and where they have, the honest next
  step is to find that work rather than to treat the class as unexamined.
- **The candidate list is not ranked against the existing board.** Registering these as routes puts them
  on the same axes as the other routes, which is where ranking belongs. Nothing here claims a new
  candidate outranks an existing one.
- **Nothing here has been tested.** Every candidate carries a cheapest next observation precisely because
  none of them has had one yet.
