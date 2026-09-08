# R2 · Plan and cost

## 1 · The design I would have run, and its price

The specification's §4 deliverable is a convergence-extension arm: the same frozen construct set,
longer trajectory (and/or more discarded equilibration), until
`fraction_exceeding_pooled_sd` ≤ 0.20.

Retained per-run cost, quoted from `C161_r1`: **3,392 s wall** at 1,010 frames × 7,000 steps,
CPU, 4 threads. This container has exactly 4 CPUs, so runs are serial — wall time is the sum.

| candidate design | runs | length | wall (serial, 4 threads) |
|---|---|---|---|
| full re-sweep at the same length | 55 | 1× | **51.8 h** |
| full sweep at doubled length | 55 | 2× | **103.6 h** |
| targeted: the 14 exceeding runs at doubled length | 14 | 2× | **26.4 h** |
| targeted: the 14 exceeding runs, one extra 1× segment appended | 14 | +1× | **13.2 h** |

Time remaining when this was computed (2026-09-08T22:52:09Z → 2026-09-09T02:37:19Z):
**3.75 hours.**

**The smallest design that could honestly answer the question costs 13.2 h against 3.75 h
available — short by 9.5 h, a factor of 3.5.** A full re-sweep is short by 48 h. There is no
design in this family that fits, so the compute decision is settled by arithmetic alone,
independently of the environment gap in `PRECONDITION.md`.

## 2 · Why the cheapest row is still not cheap enough — and why it is also not clean

Even had it fit, the 13.2 h row has a scientific defect worth recording for whoever runs this
later. `pooled_replicate_sd_nu` is pooled across the primary constructs, and the convergence rule
is a fraction over **all 55** runs. Extending only the 14 exceeding runs would leave the panel
with two trajectory lengths in it, so the pooled SD — and therefore
`separation_threshold_nu` — would be computed across an inhomogeneous protocol. The frozen
prereg registers one protocol per panel. **A convergence extension must extend the whole panel**,
which puts the real floor at the 103.6 h row, not 13.2 h.

## 3 · What I ran instead — zero compute, zero protocol deviation

Because no new sampling was affordable or possible, I did the one thing that is both free and
legitimate: **re-score the retained panel with the frozen scorer, unmodified**, under the
alternative ν estimator the prespecification itself already registers.

- §2 of the prereg lists, as a *secondary, reported* readout, "ν over the second half of the
  trajectory". Every one of the 55 runs carries `nu_second_half` and `nu_half_vs_full_delta`.
- The second half of each trajectory is the **later-time** estimate — exactly the direction
  Amendment 1's worry points ("a chain still collapsing out of its initial configuration",
  TAF15 1–161 reading ν 0.337 whole vs 0.289 second half).
- So substituting `nu := nu_second_half` and passing the panel through the **unaltered**
  `score()` is a bounded, prespecified-readout sensitivity test of whether the drift the
  convergence block records is capable of moving the verdict.

Cost: **under 1 s** (`checks/11`, `checks/12`, both exit 0). No guard, gate, range or threshold
was touched; `emc_condensate_calvados.py` is byte-identical (see `IDENTITIES.md`).

**What this test is and is not.** It *is* evidence about whether the recorded drift is systematic
or noise, and whether an estimator taken from later in the trajectory moves any primary pair. It
is **not** the §4 deliverable and does not discharge the PROVISIONAL label: the second half is
still drawn from the same 1,010-frame trajectory, so it cannot exclude that both halves are still
relaxing in a common direction. Only longer sampling can do that, and longer sampling was not
affordable. The residual is stated in `FINDING.md`.

## 4 · Nothing was appended to the committed artifact

`research/modalities/emc-condensate-calvados.json` is **unchanged**. I am its exclusive writer for
this task and I chose to write nothing: there is no new run block to append, because no run was
executed. The sensitivity re-score is a derived reading of the existing 55 runs and lives here,
in this artifact directory, not beside them.
