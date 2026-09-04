---
name: repo-gates
description: This repository's commit gates, linters, architecture graph, deliverable map, and the six-part reviewer-AI review block. Load before committing or pushing, before running preflight, when a preflight or CI gate goes red, when writing or editing a manuscript or its SI, when touching anything under systems/ or the registry, and before any outward-facing step (preprint, submission, release, DOI). Covers: tiered preflight (scoped tests for the commit loop, PREFLIGHT_FULL=1 before publication) and why the selector fails to full; the nine gates in order; lint_claims vs lint_citations (claim strength is orthogonal to citation provenance); why the prose-style gate is scoped to submission texts only; branch drift as a data-loss bug and checking which ref a workflow actually writes to; the generated systems/views; and the retired patient-facing site, which must not be recreated; and the exact six parts a reviewer-AI review block must contain before any outward-facing step.
---

## ⛔ THE COMMIT RITUAL FOR ANYTHING THAT RECORDS A GIT REVISION

**Re-derive `aso_archive_manifest.py` as the LAST action before committing, and commit it as its OWN
commit. Never `--amend` and never rebase afterwards.**

⚠ *Measured three times in one session, 2026-08-27, always the same shape.* The manifest records the
revision it was generated at. Generate it, then amend or rebase, and that commit is rewritten — so the
manifest names a sha reachable from no branch and no tag, and the deposit's provenance line points
nowhere. `test_the_recorded_revision_is_a_commit_this_clone_can_resolve` catches it **one commit late**,
which is exactly late enough to have pushed it once.

⭐ **THE LAG IS FINE; THE REWRITE IS NOT.** A manifest generated before its own commit legitimately
names that commit's PARENT, which is reachable. What breaks it is history rewriting, not sequencing.

⛔ **AND ITS BLAST RADIUS IS BIGGER THAN ITS OWN TEST.** A module red at baseline blinds the ablation
gate's batched witness command (AUT-PD-006), so an orphaned revision ALSO makes an unrelated document
report a covered sentence as blind — a blindness finding pointing at a manuscript, manufactured
entirely by a stale sha. Two failures, one cause, and the second one looks like a paper defect.


# Commit gates, architecture and deliverables

Extracted from CLAUDE.md §7 (plus §5's deliverable map) on 2026-08-15, **verbatim**.

⚠ **This file is a `pinned-figures.json` target.**

## Branch hygiene

- **★★ KEEP EVERYTHING SYNCED TO `main`, AND KEEP `main` CURRENT — BRANCH DRIFT IS A DATA-LOSS BUG, NOT AN
  INCONVENIENCE (trimcrae, 2026-07-29, after it cost a day).** Long-lived feature branches that a *workflow*
  runs from are the dangerous kind, because they hold **state as well as code**. Measured that morning:
  `step1-fanout-autoscale.yml` checks out `fleet_branch` and writes its
  map there. Its default was then `claude/max-effort-2dq11l`, so `main` said the fan-out was **1 of 19 edges,
  $22.62** while the branch — where the lane really ran — said **14 of 19, $68.98, 197 rentals**. ✅ **CLOSED:
  the default is now `main` and every fallback in that workflow is `|| 'main'`; `step1-fanout-map.json` is
  byte-identical on this branch and `origin/main`.** The incident is kept because the *rule* is what binds,
  not the branch name. Three separate harms, all real:
  1. **The paper was wrong.** §2.9 was written off `main`'s artifact and understated the work by 13 computed
     ΔΔG edges. An artifact on the wrong branch is a stale fact that reads as a current one.
  2. **Fixes landed where nothing runs.** The exclusion-set repair, `leg_failure_breaker` and
     `teardown_decision` all went to `main`, which that lane did not check out — so they were inert.
     ⚠ *Superseded, retained: this line carried "(union 58 → 27)". Those numbers have **no home anywhere** —
     not in `vast_machine_blacklist.py`, not in any artifact, not in history — so rule 1 cannot check them,
     and the mechanism they describe is itself retired (`DURABLE_EXCLUSIONS_ENABLED = False`). An unhomed
     figure inside the rule that exists to stop unhomed figures.*
  3. **Re-pointing the lane became expensive.** Flipping `fleet_branch` to `main` would have shown 13 finished
     edges as unrun and **re-bought them** (~$46) on a lane that rents unattended.
  So: **merge to `main` early and often; rebase working branches onto `main` before every push; never let a
  branch a workflow runs from be the only home of an artifact.** Before writing ANY claim from a committed
  artifact, check which ref the producing workflow actually writes to — `main` is not automatically it. If a
  lane must run off a branch, that branch's artifacts belong on `main` too, and reconciling them is
  **port-then-switch, never switch-then-discover**.

- **⛔⛔ `git checkout --ours` OVER THE CONFLICT LIST SILENTLY DISCARDS EVERY RESOLUTION YOU JUST
  WROTE BY HAND (2026-08-23, caught by luck).** A 39-ahead/49-behind merge produced 14 conflicts:
  two source files needing real merges, twelve generated artifacts that only needed regenerating.
  The source conflicts were resolved carefully — a UNION of two generator checks in `preflight.sh`,
  and `build_submission_pdf.py`'s vaccine-path banner taken from `main` because main's names where
  that paper actually is. Then a loop ran `git checkout --ours` over
  `git diff --name-only --diff-filter=U` to clear the *generated* files, and that list **still
  contained the two source files**, because resolving a conflict in the working tree does not
  remove it from the unresolved list — only `git add` does. Both hand-written resolutions were
  overwritten with the branch's side. The build stayed green: main's `vaccine_path_tables` generator
  check had simply vanished from preflight, and the vaccine paper's PDFs went back to announcing a
  deposit that had already happened elsewhere.
  ★ **THE TELL WAS A HASH THAT MATCHED WHEN IT SHOULD NOT HAVE.** `selector-validation.json` reported
  `preflight.sh: MATCH` — impossible for a union neither side had recorded — and chasing that one
  surprising line is the only reason it surfaced. ⚠ Nothing else would have: a dropped gate is
  invisible, and `--ours` is a legitimate command that reported success.
  **So: `git add` each file the moment you resolve it, and only then clear the remainder.** Better,
  never blanket-`--ours` a mixed list — name the generated paths explicitly, since those are the
  ones whose contents you are about to overwrite anyway.

## Evidence and registry

- **Citing & combining studies:** registry data uses a structured citation map (`registry.citations` +
  `sourceId`/`primaryRef`, primary vs secondary) and a fixed pooling method (crude denominator-weighted
  proportions + Wilson 95% CIs, non-overlapping cohorts only). Read **[systems/POLICY-evidence.md](./systems/POLICY-evidence.md)** before
  touching `registry`.

## Preflight

- **★★ PREFLIGHT IS TIERED: FAST GATES ALWAYS, THE TEST SUITE SCOPED TO THE CHANGE, AND THE WHOLE
  THING ONLY BEFORE PUBLICATION (trimcrae, 2026-08-12: *"not running tests on every single modality,
  only the ones affected"* and *"not requiring preflight to run on every push to main, only manually
  before publication"*).** Measured that day: the modalities suite was **745.9 s of a ~15-minute
  gate — 87 % of preflight** — while the seven doc, systems-model and medical-integrity gates cost
  about a minute between them, and those are the ones that have actually caught things here. ⚠ And
  the expensive copy is the WEAKER one: this sandbox lacks numpy, rdkit, boto3, scipy, pymbar and
  netCDF4, so 48 of those tests fail as missing imports and five modules do not import at all, while
  `tests.yml` runs `on: push` with the real dependencies. Twelve local minutes bought a degraded
  rerun of a check that was about to run properly. Scoped, a typical change now runs in **under a
  second** (measured: a `junction_aso_offtarget.py` edit selects 3 test modules, 39 tests, 0.51 s).
  - ⛔ **BEFORE YOU START ANY TIER: it gates the COMMIT, not the work.** Settle the tree first —
    edits AND their regenerations — then run it ONCE in the background and keep working through the
    backlog while it runs. **Polling a running gate is not work.** Rule and evidence: CLAUDE.md §6.
  - **`./scripts/preflight.sh`** — every fast gate, **plus gate 13: the pure-logic suites nothing
    else runs** (`scripts/tests`, `research/autonomy/tests`, and the systems model), which
    `preflight.sh:1218` runs unconditionally, outside the `RUN_TESTS` block. **About two minutes** —
    **130.7 s** measured end to end on 2026-09-02, of which gate 13 is **57.1 s over 1 030 tests**.
    **This is the commit loop.**
    ⚠ *The ~9-minute loop was FIXED on 2026-09-02, not re-estimated, and no assertion changed:
    `stuck_clock.ledger_versions()` — S6-COMMITLOOP's named hot spot, 96 % of the gate's git calls —
    is memoised per HEAD and batched into one `git cat-file`, and gate 6 stopped walking the whole
    prose corpus twice. Gate 13 previously 446.3 s, now 57.1 s on a suite that grew 789 → 1 030
    tests; gate 6 72.4 s → 37.7 s with byte-identical output. Evidence and the mutation results:
    `research/autonomy/sprint-2026-09-01/S6b-COMMITLOOP-FIXED.md`. One home for the figure:
    CLAUDE.md §6.*
    ⚠ *Superseded 2026-09-02, retained (CLAUDE.md rule 1.2): "**About 9 minutes** on a quiet box —
    fast gates **81.3 s**, gate 13 **446.3 s** quiet and **1 247.8 s** under twelve-way contention";
    no longer current, "**gate 13 is 85–94 % of the loop**." Correct when taken, and it is the
    measurement that made the fix findable.*
    ⚠ *Superseded 2026-09-01, retained (CLAUDE.md rule 1.2): "every fast gate, and **no test**.
    ~**30 s**." The tier has run tests since 2026-08-27, and the 30 s described a smaller fast tier
    that has since gained the receipt, residue and cycle-contract gates and a publication-type axis
    on gate 6.*
    ⚠ *Superseded 2026-08-23, retained (rule 1.2): "every fast gate, plus
    only the tests the change can reach". True from 2026-08-12 until the day the remaining suite was
    measured — see the tier below.*
  - **`PREFLIGHT_TESTS=1 ./scripts/preflight.sh`** — the fast gates plus both suites, modalities
    scoped to the change ([`affected_tests.py`](./scripts/affected_tests.py), a static import graph
    with transitive closure), manuscripts in full. **Run this when the change touches a manuscript,
    an SI, a citation or a deposit artifact.**
  - **`PREFLIGHT_FULL=1 ./scripts/preflight.sh`** — everything, **~25 minutes** (the modalities
    suite alone is ~20). **Required before PUBLISHING, and publishing is a CLOSED LIST OF FOUR: a
    preprint, a submission, a release, a DOI.** Scoping is not a claim that the rest of the suite
    passes — but `tests.yml` makes that claim on every push, with the real dependencies, and it is
    the authority. Watch CI; do not pre-run it locally.
    - ⭐⭐ **AND THE TEST SUITES LEFT THE DEFAULT TIER ON 2026-08-23, WHICH IS THE OTHER HALF OF
      THE SAME 2026-08-12 ARGUMENT** (trimcrae: *"change the rules so that it's not constantly
      running and blocking things"*). That day scoped the modalities suite because *"the expensive
      copy is the WEAKER one"*; the manuscripts suite was never scoped and inherited the whole cost.
      Measured: **fast gates 31.4 s, manuscripts 176.1 s on every commit** — including a run against
      a **clean tree at `origin/main`**, which still executed all 878 tests — and modalities ~0 s.
      So ~85 % of the gate was one step that could not tell a manuscript rewrite from no change at
      all. ⚠ **Scoping it was tried first and the measurement refused it.** A selector was built and
      validated against traced ground truth — all 50 guards run in their own processes under a
      tracer recording every file each really reads, content reads kept apart from directory
      enumeration — and reached **zero under-selection**. It still left a **132.5 s floor of the
      176.1 s**, because these guards bind to directory scans and to paths read out of committed
      artifacts: 28 of 50 are unscopeable on their own terms. A 25 % saving does not pay for a new
      selector's failure surface, so it was reverted. ⛔ **The cost is real and is not glossed:**
      gate 12 entered the commit loop so a citation guard would not *"fire after the mistake is
      shared"*, and it now fires later — caught by CI minutes afterwards and fixed with another
      commit, which is precisely the content-vs-ceremony line below. **`PREFLIGHT_TESTS=1` is one
      word; spend it on manuscript work.**
    - ⛔ **A MERGE OR PUSH TO `main` IS NOT ON THE LIST, AND READING IT ONTO THE LIST COST ABOUT TWO
      HOURS (2026-08-23).** The reasoning that gets you there is seductive and wrong: *`main` is the
      trunk every workflow runs from, so surely it deserves the full gate.* The rule defined FULL by
      four examples and named nothing on the other side, so the gap got filled with the expensive
      guess. ⚠ **And do not reach for visibility as the test either — this repository is PUBLIC**, so
      a stranger can read `main` the moment you push, and "outward-facing" read literally would sweep
      in every commit. ★★ **THE TEST IS WHETHER ANYONE ACTUALLY READS IT** (trimcrae, 2026-08-23:
      *"Nobody is reading this repo. The only time anyone reads anything is when we submit a paper."*).
      Public is a permission, not a reader. **This repository has exactly one reader — the project
      itself**, so every mistake in it is caught and fixed by us with another commit; a submission is
      the only moment anything reaches an outside reader, and is undone only by a public correction
      against an identifier someone may already have cited.
    - ⛔ **THAT IS NOT A LICENCE TO BE SLOPPY IN THE REPO. Two things get conflated and must not be.**
      *Rigour of CONTENT* — one fact one place, derived totals, honest UNKNOWNs, negatives at their
      true weight — **never relaxes**, because the reader relying on it is the NEXT SESSION, which
      inherits every wrong number as a fact. *Ceremony of GATING* — minutes of checking bought per act
      — **scales with who reads the result**, and that is nobody until we submit.
    - ⭐ **THE 25 MINUTES IS NOT THE COST — THE CASCADE IS.** An unneeded FULL run surfaces
      pre-existing failures unrelated to your change, and chasing them becomes the task. On
      2026-08-23 it surfaced 84 modality failures that were **all** a missing-dependency gap present
      on `main` before the change; fixing the environment then cost three more 25-minute runs to
      verify. The fix was worth having and is documented below — **it was not the task that was
      asked for**, and absorbing it silently was the error.
    - ⭐ **SO WHEN FULL GOES RED ON SOMETHING YOU DID NOT TOUCH, THE FIRST MOVE IS `git stash` AND
      RE-RUN ON CLEAN `origin/main`.** If it reproduces, it is not yours. Say so, and treat fixing it
      as a separate task to raise rather than one to swallow into the current one.
  - ⛔ **THE SELECTOR FAILS TO FULL, AND THAT IS THE ENTIRE SAFETY ARGUMENT.** A changed `conftest`,
    a changed test helper, an unparseable source, a git that will not answer, or an edit to the
    selector or to `preflight.sh` all take the whole suite. A gate that quietly runs too little is
    the "reports while measuring nothing" defect this repository keeps paying for, not a faster
    gate; `scripts/tests/test_affected_tests.py` asserts each of those directions, and the
    baseline-pruning readout is suppressed on a scoped run because **a subset cannot say a test it
    never executed is fixed.**
- **Before committing:** `./scripts/preflight.sh` must pass. **Nineteen gates, in this order:** (1) the consistency
  linter (`research/manuscripts/lint_consistency.py`), (2) `systems/systems_check.py --check`, (3) `research/manuscripts/emc_systems_map_check.py --check`,
  (4) claim strength (`lint_claims.py`), (5) changed prose (`lint_changed_prose.py`, warnings only),
  (6) citation provenance AND publication type — `research/manuscripts/lint_citations.py`, which since
  2026-08-27 also runs `lint_citation_types.py` under the same ordinal and the same command,
  (7) `research/manuscripts/lint_style.py`,
  (8) the readability screen (`research/manuscripts/lint_readability.py`, ADVISORY — where to look, not
  whether the prose is good; the HARD gate on an outgoing version is publish_bar clause 7, not this one),
  (9) `systems/parser_guard.py`, (10) the registry evidence
  contract (`validate-registry.mjs`), (11) the generated deposit artifacts reproducing from their
  generators, (12) the cycle receipts' fan-out width (`research/autonomy/receipt_schema.py`),
  (13) the modalities tests, (14) the manuscripts tests, (15) the pure-logic suites nothing else
  runs — `scripts/tests` (the selector's own contract) and `research/autonomy/tests` (the loop's
  instruments: continuity, the session reaper, the receipt schema),
  (16) unverified-output residue in the documents that go out
  (`research/manuscripts/lint_submission_residue.py`) — residual model meta-comments and unremoved
  placeholder text in manuscripts, SIs, tables, reference files and cover letters, two of the three
  triggers a preprint server applies a one-year submission ban over; the third, hallucinated
  references, is gate 6's and is not duplicated. **APPENDED LAST SO NO ORDINAL MOVED**, since gates
  13–15's numbers are written into `research/autonomy/ids.py`, `research/autonomy/priority.py` and
  committed ledger rows.
  **(17)** the cycle contract against the receipt-schema gate
  (`research/autonomy/contract_check.py`) — gate 12 refuses a receipt missing `ccr_session_id`, and `.claude/skills/research-loop` §2 step 10, the text
  a cycle follows when it hand-authors that receipt, did not name the field, so a cycle obeying the
  contract exactly could not commit (AUT-PD-146). It DERIVES what gate 12 requires by deleting each
  field from receipts the enforcer accepts, and reds the build when step 10 does not name one.
  **ALSO APPENDED LAST, FOR THE SAME REASON** — it belongs beside gate 12 by subject and sits at the
  end by necessity, because these ordinals are positional and four of them are referenced by number.
  **(18)** what each test tier costs, against the budget somebody set for it
  (`scripts/tier_budget.py --check` over `scripts/tier-budgets.json`) — ⛔⛔ **THE ANTI-BLOAT GATE,
  ADDED 2026-09-02 AFTER THE PUBLICATION GATE REACHED 9.7 MINUTES TO CHECK A 4,695-WORD PAPER.**
  Nothing in it was wrong; it had grown one justified test at a time — gate 13 went **789 → 1 030 →
  1 119** in ten days, the modalities suite reached **8 212 tests, 72 % of every publication run and
  0 failures across the eight committed PREFLIGHT_FULL logs**, and the repository held **2 973 tests
  for six pages**. ★ Every one of those tests was justified by a real incident, which is exactly why
  the TOTAL went unexamined: each addition was correct and the sum was never anybody's decision.
  It caps **test functions, never seconds** (wall time varies with the box, and a gate that reddens
  under load is one people learn to re-run), counts by AST in ~0.1 s so it cannot itself be the
  bloat, and requires every `tests/` directory in the repository to belong to some tier — so a new
  one cannot appear and grow while every budgeted tier reads green. **Raising a ceiling is the LAST
  of three answers**, after "does it belong in a cheaper tier?" and "has something already in this
  tier stopped earning its place?", and is declared like any other bar change.
  **APPENDED LAST, AGAIN FOR THE ORDINAL REASON** — inserting it beside the other test rows, where
  it belongs by subject, would have renumbered gate 17 and every reference to it. 
  **(19)** every route's derived ledger id is frozen, not counted
  (`research/autonomy/derived_ids.py --check` over `research/autonomy/derived-ledger-ids.json`) —
  ⛔⛔ **AN `AUT-NNN` NAMES ONE ROUTE FOREVER, AND UNTIL 2026-09-03 IT NAMED WHICHEVER ROUTE LANDED
  IN ITS SLOT (AUT-PD-215).** `priority.build_entries()` minted a derived row's id as
  `AUT-{index + 1:03d}` over routes sorted by id, so the id was a POSITION. Reproduced against the
  live graph before any code changed: adding **one** route whose id sorts early moved **76 of 77**
  ids and took `AUT-073` — the escalation trimcrae answered on 2026-09-01 — from `RT-TRIAL-REACH` to
  `RT-TRABECTEDIN-PPARG`, with nothing red anywhere. ★ **It is a gate rather than a test because the
  commit-loop test tier is opt-in** (`PREFLIGHT_TESTS=1`) **and this has to fire on the commit that
  ADDS A ROUTE**, the only moment the binding can go wrong; a guard behind a flag nobody set reports
  the damage instead of preventing it. It costs ~0 s (three small JSON reads), fails closed on an
  unbound route, a duplicated id or a ledger row disagreeing with the frozen map, and names
  `derived_ids.py --extend` as the remedy. A binding whose route has left the graph is reported and
  KEPT — receipts still name that id.
  **APPENDED LAST, AND THE DRAFT THAT WAS NOT IS THIS ENTRY'S OWN LESSON.** Placed at 13 beside the
  other autonomy-record gates, where it reads best, it pushed the modalities, manuscripts and
  pure-logic test gates from 13/14/15 to 14/15/16 — the three ordinals written into
  `research/autonomy/ids.py`, `research/autonomy/priority.py`, four prose documents and committed
  ledger rows. **That is a positional id silently coming to mean something else: the exact defect
  this gate exists to stop, one register over.** `[P1]` caught it in the same run that ran the fix.
  Its exit code cannot be masked.
**Do not
  re-type an ordinal from memory** — `[P1]` derives it from the script and fails the build on any document
  that disagrees. *(It did exactly that when the citation gate was inserted, catching four documents in one run.)*
  ⚠ *Superseded 2026-08-22, TWICE OVER: `lint_claims.py` WAS CI-only, and a manuscript repair then shipped a word that fires R2 — preflight green, CI red at that step, and the 26 steps behind it skipped. The note that added it here then said it was **gate 7** and `lint_changed_prose.py` **gate 8**, typed from the intended reading rather than derived from the script, which runs both BEFORE the citation gate: they are **4** and **5**, and everything from citations to parser guard shifted down by two. `[P1]` did not catch it because it only ever derived the REGISTRY VALIDATOR's ordinal — the one number four documents had already got wrong once — and nothing checked the enumerated list this very sentence lives in. It does now.* *Superseded, retained: "It runs the registry evidence contract
  (`validate-registry.mjs`), the doc linters and the modalities tests" — written before gates 2 and 3 existed,
  and "the doc linters" plural was never true of this script. And: **"Five gates"**, which listed the map
  check nowhere, **"Six gates"**, written before citation provenance was one, and **"Seven gates"**, written
  before manuscript prose style was one, **"Eight gates"**, written before the manuscript tests, and
  **"Twelve gates"**, written before `scripts/tests` was one — the selector's own contract, cited by this
  very section as the safety evidence for scoping while running in no gate at all (round 14 seat 4), and
  **"Fourteen gates"**, written before the receipt-schema gate and before `research/autonomy/tests`
  joined the last entry — 53 assertions guarding the loop's own instruments that neither this script
  nor `tests.yml` ran, which is round 14 seat 4's finding recurring in a different directory, and
  **"Fifteen gates"**, written before the unverified-output residue gate (AUT-PROP-032, 2026-08-28),
  and **"Sixteen gates"**, written before the cycle-contract gate (AUT-PD-146, 2026-08-29) — which
  `[P1]` caught within the same commit, exactly as this note's own last line says it would.
  The count above is not typed twice: `[P1]` derives it from `preflight.sh`, and `check_preflight_gate_list`
  derives the enumerated list beside it.
  were run locally at all — CI had run them since 2026-08-03 and this script had not, so a green
  preflight was silent about every guard in `research/manuscripts/tests`, the newest of which checks
  citation numbering.*
  - **★★ GATE 5 IS ABOUT REGISTER, AND IT IS SCOPED ON PURPOSE (2026-08-09).** This repository's house
    style — glyph warnings, bold on the load-bearing clause, running commentary on why a rule exists —
    is correct *here*, in the roadmap and in the artifacts, where the reader is a maintainer or an agent
    being stopped from repeating a specific mistake. It is wrong in a **manuscript**: a journal reader is
    not being warned, prose that keeps asserting its own honesty reads as advocacy rather than as a
    report, and the tics are recognisable as machine-written, which costs a paper credibility it has
    otherwise earned. So `lint_style.py` checks only the files in its own `TARGETS` — submission texts —
    and exempts frontmatter, fenced code and **every section under an `Appendix` heading**, because
    superseded-value bookkeeping is *required* by rule 1.2 and belongs in an appendix rather than in the
    running text. **A memo, a plan or a findings note is not a submission text and must not be added to
    `TARGETS`.** Measured the day the gate landed: **81 findings in the one manuscript listed** — 25
    glyphs, 32 mid-sentence bolds, 14 sentence-shaped headings, bold at 20.1 per 1000 words against a
    limit of 12 and em-dashes at 11.4 against a limit of 6.
  - **★★ A HEDGED SENTENCE ON A FABRICATED PMID IS A PERFECT SENTENCE TO `lint_claims` — WHICH IS WHY
    GATE 4 EXISTS (2026-08-07).** An agent drafting a manuscript wrote a citation from **recollection**:
    a PMID present in **no committed source anywhere in this repository**. It **passed `lint_claims`
    twice**, and six invented titles and author-lists went out in the same pass; a human-directed audit
    of every identifier caught them, and nothing automatic could have. ⚠ **`lint_claims` is not
    deficient for missing it** — R1–R5 check how strongly a claim is WORDED, and claim STRENGTH is
    orthogonal to citation PROVENANCE. No other gate read an identifier at all, in a repository whose
    first golden rule is "never fabricate … citations".
    [`lint_citations.py`](./research/manuscripts/lint_citations.py) asks the one question an offline
    checker can answer: does this identifier ALSO appear in a tracked `.json`/`.jsonl`? Those are fetch
    products — a network read, a registry curation, a graph edit — none of which a model does from
    memory. ⛔ **It is a LEDGER, not a wall**: the 215 prose-only identifiers found on day one are
    baselined, because a gate that goes red on everything gets switched off, and **the baseline is the
    finding** — it names for the first time which citations nobody has checked. The count is meant to
    fall. **Anything NEW and unanchored fails immediately**, which is the case that actually happened.
    ⚠ An anchored identifier is **not thereby verified** — an artifact carrying it is evidence of a
    fetch, not of correctness. This raises the floor; it is not a truth oracle.
  - **★★ AND ON 2026-08-26 THAT EXACT SENTENCE CAME TRUE, SO GATE 6 GREW A THIRD AXIS.** A metastasis
    claim was attributed to *"the review literature"* over four PMCIDs. **One was a review.** The
    others were a Japanese national-registry outcome cohort (PMC12398172, n = 171) and two
    single-patient case reports (PMC12376927, PMC9131214). Every identifier was real, every one was
    **anchored**, gate 6 was **green and correct to be** — origin was never the question — and the
    misattribution survived **two cycles** before a blind seat read the papers (correction register
    A11). ⭐ **The discriminator is one field: PubMed's `article_types`.**
    [`lint_citation_types.py`](./research/manuscripts/lint_citation_types.py) runs from inside
    `lint_citations`, under the same gate ordinal and the same command, and asserts that where prose
    puts an identifier in the attributive slot after a type word — *a review*, *a case report*, *a
    randomised controlled trial* — PubMed agrees. **Three orthogonal axes now:** how strongly a claim
    is WORDED (gate 4), whether an identifier has an ORIGIN (gate 6a), whether the paper is the KIND
    of thing the sentence says (gate 6b).
    ⛔ **CACHE, NEVER CALL.** The PubMed MCP connector is the FETCHER; the gate reads
    `research/manuscripts/citation-article-types.json`, so preflight stays offline and deterministic.
    A claim whose identifier has no cached row is an **ERROR naming the fetch**, never a silent pass.
    ⚠ PubMed's terms require attribution and a DOI link wherever its metadata travels — the cache
    carries `doi_url` on every record and every failure line prints it.
    ⭐ **It needed NO baseline**: 18 type claims in the tree the day it was written, 18 correct. What
    it deliberately does **not** bind is listed in the module's `NOT_BOUND` with a reason each —
    *cohort study*, *case series* and bare *trial* have no MeSH publication type that could confirm
    them, and a rule that can only ever pass is a rule that reports while measuring nothing.
  - **★★ A GREEN PREFLIGHT THAT SKIPS A MEDICAL-INTEGRITY GUARD IS WORSE THAN NO PREFLIGHT (measured
    2026-08-06, and it turned `main` red).** Gate 3 was **CI-only** until that day, so a session could run
    this script, read `PREFLIGHT OK`, merge, and only then learn that a newly-generated view named a cell
    line whose identity is **disputed** — `O4` requires every tracked file naming it to classify the use as
    invalidated / survives_relabelled / unaffected, and it fired in CI and nowhere else. The gap was not
    tidiness: gates 2 and 3 are the two checks that enforce **provenance and medical integrity**, and one
    of them was invisible locally while the other was trusted. ⚠ **When you add a check to `tests.yml`, the
    question is not "does CI run it" but "would a session that only ran preflight have seen it".**

### ⭐ THE SANDBOX DEP GAP IS FIXABLE — AND SINCE 2026-08-23 IT IS `./scripts/dev-setup.sh`

**⛔ RUN `./scripts/dev-setup.sh` BEFORE BELIEVING A RED PREFLIGHT IN A FRESH SANDBOX.** A
`SessionStart` hook in `.claude/settings.json` runs `dev-setup.sh --if-needed` (an import probe of
both interpreters, not a marker file), so this should already be done; the command is here for when
it is not.

⚠ **THE PROSE BELOW WAS TRUE AND STILL DID NOT FIX ANYTHING, WHICH IS THE LESSON.** It recorded the
exact remedy on 2026-08-23 — and that same day `main` came up red on a clean tree at `origin/main`:
gate 2 wanting `jsonschema`, and 29 manuscript guards wanting `pdfminer.six`/`pypdf`, while CI was
green on the same commit. **Instructions in a skill file run only if a session loads that skill and
acts on it.** A script plus a hook runs either way. ⭐ Note also that the two interpreters need
**different** lists — system `python3` runs the fast gates AND everything
`regenerate_aso_chain.sh` calls, so it needs `jsonschema`, `pypdf`, `cffi` and `biopython`.
⚠ *Superseded 2026-08-24, retained: "system `python3` gets `jsonschema` only, because this image's
distro `cryptography` panics on import and `pypdf` imports it — and nothing under `preflight.sh`
needs pypdf there, since the PDF guards are TESTS and resolve inside the pytest venv." Both halves
were wrong in a way that cost a chain run each.* **The panic's cause is a missing `_cffi_backend`,
not the distro package** — `RUST_BACKTRACE=1 python3 -c "from cryptography.hazmat.bindings._rust
import exceptions"` prints that `ModuleNotFoundError` one line above the panic, pyo3 having
swallowed it into `Python API call failed`; `pip3 install cffi` fixed it with no distro package
touched. **And preflight is not the only thing that runs in that interpreter**:
`build_submission_pdf.py` imports `pypdf` and `junction_aso_thermo.py` imports `Bio`, so a probe
scoped to preflight reported "nothing to do" while no ASO PDF could be built and the thermodynamics
step refused. `SYSTEM_PROBE` now covers both.

#### The original note, retained

**`PREFLIGHT_FULL=1` could not pass in this dev sandbox at all — on `main`, before any change.**
Measured that day: **84 modality failures and 29 manuscript failures, every one a missing import**,
plus `systems_check.py` refusing to run for want of `jsonschema`. The tiered-preflight note above
records the gap as a fact of life (*"this sandbox lacks numpy, rdkit, boto3, scipy, pymbar and
netCDF4"*) and routes around it. **It is not a fact of life. It is nine pip installs.**

⛔ **THE TRAP, AND IT COSTS AN HOUR IF YOU MISS IT: `pytest` IS A `uv` TOOL IN ITS OWN VENV.**
Installing into the system interpreter changes nothing the tests can see — `python3 -c "import
pdfminer"` succeeds while the identical import inside a test still raises `ModuleNotFoundError`.
The deps have to go into the tool's environment:

```bash
uv tool install --force \
  --with pdfminer.six --with pypdf --with jsonschema --with numpy --with scipy \
  --with rdkit --with boto3 --with netCDF4 --with pymbar --with pyyaml --with biopython \
  pytest
python3 -m pip install jsonschema        # systems_check.py runs under system python3, not pytest
```

**Measured effect, in order, each step's failures being purely the next missing import:**
84 → 36 (numpy/scipy/rdkit/boto3/netCDF4/pymbar) → 1 (pyyaml) → **0** (biopython). Final:
**7,822 passed, 0 failed** on the full modality suite, and `PREFLIGHT OK` end to end.

⚠ **DO NOT PRUNE `sandbox-failure-baseline.txt` ON THE STRENGTH OF THIS.** A green run after
installing the deps reports *"11 baseline entries no longer fail — prune them"*, and pruning would be
wrong: those entries describe a **fresh** sandbox, which is what the next session gets. The baseline
is a statement about the default environment, not about yours. **Install the deps; leave the baseline
alone.**

⚠ And note what the gate did right while the gap was open: with deps missing it reported the extra
failures as **"NOT in the sandbox baseline"** and refused to pass, rather than tolerating a count.
That is the 2026-08-08 design working — the baseline had drifted behind a growing suite, and the gate
failed closed instead of waving 36 unknown failures through.

## Architecture and retired surfaces

- **★★ THE ARCHITECTURE IS [`systems/`](./systems/) — READ
  [`systems/views/L0-ecosystem.md`](./systems/views/L0-ecosystem.md) FOR THE WHOLE LANDSCAPE IN ONE SCREEN.**
  `systems/graph/*.json` is the source of truth for every strategy family, route, blocker, technology
  dependency and forecast; everything under `systems/views/` is **GENERATED** and a hand-edit fails the
  build (`python3 systems/systems_check.py --write-views` to regenerate). Design and rationale:
  [`systems/ARCHITECTURE.md`](./systems/ARCHITECTURE.md). Identifiers, glyphs and controlled vocabularies:
  [`systems/CONVENTIONS.md`](./systems/CONVENTIONS.md).
- **⛔ THE PATIENT-FACING SITE IS RETIRED AND DELETED (2026-08-05), NOT SHELVED.** *Superseded, retained:
  "The patient-facing site is shelved — keep it working if you touch it, but don't invest new effort there
  without being asked."* The HTML, assets, templates, per-cancer data index, the `add-cancer` skill and the
  Pages workflow are gone. **Two things survived because they were never site tooling:** the cited EMC
  clinical registry, now [`research/data/emc-clinical-registry.json`](./research/data/emc-clinical-registry.json)
  — read by `research/meta/meta-analysis.mjs` and `research/hypotheses/enumerate-drugs.mjs`, both of which build
  the path from segments, so **searching for the DIRECTORY name finds neither; searching for the filename finds
  both** — and its validator, now `scripts/validate-registry.mjs`, which is **gate 10 of preflight's 16**.
  **Do not recreate the site.** Full accounting: [`systems/MIGRATION.md`](./systems/MIGRATION.md).
  ⚠ *Superseded, retained: "both via segment-built paths a text search will not find … which is gate 2 of
  preflight." The first over-stated the problem — `grep emc-clinical-registry` returns both readers at once,
  and the precise warning is the one `enumerate-drugs.mjs` itself writes. The second was simply the wrong
  ordinal, which is worse than vague: it sends a reader to the wrong gate when preflight fails.*

## The deliverable map (from CLAUDE.md §5)

- **ONE FILE PER DELIVERABLE** (from CLAUDE.md §5's OPERATING REGIME bullet; the regime's judgment
  clauses stay resident in CLAUDE.md, this is the file map):
  **ONE FILE PER DELIVERABLE:** [nr4a3-degrader-paper.md](./research/manuscripts/degrader/nr4a3-degrader-paper.md) + its
  SI **is** both the ChemRxiv preprint and the JCIM submission **for the degrader route**. ⚠ *Superseded,
  retained: **"SINGLE DELIVERABLE"**, unqualified — the anti-duplication rule it protects is live and unchanged,
  but as written it also said this repository has ONE deliverable, and it has
  [sixteen publication endpoints](./systems/views/L3-publications.md) covering all forty routes. Reading an
  anti-duplication rule as a portfolio statement is how every other route's paper became invisible.*
  `nr4a3-degrader-preprint.md` and
  `nr4a3-degrader-preprint-si.md` are retired stubs — a
  parallel condensed draft drifted out of sync and self-contradicted; **don't recreate one.** ⚠ *Superseded,
  retained: "`nr4a3-degrader-preprint*.md` are retired stubs" — that glob also swept in
  `nr4a3-degrader-preprint-plan.md`, which is 174 live lines and which this very sentence goes on to cite.*
  Pre-post checklist:
  [preprint-plan.md](./research/manuscripts/degrader/nr4a3-degrader-preprint-plan.md); ready-to-send outreach:
  [outreach-emails.md](./research/manuscripts/degrader/nr4a3-degrader-outreach-emails.md).

## The reviewer-AI review block — its six required parts

CLAUDE.md §3 owns **when** to produce a block (program-shifting decisions, >$50 GPU spend, outward-facing or
irreversible acts) and the rule that it is the **first thing** in your reply — self-contained, copyable and
fenced, because the reviewer sees only what is inside the box. This is **what goes in it**:

1. Role + the ask, verbatim: *"approve, or return a specific list of fixes"*.
2. Project + goal, one paragraph.
3. What was done, with repo/PR/file paths.
4. The exact proposed next action(s) needing sign-off, verbatim.
5. Known risks, uncertainties and judgment calls, stated honestly — over-claim vs verification level, medical
   integrity, ethics/tone.
6. Your specific questions.

Apply the returned changes **yourself**, and only then proceed.

⚠ *Superseded, retained: "every hand-off gets a block" (corrected 2026-07-12 after over-escalation). A block is
NOT for finished free work, curation you can verify, ordering self-doable work, or cheap authorized runs — for
those, execute and report the result.*
