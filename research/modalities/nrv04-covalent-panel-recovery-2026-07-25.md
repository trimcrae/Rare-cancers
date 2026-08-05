---
id: DOC-NRV04-COVALENT-PANEL-RECOVERY-2026-07-25
title: NR-V04 covalent feasibility panel — can the withdrawn GO be recovered? (2026-07-25)
level: L4
kind: memo
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `memo` from its location under research/modalities/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# NR-V04 covalent feasibility panel — can the withdrawn GO be recovered? (2026-07-25)

**Question put to this lane:** the 18 endpoint-MD legs already ran and the defect was in the *analysis* (which
chain was called "target"), not the *physics* — so can the corrected R1/R2/R3 be recomputed from the committed
trajectories at **$0**, recovering the withdrawn GO without re-running any MD?

**Answer: no — and it does not matter, because the panel's GO was never available to recover.** Six
independent findings, each measured from a committed artifact. Total spend: **$0**.

| # | finding | evidence |
|---|---|---|
| 1 | **No trajectory was ever written.** The $0 recompute is impossible. | 72 objects under `nrv04-covalent-results/`, **zero** with any trajectory extension; zero surviving checkpoints |
| 2 | **The panel's own frozen verdict function returns `go: false`** on the panel's own committed legs — independent of the chain split | `nrv04_readouts.panel_verdict` run on the 17 landed legs |
| 3 | **The panel's inputs were CONTAMINATED**: it simulated 14-3-3 epsilon in place of Elongin B | census of all 12 persisted systems (`A=254, E=213, F=255, G=112`) + a CA-geometry match to `nrv04-descriptive-v3/nr4a1/seed_1` at **RMSD 0.000 Å** |
| 4 | **The chain-blind defect had a second live instance** — the reactive-cysteine search — still unfixed | both `warhead_only` legs record the adduct on Elongin C Cys74 at 12.44 Å |
| 5 | **R3 was reported in nanometres under an Ångström label** — every committed R3 distance is ~10× too small | independent t=0 recomputation reconciles with the committed `min_A` at a ratio of ~10 at two well-separated values |
| 6 | **The re-run cannot reach the frozen GO on any available input** — so it must not be paid for yet | free staging check: `warhead_only`'s nearest target-chain Sγ is **16.39 Å** on the *clean* co-fold |

---

## 1. The $0 recompute is impossible — the trajectories do not exist

[`nrv04_result_forensics.py`](./nrv04_result_forensics.py) → [`nrv04-result-forensics.json`](./nrv04-result-forensics.json).
Read-only `list_objects_v2` + `get_object` over the real bucket.

```
nrv04-covalent-results/   72 objects, 19 units
    built_cif      n=12    796,689,589 B    the solvated topology + PRE-MINIMIZATION coordinates — ONE frame
    built_system   n=12  1,349,596,712 B    the OpenMM System (forces/parameters) — no coordinates over time
    built_meta     n=12          2,920 B
    leg_result     n=17         26,890 B    R1/R2/R3 ALREADY REDUCED against the split that was used
    phase          n=18            544 B
    other          n=1           4,210 B    _price_ledger.json
    trajectory     n=0                      ← the decisive line
```

**Mechanism, confirmed against the driver after the listing established the fact.** `nrv04_covalent_md.run_leg`
never opens a trajectory reporter: each frame's positions are reduced *in the loop* to a contact count, an
interface RMSD and the target-chain Lys Nζ coordinates, and the positions are discarded. The accumulating arrays
live only in `ckpt_*.ckpt.json`, and `_rm_ckpt` **deletes** that checkpoint when a leg finishes cleanly — which
17 of 18 did. So for every completed leg the only surviving coordinates are the build-time snapshot.

**Why no reduced artifact helps either.** Recomputing R1/R2/R3 for a *different* chain pair needs per-frame
all-atom positions. What survives is: per-frame contact **counts** (integers, for the wrong pair), per-frame
interface **RMSDs** (floats, for the wrong pair), and Lys Nζ coordinates **for the wrong chain**. None can be
re-derived into the corrected quantities. This is a design consequence worth carrying forward — see §5.

---

## 2. The frozen prereg verdict on the panel's own numbers is NO-GO

The superseded science numbers were quoted as an R1-stability narrative ("recruiter_active 3/3 stable vs epimer
1/3"). But prereg §5 is executable — `nrv04_readouts.panel_verdict` — and §5 criterion 3 does not score that
comparison at all. Running the frozen function on the panel's own committed legs:

```json
{"go": false,
 "reasons": ["warhead_only recruited despite no E3 moiety — readout artifact",
             "inactive epimer engaged VHL — negative control failed"]}
```

**Both negative controls returned positive.** In fact **all 17 legs** returned `frac_frames_in_contact = 1.0`
and `recruited = true`, with mean contact counts 1620–3861. R2's frozen rule is *"any interface contact in more
than 50 % of production frames"*; started from a co-folded complex and run for 5 ns, no leg can fail it. R2 as
frozen does not discriminate — that is measured, not argued.

The corrected split does not rescue it: the one leg that has ever run with the identified split (the
`nrv04-covalent-results-chainfix` smoke leg, `target=['A'] e3=['E','F','G'] explicit=true`) returns
`frac_frames_in_contact = 1.0, mean_contacts = 1979.4, recruited = true`.

**So the withdrawn GO was not a correct result made wrong by the chain split. It was never the output of the
frozen scoring rule.** The chain split made the numbers describe the wrong interface; §5 would have said NO-GO
on the right one too, for a different reason.

R1 stability is also weaker than reported when read per seed: `cov_nr4a1` 2/3 stable (plateaux 2.561 / 3.703 /
**5.003** Å), `noncov_nr4a1` 2/3 (2.938 / 3.651 / **5.047**), `cov_c551a` 1/3, `recruiter_epimer` 1/3,
`recruiter_active` 3/3. Against a 4.0 Å threshold with n = 3, none of these separations is resolved.

---

## 3. The panel simulated the wrong E3 subunit — a third, independent invalidation

[`nrv04_corrected_t0.py`](./nrv04_corrected_t0.py) reads each leg's `built_*.solv.cif` — *the exact system that
was integrated*. The protein chain census is identical across all 12 snapshots:

```
A = 254   NR4A LBD (frozen construct)
E = 213   VHL
F = 255   ← 14-3-3 epsilon (P62258), NOT Elongin B (118)
G = 112   Elongin C
```

The 2026-07-24 forensics recorded the covalent panel as *"clean on this defect — its inputs were regenerated
after the correction."* **That conclusion is refuted by the panel's own systems.** It was reached by auditing
the co-fold *prefix the code points at* (`nrv04-covalent-cofold`, which is genuinely clean at F = 118) rather
than the artifact that actually ran.

**The clean prefix cannot be the source.** Its models are dated **2026-07-22 15:00–15:06 UTC**; the panel's
first leg landed **2026-07-23 05:05 UTC**. A clean co-fold existed and was not used.

**Positive identification, not just elimination.** Solvation translates every atom and PDBFixer adds hydrogens,
but the target chain's heavy-atom CA geometry carries through unchanged, so a Kabsch RMSD against candidate
co-fold models identifies the exact source:

| candidate model | CA RMSD to the simulated system (Å) |
|---|---|
| `nrv04-descriptive-v3/nr4a1/**seed_1**` | **0.000** ← the source |
| `nrv04-shakeout/nr4a1/seed_1` | 0.001 (the same model, copied into a second prefix) |
| `nrv04-descriptive-v3/nr4a1/seed_2` | 3.028 |
| **`nrv04-covalent-cofold/nr4a1/seed_0`** (the clean prefix) | **5.884** |
| `nrv04-descriptive-v3/nr4a1/seed_3` | 8.159 |

**Mechanism, from the tree as it stood when the panel ran** (`fusion-cpu-extras.yml` @ `786759a9`):

```yaml
      cofold_prefix:
        description: "nrv04_vast_launch: S3 prefix of the EXISTING NR-V04 co-fold to reuse (ValB output)"
        default: "nrv04-descriptive-v3"        # ← the contaminated prefix
```

The launcher's own fallback was `nrv04-covalent-cofold`, but **a fallback never fires when the workflow always
supplies the input.** The default was corrected to `nrv04-covalent-cofold` on 2026-07-24 — after the panel ran,
and before the audit that pronounced it clean, which is exactly why the audit read the wrong thing.

This is the general lesson: **audit the artifact that ran, not the input the code currently names.** The
build-time snapshot is what makes that possible, and it is the reason it should be kept.

---

## 4. The chain-blind defect had a second live instance, still unfixed

`_topology_indices` was fixed on 2026-07-24. `_reactive_cys_by_geometry` was not, and it is the same defect
class — *a selection rule that ignores a dimension the data varies along*. It searched **every** chain for the
Cys Sγ nearest the warhead electrophile, on the reasoning that *"the co-fold placed the warhead in the NR4A1
pocket, so the nearest Sγ IS the covalent partner"* — which assumes its conclusion.

**It fired in production.** Both landed `warhead_only` legs record `reactive_cys = chain G resid 74 at 12.44 Å`
— the covalent restraint was built onto **Elongin C** — while the other 15 legs record chain A resid 222 at
7.4 Å. A second, independent signature: the `warhead_only` systems are **~645 k atoms** against ~466 k for every
other leg, i.e. free celastrol sits far enough outside the complex that solvating it needed ~180 k more waters.
The only consequence at the time was a `WARN` line.

**Fixed here:** the chain now comes from `chains.json` (identification); the geometry only chooses *which*
cysteine on it; `chains.json` is read **before** the build so `build_system` can use it; a covalent leg whose
target-chain Sγ exceeds `MAX_COVALENT_TETHER_A` (8.0 Å — the driver's own former warning threshold) now
**raises** instead of winching the ligand across the assembly; a target chain with no cysteine raises rather
than falling back off-target; and the full search diagnostics, including the global nearest, are recorded in
`meta.reactive_cys` so a bad co-fold stays distinguishable from a bad build. Six regression tests in
[`tests/test_nrv04_chain_split.py`](./tests/test_nrv04_chain_split.py) (12 pass), including the old rule pinned
as the bug.

Two related traps closed: `nrv04_build_smoke.py` defaulted to the contaminated `nrv04-descriptive-v3` prefix and
called `build_system` **without** the target chain, so the smoke exercised the old global search.

### A fifth instance, in this document's own tooling

The first run of `nrv04_corrected_t0.py` classified chains with `gemmi.find_tabulated_residue(...).is_amino_acid()`.
**`UNK` — the small molecule's residue name — is a tabulated amino acid** (the PDB's "unknown residue"), so the
ligand chain counted as a 1-residue protein, "sorted-last" became the ligand instead of Elongin C, and the
as-run comparison reported 0 target lysines. It was caught only because the derived numbers disagreed with the
driver's own recorded R3. The protein test now matches the driver's verbatim. Recorded because the defect class
is evidently easy to reproduce, including by the person auditing for it.

---

## 4b. R3 was reported in nanometres under an Ångström label

Recomputing R3's inputs independently from the persisted starting systems and comparing against the driver's
committed numbers does not reconcile — until a single factor of 10 is applied, at which point it reconciles at
two well-separated values:

| legs (as-run split) | independent t=0 distance | committed `min_A` | ratio |
|---|---|---|---|
| `warhead_only` ×3 | 25.21 Å | 2.34 / 2.44 | 10.3–10.8 |
| cov / noncov / active / c551a / epimer | 48.92 Å | 4.00–4.48 | 10.9–12.2 |

The ratio is ~10 at both, and **≥** 10 exactly as it must be, since the committed value is the *minimum over 500
frames* while the recomputation is a single starting frame.

**Mechanism, in the code.** `nrv04_readouts`' contract is Ångström (*"frames are lists of (x,y,z) tuples, Å"*),
but the driver works throughout in nanometres. R1 converts explicitly — `* 10.0  # nm -> Å` in
`_aligned_iface_rmsd` — and **R3 did not**. `lys_frames` and the catalytic proxy both came from
`_positions_nm()` and went straight into `lys_presentation`, whose output field is named `min_A`.

**Why it matters beyond bookkeeping.** R3 is descriptive and is not scored by `panel_verdict`, so it does not
change the GO. But the reported values read as *ubiquitination-competent* geometry (~2–4 Å from a Lys Nζ to the
E2~Ub proxy) when the true corrected separation is **~30–49 Å**. Quoted anywhere, that inverts the conclusion.
Fixed in the driver (converted at the boundary, where R1 already converts) with a regression test pinning the
round trip.

---

## 5. What this means for the re-run, and for the prereg

**The corrected re-run is not a correction.** It would be staged from `nrv04-covalent-cofold`, a *different and
cleaner* co-fold than the one that ran. It is a **new feasibility panel on new inputs**, and must be described
that way rather than as a re-analysis of the existing one.

**It cannot reach the frozen GO as the prereg stands**, because §5 criterion 3 requires
`warhead_only.recruited == False` and `recruiter_epimer.recruited == False`, and R2 is measured-degenerate. Two
things would have to change first, and both are prereg-level decisions, not implementation choices:

1. **R2 needs a threshold that can fail.** "Any contact in > 50 % of frames" is satisfied by every co-folded
   assembly. A discriminating rule would compare the *magnitude* (e.g. mean interface contacts or BSA against a
   matched reference), or measure engagement of the *ligand* with VHL rather than the protein–protein interface.
2. **`recruiter_epimer` is not a structural negative control as implemented.** Prereg §3 specifies it as a
   **binary** "VHL + epimer-NR-V04" system, but `assemble_leg` is called with `keep_chains=None`, so all chains
   are kept and the leg runs as a **full ternary** — confirmed from its artifacts: it records a reactive Cys on
   chain **A** (a binary VHL system has no chain A) and is ~486–490 k atoms, larger than the ternary legs. Since
   the active and epimer systems then differ *only* in a ligand stereocentre, the protein–protein interface is
   identical by construction and no protein-interface readout can separate them. The matched-ternary design is
   the better experiment; it is simply not the one that was preregistered, and the prereg must be amended to say
   so, with the readout moved to the ligand.

**`warhead_only` is not runnable on any co-fold in the bucket.** [`nrv04_prespend_check.py`](./nrv04_prespend_check.py)
→ [`nrv04-prespend-check.json`](./nrv04-prespend-check.json) stages all six legs from the **clean**
`nrv04-covalent-cofold` on a free runner:

| leg | stages? | target chain | nearest **target-chain** Cys Sγ to the warhead electrophile | staged E3↔target contacts |
|---|---|---|---|---|
| `cov_nr4a1` | OK | A | **8.99 Å** ← over the 8 Å preformed-adduct limit | 381 |
| `noncov_nr4a1` | OK | A | 8.99 Å (noncovalent — descriptive only) | 381 |
| `cov_c551a` | OK | A | 8.99 Å (noncovalent by design) | 381 |
| `warhead_only` | OK | A | **16.39 Å** ← free celastrol is nowhere near the pocket | 332 |
| `recruiter_active` | OK | A | 8.99 Å | 381 |
| `recruiter_epimer` | OK | A | 8.87 Å | **369** |

Three things follow, and together they are the reason not to spend:

1. **The chain-identification fix works end-to-end** — every leg stages and resolves `target = A`,
   `e3 = [E, F, G]`. That part of the correction is proven, for free.
2. **`warhead_only` cannot be built from any co-fold in the bucket.** 16.39 Å is not a preformed Michael
   adduct; it is the restraint winching the ligand a third of the way across the complex. Boltz does not place
   free celastrol against an NR4A1 cysteine, in the contaminated co-fold *or* the clean one — so this is not a
   contamination artifact, and prereg §5 criterion 3 has no way to be evaluated. (`cov_nr4a1`'s own 8.99 Å is
   marginal on the same measure; the panel's original legs ran at 7.4 Å only because the *contaminated* co-fold
   happened to pose it closer.)
3. **The epimer is not separable by any protein-interface readout.** Its staged interface is 369 contacts
   against the active leg's 381 — a 3 % difference between two independent Boltz diffusion runs, i.e. noise.

**Recommendation: do NOT launch the re-run yet. $0 has been spent and nothing is pending.** The order that
would make a re-run worth paying for is: (a) amend the prereg — an R2 threshold that can fail, and
`recruiter_epimer` restated as a matched-ternary *ligand-level* control; (b) re-fold `neg_celastrol` with more
seeds and keep a model where celastrol is actually seated against an NR4A1 cysteine (~$1), or drop
`warhead_only` from the panel and say so; (c) only then run the 18 legs (~$8).

**Infrastructure change that should be adopted regardless:** the driver should write a **strided trajectory**
(a few hundred frames of protein + ligand heavy atoms is a few tens of MB per leg, against the ~112 MB System
XML it already uploads). Every one of the analysis defects above would have been correctable for $0 if it had.
The panel's cost record (~$0.43/leg) is unaffected by any of this and stands.
