# RUNG 2b on Vast — the 4 fs ternary test, and what it corrects in the cost base

**Lane:** `gpu-ternary-fep-vast.yml` → `ternary_vast_launch.py` → `run_ternary_leg.sh` → `nr4a3_ternary_fep.py`.
**Provider:** Vast RTX 4090 (trimcrae, 2026-07-25 — all production GPU runs on Vast).
**Status of each number below is stated explicitly: DERIVED FROM CODE, MEASURED, or PENDING.**

This file is the evidence for the RUNG 2b entries; STRATEGY.md and `pricing.md` own the live figures and should
point here rather than restate the derivations.

---

## 1 · The 4 fs saving is ~1.56×, not 2× — DERIVED FROM CODE, and it changes the RUNG 2b headline

STRATEGY's cost lever 1 says: *"Iterations are timestep-independent (2.5 ps/iter), so 4 fs is exactly half the
force evaluations → ~$8.8/edge → ~$4.4."* The first clause is right and the conclusion does not follow, because
**it applies to production only**.

**The mechanism, from the code rather than from the claim.** `rbfe_spot_driver._iters_from_time` computes

```python
steps_per_iter = integrator.n_steps                 # = time_per_iteration / dt, fixed when the move is built
timestep       = from_openmm(integrator.timestep)
total_steps    = get_simsteps(sim_length, timestep, steps_per_iter)
return int(total_steps / steps_per_iter)
```

so `iterations = sim_length / time_per_iteration` — the two dt's cancel. That is the timestep-independence.
**But the warmup is measured with the WARMUP integrator** (`rbfe_spot_driver.py:365-366`), and the reduced-dt
warmup is built by overriding `.timestep` on a move whose `n_steps` was already fixed at the PRODUCTION dt
(`rbfe_spot_driver.py:349-351`). So the warmup covers `equilibration_length` **in real time at 1 fs**, and its
step count does not depend on the production timestep at all.

For the as-run protocol (`EQUILIBRATION_NS = 1.0`, `PRODUCTION_NS = 5.0`, `nr4a3_ternary_fep.py:358-359`), per
replica:

| production dt | warmup steps @1 fs | production steps | total | leg cost |
|---|---|---|---|---|
| 2 fs | 1.00e6 (800 iters × 1250 steps) | 2.50e6 (2000 × 1250) | **3.50e6** | 1.00× |
| 4 fs | 1.00e6 (1600 iters × 625 steps) | 1.25e6 (2000 × 625) | **2.25e6** | **0.643×** |

**Leg-level speedup = 3.50/2.25 = 1.556×, not 2×.** Asserted by
`tests/test_ternary_vast_launch.py::test_four_fs_speedup_is_not_two_because_the_warmup_does_not_shrink`, and the
same test shows the ratio only approaches 2× as the warmup goes to zero.

**Consequence for the ladder:** the 4 fs ternary leg is ~0.64× the 2 fs leg, not ~0.5×. Whatever the 2 fs base
is, the 4 fs base is that × 0.643.

## 2 · The as-run leg is 2800 iterations, not 2400 — DERIVED FROM CODE

STRATEGY's ternary basis row says *"Leg length confirmed at 2400 iterations (400 equil + 2000 production at
2.5 ps/iter)"*. The 400 is what you get if the warmup runs at the **production** timestep. The as-run valB
protocol sets `warmup_timestep_fs=1.0` against `timestep_fs=2.0`, and by §1 that makes the warmup **800**
iterations, each with the **same 1250 steps** as a production iteration — i.e. the same wall time per iteration.

So the as-run 2 fs leg is **800 + 2000 = 2800 iterations of equal cost**, and a leg priced as `2400 × s/iter`
understates it by **~17 %**. This is a pure bookkeeping correction to the *count*; it does not change the
measured per-iteration rate, and it is the same correction in both timestep arms, so it does not affect §1's
ratio.

At 4 fs the count is **1600 + 2000 = 3600 iterations**, but each is half the steps — which is why iteration
counts are a misleading unit here and **steps (force evaluations) are the right one.** Any future per-leg price
should be built from steps × measured seconds-per-step, not from an iteration count carried between protocols.

## 3 · Why the warmup checkpoint interval is per-mode — DERIVED, to be confirmed by measurement

A commit costs a reporter sync plus a ~25 MB `.nc`/`.chk` pair copied and PUT to S3; the MD between commits
costs `interval × seconds-per-iteration`. The GCP lane's warmup interval of **8** was chosen against an
800-iteration warmup. At 4 fs the warmup is **1600** iterations, so 8 would mean ~200 commits. The Vast lane
therefore uses **64** for `edge` (25 commits; first resumable snapshot ~8 min in, far inside a preemption
window) and keeps **8** for `probe` — partly because 48 must remain a multiple of the interval, and partly
because a short interval is exactly what **measures** the per-commit overhead. The probe's `[timing]` lines
versus its wall clock give that number; it is **PENDING**, not assumed.

## 4 · The first NR4A-adjacent ternary rate on Vast — PENDING

STRATEGY flags that the ternary cost base is a **SMARCA2/VHL 8G1Q** rate being used to price **NR4A** ternaries
— *"the same move that just cost 2.6× on the binary lane"* — and says not to treat it as transferable until an
NR4A ternary leg has been timed. This lane records per-phase `median/min/max/mean` seconds-per-iteration into
every `leg.json` (`timing.warmup`, `timing.production`) together with the card name, so the rate is a
deliverable rather than a log line.

Note what this lane can and cannot settle: `calib_hi_to_lo` **is** the SMARCA2/VHL 8G1Q system, so it re-measures
the *existing* basis on a full leg rather than transferring it to NR4A. It removes the "rate came from a
60-iteration probe" caveat; it does **not** remove the NR4A transferability warning. That still needs an
`nrv04_active_to_epimer__ternary_nr4a1` leg.

## 5 · Test status

| claim | status |
|---|---|
| 4 fs leg-level speedup = 1.556× | DERIVED FROM CODE + unit-tested |
| as-run 2 fs leg = 2800 equal-cost iterations | DERIVED FROM CODE |
| 4 fs production survives ≫40 iterations | **PENDING** — RUNG 2b stage 1 (probe, 200 iterations) |
| ΔΔG_coop at 4 fs agrees with the 2 fs value | **PENDING** — RUNG 2b stage 2 (matched edge) |
| measured s/iter for warmup and production on a Vast 4090 | **PENDING** — recorded by both stages |
| per-commit checkpoint overhead | **PENDING** — read from the probe |
