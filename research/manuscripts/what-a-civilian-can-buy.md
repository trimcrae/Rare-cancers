---
id: DOC-WHAT-A-CIVILIAN-CAN-BUY
title: What a civilian can buy — the third tier, scoped and closed
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: a scoping memo written to one question, and it returns a NEGATIVE answer
scope: As stated in the document's own role banner.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# What a civilian can buy — the third tier, scoped and closed

> **Role: a scoping memo written to one question, and it returns a NEGATIVE answer.** *"What experiments
> can a private individual with a credit card actually cause to happen — mail-order products and
> contracted services — with no lab and no institutional affiliation?"*
>
> **Why it was asked.** Every route memo in this repo grades routes partly on **"the wet-lab ask"**, and
> that axis silently assumes a collaborator with a bench who will run it. trimcrae is a private
> individual: no lab, no institutional affiliation, no committed collaborator. So the repo has been
> ranking routes on an axis that describes a *hope* rather than a *capability*. This memo asks whether
> there is a third tier underneath — things a credit card can buy outright — and scopes it honestly.
>
> **Subordinate to [`nr4a3-program-map.md`](./nr4a3-program-map.md)** (the roadmap owns the plan, the
> gates and every programme figure — nothing here restates one, everything points at it), and to
> [`emc-treatment-strategy.md`](./emc-treatment-strategy.md) + [`../IDEAS.md`](../IDEAS.md) (the route
> portfolio). Where any of them conflicts with this memo, **they win.**
>
> **$0.** Research and writing only. **Nothing was purchased, no vendor was contacted, nothing was
> signed up for, no lab and no person was approached.** Vendor pages were fetched read-only from a CI
> runner into [`lit-targets-civilian-purchasing.json`](./lit-targets-civilian-purchasing.json) +
> [`-b.json`](./lit-targets-civilian-purchasing-b.json) → the `literature-cache` branch, and every
> eligibility and price claim below is quoted from the vendor's own public page.
>
> **No efficacy, safety, therapeutic-window or clinical-readiness claim is made or implied for any
> molecule, route or experiment named here.**

---

## 0 · THE VERDICT, STATED FIRST

⛔ **There is no buyable tier. For every open scientific question in this programme, the answer is
either IN-SILICO (we do it ourselves for $0) or NEEDS-A-LAB-WE-DO-NOT-HAVE. The middle tier is
empty.**

That is the whole finding, and it is a useful one rather than a disappointing one: it means the
repo's standing two-lever strategy — **publish-to-convince** and **in-silico evaluation** — is not a
limitation anyone has failed to notice a way around. It is the correct strategy, and this memo is
the audit that says so. **It should stop the third tier being re-proposed every few months.**

⭑ **The one genuinely new fact, and it does not rescue the tier — it relocates the blocker.** A
**catalogue recombinant human NR4A3 ligand-binding domain exists and can be bought off the shelf**
(Cayman Chemical item 40344; §4.2). Nobody in this repo knew that. So the thing standing between us
and `R4` is **not protein supply**, which is what a future session would naturally have assumed and
spent effort attacking. It is the assay, and the assay problem is not a money problem — **it is that
the experiment `R4` names cannot be bought in a form that answers `R4`** (§2).

### The three filters every candidate had to pass

Applied per trimcrae, 2026-08-03 — *"If it's multiple thousands of dollars for an in home wet lab
test I could mess up I'm gonna rule that out anyway."*

| # | filter | what it rules out |
|---|---|---|
| **F1 · COST** | hundreds of dollars. **~$1,000 soft ceiling**; four figures is effectively ruled out unless decisive alone | every contracted assay found |
| **F2 · NO HANDS-ON EXECUTION** | trimcrae does no bench work. A fully contracted service where he ships nothing and does nothing is acceptable; **a "kit you run yourself" is not** | every DIY/community-lab route, every home kit |
| **F3 · INTERPRETABLE ON FAILURE** | a negative must MEAN something. If a plausible technical failure yields an uninterpretable null, the money is simply gone | `R4` in every purchasable configuration |

⚠ **A fourth barrier emerged that was not in the brief and applies to the whole tier: the assay
services are QUOTE-ONLY.** Not one biophysics or screening CRO examined publishes a price (§4.4). So
their cost cannot be established *without contacting a vendor* — which is both outside this memo's
constraints and, more importantly, means **a spend in this tier cannot be checked against F1 in
advance at all.** An unpriceable purchase is not a cheap purchase; it is an unbounded one.

---

## 1 · The headline question — is `R4` buyable?

**`R4` is the roadmap's requirement *"Something binds that pocket"*, scoped to the opened cryptic
Pocket-5, and it is registered there as the programme's one requirement that **no in-silico
instrument can serve** and as its **cheapest decisive experiment**
([roadmap §2.1 / §2.2 / §5 row R4](./nr4a3-program-map.md#5--where-each-requirement-stands) own all
of that).**

### ⛔ VERDICT: `R4` IS NOT BUYABLE — on three independent grounds, any one of which is sufficient

| # | ground | status |
|---|---|---|
| **A** | **The named instrument does not exist as a purchasable product.** `R4` asks for a binding screen ***against the opened site***. No purchasable binding assay can be pointed at a *site* | ⛔ decisive, and it is a category error rather than a budget problem |
| **B** | **F1 — cost.** Even the cheapest configuration exceeds the ceiling on the protein alone, before any assay is priced | ⛔ fails |
| **C** | **F3 — interpretability.** A negative has at least five indistinguishable causes, and the *positive* is already known not to settle `R4` — by published precedent on this exact protein | ⛔ fails |

### 1.1 · First, the defeater I was handed — and it is REFUTED by our own evidence

**The defeater as posed:** *the NR4A3 pocket is cryptic, opened only under dynamics in this repo's
metadynamics work, so a purchased LBD would not present the site at all, and a binding screen would
be testing a closed pocket and returning an uninterpretable negative.*

⭑ **That specific argument does not hold, and the observation that settles it was already on disk
and free.** Per CLAUDE.md §4 — a $0 observation is never "watching" — here it is:

- **The site is present in an experimental, ligand-free, solution-state ensemble of the isolated LBD
  — the very object a vendor ships, in the very state an assay would present it.** PDB **8XTT** is
  an apo NR4A3 LBD solution-NMR ensemble, and under the repo's harmonized detector the orthosteric
  pocket is *matched in 19 of the 20 deposited conformers*, three of them scoring at or above the
  druggability threshold ([roadmap §5 row R1](./nr4a3-program-map.md#5--where-each-requirement-stands)
  owns those counts and the threshold `C1`). **No MD, no bias, no metadynamics.**
- **An orthogonal, unbiased, learned ensemble agrees.** BioEmu, generating from sequence alone,
  re-finds and opens the same site at a minority population closely matching the NMR ensemble's —
  the paper's §2.1 owns both fractions and states plainly that the two *unbiased* sources concur
  against the biased metadynamics majority.
- **And the roadmap has already retired the two-state framing the defeater depends on.** Pre-registered
  **Gate 1 — a genuine two-state cryptic *opening* — FAILED as registered and was reformulated to
  basin-internal breathing** ([roadmap §5 row R1](./nr4a3-program-map.md#5--where-each-requirement-stands)).
  Basin-internal breathing is the *opposite* of "only opens under dynamics": the cavity is a feature
  of the native basin, not a separately-activated state that simulation had to manufacture.

⇒ **A purchased LBD would, on the repo's own best evidence, present the site at some minority
population.** The defeater as posed is not the reason `R4` is un-buyable, and recording that matters,
because a future session that believed it would draw the *wrong* strategic conclusion — that better
sampling or a cleverer construct would unlock a cheap experiment.

⚠ **Stated at its true weight, because two caveats are load-bearing and cut the other way.**
**(i)** The 8XTT conformers are the lowest-energy models of a calculation, **not population-weighted
equilibrium samples**, and the paper says explicitly that the count is a structural-heterogeneity
observation and *not* an open-state population estimate. **(ii)** `R2` (is the state accessible at
equilibrium) is unresolved and `R6` (the opening penalty, ΔG_open) has **never been computed for any
paralogue** ([roadmap §5](./nr4a3-program-map.md#5--where-each-requirement-stands)). So we do not know
the population and cannot compute the conformational-selection penalty a ligand would pay. **The
honest statement is "present as a minority sub-state of unknown weight", not "available".**

### 1.2 · ⭑ The REAL defeater, which nobody has written down

**It is about the assay, not the protein — and it is stronger than the one I was handed, because no
amount of money or protein quality fixes it.**

Re-read what `R4` actually asks for. The roadmap scopes it to *"the opened cryptic Pocket-5"* and
says in terms that **the scoping word is load-bearing**; its named instrument is *"a thermal shift /
SPR / NMR fragment screen **against the opened site**."*

⛔ **You cannot buy an assay "against a site." Every affordable binding assay reports a binding
EVENT on a PROTEIN. None of them reports WHERE.** DSF/thermal shift reports a global unfolding
temperature. SPR, BLI, MST and ITC report an interaction with the immobilised or titrated molecule
as a whole. Native/intact mass spectrometry reports a mass adduct. **Site resolution is a
*structural* experiment**, not a binding one — protein-observed 2D NMR chemical-shift-perturbation
mapping, a co-crystal, or cryo-EM — and it is an order of magnitude more expensive in both protein
and money.

⭑ **And the cheap workaround is closed by the definition of the question.** SARomics Biostructures,
describing its own fragment-screening service, states the two options verbatim: *"In 2D experiments,
the protein must generally be labeled with 15N (or 2H for large proteins)"* — the expensive route —
and, for locating a site cheaply, *"we can identify potential binding sites by competition
experiments with a known binder."*
([saromics.com](https://www.saromics.com/fragment-screening-drug-discovery-services/), fetched.)
**For NR4A3's cryptic Pocket-5 there is no known binder — that is precisely and entirely what `R4`
asks.** The cheap site-localisation method requires the answer to the question it would be used to
answer. **Circular by construction.**

⚠ The same circularity closes the standard cheap nuclear-receptor format. **Fluorescence-polarisation
or TR-FRET tracer-displacement assays — the routine, plate-scale, genuinely inexpensive way to screen
a nuclear receptor — require a labelled reference ligand of known affinity.** NR4A3's cryptic pocket
has none. The assays that are cheap are cheap *because* they presuppose a characterised ligand.

### 1.3 · ⭑ The experiment has already been bought once — and it did not answer `R4`

**This is the single most decisive piece of evidence in the memo, and it is a published fact about
this exact protein.**

Zaienne et al. 2022 ran the field's one NR4A3 ligand-discovery campaign
([ChemMedChem 17(16):e202200259, PMC9542104](https://pmc.ncbi.nlm.nih.gov/articles/PMC9542104/) —
fetched and quoted, not summarised). Two things about it are decisive here, and **only one of them is
already in this repo**:

1. **Already known here:** it succeeded. A fragment library screen, hit rate <1 %, returned three
   NOR-1 ligand chemotypes, one elaborated to a low-micromolar inverse agonist that shifted
   NOR-1-regulated gene expression in cells — and the repo's own reading is that these results
   *"leave the binding site **structurally undefined**"*
   ([paper §1](./nr4a3-degrader-paper.md); [roadmap §5 row R4](./nr4a3-program-map.md#5--where-each-requirement-stands)).
2. ⭑ **NEW, and it sharpens the point considerably: that screen used no purified protein and made no
   biophysical binding measurement at all.** In the authors' own words: *"we have established a
   robust reporter gene assay to monitor NOR‐1 activity and screened a medium size fragment library
   for NOR‐1 modulation. The screening assay was based on the Gal4 hybrid system"* — firefly
   luciferase under five tandem Gal4 response elements, renilla for normalisation, with a Gal4-VP16
   control for non-specific effects. It measured **transcriptional activity in cells**, not binding.
   Binding sites were inferred only indirectly, by competition, and the conclusion was that two of
   the hits occupy *"different binding sites"* — unassigned.

⇒ **Two consequences, both bad for a purchased `R4`.**
**(a)** A clear POSITIVE, with SAR, on this protein already failed to settle `R4`. If a positive does
not settle it, a negative certainly cannot. **(b)** There is **no published precedent for a
purified-protein biophysical assay on NR4A3 at all** — the field's one campaign routed around
purified protein. That is not proof that such an assay is hard, but it is the opposite of the worked
precedent a $1,000 purchase would need to copy.

### 1.4 · ⭑ And the catalogue protein is not the object this repo modelled

**Measured, not assumed — from the vendor's own specification.** The catalogue LBD (§4.2) is
**amino acids 398–626** of UniProt Q92570.

| construct | span | what it is |
|---|---|---|
| **catalogue protein (Cayman 40344)** | **398–626** (229 aa) | what a credit card buys |
| **experimental NMR ensemble, PDB 8XTT** | **379–626** (248 aa) | where *all* the experimental "the pocket is present in solution" evidence comes from |
| **this repo's modelled LBD** | **373–626** (254 aa) | the object every computation in the programme was run on |

*(8XTT's span is derived, not typed: the deposited construct is 248 residues and the paper registers
its numbering onto the UniProt frame by an **exact +378 offset** — [paper §2.1](./nr4a3-degrader-paper.md).)*

✅ **The good news:** Pocket-5's lining set and span — residues 406–534, owned by
[`pocket_tracking.POCKET5_LINING` / `POCKET5_SPAN`](../modalities/pocket_tracking.py) and frozen as
configuration item `C5` — sit **entirely inside 398–626, with 8 residues of N-terminal margin.** The
catalogue construct does contain the cryptic site.

⛔ **The bad news, and it is exactly F3's failure mode made concrete:** the catalogue protein is
**19 residues shorter than the experimental structure and 25 shorter than the modelled one, all at
the N-terminus** — the region that in a nuclear-receptor LBD carries helix H1 and the H1–H3 loop,
which pack against the ligand pocket. **Nothing in this repo has ever evaluated a 398–626 ensemble.**
So a negative on the catalogue protein would be unattributable between *"nothing binds the cryptic
pocket"* and *"this is a 25-residue-truncated construct whose ensemble at Pocket-5 we have never
characterised."* ⚠ This is a **named, unmeasured risk**, not a finding: no one has shown the
truncation matters. But under F3 an unmeasured construct difference sitting directly on the
question's critical path is a reason not to spend, not a detail.

### 1.5 · The cost arithmetic — `R4` fails F1 on the protein alone

**Basis, stated so it can be checked and corrected.** The protein price is **measured** (a vendor's
published list price, §4.2). The protein *requirement* is an **ESTIMATE** from standard assay
practice, and is labelled as one throughout — it is not a measured quantity and nothing in this repo
measures it.

- Catalogue LBD: **734.00 € per 100 µg** (Biomol list price for Cayman 40344, fetched).
- Estimated DSF consumption, **stated as an estimate**: a 27.74 kDa protein at a routine
  1–10 µM in a 20 µL well is on the order of **1–6 µg per well**; a plate is therefore on the order
  of **0.1–0.6 mg**, and a 480-fragment screen with replicates on the order of **2–3 mg**.
- ⇒ A screen at the scale of the one published campaign is on the order of **20–30 catalogue packs,
  i.e. roughly €15,000–22,000 of protein** — before any assay is priced at all.
- ⇒ Even the **absolute floor** — one 100 µg pack, ~15–35 wells, a dozen-odd compounds, no
  replicates — is **€734 of protein**, which consumes the entire F1 ceiling *before* a CRO fee that
  no vendor will publish.

⛔ **And that floor configuration is the worst possible science.** A dozen compounds, chosen from
poses that the roadmap records as **one method's top pose with a second, independent method
disagreeing** ([roadmap §5 row R5](./nr4a3-program-map.md#5--where-each-requirement-stands)), against
a sub-state of unknown population, on an uncharacterised truncated construct, read out by an assay
that reports global unfolding and cannot say where anything bound. **A null there carries no
information whatsoever.** Spending the ceiling to buy a guaranteed-uninterpretable result is the
precise combination F3 exists to refuse.

### 1.6 · What this means for the roadmap's `R4` row

The roadmap calls `R4` the *"cheapest decisive experiment in the program"*, and **that is true and
should stay** — it is cheapest *relative to the other fifteen requirements*, all of which need
ternaries, paralogue panels or fusion-context ensembles. But "cheapest in the programme" has been
read as "nearly buyable", and it is not. The correction this memo contributes is one sentence:

⛔ ***`R4`'s stated instrument — a binding screen "against the opened site" — does not exist as a
purchasable product, because site resolution is a structural experiment and every affordable binding
assay reports an event rather than a location. `R4` needs a collaborator with a structural-biology
capability, not a credit card.***

---

## 2 · The three-way classification of the repo's open questions

**(a) IN-SILICO** — we settle it ourselves for $0 · **(b) BUYABLE** — a private individual can
purchase the thing that settles it, passing F1+F2+F3 · **(c) NEEDS A LAB WE DO NOT HAVE** — a
publish-to-convince hope, not a plan.

⚠ **A fourth category was needed and is marked (c\*).** Two items need **a clinician and a patient**,
which is neither a lab we lack nor a purchase — the distinction matters because "find a collaborator"
is the wrong action for them.

### 2.1 · From [`emc-post-degrader-options.md`](./emc-post-degrader-options.md)

| open question | tier | why |
|---|---|---|
| Route 6 — EMC PPARG-axis expression: is the receptor active or poised? (agonism vs redundancy) | **(a)** | public expression data + machinery that already exists. **$0, and it is on the memo's own next-two-weeks list** |
| Route 4 — is a productive TCIP bivalent geometrically possible (linker enumeration, no E3 arm)? | **(a)** | free CPU; a strictly smaller geometric problem than the one already enumerated |
| Route 3 — the methods paper about the four failures and their controls | **(a)** | $0; the negative results *are* the result |
| Route 2 — RNase-H1 cleavage-discrimination MD | **(a)** | GPU, on the ladder; ours to run |
| Route 1 — does any NR4A3 fusion show DSB recruitment / impaired ATM signalling? | **(c)** | needs EMC cells + immunofluorescence/immunoblot. §4.1: the repository lines are institution-gated and the EMC-specific lines are academic-MTA-gated |
| Route 1 — ATRi dose–response + γH2AX + PARPi control + proliferation index on EMC lines | **(c)** | the compounds are buyable (§4.3); **the cells and the hands are not.** This is the memo's cheapest wet-lab ask and it is still (c) |
| Route 6 — trabectedin × PPARγ two-drug matrix on EMC lines | **(c)** | same gate: approved drugs, unavailable cells |
| Route 5 — covalent probe at C397 as a reagent, read by intact-mass | **(c)** | needs the probe *synthesised* (nothing in a catalogue), then purified protein + MS. Strictly harder than `R4` |
| Route 7 — does EMC express SSTR2? (⁶⁸Ga-DOTATATE PET) | **(c\*)** | an approved diagnostic scan **ordered by a physician for a patient**. Cheapest decisive test in the portfolio and **not purchasable by trimcrae in any form** |
| Route 2 — tumour delivery for a junction ASO | **(c)** | an engineering programme, not a purchase |
| Approaching a group that holds an EMC model | — | **outward-facing; trimcrae's call** (CLAUDE.md §3). Not a purchase and not blocked on one |

### 2.2 · From [`nr4a3-program-map.md`](./nr4a3-program-map.md) — the requirement register

| requirement | tier | why |
|---|---|---|
| `R2` state is equilibrium-accessible; `R6` ΔG_open per paralogue | **(a)** | compute. `R6` is already priced in the roadmap's OPTIONAL/HELD tier |
| `R5` pose is right — a third method, or a known-answer system in regime | **(a)** | the roadmap records the cheapest item that would move it as **$0 and a sourcing question** |
| `R8` linker geometry — reconcile to its artifact · `R9`/`R10` rebuild the ternary by the assembly route · `R11` selectivity · `R12` degradation geometry | **(a)** | all compute; several already priced on the ladder |
| `R13` fusion-context object · `R14` AR/MR scope bounding | **(a)** | the roadmap prices and gates both; `R14`'s instrument is mostly built |
| `R3` generation-frame submission gate | **(a)** | ✅ already built and run at $0 — and it **failed**, which is a result, not a gap |
| **`R4` does anything bind the opened cryptic pocket** | **(c)** | ⛔ **the headline. See §1 — not buyable on three independent grounds** |
| `R7` binder is paralogue-selective | **(a)** then **(c)** | the computational half is ours and parked on a named defect; the experimental test is a bench |
| `R15` candidate set is constructible | **(a)** | ✓ chemistry-verified in silico. ⚠ *Synthesising* one is (c) — not a catalogue purchase |
| `R16` NR4A3 is the right target (EMC dependence, dTAG) | **(c)** | delegated to the EMC programme; needs cells |
| `R1` a druggable pocket exists | **(a)** | ✓ work complete; the open gates are computational |

### 2.3 · The count

| tier | count | share |
|---|---|---|
| **(a) IN-SILICO — $0 or on the ladder** | **12** | the overwhelming majority |
| **(b) BUYABLE — passes F1 + F2 + F3** | **0** | ⛔ **empty** |
| **(c) NEEDS A LAB WE DO NOT HAVE** | **9** | (of which **1** is (c\*) — needs a clinician and a patient) |

*(21 tier-assignments over 20 classified rows in §2.1–§2.2: `R7` is counted once in each tier it spans,
and the outward-facing approach row is not a question. ⚠ **Superseded, retained: 13 / 0 / 8 with 2 (c\*)**
— typed from memory rather than counted off the tables, and corrected the same session by counting them.)*

⭑ **The buyable tier is empty. Not thin — empty.** Nothing in this repo's open-question set is
settled by any product or service a private individual can purchase inside the three filters.

---

## 3 · Why it is empty — the four structural reasons

Worth naming, because each would otherwise be re-discovered separately.

1. **We have no sample.** The two genuinely individual-accessible service classes — **sequencing** and
   **DNA/oligo synthesis** — both operate on material you send or a sequence you specify. Sequencing
   is cheap, fast and sold to individuals with a credit card (§4.5), and it settles nothing here
   because there is no EMC nucleic acid in this project's possession, and there is no route to one
   that does not begin with a patient or a lab.
2. **We have no assay to put a compound into.** Tool compounds are genuinely cheap and genuinely
   purchasable (§4.3). Possessing elimusertib or a fragment set advances nothing without cells or
   purified protein *and* an instrument *and* hands. **The compound was never the bottleneck.**
3. **Biological materials are institution-gated by policy, not by price** (§4.1). This is the barrier
   that no budget clears: the repositories' own published rules require an organisation.
4. **The one thing we could buy — protein — feeds an assay that cannot answer the question** (§1.2),
   and the services that would run it are unpriceable in advance (§4.4).

---

## 4 · What is actually purchasable — the supporting scoping

*Evidence, not the argument. Every row is quoted from the vendor's own public page, fetched read-only
on 2026-08-03 and committed to `literature-cache` under `literature/civilian-purchasing/`. Prices are
list prices as published on that date and will drift; they are cited to establish an order of
magnitude, not carried as programme figures.*

### 4.1 · Cell lines from repositories — ⛔ institution-gated, and this is explicit

| repository | eligibility for an unaffiliated individual | evidence |
|---|---|---|
| **DSMZ** (Leibniz Institute) | ⛔ **NO — explicitly excluded.** *"Only institutions and companies are eligible to order from the DSMZ."* And: *"If you are ordering bioresources from the DSMZ for the first time, **a validation of your institution is required**."* | [dsmz.de/customer-support/faq-order](https://www.dsmz.de/customer-support/faq-order) |
| **ATCC** | ⛔ **NO in practice.** The account application is organisation-based at every step (*"Enter details about your organization"*), needs a **Legal Signatory** — *"The person authorized to execute legally binding agreements on behalf of your organization"* — and the shipping step states: *"**Do not use a P.O. box or residential address, as this will prevent your account from being approved.**"* Additionally *"All new standard accounts default to Biosafety Level 0"*, and the delivery address's biosafety level must meet or exceed the product's | [atcc.org/support/order-support/applying-for-an-atcc-account](https://www.atcc.org/support/order-support/applying-for-an-atcc-account) |
| **JCRB** (holds **H-EMC-SS** — ⚠ the DepMap line *labelled* EMC, whose fusion status the curated record contradicts as of 2026-08-05, [Amendment 1](./emc-surface-target-landscape.md); *superseded, retained: "the one EMC line in DepMap"*) | ⛔ **NO.** Distribution is structured around **affiliation** — academic vs profit-making — and commercial users *"must conclude MTA with the institution"*, which JCRB *"cannot mediate"*. There is no unaffiliated-individual path | [cellbank.nibn.go.jp](https://cellbank.nibn.go.jp/english/flow_of_distribution_of_cells.html) |
| **ECACC / Culture Collections (UK)**, **RIKEN BRC** | ⛔ **UNCERTAIN, resolving to NO on the same structure.** Both operate the same institutional-account + MTA model. ⚠ Our fetches of the specific ordering-terms pages 404'd (URLs moved), so this row is **inference from the sibling repositories rather than a quoted rule** — it is recorded as UNCERTAIN and it changes nothing, because DSMZ/ATCC/JCRB already close the route | fetch manifest, `literature/civilian-purchasing/_manifest.json` |
| **The EMC lines that actually matter** — USZ20-EMC1, USZ22-EMC2, NCC-EMC1-C1 | ⛔ **NO.** These are **academic lines held by their originating groups**, not repository catalogue items. Obtaining one is an MTA between two institutions — i.e. **exactly the outreach step the memo already routes to trimcrae as an outward-facing decision**, not a purchase | [`emc-post-degrader-options.md`](./emc-post-degrader-options.md) route 1 |

⭑ **This is the load-bearing row of the whole memo.** Route 1 — the repo's current #1 near-term
candidate and *"the cheapest wet-lab ask on this board"* — has catalogue compounds and a
readout its source paper reports as reliable, and it is still **(c)**, because the cells are gated by policy. **No budget
changes that.** The unlock for route 1 is a collaborator, exactly as the memo already says.

### 4.2 · ⭑ Recombinant protein — the surprise: NR4A3's LBD is a catalogue item

| product | spec, as published | price |
|---|---|---|
| **NR4A3 Ligand-binding Domain (human, recombinant)** — Cayman Chemical **40344** | *"Recombinant human N-terminal His-tagged NR4A3 expressed in E. coli. **Amino Acids: 398-626.** MW: 27.74 kDa"*, **Purity: >80 %**, in 50 mM Tris·HCl pH 7.5 / 100 mM NaCl / 2 % glycerol; UniProt **Q92570** | **734.00 € / 100 µg** ([Biomol Cay40344-100](https://www.biomol.com/products/proteins-and-peptides/proteins/nr4a3-ligand-binding-domain-human-recombinant-cay40344-100)) |
| PPARα LBD (human, recombinant), Cayman 10009088 — *class comparator* | aa 170–430, E. coli, His-tagged | **791.00 € / 100 µg** |
| Full-length NR4A3 protein, OriGene **TP323629** — *wrong construct for Pocket-5* | HEK293-expressed, transcript variant 3 | **$737.00 / 20 µg** (sizes to 1 mg offered; 4-week lead) |

- ✅ **Available to an individual?** These are ordinary research-chemical catalogue items with no
  repository-style eligibility gate — materially easier than a cell line. ⚠ **UNCERTAIN in one
  respect that we deliberately did not resolve:** whether these vendors' account-opening and
  research-use-only terms accept a residential ship-to. Resolving it means opening an account, which
  is outside this memo's constraints. **It does not matter**, because §1 rules `R4` out on grounds
  that survive a "yes."
- **Custom expression as an alternative.** GenScript advertises bacterial expression *"Starts at
  $200/protein"* with *"Gene to protein from 1 week"*
  ([genscript.com](https://www.genscript.com/bacterial-protein-customized-service.html)). ⚠ Read that
  correctly: it is a **floor for the smallest screening-scale tier**, not the price of a purified,
  milligram-scale, biophysics-grade nuclear-receptor LBD — a construct class with well-known
  solubility difficulty. Treat it as evidence that custom protein is *not* absurdly priced, **not**
  as a quote.

### 4.3 · Off-catalogue small molecules and tool compounds — ✅ genuinely buyable, and it changes nothing

MedChemExpress, Selleck Chemicals, Cayman Chemical, Tocris/Bio-Techne and MilliporeSigma sell
milligram quantities of tool compounds — including the ATR inhibitors route 1 names — as ordinary
catalogue chemicals, typically tens to low hundreds of dollars per compound. Enamine and Life
Chemicals sell fragment libraries and make-on-demand compounds. **This tier passes F1 and F2
comfortably.**

⛔ **And it settles nothing**, because there is no assay in this project to put a compound into
(§3.2). ⚠ Two honest caveats: research chemicals ship under research-use-only terms to a
**qualified purchaser**, and several suppliers operate customer-qualification checks; and a compound
delivered to a residence is a compound with nowhere to go. **Recorded so it is not mistaken for a
route.**

### 4.4 · Biophysical binding assays as a service — ⛔ sold, but quote-only and unpriceable in advance

Thermal shift/DSF, SPR, BLI, MST, ITC, ligand-observed NMR and native MS **are** all sold
fee-for-service, by CROs including **2bind GmbH** (MST, nanoDSF, DLS, BLI, GCI, ITC — *"tailor-made
biophysics services"*, *"milestone-based projects"*), **Reaction Biology** (thermal shift), **Charles
River**, **SARomics Biostructures** (NMR and crystallographic fragment screening) and **Sygnature
Discovery**.

| filter | verdict |
|---|---|
| **F2 — no hands-on** | ✅ **passes.** This is the one part of the tier that genuinely does: a fully contracted service where the client ships nothing and does nothing is exactly the acceptable shape |
| **F1 — cost** | ⛔ **cannot even be evaluated.** **Not one of the CROs examined publishes a price.** The closest any page comes is Reaction Biology's *"very cost-effective"*. Establishing a number requires requesting a quote — i.e. contacting a vendor. **An unpriceable spend cannot be authorised against a $1,000 ceiling in advance** |
| **F3 — interpretable** | ⛔ **fails for `R4` specifically**, per §1.2: the formats sold report a binding *event*, and `R4` asks about a *site* |

⚠ **The sales model is itself a barrier, independent of price.** These are milestone-based project
engagements with scoping calls and a business counterparty — a shape that presumes an organisation.
Whether any would contract with a private individual is **UNCERTAIN, and deliberately unresolved**:
resolving it means contacting a vendor. **What would resolve it:** a single scoping enquiry stating
no institutional affiliation. **It is not worth making**, because F3 already rules out the only
experiment we would buy.

### 4.5 · DNA/oligo synthesis and sequencing — ✅ the one tier genuinely open to individuals

**As the brief anticipated.** Plasmidsaurus advertises *"Sign up in seconds. Submit any
number of samples online. Pay using a PO, credit card, or dinocoins."* — no institutional gate in the
sign-up path ([plasmidsaurus.com](https://www.plasmidsaurus.com/)). IDT, Twist, Azenta/GENEWIZ,
Eurofins Genomics and Novogene operate comparable self-serve ordering.

⚠ **With one real qualifier.** Gene-synthesis providers screen **customers as well as sequences**:
the International Gene Synthesis Consortium — *"approximately 80 % of gene synthesis capacity
worldwide"* — describes *"a common protocol to screen both the sequences of synthetic gene orders and
the customers who place them"*, including *"vetting customers"*
([genesynthesisconsortium.org](https://genesynthesisconsortium.org/)). Nothing this programme would
order is a regulated sequence, so this is a note about the tier's shape rather than a barrier here.

⛔ **And it settles nothing, for the reason the brief predicted: we have no sample to sequence.**
There is no EMC nucleic acid in this project and no route to one that does not start with a patient
or a lab. **This tier is real, cheap, individual-accessible — and inapplicable.**

### 4.6 · Community / DIY biology labs — ⛔ ruled out twice over

**Genspace** (NYC) has *"provided Biosafety Level 1-compliant lab space to independent researchers,
scientists, artists, designers, entrepreneurs, hobbyists, teachers and students"* since 2010, and asks
members to *"start a project that meets the Centers for Disease Control and Prevention's Biosafety
Level 1 guidelines"* ([genspace.org](https://www.genspace.org/join-the-lab)). BioCurious (Sunnyvale)
and equivalents operate the same model.

- ⛔ **F2 rules it out outright.** The entire premise is that *you* do the bench work. That is the one
  thing the filter forbids.
- ⛔ **Biosafety rules it out independently.** These are **BSL-1** facilities. Human cancer cell lines
  are conventionally handled at **BSL-2** (bloodborne-pathogen potential), so a human cancer line is
  outside a BSL-1 facility's stated scope — and it could not be obtained anyway (§4.1).
- ⚠ Recorded properly rather than dismissed, because it is the obvious idea and deserves a stated
  reason rather than silence.

### 4.7 · Cell-based assay services, and the other routes checked

| route | verdict |
|---|---|
| **Cell-based viability / dose–response CROs** (Reaction Biology, Eurofins Discovery, Charles River, Crown Bioscience) | ⛔ Sold fee-for-service, quote-only, business-counterparty model — and **for EMC they would need the EMC line, which §4.1 closes.** A dose–response in a generic line answers no question this repo has |
| **Cloud labs** (Emerald Cloud Lab and successors) | ⛔ **UNCERTAIN → effectively no.** Genuinely interesting under F2 (remote-operated, no hands). But it is an enterprise engagement with no published consumer pricing (our pricing-page fetch 404'd), it still requires the client to supply materials and design the protocol, and **F3 is unchanged.** ⚠ Flagged as the one item worth re-checking if the model ever becomes self-serve |
| **SGC (Structural Genomics Consortium) donated chemical probes** | ⛔ Open-science probes are distributed **to researchers**, and **there is no NR4A3 probe**. A probe without an assay settles nothing |
| **NCI Patient-Derived Models Repository; patient-advocacy model brokers** (e.g. the Chordoma Foundation's model programme) | ⛔ These **distribute to investigators under agreements**; they are not purchases. ⭑ **But they are a genuine and under-used route for the *outreach* lever** — they exist precisely to connect a well-argued hypothesis with someone who has models. That is publish-to-convince, and it belongs on the outreach list rather than here |
| **Crowdfunded CRO work** (Experiment.com and similar) | ⛔ Not a purchase — it is fundraising, and it delivers a *collaborator* running the work, i.e. tier (c) reached by a different door. ⚠ Not dismissed: for an ultra-rare cancer with a preregistration already written, it is a real option **for the outreach lever**, and it is out of scope for a memo about what a credit card buys |
| **Commercial human tissue / tissue microarrays** (e.g. for an SSTR2 IHC on EMC) | ⛔ **UNCERTAIN, resolving to no.** Sarcoma TMAs are sold; **EMC-containing arrays were not found**, which is what EMC's rarity predicts. And an IHC on one or two cores is uninterpretable under F3, on top of the consent and ethics questions a private individual buying human tumour tissue would raise |

---

## 5 · What this means for strategy

1. ⭑ **The repo's two levers are the right two levers, and this memo is the audit that closes the
   question.** [`emc-treatment-strategy.md`](./emc-treatment-strategy.md)'s *"two paths"* —
   publish-to-convince and in-silico evaluation — are not a failure of imagination about a third
   option. **The third tier was scoped and it is empty.** That should be recorded once and not
   re-litigated.
2. **"The wet-lab ask" stays a real ranking axis — but it must be read as *what we are asking someone
   else for*, never as *what we could arrange*.** Every route memo should read that column as a
   measure of **how easy it is to persuade a collaborator**, which is what it has always actually
   measured. Route 1 scores well on it *for the right reason*: catalogue compounds and existing
   models make it an easy ask **of someone who has a bench**.
3. ⛔ **`R4` should stop being described in a way that invites a purchase attempt.** It is the
   cheapest requirement in the programme *and* it is not obtainable with money. The roadmap's own
   framing — *"carry it as the standing wet-lab dependency"* — is right; §1.6 adds the reason.
4. ✅ **The correct response to an empty buyable tier is to spend harder on the levers that work.**
   All 12 in-silico rows in §2.1–§2.2 are ours, several are $0, and the outreach step route 1 is waiting
   on costs nothing but a decision. **The binding constraint was never money; it is a collaborator,
   and it always was.**
5. ⚠ **One narrow thing a credit card genuinely does buy: dissemination.** Preprint posting, DOIs,
   figure production and open-access fees are purchasable by an individual for tens to hundreds of
   dollars. **That is the publish-to-convince lever, not the evidence lever** — it produces no new
   result and settles no open question, and it is noted only so the "empty tier" claim is precise
   about its scope: empty **of experiments**, not of every possible expenditure.

---

## 6 · Limits of this memo, stated so it is read correctly

- **Prices are list prices published on 2026-08-03 and will drift.** They are cited to establish an
  order of magnitude. The **protein-consumption figures in §1.5 are ESTIMATES from standard assay
  practice, explicitly labelled as such** — nothing in this repo measures them, and a real quote
  could differ substantially. Correcting them does not change the verdict, which rests on §1.2's
  category argument.
- **No vendor was contacted, so every eligibility conclusion rests on published policy rather than on
  a tested application.** Where a policy is explicit (DSMZ, ATCC, JCRB) the conclusion is firm; where
  it is inferred (ECACC, RIKEN, the assay CROs, the chemical suppliers' ship-to terms) it is marked
  **UNCERTAIN** with what would resolve it. **No UNCERTAIN row is load-bearing** — each is a route
  already closed on other grounds.
- **The `R4` verdict is about *purchasability*, not about the science.** `R4` remains the programme's
  cheapest decisive requirement and a negative would remain as valuable as a positive. Nothing here
  argues against running it; it argues that it cannot be *bought*.
- ⚠ **§1.1 is a refutation of a specific defeater, not a claim that the pocket is available.** The
  repo's own caveats stand and are restated there: 8XTT's conformers are not equilibrium samples,
  `R2` is unresolved, and `R6` has never been computed for any paralogue.
- **The §1.4 construct-truncation risk is NAMED AND UNMEASURED.** Nobody has shown that 398–626
  behaves differently from 373–626 at Pocket-5. It is recorded as a risk that would have to be
  retired before any purchase, not as a finding.
- **This memo does not re-rank anything.** [`emc-treatment-strategy.md`](./emc-treatment-strategy.md)
  owns the portfolio ranking and [`nr4a3-program-map.md`](./nr4a3-program-map.md) owns the plan; where
  either differs from this memo, it wins.
