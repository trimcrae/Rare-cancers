---
id: DOC-WET-LAB-CONTRACTING-COSTS
title: What contracting the wet-lab experiments would cost — the F1 gap, closed at $0
level: L3
kind: manuscript
status: live
canonical_for: [wet-lab contracting prices, academic core-facility rate evidence]
purpose: closes the one filter what-a-civilian-can-buy.md declared unevaluable, and re-scopes what the money question actually is
scope: As stated in the document's own role banner.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-23
last_verified: 2026-08-23
---
# What contracting the wet-lab experiments would cost — the F1 gap, closed at $0

> **Role: the price half of [`what-a-civilian-can-buy.md`](./what-a-civilian-can-buy.md), which that memo
> could not compute and said so.** Its §4.4 examined biophysics and screening CROs, found that **not one
> publishes a price**, and concluded that filter **F1** *"cannot even be evaluated … an unpriceable spend
> cannot be authorised against a $1,000 ceiling in advance."*
>
> **That finding is correct about CROs and is not disturbed here.** It was drawn over one supply channel.
> There is a second the memo never examined — **academic core facilities, which publish their rates,
> itemise them per instrument-hour and per technician-hour, and often carry an explicit
> external-academic and external-commercial tier.** Those rate cards make a bottom-up estimate possible
> **without contacting anybody**, which is what this memo builds.
>
> **Subordinate to [`nr4a3-program-map.md`](../nr4a3-program-map.md)** (the roadmap owns the plan and the
> gates) and to [`what-a-civilian-can-buy.md`](./what-a-civilian-can-buy.md) (which owns the
> **eligibility** findings, the three filters, and the protein price — **nothing here restates one**).
> Where either conflicts with this memo, **they win.**
>
> **$0.** Research and arithmetic only. **Nothing was purchased, no vendor or facility was contacted,
> nothing was signed up for, no lab and no person was approached.** Rate cards were fetched read-only
> from a CI runner to `literature-cache` under `literature/wetlab-pricing/` and
> `literature/wetlab-pricing-b/`; every figure below is quoted from the facility's own public page.
> Derived totals come from [`wetlab_contracting_costs.py`](../../modalities/wetlab_contracting_costs.py)
> → [`wetlab-contracting-costs.json`](../../modalities/wetlab-contracting-costs.json) — **no total in
> this document is typed.**
>
> **No efficacy, safety, therapeutic-window or clinical-readiness claim is made or implied for any
> molecule, route or experiment named here.**

---

## 0 · THE VERDICT, STATED FIRST

⭑ **The money question has an answer, and it is roughly ten to fifty thousand dollars per experiment —
one to two orders of magnitude above the $1,000 filter, and one to two orders of magnitude BELOW what
"contract a wet lab" sounds like.** The repository's own **smallest** wet-lab ask prices at about
**$18k**; its **decisive** ASO experiment at about **$35k**, plus about **$12k** for the engineered
control line that makes its central claim provable at all.

⛔ **And the answer does not change the strategy, because price was never the binding constraint.**
The three EMC cell lines every one of these experiments needs are **institution-gated by policy**
([`what-a-civilian-can-buy.md` §4.1](./what-a-civilian-can-buy.md), which owns that finding). A
facility that publishes a rate is not thereby a facility that will take this project, this client, or
these cells. **The binding constraint is a collaborator, and it always was** — this memo makes that
statement *quantitative* instead of merely asserted.

### ⭑ The three findings that are genuinely new

| # | finding | why it matters |
|---|---|---|
| **1** | **F1 is evaluable after all — through a channel the memo did not check.** Academic cores publish rate cards; CROs do not. The unpriceability was a property of **who was asked**, not of the work | An unbounded spend became a bounded one. §1 |
| **2** | **Instrument time is nearly free; LABOUR is most of the cost — but it splits in two.** Biacore 8000 SPR runs **$20.55/hour at an external *commercial* tier**; a technician runs **$120/hour**. Hourly hands are **60.9%** of the total and **82–85%** of the plate experiments; a further **24.1%** is bundled cell-engineering service fees that no hourly discount touches | It re-points the cost question, and it is what any "automation makes this cheap" argument turns on. §2, §3.2 |
| **3** | **The external-commercial markup is small and MEASURABLE, not a guess** — 1.644× internal at the one facility publishing both tiers | "They'd charge an outsider a fortune" is refuted for at least one real rate card. §2.1 |

⚠ **One correction this memo owes to its parent.** [`what-a-civilian-can-buy.md` §1.2](./what-a-civilian-can-buy.md)
argues that site resolution — the structural experiment `R4` actually needs — is *"an order of magnitude
more expensive in both protein and money"* than a binding assay. **The money half of that is not
supported by the rate evidence** and is re-scoped in §4. The **category** argument it rests on — that you
cannot buy an assay pointed at a *site* — is untouched and remains decisive.

---

## 1 · Why the price existed all along, and where the parent memo's search missed it

**The parent memo asked CROs.** 2bind, Reaction Biology, Charles River, SARomics, Sygnature. Re-fetched
2026-08-23, the finding replicates exactly: **Altogen Labs' page for the very assay class route 1 needs
advertises *"Get an Instant Quote"* and then resolves to an email address and a phone number**
(`literature/wetlab-pricing/cro_altogen_quote_pharmtox.txt`); 2bind offers a *"Quote Inquiry"*
(`.../cro_2bind_small_molecule.txt`). **Still not one published price.** §4.4's verdict stands.

⭑ **But a CRO is not the only thing that sells an experiment.** Academic core facilities sell the same
instruments and the same hands, and they are **required to publish their rates** — a recharge centre
prices by a documented cost basis, which is exactly why the number is on a public page instead of behind
a scoping call. Several publish an explicit outside-user tier:

- **McGill's Imaging and Molecular Biology Platform** states it plainly: *"The platform is also open to
  users outside of academia. Please contact the platform administrators for more information."*
  (`literature/wetlab-pricing-b/mcgill_impact_pricing.txt`)
- **The University of Chicago BioPhysics Core Facility** publishes **five** tiers — Internal, External
  Affiliated, External Academic Non-Profit, **External Start-Up Company** and **External Commercial**
  (`literature/wetlab-pricing/core_uchicago_biophysics_fees.txt`).
- **NC State's Biomolecular Interactions Core Facility** publishes self-use academic rates and directs
  corporate users to *"contact for corporate and assisted use fees"* (`.../core_ncsu_bicf.txt`).

⇒ **The unpriceability was a property of the vendor class the memo happened to sample, not of the
work.** That is the whole methodological finding, and it is worth stating because it generalises: **when
a market says "quote only", check whether a recharge-funded institution sells the same thing.**

⚠ **Publishing a rate is not offering access.** §5 keeps these separate, and the separation is the
memo's honest core: **§1–§4 answer "what does it cost", and nothing in them answers "may we buy it".**

---

## 2 · The rate card — what an hour of each thing actually costs

*Every figure quoted from the named facility's own published page. `tier` matters: an internal-academic
rate is the FLOOR any user pays, not what an outsider pays. Full machine-readable card, with source and
cache path per row: [`wetlab-contracting-costs.json`](../../modalities/wetlab-contracting-costs.json)
→ `rate_card`.*

| what | rate | tier | facility |
|---|---|---|---|
| **A technician's hands** | **$120 / hour** ($80 internal) | external academic | McGill Imaging & Molecular Biology Platform |
| High-content imaging (Operetta) — *the γH2AX readout* | **$40 / hour** ($15 internal) | external academic | McGill |
| High-content image analysis (Harmony / Columbus) | $25 / hour | external academic | McGill |
| Plate reader (Tecan Spark) — *viability* | $30 / hour | external academic | McGill |
| qPCR, 96-well (ViiA7) — *junction knockdown readout* | $20 / hour | external academic | McGill |
| **SPR (Biacore 8000)** | **$20.55 / hour** ($12.50 internal) | **external COMMERCIAL** | UChicago BioPhysics Core |
| ITC (MicroCal PEAQ) | $40 / hour, 2 h min | academic self-use | NC State BICF |
| Circular dichroism | $25 / hour, 4 h min | academic self-use | NC State BICF |
| **A screening core's bundled hands-plus-robot day** | **$577.23 / day** | internal academic (2015 rates) | CU Boulder HTS Core |
| Pilot screen, 1,000 compounds | $1,354.66 | internal academic (2015 rates) | CU Boulder HTS Core |
| Full HTS, 14,400-compound library in replicate | $10,837.24 | internal academic (2015 rates) | CU Boulder HTS Core |
| HTS cost per well, reagents + scientist time | $0.10 – $1.00 | academic core, stated range | UW Carbone SMSF |
| Catalogue tool compound, 1–5 mg | $25 – $100 | commercial catalogue | UW Carbone SMSF (quoting suppliers) |
| **2′-MOE gapmer wing chemistry** | **$15 per modified base** (50 & 200 nmol; $18 at 1 µmol) | commercial list | Gene Link |
| CRISPR HDR-mediated gene tagging — *the dTAG shape* | **$10,840** | academic core service, FY2026 | UMN Genome Engineering |
| CRISPR single-amino-acid knock-in | $9,680 | academic core service, FY2026 | UMN Genome Engineering |
| CRISPR simple single-gene KO line | $5,126 | academic core service, FY2026 | UMN Genome Engineering |
| HDR donor vector construction | $1,469 | academic core service, FY2026 | UMN Genome Engineering |
| gRNA design + validation | $1,108 | academic core service, FY2026 | UMN Genome Engineering |
| Commercial custom KO cell line, advertised floor | from $1,980 | commercial promotional | Ubigene |

⚠ **The CU Boulder rates carry an effective date of 2015-07-01 on their own page.** They are eleven
years stale and are used here only where nothing newer was found; they almost certainly understate.
Flagged rather than silently modernised.

### 2.1 · ⭑ The external-commercial markup, measured rather than assumed

The UChicago card is the one place this repository can **measure** what a facility charges an outside
commercial user against what it charges itself, on the same instrument on the same page:

**Biacore 8000 SPR — $12.50/hour internal → $20.55/hour external commercial = 1.644×**
(derived, `wetlab-contracting-costs.json` → `external_commercial_markup`).

⇒ **The instinct that an outsider pays a punitive multiple is wrong for at least one real rate card.**
⚠ It is **one facility and one instrument**, cited to bound the markup rather than to be applied
elsewhere; a different core could differ, and none of the totals below applies it.

---

## 3 · What each named experiment would cost

*Derived — every total below is computed by [`wetlab_contracting_costs.py`](../../modalities/wetlab_contracting_costs.py),
not typed. **Rates are MEASURED; quantities are ESTIMATES made by that module**, and the quantities are
the dominant uncertainty: labour dominates every row, so a technician-hour count wrong by 2× moves the
total by nearly 2×.*

| # | experiment | who specifies it | **total** |
|---|---|---|---|
| **E1** | **Route 1b — 7-point ATRi dose–response in EMC lines, γH2AX readout, PARPi arm, proliferation index** | [`emc-post-degrader-options.md`](../program/emc-post-degrader-options.md) Axis W2 | **$17,580** |
| **E2** | **ASO §4 — junction-ASO vs scrambled knockdown in two patient-derived EMC lines, sparing + phenotype arms** | [`fusion-junction-aso-working-record.md` §4](../aso/fusion-junction-aso-working-record.md) | **$34,840** |
| **E2b** | **ASO §4 controls — the engineered isogenic fusion-positive/negative pair** | same §4 | **$12,257** |
| **E3** | **`R4` binding half — a 1,000-compound pilot screen plus SPR follow-up** | [roadmap §5 row R4](../nr4a3-program-map.md#5--where-each-requirement-stands) | **$2,277** |
| **E4** | **`R16` — dTAG degron knock-in in an EMC line, the delegated dependency test** | [roadmap §5 row R16](../nr4a3-program-map.md#5--where-each-requirement-stands) | **$25,257** |
| **E5** | **Route 6 — trabectedin × PPARγ agonist two-drug matrix** | [`emc-post-degrader-options.md`](../program/emc-post-degrader-options.md) route 6 | **$14,160** |

⚠ **These are ALTERNATIVES, not a sequence.** The portfolio sum in the artifact
(`portfolio_total_usd`) is arithmetic over five options that are ranked against each other elsewhere;
**it is not a programme budget and nobody plans to buy all five.**

### 3.1 · The three things the totals say that the tiers do not

1. ⭑ **The repository's "cheapest wet-lab ask" is about $18k, and roughly two-thirds of that is a
   technician.** [`emc-post-degrader-options.md`](../program/emc-post-degrader-options.md) grades
   route 1b's ask **the smallest in the portfolio** and calls it *"a plate experiment, not a program"* —
   both true, and **still ~18× the $1,000 filter**. The compounds, which the route memo correctly
   emphasises are catalogue items, are **under $500 of it.** *"The compound was never the bottleneck"*
   ([`what-a-civilian-can-buy.md` §3.2](./what-a-civilian-can-buy.md)) is confirmed with a number:
   the compounds are **~2%** of the experiment.
2. ⭑ **`R4`'s binding half is the cheapest thing in the portfolio by a factor of five — and it is the
   one the parent memo rules out on grounds that survive any price.** ~$2.3k of screening and SPR,
   *before* protein, which [`what-a-civilian-can-buy.md` §1.5](./what-a-civilian-can-buy.md) prices and
   shows dominates. Cheap and uninterpretable is still uninterpretable (§4).
3. ⭑ **Cell engineering is a step change, and it is unavoidable in exactly the two places the science
   needs it most.** E2b and E4 are ~$12k and ~$25k because an HDR knock-in is a published service with
   a published five-figure price. **The ASO paper's red team required the isogenic pair to make the
   wild-type-sparing claim provable at all** — so the honest cost of the decisive ASO experiment is
   **E2 + E2b ≈ $47k**, not E2 alone.

---

### 3.1.1 · ⭑ One independent check on the quantities, and it is the repository's own

**The dominant uncertainty here is hours, not rates (§6), so an outside estimate of the same
experiment's labour is worth more than another rate card.** There is one, and it was written before
this memo and without reference to it: [`fusion-junction-aso-working-record.md` §4](../aso/fusion-junction-aso-working-record.md)
describes the decisive ASO experiment as asking a lab to weigh **"a technician-month"**.

| estimate | hands for E2 | source |
|---|---|---|
| this memo | **240 h** ≈ 1.4 technician-months | `wetlab_contracting_costs.py`, an assumption |
| the ASO working record | **~150–173 h** = 1 technician-month | written independently, for a different purpose |

⇒ **They agree to within about 1.5×**, and this memo's is the more conservative. Taking the working
record's figure instead would put E2 at roughly **$24k–$27k** rather than $34,840 — the same order,
and it does not move any conclusion in §3.2.3, where even **free** labour leaves the experiment far
above the filter.

⚠ **Stated at its true weight: this is a weak check, not a validation.** Both numbers are estimates
by the same project, neither was measured against a real run, and "a technician-month" was written as
a rhetorical scale for an outreach letter rather than as a costing. It bounds the disagreement; it
does not establish that either is right.

### 3.2 · ⭑ Is it labour? Mostly — but "mostly" hides the part that decides the answer

**Measured against the model rather than eyeballed** (`wetlab-contracting-costs.json` → `cost_structure`).

| what you are buying | share of all five | what it is |
|---|---|---|
| **`hands` — hourly technician time** | **60.9%** | billed by the hour on a published rate card |
| **`cell_engineering_service`** | **24.1%** | a bundled CRISPR project price, sold as an outcome |
| consumables | 8.5% | plasticware, media, antibodies |
| instrument time | 3.4% | SPR, imagers, plate readers, qPCR |
| materials (compounds + oligos) | 1.8% | the catalogue chemistry |
| bundled screening | 1.3% | a core's hands-plus-robot package |

⛔ **The aggregate is the misleading number. The split by experiment is the real finding:**

| experiment | hourly hands | bundled service |
|---|---|---|
| E1 · ATRi dose–response | **81.9%** | — |
| E2 · ASO knockdown | **82.7%** | — |
| E5 · trabectedin × PPARγ | **84.7%** | — |
| E4 · dTAG degron knock-in | 38.0% | **53.1%** |
| E2b · isogenic control line | **0%** | **100%** |
| E3 · `R4` binding half | **0%** | — (40.5% instrument, 59.5% bundled screen) |

⭑ **Two populations, not one.** The **plate experiments** are 82–85% hourly hands. The **cell-engineering**
experiments contain no hourly hands at all — they are a fixed project price whose cost driver is **clonal
selection and validation**, i.e. iterative biology on a timeline set by how fast cells divide. Labour is
inside that price, but it is not sold by the hour and **a faster pipettor does not make cells divide
faster.** And `R4`'s binding half — already the cheapest thing here — has **no labour line at all.**

### 3.2.1 · What happens if hourly labour gets cheap

*Derived, `wetlab-contracting-costs.json` → `labour_sensitivity`. It scales **`hands` only**, because
assuming a robot discounts a fixed project fee would be assuming the answer.*

| experiment | today | ×0.5 | ×0.1 | **hands free** |
|---|---|---|---|---|
| E1 · ATRi dose–response | $17,580 | $10,380 | $4,620 | **$3,180** |
| E2 · ASO knockdown | $34,840 | $20,440 | $8,920 | **$6,040** |
| E5 · trabectedin × PPARγ | $14,160 | $8,160 | $3,360 | **$2,160** |
| E4 · dTAG degron | $25,257 | $20,457 | $16,617 | **$15,657** |
| E2b · isogenic line | $12,257 | $12,257 | $12,257 | **$12,257** |
| E3 · `R4` binding half | $2,277 | $2,277 | $2,277 | **$2,277** |

⇒ **The plate experiments get 5–6× cheaper. The cell-engineering ones barely move, and two do not move
at all.** ⚠ **This is an arithmetic bound, not a forecast**, and no date is claimed for any column.

### 3.2.2 · What the automation evidence actually says — including the half that cuts against it

**Recorded as a vendor's claim, because that is what it is.** Emerald Cloud Lab's own startup
comparison (`literature/wetlab-automation/ecl_efficiency_startup.txt`) sets a traditional lab's team at
**2 co-founders, 2 scientists and 4 technicians — $802K/year** against a cloud lab's **2 co-founders and
2 scientists — $480K/year**, with throughput of **8,880 → 46,620** samples a year.

⭑ **The layer it removes is exactly the four TECHNICIANS. The scientists stay.** That maps precisely onto
the `hands` category above and not onto design or interpretation, which is why the sensitivity's
`hands → 0` limb is the right shape. Derived from those figures: a **40.2%** headcount cut, **5.25×**
throughput, and **8.77×** better headcount-cost per sample.

⛔ **And two things from the same vendor cut hard the other way, which is why this is not a green light.**

1. **A robotic lab still bills a human.** ECL's own pricing function composes a protocol's cost from
   `PriceInstrumentTime`, **`PriceOperatorTime`**, `PriceCleaning`, `PriceStocking`, `PriceWaste` and
   `PriceMaterials` (`.../ecl_price_experiment.txt`). **Operator time is a line item on the invoice.**
   Automation did not delete the human from the cost model; it moved them off the client's payroll and
   onto the bill.
2. **The tier is still quote-only.** That same documentation says its displayed figures *"are only for
   the sake of example and do not represent actual prices."* [`what-a-civilian-can-buy.md` §4.7](./what-a-civilian-can-buy.md)
   flagged the cloud lab as *"the one item worth re-checking if the model ever becomes self-serve."*
   **Re-checked 2026-08-23: it has not.** The vocabulary is still `team`, `notebook` and *financing
   team* — an organisation's shape, not an individual's.

### 3.2.3 · So the honest answer to "does automation make this reachable?"

⭑ **It makes it cheaper. It does not make it reachable, and the two are different claims.**

- ✅ **Cheaper, genuinely, and by the most-of-it margin** — 61% of the aggregate and 82–85% of the plate
  experiments is the exact layer automation is claimed to remove.
- ⛔ **But the floor is not near the filter.** With hands entirely free, **no experiment here falls below
  $2,000**, and the five together still total tens of thousands. The $1,000 filter is not reached by any
  labour assumption, including a free one.
- ⛔ **And the binding gate is untouched.** Every experiment except `R4`'s binding half needs the EMC
  cell lines, which are **institution-gated by policy** and held under MTA by three academic groups.
  **A robot does not get you an MTA, and no throughput multiple creates a patient-derived line that
  three labs in the world hold.** [`method-watch.md`](../../method-watch.md)'s remote-robotic-wet-lab row
  reached this conclusion before this memo existed and states it exactly: a cloud lab *"flips the
  execution gate, not automatically the material gate."* **This memo supplies the number that row
  lacked, and does not change its verdict.**

⚠ **Where automation WOULD change something real, and it is not the one people reach for.** It makes the
ask cheaper **for the collaborator who already holds the cells** — which is a *persuasion* argument, not
an access one, and persuasion is the lever this programme actually pulls.

---

## 4 · The correction the rate evidence forces on `R4`

[`what-a-civilian-can-buy.md` §1.2](./what-a-civilian-can-buy.md) makes two claims about site
resolution. **One holds and is decisive. The other does not, and keeping them married would hide a real
option behind a wrong reason.**

| claim | verdict |
|---|---|
| *"You cannot buy an assay 'against a site.' Every affordable binding assay reports a binding EVENT on a PROTEIN"* — and the cheap site-localisation workaround needs a known binder, which is **precisely what `R4` asks** | ✅ **HOLDS, and it is the decisive one.** Circular by construction, unchanged by any price |
| *"Site resolution … is an order of magnitude more expensive in both protein and money"* | ⚠ **THE MONEY HALF IS NOT SUPPORTED.** Academic crystallography cores publish **per-structure** prices in the **hundreds to low thousands** — the same order as the assays, not an order above. ⚠ **Rung-0 evidence only:** the specific facility pages 403'd at fetch, so no figure from them is quoted as measured here, and the claim is stated as **the parent memo's figure is unsupported**, not as a counter-figure |

⭑ **And there is a third thing neither memo recorded: the site-resolved experiment `R4` names is offered
at NO COST to peer-reviewed academic proposals.** Diamond Light Source's **XChem** runs crystallographic
fragment screening — up to ~1,000 compounds screened individually — allocated through biannual calls for
peer-reviewed academic proposals, with results published and hit structures deposited in the PDB;
industrial access is arranged separately and is quote-only.

⛔ **This does not open a route, and it must not be read as one.** XChem is **affiliation-gated at the
proposal stage** — it wants a peer-reviewed academic proposal from an institution — and it needs a
**crystal system for the target**, which nobody has for NR4A3's Pocket-5. ⚠ Fetches of every XChem page
returned **403** (`literature/wetlab-pricing-b/xchem_*`), so the access terms here are **rung-0 search
evidence and are marked UNCERTAIN**; the industrial rate is **UNKNOWN** and an honest unknown is
recorded rather than a remembered number.

⇒ **What actually changes.** `R4`'s roadmap sentence should stop carrying *cost* as a reason.
[`what-a-civilian-can-buy.md` §1.6](./what-a-civilian-can-buy.md) already lands on the right conclusion —
*"`R4` needs a collaborator with a structural-biology capability, not a credit card"* — and this memo
sharpens **why**: not because the structural experiment is expensive, but because it is **gated on an
affiliation and on a crystal system**, and because **a positive on this exact protein has already failed
to settle `R4` once** ([§1.3](./what-a-civilian-can-buy.md)).

---

## 5 · What money still cannot buy — the gates that no rate card touches

**Stated separately from every number above, because a price is not an offer.**

| gate | status | owner |
|---|---|---|
| **The EMC cell lines** — USZ20-EMC1, USZ22-EMC2, NCC-EMC1-C1 | ⛔ **Academic lines held by their originating groups. An MTA between institutions, not a purchase.** Every experiment in §3 except E3 needs them | [`what-a-civilian-can-buy.md` §4.1](./what-a-civilian-can-buy.md) |
| **Repository lines** (DSMZ, ATCC, JCRB) | ⛔ Institution-gated by explicit published policy | same |
| **Would a core take an unaffiliated individual?** | ⚠ **UNCERTAIN and deliberately unresolved.** McGill's page says the platform is *"open to users outside of academia"*; UChicago publishes commercial tiers. Neither says *unaffiliated individual*, and resolving it means contacting a facility | this memo |
| **Marketplaces** (Science Exchange) | ⛔ **Enterprise-shaped.** *"Under one contract with Science Exchange"*, subscription or take-rate, supplier-onboarding framing — a business counterparty model, not a self-serve checkout | `literature/wetlab-pricing/marketplace_science_exchange.txt` + rung-0 |
| **XChem / synchrotron fragment screening** | ⛔ Affiliation-gated at proposal stage; needs a crystal system nobody has | §4 |
| **Route 7's ⁶⁸Ga-DOTATATE scan** | ⛔ Unchanged — an approved diagnostic **ordered by a physician for a patient**. Not purchasable in any form | [`what-a-civilian-can-buy.md` §2.1](./what-a-civilian-can-buy.md) |

⭑ **So the tier structure survives with one amendment.** The parent memo's **(b) BUYABLE** tier is still
**empty**, and for the reason it always gave — *eligibility*, not price. What changes is that the
**(c) NEEDS A LAB WE DO NOT HAVE** rows now carry a **number**, which is what an outreach conversation
needs: the ask is no longer *"would you run this?"* but *"this is ~$18k of your core's time, ~2% of it
reagents, and here is the preregistration."*

---

## 6 · Limits of this memo, stated so it is read correctly

- **Every quantity is an ESTIMATE and nothing in this repository measures one.** Technician-hours,
  plate counts, imaging hours and oligo scales are this memo's assumptions. **Labour dominates every
  total**, so the quantities — not the rates — are where the error lives. A 2× error in hours is a
  ~2× error in the answer. ⭑ **The only check available is in §3.1.1** — the ASO working record's
  independent "technician-month" for the same experiment, which agrees to within ~1.5× and is
  *lower* than this memo's. Two estimates by one project are a bound on disagreement, not a
  validation.
- **Rates are list prices published on 2026-08-23 and will drift.** The CU Boulder card is dated
  **2015-07-01** on its own page and is used only where nothing newer was found.
- **Rate tiers are mixed and are labelled per row.** Several are internal-academic — the floor. Only
  one instrument on one card supplies a measured external-commercial multiple, and it is not applied
  to any total.
- **No facility was contacted, so every eligibility conclusion is inference from published policy**,
  and the one that matters most — whether any core would contract with an unaffiliated individual — is
  marked **UNCERTAIN** and is **not load-bearing**, because §5's cell-line gate already closes the
  routes without it.
- **Twelve of sixty-nine fetches returned 403 or 404** — all five XChem pages, Harvard's Center for
  Macromolecular Interactions fee page, the Broad's genomics platform, Charles River's in-vitro
  oncology page, and four others; the per-target status is in each corpus's `_manifest.json`.
  Nothing quoted as **measured** comes from them; where they were the only source, the row says
  **UNCERTAIN** or **UNKNOWN**. ⚠ The 403s are TLS-fingerprint blocks that a headless browser clears,
  so this is a **deferred free observation, not a closed question** — the one that would most repay
  it is XChem's industrial rate.
- **This memo does not re-rank anything and does not authorise anything.**
  [`emc-treatment-strategy.md`](../program/emc-treatment-strategy.md) owns the portfolio ranking,
  [`nr4a3-program-map.md`](../nr4a3-program-map.md) owns the plan, and
  [`what-a-civilian-can-buy.md`](./what-a-civilian-can-buy.md) owns eligibility and the three filters.
  **A price is not a purchase, and no purchase is proposed here.**
