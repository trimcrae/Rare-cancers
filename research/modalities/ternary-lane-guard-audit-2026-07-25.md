# Ternary-lane audit: guards, keys and fallbacks that report success while measuring nothing

**Date:** 2026-07-25 · **Trigger:** trimcrae — *"check for more bugs like this so we don't have to keep finding
them one by one."* Written after the reverse leg was blocked five separate times by the same defect shape.

## The bug class, stated precisely

> **A key, guard or fallback that ignores a dimension the data actually varies along — and therefore returns a
> confident answer about the wrong thing.**

Every instance shares three properties that make it expensive:
1. **It reports SUCCESS** (`status=OK`, `conclusion: success`, `True`) rather than erroring.
2. **The wrong answer is indistinguishable from the right one** without going outside the report.
3. **It survives review** because the code reads correctly for the dimension its author had in mind.

Two dimensions dominate here: **DIRECTION** (fwd/rev — new, so nothing was keyed on it) and **PRESENCE**
(absent data defaulting to pass rather than to unmeasured).

---

## A. DIRECTION-blind keys — 5 found, 5 fixed

The engine has supported `DIRECTION=rev` since it was written. Every blocker was a *caller*.

| # | site | what it did | fixed |
|---|---|---|---|
| 1 | `gpu-ternary-fep-gcp.yml` run invocation | `DIRECTION=fwd` hardcoded | passes `$DIRECTION` |
| 2 | same, dispatch inputs | no `direction` input existed | added (retired the confirmed-no-op `constrain_ligand_ch` for the 25-input cap, pinning `CONSTRAIN_LIG='0'` so existing `clig0` prefixes stay resumable) |
| 3 | same, spot commit prefix | keyed `leg+seed+dt+clig+wu+salt`, **no direction** — a rev leg would have RESUMED the fwd trajectory and reported it as reverse | `_dir<rev>` suffix, applied only when direction≠fwd so every existing prefix is byte-identical |
| 4 | `ternary-setup-prime-cpu.yml` | `DIRECTION: fwd` pinned; setup-cache key is `tag=<leg>_<dir>_r<seed>`, so a rev leg needed its own prime and could never get one while the GPU lane fails fast on `RBFE_REQUIRE_PRIMED_SETUP=1` — **unsatisfiable from both ends** | `direction` input |
| 5 | `gpu-ternary-fep-gcp.yml` idempotent skip | `gcloud storage ls .../leg_${LEG_ID}_fwd_r${SEED}.json` — a rev leg found the **fwd** result, printed `TFEP_RESULT status=OK (idempotent-skip)` and exited after 37 s CPU with no MD | keys on `${DIRECTION}` |

**#5 cost two VMs.** And because the VM's service account lacks `compute.instances.delete`, the self-delete trap
no-ops, so each such exit leaves an idle L4 spot **billing zombie holding the single-GPU quota**.

### Direction-blind by design — checked and CORRECT, do not "fix"
- **stage cache** `stagecache/<leg>__<template>__seed<n>__v1.tar` — staging output (complex.pdb + ligands.sdf) is
  built from the same crystal for both endpoints, so it is genuinely direction-independent.
- **preequil cache** `preequilcache/<leg>__<template>__seed<n>__v2.tar` — relaxes the *physical* complex.
- **`ternary_fep_reduce._find_leg_files(leg, "fwd")`** — the coop cycle is deliberately built from fwd legs;
  rev is consumed only for hysteresis.

---

## B. PRESENCE-blind guards: absent data defaulting to PASS — 4 found, 4 fixed

| # | site | what it did | fixed |
|---|---|---|---|
| 1 | `ternary_fep_reduce.calibration_decision` | `hysteresis_ok = all(...) if hys else True` — **no rev leg ⇒ the preregistered "no unresolved fwd/rev disagreement" criterion PASSED by never being measured.** No rev leg had ever run, so it always passed | tri-state: `None` = unmeasured → INDETERMINATE with that reason |
| 2 | `ternary_fep_reduce._diagnostics_ok` | absent convergence report ⇒ `True`. The report was unproducible (unwired, missing `openfe`), so "all diagnostics pass" was satisfied by never measuring them | returns `None` when a report exists but is INCOMPLETE; gate routes `None` → BORDERLINE, not PASS |
| 3 | `calibration_gate` accuracy criterion | `\|mean − 0.944\| ≤ 1.0` admits `mean = 0` — a method predicting **nothing** passed (22% vs 23% for an accurate one: no discriminating power) | + `mean > target/2` and CI-excludes-zero; null 22% → 1.7% |
| 4 | `ternary_fep_convergence` health flags | `None` (not computable) counted the same as pass in `technical_failure` | `mandatory_unmeasured` / `diagnostics_complete` / `gate_note` |

**Verified after fixing** — the gate now separates all three states on identical data:

| diagnostics | on-target n=5 verdict |
|---|---|
| measured & clean | PASS |
| **incomplete (never computed)** | **BORDERLINE** |
| measured failure | FAIL |

and `calibration_decision` with no rev leg returns INDETERMINATE — *"forward/reverse hysteresis NOT MEASURED"* —
where it previously returned PASS.

---

## C. Stale-source fallbacks: recency preferred over identity — 1 found, 1 fixed

`gpu-ternary-fep-gcp.yml` postmortem selection:
```
NEWEST=$(... | grep -aE "${LEG_ID}_seed${SEED}" | sort | tail -1)   # name had NO direction
[ -z "$NEWEST" ] && NEWEST=$(... | sort | tail -1)                  # ANY leg's newest log
```
Postmortems were uploaded as `<leg>_seed<n>_<epoch>.log` — **no direction** — so fwd and rev were
indistinguishable; and with no match it silently substituted **any** leg's newest log. On 2026-07-25 that
returned a traceback at production iteration 520/540 for a rev leg **2 minutes old**, which could not have
reached iteration 520 for ~4.7 h. Caught on the arithmetic, not by the tooling.

Fixed: filenames carry `${DIRECTION}`; selection prefers the direction-keyed name, warns explicitly when it
matches a legacy direction-less one, and **says nothing was found rather than substituting a stranger's log**.

Note the near-miss: someone had already guarded live-vs-postmortem *precedence* ("the leg-wide postmortem is a
DIFFERENT (dead) run's log and must NOT override a live leg's") — but never the postmortem's *identity*.

---

## D. Verdicts readable only by log excavation — fixed

Not a wrong-answer bug, but it *caused* one: a 24-second cache restore was read as a passing hypothesis test
because the distinguishing evidence (step DURATION) sat in a log at an unpredictable depth. Verdicts now land in
**step conclusions** and **`::notice::`/`::error::` annotations**, retrievable in one API call:
- IAM write probe exits non-zero per-prefix
- tail emits `TERNARY-PROGRESS`, at **error** level when `live_vms=0` or a NaN appeared, and carries the
  preempt-vs-crash `death=` verdict
- `/var/log/tfep.log` (the log the startup script actually writes) is now dumped — the lookup list named three
  files, none of which exist, while the real one sat there at 4145 bytes

---

## E. Judged acceptable — recorded so they are not re-litigated

- `|| true` on `gcloud storage ls/cat` that gather **optional context** (lane listings, live-VM lists).
- `gcp-quota-check.yml` "Print quotas" is `set +e` with no failure path — it is a *print* step; the probe step
  beside it now carries the verdict.
- `verify-refs.yml` is `set +e` with no failure path. **Not audited today** — outside the ternary lane, but the
  same shape, so worth a look before its output is trusted.

---

## The standing lesson

Three independent times today, **step DURATION rather than status** was the only thing separating outcomes:

| duration | meaning |
|---|---|
| ~0.4 min + success | cache restore that ran **no build** (voided a hypothesis test) |
| ~0.5 min + failure | endpoint-construction radical |
| ~11.5 min + failure | a real, complete build that failed only on upload |
| ~37 s CPU + `status=OK` | the direction-blind idempotent skip |

**When a step's runtime is wildly inconsistent with the work it claims to have done, that is the signal — not
its conclusion.** Whenever a new dimension is added to this lane (a direction, a paralogue, a charge model, an
E3), grep every cache key, commit prefix, result filename, postmortem name and skip check for the *old* implicit
value before running anything.
