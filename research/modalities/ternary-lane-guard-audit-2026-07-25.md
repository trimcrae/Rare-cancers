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

---

## F. LIVENESS mistaken for PROGRESS — 1 found, 1 fixed

The watchdog (`ternary-leg-watchdog.yml`) originally classified a leg as healthy on the strength of *a VM
exists*. That is the same class one level up: a guard reporting success while measuring the wrong quantity.
All three of today's silent stalls presented as a perfectly healthy RUNNING VM — an am1bcc cold-cache wait
(~40 min at 0% GPU), a 25000-step minimize (~15 min at ~0% GPU), and the warmup-iteration-1 NaN. A liveness
watchdog would have reported "RUNNING, leaving it alone" through every one of them, indefinitely.

Fixed: the RUNNING branch now asks whether the leg is **advancing**, comparing the furthest committed
iteration against the previous pass (state in GCS, so it survives restarts). Two distinct alarms, because the
two failure modes have different signatures and different graces:

| condition | alarm |
|---|---|
| zero committed iterations, VM older than `SETUP_GRACE_MIN=75` | **SETUP STALL** — hung in env-solve/charge/minimize |
| committed iteration frozen ≥ `STALL_PASSES=2` passes (~30 min) | **STALLED** — MD not advancing |

Neither relaunches: a relaunch of a hung setup hangs identically. Both **fail the job**, so GitHub's own
workflow-failure notification is the alert path — an `::error::` annotation nobody opens is no better than the
silent stall the watchdog exists to remove. RUNNING and DONE stay green so the mailbox stays quiet.

Note the census had to be made **direction-aware** for the same reason as §A: a direction-blind census reads
the fwd leg's far-further trajectory and reports a dead-stopped rev leg as racing ahead.

### F.1 The octal trap — found by the test, not by review

Writing the test for that census turned up a live defect in it. The commit store pads iterations to 8 digits
(`iter-00000520`), and **bash reads a leading-zero literal as octal**:

- `$((1000000 + 00000520))` → `1000336` — a silently *wrong* progress scalar;
- `00000999` is not octal at all → the arithmetic **errors**, `PROG` is never assigned, and `set -u` then kills
  that watch entry mid-loop — reintroducing the exact silent-skip this workflow was built to remove.

Fixed with `$((10#$MAXW))` / `$((10#$MAXP))` (and the same guard on the relaunch counter, as free insurance).
`research/modalities/tests/test_watchdog_census.sh` locks in both properties — direction isolation and base-10
parsing — and **extracts the census block from the workflow at run time** rather than copying it, so it cannot
pass against a stale duplicate of logic the workflow no longer has.

The pre-existing `WMAX`/`PMAX` in `gpu-ternary-fep-gcp.yml` and `gpu-rbfe-gcp-tail.yml` were checked: they are
only ever interpolated into display strings, never into `$(( ))`, so they are cosmetically zero-padded but not
wrong.

---

## G. `verify-refs.yml` — audited, and fixed

Flagged in §E as un-audited. Checked: it is `set +e` with no failure path, and it is the **same shape** — every
`curl` can time out or hit a Crossref/Europe PMC outage, the `node` one-liners then print `PARSE-ERR` or an
undefined DOI, and the job still ends **green**.

Its blast radius is genuinely smaller than the ternary guards': `permissions: contents: read`, it commits
nothing, and nothing consumes its output automatically. So the failure is not a corrupted artifact — it is a
**human reading a green "Verify external references" run as though it verified something**, when most lookups
may have returned nothing. That is §D's defect (a verdict readable only by excavation), and it is exactly the
kind of run whose conclusion gets trusted.

Fixed proportionately — not a rewrite. Output is mirrored to a file and censused at the end:
`crossref_titles`, `dois_resolved`, `parse_errors`, `undefined_dois`. Section 1 has a **fixed list of 6 DOIs**,
so its expected count is knowable rather than inferred: fewer than 6 resolved is an `::error::` **and a job
failure** ("do NOT treat this run as having verified anything"). Parse errors elsewhere raise a `::warning::`
naming the specific unverified references, since those sections are searches with no knowable expected count.

One implementation trap worth recording: the mirror needs the real stdout/stderr saved on fds 3/4 **first**.
Both 1 and 2 get pointed at the same `tee`, so with no saved copy there is nothing to restore them to — the
obvious `exec 1>&2` merely re-points stdout at the tee, its stdin never closes, and the `wait` hangs forever.
Verified locally that the restore terminates and the census counts correctly (a would-be CI hang, caught on the
bench).

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
