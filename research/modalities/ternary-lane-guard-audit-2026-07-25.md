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

**⚠ CORRECTED 2026-07-25 3:25 PM ET — the original text here asserted a physical property without measuring
it, which is the exact failure this document exists to catalogue.** It claimed pre-equilibration "only moves
coordinates — the atom set is identical — so the particle counts match and OpenFE's check cannot fire." **That is
false.** Measured from the prime markers: the `v1` rev build is **146,020** particles and the `v2pe` build is
**141,968** — a difference of 4,052. The pre-equilibrated complex is re-solvated, not merely relaxed. So
`assert_multistate_system_equality` **would** catch a `v1`↔`v2pe` cross-restore, exactly as it caught §H.

The hazard is therefore **real but narrower than stated**: `use_preequil` is genuinely absent from the commit
prefix, so the two provenances do share a prefix — but the failure mode is a *loud* rejection deep in the restore
path, not a silent wrong answer. The genuinely undetectable cases are the ones where the atom set is unchanged:
**`CHARGE_METHOD`** (`nagl` vs `am1bcc` — same atoms, different partial charges) and **`N_WINDOWS`** in the cases
OpenFE does not check. Those are what §J.4's fingerprint is load-bearing for; for `use_preequil` it upgrades a
late, cryptic failure into an early, named one at zero download cost.

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

What this buys over OpenFE's own check — stated accurately, after the correction in §J.2:
`assert_multistate_system_equality` compares particle counts, so it catches any mismatch that changes the atom
set (§H's fwd/rev, and — measured — `v1` vs `v2pe`, which differ 146,020 vs 141,968 because the pre-equilibrated
complex is re-solvated). It is **blind** to a mismatch that preserves the atom set: `CHARGE_METHOD` `nagl` vs
`am1bcc` is the same atoms with different partial charges, i.e. a different Hamiltonian that would resume
silently. That case is what the fingerprint is load-bearing for. For the atom-set-changing cases it is still worth
having, because it converts a cryptic failure after a download and reporter validation into a named refusal
against the manifest alone.

`tests/test_system_fingerprint.py` — 28 checks. The real checkpoint suite
(`rbfe_spot_checkpoint_test.py`) needs numpy + openmm and runs only in the AWS GPU workflow, so it cannot gate
this; the new test drives `restore_latest` through a **fake store** instead, needing no scientific stack, and
asserts the properties that matter: a mismatched generation is skipped **without being downloaded**, a prefix
holding a mix still resumes from the newest **compatible** generation rather than refusing outright, and no flag
excuses a real mismatch.

### J.5 Provenance measured, comparability confirmed, and a gap in the leg record

The `v2pe` rev prime (2026-07-25 3:22 PM ET) and the `v2pe` **fwd** prime (2026-07-20) report **identical**
system identity:

| | fwd `v2pe` prime | rev `v2pe` prime |
|---|---|---|
| `n_particles` | **141,968** | **141,968** |
| `protocol_hash` | `52488cfc…` | `52488cfc…` |

So the rev leg now runs the same system, under the same protocol, as the leg it will be compared against — the
hysteresis test is well-posed. (The prime's `52488cfc…` differs from the *leg's* `a5ad9520…` because the prime
takes no `timestep_fs`; both primes agreeing is the relevant fact, and the leg recomputes its own hash with the
timestep at run time.)

This also confirms the diagnosis of the four failures beyond the pre-equilibration argument: at **146,020**
particles they were not merely a badly-equilibrated version of fwd's system, they were **a different system**.

**Gap found while checking this, and it is a real one.** The leg result JSON records `leg_id`, `environment`,
`morph`, `direction`, `seed`, `dg_morph_kcal`, `mbar_se_kcal`, `n_mapped_atoms`, `n_windows`, `protocol_hash`,
`protocol_settings` and `starting_model` — but **not `n_particles`, and not which setup cache it used.** The
reduce's per-leg forensic table exists precisely so a ΔΔG can be audited for cross-leg comparability, and the most
basic system-identity number is absent from it, which is why answering "did fwd and rev use the same system?"
required excavating a five-day-old CI log for a workflow that is not even the leg. The value is in hand at
leg-write time (`_ana_keys["n_particles"]`, already printed one line away). **Now closed:**

- the leg record gains `n_particles`, `setup_cache_dir`, `charge_method` and `setup_cache_version`;
- the reduction gains **`system_identity_consistency`** alongside `protocol_hash_consistency` — a separate check,
  because `protocol_hash` covers the OpenFE *settings* and not the *system*;
- legs written before these fields existed record `None`, and that reports as **`UNKNOWN` — "NOT VERIFIED"** —
  rather than being folded in as agreement. Absent provenance must not read as matching provenance; that is §B's
  defect, and it has already recurred three times in this document, so the tri-state is explicit and tested.

`tests/test_system_identity_consistency.py`, 16 checks, including that **today's actual situation is caught**:
a 146,020-particle `v1` rev leg against a 141,968-particle `v2pe` fwd leg returns `INCONSISTENT` and names both
counts, and that a `nagl`-vs-`am1bcc` mismatch — the atom-set-preserving case OpenFE structurally cannot see — is
caught too.

---

## K. The watchdog was silently disabled a SECOND time — by a length cap this time

**3:40 PM ET.** A dispatch returned:

```
422 Invalid Argument - failed to parse workflow: (Line: 71, Col: 14): Exceeded max expression length 21000
```

Line 71 is `run: |`. A `run:` block **containing an expression** (`${{ … }}`) is compiled as a **template**, and
the template is capped at **21,000 characters**, counting the raw indented block. The body had reached **23,453**
— grown mostly by the comments added while fixing everything else in this document — so the workflow stopped
parsing. And the failure mode is the familiar one: the dispatch errors, but a **`schedule:` cron on an
unparseable file simply never fires**, reporting nothing.

That is the **second** time this one workflow was silently disabled by a parse failure. §G was column-0 Python
inside the block scalar; this is length. Both times the body was inline, and both times **PyYAML parsed the file
happily**, so §G's YAML gate could not see it.

**Fixed structurally, not by trimming comments.** The body moved to
[`research/modalities/watchdog_run.sh`](watchdog_run.sh) (304 lines), leaving a 5-line `run:` that exports
`WATCH_REF` and calls it. A file has no expression cap, can be `bash -n`'d **directly** instead of scraped back
out of YAML, and cannot dedent itself out of a block scalar — so it retires both failure modes at once. The two
tests that used to extract from the YAML now read the script, and their extraction is
`textwrap.dedent`-based rather than assuming a hard-coded indent width.

### K.1 The condition that makes the cap bite — measured, because the first gate cried wolf

The obvious gate ("flag any `run:` block over 21,000 chars") immediately failed a workflow that **demonstrably
works**: `gpu-ternary-fep-gcp.yml` carries a **29,434-character** `run:` block and has been dispatching all day.

Measured rather than rationalised: that block contains **zero** `${{ }}`. A block with no expression is a plain
string, not a template, and is **not capped**. The watchdog's block had `${{ github.ref_name }}` — one
interpolation, which is what turned a 23 KB script into a 23 KB *template*.

So the gate checks **length AND the presence of an expression**. A gate that fires on a working workflow is worse
than no gate: it trains everyone to ignore it. `tests/test_workflows_parse.py` now reports 132 workflows, 0
failures, with a `[WARN … n from the cap]` on any expression-bearing block within 3 KB of the limit (one is, at
20,734). Verified to discriminate: re-inlining the watchdog body *with* its expression restored produces the
failure; re-inlining it without does not.

**The transferable rule:** when a value crosses into a templated context, its *size* becomes a correctness
property, not just its content — and the cheapest fix is to stop it crossing at all.

---

## L. §B#2 twice more in one morning, and a pocket-escape threshold applied for the third time to atoms with no pocket

Three findings from 2026-07-26, all the same class as §B#2 — *a key, guard or fallback that ignores a dimension
the data varies along, and returns a confident answer about the wrong thing.* Two of them were in code I wrote
the same morning, and one of those was in the diagnostic built to investigate the other.

### L.1 `mode=converge` analysed whichever direction had run longest

The discovery was `grep -a "$LEG" /tmp/lane.txt | grep -aE "/simulation\.nc$"`, then "take the highest
`iter-N`". The commit prefix carries the direction as a `_dir<dir>` suffix, so **both** directions' trajectories
are in that match set and the rule reduces to *whichever leg has run longest* — always the forward one. The
download directory was then named `${LEG}_sim_shared`, dropping the direction, so nothing downstream could tell.

Observed live: a `mode=converge` run dispatched for `direction=rev` reported `iterations_compared: [0, 2000]`
while the rev leg it was dispatched for sat at production ~300 (GH run 30201372471).

That last part is what made it dangerous rather than merely wrong. `ternary_fep_reduce.py` reads exactly this
`ternary_convergence.json` for `diagnostics_ok`, and the watchdog auto-dispatches `mode=converge` then
`mode=reduce` when a leg lands — so **the rev leg's hysteresis verdict would have rested on the forward leg's own
convergence.**

Fixed: direction-keyed selection, a direction-tagged report directory (fwd keeps its historical untagged name so
existing fwd reports stay comparable), and the cycle's fwd-only shared arms (`binary`, `solvent`) **skipped with
an explicit annotation** on a rev pass rather than silently substituted. The checkpoint fallback had the same
defect one level down and worse — `simulation.nc` does not carry positions, so pairing a rev trajectory with the
fwd checkpoint would have fed the pose-RMSD diagnostic coordinates from a different trajectory — so its search
root is now derived from the selected path's own commit prefix. `tests/test_converge_direction.sh` extracts the
real loop body from the workflow and drives it against a synthetic lane; reinstating the direction-blind grep
fails 6 checks and reinstating the lane-wide checkpoint grep fails 4.

### L.2 The phase labels in a brand-new timing diagnostic were a buffer artifact

`ternary-watch.json` carried **33.91 s/iter** as the leg's per-iteration cost and extrapolated the whole leg from
it. That was a *warmup* measurement, and the step count says warmup and production must cost the same: OpenFE
fixes the move's `n_steps` once from the **production** timestep (2.5 ps `time_per_iteration` / 2.0 fs = 1250
steps) and `rbfe_spot_driver` builds the warmup move as a **copy** with only `.timestep` changed, so warmup runs
the same 1250 MD steps at 1.0 fs. So a 1.95× gap against the GCS-marker rate was unexplained and needed a real
diagnostic, not a story. Two candidate mechanisms were killed by reading the source: the autostop convergence
check does run full MBAR per checkpoint boundary, but it is opt-in, off here, and would not engage until 40% of
the cap; and warmup checkpoints *more* often than production (every 8 vs 40), so commit overhead would make
warmup the slower phase, not the faster one.

The diagnostic (`iter_timing_profile.awk`, `mode=tail`, CPU-only, $0) then reported phases `pre-warmup` (n=448,
46.52 s) and `warmup` (n=490, 53.58 s) and **no production phase at all** — while GCS showed production at
320/2000 for the same VM. Root cause, from the driver's own lines rather than inference:

```
[spot-driver] warmup_target=800 (ci=8) prod_target=2000 (ci=40)
[spot-driver] restore -> warmup@iter 200
[spot-driver] WARMUP from iter 200 -> 800 (interval=8)
```
…and then nothing; newest `[barrier]` line `iteration 640/800`; 938 timing lines.

`run_spot_safe` defaulted `log=print`, and the VM runs the engine as `( ... ) | tee /tmp/tfep_run.log`, so
Python's stdout is **block-buffered** — while openmmtools' per-iteration progress goes through `logging`, whose
StreamHandler flushes every record. **Two differently-buffered writers into one pipe.** The driver's lines land
thousands of iterations late; openmmtools' are current. So the "pre-warmup/warmup" split at iteration 448 was
purely the buffer lag, the real phase change was invisible, and 320 production iterations were labelled warmup.

Fixed at the source (`log` defaults to a flushing print) and in the reader, which now emits phase-**free**
ordinal `SEGMENT` blocks as the trustworthy view, prints the GCS object census as the authoritative phase source,
and **warns out loud** when many timing lines precede the first phase marker or when a production marker is
absent. Logs already written — including the leg running now — still carry the artifact, which is why the warning
matters and not just the flush.

What the corrected reading actually says: per-iteration cost **rises** 45.3 s → 56.5 s over ~900 iterations and
plateaus, and end-to-end from GCS markers is **60.5 s/iter**. Every duration derived from 33.91 s was ~44% too
short. Figures corrected in `ternary-watch.json` with the superseded values registered in its `_rate_appendix`.

**The lesson worth keeping:** my diagnostic's own output window hid the evidence twice — first because a
`tail -60` filled with ~80 per-checkpoint `[barrier]` lines, then because the phase markers it keyed on were on a
lagging stream. *A diagnostic must ship the evidence for its own labels.* It now prints the driver lines in full,
the barriers collapsed to count+first+last, and the GCS census beside the profile.

### L.3 The binary leg's `technical_failure` is not established — a pocket threshold on atoms with no pocket, a third time

`LIG_RMSD_MAX_A` (4 Å) is a **pocket-escape** threshold, and `ternary_fep_convergence.py` has now had to stop
applying it to atoms that have no pocket three separate times:

| # | what it was applied to | reading | run |
|---|---|---|---|
| 1 | the whole 146 k-particle system | 78.94 Å, dominated by bulk water | 30156744299 |
| 2 | the SOLVENT leg's internal RMSD | `technical_failure=TRUE`; a free PROTAC in water is *supposed* to explore | 30167976061 |
| 3 | the BINARY leg's whole-ligand pose RMSD | `technical_failure=TRUE`, max 16.636 Å / med 6.987 Å | 30201372471 |

In the same cycle the ternary leg read max 2.765 / med 1.644 Å. A PROTAC in a **binary** complex has one warhead
bound; the linker and the distal warhead are in solvent **by construction**, because the second protein is
absent. So a whole-ligand RMSD over all 59 heavy atoms is dominated by the free end moving, and it cannot
distinguish

- *the bound warhead left its pocket* — real, and it would invalidate ΔG_binary and with it
  ΔΔG_coop = ΔG_ternary − ΔG_binary, hence r0's −0.534; from
- *the unbound end moved* — the expected physics of the binary state.

**So — at the time this section was written — `tech_fail=True` on the binary leg was neither confirmed nor
dismissed by the evidence that produced it.** That mattered because the r0 result depends on the binary arm and it
must not be quietly discounted *or* quietly accepted. §L.3a below records the answer, and it is **confirmed, not
dismissed**: the expectation stated in this section (that the free end was doing the work) is measured FALSE.
Everything from here to §L.3a is the reasoning that motivated the measurement, kept for that reason; the numbers
that settle it are in §L.3a.

The discriminating observable now exists: `_contact_ligand_rows` selects the ligand heavy atoms within 0.45 nm of
the receptor **in the reference frame** (never re-derived at the later frame — an escaping warhead would drop out
of a frame-B contact set and erase its own evidence), and the flag is the contact-moiety pose RMSD. Not a
loosening, and `tests/test_contact_moiety_pose_rmsd.py` pins all three directions: a flailing free end passes
*while its large whole-ligand value stays in the record*; a bound warhead displaced 1 nm still **fails**; and no
contact moiety at all is **UNMEASURED, never passed**, because a ligand with no receptor contact at t₀ is itself
a finding. Both numbers appear on the summary line with the flagged one marked, so which observable decides the
gate is legible without opening the JSON.

### L.3a THE ANSWER: hypothesis REFUTED. The binary leg's failure is real, and now it is measured on the right observable

The contact-moiety re-run landed (GH run 30202934339) and it says the opposite of what L.3 expected:

| leg | **FLAG** contact-moiety pose RMSD max / med (Å) | n_contact heavy | *info* whole-ligand max / med (Å) | tech_fail |
|---|---|---|---|---|
| `binary_vhl` | **16.327 / 4.333** | 30–52 of 59 | 16.636 / 6.987 | **True** |
| `solvent` | n/a (no receptor) | 0–0 | n/a | False — NOT APPLICABLE |
| `ternary_vhl` | 2.835 / 1.653 | 51–57 of 59 | 2.765 / 1.644 | False |

**The floppy-free-end explanation is wrong.** Restricting the measurement to the atoms actually in the VHL pocket
removed almost none of the excursion: 16.636 → 16.327 Å at the max. The atoms *in contact* are themselves moving
~16 Å in the worst replica. Two further reasons this is not a single-replica artifact or a threshold quibble:

- the **median** contact-moiety RMSD is 4.333 Å — above the 4.0 Å threshold on its own, so it is not one bad
  replica dragging a max. (It did drop from the whole-ligand median of 6.987, so the free end *was* contributing
  something — just nowhere near enough to explain the flag.)
- `n_contact` is **30–52 of 59 heavy atoms**, not the ~half a "one warhead bound, rest in solvent" picture would
  predict. In the binary state this PROTAC lies substantially against VHL, so there was less free-end leverage
  available than the hypothesis assumed. That premise was wrong too, and it was checkable — the number was
  simply never measured before.

So `calib_hi_to_lo__binary_vhl` has a **confirmed** technical failure of the observable the preregistered
threshold is actually about, and the ternary leg in the same cycle is clean at 2.835 / 1.653 Å with 51–57 atoms
in contact. **ΔG_binary is not a measurement of the intended binding mode**, and since
ΔΔG_coop = ΔG_ternary − ΔG_binary, r0's −0.534 rests on a broken arm.

**This is the outcome that makes the change worth having made.** The point of the contact-moiety observable was
never to clear the binary leg — it was to find out *which* of two indistinguishable explanations was true. It
returned the one I did not expect, and the guard it feeds is now failing for a reason that is measured rather than
assumed. Had it come back clean I would have had a pass I could defend; instead I have a failure I can defend,
which is worth more. Recorded as a flag rather than a revised r0 verdict because the rev leg's hysteresis result
is still outstanding, and the two together are what the valB_mini rescope decision rests on.

**What it does NOT establish:** *why* the bound moiety moves 16 Å. Candidates worth separating — a genuine
unbinding event in the binary complex (physics, and arguably the interesting result), versus a setup or
restraint problem specific to the binary arm — are not distinguished by a two-frame RMSD. The next diagnostic
should be per-replica time-resolved rather than endpoint-to-endpoint, because `iterations_compared: [0, 2000]`
cannot tell a drift from a jump and back. Not started; not spent on yet.

### L.4 One thing deliberately NOT changed mid-flight: `run_analyze()` on the GPU VM

The lane is otherwise CPU-factored — `prime`, `converge`, `reduce`, `forensic`, `calibchem`, `tail` and the
watchdog are all runner-only, $0, no VM. The one remaining GPU-billed CPU task is the leg's final MBAR inside
`run_analyze()`, which runs on the L4 VM while the GPU sits idle.

**Left alone on purpose, and it is worth writing down why rather than leaving it as an open loop.** The saving is
~10–30 min of L4 time, ≈$0.25 of trial credit. Against that, it is a change to the *completion path* of a leg
14 h in: the VM is what writes `leg_<id>_<dir>_r<seed>.json`, and that object is the sole signal the watchdog
uses to decide a leg is DONE and to fire `mode=converge` → `mode=reduce`. Getting it wrong does not cost $0.25,
it costs the leg's landing. The next relaunch picks up `main`, so a change made now *would* take effect at the
~2:40 PM boundary — which is an argument for not making it now, not for making it.

Note also that running the analysis on the VM is the **parity-correct** choice by CLAUDE.md's own rule: the
trajectory's producing environment and the analysing environment are the same interpreter, and a different
pymbar/openmmtools can change the MBAR numbers. Moving it to a runner is only safe *because*
`Dockerfile.ternaryfep` is byte-for-byte the spec the GPU legs build — so this is a small optimisation with a
real correctness precondition, which is the opposite of a free win.

**Revisit after the leg lands**, not before.

### L.3b Time-resolved: the binary leg's ligand LEAVES AND STAYS OUT in 8 of 12 replicas — and the ternary leg is the control that makes it mean something

GH run 30209580292, `mode=converge` with the per-replica contact-moiety series (25 frames, iterations 0–2000):

| leg | replicas ending beyond 4.0 Å | class counts |
|---|---|---|
| `calib_hi_to_lo__binary_vhl` | **8 of 12** | `DISPLACED_AND_STAYED: 5`, `INTERMEDIATE: 3`, `STABLE: 4` |
| `calib_hi_to_lo__ternary_vhl` | **0 of 12** | `STABLE: 12` |
| `calib_hi_to_lo__solvent` | — | no receptor in the stored subset, so a pose series has no referent |

Three things are settled by what is **absent**:

- **`JUMP: 0`.** No replica's displacement is carried by a single-frame discontinuity. A PBC-imaging or
  replica-indexing bug produces exactly that signature, and it is not there. **Not bookkeeping.**
- **`EXCURSION_AND_RETURNED: 0`.** No replica goes out and comes back. So the two-frame 16.327 Å was not the
  endpoint frame unluckily catching a transient — the displaced replicas *stay* displaced. **Not an artifact of
  comparing iteration 0 to iteration 2000.**
- **the ternary leg is `STABLE: 12`.** Same cycle, same 12 windows, same analysis code, same contact definition,
  same 0.45 nm cutoff, same reference-frame convention — and it comes back clean at 2.835 / 1.653 Å with 51–57
  atoms in contact. That is the control, and it is what turns "the binary number is large" into "the binary
  **leg** is different". Any explanation that blames the diagnostic has to explain why the diagnostic works on
  the leg next to it.

**So: in the binary complex the ligand progressively leaves its starting pose in the majority of replicas and does
not return.** ΔG_binary is not a free energy of the intended bound state, and since ΔΔG_coop = ΔG_ternary −
ΔG_binary, **r0's −0.534 is not a valid measurement of cooperativity.** Critically, this is *not* the kind of
defect more sampling fixes — the sampling is working, it is finding a state the calculation was not meant to be
about.

**What this does and does not change:**

- The **rev leg now running is still worth finishing.** It is a `dir=rev` leg of the *ternary* arm, and the ternary
  arm is the clean one (12/12 stable). The preregistered |ΔG_fwd + ΔG_rev| antisymmetry check remains a valid
  measurement of that arm.
- **ΔΔG_coop cannot be reported from this cycle** even with a perfect hysteresis result, until the binary arm is
  re-run with whatever addresses the departure. Those are now independent blockers, not one.

**Still open — and this is the next free question, not a spend:** *which λ were the departing replicas at when they
left?* Replicas exchange λ rather than coordinates, so a replica wanders the ladder, and the answer separates two
very different diagnoses: departures confined to weakly-coupled windows are a protocol-design issue (the binary
leg wants a restraint, and the ΔG may still be salvageable), whereas departures at the fully-interacting physical
endpoint mean the **binary complex model itself is wrong**. `reporter.read_replica_thermodynamic_states()` carries
the per-iteration λ assignment, so this costs reads of a file `mode=converge` already has open.

### L.3c λ attribution: the departure is alchemically FACILITATED but not alchemically CONFINED

GH run 30210186711, the binary leg (`calib_hi_to_lo__binary_vhl`), 12 λ states:

| statistic | at physical endpoint states (0, 11) | in the alchemical interior | per-state histogram |
|---|---|---|---|
| **PERSISTENCE** — every over-threshold (replica, frame) pair | 29 | 116 | `{0:12, 1:14, 2:8, 3:11, 4:13, 5:11, 6:11, 7:13, 8:11, 9:11, 10:13, 11:17}` |
| **INITIATION** — first over-threshold frame, one per replica | **1** | **7** | `{0:1, 4:1, 7:3, 9:2, 10:1}` |

The ternary leg is `0 / 0` on both, with empty histograms — consistent with its 12/12 STABLE classification, and the
control that says these numbers are measuring something real.

**Read together they give a mechanism that neither gives alone:**

- **Initiation is λ-dependent.** 7 of 8 departures begin in the interior, skewed to the upper-λ states
  (`{7:3, 9:2, 10:1}` = 6 of 8), where the softcore region is largest. Only 1 of 8 begins at a fully-interacting
  physical endpoint. **So the alchemical softening is what opens the door.**
- **Persistence is λ-INdependent.** Once a replica has departed, the displaced configuration survives everywhere
  on the ladder — the pooled histogram is nearly flat and per-state the endpoints are mildly *enriched*
  (14.5/state at 0 and 11 vs 11.6/state across the interior). **The physical Hamiltonian does not close the door
  again.**

**What that licenses, and what it does not:**

- ✅ **It is plausibly a PROTOCOL problem, not necessarily a wrong model.** I had explicitly left open that
  departures at physical λ would mean "the binary complex model itself is wrong"; the initiation statistic does
  **not** support that, and I am not claiming it. A restraint on the receptor-contacting moiety would be the
  obvious remedy for an alchemically-facilitated escape.
- ✅ **It confirms more sampling will not fix the existing trajectory.** Not because sampling is inadequate, but
  because the departure is effectively irreversible on this timescale — so the committed trajectory is
  *contaminated*, with unbound configurations entering MBAR at physical λ, rather than merely under-converged.
- ❌ **n = 8.** "Concentrated at states 7–10" is 6 of 8 departing replicas. Suggestive of an upper-λ mechanism,
  nowhere near a rate, and it must not be quoted as one. The `initiation_note` field carries this caveat with the
  number so it cannot be separated from it.
- ❌ **It does not establish that a restraint would be sufficient**, only that it addresses the observed
  initiation channel. Adding one **changes the Hamiltonian**, so it must key the commit prefix and the system
  fingerprint (§L.3f) — but in this RBFE it carries **no standard-state correction**, and importing ABFE's would
  be wrong rather than conservative. Ruling and physics: **§L.3f**.

**Net for the r0 cycle, unchanged from §L.3b:** ΔG_binary is not a free energy of the intended bound state, so
ΔΔG_coop(r0) = −0.534 is not a valid measurement of cooperativity, and the binary arm needs re-running rather than
extending. What §L.3c adds is *what to change on the re-run*, and that the ternary arm remains clean throughout.

### L.3d The 4 fs cycle reproduces the departure exactly — so the r0 finding is REINFORCED, not softened, and the 2b timestep PASS stands

This was set up as a test that could go against §L.3–L.3c. RUNG 2b's 4 fs cycle agrees with r0's 2 fs cycle to
|Δ(ΔΔG_coop)| = 0.0215 kcal/mol, and if 2b's binary leg had held its pose then a contaminated arm and a clean one
agreeing that closely would have meant the departure barely moves ΔG_binary. It did not hold.

GH run 30210676030 (Vast lane, `task=converge`, CPU, $0) against GH run 30210186711 (GCP lane, r0):

| | **2 fs (r0, GCP L4)** | **4 fs (RUNG 2b, Vast)** |
|---|---|---|
| binary `contact_pose` max / median (Å) | 16.327 / 4.333 | **17.622 / 5.358** |
| binary `n_contact` heavy | 30–52 | 30–47 |
| binary replicas ending beyond 4.0 Å | **8 of 12** | **7 of 12** |
| binary classes | DISPLACED_AND_STAYED 5, INTERMEDIATE 3, STABLE 4 | DISPLACED_AND_STAYED 7, INTERMEDIATE 3, STABLE 2 |
| binary λ **initiation** (endpoint / interior) | 1 / 7 | **1 / 9** |
| binary λ **persistence** (endpoint / interior) | 29 / 116, flat histogram | 23 / 121, flat histogram |
| **ternary** `contact_pose` max / median (Å) | 2.835 / 1.653 | **2.999 / 1.897** |
| **ternary** replicas beyond 4.0 Å | **0 of 12** | **0 of 12** |
| solvent | not applicable (no receptor) | not applicable |

**Every feature reproduces.** Same magnitude of departure, same fraction of replicas, same class mix, the same
λ signature (initiation overwhelmingly interior with exactly 1 endpoint case), the same flat persistence
histogram — and the same completely clean ternary arm. Across a **different timestep** (2 fs vs 4 fs), a
**different provider and GPU** (GCP L4 vs Vast 4090/4080S), a **different commit interval**, and **independent
runs**.

**What follows, kept separate because they are separate:**

1. **The r0 conclusion is strengthened.** The binary-arm departure is not a one-off of one trajectory — it is a
   systematic, reproducible property of this binary leg's setup. About as well-established as an in-silico
   observation gets here.
2. **The RUNG 2b timestep PASS stands, on its own terms.** The gate asks whether 4 fs reproduces 2 fs, and it
   does. A defect the two cycles share cancels from the comparison, which is exactly the condition §L.3b named and
   this measurement satisfies. **4 fs adoption is not undermined by any of this.**
3. **Neither absolute ΔΔG_coop is a valid cooperativity.** −0.534 (2 fs) and −0.5125 (4 fs) are two precise
   measurements of the same wrong thing. Precision was never the problem, and the agreement is not evidence of
   correctness — it is evidence of *reproducibility*, which is a different claim and the one the gate makes.
4. **The wrong-sign mechanism is now a much better-supported hypothesis — still a hypothesis.** The experimental
   target is **+0.94**; both cycles return ≈ −0.52 to −0.53; both have a reproducibly departed binary arm and a
   clean ternary arm. That co-occurrence is suggestive and it is still **correlational**. The test is a restrained
   binary re-run: if the sign flips positive with a held pose, the mechanism is established; if it does not, the
   wrong sign has another cause and the departure is a separate (real) defect.
5. **Both cycles need the binary arm re-run**, not just r0 — with a restraint on the receptor-contacting moiety
   (§L.3c), **and no standard-state correction: see §L.3f**, which also rules that **only the binary arm is
   re-run** and the clean ternary arm is not. Extending either trajectory is useless: they are contaminated,
   not under-converged.

**And note what made this checkable at all:** the diagnostic had to be pointed at a *different lane's* storage
(S3 via Vast, not GCS), which is why `--fetch-trajectories` and the Vast `converge` task exist. A finding that can
only be verified on the lane that produced it is a finding that cannot be cross-checked.

### L.3e A free pre-check on the replacement design — and a prediction worth pre-registering

The valB_mini rescope's specified replacement is the **synthetic closure triangle** (~$6, `valb_triangle_closure.py`),
3 edges × (ternary + binary) = **6 legs**. Its three binary legs are *the same construction that departs*: an
alchemical morph of the ligand inside VCB. The departure is established across two cycles, two timesteps and two
providers (§L.3d), so there is no reason to expect these three to behave differently.

**The design is already built for this, which is the good news.** `closure_decomposition` splits the residual:

    R_coop = R_ternary − R_binary,  each a closed cycle in its own environment, each separately zero for an exact
    method — and its `_rule` already says to report both, never R_coop alone, because a clean-looking R_coop can
    be two large closures cancelling.

So nothing about the design needs changing. What changes is that it now has a **specific prediction to state in
advance**, which is worth more than a generic path-error detector:

> **PRE-REGISTERED PREDICTION.** `R_binary` will be materially non-zero and `R_ternary` will be small, because
> all three binary legs carry the departure and all three ternary legs do not (0/12 replicas displaced in both
> cycles measured so far).

Both outcomes are informative, which is what makes it worth stating up front rather than after:

- **R_binary large, R_ternary small** → the departure's bias is **path-dependent**, a closure residual sees it, and
  the triangle has independently localised the defect to the binary environment. Confirms §L.3b–L.3d by a
  completely different route.
- **R_binary small too** → the bias is a per-endpoint **state function**, telescopes out of any cycle, and
  therefore also largely cancels from ΔΔG_coop. That would mean the departure, while real, corrupts the
  *cooperativity number* far less than §L.3b implies — and I would have to say so. It is the outcome that argues
  against my own reading, which is exactly why it belongs in the prediction.

**One thing to actually do, and it is free:** run the pose diagnostic on the triangle's legs when they land.
`mode=converge` (GCP) and `task=converge` (Vast) both now report the contact-moiety series and λ attribution per
leg, so this costs a dispatch. **Do not interpret `R_binary` without it** — a non-zero binary closure has at least
two causes (the departure, or ordinary path error) and the pose data is what separates them.

**And the open design question, stated but NOT decided here:** whether the triangle's binary legs should be run
**restrained** (§L.3c's remedy — see §L.3f for why no standard-state correction attaches to it) rather than
as-is. Restrained legs would make `R_binary` a clean path-error measurement; unrestrained legs make it a
measurement of the departure. Those are different experiments — it changes what the ~$6 buys.
**→ DECIDED 2026-07-26: UNRESTRAINED. The decision and its three reasons live in
[nr4a3-program-map.md](../manuscripts/nr4a3-program-map.md) (one home; not restated here).** Note it is a **different question** from
§L.3f's, which governs the r0 / 2b cycles' own binary and ternary **arms**, not the triangle's legs.

### L.3f THE RE-RUN'S TWO RULINGS: no standard-state correction, and the ternary arm is NOT re-run restrained

Both of these were left open above. Both are decided here, because a re-run cannot be dispatched without them and
"not deciding" is the one answer that costs a GPU-day to discover.

#### 1 · There is NO standard-state correction, and adding one would be WRONG — not conservative

**This is an RBFE, not an ABFE.** The ligand is never decoupled: both alchemical endpoints have a fully
interacting ligand in the pocket and only the perturbed atoms change. The restraint
(`ternary_restraint.add_flat_bottom_restraint`) is added to the `System` **once, before the integrator**, so every
λ state's `ThermodynamicState` is built from it and it is never scaled by λ. An identical, never-scaled term
contributes the same amount at both endpoints and **cancels exactly from ΔG(A→B)**.

The Boresch-style analytic release term in `nr4a3_abfe.boresch_standard_state_correction` exists because ABFE's
decoupled endpoint holds a *non-interacting* ligand confined to a restrained volume that must be released to 1 M.
**No such endpoint exists in this calculation.** Importing that term here would not be a safe over-correction —
it would add a spurious few kcal/mol to a quantity from which the restraint has already cancelled, and it would
do so on the *binary* arm only, i.e. directly into ΔΔG_coop. It is pinned by an **AST** test
(`test_ternary_restraint.test_the_module_never_imports_the_abfe_correction` — AST because the first cut grepped
the text and fired on the module's own docstring explaining why the term does not apply), and
`restraint_standard_state_dg` is deliberately never emitted so `abfe_xtag_guard` cannot be tripped into demanding
it.

The cancellation has one precondition and it is checked rather than assumed: the restrained atoms must exist at
both endpoints. The restraint is built only from the ligand's **contact moiety**, and `restraint_report` records
`unmapped_contact_atoms` — any restrained atom that is alchemically perturbed — so the assumption is auditable
per leg.

> **SUPERSEDED, retained for the record (rule 1.2).**
> **(a)** §L.3c, §L.3d#5 and §L.3e each said the restrained re-run needs "the standard restraint correction".
> **That statement is withdrawn and must not be quoted.** It imported ABFE reasoning into an RBFE lane. The
> physics is as stated in this section; the three sites now point here.
> **(b)** The first draft of ruling 2 below justified itself with "**0 of 12** replicas beyond the 4.0 Å
> threshold, in both cycles and **in both directions**". **Withdrawn — it was wrong for the reverse leg**, whose
> converge pass reads **1 of 12** departing to **4.737 Å**, i.e. *past* the flat-bottom half-width, so the claim
> that the restraint could never engage on the ternary arm was an overstatement. The ruling is unchanged and the
> reasoning is now stronger rather than weaker: see reason 3, where the λ signature of that single excursion —
> initiating at a **physical endpoint**, not in the alchemical interior — is what disqualifies it from being a
> restraint's business at all. Recorded because a ruling defended by a number that turns out to be wrong is a
> ruling that has to be re-derived, not quietly re-worded.

#### 2 · The ternary arm is **NOT** re-run restrained. Only the binary arm is. ⟵ THE RULING

The re-run is: **binary arm, restrained (`restrain=1`), both cycles.** The ternary arm keeps its existing
committed trajectories, unrestrained. Four reasons, in decreasing order of how much they would survive a
reviewer:

1. **"The same restraint on both arms" is not actually available.** The restraint is constructed *per leg from
   that leg's own starting frame*: its ligand group is whichever contact-moiety atoms sit within 4.5 Å of a
   receptor in **that** environment, its anchor group is those receptor atoms, and `r0` is **that** leg's centroid
   separation. In the ternary complex the PROTAC contacts *two* proteins, so `select_restraint_groups` would pool
   anchors across SMARCA2 **and** VCB and take in both warheads — a **different restraint on different atoms with
   a different r0**. Symmetry between the arms is therefore cosmetic, not formal. What makes the restraint safe is
   that it cancels **within each leg**, between that leg's own A and B endpoints, and that holds for the binary arm
   whether or not the ternary arm has one. **The restraint is not a term in ΔΔG_coop at all** — neither arm's is.
2. **On the FORWARD ternary legs — the ones that enter ΔΔG_coop — the restraint would be almost exactly zero, so
   it can only add unquantified risk.** The well is flat (force identically zero) out to `r0 + 0.30 nm`, and only
   *outward* motion is ever restrained. The fwd ternary arm's worst receptor-superposed contact-moiety pose RMSD,
   over all replicas and frames, is **2.835 Å (2 fs) and 2.999 Å (4 fs)** — §L.3d — against a **3.0 Å** half-width.
   A group centroid's displacement is bounded above by that group's RMSD, so the dominant term is below the well
   edge at the single worst frame measured, and typical frames (median 1.65 / 1.90 Å) are nowhere near it.
   *(Not "provably zero": the receptor anchor centroid also drifts slightly under superposition and that term is
   not measured. The claim is that engagement would be marginal at worst, which is what the numbers support.)*
   A restraint that is essentially never felt cannot improve a clean arm; it can only introduce an effect nobody
   has quantified.
3. **The one ternary excursion that DOES exceed the well is exactly the kind a restraint must not remove.** The
   REVERSE ternary leg's converge pass clears every health flag except `ligand_stable_ok`: **1 of 12** replicas
   departs, to a contact-pose max of **4.737 Å** — past the 4.0 Å threshold and therefore past the 3.0 Å flat
   half-width, so a restraint **would** have engaged there. That is not an argument for restraining it, and here
   is why: **the departure initiates at λ state 11 — a PHYSICAL endpoint.** The restraint exists to close an
   *alchemically facilitated* escape channel (§L.3c: 7 of 8 binary departures initiate in the alchemical
   interior, skewed to upper λ where the softcore region is largest). An excursion that begins at a
   fully-interacting physical endpoint is not that channel; it is the physical Hamiltonian's own sampling.
   Restraining it would **suppress physical sampling and call the result a fix**, which is a worse error than the
   one being repaired — and it would do it inside the leg whose only job is the preregistered fwd/rev hysteresis,
   changing what that number measures.
4. **The arm has no defect the remedy addresses — and the contrast IS the control.** Binary: **8 of 12** replicas
   out, max **16.6 Å**, initiation **7 of 8 in the alchemical interior**. Ternary: **0 of 12** out in both fwd
   cycles, **1 of 12** at 4.737 Å in rev, that one initiating at a **physical endpoint**. Same alchemy, same
   ligand, same E3 — the arms differ only in whether the second protein is present. So the departure is
   **specific to the binary arm's missing second protein**, which is both why the remedy belongs there and why it
   does not belong on the ternary arm. You re-run what is broken. CLAUDE.md §5 — *deepening a test past its field
   standard defaults to NO* — points the same way, and "more rigorous" is explicitly not a reason.
4. **It would cost the scarcest resource in the program and re-open a settled gate.** The ternary leg is the
   expensive one (146k atoms, 12 λ windows) and `GPUS_ALL_REGIONS = 1` forces every leg **sequential**, so
   re-running the ternary arm roughly doubles the re-run in GPU-days against a credit that expires
   **2026-10-10**. It would also change the ternary protocol underneath the RUNG 2b timestep PASS, whose whole
   content is that the 4 fs and 2 fs **ternary** legs agree (|Δ(ΔΔG_coop)| = 0.0215 kcal/mol, §L.3d#2).

**THE HONEST CAVEAT, stated because it is the reviewer's first question.** ΔG_binary(restrained) is the morph's
free energy in a bound-state-restricted ensemble; ΔG_ternary is the morph's free energy in an unrestricted one.
They are comparable **to the extent the ternary arm never visits the region its own restraint would have
excluded** — which is measured (reason 2), not assumed. This is not free of assumption and the paper must say so
in those words.

**THE FALSIFIABLE CONDITION THAT REOPENS THIS RULING, and it costs $0.** *If the restrained binary leg spends a
material fraction of its production frames OUTSIDE the flat region*, then the restraint is doing real work, the
restrained ensemble is genuinely narrower than a free bound state, reason 2's symmetry argument weakens, and the
ternary arm must be re-run restrained after all.

**How it is evaluated, concretely, so this is not an aspiration.** The leg writes `restraint.json` (groups,
`r0_nm`, `r_flat_nm`) and `gpu-ternary-fep-gcp.yml` uploads it to
`…/valB-6hax/results/restraint_<leg>_<dir>_r<seed>.json` — it had to be uploaded explicitly, because the driver
writes it into the VM's shared dir and the run log is only preserved on NORESULT, so on a *successful* leg the
report would have died with the instance. Against that, `mode=converge`'s existing contact-moiety pose series
gives the per-replica, per-frame displacement over the committed trajectory, at $0 on CPU.

**Read the comparison honestly: it is an UPPER BOUND, and only decisive in one direction.** The restraint acts on
the *centroid separation*; the pose series reports a *receptor-superposed RMSD*, which upper-bounds the centroid
displacement. So "fraction of frames with contact RMSD > `r_flat` − `r0`" **over**-estimates the fraction of
restrained frames. A **small** value therefore settles it — the restraint was essentially never engaged, and the
ruling stands. A **large** value does **not** settle it the other way and must not be reported as if it did; it
means the cheap proxy has run out and the restraint's own force group has to be read directly
(`ternary_restraint.restraint_energy_kj`, which exists precisely so that this is possible — a restraint you
cannot measure is a restraint you cannot defend).

#### 3 · SEQUENCING: the rest of the re-run is HELD until the closure triangle's residual `R` lands

**Ruled 2026-07-27, and the reason is scientific, not budgetary.** One restrained binary leg is running; the
remaining seeds and the 4 fs cycle's arm are **not** dispatched. The closure triangle is running on Vast and it
decides whether the valB edge's miss is **path error at all**: `R` is provably **zero for any endpoint-STATE
error** and non-zero only for **PATH error**. If `R` comes back materially non-zero, the premise the full binary
re-run rests on changes — and a multi-day commitment of the only GCP GPU would have been spent on a design that
wanted revisiting first.

This is the §"serialize only when one result could cancel the rest" litmus test answering **YES**: there is a
result the triangle could return that would make us not run the rest. The single leg already launched is the
right amount of exposure until it lands. **Waiting costs nothing** — the work is checkpointed, and the credit
does not expire until 2026-10-10.

**Where this is enforced.** `restrain` is a `workflow_dispatch` input on `gpu-ternary-fep-gcp.yml`, default `0`,
and it **keys the commit prefix** (`_rst`, placed before `_dir<dir>` so the direction stays terminal) and the
commit-manifest system fingerprint. Both directions are asserted before a GPU is provisioned. That keying is not
bookkeeping: restrained and unrestrained systems are **identical in composition** — same atoms, same particle
count, one extra `CustomCentroidBondForce` — so `assert_multistate_system_equality`, the check that caught the
fwd/rev collision in §H by luck, **provably cannot fire here**. See `tests/test_commit_prefix_restraint.sh`,
which extracts the workflow's real `DIRSUF`/`RSTSUF`/`COMMIT_PREFIX` lines and its refusal block and evaluates
them rather than restating the rule and agreeing with itself.

### L.5 The keying fix exposed the SAME flaw one level out — and then a sweep found no third instance

Caught 2026-07-27 8:00 AM, ~4 h before it would have fired unattended. §L.1 made `mode=converge`'s *analysis*
direction-aware and left its *output* keyed on nothing:

```
gcloud storage cp /tmp/conv/ternary_convergence.json "$RESULTS/ternary_convergence.json"
```

One filename, both directions. Because a rev pass now correctly covers **only** the rev ternary leg (binary and
solvent are the cycle's fwd-only shared arms and are skipped), uploading it under the bare name would have
**overwritten the fwd cycle's three-leg report** — the file `ternary_fep_reduce` reads for `diagnostics_ok`. The fwd
binary and ternary diagnostics would have vanished, `diagnostics_complete` would have gone False, and the gate
would have routed to BORDERLINE *on data it previously had*. It would also have destroyed the §L.3–L.3d pose
findings; regenerable, but only by someone noticing they were gone.

**Fixed:** fwd keeps the bare name (the reducer and every existing reader are untouched), rev writes
`ternary_convergence_rev.json`, and a notice states that the fwd report was not touched and that the rev report
covers the ternary arm only. Four checks in `tests/test_converge_direction.sh`, verified to fail on the bare-name
upload.

**THE TRANSFERABLE RULE, and it is the one that generalises past this repo:** *fixing a keying bug is not done
until you have asked what ELSE is keyed on the same nothing.* The direction-blind key was fixed in the commit
prefix (§H), then in the analysis (§L.1), then in the output name (here) — three layers, each exposed only by
fixing the one before it.

**So the sweep was done rather than assumed, and it comes back CLEAN.** Every artifact the GCP lane writes to
`$RESULTS/`:

| artifact | keyed by direction? | verdict |
|---|---|---|
| `ternary_convergence*.json` | now yes | fixed here |
| `ternary_coop_reduction.json` | no — **correctly** | there is ONE cycle: the reducer builds it from fwd legs and consumes rev only for hysteresis, and the watchdog dispatches `mode=reduce` with no direction, so `DIRECTION` is always `fwd`. A second name would imply a second cycle that does not exist |
| `ternary_convergence_summary.txt` | n/a | never uploaded — written to the runner's `CKPT` and `cat` into the log |
| `leg_<id>_<dir>_r<seed>.json` | yes | §A#5 |
| `postmortem/<leg>_<dir>_seed<n>_<epoch>.log` | yes | §C |
| commit prefix, setup cache, watchdog GCS markers | yes | §H, §J.2, §F |

**Known and deliberate gap, recorded so it is not mistaken for an oversight:** nothing reads
`ternary_convergence_rev.json`. The rev leg's own convergence diagnostics are therefore *informational* — they do
not gate the hysteresis result. Wiring them in would mean deciding what a rev-leg diagnostic failure should do to
a hysteresis number, which is a design question, not a bug fix.
→ **CLOSED the same day — see §L.6, which also found the FOURTH layer of the keying bug and two more instances of
the lane's signature defect. The sweep above was clean about artifact *names* and I read that as the question being
settled; it was clean about names and silent about *readers*, and the paragraph above is where I said so and moved
on anyway.**

### L.6 A FOURTH layer of the same keying bug, and two more instances of the signature defect

Found 2026-07-27 9:15 AM, tracing what would actually happen when the rev leg lands and the watchdog chains
`converge → reduce`. §L.5's sweep asked *"what else is keyed on the same nothing?"* and answered it for artifact
**names**. It never asked the adjacent question — *who **reads** these?* — and every finding below sits in that gap.

**1 · The fetch (fourth layer).** `mode=reduce` downloaded the report with a literal:

```
gcloud storage cp "$RESULTS/ternary_convergence.json" /tmp/legs/
```

Correct while `converge` wrote one file; wrong the moment §L.5 made it write two. The rev report would sit in the
bucket and never reach the reducer. Now a glob, so every direction's report travels. The sequence is now **commit
prefix (§H) → analysis (§L.1) → output name (§L.5) → fetch (here)**, four layers, each exposed only by fixing the
one before. The rule generalises further than §L.5 stated it: *anything keyed on a dimension must be keyed
**everywhere the artifact travels** — produced, named, stored, fetched, and read.*

**2 · The rev report was read by nobody — gap closed.** §L.5 parked this as "a design question, not a bug fix".
That framing was wrong in a specific way: it treated *what to do about a failing rev leg* as unresolved, when the
module had already answered it three times over. `_diagnostics_ok()` is a **tri-state** — measured-and-clean /
measured-failure / not-verified — precisely so "we did not check" never reports as "it is fine". The rev leg
existed for one purpose, the preregistered hysteresis |ΔG_fwd + ΔG_rev| ≤ 1.0, and a rev leg whose ligand left its
pocket produces a number that is **not a measurement of path error at all** — so a *small* hysteresis off a broken
rev leg reads as a *clean cycle*. That the ligand-departure failure in §L.3a–L.3d was found **by this very
convergence analysis** makes it concrete rather than hypothetical: the lane's one demonstrated structural failure
mode is exactly what an unread rev report hides.

`_diagnostics_ok()` now consults both directions: a measured failure in either → FAIL, unverified in either →
BORDERLINE. Conditional on a rev leg actually existing, because demanding a rev report from a forward-only cycle
would pin every one of them at NOT_VERIFIED — a different way of being wrong, and pinned as its own test.

**3 · `hysteresis_kcal or 0.0` — an unmeasured criterion arriving pre-satisfied, across a module boundary.**
The worst of the three, because it defeated a gate written specifically to catch it. `leg_output_record` built:

```python
"hysteresis_kcal": leg_agg["hysteresis_kcal"] or 0.0
conv = bool(... and (leg_agg["hysteresis_kcal"] is None or leg_agg["hysteresis_kcal"] <= 1.0))
```

`hysteresis_kcal` is `None` whenever a leg has no `DIRECTION=rev` partner — which, until rev was unlocked, was
**every leg in the lane**. So "no reverse leg ran" was written out as the literal value **0.0**: *perfect*
forward/reverse antisymmetry. And `ternary_coop_gate.gate_technical_convergence` — the reviewer's cycle-closure
check — declares `hysteresis_kcal` as `"float|null"` and **fails a leg whose value is null**
(`ternary_coop_gate.py:188`). Handing it `0.0` meant that branch could never fire. The criterion was inert for the
whole lane, and the gate's own author had anticipated the exact case.

Sharpest detail: `calibration_decision` in the **same file** already routes an unmeasured hysteresis to
INDETERMINATE, and carries a comment explaining why an unmeasured criterion does not satisfy a frozen rule. The
per-leg record contradicted it one function away. Null now propagates, `converged` has to be earned, and
`ternary_coop_io.validate_result` gained the cross-field invariant — *`converged=True` beside a null hysteresis is
a schema failure* — because the schema is what a future producer reads. The end-to-end test asserts the gate
**really does** fire on null and **really does** pass a measured 0.0, across the module boundary, rather than
arguing it.

**4 · A tri-state flattened on the way out.** `calibration_gate` reported `"diagnostics_ok": bool(diagnostics_ok)`,
mapping *measured failure* and *never computed* onto the same `false`. The decision logic distinguished them
correctly (FAIL vs BORDERLINE); only the record did not, so no machine reader of the verdict JSON could tell a
broken leg from an unexamined one — only the prose `reason` carried it. Now emitted faithfully, plus an explicit
`diagnostics_state` of `CLEAN` / `MEASURED_FAILURE` / `NOT_VERIFIED`.

**What ties 2, 3 and 4 together** is not the keying bug — it is bug class **§B#2's sibling**: *a default, coercion
or cast that turns "not measured" into a value indistinguishable from "measured and fine".* `or 0.0`, `bool(None)`,
the absent-report `return True` of 2026-07-25, `if hys else True`, and `_diagnostics_ok` ignoring a whole file are
five instances of one shape. **The generalisation worth carrying:** every place a measurement can be absent needs a
representation for absent that is not also a legal *good* value — and `0.0`, `False` and `True` are all legal good
values somewhere. Where the type cannot carry it, the invariant belongs in the validator.

**Verification.** 21 new tests across `tests/test_hysteresis_null_is_not_zero.py` (10) and
`tests/test_rev_convergence_report_is_read.py` (11), plus 7 checks added to `tests/test_converge_direction.sh`
(28 total). Every one pins **both** directions, because the cheap way to "fix" each of these is to loosen the gate
or to over-tighten it into uselessness. The workflow's bash filename rule is now **extracted from the YAML** and
asserted equal to `ternary_fep_reduce.convergence_report_name()` — a retyped copy would have proved only that the
copy agreed with Python and would have passed any edit to the workflow. Both new workflow checks were verified to
**fail** when the fix is reverted. Full suite: 1,945 pass, 14 pre-existing sandbox failures (`pymbar`/`scipy`/`rdkit`
absent), `lint_consistency` 0 errors.

**Timing.** All four landed before the rev leg's ~12:10 PM ET readout, so the first hysteresis this program has
ever measured gets computed by code that checks the leg it came from.

#### L.6a The sweep that §L.6's generalisation demanded — one more instance, in a different lane

§L.6 ended on a claim (*"absent needs a representation that is not also a legal good value"*), and §L.5's rule says
a claim like that is not finished until it has been **run as a search**. Three shapes were swept across
`research/` (non-test):

| shape | what it looks like | result |
|---|---|---|
| `<x> if <measured> else True` | an unmeasured criterion arriving pre-satisfied | **1 real hit** (below); the only survivor is `ternary_coop_gate.py:536`, which is the *correct* tri-state |
| `is None or <threshold>` | absent satisfies a threshold gate | **0** — the hysteresis one fixed in §L.6 was the only instance |
| `(<x> or 0)` compared to a threshold | absent coerced to a passing number | **0 real** — every hit is a counter or sort key; `nr4a3_8xtt_pocketminer.py:127` coerces to 0.0 but that direction yields *no positive finding*, which is the correct way round |

The `else True` hit was **`report_cofold.py`**, and it is the same defect with more consequence attached:

```python
coupled = inter_pae is not None and inter_pae < PAE_COUPLED
folds_together = ordered_iface and (coupled if inter_pae is not None else True)
```

`coupled` is **already** False when `inter_pae is None`, so the trailing conditional did exactly one thing: flip the
unmeasured case from fail to pass. With no usable PAE matrix the co-fold call rested on the contact patch alone —
and the verdict string then read *"halves fold together (ordered contact patch + **confident relative
placement**)"*, naming as observed the criterion that had never been measured. A co-fold call is what sends an
interface on to fpocket, so it is the expensive direction to be wrong in. It had **no test coverage at all**.

Now tri-state — `True` / `False` / `None` = *placement not assessable* — with the decision extracted into the pure
`cofold_call()` so it has one home and can be exercised without gemmi, and a `CO-FOLD NOT ASSESSED` verdict that
still reports the ordered patch as *necessary but not sufficient* rather than discarding it. 9 tests, both
directions pinned, plus a call-site check (the same gap that let a frame-B swap pass eight tests in §L.3).

**Method note worth keeping.** The regression check was first written as a text search for the offending
expression and it was wrong in both directions: it fired on the expression quoted inside the new docstring — a
false positive that cost a red run — and it would have missed any reformatting across lines. It is now an **AST**
walk for `IfExp` whose `orelse` is the literal `True`, which is what made the repo-wide sweep above possible at
all. *A lint precise enough to trust on one file is the thing you can then run everywhere.*

Suite after this: **2,111 pass**, 15 sandbox-only failures — the 14 pre-existing (`pymbar`/`scipy`/`rdkit` absent)
plus one that arrived from a concurrent session's 2026-07-26 push (`test_expected_heavy_map_size...`, an unguarded
`from rdkit import Chem`). All green in CI, which has the stack; left alone rather than edited, since it is another
session's live file.

### L.7 THE ONE THAT MATTERED: the first hysteresis this program ever measured was reported as NOT MEASURED

Found 2026-07-27 ~1:55 PM ET, minutes after dispatching the `mode=reduce` that §L.6 had been racing to make
correct in time. The reverse leg landed (production 2000/2000, GCP L4, flat 56.65 s/iter, no NaN), so for the
first time the preregistered criterion **|ΔG_fwd + ΔG_rev| ≤ 1.0 kcal/mol** had both of its inputs:

| | leg | ΔG_morph (kcal/mol) | MBAR SE |
|---|---|---|---|
| forward | `calib_hi_to_lo__ternary_vhl` `dir=fwd` `seed=0` | **+47.470131055401** | 0.11075836689255258 |
| reverse | `calib_hi_to_lo__ternary_vhl` `dir=rev` `seed=0` | **−47.79473620121289** | 0.08648735348921666 |

**|ΔG_fwd + ΔG_rev| = 0.32460514581189415 kcal/mol against the 1.0 ceiling → PASS.** The reducer computed it —
it is in `morph_summaries[0].legs` and in `leg_algebra_audit` as `antisymmetry_ok: true` — and the
`[REDUCE-VERDICT]` annotation, the artifact §D of this document exists to guarantee, said:

```
fwd/rev hysteresis: NOT MEASURED (no reverse leg reduced)
```

**Two independent defects produced that sentence, and either alone was sufficient.** Neither is a coercion, so
neither would have been caught by §L.6a's sweep — this is the same bug class arriving by two new routes.

**1 · A guard belonging to a DIFFERENT criterion suppressed this one.** `calibration_decision()` computed the
hysteresis only *after* the Welch–Satterthwaite CI succeeded. With one replicate per environment
`_welch_satterthwaite` returns None and the function returned early carrying `{decision, reason, n_ternary,
n_binary}` — nothing about the hysteresis at all. But the two criteria have **different data requirements**:
`|mean(ΔG_fwd) + mean(ΔG_rev)|` needs one replicate per **direction** and no replicate spread whatever, so it is
measurable in **precisely** the case where the CI is not. Not `or 0.0` and not `bool(None)` this time, but a
**control-flow path that never computes the value** — which renders as the same None, and None is a legal
"not measured".

**2 · The reader named a field the producer does not have.** The annotation read `dec.get('hysteresis_ok')`.
`calibration_decision` emitted no such key on **any** path; it emitted `checks.hysteresis_resolved`. `.get()` on
an absent key is None, and None was mapped to the string "NOT MEASURED". **The sentence was hardwired**, and no
amount of measuring could have changed it. The reciprocal is worse: `quiet = (verdict == 'PASS' and hy is True)`
could never be True, so a genuine PASS would have been annotated `::error` with *"GATE PASSED BUT THE
PREREGISTERED FWD/REV CRITERION DID NOT"* — naming as unmeasured a criterion that had been measured and passed.
That is **`report_cofold.py` (§L.6a) reflected**: there an unmeasured criterion was named as observed, here an
observed one is named as unmeasured. The common root is not the direction — it is a **verdict string decoupled
from the measurement it claims to report**.

**3 · And §L.6#4 again, one control-flow branch out.** `calibration_gate`'s `n < 2` return dropped
`diagnostics_ok` — a value `_diagnostics_ok()` had *already computed at the call site* and handed in. The three
states then produced **byte-identical key sets**:

```
PRE-FIX gate diagnostics_ok=True  -> keys ['decision', 'n_replicates', 'reason']
PRE-FIX gate diagnostics_ok=False -> keys ['decision', 'n_replicates', 'reason']
PRE-FIX gate diagnostics_ok=None  -> keys ['decision', 'n_replicates', 'reason']
```

so the annotation printed `diagnostics_ok=None` — NOT_VERIFIED — for a state that is a **MEASURED FAILURE**.
`diagnostics_state`, invented the same morning so a machine reader could tell those apart, was absent in exactly
the case the lane was in. **An absent key is not an acceptable third state, because `.get()` renders absence as
None and None is one of the three states.**

**Fixes.** `hysteresis_fields()` and `_diagnostics_fields()` are single homes emitted on **every** return path;
`per_replicate_ddg_coop_kcal` moves into the gate that owns it instead of being attached by the caller; the
`1.0` ceiling is **read from `nr4a3-ternary-coop-prereg.json`** (it was typed twice in this file, and
`ternary_coop_gate` already reads that same field — rule 1); the annotation reports the measured **value** and
the threshold, prints `diagnostics_state`, prints the single-replicate point estimate rather than only `None`,
and distinguishes **KEY ABSENT** from a measured null with a sentinel.

**One more turn of the same screw, found by the fix's own output.** The corrected annotation printed
`mean_ddG_coop=KEY ABSENT | target=KEY ABSENT | cycle_SD=KEY ABSENT`. Two of those are honest — with one
replicate there is no replicate mean and no cycle SD — but `target_kcal` is a **frozen constant handed straight
into the call and discarded**, the identical discard as `diagnostics_ok`. And sharing one rendering between
*"undefined on this path"* and *"the reader and the producer disagree about the field name"* hands back the very
ambiguity the sentinel was added to remove. So the gate now emits a **constant schema**: explicit `null` where a
quantity is undefined, and **KEY ABSENT reserved for one meaning only — a schema mismatch**.

**Verification, 21 checks over two new files.** The phantom-key sweep **EXTRACTS** every `<obj>.get('<key>')`
from the workflow YAML **by AST** and requires each key to be emitted by some branch of the real producer — a
retyped key list would prove only that the copy agrees with itself (§L.6), and a text grep false-positives on
its own docstring (§L.6a). The annotation script itself is extracted and **exec'd** against real reducer output.
Both halves were verified to fail when reverted.

**An honest limit, recorded because it is the interesting part.** A repo-wide sweep of every workflow heredoc
that `json.load`s a repo artifact, flagging any `.get()` key whose name appears nowhere in the repo's Python or
JSON, returns **zero candidates** — and it **would not have caught this one**: `hysteresis_ok` existed as a
*local variable one line above the dict literal that omitted it*, so the name was in the corpus. **A
name-occurrence sweep cannot see a phantom key whose name is real somewhere else**; only calling the producer
and comparing key sets can. That is what the test does, and it is why "run the claim as a search" (§L.5) needs
the search to be run against the *producer*, not against the *text*.

**End-to-end confirmation on the real data**, `mode=reduce` GH run **30293870930** (the constant-schema pass; run 30292846577 was the first post-fix pass and is the one whose `KEY ABSENT` output prompted the constant-schema change described above):

```
valB_mini reduce — decision=INDETERMINATE | mean_ddG_coop=None | per_replicate_ddG_coop=[-0.534] |
target=0.944 | abs_err=None | cycle_SD(replicate-SD, NOT MBAR-SE)=None | n_replicates=1 |
diagnostics=MEASURED_FAILURE | fwd/rev hysteresis: MEASURED |dG_fwd+dG_rev| = 0.325 <= 1.000 (PASS).
reason: need >=2 independent replicates for a cycle SD.
```

`diagnostics=MEASURED_FAILURE` is itself a result rather than a restatement: it is the first time the lane's
convergence state has been *reported* as measured-and-bad rather than as unexamined, and it is driven by
`ligand_stable_ok` in **both** directions' reports (§L.3a–L.3d for fwd, and the rev report below).

#### L.7a Before trusting the number: PROOF the reverse leg ran in reverse

The value above is worthless if the rev leg silently reported the forward answer under a reverse label — the
§H failure, where a direction-blind commit prefix let a rev attempt resume the *forward* trajectory. Under the
reducer's `|mean_fwd + mean_rev|` that failure mode does not announce itself: a sign-flipped copy of the forward
number gives **exactly 0.000**, i.e. perfect antisymmetry, the best-looking result the criterion can produce.
So the check was made **before** the number was read, from the artifact rather than from the label. Four
independent discriminators, all from `mode=converge` GH run 30287379531 and the leg records:

| discriminator | forward leg | reverse leg | reads as |
|---|---|---|---|
| `n_atoms_total` in the opened `.nc` | 141,968 (`v2pe`) | **141,968** | the **same system** as fwd, i.e. `v2pe` — **not** the 146,020-particle `v1` build that killed the four attempts of 2026-07-25 (§J.2, §J.5) |
| ΔG_morph | +47.470131055401 | **−47.79473620121289** | not a sign-flipped copy; a copy would give −47.470131055401 and a hysteresis of **exactly 0.000** |
| MBAR SE | 0.11075836689255258 | **0.08648735348921666** | different sampling, so a different trajectory |
| contact-pose max / median (Å) | 2.835 / 1.653 | **4.737 / 2.529** | different per-replica structural history — a re-reported forward trajectory would reproduce the forward statistics exactly |

The leg record also now carries `setup_cache_version: v2pe` and `charge_method: nagl` for the rev leg (the §J.5
fields), and all four legs share one `protocol_hash` `a5ad9520f912…` at `n_windows` 12. Cross-leg
`system_identity_consistency` still reports **UNKNOWN**, correctly: `n_particles` is recorded by *no* leg record,
and the three forward legs pre-date the §J.5 fields entirely — so the fwd/rev system match above rests on the
**convergence analysis reading the `.nc` directly** plus the two `v2pe` primes of §J.5, not on the leg records.
That gap is the §J.5 to-do that is still open on the GCP lane.

**The rev leg's own convergence report** (`ternary_convergence_rev.json`, now actually read by the reducer per
§L.6#2): every health flag passes — `overlap_ok`, `overlap_connected_ok`, `equilibrated_ok`, `mixing_ok`,
`forward_reverse_ok`, `plateau_full_vs_half_ok`, `quarter_block_ok` — **except `ligand_stable_ok`**:
contact-pose max **4.737 Å** against the 4.0 threshold, median **2.529**, **11 of 12 replicas STABLE**, one
`DISPLACED_AND_STAYED`, and the single departure **initiating at λ state 11 — a physical endpoint**, so it
cannot be attributed to alchemical softening.

**That is the control doing its job, and it is the load-bearing reading.** Against the **binary** arm's
**8 of 12** replicas departing at **16.6 Å** (§L.3a–L.3b), a ternary arm that is 12/12 clean forward and 11/12
clean in reverse — with the single reverse exceedance a marginal 4.737 against a 4.0 line — says the departure
is **specific to the binary arm's missing second protein**, not a protocol-wide defect. The ternary arm being
clean in *both* directions is what makes that a comparison rather than an assertion.
