---
id: DOC-SPRINT-S38-BRANCH-CENSUS
title: "S38-BRANCH-CENSUS — 185 unmerged refs, not 38: forty carry live work, fifteen are CI infrastructure, and the instrument that first said everything was clear was wrong"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Read every stranded ref on origin and give each a verdict with the reading that supports it, so that
  branch drift stops being an unbounded data-loss risk carried as a hook warning nobody can act on.
scope: >
  Every ref returned by `git for-each-ref --no-merged=origin/main`, which is 185 rather than the 38 the
  merge-debt hook reports. Excludes this session's own HEAD branch and claude/s24-threshold-calibration,
  which the driver read separately and merges for content. Verdicts are per branch; a branch graded
  obsolete may still carry a single-ref file worth rescuing, and one did.
last_verified: 2026-09-02
---

# BRANCH CENSUS 2 — every stranded ref on `origin`, read and given a verdict

Written 2026-09-02, appended as each branch settled. Read-only throughout: no write command was
run against `/home/user/Rare-cancers` and no git write command of any kind was issued.

Enumeration was taken here, not from the prompt:

    git for-each-ref --format='%(refname:short) %(committerdate:short) %(objectname:short)' \
      refs/remotes/origin --no-merged=origin/main

**185 refs** (excluding `origin/HEAD`), not the 38 the Stop hook names. The hook's 38 is the
subset that still HAS a merge-base with `main`; the other 147 are invisible to an ancestry test
for the reason in §1 and were counted by the hook as neither merged nor stranded.

---

## §1 · THE STRUCTURAL FINDING THAT GOVERNS 147 OF THE 185 REFS

`origin/main` shares **zero commits** with those refs. Not "a distant merge-base" — zero.

    $ git merge-base origin/main origin/claude/max-effort-2dq11l ; echo $?
    1
    $ comm -12 <(git rev-list origin/main|sort) \
               <(git rev-list origin/claude/max-effort-2dq11l|sort) | wc -l
    0
    $ git rev-list --max-parents=0 origin/main
    ca00d750e5fc51152db0766976d626dd58e157a8      # a GRAFT, dated 2026-08-04, not a real root

`.git/shallow` carries 8 graft points, seven dated 2026-08-04 and one 2026-08-12. `main`'s
visible history begins at the graft, so every branch that forked before 2026-08-04 has its own
separately-fetched partial history sharing no object with it.

★ **This does NOT make those branches unreadable — only unclassifiable by ancestry.** A two-dot
TREE diff (`git diff origin/main <ref>`) needs no merge-base and compares content directly, which
is the question that actually matters. Every verdict below rests on a tree read, and the verdicts
that could not be settled that way are recorded as **D · UNMEASURED** rather than folded in.

---

## §2 · THE TWO CONTENT FAMILIES THAT ACCOUNT FOR ~95 PRE-GRAFT BRANCHES

Across the pre-graft branches the "present on branch, absent on `main`" set is nearly constant:
either ~18–36 files, or those plus ~1,455 more. Both sets were read, and both are **B · OBSOLETE**
against a NAMED retiring commit.

### 2a · The retired patient-facing site (~18–36 files, every pre-graft branch)

    index.html  404.html  assets/css/styles.css  assets/js/hub.js  assets/js/cancer.js
    cancers/emc/index.html  data/index.json  data/schema.json  templates/cancer-shell.html
    templates/cancer.template.json  scripts/new-cancer.mjs  scripts/smoke-render.mjs
    scripts/validate.mjs  .github/workflows/pages.yml  .claude/skills/add-cancer/SKILL.md

All eight probed are `ABSENT` on `origin/main`. CLAUDE.md §7 is explicit: *"THE PATIENT-FACING SITE
IS RETIRED AND DELETED (2026-08-05), NOT SHELVED. DO NOT RECREATE IT."* Accounting in
`systems/MIGRATION.md`. **A branch carrying these files is carrying the deleted site, and merging
it would recreate exactly what that rule forbids.**

### 2b · The manuscripts in that set are RENAMES, not losses

The A-lists also name `research/manuscripts/nr4a3-degrader-paper.md`,
`…-paper-SI.md`, `…-paper-redteam.md`, `…/nr4a3-emc-biology-evidence.md`,
`…/fusion-junction-aso-paper.md`, `…/emc-treatment-strategy.md`, `…/repurposing-hypotheses.md`
and others as absent from `main`. They are absent **at that path** and present one directory
down — `main` foldered the manuscripts by programme:

    research/manuscripts/degrader/nr4a3-degrader-paper.md
    research/manuscripts/degrader/nr4a3-degrader-paper-SI.md
    research/manuscripts/degrader/nr4a3-degrader-paper-redteam.md
    research/manuscripts/degrader/nr4a3-emc-biology-evidence.md
    research/manuscripts/aso/fusion-junction-aso-paper-redteam.md
    research/manuscripts/program/emc-treatment-strategy.md

⛔ So the A-count OVERSTATES loss on every pre-graft branch, and a reader treating "absent from
`main`" as "would be lost" would wrongly promote ~95 branches to C.

### 2c · The extra ~1,455 files are SageMaker profiler telemetry, dropped on purpose

On ~95 branches the A-set additionally contains `results/nr4a3-metad-r{1,2,3}/…` and
`results/nr4a3-8xtt-redock/…`. File-type census of the branch copy:

    483 × <epoch>.algo-1.json      profiler-output/system/incremental/…
      1 × MANIFEST.json  COLVAR  HILLS  fes.dat  AF-Q92570.pdb

129.9 MB over 489 files for r1 alone. `main` keeps 6 files there. The retiring commit is named:

    4bacf7a2d  2026-08-05  "§H: green the remaining five, and drop 383 MB that was never evidence"
               body: "results/ — 551 MB → 168 MB"

★ **And the science payload survived byte-identical** — this was checked by blob sha, not by
inspection:

    MANIFEST.json   IDENTICAL      COLVAR   IDENTICAL      HILLS   IDENTICAL
    fes.dat         IDENTICAL      AF-Q92570.pdb          IDENTICAL

**Verdict for the family: B · OBSOLETE.** The only branch-exclusive content is profiler telemetry
that a named commit deleted as "never evidence", plus the deleted site. Nothing scientific is
branch-exclusive.

---

## §3 · THE HIGHEST-RISK CATEGORY — FILES THAT EXIST ON EXACTLY ONE REF

After subtracting the retired site, the profiler telemetry and the renamed manuscripts, **150 paths
remain that are absent from `origin/main`.** Each was then checked against **all 302 refs** on
`origin`, not just `main`:

    while read r; do git ls-tree -r --name-only "$r" | grep -Fx -f absent.txt | sed "s|^|$r\t|"; done < allrefs.txt

**123 of them are carried by exactly ONE ref.** That is the shape that loses work permanently, and
it concentrates into ten branches. All ten are **C · WORTH KEEPING**.

### C-1 · `origin/claude/emc-research-strategy-kdz9kn` — 38 single-ref paths ⚠ THE SERIOUS ONE

**What would be lost: the entire EMC Open Target & Drug Atlas — 39 files under `research/atlas/`
(23 curated atomic claims, 32 graded sources, 10 scored therapeutic axes, five `dist/*.tsv`
deposit tables, five analysis scripts, a METHODS/REPRODUCIBILITY/DEPOSIT set, a collaborator brief
and a plain-language overview) plus the `atlas-data.yml` (does not exist in this checkout) workflow that regenerates it.**

⛔ **`main` has no `research/atlas` path at all**, and this is not a rename — every distinctive
basename was probed individually and returns 0 on `main`:

    emc_evidence_score.tsv 0   antigen-expanded.json 0   panel_exposure.py 0
    collaborator-brief.md  0   lineage-antigen-program.md 0  build.mjs 0
    samples.json 0   drug_screens.json 0   overview-plain-language.md 0
    antiangiogenic-mechanism.md 0

⛔⛔ **AND `STRATEGY.md` ON `main` TODAY STILL POINTS AT IT.** Line 156, live text, not an
appendix entry:

> **Atlas-anchor reframe** … the **EMC Open Target & Drug Atlas** (`research/atlas/`…) … The atlas
> *work* stays valuable as **support** — biological rationale, fusion-vs-WT biology, anti-target
> liabilities, an assay roadmap for collaborators, and the **backup route if degrader design
> fails** … Its own state: `research/atlas/README.md` + `STATUS.md`

Those two files do not exist on `main`. So a live strategy document cites, as still-valuable and
as the degrader programme's named backup route, a subtree that survives on one branch and nowhere
else. ⚠ Line 161 of the same file records the branch as *"Resolved — merged and reconciled to
degrader-primary"* — **that note is true about the framing decision and false as a statement about
the files.** The deletion is not visible in `main`'s history because it predates the 2026-08-04
graft (`git log --diff-filter=D origin/main -- 'research/atlas/*'` is empty).

⛔ **Do not merge this branch to recover it** — it also carries the retired patient-facing site
(§2a). Recovering the atlas means taking `research/atlas/**` and `.github/workflows/atlas-data.yml`
as a path-scoped extraction, nothing else.

### C-2 · `origin/claude/add-skill-my44c1` — 44 single-ref paths

**What would be lost: the `building-an-exo` skill in full (35 files — SKILL.md, schema.json, 15
reference notes, 12 templates, 8 decision-trace JSONL logs dated 2026-05-22 to 2026-06-22), two
governance linters (`scripts/govern-overclaim-lint.mjs`, `scripts/decision-trace.mjs`), the
`research/degrader/decision-traces.jsonl` log they write, and six manuscripts that exist on no
other ref: `degrader-grant-draft.md`, `degrader-moat-decision-traces.md`, `degrader-mtp-protocol.md`,
`degrader-startup-plan-exo.md`, `degrader-task-decomposition-matrix.md`, `govern-assure-eval.md`.**

`.claude/skills/building-an-exo/SKILL.md` returns exactly 1 carrying ref out of 302.

### C-3 · `origin/replicate-standard-cache` — 17 single-ref paths

**What would be lost: the raw harvest behind the replicate-standard reading —
`research/modalities/_replicate_standard/` with `harvest-summary.json`, `harvest.log`,
`keyword-context.json` and 13 `raw/*.txt` source captures (OpenFE protocol docs, the Cinnabar
FE-map/README/stats, `ross2023_nature.txt`, `mey2020_arxiv_abs.txt`).** These are the primary
sources a replicate-count or field-standard claim rests on; the derived claim may be on `main`,
the evidence it was read from is on this branch alone.

### C-4 · `origin/claude/nr4a1-protac-positive-control-xnszjl` — 5 single-ref paths

**What would be lost: the paralogue site-correction analysis — `paralogue_site_correction.py` (does not exist in this checkout), its
result `paralogue-site-correction.json`, its unit test `tests/test_paralogue_site_correction.py`,
the `paralogue-site-correction.yml` (does not exist in this checkout) workflow, and `apo-pose-regime-dock.json`.** Code, result,
test and CI wiring for one analysis, all four on one ref.

### C-5 · `origin/claude/nr4a3-structure-update-i0pgpx` — 4 single-ref paths

**What would be lost: the 8XTT cross-check job in full — `nr4a3_xtt_crosscheck.py` (does not exist in this checkout), its SageMaker
driver `nr4a3_xtt_crosscheck_sagemaker.py` (does not exist in this checkout), the container entrypoint
`sagemaker_src/entry_xtt_crosscheck.py`, and `report-xtt-crosscheck-aws.yml` (does not exist in this checkout).**

### C-6 · `origin/claude/rare-disease-grants-4pyyvc` — 2 single-ref paths

**What would be lost: `research/grants/anthropic-rare-disease-grant-application.md` and
`research/grants/ai-credits-strategy-deep-dive.md`.** `main` has no `research/grants/` directory.
⚠ This one bears on funding rather than science, and it is outward-facing text — worth trimcrae
seeing before it is dropped.

### C-7 · `origin/claude/cofold-image-bake` — 2 single-ref paths

**What would be lost: `research/compute/Dockerfile.selcalcofold` and
`.github/workflows/selcal-cofold-bake.yml` — the recipe for a baked cofold image.** ⚠ CLAUDE.md §6
forbids building an environment on a paid machine and says the first question is *"which baked
image?"* — this is the definition of one of those images.

### C-8 · four single-file branches

| ref | the one file that exists nowhere else |
|---|---|
| `origin/litverify-tmp` | `scripts/litverify_fetch.py` |
| `origin/vast-blacklist-retest` | `research/modalities/vast-exclusion-census.json` |
| `origin/claude/nr4a3-fusion-degrader-efidn1` | `research/modalities/fusion-cofold-result.json` |
| `origin/claude/max-effort-2dq11l-cofold` | `research/modalities/nrv04-covalent-adduct-build.json` |
| `origin/claude/max-effort-2dq11l-anchor` | `research/modalities/nr4a3-orientation-basins-native-12pose.json` |
| `origin/claude/gcp-gpu-quota-increase-61pnzu` | `.github/workflows/gcp-billing-history.yml` |
| `origin/claude/azure-l4s-setup-y856cz` | `.github/workflows/azure-quota-check.yml` |
| `origin/rbfe-split-cache` | `_splitshake/analysis_raw_shared_solvent.json`, `_splitshake/leg_shared_solvent.json` |
| `origin/rbfe-introspect-cache` | `_introspect/introspect_report.txt`, `_introspect/openfe_unit_source.txt` |

⚠ The three `research/modalities/*.json` result files are **computed results with a real GPU cost
behind them**, held on one ref each.

### The one absent path that is NOT high-risk

`research/manuscripts/fusion-junction-aso-paper.md` is on **174 refs** and not on `main`. It is the
9,967-word predecessor of the PUB-ASO paper; `main` carries the 4,695-word successor as
`research/manuscripts/aso/fusion-junction-aso-journal-article.md` under a different title, with
eleven red-team rounds, a cover letter and built PDF/DOCX beside it. **B · superseded.**

---

## §4 · THE 38 BRANCHES THAT STILL HAVE A MERGE-BASE (the Stop hook's set)

38 refs, **182 commits ahead of `origin/main`** — the hook says 169, and the gap is that this
census was taken after nine `-s ours` supersession merges were made locally but before they reached
`origin`.

### 4a · A BUG IN MY OWN FIRST INSTRUMENT, AND WHAT IT WAS HIDING

The first pass reported **`MAIN-MISSING = 0` for all 38** — no branch adds a file `main` lacks.
That was wrong, and the failure was silent:

    $ git rev-parse origin/main:scripts/lit_batch_probe.py
    fatal: path 'scripts/lit_batch_probe.py' does not exist in 'origin/main'   # stderr
    origin/main:scripts/lit_batch_probe.py                                     # STDOUT, exit 128

`git rev-parse` **echoes the unresolved path to stdout on failure**, so
`$(git rev-parse … 2>/dev/null || echo MISSING)` captured `"<path>\nMISSING"`, which equals neither
`MISSING` nor the branch blob — every absent file was silently graded `DIFFERS`. It surfaced only
because a two-dot diff showed `new file mode` for a path the rollup called present.

Re-run with `git cat-file -e` and an explicit exit test, the true figure is **138 files that a
merge-base branch has and `main` does not.** ⚠ Recorded here because the optimistic reading was
produced by an instrument, not by a guess, and it would have cleared every one of these branches.

### 4b · Then the rename test, applied to all 138

24 are renames into `main`'s foldered manuscript tree (`research/manuscripts/mtap-prmt5/`,
`/surface-targets/`, `/fusion-output/`, `/dependency/`, `/repurposing/`, `/program/`), and the
`_s4_lane_inputs/GSM*.soft.txt` set is on `main` gzipped. **114 are on no path of `main` at all.**

### 4c · C · WORTH KEEPING — the merge-base branches, largest first

#### C-9 · `origin/claude/best-paper-submission-tqa0cn` (20 commits, 46 paths on no path of `main`)

**What would be lost: the entire 2026-08-10 peer-review round for five papers, plus the MTAP/PRMT5
computational programme.** Named: ten `*-peer-review-2026-08-10.md` / `*-review-response-2026-08-10.md`
files across the ATR collaborator package, the MTAP-PRMT5 hypothesis, the surface-target landscape,
the fusion-transcriptional-output paper and repurposing-hypotheses; the five `emc-mtap-prmt5-decline-review-*`
seat reports (biology, editor, integrity, statistics, response); six analysis scripts with their JSON
results (`emc_prmt5_effect_sizes.py` (does not exist in this checkout), `emc_prmt5_multiplicity.py`, `emc_mtap_locus_persample.py`,
`emc_tissue_read_statistics.py` (does not exist in this checkout), `emc_fet_frame_and_composition.py`, `emc_prior_art_fulltext_screen.py`),
`research/hypotheses/txgnn_exact_match_reanalysis.py` + its JSON, three tests, five literature
screens, and **six figure files** (`emc-fusion-frame-fig1.png/.pdf`, `emc-surface-fig1-transfer.png/.pdf`
and two `*-figure-provenance.json`).
⚠ The *manuscripts* on this branch are NOT lost — all twelve are on `main` under folder paths, with
`main`'s copies further developed. It is the **review round, the figures and the computed evidence**
that are branch-only. Probed individually: `emc_prmt5_effect_sizes.py` (does not exist in this checkout), `emc-surface-fig1-transfer.png`,
`txgnn_exact_match_reanalysis.py` (does not exist in this checkout) and `emc-mtap-prmt5-hypothesis-peer-review-2026-08-10.md` each
return **1 carrying ref of 302**.

#### C-10 · `origin/claude/emc-symptom-treatment-742257` (13 commits, 32 paths on no path of `main`)

**What would be lost: a whole strategy family — EMC mortality mechanisms — that is absent from the
architecture graph `main` calls its source of truth.** `main`'s `systems/graph/routes.json`
contains none of `ST-MORTALITY-MECHANISM`, `RT-COMPETING-MORTALITY`, `RT-EARLY-PALLIATIVE`,
`RT-HOST-FACTOR`, `RT-RESPIRATORY-FAILURE`, `RT-TREATMENT-HARM`, `RT-VTE-PROPHYLAXIS`; the branch's
copy contains all seven.

    $ git show origin/main:systems/graph/routes.json | grep -oE '"(RT|ST)-…(MORTALITY|PALLIATIVE|…)…"'
    (no output)
    $ git show origin/claude/emc-symptom-treatment-742257:systems/graph/routes.json | (same)
    "RT-COMPETING-MORTALITY" "RT-EARLY-PALLIATIVE" "RT-HOST-FACTOR" "RT-RESPIRATORY-FAILURE"
    "RT-TREATMENT-HARM" "RT-VTE-PROPHYLAXIS" "ST-MORTALITY-MECHANISM"

With them: two manuscripts (`emc-mortality-mechanisms.md`, `emc-mortality-mechanisms-paper.md`),
five analysis scripts (`emc_mortality_decomposition.py` (does not exist in this checkout), `emc_relative_survival.py`,
`emc_terminal_events.py` (does not exist in this checkout), `emc_host_factor_model.py`, `emc_supportive_effect_transfer.py`), their
six JSON results, four tests, five literature probe scripts and four probe corpora, and the seven
generated `systems/views/L1-st-mortality-mechanism.md` / `L2-rt-*.md`.
★ **The views are regenerable — but only from graph rows that are themselves branch-only**, so this
is not "seven generated files", it is one strategy family. Probed: `emc-mortality-mechanisms-paper.md`
and `emc_mortality_decomposition.py` (does not exist in this checkout) each return **1 carrying ref of 302**.
⚠ Under CLAUDE.md §5 this is a *live* route family (supportive/mortality care for EMC), not a
finished negative.

#### C-11 · `origin/claude/preprint-host-unaffiliated-srzofd` (12 commits, 7 paths on no path of `main`)

**What would be lost: the record and the built artifacts of the ASO preprint's Research Square
submission of 2026-08-21** — `fusion-junction-aso-research-article.pdf`,
`…-research-article-manuscript.pdf`, `…-supplementary-information.pdf`, their two build-stamps, and
the two host-policy fetchers `scripts/preprint_host_policy_fetch.py` and `scripts/arxiv_route_fetch.py`
(arXiv endorsement/format/category rules and a q-bio endorser search).
⛔ This concerns **PUB-ASO**, the one paper CLAUDE.md §3 excludes from the standing publication
grant. A submission record for it is exactly the class of artifact that must not be dropped
silently.

#### C-12 · `origin/claude/aws-budget-storage-shutdown-iq8oh7` (22 commits, 7 paths on no path of `main`)

**What would be lost: the AWS spend shutdown in full — `research/compute/aws-account-state.md` plus
`aws_spend_census.py` (does not exist in this checkout) / `aws_spend_probe.py` / `aws_spend_shutdown.py` and their three JSON
results.** The log records applied actions (`s3_purge`, `ecr_lifecycle_expire`, `log_delete`), a
corrected object count, a verified-empty bucket, and *"retire the crons the S3 purge silently
armed"*. ⚠ This is the evidence that a paid account was actually shut down and that nothing is
still billing at rest — a money record, and the only copy.

#### C-13 · `origin/claude/gcc-nat-emc-aso-aq0eba` (20 commits, 4 paths on no path of `main`)

**What would be lost: the venue fee screen — `research/manuscripts/venue_fee_screen.py` and
`aso/venue-fee-screen.json`, plus `aso/gcc-scope-census.json` and `aso/aso-design-only-census.json`.**
Which shape-publishing journals have a no-fee route, computed against OpenAlex with the
journal-identity bug fixed in the tip commit. Bears directly on where a paper can be submitted.

#### C-14 · single-file and small merge-base branches

| ref | on no path of `main`, and on 1 ref of 302 |
|---|---|
| `origin/agent/fusion-frame-trap-fetch` | `research/modalities/fusion_frame_trap.py` + `fusion-frame-trap-breakpoints.json` — Ensembl batch POST, 7 calls instead of 314 |
| `origin/claude/orphaned-fusion-junction-catalog-0jgizz` | `research/modalities/fusion-junction-orphan-census.json` — *"the two items held back from main when the catalog route was parked"* |
| `origin/claude/proximity-lit-sweep-7rydac` | `.github/workflows/fetch-literature-iso.yml`, `scripts/lit_batch_probe.py` |
| `origin/claude/lit-probe-immuno-architectures` | `scripts/lit_batch_probe.py` (its own version; `lit_probe_queries.json` is already identical on `main`) |
| `origin/claude/aut071-s1-CYC-0074` | `research/literature/trabectedin-emc-clinical-2026-08-29.json` — ⚠ `main` has trabectedin views and a *different* denominator corpus dated 2026-09-01 |
| `origin/seat/s3-unscreened-endpoints` | `test_every_publication_endpoint_is_style_screened_or_recorded.py` (does not exist in this checkout) — ⚠ `main` has a differently-named sibling, `test_the_census_reads_every_publication_endpoint.py` |
| `origin/lit-iso-wf` / `origin/claude/frontier-capability-sweep-r3-2026-08-07` | `research/manuscripts/lit-targets-frontier-capability-r3-2026-08-07.json` |
| `origin/cyc0073-d4ccfde4-work` | `research/autonomy/receipts/CYC-0073-d4ccfde4.json` — ⚠ `main` has `autonomy/receipts/CYC-0073-d4ccfde4.json` (no `research/` prefix) with DIFFERENT content; one of the two is misfiled |

### 4d · ⚠ A CORRECTION TO ONE OF TONIGHT'S NINE DISCHARGED VERDICTS

`origin/claude/aut-pd-145-s2-CYC-0074` was cleared as **OBSOLETE**, and as a statement about the
DEFECT that is correct — the unscored population reached 0, so "may the ceiling be pinned yet?"
stopped being a question. **But the branch carries `research/autonomy/unscored_ratchet.py`, which
exists on 1 ref of 302 and on no path of `main`**, and its docstring records a measured finding that
is not written down anywhere else:

> the plain ancestry range over the same window returned 17 commits and oscillated 84 → 85 → 84 → 85
> inside four minutes, while `--first-parent` returned 6 and was monotone … a commit that lived on a
> side branch carries a ledger missing every OTHER branch's rows, so its count is the population of a
> state the trunk never had.

Deleting the branch deletes that. **Extract the file before the deletion; do not re-litigate the
verdict.** Same shape, lower stakes: `aut-pd-148-s5`'s
`test_a_quantity_written_in_words_is_counted_not_perturbed.py` (does not exist in this checkout) is single-ref, and `main` carries a
differently-named sibling `…_can_be_perturbed.py` — consistent with the recorded "closed by a
different, better route", worth one diff before deletion.

### 4e · A · SUPERSEDED BY CONTENT, and B · EMPTY/OBSOLETE

| ref | verdict | evidence |
|---|---|---|
| `origin/worktree-agent-a8e9ae2f991db8def` | **B · EMPTY** | 1 commit, `git show --name-only` lists no file; three-dot diff empty |
| `origin/ci-input/tcip-interface-floor-2026-08-07` | **A** | all 4 files byte-identical to `main` (blob sha) |
| `origin/claude/elink-probe-ci-fefnhh` | **A** | both files byte-identical to `main` |
| `origin/claude/tcip-effector-stage-ci` | **A** | 4 identical; 183/183 added lines present in `main`'s copies (100 %) |
| `origin/claude/aso-e13-tissue-expression` | **A** | 3 identical; 5/5 added lines present (100 %) |
| `origin/worktree-agent-ab0b548a575724822` | **A** | 157/158 added lines present (99 %) |
| `origin/aut-pd-036-ls-files-scope` | **A** | 47/47 (100 %) — agrees with the prior verdict |
| `origin/aut-pd-058-deepen-ledger-history` | **A** | 328/329 (99 %) — agrees |
| `origin/s3/aut-pd-031-…-enumerate-carriers` | **A** | 313/316 (99 %) — agrees |
| `origin/aut-pd-037-ledger-serialization` | **A** | 48/49 (97 %) — agrees |
| `origin/claude/s76-sgk1` | **A** | 28/29 (96 %) — agrees |
| `origin/s1-aut-pd-050-unscored-rows` | **A** | 313/325 (96 %) — agrees |
| `origin/aut-pd-052-ci-autonomy-tests` | **A** | 12/13 (92 %) — agrees |
| `origin/claude/ci-a3b5-lanes` | **A/B** | 9 files identical; the only `main`-absent paths are 4 `GSM*.soft.txt` that `main` holds **gzipped** |
| `origin/claude/nr4a3-gapmer-presubmission-d4vqmp` | **A** | 37 files differ but every one is a PDF/DOCX/build-stamp `main` has rebuilt since; sole absent path `aso/claim-coverage.json` is `main`'s `research/manuscripts/claim-coverage.json` |
| `origin/seat/s5-retest-blocks`, `origin/seat/s4-aut-045`, `origin/seat/s1-aut-pd-130`, `origin/claude/aut-pd-130-s4-CYC-0074`, `origin/claude/aut-pd-147-s3-CYC-0074` | **A** | no `main`-absent path; 13–82 % line absorption with the remainder being ledger/JSON reserialization |

### 4f · Not judged here, by instruction

`origin/claude/s24-threshold-calibration` — already read by the driver and being merged for content.
`origin/claude/max-token-usage-sprint-cwihvo` — **this is the session's own working branch**
(`HEAD` = `f1d3621fe` = the ref's tip), not a stranded branch. Its three `main`-absent paths are
tonight's live work.

---

## §5 · THE 147 PRE-GRAFT REFS, MEASURED RATHER THAN LEFT UNMEASURED

§1 said ancestry against `main` is unusable here. It does **not** follow that these branches cannot
be dated: **pre-graft branches share merge-bases with each other**, because each carries its own
un-truncated copy of the pre-graft trunk.

    $ git merge-base origin/claude/max-effort-2dq11l origin/claude/rare-disease-grants-4pyyvc
    facd0aebf  2026-07-20  "credit-status: refresh free-credit burn board"

So a **fork point** is recoverable as the newest merge-base against a panel of sibling branches
(a lower bound on the true fork), and `diff <fork>...<branch>` is then the branch's OWN change.
That converts most of the would-be UNMEASURED set into real readings.

### 5a · 94 of the 136 pre-graft *code* branches are fully contained in a sibling

`git merge-base --is-ancestor <branch> <sibling>` is TRUE for **94** of them — their tip is a commit
already inside a longer branch, so they hold nothing that branch does not. 71 of the 109 later ones
resolve into `claude/max-effort-2dq11l`, `claude/trigger-e3-recruiter-grade`,
`worktree-agent-a1050d046c87837d4` and `claude/gcp-l4-selffeed`; 23 of the 27 earlier (June–July,
when the repo was 120–430 files) resolve into `claude/max-effort-2dq11l`.

**B · SUBSUMED** for all 94. Combined with §2 — their only `main`-absent files are the retired site
and the profiler telemetry — nothing is lost by dropping them, and the containing branch is named
for each.

### 5b · The branches with their own tip, absorbed into `main`

Measured as in §4: added lines from the branch's own diff, looked for in `main`'s copy of the file.

| ref | own added lines | present in `main` | verdict |
|---|---|---|---|
| `origin/claude/nrv04-secondaries-e2e3e4` | 1215 | 1192 (98 %) | **A** |
| `origin/fix/ternary-vast-deaths` | 855 | 842 (98 %) | **A** |
| `origin/claude/degrader-8xtt-scripts` | 781 | 758 (97 %) | **A** |
| `origin/claude/retro-smoke-forensics` | 512 | 503 (98 %) | **A** |
| `origin/vast-blacklist-retest` | 406 | 402 (99 %) | **A** (bar one file, below) |
| `origin/claude/abfe-selectivity-pricing` | 400 | 399 (99 %) | **A** |
| `origin/claude/arrival-provenance-warning` | 326 | 316 (96 %) | **A** |
| `origin/tvast-marker-recency` | 181 | 175 (96 %) | **A** |
| `origin/claude/trigger-e3-recruiter-grade` | 3906 (60-file sample) | 3597 (92 %) | **A** — its 44 "absent" paths are every one a rename into `main`'s foldered manuscript tree, checked individually |
| `origin/claude/retro-price-ledger-forensics` | 994 | 759 (76 %) | **A**, residue is `STRATEGY.md` prose `main` rewrote |

### 5c · ⚠ C · pre-graft branches whose own work did NOT reach `main`

Low absorption on a `.md` manuscript usually means `main` rewrote the prose, not that work was lost.
Low absorption on **code, a workflow or a JSON result** does not have that excuse. These are the
ones where it is code:

| ref | absorbed | what is unabsorbed |
|---|---|---|
| `origin/claude/oracle-cloud-gpu-credits-focnql` | 15/289 (5 %) | `research/compute/cheap-gpu-plan.md`, `research/modalities/gpu_backend.py` + its test — a provider backend `main`'s copy does not contain |
| `origin/claude/azure-l4s-setup-y856cz` | 5/87 (5 %) | same two files, Azure path, **plus** `.github/workflows/azure-quota-check.yml` which is on no other ref |
| `origin/claude/gpu-molecular-dynamics-selection-pvybay` | 0/102 (0 %) | `research/compute/md-throughput-optimizations.md` — 102 lines `main`'s copy lacks |
| `origin/claude/max-effort-3hgq45` | 0/34 (0 %) | `research/modalities/ternary-lane-guard-audit-2026-07-25.md`, `ternary-watch.json` |
| `origin/claude/val-b-openfe-ternary-bvfhjy` | 0/26 (0 %) | `STRATEGY.md` only — ⚠ prose, so this one is weak evidence |
| `origin/claude/protac-paper-daily-email-6yjb6r` | 14/61 (22 %) | `research/modalities/daily-email-system.md` |
| `origin/claude/degrader-fep-diagnostics` | 9/22 (40 %) | `research/modalities/_reports_abfe_diag.txt` |
| `origin/wip/lane-snapshot-latest` | 40/216 (18 %) | `ternary_vast_launch.py` (does not exist in this checkout), `tests/test_ternary_ckpt_exposure.py` |
| `origin/wip/lane-snapshot-2026-07-27-1455et` | 161/274 (58 %) | `fleet_supervision_alarm.py` (does not exist in this checkout) + test, `step1-fanout-autoscale.yml`, `fleet-supervision-alarm.yml` |

**Two more C branches surfaced only at this stage**, both single-ref and both absent from `main` by
path *and* by basename:

- **`origin/claude/degrader-paper-graphic-yomcbt`** — **what would be lost: the degrader paper's
  plain-language explainer slide**, `research/manuscripts/nr4a3-degrader-explainer.html` / `.pdf` /
  `.png`, built over three commits ("Reframe degrader explainer around the research pipeline
  steps"). `nr4a3-degrader-explainer.html` and `.png` each return **1 carrying ref of 302**;
  `main` has no file of that basename. ⚠ Public-explanation work for a paper that is still live.
- **`origin/claude/degrader-de-novo-design-8qhk6t`** — **what would be lost:
  `research/modalities/denovo_select.py`, its test `tests/test_denovo_select.py`,
  `nr4a3-denovo-result.md` and `.github/workflows/denovo-screen.yml`**, each on 1 ref of 302.
  ⚠ Weakest of the C set: `main` carries a *superseding* de-novo toolchain (`denovo_blueprint.py` (does not exist in this checkout),
  `denovo_funnel.py` (does not exist in this checkout), `denovo_library.py`, `nr4a3_denovo.py`) and two `results/nr4a3-denovo*`
  directories, so this is plausibly a precursor. **It is called C anyway** — one diff would settle
  it and none has been done.

### 5d · ⛔⛔ THE ELEVEN CACHE BRANCHES ARE LIVE INFRASTRUCTURE, NOT STRANDED WORK

`literature-cache`, `modalities-cache`, `method-watch-cache`, `preprint-cache`, `txgnn-cache`,
`enumeration-cache`, `vaccine-calibration-cache`, `deepternary-qualify-cache`, `figure-renders`,
`litverify-cache`, `lane13-watch` (and `email-outbox`, `field-scan-log`,
`replicate-standard-cache`, `rbfe-split-cache`, `rbfe-introspect-cache`) are **orphan data branches
with unrelated history**, and `main`'s own workflows write to them:

    literature-cache            187 references on main   .github/workflows/fetch-literature.yml, enumerate-drugs.yml
    modalities-cache             61                      abfe-plot-aws.yml, aso-breakpoint-scan.yml, …
    method-watch-cache           12                      method-watch.yml
    email-outbox                 10                      daily-degrader-email.yml, method-watch.yml
    field-scan-log               11
    deepternary-qualify-cache     5                      deepternary-qualify.yml, -blind-controls.yml, -inspect-io.yml
    figure-renders                4                      render-figures.yml
    replicate-standard-cache      3                      replicate-standard-harvest.yml
    enumeration-cache             3                      enumerate-drugs.yml
    txgnn-cache / rbfe-introspect-cache / vaccine-calibration-cache  2 each
    preprint-cache / rbfe-split-cache / lane13-watch                 1 each

⛔ **`origin/literature-cache` holds 70,992 fetched full texts across 316 slugs with ZERO overlap
with `main`'s 78 literature files** — `comm -12` on the slug lists returns 0, and
`inhaled-oligonucleotide-delivery` (16,788 files) appears nowhere on `main`. It is still receiving
commits (332 total, latest 2026-08-30), as are `modalities-cache` (401 commits, 2026-09-01) and
`vaccine-calibration-cache` (2026-09-01).

★ **These branches are not debt and must not be deleted or merged.** They are how this repository
gets data past the egress proxy. A hook that counts them as "unmerged commits" is measuring the
design, not a problem — worth fixing in the hook rather than in the branches. `litverify-cache` is
the one with **0** references on `main` and is the only plausible retirement candidate among them.


---

## §6 · THE TABLE — every one of the 185 stranded refs

`A` superseded by content · `B` empty/obsolete/subsumed · `C` worth keeping · `C-INFRA` live
cache branch, never delete · `D` cannot be judged · `—` excluded by instruction.

| ref | date | verdict | one-line evidence |
|---|---|---|---|
| `agent/fusion-frame-trap-fetch` | 2026-08-10 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `aut-pd-036-ls-files-scope` | 2026-08-28 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `aut-pd-037-ledger-serialization` | 2026-08-28 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `aut-pd-052-ci-autonomy-tests` | 2026-08-28 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `aut-pd-058-deepen-ledger-history` | 2026-08-28 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `charge-provenance-audit` | 2026-07-29 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `ci-input/tcip-interface-floor-2026-08-07` | 2026-08-07 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/abfe-nan-recovery` | 2026-07-08 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/abfe-selectivity-pricing` | 2026-08-02 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/account-orphan-alarm` | 2026-08-01 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/account-reaper` | 2026-08-01 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/add-skill-my44c1` | 2026-07-19 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/ai-research-gpu-funding-aa1ydr` | 2026-07-22 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/alternative-gpu-providers-wx4r2c` | 2026-07-24 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/armE-r1-complete` | 2026-08-01 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/arrival-provenance-warning` | 2026-08-01 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/aso-e13-tissue-expression` | 2026-08-15 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/aso-paper-improvements-m2ufex` | 2026-06-26 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/aso-paper-publication-value-d2t9hm` | 2026-06-27 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/aut-pd-130-s4-CYC-0074` | 2026-08-29 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/aut-pd-145-s2-CYC-0074` | 2026-08-29 | **B** ⚠ | obsolete defect, but ⚠ carries a single-ref file — extract first (§4d) |
| `claude/aut-pd-147-s3-CYC-0074` | 2026-08-29 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/aut-pd-148-s5-CYC-0074` | 2026-08-29 | **B** ⚠ | obsolete defect, but ⚠ carries a single-ref file — extract first (§4d) |
| `claude/aut071-s1-CYC-0074` | 2026-08-29 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/aws-budget-storage-shutdown-iq8oh7` | 2026-08-13 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/azure-l4s-setup-y856cz` | 2026-07-23 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/best-paper-submission-tqa0cn` | 2026-08-10 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/candidate-ternaries-generation-llnvoe` | 2026-07-24 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/ci-a3b5-lanes` | 2026-08-07 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/cloud-provider-free-credits-obc0e9` | 2026-07-18 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/cofold-image-bake` | 2026-08-01 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/daily-degrader-email-routine-hs8hd9` | 2026-07-15 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-8xtt-decoynull` | 2026-07-10 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-8xtt-rebase` | 2026-07-10 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-8xtt-scripts` | 2026-07-10 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/degrader-de-novo-design-8qhk6t` | 2026-06-29 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/degrader-fep-diagnostics` | 2026-07-10 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/degrader-genmatched-null` | 2026-07-10 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-metad-multiwalker` | 2026-07-10 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-paper-graphic-yomcbt` | 2026-06-29 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/degrader-paper-journals-tfjt0v` | 2026-07-05 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-paper-publication-ukqz8u` | 2026-07-05 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-paper-red-team-z9ct1n` | 2026-06-30 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-paper-review-11e22z` | 2026-06-29 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-paper-review-mvgduo` | 2026-07-10 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-paper-revision-srqaqa` | 2026-07-10 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-paralogue-specificity-s1tge3` | 2026-07-12 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-path-next-steps-zlikts` | 2026-07-17 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-restructure-si` | 2026-07-10 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degrader-timeline-plan-8e8sdj` | 2026-07-15 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/degraders-car-t-therapy-yo4twc` | 2026-07-08 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/drug-repurposing-cryptic-pocket-kq5857` | 2026-07-08 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/elink-probe-ci-fefnhh` | 2026-08-15 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/emc-research-strategy-kdz9kn` | 2026-07-11 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/emc-roadmap-red-team-s4olc0` | 2026-06-24 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/emc-symptom-treatment-742257` | 2026-08-09 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/fep-denovo-401-candidate-gd9j6f` | 2026-07-10 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/frontier-capability-sweep-r3-2026-08-07` | 2026-08-07 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/gcc-nat-emc-aso-aq0eba` | 2026-08-25 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/gcp-gpu-quota-increase-61pnzu` | 2026-07-15 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/gcp-l4-selffeed` | 2026-08-01 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/github-daily-email-routine-xhiygr` | 2026-07-26 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/gitlab-repo-thread-clarity-7w21r8` | 2026-06-24 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/gpu-experiment-orchestration-49ocxp` | 2026-08-02 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/gpu-molecular-dynamics-selection-pvybay` | 2026-08-01 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/lane-registry-contract-test` | 2026-08-01 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/lit-probe-immuno-architectures` | 2026-08-07 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/litverify-cycle-closure` | 2026-07-27 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/manuscript-strategy-alignment-elx4b2` | 2026-07-24 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/manuscript-strategy-review-ie23f0` | 2026-07-31 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l` | 2026-07-30 | **B** | own diff resolves to 0 files against its fork point; §2 families only |
| `claude/max-effort-2dq11l-4fs` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-anchor` | 2026-07-25 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/max-effort-2dq11l-basin` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-calib` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-cofold` | 2026-07-25 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/max-effort-2dq11l-e3` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-linker` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-nrv04` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-paper` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-paralogue` | 2026-07-26 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-reach` | 2026-07-26 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-relib` | 2026-07-26 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-retro` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-triangle` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-2dq11l-watch` | 2026-07-26 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-3hgq45` | 2026-07-27 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/max-effort-chy5sj` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-effort-phbmra` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/max-token-usage-sprint-cwihvo` | 2026-09-01 | — | this session's own working branch (`HEAD`) |
| `claude/method-watch-llm-filter-x7mlm1` | 2026-07-17 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/new-session-4pk0vx` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/next-expansion-priorities-t64njy` | 2026-07-24 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr-v04-retrospective-testing-6ywxye` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr4a-degrader-red-team-3qvsod` | 2026-06-26 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr4a1-protac-positive-control-xnszjl` | 2026-08-03 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/nr4a3-degrader-denovo-um2xby` | 2026-06-29 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr4a3-degrader-design-3dqcw7` | 2026-07-12 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/nr4a3-degrader-next-steps-s9i3ii` | 2026-06-28 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr4a3-druggability-4sspvq` | 2026-07-05 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr4a3-emc-addiction-ddnlci` | 2026-06-29 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/nr4a3-ensemble-redesign-oe4ilo` | 2026-07-11 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr4a3-fusion-degrader-efidn1` | 2026-07-09 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/nr4a3-fusion-reversal-027n31` | 2026-07-03 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr4a3-gapmer-presubmission-d4vqmp` | 2026-08-25 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/nr4a3-lbd-bioemu-validation-w421nb` | 2026-07-24 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr4a3-mmgbsa-verdict-dgpemq` | 2026-06-29 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr4a3-selectivity-matrix-r2b323` | 2026-06-28 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr4a3-structure-update-i0pgpx` | 2026-07-10 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/nr4a3-ternary-coop-prereg-51wqw9` | 2026-07-13 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nr4a3-ternary-coop-prereg-5ml7r2` | 2026-07-16 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/nrv04-retro-fold` | 2026-08-01 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/nrv04-secondaries-e2e3e4` | 2026-08-01 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/nrv04-secondaries-e2e4` | 2026-08-01 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/oracle-cloud-gpu-credits-focnql` | 2026-07-23 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/orphaned-fusion-junction-catalog-0jgizz` | 2026-08-13 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/paper-testing-plan-ke1cip` | 2026-07-16 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/parallel-test-vast-cs5ugw` | 2026-07-25 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/preprint-host-unaffiliated-srzofd` | 2026-08-21 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/protac-cancer-treatment-8hg282` | 2026-07-23 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/protac-paper-daily-email-6yjb6r` | 2026-07-15 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/proximity-lit-sweep-7rydac` | 2026-08-07 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/rare-cancer-info-hub-vb8uui` | 2026-06-24 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/rare-disease-grants-4pyyvc` | 2026-07-20 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/red-team-degrader-paper-l1hukn` | 2026-07-06 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/red-team-nr4a3-degrader-pwi0fd` | 2026-06-30 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/retro-price-ledger-forensics` | 2026-07-31 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/retro-smoke-forensics` | 2026-07-31 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/robotic-wet-lab-monitoring-nc0b96` | 2026-07-05 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/rung-2-parallel-7asnpk` | 2026-07-23 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/s24-threshold-calibration` | 2026-09-01 | — | driver already read it; merging for content |
| `claude/s76-sgk1` | 2026-08-29 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/sagemaker-flagship-paper-setup-l6chwo` | 2026-06-26 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/selcal-reap-fix` | 2026-08-01 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/selcal-watch-resurrect` | 2026-08-01 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/selectivity-resolution-options` | 2026-08-01 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/spot-training-pricing-vkjfow` | 2026-07-09 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/step1-fanout-cmpd19-congeneric-jfwg0j` | 2026-07-24 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/tcip-effector-stage-ci` | 2026-08-06 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/test-results-docs-sync-opypup` | 2026-07-30 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/trigger-e3-recruiter-grade` | 2026-08-03 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `claude/val-b-openfe-ternary-bvfhjy` | 2026-07-17 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `claude/vala-mini-results-skip-lyo783` | 2026-07-18 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/valb-mini-gate-failure-next-jkk1ea` | 2026-07-30 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `claude/vast-exclusion-fix` | 2026-07-29 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `cyc0073-d4ccfde4-work` | 2026-08-29 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `deepternary-qualify-cache` | 2026-07-13 | **C-INFRA** | orphan data branch; 5 references on `main`; workflows write to it |
| `email-outbox` | 2026-08-28 | **C-INFRA** | orphan data branch; 10 references on `main`; workflows write to it |
| `enumeration-cache` | 2026-06-20 | **C-INFRA** | orphan data branch; 3 references on `main`; workflows write to it |
| `field-scan-log` | 2026-07-13 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `figure-renders` | 2026-06-22 | **C-INFRA** | orphan data branch; 4 references on `main`; workflows write to it |
| `fix/ternary-vast-deaths` | 2026-07-29 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `lane-ckpt-exposure` | 2026-07-29 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `lane-deadunits-fix` | 2026-07-29 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `lane-work-ledger` | 2026-07-28 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `lane13-watch` | 2026-07-26 | **C-INFRA** | orphan data branch; 1 references on `main`; workflows write to it |
| `lit-iso-wf` | 2026-08-07 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `literature-cache` | 2026-08-30 | **C-INFRA** | orphan data branch; 187 references on `main`; workflows write to it |
| `litverify-cache` | 2026-07-27 | **C-INFRA** | orphan data branch; 0 references on `main`; workflows write to it |
| `litverify-tmp` | 2026-07-27 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `method-watch-cache` | 2026-08-28 | **C-INFRA** | orphan data branch; 12 references on `main`; workflows write to it |
| `modalities-cache` | 2026-09-01 | **C-INFRA** | orphan data branch; 61 references on `main`; workflows write to it |
| `preprint-cache` | 2026-08-09 | **C-INFRA** | orphan data branch; 1 references on `main`; workflows write to it |
| `rbfe-introspect-cache` | 2026-07-14 | **C-INFRA** | orphan data branch; 2 references on `main`; workflows write to it |
| `rbfe-split-cache` | 2026-07-16 | **C-INFRA** | orphan data branch; 1 references on `main`; workflows write to it |
| `replicate-standard-cache` | 2026-07-30 | **C-INFRA** | orphan data branch; 3 references on `main`; workflows write to it |
| `s1-aut-pd-050-unscored-rows` | 2026-08-28 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `s3/aut-pd-031-line-citations-enumerate-carriers` | 2026-08-28 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `seat/s1-aut-pd-130` | 2026-08-28 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `seat/s3-unscreened-endpoints` | 2026-08-28 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `seat/s4-aut-045` | 2026-08-28 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `seat/s5-retest-blocks` | 2026-08-28 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `supervisor-fix` | 2026-07-27 | **B** | tip is an ancestor of `claude/max-effort-2dq11l`; adds only the retired site + profiler telemetry (§2, §5a) |
| `tvast-marker-recency` | 2026-07-28 | **A** | measured line-absorption into `main` (§4e/§5b) |
| `txgnn-cache` | 2026-06-21 | **C-INFRA** | orphan data branch; 2 references on `main`; workflows write to it |
| `vaccine-calibration-cache` | 2026-09-01 | **C-INFRA** | orphan data branch; 2 references on `main`; workflows write to it |
| `vast-blacklist-retest` | 2026-07-28 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `wip/lane-snapshot-2026-07-27-1410et` | 2026-07-27 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `wip/lane-snapshot-2026-07-27-1440et` | 2026-07-27 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `wip/lane-snapshot-2026-07-27-1455et` | 2026-07-27 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `wip/lane-snapshot-2026-07-27-1705et` | 2026-07-27 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `wip/lane-snapshot-latest` | 2026-07-28 | **C** | see §3/§4c/§5c — carries content on no other ref, or unabsorbed code |
| `worktree-agent-a1050d046c87837d4` | 2026-08-02 | **B** | tip is an ancestor of `claude/trigger-e3-recruiter-grade`; adds only the retired site + profiler telemetry (§2, §5a) |
| `worktree-agent-a8e9ae2f991db8def` | 2026-08-07 | **B** | empty commit; three-dot diff and `--name-only` both empty |
| `worktree-agent-ab0b548a575724822` | 2026-08-07 | **A** | measured line-absorption into `main` (§4e/§5b) |

---

## §7 · TALLY, THE UNMEASURED COUNT, AND THE MERGE-ORDER HAZARDS

### 7a · Tally over all 185 refs

| verdict | count |
|---|---|
| **A** · superseded by content on `main` | 31 |
| **B** · empty, obsolete, or subsumed by a named sibling | 95 |
| **B ⚠** · obsolete verdict stands, but a single-ref file must be extracted first | 2 |
| **C** · worth keeping | 40 |
| **C-INFRA** · live cache branch — must not be deleted or merged | 15 |
| — · excluded by instruction (`s24-threshold-calibration`, this session's own `HEAD` branch) | 2 |
| **D · UNMEASURED** | **0** |

### 7b · Why the UNMEASURED count is 0, and where the residual doubt actually sits

The shallow graft made **ancestry against `main`** unusable for 147 refs, and a census that stopped
there would have had to report 147 UNMEASURED. Two instruments removed that:

1. **A tree diff needs no merge-base.** Whether a file exists on `main`, and whether its bytes match,
   is answerable directly — so every branch's ADDITIONS are settled, and the all-302-ref probe
   behind §3 is exact.
2. **Pre-graft branches share merge-bases with each other**, so a fork point is recoverable and each
   branch's own change is readable. The `--is-ancestor` containment test is exact, and it settled 93
   refs outright.

⚠ **Three residual uncertainties, named rather than hidden:**

- **The fork point is a LOWER BOUND.** `diff <fork>...<branch>` can therefore include commits the
  branch merely inherited, inflating its apparent own-work. This biases toward **C**, which is the
  safe direction, and it is why several C rows in §5c are marked weak.
- **Prose absorption cannot separate "rewritten on `main`" from "lost".** Every C verdict whose only
  evidence is low absorption on a `.md` is therefore soft; each is flagged in §5c, and
  `origin/claude/val-b-openfe-ternary-bvfhjy` (STRATEGY.md alone) is the softest.
- **`origin/claude/trigger-e3-recruiter-grade` was absorption-sampled at 60 of 348 files** (92 %),
  with all 44 of its `main`-absent paths individually rename-checked. The unsampled 288 files are
  the largest single gap in this census.

### 7c · MERGE-ORDER HAZARDS

**H1 — the working tree is not on `main`, and it holds the previous discharge.** `HEAD` is
`claude/max-token-usage-sprint-cwihvo` at `f1d3621fe`, **20 commits ahead of `origin/main`** with
**61 uncommitted paths**. The nine `-s ours` supersession merges from earlier tonight are among
those 20 commits and **have not reached `origin/main`** — which is why this census counts 38
merge-base branches / 182 commits where the hook says 38 / 169. ⛔ Nothing here is discharged on the
trunk until that branch merges.

**H2 — six branches collide with files that are dirty right now.** Merging any of them before the
working tree is committed means resolving against a moving file:

| dirty file | branches that also touch it |
|---|---|
| `research/autonomy/research-ledger.json` | 9 branches — `aut-pd-145`, `aut-pd-147`, `aut-pd-148`, `s76-sgk1`, `seat/s3`, `seat/s4`, `seat/s1-aut-pd-130`, `aut071-s1`, `aut-pd-130-s4`, `cyc0073-d4ccfde4-work` |
| `research/autonomy/amendments.jsonl` | `aut-pd-052`, `aut-pd-145`, `s1-aut-pd-050`, `cyc0073-d4ccfde4-work` |
| `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` + 7 built PDF/DOCX | `nr4a3-gapmer-presubmission-d4vqmp` (13 overlapping paths — the largest collision), `preprint-host-unaffiliated-srzofd`, `seat/s1-aut-pd-130`, `aut071-s1`, `aut-pd-130-s4` |
| `systems/graph/routes.json` | `s76-sgk1`, `seat/s4-aut-045`, `aut071-s1`, `emc-symptom-treatment-742257`, `best-paper-submission-tqa0cn` |
| `research/manuscripts/pinned-figures.json` | `best-paper-submission-tqa0cn`, `nr4a3-gapmer-presubmission`, and three pre-graft branches |
| `research/modalities/vaccine_threshold_calibration.py` | `s24-threshold-calibration` — **the branch the driver is merging right now** |

⛔ Under CLAUDE.md §6 this is exactly the mutation window that put 13 inverted claims on
`origin/main`: **stage by path, never `git add -A`, while any of this is in flight.**

**H3 — branch-to-branch overlaps.** `origin/lit-iso-wf` is a strict superset of
`origin/claude/frontier-capability-sweep-r3-2026-08-07` (they share all four of the latter's
commits); merge `lit-iso-wf` and the other is discharged for free. `origin/claude/proximity-lit-sweep-7rydac`
and `origin/claude/lit-probe-immuno-architectures` **both add `scripts/lit_batch_probe.py` with
different content** — a real conflict, and whichever merges second overwrites the other. The five
`wip/lane-snapshot-*` refs carry the same three files at four timestamps; only
`…-1455et` adds anything the others lack (the fleet-supervision alarm).

**H4 — two `CYC-0073-d4ccfde4.json` receipts.** `origin/cyc0073-d4ccfde4-work` has it at
`research/autonomy/receipts/`; `main` has different content at `autonomy/receipts/` (no `research/`
prefix). One of the two is misfiled and merging will not reveal which.

**H5 — the C-1 recovery must be path-scoped.** `origin/claude/emc-research-strategy-kdz9kn` carries
the atlas **and** the retired patient-facing site. A plain merge recreates the site CLAUDE.md §7
forbids. Take `research/atlas/**` and `.github/workflows/atlas-data.yml`; take nothing else. The
same applies to every pre-graft C row.

### 7d · What this census does not claim

⛔ It does not claim a **B** row is safe to delete without reading §2 — a B verdict here means "its
`main`-absent files are the retired site or the profiler telemetry, and its tip is inside a named
sibling". If either of those premises is wrong for a given branch, so is its row.
⛔ It does not claim the **C** rows are all valuable, only that each holds bytes that exist nowhere
else, which is a different and much easier thing to be sure of.
⛔ **Nothing was deleted, merged, or written to the repository by this census.**

---

## §8 · ADDENDUM — the working tree moved WHILE this census ran

Re-read at the end: the uncommitted set went **61 → 81 paths**. This census wrote nothing to the
repository, and none of the 20 new paths is its own (`git status | grep scratch` is empty). They are
the concurrent gate run and document build:

    research/manuscripts/claim-coverage.json     research/modalities/emc-atr-vulnerability.json
    systems/graph/blockers.json                  systems/graph/publications.json
    systems/views/L0-ecosystem.md                systems/views/L3-publications.md
    systems/views/L1-st-{care-delivery,locoregional,strategy}.md
    systems/views/L2-rt-{ipd-survival,limb-perfusion,lung-directed,metastasectomy,risk-model,
                          rt-intensify,sequencing,surgical-quality,surveillance}.md
    systems/views/paper-strength.md              systems/views/registers/blockers.md

⛔ **This widens hazard H2 into `systems/`.** `systems/graph/*.json` is the source of truth and
`systems/views/**` is GENERATED — a hand-edit fails the build. Two C branches write there:
`origin/claude/emc-symptom-treatment-742257` adds seven `systems/views/L1|L2-*.md` **and** the seven
graph rows they generate from, and `origin/claude/best-paper-submission-tqa0cn` modifies
`systems/graph/routes.json`. ⛔ **Merge either only after the in-flight regeneration has landed, and
recover the graph rows rather than the generated views** — taking the views alone would put
hand-carried files where the build expects generated ones.

⚠ And `research/manuscripts/claim-coverage.json` is now dirty — the same file §4e cites as the
present-day home of `nr4a3-gapmer-presubmission-d4vqmp`'s `aso/claim-coverage.json`. That A verdict
was taken against the committed `origin/main` copy and is unaffected, but the file is moving.
