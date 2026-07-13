# DeepTernary qualification protocol — Option A* (final reviewer-AI verdict, 2026-07-13)

**Status:** ADOPTED as the governing protocol for whether/how DeepTernary enters the NR4A3 ternary-generation
stage. Supersedes the earlier bare "evaluate DeepTernary" note in `method-watch.md`. Origin: final AI-reviewer
verdict on the DeepTernary-vs-current-plan writeup (routed by trimcrae, 2026-07-13).

DeepTernary = Li et al., *Nat. Commun.* 2025, 16:5514 (arXiv 2502.18875); GitHub `youqingxiaozhua/DeepTernary`,
**Apache-2.0**. SE(3)-equivariant GNN ternary-structure predictor for PROTAC/molecular-glue complexes; trained
on **TernaryDB (~22k two-protein/one-ligand PDB complexes, known PROTACs/MGDs EXCLUDED)**.

---

## Decision: Option A* (adopt as a conditional, orthogonal proposal generator)

- **Run Boltz AND DeepTernary as complementary architecture GENERATORS.** Take the **union** of physically
  admissible pose clusters from both.
- **Concordance is a WEAK robustness annotation, NOT a hard acceptance filter.** Record Boltz↔DeepTernary
  concordance only to influence **which architectures enter expensive MD first** — never to discard a plausible
  architecture that only one generator produced.
- **Keep ALL affinity / cooperativity / paralogue-selectivity / linker-strain / ubiquitination judgments in the
  existing physics-based Stage D, behind the NR-V04 functional gate.** DeepTernary scores (incl. PAE, BSA) do
  **NOT** enter the ranking function `S_d`.
- **Do NOT replace Boltz** (Option B unsupported by current evidence — see "why" below).
- **Option C (skip)** remains defensible *only* if preparing credible binary poses + receptor ensembles for
  DeepTernary would consume disproportionate engineering effort.

### Why A*, not B (replace)
DeepTernary is **more conditional than "ternary predictor" implies**. In PROTAC mode it takes the two protein
structures **plus pre-positioned/docked warhead and E3-anchor binary poses**, then predicts the PROTAC
conformation + relative protein placement. Consequences for us:
1. It does **not** solve an uncertain NR4A3 cmpd-19 binding mode — it **propagates the assumed binary pose** into
   the ternary proposal.
2. It treats proteins as **rigid bodies** → **receptor-frame selection stays an external responsibility** (no
   induced fit / helix rearrangement). Acute here because **8XTT is an unliganded solution-NMR ensemble** (100
   calculated, 20 deposited low-energy conformers; **not** an equilibrium population; **no** cmpd-19 pose). So
   production needs an **outer loop over receptor frames × independently-justified warhead poses**.
3. Headline DockQ is **best-of-many sampling**, not reliable top-1 selection: ~40 seeds/conformers,
   **best-of-40 DockQ ≈ 0.65**, but **PAE-selected top-1 ≈ 0.32 (repro) / ~0.4 (main)**; mean top-ranked ligand
   RMSD **3.43 Å, 43 % < 2 Å**. → **PAE is NOT a physical confidence/energy; never compare it across compounds.**
4. AF3-superiority evidence is thin (clean comparison = **3** post-training PROTACs). Three cases do not establish
   superiority on a **previously-untested nuclear-receptor LBD** system.

DeepTernary is valuable **because it is different enough to add proposals**, not because it has earned sole authority.

---

## Cross-method concordance — legitimate use vs false-confidence boundary

**Legitimate:** architecture stability under two different inference procedures, *conditional on the supplied
receptor conformers and binary ligand poses* — e.g. does a similar E3-vs-NR4A orientation recur? are the same
interface patches / linker trajectories reselected? is a pose family robust enough to fund MD first?

**Does NOT independently validate:** ternary cooperativity; active-vs-inactive VHL epimer discrimination;
NR4A3-vs-NR4A1/2 degradation selectivity; linker energetics; lysine transfer; productive residence times. Both
models learn from **static PDB geometry** and can be driven to the same answer by **shared receptor frames,
attachment vectors, and binary poses** → agreement may reflect a shared input assumption, not biological truth.

**Encoding:** keep concordance in a **separate provenance/robustness field**, NOT inside `S_d`:
`R_gen ∈ {Boltz-only, DeepTernary-only, cross-method-recurring}`. Use `R_gen` to **allocate simulation effort**;
`S_d` stays purely physical/functional.

**Concordance definition (do NOT use whole-complex RMSD alone).** Two architectures are concordant only if they
share MOST of: (1) similar POI-relative E3 rigid-body orientation; (2) similar E3–POI interface contact
fingerprint; (3) same receptor + E3 surface patches; (4) compatible attachment-vector + linker topology;
(5) preserved intended binary warhead + anchor poses; (6) no major protein–protein / protein–linker / intraligand
clashes. **Calibrate thresholds on crystal-structure controls BEFORE seeing NR4A3 results.** **Preserve ≥1
physically-admissible method-unique cluster from each generator** through initial relaxation, else concordance
becomes an unintended mode-collapse mechanism.

---

## Qualification sequence (all cheap; GNN inference + relaxation, NO production MD)

**1. Software & provenance qualification.** Freeze: repo commit; pretrained checkpoint; environment + RDKit
version; input-prep scripts; random seeds; model/DB versions. Record dependency + redistributed-data terms in the
project SBOM (Apache-2.0 code; paper states academic/personal/commercial availability). **Reproduce ≥1 released
example** before any scientific evaluation.

> **STEP-1 SBOM / PROVENANCE FROZEN (2026-07-13):**
> - Repo: `github.com/youqingxiaozhua/DeepTernary` — pinned commit **`827821dccca31a5918bd0355e2d6bf70c072b6dd`**
>   (2025-11-29). **License: Apache-2.0** (confirmed in-repo).
> - Runs on **CPU** (`predict_cpu.py` / `predict.py --device cpu`) — no GPU needed for qualification → **free CPU
>   GitHub-Actions runner**. Env: Python 3.10, `mmengine==0.10.3`, `mmcv-lite==2.2.0`, `rdkit==2023.9.3`,
>   `biopandas==0.5.1`, `dgl==2.3.0`, `POT==0.9.4`, `torch==2.3.1`. **CAVEAT:** upstream `requirements.txt` pins
>   **CUDA** wheels (`torch/dgl +cu121`); the CPU harness swaps in CPU wheels (`torch==2.3.1` cpu index +
>   `dgl==2.3.0` from the torch-2.3 CPU wheel repo, remaining reqs minus the cu121 lines).
> - Pretrained checkpoint + PROTAC unbound structures: release **v1.0.0 `output.zip`**
>   (`.../releases/download/v1.0.0/output.zip`). TernaryDB (for the leakage audit, risk #5): release
>   **v1.0.1 `TernaryDB.tar.gz`** (~22k two-protein/one-ligand complexes; PROTAC/MGD test lists inside).
> - Released-example reproduction: single case **5T35_H_E_759** via `predict.py --task PROTAC` (unbound,
>   multi-seed) → per-seed complex PDBs + `summary_<name>.csv` (top-1 = lowest predicted P2 RMSD). Whole
>   PROTAC test set via `predict_cpu.py output/checkpoints/PROTAC` (step-2 metrics).
> - Harness: **push-triggered** workflow `.github/workflows/deepternary-qualify.yml` (runs off this feature
>   branch with no main dependency — the `modalities-run.yml` pattern). Reported DockQ (paper): PROTAC 0.65 /
>   MGD 0.23 best-of-40; **operational top-1 much weaker** — record PAE-top-1 + best-of-40 both (see step 2).
> - **CPU install caveat resolved:** upstream reqs pull NumPy 2.x → rdkit 2023.9.3 crashes (`_ARRAY_API not
>   found`); harness pins **`numpy<2`** last.
>
> **✅ STEP-1 RESULT — PASS (2026-07-13, CI run 29218681617).** DeepTernary installs on a **free CPU GitHub
> runner** and reproduces the released **5T35** PROTAC example: 8 predicted complex PDBs + `summary_5T35-qual.csv`,
> per-seed internal `pred_p2_rmsd` = 1.71/1.73/1.78/1.94/2.54/2.62/2.62/4.89 Å (clash 0 except the 4.89 Å seed at
> 0.10). Install + released-example reproduction confirmed. **Caveat:** `pred_p2_rmsd` is DeepTernary's *internal
> surrogate*, NOT DockQ-vs-crystal — that (+ PAE-top-1 vs best-of-N) is **Step 2** (public crystal controls).

> **STEP-2 MECHANICS MAPPED (2026-07-13, from the frozen clone) — ready to build the subset run:**
> - Benchmark test list = **`data/PROTAC/protac22.txt`** (22 complexes, IDs = `PDB_chainP1_chainP2_lig`, e.g.
>   `5T35_H_E_759`, `6HR2_B_A_FWZ`, `6W8I_D_A_TKY`, `7KHH_C_D_WEP`, `7Q2J_C_D_8KH`, …). Full list captured in
>   session notes.
> - `predict_cpu.py <work_dir>` reads that list, runs **`predict_one_unbound`** (PROTAC) at **SEED_NUM=40**, and
>   **computes DockQ per seed** via `DockQ/dockq_util.cal_dockq` → returns `fnat, irms, Lrms, DockQ` plus
>   `pred_p2_rmsd` (the PAE surrogate), `gt_p2_rmsd`, `sm_rmsd`, `lig_rmsd`. Results are **sorted by
>   `pred_p2_rmsd`** → this gives the **PAE-selected top-1** AND the **best-of-N** the reviewer wants both of.
>   Supports `multiprocessing.Pool(THREAD_NUM)` → use runner cores.
> - **Runtime reality:** 22×40 seeds on CPU is impractical (~hours-to-15h) → **MUST subset to the reviewer's
>   4–6 (≥2 VHL + ≥2 CRBN)** and/or thread it + bump the job timeout.
> - **⚠ INTEGRITY GATE — CLEARED 2026-07-13 (E3 labels SOURCED from RCSB, not guessed).** My memory-based
>   guesses were WRONG on three (6BOY/6BN7 are CRBN not VHL; 6W7O/6W8I are cIAP not CRBN) — hence the gate.
>   Verified E3 per PDB:
>   - **VHL:** `5T35` (BRD4^BD2–MZ1–pVHL:EloC:EloB, Ciulli 2017), `6HAX`/`6HAY` (SMARCA2–PROTAC–VHL),
>     `6HR2` (SMARCA4–PROTAC–VHL).
>   - **CRBN:** `6BOY` (DDB1–CRBN–BRD4(BD1)–dBET6), `6BN7` (CRBN–BRD4, dBET-series).
>   - **cIAP (excluded — not our matrix's E3):** `6W7O`, `6W8I` (BTK).
>   Sources: rcsb.org/structure/{5T35,6HR2,6HAY,6HAX,6BOY}.
> - **STEP-2 SUBSET (5 complexes, 3 VHL + 2 CRBN, spanning BRD4/SMARCA2/SMARCA4):**
>   `5T35_H_E_759` (VHL), `6HAX_B_A_FWZ` (VHL), `6HR2_B_A_FWZ` (VHL), `6BOY_B_C_RN6` (CRBN),
>   `6BN7_B_C_RN3` (CRBN). Run = overwrite `data/PROTAC/protac22.txt` with this list → `predict_cpu.py
>   output/checkpoints/PROTAC`. CI-feasibility: SEED_NUM reduced from 40 → **16 for the first pass** (CPU
>   runtime); report as preliminary best-of-16 + PAE-top-1, and note the seed count honestly (full 40 later
>   if promising). Labelled **SOFTWARE-REPRODUCTION control**, not independent validation (these are in
>   DeepTernary's published benchmark).

> **✅ STEP-2 RESULT (2026-07-13, CI run 29243531774; self-reported via `deepternary-qualify-cache` branch).**
> Ran on CPU (avg 9.3 s/prediction) after fixing 2 bugs the self-report surfaced: released checkpoint nests its
> config in a timestamped subdir → pass `--config deepternary/configs/protac.py --checkpoint .../checkpoint.pth`
> explicitly; and `predict_cpu.py` hardcodes `device='cuda'` → patched to `cpu`. **Preliminary best-of-16**
> (not 40), N=5, **SOFTWARE-REPRODUCTION control** (these are in DeepTernary's own benchmark — NOT independent
> validation).
>
> | Complex | E3 | PAE-top-1 DockQ | Best-of-16 DockQ | RMSD<10 | Acceptable |
> |---|---|---|---|---|---|
> | 5T35 (BRD4) | VHL | 0.66 | 0.83 | 0.88 | ✅ |
> | 6HAX (SMARCA2) | VHL | 0.62 | 0.62 | 1.00 | ✅ |
> | 6HR2 (SMARCA4) | VHL | 0.62 | 0.62 | 1.00 | ✅ |
> | 6BOY (BRD4/dBET6) | CRBN | 0.06 | 0.15 | 0.06 | ❌ |
> | 6BN7 (BRD4) | CRBN | 0.51 | 0.51 | 0.63 | ✅ |
> | **mean** | | **0.49** | **0.54** | **0.71** | **0.8 rate** |
>
> **Reading (honest):** (a) best-of-16 mean 0.54 is in the paper's best-of-40 ~0.65 ballpark (fewer seeds,
> tiny N) → install/pipeline reproduces. (b) On THIS subset the PAE-top-1 (0.49) is close to best-of-N (0.54)
> — the internal `pred_p2_rmsd` ranking held up better than the reviewer's ~0.32–0.4 caution warned (but N=5,
> don't over-read). (c) **VHL recovered well (0.62–0.83); CRBN mixed — 6BOY fails outright (0.06/0.15).** So
> DeepTernary is not uniformly reliable even on its own benchmark; per-case failures happen (exactly why we
> keep it architecture-triage-only, union-of-clusters, never a ranker). NEXT: Step 3 = prospective-like BLIND
> controls (the test that actually resembles NR4A3); optionally re-run this subset at 40 seeds if worthwhile.

**2. Installation-reproduction controls (label as SOFTWARE-REPRODUCTION, not independent validation).** Use
**4–6 public crystal ternaries**: **≥2 VHL, ≥2 CRBN**, preferably +1 other E3 class if it may enter the matrix; mix
rigid and difficult linker/interface geometries. (May overlap DeepTernary's 22-structure benchmark / "unbound"
protocol — label correctly.) For each, report: **PAE-selected top-1 DockQ; top-5 success; best-of-40 DockQ; rank
of first acceptable pose; ligand + endpoint RMSDs; interface-contact recovery; clash counts; #/diversity of pose
clusters.** Reporting only best-of-40 overstates operational performance.

**3. Prospective-like blind controls (the test that actually resembles NR4A3).** ≥2–3 ternaries **not** in
DeepTernary's train/val/test, ideally deposited after its cutoff. Prepare **without consulting the native ternary
pose**: separate monomer/binary structures, dock warhead + E3 anchor independently, blind the native interface
until predictions are frozen. (DeepTernary peer review flagged dataset similarity, prospective monomer
generalization, ligand-pose evaluation, and absence of induced fit — so this matters more than adding familiar
benchmarks.)

> **STEP-3 FOUNDATION BUILT (2026-07-13) — leakage audit + sourced post-cutoff candidate finder.** Selecting a
> valid blind control requires two things first, and both are done from PRIMARY data (integrity gate: no
> memory-based structure facts): (A) the **exclusion set** — every PDB ID DeepTernary may have seen — and
> (B) a **sourced list of degrader-ternary structures deposited AFTER** that horizon. Built:
> `research/modalities/deepternary_blind_controls.py` (pure stdlib) + `.github/workflows/deepternary-blind-controls.yml`
> (push-triggered CPU runner) + `tests/test_deepternary_blind_controls.py` (5 passing, parser/regex/provenance).
> The workflow clones DeepTernary@`827821d`, downloads the v1.0.0 release + v1.0.1 TernaryDB, extracts every
> PDB ID from all split/list/manifest files (with per-ID provenance), then via the **public RCSB search + data
> APIs** (reachable from the runner; egress-blocked in-sandbox) computes the max deposit date in the exclusion
> set = the data horizon and enumerates PROTAC/degrader/glue ternaries (≥2 protein entities) deposited after it,
> annotating each with deposit date, protein names, **UniProt-classified E3 identity** (VHL/CRBN/cIAP/… by
> accession, not guessed), and degrader-sized ligands. Output = `deepternary_blind_controls.json` on the
> `deepternary-qualify-cache` branch, with a `shortlist_hint` for curating the final 2–3 controls. **This is the
> foundation, not the blind test itself** — the actual blind prediction (inputs prepped from separate binary
> structures, native pose blinded, DockQ + input-sensitivity sweep per §4) is the next step once controls are
> curated from this table.

> **STEP-3 RUN CLEAN + CONTROLS CURATED (2026-07-13, CI run 29245576499).** A parser bug (training-log
> `vis_data/scalars.json` loss/iteration integers matched a naive PDB-ID regex → false IDs like `1000`) and a
> silently-empty batched GraphQL metadata query were both fixed (parser now skips training logs + requires ≥1
> letter in bare tokens; metadata now via the stable REST data API). Clean result:
> **exclusion set = 4,471 PDB IDs** (committed durable artifact `deepternary_exclusion_set.json`), **data horizon
> = 2023-10-14**, **266 post-horizon degrader-ternary candidates** (0 overlap with the exclusion set), 12 passing
> the E3+degrader-ligand shortlist filter. **Curated 3 blind controls** (`deepternary_step3_controls.json`), all
> post-horizon, all verified NOT in the exclusion set, PROTACs (not glues), spanning VHL+CRBN, with separable
> apo/binary inputs:
> - **9RKC** — VHL / **KRAS G12D** / ACBI4 PROTAC (dep 2025-06-13). **No target-E3-pair training prior** (earliest
>   KRAS-VCB PROTAC 8QVU is 2023-10-18, 4 d after horizon). *Strongest NR4A3-like blind test* (novel pairing + real
>   pose uncertainty). Inputs: KRAS-G12D-GDP apo + VCB apo.
> - **23SR** — CRBN / **CDK2** / cpd B11 (dep 2026-02-16). **No prior.** Second CRBN case (CRBN was the Step-2 weak
>   arm — 6BOY failed 0.06/0.15) with a NanoBiT/GFP reporter-fusion POI (use the CDK2 kinase domain for blind prep,
>   note the tags).
> - **9SAF** — CRBN / **BRD4-BD1** / JQ1-AcQ PROTAC (dep 2025-08-07). **Target-E3-pair prior PRESENT** (6BOY/6BN7
>   dBET are in the protac22 benchmark) → NOT a novel-pair test; a familiar, well-behaved *operational* blind-prep
>   control. Prior noted explicitly.
> Alternates on file: 9N88 (VHL/IRE1), 9YA9 (CRBN/BCL6), 9HYO (VHL/SMARCA2, dual-use w/ the ternary-coop calib
> panel). **Risk-#5 leakage re-check at reveal is still required** (homologues, target-pair priors, scaffold
> analogues; exclusion-set membership is necessary, not sufficient). **Next:** understand DeepTernary's unbound-input
> format from `predict.py`, source separate apo/binary POI+E3 PDBs per control (CI, sourced not guessed), build the
> blind-prep + prediction + DockQ harness, freeze predictions, THEN unseal natives.

> **DeepTernary UNBOUND-INPUT CONTRACT (2026-07-13, CI run 29246136067 read of `predict.py`/`predict_cpu.py`).**
> `predict_one_unbound(name)` reads from `output/protac22/<name>/`; the files a blind-prep must CREATE per control:
> - `unbound_protein1.pdb` — POI, from a structure that is NOT the native ternary.
> - `unbound_lig1.pdb` — the WARHEAD fragment coords in that POI frame (from a POI+warhead binary co-crystal).
> - `unbound_protein2.pdb` — E3, from a non-native structure.
> - `unbound_lig2.pdb` — the E3-ANCHOR fragment coords in that E3 frame (from an E3+anchor binary).
> - `ligand.pdb`/`ligand.sdf` — the FULL degrader (RDKit/`ligand_ideal.sdf` coords, NOT the native bound pose;
>   `auto_download_ideal_sdf` pulls the CCD ideal SDF by comp id).
> - `gt_complex.pdb` — the native ternary; **used ONLY at `cal_dockq(...)` for scoring — kept SEALED until
>   predictions are frozen.**
> Mechanics: `replace_to_unbound_coords` maps the warhead/anchor atoms of the full degrader onto the unbound
> fragment coords, finds each protein's pocket near its fragment (`pocket_cutoff` 6 Å), then predicts the relative
> protein placement + linker (proteins are RIGID; `freeze: protein1`; `random_flip_proteins`). So the blind inputs
> reduce to: **one POI+warhead binary + one E3+anchor binary + the CCD degrader** — the native pose enters nowhere
> except DockQ. Training snapshot is `pdb2311` (Nov 2023) — corroborates the 2023-10-14 horizon.
> **Input-structure sourcing (`--source-inputs` mode + `deepternary-source-inputs.yml`):** queries RCSB by POI/E3
> UniProt (KRAS P01116, CDK2 P24941, BRD4 O60885; VHL P40337, CRBN Q96SW2) for separate binary candidates
> (≤2 protein entities for the POI, ≤4 for the E3, ≥1 ligand), excluding the native → `deepternary_step3_input_candidates.json`
> for human curation of the exact warhead/anchor binaries. Remaining harness (the heavy, iteration-worthy build):
> fragment extraction (warhead substructure ↔ full-degrader atom map for `replace_to_unbound_coords`), the 6-file
> input assembly per control, the multi-seed prediction run, DockQ vs sealed native, and the §4 input-sensitivity
> sweep — to be built + validated on the DeepTernary CPU env (as Steps 1–2 were).

> **STEP-3 STATE (2026-07-13 end-of-session) — FOUNDATION COMPLETE; sourced binaries in hand; blind RUN is the
> next focused build.** Committed + verifiable so far: exclusion set (`deepternary_exclusion_set.json`), curated
> controls (`deepternary_step3_controls.json`), pre-registered execution recipe (above), input contract (above),
> the blind-prep harness (`deepternary_blind_prep.py` + 4 offline tests), and the **sourced per-control binary
> input-candidate table** (`deepternary_step3_input_candidates.json`, CI run 29247191166) — POI+warhead and
> E3+anchor binary candidates each with deposit date + bound-ligand IDs/MW, e.g.:
> - **9RKC (KRAS/VHL):** POI KRAS-G12D+inhibitor binaries `10NU`(A1C6Y 608)/`10JT`(A1C5K 720)/`36OI`(A1AOL 906)…
>   (all GDP/GNP-bound); E3 VCB+VH032-class binaries `7KHH`(WEP 1096)/`7Q2J`(8KH 1012)/`7Z6L`(IEI 1038)….
> - **23SR (CDK2/CRBN):** POI CDK2+inhibitor binaries `1PXI-P`(CK1-8)/`1OIU`(N76)…; E3 CRBN/DDB1 binaries
>   `9DUR`(A1IQT 676)/`9E2U`(RN9 494)….
> - **9SAF (BRD4-BD1/CRBN):** POI BRD4-BD1+inhibitor binaries `4CL9`(IES 552)/`4CLB`(83T)/`4C66`(H4C)…; E3 CRBN
>   binaries as above.
> **The next build (do carefully — trustworthiness > speed; a wrong warhead fragment = meaningless DockQ):**
> (1) **Warhead/anchor MATCHING** — fetch each degrader's CCD SMILES (9RKC `A1JHI` ~970 Da, 9SAF `A1JM8`
> ~739 Da) + each candidate ligand's SMILES, RDKit-MCS to confirm which binary's ligand is a real substructure of
> the degrader's warhead/anchor (verify overlap, don't guess); pick one POI+warhead + one E3+anchor binary per
> control. **⚠ Curation catch (2026-07-13): 23SR's degrader `A1E59` is ~490 Da = GLUE-sized, not PROTAC-sized —
> likely a molecular glue with NO separable warhead/anchor, so it is a POOR PROTAC blind control. SWAP 23SR for a
> proper CRBN PROTAC** with a linker (candidates already sourced: `9YA9` BCL6-CRBN LDD `A1CTU` 628, `9Q03` BCL6
> `A1CM7` 715, or `8RQ9` CRBN+BRD4-BD2 `A1H2F` 824) so the CRBN arm stays a true bifunctional-degrader test.
> The matching step's MW/linker check catches exactly this — verify each degrader is PROTAC-sized + splittable
> before committing a control. (2) Fill `deepternary_blind_prep.py` configs, run prep in the DeepTernary CI env, VALIDATE the 6 input
> files + gt-not-in-predict-dir. (3) Multi-seed `predict_one_unbound` per control → freeze all seeds → DockQ vs
> the sealed native (PAE-top-1 + best-of-N + rank-of-first-acceptable). (4) §4 input-sensitivity sweep. (5)
> Risk-#5 reveal-time leakage re-check. Validate-first on ONE control (likely 9SAF, cleanest inputs) before all 3.

**4. Input-sensitivity test.** For every blind control AND NR-V04, vary: receptor conformer; initial warhead pose;
warhead attachment-vector rotamer; E3 binary structure; protonation/tautomer. Question is not "can 1/40 runs
recover native?" but **"does the native-like architecture survive reasonable input uncertainty, and does the model
expose that uncertainty via multiple clusters rather than a deceptively stable wrong answer?"** Essential because
cmpd-19's NR4A3 binary pose is **not** experimentally fixed.

**5. NR-V04 FUNCTIONAL gate (reframed — see below).** (1) Generate NR4A1/2/3 architectures with Boltz + DeepTernary;
(2) keep generators + downstream analysts blinded to the paralogue outcome where practical; (3) identical
clash/strain/ensemble-prep rules; (4) send the **union** of viable clusters into the existing physics workflow;
(5) require the **complete pipeline — not DeepTernary alone, not generator concordance** — to recover
NR4A1-degradation compatibility + NR4A2/3 counterexamples; (6) include the **inactive hydroxyproline epimer as a
negative FUNCTIONAL control**, explicitly allowing generators to give it a similar geometry.

---

## Step-3 EXECUTION RECIPE — frozen 2026-07-13, BEFORE any control is picked or any native pose is seen

Pre-registered so the blind test stays blind (analogous to `nr4a3-abfe-repair-prereg.md` discipline). Fill the
bracketed control IDs from `deepternary_blind_controls.json` once the audit run lands; do **not** alter any
threshold below after seeing a native structure.

**Control selection (from the audit's `shortlist_hint`).** Pick **2–3** entries that ALL satisfy: (a) NOT in the
exclusion set; (b) `deposit_date` strictly after `deepternary_data_horizon.max_deposit_date_in_exclusion_set`;
(c) a UniProt-classified E3 in our matrix scope (prefer ≥1 VHL + ≥1 CRBN to mirror Step 2); (d) ≥2 protein
entities + a degrader-sized ligand. Record for each the exact native ternary PDB (kept SEALED) and the SEPARATE
binary/apo PDBs used to build inputs. If <2 qualify, widen the search window or record the shortfall honestly —
do NOT relax (a) or (b).

**Blind input preparation (native pose never consulted).** For each control: (1) take the POI from a DIFFERENT
PDB than the native ternary (apo, or bound to the warhead only); (2) take the E3 from a DIFFERENT PDB (apo, or
bound to the E3 anchor only); (3) build the degrader molecule from its 2D chemistry (SMILES/CCD), NOT from the
native bound conformer; (4) supply DeepTernary the two separated proteins + degrader in its "unbound" PROTAC
protocol; (5) freeze predictions (all seeds) to disk BEFORE unsealing the native ternary. The native is used
ONLY to compute DockQ after freezing.

**Metrics (report ALL — reporting only best-of-N overstates operational performance).** Per control:
PAE-selected top-1 DockQ; top-5 success; best-of-N DockQ (state N); rank of first acceptable pose (DockQ≥0.23);
ligand + endpoint RMSDs; interface-contact recovery; clash counts; #/diversity of pose clusters.

**Input-sensitivity matrix (§4), frozen.** For EACH control, run the prediction under each single-variable
perturbation and report whether the native-like cluster survives (not "did 1/N seeds hit native"):
| Axis | Variation |
|---|---|
| Receptor conformer (POI) | ≥2 defensible POI frames (alt PDB / alt chain / minimised) |
| Warhead binary pose | re-dock the warhead into the POI pocket, take top-2 distinct poses |
| Attachment-vector rotamer | rotate the exit-vector torsion to a 2nd low-energy rotamer |
| E3 binary structure | ≥2 E3 frames (alt PDB of the same ligase) |
| Protonation/tautomer | degrader protonation state at pH 7.0 vs a defensible alternate |
Pass = the native-like architecture recurs across a MAJORITY of single-axis perturbations AND the model exposes
residual uncertainty as multiple clusters (not one deceptively stable wrong answer). This maps to **adoption
criteria 3 (prospective-like) + 4 (not catastrophically unstable)**.

**Leakage re-check at reveal.** Before trusting any control, re-run the risk-#5 checks against the sealed native
(homologues, VHL/target-pair priors, celastrol/scaffold analogues, curated benchmark files) — exclusion from the
exclusion set is necessary but not sufficient.

**Honest-null handling.** A control where blind prep is infeasible (no separate POI/E3 structure exists) is
RECORDED as not-runnable, not silently dropped; DeepTernary failing a blind control is a real Step-3 result, not
a bug to engineer around (cf. the 6BOY 0.06 failure in Step 2).

---

## ⚠ NR-V04 REFRAMED — the largest required change

NR-V04 has **no deposited NR4A1–NR-V04–VHL structure** (selective degradation + VHL/proteasome dependence + PLA/
co-IP proximity; ligand designed by docking). Therefore:
- DeepTernary **cannot** be tested for "reproducing the known NR-V04 architecture."
- Boltz↔DeepTernary agreement on NR-V04 = **inter-model agreement, not structural validation.**
- **NR-V04 is the END-TO-END FUNCTIONAL retrospective gate**: does the whole generation+physics+ubiquitination
  pipeline recover the NR4A1-over-NR4A2/3 **degradation outcome**? Make this explicit in the protocol + final report.
- Epimer: failure of a generator to distinguish it geometrically is **not disqualifying** — claiming it *should*
  would repeat the co-fold category error.

*(This correction is propagated into `nr4a3-degrader-strategy-ternary-first.md` → "Gate that still governs
everything".)*

---

## Case-specific risks (must be handled, not hidden)

1. **Binary-pose uncertainty may dominate the generator comparison.** A wrong cmpd-19 pose → internally coherent
   but biologically irrelevant ternary. Run the production matrix over **several independently-supported warhead
   pose families** (not just linker conformers around one pose); track conclusions **conditional on warhead-pose
   family**; a compound favorable **only** under one poorly-supported binary pose gets an explicit uncertainty
   penalty or exclusion from the synthesis matrix.
2. **Nuclear-receptor conformational plasticity** (rigid-body model can't do induced fit). Generate separately from
   **multiple** druggable + design frames; **do not average coordinates across NMR models**; locally minimize each
   assembled ternary; restrained relaxation before interface scoring; require conclusions to survive **>1 defensible
   receptor frame**. Keep **"frame robustness" distinct from "generator concordance."**
3. **Isolated LBD vs EWSR1::NR4A3 context.** An LBD-only ternary can look favorable yet be inaccessible /
   ubiquitination-incompetent in the fusion. Before lysine-presentation scoring, **graft surviving LBD architectures
   into ensembles representing the larger EWSR1::NR4A3 context** and check E3 steric accessibility, linker clearance,
   accessible lysine neighborhoods, disordered/fusion-region interference, target-lysine reachability across plausible
   domain arrangements. Surface this uncertainty in the evidence table, not inside one lysine score.
4. **DeepTernary can't evaluate the full ubiquitination machinery** (models 2 proteins + degrader only; not
   VCB/CUL2/RBX1/E2~Ub or CRBN/DDB1/CUL4/RBX1/E2~Ub). For each surviving cluster, **graft the recruited E3
   subcomplex into multiple full-ligase conformations** and evaluate lysine reachability vs an **E2~Ub transfer
   ensemble**. Predicted **BSA** = descriptive interface QC only (after de-clashing) — **never** a cooperativity/
   degradation proxy (paper notes system-dependent BSA + clash inflation).
5. **Training-set leakage audit — broader than "PROTACs excluded."** NR-V04's ternary can't be a TernaryDB PDB entry
   (no deposited structure), but the blind-control audit must still check for: NR4A1/2/3 entries; close sequence
   homologues; VHL complexes; celastrol / close scaffold analogues; similar target–E3 protein pairs; any curated
   benchmark/example files in the repo. Exclusion of intact degraders ≠ absence of target-family / interface priors.

---

## Adoption criterion — DeepTernary enters NR4A3 production ONLY if ALL hold

1. Installation reproduces released examples within expected variation.
2. PAE-selected top poses **and** top-k ensembles show useful performance on public controls.
3. Succeeds on **prospective-like blinded** structures prepared from genuinely separate inputs.
4. Predictions are **not catastrophically unstable** to modest binary-pose / receptor-frame changes.
5. Contributes **nonredundant physically-admissible clusters** beyond Boltz.
6. The downstream **NR-V04 workflow — not generator concordance alone** — recovers the paralogue-selective outcome.
7. **Full-ligase ubiquitination checks remain downstream and mandatory.**

**Final disposition:** adopt under Option A* as an orthogonal, conditional architecture-proposal engine. Do not
replace Boltz; do not add DeepTernary scores to the degradation-ranking function; do not use Boltz↔DeepTernary
agreement as a hard filter. Biggest plan change: **stop calling NR-V04 a known-architecture structural validation —
it is the functional retrospective test of the whole pipeline.**
