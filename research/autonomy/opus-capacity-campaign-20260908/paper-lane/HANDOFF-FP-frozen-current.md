---
id: DOC-OPUS-CAMPAIGN-HANDOFF-FP-FROZEN-CURRENT
title: "Frozen FP handoff, current — assembled from existing records only"
level: L4
kind: memo
status: live
purpose: >
  Carry the CURRENT frozen fusion-partner package to root as one document: exact pins read from disk
  and git, the nine round-11 findings each against its disposition, the targeted execution records as
  actually retained, the interrupted runs kept labelled INTERRUPTED, and a plain readiness statement.
scope: >
  L4. A COLLECTION. It produces no scientific result. Nothing was re-run, re-derived, re-reviewed or
  regenerated for it; no producer, gate, guard, figure or preflight was executed; no network request
  was made; no manuscript, artifact, packet, hold or receipt was edited; nothing was deleted.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Frozen FP handoff — current, collected not measured

**Collector, not reviewer.** Every value below was read from a file or from git on branch
`claude/confident-bardeen-ji76cd` at the time of collection. Where a record does not exist, the gap is
named as a gap. ⛔ No stopped run is reported as a pass anywhere in this document.

---

## 0 · Index — what is present, what is missing

| # | Asked for | State |
|---|---|---|
| 1 | Exact pins: manuscript, artifact, producer, guards, companions | ⭐ **PRESENT.** 18 paths, blob sha + bytes read at `HEAD`; all 18 working-tree-identical to `HEAD` |
| 2 | The nine round-11 findings, each mapped to its disposition | ⭐ **PRESENT, all nine, none merged.** 7 applied (register rows A34–A40), **2 open** (REF-B-2, REG-B-2) |
| 2a | **REG-B-2** | ⛔ **OPEN** — still in the generator (line 1129) and in the committed artifact |
| 2b | **REF-B-2** | ⛔ **OPEN** — prose discloses it; artifact still carries the disputed label |
| 2c | **A38 artifact/prose residual** | ⚠ **PROSE APPLIED, ARTIFACT HALF OPEN** — register row A38 says so in its own words |
| 3 | Five-module targeted execution record | ⭐ **PRESENT** — command, stdout and elapsed retained. ⚠ **ONE PART MISSING: no exit code was emitted for the pytest itself** (see §3.2) |
| 4 | Interrupted FP broad manuscript runs + termination timestamps | ⭐ **PRESENT**, seven termination markers, verbatim. ⚠ **The intended `STATUS: INTERRUPTED` block never landed as its own block** (see §4.4) |
| 4a | The newer ablation partial | ⭐ **PRESENT**, and ⚠ **it is NOT an FP ablation** — it covers two other papers (see §4.5) |
| 5 | Plain readiness statement | ⭐ **PRESENT** — §5. Root's position carried, not softened |
| 6 | Other eligible frozen candidate packages | ⭐ **PRESENT** — §6. Five other frozen handoffs exist; **every one is under a live paper-specific hold**, so **none besides FP is an unheld candidate** |
| — | A blind-seat record covering the current FP revision | ⛔ **DOES NOT EXIST.** Newest FP seats are pinned to `9d5b4def…` (round 11) |
| — | A `preflight.sh` / `PREFLIGHT_FULL=1` receipt for the current FP revision | ⛔ **DOES NOT EXIST** (see §5.3) |
| — | A repo-wide `lint_citations` pass | ⛔ **DOES NOT EXIST** — standing repo-wide failure, pre-existing, not re-measured here |

---

## 1 · Exact pins — read, not remembered

**Branch** `claude/confident-bardeen-ji76cd`. **`HEAD` = `39f861c14d86975d95abfd3cfe69b57fef79bc9f`**
("Two root metadata corrections; the endpoint source-validation evidence; systems map to 0 ERROR",
2026-09-08 19:03:06 +0000).

**The FP manuscript's own current pin is `4b2c54c5309d83c728e1ee0c5ae84159c4ceb0c1`**
("Fusion-partner round-11 repair batch, and the maintenance pointer fixes", 2026-09-08 18:20:16 +0000).
⭐ `4b2c54c53` is an **ancestor of `HEAD`** (checked with `git merge-base --is-ancestor`).

⚠ **This supersedes the earlier handoff.** `HANDOFF-fusion-partner-frozen-readiness.md` (17:26) freezes the
paper at `0f58b4ba` and reports the manuscript as **82,557 bytes**. That is no longer the current text: the
round-11 repair batch landed 40 minutes later and the manuscript is now **88,081 bytes**. Both documents are
retained; this one is the current one.

### 1.1 The pin table

Every row: path, git blob sha at `HEAD`, byte size. `WT=HEAD` records that the working-tree bytes are
identical to the blob at `HEAD`.

| role | path | blob sha (at `HEAD`) | bytes | last touched by | WT=HEAD |
|---|---|---|---:|---|---|
| **main manuscript** | `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md` | `5f03ef421917e9ac1235f4e150c7131cd381c5c4` | 88,081 | `4b2c54c53` | ✔ |
| second prose document (guarded identically) | `research/manuscripts/fusion-partner/emc-fusion-partner-correction-register.md` | `25d1dd2c9315ea4d0b12be96ce9b72a898da6fa5` | 61,026 | `4b2c54c53` | ✔ |
| **the one home of every number** | `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` | `2836e2fb417cf7db58e23351aedb23a76b39cd98` | 113,953 | `8c76f51bb` | ✔ |
| **producer** | `research/manuscripts/emc_fusion_partner_pooling.py` | `42bbdf97c424a5d2e1974997ff9d4496916bc5f8` | 141,313 | `8c76f51bb` | ✔ |
| extraction companion (read by two guards) | `research/manuscripts/fusion-partner/partner-event-counts-2026-08-08.md` | `34ff6670d14c7a8332aaa46524502fa17f3d9e0f` | 24,809 | `14a3f172d` | ✔ |
| foreign artifact bound by the prose guard | `research/modalities/gse28866-tumour-vs-normal.json` | `526084a99b3a44af0eb1720abe0ec268bae2c47a` | 27,256 | `14a3f172d` | ✔ |
| binding evidence contract | `systems/POLICY-evidence.md` | `f8a263b4733e39384cfccb2ee3c0ffa1582b5e48` | 22,663 | `14a3f172d` | ✔ |
| guard — prose↔artifact | `research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py` | `7f66ada9f2c2405d2dddcc52726fae576c78dc99` | 151,822 | `4b2c54c53` | ✔ |
| guard — relations | `research/manuscripts/tests/test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py` | `23f4b5e1660c262fb0142980e1ba21b16dfbe691` | 41,660 | `14a3f172d` | ✔ |
| guard — author-year↔citation-map | `research/manuscripts/tests/test_fusion_partner_author_years_are_bound_to_the_citation_map.py` | `902bbaec6cd52d2b9eec1c08c04ddb209c38f50b` | 14,989 | `14a3f172d` | ✔ |
| guard — gene-identifier attestation | `research/manuscripts/tests/test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py` | `db8276ae1923b277e85f571f9f82c6139af25775` | 24,233 | `14a3f172d` | ✔ |
| guard — generator `--check` | `research/manuscripts/tests/test_emc_fusion_partner_pooling_check.py` | `6cf12bc827d8492991daaa4e56cff42ae0dba07d` | 10,578 | `14a3f172d` | ✔ |
| the guards' own mutation harness | `research/manuscripts/tests/mutate_fusion_partner_guard.py` | `45eb5b826b81953a2806f95fb8fbf0eed03366de` | 54,876 | `14a3f172d` | ✔ |
| lane companion | `research/manuscripts/fusion-partner/lit-targets-partner-events.json` | `7d6e7c30d977cef24d6b9ec88533f61ebf9a78af` | 14,937 | `14a3f172d` | ✔ |
| lane companion | `research/manuscripts/fusion-partner/partner-strat-graph-records.json` | `c7e1388825e22738f6c5ddc063491eabd9ac1c29` | 29,605 | `14a3f172d` | ✔ |
| lane companion | `research/manuscripts/fusion-partner/emc-fusion-partner-map-edits.json` | `95925888b96c14b59e6a2cc0a7135e16f47613a5` | 8,487 | `14a3f172d` | ✔ |
| clause-1 evidence file | `research/autonomy/hardening-state/PUB-FUSION-PARTNER.json` | `29048fcdfdc848b6cfd317cec6dd4e75c42e45da` | 31,084 | `14a3f172d` | ✔ |
| pin registry binding three FP figures | `research/manuscripts/pinned-figures.json` | `77711bd742a79e3fd96b197007d9e83548202698` | 153,842 | `14a3f172d` | ✔ |

⭐ **All eighteen are clean:** no FP path is dirty in the working tree, and every blob size equals the
on-disk size. The only modified files in the tree are
`research/manuscripts/citation-provenance-ledger.json`,
`research/manuscripts/surface-targets/emc-surface-target-landscape.md` and its `-si.md` — another writer's
package. ⭐ **Checked, because it matters to CITE-B-1:** that uncommitted diff does **not** touch the Lenz
locator line; `emc-surface-target-landscape.md:674` still reads `2023;134:19-29. doi:10.1016/j.humpath.2022.12.005. PMID 36563884.`

### 1.2 sha256 for the five load-bearing files

```
c8f9c74aa03fa2e362be3149f5e3206c12a362f941c6f94639dde0526ad16980  emc-fusion-partner-stratification.md
b43ce728ac62fc3963628f44f8d87fddfa3ad5bc7b60703669f819a651efa287  emc-fusion-partner-correction-register.md
f60c550c617fdc34a2edc146c770cfd0ca2f3071a1d7e383b84acdf39cf6c53b  emc-fusion-partner-pooling.json
7ba6f81a3ee8f8f284f6cb59cc63a9657c6d791499bd7bdbec854c88c45ec9a9  emc_fusion_partner_pooling.py
6429e1a36edda3d9f69a7e89fc74c4c52c9f0228e79f726489ad4ceaf1daa3ed  test_fusion_partner_prose_matches_its_artifact.py
```

⭐ **The artifact and the producer are byte-unchanged since `8c76f51bb`** — their sha256 match the earlier
handoff exactly. **This is the fact that makes §2's two open findings open:** the round-11 batch changed
prose and one guard, and did **not** go through the generator.

### 1.3 One dependency that is NOT a fixed list, relayed not re-measured

`test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py` builds its attestation corpus by
walking `research/modalities/`, `research/data/` and `research/literature/`. The earlier handoff measured
that corpus at **936 files, 123,040,796 bytes** on the `0f58b4ba` tree. ⚠ **I did not re-measure it**, and
the tree has moved since, so treat that figure as the last recorded measurement rather than a current one.
It is a guard's corpus, not a dependency of the paper.

### 1.4 Publication record

`systems/graph/publications.json` → `PUB-FUSION-PARTNER`: `state: drafted`, `target_venue: preprint`,
**`blocked_by: null`**.

⚠ **A residual of REF-B-1 outside the manuscript, found while reading the pin and reported as an
observation, not as a re-opened finding.** Register row A36 bounded both prose superlatives in place —
verified: manuscript line 84 and line 363 now read *"in the sources this synthesis examined"*. But the
graph's `what_it_would_claim` for this paper still carries the **unqualified** form,
*"a magnitude this contrast has never had"*. Round-11's REF-B-1 was scoped to the Abstract and §3.3 of the
manuscript, so this is a third copy the sweep did not reach. ⛔ **Not edited here.** Named with its exact
location so the owner can close it in one move.

---

## 2 · The nine round-11 findings, each against its disposition

**Source of the nine:** `research/autonomy/hardening-state/PUB-FUSION-PARTNER.json` —
`reviewed_commit: 9d5b4defef94425c91ac7dcdfa6cf898a196a8ac`, `last_round: 11`,
`utc: 2026-08-29T12:34:27Z`, `converged: false`, **9 blockers and 25 P1 instances** across 5 seat files.
Its own note: *"Round 12 (apply) required, then a re-pin and re-seat."*

**All nine appear below. None is merged into another.**

| # | id | disposition | record that establishes it |
|---|---|---|---|
| 1 | **CITE-B-1** | ✅ **APPLIED** | Register row **A35**, *"Round-11 blind seat finding CITE-B-1, applied 2026-09-08"*; landed in `4b2c54c53` |
| 2 | **REF-B-1** | ✅ **APPLIED** in the manuscript (⚠ third copy open in the graph — §1.4) | Register row **A36**, *"…REF-B-1, applied 2026-09-08"*; `4b2c54c53` |
| 3 | **REF-B-2** | ⛔ **OPEN** | No register row exists. `4b2c54c53`'s own message: *"Two findings stay OPEN at the regeneration boundary"* |
| 4 | **REF-B-3** | ✅ **APPLIED** | Register row **A34**, *"…REF-B-3, applied 2026-09-08"*; `4b2c54c53` |
| 5 | **REG-B-1** | ✅ **APPLIED** | Register row **A40**, *"…REG-B-1, applied 2026-09-08"*; `4b2c54c53` |
| 6 | **REG-B-2** | ⛔ **OPEN** | No register row exists. Named as open in `4b2c54c53`'s message; still present in generator and artifact |
| 7 | **STAT-B-1** | ✅ **APPLIED** | Register row **A37**, *"…STAT-B-1, applied 2026-09-08"*; `4b2c54c53` |
| 8 | **STAT-B-2** | ⚠ **PARTLY APPLIED — prose applied, artifact half OPEN** | Register row **A38**, *"…STAT-B-2, **prose half applied** 2026-09-08"* |
| 9 | **STAT-B-3** | ✅ **APPLIED** | Register row **A39**, *"…STAT-B-3, applied 2026-09-08"*; `4b2c54c53` |

**Tally: 7 applied, 1 partly applied, 2 open. None superseded, none withdrawn.**
⚠ **No round-11 finding has been re-reviewed.** "Applied" means a repair was made and recorded; it does
**not** mean a seat has agreed the repair closes the finding. That agreement requires a re-pin and re-seat,
and none has happened (§5.1).

### 2.1 REG-B-2 — OPEN, verified open by reading both homes

**What the seat recorded** (hardening state, `blockers[5]`): the artifact's
`cohorts[llombart-bosch-2022-prevalence].context_note` asserts that *"Its TAF15 share over assigned cases
(7 of 26) is the highest of any series here"*, which is **false** — 7/26 = 26.9 %, against Agaram 7/24 =
29.2 % (pooled) and Sjögren 3/9 = 33.3 % (excluded). **It is third, not highest.** The seat's own
`driver_confirmed` field: *"YES -- 7/26 = 26.9% against Agaram 7/24 = 29.2% and Sjogren 3/9 = 33.3%, and the
manuscript's own S3.5 prints the per-cohort range as '15.8 - 29.2', which the artifact's superlative
contradicts."*

**Still open, read at the current pin — both homes:**

- Artifact `emc-fusion-partner-pooling.json`, `cohorts[llombart-bosch-2022-prevalence].context_note`,
  verbatim: *"…Its TAF15 share over assigned cases (7 of 26) is the highest of any series here and is quoted
  only as a range endpoint."*
- Generator `emc_fusion_partner_pooling.py` **line 1129**:
  `"Its TAF15 share over assigned cases (7 of 26) is the highest of any series here and is "`

**Why it was not closed** (`4b2c54c53`'s own message, quoted): *"REG-B-2's false 'highest of any series here'
(7/26 = 26.9% against 29.2% and 33.3% — third, not highest) lives in a generator string… Closing them is a
producer edit plus regeneration, which was out of scope."* ⛔ Not closed here either — this is a collection.

### 2.2 REF-B-2 — OPEN, and the manuscript itself says so

**What the seat recorded** (`blockers[2]`): the sunitinib series' comparator arm is labelled
`EWSR1::NR4A3` (6/8 = 75.0 %) *"on an inference the quoted evidence does not license, while the paper
refuses that exact label for the pazopanib arm."* The held quotations run *classical → SD/PR*; they do not
license *SD/PR → classical*.

**State at the current pin — the two halves have been separated, and only one is closed:**

- ⭐ **Prose half: disclosed.** §4.6 (manuscript lines ~640–653) now carries the caveat in the secondary
  analysis too, and names the residual itself: *"⛔ **The artifact still names that stratum `EWSR1::NR4A3`**
  in `cohorts[sunitinib-2014].strata` and `stratum_definition`; correcting it is a generator change and an
  artifact regeneration, and it has **not** been made — so the artifact and this limitation disagree on the
  label until it is."*
- ⛔ **Artifact half: open.** `cohorts[sunitinib-2014].strata` read at the current pin:
  `{"EWSR1::NR4A3": {"events": 6, "denom": 8}, "TAF15::NR4A3": {"events": 0, "denom": 2}}`
- ⚠ The manuscript's §3.1 secondary-analysis table (line 292) still prints **75.0 % (sunitinib, 6/8)** in
  the row the seat named. No count is disputed by the finding — only the label.

⚠ **This is not a closed finding, and the honest reading is that the paper now documents its own open
defect rather than having repaired it.** That is better than silence and is not the same as applied.

### 2.3 The A38 artifact/prose residual — prose applied, artifact half open

Register row **A38**, quoted verbatim from the file, is the record that establishes this:

> *"§6 now states the third choice and drops the completeness claim. ⛔ **The counts under the alternative
> criteria are deliberately NOT printed**, because every threshold that section states is derived in the
> generator from the artifact's own counts and no such field exists; and the artifact's twin sentence
> **still carries the superseded wording** until the generator is changed and the artifact regenerated.
> Round-11 blind seat finding STAT-B-2, prose half applied 2026-09-08."*

**Read at the current pin, confirming both halves:**

- ⭐ **Prose: applied, and the superseded sentence is retained rather than erased** — manuscript line 816:
  *"⚠ Superseded, retained: 'both choices make this falsifier easier to trigger.'"* The string
  `both choices` occurs **once** in the manuscript (that retention marker) and **zero** times in the
  artifact and **zero** times in the generator.
- ⛔ **Artifact: open.** `what_could_kill_this[4]` at the current pin still reads
  *"⚠ BUT ONE SUCH COHORT WOULD NOT OVERTURN THIS, AND SAYING SO IS PART OF THE FALSIFIER: it would take 19
  FURTHER TAF15 patients…"* — the completeness reading STAT-B-2 disputes, with no mention of the third
  degree of freedom. `zero_death_patients_to_reconcile()` in the producer is unchanged.

**So the A38 residual is exactly this: the paper and its own declared "one home of every number" disagree,
and the disagreement is documented rather than resolved.** ⛔ Closing it is a producer edit plus a
regeneration. Not done here.

### 2.4 What the applied seven actually moved — spot-checks, read not assumed

Two of the seven were re-read at the current pin to confirm the register's claim is true of today's text:

- **CITE-B-1.** Reference [10], manuscript line 1000, now reads *"**Hum Pathol** 2023;**134:19–29**. PMID
  36563884. doi:10.1016/j.humpath.2022.12.005"* — the locator the repository already held. ✅
- **REF-B-1.** Manuscript line 84 and line 363 both now read *"in the sources this synthesis examined"*, and
  line 84 adds *"no systematic search was run (§2.3a), so this is not a claim about the whole published
  record."* ✅ (⚠ third copy in `publications.json` — §1.4.)

⚠ The other five applied rows (A34, A37, A39, A40) are **relayed from their register rows and the commit
message; I did not re-verify each against today's prose line by line.** Treat those five as recorded, not as
independently re-checked by this collection.

### 2.5 The 25 P1s

⚠ **Not dispositioned anywhere I can find.** The hardening state holds all 25 (`ARI-P1-1/2`, `CITE-P1-1/2/3`,
`REF-P1-1…7`, `REG-P1-1…8`, `STAT-P1-1/2/3`). `4b2c54c53` addressed **blockers only**; no register row
references a P1 id. **Root asked for the nine, and the nine are above — but the 25 are an unmeasured surface
and should not be assumed clean.** Among them, `CITE-P1-3` records the committed mutation harness exiting
**RC=1** at the pin (94 declared mutations, 86 caught, 0 survived, **8 UN-RUN** on anchor drift), with the
seat's own note that it re-anchored six and all six were caught, so guard coverage was intact and the defect
was confined to the harness. ⛔ **I did not run the harness**; that is the recorded state as of the round-11
pin, not a current measurement.

---

## 3 · The five-module targeted execution record

### 3.1 The command, exactly as recorded

Recorded **2026-09-08T18:19:19.266Z**, tool call `toolu_01SJe6ThAY3QgrV7toV9kZkB`, immediately before the
`4b2c54c53` commit at 18:20:14Z. Command stream verbatim:

```
cd /home/user/Rare-cancers
/root/.local/bin/pytest -q research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py research/manuscripts/tests/test_fusion_partner_prose_asserts_the_relations_its_artifact_computes.py research/manuscripts/tests/test_fusion_partner_author_years_are_bound_to_the_citation_map.py research/manuscripts/tests/test_the_fusion_partner_gene_identifiers_are_ones_an_artifact_names.py research/manuscripts/tests/test_emc_fusion_partner_pooling_check.py 2>&1 | tail -3
python3 research/manuscripts/lint_style.py >/dev/null; echo "style gate exit=$?"
python3 research/manuscripts/lint_consistency.py | tail -1
```

**The five modules are exactly the five FP guards pinned in §1.1.**

### 3.2 The retained output, verbatim

Result recorded 2026-09-08T18:19:29.379Z, `is_error: false`:

```
........................................................................ [ 80%]
....................................                                     [100%]
180 passed in 2.76s
style gate exit=0
lint_consistency: 0 ERROR across 29 target file(s)
```

**What is retained:** the command; the pytest progress tail and its summary line **`180 passed in 2.76s`**;
`lint_style.py` (no-argument gate form) **exit 0**; `lint_consistency.py` final line **`0 ERROR across 29
target file(s)`**.

⚠ **What is MISSING, named exactly and not reconstructed: the pytest run's own exit code was never
emitted.** The command pipes pytest through `2>&1 | tail -3` with **no `echo "EXIT=${PIPESTATUS[0]}"`**, so
no exit status for the pytest was captured, and none appears in the record. ⛔ **I will not write EXIT=0 for
it.** `180 passed` with no `failed`/`error` token in the retained tail is what the record supports and is all
this document asserts. The two lint lines below it **do** carry real observed status (`style gate exit=0`).

⚠ **`2>&1` merges stderr into stdout**, so there is no separately retained stderr stream for this run. Nothing
warning-shaped appears in the retained three lines, but a separate stderr record does not exist.

### 3.3 Corroboration in the commit message (a second record, same run)

`4b2c54c53`, verbatim: *"⭐ THE GUARD DIFF IS TIGHTER, NOT LOOSER — the thing I was required to check. The
identifier census widens from ("pmid","doi","nct") to include "pmc", keying on the artifact's real `pmcid`
field; the floors are untouched at <= 20, >= 90 and >= 12; and the module diff is additions only. I re-ran the
five fusion-partner modules myself: 180 passed, exit 0. lint_style gate 0 ERROR exit 0, lint_consistency 0
ERROR."*

⚠ **The message says "exit 0" for the pytest; the retained command stream does not contain a measurement of
it.** Both are recorded here so root can see the discrepancy rather than inherit the stronger of the two. On
the evidence actually retained, **the pytest exit code is unmeasured**.

### 3.4 One earlier targeted record, retained and complete for what it covers

Recorded 2026-09-08T15:19:43.044Z (`toolu_01CTbxgCLesuLLSbdYa1tFU5`), the `0f58b4ba` one-word reword:

```
reworded
lint_claims: 0 ERROR, 183 WARN across 137 file(s)
lint_style: 0 ERROR across 15 file(s)
lint_consistency: 0 ERROR across 29 target file(s)
137 passed in 0.50s
```

⚠ **This is the single prose↔artifact module only (137 tests), on the pre-batch text.** It is not the
five-module run and must not be quoted as one. Its own exit codes were likewise not captured (`| tail -1`
throughout).

### 3.5 Costs the same commit reported against itself, relayed unchanged

From `4b2c54c53`, verbatim, because they are measurements and they went the wrong way:

> *"⚠ Reported as costs, not smoothed. … ⚠ The explicit-path register measurements got WORSE (manuscript 191
> -> 208, register 155 -> 190); both files are off-gate, but this is a real release-side regression from
> adding bold and em-dashes in repository register. ⚠ claim-coverage.json was ALREADY stale for this paper
> before the batch (303 committed vs 312 baseline) and this batch moves it to 324/95; it is NOT regenerated
> here… The census pairing is recorded as owed."*

⛔ **Not re-measured here.** `lint_style.py` on an explicit path is **not the gate** — the gate is the
no-argument form, which does not cover this manuscript at all (its `TARGETS` list omits it). The 208 is a
register measurement, not a failing gate.

---

## 4 · Interrupted work — INTERRUPTED, NOT PASSED

**Primary record, retained and intact:**
`/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/interrupted-2026-09-08/observed-before-stop.txt`
— **68,528 bytes**, 541 lines, opening line
`RECORD of processes observed before termination, 2026-09-08T18:13:02Z`.

⛔ **Nothing below is a pass. No exit code was emitted by any run in this section.**

### 4.1 The FP broad manuscript test runs that were stopped

The broad run's own command line, captured verbatim inside the record (line 77, pid 25870/25872/25874):

```
timeout 580 /root/.local/bin/pytest -q research/manuscripts/tests/ -p no:cacheprovider 2>&1 | tail -6; echo "EXIT=${PIPESTATUS[0]}"
```

⚠ **That `echo "EXIT="` never ran.** The pipeline was killed by `SIGTERM` before pytest finished, so **no
`EXIT=` line for it exists anywhere.** At the moment of the record it had been running **08:45** elapsed.

**Every recorded termination marker, verbatim and in file order:**

| line | marker as written in the file |
|---:|---|
| 1 | `RECORD of processes observed before termination, 2026-09-08T18:13:02Z` |
| 101 | `TERMINATED_UTC=2026-09-08T18:13:12Z` |
| 102 | `--- REPLACEMENT WIDE RUN observed and stopped 2026-09-08T18:13:43Z ---` |
| 189 | `--- final sweep 2026-09-08T18:13:58Z ---` |
| 274 | `--- relaunched wide run stopped 2026-09-08T18:14:31Z ---` |
| 363 | `--- stopped 2026-09-08T18:15:11Z ---` |
| 450 | `--- redundant poller stopped 2026-09-08T18:25:05Z ---` |
| 538 | `--- unauthorized broad ablation sweep observed 2026-09-08T18:36:13Z ---` |
| 541 | `TERMINATED_UTC=2026-09-08T18:36:25Z — broad ablation sweep, INTERRUPTED NOT PASSED` |

**Five successive wide `research/manuscripts/tests/` runs were started and each was terminated** — the
original (18:13:12Z), a replacement (18:13:43Z), a relaunch (18:14:31Z), a further one (18:15:11Z), and the
poller left waiting on a file nothing would finish writing (18:25:05Z). ⛔ **None completed. None produced a
summary line. None produced an exit code.**

### 4.2 The truncated stdout the stopped runs left behind

Both partial outputs are retained on disk and both stop mid-progress-bar with **no summary line**:

| file | bytes | last retained content |
|---|---:|---|
| `…/scratchpad/wide_with_changes.txt` | 371 | four full progress rows to `[ 14%]`, then 51 dots — cut off |
| `…/scratchpad/wide2.txt` | 298 | three full progress rows to `[ 10%]`, then 58 dots — cut off |

⛔ **Neither contains `passed`, `failed`, or `EXIT=`.** They are evidence of how far a run got, and of
nothing else.

### 4.3 What the two files were and were not

The 18:13 sweep also signalled several **B2-lane pollers** waiting on
`/tmp/claude-0/b2-lane/out/BASELINE-fullsuite.txt` (pids 18798, 18864, 18908) — those belong to a different
lane and are recorded in the file as *"old B2 pollers, NOT touched"* at the earlier sweeps. They are named
here only so the pid list in the record is not misread as all-FP.

### 4.4 ⚠ The gap in this record, named exactly

**The intended `STATUS: INTERRUPTED — NOT PASSED` block was never appended as its own block.** The command
that would have written it (`toolu_01PwQLfgWsjfqXu6aMq99Fz7`, 2026-09-08T18:15:09.181Z) **returned exit code
144** — the shell was itself terminated by the `pkill` it had just issued, before its `cat >> … <<'EOF'`
heredoc ran.

⭐ **The text survives anyway, and only incidentally:** the *next* `ps` capture recorded the still-forming
process's own command line, so the intended wording is preserved verbatim inside **line 448** of the record,
as the arguments of pid 31736 rather than as a status block:

> *"STATUS: INTERRUPTED — NOT PASSED. Every wide `research/manuscripts/tests/` run listed above was
> terminated by SIGTERM before completion, except where a completed result is recorded separately. No exit
> code from these runs is a pass, none is a baseline, and none may be quoted as acceptance evidence. Original
> command strings, elapsed times and termination timestamps are retained above. Nothing was deleted."*

⛔ **Recorded as a partial write, not reconstructed.** The missing part is precisely: *the standalone status
block at the tail of the file.* Its content is not lost; its placement is. **The labelling stands and is
carried forward by this document.**

### 4.5 The newer ablation partial — and what it is actually about

**Observed** 2026-09-08T18:36:13Z, **terminated** 2026-09-08T18:36:25Z, marked in the record itself as
`INTERRUPTED NOT PASSED`. It was a `repro.py` sweep (pids 15273/15275, 04:28 elapsed at observation),
described in the record's own marker as an *"unauthorized broad ablation sweep"*.

⚠ **It is NOT a fusion-partner ablation.** Its two preserved partial outputs — copied into the interrupted
directory before the stop, and intact — cover two other papers entirely:

| preserved file | bytes | rows completed | paper |
|---|---:|---:|---|
| `repro-fusion-junction-aso-journal-article.json` | 4,923 | **8** | the ASO journal article |
| `repro-response-endpoint-indolent-tumours.json` | 1,916 | **4** | the response-endpoint manuscript |

Each row is a per-sentence ablation record (`status: applied`, `red: true/false`, the mutation, the guards
that read it). One row is instructive and is quoted because it is a negative result:
`red: false`, *"no guard reading this file noticed any of: 282->287, 100->107, Two->Six, three->seven,
one->two"* — an unread surface in the endpoint paper, **not in FP**.

⛔ **These twelve rows are a partial sweep, not a completed ablation, and they say nothing about FP.**
`…/scratchpad/repro.log` is 159 bytes and holds one line: `python3: can't open file '…/repro.py': [Errno 2]
No such file or directory` — the script was removed after the stop, so **the sweep is not resumable from this
record and the row count above is all there is.**

⛔ **No FP `claim_ablation.py` run exists at the current pin, interrupted or completed.** That is a gap, not
a zero.

### 4.6 Retention

⛔ **Nothing in `interrupted-2026-09-08/` was deleted, moved or rewritten by this collection**, and nothing
elsewhere in the campaign tree was either. `FP1-executed-artifacts/` is intact — `BEFORE`/`AFTER`
manuscripts, `applied-fixes.diff`, and `ORIGINAL-CHILD-TRANSCRIPT-a81e800ea32b54de9.jsonl` (437,485 bytes).
Per CLAUDE.md §8 these stay intact until a directory-specific local receipt verifies them; **no such receipt
naming `FP1-executed-artifacts/` was found**, so it stays.

---

## 5 · Readiness — root's position, carried

⛔ **A revised main manuscript plus its guard is NOT final-review-ready.** That is root's position and this
collection does not soften it. The five-module green in §3.2 and the seven applied register rows in §2 are
real work, and they are **not** the evidence a final review needs.

**What is actually still missing:**

### 5.1 Independent review of the revision that exists — the decisive gap

⛔ **No blind seat has ever read this text.** `hardening-state/PUB-FUSION-PARTNER.json` is pinned to
`9d5b4defef94…`, round 11, `converged: false`. There are **29 FP seat files** in
`research/autonomy/review-seats/`, across **seven** pinned shas (`053a8211…`, `0743ac15…`, `21bc8578…`,
`34264bbe…`, `475ad7d0…`, `69d8a6ac…`, `9d5b4def…`). **None of them is `4b2c54c5`, `0f58b4ba`, `56c9f985` or
`39f861c1`.** Since publish-bar clause 1 grades the commit to be posted against seats covering **that sha**,
this revision has **no clause-1 evidence at all**. ⭐ A missing measurement is unknown, not a pass.

### 5.2 Two round-11 blockers are still open, and a third is half-open

REF-B-2 and REG-B-2 are **open in the artifact and the generator** (§2.1, §2.2); STAT-B-2's artifact half is
open (§2.3). All three sit **behind the same regeneration boundary**: closing them means editing
`emc_fusion_partner_pooling.py` and regenerating `emc-fusion-partner-pooling.json`, which no one has done.
⛔ **A paper cannot go to final review while its own declared "one home of every number" contradicts its
prose in three named places.**

### 5.3 No preflight receipt for this revision

⛔ **Neither `scripts/preflight.sh` nor `PREFLIGHT_FULL=1` has a receipt for any FP commit.** The one
`PREFLIGHT_FULL` result in this campaign is `RESULT-preflight-full-6186189a.md`, and it is **for the ATR
candidate commit `6186189abf5291fabdd45819ae42474eecb5ee74`** (an ancestor of `HEAD`, 16:16Z, i.e. *before*
the FP batch), and its conclusion is **FAILURE**: run 34250066740, log ends `PREFLIGHT FAILED -- do not
commit.` / `EXIT=1`, **no receipt exists**, and `publish_bar`'s `preflight_full_green` clause has no evidence
for that commit either. ⛔ It is not FP evidence in any direction.

### 5.4 Round 12 is not finished on the ledger's own terms

`research/autonomy/research-ledger.json` row **AUT-PROP-052** states the contract:
*"ROUND 12 IS AN APPLY ROUND: CLOSE THE NINE ROUND-11 BLOCKERS, THEN RE-PIN AND RE-SEAT AS ROUND 13."*
**Seven of nine are closed. The re-pin has not happened and the re-seat has not happened.** By the row's own
definition round 12 is incomplete, and its `depends_on_evidence` still records
*"publish_bar --paper PUB-FUSION-PARTNER --sha 9d5b4defef94 2026-08-29: BLOCKED 4/7. Clause 1 FAIL (9
blockers, 25 P1s at round 11), clause 6 FAIL, clause 2 absent."*

### 5.5 The other things a final review would ask for, which do not exist

- ⛔ **The 25 round-11 P1s have no dispositions** (§2.5) — an unmeasured surface, not a clean one.
- ⛔ **No source↔generator check exists.** `--check` closes generator↔artifact and the five guards close
  artifact↔prose; **nothing in this repository closes source↔generator**. Every cohort count is typed into
  the producer's own tables and there is no independent input to re-verify them against by machine.
- ⛔ **No FP claim-ablation** at this pin (§4.5).
- ⛔ **`lint_citations` still fails repo-wide** — pre-existing, untouched, not re-measured here.
- ⚠ **Gate coverage is partial:** `lint_style` does not cover this manuscript at all (not in `TARGETS`);
  `lint_consistency` covers it for **three pinned figures only**, via `must_appear_in` rather than via the
  29-target list.
- ⚠ The manuscript's front matter still reads `date: 2026-08-08` / `last_verified: 2026-08-08`, which
  predates every 2026-09-08 correction.

### 5.6 What is genuinely settled

⭐ Pins are exact and clean (§1). ⭐ Seven of nine round-11 blockers have recorded, located repairs, and the
guard diff that accompanied them was **additions only, with no floor lowered and no regex loosened**
(`4b2c54c53`, relayed). ⭐ The two findings that were not closed were **reported as open in the commit that
closed the others**, not smoothed away, and one of them is disclosed on the paper's own pages. ⭐ Every
interrupted run is labelled as interrupted, and the evidence is intact.

⛔ **Publication authority is not sought and not granted by this document.** `publication-authority.json`
does not exclude PUB-FUSION-PARTNER from the aiXiv standing grant, but the grant covers endpoints *passing
all clauses* and **clause 1 has no evidence for this revision** (§5.1). This handoff is not a publication act
and requests none.

---

## 6 · Other frozen candidate packages on disk

**Answer: none besides FP is an unheld candidate.** Five other frozen handoff packages exist in this
lane; **every one of them is paired with a live paper-specific HOLD.** Per instruction the holds are
**documented and skipped** — not worked around, not reworded, and no fresh merit pass sought for any of them.

| package | frozen handoff | hold that governs it | status |
|---|---|---|---|
| ATR collaborator package | `HANDOFF-ATR-frozen-readiness.md` (9,834 B) | `HOLD-atr-release-path.md` (19,622 B, `status: live`, updated 19:01) | ⛔ **HELD** — release path blocked; also the only `PREFLIGHT_FULL` in this campaign, and it **failed** (§5.3) |
| Biomarker-selected classes | `HANDOFF-biomarker-frozen-readiness.md` (10,872 B) | `HOLD-biomarker-selected-classes.md` (7,117 B, `status: live`) | ⛔ **HELD** |
| Response endpoint in indolent tumours | `FROZEN-HANDOFF-endpoint-response.md` (7,732 B) | `HOLD-endpoint-extraction-validity.md` (6,886 B, `status: live`) | ⛔ **HELD** — extraction validity |
| HLA population coverage | `HANDOFF-hla-coverage-frozen-readiness.md` (18,235 B) | `HOLD-hla-population-coverage.md` (9,583 B, `status: live`) | ⛔ **HELD** — and the publication record lists it **`blocked_by: BLK-ANTIGEN-COLD`** |
| Mortality mechanisms | `HANDOFF-mortality-frozen-readiness.md` (12,568 B) | **two** holds: `HOLD-mortality-causal-ceiling.md` (9,168 B) and `HOLD-mortality-death-counts.md` (6,834 B), both `status: live` | ⛔ **HELD** |

⛔ **`PUB-CLOSED-ROUTES` is not a candidate and is not listed as one.** `STOPPED-closed-routes-held-paper/`
records that a lane was dispatched against it in error and stopped; the **CR1 route-permission / merit hold
stands unchanged**, and its preserved partial edits are explicitly *"not a candidate, not an approved
revision, and not to be applied."* ⛔ Not touched, not re-audited, not re-opened here.

⭐ **FP is the only package in this lane that is frozen, pinned clean, and carries no paper-specific HOLD**
(`blocked_by: null`). ⚠ That is what makes it a candidate. It is **not** what makes it review-ready — §5
states why it is not.

---

## 7 · What this document is not

⛔ It is not a review, not an adjudication, not a merit pass, not publication permission, and not a claim
that any gate is green. No producer, gate, guard, figure, preflight or test was run for it; no network
request was made; no manuscript, artifact, packet, hold or receipt was edited; no commit, push, branch or
worktree was created; **nothing was deleted.** Where a record does not exist — a seat for this revision, a
preflight receipt, an FP ablation, dispositions for the 25 P1s, an exit code for the five-module pytest, the
standalone `STATUS: INTERRUPTED` block — this document says so and stops there.

---

## 8 · Addendum — `HEAD` advanced during collection, and no FP pin moved

⭐ **Recorded because a pin read against a moving branch must say which commit it was read at.**

The §1 pin table was read at **`HEAD = 39f861c14`**. While this collection was being assembled, another
writer landed seven further commits on the same branch, ending at
**`ae7591846`** ("Surface-target batch NOT accepted, preserved intact; the decisions register for root"):
`3286feff0`, `bab81c4e8`, `b7bf80377`, `88a748672`, `40249d7c0`, `dbc29ae7d`, `ae7591846`.

⭐ **Re-checked at the new `HEAD`, not assumed:** `git diff 39f861c14 HEAD` over the fusion-partner
directory, the producer, `research/manuscripts/tests/`, `hardening-state/`, `pinned-figures.json`,
`POLICY-evidence.md`, `gse28866-tumour-vs-normal.json` and `publications.json` is **empty**. **Every one of
the eighteen pins in §1.1 is unchanged, and the FP manuscript's own pin is still `4b2c54c53`.**

⭐ The CITE-B-1 corroborating locator also re-checked at the new `HEAD`:
`emc-surface-target-landscape.md:669` reads `2023;134:19-29. doi:10.1016/j.humpath.2022.12.005. PMID
36563884.` — the surface-targets working-tree changes noted in §1.1 were resolved by that writer as **NOT
ACCEPTED and preserved intact**, and the line number moved from 674 to 669 without the locator changing.

⚠ Nothing in those seven commits touches FP, and **none of them is a review, a seat, a re-pin or a preflight
receipt for FP.** §5 is unchanged by them.
