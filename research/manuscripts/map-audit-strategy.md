# Audit — every factual claim in `nr4a3-program-map.md` against STRATEGY.md and the committed artifacts

**READ-ONLY AUDIT, $0.** No GPU, no CI dispatch, no rental. Every check below is a read of a committed file, a
`git show` of a prior blob, a local `python3` run, or a public GitHub Actions API read.

**Audited:** `research/manuscripts/nr4a3-program-map.md` at commit `f67d0781` (459 lines, 2026-08-02
4:07 PM ET), against `STRATEGY.md` (3230 lines, HEAD), `research/manuscripts/nr4a3-degrader-paper.md`,
`research/manuscripts/pinned-figures.json` and the artifacts under `research/modalities/`.
Line numbers are the live file's; the map moved twice during the audit (`96f5543f` → `f67d0781`), and every
finding below was re-confirmed against the later version.

**Out of scope, by instruction** (other agents hold these): map §5 branch **1b** and anything about
`nr4a3_linker_covalent_reach`; the pose rows and `apo-pose-recovery.json`; map §2's dead-end/parked register.
Where an audited section's *state* depends on an excluded one, the finding is about the state only and says so.
§2 rows checked incidentally are listed at the end and are **not** counted in the totals.

**Method note.** Per CLAUDE.md §4b a populated field is not a measured one, so for every artifact-backed number
the check was against the field only a real run can produce — a per-model `n_accessible` count, a per-frame
distance distribution, a dispatch log's env block — never a summary line that a default could fill.

---

## Verdict counts

| verdict | n |
|---|---|
| **CONTRADICTS** | **10** (1 already fixed mid-audit by a concurrent agent) |
| **STALE** | **4** (3 of them in STRATEGY.md, not the map) |
| **UNSOURCED** | **6** |
| **UNVERIFIABLE** | **2** |
| **AGREES** | **24** |

**Headline:** 10 contradictions, 6 unsourced claims. **The single most damaging error is finding 1** — map §6
item 4, the ternary rebuild that the §1 graph names as the paper's blocker, is marked ◐ **in work** when no
module, workflow, artifact, rung, gate or price for it exists anywhere in the repo. §0 defines ◐ as *"dispatched
or building right now — wait for it; **don't start a second copy**"*, so the map instructs a reader not to start
the one item it identifies as blocking the paper.

---

# CONTRADICTS

## 1 · `◐ in work` on a lane that does not exist — the ternary rebuild ⛔ MOST DAMAGING

| | |
|---|---|
| **Claim** | *"**Rebuild the ternaries by the assembly route**, from a molecule whose structure is recorded this time \| **◐ in work**"* |
| **Map** | `research/manuscripts/nr4a3-program-map.md:439` (§6 item 4); relied on at `:119` (§1 caption) and `:441` (item 6 "gated on 4") |
| **STRATEGY.md** | `STRATEGY.md:511–513` — prose only: *"The next step is therefore in-silico and specified: rebuild the three paralogue ternaries by the assembly route (opened LBD + docked warhead pose as site 1; CRBN + IMiD from a binary crystal as site 2; a degrader whose SMILES is recorded this time), then re-run (f)."* It appears in **no** rung of §THE ORDERED PLAN, **no** row of §Dependency spine (`:2577`), and **no** rank of §6's decision-value list (`:2753–2764`). No price, no gate. |
| **Artifact that should own it** | none exists |
| **What the evidence actually says** | `grep -rl "assembly route\|assembly_route\|rebuild the ternar"` over `research/` and `.github/` returns **the map itself and nothing else**. No `.py`, no `.yml`, no `.json`. Live compute, three independent reads: `research/modalities/inflight-board-all.md` (merged 4:05 PM ET) prints `IN-FLIGHT BOARD: no GPU legs.` for all four Vast lanes; `research/modalities/ternary-vast-account-census.json` (`utc 2026-08-02T19:56:10Z`) reports `n_instances: 0`; `research/modalities/vast-account-reaper.json` (4:05 PM ET) `verdict: NOTHING-TO-REAP`. |
| **VERDICT** | **CONTRADICTS** (and UNSOURCED) |

**Why this is the worst one.** §1's caption (`:119`) says the PAPER node is blocked because *"the ternary claim
rests on a molecule that cannot be recovered, so it needs the §6 step-4 rebuild"* — and then §6 step 4 reads
◐. STRATEGY.md `:500` is unambiguous that this is the program's largest open gap: *"**Is there a
correctly-assembled ternary to point it at?** ⛔ **NO, and this is the whole remaining gap.**"* A reader
following the map's own §0 semantics will **not start it**, because ◐ tells them someone already has. Nobody
has. The correct state is **○ future**, and the correct next action is to give it a rung and a price in
STRATEGY.md — which its own §6 note anticipates: *"**A caveat with nowhere to go is how work gets silently
dropped**"* (`STRATEGY.md:2767–2769`).

## 2 · The same node carries four different states, and STRATEGY.md says the answer is NO

| | |
|---|---|
| **Claim** | §1 graph node `ARCH["✓ Ternary correctly ASSEMBLED"]`, classed `done` |
| **Map** | `:82` (node), `:109` (`class PO,ARCH,V1,V2 done`) |
| **STRATEGY.md** | `:500–505` — *"**Is there a correctly-assembled ternary to point it at?** ⛔ **NO, and this is the whole remaining gap.** The existing NR4A ternaries are sequence-only co-folds from the route (d) measures as failing at assembly by a factor of 10, and the molecule that produced them is **unrecoverable**"* |
| **Artifact** | `research/modalities/nr4a-ternary-ligand-provenance.json` — `n_recovered: 0`, `n_arms: 3`, `sentence: "REFUSED — no arm's degrader could be recovered with sourced bond orders…"` |
| **VERDICT** | **CONTRADICTS** |

The same proposition is stated at **four** states inside two files: map §1 `ARCH` = **✓**; map §4 row *"A ternary
forms"* (`:245`) = **○ future**; map §6 item 4 = **◐**; STRATEGY.md `:500` = **⛔ NO**. That is a rule-1 violation
*within a single document*. If `ARCH` was meant as the *capability* to assemble (validated by `V2`, DeepTernary's
9DTY DockQ 0.839) rather than the *claim* that our ternary is assembled, then it duplicates `V2` and belongs on
the dashed instrument layer — but its label says the claim, and §0 requires exactly one state per node.

## 3 · §4 quotes a value that `pinned-figures.json` registers as superseded — and the linter's regex misses it

| | |
|---|---|
| **Claim** | *"**4 of 20 conformers** of the experimental apo NMR ensemble **8XTT** are cavity-bearing"* |
| **Map** | `:241` (§4 row 1, "A pocket exists", state ✓ complete) |
| **STRATEGY.md** | `:3150` — **Appendix A row 12**, i.e. the superseded register: *"8XTT: **4/20** conformers above D\* \| The harmonized rerun (pinned fpocket + score-independent matcher) reports **19/20 detected, 3 ≥ D\*** = 3/19 among detected, **3/20** across all deposited"*. Appendix A's own header (`:3135`): ***"Do not cite anything in this table."*** |
| **Artifact that owns it** | `research/modalities/nr4a3-pocket-reharmonize-summary.json` → row `8xtt_20conformers`: `n_propagated: 20`, `n_detected: 19`, **`n_ge_dstar: 3`**, `frac_ge_among_propagated: 0.15` |
| **Paper** | `nr4a3-degrader-paper.md:180–186` states the correction explicitly, *"one fewer than the original 4/20"* |
| **VERDICT** | **CONTRADICTS / STALE** |

**And the machine guard was in place and did not fire.** `pinned-figures.json` → `superseded[19]`, id
`xtt_pre_harmonized`, pattern `4/20 (above|conformers)|placed \*\*4/20\*\*`, current
`19/20 detected, 3 ≥ D* (= 3/19 among detected, 3/20 across all deposited)`. The map **is** one of the 12
`targets`. The map writes *"4 of 20 conformers"*, which the regex does not match. `python3
research/manuscripts/lint_consistency.py` run locally during this audit: **`0 ERROR across 12 target file(s)`**.
So a green `lint_consistency` is currently *not* evidence the map is clean. Fix is two lines: correct `:241` to
3/20 and widen the pattern to `4[ /](of )?20`.

## 4 · "an ~80 %-identical pocket" is the SMARCA2/SMARCA4 number, transplanted onto NR4A

| | |
|---|---|
| **Claim** | *"instead of asking the warhead to discriminate an **~80 %-identical pocket**, put the electrophile on the **linker**"* |
| **Map** | `:411` (§5b Route B, chemical basis) |
| **STRATEGY.md** | `:402` — *"**SMARCA2/SMARCA4 bromodomains are ~80 % identical** and the published selectivity turns on a single Gln1469 hydrogen bond"*. Also `nr4a3-degrader-paper.md:2109`, same pair. |
| **Artifact for the real NR4A figure** | `research/modalities/nr4a-selectivity.json` → pocket 5: `n_residues: 10`, `n_divergent: 7` ⇒ the pocket lining is **30 % identical**. `research/modalities/nr4a3-differential-surface-atlas.json` → `summary.counts`: `n_residues_aligned: 254`, `n_divergent_any: 109`, `pct_divergent_any: 42.9` ⇒ the LBD is **≈57 % identical** (mirrored at `STRATEGY.md:494–496`). |
| **VERDICT** | **CONTRADICTS** |

Nothing in the repo puts the NR4A paralogue pocket at ~80 % identity. The number belongs to a different protein
pair studied for a different reason. It matters because Route B's entire rhetorical case is *"Route A is asking
the warhead to do something very hard, so use the linker instead"* — and it argues that against the map's own
Route A, sixteen lines earlier, which reports **7 of 10** lining residues divergent. On the map's own numbers the
premise is backwards.

## 5 · C559 is called "exposed"; by the module's own criterion it is exposed in **0 of 20** conformers

| | |
|---|---|
| **Claim** | *"\| C397, C420, C559 \| no — **11–19 Å**, linker-tether range \| **yes**, and exposed \|"* |
| **Map** | `:299` (§5 branch 1 table) |
| **STRATEGY.md** | `:984` — *"**C559** (12.8 Å but RSA 0.095 — **buried in this conformer, so not currently tether-reachable**)"* |
| **Artifact** | `research/modalities/nr4a3-covalent-handle-ensemble.json` → `ensembles.NR4A3_8xtt_nmr.cysteines`: **C559** `n_accessible: 0` of 20, `n_flagged: 0`, RSA min 0.155 / median 0.205 / **max 0.240** against the pre-specified `EXPOSED_RSA = 0.25`. **C420** `n_accessible: 16` of 20, not 20. **C397** `n_accessible: 20`. The `.md` companion's own table (`nr4a3-covalent-handle-ensemble.md:78–84`) prints "flagged in" 20/20, 16/20, **0/20**. |
| **VERDICT** | **CONTRADICTS** |

**This is self-inconsistent within the same section.** Three lines below, `:302`, the map uses that exact
criterion to condemn the positive control: *"NR4A1 **Cys551** … does not pass the pre-specified exposure cutoff
… in **0 of 25** frames."* NR4A3's own C559 fails the identical test in 0 of 20 and is nonetheless printed as
"exposed". The honest cell is *"C397 yes (20/20); C420 mostly (16/20); **C559 no — 0/20**, and the rank
reading is what carries it"* — which is also what the artifact's `criteria_diagnosis` says should be quoted.

## 6 · The three-attempts-at-E1 mis-attribution — ✅ **FIXED MID-AUDIT**, recorded for the register

| | |
|---|---|
| **Claim (as audited at `96f5543f`)** | *"Interface-stability endpoint (E1) \| three attempts: **cooperativity calibrator**, NR-V04 retrospective, SMARCA2/4 control \| wrong sign · p = 0.393 · p = 0.747"* |
| **STRATEGY.md** | `:87–89` — *"⚠ **#1 AND #2 ARE DIFFERENT INSTRUMENTS** … #1 is alchemical ternary FEP, #2 is endpoint-MD E1."* Repeated at `:341–344`: *"**DO NOT CONFLATE THIS WITH THE SENSITIVITY-CONTROL NULL BELOW** … reading them as one finding would overstate both."* |
| **VERDICT** | **CONTRADICTS — resolved at commit `f67d0781` (4:07 PM ET)** |

The live table now reads *"**two** attempts"* for E1 and gives `valB_mini ΔΔG_coop` its own row. Kept here
because the register must not lose the correction, and because the identical conflation still stands in **§2b's
parked row**, which is out of audit scope but should be reconciled to the same fix.

## 7 · "the single highest-leverage item in the program" is an item STRATEGY.md does not authorize

| | |
|---|---|
| **Claim** | *"its selectivity benchmark (CREBBP vs BRD4(1), SGC-CBP30) was built and staged with no `result` key, and its first leg is now on spot … **This is the single highest-leverage item in the program, and it is the one thing moving.**"* |
| **Map** | `:400–404` (§5b Route A); `:223` (§3 row 4, "solvent leg dispatched; full pass priced", ◐); `:440` (§6 item 5, ◐) |
| **STRATEGY.md** | `:531–532` — *"Two known-answer tests are already built and **have never been run**"*; `:546` — *"**Neither is authorized here** and neither is a positive control for paralogue *degradation* selectivity."*; `:536–538` — *"⛔ It is a **binary** selectivity control and would **not** discharge §4's paralogue/ternary statement."* It appears in no rung of the ordered plan and on no rank of §6's list; the nearest ranked item, rank **9 of 9** (`:2763`), is *"A known-answer calibrator for the `S`-shaped quantity \| **unpriced** \| … **It unlocks nothing on its own** … so it **follows 4 rather than leading it**."* |
| **Artifact** | `research/modalities/selectivity-benchmark.json` — confirmed **no `result` key**; `ddg_kcal_per_mol: -2.19` (map's "≈ 2.2" ✓). `research/modalities/abfe-selectivity-benchmark-cost.json` → `cases.1_replicate.usd: 8.48`, range `[4.74, 14.88]` — so *"full pass priced"* **is** sourced. |
| **VERDICT** | **CONTRADICTS** on priority and authorization; the *status* half is true but unsourced (see finding 15) |

**Both cannot stand.** The dispatch is real — public Actions run **30762989810**, job **91536747799**, dispatched
2026-08-02 **3:16 PM ET** on `main`, env `ABFE_TAG: sel-cbp30-v1`, `ONLY_LEGS: solvent`, `SPOT: 1`,
`INSTANCE: ml.g5.xlarge`, log line `[abfe] launched solvent (solvent/shared):
sel-cbp30-v1-solvent-2026-08-02-19-16-52-862`. So `STRATEGY.md:531/546` is now the stale side and needs
correcting. But the map's *ranking* claim has no basis in STRATEGY.md at all, and STRATEGY.md's explicit bound
(a **binary** control that does not discharge the paralogue statement) is a limit the map's §5b omits while
resting Route A on it. Note also: the lane runs on **AWS SageMaker**, not the standing Vast default, the map
names no provider (CLAUDE.md §6 requires it), and the lane appears on **no** row of `inflight-board-all.md`.

## 8 · §3's closing pattern claim is contradicted by its own table and by STRATEGY.md

| | |
|---|---|
| **Claim** | *"★ **The pattern.** Every instrument put to a known-answer test **either passed cleanly or failed cleanly.**"* |
| **Map** | `:229` |
| **Contradicted by** | its own table two rows up, `:224`: *"✓ complete — **verdict INCONCLUSIVE**"*; and `STRATEGY.md:71`, which classifies the NR-V04 retrospective as *"⚠ **NON-RESOLUTION**, never a candidate control"* and `:377` *"a non-resolution rather than a negative"* — explicitly neither a clean pass nor a clean fail. |
| **VERDICT** | **CONTRADICTS** |

The table's real pattern is stronger and honest: *every instrument put to a known-answer test returned a
readable verdict — two passed, two failed, one did not resolve, one was inconclusive — and every withdrawn
selectivity claim came from an instrument that was never tested.*

## 9 · §1 makes "Target is a driver" a feeder of PAPER; the paper says it is not

| | |
|---|---|
| **Claim** | `TG["○ Target is a driver (EMC dependence)"]` with edge `TG --> P` |
| **Map** | `:77` (node), `:97` (edge); map §4 row 7 (`:247`) simultaneously states *"○ future — **outside scope**"* |
| **Paper** | `nr4a3-degrader-paper.md:2508` — *"the **make-or-break dTAG test is delegated to the EMC-program paper** … **This paper's claimed contribution is the target's computational druggability/selectivity, not EMC efficacy.**"* |
| **VERDICT** | **CONTRADICTS** |

The map's own §1 caption (`:119`) names only `B` and `TS` as PAPER's blockers, conceding that `TG` does not
block it — while the graph draws `TG → P` as an equal solid dependency. On the paper's stated scope `TG` is a
**delegated** precondition of the therapeutic claim, not of this paper. Either drop the edge or mark it
delegated.

## 10 · "three cysteines the paralogues lack", unqualified, against STRATEGY.md's "4 of 20"

| | |
|---|---|
| **Claim** | *"NR4A3 has **three** cysteines the paralogues lack — C397, C420, C559"* |
| **Map** | `:293` |
| **STRATEGY.md** | `:941` — *"**Only 4 of NR4A3's 20 enumerated cysteines are unique; 16 are SHARED** — and one of the shared ones is inside the design gate."* |
| **Artifact** | `research/modalities/nr4a3-covalent-handle-ensemble.json` → `nr4a3_unique_lbd_cysteines: [397, 420, 559]`, `nr4a3_lbd_cysteines` = 7 entries. The artifact is scoped to the **LBD**; STRATEGY.md's 4/20 is **full-length**. |
| **VERDICT** | **CONTRADICTS** as written — resolved by adding one word: *"three **LBD** cysteines"* |

The map uses the LBD qualifier correctly nine lines later (`:304`, *"all 18 NR4A-family **LBD** cysteines"*), so
this is an omission rather than a wrong number. But unqualified it reads as a whole-protein count that
STRATEGY.md contradicts, and the whole-protein count is the one that matters to the design (STRATEGY.md's point
at `:941` is precisely that a *shared* cysteine sits inside the gate).

## 11 · Two different measurements merged into one sentence about the positive control

| | |
|---|---|
| **Claim** | *"NR4A1 **Cys551** … does not pass the pre-specified exposure cutoff (**RSA 0.165** against 0.25) in **0 of 25** frames"* |
| **Map** | `:301–303` |
| **Artifact** | `nr4a3-covalent-handle-ensemble.md:28–30` keeps them apart: *"state-matched opened model: RSA **0.165**"* (n = 1) **and** *"across the 25-frame NR4A1 metadynamics ensemble: RSA 0.026–0.223 (**median 0.064**) … flagged in **0/25** frames"*. The JSON agrees: `ensembles.NR4A1_metad.cysteines.551` → `rsa.median 0.064`, `rsa.max 0.223`, `n_accessible 0` of 25. |
| **VERDICT** | **CONTRADICTS** (minor) — both facts true, of different objects |

As written it reads as RSA 0.165 in each of 25 frames. The ensemble median is 0.064 — **2.6× lower** — which
makes the control fail *harder* than the map states, not softer. Worth fixing because the rank argument that
replaces the cutoff is built on the single opened model (`control_rank.pool = "all cysteines of NR4A1, NR4A2,
NR4A3 **state-matched opened models**"`), and conflating the two blurs which pool the 3/18 rank came from.

---

# STALE

## 12 · The 76 % thiol-occlusion figure was superseded 10 minutes after it was written

| | |
|---|---|
| **Claim** | *"the thiol's **own HG proton occludes a median 76 %** of the SG surface"* |
| **Map** | `:309–311` |
| **Artifact now** | `nr4a3-covalent-handle-ensemble.json` → `thiol_hydrogen_occlusion.fraction_occluded`: `n: 16`, `min: 0.21`, `q1: 0.643`, **`median: 0.918`**, `q3: 1.0`, `max: 1.0`, `mean: 0.777`. The `.md` companion (`:56`) prints *"**0.21–1.0** of the SG surface (median **0.918**)"*. |
| **Where 76 % came from** | commit **`4381c2a6`** (2026-08-02 2:31 PM ET), first generation of the artifact: `{"n": 12, "median": 0.764, "mean": 0.729}`. Superseded six minutes later by `a5d026ad` (2:37 PM ET) and again by `70fed0ff` (2:41 PM ET), both `n: 16, median: 0.918`. |
| **VERDICT** | **STALE** — correct value **≈92 %** (median), or **78 %** if the mean was intended |

Neither 0.918 nor 0.777 rounds to 76 %. The map was written off the artifact's first generation and not
re-read after the 960-point regeneration. Everything *else* in the same paragraph survived that regeneration
and is verified below (finding A8).

## 13 · STRATEGY.md's gate-failed header is stamped ~7 hours in the future

| | |
|---|---|
| **Claim** | `## ❌ GATE FAILED — the SMARCA2/4 sensitivity control returns **NULL** on an adequately-powered design **(2026-08-02 10:42 PM ET)**` |
| **STRATEGY.md** | `:351` |
| **Artifact that owns it** | `research/modalities/selcal-verdict.json` → **`utc: "2026-08-02T02:43:16Z"`** |
| **Correct value** | EDT = UTC−4 ⇒ **2026-08-01 10:43 PM ET**. Current time when this audit ran: **2026-08-02 4:05 PM ET**, so the header is dated ~6 h 40 m in the future. |
| **VERDICT** | **STALE / wrong** |

**Root cause, from the data rather than guessed:** the clock face was converted and the calendar date was not.
`02:43 Z` → `10:43 PM` is the correct 12-hour conversion; the date must roll back from 08-02 to 08-01 at the
same time and did not. (The minute is also off by one — 10:42 against the artifact's :43:16.) This is exactly
the slip CLAUDE.md §1 ⏰ flags as recurring. `git log -S` on the header string returns only the repo-wide
squash commit `8f3e3732`, so history cannot date the edit independently; the artifact's own UTC stamp is the
authority and is unambiguous.

## 14 · STRATEGY.md's IN FLIGHT board is 3 days stale and cannot see the lanes that have billed since

| | |
|---|---|
| **Claim** | `## ⏱️ IN FLIGHT — what is actually running right now (as of **2026-07-30 5:30 PM ET**)`, and inside it `:566` *"**NOTHING IS BILLING. Every lane on this board is off a host.**"* |
| **STRATEGY.md** | `:552`, `:566`; scoreboard `:56–58` *"As of 2026-08-02 3:30 AM ET … **NOTHING BILLING on Vast**"* |
| **What it claims is running** | Nothing. Six of its seven rows are struck-through complete (step-1 fan-out; valB_mini r1+r2; RUNG 5a-KS, landed 2026-08-02; the closure triangle; valB reverse leg r0; LANE 13). The seventh, *"The restrained binary re-run (LANE 20)"* (`:578`), is **HELD ON PURPOSE**, `$0`, gated on the pose diagnostic — measured 2026-07-31 11:08 AM ET and *"has still never run"*. |
| **Is any of it still true?** | **Yes for Vast, and verified three ways at $0:** `ternary-vast-account-census.json` `utc 2026-08-02T19:56:10Z` → **`n_instances: 0`**; `inflight-board-all.md` (4:05 PM ET) → `no GPU legs` on all four Vast lanes; `vast-account-reaper.json` (4:05 PM ET) → `census_n_instances: 0`, `verdict: NOTHING-TO-REAP`. |
| **VERDICT** | **STALE** — the header, not the rows |

Two real gaps behind the stale stamp, both of which the header's own as-of makes invisible:

1. **The SMARCA2/4 selcal panel billed after the as-of and is not on the board.** Its own fragment in
   `inflight-board-all.md` reads *"instance **46560490** running, rented **2026-08-02T02:30:30Z**"* — i.e.
   **10:30 PM ET Aug 1**, hours *after* the header's 2026-07-30 as-of and hours *before* the scoreboard's
   "NOTHING BILLING on Vast (3:30 AM ET Aug 2)". That fragment is now **1047 min stale** (>17 h). The host is
   in fact gone (`n_instances: 0`), so nothing is billing unsupervised — but the board could not have told
   anyone that, which is the failure shape CLAUDE.md §4 records from 2026-08-01.
2. **Today's CREBBP/BRD4 ABFE solvent leg is on no board at all.** Dispatched 3:16 PM ET to AWS SageMaker
   managed spot (finding 7). `inflight-board-all.md` is scoped to Vast + GCP lanes, and STRATEGY.md's board
   says "on Vast" — so a non-Vast rental is structurally invisible to both. Priced at `$8.48` (range
   `$4.74–14.88`, `abfe-selectivity-benchmark-cost.json`), well inside the autonomy threshold, so this is a
   reporting gap and not a spend问题 — but it means "nothing is billing" is true only of one provider.

## 15 · STRATEGY.md quotes a DeepTernary median its own artifact no longer holds

| | |
|---|---|
| **Claim** | *"reaches **DockQ 0.618 (CAPRI "Medium"), median 0.438 over 16 scored poses**, best iRMSD 1.21 Å"* |
| **STRATEGY.md** | `:420–421` |
| **Artifact** | `research/modalities/selcal-deepternary-poscontrol.json` → `summary`: `best_DockQ 0.6178` ✓, **`median_DockQ 0.4143`**, `best_iRMSD_A 1.2114` ✓. Recomputed from the 16 `poses`: true median **0.4087**. |
| **Where 0.438 came from** | the previous commit of that artifact, `5913ae83`: `{"best_DockQ": 0.6185, "median_DockQ": 0.4376, "best_iRMSD_A": 1.2109}` |
| **VERDICT** | **STALE** (STRATEGY.md only — the map's §3 row 2 quotes no median and is clean) |

---

# UNSOURCED

## 16 · "5 stay pocket-facing" has no committed artifact, and the paper says so in the sentence the map skips

| | |
|---|---|
| **Claim** | *"in the opened druggable ensemble **5 stay pocket-facing** (L406, T410, I484, I531, L534), so those five are the realistically engageable handles"* |
| **Map** | `:394–395`, cited to *"[`nr4a-selectivity.json`](../modalities/nr4a-selectivity.json), paper §2.4"* (`:392–393`) |
| **Artifact cited** | `research/modalities/nr4a-selectivity.json` — top-level keys are `_note`, `paralogues`, `nr4a3_lbd_pockets` only. It contains pocket lining and paralogue divergence. **It contains no facing data at all.** |
| **Artifact that should own it** | `handle_facing_summary.json` — **does not exist in this repository.** `ls research/modalities/ \| grep -i facing` returns three `.py` files and no artifact. |
| **Paper** | `nr4a3-degrader-paper.md:561–566`, verbatim: *"**Artifact status:** these fractions are recorded in the committed run ledger … but the primary output `handle_facing_summary.json` is an **S3-only object that is not committed to this repository**, so the numbers are traceable to a run record rather than to a checked-in artifact; they are quoted here at that weight."* And `:552–554`: *"computed under the **pre-harmonized** tracker and **not** re-run under the harmonized one, so it is **reported but not treated as confirmed**, since the set of druggable frames it is computed over is the **superseded** one."* |
| **VERDICT** | **UNSOURCED** |

Three separate defects in one cell. **(a)** The cited artifact does not hold the number. **(b)** The number is
§2.3, not §2.4. **(c)** The paper explicitly refuses to treat it as confirmed — because the druggable-frame
denominator it is computed over is the same superseded pre-harmonized set as finding 3 — and the map states it
flatly, then builds Route A's whole engageable-handle conclusion on it. This is the map's own banner (`:11`,
*"STATUS VALUES ARE READ FROM COMMITTED ARTIFACTS, NEVER TYPED HERE"*) failing on the section it calls the
program's highest-leverage route.

## 17 · Route A drops the paper's paralogue-resolved narrowing: only **4** of the 5 handles distinguish NR4A2

| | |
|---|---|
| **Claim** | *"7 are paralogue-divergent — L406, T407, T410, R412, I484, I531, L534 — and … **5 stay pocket-facing** … so those five are the realistically engageable handles"*, with no qualifier |
| **Map** | `:393–395` |
| **Artifact** | `nr4a-selectivity.json` → pocket 5 residue rows. **I531: `nr4a3 "I531", nr4a1 "V", nr4a2 "I"`** — identical in NR4A2. Six of the seven differ from both; I531 differs from NR4A1 only. |
| **Paper** | `:606–611`, in bold: *"Against **NR4A2**, only **6 of 7** differ — **I531 is identical (Ile in both NR4A3 and NR4A2)** — so of the 5 engageable handles, only **4** distinguish NR4A3 from NR4A2 (L406, T410, I484, L534; I531 drops out). NR4A2 selectivity therefore rests on a **narrower** engageable set … which matters because NR4A2/Nurr1 is the paralogue carrying the dopaminergic-loss liability one most wants to spare."* Repeated at `:2421–2422` and `:2568–2569`. |
| **VERDICT** | **UNSOURCED / materially incomplete** |

This is the same defect the map itself states as definitional in §2a — *"A residue the paralogues share cannot
discriminate between them"* — applied to the route the map ranks first. The paper carries the caveat in three
places; the map carries it in none.

## 18 · The ortholog claim cites a module, and its artifact is on neither this branch nor `main`

| | |
|---|---|
| **Claim** | *"★ **And all ten are ortholog-invariant across six species spanning ~300 My** (`nr4a3_resistance_map.py`)"* |
| **Map** | `:397` |
| **Artifact** | `nr4a-resistance-map.json` — **absent** from `HEAD`, absent from local `main`, absent from `origin/main`. It exists only on `remotes/origin/modalities-cache` (blob `ec25568b`, commit `06349baa`). |
| **What that blob says** | `summary.durable_anchors: [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]`, `resistance_liable: []`; every one of the 10 rows carries `ortholog_conserved_fraction: 1.0`; `orthologs_used` = MOUSE, RAT, BOVIN, PIG, CHICK (5, + human = 6); `orthologs_dropped_low_identity: {XENTR 0.593, DANRE 0.578}`; identities 0.792–0.949 (paper's "0.79–0.95" ✓). |
| **VERDICT** | **UNSOURCED on this branch and on `main`** — content AGREES where the artifact lives |

CLAUDE.md §7 exactly: *"never let a branch a workflow runs from be the only home of an artifact … Before
writing ANY claim from a committed artifact, check which ref the producing workflow actually writes to."* The
producer is also allowed to fail silently — `.github/workflows/depmap-dependency.yml:59` runs it with
`|| echo "resistance-map soft-fail (network); non-blocking"` and copies the output with `2>/dev/null || true`.
Separately, **"~300 My" appears in no artifact**; it is a literature inference carried in prose
(`nr4a3-degrader-paper.md:623`, `nr4a3-degrader-insilico-completeness.md:144`).

## 19 · "solvent leg dispatched" / "its first leg is now on spot" — true, but from no committed record

| | |
|---|---|
| **Claim** | §3 row 4 *"solvent leg dispatched; full pass priced \| ◐ in work"*; §5b *"its first leg is now on spot"* |
| **Map** | `:223`, `:402–403` |
| **Artifacts** | `selectivity-benchmark.json` — **no `result` key, no dispatch record**. `abfe-selectivity-benchmark-cost.json` — a cost model only; it prices the pass and records nothing about a run. Neither `inflight-board-all.md` nor any `inflight-board.d/` fragment carries this lane. |
| **How it was verified** | public Actions API, $0: run **30762989810** (`gpu-abfe-aws.yml`, `workflow_dispatch`, `main`, 2026-08-02T19:16:11Z = **3:16 PM ET**, `success`, 37 s), job **91536747799**, log env `ABFE_TAG: sel-cbp30-v1` · `ONLY_LEGS: solvent` · `SPOT: 1` · `INSTANCE: ml.g5.xlarge` · `RECEPTOR_PREFIX: selectivity-benchmark`, and `[abfe] launched solvent (solvent/shared): sel-cbp30-v1-solvent-2026-08-02-19-16-52-862`. |
| **VERDICT** | **UNSOURCED** (claim is correct) |

The map's banner says status is read from artifacts and never typed. This one was typed. The fix is a
one-field write into `selectivity-benchmark.json` (or a lane fragment) recording the SageMaker job name and
dispatch time, plus an `inflight-board.d/` fragment so the lane is visible on the all-lane board at all.

## 20 · "a free-energy engine that has never recovered a known ΔΔG" — unqualified, and its own §3 disagrees

| | |
|---|---|
| **Claim** | *"the binder claim rests on **a free-energy engine that has never recovered a known ΔΔG**"* |
| **Map** | `:116` (§1 caption). Note `:402` gets it right — *"**the ABFE engine** has never recovered a known ΔΔG"*. |
| **STRATEGY.md** | `:132` — RUNG 1 accuracy control (valA_mini) **PASSED**: *"our binary free-energy pipeline reproduces a known answer"*. `:539–540` — pmx/GROMACS is *"the only physics lane here that **has** recovered a published known answer"* (barnase–barstar Y29A +4.42 ± 1.08 vs +3.4; Y29F −0.37 ± 0.18 vs −0.13). `:538` gives the precise scope: *"valA validates relative FEP **within one pocket**"*. |
| **Map's own §3** | row 3 (`:222`) marks the pmx lane **✓ complete — PASSES**. |
| **VERDICT** | **UNSOURCED / over-broad** — the defensible statement is *"has never recovered a known **selectivity** ΔΔG, i.e. one across two pockets"* |

## 21 · §6's summary count does not follow from §6's own column

| | |
|---|---|
| **Claim** | *"★ **Read the column, not the list.** **Four of the six are moving or done**; the two ○ rows are gated on something else … **There is no row here waiting on a decision.**"* |
| **Map** | `:443–444` |
| **Its own column** | item 1 ○; item 2 *"✓ ran → ○ re-run needed"*, whose own cell says the re-run *"is now the **top unrun item**"*; item 3 ✓ (but see finding 22); item 4 ◐ — **not moving**, finding 1; item 5 ◐ — moving; item 6 ○. |
| **VERDICT** | **UNSOURCED** (a derived count that its source table does not support) |

Actual: **1 moving** (item 5), **1 done with a caveat** (item 3). And *"no row waiting on a decision"* sits
against item 1, which needs a bench — which `STRATEGY.md`'s operating regime and CLAUDE.md §5 both put outside
what this program can buy. Per CLAUDE.md rule 1.1 a total is derived, never typed; this one was typed.

---

# UNVERIFIABLE

## 22 · §6 item 3's ✓ rests half on branch 1b, which the map itself says must not be quoted

| | |
|---|---|
| **Claim** | *"\| 3 \| **Is there a ligandable NR4A3 cysteine?** A yes opens a route **needing no cryptic pocket at all** \| **✓ complete — §5 branch 1 + 1b** \|"* |
| **Map** | `:438` |
| **Why unverifiable** | branch 1b is out of audit scope by instruction. What is checkable without touching its numbers: its artifact `research/modalities/nr4a3-linker-covalent-reach.json` is **confirmed absent from the tree**, and the map's own §5 branch-1b banner says *"**do not quote branch 1b anywhere**, and read every number below as provisional."* A ✓ that cites `1b` as half its evidence therefore quotes what the same file forbids quoting. |
| **Secondary** | *"needing no cryptic pocket at all"* is contradicted by §5b Route B's own closing line, *"⛔ **What remains blocking is upstream, not here:** every anchor comes from the docked pose"* — and the anchors are the pocket. |
| **VERDICT** | **UNVERIFIABLE** — recorded, not guessed. The state should read ◐ or ✓(branch 1 only) once 1b settles. |

## 23 · The rendered artifact

| | |
|---|---|
| **Claim** | *"Rendered version (mermaid + status colouring): published artifact, regenerated from this file's content."* |
| **Map** | `:15` |
| **Why unverifiable** | no URL, no artifact id, no generating script named. I cannot confirm the page exists, that it is current, or that its colouring matches the five classes defined at `:103–108`. Recording the refusal rather than assuming. |
| **VERDICT** | **UNVERIFIABLE** |

---

# The three spines, compared

The task named `STRATEGY.md:1031` ("Validation architecture — the five requirements") and `STRATEGY.md:2577`
("Dependency spine") as describing the same structure as map §1. **They do not describe the same object**, and
most of the differences are category differences rather than contradictions:

| | what it actually is | unit |
|---|---|---|
| **map §1** (`:63–110`) | a **claim** dependency graph — what must be true before the paper can claim a candidate | claims + instruments |
| **STRATEGY.md:1031** | the external reviewer's **conditions on what a result may claim** — (A) accuracy control, (B) target-specific precision, (C) ternary known-answer control, plus conditionality, ABFE-HELD, NR-V04-covalent, prioritize-don't-score | requirements |
| **STRATEGY.md:2577** | a **spend ladder** — TIER-0 → RUNG 0 → 1 → 2 → 2b → 3 → 4 → 5 → 6, with cumulative cost | purchases |

So there is **no evidence of multiple inconsistent spines** in the sense of three rival orderings of the same
thing. But four substantive disagreements survive the category difference, and each is a real gap:

### D1 · Val B — the failed instrument that gates the whole ladder — has **no node on the map's graph**

STRATEGY.md requirement 1(C) (`:1045–1047`) is the ternary known-answer control, and `:1156` calls it *"**the
highest-value dollar in the plan** — the cheapest gate on the entire prospective ladder."* It **FAILED**
(`:136`, RUNG 2, wrong sign, `−0.599` against `+0.944`), and `R` localises the miss to an endpoint-state error
so *"more sampling will NOT fix"* it (`:603–604`). The map's §1 carries `V1`–`V4` and **none of them is Val B**;
the `T` node has **no dashed validation edge at all**. The program's hardest instrument failure — and the gate
STRATEGY.md puts under the entire prospective ladder — is absent from the dependency graph. It appears only in
§3, and until commit `f67d0781` it appeared there mis-labelled as E1 (finding 6).

### D2 · The map's `V4` is ABFE; STRATEGY.md requirement 3 files ABFE as **HELD**, behind two unmet preconditions

`STRATEGY.md:1058–1064`: *"**ABFE is HELD and reframed** … **Not worth running until the accuracy benchmark
passes, the opening penalty is handled, and multiple poses are treated.**"* The spine's own last line
(`:2615`) files `dg_open_paralogue` and `abfe_conditional` under **OPTIONAL/HELD (explicit nod only)**.
Requirement 2 (`:1049–1056`) is the opening penalty, and its warning bears directly on the map's `B` node:
*"Each paralogue can have a **different opening penalty**, so comparing binding only in matched open receptors
can **miss or REVERSE selectivity**."* **That is a documented way the map's `B` node can come out backwards,
and the map's graph has no node, edge or note for it.**

### D3 · Ordering — the map's critical path and STRATEGY.md's ranked list share **zero** items

| map §6 critical path (`:435–441`) | STRATEGY.md §6 ranked by decision value ÷ $ (`:2753–2764`) |
|---|---|
| 1 wet-lab binding · 2 pose re-run · 3 cysteine ✓ · 4 ternary rebuild · 5 CREBBP/BRD4 · 6 ≥3 models/paralogue | 1–3 ✅ done ($0) · 4 `S` at n=2 (~$23) · 5 NR-V04 Arm E (≈$7.7) · 6 ✅ done · 7 replicates on the open cycle (~$25) · 8 generative arm of the generation-matched null · 9 an `S`-shaped calibrator (unpriced) |

Not one item appears on both. STRATEGY's ranks 4 and 5 have since landed (5a-KS `S = −0.1297 ± 0.3264`,
2026-08-02; NR-V04 Arm E 16/16 → DISCORDANT), so that part of the list is simply stale — but **ranks 7, 8 and 9
are open, priced or explicitly unpriced, and appear nowhere on the map.** Conversely the map's items 4 and 6
exist in STRATEGY.md only as §(g) prose at `:486–513` with no rung, no gate and no price — which is precisely
the condition STRATEGY.md's own §6 note calls out at `:2767–2769`. **Neither document currently contains the
union.** That is the reconcilable half of what the map was created to fix.

### D4 · What creates selectivity — the thesis and the map's Route A point opposite ways

`STRATEGY.md:897–903` (Thesis): *"Close-paralogue degrader selectivity is created at the **induced target–E3
interface** and differential lysine geometry … **never at the conserved warhead pocket**, and in every landmark
case it was *discovered then rationalized* by a solved ternary structure — never predicted blind."*
`STRATEGY.md:910–913`: a useful degradation window needs **~2.0 kcal/mol** of true margin, against a best-case
**resolvable** difference of **0.60** and a **measured** accuracy of **1.543, wrong sign**.

The map's §5b makes the **warhead-pocket** route the program's highest-leverage item (`:404`) and carries
**none** of those three numbers. The map's §4 row 4 (`:244`) is right that the *paper* reads selectivity as
resting on the binder margin (`nr4a3-degrader-paper.md:729`, `:2600` — ✓ verified) — but the paper says that as
*"on current evidence, and the ternary route gave us nothing"*, not as a claim that the pocket is where
selectivity lives. Presenting it without STRATEGY's ~2.0-vs-0.60 gate lets the reader conclude the ABFE
benchmark, once passed, would settle Route A. It would not: even a perfectly-calibrated engine at the measured
SD resolves 0.60 kcal/mol against a margin requirement of ~2.0.

The mirror-image omission is on Route B: `STRATEGY.md:952–967` measures P(a paralogue Cys is also reached | an
NR4A3-unique one is) at **0 at 12 atoms, 0.081 at 16, 0.258 at 20** and concludes *"**keep the linker SHORT** …
any design drifting to 16+ atoms **trades away the axis it exists to exploit**."* The map's Route B proposes to
place the electrophile at **11–19 Å**, in that band, and the constraint appears nowhere in the map.

---

# AGREES — verified, no action

Every one of these was checked against the artifact's own record, not against a summary line.

| # | claim (map line) | checked against | result |
|---|---|---|---|
| A1 | 3 unique LBD cysteines C397/C420/C559 (`:293`) | `nr4a3-covalent-handle-ensemble.json` → `nr4a3_unique_lbd_cysteines: [397,420,559]` | ✓ |
| A2 | C496/C536 in-pocket at **2.7–6.4 Å**, conserved (`:298`) | same → C496 `dist_to_pocket_A` 2.66–5.59, C536 5.89–6.42, both `reach_class: in_pocket`, both `unique_vs_both: false` | ✓ |
| A3 | C397/C420/C559 at **11–19 Å** (`:299`) | same → 10.93–14.06 / 16.85–18.93 / 12.22–13.23; union 10.93–18.93 | ✓ |
| A4 | C397 flagged in **20/20** conformers (`:305`) | same → `n_flagged: 20` of 20 | ✓ |
| A5 | C551 ranks **3/18** on **every** accessibility observable (`:304`) | same → `control_rank.observables`: rsa, rsa_heavy, sg_sasa_A2, sg_sasa_heavy_A2, sg_rel — all `rank: 3, of: 18` | ✓ 5/5 |
| A6 | the two above it are NR4A3's C397 and C420 (`:305`) | same → every `top3` list | ✓ 5/5 |
| A7 | *"the thresholds were **not moved**; a test asserts the module holds no local copy"* (`:303`) | `tests/test_nr4a3_covalent_handle_ensemble.py:128–135` — `assert che.EXPOSED_RSA is atlas.EXPOSED_RSA`, `assert che.REACH_BANDS is uniq.REACH_BANDS`, and `"EXPOSED_RSA = 0.25" not in body` | ✓ |
| A8 | SG SASA quantized at **1.34 Å²** by a 96-point sphere until single-atom measures moved to **960**; **ranks unchanged** (`:311–313`) | `nr4a3_covalent_handle_ensemble.py:222–224` states the 1.34 lump verbatim; ranks compared across `4381c2a6` → `70fed0ff` — all still 3/18 | ✓ |
| A9 | *"no experimental NR4A1/NR4A2 ensemble, so the like-for-like comparison is a **missing input, not a negative result**"* (`:314–315`) | `nr4a3-covalent-handle-ensemble.md:108` | ✓ |
| A10 | §3 row 1: **Gln98 Oε1 → Arg12 Nη2, 2.88 Å** vs Leu1545 (`:220`) | `selcal-interface-signature.json` → `known_answer.positions[0]`: `target_atom "OE1"`, `e3_resname "ARG"`, `e3_resseq 12`, `e3_atom "NH2"`, `distance_A 2.88`; GLN98 34 contacts vs LEU1545 10; `recovered: true` | ✓ |
| A11 | §3 row 2: DockQ **0.618** (6HAX) / **0.839** (9DTY), iRMSD **0.67 Å** (`:221`) | `selcal-deepternary-poscontrol.json` best 0.6178; `selcal-deepternary-headtohead.json` best 0.8388, `iRMSD_A 0.6713`, `fnat 0.833` | ✓ |
| A12 | §3 row 3: barnase–barstar Y29A **+4.42 ± 1.08 vs +3.4** (`:222`) | `STRATEGY.md:540` | ✓ |
| A13 | §3 row 4: CREBBP/BRD4 ΔΔG **≈ 2.2 kcal/mol** (`:223`) | `selectivity-benchmark.json` → `experimental_selectivity.ddg_kcal_per_mol: -2.19`, 40× fold, RT·ln(40) | ✓ |
| A14 | §3 row 4: benchmark *"built and staged with **no `result` key**"* (`:402`) | `selectivity-benchmark.json` — `'result' in d` → **False** | ✓ |
| A15 | co-fold DockQ **0.023–0.046** (`:225`) | `selcal-deepternary-headtohead.json` → `incumbent_our_cofolds`: smarca2 min 0.0228 / max 0.0378, smarca4 min 0.0347 / max **0.0459** | ✓ |
| A16 | *"≈ true structure moved **32 Å**"* (`:225`) | `selcal-dockq-decoy-scale.json` — 1.000 / 0.948 (0.5 Å) / 0.845 (1) / 0.717 (2) / 0.401 (4) / 0.240 (8) / 0.085 (16) / **0.026 (32)** | ✓ |
| A17 | E1 p-values **0.393** and **0.747** (`:226`) | `selcal-verdict.json` → `p: 0.746753`; NR-V04 retro `p = 0.392857` (`STRATEGY.md:71`) | ✓ |
| A18 | *"three separate selectivity results had to be withdrawn"* (`:216`, `:231`) | `STRATEGY.md:13` — *"it is how three selectivity results came to be withdrawn"*; the tally at `:522–527` | ✓ |
| A19 | §4 row 6: **GLU208** sequence-encoded (**Pro** in NR4A1, **Tyr** in NR4A2); **5** placement artifacts; **1 model per arm** vs a bar of 3 (`:246`) | `nr4a-ternary-signature.json` → `result.sequence_encoded: ["GLU208"]`; `detail` rows `aa_a "E"` / `aa_b "P"` and `aa_b "Y"`; `same_residue_placement_artifact: [ARG174, ARG219, GLU104, LEU234, LYS195]`; `replicated.n_models: {1,1,1}`, `reproducibility_bar: 3`, `reproducibility_testable: false` | ✓ |
| A20 | §4 row 5: *"predicted for all three paralogues at comparable confidence"* (`:245`) | `nr4a3-degrader-paper.md:719–720` — per-paralogue iptm 0.72 / 0.83 / 0.82 | ✓ |
| A21 | §4 row 7: transfer prior · near-invariant clonal fusion in a quiet genome · no LOF in any EMC model · dTAG delegated (`:247`) | `nr4a3-degrader-paper.md:2508`, word-for-word | ✓ |
| A22 | §4 row 1: *"Gate 3A supported; Gate 3B still open"* (`:241`) | `nr4a3-degrader-paper.md:497`, `:545–546` | ✓ |
| A23 | §5b Route A: **10** Pocket-5 lining residues, **7** paralogue-divergent — L406, T407, T410, R412, I484, I531, L534 (`:393–394`) | `nr4a-selectivity.json` → pocket 5: `n_residues: 10`, `n_divergent: 7`, `selectivity_handles` = exactly those seven, residue-by-residue | ✓ |
| A24 | §5b Route A: *"T407 and R412 mostly splay outward"* (`:395`) | `nr4a3-degrader-paper.md:558–559` — facing in 0.0 and 0.25 of druggable frames | ✓ (but the owning artifact is uncommitted — finding 16) |

**§2 rows checked incidentally** (out of scope, **not counted**) — all four AGREE: Cys551 unique to NR4A1
(`nr4a3-covalent-handle-ensemble.json` → `positive_control.paralogue_partners`: NR4A2 **Y551**, NR4A3 **T579**);
C6→S **28.42–39.11 Å** (exact min and max of the 7 clean-assembly `frozen_site.sg_dist_A` readings in
`nrv04-covalent-input-audit.json`; `summary.best_frozen_site_dist_A: 28.42`); 9DTY **8** copies / 9DTX **1**,
`design.min_attainable_p: 0.5`, `can_reach_alpha: false` (`selcal-xtal-census.json`); *"shipped ligand ≡ native,
0.000 Å over 66 atoms"* (`selcal-deepternary-STATUS.md:38`).

---

## Recommended fixes, cheapest first — all $0

1. **`:439` ◐ → ○**, and give the ternary rebuild a rung, a gate and a price in STRATEGY.md. *(finding 1)*
2. **`:82` `ARCH` ✓ → ○**, or relabel it as an instrument node beside `V2`. *(finding 2)*
3. **`:241` 4 of 20 → 3 of 20**, cite `nr4a3-pocket-reharmonize-summary.json`, and widen `pinned-figures.json`
   `superseded[19].pattern` to `4[ /](of )?20` so the guard catches the spelled-out form. *(finding 3)*
4. **`:411`** drop "~80 %-identical" or replace with the measured pocket figure (7 of 10 divergent). *(4)*
5. **`:299`** state C397 20/20, C420 16/20, **C559 0/20**. *(5)*
6. **`:310` 76 % → 92 %** (median), re-read from the current artifact. *(12)*
7. **`STRATEGY.md:351`** → `2026-08-01 10:43 PM ET`; **`:552`** re-stamp the board and add the SageMaker lane;
   **`:531`/`:546`** retire "never been run / neither is authorized" for the CREBBP arm into Appendix A;
   **`:421`** median 0.438 → 0.4143. *(13, 14, 7, 15)*
8. **`:394`** cite the real owner and carry the paper's two caveats (S3-only; pre-harmonized, not confirmed);
   **`:395`** add *"— and only **4** of the five distinguish NR4A2; I531 is Ile in both"*. *(16, 17)*
9. **Port `nr4a-resistance-map.json` from `origin/modalities-cache` to `main`** and cite it instead of the
   module. *(18)*
10. **Write a dispatch record** for the ABFE lane (SageMaker job name + time) and an `inflight-board.d/`
    fragment so it is visible on the all-lane board. *(19)*
11. **`:116`** add "selectivity"; **`:229`** rewrite the pattern claim to admit INCONCLUSIVE and NON-RESOLUTION;
    **`:443`** recount; **`:77`/`:97`** mark `TG` delegated; **`:293`** add "LBD"; **`:301`** split the two
    C551 measurements. *(20, 8, 21, 9, 10, 11)*
12. **Add a Val B node and an opening-penalty node to §1**, and reconcile the two ordering lists so one of them
    holds the union. *(D1, D2, D3)*
