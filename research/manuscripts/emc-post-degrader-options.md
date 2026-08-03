# If the degrader does not deliver a candidate — the ranked alternatives

> **Role: decision memo, written to one question.** *"If the NR4A3 degrader paper ends up unable to
> deliver a good candidate — which is where it is trending — what are the next best routes to a
> **publishable EMC treatment candidate that a wet lab would actually test?**"* (trimcrae,
> 2026-08-03.) It ranks every route, including several this repo has never carried, on the axes that
> the degrader program's own failure record says matter.
>
> ⚠ **THE RANKING BELOW IS THE SECOND ONE. The first was graded on an axis that assumed a
> collaborator we do not have** — it scored the wet-lab ask on *cheapness*, which only matters if
> somebody exists who would run it. Corrected the same day: Axis W split into **W1 (is there a
> self-interested taker?)** and **W2 (the ask's size, conditional on W1)**, and **Axis D (what do we
> end up holding if the experiment never happens?)** was added, which is the axis that actually
> decides things for a programme that cannot execute. The superseded tiers are kept quotable in
> [§6](#6--appendix--the-superseded-ranking-and-what-was-wrong-with-its-axis) and registered in
> [STRATEGY.md Appendix B](../../STRATEGY.md#appendix-b--superseded-strategy-framings); **the live
> text carries only the corrected ranking.** ⚠ **Route NUMBERS are stable identifiers and did not
> change** — other files cite "route 1", "route 4" — so a route's number tells you which route it is
> and its **tier** tells you where it now ranks.
>
> **Subordinate to [`nr4a3-program-map.md`](./nr4a3-program-map.md)** (the roadmap owns the plan, the
> gates and the prices — nothing here restates one), to
> [`emc-treatment-strategy.md`](./emc-treatment-strategy.md) + [`../IDEAS.md`](../IDEAS.md) (the route
> portfolio) and to [`target-route-options.md`](./target-route-options.md) (the *target* axis). Where
> any of them conflicts with this memo on a plan or an ordering, **they win.** This memo's
> contribution is the **post-failure** axis, which none of them carries: what survives when the
> instrument that was supposed to prove selectivity has failed three times.
>
> **$0.** No GPU, no rental, no wet lab. Every literature claim is fetched and quoted from a
> committed corpus ([`lit-targets-emc-post-degrader.json`](./lit-targets-emc-post-degrader.json) →
> `literature-cache` branch, 33 of 38 targets at HTTP 200 — the 5 misses are publisher paywalls,
> named in §5); every public-data number is computed by [`fet_ddr_axis_scan.py`](../modalities/fet_ddr_axis_scan.py) →
> [`fet-ddr-axis-scan.json`](../modalities/fet-ddr-axis-scan.json), **committed on `main`** (it used to
> exist only on `modalities-cache`, so every relative link here was broken and every number below was
> quoted off a branch — CLAUDE.md §7 harm #1, fixed 2026-08-03 by porting the artifact and by making
> `depmap-dependency.yml` publish to the branch it was dispatched from as well as to the cache).
> **Nothing here is a molecule, a dose, an efficacy claim or a statement about activity or
> tolerability in a patient**, and none is implied.

---

## 0 · The finding that reorganises the whole list, stated first

**Every one of the degrader program's blocking failures is a property of the DEGRADER ARCHITECTURE,
not of the target.** That is not consolation, it is the ranking criterion. Read the four failures
([roadmap §WHERE WE ARE](./nr4a3-program-map.md#-where-we-are--the-scoreboard-in-plain-language) is
their one home) by *what they are about*:

| the failure | what it is a statement about | does it block a route that needs only a BINDER? |
|---|---|---|
| valB_mini wrong sign | alchemical **ternary** FEP | **no** — there is no ternary |
| SMARCA2/4 null | an **endpoint-MD selectivity** readout | **no** — no ΔΔG is being resolved |
| co-fold assembly, DockQ 0.023–0.046 | **ternary generation** | **no** — no second protein to place |
| NR-V04 discordant | a **paralogue-discrimination** positive control | only if the route needs paralogue discrimination |

And the roadmap's own arithmetic says why this is structural rather than a matter of trying harder: a
useful degradation window needs **~2.0 kcal/mol** of true margin against a resolvable difference of
**0.60** and an engine accuracy of **1.543 kcal/mol, wrong sign**
([MECHANISM-FIRST](./nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged)
owns those figures). A route whose central claim is *a free-energy difference between two similar
pockets* is asking this program for a measurement it has now failed to make four separate ways.

⭑ **So the asset and the liability separate cleanly, and they were being carried as one thing.**

- **The ASSET is the ligandable pocket** — an opened, state-matched cryptic NR4A3 LBD with docked
  de-novo binders and 33 exposed divergent surface handles. That survives every failure above intact.
- **The LIABILITY is the degradation geometry** — ternary, E3, exit vector, ubiquitin transfer, and a
  ~1 kcal/mol paralogue margin. That is what failed.

⛔ **And the field has just told us, in print, that the asset is the scarce half.** The flagship
demonstration of chemically-induced-proximity *rewiring* of a fusion TF —
[EB-TCIP on EWSR1::FLI1, JACS 2025](https://pubs.acs.org/doi/10.1021/jacs.5c05634) — could not use
the real oncoprotein. It had to tag it: *"Due to the dearth of EWSR1::FLI1-specific ligands, we have
used a N-FKBP12^F36V-EWSR1::FLI1 (FKBP-E::F) model system"*, and its own stated first limitation is
*"endogenous EWSR1::FLI1 will need to be recruited. Although there is a lack of ligands for
EWSR1::FLI1…"*. **EWSR1::NR4A3 is the FET fusion whose partner brings a real ligand-binding domain.**
Whatever else is true, that is the thing this program has and the field does not, and it should be
spent on modalities that need a binder rather than on the one modality that also needs a ternary.

---

## 1 · The four axes every route is graded on

A single tier number blends questions that do not move together — the mistake
[`emc-treatment-strategy.md`](./emc-treatment-strategy.md) already corrected for the portfolio. This
memo asks a narrower question than that capstone (*what produces a testable candidate now*), so it
uses axes of its own and reports each separately.

- **Axis P — what NEW evidence can we generate with no wet lab?** Not "can we argue for it" — can we
  *compute* something that did not exist before. This is the axis that decides whether a route yields
  a paper or an opinion.
- **Axis W1 — is there a plausible, SELF-INTERESTED taker?** Not *is the experiment cheap* but **does
  a specific group already exist that would want this result for their OWN reasons?** The calibrating
  example is route 1's: the FET/ATR authors published a partner-class argument spanning an **ETS**
  (FLI1), a **bZIP** (ATF1) and a **zinc-finger** (WT1) partner, and **EMC's NR4A3 is a nuclear
  receptor — the missing fourth class in their own argument.** Running it completes something they
  already own. That is a materially stronger position than *"please test our molecule"*, and it is
  the bar every route is graded against. ⚠ **Grade the taker, not the reagent** — a group that could
  in principle do it is not a group that wants to.
- **Axis W2 — the ask's SIZE**, and it is **conditional on W1**. A catalogue compound on a plate is a
  smaller ask than a bespoke synthesis, and that ordering is real — but **a cheap ask with no
  plausible taker scores worse than a moderate ask with a motivated one**, because an experiment
  nobody will run has no size. W2 is a tie-breaker within a W1 band, never a substitute for one.
- **Axis S — does it inherit the program's blockers?** Specifically: does its central claim reduce to
  a ~1 kcal/mol free-energy difference, does it need a generated ternary, and does it need
  NR4A-paralogue discrimination. **Three noes is the profile that survives.**
- **⭑ Axis D — what do we END UP HOLDING if the experiment never happens?** A complete published
  deliverable, or an unrun proposal. **This is the decisive axis under this programme's real
  constraint** and it is the one the first ranking lacked entirely. It is not a pessimism axis: it
  asks what the *expected* product of a route is, given that this programme can finish computation
  and writing and cannot finish an assay. A route whose in-silico half stands alone scores high; a
  route whose in-silico half is a preamble to somebody else's experiment scores low **however good
  that experiment is**.

⛔ **Why the axis set changed, stated once here so the tables do not have to.** trimcrae is a private
individual: **no lab, no institutional affiliation, no committed collaborator**, and paying four
figures for a contracted assay whose failure he could not interpret has been ruled out. The first
ranking's Axis W graded *"how cheap is this for whoever runs it"*, which silently assumes a
whoever. Cheapness is real but it is **conditional**, and the thing it was conditional on is what we
do not have. The full correction and the superseded tiers are in
[§6](#6--appendix--the-superseded-ranking-and-what-was-wrong-with-its-axis).

⚠ **What this memo deliberately does NOT decide: which of these an unaffiliated individual could
BUY.** That is a separate question with its own evidence — vendor policies, catalogue protein,
assay services, institutional-affiliation requirements — and it is being fetched into its own
corpora ([`lit-targets-civilian-purchasing.json`](./lit-targets-civilian-purchasing.json),
[`lit-targets-civilian-purchasing-b.json`](./lit-targets-civilian-purchasing-b.json)) rather than
guessed at here. **Nothing in W1/W2 above should be read as a claim about what is purchasable**;
where the two touch, the purchasing memo those corpora feed owns the answer and this one cites it.

⚠ **One standing constraint that no route escapes, so it is stated once here rather than in every
row.** EMC is indolent: **5-year OS 66–88 %, 10-year DSS ≈ 85 %, median time to metastasis ≈ 28
months**, and the best EMC-specific systemic result on record is pazopanib at **ORR 18 %, median PFS
19 months** ([Stacchiotti et al., *Lancet Oncol* 2019;20:1252–62, NCT02066285](https://pubmed.ncbi.nlm.nih.gov/31331701/),
as summarised by the 2025 review below). The same review states plainly: **"No clinically validated
agents directly target NR4A3"**
([Journal of Cancer Research and Clinical Oncology 2025, 10.1007/s00432-025-06316-5](https://link.springer.com/article/10.1007/s00432-025-06316-5)).
That is the gap and the bar together — an indolent disease with a 19-month PFS comparator means a new
agent is judged on disease control over a long horizon, and it means **no in-silico result is going
to look decisive against it.** What we can deliver is a *testable* candidate, and the honest framing
of every route below is that.

---

### ⭑ The trade-off this ranking makes, stated plainly so it can be overruled

**Tier 1 is now defined by what this programme can FINISH, not by what would be cheapest for someone
else to run.** Every Tier-1 entry is a document this programme can complete alone and post; every
Tier-2 entry is an *ask* — a specific experiment, a specific taker, a preregistration already
written. The two are separated because they fail differently: a deliverable's risk is that nobody
cites it, an ask's risk is that nobody runs it, and only the second risk is outside our control.

**What this costs, named rather than glossed.** Ranking on Axis D pushes the routes with the biggest
*ceiling* down. Route 1's cell panel, if run and positive, would be the first mechanistically-grounded
systemic hypothesis EMC has had — larger than anything in Tier 1 — and it is now Tier 2 not because
it got worse but because **we cannot cause it.** The ranking deliberately prefers a smaller certain
product to a larger contingent one. ⚠ **That preference is a judgement about the operating regime,
not about the science, and it flips if the regime changes**: a committed collaborator, an
institutional affiliation, or a funded model-holding group would move route 1's panel to the top of
the list on the same evidence. The asks are written so they are ready the moment that happens —
that is what Tier 2 is *for*, and it is why nothing is deleted.

⚠ **The one thing this reordering must not be read as.** Tier 2 is **not** a discard pile and the
Tier-1/Tier-2 boundary is **not** a claim that the asks are weak. Route 1's panel has the best W1 in
the portfolio and the smallest W2; it is simply not a thing this programme executes, and the previous
ranking obscured that by scoring its cheapness as if cheapness were ours to spend.

---

## 2 · THE RANKED LIST

⚠ **Read the tier, not the number.** Route numbers are stable identifiers carried over from the first
ranking and cited by other files; the **tier** is the rank. Where a route moved, the move is stated in
its row and the reason is one of the corrected axes (W1, W2 or D).

**Tier 1 — DELIVERABLES. Each is a complete, publishable product this programme can finish alone, at
$0, with nobody's cooperation. Ranked on Axis D first; W1/W2 do not apply, which is the point.**

| rank | # | route | P (what we compute) | D (what we hold if no experiment ever happens) | S |
|---|---|---|---|---|---|
| **1** | **3** | **The honest methods paper the degrader program has already earned** — ⭑ **was Tier 1 #3, now #1** | nothing new needed — the negative results *are* the result, and two further instruments failed their own known-answer tests on 2026-08-03 | ⭑ **the whole paper.** Its content is already computed, already preregistered, already red-teamed. It is the only route in this memo whose value **rises** as the degrader program's failures accumulate, and the only one that is finished when we stop typing | n/a — it is *about* the blockers |
| **2** | **2** | **Fusion-junction ASO / siRNA** *(already the repo's priority paper 2)* — ⭑ **held rank, and it is the route the reframe most clearly vindicates** | in-silico arc is complete: design → transcriptome-wide off-target → per-breakpoint favorability → gap-resolved cleavage-risk. The open GPU item (RNase-H1 cleavage-discrimination MD) is an upgrade, **not a gate on posting** | ⭑ **a complete red-teamed manuscript**, [`fusion-junction-aso-paper.md`](./fusion-junction-aso-paper.md) + [its red team](./fusion-junction-aso-paper-redteam.md). The delivery gate is stated honestly *inside* the deliverable rather than being a precondition for having one | **none of the three** |
| **3** | **1a** | **The in-silico ATR vulnerability assessment** — the COMPUTED half of route 1, separated from its ask; its module is [`emc_atr_vulnerability.py`](../modalities/emc_atr_vulnerability.py) | ✅ **done, and it cuts both ways** — the FET-IDR/RGG structural precondition computed from sequence, plus the public ATRi sensitivity data re-cut by **FET status** with a general-sensitivity correction: the ATRi effect survives (AZD6738 Δ −0.491, *t* −5.08) but PARP inhibitors are 2–4× larger, and PARPi monotherapy already failed clinically in Ewing | ⭑ **a computed result either way** — a class-inheritance assessment with its own internal bound, which stands as a paper whether or not one cell is ever plated. ⚠ It is an assessment, **not** a measurement in EMC; §5 holds that limit | **none of the three** |

**Tier 2 — ASKS. Each is an experiment this programme has specified and cannot run. Ranked on W1
(is there a self-interested taker?), then W2 (size). ⚠ These are not lesser routes; they are the ones
whose completion is outside our control.**

| rank | # | route | W1 — the taker | W2 — the ask | D (if it never happens) |
|---|---|---|---|---|---|
| **4** | **1b** | **The ATR-inhibitor cell panel in EMC lines** — ⭑ **the ASK behind route 1, presented as one** | ⭑ **the strongest in the portfolio.** The FET/ATR authors' own class argument runs ETS → bZIP → zinc-finger; **EMC's nuclear-receptor partner is the missing fourth class**, so running it completes something they already published rather than testing something of ours. Secondary help: the compounds have been commercially deprioritised, which makes them *easier* to obtain for investigator-initiated work | **smallest in the portfolio** — catalogue ATR inhibitor, 7-point dose–response, published EMC lines, γH2AX (the readout the source paper reports as the reliable one here, after p-CHK1 did not discriminate), **plus a PARPi arm and a proliferation index**, both required by [the prereg](../modalities/emc-atri-prereg.md) | the prereg and the assessment above. **The panel itself is an unrun proposal** — which is exactly why it sits here and not in Tier 1 |
| **5** | **6** | **Trabectedin + PPARγ agonist, on EMC's own documented fusion→PPARG axis** | **good, and better than its in-silico half suggests.** All drugs approved; the pioglitazone + trabectedin combination was published in the sibling myxoid sarcoma, so **its own authors have a class-extension interest** of the same shape as route 1's. Sarcoma clinicians already give trabectedin in EMC | small — a two-drug matrix on the existing EMC lines, one plate, catalogue reagents | ⚠ **thin, and this is what stops it out-ranking the panel.** A literature synthesis plus, at best, a one-line expression read on the single EMC model in DepMap (`n = 1`, no CRISPR data). It is a *hypothesis*, not a computed result |
| **6** | **2b** | **Junction knockdown + parental sparing in EMC lines** — the ASK behind route 2 | ⚠ **weak, and stated as such.** No group has a standing self-interest in an EMC-specific junction oligo; the ASO field's takers want de-risked targets in larger indications. The route's rank comes from its **deliverable**, not its ask | moderate — synthesised gapmers plus the lines | **the paper is unaffected** — this is the one ask whose failure costs the route nothing, because Tier 1 #2 does not depend on it |

**Tier 3 — value concentrated in an experiment nobody here can cause, with an in-silico half too thin
to stand alone. ⭑ The first three rows are the DEMOTIONS from Tier 2, each graded individually and
none of them as a block.**

| # | route | why it dropped, or why it is here |
|---|---|---|
| **4** | **TCIP / transcriptional chemically-induced proximity on EWSR1::NR4A3** — ⭑ **was Tier 2 #4** | **W1 is real but contingent, and P has not been run.** The TCIP authors' stated first limitation *is* the missing ligand, so they have a genuine interest — **but what we can offer is a computationally-opened cryptic pocket, not a ligand**, and `R4` (does anything bind it) is unanswered, which is precisely the gap they named. W2 needs a bespoke bivalent synthesised. **D is currently zero and one free CPU run from being non-zero** — the TCIP-configuration linker enumeration (§3, route 4) has not been executed. ⭑ **Run it, then re-grade** — this is the cheapest promotion available in the memo |
| **5** | **Covalent probe at C397 — as a REAGENT, not a drug** — ⭑ **was Tier 2 #5, the largest drop** | ⛔ **D ≈ 0, and P is negative rather than merely absent.** Its entire value is a wet-lab readout: no thiol pKa or intrinsic reactivity is computed anywhere in this repo, and its own exposure instrument `V17` **fails its positive control**, so the in-silico half is not publishable as it stands. W2 is a bespoke synthesis — the largest ask class — and W1 has no identified group with a standing interest in an EMC covalent probe. Its earlier rank came from being *cheap for a collaborator*, which is the exact axis this memo corrected |
| **7** | **SSTR2 / neuroendocrine theranostic** — ⭑ **was Tier 2 #7** | **W2 is the smallest imaginable (an approved scan) and W1 is the problem.** Ordering ⁶⁸Ga-DOTATATE needs a clinician **with an EMC patient**; that is not a group wanting a result for its own reasons, it is the hardest access class in the memo. **D ≈ 0:** [`emc-surface-target-landscape.md`](./emc-surface-target-landscape.md) already exists and already records SSTR2 as unmeasured in EMC, so nothing further is computable and no new document falls out. ⚠ The route is not refuted — a negative scan still kills it cheaply, and it stays on the ask list |
| 8 | RIPTAC (bind-the-tumour-protein, poison an essential one) | needs paralogue selectivity *and* a medicinal-chemistry campaign — strictly worse than route 4 on both |
| 9 | CRISPR/Cas9 intron-targeted fusion disruption; Cas13 fusion-RNA knockdown | delivery, and Cas13 collateral activity |
| 10 | Fusion-junction TCR / ImmTAC | the weak-junction-pHLA problem; EMC is antigen-cold |
| 11 | HDAC / BET to lower fusion *expression* | not fusion-selective; a class effect, not an EMC result |
| 12 | Trans-splicing ribozyme → suicide gene, triggered by the fusion transcript | vector delivery; a 2000s-era technique with no modern solid-tumour clinical footing |
| 13 | B7-H3 / CD56 ADC or CAR-T | already red-teamed in this repo: not selective (BH q = 1.0) |
| **14** | ⭑ **Fusion-driven synthetic promoter → suicide gene** *(NEW to this repo)* | vector delivery — **and EMC lacks the neomorphic DNA-binding element the technique depends on** (§3, route 14). ⭑ Note on Axis D: the *reason* it fails is itself a computed-and-cited EMC result and belongs in a paper, even though the route does not |
| **15** | ⭑ **A ligand for the shared FET low-complexity half** *(NEW to this repo)* | binds wild-type EWSR1 too — an essential housekeeping protein — so it *relocates* selectivity somewhere worse |

**Tier 4 — closed. Do not spend on these; two of them are closed *by this session's reading* and are
new entries.** ⭑ **Unchanged by the axis correction, and worth one line on why:** a closure is a
completed product needing nobody's cooperation, so on Axis D these are the highest-scoring rows in
the memo. They are Tier 4 because they close a *route*, not because the work was worth less — and
they are exactly the kind of content Tier 1 #3 is made of.

| route | why closed |
|---|---|
| **RXR-heterodimer modulation of the fusion** — ⭑ **NEW, closed today, on a verbatim primary source** | **NR4A3 does not heterodimerise with RXR**, unlike NR4A1 and NR4A2. Quoted rather than paraphrased, because the whole closure turns on it: *"Nor1 is unable to promote RXR signaling due to its inability to form heterodimers with RXR"* ([Zetterström et al., *Mol Endocrinol* 1996;10:1656–66, PMID 8961274](https://pubmed.ncbi.nlm.nih.gov/8961274/) — the paper's title is literally that RXR heterodimerisation *distinguishes* the three). The one pharmacology this receptor family has actually solved is the one place our paralogue is absent |
| **6-mercaptopurine / AF-1 agonism of the fusion** — ⭑ **NEW, closed today** | 6-MP is the one **approved** drug that activates NR4A3, which would have been the cheapest imaginable entry — but it acts *through the AF-1, not the LBD* — and the source delimits that domain exactly: *"The N-terminal AF-1 domain delimited to between amino acids 1 and 112, preferentially recruits the steroid receptor coactivator (SRC)… SRC-2 modulates the activity of the AF-1 domain but not the C-terminal ligand binding domain (LBD)"* ([Wansa et al., *J Biol Chem* 2003;278(27):24776–90, PMID 12709428](https://pubmed.ncbi.nlm.nih.gov/12709428/)). ⭑ **NOR-1 residues 1–112 sit entirely inside the 1–260 stretch the fusion replaces** with EWSR1's low-complexity region ([`target-route-options.md` check B](./target-route-options.md) measured that swap: NR4A3 AF1 1–260 ↔ EWSR1-LC 1–264). A ligand whose whole mechanism lives in a domain the disease deletes cannot act on the chimera at any dose |
| molecular glue instead of a PROTAC | ⏸ already parked by the roadmap — *removes* handles and keeps the same ~1 kcal/mol claim |
| relocating the target to the DBD / DNA binding | ✕ already dead by arithmetic — 93–99 % paralogue identity against 59–67 % |
| fusion-junction vaccine / HLA coverage | ⏸ already parked — weak immunogen in a cold tumour |

---

## 3 · The routes in detail

### Route 1 — ⭐ ATR-inhibitor synthetic lethality: EMC inherits a class vulnerability it has never been tested for

⭑ **READ THIS ROUTE AS TWO THINGS, because the axis correction split it and the split is the most
consequential thing in this memo.**

| | **1a — the in-silico vulnerability assessment** | **1b — the ATR-inhibitor cell panel** |
|---|---|---|
| what it is | a computed class-inheritance assessment: the FET-IDR/RGG structural precondition from sequence, the GDSC2 ATRi re-cut by FET status, the PARPi negative-translation bound | a 7-point dose–response in EMC lines with γH2AX, a PARPi arm and a proliferation index |
| who has to agree | **nobody** | a group holding an EMC model |
| tier | **Tier 1, rank 3** — it produces a result either way | **Tier 2, rank 4** — best W1 and smallest W2 in the memo, and still not ours to run |
| its home | ⭑ **[`emc_atr_vulnerability.py`](../modalities/emc_atr_vulnerability.py)** — the dedicated assessment module, which asks the reviewer's next four questions and reports a failing specificity control as a failure; upstream of it, [`emc_fet_idr_census.py`](../modalities/emc_fet_idr_census.py) → [`emc-fet-idr-census.json`](../modalities/emc-fet-idr-census.json) (the structural precondition) and [`fet_ddr_axis_scan.py`](../modalities/fet_ddr_axis_scan.py) → [`fet-ddr-axis-scan.json`](../modalities/fet-ddr-axis-scan.json) (the transfer prior and its two bounds). **This memo cites those, it does not restate them** | [`emc-atri-prereg.md`](../modalities/emc-atri-prereg.md), written before anyone was approached |

**The two must not be quoted as one route.** Merging them is what let the first ranking put route 1
at #1 on the strength of an experiment nobody has agreed to run. **1a is the strongest new
*deliverable* this memo found; 1b is the strongest *ask* it found; they are different claims.**

**This is the strongest new candidate in the memo and it is not a molecule we have to invent.**

**The mechanism, cited.** FET fusion oncoproteins are recruited to DNA double-strand breaks through
their N-terminal intrinsically-disordered region and **impair ATM activation and downstream
signalling**, leaving the compensatory ATR axis load-bearing — so ATR inhibition is synthetic lethal
([Cancer Res / bioRxiv 10.1101/2023.04.30.538578, PMID 37205599](https://pubmed.ncbi.nlm.nih.gov/37205599/);
open-access full text in the corpus). Two things in that paper make it transfer to EMC rather than
stopping at Ewing, and both are quoted rather than paraphrased:

1. **The effect is carried by the FET half, not the partner.** *"the N-terminal IDRs, as a shared
   structural feature of FET fusion oncoproteins … could promote aberrant DSB recruitment in other
   tumors within this class. EWSR1-ATF1 is the sole oncogenic driver of clear cell sarcoma (CCS) and
   contains the identical N-terminal IDR sequence as EWSR1-FLI1."* They then show CCS behaves the
   same: *"CCS cells also display FET fusion oncogene-dependent synthetic lethality with ATR
   inhibitors."*
2. **It is already partner-agnostic in the tested set.** The panel and the in-vivo work span an
   **ETS** partner (FLI1), a **bZIP** partner (ATF1) and a **zinc-finger** partner (WT1, DSRCT), plus
   myxoid liposarcoma. Elimusertib IC50s were **20–60 nM** in FET-driven lines, and **5 FET-rearranged
   PDX models** — 2 Ewing, 2 CCS, 1 DSRCT — *"show significant anti-tumor responses"*, the DSRCT
   xenograft best (*"partial by RECIST criteria, >50 % reduction in tumor volume"*). **EMC's partner,
   NR4A3, is a nuclear receptor — a fourth TF class, and the untested one.**

#### ⭐ The structural precondition, computed — and EMC's fusion carries the *identical* FET segment

**The partner-list argument is about gene names. The mechanism is about structure**, and the source
states it as a conjunction: the fusion **retains** the FET N-terminal IDR (so it reaches DSBs) and
**loses** the C-terminal RGG repeats (so its recruitment is aberrant) — *"all oncogenic FET fusion
proteins including EWSR1-FLI1 share a similar structure: the N-terminal IDR of the FET protein fused
to the DNA binding domain of a transcription factor … with loss of the C-terminal RGG repeats"*. The
RGG half is the one shown **causally**: putting 1 or all 3 RGG domains back into EWSR1-FLI1 restored
earlier recruitment kinetics in an RGG dose-dependent manner. **Nobody had checked this for any NR4A3
fusion.** [`emc_fet_idr_census.py`](../modalities/emc_fet_idr_census.py) →
[`emc-fet-idr-census.json`](../modalities/emc-fet-idr-census.json) does, from sequence, for $0.

| fusion | EWSR1 retained | RG dipeptides kept | precondition |
|---|---|---|---|
| **EWSR1::NR4A3 (EMC, canonical)** | **1–264** | **0 of 30** | ✅ met, 35 residues of margin |
| EWSR1::FLI1 (Ewing, type 1) — *mechanism measured here* | 1–264 | 0 of 30 | ✅ met |
| EWSR1::ATF1 (clear cell, e7) — *mechanism measured here* | 1–264 | 0 of 30 | ✅ met |
| EWSR1::ATF1 (clear cell, **commonest** type, e8) | 1–324 | **7 of 30** | ✖ strict criterion — **and the mechanism was measured anyway** |

⭑ **The headline: EMC's canonical fusion retains a segment that is BYTE-IDENTICAL to the Ewing
type-1 fusion's** (`byte_identical: true`) — not similar, not homologous, the same 264 residues of
EWSR1. Whatever the retained FET N-terminus does at a double-strand break in Ewing sarcoma, EMC's
commonest fusion presents the same object.

⚠ **And the controls calibrate the criterion instead of merely passing it**, which is why the last
row matters more than the first three. The *commonest* reported clear-cell type keeps 7 of 30 RG
dipeptides and the lesion was still measured in that disease — so "loses the RGG repeats" means
losing the bulk, not literally all, and **the strict verdict is conservative**. The defensible claim
is therefore comparative and needs no threshold at all: **EMC loses at least as much RGG content as
every fusion in which ATM suppression has been measured.**

⚠ **Three limits, all recorded in the artifact.** This is a *sequence* argument — it cannot show that
any NR4A3 fusion is recruited to DSBs or suppresses ATM, which is exactly the wet-lab ask. TAF15 and
FUS breakpoints are **swept, not known** (this repo has no exon audit for them), so their answer is
reported as a function of breakpoint. And the module's first two designs were wrong and were caught
by testing rather than by review: an RGG box was reported at its sliding-window edge (putting EWSR1's
first box at 258 when its first RG is at 300 — an error straddling the very breakpoint being judged),
and the IDR half was gated on a composition threshold that *decided* the answer, so it is now
reported and never gated.

**Why EMC is arguably the *cleanest* member of the class.** EMC's three commonest 5′ partners —
**EWSR1, TAF15 and FUS** — are the three FET-family genes. From two published series: **EWSR1 62 % /
TAF15 27 % / TCF12 4 %** (n = 26, [Agaram et al., *Hum Pathol* 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4015728/))
and **EWSR1 79 % / TAF15 16 % / TCF12 3 %** (n = 58, [Warmke/Antonescu-type series, *Mod Pathol* 2023](https://pubmed.ncbi.nlm.nih.gov/36948401/)).
So **≈ 89–95 % of EMC carries a FET-family 5′ partner** — a higher FET fraction than any tumour in the
paper's own panel, because Ewing's *EWSR1::ERG* and *FUS::ERG* variants are the exception there and
here the FET partner is the rule. ⚠ Stated at its true weight: that is an *inclusion* argument, not
evidence that the ATM lesion occurs in EMC. **Nobody has measured a DSB-recruitment or ATM-signalling
phenotype for any NR4A3 fusion.** That is the gap, and it is exactly what makes the experiment worth
running.

**What we already computed, including the part that did not work.** The DepMap knockout scan
([`fet-ddr-axis-scan.json`](../modalities/fet-ddr-axis-scan.json), release 24Q4, 1,178 models) was
pre-registered as a **double** prediction — ATR axis more essential in FET lines *and* ATM axis not
more essential — because either half alone is consistent with a lineage artefact. **It came back
`NEITHER` / `ATR_HALF_ONLY`, and the diagnosis is the instrument, exactly as the module said in
advance it would be.** Three measurements say so rather than one argument:

- The ATR axis sits at **−1.578** in FET lines, **−1.601** in non-FET sarcoma and **−1.559** in
  everything else — a between-group delta of **0.02** against a within-group SD of **0.12–0.15**.
- ⭑ **`frac_lines_dependent_on_axis` = 1.000.** *Every* line in DepMap passes the standard dependency
  threshold on this axis. A readout on which nothing is negative has no discriminating power at all,
  and that is a cleaner statement of the problem than any delta.
- The **controls now pass**, so the read itself is sound: RPL5 **−2.55** panel-wide (essential),
  ATM **−0.008** (near-neutral). ⚠ On the first run the stated pan-essential control read `null`
  because **POLR2A and PRKDC are simply not in the 24Q4 column set** — measured, then fixed, not
  explained away.
- ⭑ **And a second, independent grouping agrees.** Rebuilding FET status from DepMap's own
  `OmicsFusionFiltered` calls instead of disease labels (**81 models carry an EWSR1/FUS/TAF15 fusion
  call, 55 with CRISPR data**) gives an ATR-axis delta of **0.006**. Two different groupings, same
  blindness — so the null is a property of the instrument, not of how the groups were drawn.

⛔ **This is reported as a failed instrument and must not be quoted as evidence against the
hypothesis.** A full ATR knockout removes the protein everywhere, which is a different question from
what a sub-lethal inhibitor does. The scan now carries the *right* instrument — **ATR-inhibitor
sensitivity** — because the source paper used exactly that (*"we utilized DepMap screening data for
elimusertib in 880 cancer cell lines which included 17 ES samples"*) and **split it only as Ewing vs
non-Ewing**. Re-cutting by FET status, so CCS, DSRCT and myxoid liposarcoma sit *with* Ewing instead
of in the comparator, is a free analysis that is not in the paper and that directly tests whether the
class claim is partner-agnostic or a Ewing effect. ⚠ **Where that data lives was itself a measured
question, and two guesses were wrong**: the quarterly figshare releases carry no drug matrix (73 and
52 files, all CRISPR/omics) and figshare's search endpoint returns unrelated articles for every PRISM
term tried, so the scan reads ATR-inhibitor LN_IC50 from **GDSC2 (release 8.5)**, keyed through
`Model.csv`'s Sanger/COSMIC ids, with control drugs run through the identical path.

#### ⭐ The ATRi contrast, and the two things it says — one supporting route 1, one bounding it hard

**69 FET-keyed lines against 1,230 comparators, GDSC2 8.5, LN_IC50 (lower = more sensitive).** Both
the raw contrast and one corrected for **each line's own median LN_IC50 across every GDSC drug** are
reported, because FET-rearranged lines — Ewing especially — are fast-growing and broadly
chemosensitive, so a raw contrast measures growth rate as much as biology. **Quote the corrected
column.**

| drug | class | n FET | raw Δ (t) | **corrected Δ (t)** |
|---|---|---|---|---|
| **ceralasertib / AZD6738** | **ATR inhibitor** | 57 | −0.757 (−4.48) | **−0.491 (−5.08)** |
| **berzosertib / VE-822** | **ATR inhibitor** | 54 | −0.691 (−2.59) | **−0.423 (−2.20)** |
| talazoparib | PARP inhibitor | 57 | −2.336 (−5.67) | **−2.065 (−5.85)** |
| olaparib | PARP inhibitor | 57 | −1.280 (−5.37) | **−1.016 (−5.58)** |
| paclitaxel | tubulin (non-DDR) | 57 | −0.792 (−3.19) | **−0.525 (−3.08)** |
| adavosertib / MK-1775 | WEE1 inhibitor | 57 | −0.242 (−1.62) | **+0.021 (+0.17)** |
| bortezomib | proteasome | 57 | −0.183 (−1.98) | **+0.087 (+0.88)** |

**✅ What supports route 1.** The ATR-inhibitor effect is real and it **survives the correction** —
about a third of the raw signal was general chemosensitivity, two thirds is drug-specific — and the
correction demonstrably works, because two controls that should land at zero do (adavosertib +0.02,
bortezomib +0.09). This is a **computed** result rather than an inherited argument, and it is one the
source paper did not produce: its DepMap cut was Ewing-vs-everything, this is FET-vs-everything with
a general-sensitivity correction and non-DDR controls.

**⛔ What bounds it, and this is the more important half.** ATR is **not** the dominant DDR
vulnerability in this data. **Talazoparib is four times the effect and olaparib twice**, both with
larger *t* than either ATR inhibitor — and **paclitaxel, which has nothing to do with DNA repair,
matches AZD6738**. So this dataset supports "FET-rearranged lines are drug-sensitive, including but
not especially to ATR inhibitors"; it does **not** isolate ATR, and it must not be written as if it
did.

⭑ **And the PARP row is the single most useful thing this analysis produced, because its clinical
answer is already known.** *"Both xenograft studies and clinical trials in ES patients failed to
demonstrate any benefit for PARP inhibitor monotherapy"* — quoted from the very paper proposing the
ATR route. **This dataset therefore contains a worked example of a large, reproducible, in-vitro
FET-line DDR sensitivity that did not translate to patients** — and it is *larger* than the ATR
signal we would be arguing from. That is a real bound on how much weight route 1's in-vitro case can
carry, and it converts directly into a design requirement: **the preregistration must include a
PARP-inhibitor arm as an internal negative-translation control.** If EMC lines look PARPi-sensitive
too, the assay is reproducing the Ewing pattern that already failed, and the ATRi number should be
discounted accordingly. That control costs one extra column on the same plate.

⭑ **Two other $0 answers fell out of the same run.** The one EMC model in DepMap, **ACH-001519 /
H-EMC-SS**, is present with `OncotreeSubtype: "Extraskeletal Myxoid Chondrosarcoma"`,
lineage `Bone` — and **has no CRISPR gene-effect data** (`has_crispr_gene_effect: false`), which
closes the `[to verify]` that has sat in [`../IDEAS.md`](../IDEAS.md) since 2026-07-03. And
**POLR2A and PRKDC are simply absent from the 24Q4 column set**, which is why the first run's stated
pan-essential control read `null`; the control is now RPL5.

**Axis P (1a) — what we can publish without a lab.** The FET-fraction arithmetic above; the re-cut
ATRi sensitivity analysis; a structural argument that all three EMC fusions retain the full FET IDR
(this repo already owns the exon-resolved fusion model that resolves the junction to **EWSR1(1–264)::NR4A3(1–626)**,
[`target-route-options.md` §1.3](./target-route-options.md)); and a preregistered prediction with
kill criteria.

**⭑ Axis D (1a) — what we hold if nobody ever plates a cell.** A complete in-silico vulnerability
assessment: a class-inheritance argument with a **computed** structural precondition, a **computed**
drug-sensitivity re-cut the source paper did not perform (it split Ewing-vs-rest; this is
FET-vs-rest with a general-chemosensitivity correction and two non-DDR controls that land at zero),
and a **computed internal bound** — the PARPi rows, which are larger than the ATRi rows and whose
clinical answer is already known to be negative. ⚠ **That last part is what makes 1a a real
deliverable rather than an advocacy document**: it publishes the strongest available argument
*against* its own hypothesis alongside it, from the same data, and a reader can grade it without
running anything.

**Axis W1 (1b) — the taker, and this is the calibrating example for the whole axis.** The source
paper's argument is a **partner-class** argument: it spans an ETS partner (FLI1, Ewing), a bZIP
partner (ATF1, clear cell) and a zinc-finger partner (WT1, DSRCT), and it generalises from the shared
FET N-terminus rather than from any partner. **EMC's partner, NR4A3, is a nuclear receptor — a fourth
TF class, and the untested one.** So the ask is not *"please test our molecule"*; it is *"here is the
missing class in the argument you published, with the structural precondition already computed and
byte-identical to your own system's, and a preregistration that includes the control that would
embarrass it."* ⚠ **Stated at its true weight: a self-interested taker is not a committed one.**
Nobody has been approached — that step is outward-facing and is trimcrae's alone (CLAUDE.md §3) — so
W1 grades the *position*, and no group's willingness is claimed or implied.

**Axis W2 (1b) — the ask's size, and it is the smallest in the portfolio.** *Run a 7-point
elimusertib (or ceralasertib/berzosertib) dose–response in EMC cells against a non-FET sarcoma
control, and stain γH2AX.* Every component exists: **the compounds are catalogue reagents**; **the
models exist** — USZ20-EMC1 and USZ22-EMC2 ([Bangerter et al., *Human Cell* 2023;36:446–455](https://link.springer.com/article/10.1007/s13577-022-00818-x)),
NCC-EMC1-C1 ([Iwata et al., *Human Cell* 2025](https://link.springer.com/article/10.1007/s13577-025-01250-7)),
and H-EMC-SS; and **the readout is pre-validated** — the source paper found *"gH2AX proved to be a
reliable biomarker for elimusertib activity"* after p-CHK1 did not discriminate. This is a plate
experiment, not a program. ⚠ Per Axis W2's definition this counts **only because W1 is strong**; the
same plate with no interested group would be worth nothing.

**Axis S — inherits none of the three blockers.** No ΔΔG, no ternary, no paralogue discrimination.
The molecule is not ours and does not need to be selective for anything in the NR4A family.

⚠ **A fourth counterweight that is mechanistic rather than commercial, and it is the one I would
press hardest if I were reviewing this.** ATR-inhibitor activity generally tracks **proliferation and
replication stress**, and EMC is the opposite of that — indolent, median time to metastasis ≈ 28
months, 10-year DSS ≈ 85 %. The published mechanism here is ATM suppression at double-strand breaks
rather than replication stress *per se*, so the two are not the same argument, but a slowly-cycling
tumour has fewer replication forks for an ATR inhibitor to catch and a lower baseline γH2AX for the
readout to move. **This does not change the ranking** — the experiment is cheap enough that the
objection is better answered than argued, and the PDX panel that responded included relapsed disease —
but it belongs in the preregistration as a stated prior, and it argues for including a **proliferation
index** alongside γH2AX so a null can be attributed rather than merely recorded.

⚠ **Three further counterweights, none of which is a reason not to run it.** (i) **The ATR class has
had a bad two years commercially** — ceralasertib missed in a phase 3 NSCLC readout, Bayer
discontinued elimusertib, berzosertib was shelved, and Roche returned camonsertib; a basket expansion
of elimusertib in DDR-defective solid tumours reported **ORR 4.5 % with DCR 49.3 %**
([PMID 40516108](https://pubmed.ncbi.nlm.nih.gov/40516108/)). Commercial retreat is not a mechanistic
refutation, and for a rare disease it can even help — deprioritised compounds are easier to obtain
for investigator-initiated work — but it must be said, and it means **the deliverable is a hypothesis
plus a biomarker, not a development plan.** (ii) **The inhibitors are not interchangeable**: the same
paper notes berzosertib *"showed no anti-tumor activity as monotherapy in ES cell line xenografts"*.
(iii) **PARP-inhibitor monotherapy failed in Ewing** despite the older R-loop/BRCA-like model — the
cautionary precedent for exactly this kind of class transfer, and the reason the ask includes a
mechanism readout rather than viability alone.

---

### Route 2 — ⭐ Fusion-junction ASO / siRNA: unchanged in rank, and the route the axis correction most clearly vindicates

Nothing in this memo changes the existing plan ([`fusion-junction-aso-paper.md`](./fusion-junction-aso-paper.md);
route detail in [`target-route-options.md` route 3](./target-route-options.md)). It is repeated here
only because the ranking would be wrong by omission, and because **the degrader's failures raise its
relative rank without anything about it changing**: base pairing is categorical, so it inherits none
of the three blockers, and it is the only route that removes the paralogue requirement *and* the
wild-type-NR4A3 liability at once.

**The one gate is tumour delivery, and that gate has moved.** Antibody-oligonucleotide conjugates are
now a real extrahepatic-delivery modality with clinical programs, explicitly framed as *"a promising
class of therapeutics for extrahepatic delivery of small interfering ribonucleic acids"*
([Antibody Therapeutics 2026](https://academic.oup.com/abt/article/9/3/273/8664745)) — which converts
"delivery is unsolved" into "delivery needs a tumour-restricted surface antigen", and **this repo has
already built the EMC surfaceome scan that asks precisely that question**
([`emc-surface-target-landscape.md`](./emc-surface-target-landscape.md)). ⚠ That landscape's own
honest headline is that the intersection of selective and normal-tissue-restricted is **empty** among
classic antigens, so this is a *reframing of the gate*, not a solution to it.

**⭑ Axis D — why this route survives the reframe better than anything except the methods paper.** Its
in-silico arc was *completed and red-teamed before* the wet-lab question was ever asked, so the
deliverable and the ask are already separate objects:
[`fusion-junction-aso-paper.md`](./fusion-junction-aso-paper.md) is finished work with its own
[red team](./fusion-junction-aso-paper-redteam.md), and the delivery gate lives **inside** it as a
stated limitation rather than as a precondition for having a paper. ⚠ **That is the profile Axis D
was added to detect** — and note what it does *not* claim: base-pairing selectivity is computed, not
demonstrated in a cell, and the one remaining GPU item (RNase-H1 cleavage-discrimination MD) would
strengthen the specificity argument without changing that. **Axis W1 — weak, and it costs the route
nothing.** No group has a standing self-interest in an EMC-specific junction oligo; the route ranks
where it does entirely on D.

---

### Route 3 — ⭐⭐ Publish the methods result the program has already earned — **RANK 1**

⭑ **This route was #3 in the first ranking and it should have been #1.** It was under-rated for
exactly the reason it is now first: the old Axis W had nothing to say about a route with **no wet-lab
ask at all**, so a route needing nobody scored as though it offered nothing, while a route needing a
collaborator scored on how cheap that collaborator's afternoon would be. Under Axis D the ordering
inverts — **this is the only entry in the memo that is finished when we stop typing.**

**And it feels like a consolation prize, which is the second reason it was under-rated. It is not.**
The north star is *"the state of the art of what in-silico can do"* — and a rigorous, preregistered
demonstration of **where in-silico selectivity prediction breaks** is a state-of-the-art result about
the state of the art. What this program can put on the record that essentially nobody else has:

- **Three independent, preregistered attempts at a positive control for paralogue-selectivity
  detection, all failing, with their mechanisms diagnosed** — a wrong-sign ternary FEP calibrator, an
  adequately-powered endpoint-MD null with zero technical failures and a reference-set floor two
  orders under α, and a covalency-confounded retrospective that could never have worked at any *n*.
- **The measured reason the third one is uninterpretable**: sequence-only co-folding assembles
  ternaries wrongly rather than approximately — **DockQ 0.023–0.046, fnat 0.000** on the
  target↔E3 interface while the internal E3 machinery scores 0.89–0.97 — localised by decomposition to
  *relative placement of the two proteins*, at the scale a true complex reaches when displaced ~32 Å.
- **A selectivity detector that passes a known-answer test** (the SMARCA2/SMARCA4 Gln98→Leu interface
  signature, instrument `V1`) **and then returns "not yet" on our own system for a stated,
  reproducible reason.**
- ⭑ **Two further instruments that were assembled and then FAILED or DISAGREED on their own
  known-answer terms, both landed 2026-08-03 and neither in the first ranking** — the anti-target
  docking panel `V21`, which cannot recover 3 of its own 10 cognate crystallographic ligands and is
  therefore graded unreadable, and the scoring-independent second pose method `V22`, which disagrees
  with the primary docking instrument. **The roadmap's instrument register is the one home for both
  verdicts and their numbers** ([§V-register](./nr4a3-program-map.md#3--instruments--which-one-answers-each-requirement));
  this memo only records that the paper has them. ⚠ **A failing instrument is a *harder* result to
  publish than a hole and a more useful one** — a hole says nothing was built.
- ⭑ **A published method's blindness claim retracted from that method's own released data.** The
  DeepTernary benchmark's unbound protocol turns out to superpose both binaries into the native
  ternary frame and supply the native degrader pose, so it is blind to the two proteins' relative
  placement and **not** to which pocket each ligand end occupies; our own arms were re-labelled and
  the positive control moved to an honestly-labelled in-set case. One home for the evidence:
  [STRATEGY.md Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims)
  row 65. **This is a finding about the field's instrument, not about our target**, which is the
  kind of content a methods venue exists for.

Negative results with working controls are publishable and they are what the field is short of. Venue
is a methods/assessment journal, not a target paper. **Cost: $0. Blockers inherited: none — it is a
paper *about* the blockers.** This also protects the program's credibility: the alternative is a
target paper carrying an unvalidated selectivity prediction, which is the outcome the roadmap's
language discipline exists to prevent.

**⭑ Axis D — maximal, and the reason this is rank 1.** Every input already exists as a committed
artifact with a preregistration in front of it; nothing here is waiting on a reagent, a group, a
scan or a plate. **W1 and W2 are not weak for this route — they are undefined**, because there is no
ask. ⚠ **What it is not:** it is not an EMC treatment candidate, and it must never be presented as
one. It is the honest product of a program that set out to build a selectivity instrument and can
report, with controls, that the instrument is not yet there. The memo's own question — *what reaches
a testable candidate* — this route answers with "nothing, and here is precisely why", which is a
result rather than a failure to have one.

---

### Route 4 — TCIP: spend the ligand on rewiring instead of degradation

**Rationale, cited.** Bivalent "transcriptional chemical inducers of proximity" recruit a fusion TF to
new chromatin sites rather than removing it; EB-TCIP relocalises EWSR1::FLI1 to BCL6-bound loci with
*"rapid chromatin remodeling and expression of BCL6 target genes"*
([JACS 2025](https://pubs.acs.org/doi/10.1021/jacs.5c05634)). **The demonstrated blocker is the
ligand**, quoted in §0.

**What would have to be true, and where it is genuinely easier than the degrader.** A TCIP needs a
binder and a *productive* induced proximity — but **not a ubiquitin-transfer geometry**: no E3 exit
vector, no lysine reach, no transfer-zone enumeration. That deletes the entire `R12`/`R15` machinery
and the ternary-generation stage that measurably fails. What it does **not** delete is paralogue
discrimination — a molecule binding NR4A1/NR4A2 would rewire those too — so this route **reshapes**
the requirement rather than removing it, and must be graded that way.

**Cheapest decisive $0 test:** re-run the linker enumeration in the TCIP configuration (anchor +
effector-recruiter, **no E3 arm**), which is a strictly smaller geometric problem than the one already
enumerated, and ask whether a productive bivalent exists at all. Same free CPU as
[route 2 of `target-route-options.md`](./target-route-options.md), different pendant.

**⭑ Grade under the corrected axes: Tier 3, and one free CPU run from moving.** *(Superseded, kept
quotable: the first ranking's* **"★★ promote, behind Tier 1 only because it still needs a molecule"**
*— see [§6](#6--appendix--the-superseded-ranking-and-what-was-wrong-with-its-axis).)*

- **W1 — real but contingent, which is the whole demotion.** The TCIP authors' own stated first
  limitation is the missing ligand for the endogenous fusion, so the interest is genuine. ⛔ **But
  what this repo can offer them is a computationally-opened cryptic pocket, not a ligand** — `R4`
  (*does anything bind it*) is the program's one un-buyable requirement and is unanswered. So the
  offer is "we predict a site", which is a weaker position than route 1b's "we complete your class
  argument with a catalogue compound", and W1 is graded against that bar.
- **W2 — large.** A bespoke bivalent, synthesised, downstream of a binder that does not yet exist.
- **⛔ D — currently ZERO, and that is the correctable part.** The TCIP-configuration enumeration
  above has **not been run**, so as of this memo the route holds no computed result of its own.
  ⭑ **It is the cheapest promotion available here:** free CPU, and a negative is worth as much as a
  positive because "no productive bivalent exists in the enumerated space" is itself a publishable
  geometric result. **Run it, then re-grade this row** — do not re-rank it on the expectation.

---

### Route 5 — the covalent probe at C397, proposed as a REAGENT — ⭑ **the largest single demotion**

Already specified in [`target-route-options.md` route 2](./target-route-options.md). The program's
single un-buyable requirement is **`R4` — does anything bind the opened cryptic pocket** — and a
covalent probe is the cheapest form of that experiment for a collaborator: an irreversible adduct
gives an intact-mass readout with no SPR, ITC or thermal-shift rig. **Ask for the probe, not the
drug.** ⚠ Its named risks stand unchanged: reach is necessary and never sufficient, no thiol pKa or
intrinsic reactivity is computed anywhere in this repo, and the exposure criterion `V17` fails its
own positive control.

**⭑ And that last clause is now the ranking, not a footnote. Tier 2 → Tier 3.** *(Superseded, kept
quotable: the first ranking's* **"its rank RISES here for one reason … the cheapest form of that
experiment for a collaborator"** *.)* The sentence "the cheapest form of that experiment **for a
collaborator**" names the defect exactly: the whole promotion was an Axis-W judgement about somebody
else's cost.

- **W1 — no identified taker.** Chemical-probe programmes exist for orphan targets, but none has a
  standing interest in an **EMC-specific** covalent NR4A3 probe, and nothing has been approached.
- **W2 — the largest ask class in the memo:** a bespoke molecule synthesised, before any readout.
- **⛔ D ≈ 0, and P is negative rather than merely absent.** This is what separates route 5 from
  route 4, which is otherwise similarly gated. Route 4 has a free computation waiting; route 5's
  in-silico half is **not currently publishable on its own terms** — no thiol pKa or intrinsic
  reactivity is computed anywhere in this repo, and its own exposure instrument fails its positive
  control, so the reach argument cannot be read. ⚠ **Not refuted, and not closed** — the route is
  intact and the fix (a working exposure instrument, or computed reactivity) is in-silico and
  therefore ours to do. It simply cannot be ranked above routes that already hold their product.

#### ⭑ The THIRD framing of C397 now has its own memo — and it hardens two of the rows above

This row frames C397 as a **reagent**; [`target-route-options.md` route 2](./target-route-options.md)
frames it as the **targeting arm of a bivalent**. Neither states the third option — *a standalone
monovalent molecule that only occupies the LBD and thereby alters what the fusion does*. It is written
up and graded in [`nr4a3-monovalent-pocket-route.md`](./nr4a3-monovalent-pocket-route.md) (2026-08-03,
$0) rather than here, because it turns on a different question: not *does anything bind*, but **does
binary occupancy change what the fusion does.** Its verdict is **registered, not promoted**, and three
of its findings bear on this row:

1. ★ **The AF-1 argument that closes 6-MP in Tier 4 does NOT also close LBD-directed modulation.** The
   one published demonstration of LBD-borne functional modulation of NOR-1 was read out on a
   **Gal4-NOR-1-LBD** reporter — a construct that is *itself* AF-1-less — so the domain the fusion
   deletes is not the domain that result rests on. Free, and it was sitting unconnected in the repo.
2. ⛔ **The E3-arm-free reach enumeration that item 4 of §4 asks for HAS NOW BEEN RUN** (in the
   monovalent configuration; the TCIP configuration is still a different second terminus and is not
   answered by it). **It goes against the covalent axis:** removing the second terminus does not widen
   the categorical window at C397 — on the conservative convention it closes every cell that had one.
   A strictly smaller search problem returning a strictly worse selectivity margin, with the mechanism
   measured ([`nr4a3-monovalent-reach.json`](../modalities/nr4a3-monovalent-reach.json)).
3. ⛔ **`R4` is not purchasable as a service either, and the reason is not the price.** `R4` is two
   questions: *does anything bind NR4A3's LBD* is already answered yes in the literature, and *does
   anything bind the **opened cryptic** site* needs the site to be populated in the sample — which is
   `R2`. So a bought binding screen cannot tell "no ligand" from "no pocket", and its negative is
   unreadable at any price. That **strengthens the demotion above** rather than merely accompanying
   it: the ask cannot be routed around a missing collaborator by buying it.

---

### Route 6 — ⭐ Trabectedin + a PPARγ agonist: an all-approved-drug combination on EMC's own documented axis

**This is a new synthesis, not a new fact.** The repo has carried trabectedin and PPARG as separate
rows for months and never joined them. Three published pieces make the join:

1. **The fusion transactivates *PPARG* directly** — the EMC-specific, non-transfer evidence this repo
   already leans on ([Filion et al., *J Pathol* 2009, PMC4429309](https://pmc.ncbi.nlm.nih.gov/articles/PMC4429309/)).
2. **Trabectedin's mechanism is displacing fusion transcription factors from their target promoters**,
   shown in myxoid liposarcoma, and EMC has a reported responder plus a report of near-complete
   regression of metastatic EMC lesions with radiotherapy + trabectedin (Filannino et al. 2018, via
   the [2025 review](https://link.springer.com/article/10.1007/s00432-025-06316-5)).
3. **The combination already worked in the sibling myxoid sarcoma**: pioglitazone + trabectedin
   *"induce adipocyte differentiation to overcome trabectedin resistance in myxoid liposarcomas"*, with
   tumour regression in xenografts only marginally sensitive to trabectedin alone
   ([*Clin Cancer Res* 2019;25:7565](https://aacrjournals.org/clincancerres/article/25/24/7565/82159/Combination-of-PPAR-Agonist-Pioglitazone-and)).

⚠ **And the direction question that IDEAS.md flags is real and cuts against the naive version.** In
myxoid liposarcoma the logic is that FUS::DDIT3 **blocks** adipocytic differentiation and a PPARγ
agonist restores it. In EMC the fusion **turns PPARG on**, so "add an agonist" is not the same
argument and could be redundant. The honest hypothesis is narrower and more interesting: *EMC is a
tumour whose driver has already installed a differentiation-competent nuclear receptor, and
trabectedin's promoter-displacement may be what unmasks it.* **Deciding this needs EMC expression
data, which is the $0 next step** (does EMC express PPARG target genes at a level consistent with an
active or a poised receptor). **Blockers inherited: none.** **Wet-lab ask: a two-drug matrix on the
existing EMC lines** — approved drugs, catalogue reagents, one plate.

**⭑ Grade under the corrected axes: Tier 2, rank 5 — and it is the route where the two new axes
disagree with each other, so both are reported.**

- **W1 — good, and better than the route's in-silico half would suggest.** The pioglitazone +
  trabectedin result was published in the sibling myxoid sarcoma, so **its own authors hold a
  class-extension interest** of the same shape that makes route 1b strong: EMC would be a second
  myxoid sarcoma for their combination, not a favour. Every drug is approved, which removes the
  usual reagent barrier entirely. ⚠ As with 1b, **nobody has been approached** and no willingness is
  claimed.
- **W2 — small.** One plate, catalogue reagents, no synthesis.
- **⚠ D — thin, and this is what keeps it behind route 1b.** If nobody runs the matrix we hold a
  *literature synthesis* — three published pieces joined for the first time — plus, at best, a
  PPARG-axis expression read on **the single EMC model in DepMap** (`ACH-001519 / H-EMC-SS`, `n = 1`,
  expression only). That settles the agonism-vs-redundancy direction question well enough to write
  down and **not** well enough to call a computed result about EMC. The synthesis is genuinely new
  and worth publishing inside a broader memo; it is not a paper on its own.
- **Net:** high W1 and low D pull opposite ways. It sits above the ASO's ask (better taker, smaller
  ask) and below route 1b (whose deliverable half stands alone and whose taker is stronger still).

---

### Route 7 — SSTR2 / neuroendocrine theranostic: the cheapest possible confirm, and the clearest case of cheapness not being enough

Fully worked in [`emc-surface-target-landscape.md` §3.4](./emc-surface-target-landscape.md) and
unchanged; **its confirm is an approved diagnostic scan that a clinician can order on a single
patient**, which no other route in this memo can say. If EMC's neuroendocrine phenotype extends to
SSTR2, ⁶⁸Ga-DOTATATE PET is both the biomarker and the eligibility test for an off-the-shelf
¹⁷⁷Lu-DOTATATE theranostic. ⚠ SSTR2's normal-tissue window is `ENHANCED_BROAD`, the expression is
**unmeasured in EMC**, and a negative scan kills the route — which is exactly why it is worth asking
for.

**⭑ Grade under the corrected axes: Tier 2 → Tier 3, and this route is the axis correction's cleanest
worked example.** *(Superseded, kept quotable: the first ranking's* **"the cheapest decisive confirm
in the entire portfolio"** *, which was true and was not a reason.)*

- **W2 is as small as W2 gets** — an already-approved scan, no reagent, no protocol development.
- **⛔ W1 is the smallest in the memo, and it dominates.** Ordering that scan requires a clinician
  **who has an EMC patient in front of them.** That is not a group wanting a result for its own
  reasons; it is the single hardest access class here, and it is contingent on an ultra-rare
  disease's presentation rather than on anyone's research interest. **A free experiment with no
  taker is not a cheap experiment — it is an experiment that does not happen**, which is precisely
  the conflation the old Axis W encoded.
- **⛔ D ≈ 0.** The surface-target landscape memo already exists and already records SSTR2 as
  unmeasured in EMC. There is no further computation that moves the question — the answer is an
  expression measurement — so if the scan never happens, **nothing new is written.** ⚠ Not refuted
  and not removed: it stays on the ask list, because a single negative scan would still close it for
  the cost of one existing procedure.

---

### Routes 8–13 — why each sits in Tier 3

- **RIPTAC** ([bioRxiv 2023.01.01.522436](https://www.biorxiv.org/content/10.1101/2023.01.01.522436.full.pdf);
  first-in-class now in the clinic) forms a ternary between a tumour-selective protein and a
  pan-essential one, killing only cells expressing the target. Conceptually attractive for a fusion —
  and it is a **nuclear-receptor**-anchored modality in humans already. ⛔ But it needs the target to
  be genuinely tumour-restricted, and NR4A1/NR4A2 are expressed in normal tissue, so it inherits the
  paralogue requirement **in full** while also needing a new medicinal-chemistry campaign. Strictly
  worse than route 4 on both axes.
- **CRISPR intron-targeted fusion disruption** is real and published in sarcoma
  ([*Nat Commun* 2020](https://www.nature.com/articles/s41467-020-18875-x)), and **Cas13** fusion-RNA
  knockdown is the RNA analogue. Both are delivery-gated exactly like route 2, and Cas13 additionally
  carries collateral-cleavage risk. They are worth one paragraph in a paper, not a program.
- **Fusion-junction TCR / ImmTAC**: the class works elsewhere (SYT-SSX in synovial, EWSR1-WT1 in
  DSRCT), but EMC's measured microenvironment is against it — absent PD-L1, no TMB, M2-predominant,
  sparse CD8 ([PMC9527174](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9527174/)).
- **HDAC / BET to lower fusion expression** has a direct sibling precedent — vorinostat reduces
  EWSR1::ATF1 expression in clear cell sarcoma and synergises with JQ1
  ([Cancer Res Commun 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10317042/)) — but it is not
  fusion-selective and this repo's own DepMap read already found BET/CDK pan-essential with no
  selectivity window.
- **Trans-splicing ribozyme → suicide gene** triggered by the fusion transcript is the most elegant
  fusion-exclusive idea in the list and has real literature behind it, but it is vector-delivered and
  has no modern solid-tumour clinical footing.
- **B7-H3 / CD56** are already red-teamed here: not selective (BH q = 1.0).

### Route 14 — ⭑ the fusion-driven synthetic promoter, and the precise reason EMC is a *harder* case than Ewing

Worth writing up because it is the most elegant idea in the search and because **the reason it does
not transfer cleanly is itself a result about EMC.** In Ewing, EWSR1::FLI1 has **neomorphic** DNA
binding — it activates GGAA microsatellites that wild-type FLI1 does not — so a GGAA-based synthetic
cassette is active *only* where the fusion is. That has been built: a de-novo enhancer-based
expression cassette giving EWSR1-FLI1-dependent expression
([*Mol Cancer* 2022](https://link.springer.com/article/10.1186/s12943-022-01641-6)), and a GGAA
promoter driving HSV-TK with ganciclovir-dependent killing in vitro and in vivo
([*Sci Rep* 2025](https://www.nature.com/articles/s41598-025-14945-6)), delivered by an
anti-GPR64-pseudotyped lentivirus.

⛔ **EWSR1::NR4A3 retains NR4A3's own zinc-finger DBD, which binds the same NBRE/NurRE elements the
wild-type paralogues bind** — the roadmap already records that *"the whole family also binds the same
NBRE/NurRE elements, so the functional site is shared as well as the sequence"*
([§6a](./nr4a3-program-map.md#6a--dead--conclusively-unworkable-never-retry)). So an NBRE cassette
would fire in any cell with active NR4A signalling. What EMC's fusion changes is **transactivation
potency**, not binding site — which makes the achievable selectivity a **gradient rather than a
switch**, and a gradient is the wrong basis for a suicide gene. ⭑ **This is the same finding as §0 in
a third guise**: EMC's paralogue problem is not solved by moving to DNA, and here it is not solved by
moving to a promoter either. The route is worth one paragraph in a paper and a named reopening
trigger — *a demonstrated EMC-specific neomorphic element or enhancer* — not a program.

### Route 15 — ⭑ a ligand for the shared FET low-complexity half

**MS0621** is a real small molecule that modulates chromatin accessibility at EWSR1::FLI1-bound loci
and interacts with an EWSR1-containing RNA-associated complex
([*Front Oncol* 2023](https://www.frontiersin.org/journals/oncology/articles/10.3389/fonc.2023.1099550/full));
the TCIP paper names it as the candidate handle for recruiting *endogenous* EWSR1::FLI1. Because
**all three of EMC's common fusions carry a FET low-complexity domain**, a ligand for that half would
engage EWSR1::NR4A3, TAF15::NR4A3 and FUS::NR4A3 alike — the widest possible EMC coverage, and it
sidesteps NR4A entirely. ⛔ **And that is also its defect, already recorded on the target axis**:
targeting a FET protein at the protein level *"moves the selectivity burden onto an essential
housekeeping protein"* ([`target-route-options.md` §3](./target-route-options.md)). It **relocates**
the requirement rather than removing it, and it relocates it somewhere worse. Recorded so the idea
is not re-derived as novel.

---

## 3b · The technique classes searched, and where each landed

*So the breadth of the search is auditable rather than asserted, and so a class that was considered
and rejected is not re-proposed as an unexplored idea. **Absence from Tier 1–2 here is a judgement,
not an oversight.***

⚠ **The `landed` column is the CORRECTED tier.** Where it moved, the first ranking's tier is given
beside it so the change is auditable from this table alone; the reasoning is in
[§6](#6--appendix--the-superseded-ranking-and-what-was-wrong-with-its-axis).

| technique class searched | landed |
|---|---|
| in-silico methods/assessment of where selectivity prediction breaks | **Tier 1 rank 1** *(was Tier 1 #3)* |
| fusion-junction ASO / siRNA; antibody-oligonucleotide delivery | **Tier 1 rank 2** *(was Tier 1 #2 — held)* |
| DDR synthetic lethality in FET-rearranged cancer — **the computed assessment** | **Tier 1 rank 3** *(was, merged with its ask, Tier 1 #1)* |
| DDR synthetic lethality in FET-rearranged cancer — **the cell panel** | **Tier 2 rank 4 — an ASK, best W1 in the memo** |
| differentiation therapy + fusion-TF displacement (PPARγ × trabectedin) | **Tier 2 rank 5** *(was Tier 2 #6 — held tier, now explicitly an ask)* |
| chemically-induced proximity: TCIP (rewiring) | **Tier 3** *(was Tier 2 #4)* — one free CPU run from re-grading |
| covalent probes / chemical-biology reagents | **Tier 3** *(was Tier 2 #5)* — the largest demotion |
| peptide-receptor radioligand therapy / theranostics | **Tier 3** *(was Tier 2 #7)* |
| chemically-induced proximity: RIPTAC (essential-protein poisoning) | Tier 3 #8 |
| gene editing: Cas9 intron-targeting, Cas13 RNA knockdown | Tier 3 #9 |
| TCR-T / ImmTAC / fusion-junction immunopeptidomics | Tier 3 #10 |
| epigenetic suppression of fusion expression (HDAC, BET) | Tier 3 #11 |
| RNA trans-splicing ribozymes → suicide gene | Tier 3 #12 |
| surface-antigen ADC / CAR-T / bispecific | Tier 3 #13 |
| transcriptional targeting via a fusion-responsive synthetic promoter | Tier 3 #14 |
| ligands for the shared FET low-complexity domain | Tier 3 #15 |
| RIBOTAC / RNase-L-recruiting small molecules against the fusion transcript | not ranked — needs a small-molecule-bindable RNA structure at the junction, which the repo's junction work gives no reason to expect; a reopening trigger, not a route |
| condensate-partitioning small molecules against FET fusion condensates | not ranked — the field's own reviews say selective partitioning into a *specific* condensate is unsolved; watch item |
| de-novo binder / minibinder design (RFdiffusion-class) | not ranked as a route — it is a *method* that would serve routes 4 and 5, and intracellular delivery of a designed protein is the unsolved half |
| virtual-cell / perturbation foundation models (X-Cell, STATE, scGPT-class) | not ranked as a route — same reason; it is the in-silico lever that would *find* candidates, and belongs in `method-watch.md` |
| nuclear-receptor heterodimer pharmacology (RXR) | **Tier 4 — closed** |
| approved NR4A3 agonist (6-mercaptopurine) | **Tier 4 — closed** |

---

## 4 · What I would do in the next two weeks, in order

Everything below is $0 or free CI. ⭑ **Re-ordered on Axis D: FINISH THINGS FIRST.** The old order put
the ask-preparation work at the top, which was correct under the old axes and is not under these —
preparing an ask we cannot execute ahead of finishing a paper we can is the exact inversion the
correction identified. *(Superseded, kept quotable: the old order's step 5,* **"Draft the methods
paper's outline"** *, ranked below three ask-side items.)*

1. ⭑ **Draft the methods paper (route 3) — rank 1, and it is the largest un-started deliverable in
   the repo.** Its inputs are all committed: the three failed selectivity controls with their
   diagnosed mechanisms, the co-fold assembly result, `V1`'s known-answer pass beside its "not yet"
   on our own system, and the two 2026-08-03 instrument results (`V21` failing its own panel, `V22`
   disagreeing with `V3`). The roadmap's registers are the one home for every verdict; the paper
   cites them rather than restating.
2. **Re-run the linker enumeration in the TCIP configuration** (no E3 arm) — free CPU, and a negative
   is worth as much as a positive. ⭑ **Promoted in the order because it is the one action that moves
   a route's Axis-D grade**: route 4 holds nothing until this runs, and holds a real geometric result
   the moment it does, whichever way it comes out.
3. **Pull EMC PPARG-axis expression** to settle route 6's direction question, using the surfaceome/
   expression machinery that already exists. ⚠ Bounded in advance: the only EMC model in DepMap is
   `n = 1`, expression-only, so the honest ceiling on this is *a direction*, not a result.
4. ✅ **DONE — the ATRi-sensitivity re-cut landed** (GDSC2 8.5; §3 route 1a). It is a genuine result
   in both directions: the ATR-inhibitor effect in FET lines survives correction for general
   chemosensitivity, and PARP inhibitors are 2–4× larger in the same lines despite having already
   failed clinically in Ewing. Route 1a keeps Tier 1; its in-vitro case is explicitly bounded.
5. ✅ **DONE — the structural precondition is computed** and EMC's canonical fusion meets it with a
   byte-identical FET segment to the Ewing fusion the mechanism was measured on (§3 route 1).
6. ✅ **DONE — the route-1b preregistration is written and committed**
   ([`emc-atri-prereg.md`](../modalities/emc-atri-prereg.md)), before anyone has been approached. It
   carries the two design requirements this session's analyses produced — **a PARP-inhibitor arm as
   an internal negative-translation control** and a **proliferation index** alongside γH2AX — names
   the published EMC models, fixes the criteria in advance, and registers its own adverse prior in
   writing rather than discovering it later.
7. ⛔ **THE ASK — trimcrae's CALL, NOT MINE, AND NOT A BLOCKER ON 1–3.** The remaining step for route
   1b is to approach one of the groups holding an EMC model, or the FET/ATR authors whose class
   argument it completes. That is **outward-facing**, so CLAUDE.md §3 gates it. Everything needed for
   the ask exists. ⭑ **What changed with the axis correction: this is no longer the top of the
   list.** It was, when the ranking treated a cheap ask as a near-certain experiment. It is now a
   step whose timing is trimcrae's and whose failure costs the programme nothing that is not already
   written down — which is the whole reason for splitting 1a from 1b.
8. ✅ **DONE this session** — routes 1 and 6 and the two Tier-4 closures are on
   [`../IDEAS.md`](../IDEAS.md)'s board, and the closures are rows in the roadmap's
   [§6a register](./nr4a3-program-map.md#6a--dead--conclusively-unworkable-never-retry), pointing here
   rather than restating the reasoning.

---

## 5 · Limits of this memo, stated so it is read correctly

- **No efficacy, safety, therapeutic-window or clinical-readiness claim is made for any route here**,
  including route 1. Everything is an untested hypothesis, and for an untested agent efficacy is
  unmeasurable.
- **The ATR hypothesis is a class inheritance, not an EMC measurement.** No NR4A3 fusion has been
  tested for the DSB-recruitment or ATM-signalling phenotype the mechanism rests on. That is the
  experiment, not a gap in the write-up.
- **The DepMap knockout scan failed as an instrument and is reported as a failure**, not as a null
  about biology. Its saturation is decided from the data and recorded in the artifact.
- **The GDSC contrast's comparator is every non-FET line in GDSC2, not other sarcomas.** A
  sarcoma-restricted comparator would be the better test and is free; it is not run here. The
  FET group is also dominated by Ewing, so "FET" in that table is substantially "Ewing plus a few",
  and it says nothing about EMC directly — no EMC line is in GDSC2.
- **Five of the 38 literature targets returned HTTP 403** at their publisher (`emc_tamoxifen_pgr_nr4a3_jcopo`,
  `emc_taf15_modern_pathology`, `emc_ngs_oncotarget`, `pioglitazone_trabectedin_mls_ccr2019`,
  `aoc_extrahepatic_delivery_abt2026`), so route 6's myxoid-liposarcoma precedent and route 2's AOC
  claim are cited from their abstracts and the search record rather than from fetched full text, and
  should be re-verified against full text before either enters a manuscript. The 2023 fusion-frequency
  series was re-fetched successfully on PubMed and **its percentages are verbatim-verified**: of 58
  EMCs, *"46 (79 %), 9 (16 %), and 2 (3 %) cases harbored EWSR1::NR4A3, TAF15::NR4A3, and TCF12::NR4A3
  fusions, respectively"*, plus 1 (2 %) with no identifiable partner.
- ⚠ **One citation in an earlier draft of this memo was wrong and was caught by fetching it.** The
  6-MP/AF-1 closure initially pointed at PMID 12709434, which is a paper about an apolipoprotein E
  peptide; the correct id is 12709428. It is recorded here rather than silently fixed because it is
  the case for routing every closure through fetch-and-quote instead of a search summary — and because
  the RXR closure, written the same way, came back verbatim and stands.
- ⭑ **W1 grades a POSITION, never a person's willingness.** Nobody has been approached for any route
  in this memo — outreach is outward-facing and gated by CLAUDE.md §3 — so every W1 statement is an
  argument about why a group *would have reason* to want a result, and none of them is evidence that
  any group will do anything. A strong W1 with nobody contacted is still an unrun experiment, which
  is why W1 cannot by itself put a route in Tier 1.
- ⭑ **Axis D is a judgement, not a measurement, and it is the axis doing the most work here.** "What
  we end up holding" is graded from what is already committed to this repo (an existing manuscript,
  a committed artifact, a preregistration) versus what would have to be written from nothing. That
  is checkable, but the *weighting* of a certain small product against a contingent large one is a
  preference about the operating regime, stated in §2's trade-off block so it can be overruled.
- **This memo does not re-rank the portfolio.** [`emc-treatment-strategy.md`](./emc-treatment-strategy.md)
  owns that, on its own two axes and for a different question (what could help a patient), and where
  the two differ it wins.

---

## 6 · APPENDIX — the superseded ranking, and what was wrong with its axis

*★ **APPENDIX, per CLAUDE.md §1.2.** Kept so the first ranking stays quotable and is never silently
dropped; kept **out of the live text** so it stops competing with the corrected one. ⛔ **Do not cite
anything in this section as current.** Registered alongside the repo's other retired plan framings in
[STRATEGY.md Appendix B](../../STRATEGY.md#appendix-b--superseded-strategy-framings).*

### 6.1 · What the first ranking assumed

| the assumption | where it lived | why it was wrong |
|---|---|---|
| **A collaborator with a bench exists who will run the winning experiment**, so the right question is which experiment is cheapest and most decisive **for them** | **Axis W — "the wet-lab ask. How cheap, how decisive, and does the reagent and the model already exist?"** | trimcrae is a private individual: **no lab, no institutional affiliation, no committed collaborator**, and paying four figures for a contracted assay whose failure he could not interpret is ruled out. **Cheapness is conditional on a whoever**, and the whoever is exactly what is missing. An experiment nobody will run has no size |
| **Speed-to-a-tested-candidate is the thing to optimise**, because *"the binding constraint is not idea supply — it is getting anything tested at all"* | the §2 trade-off block, verbatim | The observation is true and the inference from it was backwards. If getting anything tested is the binding constraint **and it is outside our control**, then optimising for it ranks routes by a variable we cannot move. The constraint we *can* move is what this programme can finish |
| **A route with no wet-lab ask has nothing to score on the ask axis**, so it ranks low by omission | route 3's `W (the ask)` cell reading simply **"none"** | Under Axis D "needs nobody" is the highest possible score, not a blank. This is the mechanism by which the methods paper — a complete deliverable — was ranked below two proposals |
| **A route's in-silico half and its wet-lab ask are one route with one rank** | route 1 as a single row | They fail independently and belong to different owners. Merging them let route 1 take #1 on the strength of an experiment nobody had agreed to run, while its genuinely-finished computed half was never graded on its own |

### 6.2 · The superseded tiers, verbatim, so they stay quotable

⛔ **Superseded 2026-08-03. Retained, not current.**

**Superseded Tier 1** — *"start now. Each is $0-to-cheap for us, each produces a paper, and each hands
a lab an experiment it could run in weeks with reagents that already exist."*

| # | route | superseded W (the ask) |
|---|---|---|
| **1** | ATR-inhibitor synthetic lethality, inherited by EMC as a FET-rearranged cancer | catalogue ATR inhibitor, dose–response, 3 existing EMC lines, γH2AX readout |
| **2** | Fusion-junction ASO / siRNA | junction knockdown + parental sparing in EMC lines |
| **3** | The honest methods paper the degrader program has already earned | **none** |

**Superseded Tier 2** — *"high ceiling, one build away, still no wet lab required from us."*

| # | route | superseded reason |
|---|---|---|
| **4** | TCIP / transcriptional chemically-induced proximity on EWSR1::NR4A3 | the field's blocker is "no ligand for the fusion"; ours is the fusion that has one |
| **5** | Covalent probe at C397 — as a REAGENT, not a drug | the cheapest possible form of the one un-buyable requirement (`R4`) |
| **6** | Trabectedin + PPARγ agonist | all-approved-drug combination with an exact precedent in a sibling myxoid sarcoma |
| **7** | SSTR2 / neuroendocrine theranostic | *"the confirm is an existing approved scan, which is the cheapest decisive test in the whole portfolio"* |

**Superseded Tier 3 and Tier 4** are unchanged by the correction except for the four demotions into
Tier 3 and their renumbering; nothing was removed from either.

**Other superseded lines, retained because they are quotable and are now wrong:**

- *"**Grade: ★★ promote, behind Tier 1 only because it still needs a molecule**"* (route 4).
- *"its rank **rises** here for one reason … **the cheapest form of that experiment for a
  collaborator**"* (route 5).
- *"the cheapest **decisive confirm in the entire portfolio**"* as a *ranking* reason (route 7). The
  clause itself remains true on Axis W2 and is still in the live text; what is superseded is treating
  it as sufficient.
- *"**If the program's goal is weighted instead toward originating a novel agent, the correct
  reordering is 2 → 4 → 5 first**"* — the alternative ordering offered in the old trade-off block. It
  is superseded because it re-ranks on *ownership of the molecule*, which the corrected axes do not
  score, and because it puts routes 4 and 5 — the two thinnest on Axis D — ahead of route 3.
- The old §4 ordering, in which **"Draft the methods paper's outline"** was step 5, below three
  ask-side items.

### 6.3 · What actually changed, in one table

| route | first ranking | corrected | the axis that moved it |
|---|---|---|---|
| **3** methods paper | Tier 1 **#3** | **Tier 1 rank 1** | **D** — a complete deliverable needing nobody. Under the old axes "no ask" scored as nothing |
| **2** junction ASO | Tier 1 #2 | **Tier 1 rank 2** *(held)* | **D** — its in-silico arc was already finished and red-teamed, which is the profile the reframe rewards |
| **1a** ATR assessment | *(not separated)* | **Tier 1 rank 3** | **D** — the computed half produces a result either way and is now graded on its own |
| **1b** ATR cell panel | *(not separated; the merged route was #1)* | **Tier 2 rank 4** | **W1 keeps it top of the asks; D is what stops it being top of the memo** — it is the ask, not the deliverable |
| **6** trabectedin + PPARγ | Tier 2 #6 | **Tier 2 rank 5** | **W1 good** (the sibling-sarcoma authors' own class extension), **D thin** — the two disagree and both are reported |
| **4** TCIP | Tier 2 #4 | **Tier 3** | **D = 0 today**, and one free CPU run from moving. W1 is real but contingent on `R4`, which is unanswered |
| **5** covalent probe | Tier 2 #5 | **Tier 3** | **D ≈ 0 and P negative** — its own exposure instrument fails its positive control, so the in-silico half is not readable |
| **7** SSTR2 | Tier 2 #7 | **Tier 3** | **W1** — the smallest possible ask, and no taker who is not a clinician with an EMC patient. **D ≈ 0** |

⚠ **What did NOT change, and must not be inferred from the above.** Every Tier-3 and Tier-4 entry
from routes 8–15 keeps its grounds and its reasoning; the two Tier-4 closures stand on their cited
primary sources and are untouched. §0's organising finding — that every degrader blocker is a
property of the architecture rather than of the target — is **unaffected**, because it is a claim
about the failures and not about who would run an experiment. And **no route was refused, refuted or
removed**: four moved from Tier 2 to Tier 3, which is a statement about what this programme should do
next, not about whether the science is sound.
