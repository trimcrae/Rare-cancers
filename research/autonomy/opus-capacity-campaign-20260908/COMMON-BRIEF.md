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

### Two more measured results — 2026-09-08T04:50Z

* **The citation ledger's `status` vocabulary is UNDECIDABLE (W55).** 237 entries, 17-key union,
  11 keys distinguishing `unverified_at_baseline` (143) from `verified` (93). **Exactly one code file
  names the ledger path at all** — `research/manuscripts/lint_citations.py` — and its exit code is a
  function of ledger **membership only** (`:432` builds `known` from `e["key"]`; `:443` computes `new`
  from that). `status` is a RENDER, not a READ: the two readers are a vocabulary-membership assert and
  a `Counter` interpolated into a printed line. Relabelling all 237 rows `verified` by hand would change
  one console line and no exit code. `retracted` is in `STATUSES` with **0 rows** and no branch.
  ⛔ **The transition mechanism the artifact prescribes for itself does not exist**: the ledger header
  and `lint_citations.py:36,371,493,508` all say resolve a row *"with `--verify-online` … never by
  relabelling it by hand"*, and the argparse block at `:545-547` defines only `--baseline` and
  `--report`. There is no `--verify-online` anywhere in the tree. The two workflows named inside
  `verified_by` values contain zero references to the ledger. ⭐ Refinement to W43: five verified-only
  keys are **content**, not act-assertions, and are decidable in principle from committed bytes — all
  11 `verified_pmid` values appear in `research/manuscripts/citation-retraction-sweep.json`. Nothing
  here says any row is mislabelled; no link was opened.
* ⛔ **The ASO deposited-chain guard is GREEN and the four-artifact gap is genuinely unwatched (W03j).**
  `pytest research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py` → **10 passed,
  exit 0**. The blind spot is at `:218-233` and `:240`: the resolver's `ev()` handles `Constant`, `Name`
  and a restricted `Call`, and **returns `None` for `ast.Tuple`/`List`/`Set`/`Dict`**, so a module-level
  *container* of path strings never becomes bindings. Measured by calling the shipped helper on the
  shipped module: `_module_level_paths(aso_sequence_manifest.py)` returns only `OUT_CSV` and `OUT_FASTA`
  — both **outputs**, which `:311` skips — so the guard extracts **zero inputs** from the one chain step
  this is about and passes vacuously. ⚠ **A second, disjoint escape route**: `:293` iterates
  `_invoked(_script())` only, so deposited-but-not-chain-invoked modules are never opened —
  `aso_taf15_intron2_designs.py`'s `GENOME_SCREEN`/`PREMRNA_SCREEN` **are** resolvable and point at
  existing undeposited files, and the guard simply never looks. AST census: 8 deposited modules use the
  container idiom; only `aso_sequence_manifest.py` currently hides an undeposited artifact from a
  chain-invoked step. W03i's two UNKNOWNs are settled: both `aso-genome-offtarget-taf15intron2.json`
  (opened at `aso_taf15_intron2_designs.py:404` via an f-string path) and `junction-aso-offtarget.json`
  (opened at `junction_seam_retraction.py:431,434-435` via a glob) are **OPENED, not merely mentioned** —
  but both opens are absence-tolerant, unlike the premrna four's deliberate no-`try/except`.

### The 40 `--write-views`-invisible fields have their consumers mapped — measured 2026-09-08T04:48Z

W09j searched all 40 of W09i's (collection, required-name) pairs across `systems/`, `scripts/` and
`research/`, reading every non-trivial hit and attributing it to a collection: **10 read by another
executable, 30 named only by their JSON Schema `required` declaration (and prose), 0 unreferenced.**
The (c)=0 is by construction — being `required` is what put them on the list — so **the substantive
number is 30**: for three quarters of the set, `check_schemas` in plain mode is the only thing that
reads the field at all, and its *content* is unverifiable by any executable in the tree.

The 10 split three ways, and only three are load-bearing outside `systems_check.py`:
`modalities/revisit_trigger` (`systems/tests/test_modality_census.py:175`), `technologies/paper_id`
(`scripts/trigger_scan.py:785,795`), `publications/kind` (`claim_coverage.py:141` +
`test_the_census_reads_every_publication_endpoint.py:104`). Four more are one mechanism —
`file` in instruments/lanes/requirements/strategies is read by `check_pointers` `[P1]`/`[P2]`
(`systems_check.py:700` → `:714`, via `_owner_blocks`, which yields **every dict at any depth carrying
a string `file`**), a **plain-mode** gate that never runs under `--write-views`: deleting the field
does not fail it, it makes it silently check fewer pointers. The last three (`routes/title`,
`requirements/title`, `blockers/why`) are read by `research/manuscripts/lint_asymmetry.py:507,557`
**value-generically**, and ⚠ that linter is wired into no gate at all — not `scripts/preflight.sh`,
not `scripts/fast_checks.py`, not `.github/`; its only executable exercise is its own test against
`tmp_path`.

⚠ Two fields are mentioned **nowhere** in the repository outside `systems/graph/` and their own schema
file: `publications/posted_by` and `instruments/module`. Required, stored (1 and 32 instances), never
mentioned again.

⚠ Beware name collisions when auditing graph fields: `kind`, `level`, `owner`, `provenance`, `status`,
`title`, `file`, `why`, `last_verified`, `confidence` and `closure_kind` all collide across collections
and against document frontmatter. W09j's disambiguation method is the one to reuse — map each hit line
to its enclosing top-level `def`, then extract which `g["<collection>"]` keys that function actually
indexes. Raw hit counts are not evidence.

### Six more measured results — 2026-09-08T04:52Z. Take these as given.

* ⛔ **W37c's escape prediction is CONFIRMED by execution (W61): 18 ERROR, all `[W1]`.** Green baseline
  reproduced a fourth time (campaign directory outside the scan root → `0 ERROR · 87 WARN · 7 INFO`,
  exit 0). Emptying the 15 graph collections → 136 (`[L2]`89 `[W1]`18 `[M2]`16 `[G2]`13); `--write-views`
  → 123; **additionally emptying `emc-systems-map.json` (187 records) and the 16 `**R<n>**` roadmap rows,
  then both modules' own remedies → 18, 100% `[W1]`, no new family.** So **105 of 123 surviving errors
  are removable by editing a second home in the same commit**, and the `LANE-n` filesystem sweep is the
  only anchor left standing. That is an argument for *not* giving it a generator. ⚠ Incidental and
  important for anyone diffing two `systems_check` transcripts: the `[L4]` WARN block is emitted from a
  `set` difference, so **its order varies between processes** — sort first or pin `PYTHONHASHSEED`, or
  you will read nondeterminism as drift.
* **The stale-watcher class has at least 104 members and 3 measured STALE (W57).** Of 13,506 string
  leaves in `systems/graph/`, 104 fields state a quantity about a named JSON artifact outside the graph;
  31 resolve to a comparable live value: **24 AGREES, 3 STALE, 4 UNCHECKABLE**. New beyond W26d's seed:
  `objects.json OBJ-LINE-HEMCSS.notes` says a **30-entry** `read_by` sweep where `emc-systems-map.json`
  carries **114** (and that sentence's own argument is that the graph must not hold a second copy);
  `routes.json` route 81 attributes **162** to "death-cue sentences" where 162 is the *paper* count and
  the sentence count is 577. ⛔ **A number-presence grep cannot detect this class** — W57 measured that
  such a screen grades W26d's known-STALE case as corroborated. Resolve the key, never the number.
  29 of the 31 sit under a key literal some executable contains, and **not one executable anywhere opens
  the cited artifact and compares** — readership is not checkability.
* **Manuscript-linter coverage splits by defect class, not by gate (W59).** `lint_citations.py:187` uses
  `git ls-files --cached --others --exclude-standard` and covers **187/187** manuscripts; every other
  prose gate is list- or model-scoped — `lint_claims` 36, `lint_submission_residue` 34,
  `lint_consistency` 16, `lint_style` 13. **Union: 41 of 187 (21.9%); 146 manuscripts are in none.**
  Verified by paired injections (byte-identical text in a covered and an unlisted file): a fabricated
  PMID/DOI in an unlisted manuscript is CAUGHT; banned phrases, over-claiming and AI-residue are caught
  only inside the set. ⭐ `lint_claims.py:249-252` is the repository's own statement of the principle —
  *"coverage must follow the model, not a list someone remembers to extend"* — applied to
  `systems/views/` and publication endpoints and **not** to the manuscript corpus. ⚠ Methodological:
  a `lint_style` injection appended at EOF is not caught even in a covered file; inject after a `##`.
* **The shrink-vs-growth asymmetry is a property of *inclusion* registries (W64).** 15 registries
  classified: **4 are shrink-guarded but not growth-guarded** (`pinned-figures` `targets` and
  `must_appear_in`, `lint_style.TARGETS`, `parser_guard`'s graph list). Exclusion lists (`DOC_SKIP`,
  `ID_SKIP`, `TRANSIENT_DIRS`) do not exhibit it — opt-out means growth is covered by default — and
  model-derived or walk-derived sets (`lint_claims` 137 effective, the preflight-gate enumeration
  `[P1]`, the residue/readability baselines) are growth-guarded by construction. ⚠ `lint_style.TARGETS`
  covers **8 of the 26** `publications.json` `document.file` entries, and `lint_readability.py:297` and
  `lint_submission_residue.py:225` both re-use that one list, so its gap propagates to three gates.
  ⚠ `artifact-refs.json`'s own `_why` claims *"It cannot silently grow"* — measured, it grows with a WARN.
* **A green push/PR CI run proves 20 of 36 preflight gate units (W63).** Of 176 workflows, **exactly one
  (`tests.yml`) is a general push/PR gate**, and it has no `|| true`, no `continue-on-error` and no
  pipeline on any gate step. ⚠ Its `push:` is pinned to `main`, so **a push to this campaign branch
  triggers no workflow at all.** 14 gate units are NOT-IN-CI on any trigger — including
  `node scripts/validate-registry.mjs` (the clinical registry's only evidence-contract gate, running on
  **zero** triggers), `receipt_schema --check`, `contract_check --check`, `derived_ids --check`, and 10
  of the 18 generator `--check`s. The 7 `|| true` call sites all live on manual or feature-branch
  workflows, so W47's finding weakens no push/PR gate; both workflows that run `preflight.sh` handle its
  exit code correctly (`PIPESTATUS`/`set +e` + a final `exit 1`). Green preflight and green CI are
  **overlapping, not nested** — `tests.yml` also enforces ~25 checks preflight never runs.
* **The `km_risk_row_detect.py` precedent holds up (W65).** It measures band structure beneath a figure's
  axis — nothing lexical — and the recorded claim is verified: **9/9 agreement** with the human reading
  across the nine KM figures (2 `present`, 7 `absent`, 0 `undetermined`), and the control reproduces
  8/8 separations, exit 0, including the two mutations that would make a structural rule useless.
  ⭐ The strongest single row: on `morioka2016trabectedin` the text arm recovered the risk row's **values**
  `['5','5','5','3','3','1','1','1']`, byte-identical to the eye reading transcribed two days earlier —
  an independent second reading by a different method. ⚠ Scope: `present` is a statement about a
  **graphic**, never about survival, and it says nothing about whether any digitized coordinate is right.
  ⚠ The instrument's own input provenance is currently unfalsifiable here: its recipe names
  `origin/literature-cache` at `cache_commit 454df711…`, and that ref does not exist in this checkout.

### Two more measured results — 2026-09-08T04:53Z

* **`is_cleared` is characterised (W56).** Three disjuncts: a 28-char same-line NEGATOR lookback, a
  PROXIMITY window (±2/±1 lines, ±200 chars, ATX-heading lines blanked length-preservingly except the
  match's own), and an unbounded HEADING-aboutness scan. **No entry identity is passed to `is_cleared`
  at all**, and marker matching is bare case-insensitive substring — so a marker for supersession A does
  clear a match for supersession B, demonstrated end-to-end with the real linter plus a negative control.
  Path split over the 246: PROXIMITY 220, HEADING 17, NEGATOR 9; a total regression un-covers **58
  entries / 246 occurrences at once**, the proximity limb alone 193. Slack: 44 unbounded (heading path),
  202 finite with median **160 chars** and a minimum of **7**; 96 of 220 rest on a single marker
  occurrence and **25 of 246 rest only on an ordinary English word** (`carried`, `once `, `previously`…).
  ⚠ `_WINDOW_CHARS` has **13 characters of margin** against its own regression test — widening 200→213
  re-admits the measured 2026-08-05 false clear with the suite still green. ⛔ Two defects found:
  the 2026-08-05 heading-blanking narrowing **does not see setext headings** (`## X superseded` correctly
  fails to clear; the same words underlined with `---` do clear), and `check_superseded:604` uses
  `rx.search` — **first match per line only** — so 77 registered occurrences on committed target lines
  are never examined, **4 of them uncleared** (`pricing.md:246` ×3, `degrader-paper-schedule.json:292`).
  The tree exercises 323 occurrences, not 246; fold that into any future inertness question.
* **The ASO guard's second escape route is the larger surface but the milder defect (W66).** Measured
  from the shipped helpers: the manifest deposits **77 `.py`**, `_invoked(_script())` covers **29**, so
  **48 (62%) are never opened by the guard** — and on 34 of them the resolver has no blind spot at all,
  it simply is never asked. Replicating the guard's exact filter chain over those 48 yields **3 modules,
  6 artifacts: 5 genuine undeposited inputs + 1 false alarm.** ⚠ Severity is lower than route 1's:
  none of the three is chain-invoked, so none of these reads happens when a reader runs
  `regenerate_aso_chain.sh`. Route 1's four remain the sharper defect. ⛔ A **third** limitation, new:
  `_names_opened_for_writing` (`:333-336`) records only `open()` whose first arg is a module-scope
  `ast.Name`, so `junction_sirna.py` — which writes through a **local** `out` while naming the same file
  in a module-level `OUT` — is classed as reading an input it actually creates.

### Three more measured results — 2026-09-08T04:55Z

* **The opt-in tiers DO cover much of what W48 called unenforced (W60), and 12 mutations decide it.**
  Baseline `146 passed, exit 0` across 7 modules. **7 predicates are COVERED-AND-FALSIFIABLE** in an
  opt-in tier (§2.1(3), §2.2-Wilson, §2.6(g), §2.6(h), §2.7-risk-table, §2.7-provenance, plus the §2.4
  cross-anchor guard — each verified by defanging the guard and watching exit 1). **2 are
  COVERED-VACUOUSLY** and **2 are GENUINELY-UNENFORCED-ANYWHERE**: §2.2's *denominator-weighting*
  (pooled p̂ silently replaced by an unweighted mean → 23 passed, exit 0) and **§2.3 across-study**
  (two cohorts sharing `populationKey`, both `pool:true`, summed to 38/211 with `cohorts_excluded={}`;
  `pool()` has no overlap logic and no test asserts one). ⛔ The sharpest measurement: the **same** §2.4
  violation exits 1 when the artifact is stale and **exit 0 when the artifact is regenerated from the
  mutated generator** — an executed instance of W45's regenerate-then-check escape. `test_nothing_is_pooled`
  checks only for the literal keys `pooled_median`/`combined_median`, so a merged time-anchored figure
  under any other key name passes. ⚠ Also measured: **15 files each define their own `wilson()`**; the
  closed-form control guards one, an identity assertion binds a second, and thirteen are unexercised.
* **The 23 inert `superseded[]` entries adjudicate 19 CORRECTLY-INERT / 4 SILENTLY-INERT / 0 UNDECIDABLE
  (W62).** Whole-repository scan of 7,604 files with the compiled patterns, campaign directory excluded.
  The four, by three distinct causes: `aso_thermo_cross_margin_discordance` is unreachable **inside a
  target file** purely because the pattern straddles a soft wrap (`check_superseded` is line-oriented;
  measured — per-line match False, joined-with-previous True); `vaccine_coverage_wilson_intervals` and
  `vaccine_e7_coverage_stated_without_a_panel` are printed as **current** in
  `fusion-junction-neoantigen-paper.md` and the modality census, files no rule scans; and
  `realised_spend_omitted_the_selcal_lane`'s retired **$126.17** survives **inside `pinned-figures.json`
  itself** (`:1848`, `:1854`) against a live artifact reading `$133.38`. ⚠ Standing caution for W47's
  alarm proposal: **19 of 23 are inert for the right reason**, so a blanket ERROR would redden 19 correct
  rows to surface 4. A WARN-level census with repo-wide hit counts surfaces all four at no cost.
* **The manuscript quotes both pooling methods correctly, and the mis-citation hazard does not exist in
  the corpus (W68).** `research/manuscripts/endpoint/meta-analysis.md` is the **only** document printing
  any of the three headline pools; it headlines DL (28% / 14–47% / I²=90%) and prints crude+Wilson
  (27% / 22–32%) in a separately labelled column, with its §2 Methods stating the arrangement in advance.
  `emc-locoregional-eligibility.json` uses crude+Wilson and names its estimator, its § numbers **and the
  pooler it deliberately did not use**. W53's null grep is explained: the manuscript rounds to whole
  percents, and `research/manuscripts/*.md` does not glob `endpoint/`. ⚠ `pinned-figures.json` pins
  **none** of these values — `meta-analysis.md` is not among its 29 targets, and the file contains 0
  occurrences of `recurrence`, `metasta`, `diseaseDeath`, `meta-analysis`, `results.json` or
  `DerSimonian`. Combined with W30c's "no gate runs the pooler", the DL figures are unpinned, unlinted
  and unregenerated by any gate. ⚠ One measured non-reconciliation: `meta-analysis.md:136` prints the
  disease-specific-mortality crude cell as `14% (n=266)` where the summed denominator is **262**; the
  percentage is right, the source of the 4 is UNKNOWN.

### Two more measured results — 2026-09-08T04:57Z

* **The 36 hand-audited test files are now executed, and the tracked tree stays clean (W70).**
  `pytest scripts/tests systems/tests -n 3` in a `cp -a` copy: **685 collected, 673 passed, 11 failed,
  1 skipped, exit 1** — and scratch `git status --porcelain` is **empty before and after**. All 11
  failures are the campaign footprint (`[D1]`/`[D4]` missing frontmatter over collected reports, the
  `[D6]` `DOC-AUTONOMY-OPERATING-PROTOCOL` id collision, `[K1]`/`[K2]` dangling links inside campaign
  reports, plus W41's predicted tier-budget failure). ⚠ `test_repo_state_is_clean` is **not** a
  working-tree check — it asserts `run_checks(graph).errors == []`. ⭐ The run was **not inert**:
  `.git/emc-hooks/promised-work-last-head` changed (`063f00fa…` → the scratch HEAD), written both
  in-process by `scripts/tests/test_a_promise_with_no_commit_stops_the_turn.py:65,84,185,201,210` **and**
  out-of-process by `.claude/hooks/promised-work-at-turn-end.sh:107` — a measured instance of the
  subprocess route the in-process audit hook structurally cannot cover, on a git-internal path that
  `assert_tree_unchanged()` cannot see either. **Neither half of the guard design covers this write.**
  ⚠ That test's `:210` comment says *"leave the baseline as we found it"* but writes `_head()`, not the
  original bytes. ⚠ Two snapshots cannot see a write-then-revert **window**, which is the actual shape
  of the AUT-PD-186 defect — this upgrades the 36 from source-reading to no-residue, not to never-touched.
* **The four invisible `file` fields carry 13.89% of all pointer verification (W71).** Measured by
  instrumenting the shipped `check_pointers` from outside (counting `os.path.exists` calls and
  `anchor_resolves` calls; the module was never edited): baseline **723 `[P1]` + 184 `[P2]` = 907**
  pointer checks, 0 errors. Deleting `file` costs **instruments 62** (32+30), **requirements 32**
  (16+16), **lanes 18**, **strategies 14** — total **126 checks, 11.07% of existence checks and 25.00%
  of all anchor checks**, with `check_pointers` still reporting 0 errors in every case. ⭐ Refinement to
  W09j: in **plain** mode the deletion is not silent overall — `check_schemas` fires 14–32 extra errors.
  The genuinely silent configuration is `--write-views`, where neither check runs. ⚠ The schema code
  differs by collection (`[S1]` for strategies, `[S3]` for the other three) — do not key a census on one
  code. ⚠ Methodological trap W71 hit and corrected: wrapping `_owner_blocks` itself **over-counts ~2.7×**
  because it recurses through the global name; count `os.path.exists` instead. ⚠ Nothing in the tree
  records how many pointer checks a run performed — the summary line prints objects/ERROR/WARN/INFO only,
  so a run verifying 781 pointers and one verifying 907 print an identical story.

### Four more measured results — 2026-09-08T04:58Z

* ⛔ **ESCAPE HOLDS WITH GIT (W74).** W45's UNKNOWN is settled. In a `.git`-present scratch copy where
  `origin/main` resolves (`0dcb24c0`, a different commit from HEAD), `[C1]` and `[O4]` are **live and
  passing, not unavailable** — the green baseline prints **0 WARN** — and the same three steps still end
  at **exit 0 over 0 registry items, 0 ERROR, 0 WARN**. Mechanism, located: both checks are anchored in
  another home but **iterate collections inside the emptied file** (`emc_systems_map_check.py:655`
  `for c in m.get("claims", [])`; `:405`/`:510` returns before `_tracked_files()` is called). ⭐ This
  refines the discriminator to a fourth value: **a cross-source anchor blocks the escape only if the
  loop is driven from the non-emptied side.** ⚠ Also measured: **removing `.git` HIDES 5 real `[O4]`
  errors** — a git-less `--check` is a weaker gate than CI runs, and W45/W37/arm-C all ran that weaker
  one. Those 5 are this campaign's own footprint (five reports naming `H-EMC-SS`/`HEMCSS`/`ACH-001519`).
* **5 of 33 dedicated checkers are invoked by nothing — 15.2% (W72).** Three are new beyond W09j's and
  W30c's: `research/manuscripts/fet_notice_sync_check.py` (**exit 0**),
  `research/manuscripts/figures/check_figure_specs.py` (**exit 1, `ModuleNotFoundError: PIL`** — a
  container gap, not a content defect), and `scripts/validate-research.mjs` (**exit 0**, 14 candidates,
  1 WARN). ⛔ `validate-research.mjs` is not merely unwired but **documented-out**: it is the only entry
  in `fast_checks.py`'s `EXCLUDED` block whose comment does not name a covering surface — its three
  siblings' comments all do. `lint_asymmetry.py` is invoked-but-never-aimed (its suite runs on
  `tmp_path` corpora only, by its own docstring). ⚠ A fifth real gate exists outside the four surfaces:
  `core.hooksPath` **is** `.githooks`, and `.githooks/pre-push` runs `push_guard.py` and
  `prepush_ledger_guard.py`. ⚠ Grep traps recorded: `fast_checks.py:100-108` names four checkers inside
  an **`EXCLUDED` tuple** that greps identically to a run; `preflight.sh:7` names a gate in a header
  comment; and a `grep -v "/<basename>:"` self-filter silently deletes `tests/test_<basename>:` lines.
* **The ledger's five content fields: 157 AGREES / 0 DISAGREES / 41 NOT-CARRIED / 4 NULL over 202
  instances (W67).** W43's and W55's undecidable class shrinks by 157. ⚠ **75% of the title
  corroboration is a transcription check, not an independent one** — 58 of 77 come from
  `lit-targets-degrader-citations.json`, which the ledger itself names as the record it was copied from;
  only 19 come from seven other artifacts by different routes. ⚠ Sharpening of W55: only **3 of 11**
  `verified_pmid` values appear in an object that also carries the row's own identifier; the other 8 sit
  in `citation-retraction-sweep.json` as standalone swept ids with no DOI, title or year, so the
  DOI↔PMID linkage is asserted by the ledger and nothing else. ⚠ `verified_pmcid` has **0 AGREES and no
  exercised path** — no positive control is possible for it. The instrument was shown capable of the
  other answer on 4 of 5 fields via mutated scratch copies. Also: 8 works cited only from
  `research/method-watch-autonomy-prior-art-2.md` are the ledger's entire uncorroborated surface, and
  `research/modalities/e3-provenance-correction.json` is **tracked, named `.json`, and not valid JSON**
  (Python-style adjacent-string concatenation at `:21-26`).
* ⛔ **The fetch contributes nothing to any of W34c's three UNKNOWN verdicts (W75), and a networked
  runner would not settle two of them.** `junction_aso.py:274` reads `TRANSCRIPT_SOURCE` at import with
  default `"auto"`; `hla_coverage.py:311` pins it to `"cache"`, but `pgr_parent_engagement.py` and
  `aso_noncoding_acceptor_designs.py` never do — so a bare `--check` regenerates `requested: "auto"`
  against a committed `"cache"` and **the byte compare fails before the network is relevant at all**.
  The 403 was swallowed by a documented fallback. **On a networked runner these two go red for MORE
  reasons, not fewer** (`used_per_gene` becomes `"ensembl"`), so W34c's proposed CI resolution should be
  retired. Fetch-sensitive surface: **10 of 148 leaves (pgr), 10 of 857 (aso_noncoding), 0 of 448
  (hla_coverage)**. `hla_coverage.py --check` reads **2 of 448 leaves** and says so in its own success
  line; its AFND half is UNKNOWN by construction — there is **no committed AFND or ISO cache** in the
  tree. ⚠ `hla_coverage.py`'s advised remedy has **no `source_ok` guard on the write** (`:544-546`), so
  running it offline would replace 16 regional tables with `{}` and `--check` would still exit 0.

### The producer census explains W44's row 17 — measured 2026-09-08T04:58Z (W73)

Of **133** tracked artifacts read by the 18 preflight `--check` rows, **26 (19.5%) are HAND-MAINTAINED**
— no writer anywhere in `systems/`, `scripts/`, `research/`, `.github/`. ⭐ But the exposure is not about
record counts: **row 17 (`citation_debt.py`) is the only gate whose entire input set is hand-maintained
AND the only gate that produces no artifact of its own**, so its `--check` has nothing to byte-compare.
Every other row owns at least one produced artifact, so emptying a hand-maintained *input* changes a
recomputation and the compare fails. 13 of the 26 are small enough to be emptied by ordinary editing,
but only 2 of those 13 sit behind a gate that could then pass vacuously — both at row 17. That is the
denominator that makes W44's single measured row a finding rather than an anecdote.

⚠ Methodological warning, recorded because W73 hit it and corrected itself: **writer detection by
basename grep has a real false-negative mode.** Three passes were needed — literal write idioms, then
helper verbs (`_write_json`/`dump`/`emit`/`save`), then ±25-line proximity (which recovered the
"`<artifact>` is stale; re-run without `--check`" idiom where a producer names its file only in its own
staleness message). Two further classes carry no greppable basename at all: **f-string paths**
(`atr_hrd_sarcoma_series.py:1352-1353` via `paths_for(SERIES)` — initially misclassified HAND, corrected
to PRODUCER) and **env-knob paths** (`PREMRNA_OUT`, `GENOME_OUT`, `OUT_SUFFIX`, set by
`.github/workflows/aso-offtarget.yml:330,715`). The 26 is an **upper bound**; the 133 is a **floor**.

⚠ Source-read, not executed: `scripts/news_match.py:279-280` returns `"no queue committed yet — nothing
to validate"` before any validation if the queue file is **absent** — a vacuous pass reachable by
*deletion* rather than emptying, an operation W44's sweep did not test.

### Two more measured results — 2026-09-08T05:00Z

* **W45's 16 source-graded modules are now executed (W58): 4 ESCAPE, 4 CROSS-SOURCE ANCHOR, 4 ACCIDENTAL
  CRASH, 3 N/A, 0 IN-SOURCE CONSTANT** (1 excluded and never invoked). Campaign total across W45+W58:
  **26 enumerated, 25 executed, 8 full escapes.** ⭐ Two refinements to the discriminator: (1) the three
  values are **tried in execution order, not exclusive** — `emc_prmt5_multiplicity` owns a deliberate
  cross-cache refusal (`:568-575`, *"⛔ THE MERGE IS REFUSED unless the two caches agree…"*) and never
  reached it because an `IndexError` fired first, so a one-shape census reports the **first** blocker,
  not the strongest; (2) **the escape needs no external source file at all** — `alcam_precedent` and
  `cd248_precedent` hold their source as an in-module `RECORDS` dict, so emptying it reddens the check,
  the bare run rewrites the artifact from the emptied dict, and `--check` returns `REPRODUCES` at rc 0.
  That is the mirror of `lint_readability`: **an in-source constant blocks the escape when the check
  compares against it and enables it when the check re-derives from it. Direction decides.**
  ⛔ **W45's `.git` confound is REFUTED for both modules it named.** With `.git` present,
  `expression_validation_readiness` is still red because its pinned `BASE = 8c1f2925…` is **absent from
  this shallow clone** (`git rev-parse --is-shallow-repository` → `true`), and `fusion_frame_trap` is
  still red because `fusion-frame-trap-inputs.json` is **not tracked and does not exist**. ⚠ Nine of the
  sixteen are `--check`-red on an untouched copy at `8a667406`. ⚠ Three of the four crashes are **one bug
  in three files** — the same zip-by-index over a values list and a per-sample background list
  (`emc_expression_panels`, `emc_prmt5_multiplicity`, `nr4a3_fusion_targets`). ⚠ `realised_spend.py:437-439`
  returns 0 **unconditionally** — confirmed by execution; `junction_seam_retraction --check` is a true
  universal over an **empty set** (0 artifacts carry its `BANNER_KEY`); `continuity` has **no write
  operation at all**, so W45's Tier-B denominator over-counts by at least one.
* **The setext defect has zero current reach; the first-match defect hides 4 correct corrections (W78).**
  (a) Across the 29 `targets[]` there are **0 genuine setext headings** — all 28 naive candidates are the
  closing `---` of a YAML frontmatter block, one per file, and **0 verdict flips** result even when all
  28 are *granted* setext status (the nearest is 5 lines from any occurrence, against a ±2/±1-line
  window). W56's finding is a real latent hazard against future prose, not a live false clear.
  (b) The 77 never-examined occurrences span **11 files and 27 entry ids**; evaluated at their own
  offsets, **73 of 77 would clear anyway** (61 PROXIMITY, 9 HEADING, 3 NEGATOR) and only 4 would flag.
  ⛔ **All four are correctly-written corrections**, quoted and adjudicated: three in `pricing.md:246`
  retract their own figures in the same clause (*"which is why ~$3–6 and ~$4–7 are each ~2.6× low"*),
  and `degrader-paper-schedule.json:292`'s `x1.9` is covered by a bracketed `[both SUPERSEDED…]` 864
  characters earlier in the same JSON string. **So changing `rx.search` to `rx.finditer` today would turn
  a green gate red on four sentences a human would call correct** — the coverage gap's current contents
  are clean, and repairing it in isolation makes the gate worse before it makes it better.

### Two more measured results — 2026-09-08T05:01Z

* ⭐ **The ASO guard's output-detector limitation is FALSE-ALARM-ONLY, so the guard's green stands (W76).**
  Over all 77 deposited `.py`: **FALSE PASS = 0** (a genuine input mistaken for an output and skipped by
  `:305`), confirmed by two independent checks — 35 `W ∩ P` pairs all written to their own resolved path
  by a module-scope `Name`, and **0 write-`open` sites anywhere where a function-local name shadows a
  resolved module-level path constant**. FALSE ALARM = 3 modules (2 surviving the filter chain, **0
  chain-invoked**), of which only `junction_sirna.py` is a *pure* false alarm; the two
  `fusion_neoantigen_invalidation.py` constants are read-modify-write and W66's TRUE-GAP grade for them
  is right. The entire `:305` suppression surface on the 29 chain-invoked modules is **3 candidates, all
  correct products**. So the scope limit can only *under*-populate the outputs set, which makes the guard
  **stricter, never laxer** — W03j's 10/10 exit 0 is untouched by this axis. All three of the guard's
  limitations are now characterised; the remaining question is outside the AST: whether the *published
  archive* contains what `files[]` says, which needs the ZIP.
* **All 15 `wilson()` implementations agree — 0 arithmetic divergences (W80).** Every one computes the
  same Wilson score interval: **no continuity correction, no Wald approximation, no Agresti–Coull,
  Jeffreys or Clopper–Pearson anywhere.** Two are bit-exact against the closed form at their own z
  (`emc_locoregional_eligibility:137`, `emc_mortality_decomposition:317`); every other residual is fully
  explained by that module's own `round()`. The two causes are presentational: **z is `1.96` in nine and
  `1.959963984540054` in five** (one uses a truncated `1.959963985`), worth at most **7.4e-04 percentage
  points** — below every artifact's reporting precision; and rounding granularity spans 1e-3 to none.
  So **no committed artifact's published intervals are affected by a divergence.** ⚠ Behavioural
  differences that are not arithmetic: `n=0` returns `[None,None]` in nine modules, a 3-tuple of `None`
  in two, scalar `None` in one, **`(0.0, 1.0)` — a full-width interval — in `emc_mortality_decomposition`,
  and **raises `ValueError`** in `emc_fusion_partner_pooling`. Six do not clamp to [0,1] (latent, not live
  — no out-of-range or inverted bound occurred on 18 inputs), and `nr4a3_tcip_reach.wilson(0,10)`
  serialises as **`-0.0`**. ⚠ The one control-value failure, `emc_fusion_partner_pooling`, is **not** an
  arithmetic disagreement: it rounds its published output to 0.1 pp, coarser than the control's 1e-4.
  ⚠ Also measured: **all 15 modules guard `main()` with `if __name__ == "__main__":`** — the in-source
  comments in `emc_endpoint_alternatives.py:609` and `orr_dcr_reread.py:55` warning that import runs a
  full build describe a hazard the guards now prevent.

---

## PRIORITY UPDATE 2026-09-08 ~05:10Z — refills go to unpublished-paper work, not infrastructure audits

Standing prioritization from the orchestrator, applied at this message boundary. This is a priority change
**within the same admitted campaign** — not a new scientific admission, not a new synthesis. The technical
audits already collected (W01–W89) are retained as assets; they do not establish an eligible next paper.
Running assignments finish under their existing contract. Every constraint already in force is unchanged:
deadline 2026-09-09T02:37:19Z, `claude-opus-5` only on the existing subscription, no paid fallback, no GPU,
no publication, no merge, no external contact, read-only workers with one parent collector.

**The W25 / writer / primary-article / Results / novelty hold remains EXACTLY in force.** It is not retried,
reworded or rerouted — not through a different worker, owner, scientific topic label, venue or admission
proxy. The blocked writer is not prompted. Completed W25 and its retained computation are preserved. This
prioritization creates no exception to that hold or to any other closed or refused route, including the
NR4A Perspective, which must not be recreated under any label.

### Candidate-by-candidate eligibility, read from `systems/graph/publications.json` (33 endpoints)

No new synthesis was commissioned to produce this; it is the existing record, read. Excluding `drafted` and
`posted` endpoints, seven candidates remain. Six are eligible by their own recorded dependency state and are
each dispatched to exactly one worker (P1–P6), one distinct route apiece:

| worker | endpoint | state | recorded dependency state |
|---|---|---|---|
| P1 | `PUB-IPD-SURVIVAL` | unwritten | blocker `BLK-NO-CURATED-CLINICAL-DATA`; record says the science now exists and the FINDING changed (a negative about reporting practice) rather than the readiness |
| P2 | `PUB-CARE-DELIVERY` | unwritten | `BLK-NO-FIELD-ATTENTION-MEASUREMENT`; record says both halves of the old blocker are FALSE as of 2026-09-01 and names four extraction artifacts by path; one free step (a term census over a 554-record corpus on the literature-cache branch) has never been executed |
| P3 | `PUB-LOCOREGIONAL` | outlined | `BLK-NO-EMC-DATA` half-retired: denominator computed, numerator not extractable because never curated |
| P4 | `PUB-KINASE-LEADS` | outlined | `BLK-NO-EMC-DATA` retired; four leads graded, three demoted on reading their primary records |
| P5 | `PUB-MATRIX-ADDRESS` | outlined | `BLK-NO-EMC-DATA` retired; mostly negative, two of four routes UNREACHABLE rather than refuted |
| P6 | `PUB-NR-OUTSIDE-NR4A3` | outlined | `BLK-NO-EMC-DATA` retired; both routes graded negatively, general fusion-architecture claim survives |

**One candidate is NOT eligible and is NOT dispatched, recorded honestly rather than worked around:**
`PUB-PARKED-MODALITIES` (unwritten), blocked by `BLK-VECTOR-DELIVERY` and `BLK-INDUCED-COMPLEX`. Its own
record states every route it would cover is parked on a technology nobody has, so it has no result to report
and is worth writing only once at least one watched capability lands. **No such capability has landed.** Its
named dependencies are retained verbatim; no eligibility is inferred from the absence of its inputs, and no
substitute route is manufactured to keep a headcount.

Each P-worker is instructed that where a route's required input is missing, it records the **exact failed
condition and the exact input required to reopen it** and stops that route — it does not recycle an unchanged
failed gate, does not infer novelty from a missing selected input, and does not substitute another claim.

**Infrastructure audits are not refilled from this point.** The 20-worker target does not justify invented
eligibility or redundant work; the concurrency figure follows the eligible-work count, not the reverse.

### Paper-lane result 1 — `PUB-IPD-SURVIVAL` is WRITABLE NOW (P1, collected 05:12Z)

All 13 quantitative assertions in the endpoint's current (non-superseded) record resolve to a committed
artifact; **none graded UNSUPPORTED**. `emc_ipd_survival.py --check` exits 0 (write-freedom of the check path
read in source first). The headline negative — *there is no pooled time-to-event dataset* — is carried by the
generated artifact itself (`emc-ipd-survival.json` → `pooled.⛔_this_is_not_a_pool`), not by an author's
assertion. `BLK-NO-CURATED-CLINICAL-DATA` remains true and **does not block this paper**: it is the paper's
subject, not its obstacle.

Verified: 7 curves with no numbers-at-risk row across `masunaga2025` (3, n=171) and `chiusole2020` (4, n=59),
with per-figure verdicts and `pdf_sha256` committed; 11 patients / 9 events / median 7.984996 mo against a
printed 8 the reconstruction never saw; 4 swimmer-plot patients with 5 passing external checks; 2 patients
transcribed from a printed table; `CURVES == []` enforced by `test_emc_ipd_survival.py:165`; the error control
at worst 0.0636 / off-step 0.0035, explicitly a LOWER bound.

⚠ **One wording defect found, repairable in prose with no new input:** the record says *"series reachable at
no cost"*, but `seer270_2022` (n=270) is Unpaywall **gold** and graded `free_to_read_but_not_retrieved` — a
larger free-to-read series exists whose figures were never seen. The true predicate is "the two largest series
**whose figures could be retrieved and read**". Fix the predicate; do not drop the row.

⚠ **A judgement inside the headline number, which must stay visible:** the 11-patient reconstruction anchors
the risk table at N=11 rather than using its printed first row `[2,10]`; taken verbatim the reconstruction
misses the floor and contradicts the paper's own caption. Both tables are retained in
`km-figure-readings.json`. Pixel-internal corroboration: first two steps read 0.9097/0.8188 vs 0.9091/0.8182
for N=11 (miss 0.0007) and 0.900/0.800 for N=10 (miss 0.0188), against a worst off-step error of 0.0035.

**Not required to write it** (so nobody blocks on them): independent re-digitization of the stacchiotti2013
figure, and retrieval of `seer270_2022` — its absence is a reported census outcome, not a gap.

**Two disclosed re-derivation gaps, to travel with the paper:** the swimmer-plot figure is CC BY-NC 4.0 and is
NOT committed, so those 4 readings are not re-runnable from a bare checkout; and the admissibility artifact's
`reads_from.retrieval_rounds` points at `origin/literature-cache`, which has never existed in this checkout —
the per-figure verdicts, captions and digests ARE committed, so this is a re-derivation route, not the
evidence.

Full deliverable, including the drafted Results and Limitations: `paper-lane/P1-PUB-IPD-SURVIVAL-paper-step.md`.
No manuscript file was created; that is an owner act, not a campaign-worker act.
