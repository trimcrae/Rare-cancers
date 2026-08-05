---
id: DOC-PROTFEP-PMX-PLAN
title: 5a-KS wedge engine — the pmx + GROMACS route (decided 2026-07-24)
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
# 5a-KS wedge engine — the pmx + GROMACS route (decided 2026-07-24)

**Status: ★ QUALIFIED 2026-07-25, full 3 × 3 replication.**

| benchmark | computed ΔΔG_bind | reference (SKEMPI-verified) | abs err | within ±1.5 |
|---|---|---|---|---|
| barnase–barstar **Y29A** (hot spot) | **+4.424 ± 1.077** | +3.40 | 1.024 | ✔ |
| barnase–barstar **Y29F** (near-null control) | **−0.370 ± 0.175** | −0.13 | 0.240 | ✔ |

Ordering correct (Y29A ≫ Y29F). Measured **1.058 ± 0.432 GPU-h/leg** over 11 legs, **$0.212/leg**;
PROJECTED wedge ~**$4.7 (3 rep)** — particle-count-scaled, an assumption not a rate.

## ★ The result that should change decisions: the noise is effect-size dependent

Between-replicate SD differs **6.2×** between the two benchmarks, at identical replication:

| perturbation | effect | between-leg SD | within-leg MBAR SE |
|---|---|---|---|
| Y29A hot-spot knockout | +4.4 | **±1.077** | 0.05–0.13 |
| Y29F near-null | ≈0 | **±0.175** | 0.05–0.13 |

Within-leg sampling error is ~10× smaller than between-leg scatter in both cases, so this is
**setup/equilibration variance, not sampling length**. Longer legs will not fix it; more legs will.

Two consequences. First, **a single leg does not determine a number** — Y29A's mean walked
2.851 → 3.951 → 4.025 → 4.424 as replicates arrived and its error against the reference *grew*
(0.549 → 1.024). The reducer's refusal to attach an error bar to one leg was right. Second, and more
usefully: the wedge measures a SMALL induced-interface difference (~1.12 kcal/mol best-case resolvable,
per the ternary-selectivity review), which is the regime where this engine is reproducible to ±0.18 —
not the ±1.08 the hot spot implies. **So the honest validation still missing is a benchmark sized like
the wedge.** The hot spot proves the engine sees a large effect; the near-null proves it does not
invent one; neither directly proves it resolves ~1 kcal/mol between two real ternary states.

The pipeline reached this through heavy host churn (see the failure table and
`research/compute/vast-churn-observations-2026-07-25.md`): the resume path, not host stability, is what
made it finish — legs survived repeated host death by restoring banked λ windows from S3.

## Why the engine changed

The 5a-KS wedge was implemented on **perses** (`nr4a3_protein_fep.py` + `protfep_run.py`) and the
benchmark lane was built and launched. The first real leg failed, and the failure is structural, not
a packaging detail:

```
PointMutationEngine.propose
  -> _construct_atom_map                                    topology_proposal.py:634
  -> PolymerProposalEngine.generate_oemol_from_pdb_template  :1179, :1180
  -> createOEMolFromSDF                                      :487
  -> oechem.oemolistream()                                   perses/utils/openeye.py:346
```

perses 0.10.3 builds the **old→new residue atom map** — which *is* the alchemical transformation — by
round-tripping each residue template through an OpenEye OEMol. OpenEye is commercial and
licence-gated. Free-CI probes confirmed `generate_oemol_from_pdb_template` has no conditional and no
RDKit alternative; perses' only RDKit-backed mapper (`rjmc/atom_mapping.py`) is the *ligand* mapper
and is not on this path. An import shim satisfies the import and correctly **refuses** the call.

trimcrae's decision (2026-07-24): **switch to pmx + GROMACS** rather than pursue a commercial licence,
descope the wedge, or fall back to the MM-GBSA proxy. pmx is the published, field-standard free engine
for exactly this quantity (Gapsys & de Groot), and "a second MD stack" is engineering — which is free
here — whereas a licence is not.

**Cost of establishing all of the above: ~$0.05 of Vast time**, plus free CI.

## What the probes established (so the build does not repeat them)

| Question | Answer | Gotcha that produced a FALSE negative first |
|---|---|---|
| Is pmx on conda-forge? | **No** — pip/GitHub only | — |
| Does pmx install on Python 3.11? | **Yes, from the `develop` branch** | The repo's DEFAULT branch is the legacy **Python 2** codebase: pip refuses it with `requires <3,>=2.7`. That reads as "pmx does not support modern Python" and is wrong. |
| Is there a CUDA-enabled GROMACS on conda-forge? | **Yes** — `gromacs=*=*cuda*` solves (165 packages, ~2 GB) | Solving on a GPU-less machine fails with `__cuda ... missing on the system`. That is the **virtual package**, not the build's absence. Needs `CONDA_OVERRIDE_CUDA` — including **at bake time**, since the image builder has no GPU either. |
| pmx submodules present | `alchemy`, `estimators`, `forcefield`, `gmx`, `model`, `mutdb`, `ligand_alchemy`, `analysis`, `scripts` | `pmx.scripts.workflows` does **not** exist on `develop`; it is not needed. |

## What carries over unchanged

Everything except the perses-specific build/sample layer is engine-agnostic and already tested:

- `protfep_bench.py` — RCSB staging, chain surgery, and the mutation-site check that **refuses** to
  stage if the residue at the site is not the one the benchmark names (it caught a chain-A/chain-D
  error); scoring; the qualification verdict.
- Reference values — **verified against SKEMPI 2.0** (Y29A 3.469 vs stored 3.4; Y29F corrected from a
  wrong-signed +0.5 to −0.13), with a checker that now fails any sign disagreement.
- `protfep_reduce.py` — ΔΔG from complex−apo, between-replicate SD, the verdict, and the per-leg
  **price** that finally makes this rung priceable.
- The Vast lane — launcher, label/leg-id matching, the reap, continuous S3 checkpointing.

The leg JSON schema is what couples them, so the pmx driver must emit the same keys
(`status`, `dg_kcal`, `gpu_hours`, `n_particles`, `s_per_iter`, `meta.benchmark`, `meta.environment`).

## What still has to be built

1. **`research/compute/Dockerfile.pmxfep`** — CUDA GROMACS from conda-forge (with
   `CONDA_OVERRIDE_CUDA` at build time), pmx from `git+https://github.com/deGrootLab/pmx.git@develop`,
   plus the usual awscli/boto3. Same bake-time sanity assertions as the perses image: fail the free
   build, not a paid host.
2. **`protfep_pmx.py`** — the driver: `pmx mutate` → hybrid structure, `pmx gentop` → hybrid topology,
   GROMACS equilibration, then λ-window FEP reduced with BAR. Equilibrium λ windows are preferred over
   pmx's non-equilibrium protocol for the first implementation: simpler control flow, and GROMACS
   `.cpt` files give natural per-window checkpoint/resume on a spot host.
3. **Checkpoint/resume shaped for GROMACS**, not openmmtools — the `.nc`-based resume in
   `protfep_run.py` does not transfer.
4. **The same staged ladder**: free CI build-test of the hybrid construction (CPU work — only the
   sampling needs a GPU) → smoke → pilot (the abort gate) → full set.

## Open question for the driver, worth settling deliberately

pmx's *published* protocol is **non-equilibrium** (fast-growth + Crooks/BAR), which is what its
benchmarks use and is generally cheaper. Equilibrium λ-window FEP is easier to drive and checkpoint.
Start equilibrium; if convergence is poor or the cost is unattractive, the non-equilibrium path is the
documented fallback and pmx has the estimators for both (`pmx.estimators`). Record whichever is used
in the leg JSON — the two are not interchangeable when quoting a number.


## What the ladder actually cost to get working (2026-07-24)

Seven distinct failures, six of them caught on FREE CI. This is the build-test earning its place:
only the alchemical sampling needs a GPU, so the entire CPU half — staging, pdb2gmx, pmx mutate,
gentop, solvation, minimise/NVT/NPT — is provable for $0 before a host is rented.

| # | Where | Failure | Root cause | Cost |
|---|---|---|---|---|
| 1 | bake | `No module named 'pmx'` | `RUN pip install ... \|\| true` — the tolerant exit applied to the whole chain, so a FAILED install made a SUCCESSFUL layer | $0 |
| 2 | bake | Dockerfile parse error | multi-line `python -c` payload; Dockerfile has no continued quoted strings | $0 |
| 3 | build-test | `forcefield path ... not found` | pmx's data layout differs by release; the GMXLIB guess was conditional and only warned | $0 |
| 4 | build-test | `IndexError` in `pmx.molecule.__getitem__` | pmx copies coordinates onto the hybrid residue BY ATOM NAME; `pmx mutate` ran before `pdb2gmx`, so naming was not the force field's | $0 |
| 5 | build-test | `12 missing atoms ... Y2A 29` | `-ignh` on pass 2 stripped the hybrid's vanishing hydrogens that pmx had just placed | $0 |
| 6 | GPU smoke | grompp rejects the mdp | vdW softcore with a nonzero coul-lambda needs `sc-coul`; the ligand decharge-then-decouple answer does not transfer to a residue mutation | $0.02 |
| 7 | (earlier) | leg looped, billing | smoke's label and LEG_ID diverged, so the reap never matched it | ~$0.05 |

| 8 | build-test | 19 grompp errors in `topol_Protein_chain_D.itp` | `pdb2gmx` splits the topology per chain; `gentop` converted only the top-level file, so the mutated chain's own `.itp` stayed wild-type. `-merge all` + a guard that refuses if split files exist | $0 |
| 9 | Vast | complex host sat 36 min at `cur_state=stopped`, image pull frozen at `Waiting` | Vast's create/start race — the start PUT can be lost while the create finishes, leaving a box that never runs. NOT outbid (`min_bid` 0.24 < our 0.3015), so nothing would ever have resumed it. Re-issuing start is idempotent and fixed it in one call | ~$0.21 |

| 11 | CI | the reduction was never committed; the pilot's ddG lived only in a CI log | `git diff --quiet -- <path>` compares the working tree to HEAD **for tracked files only** and reports "no change" for a file git has never seen. The artifact had never been committed, so every collect since the lane was built printed "no change to commit" and discarded it. Stage first, test `--cached` | $0 |
| 12 | fleet | a 10-leg launch put 2 legs on machine 53989 and a 3rd on 11892; all refused to start | Vast offers are per GPU **slot**, and $/ns selection is per-leg with no memory, so the single cheapest machine wins several legs of one fleet. A host advertising slots it cannot schedule accepts every rental and refuses every start — so the failure **scales with fleet width**. One leg per machine per launch | ~$0.05 |
| 13 | fleet | a relaunch meant to replace 3 dead hosts re-rented all 10 legs | The launch-time skip only knew about legs whose result was already in S3; the 7 still RUNNING were invisible to it, so each got a second instance on the same leg_id and S3 key. Skip in-flight legs too, and dedupe in collect keeping the oldest | ~$0 (the first fleet's hosts had already been reaped, so the leg ids never actually overlapped — the hole was real, the damage was not) |

Failures #11–13 share one shape and it is worth naming: **each was a guard that reported success while
doing nothing.** A diff that cannot see untracked files, a selector with no memory across a fleet, a
skip list that knew "finished" but not "running". None of them errored; all of them printed a
reassuring line. That is strictly more dangerous than a crash, because the board looked healthy
while the deliverable was being dropped, the fleet was self-colliding, and the bill was doubling.
The lesson generalises past this lane: a guard must be tested against the case it exists to catch,
not merely against the happy path where it has nothing to do.

Failure #8 is the one that explains the whole shape of the lane: **the apo leg always worked and the
complex leg never could**, because apo is a single chain and has no per-chain split to get wrong. It
was found in one free build-test run, after three paid GPU failures, purely because the build-test was
extended to cover the complex environment as well as apo. Cover every environment the production run
uses, or the free tier only proves the easy half.

| 10 | Vast | two hosts in a row sat at `cur_state=stopped` through ~13 start PUTs that all appeared to succeed | Vast answers a start it cannot satisfy with **HTTP 200** and `{"success": false, "error": "resources_unavailable", "msg": "...state change queued."}` — the machine has no free GPU and the start is QUEUED. Both the nudge and `gpu_backend._ensure_running` discarded that body, so a capacity wait was indistinguishable from a working start | ~$0.45 |

Failure #10 produced a **wrong action of mine**, which is the part worth remembering. Because the
body was discarded, the stopped-box guard read a capacity wait as "the nudge is not taking" and
destroyed the host after 45 minutes — and would have destroyed every replacement for the same
reason, since the cause was never the host. The repo's standing rule (**always wait out spot
capacity**) applies directly: a queued instance bills storage only (`instance.gpuCostPerHour` is 0
in the record) and starts by itself when a slot frees. The generalisable lesson is narrower than
"read the docs": **an API that signals failure inside a 200 body turns every discarded response into
a silent wrong branch.** The forensic dump had already ruled out the obvious causes — `is_bid` true
with `dph_base` 0.0553 over a `min_bid` of 0.0442, `rentable` true, reliability 0.99 — and still
could not explain it, because the explanation was never in the instance record.

### The $/ns work, applied here — and one negative result (2026-07-25)

The 2026-07-24 selection change (rank offers by measured cost per ns, not by $/hr) **is** active on
this lane and is why its spend is low: the complex leg sits on an RTX 3090 at a $0.044212 floor =
**$0.002953/ns**, against the 4090 alternative at $0.14889 = **$0.004731/ns**. A 4090 needed a floor
below **$0.0929/h** to win, so ranking by $/hr would have picked the cheap card only by luck.

What was *not* using it was the BID. `vast_bid_optimizer.py` is imported by nothing that launches;
the live path bids a fixed `min_bid × VAST_BID_FLOOR_MULT`, a constant that knows nothing about the
card it is bidding on — so a slow card can be bid past the point where a faster one would have been
cheaper per ns. `protfep_vast_launch.value_ceiling_bid` closes that: bid up to where this card's
$/ns equals the best alternative on the market right now, and no further.

**The negative result is the useful part.** Applying it raised the stuck leg's bid from $0.0553 to
$0.0698 (+26%, and free in $/ns terms by construction) — and the instance *still* returned
`resources_unavailable`. So the wait is not a thin-margin auction we can outbid; that machine's GPU
is genuinely occupied. Two consequences worth carrying forward:

- **Do not reach for the bid when a start is queued.** It was the obvious lever and it does nothing.
  The `resources_unavailable` body, not the bid, is the thing to read.
- **Do not WAIT it out either — that was this lane applying the wrong market's rule.** The repo's
  standing "always wait out spot capacity" rule is written for **AWS managed spot**, a *pool* where
  you have no host choice and waiting is the only move. Vast is not a pool. The 2026-07-24
  reservation-price retraction says it directly — *"Vast is ~23 independently-priced RTX 4090 hosts
  visible at once, so you do not wait for a price, you pick a host"* — and the price history says
  the same from the other side: **the floor is FLAT** (RTX 4090 daily lows $0.1356–$0.1689 over 20
  days, 17/20 at the trough), so a different host today costs what this one will cost tomorrow.
  Queueing behind an occupied machine buys nothing and delays everything.
- **Selection had no availability term, and that was the binding gap.** `_select_cheapest_offer`
  ranked purely on $/ns; a machine that cannot schedule us has *infinite* realised $/ns, which the
  metric cannot see, so it kept winning and kept failing to start. Fixed with
  `ResourceSpec.exclude_machine_ids`, fed from a `_blocked_machines` list that `collect` records
  whenever a start comes back `resources_unavailable`. The cheapest offer on the board and the
  cheapest way to actually finish a leg are not the same quantity.

Failure #9 is worth reading as a monitoring lesson rather than an infrastructure one. The board showed
`loading` for 36 minutes and that was indistinguishable from a healthy pull, because it printed a
STATE without a REASON and a timestamp without an AGE. Three fields — `intended_status`, `min_bid` vs
price, and the marker's age in minutes — turned an unexplained stall into a one-call fix. A status
board that cannot separate "slow" from "stuck" is a liveness check wearing a progress check's clothes.

Two more lessons worth keeping. **A tolerant exit on a load-bearing step is worse than no check at all** —
failure #1 sailed on to fail three layers later with a misleading error, and
`tests/test_dockerfile_hygiene.py` now enforces the class. And **`-missing` would have "fixed" #5 by
building an INCOMPLETE topology** — a green run on bad physics, which is the failure mode this whole
ladder exists to avoid.
