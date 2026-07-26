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
in [STRATEGY.md](../../STRATEGY.md).

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
- **A one-chain "ternary" leg is a binary leg nobody labelled**, and it would give `S ≈ 0` — which looks
  exactly like the preregistered null. The stager refuses it.
