---
id: DOC-SPRINT-S7-CHAIN
title: "S7-CHAIN — an artifact that records a commit sha, produced at a moment that is not the moment it is published"
level: L3
kind: process
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
---

# S7-CHAIN — the sha-recorded-at-the-wrong-moment cluster

**Item(s):** AUT-PD-028, AUT-PD-141, AUT-PD-168, AUT-PD-175, AUT-PD-195, AUT-PD-001, AUT-PD-189,
plus the driver's mid-task hand-off (the red trunk on `tests (modalities)`)
**Owned paths:** `scripts/regenerate_aso_chain.sh`, `research/manuscripts/aso_archive_manifest.py`,
`.github/workflows/` (AUT-PD-168's workflow only), and — widened by the driver mid-task —
`.github/workflows/tests.yml` and
`research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py`. New file written:
`research/manuscripts/tests/test_the_manifest_revision_survives_the_push.py`.
**Started (UTC):** 2026-09-01T18:38Z **Finished (UTC):** 2026-09-01T19:10Z

## Verdict

**PARTIAL — four of the seven rows no longer reproduce, the red trunk is fixed and proved fixed in a
real depth-1 clone, and the one genuinely live defect (a `git_revision` recorded before the push)
now has a check that fires at the moment the mistake is made.**

| row | verdict | one line |
|---|---|---|
| **driver's hand-off** | **FIXED** | one-of-a-pair defect: the fetching helper existed and one of the two identical call sites still used a bare `git cat-file`. Before/after run in fresh `git clone --depth 1` of `main`: `1 failed, 5 passed, 1 skipped` → `8 passed`. **`tests.yml` deliberately NOT changed** — see §"why depth-1 stays". |
| **AUT-PD-189** | **REFUTED** | both steps now succeed, and the chain does **not** exit 0 on failure — a full run in a clean copy exited **1**. Root cause (absent `libreoffice-writer`) was fixed in `dev-setup.sh` at `474921054`, the day the row was filed. |
| **AUT-PD-001** | **PARTIAL** | its three named steps all run now (same fix). Its *other* two asks are live and are now built: cause-separated verdicts, and `--only` scoping. Reproduced today that a full run rewrites **12** tracked files across three papers. |
| **AUT-PD-141** | **REFUTED as written** | its central claim — that `test_the_manifest_revision_is_a_commit_a_reader_can_resolve` passes on an orphan — is false; the reachability assertion it proposed landed `24e99ed75` (2026-08-22), six days before the row. The real gap is **timing**, not coverage. |
| **AUT-PD-175** | **CONFIRMED, and now checkable** | its ordering rule is correct and is now *measured* rather than remembered. |
| **AUT-PD-195** | **CONFIRMED, with one correction** | candidate (3) is wrong that a content digest is "the only option immune to the mechanism". A **pushed** sha is equally immune, and the content digest already exists. |
| **AUT-PD-168** | **PARTIAL** | its point fix landed in `emc-expression-datasets.yml`. Its actual ask — one shared publish step — needs `research/compute/publish_artifacts.sh`, **which I do not own**. The predicate that step needs is built and tested here; the four-line wiring is written out below for the driver. |
| **AUT-PD-028** | **NO CHANGE — it is downstream of AUT-PD-168** | the row's own analysis already says so. Nothing further is doable without the shared publish step above. |

---

## What I measured

### 1 · The red trunk (driver's hand-off) — reproduced and fixed, end to end

The driver's diagnosis was right about the mechanism and one level short of the fix. `_commit_is_present`
— a helper that fetches the exact sha when the object is absent — **already existed** in
`test_the_deposit_the_papers_cite_is_current.py`, with a docstring describing this exact depth-1
failure. It was wired into `test_the_published_record_is_corroborated_by_git_rather_than_declared`
and **not** into its twin, `test_the_recorded_upload_digest_is_corroborated_by_git_rather_than_declared`,
which kept a bare `git cat-file -e`. That twin is the one failing in runs 33532168479 (c48875a00),
33534733266 (7e9409a4b) and 33537002198 (bd8aac753).

⭐ **And the last GREEN run, 33523366953, is the proof that its green was a coincidence rather than a
reading**: that run's `head_sha` is `850edb335` — which *is* `pending.uploaded_at_git_revision`. A
bare presence probe in a depth-1 checkout can only pass while the recorded revision happens to BE the
checked-out tip, so the guard had been answering "is the recorded sha the same as HEAD?" for as long
as it had been passing.

Reproduced in a real `git clone --depth 1 https://github.com/trimcrae/Rare-cancers.git` (head `7af66a7`):

```
commits in clone: 1
pending.uploaded_at_git_revision = 850edb3358ba56ca127f3b5c79e23804b08c540c
-- before fetch --   fatal: Not a valid object name 850edb...^{commit}      cat-file: ABSENT
-- targeted fetch -- * branch  850edb3358ba... -> FETCH_HEAD               fetch rc=0
-- after fetch  --                                                          cat-file: PRESENT
git show: OK (381097 bytes)
digest at rev = f59a02acd74e9701d8357beb3be5d8bf61d30c4556b2547271a21ff50aff5aa9
recorded      = f59a02acd74e9701d8357beb3be5d8bf61d30c4556b2547271a21ff50aff5aa9
```

**The deposit record was correct the whole time.** The digest the manifest held at `850edb3358ba`
is exactly `pending.uploaded_manifest_digest`. Only the instrument was blind.

Before/after, two fresh depth-1 clones of the same head:

```
=== BEFORE (main's version) ===
E  AssertionError: deposit-state.json records the draft as built at 850edb3358ba, which is not a
   commit in this repository.  assert 128 == 0
1 failed, 5 passed, 1 skipped in 3.35s

=== AFTER (this seat's fix) ===
8 passed in 5.01s
```

⭐ **The skip is gone too, and that is a second guard recovered.**
`test_a_declared_drift_states_the_size_it_actually_has` reads the manifest at the *published*
revision with `git show` and skips when that fails — which in a depth-1 checkout is always. It now
calls `_commit_is_present` first, so it runs instead of announcing that it could not. Net: 7 tests
of which 1 never ran → 8 tests all running.

#### Why `tests.yml` stays at depth 1 — the constraint the driver named, honoured

The driver was right to flag it. `tests.yml`'s own comment (in the `pytest` job's suite step) records
that a genuine `git clone --depth 1` of that HEAD passes all 264, and that
`test_stuck_clock_a_retry_is_not_an_advance.py` and `test_stalls_are_named_reaches_the_board.py`
"already carry the shallow-horizon degrade-gracefully path" — a path **CI is the only place that
exercises**. `fetch-depth: 0` would retire that exercise permanently to fix one guard.

⭐ The targeted `git fetch --depth=1 origin <sha>` is strictly better on every axis: it costs one
commit object instead of 10,974, it leaves the shallow horizon intact for the tests that need it,
and it is the pattern this file already adopted. **`tests.yml` is unchanged.** The direction is the
one the driver demanded — the guard was made *able to run*, not easier to pass: the assertion it
makes is identical, and a revision that a targeted fetch of that exact sha cannot produce still
fails.

### 2 · AUT-PD-189 — REFUTED, on both of its two claims

Ran the chain in a **clean copy of the repository at `bd8aac753`** (a full `cp -a`, cleaned to HEAD,
never the live tree — eleven other seats are mutating it), 18:41:25Z → 18:46:22Z:

```
== submission parts · title page and figure legends     ok
== figure print formats · EPS and TIFF                  ok
== Word manuscript · submission format                  ok
== prior-art evidence                                   FAILED
ASO CHAIN: something is stale or failed -- see above.
EXIT=1
```

- **"two steps fail"** → both now succeed. `dpkg -l` shows `libreoffice-writer 4:24.2.7` present.
  The root cause was diagnosed and fixed the day the row was filed: `474921054` (2026-08-30,
  *"The .docx chain works in the sandbox: libreoffice-writer was absent, not broken"*) added the
  install to `dev-setup.sh`, and `fade4a548` (2026-08-31) added the `apt-get update` that a stale
  package index needs.
- **"the chain still exits 0"** → it exits **1**. The conditional `ok` and `fail=1` landed
  2026-08-19, per the script's own comment, eleven days before the row.

### 3 · AUT-PD-001 — three steps REFUTED, two asks live and now built

`build_submission_parts.py`, `svg_to_print_formats.py` and `build_submission_docx.py` all ran green
above (`gs` and `writer.xcd` both present). What survives is the part the row called the real cost:

**(a) the verdict cannot be told from a drift finding.** Reproduced today: the one failing step was
`prior-art evidence`, and its actual cause is that `origin/literature-cache` is not fetched —

```
REFUSED: origin/literature-cache does not carry ['literature/aso-priorart-fusiononco/_index.json',
 'literature/aso-priorart-junction/_index.json']. Fetch it first: git fetch origin literature-cache:...
```

— a **$0 fetch** which I then ran (`* [new branch] literature-cache -> origin/literature-cache`),
after which the step wrote its artifact and exited 0. The chain reported that as
`ASO CHAIN: something is stale or failed`, which is what a genuinely drifted artifact prints.

**(b) a full run rewrites other papers.** Measured on the clean copy after one chain run — twelve
tracked files, across **three** manuscripts:

```
 M research/manuscripts/aso/…-archive-manifest.json          (+7 more ASO deliverables)
 M research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-manuscript.pdf
 M research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.pdf
 M research/manuscripts/neoantigen/emc-vaccine-development-path-manuscript.pdf
 M research/manuscripts/neoantigen/emc-vaccine-development-path.pdf
```

### 4 · AUT-PD-141 / -175 / -195 — the one genuinely live defect, and where each row is wrong

**AUT-PD-141's central claim is false.** It says
`test_the_manifest_revision_is_a_commit_a_reader_can_resolve` "passes locally because the orphaned
sha still resolves through the local reflog". That test has asserted `git branch -a --contains`
since `24e99ed75` (2026-08-22), six days before the row was filed. Driven in a synthetic repo:

```
recorded git_revision = ee8808a3cc76c704227f9f867462d5902410c7d3   (then rebased)
cat-file -e            RESOLVES=yes          ← what the row saw
branch -a --contains   []                    ← what the guard actually asserts
merge-base --is-ancestor  ANCESTOR=no
```

The `--contains` check the row proposed building (`merge-base --is-ancestor`) is already there and
already fires. **What is live is the TIMING, not the coverage:** the local gate runs *before* the
rebase (regenerate → commit → preflight → rebase → push), so it is green at the moment it runs and
the orphaning happens afterwards. AUT-PD-195 records exactly this — the guards "catch it AFTER the
push, in CI, which costs a commit each time."

**AUT-PD-195's candidate (3) is wrong, and this is the decision I was asked to make.** Two clones
and a bare origin, real pushes and real rebases:

```
SCENARIO 1 · record a PUSHED tip (AUT-PD-175's ordering)
  REC on origin at recording time?  origin/main
  after a racing push forced a rebase and re-push:
     branch -r --contains REC : [origin/main]      ANCESTOR_OF_ORIGIN=yes

SCENARIO 2 · record a LOCAL-ONLY HEAD (the ordering AUT-PD-195 measured)
  REC on origin at recording time?  []
  after a racing push forced a rebase and re-push:
     cat-file -e REC2      : RESOLVES_LOCALLY
     branch -a --contains  : []                    ANCESTOR_OF_ORIGIN=no
```

## The design decision, and why the other option is worse

**Decision: keep the commit sha, and make the moment it is taken checkable. Do not switch to a
content digest.**

AUT-PD-195 offers recording a tree hash as "the only option immune to the mechanism rather than
defending against it". That is wrong twice, and the second reason is decisive.

1. **A pushed sha is equally immune, not a defence.** `origin/main` is append-only in this
   repository, so a commit that is on origin when it is recorded is an ancestor of every later
   origin tip, permanently. Scenario 1 above survived **two** racing rebases with nothing to
   remember and nothing to re-run. The rebase does not lose to the check; it cannot reach the
   commit.
2. **The content digest already exists and answers a different question.**
   `archive_content_digest` is a field of this manifest and is what `deposit-state.json`
   corroborates against. Replacing `git_revision` with a digest would duplicate it — CLAUDE.md
   rule 1, one fact one place — while destroying the only thing the sha does: name a point in
   history a reader can check out. The deposit's own step 1 is *"Check out the revision named in
   `git_revision`"*, five deposited PDFs print it as their provenance line, and a tree hash is not
   checkoutable.

⛔ **And it is a check, not a convention.** AUT-PD-141 is explicit that "regenerate after every
rebase" fails as a remembered pairing (AUT-PD-130). The bit that separates the two scenarios is
available **at recording time** — `git branch -r --contains HEAD` was `origin/main` in one and empty
in the other, before any rebase — so it is computed there.

---

## What I changed

### `research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py` *(driver-widened)*
- `test_the_recorded_upload_digest_is_corroborated_by_git_rather_than_declared` now calls
  `_commit_is_present(rev)` instead of a bare `git cat-file -e`. **Assertion strength unchanged**: a
  revision a targeted fetch of that exact sha cannot produce still fails.
- `test_a_declared_drift_states_the_size_it_actually_has` calls `_commit_is_present(rev)` before its
  `git show`, so it runs in CI instead of skipping. The skip stays as the honest floor.
- **New** `test_every_git_corroboration_in_this_file_goes_through_the_fetching_helper` — a
  source-level guard that no raw presence probe exists outside the helper. Written at source level
  deliberately: a behavioural version would have to manufacture a shallow clone, which is the one
  condition this sandbox cannot make and CI is the only place that has.

### `research/manuscripts/aso_archive_manifest.py`
- **`_revision_durability(rev)`** → one of `PUBLISHED` / `LOCAL_ONLY` / `ORPHANED` / `UNCHECKED`,
  from remote-tracking reachability. ⚠ It does **not** blanket-degrade on
  `--is-shallow-repository`: this sandbox reports `true` while holding 10,974 commits back to
  2026-08-04, so that flag would make the check answer `UNCHECKED` in the one place it most needs to
  run. The honest boundary is the **object** — if the commit resolves, `--contains` walked a graph
  that holds it.
- **`--check-revision-published`** — reads the manifest on disk, never builds. Exit 1 on
  `LOCAL_ONLY` / `ORPHANED`, **0 on `UNCHECKED` with the weakening announced** (a check that cannot
  look must not be red, or it gets switched off in every fresh clone).
- **A warning on the write path**, at the moment the sha is stamped. ⛔ It warns and does not refuse:
  refusing would break the legitimate case of regenerating on a branch about to be pushed for the
  first time, and a generator that starts exiting non-zero on a normal flow gets its exit code
  ignored. **The warning is not the fix** — the enforcement is the same command on the push path,
  and that wiring is the driver's (below).
- **`--is-inventoried PATH…`** — the predicate AUT-PD-168's shared publish step needs. Exit 0 and
  print the hits if any named path is in the archive, 1 if none, **2 if the inventory cannot be
  read** (fail loud: "I could not look" must not answer "no"). Verified against the row's own
  incident and its own correction:

  ```
  --is-inventoried research/modalities/emc-expression-panels.json   → prints it, EXIT=0
  --is-inventoried research/autonomy/claim.py research-ledger.json  → EXIT=1
  --is-inventoried (no args)                                        → EXIT=2
  ```

- ⛔ **No schema change.** The manifest's output bytes are untouched, because
  `research/manuscripts/aso/` is not mine and regenerating it would edit a file I may not edit.

### `scripts/regenerate_aso_chain.sh`
- **A fourth, optional `run_step` field: a prerequisite probe.** Consulted **only after a step has
  already failed** — the tool's own failure is the better witness than a probe that runs first, and
  a probe that ran first would be a second home for the truth about whether a tool works. It
  classifies a failure; it never skips work. Attached to `prior-art evidence`
  (`origin/literature-cache`) and the two `.docx` steps (`writer.xcd`).
- **The verdict names the cause, and the exit code carries it.** `1` = stale or failed; **`3` = every
  failure was a missing prerequisite**, with the remedy printed. ⛔ Both are non-zero — AUT-PD-189's
  complaint is that a step which wrote nothing must not be survivable, so naming the cause must not
  soften it.
- **`--check` gained an `UNCHECKABLE HERE` outcome** distinct from `STALE`, for the same reason.
- **`--only <substring>` and `--list`.** `--only` runs the matching steps and **always** the archive
  manifest afterwards, because the manifest hashes whatever they wrote. A scoped run never prints
  `ASO CHAIN OK`; it prints how many steps it did not look at and says the result must not be quoted
  as OK.
- **A reported (not gated) `manifest revision durability` step** calling
  `--check-revision-published`.

Measured, in the scratch copy, four scenarios — the classification is only worth anything if it
also refuses to soften a real failure, so that is scenario C:

```
A · --only "prior-art", with origin/literature-cache deleted
      ENV-BLOCKED: prior-art evidence — this machine cannot run it
        fix: git fetch origin literature-cache:refs/remotes/origin/literature-cache  ($0, seconds)
      ASO CHAIN: 1 step(s) could not run on this machine …
      "no staleness found, but the run was INCOMPLETE"        EXITCODE=3

B · same, ref restored
      == prior-art evidence   ok                              EXITCODE=0  (SCOPED, 25 not looked at)

C · a step with NO probe that genuinely fails (producer removed)
      FAILED: python3 research/manuscripts/aso_sequence_manifest.py
      FAILED: python3 research/manuscripts/aso_archive_manifest.py   ← correct cascade: it is inventoried
      ASO CHAIN: something is stale or failed -- see above.   EXITCODE=1

D · BOTH causes at once (producer removed AND the ref deleted), near-full chain
      FAILED: python3 research/manuscripts/submission_tables.py
      FAILED: python3 research/manuscripts/aso_sequence_manifest.py
      ENV-BLOCKED: prior-art evidence — this machine cannot run it
      ASO CHAIN: 1 step(s) could not run on this machine: · prior-art evidence — git fetch …
      ASO CHAIN: something is stale or failed -- see above.   EXITCODE=1

  · every run also printed:  == manifest revision durability
                             git_revision bd8aac753fea is on a remote-tracking ref
```

⭐ **C and D are the important ones.** The classification adds a reason; it removes no failure. A
step with no prerequisite probe that fails is still `FAILED`, still `fail=1`, still exit 1 — and the
archive manifest correctly went red behind it, because the file the removed producer writes is
inventoried. In D, both causes are present: the environment cause is still **named**, and the hard
failure still **wins the exit code**.

⚠ D also re-ran the three steps AUT-PD-189 and AUT-PD-001 call broken —
`submission parts · title page and figure legends`, `figure print formats · EPS and TIFF`,
`Word manuscript · submission format` — and all three printed `ok`, a second independent reading
beside §2's.

### `research/manuscripts/tests/test_the_manifest_revision_survives_the_push.py` — NEW, 8 tests
Drives real git (a bare origin plus two clones performing the actual race) rather than a fake,
because an orphaned sha is a property of an object graph and a fake would only assert what its
author already believed. Includes
`test_a_sha_recorded_at_a_pushed_tip_survives_two_racing_rebases`, which is the evidence for the
design decision above.

### Mutation testing — 5 mutations, 5 caught, in a scratch copy of the repository, never the live tree

| # | mutation | caught by |
|---|---|---|
| M1 | revert the fixed call site to a bare `cat-file` probe | `test_every_git_corroboration_…` |
| M2 | swap the probe inside `_commit_is_present` for `rev-parse` | `test_every_git_corroboration_…` (second assertion) |
| M3 | `_revision_durability` treats resolvable as `PUBLISHED` (the naive witness) | 3 tests |
| M4 | `UNCHECKED` reports as fine (`report is None`) | `test_a_clone_with_no_remote_says_unchecked_rather_than_published` |
| M5 | `--check-revision-published` always returns 0 | `test_the_check_mode_exits_nonzero_only_on_a_revision_that_will_not_survive` |

Control green before and after every mutation. ⚠ One defect was found **by** this and fixed rather
than kept: the first version of the source-level pair guard quoted the probe it forbids, matched
itself, and failed on a correct tree — the same self-reference trap `_tree_clean_apart_from_this_manifest`
records. It now excludes its own body as well as the helper's.

### Local gate results

```
pytest research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py   →  8 passed
pytest research/manuscripts/tests/test_the_manifest_revision_survives_the_push.py  →  8 passed
bash -n scripts/regenerate_aso_chain.sh                                            →  SYNTAX OK
```

---

## What I could not do, and what it is actually waiting on

### AUT-PD-168's real fix needs a path I do not own — here is the whole of it

⛔ **`research/compute/publish_artifacts.sh` is not in my OWNED PATHS.** It is the single shared
choke point and it is the right home: measured today, `.github/workflows/` holds **170** `.yml`
files, **75** of which can commit or push, **47** of which route through `publish_artifacts.sh`, and
exactly **3** of which mention `aso_archive_manifest.py` at all (`aso-submission-parts.yml`,
`emc-expression-datasets.yml`, `tests.yml` — and `tests.yml` only checks it).

⚠ AUT-PD-168 records this audit as "of 34 workflows, 33 can write an inventoried file". My count of
the workflow directory is 170 files; I do not know what population the 34 was over, so I am
reporting my measurement and its command rather than reconciling to theirs.

⛔ **It cannot be a plain `PUBLISH_REGEN`, and that is the whole content of the fix.** `PUBLISH_REGEN`
runs after the reset and **before** the commit, so a manifest built there records
`git_tree_is_clean_apart_from_this_manifest: false` — hashes describing content in no commit — which
`--check-archive` refuses outright. It has to be a **second pass after the push**, which is what
`emc-expression-datasets.yml` does by hand. Pasteable, for the driver or a seat that owns that file:

```sh
# AUT-PD-168: this publish may have written a file the ASO deposit inventories. Regenerate the
# manifest in a SECOND pass — after the commit, so the tree is clean apart from the manifest —
# rather than through PUBLISH_REGEN, which runs pre-commit and would record `clean: false`.
if [ "${PUBLISH_ARCHIVE_REGEN:-1}" = "1" ] && [ -f research/manuscripts/aso_archive_manifest.py ]; then
  if python3 research/manuscripts/aso_archive_manifest.py --is-inventoried "${PATHS[@]}" >/dev/null 2>&1; then
    PUBLISH_ARCHIVE_REGEN=0 PUBLISH_FAIL_HARD=1 \
    PUBLISH_REGEN="python3 research/manuscripts/aso_archive_manifest.py" \
    PUBLISH_REGEN_ADD="research/manuscripts/aso/fusion-junction-aso-archive-manifest.json" \
      bash "$0" "$BRANCH" "regenerate the ASO archive manifest after an inventoried publish (CI)"
  fi
fi
```

`PUBLISH_ARCHIVE_REGEN=0` on the inner call is the recursion guard. Landing this is what lets
`emc-expression-datasets.yml`'s hand-rolled copy be deleted, and it is what closes AUT-PD-028 —
whose own analysis already concluded the answer is "make the regeneration a step the trunk owns
rather than each session".

### The provenance check is not yet ENFORCED, only reported

`--check-revision-published` exists, is tested and fires. Nothing calls it on the push path.
⛔ **`.githooks/pre-push` is not in my OWNED PATHS.** One line, after the two existing checks:

```sh
python3 research/manuscripts/aso_archive_manifest.py --check-revision-published </dev/null || exit 1
```

⚠ Until that lands, CLAUDE.md's *"recorded is not enforced"* applies to this seat's own work: the
generator warns, the chain reports, and a session that ignores both can still push an orphaned
revision.

### The archive manifest reads STALE on the live tree right now

`--check-archive` exits 1 on the working tree as I write this. That is eleven concurrent seats
mutating the tree, not a finding; the manifest output lives under `research/manuscripts/aso/`, which
I may not edit. **The driver must regenerate it on the settled tree before committing the wave** —
and, per AUT-PD-175, *after* the final fetch/rebase, not before.

### Not attempted, and why

- **`git merge-base --is-ancestor` against `origin/main` specifically** rather than any
  remote-tracking ref. `--contains refs/remotes` is the weaker, correct question here: work legitimately
  lands on a feature branch that is pushed but not yet merged, and that revision is durable.
- **A behavioural test of the depth-1 path.** It needs a real shallow clone over the network inside
  a test; the source-level pair guard is the part that runs everywhere.

---

## Ledger rows the driver should write

I may not edit the ledger. Proposed:

| id | `what` (abbreviated) | `kind` | `state` |
|---|---|---|---|
| AUT-PD-189 | **CLOSE — REFUTED.** Both steps run; the chain exits 1, not 0. Root cause fixed at `474921054` (2026-08-30) + `fade4a548`. Evidence: full chain run in a clean copy of `bd8aac753`, 2026-09-01T18:41–18:46Z. | `process_defect` | `closed_refuted` |
| AUT-PD-141 | **CLOSE — REFUTED as written.** The reachability check it proposed landed `24e99ed75` (2026-08-22), six days before filing, and it fires on the orphan (`branch -a --contains` → `[]` while `cat-file` resolves). The live half is timing, which is AUT-PD-195's. | `process_defect` | `closed_refuted` |
| AUT-PD-175 | **CLOSE — the ordering rule is now measured, not remembered.** `aso_archive_manifest.py --check-revision-published` decides it; 8 tests in `test_the_manifest_revision_survives_the_push.py`. | `process_defect` | `done` |
| AUT-PD-195 | **PARTIAL → keep open for ENFORCEMENT only.** The decision is made and justified (keep the sha, check the moment; a pushed sha is immune, and the content digest already exists as `archive_content_digest`). Remaining: one line in `.githooks/pre-push`. ⚠ Its candidate (3) is corrected, not adopted. | `process_defect` | `queued` |
| AUT-PD-001 | **PARTIAL → the three steps are refuted; the two real asks are built.** Cause-separated verdicts (exit 3) and `--only` scoping landed. Reproduced: a full run rewrites 12 tracked files across three papers. | `process_defect` | `queued` (was: three steps blocked) |
| AUT-PD-168 | **BLOCKED ON ONE PATH, and the block is real.** The predicate (`--is-inventoried`) is built and tested; the shared publish step needs `research/compute/publish_artifacts.sh`, pasteable in S7-CHAIN.md. ⚠ Its "34 workflows" figure does not match my count of 170 files / 47 `publish_artifacts.sh` callers. | `process_defect` | `queued`, `blocked_by: publish_artifacts.sh ownership` |
| AUT-PD-028 | **NO CHANGE — downstream of AUT-PD-168**, as the row itself concludes. | `process_defect` | `queued` |
| **NEW** | ⛔ **A GUARD THAT CANNOT SEE THE HISTORY IT CHECKS READS AS GREEN BY COINCIDENCE.** `test_the_recorded_upload_digest_…` was red on `main` for three commits (33532168479 / 33534733266 / 33537002198) because it asked a depth-1 `actions/checkout` whether a recorded sha exists; its last green run's `head_sha` **was** that sha. Fixed by routing it through the fetching helper its twin already used, and pinned by a source-level pair guard. ⭐ THE REUSABLE PART: when a fix lands for a defect that has two identical call sites, the second site is the defect. | `process_defect` | `done` |

## Amendment record for the driver

⛔ I did not append to `research/autonomy/amendments.jsonl`. Two records, ready to paste:

```json
{"cycle_id": "SPRINT-2026-09-01-S7-CHAIN", "utc": "2026-09-01T19:12:00Z", "path": "research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py", "what_changed": "One call site routed through the existing `_commit_is_present` helper instead of a bare `git cat-file -e`; `test_a_declared_drift_states_the_size_it_actually_has` fetches before its `git show` so it runs in CI instead of skipping; one test ADDED, `test_every_git_corroboration_in_this_file_goes_through_the_fetching_helper`, a source-level guard that no raw presence probe exists outside the helper. 7 tests (1 never running) -> 8.", "old_value": "`tests (modalities)` red on main for three commits (runs 33532168479, 33534733266, 33537002198) on `test_the_recorded_upload_digest_is_corroborated_by_git_rather_than_declared`; in a fresh `git clone --depth 1` of main: 1 failed, 5 passed, 1 skipped.", "new_value": "Same fresh depth-1 clone: 8 passed. 2/2 mutations caught.", "why": "Driver hand-off, 2026-09-01. One-of-a-pair defect: the depth-1 fix landed for one of two identical corroboration sites. The deposit record was correct throughout - the digest the manifest holds at 850edb3358ba IS `pending.uploaded_manifest_digest`; only the instrument was blind.", "self_serving_check": "ANSWERED: NO, and the direction is checkable. The assertion is unchanged in strength - a revision that a targeted fetch of that exact sha cannot produce still fails - and the change makes TWO guards run that previously could not (one failing wrongly, one skipping). `tests.yml` was deliberately NOT changed to `fetch-depth: 0`, which would have been the easier fix and would have retired the shallow-horizon path that file's own comment says CI is the only place to exercise."}
{"cycle_id": "SPRINT-2026-09-01-S7-CHAIN", "utc": "2026-09-01T19:14:00Z", "path": "research/manuscripts/tests/test_the_manifest_revision_survives_the_push.py", "what_changed": "New test file, 8 tests, for `aso_archive_manifest.py`'s new `_revision_durability` / `--check-revision-published`: a pushed tip reads PUBLISHED and warns not at all; an unpushed commit reads LOCAL_ONLY; a rebased-away commit is caught although `cat-file` still resolves it; a sha no clone holds reads ORPHANED; a remote-less clone says UNCHECKED rather than PUBLISHED; the check mode's exit codes (1 on LOCAL_ONLY, 0 on UNCHECKED); the check mode never rebuilds the manifest; and a sha recorded at a pushed tip survives TWO racing rebases.", "old_value": "No test existed. AUT-PD-141/-175/-195 record the defect three times; the only instrument was a CI guard that fires one commit after the push.", "new_value": "8 tests, all passing; 3/3 mutations caught on the module (plus 2/2 on the deposit-guard file).", "why": "AUT-PD-141, AUT-PD-175, AUT-PD-195. The tests drive real git - a bare origin and two clones performing the actual push race - because an orphaned sha is a property of an object graph and a fake would only assert what its author already believed.", "self_serving_check": "ANSWERED: NO. Every test constrains the module further; none relaxes a bar. ⚠ One deliberate non-red: UNCHECKED exits 0, asserted explicitly. That is a weakening of the exit code and it is argued rather than assumed - a fresh clone, a CI checkout and a remote-less worktree all land there, and making them red would get the check switched off in exactly the places it can never answer, which is the cry-wolf history `_archive_only` in the same module already records. The reading is ANNOUNCED, never rendered as PUBLISHED, and `test_a_clone_with_no_remote_says_unchecked_rather_than_published` fails if it ever is."}
```
