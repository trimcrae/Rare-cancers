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
| 3 | same, spot commit prefix | keyed `leg+seed+dt+clig+wu+salt`, **no direction** — a rev leg would have RESUMED the fwd trajectory and reported it as reverse | ⚠ **THE FIRST FIX DID NOT WORK — see §H. It shipped, read correctly, and left the bug fully live.** Now fixed runner-side with an assertion + a test |
| 4 | `ternary-setup-prime-cpu.yml` | `DIRECTION: fwd` pinned; setup-cache key is `tag=<leg>_<dir>_r<seed>`, so a rev leg needed its own prime and could never get one while the GPU lane fails fast on `RBFE_REQUIRE_PRIMED_SETUP=1` — **unsatisfiable from both ends** | `direction` input |
| 5 | `gpu-ternary-fep-gcp.yml` idempotent skip | `gcloud storage ls .../leg_${LEG_ID}_fwd_r${SEED}.json` — a rev leg found the **fwd** result, printed `TFEP_RESULT status=OK (idempotent-skip)` and exited after 37 s CPU with no MD | keys on `${DIRECTION}` |

**#3's first fix was ineffective and #5 cost two VMs.** And because the VM's service account lacks `compute.instances.delete`, the self-delete trap
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

### F.0 A comment that asserted a property the code did not have

The watchdog's body opened with:

```bash
set -uo pipefail          # NOT -e: one entry failing must not abandon the others
```

**GitHub's default shell is `bash -e {0}`, and `set -uo pipefail` does not clear an `-e` that arrived on the
invocation.** So `-e` was live the entire time and the comment was simply false — the purest form of this
audit's bug class, since the *stated* guarantee was the thing being violated.

It cost a run within minutes of deploying the progress census. On a leg with no commits yet,
`MAXW=$(... | grep ... | tail -1)` takes the failing pipeline's status (grep matched nothing, `pipefail`
propagated it), `-e` killed the watch entry, and the step died **24 seconds after printing the entry header,
with no verdict of any kind** — the silent skip the watchdog exists to remove, reintroduced by a wrong comment.

Fixed at the root — `shell: bash --noprofile --norc -uo pipefail {0}`, so the invocation matches the intent —
plus `set +e` in the body and `|| true` on the census greps as defence in depth.

Two things worth keeping straight, both settled by running them rather than by reading POSIX:

- A failing **non-final** command in an `&&` list is **exempt** from `-e`: `[ -z "$x" ] && continue` is safe.
  (So the `; true` terminators added alongside are defensive-only, and an earlier draft of this fix justified
  them incorrectly.)
- A bare **assignment from a command substitution** is *not* exempt — its status is the pipeline's. That is the
  construct that actually killed the run.

Checked the one other workflow with the same header, `gcp-reap-vms.yml`: it inherits `-e` too, but its only
`&&` lists are the exempt shape and its list/delete failures are already explicitly handled — and for a reaper,
failing loudly is the correct posture anyway. Left as-is.

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

---

## H. THE ONE THAT ACTUALLY HAPPENED: §A#3's fix never worked, and a rev leg resumed the FORWARD trajectory

**2026-07-25, 1:41 PM ET.** This is the most serious finding in this document, and it was found *by* the audit's
own remedies rather than by review — §A#3 was recorded above as **fixed**, the code read correctly, and the bug
was fully live the whole time.

### What happened
The reverse leg restored **the forward leg's committed production trajectory at iteration 2000**:

```
[spot-safe] commit store: .../commits/calib_hi_to_lo__ternary_vhl/0_dt2.0fs_clig0_wu1.0_v2pe   <- no _dirrev
[spot-driver] restore -> production@iter 2000
ValueError: Stored checkpoint System particles do not match those of the simulated System
```

It failed **only** because the fwd and rev hybrid Systems have different particle counts (this rev build maps
109 atoms), so OpenFE's `assert_multistate_system_equality` refused the restore. **Had the counts matched, the
rev leg would have resumed forward sampling and reported it as reverse** — a silent wrong answer in the
production lane, in the exact form §A#3 warned about. A third-party library's sanity check is the only thing
that stood between this and a fabricated antisymmetry result. Nothing in this repo caught it.

*(No data was corrupted: the failure occurs in `_get_sampler`, before `run_to_target`, so nothing was committed
into the forward prefix. Verified by the absence of commit lines in the run log, not assumed.)*

### The mechanism — a variable set in one shell and read in another
The VM startup script is built with an **unquoted** heredoc, `cat > /tmp/startup.sh <<SS`. In an unquoted
heredoc, unescaped `$VAR` is expanded **by the runner** as the script is written, while `\$VAR` survives into
the file to be expanded **by the VM**. The fix as shipped did:

```bash
DIRSUF=""; [ "$DIRECTION" != fwd ] && DIRSUF="_dir$DIRECTION"      # inside the heredoc -> executes ON THE VM
COMMIT_ENV="...wu${WARMUP_TS}${SALT:+_$SALT}${DIRSUF} ..."         # ${DIRSUF} unescaped -> RUNNER expands it
```

`DIRSUF` was assigned in the VM's shell and read in the runner's, where it had never been assigned. It expanded
to the empty string, the suffix vanished, and **nothing errored**. Every other prefix component — `SEED`,
`TIMESTEP_FS`, `CONSTRAIN_LIG`, `WARMUP_TS`, `SALT` — is a runner-level `env:` var, which is precisely why
`DIRSUF` was the only one that disappeared: it was the only one whose value depended on a shell assignment.

### Why nobody noticed for hours
Two independent concealments, both already named elsewhere in this document:

1. **A truncated log line (§D).** The workflow's own echo was
   `echo "spot-safe commit store: gs://$BUCKET/valB-6hax/commits/$LEG_ID/$SEED"` — it stopped at the seed and
   **never printed the suffix**. True, and useless. The real prefix appeared only in the Python's
   `[spot-safe] commit store:` line, deep in a detached VM's log.
2. **It needed a second condition to surface.** The rev leg's *first* attempt used no warmup override, so its
   prefix was `wu` while the forward data sits under `wu1.0` — no collision, and it died on an unrelated 2.0 fs
   warmup NaN instead. Setting `warmup_timestep_fs=1.0` to fix that NaN is what aligned the two prefixes and
   exposed this. **The NaN fix accidentally found the real bug.**

### The fix, and the check that was missing
The prefix is now computed **entirely in the runner**, before the heredoc, with nothing about it deferred to the
VM's shell, and the generated script carries the finished literal (auditable by reading it). Added:

- an **assertion before provisioning**: if `direction != fwd` and the prefix does not end in `_dir<direction>`,
  emit `::error title=COMMIT PREFIX LOST THE DIRECTION::…` and **exit before a GPU is bought**;
- the echo now prints the **full** prefix;
- `research/modalities/tests/test_commit_prefix_direction.sh` (10 checks) asserts on the workflow text — that
  `DIRSUF` is assigned *before* the heredoc line, that the commit env consumes the finished prefix and no longer
  interpolates `DIRSUF`, that the assertion exists, and that the echo is not truncated. **Verified it
  discriminates by restoring the exact pre-fix arrangement: 6 of its checks fail.**

### The lesson, which generalises past this repo
> **A fix that "reads correctly" is not a fix. §A#3 was marked fixed in this very document while the bug was
> live.** Where a value crosses a boundary — two shells, generation-time vs run-time, runner vs VM — the only
> acceptable evidence is an **assertion on the produced artifact**, not an inspection of the producing code.
> Add the assertion in the same commit as the fix.

### H.1 Was DIRSUF the only one? Scanned mechanically — yes, and the trap was already documented

The two-shell defect is decidable, so it was scanned for rather than reasoned about: extract the unquoted
heredoc body, collect every variable **assigned inside it**, and flag any that is also referenced **unescaped**
(i.e. runner-expanded). Two candidates came back, both false positives, and both instructive:

- **`CHARGE_METHOD`** — a runner-level `env:` key on the step, so the runner genuinely holds it. The apparent
  "assignments" are `env CHARGE_METHOD=$CHARGE_METHOD …` subprocess prefixes, not shell assignments read later.
- **`STAGE_CACHE`** — assigned with runner-side values baked into the literal, and **every use is `\$STAGE_CACHE`**
  (escaped, VM-side). The flagged line was the *comment* directly above it:

  > `# NOTE the backslash escapes: \$STAGE_CACHE must be evaluated ON THE VM. Unescaped ($STAGE_CACHE) the …`

So `DIRSUF` was the **only** instance — and this file already carried an explicit written warning about the exact
trap, a few dozen lines from where the DIRSUF fix violated it. **A prose warning is not a guard.**
`research/modalities/tests/test_heredoc_two_shell.py` is now the guard: it ignores comments and `env VAR=`
prefixes (the only two false-positive sources found), and was **verified to discriminate** — reintroducing the
DIRSUF pattern makes it fail, naming the variable, the line, and the fix.

---

## I. §B#1 reproduced a third time — in the annotation that reports the verdict

The watchdog now dispatches `mode=converge` then `mode=reduce` automatically when a leg lands, so the calibration
verdict can arrive with **no session awake**. That autonomy is worth nothing if the verdict is only readable by
excavating a log (§D), so `mode=reduce` gained a one-call `[REDUCE-VERDICT]` annotation.

**And the annotation shipped with §B#1's defect in it.** Its level was keyed on the gate's `decision` alone:

```python
level = 'notice' if verdict == 'PASS' else 'error'
```

But the gate's `decision` **deliberately excludes hysteresis** — the fwd/rev criterion lives on
`calibration_decision`, which is the whole reason §B#1 existed. So a PASS whose preregistered
`|ΔG_fwd + ΔG_rev|` criterion was **never measured** (`hysteresis_ok is None`), or was measured and **failed**,
emitted a **green notice**. Absent data reading as fine, for the third time in this document, in code written
*because of* the first two.

Fixed: quiet requires **both** a passing gate **and** measured, passing hysteresis, and a PASS with anything else
carries an explicit rider — *"GATE PASSED BUT THE PREREGISTERED FWD/REV CRITERION DID NOT … This is NOT a pass of
the calibration."* All four routings verified against **real reducer output**: ok → notice; unmeasured → error;
exceeded → error; wrong sign → error.

**Why it was caught this time:** the formatter was *exercised* against real gate output rather than read. Reading
it would not have surfaced this — the line is obviously correct unless you happen to remember that `decision`
excludes one of the criteria. Which is the same conclusion as §H, arrived at from the opposite direction:

> **Reading code cannot verify a claim about what it produces. Run it and assert on the output.**

---

## J. The real cause of the rev NaN was already written down — and a key that cannot catch its own mismatch

### J.1 Two GPU attempts spent rediscovering a documented result

Both 2026-07-25 rev attempts died at **warmup iteration 1** — at 2.0 fs (replica 0, state 1) and at 1.0 fs
(replica 0, state 7). Halving the timestep moved *which* λ window blew up and **not the iteration**, which is the
empirical signature of something other than a timestep ceiling.

`nr4a3_ternary_fep.py` already said so, in a comment, with a measurement behind it:

> *"the instability is the softcore alchemical (dis)appearing region in a large, rough homology-built assembly,
> and there is NO static predictor of the ternary timestep. **The fix that WORKS is NOT a smaller timestep**:
> relax the fully-interacting physical complex with plain MD BEFORE the alchemy (`ternary_preequil.py`,
> `use_preequil=1`). With the relaxed structure the calib leg ran warmup 48/48 at 1 fs → production 40/40 at
> 4 fs with zero NaN, **where every prior run died at warmup iter 1.**"*

"Every prior run died at warmup iter 1" is a verbatim description of both of today's failures. The cost of not
reading it first: two GPU attempts and ~40 minutes of L4.

Two related false leads, recorded so they are not re-run:
- **The `[hmr-diag]` line is misleading but not broken.** It prints `X-H bonds=0 constrained=0 UNCONSTRAINED=0`
  and concludes *"NO unconstrained X-H bonds found → 4 fs is safe"*. With `constraints=hbonds` every X-H is a
  *constraint* rather than a stretch term, so `xh_total=0` is correct — but `constrained=0` is computed as
  `xh_total - xh_unconstrained` and therefore reads **0 when the truth is "all of them"**. The file itself already
  flags that `xh_total == 0` is *ambiguous*, and the disambiguating counter (`count_morphing_xh`, the
  edge-discriminating one) runs **only** under `RBFE_HMRDIAG_ONLY=1` — i.e. never during a real leg. So a real
  leg prints a confident safety verdict from the statistic that cannot support it.
- **The edge has no morphing X-H.** valB_mini is a linker pyridine **N→CH**, so a hydrogen appears/disappears on
  a mapped heavy atom — which looks exactly like the unconstrainable bond that caps a timestep. It was already
  measured and refuted for this edge: `xh_total=0` with **4997 constraints**, and the alchemical valence force
  holds **28 bonds, none an X-H** (`rbfe_edge_timestep_scan.py`).

### J.2 `use_preequil` changes the system but is NOT in the commit prefix — and here the particle check cannot save us

The prefix is `<seed>_dt<dt>fs_clig<c>_wu<warmup_dt>[_<salt>][_dir<dir>]`. **`use_preequil` is absent from it**,
yet it selects whether the alchemy starts from the plain-MD-relaxed physical complex (`SETUP_VER=v2pe`) or the raw
one (`v1`). So a `v1`-started and a `v2pe`-started run of the same leg share a prefix.

**This one is worse than §H, not better.** In §H the fwd/rev mismatch was caught by OpenFE's
`assert_multistate_system_equality` because the two hybrid systems had different particle counts. Pre-equilibration
only **moves coordinates** — the atom set is identical — so the particle counts match and that check **cannot
fire**. A `v1` trajectory restored into a `v2pe` run would resume silently.

*Nothing is contaminated today:* both failed rev runs died before `run_to_target`, so neither committed a
generation. Verified from the absence of commit lines in their logs.

The existing convention encodes the provenance in the **salt** — fwd's prefix is `…_wu1.0_v2pe`, and that salt is
literally named for the v2 pre-equilibrated setup. That convention is what made today's confusion possible: the
rev relaunches passed `commit_salt=v2pe` while leaving `use_preequil` at its **default 0**, so the salt *said*
pre-equilibrated while `SETUP_VER` was `v1`. A salt is a human-maintained label, not a key.

Adding `use_preequil` to the prefix would orphan fwd's committed data (its prefix carries no `_pe`), so the fix
is to record the provenance **in the commit manifest** and refuse a restore whose provenance differs. **This is
now BUILT** — see §J.4. What else is in place:

- `use_preequil` is a **required** watch parameter, so a watchdog relaunch can never silently flip it. The list
  was renamed `_required_run_params` (the old `_prefix_keying_params` is still honoured) precisely because it
  outgrew "prefix-keying" — this param matters and is *not* in the prefix.
- The watch file's fields must reach the dispatch **unshifted**: the entry is serialised as a pipe-joined line and
  read back with `read -r A B C…`, so a disagreement between the format slots, the values and the variable names
  silently shifts every later field — `charge_method` landing in `use_preequil`. Checked now
  (`test_watchdog_validate.py`, verified to fail when one read variable is removed).

### J.3 And the fix is what fwd already did, so comparability is preserved

The worry that switching rev to pre-equilibration would invalidate `|ΔG_fwd + ΔG_rev|` — fwd and rev must be the
same transformation on the same system — resolves the right way: **fwd ran with `use_preequil=1`.** Its prefix's
`v2pe` salt and `SETUP_VER=v2pe` (set only by `use_preequil=1`) say so. Pre-equilibration is therefore not a
deviation from fwd; it is a *correction of the rev run back into agreement with fwd*. It fixes the crash and
restores comparability in the same change.

### J.4 The durable guard: a system fingerprint in the commit manifest

Recorded first as an open gap, then built. The scan for siblings found the hazard is **wider than
`use_preequil`** — three system-changing params are absent from the commit prefix:

| absent from the prefix | what it changes |
|---|---|
| `SETUP_CACHE_VERSION` | `v2pe` (alchemy from the plain-MD-relaxed complex) vs `v1` (raw) |
| `CHARGE_METHOD` | `nagl` vs `am1bcc` — different partial charges, i.e. a different Hamiltonian |
| `N_WINDOWS` | a different λ schedule |

So piecemeal prefix suffixes were the wrong shape. Instead `rbfe_spot_checkpoint.py` now hashes those params
(plus the prefix ones, as cheap redundancy) into a `system_fingerprint`, stamps it into **every** commit manifest
(`schema: 2`), and consults it in `restore_latest` — **against the manifest alone, before any download**, so a
mismatch costs nothing. One field covers all three backends (local/S3/GCS) because they share
`_BaseCommitStore.commit`.

**Two cases, deliberately treated differently.** The first implementation failed closed on both, which looked
more correct and was worse:

- **Stamped and DIFFERENT → refused unconditionally.** Positive evidence that the generation came from another
  configuration. No flag overrides it; the rejection names the differing fields and both values.
- **UNSTAMPED (pre-dating the field) → warn loudly, allow; refuse only under `RBFE_STRICT_PROVENANCE=1`.**
  Absence of provenance is not evidence of mismatch. Failing closed would have made **another session's already
  running leg refuse to resume after a preemption and discard paid GPU hours** — for a change it had no part in.
  For a running leg the generation was written by the dispatch that will resume it, so accepting is almost
  certainly right; the dangerous case is a human resuming an old prefix with changed params, which is exactly
  when the stamped branch fires. The unstamped population is finite and shrinking. **The ternary GPU lane opts
  into `RBFE_STRICT_PROVENANCE=1`**, having verified nothing unstamped needs resuming there (fwd is complete and
  the rev prefix holds no generations).

Note what this buys that OpenFE cannot: `assert_multistate_system_equality` caught the §H fwd/rev mismatch only
because particle counts differed. Pre-equilibration **moves coordinates without changing the atom set**, so
counts match and that check cannot fire. This is the only guard that covers it.

`tests/test_system_fingerprint.py` — 28 checks. The real checkpoint suite
(`rbfe_spot_checkpoint_test.py`) needs numpy + openmm and runs only in the AWS GPU workflow, so it cannot gate
this; the new test drives `restore_latest` through a **fake store** instead, needing no scientific stack, and
asserts the properties that matter: a mismatched generation is skipped **without being downloaded**, a prefix
holding a mix still resumes from the newest **compatible** generation rather than refusing outright, and no flag
excuses a real mismatch.
