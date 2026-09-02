---
id: DOC-SPRINT-S34-STRANDED
title: "S34-STRANDED — the thirteen unread branches read: three carry live work, eight are already on the trunk by another route, and one committed receipt is false"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: >
  Read every one of the thirteen 2026-08-28/29 stranded branches S31-ORPHANS named but could not open;
  decide each by DIFF against the live tree rather than by ancestry; produce tested patches for what is
  still live; and say plainly what is lost if each is deleted.
scope: >
  Thirteen branches on `origin`, plus tonight's `claude/s24-threshold-calibration`. It merges nothing,
  writes no ledger row, and settles no scientific question of its own — every scientific reading below is
  quoted from the branch that made it or re-measured against the live tree, and labelled which.
last_verified: 2026-09-01
---

# S34-STRANDED — thirteen branches read, five patches, and eight collided ids

**Item(s):** the "thirteen more branches from the same two days are UNREAD" row S31-ORPHANS proposed
**Owned paths:** `research/autonomy/sprint-2026-09-01/S34-STRANDED.md` (this file only), plus patches in scratchpad
**Refs read:** `HEAD` = `f9aa5df3675ebfd638ad7755eeda823abf30ff3f`, `origin/main` = `1d01f0790040d6b7107e58a98f5b8c81640247b2`
**Started/Finished (UTC):** 2026-09-01T20:07Z / 2026-09-01T20:35Z

## Verdict

**PARTIAL.** All thirteen are genuinely unmerged by commit and **eight of them are SUPERSEDED by
content** — the change is on the trunk through a different route, which is the clean result the
prompt anticipated and it is the majority outcome. **Three carry work that reproduces at HEAD and is
on no other ref**, and five patches for it are written and `git apply --check` clean. **Two are
OBSOLETE**: the defect each fixed was closed by a different, better route in the last four days.

⭐ **The largest single finding is not a branch, it is an id.** Checking every branch's ledger rows
against the current ledger — S31's `seat/s3` lesson, applied to all thirteen — found **eight
collisions across five branches**, and **`AUT-PD-154` and `AUT-PD-158` each name THREE different
defects on three different refs.** Two of those collided rows carry findings that are live at HEAD and
filed nowhere on the trunk; **one of them I reproduced tonight in one command.**

---

## ⭐ THE HEADLINE, FIRST

1. **`claude/aut-pd-147-s3-CYC-0074` is the branch worth having.** It carries a mutation-tested
   identifier-provenance guard for the fusion-partner synthesis. The repo-wide sibling guard exists and
   its `DOCUMENTS` map is **ASO-only, twelve documents**; the synthesis is in none of them, so `NR4A3`
   → `NR4A7` on that paper passes every gate that reads it — the branch's own measured claim, and the
   coverage gap reproduces at HEAD. I re-ran the guard's assertions against the live tree without
   pytest: **all of them hold today** (§2.6).
2. **`claude/aut071-s1-CYC-0074` did the trabectedin literature work FOUR DAYS BEFORE tonight's S19
   did it again.** Both read PMC9780071 Table 2; both got 3 EMC patients, 0 objective responses, 2
   stable, 1 progressive. Tonight's route prose is the better version and supersedes the branch's — but
   **the registry row and the `EV-PALMERINI-2022` evidence node are on no other ref**, S19 says in its
   own scope line that it "does not touch the clinical registry", and `RT-TRABECTEDIN.evidence` is
   still `[]` while its rationale names two PMIDs. That is the duplicated-work cost of the orphaning,
   stated as a measurement.
3. **A committed receipt on the trunk says a handoff was not attempted, and it was.**
   `receipts/CYC-0073-d4ccfde4.json` carries `handoff.attempted: false`, `child_session_id: null` and
   `blocked_by: []`. The branch records the successor session id, its creation time, and eight push
   rejections over ~61 minutes. CLAUDE.md §4: *a plausible-looking record is more dangerous than an
   empty one*. Narrow patch, 22 lines, `apply --check` clean.

---

## What I measured

### 1 · The method, and why it is not ancestry

`git merge-base --is-ancestor <branch> origin/main` returns **false for all thirteen** — and that is
the question the row asks, not the question worth answering. For every changed file on every branch I
ran the pair of read-only checks that discriminate:

```
git apply --check -R <per-file patch>   → clean  ⇒ the branch's POST state is already in the tree (SUPERSEDED)
git apply --check    <per-file patch>   → clean  ⇒ the branch's change is absent and lands cleanly (LIVE)
```

and, because "conflicts" is ambiguous between *drifted context* and *genuinely absent*, a third
measurement: **how many of the branch's added lines are absent from the live file, verbatim.** Zero
missing over 1,000+ added lines is supersession; 128 of 128 missing is live work. Every verdict below
cites that count.

### 2 · Per branch

#### 2.1 `cyc0073-d4ccfde4-work` — `9780481ad`, 5 unique commits — **SUPERSEDED, one real residue**

The branch a receipt on the trunk calls *"the successor's first job"*. Its code all landed by other
routes: `contract_check.py` **0 of 241** added lines missing, `push_guard.py` **0 of 220**,
`.githooks/pre-push` 0/17, `systems_check.py` 0/28 (the `.claude` CODE_DIRS fix), `dev-setup.sh` 0/35,
`preflight.sh` 0/41, and four whole test modules 0/238, 0/219, 0/88, 0/23.

Its three ledger rows resolve too: `AUT-PD-159` is the same defect on the trunk and is **done**;
`AUT-PD-160` is the same defect and **done**; `AUT-PD-161`'s defect ("the commit loop is slower than
the trunk's push interval") is on the trunk as **`AUT-PD-162`** — the id collided, the content did not.

⛔ **The residue is a false record, not code.** See §3.

#### 2.2 `claude/aut-pd-130-s4-CYC-0074` — `c20bc5288` — **PARTIAL**

`claim_coverage.py`'s check mode is **0 of 103** missing, and all three wiring edits are live at HEAD
(`preflight.sh:793`, `tests.yml:237`, `regenerate_aso_chain.sh:311`) — the "missing" lines in those
files are comment blocks around wiring that is already there.

**Two things are not on the trunk, and they pull in opposite directions.**

- ⭐ `test_a_missing_artifact_is_refused` — 17 lines. The branch found it **by mutation**: flipping
  `main()`'s `return 1` on an absent artifact to `return 0` was **the only survivor of thirteen
  single-site mutations**. Main's code returns 1 today, so this is a ratchet on correct behaviour with
  no behaviour change. Patch **P4**, clean.
- ⛔ The branch replaces `_selective_excerpt`'s `pytest.skip` with `pytest.fail`. **Tonight's commit
  `f9aa5df3` deliberately went the other way** — it kept the skip and wrote the decision at the site,
  which is what `test_every_remaining_skip_in_the_deposit_suite_is_a_decision_somebody_took` asks for.
  Two defensible positions; tonight's is the later one and was taken with the guard's contract in
  hand. **Do not apply that half.**

#### 2.3 `claude/aut071-s1-CYC-0074` — `426073c4e` — **PARTIAL, and the duplicated-work case**

| what | on the trunk? |
|---|---|
| the reading of PMC9780071 Table 2 (3 EMC pts, 0 ORR, 2 SD, 1 PD) | **yes** — tonight's S19, independently, in `RT-TRABECTEDIN.rationale` |
| the Chiusole-overlap caution | **yes** — tonight's version, in `remaining_unknowns`, and better argued |
| `palmerini2022trobsultrarare` source entry + `Trabectedin (second EMC-specific series)` row in `emc-clinical-registry.json` | **no** — 20 of 30 added lines absent |
| `EV-PALMERINI-2022` in `systems/graph/evidence.json` | **no** — 18 items, none is it |
| `RT-TRABECTEDIN.evidence` = `["EV-PALMERINI-2022"]` | **no** — `[]` on `origin/main` **and** in the live worktree |

Two independent reads of the same table four days apart agreeing exactly is corroboration worth
recording; it is also ~an hour of literature work done twice. **The registry gap is the substantive
one:** the trunk's route rationale now states counts in prose while the file the repository designates
as their home does not carry them, which is the shape CLAUDE.md §1 exists to prevent. Patches **P1**
(registry), **P2** (evidence node), **P2b** (the `emc-systems-map.json` key) — all clean.
`node scripts/validate-registry.mjs` is green on the live tree before the patch (24 citations, 14
cohorts, 0 warnings), and P1 uses only key shapes the file already uses (`pool` ×14,
`contextReason` ×9).

#### 2.4 `claude/s76-sgk1` — `d40898eb7` — **SUPERSEDED. DROPPABLE, nothing lost.**

⚠ **My first hypothesis here was wrong and the measurement refuted it.** `AUT-PD-099` is `done` on the
trunk and the string *"activity-shaped reading rather than an abundance one"* is still in
`routes.json` — which reads exactly like a row closed over a fix that never landed. It is not: the
corrected text **quotes the old clause inside its own "superseded, retained" note**, so the string is
present because the correction is present. The discriminating observation is the reverse-apply check:
**all five files reverse-apply clean**, and `61231a22c` on `origin/main` is the same commit message
and the same work, pushed to the trunk directly. The branch is a duplicate push.

#### 2.5 `claude/aut-pd-148-s5-CYC-0074` — `08f02f002` — **OBSOLETE**

The branch's finding — a quantity written in words is unfalsifiable because `claim_ablation` perturbs
digits only — was **fixed tonight by a different and fuller route** in `062a48ae1`, which names
AUT-PD-148 in its own comments: `perturbations()` now emits word swaps after digit swaps (order
load-bearing, so no prior verdict moves), `states_a_quantity()` widens **both** copies of the
population predicate, and `quantity_kind()` reports `digits|words|both|none`.

Residue: three census columns (`with_a_word_quantity*`) in `claim-coverage.json` — 128 of 128 lines
absent. **Recommend dropping them.** They are a second accounting of what `quantity_kind` now reports,
and a second copy of a count is the defect CLAUDE.md §1 names, not a gain.

#### 2.6 `claude/aut-pd-147-s3-CYC-0074` — `777ffdd5f` — ⭐ **STILL LIVE. The one to take.**

`test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py` (385 lines, absent) plus the
mutation harness taught to run three guard modules instead of two (51 of 51 lines absent).

**The gap reproduces at HEAD:** the sibling guard
`test_the_manuscripts_gene_identifiers_are_ones_an_artifact_names.py` scopes itself with a `DOCUMENTS`
map of **twelve ASO documents**, and none of the fusion-partner synthesis's three prose documents is
in it. The branch's measured claim — perturbing the endpoint declaration's `NR4A3` to `NR4A7` left the
quantity guard, the relation guard, three linters and the pooling check all green — is a claim about a
surface nothing else reads, and nothing has been added to read it since.

⭐ **Would it land green tonight? I re-ran its assertions against the live tree, in a standalone script
rather than under pytest** (charter §6, and S31's incident: no suite in a twelve-seat tree):

```
attestation corpus            902 files, 105,587 distinct identifier-shaped tokens
vacuity probes                NR4A7 NR4A9 EWSR7 TAF19 TAF16 TCF13 — all absent from the corpus
DOCUMENTS completeness        3 prose .md in fusion-partner/, 3 in DOCUMENTS, 0 unlisted
unattested identifiers        0 / 0 / 0  across the three documents
MUST_APPEAR floors            0 missing
fusion pairs vs the artifact  scoped to `kind: manuscript` → stratification only → 0 not permitted
```

⚠ **And one honest correction to my own run.** My first pass applied the pair check to all three
documents and reported a RED on `partner-event-counts-2026-08-08.md`, which prints `ACTB::NR4A3` and
`FUS::NR4A2`. That was my error, not the guard's: the guard scopes that check by front-matter `kind`
precisely because a register quotes what a source reports, and its docstring says so in advance, naming
that exact file. `kind: register` — out of scope. The guard is right and my model of it was wrong.

Patches **P3a** (new file) and **P3b** (harness), both clean.

#### 2.7 `claude/aut-pd-145-s2-CYC-0074` — `76a8f7f2d` — **OBSOLETE**

`unscored_ratchet.py` (⚠ **superseded, retained: this read "does not exist in this checkout — the file is only on that branch, on no ref this checkout
carries, and naming it here is a pointer to the branch's contents, not to a path a reader can
open". ⭐ **IT IS IN THE REPOSITORY NOW, AT `research/autonomy/unscored_ratchet.py`, RESCUED 2026-09-02 WITH ITS 11-CASE TEST.** A branch census read this branch rather than trusting the OBSOLETE verdict and found the file was single-ref — present on one of 302 refs and on no other — carrying findings recorded nowhere else: that a plain git ancestry range over one window **oscillated 84 → 85 → 84 → 85 inside four minutes while `--first-parent` was monotone**, because a commit that lived on a side branch carries a ledger missing every other branch's rows and so reports the population of a state the trunk was never in; and that an ancestry range silently admits commits whose timestamp PRECEDES its own start, two of which carried the +1 that made a series look as though it had risen when it had not. ⛔ Both are errors any instrument reading trunk history can make, this sprint's own branch census included. The OBSOLETE verdict on the branch stands — the ratchet it gated landed on the trunk on 2026-08-29 — but a branch being obsolete is not the same as every file on it being obsolete, and that distinction is what nearly lost this one**) plus a 203-line test, together measuring the entry condition for landing
`MAX_UNSCORED_OPEN`. **The ratchet itself landed on the trunk** on 2026-08-29 (`CYC-0083-381d0696`,
pinned at 73 — seven *below* the 80 it was written against — later re-pinned **down** to 69), and
`AUT-PD-145` is `done`. The condition this instrument existed to measure was met, by hand, twice.

**What is lost by dropping it:** the next re-pin measures the series by hand again, from the recipe
`AUT-PD-145` already writes out (`git log … -- research-ledger.json`, then `admissibility.is_unscored_open`
over each blob). That is a real but small cost, and it is a *convenience* item, not a defect.

#### 2.8 `s3/aut-pd-031-line-citations-enumerate-carriers` — `429241264` — **SUPERSEDED**

`line_citations.py` **1 of 147** added lines missing, its test **1 of 178**, `preflight.sh` **1 of 12**
— and each of the three is a context line the trunk has since reshaped (a print format, an import
placement, a loop entry that now also lists `instrument_census.py`). Droppable.

#### 2.9 `s1-aut-pd-050-unscored-rows` — `d082c01a7` — **SUPERSEDED, and it is the success story**

`continuity.py` 0/23, `priority.py` 0/68, `test_a_score_must_derive_from_its_own_inputs.py` 0/11.
The ratchet this branch *held back on purpose* was landed **verbatim from this exact sha** by
`CYC-0083-381d0696`, which the ledger records in those words. Residue: four lines of an older
"row(s) are UNSCORED" message the trunk has rewritten (`admissibility.py:661`).

⭐ **This is the branch that was recovered, and the mechanism was a pointer in a ledger row naming the
sha** — the same finding S31 reached from `seat/s1`. Two of two recoveries in this repository have
happened that way; no hook has ever done it.

#### 2.10 `aut-pd-058-deepen-ledger-history` — `4a56de2fa` — **SUPERSEDED. Do not apply.**

`stuck_clock.py` 0/20, `dev-setup.sh` 0/109. The only absent lines are **three
`@pytest.mark.skipif(shutil.which("git") is None, …)` decorators**, and the trunk's copy replaced them
deliberately with an explicit in-body check whose own docstring says a skipif *"is a check that can
evaporate"*. Applying the branch reintroduces exactly what the trunk removed — the `seat/s1` shape S31
warned about, from the other direction.

#### 2.11 `aut-pd-052-ci-autonomy-tests` — `ff828c1ce` — **SUPERSEDED**

`tests.yml` 0/12. Residue: one `amendments.jsonl` line recording the amendment. Bookkeeping only.

#### 2.12 `aut-pd-037-ledger-serialization` — `b29ffc4f1` — **SUPERSEDED**

`claim.py` 0/8, `priority.py` 0/7, `test_the_ledger_has_one_serialization.py` 0/149, `ledger_io.py`
1/37 — and the one line is `def write_ledger(...)`'s signature, which the trunk has since changed.
Droppable.

#### 2.13 `aut-pd-036-ls-files-scope` — `8aeeea201` — **SUPERSEDED, cleanly**

All four files, **0 of 103** added lines missing. Droppable, nothing lost.

#### 2.14 ⚠ Not one of the thirteen: `claude/s24-threshold-calibration` — `fc9a94776`, **tonight's**

Not an ancestor of `origin/main`. Both of its files exist in the working tree as **untracked** and
**differ from the branch** — the seat kept working after pushing. Nothing is lost by deleting the
branch *provided the driver commits the two worktree files*; if it does not, this is the fifth
stranding, happening tonight, exactly as S31 predicted.

### 3 · ⛔ A FALSE RECORD ON THE TRUNK, AND IT IS THE LOOP'S OWN EVIDENCE

`research/autonomy/receipts/CYC-0073-d4ccfde4.json`, committed on `main`:

| field | on the trunk | what the branch records |
|---|---|---|
| `handoff.attempted` | **`false`** | `true`, `succeeded: true` |
| `handoff.child_session_id` | **`null`** | `session_01NsMER9Gsh1jLUTPYS1561F`, created `2026-08-29T02:34:29Z` |
| `blocked_by` | **`[]`** | the push, 8 rejections in ~61 min, with the log path |

The trunk's receipt was written at step 10 and never updated, because the update was in the commit
that never merged. **`attempted: false` is not an absent reading — it is a positive claim that no
handoff was tried, and it is wrong.**

⛔ **The fix must be narrow, and here is why.** The branch's version also extends `changed`,
`what_i_got_wrong` and `now_queued` by ~3,850 characters, and that prose names `AUT-PD-161` as *"the
commit loop is slower than the trunk's push interval"* — which on the trunk is a **different row**
(§4) — and instructs a reader that *"the successor's first job is to merge that branch"*, which is
four days obsolete. Patch **P5** takes `handoff` and `blocked_by` only; every other field, including
the trunk's later rewording of `subagents._why`, is left byte-identical.

### 4 · ⛔⛔ EIGHT COLLIDED IDS — `AUT-PD-154` AND `AUT-PD-158` EACH NAME THREE DIFFERENT DEFECTS

S31 found this on `seat/s3` and called it "`AUT-PD-171` caught in the wild". Run across all thirteen,
it is not one instance:

| id | on the trunk | on a stranded branch | and again |
|---|---|---|---|
| **`AUT-PD-154`** | step 11 cannot complete in an auto-permission CCR session | `aut071`: a route quotes three figures its source retracted | `aut-pd-147`: a gene symbol can drift to another **real** symbol |
| **`AUT-PD-158`** | decide what `RT-AUTONOMY` is in `systems/graph` | `aut-pd-148`: bind the quantities written in words | `aut-pd-145`: R5 is on the trunk and open-unscored still grew |
| `AUT-PD-155` | the commit loop costs ~5× what CLAUDE.md says | `aut-pd-147`: one item's evidence is stamped on eight unrelated rows | — |
| `AUT-PD-156` | `amendment_guard.changed_paths()` (done) | `aut-pd-147`: 8 of 94 mutations no longer land, harness exits 1 | — |
| `AUT-PD-161` | `handoff.py` advertises rows that exist on no ref | `cyc0073`: the commit loop is slower than the push interval (**= trunk `AUT-PD-162`**) | — |
| `AUT-PROP-051` | widen `AUT-PROP-048` to the full panels | `aut071`: are TrObs's 3 EMC patients Chiusole's 3? | — |

⭐ **One of the collided branch rows I reproduced at HEAD in a single command, and it is filed nowhere
on the trunk.** `aut-pd-147`'s `AUT-PD-155` claims one item's `evidence` string is stamped on eight
unrelated ledger rows. Measured on the live ledger tonight — group the `evidence` field by value:

```
duplicate evidence strings shared by >1 row: 1
  8 rows: AUT-PD-049 done, AUT-PD-140 done, AUT-PD-132 done, AUT-PD-147 in_progress,
          AUT-PD-130 in_progress, AUT-PD-148 in_progress, AUT-PD-133 queued, AUT-PD-149 queued
  the text: "BUILT AND TESTED. Added `lease_arbitration()` to research/autonomy/continuity.py …"
```

**Eight rows, one item's evidence; five of them still open.** A reader deciding whether `AUT-PD-133`
has been worked reads a receipt for `lease_arbitration()`. That is a live defect, recovered from a
branch nobody read, wearing an id that means something else on the trunk.

⚠ The sibling claim on the same branch — that `mutate_fusion_partner_guard.py` exits 1 on `origin/main`
with 8 un-run mutations — is **UNKNOWN to me**: the harness builds clones and runs guard suites, and
charter §6 forbids me running that in a twelve-seat tree. What settles it is one run of that harness on
a settled tree. It is not evidence of absence either way.

---

## What I changed

**Nothing outside my one owned path.** No git write command of any kind was run — no merge,
cherry-pick, checkout, branch, stash, restore, add or commit. Every branch was already present under
`refs/remotes/origin`, so I did not even fetch. `git apply --check` is read-only and is the only
command that touched a patch against the tree.

⚠ **I ran no pytest.** The one thing I needed a suite to answer — would P3a's guard land green — I
answered by re-implementing its assertions in a standalone script in scratchpad that only reads
(§2.6). That was S31's incident and its cost is on the record.

**Patches, in scratchpad** (`…/e71cf460-51bb-5657-a314-50a7b993acba/scratchpad/patches/`), every one
`git apply --check` clean against the live worktree at `f9aa5df3`:

| patch | from | touches | verdict |
|---|---|---|---|
| `P1-aut071-registry-palmerini.patch` | `claude/aut071-s1` | `research/data/emc-clinical-registry.json` | clean |
| `P2-aut071-EV-PALMERINI-2022.patch` | `claude/aut071-s1` | `systems/graph/evidence.json` (rebuilt against the live file) | clean |
| `P2b-aut071-systems-map-key.patch` | `claude/aut071-s1` | `research/manuscripts/emc-systems-map.json` | clean |
| `P3a-aut-pd-147-identifier-guard-newfile.patch` | `claude/aut-pd-147-s3` | new test module, 385 lines | clean |
| `P3b-aut-pd-147-mutate-harness.patch` | `claude/aut-pd-147-s3` | `research/manuscripts/tests/mutate_fusion_partner_guard.py` | clean |
| `P4-aut-pd-130-missing-artifact-test.patch` | `claude/aut-pd-130-s4` | one test, spliced against the live file | clean |
| `P5-cyc0073-receipt-handoff-and-blocked.patch` | `cyc0073-d4ccfde4-work` | the receipt's `handoff` + `blocked_by` only | clean |

⛔ **No patch touches `research/autonomy/research-ledger.json`** (charter §2 — unownable this sprint).
⛔ **No patch touches `systems/views/*`** — generated; the driver regenerates.
⛔ **No patch for the eight superseded branches.** Applying any of them ranges from a no-op to a
regression (`aut-pd-058` and the `aut-pd-130` skip half would each undo a deliberate later decision).

---

## ⛔ Sequencing — and what must NOT be applied tonight

**Files this sprint has already moved** (`git status --porcelain`, read 20:07–20:35Z, 16 → 18 entries
while I worked — the tree is moving under this section): `scripts/preflight.sh`,
`scripts/regenerate_aso_chain.sh`, `.github/workflows/tests.yml`, `systems/graph/routes.json`,
`research/manuscripts/lint_citations.py`, `lint_citation_types.py`, `claim-coverage.json`,
`scripts/tests/test_affected_tests.py`, `.claude/skills/repo-gates/SKILL.md`, the ledger.

**None of my seven patches touches any of them** — that is why they are the seven.

| order | apply | why here | gate to run after |
|---|---|---|---|
| 1 | **P5** (receipt) | corrects a false record; touches one file nothing else reads | `contract_check.py` / gate 17 |
| 2 | **P4** (missing-artifact test) | additive test on a file that is clean at HEAD | that one test module |
| 3 | **P1** (registry) | additive row; `validate-registry.mjs` green before, and the keys are established | `node scripts/validate-registry.mjs`, then the citation/provenance gates |
| 4 | **P3a + P3b** (identifier guard) | verified green against the live tree; both files untouched tonight | the new module + `test_the_manuscripts_gene_identifiers…` (the shape-parity test binds them) |
| 5 | **P2 + P2b** (evidence node) | ⚠ **after the systems-graph seats settle**, then regenerate `systems/views/` | `systems_check.py`, then the generated-artifact check |

⛔ **THE ONE THING THAT MUST WAIT: `systems/graph/routes.json`.** The honest completion of P2 sets
`RT-TRABECTEDIN.evidence` to `["EV-PALMERINI-2022"]`, and that file is **modified in the tree right
now** by another seat. I deliberately did **not** write that hunk. Applying P2 alone is safe —
`check_evidence_base` **warns** on an orphan evidence item and does not err (read at
`systems_check.py:1725`, not assumed) — but it leaves the node reachable only from L5 until the wiring
lands. Do both, in that order, or neither.

⚠ P2 was rebuilt against the **live** `evidence.json` (18 items → 19), not lifted from the branch, so
`L5-evidence-base.md`'s counts must come from a regeneration and not from the branch's version, which
was computed against a different file.

---

## ⭐ Is it worth having? What is lost if each is dropped

| branch | keep? | what is lost by deleting it |
|---|---|---|
| `claude/aut-pd-147-s3` | ⭐ **KEEP** (P3a/P3b) | the only guard that would catch a gene-symbol slip in a publication-endpoint manuscript outside the ASO lane. Nothing else reads that surface. |
| `claude/aut071-s1` | ⭐ **KEEP** (P1/P2/P2b) | the registry's second EMC trabectedin denominator and the graph's evidence node for it — the trunk states those counts in route prose with no home behind them. |
| `cyc0073-d4ccfde4-work` | **KEEP the two fields** (P5) | a committed receipt keeps saying a handoff was not attempted when it was, and that no push blocked it when eight did. |
| `claude/aut-pd-130-s4` | **KEEP one test** (P4) | the ratchet on the only mutation that survived thirteen; the behaviour is correct today and unbound. |
| `claude/s76-sgk1` | **DROP** | nothing. Byte-for-byte on the trunk via `61231a22c`. |
| `aut-pd-036-ls-files-scope` | **DROP** | nothing. 0 of 103 added lines absent. |
| `aut-pd-037-ledger-serialization` | **DROP** | nothing but a superseded function signature. |
| `aut-pd-052-ci-autonomy-tests` | **DROP** | one `amendments.jsonl` line. |
| `s3/aut-pd-031-line-citations` | **DROP** | three context lines the trunk reshaped. |
| `s1-aut-pd-050-unscored-rows` | **DROP** | four lines of a message the trunk rewrote. Its real payload landed verbatim. |
| `aut-pd-058-deepen-ledger-history` | **DROP** | nothing — and keeping it is worse than dropping it, because applying it reinstates three skipifs the trunk deliberately removed. |
| `claude/aut-pd-148-s5` | **DROP** | three census columns duplicating what `quantity_kind` now reports. The defect itself is fixed. |
| `claude/aut-pd-145-s2` | **DROP** | an automated series measurement whose ratchet has already landed; the next re-pin does it by hand from a recipe the ledger already carries. |
| `claude/s24-threshold-calibration` | **n/a — tonight's** | nothing, **if** the driver commits the two untracked worktree files, which are newer than the branch. |

⛔ **Eleven of the thirteen are deletable after the five patches land.** That is the point of reading
them: a branch nobody can delete is carried forever, and eleven of these were carrying nothing.

---

## What I could not do, and what it is actually waiting on

- **Merging, cherry-picking or deleting any branch.** Correct: charter §1, and my prompt forbids every
  git write. The patches are written and checked; this is a driver act.
- **Writing ledger rows.** Charter §2 — proposed below.
- **Wiring `RT-TRABECTEDIN.evidence`.** Waiting on the seats holding `systems/graph/routes.json`
  tonight, not on anything else. It is one array element.
- **Verifying `aut-pd-147`'s second claim** (the mutation harness exits 1 on `origin/main` with 8 un-run
  mutations). Waiting on a settled tree, because the harness builds clones and runs guard suites — one
  run answers it. Recorded as **UNKNOWN**, not as absent.
- ⛔ **Nothing here is waiting on trimcrae.** No §3 trigger: no spend, nothing outward-facing, no
  irreversible act, no goal change.

---

## Ledger rows the driver should write

| id | `what` (proposed) | `kind` | `state` |
|---|---|---|---|
| new | ⭐ THE THIRTEEN UNREAD STRANDED BRANCHES ARE READ (S34, 2026-09-01). Eight are SUPERSEDED by content, two OBSOLETE, three carry live work; five patches written and `apply --check` clean (registry + `EV-PALMERINI-2022`; the fusion-partner identifier guard + harness; one mutation-derived census test; a receipt correction). Eleven of the thirteen are deletable once those land. Detail and per-branch evidence: `research/autonomy/sprint-2026-09-01/S34-STRANDED.md`. | `process_defect` | `in_progress` |
| new | ⛔⛔ ONE ITEM'S `evidence` STRING IS STAMPED ON EIGHT UNRELATED LEDGER ROWS AND FIVE ARE STILL OPEN. Reproduced at HEAD 2026-09-01 by grouping `evidence` by value: AUT-PD-049, 132, 140 (done), AUT-PD-130, 147, 148 (in_progress), AUT-PD-133, 149 (queued) all carry the `lease_arbitration()` receipt verbatim. A reader checking whether AUT-PD-133 was worked reads another item's proof. Found on `claude/aut-pd-147-s3-CYC-0074` as its "AUT-PD-155", an id that on the trunk means the commit-loop cost row — so it has been invisible for four days. | `process_defect` | `queued` |
| new | ⛔ `receipts/CYC-0073-d4ccfde4.json` ON THE TRUNK RECORDS `handoff.attempted: false` AND `blocked_by: []`, AND BOTH ARE FALSE. The cycle created `session_01NsMER9Gsh1jLUTPYS1561F` at 2026-08-29T02:34:29Z and was blocked by 8 push rejections over ~61 min; the update lived only on `cyc0073-d4ccfde4-work`. `attempted: false` is a positive claim, not a missing reading. Narrow patch ready (`handoff` + `blocked_by` only — the branch's narrative fields carry now-collided ids and an obsolete "merge that branch first" instruction). | `process_defect` | `queued` |
| `AUT-PD-171` (update) | ⛔ THE ID ALLOCATOR'S COLLISIONS ARE EIGHT, NOT ONE, AND TWO IDS NAME THREE DEFECTS EACH. Measured across all thirteen stranded branches 2026-09-01: `AUT-PD-154` and `AUT-PD-158` each mean three different things on three refs; `AUT-PD-155`, `AUT-PD-156`, `AUT-PD-161` and `AUT-PROP-051` each mean two. Two of the branch-side meanings are live findings filed nowhere on the trunk. This is the mechanism by which a real finding reads as already-handled. | `process_defect` | `queued` |
| `AUT-071` (update) | ⚠ THE PALMERINI/TrObs READING WAS DONE TWICE, FOUR DAYS APART, BY TWO SESSIONS THAT COULD NOT SEE EACH OTHER — `claude/aut071-s1-CYC-0074` on 2026-08-29 and tonight's S19-TRABECTEDIN. Both read PMC9780071 Table 2 and both got 3 EMC patients / 0 ORR / 2 SD / 1 PD, which is corroboration. ⛔ THE REGISTRY ROW AND `EV-PALMERINI-2022` ARE STILL ON NO OTHER REF: S19's scope excludes the registry and `RT-TRABECTEDIN.evidence` is `[]`. Patches P1/P2/P2b ready. | `fetch` | `queued` |
| new | ⭐ ADD THE FUSION-PARTNER IDENTIFIER-PROVENANCE GUARD, RECOVERED FROM `claude/aut-pd-147-s3-CYC-0074`. The repo-wide sibling guard's `DOCUMENTS` is twelve ASO documents; the fusion-partner synthesis is in none, so `NR4A3` → `NR4A7` there passes every gate that reads it. The branch's guard is mutation-tested (101 mutations, 93 caught, 0 survived, 7 caught by it alone) and its assertions were re-verified against the live tree 2026-09-01 — 105,587-token corpus, 6 vacuity probes absent, 0 unattested identifiers, floors intact, pair check green under its `kind: manuscript` scope. Patches P3a/P3b clean. | `process_defect` | `queued` |
| new | ⚠ UNKNOWN, NOT ABSENT: does `mutate_fusion_partner_guard.py` still exit 1 on the trunk with 8 un-run mutations whose anchors no longer occur? Claimed on `claude/aut-pd-147-s3-CYC-0074` (as its "AUT-PD-156", a collided id) and reproduced there on a pristine clone at `8edd15fe`. Not measured tonight because the harness builds clones and runs guard suites, which a twelve-seat tree cannot host. One run on a settled tree settles it. | `process_defect` | `queued` |
| new | ⚠ `claude/s24-threshold-calibration` IS TONIGHT'S FIFTH STRANDING IN PROGRESS. Not an ancestor of `origin/main`; both of its files exist untracked in the worktree and DIFFER from the branch (the seat kept working after pushing). Nothing is lost only if the driver commits `research/modalities/vaccine_threshold_calibration.py` and `.github/workflows/vaccine-threshold-calibration.yml`. | `process_defect` | `queued` |
