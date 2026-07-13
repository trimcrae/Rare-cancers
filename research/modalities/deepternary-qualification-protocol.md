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
