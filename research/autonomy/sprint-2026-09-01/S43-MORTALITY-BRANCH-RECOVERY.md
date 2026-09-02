---
id: DOC-SPRINT-S43-MORTALITY-BRANCH-RECOVERY
title: "S43-MORTALITY-BRANCH-RECOVERY — the stranded mortality family is 53 files rather than 15, nothing on it is superseded by the trunk, and four of its seven graph rows are stale against its own later commits"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Decide, per file and per graph row, whether the ST-MORTALITY-MECHANISM family stranded on
  origin/claude/emc-symptom-treatment-742257 is work the trunk has since overtaken or work the trunk
  never had, applying the standard S39 set when it refused the atlas recovery: a route whose evidence
  has since been retracted or corrected must not be recovered.
scope: >
  The 53 files the branch's own thirteen commits touched, read against origin/main as of
  4f54ac80b967. Grades the seven graph rows, the two manuscripts, the five analysis scripts, the five
  probe scripts, the nine result and corpus artifacts, the four test files, the seven generated views
  and the twenty-one modified shared files. Proposes; changes no graph file.
last_verified: 2026-09-02
---

# S43 — the stranded mortality family, read against the trunk

**Item:** `AUT-083-e71cf460` · **Branch tip read this session:**
`git rev-parse origin/claude/emc-symptom-treatment-742257` → **`59bb15cbe9b61e20a48f43016dc47030ed46ed51`**
(after `git fetch origin --prune -q`; `origin/main` at `4f54ac80b9672851b3da34846a346fb650f6c830`).
**Owned paths:** this memo and `S43-proposed-graph-additions.json`. **No git write command was run.**
**Started/Finished (UTC):** 2026-09-02T08:05Z / 2026-09-02T08:35Z.

## Verdict

**RECOVER THE FAMILY — but not by taking the branch, and not the rows as written.** Nothing in this
family is superseded by the trunk on its science: the one supersession found is a lung *retrieval*
that `main` re-ran better a day later, and one figure-provenance stamp the trunk has since moved past.
**Zero rows rest on a retracted or corrected trunk artifact** — the failure mode S39 refused the atlas
for. ⛔ **What is stale is stale against the branch's OWN later commits**, which is a defect a
path census cannot see and which makes the six route rows unusable verbatim: `routes.json` was last
written at commit `7b32ebe6f`, **six commits before** the correction that moved the headline competing
share from 39.4 % to 21.7 % and before the commit that closed the background check the rows still list
as missing.

★ **Three of the seven graph rows are RECOVER as written; four are NEEDS-REGRADE; none is SUPERSEDED.**

---

## 1 · ⛔ THE INVENTORY IN THE LEDGER IS WRONG IN TWO DIRECTIONS, AND THE INSTRUMENT THAT PRODUCED IT WAS A PATH DIFF

The `AUT-083` row and S38 §C-10 say the branch carries *"2 manuscripts, 5 scripts, 4 tests and 4
literature probes, plus `ST-MORTALITY-MECHANISM` and six `RT-*` routes in its `systems/graph/routes.json`"*.
**Verified rather than inherited, and three parts of that sentence do not survive.**

### 1.1 · A raw path diff over-reports by 170 files, because `main` reorganised `research/manuscripts/`

    $ git ls-tree -r --name-only <branch>  > branch-files.txt   # 2 852 paths
    $ git ls-tree -r --name-only origin/main > main-files.txt   # 7 051 paths
    $ comm -23 <(sort branch-files.txt) <(sort main-files.txt) | wc -l
    203

**203 is an artefact.** `research/manuscripts/nr4a3-degrader-paper.md` is in that list and is not
stranded — `main` holds it at `research/manuscripts/degrader/nr4a3-degrader-paper.md`. Re-running the
diff on **basenames** gives **33**, one more than S38's 32 (the extra is
`research/manuscripts/fusion-junction-aso-paper.md`, which belongs to `PUB-ASO` and not to this family).

⚠ **THE INSTRUMENT WAS TESTED BEFORE ANY VERDICT WAS TRUSTED**, per S38's own warning that
`git rev-parse` echoes an unresolved path instead of failing. `git cat-file -e <ref>:<path>` was run
against a path known to be absent (`research/manuscripts/THIS-FILE-DOES-NOT-EXIST-xyz.md`) on both
refs and returned ABSENT on both, and against two paths known present, before it was used anywhere.

### 1.2 · ⭑ AND ANCESTRY WORKS — THE BRIEF AND THE LEDGER ARE BOTH WRONG THAT IT MIGHT NOT

    $ git merge-base origin/main 59bb15cbe9b6
    ddd98c03ebd8f6eac518e42aeef21e780ef02d9f     (2026-08-09, "in-flight board (CI)")
    $ git rev-list --count origin/main..59bb15cbe9b6
    13

**The branch does share a merge-base with `main`**, so the tree-diff-only instruction was a precaution
rather than a necessity — and the merge-base is the far better instrument, because it isolates *what
this branch's work did* from *what the trunk did in the three weeks since*.

    $ git diff --name-status ddd98c03ebd8 59bb15cbe9b6 | sort
    ... 53 lines: 32 A, 21 M

★ **THE REAL INVENTORY IS 53 FILES — 32 ADDED, 21 MODIFIED.** The ledger's "2 + 5 + 4 + 4" names
**15 of the 32 added** and **none of the 21 modified**. The uncounted work is: 5 committed JSON results,
5 probe *corpora* (the ledger's "4 literature probes" conflates 5 probe scripts with 4 corpora),
7 generated views, and twenty-one edits to files that exist on both refs — **which a path census is
structurally blind to, and two of which are load-bearing on whether the recovery even runs** (§4).

### 1.3 · `ST-MORTALITY-MECHANISM` is not in `routes.json`

    $ for f in $(git ls-tree -r --name-only <branch> systems/graph/); do ... grep -c ST-MORTALITY-MECHANISM
    systems/graph/modalities.json: 1
    systems/graph/routes.json:     6      <- six RT rows' `strategy` field, not a definition
    systems/graph/strategies.json: 1      <- the definition

The strategy family is defined in **`strategies.json`**. `routes.json` only *references* it. Minor, but
a recovery patch written from the ledger's sentence would put a strategy row in the wrong file.

---

## 2 · THE SEVEN GRAPH ROWS

**Route-id and strategy-id set derived by set-difference on parsed JSON**, not by grep:
`{r['id'] for r in branch routes} - {r['id'] for r in main routes}` = the six `RT-*` below
(branch 74 routes, main 77, main-only 9); `branch strategies − main strategies` = `ST-MORTALITY-MECHANISM`
alone, and `main − branch` = `ST-CARE-DELIVERY` alone.

### 2.1 · ⭑ FIRST, THE SUPERSESSION QUESTION S39 ASKED — AND THE NEAR-MISS

**`main` minted `ST-CARE-DELIVERY` the same day (2026-08-09) that the branch minted
`ST-MORTALITY-MECHANISM`, and it landed while this one did not.** That is the one candidate for
"the trunk already has this", and it fails on both families' own `purpose` strings:

| | question it asks |
|---|---|
| `ST-CARE-DELIVERY` (on `main`, 7 routes) | *"Which of this disease's survival is decided by the care a patient actually receives — the diagnosis, the operation, the follow-up — rather than by which agent they are given?"* |
| `ST-MORTALITY-MECHANISM` (branch only) | *"When an EMC patient dies, what is the proximate mechanism — and is any of it treatable without treating the cancer?"* |

Its seven routes were read individually: `RT-IPD-SURVIVAL`, `RT-SURGICAL-QUALITY`,
`RT-DIAGNOSTIC-PATHWAY`, `RT-SURVEILLANCE`, `RT-METASTASECTOMY`, `RT-RISK-MODEL`,
`RT-POPULATION-REGISTRY`. **Not one asks what the terminal event is.** ★ So S38 and S39's *"no
counterpart anywhere on the trunk"* survives contact with the family that most looked like one, and it
now survives it with the reading attached rather than as an assertion.

⭐ **Corroborated from `main`'s own artifacts, at $0:** `grep -c -i thromb` over
`research/data/emc-clinical-registry.json` on `origin/main` returns **0**; `grep -c -i palliativ`
returns **1**, and that one occurrence reads *"palliative use of systemic therapy in advanced
disease"* — an antitumour sentence. `git grep -l -iE 'ederer|relative survival|life[_ -]table'` over
`origin/main` returns **one** file, `research/literature/no-wet-lab-archetypes-2026-08-12.json`, and
no instrument. **The trunk holds no thrombosis content, no supportive-care content, and no
relative-survival machinery for this disease.**

### 2.2 · ⛔ THE DEFECT THAT DECIDES FOUR OF THE SEVEN: THE ROWS PREDATE THEIR OWN FAMILY'S FINDINGS

    $ git log -1 --format='%h %s' <branch> -- systems/graph/routes.json
    7b32ebe6f register mortality-mechanism-directed care as a strategy family, plus the host-factor model

That commit is **sixth from the tip**. The four commits that landed after it and before the paper are:

    4d61197b3 the retrieval corrects the headline: competing share 39.4% -> 21.7%, and the ceiling splits by stratum
    6728de886 close the background check: EMC patients die of other causes at the rate their age and sex predict
    e0e56c1b7 / e6b8fffe7  lung-probe / attribution-probe: Europe PMC citation index
    59bb15cbe the paper: what kills EMC patients, and the survival available to tumour-directed therapy

★ **So the graph rows are a snapshot of what the family believed on its first afternoon**, and the
branch spent the rest of that day refuting parts of it. **This is the same class of defect S39 refused
the atlas for — a row resting on a number its own programme has since corrected — except that here the
correction is on the branch itself rather than on the trunk.** The standard does not change with the
location of the correction.

### 2.3 · The rows, one line each

| row | verdict | the artifact that decides it |
|---|---|---|
| `ST-MORTALITY-MECHANISM` | **NEEDS-REGRADE** | Its own `state.running_job` — *"the mechanism-of-death probe and the competing-mortality decomposition"* — names two jobs that both finished on the branch, and its `next.best_next_action` (*"Read the retrieved terminal-event corpus and classify each quoted sentence"*) was executed: branch `research/manuscripts/emc-terminal-events-classified.json` classifies 52 patient-deaths. No counterpart on the trunk (§2.1). |
| `RT-COMPETING-MORTALITY` | **NEEDS-REGRADE** | Rationale states *"39.4% of deaths at ten years were not EMC deaths"*; branch commit `4d61197b3` moved the headline to **21.7 %** at ~3 y (30.8 % localised / 10.0 % metastatic) and the memo carries it as superseded-retained. `readiness.missing` says the background comparison is *"fetched but not yet folded in"*; branch `emc-mortality-decomposition.json` → `background_mortality_check.status` is **`"RUN"`**, with horizon-matched observed/expected ratios **0.97** (localised) and **1.04** (metastatic). |
| `RT-RESPIRATORY-FAILURE` | **NEEDS-REGRADE** | Rationale: *"The mechanism is asserted everywhere in the clinical prose and tabulated nowhere."* The branch tabulated it. `emc-terminal-events.json` → `deaths_by_label`: **`respiratory_failure` 3**, against **`mechanism_unstated` 28** of 52. The branch's own `PUB-MORTALITY-MECHANISM.what_it_would_claim` reads *"respiratory failure is not dominant"*. The route is still `maturity: "concept"` with `readiness.missing: []`. ⭐ The premise **failed**, and that is a result, not a reason to drop the row. |
| `RT-TREATMENT-HARM` | **RECOVER** | Every clause of its rationale verified against `origin/main` **today**: the registry's `drilon2008` cohort note reads *"13% metastatic at presentation; chemotherapy gave no objective responses (median PFS 5.2 mo)"*, and `systemicEvidenceCorrections.superseded[6]` on `main` independently re-attributes the 5.2 months to Drilon 2008 (PMID 18951519). Unretracted, uncorrected, no counterpart. Refresh `next` on entry — the count it asks for exists (2 `treatment_related` of 52). |
| `RT-VTE-PROPHYLAXIS` | **RECOVER** | `grep -c -i thromb` over `main`'s registry = **0**; over `main`'s whole graph, no route or modality covers it (`MOD-ANTICOAGULANT` is `not_applicable` for *"no antitumour claim to assess"*). The row is a question carrying its own most-likely negative — *"reducing events is not the same as prolonging life"* — and nothing on either ref refutes it. `maturity: concept`, `readiness: internal_note`, nothing run: the row says so, so it is accurate as written. |
| `RT-HOST-FACTOR` | **RECOVER** | No counterpart: every entry in `main`'s `outcomes.prognosticFactors` is a property of the tumour (size, grade, fusion partner, stage, site) or of its treatment (R0 resection); the one host property, *"Older age (e.g. > 60)"*, is not modifiable, which is this route's whole criterion. Its `readiness.missing` — *"the retrieved effect sizes and the bias assessment they have to be read through"* — is **accurate**: `emc_host_factor_model.py` declares `OUT = research/manuscripts/emc-host-factor-model.json` and that file is committed on **neither** ref. An honest row about unfinished work. |
| `RT-EARLY-PALLIATIVE` | **NEEDS-REGRADE** | Same structure as `RT-HOST-FACTOR` but the row is **not** honest about it: `readiness.missing` is `[]` while `emc_supportive_effect_transfer.py` declares `OUT = research/manuscripts/emc-supportive-effect-transfer.json`, committed on neither ref. The route's substance stands (`main` has no palliative-care content at all, §2.1); one field is measurably wrong. |

⛔ **A patch of the three RECOVER rows does not stand alone.** All six routes carry
`strategy: "ST-MORTALITY-MECHANISM"` (graded NEEDS-REGRADE) and
`publication.endpoint: "PUB-MORTALITY-MECHANISM"`, which is on the branch's `publications.json`
(29 entries) and **not** on `main`'s (32 entries; id list read and checked). Adding three routes alone
leaves two dangling references. The proposed patch records that dependency explicitly rather than
smuggling ungraded rows in beside the graded ones.

---

## 3 · THE FILES

### 3.1 · Added — the 32, one line each

**Manuscripts (2)**

| file | verdict | evidence |
|---|---|---|
| `research/manuscripts/emc-mortality-mechanisms.md` (3 952 w) | **RECOVER** | `canonical_for` all seven rows; no counterpart. ⭐ Handles its own correction the way rule 1.2 requires — *"The headline competing share was 39.4 % and is now 21.7 % at ~3 years / 30.8 % in the localised"*, with the old figure retained. |
| `research/manuscripts/emc-mortality-mechanisms-paper.md` (3 721 w) | **RECOVER** | The `PUB-MORTALITY-MECHANISM` document, `state: drafted`. Reports both stratified ceilings (6.7 pp localised, 31.0 pp metastatic) and the two-method convergence (23.0 % relative-survival median vs 21.7 % count-ratio). ⚠ `document.file` must be re-pathed — `main` moved manuscripts into subdirectories (§1.1). |

**Analysis scripts (5)** — all five run and all five are unmatched on `main`

| file | verdict | evidence |
|---|---|---|
| `emc_mortality_decomposition.py` (512 l) | **RECOVER, blocked until §4.1 lands** | Its provenance guard **fails against `main`'s registry today** — measured, §4.1. |
| `emc_relative_survival.py` (266 l) | **RECOVER** | Ederer II on published summary survival + a WHO GHO life table. `main` has **no** relative-survival machinery (§2.1). Complementary to `main`'s `research/modalities/emc_ipd_survival.py`, which reconstructs patient-level data from digitized curves and is blocked on `BLK-NO-CURATED-CLINICAL-DATA`; this method needs no curves. |
| `emc_terminal_events.py` (212 l) | **RECOVER** | Fails if a quoted sentence no longer matches the retrieval artifact verbatim. No counterpart. |
| `emc_host_factor_model.py` (276 l) | **RECOVER** | 15/15 of its tests pass. Output never produced (§2.3). |
| `emc_supportive_effect_transfer.py` (208 l) | **RECOVER** | 11/11 of its tests pass. Output never produced (§2.3). |

**Committed results (5)** — the ledger's "six JSON results" is **five**

`emc-mortality-decomposition-inputs.json`, `emc-mortality-decomposition.json`,
`emc-relative-survival.json`, `emc-terminal-events-classified.json`, `emc-terminal-events.json` —
**all RECOVER.** None has a counterpart on `main`; none rests on a trunk artifact that has since moved
(§4.1 is a *shape* change to the registry, not a figure correction — the disease-death counts
`9/134` and `9/29` are byte-identical on both refs).

**Test files (4)** — 70 tests, **all four RECOVER**, and two of them fail on `main` *by design*

| file | tests | on the branch's tree | on `main`'s |
|---|---|---|---|
| `test_emc_mortality_decomposition.py` | 19 | 19 pass | **18 pass, 1 fails** — §4.1 |
| `test_emc_host_factor_model.py` | 15 | 15 pass | 15 pass |
| `test_emc_supportive_effect_transfer.py` | 11 | 11 pass | 11 pass |
| `test_lit_mortality_probe.py` | 25 | 25 pass | **24 pass, 1 fails** — §4.2 |

⚠ **A real coverage gap, stated rather than left implicit:** `emc_relative_survival.py` and
`emc_terminal_events.py` have **no test file**. Two of the five analysis scripts are unguarded, and one
of them owns the paper's second, independent method.

**Probe scripts (5)**

| file | verdict | evidence |
|---|---|---|
| `scripts/lit_mortality_probe.py` (476 l) | **RECOVER** | Produced the corpus the family's headline finding rests on. Not on `main`. |
| `scripts/lit_host_factor_probe.py` (424 l) | **RECOVER** | 22 queries; no counterpart. |
| `scripts/lit_attribution_probe.py` (165 l) | **RECOVER** | 17 queries on how a cause of death is *assigned* at all — SEER classification, death-certificate accuracy, Pohar-Perme net survival. Nothing on `main` asks this, and every disease-specific survival figure in the registry inherits the answer. |
| `scripts/lit_lung_probe.py` (158 l) | **SUPERSEDED — salvage 7 queries** | §3.2. |
| `scripts/lit_probe_common.py` (114 l) | **OBSOLETE standalone; RECOVER as a dependency** | Its own docstring: *"IT DELIBERATELY DOES NOT TOUCH THE EXISTING FOUR."* Verified — `main`'s `lit_lane_probe.py` and `lit_consensus_probe.py` import only stdlib. It refactors nothing that exists; its only consumers are the three probes above. |

**Probe corpora (4)** — ⭑ and they are **measured runs, not scaffolds**

`emc-mortality-probe.json` (24 queries, all with hits), `emc-host-factor-probe.json` (22),
`emc-attribution-probe.json` (17) — **all RECOVER**; `emc-lung-probe.json` (16) — **SUPERSEDED**, §3.2.

⚠ Checked against §4's *"a populated field is not a measured one"*: the mortality corpus carries
`hitCount: 270` on its first query with real PMIDs, PMCIDs and DOIs, and a summary of
**600 open-access papers enumerated, 400 full texts attempted, 328 retrieved, 162 with a death
sentence, 577 death sentences** — quantities only a real retrieval produces. It also carries an
honest failure: `background_mortality.status: "FETCH_FAILED"` on the SSA life table, later closed
against WHO GHO in commit `6728de886`.

**Generated views (7)** — `L1-st-mortality-mechanism.md` and six `L2-rt-*.md`:
**OBSOLETE AS FILES, REGENERATE.** CLAUDE.md §7: everything under `systems/views/` is GENERATED and a
hand-edit fails the build. They are seven files but **one fact** — the graph rows — and they follow
whatever §2 lands.

### 3.2 · ⛔ THE ONE GENUINE SUPERSESSION, AND IT IS BY ONE DAY

`scripts/lit_lung_probe.py` + `research/literature/emc-lung-probe.json` were committed **2026-08-09**.
`main` carries `scripts/lit_rt_probe.py`, committed **2026-08-10** — *"rt probe: discriminate a zero
that may be a plural, not an absence"* — with **28 queries** including `emc_topic_metastasectomy`,
`sarcoma_lung_sbrt`, `emc_topic_thermal_ablation`, `emc_topic_oligometastatic`,
`emc_topic_natural_history` and `chondrosarcoma_radioresistance`; plus
`research/literature/rt-lung-mets-probe.json`, a findings artifact
`research/literature/emc-rt-lung-mets-findings.json` (*"ANSWER: YES — at least seven reported
deliveries"*), and a **route**, `RT-MDT-LUNG`, which the branch does not have.

★ **That is exactly block (A) of the lung probe — the TUMOUR-DIRECTED half — done better, one day
later, on the trunk.** ⚠ **But not block (B).** Seven queries have no counterpart anywhere on `main`:
`malignant_pleural_effusion_management`, `malignant_airway_obstruction_stent`,
`cancer_breathlessness_management`, `home_oxygen_niv_cancer`, `pulmonary_rehabilitation_cancer`,
`lymphangitic_carcinomatosis`, `pulmonary_embolism_cancer_lung_metastases`. The file's own header
warns that conflating the two blocks *"would let evidence for metastasectomy silently license a claim
about supportive care"* — so the split is already drawn and the salvage is mechanical.

⚠ **And the corpus records its own premise as unsettled** (`premise_status: "CONDITIONAL"`), which the
terminal-event classification then **refuted**: 3 respiratory deaths of 52 (§2.3). Recovering it
whole would import a retrieval commissioned on a premise its own family disproved.

### 3.3 · Modified — the 21 a path census cannot see

| file | verdict | evidence |
|---|---|---|
| `systems/graph/routes.json` (6 rows) | 3 RECOVER / 3 NEEDS-REGRADE | §2.3 |
| `systems/graph/strategies.json` (1 row) | NEEDS-REGRADE | §2.3 |
| `systems/graph/publications.json` (`PUB-MORTALITY-MECHANISM`) | **RECOVER as a dependency**, re-path `document.file` | Absent from `main`'s 32-entry id list; six routes point at it. |
| `systems/graph/modalities.json` | **RECOVER, conditional** | Flips `MOD-ANTICOAGULANT` `not_applicable` → `on_board` and rewrites `MOD-GLUCOCORTICOID`'s rationale, both citing routes by id. `main` still reads `not_applicable` / `excluded` (read this session). ⛔ Landing this **without** `RT-VTE-PROPHYLAXIS` writes a census verdict that cites a route that does not exist. |
| `research/data/emc-clinical-registry.json` | **RECOVER 6 KEYS ONLY — NEVER THE FILE** | §4.1 |
| `scripts/validate-registry.mjs` | **RECOVER** | §4.1 |
| `.github/workflows/fetch-literature.yml` | **RECOVER the wiring, by hand-merge** | §4.2 |
| `research/manuscripts/lint_style.py` | **RECOVER** (1 line) | Adds the paper to `TARGETS`. Only if the paper lands; a `TARGETS` entry for a missing file is a red gate. |
| `research/IDEAS.md` | **NEEDS-REGRADE** | The added row quotes **39.4 %** as the headline and says *"registered … with **five** routes"*. Both wrong by the branch's own later work: 21.7 % (`4d61197b3`) and **six** routes. |
| `research/manuscripts/emc-treatment-strategy.md` | **NEEDS-REGRADE** | +23 lines. `main` moved the file to `research/manuscripts/program/emc-treatment-strategy.md`; the addition needs re-pathing and its figures re-checking against §2.2. |
| 5 figure PDFs + `figures/figure-provenance.json` | **SUPERSEDED** | Commit `df6227cf9` restamped `nr4a3-fusion-targets-confounds.json` `b35a2ff7…` → `68774a2a…`. `main` restamped the same key to **`fd8e60e7…`** *and* moved `nr4a3-fusion-targets.json` `548dca5c…` → `0c338c16…`, which the branch did not. **The trunk is further along on the identical fix.** Unrelated to this family. |
| 5 generated views (`L0-ecosystem`, `L3-publications`, `modality-census`, `readiness`, `registers/blockers`) | **OBSOLETE AS FILES, REGENERATE** | Generated; follow §2. |

---

## 4 · ⛔⛔ TWO RECOVERY DEPENDENCIES THAT A PATH CENSUS IS BLIND TO, BOTH MEASURED BY RUNNING THE CODE

### 4.1 · The decomposition's own provenance guard FAILS against `main`'s registry — and it is a shape change, not a retraction

`emc-mortality-decomposition-inputs.json` declares its own supersession test in its `_readme`: *"the
script FAILS if that string is no longer present in the registry at the stated path, so a registry
correction cannot silently leave a stale figure in the decomposition."* **So the test S39 had to
construct by hand for the atlas already exists here. It was run.**

Nine `registry_verbatim` strings, checked against each ref's registry:

    MAIN    7 OK, 2 MISSING   (masunaga2025_localized, masunaga2025_metastatic)
    BRANCH  9 OK

Then the real thing, in a scratch tree built with `git archive` (**no checkout, no git write**), with
`main`'s registry swapped in:

    $ python3 -m pytest research/manuscripts/tests/test_emc_mortality_decomposition.py -q
    # branch registry (control):  19 passed
    # main registry:              1 failed, 18 passed
    FAILED ... ::test_the_real_inputs_still_resolve_against_the_real_registry
    E  assert ['masunaga2025_localized: registry_verbatim 'eight (6.3%) died from tumors,
       and four (3.1%) died from other causes' no ...'] == []

★ **AND THE CAUSE IS THE OPPOSITE OF THE ATLAS CASE — NOTHING WAS CORRECTED.** A structural diff of
the two registries gives **7 branch-only keys, 64 main-only keys, 12 changed values**. The branch-only
keys are:

    .registry.cohorts[0].otherCauseDeath.{events:4, denom:134} + otherCauseDeathNote
    .registry.cohorts[1].otherCauseDeath.{events:1, denom:29}  + otherCauseDeathNote

**The branch ADDED other-cause death counts that `main` never received.** `grep '"[a-zA-Z]*[Oo]ther[a-zA-Z]*"'`
over `main`'s registry returns **zero** matches — the trunk holds **no other-cause mortality data for
this disease at all**. Both cohorts are otherwise identical across refs, `diseaseDeath` included. The
guard fails because the quoted prose sentence was never carried to `main`, not because a figure moved.

⛔ **AND THE FIX HAS A SECOND HALF THAT MUST LAND IN THE SAME COMMIT.** Commit `4d61197b3` also
extended `scripts/validate-registry.mjs` — which is at the **merge-base sha on `main`, untouched
since** — to contract-check the new field:

```js
for (const k of ["recurrence", "metastasis", "diseaseDeath", "otherCauseDeath"]) { ... }
// ⛔ Disease deaths and other-cause deaths are disjoint by construction, so their sum
// cannot exceed the cohort. A pair that does proves one of the two was misread out of the
// source -- the exact failure mode of extracting counts from prose.
if (c.diseaseDeath && c.otherCauseDeath) { ...denom mismatch, ...events sum > denom }
```

★ **Recovering the registry fields without the validator adds an unvalidated field — the exact defect
CLAUDE.md §6 records for `subagent_width`: recorded is not enforced.**

⛔ **AND THE BRANCH'S REGISTRY MUST NOT BE TAKEN WHOLE.** The 64 main-only keys are three weeks of
trunk work the branch predates — the `palmerini2022trobsultrarare` trabectedin citation block and the
pembrolizumab n=1 case among them. **Six keys, by hand, plus the validator.**

### 4.2 · `main`'s literature workflow never invokes the probe

`test_lit_mortality_probe.py` carries `test_the_probe_is_actually_wired_into_the_fetch_literature_workflow`,
whose docstring says *"a value a caller passes is a hope, not a property"*. Run against each ref's
workflow file in the same scratch tree:

    branch .github/workflows/fetch-literature.yml -> 25 passed
    main   .github/workflows/fetch-literature.yml -> 1 failed, 24 passed
    E  AssertionError: the probe is never invoked
    E  assert 'scripts/lit_mortality_probe.py' in '...'

⚠ **`fetch-literature.yml` has moved on `main` since the merge-base**, so this is a hand-merge of the
slug guard, not a file take.

---

## 5 · COUNTS

**Graph rows (7):** RECOVER **3** · NEEDS-REGRADE **4** · SUPERSEDED **0**.

**Files (53 = 32 added + 21 modified), counting each path once:**

| verdict | n | what |
|---|---|---|
| **RECOVER** | **30** | 2 manuscripts, 5 analysis scripts, 5 results, 4 tests, 3 probe scripts + `lit_probe_common.py` as their dependency, 3 corpora, 3 RECOVER graph rows (1 path: `routes.json`), `publications.json`, `modalities.json`, the registry (6 keys), `validate-registry.mjs`, `fetch-literature.yml`, `lint_style.py` |
| **NEEDS-REGRADE** | **3** | `strategies.json`, `IDEAS.md`, `emc-treatment-strategy.md` |
| **SUPERSEDED** | **8** | `lit_lung_probe.py`, `emc-lung-probe.json`, 5 figure PDFs, `figure-provenance.json` |
| **OBSOLETE (regenerate)** | **12** | 7 added `systems/views/` + 5 modified `systems/views/` |
| **UNMEASURED** | **0** | — |

**The column sums to 53, which is the check: 30 + 3 + 8 + 12.** Split by side of the change set it is
`added 32 = 23 RECOVER + 2 SUPERSEDED + 7 OBSOLETE` and
`modified 21 = 7 RECOVER + 3 NEEDS-REGRADE + 6 SUPERSEDED + 5 OBSOLETE`.
⚠ **`routes.json` is one path carrying rows with two different verdicts** — three RECOVER and three
NEEDS-REGRADE — so it is counted once, under RECOVER, and §2.3 is the row-level truth. That is the only
place the file table and the row table can be read as disagreeing, and they do not.

**UNMEASURED = 0, and here is why that is a claim rather than a hope.** Every added file was opened;
every modified file was read as a merge-base-to-tip diff; the five binary PDFs were graded by blob-sha
comparison across three refs (`merge-base` / branch / `main`) rather than by opening them, which is
sufficient because `figure-provenance.json` records what they are stamped to and `main`'s stamp is
strictly further along. **Two verdicts that would otherwise have been predictions were measured by
executing the branch's own tests** (§4.1, §4.2).

---

## 6 · IS THIS FAMILY WORTH RECOVERING?

**Yes — and it is the strongest recovery case this sprint has produced, for a reason that is
structural rather than enthusiastic.** ⭐ Every other route on the board is blocked on EMC-specific
evidence nobody without a wet lab can obtain. This family's central result is **arithmetic on figures
`main`'s own registry already carries** — 9 disease deaths of 134 localised and 9 of 29 metastatic,
byte-identical on both refs — and it produces a number that **bounds every other route in the
portfolio**: preventing every EMC death adds 6.7 percentage points of survival in localised disease
and 31.0 in metastatic. That ceiling is a fact about the whole board, and the board does not currently
hold it.

⛔ **Three honest deductions, so this is not read as an unqualified yes.** (1) Two of the six routes
(`RT-HOST-FACTOR`, `RT-EARLY-PALLIATIVE`) have code, tests and a retrieval but **no committed result** —
they are scaffolding, and the ranker must not be told otherwise. (2) The organising empirical finding
is **negative and thin**: 28 of 52 classified deaths state no mechanism at all, and *"respiratory
failure is not dominant"* rests on 3 events. (3) Every supportive-care effect size available to the
family was measured in some other cancer; the family's own `limitations` says so.

★ **THE RECOVERY ACT IS NOT A MERGE AND IS NOT A CHERRY-PICK.** It is: six registry keys plus a
validator (§4.1), a workflow slug (§4.2), 23 added files taken as-is, one probe split in two, four
graph rows rewritten against evidence that already exists on the branch, and a regeneration. **A merge
would import a three-week-stale registry, a superseded figure stamp, and four route rows the branch
itself refuted.** ⛔ That is the S39 finding restated for this branch: *the recovery worth doing is
never the one the branch makes easy.*

---

## 7 · WHAT I WROTE, AND WHAT I DID NOT

**Written:** this memo, and `S43-proposed-graph-additions.json` — the three RECOVER rows verbatim from
the branch, with their unresolved references named.

**Not written, deliberately:** nothing under `systems/graph/` or `systems/views/`, no registry edit, no
merge, no cherry-pick, no branch. **No git command that touches the working tree, the index or a local
ref was run** — the verbs used were `rev-parse`, `merge-base`, `rev-list`, `log`, `show`, `diff`,
`ls-tree`, `cat-file`, `grep`, `status` and `archive`, plus one `git fetch origin --prune -q`, which
writes remote-tracking refs and nothing else. **The two test runs in §4 executed inside a scratch tree
built by `git archive`**, never in this checkout, because other seats are editing it concurrently. A family added to `routes.json` is a family the ranker starts
offering, and that is the driver's gated call.
