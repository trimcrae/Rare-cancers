# NR-V04 retrospective — SESSION HANDOFF (2026-07-24 night)

**Read this first if you are picking up the NR-V04 retrospective.** It is the state of play, the exact
commands to resume, and the traps that cost this session an evening. Everything below is on `main`.

**One-line state:** the holdout is fully built, preregistered and de-risked; **no retrospective leg has yet
produced a result**; three infrastructure defects that prevented that are fixed but **unproven on hardware**;
nothing is launched.

---

## 1. What this rung is

nr4a3-program-map.md RUNG 4, schedule id `nrv04_retrospective`. Known answer (Wang 2024): NR-V04 degraded **NR4A1**,
spared **NR4A2/NR4A3**. No solved ternary, no paralogue-resolved α — so the holdout can only test
**directional concordance**, never recovery of a measured quantity.

**The design point is a measured confound, not the phenotype.** Leg 0 established that celastrol's reactive
**Cys551 is unique to NR4A1** (NR4A2 → Tyr, NR4A3 → Thr, no Cys within ±5). Celastrol *cannot* form the adduct
on the paralogues, so reproducing the phenotype would prove nothing. The panel therefore **decomposes**:

| stage | contrast | why |
|---|---|---|
| **R1** (primary) | NR4A1 vs NR4A2 vs NR4A3, **all non-covalent** | the only contrast that tests whether the *workflow* discriminates paralogues with the warhead confound held off — which is what a prospective non-covalent NR4A3 campaign depends on |
| **R2** | NR4A1 covalent vs non-covalent | how much of the phenotype is warhead chemistry |
| **R3** | epimer arms | **conditional** — only runs if R1 shows an ordering; needs 6 new co-folds |

**A null R1 is a registered, publishable outcome**, not a failure: it localises NR-V04's selectivity to warhead
reactivity. Do not let it be re-narrated as a method failure.

Authority: [`nr4a3-nrv04-retrospective-prereg.md`](./nr4a3-nrv04-retrospective-prereg.md) (prose, wins) +
[`nrv04-retrospective-prereg.json`](./nrv04-retrospective-prereg.json) (machine mirror).

---

## 2. What is DONE

- **Preregistration frozen before any data** — panel, endpoints, statistics, blinding, verdict tiers, honest
  failure semantics, claim ceiling. Enforced in code, not just prose:
  `nrv04_retro_panel.py` (24 authorized units), `nrv04_retro_gate.py` (exact permutation test at the
  **co-fold-model** level — the leg is *not* the unit of independence), `nrv04_retro_blind.py`.
  Offline tests: `tests/test_nrv04_retro.py`, `tests/test_nrv04_retro_launch.py`.
- **Two data-invalidating defects found and fixed** — see
  [`nrv04-cofold-chain-forensics-2026-07-24.md`](./nrv04-cofold-chain-forensics-2026-07-24.md). Short version:
  the co-folds contained **14-3-3 epsilon** where Elongin B belongs, and the E3/target chain split was
  **positional and pointed at Elongin C**. Both produced numbers rather than errors.
- **Co-folds regenerated clean** → `nrv04-descriptive-v4` (9 models: nr4a1/nr4a2/nr4a3 × seeds 1,2,3),
  verified A=254 (NR4A LBD) / E=213 (VHL) / **F=118 (Elongin B)** / G=112 (EloC).
- **`retro_stage_test` PASSES** on v4 — the identified split resolves the NR4A LBD on all three arms.
- **Vast co-fold lane built** (`cofold` mode) so co-folding no longer routes to SageMaker by default.
- **Chain-split fix confirmed on real hardware** — a smoke leg's committed JSON reads
  `target=['A'] e3=['E','F','G'] explicit=True target_lys_nz=13`.

## 3. What is NOT done — and the honest reason

- **No retrospective leg has produced a result.** Three pilot attempts died (see §5).
- **The covalent feasibility panel's GO is WITHDRAWN.** Its readouts measured the Elongin C interface. The
  corrected 14-leg re-run is built (writes to `nrv04-covalent-results-chainfix`) and unlaunched. Until it
  lands, **RUNG 4's stated gate is not satisfied by that rung**.
- **The three OOM/monitoring fixes are unproven on hardware.** They are correct in code and tested offline,
  but no leg has yet run with them. **The next launch is still a pilot, not a fan-out.**

---

## 4. EXACTLY how to resume

All via `fusion-cpu-extras.yml`, `task=nrv04_vast_launch`. Dispatch with `ref=<your branch>` (an on-`main`
workflow runs the branch's version of the file + code).

```
# 0. FREE — confirm staging still passes before spending anything
   vast_launch_mode=retro_stage_test

# 1. PILOT ONE LEG (~$0.50). The fixes are unproven; do NOT skip to the fan-out.
   vast_launch_mode=retro_pilot   md_mode=run
   → pilot is retro_noncov_nr4a2 m1 r0 ON PURPOSE: the abort information is STRUCTURAL, and the
     assembler had never read a paralogue co-fold. Piloting NR4A1 leaves the real risk unexercised.

# 2. CHECK PROGRESS (not liveness) — prints per-leg phase markers + the chain split each leg used,
#    REAPS this lane's finished/stale hosts, and persists its readout to S3 + the run's artifacts
   vast_launch_mode=retro_collect
   → refuses to compute the paralogue contrast until every AUTHORIZED unit lands (prereg §4f,
     no interim analysis). The count is `nrv04_retro_panel.enumerate_units()` — do NOT re-type it here.
   → this is also the SUPERVISION TICK. While the fleet is billing, dispatch it yourself on the cadence
     the work needs; a `schedule:` cron does not supervise a billing fleet (CLAUDE.md §6).

# 3. FAN OUT the rest once the pilot completes end-to-end
   vast_launch_mode=retro_full    md_mode=run
   → gated on $/ns before anything is rented, and again per offer inside submit. A HOLD rents nothing,
     drops nothing and writes `nrv04-retro-market-hold.json`; re-dispatch when the board improves.

# 4. CORRECTED FEASIBILITY RE-RUN (~$6) — independent of the above, can run in parallel
   vast_launch_mode=full   cofold_prefix=nrv04-covalent-cofold
   nrv04_result_prefix=nrv04-covalent-results-chainfix   md_mode=run
   → the FRESH result prefix is mandatory: the launcher skips units that already have results, and the
     superseded numbers must stay readable beside the correction, not be overwritten

# DIAGNOSTICS
   vast_launch_mode=diag       vast_selector=<instance id or label substring>
   vast_launch_mode=stop_all   vast_selector=<id or label>   # ⚠ BLANK DESTROYS EVERY INSTANCE ON THE
                                                             #   ACCOUNT, including other sessions' work
   vast_launch_mode=cofold_audit          # re-verify E3 identity in any co-fold prefix

# CO-FOLDING ON VAST (needed for R3's 6 epimer models, ~$1)
   vast_launch_mode=cofold   cofold_output_prefix=<FRESH prefix>
   ternary_script=nrv04_ternary.py   ternary_extra_args="--skip-control --targets NR4A2,NR4A3"   seeds=1,2,3
   → refuses a prefix that already has objects: co-folds are a preregistered panel's inputs
```

**Cost ledger for what remains:** the retrospective's authorized panel (R1 only — see the note below);
corrected feasibility 14 legs ≈ **$6**; R3 co-folds ≈ **$1**. All under the ≲$50 autonomy threshold. Provider:
**Vast** for everything.

> **⚠ UPDATED 2026-07-31 — THE PANEL IS SMALLER THAN THIS FILE ORIGINALLY SAID.** AMENDMENT 3 defect 1 (dated
> 2026-07-25, applied in code 2026-07-31) **RETIRED the covalent R2 arm**: it is unbuildable on every available
> input, and while it stayed enumerable its 6 never-landing units kept `panel_complete` False and suppressed
> the R1 verdict permanently. The authorized panel is **R1 only**. Per rule 1 the count is not re-typed here —
> `nrv04_retro_panel.enumerate_units()` owns it and `nrv04-retrospective-prereg.json` mirrors it; the
> corresponding cost is the prereg §7 **R1** row. **Superseded, retained for the record:** the "**24 legs ≈
> $11**" and "**fan out the remaining 23**" figures above and below, which counted the retired arm.

Basis: the measured endpoint-MD leg, **~$0.43/leg on a 3090** from the completed 15-leg feasibility ledger
(`research/compute/pricing.md`). That basis **survives the 2026-07-25 repricing** — the retired 24-leg panel
came to ≈ $10.3 on it. Note the
**"4090 default / 3090 fallback" card rule was RETIRED on 2026-07-25**: rank *offers* on all-in `$/ns`, not
cards (a 3090 offer at $0.015/hr beats a 4090 at $0.13/hr despite being 2.10× slower). The launcher's offer
selection was untouched by that change, so every command above still runs as written.

---

## 5. Traps that cost this session an evening

1. **OOM kills leave no trace and can leave a billing instance up.** Three pilot legs died to the kernel OOM
   killer (bare `Killed` in the container log). RAM is now 48 GB (MD) / 64 GB (co-fold) — VRAM was never the
   constraint (<4 GB used). Worse: **the EXIT trap did not fire**, because the OOM killed the process, the
   container restarted, and the restart died at `git clone`. Instance 45749462 sat billing for ~2 h before
   being reaped by hand. **After any leg failure, run `diag` and check for survivors.**
2. **Monitoring that swallows its own errors is worse than none.** `mark()` ended in `2>/dev/null || true` and
   nothing captured stdout, so a dead leg was indistinguishable from a slow one — which produced two *wrong*
   intermediate hypotheses (slow image pull; broken S3 writes) before the real cause surfaced. Now stdout
   streams to `$RESULT_S3/run.log` every 45 s and the first `mark` is a hard preflight that aborts a leg which
   cannot write its own results.
3. **The workflow is at GitHub's hard 25-input cap — ZERO slots free.** It hit 26 (two sessions each added a
   few) and *every* dispatch 422'd, taking the whole Vast control plane down. `tests/test_workflow_input_cap.py`
   now fails locally instead. **If you need an input, MERGE two related ones** (that is how `vast_kill` +
   `diag_filter` became `vast_selector`) — do not delete a capability.
4. **A slow Vast host can spend >65 min pulling the image** and never create a container. Diagnose with
   `diag`, then kill and relaunch; a different offer usually boots in under a minute. The 6.7 GB baked MD image
   is the lever if this recurs — the co-fold lane's smaller base image booted instantly on the same account.
5. **The account is shared with concurrent sessions.** A sibling was mid-run on the protein-mutation FEP
   benchmark all evening. Always pass `vast_selector`; never run a bare `stop_all`.
6. **`retro_collect` reporting 0/24 does not mean the legs are dead** — check `diag` and the phase markers
   before concluding anything.

---

## 6. Things a fresh session will otherwise get wrong

- **The co-fold model, not the leg, is the unit of independence.** Two MD replicas of one model share a
  starting structure. The gate collapses to model-level means (n=3/arm) before testing — permuting legs would
  fake independence. Do not "improve" this by using every leg as a sample.
- **The one-sided direction is registered** (NR4A1 predicted *more* stable = lower E1 plateau). It is
  hard-coded. Do not flip it after seeing data.
- **`nrv04-descriptive-v3` and `nrv04-shakeout` are contaminated** and must never be a panel source. Staging
  rejects a 255-residue chain outright, but do not point anything at them.
- **Arm F (alchemical ΔΔG_coop) is BLOCKED** on the valB calibration PASS (calib addendum condition 7) and is
  *not* authorized by the retrospective prereg. Only Arm E (ensemble endpoint MD) is in scope.
- **Claim ceiling:** directional concordance/discordance only. No ΔΔG, α, cooperativity, affinity, or
  degradation claim; no efficacy/safety/window language. The claim linter enforces the vocabulary.

---

## 7. Open items that are trimcrae's, not yours

- Authorizing any spend above the ≲$50 threshold (nothing queued currently exceeds it).
- Anything outward-facing — submitting or posting the manuscript.
- A genuine strategic fork about the program's direction.

Everything else listed here is self-doable: build it, run it, verify it, commit it.
