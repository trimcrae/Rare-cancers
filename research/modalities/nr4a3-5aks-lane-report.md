# LANE 16 — RUNG 5a-KS, the ligand-side causal kill-switch

> **What this rung is.** The preregistered Tier-3 test of the design ladder
> ([paper §5](../manuscripts/nr4a3-degrader-paper.md)): a ligand-side double difference over one matched
> molecule pair, asking whether a **designed element** *creates* paralogue discrimination.
>
> ```
> S = ddG_coop(d0 -> d | NR4A3) - ddG_coop(d0 -> d | NR4A1)
> ```
>
> `d0` and `d` differ by **one atom** — an aromatic C-H becomes N (phenyl -> 3-pyridyl) on a wedge aimed at
> **T407**, which is Leu in NR4A1 and Val in NR4A2, so the H-bond donor NR4A3 presents is absent in *both*
> paralogues. The pair was designed and RDKit-verified by RUNG 5b and is read from
> [`nr4a3-linker-design.json`](nr4a3-linker-design.json) → `matched_pair_for_rung_5a_ks`; **no SMILES is
> hand-typed anywhere in this lane, and a test enforces that.**
>
> **Why it matters beyond its own answer:** running it retires the paper's own stated limit **§2.10(d) "The
> causal test has not been run."**

**Costs are not restated here.** [pricing.md](../compute/pricing.md) owns them; the ladder and the gate live
in [nr4a3-program-map.md](../manuscripts/nr4a3-program-map.md).

---

## 1 · The algebra, and why this costs two legs instead of six

Each species' cooperativity difference is itself a difference of environments:

```
ddG_coop(d0 -> d | X) = dG_ternary(X) - dG_binary
```

The **binary** leg is the construct + CRBN with **no target chain**. It is therefore the *same physical leg*
for both species — the molecule and the E3 are identical and the paralogue is simply absent. Substituting:

```
S = [dG_tern(NR4A3) - dG_bin] - [dG_tern(NR4A1) - dG_bin]
  =  dG_tern(NR4A3) - dG_tern(NR4A1)
```

**The binary leg cancels EXACTLY — algebraically, not approximately — and so does the solvent leg beneath
it.** That is the whole reason this rung is two ternary legs rather than a full cycle per species.

It is also a trap, which is why [`nr4a3_5aks_reduce.py`](nr4a3_5aks_reduce.py) **refuses** rather than warns:
a well-meaning "let's complete the cycle" pass that measures the binary leg and subtracts it from *both* arms
computes the same number with strictly more noise, and one that subtracts it from **one** arm computes
something that is not `S` at all — and nothing downstream could tell.

## 2 · Sign convention, fixed in advance

Each leg's `dg_morph_kcal` is `dG(d0 -> d)` in that environment; positive means the pyridyl endpoint `d` is
disfavoured relative to the phenyl control `d0`.

| reading | meaning |
|---|---|
| **S < 0** | the wedge is better tolerated on NR4A3 → discrimination **in the designed direction** (T407's hydroxyl accepts the pyridyl nitrogen; NR4A1's Leu363 cannot) |
| **S ≈ 0** | the marginal wedge is absent. **Preregistered as the LIKELY outcome, and NOT a stop** — it means the claim rests on the categorical axis, which LANE 13 tested against paralogue dynamics and found intact |
| **S > 0** | the wedge is **anti-selective** — worse on NR4A3 than on the paralogue |

**The expectation, recorded before the run:** the aligned paralogue residues are hydrocarbon and simply
cannot donate, so the designed pair offers NR4A3 a *gain* rather than imposing a paralogue *penalty* —
roughly one partly-buried hydrogen bond, ~0.5–1.5 kcal/mol, against a best-case resolvable ~1.12. A null is
the expected result and must not be written up as a failure; paper §5(b) fixes that reading in advance.

## 3 · The pipeline, end to end

| step | where | cost |
|---|---|---|
| **pair + plan** — read RUNG 5b's artifact, refuse unless it really is the one-atom aza-scan | `nr4a3_5aks_cofold.py`, CI | $0 |
| **co-fold** — Boltz-2, CRBN + NR4A{3,1}-LBD + the construct | Vast, via `nrv04_vast_launch.cofold` | see pricing.md |
| **stage** — co-fold CIF → `<leg>/complex.pdb` + `<leg>/ligands.sdf`, seeded into the FEP lane's stage cache | `nr4a3_5aks_stage.py`, CI, in the parity image | $0 |
| **2 ternary legs** — OpenFE RBFE, 4 fs (RUNG 2b) | Vast, `gpu-ternary-fep-vast.yml` mode `5aks` | see pricing.md |
| **reduce** — the double difference | `nr4a3_5aks_reduce.py`, parity image | $0 |

**Only `d0` is co-folded, and both endpoints are staged from that ONE pose.** The engine re-imposes each
endpoint's bond orders and stereo from SMILES and OpenFE's hybrid topology handles the one-atom perturbation.
Two independent co-folds would put a **pose difference** between the endpoints that the alchemical
transformation would then have to absorb — a contribution to `S` that is not the physical question. Verified:
the two built endpoints have a maximum heavy-atom coordinate difference of **0.0000 Å** and exactly one
element change.

**No new engine was written on either GPU step.** The co-fold reuses the Vast co-fold lane that already
exists and is parameterised by `$TERNARY_SCRIPT`; the legs reuse `ternary_vast_launch.py` +
`run_ternary_leg.sh` — the single source of truth for the ternary recipe, which a hand-copied duplicate once
made run 16 λ-windows and NaN where the proven recipe uses 12.

## 4 · The pre-spend shakeout — five defects, each of which would have cost a rental

`stage_from_cofold` had never met a real structure file. Rather than discover that on a rented host, the
whole ligand-side chain was driven with **no GPU** against a synthesised Boltz-shaped mmCIF whose ligand
coordinates come from an RDKit embedding of the **committed** d0 SMILES. Every item below is a defect the
shakeout **found**, not one it anticipated. All five are now pinned by
[`tests/test_5aks_pose.py`](tests/test_5aks_pose.py).

1. **The co-fold lookup matched the positive control.** The glob was `*nr4a3*model_0.cif`, and
   `nr4a3_ternary.py` writes its CRBN+lenalidomide control as `nr4a3-ternary-control` — a **single-chain**
   structure with no NR4A3 in it. Sorted, `control` precedes `protac`, so the NR4A3 leg would have been
   staged from a structure containing neither the target nor the construct. The prediction stem now has one
   home (`cofold_cif_stem`).
2. **`gemmi.remove_ligands_and_waters()` empties the ligand chain but does not delete it.** The chain census
   read three chains, and the "a ternary leg needs exactly two" guard rejected good input. *A guard that
   fires on correct input is not a safe guard — it teaches you to loosen it.*
3. **RDKit assigns chirality from 3D, so the pose resolves a stereocentre the design leaves open.** The
   construct's glutarimide C-H is the thalidomide-class centre, drawn unassigned throughout the IMiD
   literature because it epimerises. The extracted pose canonicalised to `N([C@H]3CCC(=O)NC3=O)` against the
   design's `N(C3CCC(=O)NC3=O)`, and plain SMILES equality **rejected a chemically correct ligand** — in the
   stager *and* in the FEP engine. Both now ask the two questions that actually matter: **constitution
   identical**, plus **every stereocentre the design SPECIFIES reproduced** (a chirality-aware substructure
   match, under which an unspecified centre matches either configuration). For a fully-specified target the
   pair is equivalent to the old test, so no existing leg's acceptance moves — and an inverted α-carbon is
   still caught.
4. **Changing an aromatic C to N with its explicit H still attached makes a pyrrole-type N-H, not pyridine.**
   Every candidate site failed with "Can't kekulize mol" until the hydrogens came off.
5. **The FEP engine could not resolve these legs at all.** `leg_spec` knew only the frozen `PILOT_LEG_MAP`,
   and `ternary_coop_prep._morph_endpoints` had no branch for this pair, so the leg would have aborted on
   unresolved endpoints. Fixed with an **extension registry** — the frozen pilot bundle is untouched and
   still loads, because `load_pilot_legs` fails closed on drift and enlarging a preregistered bundle is
   exactly what that guard exists to prevent.

**A sixth, found in the same pass and wider than this rung.** The causal test needs an **aza-scan**, and the
engine only had the calibration edge's hand-written pyridine→benzene rule — the perturbation in the opposite
direction. Rather than write a third hand-identified rule, `_endpoint_pose` now falls back to a **general
single-aromatic-atom element swap that verifies against the target** instead of naming the atom. Ties are
real (either meta carbon of the phenyl gives 3-pyridyl); it takes the lowest index **deterministically** and
records the count, because the two differ only by a 180° flip of a freely rotating benzylic ring that the MD
samples.

### What the real Boltz output then showed — the shakeout earned its keep twice

The co-fold ran on Vast (instance **45935273**, RTX 4090) and all three predictions returned rc = 0. Staging
against the **real** CIFs then passed **first time**, and two of its details are worth recording because both
were live risks rather than hypotheticals:

| leg | co-fold CIF | chains | residues | ligand chain/residue |
|---|---|---|---|---|
| `5aks_d0_to_d__ternary_nr4a3` | `nr4a3-ternary-protac_model_0.cif` | A, B | **A = 254** (LBD), **B = 442** (CRBN) | `L` / **`LIG1`** |
| `5aks_d0_to_d__ternary_nr4a1` | `nr4a1-ternary-protac_model_0.cif` | A, B | **A = 254**, **B = 442** | `L` / **`LIG1`** |

1. **Boltz names the ligand residue `LIG1`, not `LIG`.** An extractor keyed on the residue name would have
   found nothing and reported "the construct did not co-fold" on a co-fold that was perfectly good. It was
   found by the *"residue name is not in the standard polymer set"* criterion — which is exactly why
   `_candidate_ligand_residues` ORs three independent criteria instead of trusting any one of them.
2. **Both species resolved the free stereocentre the SAME way** — `[C@H]3CCC(=O)NC3=O` in both — so the
   guard below passed. That was a genuine coin flip, not a formality: nothing in the co-fold couples the two
   predictions' choice at that centre.

The residue counts are their own check: 254 is the LBD by `nr4a3_ternary.LBD_LEN` and 442 is CRBN, so the
"exactly two chains" guard is confirmed against the sequence lengths rather than against a file name.

### The cross-leg stereo guard, which nothing else would have caught

Because the glutarimide centre is unspecified, **Boltz resolves it independently in each species' co-fold and
can perfectly well resolve it both ways.** `S` is a difference of two legs, so anything differing between
them other than the paralogue lands inside `S` and is indistinguishable from the signal — in that case `S`
would be a difference of **two diastereomers in two different proteins**, reported as a paralogue wedge
effect. `stage_from_cofold` now refuses to stage the pair unless both legs resolved it identically, and
records the shared stereo SMILES. Free to catch at staging; invisible afterwards.

## 5 · The smoke leg failed in PRE-EQUILIBRATION — which is exactly what a smoke leg is for

**The plumbing shakeout did its job: the ~$12 pair was not spent.** The smoke cost **~$0.02**, and `collect`
destroyed the host on the spot (*"unit FAILED — nothing left to produce"*).

**The diagnosis came from `status.json`, not from a story:**
`{"status":"failed","phase":"preequil","rc":1}`. So the leg cleared the CUDA probe, the repo pull and
**staging** — the pre-seeded stage cache HIT, which is the whole new mechanism this rung depends on — and
died in pre-equilibration.

**Cause.** `nr4a3_5aks_stage` wrote the co-fold's polymer straight out and explicitly stripped hydrogens, so
`complex.pdb` reached OpenMM with **no hydrogens and no terminal OXT**. `ForceField.createSystem` does not
add protein hydrogens — it fails template matching. This is the **same defect the crystal stager hit on
2026-07-17**, whose own docstring records *"this ternary-staging path had never carried a real production
leg before"*. A co-fold-derived leg is a **second entry point into the same wall**, so the fix calls the
*same* function (`ternary_pdb_stage._hydrogenate_pdb`) rather than growing a second copy that can drift.

**Proved, not asserted.** [`nr4a3_5aks_preequil_repro.py`](nr4a3_5aks_preequil_repro.py) runs the one
observation that discriminates: the same `ternary_preequil` invocation, in the same parity image, against
two `complex.pdb` files differing **only** in hydrogenation. It reports **HYPOTHESIS REFUTED** if the
unfixed arm passes and **FIX INSUFFICIENT** if both fail — and in both cases says *do not re-rent*. It runs
on CPU because system construction touches no GPU.

**The verdict it returned, verbatim** (GH run 30218400450, 2026-07-26 4:39 PM ET):

```
================ VERDICT ================
  ARM A (no hydrogens) rc=1   ARM B (hydrogenated) rc=0
  CONFIRMED: hydrogenation is the cause. The unfixed complex fails and the fixed one does not,
  with nothing else differing between the two runs.
  ARM A failed on a force-field TEMPLATE error: True
```

The hydrogens are physically present, not merely reported: the re-seeded stage-cache tars went
**471,040 B → 921,600 B** per leg. That delta *is* the added hydrogens and terminal atoms.

### ★ The rung's central claim, verified inside OpenFE rather than in our own harness

ARM B ran far enough to build the alchemical mapping, and the engine's **own** endpoint verification is the
strongest evidence in this lane that `S` measures what it is supposed to:

```
[preequil] endpoint map (lomap_element_change): 111 mapped atoms A->B (ligA 111, ligB 111)
[preequil] endpoint verification: {"mapped_max_displacement_ang": 0.0, "graph_identical": true,
  "chirality_not_inverted": true, "net_charge_conserved": true, "n_mapped": 111, "n_dummy_B": 0,
  "dummy_bond_lengths_ok": true, "min_pair_distance_ang": 1.023, "no_clash": true, "ok": true}
```

Read what those two numbers mean together. **`n_dummy_B = 0`** — the perturbation creates and destroys *no*
atoms, so it is a pure element change and not a fragment being grown; that is the definition of an aza-scan.
**`mapped_max_displacement_ang = 0.0`** — every mapped atom sits at *identical* coordinates in both
endpoints, which is the "one pose, two endpoints" requirement holding exactly, measured by the engine that
will run the leg rather than asserted by the stager that wrote it. `chirality_not_inverted` and
`net_charge_conserved` close the two remaining ways a one-atom edit could have smuggled a second difference
into `S`.

### The smoke leg then reached its real success terminus

Re-launched after the fix as instance **45939256** (machine 55559, RTX 4090, $0.1935/hr):

```
status=done  dG=-9.2369  se=0.4319  NaN=False  prod_s_per_iter=7.9
committed=production/12   up=exited   -> destroying 45939256 (unit done)
```

The ΔG is **meaningless by construction** at 12 production iterations — the smoke's deliverable is the
*terminus*, and the whole chain now has one: hydrogenated stage-cache hit → pre-equilibration → setup →
warmup → production → leg record → upload → reap, on a real host. Per the repo's rule, the pipeline is
"proven" only now, and monitoring can relax from every-few-minutes to a heartbeat.

**A real rate falls out of it: 7.9 s/iter of production**, against 17.0 for the calibration ternary — this
system is ~2.2× cheaper per iteration. Feeding the measured rate to `ternary_cost_model` gives **~7.9 h and
~$1.53 per leg, ~$3.06 for the pair** at the observed $0.1935/hr, comfortably inside the ladder's ~$12
(28–144 ref GPU-h). *The warmup term uses the model's 400-iteration default, so this is an estimate anchored
on a measured production rate, not a measurement of the whole leg.*

### A second, wider bug the diagnosis exposed: the log-preservation block was ordered wrong

The ternary pipeline archives the previous attempt's `run.log` before overwriting it — a guard whose comment
cites the NR-V04 census as the cost of not having it. **It could not work**: `mark()` uploads `/tmp/run.log`,
which `exec > >(tee ...)` has just **truncated**, to `$RESULT_S3/run.log`, and `mark start` ran **before** the
archive block. So the fresh ~170-byte stub overwrote the previous attempt's log in S3, and the archive then
dutifully copied the stub. Seventeen archived attempts on this leg, **every one 168 bytes**, and the log of
the attempt that actually failed was gone. Only `status.json` — written by `fail()`, which nothing overwrites
— made the failure diagnosable at all. The archive now runs before the first `mark`.

## 6 · `n_particles` — the identity check the RUNG 2b cycle could not make

RUNG 2b reached a verdict with `system_identity_consistency` reporting **every** field UNRECORDED, so
comparability rested on `protocol_hash`, which by construction covers the OpenFE **settings** and not the
**system**. That is the same hole through which four reverse-leg attempts ran a 146,020-particle build
against a 141,968-particle one.

`charge_method` and `setup_cache_version` were fixed earlier today (record the **resolved** value, not the
raw env). **`n_particles` had a different and deeper cause, now found:**
`nr4a3_rbfe.execute_hybrid_dag_spot_safe` returned `dg, unc, list(ana_outputs)` on the production path, while
the leg writer reads `_ana_keys.get("n_particles") if isinstance(_ana_keys, dict)`. **A list is not a dict**,
so the field was `None` on *every leg that actually ran MD* — only the PRIME branch, which returns a dict and
exits before MD, ever populated it. The count was in `system` the whole time, one line away. It now returns a
dict, and the Vast lane promotes it into the normalised leg record the reducers read.

**So `S` can be identity-checked, which is the one thing a double difference most needs.**

## 6b · Both production legs went down on their first attempt — one preemption, one REAL defect

**No GPU is billing:** NR4A3's host exited and NR4A1's was destroyed by `collect`. Realized cost of the
attempt is small; what it bought is two distinguishable failures.

### NR4A3 (`45941659`, machine 117843) — PREEMPTION, routine
Its `run.log` was advancing normally right up to the end — `Iteration 44/64, took 7.742s`, steady at
~7.7 s/iter — and then the instance exited having written **no `leg.json` and no `status.json`**. Work
stopping mid-iteration with no failure record written is a host going away, not code failing; the pipeline
deliberately leaves no `leg.json` in that case so a relaunch picks a different machine. Re-dispatch resumes.

### NR4A1 (`45941913`, machine 114101) — a real, reproducible defect, and NOT in staging
It completed solvation (286,494 atoms), minimisation, NVT, NPT and the full 0.5 ns relaxation, then aborted:

```
[preequil] endpoint map (lomap_element_change): 80 mapped atoms A->B (ligA 111, ligB 111)
[preequil] endpoint verification: {"n_mapped": 80, "n_dummy_B": 31, "graph_identical": false,
  "mapped_max_displacement_ang": 0.0, "chirality_not_inverted": true, "net_charge_conserved": true,
  "no_clash": true, "ok": false}
[preequil] ABORT: endpoint verification FAILED (reviewer condition 1)
```

against the NR4A3 arm's **111 mapped / 0 dummy / `graph_identical: true`** on the *same construct*. The
engine's own report names the difference, and it is **not the aza-scan**: `smiles_in` carries the warhead's
indole in a **non-aromatic Kekulé** form (`[H]C1=C(...)c2...N1[H]`) while `smiles_out` carries a properly
aromatic one (`...c([H])n3[H]`).

**Staging is exonerated by measurement, not by argument.** `nr4a3_5aks_ligand_diag.py` pulled *both* legs'
`ligands.sdf` out of the stage cache the rented hosts actually read, in the parity image:

| | records | constitution identical | aromatic atoms | formula |
|---|---|---|---|---|
| `…__ternary_nr4a3` | 2 (`5aks_d0`, `5aks_d`) | ✅ both, and to NR4A1's | 21 / 21 | `C44H47N7O13` |
| `…__ternary_nr4a1` | 2 (`5aks_d0`, `5aks_d`) | ✅ both, and to NR4A3's | 21 / 21 | `C44H47N7O13` |

Identical files, indole correctly aromatic in both. **So the defect is downstream of staging** — in the
endpoint rebuild that happens *after* the pre-equilibration MD (`ligB` is core-transplanted onto the relaxed
`ligA`), where the perception of the relaxed geometry is evidently not stable across poses.

**What this is NOT:** it is not the one-atom wedge, not the stereocentre, and not the hydrogenation fix —
`mapped_max_displacement_ang` is still 0.0 and charge and chirality still check out. It is a *warhead*-side
aromaticity perception failure that happens to abort the leg.

**Next measurement (still $0, still CPU):** run `ternary_preequil` on the **NR4A1** leg specifically, in the
parity image, dumping the intermediate `ligA`/`ligB` mols either side of the core transplant — the same
two-arm discipline that settled the hydrogenation question. Do **not** re-rent NR4A1 until that returns: the
failure is deterministic for this pose and a re-rental would reproduce it at full pre-equilibration cost.
**NR4A3 can be relaunched independently** — its defect was the host, not the science.

## 6c · ★ THE ATOM MAP WAS HOST-SPEED-DEPENDENT — the most consequential defect this lane found

**Both hypotheses I preregistered were wrong, and so was my "deterministic for this pose" claim.** The $0
reproduction ran the *same NR4A1 leg* that aborted on Vast and it **passed cleanly** — 111 mapped, 0 dummies,
`graph_identical: true`, `min_pair_distance_ang` 1.023, identical to the NR4A3 arm.

| where | element_change=True | element_change=False | verdict |
|---|---|---|---|
| NR4A3 leg, Vast host | 111 mapped | 111 mapped | ok |
| NR4A1 leg, CPU runner | **111 mapped** | **111 mapped** | **ok** |
| NR4A1 leg, Vast host | **80 mapped, 31 dummies** | **80 mapped** | **ABORTED** |

**The cause is `LomapAtomMapper(time=20, threed=False)`.** `time` is the MCS timeout **in seconds**, and a
timed-out MCS returns its best **partial** match — silently. Three things make this the explanation rather
than a candidate:

1. **`threed=False` makes the map pose-independent.** Neither the MD length, nor CUDA-vs-CPU, nor the
   generated `ligB` conformer can change it. That refutes *both* the "0.5 ns relaxation distorted the indole"
   and "the `ligB` rebuild loses aromaticity" hypotheses outright.
2. **The short map came back at `element_change` BOTH True and False.** A genuine element-change asymmetry
   *separates* those two settings — that is the entire reason `_mapping` computes both and takes the larger.
   Both collapsing to the same smaller number is a budget signature, not a chemistry signature.
3. **The two ligands differ by one atom**, so a complete 111-atom 1:1 map provably exists. A shorter map is a
   failed search, not a property of the molecules.

**Why this matters far beyond 5a-KS.** A partial map is not a slow answer, it is **a different experiment**:
31 atoms that should map 1:1 instead become dummies that are annihilated and recreated. It converges, it
produces tight statistics, and it returns a confident ΔG for a perturbation nobody designed. Every lane
through this mapper was exposed — including the calibration legs.

**Fix** (`nr4a3_rbfe._mapping`): budget raised to **300 s**, env-overridable via `RBFE_LOMAP_TIME_S` so the
old value stays reachable for an exact re-run. A longer search can only find an equal-or-larger MCS, so it
cannot make a previously-correct map worse. Plus a loud **`DEGENERATE MAP`** warning emitted *at the point
the map is produced* whenever both endpoints have the same atom count and the map is short — because
downstream, only `ternary_endpoint_align.verify_endpoints` catches this, and only on lanes that run it.

**⚠ Carried forward, not closed:** the RUNG 2b calibration legs ran under `time=20`. Their maps were never
printed against an expected count, so whether any of them used a degenerate map is **unverified**. That is a
$0 check against their archived logs and it is owed before those numbers are relied on further.

### ⚠ CORRECTION — the timeout was a contributing cause, not the cause

The budget fix above is real but it was **not sufficient**, and the diagnosis it rested on was incomplete.
With `RBFE_LOMAP_TIME_S=300` the NR4A1 leg mapped **110 of 111** and aborted again. The residual 1 was not a
budget artifact, and chasing it found the actual mechanism:

**At pre-equilibration time `ligA` and `ligB` are THE SAME MOLECULE.** `ternary_preequil._load_ligands` takes
the SDF's two records verbatim, and this rung writes **one pose twice** — the endpoint rebuild from the
committed SMILES happens later, in the FEP engine. `nr4a3_5aks_ligand_diag` had already reported both records
as `C44H47N7O13`; the significance was mine to see and I did not.

So LOMAP was being asked to map a molecule **onto itself**:

| budget | self-map result | outcome |
|---|---|---|
| `time=20` | 80 of 111 (31 dummies) | ABORT |
| `time=300` | 110 of 111 (1 dummy) | ABORT |
| same inputs, other hosts | 111 of 111 | ok |

**There is no chemical reason for a self-map to be incomplete**, so every shortfall was a search artifact
turning identical atoms into dummies. It also explains the Kekulé-vs-aromatic indole in
`smiles_in`/`smiles_out`: one molecule re-perceived differently across a transplant it never needed.

**Fix** (`_endpoint_map_a2b`): when both endpoints have the same atom count *and* the same canonical SMILES,
use an exact full-molecule substructure match — deterministic, no timeout, immune to host speed and to
aromatic perception. Verified on the real construct: **111/111, exact identity permutation**,
`source=identity_same_molecule`. The 300 s budget stays, because it is still right for genuinely different
endpoints, but it is **no longer load-bearing for this class**.

**Confirmed independently (LANE 19 audit):** valB_mini r0 is CLEAN — all three legs 109/109 under one
protocol hash — and RUNG 2b's four 4 fs legs are 109 too. **So no validated result was corrupted by this, the
wrong sign in RUNG 2 is real and not a map artifact, and the defect is specific to a lane that writes one pose
twice.** The `⚠ DEGENERATE MAP` warning stays regardless: it is what made the residual 1 visible at all.

### This is the second time the endpoint verification earned its place

It refused a leg that would otherwise have run to completion and returned a converged number. The guard was
added as "reviewer condition 1" and could easily have been treated as ceremony; on its second outing it
caught a defect that no other check in the pipeline — not `protocol_hash`, not the system-identity fields,
not the reducer — is positioned to see. **A guard that only ever passes is untested. This one is not.**

## 6d · ★ THE "~15–20 MINUTE DEATH CADENCE" WAS AN ARTIFACT OF THE SAMPLING INTERVAL, NOT A FAULT

For most of one night this lane was run on the belief that both 5a-KS ternary legs were dying and restarting
every ~15–20 minutes, at ~3.5× overhead, on a lane that was somehow uniquely afflicted. **All three parts of
that were wrong**, and every one of them was refutable for $0 from artifacts that already existed. What made
the belief durable is that it was assembled entirely from *hourly reads of phase markers and commit counters* —
a sampling process whose period was of the same order as the thing being measured.

**The measurement that settled it.** An attempt's `run.log` is archived under `attempts/` **by the next
container's start**, so the S3 `LastModified` times of the archived logs are the death series, and consecutive
gaps are the per-attempt lifetimes. That is one `aws s3 ls` per unit. It is now the CROSS-LANE RESTART TABLE in
`rung5aks-cofold.yml mode=leg_diag` (run 30248149894, $0), which reports it for **every unit in the lane**, not
just this rung's — because the claim under test was comparative and could not be checked from the 5a-KS legs
alone.

| unit | per-attempt lifetimes (min) | sub-minute relaunch loops |
|---|---|---|
| `5aks_…__ternary_nr4a3_…_5aks` | **408, 23, 84** | 0 |
| `5aks_…__ternary_nr4a1_…_5aks` | **76, *14*, *14*, 103, *11*, 112, 35, 143, 63** | 0 |
| `calib_hi_to_lo__ternary_vhl_…_probe` | 131, 43, 12, 26, 16, 41, 6, 30, 23, 3, 65, 43, 20, 24 | 4807 |
| `calib_hi_to_lo__ternary_vhl_…_edge` | 134, 217, 84, 22, 240, 20, 180, 2, 7, 40, 143, 101 | 972 |
| `calib_hi_to_lo__binary_vhl_…_edge` | 135, 64, 108, 303, 280 | 931 |
| `calib_hi_to_lo__solvent_…_edge` | 47, 86, 17 | 5766 |

*Italicised* NR4A1 entries are the three deterministic pre-equilibration aborts of §5/§6c — a different,
already-fixed failure, and the only one in the whole table that wrote a `[tvast] FAILED at preequil` line.

Read across the table:

1. **There is no ~15–20 minute period anywhere in the 5a-KS legs.** Excluding the pre-equilibration aborts,
   post-warmup lifetimes run 23–408 min. One NR4A3 attempt ran **6.8 h unbroken** and completed the entire
   1600-iteration warmup in a single sitting.
2. **The comparison lane was never a control.** The `probe` unit — same repo, same image, same machinery, and
   the lane cited as "has run for hours without this" — restarted **fourteen** times with attempts of 3, 6, 12
   and 16 minutes. The closest thing to a 15-minute cadence in the entire dataset is on the lane assumed to be
   immune. **The 5a-KS legs are not anomalous; they are among the better-behaved units in the lane.**
3. **The 3.5× overhead does not reproduce.** Re-measured on the current attempts: NR4A3 restored at production
   iteration 160, committed 200 and 240, and reached iteration 250 in 32.6 min — **90 iterations, 21.7 s/iter
   effective against an in-run raw rate of 18.7–19.3 s/iter, ≈1.15×**, container start and setup-cache restore
   included. The 3.5× came from one 35-minute window that happened to contain a restart.
4. **The deaths are the host going away, not the process faulting.** Neither leg has ever written a
   `status.json` or `leg.json` for a post-pre-equilibration death, and every such archived log ends *mid-
   iteration* with no traceback and no `[tvast] FAILED at <phase>` line. The failure path demonstrably works —
   it fired for all three pre-equilibration aborts — so its silence is evidence, and it rules out in-process
   crash, NaN, and an OOM kill of the Python process alike (a `SIGKILL` still leaves the wrapper's `EXIT` trap
   to write the record). This is **ordinary spot churn**, which CLAUDE.md §6 says to mention lightly and not
   investigate.
5. **Two populations were being conflated, and only one is a defect.** The `loop<1m` column counts *sub-minute*
   relaunches — hundreds to thousands on every finished calibration unit. Those are not MD deaths; they are the
   post-completion relaunch loop, a host restarting a container that exits immediately because the unit is
   already `done`. Both 5a-KS legs show **zero**, which is the done-only idempotency and result-based reap of
   §6b working. Mixing that column into the lifetime series is what made one unit print 5770 entries and hid
   the dozen numbers that mattered.

**The methodological lesson, and it is the expensive one.** Repo rules already require root-causing with a real
diagnostic rather than a plausible story, and I followed that for the pre-equilibration abort and for the atom
map (§6c) — both real defects, both correctly caught. Then I spent a night characterising the *period* of a
phenomenon using observations taken at roughly that same period, and every refinement of the story ("NR4A3
hides it", "ci=40 vs ci=64 explains which one looks stalled") made it more explanatory and no more tested.
**A hypothesis that explains the sampling artifact as well as it explains the fault is not evidence for the
fault.** The check that broke it was not clever: it was measuring the quantity directly instead of inferring it,
on the comparator as well as the subject, and it cost one $0 CI run.

### The queued mitigation (`TVAST_WARMUP_CKPT_ITERS=16`) is a NO-OP on a leg already in warmup

Shortening the warmup commit interval was queued as a mitigation while the cadence was still believed real. It
was worth checking before applying, and the check kills it twice over.

**Mechanically it cannot take effect.** `rbfe_spot_driver` enforces a *single-interval invariant*: on a resume
the effective interval is read back out of the existing warmup `.nc` — `spot.read_checkpoint_interval(...)` —
and **explicitly overrides the environment**, logging `RESUME warmup: committed-file checkpoint_interval=64
OVERRIDES env warmup_checkpoint_iters=16`. That is not an oversight; it is the 2026-07-21 root-cause fix for
`resume iteration 520 != expected 540`, because openmmtools fixes the cadence when the `.nc` is *created* and a
driver running off a different grid than the file corrupts the resume. So the knob only binds on a **fresh**
warmup — which for NR4A1 means discarding the 320 committed warmup iterations it has already paid for.

**And the arithmetic no longer supports it.** Expected loss per death is half the interval ≈ **8 min**, against
measured attempt lifetimes of 23–408 min. That is single-digit-percent overhead, bought at 4× the commit
frequency, to mitigate a fault the census says is not there. `TVAST_WARMUP_CKPT_ITERS` stays available for a
fresh launch; it is not applied here, and the reason is a measurement rather than a preference.

## 7 · What runs next, in order

Everything below is wired and dispatchable; nothing here needs new code.

| # | command | cost | gate |
|---|---|---|---|
| 1 | ~~`rung5aks-cofold.yml` `mode=preequil_repro`~~ | $0 CPU | ✅ **CONFIRMED** (run 30218400450), and it re-seeded the stage cache with the hydrogenated tree |
| 2 | ~~`gpu-ternary-fep-vast.yml` `task=5aks-smoke`~~ | ~$0.05 realized | ✅ **PASSED** — `production/12`, leg record written, host reaped |
| 3 | ~~`gpu-ternary-fep-vast.yml` `task=5aks`~~ | ~$3.6 est. | ✅ **BOTH LEGS RUNNING** from 5:21 PM ET — **NR4A3** `45941659`/m117843/4090/$0.2348h, **NR4A1** `45941913`/m114101/4090/$0.2237h. NR4A1's first host (m26910) answered `resources_unavailable`; the lane destroyed it and relaunched elsewhere rather than queueing or raising the bid — the standing Vast rule executing itself |
| 4 | `gpu-ternary-fep-vast.yml` **`task=5aks-reduce`** | $0 | computes `S` in the parity image and commits `nr4a3-5aks-reduction.json` |
| 5 | fold `S` into paper **§2.10(d)** and the **Tier-3 row of §5's ladder**, and into §6 below | $0 | §2.10(d) currently reads *"The causal test has not been run"*; that sentence and the ladder row `priced, **not run** / pending` are what this rung retires |

**Monitor with `task=collect`, which is a PROGRESS check** — it prints the furthest committed iteration and
compares it with the previous poll. A leg that is "up" is not a leg that is running.

**If step 1 does NOT print CONFIRMED, do not proceed.** The script deliberately distinguishes *HYPOTHESIS
REFUTED* (the unfixed arm passed, so hydrogenation is not the cause and the real one is unfound) from *FIX
INSUFFICIENT* (both arms fail), and says do not re-rent in either case.

## 8 · Result

*(filled in when the legs land — `nr4a3-5aks-reduction.json` is the machine record and its `S_kcal` is the
one home for the number)*

---

## Standing traps, kept because each was nearly stepped in

- **`__ternary` is a DOUBLE underscore, and it is load-bearing.** `nr4a3_ternary_fep._environment_of`
  classifies any leg id not in the frozen `PILOT_LEG_MAP` by `"ternary" if "__ternary" in leg_id else
  "binary"`. A single-underscore id would classify as **binary**, the engine would drop the target chain, and
  `S` would be a difference of two binary legs **with no paralogue in either**. A binary leg converges
  perfectly well, so nothing downstream would notice.
- **Never add these legs to `ternary_coop.PILOT_LEG_MAP`.** It is the preregistered pilot bundle and
  `load_pilot_legs` fails closed on drift.
- **These legs stage off-host.** There is no crystal of CRBN + an NR4A-LBD + this construct — that is the
  point of the rung — so their inputs are pre-seeded into the FEP lane's stage cache and `STAGE_REQUIRED=1`
  makes a cache miss an immediate, explicit failure instead of a silent fall-through into the RCSB crystal
  stager with a leg id it has never heard of.
- **The reducer keys on `(leg_id, seed)`, and the MODE is not in that key.** `5aks_…__ternary_nr4a3` is the
  leg id of both the ~$12 production leg and the ~$0.15 smoke leg — the mode lives only in `unit_id`, and
  `fetch_legs` writes both to the same `leg_<leg_id>_<direction>_r<seed>.json`. A smoke leg's ΔG is meaningless
  by construction *and perfectly well-formed*, so a silent overwrite yields an `S` that passes the
  non-ternary refusal, the provenance checks and the sign convention, and is simply wrong. `load_legs` now
  raises `AmbiguousLegError` when two differing records claim one key (identical ones are still just a
  duplicate download), and the CLI writes `decision: REFUSED` with the reason **in** the deliverable.
- **A one-chain "ternary" leg is a binary leg nobody labelled**, and it would give `S ≈ 0` — which looks
  exactly like the preregistered null. The stager refuses it.
