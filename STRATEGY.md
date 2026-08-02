# STRATEGY — the NR4A3-selective degrader paper

> # ★ THE APPENDIX SET AND MACHINE-PARSED LAYER OF THE ROADMAP ★
> ## ★ READ [nr4a3-program-map.md](research/manuscripts/nr4a3-program-map.md) FIRST — IT IS THE ROADMAP
> **The one document a person reads top-to-bottom to know what is done, what is true, what is blocked and what
> is next is the roadmap.** It carries the requirement register (`R*`), the instrument register (`V*`), the
> dependency graph, the closed-route register and **the single ordered list of what to do next** — the union of
> what used to be this file's decision-value ranking and the map's critical path, which shared zero items.
>
> **This file is its APPENDIX SET.** It owns, and is the one home for: the ordered plan, the spend ladder and
> its derivation, the validation architecture, the language-discipline rules, the gate scoreboard, the open
> decisions, and the history in Appendices A and B. ⛔ **The roadmap LINKS to these; it does not restate them,
> and they do not restate it.** A figure appearing in both is the bug rule 1 exists to catch.
>
> ⚠ **WHY THE SPLIT IS STRUCTURAL AND NOT PHYSICAL — this is measured, not caution.** Seven CI checks parse
> this file **by exact heading string and text format**, 100 files carry 358 inbound references to it, and two
> of its numbering schemes are read **as data**: `realised_spend.py` sets `"read_from": "STRATEGY.md Appendix A
> row 35"`, and Open decision numbers are cited by 30 files with nothing resolving either. **Moving any of it
> would break CI quietly rather than loudly** — renaming the ordered plan's heading makes `work_ledger` print
> *"NOT SCANNED — the plan is invisible this run"* and every open item vanishes from the work board with no
> error. The roadmap's §0.7 is the index of which appendix owns what and which machine reads it.
>
> **Precedence, unchanged in substance:** for a **cost, a gate, a plan marker, a decision number or a
> superseded value**, this file wins over any other doc — reconcile the other doc to it. For **what blocks
> what, what an instrument may support, and what to do next**, the roadmap wins. Where they appear to
> disagree, the committed artifact settles it and both are the bug.
>
> **Sections below carry a one-line appendix designation naming their role in the roadmap.** No heading, slug,
> row number or decision number has been changed, and none may be.
>
> **Keep it current.** When work lands: update the stage's `[ ]/[~]/[x]` status here AND the mirrored `status` in
> [degrader-paper-schedule.json](research/manuscripts/degrader-paper-schedule.json) (its milestone `id`s match the
> stage tags below one-for-one; that JSON is a machine MIRROR of this file, not a competing source).
>
> **Three editing rules that keep this file from rotting** (it has been re-corrected three times; the failure
> was always the same — a number lived in four places and a fix reached one):
> 1. **One fact, one place.** Every number, gate and decision has exactly one home section. Everywhere else
>    points at it. If you find yourself restating a cost, delete the restatement.
> 2. **Corrections go in [§Appendix A](#appendix-a--superseded-numbers-and-retracted-claims), not inline.** Never
>    quietly drop a superseded number — but never leave the retraction narrative in the live plan either. One
>    line in the appendix, then the live text carries only the current value.
> 3. **Register the old value when you change a pinned one**, in the same commit, in
>    [`pinned-figures.json`](research/manuscripts/pinned-figures.json). Rules 1–2 are *enforced* by
>    [`lint_consistency.py`](research/manuscripts/lint_consistency.py) in CI — it fails the build when a total
>    does not equal its parts or a superseded value is restated unmarked. Run it before you commit:
>    `python3 research/manuscripts/lint_consistency.py`.
>
> **Companion docs (detail only, subordinate to this file):**
> [research/compute/pricing.md](research/compute/pricing.md) — ★ PRICING single source of truth, every cost line
> linked to its justifying test · [research/compute/bid-strategy.md](research/compute/bid-strategy.md) — host
> selection and bidding · [reviewer verdict](research/manuscripts/nr4a3-degrader-reviewer-revisions-2026-07-15.md)
> (verbatim) · [ternary-first strategy note](research/manuscripts/nr4a3-degrader-strategy-ternary-first.md)
> (biological/chemotype rationale) · [**ternary-selectivity strategy revision
> 2026-07-24**](research/manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md) (evidence behind
> the mechanism-first search and the six cost levers) ·
> [the manuscript](research/manuscripts/nr4a3-degrader-paper.md) itself.

---

## 📊 WHERE WE ARE — the scoreboard, in plain language

*★ **APPENDIX — the gate scoreboard.** The one home for every gate's verdict sentence, the deliverables table, realised spend, and ⛔ **which controls failed**. The [roadmap](research/manuscripts/nr4a3-program-map.md) §3 cites this table and must never restate it. Read by `realised_spend.py`.*

*Read this before the IN FLIGHT table. **Every status line in this file, and every lane report, must be
expressible as one of: a gate PASSED, a gate FAILED plus the remediation, or a DELIVERABLE done.** If a finding
cannot be written that way it is a detail, not a headline. trimcrae, 2026-07-26: "a headline should be
something like *we passed n gates*, or *we failed x gate and need to make y remediation*, or *we have a major
deliverable done*" — internal shorthand like "term (a) went 7 → 0" is **not** a headline, it is the evidence
underneath one.*

**As of 2026-08-02 3:30 AM ET · 7 gates passed · 4 failed · 1 DELIVERED BUT NOT GRADED
(the Step 1 fan-out map; ⚠ and one of its three cycles does not close) · 4 deliverables done and 1 PARTIAL ·
NOTHING BILLING on Vast · realised spend $84.49 machine-ledgered.**

> ### ⛔ THE ONE HOME FOR "WHICH CONTROLS FAILED" — READ THIS BEFORE COUNTING NULLS
>
> **Four results are routinely confused with each other, and three of the four are nulls of some kind.**
> They have DIFFERENT statuses and only two are failures. This table exists because summing them into
> "everything came back null" is a category error §5(b) of the paper explicitly wrote itself to prevent:
> *"without it, a predictable null becomes a verdict on the whole program through a category error."*
>
> | # | what it was | result | status |
> |---|---|---|---|
> | 1 | **valB_mini** — the FEP-side cooperativity calibrator (paper §2.11) | ΔΔG_coop = **−0.599** against a target of **+0.944** — the WRONG SIGN in all three preregistered replicates, ~34× the statistical uncertainty, so systematic and not a sampling deficit | ❌ **CONTROL FAILED** |
> | 2 | **selcal SMARCA2/4** — the endpoint-MD-side sensitivity control (§2.12a) | tier **NULL**, exact one-sided *p* = **0.7468**, **zero** technical failures, reference-set floor 0.00216 vs α = 0.05 | ❌ **CONTROL FAILED**, on an adequately-powered design |
> | 3 | **NR-V04 retrospective** — the biological holdout (§2.12) | tier **DISCORDANT**, *p* = 0.392857 — a NON-RESOLUTION, and covalency-confounded (Cys551 is unique to NR4A1) so it could never have been a positive control at ANY *n* | ⚠ **NON-RESOLUTION**, never a candidate control |
> | 4 | **RUNG 5a-KS** — the causal kill-switch (§2.10e) | **S = −0.1297 ± 0.3264 kcal/mol**, indistinguishable from zero | ✅ **NOT A FAILURE — its PREREGISTERED null**, registered in advance as the LIKELY outcome and explicitly NOT a stop |
>
> **Why #4 is not a failure, structurally and not charitably.** The Tier-3 double difference is an ordinary
> non-covalent alchemical quantity: it models no bond in either leg, so it is **structurally incapable of
> testing the categorical mechanism** the paralogue claim actually rests on. It can only see the *marginal*
> wedge, whose expected size (~0.5–1.5 kcal/mol, one partly-buried hydrogen bond) was registered in advance
> as likely to be unresolvable. It came back as a **BOUND** — excluding ≳ 0.65 kcal/mol at 2σ — because its
> design condition (two seeds per arm) was met.
>
> **What IS bad, and it is #1–#3 together, not #4.** After three attempts there is **no working positive
> control** for selectivity detection, and no fourth candidate is staged. That is why every
> paralogue-selectivity statement in the paper is an **unvalidated prediction** — and it is also what makes
> #4 uninformative *about the method*: an uncalibrated instrument returning zero cannot distinguish "there
> is no wedge effect" from "this method cannot resolve the wedge effect".
>
> ⚠ **#1 AND #2 ARE DIFFERENT INSTRUMENTS** and neither invalidates the other's numbers: #1 is alchemical
> ternary FEP, #2 is endpoint-MD E1. They fail differently too — one gets a known answer BACKWARDS, the
> other cannot see a known difference at all.

*The spend figure's as-of is its artifact's, **11:43 AM ET**, and it has not moved because nothing has billed
since: the last lane came off its host at 5:11 PM ET.*

*That spend figure is **DERIVED, never typed** — it is a reading of
[`realised-spend.json`](research/modalities/realised-spend.json), which sums each lane's own rental ledger
(`python3 research/modalities/realised_spend.py`). Two things it deliberately keeps apart. **(a)** A further
**+$48.89 attested** is real money **no machine ledger counts**, because the ternary Vast lane has never had
one — so the ledgered figure is a **FLOOR**, the best estimate is **$133.38**, and the artifact carries the
remediation that deletes the gap. ⚠ **The attested block grew on 2026-07-31 by TWO LEAKS of the same class,
not by new work.** Both are one lane going unwatched, and both are ranges. **(i)** Five `cal-*` bench
rentals were orphaned by the 2026-07-27 re-anchor sweep and ran unnoticed until they were
found and destroyed four days later — one of them `running` at `gpu_util 0.0` for ~3.85 days. Its size is
**a range, $20–$39, and must never be quoted as a point estimate**: no ledger covers those rentals, the
figure assumes continuous running which was never observed, and the hosts are destroyed so it is not
recoverable. The mechanism, which is the durable part: the sweep's ledger stopped at instance 46013005 while
the sweep went on renting, and `vast_idle_guard` is LABEL-SCOPED — a lane that stops being dispatched stops
being guarded, and nothing said so. One home for all of it:
[`realised_spend.ATTESTED`](research/modalities/realised_spend.py) → `vast_bench_sweep_orphans`.
**(ii)** The NR-V04 retrospective's one genuine Arm E host (instance `45749905`) was rented **6:59 PM ET Fri
Jul 24** and not destroyed until **6:59 AM ET Fri Jul 31** — **156.0 h of rental against a leg that computed
for 1.04 h**, because nothing dispatched that lane's collect for five days. Its size is likewise **a range,
$6.68–$25.83**: the span and the rate are both measured from the instance's own record at reap, but the host
was last seen `exited` after a container start failure, so whether the meter ran for the idle ~4.8 days is
not recoverable now the host is gone. One home:
[`realised_spend.ATTESTED`](research/modalities/realised_spend.py) → `nrv04_retro_orphan`; the field that
hid it (`uptime_s` is **billed rental time, never leg time**) is pinned by
[`tests/test_price_ledger_uptime_semantics.py`](research/modalities/tests/test_price_ledger_uptime_semantics.py).
⚠ **The jump from $24.46 is a BOOKKEEPING correction, not new spending:**
the step-1 fan-out's ledger lives on the branch that lane runs from, so `main` had been summing a copy that
stopped at 86 rentals while the real one held 197. The money was spent days ago; `main` could not see it.
Superseded pair registered in [§Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) row 46. **(b) GCP trial credit is a SEPARATE LEDGER and is never summed into
either** (CLAUDE.md §6): it buys wall clock, not headroom. `lint_consistency.py` rule A now holds this line
to the artifact, so the figure cannot drift back into prose. **Superseded, retained: `$0.74 spent`** — a
hand-carried total that stood while the fan-out lane alone had realised twenty times it
([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 39).*

| # | gate | status | what it means in one line |
|---|---|---|---|
| Tier 0 | categorical-axis screen | **PASSED — and now TESTED against paralogue DYNAMICS** | NR4A3 has chemistry the paralogues lack. The narrowing stands (the axis survives on **exposure**, not absence) and LANE 13 has now shown that exposure holds across 300 matched conformers: where the construct reaches an NR4A3-unique cysteine, **no EXPOSED paralogue cysteine is reachable in any scope** |
| Tier 1 | differential surface atlas | **PASSED** | there is a surface to steer an E3 against |
| Tier 2 | basin nomination | **PASSED** — *the covalent limb is no longer under review; it CLEARS* | at least one way to build a selective degrader exists, and the corrected geometry leaves **both** routes open — the covalent one included. It was briefly recorded here as possibly closed; the authoritative corrected+matched run says otherwise, and the block below carries the numbers |
| RUNG 1 | accuracy control (valA_mini) | **PASSED** | our binary free-energy pipeline reproduces a known answer |
| RUNG 2 | cmpd19 pilot | **PASSED** | the pipeline converges on the real target system |
| RUNG 2b | 4 fs speed test | **PASSED — both stages** | every future simulation ~1.56× cheaper. The full cycle reproduces the 2 fs answer to **0.0215 kcal/mol** against a 0.7 tolerance; adopted provisionally at one seed (no replicate-SD). **System identity is now MEASURED and passes** — same alchemical system per arm, the leftover particle-count difference is bulk solvent — but the two arms are independent cross-lane builds, **not** one system with only the timestep changed ([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 45) |
| RUNG 2 · closure | **cycle closure — fwd/rev hysteresis** | **PASSED (2026-07-27)** | the calibrator's ternary leg closes on itself, comfortably inside its preregistered ceiling. First time the criterion had both its inputs; a PATH-CLOSURE check, not an accuracy one, so it does not touch the wrong-sign FAIL below. **The numbers live once**, in the §THE FIRST FORWARD/REVERSE HYSTERESIS block below — this row deliberately does not restate them |
| RUNG 2 | **calibration benchmark (valB_mini)** | **FAILED** | wrong sign, and provably **not** fixable by more replicates. **Remediation:** replacement design drafted → refuted by its own free pre-check → second replacement specified at **~$7**. ⚠ **The 4 replicate legs now running do NOT convert this to a PASS** — see the row below |
| RUNG 2 · replicates | **valB_mini r1+r2 — is the FAIL quantified?** | **GATE FAILED, AS PRE-REGISTERED — and it is now quantified.** All 4 legs landed 3:07 AM ET Jul 30; the reduction ran at n=3 | **FAIL on the SIGN, before the replicate SD is ever consulted**: per-replicate ΔΔG_coop = −0.5125 / −1.0097 / −0.2749, mean **−0.599** against a known target of **+0.944**, abs error **1.543** on a 1.0-pass / 2.0-fail band. The decision is **NO-GO** — *"CI is entirely NEGATIVE (−1.103..−0.095) — method resolves the WRONG sign of cooperativity"* · **The durable deliverable is the replicate SD: 0.375 kcal/mol**, against per-leg MBAR SEs of 0.097–0.132 — roughly 3×, which is direct evidence for the paper's standing rule that a within-run MBAR SE speaks to precision and never to reproducibility · ⚠ **One open item for trimcrae, not decided here:** the reduction flags system identity INCONSISTENT because the ternary arm disagrees with ITSELF across seeds (r1 144,447 vs r2 141,740 particles, and binary 90,324 vs 90,720). That survives the 2026-07-30 fix that stopped the check comparing the ternary arm against the binary arm — a comparison meaningless by construction. Whether independently-solvated replicates may differ in water count, and what that does to a replicate SD, is a scientific call |
| RUNG 3 | **NR-V04 covalent feasibility** | **FAILED** | inputs never placed the warhead near its target site. **Remediation:** covalent legs **retired**, panel re-scoped to non-covalent. **~$6–8 not spent** |
| RUNG 4 | **NR-V04 retrospective** | **RAN, AND ANSWERED: Arm E / R1 completed 16/16 and the frozen gate emitted `DISCORDANT`** | The one home for the result is [`nrv04-retro-verdict.json`](research/modalities/nrv04-retro-verdict.json); its three preregistered secondaries are [`nrv04-retro-secondaries.json`](research/modalities/nrv04-retro-secondaries.json), and both are written up in the paper §2.12 / SI §S12. **What the rung buys is now known and it is a negative:** the retrospective **was** the positive control for paralogue-selectivity detection and it did not resolve, so no selectivity claim in the paper may lean on it. ⚠ **SUPERSEDED, retained — this row previously read "FAILED (blocked) … HELD pending re-check … no verdict stands".** That was true of the 2026-07-31 state and is not true now: the two bugs were fixed and one arm retired *before* the panel ran, and the hold-breach it describes (17 inadmissible smoke legs, $0.75, Appendix A row 57) was withdrawn in full and is a different event from the 16 real legs that later landed. **~$23 of the rung still not spent** |
| RUNG 4 · Step 1 fan-out | **19 congeneric RBFE edges** (LANE 17/21) | **COMPLETE — the lane closed itself at 9:24 PM ET Jul 29 (`pending=0`, `live=0`, every unit carrying a `ddg.json` or on the blocked list). The MAP is delivered; the GATE on what it means is a separate judgement and is NOT claimed here** | **18 edges complete of the 18 computable**, in a 19-edge map, for **$73.79** against a derived authorisation ceiling of $74.91 · **1 edge permanently BLOCKED** (`cw_bio_nmethyl_amide` — no mapper reaches the 20-atom provable floor, measured identical at t20 and t300, so more search time cannot fix it; and the one map that does reach 19 gets there only by mapping a carbon onto a hydrogen, which is the degenerate correspondence the floor exists to reject) · **the edge that was held on a FIXED DEFECT has since LANDED** (`cw_bio_primary_amide`, +0.935 ± 0.500 kcal/mol — two atoms of the staged hybrid system sat at exactly the same coordinates carrying a gradient 7.7e11 times the largest force on any other atom in the box; finite, so the CPU minimiser survived it and every GPU did not. Displacing one by 0.01 A removed it and changed nothing else to six significant figures. It burned 25 rentals on 7 cards before anyone counted the attempts; the de-degenerated geometry reached the execution hosts and the edge computed) · **15 of the 18 are anchor-rooted** and are the only ones readable as tighter-or-weaker than cmpd19; the other 3 join two analogues and close cycles. **The honest denominator is 18 computable edges of a 19-edge map**, derived in `step1-fanout-map.json` (`n_computable`), never typed — and the ranked table is built from that file's `ranking` field, which is restricted to anchor-rooted edges for the reason recorded in the paper's Appendix A · ⚠ **AND ONE OF THE THREE CYCLES DOES NOT CLOSE — a MAP-QUALITY caveat that was landed with the map and had reached no document until 2026-07-30.** `cycle_exitvector_aniline` **R = −0.726** and `cycle_exitvector_ether` **R = −0.756** are inside the ±1.0 tolerance; **`cycle_3carbonyl` sums to R = +1.307 → VIOLATION**. The artifact's own rule is that an open cycle means at least one of its edges is unconverged or mis-mapped, so **the three edges of that loop** (`cw_ms_free_acid` +0.136, `cw_bio_primary_amide` +0.935, `cw_ms_free_acid → cw_bio_primary_amide` +2.106) **carry that reservation wherever they are quoted**. R is a property of the loop and does NOT name the guilty edge; at one replicate per edge it also cannot be separated from three unlucky single draws, which is the same want-of-replicates limit as everywhere else on this lane. Numbers live once, in `step1-fanout-map.json` → `cycle_closure` |

| deliverable | status |
|---|---|
| **The virtual linker library**, chemistry-verified end to end — **54 constructs (36 exemplar + 18 representative), RDKit-verified 54/54**, counts derived from `nr4a3-linker-design.json` → `library_summary` | **DONE** ($0). ⚠ **Superseded, retained: "21 candidate molecules"** — that was the pre-wedge-fix enumeration and it contradicted this file's own library line ([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 48) |
| **The matched molecule pair for the decisive causal test** | **DONE** ($0) — that test could not be run at all before 2026-07-26 |
| **The ranked congeneric ΔΔG map** — 18 computable RBFE edges, the paper's §2.9 | **DONE** (2026-07-29, `$73.79` — inside the derived `$74.91` cap). ⚠ **One of its three cycles does NOT close** — the fan-out row above is the one home for that caveat |
| **The generation-matched null** — the winner's-curse / generative-confound control on the de-novo funnel | **PARTIAL, and the partiality is the point ($0).** The **scrambled-objective** arm has run and manufactured **0 survivors of 191** against the real campaign's 1 of 191. ⚠ **That does NOT exclude the confound and must not be quoted as if it did:** zero events in 191 generations bounds the manufactured rate at **≤0.0157 (95 %, rule of three)**, **3× the real campaign's own 0.0052**, and Fisher for 1/191 vs 0/191 gives **p = 0.5**. The artifact's earlier `p = 0.0 / enrichment = ∞` came from reading a zero point estimate as a measured zero and is retired in place in its `_superseded` block ([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 52). **The arm that actually addresses the GENERATIVE step — a fresh generation into a paralogue pocket — is UNRUN**, and it is the cheap next thing this control needs |

**Nothing on this board is waiting on trimcrae.** The question that used to sit here — whether the covalent
design route still has candidates — was answered by the corrected+matched Tier 2 run: it **clears**, and the
Tier 2 row above is the one home for that status. (Retained as a heading only because it was quotable; see
Appendix A.)

---

### ✅ PASSED — the covalent design route clears the gate. **3 basins, not 0, and not "missed by one atom".**

⚠ **This block previously read "it missed the gate by ONE ATOM" and that was WRONG — my error, corrected
2026-07-26.** I read a **superseded artifact** and reported its numbers as the corrected result.

| run | samples | runtime | term (a) | term (b) | nominal |
|---|---|---|---|---|---|
| published, pre-correction | 10⁶ | 4294.9 s | **7** | 40 | 28 |
| *what I quoted* — corrected but **under-sampled** | **250 000** | **1082 s** | **0** | **31** | 27 |
| **corrected + MATCHED — authoritative** | 10⁶ | 4303.6 s | **3** | **40** | **28** |

**The signal I missed was sitting in my own table: term (b) had moved, 40 → 31.** Term (b) is computed from
the lysine transfer zone and is **untouched by the reach rule** — it had no business changing at all, and its
movement was proof the run was not comparable rather than merely corrected. I checked provenance on *scope*
(12 poses, 192 basins — which matched) and never on **sample count**, where the 4× runtime gap was visible.
The matched run reproduces published term (b) **and** the nominal limb **exactly**, so only term (a) moved and
the comparison is genuinely rule-attributable. Confirmed-basin patches match at Jaccard **1.000**.

**So the corrected result is 7 → 3, and the gate PASSES.** Three basins clear the preregistered **12-atom**
gate: **`vhl|M2` at 10 atoms** (reach fraction 0.057), **`vhl|M3` at 11** (0.021), **`crbn|M17` at 12** (0.045,
term-b 3.87×). Shortest reach per residue is **C397 10 · C420 16 · C559 27** — *not* the 13/16/31 I reported.
And nothing is rescued by a newly-invented surface: **`crbn|M17` matches `crbn|M0`** — the strongest
nomination — at Jaccard exactly **0.600**, i.e. the gate-passing CRBN placement sits on the strongest basin's
own surface. (`crbn|M0` itself reads 13 and does miss by one.)

**The gate was never moved, and did not need to be.** The design consequence from the collision profile still
stands and is the durable part: **0 collisions at 12 atoms, 0.081 at 16, 0.258 at 20**, so every extra linker
atom is a *selectivity* cost, not just a synthesis cost. **The honest cut-off is 14 backbone atoms** — the
longest length at which reach-only collision is a measured zero. It is **not** made a gate, for two stated
reasons: no *enumerated molecule* reaches 12 (the shortest is 14), and reach-**and**-exposure is 0.000
everywhere, so the axis rests on **burial**, not on distance.

### Library and matched pair — one real defect found and fixed

**The library survives the reach correction with ZERO casualties**, and **no construct ever
"worked" because of the pendant-credit bug** — re-enumeration returns every construct field-for-field
identical. *(It was a 21-construct library at that point; the count is now 54 and the superseded value is
[Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 48.)* The
reason is structural: 5b's enumerator always used the exact three-ball kernel, which pre-dates the correction;
the bug lived in `basin_geom.linker_can_visit`, consumed only by the basin search.

**But the recommended pair's molecules were built for the WRONG RESIDUE.** The preregistered wedge rule
(*NR4A3 must present a donor, both paralogues must not*) was enforced in `matched_pair()` but **not** in
`enumerate_library()`. The record read `wedge_target_residue: T407` while its own d/d₀ carried
`branch_target: C397` — **Asn in NR4A1, Ser in NR4A2, so BOTH paralogues keep an H-bond partner**: exactly the
"S ≈ 0 by construction" trap the rule exists to prevent. The two selections disagreed on **8 of 10** records.
Fixed with one shared `select_wedge_site()` plus a refusal when emitted molecules don't match the reported
site. Cost: 12 constructs. **Library is now 36 exemplar + 18 representative, RDKit-verified 54/54.**

**The pair stands; the shared-LENGTH reading does not.** `crbn|M0` exemplar, 3-(3-pyridyl)-L-Ala vs L-Phe at
**Thr407**, **19 backbone atoms**, **9.04 Å** E3 clearance, 64 heavy atoms, one aromatic C–H→N — every
preserved property re-measured rather than asserted. But on that placement the covalent series sits at 14 and
the wedge pair at 19, and **no single construct carries both.**
**★ THE REASON WAS MEASURED 2026-07-30 AND IT IS NOT THE ONE THIS BLOCK CARRIED.** ⚠ *Superseded, retained:
"a single chain carrying both needs 16, and the segment grid cannot build it (branch floor k=6 against T407's
k∈[2,3] at n=16) — a grid limit, not geometry"
([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 55).* Run against the committed
enumeration, **every clause of that except the branch floor is false**: the grid builds T407 branches at
n=16 **and** C397 branches at n=16, at three shared lengths (16, 18, 20); and **no recorded T407 window is
k∈[2,3]** — the real ones are k∈[2,6] and k∈[4,13], and the enumerator builds inside them. **The blocker is
that `build_smiles` takes ONE `pendant`** — its template has a single branch residue, so no choice of
segments, length or placement can emit a two-mechanism molecule, because there is no second slot. The floor
`k = 3 + SEG2 + tail` is real but **architectural** (the 3 is the branch residue's own N–Cα–C) and no grid
change reaches below it. **What would work is a two-branch template, constructible at n = 18 with the
segments the grid ALREADY has** — so the fix was never a re-grid. Derived, never typed:
[`linker_branch_reach.py`](research/modalities/linker_branch_reach.py) →
[`linker-branch-reach.json`](research/modalities/linker-branch-reach.json).

---

### 🌙 OVERNIGHT MONITORING — what is covered by what (2026-07-26, trimcrae asked for hourly)

**Three layers, and they cover different things. Stated explicitly because assumed-but-absent coverage is
exactly how `ternary-leg-watchdog.yml` sat UNPARSEABLE for days while everyone believed it was watching.**

| layer | covers | acts autonomously? | verified |
|---|---|---|---|
| `ternary-vast-watchdog.yml` (cron) | the **4 valB_mini replicate legs** (`edge_reps`), which are what is enabled now. ⚠ **NOT the 2 RUNG 5a-KS legs any more** — those are PARKED (`enabled: false` + `_parked_why`) because a relaunch is a new purchase the price gate refuses; and **not** the 4 RUNG 2b legs, which landed | **YES** — relaunches a DIED leg from its last checkpoint; a STALL alerts but does **not** relaunch, because a relaunch would hang the same way and pay for it again | **Exercised repeatedly through 2026-07-27**, including the correction that a leg whose GPU has been reclaimed reads `stopped_and_billing` rather than "advancing". ⚠ **The delivered cron interval is MEASURED, not assumed, and it is not the interval the cron asks for** — [`fleet-supervision-alarm.yml`](.github/workflows/fleet-supervision-alarm.yml) is its one home; do not quote a remembered gap here (CLAUDE.md §6) |
| hourly routine → this session | **everything**, incl. the 2 paralogue MD legs, the valB reverse leg, and Lane reports | no — it wakes an agent to judge | fires hourly, persists server-side, survives container restarts |
| `vast-watchdog.yml` (cron) | **any Vast job kind the engine implements** — currently the **2 paralogue MD legs** (`paralogue_md`) and, by construction, `ternary` | **YES** — relaunches a DIED leg from its checkpoint, capped per UTC day, and **withholds** the relaunch while the lane's own workflow is in flight; STALL/FAILED alert but never relaunch | **Exercised live 2026-07-25 10:00–10:05 PM ET** against both legs: verdicts RUNNING, state written and read back (`prev=1014350`, `stall=1` on a frozen tick, `stall=0` on an advance). Merged to `main` 2026-07-26 |
| `vast_idle_guard.py`, acting **from CI** | **all** Vast spend | **YES** — destroys a box that is up and producing no evidence of work (log silent, or restart churn) in ~15 min. Its one inviolable rule: **GPU idleness NEVER condemns a box**, only a measured absence of *writes*, so a legitimately CPU-bound staging phase is safe | ⚠ **This row previously credited the `autoteardown` wrapper with "guaranteeing no idle-GPU billing anywhere". That was FALSE and is retired** (measured 2026-07-27, pinned by `tests/test_vast_idle_guard.py`): an unprivileged container **cannot end itself** — `kill -9 1` returns success while being ignored — so the EXIT trap stops the JOB, not the METER, and a crash-looping container never returns at all. Two 5a-KS legs billed ~53 min at `gpu_util: 0.0`. The guarantee is the CONTROL PLANE's, never the host's |

⚠ **RESOLVED 2026-07-26 — the 2 paralogue MD legs ARE now covered by a cron watchdog**, and the gap had a
**proven cause, not a suspected one.** `vast_watchdog.py` is a **kind registry** over the single shared policy
in `watchdog_policy.py`, which `ternary_vast_watchdog.py` **re-exports** — a test asserts
`tvwd.classify is wp.classify is vw.classify`, so the two monitors cannot drift into disagreeing about whether
a leg is dead. A kind the engine does not implement is **refused at validation time, loudly, aborting the
pass** — never silently skipped. The ternary list is untouched and takes the identical legacy code path.

**Root cause of the outage, from the log rather than inferred:** LANE 13's own long-running watch **died at
8:28 PM ET** on `['nr4a-pdyn-nr4a2-smoke'] made no progress for 8 ticks` — a leg that was **never launched**,
whose signature `(None, None, False)` can never change — **while both real legs were advancing at 60–69 % GPU
utilisation.** `leg_names()` synthesises a `-smoke` name per target regardless of whether one exists;
`real_done` excluded smoke legs and **the stall test did not**. That asymmetry was the whole bug: **a phantom
entry took the monitoring down and left two billed legs uncovered for ~1.5 h.** Fixed
(`watched_for_stalls()`), and the new engine **refuses to watch a smoke leg at all** rather than inherit the
failure mode.

**One trap worth keeping:** the `paralogue_md` progress scalar is `phase_rank × 1e6 + milli-ns`, because the
job's own `done_ns` **resets to zero at the metad→release boundary** — a raw counter would read a healthy
phase transition as a 60 ns regression and stall-alert a good leg.

**✅ `DIED → relaunch` IS NOW PROVEN LIVE, autonomously, on a real leg (2026-07-26 1:42 AM ET).** The
`schedule` pass at that time — not a dispatch, and with no session driving it — found `nr4a-pdyn-nr4a1` with
**no result and no instance**, classified it `DIED`, rented **45878836** on machine 17720 (attempt 1/6 for the
UTC day) and the leg **resumed from its own checkpoint at 33.55 ns** rather than restarting. That is the
watchdog's real success terminus for the recovery path, witnessed end to end, and it happened while the lane's
own watch had been dead for ~5 h — which is precisely the failure this engine was built for.

**Still not proven live:** `FAILED` and the `STALL` escalation. Proving them needs a leg that crashes with a
recorded reason or freezes while alive, and a billed one was not killed to get it; they rest on unit tests plus
the fact that they share `classify()` with the path above.

---

## ✅ LANE 13 — DOES THE CATEGORICAL CASE SURVIVE PARALOGUE DYNAMICS? **YES.** (2026-07-26 2:49 PM ET)

*★ **APPENDIX — a landed gate.** Evidence under Tier 0; the one home for the exposure-not-absence narrowing across ensembles. Roadmap: instrument `V17`, requirement `R8`.*

The assumption Tier 2 passed on was never that NR4A3's cysteines are unique — that is a sequence fact and was
never in doubt. It was that a paralogue does not present some OTHER nucleophile that the SAME linker path
reaches. A degrader does not care which cysteine it labels. That had only ever been checked on one static
conformer per paralogue; this lane checked it on **300 matched conformers** (NR4A3 / NR4A1 / NR4A2, 100 each:
25 metadynamics + 3 × 25 unbiased release) against **73 867 matched E3 placements**.

**P(no paralogue cysteine reachable | the construct reaches an NR4A3-unique cysteine)**, at the preregistered
**12-atom** gate:

| scope | all cysteines | **solvent-exposed only** (RSA > 0.25) |
|---|---|---|
| static opened model | 1.000 | **1.000** |
| **unbiased release ensemble** | 0.99876 | **1.000** |
| metadynamics (biased) | 0.9971 | **1.000** |

**On exposed cysteines the answer is exactly 1.000 in every scope** — `mean_P_any_EXPOSED_cysteine` is **0.0**
for NR4A1 and **0.0** for NR4A2 throughout. The small non-zero co-labelling on the all-cysteine measure
(0.12–0.29 %) is entirely on **buried** paralogue cysteines, which is reachability without labelability.
NR4A2 is essentially absent on every measure (1 × 10⁻⁶ to 7 × 10⁻⁶).

⚠ **STATE IT AS THE RARE-EVENT STATISTIC IT IS.** The conditioning event is thin by construction: a matched
placement reaches an NR4A3-unique cysteine in **~0.04 %** of placements, i.e. **122 hit placements out of
73 867** in the unbiased ensemble. That is what the 2 000 000-sample setting was bought for — 500 k gave
single-digit events — but 122 is a small denominator and the ratio should not be quoted to five figures as
though it were tight. **The defensible claim is the EXPOSED column: zero paralogue co-labelling events, not a
probability estimated near one.**

**Limits, from the artifact's own `_limits`:** reachability and exposure are necessary, not sufficient — no
thiol pKa, nucleophilicity, adduct stability or promiscuity is modelled; each species' conformers are
correlated within a replica, so the effective n is smaller than the frame count; and paralogue conformers are
superposed into the NR4A3 reference frame, carrying a per-frame core-fit residual.

---

## ✅ RUNG 5a-KS LANDED — the causal kill-switch returns its **preregistered null**, S = −0.13 ± 0.33 kcal/mol (2026-08-02 2:15 AM ET)

*★ **APPENDIX — a landed gate.** The one home for `S` and its bound. Roadmap: instrument `V16`, requirement `R11` — and ⛔ `V16` has no known-answer calibrator, which is roadmap §10 row 11.*

**Headline in the required form: a DELIVERABLE done — the paper's own stated limit *"the causal test has not
been run"* is retired — and the gate returns the outcome it registered as LIKELY, which is explicitly NOT a
stop.**

All four legs landed (n = 2 seeds per arm). Every figure's one home is
[`nr4a3-5aks-reduction.json`](research/modalities/nr4a3-5aks-reduction.json):

| | |
|---|---|
| **S** = ΔG_tern(NR4A3) − ΔG_tern(NR4A1) | **−0.1297 ± 0.3264 kcal/mol** (replicate SD, n = 2/arm) |
| NR4A3 arm | mean −10.9439, replicate SD 0.2354, mean MBAR SE 0.0753 |
| NR4A1 arm | mean −10.8142, replicate SD 0.2261, mean MBAR SE 0.0860 |
| reading (fixed in advance) | **S ≈ 0 → the marginal wedge is absent.** Registered as the LIKELY outcome and NOT a stop |
| what it bounds | the design could only resolve **\|S\| ≳ 0.65 kcal/mol** (2σ); it did not |

⚠ **THE ERROR IS THE REPLICATE SD, NOT THE MBAR SE** — the latter is ~0.08/arm, threefold smaller, and
quoting it would understate the uncertainty by exactly the factor the ABFE error-bar standard exists to stop.

**Staging was VERIFIED, not assumed, because one specific defect counterfeits this exact result.** A one-chain
"ternary" leg is a binary leg nobody labelled and would also give S ≈ 0. Both arms check out identically
against their committed manifests — chains `A` (254 res, the NR4A LBD) + `B` (442 res, CRBN) + ligand chain
`L`, with `protocol_hash`, `charge_method`, `setup_cache_version` and `n_windows` agreeing across all four
legs. The trap did not occur.

**Three limits, each able to hide a real effect:** the reducer flags `n_particles` disagreeing across arms
(NR4A1 ≈ 210k vs NR4A3 ≈ 148k — the solvated BOX, not the composition, so size-dependent systematics do not
cancel, which is the one thing a double difference is supposed to buy); the geometry is a **Boltz-2
prediction**, so S is pose-conditional; and ⛔ **the instrument has a failed calibrator** — §2.11's
known-answer benchmark misses with the wrong sign, systematically. **An uncalibrated instrument returning zero
cannot distinguish "no wedge effect" from "cannot resolve the wedge effect",** and it is not reported as
though it could.

⚠ **DO NOT CONFLATE THIS WITH THE SENSITIVITY-CONTROL NULL BELOW.** They are different instruments with
separate failed controls: this is **alchemical ternary FEP** (its calibrator is valB_mini, §2.11, wrong sign);
that is **endpoint-MD E1** (its calibrator is the SMARCA2/4 panel, NULL). Neither result invalidates the
other's numbers, and reading them as one finding would overstate both.

Documented at paper **§2.10e**, with §2.10(d) and the §2.10 closing paragraph re-written from "has not been
run" to "has been run and is NULL".

---

## ❌ GATE FAILED — the SMARCA2/4 sensitivity control returns **NULL** on an adequately-powered design (2026-08-02 10:42 PM ET)

*★ **APPENDIX — a landed gate.** Roadmap: instrument `V11`, requirement `R11`. ⚠ **This heading's slug is load-bearing** — it is the target of the repo's only non-Appendix-A anchor link (`nr4a-repanel-prereg-DRAFT.md:9`) and must not change.*

⚠ **CORRECTION, 2026-08-02 — THE TIMESTAMP IN THE HEADING ABOVE IS WRONG BY A CALENDAR DAY, AND THE HEADING IS DELIBERATELY NOT EDITED.** The verdict's own record is `selcal-verdict.json` `utc: "2026-08-01T02:43:16Z"`, i.e. **2026-08-01 10:43 PM ET**. Root cause, read from the data rather than guessed: **the clock face was converted and the calendar date was not** — `02:43 Z → 10:43 PM` is the correct 12-hour conversion, but the date must roll back from 08-02 to 08-01 and did not (the minute is also off by one). The heading keeps the incorrect stamp because changing it changes the slug the anchor link above depends on. **Superseded, retained: `2026-08-02 10:42 PM ET` as this gate's time.**

**The headline, in the required form: a gate FAILED, and the remediation is that there is none to buy — step 3
is not purchased and the paper's language changes instead.**

This was the **method calibrator** that Open decision 9 named as the program's real gap and that RUNG 3 module 3
adopted on 2026-07-24: the one experiment meant to show that this workflow can discriminate paralogues where
the answer is already known. It has now been run end-to-end and **it did not detect the difference.**

Every figure below has **one home**, [`selcal-verdict.json`](research/modalities/selcal-verdict.json), and is
read from it rather than typed:

| | |
|---|---|
| tier | **NULL** — a real negative, reported as one |
| statistic (mean SMARCA2 − mean SMARCA4, model-level E1 plateau) | **+0.4373 Å** (4.9684 vs 4.5311) |
| direction | ⚠ **opposite** to the primary source's prediction, and **all 11 LOMO refits keep that sign** |
| exact one-sided *p*, predicted direction | **0.7468** |
| mirrored *p* | **0.2554** — so NOT WRONG_SIGN either |
| reference set / floor | **462** arrangements, min attainable *p* **0.00216**, α = 0.05 |
| technical failures | **0** in each arm |
| admitted legs / models | **22** legs, **6 vs 5** models |

⚠ **THE DESIGN WAS ADEQUATELY POWERED BY ITS OWN FROZEN CLAUSES — this is not an underpowered miss.** The
reference-set floor is an order of magnitude under α, there were no technical failures, and the panel cleared
the per-arm model floor. The test could have returned significance and did not. That is a **worse** outcome for
the program than RUNG 4's DISCORDANT, which was a non-resolution rather than a negative.

**Two of the 24 designed legs were excluded before scoring, on a MEASURED INPUT FAULT and never on an outcome**
— SMARCA4 seed 3 places two heavy atoms **0.693 Å** apart against a 1.00 Å floor, so the pre-MD audit refused it
reproducibly on five machines before any dynamics existed. The other unfinished unit at that moment audited
**clean at 1.2994 Å** and was **re-run, not excluded**. Full standard and evidence:
[prereg AMENDMENT 1](research/modalities/selectivity-sensitivity-control-prereg.md#amendment-1--2026-08-02-measured-input-fault-smarca4-model-3).

### What this BINDS, in the words fixed before the run

The consequence is not being invented now — it was written into
[`selectivity-resolution-options.md`](research/modalities/selectivity-resolution-options.md) §4 precisely so it
could not be re-narrated after the fact, and it is machine-carried by `selcal_gate.NEXT_STEP_BY_TIER`:

1. **⛔ STEP 3 (the NR4A1/2/3 re-panel) IS NOT BOUGHT.** It would be money spent to reproduce a failure. The
   draft preregistration [`nr4a-repanel-prereg-DRAFT.md`](research/modalities/nr4a-repanel-prereg-DRAFT.md) is
   **retired unrun**, and its own power section already said the design was powered ≤ 0.16 against the
   separations this program has measured — so the tier and the power analysis point the same way.
2. **Every NR4A3 selectivity statement in the paper is an UNVALIDATED PREDICTION**, in the language of §4.
   ⚠ **Carried in THREE places and verified to be, not asserted:** the **Abstract**, **§2.12a** and **§4
   Limitations** — so a reader who never reaches the limitations still meets it. *(This line first said
   "applied in the sentences themselves"; a `grep` showed the phrase existed exactly ONCE in the paper, in
   §2.12a, so the claim was aspirational when written. It is now checked rather than believed.)*
3. **⛔ IT DOES NOT DISTINGUISH "the readout is blunt" from "this pair is hard"** and must never be reported as
   though it did. SMARCA2/SMARCA4 bromodomains are ~80 % identical and the published selectivity turns on a
   single Gln1469 hydrogen bond, so a null is consistent with both an insensitive endpoint and a genuinely
   narrow structural signal.
   ⚠ **AND A THIRD READING, MEASURED 2026-08-02, WHICH BOTH REGISTERED READINGS ASSUMED AWAY.** They share a
   premise nobody had checked — that the simulated complexes were the complexes whose selectivity was
   measured. Scored against the deposited ternaries the panel was *designed around*, all 12 co-folds
   reproduce the internal VHL/EloB/EloC machinery at **DockQ 0.89–0.97** and the degradation-target↔VHL
   interface at **DockQ 0.023–0.046, fnat 0.000** — not one native interface contact recovered, on either
   arm, by either of two independent implementations
   ([`selcal-cofold-vs-crystal.json`](./research/modalities/selcal-cofold-vs-crystal.json),
   [`selcal-cofold-dockq.json`](./research/modalities/selcal-cofold-dockq.json)).
   ⛔ **This makes the null WEAKER evidence about the instrument, not a route to re-opening it.** The endpoint
   was never exercised on the complexes in question, so the null bounds the *workflow as run* rather than the
   readout alone, and the failing stage is ternary **generation** rather than ranking. Every paralogue-
   selectivity statement remains an unvalidated prediction; nothing here licenses revisiting one.
   ★ **BOTH HALVES OF THE CONTROL A NEAR-ZERO SCORE REQUIRES ARE NOW MEASURED, so 0.023–0.046 is a
   measurement rather than a property of the scorer** — each objection answered by running it, not by
   argument. **(a) Does anything score HIGH through this harness?** DeepTernary, a dedicated SE(3)-equivariant
   ternary generator, on `6HAX_B_A_FWZ` — a VHL/SMARCA2 PROTAC ternary supplied as complete unbound inputs in
   its own released benchmark — reaches **DockQ 0.618 (CAPRI "Medium"), median 0.438 over 16 scored poses,
   best iRMSD 1.21 Å**, from the same DockQ 2.1.3 build
   ([`selcal-deepternary-poscontrol.json`](./research/modalities/selcal-deepternary-poscontrol.json)).
   ⛔ 2018 deposit, inside the model's 2023-10-14 horizon, therefore memorisation-permitting **by
   construction**: a positive control on the **harness and instruments**, never on generalisation, and it
   says nothing about NR4A3, degradation or selectivity. **(b) How wrong is 0.03?** Holding VHL fixed and
   displacing the **true** target chain of 9DTY by a known rigid RMSD — everything else perfect, placement
   the only variable — gives **1.000 → 0.948 (0.5 Å) → 0.845 (1 Å) → 0.717 (2 Å) → 0.401 (4 Å) → 0.240
   (8 Å) → 0.085 (16 Å) → 0.026 (32 Å)**
   ([`selcal-dockq-decoy-scale.json`](./research/modalities/selcal-dockq-decoy-scale.json)). The co-folds sit
   at the **~32 Å** rung — consistent with their independently measured 17.8–21.2 Å interface-RMSD — so they
   are **not a near-miss on placement**, and the generation failure is not a matter of degree.
   ★ **(c) AND THE COMPLEX IS RECOVERABLE IN SILICO — measured on 9DTY ITSELF, which is post-horizon.**
   9DTY and 9DTX are absent from DeepTernary's disclosed 4,471-entry exclusion set and deposited well after
   its 2023-10-14 horizon
   ([`deepternary-leakage-check.json`](./research/modalities/deepternary-leakage-check.json)). Given the two
   binding sites, the generator reaches **DockQ 0.839 (CAPRI "High"), iRMSD 0.67 Å, fnat 0.83**, best of 16
   seeds, median 0.442, against our co-folds' best 0.038 on the same interface and reference
   ([`selcal-deepternary-headtohead.json`](./research/modalities/selcal-deepternary-headtohead.json)).
   ⛔ **NOT the same question, and the two numbers are not interchangeable:** the published *unbound*
   protocol superposes both binaries into the native ternary frame and supplies the native degrader pose, so
   the model is told **which pocket each end of the degrader occupies** and predicts the two proteins'
   **relative placement**, which is randomised out of its input. Our co-folds were given sequence and ligand
   and nothing else. ⚠ Best-of-16, and **one arm**: the SMARCA4 arm was refused before any prediction
   (warhead fragment overlap 0.42 against a 0.55 bar) and no SMARCA4 number exists.
   **What it settles:** this ternary is not beyond in-silico reach, so 0.023–0.046 is a property of the
   sequence-only co-folding route used here and not of the problem.
   ★ **(d) AND THE FAILURE IS LOCALISED — THE HALVES ARE RIGHT, THE ASSEMBLY IS NOT.** Superposing each
   co-fold on one protein at a time and measuring the degrader over the native atoms contacting *that*
   protein (correspondence through the reference molecule's atom graph, never by proximity): all 12 sit
   within **3.2 Å** of the crystal in each protein's own frame — target median **1.83 Å**, E3 median
   **1.96 Å** — against an assembled interface scoring what the true complex scores when displaced **32 Å**.
   A factor of **10** ([`selcal-cofold-decompose.json`](./research/modalities/selcal-cofold-decompose.json)).
   ⇒ **The missing information is the relative placement of the two proteins**, which is exactly what a
   ternary generator is given when handed each end's site. That is the nameable precondition for credible
   NR4A3 ternaries, and it is why (c) matters beyond one number. ⚠ The locus is decided against that measured
   scale, never a bar chosen for the occasion; unreadable scale ⇒ locus reported UNDETERMINED.
   ★★ **(e) A PARALOGUE-SELECTIVITY READOUT THAT PASSES A KNOWN-ANSWER TEST — THE FIRST THIS PROGRAM HAS.**
   The published mechanism for this pair is a hydrogen bond, not a dynamical quantity (Kofink et al.,
   PMC9551036: *"the selectivity-inducing hydrogen bonding between Gln1469 of SMARCA2BD and VCB"*), and a
   bond between two named partners is visible in a deposited structure. Scoring the target↔VCB contact map of
   9DTY and 9DTX and aligning the bromodomains **by sequence** (identity 0.890 over the interface alignment —
   the two deposits number locally vs full-length, so equal numbers are different residues), the descriptor
   finds exactly one position where a glutamine on the SMARCA2 arm makes a **side-chain** polar contact the
   aligned SMARCA4 residue does not: **Gln98 Oε1 → VHL Arg12 Nη2, 2.88 Å**, 34 interface contacts, against
   **Leu1545** (10 contacts), which cannot make that bond
   ([`selcal-interface-signature.json`](./research/modalities/selcal-interface-signature.json)).
   ⚠ **Side-chain, not any polar contact** — SMARCA4's leucine touches the E3 through its *backbone* amide at
   2.93 Å, and counting that hid the substitution behind an interaction of a different kind (the first version
   of the check did exactly that and reported a real recovery as a failure). ⚠ No hydrogens at these
   resolutions ⇒ "polar contact" is the heavy-atom donor–acceptor proxy, labelled as one.
   ⛔ **It validates ONE contact in ONE pair.** It does **not** validate E1, and it makes no NR4A3 prediction
   correct — applying it to an NR4A3 ternary additionally requires that ternary to be credible, which (d)
   shows this route does not yet supply.
   ★★ **(f) THE VALIDATED DETECTOR, TURNED ON THIS PROGRAM'S OWN NR4A TERNARIES — AND THE ANSWER IS NOT
   YET.** With (e) passed, the same descriptor was applied to the `denovo_401` NR4A1/2/3–CRBN ternaries
   ([`nr4a-ternary-signature.json`](./research/modalities/nr4a-ternary-signature.json)). It returns **six**
   positions where the NR4A3 model contacts the E3 and both comparators do not — and **five are placement
   artifacts**: GLU104, ARG174, LYS195, ARG219, LEU234 carry the **identical residue in all three
   paralogues**, so they cannot encode a paralogue difference; a contact present in one model and not another
   is three independently-folded structures disagreeing, on the route (d) measures as wrong by a factor of 10.
   **One position is sequence-encoded: GLU208** (Glu → Pro in NR4A1, Tyr in NR4A2).
   ⛔ **And its reproducibility is NOT TESTED**: only `model_0` exists per paralogue, against a bar of 3.
   One model cannot distinguish a determinant from that model's accident — the first readout printed
   *"reproducible across ALL 1 models"*, which is n = 1 wearing the costume of a replication test, and the
   module now refuses that wording outright.
   **⇒ A justified NR4A3-selective-ternary case does not exist today, and exactly two things stand between
   here and one:** (i) **replicate models per paralogue** — a GPU spend, not a re-read, and the cheaper of
   the two; (ii) **the NR4A3 warhead pose**, which is a wet-lab fact: no deposited NR4A3 LBD–ligand complex
   exists, the binder is de novo, and the pocket itself is cryptic (opened by metadynamics), so no in-silico
   route supplies it. GLU208 is a **lead with a validated detector behind it**, not a result.
   ★★ **(g) WHAT IS ACTUALLY MISSING, AFTER (a)–(f) — AND IT IS NARROWER THAN "WE CANNOT DO THIS".**
   Three things had to be true for a justified NR4A3-selective-ternary case, and two of them now are.
   **Is the raw material there?** YES, and it was already measured: the differential-surface atlas finds
   **33 exposed, divergent-vs-both, character-changing handles** on the NR4A3 LBD (of 254 aligned residues;
   137 exposed, 109 divergent) and its gate reads **GO**
   ([`nr4a3-differential-surface-atlas.json`](./research/modalities/nr4a3-differential-surface-atlas.json)).
   ★ And (e) calibrates how much is enough: the SMARCA2/SMARCA4 selectivity that PRT3789 exploits rests on
   **one** such position (Gln98 → Leu). NR4A3 has 33 candidates where one sufficed.
   **Is there a detector?** YES — (e), validated against a published known answer.
   **Is there a correctly-assembled ternary to point it at?** ⛔ **NO, and this is the whole remaining gap.**
   The existing NR4A ternaries are sequence-only co-folds from the route (d) measures as failing at assembly
   by a factor of 10, and the molecule that produced them is **unrecoverable** — no `_chem_comp_bond` loop in
   any of the three models, and it entered as `$PROTAC_SMILES`
   ([`nr4a-ternary-ligand-provenance.json`](./research/modalities/nr4a-ternary-ligand-provenance.json)), so
   §2.5's ternary result cannot be replicated or extended at any price.
   ⚠ **A CORRECTION TO A FRAMING USED EARLIER THE SAME DAY:** the assembly method was described as unusable
   on NR4A3 "for want of a binding site". That is wrong and the repo refutes it — `results/nr4a3-matrix/
   nr4a{1,2,3}-opened.pdb` are state-matched opened LBDs, **Gate 3A is supported** (the opened geometry does
   not relax once the bias is removed), and a docked `denovo_401` pose exists in that frame. The site is
   **UNVALIDATED, NOT ABSENT**, and those are different: the generator can be handed our own pose today.
   ⇒ **The next step is therefore in-silico and specified**: rebuild the three paralogue ternaries by the
   assembly route (opened LBD + docked warhead pose as site 1; CRBN + IMiD from a binary crystal as site 2;
   a degrader whose SMILES is **recorded this time**), then re-run (f). What remains genuinely experimental
   is narrower still — whether anything binds the opened pocket at all, which a thermal-shift/SPR/NMR screen
   answers far more cheaply than a co-crystal, and whose NEGATIVE would be equally decisive.
   ⛔ None of (a)–(g) is a positive control for paralogue-selectivity **detection at this program's E1
   endpoint**; that endpoint still has none, and none of them may be read as softening the tally below.
4. **It re-scores no landed leg and changes no ΔΔG.** It is a statement about the instrument.

### The standing tally this closes

**All three** attempts to establish a positive control for this program's selectivity claims have now been run,
and none succeeded: §2.11's cooperativity calibrator (`valB_mini`) failed on **sign**; RUNG 4's NR-V04
retrospective returned **DISCORDANT** (non-resolution, and covalency-confounded so it could never have been a
positive control at any *n*); and this control — the one built specifically to be free of those defects, on
solved structures on both arms — returns **NULL on an adequately-powered design**. Documented in the paper at
§2.12a.

⚠ **"There is no fourth candidate staged" was WRONG and is retired** (2026-08-02; superseded line kept in
[Appendix A](#appendix-a--superseded-numbers-and-retracted-claims)). It was a statement about the search, not
about the repo, and the search had stopped one stage too early. **Two known-answer tests are already built
and have never been run:**
- **CREBBP vs BRD4(1) / SGC-CBP30** — `selectivity-benchmark.json` + `selectivity_benchmark_prep.py` +
  `stage-selectivity-benchmark-aws.yml`, fully specified with an `abfe_plan` and **no result key**. Both arms
  are real holo crystals with the **same ligand** (4NR7 / 5BT4), so no docking and no pose assumption, and an
  experimental ΔΔG ≈ **2.2 kcal/mol** against a demonstrated ~1.5 kcal/mol band. ⛔ It is a **binary**
  selectivity control and would **not** discharge §4's paralogue/ternary statement — but this program has no
  binary selectivity control either (valA validates relative FEP *within one pocket*).
- **A pmx/GROMACS interface point-mutation ΔΔG** — the only physics lane here that has recovered a published
  known answer (barnase–barstar Y29A **+4.42 ± 1.08** vs +3.4 and Y29F **−0.37 ± 0.18** vs −0.13, both inside
  1.5 kcal/mol, ~$0.21/leg, `triskit23/pmxfep` already baked) and it works on **PPI interfaces**. This
  document's own reading of the selcal null is that SMARCA2/4 selectivity *"turns on a single Gln1469
  hydrogen bond"* — i.e. a point mutation. Conditional on a measured mutational value existing in a primary
  source, which is a $0 check that must precede any spend (Open decision 7).
  ⛔ **THE $0 CHECK RAN ON 2026-08-02 AND THE ANSWER IS NO. THIS ARM IS CLOSED ON EVIDENCE, NOT ON BUDGET.**
  One home for the verdict and every reading behind it:
  [`pmx-mutation-reference-precheck.json`](research/modalities/pmx-mutation-reference-precheck.json)
  (generator [`pmx_mutation_reference.py`](research/modalities/pmx_mutation_reference.py)) —
  **`STOP_NO_REFERENCE`**. Do not restate its counts here. The Gln1469 contact is documented
  **structurally** (a hydrogen bond in a crystal) and **functionally** (cellular degradation ratios), and
  **neither is a measured interface mutational ΔΔG** — so the run would have had no known answer to be
  scored against, which is the defect that cost this program three withdrawn selectivity claims.
  ⚠ **The nearest measured thing is named rather than hidden, because it is what a reader will ask about:**
  an interface point mutation *has* been measured in this exact system — **VHL R69A** (Farnaby 2019,
  PMC6600871) — but it sits on the **E3 arm** rather than the paralogue-discriminating residue, and its
  reported quantity is a **TR-FRET cooperativity ratio**, not a binding ΔΔG. Converting one into the other
  would fabricate the link this program does not have.

**Authorization is no longer what blocks the pmx arm — evidence is (trimcrae, 2026-08-02: *"pmx only"*).**
The superseded line, retained because it stood until that answer:
*"Neither is authorized here."* The ABFE arm above is **still not authorized**; the pmx arm **was**, and
then failed its own $0 precondition, which is a stronger and more durable reason to leave it unrun.
Neither is a positive control for paralogue *degradation* selectivity. They are recorded because "nothing
is left" was the wrong sentence, and a tally that closes a search is worth exactly as much as the search
behind it.

★ **WHAT WOULD UNBLOCK THE INSTRUMENT — and it is a different question from the one just closed.** The
precheck refuses the *SMARCA2/4 application*. The lane's own stated limitation is separate and now has a
concrete, priced answer: the qualified set **brackets** the wedge (+3.4 hot spot, ~0 near-null) and covers
nothing at the size a paralogue-scale difference has, so
[pricing.md](research/compute/pricing.md) records that the confirmatory line *"may not claim to resolve a
paralogue-scale difference"*. Scanning all 7,085 SKEMPI rows for a wedge-sized, charge-conserving,
buildable mutation of 1BRS returns **exactly one** candidate —
[`protfep-wedge-band-candidates.json`](research/modalities/protfep-wedge-band-candidates.json), 29
rejected — and it is now defined as `barnase_barstar_W35F` and CI-verified to stage. It is deliberately
**not** in `protfep_bench.QUALIFICATION_SET`, so it cannot flip the engine's committed verdict without a
measurement. ⚠ **It would settle whether THIS ENGINE resolves a ~1 kcal/mol interface effect. It is not a
selectivity control, involves no paralogue, and passing it would license no SMARCA2/4 or NR4A3 claim.**

---

## ⏱️ IN FLIGHT — what is actually running right now (as of **2026-07-30 5:30 PM ET**)

*★ **APPENDIX — a superseded board plus four one-homes.** ⛔ **DO NOT READ THE TABLE AS LIVE STATE.***

⛔ **THIS BOARD IS NOT LIVE, AND IT IS STRUCTURALLY BLIND TO PART OF THE FLEET.** Its own as-of is above; the live board is [`inflight_usd_per_ns.py`](research/modalities/inflight_usd_per_ns.py) / `inflight-board-all.md`, which is its one home. Two defects, both recorded rather than patched: it is **stale by days**, and it is **scoped to Vast + GCP**, so **a SageMaker rental is invisible to it by construction** — which is exactly how a 3:16 PM ET ABFE dispatch on 2026-08-02 appeared on no board at all. ⚠ **It is deliberately NOT re-stamped here**: inventing a current state is the failure this board already committed. What is *not* stale is the four one-homes in the prose below the table — the buy-line arithmetic, what `R` decides, the binary-arm departure finding, and the pose-diagnostic status. See [roadmap](research/manuscripts/nr4a3-program-map.md) §12 finding 6.

*Every row is a PROGRESS reading — the counter moved since the previous pass — not a liveness ping. Rates are
measured over the stated interval, and **only quoted off a window long enough to swamp the 40-iteration commit
block**; the two withdrawn ETAs in [§Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 19b/19c
are both what happens when that rule is broken.*

**Every GPU row carries `$/ns` and its multiple of the ladder basis, and says whether that multiple is money
going out or money we refused** (CLAUDE.md §1). The basis is **$0.003412/ns**, DERIVED
(`congeneric_fanout.basis_usd_per_ns()`); the buy line is the absolute rate **$0.006539/ns**, which against
that basis is **≈1.92×**. ⚠ **That is NOT a loosening of the 1.5× ruled the same day — it is the identical
dollars per nanosecond.** The basis moved 22 % because the throughput table was re-anchored and widened, not
because any price changed; see [Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 40.

**NOTHING IS BILLING. Every lane on this board is off a host.** The closure triangle closed at 5:11 PM ET
on 2026-07-30 — all four legs landed and `R` is computed — which was the last owed GPU work in the fixed
scope. The Step 1 fan-out (LANE 17/21) and the valB_mini replicates (LANE 19) closed earlier the same day —
the rows below say what each returned. The RUNG 5a-KS legs remain **PARKED, not finished**: on no host,
costing nothing. Both LANE-13 paralogue legs and all four RUNG 2b legs have reached their deliverables.

| what | state | ETA (ET) | cost | `$/ns` vs basis |
|---|---|---|---|---|
| ~~**Step 1 fan-out** (LANE 17/21) — 19 congeneric RBFE edges~~ | ✅ **COMPLETE — 18 of 18 computable edges landed; the 19th is not computable and is recorded as such.** Off every host. The ranked table it produced is the paper's §2.9 | — | realised **$73.79** machine-ledgered, against the DERIVED cap **$74.91** (`market_ceiling_usd(19)`) — finished inside its ceiling with **$1.12** to spare | every unit of the lane was bought under the **$0.006539/ns** buy line, and the units that could not be were ⛔ **REFUSED — $0 spent** and re-offered on later ticks rather than dropped |
| ~~**valB_mini r1+r2** (LANE 19) — the 4 replicate legs~~ | ✅ **CLOSED AT n=3 — and the gate FAILED on sign, so the decision is NO-GO.** Off every host. The deliverable is the **cycle SD**, which is the number this lane existed to produce | — | realised is **NOT machine-ledgered on this lane**; the floor and the reason are in [`realised-spend.json`](research/modalities/realised-spend.json)'s attested block, which is a defect register, not an accounting category | — (no host) |
| **RUNG 5a-KS** (LANE 16) — the ligand-side causal kill-switch | ✅ **LANDED 2026-08-02 — all four legs (n = 2 seeds/arm). S = −0.1297 ± 0.3264 kcal/mol → the PREREGISTERED NULL: the marginal wedge is absent, registered in advance as the LIKELY outcome and NOT a stop.** Full record, limits and the staging verification: [the gate section above](#-rung-5a-ks-landed--the-causal-kill-switch-returns-its-preregistered-null-s--013--033-kcalmol-2026-08-02-215-am-et) and paper §2.10e. *Superseded, retained: this row previously read PARKED, NOT FINISHED, NOT BILLING since 2026-07-27 — both original legs died on a rotated S3 key and were destroyed, and the lane stayed parked because `relaunch_market_gate` refuses to re-buy above the buy line. It resumed and finished.* | **done — nothing owed** | realised: see [the ledger](research/modalities/); ladder ~$23 at four legs | ✅ bought inside the line and landed |
| ~~**The closure triangle** (LANE 9/20) — decides whether valB's miss is fixable at all~~ | ✅ **CLOSED. All four legs landed 5:11 PM ET Jul 30 and `R` is computed** — [`valb-triangle-reduction.json`](research/modalities/valb-triangle-reduction.json). Off every host | — | the 4-leg tranche was priced against its own **$3.85** ceiling per pass | every rental cleared the **$0.006539/ns** buy line; the leg that finished it ran at **$0.005049/ns · 1.48× basis**. ⚠ **THE DAY'S CHURN — SEVEN HOSTS, 11:41 AM to 4:06 PM ET, ZERO COMMITTED ITERATIONS — WAS NEITHER PRICE NOR CARD SPEED, AND BOTH EARLIER READINGS ARE SUPERSEDED.** Two measured causes. **(1)** A host wedged INSIDE a checkpoint persist: commit-store generation `fa5da1eb` holds `simulation.nc` alone, and `_persist` writes .nc → .chk → manifest — so the board counted a torn generation and read `production/1800` while the next host correctly resumed at 1760, and the leg re-ran the same 40 iterations after every host change with the percentage RISING each time. **(2)** The lane had **11 `workflow_dispatch` inputs against GitHub's cap of 10**, which is SILENT: every placement flag — card floor, bid escalation, uninterruptible tier — arrived EMPTY, so each control was chosen correctly and discarded at the door. Fixes, all with tests: `committed_progress` requires the manifest, `commit_store_audit.py` names which rule refused each generation, the idle guard condemns on byte-identical log CONTENT (its mtime test was vacuous against a 120 s timer sync), `collect` re-places a dead host in the same pass, and CI now fails a workflow that exceeds the input cap or uses GCP auth without `id-token: write` |
| **The restrained binary re-run** (LANE 20) | **HELD ON PURPOSE — and ⚠ NOT behind `R`, which LANDED on 2026-07-30.** Its gate is the **pose diagnostic** (`gpu-ternary-fep-vast.yml task=triangle-converge`, $0): the prereg forbids interpreting `R_binary` without it. **Measured 11:08 AM ET 2026-07-31** — the option reached `main` only that morning (commit `42c99101`) and the `converge` job is `skipped` in every one of the five most recent lane dispatches, so it **has still never run**. Also **not GCP-runnable**: these are the *triangle's* binary legs (2 fs, seed 0, S3-keyed), a different experiment from the r0 calibrator's restrained re-run that landed 2026-07-28 ([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 44). **The ternary arm is NOT being re-run restrained** (audit §L.3f) | held pending the pose diagnostic | **$0** | — |
| ~~**valB_mini reverse leg r0**~~ (GCP L4 **on-demand**) | ✅ **LANDED — `production/2000` of 2000; the hysteresis it unlocked is measured in the block below** | — | **$0 real dollars** — expiring GCP trial credit (closes **2026-10-10**). **A SEPARATE LEDGER**: never summed into realised or ladder spend | — |
| ~~LANE 13 categorical-dynamics analysis~~ | ✅ **DONE 2:49 PM — the verdict is above.** Legs, collect and analysis all landed | — | realised **~$4–5** against a ~$4.3 projection | — |

**✅ `R` HAS LANDED (5:11 PM ET, 2026-07-30) AND THE ANSWER IS THE FIRST BRANCH BELOW.** Every number here is
a reading of [`valb-triangle-reduction.json`](research/modalities/valb-triangle-reduction.json), never typed:
**`R = 0.2128 kcal/mol`**, decision **`R_CONSISTENT_WITH_ZERO`** — inside the tightest plausible noise floor
(0.216 at `sigma_leg = 0.045`). Read against the mapping below, that says valB_mini's miss is an
**ENDPOINT-STATE error, and more sampling will not fix it.**
The two closures are reported separately as the rule requires — **`R_ternary = −0.0312`**, essentially zero,
against **`R_binary = −0.2440`**, which carries nearly all of it — so this is not a clean `R_coop` hiding two
large cancelling terms. The frozen pre-registered verdict at the original bounds reads
**BINARY_PATH_DEPENDENT, prediction upheld**.
⚠ **THREE LIMITS, NONE OF THEM SMALL PRINT.** *(a)* **n = 1 and NO error bar is quoted or invented** — the
design requires one seed per edge, because a mixed-seed triangle is not a closure, so no replicate SD exists.
*(b)* At the `sigma_leg` upper bound now MEASURED from the n=3 replicates (0.265) the addendum also reads
`R_CONSISTENT_WITH_ZERO`, but at the superseded assumed 0.7 the same design reads **UNDERPOWERED** — and that
divergence is exactly [§Open decisions](#open-decisions) 7, still trimcrae's to settle. *(c)* Closure measures
**INTERNAL CONSISTENCY, NOT ACCURACY**: it is structurally blind to force-field error, the SMARCA4→SMARCA2
homology substitution, NAGL charges and protonation, every one of which is a per-endpoint state function.

**★ WHAT `R` DECIDES, stated the right way round.** The closure triangle exists to answer one question about
valB_mini's miss — **1.543 kcal/mol** at the landed n=3, the one home for which is the RUNG 2 · replicates row
in the scoreboard above — and the two outcomes point in opposite directions:

- **`R` ≈ 0 ⇒ an ENDPOINT-STATE error.** The bias is a per-endpoint state function, it telescopes out of any
  cycle, and **more sampling will NOT fix the miss.**
- **`R` materially non-zero ⇒ a PATH error, and the miss IS fixable** by the protocol changes that address it.

*(I stated this backwards earlier on 2026-07-27; the correction is
[Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 41 and this is the one home for the
mapping.)* `closure_decomposition` splits `R_coop = R_ternary − R_binary` and its own rule is to report both,
never `R_coop` alone.

**★ AND `R_ternary` NOW DECIDES A SECOND THING — whether the parked RUNG 5a-KS resume is worth buying at all.**
`S` is a two-leg difference inside the **ternary** environment, so it inherits that environment's
non-conservative error; `R_ternary` is the only measurement in the program that bounds it. The arithmetic, the
three branches (**ADMIT / HOLD / STOP\_AND\_REDRAW**) and the thresholds are **pre-registered before `R` landed**
and live once, in
[`valb_failure_propagation.s_resolvability_from_R_ternary`](research/modalities/valb_failure_propagation.py) →
[`valb-failure-propagation.json`](research/modalities/valb-failure-propagation.json) — do not restate them here.
Two properties of that rule that must survive being quoted: a large `R_ternary` at n=1 buys a **hold and a
second draw, never a kill** (`closure_noise_floor`'s own asymmetry — one draw cannot convict), and an ADMIT
bounds the **non-conservative** error class *only*, because closure is blind to per-endpoint state functions.

**⚠ AND THE POWER TO READ `R` AT ALL IS NOW MEASURED RATHER THAN UNKNOWN.** `closure_noise_floor` was written
saying `sigma_leg` is unknown to a factor of **15.6** and that *"nothing in this lane has measured it"* — the
n=3 replicates did. Converting the landed cycle SD through the design's own SD relation bounds `sigma_leg`
**above**, which excludes the range where the triangle was hopeless but leaves its power **mediocre rather than
comfortable** at the worst case. Derived, never typed: `valb_failure_propagation.sigma_leg_now_bounded` /
`power_at_measured_bound`. ⚠ **One consequence needs a $0 decision from trimcrae, and it is deliberately NOT
taken here:** `binary_departure_prereg` demotes a null closure to `UNDERPOWERED` on a hand-set `sigma_leg > 0.2`
proxy that the measured bound now trips — so as frozen, **a null `R` reports UNDERPOWERED and the diagnostic we
have already paid for answers nothing.** Amending a preregistered rule after a failing result is the retune this
program forbids, so the discrepancy is *recorded* (before `R` landed) and routed the same way as the
admits-zero gate defect — see [§Open decisions](#open-decisions).

**Committed if both billing lanes complete: ~$43** (fan-out ~$36 + valB replicates ~$7.32), against the
lane bands quoted in the rung entries below. Every figure in this column is either the LADDER's, quoted from
those entries, or the REALISED figure derived in
[`realised-spend.json`](research/modalities/realised-spend.json) —
[pricing.md](research/compute/pricing.md) owns the per-unit cost evidence and this board owns nothing.


⚠ **WHY NR4A1's REPLACEMENT HOST APPEARED TO STARVE ITS GPU — kept because the diagnosis outlived the leg,
which finished on that same host.** Three agreeing
intervals (3.4, 3.14, 3.00, the last over a full hour) put the 4080S at **~3.0–3.4 ns/h** against **~5.5–6.0
ns/h** for the same job on a 4090 — a ratio of **0.55**, where the cards' own throughput ratio for this class of workload is ~0.83. The utilisation gap says
the same thing from the other side: **44 % GPU on the 4080S against 75 % on the 4090**, steady across passes.
A card that is merely slower runs *busy*; one that is fed too slowly runs *idle*, and this one is idle. So the
cause is **host-side (CPU/PCIe feeding the PLUMED bias), not the card**.
**A SINGLE `gpu_util = 0.0` IS NOT A STALL — the progress scalar is the authority.** This host has now read 0.0
twice (05:48 AM during startup, 08:36 AM mid-run) and both times the ns counter kept climbing; a re-read seven
minutes after the second put it back at 45 %. Vast's utilisation field is an **instantaneous poll**, so it
catches the process between kernels or during a checkpoint write. The watchdog is right to require the durable
scalar to ADVANCE rather than the box to look busy — which is exactly why it reported "advancing, leaving it
alone" through both. A stall needs a **frozen counter** across two passes, not an idle-looking sample.
**The decision is to leave it alone**, and the reason is arithmetic rather than caution: moving hosts buys
~5 h of wall-clock that nothing is waiting on — the analysis is a MATCHED comparison and cannot start without
NR4A2 either way — at the price of a capacity scramble, whatever progress sits past the last checkpoint, and
a re-rent that can land on another starving host. The extra billed time is **~$0.75**. What *is* worth
carrying forward: machine **17720** should be excluded when the next paralogue leg is launched.

✅ **THE BINARY LEG'S "SLOWDOWN" WAS QUANTISATION — RESOLVED, and the discriminating observation was taken
rather than assumed.** Over 82 min the leg did **320 iterations = 234/h**, back at its baseline, so the "40 in
27 min" was one commit block caught whole. The mechanism is now confirmed rather than merely plausible: **every
delta observed on either leg is an exact multiple of 40** — binary 40, 320; ternary 120, 200 — so the commit
store advances in **blocks of 40 iterations** and a short window measures the block boundary, not the rate.
**The rule this leaves behind is in the table caption: never quote a FEP rate off a window that spans only a
few blocks.** I broke that rule in the same breath as writing it — the ternary leg's "~7:45 AM" came off a
27-minute window carrying exactly 3 blocks, which is why it is now a range off 82- and 109-minute windows
instead. *(Withdrawn ETAs are in [§Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) row 19b.)*

⚠ **THE −0.534 REFERENCE RESTS ON A BROKEN BINARY ARM — and the 2b gate SURVIVES ANYWAY. Read both halves.**
Measured 2026-07-26 (GH runs 30202934339, 30209580292; audit §L.3–L.3b): in the r0 **binary** leg the ligand's
*receptor-contacting* moiety leaves its pose and does not return in **8 of 12 replicas**, while the **ternary** leg
in the same cycle is **12/12 stable**. So ΔG_binary is not a free energy of the intended bound state, and
**ΔΔG_coop(r0) = −0.534 is not a valid measurement of cooperativity.**

But the 2b gate is a **4 fs-vs-2 fs consistency check**, not an accuracy check against a trusted value — so a
defect the two timesteps *share* cancels out of the comparison, and the gate stays meaningful **on one condition:
the 4 fs cycle's binary arm has to carry the same defect as the 2 fs one.**

**★ THAT CONDITION IS MEASURED, AND SATISFIED — the 4 fs binary arm fails the same way.** Run as a genuine test
that could have gone the other way (a clean 4 fs arm agreeing with a contaminated 2 fs one to 0.02 kcal/mol would
have meant the departure barely moves ΔG_binary, and my claim would have needed substantial softening). It did not
go the other way. GH run 30210676030 (Vast `task=converge`, CPU, $0) vs GH run 30210186711 (GCP, r0):

| | 2 fs (r0) | 4 fs (2b) |
|---|---|---|
| binary `contact_pose` max / med (Å) | 16.327 / 4.333 | **17.622 / 5.358** |
| binary replicas ending beyond 4.0 Å | **8 of 12** | **7 of 12** |
| binary λ initiation, endpoint / interior | 1 / 7 | **1 / 9** |
| **ternary** `contact_pose` max / med (Å) | 2.835 / 1.653 | **2.999 / 1.897** |
| **ternary** replicas beyond 4.0 Å | **0 of 12** | **0 of 12** |

Every feature reproduces — magnitude, replica fraction, class mix, λ signature, and the clean ternary arm — across
a different timestep, a different provider and GPU, a different commit interval and independent runs (audit §L.3d).
So:

- **The RUNG 2b timestep PASS STANDS on its own terms.** The gate asks whether 4 fs reproduces 2 fs; it does, and
  the shared defect cancels from the comparison. **4 fs adoption is not undermined.**
- **The r0 finding is REINFORCED, not softened** — the departure is a systematic property of the binary leg's
  setup, not one bad trajectory.
- **−0.534 and −0.5125 are two precise measurements of the same wrong thing.** Their agreement is evidence of
  *reproducibility*, which is what the gate claims, and not of correctness, which it does not.

Consequences kept separate, because they are independent:
- **RUNG 2 was already FAILED** (wrong sign), so this changes no verdict from pass to fail — it supplies a
  candidate *mechanism*, now on much better footing but **still a hypothesis**. The experimental target is
  **+0.94**; both cycles return ≈ −0.52 to −0.53; both have a reproducibly departed binary arm and a clean ternary
  arm. That co-occurrence is suggestive and it remains **correlational**. **The test is a restrained binary
  re-run:** sign flips positive with a held pose → mechanism established; sign stays negative → the wrong sign has
  another cause and the departure is a separate (real) defect. Do not report the mechanism as settled before that.
- **BOTH cycles need the binary arm re-run**, not only r0 — the 4 fs arm carries the identical defect.
- **IT ALSO BEARS ON THE RESCOPE REPLACEMENT — free pre-check, audit §L.3e.** The specified **synthetic closure
  triangle** (~$6) is 3 edges × (ternary + binary) = 6 legs, and its **three binary legs are the same construction
  that departs**. The design already handles this correctly — `closure_decomposition` splits
  `R_coop = R_ternary − R_binary` and its own rule says to report both, never `R_coop` alone — so **nothing needs
  changing**. What it gains is a **pre-registrable prediction**: *`R_binary` materially non-zero, `R_ternary`
  small.* Both outcomes are informative, and the second argues against my own reading — if `R_binary` is also
  small, the departure's bias is a per-endpoint state function, telescopes out of any cycle, and therefore largely
  cancels from ΔΔG_coop too. **Run the pose diagnostic on the triangle's legs when they land** (`mode=converge` /
  `task=converge`, $0) and do not interpret `R_binary` without it.
  - **⛔ STATUS OF THAT DIAGNOSTIC — MEASURED 2026-07-30, 10:50 PM ET: IT HAS NEVER RUN ON THE TRIANGLE, AND
    UNTIL IT WAS FIXED IT COULD NOT HAVE. This is the single home for that fact.** Two findings, both from
    the Actions API and the workflow source rather than from memory. **(1) It was never dispatched.** Across
    the **137** `gpu-ternary-fep-vast.yml` runs from the legs landing (5:11 PM ET Jul 30) to 10:27 PM ET, the
    `converge` job is `skipped` in every one — zero executions; across the newest **1000** runs, back to
    1:02 PM ET Jul 29, also zero. It has executed **once ever**, GH run 30210676030 on 2026-07-26, which is
    where the RUNG 2b column of the §L.3d table above comes from. **(2) A dispatch would have read the wrong
    legs**, and that is MEASURED, not inferred. The job hardcoded `--mode edge` on its `--fetch-trajectories`
    call, and `unit_id` embeds *both* the timestep and the mode — so it reconstructs `..._dt4.0fs_wu1.0_edge`
    (RUNG 2b) while the triangle wrote `..._dt2.0fs_wu1.0_triangle`; the two id sets are **entirely disjoint**,
    not partially. GH run **30599871712** (10:47 PM ET Jul 30, $0) dispatched `task=converge` and came back
    **green in 3 m 54 s** having analysed `calib_hi_to_lo__{binary,ternary,solvent}_vhl` — the RUNG 2b legs —
    and reproducing §L.3d's numbers exactly. **That is the dangerous shape**: not an empty report that would
    announce itself, but a *plausible, already-published-looking* table returned under a triangle dispatch.
    Fixed by deriving the mode from the
    dispatched task — `ternary_vast_launch.CONVERGE_TASK_MODES`, new `task=triangle-converge`; `task=converge`
    still means `edge` byte-for-byte so §L.3d stays reproducible. **Consequence, and it is the live one:
    `R_binary` is still un-cross-checked by pose data, so the bullet above is unsatisfied and the restrained
    binary re-run's gate is this diagnostic, not `R`** (`R` has landed).
- **★ DECIDED 2026-07-26 (trimcrae delegated: "it's your call"): run the triangle's binary legs UNRESTRAINED.**
  Three reasons, the first on its own decisive:
  1. **Comparability.** The triangle's economy is **r0 reused as T1** — `price_triangle` buys **4 legs, not 6**
     (**$6.83** at n=1). Restrained T2/T3 in a cycle with an unrestrained T1 makes `R` measure the
     *protocol difference*, not path error. To restrain you must re-buy T1 restrained: 6 legs, **~$10.25 (+50 %)**,
     and the reuse that justified the design is gone.
  2. **It answers a question the restrained version cannot** — whether the departure's bias is path-dependent or a
     state function. That determines whether r0's and 2b's **existing** ΔΔG_coop numbers are salvageable at all,
     which is worth far more than $6.
  3. **Sequencing, by this repo's own litmus test** (§"serialize only when one result could cancel the rest"):
     *is there a result this run could return that would make me not run the rest?* **Yes** — if `R_binary` is
     small at low σ_leg, the bias telescopes out of cycles and largely cancels from ΔΔG_coop, making a restrained
     re-run unnecessary *for the cooperativity number*. So unrestrained-first is strictly correct ordering, and a
     restrained binary leg becomes a **separate, later** experiment whose value is conditional on this result.
  **Registered in code, before any leg is bought:** `valb_triangle_closure.binary_departure_prereg()` states the
  prediction, classifies the four outcomes, and — the part that matters — reports **UNDERPOWERED** rather than
  "cancellation" when neither closure resolves at high σ_leg, because σ_leg is known only to a factor of ~15 and at
  σ_leg = 0.5 the power to resolve an r0-sized effect is **~0.22**. 8 tests pin the branch logic, including both
  branches that would count *against* the r0 reading.
  **Still HELD** until the reverse leg reads out, per the rescope hold — the decision is made, the spend is not.
- **ΔΔG_coop cannot be reported from the r0 cycle at all** until the binary arm is re-run — a blocker
  *independent* of the reverse leg's hysteresis result, which concerns the (clean) ternary arm.
- **WHAT TO CHANGE ON THE RE-RUN** (λ attribution, GH run 30210186711, audit §L.3c): the escape is *alchemically
  facilitated but not alchemically confined*. **7 of 8** departures **initiate** in the interior, skewed to the
  upper-λ states where the softcore region is largest (`{7:3, 9:2, 10:1}`), so the softening opens the door — but
  once departed the displaced state **persists at every λ including both physical endpoints**, so the physical
  Hamiltonian does not close it. Consequences: a **restraint on the receptor-contacting moiety** is the obvious
  remedy; the existing trajectory is **contaminated, not merely
  under-converged**, so extending it is not an option; and this does **not** show the binary complex model is
  wrong — an interpretation the persistence numbers alone would have supported and the initiation numbers do not.
  *n = 8 departing replicas — suggestive of an upper-λ mechanism, not a rate.*
  **Built and keyed 2026-07-27** — `ternary_restraint.py` (flat-bottom, λ-independent, default OFF) +
  `gpu-ternary-fep-gcp.yml restrain=1`, which keys the commit prefix (`_rst`) and the commit-manifest fingerprint
  so a restrained leg can never resume an unrestrained trajectory. **Two rulings live in audit §L.3f and are the
  single home for both:** (a) there is **NO standard-state correction** — this is RBFE with a never-decoupled
  ligand, the λ-independent restraint cancels from ΔG(A→B), and importing ABFE's Boresch release term would be
  *wrong* rather than conservative; (b) **only the BINARY arm is re-run restrained** — the ternary arm is measured
  clean in both cycles and both directions and keeps its trajectories. This is a *separate* question from the
  closure triangle's binary legs, decided unrestrained above.

**✅ RUNG 2b — ALL FOUR LEGS LANDED, AND 4 fs REPRODUCES 2 fs.** Reduced 2026-07-26 11:44 AM ET by the
official reducer, inside the parity image that produced the trajectories (`gpu-ternary-fep-vast.yml task=reduce`,
run 30208761567) — not by hand.

| leg | ΔG_morph (kcal/mol) | MBAR SE |
|---|---|---|
| ternary | 47.6131 | 0.1294 |
| binary | 48.1256 | 0.1321 |
| solvent | 47.7982 | 0.1016 |
| probe | 48.1970 | — |

**ΔΔG_coop(4 fs) = −0.5125** against the 2 fs reference **−0.534** → **|Δ| = 0.0215 kcal/mol**, ~33× inside the
ratified 0.7 tolerance and far below the 0.35–0.7 "consistent but weakly discriminating" band. **No NaN on any
leg**, and all three cycle legs share one protocol hash (`35573f24b6c1…`). On the gate's stated terms this is a
**PASS**, and 4 fs is adopted.

⚠ **TWO QUALIFICATIONS THAT ARE NOT OPTIONAL, both from the reducer's own output.**
1. **`system_identity_consistency` is UNKNOWN, not clean.** `n_particles`, `charge_method` and
   `setup_cache_version` are **unrecorded in all three legs**, so the check that the legs describe the same
   SYSTEM could not be made — comparability rests on `protocol_hash`, which by construction covers the OpenFE
   settings and **not** the system. This is precisely the hole that let four reverse-leg attempts run a
   146,020-particle build against a 141,968-particle one on 2026-07-25. The reducer is right to report UNKNOWN
   rather than agreement. **Root cause found and half-fixed:** the leg record wrote the *raw*
   `CHARGE_METHOD` env while the protocol payload hashes the same env **with an `am1bcc` default**, so an unset
   variable produced a hash committing to am1bcc beside an identity record saying `null`; both now write the
   resolved value. `n_particles` and `setup_cache_version` still need the Vast lane to pass them through.
   **✅ THE SYSTEM-IDENTITY QUESTION IS NOW ANSWERED ANYWAY — from the trajectories, since the leg records are
   still silent (measured 2026-07-28, $0 CPU, `ternary-system-census.yml`).** Within every arm the solute is
   identical atom-for-atom and the net charge is zero with an invariant neutralising excess; the legs differ
   only in bulk water and the counter-ions that scale with it, worth ~3e-3 kcal/mol against this gate's 0.7.
   The record and the arithmetic:
   [ternary-4fs-vast-findings.md §2d](research/compute/ternary-4fs-vast-findings.md). This does **not** retire
   the leg-record fix — a census is a manual check, and `n_particles` should still be written by the lane.
2. **The reducer's own valB gates return INDETERMINATE** — "need ≥2 independent replicates for a cycle SD",
   n_replicates = 1. That is a different question from the timestep test (it asks whether the *calibrator* is
   certified), but it means **−0.5125 carries no replicate-SD error bar**, and this repo's standard is
   replicate-SD rather than MBAR-SE.

**So: 4 fs is adopted on a single-seed agreement, and the adoption is provisional in exactly the way the gate's
own 0.35–0.7 language anticipates — not because the agreement is marginal (it is not) but because one seed
cannot produce the error bar the standard asks for. The system-identity check HAS since been made and the legs
pass it** (same alchemical system per arm; the residual difference is bulk solvent —
[ternary-4fs-vast-findings.md §2d](research/compute/ternary-4fs-vast-findings.md)).

**Why the ternary leg's ETA moved so far:** production runs at roughly **half** warmup's per-iteration cost
(625 steps at 4 fs against warmup's 1250 at 1 fs), so a leg's finish cannot be extrapolated from its warmup
rate. The table's figure is measured on **production** iterations directly. *(The two earlier quotes are in
[§Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) row 19b.)*

✅ **`vast-watchdog.yml` HAS now fired on cron** — first `schedule` event **2026-07-26 1:42 AM ET**, and it is
the pass that recovered NR4A1 (above). Autonomous coverage of the paralogue legs is therefore claimed, on the
evidence rather than on the trigger block parsing. *(The ternary watchdog's own cron is stretching far worse than that — it fired 9:17 PM then **not for 3h40m**. **"Busy repo" is measurably NOT the cause:** repo Actions load had fallen to **~2 runs/h** in that window. Ruled out with evidence — the file parses, its `run:` block is 368 chars, its registered `state` is `active`, and manual dispatch works every time. The proof it is repo-wide rather than a defect in either watchdog is **`vast-price-sample.yml`**, an unrelated cron, showing the same pattern in the same window: **7:15 PM → 9:01 PM (106 min) → 12:46 AM (225 min)**. So a newly-added `schedule:` proving itself is necessary but **not sufficient** — this repo's crons deliver ~2–4 h regardless of the expression, and no cron expression changes that.)*


## ✅ THE FIRST FORWARD/REVERSE HYSTERESIS THIS PROGRAM HAS EVER MEASURED — **GATE PASSED** (2026-07-27 2:14 PM ET)

*★ **APPENDIX — a landed gate.** The one home for the hysteresis numbers; the scoreboard defers to it by name. Roadmap: instrument `V5`.*

**|ΔG_fwd + ΔG_rev| = 0.325 kcal/mol against the preregistered ceiling of 1.0 → PASS.** The `calib_hi_to_lo`
ternary leg is now complete in both directions, which is what made the criterion measurable at all; every prior
reduction in this lane reported it as unmeasured because no reverse leg had ever run.

| leg (`calib_hi_to_lo__ternary_vhl`, seed 0) | ΔG_morph (kcal/mol) | MBAR SE |
|---|---|---|
| forward | **+47.470131** | 0.110758 |
| reverse | **−47.794736** | 0.086487 |
| **abs(fwd + rev)** | **0.324605** | vs ceiling **1.0** → **PASS** |

⚠ **THE ERROR BARS ABOVE ARE MBAR SEs AND ARE THEREFORE NOT THIS REPO'S STANDARD.** They are quoted because
they are what a single replicate can produce, and they are a **provenance** label, not a magnitude claim: this
program's uncertainty is the **replicate SD**, and at `n_replicates = 1` **there is none** — the reduction
reports `cycle_sd_kcal: null`, not a small number. The hysteresis itself is a *path-closure* check on one
replicate and does not need a replicate SD to be well-posed; the **calibration** verdict does, and it is
INDETERMINATE for exactly that reason.

**Verified to be a genuine reverse run before the number was read**, because the failure mode it guards against
produces the best-looking possible answer: a reverse leg that silently re-reported the forward trajectory
sign-flipped would give a hysteresis of **exactly 0.000**. Four discriminators, all from the artifact — the
opened `.nc` holds **141,968 particles** (`v2pe`, the *same* system as fwd, **not** the 146,020-particle `v1`
build that killed four earlier attempts), the ΔG is **−47.794736** rather than −47.470131, the MBAR SE differs,
and the per-replica pose statistics differ. Full table:
[audit §L.7a](research/modalities/ternary-lane-guard-audit-2026-07-25.md).

**What this does and does not change.** It closes one preregistered criterion and nothing else:

- **RUNG 2 (valB_mini) is still FAILED** on the wrong sign, and the calibration gate is still **INDETERMINATE**
  at `n_replicates = 1` — the hysteresis is a *cycle-closure* check, not an accuracy check.
- **ΔΔG_coop still cannot be reported from the r0 cycle**, for the reason already on this board: the binary arm
  is broken and must be re-run. That blocker is independent of this result and is untouched by it.
- **The convergence state is now reported as `MEASURED_FAILURE`, not as unexamined** — the first time the lane
  has said that out loud. It is driven by `ligand_stable_ok` in both directions.

**★ AND THE REVERSE LEG IS THE CONTROL THAT MAKES THE BINARY ARM'S FAILURE SPECIFIC.** The rev leg passes every
health flag — overlap, connectivity, equilibration, mixing, within-leg fwd/rev, plateau, quarter-block — except
`ligand_stable_ok`, at contact-pose max **4.737 Å** against a 4.0 threshold, median **2.529**, **11 of 12
replicas STABLE**, and the single departure **initiating at λ state 11, a physical endpoint**. Set against the
**binary** arm's **8 of 12** replicas departing at **16.6 Å**, a ternary arm that is 12/12 clean forward and
11/12 clean reverse says the departure is **specific to the binary arm's missing second protein**, not a
protocol-wide defect. Clean in *both* directions is what makes that a comparison rather than an assertion.

**How this was nearly lost, and what changed:** the reducer computed 0.325 and the verdict annotation printed
*"NOT MEASURED (no reverse leg reduced)"* — two further layers of the direction-keying/absent-value defect, one
a replicate-count guard suppressing a criterion that needs no replicates, one a reader naming a field the
producer never emitted. Both fixed, 21 tests, the key sweep extracted from the YAML by AST rather than retyped:
[audit §L.7](research/modalities/ternary-lane-guard-audit-2026-07-25.md).

---

## Program and thesis

*★ **APPENDIX — the thesis.** The one home for the thesis and, in `MECHANISM-FIRST` below, for the margin arithmetic (required vs resolvable vs achieved). The [roadmap](research/manuscripts/nr4a3-program-map.md) §1 links here and carries none of the figures. `tests/test_selectivity_margin_model.py` asserts the derivation.*

The goal is the **state of the art of what in-silico methods can do for an NR4A3-selective degrader** — a
complete, rigorous, honest computational characterization for extraskeletal myxoid chondrosarcoma (EMC, driven by
the **EWSR1::NR4A3** fusion), pursued with **no wet lab**. Every result is reported at its true weight; the
deliverable is a preprint + journal submission (ChemRxiv/JCIM) plus targeted outreach, not a ship-when-adequate
minimum. This program is ≈70–80% of repo effort; the broader EMC route portfolio (fusion-junction ASO and other
routes as support/backup) is context beneath it — see
[emc-treatment-strategy.md](research/manuscripts/emc-treatment-strategy.md) and [IDEAS.md](research/IDEAS.md).

**Thesis.** Paralogue selectivity, where achievable, emerges **jointly** from a modest binary warhead preference,
ternary cooperativity, and ubiquitination-compatible geometry — not from binary pocket selectivity alone. Close-
paralogue degrader selectivity is created at the **induced target–E3 interface** and differential lysine geometry
(as in BRD4-vs-BRD2/3, CDK6-vs-CDK4, p38 isoforms), never at the conserved warhead pocket, and in every landmark
case it was *discovered then rationalized by a solved ternary structure* — never predicted blind. There is no
validated prospective selectivity predictor in the field, and AKT1/2/3 is the cautionary null (isoforms too
homologous → only pan-degraders).

### MECHANISM-FIRST is the search order (the thesis above is unchanged)

Selectivity mechanisms are not interchangeable, and the program was pursuing the hardest one exclusively. Two
classes:

- **MARGINAL** — the paralogue is thermodynamically disfavoured. This is the induced-interface wedge. A useful
  degradation window needs **~2.0 kcal/mol** of true margin (median over 27 potency scenarios, range 1.75–2.25;
  [`selectivity_margin_model.py`](research/modalities/selectivity_margin_model.py)), against a best-case
  **resolvable** difference of **0.60 kcal/mol** and a **measured** accuracy of **1.543 kcal/mol, wrong sign**.
  **★★ BOTH HALVES OF THAT SENTENCE CHANGED ON 2026-07-30, IN OPPOSITE DIRECTIONS, AND THIS IS THE ONE HOME FOR
  THE CURRENT PAIR.** ⚠ **Superseded, retained: a resolvable difference of `1.12 kcal/mol` at `replicate SD 0.7,
  n = 3`, beside a *literature* accuracy of ~1.7 kcal/mol RMSE** ([Appendix
  A](#appendix-a--superseded-numbers-and-retracted-claims) 53).
  - **PRECISION improved, because the replicate SD stopped being assumed.** 0.60 is
    `minimum_detectable_difference(0.375, 3)` — **DERIVED, never typed**
    ([`selectivity_margin_model.minimum_detectable_difference`](research/modalities/selectivity_margin_model.py))
    off the **measured** cycle SD whose one home is the RUNG 2 · replicates row of the scoreboard. The retired
    1.12 was the same function at **SD 0.7 — a number nothing in this program had ever measured.** Two caveats
    that travel with it and must not be dropped: the SD was measured on the **SMARCA2/VHL** calibrator and is
    *transferred* to NR4A exactly as the cost bases are, and it is an **upper** bound on sampling-only scatter
    because it also carries model-swap and independent-solvation variance
    (`valb_failure_propagation.sigma_leg_now_bounded`).
  - **ACCURACY got worse, and it is no longer a literature figure.** The one known-answer test of this exact
    quantity class missed by **1.543 kcal/mol with the wrong sign**, and `R` localises that to an
    **endpoint-state** error — so replicates cannot touch it.
  - **★ SO THE BINDING CONSTRAINT ON THIS AXIS HAS MOVED FROM PRECISION TO ACCURACY.** The axis is no longer
    "near its resolution limit" — the margin it must detect is now **~3.3× the measured noise floor** rather
    than ~1.8×. What it lacks is a calibrated known answer for the *form* the program actually uses. **This
    axis is an UNCALIBRATED confirmation tool, not a blunt one** — a different defect, with a different
    remedy (a calibrator, not more sampling), and [§WHAT THE LANDED RESULTS CHANGE](#-what-the-landed-results-change-about-the-remaining-plan)
    carries what follows from it.
- **CATEGORICAL** — ⚠ **NARROWED 2026-07-25/26 (Lane 13, $0, before any flagship spend): the paralogue is
  structurally incapable *AT THE ALIGNED POSITION* — which is NOT the same as "a covalent bond cannot form on
  it at all", and this file asserted the stronger claim.** The sequence fact is exact and unchanged: NR4A1 and
  NR4A2 carry no cysteine where NR4A3 has C397. **What does not follow is that they present no reachable
  nucleophile.** Three measurements:
  - **Only 4 of NR4A3's 20 enumerated cysteines are unique; 16 are SHARED — and one of the shared ones is
    inside the design gate.** Term (a) is built from `unique_cysteines` **only** and summarises the conserved
    set at the 20-atom *sampling ceiling*, never at the 12-atom gate — so *"all term-(a) basins reach C397 and
    only C397"* (3 of them, post-correction) is a statement about **{C397, C420, C559}**, not about every
    cysteine. Scored over **all** of
    them on the same 75 unbiased conformers, **C496 — whose homologue is NR4A1 C465 / NR4A2 C465 — reaches the
    ≤12-atom gate in 29/75 = 0.387** (Wilson 0.285–0.500). **What closes it is BURIAL (RSA median 0.023), not
    geometry.**
  - **Each paralogue's static opened model presents TWO cysteines inside the same gate**, and **NR4A1 C465 opens
    at a 6-atom linker against C397's 10** — i.e. *more* geometrically accessible than NR4A3's own handle.
    (NR4A1 C551, the celastrol site, at 10; NR4A2 C465 at 10, C534 at 12.)
  - **Matched-construct test** (same placement, warhead exit anchor, E3 anchor and budget; 5,657 placements):
    P(a paralogue Cys is also reached | an NR4A3-unique one is) = **0 at 12 atoms, 0.081 at 16, 0.258 at 20** —
    and **16–20 is a range this plan already contemplates** (C420 needs 16, C559 needs 20, `best_linker_atoms`
    reads 19).

  **★ SO WHAT ACTUALLY HOLDS THE CATEGORICAL AXIS UP IS EXPOSURE, NOT ABSENCE.** Every paralogue cysteine in
  range sits at RSA **0.011–0.165** against C397's **0.395**, so reach-**and**-exposure still gives **0
  collisions at every length**. But that is **one number per residue from one conformer**, and RSA is the most
  conformationally variable quantity in play — C397's own range over its ensemble is **0.108–0.673**. The
  matched paralogue MD ensembles that turn those single numbers into distributions are **in flight** and the
  verdict is deliberately marked **`VERDICT_NOT_EVALUABLE`** until they land, rather than reported as a clean
  pass computed against zero paralogue frames. *(Not reimplementation drift: the same pipeline reproduces the
  committed handle-ensemble values exactly — C397 0.960 at the gate, C420 0.000, C559 0.000, RSA median 0.416.)*
  **Consequence for the design: keep the linker SHORT.** The discrimination is clean at 12 atoms and degrades
  measurably by 16–20 — so a construct that reaches C397 at 11 atoms is not merely more tractable, it is
  *more selective*, and any design drifting to 16+ atoms trades away the axis it exists to exploit.

  *(Original framing, retained because the sequence fact under it is exact:)* the paralogue is structurally
  *incapable*. NR4A3 carries reactive residues that BOTH
  paralogues lack, verified from full-length UniProt with two independent aligners
  ([`nr4a_paralogue_unique_residues.py`](research/modalities/nr4a_paralogue_unique_residues.py) →
  [`nr4a-paralogue-unique-residues.json`](research/modalities/nr4a-paralogue-unique-residues.json)):
  **C397** (NR4A1 N363 / NR4A2 S363; **RSA over a 100-conformer MD ensemble: median 0.416, mean 0.405 ± 0.096,
  p10–p90 0.298–0.510 — the committed single-frame 0.395 sits at the MEDIAN**, so the handle is not a lucky
  frame; reachable at the ≤12-atom gate in **72/75 = 96 %** of unbiased frames. Also NOT geometrically closed —
  it opens at a 10-atom linker on an E3-independent bound, so a term-(a) shortfall is about WHERE RECRUITERS
  DOCK, not about the target. **★ But the chemistry axis is ONE RESIDUE DEEP: C420 and C559 reach the gate in
  0/75 unbiased frames** — C420 needs **16** atoms, C559 **20**, and that contour length is paid out of the
  *same* budget that must span to the E3. **Concentration risk, not fragility**, and there is **no geometric
  fallback**; the untested failure modes are chemical — pKa, nucleophilicity, adduct stability, promiscuity.
  A live failure mode that does **not** fire: pocket-druggability and C397 reach are **independent** —
  P(both) = 0.560 against an independence product of 0.563, and P(reachable | druggable) = **0.955**), C420
  (18.3 Å, exposed), C559 (12.8 Å but RSA 0.095 — buried in this conformer, so not currently tether-reachable);
  and exposed unique lysines **K572** (RSA 0.879, 11.5 Å), **K518** (0.413, 13.4 Å), **K592** (0.506, 16.2 Å),
  all in the same 11–16 Å band as the conserved ones — so an E3 can be steered onto a unique lysine instead of a
  shared one. At **zero** thermodynamic margin these give 0.82 (unique lysine) and 0.92 (covalent capture,
  time-integrating form) on the window metric where the interface-only null gives 0.185. **Precedent: the
  field's one demonstrated case of NR4A-family-selective degradation, NR-V04, is most parsimoniously explained
  by a paralogue-unique cysteine — NR4A1 Cys551, which NR4A3 lacks (T579).** That covalency remains a genuine
  confound for the retrospective (RUNG 4); it is *also* the reciprocal handle this program should use.

The program is therefore **mechanism-first, then orientation**: rank basins by whether they place an electrophile
at an NR4A3-unique cysteine and whether their E2~Ub transfer zone covers a unique lysine rather than a conserved
one; use interface thermodynamics to **rank within** the surviving set, never to create selectivity on its own;
test causality with a matched-pair cycle; and **STOP before the flagship spend if no mechanism survives** —
publishing the honest negative, now stronger because it rules out three mechanisms instead of one. The final
deliverable is a **computationally prioritized, structure-defined, retrosynthetically annotated candidate set
with an identified causal selectivity mechanism — degradation experimentally unvalidated.**

*Checked and reported weak, not quietly dropped:* the EWSR1 moiety of the fusion contributes only **1 lysine**
(residues 1–264, K144) or 2 (1–349) — the low-complexity domain is Lys-poor — so fusion-lysine-directed
ubiquitination is a thin handle and is **not** a design axis. It stays a modelling scenario only.

## Honest scope and language discipline (apply everywhere, including the manuscript)

*★ **APPENDIX — language discipline.** ⚠ **21 provenance strings in [`lint_claims.py`](research/manuscripts/lint_claims.py) name this section by title**; renaming or dissolving it invalidates all 21 in a CI-enforced linter. The rules run over the paper, the SI **and the roadmap**.*

Everything is **conditional on the hypothesized cmpd19 binary pose × the chosen receptor frame** — a *double*
conditionality; a wedge surviving only one poorly-supported pose is penalized or dropped. Right-size every claim:

- "selective hit" → **"predicted selective candidate"**; "NR4A3-selective" → **"predicted NR4A-paralogue-selective"**
- "does bind at all" → **"is compatible with the hypothesized conditional bound state"**
- "recovered degradation" → **"produced a surrogate score concordant with the reported outcome"**
- "synthesis-ready matrix" → **"a computationally prioritized, structure-defined, retrosynthetically annotated
  candidate matrix for synthesis and experimental testing"** (only earned once exact structures/stereochem,
  exit-vector chemistry, routes, building-block availability, and physicochemical assessment exist).
- **Never imply** proteome-wide selectivity, EMC efficacy, safety, a therapeutic window, or clinical readiness.
  The parent cmpd19 study reported transcriptional effects **including MYC induction**, so parent-warhead
  pharmacology is a **potential liability**, not evidence of benefit.
- **Novelty is incremental, not landmark.** All-atom alchemical ternary-cooperativity FEP — the same
  `ΔΔG_coop = ternary − binary` cycle, including VHL–BRD4/MZ1 and paralogue-selectivity applications — is an
  active published area (Chen 2023; *JCTC* 2025 `10.1021/acs.jctc.5c00064` / `5c00736`; *JCIM* 2024
  `10.1021/acs.jcim.4c01227`). The paper must cite and benchmark against this prior art. An open-source
  OpenFE-based implementation + the honest NR4A application is an incremental methods contribution.

Enforcement: [`lint_claims.py`](research/manuscripts/lint_claims.py) implements rules R1–R5 from this section
against the paper + SI and runs in CI on every push. It is sentence-scoped — a disclaimed use of a regulated
word passes; asserting the regulated claim does not.

---

## Validation architecture (the five requirements)

*★ **APPENDIX — the validation architecture.** The external reviewer's five conditions on what a result may claim. ⚠ **Cite these as "validation requirement 1–5", never as "R1–R5"** — the [roadmap](research/manuscripts/nr4a3-program-map.md) §0.6 lists five different things in this program called `R`. Roadmap mapping: requirement 1(A)→`V6`, 1(C)→`V5`, 2→`R6`, 3→`V9`, 4→§6a's NR-V04 row, 5→`R12` and `R13`.*

These come from the external reviewer's conditional approval ([verbatim
verdict](research/manuscripts/nr4a3-degrader-reviewer-revisions-2026-07-15.md)) and govern what any result is
allowed to claim.

1. **Three DIFFERENT validations — never let one stand in for another.**
   - **(A) Accuracy control** — a compact *public* RBFE benchmark (measured ΔΔG + supported poses) through the
     *exact* container / protocol / force field / water model / sampling / analysis used for NR4A. Cycle closure,
     fwd/rev agreement, and MBAR overlap are **precision diagnostics, NOT accuracy** — a closed cycle can be
     systematically wrong.
   - **(B) Target-specific precision** — the cmpd19 RBFE, framed as *conditional relative free energies for a
     hypothesized cmpd19 mode within preselected open NR4A conformers.* It tests reproducibility and
     receptor-sensitivity, **not** binding-model correctness (cmpd19 has no measured affinity, no pose).
   - **(C) Ternary known-answer control** — a system with an experimental ternary structure + measured
     binary/ternary affinity/cooperativity + an analogue series (VHL–BRD4 or VHL–SMARCA2). **NR-V04 is a
     biological-selectivity holdout, not the method calibrator.**

2. **Cryptic-pocket thermodynamics are conditional.** An affinity computed in a pre-opened pocket is
   ΔG_bind|open, not the observable ΔG_bind,obs ≈ ΔG_open + ΔG_bind|open. Each paralogue can have a **different
   opening penalty**, so comparing binding only in matched open receptors can miss or REVERSE selectivity.
   Either integrate a converged **ΔG_open per paralogue**, or report everything **explicitly conditional** on the
   chosen open states. Pocket collapse in MD is *evidence the state is unstable*, not an auto-fail; restraint free
   energies must be included or the result stays conditional; **do not** claim "under-sampling means true binding
   is likely stronger" (bias runs both ways). Never pool conformers of unknown population as equally weighted;
   use Boltzmann weighting where estimable, else report sensitivity ranges — never a synthetic "ensemble affinity."

3. **ABFE is HELD and reframed.** T4L-L99A·benzene is an implementation smoke test, **not a transferable
   offset** — report raw ABFE, report the T4L discrepancy separately, apply no offset. ABFE does **not** prove
   cmpd19 "binds at all"; it only asks whether the hypothesized pose is thermodynamically plausible under the
   modeled assumptions. Not worth running until the accuracy benchmark passes, the opening penalty is handled,
   and multiple poses are treated. Step 8 cannot "consume the anchor ABFE per construct" — linker/recruiter
   attachment alters the bound ensemble, so free-cmpd19 ABFE ≠ each degrader's binary affinity. **HELD also means
   the λ-overlap repair of the existing ABFE block is parked, not in flight** — the manuscript must say so.

4. **NR-V04 is covalent.** Celastrol binds NR4A1 **covalently via C551**, so NR-V04 does not validate the
   noncovalent machinery used for cmpd19, and its selectivity may be largely **target-engagement**, not ternary
   cooperativity. Model a **preformed covalent adduct**; add a **noncovalent-vs-covalent sensitivity analysis**,
   an **NR4A1 C551A / nonreactive control**, and **warhead-only + active/inactive recruiter** controls; use
   scoring rules preregistered on control (C). Report only **directional concordance** with the reported
   NR4A1-degraded / NR4A2·3-spared outcome — never "recovered degradation."

5. **The prospective stage is hypothesis PRIORITIZATION, not scoring.** Replace any tunable scalar with **staged
   gates + a Pareto/constraint-satisfaction front** (binary plausibility → ternary thermodynamic/ensemble →
   linker strain → ubiquitination geometry → physicochemical → robust selection), with uncertainty on every
   axis. Model the **real biological object, EWSR1::NR4A3** (not an isolated LBD): fusion-context ensemble;
   lysines **outside** the LBD (hinge, DBD, fusion partner); public EMC VHL/CRBN expression; **full CRL/E2~Ub
   geometry ensembles**. Ternary formation is necessary, not sufficient — productive lysine positioning is a
   distinct requirement.
   **★ TWO MEASUREMENTS LANDED HERE 2026-07-25 (LANE 2, $0), and BOTH correct assumptions the program was
   using — they bind on every ternary / degradation-geometry step, not just 5a:**
   - **The ubiquitin-transfer distance is 17.1 Å, MEASURED** — nearest of 11 substrate lysines in a *solved*
     CRL4–CRBN assembly. The repo's assumed **10 Å was ~7 Å too strict** and, applied as written, **would have
     been the wrong scale and would have MATERIALLY WEAKENED the term-(b) lysine signal.** ⚠ *Corrected
     2026-07-25: an earlier "would have suppressed it entirely" is **contradicted by the committed sweep** —
     84/192 basins still reach rank ≥3 at 10 Å, against 75 at 17 Å.* Any transfer-zone criterion must use the
     measured band.
   - **⚠ A COMPOSED CRL RING CARRIES ~30–50 Å OF POSITIONAL UNCERTAINTY** *(measured on both arms 2026-07-25:
     **VHL 30.18 Å, CRBN 50.14 Å** — the original 48.6 Å was one arm. **NOT IN FORCE in the authoritative
     Tier-2 run**, which anchors both arms on the observed E2 catalytic cysteine rather than a composed RING.)*
     Original finding:** A known-answer check *falsified its
     own construction*: a RING composed from a receptor entry + a cullin scaffold — with **both bridges < 1.5 Å** *(true of the 48.58 Å pair only; CRBN's own-assembly bridge is **1.916 Å** — and CRBN carries two live composed-RING numbers, 48.58 and 50.14, through different bridges, which is a one-fact-one-place hazard)*,
     i.e. each join individually excellent — sat **48.6 Å** from the RING of an intact deposited assembly. This
     is **conformational, not error**: CRLs are genuinely mobile, so a well-fitted composition is still not a
     position. **Consequence: no degradation-geometry claim may rest on a RING or E2 that was COMPOSED rather
     than observed.** The fix in use is to anchor on the **observed E2 catalytic cysteine** from solved
     assemblies (**8R5H** for VHL, **9UUM** for CRBN). Relatedly, the E2 catalytic cysteine had been *guessed*
     by a heuristic; identifying it by proximity to ubiquitin's C-terminus gives **Cys85 at 3.4 Å vs 16.4 Å**
     for the next-nearest — and **overturns the heuristic's answer**.

### Why Val A is nearly free but Val B is load-bearing

**Val A (binary RBFE accuracy) — a citation, not a paid benchmark, FOR THE BINARY LANE ONLY.** We run OpenFE's
*standard* RelativeHybridTopology protocol, already benchmarked (~1.7 kcal/mol over 58 public systems). The only
thing that had made it non-citeable was a self-inflicted deviation — the RBFE env shipped without AmberTools, so
am1bcc charging failed and fell back to the NAGL surrogate. With AmberTools added and `am1bcc` restored, the
**binary RBFE lane** is on the documented reference method → we **cite OpenFE** and run only a ~$0–15
build-consistency smoke (valA_mini, done).

**The charge model is NOT shared across lanes.** The lanes split:

| Lane | Charge model | Evidence |
|---|---|---|
| Binary RBFE (`nr4a3_rbfe.py`) | **am1bcc** | code default; valA_mini/step0/step1_pilot all ran am1bcc |
| Ternary FEP (`nr4a3_ternary_fep.py`) | **NAGL** | **the stored hybrid `System` of every banked valB leg, read 2026-07-29** ([`charge-provenance-forensic.json`](research/modalities/charge-provenance-forensic.json)) — *not* the `gpu-ternary-fep-gcp.yml` default or the `CHARGE_METHOD: nagl` log line, which record what was requested ([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 47) |
| Endpoint / covalent MD | **NAGL** | `md_settings.py:60` `CHARGE_METHOD = "nagl"` |

The split is **physically forced, not sloppiness**: AM1-BCC via AmberTools `sqm` is intractable on PROTAC-sized
ligands — measured 2026-07-22, `sqm` ran **>85 min on the 166-atom NR-V04 recruiter without converging**
(`md_settings.py:53–60`). NAGL is an ML surrogate *for* am1bcc, so this is a defensible substitution, but it is a
**different Hamiltonian** and must be handled explicitly:

1. **ΔΔG_coop is SAFE — and this is now MEASURED FROM THE SYSTEMS, not read off the configuration
   (2026-07-29, $0, `task=charge-provenance`).** Both morphs of the cooperativity cycle
   (`ternary − binary-of-the-same-PROTAC`) run inside the ternary lane at the same `CHARGE_METHOD`, so the
   charge model cancels; the cancellation argument holds *within* a lane, which is all it ever needed.
   ⚠ **But `CHARGE_METHOD` is what was REQUESTED, and for a while that was the only evidence there was.**
   OpenFE prefers user-supplied charges over its configured `partial_charge_method`, and every relaxed pose
   file on this lane carries a complete per-atom set for its λ=0 endpoint — so a `partial_charge_method = nagl`
   log line proves nothing about what a leg actually sampled, and the failure mode it hides is silent by
   construction ([`nr4a3_rbfe.strip_foreign_partial_charges`](research/modalities/nr4a3_rbfe.py), third
   failure mode). Every banked valB leg's stored hybrid `System` was therefore read: the arms of r0, r1 and r2
   carry **identical** alchemical charges (109/109 core atoms), the reverse leg's endpoints are the forward
   leg's swapped, and the inherited set is the protocol's own NAGL set — fixed by the binary arm, which ran
   with **nothing to inherit** and produced the same numbers. One home for the per-leg evidence:
   [`charge-provenance-forensic.json`](research/modalities/charge-provenance-forensic.json). Superseded (the
   configuration-only basis): [Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 47.
2. **Any CROSS-LANE subtraction is NOT safe.** A quantity built as `(ternary-lane leg) − (binary-lane leg)`
   mixes NAGL against am1bcc, and a charge-model difference is a real potential-energy-surface difference that
   does **not** cancel. Such cycles must pin one `CHARGE_METHOD` across **both** legs — this is why the
   protein-mutation wedge (RUNG 5a-KS confirmatory) carries a hard `assert_charge_consistency` refusal.
   (Timestep differs across lanes too — 2 fs ternary vs 4 fs+HMR binary — but HMR changes only masses, so that
   is a *sampling/precision* difference, not a bias in ΔG.)
3. **Val A's citation does not cover the NAGL lanes.** OpenFE's published ~1.7 kcal/mol accuracy was measured on
   the am1bcc method; valA_mini reproduced a known ΔΔG on am1bcc. Neither transfers to a NAGL ternary lane. The
   accuracy control for the NAGL lane is **Val B** (its own known-answer PROTAC) — which is why valA_full's
   "re-open if am1bcc is forced onto NAGL" trigger is satisfied *by Val B* and not by a separate paid NAGL
   binary benchmark. Say this in the paper; do not let a reader infer the OpenFE citation covers the ternary
   numbers.

**Val B (ternary cooperativity) — genuinely needed, for pipeline-validation.** The general approach is citeable
(prior art above), but you never certify your own container / force field / charge model / ternary wiring by
pointing at someone else's engine's benchmark. NR-V04 cannot calibrate it (no solved ternary; celastrol is
covalent, so it doesn't even exercise the noncovalent morph). The only way to know our cooperativity numbers
mean anything is to run a known-answer PROTAC (VHL–BRD4 / VHL–SMARCA2) through our own pipeline. **Val B-mini is
the highest-value dollar in the plan** — the cheapest gate on the entire prospective ladder.

---

## The prospective stage: mechanism-first, then orientation-first inverse design

*★ **APPENDIX — the prospective stage.** The kill-switch semantics, the four-tier table and the Tier-2 result in full. `e3_recruiter_staging.py` reproduces its panel verbatim. Roadmap: `R11`, `R12`, `R15`.*

The molecule-first approach — enumerate a fixed {warhead×exit×ligase×linker} matrix, model each ternary, score,
and hope the Pareto front contains a selective degrader — is a well-controlled lottery: it *verifies* selectivity
if already present but never asks the design question. Orientation-first fixed that. Putting the **mechanism**
above the orientation fixes what the orientation search is optimising:

```
paralogue-unique CHEMISTRY (nucleophile) + paralogue-unique GEOMETRY (lysine)
    → basins that exploit ONE of them → productive CRL geometry
    → interface thermodynamics used to RANK within the survivors
    → linker requirements → candidate molecules
```

This removes blind linker guessing and preserves everything requirement 5 mandates (Pareto/uncertainty,
EWSR1::NR4A3 fusion context, lysines beyond the LBD, full CRL/E2~Ub ensembles). Four additions to the basin
search, all **$0 CPU** (rationale and evidence: the [2026-07-24
revision](research/manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md)):

- **(a) Electrophile-reach term** — does the basin's linker path pass within tethering distance of C397 / C420 at
  a geometry a mild electrophile could adopt? Neither sits *inside* the pocket, so this is an electrophile on the
  **exit vector or the linker**, which in a degrader is architecturally free — the linker already leaves the
  pocket and travels 10–20 Å. **Prefer a REVERSIBLE-covalent handle** (cyanoacrylamide-type): an irreversible
  adduct makes the degrader stoichiometric and forfeits catalytic turnover, the property that makes PROTACs
  attractive. Electrophile promiscuity is an unresolved liability with no wet lab to check it, and must be
  reported alongside the parent warhead's MYC induction, not buried. *(C559 is unique and 12.8 Å out but buried
  at RSA 0.095 in this conformer — carried only as a candidate the MD-ensemble add-on could reopen.)*
- **(b) Transfer-zone lysine-identity term** — which lysine does the modelled E2~Ub transfer zone cover? Score
  *unique-only* highest, *unique + conserved* next, *conserved-only* lowest. This is set membership, not energy.
  Honest limit: real degraders often ubiquitinate several lysines and lysine-less substrates can still be
  degraded (N-terminal / Ser / Thr / Cys ubiquitination), so this **raises the odds; it does not guarantee** the
  paralogue is spared.
- **(c) E3 breadth, free at the search stage** — widen beyond VHL/CRBN to the ligandable set with public
  ligand-bound structures (cIAP1/BIRC2, DCAF1, DCAF15, DCAF16, KEAP1, FEM1B, RNF114, MDM2). Since basin search is
  CPU this costs ~nothing and multiplies the chance that *some* E3 surface complements NR4A3's differential
  surface. **Downselect to ≤2 recruiters before any GPU leg, and log what was dropped** — a silent top-N reads as
  "we covered everything". Availability is already answered and does **not** constrain the choice (RUNG 5a).
  **★ DONE 2026-07-25, $0 (CI run 30169233382, 2,919 fetched URLs — every field fetched, none recalled).**
  Staged, assessed and downselected: **CRBN (9CUO, 1.60 Å) + VHL (9GIO, 1.486 Å) advance**, with VHL explicitly a
  **backfill** for E3-choice sensitivity, *not* a co-winner — CRBN is the sole Pareto-front member and the
  CRBN−VHL margin is **0.033** in open solid angle on one conformer each, reported as a tie rather than a
  finding. All eight others are logged with reasons in
  [`e3-recruiter-staging.json`](research/modalities/e3-recruiter-staging.json) → `downselect.dropped[]`, each
  carrying an explicit `availability_was_not_a_factor: true`; rationale in
  [e3-recruiter-downselect-2026-07-25.md](research/modalities/e3-recruiter-downselect-2026-07-25.md). The rule
  was **preregistered before the fetch**: three gates (public ligand-bound structure ≤3.0 Å; ligand buried
  fraction ≥0.50; exit clearance ≥8 Å with 30° cone openness ≥0.30), then a Pareto front over analogue tier /
  exit quality / open solid angle, then a fixed lexicographic tiebreak — **no tunable scalar**.
  **★ THE FINDING THAT CHANGES HOW THIS ITEM READS: the binding constraint on E3 breadth is STRUCTURAL
  STAGEABILITY, not availability.** HPA says all eight widened arms are available; the **PDB says the panel is
  materially smaller**. **RNF114 has no deposited structure of the protein at all**; **DCAF16**'s ligand is only
  **34 % buried** once its partner is removed — a *glue interface, not a handle pocket* — despite having the
  panel's highest open solid angle (0.736); and **DCAF15** has no partner-free liganded structure, its "solved
  ternary" claim failing coordinate-level verification. **So the widening delivered less breadth than this
  plan's text implied, and it CONFIRMED the incumbents rather than displacing them — a real, publishable
  negative for the E3-breadth argument, and it must be reported as one rather than quietly absorbed.**
  ✅ **THE VHL ARM WAS RE-CHECKED AND IT HOLDS (2026-07-26, $0, CI run 30180602564).** The concern was that
  **9GIO** — the structure the downselect advanced VHL on — is titled *"…with a covalent compound bound to C77
  of VHL"*, which would mean its ligandability and exit-vector numbers described a **covalent Cys77 site** rather
  than the VH032-class **hydroxyproline pocket** every VHL PROTAC linker actually leaves from. **Both
  descriptions are true, of DIFFERENT ligands — and the staging used the right one.** 9GIO carries **two**:

  | ligand | hydroxyproline-pocket residues contacted | contacts Cys77? | nearest Cys77 Sγ |
  |---|---|---|---|
  | **`3JF`** — *the one the staging used* | **10** | **no** | **12.35 Å** |
  | `A1IMD` — the one the title describes | 1 | **yes** | **1.84 Å** |

  `3JF` is `N-acetyl-3-methyl-L-valyl-(4R)-4-hydroxy-N-[4-(4-methyl-1,3-thiazol…]` — the canonical VH032
  hydroxyproline + methylthiazole handle — sitting in the recruiter pocket, **12.35 Å away from Cys77**. The
  covalent compound is `A1IMD`, at **1.84 Å** from the Sγ, i.e. essentially exactly a C–S bond length. **So the
  E3 downselect's VHL row stands, and the attributed fpocket druggability of 0.001 was scored on the wrong
  ligand's site.** *(A useful side-validation: 1.84 Å is what a real covalent adduct measures — which is
  precisely the scale that makes the NR-V04 panel's 28–39 Å at C551 unambiguous rather than borderline.)*
  **BIRC2 is the flagged first recruiter to revisit** at $0 (tier-3 verified, best resolution 1.249 Å, openness
  within 0.04 of CRBN) if CRBN/VHL prove geometrically unpromising — it is already fully staged.
  ⚠ **The downselect is BLIND to recruiter-intrinsic pharmacology by construction.** MDM2 and KEAP1 rank well on
  geometry while their handles are developed inhibitors of the E3's *own* function. Recorded as a **required
  input to the next gate** — a recruiter must not be committed to on geometry alone.
- **(d) Pose-marginalisation, free** — run the basin search over the warhead-**pose ensemble** and carry only
  basins that persist, reporting the surviving fraction. Sequence-level uniqueness of C397/K572 is
  pose-independent; only the *reach* estimate is conditional, which is a far smaller conditional surface than the
  stage currently carries.

Five load-bearing pieces:

1. **A paralogue-differential surface atlas (free, CPU).** NR4A1/2/3 in a **matched** ensemble — homologous
   frames, identical pose hypotheses, protonation, target–E3 transforms, and sampling — mapping E3-reachable,
   solvent-exposed, divergent residues and lysines (LBD / hinge / DBD / fusion partner, separately). Output is a
   discrimination **map**, not three receptor models; states are explicit scenarios unless populations are
   defensibly estimable. **Done** (RUNG 4).
2. **Orientation-space search before real linkers.** For each ligase, sample many relative transforms of
   VHL/CRBN around the warhead-bound target under a flexible linker-reach restraint; keep only interfaces that are
   favorable on NR4A3 and systematically weaker/frustrated on NR4A1/2, bridgeable, clash-free, ensemble-compatible,
   and place an accessible lysine in a productive transfer region. Cluster into **~3–8 basins per ligase**.
3. **Wedges proven by a matched-pair causal cycle — the primary causal test.**
   **PRIMARY: the LIGAND-side double difference, on the lane Val B calibrates.** For a candidate *d* and a
   matched control *d₀* differing only in the element that engages the wedge,
   `S = ΔΔG_coop(d₀→d | NR4A3) − ΔΔG_coop(d₀→d | NR4A1)`. Each term is an ordinary relative alchemical quantity
   *inside one protein*; the difference asks the **design** question — does this structural element create
   paralogue discrimination? It needs **no protein-mutation engine**, makes **no cross-lane subtraction**, and by
   the cancellation identity (cost lever 2) needs **only ternary legs**. This is far stronger than observing
   ΔG_ternary,3 < ΔG_ternary,1.
   **CONFIRMATORY: the reciprocal PROTEIN-mutation cycle.** For a target-surface mutation *m*,
   `ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary` (the binary leg subtracts mutation effects from the
   target–warhead complex, isolating the recruited-interface effect). A strong wedge shows a favorable NR4A3
   interface, **loss** on NR4A3→NR4A1/2 mutations, **partial gain** on reciprocal NR4A1/2→NR4A3 mutations,
   persistence across frames, and a recognizable steric/electrostatic/H-bond mechanism. Its engine is built and
   its known-answer benchmark **passed 2026-07-25** (RUNG 5a-KS). ⚠ **BUT IT IS NOT AN INDEPENDENT SECOND
   LINE — corrected 2026-07-30, see [Open decisions 10](#open-decisions).** `ΔG_mut^ternary − ΔG_mut^binary`
   is a **ternary-minus-binary contrast, the same shape as the quantity valB_mini failed on**, and its
   benchmark passed on a *protein-mutation* quantity rather than on that shape. Retained as a second line —
   but the paper's headline causal result is not hostage to it. **ADOPTED 2026-07-24 (trimcrae go).**
4. **Separate ACCESSIBILITY from STABILITY.** Estimate `P(B_k | d, s)` (can the linker reach and hold basin *k*?)
   separately from `ΔG_coop(d, B_k, s)` (is the orientation plausible?). A favorable basin the linker rarely
   accesses is irrelevant.
5. **Robust constraint-satisfaction selection.** A candidate advances only if it satisfies preregistered
   constraints across a required fraction of scenarios (binary non-destabilization; basin populated in replicated
   MD; NR4A3 advantage over **both** paralogues under perturbation; ≥1 NR4A3-specific contact survives
   counterfactual mutation; ubiquitin near an accessible NR4A3 lysine in a meaningful CRL-conformer fraction;
   credible unstrained linker). Rank by `P_d = P(all constraints hold)`, robust to dropping any one favorable
   scenario — this kills the best-of-N winner's-curse artifact a raw Pareto set still admits.

### The hard kill-switch — tiered, cheapest-decisive-first

No causally-confirmed NR4A3 wedge ⇒ **STOP**: no linker matrix, no ensemble refinement, no flagship spend;
publish *"we mapped orientation space and no robust NR4A3-discriminating, ubiquitination-compatible basin
survives causal testing."* The *decision* to commit the flagship is cheap, not a gate on the whole tail.

> **★★ CRITICAL SEMANTICS, ADDED 2026-07-25 BEFORE 5a-KS EVER RUNS — A NULL AT TIER 3 DOES *NOT* STOP THE
> PROGRAM, AND THE ROW BELOW USED TO SAY IT DID.** Tier 2's GO was won on the **CATEGORICAL** basis: the
> paralogues have **no nucleophile at the aligned position**, so a covalent bond *cannot form* on them at all.
> But Tier 3's `S` is a **NON-COVALENT** double difference — it models no bond in either leg, so it can only
> ever see the **pre-covalent complex**. **It is therefore structurally incapable of testing the categorical
> mechanism.** What `S` tests is the **MARGINAL** (induced-interface, thermodynamic) wedge — the axis this file
> **previously** described as *"a confirmation tool operating near its limit, not a discovery tool"* — a
> characterisation that **no longer** stands and is **superseded** by measurement ([Appendix
> A](#appendix-a--superseded-numbers-and-retracted-claims) 53); §MECHANISM-FIRST carries the current reading and
> this box does not restate it.
> **So: `S` ≈ 0 ⇒ the MARGINAL wedge is absent, and the claim rests on the CATEGORICAL axis alone. STOP only if
> the categorical axis has ALSO failed.** Writing this down *before* the run is deliberate — a null is a
> **plausible** outcome for the recommended pair (its expected NR4A3 gain is bounded by roughly one partly
> buried H-bond, ~0.5–1.5 kcal/mol), and a pre-registered reading is the only thing
> that stops a predictable null being read after the fact as a verdict on the whole program.
>
> ⚠ **AMENDED 2026-07-30 8:21 PM ET — THE DECISION RULE ABOVE IS UNTOUCHED; ONE SUPPORTING FIGURE IT QUOTED IS
> SUPERSEDED, AND THE CHANGE MAKES A NULL *MORE* INFORMATIVE, NOT LESS.** The box was written against a
> best-case resolvable difference that was **assumed**, and against which the pair's own expected effect sat
> *below* resolution — so a null could not be told apart from a wedge the method simply could not see, and
> "likely" above was doing double duty for both. On the **measured** replicate SD the resolvable difference is
> the figure now carried in §MECHANISM-FIRST, and the pair's expected effect straddles it instead of sitting
> under it. **Consequence, and it is the whole reason this note exists: at an adequate replicate count a null
> now BOUNDS the marginal wedge rather than merely failing to find one** — which is what turns the pre-registered
> reading from an excuse into a result. It also makes the replicate count a *design* question rather than a
> formality; [§Open decisions 11](#open-decisions) is where that is settled. Nothing here loosens the STOP
> condition, and nothing here was changed after seeing an `S` — **no `S` has been computed.**

| tier | test | cost | status |
|---|---|---|---|
| **0** | **Categorical-axis screen.** No paralogue-unique nucleophile within tether range AND no paralogue-unique exposed lysine ⇒ selectivity must come from the marginal axis alone, which sits at the method's resolution limit ⇒ say so and expect a negative | **$0 CPU** | **PASSED — GO on both axes** (C397 at 10.9 Å exit-vector reach; K572/K518/K592 exposed). ⚠ **NARROWED 2026-07-26: "structurally incapable" holds AT THE ALIGNED POSITION only** — 16 of NR4A3's 20 cysteines are shared, each paralogue presents **two** inside the 12-atom gate (NR4A1 C465 at **6** atoms), and the axis survives on **exposure**, not absence. Clean at 12 atoms; P(paralogue collision) rises to **0.081 at 16** and **0.258 at 20**. See §MECHANISM-FIRST |
| **1** | **Differential surface atlas.** No E3-reachable divergent surface ⇒ STOP for free | **$0 CPU** | **PASSED** (46 handles) |
| **2** | **Basin nomination.** No basin exploits a categorical handle *and* none even nominally discriminates NR4A3 ⇒ STOP cheaply | **$0 realized** (budget was $0–50; **no GPU used**) | **✅ GO — CONFIRMED on the full 12-pose run** (CI 30169233690, 55 min, 3:11 PM ET). Basis **CATEGORICAL**. 58 meta-basins / 192 basins; **7** exploit term (a), **40** term (b), **28** nominally discriminating. See the block below |
| **3** | **Pilot ONE causal direction** — the ligand-side double difference `S`, one matched pair, ternary legs in NR4A3 and NR4A1. ⚠ **`S` is NON-COVALENT, so it tests the MARGINAL wedge only. No discrimination ⇒ the marginal wedge is absent and the claim rests on the CATEGORICAL axis alone — STOP only if the categorical axis has ALSO failed** (see the box above; a null is the *likely* outcome for the recommended pair) | **~$12 ($1.6–45)** | pending (RUNG 5a-KS) — **matched pair now DESIGNED**, see RUNG 5b |

Tier 2's asymmetry is what makes it usable: cheap scoring has poor S/N for a ~1 kcal/mol *energy* difference, so
it only **nominates** — but "does this basin place an electrophile at C397 / cover K572?" is a **geometric**
set-membership question, which cheap scoring answers reliably. A gross absence of signal is an informative
NO-GO; it is not trusted to kill a real small wedge.

### ★ Tier-2 result in full — the 12-pose run, at its CORRECTED exact-kernel values (LANE 2, 2026-07-25; reach correction 2026-07-26; **$0 realized — no GPU**)

**GO, basis CATEGORICAL — and "weakly" is part of the verdict, not a hedge to drop when quoting it.**

**★ THE FULL RUN CONFIRMED THE GATE AND CHANGED THE HEADLINE. Both must be reported.** The definitive run
(10⁶ placements × **12** poses × VHL+CRBN) gives **58 meta-basins / 192 basins**, of which **3** exploit
term (a), **40** term (b), and **28** discriminate nominally. Every figure below is the **corrected
exact-kernel** reading, i.e. post-2026-07-26 — ⚠ **this block carried the pre-correction table live for four
days, with its own correction stated 50 lines further down, and the manuscript copied the stale values out of
it. Superseded numbers are in [Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 49 and are
NOT restated here.**

| meta-basin | poses | C397 reach (exact) | at-gate reach fraction | term (b) vs background | paralogue zones bare |
|---|---|---|---|---|---|
| `vhl|M2` | 6/12 = 0.50 | **10 atoms** (shortest) | **0.057** | 1.43×, exceeds | 0.008 |
| `vhl|M3` | 9/12 = 0.75 | 11 atoms | 0.021 | 1.4×, exceeds | **0.0** |
| `crbn|M17` | 3/12 = 0.25 | 12 atoms *(at the gate)* | 0.045 | **3.87×**, exceeds | — |
| **`crbn|M0`** ← strongest **nomination** | **11/12 = 0.92** | 13 atoms — **MISSES the gate by one** | **0.000** | **7.5×**, exceeds | 0.032 |
| `vhl|M14` | 3/12 = 0.25 | — | 0.000 | **does NOT exceed** | 0.0 |

**Three things this table says.**
1. **All 3 term-(a) basins reach C397 — and only C397.** Shortest reach per residue across the whole run is
   **C397 10 · C420 16 · C559 27**, so at a 12-atom gate the other two are not near-misses.
   **The categorical chemistry axis rests on a single residue.**
2. **★ THE STRONGEST BASIN AND THE GATE-CLEARING BASINS ARE NOT THE SAME BASINS, and that separation IS the
   result.** `crbn|M0` leads on pose persistence (0.92) and on the *lysine* term (7.5× over background, so it
   is not merely riding CRBN's null) — but under the exact kernel its shortest C397 requirement is **13**
   atoms, so it does not clear the electrophile gate at all. Tier 2 passes CATEGORICAL because `vhl|M2`,
   `vhl|M3` and `crbn|M17` clear it, **not** because the leading basin does. Anyone quoting `crbn|M0` as a
   term-(a) basin is quoting the superseded run.
3. **Reach fractions are 0.021–0.057**, i.e. an electrophile reaches C397 in only **2–6 %** of a basin's
   placements. This is the quantitative form of "weakly", and it is why the gate **nominates** rather than decides.

*Reconciliation note, checked rather than assumed:* `best_linker_atoms` reads **19** on every meta-basin while
the term-(a) gate is 12, which looks like a contradiction and is not — `best_linker_atoms` is the linker length
that best supports **basin accessibility** (`P(B_k | d, s)`), whereas the gate counts
`term_a_union[cys].max_fraction_reachable_at_gate`, whether an **electrophile** reaches that cysteine within 12
atoms. Two different quantities; the 3 reconciles exactly against the gate block.

Per arm, from the same definitive run (rows sum to the 58 / 3 / 40 above, which is how they are checked):

| | VHL *(Lane 1 staged it only as a **sensitivity control**)* | CRBN *(Pareto front)* |
|---|---|---|
| meta-basins | 28 | 30 |
| exploiting **term (a)** at the 12-atom gate | **2** (`vhl\|M2`, `vhl\|M3`) | **1** (`crbn\|M17`) |
| shortest C397 linker (exact) | **10 atoms** | 12 atoms |
| exploiting **term (b)** above the null | 21 | 19 |
| enrichment over null | 1.06–7.37× | 1.07–8.0× |
| null: covers *any* NR4A3 lysine | 0.31–0.48 | 0.77–0.95 |

- **The categorical terms fire in a small MINORITY of placements** — 0.5–8 % cover a unique lysine, term (a)
  reaches gate level in 2–6 % — against the gate's **unique-lysine null of 1.0–7.5 %** (`term_b_background_null.fraction_unique_covering`, 24 arm×pose nulls). **Enrichments, not saturation.** ⚠ *Do not pair one range with both terms — the reach control is a different quantity, and is zero in 184/192 basins.*
- ⚠ **RETRACTED SAME DAY (2026-07-25, LANE 7): "CRBN's null is 0.81–0.96, so most of CRBN's term-(b) signal is
  background — the discrimination lives on VHL."** That inference was wrong **twice over**, and it was recorded
  here earlier today, so it is corrected rather than quietly dropped.
  **(i) Wrong quantity.** 0.81–0.96 is the **any-lysine** null, whereas term (b)'s signal is an enrichment over
  the **unique-lysine** null. The conclusion was drawn from a different denominator than the one the gate uses.
  **(ii) The 0.81–0.96 is itself an EXIT-VECTOR ARTIFACT.** Restaged **assembly-native** (8R5H / 9UUM, every
  bridge **0.0 Å**) and re-run twice at identical settings, CRBN's any-lysine null **halves, 0.858 → 0.399**,
  while VHL's does not move (0.419 → 0.437). The change tracks the manipulated variable and nothing else —
  CRBN's exit vector moved **16.5 Å** between constructions, VHL's only **0.99 Å**.
  **What survives:** the **gate's actual denominator barely moves** (`fraction_unique_covering` 0.040 → 0.035 on
  CRBN, 0.027 → 0.026 on VHL), so **the Tier-2 GO and its published enrichments are UNAFFECTED**, and Tier-2
  passes CATEGORICAL on **both** constructions (native marginally stronger: 3 vs 2 term-(a), 26 vs 22
  discriminating). **What falls is only the claim that the discrimination lives on VHL.** Do not repeat it.
- ⚠ **Term (b)'s discrimination is a RARE JOINT EVENT, not paralogue lysine scarcity (Lane 13, $0).**
  P(the transfer zone covers *any* lysine) is **NR4A3 0.438 / NR4A1 0.387 / NR4A2 0.363** — i.e. essentially
  **non-discriminating on the any-lysine measure**, consistent with the committed 0.0–0.032 *joint* statistic.
  The term earns its signal from the coincidence of covering a *unique* lysine while both paralogue zones stay
  bare, not from the paralogues having fewer lysines to hit. State it that way; the scarcity reading is wrong.
- **`term_b_best_rank` is a best-of-N statistic, inflated by construction** (exactly piece 5's winner's-curse
  artifact), so those counts are **upper bounds**; the unbiased mean fractions lead. One CRBN basin reached
  rank 4 while scoring *below* background and was correctly excluded — **without the null it would have counted.**
- **Shortest gate-clearing nomination `vhl|M2`:** 6/12 poses, C397 reachable at a **10-atom** linker (the
  shortest anywhere in the run), term-(b) enrichment 1.43× with a unique lysine covered and *both* paralogue
  zones bare at 0.008, and its interface patch (UniProt 390–412 + **572**) sits *around K572 itself*.
  **`vhl|M0` survives 5/12 poses** despite a **negative nominal Δ** — under mechanism-first that does not
  disqualify it, and **a scalar score would have hidden it**, which is the clearest vindication yet of
  dropping the tunable scalar; note it does **not** clear the electrophile gate (C397 at 19 atoms). ⚠ *The
  6-pose preview's "`vhl|M2` 5/6" and "`vhl|M0` 6/6 with C397 at 9 atoms" are superseded by the 12-pose run
  and must not be quoted ([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 49).*
- **Pose-marginalisation on the 12-pose run:** top CRBN meta-basin **11/12 = 0.92** (`crbn|M0`); top VHL
  **9/12 = 0.75** (`vhl|M3`); the rest spread down to 0.25.
- **★ LINKER TRACTABILITY, ADDED BY RUNG 5b (2026-07-25) — and it does NOT invert the ranking, though a first
  pass said it did.** `min_linker_atoms` is a **best-of-N** over a basin's placements, and the member achieving
  it is **not** the published representative. Measured at the *representative*, C397 needs 14–25 atoms and
  `crbn|M0` looked the least buildable — an apparent inversion of the basin ranking. Re-run with the
  achieving placement emitted explicitly (`exemplar_placement`, $0, 71.6 min), the addition is **purely
  additive to the gate**: it reproduced the counts standing at the time exactly, and the electrophile term
  moved later and separately, in the reach correction below. Exact-kernel figures, at the search's own 3.0 Å
  pendant convention:

  | basin | C397 atoms, representative → exemplar | comfortable length |
  |---|---|---|
  | **`crbn\|M0`** | 33 → **13** | **~15 atoms** (1.1 kT) |
  | `vhl\|M3` | 23 → 11 | ~13–15 |
  | `vhl\|M2` | 16 → 10 | ~12–14 |

  **So the inversion was an artifact of comparing a best-of-N length against a typical placement** — correcting
  it leaves `crbn|M0` **comparable** to the others rather than an outlier. ⚠ It does **not** make it the most
  tractable, and the earlier reading "the strongest basin is among the MOST tractable" is withdrawn
  ([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 49), along with the pre-correction
  25 → 11 / 14 → 11 / 15 → 10 row values. Both placements are emitted — exemplar (optimistic), representative
  (typical) — and **neither may be quoted without saying which, nor without its pendant convention**: at the
  longest pendant in the sweep `crbn|M0`'s representative reads 25 rather than 33.
- ✅ **CORRECTED 2026-07-26 (LANE 10) — the C397 reach figures are no longer lower bounds.** They previously
  were, by up to ~5 atoms: RUNG 5a's reach rule credited the pendant with shortening the **span**, which no
  pendant can do (all 576 records were audited and none was internally impossible, so it was a bound, not an
  error). The exact three-ball kernel has since replaced it and every figure was recomputed on the matched
  **10⁶** run. **The correction moved term (a) 7 → 3 and left term (b) 40 and the nominal limb 28
  bit-identical** — the values and the gate verdict are stated once, in the §WHERE WE ARE "the covalent design
  route clears the gate" block above. Quote them from there, not as bounds. ⚠ **This bullet sat 50 lines below
  a table still printing the pre-correction values, and the manuscript copied that table rather than this
  bullet** — a correction is not delivered until the live text above it stops disagreeing with it (rule 2).
  Both are now current; the superseded set is [Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 49.
- ⚠ **`best_linker_atoms = 19` on 188/192 basins is the scan's LAST GRID POINT**, not an optimum. Do not read it
  as a converged optimum in either direction.
- **Exit vectors never let the linker run taut** — α = 33–100°, costing 1–3 backbone atoms of detour at minimum.
- **Term (b) is NOT EVALUABLE for BIRC2/MDM2** — their ligandable structures are 15 %/19 % fragments lacking the
  RING. This agrees with Lane 1's CRBN+VHL answer by a different route, and argues for adding
  **ubiquitination-geometry evaluability as an explicit Pareto axis** rather than discovering it downstream.
- **MM-GBSA rescore: NOT run, and recommended against** — it would refine the very axis the mechanism-first
  reframe demoted. **Next spend should be 5a-KS.**
- **✅ RESOLVED 2026-07-25 (LANE 7) — registry A (5T35) is CORRECT, and the Tier-2 result rests on it.** The
  discriminating observation nobody had run: **8R5H** is a solved, *intact* CRL2^VHL ubiquitylation assembly
  holding VHL·EloB·EloC, MZ1 **and** a trapped UBE2R2~Ub **in one frame** — so the disputed distance is
  measurable with **no bridge, no composition, no model**. **Ground truth: exit atom `759.CAE` → UBE2R2
  catalytic Cys93 = 30.76 Å.** Registry A reproduces it at **30.85 Å (miss 0.09 Å)**; registry B (6GMN) gives
  **69.91 Å (miss 39.15 Å)**. Decomposed: Δ mapped E2 cysteine **0.02 Å**, Δ exit vector **50.67 Å** — so the
  disagreement is entirely in the *exit vector*, not the anchor.
  **Root cause, read off the structure:** 6GMN's chosen "recruiter ligand" (F4E) has a 4.5 Å lining of **eight
  Elongin C residues and ZERO VHL residues**, 6.87 Å from the nearest VHL atom. `pick_ligand` tested contact
  against the receptor **body** (recruiter + obligate partners) and **never against the recruiter itself**.
  Fixed and unit-tested; **verified bit-identical** on both consumed arms (5T35 MZ1 2.57 Å, 6BOY dBET6 2.69 Å).
  **⚠ And the tempting explanation was FALSIFIED:** this is **not** a second instance of the 48.6 Å composed-RING
  spread — 8R5H is single-copy and the mapped E2 cysteine agrees to 0.02 Å. **The numeric similarity to 48.6 Å
  was coincidence.** *(Consequence: the feared "~40 Å of transfer-zone variation would weaken term (b) further"
  does not exist, and the VHL basin ranking is unchanged.)*

---

## Spending rules

*★ **APPENDIX — the spending rules.** Four rules, zero history. The [roadmap](research/manuscripts/nr4a3-program-map.md) §11 links here and restates nothing. Rule 4 is why the roadmap's price column distinguishes priced / PROJECTED / **unpriced**.*

1. **No pre-authorization, no pre-staging.** Nothing is ever queued to auto-fire. Every GPU run is presented at
   its gate with (a) the prior step's result, (b) a pinned cost (from realized GPU-h, not a guess), and (c) a wait
   for an explicit trimcrae "go." Only $0 CPU/CI work runs without a nod.
2. **Spend-gated ladder, cheapest-decisive-first.** The cheapest run that could kill the paper comes first; each
   rung's bigger spend unlocks only if the previous, cheaper rung looks promising. Never pay for an expensive
   stage on a hypothesis a cheap stage could have falsified.
3. **GO/NO-GO after every priced rung.** Each rung ends with an explicit test; NO-GO = stop or pivot.
4. **Every step is priced bottom-up per edge** on the Vast-4090 bases below; provenance in
   [pricing.md](research/compute/pricing.md). A step whose engine has no completed benchmark leg is carried as
   **PROJECTED and excluded from the pinned total**, never at a fake number.

## GPU economics (full provenance in [pricing.md](research/compute/pricing.md))

*★ **APPENDIX — GPU economics.** ⚠ Largely a **pointer**: the throughput table's home is `vast_cost_model.MEASURED_NS_PER_DAY_84K`, the bid rule's is `bid-strategy.md §7`, the per-edge bases' is `pricing.md`. What genuinely lives here is the **six cost levers**, which are ratios and survive any reprice.*

**All production runs go on Vast.** GCP L4 / SageMaker / Modal are not the go-forward basis. **The card is not
the decision — the OFFER is.** Rank live offers by all-in **`$/ns`** (bid + storage ÷ measured throughput) and
take whatever wins; the top 10 routinely contain both 4090s and 3090s. Measured throughput @84,534 particles is
**4090 804.06 / 4080 693.35 / 3090 460.91 ns/day** (4090/3090 = **1.745×**) — table of record
`vast_cost_model.MEASURED_NS_PER_DAY_84K`, re-anchored 2026-07-27 onto a median over N≥3 independent hosts
(pricing.md → Appendix T). The cheapest 3090 floor was **$0.0147/hr** against **$0.1310** for the cheapest 4090
— an **8.8×** price spread that more than covers the throughput gap. VRAM is never the constraint (≥24 GB is
ample). A 3090 does need **1.745×** the wall clock, so a leg with a hard continuity requirement is
proportionally more exposed on it — scaled and flagged per card, not ignored.
*(Superseded, retained: the single-host figures **4090 755.36 / 4080 703.51 / 3090 359.36** and the
**2.10×** ratio derived from them. Appendix T says what retired them.)*

- **★ PLANNING RATE: $0.137 per reference (4090) GPU-hour** — best-10-offer mean on the live board; range
  $0.057 (best offer) to $0.309 (median). Against the **$0.35–0.39/hr `step1_fanout` actually paid**, that is
  **2.6–2.8×**. Best-to-median spread is **5.43×**, so *selection* is the dominant lever — worth several times
  the bid policy.
- **Bid = the market floor plus a staleness tick** (`min_bid × 1.02`, min +$0.0005), **capped at that machine's
  on-demand price**, never at or below the floor. Measured 2026-07-25 by renting one offer at three bid
  multiples: **`charged = min(your bid, the machine's on-demand price)`** — so a premium is paid on *every*
  hour and cannot buy safety from on-demand renters. Retention is bought with **checkpoint frequency**, which is
  free. Every multiplier this repo has used (`×1.1`, `×1.5`, `×1.9`, `×1.25`) is retired; derivation, the
  measured bid ladder, and what retired each one are in
  [bid-strategy.md](research/compute/bid-strategy.md). `VAST_BID_FLOOR_MULT` survives only as an unset escape
  hatch for a leg that genuinely cannot be paused.
- **Storage is a real line, not a rounding error** — ~$0.011/hr at the 40 GB the launcher requests, which on the
  *best* offer is 42 % of all-in cost. Ask for the disk the job needs.
- **On a `resources_unavailable` refusal, pick another host — do not wait it out.** Vast is a market of ~23
  independently-priced machines you can see at once, not a pool; the floor is flat day-to-day, so a different
  host today costs what this one will cost tomorrow. `protfep_vast_launch.collect` records and destroys the
  machine and `ResourceSpec.exclude_machine_ids` keeps selection off it — a host that never starts has infinite
  realised $/ns, which the ranking cannot otherwise see.

### Per-edge bases — one extrapolated, one rate-measured, one converted

**None is a completed end-to-end edge on a 4090.** That caveat is the reason every stage cost below is a
bottom-up estimate rather than a total.

| basis | value | how it was obtained |
|---|---|---|
| **RBFE binary edge** (complex+solvent, ~35k atoms) | **~13.7 ref GPU-h ≈ ~$1.9** | Live-diagnosed per-iteration rate on the **real cmpd19/NR4A3** complex — 12.76 / 13.70 / 14.42 s/iter on three independent Vast 4090 hosts (16 samples each) — × the hardcoded 2400-iteration leg. A clean end-to-end ΔG was **not** captured (both spot instances preempted), so this is an extrapolated rate, not a completed-edge measurement |
| **Ternary cooperativity edge** (3 replicas, ~146k particles, 12 windows) | **~$8.8 ($3.2–22)**, 56–72 ref GPU-h | Rate **measured directly on a Vast 4090** (firm leg via `run_ternary_leg.sh`, self-staged 8G1Q, 146,284 particles): warmup clean, production steady at **~14–18 s/iter (median ~16)**. Leg length **confirmed at 2400 iterations** (400 equil + 2000 production at 2.5 ps/iter, `nr4a3_ternary_fep.py:343-344`) — and now *observed*: valB_mini's ternary seed 0 reached **2000/2000** production iterations. 2400 × 16 s ≈ **~10.7 GPU-h/leg** × 2 legs × 3 replicas ≈ **~64 GPU-h/edge** |
| **Endpoint-MD leg** (~466k atoms) | **~$0.19**, ~1.38 ref GPU-h | Backed out of the **completed** 18-leg NR-V04 covalent panel: ~$0.43/leg realized on a 3090 at ~$0.10–0.21/hr ÷ the card ratio *(computed with the then-current **2.102×**, superseded 2026-07-27 — pricing.md Appendix T; the conversion is due a refresh at the next reprice)*. The one basis resting on a completed multi-leg ledger; the 4090 conversion itself is inferred |

**Two live transferability warnings.** (i) The ternary rate was measured on the **SMARCA2/VHL 8G1Q** assembly
and is being used to price **NR4A** ternaries — the *same* move that cost 2.6× on the binary lane when the real
cmpd19/NR4A3 complex turned out to sample at ~13.6 s/iter against TYK2's ~5.2. Expect an NR4A ternary leg to be
heavier, not lighter; time one before treating these rows as firm. (ii) The **L4→4090 card ratio is validated at
~2.06×** (33 → 16 s/iter) — a ratio of rates is count-independent, so that conclusion is solid.

**Provider reality check.** The ladder is *priced* in Vast-4090 dollars, but `valB_mini` is *actually running* on
**GCP L4 on-demand**, a lane pricing.md bills at ~$94/edge. That is a deliberate use of the **expiring GCP free
trial** (~$292 left of $300, window closes **2026-10-10**; Modal's $30/mo is already $27.54 spent and does not
carry over) — free credit beats cheap cash, and it buys ≈3 ternary edges, not the ladder. But it means
**realized spend and ladder spend are two different ledgers**: `credit-status.json` records GCP `spent: 8.0`
from a **manual** source not yet reconciled against the ~8 dispatched L4 legs. Track GCP burn separately, and do
not let "we spent ~$2 so far" imply the L4 lane was free.

### Cost levers adopted 2026-07-24 ([evidence](research/manuscripts/nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md))

1. **~~4 fs ternary production ≈ 2× cheaper per leg.~~ ⚠ CORRECTED 2026-07-25 — the saving is **1.56×**, not
   2×, and the leg is **2800 iterations**, not 2400. Both verified against `rbfe_spot_driver` source, both pure
   arithmetic on the existing measured rate.**
   - **Why not 2×:** halving the timestep halves the force evaluations only in the phase whose dt *changed*.
     The warmup is pinned at **1 fs either way**. Per replica: 2 fs = 1.0e6 (warmup) + 2.5e6 (production)
     = **3.5e6 steps**; 4 fs = 1.0e6 + 1.25e6 = **2.25e6**. Ratio **0.643×** ⇒ a **1.56×** saving. The old
     "2×" overstated it by ~36 %.
   - **Why 2800, not 2400:** "400 equil + 2000 production at 2.5 ps/iter" assumes the warmup runs at the
     *production* timestep. It does not — `_iters_from_time` derives warmup iterations from the **WARMUP**
     integrator, and the source comment says so outright (*"more iters at a smaller dt"*). At the as-run
     `warmup_timestep_fs=1.0`, 1 ns of equilibration is 1e6 steps ÷ 1250 steps-per-iteration = **800**
     iterations, each costing the **same 1250 force evaluations** as a production iteration. So the as-run 2 fs
     leg is **2800 equal-cost iterations**, and pricing it at 2400 understated **every 2 fs ternary stage by
     ~17 %**.
   - **⚠ The claim "iterations are timestep-independent (2.5 ps/iter)" is FALSE and is retired.** Iterations are
     `steps ÷ steps_per_iteration`, and steps depend on dt; 2.5 ps/iter holds only *at 2 fs*. **Price in STEPS,
     not iterations** — iteration counts are not comparable across protocols.
   - Net effect on the edge: **~$8.8 → ~$10.2 at 2 fs**, and the 4 fs edge is **~$6.6, not ~$4.4**.
   **The as-run lane is 1 fs warmup → 2 fs production**, verified against the live VM, not the doc (GH run
   30123894814 `mode=tail` on VM `gcp-ternary-30112102294`: `[tfep] timestep=2.0 fs`,
   `warmup_dt_override="WARMUP timestep overridden to 1.0 fs"`, `NaN_seen=no`; `gpu-ternary-fep-gcp.yml` defaults
   `timestep_fs: 2.0`, `use_preequil: 0`). The "4 fs" people remember is the runbook §1c *pre-equilibration
   demonstration* — after plain-MD pre-equilibration the calib leg ran warmup 48/48 @1 fs → production 40/40
   @4 fs, zero NaN, ΔG_morph 47.28 ± 0.53, where every prior attempt died at warmup iteration 1 — i.e. 40
   production iterations, not 2000, and it held **only because** pre-equilibration was on. Settling step: RUNG 2b.
2. **The binary and solvent legs cancel EXACTLY in any paralogue comparison — up to 2×.**
   `nr4a3_ternary_fep.py` defines `binary_<e3>` as **E3 machinery + PROTAC with NO target**, and solvent as
   ligand-in-water. Both are **paralogue-independent**, so for any morph
   `ΔΔG_coop(P) − ΔΔG_coop(P′) = ΔG_ternary,P − ΔG_ternary,P′` **exactly.** A 3-paralogue comparison therefore
   needs **3 ternary legs + 1 shared binary + 1 shared solvent — NOT 3 edges** (18 legs vs 12, −33 %; 9 if only
   the selectivity contrast is needed, −50 %). **Never price a paralogue panel as N edges again.** And the
   saving is *larger* than the leg count suggests: the `binary_vhl` leg ran at **~28.6–38.2 s/iter (median ≈33)**
   on L4, the *same* rate as the ternary leg — a shared binary leg is a full-price leg paid for once instead of
   N times.
3. **~~Sequential (anytime-valid) stopping instead of a fixed 3 replicas — ~20–25 %.~~ ⚠ REFUTED BY MEASUREMENT
   2026-07-25 — it saves ~0.8–2.6 % on THIS ladder, and should NOT be wired.** `adaptive_certify.py` /
   `adaptive_allocator.py` are built and unit-tested but were never wired to the ternary ladder, and the
   ~20–25 % was an allocation-design figure that was never checked against this ladder's actual shape. Measured
   as a futility stop (`valb_rescope_design.py`): at σ = 0.5 it stops after **4.87 of 5** replicates (**2.6 %**);
   at σ = 0.7, **4.96 of 5** (**0.8 %**). **Mechanism, not a fitting artifact:** an anytime-valid bound must be
   wide enough to remain valid under *every* stopping time, so at n = 2–4 with σ ≈ 0.7 it is simply never tight
   enough to fire. The saving is real for long horizons; **a 5-replicate ladder is too short to pay for it.**
   Do not carry the 20–25 % in any total.
4. **Free gates lead.** `selectivity_wedge_confirm` depended on `valB_full` + `nrv04_retrospective` (~$43) even
   though its validation need is matched-pair, not cooperativity-cube. Decoupled.
5. **Ligand-side double difference replaces the protein-mutation campaign** as the primary causal test — which
   at the time had no engine at all, and still has no NR4A-scale rate.
6. **E3 breadth is free at search, capped before GPU** (≤2 recruiters, dropped set logged).

*Operational Vast setup — image `triskit23/nr4a3fep:latest` (openfe ≥1.12 + ambertools + lomap/kartograf +
OpenMM pinned to CUDA 12.6), the `probe_offers` / `bench` / `firm` tooling in
[`nrv04_vast_launch.py`](research/modalities/nrv04_vast_launch.py), and the bid/ranking code of record in
[`gpu_backend.py`](research/modalities/gpu_backend.py) + `vast_cost_model.recommended_bid` — is documented in
[pricing.md §E](research/compute/pricing.md); not repeated here. The hourly read-only price sampler is
`.github/workflows/vast-price-sample.yml`.*

---

## THE ORDERED PLAN (spend-gated) — read top-to-bottom for "what's next"

*★ **APPENDIX — the item layer, and the most fragile object in the repo.** ⚠ **Parsed by [`work_ledger.scan_plan_items`](research/modalities/work_ledger.py)** on this heading string, the bullet regex and the `###` rung sub-headings; the skipped marker is an **en dash**, not a hyphen. Renaming the heading makes the plan invisible with no error; reformatting a bullet makes an open item vanish from the work board. `degrader-paper-schedule.json` is its declared one-for-one machine mirror. The [roadmap](research/manuscripts/nr4a3-program-map.md) §10 presents this layer and links to it; it never restates a price.*

Legend: `[ ]` pending · `[~]` in progress · `[x]` done · `[–]` skipped · `[!]` result under correction.
**Price** = spot $ for that step on Vast 4090; **Cum.** = running total if GO at every gate to here (mid-range).

### RUNG 0 — free / already done (~$0)

- **`[x]` Charge-model fix — am1bcc on the BINARY path** — **$0.** Added `ambertools>=23` +
  `partial_charge_method="am1bcc"`; the **binary RBFE lane** is on the documented reference method → cite OpenFE.
  The ternary and endpoint-MD lanes run NAGL — a *lane split*, not a shared charge model (see §Val A above).
- **`[x]` Step 0 — RBFE infra shakeout** — **~$1–2 · PASSED.** One OpenFE edge ran end-to-end via the spot-safe
  split and returned a converged **ΔG_morph = −48.75 ± 0.57 kcal/mol** (MBAR); am1bcc charging and the
  warmup→production→commit/restore driver are GPU-validated. **GO.**
- **`[x]` EMC E3-ligase expression** — **$0.** All 10 components of both CRL2^VHL and CRL4^CRBN are broadly
  expressed (HPA), so the VHL-vs-CRBN choice is **not** constrained by machinery availability — decide on
  geometry/selectivity. (No EMC line in HPA — general mesenchymal availability.)
- **`[x]` Pocket-tracking re-analysis** — **$0.** Harmonized detection folded into the paper's Gate-2 wording:
  8XTT **19/20 frames detected, 3 ≥ D\*=0.53** (= 3/19 among detected, 3/20 across all deposited); release
  continuations druggable in 56/40/80 % of frames per replica, **44/75 = 59 % pooled**
  (`nr4a3-pocket-reharmonize-summary.json`).

### RUNG 1 — reference-reproduction smoke (mostly a citation)

- **`[x]` Validation A-mini — build-consistency smoke + cite OpenFE** — **~$0 · Cum. ~$2 · PASS/GO.** The public
  TYK2 `ejm31→ejm42` edge (both legs, 5 ns × 12 windows) gave **ΔΔG_bind = +0.366 vs exp −0.24 → abs err 0.61
  kcal/mol**, inside the 2.0 tolerance. Our container reproduces a known ΔΔG on the standard am1bcc method → cite
  OpenFE's published ~1.7 kcal/mol accuracy. Does not touch NR4A. **GO to Rung 2.**
  *(Scope: this covers the **am1bcc binary lane only**. The old rider "if am1bcc is ever forced to NAGL, Val A
  reverts to a paid ~$25 NAGL benchmark" has in fact **already fired** — every ternary and endpoint lane runs
  NAGL because sqm cannot charge PROTAC-sized ligands. Resolution: **Val B is the NAGL lane's known-answer
  accuracy control**, already on the ladder. What this costs us is the *citation*: OpenFE's accuracy number may
  not be quoted for any ternary result.)*

### RUNG 2 — cheap precision + cheap probes *(only if Rung 1 = GO)*

- **`[x]` Step 1 pilot — cmpd19 conditional RBFE** — **~$2.8 ($0.8–8.5; 1–2 RBFE edges) · Cum. ~$4.** First edge
  `zaienne_cmpd19 → cw_ev_5nh2` (5-Br→5-NH₂) converged: complex ΔG_morph −29.68 ± 0.24, solvent −31.52 ± 0.26 →
  **ΔΔG_bind = +1.84 kcal/mol** (the 5-NH₂ analogue ~1.8 kcal/mol weaker *in the modeled opened pocket*). Proves
  the congeneric-RBFE pipeline converges on the real NR4A3 system without pocket collapse — the pilot's crux is
  cleared. Reproducibility replicas + pose/state sensitivity are carried forward as **fan-out inputs** (they
  refine per-edge `n_windows` and the conditional caveat, and gate the fleet). This is statistical convergence on
  a *hypothesized* pose, **not** an accuracy claim.

- **`[~]` Validation B-mini — all-binding graded cooperativity edge** — **~$8.8 ($3.2–22) · Cum. ~$13.** The Wurz
  SMARCA2–VHL **cmpd 1→4** all-binding graded edge (α 12.8→2.6 ≈ +0.94 kcal/mol; both endpoints are productive
  binders — the cleanest first calibration). Exercises the bespoke `ΔΔG_coop = ternary − binary` cycle that
  cannot be cited away. **GO/NO-GO (verbatim from the prereg in `degrader-paper-schedule.json`; the
  ±1.0 kcal/mol band was deliberately REMOVED on 2026-07-17 because a separation <1 kcal/mol makes a noisy
  positive point estimate INDETERMINATE — do not re-introduce it):** PASS requires **positive sign + CI excludes
  zero + no fwd/rev disagreement + no collapse/escape/restraint-dominated leg + broad consistency with the
  measured +0.94**. valB_mini gates valB_full only — it does **not** authorize the NR4A matrix; until valB_full
  passes, NR4A ternary scores are **exploratory**. *(The cis-epimer PROTAC-2 edge is demoted to the
  negative-endpoint stress module of the cube below — a pass forced by holding an unstable pose is not a pass.)*

  **As-run protocol** (this is what the cost basis and the paper must describe): `NWIN=12` λ-windows ·
  `CHARGE_METHOD=nagl` · `TIMESTEP_FS=2.0` (warmup 1.0 fs) · `TEMPLATE_PDB=8G1Q` · GCP **L4 on-demand**. Both of
  this lane's deviations — timestep and NAGL-vs-am1bcc — are registered in `md_settings.py`'s docstring. The 2 fs
  step is empirical: the cause of the earlier warmup NaN is the **softcore alchemical region in a large, rough
  homology-built assembly**, there is no static predictor, and the fix that works is **plain-MD
  pre-equilibration** (`ternary_preequil.py`), not a smaller timestep. Authority: `ternary-rbfe-runbook.md`
  §1b/§1c.

  **★ r0 IS IN, IT IS THE WRONG SIGN, AND MORE REPLICATES CANNOT FIX IT (2026-07-25). Full analysis +
  recommendation: [valB-mini-r0-verdict-2026-07-25.md](research/manuscripts/valB-mini-r0-verdict-2026-07-25.md).**
  The first complete cycle (CI 30148463967, re-dumped 30155238348) gives **ΔΔG_coop(r0) = −0.534 kcal/mol**
  against the +0.944 target — wrong sign, 1.478 off, **both of which are r0's own superseded reading and NOT
  the lane's headline** ([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 44 and 51; the
  current values are the n=3 mean −0.599 / abs error 1.543 in the scoreboard) — from legs binary **48.0046** / ternary **47.4701** /
  solvent **47.8060**, i.e. the answer is **1.1 % of the numbers being subtracted** (the reduction's own
  `cancellation_ratio` = 0.0111). Protocol hashes are
  **consistent** across the three legs, so the cycle is *not* contaminated by a protocol mismatch; the record's
  `converged: false` is only `n_replicas >= 3` failing at n=1, **not** an MD-convergence finding. Four
  consequences, each verified against the frozen gate rather than asserted:
  - **r1+r2 cannot PASS.** Exhaustive scan of every (r1,r2) over [−4,+8]² through `calibration_gate`: 0 PASS,
    17,276 BORDERLINE, 11,885 FAIL. Condition 3's boundary rule needs a first-round PASS to carry cycle
    SD ≤ 0.25, while one replicate pinned at −0.534 forces SD ≥ 0.69. Buying r1+r2 buys a
    *BORDERLINE-extend-to-5* or a FAIL — neither authorizes NR-V04.
  - **The n=3 round was never decisive.** A *perfectly accurate* method passes first-round only 9 % of the time
    at the repo's own assumed replicate SD of 0.7 (50 % at SD 0.3, 20 % at 0.5, 4 % at 1.0).
  - **The gate admits the null.** `|mean − 0.944| ≤ 1.0` accepts mean = 0.0, so at n ≥ 5 a method predicting **no
    cooperativity change** PASSES (verified: five replicates at +0.05 → PASS). Monte Carlo: PASS 22 % for μ=0 vs
    23 % for a method that is exactly right. **A gate you can pass by predicting nothing cannot validate
    anything.** ⚠ Recorded, deliberately **NOT applied** — amending a preregistered rule after a failing result
    needs an explicit, dated, reviewer-approved defect-fix, not a quiet retune.
  - **Two of three systematic-error detectors were never run; one *could not* run.** No reverse legs exist
    (`antisymmetry_fwd_plus_rev_kcal: null` on all three), there is no redundant edge so no cycle closure, and
    the reviewer's required change #1 (convergence analysis of the committed `.nc`) was **built but never wired
    to any dispatch path** — while `_diagnostics_ok()` returns True when the report is *absent*, so the gate's
    "all diagnostics pass" requirement was satisfied by never measuring it.

  **★ CONVERGENCE READ OUT (2026-07-25, run 30157501491) — r0 IS A MEASUREMENT, NOT A BROKEN RUN, WHICH SETTLES
  THE REPLICATE QUESTION.** Leg `calib_hi_to_lo__ternary_vhl`, seed 0: **2000/2000** production iterations ·
  MBAR ΔG **47.511 ± 0.045** ·
  overlap connected, min-adjacent **0.109** (floor 0.03) · equilibration fraction **0.381** · N_eff **676** ·
  12/12 replicas visiting both ends · **ΔG(t) full-vs-final-half 0.0023**, q3-vs-q4 **0.1255** · **fwd/rev gap
  0.0255** at f=0.875. Replica mixing **0.8915** against a 0.90 ceiling — passes, but **record as marginal**.
  Structurally stable: the alarming 78.9 Å → 14.97 Å solute RMSD is **periodic wrapping** (p50 2.50 Å, p90
  5.91 Å, ~2 % of atoms at ~1 box edge of 126.3 Å; √(0.02·100²+0.98·3²) ≈ 14.4 reproduces it), so the *ternary
  assembly did not rearrange* and the systematic does **not** implicate the SMARCA4→SMARCA2 starting model.
  **Consequence: the statistical error (0.045) is far smaller than the miss — ~34× against the landed n=3 miss
  of 1.543, and ~33× against the superseded 1.478 r0 read that day — so the wrong sign is
  SYSTEMATIC, and replicates shrink variance, not bias.** *(1.478 is r0's reading and is superseded twice over,
  [Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 44 and 51; the conclusion is unchanged by
  either correction, which is why it survives being restated at both values.)* Made worse for the replicate case, not better:
  ternary seed *s* uses the *s%n*-th relaxed SMARCA2 model, so r1/r2 are partly *different structures* and their
  spread would conflate sampling noise with homology-model sensitivity.
  **★ THE LAST OPEN DIAGNOSTIC IS NOW CLOSED — `diagnostics_complete: TRUE` (2026-07-25, run 30169056960).** The
  **ligand-only** pose RMSD was the one mandatory metric never measured. No committed artifact is a topology
  file, so the ligand was *derived*: bonded connectivity read from the hybrid System inside the `.nc`
  (HarmonicBondForce + the softcore CustomBondForce + **constraints**, where X–H bonds live) partitions 141,968
  particles into 4 protein chains, 44,860 waters, 248 ions and **exactly one** ligand-sized molecule — a
  fail-closed identification with a single candidate, not a ranked guess. Result: `n=110, heavy=59` · **pose RMSD
  max 2.765 Å, median 1.644 Å** against a 4.0 Å threshold · `ligand_stable_ok: true` · `mandatory_unmeasured: []`.
  Two *independent* corroborations, both consistent: 59 heavy atoms equals `wurz-calib-frozen.json`'s
  `validation.heavy_1 = heavy_4 = 59` (an RDKit count from freeze time, unrelated to this trajectory), and the
  ligand identified separately in the 5k-particle solvent box matches the one found in the 142k-particle assembly.
  **So the ligand did not drift — which removes the last benign explanation for the wrong sign and leaves the
  systematic where the convergence analysis put it: in the model or the reference data, not in the sampling.**
  ⚠ **Seven defects were found in this gating diagnostic on 2026-07-25, every one reporting success while
  measuring nothing** (never wired · missing `openfe` · an unguarded lazy `mbar` that deleted six other metrics ·
  slice-MBAR never converging · a fwd/rev gap taken where it is identically zero · the checkpoint never opened
  because openmmtools wants `checkpoint.nc` and the driver writes `checkpoint.chk` · a ligand-pose threshold
  applied first to bulk solvent then to a four-chain assembly). Two produced *wrong verdicts*: a silent
  `diagnostics_ok=True`, then a fabricated hard FAIL. **This is an argument for spending the next dollar on
  INDEPENDENT checks — reverse legs, cycle closure — not more replicates through the same machinery.**

  **★ THE REVERSE LEG WAS UNREACHABLE — FOUR CALLERS PINNED IT SHUT (2026-07-25, all fixed).** The preregistered
  forward/reverse antisymmetry check (`hysteresis <= 1.0` — **now MEASURED, see the ★★ result immediately
  below; the `null` this block was written against is superseded**) could not be run at
  all, and each blocker was the same shape — *capability present in the engine, unreachable from outside*:
  (a) `MODE=converge` existed in `nr4a3_ternary_fep.main()` but no workflow could dispatch it; (b) the run
  invocation hardcoded `DIRECTION=fwd`; (c) there was no `direction` dispatch input (adding one hit GitHub's
  25-input cap → retired the confirmed-no-op `constrain_ligand_ch`, pinning `CONSTRAIN_LIG='0'` so every existing
  `clig0` commit prefix stays resumable); (d) `ternary-setup-prime-cpu.yml` pinned `DIRECTION: fwd`, and since
  the setup-cache key is `tag=<leg>_<dir>_r<seed>` a rev leg needed its own prime and could never get one while
  the GPU lane fails fast on `RBFE_REQUIRE_PRIMED_SETUP=1`. A `direction`-keyed commit prefix (`_dirrev`, applied
  only when direction≠fwd) now makes it impossible for a rev leg to silently resume the fwd trajectory.
  **Root cause of the rev-only failure (fixed):** `_build_components` passed `base_smiles=sa` to `_endpoint_pose`,
  where that argument means *"the identity of the molecule in the staged crystal SDF."* `sa` is the crystal ligand
  only in the FORWARD direction (calib_hi = cmpd1 = 8G1Q CCD `YHB`); cmpd4 is derived and in no crystal. With A/B
  swapped, the rev leg claimed the crystal held **cmpd4**, `_repair_pose` assigned bond orders against a template
  differing by N→CH, the thiazole lost its aromatic C–H, and NAGL rejected the molecule
  (`RadicalsNotSupportedError`). `CRYSTAL_SMILES` is now captured from the *unswapped* endpoint A; forward
  behaviour is byte-identical; 4 pure-stdlib regression checks added (`tests/test_ternary_crystal_identity.py`),
  one asserting that in rev the crystal must NOT equal endpoint A so the test discriminates the fix from the bug.
  **The forward r0 result is unaffected** — in fwd the argument was correct, `_endpoint_pose` fails closed on a
  SMILES mismatch, and the $0 5-part pre-spend gate's `endpoints_match` check passed.
  **Infrastructure finding worth keeping (fixed):** the setup-cache upload failure was **not** the "transient
  GcsApiError" the code called it — `gcloud storage cp` renders a permission denial as `GcsApiError('')` with an
  empty message, and only the python client showed the truth: **403, `gpu-runner@` lacked
  `storage.objects.create` on the `setupcache/` prefix** while succeeding on `stagecache/` in the same job. Two
  fresh builds died there (fwd 11.5 min, rev 11.7 min, same file) so it was systematic, and retries could never
  help; a 403 now aborts immediately with the real reason. **trimcrae granted the permission 2026-07-25 and a
  per-prefix write probe (`gcp-quota-check.yml`) confirms all four prefixes writable.**

  **★★ THE REVERSE LEG LANDED AND THE ANTISYMMETRY CHECK PASSES — the detector that "could not be run" is now
  a MEASUREMENT (2026-07-28, reduce [run 30353349373](https://github.com/trimcrae/Rare-cancers/actions/runs/30353349373)).**
  `calib_hi_to_lo__ternary_vhl` dir=rev seed 0 reached its result on GCP L4 (free trial credit) at 4:03 PM ET
  2026-07-27, and the reducer reports **`MEASURED |ΔG_fwd + ΔG_rev| = 0.325 ≤ 1.000 (PASS)`**. One home for the
  number: the reduction JSON in `gs://…-rbfe-ckpt/valB-6hax/results/` and that run's `[REDUCE-VERDICT]`
  annotation — never re-typed elsewhere.
  **What it does and does not buy.** It is an *internal-consistency* detector, and it is the first of the three
  systematic-error detectors to return anything at all: the forward and reverse alchemical paths agree to
  0.325 kcal/mol, so the wrong sign on this calibrator is **not** a path/hysteresis artifact. That is a genuine
  narrowing — it removes one of the two remaining benign explanations, exactly as the ligand-pose RMSD removed
  drift — and it leaves the systematic where the convergence analysis put it: **in the model or the reference
  data.** It is emphatically **not** evidence that ΔΔG_coop is right; antisymmetry is a check the sampling can
  pass while the answer stays wrong.
  **The calibrator verdict itself is still `INDETERMINATE`, and for a different reason than before:**
  `n_replicates=1`, `per_replicate_ddG_coop=[-0.522]` against `target=0.944`, so there is no replicate SD and
  the cycle cannot be graded. Cycle closure (the redundant edge) is **RUNNING as of 2026-07-29, 11:24 AM ET** —
  see step 5 below for its status and gate reading; it was the last unrun systematic-error detector.
  ⚠ **−0.522 here, −0.534 in the RUNG 2b timestep rows above, and BOTH are correct — do not "reconcile" them.**
  This line is the calibrator's CURRENT reading, which uses the restrained binary arm (Appendix A 44). RUNG 2b
  compares a 4 fs cycle against the *unrestrained* 2 fs one, so its comparator must stay **−0.534**: swapping
  in −0.522 would measure the restraint rather than the timestep, which is the whole quantity that gate exists
  to isolate. Changing either number in isolation silently breaks the other.
  **The blocker is still r1+r2, but they are no longer blocked — both are RUNNING** (2026-07-29, 11:10 AM ET).
  The partial-charge defect that had them dying on dozens of hosts is fixed and merged to `main`; each arm
  holds an RTX 5090 at **$0.005119/ns · 1.50× basis**, under the buy line. It was never held on price, never
  on capability, and never on anything GCP can supply (`GPUS_ALL_REGIONS = 1` makes GCP strictly serial) —
  that last clause still stands and is why the closure triangle went to Vast too.
  **Superseded, retained** (per rule 1, because the old status is quotable): "withheld by the failure breaker
  … its fix is on `fix/ternary-vast-deaths` and unmerged as of this writing." The branch is merged; the
  breaker's withholding of *these* units ended when the fix landed, and the four TRIANGLE units it was still
  withholding were cleared by `task=supersede-failed leg_only=to_lo2` at 11:18 AM ET — a deliberate gesture
  after the cause was fixed, not a loosening of the breaker, which re-arms on the next fresh `status=failed`.

  **Recommended next steps (spend order) — REVISED 2026-07-25 (LANE 5); steps 1, 2 and the ligand diagnostic are
  DONE, and step 4's named design was REFUTED for $0 before any spend:**
  1. ✅ *done, free* — the convergence analysis above, and now the **ligand-only pose RMSD** (`diagnostics_complete: TRUE`).
  2. ✅ *done, free* — **the admits-zero gate defect fix was already APPLIED in place at 8:25 AM ET**
     (commit `3f11cbf5`, delegated reviewer authority) — not merely proposed. It has since been **independently
     audited** (`valb_gate_audit.py`, calling the shipped gate): **strictly stricter across 20,468/20,468 grid
     points with 0 counterexamples**; **conditioned on r0 the corrected PASS rate is 0.0 % in every cell**
     (superseded rule: up to 71.6 %); an exhaustive 58,081-cell (r1,r2) scan gives **0 PASS under both**, so it
     demonstrably **does not rescue the failing result**; discrimination improves 2.0× → 10–3330×. Ratification
     block: §8 of [valb-gate-defect-fix-audit-2026-07-25.md](research/manuscripts/valb-gate-defect-fix-audit-2026-07-25.md),
     which states the "applied after an unfavourable result" optic plainly as the risk.
  3. *in flight* — the **reverse** ternary+binary legs, testing |ΔG_fwd + ΔG_rev|.
  4. **⚠ THE NAMED RESCOPE IS DEAD — the P-series cannot carry this calibrator, established for $0 on real data**
     (`valb_pseries_chem.py` → `valb-pseries-chem.json`; RCSB REST + RDKit MCS in the production mapper's own
     container). **6 of 10 pairs change formal charge** — including **P1→P4 (+2.53), which is `charge_change: -1`
     and therefore blocked by the same missing charge correction that blocks 8 legs of `step1_fanout`** — and the
     4 charge-neutral pairs perturb **58–80 heavy atoms** against the **2** of the edge already running. P4's
     structure (9HYO) is also only **3.74 Å**, so it would not have fixed the resolution problem either.
     **General conclusion worth stating in the paper: a ≥2 kcal/mol ternary calibrator that is simultaneously
     small, charge-neutral and mappable may not exist in the public literature** — large cooperativity
     differences are *produced by* large chemical changes.
  5. **★ RECOMMENDED INSTEAD — a synthetic closure TRIANGLE, RE-SCOPED BY ITS OWN $0 PRE-GATE.**
     **`[~]` RUNNING — AND THE FIX IS PROVEN ON THIS LANE, not merely deployed to it (2026-07-29, 12:12 PM
     ET).** Both binary legs have written committed checkpoints (`warmup/64` → `192`), and these are the exact
     units that died 15 and 7 times at `proto.create` on the partial-charge defect. Passing setup and
     committing is the first direct evidence the fix holds for the triangle's own endpoints — the earlier
     evidence was from the 4 fs replicate arms, a different morph. Progress since has been by COMMITTED
     CENSUS, never a watchdog verdict.
     **`[~]` RUNNING 2026-07-29, 11:24 AM ET — all four legs rented in parallel on Vast.** The gate cleared at
     **1.36× basis** (`$0.004637/ns` mean, against the `$0.006539/ns` buy line) on a deep board — 163 offers,
     159 qualifying, 100 priceable — projecting **$7.73 against this rung's $15.40 ceiling**. It had been
     stalled since 2026-07-28 not on price but on the partial-charge defect, which killed the four units on
     15, 15, 7 and 21 separate hosts and left them withheld by `leg_failure_breaker`; the fix landed 10:53 AM
     ET and the stale failed records were superseded at 11:18 AM ET. Cost of that stall being *legible*: the
     triangle gate had no branch for the breaker's exit code, so it printed the block as `HELD on price` —
     fixed in the same session and pinned by `tests/test_gate_exit_codes_render_distinctly.py`.
     **`[x]` BUILT AND RUNNABLE 2026-07-27 (LANE 19).** It was fully costed and fully argued and could not be
     *run*: no leg id, no third endpoint, no launcher mode, no reducer. It now has all four —
     [`valb_triangle_legs.py`](research/modalities/valb_triangle_legs.py) (the 4 new legs plus the derived
     third vertex, frozen in [`valb-triangle-frozen.json`](research/modalities/valb-triangle-frozen.json)),
     `MODES['triangle']` in [`ternary_vast_launch.py`](research/modalities/ternary_vast_launch.py), and
     [`valb_triangle_reduce.py`](research/modalities/valb_triangle_reduce.py) → `R`. Venue **Vast**; GCP was
     declined deliberately — its scarce quantity is **GPU-days, not dollars**, and this rung would cost
     ~7.3 SERIAL days of the only GPU to save the plan figure below.
     **Three invariants are enforced in code, not remembered**, because each silently turns `R` from a
     path-error detector into a *protocol-difference* detector: **2 fs** (a mode-level pin that beats the
     lane-wide 4 fs export — r0 is 2 fs and r0 *is* T1), **seed 0** on every leg, and **UNRESTRAINED** binary
     legs matching r0. *(The restrained binary re-run is a DIFFERENT experiment; the two must never be
     conflated or their legs mixed in one reduction.)*
     T1 = cmpd1→cmpd4 **is r0, reused** at coefficient +1 (verified: the triangle closes in T1's as-run
     direction, no sign flip). Evidence:
     [valb-closure-triangle-pregate-2026-07-25.md](research/manuscripts/valb-closure-triangle-pregate-2026-07-25.md)
     (`valb_triangle_chem.py` in the production mapper's own container + `valb_triangle_closure.py`, 19 tests).
     **Three corrections to the design as originally proposed:**
     - **(i) T3 is a DOUBLE perturbation for all four named cmpd4′ candidates** — X and Y act at different
       sites, so the closing edge carries both, which `rbfe_map.py` forbids *specifically for closing edges*
       (*"Each closing edge is itself a SINGLE-site change (not a double mutation)"*). **Use an AZA-SCAN at the
       linker ring instead:** cmpd1 (aza) → cmpd4 (all-carbon) → cmpd4″ (aza moved) — three vertices at **one**
       site, every edge **single-site, charge-neutral, a pure element change with ZERO heavy dummies**, and
       entirely inside the linker so it touches **no pharmacophore** (all four named candidates land on one).
       Hand-verified from the SMILES: the linker ring is `c4ccnc(c4)` with a carbonyl and a piperazine at the
       substituted positions, leaving **exactly 3 free CH** vertices.
     - **(ii) Price is ~$6.83 at n=1 and ~$27.32 at n=3, not $5.9/$17.6.** Three corrections, and **the largest
       is NOT the iteration basis**: (a) the 2800-iteration/3.5e6-step basis is +16.7 %; (b) solvent legs add
       ~$1.31 if run by default; **(c) T1 has only r0, so an n=3 triangle is 16 legs, not 12 (+33 %) — and it
       silently re-includes the r1/r2 spend the r0 verdict argued against.** At 4 fs everything scales by
       **0.643, not 0.5** → n=1 ≈ $4.39. Every figure is a **ceiling** (the binary leg is charged at the
       ternary rate despite lacking the SMARCA2 bromodomain).
     - **(iii) `_endpoint_pose` cannot build any cmpd4′ today** — it has exactly one mutation path
       (`_pyridine_to_benzene_pose`) and raises `SystemExit("refusing a wrong-molecule leg")` otherwise. The
       claim that "the machinery carries over unchanged" is false; the aza-scan needs a one-line generalisation.
     **Reporting rules that fall out of the algebra:** report **`R_ternary` and `R_binary` SEPARATELY** — since
     `R = R_ternary − R_binary`, a clean `R` can be two large closures cancelling, and both come from the same
     six legs. And **run all three edges at seed 0**: seed *s* selects the *s%n*-th relaxed SMARCA2 model, so
     mixed seeds mean different Hamiltonians, unshared endpoints, and `R` stops being a closure residual at all.
     **★ HONEST LIMIT, SHARPENED FROM "consistency, not accuracy" TO SOMETHING MUCH STRONGER: closure is
     IDENTICALLY ZERO for ANY per-endpoint state-function error.** Writing `ΔΔG_calc = ΔΔG_true + e`, the true
     terms telescope around a cycle so `R = Σe`; and if `e(A→B) = ε(B) − ε(A)` — which is what a *state*
     property gives — that telescopes too. **So closure sees only the NON-CONSERVATIVE part of the error.**
     Invisible to it: **force field, the SMARCA4→SMARCA2 homology model, NAGL charges, protonation, and the
     reference data**. Visible: λ-sampling/hysteresis, endpoint-state inconsistency, inconsistent atom maps.
     *(Verified numerically two ways: max |R| ≈ 1e-14 over 20,000 random state-function draws, non-zero the
     moment a path error is added.)* The known-answer **accuracy** requirement therefore stays **OPEN**.
  6. **⚠ Rev-leg decision tree — and "the triangle is worth buying under either branch" is RETRACTED. It was
     recorded here on 2026-07-25 afternoon and its own pre-gate refuted it the same evening.**
     - **Branch A** (|ΔG_fwd + ΔG_rev| ≈ 0 ⇒ the systematic is in the **model or the reference data**): closure
       is **provably blind to both** by the telescoping identity above. It would return a clean `R` and diagnose
       **nothing**. *Refuted for diagnosis.*
     - **Branch B** (large ⇒ path error): closure is the right *class*, but the reverse leg already establishes
       it for those 2 legs, and the design's own instruction is **"fix the protocol first"** — so a triangle
       bought before the fix measures the **old** protocol. *Redundant, then stale.* Replica mixing **0.8915**
       against the 0.90 ceiling leans toward this branch, i.e. **the worst branch to buy into.**
     - **★ The real reason to buy is narrower and specific.** The fwd/rev pair already in flight **is** a closed
       2-cycle, so the triangle only earns its keep where a 2-cycle cannot reach. Over 4000 draws — state-function
       error: 2-cycle 0.00 / 3-cycle 0.00; symmetric path bias: both 1.00; **antisymmetric per-edge bias:
       2-cycle 0.00, 3-cycle 1.00.** That last row is the triangle's **exclusive** territory, and on an
       equal-cost 4-leg comparison it still beats both alternatives.
     - **Order:** read the rev leg → **Branch B ⇒ fix the protocol, do NOT buy** → **Branch A ⇒ buy the ~$1.31
       SOLVENT-ONLY closure pre-scout first** (2 new legs; T1's solvent leg already ran; a full machinery closure
       — atom maps, endpoint identity, λ schedule, charges — in a ~5k-particle box at **19 %** of the scout
       price, able to falsify the triangle before any 142k-particle leg), then the **~$6.83 n=1 scout**.
       **Do not buy n=3 at ~$27.3 without a separate decision.**

  **★ THREE MEASUREMENTS THAT REORDER THE PROBLEM (LANE 5, $0):** (i) even the *corrected* gate certifies only to
  a **factor of 4.1** (accept band [+0.472, +1.944] on a +0.944 target); (ii) **P(PASS) has a hard ceiling of
  `P(sample SD ≤ 0.75)` = 66.8 % at σ = 0.7, independent of the target** (analytic and MC agree to 0.15 %) — so
  above ~2 kcal/mol **only precision buys anything**; (iii) sweeping the target shows **2.0 kcal/mol is the
  knee**, which *derives* this file's "≳2" from the gate's own arithmetic instead of asserting it. Consequence:
  **redesigning for a tighter cycle SD beats hunting a bigger signal.**

- **`[ ]` Rung 2b — 4 fs adoption + matched re-calibration** — **~$4.4 ($1.6–11) · Cum. ~$17 · PROPOSED, needs a
  go.** **Exact invocation** (three flags, all load-bearing): `mode=preequil` once (cached), then
  `mode=run use_preequil=1 timestep_fs=4.0 warmup_timestep_fs=1.0 reset_commits=1`. `use_preequil=1` because 4 fs
  only held *with* pre-equilibration; `reset_commits=1` because OpenFE refuses to resume a checkpoint whose
  protocol timestep differs ("Sampler in checkpoint does not match Protocol settings"), so a dt change **starts
  clean** — a fresh edge, not a continuation, which is what the ~$4.4 already prices. One edge, three jobs:
  (a) exercises 4 fs over a **full** 2000-iteration production leg (the existing evidence is 40 iterations);
  (b) supplies the **matched-timestep** calibration the runbook requires before any 4 fs production result may be
  quoted; (c) is an independent reproducibility replicate of the 2 fs ΔΔG_coop. **GO/NO-GO:** no NaN across the
  full leg AND ΔΔG_coop consistent with the 2 fs run within replicate SD → adopt 4 fs for every downstream
  ternary leg (**1.56×** cheaper — *not* 2×, see cost lever 1 — and the ladder has ≥6 of them). NaN or a shifted
  ΔΔG → stay at 2 fs.

  **★ THRESHOLD RATIFIED 2026-07-25 (trimcrae delegated judgement): |ΔΔG_coop(4 fs) − (−0.534)| ≤ 0.7 kcal/mol.**
  The frozen wording says "within replicate SD" and **there is no replicate SD** — the 2 fs arm is a single
  cycle. Lane 4 pre-specified **0.7**, the repo's own assumed replicate SD, **before any number existed**.
  Ratified as written, for one reason that outranks the others: **pre-specification is the property that
  matters, and revising a threshold now — after the probe survived — would be precisely the retune this program
  forbids.** Both arms are seed 0, hence the same homology model *index* — and the two lanes each built their
  own copy of it, so what is established is that the two builds have an identical atom set (measured:
  [ternary-4fs-vast-findings.md §2d](research/compute/ternary-4fs-vast-findings.md)), not that they started
  from bit-identical coordinates.
  **⚠ AND THE COMPARATOR STAYS THE UNRESTRAINED r0 VALUE.** The r0 cycle now also has a **restrained** binary
  arm ([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 44), and swapping that reading in here
  would pair a restrained arm against the 4 fs cycle's unrestrained one — measuring the restraint, not the
  timestep. The restraint is deliberately a different Hamiltonian and is invisible to a composition census
  (it adds a force, not atoms), so this is the one place the like-for-like pairing has to be stated rather
  than inferred.
  **Recorded honestly: 0.7 is LENIENT, and the leniency runs in the unsafe direction.** It is an *assumption*,
  not a measurement, and today's protein-mutation benchmark showed between-setup SD is strongly regime-dependent
  (**±0.175** on a near-null perturbation vs **±1.077** on a hot spot, a 6.2× spread). A 4 fs-vs-2 fs comparison
  on the *same system with only the timestep changed* is a **small**-perturbation regime, so the honest expected
  SD sits near the ±0.175 end — which makes 0.7 roughly 4× wider than the physics warrants. Since a PASS *buys*
  a protocol change, a too-wide band errs toward adopting 4 fs on weak evidence. **Therefore, reporting rule
  (additive, not a loosening): report the actual |Δ|, and a pass landing in the 0.35–0.7 band is
  "consistent but WEAKLY DISCRIMINATING" — adopt provisionally and require the next ternary replicate to
  confirm it, rather than treating 4 fs as settled.**
  **✅ THE PRE-EQUILIBRATION CONFOUND IS RESOLVED (2026-07-25, $0) — the 2 fs baseline WAS pre-equilibrated.**
  The caveat this replaces read: *"`use_preequil` for the 2 fs baseline was never verified — only the workflow
  default of 0 is recorded"*, and it would have made a NO-GO uninterpretable.
  **⚠ BUT THAT DOES NOT MAKE THE TIMESTEP THE ONLY DIFFERENCE, AND THIS ENTRY USED TO SAY IT DID
  ([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 45).** Measured 2026-07-28, $0, from the
  committed trajectories themselves: the two arms run the **same alchemical system** — solute identical
  atom-for-atom in every arm, and the neutralising ion excess (i.e. the solute's formal charge) invariant across
  every build — but they are **two independently constructed builds of it**, on different lanes, providers and
  GPUs, each with its own staging, solvation and pre-equilibration. Their ternary boxes differ by 675 bulk
  waters and 4 ions. **A disagreement would therefore still not have been attributable to the timestep alone**;
  the agreement is a cross-lane independent reproduction, which is a different and in one respect stronger
  claim. Evidence, the full composition census and the ΔΔG sizing:
  [ternary-4fs-vast-findings.md §2d](research/compute/ternary-4fs-vast-findings.md).
  **How it was settled, and why a cache listing could not do it.** A read-only setup-cache probe (added to
  `gcp-quota-check.yml`, dispatched against this branch — it writes nothing and cannot perturb the concurrent
  GCP leg) shows **three** versions coexisting for the forward leg: `v1`, `v1pe`, **`v2pe`**. So *presence* is
  not the discriminator — several caches legitimately exist and a listing cannot say which one a leg
  **restored**. The decisive field is the leg's own `setup_cache_version`, whose physical fingerprint is the
  **particle count**: `v2pe` (alchemy from the plain-MD-relaxed complex) = **141,968**; `v1` (raw) = **146,020**
  (`ternary_fep_reduce._SYSTEM_IDENTITY_FIELDS`). **The committed r0 forward `.nc` holds 141,968 particles** —
  measured independently by the ligand-identification work, which partitioned exactly that many particles into
  4 chains, 44,860 waters and 248 ions — and `nr4a3_ternary_fep.py:682` records the same fingerprint verbatim
  (*"fwd's 141,968-particle v2pe"*). **⇒ r0 is `v2pe`, pre-equilibrated.**
  *(This is also the fingerprint that caught the four failed reverse attempts, which ran a 146,020-particle `v1`
  build against the forward leg's 141,968-particle `v2pe` — a mismatch `protocol_hash` cannot see.)*
  **Two-stage, per the 2026-07-24 decision:** stage 1 is a **~$1–2 survival probe** (`prod_iters≈200`) asking
  only "does 4 fs survive well past the 40 iterations the runbook demonstrated?"; stage 2 is the full matched
  edge, only on a passing probe. Sequenced **after** valB_mini's 2 fs result, both because the calibration needs
  something to compare against and because dispatching into that lane now risks cancelling another session's run.

### RUNG 3 — expand the benchmarks *(only if Rung 2 probes look promising)*

- **`[–]` Validation A-full (10–20 edges) — SKIPPED · saves ~$50–140.** valA_mini reproduced the known ΔΔG cleanly
  on the standard am1bcc method, so a full re-derivation is redundant with OpenFE's published benchmark. Framing
  that must hold: cite OpenFE for accuracy; present valA_mini as a single-edge build-consistency confirmation, not
  a standalone benchmark.
- **`[ ]` Validation B-full — component-calibration cube** — **~$22.5 ($6–67) · Cum. ~$40.** ★ **Module 3
  (paralogue discrimination) runs on SMARCA2-vs-SMARCA4, not NR-V04** — **ADOPTED 2026-07-24 (trimcrae go)**: a
  close paralogue pair with degrader-level selectivity, solved structures, a **non-covalent** mechanism, and —
  decisively — **already staged in this repo** (8G1Q, `smarca2_model.py`, the frozen Wurz calibration), so it is
  a marginal add-on to the lane valB_mini already runs rather than a new campaign. NR-V04's selectivity is, by
  the repo's own UniProt result, most plausibly **covalent target-engagement**, which makes it a weak calibrator
  for a noncovalent ternary pipeline — exactly why the reviewer demoted it to a biological holdout. It stays the
  holdout. Apply cost lever 2: the paralogue module needs **N ternary legs + 1 shared binary + 1 shared
  solvent**, not N edges. Four separately-calibrated modules, each with its own pass/fail (a failed module →
  qualitative-only; no blanket "validated"): (1) a second all-binding graded cooperativity edge; (2) ternary pose
  recovery (co-fold, ~$0); (3) paralogue discrimination on a public system (the direct analogue of the NR4A ask);
  (4) productive-vs-unproductive ubiquitination geometry (full-CRL MD). Plus the cis-epimer negative-endpoint
  stress module. **GATE:** the prospective ladder never runs unless the **cooperativity + paralogue-discrimination**
  modules pass.
- **`[!]` NR-V04 covalent feasibility panel — ⚠ RESULT UNDER CORRECTION; ITS **GO** DOES NOT STAND** —
  **~$8 (MEASURED as-run, 18 legs) · Cum. ~$48.** Covalent celastrol–NR4A1 (C551) adduct + C551A + noncov/cov
  sensitivity + warhead/recruiter controls; 18 legs (6 systems × 3 seeds), 6 ns each, ~466k atoms; 17/18
  completed, no blow-ups.
  **⚠ THE READOUTS DESCRIBE THE WRONG INTERFACE.** `nrv04_covalent_md._topology_indices` split E3 from target
  POSITIONALLY ("target = last sorted protein chain"), while the co-fold YAML builder writes the target FIRST
  (`proteins = [("A", lbd)] + e3`). The chains are A=254 (NR4A LBD), E=213 (VHL), F=118 (EloB), G=112 (EloC), so
  the rule selected **Elongin C** as the degradation target: R1/R2 measured the **EloC↔rest** interface and R3
  counted **Elongin C's** lysines, not NR4A1's. Proof from the panel's own committed legs — the reactive Cys,
  resolved independently by geometry and sitting on the NR4A1 LBD, is recorded on chain **A** in 12 of 14 legs
  while the positional rule pointed at **G** (CI run 30122828434). The arithmetic reproduces the reported numbers
  exactly; the *interface* is wrong. The superseded science numbers are listed in
  [§Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) and **must not be cited**; the
  infrastructure/pricing record (~$0.43/leg, ~$8/panel) is unaffected.
  **★ STATUS (2026-07-25, LANE 3) — THE WITHDRAWN GO CANNOT BE RECOVERED AT $0, AND IT WAS NEVER AVAILABLE TO
  RECOVER. THE RE-RUN IS `[HELD]`, NOT MERELY UNLAUNCHED.** Four findings, each measured, not argued:
  1. **No trajectory was ever persisted**, so recomputation against the correct chain pair is impossible. A
     read-only S3 census (`nrv04_result_forensics.py`, CI run 30167457977 → `nrv04-result-forensics.json`) finds
     **72 objects / 19 units and `trajectory_objects_found: 0`** — 796 MB of `built_cif` (solvated topology +
     **pre-minimisation** coordinates = one frame), 1.35 GB of `built_system` (forces/parameters, no coordinates
     over time), and 27 kB of `leg_result` scalars **already reduced against the wrong split**. The driver
     reduces each frame in-loop and discards positions, and `_rm_ckpt` deletes the single checkpoint frame on
     clean completion (17/18 legs). The MD must be re-run or nothing.
  2. **The prereg's own frozen `panel_verdict()` returns `go: false` on the panel's own committed legs** —
     *"warhead_only recruited despite no E3 moiety"* and *"inactive epimer engaged VHL"*, i.e. **both negative
     controls came back positive**. All 17 legs returned `frac_frames_in_contact = 1.0`, and R2's frozen rule
     (any contact in >50 % of frames) **cannot be failed by a system started from a co-folded complex** — the one
     leg ever run with the *corrected* split returns `recruited=true` too. The recorded GO ("active 3/3 vs epimer
     1/3") is an **R1 narrative that §5 does not score.** So the chain split changed which interface the numbers
     described; it did **not** manufacture a GO that the frozen rule would otherwise have given.
  3. **The panel's INPUTS were contaminated as well — a third, independent data-invalidating defect.** A census
     of all 12 persisted systems gives `A=254 E=213 F=255 G=112`; a CA-geometry Kabsch match identifies the
     source as `nrv04-descriptive-v3/nr4a1/seed_1` at **RMSD 0.000 Å**, with the clean `nrv04-covalent-cofold`
     **5.884 Å** away. So the panel **simulated 14-3-3 epsilon where Elongin B belongs.** Mechanism:
     `fusion-cpu-extras.yml@786759a9` set `cofold_prefix` default `"nrv04-descriptive-v3"`, so the launcher's
     clean fallback never fired. **⚠ The 2026-07-24 forensics' "the panel is clean on this defect" is RETRACTED**
     — it audited the prefix the *code names*, not the artifact that *ran*.
  4. **A free pre-spend staging check shows the re-run cannot reach the frozen GO on any co-fold in the bucket.**
     All 6 legs stage cleanly with `target=A e3=[E,F,G]` (so the chain fix itself is proven end-to-end for $0),
     but `warhead_only`'s nearest **target-chain** Cys Sγ is **16.39 Å** and `cov_nr4a1`'s is **8.99 Å** — Boltz
     does not seat celastrol against an NR4A1 cysteine in *either* co-fold, so criterion 3 is **unevaluable** on
     every available input. Staged epimer interface 369 contacts vs active 381 (**3 %**) is noise.

  **Consequence: do not pay for the re-run as built.** It is `[HELD]`.

  **★ THE PREREG AMENDMENT IS DONE (2026-07-25, trimcrae-delegated) — and it does NOT authorise the re-run.**
  [AMENDMENT 1](research/modalities/nr4a3-nrv04-covalent-feasibility-prereg.md#amendment-1--2026-07-25-dated-defect-fix-trimcrae-delegated)
  is appended to the prereg with the frozen text left **unedited**. The standard applied: a rule may be amended
  only if its *statistic is shown to lack discriminating power*, demonstrated independently of whether we liked
  its answer. Four rulings:
  - **R2 retired as a gating criterion** → descriptive only. `frac_frames_in_contact` took **18 values and one
    distinct value, 1.0**, including `warhead_only` (no E3-binding moiety) and `recruiter_epimer` (inactive
    stereoisomer). Zero variance across the contrast ⇒ cannot score the contrast.
  - **Frozen criterion 3 removed from the GO condition** — it depended entirely on R2 discriminating, so it was
    **unsatisfiable**, and the gate returned NO-GO regardless of the science. Uninformative, not conservative.
  - **`recruiter_epimer` demoted** to a descriptive sensitivity leg — it runs as a full ternary, not the binary
    §3 specifies, and 6 ns from a co-folded pose cannot resolve a binding-affinity difference anyway.
  - **★ NEW BINDING CRITERION A1 — input admissibility, and it FAILS NOW.** A covalent leg must stage its
    electrophilic carbon within bonding distance of the **target-chain** Cys Sγ.
    ⚠ **CORRECTED SAME DAY BY [AMENDMENT 2](research/modalities/nr4a3-nrv04-covalent-feasibility-prereg.md):
    A1 was measuring the WRONG CYSTEINE.** It resolved the *nearest* of the construct's **six**, which is
    **C566**, not the preregistered site **C551** (offset 344: co-fold resid 222 = C566, 207 = C551; the panel's
    legs record resid **222** throughout). **At C551 the real distances are 28.46 Å (`cov_nr4a1`) and 36.43 Å
    (`warhead_only`), and 28.42–39.11 Å across ALL 34 co-fold models** — against a ~1.8 Å C–S bond.
    *(Superseded, do not cite: 8.99 / 16.39 Å.)* **This makes A1 more binding, not less: at ~9 Å it was NEARLY
    PASSING an 8.0 Å limit, so a co-fold seating celastrol 7 Å from C566 would have PASSED while the real site
    sat ~28 Å away.** Two further defects shared the root cause and are fixed: the covalent **restraint would
    have been built onto C566**, and **`cov_c551a` was mutating C566** — the control named for removing C551
    engagement was not touching C551 at all. Boltz seats
    celastrol against no NR4A1 cysteine in any co-fold in the bucket, so §5 criterion 2 (*does covalency swamp
    the ternary signal* — the panel's stated crux) is **unevaluable on these inputs**, not merely unmeasured.
    Enforced in code (`nrv04_covalent_md`, `MAX_COVALENT_TETHER_A` default 8.0 Å, override only with a recorded
    deviation) and **retrospective in force** — it binds the NR-V04 retrospective's covalent legs too.

  **Non-rescue, stated as the integrity test:** the amended gate leaves the panel exactly where the unamended one
  did — **`[HELD]`** — because A1 fails on every available input. What changed is *why*: from "a gate that can
  never pass" to "inputs that do not instantiate the contrast." **It converts no NO-GO into a GO.** Stated
  plainly: removing an unsatisfiable criterion *is* a loosening, since GO becomes reachable where it was not;
  the justification is the measured absence of discriminating power, not the unwelcome verdict. Same degenerate
  class as valB_mini's gate that **admits the null** — one always fails, one passes anything.
  **★ SAID, 2026-07-25: the covalent legs are DROPPED and the panel is re-scoped to NONCOVALENT.** The re-fold
  route was **run and refuted** for **$0.05** on Vast (2 systems × 3 seeds), not argued away: deleting the E3
  makes seating *worse* (33.6/36.6/44.7 Å vs ~28 Å ternary, so the ternary arrangement is not the cause), and a
  **steered** co-fold that demonstrably honoured an explicit `max_distance: 6.0` restraint to residue 207
  (~37 → ~15 Å, contacts doubled) **still never satisfied its own 6 Å bound on any of three seeds**, parking
  celastrol near the buried C505. **One predictor** (Boltz-2) fails to produce the pose across 7/7 clean models, 4 seeds and 3 prefixes *(the "2 providers" are compute hosts, not two independent predictors — so this is a Boltz-2 result, not a statement about structure prediction in general)* and no deposited celastrol–NR4A1 structure constrains it, so the only route left is a **hand-placed
  pose** — which fixes the *comparison* without supplying the *evidence*. **This is a statement about the
  predictor, not about whether celastrol binds C551**, which is literature-anchored (Zhang 2018,
  doi:10.1039/C8CC06140H). **Retiring them costs little: Leg 0 already did their job for $0** — the reactive Cys
  is unique to NR4A1 (NR4A2 Tyr, NR4A3 Thr579), which is the covalent confound's actual content — and NR-V04 is
  already a demoted *biological holdout*, so modelling its covalency inverts the ladder.
  *Hypothesis the amendment raises and the re-run can test (not asserted): the superseded covalent-vs-noncovalent
  null (2/3 = 2/3) is what one predicts if the "covalent" leg never carried a bond.* Full evidence:
  [nrv04-covalent-panel-recovery-2026-07-25.md](research/modalities/nrv04-covalent-panel-recovery-2026-07-25.md)
  · prior chain forensics
  [nrv04-cofold-chain-forensics-2026-07-24.md](research/modalities/nrv04-cofold-chain-forensics-2026-07-24.md).

  **★ FOUR BUGS FOUND HERE PROPAGATE TO THE UNLAUNCHED NR-V04 RETROSPECTIVE (RUNG 4), WHICH SHARES THIS DRIVER —
  both are fixed with regression tests, and the retrospective must not launch on the old code.**
  (i) **`_reactive_cys_by_geometry` was chain-blind** — a second live instance of the *same* defect class as the
  chain split; it is now restricted to the identified target chain, raises above an 8 Å preformed-adduct limit on
  covalent legs, and records its search diagnostics. (ii) **R3 reported NANOMETRES under an Ångström label.**
  OpenMM positions are nm; R1 converted (`* 10.0`), R3 did not, so **every committed R3 is ~10× too small** —
  reading as ubiquitination-competent (~2–4 Å) when the true separation is **~30–49 Å**. Independently
  cross-checked: `warhead_only` reported `min_A` 2.34/2.44 against a t=0 distance of **25.21 Å**.

  **★ HIGHEST-LEVERAGE INFRASTRUCTURE CHANGE FOR THE WHOLE TERNARY PROGRAM (adopted as a requirement, 2026-07-25;
  ✅ IMPLEMENTED 2026-07-30): every MD driver must persist a strided TRAJECTORY.** Tens of MB against the ~112 MB
  System XML the driver *already* uploads — and every analysis defect above (wrong chain split, chain-blind
  cysteine search, the R3 unit error) would then have been correctable for **$0** instead of costing a re-run.
  This is the concrete, general lesson from a panel that produced three data-invalidating defects and left
  nothing to re-derive from. **The requirement stood unimplemented for the whole of that period and the
  retrospective would have inherited the gap** — what shipped, why it is an *analysis-atom* closure rather than
  every heavy atom, and what that does and does not buy, is in
  [§WHAT THE LANDED RESULTS CHANGE](#-what-the-landed-results-change-about-the-remaining-plan) 4,
  which is the one home; code: [`md_analysis_traj.py`](research/modalities/md_analysis_traj.py).

### RUNG 4 — warhead map, differential atlas, retrospective gate

- **`[~]` Step 1 fan-out — cmpd19 congeneric map** — **~$36 ($15–80; ≈19 RBFE edges × ~13.7 ref GPU-h) ·
  Cum. ~$84.** **RESUMED and RUNNING as of 2026-07-27** — the old *"HALTED at ~$2 with 0/19 ΔΔG"* framing is
  retired. **1 edge complete** (`cw_ev_5cooh`, ΔΔG_bind **0.688 ± 0.197** kcal/mol — a within-run MBAR
  uncertainty, **not** a replicate SD), **1 edge permanently BLOCKED** (`cw_bio_nmethyl_amide`: no available
  mapper reaches the **20-atom provable floor** — LOMAP 17/19, Kartograf 18, against a complete 22-atom map
  that exists as a graph fact, and both LOMAP budgets returned in **0.01 s**, so the MCS timeout is measured
  *not* to be the mechanism. A relaunch aborts identically and buys nothing), **17 remaining and being placed
  as the market allows.** Spend, live state and `$/ns` are on the IN FLIGHT board and in
  [`realised-spend.json`](research/modalities/realised-spend.json) — not restated here.
  Full record: [step1-fanout-lane.md](research/modalities/step1-fanout-lane.md).
  **Scope, if resumed:** the price covers **tranche 1 only** — the 19 edges at their charge-**conserving**
  microstate leg on the **primary frame**. The 8 charge-changing legs are *blocked* (no charge correction
  implemented) and the 6-frame conformer/paralogue axis is a **separate ~6× spend** — so tranche 1 yields a
  single-conformer **conditional** map, **not** the selectivity readout and **not** the sensitivity ranges.
  **Gate:** Val A satisfied (cite OpenFE) AND the Step 1 pilot behaved.
  **Timestep is NOT a lever** — measured free on CPU: the protocol runs at OpenFE's default `constraints=hbonds`
  + HMR 3.0, every X–H is constrained, so all edges are already 4 fs and no 2× saving exists.
  **The "HELD by decision" line that stood here is SUPERSEDED** — the hold was reversed on 2026-07-26 and the
  lane is running; §Open decisions 4 records what retired it.
- **`[ ]` Step 1 fan-out · REPLICATES ON THE OPEN CYCLE — the map's two open caveats share ONE fix** —
  **~$25 (3 edges × 2 further replicates)** · Cum. ~$109. **Added 2026-07-30.** The fan-out delivered 18 edges
  at **one replicate each**, and that single fact is what leaves two separate things unresolvable:
  1. **`cycle_3carbonyl` does not close** (R = +1.307 against a ±1.0 tolerance). The residual is a property of
     the LOOP, so it cannot name the guilty edge — and at n = 1 it also cannot be separated from three unlucky
     single draws. **Its three edges therefore carry a reservation wherever they are quoted**, which is a live
     tax on the paper's §2.9.
  2. **The pilot and the fan-out disagree by ≈0.78 kcal/mol on the SAME nominal perturbation**
     (`cw_ev_5nh2`: +1.84 ± 0.36 vs +1.064 ± 0.118) — several times either stated error. Different lanes and
     settings, so it is not a like-for-like replicate and licenses no reproducibility statistic in either
     direction; it is currently reported as an unreconciled discrepancy.
  **What replicating the three edges of that cycle buys, and why it is one purchase not two:** it attributes
  or dissolves the closure violation, *and* it delivers **the binary lane's first measured replicate SD**. The
  program owns exactly one replicate SD today (0.375, on the **ternary** lane) and transfers it everywhere —
  including into the resolvable-margin figure in §MECHANISM-FIRST and into `S`'s power. A binary-lane number
  would stop that being a transfer.
  **★ THIS IS BRINGING A TEST *TO* ITS FIELD STANDARD, NOT PAST IT** — the distinction CLAUDE.md §5 draws, and
  it matters because "more replicates" is otherwise the thing that rule defaults **NO** to. The repo's own
  stated RBFE/ABFE standard is *"converged fwd/rev + ~3 independent replicates + honest replicate-SD, not
  MBAR-SE error bars"*; this lane shipped at **one**, and the paper says so in three places. Scope is
  deliberately **3 edges of 18**, not the map — the open cycle is the decision-relevant subset.
  **Price, DERIVED not typed:** `realised_usd` **$73.79** over `n_computable` **18** edges
  ([`realised-spend.json`](research/modalities/realised-spend.json) →
  [`step1-fanout-map.json`](research/modalities/step1-fanout-map.json)) ⇒ ~$4.10/edge × 6 edge-replicates.
  **Gate:** the market, on the same buy line as everything else. **NO-GO reading:** if the replicated cycle
  still fails to close, the defect is mapping or setup rather than sampling, and the three edges are
  **withdrawn from the ranked table** rather than carried with a caveat.
- **`[ ]` The generation-matched null's GENERATIVE arm — control (c), the one that addresses the confound
  actually raised** — **$0 prep + PROJECTED GPU (excluded from the pinned total)** · **Added 2026-07-30.**
  The committed control is the **scrambled-objective** arm, which isolates the winner's curse in the
  **SELECTION** step. The reviewer's confound is the **GENERATIVE** one: `denovo_401` was generated
  *conditioned on the NR4A3 pocket*, and the decoy null it beats was generated for no pocket at all.
  ⚠ **The arm that ran cannot exclude it, and the arithmetic says so out loud:** 0 survivors of 191 bounds
  the manufactured rate at **≤0.0157** (rule of three, 95 %) against the real campaign's own **0.0052** —
  **3×** — with Fisher p = 0.5. **Narrowed, not excluded**, and the deliverable table is the one home for that.
  **What control (c) is:** a *fresh* generation into the **NR4A1** metad-opened pocket, then the identical
  generate → developability → dock → multi-snapshot MM-GBSA → best-of-N funnel. Any NR4A3-selective survivor
  it produces is a manufactured false positive by construction, because the molecules were designed for a
  different pocket. **The driver already supports it** (`nr4a3_generation_matched_null.py MODE=prep-manifest`
  → control receptor manifest; `MODE=reduce` folds the result into the same artifact), and the control
  receptor **exists** — `results/nr4a3-matrix/nr4a1-opened.pdb`, the criterion-matched opened NR4A1 conformer
  §2.5 already uses.
  ✅ **THE $0 HALF IS DONE (2026-07-30): the control receptor and its manifest are staged and committed** —
  `results/nr4a3-genmatched-control-c/`, built by `MODE=prep-manifest`. **The paid half is one generation +
  one funnel pass**, and the lane is launch-ready rather than needing a build first.
  ⚠ **AND STAGING IT SURFACED A TRAP THAT WOULD HAVE INVALIDATED THE CONTROL SILENTLY.** The two committed
  NR4A1 artifacts describing this pocket **do not share a residue numbering** — the LANE-13 release ensemble
  carries `cv_residues` in UniProt numbering, the matrix's opened conformer is renumbered — so handing one
  artifact's numbers to the other boxes **ten wrong residues and reports success**, the same shape as the
  positional chain split that cost the NR-V04 covalent panel its entire spend. The box is therefore **not a
  remembered list**: it is re-derived by matching residue **IDENTITIES**, and **exactly one** alignment of 400
  candidates reproduces all ten. One hit is a resolution; several would have been a fit, and a test fails if
  that ever becomes true.
  ⚠ **Priced PROJECTED and excluded from the pinned total**, per §Spending rules 4: the real campaign ran this
  exact funnel, but its cost was never broken out as a ladder line, so there is no completed benchmark leg to
  quote. Price it off the real campaign's ledger before buying it, not off this entry.
  **Gate:** none upstream — it is a control on work already in the paper. **Reading, pre-registered here:** a
  manufactured rate at or above the real campaign's own survival rate means the confound is **not** excluded
  and §2.6/§2.7 keep their current hedges; materially below it means the survival is not a generic funnel
  artifact. **Either outcome is publishable and neither unlocks anything downstream.**
- **`[x]` TIER-0 · NR4A paralogue-UNIQUE reactive-residue map — DONE 2026-07-24 · $0 · GATE PASS/GO.** Full-length
  UniProt (P22736/P43354/Q92570/Q01844) + dual-aligner agreement + matched-model geometry
  (`nr4a_paralogue_unique_residues.py`, 15 unit tests, run on CI because the sandbox proxy blocks UniProt).
  **4 NR4A3-unique cysteines** (2 exposed) ⚠ *out of **20** enumerated — the other 16 are SHARED, and uniqueness here is enumerated **ONE-WAY only**: the reciprocal handles (both paralogues carry C534 where NR4A3 has S565; NR4A1 carries C551) are absent from the JSON*: **C397** — NR4A1 N363 / NR4A2 S363, RSA 0.395, **10.9 Å** from the
  cryptic pocket (exit-vector reach) — plus C420 (18.3 Å, RSA 0.311), C559 (12.8 Å but RSA 0.095, buried in this
  conformer), C166 (outside the LBD). **4 NR4A3-unique lysines** (3 exposed in the LBD): **K572** (RSA 0.879,
  11.5 Å), **K518** (0.413, 13.4 Å), **K592** (0.506, 16.2 Å), K178 (outside). Reciprocal check reproduces the
  NR-V04 Leg-0 exactly (NR4A1 C551 → NR4A3 T579) and completes it: NR4A1 has 5 cysteines NR4A3 lacks. K85/K194
  excluded on aligner disagreement. EWSR1 fusion moiety contributes only 1–2 lysines → **fusion-lysine axis is
  thin, not a design axis**. This is the FIRST gate in the ladder — it costs nothing and it decides what 5a
  optimises. *(Open, cheap: the matched NR4A1/2 MD-ensemble add-on should report the **distribution** of C397
  exposure, not one frame's 0.395 — and could reopen C559.)*
- **`[x]` NR4A differential surface atlas — DONE · $0 · GATE PASS/GO.** Matched Shrake–Rupley SASA + BLOSUM62
  alignment over NR4A{3,1,2} opened models → **46 differential-surface handles** (exposed × divergent ×
  character-changing), 15/15 LBD lysines exposed; per-residue identities reproduce the canonical map 148/148. A
  differential surface exists to steer an E3 against (distinct from the ~70 % pocket hotspot), so the 5a
  orientation-basin search is warranted. *(Optional add-on: matched NR4A1/2 MD ensembles ~$10–40 to test which
  handles survive dynamics.)*
- **`[!]` NR-V04 retrospective — preregistered holdout — ★ HELD 2026-07-25: IT COULD NOT HAVE RETURNED A
  VERDICT UNDER ANY PHYSICS, TWICE OVER** — **~$24 ($5.6–78; repriced from ~$21 onto the 2800-iteration basis)
  · Cum. ~$107.**
  A **$0** pre-spend audit (`nrv04-retrospective-prespend-audit-2026-07-25.md`) found **two independent, silent
  blockers**, each of which would have consumed the whole spend and read post-hoc as a result:
  - **(1) The collector read keys the driver never writes.** `retro_collect` read `d["R1"]`/`d["R2"]`; the
    driver writes **`R1_interface` / `R2_recruitment` / `R3_lys`**. Controlled reproduction through the *real*
    collector: **24 flawless legs → every `e1_plateau_A` None → every leg `technical_failure` → every arm
    underpowered → `tier: INDETERMINATE`.** Corroborated on real artifacts — **19/19 leg JSONs carry
    `R1_interface`, 0/19 carry `R1`**, and two other in-repo consumers read the correct key. **The existing
    tests could not catch it**: they feed the gate `e1_plateau_A` directly, so the driver→collector boundary was
    never crossed. Fixed, with a schema guard that refuses a verdict when legs land, none blow up, and none
    yield an endpoint.
  - **(2) The covalent R2 arm is unbuildable — and it BLOCKS R1 rather than merely costing an arm.** AMENDMENT
    2's finding reproduces on *independent* models: at the preregistered C551, `retro_cov_nr4a1`'s three pinned
    models measure **34.42 / 29.87 / 39.11 Å** against the 8.0 Å limit, so `build_system` **raises**. The raise
    happens *before a leg JSON is written*, so those 6 units never land, **`panel_complete` stays False and §4f
    suppresses the R1 contrast permanently.** The two blockers are **sequential, not alternatives**.
  **Cleared, and verified rather than assumed:** the nm/Å unit error, the positional chain split and the input
  contamination are **NOT** inherited — confirmed on **all 9 models**, including the **6 NR4A2/NR4A3 co-folds no
  prior audit had ever measured** (the earlier allowlist skipped them) which feed **12 of the 18 primary legs**.
  **★ AMENDMENT 3 APPLIED (trimcrae-delegated):** R2 **retired** (authorized panel = **R1 only, 18 legs**); the
  §4d extension window corrected from an unreachable `(0.012, 0.05]` to `(0.05, 0.12]`; the **inert** LOMO
  clause demoted to a reported diagnostic (228,543 configurations reached p ≤ α with correct ordering and
  **zero** then failed LOMO); and an **MDE registered** — measured leg-to-leg σ **0.855 Å**, 80 % power only at
  **1.5–2.0 Å**. Non-rescue: **no result exists to flip**, and defects 1/3/4 all tighten while 2 can only add
  work to already-non-concordant results. **Net, the retrospective can claim LESS than before.**
  ⚠ **And a limitation that is not a bug:** R1's arms are **not matched in ligand placement, with the asymmetry
  running against the hypothesis** — warhead↔target contacts at t=0 are NR4A1 **47** vs NR4A2 **106** / NR4A3
  **73**, i.e. *the spared paralogues start better engaged with their target*, and the designated **pilot leg**
  (`nrv04-descriptive-v4/nr4a2/seed_1`) starts with a **1.05 Å heavy-atom overlap**. A null R1 remains a
  registered outcome, but it licenses *"did not resolve a difference of the size this design can detect"* — **not**
  "selectivity is localised to warhead reactivity", which stands on Leg 0 + Zhang 2018 alone.
  **Price, two different objects wearing one name:** the ~$21 line was **Arm F (alchemical)**, which the prereg
  does not authorise and which is blocked — repriced **~$24 ($5.6–78)**. What a GO would actually spend is
  **Arm E: 18 legs ≈ $7.7** at the measured $0.43/leg.
  *(Original entry retained below for the frozen gate wording.)*
- **`[ ]` NR-V04 retrospective — preregistered holdout** — **~$21 ($4.8–67) · Cum. ~$104.** Full ensembles
  through the pipeline, no tuning, epimer control; report directional concordance only.
  **★ GATE RECONCILED TO THE PREREG, 2026-07-30 (trimcrae go; [Open decisions 12](#open-decisions)) — ARM E
  RUNS, ARM F STAYS BLOCKED.** ⚠ *Superseded, retained: **"Gate: Val B-full + NR-V04 feasibility + Step 1
  fan-out"**, applied to the WHOLE item.* That wording was **this file's, not the prereg's**, and the two had
  disagreed since 2026-07-24: the prereg blocks only **Arm F** (the free-energy arm) on the valB PASS, prices
  **Arm E** (R1, 18 legs — *(count SUPERSEDED by prereg AMENDMENT 4, 2026-07-31: **16 legs** — `nr4a3` co-fold seed 3 excluded by measured input fault)*, ≈$8) inside the standing ≲$50 autonomy threshold, and its **§9 "Dependency honesty"**
  had already argued — before any leg ran — that running Arm E is a *narrowing* rather than a gate jump,
  leaving the judgement explicitly open. **The prereg got there first; this is that judgement being taken**, and
  it is recorded as a dated addition in the prereg itself, amending no criterion. What changed since is only the
  premise: `step1_fanout` **completed** and the feasibility panel was **WITHDRAWN**, so two of the three listed
  gates stopped being pending and became unreachable. **HARD PRECONDITION, met:** the shared driver now persists
  a durable trajectory (`md_analysis_traj.py`) — do not launch 18 legs on a build without it.
  **It no longer gates the causal kill-switch** (lever 4).
  **GO/NO-GO:** at least directionally concordant with the NR4A1-degraded / NR4A2·3-spared outcome → GO to the
  prospective ladder; discordant → the ladder is not justified, publish the honest negative. **Interpret with the
  covalent confound explicit:** NR4A1 Cys551 is unique to NR4A1 (NR4A3 T579), so a concordant result may be
  recovering *target engagement*, not ternary cooperativity — which is why this is a biological holdout and
  SMARCA2/4 is the method calibrator.
  **State: fully built + preregistered + unlaunched.** Because the covalent confound is *measured*, the panel
  **decomposes** — **R1** (primary, all-non-covalent NR4A1/2/3) tests whether the workflow discriminates
  paralogues with the warhead held off; **R2** isolates warhead chemistry; **R3** (epimer) is conditional. **A
  null R1 is a registered, publishable outcome**, not a method failure. Three infrastructure defects (kernel OOM,
  error-swallowing monitoring, the 25-input dispatch cap) are fixed in code and **unproven on hardware**, so the
  next launch is a **pilot, not a fan-out**.
  **Resume here: [nrv04-retrospective-handoff-2026-07-24.md](research/modalities/nrv04-retrospective-handoff-2026-07-24.md)**
  (exact commands, cost ledger, traps) · prereg
  [nr4a3-nrv04-retrospective-prereg.md](research/modalities/nr4a3-nrv04-retrospective-prereg.md) · its co-folding
  moved off SageMaker onto the Vast lane
  ([provider-deviation-2026-07-24.md](research/compute/provider-deviation-2026-07-24.md)).

### RUNG 5 — mechanism-first prospective ladder *(the flagship, gated mid-ladder by the causal kill-switch)*

- **`[x]` 5a · Orientation-basin search, mechanism-first — DONE 2026-07-25, $0 REALIZED · TIER-2 GO (CATEGORICAL)** — **~$0 realized (budget was $0–50; the optional MM-GBSA rescore was NOT run and is recommended against — it refines the axis mechanism-first demoted) ·
  Cum. ~$129.** Broad transform sampling across the **widened ligandable E3 set** (VHL, CRBN, cIAP1/BIRC2, DCAF1,
  DCAF15, DCAF16, KEAP1, FEM1B, RNF114, MDM2 — free at CPU. **★ RECRUITER STAGING + THE MANDATORY ≤2 DOWNSELECT
  ARE DONE, $0 (2026-07-25): CRBN (9CUO) + VHL (9GIO) advance — VHL as a labelled *backfill*, not a co-winner —
  and the full dropped set is logged with reasons**, none of them availability. Engine
  `e3_recruiter_staging.py` → [`e3-recruiter-staging.json`](research/modalities/e3-recruiter-staging.json);
  consumer API `load_advanced()`, whose `anchor_xyz` / `exit_direction` / `caveats` fields are the contract the
  basin search consumes. **The remaining 5a work is the orientation-basin search itself.** Two constraints it
  inherits: the E3-breadth widening **confirmed the incumbents rather than displacing them** (structural
  stageability, not availability, is the binding limit — see item (c) above), and the downselect is **blind to
  recruiter-intrinsic pharmacology**, which is a required input to the next gate). **★ Availability answered $0 and it does NOT constrain the choice** (CI run 30125742542): all 8
  widened arms are broadly expressed and record-complete on HPA (`nr4a3_e3_expression.py`, extendable to any
  further candidate), every symbol resolved through HPA's own search with an exact-match guard — same verdict as
  the original VHL/CRBN check. So the downselect must be made on
  **ligandability + interface geometry**, never on availability, and **no recruiter may be dropped with "not
  expressed" as the reason.** Matched 3-paralogue scoring **over the warhead-pose ensemble**; cluster into ~3–8
  basins/ligase; score with the two **categorical** terms (a) and (b) above, then the cheap counterfactual screen
  to nominate marginal wedges.
- **`[~]` 5a-KS · Wedge confirmation — pilot-first KILL-SWITCH + causal RESULT** — **~$23 ($3.1–97) · Cum. ~$152.**
  ★ **FOUR ternary legs — n = 2 SEEDS PER ARM (trimcrae go, 2026-07-30; [Open decisions 11](#open-decisions)).**
  ⚠ *Superseded, retained: **~$12 ($1.6–45) · Cum. ~$141**, which was the TWO-leg configuration — at one seed
  per arm `S` has no replicate SD and cannot report a null, which is its own pre-registered likely outcome.*
  **`[~]`, not `[ ]`: both ternary legs HAVE run and their checkpoints are durable** (NR4A3 `production/800` of
  2000, NR4A1 `warmup/640` of 1600). They are **PARKED, not finished** — see the IN FLIGHT board for why, and
  for the price condition that re-enables them. `[ ]` would say no work exists; it does, and it is banked.
  **PRIMARY: the ligand-side double difference.** Pilot ONE matched pair first:
  `S = ΔΔG_coop(d₀→d | NR4A3) − ΔΔG_coop(d₀→d | NR4A1)`, ternary legs only (lever 2), on the lane Val B
  calibrates. ⚠ **"No discrimination ⇒ STOP" is SUPERSEDED — see the Tier-3 semantics box under §The hard
  kill-switch.** `S` is **non-covalent**, so it tests the **marginal** wedge only and is structurally incapable
  of testing the **categorical** mechanism Tier 2 actually passed on. **`S` ≈ 0 ⇒ the marginal wedge is absent
  and the claim rests on the categorical axis alone; STOP only if the categorical axis has ALSO failed.**
  Discrimination ⇒ extend to NR4A2 and to a second design element.

  **★ THE MATCHED PAIR IS DESIGNED (RUNG 5b, 2026-07-25, $0) — 5a-KS is now buildable.**
  **`crbn|M0` at its term-(a) exemplar**, wedge **3-(3-pyridyl)-L-Ala (*d*) vs
  L-Phe (*d₀*)** at **Thr407** — Leu in NR4A1, Val in NR4A2, so the H-bond **donor is removed in BOTH**
  paralogues. Backbone length, chain strain, E3 clearance and heavy-atom count are stated **once**, in the
  §WHERE WE ARE 5b block above ("The pair stands; the shared-LENGTH reading does not"); the mechanical point
  here is only that the clearance keeps the wedge **off the E3 interface**, so the shared **binary and solvent
  legs still cancel exactly** and only **ternary** legs are needed. ⚠ **The wedge pair and the covalent series
  do NOT share one molecule** — the placement hosts both, but the covalent series sits at 14 backbone atoms and
  the wedge pair at 19. ⚠ *The reason this block **originally** gave — "a single chain carrying both needs 16,
  which the segment grid cannot build (LANE 14 delta L14-7)" — is superseded; the measured blocker is the
  one-pendant chain template, and the §WHERE WE ARE 5b block is its one home.*
  *Differs only in the wedge element:* one atom (C–H→N), identical formal charge, heavy-atom count, rotatable
  bonds and (S) centre.
  **A geometry-only pick would have been wrong**, and the preregistered rule that replaced it is worth keeping:
  geometry alone selected I396 (12.6 Å) — but a pyridyl N against **isoleucine** is desolvation with no
  compensation *in any paralogue*, so `S` would have been ≈0 **by construction**. Rule now: **NR4A3 must present
  a donor and both paralogues must not.**
  **Honest expectation, recorded BEFORE the run:** NR4A1 offers *absence*, not a penalty, so the expected effect
  is an **NR4A3 gain bounded by roughly one partly-buried H-bond (~0.5–1.5 kcal/mol)** — an effect that
  **straddles** the resolvable difference now carried in §MECHANISM-FIRST instead of sitting under it, so **a
  null is PLAUSIBLE and, at an adequate replicate count, INFORMATIVE.** ⚠ *The clause that stood here —
  "against 1.12 resolvable — i.e. A NULL IS LIKELY" — quoted a resolvable figure that has since been measured,
  and is superseded ([Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) 53). The pre-registered
  READING of a null is unchanged; only its informativeness moved.* ⚠ **And the replicate count is now the
  binding design question, not the price:** as parked, the lane is **one seed per arm**, at which `S` resolves
  only the TOP of its own expected range — see [§WHAT THE LANDED RESULTS
  CHANGE](#-what-the-landed-results-change-about-the-remaining-plan) 3 and [§Open
  decisions 11](#open-decisions).
  Fallback fully enumerated and RDKit-verified: `vhl|M3` representative, 11 atoms,
  T407, 10.3 Å — **C52H65N9O9S vs C53H66N8O9S** *(per `nr4a3-linker-library-chem.json`; an earlier C₄₇H₅₅N₉O₉S / C₄₈H₅₆N₈O₉S with "66 heavy atoms" disagreed with the artifact and is superseded — the equal-heavy-atom property holds, the formulae were wrong).*
  *Remaining confounds:* modelled rotamer; double conditionality; unmeasured linker-conformer populations. **Evidence grade:** a NO-GO may be taken on
  valB_mini-grade evidence (stopping is the conservative action), but a POSITIVE result stays **exploratory**
  until valB_full passes.

  **CONFIRMATORY second line — the reciprocal PROTEIN-mutation cycle. ENGINE QUALIFIED 2026-07-25; cost
  PROJECTED, not measured on NR4A.** Pilot ONE direction (3→1); loss ⇒ complete the reciprocal cycle
  (3→2 + reciprocal 1/2→3).

  *Engine:* **pmx + GROMACS** (Gapsys & de Groot) — the published, field-standard *free* engine for
  protein-mutation FEP. perses was retired the same day it was tried: its core protein-mutation path builds the
  old→new residue atom map by round-tripping each residue template through an **OpenEye OEMol**
  (`PolymerProposalEngine.generate_oemol_from_pdb_template` → `oechem.oemolistream`), which is commercial and
  licence-gated, with no conditional and no RDKit alternative on that path. Cost of establishing that dead end:
  **~$0.05.** Everything around the engine was engine-agnostic and survived the swap: staging with a
  mutation-site refusal, the SKEMPI-verified references, scoring, the verdict, and the Vast lane. Code:
  [`Dockerfile.pmxfep`](research/compute/Dockerfile.pmxfep),
  [`protfep_pmx.py`](research/modalities/protfep_pmx.py),
  [`protfep_run.py`](research/modalities/protfep_run.py),
  [`protfep_bench.py`](research/modalities/protfep_bench.py),
  [`protfep_reduce.py`](research/modalities/protfep_reduce.py),
  [`protfep_refcheck.py`](research/modalities/protfep_refcheck.py), `gpu-protfep-vast.yml`; plan in
  [protfep-pmx-plan.md](research/modalities/protfep-pmx-plan.md). **Most of the ladder is $0** — stage-test,
  refcheck, bake and a build-test that runs the ENTIRE hybrid construction on a CPU runner; a host is rented only
  once a hybrid demonstrably builds.

  *Known-answer benchmark — PASSED* (full set on Vast, equilibrium λ windows + BAR, scored by `protfep_reduce`
  against SKEMPI 2.0-verified references; artifact
  [`protfep-benchmark-result.json`](research/modalities/protfep-benchmark-result.json)):

  | benchmark | computed ΔΔG_bind | reference | abs err | within ±1.5 |
  |---|---|---|---|---|
  | barnase–barstar **Y29A** (hot spot) | **+4.424 ± 1.077** (3 complex × 3 apo) | +3.40 | 1.024 | ✔ |
  | barnase–barstar **Y29F** (near-null control) | **−0.370 ± 0.175** (3 complex × 3 apo) | −0.13 | 0.240 | ✔ |

  **Ordering correct** (Y29A ≫ Y29F), which is the test that matters — a wedge is read as a ranking, so a
  magnitude pass with the ordering wrong is a fail. The near-null control did its job: the engine returned
  ≈−0.37 where the experiment sees ≈0, rather than inventing an effect. Both mutations are charge-conserving, so
  engine error is not confounded with the net-charge artifact. `plan_wedge` may now stamp `validated: true`.

  **★ THE MOST DECISION-RELEVANT RESULT IS THE NOISE STRUCTURE, NOT THE AGREEMENT.** At full replication the
  between-setup scatter differs by **6.2×** between the two benchmarks (±1.077 on the +4.4 hot-spot knockout vs
  ±0.175 on the near-null), while *within*-leg MBAR standard errors are 0.05–0.13 kcal/mol in both — an order of
  magnitude smaller. So this is **setup/equilibration variance, NOT insufficient sampling**: running each leg
  longer would not fix it; running more legs would. Two consequences:
  1. **A single leg does not determine a number.** Y29A's mean walked 2.851 → 3.951 → 4.025 → 4.424 as
     replicates landed, and its error against the reference *grew* (0.549 → 1.024). Replicates are mandatory.
  2. **The wedge's own regime is the well-determined one.** The wedge measures a *small* induced-interface
     difference (the best-case resolvable figure lives once, in §MECHANISM-FIRST — this line deliberately does
     not restate it, and the value it **originally** carried is retired there) — exactly where this engine reproduces to ±0.18, not the
     ±1.08 the hot spot suggests. Encouraging for the wedge, and it means **the right validation for 5a-KS is a
     benchmark sized like the wedge**, not a hot-spot knockout. **That benchmark does not exist yet**, and until
     it does the confirmatory line may not claim to resolve a paralogue-scale difference.

  *Price:* **measured 1.058 ± 0.432 GPU-h/leg** over 11 legs (range 0.379–1.8) at a 25,187-particle mean,
  **$0.212/leg** at the $0.20/hr assumed in the reducer → a **PROJECTED** wedge of **~$4.6 (3 replicates)** /
  ~$3.1 (2 replicates). The projection is a **linear particle-count scaling** from 25,187 to the NR4A sizes — an
  assumption, not a measurement, so it may not be quoted as a rate and the confirmatory line stays **excluded
  from the pinned ladder total**. The per-leg GPU-h SD (0.432 on a mean of 1.058) is **host variance, not
  physics** — two hosts rented minutes apart differed ~10× in throughput per particle.

  *Two blockers, both cleared in code before any leg runs*
  (planning layer: [`nr4a3_protein_fep.py`](research/modalities/nr4a3_protein_fep.py), whose wedge subtraction
  delegates to `ternary_coop.ddg_coop` so there is **one** definition of the cycle in the repo, not two):
  - **Cross-lane charge mismatch.** `assert_charge_consistency` hard-fails any wedge whose ternary and binary
    legs charge the ligand differently. An un-pinned wedge is not a thermodynamic cycle, so this is a refusal,
    not a warning. Pin NAGL across both legs (the only method that can charge both a small mutation edge and a
    PROTAC-scale assembly) and stamp it into both result JSONs. Cost: $0.
  - **Net-charge-changing mutations, and it bites immediately.** **R412 is one of our own seven selectivity
    handles, and R→A is charge-changing** — exactly what PME cannot do naively (the neutralising background
    plasma shifts the electrostatic free energy by a system-size-dependent amount that does not cancel between
    the differently-sized ternary and binary boxes). `plan_wedge` refuses a charge-changing mutation unless an
    explicit correction strategy is chosen. **Prefer a charge-conserving handle (L406/T410/I484/I531/L534) for
    the FIRST causal test.**

  *Declared physics deviation:* 2 fs with a 1 fs warmup, not the canonical 4 fs+HMR. Softcore regions are where
  the ternary lane NaN'd, the timestep is empirical with no static predictor, and on a new engine's first leg a
  NaN costs the whole rental while 2 fs costs ~2× the iterations of a sub-dollar leg. Escalate only after this
  lane survives a full NR4A-scale leg — and record it; do not assume it transfers.

  *Sequence, cheapest-decisive-first:* smoke (~$0.10) → pilot (both legs of one direction, ~$1–3 — **the abort
  gate**) → full set (~$5–10) only if the pilot sees it.

- **`[x]` 5b · TWO-MECHANISM REACH — DIAGNOSED 2026-07-30, $0, AND THE ANSWER REFUTES THE QUESTION.**
  Added and closed the same day. The item asked whether a finer segment grid could build one chain carrying
  both the covalent electrophile (→C397) and the causal wedge (→T407). **It cannot, and a finer grid was never
  the issue.** Numbers and the refutation live once, in the §WHERE WE ARE 5b block above; the plan-level
  consequences are here:
  1. **The blocker is the chain TEMPLATE, not the grid** — one `pendant` slot, one branch residue. **That is a
     one-line signature, and it means every sweep over segments and lengths was searching a space that
     structurally cannot contain the answer.**
  2. **A two-branch template is constructible at n = 18 with the segments already in the grid**, so the fix
     costs no new chemistry — but it is a **DESIGN change to a preregistered enumeration**, not a defect fix,
     so it does **not** qualify under the amendment standard that covers a statistic shown to lack
     discriminating power. **It needs an explicit decision, and it is not taken here.**
  3. **The pre-registered NO-GO reading half-fires, and the honest report is the half that did.** It said: *if
     no admissible branch exists either, the limit IS geometric and that is the finding.* One exists in
     principle; what does not exist is a template to hold it. **So the paper's statement is neither "a grid
     limit" nor "geometry" — it is that the enumerated architecture carries one mechanism per molecule**, which
     is a real and reportable constraint on the design as enumerated.
  ⚠ **The existing library is untouched and nothing in it is invalidated** — the diagnostic re-enumerates
  nothing, and a test asserts that.
- **`[x]` 5b · THE TWO-BRANCH TEMPLATE — BUILT 2026-07-30, $0 (trimcrae: *"use your judgement"*). ONE molecule
  CAN carry both mechanisms, there is EXACTLY ONE way to do it, and it is not free.**
  [`linker_twobranch.py`](research/modalities/linker_twobranch.py) →
  [`nr4a3-linker-twobranch.json`](research/modalities/nr4a3-linker-twobranch.json), 10 tests, RDKit-verified
  **16/16**. **The preregistered enumeration is UNTOUCHED and a test asserts it is byte-identical after a full
  run** — this is a SEPARATE artifact and an additive extension, not an amendment. **It unlocks nothing
  downstream** and no gate, verdict or existing construct changes.
  - **★ THE SOLUTION IS A POINT, NOT A REGION — and that is as much the finding as the molecule.** Scanning
    every (SEG1, SEG2, SEG3, warhead) against the windows the committed library actually recorded, **exactly
    one chain** satisfies both at the same length and placement: **n = 18, term-(a) exemplar, a2–a2–a2, the
    5-amide warhead**, electrophile at **k = 13**, wedge at **k = 6**. Change any one segment and one of the
    two windows breaks. A two-mechanism design here has no room to be optimised.
  - **⚠ AND IT COSTS REAL PROPERTY SPACE — reported because it is the honest half.** Against the committed
    single-mechanism library (same chemistry, same handles): **median +10 heavy atoms and +120 Da**, with the
    top of the set at **1248 Da**, *above the entire committed range* (698–1099). That is well into where
    permeability rather than affinity is the binding problem. **So this is a demonstration that the two
    mechanisms CAN be carried on one chain — NOT a claim that the molecule is developable**, and the paper
    must frame it that way.
  - **Claim ceiling, in the artifact:** *constructible and window-admissible against TRANSFERRED windows*. The
    windows come from **single**-branch records; `branch_position_window` is a function of (endpoints, target,
    length, reach) and **not** of branch count, so the transfer is sound — **but no two-branch chain has had
    its own window computed**, and this may never be reported as though one had. No docked pose, no strain, no
    basin-fidelity filtering, no energetic or selectivity quantity of any kind.
  - **Why building it was the right call rather than scope creep:** $0, additive, and the *existing* filters
    and windows decided the outcome rather than my judgement — I put no thumb on the scale. It converts
    *"unknown because inexpressible"* into a measured answer with a stated cost, which is what the deliverable
    (a candidate set with an identified causal mechanism) needs in order to say whether one molecule can carry
    both. **What it does NOT do is make the 5a-KS matched pair two-mechanism** — `S` must isolate a single
    structural element, so the causal test article stays exactly as designed.
- **`[x]` 5b · Inverse linker design — DONE 2026-07-25, $0 REALIZED (1,995 enumerated → 21 retained, RDKit-verified 21/21)** — **~$0–20 (mostly $0 CPU) · Cum. ~$162.** For each confirmed basin, derive
  linker requirements (endpoint distance, exit-vector dihedral, strain, reach), enumerate a virtual library,
  filter by basin fidelity, annotate exact structures + synthetic feasibility → **~12–20 virtual constructs** (the
  reviewer's "24–36" now bounds this virtual set, not a hand-built grid). For basins carrying the covalent handle,
  the library enumerates the **electrophile position on the linker** as a design variable, and **prefers
  reversible-covalent** chemistry.
- **`[ ]` 5c · Explicit ternary-ensemble refinement** — **~$21 ($1.9–85; endpoint MD, 24–~200 legs at ~1.38 ref
  GPU-h each) · Cum. ~$183.** *(The biggest swing item — the leg COUNT, not the rate, dominates its uncertainty.)*
  Replicated ternary + full CRL/E2~Ub MD across target states, linker conformers, and in-basin poses; matched
  NR4A1/2/3; separate accessibility from stability; robust constraint-satisfaction filtering → **~4–8 constructs**
  nondominated under scenario + model uncertainty. Add a constraint: **which lysine the ubiquitin actually
  reaches**, reported per construct as a distribution over unique-vs-conserved sites, not just "a lysine is near".
- **`[ ]` 5d · Local ternary FEP** — **~$21 ($3.1–87; 3–6 ternary comparisons) · Cum. ~$169.** Alchemy **only**
  within a retained basin (both endpoints plausibly bound, modest congeneric change). Refines the matched final
  series → **~6–12** with ≥2 mechanistic wedges, ≥2 linker architectures, VHL/CRBN only where both survive,
  explicit negative controls. **Deliverable** = the prioritized, structure-defined, retrosynthetically annotated
  candidate set with an identified causal selectivity mechanism — degradation experimentally unvalidated.

### OPTIONAL / HELD — only if a specific claim needs them AND a budget nod is given

- **`[ ]` ΔG_open per paralogue** — **~$120–300.** Only to make affinity/selectivity *unconditional*; otherwise
  report conditional on the open state ($0, fully defensible).
- **`[ ]` Conditional ABFE (pose-plausibility)** — **~$80–200.** Raw values, T4L discrepancy separate, no offset,
  does not prove binding. **This hold covers the existing ABFE block's λ-overlap repair too** — it is parked, not
  in flight. Launch only with an explicit nod after everything above.

### RUNG 6 — write & ship (~$0)

- **`[ ]` Fold results into paper** — language discipline; QM/torsion validation at linker junctions;
  physicochemical + retrosynthetic assessment; re-render figures.
- **`[ ]` Final red-team + review-response.**
- **`[ ]` Post + submit** — OUTWARD-FACING, needs trimcrae sign-off.

---

## Spend summary

*★ **APPENDIX — the spend ladder's arithmetic.** The pinned total is **DERIVED** (`vast_cost_model.py` → `vast-ladder-repricing.json`) and `lint_consistency.check_derivations` fails the build if this file, `pricing.md` or `bid-strategy.md` drifts from it. Never hand-carry it.*

**PINNED TOTAL: ~$169 mid-range (~$46–626)**, GO at every gate, priceable stages only.
*(Superseded, retained: **~$158 mid (~$44–578)** — retired 2026-07-30 when RUNG 5a-KS went from **2 ternary legs
to 4** (n = 2 seeds per arm; [Open decisions 11](#open-decisions)). ⚠ **That reprice is the cleanest in this
file's history and it is worth saying why: the market snapshot, the `$/reference-GPU-hour` rate and every other
stage's GPU-hours are BYTE-IDENTICAL across it**, so the entire **+$11 mid** is the second seed per arm and
nothing else — the opposite of the 2026-07-27 reprice, where no price moved and only the yardstick did. And
that earlier one is retained too: **~$185 mid (~$51–614)**, retired 2026-07-27 when the throughput table was
re-anchored; the GPU-hours did not change, the `$/reference-GPU-hour` did. pricing.md Appendix T.)*

**How it is built** — regenerate the alchemical/MD stages with
`python research/modalities/vast_cost_model.py --json-out vast-ladder-repricing.json`
(JSON: [`vast-ladder-repricing.json`](research/modalities/vast-ladder-repricing.json)); the tool prices 9 stages
at **$149.63 ($36.58–531.46)** at the committed snapshot's **$0.1143/ref-GPU-h**. The ladder figure adds the
stages the tool does not cover, at the **[low, mid, high] the machine registry uses** — step0 ~$1–2 (mid
**$1.5**), valA_mini ~$0–15 (mid **$0**, its *realized* cost on GCP credit rather than the band's midpoint), the
~$8 measured covalent panel, 5a basin ~$0–50 (mid **$0**, realized), 5b linker ~$0–20 (mid **$10**):
`149.63 + 1.5 + 0 + 8 + 0 + 10 ≈ 169`; low `36.58 + 1 + 0 + 8 + 0 + 0 ≈ 46`; high
`531.46 + 2 + 15 + 8 + 50 + 20 ≈ 626`. [pricing.md §C](research/compute/pricing.md) and
[bid-strategy.md §6](research/compute/bid-strategy.md) carry the same total — all three must agree, and
[`lint_consistency.py`](research/manuscripts/lint_consistency.py) recomputes it from
[`pinned-figures.json`](research/manuscripts/pinned-figures.json) → `derivations.ladder_total` rather than
trusting any of them.

⚠ **TWO THINGS THIS PARAGRAPH GOT WRONG UNTIL 2026-07-30, both found by regenerating rather than reading.**
**(a)** It stated the 5a basin stage at **mid $25** while the machine registry has always used **$0** — so its
own printed arithmetic came out at **`≈ 194`** beside a pinned total of `~$158`, and the sentence that followed
asserted the chain *"ends on the same ~$158"*. A doc contradicting itself inside four lines, which is precisely
what rule 1 exists to catch; the registry was right and the prose was wrong. **(b)** The tool figures quoted
here (**$149.4 at $0.137/ref-GPU-h**) were from an older market snapshot than the committed artifact, which
carried **$138.16 at $0.1143**. ⚠ **Beware a near-collision when reading old copies of this file: the tool total
is NOW $149.63, which is within $0.25 of the stale $149.4 it replaces, and the two have nothing to do with each
other** — the old one was 2 legs at a higher rate, the new one is 4 legs at a lower one.

**Excluded from the total:** (a) the 5a-KS **confirmatory** protein-mutation wedge and its reciprocal cycle —
engine qualified, but the NR4A cost is a particle-count projection, not a measured rate; (b) Optional/HELD
ΔG_open + ABFE (~$200–500 more).

**⚠⚠ THE `$/hr` AXIS IS MEASURED; THE GPU-HOUR AXIS IS NOT.** The reference GPU-hours are the repo's own work
estimates; this multiplies them by a measured rate, it does not re-derive them. **A rate measured on one
molecular system is not a price for another** — the single largest correction to date (~4× on the fan-out) came
from applying a public-TYK2 per-iteration rate to the NR4A3 complex, which is ~2.6× heavier. The ternary base is
*still* a SMARCA2/VHL rate pricing NR4A ternaries. If the GPU-hours are 2.6× low, these costs are 2.6× low no
matter what we bid. Dominant uncertainties, in order: the **ensemble-MD leg count** (5c + retrospective), the
**ternary transferability risk**, then the confirmatory wedge's particle-count projection.

**What survives every reprice.** The six cost levers are **ratios** — 4 fs halving force evaluations, the exact
binary/solvent cancellation, sequential stopping — so they are independent of $/hr and of system heaviness. And
**none of this weakens the mechanism-first case** — but ⚠ **one of the two arguments that used to carry it has
been retired by measurement and must not be re-quoted.** The *precision* argument — *"spending on an axis
needing ~2.0 kcal/mol when the method resolves 1.12 is a bad trade at any price"* — **no longer holds**, because
the resolvable difference was assumed and is now measured (§MECHANISM-FIRST; [Appendix
A](#appendix-a--superseded-numbers-and-retracted-claims) 53). **Two arguments survive intact and they are
sufficient on their own:** (i) a **categorical** handle needs *no* margin at all, so it is not competing with
the marginal axis for resolution; and (ii) the categorical screens are **$0 CPU** and therefore dominate on
cost at any noise floor. What the correction does change is the marginal axis's **rank**, not its **order** —
it is worth confirming, and §MECHANISM-FIRST says on what condition.

| Rung | GPU work | Step $ (low–high) | Cum. (mid) |
|---|---|---|---|
| 0 · infra + free CPU (DONE) | step0 + emc_e3 + pocket | ~$1–2 | ~$2 |
| 1 · Val A smoke (DONE, realized ~$0 on GCP credit) | 1 public RBFE edge | ~$0–15 | ~$2 |
| 2 · pilot (DONE) + Val B-mini | 1–2 RBFE edges + 1 ternary edge | ~$2.8 + ~$8.8 (range $4–31) | ~$13 |
| **2b · 4 fs adoption + matched re-calibration** | 1 ternary edge @4 fs | **~$4.4** ($1.6–11) | ~$17 |
| 3 · Val B cube (SMARCA2/4 module) + NR-V04 feas. (DONE) | 2–3 ternary edges + CRL-MD; covalent panel | ~$22.5 + ~$8 (range $14–75) | ~$48 |
| 4 · fan-out + atlas + **unique-residue map** (both $0) + NR-V04 retro | ≈19 RBFE edges + NR4A1/2/3 ternary **legs** | **~$36** + ~$21 (range $20–147) | ~$104 |
| 5a · mechanism-first basin search + **KILL-SWITCH** | basin ($0–50, multi-E3, CPU) + ligand-side double difference, **4 ternary legs (n = 2 seeds × 2 arms)** | ~$0–50 + **~$23** ($3.1–97) | ~$152 |
| 5 (if GO) · linker + ensemble refine + local FEP | inverse-linker ($0–20) + ensemble MD (~$18) + within-basin FEP (~$21) | ~$49 (range $5–187) | ~$169 |
| Confirmatory protein-mutation cycle (optional) | 1–3 mutation directions | **~$4.6 PROJECTED** | *(excl.)* |
| Optional ΔG_open / ABFE (HELD) | — | +$200–500 | *(excl.)* |

Notes: the restructuring buys **causal evidence** (matched-pair cycles + ensemble MD + local FEP) over
co-fold-and-score — higher information per dollar, not lower. A non-viable paper still dies for ~$2 at Val A, or
**free** at the Tier-0 unique-residue map and the atlas (both passed). The *expected* cost is lower than the
totals suggest, because the leading gates are now $0.

## Dependency spine

*★ **APPENDIX — the authorisation graph.** ⚠ **This is a SPEND graph: its edges are authorisations, not entailments.** The [roadmap](research/manuscripts/nr4a3-program-map.md) §4's graph is the claim graph, and the two must never be merged — collapsing them loses either the money or the epistemics. Its cumulative notation is deliberately distinct from the plan's and `lint_consistency.check_subsets` errors if the two are unified.*

```
TIER-0 unique_residue_map [x]($0) + atlas [x]($0)  ──[BOTH PASS]──►    ★ leads everything priced
          │        (C397 exit-vector reach; K572/K518/K592 exposed; EWSR1-lysine axis thin)
          │
RUNG0  step0 [x] + emc_e3 [x] + pocket [x]                              (CPU/$0, done; Cum ~$2)
          │
RUNG1  valA_mini [x] ──[GO]──►                                          (cite OpenFE; Cum ~$2)
          │
RUNG2  step1_pilot [x] ∥ valB_mini [~ 2 fs, r0 wrong sign]  ──[GO?]──►  (Cum ~$13)
          │
RUNG2b 4 fs adoption + MATCHED re-calibration (~$4.4) ──[no NaN & ΔΔG consistent?]──►   (Cum ~$17)
          │      └── YES ⇒ every downstream ternary leg ≈2× cheaper
          │      └── NO  ⇒ stay at 2 fs, carry the 2 fs base
          │
RUNG3  valB_full cube (module 3 = SMARCA2-vs-SMARCA4) + nrv04_feasibility [!] ──[GO?]──►   (Cum ~$48)
          │            ([!] = feasibility's GO is WITHDRAWN pending a corrected re-run: its readouts
          │             measured the Elongin C interface, not VHL<->NR4A1. It gates nothing until then.)
          │
RUNG4  step1_fanout ∥ atlas [x]($0) ──► nrv04_retrospective ──[concordant?]──►   (Cum ~$104)
          │      (holdout, NOT the calibrator; read WITH the Cys551 covalent confound)
          │
RUNG5  basin_search($0–50, multi-E3, pose-marginalised, CATEGORICAL terms)        (Cum ~$129)
          │        ──► ★ KILL-SWITCH = ligand-side double difference (~$12)       (Cum ~$141)
          │      └── no discrimination ⇒ STOP: publish honest causal negative
          │      └── discrimination    ⇒ extend + tail
          │      └── CONFIRMATORY 2nd line: the protein-mutation cycle — pmx + GROMACS
          │           (perses retired: OpenEye-gated). Known-answer benchmark PASSED
          │           2026-07-25; NR4A cost PROJECTED (~$4.6), so it is excluded from
          │           the total and still owes a WEDGE-SIZED benchmark before it may
          │           claim to resolve a paralogue-scale difference. It does NOT gate
          │           the ladder — the ligand-side double difference does.
          │
       inverse_linker($0) ──► ternary_ensemble_refine ──► local_ternary_fep         (Cum ~$169)
          │
RUNG6  fold ──► redteam ──► post/submit                                             ($0)

OPTIONAL/HELD (explicit nod only): dg_open_paralogue, abfe_conditional (incl. the λ-repair)
```

## ★★ WHAT THE LANDED RESULTS CHANGE ABOUT THE REMAINING PLAN

*★ **APPENDIX — the reasoning behind the ordering.** Its item 6, the decision-value ranking, is **folded into the [roadmap](research/manuscripts/nr4a3-program-map.md) §10** together with the map's old critical path; the roadmap now holds the union of both plus eight rows that were on neither list. Read this for the *why*; read §10 for the order.*

*Written 2026-07-30 8:21 PM ET, with nothing billing and the fixed scope closed.
Everything above this line records what happened. **This section is the only place that says what it means for
what is still UNBOUGHT**, and it exists because most of what follows is a correction to a load-bearing INPUT of
the plan rather than a new piece of work: with the fixed scope closed and nothing billing, the remaining ladder
was still being steered on three numbers that had never been measured and one requirement that was never
implemented. Per rule 1 nothing here restates a figure that has a home elsewhere — each item points at its
home and carries only the CONSEQUENCE.*

**The one-line reading. The program's blocker is no longer precision and is no longer money — it is that the
flagship quantity `S` has never had a known answer, and, as it was parked, could not have reported its own most
likely result.** ✅ **Both halves of that are now acted on** (2026-07-30, trimcrae go): the lane is re-specified
to **n = 2 seeds per arm**, so a null becomes a *bound* rather than a shrug; and the calibrator question is
split so the free half — *can a null be READ?* — no longer waits behind the paid half
([§Open decisions 11 and 13](#open-decisions)). **Nothing is bought: the four legs stay parked behind the
market gate.** What is left below is the reasoning, and the parts that are still open are marked as such.

### 1 · The axis the plan demoted was demoted on an assumption that has since been measured

§MECHANISM-FIRST is the home for the numbers; the strategic consequence is here, and it is a **re-rank, not a
re-order**:

- **Mechanism-first survives untouched.** A categorical handle needs no margin at all, and the categorical
  screens are $0 — either argument alone is sufficient, and Tier 0/1/2 all passed on that basis.
- **But the marginal axis was written off as a *discovery* tool for a reason that no longer holds**, and the
  §Spend summary paragraph that quoted it is corrected in place. Its problem was never really resolution; the
  measured accuracy failure is a *different* defect with a *different* remedy. **Remedy for a blunt tool: more
  sampling. Remedy for an uncalibrated one: a calibrator.** The plan has been buying neither.
- **⚠ The correction cuts against my own reading as well as for it, and both halves must be carried.** A better
  noise floor does **not** make a 2.0 kcal/mol induced-interface margin *exist* — that is a property of the
  designed molecule, not of the instrument. It only means that **if** one exists, this pipeline can now be
  shown to resolve it.

### 2 · The FAIL was measured on the WORST-cancelling form of the quantity; the flagship uses the BEST-cancelling one

The algebra already lives in [`valb_failure_propagation.error_algebra`](research/modalities/valb_failure_propagation.py)
and is **not restated here**. What had not been drawn out of it is the planning consequence: `ΔΔG_coop` — the
quantity that failed at 1.543 kcal/mol — differences two environments **that differ by a whole protein chain**,
while `S` differences **one morph of one atom across two homologous pockets at matched ternary architecture**.
They are opposite ends of the same cancellation spectrum, and the program measured the bad end and then priced
the good end as though the result transferred.

**⚠ THIS IS NOT A LICENCE AND MUST NEVER BE QUOTED AS ONE.** *"Not implicated"* is an **argument**, not a
measurement — the file's own words. A per-endpoint error that differs **between the NR4A3 and NR4A1 pockets**
cancels from neither `S` nor anything else this program runs, and no check we own can see it
(`s_resolvability_from_R_ternary._blind_spot_stated`). The correct conclusion is narrow and it is enough:
**the valB FAIL is not a reason to leave `S` unbought — it is a reason `S` needs its own known answer.**

### 3 · ★ 5a-KS AS PARKED CANNOT REPORT ITS OWN MOST LIKELY RESULT — a DESIGN defect, and only the PRICE one is on the board

[`valb_failure_propagation.s_error_bar_scope`](research/modalities/valb_failure_propagation.py) computes it and
is the one home: at **one seed per arm** — which is exactly what the two parked legs are — `S` resolves only the
**top** of its own designed effect range. The pre-registered expectation is that the effect sits **inside** that
range. **So the configuration that is parked buys, in its likely case, a number that cannot answer its own
question — the identical defect as valB_mini at n = 1, on the lane that was supposed to have learned it.**

**★ THE $0 CHECK THAT ITEM OWED IS NOW DONE, AND THE ANSWER IS FAVOURABLE.** `s_error_bar_scope` flagged
*"CHECK BEFORE BUYING: whether the 5a-KS co-fold staging has the same seed→model wrap is UNVERIFIED here and
must be checked, not assumed, or the second seed re-runs the first model and buys no independence."* Checked
against the source rather than assumed:

- The wrap that motivated the warning is **`ternary_pdb_stage.py`'s `starting_model_index = SEED % n_models`,
  and it is gated on `target_acc == "P51532"`** — the SMARCA4 template, i.e. the valB calibrator's homology
  substitution. **It cannot reach a 5a-KS leg**, which stages through `nr4a3_5aks_stage` against a CRBN co-fold.
- 5a-KS is **one co-fold per species BY DESIGN** (`nr4a3_5aks_stage` docstring: both endpoints are staged from
  one pose, deliberately, so the alchemical transformation does not have to absorb a pose difference).
- `nr4a3_ternary_fep` seeds each replica's sampler, so **a second seed is genuinely independent SAMPLING**.

**Consequence, stated in both directions.** A second seed **does** buy a real replicate SD — the blocker is
cost, not machinery. It **does not** buy co-fold-pose independence, by construction, so an `S` replicate SD
measures sampling scatter *within one pose* and the pose stays a stated conditional. That is a limit to declare,
not a reason to stay at n = 1: **an error bar that covers one of two error sources beats no error bar at all**,
and n = 1 covers neither.

**The parked row on the IN FLIGHT board was therefore parked for TWO reasons and listed one.** The price gate is
real and its refusal was correct. But `s_resolvability_from_R_ternary` reads **ADMIT** on the landed
`R_ternary` — the *science* gate says buy — so if the market had opened the lane would have resumed **in the
configuration this item calls under-powered.** ✅ **SETTLED 2026-07-30 (trimcrae go): n = 2 seeds per arm.** The
lane now declares four legs, the ladder is regenerated, the stage-cache seeder covers every declared seed and
both new units are watched — all still `enabled: false` behind the price gate, re-enabling together.
[§Open decisions 11](#open-decisions) carries the reasoning and what was NOT chosen.

### 4 · ✅ FIXED — a REQUIREMENT this file adopted had never been implemented on the driver whose loss created it

RUNG 3 records *"the highest-leverage infrastructure change for the whole ternary program (adopted as a
requirement, 2026-07-25): every MD driver must persist a strided heavy-atom TRAJECTORY"*, because the NR-V04
panel's three data-invalidating defects would each have been correctable for **$0** instead of costing a re-run.
**Measured against the source on 2026-07-30, ten months of that requirement had produced nothing on the one
driver that needed it: `nrv04_covalent_md.py` had no trajectory reporter at all** — it reduces in-loop and
discards positions, which is the exact mechanism `nrv04_result_forensics` recorded as
`trajectory_objects_found: 0`. Every other endpoint-MD lane at least writes one — `nr4a3_md`, `nr4a3_metad`,
`nr4a3_md_release` and `nr4a_paralogue_release` all attach a `DCDReporter` into the job's output directory, and
`nr4a_paralogue_release` documents an explicit strided heavy-atom persist. ⚠ **Stated at what was actually
checked: that is a reporter, not an audited end-to-end persist for all four** — the claim here is only that the
lane which lost everything had no reporter at all.
**And the NR-V04 retrospective SHARES THAT DRIVER**, so the 18-leg holdout would have repeated the
irrecoverability that retired the panel it descends from.

**✅ BUILT AND WIRED 2026-07-30, $0** — [`md_analysis_traj.py`](research/modalities/md_analysis_traj.py),
mirrored to S3 on the driver's existing per-checkpoint hook (upload-as-written, per CLAUDE.md's checkpoint
rule) and with its own receipt in every leg's result JSON, so a leg that silently failed to persist coordinates
is visible in the artifact the collector already reads. 11 tests, all runnable in the dev sandbox.
**⚠ IT IS DELIBERATELY NOT A FULL HEAVY-ATOM TRAJECTORY, and the honest version of that is the point:** full
heavy-atom on a ~466k-atom solvated assembly is ~2.8 MB/frame, i.e. hundreds of MB per leg — outside the "tens
of MB against the ~112 MB System XML the driver already uploads" the requirement was costed at, which is
plausibly why it was adopted and never done. What ships instead is the **closure of the atoms every readout in
this lane consumes** — every protein CA, every Cys SG, every Lys NZ, every non-polymer heavy atom — at ~1k
atoms and single-digit MB per leg. **All three historical defects become $0 re-derivations** (a test asserts
exactly that, atom by atom); an analysis nobody anticipated over a dropped sidechain does not, and
`select_analysis_atoms(all_heavy=True)` is there for a leg that can afford the bytes. **The cheap 95 %,
labelled as such in the file's own manifest**, beats a complete record that stays unwritten.

### 5 · ✅ RESOLVED — the NR-V04 retrospective's own gate could no longer be satisfied by anything

Its **Gate** reads *"Val B-full + NR-V04 feasibility + Step 1 fan-out."* The fan-out is **DONE**; the
feasibility panel is **WITHDRAWN**, not merely paused; and valB_full sits behind a module-1 gate that
[§Open decisions 9](#open-decisions) has just **declined to amend, correctly**. Two of the three preconditions
are therefore not pending — they are **unreachable**. An item that is "built, preregistered and idle" behind a
gate that cannot fire is not being held; it is being **abandoned without saying so**, which is the failure mode
this file's own §Current front paragraph was corrected for. **It needed a decision either way**, and it got one:
✅ **2026-07-30 (trimcrae go) — Arm E RUNS, Arm F stays blocked on the valB PASS.** ⚠ **And my framing was wrong
in a way worth keeping: I proposed this as a scope correction I had derived, and the prereg's own §9
"Dependency honesty" had made the same argument on 2026-07-24** and left the judgement open — so no criterion
is amended and none needed to be. [§Open decisions 12](#open-decisions).

### 6 · Ranking what is left by DECISION VALUE PER DOLLAR — not by dollars

*Cheapest-decisive-first is a rule about **decisiveness ÷ cost**, and the ladder has lately been ordered on the
denominator alone. The lane that spent the most this month (~$74, the fan-out) returned a **single-conformer,
single-replicate, one-cycle-open** map that the paper can only report as provisional, while the three items
that could change what the program CONCLUDES cost $0, $0 and low-tens-of-dollars and are unbought. That is not
an argument the fan-out was wrong — it is §2.9 and it is real — it is an argument about **ordering**, and it is
the ordering below.*

| rank | what | $ | why it ranks here |
|---|---|---|---|
| 1 | **Re-anchor the paper's resolvability argument on the measured SD** | **$0** | The paper currently states the *assumed* SD in §2.10/§4/§5 while **reporting the measured one in §2.11** — one fact, two values, in one document. Done in this pass |
| 2 | ~~**Wire the strided-trajectory requirement into `nrv04_covalent_md`**~~ ✅ **DONE 2026-07-30** | **$0** | Item 4. It was a hard precondition on the only built-and-unlaunched GPU item we own, and it is now met |
| 3 | ~~**Settle the `S` replicate count BEFORE the market re-opens**~~ ✅ **DONE — n = 2 per arm** | **$0 to decide** | Item 3. The lane would otherwise have resumed under-powered the moment price allowed |
| 4 | **`S` at n = 2 per arm** — the flagship kill-switch, correctly sized and now CONFIGURED | **~$23** (ladder) | The only unrun test of the program's headline causal claim, and the second seed is what makes its *likely* answer readable. Waiting on the market, not on a decision |
| 5 | **NR-V04 retrospective, Arm E (R1 only, 16 legs)** ✅ **RUNNING** — *was "18 legs", superseded by prereg AMENDMENT 4 (2026-07-31): `nr4a3` co-fold seed 3 excluded by measured input fault (0.181 Å heavy-atom clash), so n = 3/3/2* | **≈$7.7** | A *new axis of evidence* (biological holdout), built and preregistered, with a registered MDE — CLAUDE.md §5's "default YES". The gate is reconciled to the prereg and the durable-trajectory precondition is met |
| 6 | ~~**Segment-grid re-enumeration** (5b)~~ ✅ **DONE 2026-07-30 — and it refuted its own premise** | **$0** | Neither a grid limit nor geometry: the chain template carries **one pendant**. A two-branch template is constructible at n = 18 with existing segments, but that is a DESIGN change to a preregistered enumeration and is not taken here |
| 7 | **Replicates on the open cycle** (3 of 18 fan-out edges) | **~$25** | One purchase, two open caveats: it attributes or dissolves `cycle_3carbonyl`'s violation AND gives the binary lane its first measured replicate SD, which today is transferred from the ternary lane |
| 8 | **The generative arm of the generation-matched null** (control c) — ✅ **$0 prep DONE, launch-ready** | **PROJECTED** | Addresses the confound actually raised (the GENERATIVE step); the arm that ran addresses the SELECTION step and bounds the manufactured rate at 3× the real campaign's own — narrowed, not excluded |
| 9 | **A known-answer calibrator for the `S`-shaped quantity** | **unpriced** | The real gap [Open decision 9](#open-decisions) exposed. It unlocks nothing on its own and must obey decision 9b's binding requirement (reference data and structure on the **same** protein), so it follows 4 rather than leading it |
| — | **More replicates on `ΔΔG_coop` / a rescoped valB edge** | — | **Explicitly NOT on this list.** `R` says the miss is endpoint-state; replicates shrink variance, not bias; [decision 6](#open-decisions) closed it |

*(Ranks 6–8 were added on 2026-07-30 — they are not new discoveries, they are items that had been sitting as
prose in a deliverable table or a §2.9 caveat with no rung, no price and no gate. **A caveat with nowhere to go
is how work gets silently dropped**, which is the same failure this section's item 5 names for the
retrospective. They now have entries in the ordered plan.)*

**★ AND THE PAPER IS CLOSER TO SHIPPABLE THAN THE LADDER IMPLIES.** Ranks 1–3 are **$0**, ranks 4–5 together
are **low tens of dollars**, and the flagship's tail (5c + 5d, priced in their own rung entries — not restated
here) is gated behind a causal result that rank 4 either delivers or honestly bounds. **Nothing on this list is
a multi-hundred-dollar commitment**, and no item above needs the prospective NR4A ternary matrix that
[decision 9](#open-decisions) correctly left locked. ⚠ **The corollary is a stopping condition, and it is worth
stating because "state of the art" can drift into "never finish":** once rank 4 reads out, **every result the
paper's current claims rest on has either landed or been honestly bounded** — what remains after that is the
tail that a *positive* `S` would unlock, and a paper reporting a bounded null does not wait for it.

---

## Current front

*★ **APPENDIX — superseded by the roadmap §10, retained for one statement.** ⚠ This section has **zero** inbound references and names its own homes for everything it says. The one thing it owns is the sharpest statement of the feasibility panel's status — **WITHDRAWN**, not merely "under correction" — which contradicts the ordered plan's `[!]` marker and the schedule JSON, and is recorded as [roadmap](research/manuscripts/nr4a3-program-map.md) §12 finding 12.*

Rungs 0–1 are done. The Tier-0 unique-residue map and the differential atlas are done ($0, both PASS). The
NR-V04 covalent feasibility panel is **WITHDRAWN** — not merely "under correction". Its GO was never
produced by the frozen scoring rule, its inputs were contaminated, and no trajectory survives to re-derive from,
so its re-run is **`[HELD]`** pending a prereg amendment. It gates nothing.

**NOTHING IS BILLING.** All three lanes that were running closed on 2026-07-30 — the **Step 1 fan-out** (19
congeneric RBFE edges), the **valB_mini replicates** (4 legs) and the **closure triangle**, whose `R` landed at
5:11 PM ET and was the last owed GPU work in the fixed scope. **Two lanes remain held, deliberately and for
stated reasons**: RUNG **5a-KS** behind the relaunch price gate, and the **restrained binary re-run** behind
the triangle's `R` — which has now landed, so what that leg is waiting on is a *reading*, not a run. Live
state, cost and `$/ns` for every one of them: the **IN FLIGHT** board at the top of this file, which is their
one home — ⚠ **and this paragraph must never restate it.** It said *"three lanes are billing"* for a day after
the board said nothing was, which is a rule-1 defect in the one direction that matters, since a stale
"currently spending" line is what an unattended fleet looks like when it is *not* being supervised.

**Built and idle, awaiting a go or a decision:**
- **The NR-V04 retrospective** — built, preregistered, never launched; next launch is a pilot, not a fan-out.
  ⚠ **"Awaiting a go" overstates it, and the correction is the point:** its own gate names two preconditions
  that are **unreachable**, and its driver does not meet a requirement this file adopted. Both are in
  [§WHAT THE LANDED RESULTS CHANGE](#-what-the-landed-results-change-about-the-remaining-plan) 4–5;
  the decision is [§Open decisions 12](#open-decisions).

**★ WHAT IS ACTUALLY NEXT is not on this page.** This section says what is *idle*; it has never said what to do
first, and while the fixed scope was closing that gap did not matter. It does now — nothing is billing, so the
next thing to happen is a *choice* rather than a result landing. The ranked list, the reasoning and the prices
are in [§WHAT THE LANDED RESULTS CHANGE](#-what-the-landed-results-change-about-the-remaining-plan) 6,
which is their one home; **this paragraph deliberately does not restate the order.**

**Closed earlier:** the 5a-KS confirmatory protein-mutation benchmark **qualified** (RUNG 5a-KS), moving the
ladder's only unscoped rung from UNPRICED to *projected*. Nothing with a GPU price launches without an explicit
go, and every rental — fan-out, resume or single cold unit — now faces the buy line as well as its rung's
dollar ceiling.

## Open decisions

*★ **APPENDIX — the decision register.** 15 numbered rulings, all closed. ⚠ **Cited by number in 30 files and nothing resolves a decision number** — the numbering is **frozen**. Roadmap rows cite these by number.*

1. **`[x]` ADOPTED — method calibrator swapped from NR-V04 to SMARCA2-vs-SMARCA4** (valB_full module 3). NR-V04
   stays the biological holdout; its selectivity is most plausibly covalent target engagement, and SMARCA2/4 is
   already staged in-repo.
2. **`[x]` ADOPTED — the protein-mutation wedge is demoted from primary to confirmatory.** The ligand-side double
   difference is the paper's headline causal evidence and runs on the lane Val B already has an accuracy control
   for. The mutation cycle is kept, not deleted: its benchmark has now passed. ⚠ **The clause that stood here —
   *"so the paper can have two independent causal lines"* — is WITHDRAWN (2026-07-30):** the mutation cycle is
   a **ternary-minus-binary contrast, structurally the quantity that failed**, so it is a second line but not an
   independent one. Algebra and consequences: [Open decisions 10](#open-decisions).
3. **`[x]` DECIDED — adopt 4 fs, but TWO-STAGE**, sequenced after valB_mini's 2 fs result (RUNG 2b).
4. **`[x]` REVERSED — the step1 fan-out was RESUMED on 2026-07-26 and is running.** The hold below is
   **superseded**; it is kept because its reasoning is still the right reasoning and would apply again to any
   *new* edge list.
   *Superseded text, do not cite as current:* **"HOLD the step1 fan-out; do NOT resume the 19-edge tranche"**,
   on a *scientific* reason independent of price — under mechanism-first the fan-out's **selection criterion**
   had changed, the exit vector must now carry a linker toward **C397** (10.9 Å) and orient the E3 so the
   transfer zone covers **K572/K518/K592**, which is not the same as ranking substituents by affinity, so
   resuming the old edge list would spend ~$36 optimising the wrong objective; and nothing was lost by
   re-scoping because **0/19 units had produced a ΔΔG**.
   **What retired it:** the 5a basin search — the $0 step the hold was waiting on — **completed**, and the two
   preconditions it was protecting are now met. The lane also ceased to be a $36 all-or-nothing bet: placement
   is **per unit** and gated on `$/ns`, so it buys only what the market sells inside the buy line and holds the
   rest, and the cycle-closure edges are in the queue rather than stranded in a last wave. The rung entry under
   RUNG 4 carries the live status.
5. **`[x]` CLOSED — raising `GPUS_ALL_REGIONS` is NOT available to us.** trimcrae, 2026-07-26: *"We've tried
   over and over for more quota. They won't give it to a small account like ours."* Repeatedly requested,
   repeatedly refused. **Do not re-file it, and do not plan around a quota that is not coming.** (I raised it as
   an ask the same day, quantified at 1→4; withdrawn — see [Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) row 20.)

   **AND A FASTER GPU WOULD NOT HELP EITHER — because the GCP lane is DOLLAR-bound, not time-bound.** Asked and
   answered 2026-07-26 rather than assumed. From [credit-status.json](research/compute/credit-status.json): cap
   **$300**, spent **$8**, so **~$292 remains** against a 2026-10-10 expiry.

   | | value |
   |---|---|
   | one full ternary leg (2800 iters × 56.5 s) | **43.9 L4-h ≈ $31** |
   | credit runway | **~411 L4-h ≈ 17 days continuous ≈ 9.4 full legs** |
   | calendar available | 76 days ≈ 1,824 h of single-GPU wall clock |

   The credit is exhausted after ~17 days of continuous running inside a 76-day window, so **calendar is not
   scarce — money is.** And science-per-dollar is `speed / rate`, which is flat-to-worse on faster cards
   *(non-L4 rates are list-price approximations, not repo-measured)*:

   ⛔ **SUPERSEDED 2026-07-31 — the non-L4 rows of BOTH tables below are WITHDRAWN, do not cite them as
   current; the correction is beneath them and in [Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) row 56.**

   | card | rel. speed | ~$/h | units/$ | leg-equivalents on $292 |
   |---|---|---|---|---|
   | **L4 (current)** | 1.0× | 0.71 | **1.41** | **9.4** |
   | A100 40 GB | ~5.2× | 3.67 | 1.41 | 9.4 |
   | V100 ⛔ *superseded* | ~3.0× | 2.48 | 1.21 | 8.0 |
   | H100 80 GB | ~11× | 11.0 | 1.02 | 6.7 |

   **★ BUT THE CENSUS CHANGED THE ANSWER, AND NO REQUEST IS NEEDED FOR ANY OF IT.** `GPUS_ALL_REGIONS = 1` caps
   the **count**; the **per-type** quotas say which card, and several are **already granted at limit 1** —
   `NVIDIA_V100_GPUS`, `NVIDIA_P100_GPUS`, `NVIDIA_T4_GPUS`, `NVIDIA_P4_GPUS`, `NVIDIA_K80_GPUS` alongside
   `NVIDIA_L4_GPUS` (A100/H100 are the only ones at 0). Nobody had looked, because the quota check only grepped
   `L4|G2|GPU` and printed the rows mid-log. Spec-derived against the ~$292:

   ⛔ **SUPERSEDED 2026-07-31 — WITHDRAWN, do not cite; see beneath the table.**

   | card | quota | ~×L4 | ~$/h | ~$/leg | legs on $292 | science/$ |
   |---|---|---|---|---|---|---|
   | L4 (current) | 1 | 1.00 | 0.71 | 31 | 9.4 | 1.41 |
   | **P100** ⛔ *superseded* | **1** | ~2.4 | 1.46 | **26** | **11.1** | **1.67** |
   | V100 ⛔ *superseded* | 1 | ~3.0 | 2.48 | 36 | 8.0 | 1.21 |
   | T4 ⛔ *superseded* | 1 | ~1.1 | 0.35 | 14 | 20.3 | 3.05 |

   ⛔ **SUPERSEDED BY MEASUREMENT, 2026-07-31 — DO NOT CITE EITHER TABLE ABOVE AS CURRENT.** The reading they
   supported — *"P100 looks better than L4 on BOTH axes, faster and more science per dollar, i.e. **+18 % more
   legs from the same money**"*, and the T4 at **2.2×** the L4's science-per-dollar — is **WITHDRAWN**. It was
   never measured, it was flagged as unmeasured, and the measurement has now refuted the heuristic that
   produced it. Retained above because it is what the plan carried for five days;
   [Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) row 56 has the correction.

   **★★ WHAT THE PROBE MEASURED, AND WHY IT INVERTS THE TABLE.** Built and run 2026-07-31 on free trial credit
   (`gpu-bench-gcp.yml` + [`gcp_card_bench.py`](research/modalities/gcp_card_bench.py)); one home for every
   number is [`gcp-card-bench.json`](research/modalities/gcp-card-bench.json), and the readable table with its
   full caveats is **[gcp-gpu-facts.md §1c](research/compute/gcp-gpu-facts.md)**. Do not copy figures here —
   point at those.

   1. **THE WORKLOAD IS COMPUTE-BOUND, NOT BANDWIDTH-BOUND — and that is the whole ballgame.** The T4 is the
      discriminating card precisely because its two specs point opposite ways (bandwidth 320 vs the L4's 300,
      FP32 8.1 vs 30.3 TFLOPS). Bandwidth predicts **1.07× L4**; FP32 predicts **0.27×**. **Measured: ~0.31×**
      at the ternary system size. So every row generated by the bandwidth heuristic — P100 and V100 included —
      rests on a premise the measurement rejects.
   2. **THE SPEC TABLE ALSO HAD A PRICE ERROR THAT NEEDED NO MEASUREMENT AT ALL.** Its `$/h` column compares
      the L4's **whole-VM** rate (0.71 = a g2-standard-4, which *bundles* the L4) against **bare GPU** rates
      for the others (1.46 / 2.48 / 0.35). A P100 cannot run without a host. Adding the n1-standard-4 it needs
      (**$0.190/h**) to the same table, with its own speed assumptions untouched, already collapses P100's
      advantage from **+18 % to +3 %** and the T4's from **2.16× to 1.44×**. Two independent errors, both in
      the direction that made the alternatives look good.
   3. **THE PRACTICAL ANSWER: STAY ON THE L4.** Combining the two, the T4 delivers **~0.41×** the L4's
      science-per-dollar where the table promised 2.2× — wrong by **~5×**, and in the direction that would have
      sent the next GCP leg to the worst card available. The original framing of this decision — *"a faster GPU
      would not help either, because the GCP lane is DOLLAR-bound"* — **survives, and is now measured rather
      than assumed.**

   ⚠ **WHAT IS STILL NOT MEASURED, stated so nobody over-reads this.** The T4 figure was **REFUSED by the
   probe's own admission gate** (CV 5.6 % against a 5 % ceiling) and is reported as a *ranking*, not a rate —
   a 3.5× discrepancy cannot be manufactured by 5.6 % of block scatter, but the number itself is provisional.
   Capacity also intervened: `NVIDIA_T4_GPUS` on-demand returned **`ZONE_RESOURCE_POOL_EXHAUSTED` in all four
   us-central1 zones**, so the T4 arm had to run on spot ([facts §1d](research/compute/gcp-gpu-facts.md)).
   **A granted per-type quota is not capacity** — that is new, and it is the one respect in which "we already
   hold quota for several GPU types" oversold itself.

   **What no longer holds: "buy the probe together with the first GCP leg that is actually queued."** That was
   right while the probe was hypothetical and the answer had no consumer. It is now bought and the answer
   exists, so the sequencing question is closed rather than deferred.

   **What stands regardless: no GPU quota REQUEST is worth filing** — not more count (refused, and wouldn't have
   helped), and not a faster type (we already hold several). ⚠ This also means the quota increase I
   proposed would not have helped **even if Google had granted it**: at 4 GPUs the same $292 is spent 4× faster,
   not turned into 4× the science. That table's central claim was wrong independently of the refusal — see
   [Appendix A](#appendix-a--superseded-numbers-and-retracted-claims) row 20.

   **THE REAL BUDGET, and the number to plan the rescope against: ~$292 ≈ 9 more full ternary legs on GCP.**
   The lane split still holds and is still not a cost question — GCP free/serial/1-GPU at ~56.5 s/iter, Vast paid/
   parallel at ~16 s/iter (**3.53×**, corrected from the 2.06× in pricing.md, which compared an L4 *warmup* rate
   against a 4090 *production* rate). Every idle GCP-GPU minute is still expiring credit lost, so keeping that one
   GPU fed still matters — it just cannot be fed for more than ~411 hours in total.

6. **`[x]` CLOSED 2026-07-30 — the valB_mini rescope. `R` answered it, and the answer is that no rescope of
   this calibrator's EDGE can help.** *(It was held until the reverse leg read out; that landed 2026-07-28, and
   the closure triangle then produced `R`.)* Every rescope variant was a search for a better **edge** — a bigger
   signal, a cleaner replicate SD, the P-series network. **`R ≈ 0` says the miss is an ENDPOINT-STATE error**,
   which telescopes out of any cycle and is a property of the **model or the reference data**, not of which edge
   sits on top of them. Changing the edge changes neither. The live successor is a **system** question, not an
   edge question — [decision 9](#open-decisions) and its $0 survey of paralogue-selective systems with a solved
   structure on **both** arms. *(Superseded framings retained: the P-series congeneric network, refuted for $0
   on charge/heavy-atom grounds; and the synthetic closure triangle, which was not a rescope in the end but the
   diagnostic that closed this item.)*
7. **`[x]` RESOLVED 2026-07-30 — the admits-zero gate defect. It never touched valB's verdict, and it is now a
   BINDING REQUIREMENT ON THE NEXT CALIBRATOR rather than a retrospective amendment. $0.** The frozen gate
   accepts a method that predicts no cooperativity change (**22 % vs 23 %** — a gate you can pass by predicting
   nothing). Two things settle it. **(a) It is moot for valB_mini**, which failed on **SIGN**, before the
   `|mean − target| ≤ 1.0` band was ever consulted — so no amendment could change that verdict and none is
   sought, which is exactly why this is not the forbidden retune. **(b) It is NOT moot going forward**, because
   any future calibrator reusing this gate design inherits it. **It therefore binds the S-calibrator spec
   ([decision 9](#open-decisions)): no accuracy band wider than the signal being calibrated, and a stated
   null-rejection rate up front.** The 22 %/23 % measurement is the evidence for that requirement; the frozen
   valB gate itself is left **unamended**, on the record, failed on sign.
8. **`[x]` RESOLVED 2026-07-30 — the `UNDERPOWERED` proxy. $0, LOW STAKES, and it is low-stakes because the measurement says
   so.** `binary_departure_prereg` demotes a null closure to `UNDERPOWERED` whenever `sigma_leg > 0.2` — a
   threshold hand-set when `sigma_leg` was unknown to a factor of 15.6, i.e. a proxy chosen because the power
   itself was not computable. **It is computable now, and it VINDICATES the proxy:** bisecting the design's own
   power curve puts a conventional 0.80-power threshold at `sigma_leg ≈ 0.216` against the frozen **0.200** —
   agreement to ~7 %. ⚠ **So amending it would NOT rescue a null `R`**: at the measured upper bound the power
   is ~0.63, which a conventional threshold demotes anyway. **Proposed fix is therefore transparency, not
   correction** — report the computed power *beside* the verdict, keeping the demotion rule, because
   "UNDERPOWERED" currently cannot distinguish power 0.63 from 0.05 and those warrant different responses.
   Evidence: [`valb_failure_propagation.frozen_rule_vs_measured_power`](research/modalities/valb_failure_propagation.py).
   **Same standard as item 6 and it is why nothing was changed:** a rule may be amended only if its statistic
   is shown to lack discriminating power, demonstrated independently of whether we like its answer — and here
   the statistic turned out **not** to lack it. Written down **before `R` landed**.
   **★ THE LIVE QUESTION IS NOT THIS RULE — IT IS WHERE `sigma_leg` ACTUALLY SITS.** The crossing (≈0.216) lies
   *inside* the bounded interval [0.045, 0.265], so a null `R` is readable or not depending on the true value,
   and the bound is an UPPER bound. **That is settleable for $0 from the triangle's OWN legs when they land** —
   `valb_failure_propagation.narrow_sigma_leg_from_triangle_legs` applies the n=3-measured replicate-SD/MBAR-SE
   ratio to the triangle's own per-leg MBAR SEs, giving an estimate with no homology-model and no cross-seed
   solvation term. ⚠ The ratio is **transferred, not measured on the triangle** (which has no replicates), so
   this narrows the interval and must never be reported as though the triangle had replicates.
9b. **`[x]` DONE 2026-07-30 — decision 9's $0 survey RAN, and it answered more than it was asked.
   Artifact: [`s-calibrator-survey.json`](research/modalities/s-calibrator-survey.json)
   (generator [`s_calibrator_survey.py`](research/modalities/s_calibrator_survey.py)); every PDB ID is fetched
   from RCSB, never typed.** Ten candidate paralogue pairs screened on whether a deposited **ternary** exists
   on **both** arms. **2 of 10 are symmetric: SMARCA2/SMARCA4 and IKZF1/IKZF3.** The incumbent therefore
   **survives its own screen** and decision 9 forces no system change. Two pairs would have been traps —
   **BRD4 has 24 ternary structures while BRD2 and BRD3 have zero**, so either BET pairing puts a modelled arm
   opposite a real one, the exact configuration decision 9 exists to avoid.
   **★ THE FINDING THAT MATTERS MOST WAS NOT THE QUESTION ASKED, AND IT IS A CORRECTION.** A first reading of
   this survey said the lane's SMARCA4→SMARCA2 homology substitution "was avoidable". ⚠ **It was not — not for
   this ligand.** 8G1Q's own deposition title is *"Compound 1 … bromodomain of human **SMARCA4** and
   pVHL:ElonginC:ElonginB"*: Wurz **compound 1**, the calibrator's `calib_hi`, was co-crystallised **only** with
   SMARCA4. Every deposited SMARCA2 ternary carries a **different ligand** (8G1P = Compound 11, 6HAX = PROTAC 2,
   6HAY = PROTAC 1, 9HYB = P-series P3). Keeping the ligand whose SPR α values **are** the reference data
   therefore *forced* the substitution.
   **What the choice cost is the real result: the calibrator is built on the LOWEST-RESOLUTION structure in the
   family — 3.73 Å — AND on the wrong paralogue, while SMARCA2 ternaries exist at 2.24–2.84 Å.**
   Ligand-identity and protein-identity are **coupled** here, and the lane resolved that coupling in favour of
   the ligand. **`R` has since localised the valB miss to the model or the reference data — and both candidate
   causes trace to that one coupled choice.** Binding consequence for the S-calibrator spec: **pick a pair
   whose reference data and structure sit on the SAME protein**, rather than buying reference data at the price
   of a modelled arm. *(Not established and not claimed: that a different template would change the
   calibrator's answer. A shared deposition series does not make two entries interchangeable.)*

9. **`[x]` DECIDED 2026-07-30 (trimcrae delegated: *"You make an educated call yourself"*) — the valB_full gate
   is NOT amended, and module 3 is NOT decoupled to unlock it.** The question was whether module 3 (paralogue
   discrimination, SMARCA2-vs-SMARCA4) should be freed from behind the failed cooperativity gate now that `R`
   says the ternary environment is internally clean. **It should not.** Module 1's statistic did not *lack
   discriminating power* — it discriminated perfectly well and returned NO — so the repo's own amendment
   standard ([AMENDMENT 1](research/modalities/nr4a3-nrv04-covalent-feasibility-prereg.md#amendment-1--2026-07-25-dated-defect-fix-trimcrae-delegated))
   does not reach it; and `R` supplies no licence either, because `R` is **blind to the endpoint-state class
   that broke valB**. Unlocking the prospective ladder here would be the retune this program forbids, wearing
   a diagnosis as cover. **The prospective NR4A ternary matrix stays unrun and cooperativity claims stay
   exploratory.**
   **★ THE REAL FINDING IS A GAP, NOT A GATE IN THE WAY.** `S` — the flagship kill-switch the whole prospective
   stage turns on — **has never had a known-answer calibrator**, because valB_mini calibrated `ΔΔG_coop`, a
   quantity `S` does not contain (its binary leg cancels algebraically). The failure *exposed* that; it did not
   cause it. Closing it is a **new item**, not a gate amendment, and it unlocks **nothing** beyond whether `S`
   may be read as calibrated rather than exploratory. Reasoning + what must be preregistered first:
   [`valb_failure_propagation.module3_decision`](research/modalities/valb_failure_propagation.py).
   ⚠ **The strongest argument against, recorded because it must be preregistered rather than discovered:** an
   S-calibrator on SMARCA2-vs-SMARCA4 runs on the **same system family carrying the suspected error**, and a
   known-answer accuracy test does *not* telescope an endpoint-state error the way a cycle does — which is
   precisely why valB_mini caught it. The arms are also **asymmetric**: 8G1Q is a *SMARCA4* structure and
   SMARCA2 is the homology-substituted arm, so a homology-model error sits on **one arm and does not cancel**.
   A failure would then be ambiguous between *"the S-class quantity does not work"* and *"this benchmark
   inherited the same model defect."* **So the system must be chosen on which arm is REAL, not on what is
   already staged** — and the $0 survey of paralogue-selective systems with a solved structure on *both* arms
   leads, before any spend.
10. **`[x]` RESOLVED 2026-07-30 — the protein-mutation cycle is no longer called an independent second causal line.
   $0.** RUNG 5's CONFIRMATORY cycle is `ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary` — a
   **ternary-minus-binary contrast, structurally identical to the quantity that failed** (the PRIMARY `S`
   escapes this only because its binary leg cancels *algebraically*; a protein mutation changes the target,
   which is exactly what the two environments differ by). Its known-answer benchmark passed on a
   *protein-mutation* quantity, **not** on a ternary-minus-binary one, so that pass does not cover this
   exposure. Consequence: a concordance between `S` and this cycle is **not two independent lines agreeing**,
   and a discordance would be uninterpretable. Derived in
   [`valb_failure_propagation.error_algebra`](research/modalities/valb_failure_propagation.py). *Not
   load-bearing* — the paper's headline causal result is already stated as not hostage to it.
11. **`[x]` DECIDED 2026-07-30 (trimcrae go) — `S` GETS n = 2 SEEDS PER ARM (4 ternary legs).**
    The lane is re-specified and the ladder regenerated: `ternary_vast_launch.MODES['5aks']` declares four
    legs, `vast_cost_model` prices four, the stage-cache seeder now seeds **every declared seed** (it seeded
    only seed 0, and `5aks` sets `stage_required: True`, so a seed-1 leg would have died on a cache MISS on a
    rented host), and both new units are on the watch list rather than launching unwatched. **Nothing is
    bought yet** — all four stay `enabled: false` behind the relaunch price gate and re-enable **together**,
    because a partial re-enable buys a number that still cannot report a null.
    ⚠ *The two parked seed-0 legs are untouched and resume byte-identically from `production/800` and
    `warmup/640`; the seed-1 legs are cold starts.* The question, as it stood:

    **`[~]` HOW MANY SEEDS PER ARM DOES `S` GET? This is trimcrae's, because it is a multi-leg GPU
    spend; everything else about it is settled and free.** ⚠ **It must be settled BEFORE the market re-opens,
    not after**: the relaunch price gate is the only thing currently holding the lane, and `R_ternary` already
    reads **ADMIT** on the science gate — so the next cheap offer resumes 5a-KS in the **n = 1 per arm**
    configuration that
    [§WHAT THE LANDED RESULTS CHANGE](#-what-the-landed-results-change-about-the-remaining-plan) 3
    shows cannot report its own likely answer.
    **RECOMMENDED — n = 2 per arm (4 legs; the 2 parked legs plus 2 more), for roughly double the parked
    ladder figure.** The reasoning is this repo's own litmus test, applied to the *design* instead of the
    sequence: *is there a result the extra pair could return that changes what we do?* **Yes — a readable
    null.** The pre-registered expectation is that the effect sits inside the range `S` can only half-resolve
    at n = 1, so the increment is what converts the **likely** outcome from an uninterpretable non-result into
    a **publishable bounded negative** — the same argument that made valB-mini "the highest-value dollar in
    the plan", now applied to the test valB-mini was supposed to certify. The $0 machinery check is **done**
    and favourable (item 3); the seeds are genuinely independent.
    **The alternatives, stated fairly.** *(a) Finish as parked (n = 1, ~$12 total, ~$1.5 already banked):*
    cheapest, retires the paper's *"the causal test has not been run"*, and is enough **if** `S` comes back
    large. Its failure mode is the likely case. *(b) n = 3 per arm (6 legs):* the repo's stated replicate
    standard, and it brings the resolvable difference down to the figure in §MECHANISM-FIRST — but the second
    seed buys most of the readability and the third is the shallow part of a `1/√n` curve, so it is the
    "deepening past field standard" CLAUDE.md §5 defaults against. *(c) Don't buy:* defensible only if the
    paper is content to ship with its headline causal test unrun, which contradicts the North Star.
    **What I would do, and would not do without a nod:** buy (b)-minus — the 2 parked legs plus 2 more, at
    n = 2 — and read a null as a bound rather than an absence. **Not proposed:** re-running the parked legs
    from scratch (their checkpoints are intact and durable) or extending them (more sampling on one seed buys
    precision that `S` does not lack).
12. **`[x]` DECIDED 2026-07-30 (trimcrae go) — THE NR-V04 RETROSPECTIVE RUNS: ARM E (R1, 18 legs, ≈$8). *(count SUPERSEDED by prereg AMENDMENT 4, 2026-07-31: **16 legs** — `nr4a3` co-fold seed 3 excluded by measured input fault)*.
    Arm F stays blocked on the valB PASS.** ⚠ **AND MY FRAMING OF THIS WAS WRONG IN A WAY WORTH
    CORRECTING: I proposed it as a scope correction I had derived, and the prereg had already made the
    same argument on 2026-07-24.** Its **§9 "Dependency honesty"** states that the gates govern the
    free-energy arm, that Arm E asserts no free energy, and that running Arm E is a *narrowing* rather
    than a gate jump — then names the alternative (hold Arm E until valB passes) and leaves the
    judgement open. So no criterion is amended and no amendment was needed; the decision is recorded as
    a **dated addition** in the prereg, which is what §9 itself asks for. The gate wording that
    conflicted was **this file's**, and it is reconciled in the RUNG 4 entry. What genuinely changed
    since 2026-07-24 is the premise: `step1_fanout` completed and the feasibility panel was WITHDRAWN,
    so two of three gates became **unreachable** rather than pending. **Integrity test, checkable
    rather than rhetorical: the panel has never run, so no result exists that this could have been
    motivated by disliking** — the distinction from [decision 9](#open-decisions), where a real NO
    existed and the gate was correctly left standing. **Precondition met** (durable trajectory).
    The question, as it stood:

    **`[~]` DOES THE NR-V04 RETROSPECTIVE RUN, OR IS IT FORMALLY RETIRED? It cannot stay "idle".**
    Its gate names **valB_full** and the **NR-V04 feasibility panel**; the first is behind a module-1 gate
    [decision 9](#open-decisions) has just declined to amend, and the second is **WITHDRAWN**. Neither is
    coming. Leaving it listed as built-and-awaiting-a-go is the *appearance* of a plan for ~$7.7 of work that
    nothing can authorise.
    **RECOMMENDED — a SCOPE correction to the gate, not an amendment to a rule, and only after the $0
    precondition below.** The argument, and it is deliberately narrow: **valB calibrates the ternary-FEP
    cooperativity lane, and the retrospective's authorised readout (`R1`, Arm E, 18 legs — *(count SUPERSEDED by prereg AMENDMENT 4, 2026-07-31: **16 legs** — `nr4a3` co-fold seed 3 excluded by measured input fault)*) is not in that
    lane** — it is an **endpoint-MD geometric contrast reported in Ångström**, with its own registered MDE
    (leg-to-leg σ 0.855 Å, 80 % power at 1.5–2.0 Å) and its own preregistered *directional-concordance-only*
    claim ceiling. A gate that names a control which does not cover the quantity is a **scope** defect, and it
    reads as one in the direction that matters: this is a *biological holdout*, i.e. exactly the kind of **new
    axis of evidence** CLAUDE.md §5 defaults YES to. ⚠ **The integrity test it must pass, stated because the
    repo forbids the retune this could be mistaken for:** amending a gate after a failing result is forbidden
    — **but there is no result here to rescue.** The retrospective has never run, so no verdict exists that
    this correction could be motivated by disliking. That is the difference between this and
    [decision 9](#open-decisions), where a real NO existed and the gate was correctly left standing.
    **HARD PRECONDITION — ✅ NOW MET, $0.** The shared driver had to persist a durable trajectory first, because
    launching 18 legs on a driver that discards positions repeats, exactly, what made the parent panel
    unrecoverable. Built and wired 2026-07-30 (item 4 above), so **this decision is no longer blocked on
    engineering — only on the call.** **If the decision is no, retire it explicitly** with the reason on the
    record — a named retirement is a result; an indefinite hold is not.
13. **`[x]` SPLIT 2026-07-30 — the "`S` has no calibrator" gap is TWO items, and the free half is now DONE.**
    [Decision 9](#open-decisions) recorded the gap as one thing and left it unsequenced, which is why it never
    acquired a rung. It separates cleanly:
    - **(a) Can a null `S` be READ? — a power/MDE question, $0, and it needs no known answer at all.** It is
      arithmetic on measurements this program already owns, and it is what item 3 above just did. **Done.**
      This is the half that actually gates the 5a-KS spend, and it was never the expensive half.
    - **(b) Can a non-null `S` be called CALIBRATED? — a known-answer question, and it is the paid one.** It
      stays deferred, behind [decision 9b](#open-decisions)'s binding requirement (pick a pair whose reference
      data and structure sit on the **same** protein) and [decision 7](#open-decisions)'s (no accuracy band
      wider than the signal being calibrated). ⚠ **It does not gate item 11**, and conflating the two is what
      made the gap look unaffordable: a *bounded null* needs (a) only, and a bounded null is the
      pre-registered likely outcome.
    **Consequence for the ladder:** `S` may be bought and read as a **bound** now; it may not be reported as
    calibrated until (b) exists. Both statements can be true in the same paper, and saying so is cheaper and
    more honest than waiting for (b) to buy (a)'s answer.

---

## Appendix A — superseded numbers and retracted claims

*★ **APPENDIX — the correction ledger.** ⚠ **Rows are cited as data by 35 files** (`realised_spend.py` reads rows 35 and 38 as provenance) and `lint_consistency.is_cleared` treats this exact heading as a structural clear — **numbering and slug are frozen**. The [roadmap](research/manuscripts/nr4a3-program-map.md) §6 imports only the ~1-in-10 rows where an *approach* died, never a corrected value.*

*Kept so a correction is never silently dropped, and out of the live plan so it stops competing with it. Each
line: what was believed, and what retired it. Do not cite anything in this table.*

| # | superseded claim | what retired it |
|---|---|---|
| 1 | Ladder total **~$390 (~$170–610)**, then **~$240 (~$90–390)**, then **~$467 (~$249–685)**, then a stray **~$128 (~$36–381)** | Successively: the six cost levers; the measured per-edge work correction; the measured bid/selection policy. The **$128** was `bid-strategy.md` §6's table with the **5c row missing** — fixed there; the pinned total is **~$158 (~$44–578)**; the intermediate **~$185 (~$51–614)** was retired 2026-07-27 by the throughput re-anchoring (pricing.md Appendix T) |
| 2 | "The 4090 wins $/ns at every size (1549 / 669 / 175.6 vs 3090 72.5 @444k; 2.42× for ~9 % more $/hr)" — a **card** rule | The 23:08 2026-07-24 bench was **withdrawn** (single 0.9–4.5 s windows; it also ranked a 4080 SUPER above a 4090). Validated grid: 4090 755.36 / 4080 703.51 / 3090 359.36 ns/day → **2.10×**, and the cheapest 3090 floor is **8.8×** below the cheapest 4090. **Rank offers on all-in `$/ns`; the card is not the decision** |
| 3 | Bid = `min_bid × 1.1` / `× 1.5` / `× 1.9` / `× 1.25`; and a `P* = clamp(max(no-churn floor, √(m̂·d) or UCB_q), ≤ on-demand)` reservation-price/adaptive-UCB scheme | All four multipliers were live at once. The measured bid ladder showed `charged = min(bid, on-demand)`, so a premium is paid on **every** hour and cannot buy safety from on-demand renters; the ~20-min reload that justified `×1.9` was **self-inflicted** (our reaper DELETEd paused instances). The UCB scheme never reached the launch path. Current rule: **floor + staleness tick, capped at on-demand** ([bid-strategy.md](research/compute/bid-strategy.md) §7) |
| 4 | RBFE binary edge ≈ **5–6 GPU-h ≈ $0.6–1.4**; `step1_fanout` **$12–26**, then **$91–101** | The 5–6 GPU-h was a **public TYK2** rate (~5.2 s/iter) applied to the ~2.6× heavier cmpd19/NR4A3 complex (~13.6 s/iter on three hosts). Unit is **~13.7 ref GPU-h**. The $91–101 then used the **$0.35–0.39/hr** realized, which was a consequence of bidding `×1.5` on a `min_bid`-ranked offer, not the market. Current: **~$1.9/edge, ~$36 fan-out** |
| 5 | Ternary edge ≈ **$3–6**, then **$4–7**, then **$65–110**, then **$7–15** | Each of the first two treated **920 iterations as a full leg**; 920 = 23 × 40 is a **checkpoint boundary**, and that line was the **binary** arm. A leg is 400 equil + 2000 production = **2400 iterations**. The $65–110 came off a refuted 55-GPU-h AWS anchor (a leg that was ~65 % GPU-idle from 12× per-window am1bcc re-charging). Current: **~$8.8 ($3.2–22)** |
| 6 | Endpoint-MD leg **~$0.6/leg**, then **~$0.45**, then **~$0.26 on a 4090** (via the 2.42× ratio) | Completed 18-leg ledger gives ~$0.43/leg on a 3090; converted by the *validated* 2.102× ratio → **~1.38 ref GPU-h ≈ ~$0.19** |
| 7 | "**No ternary leg has ever run to completion**, so even the leg length is unverified" | valB_mini's ternary seed 0 reached **2000/2000** production iterations (convergence run 30157501491). The leg length is now observed. *Still true and still load-bearing:* **no ternary edge has completed end-to-end on a 4090**, so the Vast cost basis remains rate × leg length |
| 8 | "5a-KS is **UNPRICED and BLOCKED** — no protein-mutation FEP engine exists in this repo; scope one before RUNG 5 can be planned or priced" | True when written (OpenFE's RHTP maps **ligand** atoms only; the sole protein-mutation path, `nr4a3_resistance_ddg.py:53`, is PDBFixer + MM-GBSA, non-alchemical). The engine was then built (perses → retired as OpenEye-gated → pmx + GROMACS) and **passed its known-answer benchmark 2026-07-25**. The **primary** kill-switch never needed it — it is the ligand-side double difference at ~$12 |
| 9 | NR-V04 covalent panel science: recruiter_active **3/3** stable vs epimer **1/3**; covalent NR4A1 **2/3** = noncovalent **2/3**; C551A **1/3** | Retired **three times over** (2026-07-25): the split was **positional** and selected Elongin C, so the numbers describe the wrong interface; the **inputs were contaminated** (14-3-3 epsilon in place of Elongin B, source pinned to `nrv04-descriptive-v3/nr4a1/seed_1` at CA-Kabsch **RMSD 0.000 Å**); and the prereg's frozen `panel_verdict()` returns **`go: false`** on these very legs, both negative controls positive. The GO was an **R1 narrative §5 does not score**. The **cost** record (~$0.43/leg, ~$8/panel) is unaffected |
| 10 | 5a-KS benchmark: Y29A **4.025 ± 1.100** (2 × 3); Y29F **−0.552** (single replicate) | Superseded by the full 3 × 3 set: **+4.424 ± 1.077** and **−0.370 ± 0.175**. Y29A's error against the reference *grew* as replicates landed (0.549 → 1.024) — the scatter showing itself, not a drift to explain away |
| 11 | The warmup NaN was "an alchemical C–H whose constraint changes between endpoints", then "the whole ligand's C–H are unconstrained" | **Both** were artifacts of a `[hmr-diag]` counter that mistook alchemical *nonbonded-exception* pairs for X–H bonds. A perses force-layout dump showed **0 unconstrained valence X–H** on both anchors, and calib NaN'd at 4 fs anyway. Real cause: the **softcore region in a rough homology-built assembly**; the fix is plain-MD pre-equilibration |
| 12 | 8XTT: **4/20** conformers above D\* | The harmonized rerun (pinned fpocket + score-independent matcher) reports **19/20 detected, 3 ≥ D\*** = 3/19 among detected, **3/20** across all deposited |
| 13 | "There is no interruptible discount on Vast" | A tautology of the query type — `_live_offers` defaults to `interruptible=True`, and a bid-type search reports `dph_base` as your rate *at the floor*. Measured across 63 machines / 12 card classes: median on-demand = **1.25× the floor**, IQR 1.14–1.68, zero hosts at parity |
| 14 | `lint_claims.py` R5's premise, "no per-edge alchemical dollar figure is a completed run on the card quoted" | Falsified **for the binary lane only** — the NR4A3 rate was taken on the real system, on the quoted card, across three hosts. The rule should be re-scoped to the ternary lane when the step1 branch merges; left alone rather than raced |
| 15 | Every committed NR-V04 **R3 `min_A`** (2.34–4.48, read as ubiquitination-competent) | The value was in **NANOMETRES under an Ångström label** — OpenMM positions are nm, R1 converted (`* 10.0`), R3 did not. True separations are **~30–49 Å**. Cross-checked independently: `warhead_only` reported 2.34/2.44 against a t=0 distance of **25.21 Å**. Fixed with a regression test |
| 16 | NR-V04 prereg **R2** (*recruited = BSA > 0 in >50 % of frames*) and frozen **criterion 3** (*controls behave*) as GATING criteria | Retired by [AMENDMENT 1](research/modalities/nr4a3-nrv04-covalent-feasibility-prereg.md) (2026-07-25, trimcrae-delegated). R2 returned **one distinct value across 18 legs — 1.0** — including both negative controls, so it had **zero discriminating power**; criterion 3 depended on it and was therefore **unsatisfiable**, making the gate return NO-GO regardless of the science. Replaced by binding criterion **A1 (input admissibility)**, which fails now: covalent legs stage the electrophile **8.99–16.39 Å** from the target-chain Cys Sγ against a ~1.8 Å C–S bond. Panel stays `[HELD]` — no NO-GO became a GO |
| 17 | Cost lever 3: **sequential (anytime-valid) stopping saves ~20–25 %** | Measured on THIS ladder (`valb_rescope_design.py`): **0.8–2.6 %**. At σ=0.5 it stops after 4.87 of 5 replicates, at σ=0.7 after 4.96 of 5. An anytime-valid bound must stay valid under *every* stopping time, so at n = 2–4 with σ ≈ 0.7 it never fires. Real for long horizons; a **5-replicate ladder is too short**. Do not carry it in any total |
| 18 | The valB_mini rescope path: **the high-contrast P1→P4/P5 pair (+2.53 / +2.99) reached through intermediate hops** | Refuted for **$0** on real data (RCSB REST + RDKit MCS, production container): **6 of 10 P-series pairs change formal charge**, including **P1→P4 (`charge_change: -1`)**, blocked by the same missing charge correction that blocks 8 legs of `step1_fanout`; the 4 charge-neutral pairs perturb **58–80 heavy atoms** vs **2** for the running edge; and 9HYO (P4) is **3.74 Å**. Replaced by a **synthetic closure triangle** (~$5.9 at n=1) |
| 19a | "`vast-watchdog.yml` has NOT yet fired on cron … autonomous coverage of the paralogue legs is claimed only once a `schedule` event appears", and "**honestly not proven live:** `DIED → relaunch`" | Both retired by the same event: the **1:42 AM ET 2026-07-26 `schedule` pass** found `nr4a-pdyn-nr4a1` dead with no instance, relaunched it as **45878836**, and it resumed from its 33.55 ns checkpoint — with no session awake. `FAILED` and `STALL` remain unproven live |
| 19d | LANE 13 categorical-dynamics analysis finish "**~1:50 PM ET**" | Quoted with no arithmetic behind it. The task file's own `_analyse_samples_why` prices the committed 2 000 000 samples at **~2.6 h of free CPU** for term (b) alone, before term (a) over 300 conformers — so ~**3:15 PM or later**. Third ETA today given without doing the sum; the rule is in the IN FLIGHT caption |
| 19c | valB_mini reverse leg r0 finish "**~Mon 8:40 PM – Tue 8:40 AM**", flagged as a day later than the `max-effort-3hgq45` session's ~Mon 8:40 AM | Measured on the **first hour after the warmup→production change**, which was a ramp, not the rate: the leg went **40 → 60 → 79 iter/h** across three consecutive windows. The longest window gives 63.8, and the finish lands **~Mon 5:40–10:40 AM** — the sibling session's figure was right and mine was the unrepresentative window, which is the same error this file corrects twice in row 19b |
| 19b | RUNG 2b **ternary** edge finish "**~1 AM**", then "**~6:00 AM**", then "**~7:45 AM**"; **binary** edge "**~overnight**", then "a possible **2.9× slowdown**"; NR4A1 paralogue metad "~**5:30 AM**", NR4A2 "~**6:00 AM**" (all ET, 2026-07-26) | The ~1 AM figure was carried forward without arithmetic. The ~6:00 AM replacement extrapolated from **warmup**, which costs ~2× per iteration what production does. The ~7:45 AM and the binary "slowdown" were both **commit-block quantisation**: the store advances in blocks of 40 iterations and both came off a 27-min window. Live ETAs now come from windows long enough to span many blocks; NR4A1's slipped when it was preempted onto a host that starves its GPU |
| 20 | **"Raise `GPUS_ALL_REGIONS` 1 → 4"** as an open action for trimcrae, quantified at ~1,824 → ~7,296 GPU-h of burnable credit and a closure triangle at 1.8 days instead of 7.3 | **Withdrawn the same day it was written, and WRONG ON ITS OWN TERMS as well as unavailable.** trimcrae: *"We've tried over and over for more quota. They won't give it to a small account like ours."* Repeatedly requested, repeatedly refused. The arithmetic was right and the action was not available — I proposed a lever that had already been pulled and had already failed, without asking. **And the arithmetic was ALSO wrong:** ~1,824 GPU-h is the *wall-clock* ceiling, but the *dollar* ceiling is ~411 L4-h (~$292 remaining at ~$0.71/L4-h), so 1,824 GPU-h was never purchasable and the asset was overstated ~4.4×. At quota 4 the same $292 is simply spent 4× faster — the increase would not have bought more science even if granted. The 1-GPU cap is **permanent** and is now treated as a fixed property of the lane: GCP is the always-on serial worker whose idle time is expiring credit, Vast is burst capacity bought when wall clock matters |
| 21 | A **SECOND scoreboard** at the top of this file — *"6 gates passed · 3 failed · $0.74 spent, **~$35 not spent**"*, with **Tier 0 as "PASSED *(narrowed)*"** carrying no LANE 13 result and **RUNG 2b as "stage 1 PASSED … stage 2 in flight"** | Two scoreboards, ~30 lines apart, disagreeing about the two gates that moved that day — precisely the failure rule 1 exists to catch, in the file rule 1 points at. The stale copy is **deleted**; the surviving board is the one home. The **~$35 not spent** went with it: it never summed from the rows it summarised (~$6–8 + ~$21 = **~$27–29**), so it was a hand-carried total, and per rule 1.1 a total is derived or it is not written. `lint_consistency.py` did not catch either, because both were self-consistent prose — the duplicate was found by reading the section index |
| 22 | *"**The one thing needing a decision:** whether the covalent design route still has candidates"* at the head of the scoreboard | Contradicted **by the row four lines above it**, which records Tier 2 as **PASSED, the covalent limb no longer under review**, and by the `### ✅ PASSED` block immediately below. It was a decision presented to trimcrae that had already been answered by the corrected+matched run. Nothing on that board is waiting on him |
| 23 | Implicit in six consecutive green-except-`tests` builds: that the **guard suite gates the GPU launches** | The suite had been executing **zero tests**. A module-scope `sys.exit(0)` in `test_5aks_pose.py`'s gemmi guard aborts pytest **collection** — `INTERNALERROR> SystemExit: 0`, *"no tests ran in 0.19s"* — so the gate in front of every launch stopped checking anything while still looking like an ordinary red build, and the 5a-KS smoke leg was rented behind it. Fixed as a class (`tests/_skip_guard.py` + an AST test over all guards); the suite now runs **2007** tests |
| 24 | The `step1_fanout` watch entries' implicit claim of interlock cover — `owning_workflow: "fusion-cpu-extras.yml"` alongside `vast-watch.json`'s own note that an entry "may name an owning_workflow that ALSO re-rents dead legs" | **The list was one workflow short from the moment `step1-fanout-autoscale.yml` existed (2026-07-26, LANE 17).** That workflow's `launch` step re-rents any pending unit of the same `nr4a3-step1-fanout` checkpoint prefix, so from then on there were **two** peer relaunchers and the interlock named one. Asked about the wrong workflow, `relaunch_withheld` would have returned *"fusion-cpu-extras.yml is idle — this watchdog is the only relauncher right now"* **while the autoscale tick was mid-launch** — the exact interleaved-trajectory failure the interlock exists to prevent, and the one that produces a confident converged number rather than an error. Field is now a comma-separated list, the engine withholds if **any** named owner is busy, and the required set is **derived from the workflow files** in `tests/test_vast_watchdog.py`, so a third launcher added without registering it fails CI. Verified by mutation: restoring the single-owner string fails the new test. **Not observed in the wild** — no step1 unit died in the window — so this is a closed hole, not a corrected result |
| 25 | My IN FLIGHT board, 4:55–5:25 PM: *"`step1-fanout-autoscale.yml` has so far only ever run on `workflow_dispatch` — **no `schedule` event yet**, so the auto-release of the 18 is not yet proven autonomous"* | **First-fire latency, not a defect** — it fired on `schedule` at **5:30 PM ET**, and row 24's row above carries the measured numbers. Two things I got wrong in reading it as suspicious: three-plus missed `*/20` windows are not diagnostic on this repo, whose measured first-fire is **56/208/210 min**; and the contrast I leaned on — *"the hourly watchdogs fire on schedule, so cron works here"* — set a LONG-ESTABLISHED schedule against a brand-new one, which is not the same claim. What was right, and is why the row stays: the statement was made as **"not yet proven"** rather than as a failure, and it was worth an hour of a $0 lane to go and check — a genuinely dead cron would have left the fan-out doing **one nineteenth** of the work overnight while every hand-dispatched run reported green |
| 26 | Both anchor rows of [`congeneric-edge-timestep-table.json`](research/modalities/congeneric-edge-timestep-table.json) as measurements **of the edges they name** — the force census (`total_constraints` 1771 / 4997, the alchemical `CustomBondForce` holding 11 / 28 bonds, `n_morphing_xh: 0`, `xh_total: 0`), and the `4fs` verdicts derived from them | **The hybrid topologies those numbers were read off were built from DEGENERATE atom maps.** `_mapping` ran `LomapAtomMapper(time=20)`, where `time` is the MCS **timeout** and a timed-out search returns its best *partial* map silently. The calib anchor recorded **47 mapped atoms** for an edge whose two endpoints are the same 59-heavy-atom graph up to one ring N→CH — a **complete 109-atom map provably exists**, and the same edge mapped **109** on the valB legs. The pilot anchor recorded **15** against a provable floor of **19**. So the alchemical region those censuses inventoried is not the designed edge's: ~60 atoms that must map were dummies. The table's own `anchor_check_passed` was already **false**. *Direction of the bias, stated because it matters and is not yet resolved:* a degenerate map makes the alchemical region **larger**, so finding `xh_total = 0` in it is if anything a **conservative** reading — the "every X-H is a constraint, so 4 fs by construction" conclusion (mirrored in [`degrader-paper-schedule.json`](research/manuscripts/degrader-paper-schedule.json)) is **not shown wrong, it is unsupported by these rows**, and needs a re-run on correct maps before it is cited again. Method + floors: `atom_map_audit.py`, pinned by `tests/test_atom_map_audit.py` |
| 27 | *(a hypothesis retired, not a number)* That valB_mini r0's wrong-sign **ΔΔG_coop = −0.534** might be an artifact of the same degenerate-map bug — the possibility that gating all valB_full spend on it, and calling the NR4A ternary scores "exploratory", rested on a failed MCS search rather than on physics | **Tested and REFUTED, which is why it is recorded here rather than left as a worry someone re-raises.** All three r0 legs recorded **`n_mapped_atoms: 109`** — the **complete** map for Wurz cmpd1 (109 atoms; 1 dummy H on cmpd4's 110) — under one protocol hash `a5ad9520f912`. Evidence: GH Actions run **30155238348**'s `[LEG-TABLE]` per-leg dump. The RUNG 2b 4 fs cycle is the same edge and the same mapper. **So −0.534 is a real measurement of something real**, the binary-arm departure remains the live mechanism (§RUNG 2), and nothing in the r0 verdict changes. Pinned as a fixture in `tests/test_atom_map_audit.py::test_valb_r0_legs_are_clean` so it cannot be quietly re-opened |
| 28 | Step-1 shakeout production rate **"7.5 s/iter, matching the smoke's 7.9"** (my 10:45 PM board) | **Wrong by 2.2×, and wrong in the way that hides itself.** I divided 200 iterations by the **~25 min between when I LOOKED**, not the **52 min between the READOUTS** — the committed tick timestamps are the observation times, and the file I was reading was already 30 min old. Recomputed from those: **15.6, then 16.7, and 16.4 s/iter over a 720-iteration, 197-minute window** — steady, not drifting. The compounding error was writing that it *"matched the smoke's 7.9"*: a wrong number that lands on a figure you already believe reads as corroborated, so the agreement suppressed the check instead of prompting it. **A rate window must be measured between the artifact's own timestamps, never between the times an agent happened to read it** — the same class as 19b's commit-block quantisation, which this file already records four times |
| 29 | RUNG 5a-KS NR4A3 leg finish **"~6:20 AM ET"** (my 10:45 PM and 1:35 AM boards) | **Built on a 12-iteration sample.** The warmup half was sound — 17.2 s/iter measured across three commit blocks — but the production half used **7.9 s/iter taken from the SMOKE leg, which ran 12 production iterations in total** before terminating by design. Twelve iterations is not a rate. Observed on the real leg: **120 production iterations in 34 min ≈ 17 s/iter**, i.e. **~2× slower**, though that window spans the warmup→production transition and so is itself contaminated. No replacement ETA is quoted — the honest state is that **no clean production-rate window exists yet**. This is the fourth ETA this file has had to withdraw (19b, 19c, 19d, 28) and the second in six hours where the defect was **the sample the rate came from**, not the arithmetic |
| 30 | *"Tonight's board is not merely expensive, it is **unstable**: hosts are expiring shortly after rent"* offered as the explanation for NR4A1's repeated deaths (my 2:05 AM board) | **Half right, and the wrong half was load-bearing.** The nine-machine blacklist and the 36-minute host death are real, and the churn genuinely does strengthen the fan-out hold. But it does **not** explain NR4A1: that unit has now frozen at **exactly `warmup/192` on three independent machines** while **NR4A3 — same rung, same image, same code — runs clean to `production/160`**. A fault reproducing at one specific iteration across separate hardware, with a healthy sibling, is the **leg or its checkpoint**. I reached for the environmental explanation because it was already on the board and it fitted the first instance; the third instance is what falsifies it. **A pattern that repeats on new hardware is evidence AGAINST a hardware cause** — and the sibling leg was the control I already had and did not use |
| 31 | *"the leading hypothesis is a **poisoned checkpoint at 192**"* (my 3:05 AM board, and the brief I sent LANE 16) | **Refuted by the leg's own log, which had been saying so for 45 minutes.** The resume from 192 works perfectly — `Iteration 233/256 … 237/256 … 240/256` at 14–15 s each, no NaN, no traceback. The leg dies **inside** the 64-iteration commit segment, so `scalar` stays at the last boundary while real work is done and discarded. **The frozen number was the COMMIT INTERVAL, not the failure point.** Worth keeping because a frozen `scalar` has now meant three different things in one night — a predecessor's commit surviving a host change, a phase that commits nothing by construction, and a process dying inside a segment — and all three are identical from outside. My error was procedural rather than analytical: I escalated twice with a confident mechanism attached, reading the watchdog's **verdict** instead of the **artifact it summarises**, when the log was already in hand |
| 32 | *"NR4A3 — same rung, same image, same code — runs clean … a fault reproducing across separate hardware **with a healthy sibling** is the leg or its checkpoint"* (Appendix A 30 and my 3:05 AM board) | **The sibling was never a control.** NR4A3's phase marker is rewritten on the same ~15–20 min cadence as NR4A1's — it is dying just as often and **hiding it**, because `ci=40` in production crosses a commit boundary before each death while NR4A1's `ci=64` in warmup mostly did not. Both legs have the same disease; one has better instrumentation. Row 30's conclusion (not hardware) survives; its **premise** does not, and the premise is what I reasoned from. The lesson is narrow and reusable: **a comparator is only a control if you have checked it is unaffected** — I checked that NR4A3's counter was advancing, which is a different and weaker claim than that NR4A3 was well |
| 33 | *"Both 5a-KS legs die every **~15–20 min**"*, *"NR4A3 restarts on the same cadence and hides it"*, and the derived *"**≈3.5× overhead** paid in restarts"* (row 32 and my 3:05 AM / 4:40 AM boards) | **The period does not exist, and the anomaly does not either — measured, $0, from every archived attempt of every unit in the lane (`rung5aks-cofold.yml mode=leg_diag`, run 30248149894).** An attempt's log is archived by the *next* container start, so consecutive archive timestamps ARE the death series. Per-attempt lifetimes, in minutes: **NR4A3 [408, 23, 84]**, **NR4A1 [76, 14, 14, 103, 11, 112, 35, 143, 63]** — and the three short NR4A1 entries are the deterministic pre-equilibration aborts, a different and already-fixed failure that wrote `[tvast] FAILED at preequil`. Nothing in either series is a ~15–20 min cadence; one NR4A3 attempt ran **6.8 h** unbroken and completed the whole 1600-iteration warmup. **Nor is the comparison lane a control:** the same measurement on the units said to be immune gives `calib_hi_to_lo__ternary_vhl…_probe` **[131, 43, 12, 26, 16, 41, 6, 30, 23, 3, 65, 43, 20, 24]** and `…ternary_vhl…_edge` **[134, 217, 84, 22, 240, 20, 180, 2, 7, 40, 143, 101]** — restarting at least as often as the 5a-KS legs, with 2- and 3-minute attempts the 5a-KS legs never had. The **3.5×** figure was a sampling artifact: re-measured on the current attempts, NR4A3 did 90 production iterations in 32.6 min = **21.7 s/iter effective against 18.7–19.3 s/iter raw, ≈1.15×**, container start included. What the whole episode actually was: **ordinary spot churn**, which CLAUDE.md §6 already says to mention lightly and not investigate. The lesson is the one row 32 half-learned and then mis-applied — *a comparator is only a control if you have measured it* — except this time the comparator was measured and it exonerated the patient. |
| 34 | My own 12:30 AM self-scheduled escalation: *"if `held: true` and `first_held_utc` is more than 6 h old … the 18 edges **cannot be bought** inside the authorised $15–80 band … that is trimcrae's decision"* | **The premise was wrong and the escalation was not warranted.** The 18 are held by the **TERMINUS** gate — no unit has a `ddg.json`, so the tick submits 0 and the price guard never evaluates. The $112.71/$80.44 snapshot is a **single evaluation at 10:06 PM**, not a six-hour continuous hold; `held_hours: 0.03` in the file says so, and I read `first_held_utc` as though it were a duration. Escalating would have woken trimcrae at 4 AM to decide a ceiling that is not currently binding. **The check I scheduled was right; the trigger condition I wrote into it was not** — a stale artifact reads identically to a live one unless you check when it was written, and the fix is that a hold must be re-evidenced by a FRESH evaluation before it can escalate |
| 35 | CLAUDE.md §6's `$/ns` gate as I first scoped it: *"before any **multi-unit fan-out** … **A single unit already running is not affected**; this gates the *fan-out*, not the shakeout"* (written 2026-07-26 at trimcrae's instruction, and the code matched it — `if len(batch) > 1` in `congeneric_fanout_vast.mode_launch`, with no gate at all on either watchdog's relaunch path) | **The exemption was cut on the wrong axis, and the board showed it the same night** (trimcrae, 2026-07-27: *"Why are there so many high $/ns rows that are flagged but you're still paying for them? The whole point is to pause the test if it gets that expensive."*). A fan-out at **2.05× basis** was correctly refused while the step 1 shakeout ran at **1.76×** and the 5a-KS NR4A3 leg at **1.51×**, both printing `⚠ DRIFT`, both untouched — and overnight both lanes were re-rented repeatedly on spot churn, **every relaunch a fresh decision to rent a host at whatever the market was charging**, none of them priced. "Already running" was never true at the moment the decision was taken: the host is already gone. **The right axis is "would waiting actually lose work?"**, which for a checkpointed unit is no — the surviving state is a durable S3 object, and that premise was **measured rather than assumed** (`--durability-probe`, run 30261866562): the direct read is refused (`AccessDenied` — CI has no `s3:GetLifecycleConfiguration`), so it was closed on a property of S3 instead — **lifecycle expiration is expressed in days, minimum 1**, so the shortest possible rule is 24 h while a hold becomes trimcrae's decision at 6 h, and the listing separately excludes any 1–2 day rule (checkpoints 2.6 d old survive) and any storage-class transition (all `STANDARD`). Superseded by the rule now in §6: **every rental of a new host is gated**, a single host on the §1 drift line rather than a tranche's dollar band, with `relaunch_market_gate.EXEMPTIONS` the closed list of the cases where waiting genuinely does cost something. Realised cost of the hole: **~$1.5** (5a-KS) + **$0.35** (fan-out) — it was closed before it mattered at width, not after |
| 36 | Two readings of the same rental, both carried as if they were the same quantity: the Step 1 shakeout on `45996071` at **$0.1926/hr → $0.00612/ns · 1.41× basis** at 7:02 AM ET and **$0.2497/hr → $0.00793/ns · 1.82× ⚠** at 7:45 AM — read as a **post-rental price rise**, and very nearly used to justify giving the relaunch gate reach over LIVE hosts (kill-or-migrate), which CLAUDE.md §6 forbids | **The rate never moved. The two numbers are different quantities, measured $0 and read-only (`vast_rate_forensics.py --probe`, run 30265697399, 8:23 AM ET).** On all six live instances `dph_total = dph_base + storage_total_cost` **exactly** (residual 0.0; the `inet_*_cost` pair is not in the total). On the one instance with a recorded bid — `46000463`, running at 96 % GPU — `dph_base` is **$0.180500 against a recorded bid of $0.180500**, while that machine's floor had *moved* from $0.177 to $0.1733333 in the meantime: the market shifted under a live rental and the charged rate did not follow. The offer→instance gap decomposes with nothing left over: **$0.0235/hr = $0.0035 floor→bid + $0.0200 disk line**, because the launcher's `dph≈` line is the OFFER's `dph_total` (market floor + the disk line the search priced at **8 GB**) while the instance is billed our BID + the disk line for the **80 GB** actually allocated — a **10.0×** under-quote of storage. So the 1.41× was an offer quote reading low and the 1.82× was the honest billed figure; nothing rose. **The premise was checked before the mechanism was built, and the mechanism was not built** — §6's live-host boundary stands, now on a measurement instead of an assumption. What WAS defective is the reporting: a board row typed off `dph≈` under-reports its own multiple, so `inflight_usd_per_ns.row()` now carries a `rate_basis` and marks a quote-derived row as a LOWER BOUND |
| 37 | The IN FLIGHT board rendering **`⚠ DRIFT` identically on rows we are PAYING and rows the gate REFUSED** — the 19-edge fan-out at 3.25× and valB at 1.96× (both held, **$0 out**) carrying the same mark as the 5a-KS leg at 1.51× and the shakeout at 1.82× (both being billed) | **A reporting defect, and it cost a question that should never have needed asking** (trimcrae, 2026-07-27: *"the `$/ns` column still shows several rows over 1.5×. Why? Are we not stopping those runs? What's the point of tracking that if we don't act on it?"*). The gate was working; the format made a refusal indistinguishable from a bill, so a guard doing exactly its job read as a guard being ignored. One glyph cannot carry two opposite meanings. Replaced by `⚠ PAYING OVER THE …× LINE` versus `⛔ REFUSED at … — $0 spent` in `inflight_usd_per_ns.py`, with the rule in CLAUDE.md §1 and the distinction pinned in `tests/test_inflight_usd_per_ns.py`. **The threshold itself did not move** — it was later re-expressed from a multiple to the absolute rate `$0.006539/ns`, which is row 40 below and is *not* a change in what we will pay |
| 38 | Two things the valB_mini replicate board carried as live facts: **(a)** the per-host `$/ns` of the **12:14 PM** cohort (ternary r1 $0.002730 · 0.80×, binary r1 $0.003576 · 1.05×, ternary r2 $0.003652 · 1.07×, binary r2 $0.003696 · 1.08×) and then of the **2:13 PM** cohort ($0.003362 · 0.985×, $0.004488 · 1.315×, $0.003911 · 1.146×, $0.004488 · 1.315×), each written as *what we are paying*; and **(b)** `ternary_vast_launch.MODES['edge_reps']`'s own comment, *"seeds 1 and 2 start from DIFFERENT independently relaxed SMARCA2 models"* | **(a) Both cohorts are gone and neither rate is being paid.** They were correct when written — read off the live instance records at rental — and are retained because the *shape* is the lesson: on this lane a per-host rate is a fact with a **half-life of about two hours**, so a board row quoting one must name the cohort it belongs to or it will be read as current long after the host is destroyed. Realised across both cohorts is small (**$0.81** measured on the second) against a derived **$7.32** plan and a **$20.74** ceiling; what was actually lost is **~85 min × 4 hosts** of billing after the GPUs were reclaimed, because nothing on a cron looks at `cur_state` (fixed — see the IN FLIGHT row). **(b) True of the PAIR, false of the SET, and the SET is what the cycle SD is computed over.** `ternary_pdb_stage` builds the homology ensemble at **n_models=2** and takes `starting_model_index = seed % n_models`, so seed 2 lands back on **model 0 — r0's pose**. At n=3 only two distinct relaxed models are used, reviewer condition #3 is met for 2 of 3 ternary replicates, and the between-replicate SD therefore **understates the homology-model variance**. Not fixed in flight (rebuilding at n_models=3 would re-relax the ensemble and break comparability with the two replicates that already exist); recorded, reported with the SD, and pinned by `tests/test_edge_reps_seed_independence.py`, which also flags that an *extend to 5* round would put **three of five** replicates on model 0 and so must widen the ensemble first |
| 39 | The scoreboard headline **`$0.74 spent`** (and, before it, `$0.74 spent, ~$35 not spent` in the duplicate board retired at row 21) | **A hand-carried realised total, wrong by more than an order of magnitude, and wrong in the direction that matters** — it stood while the step 1 fan-out's own rental ledger read **$20.11** and the throughput bench sweep's read **$3.49**, i.e. while three lanes were billing. Rule 1.1 already said a total is DERIVED; nothing enforced it for *this* total, because it was not a ladder figure, not a table row, and not a superseded value — just a number in prose with no machine behind it. Replaced by [`realised-spend.json`](research/modalities/realised-spend.json), summed from the lanes' own ledgers by `realised_spend.py`, and by **rule A** in `lint_consistency.py`, which fails the build if the doc and the artifact disagree. The same pass recorded what the arithmetic still cannot see: the **ternary Vast lane has no rental ledger at all**, so its spend is attested rather than counted and the ledgered figure is a **floor** until that lane gets one |
| 40 | The buy line written as a **multiple**, `1.5× basis`, in the IN FLIGHT board's `⚠ PAYING OVER THE …× LINE` marks and in row 37's closing clause *"The 1.5× threshold itself did not move"* | **Re-expressed, NOT loosened, and the distinction is the whole point** (trimcrae, 2026-07-27). The invariant is the **absolute rate `$0.006539/ns`**; against the re-anchored basis `$0.003412/ns` that is **≈1.92×**. `1.5 × $0.004359` and `1.92 × $0.003412` are the **same dollars per nanosecond** — the basis fell 22 % because the throughput table was re-anchored (the RTX 4090 anchor read ~6.7 % low) and widened (gradeable offers **132 → 229**, table **3 → 10** cards), and **no price moved**. Pinning a rule to a correctable denominator had silently made it much stricter than the one agreed; the multiple is now DERIVED from the rate (`inflight_usd_per_ns.drift_multiple()`) and `tests/test_buy_line_invariant.py` fails if the flag and the refusal ever diverge. Anyone quoting the multiple alone will reach the wrong conclusion, which is why both expressions travel together |
| 41 | The closure triangle's reading, stated **backwards** on 2026-07-27: that a small `R` would mean the valB miss was fixable | **The mapping is the other way round, and it is now stated once, in the IN FLIGHT board's `WHAT R DECIDES` block.** `R ≈ 0` ⇒ an **endpoint-STATE** error: the bias telescopes out of any cycle and **more sampling will not fix the miss**. `R` materially non-zero ⇒ a **PATH** error, and the miss **is** fixable. Both outcomes are informative and the second argues against my own earlier reading of the departed binary arm, which is why the prediction was pre-registered before the legs ran |
| 42 | The closure triangle priced at **projected $2.49 against a $3.85 ceiling** and described as **NOT LAUNCHED — refused by the atom-map gate at 6:01 PM ET on 2026-07-27** | **Both retired the same evening, and neither by a price move.** The map gate PASSED once the smoke ran the closing edge end to end (`status=done` at 6:56 PM, dG 44.807 ± 0.582, `NaN=False`), so the refusal was the gate doing its job on incomplete evidence, not a standing defect. The $2.49/$3.85 pair was priced for a **smoke-scale** unit; the 4-leg launch at 7:51 PM is a different purchase and derives **$9.86 against a $15.40 ceiling** (1.73× basis board mean, `n_rented: 3` of 4). Do not quote the $2.49 or the $3.85 against the 4-leg triangle |
| 43 | The forward/reverse antisymmetry detector recorded as **`antisymmetry_fwd_plus_rev_kcal: null` on all three legs** — one of "two of three systematic-error detectors were never run; one *could not* run" | **MEASURED and PASSED on 2026-07-28**: `|ΔG_fwd + ΔG_rev| = 0.325 ≤ 1.000`, once the rev leg landed on GCP (reduce [run 30353349373](https://github.com/trimcrae/Rare-cancers/actions/runs/30353349373)). The `null` is superseded as a *live* statement and retained only as the state the 2026-07-25 audit was written against. **What did NOT change:** the calibrator verdict is still `INDETERMINATE` — now for want of replicates (`n_replicates=1`) rather than for want of a detector — and cycle closure, the third detector, is still unrun. Anyone quoting "no systematic-error detector has ever returned a value" is now wrong; anyone reading the PASS as validating ΔΔG_coop is also wrong, since antisymmetry is a check the sampling can pass while the answer stays wrong |
| 44 | The valB_mini calibrator's r0 reading **ΔΔG_coop = −0.534 kcal/mol**, abs error **1.478** (quoted in the reduce annotations of 2026-07-27/28 and in the first draft of the paper's §2.11) | **Superseded by the restrained binary re-run, NOT by a re-analysis.** The original binary arm was contaminated — its ligand left the pocket in 8 of 12 replicas — so it was re-run from scratch under a flat-bottom λ-independent pocket restraint on its own commit prefix. With the clean arm the reduction reads **−0.522**, abs error **1.466** (reduce [run 30438773820](https://github.com/trimcrae/Rare-cancers/actions/runs/30438773820), 2026-07-29). **The point is how little it moved: 0.012 kcal/mol against a ~1.47 miss, under 1 %.** The contamination was real and worth fixing, and it was NOT the cause of the wrong sign — which is a measured elimination of the most plausible benign explanation, not an argument for one. Do not quote −0.534 as the current value; do not cite the re-run as having "not mattered" either, since a null result on a named confounder is exactly what it was run to establish |
| 45 | RUNG 2b's ratified-threshold note: *"the 2 fs baseline WAS pre-equilibrated, so **the two arms differ in the TIMESTEP ALONE** and a disagreement IS attributable to it"*, and beside it *"both arms are seed 0, hence **the same starting homology model**, so the comparison is not additionally confounded by model choice"* | **The pre-equilibration half is right and stands; the "timestep alone" half is false.** Measured 2026-07-28, $0 CPU, by a composition census of the committed trajectories themselves ([`ternary_system_census.py`](research/modalities/ternary_system_census.py), [GH run 30353705917](https://github.com/trimcrae/Rare-cancers/actions/runs/30353705917); full table in [ternary-4fs-vast-findings.md §2d](research/compute/ternary-4fs-vast-findings.md)). The two arms ran on **different lanes and object stores** — r0 on GCP/GCS, the 4 fs cycle on Vast/S3, which `ternary_vast_launch.py` says outright "never touches GCS" — each with its **own** RCSB fetch, SMARCA2 relaxation, solvation and pre-equilibration. Their ternary boxes differ by **675 waters and 4 ions** (141,968 vs 139,939 particles). What the census establishes positively is that this is **only** bulk solvent: the solute is identical atom-for-atom in every arm (ternary 7,140 = chains 2343/1925/1433/1329 + a 110-atom ligand; binary 5,215), net charge 0 throughout, and the neutralising ion excess — the solute's formal charge — is invariant at +4 ternary / +7 binary across every build, which is what a protonation or tautomer difference would have broken. Sized against the gate the solvent difference is **~3e-3 kcal/mol**, ~7× under the observed |Δ| = 0.0215 and ~230× under the 0.7 threshold, so **the PASS and the 4 fs adoption stand** — but as a *cross-lane independent reproduction*, not a controlled single-variable timestep swap, and nothing should be built on the stronger reading. Two numbers that prompted this were also misattributed and must not be quoted as the 4 fs arm's: **7,398 and 7,392** are GCP-lane builds that produced no leg result and are in no cycle; the RUNG 2b ternary leg's own analysis subset is **7,384**. |
| 46 | The realised-spend scoreboard at **$24.46 ledgered / $26.77 best estimate** (and every board that quoted it) | **Undercounted by ~3x, and not because anything was mis-summed — because `main` was summing the wrong copy.** The step-1 fan-out writes its ledger to `claude/max-effort-2dq11l`, the branch its workflow checks out; `main`'s copy stopped at 86 rentals while the lane's real one held **197**. Corrected to **$72.47 ledgered / $74.78 best estimate** once the artifact was ported. **No new money was spent** — this is a bookkeeping correction to figures that were wrong when written. The general lesson is now a standing rule (CLAUDE.md §7, branch drift): before quoting any committed artifact, check which ref the producing workflow actually writes to |
| 47 | The evidence offered for "ΔΔG_coop is SAFE, the charge model cancels": **`CHARGE_METHOD` is `nagl` on both arms** — a configuration flag plus a `partial_charge_method = nagl` line in a live leg log (this table's own §Val A evidence column, 2026-07-24) | **The conclusion survives; the basis did not, and the gap it left was real rather than pedantic.** OpenFE *prefers user-supplied charges over its configured `partial_charge_method`*, and until 2026-07-28T00:54Z the relaxed pose file every leg read shipped a complete per-atom charge set — so the configured value and the parameterised value were free to differ, silently, with the log still saying `nagl`. Read from the stored setup-cache `System`s instead (2026-07-29, $0, `task=charge-provenance`): the inheritance **did** occur on every banked forward leg, and it changed nothing, because the inherited values **are** the protocol's NAGL values (the binary arm ran with nothing to inherit and produced the same numbers to 0.0 *e*). r0/r1/r2 arms carry identical alchemical charges (109/109 core atoms; max \|Δq\| 0.0 / 0.0 / 1.9 × 10⁻⁷ *e*), and the reverse leg's endpoints are the forward leg's swapped. **No banked ΔG or ΔΔG changes.** Do not cite a `CHARGE_METHOD` flag or a log line as evidence of what a leg sampled; cite [`charge-provenance-forensic.json`](research/modalities/charge-provenance-forensic.json) |
| 19 | "E3 breadth is free at the search stage — widen to the ligandable set and *some* E3 will complement NR4A3's differential surface" (availability checked, and it did not constrain) | Availability was the **wrong constraint**. Structural stageability is the binding one: of 10 recruiters, **RNF114 has no deposited structure at all**, **DCAF16**'s ligand is **34 % buried** with its partner removed (glue interface, not a handle pocket), and **DCAF15** has no partner-free liganded structure. The widening **confirmed CRBN + VHL rather than displacing them** — a real negative for the breadth argument, to be reported not absorbed |
| 48 | The scoreboard deliverable **"21 candidate molecules, chemistry-verified end to end"** | **Stale, and it contradicted this file's own library line 56 rows above it** (*"Library is now 36 exemplar + 18 representative, RDKit-verified 54/54"*) — a one-fact-two-values defect of exactly the kind rule 1 exists to prevent, surviving because the deliverable row and the library block were edited in different passes. The live count is **54** and it is DERIVED from [`nr4a3-linker-design.json`](research/modalities/nr4a3-linker-design.json) → `library_summary.n_constructs` (36) + `library_summary_at_representative_geometry.n_constructs` (18), never typed. **21** was the pre-wedge-fix enumeration; it is not withdrawn as wrong for the run that produced it, and the manuscript's §2.10 carried it too until 2026-07-30 |
| 49 | The Tier-2 orientation-basin figures as they stood in the **manuscript** until 2026-07-30: **7** basins exploiting term (a), `crbn|M0` reaching C397 at **11** backbone atoms and so clearing the 12-atom gate, gate-level reach fractions **0.019–0.057**, the conserved-cysteine control **zero in 168 of 192** basins (0–6.6 %), and every reach length carried as a **lower bound** | **Superseded by the 2026-07-26 reach correction, which this file had recorded and the paper had not** — the defect that let a document lag a correction by four days is the same branch/document-drift failure as row 46, in a different medium. Corrected+matched values, which are the ones in the §WHERE WE ARE block above and now in the paper: **3** basins (`vhl\|M2` 10 atoms / 0.057, `vhl\|M3` 11 / 0.021, `crbn\|M17` 12 / 0.045), `crbn\|M0` at **13** and therefore MISSING the gate at a reach fraction of **0.000**, fractions **0.021–0.057**, control zero in **184 of 192** (0.4–3.9 %), and no figure a bound. Term (b) **40** and the nominal limb **28** are bit-identical across the correction, and the Tier-2 GO is unchanged. Also withdrawn with it: the paper's claim that emitting the achieving placement left *"the strongest basin among the most tractable"* — `crbn\|M0` at 13 atoms is **comparable** to `vhl\|M2` (10) and `vhl\|M3` (11), not ahead of them |
| 50 | The step-1 fan-out map reported as complete **with no cycle-closure readout at all**, in this file and in the paper's §2.9, while all three of `cycle_3carbonyl`'s edges were quoted unflagged | **The closures were computed and landed with the map; they had simply reached no document.** Two of three close (**−0.726**, **−0.756**, tolerance ±1.0); **`cycle_3carbonyl` sums to +1.307 — VIOLATION**, so by the artifact's own rule at least one of its three edges is unconverged or mis-mapped and all three now carry that reservation where they are quoted. Nothing about the map's counts or spend changes. Separately fixed in the same pass: `cycle_closure`'s `signed_terms` zipped the caller's **declaration-order** edge ids against `_walk_cycle`'s **walk-order** values, mislabelling which edge carried which value in every cycle where the two orders differ. `sum_kcal` is order-independent and was never wrong, which is why it went unnoticed; pinned now by `test_signed_terms_label_each_edge_with_its_OWN_ddg` |
| 51 | The valB_mini miss quoted as **1.466** (paper §2.11) and **1.478** (SI §S11, and this file's live text in two places), with the derived ratio **"~33× the statistical uncertainty"** in the paper's abstract, §2.11, §5 and the SI — and the **abstract still reporting the r0-only headline ΔΔG_coop = −0.522** | **All superseded by the landed n = 3 replicates, and the paper's own Appendix A already said so while its abstract did not** — a document contradicting itself four sections apart, which is the failure mode rule 1 exists to catch. Live values: mean **−0.599**, abs error **1.543**, ratio **~34×**. 1.466 is the r0-only reading after the restrained binary re-run (row 44); **1.478 is the reading before it, i.e. superseded twice over**, and it was still live in the SI on 2026-07-30. Nothing about the conclusion moves — the sign was wrong at every one of the three values, which is why the correction is a bookkeeping one and is recorded rather than argued |
| 52 | The generation-matched null's comparison block reporting **`p_value: 0.0`, `enrichment: Infinity`, `exceeds_chance: true`** and the verdict *"real campaign produced a survivor the control objectives NEVER manufactured → survival is not a generic funnel artifact"* | **Every measured count in that artifact is correct and unchanged; the statistics derived from them were not.** `false_positive_rate` returned a per-molecule control rate of exactly **0** — a point estimate from a *single* 191-molecule campaign — and `compare_campaigns` then divided by it, so any real survivor was infinitely enriched at p = 0 **by construction**, independently of the evidence. The honest reading is the **rule-of-three bound**: 0 events in 191 generations puts the manufactured rate at **≤0.0157 (one-sided 95 %)**, which is **3× the real campaign's own 0.0052**, so the confound is **narrowed, not excluded**; one-sided Fisher for 1/191 vs 0/191 is **p = 0.5**. Fixed at the source (`per_molecule_fp_rate_upper95`, and the zero branch now grades the real rate against that bound), retired in place in the artifact's `_superseded` block, and pinned by two tests — one of which previously asserted the overclaim. The artifact was also **not strict JSON** while it carried a bare `Infinity`; it is now |
| 55 | *"A single chain carrying both the covalent handle and the causal wedge needs 16 backbone atoms, and the segment grid cannot build it (branch floor k=6 against T407's k∈[2,3] at n=16). That is a **grid limit, not geometry**"* — live in three places in this file and named as a $0 re-grid | **Run against the committed enumeration on 2026-07-30 ($0), and every clause except the branch floor is FALSE.** The grid builds T407 branches at n=16 **and** C397 branches at n=16 — both targets at **three** shared lengths (16, 18, 20) — so "cannot build it at 16" is refuted by the artifact's own records. **No committed T407 window is k∈[2,3]**: the real ones are **k∈[2,6]** (exemplar) and **k∈[4,13]** (representative), and the enumerator builds at k=6, 7 and 11, all inside them. **The real blocker is that `build_smiles` takes ONE `pendant`** — its template has a single branch residue, so no choice of segments, length or placement can emit a two-mechanism molecule; every sweep over the grid was searching a space that structurally cannot contain the answer. The floor `k = 3 + SEG2 + tail` is real, is **independent of SEG1 and of chain length**, and is **architectural** — the 3 is the branch residue's own N–Cα–C and `SEG2 = 0` is refused because it would form an acylurea — so **no grid change reaches k < 4**. What would work is a **two-branch template**, constructible at **n = 18** with the segments the grid already has, i.e. the fix needs no new chemistry and was never a re-grid. Derived, never typed: `linker_branch_reach.py` → `linker-branch-reach.json`, 7 tests |
| 54 | Pinned ladder total **~$158 mid (~$44–578)**, and RUNG 5a-KS priced at **~$12 ($1.6–45)** for **two** ternary legs | **RUNG 5a-KS went to n = 2 SEEDS PER ARM — four legs** (trimcrae go 2026-07-30, [Open decisions 11](#open-decisions)), because at one seed per arm `S` has no replicate SD and cannot report a null, which is its own pre-registered likely outcome. Current: **~$169 mid (~$46–626)**, stage **~$23 ($3.1–97)**. ⚠ **The cleanest reprice in this file's history and it is worth saying why: the market snapshot, the `$/reference-GPU-hour` rate and every other stage's GPU-hours are BYTE-IDENTICAL across it** — the whole +$11 mid is the second seed, the exact opposite of row 40's reprice where no price moved and only the yardstick did. Two collateral corrections found by regenerating rather than reading: the §Spend-summary prose had been carrying the 5a basin stage at **mid $25** where the machine registry uses **$0**, which is why its own printed arithmetic said `≈ 194` beside a pinned `~$158` and then claimed they agreed; and its quoted tool figures (**$149.4 at $0.137/ref-GPU-h**) were from an older snapshot than the committed artifact (**$138.16 at $0.1143**). ⚠ **Near-collision, stated so nobody misreads an old copy: the tool total is NOW $149.63, within $0.25 of the stale $149.4 it replaces, and they are unrelated quantities** — 2 legs at a higher rate vs 4 legs at a lower one. Derived, never typed: `vast_cost_model.py --json-out vast-ladder-repricing.json`, checked by `lint_consistency`'s `ladder_total` derivation |
| 56 | The GCP card table's claim that **P100 is faster than L4 AND +18 % better on science-per-dollar** (`~2.4×`, `1.67`), that **T4 is 2.2× better** (`~1.1×`, `3.05`), and that **V100 is ~3.0×** — live in this file's Open decision 5 and in gcp-gpu-facts.md §1b, every row flagged SPEC-DERIVED and unplannable | **MEASURED 2026-07-31 on free trial credit, and the heuristic behind every non-L4 row is REFUTED.** The T4 was the discriminating case by construction — bandwidth 320 vs the L4's 300 predicts **1.07× L4**, FP32 8.1 vs 30.3 TFLOPS predicts **0.27×** — and it measured **~0.31×** at the lane's real 141,867-particle system. **The workload is compute-bound, so the bandwidth argument that generated the P100 and V100 rows does not hold either.** ⚠ **A SECOND, INDEPENDENT ERROR needed no measurement at all:** the `$/h` column compared the L4's WHOLE-VM rate (0.71 = a g2-standard-4, which bundles the L4) against BARE GPU rates for the others (1.46 / 2.48 / 0.35), and a P100 cannot run without a host — adding the n1-standard-4 it needs ($0.190/h), with the old speeds untouched, already takes P100 from **+18 % to +3 %** and T4 from **2.16× to 1.44×**. Both errors point the same way: they flattered the alternatives. Net: the T4 delivers **~0.41×** the L4's science-per-dollar against a promised 2.2×, **wrong by ~5× in the direction that would have bought the worst card on the board.** ⚠ **What must NOT be over-read:** the T4 number was REFUSED by the probe's own admission gate (CV 5.6 % vs a 5 % ceiling) and stands as a RANKING, not a rate — the 3.5× discrepancy cannot be manufactured by 5.6 % of scatter, but the figure is provisional; and P100/V100 remain unmeasured, so they are not *refuted*, only left without support. **What SURVIVES, now measured rather than assumed:** the original 'a faster GPU would not help — the GCP lane is DOLLAR-bound' conclusion, and 'no GPU quota request is worth filing'. Derived, never typed: `gcp_card_bench.py` → [`gcp-card-bench.json`](research/modalities/gcp-card-bench.json); readable table and full caveats in [gcp-gpu-facts.md §1c/§1d](research/compute/gcp-gpu-facts.md) |
| 53 | The marginal axis's **best-case resolvable difference of 1.12 kcal/mol** at an assumed **replicate SD 0.7, n = 3**, quoted beside a **literature** accuracy of **~1.7 kcal/mol RMSE** — live in five places in this file (the MECHANISM-FIRST definition, the Tier-3 semantics box, the 5a-KS honest expectation, the pmx noise-structure block, the Spend-summary defence of mechanism-first) and three in the paper (§2.10, §4, §5). With it, the derived reading **"the marginal axis is a confirmation tool operating near its LIMIT"** and the Spend-summary claim that spending on it *"is a bad trade at any price"* | **The SD was never measured; the n = 3 valB_mini replicates measured it at 0.375**, and the same function on the measured value gives **0.60** — the noise floor is ~1.9× better than the plan had been assuming, so the required margin sits at **~3.3× the floor rather than ~1.8×**. In the same landing the **accuracy** stopped being a literature figure and became a measured one that is **worse**: 1.543 kcal/mol with the **wrong sign** on this exact quantity class, localised by `R` to an **endpoint-state** error that replicates cannot touch. **So the axis is UNCALIBRATED, not blunt** — the two defects have different remedies, and the plan was buying neither. ⚠ **What did NOT change, and must not be inferred:** the mechanism-first *order* (a categorical handle needs no margin, and the categorical screens are $0 — either argument alone carries it), and the fact that a better noise floor cannot make a 2.0 kcal/mol margin *exist*. Derived, never typed: `selectivity_margin_model.minimum_detectable_difference`; consequences in §WHAT THE LANDED RESULTS CHANGE |
| 57 | The NR-V04 retrospective board reading **"17 of 18"** and then **"18 of 18 authorized R1 leg(s) landed"** (10:54 and 11:10 AM ET 2026-07-31), the collect readout `panel_complete: true` with a frozen-gate `verdict` carrying **model-level E1 means for all three arms** (nr4a1 1.085/1.086/1.1125, nr4a2 2.355/1.092/1.0905, nr4a3 1.083/1.0315) and `tier: INDETERMINATE`; and this file's RUNG 4 ledger line **"~$21 not spent"** | **Seventeen of those 18 records are SMOKE legs and none of the means is physics.** Measured (job 91195498091 + `nrv04_retro_smoke_forensics.py`): `mode: smoke`, **n_frames 5**, **timed_ns 0.002** and **prod_wall_s 4.0–20.5 s** against the one genuine leg's 500 / 5.0 / 3730.5 — i.e. **2 ps of sampling after ZERO equilibration**, which is the minimised starting structure, so an E1 near 1 Å measures that the structure has not moved. Two mechanisms, both now fixed with tests: `retro_collect` counted a unit as landed on the mere EXISTENCE of a `leg_*.json` (a smoke record still echoes `prod_ns: 5.0` from its env and still fills `R1_interface`, so it is *plausible*, not empty) — the predicate is now `nrv04_retro_panel.production_leg_check`; and `retro_supervise` re-placed every unit that was neither done nor hosted, which describes a **HELD** unit perfectly, at `MODE=smoke` inherited from the dispatching workflow's default — supervision now re-places only units an operator dispatch recorded in `_authorized_units.json`, and pins `MODE=run`. **prereg §4f was not violated by the gate; it was bypassed by the coverage count feeding it.** The verdict is withdrawn in full and no R1 result exists. Realized cost **$0.75** (the lane ledger's $26.57 total is dominated by one 6.5-day Jul-26 host entry, which is a separate pre-existing figure) |
| 58 | Realised spend **attested-only $22.31** and **best estimate $99.59** (this file's Spend summary, 2026-07-31 morning); and row 57's parenthetical that the retrospective ledger's **$26.57** total is "dominated by one 6.5-day Jul-26 host entry, **which is a separate pre-existing figure**" | **That entry is a SECOND ORPHANED RENTAL of the same class as the `cal-*` leak, and it is now registered rather than set aside.** Instance **45749905** — the host of the lane's ONE genuine Arm E leg (`nrv04retro-retro_noncov_nr4a2-m1-r0`) — was rented **6:59 PM ET Fri Jul 24** and not destroyed until **6:59 AM ET Fri Jul 31**: **156.0 h of rental against a leg that computed for 1.04 h** (its own record's `prod_wall_s` 3730.5), because nothing dispatched that lane's collect for five days. Current: attested **$48.89**, best estimate **$126.17**, both DERIVED (`realised_spend.py --write`). The lane's other **$0.75** — the 17 withdrawn smoke rentals of row 57 — is registered beside it as `nrv04_retro_smoke_fanout`, so the two sum to the **$26.5733** this lane's own S3 ledger reports and nothing is left unaccounted. ⚠ **The size is a RANGE, $6.68–$25.83, and must never be quoted as a point estimate:** span (561615 s) and rate ($0.16555…/hr) are both measured from the instance's own record at reap (run 30625438729 job 91139494243, 10:59:45 UTC, one second before `auto-stopped … result-in-S3`), but the host was last seen `exited` after a container start failure and its last S3 write was 11:20 AM ET 07-26, so whether the meter ran for the idle ~4.8 days is unrecoverable now the host is gone. ⚠ **What was NOT wrong is the arithmetic.** `uptime_s` is `now − instance.start_date` at whatever poll saw the host — **billed rental time, never leg time, and a LOWER bound on the rental** (the poll is at or before teardown). The control that settled it: the same census showed three sibling hosts rented 14/31/72 min earlier reading `start_date` ages of 14m/31m/1h12m while their `duration` field read 135d/1958d/30d. **The reporting was wrong in both directions and both are fixed:** a leak was averaged into `measured_mean_usd_per_leg` (dragging an 18-row mean to $1.4763/leg against 17 real rows of $0.01–$0.11), and `final` latched on the mere existence of a `leg_*.json`, freezing a re-rent's price at minutes while its host billed on. One home: `realised_spend.ATTESTED` → `nrv04_retro_orphan`; evidence `nrv04_retro_price_forensics.py` → `nrv04-retro-price-forensics.json`; meaning pinned by `tests/test_price_ledger_uptime_semantics.py` |
| 59 | The framing under which a Vast machine exclusion could be **DURABLE, CROSS-LANE AND PERMANENT** — CLAUDE.md §6's capacity-refusal bullet read as endorsing it ("without the exclusion it keeps winning selection and keeps failing"), `vast_machine_blacklist`'s `scope="host"` shared set, and every lane-local `_excluded_machines.json`. Also the earlier position that only the **capacity** class is perishable while a **host** verdict may be stored forever, because "how long is a host verdict true for" had no measurement behind it | **RETIRED by trimcrae 2026-07-31: *"You've gotta just stop doing the blacklist. It seems like it only ever bites us in the ass and clearing it always makes things better."*** The standing rule is now CLAUDE.md §6 — **nothing that excludes a machine may outlive the placement call or the launch wave that learned it.** ⚠ **What is KEPT and must not be confused with the retired set, because both are bounded and neither accumulates:** `used_machines` (`congeneric_fanout_vast.mode_launch`), which stops one wave double-renting a host we already hold and dies with the wave; and `gpu_backend.submit`'s in-call retry skip, which drops a machine that just answered `resources_unavailable` for the remaining offers of that same call, on a copy of the spec. **The defect was never that a given entry was wrong** — some of those hosts really do refuse every start — **it is that the set had no evidence that could ever RETIRE an entry** (nothing ages out, and a TTL was correctly refused for want of a measurement), so it was a ratchet on the one quantity that has to stay wide. The asymmetry that decides it: re-learning a bad host costs one **free** failed submit, while over-excluding costs capacity on every lane, every night, silently. Consequence for reading the record: the *incidents* stay true and are still the best evidence for the rule (`vast_exclusion_census.__doc__`, `congeneric_fanout_vast.withdraw_wrong_exclusions` / `.retire_perishable_exclusions`, `vast_machine_blacklist.__doc__`) — it is their **remedy** that is superseded, not their measurements. Indexed, with what is still open, in [vast-placement-facts.md §1](research/compute/vast-placement-facts.md) |
| 60 | **RUNG 5a-KS's staged system is 285,133 particles** — asserted 2026-07-31 in `step1-fanout-supervisor.yml` to justify a `min_ns_per_h=28` card floor for 5a-KS | **UNSOURCED, and contradicted by the only measurement.** The sole recorded particle count for that assembly is **147,788**, from the leg record of `5aks_d0_to_d__ternary_nr4a3` (`ternary-arm-iteration-rates.json`), whose smoke and production runs share one `leg_id` and one staged input. The valB ternary legs are 141,458-144,447, so 5a-KS is ~3-4 % larger than the triangle, not ~2x. The extrapolation built on it ("a 5a-KS warmup interval near 71 min") inherits the error. The card floor it argued for was reverted the same day on separate evidence (the fan-out's 208-rental ledger: 3090-class hosts held a 1.50 h median against 1.65 h for 4090/5090-class), so nothing downstream still rests on it. |
| 61 | **`vast_cost_model.ns_per_hour` — "ns/hr for this card at the ternary system size"** | **FALSE, corrected 2026-07-31.** No caller passes a system and none ever has. The figure is `MEASURED_NS_PER_DAY_84K`, whose protocol `vast_bench_sweep` records verbatim as *"TIP3P/PME 84,534 particles, 4 fs HMR, 3 timed blocks"* — plain, single-replica MD on a pure WATER BOX. It is a REFERENCE-GPU index, not a physical rate for any lane's assembly. ⚠ **No gate decision was affected:** `REFERENCE_NS_PER_H` is in the numerator of `rung_ns_per_unit` and the denominator of `basis_usd_per_ns`, so it cancels out of BOTH ceilings — `ratio_vs_basis` and `projected_usd` are exactly invariant to system size (verified at 1.748x, 3.37x, 10x and 0.5x uniform slowdown, identical to 1e-9: `tests/test_throughput_is_an_index.py`). The residual, stated rather than closed: the cancellation is exact only for a UNIFORM factor, and card-ratio transfer from the water box to a real assembly is **untested** — one production point per card, no two cards sharing a leg. |
| 62 | **"Legs die during the ~28 min COLD START, before MD begins"** — reported 2026-07-31 by this session, and the ~28 min itself inherited from `retention_bid.py` | **MECHANISM RETRACTED, measured the same evening.** `phase.txt`'s own timestamp against the log's `[tvast] <utc> start`, on all four live 5a-KS legs: container start → `md-running` is **0.3 / 0.4 / 0.5 / 0.6 min**. MD begins within ~30 s because all three caches hit (23 of 27 attempts), exactly as `ternary-4fs-vast-findings.md`'s budget predicted ("~15 min of that is cached and will not repeat"). The ~28 min is **time to the first COMMIT**, dominated by one checkpoint interval of MD: 64 warmup iterations × the measured rate gives 19.5–35.7 min across the four legs. ⚠ **This changes the remedy**: not faster staging or a bigger host, but the CHECKPOINT INTERVAL — and that is a change for NEW legs only, because the interval is fixed when the .nc is created (`rbfe_spot_checkpoint.effective_interval`). It also explains why measure-on-arrival would have condemned nobody: the MD rate is fine, the interval is long. Not separated yet: minimisation and the setup restore both sit inside `md-running` before the first `[timing]` line. |
| 63 | **5a-KS warmup checkpoint interval 64 → 32** — approved 2026-07-31 to halve time-to-first-commit, on the arithmetic that a 3090 leg needs ~36 min to bank at 64 (~60 % of a ~1.00 h median session) | **APPLIED AND REVERTED THE SAME EVENING**, on the measurement the approval was explicitly conditioned on (*"price the upload, do not assume it … if the write is slow enough that 32 costs more in pauses than it saves, say so and stop"*). The committed `.nc` is **CUMULATIVE** — every commit re-uploads the whole trajectory so far — so the payload is a curve, not a constant: **76.3 MiB at iteration 40 → 5461.8 MiB at 1720** on one leg; median **699.5 MiB per commit** across 158 real generations, i.e. **28× the "~25 MB pair"** that `COMMIT_OVERHEAD_S = 23.0` was measured on. Halving the interval doubles the commit COUNT while each carries the cumulative payload (~+17.5 GiB per leg over warmup), and a ~1.3 GiB late-warmup commit against 586 s of MD would breach this lane's own `MAX_COMMIT_OVERHEAD_FRAC = 0.05`. ⚠ Reverting cost nothing: the four in-flight legs resume on the 64-grids baked into their own `.nc` files regardless (`effective_interval`), so 32 was **inert** for the current campaign. `rbfe_spot_checkpoint.commit` now self-times (`[barrier] commit …persisted N MiB in Ns`) and `setup_tax.commit_cost` parses it; one re-placement settles it. ★ The larger finding: re-uploading the full trajectory per commit makes total bytes **O(n²)** in commit count — that, not the interval, is the expensive property, and fixing it would make a shorter interval nearly free. |
| 64 | **"There is no fourth candidate staged"** (the standing tally closing the selcal NULL, 2026-08-02 morning); and §2.12a / §4's framing of that null as bounded between exactly two readings — *"the readout is blunt"* and *"this pair is hard"* | **Both were statements about the SEARCH, not about the repo, and the search had stopped one stage too early.** ⚠ **The tally was wrong:** two known-answer tests are already built and have never been run — **CREBBP vs BRD4(1) / SGC-CBP30** (`selectivity-benchmark.json`, fully specified with an `abfe_plan` and NO result key; both arms real holo crystals with the SAME ligand 4NR7/5BT4, experimental ΔΔG ≈ 2.2 kcal/mol) and a **pmx/GROMACS interface point-mutation ΔΔG** (the one physics lane here that recovered a published known answer: barnase–barstar Y29A +4.42 ± 1.08 vs +3.4, Y29F −0.37 ± 0.18 vs −0.13, ~$0.21/leg, image already baked). Neither is a positive control for paralogue *degradation* selectivity and neither is authorized — but "nothing is left" was not true. ⚠ **The two-way bound was also incomplete, and the third reading WEAKENS the result rather than rescuing it:** both registered readings assumed the simulated complexes were the complexes whose selectivity was measured, and scored against the deposited ternaries the panel was designed around, all 12 co-folds reproduce the internal VHL/EloB/EloC machinery at **DockQ 0.89–0.97** and the target↔VHL interface at **DockQ 0.023–0.046, fnat 0.000** — zero native interface contacts recovered, on either arm, by either of two independent implementations (the second being canonical DockQ 2.1.3). The endpoint was never exercised on the complexes in question, so the null bounds the WORKFLOW AS RUN rather than the readout alone, and the failing stage is ternary **generation** rather than ranking. ⛔ **Nothing here re-opens any selectivity claim; every paralogue-selectivity statement remains an unvalidated prediction.** Evidence: `selcal-cofold-vs-crystal.json`, `selcal-cofold-dockq.json`, `structural-provenance-census.json` |
| 65 | The DeepTernary lane's standing description of its 9DTY/9DTX arms as **BLIND** — in `selcal-deepternary-headtohead.yml`'s header, `selcal_deepternary_score.py`'s docstring and artifact keys, the STATUS doc's *"a known-answer ternary test, run blind, that the workflow passes"*, and the implicit step from *absent from the disclosed exclusion set* to *blind* | **RETRACTED 2026-08-02 from DeepTernary's OWN released data, not from an argument.** `output.zip` ships the finished unbound inputs for all 22 benchmark cases, and in `6HAX_B_A_FWZ`: `ligand.pdb` is **byte-identical to the native ligand of `gt_complex.pdb` — max deviation 0.000 Å across all 66 heavy atoms**; `unbound_protein1.pdb` (a different entry, chain I, 1150 atoms vs the native's 1201) sits at centroid (−21.6, 17.3, −20.3) against the native POI's (−21.3, 17.6, −20.7), and `unbound_protein2.pdb` matches the native E3 the same way; 33 of 66 ligand atoms then fall within 1 Å of `unbound_lig1` and 18 within 1 Å of `unbound_lig2`. So the published **UNBOUND protocol superposes both binaries into the native ternary frame and supplies the native degrader pose** — it is blind to the two proteins' *relative placement* (protein 2 and the ligand are each randomly rotated and translated before the forward pass, and `gt_complex.pdb` is read at exactly one line, `cal_dockq`), and **not** blind to which pocket each ligand end occupies. ⚠ **This is what the two dead runs were telling us**: our `ligand.pdb` was the CCD ideal conformer in an arbitrary frame, so `replace_to_unbound_coords`' 1 Å proximity mask was empty and the reduction over it died — the empty tensor was the model correctly reporting that nothing had been positioned, and the constrained-embed fix drafted for it would have answered a different question. **The leakage check still holds and is still necessary; it is no longer sufficient** — exclusion-set membership bounds *memorisation*, not *what the inputs hand the model*. Consequence: the selcal arms' number may never be set beside our sequence-only co-folds' 0.023–0.046 as though the two were one test, and the positive control moved to a separate, honestly-labelled in-set case (`selcal-deepternary-poscontrol.json`, 6HAX). Enforced by `tests/test_selcal_deepternary_frame.py`, which fails on an unretired "blind" claim; construction verified by `selcal_deepternary_frame.reproduce_reference` (displace the shipped inputs 63°/40 Å, re-derive the frame, snap masks return 33→33 and 18→18, no pinned number compared against) |

---

## Appendix B — superseded strategy framings

*★ **APPENDIX — retired plan framings.** CLAUDE.md §5 points here. Its closing inference-discipline paragraph is live, not history: NR-V04 is event-level evidence that family-selective NR4A degradation is achievable — never evidence that the mechanism is known or transferable.*

*Moved out of CLAUDE.md 2026-07-25, where 168 lines of plan mirror had accreted (including two blocks already
labelled superseded) in the file that loads into every session. Plan history belongs with the plan. Same rule as
Appendix A: kept so a decision is never silently dropped, out of the live text so it stops competing with it.*

| framing | status |
|---|---|
| **Atlas-anchor reframe** (2026-07-11 AM) — the repo's #1 priority is an EMC treatment anchored by the **EMC Open Target & Drug Atlas** (`research/atlas/`: proteostasis-chromatin; fusion-subtype antiangiogenic biomarker; fusion-junction + lineage antigens; direct fusion targeting) + collaborator outreach | **Superseded the same day** by the degrader-primary decision (trimcrae + gate-AI). The atlas *work* stays valuable as **support** — biological rationale, fusion-vs-WT biology, anti-target liabilities, an assay roadmap for collaborators, and the **backup route** if degrader design fails — but it must not absorb most effort via indefinite evidence aggregation. Its own state: `research/atlas/README.md` + `STATUS.md` |
| **Two-papers-first plan** (2026-06-26) — publish (1) the NR4A3-degrader result paper and (2) the fusion-junction ASO paper, with the EMC-program roadmap and the fusion-exclusivity framework in the next tier | Still the portfolio shape, but the degrader paper is now the ≈70–80% program and the ASO paper is support. Route board: [IDEAS.md](research/IDEAS.md); capstone ranking: [emc-treatment-strategy.md](research/manuscripts/emc-treatment-strategy.md); why splitting the degrader paper out serves rather than replaces the EMC goal: [nr4a3-degrader-paper-positioning.md](research/manuscripts/nr4a3-degrader-paper-positioning.md). The ASO route's one remaining gate is **delivery** |
| **Three-step spine** — (1) FEP converges on cmpd19 → (2) replicate NR-V04's selectivity in silico → (3) design + ternary-test on the cmpd19 anchor | **Superseded as the ORDERING** by the 2026-07-15 reviewer verdict (the thesis is unchanged). NR-V04 is a *holdout*, not the calibrator, and runs *after* the known-answer SMARCA2/VHL control. The ordered plan above is authoritative |
| **Track A** — qualify an NR4A3-engaging warhead via repaired ABFE (`denovo_401` as a credible design input) | **SHELVED 2026-07-15** — parked, not deleted. `denovo_401` is a **side comparator / benchmark, not a lead**. Revisit only if the ternary workflow needs an absolute-affinity anchor that a coming method makes cheap |
| **Orientation-first** prospective search | **Superseded 2026-07-24** by mechanism-first (§Program and thesis). Orientation is still the second stage; it is no longer the first |
| **PR #3 coordination note** (`claude/emc-research-strategy-kdz9kn` set atlas-primacy) | Resolved — merged and reconciled to degrader-primary |

**One inference discipline worth keeping from that history, because it is easy to overclaim:** NR-V04 is
event-level proof that family-selective NR4A degradation is *achievable*, which is what makes this program
credible and rebuts "the family is too homologous." It is **not** proof that the structural mechanism of that
selectivity is known, solved, or transferable — there is no solved ternary and no matched cross-paralogue
cooperativity measurement. Never claim the latter.
