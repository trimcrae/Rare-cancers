# The family of paths — synthesis across five independent fan-outs

★ **trimcrae, 2026-08-02: *"fan out about alternative ways we could get to our end goal paper… Use everything
we've learned from our failed tests to help guide what we think would and wouldn't work… I want to make sure
we have a really well considered family of paths and we can start with the ones that are the best
candidates."***

Five agents worked independently on five different axes. This file is the synthesis, not a sixth opinion, and
it is a **queue you can act from**: [§2](#2--tier-1--the-queue) gives every top row a single next action, a
cost, what it settles, and its falsifier. Every number below points at the register or artifact that owns it
(rule 1): [mechanisms](../modalities/selectivity-mechanism-options.md) ·
[framings](paper-framing-options.md) · [targets](target-route-options.md) ·
[instruments](../modalities/instrument-options.md) · [the candidate](../modalities/nr4a3-short-linker-probe.json) ·
[the plan](nr4a3-program-map.md).

⛔ **REVISED 2026-08-03. The 2026-08-02 ranking is superseded and its Tier 1 is not quotable** — ten results
landed in between and four of them reorder the page. The superseded ordering is kept in
[§6](#6--superseded--the-2026-08-02-ranking-and-why-each-row-moved) so nothing is silently dropped.

⚠ **This file amends nothing.** It changes no gate, price, rung, status or claim ceiling
([§0.8 of the roadmap](nr4a3-program-map.md#08--the-six-options-registers--what-they-own-and-the-one-thing-they-may-never-do)).
Where its grade and the roadmap's disagree, **the roadmap binds.** $0 — no GPU, no rental, nothing dispatched.

---

## 1 · What landed since 2026-08-02, and what it did to the page

Ten results, each re-read against its artifact while writing (never off a summary). The right-hand column is
the *consequence for the ranking*, which is the only reason they are listed here rather than in their registers.

| # | what landed | where it lives | what it moved |
|---|---|---|---|
| **L1** | ⛔ **`R3`'s submission gate FAILS.** The generation frame scores harmonized druggability **0.259 against D\* = 0.53**, and it reaches the **generation receptor** — not a frame-fraction. Stated at true strength: **2 of 15** cavities clear the gate (0.667 and 0.259) and the harmonized rule prefers the better-matching, less druggable one. Rule-sensitive, not "the classifier was wrong" | [`r3-generation-frame-harmonized.json`](../modalities/r3-generation-frame-harmonized.json) · [map §5 row `R3`](nr4a3-program-map.md#5--where-each-requirement-stands) | every pose-anchored row now carries the dependency **in its row**, not as a footnote — [§4](#4--the-r3--r5-inheritance-carried-explicitly) |
| **L2** | ★ **The prespecified site is SPLIT across two real cavities** — 4 shared residues, Jaccard **0.21**, centroids **9.853 Å** apart, *further than the gate's own 8.0 Å ceiling*. Pocket 1 = the helix-3 face; pocket 2 = the helix-11/12 face | [`r3-site-choice-audit.json`](../modalities/r3-site-choice-audit.json) ⚠ **branch-only** | ⭑ **and it re-ranks path 2** — see the finding in [§8 C1](#8--cross-checks-taken-while-writing-all-0) |
| **L3** | **The categorical decoy background exists.** 8 gradeable close-paralogue pairs at the 12-atom gate; **exactly-zero in 1 of 8 reach-only, 2 of 6 exposed**. ⛔ The NR4A3 arm is **not comparable** — the pre-registered pLDDT ≥ 70 trim keeps UniProt 427–570, so **C397 is not scored at all**. And **10 of 20** ordered pairs have no target-unique cysteine | [`categorical-decoy-null.json`](../modalities/categorical-decoy-null.json) | path 1 **loses its promised calibration** and keeps its committed result — it drops one place |
| **L4** | **The cryptic pocket discriminates on FREQUENCY, not existence.** All three species detect the cavity; matched over the **same 75 unbiased frames**, NR4A3 reaches D\* in **44**, NR4A1 in **18**, NR4A2 in **21** | [`paralogue-pocket-contrast.json`](../modalities/paralogue-pocket-contrast.json) | categorical form stays dead (`S14`); the **matched ranking** is alive and is one of the few discriminators with no free energy in it |
| **L5** | **NR4A2 is BOUNDED** (MGI, complete-penetrance neonatal lethality, PMID 9092472/9608532) — **and NR4A3's own single KO is lethal too** (PMID 13129926). Across 51 HPA tissues NR4A2 co-expresses with NR4A3 in **47**, is dominant in **0**, unbuffered in **0** | [`nr4a2-sparing-bound.json`](../modalities/nr4a2-sparing-bound.json) | ⛔ **closes the exposure half of the asymmetric brief** — tissue distribution cannot separate target from anti-target, so the NR4A2 constraint must be **molecular**. Path 4 survives in a *harder* form |
| **L6** | **Steric exclusion has TWO usable vectors, not three.** I484→Tyr/Tyr and L534→Phe/Phe clear a **measured** volume bar; **L406→His/His fires on clash but denies less space than the null class's own largest lobe** at conserved R481 | [`steric-design-rule.json`](../modalities/steric-design-rule.json) · [map §10.1 row 24](nr4a3-program-map.md#101--open-rows-ordered-by-what-unblocks-the-most) | path 2 becomes a **built rule with a scorer**, not a measurement — it rises to the top |
| **L7** | ★★ **The steric mechanism does NOT invert.** The NR4A1-sparing ("inverse NR-V04") direction fires at **0.96× its own null** over the same frame, poses and threshold, against the forward direction's **5.34×**. Structural reason: the best forward bulk margin is **+4** heavy atoms; the best inverse margin anywhere is **+1** | [`nr4a1-sparing-axis.json`](../modalities/nr4a1-sparing-axis.json) ⚠ **branch-only** | answers a route trimcrae asked about, **⏸ parked at its own measured null** — and it bounds what path 2 may generalise to |
| **L8** | **The canonical-library question is SETTLED and `5b-T` is invariant to the ruling** — every one of its four candidates is present with identical SMILES in both enumerations | [`nr4a3-linker-library-canonical.json`](../modalities/nr4a3-linker-library-canonical.json) → `release_condition` | two of `5b-T`'s three blockers are gone. ⚠ Its **scope is explicit**: it discharges the row-25 hold **and nothing else** — the rung's geometry still inherits `R5` |
| **L9** | ⛔⛔ **`R14-a`'s cognate-ligand self-control RAN — on `main` — AND FAILED.** 10 targets, **7 pass**; CYP3A4, PXR and PPARG miss by **9.503 / 6.761 / 6.87 Å** against a 2.0 Å recovery criterion. `panel_readable: false`, so **all four SI §S1 anti-target clauses are now measured-unreadable.** MR was added and passes. ⛔ **And a second, independent block:** the NR4A3 ΔG column those published margins subtract **is not committed anywhere in this repo** | [`antitarget-selfcontrol.json`](../modalities/antitarget-selfcontrol.json) ⚠ **`main`-only — absent from this branch** | ★ **the largest single change to the queue.** A $0 instrument repair now gates four sentences the SI already publishes. It was not on this page at all |
| **L10** | ⛔⛔ **`denovo_401`'s pose does not converge.** 6 poses, 15 pairs, pocket-superposed ligand RMSD **median 7.006 Å** (1.605–7.975) — on a **10.4 Å** molecule whose end-for-end flip costs **6.84 Å** and whose random reorientation averages **5.11 Å**. **1 of 15** pairs agrees within 2 Å. The score spread is **0.023–1.227 kcal/mol**, so the score did not choose among them; and 7 pairs whose *receptors* superpose within 1 Å still span the full range. **Cross-method evidence: NONE** — every pose is the same method's top pose | [`pose-convergence-401.json`](../modalities/pose-convergence-401.json) | **`R5` got materially worse**, and `R5` is upstream of paths 1, 2, and rung `5b-T`'s site 1. It is why [§2 row 2](#2--tier-1--the-queue) exists |

⭑ **One sentence holds L1, L9 and L10 together, and it is the most useful thing on this page:** *three
independent results landed on the same molecule in one day* — its generation frame fails its own submission
gate, its pose is not a singular object, and the panel that bounds its off-target scope cannot be read. None
of them is about chemistry. **All three are instrument-provenance results**, which is exactly the class the
[framing register](paper-framing-options.md) says the program is best at producing.

⛔ **And the generalisation from 2026-08-02 survives intact, now with three more instances:** every route that
genuinely reduces the selectivity requirement does so by **leaving the free-energy axis**, not by better pocket
chemistry. The requirement is a *measurement* problem; mechanisms that terminate in a ΔΔG inherit that,
mechanisms that terminate in a geometry, a sequence fact or a shape constraint do not.

---

## 2 · Tier 1 — the queue

**Read top to bottom. Each row is startable without reading the five registers.** `↯ R3/R5` marks a row whose
result is conditional on the pose/site question — carried in the row, per [§4](#4--the-r3--r5-inheritance-carried-explicitly).

| # | path | the single next action | cost | what it settles | its falsifier | ↯ |
|---|---|---|---|---|---|---|
| **1** | ★★ **Repair the anti-target panel, then re-read `R14`** — the self-control failed on 3 of 10 receptors and four published SI §S1 clauses are unreadable until it passes (**L9**) | **Fix the receptor PREPARATION, not the criterion.** The failure was *predicted in advance* by the module's own docstring: `antitarget_prep` emits standard-amino-acid ATOM records only, so **CYP3A4 loses its haem** and ketoconazole's binding mode is a direct Fe–N coordination. Retain the catalytic cofactor, establish whether PPARG/PXR are cofactor cases or large-cavity cases, re-run [`antitarget_selfcontrol.py`](../modalities/antitarget_selfcontrol.py) | **$0** CPU/CI | whether the anti-target scope bound the SI already publishes may be read **at all** — and, separately, whether an instrument this program has quoted for months can dock | the prepared receptors still miss after the cofactor is retained ⇒ the panel's reach shrinks and §S1's four clauses must be rewritten. ⛔ The frozen rule forbids the easy exits: **a failing target may not be dropped, its box may not be re-centred, no band may be lowered** | — |
| **2** | ★★ **Settle the pose/site question** — the pose is not singular (**L10**) and the site route fails in regime (**L11**, [§8 C4](#8--cross-checks-taken-while-writing-all-0)) | **Run a SECOND, INDEPENDENT pose method** on the same ligand in the same receptor. The convergence artifact's own finding is that `cross_method_evidence` is **NONE** — every pose this program holds is one method's top pose, so the disagreement cannot currently be attributed to anything. This is also roadmap [row 4](nr4a3-program-map.md#101--open-rows-ordered-by-what-unblocks-the-most) (site and docking separated) seen from the other side | cheap CPU (a second docking engine) → optionally cheap GPU (a co-fold) | `R5` — and `R5` is upstream of **rows 3, 4 and 6 below and of rung `5b-T`'s site 1**. Nothing else on this page unblocks more | independent methods disagree as widely as the six existing poses ⇒ *"the predicted pose"* is not an object this program is entitled to, and every pose-conditional row above must be restated as marginalised-over-poses | ↯ |
| **3** | ★★ **Steric exclusion / negative design** — now a **built** rule with two vectors and a per-candidate scorer, not a measurement (**L6**) | **Score the committed construct set** through `steric_design_rule.score_pose()` and report which constructs reach the I484 or L534 lobe. The rule reproduces its own source measurement over its own poses, so this is arithmetic, not a new claim. Then route it into [§8 Route A](nr4a3-program-map.md#8--the-two-live-routes-to-selectivity--and-where-each-is-actually-blocked), which row 24 names as the remaining half | **$0** | whether the design rule has a *carrier* — i.e. whether anything in the committed library already occupies the two lobes, or whether the rule is a specification for a molecule that does not exist | no committed construct reaches either lobe ⇒ the rule is a design target, not a property of the current set. ⛔ **Its ceiling is already measured and travels with every score:** the paralogue *relocates* these molecules rather than refusing them, so a high score means **"this POSE is denied"**, never *"the paralogue cannot bind this molecule"* | ↯ |
| **4** | ★ **Categorical covalent at C397 at ≤12 atoms** — the incumbent; a named construct exists | **Close the calibration gap the decoy null left open (L3).** The cross-system background was measured, but the NR4A3 arm through the identical harness scores **C559, not C397** — so no percentile may be quoted for the program's headline residue. Either re-run the NR4A3 arm under a window that contains C397, or state the background as a statement about the **screen** and stop implying it places NR4A3 | **$0** | how special the NR4A3 configuration actually is. ⚠ Today the honest reading is *"at the favourable end of a background of 8 gradeable pairs"* — and **1 of those 8 also returns exactly zero**, so zero is not by itself extraordinary | a C397-containing re-run puts NR4A3 mid-distribution ⇒ the categorical gate is a common configuration, not a discovered one. ⭑ **A result either way:** *10 of 20* pairs have no target-unique cysteine at all, which is itself evidence the configuration is not generic | ↯ |
| **5** | ★ **Write the brief asymmetrically — in its HARDER, measured form** (**L5**) | **Restate the brief without the exposure lever.** NR4A2 is now bounded (a cited floor exists) *and* co-expressed with NR4A3 in 47 of 51 tissues with **zero** tissues where it is dominant or unbuffered — so *"treat the residual as an exposure question rather than a chemistry question"* is no longer available. The brief becomes: **hard vs NR4A1, hard-but-lower-priority vs NR4A2, both molecular** | **$0** | the design target itself. No result can invalidate a brief; what today changed is which half of it is honest | ⛔ **What would reopen the exposure half:** single-cell or region-resolved expression. The artifact flags its own limit — **bulk tissue averages dilute a small nucleus**, and the dopaminergic liability lives in one | — |
| **6** | **Widen the categorical enumeration** — 35 unique alignment-robust LBD positions across 11 reactive classes, 31 within linker reach | **Take the threshold-free rank as the roadmap mandates and stop quoting both rulers as equals.** Under the `V17` cutoff **no new handle clears at all**; under the rank the roadmap says must *replace* it, **Y419** (SuFEx tyrosine, one residue from C420) sits **above** NR4A1 Cys551 — the family's one literature-anchored covalent site and the very false negative that discredited the cutoff. **M398/M399 fall below the reference on both readings and are dropped, not carried** | **$0** | whether Route B's single point of failure is a fact about the protein or a gap in the enumeration. It is the latter | chemistry credibility is a literature label, not a computed quantity. SuFEx tyrosine is *precedented rather than routine*, and every added handle re-opens the chemoselectivity-window question `S1` already answers uncomfortably | ↯ |

⚠ **Rows 1 and 2 are the two that changed category.** Everything else on this queue is a *mechanism*; those
two are **instrument repairs that gate numbers already in print**. That is the shape of the day's results, and
a queue that buried them under mechanisms would be reporting the wrong thing.

---

## 3 · Tier 2 and Tier 3

### Tier 2 — strong, but gated on something

| # | path | gate, as of today |
|---|---|---|
| 7 | **Ternary rung `5b-T`** (`V2`→`V1`, each having recovered a known answer in scope) | ✅ **Two of three blockers cleared (L8)** — the library ruling settles which enumeration is canonical and the rung is invariant to it. ⛔ **Two remain, and one is new:** its site 1 *is* the docked pose row 2 is about (↯), and its own assembled-inputs artifact [`nr4a3-5bt-frame.json`](../modalities/nr4a3-5bt-frame.json) **does not parse** — see [§8 C2](#8--cross-checks-taken-while-writing-all-0) for the root cause |
| 8 | **Ligand-side ΔΔΔG as a named instrument** (`C01`) | unchanged: needs a paralogue-scale known-answer benchmark; two $0 searches decide whether one is buildable. It inherits **no** validation from `V6` — the [double-difference analysis](../modalities/instrument-options.md#2--the-double-difference-analysis) is the one home of why |
| 9 | **`barnase_barstar_W35F`** — the only probe of the ~1 kcal/mol regime | priced and staged. ⛔ **Its authorization is moot**: the $0 precheck **refused it on evidence** (`STOP_NO_REFERENCE`) for the application it was authorized for. What survives is the *engine* question, and it licenses nothing about paralogues directly |
| 10 | **Covalent inhibitor rather than degrader** at C397 | ⭑ unchanged and still under-run: the 30-of-30 counter-result was computed for a molecule that must **also** present an E3 arm, and **an inhibitor has none**. The enumeration has never been run in that configuration; it is free CPU and one fewer terminus to satisfy. Retires the ternary/ubiquitin stack; loses the degradation mechanism |

### Tier 3 — real, but they change what the paper is

| # | path | note |
|---|---|---|
| 11 | **Junction ASO / junction neoantigen** | genuinely removes the paralogue requirement. ✅ The ASO lane was **corroborated** by the exon audit (its deliberate refusal of the exon→CDS mapping bracketed the correct answer). ⚠ The neoantigen lane still owes a correction — its 26 binders span seams that do not exist |
| 12 | **TCIP** | retires `R9`/`R10`/`R12`; keeps `R4`/`R5`/`R7`. Its citation is still an auto-captured lead and must clear `verify-refs` before any manuscript quotes it |
| 13 | **Downstream / dependency target** (PPARG axis) | removes the requirement by leaving the target. Stalled on one **literature** question — agonism vs antagonism — that nobody has spent an hour on, and that is a CI job, not a compute job |
| 14 | **Ex-vivo pan-NR4A pole** | ⛔ the only place in the program where the cross-reactivity everything else exists to avoid is the **design goal**. Already banked, still under-used *as an argument* |

---

## 4 · The `R3` / `R5` inheritance, carried explicitly

**This section exists because a dependency stated once, in a footnote, is a dependency that gets dropped.**

`R3` asked whether the receptor frame the carried candidate was generated into still qualifies. **It does not**
(L1). Two things must be said in the same breath, because saying either alone is misleading:

1. ⛔ **It reaches the generation receptor**, not a reported frame-fraction — the paper's own sentence. Every
   result whose geometry starts from that frame inherits it.
2. ⭑ **It is repairable without new MD, and the repair is not mine or any agent's to make.** 44 of 75 unbiased
   frames clear D\* on the mapped site, and the program's own selector re-run returns a specific qualifying
   frame. **Re-anchoring is a judgement call about a preregistered artifact**, which is why the audit that
   found it declined to take it and routed it instead.

**What inherits what.** ⚠ The two dependencies are *different* and have been conflated:

| row | inherits `R3` (the **frame** fails)? | inherits `R5` (is the **site** right, is the **pose** singular)? |
|---|---|---|
| Tier-1 row 3 — steric exclusion | **No.** It is scored on the matched opened-LBD frame, not the generation frame | **Yes**, and explicitly: the rule is conditional on the cryptic pocket being the site, and `V3` returned INCONCLUSIVE on site selection |
| Tier-1 row 4 — categorical covalent | **No** for the reach statistic (enumeration over ensembles) | **Yes** for the exit vector — the warhead anchor is marginalised over pocket-mouth anchors rather than taken from a docked pose |
| Tier-1 row 6 — widened enumeration | **No** | **Yes**, identically to row 4 |
| Tier-2 row 7 — rung `5b-T` | **Indirectly** — its site 1 is a docked pose in a frame from the same family | **Yes, directly.** Site 1 *is* the pose L10 measures |
| the paralogue ABFE legs, `5c`, `5d` | **Yes** — all are anchored on the carried candidate in that receptor | **Yes** |
| Tier-1 rows 1, 5 | **No** | **No.** Both are sequence/data-level and pose-free — which is exactly why they are at the top of the queue |

⭑ **The observation that makes this section worth reading rather than skimming.** L2 found the prespecified
site is split across **two** real cavities, and [§8 C1](#8--cross-checks-taken-while-writing-all-0) reports
which residues went where. **Row 3's two surviving vectors are in the cavity that PASSES the gate; the
positions that failed the steric test are in the cavity that fails it.** That is not a rescue of `R3` — the
frozen rule's answer stands and was not touched — but it does mean row 3 and the failing gate are pointing at
*different halves of the same split site*, which no document said before.

---

## 5 · The paper-framing question — elaborated, because it is a genuine fork

⚠ **The framing sweep's recommendation is NOT the paper being written**, and this page previously reduced that
to a pointer. It is a live decision with real consequences, so each candidate is stated here with (a) what
already supports it, (b) what it still needs, and (c) **what today changed about it** — the last column being
the reason a 2026-08-02 pointer was not good enough. Every grade and figure is owned by
[paper-framing-options.md](paper-framing-options.md); this is the decision view over it.

| id | framing, in one line | what already supports it | what it still needs | ⭑ what 2026-08-03 did to it |
|---|---|---|---|---|
| **P1** | **The known-answer audit** — the instrument register is the subject; NR4A3 is the worked system | ✅ **Its central claim needs no instrument to pass, because the failures ARE the result.** A decoy null replicated at two scales; a *proof* that the program's favourite convergence diagnostic is blind to the defect it was used to exclude; a threshold that fails its own positive control; a blind-docking benchmark that measured the box | **two $0 items**: bring the decoy null's primary output into a committed artifact, and one census artifact holding all instruments with test/result/scope | ⭑ **STRENGTHENED, three ways.** L1 and L9 are two more known-answer tests run to completion, both returning failures that reach **published** numbers; L10 is a third. And the day produced **two fresh instances of the audit's own rule (b)** — *persist the primary artifact*: the panel's ΔG column exists only in S3, and `5b-T`'s inputs artifact was destroyed by an unserializable object ([§8 C2](#8--cross-checks-taken-while-writing-all-0)) |
| **P2** | **Where sequence-only co-folding breaks on ternary complexes** — components right, assembly wrong, by a factor of ten | ✅ 100 % committed, calibrated in **both** directions (a positive control upward, a rigid-displacement ruler downward), and localised to the *relative placement of the two proteins* | nothing the claim needs. Two disclosures are mandatory and already written | **unchanged — and it is still the only framing with a live clock.** It ages; nothing else here does |
| **P3** | **Target enablement** — the cryptic pocket, its divergence, its unique chemistry, **no candidate** | ✅ an experimental anchor independent of our machinery (8XTT); dynamics reported at the weight the gates returned; the divergence census; Lane 13, unpublished | the `V17` disclosure must appear in the manuscript | ⚠ **MIXED, and it is the framing today moved most.** ✅ One named blocker is **discharged** — `nr4a-resistance-map.json` is now on `main`, so the ortholog-invariance sentence has an artifact (the *"~300 My"* figure still needs a source or must go). ⛔ Against it: L1 and L2 mean a dossier must now say the site is **split across two cavities** and that the frame the program generated into does not clear its own gate. **That is a better dossier, not a worse one** — but it is a rewrite |
| **P4** | **The resolution budget** — prospective paralogue selectivity is not currently decidable by free energy | ✅ arithmetic over measured quantities: required ≫ resolvable, and the one calibration attempt on the relevant quantity class missed **in the wrong direction** | nothing. Two caveats must travel with it | **unchanged.** Recommendation stands: it is **P1's spine**, not a separate paper |
| **P5** | **Categorical > marginal** — a close-paralogue design principle, with linker length as the filter | ✅ the linker-length filter at its landed values, and a self-auditing scope statement: at the 12-atom gate the claim stands on **reach alone** | ⛔ **the transferability claim has no evidence in this repo.** The cross-family survey that would fix it is $0 CI and exists on no rung | ⚠ **Partly supplied and partly undercut.** L3 gives the principle its first **cross-system background** — the thing it most lacked. But that background's NR4A3 arm does not contain C397, and L7 shows the sibling mechanism **does not invert**, which bounds how general "categorical" is allowed to sound |
| **P6** | **The candidate paper** (the current plan) | a falsification-controlled funnel with a preregistered gate ladder, a disclosed deviation log, and a published record of its own retractions | ⚠ a bench, at `R4` — which has no in-silico instrument and never will | ⛔⛔ **MATERIALLY WORSE, and this is the sharpest change on the page.** Its sole carried candidate took **three independent hits in one day**: generation-frame gate failed (L1), pose not convergent (L10), anti-target scope bound unreadable (L9). **P6 is still not *wrong* — it is mis-titled**, and the gap between its title and its own Limitations section just widened |
| **P7** | **The benchmark / infrastructure suite** | the register, the coverage matrix, the invariants, the claim-ceiling rule, the linters, the preregistrations | **n = 1** — a benchmark is a benchmark when someone else runs it on something else | **unchanged.** Ship it as P1's Data & Software Availability section, where the apparatus is evidence rather than product |

**How to make the choice, stated as a decision rather than a preference.** Three tests, in order, each of
which the operating regime makes binding:

1. **Does its central claim need an instrument that has passed in the regime the claim needs?** P1, P2, P4 and
   P7: no. P3: partly. **P6: yes, and 0 of 16 requirements stand on one.**
2. **Does its headline need a bench?** Only P6 does — at `R4`, the one row on the whole board that **cannot be
   bought at all**. Under *one researcher, no wet lab, ever*, that is structural, not a scheduling fact.
3. **Does it require softening a claim already in print?** Nothing is in print, which is the whole opportunity.
   P1/P2/P3 *remove* the claim the substantive lint warnings attach to rather than hedging it.

⇒ **P1 leads on all three, and today's results widened the gap rather than narrowing it.** ⚠ But this page
does not decide it, and **no Tier-1 row waits on it** — the mechanism, instrument and requirement work
strengthens whichever paper is written. The decision is trimcrae's, and it is
[§13 of the roadmap](nr4a3-program-map.md#13--the-deliverables-framing--an-open-question-with-a-register-and-no-decision).

⚠ **The one genuine risk of splitting, named rather than discovered:** a parallel condensed draft drifted out
of sync and self-contradicted once already. Splitting is safe only if every shared number has exactly one home
and is read from a committed artifact, never copied between drafts.

---

## 6 · Superseded — the 2026-08-02 ranking, and why each row moved

⛔ **Do not quote the ordering below.** It is retained because a ranking that changes silently is worse than one
that changes loudly (rule 1.2).

| was | path | now | why it moved |
|---|---|---|---|
| **1** | Categorical covalent at C397, ≤12 atoms — *"⏳ falsifier `C02`, running"* | **4** | `C02` **landed and did not falsify it** — but it also showed the NR4A3 arm through the identical harness never scores C397, so the calibration the row was waiting for arrived aimed slightly off-target (L3) |
| **2** | Steric exclusion / negative design | **3** | **Rose in strength, fell one place.** It gained a built rule, a scorer and a measured volume bar (L6) and lost one of its three vectors; it is now behind two rows that gate numbers already in print |
| **3** | Widen the categorical enumeration | **6** | unchanged on its merits; overtaken |
| **4** | Write the brief asymmetrically | **5** | **survived in a harder form.** L5 bounded the NR4A2 half *and* closed its exposure lever, so the row is more honest and less free-lunch than it was |
| **5** | Ligand-side ΔΔΔG (`C01`) | **8** | unchanged |
| **6** | Ternary rung `5b-T` — *"⛔ CRBN corridor conflict; library no longer reproduces"* | **7** | ⚠ **both stated blockers are resolved** (L8), and one **new** one was found that is worse than either: its inputs artifact does not parse ([§8 C2](#8--cross-checks-taken-while-writing-all-0)) |
| **7** | `barnase_barstar_W35F` — *"priced, staged, **authorized**"* | **9** | ⛔ **the authorization framing is superseded**: the $0 precheck refused it on evidence for the application it was authorized for |
| **8** | Covalent inhibitor rather than degrader | **10** | unchanged |
| — | *(not on the page)* | **NEW 1** | the anti-target panel repair — the self-control **ran and failed**, on `main` (L9) |
| — | *(not on the page)* | **NEW 2** | the pose/site question — `denovo_401`'s pose is **not singular** (L10) |

**Also superseded from the 2026-08-02 text, retained:** the header block *"⏳ ONE INPUT IS STILL OUTSTANDING…
`C02` is running… Nothing here is final until that lands"* — it landed (L3). And *"the cryptic pocket is
NR4A3's edge → refuted; fpocket rates NR4A1's opened frame more druggable"*: still true **of the opened
frames**, and now sitting beside L4's matched-ensemble ranking, which points the other way on **frequency**.
Both readings are live and they are not in conflict — one is about a state, the other about how often it is
reached.

---

## 7 · Closed vs weakened — the strict bar applied

⛔ **The bar for ✕ is POSITIVE EVIDENCE OF IMPOSSIBILITY.** *"The measurements we already have close this"* is
**⏸**, not ✕ — [§6 of the roadmap](nr4a3-program-map.md#6--the-closed-route-register) is stricter than any
register, and it has already re-graded three routes their own authors marked closed. Applied honestly, today's
results close **less** than they look like they close.

### ✕ Closed — positive evidence, do not re-propose

| what | the positive evidence |
|---|---|
| **L406 as a steric design vector** | its denied lobe is **smaller than the null class's own largest lobe at a conserved arginine**. The space both paralogues deny there is denied by NR4A3 too, so there is nothing for a substituent to occupy. The bar is **measured, not chosen** |
| **M398/M399 as covalent handles** | below the reference site on **both** rulers — the cutoff and the threshold-free rank. Enumerated and dropped, not carried |
| **Degradation-competence via lysine availability** · **pocket-opening as a categorical claim** · **relocating to the DBD** · **fusion-selective ubiquitination** · **E3 choice as a lever** · **molecular glue** | closed 2026-08-02, each on a committed measurement; unchanged today |

### ⏸ Weakened, parked or blocked — with a named trigger, **not** closed

| what | why it is ⏸ and not ✕ | what would reopen or repair it |
|---|---|---|
| **`R3`'s generation frame** | the frame fails — but **44 of 75** unbiased frames clear D\* and the selector returns a qualifying one. That is a **re-anchoring decision**, not an impossibility | re-anchor to a qualifying frame, or state every downstream result as conditional on a frame that does not clear the gate. Free either way; it is a judgement, not a computation |
| **`denovo_401` as "the" pose** | 6 poses of one method spread 7 Å; that bounds how singular the pose is **entitled** to be. It does not say no pose is right | Tier-1 row 2 — an independent second method |
| **SI §S1's anti-target margins** | `panel_readable: false` is an instrument statement, and the named cause is a **preparation** defect with a predicted mechanism | Tier-1 row 1. ⛔ Note the *second*, independent block: the NR4A3 ΔG column is not committed anywhere, so even a passing control leaves the margins non-re-derivable from this repo |
| **NR4A1-sparing (the "inverse NR-V04" profile)** | ⏸ **measured at its own null**, on **one static conformer per species**. The conformer-independent half — no NR4A1-unique lining position exceeds a **+1** heavy-atom bulk margin — points at ✕ and is a fact about the protein, but +1 is not zero | an ensemble in the NR4A1 direction; poses docked into NR4A2 as the design frame; or a site other than the cryptic pocket |
| **Tissue distribution as an NR4A2 lever** | **0 of 51** tissues where NR4A2 is dominant or unbuffered is a strong measured absence — but the artifact flags its own limit: **bulk averages dilute a small nucleus**, and the liability lives in one | single-cell or region-resolved expression. ⚠ **The design consequence is settled regardless: the brief may not rest on it** (Tier-1 row 5) |
| **The categorical decoy percentile for NR4A3** | 8 gradeable pairs is coarse, and the NR4A3 arm does not contain C397 | Tier-1 row 4 |

---

## 8 · Cross-checks taken while writing (all $0)

Per CLAUDE.md §4 — *a $0 observation is never "watching"*. Each was cheap, so each was taken. **Four changed a
sentence in this file and two are findings this file did not go looking for.**

| # | check | result |
|---|---|---|
| **C1** | ⭑ Cross-referenced L2's split-site residue lists against L6's two surviving steric vectors | ★ **NEW FINDING.** The two cavities partition the prespecified lining set almost cleanly, and **the split is not neutral**: the cavity that clears D\* uniquely holds **I484 and L534** — *exactly* row 3's two design vectors — while the cavity that fails uniquely holds **T407, T410, P411, R412**, which are exactly the `unique_not_bulkier` positions that fire at **0.000** on the steric test and are electronic rather than steric handles. Reported in [§4](#4--the-r3--r5-inheritance-carried-explicitly); it changes no rule and rescues no gate |
| **C2** | ⛔ Parsed [`nr4a3-5bt-frame.json`](../modalities/nr4a3-5bt-frame.json), the assembled-inputs artifact for rung `5b-T` | ⛔ **NEW FINDING — IT DOES NOT PARSE**, and the root cause is diagnosed rather than guessed: it is truncated **mid-key at `"_mol":`**, and `nr4a3_5bt_assemble.py` returns a raw RDKit `Mol` object under that key. `json.dump` writes incrementally, so it emitted the document up to that point and then raised on the unserializable value. The file is committed in that state on this branch and **absent from `main`.** ⚠ Reported, **not fixed** — that lane is held by a suspended agent — but it belongs in Tier 2 row 7's gate, not in a footnote |
| **C3** | Re-read L4's contrast rather than quoting the brief that commissioned this file | ⚠ **The brief's comparison mixes ensembles.** *"44/75 unbiased against NR4A1's 4/25 metadynamics"* pairs a pooled unbiased figure with a biased one. The **like-for-like** matched-unbiased triple is **44 / 18 / 21 of 75**, and the matched metadynamics triple is **17 / 4 / 7 of 25**. Both support the ranking; **mixing them is the same error class the mechanism register already corrected once** (its `M1` ensemble-label correction). This file quotes the matched values only |
| **C4** | Read [`apo-pose-site-in-regime.json`](../modalities/apo-pose-site-in-regime.json) — the row-4 site question re-asked in regime | ⛔ **L11, and it is why Tier-1 row 2 exists.** Of 14 gradeable in-regime apo/holo pairs, the pipeline's **sequence** transfer put the crystallographic ligand inside its own box in **0**, its **Pocket-5 structure** transfer in **0**, and an **fpocket-chosen** box in **11**. Two independent site routes, both zero. ⚠ It is explicitly a **site supplement, not a panel verdict** — it emits no RMSD and does not change the preregistered INCONCLUSIVE |
| **C5** | Checked which ref each cited artifact actually lives on, before writing any claim from it (CLAUDE.md §7) | ⛔ **BRANCH DRIFT IS LIVE, IN BOTH DIRECTIONS, ON THE SAME DAY.** `main`-only: [`antitarget-selfcontrol.json`](../modalities/antitarget-selfcontrol.json) — **the largest result on this page is absent from the branch these registers were written on.** Branch-only: `r3-site-choice-audit.json`, `pocket-accepted-candidates.json`, `nr4a1-sparing-axis.json`, `apo-pose-site-in-regime.json`. Every claim above that rests on one of these **says which ref it is on** |
| **C6** | Re-read the R3 harmonized artifact on **both** refs, because the branch copy is 3× the size | the **verdict is identical on both** (`GATE_A_FAIL_BELOW_DSTAR`, same score, same D\*). The branch adds the pocket-identity and split-site blocks. So L1 may be quoted from `main`; **L2 may not be** |
| **C7** | Verified the framing register's four must-fix items against the live tree | **1 of 4 is now DONE**: `nr4a-resistance-map.json` is on `main`, so P3's ortholog-invariance sentence has an owning artifact. The other three stand — the SI heading, the `V17` disclosure, and the decoy null's S3-only primary output |
| **C8** | Checked whether the panel-completion half of `R14-a` was still outstanding | **No — MR/NR3C2 was added on `main`** (resolved by a live RCSB query under written rules, never from memory) and it **passes** the self-control. The roadmap row's *"MR is not in the panel"* is stale; what remains is the three failing receptors |

---

## 9 · Which single path I would start tomorrow

> ### ⭑ **Tier-1 row 1 — repair the anti-target panel.**
> **First action:** retain CYP3A4's catalytic cofactor in `antitarget_prep`, establish whether PPARG and PXR
> fail for the same reason or a different one, and re-run the cognate-ligand self-control.

**Why this one, over the two that look more scientific.** Four reasons, in the order they bind:

1. **It is the only item on the page where a sentence already written into the SI is currently unreadable.**
   Everything else changes what a future paper *could* say; this changes whether four clauses in the present
   one may be read at all.
2. **It is $0, the harness exists, and it contains no decision.** Rows 2 and 3 both need a judgement (re-anchor
   or not; which frame) or a second method. This one is mechanical.
3. **Its failure was predicted in advance, in writing, by the module that then measured it** — a receptor
   stripped to standard amino acids loses a haem, and the reference ligand's binding mode is a direct metal
   coordination. That is the strongest possible starting position for a repair: a named mechanism, not a search.
4. ⛔ **And the honest reason it is first rather than second:** three results landed on the carried candidate in
   one day. The right response to that is **not** to advance more candidate-conditional work — it is to take
   the free instrument repairs that gate numbers already in print, and let rows 2 and 3 follow once the pose
   question has an answer.

**Runner-up, and it should run in parallel because it is independent and also $0:** Tier-1 row 3 — score the
committed construct set against the two steric vectors. It is the only Tier-1 row whose *evidence got stronger*
today, its scorer is built and self-checked against its own source measurement, and nothing about it waits on
row 1 or row 2.

⛔ **What I would NOT start tomorrow, and it is the most useful negative here:** rung `5b-T`. It reads as the
obvious move — the roadmap calls it the program's largest open gap, it costs $0, and its stated blocker was
cleared today. But its inputs artifact does not parse (C2) and its site 1 is the pose that just failed to
converge (L10). **Running it now would spend free compute producing a result conditional on two things that are
about to change.**

---

⛔ **Nothing in this file licenses a selectivity, efficacy, safety, therapeutic-window or clinical claim, and
none of those is computed anywhere in it.** No claim of proteome-wide selectivity is made or implied; the
comparison set throughout is NR4A1 and NR4A2, and the program's own scope is separately bounded by a
cross-binding check whose instrument [§2 row 1](#2--tier-1--the-queue) reports as currently unreadable. The
candidate is a target-engagement geometry result: no binding affinity has been measured or computed for it, no
ternary has been assembled with it, and the pocket it targets has never been shown to bind anything at all.
Rankings here are for **planning**; a rank is not evidence, and a top row is still an unvalidated prediction
under the roadmap's claim-ceiling rule.

*Revised 2026-08-03 on `claude/nr4a1-protac-positive-control-xnszjl`. $0 — committed artifacts only, no GPU, no
rental, nothing dispatched. No register and no roadmap section was edited by hand; the map edits are routed in
[`path-family-synthesis-map-edits.json`](path-family-synthesis-map-edits.json) through `route_map_edits.py`.*
