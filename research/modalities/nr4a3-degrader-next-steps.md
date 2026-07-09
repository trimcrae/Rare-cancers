# NR4A3 degrader — in-silico program state & how to run the warhead next (handoff)

**Single source of truth for resuming the degrader work from a fresh session.** Read this + the
manuscript ([`../manuscripts/nr4a3-degrader-paper.md`](../manuscripts/nr4a3-degrader-paper.md)) and the
pre-registration ([`nr4a3-druggability-prereg.md`](./nr4a3-druggability-prereg.md)) before launching
anything. Last updated 2026-06-26.

## TL;DR
Druggability case is a **feasibility result, stated honestly** (see the red-team:
[`../manuscripts/nr4a3-degrader-paper-redteam.md`](../manuscripts/nr4a3-degrader-paper-redteam.md)).
**Gate 0/0b** pass; **Gate 2** (opened-pocket druggable + handle-facing) passes; **Gate 1** is met only in
the weaker *basin-breathing* sense (F(Rg) is **monotonic — no separate opened minimum**, so not the
pre-registered "minimum/shoulder, not just biased excursions"); **Gate 3** (energetic accessibility) —
status **UPDATED 2026-06-29, now mixed/cautiously-positive after a corrected test:**
- The first release run seeded the **max-Rg frontier frame (0.984 nm, ~38 kcal/mol edge)** and it
  collapsed (frac-near-open 0.00). **But that was the wrong frame** (trimcrae's catch): the worst case,
  near-guaranteed to collapse.
- The **corrected** release run seeded the **low-energy DRUGGABLE frame (Rg 0.717, ~0.76 kcal/mol)** and it
  **did NOT collapse — it is metastable by Rg** (held 5 ns, frac-near-seed 1.00, mean |drift| 0.042 nm).
- **Druggability of that metastable state — RESOLVED 2026-06-29, POSITIVE (as a breathing/cryptic site):**
  mdpocket on the unbiased release trajectory gives `max 0.842, mean 0.262, frac≥0.5 = 0.24, frac≥0.53 = 0.20`
  (static 0.495) — druggable in **~24% of unbiased frames** (clears the pre-reg ≥5%@0.53 bar, with NO bias).
  So **Gate 3 is now cautiously PASSED as an induced-fit / conformational-selection target** (a dynamic
  pocket druggable ~¼ of the time), NOT a static always-open pocket. **Metastability CONFIRMED 3/3** (triplicate
  replicas all held 5 ns, mean |drift| 0.025 nm). Do **not** restate "Gate 3 FAILS" — the corrected
  (right-frame) test reversed it. The 0.931/0.751 opened-frame druggability is the
**orthosteric Pocket-5** metric (commensurate with the static 0.495) but is a **biased-MD-frame peak over
frames** — report it as the fraction of opened frames ≥ D\*=0.53 (≥5% pre-reg bar, met) with 0.931 as the
peak, and not as a like-for-like beat of the *static* drug-bound band. (fpocket itself is standard and the
§2.1 panel already anchors it, so no bespoke negative control is needed.) Gate-2 handle-facing **CONFIRMED**
2026-06-26 (run 28249776934): mean **5.0/7** pocket-facing; engageable set **five — L406, T410, I484, I531,
L534**; T407/R412 splay out. *Selectivity asymmetry:* engageable **divergent** handles are **5 vs NR4A1 but
only 4 vs NR4A2** (I531 conserved with NR4A2). The **warhead screen ran** (run 28252182123): NR4A3-favoured
chemotypes, top margin ~+1.7 kcal/mol (e.g. CHEMBL1873475), 4/5 engageable handles — but these margins are
**confounded triage** (opened NR4A3 vs *static* paralogues; see below).

**STRATEGY (2026-06-26, user-directed): build a family-wide selectivity matrix.** Run the *same* 30 ns
metad on **NR4A1 + NR4A2** → state-matched opened-pocket ensembles for all three → dock one library into
each → per-candidate **selectivity fingerprint** (NR4A3-only / pan-NR4A / anti-target NR4A1+NR4A3). This
is simultaneously the rigor fix (kills the opened-vs-static confound) and the scope expansion (programmable
selectivity). **STATUS (2026-06-28) — MATRIX COMPLETE.**
- **All three `*-metad` ensembles confirmed in S3** (`verify-aws.yml` run 28319715809, 2026-06-28):
  `nr4a3-metad` (640 MB), `nr4a1-metad` (732 MB), `nr4a2-metad` (711 MB) all `COMPLETE-SET: YES`;
  SageMaker jobs `nr4a1-metad-2026-06-27-11-44-08` + `nr4a2-metad-2026-06-27-22-00-03` both `Completed`.
  (The earlier NR4A1/NR4A2 truncations were the 8 h `MaxRuntime` incident; the 20 h-cap reruns completed.)
- **MATRIX — DONE.** `gpu-matrix-aws.yml` run 28319737517 (2026-06-28, ~25 min SageMaker docking,
  `Completed`) wrote `s3://<bucket>/nr4a3-matrix/nr4a3-matrix.json` (+ the three opened-conformer PDBs,
  docked SDFs, and `nr4a3-matrix.png` = Fig 4 heatmap). State-matched opened conformers docked: **NR4A3
  frame 300 (druggability 0.931), NR4A1 frame 524 (0.981), NR4A2 frame 125 (0.938)** — this kills the
  opened-vs-static confound that flagged the first warhead screen. Read the full ranked table any time via
  `report-matrix-aws.yml` (read-only S3 dump). **RESULT (13 deduped candidates, all contact 4/5 engageable
  handles):**
  - **NR4A3-selective lead (EMC/AciCC):** **cytosporone B** (= dup `CHEMBL1221517`) — dG_NR4A3 −7.08,
    margins **+1.42 vs NR4A1, +1.16 vs NR4A2** (only candidate clearing the strict ≥~1 kcal/mol-both bar).
    **amodiaquine** (= dup `CHEMBL682`) is the runner-up NR4A3-only cell (dG_NR4A3 −7.82, margins
    +1.31/+0.89 — sub-threshold on NR4A2 only, so NR4A3-leaning with better raw potency).
  - **pan-NR4A leads (ex-vivo immuno / triple degrader):** **celastrol** (−8.58, engages all three,
    margins +0.44/+0.96) and **`CHEMBL1873475`** (−8.40, margins ≈0/−0.40). These are the conserved-pocket
    design starting points for the distinct pan molecule.
  - **NR4A1+NR4A3 anti-target cell (AML-risk, design AWAY from): EMPTY (0)** — no candidate combines
    NR4A1+NR4A3 engagement while sparing NR4A2, so nothing to design away from here. Off-target leakage
    instead leans NR4A2 (`resveratrol` → NR4A1+NR4A2 cell; `CHEMBL475`/`CHEMBL196` → NR4A2-side).
  - **Census:** NR4A3-only 4, pan-NR4A 3, none 3, NR4A2+NR4A3 1, NR4A2-only 1, NR4A1+NR4A2 1, NR4A1+NR4A3 0.
- **NEXT ACTION:** the **MM-GBSA / FEP quantitative tier** (matrix step 2 below) — docking dG here is a
  triage prior, not affinity, so the margins nominate chemotypes, not a lead. **Flag the FEP cost before
  launching** (selectivity FEP on 1–3 leads × 3 paralogues is the expensive step; MM-GBSA endpoint rescoring
  is cheap and should go first). **Full result + robustness + FEP go/no-go memo:
  [`nr4a3-matrix-result.md`](./nr4a3-matrix-result.md).** Headline of the memo: matrix succeeds as the
  *framework* result (programmable selectivity; anti-target cell empty), but 6/9 calls are within docking
  noise and the top "NR4A3-selective" hit (cytosporone B) is a **known NR4A1 agonist** — so **FEP is
  recommended DEFERRED** behind (i) the unbiased release run confirming the pocket is metastable and (ii)
  MM-GBSA + de-novo *bona fide* selective candidates worth a multi-day alchemical run.

## 2026-07-06 SESSION — "better binder than 401?" + receptor-FRAME metastability screen (trimcrae, overnight)
**Prompt:** initial FEP returns make `denovo_401` look like a **poor absolute binder** (ΔG_bind(NR4A3) ≈ **−1.2
kcal/mol** per the preliminary n_iter=500 ABFE — selective by ΔΔG but essentially non-binding); trimcrae wants a
**much better binder queued for FEP, cheaply**, and asked (a) whether other pockets are an option and (b) whether
the weak binding is a **weak candidate vs a weak pocket**, flagging that the receptor frame should be the one that
**stays open (metastable), not just the highest fpocket-druggability one**.

### RESULT 1 — the FEP receptor frame was NOT mis-chosen (metastability ladder). Refutes the "lower-druggability-but-held-better" worry.
Seeded unbiased release MD (spot Training, `gpu-release-aws.yml`, 5 ns × 1 rep) at a **ladder of TARGET_RG**, then
scored each trajectory for **held-open ORTHOSTERIC druggability** (`gpu-mdpocket-aws.yml`, new `offsite_scan` added
to `nr4a3_mdpocket.py`). Rg-persistence: **all** frames (0.70–0.82) held on 5 ns (no collapse; drift 0.014–0.040 nm)
— the metastable basin is broad. Druggability-persistence (the discriminating metric):
| seed Rg | frac frames fpocket ≥0.5 | max | note |
|---------|--------------------------|-----|------|
| 0.70 | 0.20 | 0.905 | relaxes; orthosteric closes, AF-2/C-term opens |
| 0.72 | 0.12 | 0.86  | worst orthosteric |
| **0.74 (= the actual FEP frame, release primary 0.667)** | **0.48** | 0.874 | **PEAK — best-held druggable** |
| 0.82 | 0.40 | 0.962 | higher peak but druggable less often |
**The FEP frame (0.74) is the sweet spot** — stays orthosterically druggable ~48% of unbiased frames, MORE than
either lower (0.70/0.72) or higher (0.82). Going lower per the hypothesis makes it WORSE. **So denovo_401's −1.2 is
NOT a collapsing-/wrong-frame artifact; the receptor is the best-held druggable conformation available.** Even at
best the pocket is druggable only ~½ the time (mean fpocket ~0.34) → a genuine **conformational-selection / dynamic
pocket** (a binder pays an entropic cost to select the druggable state). Data: `nr4a3-metastab-rg0{70,72,74,82}` +
`*-pocket` prefixes. (0.76 rung failed on shared spot quota; not re-run — trend is monotone around the 0.74 peak.)

### RESULT 2 — OTHER pockets: only the AF-2/H12 surface, and it is a different modality.
Static fpocket (33 pockets; Pocket-5 dominates 0.495 vs next 0.196) + PocketMiner (only Pocket-5 enriched) already
said Pocket-5 is the sole cryptic site. The new **whole-surface offsite scan** on unbiased trajectories confirms one
secondary cavity: the **H12 / AF-2 coactivator region (UniProt ~598–624, traj resid ~226–248)**, transiently
druggable **~12–32%** of frames (peak 0.83–0.89), independent of the orthosteric pocket. It is a shallower, more
CONSERVED PPI surface (worse for paralogue selectivity) — a real but second-tier option, best pursued as a
molecular-glue/PPI modality, not a high-affinity orthosteric binder. In reserve, not the lead.

### RESULT 3 — bigger pocket-filling molecules did NOT out-bind 401 at docking, and trended pan-NR4A.
Generated 800 larger candidates (DiffSBDD, 28–40 heavy atoms vs 401's ~22; `nr4a3-denovo-affinity`), docked deep +
state-matched into the 0.74 release frame (`nr4a3-denovo-affinity-matrix`, 33 developable). Best dock dG_NR4A3 =
**−8.53** (denovo_657, pan-NR4A); the only strictly NR4A3-selective cells (denovo_661 −7.13, denovo_372 −7.12) are
weaker binders with narrow NR4A2 margins. **0 strict NR4A3-selective leads; 11 pan-NR4A** — filling the pocket
better engages the CONSERVED core → affinity-vs-selectivity tension. Multi-snapshot MM-GBSA on the top 8
(`nr4a3-denovo-affinity-mmgbsa-ms`, run 28770115405) vs 401's release-frame **−38.18** baseline (margin +12.83):
| candidate | mmΔG3 (NR4A3) | margin ± SD | verdict |
|-----------|---------------|-------------|---------|
| **denovo_401 (baseline)** | **−38.18** | **+12.83 ± 2.98** | (best-in-program) |
| denovo_560 | −21.51 | +5.55 ± 3.08 | confirmed_selective |
| denovo_318 | −20.29 | +1.64 ± 5.42 | confirmed_selective |
| denovo_372 | −18.28 | +1.01 ± 4.14 | confirmed_selective |
| denovo_657 | −30.73 | −5.69 | nonselective (strongest binder, not selective) |
| denovo_193 | −28.61 | −4.24 | nonselective |
**NO new candidate beats 401 on EITHER axis.** The selective ones bind much weaker (−18…−22 vs 401's −38); the
stronger binders (−29…−31) are non-selective. Since 401's MM-GBSA −38 already maps to FEP ≈ −1.2, these would FEP
even worse. **denovo_401 remains the strongest MM-GBSA binder found across the entire program.**

### ★★ SCAFFOLD LEAD-OPT BEATS 401 (2026-07-06, later) — a better candidate, found. Retracts the "weak pocket" call below.
**⚠ Reconcile with the converged 401 FEP (merged from main, same day):** the "401 is a poor binder" premise that
motivated this search was an **engine-calibration artifact** — the converged r1 ABFE + the +7.1 kcal/mol
under-binding engine offset (`nr4a3-abfe-calibration.json`, T4L·benzene zero) put 401 at a **favourable
~−4.5 kcal/mol** (offset-corrected), selective (ΔΔG −6.9/−5.5). So lo_m0_NCCO is a genuine **lead-optimization**
(tighter + still selective), not a rescue of a non-binder. The lead-opt result stands; only the framing shifts.
RBFE anchor updated accordingly (`rbfe_edges.ANCHOR_401_ABFE`).
The earlier conclusion was premature: it tested blind + bigger-molecule generation, but NOT the obvious med-chem
move — **keep 401's selective core, decorate it toward the divergent handles.** `nr4a3_leadopt.py` enumerated 163
scaffold-decorations of denovo_401 (phenyl-ring + terminal-arm R-groups; hydrophobic for L406/I484/L534, H-bonders
for T410), docked 133 developable ones **+ ref_401 as an in-run baseline** into the 0.74 release frame
(`nr4a3-leadopt-matrix`, dock run 28785469610), then multi-snapshot MM-GBSA on the top 12 (`nr4a3-leadopt-mmgbsa-ms`,
run 28790844819). **THREE variants beat ref_401 on BOTH absolute affinity AND selectivity margin, and held under
de-noising** (ref_401 in-run baseline: margin **+13.22 ± 4.09**, ΔG3 **−35.44**):
| variant | decoration (on 401's phenyl) | margin ± SD | ΔG3 | SMILES |
|---------|------------------------------|-------------|-----|--------|
| **lo_m0_NCCO** | ortho-acetamido (NHAc) | **+16.92 ± 4.51** | **−40.96** | `COC[C@H](c1ccccc1NC(C)=O)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1` |
| **lo_m0_CC** | ortho-ethyl | **+17.78 ± 4.47** | **−40.78** | `CCc1ccccc1[C@@H](COC)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1` |
| **lo_m0_SNOO** | ortho-sulfonamide (SO₂NH₂) | **+15.18 ± 3.84** | **−40.42** | `COC[C@H](c1ccccc1S(N)(=O)=O)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1` |
| ref_401 | (baseline) | +13.22 ± 4.09 | −35.44 | (denovo_401) |
All three are **clean** (no structural alerts, QED 0.71–0.72, SA 3.99–4.13, MW 332–384), **confirmed_selective**,
**margin − SD ≈ +11 to +13 > 0**, and **clear the release-frame multi-snapshot decoy null decisively** (95th +6.69,
max +7.10 — all ≥ +15). ΔG3 ≈ −41 vs 401's −35 = **~+5.5 kcal/mol tighter MM-GBSA binding, selectivity improved too.**
(lo_m1_CFFF — *meta*-CF3 — REVERSED, binding paralogues far tighter: position matters; ortho decoration is the win.)
- **LEAD = `lo_m0_NCCO`** (401 + ortho-acetamido, "401-NHAc"): strongest ΔG3 (−40.96) AND developable H-bond
  donor/acceptor. `lo_m0_CC` (ethyl; best margin) + `lo_m0_SNOO` (sulfonamide) are the sibling set.
- **HONEST WEIGHT:** MM-GBSA magnitude is inflated (401's −35 MM-GBSA ↔ FEP −1.2), so these are NOT proven strong
  *absolute* binders — but they beat 401 by **the same cheap tier that ranks 401, plus the decoy null**, which is
  exactly the pre-FEP nomination bar. The improvement is *relative* and *specificity-controlled*; FEP is the arbiter.
- **BONUS for FEP:** the winners are a **congeneric series** off one scaffold (H → ethyl/acetamido/sulfonamide at the
  ortho position), so this is ideal for **relative FEP (RBFE)** — cheaper and more accurate than the single-ligand
  ABFE 401 required. **New FEP subject: `lo_m0_NCCO` (+ the ethyl/sulfonamide siblings), staged for FEP (gated).**
Reproduce: `report-matrix-aws output_prefix=nr4a3-leadopt-matrix`; `report-mmgbsa-aws output_prefix=nr4a3-leadopt-mmgbsa-ms`.

### ⚠️ SUPERSEDED CONCLUSION (2026-07-06, earlier) — read as "weak pocket"; the scaffold lead-opt ABOVE refuted it.
_Kept for honesty. The reasoning was sound for what it tested (frame optimal; blind + bigger-molecule generation
doesn't beat 401) but it stopped one idea short of the 401-scaffold lead-opt, which then beat 401 cleanly._
Three independent cheap-tier results converge: **(1)** the receptor frame is optimal (0.74 is the best-held
druggable conformation; not a collapse/wrong-frame artifact); **(2)** 401 is already the strongest binder the whole
campaign has produced, and a fresh 800-molecule pocket-filling generation could not beat it (bigger → weaker and/or
non-selective); **(3)** the pocket is druggable only ~½ the time even at its best frame (conformational-selection).
So the orthosteric cryptic pocket **caps achievable selective small-molecule affinity** — 401 (FEP ≈ −1.2) is near
the ceiling for a *selective* orthosteric binder, and more binder-optimization here has negative expected return.
**Strategic implication (already the paper's architecture, now empirically reinforced):** stop trying to source the
affinity/selectivity from the orthosteric binder alone; source it from the **ternary/degrader machinery**
(cooperativity × the divergent CRBN-interface patch mapped in §2.7) and/or the **ASO** (fusion-level). The
**AF-2/H12 surface** (Result 2) is a possible PPI/molecular-glue alternative but is conserved (selectivity-poor).
**Recommendation: do NOT spend the selectivity FEP on a *new* orthosteric binder** — there isn't a better one; if
FEP budget is spent, spend it confirming 401 or on the ternary geometry, not on chasing an orthosteric win the
cheap tiers say isn't there. **No FEP/metad launched this session; all runs cheap-tier (<$10 each).**

## ✅ denovo_401 SURVIVES MULTI-SNAPSHOT (2026-06-30) — first FEP-worthy selective lead
Ran the multi-snapshot de-noising tier on `denovo_401` (run 28469414513, report 28470289876, `nr4a3-denovo-mmgbsa-v2-ms`):
| candidate | single-snapshot | **multi-snapshot mean ± SD** | NR4A3 ΔG | NR4A1 ΔG | NR4A2 ΔG | margin − SD | verdict |
|-----------|-----------------|------------------------------|----------|----------|----------|-------------|---------|
| **denovo_401** | +13.92 | **+12.83 ± 2.98** | **−38.18** | −22.98 | −25.35 | **+9.85** | **confirmed_selective** |
**This is the breakthrough.** Where denovo_393 *collapsed* under the identical tier (+18.34 → −2.95 ± 3.65),
denovo_401 *holds*: the multi-snapshot margin (+12.83) is barely below its single-snapshot value, the SD (2.98)
is small (vs the 4–6 that buried 393/780), and **margin − SD = +9.85 ≫ 0** — the FEP-worthy bar is cleanly met.
NR4A3 binding is strong and favorable (−38.18 kcal/mol) with both paralogues ~13–15 kcal/mol weaker. So the
de-noising tier is *discriminating*, not destroying: it killed a noise artifact (393) and confirmed a real
lead (401). **denovo_401 is the first candidate queued for FEP** (do NOT launch yet per trimcrae). SMILES
`COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1` (MW 304, QED 0.80, SA 3.87, clean — no structural
alerts). Next: keep the multi-snapshot screen running over the remaining v3deep pool to find siblings, and
scaffold-seed lead-opt around denovo_401's chemotype.

## ✅ MATCHING CONTROLS RUN (2026-06-30, red-team follow-up) — denovo_401 clears a like-for-like multi-snapshot decoy null
Two controls the paper had flagged as pending (caveat 7 / §2.6) were run and folded into the paper + prereg:
- **Multi-snapshot decoy null** (`mmgbsa-aws.yml` multisnapshot=1 on `nr4a3-decoy-matrix`, run **28473680997**
  → `nr4a3-decoy-mmgbsa-ms`; read via `report-mmgbsa-aws.yml output_prefix=nr4a3-decoy-mmgbsa-ms`). All 38
  decoys re-scored multi-snapshot collapse to **mean −3.47, 95th +6.69, max +7.10, confirmed_selective 11/38
  (29 %)** (vs single-snapshot +13.1 / +16.46 / 39 %). **denovo_401 (+12.83 ± 2.98, margin−SD +9.85) clears the
  whole null** — first like-for-like specificity-controlled hit.
- **Fully state-matched re-dock** (`gpu-denovo-dock-aws.yml receptor_mode=metad top_n=60 denovo_prefix=nr4a3-denovo-v2`,
  dock run **28473682532** → `nr4a3-denovo-matrix-v2-statematch`; rescore `mmgbsa-aws.yml multisnapshot=1
  candidate_filter=denovo_401,denovo_111`, run **28480041030** → `nr4a3-denovo-mmgbsa-v2-statematch`). With NR4A3
  in its metad-opened frame, **denovo_401 stays selective but weaker: +7.44 ± 4.18** (ΔG3 −32.37 / ΔG1 −24.93 /
  ΔG2 −22.80) → **direction robust, magnitude frame-dependent.** (denovo_111 is a dev-set candidate, not in the
  v2 pool, so it was not in the state-matched poses — not rescored here.)
- **⚠️ Metad-frame decoy null — RUN 2026-07-01 (run 28483612927 → `nr4a3-decoy-mmgbsa-metad-ms`), PARTIAL
  NEGATIVE.** The matched control for the +7.44 state-matched margin is done, and it flips the verdict: in the
  biased metad-opened frame the decoy null **balloons** (mean +1.59, **95th +17.70, max +24.74**; top decoys
  diphenhydramine +24.74, lidocaine +22.08) and **`denovo_401`'s +7.44 does NOT clear it** (~84th pct; 6/38
  decoys higher). So the metad-opened frame is a **poor, promiscuous discriminator**, and denovo_401's
  specificity-controlled result is **release-frame-specific**, not universal — a real but **receptor-frame-
  dependent** hit (clears the release-frame null +12.83 vs +6.69/+7.10; fails the metad-frame null). Folded into
  paper abstract/§2.6/§5-caveat-7/§6-Gate-4 + prereg. **Right resolution = ensemble scoring over the druggable
  release sub-ensemble (not one frame)** — **now a PRE-PREPRINT task** (regime updated 2026-07-01: paper must be
  as strong as in-silico allows before posting), being run in the red-team-mitigation program below.
- **Remaining gates:** selectivity FEP (the one quantitative tier left; frame-dependence best fixed by ensemble
  scoring first) — **no longer skipped** (regime updated 2026-07-01).

## 🔴 RED-TEAM MITIGATION PROGRAM (2026-07-01, trimcrae authorized autonomous GPU) — IN PROGRESS
**★ North star (trimcrae 2026-07-01):** produce **the state of the art of what in-silico testing can do for an
NR4A3-selective degrader.** Every warranted run below serves that; the preprint documents the SOTA in-silico case.
**Authorization:** trimcrae, 2026-07-01: *"Do the GPU runs that are warranted to strengthen the claims. Merge
to main as you go. Dont come back to me until all your red team findings are mitigated."* This is a **task-scoped
override of the "GPU runs cost money — ASK FIRST" standing rule** — for this program, dispatch the warranted GPU
jobs without a per-job AskUserQuestion. (The ASK-FIRST rule still applies to *future* unrelated work.) The regime
was also updated (no GPU-$ ceiling gating paper quality; FEP no longer skipped; preprint waits on this work).
**💸 STANDING AUTHORIZATION (trimcrae 2026-07-01): any single GPU run under **$10** may be launched WITHOUT
asking.** ("You don't need to ask me for permission to run an <$10 run.") So the ASK-FIRST standing rule now
only applies to runs ≥ $10 (e.g. metad ~$15, or the full FEP fleet) and to the FEP carve-out below. Cheap
Processing/MM-GBSA/dock jobs: just run them and report.
**⛔ FEP CARVE-OUT (trimcrae 2026-07-01): do NOT start any FEP job without checking with the user first** — they
expect GPU-setup changes are needed for it. This is the ONE exception to the autonomous-GPU authorization above.
FEP is "no longer skipped" (it's the SOTA gate) but it is **gated on an explicit user go-ahead**, not auto-dispatched.
**FEP HARNESS BUILT (2026-07-01, spot + parallel + early-stop; NOT yet run) — the GPU-setup change trimcrae asked
for.** Full design: [`nr4a3-fep-plan.md`](./nr4a3-fep-plan.md). Spot Training jobs (Processing can't do spot),
fanned out one per (receptor×leg×λ-window) shard, continuous-checkpoint spot resume, **pilot-first two-pass +
central early-stop monitor** that `StopTrainingJob`s the whole fleet if the pilot ΔΔG is confidently
non-selective or non-converging. Files: `fep_sharding.py`+`fep_decision.py` (pure, 16 tests), `nr4a3_fep.py`,
`sagemaker_src/entry_fep.py`, `nr4a3_fep_sagemaker.py`, `report_fep.py`, `fep_monitor.py`,
`.github/workflows/gpu-fep-aws.yml` (modes: plan/smoke/run/monitor/reduce; **default plan = dry-run, no spend**).
**Two things still needed before a real run:** (a) trimcrae go-ahead for `mode=run`; (b) a Service-Quotas
increase for *"ml.g5.xlarge for spot training job usage"* (sets the parallel width). `mode=smoke` validates the
spot+checkpoint path cheaply and probes that quota. The real compute protocol (openmmtools alchemy) is
first-pass and needs a shakeout run before its numbers are trusted (like every prior pipeline here).
Fourth-pass red-team findings (F16–F20; see the red-team memo) and their GPU mitigations:
- **F16 (HIGH)** decoy null doesn't control the generative step / best-of-N → ensemble scoring over the release
  sub-ensemble + a generation-matched decoy null (and, ultimately, FEP).
- **F17 (med-high)** winner's-curse on the best-of-~10 survivor → ensemble/multi-frame de-biasing + independent re-run.
- **F18 (med)** ternary "positive control" is in-distribution (CRBN/IMiD) → run the actual denovo_401-PROTAC
  degradation-geometry prediction across NR4A1/2/3.
- **F19 (med)** denovo_111 never multi-snapshot-tested → dock + multi-snapshot it (both leads on one footing).
- **F20 (low)** abstract editing/bloat → editorial (no GPU).
Progress is logged inline below as each job lands; results folded into paper/preprint/red-team + merged to main.

**✅ F19 DONE (2026-07-01, run 28516596503 → `nr4a3-denovo-mmgbsa-dev-ms111`, report 28517438970).**
denovo_111 multi-snapshot MM-GBSA (release frame, 10-frame GB-MD avg): **+14.60 ± 4.10** (ΔG3 −34.02,
ΔG1 −18.30, ΔG2 −19.42), **confirmed_selective, margin − SD = +10.50 > 0.** So denovo_111 **also survives
de-noising** and clears the release-frame multi-snapshot decoy null (95th +6.69, max +7.10) — a **SECOND**
de-noised, decoy-null-clearing foothold alongside denovo_401 (+12.83 ± 2.98, margin − SD +9.85). Resolves F19
and *strengthens* the paper: "sole survivor / n=1 of ~10" becomes **n=2** at the release-frame multi-snapshot
tier. Caveats preserved: denovo_111 SD (4.10) is larger (noisier); both are release/design-frame results (F16
still applies to both); denovo_111 not yet state-matched (metad-frame) re-docked, so its frame-dependence is
uncharacterized (unlike denovo_401).

**✅ F18 DONE (2026-07-01, run 28517419306 → `nr4a3-ternary`, report run 28518979909).** denovo_401-PROTAC
(RDKit-validated, C41H56N4O8, MW 733) ternary across NR4A3/NR4A1/NR4A2 LBD + CRBN, Boltz-2 `--no_kernels`.
- **Control reproduced:** CRBN+lenalidomide SEATED in tri-Trp (2.85 Å W380, ligand-iPTM 0.99).
- **NR4A ternaries — all three form a productive-geometry-proxy complex, NOT NR4A3-selective:**
  | target | iptm | ligand_iptm | bridges | closest Lys→CRBN | Lys ≤8/12/16 Å |
  |--------|------|-------------|---------|------------------|-----------------|
  | NR4A3 | 0.720 | 0.930 | yes (3.06/2.77) | K195 @ 3.12 Å | 2/5/10 |
  | NR4A1 | 0.829 | 0.951 | yes (2.91/2.45) | K53 @ 2.34 Å | 4/6/7 |
  | NR4A2 | 0.820 | 0.961 | yes (3.05/2.51) | K175 @ 3.96 Å | 4/5/5 |
- **Honest reading (mitigates F18 + corrects §2.7):** we ran the *actual* NR4A ternary prediction (not just the
  in-distribution control). Result: for this representative PROTAC the ternary forms productively for **all three**
  paralogues with comparable (within-Boltz-noise) confidence — **no NR4A3 ternary-selectivity signal**. So §2.7's
  hope that "the ternary can *multiply* the binder's NR4A3 margin (the highest-value un-run experiment)" is **not
  borne out for this linker**: degradation selectivity would have to come from the **binder** margin
  (denovo_401/111), with **linker/exit-vector design** the (untested) lever to try to add ternary selectivity.
- **Caveats:** the PROTAC linker/exit-vector is REPRESENTATIVE (one arbitrary choice); Boltz gives a single
  ternary pose (not the productive-ensemble/cooperativity α that sets real degradation selectivity); the
  Lys-proximity is a CRBN-only proxy (no full CRL4^CRBN + E2~Ub). So "no ternary selectivity" is a
  single-pose, single-linker in-silico result, not definitive — but it replaces an untested hopeful assumption
  with a computed one.

**✅ F17 DONE (2026-07-01, run 28518978321 → `nr4a3-denovo-mmgbsa-v2-ms-rep2`, report 28519893316).**
Independent-seed multi-snapshot replicate of `denovo_401` (the MD is unseeded, so a re-run is a genuinely
independent estimate): **+14.75 ± 4.82** (ΔG3 −37.50 / ΔG1 −22.75 / ΔG2 −20.43), confirmed_selective — vs the
original +12.83 ± 2.98. The margin **reproduces (slightly higher) under an independent trajectory → not a
single-draw artifact**, bounding the winner's-curse (within-candidate/seed) concern. Between-candidate best-of-N
selection remains a bounded caveat (only re-selection-from-scratch or FEP fully removes it). Folded into §2.6.

**✅ TERNARY-INTERFACE DIVERGENCE (2026-07-01, report run 28520559139; `report_ternary.py` interface mode).**
Follow-up to trimcrae's "is it not advantageous to have both binder AND ternary selective?" — computed on the
F18 structures (read-only, no GPU). **NR4A3–CRBN interface = 33 residues; 8 divergent vs NR4A1, 8 vs NR4A2, 6 vs
both (E545/T563/Q570/S571/L576/E580/V588…); ZERO of the 7 pocket handles are at the interface.** So ternary
selectivity is **structurally AVAILABLE** (a divergent patch a linker could target) on a surface **independent**
of the binder's pocket handles → binder × ternary is a genuine multiplicative budget, not double-counting. The
representative linker didn't *realize* it (F18), and single-pose Boltz can flag availability but can't
optimize/validate ternary selectivity (needs a ternary-ensemble/cooperativity method — method-watch). Closes
the §2.7 "surface/PPI proxy" caveat (real interface now mapped). Folded into paper §2.7 table + preprint §2.7.

**✅ PRE-FEP SPECIES RESOLUTION DONE (2026-07-01, dock 28538579322 → MM-GBSA single 28540078644 / multi
28542048560; species set = `fep_species.py`).** Docked+scored denovo_401's 16 stereoisomers + denovo_111
neutral/cation to pick the correct 3D species BEFORE spending on FEP.
- **denovo_401 stereochemistry — RESOLVED; the chemotype is stereochemistry-robust.** Nearly all 16
  diastereomers were confirmed_selective (single-snapshot); de-noised top four: **iso08 +11.36 ± 5.25**
  (C13-epimer, nominal best), **gen +9.54 ± 4.26** (the DiffSBDD-generated isomer all prior denovo_401 work used
  → those results stand on a near-optimal isomer), iso14 +8.56, iso00 +6.75. iso08 vs gen overlap within SD →
  **FEP subjects = denovo_401 iso08 + gen** (FEP resolves the epimer at affinity grade). iso08 SMILES
  `COC[C@H](c1ccccc1)[C@@H]1CC[C@@H](CC(C)(C)[C@@H](C)O)C1`.
- **denovo_111 — DEMOTED (protonation-fragile).** Neutral form selective (single-snapshot +8.76) but the
  **cation (physiological pH 7.4) REVERSES**: multi-snapshot **−15.01 ± 5.14**, binding NR4A1 *tighter* than
  NR4A3 (−36.81 vs −21.80). Its selectivity was a neutral-form artifact → **not an FEP candidate**; denovo_401
  is the sole robust lead. The F19 "two footholds" claim is corrected in paper §2.6/abstract + preprint.

**🎯 PROGRAM COMPLETE (2026-07-01):** all fourth-pass red-team findings mitigated — F16 (narrowed + empirically
bounded), F17 (replicate reproduces), F18 (ternary run: productive-not-selective, but interface divergent →
ternary selectivity engineerable), F19 (denovo_111 later demoted — protonation-fragile; denovo_401 sole robust
lead, stereochemistry-resolved), F20 (typo + factually current). **FEP is the one
remaining SOTA tier — GATED on trimcrae go-ahead (GPU-setup change expected); do NOT auto-start.**
Representative PROTAC SMILES (for any ternary follow-up):
`COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)OCCOCCNC(=O)CCC(=O)Nc2ccc3c(c2)CN(C4CCC(=O)NC4=O)C3=O)C1`.

- **Ternary control — 3 infra walls hit 2026-07-01; all fixed at the code level, but the re-run is DEFERRED
  (not on the preprint critical path).** The CRBN+lenalidomide Boltz-2 control never validated. Failures, in order:
  1. **Empty `ContainerArguments`** (control mode passed `[]`) → SageMaker `ParamValidationError` (run 28488228214,
     $0). Fixed: `--control` sentinel in `nr4a3_ternary_sagemaker.py` + `boltz_src/entry.py`.
  2. **`ml.g5.2xlarge` quota = 0 instances** → `ResourceLimitExceeded` (run 28488478427, $0). Fixed: default
     instance flipped to **`ml.g5.xlarge`** (account has quota; ran fine in 16 GB RAM) in the workflow + submitter.
  3. **`ModuleNotFoundError: cuequivariance_torch`** — boltz>=2 hard-crashes in its triangular-mult kernel without
     the cuEquivariance accel stack (run 28488554878; job reported false-green because entry.py didn't propagate
     the non-zero exit). Fixed: add `cuequivariance-torch` + `cuequivariance-ops-torch-cu12` to the Boltz install
     (requirements.txt + entry.py), and **entry.py now `raise SystemExit(r.returncode)`** so a Boltz crash fails
     loud, not false-green. **NOTE: may need further Boltz env shakeout** (this is a 2023-era-style dep cascade,
     cf. the DiffSBDD 6-run shakeout) — the deps are a best-effort fix, not verified end-to-end.
  4. **`cuequivariance_ops_torch` kernel ImportError** — even with the dep installed, boltz>=2 crashed when it
     *called* the accel kernel (CUDA-ops build mismatch on the A10G), AND `nr4a3_ternary.py` swallowed the failure
     and exited 0 (recorded `control_run: 1` but returned green). Fixed: **`boltz predict --no_kernels`**
     (pure-PyTorch triangle path — sidesteps the whole cuequivariance chain) + `nr4a3_ternary.py` now
     `sys.exit` non-zero on a boltz failure (no more false-green at the script level).
  **✅ CONTROL VALIDATED (2026-07-01, run 28513626068).** With `--no_kernels`, Boltz-2 ran clean (`control_run: 0`,
  "Number of failed examples: 0", ~11 min). Read via **`report-ternary-aws.yml`** (new read-only reporter:
  `report_ternary.py`, boto3+gemmi — Boltz confidence + a ligand↔tri-Trp geometry check). **Result: Boltz-2 seats
  lenalidomide's glutarimide in CRBN's tri-Trp pocket** — closest heavy-atom approach **2.85 Å to W380** (3.39 Å
  W386, 3.47 Å W400; 3/3 within 8 Å), **ligand-iPTM 0.99** / confidence 0.87. Recovers the known IMiD binding
  mode → the ternary pipeline is **trustworthy** for the NR4A3 degradation-geometry question. Folded into paper
  §2.4 + preprint §2.7/Limitations. **STILL AHEAD (Stage 2, the real result):** the NR4A3–PROTAC–E3 degradation-
  geometry prediction needs a warhead **PROTAC** (denovo_401 + linker + CRBN/VHL ligand) — future work, dispatch
  `gpu-ternary-aws.yml` with `protac_smiles=...` once built. Defaults are now correct (g5.xlarge, --no_kernels).

**v3deep-ms2 batch (run 28470643031, 6 candidates) — ZERO further survivors; denovo_401 stands alone.**
Multi-snapshot on denovo_921/277/804/431/838/924(neg ctrl): best is denovo_921 +4.22±5.23 (margin−SD=−1.01),
then denovo_277 +2.23±3.52 (−1.29) — both "confirmed_selective" by sign but **neither survives de-noising**;
804/431/838 weakened/nonselective; neg control denovo_924 −20.78 (stays nonselective ✓, method discriminating).
So across ~10 candidates now multi-snapshot-tested, **denovo_401 (margin−SD=+9.85) is the SOLE survivor** —
an honest, sobering count: the funnel does NOT reliably produce de-noising survivors. Reinforces the paper's
"n=1 of ~10" caveat (§2.6) and the architecture conclusion that binder selectivity is the fragile place to
source it (§2.7). No new GPU jobs dispatched (trimcrae stopping for a fresh red-team before FEP).

## ⚠️ MULTI-SNAPSHOT CONFIRMATION REFUTES denovo_393 (2026-06-30) — single-snapshot harvest is noise
Built the multi-snapshot de-noising tier (`endpoint_dG_multisnapshot`: minimize → short GB Langevin MD → ΔG
averaged over 10 frames + SD) and ran it on the lead set (run 28467383090, `nr4a3-denovo-mmgbsa-v3deep-ms`):
| candidate | single-snapshot | **multi-snapshot mean ± SD** | verdict |
|-----------|-----------------|------------------------------|---------|
| denovo_393 (was BEST, above decoy max) | +18.34 | **−2.95 ± 3.65** | **reversed** (selectivity gone) |
| denovo_780 | +14.66 | +2.07 ± 6.36 | within noise of 0 |
| denovo_924 (neg control) | −19.41 | −25.20 ± 4.55 | stays nonselective ✓ (method works) |
**The single-snapshot MM-GBSA selectivity margins have SD ~4–6 kcal/mol — LARGER than the margins — so the
"above-null" harvest (decoy bar was also single-snapshot) is dominated by noise.** denovo_393's +18.34 was an
extreme-value artifact; de-noised it is ~0/slightly paralogue-favoring. The negative control behaving correctly
makes this a TRUSTWORTHY refutation, not a method failure. **This $1.50 step avoided a ~$300 inconclusive FEP.**
Checking denovo_401 (+denovo_94) under multi-snapshot next (run 28469110227, `-v2-ms`); given the strongest
lead collapsed, expect the others to as well. **Implication: single-snapshot scoring cannot find a real
selective lead here; a genuine candidate needs multi-snapshot (or FEP) scoring IN THE SELECTION LOOP, not just
at the end — which is far costlier per candidate. Strategic decision pending trimcrae (do NOT publish a null;
options: multi-snapshot-in-the-loop lead-opt around a scaffold; revisit whether the cryptic pocket can support
selective small-molecule binding at all; or shift weight to the degrader's other legs / ASO).**

## Selectivity architecture — binder vs ternary (2026-06-30 analysis)
Full rigorous treatment: **[../manuscripts/nr4a3-degrader-selectivity-architecture.md](../manuscripts/nr4a3-degrader-selectivity-architecture.md)**.
Key computed result that reframes the campaign: the **orthosteric cryptic pocket is a selectivity HOTSPOT**
(7/10 warhead-contact residues divergent = 70%, vs 43% for the rest of the LBD; 60% vs 28% on the
"differs from BOTH paralogues" criterion). So the binder's problem was never handle scarcity — it is
pocket druggability + affinity-margin-robustness. Strategic conclusions: (1) selectivity is a
*multiplicative budget* across binding × ternary × kinetics — the binder need not carry it alone;
(2) **fusion-vs-WT is unobtainable from the degrader at any stage** → that is the ASO's job, accept WT loss;
(3) source **paralogue selectivity from the TERNARY** (run the primed `nr4a3_ternary.py` across NR4A1/2/3 —
highest-value un-run experiment), and **NR4A2 safety from PK/CNS-exclusion** (I531 is NR4A3=NR4A2-identical,
so NR4A2 is the hardest molecular case but the tox is CNS-localized); (4) pan-NR4A is ex-vivo-CAR-T-only,
off-table for systemic EMC. denovo_401's pocket selectivity is a *bonus* that relaxes the ternary's burden,
not the gate.

## Red-team Tier-1/2/3 in-silico execution — state (2026-06-29, async; resume here)
Strengthening the de-novo case (red-team). All code merged to `main`. Several SageMaker jobs are async; the
dependent steps below must be dispatched as each upstream job lands (verify via S3 / the run conclusion).
- **Tier 1 #1 (developability gate) — DONE.** Gate built (`structural_alerts.py`: BRENK + curated SMARTS +
  aromatic + SA≤4.5), wired into funnel/selector/report. **Result: 11/191 generations clean, 9 with ≥4
  handles, NONE currently NR4A3-selective** (denovo_57 clean+confirmed_selective but dock cell "none").
  Developable-only **release** dock **succeeded** → `s3://<bucket>/nr4a3-denovo-matrix-dev`. **MM-GBSA
  dispatched** → `nr4a3-denovo-mmgbsa-dev` (read with `report-mmgbsa-aws.yml input=nr4a3-denovo-mmgbsa-dev`).
- **Tier 1 #2 (decoy/specificity control) — DONE + DECISIVE NEGATIVE (2026-06-30).** `decoy_library.py` (38
  non-NR4A drugs) docked → `nr4a3-decoy-matrix`, MM-GBSA → `nr4a3-decoy-mmgbsa` (run 28414348202, needed
  `compute_timeout=7200` for 38×3 legs). **RESULT: the single-snapshot MM-GBSA "NR4A3-selective" verdict is
  NON-SPECIFIC.** Decoy null `confirmed_selective` **15/38 = 39 %** (~58 % positive NR4A3 margin), incl.
  caffeine/ibuprofen/lidocaine/phenytoin; developability-gated de-novo set (`nr4a3-denovo-mmgbsa-dev`)
  `confirmed_selective` **2/11 = 18 %** (denovo_111, denovo_67) — **below the decoy baseline, NOT enriched.**
  → The MM-GBSA selectivity tier as run **cannot support a selectivity claim** (it labels ~40–58 % of any
  drug-like matter selective; explains why artifact denovo_15 scored "selective"). Paper §2.5/abstract/§6 Gate
  4 + red-team F15 updated to retract "MM-GBSA-confirmed selective". **The fix = Tier 3 #6 multi-snapshot /
  ensemble MM-GBSA (or FEP) that must BEAT the decoy null — now necessary, not optional; keep the decoy set as
  a standing specificity gate.** (Single-snapshot MM-GBSA on the small clean de-novo/decoy sets is cheap, but
  multi-snapshot is the real tier.)
- **Tier 1 #3 (state-matched re-dock) — DONE + reinforces the negative (2026-06-30).** `receptor_mode=metad`
  (NR4A3 in its metad-opened conformer). First run failed on a `NR4A3_RECEPTOR` KeyError (fixed, env.get),
  re-dispatched → `nr4a3-denovo-matrix-statematch`, MM-GBSA → `nr4a3-denovo-mmgbsa-statematch` (run 28416206108,
  success). **RESULT: the MM-GBSA "selective" set is NOT robust to receptor-frame choice.** Release-frame dev
  confirmed_selective = {denovo_111, denovo_67}; state-matched confirmed_selective = {denovo_111, denovo_170,
  denovo_0} (+denovo_67 rescued). **Only denovo_111 is NR4A3-favoured in BOTH states** — the rest flip. Layered
  on the decoy non-specificity (#2), this confirms the single-snapshot verdict is unstable + non-specific; even
  denovo_111 is not above the ~39–58 % decoy null. Reinforces: a controlled multi-snapshot/FEP tier is required.
- **Tier 2 #4 (re-generate with the filter in-loop) — RUNNING.** `gpu-denovo-aws.yml n_samples=500
  output_prefix=nr4a3-denovo-v2` (the funnel now demotes non-developable, so clean candidates rank top).
  **NEXT once it lands: dock `gpu-denovo-dock-aws.yml denovo_prefix=nr4a3-denovo-v2 developable_only=1
  output_prefix=nr4a3-denovo-matrix-v2` → MM-GBSA → `nr4a3-denovo-mmgbsa-v2`**; goal = a clean AND
  NR4A3-selective hit (the existing pool had none). Re-screen with `report-denovo-aws.yml denovo_prefix=nr4a3-denovo-v2`.
- **Tier 3 #6/#7 — READY FOLLOW-UPS (gated on a clean selective lead).** #7 ensemble docking over the druggable
  release sub-ensemble (primary+alt1+alt3 from `nr4a3-release-druggable`) instead of one frame — a receptor-set
  change in `nr4a3_matrix.py::_use_release_receptor`. #6 multi-snapshot / MD-relaxed MM-GBSA + per-residue
  decomposition + error bars (the documented MM-GBSA follow-up) — apply to whichever candidate survives Tier 2.
  Both are best run on a real lead; neither is built yet.

## PATH FORWARD to a real candidate (2026-06-30, trimcrae: do NOT publish a null; keep pushing; no FEP yet)
The decoy control is a **calibrated yardstick**, not a stop sign. Decoy null (n=38): mean 1.26, sd 6.25, 90th
9.74, **95th 13.12**, max 16.46 (`selectivity_calibration.py`, unit-tested). Against the 95th-pct bar
**`denovo_111` (+15.7) is the ONE candidate that clears the null** (clean fluoro-phenyl-pyrrolidine, QED 0.87 /
SA 2.9, favoured in both receptor states; 1/38 decoys above it). That is the foothold. Plan:
1. **Mine v2 — DONE (2026-06-30). TWO above-null leads now.** v2 MM-GBSA (run 28437077111) done; ranked dev +
   v2 vs the decoy bar (+13.1). **Above-null set (clean + margin > +13.1):**
   - **`denovo_401`** (v2) `COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1` — margin **+13.92**, **dock
     cell NR4A3-only** (selective at BOTH tiers), QED 0.80 / SA 3.87 / MW 304, CLEAN. The strongest foothold.
   - **`denovo_111`** (dev) `CC[C@H](C)c1cc(OCCO)cc(N2CCCC2)c1F` — margin **+15.70** (MM-GBSA, both receptor
     states), QED 0.87 / SA 2.9 / MW 281, CLEAN.
   (Other v2 confirmed_selective — denovo_65 +9.79, denovo_297 +7.63, denovo_269 +2.55 — are below the decoy
   bar; not above-null.) So blind generation yields ~1 above-null hit per ~500 gens → brute-force scales but
   the higher-value move is lead-opt around these two (step 2).
2. **Lead-opt around denovo_111 (+ any v2 above-null hits).** Scaffold-seeded generation (keep the
   fluoro-phenyl-pyrrolidine core, vary substituents) conditioned hard on the FOUR both-paralogue divergent
   handles (L406/T410/I484/L534 — the physical basis of selectivity), heavily oversampled (≥1000), developability-
   gated, docked state-matched, ranked vs the decoy null. (DiffSBDD scaffold/inpaint conditioning, or R-group
   enumeration around the core, in `nr4a3_denovo.py`.)
3. **Confirm survivors with decoy-calibrated MULTI-snapshot/ensemble MM-GBSA** (Tier 3 #6 — MD-relaxed,
   multi-frame, error bars; re-run a decoy subset through it to re-calibrate). Only then FEP, only on an
   above-null lead. Decoy set is a **standing specificity gate** for every tier.

## ABOVE-NULL LEAD SET (2026-06-30, decoy bar = +13.12; grows as deeper docks land)
Dock-deeper worked: the v3-deep (top-60) MM-GBSA surfaced the two best candidates that top-20-by-promise had
buried. Current clean, above-decoy-null NR4A3-selective leads (margin = NR4A3 MM-GBSA selectivity margin):
| lead | margin | dock cell | QED/SA/MW | SMILES | note |
|------|--------|-----------|-----------|--------|------|
| **denovo_393** | **+18.34** | **NR4A3-only** | 0.77/3.63/233 | `C[C@@]1(N2CCc3ccccc32)CC[C@@H](O)[C@@H]1O` | **BEST** — both tiers, above decoy MAX (16.46); small+clean (indoline + cyclohexane-1,2-diol) |
| denovo_111 | +15.70 | none | 0.87/2.9/281 | `CC[C@H](C)c1cc(OCCO)cc(N2CCCC2)c1F` | MM-GBSA both states |
| denovo_780 | +14.66 | pan-NR4A | 0.41/4.38/494 | (large) | weak: pan dock cell, low QED, MW 494 |
| denovo_401 | +13.92 | **NR4A3-only** | 0.80/3.87/304 | `COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1` | both tiers, clean |
**Strongest = denovo_393 + denovo_401** (NR4A3-only at docking AND above the decoy MM-GBSA bar AND clean) —
the seeds for scaffold-seeded lead-opt + the multi-snapshot/FEP confirmation tier. v4-deep MM-GBSA running →
will extend this. NOTE single-snapshot noise is real (denovo_277 +13.07 top-20 → +11.01 deep), so multi-
snapshot confirmation is needed before FEP, but the decoy bar reliably ranks the strong outliers.

## STATUS 2026-06-30 ~17:15 UTC: blind generation exhausted; PIVOT to confirm + optimize
v4-deep (1000 gen, top-60) MM-GBSA added **0 above-null** (top denovo_799 +6.47, all < the +13.12 bar). With
v3-deep giving 2 and v4-deep giving 0, **blind generation has diminishing returns** — stop spinning new blind
rounds (waste of the single g5). Portfolio stands at **4 above-null clean leads, denovo_393 the standout
(+18.34, above the decoy max, NR4A3-only both tiers)**. (Minor: v4-deep `nr4a3-mmgbsa.json` `_status` read
`in_progress` — per-candidate rows all present/ranked, only the final census write missed; no above-null so
immaterial.) **Next phase (deliberate builds, gated on trimcrae steer + GPU spend):**
1. **Confirm denovo_393 (+401/111) with decoy-calibrated MULTI-snapshot MM-GBSA** (Tier-3 #6: short MD relax +
   multi-frame avg + SD; re-score a decoy subset to re-calibrate). denovo_393 above the decoy *max* is the most
   noise-robust, most worth confirming.
2. **Scaffold-seeded lead-opt around denovo_393/401** — DiffSBDD inpainting (fix core, regenerate substituents)
   conditioned on the divergent handles; far higher above-null hit-rate than blind generation.
Then FEP only on a multi-snapshot-confirmed above-null lead. Do NOT keep firing blind generation rounds.

## KEY LEVER (2026-06-30 late): DOCK DEEPER, don't just generate more
The dock funnel only scores **TOP_N=20 by `denovo_promise`** — but promise ranks on QED/SA/handles, **NOT
selectivity** — so above-null selective candidates ranked >20 by promise are never docked/scored. Evidence:
v2 (500 gen, top-20) → 1 above-null (denovo_401); v3 (1000 gen, top-20) → 0 (best denovo_277 +13.07, just
under the +13.12 bar). Scaling generation didn't help because we under-sample each pool. **Fix: raise TOP_N
(dock the full developable set, ~60–110 for 1000 gens) so the decoy-calibrated MM-GBSA can find the buried
above-null hits.** Dock is CPU (cheap, overlaps the g5 generation); MM-GBSA on ~60 cands = ~2–3 h g5 (~$3–4).
- **v3-deep dock RUNNING** (`top_n=60` → `nr4a3-denovo-matrix-v3deep`); then MM-GBSA → rank vs decoy bar.
- **v4 generation RUNNING** (`nr4a3-denovo-v4`, n=1000) — dock it deep too (top_n=60), not top-20.
- **Also deepen v2** (top_n=60) — cheap, may surface more siblings of denovo_401.
- Better still (next build): rank the developable set by a **selectivity-aware prior** before docking (e.g.
  divergent-handle-contact count from the generated pose) instead of `denovo_promise`, so the docked subset is
  enriched for selectivity, not drug-likeness. Then the scaffold-seeded DiffSBDD inpainting around denovo_401.

## Where the science landed (all committed to `main`)
| Result | Value | Source |
|--------|-------|--------|
| Static orthosteric druggability (AF2) | **0.495** (Pocket 5, res 406–534) | `nr4a3-structure-assessment.json` |
| Calibrated druggable threshold **D\*** | **0.53** (validated drug-bound NR band 0.53–0.68) | `gpu-calibration-aws.yml` → `nr4a3-calibration.json` |
| Model over-call? | **No** — NR4A2 model 0.801 ≈ 1OVL crystal 0.864; 0.495 is conservative | calibration |
| **Gate 1** cryptic *opening* (distinct opened basin) | **Weaker basin-breathing pass** — F(Rg) monotonic, no opened minimum/shoulder; not the literal pre-reg condition | `fes.dat` (sum_hills) |
| **Gate 2** opened-pocket druggability (30 ns) | **0.931** (orthosteric Pocket-5, *peak* over frames; report fraction ≥ D\* — ≥5% bar met; biased-MD); PASS | `gpu-mdpocket-aws.yml` on `nr4a3-metad` |
| **Gate 3** energetic accessibility | **PROVISIONAL** — druggable (0.80) at CV Rg 0.717 nm for **0.76 kcal/mol** read off the same under-converged biased F(Rg) (the ~38 kcal/mol was the cost to the most-OPEN *edge*); release run is the independent confirmation | F(Rg)-vs-druggability re-analysis |
| Selectivity handles (NR4A3 vs NR4A1/2) | **7**: L406, T407, T410, R412, I484, I531, L534 | `nr4a-selectivity.json` |

Full reconciliation + gate scoring + the disclosed Gate-0 deviation:
[`nr4a3-druggability-reconciliation.md`](./nr4a3-druggability-reconciliation.md).

**Indications = a programmable matrix (see paper §3):** **lead** = NR4A3-selective → EMC + AciCC
(NR4A3-overexpression-driven) + other NR4A3-fusion sarcomas. **Second design mode** = *pan*-NR4A (triple
degradation) for ex-vivo/transient immuno-oncology (T-cell exhaustion; Chen 2019) — a distinct molecule,
not a contingency. **Anti-target** = NR4A1+NR4A3 (combined loss → AML; design *away* from). HCC/breast
also tumour-suppressive. Detail:
[`../manuscripts/nr4a3-degrader-broader-indications.md`](../manuscripts/nr4a3-degrader-broader-indications.md).

## STEP 0 — handle-facing confirmation — ✅ DONE (CONFIRMED 2026-06-26, run 28249776934)
**Result:** druggable frames 8/25 sampled (fpocket ≥ D\*=0.53); **mean 5.0/7 handles pocket-facing**;
87.5 % of druggable frames keep ≥4 facing → registered Gate-2 second clause **CONFIRMED**. Per-handle
fraction-facing in druggable frames: **L406 1.0, I531 1.0, L534 1.0, T410 0.875, I484 0.875** (the five
engageable handles) vs **T407 0.0, R412 0.25** (splay outward). Output:
`s3://sagemaker-us-east-2-646605541856/nr4a3-handle-facing/handle_facing_summary.json` (+ `handle_facing.png`).
Implication for the warhead screen: the realistic selectivity-handle set is five, not seven.

**Pipeline (built, unit-tested, committed):** `nr4a3_handle_facing.py` + `handle_facing_geom.py` (pure,
8 passing tests in `tests/test_handle_facing_geom.py`) + `sagemaker_src/entry_handle_facing.py` +
`nr4a3_handle_facing_sagemaker.py` + `.github/workflows/handle-facing-aws.yml`.

**Why first:** the warhead screen ranks candidates partly by **handle-contact count**; if the 7 handles
do not stay pocket-facing in the opened/druggable frames, that score is meaningless. This is also the
unmet second clause of the pre-registered Gate-2 pass condition. It reuses the existing 30 ns trajectory
(no new GPU run), runs fpocket + pure geometry over ~25 frames (CPU, well under an hour, `wait=True` safe).

**To launch:** dispatch **`handle-facing-aws.yml`** on `main` (defaults fine): `input_prefix=nr4a3-metad`,
`dcd_name=nr4a3-lbd-metad.dcd`, `output_prefix=nr4a3-handle-facing`, `region=us-east-2`, `git_ref=main`.

**What it does / how to read it:** for sampled frames it finds the orthosteric pocket (same fpocket
mapping as `nr4a3_mdpocket.py`) and its druggability, takes the cavity centroid from that pocket's lining
CA atoms, and for each handle decides "pocket-facing" (CA→side-chain centroid has a positive component
along CA→cavity). Output `nr4a3-handle-facing/handle_facing_summary.json` reports, per handle, the
fraction of druggable frames it faces in, plus a **verdict**: CONFIRMED if a majority of druggable
(fpocket ≥ D\*=0.53) frames keep ≥ 4 of 7 handles facing in. **CONFIRMED → proceed to the warhead screen;
NOT CONFIRMED → the handle-based selectivity spec needs rework before docking (and Gate 2's second clause
fails, weakening the route).** Then update paper §2.2/§5, the reconciliation Gate-2 row, and this file.

## THE NEXT STEP (after Step 0) — run the selective-warhead screen
**Pipeline (built, tested-compile, committed):** `nr4a3_warhead.py` + `sagemaker_src/entry_warhead.py`
+ `nr4a3_warhead_sagemaker.py` + `.github/workflows/gpu-warhead-aws.yml`.

**To launch (from a session with GitHub Actions access):** dispatch **`gpu-warhead-aws.yml`** on `main`
(defaults are fine): `input_prefix=nr4a3-metad`, `output_prefix=nr4a3-warhead`, `region=us-east-2`,
`git_ref=main`. It is CPU work (< 6 h), so the GitHub wrapper's `wait=True` is safe.

**What it does:** (1) extracts the most-druggable OPENED conformer from the 30 ns trajectory
(`s3://<bucket>/nr4a3-metad/nr4a3-lbd-metad.dcd`) — designs against the open 0.93 pocket, not the
collapsed static one; (2) maps Pocket-5 onto NR4A1 (P22736) / NR4A2 (P43354) by BLOSUM62 alignment to
box the homologous paralogue pockets; (3) docks candidate ligands (real ChEMBL NR4A actives via
`nr4a3_dock` helpers) into NR4A3-opened + NR4A1 + NR4A2 with smina; (4) scores per candidate:
`dG_NR4A3`, **selectivity margin** = min(dG_NR4A1, dG_NR4A2) − dG_NR4A3 (more positive = more
NR4A3-selective), and **handle-contact count**. Output → `s3://<bucket>/nr4a3-warhead/nr4a3-warhead.json`
(+ opened-conformer PDB + pose SDFs).

**How to read it:** rank by selectivity margin → NR4A3 potency → handle engagement. A good warhead lead
binds NR4A3-opened well, has a positive selectivity margin vs both paralogues, and contacts several of
the 7 handles. Remember: docking = screening prior, NOT affinity; this nominates chemotypes, not a lead.

**Warhead screen — DONE (run 28252182123, 2026-06-26).** Top NR4A3-favoured: CHEMBL1873475
(dG_NR4A3 −8.34, margin +1.7, 4/5 handles), amodiaquine (−7.63, +1.53). **Caveat:** a first run silently
voided selectivity (paralogue docks failed on a residue-renumbering bug — the opened conformer is
renumbered 1..254, not the AF2 406..534); fixed by passing the opened conformer's actual resSeqs (`box_res`)
into `map_pocket_to_paralogue`, plus fail-loud guards (`selectivity_evaluated`, `paralogue_pocket_residues_mapped`).
These margins are still **opened-NR4A3-vs-STATIC-paralogue = confounded upper bounds** on selectivity —
the family metad (in flight) is the fix.

**FAMILY-WIDE MATRIX — build steps once `nr4a1-metad` + `nr4a2-metad` land in S3:**
1. **State-matched warhead matrix** — extend `nr4a3_warhead.py` to dock the library into each paralogue's
   OWN opened conformer (extracted from `nr4a1-metad`/`nr4a2-metad` like NR4A3's), not the static AF model.
   Output a per-candidate selectivity *fingerprint* across the three → partition into NR4A3-only / pan /
   NR4A1+NR4A3 anti-target cells. Also add a **conserved-residue contact score** + pan ranking, and **dedup**
   the candidate list (CHEMBL682 duplicated in run 28252182123).
   - **DONE (2026-06-28, run 28319737517).** classifier `selectivity_fingerprint.py` (7 tests) + driver
     `nr4a3_matrix.py` (mounts all three `*-metad` prefixes, extracts each opened conformer, docks the
     deduped library into all three, classifies via `classify()`, scores divergent-handle + conserved-CV
     contacts) + `sagemaker_src/entry_matrix.py` + `nr4a3_matrix_sagemaker.py` + `.github/workflows/gpu-matrix-aws.yml`.
     Output `s3://<bucket>/nr4a3-matrix/nr4a3-matrix.json` = per-candidate cell + census + leads. **Read it
     back with `report-matrix-aws.yml`** (read-only S3 dump → ranked table + census + leads). Result summary
     in the STATUS block above; lead = **cytosporone B** (NR4A3-selective, margins +1.42/+1.16), pan leads =
     celastrol + CHEMBL1873475, **anti-target cell empty**.
2. **Endpoint free energy (the defensible margin)** — MM-GBSA then selectivity FEP. Docking stays triage only.
   - **MM-GBSA — DONE (2026-06-28, run 11): docking selectivity does NOT robustly survive; cytosporone B
     reverses as predicted.** Census of 13: rescued 3 · confirmed_selective 3 (amodiaquine, celastrol +
     amodiaquine's dup) · reversed 3 (cytosporone B + its CHEMBL1221517 dup, piperlongumine) · weakened 2 ·
     confirmed_nonselective 2. Same molecule under two library labels gets the same verdict (consistency
     check passes). Magnitudes are inflated by the single-snapshot/no-entropy approximation — trust the
     verdict/direction, not the kcal/mol. Read it via `report-mmgbsa-aws.yml`. Full build/run history:**
     Single-snapshot 1-trajectory MM-GBSA (enthalpy + GBn2 implicit solvent; **no entropy, no ensemble
     average**) that **re-scores the matrix's own docked poses** — pure `mmgbsa_select.py` (10 tests) +
     `mmgbsa_energy.py` (OpenMM + OpenFF/GAFF-2.11 + PDBFixer; guarded heavy deps) + driver `nr4a3_mmgbsa.py`
     (mounts `s3://<bucket>/nr4a3-matrix`, prepares each receptor once, computes ΔG into NR4A3/NR4A1/NR4A2,
     recomputes selectivity margins, emits a **verdict** vs the docking margins: confirmed_selective /
     reversed / weakened / rescued) + `sagemaker_src/entry_mmgbsa.py` + `nr4a3_mmgbsa_sagemaker.py` +
     `.github/workflows/mmgbsa-aws.yml`. **NO re-dock, NO MD → CPU work, minutes** (not a multi-hour GPU run).
     Output `s3://<bucket>/nr4a3-mmgbsa/nr4a3-mmgbsa.json`.
     - **Run-7 post-mortem (2026-06-28) — the real story behind the "5 fixes".** Runs ≤4 failed *fast*
       all-`incomplete` on a cascade of platform bugs in `mmgbsa_energy.py` (nonbonded kwargs → box strip →
       GPU platform → CUDA-PTX→OpenCL fallback). **Run 7 then hung for 82 min in TOTAL SILENCE and had to be
       killed.** Reading the cancelled job's CloudWatch log showed it never reached the compute at all: it
       stalled in **conda env creation**. Root cause = the env was **unpinned** and `openff-toolkit` (the
       metapackage) pulls `openff-nagl`, which drags in the multi-GB **PyTorch-CUDA stack** we never use; that
       bloat stalled the build, and there was **no heartbeat/timeout** so it would have burned to the 4 h cap.
       So the four `mmgbsa_energy.py` platform fixes addressed a *downstream* problem run 7 never reached.
     - **The hardening (this session) — three changes, all CPU-side/free:** (1) **slim env** — install
       `openff-toolkit-base` (no nagl → no PyTorch/CUDA); AM1-BCC charges for gaff-2.11 come from AmberTools
       `sqm`, so nothing is lost; `entry_mmgbsa.py` also captures a `conda list --explicit` lock to
       `mmg-lock.txt` for future pinning. (2) **never go blind** — every long step streams live + prints an
       elapsed heartbeat + has a hard wall-clock timeout (30 min env build, 90 min compute, 600 s/leg via
       SIGALRM); the compute prints the chosen OpenMM platform up front and **checkpoints `nr4a3-mmgbsa.json`
       after every ligand**. (3) **cheap + certain instance** — default flipped from `ml.g5.xlarge` to
       **`ml.c5.2xlarge`** (CPU; this step never needed a GPU — removes the OpenCL uncertainty; ~$0.34/h,
       a clean run ≈ $0.2). Override with `INSTANCE=ml.g5.xlarge` for GPU.
     - **NEW observability tool:** `tail-cloudwatch-aws.yml` (+ `tail_cloudwatch.py`) — read-only, dispatch
       any time to print the last N CloudWatch events of a **running** job (`job_prefix=nr4a3-mmgbsa`). Use it
       to watch a live run instead of cancelling to see the log. **NOTE: a brand-new workflow is only
       API-dispatchable once it exists on the *default branch* — merge `tail-cloudwatch-aws.yml` to `main`
       before relying on live-tailing.**
     - **Run 8 (2026-06-28, CPU `ml.c5.2xlarge`, on the fix branch) — env fix CONFIRMED, CPU NON-VIABLE.**
       The hardening worked exactly as designed: the slim env built in **172 s** (vs run 7's 82-min hang),
       `mmg-lock.txt` (212 lines) was captured, the platform line printed (`OpenMM platform: CPU` — CUDA/OpenCL
       not registered on a c5), heartbeats streamed throughout, and the job **timed out cleanly at 90 min**
       (exit 124) with a per-ligand checkpoint written — no blind burn, full visibility. BUT the CPU compute
       is brutally slow: `[1/13] celastrol -> incomplete (2866s)` — one ligand took **48 min** and still came
       back incomplete (an NR4A3 leg failed/over-ran); ligand 2 was mid-flight at the cap. The ~4000-atom GB
       minimisations need a GPU; 13×3 on CPU would be ~10+ h. **Takeaway: the env was the real bug (fixed);
       the compute genuinely needs the GPU after all** — the original g5 instinct was right, just sabotaged by
       the env hang. (Watch celastrol's `incomplete` — if it's a real GAFF/AM1-BCC param failure, not just
       slowness, it will recur on GPU.)
     - **NO CPU FALLBACK (trimcrae, 2026-06-28).** `mmgbsa_energy._platform` now tries only CUDA -> OpenCL
       and **raises in seconds** if neither GPU platform loads (no silent CPU grind); `nr4a3_mmgbsa.py`
       probes the platform up front so the job dies fast with a clear message. Compute timeout cut 90 -> 30
       min. Instance defaults flipped back to `ml.g5.xlarge`. Escape hatch: `MMGBSA_ALLOW_CPU=1` (explicit
       opt-in only).
     - **Run 9 (2026-06-28, g5, watched live) — both GPU platforms unusable; fail-fast worked; ROOT CAUSE
       found.** The live `tail-cloudwatch-aws.yml` caught it in real time: `CUDA unavailable: ...
       UNSUPPORTED_PTX_VERSION` AND `OpenCL unavailable: There is no registered Platform called "OpenCL"`,
       so the no-CPU path raised and the job **died in seconds** (exit 1, ~$0.25) with a clear message — no
       grind. Cause of the OpenCL miss: **slimming the env dropped the OpenCL ICD loader** that run 7's
       bloated env carried transitively; OpenMM's OpenCL plugin needs `libOpenCL` at runtime to register.
     - **Fix applied: add `ocl-icd-system` to the slim env** (entry_mmgbsa.py) — the ICD bridged to the
       instance's NVIDIA OpenCL driver, so OpenMM's OpenCL platform registers and runs on the A10G,
       sidestepping the CUDA PTX problem (the original point of the CUDA->OpenCL design).
     - **Run 11 (2026-06-28, g5) — SUCCESS, the OpenCL ICD fix worked.** Live tail showed `CUDA unavailable:
       UNSUPPORTED_PTX_VERSION` then **`[mmgbsa] OpenMM platform: OpenCL`** — OpenCL now drives the A10G;
       ~1–2 min/ligand, all 13 done in ~25 min, `_status: ok`. The full chain that unblocked it: slim env
       (run 8) + `ocl-icd-system` loader (run 10) + writing `/etc/OpenCL/vendors/nvidia.icd` (run 11). The
       no-CPU fail-fast kept every wrong guess (runs 8–10) to seconds/~$0.25 and the live tail diagnosed each
       without a kill. **MM-GBSA is now a working, repeatable GPU pipeline.**
     - **Result (the science):** see the census above. Bottom line — docking's specific NR4A3-selectivity
       calls are mostly *not* robust to a better energy model (headline hit cytosporone B reverses, as its
       known NR4A1 pharmacology demands), but amodiaquine and celastrol survive as `confirmed_selective`.
       Treat as triage (inflated magnitudes); FEP stays the affinity tier, still gated behind the release run.
     - **To launch (asks first — GPU rule still applies to the c5 spend by courtesy):** dispatch
       `mmgbsa-aws.yml` on `main` (defaults fine), then `tail-cloudwatch-aws.yml` to watch, then
       `report-mmgbsa-aws.yml` for the verdict census + ranked table. This tests the matrix's central caveat
       (every selectivity call within docking noise; top hit cytosporone B is a known NR4A1 agonist → expect a
       `reversed` verdict if the docking selectivity is artefactual). **Per-residue decomposition +
       multi-snapshot averaging remain the documented follow-ups.**
   - **Selectivity FEP** on the lead 1–3 — the program's dominant GPU cost (~1–3 weeks serial). **DEFERRED**
     pending (i) the unbiased release run confirming the opened pocket is metastable and (ii) MM-GBSA + a
     de-novo *bona fide* selective candidate worth the spend. See `nr4a3-matrix-result.md` for the go/no-go.
3. **De-novo generative design** — `nr4a3_warhead.py::generate_denovo()` stub: wire DiffSBDD/Pocket2Mol,
   two campaigns (divergent-handle-conditioned = selective; conserved-conditioned = pan) to fill empty cells.
   - **DE-NOVO SESSION 2026-06-29 — Step 0 + Step 1 DONE; DiffSBDD wiring (Step 2) next.**
     - **Step 0 — receptor RE-ANCHORED to a druggable UNBIASED RELEASE frame (run 28365883750, CPU c5,
       DONE).** New pipeline `release_frame_select.py` (pure, 9 tests) + `nr4a3_release_druggable.py` +
       `sagemaker_src/entry_release_druggable.py` + `nr4a3_release_druggable_sagemaker.py` +
       `.github/workflows/release-druggable-aws.yml`. Reuses the `nr4a3-release-pocket` per-frame
       druggability to pick candidates, then re-runs fpocket on each chosen frame to CONFIRM + read the
       docking box. Output `s3://<bucket>/nr4a3-release-druggable/` (manifest + 4 receptor PDBs + plot).
       **Result:** **primary = rep0 frame 95, Rg 0.7367 (≈ target 0.737), confirmed druggability 0.667**
       (in the 0.53–0.68 drug-bound band). Druggable **sub-ensemble = primary + alt1 (0.536) + alt3
       (0.642)**, spanning Rg 0.737–0.764. **alt2 (frame 41) DROPPED:** reused-summary 0.558 but confirmed
       **0.001** on re-extraction (single-frame fpocket / fpocket-build fragility — the reason the driver
       re-confirms). Driver hardened to confirm-filter the sub-ensemble (`druggable_subensemble`,
       `docking_primary_receptor`) so the manifest is self-describing; **downstream docking/MM-GBSA must use
       the confirmed sub-ensemble, not the biased-metad frame and not every chosen frame.**
     - **Step 1 — selectivity BLUEPRINT DONE (CPU/local).** `denovo_blueprint.py` (pure, 8 tests) +
       `nr4a3_denovo_blueprint.py` → `nr4a3-denovo-blueprint.json`. Classifies Pocket-5: **5 engageable
       selective handles** — **4 discriminate BOTH paralogues (L406, T410, I484, L534)**, **1 NR4A1-only
       (I531 ≡ NR4A2)** — conserved core **P411, R481, R485** (pan campaign). Selective campaign weights the
       both-paralogue handles over I531.
     - **Step 2 — DiffSBDD PIPELINE BUILT + PILOT RAN (run 28381505291, g5, DONE 2026-06-29).** Pipeline:
       `nr4a3_denovo.py` + `denovo_funnel.py` (pure, 7 tests) + `sagemaker_src/entry_denovo.py` +
       `nr4a3_denovo_sagemaker.py` + `gpu-denovo-aws.yml`. Conditions DiffSBDD (pretrained CrossDocked,
       Zenodo 8183747) on the Step-0 `docking_primary_receptor` pocket (resi_list = the 12 fpocket box
       residues; handles mapped via residue_map), then RDKit-profiles + counts engageable-handle contacts
       from the GENERATED POSE + ranks (denovo_funnel).
       - **ENV SHAKEOUT (6 runs, each caught live via streamed log + fail-fast, ~$0.2–0.5 each).** DiffSBDD
         is a 2023 repo; on the g5 it needed: (1) `pip<24.1` (PL 1.7.4 legacy metadata); (2) pin
         `torch==1.12.1+cu116` + `torchmetrics==0.9.3` (else framework deps pull a CUDA-13 torch the A10G
         driver rejects — caught by the no-CPU GPU probe); (3) `setuptools<81` (PL imports removed
         `pkg_resources`); (4) `biopython=1.79` (`Bio.PDB.Polypeptide.three_to_one` removed ≥1.80);
         (5) `libstdcxx-ng` + prepend env lib to `LD_LIBRARY_PATH` (base-conda libstdc++ shadowed the env's,
         matplotlib CXXABI_1.3.15). All five fixes are in `entry_denovo.py` and ran clean on run 6.
       - **PILOT RESULT (selective campaign, n=200):** generation 95 s; **191/197 valid, 182 unique;
         synthesizable SA≤4.5 = 0.874, PAINS-free = 0.99, contacts ≥4 handles = 0.901 (max 5).** Pipeline
         validated end-to-end. **CAVEAT (the eyeball finding): top-ranked hits are FRAGMENT-sized**
         (benzoic acid, toluic acid, 4-Cl-N-cyclopropylaniline) — generation ran with UNCONSTRAINED ligand
         size and the promise score (QED + low SAscore) rewards trivially-small fragments. Not leads.
         **Production run needs a ligand-SIZE constraint** (`--num_nodes_lig` / a lead-sized node
         distribution, ~25–40 heavy atoms) **+ a MW/heavy-atom floor in `denovo_funnel.score_molecule`**,
         then re-rank. Output `s3://<bucket>/nr4a3-denovo/` (nr4a3-denovo.json + .sdf + raw .sdf + plot).
       - **SIZE-CONSTRAINED RE-RUN — DONE (run 28384233714, 2026-06-29). Fragments fixed.** Added a
         lead-size split (`NUM_NODES_LIST=24,28,32,36` heavy atoms via DiffSBDD `--num_nodes_lig`, N split
         across them) + a `min_mw=250` size penalty in `denovo_funnel.score_molecule`. Result: **191/195
         valid, 191 unique, PAINS-free 0.963, contacts ≥4 handles 0.916 (max 5).** Top candidates are now
         LEAD-SIZED (not fragments): **denovo_189** `COc1ccc(-c2cc(C(C)=O)cc(C(=O)O)c2)cc1` (promise 0.953,
         QED 0.87, SA 1.73, 4 handles, ~270 Da, COOH PROTAC handle) · denovo_17
         `NCC(=O)Nc1ccc(CCC2CC2)cc1` (0.814, amine handle) · **denovo_106** (0.701, **5/5 handles**) ·
         denovo_139 (thienopyrimidine, QED 0.82). SA≤4.5 frac fell to 0.393 (larger mols → higher SA), but
         the top hits remain very synthesizable. Output `s3://<bucket>/nr4a3-denovo/` (nr4a3-denovo.json +
         .sdf + per-size raw SDFs + plot). These are bona-fide de-novo selective-warhead starting points.
       - **FUNNEL — DOCK TIER DONE (run 28387098688, CPU c5, 2026-06-29).** New env-guarded de-novo mode in
         `nr4a3_matrix.py` (+ `denovo_library.py`, 4 tests) + `entry_denovo_dock.py` +
         `nr4a3_denovo_dock_sagemaker.py` + `gpu-denovo-dock-aws.yml`. Docked the top-20 de-novo candidates
         into the **Step-0 NR4A3 release receptor** (box on its 12 fpocket residues) + NR4A1 frame 524
         (0.981) + NR4A2 frame 125 (0.938). Output `s3://<bucket>/nr4a3-denovo-matrix/` in the SAME format
         MM-GBSA consumes. **Selectivity fingerprint (DOCKING PRIOR, within noise):** NR4A3-favoured-by-margin =
         **denovo_15** (margin +1.0; **NB its strict matrix cell is NR4A2+NR4A3** — at the permissive
         −7 kcal/mol engagement cutoff NR4A2 is weakly co-engaged, so it is the *favoured* paralogue, not an
         exclusive NR4A3-only cell. There is **no NR4A3-only cell** in the census below — an earlier "the only
         NR4A3-only cell" note here was wrong; the paper §2.5 states it the careful way, reconcile to that).
         **Caveat: this de-novo dock is NOT state-matched** (NR4A3 unbiased-release frame 0.667 vs biased-metad
         NR4A1 524 / NR4A2 125 — conservative for NR4A3-selectivity). pan-NR4A = denovo_21 / **denovo_106**
         (5/5 handles) / denovo_51; **anti-target (NR4A1+NR4A3) = denovo_189** (the top-by-chemistry hit — so
         chemistry promise ≠ selectivity). Census/20: NR4A2+NR4A3 4 · pan 4 · none 5 · NR4A2-only 3 ·
         NR4A1+NR4A2 2 · NR4A1+NR4A3 1 · NR4A1-only 1.
       - **FUNNEL — MM-GBSA TIER DONE (run 28393997521, g5/OpenCL, 2026-06-29). HEADLINE RESULT.** Re-scored
         the 20 de-novo docked poses (single-snapshot 1-traj MM-GBSA) → per-candidate verdict vs docking.
         (First attempt run 28391025615 hit the old 30-min compute cap on 20×3 legs and — being EndOfJob
         upload — lost the partial; that prompted the continuous-upload + configurable-timeout fix above, and
         the re-run with `compute_timeout=3600` finished all 20 in 46 min.) **Verdict census: confirmed_selective
         3 · rescued 7 · weakened 1 · confirmed_nonselective 9 · REVERSED 0.** Output
         `s3://<bucket>/nr4a3-denovo-mmgbsa/` (read via `report-mmgbsa-aws.yml`).
         - **confirmed_selective = `denovo_15`, `denovo_94`, `denovo_57`.** Unlike the repurposed-compound
           MM-GBSA (where the headline cytosporone B **reversed**), **NO de-novo candidate reversed** — the
           de-novo route produced selectivity that survives a physics-based energy model.
         - **LEAD = `denovo_15`** (SMILES `C=C(CC1=CC=C(NC(=O)O)C1)[C@H]1C=C2C(=NC1)OC[C@H](C)[C@@H]2C`;
           QED 0.774, SAscore 5.08, contacts 4/5 handles — resolved from nr4a3-denovo.json into paper §2.5 +
           figures): the
           ONLY candidate selective at BOTH tiers (docking margin +1.0, **MM-GBSA margin +10.71 kcal/mol**),
           the most robust call. denovo_94 (+0.15 dock, +5.02 mm) second. (MM-GBSA magnitudes are inflated by
           the single-snapshot/no-entropy approximation — trust verdict/direction, not kcal/mol; and that
           direction is itself a single-snapshot, unreplicated point estimate — no ensemble/replicate error.)
           denovo_189 (top-by-chemistry / docking anti-target) did NOT come back selective — consistent.
         - **🛑 CHEMISTRY RED-TEAM on `denovo_15` (2026-06-29, RDKit on the SMILES) — it is a chemotype/pose
           hypothesis, NOT a developable molecule.** The SMILES carries DiffSBDD-typical liabilities: a
           **carbamic acid** (`NC(=O)O`, the polar handle — hydrolytically unstable → amine + CO₂), a
           **1,3-cyclopentadiene** (reactive diene), an **imine**, an **exocyclic alkene**, and **no aromatic
           ring** (C19H24N2O3, MW 328); **SAscore 5.08 is ABOVE the campaign's own ≤4.5 synthesizability cut**
           (QED 0.774 does not screen stability/reactivity). The durable result is the *funnel + selectivity
           direction* (de-novo matter survives MM-GBSA without reversing; repurposed matter reversed), not this
           molecule.
         - **94/57 SCREEN DONE (report-denovo run 28405141248 + RDKit, 2026-06-29) — neither rescues the lead.**
           **denovo_94** (`CO[C@H]1S[C@H](N[C@H]2CCOO[C@@]2(C)CO)c2nc(-c3ccccc3F)ccc21`, mm +5.02, 4 handles,
           cell NR4A2+NR4A3) carries a **peroxide (1,2-dioxane)** + N,S-/O,S-acetals — non-viable. **denovo_57**
           (`NC[C@@H]1CCN(Cc2ccccc2)C1`, 3-(aminomethyl)-1-benzylpyrrolidine, mm +1.07, **2** handles, cell
           **none**) is the **only chemically clean** hit (SA 2.09, aromatic, basic amine, no flags) but is the
           **weakest** selectivity signal / fewest handles. **Net: the 3 confirmed_selective hits are
           strong-but-artifactual (15/94) or clean-but-weak (57); none is both viable AND strongly selective** —
           so the honest paper claim is the **method/funnel** (selectivity survives MM-GBSA), not a developable
           molecule. **Next de-novo steps:** add a stability/reactivity filter to `denovo_funnel.score_molecule`
           (reject peroxides, carbamic acids, cyclopentadienes, acetals/aminals, non-aromatic warheads, SA>4.5)
           and **re-generate**; only then consider a single defensible candidate for FEP/ternary.
         - **DEVELOPABILITY GATE BUILT + 191 RE-SCREENED (2026-06-29, red-team Tier-1 #1 + external review).**
           New `structural_alerts.py` (BRENK + curated reactive/unstable SMARTS: peroxide, carbamic acid,
           hemiketal/aminal, acetals, cyclopenta-/cyclohexadiene, Michael acceptor, N-O bond, thiocarbonyl,
           ...) + aromatic-ring + SA≤4.5 gate, wired into `denovo_funnel.score_molecule`,
           `denovo_library.top_developable_candidates`, and `report_denovo.py` (run via `report-denovo-aws.yml`,
           now installs rdkit). **Re-screen of the 191 generations: only 11 are clean (BRENK was the big
           filter, 30→11), 9 of those contact ≥4 handles, and NONE of the clean ones is currently
           NR4A3-selective** — the clean+favourable docking cells are pan/nonselective or the NR4A1+NR4A3
           anti-target; denovo_57 is the only clean confirmed_selective but lands in dock cell "none". Only 3
           clean candidates were never docked (denovo_170, denovo_0, denovo_83). **Implication: clean hits are
           sparse → the real lever is re-generation with the filter in-loop over a larger pool (Tier 2), not
           docking the existing set.** `gpu-denovo-dock-aws.yml` now takes `developable_only` (default 1) +
           `receptor_mode` (release|metad, the Tier-1 #3 state-matched re-dock).
       - **NEXT (gated):** `denovo_15` is the program's first bona-fide in-silico NR4A3-selective warhead
         candidate. Options: (a) selectivity FEP on denovo_15 (the defensible affinity tier; $-hundreds,
         ~1–3 wk serial — gate hardest); (b) ternary-complex modeling (`gpu-ternary-aws.yml`) to turn the
         selective binder into a selective degrader; (c) pan campaign (conserved-core resi_list) for contrast.
         **This whole de-novo arc (Step 0 → blueprint → DiffSBDD → dock → MM-GBSA) is now a complete, citable
         in-silico result for the degrader paper: a designed, MM-GBSA-confirmed NR4A3-selective warhead.**
4. **Ternary complex per paralogue** — once a warhead SMILES exists, `nr4a3_ternary.py` / `gpu-ternary-aws.yml`
   for degradable-lysine geometry (degradation selectivity ≠ warhead-binding selectivity).
5. **Handle-facing confirmation** — done (Step 0); rerun on each paralogue's opened ensemble for symmetry.

## Infra gotchas a fresh session MUST know
- **🛑 ABFE ENGINE POLICY — Yank is the CURRENT engine but END-OF-LIFE; the NEXT *fresh* FEP uses a MODERN,
  MAINTAINED stack (trimcrae decision, 2026-07-04).** The denovo_401 selectivity FEP runs on **Yank 0.25.2
  (2020, unmaintained)** — chosen for turnkey *declarative* ABFE, but it cost ~a full day of dependency/schema
  archaeology (numba swap-all masked-array crash → `replica_mixing_scheme: swap-neighbors`; that key is a
  ReplicaExchangeSampler ctor arg, NOT an `options:` key → move to a `samplers:` header; `libnetcdf<4.9`;
  `pymbar<4`; `python=3.9`; the `conda run` PYTHONPATH leak). **The working env is now FROZEN** for
  reproducibility: `sagemaker_src/environment-fep.yml` (pinned spec) + `sagemaker_src/Dockerfile.fep` (buildable
  image) + `sagemaker_src/fep.lock` (authoritative `conda list --explicit`, emitted by `yank-env-check.yml`
  between `----FEP_LOCK_BEGIN/END----` — capture it once and commit). **Decision:**
  - The **current** denovo_401 run **finishes on Yank** — do NOT whipsaw a run that is producing; the physics is
    standard double-decoupling ABFE and the number is valid.
  - The **next time an ABFE/FEP is STARTED FRESH** — whether **(a)** Yank hits another failure, or **(b)** we run
    FEP on a **new degrader candidate / target** — do **NOT** extend Yank. Stand up a maintained stack:
    **OpenFE's absolute-binding protocol**, or an **openmmtools-scripted ABFE** (compose its *tested*
    alchemy/`ReplicaExchangeSampler`/MBAR primitives).
  - **Rationale:** (i) the field's values shifted to explicit/composable/reproducible pipelines over black-box
    declarative apps — better provenance for a convince-the-field paper; (ii) Yank's abandonment is a standing
    reproducibility/provenance liability (env-freeze mitigates it for *this* result, doesn't fix it for future
    ones); (iii) **the only thing Yank bought — turnkey = less code — is nearly free here anyway, because the
    agent writes the more-custom modern-stack code at low cost (trimcrae, 2026-07-04).** The residual cost of
    "more custom" is *validation-correctness* risk (a hand-rolled restraint/standard-state bug silently corrupts
    the number), mitigated by composing openmmtools' *tested* primitives and validating against a known
    benchmark **or** the existing Yank ΔΔG.
  - **Cost caveat (keep honest):** agent-cheap coding removes the *engineering* cost, NOT the *compute* cost.
    Running the modern stack as a **second engine on the SAME candidate** still ~2× the GPU — so cross-engine
    reproduction stays a **conditional capstone** (method-watch: "if the ΔΔG is contested"). But for a **NEW
    candidate** the modern stack costs ~nothing extra (you run FEP once regardless) — so there it is a clear win.
- **🛑 VALIDATE A FAN-OUT GPU FLEET ON ONE SHARD BEFORE SCALING (trimcrae rule, 2026-07-03).** For any job that
  fans out N parallel GPU shards (the FEP fleet; any future spot fleet): run `n_shards=1` first, confirm it
  reaches the real work, THEN launch all N. A failed env/wiring test on 8 shards costs 8× for the same
  information. The per-unit S3 checkpointing means the validation shard's completed units are NOT wasted — the
  full fan-out `resume`s from them. **Rung ladder:** `mode=smoke` (spot + checkpoint plumbing, no MD, no heavy
  env) → **`n_shards=1` real** (builds the heavy MD conda env, imports the MD stack, does first windows) →
  `n_shards=8`. **The `n_shards=1` rung is essential because `mode=smoke` deliberately skips the heavy MD env**
  (`entry_fep.py` `--smoke` path), so smoke passing tells you NOTHING about whether the MD env builds/imports.
  - **The FEP env bug this caught (2026-07-03).** The full 8-shard fleet failed twice (~$3, all fail-fast in
    ~13 min) with `module 'numpy.dtypes' has no attribute 'StringDType'` while importing openmm/openmmtools/
    pymbar. Misdiagnosis #1: "numpy < 2 in the env" → pinned `numpy>=2` (didn't help). **Real cause:** the `fep`
    conda env *did* have numpy 2 (scipy 1.17 / pandas 2.3 in the solve force it), but the SageMaker PyTorch
    **base container's `PYTHONPATH`** pointed at its own site-packages (numpy 1.x), and `conda run -n fep`
    inherited that `PYTHONPATH`, so `import numpy` resolved the base 1.x (no `StringDType`) instead of the fep
    env's 2.x. **Fix:** in `entry_fep.py`, clear `PYTHONPATH` (`fep_env["PYTHONPATH"]=""`) for the `conda run`
    subprocess — the local modules still import via `cwd` (`sys.path[0]`). **Lesson:** `conda run` does NOT
    isolate `PYTHONPATH`; always clear it when the base container may leak packages. Diagnostics used:
    `fep-status-aws.yml` (describe training-job status + `FailureReason` + CloudWatch stdout of the first
    failed shard) and `fep-stop-aws.yml` (StopTrainingJob kill-switch — the generic `stop_sagemaker_jobs.py`
    only stops *Processing* jobs, not *Training*).
- **🛑 CHECKPOINT + DURABLE (CONTINUOUS) UPLOAD ON ANY RUN WHOSE RUNTIME YOU'RE GUESSING (trimcrae standing
  rule, 2026-06-29).** Repeated wasted-GPU-hours incidents all came from the same shape: launch a job with a
  *guessed* wall-clock timeout and no durable checkpoint, so a timeout/crash discards EVERY completed unit of
  work and forces a full re-run. **Before launching ANY long/GPU SageMaker job, all four must hold:**
  1. **Incremental checkpoint** — the driver writes partial results to `OUTPUT_DIR` after *each unit*
     (per ligand / frame / candidate / window), NOT only at the end.
  2. **Continuous upload** — the `ProcessingOutput` uses `s3_upload_mode="Continuous"` so those checkpoints
     reach S3 *as they are written*. Default **EndOfJob uploads ONLY on a clean (exit 0) finish**, so a
     timeout (exit 124) or crash → job `Failed` → **nothing uploaded, all partial work lost** (this is the
     MM-GBSA 20×3 incident, run 28391025615: the per-ligand checkpoint existed but EndOfJob + non-zero exit
     meant it never landed in S3; fixed in `entry_mmgbsa.py` / `nr4a3_mmgbsa_sagemaker.py`).
  3. **Right-sized, configurable timeout** — the overall wall-clock cap is an *input* scaled to the work
     (N units × per-unit cost) with generous headroom, never a hardcoded guess. The real fast-fail guard is a
     **per-unit timeout** (e.g. SIGALRM per leg), so the overall cap can be loose without risking a silent hang.
  4. **Treat the partial as the deliverable** — on hitting the cap, read the partial S3 checkpoint (via the
     `report-*` workflow) and decide from it; only raise the cap + re-run if too few units finished. Never
     re-run blind. **Apply this pattern to every GPU pipeline (release, metad, matrix, mmgbsa, denovo, ternary,
     FEP).** The metad set already does continuous upload + resume — mirror it.
- **💰 HOW MANAGED-SPOT BILLING ACTUALLY WORKS — THE SAVINGS IS IN THE *HOURS*, NOT THE RATE (verified against
  AWS docs + real job data, 2026-07-09; documented because a session mis-read the bill and wrongly concluded
  "spot cost more than on-demand").** A recurring confusion: the bill's `SpotTraining` line shows a **per-hour
  rate** that can look **equal to or HIGHER than** the on-demand rate — e.g. 2026-07 Ohio bill:
  `$1.4084 per hour for SpotTraining ml.g5.xlarge` vs `$1.2575 per Training ml.g5.xlarge hour` on-demand. **Do
  NOT conclude "no discount" from that.** Managed-spot savings do **not** live in the rate — they live in the
  **billed hours**:
  - **AWS bills you at (≈)the on-demand rate, but ONLY for `BillableTimeInSeconds`** — and billable time
    **excludes the compute reclaimed by spot interruptions** (AWS eats it). `BillableTimeInSeconds` is defined by
    AWS as "the absolute wall-clock time" billed; it is *less than* `TrainingTimeInSeconds` (the gross training
    time) whenever the job was interrupted.
  - **AWS's own savings formula:** `savings% = (1 − BillableTimeInSeconds / TrainingTimeInSeconds) × 100`. AWS
    explicitly calls this "the savings from using managed spot training," i.e. it IS your discount vs on-demand.
  - **Empirical (this account, 2026-07-09):** every recent g5.xlarge spot job billed **~1/3** of its training
    time → **realized 59–68% savings**, right in the "60–70%" range. So the "$102 SpotTraining" line is
    **already ~65% off**: those 72.6 billed hours are the *reduced* number; on-demand would have billed the
    full ~207 training-hours (~$260). **Spot saved ~$160 on that line — it did NOT cost more.**
  - **The trap to avoid:** comparing the SpotTraining meter's $/hr to the on-demand $/hr. That comparison is
    meaningless — the discount is delivered as fewer billed hours, so always compare **BillableTime vs
    TrainingTime**, never rate vs rate.
  - **Ironic corollary:** a worse spot-capacity crunch (more interruptions) yields a *higher* savings% (more
    reclaimed time AWS doesn't bill) — you pay in wall-clock, not dollars. So a tight-capacity month is not a
    reason to abandon spot; the "default everything to spot" rule stays correct.
  - **How to CHECK realized savings (do this instead of guessing):** run the read-only
    **`list-sagemaker-aws.yml`** workflow with input **`mode=savings`** (optional `instance_filter=ml.g5.xlarge`).
    It calls `describe_training_job` on recent completed/stopped jobs and prints `billable_h`, `training_h`, and
    `savings%` per job (added to `list_sagemaker.py`, 2026-07-09).
  - **Minor real footnote (not the main story):** in us-east-2 the `SpotTraining` g5.xlarge meter references the
    "Accelerated Computing" price book (**$1.4084**) while plain on-demand `Training` uses the cheaper "Compute
    Optimized" book (**$1.2575**) — a ~12% higher *reference* rate on spot, but it is dwarfed by the ~65% hours
    discount, so spot is still far cheaper net.
  - **Other line items on the same bill worth knowing (2026-07):** **S3 Tier-1 requests ~$14** (2.75M PUT/LIST —
    driven by the per-unit *continuous checkpoint upload*; this is the cost of the checkpoint-safety rule and is
    intentional — do NOT reduce checkpoint frequency to save it) and **KMS ~$6** (2M requests — SSE-KMS charges
    one KMS call per encrypted S3 object op). The KMS line is the one easy win: **enable S3 Bucket Keys** on the
    SageMaker bucket (cuts KMS request traffic up to ~99%). **Confirmed 2026-07-09** (one-off audit): objects in
    `sagemaker-us-east-2-<acct>` are `aws:kms`-encrypted with `bucketKey=None` (so Bucket Keys WOULD help), but
    the **CI user `nr4a3-ci-submitter` lacks `s3:Get/PutEncryptionConfiguration`**, so CI can't apply it. Fix is
    a **one-time bucket-owner action** (trimcrae, ~30 s): `aws s3api put-bucket-encryption --bucket
    sagemaker-us-east-2-<acct> --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryption
    ByDefault":{"SSEAlgorithm":"aws:kms"},"BucketKeyEnabled":true}]}'` (or Console → bucket → Properties →
    Default encryption → Bucket Key = Enable). Not kept as tooling since CI can't execute the fix; the command
    above is the whole remediation.
- **🛑 GPU runs cost money — ASK FIRST (trimcrae standing rule, 2026-06-28).** Before dispatching ANY new
  GPU/SageMaker run (anything that spins up a `ml.g5.*` / GPU instance — metad, matrix, MM-GBSA, FEP,
  release, ternary, warhead, calibration), present the user a decision pop-up (`AskUserQuestion`) with a
  **cost estimate** and the **payoff value**, and let them choose. Do NOT auto-launch GPU jobs under the
  "drive autonomously" authorization — that authorization covers the pipeline logic and commits/merges, NOT
  spending on new GPU runs. (Read-only/CPU GitHub-Actions jobs — `verify-aws`, `report-*`, the stop
  workflows — do not need this; they don't start a GPU instance.) **Rough cost (ml.g5.xlarge SageMaker,
  us-east-2, ~$1.4/h, billed on actual runtime):** a ~25 min job (matrix / optimized MM-GBSA) ≈ **$0.5–0.7**;
  a 30 ns metad (~9–10 h) ≈ **$13–15**; selectivity **FEP** (~1–3 weeks serial) ≈ **hundreds of $** — always
  the one to flag hardest. Quote a number + payoff in the pop-up; if unsure, say so and give a range.
- **metad is now multi-target:** `gpu-metad-aws.yml` takes `target=NR4A3|NR4A1|NR4A2` (+ optional
  `output_prefix`, default `<target>-metad`). Paralogue LBD trim + Pocket-5 CV residues are mapped to the
  NR4A3 reference by BLOSUM62 alignment at runtime (fail-loud + audit log + the initial-Rg pre-flight).
  One pipeline builds the whole family for the matrix.
- **SageMaker MaxRuntime must fit the run (incident 2026-06-27):** a 30 ns metad needs **~9-10 h of MD**
  at NR4A LBD speeds (~80 ns/day). The old **8 h** `MaxRuntime` default **killed NR4A2 (and a first NR4A1)
  before the script finished + uploaded → EMPTY S3 prefix, run wasted** (SageMaker uploads
  `ProcessingOutput` only on clean completion in EndOfJob mode). **Fixed:** default `MaxRuntime` raised to
  **20 h** (it's a CEILING — billed on actual runtime, so headroom is free), AND the restart set now
  streams to S3 in **`S3UploadMode="Continuous"`** (the metad writes checkpoint/HILLS/DCD/system/state to
  `OUTPUT_DIR`), so an interrupted run is **resumable from S3** (`resume_from=auto`) — verified live
  (checkpoint+HILLS+system+solvated in `nr4a1-metad/` mid-run). **Always confirm a run via S3
  (`verify-aws.yml`), not GitHub.**
- **GitHub 6 h job cap (separate, harmless):** the metad submitter uses `wait=True`, so the GitHub
  *wrapper* is cancelled at 6 h — but the SageMaker job **survives and finishes on AWS** to its MaxRuntime.
  Confirm via S3, not GitHub status. (Resume-chained <6 h segments are now possible via the continuous
  checkpoint set, if ever wanted; not needed with the 20 h ceiling.)
- **Stopping GPU:** cancelling a GitHub run does NOT stop the SageMaker job. Use **`sagemaker-stop-aws.yml`**
  (`job_prefix=<base-name>`) which calls `StopProcessingJob`.
- **S3 layout (`s3://<default-bucket>/...`):** `nr4a3-metad` = 30 ns outputs (trajectory, `fes.dat`,
  HILLS/COLVAR, and the checkpoint/restart set `metad_system.xml` / `metad_checkpoint.chk` /
  `metad_state.xml` / `metad_manifest.json`); `nr4a3-calibration`; `nr4a3-metad-pocket-30ns` /
  `nr4a3-metad-fes2` = analyses; `nr4a3-handle-facing` = handle-facing output (after Step 0);
  `nr4a3-warhead` = warhead output (after you run it).
- **Extending the metad** (if ever needed for a converged F(Rg)): `gpu-metad-aws.yml` with
  `resume_from=auto` continues from the saved checkpoint — but only if CV/metad params are unchanged
  (the manifest guard enforces this).
- **Release run (`nr4a3_md_release.py`) — RAN 2026-06-29. TWO results; the corrected one is cautiously
  POSITIVE.** First a NaN-on-step-1 bug had to be fixed (seeded unbiased dynamics from the strained
  metad frame with **no energy minimization** — added `minimizeEnergy(5000)`). Then:
  - **Run A — WRONG FRAME (run 28339743810):** seeded the **max-Rg frontier (0.984 nm, the ~38 kcal/mol
    opening edge)** via the old `argmax` default. Minimization kept it open (0.984→0.980) but 5 ns unbiased
    dynamics **collapsed** it (`end 0.782, mean 0.784, frac-near-open 0.00`). **This is the worst-case frame
    and collapsing it is near-expected — it does NOT condemn the pocket** (trimcrae's catch: we'd tested the
    high-energy edge, not the realistic target). Stopped after replica 0.
  - **Run B — CORRECT FRAME (run 28342282658), the one that matters:** seeded the **low-energy DRUGGABLE
    frame (Rg 0.717, fpocket 0.80, ~0.76 kcal/mol)** via the new `TARGET_RG=0.717`. Result: **METASTABLE by
    Rg** — `end 0.754, mean 0.759, frac-near-seed 1.00, mean |drift| 0.042 nm`. It held the full 5 ns, the
    opposite of Run A. (Minimization moved 0.717→0.748 first, so it settled at ~0.755.)
  - **DRUGGABILITY of the metastable state — DONE (mdpocket on `release_rep0.dcd`, runs 28344732143 /
    28345138975, output `s3://<bucket>/nr4a3-release-pocket`). POSITIVE, as a BREATHING/cryptic site:** over
    the unbiased release trajectory the orthosteric pocket scores `max=0.842, mean=0.262, min=0.002,
    frac≥0.5 = 0.24, frac≥0.53 = 0.20` (static 0.495). So it is druggable in **~24% of unbiased frames**
    (1 in 4 clear 0.5; 20% clear the 0.53–0.68 drug-bound band; peak 0.842 > the band), at CV Rg ~0.737 —
    i.e. **spontaneously, thermally druggable a quarter of the time, with NO metadynamics bias.** It is NOT
    always-open (mean 0.262 < 0.5): a **dynamic/cryptic pocket requiring induced-fit / conformational
    selection** (the norm for NR cryptic sites, cf. de Vera 2019 Nurr1). This clears the pre-registered
    "≥5% of frames ≥ D*=0.53" bar (20% here) — and unlike the original metad number, it is on UNBIASED
    dynamics, so it is *not* a bias artifact.
  - **METASTABILITY — CONFIRMED 3/3 (triplicate, run 28343901058, DONE 2026-06-29):** all three independent
    velocity seeds held near the seed Rg for the full 5 ns — replicas mean Rg 0.741 / ~0.74 / 0.732, every
    one frac-near-seed 1.00, **mean |drift from seed| 0.025 nm**, verdict "3/3 PERSISTENCE → thermally
    metastable." No collapse in any replica. (Live Rg streaming let us watch all three hold in real time.)
  - **Net verdict (2026-06-29): the cryptic-pocket case is REVIVED — as an induced-fit druggable site, not a
    static pocket.** Seeded at the correct low-energy frame, the pocket is (i) **metastable (3/3 replicas held
    5 ns unbiased, drift 0.025 nm)** and (ii) **druggable ~24% of unbiased frames** (frac≥0.5 0.24, ≥0.53
    0.20, peak 0.842; static 0.495). The premature "Gate 3 FAILS" came from testing the wrong (max-energy)
    frame. **Honest scope:** this supports a *conformational-selection / induced-fit* warhead (bind &
    stabilise the ~24% druggable conformations), NOT a permanently-open pocket. The matrix / MM-GBSA / FEP /
    de-novo work therefore has a real foundation, but should be framed as targeting a *dynamic* pocket
    (dock/score against the druggable sub-ensemble, not one static frame).
  - **Next, before FEP / de-novo spend (for trimcrae):** re-pick the docking/MM-GBSA receptor as a
    *druggable UNBIASED release frame* (Rg ~0.737, fpocket ≥0.5 — extract from `release_rep*.dcd`) rather than
    the biased metad max frame, so all downstream work uses a thermally-real, druggable conformation. Then the
    matrix selectivity + MM-GBSA verdicts should be re-confirmed on that receptor before any FEP.

## Open items (not blockers for the warhead)
- [ ] **Report 0.931 as a distribution, not just a max (red-team F2).** The headline is the peak over 600
      frames (extreme value). In the writeup/figures lead with the *fraction of opened frames ≥ D\*=0.53*
      (pre-registered ≥5% bar, met) + the median of the druggable cluster, with 0.931 as the peak. (A
      bespoke fpocket negative control is **not** needed — fpocket druggability is standard and the §2.1
      panel, incl. the occluded 1OVL, already anchors it; the biased-vs-physical question is the release
      run's job, below.)
- [~] **Release run = the Gate-3/Gate-1 closer — RAN 2026-06-29; WRONG frame collapsed, CORRECT frame is
      metastable; druggability check in flight.** Run A (max-Rg 0.984 frontier) collapsed (expected — wrong
      frame). Run B (low-energy druggable 0.717) is **metastable by Rg** (held 5 ns, frac-near-seed 1.00). But
      it settled at ~0.755 (≈ closed ref), so the decisive question — is the metastable state still
      *druggable*? — is being answered by the running mdpocket job (+ a triplicate). See the Release-run entry
      above. **Still gates FEP + de-novo: do NOT launch until the druggability check resolves.**
- [x] Harden the metad submitter against interruption — DONE 2026-06-27: 20 h MaxRuntime ceiling +
      continuous S3 checkpoint upload (resumable). The 6 h GitHub-wrapper cancellation is now harmless.
- [x] Opened-frame handle-facing confirmation — **DONE** (CONFIRMED 2026-06-26, run 28249776934; mean
      5.0/7 handles facing, T407/R412 the exceptions). Result written into paper §2.2/§5 and the
      reconciliation Gate-2/3 rows.
- [x] Fix `nr4a3_md_release.py` startup crash (AF-fetch regression) — DONE; pending a GPU validation run
      for the orthogonal metastability confirmation (optional, not a blocker).
- [ ] (optional) Converged longer metad to put a precise number on the full free-energy profile.
- [x] Verify "[…to confirm]" reference locators — DONE 2026-06-26 via `verify-refs.yml` §7 (Crossref +
      Europe PMC): resolved PMC4535767 (Lanig, PLoS ONE 2015), Munoz-Tello (J Med Chem 2020), and
      corrected the NR4A3–MYB paper to Lee et al. 2020 (Cancers), not Haller. DOIs added to paper +
      reconciliation + broader-indications. Remaining: a few volume/page numbers from the primary record.
