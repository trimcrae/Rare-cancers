# Common worker brief — OPUS-CAPACITY-CAMPAIGN-20260908

Read this in full before doing anything else. It binds every worker in this campaign.

## 1. Your environment and boundaries

- Repository: `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`.
  **CORRECTED 2026-09-08T03:36Z (W35, measured): there is no frozen read commit.** HEAD advances
  during this campaign as the coordinator collects reports — **record the HEAD you actually read**,
  at start and at end. `92abbcb905cacf07f14b238db50d1b98f6590374` is the campaign's *start* commit,
  not a pin, and the campaign directory does not exist at it (`git ls-tree -r --name-only 92abbcb --
  research/autonomy/opus-capacity-campaign-20260908` returns 0 files), so this brief and
  `CLOSED-WORK.md` are unreadable there. Read the working tree. Treat the whole tree as
  **read-only** except your own two paths.
  **Why the stale pin caused no measurement error, and when that stops being true (W35b, measured
  2026-09-08T03:41Z):** `92abbcb` is the parent of the first campaign commit, and every commit since
  touches ONLY this campaign directory — `git diff --name-only 92abbcb HEAD | grep -v
  opus-capacity-campaign-20260908` is empty, re-measured at HEAD `5ae0fa04`. W35b classified all 133
  reports citing the pin: 0 CONTRADICTORY, and every pin-anchored claim survives re-running at both
  commits. **If a coordinator commit ever touches anything outside this directory, that guarantee
  ends and 39 pin-anchored reports lose it silently.**
- **WRITE ISOLATION — CORRECTED 2026-09-08T01:52Z, this supersedes any write path named in your
  dispatch prompt.** You are **READ-ONLY on the Git working tree**. Disjoint paths inside one
  shared working tree do not satisfy `AGENTS.md`, so no worker writes into the repository at all.
  Instead you **draft in response**: return your complete report as the body of your final
  response, and the coordinator (the single collector) writes it to disk. Any code you author is
  returned inline in fenced blocks, not written into the tree.
  You MAY write scratch files under `/tmp/claude-0/` if you need to execute code — run it there,
  outside the repository, and quote the real command, environment and exit code.
  Do not touch `main`, other workers' files, frozen deliverables, preregistrations,
  `systems/graph/`, the clinical registry, or shared coordination state (`cycle-tasks.json`,
  claims, receipts, health, hardening-state).
- **No git write operations at all**: no commit, branch, checkout, worktree, stash, push, merge,
  PR. The coordinator integrates. Do not run `scripts/preflight.sh` unless your dispatch says to.
- No paid API, no GPU spend, no alternative model, no contacting humans, no publication, no
  posting to aiXiv/Qeios/journals, no external correspondence.
- Bounded run — this is a **target you self-observe, not a limit the harness enforces**: aim to
  finish within roughly 40 minutes and roughly 40 tool calls, and report your actual counts.
  **Return as soon as your stop condition is met** — do not pad, do not invent extra work,
  do not sleep.

## 2. Scientific integrity (non-negotiable)

- Never invent facts, sources, citations, patient data, measurements, accessions, or test
  results. Every claim traces to a retrievable source or a computation you actually ran.
- Distinguish **primary evidence / prediction / association / experimental validation**. No
  computational result establishes clinical efficacy, safety, selectivity, therapeutic window,
  or clinical readiness. There is no wet lab; no reagent design.
- **Actual test evidence = command + environment + exit code**, quoted from a run you performed.
  Anything you did not execute must be labelled `PROPOSED (NOT RUN)`. A skipped test is not a
  pass. Never weaken a check to make something pass. You may not author or relax your own
  acceptance criteria.
- Preserve negative results and scope limitations exactly as they stand.
- If you hit a content-policy refusal, **stop that branch, record it verbatim, and do not
  rephrase, reroute, or relabel it.** Report the refusal in your deliverable.
- Access controls are respected: a 403/paywall is an honest unrecovered source, not a hurdle to
  circumvent. Do not replay a route already recorded as denied without a genuinely new route.
- A missing file, absent abstract, or empty search is **UNKNOWN, not proof of absence.**

## 3. Mandatory prior-work check before claiming anything is new

Search the actual tracked corpus first, e.g.
`rg -n -i "<term>" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**' | head -50`
  **Campaign reports are not repository evidence.** If your only hit is a sibling's report, that is
  not prior art and not a refutation (W35, 2026-09-08T03:36Z).
and `git ls-files | rg -i "<term>"`. Then read `CLOSED-WORK.md` in this directory. If your
proposed question turns out to be already answered or already closed, say so plainly and pivot
to the nearest genuinely open question **inside your lane**, recording why.

## 4. Deliverable format (your report file)

**Return this as your final response body** (do not write it into the repository). Sections in
this order:

1. `## Worker` — worker ID, lane, and **model evidence**. State your model identity explicitly
   as a **SELF-REPORT (not independently verified)**, and paste the literal output of
   `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`
   and `date -u` at start and end. Do not assert a served model as observed fact; the coordinator
   extracts the actual per-child runtime model from the transcript.
2. `## Question` — the one concrete question you actually pursued, and why it is open.
3. `## Prior-work check` — the exact `rg`/`git ls-files` commands you ran and what they showed;
   which closed items you confirmed you are not replaying.
4. `## Method / inputs` — exact files, accessions, URLs, tools, versions.
5. `## Result` — what you actually found. Tables with units, n, and uncertainty definitions.
   Mark every row `PRIMARY`, `SECONDARY`, `PREDICTION`, or `UNKNOWN`.
6. `## Validation evidence` — commands run, environment, exit codes, verbatim key output.
   Separate `RUN` from `PROPOSED (NOT RUN)`.
7. `## Limitations` — including transfer limits, denominator gaps, and what this cannot claim.
8. `## Stop condition` — the condition you set, and whether it was met, not met, or blocked.
9. `## Tool-call and wall-clock count actually used`, then `## Next concrete action` — one specific successor task for this lane, or an honest
   "no viable successor in this lane, because …".

## 5. What counts as a useful artifact

A retrievable, source-traceable finding; a working script with a real test run; a reproducible
table built from committed or public data; a precise, evidence-backed negative result; or a
concrete diagnosis of a real defect with the smallest correct repair. A plan alone is not an
artifact. A restatement of existing repository content is not an artifact.

## Known, measured, and NOT worth rediscovering

- **The campaign's resolution rate is 0 of 89, and it is measured — do not re-measure it.**
  W36 indexed 103 routed-but-unlanded items; W36b then checked **every** row against the tree
  (2026-09-08T03:52Z): **87 confirmed still unlanded, 2 false report premises, 14 not checkable by
  inspection, 0 landed.** The structural reason is stronger than the greps: at every HEAD checked,
  `git diff --name-only 92abbcb HEAD | grep -v opus-capacity-campaign-20260908` returns **0 files** —
  **no repository file outside this campaign directory has changed at all.** So no Tier-1/2/3 item
  *could* have landed. Re-measuring this is the "repeatedly rewrite a correct paper" failure
  CLAUDE.md §5 names. If you find a routed item, add it; do not re-verify the backlog.

- **`origin/literature-cache` has never existed in this checkout, and that is not an incident.**
  W40 settled it (2026-09-08T03:49Z): neither `refs/heads/literature-cache` nor the remote-tracking
  ref exists, `.git/packed-refs` does not exist, the object `216bd1b5…` reports `missing` from
  `cat-file --batch-check`, and `.git/logs` has **zero** literature-cache trace — a state git does
  not produce by deleting a branch. The checkout is **shallow** (42 grafts, `+refs/heads/*` fetch
  spec), which is a sufficient ordinary explanation. An earlier report's line attributing a
  `<sha>\t<refname>` output to `git branch -a --list` is a format mismatch (`git branch` prints
  indented short names with no SHA); that shape comes from `git show-ref` or `git ls-remote`.
  **Do not read this as a lost ref.** Whether the branch exists on the remote is UNKNOWN — do not
  fetch to find out. Of nine consumers that resolve the ref, six fail loud, two degrade and say so
  in their artifact, and one (`submission_citations.py:304,307`) is silent; that one is already
  routed to its owner.

- **`pytest` IS INSTALLED in this container, and `python3 -m pytest` is the wrong command.**
  W29f settled this by execution (2026-09-08T03:49Z): pytest 9.1.1 lives at `/root/.local/bin/pytest`,
  a symlink into a **uv tool venv** whose shebang names `/root/.local/share/uv/tools/pytest/bin/python3`
  — a different interpreter from `/usr/local/bin/python3`, with a different site-packages.
  So `python3 -m pytest` correctly reports `No module named pytest` while `pytest` runs fine.
  **Any claim in this campaign that "pytest is not installed, so no pass/fail is obtainable" is
  measuring the wrong interpreter**, and every "a test compensates" claim resting on it is a source
  reading that could have been a real run. The repository already documents this exact trap:
  `scripts/tests/test_the_dep_probe_asks_the_interpreter_that_runs_the_tests.py` records incident
  AUT-PD-026 (2026-08-15, 36 invented failures), and `scripts/preflight.sh` resolves `_PYTEST_PYTHON`
  by branching on it. Run tests with `pytest`, never `python3 -m pytest`, and a skipped test is
  still not a pass.

- **`scripts/preflight.sh`'s systems step is red for reasons that have nothing to do with your change.**
  W31b measured (2026-09-08T03:34Z) that removing this campaign directory takes
  `systems/systems_check.py --check` from 172 ERROR to **0 ERROR, exit 0**, and that the
  pre-campaign commit `92abbcb9` is likewise 0 ERROR. **100% of that baseline is this campaign's
  own footprint**, and ~87% of it is one `[D4]` "no frontmatter" error per collected report, so
  the count grows by one per report and is never the same number twice. Do not spend a run
  attributing it. `systems/tests/test_views_match_the_graph` remains the honest signal for view
  drift. The coordinator has NOT added a `DOC_SKIP` exclusion: the 9 `inputs/` errors under it are
  real findings, and narrowing a checker to shrink a number is the move this repository's own
  design note at `systems_check.py:1436` warns against.

### The clinical registry passes its validator cleanly — measured 2026-09-08T04:40Z

`node scripts/validate-registry.mjs` at HEAD `408b676a` prints
`OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).` and exits **0**.
W30d audited all 170 lines against every registry-facing sentence of `systems/POLICY-evidence.md`
(34 requirement rows) and mutation-probed each weak row. **Every WEAKER and NOT-IMPLEMENTED row is
LATENT — zero are live**: the committed registry satisfies the policy *text* on every sentence
decidable from the file, not merely the weaker gate. Do not re-run the shape census (25 citations,
14 cohorts, 4 patients, 2 evidenceQuestions/9 positions, 10 systemicEvidence, 6 emergingTreatments,
11 studies, 12 metric blocks; provenance vocabularies clean at `{primary, secondary}`; 25/25 licenses;
9/9 contextReason; 5/5 pooled cohorts periodised or explicitly `studyPeriodUnknown`).

One measured **code defect** worth knowing before you read that script: `scripts/validate-registry.mjs:115`
stores an array **index** in `poolKeys[key]` and then tests it for truthiness, so index `0` is falsy and
the §2.3 double-counting guard is silently inoperative for `cohorts[0]` — the registry's largest pooled
cohort. Measured: duplicating `cohorts[0]` → `0 warning(s)`, exit 0; duplicating `cohorts[1..4]` → WARN.
Also note the script has **no test of its own**; the one grep hit in `scripts/tests/` is a docstring.

### `modalities.json` prose does not reach any generated view — measured 2026-09-08T04:40Z

W26d whole-field-sentinelled 14 fields and regenerated all 111 views. Six `modalities.json` fields
(`MOD-ARGININE-DEPRIVATION.requires[0]`, `MOD-PRMT5-MAT2A.requires[0]` and `.rationale`,
`MOD-MCL1-BCLXL.rationale`, `MOD-RET.rationale`, `MOD-TF-LBD-OCCUPANCY.rationale`) have a blast radius
of **exactly zero view files** — nothing re-rendering can ever check them. The mechanism is structural,
not the 150-char clip: `grep -n '"requires"' systems/systems_check.py` returns **no hits** (the field is
never read), and the census renderer's `rationale` row is gated on the record having no `route`, which
all five of those records do. Do not re-derive this.

Also retired by measurement: the inherited claim that a `strategies.json` `limitations[n]` fans out to
"5–8 view pages". Measured range on W26c's four fields is **3 to 12** (`ST-REPURPOSING.limitations[1]`
= 12 pages, `ST-RADIOLIGAND.limitations[0]` = 3). Fan-out tracks the size of the route family the
strategy owns, not the file. Quote the measured number, not the range.

### `inputs/` is untracked scratch, and it will fail `PREFLIGHT_FULL=1` — measured 2026-09-08T04:39Z

W41 measured that `research/autonomy/opus-capacity-campaign-20260908/inputs/` is **gitignored** (this
directory's own `.gitignore:10`): `git ls-files` returns 0 files under it, it is in no commit, and it
does not exist in a fresh clone or in CI. It is the only non-cache ignored path in the whole tree.
Consequences, all measured, none of them a repository defect:

* All **9** `systems_check --check` errors attributed to `inputs/` are working-tree-only. Six are not
  findings about this repository at all (3 link-depth artefacts, 2 `[D4]` over untracked scratch, 1
  `[D6]` id collision); 3 are real dangling links inside the *capsule's* text, which no tracked file
  contains. `git grep -l -F 'id: DOC-AUTONOMY-OPERATING-PROTOCOL' HEAD --` returns **exactly one**
  tracked claimant, so the id-uniqueness invariant **holds** over the repository.
* Gate 2 (`systems_check --check`) is red from the tracked `reports/` regardless — removing `inputs/`
  would leave ~210 errors and rc=1. The 9 are ~4% of a gate that fails either way.
* ⚠ **`PREFLIGHT_FULL=1` — the publication-candidate gate — additionally fails a pure-logic test for a
  reason unconnected to any change**: `scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py::`
  `test_every_tests_directory_in_the_repository_is_inside_some_budget` walks the root skipping only
  `.git`, `node_modules`, `__pycache__` and dot-directories, and finds the two capsule `tests/`
  directories under `inputs/source-index/` in no tier of `scripts/tier-budgets.json`. Anyone running
  the full gate on this branch must expect that failure and must NOT "fix" it by widening a budget or
  narrowing a walk. (W41's evidence is a verbatim replication of the assertion body, exit 1, not a
  captured pytest run.)
* Only `systems_check.py` sees `inputs/` at all: `lint_citations.py:187` and `emc_systems_map_check.py:351`
  use `git ls-files --cached --others --exclude-standard`, which excludes ignored paths by construction,
  and the other ten gates iterate declared collections or fixed globs.

⚠ Separately, and worth a deliberate human check: `inputs/evidence-4878/research/autonomy/OPERATING_PROTOCOL.md`
is a **divergent copy** of the live protocol — same `id: DOC-AUTONOMY-OPERATING-PROTOCOL`, same
`last_verified: 2026-09-04`, but 74 lines present only in the copy and 1 only in the live file. The
copy-only text includes procedural rules (a standing pre-submission "ultra-reasoning pass" requirement
dated 2026-09-05, a "continue beyond a route-specific blocker" section) that appear in **no tracked file**
at this HEAD. Which version is authoritative is **UNKNOWN**. Do not follow the copy: read
`research/autonomy/OPERATING_PROTOCOL.md` from the working tree, as this brief already instructs.

### ⛔ Lane 2 is CLOSED, and its last surviving claim is WITHDRAWN — measured 2026-09-08T04:38Z

W02k ran the pre-declared E2-limb calibration W02j named as the only remaining falsifying test on this
substrate. Both limbs of W02i's frozen arm-to-arm rule are now measured against random 14-gene panels
drawn from the same 423-gene non-marker universe:

* `E1` fires for **0.2950** of random panels (W02j), nominal 0.05.
* `E2` (`p_lo <= 0.05` against the exhaustive C(17,6)=12376 LGFMS subsamples) fires for **0.2075**
  (83/400), nominal 0.05 — 4.15x nominal, 15.4 binomial SE above it.
* The joint rule returns `U` for **15%** of random panels.
* Most telling: `p_lo == 1/12377` — the *exact* minimum-attainable event the fibro/ECM row achieved —
  occurs in **15 of 400** random panels (0.0375) against an expected 0.032 panels. The `p_lo = 0.00008`
  headline was never a small probability; it is a floor the EMC arm reaches routinely.

**The fibro/ECM `U` (EMC `R_gene` 2.0460) is WITHDRAWN as evidence of anything about fibro/ECM genes.**
The measured number is still true — EMC's fibro/ECM `R_gene` really is 2.0460 and really is below all
12376 LGFMS subsamples — what is withdrawn is the claim that it is *unusual*. The failure is directional
(`F_HI` = 0.0675, near nominal), which points at a gene-set-independent offset between the EMC arm's six
arrays and LGFMS arrays; batch, scan date, processing and cellularity are all confounded with disease
class in this deposit and none is separable. **The cause is UNKNOWN and no candidate is claimed.**

Lane 2 is finished on this substrate: two withdrawn findings (endothelial W02i, fibro/ECM here), one
measured specificity failure, and a rule with no informative limb. The next real question — arm
exchangeability — needs the uncommitted GSE24369 series matrix, whose retrieval is DENIED. **Do not
dispatch further lane-2 statistics on `emc-expression-panels.json`.** No new lane-2 worker, and no
report, may restate the fibro/ECM `U` as a finding.

### The `superseded[]` guard census is settled at 39 / 13 / 29 — measured 2026-09-08T04:39Z

W28d individually transplant-tested all 40 of W28c's WOULD-MATCH entries against the real compiled
patterns: **39 MATCH, 1 reclassified UNTESTABLE, 0 refuted**. The registry-wide split is therefore
**39 WOULD-MATCH / 13 WOULD-NOT-MATCH / 29 UNTESTABLE**, and the frame screen's measured error over all
81 entries is **one false negative and zero false positives** (failure mode named: quantity-*arity*
mismatch, as in `rbfe_edge_tyk2_rate`). Do not re-run the transplant set.

Two corrections that must travel with any use of these numbers:

* ⛔ **The 13 WOULD-NOT-MATCH is NOT a dead-guard count.** Three of them —
  `buy_line_1_5x_multiple_expression`, `card_ratio_4090_over_4080_within_7pct`, `xtt_pre_harmonized` —
  do fire on live committed target text. The 13 measures phrasing fragility against the registry's own
  `current` field, nothing more.
* ⭐ **A far stronger and cheaper instrument exists, and it needs no fixture at all**: run the compiled
  patterns over the real 29 `targets[]` through the real `is_cleared`. Measured: **58 of 81 entries fire
  on committed text, 246 times, and all 246 are cleared**; `python3 research/manuscripts/lint_consistency.py`
  → `0 ERROR across 29 target file(s)`, exit 0. Start any future liveness question there and use
  transplants only for the ~23 entries the tree cannot exercise. Note the consequence: the guards' only
  live exercise path is through `is_cleared`, so a regression there would un-cover 58 guards at once.

⚠ Methodological warning for anyone building a frame screen: for an alternative that is a bare numeric
literal, the frame degenerates to "any number" and the automatic transplant lands on whatever numeral
comes first — producing inadmissible fixtures like `RTX 755.36 = 804.06`. 8 of 40 of the screen's calls
rested on such a vacuous frame. A fixture is admissible only if its wording comes from committed text.

### The unread-act-assertion class is censused at 34 fields — measured 2026-09-08T04:40Z

W43 enumerated act-asserting fields by *reading the key space* of the clinical registry,
`pinned-figures.json`, `systems/graph/*.json` and 986 provenance-carrying JSON files under
`research/modalities/` and `research/manuscripts/`: **13 ENFORCED, 1 UNREAD-BUT-DECIDABLE, 20
UNREAD-AND-UNDECIDABLE**, totalling **≈478 unread act-assertion records**. Do not re-census this.
Corrections and cautions it establishes:

* **Registry `verified` is 36 records, not 25** — 25 under `registry.citations`, plus 11 under
  `studies.items[]`. W30c's core result (nothing reads it) stands with the denominator corrected;
  the field is **36/36 UNEVAL**.
* ⚠ **Do the grep per artifact, never per field name.** `verified_by` is ENFORCED in
  `graph/requirements.json` (`systems_check.py:374,1006,1220,3939,3954`) and UNREAD for all 90
  occurrences in `citation-provenance-ledger.json`. A name-level census overstates coverage.
* ⚠ **Use a key-literal grep, not a substring grep.** Substring `verified` returns 5,088 hits,
  almost all prose; `[\"']verified[\"']|\.verified\b` over `*.py *.mjs *.sh *.yml` returns 86.
* **Four fields are called load-bearing by committed prose and read by nothing** (W30c found one):
  registry `verified` (36), `open_access_full_text_retrieved` (58, 38 of them `false`),
  `read_level` (16), `figure_checked` (17).
* ⭐ **The repository already identified this class itself and answered it once.**
  `research/modalities/emc_ipd_survival.py:220-228` states that *"an eye reading recorded in a JSON
  field is unfalsifiable: nothing in the repository could disagree with it"* and records that on
  2026-08-27 every such reading was re-taken by an instrument (`km_risk_row_detect.py`) that measures
  band structure and can return present/absent/undetermined, agrees with the human reading on all
  nine KM figures, and is shown capable of the other answer. Cite that precedent rather than
  proposing a new instrument.
* An unread field is **undecidable, not false**. No worker has opened any link; every `verified: true`,
  `accessed` and `figure_checked: true` value is UNKNOWN.

### Eight measured results — 2026-09-08T04:43Z. Take these as given.

* **No campaign citation is broken (W50).** Complete census over 199 reports: 1,811 line-bearing
  citations, 500 distinct cited files, **19 disagree line-for-line** between live and corpus (18
  line-shifted, 1 append-only), **67 distinct affected citations across 19 reports**. Every one was
  written from the live checkout and still resolves there as written; 64 of 67 also survive at a
  *different* line in the corpus — which is the silent hazard, not a citation defect. 87 of 97
  affected occurrences are in just three files: `systems/systems_check.py`,
  `systems/views/L3-publications.md`, `systems/graph/publications.json` — **resolve those in the live
  tree only.** The one row worth a human note: W09f's `L3-publications.md:96` is the sole citation
  whose corpus-side text has no live counterpart (W09f's own claim is intact).
* **`[B5]` is a five-member family (W31e).** Checks whose message claims about a field they never
  dereference: `[B5]` (6/6 records), `[B6]` (over-counts "with a document" 30 vs a true 26),
  `[B3]` (blind to 15 blockers named across 23 publications' `blocked_by`), `[L5]`, `[B9]` (says
  "12 trigger(s)" for 12 *pairs* across 11 triggers). All in one seam: `publications.json` models
  `blocked_by`/`why_not_written`/`document` and the checks read `state`. **No sixth instance exists**
  among record-reasoning checks — do not re-census. ⚠ Also: `[B1]`–`[B5]`, `[P1]`, `[K1]`, `[K2]`,
  `[X1]`, `[X4]` are each emitted by **two different functions**; a bare code is ambiguous.
* **The `systems_check.py` anchor census is complete (W37c).** 72 code literals, 89 (code, function)
  pairs: **2 VIEW-anchored, 35 GRAPH-only, 28 CROSS, 24 NON-GRAPH.** Emptying the graph silences the
  35 without needing the regenerator at all; among CROSS families **direction decides** — "present in
  the other home, absent from the graph" survives (`[L2]` 89, `[M2]` 16, `[W1]` 18), the reverse goes
  vacuous. ⛔ **Named hazard:** giving the regenerator ownership of
  `research/manuscripts/emc-systems-map.json` would make 89 of the 123 surviving errors escapable, and
  it is the cheapest-sounding change (that file has **no** generator today — the roadmap and plan
  extractors both run the *other* direction, and `extract_requirement_register.py` says so in its own
  docstring: *"THE ROADMAP IS THE SOURCE, ALWAYS … never writes in the other direction."*). Also:
  `--write-views --check` in ONE invocation skips `check_views` entirely (`:4568`), as does
  `--no-view-check`.
* **The regenerate-then-check escape is a real class (W45).** 26 modules enumerated (10 with an
  explicit write flag, 17 whose regeneration mode is the *bare* invocation and `--check` is the added
  flag); 10 tested by execution. **4 fully escape** — `emc_systems_map_check`, `emc_fet_idr_census`,
  `atm_status_atri_stratification`, `emc_atr_vulnerability` (the last still emitted a scientific
  verdict string and was certified `REPRODUCES` after 102,397 rows were removed from its inputs
  cache, on a scratch copy — the live cache is populated and green). The discriminator is
  **three-valued**: a cross-source anchor blocks it, an *in-source constant* blocks it
  (`lint_readability` splits cleanly: its baseline-anchored errors dissolve, its 60-word-sentence
  errors survive, exit stays 1), and an accidental crash blocks it (`emc_fet_frame_and_composition`
  raises `KeyError`). A cross-source anchor is **sufficient, not necessary**.
* **POLICY-evidence enforcement, measured by mutation not by reading (W48).** 41 mutations against
  `validate-registry.mjs` on a sandbox copy: of 31 decidable predicates, **11 ENFORCED-AND-FALSIFIABLE,
  4 WARN-ONLY, 3 ENFORCED-VACUOUSLY, 13 UNENFORCED**. `systems_check.py` enforces **none** of the 16
  units (its only 4 references are the `[P1]` gate-ordinal documentation check). Independently
  confirms the `:115` falsy-index defect W30d found. Vacuous rows: §2.1(2) integer-ness (`3.5` is a
  `number`), §3's "≥2 positions" (one `mixed` satisfies it), §2.3 for `cohorts[0]`. ⚠ Also measured:
  the `dataStatusBanner` ERROR fires only when `dataStatus === "SAMPLE_SYNTHETIC"`, so deleting the
  banner outright on the live `partial-curated` registry is a **silent pass**.
* **`pinned-figures.json` has no unread entries (W47).** 183 entries: **160 ENFORCED, 23
  READ-BUT-NOT-COMPARED, 0 UNREAD**; 18 consumers enumerated at their use sites. The 23 are
  `superseded` patterns matching nothing in any of the 29 targets — and unlike `subset_checks`
  (`lint_consistency.py:571-578`, which errors when a pattern matches nothing), the superseded arm has
  **no anti-inertness alarm**. ⚠ `.github/workflows/nr4a3-covalent-handle-ensemble.yml:88` runs the
  gate under `|| true`, discarding the verdict.
* **`lint_consistency.py` is a numeric-registry conformance checker, not a manuscript linter (W51).**
  No glob and no directory walk exist in it; every file it reads is a literal path in
  `pinned-figures.json`. Union file set: **31 paths, 16 of them `research/manuscripts/*.md` — 171 of
  187 tracked manuscript `.md` files (91.4%) are outside every rule.** Six injections on a scratch
  copy: a contradicted pinned value at a declared context is CAUGHT (exit 1) and an unmarked
  superseded value is CAUGHT (exit 1); the same quantity stated at two different values is NOT caught,
  a dead anchor/dead link is NOT caught, a pinned-value contradiction stated outside the declared
  `context` is NOT caught, and both caught kinds are invisible one directory over. **`0 ERROR across
  29 target file(s)` is a true statement that reads as a much stronger one.**
* **The `[X4]` backlog is characterised for human triage (W46) — 301 ungraded signals, and nobody
  should try to shrink it by deduplication (the available saving is 3 rows).** It arrived in five
  batches; 130 queued 2026-08-08 and untouched, 111 queued 2026-09-04 (37% of the "backlog" is one
  week old). 301/301 carry a resolvable identifier; **126 have an abstract already committed** in
  `research/method-watch-trigger-hits.json`, 175 would need a retrieval. ⭐ The high-leverage tail is
  **8 signals under 20 routes**: `TECH-EMC-MODEL-ACCESS` (1 signal, 10 routes),
  `TECH-EMC-EXPRESSION-DATA` (2, 9 routes), `TECH-CLOUD-WET-LAB` (1, gates a *ready* route),
  `TECH-COFOLD-ASSEMBLY` (3, 5 routes), `TECH-CHARGE-CHANGE-FEP` (1). ⚠ `TECH-CONDENSATE-RESOLUTION`
  is 34 signals — 11% of the backlog — against a technology the graph records as unblocking **no
  route, no blocker and no requirement**. Grading is reserved to a human (`MAINTENANCE.md:74`); no
  worker may grade a signal.

### Six more measured results — 2026-09-08T04:46Z. Take these as given.

* ⛔ **The routed-conflict surface is a fifth the size the index claims (W49).** Of the 20 "conflicting
  pairs", only **19 are enumerable** (W36's table sums to 15, not the 16 it states — the 16th is
  unrecoverable, UNKNOWN). Adjudicated against the tree: **7 are not conflicts at all** (five turn on
  one line of `scripts/tier-budgets.json` — `research/modalities/tests` is the `modalities` tier, NOT
  `commit-loop`, and W27's hold names only `commit-loop`), 5 reduce to ordering or a stated
  complementarity, 4 are a successor correcting a predecessor, **0 are A-CORRECT**, and exactly
  **one — R07 vs R08 on `emc_fourth_cohort_quant.py` — is a genuine forced either/or** needing an
  owner ruling. ⚠ Measured: `commit-loop` is **1466/1500** (headroom 34), not W27's 1497/1500
  (headroom 3) — an 11-fold difference in the quantity W27's hold rests on; the gap is unexplained.
  ⚠ Both published repair diffs are **not machine-applicable**: W14c's R07 fence opens directly on
  `@@ -567,7 +567,7 @@` with no `--- a/`/`+++ b/` header, and W14d's R08 headers are abbreviated
  prose. "Land the report's bytes" is not an available instruction for either.
* **The AUT-PD-186 xdist corruption does not reproduce (W54).** `pytest test_endpoint_producers_check.py
  test_endpoint_logic.py test_endpoint_manuscript_figures.py -n 3` → **70 passed, exit 0**, tree clean.
  Repository-wide census of 649 tracked test files: **612 CONFINED by an enforced runtime guard**
  (`research/manuscripts/tests/tracked_tree_guard.py`, a `sys.addaudithook` refusing any write to a
  `git ls-files` path, bound in three `conftest.py`; its `ALLOWED` dict is **empty on purpose** — zero
  declared exemptions), 36 CONFINED by hand-audit, **1 IN-PLACE** —
  `scripts/tests/test_a_promise_with_no_commit_stops_the_turn.py`, whose target is inside `.git/` and
  is therefore not a committed artifact. ⚠ **Three stale module docstrings describe the retired
  in-place design while the code beneath is `tmp_path`-confined**:
  `test_endpoint_producers_check.py:9-11`, `test_emc_fusion_partner_pooling_check.py:85`,
  `test_emc_systemic_therapy_pooling_check.py:80`. This prose has already caused two workers to refuse
  to run a safe file. **Read the code, never the docstring.** ⚠ `scripts/tests` (21) and `systems/tests`
  (16) have **no guard installed at all**.
* **The 18-row vacuous-pass census is closed at 4 of 18 (W44)** — rows 11, 16, 17, 18 — now measured for
  every row by execution rather than argued for thirteen. Each row's minimum input set was measured at
  runtime with a `sys.addaudithook`, then emptied in a scratch copy. Rows 1-10 and 12-15 go red, but by
  **three different mechanisms**: 9 REFUSE with a purpose-built message (rows 14 and 15 name the
  emptiness in the sentence they print), **4 CRASH with an uncaught exception** (5, 9, 12 → `KeyError`;
  7 → `GeometryError`), and row 13 refuses through a different guard than its own comparison. In the
  crash cases the operator is told `STALE … rerun and commit`, which is wrong advice for an empty input.
  ⚠ **Row 17 (`citation_debt.py`) is the one exposed row**: 4 records, no writer anywhere in the tree,
  and `rows: []` prints *"every declared destination is decided and every discharge verified"*. Row 16 is
  39 triggers, row 18 is 47 items, and row 11's vacuous state is not live at this HEAD.
* **`modalities.json` coverage resolves W26d's UNKNOWN two ways (W52).** The four `.rationale` fields
  ARE covered — `systems/tests/test_modality_census.py:308` iterates every row with no route or verdict
  gating and catches claim language the renderer never prints. The two `requires[0]` fields are covered
  by **nothing but a schema length floor**. ⛔ Measured by mutation: the string *"the tumour is safe and
  this cures it"* placed in `MOD-ARGININE-DEPRIVATION.requires[0]` **passes the entire suite and the
  schema** — the guard's field list is `("rationale", "zero_dollar_next_step", "name")` and omits
  `requires` and `exemplar`. Unread by any executable: `level`, `kind` (both `const`, harmless) and
  `requires` — substantively **1 of 15 content-bearing field names, 2,883 bytes, 1.54% of the file**.
  A named human reviewer is still required for all six: the regex catches one class of overclaim and
  cannot see a false absence, a wrong direction of effect, or a stale citation.
* **The pooler's arithmetic is correct and its policy conformance is not the same question (W53).**
  `research/meta/meta-analysis.mjs` regenerates `results.json` byte-identically, and an independent
  Python reimplementation of every published estimate, interval, weight, τ², I², Q, leave-one-out range
  and sensitivity subset agrees to **1.42e-14** — machine roundoff. Per-sentence against POLICY-evidence:
  1 EXACT, 1 EXACT-by-omission, 5 WEAKER, **1 STRONGER**, 8 NOT-IMPLEMENTED. ⭐ §2.1(3)'s guard exists
  (`:36`) and fires — but it is one string literal (`stage === "distant"`) for one metric with no
  vocabulary check: respelling the same cohort's stage as `"metastatic"` admits a structurally-100% row
  and metastasis goes 37.9% → 42.7% with **I² collapsing 69% → 0%**. §2.2 is not implemented here at all
  (no Wilson anywhere in the module — the manuscript uses DerSimonian–Laird by the policy's own
  carve-out); had §2.2's arithmetic been used the recurrence interval would be **3.3× narrower**.
  ⚠ The one live policy-vs-artifact contradiction: §2.2 says *"we do not compute I²"* and `results.json`
  publishes three of them. Also latent: `:32` filters `c.pool !== false`, so a cohort with **no** `pool`
  key is pooled by default, and `:38` tests only `if (mm && mm.denom)`, so `events: 3.5` runs clean and
  moves the recurrence headline 27.8% → 22.0%.
* **Self-defeating remediation advice is 1 of ~48 (W34c).** Of ~48 advice-bearing gate-failure messages
  in 46 modules, 38 `--check` gates were executed: **31 green, 4 red, 3 UNKNOWN** (blocked Ensembl
  egress — a 403 at the proxy is not a measurement). Of the four reds, exactly **one is LOSSY in the
  destructive sense**: `aso_control_oligos.py:153`, whose advised re-run would revert
  `_not_a_claim_of_inertness` from *"CLEARS the same specificity screen"* back to *"FAILS"* and delete
  the artifact's own dated record of the 2026-08-30 correction. `aso_archive_manifest.py:1970` is SAFE
  (the only differing leaf is `.git_revision`). `build_aixiv_metadata.py --paper fusion-output` and
  `emc_fusion_frame_figure.py` would overwrite committed bytes, but there the committed side is the
  stale side and the module documents regeneration as the correct fix. ⚠ **The distinguishing property
  is not the message wording** — ~30 modules share the boilerplate — **but whether a hand-applied
  correction was ever carried back into the generator.** Separately, for the manuscript owner:
  `nr4a3-fusion-transcriptional-output-aixiv-metadata.json` currently publishes a *wider* claim
  ("three cohorts on three platforms") than its own manuscript ("the two readable array platforms").
