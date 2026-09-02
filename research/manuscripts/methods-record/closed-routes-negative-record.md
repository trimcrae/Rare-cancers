---
id: DOC-CLOSED-ROUTES-NEGATIVE-RECORD
title: Seven routes closed on argument rather than on experiment — the negative record of an EWSR1::NR4A3 route search
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: Turns seven register entries into one argument an outside reader can use — when a therapeutic route may be closed without an experiment, which closures are permanent, and which must name the observation that would reopen them.
scope: The seven routes filed against publication endpoint PUB-CLOSED-ROUTES. It covers the GROUNDS of each closure and the taxonomy that separates them; it covers no positive result, no molecule and no clinical statement.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-06
last_verified: 2026-08-06
---

# Seven routes closed on argument rather than on experiment — the negative record of an EWSR1::NR4A3 route search

> **Role: the manuscript for publication endpoint
> [`PUB-CLOSED-ROUTES`](../../../systems/views/L3-publications.md).** Seven routes in this repository's
> route register are closed, and every one of them was closed by an argument over a fact already on
> record rather than by an experiment. Their grounds are complete and each is filed with its own
> entry; what did not exist until this document is the writing that makes those seven entries **one
> argument a reader outside this repository can use.**
>
> **Subordinate to its sources, and it restates none of them.** The route register
> ([`systems/graph/routes.json`](../../../systems/graph/routes.json), rendered per route as
> `systems/views/L2-rt-*.md`) owns every route's state, grade and closure note. The closure
> vocabulary is owned by
> [`systems/graph/integrity.json` → `_closure_model`](../../../systems/graph/integrity.json) — **this
> paper adopts it and invents no category.** The program's own dead/parked/held register is
> [the roadmap §6](../nr4a3-program-map.md#6--the-closed-route-register); the route grades are owned by
> [`emc-post-degrader-options.md`](../program/emc-post-degrader-options.md) and
> [`target-route-options.md`](../program/target-route-options.md). Where any of them conflicts with this paper
> on a grade or a state, **they win** and this paper is the file to fix.
>
> **$0.** No GPU, no rental, no wet lab, no new computation. Every claim below is a read of an
> artifact, a route record or a cited primary source that was already committed.
>
> ⛔ **Nothing here is a molecule, a dose, a treatment recommendation or a statement about activity or
> tolerability in a patient**, and none is implied. A closed route says only that a particular
> *surface* is not the way; it says nothing about whether this disease can be treated. That
> distinction is asserted as a standing claim ceiling on the route families themselves
> ([`L1-st-fusion-direct.md`](../../../systems/views/L1-st-fusion-direct.md)) and it binds this paper.

---

## 1 · The claim, stated first so it can be disagreed with

**A therapeutic route can be closed rigorously without an experiment when the closure is
*definitional* — a fact about what the objects are — or is *arithmetic over a fixed measured fact*.
Those two kinds are permanent. Every other kind of closure is contingent on a premise, and a
portfolio that does not separate the two loses exactly the information it needs: which settled
questions may never be re-litigated, and which are one measurement away from reopening.**

The corollary is the operational half, and it is the half that costs money when it is missing. A
permanent closure **must carry no reopening trigger** — putting one beside it invites a future reader
to wait for a capability that could not change the answer. A contingent closure **must name the
observation that would reopen it**, in words specific enough to search for. Filing either as the
other is a defect, and this paper reports one of each direction from its own record.

The seven routes below are the worked examples. Six of them are ordinary; the seventh, 6-mercaptopurine,
is the one worth the reader's time, because **its closure was filed at the most permanent grade in the
vocabulary and its premise was later measured false.** A negative record that omits its own retracted
negative is not a negative record.

---

## 2 · Why this is publishable at all

Three reasons, none of them consolation.

1. **The field publishes almost none of them.** A route that a group considered and abandoned on
   argument leaves no trace, so the next group repeats the reasoning from scratch — and, more often,
   repeats it *incompletely*, because the discriminating fact is usually one line in a 1996 paper or
   one column of a sequence alignment.
2. **Closures are the cheapest deliverable a computation-only program has.** Every route here was
   closed for $0. On the axis of *what do we still hold if no experiment ever happens*, a completed
   closure scores higher than a hypothesis: it is finished, it needs nobody's cooperation, and it does
   not decay ([`emc-post-degrader-options.md` §2, Tier 4](../program/emc-post-degrader-options.md#2--the-ranked-list)).
3. **The taxonomy transfers even where the biology does not.** Nothing in §3 is specific to a fusion
   sarcoma. Any target-selection program that keeps a route register faces the same question — *may
   this row ever be reopened, and by what?* — and the same failure modes when it answers by prose
   instead of by an enumerated field.

---

## 3 · The taxonomy — nine closure kinds, two of them permanent

**Adopted, not invented.** The enumeration below is
[`systems/graph/integrity.json` → `_closure_model.kinds`](../../../systems/graph/integrity.json), which
is the single home of these definitions and of the `permanent` / `needs_trigger` flags. The reason it
is an enumerated field rather than prose is recorded there. It is worth quoting, because it is the
whole design brief: *"AI methods are advancing fast, so many currently-closed paths WILL be unblocked
— and a register that files a permanent fact about a sequence alongside a limitation of today's
free-energy engine loses exactly the information needed to know which is which."*

| kind | permanent | must name a trigger | what it means |
|---|---|---|---|
| `definitional` | **yes** | no | a fact about what the objects ARE — e.g. a residue the paralogues share cannot discriminate between them |
| `arithmetic_over_fixed_fact` | **yes** | no | an arithmetic consequence of a fixed measured fact. Never revivable |
| `premise_false` | no | **yes** | a stated premise was measured and is not true. Revivable only if the measurement or the underlying fact changes |
| `confound_in_the_system` | no | **yes** | the TEST SYSTEM cannot answer it. Revivable by a *different* test system, not by a better method and not by more sampling |
| `unregenerable_artifact` | no | **yes** | the specific RESULT is unrecoverable forever while the QUESTION is open. The trigger re-answers the question; it never recovers the result |
| `instrument_limit` | no | **yes** | the method cannot resolve it *today* — the most revivable kind, and the one most of this program's own failures fall into |
| `authorization` | no | **yes** | waiting on a person, not on nature |
| `cost` | no | **yes** | waiting on a budget, not on nature |
| `open` | n/a | n/a | not closed at all |

### 3.1 · The two-question test that assigns a kind

Applied in order, and the first question is the one that is usually skipped:

1. **Could the closing statement be false while every object stayed what it is?**
   If **no** — the statement is about what the things *are* — it is `definitional`.
   If **yes**, continue. *(This question is what separates "a ligand for a shared region cannot
   discriminate among the things that share it" from "this shared region's protein is more essential
   than that one's". The first is about the objects; the second is a measurement, and it can move.)*
2. **Does the closure follow from a measured quantity by arithmetic alone, such that no future
   development changes the quantity?**
   If **yes** — a sequence identity, an exon boundary, a copy count in a deposited structure — it is
   `arithmetic_over_fixed_fact`.
   If **no**, the closure rests on a *premise*, and the remaining kinds sort it by what the premise
   depends on: a measurement (`premise_false`), the test system (`confound_in_the_system`), a lost
   artifact (`unregenerable_artifact`), today's methods (`instrument_limit`), a person
   (`authorization`), or money (`cost`).

### 3.2 · The discipline the taxonomy imposes

- **A permanent kind may carry no reopening trigger, and this is enforced rather than encouraged.** A
  blocker declared permanent cannot simultaneously name a technology that would retire it; the
  repository's checker fails the build on that combination, with the reasoning *"a fact about what the
  objects ARE is not waiting on a capability"* ([`systems_check.py` `check_blockers`](../../../systems/systems_check.py)).
- **A contingent kind must name a trigger specific enough to search for.** The registry's own rule is
  that the trigger string has to name a method, benchmark, artifact, measurable quantity or capability
  and may not lean on a bare comparative — *"better X"* is not a trigger
  (`_closure_model._specificity_rule`).
- **One fact may not be permanent on one route and contingent on another.** This sounds like
  bookkeeping and is not: §4.5 is a route that was re-filed for exactly this reason.

---

## 4 · The seven routes, placed

**Five of the seven** inherit `BLK-NOT-FUSION-SELECTIVE`, a blocker filed
`fundamental_biological_limit` — *the route also engages the wild-type protein* — and they are
RT-EWSR1-PROTEIN, RT-FET-LC-LIGAND, RT-DBD, RT-SYNPROMOTER and RT-6MP. That is the shape of the whole
problem: **EWSR1::NR4A3 is a chimera of two things that normal cells also contain**, so every route
that reaches for one half, or for a feature both halves share with something else, inherits a
discrimination problem it did not create. Those five closures are one observation applied to five
different surfaces — the partner half, the shared low-complexity region, the paralogue-shared zinc
finger, the shared response element, and a coactivator-recruiting domain present identically in the
wild-type receptor. The remaining two, RT-RXR and RT-HDAC-BET, close on different grounds and inherit
that blocker not at all.

| # | route | closure kind | permanent | what reopens it |
|---|---|---|---|---|
| 1 | [RT-EWSR1-PROTEIN](../../../systems/views/L2-rt-ewsr1-protein.md) — target the EWSR1 half at the protein level | `definitional` | **yes** | nothing |
| 2 | [RT-FET-LC-LIGAND](../../../systems/views/L2-rt-fet-lc-ligand.md) — a ligand for the shared FET low-complexity half | `definitional` | **yes** ⚠ see §4.1 | nothing, on the leg that carries the permanence |
| 3 | [RT-DBD](../../../systems/views/L2-rt-dbd.md) — relocate to the DNA-binding domain | `arithmetic_over_fixed_fact` | **yes** | nothing |
| 4 | [RT-RXR](../../../systems/views/L2-rt-rxr.md) — RXR-heterodimer modulation | `premise_false` | no | a contradicting primary measurement, named |
| 5 | [RT-SYNPROMOTER](../../../systems/views/L2-rt-synpromoter.md) — fusion-driven synthetic promoter → suicide gene | `premise_false` | no | an EMC dataset reading the fusion's binding specificity |
| 6 | [RT-HDAC-BET](../../../systems/views/L2-rt-hdac-bet.md) — epigenetic agents to lower fusion expression | `premise_false` | no | EMC data replacing a sarcoma-wide transfer prior |
| 7 | [RT-6MP](../../../systems/views/L2-rt-6mp.md) — 6-mercaptopurine / AF-1 agonism | `premise_false` | no ⚠ **was filed `definitional`** — §5 | a primary direction-of-effect measurement on the fusion |

⚠ **Two honesty notes on the table, both from the register rather than from this paper.** **Four of the
seven carry route *state* `parked`, not `closed`** — RT-HDAC-BET, RT-RXR, RT-SYNPROMOTER and RT-6MP,
each with a `monitor` recommendation. What is closed in those four is the **claim**, not the route, and
§4.6 states the difference. ⭐ **The `permanent` column and the route state therefore agree across all
seven rows**: the three permanent closures are exactly the three routes recorded `closed`, and the four
revivable ones are exactly the four recorded `parked`. RT-SYNPROMOTER's work state is `future`; it
was never started, and closing an unstarted route is a legitimate act only because the closing premise
is about the disease rather than about the effort.

### 4.1 · The definitional pair — and the class of argument they instantiate

**RT-EWSR1-PROTEIN** and **RT-FET-LC-LIGAND** close on one sentence in two costumes: *a handle defined
by a feature the tumour shares with normal cells cannot discriminate for the tumour.*

- The EWSR1 half of the fusion **is wild-type EWSR1 sequence**, so a ligand for it engages wild-type
  EWSR1 by construction. The closure is a statement about what the object is, and no method advance,
  dataset or capability reopens it.
- The shared FET low-complexity region is the same statement at class scope: all three of EMC's common
  fusions carry a FET low-complexity domain, which is what makes a ligand for it attractive — the
  widest possible coverage, sidestepping the NR4A family entirely — and is *also* precisely why it
  cannot discriminate. The low-complexity region is present breakpoint-independently
  ([`fusion-object-inventory.json`](../../modalities/fusion-object-inventory.json)).

**Registering both separately is deliberate and is not duplication.** They are reached from different
directions — one targets EWSR1 *as EWSR1*, the other targets the low-complexity region *as a shared
class feature that happens to be EWSR1 sequence* — and a register that collapsed them would answer
only the question that was asked first. That two independent entry points land on one closure is what
makes this a **class of argument rather than a one-off**, which is the single most reusable thing in
this paper: the same test applies to any fusion-directed programme reaching for the partner half.

⛔ **The scoping is load-bearing and must travel with the closure.** This closes targeting the EWSR1
half **on its own**. It does **not** close a coincidence-detection ("AND-gate") design whose logic
requires both arms in cis, and it does **not** close the junction routes, which act on a sequence
wild-type EWSR1 does not have. A closure quoted without its scope becomes a closure of things it never
touched.

⚠ **And one leg of RT-FET-LC-LIGAND's grade is *not* definitional, which its own record says.** The
grade reads *"relocates selectivity somewhere worse"*, and the comparative rests on a DepMap
essentiality trade — wild-type EWSR1 at gene effect ≈ −1.2 against NR4A1/NR4A2 dependency fractions
below 1% ([`depmap-insilico-findings.md`](../../modalities/depmap-insilico-findings.md), a **surrogate
cell-line read, not EMC data**). This repository does not otherwise treat *"engages an essential
protein"* as fatal by construction — a proteasome-inhibitor route is filed `ready` on a pan-essential
target, and a RIPTAC route is parked rather than closed on a deliberately essential-protein mechanism.
So **the permanence rests on the shared-region leg alone**, and whether *"worse"* should be dropped from
the grade is recorded as open ([`AUDIT-2026-08-06-routes.md` X11](../../../systems/AUDIT-2026-08-06-routes.md)).
That is not a caveat added for modesty; it is the §3.1 test applied honestly, and it changes what the
sentence may be quoted for.

### 4.2 · The arithmetic closure — RT-DBD

The intuitive move on a transcription-factor fusion is *"it works through DNA binding, so block DNA
binding."* For this target it lands on the **worst available place to stand**, and that follows from a
sequence identity by arithmetic.

| region | NR4A3 vs NR4A1 | NR4A3 vs NR4A2 |
|---|---:|---:|
| zinc-finger window (69 aligned columns) | **92.8 %** | **98.6 %** |
| ligand-binding domain (254 aligned columns) | **59.4 %** | **67.3 %** |

One home for these values, computed from cached UniProt sequences:
[`target-route-census.json`](../../modalities/target-route-census.json) → `zinc_finger_window.identity`
and `paralogue_identity_by_domain`; the reasoning is owned by
[`target-route-options.md` route 12](../program/target-route-options.md). The artifact's own limits are
explicit — *percent identity only; no structure, affinity, reach, reactivity or degradation quantity
is computed* — and that is all the closure needs.

Moving the target from the LBD to the zinc finger makes the paralogue discrimination problem
**strictly harder**, monotonically, by a quantity that no future development changes. A sequence
identity is not a measurement that a better instrument re-reads; it is arithmetic over two fixed
strings. The route additionally has a functional analogue of the same problem — the whole NR4A family
binds the same NBRE/NurRE response elements — so the *functional* site is shared as well as the
sequence, but that observation is a corroboration and the closure does not need it.

**Why this is the cleanest case in the register.** It is the only one of the seven where a reader who
disagrees can be handed a single number and asked which direction they think it points.

### 4.3 · Closed on a published primary measurement — RT-RXR

Nuclear receptors commonly act as RXR heterodimers, and rexinoid pharmacology is the one place this
receptor family already has a working ligand handle. **NR4A3/NOR-1 does not form heterodimers with
RXR, unlike NR4A1 and NR4A2** — quoted rather than paraphrased, because the whole closure turns on it:
*"Nor1 is unable to promote RXR signaling due to its inability to form heterodimers with RXR"*
([Zetterström et al., *Mol Endocrinol* 1996;10:1656–66, PMID 8961274](https://pubmed.ncbi.nlm.nih.gov/8961274/);
registered as `EV-ZETTERSTROM-1996`). The paper's own title is that RXR heterodimerisation
*distinguishes* the three family members. **So the single solved pharmacology in this family is the one
place our paralogue is absent from.**

This is `premise_false` and deliberately **not** `definitional`, and the distinction is exactly §3.1's
first question: the statement *could* be false while every object stayed what it is, because it is a
measurement rather than a fact about composition. **Only a contradicting primary measurement of the
same fact reopens it — no method advance does**, which is why the route carries a trigger and why the
trigger names an observation rather than a capability.

The measurement transfers from wild-type NOR-1 to the chimera because the LBD is byte-identical in both
and the fusion alters only the N-terminal region — a transfer stated on the route's own evidence row
rather than assumed silently.

⭐ **The trigger was checked rather than asserted, and the check was free.** The route's revival
condition had previously been recorded as *"the published negative stands unchanged"* — an assertion
with no reading behind it — while a 2025 primary paper on that exact question sat unread in the
committed literature-target list. It was read: it studies **Nurr1–RXRα and Nur77–RXRγ only**, i.e. the
two paralogues that *do* heterodimerise. The negative stands, and it is now a reading rather than an
assumption ([`AUDIT-2026-08-06-routes.md` → RT-RXR](../../../systems/AUDIT-2026-08-06-routes.md)). **A
trigger that is never checked is a closure with a decorative escape hatch.**

### 4.4 · Closed on a premise about this disease — RT-SYNPROMOTER, and the reason it is the reopenable example

A synthetic promoter driven by the fusion, wired to a suicide gene, is the most elegant idea in the
search, and it has been built in the sibling disease. In Ewing sarcoma, EWSR1::FLI1 has **neomorphic**
DNA binding — it activates GGAA microsatellites that wild-type FLI1 does not — so a GGAA-based cassette
is active only where the fusion is. Both an enhancer-based expression cassette and a GGAA-driven
HSV-TK/ganciclovir construct have been reported
([`emc-post-degrader-options.md` route 14](../program/emc-post-degrader-options.md#route-14---the-fusion-driven-synthetic-promoter-and-the-precise-reason-emc-is-a-harder-case-than-ewing)
holds both citations).

**EWSR1::NR4A3 retains NR4A3's own zinc-finger DBD and binds the same NBRE/NurRE elements the wild-type
paralogues bind.** An NBRE cassette would therefore fire in any cell with active NR4A signalling. What
the fusion changes is **transactivation potency, not binding site** — which makes the achievable
discrimination a **gradient rather than a switch**, and a gradient is the wrong basis for a suicide
gene.

Two things make this the paper's example of a closure that is **not** permanent:

- **It rests on a premise about EMC, and the premise is under-measured rather than refuted.** The
  route's own `remaining_unknowns` says so in as many words: what is open is *whether the absence of a
  neomorphic binding element is firmly established, or merely unmeasured in EMC* — and that is the
  sentence that distinguishes a closed route from a data-blocked one. The named reopening observation
  is a direct read of the fusion's DNA-binding specificity in EMC; no instrument for it is built here.
- **The reason it fails is itself a result.** The finding *"EMC's fusion reads a normal NR4A response
  element, not a neomorphic one"* is a statement about this disease worth a paragraph in the literature
  even though the route is not worth a programme. A closure can have a publishable positive inside it.

### 4.5 · Closed on a transfer prior — RT-HDAC-BET, and the consistency rule that re-filed it

Lowering the expression of the driver with a broad epigenetic agent is not fusion-selective by
construction: the mechanism does not distinguish the chimera from anything else the drug class affects.
There is a direct sibling precedent for the *activity* — vorinostat lowers EWSR1::ATF1 expression in
clear cell sarcoma — and this repository's own DepMap read finds BET/CDK pan-essential with no
selectivity window.

**This route was filed `definitional` and was re-filed `premise_false` on 2026-08-06**, and the reason
is §3.2's third rule rather than any new biology. The closure names no fact about an object; it rests
on a **measurement** — [`depmap-sarcoma-dependency.json`](../../modalities/depmap-sarcoma-dependency.json)
— which is a **sarcoma-wide transfer prior, not EMC data**. A second route in the register rests on the
*same artifact and the same sentence* and was filed `premise_false` with two triggers. **One artifact
cannot be a permanent definitional fact on one route and a revivable measured premise on another**, so
one of the two filings had to move, and the one that moved is the one whose grounds were a
measurement ([`AUDIT-2026-08-06-routes.md` X24](../../../systems/AUDIT-2026-08-06-routes.md)).

⛔ **Scope, which the grade previously got wrong.** What is closed is the **fusion-selectivity** claim.
Non-selective activity of these classes in EMC is **explicitly not closed**, and the repository holds a
fact-checked ex-vivo result pointing the other way: a 221-drug high-throughput screen on the
patient-derived line NCC-EMC1-C1 returned romidepsin and panobinostat among its low-IC50 hits
([Iwata et al., *Human Cell* 2025, PMID 40580361](https://doi.org/10.1007/s13577-025-01250-7); the
verification is logged in [`fact-check-log.md`](./fact-check-log.md)). The route's earlier grade said
*"not an EMC result"*, which was false of that screen; it now says *"not a fusion-SELECTIVITY result"*,
which is the claim actually closed. **A closure that overstates its own scope is the fastest way to
lose a live option**, and this one nearly took an ex-vivo signal down with it. Nothing here asserts
activity, benefit or tolerability in a patient — the ex-vivo hit is named to bound the closure, not to
recommend anything.

### 4.6 · The state a closure is filed under is not the same as the closure

RT-HDAC-BET, RT-RXR, RT-SYNPROMOTER and RT-6MP each carry `status: parked` with a `monitor`
recommendation while the claim this record closes is closed; the three permanent closures carry
`status: closed` and no recommendation to revisit. **A route's work state, its closure kind and its
authorization state are three orthogonal axes**, and the register keeps them apart on purpose —
RT-SYNPROMOTER is `work_state: future` and was never started while RT-RXR is `work_state: complete`,
and both sit under the same `premise_false` kind. The closure kind answers *may
this ever be reopened, and by what*; it does not by itself say whether anyone is watching, and the
watch list is a separate object with separate triggers.

⚠ *Superseded, retained (CLAUDE.md rule 1.2): "RT-SYNPROMOTER carries `status: closed` with a `monitor`
recommendation because two of its blockers are technology-gated." That was the register's reading until
2026-09-02, when AUT-PD-088 corrected it: `systems/CONVENTIONS.md` §4.1 defines `closed` as carrying no
trigger that would reopen the route, and RT-SYNPROMOTER named two technologies and a revival trigger.
RT-RXR and RT-6MP were mis-filed the same way and moved with it. **No closure kind, no permanence
verdict and no claim in this record changed** — only the state field the register files them under.*

---

## 5 · The instructive failure — RT-6MP, a closure whose premise was measured false

This route is in the paper because it went wrong, and because the way it went wrong is the strongest
argument for the taxonomy in §3.

### 5.1 · What was filed

6-mercaptopurine is the one **approved** drug reported to activate NR4A3, acting through the
N-terminal AF-1 rather than the ligand-binding domain. Verbatim: *"the N-terminal AF-1 domain
delimited to between amino acids 1 and 112, preferentially recruits the steroid receptor coactivator (SRC)… SRC-2
modulates the activity of the AF-1 domain but not the C-terminal ligand binding domain (LBD)"*
([Wansa et al., *J Biol Chem* 2003;278(27):24776–90, PMID 12709428](https://pubmed.ncbi.nlm.nih.gov/12709428/);
`EV-WANSA-2003`). That made it, in the repository's own words, *"the cheapest imaginable entry."*

It was closed on 2026-08-03 with this reasoning, filed `closure_kind: definitional` — **permanent, no
revival trigger, never retry**:

> *"NOR-1 residues 1–112 sit inside the 1–260 stretch the fusion REPLACES with EWSR1-LC — a ligand
> whose mechanism lives in a domain the disease DELETES cannot act on the chimera at any dose."*

**That premise is false, and this document does not repeat it as anything other than a retraction.**

### 5.2 · What was measured

NR4A3's canonical transcript ENST00000395097 has eight exons, six of them coding. **Transcript exons 1
and 2 are entirely non-coding** — `coding_nt_in_exon: 0` for both, `first_transcript_exon_is_coding:
false` — so the literature's *"NR4A3 exon 3"* **is protein residue 1**
([`nr4a3-exon-audit.json`](../../modalities/nr4a3-exon-audit.json), Ensembl REST, run in CI for $0). An
independent gene model built for a different purpose agrees: NR4A3's 5′ UTR on the same transcript is
**699 nt**, long enough to consume two whole exons
([`emc-fet-construct-designs.json`](../../modalities/emc-fet-construct-designs.json) →
`gene_models.NR4A3.utr5_len`).

Consequently `EWSR1(1–264)::NR4A3(1–626)` **retains the AF-1, the DBD, the hinge and the LBD**, and
**EWSR1's low-complexity region is additive, not a replacement.** The retention is not an artifact of
one assumed breakpoint: of 18 arithmetically possible junctions across the declared exon windows, 9
retain an intact C4 zinc-finger DBD — the filter the fusion's own documented DBD-dependent function
requires — and **all 9 retain the AF-1**
([`fusion-object-inventory.json`](../../modalities/fusion-object-inventory.json) →
`plausible_breakpoints`). The independent literature agrees at the exon level: the common type-1
transcript is reported as EWSR1 exons 1–12 fused to **NR4A3 exons 3–8**, and a rare isoform is
described as splicing into a cryptic exon *"prior to the NR4A3 ATG"* — both of which place the start
codon in exon 3 (`EV-PMC6766969`, `EV-PMC3335514`).

⭐ **A third, independent source states the retention directly rather than at the exon level, and it was
found by accident (2026-08-08).** Huang SC et al., *Mod Pathol* 2023 (PMID 36948401,
doi 10.1016/j.modpat.2023.100161) — a 15-institution Taiwanese EMC series read for an entirely different
purpose, the per-partner outcome counts folded into
[`emc-fusion-partner-stratification.md`](../fusion-partner/emc-fusion-partner-stratification.md) — describes the *NR4A3*
fusions as containing **"the transactivation domain of the N-terminal partners and the whole coding sequence
of NR4A3"**. *The whole coding sequence* is the same statement as "NR4A3 is retained from residue 1", reached
with no exon arithmetic at all, by pathologists describing the fusion rather than by a gene-model computation.
**That is corroboration of a different kind from the two above, which is why it is worth recording:** the
exon-level literature agreement and the Ensembl audit are both *coordinate* claims and could in principle
share a coordinate error; a prose statement about protein content cannot. ⚠ Read from the published PDF by a
human, because the publisher's edge returns HTTP 403 to automated fetchers while designating the same PDF free
— provenance in [`emc-fusion-partner-pooling.json`](../fusion-partner/emc-fusion-partner-pooling.json) → `citations.huang2023`.
⚠ And it corroborates the **retention**, not any particular patient-level breakpoint: the caveat immediately
below is untouched by it.

⚠ **What this does not settle**, stated because the artifacts state it: the *patient-level* breakpoint
is not pinned by exon arithmetic, and only a primary breakpoint report can pin it. The claim above is
therefore conditional in a way that is stronger than it sounds — **the AF-1 is retained under every
junction that retains the DBD**, and a junction that does not retain the DBD is incompatible with the
fusion's reported transactivation of a PPARG-promoter response element (`EV-FILION-2009`).

### 5.3 · The part that should be uncomfortable

**The repository had already resolved this on 2026-08-02 — one day before the closure was written —
inside the very artifact the closure cites.**
[`target-route-census.json`](../../modalities/target-route-census.json) →
`fusion_model_disagreement.resolution` reads *"NR4A3 exon 3 begins at residue 1 … the chimera retains
the AF1, the DBD, the hinge and the LBD."* The closure cited a different section of the same file — a
lysine/cysteine composition count — and never reached the two rows below it that resolved the junction
the other way.

So the failure was not a missing measurement. **The measurement was present, committed, and cited by
the wrong index.**

### 5.4 · The second-order damage

The taxonomy in §3 carried two worked examples of `definitional`, and one of them **was this route** —
`integrity.json`'s definition literally read *"a ligand whose mechanism lives in a domain the disease
deletes."* From the day that vocabulary was written until the correction on 2026-08-06, **it was
teaching the refuted case as its canonical one**, which means the defect was not confined to the route
that had it: any new route reasoning by analogy to the definition would have inherited it. The example
has been removed; the paralogue-shared-residue example beside it holds and is sufficient.

### 5.5 · What now closes the route, and why it is weaker in grade and stronger in argument

Two grounds survive, and the second is one the record never made:

1. **6-MP is not fusion-selective.** Retention is precisely what makes this bite: an AF-1 present in
   the chimera is *identically* present in wild-type NR4A3, so nothing about the drug distinguishes
   them.
2. ⭐ **Direction of effect.** 6-MP **enhances** NR4A3 activity
   ([`published-warhead-registry.json`](../../modalities/published-warhead-registry.json) →
   `mercaptopurine_6`, sourced to Zaienne et al., *ChemMedChem* 2022, `EV-ZAIENNE-2022`), and
   EWSR1::NR4A3 is a transcriptionally active **gain-of-function** oncoprotein. An agent that enhances
   the receptor is therefore a candidate **agonist of the oncoprotein**, which is a stronger objection
   than the one on file.

**And it is filed `premise_false`, not `definitional`, because it rests on a prior rather than a
demonstration** — no direct loss-of-function experiment for 6-MP on this fusion exists in any EMC cell
line. The route accordingly carries a named reopening observation: a primary measurement of 6-MP's
direction of effect **on the fusion**, not on wild-type NR4A3.

⚠ **The correction also opened a question that did not exist before.** In the chimera the AF-1 is
**internal** — preceded by EWSR1(1–264) and neighbouring a strong independent activation domain — and
whether an internalised AF-1 remains SRC-2-competent and 6-MP-responsive is untested. That is a bench
question, and it is recorded as one.

⛔ **Scope.** This closes **6-MP**. It does not close LBD-directed modulation of this receptor, which
is a different mechanism graded on different instruments, and the register carries that distinction as
an explicit *"not to be confused with"* row precisely so the closure cannot be quoted past its reach.

### 5.6 · The three rules this incident produces

1. **The most permanent grade demands the strongest provenance.** A `definitional` filing asserts that
   no future development can change the answer. It must rest on a fact about the objects that can be
   **re-derived from a committed artifact**, and the re-derivation must be *run*, not remembered.
2. **Citing an artifact is not reading it.** The closure cited the right file and the wrong section. A
   citation records where the answer lives; it is not evidence that anyone looked.
3. **A vocabulary's examples are load-bearing.** Definitions in a controlled vocabulary get copied by
   analogy, so a refuted example propagates further and faster than a refuted route.

---

## 6 · The two directions a mis-filing can go, and what each costs

| direction | what it looks like | what it costs |
|---|---|---|
| **Filed too permanent** (`definitional` on a contingent premise) | RT-6MP §5 — closed forever, no trigger, on a premise the repository's own artifact refuted | the cheapest available entry point was struck off the board with a "never retry" flag, and the reasoning propagated into the vocabulary that grades every other route |
| **Filed too contingent** (a permanent closure carrying a trigger) | a permanent blocker sitting beside a reopening condition | a settled question stays on a watch list, so scans keep returning to it and a reader concludes the question is live. The repository's checker fails the build on this combination |

**Both are failures of the same kind: a state that misrepresents whether the future can change the
answer.** That is why the field is enumerated rather than prose. Prose about permanence reads as
confident in both directions and is checkable in neither.

---

## 7 · What this record does not claim

- **No efficacy, tolerability, therapeutic-window or clinical claim is made or implied**, for any agent
  or route named here, closed or open. Where an approved drug appears — 6-mercaptopurine, an HDAC
  inhibitor, a rexinoid — it appears as the subject of a *mechanistic* argument about a fusion protein,
  never as a suggestion.
- **A closed route says nothing about whether this disease can be treated.** It says one surface is not
  the way. Seven closures are seven surfaces.
- **No route here was closed by an experiment in this disease**, and none of the closures should be
  read as one. Where a closure rests on a measurement it is someone else's measurement (RT-RXR) or a
  computed read of public sequence and dependency data (RT-DBD, RT-HDAC-BET, RT-6MP).
- **Two of the closures rest partly on surrogate cell-line data that is not EMC data** — RT-FET-LC-LIGAND's
  *"worse"* comparative and RT-HDAC-BET's selectivity-window read — and neither surrogate carries the
  permanence of its route.
- **The patient-level fusion breakpoint is not pinned here.** §5.2's retention claim is conditional on
  the DBD filter and is stated as such.
- **This paper computed nothing.** It is a reading of committed artifacts, route records and cited
  primary sources.

---

## 8 · How to check every claim, for $0

| claim | where it can be checked |
|---|---|
| the closure vocabulary, its `permanent` / `needs_trigger` flags, and the trigger-specificity rule | [`systems/graph/integrity.json`](../../../systems/graph/integrity.json) → `_closure_model` |
| each route's state, grade, closure kind, closure note and trigger | [`systems/graph/routes.json`](../../../systems/graph/routes.json); rendered per route as `systems/views/L2-rt-*.md` |
| a permanent blocker may not name a retiring technology | [`systems/systems_check.py`](../../../systems/systems_check.py) → `check_blockers` `[B1]` |
| zinc-finger vs LBD paralogue identity | [`target-route-census.json`](../../modalities/target-route-census.json) → `zinc_finger_window.identity`, `paralogue_identity_by_domain` |
| NR4A3 exons 1–2 are non-coding; exon 3 encodes residue 1 | [`nr4a3-exon-audit.json`](../../modalities/nr4a3-exon-audit.json) |
| the same retention, stated as protein content by an independent source rather than as coordinates | Huang SC et al., *Mod Pathol* 2023, PMID 36948401 — *"the transactivation domain of the N-terminal partners and the whole coding sequence of NR4A3"*; provenance in [`emc-fusion-partner-pooling.json`](../fusion-partner/emc-fusion-partner-pooling.json) → `citations.huang2023` |
| NR4A3's 5′ UTR is 699 nt on the same transcript — the independent corroboration | [`emc-fet-construct-designs.json`](../../modalities/emc-fet-construct-designs.json) → `gene_models.NR4A3.utr5_len` |
| the junction resolution that predated the RT-6MP closure by one day | [`target-route-census.json`](../../modalities/target-route-census.json) → `fusion_model_disagreement.resolution` |
| AF-1 retained in all 9 DBD-retaining breakpoint windows; the FET low-complexity region present breakpoint-independently | [`fusion-object-inventory.json`](../../modalities/fusion-object-inventory.json) → `plausible_breakpoints` |
| 6-MP enhances NR4A3 activity and does not bind the LBD | [`published-warhead-registry.json`](../../modalities/published-warhead-registry.json) → `mercaptopurine_6` |
| wild-type EWSR1 essentiality as a surrogate cell-line read | [`depmap-insilico-findings.md`](../../modalities/depmap-insilico-findings.md) |
| the BET/CDK sarcoma-wide dependency read behind RT-HDAC-BET | [`depmap-sarcoma-dependency.json`](../../modalities/depmap-sarcoma-dependency.json) |
| the Iwata 2025 221-drug screen hits, as fact-checked | [`fact-check-log.md`](./fact-check-log.md) |
| the RT-6MP premise correction and the RT-HDAC-BET re-filing, with their reasoning | [`systems/AUDIT-2026-08-06-routes.md`](../../../systems/AUDIT-2026-08-06-routes.md) X9, X11, X24 |
| every cited paper's canonical identifiers and aliases | [`systems/graph/evidence.json`](../../../systems/graph/evidence.json) |
| the program-side dead/parked/held register these routes are also filed in | [roadmap §6](../nr4a3-program-map.md#6--the-closed-route-register) |

---

## 9 · What is missing, stated rather than left implicit

- **Two grade-level questions are open and are not resolved here**, because they are scientific calls
  rather than editorial ones: whether *"relocates somewhere worse"* should be dropped from
  RT-FET-LC-LIGAND's grade or the closure re-filed as non-permanent
  ([X11](../../../systems/AUDIT-2026-08-06-routes.md)), and whether RT-6MP should stay closed on
  direction of effect or be reopened as `parked` pending the internalised-AF-1 question
  ([X9](../../../systems/AUDIT-2026-08-06-routes.md)). **This paper reports both as open and takes
  neither.** If the second is decided the other way, RT-6MP stops being a closure and this paper's §5
  becomes a section about a *retracted* closure, which is a smaller claim and still a true one.
- **The revival triggers are ids, not searchable strings.** The four contingent routes name triggers
  such as `TR-NR4A3-DIRECTION-OF-EFFECT`, and the reopening *conditions* are carried in prose on the
  route pages rather than in a trigger registry a scan could read verbatim. The specificity rule in §3.2
  is therefore satisfied by the prose and not by the identifier.
- **No route here was reopened by anything.** The register has never yet exercised the reopening path,
  so the discipline in §3.2 is a design that has been enforced but not tested by a real revival.
- **The route population is this repository's**, forty routes enumerated by one programme with no wet
  lab. A different search would have closed a different seven, and the taxonomy is the transferable
  part rather than the list.

---

## 10 · References

Primary literature is registered with canonical identifiers in
[`systems/graph/evidence.json`](../../../systems/graph/evidence.json); the ids below resolve there.

- **`EV-ZETTERSTROM-1996`** — Zetterström RH et al. *Mol Endocrinol* 1996;10:1656–66. PMID
  [8961274](https://pubmed.ncbi.nlm.nih.gov/8961274/). RXR heterodimerisation distinguishes NR4A1/NR4A2
  from NR4A3. *(§4.3)*
- **`EV-WANSA-2003`** — Wansa KDSA et al. *J Biol Chem* 2003;278(27):24776–90. PMID
  [12709428](https://pubmed.ncbi.nlm.nih.gov/12709428/). NOR-1's AF-1 delimited to residues 1–112;
  SRC-2 modulates AF-1 and not the LBD. *(§5.1)*
- **`EV-ZAIENNE-2022`** — Zaienne D, Arifi S, Marschner JA, Heering J, Merk D. *ChemMedChem*
  2022;17(16):e202200259. 6-MP enhances NOR-1 activity via AF-1 and does not bind the LBD. *(§5.5)*
- **`EV-FILION-2009`** — Filion C et al. (2009), PMC4429309. The fusion transactivates a PPARG-promoter
  response element — a DBD-dependent function, and the basis of the DBD filter. *(§5.2)*
- **`EV-PMC3335514`**, **`EV-PMC4055444`**, **`EV-PMC6766969`** — exon-level definitions of the
  EWSR1::NR4A3 type-1 and type-5 transcripts, including *"EWSR1 (exons 1-12)-NR4A3 (exons 3-8)"* and a
  cryptic-exon isoform *"prior to the NR4A3 ATG"*. *(§5.2)*
- Iwata S et al. *Human Cell* 2025. PMID
  [40580361](https://doi.org/10.1007/s13577-025-01250-7). NCC-EMC1-C1 and its 221-drug screen. *(§4.5)*

The Ewing synthetic-promoter precedents cited in §4.4, and the MS0621 FET low-complexity ligand behind
§4.1, are held with their links by
[`emc-post-degrader-options.md`](../program/emc-post-degrader-options.md) routes 14 and 15 and are not
re-listed here.
