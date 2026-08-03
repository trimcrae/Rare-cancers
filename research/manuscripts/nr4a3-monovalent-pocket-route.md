# The monovalent pocket-modulation route — a small molecule that only occupies the NR4A3 LBD

> **Role: route memo, written to one question that neither existing treatment of C397 asks.**
> [`target-route-options.md` route 2](./target-route-options.md) frames a C397 molecule as the *targeting
> arm of a bivalent*; [`emc-post-degrader-options.md` route 5](./emc-post-degrader-options.md) frames it as a
> *chemical-biology reagent* answering `R4`. Neither states the third option: **a standalone MONOVALENT
> molecule that simply occupies the LBD and thereby alters what the fusion does** — no second protein, no
> linker to an E3, no exit vector, no ubiquitin-transfer geometry, no ternary. This memo states it, tests
> it, and grades it.
>
> **Subordinate to [`nr4a3-program-map.md`](./nr4a3-program-map.md)** — the roadmap owns the plan, the
> gates, the requirement register and every price, and **nothing here restates one.** Where it conflicts
> with this memo, it wins. Also subordinate to [`emc-treatment-strategy.md`](./emc-treatment-strategy.md) +
> [`../IDEAS.md`](../IDEAS.md) (the portfolio) and to [`target-route-options.md`](./target-route-options.md)
> (the target axis), whose route-2 analysis this memo extends rather than replaces.
>
> **$0.** No GPU, no rental, no wet lab, no purchase, nobody contacted. Every new number is computed on CPU
> by [`../modalities/nr4a3_monovalent_reach.py`](../modalities/nr4a3_monovalent_reach.py) →
> [`nr4a3-monovalent-reach.json`](../modalities/nr4a3-monovalent-reach.json), which owns them; everything
> else is read from an artifact or a document that already owns it. **No molecule, no dose, no efficacy,
> potency, safety, therapeutic-window or clinical statement is made or implied**, and none follows from
> anything below.

---

## 0 · The four checks taken before any argument

Per CLAUDE.md §4 — a $0 observation is never "watching". **Three of the four changed the memo's conclusion,
and two of those changed it in the direction opposite to the one expected** — C promoted a sub-question the
route was assumed to fail, and D refuted this memo's own first reasoning. All four were free the whole time.

| # | check | cost | result |
|---|---|---|---|
| **A** | **Run the reach enumeration with NO second terminus** — the configuration `target-route-options.md` $0 item 4 and `emc-post-degrader-options.md` item 4 both named and neither ran | $0 CPU | ⛔ **Built, run, and it goes AGAINST the route.** Removing the E3 arm does not widen the categorical window; on the conservative convention it closes **every** cell that had one. [§3](#3--the-0-test-built-run-and-it-came-back-against-the-route) |
| **B** | **Does the repo's own reason for choosing degradation over inhibition survive contact with its own citations?** | $0, read | ⚠ **Partly not.** The caveat *"an inhibitor would have to block a function NOR-1 may not even gate on a pocket"* was written without weighing a verified primary source, in another repo file, that measured LBD-directed ligands altering NOR-1-regulated gene expression in cells. [§2.2](#22--and-the-repos-own-verified-citation-answers-it-partly-the-other-way) |
| **C** | ⭑ **The AF-1 question — is the LBD a functional handle IN THE FUSION, given that the fusion deletes NR4A3's AF-1?** | $0, read | ★ **Asked for the first time, and answered FAVOURABLY by the assay that already exists.** The one published demonstration of LBD-borne functional modulation of NOR-1 used a **Gal4-NOR-1-LBD** reporter — a construct that is *itself* AF-1-less. [§2.3](#23--the-af-1-question-asked-for-the-first-time-and-the-answer-is-not-the-one-i-expected) |
| **D** | **Is `R4` — the program's one un-buyable requirement — actually purchasable as a service?** | $0, read | ⛔ **Ruled out — owned by [`what-a-civilian-can-buy.md`](./what-a-civilian-can-buy.md), which also REFUTES this memo's first reasoning for it.** What survives here is route-specific: the one catalogue NR4A3 LBD **excludes C397 by a single residue**, so the cheap intact-mass probe readout would be blind to the programme's headline handle. [§6](#6--r4-as-a-purchase--ruled-out-and-not-for-the-reason-i-first-wrote) |

---

## 1 · The route, stated precisely — and the split that decides it

**What it is.** A small molecule that binds the NR4A3 ligand-binding domain and, by occupancy alone,
changes what EWSR1::NR4A3 does. Nothing else. It is the only LBD-directed route on the program's boards
that needs **no partner protein at any stage**.

**Why it is attractive, in one sentence.** Every one of the degrader program's blocking failures is a
property of the *architecture* rather than the target — the options memo's
[§0](./emc-post-degrader-options.md) owns that finding and its table — and a monovalent molecule discards
more of that architecture than any other route on the board.

⭑ **But the route is not one route, and the split is what decides it.** Selectivity has to come from
somewhere, and the two sub-forms take opposite paths:

| sub-form | how it would state a paralogue-selectivity claim | what that inherits |
|---|---|---|
| **non-covalent occupier** | a **binding-affinity ratio**. At equilibrium the occupancy ratio between two receptors at one free-ligand concentration is `exp(−ΔΔG/RT)` — a free-energy difference between two similar pockets | ⛔ **exactly the quantity the program has now failed to measure four separate ways** ([roadmap MECHANISM-FIRST](./nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged) owns the margin arithmetic; the options memo's §0 owns the four failures) |
| **covalent occupier at C397** | a **categorical** claim — a residue the paralogues do not have, which is set membership rather than an energy difference | the only selectivity axis this program's instruments can support ([`target-route-options.md` finding 2](./target-route-options.md)) — **and [§3](#3--the-0-test-built-run-and-it-came-back-against-the-route) measures it shut in this configuration** |

⚠ **This split is the memo's organizing fact and it has not been written down anywhere.** "Monovalent
pocket modulation" reads as one idea; it is two ideas that fail on *opposite* blockers.

---

## 2 · The crux: is the pocket FUNCTIONALLY ACTIONABLE — and is it actionable IN THE FUSION?

**Ligandability and functional actionability are different questions, and the program has only settled the
first.** The cryptic-pocket work supports the existence of an openable site, at the ceiling
[roadmap `R1`](./nr4a3-program-map.md#21--the-register) sets on it and no higher. *Does occupying it change
what the protein does* is a separate question, it is this route's make-or-break, and no other LBD-directed
route needs it —
a degrader, a TCIP and a covalent probe each need only a **binder**.

### 2.1 · The repo's own reason for choosing degradation, quoted rather than paraphrased

[`degrader-vs-synthetic-lethal.md`](./degrader-vs-synthetic-lethal.md) §1 is where the program decided
this, and it decided it against inhibition:

> *"NOR-1/NR4A3 is constitutively active and its transcriptional output scales with **expression level**
> … so lowering protein dose directly lowers oncogenic output, which is exactly what a degrader does (an
> inhibitor would have to block a function NOR-1 may not even gate on a pocket)."*

Read at its true weight, the first clause is an argument **for** degradation and the parenthesis is an
argument **against** inhibition, and they are not the same strength. "Output scales with expression level"
supports "removing protein removes output"; it does not establish that occupancy cannot also reduce output,
and the parenthesis says so itself with *"may not even"*. **The route must be graded against this, not
around it — and the honest grading is that the parenthesis was a stated uncertainty that the repo then
never went and resolved, although the material to resolve it was already in another of its own files.**

### 2.2 · And the repo's own verified citation answers it, partly, the other way

[`nr4a3-druggability-reconciliation.md`](../modalities/nr4a3-druggability-reconciliation.md) carries a
**primary-source-verified** record that the same repo's decision memo does not cite: **Zaienne et al.,
*ChemMedChem* 2022;17(16):e202200259** ([PMID 35704774](https://pubmed.ncbi.nlm.nih.gov/35704774/);
PMC9542104; doi 10.1002/cmdc.202200259) fragment-screened NOR-1/NR4A3 and, from a **<1 % hit rate**,
obtained three ligand chemotypes, one elaborated to a **low-micromolar inverse NOR-1 agonist that altered
NOR-1-regulated gene expression in cells.**

**That is a functional-actionability result, and it is the direct answer to "may not even gate on a
pocket".** Occupying the NR4A3 LBD *does* change NOR-1's transcriptional output — at low micromolar, on a
hard target, but measurably and in cells.

⚠ **Three limits travel with it and must never be dropped when it is cited.**

1. ⛔ **The binding site is structurally undefined.** The same reconciliation document says so explicitly:
   these are *pharmacological* druggability results that *"leave the binding site structurally
   undefined"*. So this is evidence about **the LBD**, and it is **not** evidence about the cryptic pocket
   the program models. `R4` — *does anything bind the opened cryptic site* — is untouched by it.
2. ⛔ **No paralogue counter-screen exists.** Verified verbatim in the same record (a single Gal4-NOR-1-LBD
   reporter, no paralog/off-target/counter-screen/cross-react language in the source). These compounds are
   NR4A3 *engagers of unmeasured paralogue selectivity*.
3. ⚠ **Low potency on a hard target.** A <1 % fragment hit rate is the measurement of how hard, and it is
   the same hardness a monovalent program would inherit.

⚠ **A citation-hygiene correction this check produced, recorded rather than silently applied.** Four repo
files — [`degrader-vs-synthetic-lethal.md`](./degrader-vs-synthetic-lethal.md) §1,
[`../IDEAS.md`](../IDEAS.md), [`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md) and
[`nr4a3-degrader-design-spec.md`](../modalities/nr4a3-degrader-design-spec.md) — attribute the NOR-1
druggability / inverse-agonist result to **"Munck 2022"**, with no PMID.
[`target-route-options.md`](./target-route-options.md)'s reference table already flags that entry as
unresolved. A search for the paper as those files describe it returns only Zaienne 2022, whose author list
(Zaienne, Arifi, Marschner, Heering — Merk group) contains no Munck. **The most likely reading is that
"Munck 2022" is a wrong author name for the paper the repo cites correctly elsewhere.** It is recorded here
as a resolution item rather than edited across four files in a route memo, and **nothing in this memo cites
"Munck 2022"** — every functional claim above is cited to the Zaienne record, which is the verified one.

### 2.3 · The AF-1 question, asked for the first time — and the answer is not the one I expected

**The question.** The disease protein is not NR4A3. It replaces NR4A3's own **AF-1** with EWSR1's
low-complexity region — the swap is measured and owned by
[`target-route-options.md` check B](./target-route-options.md) → `target-route-census.json` `af1_to_lc_swap`
— and the AF-1 is where NOR-1's only *approved-drug* pharmacology acts. The options memo's Tier 4 closes
6-mercaptopurine for exactly that reason, on a verbatim primary source
([Wansa et al., *J Biol Chem* 2003;278(27):24776–90, PMID 12709428](https://pubmed.ncbi.nlm.nih.gov/12709428/),
whose title is *"The AF-1 domain of the orphan nuclear receptor NOR-1 mediates trans-activation, coactivator
recruitment, and activation by the purine anti-metabolite 6-mercaptopurine"*), which also reports that
**SRC-2 modulates the AF-1 and not the LBD.**

**So the obvious worry is a serious one:** if NOR-1's mapped transactivation and coactivator recruitment are
AF-1-borne, and the fusion deletes the AF-1, then an LBD-directed molecule may be aiming at a domain with no
functional role *in the disease protein* — which would be worse than the wild-type case, not better.

★ **And the answer is already in the assay.** The Zaienne inverse agonists were read out on a **Gal4-NOR-1-LBD
reporter** (verbatim-verified in
[`nr4a3-druggability-reconciliation.md`](../modalities/nr4a3-druggability-reconciliation.md), 2026-07-12).
A Gal4 hybrid construct fuses the receptor **LBD** to the GAL4 DNA-binding domain; the receptor's own AF-1
and DBD are **not present**. So the one published demonstration that occupying the NR4A3 LBD changes
transcriptional output was made **in a construct that already lacks NR4A3's AF-1.**

⭑ **Stated as the finding it is: the AF-1 deletion is not, by itself, a defeater for LBD-directed
modulation of this receptor, and the evidence for that was sitting in the repo unconnected to the
question.** NOR-1 has two transactivation modules — an AF-1 that Wansa mapped, and an LBD-borne one that
Zaienne's compounds demonstrably repress with no AF-1 in the construct. **The fusion deletes the first and
keeps the second.**

⚠ **What this does NOT answer, and it is the real crux.** A Gal4-LBD chimera has **no competing
transactivation domain** — the LBD is the only activating module, so the readout is maximally sensitive to
LBD-borne activity. The EMC fusion is the opposite: EWSR1's low-complexity region is a **strong heterologous
transactivation module** in its own right, with its own mechanism (the FET prion-like domain's BAF
retargeting — Boulay et al., *Cell* 2017, relayed via
[`degrader-vs-synthetic-lethal.md`](./degrader-vs-synthetic-lethal.md)) and no known allosteric coupling to
the NR4A3 LBD. So the question the route actually turns on is:

> **Does repressing the LBD-borne component move the output of a protein whose other end is a strong,
> independently-acting activator?**

⛔ **Nobody has asked this, nothing in this repo can answer it, and it is not answerable in silico.** It is
a functional cell-assay question about a chimera. The program's delegated make-or-break — the dTAG
acute-degradation test that `R16` points at — does **not** serve it: dTAG answers *"is EMC addicted to the
fusion"*, and this route needs *"is EMC addicted to the fusion's LBD-borne function"*, which is strictly
stronger. **That is a fourth blocker, and this route is the only one on the boards that carries it.**

---

## 3 · The $0 test: built, run, and it came back against the route

**The test that existed, and why it was the right one.** The covalent sub-form is the only one that can
state a selectivity claim this program's instruments support, so its geometry is the route's decisive cheap
question. Every reach number this repo owns was enumerated for a molecule that must **also** present a
second terminus to solvent — an E3 ligand for the degrader, an effector recruiter for a TCIP. Both existing
memos record the same intuition in the same words (*"a strictly smaller search problem"*) and neither had
run it. It is free CPU. So it was built:
[`nr4a3_monovalent_reach.py`](../modalities/nr4a3_monovalent_reach.py) →
[`nr4a3-monovalent-reach.json`](../modalities/nr4a3-monovalent-reach.json) (+ `.md`), 18 unit tests.

**Design, and why it is paired.** Both configurations are computed **in one pass, from identical frames,
identical anchors and identical candidate branch-point sets**, differing only in the rule that turns a
branch position into a chain length — the bivalent rule keeps the E3 term, the monovalent rule drops it.
An unpaired comparison against the committed artifact would confound the configuration change with every
other difference between two runs. The committed
[`nr4a3-linker-covalent-reach.json`](../modalities/nr4a3-linker-covalent-reach.json) is used as a
**replication target** instead: the module refuses unless its bivalent half reproduces that artifact's
family-wide window cell for cell. ✅ It does — `replicates_the_committed_bivalent_window: AGREES`, alongside
`committed_anchor_distances: AGREES`, `unique_cysteine_partition: AGREES` and
`monovalent_never_exceeds_bivalent: HOLDS`.

### ⛔ The result

**Every bivalent (placement × pendant) cell was paired with the monovalent cell at its own warhead anchor
and the same pendant, and the transition counted.** On the **conservative** convention — a non-clashing
branch position with a clash-free arm to the sulfur — the collapse is complete and one-directional:

| corridor (conservative) | count |
|---|---|
| cells whose family-wide window **survived** removing the E3 arm | **0** |
| cells that **lost** their window | **37** |
| cells that **gained** a window | **0** |
| cells closed either way | 23 |

On the **permissive** through-space convention — an upper bound on reachability, which scores a buried
sulfur as reachable — the picture is mixed rather than favourable: some cells retain a window and a few gain
one, and **every gained window is 1–2 backbone atoms wide**, which is inside the side-chain displacement the
bivalent lane already measured between independently built paralogue models (that lane's
`noise_sensitivity` owns those figures and they are not re-typed here). Both conventions and both
configurations, with the per-cell rows, are in
[`nr4a3-monovalent-reach.json`](../modalities/nr4a3-monovalent-reach.json) → `paired_transitions` and
`family_wide_window`.

### ★ Why it happens, measured rather than argued

**The E3 term was doing selectivity work, not only costing atoms.** The bivalent length rule adds the
distance from the branch position to the E3 anchor, which penalises branch positions off the
warhead→E3 axis — and it penalises **each cysteine by a different amount**. Removing it removes a
discriminator along with a cost. The module measures this directly as the **rank of C397 among all
cysteines in the family**: bivalently C397 is the first residue in reach in almost every graded cell;
monovalently it is not first in almost every cell. The competitor set that overtakes it also changes —
including, at one anchor, **NR4A1 Cys551**, the family's one literature-anchored covalent site and the very
residue the NR-V04 confound is about ([roadmap §6a](./nr4a3-program-map.md#6a--dead--conclusively-unworkable-never-retry)),
which sat far outside the window in the bivalent configuration.

⚠ **And a second margin is lost before any paralogue is considered.** The bivalent counter-test's finding
was that the window is closed by a *paralogue* cysteine rather than by one of NR4A3's own conserved ones —
i.e. the intra-NR4A3 margin was the easy half ([roadmap branch 1b](./nr4a3-program-map.md#branch-1b--computed-not-reconciled-to-its-artifact)).
Monovalently it is not: the median intra-NR4A3 window falls by most of its width. The route loses margin on
**both** axes at once.

### What this result is, and what it is not

- ✅ **It is** a refutation of the specific hope that dropping the E3 arm would widen the categorical
  window — the hope two repo memos recorded and neither tested. **A negative here was worth exactly as much
  as a positive, and it cost nothing.**
- ⛔ **It is not** a refutation of monovalent pocket modulation as such. A **non-covalent** monovalent
  molecule has no cysteine to reach and is untouched by this measurement — it simply fails on the *other*
  blocker (§1's table).
- ⚠ **It inherits everything the bivalent lane inherits.** Geometry only: no thiol pKa, intrinsic
  electrophile reactivity, adduct stability or chemoproteomic selectivity is computed anywhere in this
  repo. Every anchor still comes from the docked pose whose known-answer test `V3` returned **INCONCLUSIVE**
  — and `V3`'s failure was **site** selection, which a marginalisation over pocket-mouth anchors does not
  absorb. Reach can refute a route; it can never license one.
- ⚠ **A robustness leg is reported and must not be read as the headline.** The module also re-grades the
  monovalent window against every available paralogue metadynamics conformer, **one paralogue at a time** —
  a smaller competitor set by construction, so more cells stay open. That says the closure is **not uniform
  across paralogue conformations**, which is a real caveat; it is not the family window, and the artifact
  says so in its own `⚠_how_to_read_this`.

---

## 4 · Effect on the paralogue requirement — RESHAPES, into a requirement of unquantified size

**It does not remove it.** A molecule that binds the NR4A3 LBD binds NR4A1's and NR4A2's LBDs too unless
something makes it not; occupancy is not more discriminating than degradation *a priori*. Stated in the
taxonomy [`target-route-options.md` §3](./target-route-options.md) uses: **RESHAPES.** Three specific ways,
and the third cuts against the route:

1. **The object of the claim changes.** The degrader's claim is a *degradation-window* claim — enough true
   margin to give a differential over a dosing interval, against a resolvable difference and an engine
   accuracy the [roadmap's MECHANISM-FIRST section](./nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged)
   owns. A monovalent antagonist's claim is a *functional-antagonism* claim: what must differ is
   occupancy-weighted output at a dose. **These are not the same object and this memo's contribution is to
   say so precisely** — but see 2.
2. ⛔ **It is still a ΔΔG.** Occupancy ratio at equilibrium is `exp(−ΔΔG/RT)`, so a non-covalent monovalent
   selectivity claim reduces to the same free-energy difference between two similar pockets. The
   requirement is reshaped in *what it is about*, not in *what instrument it needs*. Only the covalent form
   escapes it — and §3 measures that escape shut in this configuration.
3. ⚠ **The required margin is UNQUANTIFIED, which is a loss of information and not a reduction.** The
   roadmap owns a number for the degradation window. **This repo holds no corresponding number for an
   antagonism window** — nobody has stated how much occupancy selectivity a monovalent NR4A3 antagonist
   would need. "Smaller requirement" and "requirement nobody has sized" look alike on a route board and are
   opposite states.

⚠ **And one asymmetry that must not be written as good news.** The roadmap's
[§2.4](./nr4a3-program-map.md#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically)
makes NR4A1-sparing the *hard* constraint on the strength of a named anti-target genotype — a combined
germline knockout. An occupancy-based antagonist does not remove the protein, so how that genotype maps onto
pharmacological antagonism is **a different and unmeasured question** from how it maps onto pharmacological
degradation. That is a **relocation into an unmeasured space**, not a safety argument, and nothing here
licenses NR4A1 engagement. The roadmap's own standing warning applies unchanged: an absent bound means the
liability could be larger, not smaller.

---

## 5 · Does it inherit the three blockers? Each answered separately

The options memo's Axis S asks three questions. **Three noes is the profile that survives; this route
returns one clean no, one qualified yes and one yes — and adds a fourth blocker of its own.**

| blocker | verdict for this route |
|---|---|
| **Does its central claim reduce to a ~1 kcal/mol ΔΔG?** | ⛔ **YES for the non-covalent form**, in full and without qualification (§4.2). **In principle no for the covalent form** — the categorical axis is set membership, not energy — **but §3 measures that window shut once the E3 arm is removed.** So the answer is *yes in whichever form you actually build*, which is the least comfortable of the possible answers |
| **Does it need a generated ternary?** | ✅ **NO, and this is the route's genuine advantage — the largest single block in the program, deleted.** No second protein at any stage: no E3, no effector recruiter, no induced complex, no ubiquitin-transfer geometry. It retires `R9` (the roadmap's *"whole remaining gap"*), `R10`, `R11` and `R12` outright. ⭑ **It is strictly cleaner than the TCIP route on this axis** — [`target-route-options.md` route 6](./target-route-options.md) records that a TCIP still *"inherits the same induced-complex modelling problem as `R9`"*. A monovalent molecule inherits nothing of the kind |
| **Does it need NR4A-paralogue discrimination?** | ⛔ **YES.** Reshaped, partly relocated, not removed (§4) |
| ⭑ **AND a fourth, which only this route carries** | ⛔ **The LBD must be a functional handle in the FUSION.** Every other LBD-directed route — degrader, TCIP, covalent probe — needs only a **binder**. This one needs occupancy to change output in a chimera whose other end is a strong independent activator, and the program's delegated dTAG test does not answer it (§2.3) |

---

## 6 · `R4` as a purchase — ruled out, and NOT for the reason I first wrote

⛔ **ONE HOME, AND IT IS NOT THIS FILE.** The purchasability question is owned repo-wide by
[`what-a-civilian-can-buy.md`](./what-a-civilian-can-buy.md), which ran the real vendor and construct
audit. **Its verdict — `R4` IS NOT BUYABLE, on three independent grounds — stands, and nothing is
restated here.** This section carries only the two things that are route-specific and would otherwise have
no home: a correction it forces on this memo, and a consequence for C397 that its audit did not draw.

⚠ **THE CORRECTION, REGISTERED RATHER THAN SILENTLY DROPPED.** An earlier draft of this memo ruled `R4`
out primarily *because the pocket is cryptic*, arguing that a purchased LBD might not present the site so
a negative would be unreadable. **That reasoning is refuted by the owning memo's §1.1 on this repo's own
evidence:** the site is present in an experimental, ligand-free, solution-state ensemble of the isolated
LBD, so a purchased construct would on best evidence present it at some minority population. *(Superseded,
retained: "the cryptic pocket is the reason worth recording", and the framing that the defeater is
population of the site.)* The operative grounds are the owning memo's, and the strongest of them is a
category error rather than a budget one — `R4` asks for a screen **against a site**, and no purchasable
assay can be pointed at a site.

⭑ **AND THE CONSEQUENCE FOR THIS ROUTE, WHICH THAT AUDIT DID NOT DRAW: THE CATALOGUE PROTEIN CANNOT
REPORT ON C397 AT ALL, AND IT MISSES BY ONE RESIDUE.** The one off-the-shelf recombinant NR4A3 LBD its §4.2
identifies spans **UniProt 398–626** (that span is the owning memo's fact and is not re-derived here). This
programme's three paralogue-unique LBD cysteines are **C397, C420 and C559**
([`nr4a3-covalent-handle-ensemble.json`](../modalities/nr4a3-covalent-handle-ensemble.json) owns the set).
So the catalogue construct retains C420 and C559 — the two that branch 1b closed — and **excludes C397, the
one that survived every test, by a single residue.**

- ⛔ **An intact-mass covalent-probe experiment on that protein would be blind to the programme's headline
  handle.** The cheap readout that makes the probe framing attractive would be measuring the wrong
  cysteines, and a clean negative on it would say nothing about C397. That is a *distinct* defeater from
  the three the owning memo lists, it is specific to the covalent route, and it is free to know.
- ⚠ **Stated at its true weight:** this is a construct-boundary observation, not a claim that no supplier
  could express 373–626. It says the *catalogue* option does not serve *this* route, and that a future
  session tempted by "the protein is buyable" should check the span before the price.

⇒ **Net effect on this memo's grade: none, and that is the point.** `R4` was already this route's
un-buyable dependency; the audit changes *which* of its grounds is load-bearing, not whether it holds.

## 7 · Grade against the failure record

**⭑ ★ REGISTERED, NOT PROMOTED — and specifically a DOWNGRADE of what the options memo's route 5 implies
about a monovalent *drug*, with one promotion inside it.**

**What earns it a place on the board.**

- It deletes the largest block in the program — the induced-complex/ternary layer — completely, and it is
  the *only* route that does so without substituting a different partner-protein problem.
- Its chemical matter and its measurement lane already exist: the Zaienne series is the anchor of a
  congeneric RBFE map this repo has already built. A monovalent program would not start from zero.
- ★ **The AF-1 worry, which looked like a clean defeater, is answered — and answered in the route's
  favour** by an assay construct that is itself AF-1-less (§2.3). That is a genuine promotion of one
  sub-question and it was free.

**What holds it below the options memo's Tier 2.**

- ⛔ **The two sub-forms fail on opposite blockers, so there is no version that clears both.** Non-covalent
  inherits the ΔΔG requirement in full; covalent's categorical escape is **measured shut** in exactly the
  configuration this route requires (§3). That is the memo's hardest finding and it was produced by the
  route's own cheapest test.
- ⛔ **It adds a make-or-break no other LBD route carries** — functional actionability of the LBD *in the
  chimera* — which cannot be computed, cannot be bought (§6), and is not covered by the program's delegated
  dTAG test.
- ⚠ **Its requirement is unsized.** Nobody has stated how much selectivity a monovalent NR4A3 antagonist
  would need, so "the requirement is smaller" is not a claim this repo can currently make (§4.3).

**The practical consequence, stated so it can be acted on.** The **probe** framing of
[`emc-post-degrader-options.md` route 5](./emc-post-degrader-options.md) is untouched by everything above
and remains the right ask of a collaborator — a probe needs only to bind, so it inherits neither the
functional-actionability blocker nor the selectivity one. What this memo removes is the temptation to read
that probe as the first step of a monovalent **drug** programme. **They are different objects, and the
route board should carry the distinction rather than the hope.**

---

## 8 · The $0 backlog this produces

| # | action | serves | why it is worth doing |
|---|---|---|---|
| **1** | ✅ **DONE this session — the E3-arm-free reach enumeration** ([`nr4a3_monovalent_reach.py`](../modalities/nr4a3_monovalent_reach.py)) | §3; closes [`target-route-options.md`](./target-route-options.md) $0 item 4 and [`emc-post-degrader-options.md`](./emc-post-degrader-options.md) item 4 | it was named twice and never run; a negative was worth as much as a positive and it is the negative |
| **2** | **Run the same paired configuration for the TCIP arm** (anchor + effector recruiter, no E3) | [`target-route-options.md` route 6](./target-route-options.md) | the machinery now exists and takes one more anchor set. ⚠ A TCIP is still bivalent, so it is a *different* second terminus, not this one — the result here does not transfer |
| **3** | ✅ **DONE 2026-08-03 — the "Munck 2022" attribution is RESOLVED and retired.** It was **five** files, not four, and the name matches **no paper**: measured in CI against Europe PMC and PubMed (0 hits for any author Munck on NR4A3/NOR-1; the title resolves uniquely to PMID 35704774). Correction registered once in [`nr4a3-druggability-reconciliation.md` §5b](../modalities/nr4a3-druggability-reconciliation.md), superseded attribution retained and quotable, every corrected site now carries the PMID, pinned by [`test_munck_attribution_retired.py`](../modalities/tests/test_munck_attribution_retired.py) | citation integrity (§2.2) | it was a wrong author name on the paper the whole warhead lane is anchored to — and the cost was real: the evidence was unfindable to the repo's own sessions |
| **4** | ✅ **DONE 2026-08-03 — re-fetched in CI and CONFIRMED, with one sharpening.** The plasmid is `pFA-CMV-hNOR-1-LBD` *"coding for the **hinge region and LBD** of the canonical isoform of NOR-1"*, and the Results call it *"a chimeric receptor composed of the human NOR-1 LBD and the Gal4 DNA binding domain from yeast"*. ⚠ **The construct is `hinge+LBD`, not `LBD` alone** — §2.3's conclusion is unaffected (both lie entirely outside the AF-1) but its scope should read `hinge+LBD`. Two independent 2026-08-03 fetches of PMC9542104 returned byte-identical bodies. Quotes and provenance: [`nr4a3-druggability-reconciliation.md` §5a](../modalities/nr4a3-druggability-reconciliation.md) | §2.3, which is now load-bearing | a favourable finding accepted without checking is exactly the failure mode this repo has rules about |
| **5** | **Ask the roadmap for an antagonism-window number**, or record explicitly that none exists | §4.3 | a requirement nobody has sized reads like a small requirement on every board it appears on |

---

## 9 · Limits of this memo

- **No efficacy, potency, safety, therapeutic-window or clinical-readiness claim is made for this route or
  any molecule**, and none follows from anything above. No molecule was synthesized; no GPU or rented host
  was used; no wet-lab work was performed, purchased, commissioned or proposed as a next step; nobody was
  contacted.
- **The new result is GEOMETRY**, on one opened target frame and independently built paralogue models, from
  anchors whose site question `V3` left INCONCLUSIVE. It can refute a route; it cannot license one.
- **The functional-actionability evidence is about the LBD, not about the cryptic pocket** (§2.2 limit 1),
  and it carries no paralogue selectivity of any kind (limit 2).
- **The `R4`-purchasability verdict is not this memo's** — [`what-a-civilian-can-buy.md`](./what-a-civilian-can-buy.md)
  owns it, and §6 records the correction it forces on an earlier draft here rather than leaving the
  superseded reasoning quotable. No vendor was contacted from this memo and no price was obtained here.
- **This memo does not re-rank the portfolio.** [`emc-treatment-strategy.md`](./emc-treatment-strategy.md)
  owns that and [`nr4a3-program-map.md`](./nr4a3-program-map.md) owns the plan; where either differs from
  this memo, it wins.

---

## References

*Every entry is relayed from a repo document that already carries it, per the fact-check discipline in
`AGENTS.md`. No citation here was generated for this memo.*

| citation | used for | as cited in |
|---|---|---|
| **Zaienne D, Arifi S, Marschner JA, Heering J, Merk D.** *Druggability Evaluation of the Neuron Derived Orphan Receptor (NOR-1) Reveals Inverse NOR-1 Agonists.* **ChemMedChem** 2022;17(16):e202200259. PMID **35704774**, PMC9542104, doi 10.1002/cmdc.202200259 *(⭑ **Merk D** is the fifth and corresponding author; this table previously stopped at four names)* | LBD-borne functional modulation of NOR-1; the **`hinge+LBD`** Gal4 readout; the absent paralogue counter-screen (§2.2, §2.3) | [`nr4a3-druggability-reconciliation.md` §5a/§5b](../modalities/nr4a3-druggability-reconciliation.md) — primary-source verified 2026-07-05, counter-screen absence verified verbatim 2026-07-12, **construct re-verified verbatim in CI 2026-08-03**. ⛔ *Superseded, retained: cited as* **"Munck 2022"** *in five other repo files with no PMID — measured to name no paper, corrected and pinned; backlog items 3 and 4 are discharged* |
| **Wansa KDSA, et al.** *The AF-1 domain of the orphan nuclear receptor NOR-1 mediates trans-activation, coactivator recruitment, and activation by the purine anti-metabolite 6-mercaptopurine.* **J Biol Chem** 2003;278(27):24776–90. PMID **12709428** | the AF-1 is where NOR-1's approved-drug pharmacology acts, and SRC-2 modulates AF-1 and not the LBD (§2.3) | [`emc-post-degrader-options.md`](./emc-post-degrader-options.md) Tier 4 — quoted verbatim there |
| **Boulay G, et al.** *Cancer-specific retargeting of BAF complexes by a prion-like domain.* **Cell** 2017. doi:10.1016/j.cell.2017.07.036 | the EWSR1 low-complexity region is an independently-acting transactivation/chromatin module (§2.3) | [`degrader-vs-synthetic-lethal.md`](./degrader-vs-synthetic-lethal.md) |
| **Nabet B, et al.** *The dTAG system for immediate and target-specific protein degradation.* **Nat Chem Biol** 2018. doi:10.1038/s41589-018-0021-8 | the delegated fusion-dependence test, and why it does not serve this route (§2.3) | [`target-route-options.md`](./target-route-options.md) references |
| NR4A3 vs EWSR1 domain swap; per-domain paralogue identities | §2.3, §4 | [`target-route-options.md`](./target-route-options.md) check B and finding 1 → `target-route-census.json` — **not recomputed here** |
| The bivalent linker-borne covalent reach result and its noise bound | §3 — the replication target and the comparator | [`nr4a3-linker-covalent-reach.json`](../modalities/nr4a3-linker-covalent-reach.json); [roadmap branch 1b](./nr4a3-program-map.md#branch-1b--computed-not-reconciled-to-its-artifact) |

---

*Medical-integrity note: no clinical fact, statistic, citation or patient datum in this memo is fabricated.
Every quantitative statement is either read from a named committed artifact or produced by
[`nr4a3_monovalent_reach.py`](../modalities/nr4a3_monovalent_reach.py). Nothing here asserts activity in
EMC, tolerability in a patient, or clinical applicability, and the route it describes is graded as an
untested hypothesis whose central requirement is unmet.*
