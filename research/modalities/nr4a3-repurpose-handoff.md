# Handoff — NR4A3 cryptic-pocket drug-repurposing screen (+ RBFE status) — 2026-07-07

Paste this whole file into a new thread to pick up the work. Repo: `trimcrae/Rare-cancers`
(all code below is merged to `main`). Two in-silico threads on the NR4A3 degrader program:

---

## 1. RBFE (primary work — running, no decision needed)

**Question it answers:** is the lead-opt winner **`lo_m0_NCCO_gen`** (denovo_401 + ortho-acetamido) a
*tighter* NR4A3 binder than the reference **`denovo_401`**, and does it stay selective vs NR4A1/NR4A2?
Method: relative binding FEP (OpenFE), **single replicate** (trimcrae decision — escalate to 3 only if the
result lands marginal near the go/no-go line).

**Harness:** `nr4a3_rbfe.py` (engine), `nr4a3_rbfe_sagemaker.py` (submitter), `sagemaker_src/entry_rbfe.py`,
`sagemaker_src/environment-rbfe.yml`, `.github/workflows/gpu-rbfe-aws.yml`. Pure bookkeeping + 7 unit tests in
`rbfe_edges.py` / `tests/test_rbfe_edges.py`.

**State:** smoke shakeout PASSED. Six first-run bugs fixed (input-mount, ligand-record resolution,
replica/window count, old-openfe/pydantic pin, `importlib_resources`, solvent-leg `docked_shared.sdf`). The
**solvent morph leg is running** (`mode=run only_legs=solvent`) to validate the real-MD path.

**Next steps:**
- Track legs: dispatch `gpu-rbfe-aws.yml mode=jobs` → prints each SageMaker leg status + FailureReason.
- When the solvent leg completes clean → dispatch the 3 complex legs:
  `gpu-rbfe-aws.yml mode=run only_legs="" tag=nr4a3-rbfe-401-nccogen receptor_prefix=nr4a3-leadopt-species git_ref=<ref>`
  (all 4 legs; the finished solvent leg resumes from its checkpoint, so no rework).
- When all legs finish → `gpu-rbfe-aws.yml mode=reduce` → ΔΔG_bind per receptor + selectivity
  (`rbfe_edges.selectivity_from_rbfe`, anchored on 401's offset-corrected ABFE) + the anchor-free selectivity change.

**Notes:** env solve is fast now (libmamba, ~9-min job); the ~50-min walls were **spot provisioning waits**, not
env builds — so **no pre-baked image needed**. Cost ~$40–60 spot, ~a day wall (spot-wait dominated). ligand-A
record is `denovo_401_gen`, ligand-B `lo_m0_NCCO_gen`, both in `nr4a3-leadopt-species/docked_<r>.sdf`.

---

## 2. Drug-repurposing screen (**this is the decision to make**)

**Question:** do any existing drugs fit the cryptic NR4A3 orthosteric Pocket-5 (and selectively vs NR4A1/2)?
Approach = the existing selectivity funnel with a drug library as input.

**Library:** `nr4a3-repurpose-candidates.json` — **5,988 drug-like** Broad Drug Repurposing Hub compounds
(desalted, MW 150–600, deduped by InChIKey), with **4 known NR4A modulators flagged as positive controls**
(DIM, isotretinoin, tretinoin, mercaptopurine). Rebuild from source: `build_repurpose_candidates.py`
(downloads the Broad Hub; needs rdkit + network). Sharded into 11×550 + shakeout by `shard_candidates.py`
(`nr4a3-repurpose-shard-00..10.json`).

**How to dock a shard (existing funnel, no new workflow):**
```
gpu-denovo-dock-aws.yml
  denovo_prefix   = cand:nr4a3-repurpose-shard-NN.json   # 'cand:' sentinel → dock a committed JSON, no S3 upload
  output_prefix   = nr4a3-repurpose-matrix-NN
  developable_only= 0
  receptor_mode   = release
  git_ref         = <branch or main that has the shard files>
```
Exhaustiveness auto-defaults to 4 for `cand:` (large-screen) runs. Read results:
`report-matrix-aws.yml output_prefix=nr4a3-repurpose-matrix-NN` (per-drug dock ΔG into NR4A3/1/2 + selectivity
fingerprint: nr4a3_selective / pan_nr4a / anti_targets).

**Progress:** **Wave 1 DONE** — shards 00, 01 (~1,100 cmpds) → `s3://<bucket>/nr4a3-repurpose-matrix-00` and
`-01`. **Shards 02–10 PENDING.** c5.2xlarge Processing quota = 2 → run 2 shards concurrently.
**Reality check:** real drugs dock ~4 h/shard (not the ~1.5 h the small shakeout implied), so the full 6k × 3-
receptor screen is **~24 h background wall, ~$8**. Docking scores are HYPOTHESES, not affinities — any hit then
needs multi-snapshot MM-GBSA + decoy null + selectivity (the `mmgbsa-aws.yml` tier) before it means anything.

### ⇒ DECISION (pick one):
1. **NR4A3-only triage first (recommended).** Re-dock all ~6k into *just* the cryptic pocket (⅓ the compute,
   ~8–9 h), rank by pocket fit, then run the full 3-receptor selectivity + MM-GBSA on only the top ~250.
   Fastest path to "does any drug fit the pocket"; selectivity comes on the hits.
   *Impl:* add a receptor-subset ("nr4a3 only") mode to `nr4a3_matrix.py` so the funnel docks one receptor.
2. **Continue full 3-receptor waves.** Dispatch the remaining 9 shards (2 at a time) as-is — every compound
   gets a full selectivity fingerprint. ~24 h background, ~$8, no code change.
3. **Shrink library first.** Pre-filter ~6k → ~1–2k most pocket-relevant drugs (size/shape/property match to
   401 / lo_m0_NCCO), then full 3-receptor dock. Faster + cheaper; may miss unusual scaffolds.
4. **Shelve it.** Park the screen (pipeline + wave-1 data kept); all effort on the RBFE / degrader program.

*Operating rules that apply (from CLAUDE.md): times in US Eastern; no wet-lab steps; wait out spot capacity,
never switch to on-demand; checkpoint + continuous-upload any long job; the 2.5 MB of library JSON in this
commit is regenerable from `build_repurpose_candidates.py` and need not live in git long-term.*
