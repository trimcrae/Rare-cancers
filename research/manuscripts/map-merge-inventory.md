# STRATEGY.md → program-map merge inventory

**A read-only, exhaustive account of what [STRATEGY.md](../../STRATEGY.md) (3,230 lines) contains, section by
section, classified by whether it belongs in the merged source-of-truth spine, in an appendix, or nowhere —
plus every inbound reference that a merge would break.**

⛔ **THIS FILE OWNS NOTHING.** Every number, gate and status below is a *reading* of STRATEGY.md, the
[schedule JSON](degrader-paper-schedule.json), [`pinned-figures.json`](pinned-figures.json) or a committed
artifact, cited at the point of use. If this file and its source disagree, the source is right and this file
is the bug (CLAUDE.md rule 1). It is an inventory produced for one merge; it is not a second plan.

Produced 2026-08-02. $0 — no GPU, no CI, no rental. Nothing in STRATEGY.md or
[nr4a3-program-map.md](nr4a3-program-map.md) was edited.

---

## 0 · The structural fact the merge rests on

The map's §1 is a **claim dependency graph** — *what must be true before the paper can claim X, and which
instrument produces it.* STRATEGY.md's **Dependency spine** (line 2577) is a **priced spend ladder** —
RUNG0→RUNG6, cumulative dollars, a GO/NO-GO gate at each rung. They answer different questions and **both must
survive the merge as distinct layers.** Collapsing them loses either the money or the epistemics.

A third layer is present in STRATEGY.md and in neither the map nor the spine: **THE ORDERED PLAN** (line 1601,
899 lines) is the *item* layer — 30 checkbox items, each with a gate, a price and a status. It is the layer a
machine already parses (§3 below), and it is the layer the merged document's "what next" must be built from.

So the merge target is **three layers, not two**:

| layer | question it answers | current home | machine consumer |
|---|---|---|---|
| **claim graph** | what must be TRUE, and which instrument shows it | map §1/§3/§4 | none |
| **item plan** | what to DO next, its gate, its price, its status | STRATEGY.md ORDERED PLAN (1601) | `work_ledger.scan_plan_items` |
| **spend ladder** | what has been AUTHORISED and what it cost cumulatively | STRATEGY.md Dependency spine (2577) + Spend summary (2500) | `lint_consistency.check_subsets` + `check_derivations` |

---

## 1 · Section inventory

Line counts are exact and sum to 3,230. `hist` is the measured count of lines carrying a supersession /
retraction / correction marker (`supersed|retract|withdraw|retire|corrected|do not cite|refuted`, case
insensitive) — a *proxy* for historical prose, not a line-accurate appendix estimate, because a marker line
usually sits inside a 3–6 line hard-wrapped sentence.

### 1a · Summary table

| # | section | lines | n | hist | class |
|---|---|---|---|---|---|
| 0 | Title + gold-standard banner | 1–46 | 46 | 5 | **SPINE** |
| 1 | 📊 WHERE WE ARE — the scoreboard | 47–155 | 109 | 12 | **SPINE** |
| 1a | ✅ PASSED — covalent design route clears the gate | 156–187 | 32 | 7 | **SPINE** (+ appendix extract) |
| 1b | Library and matched pair | 188–225 | 38 | 6 | **SPINE** (+ appendix extract) |
| 1c | 🌙 OVERNIGHT MONITORING | 226–270 | 45 | 2 | **STALE** |
| 2 | ✅ LANE 13 — categorical case vs paralogue dynamics | 271–306 | 36 | 0 | **SPINE** |
| 3 | ✅ RUNG 5a-KS LANDED — preregistered null | 307–350 | 44 | 1 | **SPINE** |
| 4 | ❌ GATE FAILED — SMARCA2/4 sensitivity control NULL | 351–551 | 201 | 4 | **SPINE** |
| 5 | ⏱️ IN FLIGHT | 552–834 | 283 | 12 | **STALE** (+ 4 one-home extracts) |
| 6 | ✅ First forward/reverse hysteresis — GATE PASSED | 835–886 | 52 | 0 | **SPINE** |
| 7 | Program and thesis (incl. MECHANISM-FIRST) | 887–1004 | 118 | 4 | **SPINE** |
| 8 | Honest scope and language discipline | 1005–1030 | 26 | 0 | **SPINE** |
| 9 | **Validation architecture (the five requirements)** | 1031–1159 | 129 | 4 | **SPINE** |
| 10 | The prospective stage (incl. kill-switch + Tier-2 result) | 1160–1468 | 309 | 23 | **SPINE** (+ appendix extract) |
| 11 | Spending rules | 1469–1481 | 13 | 0 | **SPINE** |
| 12 | GPU economics | 1482–1600 | 119 | 8 | **DUPLICATE** → pricing.md |
| 13 | **THE ORDERED PLAN** | 1601–2499 | 899 | 53 | **SPINE** (+ large appendix extract) |
| 14 | Spend summary | 2500–2576 | 77 | 7 | **SPINE** |
| 15 | Dependency spine | 2577–2617 | 41 | 2 | **SPINE** |
| 16 | ★★ What the landed results change | 2618–2781 | 164 | 11 | **SPINE** |
| 17 | Current front | 2782–2816 | 35 | 2 | **DUPLICATE** |
| 18 | Open decisions | 2817–3131 | 315 | 34 | **split: 2 SPINE / 13 APPENDIX** |
| 19 | Appendix A — superseded numbers | 3132–3210 | 79 | 41 | **APPENDIX** |
| 20 | Appendix B — superseded strategy framings | 3211–3230 | 20 | 5 | **APPENDIX** |
| | **TOTAL** | | **3,230** | **242** | |

### 1b · Per-section detail

---

#### 0 · Title + gold-standard banner — lines 1–46 (46)

**What it owns.** The *primacy ruling* ("if any other doc conflicts with this file, this file wins"); the
**map/STRATEGY division of labour** ("costs, gates and the rung ladder live HERE; the dependency order and
instrument-validation status live THERE") — this is the single most load-bearing paragraph for the merge,
because it is the thing the merge dissolves; the **three editing rules** (one fact one place / corrections to
Appendix A / register the old value in `pinned-figures.json`); the **schedule-JSON mirror contract** ("its
milestone `id`s match the stage tags below one-for-one"); the companion-doc list.

**Classification: SPINE**, but it is the one section that *must* be rewritten rather than moved — its central
claim ("they must not restate each other") ceases to be true the moment they are one document. The mirror
contract and the three editing rules must survive verbatim.

**Inbound links.** `README.md` lines 9/14/18/26 restate the division of labour almost word for word;
`CLAUDE.md` lines 3–8 do the same. Both break on the merge and must be updated in the same commit.

---

#### 1 · 📊 WHERE WE ARE — the scoreboard — lines 47–155 (109)

**What it owns.**
- The **headline-form rule** (every status must be a gate PASSED, a gate FAILED + remediation, or a
  DELIVERABLE done) — trimcrae, 2026-07-26. One home.
- The **as-of tally**: 7 gates passed · 4 failed · 1 delivered-but-not-graded · 4 deliverables + 1 partial ·
  nothing billing · realised **$84.49** machine-ledgered.
- ⛔ **THE ONE HOME FOR "WHICH CONTROLS FAILED"** (lines 60–89) — the four-row table separating valB_mini
  (wrong sign, ❌ CONTROL FAILED) · selcal SMARCA2/4 (NULL, ❌ CONTROL FAILED) · NR-V04 retrospective
  (DISCORDANT, ⚠ NON-RESOLUTION) · RUNG 5a-KS (preregistered null, ✅ NOT A FAILURE), plus the explicit
  warning that **#1 and #2 are DIFFERENT INSTRUMENTS** (alchemical ternary FEP vs endpoint-MD E1).
  **This table is the highest-value thing in the file and the map contradicts it — see §5C-1.**
- The **realised-spend derivation and its attested block**: ledgered floor $84.49, best estimate $133.38,
  +$48.89 attested, the two 2026-07-31 leak ranges ($20–39 `vast_bench_sweep_orphans`; $6.68–25.83
  `nrv04_retro_orphan`), and the ruling that GCP trial credit is a separate ledger.
- The **gate table** (Tier 0/1/2, RUNG 1, 2, 2b, 2·closure, 2 calibration, 2·replicates, 3, 4, 4·fan-out) —
  the one home for each gate's *verdict sentence*.
- The **deliverables table**: linker library 54 constructs (36 exemplar + 18 representative, RDKit 54/54);
  matched pair; ranked congeneric ΔΔG map (18 edges, $73.79); the generation-matched null as PARTIAL with its
  rule-of-three bound (≤0.0157 vs 0.0052, Fisher p = 0.5).

**Classification: SPINE.** This is the merged document's status layer.

**Inbound links.** `realised_spend.py` (11 refs) states outright that "STRATEGY.md's scoreboard quotes this
snapshot" and its `--check` mode instructs updating the figure STRATEGY.md quotes *in the same commit*
(lines 342, 410, 427, 445). `realised-spend.json` mirrors it. 11 files co-mention a "scoreboard"/STRATEGY.
The 2026-08-02 headline block at line 351 is anchor-linked from `nr4a-repanel-prereg-DRAFT.md:9`.

---

#### 1a · ✅ PASSED — the covalent design route clears the gate — lines 156–187 (32)

**What it owns.** The **authoritative corrected+matched Tier-2 numbers**: term (a) **3** (not 7, not 0),
term (b) **40**, nominal **28**; the three gate-clearing basins `vhl|M2` @10 atoms / `vhl|M3` @11 /
`crbn|M17` @12; shortest reach per residue **C397 10 · C420 16 · C559 27**; the collision profile
**0 @12 atoms, 0.081 @16, 0.258 @20**; the **honest cut-off of 14 backbone atoms** and the explicit refusal to
make it a gate. This block is named by the Tier-2 result section (line 1438) as the one home for those values.
⚠ *Superseded 2026-07-26 for the collision profile and the cut-off: the pilot pair above was 5,657 static
placements; the landed matched ensembles (73,867 placements, three scopes) read **0.000–0.003 @12, 0.054–0.133
@16, 0.263–0.383 @20**, whose one home is `nr4a-paralogue-dynamics.json` →
`categorical_verdict.by_scope[*].by_linker_atoms`, and under them 14 is not a measured zero. The inventory's
classification below is unaffected.*

**Classification: SPINE** for the numbers; **APPENDIX extract** for the "I read a superseded artifact and
reported its numbers" narrative (lines 158–173, ~16 lines) — the correction belongs in Appendix A per editing
rule 2, and the block itself says the pre-correction table sat live for four days and the manuscript copied it.

**Inbound links.** `research/manuscripts/nr4a3-reach-rule-correction-2026-07-25.md` (6 refs),
`nr4a3-orientation-basin-search-2026-07-25.md` (10 refs), `basin_geom.py`, `nr4a3_basin_search.py` (10 refs).

---

#### 1b · Library and matched pair — lines 188–225 (38)

**What it owns.** The library survives the reach correction with zero casualties; the wedge-site defect
(`wedge_target_residue: T407` vs `branch_target: C397`, disagreeing on **8 of 10** records) and its fix
(`select_wedge_site()`); the final library **36 exemplar + 18 representative, 54/54 RDKit-verified**; the
matched pair `crbn|M0` exemplar, 3-(3-pyridyl)-L-Ala vs L-Phe at Thr407, **19 backbone atoms, 9.04 Å**
clearance, 64 heavy atoms; and — named at line 2315 as its one home — the **measured** two-mechanism blocker:
`build_smiles` takes **one** `pendant`, so the limit is **architectural, not a grid limit**.

**Classification: SPINE**; **APPENDIX extract** for the superseded "a single chain carrying both needs 16 …
branch floor k=6 against T407's k∈[2,3]" narrative (lines 209–215) — already registered as Appendix A 55.

**Inbound links.** `linker_branch_reach.py` (2), `nr4a3_linker_design.py` (6), `linker_design.py` (4),
`nr4a3-linker-design.json`, `nr4a3-inverse-linker-design-2026-07-25.md` (9).

---

#### 1c · 🌙 OVERNIGHT MONITORING — lines 226–270 (45)

**What it owns.** The three-layer watchdog coverage table; the LANE-13 phantom-smoke-leg root cause
(`leg_names()` synthesises a `-smoke` name; `real_done` excluded smoke legs and the stall test did not); the
`paralogue_md` progress-scalar trap (`phase_rank × 1e6 + milli-ns`, because `done_ns` resets at the
metad→release boundary); the proven-live `DIED → relaunch` (2026-07-26 1:42 AM ET, instance 45878836, resumed
at 33.55 ns); and the note that `FAILED` and `STALL` escalation remain unproven live.

**Classification: STALE.** Every lane it describes has closed. Its own table says it covers "the 4 valB_mini
replicate legs, which are what is enabled now" — those landed 2026-07-30 — and "NOT the 2 RUNG 5a-KS legs any
more … PARKED", which landed 2026-08-02. The `vast_idle_guard` row was already corrected in place
(CLAUDE.md §6 is the live home for that rule). **Current value:** nothing is being watched; nothing is
billing. The three durable facts (phantom-leg root cause, progress-scalar trap, DIED→relaunch proven) should
move to `research/compute/` or the watchdog module docstrings, which is where a monitoring fact belongs.

**Inbound links.** None found outside STRATEGY.md — the watchdog behaviour is documented in
`ternary-watch.json`, `ternary-vast-watch.json` and the workflow files, which do not point back here.

---

#### 2 · ✅ LANE 13 — does the categorical case survive paralogue dynamics? — lines 271–306 (36)

**What it owns.** P(no paralogue cysteine reachable | the construct reaches an NR4A3-unique cysteine) at the
12-atom gate, across three scopes; **exactly 1.000 on exposed cysteines in every scope**; the rare-event
framing (**122 hit placements of 73,867**, ~0.04 %) and the ruling that the defensible claim is the EXPOSED
column, *not* a probability estimated near one; the `_limits` (no thiol pKa/nucleophilicity/adduct stability;
correlated conformers; superposition residual).

**Classification: SPINE.** It is the evidence under Tier 0's "PASSED — and now TESTED against paralogue
DYNAMICS", and it is the *only* place the exposure-not-absence narrowing is quantified across ensembles.

**Inbound links.** `research/manuscripts/nr4a3-paralogue-dynamics-categorical-test-2026-07-25.md` (6 refs) —
and that file is itself a `pinned-figures.json` **target**, so its figures are CI-checked against this section.
`nr4a3_handle_ensemble.py`.

---

#### 3 · ✅ RUNG 5a-KS LANDED — lines 307–350 (44)

**What it owns.** **S = −0.1297 ± 0.3264 kcal/mol** (replicate SD, n = 2/arm); per-arm means and SDs; the
fixed-in-advance reading (S ≈ 0 ⇒ the marginal wedge is absent, registered as LIKELY and **not** a stop); the
bound (**|S| ≳ 0.65 kcal/mol at 2σ** was the only resolvable range); the ruling that **the error is the
replicate SD, not the MBAR SE**; the staging verification that rules out the one-chain counterfeit
(chains A 254 + B 442 + ligand L, matching `protocol_hash` / `charge_method` / `setup_cache_version` /
`n_windows` across all four legs); and three limits (n_particles 210k vs 148k across arms; Boltz-2 geometry ⇒
pose-conditional; **the instrument has a failed calibrator**).

**Classification: SPINE.** This is the program's flagship causal result and it landed today.

**Inbound links.** `nr4a3-5aks-reduction.json` is its one home for the numbers; `nr4a3-5aks-lane-report.md`;
`ternary_vast_launch.py` `MODES['5aks']`; `vast_cost_model.py` line 714 prices four legs citing
"STRATEGY Open decision 11".

⛔ **The map has no node, no instrument row and no critical-path entry for `S`.** See §5B-1 and §5C-8.

---

#### 4 · ❌ GATE FAILED — the SMARCA2/4 sensitivity control returns NULL — lines 351–551 (201)

**What it owns.** The largest single block in the file after the plan, and it owns a great deal:
- The verdict: tier **NULL**, statistic **+0.4373 Å**, direction **opposite** to the source's prediction with
  all 11 LOMO refits keeping the sign, exact one-sided **p = 0.7468**, mirrored **p = 0.2554**, reference set
  **462** with floor **0.00216**, **0** technical failures, **22** legs / 6 vs 5 models.
- The **adequacy argument** — this is not an underpowered miss — and the ruling that it is a *worse* outcome
  than RUNG 4's DISCORDANT.
- The measured-input-fault exclusion (SMARCA4 seed 3, **0.693 Å** against a 1.00 Å floor, refused on five
  machines) and the contrast case that was re-run rather than excluded (1.2994 Å).
- **### What this BINDS (385)** — machine-carried by `selcal_gate.NEXT_STEP_BY_TIER`: **step 3 is not bought**
  and `nr4a-repanel-prereg-DRAFT.md` is **retired unrun**; every NR4A3 selectivity statement is an
  **UNVALIDATED PREDICTION** carried in three verified places; the null does **not** distinguish "blunt
  readout" from "hard pair"; and the third, measured reading — the co-folds reproduce the internal
  VHL/EloB/EloC machinery at DockQ 0.89–0.97 but the target↔VHL interface at **DockQ 0.023–0.046, fnat 0.000**.
- Sub-findings **(a)–(g)**, each of which the map's §2/§3 partially inherits: DeepTernary positive control
  (0.618 in-set, **0.839** post-horizon on 9DTY, iRMSD 0.67 Å); the decoy-scale ladder (1.000 → 0.026 at 32 Å);
  the decomposition (halves right within 3.2 Å, assembly wrong by a factor of 10); the **validated
  interface-signature descriptor** (Gln98 Oε1 → Arg12 Nη2, **2.88 Å**, side-chain only, vs Leu1545); its
  application to the NR4A ternaries (**six** positions, **five placement artifacts**, one sequence-encoded
  **GLU208**, reproducibility NOT TESTED at 1 model against a bar of 3); and **(g)**'s three-part gap analysis
  ending in *"the next step is therefore in-silico and specified"* — the assembly-route rebuild.
- **### The standing tally this closes (520)** — all three positive-control attempts have run and none
  succeeded; and the retraction of *"there is no fourth candidate staged"*, naming **two** built-and-unrun
  known-answer tests: **CREBBP vs BRD4(1)/SGC-CBP30** (`selectivity-benchmark.json`, verified today to still
  have **no `result` key**) and a **pmx/GROMACS interface point-mutation ΔΔG**.

**Classification: SPINE.** Almost none of this is superseded; it is 2026-08-02 material.

**Inbound links.** `selcal-verdict.json`, `selcal_gate.py`, `selcal_panel.py`,
`selectivity-sensitivity-control-prereg.md` (+ AMENDMENT 1), `selectivity-resolution-options.md/.json`,
`selectivity_resolution_options.py`, `nr4a-repanel-prereg-DRAFT.md` (which **anchor-links this heading** —
`STRATEGY.md#-gate-failed--the-smarca24-sensitivity-control-...`, the only non-Appendix-A anchor link in the
repo, so **this heading's slug is load-bearing and must not change**), `selcal_xtal_stage.py`,
`selcal_cofold_validate.py`, `.github/workflows/selcal-cofold-validate.yml`.

---

#### 5 · ⏱️ IN FLIGHT — lines 552–834 (283)

**What it owns.** As a *board*, nothing current: its own as-of is **2026-07-30 5:30 PM ET** and its own text
says "NOTHING IS BILLING. Every lane on this board is off a host." Six of its seven rows are struck through or
closed, and the 5a-KS row has since landed. But the block underneath the table carries **four one-homes that
are not stale**:

1. **The buy-line arithmetic** (lines 559–564): basis **$0.003412/ns** DERIVED via
   `congeneric_fanout.basis_usd_per_ns()`; buy line **$0.006539/ns** ≈ **1.92× basis**; and the explicit
   statement that this is not a loosening of 1.5×. *(Duplicated in CLAUDE.md §1, which is arguably the live
   home — see class note below.)*
2. **★ WHAT `R` DECIDES, stated the right way round** (lines 599–610) — explicitly *"this is the one home for
   the mapping"*: `R ≈ 0` ⇒ **endpoint-state error, more sampling will NOT fix the miss**; `R` materially
   non-zero ⇒ a path error and the miss IS fixable. Plus `R = 0.2128`, `R_ternary = −0.0312`,
   `R_binary = −0.2440`, decision `R_CONSISTENT_WITH_ZERO`, and the three limits (n = 1 with no error bar;
   the σ_leg divergence that is Open decision 7/8; closure measures internal consistency, not accuracy).
3. **The binary-arm departure finding and its 4 fs replication** (lines 671–780) — 8 of 12 replicas depart at
   16.3 Å in the 2 fs binary arm vs 12/12 stable ternary; reproduced at 4 fs (7 of 12); the λ attribution
   (**7 of 8** departures initiate in the interior at upper λ, but persist at both physical endpoints); the
   two audit §L.3f rulings (**no standard-state correction**; **only the BINARY arm is re-run restrained**);
   and the DECIDED-2026-07-26 ruling that the triangle's binary legs run **UNRESTRAINED**.
4. **⛔ The pose-diagnostic status** (lines 722–740) — *"this is the single home for that fact"*: across 137
   `gpu-ternary-fep-vast.yml` runs and the newest 1000, `converge` is `skipped` in every one; it has executed
   **once ever**; and a dispatch would have read the **wrong legs** (`--mode edge` hardcoded, disjoint
   `unit_id` sets). Fixed via `CONVERGE_TASK_MODES` / `task=triangle-converge`.

Also here: the RUNG 2b reduction table and its two non-optional qualifications; the commit-block quantisation
rule (*never quote a FEP rate off a window spanning only a few blocks*); the 4080S host-starvation diagnosis.

**Classification: STALE as a board (the table, ~30 lines, and the "committed if both billing lanes complete"
paragraph); SPINE for the four extracts above.** In the merged document the board becomes a pointer to the
live in-flight renderer (`inflight_usd_per_ns.py` / `inflight-board-all.md`), and extracts 2–4 move into the
plan layer beside the items they gate (valB_mini, the restrained binary re-run, the closure triangle).

⚠ Extract 1 (the buy line) is a **DUPLICATE** of CLAUDE.md §1's ★★ ruling, which is the standing-rules home
and carries the same absolute rate. The merged document should point at
[`inflight_usd_per_ns.APPROVED_USD_PER_NS`](../modalities/inflight_usd_per_ns.py) rather than restate it.

**Inbound links.** `valb-triangle-reduction.json`, `valb_failure_propagation.py`, `valb_triangle_closure.py`,
`valb_triangle_reduce.py`, `ternary-lane-guard-audit-2026-07-25.md`, `ternary-4fs-vast-findings.md` (9 refs),
`congeneric_fanout.py` (3), `inflight-board-all.md`, `inflight-board.d/gcp-s1f-rep.json`.

---

#### 6 · ✅ The first forward/reverse hysteresis — GATE PASSED — lines 835–886 (52)

**What it owns.** `|ΔG_fwd + ΔG_rev| = 0.324605` against a preregistered ceiling of 1.0 → **PASS**; the
per-leg table (+47.470131 / −47.794736, MBAR SEs 0.110758 / 0.086487); the explicit label that these are MBAR
SEs and **not** this repo's standard (`cycle_sd_kcal: null` at n = 1); the **four discriminators** proving the
reverse leg was genuine (141,968-particle `v2pe` system, different ΔG, different SE, different per-replica pose
stats); what it does and does not change (RUNG 2 still FAILED; ΔΔG_coop still unreportable from r0;
convergence now `MEASURED_FAILURE`); and the reverse leg as **the control that makes the binary arm's failure
specific** (11/12 clean reverse vs the binary arm's 8/12 departing).

Line 135 of the scoreboard explicitly defers to this block — *"The numbers live once, in the §THE FIRST
FORWARD/REVERSE HYSTERESIS block below — this row deliberately does not restate them."*

**Classification: SPINE.**

**Inbound links.** `ternary-lane-guard-audit-2026-07-25.md` §L.7/§L.7a; the reduce run's `[REDUCE-VERDICT]`
annotation is named as the number's one home.

---

#### 7 · Program and thesis — lines 887–1004 (118)

**What it owns.** The North Star statement and the ≈70–80 % effort share; the **thesis** (selectivity emerges
jointly from binary preference + ternary cooperativity + ubiquitination-compatible geometry, is created at the
induced target–E3 interface, was in every landmark case discovered-then-rationalised by a solved ternary, and
AKT1/2/3 is the cautionary null).

**### MECHANISM-FIRST (905)** owns the MARGINAL/CATEGORICAL taxonomy and — named repeatedly elsewhere as
*"the one home"* — the **current pair**: required margin **~2.0 kcal/mol** (median over 27 potency scenarios,
range 1.75–2.25), best-case **resolvable difference 0.60 kcal/mol** DERIVED from
`minimum_detectable_difference(0.375, 3)`, against a **measured accuracy of 1.543 kcal/mol, wrong sign**; and
the ruling that **the binding constraint has moved from precision to accuracy** — the axis is *uncalibrated,
not blunt*, so the remedy is a calibrator, not more sampling. It also owns the categorical-axis narrowing
(only 4 of 20 NR4A3 cysteines unique; C496 reaches the ≤12-atom gate in **29/75 = 0.387** but is buried at
RSA 0.023; NR4A1 C465 opens at **6** atoms vs C397's 10; the matched-construct collision profile) and the
resulting design rule: **keep the linker SHORT**. Plus the EWSR1 fusion-lysine check (1–2 lysines ⇒ thin, not
a design axis).

**Classification: SPINE.**

**Inbound links.** 12 external files co-name MECHANISM-FIRST and STRATEGY, including
`selectivity_margin_model.py` + `tests/test_selectivity_margin_model.py` (which asserts the derived figure),
`nr4a3_basin_search.py`, `linker_branch_reach.py`, `degrader-paper-schedule.json`, `pinned-figures.json`,
`.github/workflows/fusion-cpu-extras.yml`, and four manuscript notes.
`nr4a_paralogue_unique_residues.py` → `nr4a-paralogue-unique-residues.json` owns the residue facts.

---

#### 8 · Honest scope and language discipline — lines 1005–1030 (26)

**What it owns.** The double-conditionality statement (hypothesized cmpd19 pose × chosen receptor frame); the
five earned-phrase substitutions; the **never-imply** set (proteome-wide selectivity, EMC efficacy, safety,
therapeutic window, clinical readiness) and the MYC-induction liability; the **novelty right-sizing** with its
four prior-art citations.

**Classification: SPINE — and it is the single most citation-dense section in the repo.**

**Inbound links.** ⚠ **`lint_claims.py` cites this section by name in 21 places** — its module docstring
(line 6), its rules index (lines 22–27) and every one of the 13 rule `source` strings (R1a–R5). The rules are
hardcoded in Python and CI-enforced against the paper + SI on every push, but each carries a provenance string
naming this section's wording. 16 further files co-name "Honest scope" and STRATEGY, including
`nr4a3_basin_search.py:49` and `e3_recruiter_staging.py:42`, which reproduce the conditionality clause in
their own honest-scope docstrings. **Renaming or dissolving this section invalidates 21 provenance strings in
a CI-enforced linter.** It must survive as a named section with a stable title.

---

#### 9 · Validation architecture (the five requirements) — lines 1031–1159 (129)

**What it owns.** The **external reviewer's five conditional-approval requirements verbatim**, which "govern
what any result is allowed to claim". Fully itemised in §5B below. Plus **### Why Val A is nearly free but
Val B is load-bearing (1101)**, which owns:
- The Val-A-is-a-citation ruling, scoped **to the binary lane only**.
- The **charge-model lane split table** (binary RBFE **am1bcc** · ternary FEP **NAGL** · endpoint/covalent MD
  **NAGL**) with its forensic provenance (`charge-provenance-forensic.json`, read from the stored hybrid
  `System` of every banked valB leg, *not* from the config line — Appendix A 47).
- The three consequences: **ΔΔG_coop is SAFE** (measured, cancels within a lane); **any CROSS-LANE
  subtraction is NOT safe** (hence `assert_charge_consistency`'s hard refusal); and **Val A's citation does
  not cover the NAGL lanes** — *"do not let a reader infer the OpenFE citation covers the ternary numbers."*
- The reason the AM1-BCC/NAGL split is physically forced (`sqm` >85 min on a 166-atom recruiter without
  converging).
- **"Val B-mini is the highest-value dollar in the plan."**

**Classification: SPINE. This is the section the merged document most needs and the map most lacks.**

**Inbound links.** Only one external file names "Validation architecture", but the *content* is referenced
everywhere: `nr4a3-degrader-reviewer-revisions-2026-07-15.md` is the verbatim source; `md_settings.py`'s
docstring registers the two lane deviations; `nr4a3_protein_fep.py`'s `assert_charge_consistency` implements
consequence 2; `nr4a3_rbfe.strip_foreign_partial_charges` implements the third failure mode;
`e3_recruiter_staging.py:111` cites "validation requirement 5" for its no-tunable-scalar rule;
`nr4a3_basin_search.py:37` cites "load-bearing piece 4" and line 835 "exactly as STRATEGY.md specifies".

---

#### 10 · The prospective stage — lines 1160–1468 (309)

**What it owns.**
- The mechanism-first search order diagram and the four **$0 CPU** additions **(a)–(d)** — electrophile reach
  (prefer **reversible**-covalent); transfer-zone lysine identity (set membership, not energy, with the honest
  limit that it raises odds and does not guarantee); **E3 breadth** with the mandatory ≤2 downselect (CRBN
  9CUO + VHL 9GIO advance, VHL as a labelled *backfill*, CRBN−VHL margin **0.033** reported as a tie), the
  structural-stageability finding (RNF114 no structure; DCAF16 34 % buried; DCAF15 no partner-free liganded
  structure) reported as **a publishable negative for the E3-breadth argument**, the 9GIO two-ligand
  resolution (`3JF` at **12.35 Å** from Cys77 vs `A1IMD` at **1.84 Å**), BIRC2 as the flagged revisit, and the
  ruling that the downselect is **blind to recruiter-intrinsic pharmacology**; and pose-marginalisation.
- The **five load-bearing pieces** (differential atlas · orientation search · matched-pair causal cycle with
  PRIMARY ligand-side `S` and CONFIRMATORY protein-mutation cycle · accessibility separated from stability ·
  robust constraint-satisfaction selection).
- **### The hard kill-switch (1282)** — the STOP condition, and the ★★ **Tier-3 semantics box**: `S` is
  non-covalent and therefore **structurally incapable of testing the categorical mechanism**; `S ≈ 0` ⇒ the
  marginal wedge is absent and the claim rests on the categorical axis alone; **STOP only if the categorical
  axis has ALSO failed.** Plus the 2026-07-30 amendment turning a null from "failure to find" into a **bound**.
  The four-tier table (0/1/2/3) with each tier's cost and status.
- **### Tier-2 result in full (1328)** — 141 lines. The meta-basin table; the three readings (all 3 term-(a)
  basins reach C397 and only C397; **the strongest basin and the gate-clearing basins are not the same
  basins**; reach fractions 0.021–0.057 = the quantitative form of "weakly"); the per-arm table; the
  `best_linker_atoms` reconciliation; the retracted "the discrimination lives on VHL"; the rare-joint-event
  correction; the linker-tractability table; the exit-vector registry-A resolution (8R5H ground truth
  **30.76 Å**, registry A **30.85 Å**, registry B **69.91 Å**) and its falsified "second 48.6 Å instance".

**Classification: SPINE**, with a substantial **APPENDIX extract**: 23 marker lines concentrate in the Tier-2
block (the 6-pose preview values, the pre-correction 7/40/28 table, the "strongest basin is among the MOST
tractable" withdrawal, the 25→11/14→11/15→10 row values, the VHL-discrimination retraction) — all already
registered as Appendix A 49.

**Inbound links.** `e3_recruiter_staging.py` (9 refs, including `# THE PANEL — STRATEGY.md RUNG 5a's widened
ligandable recruiter set, **verbatim**` at line 82 and the ≤2 cap at 1298), `tests/test_e3_recruiter_staging.py`
(3), `e3-recruiter-staging.json` (3), `e3-recruiter-downselect-2026-07-25.md` (4), `e3-recruiter-staging.md`,
`nr4a3_basin_search.py` (10 refs, incl. Tier-2 asymmetry, term-(b) ordering, piece 4, and the Tier-2 GO rule
at line 1372), `tests/test_basin_search.py`, `basin_geom.py`, `nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md` (6).

---

#### 11 · Spending rules — lines 1469–1481 (13)

**What it owns.** The four rules: **no pre-authorization / no pre-staging**; **spend-gated ladder,
cheapest-decisive-first**; **GO/NO-GO after every priced rung**; and **rule 4 — a step whose engine has no
completed benchmark leg is carried as PROJECTED and excluded from the pinned total, never at a fake number.**

**Classification: SPINE.** 13 lines, zero history, and rule 4 is cited by name at line 2177 to justify pricing
the generative-arm control as PROJECTED.

**Inbound links.** No file names "Spending rules" directly, but rule 1 is the standing basis for CLAUDE.md §2's
spend threshold and §3's review-block triggers, and rule 4 is what `vast_cost_model.py` implements by omitting
the confirmatory wedge and the Optional/HELD rungs from `total_plan_usd`.

---

#### 12 · GPU economics — lines 1482–1600 (119)

**What it owns (nominally).** The Vast-only ruling and *"the card is not the decision — the OFFER is"*;
measured throughput **4090 804.06 / 4080 693.35 / 3090 460.91 ns/day** (4090/3090 = **1.745×**); the planning
rate **$0.137/ref-GPU-h**; the bid rule (floor + staleness tick, capped at on-demand); the storage line
(~$0.011/hr); **### Per-edge bases (1516)** — RBFE binary **~13.7 ref GPU-h ≈ ~$1.9**, ternary cooperativity
**~$8.8 ($3.2–22)**, endpoint-MD **~$0.19**, each with its provenance and the caveat that **none is a
completed end-to-end edge on a 4090**; the two transferability warnings; the provider reality check; and
**### Cost levers (1541)** — 4 fs = **1.56×** not 2× and the leg is **2800 iterations** not 2400; the exact
binary/solvent cancellation; sequential stopping **REFUTED at 0.8–2.6 %**; free gates lead; ligand-side double
difference replaces the protein-mutation campaign; E3 breadth free at search.

**Classification: DUPLICATE.** The file's own header (line 1482) says *"full provenance in pricing.md"*, and
`pricing.md:3` says *"This file is authoritative for 'what does step X cost, and how do we know.'"* The
throughput table's home is `vast_cost_model.MEASURED_NS_PER_DAY_84K`; the bid rule's home is
`bid-strategy.md §7`; the per-edge bases' home is `pricing.md`. **Which copy wins: pricing.md / the cost
model.** In the merged document this section should shrink to a pointer plus the **six cost levers**, which
genuinely live here — they are *ratios*, independent of $/hr, and the Spend summary (line 2547) says so.

**Inbound links.** `bid-strategy.md:177` and `:218` both call out this section by name; `pricing.md:3`, `:334`,
`:494` reconcile against it; `vast_cost_model.py:664`; `congeneric_fanout.py:86`, `:487`, `:534`.

---

#### 13 · THE ORDERED PLAN — lines 1601–2499 (899) — **the big one**

**What it owns.** 30 checkbox items across RUNG 0–6 + OPTIONAL/HELD, each with a marker, a price, a cumulative
total and (mostly) a gate. Fully itemised in **§5A** below.

Beyond the items themselves it owns a great deal of unique material, most of it inside the valB_mini entry
(1644–1964, **321 lines** — 36 % of the section) and the NR-V04 feasibility entry (1986–2101, **116 lines**):
the four r0 consequences (r1+r2 cannot PASS: 0 PASS / 17,276 BORDERLINE / 11,885 FAIL; the n=3 round was never
decisive at 9 %; **the gate admits the null** at 22 % vs 23 %; two of three systematic-error detectors never
run); the convergence read-out; the seven diagnostic defects; the four callers that pinned the reverse leg
shut; the closure-triangle design with its **three enforced invariants** (2 fs, seed 0, unrestrained binary)
and **three corrections** (aza-scan not a double perturbation; $6.83/$27.32 not $5.9/$17.6; `_endpoint_pose`
cannot build cmpd4′); the ★ HONEST LIMIT (closure is identically zero for any per-endpoint state-function
error); the rev-leg decision tree with its retracted "worth buying under either branch"; the NR-V04 panel's
four measured findings and AMENDMENTS 1–2 (criterion **A1**, `MAX_COVALENT_TETHER_A = 8.0`, the C566-vs-C551
error, **28.42–39.11 Å** across all 34 co-fold models); the strided-trajectory requirement; and the pmx
benchmark table (**Y29A +4.424 ± 1.077 vs +3.40**, **Y29F −0.370 ± 0.175 vs −0.13**) with the
**6.2× noise-structure finding**.

**Classification: SPINE for the item layer; large APPENDIX extract for the rest.** 53 marker lines sit here —
more than any section except Appendix A. Concretely appendix-bound: the r0 superseded readings (−0.534 /
1.478, Appendix A 44 & 51); the P-series rescope refutation; the "worth buying under either branch"
retraction; the retracted 2026-07-24 "the panel is clean on this defect" forensics; the superseded 8.99/16.39 Å
A1 distances; the superseded "Gate: Val B-full + NR-V04 feasibility + Step 1 fan-out" wording; the superseded
5a-KS two-leg price; the superseded "a single chain carrying both needs 16"; the superseded fallback formulae.

⚠ **The item layer cannot simply be reformatted.** `work_ledger.py` parses this section (§3 below).

**Inbound links.** `work_ledger.py` / `work-ledger.json` / `tests/test_work_ledger.py`;
`degrader-paper-schedule.json` (the declared machine mirror, 12 refs); `step1-fanout-lane.md` (6);
`nrv04-retrospective-handoff-2026-07-24.md`; `nr4a3-nrv04-covalent-feasibility-prereg.md` (5);
`nr4a3-nrv04-retrospective-prereg.md` (6); `nrv04-retrospective-prereg.json`;
`valB-mini-r0-verdict-2026-07-25.md` (3); `valb-gate-defect-fix-audit-2026-07-25.md`;
`valb-calibrator-rescope-2026-07-25.md`; `valb-closure-triangle-pregate-2026-07-25.md`;
`protfep_*.py` (5 modules), `gpu-protfep-vast.yml` (2), `protfep-pmx-plan.md`;
`nr4a3-post-pilot-sequence.md` (6); `nr4a3-congeneric-rbfe-plan.md`; `nr4a3-leadopt-fep-readiness.md`.

---

#### 14 · Spend summary — lines 2500–2576 (77)

**What it owns.** **PINNED TOTAL ~$169 mid (~$46–626)**, and — critically — the **derivation**: the tool
prices 9 stages at **$149.63 ($36.58–531.46)** at **$0.1143/ref-GPU-h**, plus the five non-tool stages at the
machine registry's [low, mid, high]. The exclusions (confirmatory wedge; Optional/HELD ΔG_open + ABFE). The
**⚠⚠ the `$/hr` axis is measured, the GPU-HOUR axis is not** warning and the dominant-uncertainty ordering.
The **rung table** (8 priced rows + 2 excluded). And the ruling on **what survives every reprice**: the six
levers are ratios; the *precision* argument for mechanism-first is **retired by measurement** and must not be
re-quoted; the two surviving arguments (a categorical handle needs no margin; the categorical screens are $0).

**Classification: SPINE.** This is the ladder's arithmetic and it is CI-derived.

**Inbound links — the hardest-wired in the file.**
`pinned-figures.json` → `derivations.ladder_total.must_appear_in` **requires the string to appear in
STRATEGY.md, pricing.md and bid-strategy.md**, and `lint_consistency.check_derivations` recomputes it from
`vast-ladder-repricing.json` and fails the build if any of the three drifts. `pricing.md:323` and
`bid-strategy.md:291–292` carry the matching figures, and bid-strategy explicitly says
*"[STRATEGY.md → Spend summary](../../STRATEGY.md) carries the derivation and is [authoritative]."*
`pinned-figures.json` → `table_completeness.bid_strategy_repriced_ladder` cross-checks the rung table's row
set against the cost model's. `vast_cost_model.py` regenerates it.

---

#### 15 · Dependency spine — lines 2577–2617 (41)

**What it owns.** The ASCII ladder: TIER-0 → RUNG0 → RUNG1 → RUNG2 → RUNG2b → RUNG3 → RUNG4 → RUNG5 →
inverse_linker → RUNG6, with `(Cum ~$N)` at each rung, the `[x]`/`[~]`/`[!]` markers, the branch outcomes at
RUNG 2b and RUNG 5, the inline `[!]` explanation for `nrv04_feasibility`, the perses-retired note, and the
terminal **`OPTIONAL/HELD (explicit nod only): dg_open_paralogue, abfe_conditional (incl. the λ-repair)`**.

**Classification: SPINE — and it is the layer that must NOT be merged into the map's §1 graph.** It is a
*spend* graph: its edges are authorisations, not entailments.

**Inbound links.** `pinned-figures.json` → `subset_checks.strategy_spine_cum` is a CI check that every
`(Cum ~$N)` in the spine also appears as a `Cum. ~$N` in the ordered plan. It matches by **regex over the
whole file**, with two deliberately different formats (`Cum ~\$([0-9]+)` for the spine, `Cum\. ~\$([0-9]+)` for
the plan). ⚠ **If the merge normalises those two formats to one, `check_subsets` raises
`X-pattern-found-nothing` as an ERROR** — by design, since "a check that matches nothing silently passes
forever". The spine must keep a *distinct* cumulative notation from the plan's.

---

#### 16 · ★★ What the landed results change about the remaining plan — lines 2618–2781 (164)

**What it owns.** The only place that says what the landed results mean **for what is still unbought**:
1. The demoted marginal axis was demoted on an assumption since measured — a **re-rank, not a re-order**;
   remedy for a blunt tool is sampling, for an uncalibrated one a calibrator, and the plan was buying neither.
2. The FAIL was measured on the **worst-cancelling** form (`ΔΔG_coop`, two environments differing by a whole
   protein chain) and the flagship uses the **best-cancelling** one (`S`) — with the explicit ⚠ that this is
   **not a licence**: *"the valB FAIL is not a reason to leave `S` unbought — it is a reason `S` needs its own
   known answer."*
3. The n=1 design defect and the **$0 machinery check** that cleared it (the `seed % n_models` wrap is gated
   on `target_acc == "P51532"` and cannot reach a 5a-KS leg; 5a-KS is one co-fold per species by design;
   a second seed is genuinely independent sampling but buys **no** pose independence).
4. The strided-trajectory requirement, **built and wired** as `md_analysis_traj.py` — with the honest
   statement that it is an *analysis-atom* closure (~1k atoms, single-digit MB), not a full heavy-atom
   trajectory (~2.8 MB/frame), and that all three historical defects become $0 re-derivations.
5. The NR-V04 retrospective's gate could no longer be satisfied by anything — **"abandoned without saying
   so"** — and the decision that ended it.
6. **★ THE RANKED LIST — decision value per dollar** (nine ranks + one explicit exclusion). This is the one
   home for what to do next; §Current front (2806) defers to it by name.

**Classification: SPINE.** This is the merged document's "what next" reasoning layer, and it should sit
directly against the item plan.

**Inbound links.** No external file names this section (its heading is emoji-and-caps and unlinkable), but
`valb_failure_propagation.py` implements items 2, 3 and 8 (`error_algebra`, `s_error_bar_scope`,
`s_resolvability_from_R_ternary`, `sigma_leg_now_bounded`, `frozen_rule_vs_measured_power`,
`module3_decision`) and `md_analysis_traj.py` implements item 4.

---

#### 17 · Current front — lines 2782–2816 (35)

**What it owns.** Almost nothing, by its own admission. Its three substantive statements are all restatements
that name their own homes: *"the IN FLIGHT board at the top of this file, which is their one home — ⚠ **and
this paragraph must never restate it**"*; *"★ WHAT IS ACTUALLY NEXT is not on this page … the ranked list …
[is] in §WHAT THE LANDED RESULTS CHANGE 6, which is their one home; **this paragraph deliberately does not
restate the order**."* The one thing it *does* own is the sharpest statement of the feasibility panel's
status: **WITHDRAWN — not merely "under correction"** — which directly contradicts the ORDERED PLAN's `[!]`
marker and the schedule JSON's `under_correction` (see §5C-1).

**Classification: DUPLICATE.** Which copy wins: the IN FLIGHT board (live state), §16.6 (ordering), and — for
the feasibility panel — **this section's WITHDRAWN**, because it is the later and stronger statement and the
ORDERED PLAN entry's own body already says the re-run is `[HELD]` and "do not pay for the re-run as built."
The section's own history (it "said *three lanes are billing* for a day after the board said nothing was")
is the argument for dissolving it rather than carrying it.

**Inbound links.** None. Zero external files name "Current front". It can be dissolved safely.

---

#### 18 · Open decisions — lines 2817–3131 (315)

**What it owns.** 15 numbered entries (1–13 plus 9b, with 9 out of numeric order after 9b). **Thirteen are
`[x]` closed**; the two `[~]` sub-questions embedded in 11 and 12 are retained *as they stood* under closed
decisions. So **no decision in this section is currently open.**

Closed-decision content that is genuinely load-bearing and lives nowhere else:
- **5** — `GPUS_ALL_REGIONS` is permanently unavailable, do not re-file; the GCP lane is **dollar-bound, not
  time-bound** (~$292 ≈ 9 more full ternary legs; cap $300, spent $8); the measured card probe that
  **inverted** the spec table (workload is compute-bound; T4 ~0.31× the L4, not 1.07×; the spec table also
  compared whole-VM against bare-GPU prices) ⇒ **stay on the L4**.
- **6** — no rescope of the valB calibrator's **edge** can help, because `R ≈ 0` localises the miss to an
  endpoint-state error, a property of the model or the reference data.
- **7** — the admits-zero gate defect is **moot for valB_mini** (which failed on sign) but **binds the
  S-calibrator spec**: no accuracy band wider than the signal being calibrated, and a stated null-rejection
  rate up front.
- **8** — the `UNDERPOWERED` proxy is **vindicated** (0.216 vs the frozen 0.200, ~7 %); the live question is
  where σ_leg actually sits inside [0.045, 0.265].
- **9b** — the $0 S-calibrator survey: **2 of 10** paralogue pairs are symmetric; the SMARCA4→SMARCA2
  substitution was **not avoidable for this ligand** (Wurz compound 1 co-crystallised only with SMARCA4);
  the calibrator is built on the **lowest-resolution structure in the family, 3.73 Å**, and on the wrong
  paralogue. **Binding consequence: pick a pair whose reference data and structure sit on the SAME protein.**
- **9** — valB_full is **NOT** amended and module 3 is **NOT** decoupled. *The prospective NR4A ternary matrix
  stays unrun and cooperativity claims stay exploratory.*
- **10** — the protein-mutation cycle is **not an independent second causal line**.
- **11** — `S` gets **n = 2 seeds per arm**.
- **12** — the NR-V04 retrospective runs **Arm E; Arm F stays blocked on the valB PASS**.
- **13** — the "`S` has no calibrator" gap is **two** items: (a) *can a null be read?* — $0, **done**;
  (b) *can a non-null be called calibrated?* — paid, **deferred**. **`S` may be bought and read as a bound
  now; it may not be reported as calibrated until (b) exists.**

**Classification: SPLIT.** The *rulings* (5, 6, 7, 9, 9b, 10, 13, and 11/12's outcomes) are **SPINE** —
they are binding constraints on future work, and several are the only home for their content. The *deliberation*
(the "The question, as it stood" blocks under 11 and 12, ~55 lines; the two superseded GCP card tables and the
withdrawn P100/T4 reading, ~40 lines; decision 4's superseded hold text, ~10 lines) is **APPENDIX**.

**Inbound links — the largest single set.** **30 external files** cite "Open decision N" alongside STRATEGY:
`valb_failure_propagation.py`, `valb_triangle_closure.py`, `valb_triangle_reduce.py`,
`valb-triangle-reduction.json`, `s_calibrator_survey.py`, `s-calibrator-survey.json`,
`selectivity_resolution_options.py` + `.md` + `.json`, `selcal_panel.py`,
`selcal_reference_selectivity.py` + `.json`, `selectivity-sensitivity-control-prereg.md`,
`ternary_vast_launch.py` + `tests/test_ternary_vast_launch.py`, `ternary-vast-watch.json`,
`vast_cost_model.py`, `gcp_card_bench.py`, `nr4a3-nrv04-retrospective-prereg.md`,
`degrader-paper-schedule.json`, `pinned-figures.json`, and four workflows
(`gpu-bench-gcp.yml`, `gcp-quota-check.yml`, `gpu-ternary-fep-vast.yml`, `fusion-cpu-extras.yml`).
**They cite by NUMBER, not by anchor.** Any renumbering silently breaks 30 files with no CI signal — there is
no check that "Open decision 11" resolves to anything. **The numbering must be frozen across the merge.**

---

#### 19 · Appendix A — superseded numbers and retracted claims — lines 3132–3210 (79)

**What it owns.** **76 rows** (numbered 1–65 with 19a/19b/19c/19d and a trailing framing row), each pairing a
superseded claim with what retired it, under the standing instruction *"Do not cite anything in this table."*

⚠ **The map states this appendix has "~113 entries" (map §2, line 116). The measured count is 76 rows.**
Correct the map's sweep target before the sweep is scoped against it.

**Classification: APPENDIX** — it already is one, correctly.

**Inbound links.** **The most-cited section in the repo by anchor.** 6 anchor links resolve to
`STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims`, from `CLAUDE.md` (×2, lines 204 and 446)
and `nr4a3-program-map.md` (line 147). **35 external files** cite "Appendix A" by row number alongside
STRATEGY, including `realised_spend.py` (rows 35 and 38 are read as data provenance), `pricing.md`,
`bid-strategy.md`, `vast-placement-facts.md`, `atom_map_audit.py`, `arrival_throughput.py`,
`selcal_xtal_stage.py`, `selcal_cofold_validate.py`, the paper, and four test files.
⚠ **Row numbers are cited as data.** `realised_spend.py:167` says `"read_from": "STRATEGY.md Appendix A row 35"`.
**Row numbering must be frozen and the heading slug must not change.**
`lint_consistency.is_cleared` additionally treats *"a marker in the ENCLOSING HEADING"* as a structural clear
and names this heading as the example — so the appendix's rows are exempt from the superseded-value check
**by virtue of the heading text**. Changing the heading turns 76 rows into 76 CI errors.

---

#### 20 · Appendix B — superseded strategy framings — lines 3211–3230 (20)

**What it owns.** Six retired framings (atlas-anchor · two-papers-first · three-step spine · Track A ·
orientation-first · PR #3 note), the note that these were moved out of CLAUDE.md in 2026-07-25 where 168 lines
of plan mirror had accreted, and one durable inference-discipline paragraph: **NR-V04 is event-level proof
that family-selective NR4A degradation is achievable — never proof that the mechanism is known or
transferable.**

**Classification: APPENDIX**, except the closing inference-discipline paragraph, which is **SPINE** — it is a
live constraint on how NR-V04 may be cited and it belongs beside the language-discipline section.

**Inbound links.** `CLAUDE.md:216` ("Superseded plan framings … are in STRATEGY.md → Appendix B");
`nr4a3-program-map.md:147`; `emc-treatment-strategy.md`.

---

### 1c · The SPINE / APPENDIX split

| class | lines | share |
|---|---|---|
| **SPINE** (belongs in the merged source-of-truth document) | **~2,430** | 75 % |
| **APPENDIX** (history, superseded values, retracted claims) | **~430** | 13 % |
| **DUPLICATE** (stated elsewhere; shrink to a pointer) | **~154** | 5 % |
| **STALE** (was true, no longer is) | **~216** | 7 % |
| **DEAD** (deletable outright) | **0** | 0 % |

⚠ **These are estimates for the mixed sections and are labelled as such.** The class of each *section* is
established from its content; the *line* split inside the six mixed sections (1a, 1b, 5, 10, 13, 18) is
apportioned from the measured marker-line density (242 marker lines) expanded by the observed ~3–6-line
hard-wrapped sentence. Exact sections with no apportionment needed: SPINE-only = 0, 2, 3, 4, 6, 7, 8, 9, 11,
14, 15, 16 (**1,131 lines**); APPENDIX-only = 19, 20 (**99 lines**); DUPLICATE-only = 12, 17 (**154 lines**);
STALE-only = 1c (**45 lines**).

**Nothing classifies as DEAD.** Every candidate for deletion turned out to be either the one home for a
durable fact (§1c's three watchdog findings), a pointer that other files rely on (§12, §17), or already
correctly filed as history (§19, §20).

---

## 2 · Inbound-reference surface

**100 distinct files reference `STRATEGY.md`, across 358 mentions** — 43 Python modules, 41 markdown docs,
10 JSON artifacts, 6 workflows.

### 2a · Hard (machine-enforced) dependencies — these break the build

| consumer | binds to | what breaks |
|---|---|---|
| `work_ledger.scan_plan_items` | `## … THE ORDERED PLAN …` heading + the bullet regex `^(\s*)-\s+\*\*`\[([ x~!–-])\]`\s*(.*)$` + `### <rung>` sub-headings + `_GATE_MARKERS` prose phrases | Renaming the heading → `NOT SCANNED — no '## … THE ORDERED PLAN …' heading found. The plan is invisible this run.` Reformatting the bullets → every open item silently vanishes from the work board. ⚠ The skipped marker is an **en dash (U+2013)**, not a hyphen. |
| `lint_consistency.check_subsets` (`strategy_spine_cum`) | the Dependency spine's `Cum ~$N` **and** the ordered plan's `Cum. ~$N`, as two *distinct* regexes over the whole file | Normalising the two notations → `X-pattern-found-nothing`, ERROR, by design |
| `lint_consistency.check_derivations` (`ladder_total`) | the string `~$169` / `~$46` / `~$626` appearing in STRATEGY.md (`must_appear_in`) | Removing or restating the Spend summary total → `D-*` ERROR |
| `lint_consistency.is_cleared` | the exact heading `## Appendix A — superseded numbers and retracted claims` as a structural clear | Renaming → all 76 appendix rows become superseded-value violations |
| `lint_consistency.check_superseded` | STRATEGY.md is `targets[0]`; 59 registered patterns are matched against it | Moving a superseded value out of marker range → `S-*` ERROR |
| `lint_claims.py` | 21 provenance strings naming "STRATEGY.md → Honest scope and language discipline" and its R1–R5 wording | Renaming/dissolving → 21 stale provenance strings in a CI-enforced linter |
| `degrader-paper-schedule.json` | *declared* one-for-one mirror of the ORDERED PLAN's stage tags | Adding/removing a plan item without a matching milestone id → `work_ledger.scan_rung_gates` reasons off a stale graph |

### 2b · Soft (citation) dependencies — these break provenance, not CI

| target | inbound | note |
|---|---|---|
| **Appendix A** | 6 anchor links + **35 files citing rows by number** | Row numbers are cited **as data** (`realised_spend.py:167`). Freeze numbering + slug. |
| **Open decisions** | **30 files citing decisions by number** | No CI check resolves a decision number. Freeze numbering. |
| **§ GATE FAILED (SMARCA2/4)** heading slug | 1 anchor link (`nr4a-repanel-prereg-DRAFT.md:9`) | The only non-Appendix-A anchor link in the repo. |
| **MECHANISM-FIRST** | 12 files | Owns the resolvable-margin pair; `tests/test_selectivity_margin_model.py` asserts the derivation. |
| **Honest scope** | 16 files | See 2a. |
| **prospective stage** | 14 files | `e3_recruiter_staging.py:82` says its panel is this section "verbatim". |
| **Appendix B** | 2 files + CLAUDE.md | |
| **Spend summary** | `pricing.md`, `bid-strategy.md` | Both declare STRATEGY.md authoritative for the derivation. |
| **GPU economics** | 3 files | `bid-strategy.md:177` calls out a stale line here by name. |
| **Current front** | **0 files** | Safe to dissolve. |
| **Validation architecture** | 0 by name; content cited by ≥6 modules | See §1 detail. |
| **Dependency spine** | 0 by name; 1 by CI (2a) | |

---

## 3 · (A) THE ORDERED PLAN, itemised

30 items. `#` is the line number of the item's bullet. `sched` is the matching `degrader-paper-schedule.json`
milestone id and its status. **⚠ flags a marker that disagrees with the schedule JSON or with a later section
of STRATEGY.md itself** — enumerated in §5C.

### RUNG 0 — free / already done (~$0)

| # | id | one line | GO/NO-GO gate | cost | marker | sched |
|---|---|---|---|---|---|---|
| 1608 | charge-model fix | `ambertools>=23` + `partial_charge_method="am1bcc"` on the BINARY path | none (enabling fix) | $0 | `[x]` | — |
| 1611 | Step 0 — RBFE infra shakeout | one OpenFE edge end-to-end via the spot-safe split | converged ΔG_morph → GO; returned **−48.75 ± 0.57** | ~$1–2 | `[x]` | `step0_rbfe_mechanics`/done |
| 1614 | EMC E3-ligase expression | all 10 components of CRL2^VHL + CRL4^CRBN broadly expressed (HPA) | availability must **not** constrain the recruiter choice → decide on geometry | $0 | `[x]` | `emc_e3_expression`/done |
| 1617 | Pocket-tracking re-analysis | harmonized detection → Gate-2 wording | 8XTT **19/20 detected, 3 ≥ D\*=0.53**; release 44/75 = 59 % pooled | $0 | `[x]` | `pocket_reanalysis`/done |

### RUNG 1 — reference-reproduction smoke

| # | id | one line | gate | cost | marker | sched |
|---|---|---|---|---|---|---|
| 1624 | Validation A-mini | TYK2 `ejm31→ejm42` build-consistency smoke + cite OpenFE | abs err **0.61** vs a 2.0 tolerance → **PASS/GO to Rung 2**. Scope: **am1bcc binary lane only** | ~$0 · Cum ~$2 | `[x]` | `valA_mini`/done |

### RUNG 2 — cheap precision + cheap probes *(only if Rung 1 = GO)*

| # | id | one line | gate | cost | marker | sched |
|---|---|---|---|---|---|---|
| 1636 | Step 1 pilot — cmpd19 conditional RBFE | first congeneric edge on the real NR4A3 system | pipeline converges without pocket collapse → cleared (**ΔΔG_bind +1.84**) | ~$2.8 ($0.8–8.5) · Cum ~$4 | `[x]` | `step1_pilot_cmpd19`/done |
| 1644 | **Validation B-mini** | Wurz SMARCA2–VHL cmpd1→cmpd4 all-binding graded cooperativity edge | **verbatim from the prereg:** positive sign **+** CI excludes zero **+** no fwd/rev disagreement **+** no collapse/escape/restraint-dominated leg **+** broad consistency with **+0.94**. ⚠ the ±1.0 band was **deliberately removed 2026-07-17 — do not re-introduce it**. Gates valB_full only | ~$8.8 ($3.2–22) · Cum ~$13 | `[~]` ⚠ | `valB_mini`/**done** — **FAILED on sign**, n=3 mean **−0.599**, abs err **1.543** |
| 1899 | Rung 2b — 4 fs adoption + matched re-calibration | one edge at `timestep_fs=4.0` / `warmup 1.0` / `use_preequil=1` / `reset_commits=1` | **no NaN across the full leg AND \|ΔΔG_coop(4 fs) − (−0.534)\| ≤ 0.7** (ratified pre-specification). NaN or shifted ΔΔG → stay at 2 fs | ~$4.4 ($1.6–11) · Cum ~$17 | `[ ]` "PROPOSED, needs a go" ⚠ | `ternary_4fs_recalibration`/**done** — **PASSED both stages**, \|Δ\| = **0.0215** |

### RUNG 3 — expand the benchmarks *(only if Rung 2 probes look promising)*

| # | id | one line | gate | cost | marker | sched |
|---|---|---|---|---|---|---|
| 1968 | Validation A-full | 10–20-edge public RBFE benchmark | **SKIPPED** — redundant with OpenFE's published benchmark; saves ~$50–140 | — | `[–]` | `valA_full`/skipped |
| 1972 | Validation B-full — component-calibration cube | 4 separately-calibrated modules + the cis-epimer negative-endpoint stress module; module 3 = SMARCA2-vs-SMARCA4 | **the prospective ladder never runs unless the cooperativity + paralogue-discrimination modules pass** | ~$22.5 ($6–67) · Cum ~$40 | `[ ]` | `valB_full`/pending ⚠ **module 1 FAILED and Open decision 9 declined to amend ⇒ this gate cannot fire** |
| 1986 | NR-V04 covalent feasibility panel | covalent celastrol–NR4A1 adduct + C551A + noncov/cov sensitivity + warhead/recruiter controls; 18 legs | frozen `panel_verdict()` → **`go: false`** on the panel's own legs (both negative controls positive); **AMENDMENT 1** retired R2 + criterion 3; **AMENDMENT 2**'s binding **criterion A1** (electrophilic C within **8.0 Å** of the *target-chain* Cys Sγ) **fails now** at **28.42–39.11 Å** across all 34 co-folds | ~$8 measured · Cum ~$48 | `[!]` ⚠ | `nrv04_feasibility_covalent`/under_correction ⚠ **§Current front says WITHDRAWN** |

### RUNG 4 — warhead map, differential atlas, retrospective gate

| # | id | one line | gate | cost | marker | sched |
|---|---|---|---|---|---|---|
| 2105 | Step 1 fan-out — cmpd19 congeneric map | 19 congeneric RBFE edges, tranche 1 (charge-conserving, primary frame) | **Val A satisfied (cite OpenFE) AND the Step 1 pilot behaved** | ~$36 ($15–80) · Cum ~$84 | `[~]` ⚠ | `step1_fanout_cmpd19`/**done** — 18 of 18 computable, **$73.79** vs a derived **$74.91** cap; 1 edge permanently blocked; **one of three cycles does not close** (R = +1.307) |
| 2124 | Step 1 fan-out · replicates on the open cycle | 3 edges × 2 further replicates | **Gate: the market, on the same buy line.** **NO-GO reading:** if the replicated cycle still fails to close, the defect is mapping/setup and the three edges are **withdrawn from the ranked table** | ~$25 · Cum ~$109 | `[ ]` | `step1_fanout_replicates`/pending |
| 2151 | Generation-matched null — GENERATIVE arm (control c) | fresh generation into the NR4A1 metad-opened pocket through the identical funnel | **Gate: none upstream.** Reading preregistered: manufactured rate ≥ the real campaign's own ⇒ confound **not** excluded and §2.6/§2.7 keep their hedges; materially below ⇒ not a generic funnel artifact. **Either outcome is publishable and neither unlocks anything** | $0 prep **DONE** + **PROJECTED** GPU, excluded from the pinned total per Spending rule 4 | `[ ]` | `genmatched_null_generative_arm`/pending |
| 2184 | TIER-0 · NR4A paralogue-unique reactive-residue map | full-length UniProt + dual aligner + matched-model geometry | **GATE PASS/GO** — 4 unique cysteines (C397/C420/C559/C166), 4 unique lysines (K572/K518/K592/K178). *The FIRST gate in the ladder* | $0 | `[x]` | `nr4a_unique_residues`/done |
| 2196 | NR4A differential surface atlas | matched SASA + BLOSUM62 over NR4A{3,1,2} opened models | **GATE PASS/GO** — **46** differential-surface handles; a surface exists to steer an E3 against | $0 | `[x]` | `nr4a_differential_atlas`/done |
| 2202 | NR-V04 retrospective *(HELD entry)* | the same item, repriced onto the 2800-iteration basis after a $0 pre-spend audit found two sequential silent blockers | **HELD 2026-07-25** — collector/driver key mismatch (fixed); the covalent R2 arm is unbuildable and **blocks R1**. AMENDMENT 3: R2 **retired**, authorized panel = **R1 only** | ~$24 ($5.6–78) · Cum ~$107; a GO spends **Arm E ≈ $7.7** | `[!]` ⚠ | see below |
| 2239 | NR-V04 retrospective *(frozen-gate entry)* | full ensembles, no tuning, epimer control; directional concordance only | **Gate reconciled 2026-07-30 (Open decision 12): ARM E RUNS, ARM F stays blocked on the valB PASS.** *Superseded:* "Val B-full + NR-V04 feasibility + Step 1 fan-out" applied to the whole item. **GO/NO-GO:** directionally concordant with NR4A1-degraded / NR4A2·3-spared → GO to the prospective ladder; **discordant → the ladder is not justified, publish the honest negative.** Hard precondition (met): durable trajectory | ~$21 ($4.8–67) · Cum ~$104 | `[ ]` ⚠ | `nrv04_retrospective`/**done** — **RAN; tier DISCORDANT, p = 0.392857** |

⚠ **Missing item.** `selcal_sensitivity_control` (RUNG 4b, the SMARCA2/4 method calibrator) is a schedule
milestone with a landed **NULL** verdict and a frozen gate (`selcal_panel.PASS_CRITERION`), and it has
**no ORDERED PLAN entry at all** — only the timestamped headline at line 351. `work_ledger.scan_plan_items`
therefore cannot see it, and neither can a reader reading the plan top-to-bottom. **The merged plan layer must
add it.**

### RUNG 5 — mechanism-first prospective ladder

| # | id | one line | gate | cost | marker | sched |
|---|---|---|---|---|---|---|
| 2272 | 5a · Orientation-basin search, mechanism-first | broad transform sampling across the widened E3 set, matched 3-paralogue scoring over the pose ensemble, ~3–8 basins/ligase | **TIER-2 GO, basis CATEGORICAL** — 58 meta-basins / 192 basins; 3 term (a), 40 term (b), 28 nominally discriminating. Mandatory ≤2 downselect **done**: CRBN (9CUO) + VHL (9GIO, backfill) | ~$0 realized (budget $0–50) · Cum ~$129 | `[x]` | `orientation_basin_search`/done |
| 2290 | **5a-KS · Wedge confirmation — the KILL-SWITCH** | `S = ΔΔG_coop(d₀→d\|NR4A3) − ΔΔG_coop(d₀→d\|NR4A1)`, ternary legs only, **4 legs at n = 2 seeds/arm** | **Tier 3.** ⚠ *"No discrimination ⇒ STOP" is SUPERSEDED.* `S` is non-covalent ⇒ it tests the **marginal** wedge only. **`S ≈ 0` ⇒ the marginal wedge is absent and the claim rests on the categorical axis alone; STOP only if the categorical axis has ALSO failed.** Discrimination ⇒ extend to NR4A2 + a second design element. Evidence grade: a NO-GO may be taken on valB_mini-grade evidence; a POSITIVE stays **exploratory** until valB_full passes | ~$23 ($3.1–97) · Cum ~$152 *(supersedes ~$12/Cum ~$141, the two-leg config)* | `[~]` "PARKED, not finished" ⚠ | `selectivity_wedge_confirm`/**done** — **LANDED 2026-08-02, S = −0.1297 ± 0.3264** |
| 2290b | 5a-KS · CONFIRMATORY protein-mutation cycle | reciprocal `ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary` on pmx + GROMACS | **Known-answer benchmark PASSED 2026-07-25** (Y29A +4.424 ± 1.077 vs +3.40; Y29F −0.370 ± 0.175 vs −0.13; ordering correct). ⚠ **Open decision 10: NOT an independent second line** — same ternary-minus-binary shape as the quantity that failed. **Still owes a WEDGE-SIZED benchmark before it may claim to resolve a paralogue-scale difference.** Two blockers cleared in code: `assert_charge_consistency`; `plan_wedge` refuses charge-changing mutations (**R412 R→A is one**) | **~$4.6 PROJECTED**, excluded from the pinned total (particle-count scaling, not a measured rate) | (inside 2290) | — |
| 2417 | 5b · Two-mechanism reach | can one chain carry the covalent electrophile **and** the causal wedge? | **Gate: none.** Pre-registered NO-GO reading **half-fires**: the blocker is the chain **template** (one `pendant`), not the grid and not geometry. The honest report is *"the enumerated architecture carries one mechanism per molecule"* | $0 | `[x]` | `segment_grid_reenumeration`/done |
| 2436 | 5b · The two-branch template | `linker_twobranch.py` — **exactly one** chain satisfies both windows (n = 18, a2–a2–a2, 5-amide warhead, electrophile k=13, wedge k=6) | **Unlocks nothing downstream and no gate.** ⛔ A two-branch template is a **DESIGN change to a preregistered enumeration**, not a defect fix — **"it needs an explicit decision, and it is not taken here."** Claim ceiling: *constructible and window-admissible against TRANSFERRED windows*. Costs median **+10 heavy atoms / +120 Da**, top of set **1248 Da** vs a committed range of 698–1099 | $0 | `[x]` | — |
| 2465 | 5b · Inverse linker design | 1,995 enumerated → 21 retained, RDKit 21/21 *(library now 54 — see the scoreboard deliverable)* | basin-fidelity filtering, not atom count | ~$0–20 · Cum ~$162 | `[x]` | `inverse_linker_design`/done |
| 2471 | 5c · Explicit ternary-ensemble refinement | replicated ternary + full CRL/E2~Ub MD across target states, linker conformers, in-basin poses; matched NR4A1/2/3 | gated behind 5a-KS discrimination. Adds a constraint: **which lysine the ubiquitin actually reaches**, per construct, as a distribution over unique-vs-conserved sites | ~$21 ($1.9–85; 24–~200 legs) · **Cum ~$183** ⚠ | `[ ]` | `ternary_ensemble_refine`/pending |
| 2477 | 5d · Local ternary FEP | alchemy only within a retained basin → ~6–12 candidates | both endpoints plausibly bound; modest congeneric change. **Deliverable** = the prioritized, structure-defined, retrosynthetically annotated candidate set with an identified causal mechanism — degradation experimentally unvalidated | ~$21 ($3.1–87) · **Cum ~$169** ⚠ | `[ ]` | `local_ternary_fep`/pending |

⚠ **The `Cum.` chain is non-monotonic across 5b→5c→5d: $162 → $183 → $169.** `lint_consistency`'s subset check
only verifies that the *spine's* values are a subset of the plan's; it does not check the plan's own ordering.
The merged plan layer should regenerate the chain rather than carry it.

### OPTIONAL / HELD — only if a specific claim needs them **and** a budget nod is given

| # | id | one line | gate | cost | marker | sched |
|---|---|---|---|---|---|---|
| 2485 | ΔG_open per paralogue | integrate a converged opening penalty per paralogue | **HELD — explicit budget nod.** Only to make affinity/selectivity **unconditional**; otherwise report conditional on the open state ($0, fully defensible) | ~$120–300 | `[ ]` | `dg_open_paralogue`/pending |
| 2487 | Conditional ABFE (pose-plausibility) | raw ABFE, T4L discrepancy reported separately, **no offset** | **HELD — explicit nod after everything above.** *This hold covers the existing ABFE block's λ-overlap repair too — it is parked, not in flight.* Requirement 3 adds three technical preconditions: the accuracy benchmark must pass, the opening penalty must be handled, and multiple poses must be treated | ~$80–200 | `[ ]` | `abfe_conditional`/pending |

### RUNG 6 — write & ship (~$0)

| # | id | one line | gate | cost | marker | sched |
|---|---|---|---|---|---|---|
| 2493 | Fold results into paper | language discipline; QM/torsion at linker junctions; physchem + retrosynthetic; re-render figures | — | $0 | `[ ]` | `fold_results`/pending |
| 2495 | Final red-team + review-response | — | — | $0 | `[ ]` | `final_redteam`/pending |
| 2496 | Post + submit | ChemRxiv (CC-BY) + JCIM + outreach | **OUTWARD-FACING — needs trimcrae sign-off** (CLAUDE.md §3) | $0 | `[ ]` | `post_submit`/pending |

---

## 4 · (B) The five requirements (line 1031) mapped onto the map's claims

⛔ **THIS IS THE MOST VALUABLE SECTION IN THIS FILE. Four of the five requirements are not reflected in the
map, and three of those four are live over-claim risks.**

Method: each requirement's constraint is stated verbatim-in-substance, the map node/row/section it governs is
named, and the map is tested for whether it carries the constraint. The tests are **measured**, not asserted —
`grep -ci` over `nr4a3-program-map.md` for the requirement's own key terms returned:
`lysine 0 · ubiquit 0 · EWSR1 0 · valB 0 · kill-switch 0 · 5a-KS 0 · "opening penalty" 0 · ΔG_open 0 ·
Pareto 0 · CRL 0 · E2 0 · K572 0 · HELD 0 · Arm E 0 · Arm F 0 · DISCORDANT 0 · composed 0 · 17.1 0`.

---

### Requirement 1 — three DIFFERENT validations, never one standing in for another

**Constraint.** **(A) Accuracy control** — a public RBFE benchmark through the *exact* container/protocol/force
field/water model/sampling/analysis. Cycle closure, fwd/rev agreement and MBAR overlap are **precision
diagnostics, NOT accuracy**. **(B) Target-specific precision** — the cmpd19 RBFE, framed as *conditional*.
**(C) Ternary known-answer control** — a system with an experimental ternary + measured cooperativity.
**NR-V04 is a biological-selectivity holdout, not the method calibrator.**

**What it governs in the map.** The whole of §3 (the instrument layer) and every dashed `-.validates.->` edge
in §1.

**Reflected?** ⚠ **PARTIALLY — and the gaps are structural.**

- ✅ The *principle* is the map's §3 thesis, stated well: *"An instrument that has never recovered a known
  answer cannot support a claim."*
- ✅ NR-V04-as-calibrator is correctly closed (map §2a row 1).
- ⛔ **Val A is absent.** No §3 row for `valA_mini` / the OpenFE citation, and — more dangerous — **no
  statement that the OpenFE accuracy citation does not cover the NAGL ternary or endpoint lanes.**
  STRATEGY.md line 1144 is explicit: *"Neither transfers to a NAGL ternary lane… Say this in the paper; do
  not let a reader infer the OpenFE citation covers the ternary numbers."* A reader of the map alone would
  take the ternary and endpoint lanes to be covered by a published accuracy figure. **LIVE OVER-CLAIM RISK.**
- ⛔ **Val C is absent, and it is the one that FAILED.** **`valB_mini` — the ternary known-answer control,
  which missed by 1.543 kcal/mol with the wrong sign — has no row in the map's §3 instrument table.** The
  alchemical ternary FEP engine appears nowhere as an instrument. The map's §5b Route A names the ABFE engine
  as the blocker and calls it *"the single highest-leverage item in the program"* — while the engine that
  produced §2.5's ternary numbers and the flagship `S` has a **known-answer test on the record that it
  failed.** **HIGHEST-SEVERITY OVER-CLAIM RISK IN THE MAP.**
- ⛔ The map's §3 conflates precision with accuracy in the opposite direction to the requirement: it lists
  the **pmx/GROMACS interface-mutation physics** as `✓ complete — PASSES`, without carrying Open decision 10's
  finding that its benchmark **passed on a protein-mutation quantity, not on the ternary-minus-binary shape
  the cycle actually computes**, nor the standing debt that it **owes a wedge-sized benchmark before it may
  claim to resolve a paralogue-scale difference**. A `PASSES` with no scope is exactly the over-claim §3
  exists to prevent.

---

### Requirement 2 — cryptic-pocket thermodynamics are conditional

**Constraint.** An affinity computed in a pre-opened pocket is **ΔG_bind|open**, not
ΔG_bind,obs ≈ ΔG_open + ΔG_bind|open. **Each paralogue can have a different opening penalty, so comparing
binding only in matched open receptors can MISS or REVERSE selectivity.** Either integrate a converged
ΔG_open per paralogue, or report everything explicitly conditional. Pocket collapse in MD is evidence the
state is unstable, not an auto-fail. **Never pool conformers of unknown population as equally weighted.**

**What it governs in the map.** §4 rows "A pocket exists" and "The binder is paralogue-selective"; §1 nodes
`PO`, `L`, `B`; **and all of §5b Route A**, whose entire chemical case is a set of pocket-lining divergent
residues scored in an opened ensemble.

**Reflected?** ⛔ **NO — and this is the most consequential omission after requirement 1's Val C.**

- The map's §4 mentions "Gate 3B (equilibrium accessibility) still open", which is adjacent but not the same
  constraint.
- **The word "conditional" appears once in the entire map** (line 313), and it is about the *docked pose*, not
  about the opened state.
- **`ΔG_open` / "opening penalty" appear zero times.** The map does not say that a validated ABFE margin
  between NR4A3 and a paralogue, computed in matched opened receptors, **can carry the wrong sign** once the
  per-paralogue opening penalties differ. Route A is presented as blocked *only* on the instrument
  ("Blocked on the INSTRUMENT, not the chemistry") — which reads as: fix the ABFE engine and the margin is
  real. Requirement 2 says that is not sufficient. **LIVE OVER-CLAIM RISK.**
- The map has no reference to `dg_open_paralogue` being an OPTIONAL/HELD ladder item, so a reader cannot see
  that the unconditional version of the claim has a price ($120–300) and a standing hold.

---

### Requirement 3 — ABFE is HELD and reframed

**Constraint.** T4L-L99A·benzene is an implementation smoke test, **not a transferable offset** — report raw
ABFE, report the T4L discrepancy separately, **apply no offset**. ABFE does **not** prove cmpd19 "binds at
all"; it only asks whether the hypothesized pose is thermodynamically plausible. **Not worth running until the
accuracy benchmark passes, the opening penalty is handled, and multiple poses are treated.** Step 8 cannot
consume the anchor ABFE per construct. **HELD also means the λ-overlap repair of the existing ABFE block is
parked, not in flight — the manuscript must say so.**

**What it governs in the map.** §3 row "Selectivity free energy (ABFE)" (◐ in work); §1 node `V4` ("Physics
recovers a known ddG") and its dashed edge into `B`; §5b Route A; §6 critical-path item 5.

**Reflected?** ⛔ **NO.** `HELD` appears **zero times** in the map. The map presents an ABFE lane as `◐ in
work`, calls it *"the single highest-leverage item in the program, and it is the one thing moving"*, and
places it at §6 critical-path item 5 — with no statement that ABFE sits under a standing HOLD requiring an
explicit budget nod, that raw values must be reported with no T4L offset, that ABFE does not prove binding, or
that the λ-overlap repair is **parked**.

⚠ **In fairness, and stated because the distinction is real:** the CREBBP/BRD4 run is a *known-answer
selectivity benchmark* (`selectivity-benchmark.json`, verified today to still carry **no `result` key**),
which is arguably a different object from "conditional ABFE on cmpd19" (`abfe_conditional`). **But the map
draws no such distinction**, and requirement 3's sequencing clause ("not worth running until the accuracy
benchmark passes, the opening penalty is handled, and multiple poses are treated") is a constraint on the
ABFE machinery as a class. **The map should state which object it means and carry the hold on the other.**
**LIVE OVER-CLAIM RISK, and the cheapest of the four to fix.**

---

### Requirement 4 — NR-V04 is covalent

**Constraint.** Celastrol binds NR4A1 **covalently via C551**, so NR-V04 does not validate the noncovalent
machinery and its selectivity may be largely **target-engagement**. Model a **preformed covalent adduct**;
add a noncovalent-vs-covalent sensitivity analysis, an **NR4A1 C551A / nonreactive control**, and
**warhead-only + active/inactive recruiter** controls; preregister scoring on control (C). **Report only
directional concordance — never "recovered degradation."**

**What it governs in the map.** §2a row 1 ("NR-V04 as the positive control"); §5b Route B, which is
explicitly *"the NR-V04 mechanism relocated"*.

**Reflected?** ✅ **YES, for the core.** The map's §2a carries the confound correctly and with the right
evidence (Cys551 unique to NR4A1; C6→S **28.42–39.11 Å** against a ~1.8 Å bond), and reaches the right
conclusion — confounded **by construction**, no sample size fixes it.

**Two gaps, both minor relative to 1–3:**
- The map does not record that the **retrospective RAN and returned DISCORDANT** (`DISCORDANT` = 0 hits), so
  a reader cannot tell whether the holdout is unrun or answered. It matters: STRATEGY's scoreboard classifies
  it as a **NON-RESOLUTION**, not a failure, and that distinction is load-bearing for the standing tally.
- The required control set (preformed adduct, C551A, warhead-only, active/inactive recruiter, noncov-vs-cov
  sensitivity) was **built, run, and then retired** when the covalent legs were dropped and the panel
  re-scoped to noncovalent. The map has no register entry for that retirement — see §5C-3.

---

### Requirement 5 — the prospective stage is hypothesis PRIORITIZATION, not scoring

**Constraint.** Replace any tunable scalar with **staged gates + a Pareto/constraint-satisfaction front**, with
uncertainty on every axis. Model the **real biological object, EWSR1::NR4A3** — not an isolated LBD: fusion-
context ensemble; **lysines outside the LBD** (hinge, DBD, fusion partner); public EMC VHL/CRBN expression;
**full CRL/E2~Ub geometry ensembles**. **Ternary formation is necessary, not sufficient — productive lysine
positioning is a distinct requirement.** Plus the two 2026-07-25 measurements that bind *every* ternary /
degradation-geometry step: the ubiquitin-transfer distance is **17.1 Å, MEASURED** (the assumed 10 Å was
~7 Å too strict), and **a composed CRL RING carries ~30–50 Å of positional uncertainty**, so **no
degradation-geometry claim may rest on a RING or E2 that was COMPOSED rather than observed** (anchor on the
observed E2 catalytic cysteine — **8R5H** for VHL, **9UUM** for CRBN).

**What it governs in the map.** §1 node `T` ("TERNARY forms and **is compatible with degradation**"); §4 row
"A ternary forms"; §5b's "why they compose" argument; §6 items 4 and 6.

**Reflected?** ⛔ **NO — the most complete omission of the five.**

- **`lysine`, `ubiquit`, `CRL`, `E2`, `K572`, `Pareto`, `EWSR1` all return zero hits in the map.**
- The map's node `T` reads *"TERNARY forms **and is compatible with degradation**"* — **one node carrying
  both halves of a distinction the requirement exists to keep apart.** Requirement 5 says ternary formation is
  **necessary, not sufficient**, and that productive lysine positioning is a **distinct requirement**. The map
  has no node for it, so the graph cannot show it as unmet. **LIVE OVER-CLAIM RISK:** the map's §1 makes
  `TS → P` (ternary selectivity → paper) reachable without ever traversing a ubiquitination-geometry node.
- The **categorical term (b)** — the transfer-zone lysine-identity term, on which Tier 2's 40 term-(b) basins
  and the whole unique-lysine argument (K572/K518/K592) rest — appears nowhere. §5b's Route A and Route B are
  presented as the "two live routes to selectivity"; **term (b) is a third, and it is measured.**
- The **17.1 Å measured transfer distance** and the **composed-RING ban** are absent. The ban is a hard
  claim-ceiling on any future geometry claim; the map's §6 item 4 ("rebuild the ternaries by the assembly
  route") is precisely the step that must obey it, and does not say so.
- The **EWSR1::NR4A3 fusion context** is absent. The map's `TG` node is *"Target is a driver (EMC
  dependence)"*, which is a different claim (target validation), not the modelling-object constraint.

---

### Summary of (B)

| req | governs | reflected in the map? | severity |
|---|---|---|---|
| **1** Three different validations | map §3 + all dashed edges | ⚠ partial — **Val A scope and Val C (valB_mini) both absent**; pmx `PASSES` carries no scope | ⛔ **highest** |
| **2** Cryptic-pocket conditionality | §4 "pocket exists" / "binder is selective"; **all of Route A** | ⛔ no — ΔG_open and the sign-reversal risk absent | ⛔ **high** |
| **3** ABFE is HELD and reframed | §3 ABFE row; `V4`; Route A; §6 item 5 | ⛔ no — `HELD` appears 0 times; ABFE presented as the one thing moving | ⛔ **high, cheapest to fix** |
| **4** NR-V04 is covalent | §2a row 1; Route B | ✅ core yes; DISCORDANT + the retired control set missing | ⚠ moderate |
| **5** Prioritization, real object, ubiquitination geometry | node `T`; §4 "a ternary forms"; §6 items 4/6 | ⛔ no — **zero** hits for lysine/ubiquitin/CRL/E2/EWSR1/Pareto; `T` fuses two distinct requirements | ⛔ **high** |

---

## 5 · (C) Contradictions between the ladder's statuses and the map's

### 5C-0 · The register's own scope statement is measurably wrong

The map's §2 banner (line 116) scopes its rebuild against *"STRATEGY.md Appendix A (~113 entries)"*.
**The measured count is 76 rows** (numbered 1–65 plus 19a/19b/19c/19d and a trailing framing row). Correct the
target before scoping the sweep, or the sweep will look 33 % incomplete when it is done.

---

### 5C-1 · The four verified examples, and what each actually is

| ladder item | ladder status | in the map? | **verdict: dead / parked / held** |
|---|---|---|---|
| `nrv04_feasibility` `[!]` | Spine line 2593–2595: *"[!] = feasibility's GO is WITHDRAWN pending a corrected re-run: its readouts measured the Elongin C interface, not VHL↔NR4A1. It gates nothing until then."* §Current front (2785): **WITHDRAWN — not merely "under correction"**. Re-run is `[HELD]` | ⚠ **partially and confusingly.** The map's §2a row 1 uses the *feasibility panel's* evidence (C6→S 28.42–39.11 Å = criterion A1) to close *NR-V04 as the positive control* — which is the **retrospective's** confound, a different item | ⚫ **CONCLUSIVELY DEAD, and the map does not say so for the right reason.** Three independent data-invalidating defects; **no trajectory was ever persisted** (`trajectory_objects_found: 0`), so the specific result "can never be regenerated by anyone, including us" — the identical test the map applies to the §2.5 ternary. The *re-run* is separately `[HELD]` and unbuyable because criterion A1 fails on every available input |
| `perses` | Spine line 2605: *"perses retired: OpenEye-gated"*. Plan 2345–2348: its protein-mutation path round-trips residue templates through a licence-gated `OEMol`, *"with no conditional and no RDKit alternative on that path"*. Cost of establishing it: **~$0.05** | ⛔ **absent** (`perses` = 0 hits) | 🟡 **PARKED, and functionally moot.** A licence gate is not an impossibility — an RDKit path in `PolymerProposalEngine` reopens it. But the *avenue* (protein-mutation FEP) is **served** by pmx + GROMACS, which passed its benchmark, so this is a **retired tool choice**, not a closed route. It belongs in an appendix, **not** in the map's dead-ends table |
| `dg_open_paralogue` | Spine line 2615 `OPTIONAL/HELD (explicit nod only)`. Plan 2485: ~$120–300, *"only to make affinity/selectivity unconditional; otherwise report conditional on the open state ($0, fully defensible)"* | ⛔ **absent** | 🔵 **HELD pending a DECISION** (a budget nod). ⚠ **But requirement 2 makes it load-bearing the moment any unconditional paralogue-selectivity claim is made** — see §5B-2. It is not optional in the way the label implies |
| `abfe_conditional` (incl. the λ-repair) | Spine line 2615 `OPTIONAL/HELD`. Plan 2487: ~$80–200; *"This hold covers the existing ABFE block's λ-overlap repair too — it is parked, not in flight."* Requirement 3 adds three technical preconditions | ⛔ **absent as a hold**; an ABFE lane is shown `◐ in work` | 🟡🔵 **BOTH — and the ladder itself uses both words.** The **λ-overlap repair is PARKED** (requirement 3's own word: "parked, not in flight"); the **conditional ABFE run is HELD** pending a budget nod **and** three technical preconditions. The map showing an ABFE lane as the one thing moving, with no hold anywhere on the page, is the sharpest single ladder↔map contradiction |

---

### 5C-2 · Ladder markers that contradict a later section of STRATEGY.md or the schedule JSON

These are not map contradictions — they are **internal** to the plan layer, and every one of them will be
inherited by the merge if it is not fixed first. All five are `[~]`/`[ ]`/`[!]` markers that
`work_ledger.scan_plan_items` currently reports as **owed work**.

| plan item | marker | what the file says elsewhere | schedule JSON |
|---|---|---|---|
| Validation B-mini (1644) | `[~]` in progress | Scoreboard: **FAILED**, gate NO-GO, replicate SD 0.375 delivered; IN FLIGHT: *"CLOSED AT n=3"* | `valB_mini`/**done** |
| Rung 2b (1899) | `[ ]` "PROPOSED, needs a go" | Scoreboard: **PASSED — both stages**; IN FLIGHT: all four legs landed, 4 fs adopted | `ternary_4fs_recalibration`/**done** |
| Step 1 fan-out (2105) | `[~]` "RESUMED and RUNNING… 1 edge complete… 17 remaining" | Scoreboard + IN FLIGHT: **COMPLETE**, 18 of 18 computable, **$73.79**, lane closed 9:24 PM ET Jul 29 | `step1_fanout_cmpd19`/**done** |
| NR-V04 retrospective (2202 `[!]` **and** 2239 `[ ]` — **two entries for one item**) | `[!]` + `[ ]` | Scoreboard: **RAN, AND ANSWERED — DISCORDANT**; §16.5: resolved | `nrv04_retrospective`/**done** |
| 5a-KS (2290) | `[~]` "PARKED, not finished… both ternary legs HAVE run" | §RUNG 5a-KS LANDED (307): **all four legs landed 2026-08-02, S = −0.1297 ± 0.3264** | `selectivity_wedge_confirm`/**done** |
| NR-V04 feasibility (1986) | `[!]` "RESULT UNDER CORRECTION" | §Current front: **WITHDRAWN — not merely "under correction"** | `nrv04_feasibility_covalent`/under_correction |

⚠ **`work_ledger.py`'s own docstring flags this exact hazard** (line 108): *"WHETHER STRATEGY.md's MARKERS
AGREE WITH THE SCHEDULE'S STATUSES. Both are scanned, neither is [reconciled]."* It is a **NOT SCANNED**
coverage hole, stated honestly, and it has now been realised on six items at once.

---

### 5C-3 · Closed / terminal items in the ladder that are absent from the map's register

Every one of these has a terminal state in STRATEGY.md and **no row in the map's §2**. Classified per the
map's §0 bar (*"is there any future development that would make us retry this?"*).

| # | item | ladder evidence | classification |
|---|---|---|---|
| 1 | **The NR-V04 covalent feasibility panel result** | 3 independent data-invalidating defects; `trajectory_objects_found: 0`; frozen `panel_verdict()` returns `go: false` on its own legs | ⚫ **DEAD** — unregenerable, same test as the §2.5 ternary |
| 2 | **The covalent legs / celastrol–C551 re-fold route** | run and refuted for **$0.05**; deleting the E3 makes seating *worse* (33.6–44.7 Å); a **steered** co-fold honouring `max_distance: 6.0` still never satisfied its own bound on 3 seeds; 7/7 clean models, 4 seeds, 3 prefixes | 🟡 **PARKED** — the ladder itself says *"this is a statement about the predictor, not about whether celastrol binds C551"* (literature-anchored, Zhang 2018). A better predictor or a hand-placed pose reopens it |
| 3 | **The required covalent control set** (preformed adduct, C551A, warhead-only, active/inactive recruiter, noncov-vs-cov) | *"the covalent legs are DROPPED and the panel is re-scoped to NONCOVALENT"*; `~$6–8 not spent` | 🟡 **PARKED** with route 2 — ⚠ **and requirement 4 mandates them**, so the parking is a live constraint on what NR-V04 may be claimed to have tested |
| 4 | **Arm F of the NR-V04 retrospective** (the free-energy arm) | *"Arm F stays blocked on the valB PASS"* (decisions 12 and §16.5) — but valB **failed on sign** and decision 9 **declined to amend** | ⛔ **UNCLASSIFIED, AND THAT IS THE FINDING.** Its gate is now **unreachable**, which is exactly the state §16.5 named for Arm E: *"an item that is built, preregistered and idle behind a gate that cannot fire is not being held; it is being **abandoned without saying so**."* **Arm E got a decision. Arm F never did.** It needs one — held, or explicitly retired |
| 5 | **Step 3 — the NR4A1/2/3 re-panel** | selcal NULL ⇒ *"IT IS NOT BOUGHT"*; `nr4a-repanel-prereg-DRAFT.md` **retired unrun**; its own power section said ≤ 0.16 | ⚫ **DEAD as designed** — the tier and the power analysis point the same way; machine-carried by `selcal_gate.NEXT_STEP_BY_TIER` |
| 6 | **The valB_mini P-series rescope** | refuted for $0: **6 of 10** pairs change formal charge (incl. P1→P4, `charge_change: -1`); the 4 neutral ones perturb **58–80** heavy atoms vs 2; 9HYO is **3.74 Å** | ⚫ **DEAD for the P-series specifically.** ⚠ The broader claim — *"a ≥2 kcal/mol ternary calibrator that is simultaneously small, charge-neutral and mappable may not exist in the public literature"* — is a **conjecture**, not proof, and must not be filed as ✕ |
| 7 | **Rescoping the valB calibrator's EDGE at all** | Open decision 6: `R ≈ 0` ⇒ the miss is an **endpoint-state** error, a property of the model or the reference data; *"changing the edge changes neither"* | ⚫ **DEAD** — arithmetic (the telescoping identity), not effort |
| 8 | **`cw_bio_nmethyl_amide`** (fan-out edge 19) | no mapper reaches the **20-atom provable floor**; measured identical at t20 and t300, so the MCS timeout is *not* the mechanism; the one 19-atom map maps a carbon onto a hydrogen | ⚫ **DEAD** — a graph fact; more search time cannot fix it |
| 9 | **Cost lever 3 — sequential/anytime-valid stopping** | measured at **0.8–2.6 %** on this ladder, not 20–25 %; *"mechanism, not a fitting artifact"* — a 5-replicate ladder is too short for the bound to fire | ⚫ **DEAD for this ladder**, live for long horizons. *Do not carry it in any total* |
| 10 | **Raising `GPUS_ALL_REGIONS`** | Open decision 5: repeatedly requested, repeatedly refused; **and wrong on its own terms** — at quota 4 the same $292 is spent 4× faster | ⚫ **DEAD** — *"do not re-file it"* |
| 11 | **Switching the GCP lane off the L4** (P100/V100/T4) | both spec tables **WITHDRAWN**; measured T4 ≈ **0.31× L4** where bandwidth predicted 1.07×; the price column compared whole-VM against bare-GPU. *"STAY ON THE L4"* | ⚫ **DEAD** — refuted by measurement, and the sequencing question is closed rather than deferred |
| 12 | **Validation A-full** | `[–]` SKIPPED; saves ~$50–140; its re-open rider *"already fired"* and is discharged by Val B | 🔵 **HELD-as-skipped** — a standing decision, reversible only if the NAGL/am1bcc split changes |
| 13 | **valB_full module 3 decoupling** | Open decision 9: **NOT amended, NOT decoupled** — module 1's statistic *"did not lack discriminating power; it discriminated perfectly well and returned NO."* *"The prospective NR4A ternary matrix stays unrun and cooperativity claims stay exploratory"* | 🔵 **HELD by a taken decision.** ⚠ The consequence — **the entire prospective ladder (5c, 5d) is behind a gate whose module 1 has failed** — is the single largest structural block in the program and appears **nowhere** in the map |
| 14 | **The two-branch template as a design change** | *"a DESIGN change to a preregistered enumeration, not a defect fix… It needs an explicit decision, and it is not taken here"* | 🔵 **HELD pending a decision** — never asked for, still open |
| 15 | **The restrained binary re-run** (LANE 20) | *"HELD ON PURPOSE"* behind the **$0** pose diagnostic (`task=triangle-converge`), which *"has still never run"* as of 2026-07-31 | 🔵 **HELD pending a $0 observation.** ⚠ CLAUDE.md §4 is explicit that a $0 check is never "watching" — this is a hold on an answer that costs nothing |
| 16 | **MM-GBSA rescore of Tier 2** | *"NOT run, and recommended against — it would refine the very axis the mechanism-first reframe demoted"* | 🔵 **HELD by a reasoned default-no** |

**Tally: 7 conclusively dead · 3 parked (named trigger) · 6 held (2 pending a decision nobody has asked for,
1 pending a $0 observation, 1 unclassified).** **None of the sixteen appears in the map's §2 register.**

---

### 5C-4 · The map's §3 E1 row reproduces the exact category error the scoreboard exists to prevent

**Map §3, last row:** `Interface-stability endpoint (E1) | three attempts: cooperativity calibrator, NR-V04
retrospective, SMARCA2/4 control | wrong sign · p = 0.393 · p = 0.747 | ⏸ parked — no pass`.
**Map §2b** repeats it: *"Three independent attempts, none passed."*

**STRATEGY.md's scoreboard box says the opposite, twice:**
> ⚠ **#1 AND #2 ARE DIFFERENT INSTRUMENTS** and neither invalidates the other's numbers: #1 is alchemical
> ternary FEP, #2 is endpoint-MD E1.

> ⚠ **DO NOT CONFLATE THIS WITH THE SENSITIVITY-CONTROL NULL BELOW.** They are different instruments with
> separate failed controls: this is **alchemical ternary FEP** (its calibrator is valB_mini, §2.11, wrong
> sign); that is **endpoint-MD E1** (its calibrator is the SMARCA2/4 panel, NULL). Neither result invalidates
> the other's numbers, and reading them as one finding would **overstate both**.

The "wrong sign" in the map's own E1 row **is valB_mini's**, which is not an E1 result. So the map attributes
**two instruments' failures to one instrument**, and files the combined object as ⏸ parked. Two consequences:
1. **The alchemical ternary FEP engine's failure is hidden** — absorbed into an E1 row (§5B-1).
2. **E1 is over-charged** with a failure that is not its own, which the scoreboard says *"would overstate both."*

The scoreboard's four-row table is the declared **one home for "which controls failed"**. The map should point
at it, not restate it.

---

### 5C-5 · The map quotes a value STRATEGY.md's Appendix A explicitly retired

**Map §4, row 1:** *"**A pocket exists** | **4 of 20** conformers of the experimental apo NMR ensemble
**8XTT** are cavity-bearing, no simulation bias applied"* — presented as current, with no supersession marker.

**Appendix A row 12:** *"8XTT: **4/20** conformers above D\* | The harmonized rerun (pinned fpocket +
score-independent matcher) reports **19/20 detected, 3 ≥ D\*** = 3/19 among detected, **3/20** across all
deposited."*

**The committed artifact** ([`nr4a3-pocket-reharmonize-summary.json`](../modalities/nr4a3-pocket-reharmonize-summary.json),
`8xtt_20conformers`) reads `n_propagated: 20, n_detected: 19, n_ge_dstar: 3`. **Neither denominator is 4.**
The paper handles it correctly (§ line 180–185 names 4/20 as the *original* and gives both harmonized
denominators); the map does not.

⚠ **`lint_consistency.py` passes with 0 ERRORs (run today) and cannot catch this.** The registered pattern is
`"4/20 (above|conformers)|placed \\*\\*4/20\\*\\*"` — the map writes it **spelled out** as "4 of 20
conformers", which the regex misses. This is CLAUDE.md rule 1.3's failure mode exactly: the old value was
registered, but in one surface form only.

**Fix (one line, $0):** add `4 of 20 conformers` to the `xtt_pre_harmonized` pattern in
[`pinned-figures.json`](pinned-figures.json), then correct the map's row from the artifact. *(Not done here —
this is a read-only inventory and other agents are editing the map.)*

---

### 5C-6 · The map's dead-end row for the ternary result and the ladder's agree — a positive check

The map's §2a *"The §2.5 ternary result — the molecule folded is unrecoverable, no bond-order record, entered
as an unlogged environment variable"* matches STRATEGY.md 500–505 exactly
(`nr4a-ternary-ligand-provenance.json`, no `_chem_comp_bond` loop in any of three models, `$PROTAC_SMILES`).
**Consistent. No action.**

---

### 5C-7 · Scope difference worth noting, not a contradiction

The map's §5 branch 1 says NR4A3 has **three** unique cysteines (C397, C420, C559); the ladder's TIER-0 entry
says **four** (adding **C166**, explicitly *"outside the LBD"*). The map's scope is the LBD ensemble (8XTT,
20 conformers). **Reconcilable, but the map should state the scope** so a reader does not read 3 vs 4 as a
disagreement.

---

### 5C-8 · The map's critical path omits the program's own flagship

The map's §6 critical path lists six items and closes with *"There is no row here waiting on a decision."*
Against the ladder:
- **`S` / 5a-KS — the flagship causal kill-switch, which landed today with a preregistered null — is not on
  the critical path and is not anywhere in the map.**
- **`valB_full` — behind a failed module-1 gate that decision 9 declined to amend — is not on it either**,
  and it is what blocks 5c and 5d, i.e. the entire flagship tail.
- Three of the map's own six items are, per §5C-3, waiting on a decision or on a $0 observation
  (the two-branch template; Arm F; the restrained binary re-run's pose diagnostic) — so **"there is no row
  here waiting on a decision" is true only because the rows that are waiting are not on the page.**

---

## 6 · Recommended merge order (not taken here)

Stated because the inventory's value is in what it makes safe, not in the inventory.

1. **Freeze the two numbering schemes first** — Appendix A row numbers and Open decision numbers. 65 external
   citations depend on them and **no CI check resolves either**.
2. **Fix the six stale plan markers (§5C-2) before merging, not during.** They are the item layer's ground
   truth and `work_ledger` reports them as owed work today.
3. **Add the missing RUNG 4b entry** (`selcal_sensitivity_control`) to the plan layer.
4. **Land the four requirement gaps (§5B) into the map before dissolving §9** — Val A's scope + Val C's
   absence, ΔG_open, the ABFE hold, and the ubiquitination-geometry node. These are over-claim risks that
   exist *today*, independent of the merge.
5. **Then** merge, keeping the three layers distinct and the two `Cum.` notations distinct (§2a).
6. **Last**, update `README.md`, `CLAUDE.md` and the `pinned-figures.json` targets in the same commit.

---

*Read-only inventory. No file other than this one was created or modified.*
